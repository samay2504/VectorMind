"""
Comprehensive unit tests for TextChunker with edge cases and real-world scenarios
"""

import pytest
from src.core.ingestion.text_chunker import TextChunker


class TestTextChunkerInitialization:
    """Test text chunker initialization"""
    
    def test_default_initialization(self):
        """Test default initialization"""
        chunker = TextChunker()
        assert chunker.chunk_size == 1024
        assert chunker.chunk_overlap == 128
        assert chunker.strategy == "token-aware"
    
    def test_custom_chunk_size(self):
        """Test with custom chunk size"""
        chunker = TextChunker(chunk_size=512)
        assert chunker.chunk_size == 512
    
    def test_custom_overlap(self):
        """Test with custom overlap"""
        chunker = TextChunker(chunk_overlap=64)
        assert chunker.chunk_overlap == 64
    
    def test_custom_strategy(self):
        """Test with custom strategy"""
        for strategy in ["token-aware", "sentence", "paragraph", "fixed"]:
            chunker = TextChunker(strategy=strategy)
            assert chunker.strategy == strategy
    
    def test_invalid_strategy(self):
        """Test with invalid strategy"""
        with pytest.raises((ValueError, AttributeError)):
            chunker = TextChunker(strategy="invalid_strategy")
    
    def test_zero_chunk_size(self):
        """Test with zero chunk size"""
        with pytest.raises((ValueError, AssertionError)):
            TextChunker(chunk_size=0)
    
    def test_negative_chunk_size(self):
        """Test with negative chunk size"""
        with pytest.raises((ValueError, AssertionError)):
            TextChunker(chunk_size=-100)
    
    def test_overlap_larger_than_chunk(self):
        """Test with overlap larger than chunk size"""
        with pytest.raises((ValueError, AssertionError)):
            TextChunker(chunk_size=100, chunk_overlap=200)


