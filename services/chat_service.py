"""Azure OpenAI chat service for generating answers."""
from typing import List, Dict, Any
from openai import AzureOpenAI
from utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """Service for generating chat completions using Azure OpenAI."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment_name: str,
        api_version: str = "2024-02-01"
    ):
        """
        Initialize chat service.
        
        Args:
            endpoint: Azure OpenAI endpoint (can be different from embedding endpoint)
            api_key: Azure OpenAI API key (can be different from embedding key)
            deployment_name: Deployment name for chat model
            api_version: API version
        """
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment_name = deployment_name
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Generate an answer using retrieved context.
        
        Args:
            question: The user's question
            context_chunks: List of retrieved document chunks
            system_prompt: Optional custom system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Build context from chunks
            context = self._build_context(context_chunks)
            
            # Use default system prompt if none provided
            if not system_prompt:
                system_prompt = self._get_default_system_prompt()
            
            # Build user prompt
            user_prompt = self._build_user_prompt(question, context)
            
            # Generate completion
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            answer = response.choices[0].message.content
            
            result = {
                "answer": answer,
                "model": self.deployment_name,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "sources": self._extract_sources(context_chunks)
            }
            
            logger.info(f"Generated answer using {result['usage']['total_tokens']} tokens")
            return result
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build formatted context from retrieved chunks."""
        if not chunks:
            return "No relevant information found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source {i}] {chunk['title']}\n"
                f"Author: {chunk['author']}\n"
                f"Content: {chunk['content']}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def _build_user_prompt(self, question: str, context: str) -> str:
        """Build the user prompt with question and context."""
        return f"""Context information:
{context}

Question: {question}

Please provide a comprehensive answer based on the context provided above. If the context doesn't contain enough information to answer the question, please state that clearly."""
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for RAG."""
        return """You are a helpful AI assistant that answers questions based on the provided context from a knowledge base.

Instructions:
- Answer the question using ONLY the information provided in the context
- Be specific and cite which source(s) you used when possible
- If the context doesn't contain enough information, clearly state that
- Be concise but thorough in your explanations
- Use a professional and friendly tone
- If you find conflicting information in the sources, acknowledge it"""
    
    def _extract_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract source citations from chunks."""
        sources = []
        seen_urls = set()
        
        for chunk in chunks:
            url = chunk.get("url", "")
            if url and url not in seen_urls:
                sources.append({
                    "title": chunk.get("title", "Unknown"),
                    "url": url,
                    "author": chunk.get("author", "Unknown"),
                    "source": chunk.get("source", "Unknown")
                })
                seen_urls.add(url)
        
        return sources

