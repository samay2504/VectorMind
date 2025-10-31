"""
FastAPI dependency injection for shared resources
"""

import logging
from typing import Optional

from fastapi import Request, HTTPException, Depends
from pymongo.database import Database
import redis

from src.core.vector_adapter import VectorDBManager
from src.core.llm.provider import LLMProvider
from src.core.ingestion.embedder import Embedder

logger = logging.getLogger(__name__)


def get_vector_manager(request: Request) -> VectorDBManager:
    """Get vector DB manager from app state"""
    if not hasattr(request.app.state, "vector_manager"):
        raise HTTPException(status_code=500, detail="Vector manager not initialized")
    return request.app.state.vector_manager


def get_mongo_db(request: Request) -> Database:
    """Get MongoDB database from app state"""
    if not hasattr(request.app.state, "mongo_db"):
        raise HTTPException(status_code=500, detail="MongoDB not initialized")
    return request.app.state.mongo_db


def get_redis_client(request: Request) -> redis.Redis:
    """Get Redis client from app state"""
    if not hasattr(request.app.state, "redis_client"):
        raise HTTPException(status_code=500, detail="Redis not initialized")
    return request.app.state.redis_client


def get_llm_provider() -> LLMProvider:
    """Get LLM provider instance"""
    llm_config = {"temperature": 0.1, "provider_preference": ["google_genai", "groq", "openai"]}
    return LLMProvider(llm_config)


def get_embedder() -> Embedder:
    """Get embedder instance with GPU support"""
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return Embedder(device=device)
