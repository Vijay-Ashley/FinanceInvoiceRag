# 🎯 Invoice Intelligence Implementation Plan

## 📋 **Current State Analysis**

### **What We Have:**
- ✅ Cosmos DB with embeddings + text + metadata
- ✅ Query classifier (but filters are ignored)
- ✅ Generic metadata extraction (not invoice-specific)
- ✅ Chunk-based search (treats all chunks the same)
- ✅ Vector search with Python fallback (not server-side)

### **What's Missing:**
- ❌ Structured invoice extraction (invoice_number, vendor, dates, amounts, line items)
- ❌ Separate containers for invoice headers and line items
- ❌ Query routing that actually uses filters
- ❌ Deterministic analytics (duplicate detection, missing PO, amount mismatch)
- ❌ Chunk types (header_fields, totals_block, line_item, etc.)
- ❌ Server-side vector search (currently forced to Python fallback)

---

## 🚀 **Implementation Order (4 Phases)**

### **Phase 1: Structured Invoice Extraction** ⭐ **START HERE**

**Goal:** Extract real invoice fields instead of generic metadata

**Files to Create/Modify:**
1. `invoice_schema.py` - Data models (copy from sample codes)
2. `invoice_extractor.py` - Extract invoice fields from PDF text
3. `metadata_extractor.py` - Update to use invoice extraction

**What to Extract:**
- Invoice number
- Vendor name
- Invoice date, due date
- PO number
- Subtotal, tax, total
- Currency
- Line items (description, quantity, unit_price, amount)
- Confidence scores per field

**Estimated Time:** 2-3 hours

---

### **Phase 2: Cosmos DB Containers** ⭐ **CRITICAL**

**Goal:** Create separate logical containers for structured data

**Files to Modify:**
1. `cosmos_store.py` - Add 3 containers:
   - `invoice_documents` - Canonical invoice JSON
   - `invoice_chunks` - Searchable chunks + embeddings
   - `invoice_query_audit` - Query tracing

**Container Structure:**
```python
# invoice_documents container
{
    "id": "doc_abc123",
    "tenant_id": "default",
    "document_type": "invoice",
    "source_filename": "Google_Invoice_Feb2026.pdf",
    "vendor": {"name": "Google", "tax_id": "..."},
    "invoice": {
        "invoice_number": "INV-12345",
        "invoice_date": "2026-02-15",
        "due_date": "2026-03-15",
        "po_number": "PO-98765",
        "amounts": {"subtotal": 1000.00, "tax": 80.00, "total": 1080.00}
    },
    "line_items": [
        {"description": "Google Workspace", "quantity": 10, "unit_price": 100.00, "amount": 1000.00}
    ],
    "flags": {"duplicate_candidate": false, "po_missing": false},
    "extraction_confidence": {"invoice_number": 0.95, "total": 0.98}
}

# invoice_chunks container
{
    "id": "chk_xyz789",
    "document_id": "doc_abc123",
    "tenant_id": "default",
    "source_filename": "Google_Invoice_Feb2026.pdf",
    "page_no": 1,
    "chunk_index": 0,
    "chunk_type": "header_fields",  # or "line_item", "totals_block", etc.
    "text": "Invoice #: INV-12345...",
    "invoice_number": "INV-12345",
    "vendor_name": "Google",
    "total": 1080.00,
    "embedding": [0.123, 0.456, ...]
}
```

**Estimated Time:** 2-3 hours

---

### **Phase 3: Query Routing & Analytics** ⭐ **HIGH VALUE**

**Goal:** Make classifier filters actually work + add deterministic analytics

**Files to Create/Modify:**
1. `invoice_router.py` - Deterministic routing logic
2. `invoice_analytics.py` - Rule-based analytics
3. `app.py` - Update chat endpoint to use routing

**Routing Logic:**
```python
# Exact lookup queries
"Show me invoice INV-12345" → structured lookup (no vector search)

# Semantic queries
"What did we pay Google in February?" → hybrid search

# Analytics queries
"Find duplicate invoices" → analytics engine first
"Which invoices are missing PO numbers?" → analytics engine
"Compare Google invoices Feb vs Jan" → analytics + retrieval
```

