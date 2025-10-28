# Quick Start Guide

Get your Confluence data ingestion service running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Configure Environment

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:

### Get Confluence API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy the token to `CONFLUENCE_API_TOKEN`

### Get Confluence Space Keys
1. Go to your Confluence spaces
2. Copy the space key from the URL (e.g., `TECH` in `/spaces/TECH/overview`)
3. Add to `CONFLUENCE_SPACES` (comma-separated if multiple)

### Azure OpenAI Setup
1. Get your endpoint from Azure Portal → Azure OpenAI resource
2. Get your API key from Keys and Endpoint section
3. Ensure you have a deployment of `text-embedding-3-large`

### Azure Search Setup
1. Get your endpoint from Azure Portal → Search Service
2. Get your admin key from Keys section
3. The service will automatically create the index

## Step 3: Test Configuration

Run a one-time sync to test:

```bash
python main.py sync
```

You should see output like:
```
2024-01-15 10:00:00 - main - INFO - Starting full sync process
2024-01-15 10:00:05 - confluence_connector - INFO - Successfully connected to Confluence
2024-01-15 10:05:30 - confluence_connector - INFO - Fetched 127 pages from space TECH
...
2024-01-15 10:15:21 - sync_orchestrator - INFO - Sync Complete
```

## Step 4: Enable Scheduled Sync

Run the service with automatic daily syncs:

```bash
python main.py schedule
```

This will sync daily at 2 AM UTC (configurable via `SYNC_CRON` in `.env`).

## Troubleshooting

### "Missing required environment variables"
- Check that all required variables in `.env` are filled in
- Ensure no trailing spaces in values

### "401 Unauthorized" from Confluence
- Verify your API token is correct
- Ensure username is your email address
- Check API token hasn't expired

### "Failed to connect to Azure OpenAI"
- Verify endpoint URL (should end with `.openai.azure.com/`)
- Check API key is correct
- Ensure deployment name matches your actual deployment

### "No documents fetched"
- Verify space keys are correct (case-sensitive)
- Check you have access to those spaces in Confluence
- Ensure spaces contain pages

## Next Steps

1. **Monitor Logs**: Check console output for sync progress
2. **Test Search**: Query your Azure Search index to verify data
3. **Adjust Schedule**: Modify `SYNC_CRON` for different sync times
4. **Tune Performance**: Adjust batch sizes in `.env` if needed

## Common Configurations

### Sync more frequently (every 6 hours)
```env
SYNC_CRON=0 */6 * * *
```

### Sync only on weekdays at 3 AM
```env
SYNC_CRON=0 3 * * 1-5
```

### Sync every Sunday at midnight
```env
SYNC_CRON=0 0 * * 0
```

## Production Deployment

For production, consider:

1. **Run as a service** (systemd on Linux, Windows Service on Windows)
2. **Container deployment** (Docker/Kubernetes)
3. **Monitoring** (integrate with your logging/monitoring stack)
4. **Alerts** (set up notifications for failed syncs)
5. **Backup** (ensure Azure Search has proper backup/recovery)

See README.md for complete documentation.

