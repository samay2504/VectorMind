"""
Unified Vector Database Adapter with Qdrant (Primary) and Milvus (Fallback)
Provides automatic failover, health checks, and consistent interface
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class VectorDBAdapter(ABC):
    """Abstract base class for vector database adapters"""

    @abstractmethod
    async def create_collection(self, collection_name: str, vector_size: int, **kwargs):
        """Create a collection/index"""
        pass

    @abstractmethod
    async def index_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> bool:
        """Index vectors with metadata"""
        pass

    @abstractmethod
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        pass

    @abstractmethod
    async def bulk_upsert(
        self, collection_name: str, vectors: List[List[float]], payloads: List[Dict[str, Any]]
    ) -> bool:
        """Bulk upsert vectors"""
        pass

    @abstractmethod
    async def delete_by_filter(self, collection_name: str, filters: Dict[str, Any]) -> bool:
        """Delete vectors by filter"""
        pass

    @abstractmethod
    async def health_check(self) -> Tuple[bool, str]:
        """Check if the vector DB is healthy"""
        pass

    @abstractmethod
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection information"""
        pass


class QdrantAdapter(VectorDBAdapter):
    """Qdrant vector database adapter (Primary)"""

    def __init__(self, url: str, collection_name: str, vector_size: int, max_retries: int = 3, api_key: str = None):
        self.url = url
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.max_retries = max_retries
        self.api_key = api_key
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Qdrant client"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            # Initialize client with API key if provided (for Qdrant Cloud)
            if self.api_key:
                self._client = QdrantClient(url=self.url, api_key=self.api_key)
                logger.info(f"Qdrant client initialized with API key: {self.url}")
            else:
                self._client = QdrantClient(url=self.url)
                logger.info(f"Qdrant client initialized: {self.url}")
            
            self._distance = Distance
            self._vector_params = VectorParams
        except ImportError:
            logger.error("qdrant-client not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            raise

    async def create_collection(self, collection_name: str, vector_size: int, **kwargs):
        """Create Qdrant collection with HNSW indexing"""
        try:
            from qdrant_client.models import Distance, VectorParams

            collections = self._client.get_collections().collections
            collection_names = [col.name for col in collections]

            if collection_name not in collection_names:
                self._client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Qdrant collection: {e}")
            return False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def index_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> bool:
        """Index vectors in Qdrant"""
        try:
            from qdrant_client.models import PointStruct

            if ids is None:
                import uuid

                ids = [str(uuid.uuid4()) for _ in range(len(vectors))]

            points = [
                PointStruct(id=idx, vector=vector, payload=payload)
                for idx, vector, payload in zip(ids, vectors, payloads)
            ]

            self._client.upsert(collection_name=collection_name, points=points)
            logger.info(f"Indexed {len(vectors)} vectors in Qdrant")
            return True
        except Exception as e:
            logger.error(f"Failed to index vectors in Qdrant: {e}")
            raise

    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search in Qdrant with optional filtering"""
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            # Build filter if provided
            qdrant_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                if conditions:
                    qdrant_filter = Filter(must=conditions)

            results = self._client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=qdrant_filter,
            )

            return [
                {
                    "id": str(result.id),
                    "score": result.score,
                    "payload": result.payload,
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Failed to search in Qdrant: {e}")
            raise

    async def bulk_upsert(
        self, collection_name: str, vectors: List[List[float]], payloads: List[Dict[str, Any]]
    ) -> bool:
        """Bulk upsert in Qdrant"""
        return await self.index_vectors(collection_name, vectors, payloads)

    async def delete_by_filter(self, collection_name: str, filters: Dict[str, Any]) -> bool:
        """Delete vectors by filter in Qdrant"""
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue

            conditions = []
            for key, value in filters.items():
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))

            qdrant_filter = Filter(must=conditions)

            self._client.delete(collection_name=collection_name, points_selector=qdrant_filter)
            logger.info(f"Deleted vectors from Qdrant with filter: {filters}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors in Qdrant: {e}")
            return False

    async def health_check(self) -> Tuple[bool, str]:
        """Check Qdrant health"""
        try:
            collections = self._client.get_collections()
            return True, f"Qdrant healthy, {len(collections.collections)} collections"
        except Exception as e:
            return False, f"Qdrant unhealthy: {str(e)}"

    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get Qdrant collection info"""
        try:
            info = self._client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
        except Exception as e:
            logger.error(f"Failed to get Qdrant collection info: {e}")
            return {}


class MilvusAdapter(VectorDBAdapter):
    """Milvus vector database adapter (Fallback)"""

    def __init__(self, url: str, collection_name: str, vector_size: int):
        self.url = url
        self.collection_name = collection_name
        self.vector_size = vector_size
        self._connection_alias = "default"
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Milvus client"""
        try:
            from pymilvus import connections

            host, port = self.url.split(":")
            connections.connect(alias=self._connection_alias, host=host, port=int(port))
            logger.info(f"Milvus client initialized: {self.url}")
        except ImportError:
            logger.error("pymilvus not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Milvus client: {e}")
            raise

    async def create_collection(self, collection_name: str, vector_size: int, **kwargs):
        """Create Milvus collection"""
        try:
            from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, utility

            if utility.has_collection(collection_name):
                logger.info(f"Milvus collection already exists: {collection_name}")
                return True

            # Define schema
            fields = [
                FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, max_length=100),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=vector_size),
                FieldSchema(name="payload", dtype=DataType.JSON),
            ]
            schema = CollectionSchema(fields, description="Multimodal RAG collection")

            # Create collection
            collection = Collection(name=collection_name, schema=schema)

            # Create index
            index_params = {
                "index_type": "HNSW",
                "metric_type": "COSINE",
                "params": {"M": 16, "efConstruction": 200},
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            logger.info(f"Created Milvus collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Milvus collection: {e}")
            return False

    async def index_vectors(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> bool:
        """Index vectors in Milvus"""
        try:
            from pymilvus import Collection

            if ids is None:
                import uuid

                ids = [str(uuid.uuid4()) for _ in range(len(vectors))]

            collection = Collection(collection_name)
            entities = [ids, vectors, payloads]

            collection.insert(entities)
            collection.flush()
            logger.info(f"Indexed {len(vectors)} vectors in Milvus")
            return True
        except Exception as e:
            logger.error(f"Failed to index vectors in Milvus: {e}")
            raise

    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search in Milvus"""
        try:
            from pymilvus import Collection

            collection = Collection(collection_name)
            collection.load()

            search_params = {"metric_type": "COSINE", "params": {"ef": 100}}

            # Build filter expression
            expr = None
            if filters:
                filter_exprs = [f'payload["{k}"] == "{v}"' for k, v in filters.items()]
                expr = " && ".join(filter_exprs)

            results = collection.search(
                data=[query_vector],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=["payload"],
            )

            return [
                {
                    "id": str(hit.id),
                    "score": float(hit.distance),
                    "payload": hit.entity.get("payload", {}),
                }
                for hit in results[0]
            ]
        except Exception as e:
            logger.error(f"Failed to search in Milvus: {e}")
            raise

    async def bulk_upsert(
        self, collection_name: str, vectors: List[List[float]], payloads: List[Dict[str, Any]]
    ) -> bool:
        """Bulk upsert in Milvus"""
        return await self.index_vectors(collection_name, vectors, payloads)

    async def delete_by_filter(self, collection_name: str, filters: Dict[str, Any]) -> bool:
        """Delete vectors by filter in Milvus"""
        try:
            from pymilvus import Collection

            collection = Collection(collection_name)

            filter_exprs = [f'payload["{k}"] == "{v}"' for k, v in filters.items()]
            expr = " && ".join(filter_exprs)

            collection.delete(expr)
            logger.info(f"Deleted vectors from Milvus with filter: {filters}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete vectors in Milvus: {e}")
            return False

    async def health_check(self) -> Tuple[bool, str]:
        """Check Milvus health"""
        try:
            from pymilvus import utility

            collections = utility.list_collections()
            return True, f"Milvus healthy, {len(collections)} collections"
        except Exception as e:
            return False, f"Milvus unhealthy: {str(e)}"

    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get Milvus collection info"""
        try:
            from pymilvus import Collection

            collection = Collection(collection_name)
            stats = collection.get_stats()
            return {
                "name": collection_name,
                "row_count": stats.get("row_count", 0),
                "status": "loaded" if collection.is_empty is False else "empty",
            }
        except Exception as e:
            logger.error(f"Failed to get Milvus collection info: {e}")
            return {}


class VectorDBManager:
    """Manages vector DB with automatic failover between Qdrant and Milvus"""

    def __init__(
        self,
        qdrant_url: str,
        milvus_url: str,
        collection_name: str,
        vector_size: int,
        max_retries: int = 3,
        qdrant_api_key: str = None,
    ):
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.max_retries = max_retries

        # Initialize both adapters
        self.qdrant = QdrantAdapter(qdrant_url, collection_name, vector_size, max_retries, qdrant_api_key)
        try:
            self.milvus = MilvusAdapter(milvus_url, collection_name, vector_size)
            self.milvus_available = True
        except Exception as e:
            logger.warning(f"Milvus not available, will use Qdrant only: {e}")
            self.milvus = None
            self.milvus_available = False

        # Start with Qdrant
        self.active_adapter: VectorDBAdapter = self.qdrant
        self.active_db = "qdrant"
        self.failure_count = 0
        self.last_health_check = 0
        self.health_check_interval = 60  # seconds

    async def _check_and_failover(self) -> bool:
        """Check health and failover if needed"""
        current_time = time.time()

        # Rate limit health checks
        if current_time - self.last_health_check < self.health_check_interval:
            return True

        self.last_health_check = current_time

        # Check current adapter health
        healthy, message = await self.active_adapter.health_check()

        if healthy:
            self.failure_count = 0
            return True

        logger.warning(f"{self.active_db} health check failed: {message}")
        self.failure_count += 1

        # Failover after max_retries failures
        if self.failure_count >= self.max_retries:
            if self.active_db == "qdrant" and self.milvus_available:
                logger.warning("Failing over from Qdrant to Milvus")
                self.active_adapter = self.milvus
                self.active_db = "milvus"
                self.failure_count = 0
                return True
            elif self.active_db == "milvus":
                logger.warning("Failing back to Qdrant")
                self.active_adapter = self.qdrant
                self.active_db = "qdrant"
                self.failure_count = 0
                return True

        return False

    async def create_collection(self, **kwargs) -> bool:
        """Create collection on active adapter"""
        await self._check_and_failover()
        return await self.active_adapter.create_collection(
            self.collection_name, self.vector_size, **kwargs
        )

    async def index_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
    ) -> bool:
        """Index vectors on active adapter"""
        await self._check_and_failover()
        return await self.active_adapter.index_vectors(
            self.collection_name, vectors, payloads, ids
        )

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Search on active adapter"""
        await self._check_and_failover()
        return await self.active_adapter.search(self.collection_name, query_vector, top_k, filters)

    async def bulk_upsert(
        self, vectors: List[List[float]], payloads: List[Dict[str, Any]]
    ) -> bool:
        """Bulk upsert on active adapter"""
        await self._check_and_failover()
        return await self.active_adapter.bulk_upsert(self.collection_name, vectors, payloads)

    async def delete_by_filter(self, filters: Dict[str, Any]) -> bool:
        """Delete by filter on active adapter"""
        await self._check_and_failover()
        return await self.active_adapter.delete_by_filter(self.collection_name, filters)

    async def health_check(self) -> Dict[str, Any]:
        """Get health status of all adapters"""
        qdrant_health, qdrant_msg = await self.qdrant.health_check()

        milvus_health, milvus_msg = False, "Not configured"
        if self.milvus_available:
            milvus_health, milvus_msg = await self.milvus.health_check()

        return {
            "active_db": self.active_db,
            "qdrant": {"healthy": qdrant_health, "message": qdrant_msg},
            "milvus": {
                "healthy": milvus_health,
                "message": milvus_msg,
                "available": self.milvus_available,
            },
        }

    async def get_collection_info(self) -> Dict[str, Any]:
        """Get collection info from active adapter"""
        return await self.active_adapter.get_collection_info(self.collection_name)

    def get_active_db(self) -> str:
        """Get name of active database"""
        return self.active_db
