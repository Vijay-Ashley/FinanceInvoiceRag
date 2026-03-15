# 🚀 VM Run Options - Which One to Choose?

## 📋 **Three Ways to Run on VM**

| Method | Difficulty | Best For | Auto-Restart | Survives Reboot |
|--------|-----------|----------|--------------|-----------------|
| **1. Simple Run** | ⭐ Easy | Testing | ❌ No | ❌ No |
| **2. Background (nohup)** | ⭐⭐ Medium | Quick deploy | ❌ No | ❌ No |
| **3. Systemd Service** | ⭐⭐⭐ Advanced | Production | ✅ Yes | ✅ Yes |

---

## 🎯 **Recommendation**

- **Testing/Development:** Use **Method 1** (Simple Run)
- **Production:** Use **Method 3** (Systemd Service)

---

## 1️⃣ **Method 1: Simple Run (Start Here)**

### **Setup (One Time)**

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
# (Add credentials, save with Ctrl+X, Y, Enter)
```

### **Run**

```bash
cd ~/FinanceInvoiceRag
source .venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

### **Update**

```bash
# Stop: Press Ctrl+C
# Pull changes
git pull origin main
# Run again
python -m uvicorn app:app --host 0.0.0.0 --port 9000
```

### **Pros & Cons**

✅ **Pros:**
- Very simple
- See logs directly
- Easy to debug

❌ **Cons:**
- Stops when you close terminal
- No auto-restart
- Manual start after reboot

---

## 2️⃣ **Method 2: Background Run (nohup)**

### **Run**

```bash
cd ~/FinanceInvoiceRag
source .venv/bin/activate
nohup python -m uvicorn app:app --host 0.0.0.0 --port 9000 > app.log 2>&1 &
```

### **Check Status**

```bash
# See if running
ps aux | grep uvicorn

# View logs
tail -f app.log
```

### **Stop**

```bash
# Find process ID
ps aux | grep uvicorn

# Kill it
kill -9 <PID>
```

### **Update**

```bash
# 1. Stop
ps aux | grep uvicorn
kill -9 <PID>

# 2. Pull changes
cd ~/FinanceInvoiceRag
git pull origin main

# 3. Restart
source .venv/bin/activate
nohup python -m uvicorn app:app --host 0.0.0.0 --port 9000 > app.log 2>&1 &
```

### **Pros & Cons**

✅ **Pros:**
- Runs in background
- Survives terminal close
- Simple logs

❌ **Cons:**
- No auto-restart on crash
- Stops on VM reboot
- Manual process management

---

## 3️⃣ **Method 3: Systemd Service (Production)**

### **Setup (One Time)**

See complete guide: **`VM_SYSTEMD_SETUP.md`**

**Quick version:**

```bash
# 1. Clone and setup (same as Method 1)
git clone https://github.com/Vijay-Ashley/FinanceInvoiceRag.git
cd FinanceInvoiceRag
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
nano .env  # Add credentials

# 2. Create systemd service
sudo nano /etc/systemd/system/invoice-rag.service
```

**Add this (replace `your-username`):**
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

```bash
# 3. Enable and start
sudo systemctl daemon-reload
sudo systemctl enable invoice-rag
sudo systemctl start invoice-rag
sudo systemctl status invoice-rag
```

### **Run**

```bash
sudo systemctl start invoice-rag
```

### **Stop**

```bash
sudo systemctl stop invoice-rag
```

### **Restart**

```bash
sudo systemctl restart invoice-rag
```

### **Check Status**

```bash
sudo systemctl status invoice-rag
```

### **View Logs**

```bash
sudo journalctl -u invoice-rag -f
```

### **Update**

```bash
cd ~/FinanceInvoiceRag
git pull origin main
sudo systemctl restart invoice-rag
```

### **Pros & Cons**

✅ **Pros:**
- Auto-starts on VM boot
- Auto-restarts on crash
- Centralized logging
- Production-ready
- Easy management

❌ **Cons:**
- More complex setup
- Requires sudo access
- Need to learn systemctl commands

---

## 🎯 **Which One Should You Use?**

### **Use Method 1 (Simple Run) if:**
- You're just testing
- You want to see logs directly
- You're actively developing
- You don't need it to run 24/7

### **Use Method 2 (nohup) if:**
- You need it to run in background
- You don't have sudo access
- You want quick deployment
- You're okay with manual restarts

### **Use Method 3 (Systemd) if:**
- You're deploying to production
- You need 24/7 uptime
- You want auto-restart on crash
- You want auto-start on reboot
- You have sudo access

---

## 📊 **Quick Comparison**

| Feature | Simple Run | nohup | Systemd |
|---------|-----------|-------|---------|
| **Setup Time** | 5 min | 5 min | 15 min |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Background** | ❌ | ✅ | ✅ |
| **Auto-restart** | ❌ | ❌ | ✅ |
| **Survives reboot** | ❌ | ❌ | ✅ |
| **Easy logs** | ✅ | ✅ | ✅ |
| **Production ready** | ❌ | ⚠️ | ✅ |

---

## 🚀 **Recommended Path**

### **For You (First Time):**

1. **Start with Method 1** (Simple Run)
   - Test that everything works
   - Make sure app runs correctly
   - Verify in browser

2. **Then upgrade to Method 3** (Systemd)
   - Once you confirm it works
   - Follow `VM_SYSTEMD_SETUP.md`
   - Get production-ready setup

---

## 📝 **Example: Your Journey**

### **Day 1: Testing**
```bash
# Use Method 1
cd ~/FinanceInvoiceRag
source .venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 9000
# Test in browser, make sure it works
```

### **Day 2: Production Setup**
```bash
# Upgrade to Method 3
sudo nano /etc/systemd/system/invoice-rag.service
# (Create service file)
sudo systemctl enable invoice-rag
sudo systemctl start invoice-rag
# Now it runs 24/7!
```

### **Day 3+: Updates**
```bash
# Easy updates with systemd
cd ~/FinanceInvoiceRag
git pull origin main
sudo systemctl restart invoice-rag
# Done!
```

---

## ✅ **Next Steps**

1. **Choose your method** based on your needs
2. **Follow the setup** for that method
3. **Test** that it works
4. **Update** when needed

---

**Need detailed systemd setup?** See: **`VM_SYSTEMD_SETUP.md`**

**Ready to deploy?** Start with **Method 1** to test! 🚀

