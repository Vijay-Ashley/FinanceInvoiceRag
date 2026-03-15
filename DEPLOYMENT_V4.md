# 🚀 Deployment Guide - Version 4.0

## 📋 Pre-Deployment Checklist

- [ ] All files copied to `finalinvoicerag_v4`
- [ ] `.env` file present with all keys
- [ ] Code tested locally
- [ ] GitHub repository ready
- [ ] VM access confirmed

---

## 🎯 Deployment Steps

### **Step 1: Prepare GitHub Repository**

#### **Option A: New Repository (Recommended)**

```bash
cd finalinvoicerag_v4

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "v4.0: Invoice Intelligence with improved extraction"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/rag-invoice-v4.git

# Push
git branch -M main
git push -u origin main
```

#### **Option B: Update Existing Repository**

```bash
cd finalinvoicerag_v4

# If already a git repo
git add .
git commit -m "v4.0: Improved invoice extraction - multi-pattern regex, bug fixes"
git push origin main
```

---

### **Step 2: Deploy to VM**

#### **2.1 Connect to VM**

```bash
ssh azureuser@YOUR_VM_IP
```

#### **2.2 Pull Latest Code**

```bash
# Navigate to app directory
cd /home/azureuser/rag_pdf_finance

# Pull latest code
git pull origin main

# Or clone if first time
# git clone https://github.com/YOUR_USERNAME/rag-invoice-v4.git
# cd rag-invoice-v4
```

#### **2.3 Update Environment**

```bash
# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies (if any new ones)
pip install -r requirements.txt
```

#### **2.4 Verify Configuration**

```bash
# Check .env file exists
ls -la .env

# Verify containers exist
python check_containers.py
```

---

### **Step 3: Restart Service**

#### **If using systemd:**

```bash
# Restart the service
sudo systemctl restart rag-api

# Check status
sudo systemctl status rag-api

# View logs
sudo journalctl -u rag-api -f
```

#### **If running manually:**

```bash
# Stop old process (Ctrl+C or kill)
pkill -f "uvicorn app:app"

# Start new process
nohup python -m uvicorn app:app --host 0.0.0.0 --port 9000 > app.log 2>&1 &

# Check logs
tail -f app.log
```

---

### **Step 4: Verify Deployment**

#### **4.1 Check Server is Running**

```bash
curl http://localhost:9000/health
```

**Expected:**
```json
{"status": "healthy"}
```

#### **4.2 Check Invoice Intelligence**

```bash
curl http://localhost:9000/api/invoices
```

**Expected:**
```json
{"count": 0, "invoices": []}
```
(Or existing invoices if you have data)

#### **4.3 Upload Test Invoice**

From your local machine:
```bash
curl -X POST http://YOUR_VM_IP:9000/api/upload \
  -F "files=@test_invoice.pdf"
```

#### **4.4 Check Extraction Logs**

On VM:
```bash
# View recent logs
sudo journalctl -u rag-api -n 100

# Or if running manually
tail -f app.log
```

**Look for:**
```
✅ Invoice extracted: 5440612345, Vendor: Google LLC, Total: $195652.18
✅ Saved 8 invoice chunks to invoice_chunks container
```

---

## 🔍 Troubleshooting

### **Issue: Service won't start**

```bash
# Check for errors
sudo journalctl -u rag-api -n 50

# Check if port is in use
sudo lsof -i :9000

# Kill old process
sudo pkill -f "uvicorn app:app"

# Restart
sudo systemctl restart rag-api
```

### **Issue: Import errors**

```bash
# Reinstall dependencies
source .venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

### **Issue: Cosmos DB connection fails**

```bash
# Verify .env file
cat .env | grep COSMOS

# Test connection
python check_containers.py
```

### **Issue: Extraction not working**

```bash
# Check logs for extraction errors
sudo journalctl -u rag-api | grep "Invoice extracted"

# Verify invoice_extractor.py was updated
grep "INVOICE_NUMBER_PATTERNS" invoice_extractor.py
```

---

## 📊 Post-Deployment Verification

### **Checklist:**

- [ ] Server responds to health check
- [ ] Can upload PDF files
- [ ] Invoice extraction logs show correct values
- [ ] `/api/invoices` returns data
- [ ] `invoice_chunks` container has data
- [ ] `/api/analytics` works
- [ ] UI loads correctly
- [ ] Chat functionality works

---

## 🔄 Rollback Plan

If v4.0 has issues, rollback to v3:

```bash
# On VM
cd /home/azureuser/rag_pdf_finance

# Checkout previous version
git checkout v3.0  # or specific commit hash

# Restart service
sudo systemctl restart rag-api
```

---

## 📝 Deployment Log Template

```
Deployment Date: _______________
Deployed By: _______________
Version: 4.0
Commit Hash: _______________

Pre-Deployment:
[ ] Code tested locally
[ ] .env file verified
[ ] GitHub updated

Deployment:
[ ] Code pulled on VM
[ ] Dependencies updated
[ ] Service restarted
[ ] Health check passed

Post-Deployment:
[ ] Invoice upload tested
[ ] Extraction verified
[ ] API endpoints tested
[ ] Logs reviewed

Issues Encountered:
_______________________________
_______________________________

Resolution:
_______________________________
_______________________________

Sign-off: _______________
```

---

## 🎯 Quick Commands Reference

```bash
# Connect to VM
ssh azureuser@YOUR_VM_IP

# Pull code
cd /home/azureuser/rag_pdf_finance && git pull

# Restart service
sudo systemctl restart rag-api

# Check status
sudo systemctl status rag-api

# View logs
sudo journalctl -u rag-api -f

# Test endpoint
curl http://localhost:9000/api/invoices
```

---

## 📞 Support

If you encounter issues:
1. Check logs: `sudo journalctl -u rag-api -n 100`
2. Verify .env: `cat .env | grep -v KEY`
3. Test containers: `python check_containers.py`
4. Review VERSION.md for known issues

---

## ✅ Success Criteria

Deployment is successful when:
- ✅ Server starts without errors
- ✅ Invoice extraction shows improved accuracy
- ✅ All API endpoints respond correctly
- ✅ Logs show "Invoice Intelligence enabled"
- ✅ Chunks are saved to `invoice_chunks` container

