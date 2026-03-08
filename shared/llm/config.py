"""
LLM Configuration Module
========================
وحدة تكوين نماذج اللغة الكبيرة

Configuration settings for local LLM providers.
Supports environment-based configuration for development cost savings.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Environment(StrEnum):
    """Deployment environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class ModelCapability(StrEnum):
    """Model capability requirements."""

    CHAT = "chat"
    CODE = "code"
    EMBEDDING = "embedding"
    VISION = "vision"
    AGRICULTURAL = "agricultural"  # Domain-specific
    MULTILINGUAL = "multilingual"  # Arabic/English support


@dataclass
class OllamaConfig:
    """Configuration for Ollama local LLM server."""

    base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    default_model: str = field(default_factory=lambda: os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2"))
    timeout: float = 120.0
    max_retries: int = 3
    retry_delay: float = 1.0
    # Streaming configuration
    stream_timeout: float = 300.0


@dataclass
class OpenAICompatConfig:
    """Configuration for OpenAI-compatible endpoints (Ollama, vLLM, LM Studio)."""

    base_url: str = field(default_factory=lambda: os.getenv("OPENAI_COMPAT_BASE_URL", "http://localhost:11434/v1"))
    api_key: str = field(default_factory=lambda: os.getenv("OPENAI_COMPAT_API_KEY", "ollama"))
    default_model: str = field(default_factory=lambda: os.getenv("OPENAI_COMPAT_MODEL", "llama3.2"))
    timeout: float = 120.0
    organization: str | None = None


@dataclass
class CloudConfig:
    """Configuration for cloud LLM providers (OpenAI, Anthropic, etc.)."""

    # OpenAI
    openai_api_key: str | None = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    openai_base_url: str = "https://api.openai.com/v1"

    # Anthropic
    anthropic_api_key: str | None = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    anthropic_model: str = field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"))

    timeout: float = 120.0


@dataclass
class LLMConfig:
    """
    Main configuration for LLM utilities.

    التكوين الرئيسي لأدوات نماذج اللغة الكبيرة

    Attributes:
        environment: Current deployment environment
        development_mode: Force local models in development
        ollama: Ollama server configuration
        openai_compat: OpenAI-compatible endpoint configuration
        cloud: Cloud provider configuration
        default_temperature: Default sampling temperature
        default_max_tokens: Default max tokens for generation
        enable_fallback: Enable fallback to other providers
        enable_cost_tracking: Enable cost tracking and logging
    """

    environment: Environment = field(
        default_factory=lambda: Environment(os.getenv("ENVIRONMENT", "development").lower())
    )
    development_mode: bool = field(default_factory=lambda: os.getenv("DEVELOPMENT_MODE", "true").lower() == "true")

    # Provider configs
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    openai_compat: OpenAICompatConfig = field(default_factory=OpenAICompatConfig)
    cloud: CloudConfig = field(default_factory=CloudConfig)

    # Generation defaults
    default_temperature: float = 0.7
    default_max_tokens: int = 4096

    # Behavior
    enable_fallback: bool = True
    enable_cost_tracking: bool = True
    enable_metrics: bool = True

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == Environment.DEVELOPMENT or self.development_mode

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION

    @property
    def prefer_local(self) -> bool:
        """Check if local models should be preferred."""
        return self.is_development and not self.is_production

    @classmethod
    def from_env(cls) -> LLMConfig:
        """Create configuration from environment variables."""
        return cls()

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "environment": self.environment.value,
            "development_mode": self.development_mode,
            "prefer_local": self.prefer_local,
            "ollama": {
                "base_url": self.ollama.base_url,
                "default_model": self.ollama.default_model,
                "timeout": self.ollama.timeout,
            },
            "openai_compat": {
                "base_url": self.openai_compat.base_url,
                "default_model": self.openai_compat.default_model,
            },
            "cloud": {
                "openai_available": bool(self.cloud.openai_api_key),
                "anthropic_available": bool(self.cloud.anthropic_api_key),
            },
            "defaults": {
                "temperature": self.default_temperature,
                "max_tokens": self.default_max_tokens,
            },
            "enable_fallback": self.enable_fallback,
            "enable_cost_tracking": self.enable_cost_tracking,
        }


