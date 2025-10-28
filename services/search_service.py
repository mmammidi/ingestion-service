"""Azure Cognitive Search service."""
from typing import List, Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchFieldDataType
)
from processors.document_parser import ProcessedChunk
from utils.logger import get_logger
from utils.retry import retry_with_backoff

logger = get_logger(__name__)


class SearchService:
    """Service for Azure Cognitive Search operations."""
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        index_name: str,
        batch_size: int = 1000
    ):
        """
        Initialize search service.
        
        Args:
            endpoint: Azure Search endpoint
            api_key: Azure Search API key
            index_name: Name of the search index
            batch_size: Number of documents per upload batch
        """
        credential = AzureKeyCredential(api_key)
        self.index_client = SearchIndexClient(endpoint, credential)
        self.search_client = SearchClient(endpoint, index_name, credential)
        self.index_name = index_name
        self.batch_size = batch_size
    
    def create_or_update_index(self) -> None:
        """Create or update the search index with proper schema."""
        try:
            # Define vector search configuration
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="hnsw-config",
                        parameters={
                            "m": 4,
                            "efConstruction": 400,
                            "efSearch": 500,
                            "metric": "cosine"
                        }
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        name="vector-profile",
                        algorithm_configuration_name="hnsw-config"
                    )
                ]
            )
            
            # Define index fields
            fields = [
                SimpleField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True
                ),
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                    searchable=True
                ),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="vector-profile"
                ),
                SearchableField(
                    name="title",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True
                ),
                SimpleField(
                    name="url",
                    type=SearchFieldDataType.String,
                    filterable=True
                ),
                SearchableField(
                    name="author",
                    type=SearchFieldDataType.String,
                    searchable=True,
                    filterable=True
                ),
                SimpleField(
                    name="source",
                    type=SearchFieldDataType.String,
                    filterable=True
                ),
                SimpleField(
                    name="space_key",
                    type=SearchFieldDataType.String,
                    filterable=True
                ),
                SimpleField(
                    name="created_date",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    sortable=True
                ),
                SimpleField(
                    name="modified_date",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    sortable=True
                ),
                SearchField(
                    name="tags",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                    searchable=True,
                    filterable=True
                ),
                SimpleField(
                    name="chunk_index",
                    type=SearchFieldDataType.Int32,
                    filterable=True
                ),
                SimpleField(
                    name="total_chunks",
                    type=SearchFieldDataType.Int32,
                    filterable=True
                )
            ]
            
            # Create index
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search
            )
            
            self.index_client.create_or_update_index(index)
            logger.info(f"Created/updated search index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error creating/updating index: {str(e)}")
            raise
    
    def clear_index(self) -> None:
        """Clear all documents from the index."""
        try:
            # Get all document IDs
            results = self.search_client.search(
                search_text="*",
                select=["id"],
                top=100000
            )
            
            doc_ids = [doc["id"] for doc in results]
            
            if not doc_ids:
                logger.info("Index is already empty")
                return
            
            # Delete documents in batches
            for i in range(0, len(doc_ids), self.batch_size):
                batch_ids = doc_ids[i:i + self.batch_size]
                documents_to_delete = [{"id": doc_id} for doc_id in batch_ids]
                self.search_client.delete_documents(documents_to_delete)
                logger.info(f"Deleted {len(batch_ids)} documents from index")
            
            logger.info(f"Cleared {len(doc_ids)} documents from index")
            
        except Exception as e:
            logger.error(f"Error clearing index: {str(e)}")
            raise
    
    @retry_with_backoff(max_retries=3, exceptions=(Exception,))
    def upload_documents(
        self,
        chunks_with_embeddings: List[tuple]
    ) -> Dict[str, int]:
        """
        Upload documents with embeddings to the search index.
        
        Args:
            chunks_with_embeddings: List of (ProcessedChunk, embedding) tuples
            
        Returns:
            Dictionary with upload statistics
        """
        if not chunks_with_embeddings:
            logger.warning("No documents to upload")
            return {"uploaded": 0, "failed": 0}
        
        uploaded_count = 0
        failed_count = 0
        total = len(chunks_with_embeddings)
        
        # Process in batches
        for i in range(0, total, self.batch_size):
            batch = chunks_with_embeddings[i:i + self.batch_size]
            
            # Convert to search documents
            documents = []
            for chunk, embedding in batch:
                doc = {
                    "id": chunk.id,
                    "content": chunk.content,
                    "content_vector": embedding,
                    "title": chunk.title,
                    "url": chunk.url,
                    "author": chunk.author,
                    "source": chunk.source,
                    "space_key": chunk.space_key,
                    "created_date": chunk.created_date,
                    "modified_date": chunk.modified_date,
                    "tags": chunk.tags if chunk.tags else [],
                    "chunk_index": chunk.chunk_index,
                    "total_chunks": chunk.total_chunks
                }
                documents.append(doc)
            
            try:
                result = self.search_client.upload_documents(documents)
                
                # Count successes and failures
                for item in result:
                    if item.succeeded:
                        uploaded_count += 1
                    else:
                        failed_count += 1
                        logger.warning(
                            f"Failed to upload document {item.key}: "
                            f"{item.error_message}"
                        )
                
                logger.info(
                    f"Uploaded batch {i//self.batch_size + 1}/"
                    f"{(total + self.batch_size - 1)//self.batch_size} "
                    f"({len(batch)} documents)"
                )
                
            except Exception as e:
                logger.error(f"Error uploading batch: {str(e)}")
                failed_count += len(batch)
                continue
        
        logger.info(
            f"Upload complete: {uploaded_count} succeeded, {failed_count} failed"
        )
        
        return {
            "uploaded": uploaded_count,
            "failed": failed_count
        }

