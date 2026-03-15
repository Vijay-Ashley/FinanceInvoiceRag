# 🚀 Deploy v4.0 to Your Existing GitHub Repository

## 📍 Your Repository
**URL:** https://github.com/Vijay-Ashley/FinanceInvoiceRag.git

---

## ⚡ Quick Deployment (Recommended)

### **Option 1: Automated Script (Easiest)**

Open PowerShell in `finalinvoicerag_v4` directory:

```powershell
cd finalinvoicerag_v4
.\deploy_to_existing_repo.ps1
```

**What it does:**
1. ✅ Removes old git history
2. ✅ Initializes fresh git repo
3. ✅ Adds all v4 files
4. ✅ Commits with detailed message
5. ✅ Force pushes to your GitHub repo (replaces everything)

---

### **Option 2: Manual Deployment**

If the script doesn't work, do it manually:

```powershell
# Navigate to v4 folder
cd finalinvoicerag_v4

# Remove old git (if exists)
Remove-Item -Path ".git" -Recurse -Force -ErrorAction SilentlyContinue

# Initialize new git
git init

# Add all files
git add .

# Commit
git commit -m "v4.0: Invoice Intelligence Platform - Complete rewrite"

# Add your repository
git remote add origin https://github.com/Vijay-Ashley/FinanceInvoiceRag.git

# Force push (replaces everything)
git branch -M main
git push -f origin main
```

---

## 🔐 Authentication

### **If you get authentication errors:**

#### **Method 1: Personal Access Token (Recommended)**

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (all)
4. Copy the token
5. When prompted for password, use the token instead

#### **Method 2: GitHub CLI**

```powershell
# Install GitHub CLI
winget install GitHub.cli

# Login
gh auth login

# Then push
git push -f origin main
```

#### **Method 3: Use GitHub Desktop**

1. Open GitHub Desktop
2. File → Add Local Repository
3. Select `finalinvoicerag_v4` folder
4. Publish repository (force push)

---

## ✅ What Will Be Pushed

### **Included (will be on GitHub):**
- ✅ All Python code (`app.py`, `invoice_extractor.py`, etc.)
- ✅ UI source code (`ui/src/`)
- ✅ README.md and all documentation
- ✅ requirements.txt
- ✅ Deployment scripts
- ✅ Configuration templates

### **Excluded (protected by .gitignore):**
- ❌ `.env` - Your secrets stay safe!
- ❌ `__pycache__/` - Python cache
- ❌ `ui/node_modules/` - Node dependencies
- ❌ `uploads/` - User data
- ❌ `*.log` - Log files

---

## 🔍 Verify Deployment

After pushing, check:

1. **Visit your repo:** https://github.com/Vijay-Ashley/FinanceInvoiceRag

2. **You should see:**
   - ✅ README.md as the main page
   - ✅ All Python files
   - ✅ `ui/` folder with React code
   - ✅ Documentation files
   - ✅ No `.env` file (good!)

3. **Check the commit:**
   - Should say "v4.0: Invoice Intelligence Platform"
   - Should show ~50 files changed

---

## 🖥️ Deploy to VM After GitHub Push

Once code is on GitHub:

```bash
# Connect to VM
ssh azureuser@YOUR_VM_IP

# Navigate to app directory
cd /home/azureuser/rag_pdf_finance

# Backup current code (optional)
cp -r . ../rag_pdf_finance_backup_$(date +%Y%m%d)

# Pull new code (will replace everything)
git fetch origin
git reset --hard origin/main

# Verify .env file exists
ls -la .env

# If .env is missing, copy from backup
# cp ../rag_pdf_finance_backup_*/. env .env

# Restart service
sudo systemctl restart rag-api

# Check logs
sudo journalctl -u rag-api -f
```

**Look for:**
```
🏗️  Invoice Intelligence: Multi-container structure enabled
✅ System initialized!
```

---

## 🧪 Test After Deployment

### **1. Health Check**
```bash
curl http://localhost:9000/health
```

### **2. Upload Invoice**
```bash
curl -X POST http://YOUR_VM_IP:9000/api/upload \
  -F "files=@test_invoice.pdf"
```

### **3. Check Extraction**
```bash
curl http://localhost:9000/api/invoices
```

**Should show improved extraction:**
- Invoice Number: "5440612345" ✅ (not "Invoice")
- Vendor: "Google LLC" ✅ (not "Bill to...")
- Total: "$195,652.18" ✅ (not null)

---

## 🔧 Troubleshooting

### **Issue: Authentication Failed**

**Solution 1: Use Personal Access Token**
```powershell
# When prompted for password, use your GitHub token
git push -f origin main
# Username: Vijay-Ashley
# Password: ghp_YOUR_TOKEN_HERE
```

**Solution 2: Configure credential helper**
```powershell
git config --global credential.helper wincred
git push -f origin main
```

### **Issue: Push Rejected**

**Solution: Force push (you want to replace everything)**
```powershell
git push -f origin main
```

### **Issue: .env Missing on VM**

**Solution: Copy from backup or recreate**
```bash
# On VM
nano .env
# Paste your configuration
```

---

## 📋 Deployment Checklist

**Before Pushing to GitHub:**
- [ ] In `finalinvoicerag_v4` directory
- [ ] `.env` file exists locally (won't be pushed)
- [ ] `.gitignore` configured correctly
- [ ] README.md looks good

**After Pushing to GitHub:**
- [ ] Visit https://github.com/Vijay-Ashley/FinanceInvoiceRag
- [ ] Verify README displays correctly
- [ ] Check no `.env` file visible
- [ ] Verify all code files present

**After Deploying to VM:**
- [ ] Code pulled successfully
- [ ] `.env` file exists on VM
- [ ] Service restarted
- [ ] Health check passes
- [ ] Invoice upload works
- [ ] Extraction improved

---

## 🎯 Quick Commands Summary

**Push to GitHub:**
```powershell
cd finalinvoicerag_v4
.\deploy_to_existing_repo.ps1
```

**Deploy to VM:**
```bash
ssh azureuser@YOUR_VM_IP
cd /home/azureuser/rag_pdf_finance
git reset --hard origin/main
sudo systemctl restart rag-api
```

**Verify:**
```bash
curl http://localhost:9000/api/invoices
```

---

## 💡 Important Notes

1. **Force Push:** This will **replace all code** in your GitHub repo
2. **Backup:** Old code will be gone from GitHub (but you have v3 locally)
3. **.env Safety:** Your `.env` file will NOT be pushed to GitHub
4. **VM .env:** Make sure `.env` exists on VM after pulling

---

## ✅ Success Criteria

Deployment is successful when:

1. **GitHub:**
   - ✅ Repository shows v4.0 code
   - ✅ README.md displays correctly
   - ✅ No `.env` file visible

2. **VM:**
   - ✅ Service starts without errors
   - ✅ Extraction shows improved accuracy
   - ✅ API endpoints work

---

**Ready to deploy? Run the script!** 🚀

```powershell
cd finalinvoicerag_v4
.\deploy_to_existing_repo.ps1
```