# Model registry with capabilities
MODEL_REGISTRY: dict[str, dict[str, Any]] = {
    # Ollama models
    "llama3.2": {
        "provider": "ollama",
        "capabilities": [ModelCapability.CHAT, ModelCapability.MULTILINGUAL],
        "context_length": 128000,
        "cost_per_1k_tokens": 0.0,  # Local, free
    },
    "llama3.2:1b": {
        "provider": "ollama",
        "capabilities": [ModelCapability.CHAT],
        "context_length": 128000,
        "cost_per_1k_tokens": 0.0,
    },
    "llama3.2:3b": {
        "provider": "ollama",
        "capabilities": [ModelCapability.CHAT, ModelCapability.MULTILINGUAL],
        "context_length": 128000,
        "cost_per_1k_tokens": 0.0,
    },
    "codellama": {
        "provider": "ollama",
        "capabilities": [ModelCapability.CODE, ModelCapability.CHAT],
        "context_length": 16384,
        "cost_per_1k_tokens": 0.0,
    },
    "codellama:7b": {
        "provider": "ollama",
        "capabilities": [ModelCapability.CODE, ModelCapability.CHAT],
        "context_length": 16384,
        "cost_per_1k_tokens": 0.0,
    },
    "codellama:13b": {
        "provider": "ollama",
        "capabilities": [ModelCapability.CODE, ModelCapability.CHAT],
        "context_length": 16384,
        "cost_per_1k_tokens": 0.0,
    },
    "mistral": {
        "provider": "ollama",
        "capabilities": [ModelCapability.CHAT, ModelCapability.CODE],
        "context_length": 32768,
        "cost_per_1k_tokens": 0.0,
    },
    "mistral:7b": {
        "provider": "ollama",
        "capabilities": [ModelCapability.CHAT, ModelCapability.CODE],
        "context_length": 32768,
        "cost_per_1k_tokens": 0.0,
    },
    "qwen2.5": {
        "provider": "ollama",
        "capabilities": [
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.MULTILINGUAL,
        ],
        "context_length": 32768,
        "cost_per_1k_tokens": 0.0,
    },
    "qwen2.5:7b": {
        "provider": "ollama",
        "capabilities": [
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.MULTILINGUAL,
        ],
        "context_length": 32768,
        "cost_per_1k_tokens": 0.0,
    },
    "qwen2.5-coder": {
        "provider": "ollama",
        "capabilities": [ModelCapability.CODE, ModelCapability.CHAT],
        "context_length": 32768,
        "cost_per_1k_tokens": 0.0,
    },
    "nomic-embed-text": {
        "provider": "ollama",
        "capabilities": [ModelCapability.EMBEDDING],
        "context_length": 8192,
        "cost_per_1k_tokens": 0.0,
    },
    # OpenAI models (for reference)
    "gpt-4o-mini": {
        "provider": "openai",
        "capabilities": [
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.VISION,
            ModelCapability.MULTILINGUAL,
        ],
        "context_length": 128000,
        "cost_per_1k_tokens": 0.00015,  # Input
    },
    "gpt-4o": {
        "provider": "openai",
        "capabilities": [
            ModelCapability.CHAT,
            ModelCapability.CODE,
            ModelCapability.VISION,
            ModelCapability.MULTILINGUAL,
        ],
        "context_length": 128000,
        "cost_per_1k_tokens": 0.005,
    },
}


def get_model_info(model: str) -> dict[str, Any] | None:
    """
    Get information about a model.

    الحصول على معلومات حول نموذج
    """
    return MODEL_REGISTRY.get(model)


def get_models_by_capability(capability: ModelCapability) -> list[str]:
    """
    Get all models with a specific capability.

    الحصول على جميع النماذج ذات قدرة محددة
    """
    return [model for model, info in MODEL_REGISTRY.items() if capability in info.get("capabilities", [])]


def get_local_models() -> list[str]:
    """
    Get all local (Ollama) models.

    الحصول على جميع النماذج المحلية
    """
    return [model for model, info in MODEL_REGISTRY.items() if info.get("provider") == "ollama"]


# Default global config
_global_config: LLMConfig | None = None


def get_config() -> LLMConfig:
    """
    Get the global LLM configuration.

    الحصول على التكوين العام لنماذج اللغة الكبيرة
    """
    global _global_config
    if _global_config is None:
        _global_config = LLMConfig.from_env()
    return _global_config


def set_config(config: LLMConfig) -> None:
    """
    Set the global LLM configuration.

    تعيين التكوين العام لنماذج اللغة الكبيرة
    """
    global _global_config
    _global_config = config
