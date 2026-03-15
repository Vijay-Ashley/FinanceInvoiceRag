# 🚀 Invoice RAG v3 - Deployment Guide

## 📚 **Available Deployment Methods**

| Method | Use Case | Guide |
|--------|----------|-------|
| **Git Push/Pull** ✅ | Update existing VM installation | `VM_UPDATE_GUIDE.md` |
| **SCP/Zip** | One-time deployment or no git access | `VM_DEPLOYMENT_STEPS.md` |
| **Quick Reference** | Fast lookup | `QUICK_DEPLOY.md` |

---

## ⚡ **Recommended: Git Push/Pull Method**

### **Why This Method?**
- ✅ **Easiest updates** - Just `git pull` on VM
- ✅ **Version control** - Track all changes
- ✅ **Rollback support** - Easy to revert if needed
- ✅ **No manual file transfer** - Automated workflow
- ✅ **Team collaboration** - Multiple developers can contribute

---

## 🎯 **Quick Start (Git Method)**

### **1. On Windows (One Command)**

```powershell
cd finalinvoicerag_v3
.\deploy_to_github.ps1
```

This will:
- Build the React UI
- Copy to `public/` folder
- Commit changes
- Push to GitHub

---

### **2. On VM (First Time Setup)**

```bash
# Clone repository
git clone https://github.com/Vijay-Ashley/FinanceInvoiceRag.git
cd FinanceInvoiceRag

# Setup Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env
# Add your credentials

# Run
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

---

### **3. On VM (Future Updates)**

```bash
# Pull latest changes
cd FinanceInvoiceRag
git pull origin main

# Restart service
sudo systemctl restart invoice-rag
```

**That's it!** 🎉

---

## 📁 **Project Structure**

```
finalinvoicerag_v3/
├── app.py                          ← Main application (FIXED: deduplication)
├── cosmos_hybrid_retriever.py      ← Hybrid search
├── cosmos_store.py                 ← Cosmos DB integration
├── metadata_extractor.py           ← PDF metadata extraction
├── query_classifier.py             ← Query classification
├── requirements.txt                ← Python dependencies
│
├── public/                         ← Built UI (auto-generated)
│   ├── index.html
│   └── assets/
│
├── ui/                             ← UI source code
│   ├── src/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── uploads/                        ← User uploads (ignored by git)
│
├── build_ui.ps1                    ← Build UI script
├── deploy_to_github.ps1            ← Deploy to GitHub script
│
├── VM_UPDATE_GUIDE.md              ← Git push/pull guide
├── VM_DEPLOYMENT_STEPS.md          ← SCP/zip deployment guide
├── QUICK_DEPLOY.md                 ← Quick reference
└── README_DEPLOYMENT.md            ← This file
```

---

## 🔧 **What Changed in This Update**

### **Backend Fix (app.py)**

**Before:**
```python
# Added every chunk as a source (20 chunks = 13 duplicate documents)
sources.append({
    "source": metadata["source"],
    "page": metadata["page"],
    "score": round(float(score), 4)
})
```

**After:**
```python
# Keep only the best score for each unique document
doc_name = metadata["source"]
if doc_name not in seen_documents or score > seen_documents[doc_name]["score"]:
    seen_documents[doc_name] = {
        "source": doc_name,
        "page": metadata["page"],
        "score": round(float(score), 4)
    }

# Return only unique documents (not every chunk)
sources = list(seen_documents.values())
```

**Result:** Shows only 2-3 relevant invoices instead of all 13! ✅

---

## 📋 **Deployment Checklist**

### **First Time Deployment**
- [ ] Build UI: `.\build_ui.ps1`
- [ ] Push to GitHub: `.\deploy_to_github.ps1`
- [ ] Clone on VM: `git clone <repo>`
- [ ] Setup Python environment
- [ ] Create `.env` file
- [ ] Configure systemd service
- [ ] Test application

### **Future Updates**
- [ ] Build UI: `.\build_ui.ps1`
- [ ] Push to GitHub: `.\deploy_to_github.ps1`
- [ ] Pull on VM: `git pull origin main`
- [ ] Restart service: `sudo systemctl restart invoice-rag`
- [ ] Verify in browser

---

## 🧪 **Testing**

After deployment, verify:

```bash
# Health check
curl http://your-vm-ip:9000/health
```

**Browser test:**
1. Open: `http://your-vm-ip:9000`
2. Ask: "What is the total amount for Colabs Holdings?"
3. Check sources section
4. **Expected:** Only 1-2 relevant invoices shown ✅
5. **Before:** All 13 invoices shown ❌

---

## 📞 **Support & Documentation**

| Document | Purpose |
|----------|---------|
| `VM_UPDATE_GUIDE.md` | Git push/pull deployment (recommended) |
| `VM_DEPLOYMENT_STEPS.md` | SCP/zip deployment (alternative) |
| `QUICK_DEPLOY.md` | Quick reference commands |
| `README_DEPLOYMENT.md` | This overview document |

---

## 🎯 **Next Steps**

1. **Read:** `VM_UPDATE_GUIDE.md` for detailed instructions
2. **Run:** `.\deploy_to_github.ps1` to push changes
3. **Deploy:** Follow VM update steps
4. **Test:** Verify sources are deduplicated

---

**Questions?** Check the troubleshooting section in `VM_UPDATE_GUIDE.md`

**Ready to deploy?** Run `.\deploy_to_github.ps1` now! 🚀

