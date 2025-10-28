"""Test script for RAG question answering."""
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
from services.rag_service import RAGService


def test_rag():
    """Test the RAG pipeline."""
    print("=" * 80)
    print("Testing RAG Question Answering Pipeline")
    print("=" * 80)
    
    # Initialize services
    print("\n1. Initializing services...")
    
    try:
        embedding_service = EmbeddingService(
            endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            deployment_name=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
        print("   [OK] Embedding service initialized")
        
        query_service = QueryService(
            endpoint=settings.AZURE_SEARCH_ENDPOINT,
            api_key=settings.AZURE_SEARCH_API_KEY,
            index_name=settings.AZURE_SEARCH_INDEX_NAME
        )
        print("   [OK] Query service initialized")
        
        chat_service = ChatService(
            endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_API_KEY,
            deployment_name=settings.AZURE_OPENAI_CHAT_DEPLOYMENT,
            api_version=settings.AZURE_OPENAI_API_VERSION
        )
        print("   [OK] Chat service initialized")
        
        rag_service = RAGService(
            embedding_service=embedding_service,
            query_service=query_service,
            chat_service=chat_service,
            top_k=settings.RAG_TOP_K,
            temperature=settings.RAG_TEMPERATURE,
            max_tokens=settings.RAG_MAX_TOKENS
        )
        print("   [OK] RAG service initialized")
        
    except Exception as e:
        print(f"   [ERROR] Failed to initialize services: {e}")
        return False
    
    # Test questions
    test_questions = [
        "What is this knowledge base about?",
        "Tell me about Solara",
        "Who are the main people or characters mentioned?"
    ]
    
    print("\n" + "=" * 80)
    print("Testing RAG with Sample Questions")
    print("=" * 80)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 80}")
        print(f"Question {i}: {question}")
        print("=" * 80)
        
        try:
            # Get answer
            result = rag_service.answer_question(
                question=question,
                use_hybrid_search=True
            )
            
            print(f"\n📝 Answer:")
            print("-" * 80)
            print(result["answer"])
            print("-" * 80)
            
            print(f"\n📊 Metadata:")
            print(f"  Retrieved chunks: {result['retrieved_chunks']}")
            print(f"  Search type: {result['search_type']}")
            print(f"  Tokens used: {result['usage']['total_tokens']} "
                  f"(prompt: {result['usage']['prompt_tokens']}, "
                  f"completion: {result['usage']['completion_tokens']})")
            
            print(f"\n📚 Sources ({len(result['sources'])}):")
            for j, source in enumerate(result['sources'], 1):
                print(f"  {j}. {source['title']}")
                print(f"     Author: {source['author']}")
                print(f"     URL: {source['url']}")
            
        except Exception as e:
            print(f"   [ERROR] Failed to answer question: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "=" * 80)
    print("[SUCCESS] RAG pipeline test completed!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_rag()
    sys.exit(0 if success else 1)

