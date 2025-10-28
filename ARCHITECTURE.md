# Data Ingestion Service - Architecture

## Simplified Architecture (Full Sync Only)

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │   Confluence     │              │   Google Drive   │         │
│  │   - Spaces       │              │   - Folders      │         │
│  │   - Pages        │              │   - Documents    │         │
│  │   - Attachments  │              │   - Sheets/Slides│         │
│  └────────┬─────────┘              └────────┬─────────┘         │
└───────────┼────────────────────────────────┼───────────────────┘
            │                                │
            │ REST API                       │ Drive API v3
            │                                │
┌───────────▼────────────────────────────────▼───────────────────┐
│                  INGESTION SERVICE (Python)                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Scheduler (APScheduler)                    │   │
│  │              Cron: 0 2 * * * (Daily at 2 AM)           │   │
│  └────────────────────────┬───────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                  Full Sync Orchestrator                 │   │
│  │                                                          │   │
│  │  Step 1: Clear Azure Search Index                       │   │
│  │  Step 2: Fetch all documents from sources              │   │
│  │  Step 3: Process & chunk documents                     │   │
│  │  Step 4: Generate embeddings                           │   │
│  │  Step 5: Index to Azure Search                         │   │
│  └────────────────────────────────────────────────────────┘   │
│                            │                                    │
│  ┌─────────────┬──────────┴──────────┬────────────────┐       │
│  │             │                      │                │       │
│  ▼             ▼                      ▼                ▼       │
│ ┌──────┐  ┌─────────┐  ┌──────────┐  ┌──────────────┐        │
│ │Connec│  │Document │  │Embedding │  │Search        │        │
│ │tors  │  │Processor│  │Service   │  │Indexer       │        │
│ └──────┘  └─────────┘  └──────────┘  └──────────────┘        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ Direct Upload
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              Azure Cognitive Search Index                        │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Index: knowledge-base-index                                │ │
│  │                                                              │ │
│  │  Fields:                                                     │ │
│  │  • id (key)                                                  │ │
│  │  • content (searchable, fulltext)                           │ │
│  │  • content_vector (3072 dims)                               │ │
│  │  • title, author, source, tags (filterable)                 │ │
│  │  • created_date, modified_date (sortable)                   │ │
│  │                                                              │ │
│  │  Capabilities:                                               │ │
│  │  ✓ Full-text search (BM25)                                  │ │
│  │  ✓ Vector search (HNSW + Cosine similarity)                 │ │
│  │  ✓ Semantic search (L2 ranking)                             │ │
│  │  ✓ Hybrid search                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow - Full Sync Process

```
START (Scheduled Trigger: Daily at 2 AM)
  │
  ▼
┌─────────────────────────────────────┐
│ 1. Clear Azure Search Index         │
│    - Delete all existing documents  │
│    - Index is now empty             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Fetch from Confluence            │
│    - Connect to each space          │
│    - Get all pages                  │
│    - Download attachments           │
│    - Extract metadata               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Fetch from Google Drive          │
│    - Connect to specified folders   │
│    - List all files recursively     │
│    - Download/export documents      │
│    - Extract metadata               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Process Documents                │
│    For each document:               │
│    - Parse content (HTML, PDF, etc) │
│    - Clean & extract text           │
│    - Chunk into 800-token segments  │
│    - Preserve metadata              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Generate Embeddings              │
│    - Batch chunks (16 per request)  │
│    - Call Azure OpenAI              │
│    - Model: text-embedding-3-large  │
│    - Generate 3072-dim vectors      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 6. Index to Azure Search            │
│    - Batch upload (1000 docs/batch) │
│    - Include content + vector       │
│    - Include all metadata           │
│    - Retry on failures              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 7. Log Results                      │
│    - Total documents processed      │
│    - Success/failure count          │
│    - Duration                       │
│    - Errors (if any)                │
└──────────────┬──────────────────────┘
               │
               ▼
              END
```

## Component Architecture