**Analytics Rules:**
- Duplicate invoice detection (same vendor + amount + date)
- Missing PO number
- Amount mismatch (subtotal + tax ≠ total)
- Tax mismatch (unusual tax rate)
- Unusual freight charges
- Late fee exposure (past due date)

**Estimated Time:** 3-4 hours

---

### **Phase 4: Fix Vector Search** ⭐ **PRODUCTION BLOCKER**

**Goal:** Use server-side Cosmos vector search instead of Python fallback

**Files to Modify:**
1. `cosmos_store.py` - Fix VectorDistance query
2. Verify Cosmos vector index configuration

**Current Issue:**
```python
# Currently forced to Python fallback
results = self._fallback_similarity_search(...)
```

**Target:**
```python
# Server-side vector search
sql = "SELECT TOP @k c.id, c.text, VectorDistance(c.embedding, @embedding) AS score FROM c ORDER BY score"
```

**Estimated Time:** 1-2 hours

---

## 📊 **Implementation Priority**

| Phase | Priority | Impact | Effort | Order |
|-------|----------|--------|--------|-------|
| **Phase 1: Invoice Extraction** | 🔥 Critical | High | Medium | 1st |
| **Phase 2: Cosmos Containers** | 🔥 Critical | High | Medium | 2nd |
| **Phase 3: Routing & Analytics** | ⭐ High | Very High | High | 3rd |
| **Phase 4: Vector Search Fix** | ⚠️ Medium | Medium | Low | 4th |

---

## ✅ **This Week's Goals (Minimum Viable)**

### **Goal 1: Structured Invoice Storage**
- [ ] Copy `invoice_schema.py` from sample codes
- [ ] Create `invoice_extractor.py` with basic extraction
- [ ] Update `cosmos_store.py` to create 3 containers
- [ ] Modify upload flow to save structured invoices

### **Goal 2: Basic Analytics**
- [ ] Create `invoice_analytics.py` with 4 rules:
  - Duplicate risk
  - Missing PO
  - Total mismatch
  - Tax mismatch
- [ ] Add analytics endpoint to `app.py`

### **Goal 3: Query Routing**
- [ ] Create `invoice_router.py` with basic routing
- [ ] Update chat endpoint to use routing
- [ ] Make filters actually work (not `filters = {}`)

---

## 🎯 **Success Metrics**

**Before:**
- Query: "Find duplicate invoices" → LLM tries to infer from chunks
- Query: "Show invoice INV-12345" → Vector search all chunks
- Query: "Which invoices are missing PO?" → LLM guesses from text

**After:**
- Query: "Find duplicate invoices" → Analytics engine returns exact matches
- Query: "Show invoice INV-12345" → Structured lookup returns document instantly
- Query: "Which invoices are missing PO?" → Filter on `flags.po_missing = true`

---

## 📁 **File Structure (After Implementation)**

```
finalinvoicerag_v3/
├── app.py                          ← Updated with routing
├── cosmos_store.py                 ← 3 containers + structured queries
├── cosmos_hybrid_retriever.py      ← Compatibility wrapper
├── metadata_extractor.py           ← Delegates to invoice_extractor
├── query_classifier.py             ← Delegates to invoice_router
│
├── invoice_schema.py               ← NEW: Data models
├── invoice_extractor.py            ← NEW: Extract invoice fields
├── invoice_chunker.py              ← NEW: Field-aware chunking
├── invoice_router.py               ← NEW: Deterministic routing
├── invoice_analytics.py            ← NEW: Rule-based analytics
├── answer_builder.py               ← NEW: Grounded answer composition
│
├── requirements.txt
├── .env
└── public/
```

---

## 🚀 **Let's Start!**

**Next Step:** Implement Phase 1 - Structured Invoice Extraction

Ready to begin? 🎯

