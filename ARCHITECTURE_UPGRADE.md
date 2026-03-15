# Invoice Intelligence Architecture Upgrade

## Overview
Transitioning from generic "chunk-based search" to structured "Invoice Intelligence" platform.

## Key Changes

### 1. Multi-Container Cosmos DB Structure

**Before:** Single container `documents` with all data mixed together

**After:** Three specialized containers:

```
invoice_documents/     # Canonical invoice JSON (headers, amounts, vendor info)
├── document_id (PK: tenant_id)
├── invoice_number, vendor_name, amounts, dates
├── flags (duplicate_risk, po_missing, amount_mismatch)
└── extraction_confidence scores

invoice_chunks/        # Searchable chunks with embeddings
├── chunk_id (PK: tenant_id)
├── document_id (foreign key)
├── chunk_type (header_fields, totals_block, line_item, etc.)
├── page_no, chunk_index
├── text, normalized_text
├── embedding vector
└── denormalized fields (invoice_number, vendor_name, total)

invoice_query_audit/   # Query tracking and analytics
├── query_id (PK: tenant_id)
├── query, intent, route
├── document_ids retrieved
└── latency, confidence metrics
```

### 2. Structured Invoice Extraction

**New Module:** `invoice_extractor.py`

**Extracts:**
- Invoice number, PO number
- Vendor name, address
- Invoice date, due date
- Subtotal, tax, total, currency
- Line items (description, quantity, unit price, amount)
- Confidence scores per field
- Flags (missing PO, amount mismatch, low OCR confidence)

**Method:** Regex patterns + LLM assistance for complex cases

### 3. Field-Aware Chunking

**New Module:** `invoice_chunker.py`

**Chunk Types:**
- `HEADER_FIELDS` - Invoice number, dates, PO
- `TOTALS_BLOCK` - Subtotal, tax, total
- `LINE_ITEM` - Individual line items
- `TERMS` - Payment terms, notes
- `PAGE_TEXT` - General page content

**Benefits:**
- Preserve page numbers and chunk indices
- Enable targeted retrieval (e.g., "get totals block")
- Better context for LLM

### 4. Query Routing

**New Module:** `invoice_router.py`

**Routes:**
- `EXACT_LOOKUP` → Structured document lookup (invoice #, PO #)
- `SEMANTIC_SEARCH` → Hybrid keyword + vector search
- `COMPARISON` → Analytics engine + supporting retrieval
- `LOSS_ANALYSIS` → Analytics engine + supporting retrieval
- `RECOMMENDATION` → Analytics engine + supporting retrieval

**Currently:** Classifier returns filters but they're ignored (`filters = {}`)
**After:** Filters actually control search path

### 5. Deterministic Analytics

**New Module:** `invoice_analytics.py`

**Rules:**
- `detect_duplicates()` - Same vendor, similar amount, close dates
- `find_missing_po()` - Invoices without PO numbers
- `detect_amount_mismatches()` - Subtotal + tax ≠ total
- `detect_tax_anomalies()` - Tax rate outside 0-15%
- `compare_invoices()` - Side-by-side comparison table
- `generate_recommendations()` - Actionable next steps

**Benefits:**
- Deterministic results (not LLM-dependent)
- Fast execution (Python logic, not LLM calls)
- Explainable findings

### 6. Server-Side Vector Search

**Current Issue:** Fallback to Python-side cosine similarity is the default path

**Fix:**
- Verify Cosmos vector index configuration
- Test `VectorDistance()` function directly
- Remove fallback as default
- Keep fallback only for emergency

**Benefits:**
- 10-100x faster at scale
- Lower memory usage
- Lower cost (no data transfer)

### 7. Dynamic Vendor Boosting

**Before:** Hardcoded list of vendors (Google, Adobe, Salesforce)

**After:**
- Extract vendor names from invoice fields
- Extract vendor entities from user query
- Boost based on actual stored vendor fields

### 8. LLM as Explainer, Not Reasoner

**Before:**
```
query → retrieve chunks → LLM reads chunks and infers everything
```

**After:**
```
query → classify → route → structured lookup / analytics → merge evidence → LLM explains
```

**Benefits:**
- Faster (less LLM processing)
- More accurate (deterministic logic)
- Cheaper (fewer tokens)
- Explainable (show the rules that fired)

## Implementation Status

✅ **Completed:**
- `invoice_schema.py` - Comprehensive data models
- `invoice_extractor.py` - Structured field extraction
- `invoice_analytics.py` - Deterministic analytics rules
- `IMPLEMENTATION_PLAN.md` - Step-by-step guide

🚧 **In Progress:**
- Update `cosmos_store.py` to use multi-container structure
- Update `app.py` to use new extraction and analytics
- Test server-side vector search

⏳ **Pending:**
- Update UI to show analytics findings
- Add comparison view
- Add recommendation panel

## Next Steps

1. **Update cosmos_store.py** - Add multi-container support
2. **Update app.py** - Integrate extraction and analytics
3. **Test with real invoices** - Verify extraction accuracy
4. **Measure performance** - Compare before/after

## Expected Improvements

- **Accuracy:** 60% → 90%+ (deterministic analytics)
- **Speed:** 3-5s → 1-2s (server-side vector search)
- **Relevance:** 13 sources → 1-2 sources (better routing)
- **Cost:** 50% reduction (fewer LLM calls)

