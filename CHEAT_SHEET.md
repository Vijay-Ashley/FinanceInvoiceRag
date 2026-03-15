# 📋 Deployment Cheat Sheet

## ⚡ **Quick Commands**

### **On Windows (Deploy Changes)**

```powershell
# One command to do everything
.\deploy_to_github.ps1
```

**OR manually:**
```powershell
.\build_ui.ps1
git add app.py public/
git commit -m "Your message here"
git push origin main
```

---

### **On VM (Update)**

```bash
# One command to update and restart
cd /home/your-username/FinanceInvoiceRag && git pull origin main && sudo systemctl restart invoice-rag
```

**OR step by step:**
```bash
cd /home/your-username/FinanceInvoiceRag
git pull origin main
sudo systemctl restart invoice-rag
sudo systemctl status invoice-rag
```

---

## 🔍 **Check What Changed**

### **Before Pushing (Windows)**
```powershell
git status                    # See changed files
git diff app.py              # See line changes
git diff --stat              # See summary
```

### **Before Pulling (VM)**
```bash
git fetch origin main                    # Get latest info
git log HEAD..origin/main --oneline     # See new commits
git diff HEAD..origin/main --stat       # See what will change
```

---

## 📊 **Service Management (VM)**

```bash
# Start
sudo systemctl start invoice-rag

# Stop
sudo systemctl stop invoice-rag

# Restart
sudo systemctl restart invoice-rag

# Status
sudo systemctl status invoice-rag

# Logs (real-time)
sudo journalctl -u invoice-rag -f

# Logs (last 50 lines)
sudo journalctl -u invoice-rag -n 50
```

---

## 🧪 **Testing**

```bash
# Health check
curl http://localhost:9000/health

# From browser
http://your-vm-ip:9000
```

---

## 🔄 **Rollback (If Needed)**

```bash
# See recent commits
git log --oneline -5

# Rollback to specific commit
git reset --hard <commit-hash>

# Restart
sudo systemctl restart invoice-rag
```

---

## 🐛 **Troubleshooting**

```bash
# Port in use
sudo lsof -i :9000
sudo kill -9 $(sudo lsof -t -i:9000)

# Git conflicts
git status
git reset --hard origin/main
git pull origin main

# Service won't start
sudo journalctl -u invoice-rag -n 50
```

---

## 📁 **Important Files**

| File | Purpose |
|------|---------|
| `app.py` | Main application |
| `public/` | Built UI (auto-generated) |
| `.env` | Credentials (NOT in git) |
| `requirements.txt` | Python dependencies |

---

## ✅ **Deployment Checklist**

**Windows:**
- [ ] `.\build_ui.ps1`
- [ ] `.\deploy_to_github.ps1`

**VM:**
- [ ] `git pull origin main`
- [ ] `sudo systemctl restart invoice-rag`
- [ ] Test in browser
- [ ] Verify sources deduplicated

---

## 🎯 **What Changed**

**File:** `app.py` (Lines 632-645)

**Before:** Shows all 13 invoices
**After:** Shows only 2-3 relevant invoices

---

## 📞 **Full Guides**

- **Git Method:** `DEPLOY_RECENT_CHANGES.md`
- **VM Setup:** `VM_UPDATE_GUIDE.md`
- **Overview:** `README_DEPLOYMENT.md`

