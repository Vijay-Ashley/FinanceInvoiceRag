# 🔄 Deploy Only Recent Changes - Step by Step

## ✅ **Yes! Git will only update the changed files!**

When you do `git pull`, it only downloads and updates the files that changed. This is the beauty of Git! 🎯

---

## 📋 **Step-by-Step Guide**

### **Step 1: Check What Changed (On Windows)**

```powershell
# Navigate to project
cd "c:\Users\VVerma\OneDrive - Ashley Furniture Industries, Inc\Documents\AI coding\Ragincloud\ragf1\Ragforfinance\rag_pdf_finance\finalinvoicerag_v3"

# Check what files changed
git status
```

**You'll see:**
```
Changes not staged for commit:
  modified:   app.py
  modified:   public/index.html
  modified:   public/assets/index-abc123.js
```

---

### **Step 2: Build UI (On Windows)**

```powershell
# Build the React UI
.\build_ui.ps1
```

**What this does:**
- Compiles `ui/src/App.tsx` → `public/assets/index-*.js`
- Creates optimized production build
- Only the `public/` folder will be committed

---

### **Step 3: Review Changes Before Commit**

```powershell
# See what changed
git status

# See detailed changes in app.py
git diff app.py

# See all changes
git diff
```

**Expected changes:**
- ✅ `app.py` - Lines 632-645 (deduplication fix)
- ✅ `public/` folder - Built UI files

---

### **Step 4: Commit Only Changed Files**

```powershell
# Add only the files that changed
git add app.py
git add public/

# Commit with a clear message
git commit -m "Fix: Deduplicate sources - show only unique documents instead of all chunks"

# Check commit
git log -1 --stat
```

**You'll see:**
```
commit abc123...
Author: Your Name
Date: Thu Mar 13 2026

Fix: Deduplicate sources - show only unique documents instead of all chunks

 app.py                          | 15 ++++++++++++---
 public/assets/index-abc123.js   | 2 +-
 public/index.html               | 2 +-
 3 files changed, 14 insertions(+), 5 deletions(-)
```

---

### **Step 5: Push to GitHub**

```powershell
# Push only the new commit
git push origin main
```

**What gets uploaded:**
- ✅ Only the **changed lines** in `app.py`
- ✅ Only the **new files** in `public/`
- ❌ NOT the entire project (Git is smart!)

---

### **Step 6: Pull on VM (Only Downloads Changes)**

```bash
# SSH to VM
ssh your-username@your-vm-ip

# Navigate to project
cd /home/your-username/FinanceInvoiceRag

# Check current status
git status

# See what will be updated
git fetch origin main
git log HEAD..origin/main --oneline

# Pull ONLY the changes
git pull origin main
```

**What happens:**
```
Updating abc123..def456
Fast-forward
 app.py                          | 15 ++++++++++++---
 public/assets/index-abc123.js   | 2 +-
 public/index.html               | 2 +-
 3 files changed, 14 insertions(+), 5 deletions(-)
```

**Git only updates:**
- ✅ Lines 632-645 in `app.py`
- ✅ New files in `public/`
- ❌ Does NOT re-download entire project!

---

### **Step 7: Restart Service on VM**

```bash
# Restart the service
sudo systemctl restart invoice-rag

# Check status
sudo systemctl status invoice-rag

# View logs to confirm restart
sudo journalctl -u invoice-rag -f
```

---

### **Step 8: Verify Changes**

```bash
# Test health endpoint
curl http://localhost:9000/health

# Check which commit is running
git log -1 --oneline
```

**From browser:**
1. Open: `http://your-vm-ip:9000`
2. Clear cache: `Ctrl+Shift+R`
3. Ask: "What is the total amount for Colabs Holdings?"
4. **Verify:** Only 1-2 sources shown ✅

---

## 🎯 **Quick Commands Summary**

### **On Windows (One Script)**

```powershell
# Option 1: Use the automated script
.\deploy_to_github.ps1

# Option 2: Manual steps
.\build_ui.ps1
git add app.py public/
git commit -m "Fix: Deduplicate sources"
git push origin main
```

