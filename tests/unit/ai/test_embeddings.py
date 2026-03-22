"""
Tests for Embeddings Adapter Module
اختبارات وحدة محول التضمينات
"""

import math
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.ai.embeddings import (
    BatchEmbeddingResult,
    EmbeddingCache,
    EmbeddingConfig,
    EmbeddingProvider,
    EmbeddingProviderError,
    EmbeddingResult,
    EmbeddingsAdapter,
    embed_text,
    embed_texts,
    get_embeddings_adapter,
    text_similarity,
)


class TestEmbeddingConfig:
    """Tests for EmbeddingConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = EmbeddingConfig()
        assert config.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS
        assert config.model == "all-MiniLM-L6-v2"
        assert config.batch_size == 32
        assert config.cache_enabled is True
        assert config.cache_ttl_seconds == 3600

    def test_custom_config(self):
        """Test custom configuration"""
        config = EmbeddingConfig(
            provider=EmbeddingProvider.OLLAMA,
            model="nomic-embed-text",
            batch_size=16,
            cache_enabled=False,
        )
        assert config.provider == EmbeddingProvider.OLLAMA
        assert config.model == "nomic-embed-text"
        assert config.batch_size == 16
        assert config.cache_enabled is False

    def test_config_with_api_key(self):
        """Test configuration with API key"""
        config = EmbeddingConfig(
            provider=EmbeddingProvider.OPENAI,
            api_key="test-key",
        )
        assert config.api_key == "test-key"

    def test_config_loads_env_vars(self):
        """Test that config loads API keys from environment"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "env-test-key"}):
            config = EmbeddingConfig(provider=EmbeddingProvider.OPENAI)
            assert config.api_key == "env-test-key"


class TestEmbeddingResult:
    """Tests for EmbeddingResult"""

    def test_create_result(self):
        """Test creating an embedding result"""
        result = EmbeddingResult(
            embedding=[0.1, 0.2, 0.3],
            text="test text",
            provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
            model="all-MiniLM-L6-v2",
            dimension=3,
            latency_ms=10.5,
        )
        assert result.embedding == [0.1, 0.2, 0.3]
        assert result.text == "test text"
        assert result.dimension == 3
        assert result.latency_ms == 10.5
        assert result.cached is False

    def test_result_to_dict(self):
        """Test converting result to dictionary"""
        result = EmbeddingResult(
            embedding=[0.1, 0.2],
            text="test",
            provider=EmbeddingProvider.OLLAMA,
            model="test-model",
            dimension=2,
            latency_ms=5.0,
            cached=True,
        )
        d = result.to_dict()
        assert d["embedding"] == [0.1, 0.2]
        assert d["provider"] == "ollama"
        assert d["cached"] is True


class TestBatchEmbeddingResult:
    """Tests for BatchEmbeddingResult"""

    def test_batch_result_success_rate(self):
        """Test success rate calculation"""
        embeddings = [
            EmbeddingResult(
                embedding=[0.1],
                text="t1",
                provider=EmbeddingProvider.OLLAMA,
                model="m",
                dimension=1,
                latency_ms=1.0,
            ),
            EmbeddingResult(
                embedding=[0.2],
                text="t2",
                provider=EmbeddingProvider.OLLAMA,
                model="m",
                dimension=1,
                latency_ms=1.0,
            ),
        ]
        result = BatchEmbeddingResult(
            embeddings=embeddings,
            total_texts=3,
            successful=2,
            failed=1,
            total_latency_ms=10.0,
            provider=EmbeddingProvider.OLLAMA,
            model="m",
        )
        assert result.success_rate == pytest.approx(2 / 3)

    def test_batch_result_get_vectors(self):
        """Test getting vectors from batch result"""
        embeddings = [
            EmbeddingResult(
                embedding=[0.1, 0.2],
                text="t1",
                provider=EmbeddingProvider.OLLAMA,
                model="m",
                dimension=2,
                latency_ms=1.0,
            ),
            EmbeddingResult(
                embedding=[0.3, 0.4],
                text="t2",
                provider=EmbeddingProvider.OLLAMA,
                model="m",
                dimension=2,
                latency_ms=1.0,
            ),
        ]
        result = BatchEmbeddingResult(
            embeddings=embeddings,
            total_texts=2,
            successful=2,
            failed=0,
            total_latency_ms=5.0,
            provider=EmbeddingProvider.OLLAMA,
            model="m",
        )
        vectors = result.get_vectors()
        assert len(vectors) == 2
        assert vectors[0] == [0.1, 0.2]
        assert vectors[1] == [0.3, 0.4]


