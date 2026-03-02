"""
SAHOOL vLLM Integration Unit Tests
====================================
اختبارات الوحدة لتكامل vLLM

Comprehensive unit tests covering:
1. LLM Provider enum and config (VLLM type)
2. NATS event subjects for LLM inference
3. shared/llm provider functions (get_vllm_provider, get_deepseek_vllm_provider)
4. Subject registry and utility functions
5. Configuration defaults and environment variable handling
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = [pytest.mark.unit]


# ═══════════════════════════════════════════════════════════════════════════
# LLM Provider Enum Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMProviderEnum:
    """Test LLMProvider enum includes VLLM."""

    def test_vllm_enum_value(self):
        """VLLM enum has correct string value."""
        from shared.ai.llm_provider import LLMProvider

        assert LLMProvider.VLLM == "vllm"
        assert LLMProvider.VLLM.value == "vllm"

    def test_vllm_is_strenum(self):
        """LLMProvider members are StrEnum values."""
        from shared.ai.llm_provider import LLMProvider

        assert isinstance(LLMProvider.VLLM, str)
        assert f"Provider: {LLMProvider.VLLM}" == "Provider: vllm"

    def test_all_providers_present(self):
        """All expected providers exist in enum."""
        from shared.ai.llm_provider import LLMProvider

        assert hasattr(LLMProvider, "OLLAMA")
        assert hasattr(LLMProvider, "VLLM")
        assert hasattr(LLMProvider, "ANTHROPIC")
        assert hasattr(LLMProvider, "OPENAI")
        assert hasattr(LLMProvider, "GOOGLE")
        assert hasattr(LLMProvider, "DEEPSEEK")

    def test_vllm_and_ollama_same_priority(self):
        """VLLM and Ollama both have priority 0 (local GPU inference)."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        with patch.dict(os.environ, {"VLLM_BASE_URL": "http://localhost:8270/v1"}, clear=False):
            vllm_config = LLMConfig.from_env(LLMProvider.VLLM)
            ollama_config = LLMConfig.from_env(LLMProvider.OLLAMA)

            assert vllm_config.priority == ollama_config.priority == 0


# ═══════════════════════════════════════════════════════════════════════════
# LLM Config Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMConfigVLLM:
    """Test LLMConfig.from_env for VLLM provider."""

    def test_vllm_default_config(self):
        """VLLM config uses correct defaults when no env vars set."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        with patch.dict(os.environ, {}, clear=False):
            # Remove VLLM_BASE_URL if it exists
            env = {k: v for k, v in os.environ.items() if not k.startswith("VLLM_")}
            with patch.dict(os.environ, env, clear=True):
                config = LLMConfig.from_env(LLMProvider.VLLM)

                assert config.provider == LLMProvider.VLLM
                assert config.model == "deepseek-ai/deepseek-coder-6.7b-instruct"
                assert config.base_url == "http://localhost:8270/v1"
                assert config.priority == 0
                assert config.timeout == 300.0
                assert config.enabled is False  # No VLLM_BASE_URL set

    def test_vllm_config_from_env(self):
        """VLLM config reads from environment variables."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        env = {
            "VLLM_BASE_URL": "http://sahool-vllm:8270/v1",
            "VLLM_MODEL": "deepseek-ai/deepseek-coder-33b-instruct",
        }
        with patch.dict(os.environ, env, clear=False):
            config = LLMConfig.from_env(LLMProvider.VLLM)

            assert config.base_url == "http://sahool-vllm:8270/v1"
            assert config.model == "deepseek-ai/deepseek-coder-33b-instruct"
            assert config.enabled is True  # VLLM_BASE_URL is set

    def test_vllm_config_enabled_when_base_url_set(self):
        """VLLM provider is enabled when VLLM_BASE_URL is set."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        with patch.dict(os.environ, {"VLLM_BASE_URL": "http://vllm:8270/v1"}, clear=False):
            config = LLMConfig.from_env(LLMProvider.VLLM)
            assert config.enabled is True

    def test_vllm_config_disabled_when_no_base_url(self):
        """VLLM provider is disabled when VLLM_BASE_URL is not set."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        env = {k: v for k, v in os.environ.items() if k != "VLLM_BASE_URL"}
        with patch.dict(os.environ, env, clear=True):
            config = LLMConfig.from_env(LLMProvider.VLLM)
            assert config.enabled is False

    def test_vllm_timeout_is_long(self):
        """VLLM has 300s timeout for large model inference."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        config = LLMConfig.from_env(LLMProvider.VLLM)
        assert config.timeout == 300.0

    def test_vllm_higher_priority_than_cloud_providers(self):
        """VLLM (priority 0) has higher priority than cloud providers."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        vllm_config = LLMConfig.from_env(LLMProvider.VLLM)

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False):
            anthropic_config = LLMConfig.from_env(LLMProvider.ANTHROPIC)
            assert vllm_config.priority < anthropic_config.priority


