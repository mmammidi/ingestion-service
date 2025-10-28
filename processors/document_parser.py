"""Document parsing and processing."""
from typing import List, Dict, Any
from dataclasses import dataclass
from connectors.base_connector import Document
from processors.text_cleaner import TextCleaner
from processors.chunker import DocumentChunker
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessedChunk:
    """Represents a processed document chunk."""
    
    id: str  # Unique ID: original_doc_id + chunk index
    content: str
    title: str
    url: str
    author: str
    source: str
    created_date: str
    modified_date: str
    tags: List[str]
    space_key: str  # Confluence space key for security filtering
    metadata: Dict[str, Any]
    chunk_index: int
    total_chunks: int


class DocumentParser:
    """Parse and process documents into chunks."""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        """
        Initialize document parser.
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Number of tokens to overlap
        """
        self.text_cleaner = TextCleaner()
        self.chunker = DocumentChunker(chunk_size, chunk_overlap)
    
    def process_document(self, document: Document) -> List[ProcessedChunk]:
        """
        Process a document into chunks.
        
        Args:
            document: Document to process
            
        Returns:
            List of ProcessedChunk objects
        """
        try:
            # Clean the content
            cleaned_content = self.text_cleaner.clean_text(document.content)
            
            if not cleaned_content:
                logger.warning(f"Document {document.id} has no content after cleaning")
                return []
            
            # Chunk the content
            chunks = self.chunker.chunk_by_sentences(cleaned_content)
            
            if not chunks:
                logger.warning(f"Document {document.id} produced no chunks")
                return []
            
            # Create ProcessedChunk objects
            processed_chunks = []
            total_chunks = len(chunks)
            
            for idx, chunk_content in enumerate(chunks):
                processed_chunk = ProcessedChunk(
                    id=f"{document.id}_chunk_{idx}",
                    content=chunk_content,
                    title=document.title,
                    url=document.url,
                    author=document.author,
                    source=document.source,
                    created_date=document.created_date,
                    modified_date=document.modified_date,
                    tags=document.tags,
                    space_key=document.metadata.get("space_key", ""),
                    metadata={
                        **document.metadata,
                        "original_doc_id": document.id
                    },
                    chunk_index=idx,
                    total_chunks=total_chunks
                )
                processed_chunks.append(processed_chunk)
            
            logger.debug(
                f"Processed document {document.id} into {len(processed_chunks)} chunks"
            )
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error processing document {document.id}: {str(e)}")
            return []
    
    def process_documents(self, documents: List[Document]) -> List[ProcessedChunk]:
        """
        Process multiple documents.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of all ProcessedChunk objects
        """
        all_chunks = []
        
        for document in documents:
            chunks = self.process_document(document)
            all_chunks.extend(chunks)
        
        logger.info(
            f"Processed {len(documents)} documents into {len(all_chunks)} chunks"
        )
        return all_chunks

