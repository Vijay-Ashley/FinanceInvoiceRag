from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from cachetools import TTLCache

from invoice_schema import InvoiceChunk, InvoiceDocument, QueryAuditRecord, RetrievalEvidence

logger = logging.getLogger(__name__)


class InvoiceCosmosStore:
    """
    Production-oriented Cosmos persistence layer for invoice intelligence.

    Containers:
    - invoice_documents: canonical invoice JSON
    - invoice_chunks: searchable chunks + embeddings
    - invoice_query_audit: request-level tracing
    """

    def __init__(self):
        endpoint = os.getenv("COSMOS_ENDPOINT")
        key = os.getenv("COSMOS_KEY")
        database_name = os.getenv("COSMOS_DATABASE_NAME", "invoice_rag")
        if not endpoint or not key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY are required")

        self.client = CosmosClient(endpoint, key)
        self.database = self.client.create_database_if_not_exists(id=database_name)

        self.documents = self.database.create_container_if_not_exists(
            id=os.getenv("COSMOS_DOCUMENTS_CONTAINER", "invoice_documents"),
            partition_key=PartitionKey(path="/tenant_id"),
            offer_throughput=None,
        )
        self.chunks = self.database.create_container_if_not_exists(
            id=os.getenv("COSMOS_CHUNKS_CONTAINER", "invoice_chunks"),
            partition_key=PartitionKey(path="/tenant_id"),
            offer_throughput=None,
        )
        self.audit = self.database.create_container_if_not_exists(
            id=os.getenv("COSMOS_AUDIT_CONTAINER", "invoice_query_audit"),
            partition_key=PartitionKey(path="/tenant_id"),
            offer_throughput=None,
        )

        self._doc_cache: TTLCache[str, Dict[str, Any]] = TTLCache(maxsize=1000, ttl=3600)
        self._chunk_cache: TTLCache[str, Dict[str, Any]] = TTLCache(maxsize=5000, ttl=3600)

    # ---------- write paths ----------
    def save_invoice_document(self, doc: InvoiceDocument) -> None:
        item = doc.model_dump(mode="json")
        item["record_type"] = "invoice_document"
        item["updated_at"] = datetime.utcnow().isoformat()
        self.documents.upsert_item(item)
        self._doc_cache[doc.id] = item

    def save_invoice_chunks(self, chunks: Sequence[InvoiceChunk]) -> None:
        for chunk in chunks:
            item = chunk.model_dump(mode="json")
            item["record_type"] = "invoice_chunk"
            self.chunks.upsert_item(item)
            self._chunk_cache[chunk.id] = item

    def save_query_audit(self, record: QueryAuditRecord) -> None:
        self.audit.upsert_item(record.model_dump(mode="json"))

    # ---------- document queries ----------
    def get_invoice_document(self, tenant_id: str, document_id: str) -> Optional[InvoiceDocument]:
        try:
            cached = self._doc_cache.get(document_id)
            if cached and cached.get("tenant_id") == tenant_id:
                return InvoiceDocument(**cached)
            item = self.documents.read_item(item=document_id, partition_key=tenant_id)
            self._doc_cache[document_id] = item
            return InvoiceDocument(**item)
        except exceptions.CosmosResourceNotFoundError:
            return None

    def lookup_documents(self, tenant_id: str, filters: Dict[str, Any], top_k: int = 25) -> List[InvoiceDocument]:
        clauses = ["c.tenant_id = @tenant_id"]
        params: List[Dict[str, Any]] = [{"name": "@tenant_id", "value": tenant_id}]

        if invoice_numbers := filters.get("invoice_numbers"):
            safe = [str(x).upper() for x in invoice_numbers]
            clauses.append("ARRAY_CONTAINS(@invoice_numbers, UPPER(c.invoice.invoice_number))")
            params.append({"name": "@invoice_numbers", "value": safe})

        if po_numbers := filters.get("po_numbers"):
            safe = [str(x).upper() for x in po_numbers]
            clauses.append("ARRAY_CONTAINS(@po_numbers, UPPER(c.invoice.po_number))")
            params.append({"name": "@po_numbers", "value": safe})

        if vendor_names := filters.get("vendor_names"):
            vendor_clause_parts = []
            for idx, vendor in enumerate(vendor_names):
                key = f"@vendor_{idx}"
                vendor_clause_parts.append(f"CONTAINS(UPPER(c.vendor.name), UPPER({key}), true)")
                params.append({"name": key, "value": vendor})
            if vendor_clause_parts:
                clauses.append("(" + " OR ".join(vendor_clause_parts) + ")")

        if filters.get("amount_min") is not None:
            clauses.append("c.invoice.amounts.total >= @amount_min")
            params.append({"name": "@amount_min", "value": float(filters["amount_min"])})
        if filters.get("amount_max") is not None:
            clauses.append("c.invoice.amounts.total <= @amount_max")
            params.append({"name": "@amount_max", "value": float(filters["amount_max"])})

        if filters.get("date_from"):
            clauses.append("c.invoice.invoice_date >= @date_from")
            params.append({"name": "@date_from", "value": str(filters["date_from"])})
        if filters.get("date_to"):
            clauses.append("c.invoice.invoice_date <= @date_to")
            params.append({"name": "@date_to", "value": str(filters["date_to"])})

        sql = f"SELECT TOP {int(top_k)} * FROM c WHERE {' AND '.join(clauses)} ORDER BY c.updated_at DESC"
        results = self.documents.query_items(query=sql, parameters=params, enable_cross_partition_query=True)
        return [InvoiceDocument(**row) for row in results]

    # ---------- chunk retrieval ----------
    def keyword_search(self, tenant_id: str, query: str, filters: Dict[str, Any], top_k: int = 20) -> List[Tuple[float, RetrievalEvidence]]:
        keywords = self._extract_keywords(query)
        if not keywords:
            return []

        params: List[Dict[str, Any]] = [{"name": "@tenant_id", "value": tenant_id}]
        clauses = ["c.tenant_id = @tenant_id"]
        contains = []
        for idx, kw in enumerate(keywords):
            name = f"@kw_{idx}"
            params.append({"name": name, "value": kw})
            contains.append(f"CONTAINS(c.normalized_text, LOWER({name}), true)")
            contains.append(f"CONTAINS(LOWER(c.invoice_number), LOWER({name}), true)")
            contains.append(f"CONTAINS(LOWER(c.po_number), LOWER({name}), true)")
            contains.append(f"CONTAINS(LOWER(c.vendor_name), LOWER({name}), true)")
        clauses.append("(" + " OR ".join(contains) + ")")
        self._append_chunk_filters(clauses, params, filters)

        sql = f"SELECT TOP {int(top_k)} * FROM c WHERE {' AND '.join(clauses)}"
        rows = list(self.chunks.query_items(query=sql, parameters=params, enable_cross_partition_query=True))
        out: List[Tuple[float, RetrievalEvidence]] = []
        for row in rows:
            score = self._keyword_score(query, row)
            out.append((score, self._row_to_evidence(row, score)))
        out.sort(key=lambda x: x[0], reverse=True)
        return out[:top_k]

    def vector_search(self, tenant_id: str, query_vec: np.ndarray, filters: Dict[str, Any], top_k: int = 20, min_similarity: float = 0.05) -> List[Tuple[float, RetrievalEvidence]]:
        q = query_vec.astype("float32").flatten().tolist()
        params: List[Dict[str, Any]] = [{"name": "@tenant_id", "value": tenant_id}, {"name": "@queryVector", "value": q}]
        clauses = ["c.tenant_id = @tenant_id"]
        self._append_chunk_filters(clauses, params, filters)

        sql = f"""
        SELECT TOP {int(top_k * 3)}
            c.id, c.document_id, c.source_filename, c.page_no, c.text, c.chunk_type, c.block_id,
            c.invoice_number, c.po_number, c.vendor_name, c.total, c.currency,
            VectorDistance(c.embedding, @queryVector) AS distance
        FROM c
        WHERE {' AND '.join(clauses)}
        ORDER BY VectorDistance(c.embedding, @queryVector)
        """

        try:
            rows = list(self.chunks.query_items(query=sql, parameters=params, enable_cross_partition_query=True))
            out: List[Tuple[float, RetrievalEvidence]] = []
            for row in rows:
                similarity = max(0.0, 1.0 - float(row.get("distance", 1.0)))
                if similarity < min_similarity:
                    continue
                out.append((similarity, self._row_to_evidence(row, similarity)))
                if len(out) >= top_k:
                    break
            return out
        except Exception as exc:
            logger.warning("VectorDistance path failed, falling back to client-side cosine: %s", exc)
            return self._vector_fallback(tenant_id, query_vec, filters, top_k=top_k, min_similarity=min_similarity)

    def _vector_fallback(self, tenant_id: str, query_vec: np.ndarray, filters: Dict[str, Any], top_k: int, min_similarity: float) -> List[Tuple[float, RetrievalEvidence]]:
        params: List[Dict[str, Any]] = [{"name": "@tenant_id", "value": tenant_id}]
        clauses = ["c.tenant_id = @tenant_id"]
        self._append_chunk_filters(clauses, params, filters)
        sql = f"SELECT * FROM c WHERE {' AND '.join(clauses)}"
        rows = list(self.chunks.query_items(query=sql, parameters=params, enable_cross_partition_query=True))

        q = query_vec.astype("float32").flatten()
        q_norm = np.linalg.norm(q)
        if q_norm == 0.0:
            return []

        out: List[Tuple[float, RetrievalEvidence]] = []
        for row in rows:
            emb = row.get("embedding")
            if not emb:
                continue
            dv = np.array(emb, dtype="float32")
            denom = np.linalg.norm(dv) * q_norm
            if denom == 0.0:
                continue
            similarity = float(np.dot(dv, q) / denom)
            if similarity < min_similarity:
                continue
            out.append((similarity, self._row_to_evidence(row, similarity)))
        out.sort(key=lambda x: x[0], reverse=True)
        return out[:top_k]

    def get_neighbor_chunks(self, tenant_id: str, document_id: str, page_no: int, chunk_index: int, window_size: int = 1) -> List[RetrievalEvidence]:
        low = max(0, int(chunk_index) - window_size)
        high = int(chunk_index) + window_size
        sql = """
        SELECT * FROM c
        WHERE c.tenant_id = @tenant_id AND c.document_id = @document_id AND c.page_no = @page_no
          AND c.chunk_index >= @low AND c.chunk_index <= @high
        ORDER BY c.chunk_index ASC
        """
        params = [
            {"name": "@tenant_id", "value": tenant_id},
            {"name": "@document_id", "value": document_id},
            {"name": "@page_no", "value": page_no},
            {"name": "@low", "value": low},
            {"name": "@high", "value": high},
        ]
        rows = list(self.chunks.query_items(query=sql, parameters=params, enable_cross_partition_query=True))
        return [self._row_to_evidence(row, 0.0) for row in rows]

    # ---------- helpers ----------
    def _append_chunk_filters(self, clauses: List[str], params: List[Dict[str, Any]], filters: Dict[str, Any]) -> None:
        if filters.get("invoice_numbers"):
            clauses.append("ARRAY_CONTAINS(@invoice_numbers, UPPER(c.invoice_number))")
            params.append({"name": "@invoice_numbers", "value": [str(v).upper() for v in filters["invoice_numbers"]]})
        if filters.get("po_numbers"):
            clauses.append("ARRAY_CONTAINS(@po_numbers, UPPER(c.po_number))")
            params.append({"name": "@po_numbers", "value": [str(v).upper() for v in filters["po_numbers"]]})
        if filters.get("vendor_names"):
            vendor_parts = []
            for idx, vendor in enumerate(filters["vendor_names"]):
                pname = f"@vendor_name_{idx}"
                vendor_parts.append(f"CONTAINS(UPPER(c.vendor_name), UPPER({pname}), true)")
                params.append({"name": pname, "value": vendor})
            clauses.append("(" + " OR ".join(vendor_parts) + ")")
        if filters.get("amount_min") is not None:
            clauses.append("c.total >= @amount_min")
            params.append({"name": "@amount_min", "value": float(filters["amount_min"])})
        if filters.get("amount_max") is not None:
            clauses.append("c.total <= @amount_max")
            params.append({"name": "@amount_max", "value": float(filters["amount_max"])})

    def _extract_keywords(self, text: str) -> List[str]:
        stop_words = {
            'the','is','at','which','on','a','an','as','are','was','were','been','be','have','has','had','do','does','did',
            'will','would','should','could','may','might','can','how','what','where','when','who','why','compare','show','find',
            'get','tell','and','or','but','to','from','in','of','for','with','by'
        }
        words = [w.strip(" .,!?:;()[]{}") for w in (text or '').lower().split()]
        words = [w for w in words if len(w) > 2 and w not in stop_words]
        uniq: List[str] = []
        for w in words:
            if w not in uniq:
                uniq.append(w)
        return uniq[:10]

    def _keyword_score(self, query: str, row: Dict[str, Any]) -> float:
        text = f"{row.get('text','')} {row.get('invoice_number','')} {row.get('po_number','')} {row.get('vendor_name','')}".lower()
        score = 0.0
        for kw in self._extract_keywords(query):
            if kw in text:
                score += 1.0
        if row.get('invoice_number') and row['invoice_number'].lower() in query.lower():
            score += 3.0
        if row.get('po_number') and row['po_number'].lower() in query.lower():
            score += 3.0
        return score / max(1.0, len(self._extract_keywords(query)))

    def _row_to_evidence(self, row: Dict[str, Any], score: float) -> RetrievalEvidence:
        return RetrievalEvidence(
            document_id=row.get("document_id", ""),
            source_filename=row.get("source_filename", row.get("source", "")),
            page_no=int(row.get("page_no", row.get("page", 1)) or 1),
            score=float(score),
            text=row.get("text", ""),
            chunk_id=row.get("id"),
            chunk_type=row.get("chunk_type"),
            block_id=row.get("block_id"),
            structured_fields={
                "invoice_number": row.get("invoice_number"),
                "po_number": row.get("po_number"),
                "vendor_name": row.get("vendor_name"),
                "total": row.get("total"),
                "currency": row.get("currency"),
            },
        )


