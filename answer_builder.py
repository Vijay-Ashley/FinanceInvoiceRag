from __future__ import annotations

from typing import Callable, List, Optional, Sequence

from invoice_schema import AnalyticsFinding, InvoiceComparisonRow, RecommendationItem, RetrievalEvidence, SearchResponse


class AnswerBuilder:
    """
    Builds grounded markdown answers.

    You can use it in two modes:
    1. deterministic markdown only
    2. LLM-enhanced explanation by passing llm_callable(prompt: str) -> str
    """

    def __init__(self, llm_callable: Optional[Callable[[str], str]] = None):
        self.llm_callable = llm_callable

    def build(
        self,
        *,
        query: str,
        response: SearchResponse,
        comparison_rows: Optional[Sequence[InvoiceComparisonRow]] = None,
        findings: Optional[Sequence[AnalyticsFinding]] = None,
        recommendations: Optional[Sequence[RecommendationItem]] = None,
    ) -> str:
        comparison_rows = comparison_rows or []
        findings = findings or []
        recommendations = recommendations or []

        base_markdown = self._deterministic_markdown(
            query=query,
            response=response,
            comparison_rows=comparison_rows,
            findings=findings,
            recommendations=recommendations,
        )

        if not self.llm_callable:
            return base_markdown

        prompt = self._build_llm_prompt(query, base_markdown, response.evidence)
        try:
            llm_answer = self.llm_callable(prompt)
            return llm_answer.strip() if llm_answer and llm_answer.strip() else base_markdown
        except Exception:
            return base_markdown

    def _deterministic_markdown(
        self,
        *,
        query: str,
        response: SearchResponse,
        comparison_rows: Sequence[InvoiceComparisonRow],
        findings: Sequence[AnalyticsFinding],
        recommendations: Sequence[RecommendationItem],
    ) -> str:
        lines: List[str] = []
        lines.append(f"## Summary")
        lines.append(
            f"Query intent: **{response.plan.intent.value}**. Matched **{len(response.matched_documents)}** document(s), "
            f"evidence chunks: **{len(response.evidence)}**, confidence: **{response.overall_confidence:.2f}**."
        )

        if response.matched_documents:
            lines.append("## Matched invoices")
            lines.append("| Invoice | Vendor | Invoice Date | Due Date | PO | Total | Source |")
            lines.append("|---|---|---|---|---|---:|---|")
            for doc in response.matched_documents:
                lines.append(
                    f"| {doc.invoice.invoice_number or '-'} | {doc.vendor.name or '-'} | {doc.invoice.invoice_date or '-'} | "
                    f"{doc.invoice.due_date or '-'} | {doc.invoice.po_number or '-'} | {doc.invoice.amounts.total or '-'} | {doc.source_filename} |"
                )

        if comparison_rows:
            lines.append("## Comparison")
            lines.append("| Invoice | Vendor | Date | Due | PO | Subtotal | Tax | Total | Lines | Duplicate Risk | Late Fee |")
            lines.append("|---|---|---|---|---|---:|---:|---:|---:|---|---|")
            for row in comparison_rows:
                lines.append(
                    f"| {row.invoice_number or '-'} | {row.vendor_name or '-'} | {row.invoice_date or '-'} | {row.due_date or '-'} | "
                    f"{row.po_number or '-'} | {row.subtotal or '-'} | {row.tax or '-'} | {row.total or '-'} | {row.line_item_count} | "
                    f"{'Yes' if row.duplicate_risk else 'No'} | {'Yes' if row.late_fee_detected else 'No'} |"
                )

        if findings:
            lines.append("## Findings")
            lines.append("| Severity | Type | Invoice | Description | Impact |")
            lines.append("|---|---|---|---|---:|")
            for finding in findings:
                lines.append(
                    f"| {finding.severity} | {finding.finding_type} | {finding.invoice_number or '-'} | {finding.description} | {finding.amount_impact or '-'} |"
                )

        if recommendations:
            lines.append("## Recommendations")
            lines.append("| Priority | Title | Action | Owner |")
            lines.append("|---|---|---|---|")
            for rec in recommendations:
                lines.append(f"| {rec.priority} | {rec.title} | {rec.action} | {rec.owner or '-'} |")

        if response.evidence:
            lines.append("## Evidence")
            for ev in response.evidence[:10]:
                snippet = ev.text.replace("\n", " ")[:280]
                lines.append(f"- **{ev.source_filename}**, page {ev.page_no}, score {ev.score:.3f}: {snippet}")

        if response.needs_human_review:
            lines.append("## Review required")
            lines.append("One or more documents were flagged for human review due to low confidence or reconciliation issues.")

        return "\n".join(lines)

    def _build_llm_prompt(self, query: str, base_markdown: str, evidence: Sequence[RetrievalEvidence]) -> str:
        ev_lines = []
        for ev in evidence[:12]:
            ev_lines.append(
                f"Source={ev.source_filename}; Page={ev.page_no}; Score={ev.score:.3f}; Text={ev.text[:600]}"
            )

        return (
            "You are an invoice intelligence assistant.\n"
            "Use only the grounded data below. Do not invent missing values.\n\n"
            f"User query:\n{query}\n\n"
            f"Structured draft answer:\n{base_markdown}\n\n"
            "Evidence:\n"
            + "\n".join(ev_lines)
            + "\n\nRewrite the draft answer to be concise, professional, and grounded."
        )
