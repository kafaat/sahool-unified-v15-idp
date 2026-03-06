"""
Unit tests for Arabic Models Registry.
"""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestArabicModelsRegistry:
    """Test the Arabic models registry."""

    def test_arabic_model_task_enum(self):
        """ArabicModelTask should define NLP tasks."""
        try:
            from shared.ai.arabic_models import ArabicModelTask
        except ImportError:
            pytest.skip("arabic_models not available")

        values = [t.value for t in ArabicModelTask]
        assert len(values) >= 3, f"Should have at least 3 tasks, got: {values}"

    def test_arabic_models_registry_not_empty(self):
        """ARABIC_MODELS registry should contain models."""
        try:
            from shared.ai.arabic_models import ARABIC_MODELS
        except ImportError:
            pytest.skip("arabic_models not available")

        assert isinstance(ARABIC_MODELS, dict)
        assert len(ARABIC_MODELS) >= 5, f"Expected 5+ models, got {len(ARABIC_MODELS)}"

    def test_get_arabic_embedding_model(self):
        """get_arabic_embedding_model should return a model config."""
        try:
            from shared.ai.arabic_models import get_arabic_embedding_model
        except ImportError:
            pytest.skip("arabic_models not available")

        model = get_arabic_embedding_model()
        assert model is not None
