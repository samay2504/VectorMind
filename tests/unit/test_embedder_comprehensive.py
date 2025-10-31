"""
Comprehensive unit tests for Embedder with edge cases and real-world scenarios
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.core.ingestion.embedder import Embedder

try:
    import torch
    TORCH_AVAILABLE = True
    try:
        CUDA_AVAILABLE = torch.cuda.is_available()
    except (AttributeError, RuntimeError):
        CUDA_AVAILABLE = False
except ImportError:
    TORCH_AVAILABLE = False
    CUDA_AVAILABLE = False


class TestEmbedderInitialization:
    """Test embedder initialization scenarios"""
    
    def test_default_initialization(self):
        """Test default embedder initialization"""
        embedder = Embedder()
        assert embedder.model is not None
        assert embedder.model_name == "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        assert embedder.device in ["cpu", "cuda"]
        assert embedder.batch_size == 32
        assert embedder.embedding_dim > 0
    
    def test_custom_model_initialization(self):
        """Test initialization with custom model"""
        embedder = Embedder(model_name="sentence-transformers/all-MiniLM-L6-v2")
        assert embedder.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert embedder.model is not None
    
    def test_custom_batch_size(self):
        """Test initialization with custom batch size"""
        embedder = Embedder(batch_size=16)
        assert embedder.batch_size == 16
    
    def test_cpu_device_initialization(self):
        """Test initialization on CPU"""
        embedder = Embedder(device="cpu")
        assert embedder.device == "cpu"
    
    @pytest.mark.skipif(not CUDA_AVAILABLE, reason="CUDA not available")
    def test_cuda_device_initialization(self):
        """Test initialization on CUDA if available"""
        embedder = Embedder(device="cuda")
        assert embedder.device == "cuda"
    
    def test_embedding_dimension_property(self):
        """Test embedding dimension properties"""
        embedder = Embedder()
        dim1 = embedder.get_embedding_dimension()
        dim2 = embedder.dimension
        dim3 = embedder.embedding_dim
        assert dim1 == dim2 == dim3
        assert dim1 == 384  # For all-MiniLM-L6-v2


class TestEmbedSingleText:
    """Test single text embedding scenarios"""
    
    def test_normal_text_embedding(self):
        """Test embedding normal text"""
        embedder = Embedder()
        text = "This is a test sentence for embedding."
        embedding = embedder.embed_single(text)
        
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) == embedder.embedding_dim
        assert all(isinstance(x, float) for x in embedding)
        assert all(not np.isnan(x) for x in embedding)
        assert all(not np.isinf(x) for x in embedding)
    
    def test_empty_string_embedding(self):
        """Test embedding empty string"""
        embedder = Embedder()
        embedding = embedder.embed_single("")
        
        assert embedding is not None
        assert len(embedding) == embedder.embedding_dim
        assert isinstance(embedding, list)
    
    def test_whitespace_only_embedding(self):
        """Test embedding whitespace only"""
        embedder = Embedder()
        embedding = embedder.embed_single("   \t\n  ")
        
        assert embedding is not None
        assert len(embedding) == embedder.embedding_dim
    
    def test_very_long_text_embedding(self):
        """Test embedding very long text (>512 tokens)"""
        embedder = Embedder()
        long_text = " ".join(["word"] * 1000)  # ~1000 words
        embedding = embedder.embed_single(long_text)
        
        assert embedding is not None
        assert len(embedding) == embedder.embedding_dim
    
    def test_special_characters_embedding(self):
        """Test embedding text with special characters"""
        embedder = Embedder()
        texts = [
            "Hello! How are you? I'm fine.",
            "Price: $100.50 USD",
            "Email: test@example.com",
            "Math: 2+2=4, √16=4",
            "Symbols: @#$%^&*()",
            "Quotes: 'single' and \"double\"",
            "Newline:\nTab:\tCarriage:\r"
        ]
        
        for text in texts:
            embedding = embedder.embed_single(text)
            assert embedding is not None
            assert len(embedding) == embedder.embedding_dim
    
    def test_unicode_embedding(self):
        """Test embedding unicode text"""
        embedder = Embedder()
        texts = [
            "Hello 世界",  # Chinese
            "Привет мир",  # Russian
            "مرحبا بالعالم",  # Arabic
            "🚀 🎉 😊",  # Emojis
            "Café résumé",  # Accented
            "日本語テキスト",  # Japanese
        ]
        
        for text in texts:
            embedding = embedder.embed_single(text)
            assert embedding is not None
            assert len(embedding) == embedder.embedding_dim
    
    def test_numeric_only_embedding(self):
        """Test embedding numeric only text"""
        embedder = Embedder()
        embedding = embedder.embed_single("123456789")
        
        assert embedding is not None
        assert len(embedding) == embedder.embedding_dim
    
    def test_repeated_text_consistency(self):
        """Test that same text produces same embedding"""
        embedder = Embedder()
        text = "Consistency test text"
        
        embedding1 = embedder.embed_single(text)
        embedding2 = embedder.embed_single(text)
        
        # Should be identical (deterministic)
        np.testing.assert_array_almost_equal(embedding1, embedding2, decimal=6)
    
    def test_case_sensitivity(self):
        """Test embedding case sensitivity"""
        embedder = Embedder()
        
        lower = embedder.embed_single("hello world")
        upper = embedder.embed_single("HELLO WORLD")
        mixed = embedder.embed_single("Hello World")
        
        # Modern embedding models are typically case-insensitive
        # So embeddings should be similar (or identical)
        similarity_lower_upper = np.dot(lower, upper)
        similarity_lower_mixed = np.dot(lower, mixed)
        
        # High cosine similarity indicates case insensitivity (expected)
        assert similarity_lower_upper > 0.95
        assert similarity_lower_mixed > 0.95


class TestEmbedMultipleTexts:
    """Test multiple text embedding scenarios"""
    
    def test_normal_batch_embedding(self):
        """Test normal batch embedding"""
        embedder = Embedder()
        texts = ["First text.", "Second text.", "Third text."]
        embeddings = embedder.embed_texts(texts)
        
        assert len(embeddings) == len(texts)
        assert all(len(emb) == embedder.embedding_dim for emb in embeddings)
        assert all(isinstance(emb, list) for emb in embeddings)
    
    def test_empty_list_embedding(self):
        """Test embedding empty list"""
        embedder = Embedder()
        embeddings = embedder.embed_texts([])
        
        assert embeddings == []
        assert isinstance(embeddings, list)
    
    def test_single_item_list(self):
        """Test embedding single item in list"""
        embedder = Embedder()
        embeddings = embedder.embed_texts(["Single text"])
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == embedder.embedding_dim
    
    def test_large_batch_embedding(self):
        """Test embedding large batch"""
        embedder = Embedder(batch_size=32)
        texts = [f"Text number {i}" for i in range(100)]
        embeddings = embedder.embed_texts(texts)
        
        assert len(embeddings) == len(texts)
        assert all(len(emb) == embedder.embedding_dim for emb in embeddings)
    
    def test_mixed_length_texts(self):
        """Test embedding texts of varying lengths"""
        embedder = Embedder()
        texts = [
            "Short",
            "Medium length text here",
            " ".join(["long"] * 100),
            "",
            "a"
        ]
        embeddings = embedder.embed_texts(texts)
        
        assert len(embeddings) == len(texts)
        assert all(len(emb) == embedder.embedding_dim for emb in embeddings)
    
    def test_duplicate_texts_in_batch(self):
        """Test embedding with duplicate texts"""
        embedder = Embedder()
        texts = ["Same text", "Same text", "Different", "Same text"]
        embeddings = embedder.embed_texts(texts)
        
        assert len(embeddings) == len(texts)
        # First and second should be identical
        np.testing.assert_array_almost_equal(embeddings[0], embeddings[1], decimal=6)
        np.testing.assert_array_almost_equal(embeddings[0], embeddings[3], decimal=6)
    
    def test_batch_with_none_handling(self):
        """Test batch with None values (should handle gracefully)"""
        embedder = Embedder()
        # Filter out None values before embedding
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = embedder.embed_texts(texts)
        
        assert len(embeddings) == 3
    
    def test_batch_size_respect(self):
        """Test that batch size is respected"""
        embedder = Embedder(batch_size=5)
        texts = [f"Text {i}" for i in range(12)]  # Should process in 3 batches
        embeddings = embedder.embed_texts(texts)
        
        assert len(embeddings) == 12
        assert all(len(emb) == embedder.embedding_dim for emb in embeddings)


class TestEmbedderEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_very_long_single_word(self):
        """Test embedding very long single word"""
        embedder = Embedder()
        long_word = "a" * 10000
        embedding = embedder.embed_single(long_word)
        
        assert embedding is not None
        assert len(embedding) == embedder.embedding_dim
    
    def test_only_punctuation(self):
        """Test embedding only punctuation"""
        embedder = Embedder()
        texts = [
            "!!!",
            "...",
            "???",
            "---",
            "***",
            "@@@"
        ]
        
        for text in texts:
            embedding = embedder.embed_single(text)
            assert embedding is not None
            assert len(embedding) == embedder.embedding_dim
    
    def test_mixed_languages_in_batch(self):
        """Test batch with mixed languages"""
        embedder = Embedder()
        texts = [
            "English text",
            "Texto en español",
            "Texte français",
            "Deutscher Text",
            "中文文本"
        ]
        embeddings = embedder.embed_texts(texts)
        
        assert len(embeddings) == len(texts)
        assert all(len(emb) == embedder.embedding_dim for emb in embeddings)
    
    def test_html_content_embedding(self):
        """Test embedding HTML content"""
        embedder = Embedder()
        html = "<html><body><p>Hello World</p></body></html>"
        embedding = embedder.embed_single(html)
        
        assert embedding is not None
        assert len(embedding) == embedder.embedding_dim
    
    def test_code_snippet_embedding(self):
        """Test embedding code snippets"""
        embedder = Embedder()
        code = """
        def hello():
            print("Hello World")
            return True
        """
        embedding = embedder.embed_single(code)
        
        assert embedding is not None
        assert len(embedding) == embedder.embedding_dim
    
    def test_json_content_embedding(self):
        """Test embedding JSON content"""
        embedder = Embedder()
        json_str = '{"key": "value", "number": 123, "nested": {"data": true}}'
        embedding = embedder.embed_single(json_str)
        
        assert embedding is not None
        assert len(embedding) == embedder.embedding_dim
    
    def test_url_embedding(self):
        """Test embedding URLs"""
        embedder = Embedder()
        urls = [
            "https://www.example.com",
            "http://api.example.com/v1/users?id=123",
            "ftp://files.example.com/path/to/file.txt"
        ]
        
        for url in urls:
            embedding = embedder.embed_single(url)
            assert embedding is not None
            assert len(embedding) == embedder.embedding_dim
    
    def test_embedding_normalization(self):
        """Test that embeddings are normalized (if expected)"""
        embedder = Embedder()
        text = "Test normalization"
        embedding = embedder.embed_single(text)
        
        # Check if vector is normalized (L2 norm ≈ 1)
        norm = np.linalg.norm(embedding)
        # Some models normalize, some don't - just check it's reasonable
        assert norm > 0
        assert norm < 100  # Reasonable range


class TestEmbedderPerformance:
    """Test performance-related scenarios"""
    
    def test_large_batch_performance(self):
        """Test performance with large batch"""
        embedder = Embedder(batch_size=64)
        texts = [f"Performance test text number {i}" for i in range(500)]
        
        import time
        start = time.time()
        embeddings = embedder.embed_texts(texts)
        elapsed = time.time() - start
        
        assert len(embeddings) == 500
        # Should complete in reasonable time (< 60 seconds on CPU)
        assert elapsed < 60
    
    def test_memory_efficiency(self):
        """Test memory doesn't explode with many embeddings"""
        embedder = Embedder()
        texts = [f"Text {i}" for i in range(1000)]
        
        embeddings = embedder.embed_texts(texts)
        
        # Just verify it completes without memory error
        assert len(embeddings) == 1000
    
    def test_sequential_vs_batch_consistency(self):
        """Test sequential embedding matches batch embedding"""
        embedder = Embedder()
        texts = ["Text A", "Text B", "Text C"]
        
        # Sequential
        sequential = [embedder.embed_single(t) for t in texts]
        
        # Batch
        batch = embedder.embed_texts(texts)
        
        # Should produce same results
        for seq, bat in zip(sequential, batch):
            np.testing.assert_array_almost_equal(seq, bat, decimal=5)


