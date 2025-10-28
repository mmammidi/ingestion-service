"""Abstract base connector class."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Document:
    """Represents a document from a data source."""
    
    id: str
    title: str
    content: str
    url: str
    author: str
    source: str
    created_date: str
    modified_date: str
    tags: List[str]
    metadata: Dict[str, Any]


class BaseConnector(ABC):
    """Abstract base class for data source connectors."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the data source."""
        pass
    
    @abstractmethod
    def fetch_all_documents(self) -> List[Document]:
        """
        Fetch all documents from the data source.
        
        Returns:
            List of Document objects
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the name of the data source.
        
        Returns:
            Source name (e.g., "confluence", "google_drive")
        """
        pass

