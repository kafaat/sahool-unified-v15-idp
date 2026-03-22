"""
Tests for Embedding Service (rag/embeddings.py)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = [pytest.mark.unit]


class TestEmbeddingProvider:
    def test_all_providers(self):
        from src.rag.embeddings import EmbeddingProvider

        assert EmbeddingProvider.SENTENCE_TRANSFORMERS == "sentence_transformers"
        assert EmbeddingProvider.OLLAMA == "ollama"
        assert EmbeddingProvider.OPENAI == "openai"


class TestEmbeddingConfig:
    def test_defaults(self):
        from src.rag.embeddings import EmbeddingConfig, EmbeddingProvider

        config = EmbeddingConfig()
        assert config.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS
        assert config.batch_size == 32
        assert config.cache_enabled is True
        assert config.cache_max_size == 10000


class TestEmbeddingResult:
    def test_creation(self):
        from src.rag.embeddings import EmbeddingResult

        r = EmbeddingResult(
            embedding=[0.1, 0.2],
            text="test",
            dimension=2,
            latency_ms=1.0,
        )
        assert r.cached is False
        assert r.dimension == 2


class TestEmbeddingService:
    def test_default_dimension(self):
        from src.rag.embeddings import EmbeddingService

        service = EmbeddingService()
        assert service.dimension == 384

    @pytest.mark.asyncio
    async def test_fallback_init(self):
        from src.rag.embeddings import EmbeddingService

        service = EmbeddingService()
        result = await service._fallback_init()
        assert result is True
        assert service._initialized is True
        assert service._dimension == 384

    @pytest.mark.asyncio
    async def test_embed_produces_correct_dimension(self):
        from src.rag.embeddings import EmbeddingService

        service = EmbeddingService()
        await service._fallback_init()
        result = await service.embed("test text")
        assert len(result.embedding) == 384
        assert result.dimension == 384
        assert result.text == "test text"
        assert result.cached is False

    @pytest.mark.asyncio
    async def test_embed_caching(self):
        from src.rag.embeddings import EmbeddingConfig, EmbeddingService

        config = EmbeddingConfig(cache_enabled=True)
        service = EmbeddingService(config)
        await service._fallback_init()

        r1 = await service.embed("hello world")
        assert r1.cached is False

        r2 = await service.embed("hello world")
        assert r2.cached is True
        assert r1.embedding == r2.embedding

    @pytest.mark.asyncio
    async def test_embed_cache_disabled(self):
        from src.rag.embeddings import EmbeddingConfig, EmbeddingService

        config = EmbeddingConfig(cache_enabled=False)
        service = EmbeddingService(config)
        await service._fallback_init()

        r1 = await service.embed("hello")
        r2 = await service.embed("hello")
        assert r1.cached is False
        assert r2.cached is False

    @pytest.mark.asyncio
    async def test_embed_lru_eviction(self):
        from src.rag.embeddings import EmbeddingConfig, EmbeddingService

        config = EmbeddingConfig(cache_enabled=True, cache_max_size=2)
        service = EmbeddingService(config)
        await service._fallback_init()

        await service.embed("a")
        await service.embed("b")
        await service.embed("c")  # evicts "a"

        r = await service.embed("a")
        assert r.cached is False

    @pytest.mark.asyncio
    async def test_embed_cache_ttl_expiry(self):
        from src.rag.embeddings import EmbeddingConfig, EmbeddingService

        config = EmbeddingConfig(cache_enabled=True, cache_ttl_seconds=0)
        service = EmbeddingService(config)
        await service._fallback_init()

        r1 = await service.embed("test")
        assert r1.cached is False

        # With TTL=0, the entry should be expired immediately
        r2 = await service.embed("test")
        assert r2.cached is False

    def test_clear_cache(self):
        from src.rag.embeddings import EmbeddingService

        service = EmbeddingService()
        service._cache["k1"] = ([0.1], time.time())
        service._cache["k2"] = ([0.2], time.time())
        assert len(service._cache) == 2

        service.clear_cache()
        assert len(service._cache) == 0

    def test_get_cache_key_deterministic(self):
        from src.rag.embeddings import EmbeddingService

        service = EmbeddingService()
        k1 = service._get_cache_key("hello")
        k2 = service._get_cache_key("hello")
        assert k1 == k2

    def test_get_cache_key_different_text(self):
        from src.rag.embeddings import EmbeddingService

        service = EmbeddingService()
        k1 = service._get_cache_key("hello")
        k2 = service._get_cache_key("world")
        assert k1 != k2

    @pytest.mark.asyncio
    async def test_embed_fallback_produces_normalized_vector(self):
        from src.rag.embeddings import EmbeddingService
        import math

        service = EmbeddingService()
        await service._fallback_init()

        result = await service.embed("wheat irrigation schedule")
        norm = math.sqrt(sum(x * x for x in result.embedding))
        assert abs(norm - 1.0) < 0.01  # Should be approximately unit vector

    @pytest.mark.asyncio
    async def test_embed_batch(self):
        from src.rag.embeddings import EmbeddingConfig, EmbeddingService

        config = EmbeddingConfig(batch_size=2)
        service = EmbeddingService(config)
        await service._fallback_init()

        results = await service.embed_batch(["a", "b", "c"])
        assert len(results) == 3
        for r in results:
            assert r.dimension == 384

    @pytest.mark.asyncio
    async def test_fallback_init_sets_dimension(self):
        """Fallback init sets dimension to 384."""
        from src.rag.embeddings import EmbeddingService

        service = EmbeddingService()
        result = await service._fallback_init()
        assert result is True
        assert service._dimension == 384
        assert service._initialized is True


class TestGlobalEmbeddingService:
    def test_get_embedding_service(self):
        from src.rag.embeddings import EmbeddingService, get_embedding_service
        import src.rag.embeddings as emod

        emod._embedding_service = None
        s = get_embedding_service()
        assert isinstance(s, EmbeddingService)
        emod._embedding_service = None
