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
        # Step 1: Check if documents exist in the collection (context check)
        collection_info = None
        has_documents = False
        doc_count = 0
        
        try:
            collection_info = await vector_manager.get_collection_info()
            # Handle both None and dict responses safely
            if collection_info and isinstance(collection_info, dict):
                doc_count = collection_info.get("vectors_count", 0) or 0
                # Ensure doc_count is an integer
                doc_count = int(doc_count) if doc_count is not None else 0
                has_documents = doc_count > 0
            else:
                doc_count = 0
                has_documents = False
            logger.info(f"Collection '{request.collection_name}' has {doc_count} documents")
        except Exception as e:
            logger.warning(f"Could not check collection info: {e}")
            doc_count = 0
            has_documents = False
        
        # Step 2: Use LLM to intelligently classify query intent WITH context awareness
        classification_prompt = f"""Analyze this user query and determine the intent.

Query: "{request.query}"

Context: {"User HAS uploaded documents" if has_documents else "User has NOT uploaded any documents yet"}

Classify as ONE of these types:
1. CONVERSATIONAL - Greetings, thanks, casual chat (hello, hi, how are you, thanks, bye, etc.)
2. GENERAL_KNOWLEDGE - General factual questions that don't need specific user documents (What is AI?, How does X work?, etc.)
3. DOCUMENT_QUERY - Questions about documents, asking to explain/summarize/analyze content, or referencing "the document", "my files", "this PDF", etc.

IMPORTANT: If the query mentions "document", "file", "upload", "this", "my", or asks to explain/summarize content, it's likely a DOCUMENT_QUERY.

Respond with ONLY one word: CONVERSATIONAL, GENERAL_KNOWLEDGE, or DOCUMENT_QUERY"""

        classification_response = llm_provider.invoke(classification_prompt)
        query_type = classification_response.get("content", "").strip().upper()
        
        logger.info(f"Query classified as: {query_type} (has_documents: {has_documents})")
        
        # Step 3: Override classification if query references documents but none exist
        document_keywords = ["document", "file", "upload", "pdf", "text", "this", "my", "explain", "summarize", "analyze"]
        query_lower = request.query.lower()
        mentions_documents = any(keyword in query_lower for keyword in document_keywords)
        
        # If mentions documents but none exist, treat as GENERAL_KNOWLEDGE with helpful message
        if "DOCUMENT" in query_type and not has_documents:
            return QueryResponse(
                query=request.query,
                answer=f"I noticed you're asking about documents, but I don't see any uploaded documents in your collection yet. Please upload documents first using the DATA INGESTION tab, then I'll be able to answer questions about them.",
                sources=[],
                metadata={"type": "no_documents", "classification": query_type, "has_documents": False}
            )
        
        # If mentions documents AND they exist, force DOCUMENT_QUERY classification
        if mentions_documents and has_documents:
            query_type = "DOCUMENT_QUERY"
            logger.info(f"Overriding classification to DOCUMENT_QUERY based on keywords and document availability")
        
        # Handle conversational queries directly without RAG
        if "CONVERSATIONAL" in query_type:
            prompt = f"""You are a helpful AI assistant for a Multimodal RAG document query system. 
The user said: "{request.query}"

Respond naturally and warmly. If it's a greeting, introduce yourself briefly. 
If it's thanks, acknowledge gracefully. If it's goodbye, wish them well.
Keep it concise (2-3 sentences)."""
            
            response = llm_provider.invoke(prompt)
            answer = response.get("content", "Hello! How can I help you today?")
            
            return QueryResponse(
                query=request.query,
                answer=answer,
                sources=[],
                metadata={"type": "conversational", "classification": query_type, "has_documents": has_documents}
            )
        
        # Handle general knowledge queries without RAG
        if "GENERAL" in query_type and not mentions_documents:
            prompt = f"""You are a knowledgeable AI assistant. The user asked: "{request.query}"

This is a general knowledge question. Provide a helpful, accurate answer based on your training.
{"Since the user has uploaded documents, you can mention that you can also search through their specific materials if needed." if has_documents else "If appropriate, mention that they can upload documents if they have specific materials to analyze."}
Keep it informative but concise (3-5 sentences)."""
            
            response = llm_provider.invoke(prompt)
            answer = response.get("content", "I can provide general information on that topic.")
            
            return QueryResponse(
                query=request.query,
                answer=answer,
                sources=[],
                metadata={"type": "general_knowledge", "classification": query_type, "has_documents": has_documents}
            )
        
        # Retrieve relevant documents for document-specific queries
        retriever = DenseRetriever(vector_manager, embedder)
        results = await retriever.retrieve(
            query=request.query,
            collection_name=request.collection_name,  # Note: DenseRetriever accepts this but doesn't use it for VectorDBManager
            top_k=request.top_k,
            filters=request.filters
        )
        
        if not results:
            # No documents found - use LLM for general response
            prompt = f"""You are a helpful AI assistant. The user asked: "{request.query}"

Since no relevant documents were found in the knowledge base, provide a helpful general response. If it's a factual question, politely explain that you don't have specific documents on that topic. If it's a casual query, respond naturally."""
            
            response = llm_provider.invoke(prompt)
            answer = response.get("content", "I don't have any relevant documents on that topic. Could you try rephrasing your question or upload documents related to your query?")
            
            return QueryResponse(
                query=request.query,
                answer=answer,
                sources=[],
                metadata={"source_count": 0, "type": "general_llm"}
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
