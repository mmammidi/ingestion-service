# 📬 Postman Collection Guide

## 🎯 **Quick Start**

### **Step 1: Import the Collection**

1. Open **Postman**
2. Click **"Import"** button (top left)
3. Click **"Upload Files"**
4. Select `RAG_API_Postman_Collection.json`
5. Click **"Import"**

✅ You now have **10 ready-to-use requests** organized in 3 folders!

---

## 📂 **Collection Structure**

### **📁 System (3 requests)**
- ✅ **Health Check** - Verify API is running
- ✅ **Get Configuration** - See current settings
- ✅ **Root Endpoint** - API info

### **📁 Search (3 requests)**
- 🔍 **Search Chunks - Basic** - Simple search
- 🔍 **Search Chunks - With Filters** - Filtered by space
- 🔍 **Search Chunks - Find Person** - Person lookup

### **📁 Question Answering (4 requests)**
- 💬 **Ask Question - Simple** - Basic Q&A
- 💬 **Ask Question - About Person** - Person-specific
- 💬 **Ask Question - Advanced Settings** - Custom params
- 💬 **Ask Question - With Filters** - Space-filtered Q&A
- 💬 **Ask Question - Creative Response** - High temperature
- 💬 **Ask Question - Concise Response** - Low temperature

---

## 🚀 **How to Use**

### **Step 1: Start Your Local Server**

Open terminal and run:
```bash
cd "C:\Development\ingestion service"
python api_fastapi.py
```

Wait for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **Step 2: Test Health Check**

1. In Postman, expand **"System"** folder
2. Click **"Health Check"**
3. Click **"Send"**

✅ Expected response:
```json
{
  "status": "healthy",
  "service": "RAG API",
  "version": "1.0.0"
}
```

### **Step 3: Try Search**

1. Expand **"Search"** folder
2. Click **"Search Chunks - Basic"**
3. Click **"Send"**

✅ Expected response:
```json
{
  "chunks": [
    {
      "id": "chunk-123",
      "content": "...",
      "title": "The Rise of Solara",
      "score": 0.85
    }
  ],
  "question": "What is Solara?",
  "total_results": 5
}
```

### **Step 4: Try Question Answering**

1. Expand **"Question Answering"** folder
2. Click **"Ask Question - Simple"**
3. Click **"Send"**

✅ Expected response:
```json
{
  "answer": "Solara is a small country...",
  "question": "What is Solara?",
  "retrieved_chunks": 5,
  "model": "gpt-4o-mini",
  "sources": [...]
}
```

---

## 🔧 **Customizing Requests**

### **Change the Question:**

1. Click on any request
2. Go to **"Body"** tab
3. Edit the JSON:
```json
{
  "question": "Your custom question here?"
}
```
4. Click **"Send"**

### **Adjust Search Parameters:**

```json
{
  "question": "What is Solara?",
  "top_k": 10,           // Get more results
  "filters": "space_key eq 'ENGINEERING'"  // Filter by space
}
```

### **Control AI Response:**

```json
{
  "question": "What is Solara?",
  "temperature": 0.3,     // Lower = more focused (0.0-1.0)
  "max_tokens": 500,      // Shorter response
  "system_prompt": "Be concise."
}
```

---

## 🌐 **Switch to Render (Production)**

### **Option 1: Edit Collection Variable**

1. Click on collection name **"RAG Question Answering API - Local"**
2. Click **"Variables"** tab
3. Change `baseUrl`:
   - **Current:** `http://localhost:8000`
   - **New:** `https://your-app.onrender.com`
4. Click **"Save"**

✅ All requests now use Render!

### **Option 2: Environment Variables**

1. Click **"Environments"** (left sidebar)
2. Click **"+"** to create new environment
3. Name it: **"Local"**
4. Add variable:
   - Variable: `baseUrl`
   - Initial Value: `http://localhost:8000`
   - Current Value: `http://localhost:8000`
5. Create another environment: **"Render"**
6. Add variable:
   - Variable: `baseUrl`
   - Initial Value: `https://your-app.onrender.com`
   - Current Value: `https://your-app.onrender.com`
