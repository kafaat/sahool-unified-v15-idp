"""
LLM Provider Base Module
========================
وحدة مزود نماذج اللغة الكبيرة الأساسية

Abstract base class for all LLM providers.
Defines common interface for generation, chat, and streaming.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ProviderType(StrEnum):
    """LLM provider types."""

    OLLAMA = "ollama"
    OPENAI_COMPAT = "openai_compat"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"  # Generic local provider


class GenerationStatus(StrEnum):
    """Status of generation request."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    MODEL_NOT_FOUND = "model_not_found"


@dataclass
class Message:
    """
    Chat message structure.

    هيكل رسالة الدردشة
    """

    role: str  # "system", "user", "assistant"
    content: str
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result

    @classmethod
    def system(cls, content: str) -> Message:
        """Create a system message."""
        return cls(role="system", content=content)

    @classmethod
    def user(cls, content: str) -> Message:
        """Create a user message."""
        return cls(role="user", content=content)

    @classmethod
    def assistant(cls, content: str) -> Message:
        """Create an assistant message."""
        return cls(role="assistant", content=content)


@dataclass
class GenerationOptions:
    """
    Options for text generation.

    خيارات توليد النص
    """

    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    top_k: int | None = None
    stop: list[str] | None = None
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    seed: int | None = None
    # Response format
    json_mode: bool = False
    # Streaming
    stream: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API calls."""
        result: dict[str, Any] = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }
        if self.top_k is not None:
            result["top_k"] = self.top_k
        if self.stop:
            result["stop"] = self.stop
        if self.presence_penalty != 0.0:
            result["presence_penalty"] = self.presence_penalty
        if self.frequency_penalty != 0.0:
            result["frequency_penalty"] = self.frequency_penalty
        if self.seed is not None:
            result["seed"] = self.seed
        return result


@dataclass
class GenerationResponse:
    """
    Response from LLM generation.

    استجابة من توليد نماذج اللغة الكبيرة
    """

    text: str
    model: str
    provider: ProviderType
    status: GenerationStatus = GenerationStatus.SUCCESS

    # Token usage
    tokens_input: int = 0
    tokens_output: int = 0

    # Performance metrics
    latency_ms: float = 0.0
    tokens_per_second: float | None = None

    # Cost (0 for local models)
    cost_usd: float = 0.0

    # Metadata
    finish_reason: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    raw_response: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Get total tokens used."""
        return self.tokens_input + self.tokens_output

    @property
    def is_success(self) -> bool:
        """Check if generation was successful."""
        return self.status == GenerationStatus.SUCCESS

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "model": self.model,
            "provider": self.provider.value,
            "status": self.status.value,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "tokens_per_second": self.tokens_per_second,
            "cost_usd": self.cost_usd,
            "finish_reason": self.finish_reason,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class StreamChunk:
    """
    Single chunk from streaming response.

    جزء واحد من الاستجابة المتدفقة
    """

    text: str
    is_final: bool = False
    tokens: int = 0
    finish_reason: str | None = None


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""

    def __init__(
        self,
        message: str,
        provider: ProviderType | None = None,
        status: GenerationStatus = GenerationStatus.ERROR,
    ):
        super().__init__(message)
        self.provider = provider
        self.status = status


class ModelNotFoundError(LLMProviderError):
    """Raised when a model is not found."""

    def __init__(self, model: str, provider: ProviderType | None = None):
        super().__init__(
            f"Model '{model}' not found",
            provider=provider,
            status=GenerationStatus.MODEL_NOT_FOUND,
        )
        self.model = model


class ProviderUnavailableError(LLMProviderError):
    """Raised when a provider is unavailable."""

    pass


class RateLimitError(LLMProviderError):
    """Raised when rate limited."""

    def __init__(self, message: str, retry_after: float | None = None):
        super().__init__(message, status=GenerationStatus.RATE_LIMITED)
        self.retry_after = retry_after


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    فئة أساسية مجردة لمزودي نماذج اللغة الكبيرة

    All LLM providers must implement this interface for:
    - Text generation
    - Chat completion
    - Streaming support
    - Health checks

    Example implementation:
        class MyProvider(LLMProvider):
            @property
            def provider_type(self) -> ProviderType:
                return ProviderType.LOCAL

            async def generate(self, prompt, ...) -> GenerationResponse:
                # Implementation
                pass
    """

    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Get the provider type."""
        ...

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Get the default model for this provider."""
        ...

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        options: GenerationOptions | None = None,
    ) -> GenerationResponse:
        """
        Generate text from a prompt.

        توليد نص من موجه

        Args:
            prompt: The user prompt
            model: Model to use (defaults to provider default)
            system_prompt: Optional system prompt
            options: Generation options

        Returns:
            GenerationResponse with generated text

        Raises:
            LLMProviderError: If generation fails
        """
        ...

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        options: GenerationOptions | None = None,
    ) -> GenerationResponse:
        """
        Chat completion with message history.

        إكمال الدردشة مع سجل الرسائل

        Args:
            messages: List of chat messages
            model: Model to use
            options: Generation options

        Returns:
            GenerationResponse with assistant reply
        """
        ...

    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        options: GenerationOptions | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """
        Generate text with streaming.

        توليد نص مع التدفق

        Args:
            prompt: The user prompt
            model: Model to use
            system_prompt: Optional system prompt
            options: Generation options

        Yields:
            StreamChunk objects with text fragments
        """
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the provider is available.

        التحقق من توفر المزود

        Returns:
            True if provider is available and responding
        """
        ...

    @abstractmethod
    async def list_models(self) -> list[str]:
        """
        List available models.

        قائمة النماذج المتاحة

        Returns:
            List of available model names
        """
        ...

    async def is_model_available(self, model: str) -> bool:
        """
        Check if a specific model is available.

        التحقق من توفر نموذج محدد
        """
        try:
            models = await self.list_models()
            # Check exact match or partial match (for versioned models)
            return model in models or any(model in m for m in models)
        except Exception:
            return False

    async def close(self) -> None:
        """
        Close provider resources.

        إغلاق موارد المزود

        Override this method if the provider needs cleanup.
        """
        pass

    async def __aenter__(self) -> LLMProvider:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
