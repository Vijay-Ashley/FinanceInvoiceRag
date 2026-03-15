# 🔧 VM Systemd Service Setup - Complete Guide

## 📋 **What is Systemd?**

Systemd is a Linux service manager that:
- ✅ Auto-starts your app when VM boots
- ✅ Auto-restarts if app crashes
- ✅ Manages logs automatically
- ✅ Easy start/stop/restart commands

---

## 🚀 **Complete Setup Steps**

### **Step 1: SSH to VM**

```bash
ssh your-username@your-vm-ip
```

---

### **Step 2: Clone Repository (First Time Only)**

```bash
# Navigate to home directory
cd ~

# Clone repository
git clone https://github.com/Vijay-Ashley/FinanceInvoiceRag.git

# Navigate to project
cd FinanceInvoiceRag
```

---

### **Step 3: Setup Python Environment**

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

---

### **Step 4: Create .env File**

```bash
# Create .env file
nano .env
```

**Add your credentials:**
```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-3-small
COSMOS_ENDPOINT=https://your-cosmos.documents.azure.com:443/
COSMOS_KEY=your_cosmos_key_here
COSMOS_DATABASE_NAME=rag_finance_db
COSMOS_CONTAINER_NAME=documents
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

### **Step 5: Test Manual Run First**

```bash
# Make sure you're in the project directory
cd ~/FinanceInvoiceRag

# Activate virtual environment
source .venv/bin/activate

# Test run
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

**Test in browser:** `http://your-vm-ip:9000`

**If it works, press `Ctrl+C` to stop and continue to systemd setup.**

---

### **Step 6: Create Systemd Service File**

```bash
# Create service file
sudo nano /etc/systemd/system/invoice-rag.service
```

**Add this content (REPLACE `your-username` with your actual username):**

```ini
[Unit]
Description=Invoice RAG v3 Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/FinanceInvoiceRag
Environment="PATH=/home/your-username/FinanceInvoiceRag/.venv/bin"
ExecStart=/home/your-username/FinanceInvoiceRag/.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 9000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Important:** Replace `your-username` with your actual Linux username!

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

### **Step 7: Enable and Start Service**

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable invoice-rag

# Start service
sudo systemctl start invoice-rag

# Check status
sudo systemctl status invoice-rag
```

**Expected output:**
```
● invoice-rag.service - Invoice RAG v3 Service
     Loaded: loaded (/etc/systemd/system/invoice-rag.service; enabled)
     Active: active (running) since Thu 2026-03-13 10:30:00 UTC; 5s ago
   Main PID: 12345 (python)
      Tasks: 5 (limit: 4915)
     Memory: 150.0M
        CPU: 2.5s
     CGroup: /system.slice/invoice-rag.service
             └─12345 /home/your-username/FinanceInvoiceRag/.venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

---

### **Step 8: Configure Firewall**

```bash
# Allow port 9000
sudo ufw allow 9000/tcp

# Check firewall status
sudo ufw status
```

---

### **Step 9: Test the Service**

```bash
# Test health endpoint
curl http://localhost:9000/health

# Expected response:
# {"status":"ok"}
```

**From browser:** `http://your-vm-ip:9000`

---

## 🔄 **How to Update (After Systemd Setup)**

### **On Windows:**
```powershell
cd finalinvoicerag_v3
.\deploy_to_github.ps1
```

### **On VM:**
```bash
# 1. Navigate to project
cd ~/FinanceInvoiceRag

# 2. Pull latest changes
git pull origin main

# 3. Restart service
sudo systemctl restart invoice-rag

# 4. Check status
sudo systemctl status invoice-rag

# 5. View logs
sudo journalctl -u invoice-rag -f
```

**That's it!** The service will automatically use the new code! ✅

---

## 📊 **Systemd Commands Reference**

```bash
# Start service
sudo systemctl start invoice-rag

# Stop service
sudo systemctl stop invoice-rag

# Restart service
sudo systemctl restart invoice-rag

# Check status
sudo systemctl status invoice-rag

# Enable auto-start on boot
sudo systemctl enable invoice-rag

# Disable auto-start on boot
sudo systemctl disable invoice-rag

# View logs (real-time)
sudo journalctl -u invoice-rag -f

# View logs (last 50 lines)
sudo journalctl -u invoice-rag -n 50

# View logs (since today)
sudo journalctl -u invoice-rag --since today

# View logs (last hour)
sudo journalctl -u invoice-rag --since "1 hour ago"
```

---

## 🐛 **Troubleshooting**

### **Service won't start**

```bash
# Check detailed status
sudo systemctl status invoice-rag -l

# View error logs
sudo journalctl -u invoice-rag -n 50

# Check if port is in use
sudo lsof -i :9000

# Test manual run
cd ~/FinanceInvoiceRag
source .venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

### **Port already in use**

```bash
# Find process using port 9000
sudo lsof -i :9000

# Kill the process
sudo kill -9 <PID>

# Restart service
sudo systemctl restart invoice-rag
```

### **Permission denied**

```bash
# Check file ownership
ls -la ~/FinanceInvoiceRag

# Fix ownership (replace your-username)
sudo chown -R your-username:your-username ~/FinanceInvoiceRag

# Restart service
sudo systemctl restart invoice-rag
```

### **Service file changes not taking effect**

```bash
# After editing service file, always reload
sudo systemctl daemon-reload

# Then restart
sudo systemctl restart invoice-rag
```

---

## ✅ **Verification Checklist**

After setup, verify:

- [ ] Service is running: `sudo systemctl status invoice-rag`
- [ ] Health check works: `curl http://localhost:9000/health`
- [ ] Browser access works: `http://your-vm-ip:9000`
- [ ] Logs are clean: `sudo journalctl -u invoice-rag -n 20`
- [ ] Auto-start enabled: `sudo systemctl is-enabled invoice-rag`
- [ ] Firewall allows port: `sudo ufw status | grep 9000`

---

## 🎯 **Quick Update Workflow**

```bash
# One-liner to update and restart
cd ~/FinanceInvoiceRag && git pull origin main && sudo systemctl restart invoice-rag && sudo systemctl status invoice-rag
```

---

## 📝 **Example: Complete First-Time Setup**

```bash
# 1. SSH to VM
ssh user@192.168.1.100

# 2. Clone repo
cd ~
git clone https://github.com/Vijay-Ashley/FinanceInvoiceRag.git
cd FinanceInvoiceRag

# 3. Setup Python
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create .env
nano .env
# (Add credentials, save with Ctrl+X, Y, Enter)

# 5. Test manual run
python -m uvicorn app:app --host 0.0.0.0 --port 9000
# (Test in browser, then Ctrl+C to stop)

# 6. Create systemd service
sudo nano /etc/systemd/system/invoice-rag.service
# (Paste service config, replace username, save)

# 7. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable invoice-rag
sudo systemctl start invoice-rag
sudo systemctl status invoice-rag

# 8. Configure firewall
sudo ufw allow 9000/tcp

# 9. Test
curl http://localhost:9000/health
# Open browser: http://your-vm-ip:9000

# ✅ Done!
```

---

## 🎉 **Benefits of Systemd Service**

| Feature | Manual Run | Systemd Service |
|---------|-----------|-----------------|
| **Auto-start on boot** | ❌ No | ✅ Yes |
| **Auto-restart on crash** | ❌ No | ✅ Yes |
| **Easy start/stop** | ❌ Need to find PID | ✅ `systemctl restart` |
| **Centralized logs** | ❌ Manual log files | ✅ `journalctl` |
| **Production ready** | ❌ No | ✅ Yes |

---

**Ready to set up?** Follow the steps above! 🚀

