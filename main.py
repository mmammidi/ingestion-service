"""Main entry point for the data ingestion service."""
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from config.settings import settings
from connectors.confluence_connector import ConfluenceConnector
from processors.document_parser import DocumentParser
from services.embedding_service import EmbeddingService
from services.search_service import SearchService
from orchestrator.sync_orchestrator import SyncOrchestrator
from utils.logger import setup_logger, get_logger

# Set up main logger
setup_logger(__name__, settings.LOG_LEVEL)
logger = get_logger(__name__)


def initialize_services() -> SyncOrchestrator:
    """
    Initialize all services and return the sync orchestrator.
    
    Returns:
        Configured SyncOrchestrator instance
    """
    logger.info("Initializing services...")
    
    # Initialize Confluence connector
    confluence_connector = ConfluenceConnector(
        base_url=settings.CONFLUENCE_URL,
        username=settings.CONFLUENCE_USERNAME,
        api_token=settings.CONFLUENCE_API_TOKEN,
        space_keys=settings.CONFLUENCE_SPACES
    )
    
    # Initialize document parser
    document_parser = DocumentParser(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    
    # Initialize embedding service
    embedding_service = EmbeddingService(
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        deployment_name=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        batch_size=settings.EMBEDDING_BATCH_SIZE
    )
    
    # Initialize search service
    search_service = SearchService(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        api_key=settings.AZURE_SEARCH_API_KEY,
        index_name=settings.AZURE_SEARCH_INDEX_NAME,
        batch_size=settings.INDEXING_BATCH_SIZE
    )
    
    # Initialize orchestrator
    orchestrator = SyncOrchestrator(
        confluence_connector=confluence_connector,
        document_parser=document_parser,
        embedding_service=embedding_service,
        search_service=search_service
    )
    
    logger.info("Services initialized successfully")
    return orchestrator


def run_sync():
    """Run a single sync operation."""
    try:
        orchestrator = initialize_services()
        stats = orchestrator.run_full_sync()
        
        if not stats["success"]:
            logger.error("Sync completed with errors")
            sys.exit(1)
        
        logger.info("Sync completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to run sync: {str(e)}", exc_info=True)
        sys.exit(1)


def run_scheduler():
    """Run the scheduler for recurring sync operations."""
    logger.info("Starting scheduler...")
    logger.info(f"Sync schedule: {settings.SYNC_CRON}")
    logger.info(f"Timezone: {settings.SYNC_TIMEZONE}")
    
    scheduler = BlockingScheduler()
    
    # Parse cron expression (minute hour day month day_of_week)
    cron_parts = settings.SYNC_CRON.split()
    if len(cron_parts) != 5:
        logger.error(f"Invalid cron expression: {settings.SYNC_CRON}")
        sys.exit(1)
    
    tz = timezone(settings.SYNC_TIMEZONE)
    trigger = CronTrigger(
        minute=cron_parts[0],
        hour=cron_parts[1],
        day=cron_parts[2],
        month=cron_parts[3],
        day_of_week=cron_parts[4],
        timezone=tz
    )
    
    scheduler.add_job(
        run_sync,
        trigger=trigger,
        id='full_sync_job',
        name='Full Sync Job',
        replace_existing=True
    )
    
    logger.info("Scheduler started. Press Ctrl+C to exit.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("Data Ingestion Service - Confluence to Azure Search")
    logger.info("=" * 80)
    
    # Validate configuration
    try:
        settings.validate()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "sync":
            logger.info("Running one-time sync...")
            run_sync()
        elif command == "schedule":
            logger.info("Running in scheduled mode...")
            run_scheduler()
        else:
            logger.error(f"Unknown command: {command}")
            logger.info("Usage: python main.py [sync|schedule]")
            sys.exit(1)
    else:
        # Default: run scheduler
        logger.info("No command specified, running in scheduled mode...")
        run_scheduler()


if __name__ == "__main__":
    main()

