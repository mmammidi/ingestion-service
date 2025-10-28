"""Test script to validate Confluence connector."""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from config.settings import settings
from connectors.confluence_connector import ConfluenceConnector
from utils.logger import setup_logger

# Set up logging
setup_logger(__name__, "INFO")

def test_confluence_connection():
    """Test Confluence connector functionality."""
    print("=" * 80)
    print("Testing Confluence Connection")
    print("=" * 80)
    
    # Validate configuration
    try:
        print("\n1. Validating configuration...")
        settings.validate()
        print("   [OK] Configuration validated")
        print(f"   - Confluence URL: {settings.CONFLUENCE_URL}")
        print(f"   - Username: {settings.CONFLUENCE_USERNAME}")
        print(f"   - Spaces: {', '.join(settings.CONFLUENCE_SPACES)}")
    except ValueError as e:
        print(f"   [ERROR] Configuration error: {e}")
        print("\nPlease update your .env file with valid Confluence credentials.")
        return False
    
    # Initialize connector
    print("\n2. Initializing Confluence connector...")
    try:
        connector = ConfluenceConnector(
            base_url=settings.CONFLUENCE_URL,
            username=settings.CONFLUENCE_USERNAME,
            api_token=settings.CONFLUENCE_API_TOKEN,
            space_keys=settings.CONFLUENCE_SPACES
        )
        print("   [OK] Connector initialized")
    except Exception as e:
        print(f"   [ERROR] Failed to initialize: {e}")
        return False
    
    # Test connection
    print("\n3. Testing connection to Confluence...")
    try:
        connector.connect()
        print("   [OK] Successfully connected to Confluence")
    except Exception as e:
        print(f"   [ERROR] Connection failed: {e}")
        print("\nPossible issues:")
        print("   - Check your CONFLUENCE_URL is correct")
        print("   - Verify CONFLUENCE_API_TOKEN is valid")
        print("   - Ensure CONFLUENCE_USERNAME is your email address")
        return False
    
    # Fetch documents
    print("\n4. Fetching documents from Confluence spaces...")
    try:
        documents = connector.fetch_all_documents()
        print(f"   [OK] Successfully fetched {len(documents)} documents")
        
        if documents:
            print("\n" + "=" * 80)
            print("Sample Documents Retrieved:")
            print("=" * 80)
            
            # Show first 5 documents
            for i, doc in enumerate(documents[:5], 1):
                print(f"\nDocument {i}:")
                print(f"   ID: {doc.id}")
                print(f"   Title: {doc.title}")
                print(f"   URL: {doc.url}")
                print(f"   Author: {doc.author}")
                print(f"   Space: {doc.metadata.get('space_key')}")
                print(f"   Created: {doc.created_date}")
                print(f"   Modified: {doc.modified_date}")
                print(f"   Tags: {', '.join(doc.tags) if doc.tags else 'None'}")
                print(f"   Content length: {len(doc.content)} characters")
                
                # Show content preview
                content_preview = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content
                print(f"   Content preview:")
                print(f"   {content_preview}")
            
            if len(documents) > 5:
                print(f"\n... and {len(documents) - 5} more documents")
            
            # Statistics
            print("\n" + "=" * 80)
            print("Statistics:")
            print("=" * 80)
            
            # Documents per space
            space_counts = {}
            for doc in documents:
                space = doc.metadata.get('space_key', 'Unknown')
                space_counts[space] = space_counts.get(space, 0) + 1
            
            print("\nDocuments per space:")
            for space, count in space_counts.items():
                print(f"   {space}: {count} documents")
            
            # Average content length
            avg_length = sum(len(doc.content) for doc in documents) / len(documents)
            print(f"\nAverage content length: {avg_length:.0f} characters")
            
            # Documents with tags
            docs_with_tags = sum(1 for doc in documents if doc.tags)
            print(f"Documents with tags: {docs_with_tags}/{len(documents)}")
            
        else:
            print("\n[WARNING] No documents found in the specified spaces.")
            print("   Possible reasons:")
            print("   - Spaces are empty")
            print("   - Space keys are incorrect (case-sensitive)")
            print("   - You don't have access to these spaces")
        
        print("\n" + "=" * 80)
        print("[SUCCESS] TEST PASSED - Confluence connector is working!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"   [ERROR] Failed to fetch documents: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_confluence_connection()
    sys.exit(0 if success else 1)

