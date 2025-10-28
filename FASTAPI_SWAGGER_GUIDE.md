# FastAPI with Swagger UI - Quick Start Guide

## 🚀 Your RAG API with Interactive Documentation!

The FastAPI version includes **automatic Swagger UI** - a beautiful, interactive API documentation where you can test all endpoints directly from your browser!

---

## 📍 Access Points

Once the server is running:

| What | URL | Description |
|------|-----|-------------|
| **Swagger UI** | http://localhost:8000/docs | 🎯 **Interactive API testing** |
| **ReDoc** | http://localhost:8000/redoc | 📚 Alternative documentation |
| **Root** | http://localhost:8000/ | API info |
| **Health** | http://localhost:8000/health | Health check |

---

## 🎯 Using Swagger UI

### **1. Open Swagger UI**

Navigate to: **http://localhost:8000/docs**

You'll see a beautiful interface with all your API endpoints!

### **2. Try the "Ask Question" Endpoint**

#### **Step 1: Expand the endpoint**
Click on **`POST /api/ask`** - it will expand showing details

#### **Step 2: Click "Try it out"**
A button in the top right of the endpoint

#### **Step 3: Fill in the request**
You'll see a JSON editor with the request body:

```json
{
  "question": "What is Solara?",
  "use_hybrid_search": true,
  "top_k": 5,
  "temperature": 0.7
}
```

#### **Step 4: Click "Execute"**
The API will process your request!

#### **Step 5: See the Response**
Scroll down to see:
- **Response body** - The complete answer with sources
- **Response code** - 200 (success)
- **Response headers** - HTTP headers

---

## 📋 Available Endpoints

### **1. POST /api/ask** - Ask a Question
**What it does:** Answer questions using RAG

**Try this:**
```json
{
  "question": "What is Solara?",
  "use_hybrid_search": true,
  "top_k": 5,
  "temperature": 0.7
}
```

**You get back:**
- Comprehensive answer
- Source citations with URLs
- Token usage
- Metadata

---

### **2. POST /api/search** - Search Chunks
**What it does:** Search for relevant chunks (no answer generation)

**Try this:**
```json
{
  "question": "Solara transformation",
  "top_k": 3
}
```

**You get back:**
- Raw chunks with content
- Relevance scores
- Document metadata

---

### **3. GET /api/config** - Get Configuration
**What it does:** Shows current RAG configuration

Just click **"Try it out"** → **"Execute"**

**You get back:**
- Models being used
- Default parameters
- Index name

---

### **4. GET /health** - Health Check
**What it does:** Verifies API is running

Just click **"Try it out"** → **"Execute"**

**You get back:**
- Status: healthy
- Service name
- Version

---

## 🔧 Advanced Features in Swagger

### **Customizing Requests**

You can modify any parameter in the JSON editor:

#### **Custom System Prompt:**
```json
{
  "question": "Explain Solara's transformation",
  "system_prompt": "You are a historian. Provide detailed analysis.",
  "top_k": 5
}
```

#### **Filter by Division/Space:**
```json
{
  "question": "What projects exist?",
  "filters": "space_key eq 'ENGINEERING'",
  "top_k": 3
}
```

#### **Adjust Creativity:**
```json
{
  "question": "Tell me a story about innovation",
  "temperature": 0.9,
  "max_tokens": 500
}
```

---

## 📊 Understanding Responses

### **Success Response (200)**

```json
{
  "answer": "Solara is a small country...",
  "question": "What is Solara?",
  "retrieved_chunks": 5,
  "search_type": "hybrid",
  "model": "gpt-4o-mini",
  "usage": {
    "prompt_tokens": 3969,
    "completion_tokens": 354,
    "total_tokens": 4323
  },
  "sources": [
    {
      "title": "The Rise of Solara",
      "url": "https://...",
      "author": "Madhava Mammidi",
      "source": "confluence"
    }
  ]
}
```

### **Error Response (500)**

```json
{
  "detail": "Failed to process question: Connection timeout"
}
```

---

## 🎨 Swagger UI Features

### **1. Schema Definitions**
Click the **▼** next to any request/response to see the data structure

### **2. Example Values**
Pre-filled with realistic examples

### **3. Copy cURL**
Click the **Copy** icon to get cURL command for terminal