```
ingestion_service/
├── main.py                         # Entry point with scheduler
├── config/
│   └── settings.py                 # Configuration from .env
├── connectors/
│   ├── base_connector.py           # Abstract base class
│   ├── confluence_connector.py     # Confluence API client
│   └── google_drive_connector.py   # Google Drive API client
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

## Sequence Diagram - Full Sync

```
Scheduler          Orchestrator    Connectors    Processor    Embedding    Search
    │                  │               │             │            │           │
    │─── Trigger ─────>│               │             │            │           │
    │   (2 AM Daily)   │               │             │            │           │
    │                  │               │             │            │           │
    │                  │─────────────────────────────────────────────────────>│
    │                  │                         Clear Index                  │
    │                  │<─────────────────────────────────────────────────────│
    │                  │                                                       │
    │                  │──── Get Docs ──>│             │            │           │
    │                  │<─── Return ─────│             │            │           │
    │                  │                 │             │            │           │
    │                  │──── Process ────────────────>│            │           │
    │                  │<──── Chunks ──────────────────│            │           │
    │                  │                               │            │           │
    │                  │──── Generate Embeddings ─────────────────>│           │
    │                  │<──── Vectors ──────────────────────────────│           │
    │                  │                                            │           │
    │                  │──── Upload Documents ─────────────────────────────────>│
    │                  │<──── Success ───────────────────────────────────────────│
    │                  │                                                         │
    │<─── Complete ────│                                                         │
    │                  │                                                         │
```

## Key Design Decisions

### 1. **No Intermediate Storage**
- **Reason**: Simplifies architecture, reduces costs
- **Trade-off**: Documents are processed in-memory
- **Mitigation**: Process in batches, implement error recovery

### 2. **Full Sync Only (No Incremental)**
- **Reason**: Simpler logic, ensures consistency
- **Trade-off**: Longer sync times, higher API usage
- **Mitigation**: Run during off-hours, optimize processing

### 3. **Clear Index Before Sync**
- **Reason**: Ensures no stale documents
- **Trade-off**: Index is empty during sync
- **Mitigation**: Run during low-traffic periods

### 4. **Direct to Azure Search**
- **Reason**: Eliminates staging layer
- **Trade-off**: Need reliable error handling
- **Mitigation**: Batch uploads with retry logic

## Performance Characteristics

### Expected Metrics
- **Processing Speed**: ~50-100 documents/minute
- **Total Sync Time**: 1-3 hours (for 5,000 documents)
- **Memory Usage**: ~500MB-2GB (depending on batch size)
- **API Calls**: 
  - Confluence: ~1 call per page
  - Google Drive: ~1 call per file + 1 per folder
  - OpenAI: ~1 call per 16 chunks
  - Azure Search: ~1 call per 1000 documents

### Scaling Considerations
- Parallel processing (5 workers by default)
- Batch operations for efficiency
- Rate limiting with exponential backoff
- Configurable chunk sizes

## Error Handling Strategy

```
┌─────────────────────────────────────┐
│         Error Categories             │
├─────────────────────────────────────┤
│ 1. Transient Errors                  │
│    - Network timeouts               │
│    - Rate limits                    │
│    → Retry with exponential backoff │
│                                      │
│ 2. Document-Level Errors            │
│    - Parsing failures               │
│    - Unsupported formats            │
│    → Log, skip, continue            │
│                                      │
│ 3. Fatal Errors                      │
│    - Invalid credentials            │
│    - Service unavailable            │
│    → Stop sync, alert, rollback     │
└─────────────────────────────────────┘
```

## Monitoring & Observability

### Logs
- Start/end of sync with timestamps
- Document processing progress
- Success/failure counts
- Error details with stack traces

### Metrics (Future)
- Sync duration
- Documents processed per minute
- Error rates by source
- Index size growth

## Future Enhancements (Not in Initial Phase)

1. **Incremental Sync**
   - Track last modified timestamps
   - Only process changed documents
   - Significantly faster sync times

2. **Webhook Support**
   - Real-time updates from Confluence
   - Google Drive change notifications
   - Near-instant indexing

3. **Partial Sync**
   - Sync specific spaces/folders on demand
   - Manual re-sync of failed documents

4. **Resume Capability**
   - Checkpoint progress
   - Resume from last successful batch
   - Handle long-running syncs

5. **Azure Blob Storage (Optional)**
   - Store raw documents for reprocessing
   - Enable document preview
   - Backup before index updates

