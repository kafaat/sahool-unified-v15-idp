"""
LLM Provider Manager
====================
مدير مزودي نماذج اللغة الكبيرة

Unified interface for multiple LLM providers with:
- Automatic failover between providers
- Circuit breaker integration
- Cost tracking and audit logging
- Rate limiting support

Supported Providers:
    - Ollama (local, offline-first)
    - Anthropic (Claude)
    - OpenAI (GPT)
    - Google (Gemini)
    - DeepSeek (Code-specialized)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from .audit import calculate_cost, get_audit_logger
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerError,
    get_circuit_breaker,
)
from .metrics import get_metrics_collector

logger = logging.getLogger(__name__)


class LLMProvider(StrEnum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"


@dataclass
class LLMConfig:
    """Configuration for an LLM provider."""

    provider: LLMProvider
    model: str
    api_key: str | None = None
    base_url: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 120.0
    enabled: bool = True
    priority: int = 0  # Lower = higher priority

    @classmethod
    def from_env(cls, provider: LLMProvider) -> LLMConfig:
        """Create config from environment variables."""
        if provider == LLMProvider.OLLAMA:
            return cls(
                provider=provider,
                model=os.getenv("OLLAMA_MODEL", "codellama:13b"),
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                priority=0,  # Highest priority (offline-first)
            )
        elif provider == LLMProvider.ANTHROPIC:
            return cls(
                provider=provider,
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307"),
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                priority=1,
                enabled=bool(os.getenv("ANTHROPIC_API_KEY")),
            )
        elif provider == LLMProvider.OPENAI:
            return cls(
                provider=provider,
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                api_key=os.getenv("OPENAI_API_KEY"),
                priority=2,
                enabled=bool(os.getenv("OPENAI_API_KEY")),
            )
        elif provider == LLMProvider.GOOGLE:
            return cls(
                provider=provider,
                model=os.getenv("GOOGLE_MODEL", "gemini-1.5-flash"),
                api_key=os.getenv("GOOGLE_API_KEY"),
                priority=3,
                enabled=bool(os.getenv("GOOGLE_API_KEY")),
            )
        elif provider == LLMProvider.DEEPSEEK:
            return cls(
                provider=provider,
                model=os.getenv("DEEPSEEK_MODEL", "deepseek-coder"),
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                priority=4,
                enabled=bool(os.getenv("DEEPSEEK_API_KEY")),
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")


@dataclass
class LLMResponse:
    """Unified response from any LLM provider."""

    text: str
    provider: LLMProvider
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    finish_reason: str | None = None
    raw_response: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "provider": self.provider.value,
            "model": self.model,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "finish_reason": self.finish_reason,
            "created_at": self.created_at.isoformat(),
        }


class LLMProviderError(Exception):
    """Exception raised for LLM provider errors."""

    def __init__(self, message: str, provider: LLMProvider | None = None):
        super().__init__(message)
        self.provider = provider


class AllProvidersFailedError(LLMProviderError):
    """Exception raised when all providers fail."""

    def __init__(self, errors: list[tuple[LLMProvider, str]]):
        self.errors = errors
        message = "All LLM providers failed:\n" + "\n".join(f"  - {p.value}: {e}" for p, e in errors)
        super().__init__(message)


class LLMProviderManager:
    """
    Unified manager for multiple LLM providers.

    مدير موحد لمزودي نماذج اللغة الكبيرة

    Features:
        - Automatic failover between providers
        - Circuit breaker for each provider
        - Cost tracking and audit logging
        - Offline-first with Ollama priority

    Example:
        manager = LLMProviderManager()

        # Generate with automatic fallback
        response = await manager.generate(
            prompt="Explain photosynthesis",
            system_prompt="You are an agricultural expert"
        )

        print(f"Response from {response.provider}: {response.text}")
        print(f"Cost: ${response.cost_usd:.4f}")
    """

    def __init__(
        self,
        configs: list[LLMConfig] | None = None,
        tenant_id: str = "sahool",
        enable_audit: bool = True,
        enable_metrics: bool = True,
    ):
        """
        Initialize LLMProviderManager.

        Args:
            configs: List of provider configurations (auto-detected if None)
            tenant_id: Tenant ID for audit logging
            enable_audit: Enable audit logging
            enable_metrics: Enable metrics collection
        """
        self.tenant_id = tenant_id
        self.enable_audit = enable_audit
        self.enable_metrics = enable_metrics

        # Initialize configs
        if configs:
            self.configs = {c.provider: c for c in configs}
        else:
            self.configs = self._auto_detect_configs()

        # Sort by priority
        self._provider_order = sorted(
            [p for p, c in self.configs.items() if c.enabled],
            key=lambda p: self.configs[p].priority,
        )

        # Initialize circuit breakers
        self._circuit_breakers: dict[LLMProvider, CircuitBreaker] = {}
        for provider in self._provider_order:
            self._circuit_breakers[provider] = get_circuit_breaker(
                f"llm_{provider.value}",
                CircuitBreakerConfig(
                    failure_threshold=3,
                    success_threshold=2,
                    timeout_seconds=60.0 if provider == LLMProvider.OLLAMA else 120.0,
                ),
            )

        # Audit logger and metrics
        self._audit_logger = get_audit_logger(tenant_id) if enable_audit else None
        self._metrics = get_metrics_collector() if enable_metrics else None

        # HTTP clients (lazy init)
        self._http_clients: dict[LLMProvider, Any] = {}

    def _auto_detect_configs(self) -> dict[LLMProvider, LLMConfig]:
        """Auto-detect available providers from environment."""
        configs = {}
        for provider in LLMProvider:
            try:
                config = LLMConfig.from_env(provider)
                configs[provider] = config
            except Exception as e:
                logger.debug(f"Provider {provider.value} not configured: {e}")
        return configs

    @property
    def available_providers(self) -> list[LLMProvider]:
        """Get list of available providers in priority order."""
        return [p for p in self._provider_order if not self._circuit_breakers[p].is_open]

    def get_provider_status(self) -> dict[str, Any]:
        """Get status of all providers."""
        return {
            provider.value: {
                "enabled": self.configs[provider].enabled,
                "model": self.configs[provider].model,
                "circuit_breaker": self._circuit_breakers[provider].get_status()
                if provider in self._circuit_breakers
                else None,
            }
            for provider in self.configs
        }

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        preferred_provider: LLMProvider | None = None,
        fallback: bool = True,
        correlation_id: str | None = None,
    ) -> LLMResponse:
        """
        Generate text using available LLM providers.

        توليد نص باستخدام مزودي LLM المتاحين

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Override temperature
            max_tokens: Override max tokens
            preferred_provider: Try this provider first
            fallback: Enable fallback to other providers
            correlation_id: Correlation ID for audit

        Returns:
            LLMResponse with generated text

        Raises:
            AllProvidersFailedError: If all providers fail
        """
        errors: list[tuple[LLMProvider, str]] = []

        # Build provider order
        providers = list(self._provider_order)
        if preferred_provider and preferred_provider in providers:
            providers.remove(preferred_provider)
            providers.insert(0, preferred_provider)

        for provider in providers:
            if not self.configs[provider].enabled:
                continue

            breaker = self._circuit_breakers.get(provider)
            if breaker and breaker.is_open:
                errors.append((provider, "Circuit breaker open"))
                if not fallback:
                    break
                continue

            try:
                response = await self._generate_with_provider(
                    provider=provider,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    correlation_id=correlation_id,
                )

                # Log fallback if not first provider
                if errors and self._audit_logger:
                    self._audit_logger.log_llm_fallback(
                        correlation_id=correlation_id or "",
                        from_provider=errors[-1][0].value,
                        to_provider=provider.value,
                        reason=errors[-1][1],
                    )

                return response

            except CircuitBreakerError as e:
                errors.append((provider, f"Circuit breaker: {e}"))
            except Exception as e:
                errors.append((provider, str(e)))

                # Record failure in circuit breaker
                if breaker:
                    # The failure is already recorded by the circuit breaker call
                    pass

            if not fallback:
                break

        raise AllProvidersFailedError(errors)

    async def _generate_with_provider(
        self,
        provider: LLMProvider,
        prompt: str,
        system_prompt: str | None,
        temperature: float | None,
        max_tokens: int | None,
        correlation_id: str | None,
    ) -> LLMResponse:
        """Generate using a specific provider."""
        config = self.configs[provider]
        breaker = self._circuit_breakers.get(provider)

        start_time = datetime.now(UTC)

        # Use circuit breaker if available
        if breaker:
            response = await breaker.call(
                self._call_provider,
                provider,
                prompt,
                system_prompt,
                temperature or config.temperature,
                max_tokens or config.max_tokens,
            )
        else:
            response = await self._call_provider(
                provider,
                prompt,
                system_prompt,
                temperature or config.temperature,
                max_tokens or config.max_tokens,
            )

        latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
        response.latency_ms = latency_ms

        # Calculate cost
        response.cost_usd = calculate_cost(
            provider.value,
            config.model,
            response.tokens_input,
            response.tokens_output,
        )

        # Record metrics
        if self._metrics:
            self._metrics.record_llm_call(
                provider=provider.value,
                model=config.model,
                latency_ms=latency_ms,
                tokens_input=response.tokens_input,
                tokens_output=response.tokens_output,
                cost_usd=response.cost_usd,
                success=True,
            )

        # Record audit
        if self._audit_logger:
            self._audit_logger.log_llm_response(
                correlation_id=correlation_id or "",
                llm_provider=provider.value,
                model_name=config.model,
                output_data={"text": response.text[:500]},  # Truncate for audit
                latency_ms=latency_ms,
                token_count_input=response.tokens_input,
                token_count_output=response.tokens_output,
            )

        return response

    async def _call_provider(
        self,
        provider: LLMProvider,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Call a specific LLM provider."""
        if provider == LLMProvider.OLLAMA:
            return await self._call_ollama(prompt, system_prompt, temperature, max_tokens)
        elif provider == LLMProvider.ANTHROPIC:
            return await self._call_anthropic(prompt, system_prompt, temperature, max_tokens)
        elif provider == LLMProvider.OPENAI:
            return await self._call_openai(prompt, system_prompt, temperature, max_tokens)
        elif provider == LLMProvider.GOOGLE:
            return await self._call_google(prompt, system_prompt, temperature, max_tokens)
        elif provider == LLMProvider.DEEPSEEK:
            return await self._call_deepseek(prompt, system_prompt, temperature, max_tokens)
        else:
            raise LLMProviderError(f"Unknown provider: {provider}", provider)

    async def _call_ollama(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Call Ollama API."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for Ollama", LLMProvider.OLLAMA)

        config = self.configs[LLMProvider.OLLAMA]

        async with httpx.AsyncClient(timeout=config.timeout) as client:
            response = await client.post(
                f"{config.base_url}/api/generate",
                json={
                    "model": config.model,
                    "prompt": prompt,
                    "system": system_prompt or "",
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()

            return LLMResponse(
                text=data.get("response", ""),
                provider=LLMProvider.OLLAMA,
                model=config.model,
                tokens_input=data.get("prompt_eval_count", 0),
                tokens_output=data.get("eval_count", 0),
                finish_reason="stop" if data.get("done") else None,
                raw_response=data,
            )

    async def _call_anthropic(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Call Anthropic API."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for Anthropic", LLMProvider.ANTHROPIC)

        config = self.configs[LLMProvider.ANTHROPIC]
        if not config.api_key:
            raise LLMProviderError("Anthropic API key not set", LLMProvider.ANTHROPIC)

        async with httpx.AsyncClient(timeout=config.timeout) as client:
            messages = [{"role": "user", "content": prompt}]

            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": config.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": config.model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "system": system_prompt or "You are a helpful assistant.",
                    "messages": messages,
                },
            )
            response.raise_for_status()
            data = response.json()

            text = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text += block.get("text", "")

            return LLMResponse(
                text=text,
                provider=LLMProvider.ANTHROPIC,
                model=config.model,
                tokens_input=data.get("usage", {}).get("input_tokens", 0),
                tokens_output=data.get("usage", {}).get("output_tokens", 0),
                finish_reason=data.get("stop_reason"),
                raw_response=data,
            )

    async def _call_openai(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Call OpenAI API."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for OpenAI", LLMProvider.OPENAI)

        config = self.configs[LLMProvider.OPENAI]
        if not config.api_key:
            raise LLMProviderError("OpenAI API key not set", LLMProvider.OPENAI)

        async with httpx.AsyncClient(timeout=config.timeout) as client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": config.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()

            text = data["choices"][0]["message"]["content"]

            return LLMResponse(
                text=text,
                provider=LLMProvider.OPENAI,
                model=config.model,
                tokens_input=data.get("usage", {}).get("prompt_tokens", 0),
                tokens_output=data.get("usage", {}).get("completion_tokens", 0),
                finish_reason=data["choices"][0].get("finish_reason"),
                raw_response=data,
            )

    async def _call_google(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Call Google Gemini API."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for Google", LLMProvider.GOOGLE)

        config = self.configs[LLMProvider.GOOGLE]
        if not config.api_key:
            raise LLMProviderError("Google API key not set", LLMProvider.GOOGLE)

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        async with httpx.AsyncClient(timeout=config.timeout) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{config.model}:generateContent",
                headers={"Content-Type": "application/json"},
                params={"key": config.api_key},
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()

            text = ""
            for candidate in data.get("candidates", []):
                for part in candidate.get("content", {}).get("parts", []):
                    text += part.get("text", "")

            usage = data.get("usageMetadata", {})

            return LLMResponse(
                text=text,
                provider=LLMProvider.GOOGLE,
                model=config.model,
                tokens_input=usage.get("promptTokenCount", 0),
                tokens_output=usage.get("candidatesTokenCount", 0),
                finish_reason=data.get("candidates", [{}])[0].get("finishReason"),
                raw_response=data,
            )

    async def _call_deepseek(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Call DeepSeek API (OpenAI-compatible)."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for DeepSeek", LLMProvider.DEEPSEEK)

        config = self.configs[LLMProvider.DEEPSEEK]
        if not config.api_key:
            raise LLMProviderError("DeepSeek API key not set", LLMProvider.DEEPSEEK)

        async with httpx.AsyncClient(timeout=config.timeout) as client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            base_url = config.base_url or "https://api.deepseek.com"
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": config.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()

            text = data["choices"][0]["message"]["content"]

            return LLMResponse(
                text=text,
                provider=LLMProvider.DEEPSEEK,
                model=config.model,
                tokens_input=data.get("usage", {}).get("prompt_tokens", 0),
                tokens_output=data.get("usage", {}).get("completion_tokens", 0),
                finish_reason=data["choices"][0].get("finish_reason"),
                raw_response=data,
            )

    async def close(self) -> None:
        """Close all HTTP clients."""
        for client in self._http_clients.values():
            if hasattr(client, "aclose"):
                await client.aclose()
        self._http_clients.clear()


# Global manager instance
_global_manager: LLMProviderManager | None = None


def get_llm_manager(tenant_id: str = "sahool") -> LLMProviderManager:
    """
    Get or create the global LLM provider manager.

    الحصول على أو إنشاء مدير مزودي LLM العالمي
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = LLMProviderManager(tenant_id=tenant_id)
    return _global_manager


# Convenience functions
async def generate_text(
    prompt: str,
    system_prompt: str | None = None,
    preferred_provider: LLMProvider | None = None,
    tenant_id: str = "sahool",
) -> LLMResponse:
    """
    Generate text using the global LLM manager.

    توليد نص باستخدام مدير LLM العالمي
    """
    manager = get_llm_manager(tenant_id)
    return await manager.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        preferred_provider=preferred_provider,
    )


async def generate_with_ollama_fallback(
    prompt: str,
    system_prompt: str | None = None,
    tenant_id: str = "sahool",
) -> LLMResponse:
    """
    Generate text with Ollama as primary, cloud as fallback.

    توليد نص مع Ollama كأساسي والسحابة كاحتياطي
    """
    return await generate_text(
        prompt=prompt,
        system_prompt=system_prompt,
        preferred_provider=LLMProvider.OLLAMA,
        tenant_id=tenant_id,
    )
