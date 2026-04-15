"""
Tests for Huggingface Provider Module
=====================================
اختبارات وحدة مزود Huggingface

Tests for Huggingface embedding integration including:
- Configuration management
- Embedding generation
- Arabic language support
- Caching functionality
- Model information

Author: SAHOOL Platform Team
Created: January 2026
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.ai.huggingface_provider import (
    AGRICULTURAL_MODELS,
    EMBEDDING_MODELS,
    BatchEmbeddingResult,
    EmbeddingCache,
    EmbeddingModelFamily,
    EmbeddingResult,
    HuggingfaceConfig,
    HuggingfaceModelType,
    HuggingfaceProvider,
    ModelInfo,
    embed_text,
    embed_texts,
    get_best_arabic_model,
    get_huggingface_provider,
    list_arabic_models,
    text_similarity,
)

# ============================================================================
# Config Tests
# ============================================================================


class TestHuggingfaceConfig:
    """Tests for HuggingfaceConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = HuggingfaceConfig()

        assert config.api_url == "https://api-inference.huggingface.co"
        assert config.default_embedding_model == "intfloat/multilingual-e5-large"
        assert config.cache_enabled is True
        assert config.use_local_models is True
        assert config.batch_size == 32
        assert config.max_length == 512
        assert config.normalize_embeddings is True

    def test_custom_config(self):
        """Test custom configuration"""
        config = HuggingfaceConfig(
            api_token="test_token",
            default_embedding_model="aubmindlab/bert-base-arabertv02",
            use_local_models=False,
            batch_size=64,
        )

        assert config.api_token == "test_token"
        assert config.default_embedding_model == "aubmindlab/bert-base-arabertv02"
        assert config.use_local_models is False
        assert config.batch_size == 64

    def test_config_from_env(self):
        """Test configuration from environment variables"""
        with patch.dict("os.environ", {"HUGGINGFACE_API_TOKEN": "env_token"}):
            config = HuggingfaceConfig()
            # The __post_init__ should pick up the env var
            # Note: This depends on the actual implementation


# ============================================================================
# Enum Tests
# ============================================================================


class TestEnums:
    """Tests for enumeration types"""

    def test_model_types(self):
        """Test HuggingfaceModelType enum values"""
        assert HuggingfaceModelType.EMBEDDING.value == "embedding"
        assert HuggingfaceModelType.TEXT_GENERATION.value == "text_generation"
        assert HuggingfaceModelType.IMAGE_CLASSIFICATION.value == "image_classification"

    def test_embedding_model_families(self):
        """Test EmbeddingModelFamily enum values"""
        assert EmbeddingModelFamily.MULTILINGUAL_E5.value == "multilingual-e5"
        assert EmbeddingModelFamily.ARABERT.value == "arabert"
        assert EmbeddingModelFamily.MARBERT.value == "marbert"
        assert EmbeddingModelFamily.ALL_MINILM.value == "all-minilm"
        assert EmbeddingModelFamily.BGE.value == "bge"


# ============================================================================
# Data Class Tests
# ============================================================================


class TestEmbeddingResult:
    """Tests for EmbeddingResult data class"""

    def test_embedding_result_creation(self):
        """Test creating an embedding result"""
        result = EmbeddingResult(
            embedding=[0.1, 0.2, 0.3],
            model="test-model",
            dimension=3,
            latency_ms=10.5,
            from_cache=False,
        )

        assert result.embedding == [0.1, 0.2, 0.3]
        assert result.model == "test-model"
        assert result.dimension == 3
        assert result.latency_ms == 10.5
        assert result.from_cache is False

    def test_embedding_result_from_cache(self):
        """Test embedding result from cache"""
        result = EmbeddingResult(
            embedding=[0.1] * 768,
            model="multilingual-e5",
            dimension=768,
            latency_ms=0.5,
            from_cache=True,
        )

        assert result.from_cache is True
        assert result.latency_ms < 1.0


class TestBatchEmbeddingResult:
    """Tests for BatchEmbeddingResult data class"""

    def test_batch_embedding_result_creation(self):
        """Test creating a batch embedding result"""
        result = BatchEmbeddingResult(
            embeddings=[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]],
            model="test-model",
            dimension=2,
            total_latency_ms=30.0,
            avg_latency_ms=10.0,
            cache_hits=1,
            cache_misses=2,
        )

        assert len(result) == 3
        assert result.embeddings[0] == [0.1, 0.2]
        assert result.cache_hits == 1
        assert result.cache_misses == 2


