"""Full sync orchestrator - coordinates the entire sync process."""
from typing import Dict, Any
from datetime import datetime
from connectors.confluence_connector import ConfluenceConnector
from processors.document_parser import DocumentParser
from services.embedding_service import EmbeddingService
from services.search_service import SearchService
from utils.logger import get_logger

logger = get_logger(__name__)


class SyncOrchestrator:
    """Orchestrates the full sync workflow."""
    
    def __init__(
        self,
        confluence_connector: ConfluenceConnector,
        document_parser: DocumentParser,
        embedding_service: EmbeddingService,
        search_service: SearchService
    ):
        """
        Initialize sync orchestrator.
        
        Args:
            confluence_connector: Confluence data connector
            document_parser: Document processing service
            embedding_service: Embedding generation service
            search_service: Azure Search service
        """
        self.confluence_connector = confluence_connector
        self.document_parser = document_parser
        self.embedding_service = embedding_service
        self.search_service = search_service
    
    def run_full_sync(self) -> Dict[str, Any]:
        """
        Execute the complete full sync workflow.
        
        Returns:
            Dictionary with sync statistics and results
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info("Starting full sync process")
        logger.info("=" * 80)
        
        stats = {
            "start_time": start_time.isoformat(),
            "documents_fetched": 0,
            "chunks_created": 0,
            "chunks_embedded": 0,
            "chunks_uploaded": 0,
            "failed_uploads": 0,
            "errors": [],
            "success": False
        }
        
        try:
            # Step 1: Ensure index exists and is properly configured
            logger.info("Step 1: Ensuring search index exists...")
            self.search_service.create_or_update_index()
            
            # Step 2: Clear the index
            logger.info("Step 2: Clearing search index...")
            self.search_service.clear_index()
            
            # Step 3: Connect to Confluence
            logger.info("Step 3: Connecting to Confluence...")
            self.confluence_connector.connect()
            
            # Step 4: Fetch documents from Confluence
            logger.info("Step 4: Fetching documents from Confluence...")
            documents = self.confluence_connector.fetch_all_documents()
            stats["documents_fetched"] = len(documents)
            
            if not documents:
                logger.warning("No documents fetched from Confluence")
                stats["success"] = True
                return stats
            
            # Step 5: Process documents into chunks
            logger.info("Step 5: Processing and chunking documents...")
            chunks = self.document_parser.process_documents(documents)
            stats["chunks_created"] = len(chunks)
            
            if not chunks:
                logger.warning("No chunks created from documents")
                stats["success"] = True
                return stats
            
            # Step 6: Generate embeddings
            logger.info("Step 6: Generating embeddings...")
            chunks_with_embeddings = self.embedding_service.embed_chunks(chunks)
            stats["chunks_embedded"] = len(chunks_with_embeddings)
            
            if not chunks_with_embeddings:
                logger.error("Failed to generate embeddings")
                return stats
            
            # Step 7: Upload to Azure Search
            logger.info("Step 7: Uploading documents to Azure Search...")
            upload_results = self.search_service.upload_documents(
                chunks_with_embeddings
            )
            stats["chunks_uploaded"] = upload_results["uploaded"]
            stats["failed_uploads"] = upload_results["failed"]
            
            # Mark as successful
            stats["success"] = True
            
        except Exception as e:
            error_msg = f"Fatal error during sync: {str(e)}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            stats["success"] = False
        
        finally:
            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            stats["end_time"] = end_time.isoformat()
            stats["duration_seconds"] = duration
            
            # Log summary
            logger.info("=" * 80)
            logger.info("Sync Complete")
            logger.info("=" * 80)
            logger.info(f"Status: {'SUCCESS' if stats['success'] else 'FAILED'}")
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Documents fetched: {stats['documents_fetched']}")
            logger.info(f"Chunks created: {stats['chunks_created']}")
            logger.info(f"Chunks embedded: {stats['chunks_embedded']}")
            logger.info(f"Chunks uploaded: {stats['chunks_uploaded']}")
            logger.info(f"Failed uploads: {stats['failed_uploads']}")
            
            if stats["errors"]:
                logger.error(f"Errors encountered: {len(stats['errors'])}")
                for error in stats["errors"]:
                    logger.error(f"  - {error}")
            
            logger.info("=" * 80)
        
        return stats

