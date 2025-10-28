"""Test script to answer 'What is Solara' using the RAG system."""
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from config.settings import settings
from services.embedding_service import EmbeddingService
from services.query_service import QueryService
from services.chat_service import ChatService

def test_solara_question():
    """Answer the question 'What is Solara?'"""
    print("=" * 80)
    print("Testing RAG System with Question: 'What is Solara?'")
    print("=" * 80)
    
    question = "What is Solara?"
    
    # Check configuration
    print("\n1. Checking Configuration:")
    print(f"   Embedding Deployment: {settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
    print(f"   Chat Deployment: {settings.AZURE_OPENAI_CHAT_DEPLOYMENT}")
    print(f"   API Version: {settings.AZURE_OPENAI_API_VERSION}")
    
    # Initialize services
    print("\n2. Initializing Services...")
    
    try:
        embedding_service = EmbeddingService(
            endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            deployment_name=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
        print("   ✓ Embedding service initialized")
        
        query_service = QueryService(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            api_key=settings.AZURE_SEARCH_API_KEY,
            index_name=settings.AZURE_SEARCH_INDEX_NAME
        )
        print("   ✓ Query service initialized")
        
        chat_service = ChatService(
            endpoint=settings.AZURE_OPENAI_CHAT_ENDPOINT,
            api_key=settings.AZURE_OPENAI_CHAT_API_KEY,
            deployment_name=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
        print("   ✓ Chat service initialized")
        
    except Exception as e:
        print(f"   ✗ Failed to initialize services: {e}")
        return False
    
    # Step 1: Generate question embedding
    print(f"\n3. Generating Embedding for Question: '{question}'")
    try:
        query_embeddings = embedding_service.generate_embeddings([question])
        query_vector = query_embeddings[0]
        print(f"   ✓ Generated embedding vector ({len(query_vector)} dimensions)")
    except Exception as e:
        print(f"   ✗ Failed to generate embedding: {e}")
        return False
    
    # Step 2: Search for relevant chunks
    print("\n4. Searching for Relevant Content...")
    try:
        chunks = query_service.vector_search(
            query_vector=query_vector,
            top_k=5
        )
        print(f"   ✓ Found {len(chunks)} relevant chunks")
        
        if chunks:
            print("\n   Retrieved Chunks:")
            for i, chunk in enumerate(chunks, 1):
                print(f"   {i}. {chunk['title']} (Score: {chunk['score']:.4f})")
                print(f"      Content preview: {chunk['content'][:100]}...")
        else:
            print("   ⚠ No relevant chunks found!")
            return False
            
    except Exception as e:
        print(f"   ✗ Failed to search: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Generate answer using chat service
    print("\n5. Generating Answer with Chat Service...")
    try:
        result = chat_service.generate_answer(
            question=question,
            context_chunks=chunks,
            temperature=0.7,
            max_tokens=500
        )
        
        print("   ✓ Answer generated successfully!")
        
        # Display the answer
        print("\n" + "=" * 80)
        print("QUESTION:")
        print("=" * 80)
        print(question)
        
        print("\n" + "=" * 80)
        print("ANSWER:")
        print("=" * 80)
        print(result["answer"])
        
        print("\n" + "=" * 80)
        print("METADATA:")
        print("=" * 80)
        print(f"Model: {result['model']}")
        print(f"Tokens Used: {result['usage']['total_tokens']}")
        print(f"  - Prompt: {result['usage']['prompt_tokens']}")
        print(f"  - Completion: {result['usage']['completion_tokens']}")
        
        print("\n" + "=" * 80)
        print(f"SOURCES ({len(result['sources'])}):")
        print("=" * 80)
        for i, source in enumerate(result['sources'], 1):
            print(f"{i}. {source['title']}")
            print(f"   Author: {source['author']}")
            print(f"   URL: {source['url']}")
        
        print("\n" + "=" * 80)
        print("✓ SUCCESS!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"   ✗ Failed to generate answer: {e}")
        print("\nError Details:")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 80)
        print("TROUBLESHOOTING:")
        print("=" * 80)
        print("If you see a 'DeploymentNotFound' error, you need to:")
        print("1. Go to Azure OpenAI Studio (https://oai.azure.com/)")
        print("2. Click on 'Deployments'")
        print("3. Find or create a chat model deployment (e.g., gpt-4o, gpt-35-turbo)")
        print("4. Add to your .env file:")
        print(f"   AZURE_OPENAI_CHAT_DEPLOYMENT=<your-deployment-name>")
        print("\nCurrent setting: AZURE_OPENAI_CHAT_DEPLOYMENT=" + settings.AZURE_OPENAI_CHAT_DEPLOYMENT)
        return False


if __name__ == "__main__":
    success = test_solara_question()
    sys.exit(0 if success else 1)

