"""
Unit tests for embedder
"""

import pytest
from src.core.ingestion.embedder import Embedder


def test_embedder_initialization():
    """Test embedder initialization"""
    embedder = Embedder()
    assert embedder.model is not None
    assert embedder.embedding_dim > 0


def test_embed_single_text():
    """Test embedding a single text"""
    embedder = Embedder()
    text = "This is a test sentence."
    embedding = embedder.embed_single(text)
    
    assert embedding is not None
    assert len(embedding) == embedder.embedding_dim
    assert all(isinstance(x, float) for x in embedding)


def test_embed_multiple_texts():
    """Test embedding multiple texts"""
    embedder = Embedder()
    texts = ["First text.", "Second text.", "Third text."]
    embeddings = embedder.embed_texts(texts)
    
    assert len(embeddings) == len(texts)
    assert all(len(emb) == embedder.embedding_dim for emb in embeddings)


def test_empty_text():
    """Test embedding empty text"""
    embedder = Embedder()
    embedding = embedder.embed_single("")
    
    assert embedding is not None
    assert len(embedding) == embedder.embedding_dim


def test_batch_processing():
    """Test batch processing of texts"""
    embedder = Embedder(batch_size=2)
    texts = ["Text " + str(i) for i in range(10)]
    embeddings = embedder.embed_texts(texts)
    
    assert len(embeddings) == 10
