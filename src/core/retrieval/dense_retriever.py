"""
Dense retriever using vector similarity search
"""

import logging
from typing import List, Dict, Any, Optional

from src.core.vector_adapter import VectorDBManager
from src.core.ingestion.embedder import Embedder

logger = logging.getLogger(__name__)


class DenseRetriever:
    """Dense retrieval using embedding similarity"""
    
    def __init__(self, vector_manager: VectorDBManager, embedder: Embedder):
        self.vector_manager = vector_manager
        self.embedder = embedder
    
    async def retrieve(
        self,
        query: str,
        collection_name: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using dense vector search
        
        Args:
            query: Search query
            collection_name: Vector collection name
            top_k: Number of results
            filters: Optional metadata filters
        
        Returns:
            List of search results with scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_single(query)
            
            # Search vector DB
            results = self.vector_manager.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                top_k=top_k,
                filter_dict=filters
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Dense retrieval failed: {e}")
            return []