### **4. Models Section**
Scroll to bottom to see all data models (Pydantic schemas)

### **5. Color Coding**
- 🟢 **GET** - Retrieve data
- 🟠 **POST** - Send data
- 🔵 **PUT** - Update data
- 🔴 **DELETE** - Delete data

---

## 💡 Testing Scenarios

### **Scenario 1: Basic Question**
```json
{
  "question": "What is Solara?"
}
```

### **Scenario 2: Division-Specific**
```json
{
  "question": "Engineering projects?",
  "filters": "space_key eq 'ENGINEERING'"
}
```

### **Scenario 3: More Factual**
```json
{
  "question": "Give me precise statistics",
  "temperature": 0.2
}
```

### **Scenario 4: More Creative**
```json
{
  "question": "Tell a story about innovation",
  "temperature": 0.9
}
```

### **Scenario 5: Retrieve More Context**
```json
{
  "question": "Complex topic needing context",
  "top_k": 10
}
```

---

## 🔐 Security Filters (Multi-Division)

### **Single Division:**
```json
{
  "question": "HR policies?",
  "filters": "space_key eq 'HR'"
}
```

### **Multiple Divisions:**
```json
{
  "question": "Cross-team projects?",
  "filters": "space_key eq 'ENG' or space_key eq 'SALES'"
}
```

### **Complex Filters:**
```json
{
  "question": "Recent updates?",
  "filters": "space_key eq 'ENG' and modified_date ge '2025-10-01'"
}
```

---

## 🐍 Code Generation

Swagger UI can generate code for you!

1. Execute a request
2. Scroll down to **Request** section
3. Copy the **cURL** command
4. Or use tools to convert to Python/JavaScript

**Example cURL:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/ask' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "What is Solara?",
  "top_k": 5
}'
```

---

## 📱 Mobile/Remote Access

If you want to access from another device:

1. **Find your IP:**
   ```powershell
   ipconfig
   ```

2. **Access from other device:**
   ```
   http://YOUR_IP:8000/docs
   ```

3. **Make sure firewall allows port 8000**

---

## 🚀 Production Deployment

### **Option 1: Docker**
```dockerfile
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "api_fastapi.py"]
```

### **Option 2: Azure App Service**
Deploy directly to Azure with Swagger included!

### **Option 3: Kubernetes**
Scale horizontally with multiple replicas

---

## 🎯 Quick Comparison

| Feature | FastAPI + Swagger | Flask API |
|---------|-------------------|-----------|
| **Interactive Docs** | ✅ Built-in | ❌ Manual |
| **Data Validation** | ✅ Automatic | ⚠️ Manual |
| **Type Hints** | ✅ Full support | ⚠️ Limited |
| **Performance** | ✅ Async capable | ⚠️ Sync only |
| **Testing UI** | ✅ Swagger UI | ❌ Need tools |
| **OpenAPI Spec** | ✅ Auto-generated | ⚠️ Manual |

---

## 🔍 Troubleshooting

### **Can't access Swagger UI?**
- Verify server is running: `http://localhost:8000/health`
- Check console for errors
- Try different port if 8000 is busy

### **Endpoints failing?**
- Check `.env` file has all required values
- Verify Azure OpenAI deployments exist
- Check network connectivity

### **Slow responses?**
- Reduce `top_k` to retrieve fewer chunks
- Lower `max_tokens` for shorter responses
- Check Azure service quotas

---

## 📚 Next Steps

1. ✅ **Explore all endpoints** in Swagger
2. ✅ **Try different questions** and parameters
3. ✅ **Test security filters** if using multi-division
4. ✅ **Generate API keys** for authentication (if needed)
5. ✅ **Deploy to production** when ready

---

## 🎉 Benefits of FastAPI + Swagger

- **No Postman needed** - Test directly in browser
- **Live documentation** - Always up to date
- **Type safety** - Catch errors early
- **Easy integration** - Share with frontend team
- **Professional look** - Impress stakeholders
- **OpenAPI standard** - Works with all tools

---

## 🌐 Sharing with Your Team

Just send them the link:
```
http://YOUR_SERVER:8000/docs
```

They can immediately:
- See all available endpoints
- Test the API
- Understand request/response formats
- Generate code examples

---

**Your RAG API is now fully interactive! 🎯**

Start exploring at: **http://localhost:8000/docs**

