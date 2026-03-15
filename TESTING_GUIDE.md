# Testing Guide - Invoice Intelligence

## Quick Start

### 1. Start the Server

```powershell
cd finalinvoicerag_v3
python -m uvicorn app:app --reload --host 0.0.0.0 --port 9000
```

**Expected Output:**
```
✅ System initialized!
   📊 Config: TOP_K=5, WORKERS=4, BATCH=16
   💾 Memory optimized with batched processing
   🏗️  Invoice Intelligence: Multi-container structure enabled
INFO:     Uvicorn running on http://0.0.0.0:9000
```

---

## Test 1: Upload Invoice

### Via UI
1. Open: `http://localhost:9000`
2. Click "Upload Files"
3. Select a PDF invoice
4. Watch the progress

### Via API
```bash
curl -X POST http://localhost:9000/api/upload \
  -F "files=@path/to/invoice.pdf"
```

### Expected Logs
```
📊 invoice.pdf: [extracting] 10% - Extracting text...
📊 invoice.pdf: [analyzing] 20% - Extracting invoice fields...
✅ Invoice extracted: INV-12345, Vendor: Acme Corp, Total: $1234.56
📊 invoice.pdf: [chunking] 30% - Splitting into chunks...
📊 invoice.pdf: [embedding] 50% - Generating 15 embeddings...
📊 invoice.pdf: [storing] 80% - Saving to database...
📊 invoice.pdf: [completed] 100% - ✅ Successfully processed 15 chunks
```

**⚠️ If you see:**
```
⚠️  Invoice extraction failed (non-critical): ...
```
This is OK! The upload will still succeed using the old path.

---

## Test 2: List Invoices

### Request
```bash
curl http://localhost:9000/api/invoices
```

### Expected Response
```json
{
  "count": 3,
  "invoices": [
    {
      "id": "doc_abc123",
      "invoice_number": "INV-12345",
      "vendor": "Acme Corp",
      "total": 1234.56,
      "date": "2024-03-15",
      "po_number": "PO-98765",
      "flags": {
        "duplicate": false,
        "missing_po": false,
        "amount_mismatch": false,
        "needs_review": false
      },
      "filename": "invoice.pdf"
    }
  ]
}
```

### Filter by Invoice Number
```bash
curl "http://localhost:9000/api/invoices?invoice_number=INV-12345"
```

### Filter by Vendor
```bash
curl "http://localhost:9000/api/invoices?vendor=Acme"
```

---

## Test 3: Run Analytics

### Request
```bash
curl http://localhost:9000/api/analytics
```

### Expected Response
```json
{
  "summary": {
    "total_documents": 5,
    "total_invoices": 5,
    "total_amount": 12345.67,
    "issues_found": 2
  },
  "findings": [
    {
      "title": "Duplicate Invoice Detected",
      "severity": "HIGH",
      "description": "Invoice INV-12345 appears 2 times",
      "affected_documents": ["doc_1", "doc_2"],
      "recommendation": "Review and remove duplicate"
    },
    {
      "title": "Missing PO Number",
      "severity": "MEDIUM",
      "description": "Invoice INV-67890 has no PO number",
      "affected_documents": ["doc_3"],
      "recommendation": "Request PO number from vendor"
    }
  ],
  "recommendations": [
    {
      "priority": "HIGH",
      "action": "Review duplicate invoices",
      "reason": "Prevent double payment"
    }
  ]
}
```

---

## Test 4: Get Invoice Details

### Request
```bash
curl http://localhost:9000/api/invoice/INV-12345
```

### Expected Response
```json
{
  "invoice": {
    "number": "INV-12345",
    "date": "2024-03-15",
    "po_number": "PO-98765",
    "amounts": {
      "subtotal": 1000.00,
      "tax": 234.56,
      "total": 1234.56
    }
  },
  "vendor": {
    "name": "Acme Corp",
    "address": "123 Main St, City, ST 12345"
  },
  "line_items": [
    {
      "description": "Widget A",
      "quantity": 10,
      "unit_price": 50.00,
      "amount": 500.00
    },
    {
      "description": "Widget B",
      "quantity": 5,
      "unit_price": 100.00,
      "amount": 500.00
    }
  ],
  "flags": {
    "duplicate": false,
    "missing_po": false,
    "amount_mismatch": false,
    "needs_review": false
  },
  "metadata": {
    "filename": "invoice.pdf",
    "uploaded_at": "2024-03-15T10:30:00"
  }
}
```

---

## Test 5: Old Chat Endpoint (Backward Compatibility)

### Request
```bash
curl -X POST http://localhost:9000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the total for Acme Corp?"}'
```

### Expected Response
```json
{
  "answer": "Based on the uploaded invoices, Acme Corp has a total of $1,234.56 for invoice INV-12345...",
  "sources": [
    {
      "source": "invoice.pdf",
      "page": 0,
      "score": 0.8523
    }
  ],
  "processing_time": 2.34
}
```

**✅ This should work exactly as before!**

---

## Troubleshooting

### Issue: "Invoice Intelligence not available"

**Cause:** `invoice_store` failed to initialize

**Solution:**
1. Check Cosmos DB connection
2. Verify environment variables:
   ```
   COSMOS_ENDPOINT=https://...
   COSMOS_KEY=...
   COSMOS_DATABASE=...
   ```
3. Check logs for initialization errors

### Issue: No invoices returned

**Cause:** No invoices uploaded yet, or extraction failed

**Solution:**
1. Upload a PDF invoice
2. Check logs for extraction success
3. Verify Cosmos DB `invoice_documents` container has data

### Issue: Analytics returns empty

**Cause:** No invoice documents in the database

**Solution:**
1. Upload at least 2-3 invoices
2. Wait for upload to complete
3. Try analytics again

---

## Verification Checklist

After testing, verify:

- [ ] Server starts without errors
- [ ] Upload completes successfully
- [ ] Logs show "Invoice extracted: ..."
- [ ] `/api/invoices` returns data
- [ ] `/api/analytics` returns findings
- [ ] `/api/invoice/{number}` returns details
- [ ] Old `/api/chat` still works
- [ ] Cosmos DB has data in `invoice_documents` container

---

## Next Steps

Once all tests pass:

1. **Deploy to VM** using `deploy_to_github.ps1`
2. **Test on VM** with real invoice data
3. **Monitor logs** for any issues
4. **Iterate** based on results

---

## Support

If you encounter issues:

1. Check logs: `journalctl -u invoice-rag -f` (on VM)
2. Review `INTEGRATION_COMPLETE.md`
3. Check `MINIMAL_INTEGRATION.md` for architecture
4. Rollback if needed: `app_backup_before_integration.py`

