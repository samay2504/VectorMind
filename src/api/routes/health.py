"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
from pymongo.database import Database
import redis

from src.core.vector_adapter import VectorDBManager
from src.api.dependencies import get_vector_manager, get_mongo_db, get_redis_client

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
async def readiness_check(
    vector_manager: VectorDBManager = Depends(get_vector_manager),
    mongo_db: Database = Depends(get_mongo_db),
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Readiness check - verifies all dependencies are available
    
    Returns:
        Readiness status with dependency checks
    """
    dependencies = {}
    
    # Check Vector DB
    try:
        health = vector_manager.check_health()
        dependencies["vector_db"] = "healthy" if health.get("healthy") else "unhealthy"
    except Exception as e:
        dependencies["vector_db"] = f"unhealthy: {str(e)}"
    
    # Check MongoDB
    try:
        mongo_db.command("ping")
        dependencies["document_store"] = "healthy"
    except Exception as e:
        dependencies["document_store"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        redis_client.ping()
        dependencies["cache"] = "healthy"
    except Exception as e:
        dependencies["cache"] = f"unhealthy: {str(e)}"
    
    # LLM provider check (optional)
    try:
        from src.core.llm.provider import LLMProvider
        llm_config = {"temperature": 0.1, "provider_preference": ["google_genai", "groq", "openai"]}
        llm = LLMProvider(llm_config)
        dependencies["llm_provider"] = "healthy"
    except Exception as e:
        dependencies["llm_provider"] = f"degraded: {str(e)}"
    
    all_healthy = all("healthy" in str(status) for status in dependencies.values())
    
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
