"""
Embedding model wrapper using sentence-transformers
Supports batching and GPU/CPU inference
"""

import logging
from typing import List

import torch

logger = logging.getLogger(__name__)


class Embedder:
    """Wrapper for embedding models"""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", device: str = "cpu", batch_size: int = 32):
        self.model_name = model_name
        self.device = device
        
        # Validate and normalize batch_size
        if batch_size <= 0:
            logger.warning(f"Invalid batch_size {batch_size}, using default 32")
            self.batch_size = 32
        else:
            self.batch_size = batch_size
            
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer

            # Check if GPU is available
            if self.device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU")
                self.device = "cpu"

            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Loaded embedding model: {self.model_name} on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                return []

            # Encode in batches
            embeddings = self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=len(texts) > 100,
                convert_to_numpy=True,
            )

            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to embed texts: {e}")
            raise

    def embed_single(self, text: str) -> List[float]:
        """
        Embed a single text

        Args:
            text: Text string to embed

        Returns:
            Embedding vector
        """
        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else []

    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension"""
        return self.model.get_sentence_embedding_dimension()

    @property
    def dimension(self) -> int:
        """Alias for get_embedding_dimension"""
        return self.get_embedding_dimension()

    @property
    def embedding_dim(self) -> int:
        """Get the embedding dimension (property for tests)"""
        return self.get_embedding_dimension()
