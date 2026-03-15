# ⚡ Quick Start - Invoice Intelligence

## 🎯 Goal
Get Invoice Intelligence up and running in 5 minutes!

---

## 📋 Prerequisites

- ✅ Python 3.11+ installed
- ✅ Azure Cosmos DB account
- ✅ Azure OpenAI access

---

## 🚀 Setup (One-Time)

### Step 1: Create Cosmos DB Containers (REQUIRED)

```bash
cd finalinvoicerag_v3
python setup_cosmos_containers.py
```

**Expected output:**
```
✅ Created container: invoice_documents
✅ Created container: invoice_chunks
✅ Created container: invoice_query_audit
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Start Server

```bash
python -m uvicorn app:app --reload --port 9000
```

**Look for this log:**
```
🏗️  Invoice Intelligence: Multi-container structure enabled
```

✅ **If you see this, you're ready!**

---

## 🧪 Test It

### 1. Open UI
```
http://localhost:9000
```

### 2. Upload Invoice
- Click "Upload Files"
- Select a PDF invoice
- Wait for completion

### 3. Check Logs
```
✅ Invoice extracted: INV-12345, Vendor: Acme Corp, Total: $1234.56
```

### 4. Test New Endpoints

**List invoices:**
```bash
curl http://localhost:9000/api/invoices
```

**Run analytics:**
```bash
curl http://localhost:9000/api/analytics
```

**Get invoice details:**
```bash
curl http://localhost:9000/api/invoice/INV-12345
```

---

## 🎉 Success Criteria

- [x] Containers created in Cosmos DB
- [x] Server starts with "Invoice Intelligence enabled"
- [x] Upload shows "Invoice extracted" in logs
- [x] `/api/invoices` returns data
- [x] `/api/analytics` returns findings

---

## ❌ Troubleshooting

### "Invoice store initialization failed"

**Fix:**
```bash
python setup_cosmos_containers.py
```

### "Container not found"

**Fix:**
1. Check Azure Portal > Cosmos DB > Data Explorer
2. Verify containers exist:
   - `invoice_documents`
   - `invoice_chunks`
   - `invoice_query_audit`

### "No invoices returned"

**Fix:**
1. Upload a PDF invoice first
2. Check logs for "Invoice extracted"
3. Try again

---

## 📚 Next Steps

Once working:

1. **Read:** `TESTING_GUIDE.md` - Detailed testing
2. **Read:** `README_INVOICE_INTELLIGENCE.md` - Features overview
3. **Deploy:** Use `deploy_to_github.ps1` for VM deployment

---

## 🔗 Quick Links

| Task | Command |
|------|---------|
| **Setup containers** | `python setup_cosmos_containers.py` |
| **Start server** | `python -m uvicorn app:app --reload --port 9000` |
| **List invoices** | `curl http://localhost:9000/api/invoices` |
| **Run analytics** | `curl http://localhost:9000/api/analytics` |
| **View UI** | `http://localhost:9000` |

---

## 📊 What You Get

### Before (Generic RAG)
- ❌ Searches all chunks
- ❌ LLM guesses details
- ❌ No analytics

### After (Invoice Intelligence)
- ✅ Structured invoice data
- ✅ Duplicate detection
- ✅ Missing PO alerts
- ✅ Tax verification
- ✅ Analytics dashboard

---

**Ready?** Run this now:

```bash
python setup_cosmos_containers.py
```

Then:

```bash
python -m uvicorn app:app --reload --port 9000
```

🎉 **You're all set!**

