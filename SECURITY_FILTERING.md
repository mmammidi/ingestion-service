# Multi-Division Security with space_key Filtering

## Overview

The `space_key` field enables **division-level security** where different organizational divisions have separate Confluence spaces, and users should only access content from their authorized divisions.

## Architecture

```
Organization
├── Division A (space_key: "DIVA")
│   ├── User 1 → Can only see DIVA content
│   └── User 2 → Can only see DIVA content
├── Division B (space_key: "DIVB")
│   ├── User 3 → Can only see DIVB content
│   └── User 4 → Can only see DIVB content
└── Admin (space_key: "*")
    └── Can see all content
```

## Schema Changes

The `space_key` field has been added as a **top-level filterable field** in Azure Search:

```typescript
{
  id: String (Key)
  content: String (Searchable)
  content_vector: Collection(Single) [1536 dims]
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

## Configuration Example

### Multiple Spaces in .env

```bash
# Multiple divisions
CONFLUENCE_SPACES=ENGINEERING,SALES,MARKETING,HR
```

Or for specific space keys:
```bash
CONFLUENCE_SPACES=~7120200abc,~8230400def,~9340500ghi
```

---

## Security Implementation Patterns

### Pattern 1: Single Division User

Restrict user to only their division's content:

```python
import requests

# User from Engineering division
user_division = "ENGINEERING"

response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "What are our product specifications?",
        "filters": f"space_key eq '{user_division}'"
    }
)
```

### Pattern 2: Multiple Divisions User

User has access to multiple divisions:

```python
# User from both Engineering and Sales
user_divisions = ["ENGINEERING", "SALES"]

filters = " or ".join([f"space_key eq '{div}'" for div in user_divisions])
# Result: "space_key eq 'ENGINEERING' or space_key eq 'SALES'"

response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "What are our quarterly goals?",
        "filters": filters
    }
)
```

### Pattern 3: Admin Access (All Divisions)

Admin can access all content (no filter):

```python
# Admin user - no filter
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "Company-wide policies?",
        # No filters = access all divisions
    }
)
```

### Pattern 4: Combine with Other Filters

Space key + other security criteria:

```python
# Only Engineering docs modified in last 30 days
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "Recent updates?",
        "filters": "space_key eq 'ENGINEERING' and modified_date ge '2025-10-01'"
    }
)

# Only HR docs by specific author
response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "What are the policies?",
        "filters": "space_key eq 'HR' and author eq 'Jane Smith'"
    }
)
```

---

## Flask API Integration

### Option A: Pass space_key in Request

Client sends authorized divisions:

```python
# Client code
user_permissions = get_user_divisions(user_id)  # ["ENGINEERING", "SALES"]

response = requests.post(
    "http://localhost:5000/api/ask",
    json={
        "question": "What projects are we working on?",
        "filters": f"space_key eq '{user_permissions[0]}'"
    }
)
```

### Option B: Server-Side Enforcement

Add authentication and enforce on server:

```python
# api.py enhancement
from flask import request, jsonify
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user from token/session
        user = get_current_user(request)
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        
        # Get user's authorized divisions
        authorized_divisions = get_user_divisions(user.id)
        
        # Inject into request context
        request.user_divisions = authorized_divisions
        return f(*args, **kwargs)
    return decorated_function

@app.route("/api/ask", methods=["POST"])
@require_auth
def ask_question():
    data = request.get_json()
    question = data["question"]
    
    # Build security filter from user's divisions
    user_divisions = request.user_divisions
    division_filter = " or ".join([f"space_key eq '{div}'" for div in user_divisions])
    
    # Combine with any user-provided filters
    user_filter = data.get("filters", "")
    if user_filter:
        filters = f"({division_filter}) and ({user_filter})"
    else:
        filters = division_filter
    
    result = rag_service.answer_question(
        question=question,
        filters=filters,
        use_hybrid_search=data.get("use_hybrid_search", True)
    )
    
    return jsonify(result), 200
```

---

## Security Best Practices

### 1. Never Trust Client Input

Always validate and enforce security server-side:

```python
def validate_space_access(user, requested_space_key):
    """Verify user has access to requested space."""
    allowed_spaces = get_user_divisions(user.id)
    
    if requested_space_key not in allowed_spaces:
        raise PermissionError(f"User does not have access to space: {requested_space_key}")
    
    return True
```

### 2. Audit Trail

Log all access attempts:

```python
def log_access(user_id, space_key, question):
    """Log security-sensitive access."""
    logger.info(
        f"Access Log: user={user_id}, space={space_key}, "
        f"question='{question[:50]}...', timestamp={datetime.now()}"
    )
```

### 3. Fail Closed

If divisions cannot be determined, deny access:

```python
def get_user_divisions(user_id):
    """Get user's authorized divisions."""
    divisions = query_database(user_id)
    
    if not divisions:
        # Fail closed - no access if divisions unknown
        raise PermissionError("User divisions not configured")
    
    return divisions
```

### 4. Test Security Boundaries

```python
# Test: User from SALES tries to access ENGINEERING
response = requests.post(
    "http://localhost:5000/api/ask",
    headers={"Authorization": "Bearer sales_user_token"},
    json={
        "question": "Engineering specs?",
        "filters": "space_key eq 'ENGINEERING'"  # Should be blocked!
    }
)

assert response.status_code == 403  # Forbidden
```

---

## Database Schema for User Permissions

### Users Table
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    username VARCHAR(100),
    email VARCHAR(255),
    role VARCHAR(50)  -- 'admin', 'user', etc.
);
```

