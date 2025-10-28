"""FastAPI API for RAG question answering with Swagger UI."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sys

from config.settings import settings
from services.embedding_service import EmbeddingService
from services.query_service import QueryService
from services.chat_service import ChatService
from services.rag_service import RAGService
from utils.logger import setup_logger, get_logger

# Set up logging
setup_logger(__name__, settings.LOG_LEVEL)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Question Answering API",
    description="""
    🚀 **Retrieval Augmented Generation (RAG) API**
    
    This API enables intelligent question answering using your Confluence knowledge base.
    
    ## Features
    
    * 🔍 **Semantic Search**: Vector-based similarity search
    * 🤖 **AI-Powered Answers**: GPT-4o-mini generates comprehensive responses
    * 📚 **Source Citations**: Every answer includes source documents
    * 🔐 **Security Filters**: Filter by division/space for multi-tenant security
    * ⚡ **Fast**: Sub-second response times
    
    ## How It Works
    
    1. Your question is converted to a vector embedding
    2. Relevant chunks are retrieved from Azure Search
    3. GPT-4o-mini generates an answer using the retrieved context
    4. Response includes answer, sources, and metadata
    
    ## Try It Out
    
    Click on any endpoint below, then click **"Try it out"** to test the API!
    """,
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # Alternative documentation
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
logger.info("Initializing RAG services...")

embedding_service = EmbeddingService(
    endpoint=settings.AZURE_OPENAI_ENDPOINT,
    api_key=settings.AZURE_OPENAI_API_KEY,
    deployment_name=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    api_version=settings.AZURE_OPENAI_API_VERSION
)

query_service = QueryService(
    endpoint=settings.AZURE_SEARCH_ENDPOINT,
    api_key=settings.AZURE_SEARCH_API_KEY,
    index_name=settings.AZURE_SEARCH_INDEX_NAME
)

chat_service = ChatService(
    endpoint=settings.AZURE_OPENAI_CHAT_ENDPOINT,
    api_key=settings.AZURE_OPENAI_CHAT_API_KEY,
    deployment_name=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
    api_version=settings.AZURE_OPENAI_API_VERSION
)

rag_service = RAGService(
    embedding_service=embedding_service,
    query_service=query_service,
    chat_service=chat_service,
    top_k=settings.RAG_TOP_K,
    temperature=settings.RAG_TEMPERATURE,
    max_tokens=settings.RAG_MAX_TOKENS
)

logger.info("RAG services initialized successfully")


# Pydantic models for request/response
class AskQuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str = Field(
        ...,
        description="The question to answer",
        example="What is Solara?"
    )
    system_prompt: Optional[str] = Field(
        None,
        description="Optional custom system prompt to guide AI behavior",
        example="You are a technical documentation expert."
    )
    filters: Optional[str] = Field(
        None,
        description="OData filter for Azure Search (e.g., 'space_key eq \"ENGINEERING\"')",
        example="space_key eq 'ENGINEERING'"
    )
    use_hybrid_search: bool = Field(
        True,
        description="Use both text and vector search (recommended)"
    )
    top_k: Optional[int] = Field(
        None,
        description="Number of chunks to retrieve (default: 5)",
        ge=1,
        le=20,
        example=5
    )
    temperature: Optional[float] = Field(
        None,
        description="Response creativity (0=factual, 1=creative)",
        ge=0.0,
        le=1.0,
        example=0.7
    )
    max_tokens: Optional[int] = Field(
        None,
        description="Maximum response length in tokens",
        ge=100,
        le=4000,
        example=1000
    )

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Solara?",
                "use_hybrid_search": True,
                "top_k": 5,
                "temperature": 0.7
            }
        }


class Source(BaseModel):
    """Source document information."""
    title: str = Field(..., description="Document title")
    url: str = Field(..., description="Document URL")
    author: str = Field(..., description="Document author")
    source: str = Field(..., description="Source system (e.g., 'confluence')")


class TokenUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: int = Field(..., description="Tokens in the prompt")
    completion_tokens: int = Field(..., description="Tokens in the completion")
    total_tokens: int = Field(..., description="Total tokens used")


class AskQuestionResponse(BaseModel):
    """Response model for question answering."""
    answer: str = Field(..., description="The generated answer")
    question: str = Field(..., description="The original question")
    retrieved_chunks: int = Field(..., description="Number of chunks retrieved")
    search_type: str = Field(..., description="Type of search used")
    model: str = Field(..., description="AI model used")
    usage: TokenUsage = Field(..., description="Token usage statistics")
    sources: List[Source] = Field(..., description="Source documents used")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Solara is a small country that transformed from poverty to prosperity...",
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
                        "url": "https://confluence.../pages/327870",
                        "author": "Madhava Mammidi",
                        "source": "confluence"
                    }
                ]
            }
        }


class SearchChunksRequest(BaseModel):
    """Request model for searching chunks."""
    question: str = Field(
        ...,
        description="The search query",
        example="Solara transformation"
    )
    top_k: Optional[int] = Field(
        None,
        description="Number of chunks to retrieve",
        ge=1,
        le=20,
        example=5
    )
    filters: Optional[str] = Field(
        None,
        description="OData filter for Azure Search",
        example="space_key eq 'ENGINEERING'"
    )


class Chunk(BaseModel):
    """Retrieved chunk information."""
    id: str
    content: str
    title: str
    url: str
    author: str
    source: str
    space_key: str
    created_date: str
    modified_date: str
    tags: List[str]
    chunk_index: int
    total_chunks: int
    score: float


class SearchChunksResponse(BaseModel):
    """Response model for chunk search."""
    question: str = Field(..., description="The search query")
    count: int = Field(..., description="Number of chunks found")
    chunks: List[Chunk] = Field(..., description="Retrieved chunks")


class ConfigResponse(BaseModel):
    """Configuration information."""
    top_k: int
    temperature: float
    max_tokens: int
    chat_model: str
    embedding_model: str
    search_index: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str


# API Endpoints

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health Check",
    description="Check if the API is running and healthy"
)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    
    Returns basic service information.
    """
    return {
        "status": "healthy",
        "service": "RAG API",
        "version": "1.0.0"
    }