class TestEmbeddingCache:
    """Tests for EmbeddingCache"""

    def test_cache_set_and_get(self):
        """Test basic cache operations"""
        cache = EmbeddingCache(ttl_seconds=3600)
        embedding = [0.1, 0.2, 0.3]
        cache.set("test text", "model", embedding)

        result = cache.get("test text", "model")
        assert result == embedding

    def test_cache_miss(self):
        """Test cache miss returns None"""
        cache = EmbeddingCache()
        result = cache.get("nonexistent", "model")
        assert result is None

    def test_cache_different_models(self):
        """Test cache differentiates by model"""
        cache = EmbeddingCache()
        cache.set("text", "model1", [0.1])
        cache.set("text", "model2", [0.2])

        assert cache.get("text", "model1") == [0.1]
        assert cache.get("text", "model2") == [0.2]

    def test_cache_clear(self):
        """Test clearing cache"""
        cache = EmbeddingCache()
        cache.set("text", "model", [0.1])
        assert cache.size == 1

        cache.clear()
        assert cache.size == 0
        assert cache.get("text", "model") is None

    def test_cache_size_limit(self):
        """Test cache respects size limit"""
        cache = EmbeddingCache(max_size=10)
        for i in range(15):
            cache.set(f"text{i}", "model", [float(i)])

        # Cache should have removed some entries
        assert cache.size <= 10


