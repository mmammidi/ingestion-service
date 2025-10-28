"""Document chunking utilities."""
import re
from typing import List
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentChunker:
    """Smart document chunking with overlap."""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target chunk size in tokens (approximate)
            chunk_overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Chunk text into segments with overlap.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Approximate tokens by splitting on whitespace
        # Real tokenization would use tiktoken, but this is a good approximation
        words = text.split()
        
        if len(words) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Ensure we make progress
            if start <= len(words) - self.chunk_size:
                continue
            elif start < len(words):
                # Add remaining words as final chunk
                chunk_words = words[start:]
                if chunk_words:
                    chunk_text = ' '.join(chunk_words)
                    chunks.append(chunk_text)
                break
            else:
                break
        
        logger.debug(f"Chunked text into {len(chunks)} segments")
        return chunks
    
    def chunk_by_sentences(self, text: str) -> List[str]:
        """
        Chunk text by sentences, respecting chunk size.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        # Split into sentences (simple regex)
        sentence_pattern = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_pattern, text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence.split())
            
            if current_size + sentence_size <= self.chunk_size:
                current_chunk.append(sentence)
                current_size += sentence_size
            else:
                # Save current chunk
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                
                # Start new chunk
                if sentence_size <= self.chunk_size:
                    # Add overlap from previous chunk if possible
                    overlap_words = []
                    if chunks:
                        prev_words = chunks[-1].split()
                        overlap_words = prev_words[-self.chunk_overlap:]
                    
                    current_chunk = [' '.join(overlap_words), sentence] if overlap_words else [sentence]
                    current_size = len(' '.join(current_chunk).split())
                else:
                    # Sentence is too long, split it
                    sub_chunks = self.chunk_text(sentence)
                    chunks.extend(sub_chunks)
                    current_chunk = []
                    current_size = 0
        
        # Add final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        logger.debug(f"Chunked text by sentences into {len(chunks)} segments")
        return chunks

