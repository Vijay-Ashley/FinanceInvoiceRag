# Integration Steps - Invoice Intelligence

## Phase 1: Update Imports and Initialization

### 1.1 Update Imports
```python
# Replace old imports
from cosmos_store import CosmosVectorStore
from metadata_extractor import MetadataExtractor

# With new imports
from cosmos_store_new import InvoiceCosmosStore
from invoice_extractor import InvoiceExtractor
from invoice_analytics import InvoiceAnalytics
from invoice_chunker import InvoiceChunker  # If available
from invoice_router import InvoiceRouter      # If available
```

### 1.2 Update Global Variables
```python
# Replace
cosmos_store: Optional[CosmosVectorStore] = None

# With
cosmos_store: Optional[InvoiceCosmosStore] = None
```

### 1.3 Update Startup Event
```python
@app.on_event("startup")
async def startup_event():
    global cosmos_store, ...
    
    # Replace
    cosmos_store = CosmosVectorStore()
    
    # With
    cosmos_store = InvoiceCosmosStore()
```

---

## Phase 2: Update Upload Flow

### 2.1 Replace Metadata Extraction
**Current (line ~456):**
```python
metadatas = [
    MetadataExtractor.extract_metadata(
        text=chunk,
        source=filename,
        page=0,
        chunk_index=i
    )
    for i, chunk in enumerate(chunks)
]
```

**New:**
```python
# Step 1: Extract structured invoice data
invoice_doc = InvoiceExtractor.extract_invoice(
    text=text,
    filename=filename,
    tenant_id="default"
)

# Step 2: Save invoice document to invoice_documents container
cosmos_store.save_invoice_document(invoice_doc)

# Step 3: Create field-aware chunks
from invoice_chunker import InvoiceChunker
invoice_chunks = InvoiceChunker.chunk_invoice(
    invoice_doc=invoice_doc,
    embeddings_func=embeddings.embed_documents  # Pass embedding function
)

# Step 4: Save chunks to invoice_chunks container
cosmos_store.save_invoice_chunks(invoice_chunks)
```

### 2.2 Update Progress Messages
```python
update_status("extracting", 10, "Extracting invoice fields...")
update_status("analyzing", 20, "Analyzing invoice structure...")
update_status("chunking", 40, "Creating field-aware chunks...")
update_status("embedding", 60, "Generating embeddings...")
update_status("storing", 80, "Saving to database...")
```

---

## Phase 3: Update Chat/Search Flow

### 3.1 Add Query Routing
**Current (line ~555):**
```python
query_classification = QueryClassifier.classify(clean_question)
# ... but filters are ignored
filters = {}  # No filters - search everything
```

**New:**
```python
# Step 1: Route the query
from invoice_router import InvoiceRouter
query_plan = InvoiceRouter.route_query(clean_question)

logger.info(f"🎯 Intent: {query_plan.intent}, Filters: {query_plan.filters}")

# Step 2: Execute based on intent
if query_plan.intent == "EXACT_LOOKUP":
    # Structured document lookup
    documents = cosmos_store.lookup_documents(
        tenant_id="default",
        filters=query_plan.filters,
        top_k=10
    )
    # Convert to evidence format
    results = convert_documents_to_evidence(documents)
    
elif query_plan.intent in ["COMPARISON", "LOSS_ANALYSIS", "RECOMMENDATION"]:
    # Analytics-first path
    documents = cosmos_store.lookup_documents(
        tenant_id="default",
        filters=query_plan.filters,
        top_k=50
    )
    
    # Run analytics
    analytics_results = InvoiceAnalytics.run_all_analytics(documents)
    
    # Build context from analytics findings
    context = build_analytics_context(analytics_results, clean_question)
    
else:
    # Semantic/hybrid search (existing path)
    results = hybrid_retriever.hybrid_search(...)
```

### 3.2 Update Context Building
```python
# Add analytics findings to context
if analytics_results:
    context_parts.append("## Analytics Findings:")
    for finding in analytics_results['findings']:
        context_parts.append(f"- {finding.title}: {finding.description}")
    
    if analytics_results['recommendations']:
        context_parts.append("\n## Recommendations:")
        for rec in analytics_results['recommendations']:
            context_parts.append(f"- [{rec.priority}] {rec.action}")
```

---

## Phase 4: Add Analytics Endpoint

### 4.1 Create Analytics Endpoint
```python
@app.post("/api/analytics")
async def api_analytics():
    """Run analytics on all invoices"""
    try:
        # Get all invoice documents
        documents = cosmos_store.get_all_documents(tenant_id="default")
        
        # Run analytics
        results = InvoiceAnalytics.run_all_analytics(documents)
        
        return {
            "summary": results['summary'],
            "findings": [f.model_dump() for f in results['findings']],
            "recommendations": [r.model_dump() for r in results['recommendations']],
            "comparison": [c.model_dump() for c in results['comparison']]
        }
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Phase 5: Testing

### 5.1 Test Upload
1. Upload a sample invoice PDF
2. Check logs for extraction results
3. Verify data in Cosmos DB containers

### 5.2 Test Search
1. Query: "What is the total for invoice INV-001?"
2. Should route to EXACT_LOOKUP
3. Should return structured data

### 5.3 Test Analytics
1. Upload 2-3 invoices
2. Call `/api/analytics`
3. Check for duplicate detection, missing PO, etc.

---

## Rollback Plan

If anything goes wrong:
```bash
# Restore backup
Copy-Item "app_backup_before_integration.py" -Destination "app.py" -Force

# Restart server
python -m uvicorn app:app --reload
```

---

## Success Criteria

✅ Upload extracts structured invoice fields
✅ Cosmos DB has data in 3 containers
✅ Search uses query routing
✅ Analytics endpoint returns findings
✅ No errors in logs
✅ UI shows improved results (1-2 sources instead of 13)

