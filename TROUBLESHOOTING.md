# Troubleshooting Guide

Common issues and solutions for the Confluence Data Ingestion Service.

## Authentication Issues

### Confluence 401 Unauthorized

**Symptoms:**
```
ERROR - Failed to connect to Confluence: 401 Client Error: Unauthorized
```

**Solutions:**
1. Verify `CONFLUENCE_USERNAME` is your email address (not username)
2. Check `CONFLUENCE_API_TOKEN` is correct and hasn't expired
3. Ensure you copied the full token without extra spaces
4. Test manually with curl:
```bash
curl -u your-email@company.com:your-api-token https://yourcompany.atlassian.net/wiki/rest/api/space
```

### Azure OpenAI Authentication Error

**Symptoms:**
```
ERROR - Error generating embeddings: 401 Unauthorized
```

**Solutions:**
1. Verify `AZURE_OPENAI_API_KEY` is correct
2. Check endpoint format: `https://YOUR-RESOURCE.openai.azure.com/` (trailing slash)
3. Ensure API key is for the correct resource
4. Verify the deployment name matches your Azure OpenAI deployment

### Azure Search Authentication Error

**Symptoms:**
```
ERROR - Error creating/updating index: 403 Forbidden
```

**Solutions:**
1. Use the **admin key** (not query key) for `AZURE_SEARCH_API_KEY`
2. Verify endpoint format: `https://YOUR-SERVICE.search.windows.net`
3. Check firewall rules allow your IP address

## Configuration Issues

### Missing Environment Variables

**Symptoms:**
```
ERROR - Configuration error: Missing required environment variables: CONFLUENCE_URL, AZURE_OPENAI_ENDPOINT
```

**Solutions:**
1. Ensure `.env` file exists in project root
2. Check all required variables are set
3. Remove any trailing spaces in values
4. Don't use quotes around values in .env file

### Invalid Cron Expression

**Symptoms:**
```
ERROR - Invalid cron expression: 0 2 * *
```

**Solutions:**
1. Cron format requires 5 parts: `minute hour day month day_of_week`
2. Example valid expressions:
   - `0 2 * * *` (daily at 2 AM)
   - `*/30 * * * *` (every 30 minutes)
   - `0 0 * * 0` (weekly on Sunday midnight)

### Empty Space Keys

**Symptoms:**
```
ERROR - CONFLUENCE_SPACES must contain at least one space key
```

**Solutions:**
1. Add at least one space key to `CONFLUENCE_SPACES`
2. Format: `SPACE1,SPACE2,SPACE3` (comma-separated, no spaces)
3. Space keys are case-sensitive
4. Find space keys in Confluence URL: `/spaces/SPACEKEY/pages`

## Data Fetching Issues

### No Documents Fetched

**Symptoms:**
```
INFO - Total documents fetched from Confluence: 0
```

**Solutions:**
1. Verify space keys are correct (case-sensitive)
2. Check you have read access to those spaces
3. Ensure spaces contain published pages (not just drafts)
4. Try fetching from a known public space first
5. Check Confluence permissions for your API user

### Some Pages Missing

**Symptoms:**
- Expected 100 pages but only got 50
- Certain pages not appearing in search

