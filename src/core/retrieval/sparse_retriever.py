"""
Sparse retriever using BM25 keyword search
"""

import logging
from typing import List, Dict, Any, Optional
import math
from collections import Counter

logger = logging.getLogger(__name__)


class SparseRetriever:
    """BM25 sparse retrieval"""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.corpus_size = 0
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
    
    def index_documents(self, documents: List[Dict[str, Any]]):
        """Index documents for BM25 search"""
        self.corpus = [doc.get("text", "").lower().split() for doc in documents]
        self.corpus_size = len(self.corpus)
        self.avgdl = sum(len(doc) for doc in self.corpus) / self.corpus_size if self.corpus_size > 0 else 0
        
        # Document frequencies
        df = {}
        for document in self.corpus:
            frequencies = set(document)
            for word in frequencies:
                df[word] = df.get(word, 0) + 1
        
        # IDF calculation
        self.idf = {}
        for word, freq in df.items():
            self.idf[word] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)
        
        # Document lengths
        self.doc_len = [len(doc) for doc in self.corpus]
    
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using BM25
        
        Args:
            query: Search query
            top_k: Number of results
            metadata: Optional document metadata
        
        Returns:
            List of search results with BM25 scores
        """
        if not self.corpus:
            logger.warning("No documents indexed")
            return []
        
        query_terms = query.lower().split()
        scores = []
        
        for idx, document in enumerate(self.corpus):
            score = 0
            doc_freqs = Counter(document)
            
            for term in query_terms:
                if term not in doc_freqs:
                    continue
                
                freq = doc_freqs[term]
                idf_score = self.idf.get(term, 0)
                
                # BM25 formula
                numerator = freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * (self.doc_len[idx] / self.avgdl))
                score += idf_score * (numerator / denominator)
            
            scores.append((idx, score))
        
        # Sort by score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k results
        results = []
        for idx, score in scores[:top_k]:
            result = {
                "document_id": idx,
                "score": score,
                "text": " ".join(self.corpus[idx])
            }
            if metadata and idx < len(metadata):
                result.update(metadata[idx])
            results.append(result)
        
        return results
