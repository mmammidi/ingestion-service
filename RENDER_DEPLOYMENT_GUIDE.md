
# Render Cloud Deployment Guide

## 🚀 Deploy RAG API to Render

This guide will help you deploy your FastAPI RAG application to Render cloud.

---

## ✅ Changes Made to Fix Build Errors

### **1. Updated Pydantic Versions**
```python
# Changed from:
pydantic==2.6.1
pydantic-core==2.16.2  # ❌ Requires Rust compilation

# To:
pydantic>=2.9.0  # ✅ Has pre-built wheels for Python 3.13
pydantic-settings>=2.5.0
```

**Why**: The old version tried to compile from source on Render's read-only filesystem.

### **2. Added `runtime.txt`**
```
python-3.12.0
```

Specifies Python 3.12 (stable) instead of letting Render use 3.13 (which has limited package support).

### **3. Updated `api_fastapi.py`**
Added dynamic port binding for Render:
```python
port = int(os.getenv("PORT", 8000))
```

Render assigns a PORT environment variable automatically.

### **4. Created `render.yaml`**
Configuration file for one-click deployment.

---

## 📋 Pre-Deployment Checklist

- ✅ All changes committed to Git
- ✅ Repository pushed to GitHub/GitLab
- ✅ Have all Azure credentials ready
- ✅ Confluence credentials ready

---

## 🎯 Deployment Steps

### **Option 1: Using render.yaml (Recommended)**

1. **Push to Git**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/
   - Click **"New +"** → **"Blueprint"**

3. **Connect Repository**
   - Select your Git repository
   - Render will detect `render.yaml`

4. **Set Environment Variables**
   Go to **Environment** tab and add:

   **Confluence:**
   ```
   CONFLUENCE_URL=https://your-org.atlassian.net/wiki
   CONFLUENCE_USERNAME=your-email@example.com
   CONFLUENCE_API_TOKEN=your-token
   CONFLUENCE_SPACES=SPACE1,SPACE2
   ```

   **Azure OpenAI (Embedding):**
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-key
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
   AZURE_OPENAI_API_VERSION=2024-02-01
   ```

   **Azure OpenAI (Chat):**
   ```
   AZURE_OPENAI_CHAT_ENDPOINT=https://your-chat-resource.openai.azure.com/
   AZURE_OPENAI_CHAT_API_KEY=your-chat-key
   AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
   ```

   **Azure Search:**
   ```
   AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
   AZURE_SEARCH_API_KEY=your-search-key
   AZURE_SEARCH_INDEX_NAME=data-ingestion
   ```

5. **Deploy**
   - Click **"Apply"**
   - Wait for build to complete (~5-10 minutes)

6. **Access Your API**
   - Render provides URL: `https://your-app.onrender.com`
   - Swagger UI: `https://your-app.onrender.com/docs`

---

### **Option 2: Manual Setup**

1. **Create New Web Service**
   - Dashboard → **"New +"** → **"Web Service"**

2. **Connect Repository**
   - Select your repository

3. **Configure Build**
   ```
   Name: rag-api
   Region: Oregon (US West)
   Branch: main
   Runtime: Python 3
   Build Command: pip install --upgrade pip && pip install -r requirements.txt
   Start Command: python api_fastapi.py
   ```

4. **Select Plan**
   - **Free** tier for testing
   - **Starter** ($7/month) for production

5. **Add Environment Variables** (same as above)

6. **Create Web Service**

---

## 🔧 Troubleshooting

### **Build Fails with "Read-only file system"**

✅ **Fixed!** Updated pydantic to version with pre-built wheels.

If still fails:
- Check `runtime.txt` exists with `python-3.12.0`
- Verify `requirements.txt` has `pydantic>=2.9.0`

---

### **"Port already in use"**

✅ **Fixed!** Updated `api_fastapi.py` to use `PORT` env variable.

Render automatically sets PORT - don't override it in environment variables.

---

### **Configuration Validation Error**

**Problem**: Missing required environment variables

**Solution**: Add all required variables in Render dashboard:
- Go to your service → **Environment**
- Add each variable from the list above
- Click **"Save Changes"**
- Redeploy

---

### **"Module not found" Error**

