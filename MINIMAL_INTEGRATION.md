# Minimal Viable Integration Plan

## Problem
The new `InvoiceCosmosStore` has a different API than the old `CosmosVectorStore`. 
We can't do a direct replacement without breaking existing functionality.

## Solution: Dual-Mode Operation

Keep both stores running side-by-side:
- **Old store** (`CosmosVectorStore`) - For backward compatibility
- **New store** (`InvoiceCosmosStore`) - For invoice intelligence features

## Implementation Steps

### Step 1: Add New Store Alongside Old One

```python
# Global components
cosmos_store: Optional[CosmosVectorStore] = None  # Keep old store
invoice_store: Optional[InvoiceCosmosStore] = None  # Add new store
```

### Step 2: Initialize Both Stores

```python
@app.on_event("startup")
async def startup_event():
    global cosmos_store, invoice_store, ...
    
    # Old store (for backward compatibility)
    cosmos_store = CosmosVectorStore()
    
    # New store (for invoice intelligence)
    invoice_store = InvoiceCosmosStore()
```

### Step 3: Enhance Upload to Use Both Stores

```python
async def process_file_background(file_bytes: bytes, filename: str, file_id: str):
    # ... existing code for old store ...
    
    # NEW: Also extract structured invoice data
    try:
        if filename.lower().endswith('.pdf'):
            update_status("analyzing", 25, "Extracting invoice fields...")
            
            invoice_doc = InvoiceExtractor.extract_invoice(
                text=text,
                filename=filename,
                tenant_id="default"
            )
            
            # Save to new store
            invoice_store.save_invoice_document(invoice_doc)
            
            logger.info(f"✅ Invoice extracted: {invoice_doc.invoice.invoice_number}")
    except Exception as e:
        logger.warning(f"Invoice extraction failed (non-critical): {e}")
        # Continue with old flow
```

### Step 4: Add Analytics Endpoint

```python
@app.get("/api/analytics")
async def api_analytics():
    """Get analytics for all invoices"""
    try:
        # Get all documents from new store
        documents = invoice_store.lookup_documents(
            tenant_id="default",
            filters={},
            top_k=1000
        )
        
        if not documents:
            return {
                "summary": {"total_documents": 0},
                "findings": [],
                "recommendations": []
            }
        
        # Run analytics
        results = InvoiceAnalytics.run_all_analytics(documents)
        
        return {
            "summary": results['summary'],
            "findings": [f.model_dump() for f in results['findings']],
            "recommendations": [r.model_dump() for r in results['recommendations']]
        }
    except Exception as e:
        logger.error(f"Analytics failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 5: Add Invoice Lookup Endpoint

```python
@app.get("/api/invoices")
async def api_get_invoices(
    invoice_number: Optional[str] = None,
    vendor: Optional[str] = None,
    limit: int = 50
):
    """Get invoices with optional filters"""
    try:
        filters = {}
        if invoice_number:
            filters["invoice_numbers"] = [invoice_number]
        if vendor:
            filters["vendor_names"] = [vendor]
        
        documents = invoice_store.lookup_documents(
            tenant_id="default",
            filters=filters,
            top_k=limit
        )
        
        return {
            "count": len(documents),
            "invoices": [
                {
                    "id": doc.id,
                    "invoice_number": doc.invoice.invoice_number,
                    "vendor": doc.vendor.name,
                    "total": float(doc.invoice.amounts.total) if doc.invoice.amounts.total else None,
                    "date": doc.invoice.invoice_date.isoformat() if doc.invoice.invoice_date else None,
                    "po_number": doc.invoice.po_number,
                    "flags": doc.flags.model_dump()
                }
                for doc in documents
            ]
        }
    except Exception as e:
        logger.error(f"Invoice lookup failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

## Benefits of This Approach

✅ **No Breaking Changes** - Old functionality continues to work
✅ **Gradual Migration** - Can test new features without risk
✅ **Fallback** - If new store fails, old store still works
✅ **Easy Rollback** - Just remove new endpoints if needed

## Testing Plan

1. **Upload a PDF invoice**
   - Old store: Creates chunks as before
   - New store: Extracts structured data
   - Both succeed independently

2. **Test old search** (`/api/chat`)
   - Should work exactly as before
   - Uses old store

3. **Test new endpoints**
   - `/api/analytics` - Shows findings
   - `/api/invoices` - Lists invoices

4. **Verify Cosmos DB**
   - Old container: `documents` (unchanged)
   - New containers: `invoice_documents`, `invoice_chunks`

## Next Phase (Future)

Once new store is proven:
1. Migrate chat endpoint to use invoice_store
2. Add query routing
3. Deprecate old store
4. Clean up old code

## Rollback

If anything breaks:
```bash
# Just comment out new store initialization
# invoice_store = InvoiceCosmosStore()  # DISABLED

# New endpoints will fail gracefully
# Old endpoints continue working
```

