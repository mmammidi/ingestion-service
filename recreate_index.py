"""Script to delete and recreate the Azure Search index with space_key field."""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from config.settings import settings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient

def recreate_index():
    """Delete the existing index so it can be recreated with space_key field."""
    print("=" * 80)
    print("Recreating Azure Search Index with space_key Field")
    print("=" * 80)
    
    credential = AzureKeyCredential(settings.AZURE_SEARCH_API_KEY)
    index_client = SearchIndexClient(settings.AZURE_SEARCH_ENDPOINT, credential)
    
    print(f"\nIndex name: {settings.AZURE_SEARCH_INDEX_NAME}")
    
    # Check if index exists
    try:
        index = index_client.get_index(settings.AZURE_SEARCH_INDEX_NAME)
        print(f"Found existing index with {len(index.fields)} fields")
        
        # Delete it
        print("\nDeleting old index...")
        index_client.delete_index(settings.AZURE_SEARCH_INDEX_NAME)
        print("[OK] Index deleted successfully")
        
    except Exception as e:
        if "not found" in str(e).lower():
            print("Index does not exist yet (this is fine)")
        else:
            print(f"[ERROR] {e}")
            return False
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("=" * 80)
    print("Run the sync to recreate the index with the space_key field:")
    print("  python main.py sync")
    print("\nThis will:")
    print("  1. Create new index with space_key field")
    print("  2. Fetch documents from Confluence")
    print("  3. Process and chunk them")
    print("  4. Generate embeddings")
    print("  5. Upload to Azure Search")
    
    return True

if __name__ == "__main__":
    success = recreate_index()
    sys.exit(0 if success else 1)

