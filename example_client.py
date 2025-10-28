"""Example client for the RAG API."""
import requests
import json
import sys


class RAGClient:
    """Simple client for interacting with the RAG API."""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """Initialize the client."""
        self.base_url = base_url.rstrip("/")
    
    def health_check(self):
        """Check if API is healthy."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def ask_question(
        self,
        question: str,
        system_prompt: str = None,
        use_hybrid_search: bool = True,
        top_k: int = 5,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Ask a question using RAG.
        
        Args:
            question: The question to ask
            system_prompt: Optional custom system prompt
            use_hybrid_search: Whether to use hybrid search
            top_k: Number of chunks to retrieve
            temperature: Response creativity (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Dictionary with answer and metadata
        """
        payload = {
            "question": question,
            "use_hybrid_search": use_hybrid_search,
            "top_k": top_k,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        response = requests.post(
            f"{self.base_url}/api/ask",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def search_chunks(self, question: str, top_k: int = 5):
        """
        Search for relevant chunks without generating an answer.
        
        Args:
            question: The search query
            top_k: Number of chunks to retrieve
            
        Returns:
            Dictionary with chunks and metadata
        """
        response = requests.post(
            f"{self.base_url}/api/search",
            json={
                "question": question,
                "top_k": top_k
            }
        )
        response.raise_for_status()
        return response.json()
    
    def get_config(self):
        """Get current RAG configuration."""
        response = requests.get(f"{self.base_url}/api/config")
        return response.json()


def main():
    """Example usage."""
    print("=" * 80)
    print("RAG API Client Example")
    print("=" * 80)
    
    # Initialize client
    client = RAGClient("http://localhost:5000")
    
    # Check health
    print("\n1. Health Check:")
    try:
        health = client.health_check()
        print(f"   Status: {health['status']}")
    except Exception as e:
        print(f"   [ERROR] API is not running: {e}")
        print("\n   Please start the API server first:")
        print("   python api.py")
        sys.exit(1)
    
    # Get configuration
    print("\n2. Configuration:")
    config = client.get_config()
    print(f"   Chat Model: {config['chat_model']}")
    print(f"   Embedding Model: {config['embedding_model']}")
    print(f"   Top K: {config['top_k']}")
    print(f"   Temperature: {config['temperature']}")
    
    # Example questions
    questions = [
        "What documents are in the knowledge base?",
        "Tell me about Solara",
        "Who is the author of these documents?"
    ]
    
    print("\n3. Asking Questions:")
    print("=" * 80)
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'=' * 80}")
        print(f"Question {i}: {question}")
        print("=" * 80)
        
        try:
            # Ask question
            result = client.ask_question(
                question=question,
                use_hybrid_search=True,
                top_k=3
            )
            
            # Display answer
            print(f"\n📝 Answer:")
            print("-" * 80)
            print(result["answer"])
            print("-" * 80)
            
            # Display metadata
            print(f"\n📊 Metadata:")
            print(f"   Retrieved chunks: {result['retrieved_chunks']}")
            print(f"   Search type: {result['search_type']}")
            print(f"   Tokens: {result['usage']['total_tokens']}")
            
            # Display sources
            print(f"\n📚 Sources:")
            for j, source in enumerate(result['sources'], 1):
                print(f"   {j}. {source['title']} by {source['author']}")
            
        except Exception as e:
            print(f"   [ERROR] {e}")
    
    # Example: Search without generating answer
    print("\n\n4. Search Example (without answer generation):")
    print("=" * 80)
    
    try:
        search_result = client.search_chunks("Solara", top_k=3)
        print(f"\nFound {search_result['count']} chunks:")
        for i, chunk in enumerate(search_result['chunks'], 1):
            print(f"\n{i}. {chunk['title']} (Score: {chunk['score']:.2f})")
            print(f"   {chunk['content'][:150]}...")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print("\n" + "=" * 80)
    print("Example completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()