---

### **On VM (One Command)**

```bash
# Pull and restart
cd /home/your-username/FinanceInvoiceRag && \
git pull origin main && \
sudo systemctl restart invoice-rag && \
sudo systemctl status invoice-rag
```

---

## 📊 **What Gets Transferred?**

| Method | What Gets Transferred | Size |
|--------|----------------------|------|
| **Git Pull** | Only changed files (delta) | ~50 KB |
| **Full Clone** | Entire project | ~5 MB |
| **SCP Zip** | Entire package | ~10 MB |

**Git is the most efficient!** 🚀

---

## 🔍 **How to See Exactly What Changed**

### **Before Pushing (On Windows)**

```powershell
# See what files changed
git status

# See line-by-line changes
git diff app.py

# See summary of changes
git diff --stat
```

---

### **Before Pulling (On VM)**

```bash
# Fetch latest info (doesn't change files yet)
git fetch origin main

# See what commits are new
git log HEAD..origin/main --oneline

# See what files will change
git diff HEAD..origin/main --stat

# See detailed changes
git diff HEAD..origin/main
```

---

## ✅ **Advantages of Git Method**

1. **Efficient** - Only transfers changed bytes
2. **Safe** - Can review changes before applying
3. **Reversible** - Can rollback if needed
4. **Trackable** - Full history of changes
5. **Fast** - Only updates what changed

---

## 🔄 **Rollback if Needed**

```bash
# On VM, if something goes wrong
git log --oneline -5

# Rollback to previous commit
git reset --hard abc123

# Restart service
sudo systemctl restart invoice-rag
```

---

## 📝 **Example: What Actually Happens**

### **Scenario: You changed app.py**

**On Windows:**
```powershell
.\build_ui.ps1
git add app.py public/
git commit -m "Fix sources"
git push origin main
```

**Git uploads:**
- ✅ 15 changed lines in `app.py` (~500 bytes)
- ✅ New `public/assets/index-xyz.js` (~100 KB)
- ✅ Updated `public/index.html` (~2 KB)
- **Total: ~102 KB** (not the entire 5 MB project!)

**On VM:**
```bash
git pull origin main
```

**Git downloads:**
- ✅ Only the 102 KB of changes
- ✅ Updates only those 3 files
- ✅ Leaves everything else untouched

**Result:**
- ⚡ Fast (seconds, not minutes)
- 💾 Efficient (KB, not MB)
- ✅ Safe (only what changed)

---

## 🎯 **Your Exact Steps**

### **1. On Windows (First Time Setup)**

```powershell
cd finalinvoicerag_v3

# Initialize git if not already done
git init
git remote add origin https://github.com/Vijay-Ashley/FinanceInvoiceRag.git

# Build and push
.\deploy_to_github.ps1
```

---

### **2. On VM (First Time Setup)**

```bash
# Clone repository
git clone https://github.com/Vijay-Ashley/FinanceInvoiceRag.git
cd FinanceInvoiceRag

# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env
nano .env
# Add credentials

# Run
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

---

### **3. Future Updates (Every Time)**

**On Windows:**
```powershell
.\deploy_to_github.ps1
```

**On VM:**
```bash
cd FinanceInvoiceRag
git pull origin main
sudo systemctl restart invoice-rag
```

**That's it!** Only changed files are updated! 🎉

---

## ❓ **FAQ**

**Q: Will git pull download the entire project again?**
A: No! Only the changed files/lines.

**Q: What if I have local changes on VM?**
A: Git will warn you. Use `git stash` to save them or `git reset --hard` to discard.

**Q: Can I see what will change before pulling?**
A: Yes! Use `git fetch` then `git diff HEAD..origin/main`

**Q: What if the pull fails?**
A: Check `git status`, resolve conflicts, or use `git reset --hard origin/main`

---

**Ready?** Run `.\deploy_to_github.ps1` now! 🚀

