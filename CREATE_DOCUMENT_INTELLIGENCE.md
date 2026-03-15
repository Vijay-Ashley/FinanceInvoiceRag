# 📄 Create Azure Document Intelligence Resource

## Method 1: Azure Portal (Recommended - 2 minutes)

### **Step 1: Open Azure Portal**
1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"Create a resource"**
3. Search for **"Document Intelligence"** or **"Form Recognizer"**
4. Click **"Create"**

### **Step 2: Configure Resource**

Fill in the form:

| Field | Value |
|-------|-------|
| **Subscription** | Your subscription (same as Cosmos DB) |
| **Resource Group** | `afi-mfg-pic-rg-dev` (same as Cosmos DB) |
| **Region** | `East US` (same as Cosmos DB) |
| **Name** | `afi-mfg-pic-doc-intel-dev` |
| **Pricing Tier** | **Free (F0)** - 500 pages/month FREE! |

### **Step 3: Review + Create**
1. Click **"Review + create"**
2. Click **"Create"**
3. Wait 1-2 minutes for deployment

### **Step 4: Get Keys**
1. Go to your new resource
2. Click **"Keys and Endpoint"** (left menu)
3. Copy:
   - **KEY 1** (or KEY 2)
   - **Endpoint** (looks like: `https://afi-mfg-pic-doc-intel-dev.cognitiveservices.azure.com/`)

### **Step 5: Add to .env File**

Add these lines to your `.env` file:

```env
# Azure Document Intelligence (Form Recognizer)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://afi-mfg-pic-doc-intel-dev.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_key_here
```

---

## Method 2: Azure CLI (Advanced - 30 seconds)

If you have Azure CLI installed:

```bash
# Login
az login

# Create Document Intelligence resource
az cognitiveservices account create \
  --name afi-mfg-pic-doc-intel-dev \
  --resource-group afi-mfg-pic-rg-dev \
  --kind FormRecognizer \
  --sku F0 \
  --location eastus \
  --yes

# Get endpoint
az cognitiveservices account show \
  --name afi-mfg-pic-doc-intel-dev \
  --resource-group afi-mfg-pic-rg-dev \
  --query "properties.endpoint" -o tsv

# Get key
az cognitiveservices account keys list \
  --name afi-mfg-pic-doc-intel-dev \
  --resource-group afi-mfg-pic-rg-dev \
  --query "key1" -o tsv
```

---

## 💰 **Pricing (FREE Tier Available!)**

### **Free Tier (F0):**
- ✅ **500 pages/month FREE**
- ✅ Perfect for testing
- ✅ No credit card required (if you have Azure subscription)

### **Standard Tier (S0):**
- **Prebuilt Invoice Model:** $0.01 per page
- **Custom Models:** $0.05 per page (training)
- Only needed if you exceed 500 pages/month

**For your use case:** Start with **FREE tier** (F0)!

---

## 🎯 **What Document Intelligence Does**

### **Prebuilt Invoice Model** (What we'll use)

Automatically extracts:
- ✅ Invoice number
- ✅ Invoice date
- ✅ Due date
- ✅ Vendor name & address
- ✅ Customer name & address
- ✅ PO number
- ✅ Subtotal, tax, total
- ✅ Line items (description, quantity, price, amount)
- ✅ **Confidence scores** for each field

### **Accuracy:**
- 🎯 **95%+ accuracy** on standard invoices
- 🎯 Works with **any invoice format** (Google, AWS, Microsoft, etc.)
- 🎯 Handles **multi-page invoices**
- 🎯 Extracts **tables** automatically

---

## 📊 **Comparison**

| Method | Accuracy | Works on All Invoices? | Cost |
|--------|----------|----------------------|------|
| **Regex** | 40-60% | ❌ No (vendor-specific) | Free |
| **LLM (GPT-4)** | 80-90% | ✅ Yes | $0.03/page |
| **Document Intelligence** | 95%+ | ✅ Yes | **FREE** (500/month) |

**Winner:** Document Intelligence! 🏆

---

## ✅ **Next Steps**

1. **Create the resource** (2 minutes)
2. **Copy endpoint + key** to `.env`
3. **I'll update the code** to use it
4. **Test with your Google invoice**

---

## 🔗 **Useful Links**

- [Document Intelligence Portal](https://portal.azure.com/#create/Microsoft.CognitiveServicesFormRecognizer)
- [Pricing Details](https://azure.microsoft.com/en-us/pricing/details/form-recognizer/)
- [Invoice Model Documentation](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept-invoice)

---

## ❓ **Need Help?**

If you get stuck, share a screenshot and I'll guide you through it!

**Ready to create the resource?** It takes 2 minutes! 🚀

