"""Azure Search query service for RAG."""
from typing import List, Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from utils.logger import get_logger

logger = get_logger(__name__)


class QueryService:
    """Service for querying Azure Cognitive Search with vector search."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        index_name: str
    ):
        """
        Initialize query service.
        
        Args:
            endpoint: Azure Search endpoint
            api_key: Azure Search API key
            index_name: Name of the search index
        """
        credential = AzureKeyCredential(api_key)
        self.search_client = SearchClient(endpoint, index_name, credential)
        self.index_name = index_name
    
    def vector_search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: str = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.
        
        Args:
            query_vector: The query embedding vector
            top_k: Number of results to return
            filters: Optional OData filter expression
            
        Returns:
            List of search results with content and metadata
        """
        try:
            # Create vector query
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top_k,
                fields="content_vector"
            )
            
            # Perform search
            results = self.search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                filter=filters,
                select=[
                    "id",
                    "content",
                    "title",
                    "url",
                    "author",
                    "source",
                    "space_key",
                    "created_date",
                    "modified_date",
                    "tags",
                    "chunk_index",
                    "total_chunks"
                ],
                top=top_k
            )
            
            # Extract and format results
            search_results = []
            for result in results:
                search_results.append({
                    "id": result["id"],
                    "content": result["content"],
                    "title": result["title"],
                    "url": result["url"],
                    "author": result["author"],
                    "source": result["source"],
                    "space_key": result.get("space_key", ""),
                    "created_date": result["created_date"],
                    "modified_date": result["modified_date"],
                    "tags": result.get("tags", []),
                    "chunk_index": result["chunk_index"],
                    "total_chunks": result["total_chunks"],
                    "score": result.get("@search.score", 0.0)
                })
            
            logger.info(f"Found {len(search_results)} results for vector search")
            return search_results
            
        except Exception as e:
            logger.error(f"Error performing vector search: {str(e)}")
            raise
    
    def hybrid_search(
        self,
        query_text: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: str = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search (text + vector).
        
        Args:
            query_text: The text query
            query_vector: The query embedding vector
            top_k: Number of results to return
            filters: Optional OData filter expression
            
        Returns:
            List of search results with content and metadata
        """
        try:
            # Create vector query
            vector_query = VectorizedQuery(
                vector=query_vector,
                k_nearest_neighbors=top_k,
                fields="content_vector"
            )
            
            # Perform hybrid search
            results = self.search_client.search(
                search_text=query_text,
                vector_queries=[vector_query],
                filter=filters,
                select=[
                    "id",
                    "content",
                    "title",
                    "url",
                    "author",
                    "source",
                    "space_key",
                    "created_date",
                    "modified_date",
                    "tags",
                    "chunk_index",
                    "total_chunks"
                ],
                top=top_k
            )
            
            # Extract and format results
            search_results = []
            for result in results:
                search_results.append({
                    "id": result["id"],
                    "content": result["content"],
                    "title": result["title"],
                    "url": result["url"],
                    "author": result["author"],
                    "source": result["source"],
                    "space_key": result.get("space_key", ""),
                    "created_date": result["created_date"],
                    "modified_date": result["modified_date"],
                    "tags": result.get("tags", []),
                    "chunk_index": result["chunk_index"],
                    "total_chunks": result["total_chunks"],
                    "score": result.get("@search.score", 0.0)
                })
            
            logger.info(f"Found {len(search_results)} results for hybrid search")
            return search_results
            
        except Exception as e:
            logger.error(f"Error performing hybrid search: {str(e)}")
            raise

