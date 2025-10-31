"""
Simple unit test for text chunker (no external dependencies)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_basic_import():
    """Test that the module can be imported"""
    try:
        from src.core.ingestion.text_chunker import TextChunker
        chunker = TextChunker(chunk_size=100, chunk_overlap=20, strategy="sentence")
        assert chunker.chunk_size == 100
        assert chunker.chunk_overlap == 20
        print("✓ TextChunker import and initialization successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_basic_chunking():
    """Test basic text chunking without tiktoken"""
    try:
        from src.core.ingestion.text_chunker import TextChunker
        chunker = TextChunker(strategy="sentence")
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = chunker.chunk_text(text)
        assert len(chunks) > 0
        assert all("text" in c for c in chunks)
        print(f"✓ Basic chunking successful: {len(chunks)} chunks created")
        return True
    except Exception as e:
        print(f"✗ Chunking failed: {e}")
        return False


def test_embedder_import():
    """Test that embedder can be imported"""
    try:
        from src.core.ingestion.embedder import Embedder
        print("✓ Embedder import successful")
        return True
    except Exception as e:
        print(f"✗ Embedder import failed: {e}")
        return False


def test_retriever_imports():
    """Test retriever imports"""
    try:
        from src.core.retrieval.dense_retriever import DenseRetriever
        from src.core.retrieval.sparse_retriever import SparseRetriever
        from src.core.retrieval.hybrid import HybridRetriever
        print("✓ All retriever imports successful")
        return True
    except Exception as e:
        print(f"✗ Retriever import failed: {e}")
        return False


if __name__ == "__main__":
    print("Running basic smoke tests...\n")
    
    results = []
    results.append(("Import TextChunker", test_basic_import()))
    results.append(("Basic Chunking", test_basic_chunking()))
    results.append(("Import Embedder", test_embedder_import()))
    results.append(("Import Retrievers", test_retriever_imports()))
    
    print("\n" + "="*50)
    print("RESULTS:")
    print("="*50)
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
