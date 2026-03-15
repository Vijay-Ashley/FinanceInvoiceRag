from __future__ import annotations

import re
from typing import List

from invoice_schema import ChunkType, InvoiceChunk, InvoiceDocument


class InvoiceChunker:
    """Builds purpose-specific chunks for invoice retrieval."""

    def __init__(self, max_chars: int = 1500):
        self.max_chars = max_chars

    def build_chunks(self, doc: InvoiceDocument) -> List[InvoiceChunk]:
        chunks: List[InvoiceChunk] = []
        chunk_index = 0

        def add_chunk(page_no: int, chunk_type: ChunkType, text: str, block_id: str | None = None, extra: dict | None = None) -> None:
            nonlocal chunk_index
            clean = self._clean_text(text)
            if not clean:
                return
            chunks.append(
                InvoiceChunk(
                    document_id=doc.id,
                    tenant_id=doc.tenant_id,
                    source_filename=doc.source_filename,
                    page_no=page_no,
                    chunk_index=chunk_index,
                    chunk_type=chunk_type,
                    block_id=block_id,
                    text=clean,
                    normalized_text=clean.lower(),
                    token_count=self._estimate_tokens(clean),
                    invoice_number=doc.invoice.invoice_number,
                    po_number=doc.invoice.po_number,
                    vendor_name=doc.vendor.name,
                    total=doc.invoice.amounts.total,
                    currency=doc.invoice.amounts.currency,
                    metadata=extra or {},
                )
            )
            chunk_index += 1

        add_chunk(1, ChunkType.SUMMARY, self._document_summary(doc), extra={"layer": "document"})
        add_chunk(1, ChunkType.HEADER_FIELDS, self._header_fields_text(doc), extra={"layer": "header"})
        add_chunk(1, ChunkType.TOTALS_BLOCK, self._totals_text(doc), extra={"layer": "totals"})
        if doc.invoice.payment_terms:
            add_chunk(1, ChunkType.TERMS, f"Payment terms: {doc.invoice.payment_terms}", extra={"layer": "terms"})

        for item in doc.line_items:
            text = (
                f"Line item {item.row_index}: description={item.description}; "
                f"item_code={item.item_code or ''}; qty={item.quantity}; uom={item.uom or ''}; "
                f"unit_price={item.unit_price}; amount={item.amount}; currency={item.currency}"
            )
            add_chunk(item.page_no, ChunkType.LINE_ITEM, text, block_id=item.source_block_id, extra={"row_index": item.row_index})

        for page in doc.pages:
            if page.blocks:
                for block in page.blocks:
                    add_chunk(
                        page.page_no,
                        ChunkType.PAGE_TEXT,
                        block.text,
                        block_id=block.block_id,
                        extra={"block_type": block.block_type},
                    )
            else:
                for segment in self._segment(page.text):
                    add_chunk(page.page_no, ChunkType.PAGE_TEXT, segment, extra={"layer": "page"})

        return chunks

    def _document_summary(self, doc: InvoiceDocument) -> str:
        item_count = len(doc.line_items)
        return (
            f"Invoice summary for {doc.source_filename}. "
            f"Vendor: {doc.vendor.name or 'unknown'}. "
            f"Invoice number: {doc.invoice.invoice_number or 'unknown'}. "
            f"Invoice date: {doc.invoice.invoice_date}. Due date: {doc.invoice.due_date}. "
            f"PO number: {doc.invoice.po_number or 'missing'}. "
            f"Currency: {doc.invoice.amounts.currency}. "
            f"Subtotal: {doc.invoice.amounts.subtotal}. Tax: {doc.invoice.amounts.tax}. "
            f"Shipping: {doc.invoice.amounts.shipping}. Discount: {doc.invoice.amounts.discount}. "
            f"Total: {doc.invoice.amounts.total}. Line item count: {item_count}."
        )

    def _header_fields_text(self, doc: InvoiceDocument) -> str:
        return (
            f"Invoice header: vendor={doc.vendor.name}; tax_id={doc.vendor.tax_id}; "
            f"address={doc.vendor.address}; invoice_number={doc.invoice.invoice_number}; "
            f"invoice_date={doc.invoice.invoice_date}; due_date={doc.invoice.due_date}; "
            f"po_number={doc.invoice.po_number}; buyer_name={doc.invoice.buyer_name}; "
            f"payment_terms={doc.invoice.payment_terms}"
        )

    def _totals_text(self, doc: InvoiceDocument) -> str:
        amounts = doc.invoice.amounts
        return (
            f"Invoice totals: currency={amounts.currency}; subtotal={amounts.subtotal}; "
            f"tax={amounts.tax}; shipping={amounts.shipping}; discount={amounts.discount}; "
            f"total={amounts.total}; amount_due={amounts.amount_due}"
        )

    def _segment(self, text: str) -> List[str]:
        text = self._clean_text(text)
        if len(text) <= self.max_chars:
            return [text] if text else []
        parts: List[str] = []
        current = []
        current_len = 0
        for para in re.split(r"\n{2,}|\n", text):
            para = para.strip()
            if not para:
                continue
            if current_len + len(para) + 1 > self.max_chars and current:
                parts.append("\n".join(current))
                current = [para]
                current_len = len(para)
            else:
                current.append(para)
                current_len += len(para) + 1
        if current:
            parts.append("\n".join(current))
        return parts

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").strip())

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)