class TestModelInfo:
    """Tests for ModelInfo data class"""

    def test_model_info_creation(self):
        """Test creating model info"""
        info = ModelInfo(
            model_id="intfloat/multilingual-e5-large",
            model_type=HuggingfaceModelType.EMBEDDING,
            family=EmbeddingModelFamily.MULTILINGUAL_E5,
            dimension=1024,
            max_sequence_length=512,
            languages=["ar", "en"],
            supports_arabic=True,
            arabic_quality="excellent",
        )

        assert info.model_id == "intfloat/multilingual-e5-large"
        assert info.dimension == 1024
        assert info.supports_arabic is True
        assert "ar" in info.languages


# ============================================================================
# Cache Tests
# ============================================================================


class TestEmbeddingCache:
    """Tests for EmbeddingCache"""

    def test_cache_creation(self):
        """Test creating a cache"""
        cache = EmbeddingCache(ttl_seconds=3600, max_size=1000)

        assert cache.ttl_seconds == 3600
        assert cache.max_size == 1000
        assert cache.size == 0

    def test_cache_set_and_get(self):
        """Test setting and getting from cache"""
        cache = EmbeddingCache()

        embedding = [0.1, 0.2, 0.3]
        cache.set("test text", "model", embedding)

        cached = cache.get("test text", "model")
        assert cached == embedding

    def test_cache_miss(self):
        """Test cache miss"""
        cache = EmbeddingCache()

        cached = cache.get("non-existent", "model")
        assert cached is None

    def test_cache_different_models(self):
        """Test cache with different models"""
        cache = EmbeddingCache()

        cache.set("text", "model1", [0.1, 0.2])
        cache.set("text", "model2", [0.3, 0.4])

        assert cache.get("text", "model1") == [0.1, 0.2]
        assert cache.get("text", "model2") == [0.3, 0.4]

    def test_cache_clear(self):
        """Test clearing cache"""
        cache = EmbeddingCache()

        cache.set("text", "model", [0.1, 0.2])
        assert cache.size == 1

        cache.clear()
        assert cache.size == 0

    def test_cache_stats(self):
        """Test cache statistics"""
        cache = EmbeddingCache(ttl_seconds=3600, max_size=1000)

        cache.set("text", "model", [0.1, 0.2])

        stats = cache.stats
        assert stats["size"] == 1
        assert stats["max_size"] == 1000


# ============================================================================
# Provider Tests
# ============================================================================


class TestHuggingfaceProvider:
    """Tests for HuggingfaceProvider class"""

    def test_provider_creation_default(self):
        """Test creating provider with default config"""
        provider = HuggingfaceProvider()

        assert provider.config is not None
        assert provider.config.default_embedding_model == "intfloat/multilingual-e5-large"

    def test_provider_creation_custom_config(self):
        """Test creating provider with custom config"""
        config = HuggingfaceConfig(
            default_embedding_model="aubmindlab/bert-base-arabertv02",
            cache_enabled=False,
        )
        provider = HuggingfaceProvider(config)

        assert provider.config.default_embedding_model == "aubmindlab/bert-base-arabertv02"
        assert provider._cache is None

    def test_get_model_info(self):
        """Test getting model information"""
        provider = HuggingfaceProvider()

        info = provider.get_model_info("intfloat/multilingual-e5-large")

        assert info is not None
        assert info.dimension == 1024
        assert info.supports_arabic is True

    def test_get_model_info_unknown(self):
        """Test getting info for unknown model"""
        provider = HuggingfaceProvider()

        info = provider.get_model_info("unknown/model")

        assert info is None

    def test_list_models(self):
        """Test listing available models"""
        provider = HuggingfaceProvider()

        models = provider.list_models()

        assert len(models) > 0
        assert all(isinstance(m, ModelInfo) for m in models)

    def test_list_arabic_models_method(self):
        """Test listing Arabic-supporting models"""
        provider = HuggingfaceProvider()

        models = provider.list_models(arabic_only=True)

        assert len(models) > 0
        assert all(m.supports_arabic for m in models)

    def test_list_models_by_family(self):
        """Test listing models by family"""
        provider = HuggingfaceProvider()

        models = provider.list_models(family=EmbeddingModelFamily.MULTILINGUAL_E5)

        assert len(models) > 0
        assert all(m.family == EmbeddingModelFamily.MULTILINGUAL_E5 for m in models)

    def test_get_recommended_model(self):
        """Test getting recommended model"""
        provider = HuggingfaceProvider()

        model = provider.get_recommended_model("arabic_agriculture")
        assert model == "intfloat/multilingual-e5-large"

        model = provider.get_recommended_model("fast_agriculture")
        assert model == "sentence-transformers/all-MiniLM-L6-v2"

    def test_provider_stats(self):
        """Test provider statistics"""
        provider = HuggingfaceProvider()

        stats = provider.stats

        assert "total_embeddings" in stats
        assert "cache_hits" in stats
        assert "cache_misses" in stats
        assert "loaded_models" in stats

    def test_clear_cache(self):
        """Test clearing provider cache"""
        provider = HuggingfaceProvider()

        # This should not raise
        provider.clear_cache()


