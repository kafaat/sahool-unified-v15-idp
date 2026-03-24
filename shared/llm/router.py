"""
LLM Router Module
=================
وحدة توجيه نماذج اللغة الكبيرة

Routes LLM requests to appropriate providers based on:
- Environment (development uses local, production uses cloud)
- Model capability requirements
- Cost optimization
- Provider availability

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .config import (
    LLMConfig,
    ModelCapability,
    get_config,
    get_model_info,
    get_models_by_capability,
)
from .ollama import OllamaProvider
from .openai_compat import OpenAICompatProvider
from .provider import (
    GenerationOptions,
    GenerationResponse,
    LLMProvider,
    LLMProviderError,
    Message,
    ProviderType,
    ProviderUnavailableError,
    StreamChunk,
)

logger = logging.getLogger(__name__)


class AllProvidersFailedError(LLMProviderError):
    """Raised when all providers fail."""

    def __init__(self, errors: list[tuple[ProviderType, str]]):
        self.errors = errors
        message = "All LLM providers failed:\n" + "\n".join(f"  - {p.value}: {e}" for p, e in errors)
        super().__init__(message)


@dataclass
class RoutingDecision:
    """
    Decision about which provider to use.

    قرار حول المزود الذي سيتم استخدامه
    """

    provider_type: ProviderType
    model: str
    reason: str
    fallbacks: list[tuple[ProviderType, str]] = field(default_factory=list)


@dataclass
class RouterStats:
    """Statistics for the router."""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    fallback_count: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    provider_usage: dict[str, int] = field(default_factory=dict)
    last_request: datetime | None = None


class LLMRouter:
    """
    Intelligent LLM request router.

    موجه ذكي لطلبات نماذج اللغة الكبيرة

    Routes requests to the most appropriate provider based on:
    - Environment (dev=local, prod=cloud)
    - Model capability needed
    - Cost optimization
    - Provider availability

    Example:
        router = LLMRouter()

        # Automatically uses Ollama in dev, OpenAI in prod
        response = await router.generate(
            prompt="ما هي أفضل طريقة لري القمح؟",
            model="auto"  # Picks best available
        )

        # Force specific provider
        response = await router.generate(
            prompt="Generate Python code",
            capabilities=[ModelCapability.CODE],
            prefer_local=True
        )

        # With fallback
        response = await router.generate(
            prompt="Hello world",
            enable_fallback=True
        )
    """

    def __init__(self, config: LLMConfig | None = None):
        """
        Initialize LLM Router.

        Args:
            config: LLM configuration (uses global config if None)
        """
        self._config = config or get_config()
        self._providers: dict[ProviderType, LLMProvider] = {}
        self._stats = RouterStats()
        self._provider_available: dict[ProviderType, bool | None] = {}

    @property
    def config(self) -> LLMConfig:
        """Get configuration."""
        return self._config

    @property
    def stats(self) -> RouterStats:
        """Get router statistics."""
        return self._stats

    async def _get_provider(self, provider_type: ProviderType) -> LLMProvider | None:
        """Get or create a provider instance."""
        if provider_type in self._providers:
            return self._providers[provider_type]

        try:
            if provider_type == ProviderType.OLLAMA:
                provider = OllamaProvider(self._config.ollama)
            elif provider_type == ProviderType.OPENAI_COMPAT:
                provider = OpenAICompatProvider(self._config.openai_compat)
            else:
                return None

            self._providers[provider_type] = provider
            return provider
        except Exception as e:
            logger.warning(f"Failed to create provider {provider_type}: {e}")
            return None

    async def _check_provider_available(self, provider_type: ProviderType) -> bool:
        """Check if a provider is available (with caching)."""
        # Return cached result if recent
        cached = self._provider_available.get(provider_type)
        if cached is not None:
            return cached

        provider = await self._get_provider(provider_type)
        if provider is None:
            self._provider_available[provider_type] = False
            return False

        try:
            available = await asyncio.wait_for(provider.is_available(), timeout=5.0)
            self._provider_available[provider_type] = available
            return available
        except TimeoutError:
            self._provider_available[provider_type] = False
            return False
        except Exception:
            self._provider_available[provider_type] = False
            return False

    def _select_model(
        self,
        model: str | None,
        capabilities: list[ModelCapability] | None,
        prefer_local: bool,
    ) -> tuple[str, ProviderType]:
        """
        Select the best model based on requirements.

        اختيار أفضل نموذج بناءً على المتطلبات
        """
        # If specific model requested, use it
        if model and model != "auto":
            info = get_model_info(model)
            if info:
                provider = ProviderType.OLLAMA if info["provider"] == "ollama" else ProviderType.OPENAI
                return model, provider
            # Unknown model, try Ollama first
            return model, ProviderType.OLLAMA

        # Auto-select based on capabilities
        if capabilities:
            # Find models with required capabilities
            matching_models = set(get_models_by_capability(capabilities[0]))
            for cap in capabilities[1:]:
                matching_models &= set(get_models_by_capability(cap))

            # Filter by preference
            if prefer_local:
                local_matches = [
                    m for m in matching_models if get_model_info(m) and get_model_info(m).get("provider") == "ollama"
                ]
                if local_matches:
                    # Prefer qwen2.5 for multilingual, codellama for code
                    if ModelCapability.MULTILINGUAL in capabilities:
                        if "qwen2.5" in local_matches:
                            return "qwen2.5", ProviderType.OLLAMA
                    if ModelCapability.CODE in capabilities:
                        if "codellama" in local_matches:
                            return "codellama", ProviderType.OLLAMA
                    return local_matches[0], ProviderType.OLLAMA

        # Default selection based on environment
        if prefer_local or self._config.is_development:
            return self._config.ollama.default_model, ProviderType.OLLAMA
        else:
            return self._config.cloud.openai_model, ProviderType.OPENAI

    async def decide_routing(
        self,
        model: str | None = None,
        capabilities: list[ModelCapability] | None = None,
        prefer_local: bool | None = None,
    ) -> RoutingDecision:
        """
        Decide which provider and model to use.

        تحديد المزود والنموذج المراد استخدامهما

        Args:
            model: Specific model to use, or "auto"
            capabilities: Required model capabilities
            prefer_local: Prefer local models (defaults to config)

        Returns:
            RoutingDecision with provider and model selection
        """
        if prefer_local is None:
            prefer_local = self._config.prefer_local

        selected_model, selected_provider = self._select_model(model, capabilities, prefer_local)

        # Build fallback list
        fallbacks: list[tuple[ProviderType, str]] = []

        # Add fallbacks based on provider
        if selected_provider == ProviderType.OLLAMA:
            # Ollama -> OpenAI compat -> Cloud
            fallbacks.append((ProviderType.OPENAI_COMPAT, selected_model))
            if self._config.cloud.openai_api_key:
                fallbacks.append((ProviderType.OPENAI, self._config.cloud.openai_model))
        elif selected_provider == ProviderType.OPENAI_COMPAT:
            fallbacks.append((ProviderType.OLLAMA, self._config.ollama.default_model))

        reason = (
            f"Selected {selected_provider.value} with model {selected_model} "
            f"(prefer_local={prefer_local}, env={self._config.environment.value})"
        )

        return RoutingDecision(
            provider_type=selected_provider,
            model=selected_model,
            reason=reason,
            fallbacks=fallbacks,
        )

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        options: GenerationOptions | None = None,
        capabilities: list[ModelCapability] | None = None,
        prefer_local: bool | None = None,
        enable_fallback: bool | None = None,
    ) -> GenerationResponse:
        """
        Generate text using the best available provider.

        توليد نص باستخدام أفضل مزود متاح

        Args:
            prompt: User prompt
            model: Model to use ("auto" for automatic selection)
            system_prompt: Optional system prompt
            options: Generation options
            capabilities: Required model capabilities
            prefer_local: Prefer local models
            enable_fallback: Enable fallback to other providers

        Returns:
            GenerationResponse with generated text

        Raises:
            AllProvidersFailedError: If all providers fail
        """
        if enable_fallback is None:
            enable_fallback = self._config.enable_fallback

        # Get routing decision
        decision = await self.decide_routing(
            model=model,
            capabilities=capabilities,
            prefer_local=prefer_local,
        )

        # Track stats
        self._stats.total_requests += 1
        self._stats.last_request = datetime.now(UTC)

        # Build provider list to try
        providers_to_try = [(decision.provider_type, decision.model)]
        if enable_fallback:
            providers_to_try.extend(decision.fallbacks)

        errors: list[tuple[ProviderType, str]] = []

        for provider_type, model_name in providers_to_try:
            # Check availability
            if not await self._check_provider_available(provider_type):
                errors.append((provider_type, "Provider unavailable"))
                continue

            provider = await self._get_provider(provider_type)
            if provider is None:
                errors.append((provider_type, "Failed to create provider"))
                continue

            try:
                response = await provider.generate(
                    prompt=prompt,
                    model=model_name,
                    system_prompt=system_prompt,
                    options=options,
                )

                # Update stats
                self._stats.successful_requests += 1
                self._stats.total_tokens += response.total_tokens
                self._stats.total_cost_usd += response.cost_usd
                self._stats.provider_usage[provider_type.value] = (
                    self._stats.provider_usage.get(provider_type.value, 0) + 1
                )

                if errors:
                    self._stats.fallback_count += 1
                    logger.info(f"Used fallback provider {provider_type.value} after {len(errors)} failures")

                return response

            except Exception as e:
                errors.append((provider_type, str(e)))
                logger.warning(f"Provider {provider_type.value} failed: {e}")

                # Clear availability cache on error
                self._provider_available[provider_type] = None

                if not enable_fallback:
                    break

        # All providers failed
        self._stats.failed_requests += 1
        raise AllProvidersFailedError(errors)

    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        options: GenerationOptions | None = None,
        capabilities: list[ModelCapability] | None = None,
        prefer_local: bool | None = None,
        enable_fallback: bool | None = None,
    ) -> GenerationResponse:
        """
        Chat completion using the best available provider.

        إكمال الدردشة باستخدام أفضل مزود متاح

        Args:
            messages: List of chat messages
            model: Model to use
            options: Generation options
            capabilities: Required capabilities
            prefer_local: Prefer local models
            enable_fallback: Enable fallback

        Returns:
            GenerationResponse with assistant reply
        """
        if enable_fallback is None:
            enable_fallback = self._config.enable_fallback

        decision = await self.decide_routing(
            model=model,
            capabilities=capabilities,
            prefer_local=prefer_local,
        )

        self._stats.total_requests += 1
        self._stats.last_request = datetime.now(UTC)

        providers_to_try = [(decision.provider_type, decision.model)]
        if enable_fallback:
            providers_to_try.extend(decision.fallbacks)

        errors: list[tuple[ProviderType, str]] = []

        for provider_type, model_name in providers_to_try:
            if not await self._check_provider_available(provider_type):
                errors.append((provider_type, "Provider unavailable"))
                continue

            provider = await self._get_provider(provider_type)
            if provider is None:
                errors.append((provider_type, "Failed to create provider"))
                continue

            try:
                response = await provider.chat(
                    messages=messages,
                    model=model_name,
                    options=options,
                )

                self._stats.successful_requests += 1
                self._stats.total_tokens += response.total_tokens
                self._stats.total_cost_usd += response.cost_usd
                self._stats.provider_usage[provider_type.value] = (
                    self._stats.provider_usage.get(provider_type.value, 0) + 1
                )

                if errors:
                    self._stats.fallback_count += 1

                return response

            except Exception as e:
                errors.append((provider_type, str(e)))
                self._provider_available[provider_type] = None

                if not enable_fallback:
                    break

        self._stats.failed_requests += 1
        raise AllProvidersFailedError(errors)

    async def generate_stream(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        options: GenerationOptions | None = None,
        capabilities: list[ModelCapability] | None = None,
        prefer_local: bool | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """
        Generate text with streaming.

        توليد نص مع التدفق

        Note: Fallback is not supported for streaming.

        Args:
            prompt: User prompt
            model: Model to use
            system_prompt: Optional system prompt
            options: Generation options
            capabilities: Required capabilities
            prefer_local: Prefer local models

        Yields:
            StreamChunk objects with text fragments
        """
        decision = await self.decide_routing(
            model=model,
            capabilities=capabilities,
            prefer_local=prefer_local,
        )

        self._stats.total_requests += 1
        self._stats.last_request = datetime.now(UTC)

        provider = await self._get_provider(decision.provider_type)
        if provider is None:
            raise ProviderUnavailableError(f"Provider {decision.provider_type.value} is not available")

        try:
            async for chunk in provider.generate_stream(
                prompt=prompt,
                model=decision.model,
                system_prompt=system_prompt,
                options=options,
            ):
                yield chunk

            self._stats.successful_requests += 1
            self._stats.provider_usage[decision.provider_type.value] = (
                self._stats.provider_usage.get(decision.provider_type.value, 0) + 1
            )

        except Exception:
            self._stats.failed_requests += 1
            raise

    async def close(self) -> None:
        """Close all provider connections."""
        for provider in self._providers.values():
            try:
                await provider.close()
            except Exception as e:
                logger.warning(f"Error closing provider: {e}")
        self._providers.clear()
        self._provider_available.clear()

    async def __aenter__(self) -> LLMRouter:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def get_status(self) -> dict[str, Any]:
        """
        Get router status and statistics.

        الحصول على حالة الموجه والإحصائيات
        """
        return {
            "config": {
                "environment": self._config.environment.value,
                "prefer_local": self._config.prefer_local,
                "enable_fallback": self._config.enable_fallback,
            },
            "providers": {
                pt.value: self._provider_available.get(pt, "unknown")
                for pt in [ProviderType.OLLAMA, ProviderType.OPENAI_COMPAT]
            },
            "stats": {
                "total_requests": self._stats.total_requests,
                "successful_requests": self._stats.successful_requests,
                "failed_requests": self._stats.failed_requests,
                "fallback_count": self._stats.fallback_count,
                "total_tokens": self._stats.total_tokens,
                "total_cost_usd": self._stats.total_cost_usd,
                "provider_usage": self._stats.provider_usage,
                "last_request": (self._stats.last_request.isoformat() if self._stats.last_request else None),
            },
        }


# Global router instance
_global_router: LLMRouter | None = None


def get_router() -> LLMRouter:
    """
    Get the global LLM router instance.

    الحصول على مثيل موجه LLM العالمي
    """
    global _global_router
    if _global_router is None:
        _global_router = LLMRouter()
    return _global_router


async def generate(
    prompt: str,
    model: str | None = None,
    system_prompt: str | None = None,
    **kwargs: Any,
) -> GenerationResponse:
    """
    Generate text using the global router.

    توليد نص باستخدام الموجه العالمي

    Args:
        prompt: User prompt
        model: Model to use ("auto" for automatic)
        system_prompt: Optional system prompt
        **kwargs: Additional options

    Returns:
        GenerationResponse with generated text
    """
    router = get_router()
    return await router.generate(
        prompt=prompt,
        model=model,
        system_prompt=system_prompt,
        **kwargs,
    )


async def chat(
    messages: list[Message],
    model: str | None = None,
    **kwargs: Any,
) -> GenerationResponse:
    """
    Chat completion using the global router.

    إكمال الدردشة باستخدام الموجه العالمي
    """
    router = get_router()
    return await router.chat(messages=messages, model=model, **kwargs)
