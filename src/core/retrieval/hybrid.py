"""
Hybrid retriever combining dense and sparse search
"""

import logging
from typing import List, Dict, Any, Optional

from .dense_retriever import DenseRetriever
from .sparse_retriever import SparseRetriever

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid search combining dense and sparse retrieval"""
    
    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3
    ):
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
    
    async def retrieve(
        self,
        query: str,
        collection_name: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using hybrid search
        
        Args:
            query: Search query
            collection_name: Vector collection name
            top_k: Number of results
            filters: Optional metadata filters
        
        Returns:
            List of search results with combined scores
        """
        try:
            # Get dense results
            dense_results = await self.dense_retriever.retrieve(
                query=query,
                collection_name=collection_name,
                top_k=top_k * 2,  # Get more results for fusion
                filters=filters
            )
            
            # Get sparse results (if corpus is indexed)
            sparse_results = self.sparse_retriever.retrieve(
                query=query,
                top_k=top_k * 2
            )
            
            # Combine and re-rank
            combined = self._fusion(dense_results, sparse_results)
            
            return combined[:top_k]
        
        except Exception as e:
            logger.error(f"Hybrid retrieval failed: {e}")
            # Fallback to dense only
            return await self.dense_retriever.retrieve(
                query=query,
                collection_name=collection_name,
                top_k=top_k,
                filters=filters
            )
    
    def _fusion(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fuse results using weighted scoring"""
        # Normalize scores
        dense_scores = self._normalize_scores(dense_results)
        sparse_scores = self._normalize_scores(sparse_results)
        
        # Create combined score dictionary
        combined_scores = {}
        
        # Add dense scores
        for result, score in zip(dense_results, dense_scores):
            doc_id = result.get("id", result.get("document_id"))
            combined_scores[doc_id] = {
                "score": score * self.dense_weight,
                "data": result
            }
        
        # Add sparse scores
        for result, score in zip(sparse_results, sparse_scores):
            doc_id = result.get("id", result.get("document_id"))
            if doc_id in combined_scores:
                combined_scores[doc_id]["score"] += score * self.sparse_weight
            else:
                combined_scores[doc_id] = {
                    "score": score * self.sparse_weight,
                    "data": result
                }
        
        # Sort by combined score
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # Return formatted results
        return [
            {**item[1]["data"], "hybrid_score": item[1]["score"]}
            for item in sorted_results
        ]
    
    @staticmethod
    def _normalize_scores(results: List[Dict[str, Any]]) -> List[float]:
        """Normalize scores to [0, 1] range"""
        if not results:
            return []
        
        scores = [r.get("score", 0) for r in results]
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [1.0] * len(scores)
        
        return [(s - min_score) / (max_score - min_score) for s in scores]
