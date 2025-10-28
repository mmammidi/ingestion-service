# space_key Field Addition - Summary of Changes

## Overview

Added `space_key` as a top-level filterable field to enable **multi-division security** where different organizational divisions can be isolated at the data access level.

---

## Files Modified

### 1. `processors/document_parser.py`

**Added `space_key` to ProcessedChunk dataclass:**
```python
@dataclass
class ProcessedChunk:
    id: str
    content: str
    title: str
    url: str
    author: str
    source: str
    created_date: str
    modified_date: str
    tags: List[str]
    space_key: str  # ← NEW! Confluence space key for security filtering
    metadata: Dict[str, Any]
    chunk_index: int
    total_chunks: int
```

**Extract space_key when creating chunks:**
```python
processed_chunk = ProcessedChunk(
    # ... other fields ...
    space_key=document.metadata.get("space_key", ""),  # ← NEW!
    # ... rest of fields ...
)
```

---

### 2. `services/search_service.py`

**Added to Azure Search index schema:**
```python
SimpleField(
    name="space_key",
    type=SearchFieldDataType.String,
    filterable=True
),
```

**Added to document upload:**
```python
doc = {
    "id": chunk.id,
    "content": chunk.content,
    # ... other fields ...
    "space_key": chunk.space_key,  # ← NEW!
    # ... rest of fields ...
}
```

---

### 3. `services/query_service.py`

**Added to search result selection (both vector_search and hybrid_search):**
```python
select=[
    "id",
    "content",
    "title",
    # ... other fields ...
    "space_key",  # ← NEW!
    # ... rest of fields ...
]
```

**Added to result formatting:**
```python
search_results.append({
    "id": result["id"],
    "content": result["content"],
    # ... other fields ...
    "space_key": result.get("space_key", ""),  # ← NEW!
    # ... rest of fields ...
})
```

---

## New Index Schema

The Azure Search index now has **13 fields** (was 12):

```typescript
{
  id: String (Key, Filterable)
  content: String (Searchable)
  content_vector: Collection(Single) [1536 dims] (Searchable)
  title: String (Searchable, Filterable)
  url: String (Filterable)
  author: String (Searchable, Filterable)
  source: String (Filterable)
  space_key: String (Filterable) ← NEW!
  created_date: String (Filterable, Sortable)
  modified_date: String (Filterable, Sortable)
  tags: Collection(String) (Searchable, Filterable)
  chunk_index: Int32 (Filterable)
  total_chunks: Int32 (Filterable)
}
```

---

## Usage Examples

### Filter by Single Division
```python
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "What are our projects?",
        "filters": "space_key eq 'ENGINEERING'"
    }
)
```

### Filter by Multiple Divisions
```python
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "Company updates?",
        "filters": "space_key eq 'ENG' or space_key eq 'SALES'"
    }
)
```

### Combine with Other Filters
```python
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "Recent HR policies?",
        "filters": "space_key eq 'HR' and modified_date ge '2025-10-01'"
    }
)
```

---

## Migration Required

⚠️ **The Azure Search index needs to be recreated** because we added a new field.

### Steps:

1. **Delete the existing index** (it will be recreated automatically):
   ```bash
   # Index will be deleted and recreated on next sync
   ```

2. **Run full sync** to reindex all documents:
   ```bash
   python main.py sync
   ```

3. **Verify** the new field is present:
   ```python
   # Query with space_key filter to test
   from services.query_service import QueryService
   
   results = query_service.vector_search(
       query_vector=test_vector,
       filters="space_key eq 'YOUR_SPACE_KEY'"
   )
   
   print(results[0]['space_key'])  # Should print the space key
   ```

---

## Benefits

✅ **Division-Level Security**: Enforce access control at the data layer  
✅ **Performance**: Filtering happens in Azure Search (very fast)  
✅ **Scalability**: Works with any number of divisions  
✅ **Flexible**: Combine with other filters (author, date, tags)  
✅ **Compliant**: Meet organizational data separation requirements  
✅ **Auditable**: Track which divisions users access  

---

## Use Cases

### 1. Enterprise with Multiple Business Units
- Engineering division sees only engineering docs
- Sales division sees only sales docs
- Executives see all divisions

### 2. Multi-Tenant SaaS
- Customer A sees only their space
- Customer B sees only their space
- No cross-customer data leakage

### 3. Regulatory Compliance
- Finance team isolated from other teams
- Legal docs restricted to legal department
- Audit trail of all access

### 4. Geographic Divisions
- US office sees US space
- EU office sees EU space
- APAC office sees APAC space

---

## Security Best Practices

1. ✅ **Server-side enforcement**: Never trust client filters
2. ✅ **Fail closed**: Deny access if permissions unclear
3. ✅ **Audit logging**: Log all filtered queries
4. ✅ **User-division mapping**: Store in secure database
5. ✅ **Test boundaries**: Verify cross-division access blocked

See `SECURITY_FILTERING.md` for complete implementation guide.

---

## Testing

```python
# Test that space_key filtering works
def test_space_key_filter():
    result = rag_service.answer_question(
        question="Test",
        filters="space_key eq 'TESTSPACE'"
    )
    
    # Verify all results match filter
    for chunk in result.get("sources", []):
        assert chunk.get("space_key") == "TESTSPACE"
    
    print("✓ space_key filtering works!")
```

---

## Documentation

- **Complete Guide**: `SECURITY_FILTERING.md`
- **API Docs**: `RAG_API_DOCUMENTATION.md` (updated with filter examples)
- **This Summary**: `SPACE_KEY_CHANGES_SUMMARY.md`

---

## Next Steps

To enable full multi-division security:

1. ✅ Add `space_key` field (done)
2. ⬜ Implement authentication (JWT tokens, OAuth, etc.)
3. ⬜ Create user-division mapping database
4. ⬜ Add server-side filter enforcement in `api.py`
5. ⬜ Implement audit logging
6. ⬜ Add admin override for cross-division access
7. ⬜ Create comprehensive security test suite

---

## Questions?

See `SECURITY_FILTERING.md` for:
- Complete implementation examples
- Database schema for user permissions
- OData filter syntax reference
- Testing strategies
- Best practices

