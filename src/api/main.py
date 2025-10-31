"""
FastAPI application factory
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Initialize connections
    from src.core.vector_adapter import VectorDBManager
    from pymongo import MongoClient
    import redis
    
    # Vector DB
    vector_manager = VectorDBManager(
        qdrant_url=settings.qdrant_url,
        milvus_uri=settings.milvus_uri,
        collection_name=settings.qdrant_collection,
        vector_size=settings.qdrant_vector_size,
        max_retries=settings.qdrant_max_retries,
        qdrant_api_key=settings.qdrant_api_key,
        milvus_token=settings.milvus_token,
        milvus_user=settings.milvus_user,
        milvus_password=settings.milvus_password,
    )
    app.state.vector_manager = vector_manager
    logger.info("Vector DB manager initialized")
    
    # MongoDB
    mongo_client = MongoClient(settings.mongo_uri)
    app.state.mongo_client = mongo_client
    app.state.mongo_db = mongo_client[settings.mongo_db]
    logger.info(f"MongoDB connected: {settings.mongo_db}")
    
    # Setup MongoDB indexes and remove problematic ones
    try:
        db = app.state.mongo_db
        # Drop the problematic document_id index if it exists with null values
        try:
            existing_indexes = db.documents.list_indexes()
            for index in existing_indexes:
                if index.get("name") == "document_id_1":
                    db.documents.drop_index("document_id_1")
                    logger.info("Dropped problematic document_id_1 index")
        except Exception as e:
            logger.warning(f"Could not drop document_id index: {e}")
        
        # Create proper unique index on document_id (excluding nulls)
        db.documents.create_index(
            "document_id", 
            unique=True, 
            sparse=True,  # sparse=True allows multiple nulls
            name="document_id_unique"
        )
        logger.info("Created document_id unique sparse index")
    except Exception as e:
        logger.warning(f"Error setting up MongoDB indexes: {e}")
    
    # Redis
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis_client = redis_client
    logger.info("Redis connected")
    
    yield
    
    # Cleanup connections
    try:
        mongo_client.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB: {e}")
    
    try:
        redis_client.close()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error closing Redis: {e}")
    
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Production-grade Multimodal RAG System with GDPR/CCPA/DPDP compliance",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import and include routers
    from src.api.routes import health
    from src.api.routes import ingest, query, dsar, conversation
    
    app.include_router(health.router, tags=["Health"])
    app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
    app.include_router(query.router, prefix="/query", tags=["Query"])
    app.include_router(dsar.router, prefix="/dsar", tags=["DSAR"])
    app.include_router(conversation.router, prefix="/conversation", tags=["Conversation"])
    
    # Prometheus metrics (if enabled)
    if settings.enable_metrics:
        try:
            from prometheus_client import make_asgi_app
            metrics_app = make_asgi_app()
            app.mount("/metrics", metrics_app)
            logger.info("Prometheus metrics enabled at /metrics")
        except ImportError:
            logger.warning("prometheus_client not installed, metrics disabled")
    
    logger.info(f"FastAPI app created - {settings.app_name} v{settings.app_version}")
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
