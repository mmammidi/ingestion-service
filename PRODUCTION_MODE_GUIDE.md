# 🔒 Production Mode Security Guide

## Overview

Your RAG API now supports **production mode** which disables Swagger UI, ReDoc, and OpenAPI documentation to prevent unauthorized access in production environments.

---

## 🎯 How It Works

The API checks the `ENVIRONMENT` environment variable:

- **`ENVIRONMENT=production`** → Swagger UI **DISABLED** ✅ Secure
- **`ENVIRONMENT=development`** (or not set) → Swagger UI **ENABLED** 📖 Development

---

## 🚀 Deployment Configurations

### **Local Development (Swagger ENABLED)**

No configuration needed! By default, Swagger is enabled.

```bash
# Just run the app
python api_fastapi.py
```

**Access:**
- ✅ Swagger UI: http://localhost:8000/docs
- ✅ ReDoc: http://localhost:8000/redoc
- ✅ OpenAPI JSON: http://localhost:8000/openapi.json

---

### **Render Production (Swagger DISABLED)**

Already configured in `render.yaml`:

```yaml
envVars:
  - key: ENVIRONMENT
    value: production
```

When deployed to Render:
- ❌ `/docs` returns 404
- ❌ `/redoc` returns 404
- ❌ `/openapi.json` returns 404
- ✅ API endpoints still work: `/api/ask`, `/api/search`, `/health`

**Logs will show:**
```
Environment: PRODUCTION
⚠️  API documentation (Swagger UI) is DISABLED in production mode
ℹ️  To enable docs, set ENVIRONMENT=development
```

---

## 🔧 Manual Configuration

### **Enable Production Mode Locally (for testing)**

**Windows:**
```bash
set ENVIRONMENT=production
python api_fastapi.py
```

**Linux/Mac:**
```bash
export ENVIRONMENT=production
python api_fastapi.py
```

**PowerShell:**
```powershell
$env:ENVIRONMENT="production"
python api_fastapi.py
```

### **Force Development Mode on Render (not recommended)**

If you need to enable docs on Render temporarily:

1. Go to Render Dashboard → Your Service → Environment
2. Change `ENVIRONMENT` from `production` to `development`
3. Service will redeploy
4. **⚠️ WARNING:** This exposes your API documentation publicly!

---

## 📊 Behavior Comparison

| Feature | Development Mode | Production Mode |
|---------|-----------------|-----------------|
| **Swagger UI** (`/docs`) | ✅ Available | ❌ 404 Not Found |
| **ReDoc** (`/redoc`) | ✅ Available | ❌ 404 Not Found |
| **OpenAPI JSON** (`/openapi.json`) | ✅ Available | ❌ 404 Not Found |
| **API Endpoints** (`/api/*`) | ✅ Working | ✅ Working |
| **Health Check** (`/health`) | ✅ Working | ✅ Working |
| **Root** (`/`) | ✅ Shows docs links | ✅ Hides docs links |

---

## 🔍 Verify Current Mode

### **Check via Root Endpoint**

**Development Mode Response:**
```json
{
  "message": "RAG Question Answering API",
  "version": "1.0.0",
  "environment": "development",
  "endpoints": {
    "health": "/health",
    "config": "/api/config",
    "search": "/api/search (POST)",
    "ask": "/api/ask (POST)"
  },
  "documentation": {
    "swagger": "/docs",
    "redoc": "/redoc",
    "openapi": "/openapi.json"
  }
}
```

**Production Mode Response:**
```json
{
  "message": "RAG Question Answering API",
  "version": "1.0.0",
  "environment": "production",
  "endpoints": {
    "health": "/health",
    "config": "/api/config",
    "search": "/api/search (POST)",
    "ask": "/api/ask (POST)"
  }
}
```

Notice: No `documentation` field in production!

### **Check via Logs**

**Development Mode:**
```
INFO - Starting FastAPI server...
INFO - Environment: DEVELOPMENT
INFO - 📖 Swagger UI available at: http://localhost:8000/docs
INFO - 📖 ReDoc available at: http://localhost:8000/redoc
```

**Production Mode:**
```
INFO - Starting FastAPI server...
INFO - Environment: PRODUCTION
INFO - ⚠️  API documentation (Swagger UI) is DISABLED in production mode
INFO - ℹ️  To enable docs, set ENVIRONMENT=development
```

---

## 🔐 Security Benefits

### **Why Disable Swagger in Production?**