7. Select environment from top-right dropdown

---

## 📝 **Common Request Examples**

### **Search for a Person:**
```json
{
  "question": "Tell me about Ravi Kumar",
  "top_k": 5
}
```

### **Search with Space Filter:**
```json
{
  "question": "transformation story",
  "top_k": 10,
  "filters": "space_key eq 'ENGINEERING'"
}
```

### **Ask Question - Very Precise:**
```json
{
  "question": "What is Solara?",
  "temperature": 0.2,
  "max_tokens": 300,
  "system_prompt": "Provide factual, precise answers only."
}
```

### **Ask Question - Creative:**
```json
{
  "question": "What is Solara?",
  "temperature": 0.9,
  "max_tokens": 1000,
  "system_prompt": "Be creative and engaging while staying factual."
}
```

---

## 🎨 **Filter Syntax (OData)**

### **Filter by Space:**
```
space_key eq 'ENGINEERING'
```

### **Filter by Multiple Spaces:**
```
space_key eq 'ENGINEERING' or space_key eq 'MARKETING'
```

### **Filter by Author:**
```
author eq 'Madhava Mammidi'
```

### **Combine Filters:**
```
space_key eq 'ENGINEERING' and author eq 'Madhava Mammidi'
```

---

## 🔍 **Viewing Responses**

### **Pretty JSON View:**
After sending a request, Postman shows the response at the bottom.

- Click **"Pretty"** for formatted JSON
- Click **"Raw"** for unformatted
- Click **"Preview"** for rendered HTML

### **Response Details:**
- **Status:** Should be `200 OK`
- **Time:** Response time in milliseconds
- **Size:** Response body size

---

## 🛠️ **Troubleshooting**

### **Error: Connection Refused**
```
Error: connect ECONNREFUSED 127.0.0.1:8000
```
**Fix:** Make sure your local server is running:
```bash
python api_fastapi.py
```

### **Error: 500 Internal Server Error**
Check the server logs in your terminal for detailed error messages.

### **Error: 401 Unauthorized (Render)**
Your Azure Search credentials aren't set in Render environment variables.

**Fix:** Add these in Render dashboard:
```
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-key
AZURE_SEARCH_INDEX_NAME=data-ingestion
```

### **Error: 422 Unprocessable Entity**
Your request body is invalid.

**Fix:** Make sure JSON is valid and includes required fields:
```json
{
  "question": "Required field!"
}
```

---

## 📊 **Request Parameters Reference**

### **Search Endpoint (`/api/search`)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | string | ✅ Yes | Search query |
| `top_k` | integer | ❌ No | Number of results (1-20) |
| `filters` | string | ❌ No | OData filter expression |

### **Ask Endpoint (`/api/ask`)**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | string | ✅ Yes | Your question |
| `system_prompt` | string | ❌ No | Custom system prompt |
| `use_hybrid_search` | boolean | ❌ No | Use hybrid search (default: true) |
| `top_k` | integer | ❌ No | Chunks to retrieve (1-20) |
| `temperature` | float | ❌ No | Creativity (0.0-1.0) |
| `max_tokens` | integer | ❌ No | Max response length |
| `filters` | string | ❌ No | OData filter |

---

## 🎯 **Pro Tips**

1. **Save Responses:** Click "Save Response" to create example responses
2. **Tests Tab:** Add assertions to validate responses
3. **Pre-request Scripts:** Auto-generate timestamps or random data
4. **Console:** View detailed request/response logs (bottom left)
5. **Collections Runner:** Run all requests sequentially

---

## 📚 **Next Steps**

1. ✅ Import collection
2. ✅ Test Health Check
3. ✅ Try Search endpoint
4. ✅ Try Ask endpoint
5. ✅ Customize questions
6. ✅ Experiment with parameters
7. ✅ Switch to Render when ready

---

## 🆘 **Need Help?**

- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc (ReDoc)
- **Check Config:** Use "Get Configuration" request

---

**Happy Testing! 🚀**

