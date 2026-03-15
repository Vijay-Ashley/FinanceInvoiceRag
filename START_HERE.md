# 🚀 START HERE - Complete Deployment Guide

## 📋 **What You Need**

- ✅ Windows PC (local machine)
- ✅ Linux VM (Ubuntu/Debian)
- ✅ SSH access to VM
- ✅ GitHub account
- ✅ Azure OpenAI credentials
- ✅ Azure Cosmos DB credentials

---

## ⚡ **Quick Start (3 Steps)**

### **Step 1: Deploy from Windows**

```powershell
cd finalinvoicerag_v3
.\deploy_to_github.ps1
```

### **Step 2: Setup on VM (First Time)**

```bash
# SSH to VM
ssh your-username@your-vm-ip

# Clone repository
git clone https://github.com/Vijay-Ashley/FinanceInvoiceRag.git
cd FinanceInvoiceRag

# Setup Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env file
nano .env
```

**Add credentials:**
```env
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small
COSMOS_ENDPOINT=your_cosmos_endpoint
COSMOS_KEY=your_cosmos_key
COSMOS_DATABASE_NAME=rag_finance_db
COSMOS_CONTAINER_NAME=documents
```

Save: `Ctrl+X`, `Y`, `Enter`

```bash
# Run the app
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

### **Step 3: Test**

Open browser: `http://your-vm-ip:9000`

Ask: "What is the total amount for Colabs Holdings?"

**Expected:** Only 1-2 sources shown ✅

---

## 🔄 **Future Updates (2 Commands)**

### **On Windows:**
```powershell
.\deploy_to_github.ps1
```

### **On VM:**
```bash
cd ~/FinanceInvoiceRag
git pull origin main
# Restart the app (Ctrl+C and run again)
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

---

## 📚 **Documentation Guide**

| File | When to Read |
|------|-------------|
| **`START_HERE.md`** | 👈 You are here! |
| **`VM_RUN_OPTIONS.md`** | Choose how to run on VM |
| **`VM_SYSTEMD_SETUP.md`** | Production setup (auto-restart) |
| **`DEPLOY_RECENT_CHANGES.md`** | How git updates work |
| **`CHEAT_SHEET.md`** | Quick command reference |

---

## 🎯 **Choose Your Path**

### **Path A: Quick Testing (Recommended for First Time)**

1. ✅ Read: This file (`START_HERE.md`)
2. ✅ Run: `.\deploy_to_github.ps1` on Windows
3. ✅ Setup: Clone and run on VM (simple method)
4. ✅ Test: Verify in browser

**Time:** ~15 minutes

---

### **Path B: Production Setup**

1. ✅ Read: `VM_RUN_OPTIONS.md` (understand options)
2. ✅ Read: `VM_SYSTEMD_SETUP.md` (systemd service)
3. ✅ Run: `.\deploy_to_github.ps1` on Windows
4. ✅ Setup: Clone and configure systemd on VM
5. ✅ Test: Verify in browser

**Time:** ~30 minutes

---

## 🔧 **What Changed in This Update**

### **Problem:**
- Showing all 13 invoices as sources
- Duplicates from multiple chunks

### **Solution:**
- Deduplicate sources by document name
- Show only the best score per document
- Result: Only 2-3 relevant invoices shown

### **File Changed:**
- `app.py` (lines 632-645)

---

## 📊 **How Git Updates Work**

When you run `git pull` on VM:
- ✅ Downloads only changed files (~100 KB)
- ✅ Updates only modified lines
- ❌ Does NOT re-download entire project (5 MB)
- ⚡ Takes only 2-5 seconds

**Read more:** `DEPLOY_RECENT_CHANGES.md`

---

## 🎯 **Recommended Workflow**

### **Day 1: Initial Setup**

**On Windows:**
```powershell
cd finalinvoicerag_v3
.\deploy_to_github.ps1
```

**On VM:**
```bash
git clone https://github.com/Vijay-Ashley/FinanceInvoiceRag.git
cd FinanceInvoiceRag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
nano .env  # Add credentials
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

**Test in browser:** `http://your-vm-ip:9000`

---

### **Day 2: Production Setup (Optional)**

**On VM:**
```bash
# Create systemd service (see VM_SYSTEMD_SETUP.md)
sudo nano /etc/systemd/system/invoice-rag.service
sudo systemctl enable invoice-rag
sudo systemctl start invoice-rag
```

**Now it runs 24/7 with auto-restart!**

---

### **Day 3+: Updates**

**On Windows:**
```powershell
.\deploy_to_github.ps1
```

**On VM (Simple Run):**
```bash
cd ~/FinanceInvoiceRag
git pull origin main
# Ctrl+C to stop, then restart
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

**On VM (Systemd):**
```bash
cd ~/FinanceInvoiceRag
git pull origin main
sudo systemctl restart invoice-rag
```

---

## ✅ **Verification Checklist**

After deployment:

- [ ] Health check works: `curl http://localhost:9000/health`
- [ ] Browser access works: `http://your-vm-ip:9000`
- [ ] Can upload PDF
- [ ] Can ask questions
- [ ] Sources show only 2-3 invoices (not all 13)
- [ ] Answers are accurate

---

## 🐛 **Common Issues**

### **Issue: Can't access from browser**

```bash
# Check if app is running
ps aux | grep uvicorn

# Check if port is open
sudo lsof -i :9000

# Check firewall
sudo ufw status
sudo ufw allow 9000/tcp
```

### **Issue: Git pull fails**

```bash
# Check status
git status

# Discard local changes
git reset --hard origin/main

# Pull again
git pull origin main
```

### **Issue: Module not found**

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📞 **Need Help?**

| Question | Read This |
|----------|-----------|
| How to run on VM? | `VM_RUN_OPTIONS.md` |
| How to setup systemd? | `VM_SYSTEMD_SETUP.md` |
| How do git updates work? | `DEPLOY_RECENT_CHANGES.md` |
| Quick commands? | `CHEAT_SHEET.md` |

---

## 🎉 **You're Ready!**

### **Next Steps:**

1. **Run on Windows:**
   ```powershell
   .\deploy_to_github.ps1
   ```

2. **Setup on VM:**
   ```bash
   git clone https://github.com/Vijay-Ashley/FinanceInvoiceRag.git
   cd FinanceInvoiceRag
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   nano .env  # Add credentials
   python -m uvicorn app:app --host 0.0.0.0 --port 9000
   ```

3. **Test in browser:**
   `http://your-vm-ip:9000`

**That's it!** 🚀

---

**Questions?** Check the other documentation files or ask! 😊