### Division Access Table
```sql
CREATE TABLE user_division_access (
    user_id INT,
    space_key VARCHAR(100),
    granted_date TIMESTAMP,
    granted_by INT,
    PRIMARY KEY (user_id, space_key),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Query User Divisions
```python
def get_user_divisions(user_id):
    """Get all space_keys user has access to."""
    query = """
        SELECT space_key 
        FROM user_division_access 
        WHERE user_id = %s
    """
    result = db.execute(query, (user_id,))
    return [row['space_key'] for row in result]
```

---

## Example: Complete Secure RAG Client

```python
import requests
from typing import List

class SecureRAGClient:
    """RAG client with division-level security."""
    
    def __init__(self, base_url: str, user_token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {user_token}"}
    
    def get_user_divisions(self) -> List[str]:
        """Get user's authorized divisions from backend."""
        response = requests.get(
            f"{self.base_url}/api/user/divisions",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["divisions"]
    
    def ask_question(self, question: str, additional_filters: str = None):
        """Ask question with automatic security filtering."""
        # Get user's divisions
        divisions = self.get_user_divisions()
        
        if not divisions:
            raise PermissionError("No divisions authorized for user")
        
        # Build division filter
        division_filter = " or ".join([f"space_key eq '{d}'" for d in divisions])
        
        # Combine with additional filters
        if additional_filters:
            filters = f"({division_filter}) and ({additional_filters})"
        else:
            filters = division_filter
        
        # Make request
        response = requests.post(
            f"{self.base_url}/api/ask",
            headers=self.headers,
            json={
                "question": question,
                "filters": filters
            }
        )
        response.raise_for_status()
        return response.json()

# Usage
client = SecureRAGClient("http://localhost:5000", user_token="abc123")

# Automatically filters to user's authorized divisions
result = client.ask_question("What are our current projects?")
print(result["answer"])

# With additional filters
result = client.ask_question(
    "Recent updates?",
    additional_filters="modified_date ge '2025-10-01'"
)
```

---

## Testing Security

### Test Script

```python
"""Test division-level security."""

def test_division_security():
    """Verify space_key filtering works correctly."""
    
    # Test 1: Filter by single division
    result = rag_service.answer_question(
        question="Test question",
        filters="space_key eq 'ENGINEERING'"
    )
    
    # Verify all results are from ENGINEERING
    for source in result["sources"]:
        assert source.get("space_key") == "ENGINEERING", \
            f"Found unauthorized space: {source.get('space_key')}"
    
    print("✓ Single division filter works")
    
    # Test 2: Filter by multiple divisions
    result = rag_service.answer_question(
        question="Test question",
        filters="space_key eq 'ENGINEERING' or space_key eq 'SALES'"
    )
    
    # Verify results are only from authorized divisions
    authorized = {"ENGINEERING", "SALES"}
    for source in result["sources"]:
        assert source.get("space_key") in authorized, \
            f"Found unauthorized space: {source.get('space_key')}"
    
    print("✓ Multiple division filter works")
    
    # Test 3: Invalid division returns no results
    result = rag_service.answer_question(
        question="Test question",
        filters="space_key eq 'NONEXISTENT'"
    )
    
    assert result["retrieved_chunks"] == 0, \
        "Should return no results for invalid division"
    
    print("✓ Invalid division returns no results")
    
    print("\n✅ All security tests passed!")

if __name__ == "__main__":
    test_division_security()
```

---

## Migration Steps

### Step 1: Re-index with space_key

```bash
# Delete old index (without space_key field)
# The index will be recreated automatically with the new field

# Run full sync to reindex all documents
python main.py sync
```

### Step 2: Verify space_key is Indexed

```python
from services.query_service import QueryService
from config.settings import settings

query_service = QueryService(
    endpoint=settings.AZURE_SEARCH_ENDPOINT,
    api_key=settings.AZURE_SEARCH_API_KEY,
    index_name=settings.AZURE_SEARCH_INDEX_NAME
)

# Test query with space_key filter
results = query_service.vector_search(
    query_vector=[0.1] * 1536,  # Dummy vector
    top_k=5,
    filters="space_key eq 'YOUR_SPACE_KEY'"
)

print(f"Found {len(results)} results")
for result in results:
    print(f"  Space: {result['space_key']}, Title: {result['title']}")
```

### Step 3: Update Application Code

Implement server-side security enforcement as shown in examples above.

### Step 4: Test Thoroughly

- Test with users from different divisions
- Verify cross-division access is blocked
- Test admin users with all-division access
- Verify combined filters work correctly

---

## OData Filter Syntax Reference

### Basic Operators
```
eq  - equals
ne  - not equals
gt  - greater than
ge  - greater than or equal
lt  - less than
le  - less than or equal
```

### Logical Operators
```
and - logical AND
or  - logical OR
not - logical NOT
```

### Examples
```python
# Single space
"space_key eq 'ENGINEERING'"

# Multiple spaces (OR)
"space_key eq 'ENG' or space_key eq 'SALES'"

# Space AND date filter
"space_key eq 'HR' and modified_date ge '2025-01-01'"

# Exclude a space
"space_key ne 'CONFIDENTIAL'"

# Complex filter
"(space_key eq 'ENG' or space_key eq 'SALES') and author eq 'John Doe'"
```

---

## Benefits

✅ **Row-Level Security**: Filter at the data layer  
✅ **Performance**: Filtering happens in Azure Search (fast!)  
✅ **Scalability**: Works with millions of documents  
✅ **Flexibility**: Combine with other filters  
✅ **Compliance**: Enforce organizational data boundaries  
✅ **Audit Ready**: Log all filtered queries  

---

## Next Steps

1. ✅ Add `space_key` field (completed)
2. ⬜ Implement user authentication
3. ⬜ Create user-division mapping database
4. ⬜ Add server-side filter enforcement
5. ⬜ Implement audit logging
6. ⬜ Add admin override capability
7. ⬜ Create security test suite
8. ⬜ Document for end users

