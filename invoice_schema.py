from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict


class ChunkType(str, Enum):
    SUMMARY = "summary"
    HEADER_FIELDS = "header_fields"
    TOTALS_BLOCK = "totals_block"
    TERMS = "terms"
    PAGE_TEXT = "page_text"
    LINE_ITEM = "line_item"
    FOOTER = "footer"


class RouteIntent(str, Enum):
    EXACT_LOOKUP = "exact_lookup"
    SEMANTIC_SEARCH = "semantic_search"
    COMPARISON = "comparison"
    LOSS_ANALYSIS = "loss_analysis"
    RECOMMENDATION = "recommendation"
    ANALYTICS = "analytics"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESOLVED = "resolved"


class ConfidenceMap(BaseModel):
    model_config = ConfigDict(extra="allow")
    invoice_number: float = 0.0
    invoice_date: float = 0.0
    due_date: float = 0.0
    po_number: float = 0.0
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    line_items: float = 0.0
    vendor_name: float = 0.0


class VendorInfo(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: Optional[str] = None
    vendor_id: Optional[str] = None
    tax_id: Optional[str] = None
    address: Optional[str] = None
    remittance_address: Optional[str] = None
    payment_reference: Optional[str] = None


class InvoiceAmounts(BaseModel):
    model_config = ConfigDict(extra="allow")
    currency: str = "USD"
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    shipping: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    total: Optional[Decimal] = None
    amount_due: Optional[Decimal] = None


class InvoiceHeader(BaseModel):
    model_config = ConfigDict(extra="allow")
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    payment_terms: Optional[str] = None
    po_number: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    amounts: InvoiceAmounts = Field(default_factory=InvoiceAmounts)


class LayoutBlock(BaseModel):
    model_config = ConfigDict(extra="allow")
    block_id: str = Field(default_factory=lambda: f"blk_{uuid4().hex[:10]}")
    page_no: int
    block_type: str
    text: str
    bbox: Optional[List[float]] = None
    row_index: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PageContent(BaseModel):
    model_config = ConfigDict(extra="allow")
    page_no: int
    text: str
    ocr_confidence: float = 0.0
    blocks: List[LayoutBlock] = Field(default_factory=list)
    tables: List[List[List[str]]] = Field(default_factory=list)


class InvoiceLineItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(default_factory=lambda: f"line_{uuid4().hex}")
    document_id: Optional[str] = None
    tenant_id: str = "default"
    page_no: int = 1
    row_index: int = 0
    description: str
    item_code: Optional[str] = None
    quantity: Optional[Decimal] = None
    uom: Optional[str] = None
    unit_price: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    currency: str = "USD"
    tax_amount: Optional[Decimal] = None
    confidence: float = 0.0
    source_block_id: Optional[str] = None


class InvoiceFlags(BaseModel):
    duplicate_candidate: bool = False
    po_missing: bool = False
    amount_mismatch: bool = False
    tax_mismatch: bool = False
    low_ocr_confidence: bool = False
    line_item_parse_weak: bool = False
    needs_review: bool = False


class InvoiceDocument(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(default_factory=lambda: f"doc_{uuid4().hex}")
    tenant_id: str = "default"
    document_type: str = "invoice"
    source_filename: str
    source_uri: Optional[str] = None
    upload_id: Optional[str] = None
    status: str = "ready"
    processing_stage: str = "indexed"
    vendor: VendorInfo = Field(default_factory=VendorInfo)
    invoice: InvoiceHeader = Field(default_factory=InvoiceHeader)
    pages: List[PageContent] = Field(default_factory=list)
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    flags: InvoiceFlags = Field(default_factory=InvoiceFlags)
    extraction_confidence: ConfidenceMap = Field(default_factory=ConfidenceMap)
    page_count: int = 0
    ocr_engine: Optional[str] = None
    ocr_version: Optional[str] = None
    embedding_version: Optional[str] = None
    schema_version: str = "invoice_v1"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InvoiceChunk(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(default_factory=lambda: f"chk_{uuid4().hex}")
    document_id: str
    tenant_id: str = "default"
    source_filename: str
    page_no: int = 1
    chunk_index: int = 0
    chunk_type: ChunkType = ChunkType.PAGE_TEXT
    block_id: Optional[str] = None
    text: str
    normalized_text: str
    token_count: int = 0
    invoice_number: Optional[str] = None
    po_number: Optional[str] = None
    vendor_name: Optional[str] = None
    total: Optional[Decimal] = None
    currency: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None
    schema_version: str = "invoice_chunk_v1"


class QueryEntities(BaseModel):
    model_config = ConfigDict(extra="allow")
    invoice_numbers: List[str] = Field(default_factory=list)
    po_numbers: List[str] = Field(default_factory=list)
    vendor_names: List[str] = Field(default_factory=list)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    amount_min: Optional[Decimal] = None
    amount_max: Optional[Decimal] = None
    terms: List[str] = Field(default_factory=list)
    currencies: List[str] = Field(default_factory=list)


class QueryPlan(BaseModel):
    model_config = ConfigDict(extra="allow")
    intent: RouteIntent
    confidence: float = 0.0
    use_structured_lookup: bool = False
    use_keyword_search: bool = True
    use_vector_search: bool = False
    use_analytics: bool = False
    entities: QueryEntities = Field(default_factory=QueryEntities)
    filters: Dict[str, Any] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)


class RetrievalEvidence(BaseModel):
    model_config = ConfigDict(extra="allow")
    document_id: str
    source_filename: str
    page_no: int
    score: float
    text: str
    chunk_id: Optional[str] = None
    chunk_type: Optional[str] = None
    block_id: Optional[str] = None
    structured_fields: Dict[str, Any] = Field(default_factory=dict)


class InvoiceComparisonRow(BaseModel):
    model_config = ConfigDict(extra="allow")
    document_id: str
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    po_number: Optional[str] = None
    subtotal: Optional[Decimal] = None
    tax: Optional[Decimal] = None
    total: Optional[Decimal] = None
    line_item_count: int = 0
    duplicate_risk: bool = False
    late_fee_detected: bool = False
    missing_po: bool = False


class AnalyticsFinding(BaseModel):
    model_config = ConfigDict(extra="allow")
    finding_type: str
    severity: str
    document_id: Optional[str] = None
    invoice_number: Optional[str] = None
    title: str
    description: str
    amount_impact: Optional[Decimal] = None
    supporting_fields: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[RetrievalEvidence] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    priority: str
    title: str
    action: str
    rationale: str
    document_ids: List[str] = Field(default_factory=list)
    owner: Optional[str] = None


class ReviewItem(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(default_factory=lambda: f"rev_{uuid4().hex}")
    tenant_id: str = "default"
    document_id: str
    source_filename: str
    status: ReviewStatus = ReviewStatus.PENDING
    reason: str
    confidence: float = 0.0
    assigned_to: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = Field(default_factory=dict)
    resolution_notes: Optional[str] = None


class QueryAuditRecord(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = Field(default_factory=lambda: f"qry_{uuid4().hex}")
    tenant_id: str = "default"
    query: str
    intent: RouteIntent
    route: str
    document_ids: List[str] = Field(default_factory=list)
    latency_ms: int = 0
    retrieval_count: int = 0
    confidence: float = 0.0
    requires_review: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    query: str
    plan: QueryPlan
    matched_documents: List[InvoiceDocument] = Field(default_factory=list)
    evidence: List[RetrievalEvidence] = Field(default_factory=list)
    findings: List[AnalyticsFinding] = Field(default_factory=list)
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    answer_markdown: str = ""
    overall_confidence: float = 0.0
    needs_human_review: bool = False
