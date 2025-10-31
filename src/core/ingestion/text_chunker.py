"""
Token-aware text chunking with overlap
Uses tiktoken for accurate token counting

═══════════════════════════════════════════════════════════════════════════
Copyright © 2025 Samay Mehar. All Rights Reserved.

PROPRIETARY SOFTWARE - PATENT PENDING

Author: Samay Mehar
Created: October 31 - November 1, 2025
Project: VectorMind (Modality RAG System)

This file implements semantic text chunking with boundary detection,
created entirely from scratch (0 to 100) by Samay Mehar.

Unauthorized use is strictly prohibited and may result in legal action.
═══════════════════════════════════════════════════════════════════════════
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class TextChunker:
    """Chunks text into token-aware segments"""
    
    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 128, strategy: str = "token-aware"):
        # Validate chunk_size
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        
        # Validate chunk_overlap
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be non-negative, got {chunk_overlap}")
        
        # Validate overlap is less than chunk_size
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})")
        
        # Validate overlap is less than chunk_size
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})")
        
        # Validate strategy
        valid_strategies = ["token-aware", "sentence", "paragraph", "fixed"]
        if strategy not in valid_strategies:
            raise ValueError(f"Invalid strategy '{strategy}'. Must be one of {valid_strategies}")
        
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
        # Validate input type
        if text is None:
            raise TypeError("text cannot be None")
        if not isinstance(text, str):
            raise TypeError(f"text must be a string, got {type(text).__name__}")
            
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
                "metadata": metadata or {}
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
        """Fallback: chunk based on character count with overlap"""
        import re
        
        # Try to split into sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # If no sentences detected (no punctuation), split by character with word boundaries
        if len(sentences) == 1:
            if not text.strip():
                return [text]
            
            chunks = []
            start = 0
            
            while start < len(text):
                # Get a chunk of the specified size
                end = min(start + self.chunk_size, len(text))
                
                # If not at the end, try to break at a word boundary
                if end < len(text):
                    # Look backwards for a space
                    original_end = end
                    while end > start and text[end] not in (' ', '\n', '\t'):
                        end -= 1
                    # If we couldn't find a space, just use the chunk_size
                    if end == start:
                        end = original_end
                
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                
                # Move start forward, accounting for overlap
                # Use the position after stripping to determine next start
                next_start = start + self.chunk_size - self.chunk_overlap
                if next_start <= start:  # Prevent infinite loop
                    next_start = start + 1
                start = next_start
                
            return chunks if chunks else [text]
        
        # Process sentences
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                # Keep last few characters for overlap
                if self.chunk_overlap > 0:
                    overlap_text = ' '.join(current_chunk)
                    if len(overlap_text) > self.chunk_overlap:
                        overlap_text = overlap_text[-self.chunk_overlap:]
                        # Start new chunk with overlap
                        current_chunk = [sentence]
                        current_length = len(overlap_text) + sentence_length
                    else:
                        current_chunk = [sentence]
                        current_length = sentence_length
                else:
                    current_chunk = [sentence]
                    current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length + 1  # +1 for space
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks if chunks else [text]
