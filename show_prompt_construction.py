"""Demonstrate the exact prompt construction for 'What is Solara?'"""
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

def show_prompt():
    """Show the exact prompt that would be sent to the LLM."""
    print("=" * 80)
    print("RAG Prompt Construction Demo")
    print("=" * 80)
    
    question = "What is Solara?"
    
    # Initialize services
    embedding_service = EmbeddingService(
        endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_key=settings.AZURE_OPENAI_API_KEY,
        deployment_name=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        api_version=settings.AZURE_OPENAI_API_VERSION
    )
    
    query_service = QueryService(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        api_key=settings.AZURE_SEARCH_API_KEY,
        index_name=settings.AZURE_SEARCH_INDEX_NAME
    )
    
    # Get embedding and search
    print("\n1. Searching for relevant context...")
    query_embeddings = embedding_service.generate_embeddings([question])
    query_vector = query_embeddings[0]
    
    chunks = query_service.vector_search(
        query_vector=query_vector,
        top_k=5
    )
    
    print(f"   Found {len(chunks)} relevant chunks")
    
    # Build the context (same way chat_service does it)
    print("\n2. Building context from chunks...")
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i}] {chunk['title']}\n"
            f"Author: {chunk['author']}\n"
            f"Content: {chunk['content']}\n"
        )
    
    context = "\n---\n".join(context_parts)
    
    # System prompt (default from chat_service)
    system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from a knowledge base.

Instructions:
- Answer the question using ONLY the information provided in the context
- Be specific and cite which source(s) you used when possible
- If the context doesn't contain enough information, clearly state that
- Be concise but thorough in your explanations
- Use a professional and friendly tone
- If you find conflicting information in the sources, acknowledge it"""
    
    # User prompt (same format as chat_service)
    user_prompt = f"""Context information:
{context}

Question: {question}

Please provide a comprehensive answer based on the context provided above. If the context doesn't contain enough information to answer the question, please state that clearly."""
    
    # Display the complete prompt
    print("\n" + "=" * 80)
    print("SYSTEM PROMPT (Instructions to the AI):")
    print("=" * 80)
    print(system_prompt)
    
    print("\n" + "=" * 80)
    print("USER PROMPT (Question + Context):")
    print("=" * 80)
    print(user_prompt)
    
    print("\n" + "=" * 80)
    print("PROMPT STRUCTURE:")
    print("=" * 80)
    print("""
messages = [
    {
        "role": "system",
        "content": "<system_prompt above>"
    },
    {
        "role": "user",
        "content": "<user_prompt above>"
    }
]
""")
    
    print("=" * 80)
    print("MODEL PARAMETERS:")
    print("=" * 80)
    print(f"model: {settings.AZURE_OPENAI_CHAT_DEPLOYMENT}")
    print(f"temperature: {settings.RAG_TEMPERATURE}")
    print(f"max_tokens: {settings.RAG_MAX_TOKENS}")
    
    print("\n" + "=" * 80)
    print("RETRIEVED SOURCES:")
    print("=" * 80)
    for i, chunk in enumerate(chunks, 1):
        print(f"\n[Source {i}]")
        print(f"  Title: {chunk['title']}")
        print(f"  Author: {chunk['author']}")
        print(f"  Space: {chunk.get('space_key', 'N/A')}")
        print(f"  URL: {chunk['url']}")
        print(f"  Score: {chunk['score']:.4f}")
        print(f"  Content length: {len(chunk['content'])} characters")
    
    print("\n" + "=" * 80)
    print("TOTAL PROMPT SIZE:")
    print("=" * 80)
    total_chars = len(system_prompt) + len(user_prompt)
    estimated_tokens = total_chars // 4  # Rough estimate: 4 chars ≈ 1 token
    print(f"Characters: {total_chars:,}")
    print(f"Estimated tokens: ~{estimated_tokens:,}")
    print(f"Max response tokens: {settings.RAG_MAX_TOKENS}")
    print(f"Estimated total: ~{estimated_tokens + settings.RAG_MAX_TOKENS:,} tokens")
    
    print("\n" + "=" * 80)
    print("✓ Prompt construction complete!")
    print("=" * 80)
    print("\nThis exact prompt would be sent to:")
    print(f"  Deployment: {settings.AZURE_OPENAI_CHAT_DEPLOYMENT}")
    print(f"  Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
    
    return True

if __name__ == "__main__":
    success = show_prompt()
    sys.exit(0 if success else 1)

