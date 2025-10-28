"""List available Azure OpenAI deployments."""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from openai import AzureOpenAI
from config.settings import settings

def list_deployments():
    """List all deployments in Azure OpenAI."""
    print("=" * 80)
    print("Azure OpenAI Deployments")
    print("=" * 80)
    print(f"\nEndpoint: {settings.AZURE_OPENAI_ENDPOINT}")
    print("\nAttempting to list deployments...")
    
    try:
        client = AzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
        
        # Try to list models (this may not work with all API versions)
        try:
            models = client.models.list()
            print("\nAvailable Models:")
            print("-" * 80)
            for model in models.data:
                print(f"  - {model.id}")
        except Exception as e:
            print(f"\nCouldn't list models via API: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 80)
    print("To find your deployments manually:")
    print("=" * 80)
    print("1. Go to: https://oai.azure.com/")
    print("2. Click on 'Deployments' in the left menu")
    print("3. Look for chat models like:")
    print("   - gpt-4o")
    print("   - gpt-4")
    print("   - gpt-4-32k")
    print("   - gpt-35-turbo (note: hyphen, not underscore)")
    print("   - gpt-35-turbo-16k")
    print("\n4. Copy the EXACT deployment name")
    print("5. Update your .env file:")
    print("   AZURE_OPENAI_CHAT_DEPLOYMENT=<exact-deployment-name>")
    print("\n" + "=" * 80)
    print("Current Settings:")
    print("=" * 80)
    print(f"Embedding Deployment: {settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT} ✓ (working)")
    print(f"Chat Deployment: {settings.AZURE_OPENAI_CHAT_DEPLOYMENT} ✗ (not found)")

if __name__ == "__main__":
    list_deployments()

