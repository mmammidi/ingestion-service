"""Configuration management from environment variables."""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings from environment variables."""
    
    # Confluence Settings
    CONFLUENCE_URL: str = os.getenv("CONFLUENCE_URL", "")
    CONFLUENCE_USERNAME: str = os.getenv("CONFLUENCE_USERNAME", "")
    CONFLUENCE_API_TOKEN: str = os.getenv("CONFLUENCE_API_TOKEN", "")
    CONFLUENCE_SPACES: List[str] = os.getenv("CONFLUENCE_SPACES", "").split(",")
    
    # Azure OpenAI Settings (Embedding)
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = os.getenv(
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"
    )
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
    
    # Azure OpenAI Settings (Chat) - Can be separate resource
    AZURE_OPENAI_CHAT_ENDPOINT: str = os.getenv(
        "AZURE_OPENAI_CHAT_ENDPOINT", 
        os.getenv("AZURE_OPENAI_ENDPOINT", "")  # Fallback to same endpoint
    )
    AZURE_OPENAI_CHAT_API_KEY: str = os.getenv(
        "AZURE_OPENAI_CHAT_API_KEY",
        os.getenv("AZURE_OPENAI_API_KEY", "")  # Fallback to same key
    )
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = os.getenv(
        "AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-35-turbo"
    )
    
    # RAG Settings
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))  # Number of chunks to retrieve
    RAG_TEMPERATURE: float = float(os.getenv("RAG_TEMPERATURE", "0.7"))
    RAG_MAX_TOKENS: int = int(os.getenv("RAG_MAX_TOKENS", "1000"))
    
    # Azure Search Settings
    AZURE_SEARCH_ENDPOINT: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    AZURE_SEARCH_API_KEY: str = os.getenv("AZURE_SEARCH_API_KEY", "")
    AZURE_SEARCH_INDEX_NAME: str = os.getenv(
        "AZURE_SEARCH_INDEX_NAME", "knowledge-base-index"
    )
    
    # Processing Settings
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "16"))
    INDEXING_BATCH_SIZE: int = int(os.getenv("INDEXING_BATCH_SIZE", "1000"))
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "5"))
    
    # Scheduler Settings
    SYNC_CRON: str = os.getenv("SYNC_CRON", "0 2 * * *")  # Daily at 2 AM
    SYNC_TIMEZONE: str = os.getenv("SYNC_TIMEZONE", "UTC")
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings."""
        required_fields = [
            ("CONFLUENCE_URL", cls.CONFLUENCE_URL),
            ("CONFLUENCE_USERNAME", cls.CONFLUENCE_USERNAME),
            ("CONFLUENCE_API_TOKEN", cls.CONFLUENCE_API_TOKEN),
            ("AZURE_OPENAI_ENDPOINT", cls.AZURE_OPENAI_ENDPOINT),
            ("AZURE_OPENAI_API_KEY", cls.AZURE_OPENAI_API_KEY),
            ("AZURE_SEARCH_ENDPOINT", cls.AZURE_SEARCH_ENDPOINT),
            ("AZURE_SEARCH_API_KEY", cls.AZURE_SEARCH_API_KEY),
        ]
        
        missing = [name for name, value in required_fields if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Clean up spaces list
        cls.CONFLUENCE_SPACES = [s.strip() for s in cls.CONFLUENCE_SPACES if s.strip()]
        if not cls.CONFLUENCE_SPACES:
            raise ValueError("CONFLUENCE_SPACES must contain at least one space key")


# Create settings instance
settings = Settings()

