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
    # TODO: Initialize connections (vector DB, MongoDB, Redis)
    yield
    # TODO: Cleanup connections
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
    app.include_router(health.router, tags=["Health"])
    
    # TODO: Add other routers when implemented
    # from src.api.routes import ingest, query, dsar
    # app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
    # app.include_router(query.router, prefix="/query", tags=["Query"])
    # app.include_router(dsar.router, prefix="/dsar", tags=["DSAR"])
    
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