# ═══════════════════════════════════════════════════════════════════════════
# NATS Event Subjects Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMNATSSubjects:
    """Test NATS event subjects for LLM inference."""

    def test_llm_inference_started_subject(self):
        """LLM inference started subject is correctly defined."""
        from shared.events.subjects import SAHOOL_LLM_INFERENCE_STARTED

        assert SAHOOL_LLM_INFERENCE_STARTED == "sahool.llm.inference_started"

    def test_llm_inference_completed_subject(self):
        """LLM inference completed subject is correctly defined."""
        from shared.events.subjects import SAHOOL_LLM_INFERENCE_COMPLETED

        assert SAHOOL_LLM_INFERENCE_COMPLETED == "sahool.llm.inference_completed"

    def test_llm_inference_failed_subject(self):
        """LLM inference failed subject is correctly defined."""
        from shared.events.subjects import SAHOOL_LLM_INFERENCE_FAILED

        assert SAHOOL_LLM_INFERENCE_FAILED == "sahool.llm.inference_failed"

    def test_llm_model_loaded_subject(self):
        """LLM model loaded subject is correctly defined."""
        from shared.events.subjects import SAHOOL_LLM_MODEL_LOADED

        assert SAHOOL_LLM_MODEL_LOADED == "sahool.llm.model_loaded"

    def test_llm_model_unloaded_subject(self):
        """LLM model unloaded subject is correctly defined."""
        from shared.events.subjects import SAHOOL_LLM_MODEL_UNLOADED

        assert SAHOOL_LLM_MODEL_UNLOADED == "sahool.llm.model_unloaded"

    def test_llm_gpu_oom_subject(self):
        """LLM GPU OOM subject is correctly defined."""
        from shared.events.subjects import SAHOOL_LLM_GPU_OOM

        assert SAHOOL_LLM_GPU_OOM == "sahool.llm.gpu_oom"

    def test_llm_wildcard_subject(self):
        """LLM wildcard subject matches pattern."""
        from shared.events.subjects import SAHOOL_LLM_ALL

        assert SAHOOL_LLM_ALL == "sahool.llm.*"

    def test_all_llm_subjects_follow_naming_convention(self):
        """All LLM subjects start with 'sahool.llm.'."""
        from shared.events.subjects import (
            SAHOOL_LLM_GPU_OOM,
            SAHOOL_LLM_INFERENCE_COMPLETED,
            SAHOOL_LLM_INFERENCE_FAILED,
            SAHOOL_LLM_INFERENCE_STARTED,
            SAHOOL_LLM_MODEL_LOADED,
            SAHOOL_LLM_MODEL_UNLOADED,
        )

        subjects = [
            SAHOOL_LLM_INFERENCE_STARTED,
            SAHOOL_LLM_INFERENCE_COMPLETED,
            SAHOOL_LLM_INFERENCE_FAILED,
            SAHOOL_LLM_MODEL_LOADED,
            SAHOOL_LLM_MODEL_UNLOADED,
            SAHOOL_LLM_GPU_OOM,
        ]

        for subject in subjects:
            assert subject.startswith("sahool.llm."), f"Subject {subject} doesn't follow convention"

    def test_llm_subjects_are_valid(self):
        """All LLM subjects pass is_valid_subject check."""
        from shared.events.subjects import (
            SAHOOL_LLM_GPU_OOM,
            SAHOOL_LLM_INFERENCE_COMPLETED,
            SAHOOL_LLM_INFERENCE_FAILED,
            SAHOOL_LLM_INFERENCE_STARTED,
            SAHOOL_LLM_MODEL_LOADED,
            SAHOOL_LLM_MODEL_UNLOADED,
            is_valid_subject,
        )

        subjects = [
            SAHOOL_LLM_INFERENCE_STARTED,
            SAHOOL_LLM_INFERENCE_COMPLETED,
            SAHOOL_LLM_INFERENCE_FAILED,
            SAHOOL_LLM_MODEL_LOADED,
            SAHOOL_LLM_MODEL_UNLOADED,
            SAHOOL_LLM_GPU_OOM,
        ]

        for subject in subjects:
            assert is_valid_subject(subject), f"Subject {subject} failed validation"


