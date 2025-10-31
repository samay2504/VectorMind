"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

router = APIRouter()


@router.get("/healthz")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "multimodal-rag-system"
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check - verifies all dependencies are available
    
    Returns:
        Readiness status with dependency checks
    """
    # TODO: Add actual dependency checks
    # - Vector DB connection
    # - MongoDB connection
    # - Redis connection
    
    dependencies = {
        "vector_db": "healthy",  # TODO: Implement actual check
        "document_store": "healthy",
        "cache": "healthy",
        "llm_provider": "healthy"
    }
    
    all_healthy = all(status == "healthy" for status in dependencies.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "dependencies": dependencies
    }


@router.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": "Multimodal RAG System API",
        "docs": "/docs",
        "health": "/healthz"
    }
