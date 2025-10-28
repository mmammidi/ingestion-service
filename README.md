# Data Ingestion Service - Confluence to Azure Search

A Python-based data ingestion service that syncs Confluence content to Azure Cognitive Search with vector embeddings for semantic search capabilities.

## Features

- ✅ **Full Sync from Confluence**: Fetch all pages from specified Confluence spaces
- ✅ **Smart Document Processing**: Clean, parse, and chunk documents intelligently
- ✅ **Vector Embeddings**: Generate embeddings using Azure OpenAI (text-embedding-3-large)
- ✅ **Azure Search Integration**: Upload to Azure Cognitive Search with hybrid search support
- ✅ **Scheduled Execution**: Automatic daily syncs using APScheduler
- ✅ **Robust Error Handling**: Retry logic with exponential backoff
- ✅ **Comprehensive Logging**: Detailed structured logging for monitoring

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

### Components

```
ingestion_service/
├── main.py                         # Entry point with scheduler
├── config/
│   └── settings.py                 # Configuration from .env
├── connectors/
│   ├── base_connector.py           # Abstract base class
│   └── confluence_connector.py     # Confluence API client
├── processors/
│   ├── document_parser.py          # Parse different formats
│   ├── chunker.py                  # Smart chunking logic
│   └── text_cleaner.py             # Text cleaning utilities
├── services/
│   ├── embedding_service.py        # Azure OpenAI embeddings
│   └── search_service.py           # Azure Search operations
├── orchestrator/
│   └── sync_orchestrator.py        # Full sync workflow
└── utils/
    ├── logger.py                   # Structured logging
    └── retry.py                    # Retry decorators
```

## Prerequisites

- Python 3.8+
- Confluence Cloud account with API access
- Azure OpenAI service with text-embedding-3-large deployment
- Azure Cognitive Search service

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ingestion-service
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

## Configuration

### Environment Variables

Edit `.env` file with your settings:

#### Confluence Settings
- `CONFLUENCE_URL`: Your Confluence base URL
- `CONFLUENCE_USERNAME`: Your Confluence email
- `CONFLUENCE_API_TOKEN`: API token from Confluence
- `CONFLUENCE_SPACES`: Comma-separated list of space keys

#### Azure OpenAI Settings
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT`: Deployment name (default: text-embedding-3-large)

#### Azure Search Settings
- `AZURE_SEARCH_ENDPOINT`: Your Azure Search endpoint
- `AZURE_SEARCH_API_KEY`: Your Azure Search admin key
- `AZURE_SEARCH_INDEX_NAME`: Index name (default: knowledge-base-index)

#### Processing Settings
- `CHUNK_SIZE`: Token chunk size (default: 800)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 100)
- `EMBEDDING_BATCH_SIZE`: Embeddings per request (default: 16)
- `INDEXING_BATCH_SIZE`: Documents per upload batch (default: 1000)

#### Scheduler Settings
- `SYNC_CRON`: Cron expression (default: 0 2 * * * for 2 AM daily)
- `SYNC_TIMEZONE`: Timezone (default: UTC)

#### Logging
- `LOG_LEVEL`: Logging level (default: INFO)

## Usage

### One-Time Sync

Run a single sync operation:

```bash
python main.py sync
```

### Scheduled Mode

Run the service with automatic scheduling:

```bash
python main.py schedule
```

This will run syncs according to the `SYNC_CRON` schedule (default: daily at 2 AM).

### Default Mode

If no command is specified, the service runs in scheduled mode:

```bash
python main.py
```

## Sync Process

The full sync workflow:

1. **Create/Update Index**: Ensure Azure Search index exists with proper schema
2. **Clear Index**: Remove all existing documents
3. **Connect to Confluence**: Authenticate and verify connection
4. **Fetch Documents**: Retrieve all pages from configured spaces
5. **Process Documents**: Clean, parse, and chunk content
6. **Generate Embeddings**: Create vector embeddings using Azure OpenAI
7. **Upload to Search**: Batch upload documents with embeddings to Azure Search
8. **Log Results**: Record statistics and any errors

## Search Index Schema

The Azure Search index includes:

- **id**: Unique document identifier (key)
- **content**: Full text content (searchable)
- **content_vector**: 3072-dimensional embedding vector
- **title**: Document title (searchable, filterable)
- **url**: Original document URL
- **author**: Document author (searchable, filterable)
- **source**: Source system ("confluence")
- **created_date**: Creation date (filterable, sortable)
- **modified_date**: Last modified date (filterable, sortable)
- **tags**: Document tags/labels (searchable, filterable)
- **chunk_index**: Chunk position in document
- **total_chunks**: Total chunks in document

## Monitoring

### Logs

The service provides structured logging:

```
2024-01-15 02:00:00 - main - INFO - Starting full sync process
2024-01-15 02:00:05 - search_service - INFO - Cleared 1250 documents from index
2024-01-15 02:05:30 - confluence_connector - INFO - Fetched 127 pages from space TECH
2024-01-15 02:08:15 - document_parser - INFO - Processed 127 documents into 856 chunks
2024-01-15 02:12:45 - embedding_service - INFO - Successfully embedded 856/856 chunks
2024-01-15 02:15:20 - search_service - INFO - Upload complete: 856 succeeded, 0 failed
2024-01-15 02:15:21 - sync_orchestrator - INFO - Sync Complete - Duration: 921.34 seconds
```

### Metrics

Each sync logs:
- Total documents fetched
- Chunks created
- Embeddings generated
- Documents uploaded
- Failed uploads
- Sync duration
- Error details

## Error Handling

The service implements three levels of error handling:

1. **Transient Errors** (network, rate limits): Retry with exponential backoff
2. **Document-Level Errors** (parse failures): Log and skip, continue processing
3. **Fatal Errors** (auth failures): Stop sync and report

## Performance

Expected metrics for ~5,000 documents:

- **Processing Speed**: 50-100 documents/minute
- **Total Sync Time**: 1-3 hours
- **Memory Usage**: 500MB-2GB
- **API Calls**: Batched for efficiency

## Troubleshooting

### Authentication Errors

**Problem**: `401 Unauthorized` from Confluence
**Solution**: Verify `CONFLUENCE_API_TOKEN` and `CONFLUENCE_USERNAME`

### Index Creation Errors

**Problem**: Failed to create Azure Search index
**Solution**: Ensure your API key has admin permissions

### Embedding Errors

**Problem**: `429 Rate Limit Exceeded`
**Solution**: The service automatically retries with backoff. Consider reducing `EMBEDDING_BATCH_SIZE`

### Memory Issues

**Problem**: Out of memory errors
**Solution**: Reduce `INDEXING_BATCH_SIZE` or `EMBEDDING_BATCH_SIZE`

## Development

### Project Structure

- **connectors/**: Data source integrations
- **processors/**: Document processing logic
- **services/**: External service integrations (Azure)
- **orchestrator/**: Workflow coordination
- **utils/**: Shared utilities
- **config/**: Configuration management

### Adding New Features

To add a new data source (e.g., Google Drive):

1. Implement `BaseConnector` interface
2. Add configuration to `settings.py`
3. Update orchestrator to include new connector
4. Update `.env.example` and documentation

## Future Enhancements

- ⏳ Incremental sync (delta updates)
- ⏳ Webhook support for real-time updates
- ⏳ Additional data sources (Google Drive, SharePoint)
- ⏳ Advanced metrics and monitoring
- ⏳ Resume capability for long-running syncs

## License

[Your License Here]

## Support

For issues and questions:
- Check logs in console output
- Review [ARCHITECTURE.md](ARCHITECTURE.md)
- Contact: [Your Contact Info]