# ═══════════════════════════════════════════════════════════════════════════
# Subject Registry Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMSubjectRegistry:
    """Test LLM entries in the SUBJECT_REGISTRY."""

    def test_registry_has_llm_inference_started(self):
        """Registry maps llm.inference_started correctly."""
        from shared.events.subjects import SAHOOL_LLM_INFERENCE_STARTED, SUBJECT_REGISTRY

        assert SUBJECT_REGISTRY["llm.inference_started"] == SAHOOL_LLM_INFERENCE_STARTED

    def test_registry_has_llm_inference_completed(self):
        """Registry maps llm.inference_completed correctly."""
        from shared.events.subjects import SAHOOL_LLM_INFERENCE_COMPLETED, SUBJECT_REGISTRY

        assert SUBJECT_REGISTRY["llm.inference_completed"] == SAHOOL_LLM_INFERENCE_COMPLETED

    def test_registry_has_llm_inference_failed(self):
        """Registry maps llm.inference_failed correctly."""
        from shared.events.subjects import SAHOOL_LLM_INFERENCE_FAILED, SUBJECT_REGISTRY

        assert SUBJECT_REGISTRY["llm.inference_failed"] == SAHOOL_LLM_INFERENCE_FAILED

    def test_registry_has_llm_model_loaded(self):
        """Registry maps llm.model_loaded correctly."""
        from shared.events.subjects import SAHOOL_LLM_MODEL_LOADED, SUBJECT_REGISTRY

        assert SUBJECT_REGISTRY["llm.model_loaded"] == SAHOOL_LLM_MODEL_LOADED

    def test_registry_has_llm_model_unloaded(self):
        """Registry maps llm.model_unloaded correctly."""
        from shared.events.subjects import SAHOOL_LLM_MODEL_UNLOADED, SUBJECT_REGISTRY

        assert SUBJECT_REGISTRY["llm.model_unloaded"] == SAHOOL_LLM_MODEL_UNLOADED

    def test_registry_has_llm_gpu_oom(self):
        """Registry maps llm.gpu_oom correctly."""
        from shared.events.subjects import SAHOOL_LLM_GPU_OOM, SUBJECT_REGISTRY

        assert SUBJECT_REGISTRY["llm.gpu_oom"] == SAHOOL_LLM_GPU_OOM

    def test_lookup_subject_finds_llm_entries(self):
        """lookup_subject resolves LLM event types."""
        from shared.events.subjects import lookup_subject

        assert lookup_subject("llm.inference_started") == "sahool.llm.inference_started"
        assert lookup_subject("llm.gpu_oom") == "sahool.llm.gpu_oom"

    def test_get_subject_for_event_constructs_llm_subject(self):
        """get_subject_for_event builds correct subject for llm events."""
        from shared.events.subjects import get_subject_for_event

        assert get_subject_for_event("llm.inference_started") == "sahool.llm.inference_started"
        assert get_subject_for_event("sahool.llm.gpu_oom") == "sahool.llm.gpu_oom"

    def test_get_wildcard_subject_for_llm(self):
        """get_wildcard_subject returns correct wildcard for llm domain."""
        from shared.events.subjects import get_wildcard_subject

        assert get_wildcard_subject("llm") == "sahool.llm.*"


