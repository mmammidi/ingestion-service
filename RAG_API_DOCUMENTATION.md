# RAG API Documentation

## Overview

This API provides a Retrieval Augmented Generation (RAG) endpoint that answers questions using your Confluence knowledge base indexed in Azure Search.

## Architecture

```
User Question → Embedding → Vector Search → Context Retrieval → LLM → Answer
```

1. **Question Embedding**: Converts user question to vector using Azure OpenAI embeddings
2. **Search**: Retrieves relevant document chunks from Azure Search (vector or hybrid search)
3. **Generation**: Uses Azure OpenAI chat model to generate answer based on retrieved context
4. **Response**: Returns answer with sources and metadata

## Setup

### 1. Add Configuration to .env

```bash
# Azure OpenAI Chat Model (required for RAG)
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o

# RAG Settings (optional - defaults shown)
RAG_TOP_K=5                # Number of chunks to retrieve
RAG_TEMPERATURE=0.7        # Response creativity (0-1)
RAG_MAX_TOKENS=1000        # Maximum response length
```

**Important**: Replace `gpt-4o` with your actual Azure OpenAI chat deployment name. Check Azure OpenAI Studio → Deployments to find the correct name.

### 2. Install Dependencies

```bash
pip install flask==3.0.2 flask-cors==4.0.0
```

### 3. Start the API Server

```bash
python api.py
```

The API will start on `http://localhost:5000`

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "RAG API",
  "version": "1.0.0"
}
```

---

### 2. Ask Question (RAG)

**POST** `/api/ask`

Answer a question using RAG (retrieval + generation).

**Request Body:**
```json
{
  "question": "What is Solara?",
  "system_prompt": "Optional custom system prompt",
  "filters": "source eq 'confluence'",
  "use_hybrid_search": true,
  "top_k": 5,
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Parameters:**
- `question` (required): The user's question
- `system_prompt` (optional): Custom system prompt to guide the AI
- `filters` (optional): OData filter for Azure Search (e.g., `"source eq 'confluence'"`)
- `use_hybrid_search` (optional, default: true): Use both text and vector search
- `top_k` (optional): Number of chunks to retrieve
- `temperature` (optional): Response creativity (0-1)
- `max_tokens` (optional): Maximum response length

**Response:**
```json
{
  "answer": "Solara is a small, sun-scorched country in the southern corner...",
  "question": "What is Solara?",
  "retrieved_chunks": 5,
  "search_type": "hybrid",
  "model": "gpt-4o",
  "usage": {
    "prompt_tokens": 1234,
    "completion_tokens": 256,
    "total_tokens": 1490
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

**Example with cURL:**
```bash
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Solara?",
    "use_hybrid_search": true
  }'
```

**Example with Python:**
```python
import requests

response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "What is Solara?",
        "use_hybrid_search": True
    }
)

result = response.json()
print(result["answer"])
print("Sources:", [s["title"] for s in result["sources"]])
```

---

### 3. Search Chunks (No Answer Generation)

**POST** `/api/search`

Search for relevant chunks without generating an answer.

**Request Body:**
```json
{
  "question": "What is Solara?",
  "top_k": 5,
  "filters": "source eq 'confluence'"
}
```

**Parameters:**
- `question` (required): The search query
- `top_k` (optional): Number of chunks to retrieve
- `filters` (optional): OData filter for Azure Search

**Response:**
```json
{
  "question": "What is Solara?",
  "count": 5,
  "chunks": [
    {
      "id": "confluence_327870_chunk_0",
      "content": "In the southern corner of the world...",
      "title": "The Rise of Solara",
      "url": "https://...",
      "author": "Madhava Mammidi",
      "source": "confluence",
      "created_date": "2025-10-27T18:07:19.873Z",
      "modified_date": "2025-10-27T18:13:04.721Z",
      "tags": [],
      "chunk_index": 0,
      "total_chunks": 2,
      "score": 0.85
    }
  ]
}
```

---

### 4. Get Configuration

**GET** `/api/config`

Get current RAG configuration.

**Response:**
```json
{
  "top_k": 5,
  "temperature": 0.7,
  "max_tokens": 1000,
  "chat_model": "gpt-35-turbo",
  "embedding_model": "text-embedding-3-small",
  "search_index": "data-ingestion"
}
```

---

## Testing

### 1. Test RAG Pipeline

Run the test script:

```bash
python test_rag.py
```

This will:
- Initialize all services
- Test sample questions
- Display answers with sources
- Show token usage and metadata

### 2. Test API Endpoints

Start the API server:
```bash
python api.py
```

In another terminal, test with cURL:
```bash
# Health check
curl http://localhost:5000/health

