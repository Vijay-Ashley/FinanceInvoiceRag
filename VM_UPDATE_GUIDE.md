# 🔄 VM Update Guide - Pull from GitHub

## 📋 **Two Deployment Options**

### **Option 1: Update Existing Installation (Recommended)**
Use this if you already have the app running on VM.

### **Option 2: Fresh Installation**
Use this for first-time deployment or if you want a clean start.

---

## ✅ **Option 1: Update Existing Installation**

### **On Windows (Local Machine)**

```powershell
# Navigate to project
cd "c:\Users\VVerma\OneDrive - Ashley Furniture Industries, Inc\Documents\AI coding\Ragincloud\ragf1\Ragforfinance\rag_pdf_finance\finalinvoicerag_v3"

# Build UI and push to GitHub
.\deploy_to_github.ps1
```

**What this does:**
1. Builds the React UI
2. Copies to `public/` folder
3. Commits changes to git
4. Pushes to GitHub

---

### **On VM (Linux)**

```bash
# 1. SSH to VM
ssh your-username@your-vm-ip

# 2. Navigate to existing project
cd /home/your-username/FinanceInvoiceRag
# OR wherever you installed it

# 3. Stop the running service
sudo systemctl stop invoice-rag
# OR if running manually:
# ps aux | grep uvicorn
# kill -9 <PID>

# 4. Backup current version (optional but recommended)
cp app.py app.py.backup.$(date +%Y%m%d)

# 5. Pull latest changes
git pull origin main

# 6. Activate virtual environment
source .venv/bin/activate

# 7. Update dependencies (if requirements.txt changed)
pip install -r requirements.txt --upgrade

# 8. Restart service
sudo systemctl start invoice-rag

# 9. Check status
sudo systemctl status invoice-rag

# 10. View logs
sudo journalctl -u invoice-rag -f
```

---

## 🆕 **Option 2: Fresh Installation**

### **On Windows (Local Machine)**

```powershell
# Same as Option 1
.\deploy_to_github.ps1
```

---

### **On VM (Linux)**

```bash
# 1. SSH to VM
ssh your-username@your-vm-ip

# 2. Create new directory
mkdir -p /home/your-username/apps
cd /home/your-username/apps

# 3. Clone repository
git clone https://github.com/Vijay-Ashley/FinanceInvoiceRag.git
cd FinanceInvoiceRag

# 4. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Create .env file
nano .env
```

**Add your credentials:**
```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small
COSMOS_ENDPOINT=your_cosmos_endpoint
COSMOS_KEY=your_cosmos_key
COSMOS_DATABASE_NAME=rag_finance_db
COSMOS_CONTAINER_NAME=documents
```

Save: `Ctrl+X`, `Y`, `Enter`

```bash
# 7. Create systemd service
sudo nano /etc/systemd/system/invoice-rag.service
```

**Add this content:**
```ini
[Unit]
Description=Invoice RAG v3 Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/apps/FinanceInvoiceRag
Environment="PATH=/home/your-username/apps/FinanceInvoiceRag/.venv/bin"
ExecStart=/home/your-username/apps/FinanceInvoiceRag/.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 8. Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable invoice-rag
sudo systemctl start invoice-rag

# 9. Check status
sudo systemctl status invoice-rag

# 10. Configure firewall
sudo ufw allow 9000/tcp
```

---

## 🧪 **Verify Deployment**

```bash
# Test health endpoint
curl http://localhost:9000/health

# Expected response:
# {"status":"ok"}
```

**From browser:**
1. Open: `http://your-vm-ip:9000`
2. Ask: "What is the total amount for Colabs Holdings?"
3. Check sources - should show **only 1-2 relevant invoices**, not all 13! ✅

---

## 📊 **Useful Commands**

### **Check Service Status**
```bash
sudo systemctl status invoice-rag
```

### **View Logs**
```bash
# Real-time logs
sudo journalctl -u invoice-rag -f

# Last 50 lines
sudo journalctl -u invoice-rag -n 50

# Logs from today
sudo journalctl -u invoice-rag --since today
```

### **Restart Service**
```bash
sudo systemctl restart invoice-rag
```

### **Stop Service**
```bash
sudo systemctl stop invoice-rag
```

### **Check if Port is in Use**
```bash
sudo lsof -i :9000
```

### **Kill Process on Port**
```bash
sudo kill -9 $(sudo lsof -t -i:9000)
```

---

## 🔄 **Future Updates (Quick Reference)**

```bash
# On Windows
.\deploy_to_github.ps1

# On VM
cd /home/your-username/FinanceInvoiceRag
git pull origin main
sudo systemctl restart invoice-rag
```

---

## ❓ **Troubleshooting**

### **Issue: Git pull fails**
```bash
# Check git status
git status

# Discard local changes
git reset --hard origin/main

# Pull again
git pull origin main
```

### **Issue: Service won't start**
```bash
# Check logs
sudo journalctl -u invoice-rag -n 50

# Check if port is in use
sudo lsof -i :9000

# Test manually
source .venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

### **Issue: Still showing all invoices**
```bash
# Verify you pulled latest code
git log -1

# Check app.py has the fix
grep -A 5 "seen_documents" app.py

# Restart service
sudo systemctl restart invoice-rag

# Clear browser cache
# Press Ctrl+Shift+R in browser
```

---

## ✅ **Deployment Checklist**

**On Windows:**
- [ ] Build UI with `.\build_ui.ps1`
- [ ] Push to GitHub with `.\deploy_to_github.ps1`

**On VM:**
- [ ] Pull latest changes: `git pull origin main`
- [ ] Update dependencies: `pip install -r requirements.txt --upgrade`
- [ ] Restart service: `sudo systemctl restart invoice-rag`
- [ ] Check logs: `sudo journalctl -u invoice-rag -f`
- [ ] Test in browser
- [ ] Verify sources are deduplicated

---

**🎉 Done! Your VM is now running the latest version!**

