"""
Deterministic invoice analytics - duplicate detection, missing PO, amount mismatches, etc.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional

from invoice_schema import (
    InvoiceDocument,
    AnalyticsFinding,
    InvoiceComparisonRow,
    RecommendationItem
)

logger = logging.getLogger(__name__)


class InvoiceAnalytics:
    """Rule-based invoice analytics engine."""
    
    @classmethod
    def detect_duplicates(cls, documents: List[InvoiceDocument]) -> List[AnalyticsFinding]:
        """
        Detect potential duplicate invoices.
        
        Criteria:
        - Same vendor
        - Same or very similar total amount
        - Invoice dates within 7 days
        """
        findings = []
        
        for i, doc1 in enumerate(documents):
            for doc2 in documents[i+1:]:
                if cls._is_duplicate_candidate(doc1, doc2):
                    findings.append(AnalyticsFinding(
                        finding_type="duplicate_risk",
                        severity="high",
                        document_id=doc1.id,
                        invoice_number=doc1.invoice.invoice_number,
                        title=f"Potential Duplicate: {doc1.vendor.name}",
                        description=(
                            f"Invoice {doc1.invoice.invoice_number} may be a duplicate of "
                            f"{doc2.invoice.invoice_number}. Same vendor ({doc1.vendor.name}), "
                            f"similar amount (${doc1.invoice.amounts.total} vs ${doc2.invoice.amounts.total}), "
                            f"close dates."
                        ),
                        amount_impact=doc1.invoice.amounts.total,
                        supporting_fields={
                            "duplicate_of": doc2.id,
                            "duplicate_invoice_number": doc2.invoice.invoice_number,
                            "amount_diff": float(abs(doc1.invoice.amounts.total - doc2.invoice.amounts.total)) if doc1.invoice.amounts.total and doc2.invoice.amounts.total else 0
                        }
                    ))
        
        return findings
    
    @classmethod
    def _is_duplicate_candidate(cls, doc1: InvoiceDocument, doc2: InvoiceDocument) -> bool:
        """Check if two invoices are potential duplicates."""
        # Same vendor
        if not doc1.vendor.name or not doc2.vendor.name:
            return False
        if doc1.vendor.name.lower() != doc2.vendor.name.lower():
            return False
        
        # Similar amount (within $1)
        if not doc1.invoice.amounts.total or not doc2.invoice.amounts.total:
            return False
        amount_diff = abs(doc1.invoice.amounts.total - doc2.invoice.amounts.total)
        if amount_diff > Decimal("1.00"):
            return False
        
        # Close dates (within 7 days)
        if doc1.invoice.invoice_date and doc2.invoice.invoice_date:
            date_diff = abs((doc1.invoice.invoice_date - doc2.invoice.invoice_date).days)
            if date_diff > 7:
                return False
        
        return True
    
    @classmethod
    def find_missing_po(cls, documents: List[InvoiceDocument]) -> List[AnalyticsFinding]:
        """Find invoices missing PO numbers."""
        findings = []
        
        for doc in documents:
            if not doc.invoice.po_number:
                findings.append(AnalyticsFinding(
                    finding_type="missing_po",
                    severity="medium",
                    document_id=doc.id,
                    invoice_number=doc.invoice.invoice_number,
                    title=f"Missing PO: {doc.vendor.name}",
                    description=(
                        f"Invoice {doc.invoice.invoice_number} from {doc.vendor.name} "
                        f"is missing a PO number. Amount: ${doc.invoice.amounts.total}"
                    ),
                    amount_impact=doc.invoice.amounts.total,
                    supporting_fields={"vendor": doc.vendor.name}
                ))
        
        return findings
    
    @classmethod
    def detect_amount_mismatches(cls, documents: List[InvoiceDocument]) -> List[AnalyticsFinding]:
        """Detect invoices where subtotal + tax ≠ total."""
        findings = []
        
        for doc in documents:
            amounts = doc.invoice.amounts
            if amounts.subtotal and amounts.tax and amounts.total:
                calculated_total = amounts.subtotal + amounts.tax
                diff = abs(calculated_total - amounts.total)
                
                if diff > Decimal("0.02"):  # Allow 2 cent rounding difference
                    findings.append(AnalyticsFinding(
                        finding_type="amount_mismatch",
                        severity="high",
                        document_id=doc.id,
                        invoice_number=doc.invoice.invoice_number,
                        title=f"Amount Mismatch: {doc.vendor.name}",
                        description=(
                            f"Invoice {doc.invoice.invoice_number}: "
                            f"Subtotal (${amounts.subtotal}) + Tax (${amounts.tax}) = "
                            f"${calculated_total}, but Total shows ${amounts.total}. "
                            f"Difference: ${diff}"
                        ),
                        amount_impact=diff,
                        supporting_fields={
                            "subtotal": float(amounts.subtotal),
                            "tax": float(amounts.tax),
                            "total": float(amounts.total),
                            "calculated_total": float(calculated_total),
                            "difference": float(diff)
                        }
                    ))
        
        return findings
    
    @classmethod
    def detect_tax_anomalies(cls, documents: List[InvoiceDocument]) -> List[AnalyticsFinding]:
        """Detect unusual tax rates."""
        findings = []
        
        for doc in documents:
            amounts = doc.invoice.amounts
            if amounts.subtotal and amounts.tax and amounts.subtotal > 0:
                tax_rate = (amounts.tax / amounts.subtotal) * 100
                
                # Flag if tax rate is outside normal range (0-15%)
                if tax_rate < 0 or tax_rate > 15:
                    findings.append(AnalyticsFinding(
                        finding_type="tax_anomaly",
                        severity="medium",
                        document_id=doc.id,
                        invoice_number=doc.invoice.invoice_number,
                        title=f"Unusual Tax Rate: {doc.vendor.name}",
                        description=(
                            f"Invoice {doc.invoice.invoice_number} has an unusual tax rate of "
                            f"{tax_rate:.2f}% (Tax: ${amounts.tax}, Subtotal: ${amounts.subtotal})"
                        ),
                        amount_impact=amounts.tax,
                        supporting_fields={
                            "tax_rate": float(tax_rate),
                            "tax": float(amounts.tax),
                            "subtotal": float(amounts.subtotal)
                        }
                    ))
        
        return findings

    @classmethod
    def compare_invoices(cls, documents: List[InvoiceDocument]) -> List[InvoiceComparisonRow]:
        """
        Create comparison table for invoices.

        Returns list of InvoiceComparisonRow for easy comparison.
        """
        rows = []

        for doc in documents:
            rows.append(InvoiceComparisonRow(
                document_id=doc.id,
                invoice_number=doc.invoice.invoice_number,
                vendor_name=doc.vendor.name,
                invoice_date=doc.invoice.invoice_date,
                due_date=doc.invoice.due_date,
                po_number=doc.invoice.po_number,
                subtotal=doc.invoice.amounts.subtotal,
                tax=doc.invoice.amounts.tax,
                total=doc.invoice.amounts.total,
                line_item_count=len(doc.line_items),
                duplicate_risk=doc.flags.duplicate_candidate,
                missing_po=doc.flags.po_missing
            ))

        return rows

    @classmethod
    def generate_recommendations(cls, findings: List[AnalyticsFinding]) -> List[RecommendationItem]:
        """Generate actionable recommendations based on findings."""
        recommendations = []

        # Group findings by type
        by_type: Dict[str, List[AnalyticsFinding]] = {}
        for finding in findings:
            by_type.setdefault(finding.finding_type, []).append(finding)

        # Duplicate recommendations
        if "duplicate_risk" in by_type:
            dup_findings = by_type["duplicate_risk"]
            total_at_risk = sum(f.amount_impact or Decimal(0) for f in dup_findings)
            recommendations.append(RecommendationItem(
                priority="high",
                title="Review Potential Duplicate Invoices",
                action=f"Review {len(dup_findings)} potential duplicate invoice(s) totaling ${total_at_risk}",
                rationale=(
                    "Duplicate payments can result in significant financial loss. "
                    "These invoices have matching vendors, amounts, and dates."
                ),
                document_ids=[f.document_id for f in dup_findings if f.document_id]
            ))

        # Missing PO recommendations
        if "missing_po" in by_type:
            po_findings = by_type["missing_po"]
            total_no_po = sum(f.amount_impact or Decimal(0) for f in po_findings)
            recommendations.append(RecommendationItem(
                priority="medium",
                title="Add PO Numbers to Invoices",
                action=f"Obtain PO numbers for {len(po_findings)} invoice(s) totaling ${total_no_po}",
                rationale=(
                    "PO numbers are required for proper invoice tracking and approval workflow. "
                    "Missing PO numbers can delay payment processing."
                ),
                document_ids=[f.document_id for f in po_findings if f.document_id]
            ))

        # Amount mismatch recommendations
        if "amount_mismatch" in by_type:
            mismatch_findings = by_type["amount_mismatch"]
            recommendations.append(RecommendationItem(
                priority="high",
                title="Resolve Amount Calculation Errors",
                action=f"Investigate {len(mismatch_findings)} invoice(s) with calculation errors",
                rationale=(
                    "Amount mismatches indicate potential errors in invoice calculation. "
                    "These should be resolved before payment to avoid overpayment."
                ),
                document_ids=[f.document_id for f in mismatch_findings if f.document_id]
            ))

        # Tax anomaly recommendations
        if "tax_anomaly" in by_type:
            tax_findings = by_type["tax_anomaly"]
            recommendations.append(RecommendationItem(
                priority="medium",
                title="Verify Unusual Tax Rates",
                action=f"Review {len(tax_findings)} invoice(s) with unusual tax rates",
                rationale=(
                    "Tax rates outside the normal range (0-15%) may indicate errors or "
                    "special circumstances that require verification."
                ),
                document_ids=[f.document_id for f in tax_findings if f.document_id]
            ))

        return recommendations

    @classmethod
    def run_all_analytics(cls, documents: List[InvoiceDocument]) -> Dict[str, Any]:
        """
        Run all analytics on a set of documents.

        Returns:
            Dict with findings, comparisons, and recommendations
        """
        logger.info(f"Running analytics on {len(documents)} documents")

        # Run all detection rules
        findings = []
        findings.extend(cls.detect_duplicates(documents))
        findings.extend(cls.find_missing_po(documents))
        findings.extend(cls.detect_amount_mismatches(documents))
        findings.extend(cls.detect_tax_anomalies(documents))

        # Generate comparison table
        comparison = cls.compare_invoices(documents)

        # Generate recommendations
        recommendations = cls.generate_recommendations(findings)

        logger.info(f"✅ Analytics complete: {len(findings)} findings, {len(recommendations)} recommendations")

        return {
            "findings": findings,
            "comparison": comparison,
            "recommendations": recommendations,
            "summary": {
                "total_documents": len(documents),
                "total_findings": len(findings),
                "high_severity": len([f for f in findings if f.severity == "high"]),
                "medium_severity": len([f for f in findings if f.severity == "medium"]),
                "total_recommendations": len(recommendations)
            }
        }