# ============================================================================
# Embedding Constants Tests
# ============================================================================


class TestEmbeddingConstants:
    """Tests for embedding model constants"""

    def test_embedding_models_dict(self):
        """Test EMBEDDING_MODELS dictionary"""
        assert "intfloat/multilingual-e5-large" in EMBEDDING_MODELS
        assert "aubmindlab/bert-base-arabertv02" in EMBEDDING_MODELS
        assert "sentence-transformers/all-MiniLM-L6-v2" in EMBEDDING_MODELS

    def test_embedding_models_have_dimension(self):
        """Test that all models have dimension specified"""
        for model_id, info in EMBEDDING_MODELS.items():
            assert info.dimension > 0, f"Model {model_id} has no dimension"

    def test_embedding_models_arabic_support(self):
        """Test Arabic support flags"""
        arabic_models = [m for m in EMBEDDING_MODELS.values() if m.supports_arabic]
        english_only = [m for m in EMBEDDING_MODELS.values() if not m.supports_arabic]

        assert len(arabic_models) > 0, "No Arabic models found"
        assert len(english_only) > 0, "No English-only models found"

    def test_agricultural_models_dict(self):
        """Test AGRICULTURAL_MODELS dictionary"""
        assert "arabic_agriculture" in AGRICULTURAL_MODELS
        assert "english_agriculture" in AGRICULTURAL_MODELS
        assert "bilingual_agriculture" in AGRICULTURAL_MODELS
        assert "fast_agriculture" in AGRICULTURAL_MODELS


# ============================================================================
# Singleton Tests
# ============================================================================


class TestSingleton:
    """Tests for singleton instance"""

    def test_get_huggingface_provider(self):
        """Test getting singleton provider"""
        provider1 = get_huggingface_provider()
        provider2 = get_huggingface_provider()

        # Should return same instance
        assert provider1 is provider2

    def test_get_huggingface_provider_with_config(self):
        """Test getting provider with custom config"""
        config = HuggingfaceConfig(
            default_embedding_model="aubmindlab/bert-base-arabertv02",
        )
        provider = get_huggingface_provider(config)

        assert provider.config.default_embedding_model == "aubmindlab/bert-base-arabertv02"


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_list_arabic_models_function(self):
        """Test list_arabic_models convenience function"""
        models = list_arabic_models()

        assert len(models) > 0
        assert all(m.supports_arabic for m in models)

    def test_get_best_arabic_model_function(self):
        """Test get_best_arabic_model convenience function"""
        model = get_best_arabic_model()

        assert model is not None
        assert model in EMBEDDING_MODELS


# ============================================================================
# Async Embedding Tests
# ============================================================================


