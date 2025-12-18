"""
Embedder - Text to Vector conversion
محول النصوص إلى متجهات
"""
from abc import ABC, abstractmethod
from typing import List
import numpy as np
from .settings import settings


class BaseEmbedder(ABC):
    """Abstract base class for embedders"""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Embed single text"""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts"""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension"""
        pass


class SentenceTransformersEmbedder(BaseEmbedder):
    """Sentence Transformers based embedder"""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()

    def embed(self, text: str) -> List[float]:
        """Embed single text with normalization"""
        vec = self.model.encode([text], normalize_embeddings=True)[0]
        return vec.astype(np.float32).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts with normalization"""
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return [v.astype(np.float32).tolist() for v in vecs]

    @property
    def dimension(self) -> int:
        return self._dimension


class MockEmbedder(BaseEmbedder):
    """Mock embedder for testing"""

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    def embed(self, text: str) -> List[float]:
        """Generate deterministic mock embedding based on text hash"""
        import hashlib
        hash_bytes = hashlib.sha256(text.encode()).digest()
        # Generate normalized vector from hash
        raw = [b / 255.0 for b in hash_bytes]
        # Extend to required dimension
        vec = (raw * (self._dimension // len(raw) + 1))[:self._dimension]
        # Normalize
        norm = np.linalg.norm(vec)
        return [v / norm for v in vec]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]

    @property
    def dimension(self) -> int:
        return self._dimension


def create_embedder() -> BaseEmbedder:
    """Factory function to create embedder based on settings"""
    if settings.embedding_provider == "sentence_transformers":
        return SentenceTransformersEmbedder(settings.embedding_model)
    elif settings.embedding_provider == "mock":
        return MockEmbedder(settings.embedding_dim)
    else:
        raise ValueError(f"Unknown embedding provider: {settings.embedding_provider}")
