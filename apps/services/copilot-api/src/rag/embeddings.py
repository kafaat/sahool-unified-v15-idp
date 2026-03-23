"""
Embedding Service for Copilot RAG
خدمة التضمينات لـ Copilot RAG

Provides unified embedding generation with multiple providers.
Supports offline-first with local models.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import hashlib
import os
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class EmbeddingProvider(StrEnum):
    """Supported embedding providers"""

    SENTENCE_TRANSFORMERS = "sentence_transformers"
    OLLAMA = "ollama"
    OPENAI = "openai"


@dataclass
class EmbeddingConfig:
    """Configuration for embedding service"""

    provider: EmbeddingProvider = EmbeddingProvider.SENTENCE_TRANSFORMERS
    model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    ollama_base_url: str = "http://localhost:11434"
    openai_api_key: str | None = None
    batch_size: int = 32
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600
    cache_max_size: int = 10000

    def __post_init__(self):
        """Load from environment variables"""
        if self.openai_api_key is None:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")

        env_provider = os.getenv("COPILOT_EMBEDDING_PROVIDER")
        if env_provider:
            try:
                self.provider = EmbeddingProvider(env_provider.lower())
            except ValueError:
                pass

        env_model = os.getenv("COPILOT_EMBEDDING_MODEL")
        if env_model:
            self.model = env_model


@dataclass
class EmbeddingResult:
    """Result of embedding operation"""

    embedding: list[float]
    text: str
    dimension: int
    latency_ms: float
    cached: bool = False
    provider: str = ""
    model: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class EmbeddingService:
    """
    Unified embedding service with caching and fallback.
    خدمة تضمينات موحدة مع تخزين مؤقت واحتياطي

    Supports:
    - Sentence Transformers (local, offline-first)
    - Ollama (local LLM)
    - OpenAI (cloud, optional)
    """

    def __init__(self, config: EmbeddingConfig | None = None):
        """Initialize embedding service"""
        self.config = config or EmbeddingConfig()
        self._cache: OrderedDict[str, tuple[list[float], float]] = OrderedDict()
        self._model = None
        self._initialized = False
        self._dimension: int | None = None

    async def initialize(self) -> bool:
        """Initialize the embedding model"""
        if self._initialized:
            return True

        try:
            if self.config.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
                return await self._init_sentence_transformers()
            elif self.config.provider == EmbeddingProvider.OLLAMA:
                return await self._init_ollama()
            elif self.config.provider == EmbeddingProvider.OPENAI:
                return await self._init_openai()
            else:
                logger.error("Unknown embedding provider", provider=self.config.provider)
                return False
        except Exception as e:
            logger.error("Failed to initialize embedding service", error=str(e))
            return False

    async def _init_sentence_transformers(self) -> bool:
        """Initialize Sentence Transformers model"""
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.model)
            self._dimension = self._model.get_sentence_embedding_dimension()
            self._initialized = True
            logger.info(
                "Sentence Transformers initialized",
                model=self.config.model,
                dimension=self._dimension,
            )
            return True
        except ImportError:
            logger.warning("sentence-transformers not installed, using fallback")
            return await self._fallback_init()
        except Exception as e:
            logger.error("Failed to load Sentence Transformers", error=str(e))
            return await self._fallback_init()

    async def _init_ollama(self) -> bool:
        """Initialize Ollama embedding"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.config.ollama_base_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    self._initialized = True
                    self._dimension = 4096  # Default for nomic-embed-text
                    logger.info("Ollama initialized", url=self.config.ollama_base_url)
                    return True
        except Exception as e:
            logger.warning("Ollama not available", error=str(e))
        return await self._fallback_init()

    async def _init_openai(self) -> bool:
        """Initialize OpenAI embedding"""
        if not self.config.openai_api_key:
            logger.warning("OpenAI API key not provided")
            return await self._fallback_init()

        self._initialized = True
        self._dimension = 1536  # text-embedding-3-small
        logger.info("OpenAI embedding initialized")
        return True

    async def _fallback_init(self) -> bool:
        """Fallback to simple word-based embedding"""
        logger.warning("Using fallback word-based embedding")
        self._dimension = 384
        self._initialized = True
        self.config.provider = EmbeddingProvider.SENTENCE_TRANSFORMERS
        return True

    async def embed(self, text: str) -> EmbeddingResult:
        """
        Generate embedding for text.
        توليد تضمين للنص

        Args:
            text: Text to embed

        Returns:
            EmbeddingResult with vector
        """
        if not self._initialized:
            await self.initialize()

        start_time = time.time()

        # Check cache
        cache_key = self._get_cache_key(text)
        if self.config.cache_enabled and cache_key in self._cache:
            embedding, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self.config.cache_ttl_seconds:
                # Move to end for LRU ordering
                self._cache.move_to_end(cache_key)
                return EmbeddingResult(
                    embedding=embedding,
                    text=text,
                    dimension=len(embedding),
                    latency_ms=(time.time() - start_time) * 1000,
                    cached=True,
                    provider=self.config.provider.value,
                    model=self.config.model,
                )
            else:
                # Expired entry, remove it
                del self._cache[cache_key]

        # Generate embedding
        if self.config.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS:
            embedding = await self._embed_sentence_transformers(text)
        elif self.config.provider == EmbeddingProvider.OLLAMA:
            embedding = await self._embed_ollama(text)
        elif self.config.provider == EmbeddingProvider.OPENAI:
            embedding = await self._embed_openai(text)
        else:
            embedding = self._embed_fallback(text)

        # Cache result with LRU eviction
        if self.config.cache_enabled:
            self._cache[cache_key] = (embedding, time.time())
            self._cache.move_to_end(cache_key)
            # Purge expired entries before size-based eviction so that stale
            # items don't count toward cache_max_size and cause unnecessary churn.
            now = time.time()
            expired_keys = [k for k, (_, ts) in self._cache.items() if now - ts >= self.config.cache_ttl_seconds]
            for k in expired_keys:
                del self._cache[k]
            # Evict oldest live entries if cache still exceeds max size
            while len(self._cache) > self.config.cache_max_size:
                self._cache.popitem(last=False)

        latency_ms = (time.time() - start_time) * 1000

        return EmbeddingResult(
            embedding=embedding,
            text=text,
            dimension=len(embedding),
            latency_ms=latency_ms,
            cached=False,
            provider=self.config.provider.value,
            model=self.config.model,
        )

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        Generate embeddings for multiple texts.
        توليد تضمينات لنصوص متعددة
        """
        results = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i : i + self.config.batch_size]
            for text in batch:
                result = await self.embed(text)
                results.append(result)
        return results

    async def _embed_sentence_transformers(self, text: str) -> list[float]:
        """Generate embedding using Sentence Transformers"""
        if self._model is None:
            return self._embed_fallback(text)

        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    async def _embed_ollama(self, text: str) -> list[float]:
        """Generate embedding using Ollama"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.config.ollama_base_url}/api/embeddings",
                    json={
                        "model": self.config.model,
                        "prompt": text,
                    },
                    timeout=30.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("embedding", [])
        except Exception as e:
            logger.error("Ollama embedding failed", error=str(e))

        return self._embed_fallback(text)

    async def _embed_openai(self, text: str) -> list[float]:
        """Generate embedding using OpenAI"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.config.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "text-embedding-3-small",
                        "input": text,
                    },
                    timeout=30.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data["data"][0]["embedding"]
        except Exception as e:
            logger.error("OpenAI embedding failed", error=str(e))

        return self._embed_fallback(text)

    def _embed_fallback(self, text: str) -> list[float]:
        """
        Fallback word-based embedding using hash.
        تضمين احتياطي قائم على الكلمات
        """
        import math

        # Simple bag-of-words with hash-based features
        words = text.lower().split()
        dimension = self._dimension or 384
        embedding = [0.0] * dimension

        for i, word in enumerate(words):
            # Hash word to get index
            word_hash = int(hashlib.md5(word.encode(), usedforsecurity=False).hexdigest(), 16)
            idx = word_hash % dimension
            # Add position-weighted value
            embedding[idx] += 1.0 / (1 + i * 0.1)

        # Normalize
        norm = math.sqrt(sum(x * x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]

        return embedding

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(
            f"{self.config.provider}:{self.config.model}:{text}".encode(), usedforsecurity=False
        ).hexdigest()

    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return self._dimension or 384

    def clear_cache(self) -> None:
        """Clear embedding cache"""
        self._cache.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get or create global embedding service"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