class StructuredInvoiceRepository:
    def __init__(self, store: InvoiceCosmosStore, tenant_id: str = "default"):
        self.store = store
        self.tenant_id = tenant_id

    def lookup(self, filters: Dict[str, Any]) -> List[InvoiceDocument]:
        return self.store.lookup_documents(self.tenant_id, filters)


class CosmosHybridRetrieverAdapter:
    def __init__(self, store: InvoiceCosmosStore, embedding_client: Any, tenant_id: str = "default", alpha: float = 0.6):
        self.store = store
        self.embedding_client = embedding_client
        self.tenant_id = tenant_id
        self.alpha = alpha

    async def search_async(self, query: str, filters: Dict[str, Any], top_k: int = 12) -> List[RetrievalEvidence]:
        embedding = await self.embedding_client.aembed_query(query)
        query_vec = np.array(embedding, dtype="float32")
        return self.search(query, filters, top_k=top_k, query_vec=query_vec)

    def search(self, query: str, filters: Dict[str, Any], top_k: int = 12, query_vec: Optional[np.ndarray] = None) -> List[RetrievalEvidence]:
        lex = self.store.keyword_search(self.tenant_id, query, filters, top_k=max(top_k * 2, 20))
        dense: List[Tuple[float, RetrievalEvidence]] = []
        if query_vec is not None:
            dense = self.store.vector_search(self.tenant_id, query_vec, filters, top_k=max(top_k * 2, 20))

        merged: Dict[str, Tuple[float, RetrievalEvidence]] = {}
        for score, ev in dense:
            merged[ev.chunk_id or hashlib.md5((ev.document_id + ev.text).encode()).hexdigest()] = (self.alpha * score, ev)
        for score, ev in lex:
            key = ev.chunk_id or hashlib.md5((ev.document_id + ev.text).encode()).hexdigest()
            if key in merged:
                merged[key] = (merged[key][0] + (1.0 - self.alpha) * score, merged[key][1])
            else:
                merged[key] = ((1.0 - self.alpha) * score, ev)
        results = sorted(merged.values(), key=lambda x: x[0], reverse=True)
        return [ev.copy(update={"score": round(float(score), 4)}) for score, ev in results[:top_k]]
