from __future__ import annotations

import re
from decimal import Decimal
from typing import Dict, List, Optional

from invoice_schema import QueryEntities, QueryPlan, RouteIntent


class InvoiceRouter:
    """Deterministic query classifier and routing planner."""

    EXACT_INVOICE_PATTERN = re.compile(r"\b(?:inv(?:oice)?[-\s#:]*)?([A-Z]{0,4}\d[A-Z0-9\-_/]{2,})\b", re.IGNORECASE)
    PO_PATTERN = re.compile(r"\b(?:po|purchase\s*order)[-\s#:]*(\w[\w\-_/]{2,})\b", re.IGNORECASE)
    MONEY_PATTERN = re.compile(r"(?:over|above|greater\s+than|under|below|less\s+than|between)?\s*([\$₹€£]?\d[\d,]*(?:\.\d{1,2})?)", re.IGNORECASE)
    DATE_RANGE_PATTERN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")

    COMPARISON_HINTS = {"compare", "difference", "versus", "vs", "variance"}
    LOSS_HINTS = {"loss", "leakage", "overbilling", "overcharge", "duplicate", "mismatch", "late fee", "variance", "anomaly"}
    RECOMMEND_HINTS = {"recommend", "recommendation", "what should", "action", "next step", "improve", "optimize"}

    def classify(self, query: str) -> QueryPlan:
        clean = query.strip()
        lowered = clean.lower()
        entities = self._extract_entities(clean)

        notes: List[str] = []
        if entities.invoice_numbers or entities.po_numbers:
            intent = RouteIntent.EXACT_LOOKUP
            confidence = 0.95
            notes.append("Detected invoice or PO identifier.")
        elif any(hint in lowered for hint in self.COMPARISON_HINTS):
            intent = RouteIntent.COMPARISON
            confidence = 0.87
            notes.append("Detected comparison language.")
        elif any(hint in lowered for hint in self.LOSS_HINTS):
            intent = RouteIntent.LOSS_ANALYSIS
            confidence = 0.86
            notes.append("Detected loss/anomaly language.")
        elif any(hint in lowered for hint in self.RECOMMEND_HINTS):
            intent = RouteIntent.RECOMMENDATION
            confidence = 0.84
            notes.append("Detected recommendation language.")
        elif any(word in lowered for word in ["summary", "trend", "analyze", "analysis", "why"]):
            intent = RouteIntent.ANALYTICS
            confidence = 0.76
            notes.append("Detected analytics/explanation intent.")
        else:
            intent = RouteIntent.SEMANTIC_SEARCH
            confidence = 0.72
            notes.append("Defaulted to semantic search.")

        filters = self._build_filters(entities)
        use_structured_lookup = intent in {RouteIntent.EXACT_LOOKUP, RouteIntent.COMPARISON, RouteIntent.LOSS_ANALYSIS, RouteIntent.RECOMMENDATION, RouteIntent.ANALYTICS}
        use_vector_search = intent in {RouteIntent.SEMANTIC_SEARCH, RouteIntent.COMPARISON, RouteIntent.LOSS_ANALYSIS, RouteIntent.RECOMMENDATION}
        use_keyword_search = True
        use_analytics = intent in {RouteIntent.COMPARISON, RouteIntent.LOSS_ANALYSIS, RouteIntent.RECOMMENDATION, RouteIntent.ANALYTICS}

        return QueryPlan(
            intent=intent,
            confidence=confidence,
            use_structured_lookup=use_structured_lookup,
            use_keyword_search=use_keyword_search,
            use_vector_search=use_vector_search,
            use_analytics=use_analytics,
            entities=entities,
            filters=filters,
            notes=notes,
        )

    def _extract_entities(self, query: str) -> QueryEntities:
        entities = QueryEntities()

        invoice_numbers = [m.group(1).upper() for m in self.EXACT_INVOICE_PATTERN.finditer(query)]
        po_numbers = [m.group(1).upper() for m in self.PO_PATTERN.finditer(query)]

        filtered_invoices = []
        for value in invoice_numbers:
            if value.startswith("PO"):
                continue
            if len(value) >= 4:
                filtered_invoices.append(value)

        entities.invoice_numbers = self._unique(filtered_invoices)
        entities.po_numbers = self._unique(po_numbers)

        # quoted vendors or company-like names
        quoted = re.findall(r'"([^"]{3,})"', query)
        if quoted:
            entities.vendor_names.extend([v.strip() for v in quoted])

        company_like = re.findall(r"\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z&.]+){0,3}\s+(?:LLC|Inc|Ltd|Corporation|Corp|Services|Logistics|Technologies|Systems))\b", query)
        entities.vendor_names.extend(company_like)

        # simple month/year/date extraction can be layered later; keep exact ISO dates now
        dates = self.DATE_RANGE_PATTERN.findall(query)
        if dates:
            from datetime import date

            parsed = [date.fromisoformat(d) for d in dates]
            entities.date_from = min(parsed)
            entities.date_to = max(parsed)

        amounts = [self._to_decimal(m.group(1)) for m in self.MONEY_PATTERN.finditer(query)]
        amounts = [a for a in amounts if a is not None]
        if "between" in query.lower() and len(amounts) >= 2:
            entities.amount_min, entities.amount_max = min(amounts), max(amounts)
        elif any(w in query.lower() for w in ["over", "above", "greater than"]):
            if amounts:
                entities.amount_min = amounts[0]
        elif any(w in query.lower() for w in ["under", "below", "less than"]):
            if amounts:
                entities.amount_max = amounts[0]

        if "$" in query:
            entities.currencies.append("USD")
        for curr in ["USD", "EUR", "GBP", "INR"]:
            if curr.lower() in query.lower():
                entities.currencies.append(curr)

        for term in ["late fee", "freight", "tax", "discount", "duplicate", "overcharge", "po", "amount due"]:
            if term in query.lower():
                entities.terms.append(term)

        entities.vendor_names = self._unique([v for v in entities.vendor_names if v])
        entities.currencies = self._unique(entities.currencies)
        entities.terms = self._unique(entities.terms)
        return entities

    def _build_filters(self, entities: QueryEntities) -> Dict[str, object]:
        filters: Dict[str, object] = {}
        if entities.invoice_numbers:
            filters["invoice_number"] = entities.invoice_numbers
        if entities.po_numbers:
            filters["po_number"] = entities.po_numbers
        if entities.vendor_names:
            filters["vendor_name"] = entities.vendor_names
        if entities.amount_min is not None:
            filters["amount_min"] = entities.amount_min
        if entities.amount_max is not None:
            filters["amount_max"] = entities.amount_max
        if entities.date_from is not None:
            filters["date_from"] = entities.date_from.isoformat()
        if entities.date_to is not None:
            filters["date_to"] = entities.date_to.isoformat()
        if entities.currencies:
            filters["currency"] = entities.currencies
        return filters

    def _unique(self, values: List[str]) -> List[str]:
        seen = set()
        out = []
        for value in values:
            key = value.lower()
            if key not in seen:
                seen.add(key)
                out.append(value)
        return out

    def _to_decimal(self, value: str) -> Optional[Decimal]:
        try:
            return Decimal(re.sub(r"[^\d.]", "", value.replace(",", "")))
        except Exception:
            return None