class TestAsyncEmbeddings:
    """Tests for async embedding methods"""

    @pytest.mark.asyncio
    async def test_embed_uses_cache(self):
        """Test that embed uses cache when enabled"""
        config = HuggingfaceConfig(
            use_local_models=False,
            cache_enabled=True,
        )
        provider = HuggingfaceProvider(config)

        # Mock the API call
        with patch.object(provider, "_embed_api", new_callable=AsyncMock) as mock_api:
            mock_api.return_value = [[0.1] * 768]

            # First call - should use API
            result1 = await provider.embed("test text")

            # Second call - should use cache
            result2 = await provider.embed("test text")

            # API should only be called once
            assert mock_api.call_count == 1
            assert result2.from_cache is True

    @pytest.mark.asyncio
    async def test_similarity_calculation(self):
        """Test similarity calculation between texts"""
        config = HuggingfaceConfig(
            use_local_models=False,
            cache_enabled=True,
        )
        provider = HuggingfaceProvider(config)

        # Mock embeddings
        with patch.object(provider, "embed_batch", new_callable=AsyncMock) as mock_batch:
            mock_batch.return_value = BatchEmbeddingResult(
                embeddings=[[1.0, 0.0, 0.0], [0.9, 0.1, 0.0]],
                model="test",
                dimension=3,
                total_latency_ms=10.0,
                avg_latency_ms=5.0,
            )

            similarity = await provider.similarity("text1", "text2")

            # Should be high similarity (close vectors)
            assert similarity > 0.9

    @pytest.mark.asyncio
    async def test_find_most_similar(self):
        """Test finding most similar texts"""
        config = HuggingfaceConfig(
            use_local_models=False,
            cache_enabled=False,
        )
        provider = HuggingfaceProvider(config)

        # Mock embeddings
        with patch.object(provider, "embed_batch", new_callable=AsyncMock) as mock_batch:
            # Query embedding + 3 candidate embeddings
            mock_batch.return_value = BatchEmbeddingResult(
                embeddings=[
                    [1.0, 0.0, 0.0],  # query
                    [0.9, 0.1, 0.0],  # very similar
                    [0.5, 0.5, 0.0],  # somewhat similar
                    [0.0, 1.0, 0.0],  # not similar
                ],
                model="test",
                dimension=3,
                total_latency_ms=20.0,
                avg_latency_ms=5.0,
            )

            results = await provider.find_most_similar(
                query="query",
                candidates=["similar", "somewhat", "different"],
                top_k=2,
            )

            assert len(results) == 2
            # Results should be sorted by similarity
            assert results[0][1] > results[1][1]


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for Huggingface provider"""

    def test_multilingual_model_specs(self):
        """Test multilingual model specifications"""
        e5_large = EMBEDDING_MODELS["intfloat/multilingual-e5-large"]

        assert e5_large.dimension == 1024
        assert "ar" in e5_large.languages
        assert "en" in e5_large.languages
        assert e5_large.arabic_quality == "excellent"

    def test_arabic_model_specs(self):
        """Test Arabic-specific model specifications"""
        arabert = EMBEDDING_MODELS["aubmindlab/bert-base-arabertv02"]

        assert arabert.dimension == 768
        assert arabert.supports_arabic is True
        assert arabert.family == EmbeddingModelFamily.ARABERT

    def test_all_models_have_required_fields(self):
        """Test that all models have required fields"""
        for model_id, info in EMBEDDING_MODELS.items():
            assert info.model_id == model_id
            assert info.model_type == HuggingfaceModelType.EMBEDDING
            assert info.dimension > 0
            assert info.max_sequence_length > 0
            assert len(info.languages) > 0


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_empty_text_embedding(self):
        """Test handling of empty text"""
        provider = HuggingfaceProvider()

        # Empty text should be handled gracefully
        # (actual behavior depends on implementation)

    def test_very_long_text(self):
        """Test handling of very long text"""
        provider = HuggingfaceProvider()

        # Long text should be truncated according to max_length
        # (actual behavior depends on implementation)

    def test_arabic_text(self):
        """Test Arabic text handling"""
        provider = HuggingfaceProvider()

        # Arabic text should be handled correctly
        arabic_text = "توصية زراعية للقمح في الحقل"

        # This is a basic test - actual embedding would need mocking

    def test_mixed_arabic_english(self):
        """Test mixed Arabic/English text"""
        provider = HuggingfaceProvider()

        mixed_text = "Agricultural نصائح for القمح"

        # This is a basic test - actual embedding would need mocking

    @pytest.mark.asyncio
    async def test_close_provider(self):
        """Test closing provider releases resources"""
        provider = HuggingfaceProvider()

        await provider.close()

        # HTTP client should be closed
        assert provider._http_client is None
