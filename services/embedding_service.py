"""Azure OpenAI embedding service."""
from typing import List
import openai
from openai import AzureOpenAI
from processors.document_parser import ProcessedChunk
from utils.logger import get_logger
from utils.retry import retry_with_backoff

logger = get_logger(__name__)


class EmbeddingService:
    """Service for generating embeddings using Azure OpenAI."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment_name: str,
        api_version: str = "2024-02-01",
        batch_size: int = 16
    ):
        """
        Initialize embedding service.
        
        Args:
            endpoint: Azure OpenAI endpoint
            api_key: Azure OpenAI API key
            deployment_name: Deployment name for embedding model
            api_version: API version
            batch_size: Number of texts to embed per request
        """
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment_name = deployment_name
        self.batch_size = batch_size
    
    @retry_with_backoff(max_retries=3, exceptions=(Exception,))
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            response = self.client.embeddings.create(
                model=self.deployment_name,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def embed_chunks(self, chunks: List[ProcessedChunk]) -> List[tuple]:
        """
        Generate embeddings for document chunks.
        
        Args:
            chunks: List of ProcessedChunk objects
            
        Returns:
            List of tuples (chunk, embedding_vector)
        """
        results = []
        total_chunks = len(chunks)
        
        # Process in batches
        for i in range(0, total_chunks, self.batch_size):
            batch = chunks[i:i + self.batch_size]
            texts = [chunk.content for chunk in batch]
            
            try:
                embeddings = self.generate_embeddings(texts)
                
                for chunk, embedding in zip(batch, embeddings):
                    results.append((chunk, embedding))
                
                logger.info(
                    f"Embedded batch {i//self.batch_size + 1}/"
                    f"{(total_chunks + self.batch_size - 1)//self.batch_size} "
                    f"({len(batch)} chunks)"
                )
                
            except Exception as e:
                logger.error(f"Failed to embed batch starting at index {i}: {str(e)}")
                # Continue with next batch
                continue
        
        logger.info(f"Successfully embedded {len(results)}/{total_chunks} chunks")
        return results

