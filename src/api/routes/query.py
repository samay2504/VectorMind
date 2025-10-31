"""
Query endpoints for RAG
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from src.api.dependencies import get_vector_manager, get_embedder, get_llm_provider
from src.core.vector_adapter import VectorDBManager
from src.core.ingestion.embedder import Embedder
from src.core.llm.provider import LLMProvider
from src.core.retrieval.dense_retriever import DenseRetriever

logger = logging.getLogger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    collection_name: str = "default"
    top_k: int = 5
    filters: Optional[Dict[str, Any]] = None
    use_rag: bool = True


class QueryResponse(BaseModel):
    """Query response model"""
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@router.post("/", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    vector_manager: VectorDBManager = Depends(get_vector_manager),
    embedder: Embedder = Depends(get_embedder),
    llm_provider: LLMProvider = Depends(get_llm_provider)
) -> QueryResponse:
    """
    Query the RAG system
    
    Args:
        request: Query request with text and parameters
        vector_manager: Vector DB manager
        embedder: Embedding generator
        llm_provider: LLM provider
    
    Returns:
        Query response with answer and sources
    """
    try:
        # Retrieve relevant documents
        retriever = DenseRetriever(vector_manager, embedder)
        results = await retriever.retrieve(
            query=request.query,
            collection_name=request.collection_name,
            top_k=request.top_k,
            filters=request.filters
        )
        
        if not results:
            return QueryResponse(
                query=request.query,
                answer="No relevant documents found.",
                sources=[],
                metadata={"source_count": 0}
            )
        
        # Format context for LLM
        context = "\n\n".join([
            f"[Source {i+1}]: {r.get('payload', {}).get('text', '')}"
            for i, r in enumerate(results)
        ])
        
        # Generate answer with LLM
        if request.use_rag:
            prompt = f"""Based on the following context, answer the query.

Context:
{context}

Query: {request.query}

Answer:"""
            
            response = llm_provider.invoke(prompt)
            answer = response.get("content", "Unable to generate answer")
        else:
            answer = context
        
        # Format sources
        sources = [
            {
                "text": r.get("payload", {}).get("text", ""),
                "score": r.get("score", 0),
                "document_id": r.get("payload", {}).get("document_id"),
                "filename": r.get("payload", {}).get("filename")
            }
            for r in results
        ]
        
        return QueryResponse(
            query=request.query,
            answer=answer,
            sources=sources,
            metadata={
                "source_count": len(sources),
                "llm_used": request.use_rag
            }
        )
    
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_only(
    request: QueryRequest,
    vector_manager: VectorDBManager = Depends(get_vector_manager),
    embedder: Embedder = Depends(get_embedder)
) -> Dict[str, Any]:
    """
    Search without LLM augmentation
    
    Returns only the retrieved documents
    """
    try:
        retriever = DenseRetriever(vector_manager, embedder)
        results = await retriever.retrieve(
            query=request.query,
            collection_name=request.collection_name,
            top_k=request.top_k,
            filters=request.filters
        )
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
