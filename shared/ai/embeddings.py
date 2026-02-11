"""
Embeddings Adapter Module
=========================
محول التضمينات - واجهة موحدة لمزودي التضمينات

Unified interface for embedding providers supporting:
- Sentence Transformers (local, offline-first)
- OpenAI Embeddings
- Ollama Embeddings
- Google/Vertex AI Embeddings

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import hashlib
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class EmbeddingProvider(StrEnum):
    """Supported embedding providers | مزودي التضمينات المدعومين"""

    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OLLAMA = "ollama"
    OPENAI = "openai"
    GOOGLE = "google"
    HUGGINGFACE = "huggingface"  # New: Huggingface models with Arabic support


@dataclass
class EmbeddingConfig:
    """Configuration for embedding providers | إعدادات مزودي التضمينات"""

    # Provider settings
    provider: EmbeddingProvider = EmbeddingProvider.SENTENCE_TRANSFORMERS
    model: str = "all-MiniLM-L6-v2"

    # API settings (for cloud providers)
    api_key: str | None = None
    api_base_url: str | None = None

    # Local settings (for Ollama/SentenceTransformers)
    ollama_base_url: str = "http://localhost:11434"

    # Performance settings
    batch_size: int = 32
    max_retries: int = 3
    timeout_seconds: float = 30.0

    # Caching settings
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour

    # Dimension settings (auto-detected if not specified)
    embedding_dimension: int | None = None

    # Huggingface settings
    huggingface_api_token: str | None = None
    huggingface_use_local: bool = True  # Use local models by default (offline-first)

    def __post_init__(self):
        """Load API keys from environment if not provided"""
        if self.api_key is None:
            if self.provider == EmbeddingProvider.OPENAI:
                self.api_key = os.getenv("OPENAI_API_KEY")
            elif self.provider == EmbeddingProvider.GOOGLE:
                self.api_key = os.getenv("GOOGLE_API_KEY")

        if self.huggingface_api_token is None:
            self.huggingface_api_token = os.getenv("HUGGINGFACE_API_TOKEN")


@dataclass
class EmbeddingResult:
    """Result of an embedding operation | نتيجة عملية التضمين"""

    # The embedding vector
    embedding: list[float]

    # Metadata
    text: str
    provider: EmbeddingProvider
    model: str
    dimension: int

    # Performance metrics
    latency_ms: float
    cached: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "embedding": self.embedding,
            "text": self.text,
            "provider": self.provider.value,
            "model": self.model,
            "dimension": self.dimension,
            "latency_ms": self.latency_ms,
            "cached": self.cached,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class BatchEmbeddingResult:
    """Result of batch embedding operation | نتيجة عملية التضمين الدفعية"""

    embeddings: list[EmbeddingResult]
    total_texts: int
    successful: int
    failed: int
    total_latency_ms: float
    provider: EmbeddingProvider
    model: str

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_texts == 0:
            return 0.0
        return self.successful / self.total_texts

    def get_vectors(self) -> list[list[float]]:
        """Get just the embedding vectors"""
        return [r.embedding for r in self.embeddings]


class EmbeddingProviderError(Exception):
    """Error from embedding provider | خطأ من مزود التضمينات"""

    def __init__(
        self,
        message: str,
        provider: EmbeddingProvider,
        recoverable: bool = True,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.provider = provider
        self.recoverable = recoverable
        self.original_error = original_error


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers | الصنف الأساسي لمزودي التضمينات"""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text"""
        pass

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts"""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Get the embedding dimension for the model"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available"""
        pass


class EmbeddingCache:
    """Simple in-memory cache for embeddings | ذاكرة تخزين مؤقت للتضمينات"""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 10000):
        self._cache: dict[str, tuple[list[float], float]] = {}
        self._ttl = ttl_seconds
        self._max_size = max_size

    def _hash_text(self, text: str, model: str) -> str:
        """Create a hash key for the text"""
        content = f"{model}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def get(self, text: str, model: str) -> list[float] | None:
        """Get cached embedding if exists and not expired"""
        key = self._hash_text(text, model)
        if key in self._cache:
            embedding, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return embedding
            else:
                del self._cache[key]
        return None

    def set(self, text: str, model: str, embedding: list[float]) -> None:
        """Cache an embedding"""
        if len(self._cache) >= self._max_size:
            # Remove oldest entries (simple LRU)
            oldest = sorted(self._cache.items(), key=lambda x: x[1][1])[:100]
            for key, _ in oldest:
                del self._cache[key]

        key = self._hash_text(text, model)
        self._cache[key] = (embedding, time.time())

    def clear(self) -> None:
        """Clear all cached embeddings"""
        self._cache.clear()

    @property
    def size(self) -> int:
        """Get current cache size"""
        return len(self._cache)