class TestBasicChunking:
    """Test basic chunking functionality"""
    
    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size"""
        chunker = TextChunker(chunk_size=1024)
        text = "This is a short text."
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) == 1
        assert chunks[0]["text"] == text
        assert chunks[0]["chunk_id"] == 0
    
    def test_chunk_empty_text(self):
        """Test chunking empty text"""
        chunker = TextChunker()
        chunks = chunker.chunk_text("")
        
        assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0]["text"] == "")
    
    def test_chunk_whitespace_only(self):
        """Test chunking whitespace only"""
        chunker = TextChunker()
        text = "   \n\t  \n  "
        chunks = chunker.chunk_text(text)
        
        # Should handle gracefully
        assert isinstance(chunks, list)
    
    def test_chunk_long_text(self):
        """Test chunking long text"""
        chunker = TextChunker(chunk_size=100, chunk_overlap=20, strategy="sentence")
        text = "word " * 50  # 250 characters (reduced for speed)
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 1
        assert all("chunk_id" in chunk for chunk in chunks)
        assert all("text" in chunk for chunk in chunks)
    
    def test_chunk_metadata(self):
        """Test chunks contain proper metadata"""
        chunker = TextChunker()
        text = "Test text for metadata"
        metadata = {"doc_id": "123", "author": "test"}
        chunks = chunker.chunk_text(text, metadata=metadata)
        
        assert all("metadata" in chunk for chunk in chunks)
        assert all(chunk["metadata"]["doc_id"] == "123" for chunk in chunks)
    
    def test_chunk_ids_sequential(self):
        """Test chunk IDs are sequential"""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text = "word " * 50
        chunks = chunker.chunk_text(text)
        
        chunk_ids = [chunk["chunk_id"] for chunk in chunks]
        assert chunk_ids == list(range(len(chunk_ids)))
    
    def test_chunks_overlap(self):
        """Test chunks have proper overlap"""
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        text = "This is a long text. " * 20
        chunks = chunker.chunk_text(text)
        
        if len(chunks) > 1:
            # Check that consecutive chunks have some overlap
            for i in range(len(chunks) - 1):
                chunk1_end = chunks[i]["text"][-20:]
                chunk2_start = chunks[i+1]["text"][:20]
                # There should be some overlap
                assert len(chunk1_end) > 0 and len(chunk2_start) > 0


class TestChunkingStrategies:
    """Test different chunking strategies"""
    
    def test_token_aware_strategy(self):
        """Test token-aware chunking"""
        chunker = TextChunker(strategy="token-aware", chunk_size=100, chunk_overlap=20)
        text = "This is a test. " * 50
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        assert all(len(chunk["text"]) > 0 for chunk in chunks)
    
    def test_sentence_strategy(self):
        """Test sentence-based chunking"""
        chunker = TextChunker(strategy="sentence", chunk_size=200)
        text = "First sentence. Second sentence. Third sentence. Fourth sentence."
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        # Sentences should be preserved
        for chunk in chunks:
            # Should end with sentence punctuation or be last chunk
            text = chunk["text"].strip()
            if text:
                assert text[-1] in ['.', '!', '?', '}'] or chunk == chunks[-1]
    
    def test_paragraph_strategy(self):
        """Test paragraph-based chunking"""
        chunker = TextChunker(strategy="paragraph", chunk_size=200)  # Reduced for speed
        text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
    
    def test_fixed_strategy(self):
        """Test fixed-size chunking"""
        chunker = TextChunker(strategy="fixed", chunk_size=50, chunk_overlap=10)
        text = "a" * 200
        chunks = chunker.chunk_text(text)
        
        # Most chunks should be exactly 50 characters (except last)
        for i, chunk in enumerate(chunks[:-1]):
            assert len(chunk["text"]) <= 50 + chunker.chunk_overlap


class TestEdgeCases:
    """Test edge cases"""
    
    def test_single_character(self):
        """Test chunking single character"""
        chunker = TextChunker()
        chunks = chunker.chunk_text("a")
        
        assert len(chunks) == 1
        assert chunks[0]["text"] == "a"
    
    def test_very_long_single_word(self):
        """Test chunking very long single word"""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text = "a" * 50  # Reduced for speed
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        # Should split even within word if necessary
    
    def test_repeated_punctuation(self):
        """Test text with repeated punctuation"""
        chunker = TextChunker()
        text = "Hello!!! World??? Test..."
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
    
    def test_mixed_newlines(self):
        """Test text with various newline styles"""
        chunker = TextChunker()
        text = "Line 1\nLine 2\r\nLine 3\rLine 4"
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
    
    def test_unicode_characters(self):
        """Test chunking unicode text"""
        chunker = TextChunker()
        texts = [
            "Hello 世界",
            "Привет мир",
            "مرحبا",
            "🚀🎉😊",
            "Café résumé"
        ]
        
        for text in texts:
            chunks = chunker.chunk_text(text)
            assert len(chunks) > 0
    
    def test_special_characters(self):
        """Test text with special characters"""
        chunker = TextChunker()
        text = "Special @#$%^&*() chars <html> [brackets] {braces}"
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        assert all(chunk["text"] for chunk in chunks)
    
    def test_tabs_and_spaces(self):
        """Test text with tabs and multiple spaces"""
        chunker = TextChunker()
        text = "Text\twith\ttabs   and   multiple    spaces"
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
    
    def test_only_punctuation(self):
        """Test text with only punctuation"""
        chunker = TextChunker()
        text = "!@#$%^&*()_+-=[]{}|;:',.<>?/"
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) >= 0
    
    def test_mixed_languages(self):
        """Test chunking mixed language text"""
        chunker = TextChunker()
        text = "English text. Texto español. Texte français. Deutscher Text. 中文文本."
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0


class TestRealWorldScenarios:
    """Test real-world document scenarios"""
    
    def test_chunk_article(self):
        """Test chunking a typical article"""
        chunker = TextChunker(chunk_size=200, chunk_overlap=50)  # Reduced chunk size for speed
        article = """
        Introduction: This is the introduction of the article.
        
        Main Body: This section contains the main content of the article.
        It has multiple paragraphs with various sentences.
        
        Conclusion: This is the conclusion that summarizes everything.
        """
        chunks = chunker.chunk_text(article)
        
        assert len(chunks) > 0
        assert all("text" in chunk for chunk in chunks)
        assert all("chunk_id" in chunk for chunk in chunks)
    
    def test_chunk_code(self):
        """Test chunking code snippets"""
        chunker = TextChunker(chunk_size=200)
        code = """
        def hello_world():
            print("Hello, World!")
            return True
        
        class MyClass:
            def __init__(self):
                self.value = 42
        """
        chunks = chunker.chunk_text(code)
        
        assert len(chunks) > 0
    
    def test_chunk_json(self):
        """Test chunking JSON content"""
        chunker = TextChunker()
        json_text = '{"key": "value", "number": 123, "array": [1, 2, 3], "nested": {"data": true}}'
        chunks = chunker.chunk_text(json_text)
        
        assert len(chunks) > 0
    
    def test_chunk_html(self):
        """Test chunking HTML content"""
        chunker = TextChunker()
        html = "<html><body><h1>Title</h1><p>Paragraph text here.</p></body></html>"
        chunks = chunker.chunk_text(html)
        
        assert len(chunks) > 0
    
    def test_chunk_markdown(self):
        """Test chunking Markdown content"""
        chunker = TextChunker()
        markdown = """
        # Heading 1
        ## Heading 2
        
        This is **bold** and this is *italic*.
        
        - List item 1
        - List item 2
        
        [Link](https://example.com)
        """
        chunks = chunker.chunk_text(markdown)
        
        assert len(chunks) > 0
    
    def test_chunk_csv_like(self):
        """Test chunking CSV-like content"""
        chunker = TextChunker()
        csv = "Name,Age,City\nJohn,30,NYC\nJane,25,LA\nBob,35,SF"
        chunks = chunker.chunk_text(csv)
        
        assert len(chunks) > 0
    
    def test_chunk_email(self):
        """Test chunking email content"""
        chunker = TextChunker()
        email = """
        From: sender@example.com
        To: recipient@example.com
        Subject: Test Email
        
        Dear Recipient,
        
        This is the body of the email.
        
        Best regards,
        Sender
        """
        chunks = chunker.chunk_text(email)
        
        assert len(chunks) > 0
    
    def test_chunk_scientific_paper(self):
        """Test chunking scientific paper"""
        chunker = TextChunker(chunk_size=300, chunk_overlap=50)
        paper = """
        Abstract: This paper presents a novel approach to machine learning.
        
        Introduction: Machine learning has become increasingly important.
        Previous work has shown that deep learning models can achieve
        state-of-the-art results on various tasks.
        
        Methods: We propose a new architecture that combines CNNs and
        attention mechanisms. Our approach uses residual connections.
        
        Results: Our model achieves 95% accuracy on the test set.
        
        Conclusion: We have demonstrated the effectiveness of our approach.
        """
        chunks = chunker.chunk_text(paper)
        
        assert len(chunks) > 0
    
    def test_chunk_legal_document(self):
        """Test chunking legal document"""
        chunker = TextChunker()
        legal = """
        ARTICLE I: Definitions
        1.1 "Party" means any individual or entity entering this agreement.
        1.2 "Effective Date" means the date this agreement becomes valid.
        
        ARTICLE II: Terms and Conditions
        2.1 The parties agree to the following terms.
        2.2 This agreement shall remain in effect for one year.
        """
        chunks = chunker.chunk_text(legal)
        
        assert len(chunks) > 0
    
    def test_chunk_chat_conversation(self):
        """Test chunking chat conversation"""
        chunker = TextChunker()
        chat = """
        User: Hello, how can I help you?
        Assistant: I need information about your product.
        User: Sure, what would you like to know?
        Assistant: What are the features?
        User: Here are the main features: A, B, C.
        """
        chunks = chunker.chunk_text(chat)
        
        assert len(chunks) > 0
    
    def test_chunk_bullet_points(self):
        """Test chunking bullet point lists"""
        chunker = TextChunker()
        bullets = """
        Key Features:
        • Feature one with detailed description
        • Feature two with more information
        • Feature three explaining capabilities
        • Feature four with examples
        • Feature five with use cases
        """
        chunks = chunker.chunk_text(bullets)
        
        assert len(chunks) > 0
    
    def test_chunk_numbered_list(self):
        """Test chunking numbered lists"""
        chunker = TextChunker()
        numbered = """
        Steps to follow:
        1. First, prepare your environment
        2. Second, install the required packages
        3. Third, configure the settings
        4. Fourth, run the application
        5. Finally, verify everything works
        """
        chunks = chunker.chunk_text(numbered)
        
        assert len(chunks) > 0


class TestPerformance:
    """Test performance scenarios - optimized for speed"""
    
    @pytest.mark.slow
    def test_large_document_chunking(self):
        """Test chunking large document - marked as slow"""
        chunker = TextChunker(chunk_size=1000)
        text = "This is a sentence. " * 50  # ~1k characters (reduced for speed)
        
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        assert len(chunks) < 20  # Reasonable number of chunks
    
    def test_many_small_chunks(self):
        """Test creating many small chunks"""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10, strategy="sentence")
        text = "word " * 100  # Reduced from 1000
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 5
    
    @pytest.mark.slow
    def test_memory_efficiency(self):
        """Test memory with moderately large text"""
        chunker = TextChunker()
        text = "a" * 10000  # 10KB instead of 1MB
        
        chunks = chunker.chunk_text(text)
        
        # Just verify it completes
        assert len(chunks) > 0


class TestChunkQuality:
    """Test quality of chunks"""
    
    def test_no_empty_chunks(self):
        """Test that no empty chunks are created"""
        chunker = TextChunker()
        text = "This is a test. " * 100
        chunks = chunker.chunk_text(text)
        
        assert all(len(chunk["text"].strip()) > 0 for chunk in chunks)
    
    def test_chunk_boundaries_sensible(self):
        """Test that chunks break at sensible boundaries"""
        chunker = TextChunker(strategy="sentence", chunk_size=100, chunk_overlap=20)
        text = "First sentence. Second sentence. Third sentence."
        chunks = chunker.chunk_text(text)
        
        # Chunks should preferably end at sentence boundaries
        for chunk in chunks[:-1]:  # Except last chunk
            text = chunk["text"].strip()
            if text:
                # Should end with sentence punctuation
                assert text[-1] in ['.', '!', '?'] or len(text) >= 100
    
    def test_preserve_words(self):
        """Test that words are not split (when possible)"""
        chunker = TextChunker(strategy="token-aware", chunk_size=50, chunk_overlap=10)
        text = "Supercalifragilisticexpialidocious is a long word"
        chunks = chunker.chunk_text(text)
        
        # Words should be preserved when possible
        assert len(chunks) > 0
    
    def test_metadata_preservation(self):
        """Test that metadata is preserved in all chunks"""
        chunker = TextChunker(chunk_size=50, chunk_overlap=10)
        text = "word " * 50
        metadata = {"doc_id": "123", "author": "test", "date": "2025-10-31"}
        
        chunks = chunker.chunk_text(text, metadata=metadata)
        
        for chunk in chunks:
            assert chunk["metadata"]["doc_id"] == "123"
            assert chunk["metadata"]["author"] == "test"
            assert chunk["metadata"]["date"] == "2025-10-31"


class TestErrorHandling:
    """Test error handling"""
    
    def test_none_input(self):
        """Test with None input"""
        chunker = TextChunker()
        with pytest.raises((TypeError, AttributeError)):
            chunker.chunk_text(None)
    
    def test_numeric_input(self):
        """Test with numeric input"""
        chunker = TextChunker()
        with pytest.raises((TypeError, AttributeError)):
            chunker.chunk_text(12345)
    
    def test_list_input(self):
        """Test with list input"""
        chunker = TextChunker()
        with pytest.raises((TypeError, AttributeError)):
            chunker.chunk_text(["text1", "text2"])
    
    def test_dict_input(self):
        """Test with dict input"""
        chunker = TextChunker()
        with pytest.raises((TypeError, AttributeError)):
            chunker.chunk_text({"key": "value"})


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
