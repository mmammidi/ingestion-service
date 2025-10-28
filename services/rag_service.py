"""RAG (Retrieval Augmented Generation) service."""
from typing import Dict, Any, Optional
from services.embedding_service import EmbeddingService
from services.query_service import QueryService
from services.chat_service import ChatService
from utils.logger import get_logger

logger = get_logger(__name__)


class RAGService:
    """Service that orchestrates retrieval and generation for question answering."""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        query_service: QueryService,
        chat_service: ChatService,
        top_k: int = 5,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Initialize RAG service.
        
        Args:
            embedding_service: Service for generating embeddings
            query_service: Service for querying Azure Search
            chat_service: Service for generating answers
            top_k: Number of chunks to retrieve
            temperature: Sampling temperature for generation
            max_tokens: Maximum tokens in response
        """
        self.embedding_service = embedding_service
        self.query_service = query_service
        self.chat_service = chat_service
        self.top_k = top_k
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def answer_question(
        self,
        question: str,
        system_prompt: Optional[str] = None,
        filters: Optional[str] = None,
        use_hybrid_search: bool = True
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG pipeline.
        
        Args:
            question: The user's question
            system_prompt: Optional custom system prompt
            filters: Optional OData filter for search
            use_hybrid_search: Whether to use hybrid search (text + vector)
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            logger.info(f"Processing question: {question}")
            
            # Step 1: Generate query embedding
            logger.info("Generating query embedding...")
            query_embeddings = self.embedding_service.generate_embeddings([question])
            query_vector = query_embeddings[0]
            
            # Step 2: Retrieve relevant chunks
            logger.info(f"Retrieving top {self.top_k} relevant chunks...")
            if use_hybrid_search:
                chunks = self.query_service.hybrid_search(
                    query_text=question,
                    query_vector=query_vector,
                    top_k=self.top_k,
                    filters=filters
                )
            else:
                chunks = self.query_service.vector_search(
                    query_vector=query_vector,
                    top_k=self.top_k,
                    filters=filters
                )
            
            if not chunks:
                logger.warning("No relevant chunks found")
                return {
                    "answer": "I couldn't find any relevant information in the knowledge base to answer your question.",
                    "sources": [],
                    "retrieved_chunks": 0,
                    "question": question
                }
            
            # Step 3: Generate answer using retrieved context
            logger.info(f"Generating answer from {len(chunks)} chunks...")
            result = self.chat_service.generate_answer(
                question=question,
                context_chunks=chunks,
                system_prompt=system_prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Add metadata
            result.update({
                "question": question,
                "retrieved_chunks": len(chunks),
                "search_type": "hybrid" if use_hybrid_search else "vector"
            })
            
            logger.info("Successfully generated answer")
            return result
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}")
            raise
    
    def get_relevant_chunks(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get relevant chunks without generating an answer.
        
        Args:
            question: The user's question
            top_k: Number of chunks to retrieve (overrides default)
            filters: Optional OData filter for search
            
        Returns:
            Dictionary with retrieved chunks
        """
        try:
            logger.info(f"Retrieving chunks for: {question}")
            
            # Generate query embedding
            query_embeddings = self.embedding_service.generate_embeddings([question])
            query_vector = query_embeddings[0]
            
            # Retrieve chunks
            k = top_k if top_k is not None else self.top_k
            chunks = self.query_service.vector_search(
                query_vector=query_vector,
                top_k=k,
                filters=filters
            )
            
            return {
                "question": question,
                "chunks": chunks,
                "count": len(chunks)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            raise

