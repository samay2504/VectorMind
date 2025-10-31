"""
Configuration management for the RAG system
"""
import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application
    app_name: str = Field(default="multimodal-rag-system", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_workers: int = Field(default=4, alias="API_WORKERS")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"], alias="CORS_ORIGINS"
    )

    # Qdrant (Primary)
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_collection: str = Field(default="multimodal_docs", alias="QDRANT_COLLECTION")
    qdrant_vector_size: int = Field(default=384, alias="QDRANT_VECTOR_SIZE")
    qdrant_health_check_timeout: int = Field(default=5, alias="QDRANT_HEALTH_CHECK_TIMEOUT")
    qdrant_max_retries: int = Field(default=3, alias="QDRANT_MAX_RETRIES")

    # Milvus (Fallback)
    milvus_url: str = Field(default="localhost:19530", alias="MILVUS_URL")
    milvus_collection: str = Field(default="multimodal_docs", alias="MILVUS_COLLECTION")
    milvus_vector_size: int = Field(default=384, alias="MILVUS_VECTOR_SIZE")

    # MongoDB
    mongo_uri: str = Field(default="mongodb://localhost:27017", alias="MONGO_URI")
    mongo_db: str = Field(default="multimodal_rag", alias="MONGO_DB")
    mongo_collection_docs: str = Field(default="documents", alias="MONGO_COLLECTION_DOCS")
    mongo_collection_consent: str = Field(default="consents", alias="MONGO_COLLECTION_CONSENT")
    mongo_collection_audit: str = Field(default="audit_logs", alias="MONGO_COLLECTION_AUDIT")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_ttl: int = Field(default=3600, alias="REDIS_TTL")
    redis_max_connections: int = Field(default=50, alias="REDIS_MAX_CONNECTIONS")

    # Embeddings
    embedder_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2", alias="EMBEDDER_MODEL"
    )
    embedder_batch_size: int = Field(default=32, alias="EMBEDDER_BATCH_SIZE")
    embedder_device: str = Field(default="cpu", alias="EMBEDDER_DEVICE")

    # Vision & OCR
    vision_model: str = Field(default="openai/clip-vit-base-patch32", alias="VISION_MODEL")
    ocr_langs: str = Field(default="eng", alias="OCR_LANGS")
    ocr_config: str = Field(default="--oem 3 --psm 6", alias="OCR_CONFIG")
    tesseract_path: Optional[str] = Field(default=None, alias="TESSERACT_PATH")

    # Chunking
    chunk_size: int = Field(default=1024, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=128, alias="CHUNK_OVERLAP")
    chunking_strategy: str = Field(default="token-aware", alias="CHUNKING_STRATEGY")

    # Retrieval
    default_top_k: int = Field(default=5, alias="DEFAULT_TOP_K")
    dense_top_k: int = Field(default=10, alias="DENSE_TOP_K")
    sparse_top_k: int = Field(default=10, alias="SPARSE_TOP_K")
    rerank_top_n: int = Field(default=5, alias="RERANK_TOP_N")
    enable_reranking: bool = Field(default=True, alias="ENABLE_RERANKING")
    default_retrieval_strategy: str = Field(default="hybrid", alias="DEFAULT_RETRIEVAL_STRATEGY")

    # LLM Provider
    llm_provider_preference: List[str] = Field(
        default=["google_genai", "groq", "openai", "huggingface", "fallback"],
        alias="LLM_PROVIDER_PREFERENCE",
    )
    llm_temperature: float = Field(default=0.1, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2048, alias="LLM_MAX_TOKENS")

    # LLM API Keys
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    huggingfacehub_api_token: Optional[str] = Field(default=None, alias="HUGGINGFACEHUB_API_TOKEN")

    # Security
    jwt_secret: str = Field(default="change-this-secret", alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiration: int = Field(default=3600, alias="JWT_EXPIRATION")
    encryption_key: str = Field(
        default="change-this-32-byte-hex-key-here!", alias="ENCRYPTION_KEY"
    )
    field_encryption_enabled: bool = Field(default=True, alias="FIELD_ENCRYPTION_ENABLED")

    # Compliance
    retention_days: int = Field(default=90, alias="RETENTION_DAYS")
    enable_consent_requirement: bool = Field(default=True, alias="ENABLE_CONSENT_REQUIREMENT")
    enable_pii_redaction: bool = Field(default=True, alias="ENABLE_PII_REDACTION")
    audit_log_enabled: bool = Field(default=True, alias="AUDIT_LOG_ENABLED")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, alias="RATE_LIMIT_PER_MINUTE")
    rate_limit_per_hour: int = Field(default=1000, alias="RATE_LIMIT_PER_HOUR")

    # Observability
    sentry_dsn: Optional[str] = Field(default=None, alias="SENTRY_DSN")
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")
    prometheus_port: int = Field(default=9090, alias="PROMETHEUS_PORT")
    grafana_port: int = Field(default=3000, alias="GRAFANA_PORT")

    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(
        default="redis://localhost:6379/2", alias="CELERY_RESULT_BACKEND"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
