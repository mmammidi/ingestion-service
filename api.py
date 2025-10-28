"""Flask API for RAG question answering."""
from flask import Flask, request, jsonify
from flask_cors import CORS
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

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "RAG API",
        "version": "1.0.0"
    })


@app.route("/api/ask", methods=["POST"])
def ask_question():
    """
    Answer a question using RAG.
    
    Request body:
    {
        "question": "What is the question?",
        "system_prompt": "Optional custom system prompt",
        "filters": "Optional OData filter",
        "use_hybrid_search": true,
        "top_k": 5,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    Response:
    {
        "answer": "The generated answer",
        "sources": [...],
        "question": "The original question",
        "retrieved_chunks": 5,
        "search_type": "hybrid",
        "usage": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or "question" not in data:
            return jsonify({
                "error": "Missing required field: question"
            }), 400
        
        question = data["question"]
        system_prompt = data.get("system_prompt")
        filters = data.get("filters")
        use_hybrid_search = data.get("use_hybrid_search", True)
        
        # Override service defaults if provided
        if "top_k" in data:
            rag_service.top_k = data["top_k"]
        if "temperature" in data:
            rag_service.temperature = data["temperature"]
        if "max_tokens" in data:
            rag_service.max_tokens = data["max_tokens"]
        
        logger.info(f"Received question: {question}")
        
        result = rag_service.answer_question(
            question=question,
            system_prompt=system_prompt,
            filters=filters,
            use_hybrid_search=use_hybrid_search
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "message": "Failed to process question"
        }), 500


@app.route("/api/search", methods=["POST"])
def search_chunks():
    """
    Search for relevant chunks without generating an answer.
    
    Request body:
    {
        "question": "What to search for?",
        "top_k": 5,
        "filters": "Optional OData filter"
    }
    
    Response:
    {
        "question": "The original question",
        "chunks": [...],
        "count": 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or "question" not in data:
            return jsonify({
                "error": "Missing required field: question"
            }), 400
        
        question = data["question"]
        top_k = data.get("top_k")
        filters = data.get("filters")
        
        logger.info(f"Received search query: {question}")
        
        result = rag_service.get_relevant_chunks(
            question=question,
            top_k=top_k,
            filters=filters
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error searching chunks: {str(e)}", exc_info=True)
        return jsonify({
            "error": str(e),
            "message": "Failed to search chunks"
        }), 500


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get current RAG configuration."""
    return jsonify({
        "top_k": settings.RAG_TOP_K,
        "temperature": settings.RAG_TEMPERATURE,
        "max_tokens": settings.RAG_MAX_TOKENS,
        "chat_model": settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
        "embedding_model": settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        "search_index": settings.AZURE_SEARCH_INDEX_NAME
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": "Please check the API documentation"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == "__main__":
    # Validate configuration
    try:
        settings.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    
    # Run the Flask app
    logger.info("Starting Flask API server...")
    logger.info("API Documentation:")
    logger.info("  POST /api/ask - Answer questions using RAG")
    logger.info("  POST /api/search - Search for relevant chunks")
    logger.info("  GET /api/config - Get current configuration")
    logger.info("  GET /health - Health check")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

