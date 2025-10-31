"""
Token-aware text chunking with overlap
Uses tiktoken for accurate token counting
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class TextChunker:
    """Chunks text into token-aware segments"""
    
    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 128, strategy: str = "token-aware"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
        self._encoder = None
        self._init_encoder()
    
    def _init_encoder(self):
        """Initialize token encoder"""
        try:
            import tiktoken
            self._encoder = tiktoken.get_encoding("cl100k_base")
            logger.info("Initialized tiktoken encoder")
        except ImportError:
            logger.warning("tiktoken not available, falling back to character-based chunking")
            self._encoder = None
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Chunk text into segments
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
        
        Returns:
            List of chunks with metadata
        """
        if not text or not text.strip():
            return []
        
        if self._encoder and self.strategy == "token-aware":
            chunks = self._token_aware_chunking(text)
        else:
            chunks = self._sentence_based_chunking(text)
        
        # Add metadata
        result = []
        for i, chunk_text in enumerate(chunks):
            chunk = {
                "chunk_id": i,
                "text": chunk_text,
                "char_count": len(chunk_text),
                **(metadata or {})
            }
            result.append(chunk)
        
        return result
    
    def _token_aware_chunking(self, text: str) -> List[str]:
        """Chunk based on token count"""
        tokens = self._encoder.encode(text)
        chunks = []
        
        start = 0
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self._encoder.decode(chunk_tokens)
            chunks.append(chunk_text)
            start = end - self.chunk_overlap
        
        return chunks
    
    def _sentence_based_chunking(self, text: str) -> List[str]:
        """Fallback: chunk based on sentences"""
        import re
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                # Keep overlap
                overlap_sentences = current_chunk[-(self.chunk_overlap // 100):]
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