1. **Prevents Information Disclosure**
   - Attackers can't see all endpoints
   - Model schemas remain hidden
   - Example payloads not exposed

2. **Reduces Attack Surface**
   - No interactive "Try it out" buttons
   - Can't test endpoints from browser
   - Harder to discover API structure

3. **Professional Appearance**
   - Production APIs typically don't expose docs
   - Shows security-conscious development
   - Follows industry best practices

4. **Bandwidth Savings**
   - Swagger UI assets not loaded
   - Faster initial page load
   - Reduced server load

---

## 📖 API Documentation Alternatives

### **For Internal Teams:**

1. **Share Postman Collection**
   - Use `RAG_API_Postman_Collection.json`
   - See `POSTMAN_GUIDE.md`

2. **Share Documentation Files**
   - `RAG_API_DOCUMENTATION.md`
   - `FASTAPI_SWAGGER_GUIDE.md`

3. **Run Local Dev Instance**
   - Clone repo
   - Run with `ENVIRONMENT=development`
   - Access Swagger locally

### **For External Partners:**

1. **Generate Static Docs**
   ```bash
   # Export OpenAPI spec
   curl http://localhost:8000/openapi.json > openapi.json
   
   # Use tools like ReDoc or Swagger UI standalone
   ```

2. **Create Custom Documentation**
   - Host your own docs site
   - Use tools like Slate, Docusaurus
   - Keep control over what's exposed

---

## 🛠️ Testing Production Mode Locally

### **Test Swagger is Disabled:**

1. **Start in production mode:**
   ```bash
   set ENVIRONMENT=production
   python api_fastapi.py
   ```

2. **Try accessing docs:**
   ```bash
   curl http://localhost:8000/docs
   # Should return: 404 Not Found
   ```

3. **Verify API still works:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy",...}
   
   curl -X POST http://localhost:8000/api/search \
     -H "Content-Type: application/json" \
     -d '{"question":"test"}'
   # Should return search results
   ```

---

## 🔄 Switching Modes

### **Development → Production:**
1. Set `ENVIRONMENT=production`
2. Restart application
3. Swagger disabled

### **Production → Development:**
1. Set `ENVIRONMENT=development` (or unset it)
2. Restart application
3. Swagger enabled

**Note:** On Render, changes to environment variables trigger automatic redeployment.

---

## ⚠️ Important Notes

### **Production Mode Does NOT:**
- ❌ Add authentication (you still need to implement auth separately)
- ❌ Rate limit requests (consider adding rate limiting middleware)
- ❌ Encrypt data in transit (use HTTPS/TLS)
- ❌ Validate API keys (implement if needed)

### **Production Mode DOES:**
- ✅ Disable interactive documentation
- ✅ Hide OpenAPI schema
- ✅ Reduce information disclosure
- ✅ Follow security best practices

---

## 📚 Related Files

- **`api_fastapi.py`** - Main API file with production mode logic
- **`render.yaml`** - Render deployment config with ENVIRONMENT=production
- **`RAG_API_POSTMAN_Collection.json`** - Alternative API documentation
- **`POSTMAN_GUIDE.md`** - How to use Postman collection
- **`RENDER_DEPLOYMENT_GUIDE.md`** - Full deployment guide

---

## ✅ Quick Reference

| Task | Command/Action |
|------|----------------|
| **Check current mode** | Access `GET /` and check `environment` field |
| **Enable production mode** | Set `ENVIRONMENT=production` |
| **Enable development mode** | Set `ENVIRONMENT=development` or unset |
| **Verify Swagger disabled** | Try accessing `/docs` (should 404) |
| **Verify API working** | Access `/health` (should work) |

---

## 🆘 Troubleshooting

### **Problem: Swagger still showing in production**

**Check:**
1. Verify `ENVIRONMENT` variable is actually set to `production`
2. Restart the application after setting variable
3. Check logs for "Environment: PRODUCTION" message

**Fix:**
```bash
# Windows
echo %ENVIRONMENT%

# Linux/Mac
echo $ENVIRONMENT

# Should output: production
```

### **Problem: Can't access Swagger locally**

**Check:**
1. Verify you're NOT in production mode
2. `ENVIRONMENT` should be `development` or unset

**Fix:**
```bash
# Windows
set ENVIRONMENT=development

# Linux/Mac
export ENVIRONMENT=development

# PowerShell
$env:ENVIRONMENT="development"
```

---

**Your API is now secure by default in production! 🎉**

Swagger UI will only be available in development environments where you explicitly enable it.