class TestEmbeddingsAdapter:
    """Tests for EmbeddingsAdapter"""

    @pytest.fixture
    def adapter(self):
        """Create adapter with default config"""
        return EmbeddingsAdapter()

    @pytest.fixture
    def adapter_no_cache(self):
        """Create adapter without caching"""
        config = EmbeddingConfig(cache_enabled=False)
        return EmbeddingsAdapter(config)

    def test_adapter_creation(self, adapter):
        """Test adapter creation"""
        assert adapter.config is not None
        assert adapter.config.provider == EmbeddingProvider.SENTENCE_TRANSFORMERS

    def test_get_dimension(self, adapter):
        """Test getting embedding dimension"""
        dim = adapter.get_dimension()
        assert dim == 384  # Default for all-MiniLM-L6-v2

    def test_get_dimension_custom_model(self):
        """Test dimension for custom model"""
        config = EmbeddingConfig(model="all-mpnet-base-v2")
        adapter = EmbeddingsAdapter(config)
        assert adapter.get_dimension() == 768

    def test_model_dimensions_dict(self):
        """Test model dimensions dictionary"""
        assert EmbeddingsAdapter.MODEL_DIMENSIONS["all-MiniLM-L6-v2"] == 384
        assert EmbeddingsAdapter.MODEL_DIMENSIONS["text-embedding-3-small"] == 1536
        assert EmbeddingsAdapter.MODEL_DIMENSIONS["nomic-embed-text"] == 768

    def test_cosine_similarity(self, adapter):
        """Test cosine similarity calculation"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        sim = adapter._cosine_similarity(vec1, vec2)
        assert sim == pytest.approx(1.0)

        vec3 = [0.0, 1.0, 0.0]
        sim = adapter._cosine_similarity(vec1, vec3)
        assert sim == pytest.approx(0.0)

        vec4 = [-1.0, 0.0, 0.0]
        sim = adapter._cosine_similarity(vec1, vec4)
        assert sim == pytest.approx(-1.0)

    def test_cosine_similarity_zero_vector(self, adapter):
        """Test cosine similarity with zero vector"""
        vec1 = [1.0, 2.0]
        vec2 = [0.0, 0.0]
        sim = adapter._cosine_similarity(vec1, vec2)
        assert sim == 0.0

    @pytest.mark.asyncio
    async def test_embed_with_cache(self):
        """Test embedding with caching"""
        config = EmbeddingConfig(cache_enabled=True)
        adapter = EmbeddingsAdapter(config)

        # Mock the embedding generation
        mock_embedding = [0.1, 0.2, 0.3]
        adapter._generate_embedding = AsyncMock(return_value=mock_embedding)

        # First call - should generate
        result1 = await adapter.embed("test text")
        assert result1.embedding == mock_embedding
        assert result1.cached is False

        # Second call - should use cache
        result2 = await adapter.embed("test text")
        assert result2.embedding == mock_embedding
        assert result2.cached is True

        # Generation should only be called once
        assert adapter._generate_embedding.call_count == 1

    @pytest.mark.asyncio
    async def test_embed_batch(self):
        """Test batch embedding"""
        adapter = EmbeddingsAdapter()
        adapter._generate_embedding = AsyncMock(
            side_effect=[
                [0.1, 0.2],
                [0.3, 0.4],
                [0.5, 0.6],
            ]
        )

        texts = ["text1", "text2", "text3"]
        result = await adapter.embed_batch(texts)

        assert result.total_texts == 3
        assert result.successful == 3
        assert result.failed == 0
        assert len(result.embeddings) == 3

    @pytest.mark.asyncio
    async def test_similarity(self):
        """Test similarity calculation between texts"""
        adapter = EmbeddingsAdapter()
        adapter._generate_embedding = AsyncMock(
            side_effect=[
                [1.0, 0.0, 0.0],
                [0.707, 0.707, 0.0],
            ]
        )

        sim = await adapter.similarity("text1", "text2")
        assert 0.0 <= sim <= 1.0

    @pytest.mark.asyncio
    async def test_find_most_similar(self):
        """Test finding most similar texts"""
        adapter = EmbeddingsAdapter()

        # Mock embeddings - query and 3 candidates
        adapter.embed = AsyncMock(
            side_effect=[
                EmbeddingResult(
                    embedding=[1.0, 0.0],
                    text="query",
                    provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                    model="m",
                    dimension=2,
                    latency_ms=1.0,
                ),
            ]
        )
        adapter.embed_batch = AsyncMock(
            return_value=BatchEmbeddingResult(
                embeddings=[
                    EmbeddingResult(
                        embedding=[0.9, 0.1],
                        text="c1",
                        provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                        model="m",
                        dimension=2,
                        latency_ms=1.0,
                    ),
                    EmbeddingResult(
                        embedding=[0.0, 1.0],
                        text="c2",
                        provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                        model="m",
                        dimension=2,
                        latency_ms=1.0,
                    ),
                    EmbeddingResult(
                        embedding=[0.5, 0.5],
                        text="c3",
                        provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                        model="m",
                        dimension=2,
                        latency_ms=1.0,
                    ),
                ],
                total_texts=3,
                successful=3,
                failed=0,
                total_latency_ms=3.0,
                provider=EmbeddingProvider.SENTENCE_TRANSFORMERS,
                model="m",
            )
        )

        candidates = ["c1", "c2", "c3"]
        results = await adapter.find_most_similar("query", candidates, top_k=2)

        assert len(results) == 2
        # c1 should be most similar (closest to [1.0, 0.0])
        assert results[0][0] == "c1"

    def test_clear_cache(self, adapter):
        """Test clearing cache"""
        if adapter._cache:
            adapter._cache.set("test", adapter.config.model, [0.1])
            assert adapter.cache_size > 0

            adapter.clear_cache()
            assert adapter.cache_size == 0


class TestEmbeddingProviderError:
    """Tests for EmbeddingProviderError"""

    def test_error_creation(self):
        """Test creating an error"""
        error = EmbeddingProviderError(
            "Test error",
            provider=EmbeddingProvider.OLLAMA,
            recoverable=True,
        )
        assert str(error) == "Test error"
        assert error.provider == EmbeddingProvider.OLLAMA
        assert error.recoverable is True

    def test_error_with_original(self):
        """Test error with original exception"""
        original = ValueError("Original error")
        error = EmbeddingProviderError(
            "Wrapper error",
            provider=EmbeddingProvider.OPENAI,
            original_error=original,
        )
        assert error.original_error == original


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_get_embeddings_adapter(self):
        """Test getting default adapter"""
        adapter1 = get_embeddings_adapter()
        adapter2 = get_embeddings_adapter()
        # Should return same instance
        assert adapter1 is adapter2

    def test_get_embeddings_adapter_with_config(self):
        """Test getting adapter with custom config"""
        config = EmbeddingConfig(model="custom-model")
        adapter = get_embeddings_adapter(config)
        assert adapter.config.model == "custom-model"


class TestProviderEnums:
    """Tests for provider enums"""

    def test_embedding_provider_values(self):
        """Test EmbeddingProvider enum values"""
        assert EmbeddingProvider.SENTENCE_TRANSFORMERS.value == "sentence_transformers"
        assert EmbeddingProvider.OLLAMA.value == "ollama"
        assert EmbeddingProvider.OPENAI.value == "openai"
        assert EmbeddingProvider.GOOGLE.value == "google"

    def test_embedding_provider_string_conversion(self):
        """Test EmbeddingProvider string conversion"""
        # Test value access (consistent across Python versions)
        assert EmbeddingProvider.OLLAMA.value == "ollama"
        assert EmbeddingProvider.SENTENCE_TRANSFORMERS.value == "sentence_transformers"

        # Test name access
        assert EmbeddingProvider.OLLAMA.name == "OLLAMA"

        # str() behavior varies between Python versions:
        # Python 3.11: returns value ("ollama")
        # Python 3.12+: returns full enum name ("EmbeddingProvider.OLLAMA")
        # So we test that it's one of the expected values
        str_result = str(EmbeddingProvider.OLLAMA)
        assert str_result in ("ollama", "EmbeddingProvider.OLLAMA")