**Solutions:**
1. Check page permissions (private pages won't be fetched)
2. Verify pages are published (not drafts)
3. Check logs for parsing errors on specific pages
4. Ensure pages aren't archived

### HTML Parsing Errors

**Symptoms:**
```
WARNING - Error parsing HTML: ...
```

**Solutions:**
1. Usually non-fatal, service continues with raw HTML
2. Check if beautifulsoup4 is installed: `pip list | grep beautifulsoup`
3. Update beautifulsoup4: `pip install --upgrade beautifulsoup4 lxml`

## Processing Issues

### Memory Errors

**Symptoms:**
```
MemoryError: Unable to allocate array
```

**Solutions:**
1. Reduce `EMBEDDING_BATCH_SIZE` (try 8 or 4)
2. Reduce `INDEXING_BATCH_SIZE` (try 500 or 100)
3. Increase system memory
4. Process fewer documents at once

### Chunking Produces No Results

**Symptoms:**
```
WARNING - Document doc_id produced no chunks
```

**Solutions:**
1. Check if document content is empty
2. Verify text cleaning isn't removing all content
3. Try increasing `CHUNK_SIZE`
4. Check document for valid text content

## API Issues

### Rate Limiting

**Symptoms:**
```
WARNING - rate limit exceeded, retrying in 60s
ERROR - Failed after 3 retries: 429 Too Many Requests
```

**Solutions:**
1. Service automatically retries with backoff
2. Reduce batch sizes to slow down requests
3. Increase `EMBEDDING_BATCH_SIZE` interval in code
4. Contact Azure support to increase quota
5. Spread sync across multiple time periods

### Timeout Errors

**Symptoms:**
```
ERROR - Request timed out: ReadTimeout
```

**Solutions:**
1. Service will retry automatically
2. Check network connectivity
3. Try during off-peak hours
4. Reduce batch sizes

### Connection Errors

**Symptoms:**
```
ERROR - Connection error: Failed to establish a new connection
```

**Solutions:**
1. Check internet connectivity
2. Verify firewall isn't blocking Azure endpoints
3. Check if services are experiencing outages
4. Try with VPN if behind corporate firewall

## Embedding Issues

### Wrong Embedding Dimensions

**Symptoms:**
```
ERROR - Vector dimension mismatch: expected 3072, got 1536
```

**Solutions:**
1. Verify deployment uses `text-embedding-3-large` (3072 dims)
2. Check `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` matches deployment name
3. Update index schema if you changed models
4. Delete and recreate index if needed

### Embedding Generation Failures

**Symptoms:**
```
ERROR - Failed to embed batch starting at index 0
```

**Solutions:**
1. Check Azure OpenAI service is running
2. Verify quota limits haven't been exceeded
3. Check if content contains invalid characters
4. Try with smaller batch size

## Index Issues

### Failed to Create Index

**Symptoms:**
```
ERROR - Error creating/updating index: Bad Request
```

**Solutions:**
1. Verify index name follows naming rules (lowercase, no special chars)
2. Check Azure Search service tier supports vector search
3. Ensure you're using a supported API version
4. Try deleting existing index first (manual cleanup)

### Upload Failures

**Symptoms:**
```
WARNING - Failed to upload document doc_123: Request payload too large
```

**Solutions:**
1. Reduce `CHUNK_SIZE` to create smaller documents
2. Reduce `INDEXING_BATCH_SIZE`
3. Check for extremely large text chunks
4. Verify content doesn't exceed field limits

### Index Not Searchable

**Symptoms:**
- Documents uploaded but searches return nothing
- Index shows 0 documents

**Solutions:**
1. Wait a few minutes for indexing to complete
2. Check Azure Search indexer status in portal
3. Verify documents were actually uploaded (check logs)
4. Try a simple wildcard search: `*`
5. Check index statistics in Azure Portal

## Performance Issues

### Sync Takes Too Long

**Symptoms:**
- Sync taking more than 4-5 hours
- Process seems stuck

**Solutions:**
1. Check logs to see which step is slow
2. Increase batch sizes for faster processing
3. Check network latency to Azure services
4. Run during off-peak hours
5. Consider parallel processing (future enhancement)

### High Memory Usage

**Symptoms:**
- Memory usage growing continuously
- System becomes unresponsive

**Solutions:**
1. Reduce `EMBEDDING_BATCH_SIZE`
2. Reduce `INDEXING_BATCH_SIZE`
3. Process documents in smaller batches
4. Add memory limits to Python process

## Logging Issues

### No Logs Appearing

**Symptoms:**
- Console shows no output
- Can't debug issues

**Solutions:**
1. Check `LOG_LEVEL` in .env (should be INFO or DEBUG)
2. Verify logger configuration in utils/logger.py
3. Try running with: `python main.py sync 2>&1 | tee sync.log`

### Too Many Logs

**Symptoms:**
- Console flooded with messages
- Hard to find relevant information

**Solutions:**
1. Set `LOG_LEVEL=WARNING` or `LOG_LEVEL=ERROR`
2. Redirect output to file: `python main.py sync > sync.log 2>&1`
3. Use grep to filter: `python main.py sync 2>&1 | grep ERROR`

## Scheduler Issues

### Scheduler Not Running Jobs

**Symptoms:**
- Scheduler starts but sync never runs
- "Scheduler started" message but no activity

**Solutions:**
1. Check cron expression is valid
2. Verify timezone setting
3. Try a more frequent schedule for testing (e.g., `*/5 * * * *`)
4. Check system time is correct
5. Review scheduler logs for errors

### Process Dies Overnight

**Symptoms:**
- Scheduler runs but process stops after hours
- Need to restart manually

**Solutions:**
1. Run as a system service (systemd/Windows Service)
2. Use process manager (pm2, supervisor)
3. Check for out-of-memory issues in system logs
4. Add automatic restart on failure
5. Monitor with external health checks

## Debugging Tips

### Enable Debug Logging

Set in `.env`:
```env
LOG_LEVEL=DEBUG
```

### Test Individual Components

```python
# Test Confluence connection
from config.settings import settings
from connectors.confluence_connector import ConfluenceConnector

connector = ConfluenceConnector(
    settings.CONFLUENCE_URL,
    settings.CONFLUENCE_USERNAME,
    settings.CONFLUENCE_API_TOKEN,
    settings.CONFLUENCE_SPACES
)
connector.connect()
docs = connector.fetch_all_documents()
print(f"Fetched {len(docs)} documents")
```

### Check Azure Search Index

```bash
# List indexes
curl -X GET "https://YOUR-SERVICE.search.windows.net/indexes?api-version=2023-11-01" \
  -H "api-key: YOUR-API-KEY"

# Get document count
curl -X GET "https://YOUR-SERVICE.search.windows.net/indexes/knowledge-base-index/stats?api-version=2023-11-01" \
  -H "api-key: YOUR-API-KEY"
```

### Validate Embeddings

```python
from services.embedding_service import EmbeddingService
from config.settings import settings

service = EmbeddingService(
    settings.AZURE_OPENAI_ENDPOINT,
    settings.AZURE_OPENAI_API_KEY,
    settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
)

vectors = service.generate_embeddings(["test text"])
print(f"Vector dimensions: {len(vectors[0])}")  # Should be 3072
```

## Getting Help

If you've tried the solutions above and still have issues:

1. **Check Logs**: Review full logs with DEBUG level
2. **Simplify**: Test with one space and small dataset
3. **Version Check**: Ensure dependencies are up to date
4. **Permissions**: Verify all service permissions
5. **Support**: Contact with:
   - Error messages
   - Configuration (redact secrets)
   - Steps to reproduce
   - Environment details (OS, Python version)

## Known Limitations

1. **Large Documents**: Very large documents (>1MB text) may timeout
2. **Special Characters**: Some Unicode characters may not parse correctly
3. **Rate Limits**: Azure OpenAI has token/minute limits
4. **Memory**: Processing 10,000+ documents requires significant RAM
5. **Confluence API**: Some page types (e.g., Whiteboards) not fully supported

See ARCHITECTURE.md for design decisions and future enhancements.