@app.post(
    "/api/ask",
    response_model=AskQuestionResponse,
    tags=["Question Answering"],
    summary="Ask a Question",
    description="""
    Ask a question and get an AI-generated answer with source citations.
    
    This endpoint:
    1. Converts your question to a vector embedding
    2. Searches for relevant content in Azure Search
    3. Uses GPT-4o-mini to generate a comprehensive answer
    4. Returns the answer with sources and metadata
    
    **Example Questions:**
    - "What is Solara?"
    - "Tell me about the transformation story"
    - "Who is President Amira N'Dala?"
    """
)
async def ask_question(request: AskQuestionRequest):
    """
    Answer a question using RAG (Retrieval Augmented Generation).
    
    The system retrieves relevant chunks from the knowledge base and uses
    them as context to generate an accurate, sourced answer.
    """
    try:
        # Override service defaults if provided
        if request.top_k is not None:
            rag_service.top_k = request.top_k
        if request.temperature is not None:
            rag_service.temperature = request.temperature
        if request.max_tokens is not None:
            rag_service.max_tokens = request.max_tokens
        
        logger.info(f"Received question: {request.question}")
        
        result = rag_service.answer_question(
            question=request.question,
            system_prompt=request.system_prompt,
            filters=request.filters,
            use_hybrid_search=request.use_hybrid_search
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@app.post(
    "/api/search",
    response_model=SearchChunksResponse,
    tags=["Search"],
    summary="Search Chunks",
    description="""
    Search for relevant document chunks without generating an answer.
    
    This is useful for:
    - Exploring available content
    - Building custom UIs
    - Testing search relevance
    """
)
async def search_chunks(request: SearchChunksRequest):
    """
    Search for relevant chunks without generating an answer.
    
    Returns the raw chunks with their content and metadata.
    """
    try:
        logger.info(f"Received search query: {request.question}")
        
        result = rag_service.get_relevant_chunks(
            question=request.question,
            top_k=request.top_k,
            filters=request.filters
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error searching chunks: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search chunks: {str(e)}"
        )


@app.get(
    "/api/config",
    response_model=ConfigResponse,
    tags=["System"],
    summary="Get Configuration",
    description="Get current RAG system configuration"
)
async def get_config():
    """
    Get current RAG configuration settings.
    
    Shows the models being used and default parameters.
    """
    return {
        "top_k": settings.RAG_TOP_K,
        "temperature": settings.RAG_TEMPERATURE,
        "max_tokens": settings.RAG_MAX_TOKENS,
        "chat_model": settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        "embedding_model": settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        "search_index": settings.AZURE_SEARCH_INDEX_NAME
    }


@app.get(
    "/",
    tags=["System"],
    summary="Root Endpoint",
    description="Redirects to API documentation"
)
async def root():
    """
    Root endpoint - redirects to Swagger documentation.
    """
    return {
        "message": "RAG Question Answering API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Validate configuration
    try:
        settings.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    
    # Get port from environment (for cloud platforms like Render)
    port = int(os.getenv("PORT", 8000))
    
    # Run the FastAPI app
    logger.info("Starting FastAPI server...")
    logger.info(f"Swagger UI available at: http://localhost:{port}/docs")
    logger.info(f"ReDoc available at: http://localhost:{port}/redoc")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