# Ask a question
curl -X POST http://localhost:5000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What documents are in the knowledge base?"}'

# Search for chunks
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"question": "Solara", "top_k": 3}'

# Get configuration
curl http://localhost:5000/api/config
```

---

## Advanced Usage

### Custom System Prompts

You can customize the AI's behavior with system prompts:

```python
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "Summarize the key points",
        "system_prompt": "You are a technical documentation expert. Provide concise, bullet-point summaries."
    }
)
```

### Filtering Results

Use OData filters to search specific sources or dates:

```python
# Search only Confluence
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "What projects exist?",
        "filters": "source eq 'confluence'"
    }
)

# Search by author
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "Documents by Madhava",
        "filters": "author eq 'Madhava Mammidi'"
    }
)
```

### Adjusting Response Style

Control creativity and length:

```python
# More factual, precise (lower temperature)
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "What is the exact definition?",
        "temperature": 0.2
    }
)

# More creative, conversational (higher temperature)
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "Tell me a story about...",
        "temperature": 0.9
    }
)

# Longer response
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "Explain in detail...",
        "max_tokens": 2000
    }
)
```

---

## Error Handling

### Common Errors

**400 Bad Request**
```json
{
  "error": "Missing required field: question"
}
```
Solution: Ensure `question` field is included in request body.

**500 Internal Server Error**
```json
{
  "error": "Error message",
  "message": "Failed to process question"
}
```
Possible causes:
- Azure OpenAI deployment not found
- Azure Search index doesn't exist
- Network connectivity issues
- Invalid configuration

Check logs for detailed error information.

---

## Deployment

### Production Considerations

1. **Use a production WSGI server** (not Flask's development server):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 api:app
   ```

2. **Add authentication** to protect your API

3. **Implement rate limiting** to prevent abuse

4. **Use environment variables** for all secrets

5. **Monitor costs** - Each request uses Azure OpenAI tokens

6. **Cache frequent queries** to reduce costs

---

## Architecture Components

### Services

1. **EmbeddingService** (`services/embedding_service.py`)
   - Converts text to vectors using Azure OpenAI embeddings

2. **QueryService** (`services/query_service.py`)
   - Performs vector and hybrid search on Azure Search

3. **ChatService** (`services/chat_service.py`)
   - Generates answers using Azure OpenAI chat completions

4. **RAGService** (`services/rag_service.py`)
   - Orchestrates the complete RAG pipeline

### Configuration

Settings are loaded from `.env` file via `config/settings.py`.

Required environment variables:
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`
- `AZURE_OPENAI_CHAT_DEPLOYMENT` (new)
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_API_KEY`
- `AZURE_SEARCH_INDEX_NAME`

---

## Troubleshooting

### "Deployment not found" error

**Problem**: Azure OpenAI chat deployment doesn't exist.

**Solution**: 
1. Go to Azure OpenAI Studio → Deployments
2. Create a deployment for a chat model (GPT-4, GPT-3.5, etc.)
3. Update `AZURE_OPENAI_CHAT_DEPLOYMENT` in `.env` with the exact deployment name

### No results returned

**Problem**: Search returns no relevant chunks.

**Solution**:
1. Verify index has documents: `python test_confluence_connection.py`
2. Check if sync completed: `python main.py sync`
3. Try adjusting `top_k` parameter

### Answers are not relevant

**Problem**: AI generates answers not based on context.

**Solution**:
1. Lower the temperature (e.g., 0.2-0.4) for more factual responses
2. Increase `top_k` to retrieve more context
3. Use hybrid search instead of vector-only search
4. Customize the system prompt to be more specific

---

## Next Steps

1. **Add authentication**: Implement API keys or OAuth
2. **Add conversation history**: Support multi-turn conversations
3. **Add caching**: Cache frequent queries to reduce costs
4. **Add analytics**: Track usage, popular questions, costs
5. **Add feedback loop**: Let users rate answers to improve quality

---

## Support

For issues or questions:
1. Check logs in the console output
2. Verify all environment variables are set correctly
3. Ensure Azure services are accessible
4. Check Azure OpenAI and Search service status in Azure Portal