class EmbeddingsAdapter:
    """
    Unified adapter for embedding providers
    محول موحد لمزودي التضمينات

    Features:
    - Offline-first: Sentence Transformers/Ollama priority
    - Automatic fallback between providers
    - Caching for performance
    - Batch processing
    - Bilingual support (Arabic/English)

    Usage:
        adapter = EmbeddingsAdapter()

        # Single embedding
        result = await adapter.embed("Agricultural advisory text")

        # Batch embedding
        results = await adapter.embed_batch([
            "Wheat irrigation schedule",
            "جدول ري القمح"
        ])

        # Semantic similarity
        similarity = await adapter.similarity(
            "wheat disease",
            "مرض القمح"
        )
    """

    # Model dimensions for common models
    MODEL_DIMENSIONS: dict[str, int] = {
        # Sentence Transformers
        "all-MiniLM-L6-v2": 384,
        "all-mpnet-base-v2": 768,
        "paraphrase-multilingual-MiniLM-L12-v2": 384,
        "distiluse-base-multilingual-cased-v2": 512,
        # Ollama
        "nomic-embed-text": 768,
        "mxbai-embed-large": 1024,
        # OpenAI
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
        # Google
        "textembedding-gecko": 768,
        "textembedding-gecko-multilingual": 768,
        # Huggingface - Multilingual (Arabic support)
        "intfloat/multilingual-e5-large": 1024,
        "intfloat/multilingual-e5-base": 768,
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2": 768,
        # Huggingface - Arabic-specific
        "aubmindlab/bert-base-arabertv02": 768,
        "UBC-NLP/MARBERT": 768,
        # Huggingface - English
        "sentence-transformers/all-MiniLM-L6-v2": 384,
        "sentence-transformers/all-mpnet-base-v2": 768,
        "BAAI/bge-large-en-v1.5": 1024,
    }

    def __init__(self, config: EmbeddingConfig | None = None):
        """Initialize the embeddings adapter"""
        self.config = config or EmbeddingConfig()
        self._cache = (
            EmbeddingCache(ttl_seconds=self.config.cache_ttl_seconds)
            if self.config.cache_enabled
            else None
        )

        # Provider availability flags
        self._sentence_transformers_available: bool | None = None
        self._ollama_available: bool | None = None

        # Lazy-loaded provider clients
        self._st_model = None
        self._http_client = None

    async def embed(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for a single text
        توليد تضمين لنص واحد

        Args:
            text: The text to embed

        Returns:
            EmbeddingResult with embedding vector and metadata
        """
        start_time = time.time()

        # Check cache first
        if self._cache:
            cached = self._cache.get(text, self.config.model)
            if cached:
                latency = (time.time() - start_time) * 1000
                return EmbeddingResult(
                    embedding=cached,
                    text=text,
                    provider=self.config.provider,
                    model=self.config.model,
                    dimension=len(cached),
                    latency_ms=latency,
                    cached=True,
                )

        # Generate embedding based on provider
        embedding = await self._generate_embedding(text)
        latency = (time.time() - start_time) * 1000

        # Cache the result
        if self._cache:
            self._cache.set(text, self.config.model, embedding)

        return EmbeddingResult(
            embedding=embedding,
            text=text,
            provider=self.config.provider,
            model=self.config.model,
            dimension=len(embedding),
            latency_ms=latency,
            cached=False,
        )

    async def embed_batch(
        self,
        texts: list[str],
        show_progress: bool = False,
    ) -> BatchEmbeddingResult:
        """
        Generate embeddings for multiple texts
        توليد تضمينات لنصوص متعددة

        Args:
            texts: List of texts to embed
            show_progress: Whether to log progress

        Returns:
            BatchEmbeddingResult with all embeddings
        """
        start_time = time.time()
        results: list[EmbeddingResult] = []
        failed = 0

        # Process in batches
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i : i + self.config.batch_size]
            batch_results = []

            for text in batch:
                try:
                    result = await self.embed(text)
                    batch_results.append(result)
                except EmbeddingProviderError:
                    failed += 1

            results.extend(batch_results)

        total_latency = (time.time() - start_time) * 1000

        return BatchEmbeddingResult(
            embeddings=results,
            total_texts=len(texts),
            successful=len(results),
            failed=failed,
            total_latency_ms=total_latency,
            provider=self.config.provider,
            model=self.config.model,
        )

    async def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        حساب التشابه بين نصين

        Args:
            text1: First text
            text2: Second text

        Returns:
            Cosine similarity score (0 to 1)
        """
        emb1 = await self.embed(text1)
        emb2 = await self.embed(text2)

        return self._cosine_similarity(emb1.embedding, emb2.embedding)

    async def find_most_similar(
        self,
        query: str,
        candidates: list[str],
        top_k: int = 5,
    ) -> list[tuple[str, float]]:
        """
        Find most similar texts to a query
        إيجاد النصوص الأكثر تشابهاً مع استعلام

        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of top results to return

        Returns:
            List of (text, similarity) tuples sorted by similarity
        """
        query_result = await self.embed(query)
        candidate_results = await self.embed_batch(candidates)

        similarities = []
        for i, result in enumerate(candidate_results.embeddings):
            sim = self._cosine_similarity(query_result.embedding, result.embedding)
            similarities.append((candidates[i], sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    async def _generate_embedding(self, text: str) -> list[float]:
        """Generate embedding using configured provider"""
        provider = self.config.provider

        if provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
            return await self._embed_sentence_transformers(text)
        elif provider == EmbeddingProvider.OLLAMA:
            return await self._embed_ollama(text)
        elif provider == EmbeddingProvider.OPENAI:
            return await self._embed_openai(text)
        elif provider == EmbeddingProvider.GOOGLE:
            return await self._embed_google(text)
        elif provider == EmbeddingProvider.HUGGINGFACE:
            return await self._embed_huggingface(text)
        else:
            raise EmbeddingProviderError(
                f"Unknown provider: {provider}",
                provider=provider,
                recoverable=False,
            )

    async def _embed_sentence_transformers(self, text: str) -> list[float]:
        """Generate embedding using Sentence Transformers (local)"""
        try:
            if self._st_model is None:
                # Lazy import to avoid dependency issues
                try:
                    from sentence_transformers import SentenceTransformer

                    self._st_model = SentenceTransformer(self.config.model)
                except ImportError:
                    raise EmbeddingProviderError(
                        "sentence-transformers not installed. Install with: pip install sentence-transformers",
                        provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                        recoverable=False,
                    )

            # Generate embedding (synchronous but fast for single texts)
            embedding = self._st_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()

        except EmbeddingProviderError:
            raise
        except Exception as e:
            raise EmbeddingProviderError(
                f"Sentence Transformers error: {str(e)}",
                provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                original_error=e,
            )

    async def _embed_ollama(self, text: str) -> list[float]:
        """Generate embedding using Ollama (local)"""
        try:
            if self._http_client is None:
                try:
                    import httpx

                    self._http_client = httpx.AsyncClient(timeout=self.config.timeout_seconds)
                except ImportError:
                    raise EmbeddingProviderError(
                        "httpx not installed. Install with: pip install httpx",
                        provider=EmbeddingProvider.OLLAMA,
                        recoverable=False,
                    )

            url = f"{self.config.ollama_base_url}/api/embeddings"
            response = await self._http_client.post(
                url,
                json={"model": self.config.model, "prompt": text},
            )
            response.raise_for_status()

            data = response.json()
            return data["embedding"]

        except EmbeddingProviderError:
            raise
        except Exception as e:
            raise EmbeddingProviderError(
                f"Ollama error: {str(e)}",
                provider=EmbeddingProvider.OLLAMA,
                original_error=e,
            )

    async def _embed_openai(self, text: str) -> list[float]:
        """Generate embedding using OpenAI API"""
        try:
            if not self.config.api_key:
                raise EmbeddingProviderError(
                    "OpenAI API key not configured",
                    provider=EmbeddingProvider.OPENAI,
                    recoverable=False,
                )

            if self._http_client is None:
                import httpx

                self._http_client = httpx.AsyncClient(timeout=self.config.timeout_seconds)

            url = "https://api.openai.com/v1/embeddings"
            response = await self._http_client.post(
                url,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": self.config.model, "input": text},
            )
            response.raise_for_status()

            data = response.json()
            return data["data"][0]["embedding"]

        except EmbeddingProviderError:
            raise
        except Exception as e:
            raise EmbeddingProviderError(
                f"OpenAI error: {str(e)}",
                provider=EmbeddingProvider.OPENAI,
                original_error=e,
            )

    async def _embed_google(self, text: str) -> list[float]:
        """Generate embedding using Google/Vertex AI"""
        try:
            if not self.config.api_key:
                raise EmbeddingProviderError(
                    "Google API key not configured",
                    provider=EmbeddingProvider.GOOGLE,
                    recoverable=False,
                )

            if self._http_client is None:
                import httpx

                self._http_client = httpx.AsyncClient(timeout=self.config.timeout_seconds)

            url = f"https://generativelanguage.googleapis.com/v1/models/{self.config.model}:embedContent"
            response = await self._http_client.post(
                url,
                params={"key": self.config.api_key},
                json={"content": {"parts": [{"text": text}]}},
            )
            response.raise_for_status()

            data = response.json()
            return data["embedding"]["values"]

        except EmbeddingProviderError:
            raise
        except Exception as e:
            raise EmbeddingProviderError(
                f"Google error: {str(e)}",
                provider=EmbeddingProvider.GOOGLE,
                original_error=e,
            )

    async def _embed_huggingface(self, text: str) -> list[float]:
        """Generate embedding using Huggingface (local or API)

        توليد التضمين باستخدام Huggingface
        """
        try:
            # Try to use the HuggingfaceProvider from our module
            from .huggingface_provider import (
                HuggingfaceConfig,
                HuggingfaceProvider,
            )

            # Lazy initialize provider
            if not hasattr(self, "_hf_provider") or self._hf_provider is None:
                hf_config = HuggingfaceConfig(
                    api_token=self.config.huggingface_api_token,
                    default_embedding_model=self.config.model,
                    use_local_models=self.config.huggingface_use_local,
                    cache_enabled=self.config.cache_enabled,
                )
                self._hf_provider = HuggingfaceProvider(hf_config)

            result = await self._hf_provider.embed(text, self.config.model)
            return result.embedding

        except ImportError:
            # Fallback to direct API call if huggingface_provider not available
            try:
                if self._http_client is None:
                    import httpx

                    self._http_client = httpx.AsyncClient(timeout=self.config.timeout_seconds)

                url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.config.model}"
                headers = {}
                if self.config.huggingface_api_token:
                    headers["Authorization"] = f"Bearer {self.config.huggingface_api_token}"

                response = await self._http_client.post(
                    url,
                    headers=headers,
                    json={"inputs": text, "options": {"wait_for_model": True}},
                )
                response.raise_for_status()

                data = response.json()

                # Handle different response formats
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], list):
                        # Token-level embeddings - mean pool
                        return [sum(col) / len(data) for col in zip(*data)]
                    return data

                raise EmbeddingProviderError(
                    f"Unexpected Huggingface response format: {type(data)}",
                    provider=EmbeddingProvider.HUGGINGFACE,
                )

            except Exception as e:
                raise EmbeddingProviderError(
                    f"Huggingface error: {str(e)}",
                    provider=EmbeddingProvider.HUGGINGFACE,
                    original_error=e,
                )

        except EmbeddingProviderError:
            raise
        except Exception as e:
            raise EmbeddingProviderError(
                f"Huggingface error: {str(e)}",
                provider=EmbeddingProvider.HUGGINGFACE,
                original_error=e,
            )

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def get_dimension(self) -> int:
        """Get embedding dimension for current model"""
        if self.config.embedding_dimension:
            return self.config.embedding_dimension

        return self.MODEL_DIMENSIONS.get(self.config.model, 384)

    async def is_available(self) -> bool:
        """Check if current provider is available"""
        try:
            # Try to embed a simple test text
            await self.embed("test")
            return True
        except Exception:
            return False

    def clear_cache(self) -> None:
        """Clear the embedding cache"""
        if self._cache:
            self._cache.clear()

    @property
    def cache_size(self) -> int:
        """Get current cache size"""
        return self._cache.size if self._cache else 0

    async def close(self) -> None:
        """Close any open connections"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


# Convenience functions
_default_adapter: EmbeddingsAdapter | None = None


def get_embeddings_adapter(config: EmbeddingConfig | None = None) -> EmbeddingsAdapter:
    """Get or create the default embeddings adapter"""
    global _default_adapter
    if _default_adapter is None or config is not None:
        _default_adapter = EmbeddingsAdapter(config)
    return _default_adapter


async def embed_text(text: str) -> EmbeddingResult:
    """Embed a single text using the default adapter"""
    adapter = get_embeddings_adapter()
    return await adapter.embed(text)


async def embed_texts(texts: list[str]) -> BatchEmbeddingResult:
    """Embed multiple texts using the default adapter"""
    adapter = get_embeddings_adapter()
    return await adapter.embed_batch(texts)


async def text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts"""
    adapter = get_embeddings_adapter()
    return await adapter.similarity(text1, text2)