# ═══════════════════════════════════════════════════════════════════════════
# Provider Function Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMProviderFunctions:
    """Test get_vllm_provider and get_deepseek_vllm_provider functions."""

    def test_get_vllm_provider_defaults(self):
        """get_vllm_provider uses correct default parameters."""
        import inspect

        from shared.llm.openai_compat import get_vllm_provider

        sig = inspect.signature(get_vllm_provider)
        params = sig.parameters

        assert params["base_url"].default == "http://localhost:8270/v1"
        assert params["model"].default == "deepseek-ai/deepseek-coder-6.7b-instruct"

    def test_get_deepseek_vllm_provider_defaults(self):
        """get_deepseek_vllm_provider uses Docker service URL."""
        import inspect

        from shared.llm.openai_compat import get_deepseek_vllm_provider

        sig = inspect.signature(get_deepseek_vllm_provider)
        params = sig.parameters

        assert params["base_url"].default == "http://sahool-vllm:8270/v1"
        assert params["model"].default == "deepseek-ai/deepseek-coder-6.7b-instruct"

    def test_get_vllm_provider_is_async(self):
        """get_vllm_provider is an async function."""
        import asyncio

        from shared.llm.openai_compat import get_vllm_provider

        assert asyncio.iscoroutinefunction(get_vllm_provider)

    def test_get_deepseek_vllm_provider_is_async(self):
        """get_deepseek_vllm_provider is an async function."""
        import asyncio

        from shared.llm.openai_compat import get_deepseek_vllm_provider

        assert asyncio.iscoroutinefunction(get_deepseek_vllm_provider)

    def test_openai_compat_provider_class_exists(self):
        """OpenAICompatProvider class is importable and has expected methods."""
        from shared.llm.openai_compat import OpenAICompatProvider

        assert hasattr(OpenAICompatProvider, "generate")
        assert hasattr(OpenAICompatProvider, "chat")
        assert hasattr(OpenAICompatProvider, "is_available")
        assert hasattr(OpenAICompatProvider, "list_models")
        assert hasattr(OpenAICompatProvider, "embeddings")
        assert hasattr(OpenAICompatProvider, "generate_stream")
        assert hasattr(OpenAICompatProvider, "chat_stream")
        assert hasattr(OpenAICompatProvider, "close")

    def test_provider_exports_in_shared_llm_init(self):
        """shared.llm.__all__ includes vLLM provider functions."""
        from shared.llm import __all__

        assert "get_vllm_provider" in __all__
        assert "get_deepseek_vllm_provider" in __all__
        assert "OpenAICompatProvider" in __all__


# ═══════════════════════════════════════════════════════════════════════════
# Configuration Consistency Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestVLLMConfigConsistency:
    """Test consistency of vLLM configuration across components."""

    def test_default_model_consistent(self):
        """Default model is consistent between llm_provider and openai_compat."""
        import inspect

        from shared.ai.llm_provider import LLMConfig, LLMProvider
        from shared.llm.openai_compat import get_deepseek_vllm_provider, get_vllm_provider

        # LLM provider default
        config = LLMConfig.from_env(LLMProvider.VLLM)
        provider_model = config.model

        # openai_compat defaults
        vllm_sig = inspect.signature(get_vllm_provider)
        deepseek_sig = inspect.signature(get_deepseek_vllm_provider)

        assert provider_model == vllm_sig.parameters["model"].default
        assert provider_model == deepseek_sig.parameters["model"].default

    def test_default_port_is_8270(self):
        """Default vLLM port is 8270 across all configurations."""
        import inspect

        from shared.llm.openai_compat import get_vllm_provider

        sig = inspect.signature(get_vllm_provider)
        base_url = sig.parameters["base_url"].default

        assert ":8270/" in base_url

    def test_deepseek_docker_url_uses_service_name(self):
        """Docker-internal URL uses sahool-vllm service name."""
        import inspect

        from shared.llm.openai_compat import get_deepseek_vllm_provider

        sig = inspect.signature(get_deepseek_vllm_provider)
        base_url = sig.parameters["base_url"].default

        assert "sahool-vllm" in base_url
        assert base_url.endswith("/v1")
