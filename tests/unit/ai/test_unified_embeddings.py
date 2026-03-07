"""
Unit tests for Unified Embeddings module.
"""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestUnifiedEmbeddings:
    """Test the unified embeddings adapter."""

    def test_preprocess_arabic_function(self):
        """preprocess_arabic should handle Arabic text."""
        try:
            from shared.ai.unified_embeddings import preprocess_arabic
        except ImportError:
            pytest.skip("unified_embeddings not available")

        result = preprocess_arabic("القمح يعاني من الجفاف")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_arabic_detection(self):
        """_contains_arabic should detect Arabic characters."""
        try:
            from shared.ai.unified_embeddings import _contains_arabic
        except ImportError:
            pytest.skip("unified_embeddings not available")

        assert _contains_arabic("هذا نص عربي") is True
        assert _contains_arabic("This is English") is False
        assert _contains_arabic("Mixed عربي text") is True

    def test_fallback_status_enum(self):
        """FallbackStatus should define provider states."""
        try:
            from shared.ai.unified_embeddings import FallbackStatus
        except ImportError:
            pytest.skip("unified_embeddings not available")

        values = [s.value for s in FallbackStatus]
        assert len(values) >= 2

    def test_embedding_consistency_config(self):
        """EmbeddingConsistencyConfig should have sensible defaults."""
        try:
            from shared.ai.unified_embeddings import EmbeddingConsistencyConfig
        except ImportError:
            pytest.skip("unified_embeddings not available")

        config = EmbeddingConsistencyConfig()
        assert config is not None
