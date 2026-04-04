"""
LLM Adapter for OpenMultiAgent
===============================
محول نماذج اللغة الكبيرة لإطار OpenMultiAgent

Wraps LLMProviderManager with an adapter pattern providing a clean,
provider-specific interface for agent runners.

Adapters:
    - AnthropicAdapter: Claude models via LLMProvider.ANTHROPIC
    - OpenAIAdapter: GPT models via LLMProvider.OPENAI
    - OllamaAdapter: Local models via LLMProvider.OLLAMA
    - CopilotAdapter: GitHub Copilot API (placeholder)

المحولات:
    - AnthropicAdapter: نماذج Claude عبر LLMProvider.ANTHROPIC
    - OpenAIAdapter: نماذج GPT عبر LLMProvider.OPENAI
    - OllamaAdapter: نماذج محلية عبر LLMProvider.OLLAMA
    - CopilotAdapter: واجهة GitHub Copilot (عنصر نائب)

Author: SAHOOL Platform Team
Updated: April 2026
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

import structlog

from shared.ai.llm_provider import (
    LLMConfig,
    LLMProvider,
    LLMProviderManager,
    LLMResponse,
)

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Base adapter
# ---------------------------------------------------------------------------


class LLMAdapter(ABC):
    """
    Abstract base for provider-specific LLM adapters.

    قاعدة مجردة لمحولات مزودي نماذج اللغة الكبيرة.

    Each concrete adapter maps to a single :class:`LLMProvider` and
    delegates actual inference to the shared :class:`LLMProviderManager`.
    """

    def __init__(
        self,
        manager: LLMProviderManager,
        *,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self._manager = manager
        self._system_prompt = system_prompt
        self._temperature = temperature
        self._max_tokens = max_tokens

    # -- abstract ----------------------------------------------------------

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the canonical provider name (e.g. ``'anthropic'``)."""

    @abstractmethod
    def _get_provider(self) -> LLMProvider:
        """Return the :class:`LLMProvider` enum member for this adapter."""

    # -- public interface --------------------------------------------------

    def is_available(self) -> bool:
        """
        Check whether the underlying provider is enabled and reachable.

        التحقق مما إذا كان المزود الأساسي مفعلاً ويمكن الوصول إليه.
        """
        provider = self._get_provider()
        for cfg in self._manager.configs:
            if cfg.provider == provider and cfg.enabled:
                return True
        return False

    async def prompt(self, text: str, **kwargs: Any) -> str:
        """
        Send a single prompt and return the generated text.

        إرسال طلب واحد وإرجاع النص المولد.

        Args:
            text: The prompt text.
            **kwargs: Forwarded to :meth:`LLMProviderManager.generate`.

        Returns:
            Generated text string.
        """
        merged: dict[str, Any] = {
            "prompt": text,
            "preferred_provider": self._get_provider(),
            "fallback": kwargs.pop("fallback", False),
        }
        if self._system_prompt is not None:
            merged.setdefault("system_prompt", self._system_prompt)
        if self._temperature is not None:
            merged.setdefault("temperature", self._temperature)
        if self._max_tokens is not None:
            merged.setdefault("max_tokens", self._max_tokens)
        merged.update(kwargs)

        response: LLMResponse = await self._manager.generate(**merged)
        logger.debug(
            "llm_adapter.prompt",
            provider=self.get_provider_name(),
            tokens_in=response.tokens_input,
            tokens_out=response.tokens_output,
            latency_ms=response.latency_ms,
        )
        return response.text

    async def stream(self, text: str, **kwargs: Any) -> AsyncIterator[str]:
        """
        Stream generated text chunk-by-chunk.

        تدفق النص المولد جزءاً بجزء.

        Args:
            text: The prompt text.
            **kwargs: Forwarded to :meth:`LLMProviderManager.generate_stream`.

        Yields:
            Text chunks as they arrive from the provider.
        """
        merged: dict[str, Any] = {
            "prompt": text,
            "preferred_provider": self._get_provider(),
        }
        if self._system_prompt is not None:
            merged.setdefault("system_prompt", self._system_prompt)
        if self._temperature is not None:
            merged.setdefault("temperature", self._temperature)
        if self._max_tokens is not None:
            merged.setdefault("max_tokens", self._max_tokens)
        merged.update(kwargs)

        async for chunk in self._manager.generate_stream(**merged):
            yield chunk


