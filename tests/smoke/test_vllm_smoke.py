"""
SAHOOL vLLM Integration Smoke Tests
====================================
اختبارات الدخان لتكامل vLLM

Verifies that all vLLM-related modules can be imported without errors
and that no circular dependencies exist.
"""

from __future__ import annotations

import pytest

pytestmark = [pytest.mark.smoke]


class TestVLLMImports:
    """Test that vLLM-related modules import cleanly."""

    def test_import_shared_llm_package(self):
        """shared.llm package imports without errors."""
        import shared.llm

        assert hasattr(shared.llm, "__version__")

    def test_import_openai_compat_module(self):
        """shared.llm.openai_compat module imports."""
        from shared.llm.openai_compat import (
            OpenAICompatProvider,
            get_deepseek_vllm_provider,
            get_vllm_provider,
        )

        assert callable(get_vllm_provider)
        assert callable(get_deepseek_vllm_provider)
        assert OpenAICompatProvider is not None

    def test_import_llm_provider_module(self):
        """shared.ai.llm_provider module imports with VLLM enum."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        assert hasattr(LLMProvider, "VLLM")
        assert LLMProvider.VLLM.value == "vllm"
        assert LLMConfig is not None

    def test_import_shared_events_subjects(self):
        """shared.events.subjects module imports with LLM subjects."""
        from shared.events.subjects import (
            SAHOOL_LLM_ALL,
            SAHOOL_LLM_GPU_OOM,
            SAHOOL_LLM_INFERENCE_COMPLETED,
            SAHOOL_LLM_INFERENCE_FAILED,
            SAHOOL_LLM_INFERENCE_STARTED,
            SAHOOL_LLM_MODEL_LOADED,
            SAHOOL_LLM_MODEL_UNLOADED,
        )

        assert SAHOOL_LLM_INFERENCE_STARTED is not None
        assert SAHOOL_LLM_ALL is not None

    def test_vllm_provider_in_llm_init_exports(self):
        """get_deepseek_vllm_provider is exported from shared.llm __init__."""
        from shared.llm import get_deepseek_vllm_provider, get_vllm_provider

        assert callable(get_vllm_provider)
        assert callable(get_deepseek_vllm_provider)

    def test_llm_provider_enum_completeness(self):
        """LLMProvider enum contains all expected providers including VLLM."""
        from shared.ai.llm_provider import LLMProvider

        expected = {"ollama", "vllm", "anthropic", "openai", "google", "deepseek"}
        actual = {member.value for member in LLMProvider}
        assert expected == actual

    def test_subject_registry_contains_llm_entries(self):
        """SUBJECT_REGISTRY has LLM inference entries."""
        from shared.events.subjects import SUBJECT_REGISTRY

        llm_keys = [k for k in SUBJECT_REGISTRY if k.startswith("llm.")]
        assert len(llm_keys) >= 6, f"Expected >= 6 LLM entries, got {len(llm_keys)}: {llm_keys}"