**Problem**: Dependencies not installed

**Solution**:
1. Verify `requirements.txt` is in repository root
2. Check build command: `pip install -r requirements.txt`
3. Check build logs for specific missing package

---

### **API Returns 500 Error**

**Problem**: Runtime error in application

**Solution**:
1. Check logs: Dashboard → Your Service → **Logs**
2. Common issues:
   - Azure OpenAI deployment not found
   - Invalid API keys
   - Network connectivity to Azure
3. Test endpoints one by one using `/health` first

---

## 📊 Monitoring

### **View Logs**
- Dashboard → Your Service → **Logs**
- Real-time streaming logs
- Filter by severity

### **Metrics**
- Dashboard → Your Service → **Metrics**
- CPU usage
- Memory usage
- Request rate

### **Set Up Alerts**
- Dashboard → Your Service → **Settings**
- Configure email/Slack notifications
- Alert on failures or high resource usage

---

## 💰 Cost Optimization

### **Free Tier Limitations**
- Spins down after 15 minutes of inactivity
- 750 hours/month free
- Slower cold starts (~30 seconds)

### **For Production**
- Upgrade to **Starter** ($7/month)
- No sleep/spin-down
- Faster response times
- More resources

### **Cost-Saving Tips**
1. **Cache frequent queries** in your app
2. **Use RAG filters** to reduce Azure Search costs
3. **Monitor token usage** in Azure OpenAI
4. **Set up rate limiting** to prevent abuse

---

## 🔐 Security Best Practices

### **1. Use Environment Variables**
✅ Never commit secrets to Git
✅ Use Render's environment variables
✅ Rotate keys regularly

### **2. Enable HTTPS**
✅ Render provides free SSL/TLS
✅ All traffic is encrypted

### **3. Add Authentication**
Consider adding:
- API keys
- JWT tokens
- OAuth2

Example:
```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
```

### **4. Rate Limiting**
Add rate limiting to prevent abuse:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/ask")
@limiter.limit("10/minute")
async def ask_question(...):
    ...
```

---

## 🚦 CI/CD Setup

### **Auto-Deploy on Git Push**

1. **Enable Auto-Deploy**
   - Dashboard → Your Service → **Settings**
   - "Auto-Deploy" → **Yes**

2. **Now**: Every push to `main` triggers deployment

### **Branch Previews**
- Create Pull Request → Render creates preview deployment
- Test before merging to main

---

## 📈 Scaling

### **Vertical Scaling** (Bigger machine)
- Dashboard → Your Service → **Settings**
- Change instance type
- More CPU/RAM

### **Horizontal Scaling** (Multiple instances)
- Available on paid plans
- Automatic load balancing
- Better reliability

---

## 🧪 Testing Deployed API

### **Using cURL**
```bash
curl -X POST https://your-app.onrender.com/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Solara?"
  }'
```

### **Using Python**
```python
import requests

response = requests.post(
    "https://your-app.onrender.com/api/ask",
    json={"question": "What is Solara?"}
)

print(response.json()["answer"])
```

### **Using Swagger UI**
```
https://your-app.onrender.com/docs
```

---

## 🎯 Post-Deployment Checklist

- [ ] API accessible at provided URL
- [ ] Swagger UI works: `/docs`
- [ ] Health check passes: `/health`
- [ ] Can ask questions: `/api/ask`
- [ ] Search works: `/api/search`
- [ ] Environment variables set correctly
- [ ] Logs show no errors
- [ ] Test with actual Confluence data

---

## 📚 Additional Resources

- **Render Docs**: https://render.com/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Troubleshooting**: https://render.com/docs/troubleshooting-deploys

---

## 🆘 Getting Help

If deployment fails:

1. **Check build logs** in Render dashboard
2. **Review this guide** for common issues
3. **Test locally first**: `python api_fastapi.py`
4. **Verify all env variables** are set
5. **Check Azure services** are accessible

---

## ✅ Success!

Once deployed, share your API:
```
Swagger UI: https://your-app.onrender.com/docs
API Endpoint: https://your-app.onrender.com/api/ask
Health Check: https://your-app.onrender.com/health
```

Your RAG API is now live and ready to answer questions! 🎉

