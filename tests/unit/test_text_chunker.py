"""
Unit tests for text chunker
"""

import pytest
from src.core.ingestion.text_chunker import TextChunker


def test_text_chunker_initialization():
    """Test text chunker initialization"""
    chunker = TextChunker(chunk_size=512, chunk_overlap=64)
    assert chunker.chunk_size == 512
    assert chunker.chunk_overlap == 64


def test_chunk_text_basic(sample_text):
    """Test basic text chunking"""
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_text(sample_text)
    
    assert len(chunks) > 0
    assert all("text" in chunk for chunk in chunks)
    assert all("chunk_id" in chunk for chunk in chunks)


def test_chunk_text_with_metadata(sample_text, sample_metadata):
    """Test chunking with metadata"""
    chunker = TextChunker()
    chunks = chunker.chunk_text(sample_text, metadata=sample_metadata)
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.get("source") == "test"
        assert chunk.get("author") == "test_user"


def test_empty_text():
    """Test chunking empty text"""
    chunker = TextChunker()
    chunks = chunker.chunk_text("")
    assert len(chunks) == 0


def test_sentence_based_chunking():
    """Test fallback sentence-based chunking"""
    chunker = TextChunker(strategy="sentence")
    text = "First sentence. Second sentence. Third sentence."
    chunks = chunker.chunk_text(text)
    
    assert len(chunks) > 0
