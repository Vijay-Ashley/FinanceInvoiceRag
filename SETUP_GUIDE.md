# 🚀 Setup Guide - Invoice Intelligence

## Prerequisites

Before you can test the Invoice Intelligence features, you need to:

1. ✅ Have Azure Cosmos DB credentials in `.env` file
2. ✅ Create the new Cosmos DB containers
3. ✅ Install Python dependencies

---

## Step 1: Verify .env File

Check that your `.env` file has these settings:

```env
# Azure Cosmos DB Configuration
COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key-here
COSMOS_DATABASE_NAME=rag_database

# Old container (backward compatibility)
COSMOS_CONTAINER_NAME=embeddings

# NEW: Invoice Intelligence Containers
COSMOS_INVOICE_DOCUMENTS_CONTAINER=invoice_documents
COSMOS_INVOICE_CHUNKS_CONTAINER=invoice_chunks
COSMOS_INVOICE_AUDIT_CONTAINER=invoice_query_audit
```

**✅ Already updated!** Your `.env` file now has these settings.

---

## Step 2: Create Cosmos DB Containers

Run the setup script to create the required containers:

```bash
cd finalinvoicerag_v3
python setup_cosmos_containers.py
```

### Expected Output:

```
============================================================
Invoice Intelligence - Cosmos DB Setup
============================================================

🔗 Connecting to Cosmos DB: https://afi-mfg-pic-cosmos-db-dev.documents.azure.com:443/
📊 Database: rag_database
✅ Using existing database: rag_database
✅ Created container: invoice_documents
   📝 Structured invoice data (headers, amounts, line items, flags)
   🔑 Partition key: /tenant_id
   💰 Throughput: 400 RU/s
✅ Created container: invoice_chunks
   📝 Vector embeddings with invoice metadata
   🔑 Partition key: /tenant_id
   💰 Throughput: 400 RU/s
✅ Created container: invoice_query_audit
   📝 Query tracking and analytics
   🔑 Partition key: /tenant_id
   💰 Throughput: 400 RU/s

============================================================
✅ Cosmos DB Setup Complete!
============================================================

Containers created:
  1. invoice_documents - Structured invoice data
  2. invoice_chunks - Vector embeddings
  3. invoice_query_audit - Query tracking

Next steps:
  1. Verify containers in Azure Portal
  2. Update .env file (if needed)
  3. Run: python -m uvicorn app:app --reload
============================================================
```

### If Containers Already Exist:

```
⚠️  Container already exists: invoice_documents
   📝 Structured invoice data (headers, amounts, line items, flags)
```

This is OK! It means the containers were created previously.

---

## Step 3: Verify in Azure Portal

1. Open [Azure Portal](https://portal.azure.com)
2. Navigate to your Cosmos DB account: `afi-mfg-pic-cosmos-db-dev`
3. Go to **Data Explorer**
4. Expand database: `rag_database`
5. Verify these containers exist:
   - ✅ `embeddings` (old container)
   - ✅ `invoice_documents` (new)
   - ✅ `invoice_chunks` (new)
   - ✅ `invoice_query_audit` (new)

---

## Step 4: Install Dependencies

Make sure all Python packages are installed:

```bash
pip install -r requirements.txt
```

### Key Dependencies:
- `azure-cosmos` - Cosmos DB SDK
- `langchain-openai` - Azure OpenAI integration
- `pydantic` - Data validation
- `fastapi` - Web framework
- `python-dotenv` - Environment variables

---

## Step 5: Start the Application

```bash
python -m uvicorn app:app --reload --host 0.0.0.0 --port 9000
```

### Expected Startup Logs:

```
🚀 Initializing Production RAG System...
✅ System initialized!
   📊 Config: TOP_K=20, WORKERS=8, BATCH=50
   💾 Memory optimized with batched processing
   🏗️  Invoice Intelligence: Multi-container structure enabled
INFO:     Uvicorn running on http://0.0.0.0:9000
```

**✅ If you see "Invoice Intelligence: Multi-container structure enabled"** - Success!

**⚠️ If you see a warning:**
```
⚠️  Invoice store initialization failed (non-critical): ...
```
This means the containers don't exist yet. Run `setup_cosmos_containers.py` first.

---

## Step 6: Test the Setup

### Test 1: Upload an Invoice

```bash
curl -X POST http://localhost:9000/api/upload \
  -F "files=@sample_invoice.pdf"
```

**Expected log:**
```
✅ Invoice extracted: INV-12345, Vendor: Acme Corp, Total: $1234.56
```

### Test 2: List Invoices

```bash
curl http://localhost:9000/api/invoices
```

**Expected response:**
```json
{
  "count": 1,
  "invoices": [...]
}
```

### Test 3: Run Analytics

```bash
curl http://localhost:9000/api/analytics
```

**Expected response:**
```json
{
  "summary": {...},
  "findings": [...],
  "recommendations": [...]
}
```

---

## Troubleshooting

### Issue: "Container not found"

**Solution:**
```bash
python setup_cosmos_containers.py
```

### Issue: "Authentication failed"

**Solution:**
1. Verify `COSMOS_ENDPOINT` and `COSMOS_KEY` in `.env`
2. Check Azure Portal > Cosmos DB > Keys
3. Copy the correct values

### Issue: "Invoice store initialization failed"

**Solution:**
1. Run `setup_cosmos_containers.py`
2. Verify containers exist in Azure Portal
3. Restart the application

### Issue: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

---

## Summary

✅ **Setup Checklist:**

- [x] `.env` file updated with container names
- [ ] Run `python setup_cosmos_containers.py`
- [ ] Verify containers in Azure Portal
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Start app: `python -m uvicorn app:app --reload --port 9000`
- [ ] Test upload and endpoints

---

## Next Steps

Once setup is complete:

1. **Read:** `TESTING_GUIDE.md` - Detailed testing instructions
2. **Read:** `README_INVOICE_INTELLIGENCE.md` - Feature overview
3. **Upload:** Sample invoices and test the new features
4. **Deploy:** Use `deploy_to_github.ps1` to deploy to VM

---

## Quick Commands

```bash
# Create containers
python setup_cosmos_containers.py

# Start server
python -m uvicorn app:app --reload --port 9000

# Test upload
curl -X POST http://localhost:9000/api/upload -F "files=@invoice.pdf"

# List invoices
curl http://localhost:9000/api/invoices

# Run analytics
curl http://localhost:9000/api/analytics
```

---

**Ready to start?** Run this now:

```bash
python setup_cosmos_containers.py
```