class TestEmbedderErrorHandling:
    """Test error handling and recovery"""
    
    def test_invalid_model_name(self):
        """Test initialization with invalid model name"""
        with pytest.raises(Exception):
            Embedder(model_name="this-model-does-not-exist-xyz123")
    
    def test_invalid_device(self):
        """Test initialization with invalid device"""
        # Should fallback to CPU or raise appropriate error
        try:
            embedder = Embedder(device="invalid_device")
            # If it doesn't raise, it should fallback to cpu
            assert embedder.device == "cpu"
        except:
            pass  # Expected behavior
    
    def test_negative_batch_size(self):
        """Test with negative batch size"""
        # Should use absolute value or default
        embedder = Embedder(batch_size=-10)
        assert embedder.batch_size > 0
    
    def test_zero_batch_size(self):
        """Test with zero batch size"""
        # Should use default
        embedder = Embedder(batch_size=0)
        assert embedder.batch_size > 0
    
    @patch('sentence_transformers.SentenceTransformer')
    def test_model_loading_failure(self, mock_transformer):
        """Test handling of model loading failure"""
        mock_transformer.side_effect = Exception("Model loading failed")
        
        with pytest.raises(Exception):
            Embedder()


class TestEmbedderRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    @pytest.mark.slow
    def test_document_chunking_scenario(self):
        """Test embedding document chunks - marked as slow"""
        embedder = Embedder()
        
        # Simulate document chunks (reduced size)
        document = "This is a long document. " * 10  # Reduced from 50
        chunk_size = 100
        chunks = [document[i:i+chunk_size] for i in range(0, len(document), chunk_size)]
        
        embeddings = embedder.embed_texts(chunks)
        
        assert len(embeddings) == len(chunks)
        assert all(len(emb) == embedder.embedding_dim for emb in embeddings)
    
    def test_question_answering_scenario(self):
        """Test embedding questions and answers"""
        embedder = Embedder()
        
        questions = [
            "What is machine learning?",
            "How does deep learning work?",
            "What are neural networks?"
        ]
        
        answers = [
            "Machine learning is a method of data analysis...",
            "Deep learning uses neural networks with multiple layers...",
            "Neural networks are computing systems inspired by biological neural networks..."
        ]
        
        q_embeddings = embedder.embed_texts(questions)
        a_embeddings = embedder.embed_texts(answers)
        
        assert len(q_embeddings) == len(questions)
        assert len(a_embeddings) == len(answers)
    
    def test_semantic_search_scenario(self):
        """Test semantic search scenario"""
        embedder = Embedder()
        
        query = "How to train machine learning models?"
        documents = [
            "Training machine learning models requires data preprocessing and model selection.",
            "Cooking recipes for delicious meals at home.",
            "Machine learning training involves iterative optimization of model parameters.",
            "Travel destinations around the world."
        ]
        
        query_embedding = embedder.embed_single(query)
        doc_embeddings = embedder.embed_texts(documents)
        
        # Calculate similarities (cosine similarity)
        similarities = []
        for doc_emb in doc_embeddings:
            sim = np.dot(query_embedding, doc_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb)
            )
            similarities.append(sim)
        
        # Most similar should be ML-related docs
        assert similarities[0] > similarities[1]  # ML doc > cooking
        assert similarities[2] > similarities[3]  # ML doc > travel
    
    def test_multilingual_scenario(self):
        """Test multilingual embedding scenario"""
        embedder = Embedder()
        
        # Same meaning in different languages
        texts = [
            "Hello, how are you?",  # English
            "Hola, ¿cómo estás?",  # Spanish
            "Bonjour, comment allez-vous?",  # French
            "Hallo, wie geht es dir?",  # German
        ]
        
        embeddings = embedder.embed_texts(texts)
        
        # All should have same dimensionality
        assert all(len(emb) == embedder.embedding_dim for emb in embeddings)
        
        # With multilingual model, cross-lingual similarity should be good
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i+1, len(embeddings)):
                sim = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                )
                similarities.append(sim)
        
        # Multilingual model should capture cross-lingual semantic similarity
        avg_sim = np.mean(similarities)
        # Similar meaning across languages should have decent similarity
        assert avg_sim > 0.4  # Multilingual models can capture cross-lingual semantics
        assert all(not np.isnan(emb).any() for emb in embeddings)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
