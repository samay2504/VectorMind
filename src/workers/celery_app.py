"""
Celery application configuration
Background task processing for async operations
"""

import logging
from celery import Celery
from src.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "multimodal_rag",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.workers.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "src.workers.tasks.process_document_async": {"queue": "ingestion"},
        "src.workers.tasks.batch_embed_texts": {"queue": "embeddings"},
        "src.workers.tasks.cleanup_old_data": {"queue": "maintenance"},
    },
    
    # Task time limits
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minutes soft limit
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={
        "master_name": "mymaster"
    },
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-old-data-daily": {
            "task": "src.workers.tasks.cleanup_old_data",
            "schedule": 86400.0,  # Daily
        },
        "expire-old-consents-daily": {
            "task": "src.workers.tasks.expire_old_consents",
            "schedule": 86400.0,  # Daily
        },
    },
)

logger.info("Celery app initialized")
