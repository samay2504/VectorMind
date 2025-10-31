"""
Demonstration of multilingual embedding capabilities
Shows how the RAG system can handle multiple languages
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.ingestion.embedder import Embedder
import numpy as np


def calculate_similarity(emb1, emb2):
    """Calculate cosine similarity between two embeddings"""
    return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))


def main():
    print("=" * 80)
    print("Multilingual Embedding Demo")
    print("=" * 80)
    print()
    
    # Initialize embedder with multilingual model
    embedder = Embedder()
    print(f"Model: {embedder.model_name}")
    print(f"Embedding dimension: {embedder.embedding_dim}")
    print()
    
    # Test 1: Same phrase in different languages
    print("Test 1: Cross-lingual semantic similarity")
    print("-" * 80)
    
    phrases = {
        "English": "Hello, how are you?",
        "Spanish": "Hola, ¿cómo estás?",
        "French": "Bonjour, comment allez-vous?",
        "German": "Hallo, wie geht es dir?",
        "Italian": "Ciao, come stai?",
        "Portuguese": "Olá, como está?",
    }
    
    embeddings = {}
    for lang, phrase in phrases.items():
        embeddings[lang] = embedder.embed_single(phrase)
        print(f"{lang:12s}: {phrase}")
    
    print("\nCross-lingual similarity matrix:")
    print("-" * 80)
    
    languages = list(phrases.keys())
    print(f"{'':12s}", end="")
    for lang in languages:
        print(f"{lang[:8]:>10s}", end="")
    print()
    
    for i, lang1 in enumerate(languages):
        print(f"{lang1:12s}", end="")
        for j, lang2 in enumerate(languages):
            sim = calculate_similarity(embeddings[lang1], embeddings[lang2])
            print(f"{sim:10.3f}", end="")
        print()
    
    print()
    
    # Test 2: Different topics in same language
    print("\nTest 2: Within-language topic similarity")
    print("-" * 80)
    
    topics = {
        "Weather": "The weather is sunny and warm today.",
        "Weather (similar)": "It's a beautiful sunny day outside.",
        "Technology": "Artificial intelligence is transforming industries.",
        "Food": "I love Italian pizza and pasta dishes.",
    }
    
    topic_embeddings = {}
    for topic, text in topics.items():
        topic_embeddings[topic] = embedder.embed_single(text)
        print(f"{topic:20s}: {text}")
    
    print("\nTopic similarity matrix:")
    print("-" * 80)
    
    topic_list = list(topics.keys())
    print(f"{'':20s}", end="")
    for topic in topic_list:
        print(f"{topic[:15]:>17s}", end="")
    print()
    
    for topic1 in topic_list:
        print(f"{topic1:20s}", end="")
        for topic2 in topic_list:
            sim = calculate_similarity(topic_embeddings[topic1], topic_embeddings[topic2])
            print(f"{sim:17.3f}", end="")
        print()
    
    print()
    
    # Test 3: Multilingual documents
    print("\nTest 3: Multilingual document retrieval")
    print("-" * 80)
    
    documents = [
        ("EN - AI", "Artificial intelligence is revolutionizing technology."),
        ("ES - IA", "La inteligencia artificial está revolucionando la tecnología."),
        ("FR - IA", "L'intelligence artificielle révolutionne la technologie."),
        ("EN - Weather", "The weather is perfect for a picnic today."),
    ]
    
    query = "Tell me about AI and machine learning"
    query_emb = embedder.embed_single(query)
    
    print(f"Query: '{query}'")
    print("\nDocument similarities:")
    
    doc_similarities = []
    for doc_id, doc_text in documents:
        doc_emb = embedder.embed_single(doc_text)
        sim = calculate_similarity(query_emb, doc_emb)
        doc_similarities.append((doc_id, doc_text, sim))
        print(f"  {doc_id:15s} (sim: {sim:.3f}): {doc_text}")
    
    # Sort by similarity
    doc_similarities.sort(key=lambda x: x[2], reverse=True)
    
    print("\nRanked results:")
    for i, (doc_id, doc_text, sim) in enumerate(doc_similarities, 1):
        print(f"  {i}. {doc_id:15s} (sim: {sim:.3f})")
    
    print()
    print("=" * 80)
    print("Key Observations:")
    print("1. Cross-lingual embeddings capture semantic similarity across languages")
    print("2. Similar topics have high similarity even in different languages")
    print("3. Multilingual RAG can retrieve relevant documents regardless of language")
    print("4. Perfect for international document collections and multilingual search")
    print("=" * 80)


if __name__ == "__main__":
    main()