# ---------------------------------------------------------------------------
# Concrete adapters
# ---------------------------------------------------------------------------


class AnthropicAdapter(LLMAdapter):
    """Adapter for Anthropic Claude models. | محول لنماذج Claude من Anthropic."""

    def get_provider_name(self) -> str:
        return "anthropic"

    def _get_provider(self) -> LLMProvider:
        return LLMProvider.ANTHROPIC


class OpenAIAdapter(LLMAdapter):
    """Adapter for OpenAI GPT models. | محول لنماذج GPT من OpenAI."""

    def get_provider_name(self) -> str:
        return "openai"

    def _get_provider(self) -> LLMProvider:
        return LLMProvider.OPENAI


class OllamaAdapter(LLMAdapter):
    """Adapter for locally-hosted Ollama models. | محول لنماذج Ollama المحلية."""

    def get_provider_name(self) -> str:
        return "ollama"

    def _get_provider(self) -> LLMProvider:
        return LLMProvider.OLLAMA


class CopilotAdapter(LLMAdapter):
    """
    Placeholder adapter for GitHub Copilot API.

    عنصر نائب لمحول واجهة GitHub Copilot.

    This adapter is not yet backed by a real provider in
    :class:`LLMProviderManager`.  Calls will raise ``NotImplementedError``
    until the Copilot integration is completed.
    """

    def __init__(
        self,
        manager: LLMProviderManager,
        *,
        copilot_token: str | None = None,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        super().__init__(
            manager,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self._copilot_token = copilot_token

    def get_provider_name(self) -> str:
        return "copilot"

    def _get_provider(self) -> LLMProvider:
        # No enum value yet; kept here for interface symmetry.
        raise NotImplementedError(
            "CopilotAdapter is a placeholder. "
            "GitHub Copilot provider is not yet registered in LLMProvider."
        )

    def is_available(self) -> bool:
        """Copilot is not yet available. | Copilot غير متاح بعد."""
        return False

    async def prompt(self, text: str, **kwargs: Any) -> str:
        raise NotImplementedError("GitHub Copilot integration is not yet implemented.")

    async def stream(self, text: str, **kwargs: Any) -> AsyncIterator[str]:
        raise NotImplementedError("GitHub Copilot integration is not yet implemented.")
        # Required for the function to be recognised as an async generator.
        yield ""  # pragma: no cover


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_ADAPTER_MAP: dict[str, type[LLMAdapter]] = {
    "anthropic": AnthropicAdapter,
    "openai": OpenAIAdapter,
    "ollama": OllamaAdapter,
    "copilot": CopilotAdapter,
}


class AdapterFactory:
    """
    Factory for creating :class:`LLMAdapter` instances by provider name.

    مصنع لإنشاء محولات LLM حسب اسم المزود.

    Example::

        from shared.ai.open_multi_agent.llm_adapter import AdapterFactory

        adapter = AdapterFactory.create("anthropic", manager)
        answer = await adapter.prompt("Explain photosynthesis")
    """

    @staticmethod
    def create(
        provider: str,
        manager: LLMProviderManager,
        **kwargs: Any,
    ) -> LLMAdapter:
        """
        Create an adapter for the given provider name.

        إنشاء محول لاسم المزود المحدد.

        Args:
            provider: One of ``'anthropic'``, ``'openai'``, ``'ollama'``,
                      ``'copilot'``.
            manager: The shared :class:`LLMProviderManager` instance.
            **kwargs: Forwarded to the adapter constructor (e.g.
                      ``system_prompt``, ``temperature``).

        Returns:
            A concrete :class:`LLMAdapter` subclass instance.

        Raises:
            ValueError: If *provider* is not recognised.
        """
        key = provider.lower().strip()
        adapter_cls = _ADAPTER_MAP.get(key)
        if adapter_cls is None:
            supported = ", ".join(sorted(_ADAPTER_MAP))
            raise ValueError(
                f"Unknown LLM adapter provider '{provider}'. "
                f"Supported: {supported}"
            )
        return adapter_cls(manager, **kwargs)

    @staticmethod
    def available_providers() -> list[str]:
        """Return the list of supported provider names."""
        return sorted(_ADAPTER_MAP)
