"""
Invoice field extraction from PDF text using regex patterns and LLM assistance.
"""
from __future__ import annotations

import re
import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Tuple

from invoice_schema import (
    InvoiceAmounts,
    InvoiceDocument,
    InvoiceHeader,
    InvoiceLineItem,
    VendorInfo,
    PageContent,
    ConfidenceMap,
    InvoiceFlags
)

logger = logging.getLogger(__name__)


class InvoiceExtractor:
    """Extract structured invoice fields from PDF text."""
    
    # Regex patterns for invoice field extraction (IMPROVED)
    INVOICE_NUMBER_PATTERNS = [
        # Pattern 1: "Invoice number: 5440612345" (Google Cloud style)
        re.compile(r"invoice\s*number[\s:]+(\d+)", re.IGNORECASE),
        # Pattern 2: "Invoice #: INV-12345"
        re.compile(r"invoice\s*#?[\s:]+([A-Z0-9\-/]+)", re.IGNORECASE),
        # Pattern 3: "INV-12345" at start of line
        re.compile(r"^(INV[\-\s]?\d+)", re.IGNORECASE | re.MULTILINE),
        # Pattern 4: Generic "Invoice: 12345"
        re.compile(r"invoice[\s:]+([A-Z0-9\-/]{3,})", re.IGNORECASE),
    ]

    PO_NUMBER_PATTERNS = [
        # Pattern 1: "PO Number: PO-12345"
        re.compile(r"p\.?o\.?\s*(?:number|no|#)?[\s:]+([A-Z0-9\-/]+)", re.IGNORECASE),
        # Pattern 2: "Purchase Order: 12345"
        re.compile(r"purchase\s*order[\s:]+([A-Z0-9\-/]+)", re.IGNORECASE),
        # Pattern 3: "PO: 12345"
        re.compile(r"\bPO[\s:]+([A-Z0-9\-/]+)", re.IGNORECASE),
    ]

    DATE_PATTERNS = [
        # Pattern 1: "Dec 19, 2025" or "December 19, 2025"
        re.compile(r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}", re.IGNORECASE),
        # Pattern 2: "2025-12-19" or "2025/12/19"
        re.compile(r"\d{4}[/-]\d{1,2}[/-]\d{1,2}"),
        # Pattern 3: "12/19/2025" or "12-19-2025"
        re.compile(r"\d{1,2}[/-]\d{1,2}[/-]\d{4}"),
        # Pattern 4: "19 Dec 2025"
        re.compile(r"\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}", re.IGNORECASE),
    ]

    TOTAL_PATTERNS = [
        # Pattern 1: "Total amount due in USD $195,652.18" (Google Cloud)
        re.compile(r"total\s*amount\s*due\s*in\s*(?:USD|EUR|GBP)?[\s:]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", re.IGNORECASE),
        # Pattern 2: "Total: $1,234.56"
        re.compile(r"total[\s:]+\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", re.IGNORECASE),
        # Pattern 3: "Amount Due: $1,234.56"
        re.compile(r"amount\s*due[\s:]+\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", re.IGNORECASE),
        # Pattern 4: "Grand Total: $1,234.56"
        re.compile(r"grand\s*total[\s:]+\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", re.IGNORECASE),
    ]

    VENDOR_PATTERNS = [
        # Pattern 1: "Google LLC" followed by address
        re.compile(r"^([A-Z][A-Za-z\s&,\.]{3,50}(?:Inc|LLC|Ltd|Corp|Corporation|Co\.))\s*$", re.MULTILINE),
        # Pattern 2: "From: Acme Corp"
        re.compile(r"(?:from|vendor|seller)[\s:]+([^\n]{5,80})", re.IGNORECASE),
        # Pattern 3: Company name before "Federal Tax ID"
        re.compile(r"([A-Z][A-Za-z\s&,\.]{3,50}(?:Inc|LLC|Ltd|Corp|Corporation))\s*\n.*?Federal\s*Tax\s*ID", re.IGNORECASE | re.DOTALL),
        # Pattern 4: Look for company name in first 20 lines
        re.compile(r"^([A-Z][A-Za-z\s&,\.]{3,50}(?:Inc|LLC|Ltd|Corp|Corporation|Co\.))", re.MULTILINE),
    ]
    
    @classmethod
    def extract_invoice(cls, text: str, filename: str, tenant_id: str = "default") -> InvoiceDocument:
        """
        Extract structured invoice data from PDF text.
        
        Args:
            text: Full PDF text content
            filename: Source filename
            tenant_id: Tenant identifier
            
        Returns:
            InvoiceDocument with extracted fields
        """
        logger.info(f"Extracting invoice fields from {filename}")
        
        # Extract basic fields
        invoice_number = cls._extract_invoice_number(text)
        po_number = cls._extract_po_number(text)
        vendor_name = cls._extract_vendor(text)
        invoice_date = cls._extract_invoice_date(text)
        due_date = cls._extract_due_date(text)
        
        # Extract amounts
        amounts = cls._extract_amounts(text)
        
        # Extract line items (basic implementation)
        line_items = cls._extract_line_items(text)
        
        # Calculate confidence scores
        confidence = cls._calculate_confidence(
            invoice_number, vendor_name, invoice_date, amounts, line_items
        )
        
        # Detect flags
        flags = cls._detect_flags(po_number, amounts, confidence)
        
        # Build document
        doc = InvoiceDocument(
            tenant_id=tenant_id,
            source_filename=filename,
            vendor=VendorInfo(name=vendor_name),
            invoice=InvoiceHeader(
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                due_date=due_date,
                po_number=po_number,
                amounts=amounts
            ),
            pages=[PageContent(page_no=1, text=text)],
            line_items=line_items,
            flags=flags,
            extraction_confidence=confidence,
            page_count=1,
            ocr_engine="pypdf",
            schema_version="invoice_v1"
        )
        
        logger.info(f"✅ Extracted: invoice={invoice_number}, vendor={vendor_name}, total={amounts.total}")
        return doc
    
    @classmethod
    def _extract_invoice_number(cls, text: str) -> Optional[str]:
        """Extract invoice number using multiple patterns."""
        # Try each pattern in order of specificity
        for pattern in cls.INVOICE_NUMBER_PATTERNS:
            match = pattern.search(text)
            if match:
                invoice_num = match.group(1).strip()
                # Validate: must be at least 3 chars and not just "Invoice"
                if len(invoice_num) >= 3 and invoice_num.lower() != "invoice":
                    return invoice_num
        return None

    @classmethod
    def _extract_po_number(cls, text: str) -> Optional[str]:
        """Extract PO number using multiple patterns."""
        for pattern in cls.PO_NUMBER_PATTERNS:
            match = pattern.search(text)
            if match:
                po_num = match.group(1).strip()
                # Validate: must be at least 2 chars
                if len(po_num) >= 2:
                    return po_num
        return None

    @classmethod
    def _extract_vendor(cls, text: str) -> Optional[str]:
        """Extract vendor name using multiple patterns."""
        # Try each pattern
        for pattern in cls.VENDOR_PATTERNS:
            match = pattern.search(text)
            if match:
                vendor = match.group(1).strip()
                # Clean up vendor name
                vendor = re.sub(r'\s+', ' ', vendor)  # Normalize whitespace
                vendor = vendor.split('\n')[0]  # Take first line only

                # Validate: must be reasonable length
                if 3 < len(vendor) < 100:
                    return vendor

        return None
    
    @classmethod
    def _extract_invoice_date(cls, text: str) -> Optional[date]:
        """Extract invoice date using context-aware search."""
        # Look for "Invoice Date:" or similar with context
        date_context = re.search(r"invoice\s*date[\s:]+([^\n]{5,40})", text, re.IGNORECASE)
        if date_context:
            parsed = cls._parse_date(date_context.group(1))
            if parsed:
                return parsed

        # Try to find date near "Invoice" keyword
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if re.search(r'\binvoice\b', line, re.IGNORECASE):
                # Check this line and next 3 lines for dates
                context = '\n'.join(lines[i:i+4])
                for pattern in cls.DATE_PATTERNS:
                    match = pattern.search(context)
                    if match:
                        parsed = cls._parse_date(match.group(0))
                        if parsed:
                            return parsed

        return None

    @classmethod
    def _extract_due_date(cls, text: str) -> Optional[date]:
        """Extract due date using context-aware search."""
        # Look for "Due Date:" or "Due:" with context
        date_patterns = [
            r"due\s*date[\s:]+([^\n]{5,40})",
            r"due[\s:]+([^\n]{5,40})",
            r"payment\s*due[\s:]+([^\n]{5,40})"
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                parsed = cls._parse_date(match.group(1))
                if parsed:
                    return parsed

        return None

    @classmethod
    def _parse_date(cls, date_str: str) -> Optional[date]:
        """Parse date string to date object."""
        date_str = date_str.strip()

        # Try common formats
        formats = [
            "%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d", "%Y/%m/%d",
            "%d/%m/%Y", "%d-%m-%Y",
            "%B %d, %Y", "%b %d, %Y", "%B %d %Y", "%b %d %Y"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        return None

    @classmethod
    def _extract_amounts(cls, text: str) -> InvoiceAmounts:
        """Extract invoice amounts using multiple patterns."""
        amounts = InvoiceAmounts()

        # Extract total using multiple patterns
        for pattern in cls.TOTAL_PATTERNS:
            match = pattern.search(text)
            if match:
                amounts.total = cls._parse_decimal(match.group(1))
                break  # Use first match

        # Extract subtotal
        subtotal_patterns = [
            r"subtotal\s*in\s*(?:USD|EUR|GBP)?[\s:]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            r"subtotal[\s:]+\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
            r"sub[\s\-]total[\s:]+\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        ]
        for pattern in subtotal_patterns:
            subtotal_match = re.search(pattern, text, re.IGNORECASE)
            if subtotal_match:
                amounts.subtotal = cls._parse_decimal(subtotal_match.group(1))
                break

        # Extract tax
        tax_patterns = [
            r"tax\s*\([\d.]+%\)[\s:]*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",  # "Tax (0%): $0.00"
            r"tax[\s:]+\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",  # "Tax: $123.45"
        ]
        for pattern in tax_patterns:
            tax_match = re.search(pattern, text, re.IGNORECASE)
            if tax_match:
                amounts.tax = cls._parse_decimal(tax_match.group(1))
                break

        return amounts

    @classmethod
    def _parse_decimal(cls, amount_str: str) -> Optional[Decimal]:
        """Parse amount string to Decimal."""
        try:
            # Remove commas and convert
            clean = amount_str.replace(',', '').strip()
            return Decimal(clean)
        except (InvalidOperation, ValueError):
            return None

    @classmethod
    def _extract_line_items(cls, text: str) -> List[InvoiceLineItem]:
        """Extract line items (basic implementation)."""
        # This is a simplified version - production would use table extraction
        line_items = []

        # Look for table-like structures
        lines = text.split('\n')
        for idx, line in enumerate(lines):
            # Simple heuristic: line with description and amount
            if re.search(r'\$\s*\d+', line) and len(line) > 20:
                amount_match = re.search(r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', line)
                if amount_match:
                    description = re.sub(r'\$\s*\d+.*', '', line).strip()
                    if description:
                        line_items.append(InvoiceLineItem(
                            row_index=idx,
                            description=description[:200],
                            amount=cls._parse_decimal(amount_match.group(1)),
                            confidence=0.6  # Low confidence for regex extraction
                        ))

        return line_items[:50]  # Limit to 50 items

    @classmethod
    def _calculate_confidence(
        cls,
        invoice_number: Optional[str],
        vendor_name: Optional[str],
        invoice_date: Optional[date],
        amounts: InvoiceAmounts,
        line_items: List[InvoiceLineItem]
    ) -> ConfidenceMap:
        """Calculate confidence scores for extracted fields."""
        return ConfidenceMap(
            invoice_number=0.9 if invoice_number else 0.0,
            vendor_name=0.85 if vendor_name else 0.0,
            invoice_date=0.9 if invoice_date else 0.0,
            total=0.95 if amounts.total else 0.0,
            subtotal=0.9 if amounts.subtotal else 0.0,
            tax=0.9 if amounts.tax else 0.0,
            line_items=0.6 if line_items else 0.0
        )

    @classmethod
    def _detect_flags(
        cls,
        po_number: Optional[str],
        amounts: InvoiceAmounts,
        confidence: ConfidenceMap
    ) -> InvoiceFlags:
        """Detect invoice flags (missing PO, amount mismatch, etc.)."""
        flags = InvoiceFlags()

        # Missing PO
        flags.po_missing = not po_number

        # Amount mismatch
        if amounts.subtotal and amounts.tax and amounts.total:
            calculated_total = amounts.subtotal + amounts.tax
            if abs(calculated_total - amounts.total) > Decimal("0.02"):
                flags.amount_mismatch = True

        # Low confidence
        avg_confidence = (
            confidence.invoice_number +
            confidence.vendor_name +
            confidence.total
        ) / 3
        flags.low_ocr_confidence = avg_confidence < 0.7

        # Needs review if any flag is set
        flags.needs_review = (
            flags.po_missing or
            flags.amount_mismatch or
            flags.low_ocr_confidence
        )

        return flags

