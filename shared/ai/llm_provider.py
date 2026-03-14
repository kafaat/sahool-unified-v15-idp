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

import hashlib
import json
import logging
import os
import time
from collections import OrderedDict
from collections.abc import AsyncIterator
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
    VLLM = "vllm"
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
        elif provider == LLMProvider.VLLM:
            vllm_url = os.getenv("VLLM_BASE_URL", "http://localhost:8270/v1")
            return cls(
                provider=provider,
                model=os.getenv("VLLM_MODEL", "deepseek-ai/deepseek-coder-6.7b-instruct"),
                base_url=vllm_url,
                priority=0,  # Same priority as Ollama (local GPU inference)
                enabled=bool(os.getenv("VLLM_BASE_URL")),
                timeout=300.0,  # Long timeout for large model inference
            )
        elif provider == LLMProvider.ANTHROPIC:
            return cls(
                provider=provider,
                model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
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
        elif provider == LLMProvider.VLLM:
            return await self._call_vllm(prompt, system_prompt, temperature, max_tokens)
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

    async def _call_vllm(
        self,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_tokens: int,
    ) -> LLMResponse:
        """Call vLLM API (OpenAI-compatible)."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for vLLM", LLMProvider.VLLM) from None

        config = self.configs[LLMProvider.VLLM]
        base_url = (config.base_url or "http://localhost:8270/v1").rstrip("/")

        async with httpx.AsyncClient(timeout=config.timeout) as client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
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
                provider=LLMProvider.VLLM,
                model=config.model,
                tokens_input=data.get("usage", {}).get("prompt_tokens", 0),
                tokens_output=data.get("usage", {}).get("completion_tokens", 0),
                finish_reason=data["choices"][0].get("finish_reason"),
                raw_response=data,
            )

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
            raise LLMProviderError("httpx required for Ollama", LLMProvider.OLLAMA) from None

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
            raise LLMProviderError("httpx required for Anthropic", LLMProvider.ANTHROPIC) from None

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
            raise LLMProviderError("httpx required for OpenAI", LLMProvider.OPENAI) from None

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
            raise LLMProviderError("httpx required for Google", LLMProvider.GOOGLE) from None

        config = self.configs[LLMProvider.GOOGLE]
        if not config.api_key:
            raise LLMProviderError("Google API key not set", LLMProvider.GOOGLE)

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        async with httpx.AsyncClient(timeout=config.timeout) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1/models/{config.model}:generateContent",
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
            raise LLMProviderError("httpx required for DeepSeek", LLMProvider.DEEPSEEK) from None

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

    # ─────────────────────────────────────────────────────────────────────────
    # G-15: Health Check for All Providers (especially Ollama)
    # فحص صحة جميع المزودين (خاصة Ollama)
    # ─────────────────────────────────────────────────────────────────────────

    async def check_health(self) -> dict[str, Any]:
        """
        Check health and availability of all configured LLM providers.

        فحص صحة وتوفر جميع مزودي LLM المُهيئين

        Performs provider-specific health checks:
        - Ollama: Checks API availability AND loaded model readiness
        - Cloud providers: Validates API key presence and endpoint reachability

        Returns:
            dict with per-provider health status and overall health

        Example:
            health = await manager.check_health()
            print(health["overall_status"])  # "healthy" | "degraded" | "unhealthy"
            print(health["providers"]["ollama"]["model_ready"])
        """
        results: dict[str, Any] = {}
        healthy_count = 0
        total_count = 0

        for provider, config in self.configs.items():
            if not config.enabled:
                results[provider.value] = {
                    "status": "disabled",
                    "status_ar": "معطل",
                    "enabled": False,
                }
                continue

            total_count += 1
            start_time = time.monotonic()

            try:
                if provider == LLMProvider.OLLAMA:
                    health = await self._check_ollama_health(config)
                elif provider == LLMProvider.VLLM:
                    health = await self._check_vllm_health(config)
                else:
                    health = await self._check_cloud_provider_health(provider, config)

                latency_ms = (time.monotonic() - start_time) * 1000
                health["latency_ms"] = round(latency_ms, 2)

                if health.get("status") == "healthy":
                    healthy_count += 1

                # Include circuit breaker state
                breaker = self._circuit_breakers.get(provider)
                if breaker:
                    health["circuit_breaker"] = breaker.state.value

                results[provider.value] = health

            except Exception as e:
                latency_ms = (time.monotonic() - start_time) * 1000
                results[provider.value] = {
                    "status": "unhealthy",
                    "status_ar": "غير سليم",
                    "error": str(e),
                    "latency_ms": round(latency_ms, 2),
                }

        # Determine overall health
        if total_count == 0:
            overall = "no_providers"
            overall_ar = "لا يوجد مزودين"
        elif healthy_count == total_count:
            overall = "healthy"
            overall_ar = "سليم"
        elif healthy_count > 0:
            overall = "degraded"
            overall_ar = "متدهور"
        else:
            overall = "unhealthy"
            overall_ar = "غير سليم"

        return {
            "overall_status": overall,
            "overall_status_ar": overall_ar,
            "healthy_providers": healthy_count,
            "total_providers": total_count,
            "providers": results,
            "checked_at": datetime.now(UTC).isoformat(),
        }

    async def _check_ollama_health(self, config: LLMConfig) -> dict[str, Any]:
        """
        Check Ollama health including model readiness.

        فحص صحة Ollama بما في ذلك جاهزية النموذج
        """
        try:
            import httpx
        except ImportError:
            return {
                "status": "unhealthy",
                "status_ar": "غير سليم",
                "error": "httpx not installed",
            }

        base_url = config.base_url or "http://localhost:11434"

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check API availability
            try:
                api_response = await client.get(f"{base_url}/api/tags")
                api_response.raise_for_status()
                api_data = api_response.json()
            except httpx.ConnectError:
                return {
                    "status": "unhealthy",
                    "status_ar": "غير سليم",
                    "error": f"Cannot connect to Ollama at {base_url}",
                    "api_reachable": False,
                    "model_ready": False,
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "status_ar": "غير سليم",
                    "error": f"Ollama API error: {e}",
                    "api_reachable": False,
                    "model_ready": False,
                }

            # Check if the configured model is available
            available_models = [m.get("name", "") for m in api_data.get("models", [])]
            model_ready = any(config.model in m or m.startswith(config.model.split(":")[0]) for m in available_models)

            # Attempt a lightweight generation to verify model is loaded
            model_loaded = False
            if model_ready:
                try:
                    test_response = await client.post(
                        f"{base_url}/api/generate",
                        json={
                            "model": config.model,
                            "prompt": "test",
                            "stream": False,
                            "options": {"num_predict": 1},
                        },
                        timeout=30.0,
                    )
                    model_loaded = test_response.status_code == 200
                except Exception:
                    model_loaded = False

            status = "healthy" if model_loaded else ("degraded" if model_ready else "unhealthy")
            status_ar = {"healthy": "سليم", "degraded": "متدهور", "unhealthy": "غير سليم"}[status]

            return {
                "status": status,
                "status_ar": status_ar,
                "api_reachable": True,
                "model": config.model,
                "model_available": model_ready,
                "model_loaded": model_loaded,
                "available_models": available_models[:10],  # Limit to 10
                "base_url": base_url,
            }

    async def _check_vllm_health(self, config: LLMConfig) -> dict[str, Any]:
        """Check vLLM health via OpenAI-compatible /v1/models endpoint."""
        try:
            import httpx
        except ImportError:
            return {"status": "unhealthy", "status_ar": "غير سليم", "error": "httpx not installed"}

        base_url = config.base_url or "http://localhost:8270/v1"
        # Strip /v1 suffix for models endpoint construction
        api_base = base_url.rstrip("/")

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{api_base}/models")
                resp.raise_for_status()
                data = resp.json()
                models = [m.get("id", "") for m in data.get("data", [])]
                model_ready = config.model in models or any(config.model in m for m in models)
                return {
                    "status": "healthy" if model_ready else "degraded",
                    "status_ar": "سليم" if model_ready else "متدهور",
                    "api_reachable": True,
                    "model": config.model,
                    "model_ready": model_ready,
                    "available_models": models[:10],
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "status_ar": "غير سليم",
                    "error": str(e),
                    "api_reachable": False,
                }

    async def _check_cloud_provider_health(self, provider: LLMProvider, config: LLMConfig) -> dict[str, Any]:
        """
        Check cloud provider health (Anthropic, OpenAI, Google, DeepSeek).

        فحص صحة مزود السحابة
        """
        # Verify API key is present
        if not config.api_key:
            return {
                "status": "unhealthy",
                "status_ar": "غير سليم",
                "error": f"API key not configured for {provider.value}",
                "api_key_set": False,
            }

        # Test endpoint reachability with a lightweight request
        try:
            import httpx
        except ImportError:
            return {
                "status": "unhealthy",
                "status_ar": "غير سليم",
                "error": "httpx not installed",
            }

        endpoints = {
            LLMProvider.ANTHROPIC: "https://api.anthropic.com/v1/messages",
            LLMProvider.OPENAI: "https://api.openai.com/v1/models",
            LLMProvider.GOOGLE: f"https://generativelanguage.googleapis.com/v1/models/{config.model}",
            LLMProvider.DEEPSEEK: f"{config.base_url or 'https://api.deepseek.com'}/v1/models",
        }

        url = endpoints.get(provider)
        if not url:
            return {
                "status": "unknown",
                "status_ar": "غير معروف",
                "error": f"No health endpoint for {provider.value}",
                "api_key_set": True,
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                headers: dict[str, str] = {}
                params: dict[str, str] = {}

                if provider == LLMProvider.ANTHROPIC:
                    headers = {
                        "x-api-key": config.api_key,
                        "anthropic-version": "2023-06-01",
                    }
                    # HEAD request is not supported; use a GET to models endpoint
                    url = "https://api.anthropic.com/v1/models"
                    resp = await client.get(url, headers=headers)
                elif provider == LLMProvider.OPENAI:
                    headers = {"Authorization": f"Bearer {config.api_key}"}
                    resp = await client.get(url, headers=headers)
                elif provider == LLMProvider.GOOGLE:
                    params = {"key": config.api_key}
                    resp = await client.get(url, params=params)
                elif provider == LLMProvider.DEEPSEEK:
                    headers = {"Authorization": f"Bearer {config.api_key}"}
                    resp = await client.get(url, headers=headers)
                else:
                    resp = await client.get(url)

                is_healthy = resp.status_code < 500
                return {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "status_ar": "سليم" if is_healthy else "غير سليم",
                    "api_key_set": True,
                    "model": config.model,
                    "http_status": resp.status_code,
                    "endpoint_reachable": True,
                }

            except httpx.ConnectError:
                return {
                    "status": "unhealthy",
                    "status_ar": "غير سليم",
                    "error": f"Cannot reach {provider.value} API endpoint",
                    "api_key_set": True,
                    "endpoint_reachable": False,
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "status_ar": "غير سليم",
                    "error": str(e),
                    "api_key_set": True,
                    "endpoint_reachable": False,
                }

    # ─────────────────────────────────────────────────────────────────────────
    # G-21: LLM Response Caching
    # تخزين استجابات LLM مؤقتاً
    # ─────────────────────────────────────────────────────────────────────────

    async def generate_cached(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        preferred_provider: LLMProvider | None = None,
        fallback: bool = True,
        correlation_id: str | None = None,
        cache_ttl_seconds: float = 300.0,
    ) -> LLMResponse:
        """
        Generate text with in-memory LRU caching for repeated prompts.

        توليد نص مع تخزين مؤقت LRU في الذاكرة للطلبات المتكررة

        Uses a cache key derived from (prompt, system_prompt, provider, temperature)
        to avoid redundant LLM calls for identical requests.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Override temperature
            max_tokens: Override max tokens
            preferred_provider: Try this provider first
            fallback: Enable fallback to other providers
            correlation_id: Correlation ID for audit
            cache_ttl_seconds: Cache entry time-to-live in seconds (default 5 minutes)

        Returns:
            LLMResponse (potentially from cache)

        Example:
            # Second call with identical params returns cached result
            r1 = await manager.generate_cached(prompt="What is wheat?")
            r2 = await manager.generate_cached(prompt="What is wheat?")
            # r2 is served from cache, no LLM call made
        """
        cache = _get_response_cache()

        # Build cache key
        provider_key = preferred_provider.value if preferred_provider else "auto"
        temp_key = temperature if temperature is not None else "default"
        cache_key = _build_cache_key(prompt, system_prompt, provider_key, str(temp_key))

        # Check cache
        cached = cache.get(cache_key, cache_ttl_seconds)
        if cached is not None:
            logger.debug(f"LLM cache hit for key {cache_key[:16]}...")
            if self._metrics:
                self._metrics.record_llm_call(
                    provider=cached.provider.value,
                    model=cached.model,
                    latency_ms=0.0,
                    tokens_input=0,
                    tokens_output=0,
                    cost_usd=0.0,
                    success=True,
                )
            return cached

        # Cache miss - generate response
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            preferred_provider=preferred_provider,
            fallback=fallback,
            correlation_id=correlation_id,
        )

        # Store in cache
        cache.put(cache_key, response)
        logger.debug(f"LLM response cached with key {cache_key[:16]}...")

        return response

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get LLM response cache statistics.

        الحصول على إحصائيات تخزين استجابات LLM المؤقت

        Returns:
            dict with hits, misses, size, and hit rate
        """
        cache = _get_response_cache()
        return cache.stats()

    def clear_cache(self) -> int:
        """
        Clear the LLM response cache.

        مسح تخزين استجابات LLM المؤقت

        Returns:
            Number of entries cleared
        """
        cache = _get_response_cache()
        return cache.clear()

    # ─────────────────────────────────────────────────────────────────────────
    # G-22: Streaming Support
    # دعم البث المتدفق
    # ─────────────────────────────────────────────────────────────────────────

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        preferred_provider: LLMProvider | None = None,
        correlation_id: str | None = None,
    ) -> AsyncIterator[str]:
        """
        Generate text as a stream of chunks using SSE-compatible async generator.

        توليد نص كتدفق من الأجزاء باستخدام مولد غير متزامن متوافق مع SSE

        Yields text chunks as they are generated by the provider.
        Supports streaming for Ollama, Anthropic, OpenAI, Google, and DeepSeek.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Override temperature
            max_tokens: Override max tokens
            preferred_provider: Try this provider first
            correlation_id: Correlation ID for audit

        Yields:
            str: Text chunks as they arrive from the LLM provider

        Example:
            async for chunk in manager.generate_stream("Explain wheat irrigation"):
                print(chunk, end="", flush=True)

        Raises:
            AllProvidersFailedError: If no provider can serve the stream
        """
        errors: list[tuple[LLMProvider, str]] = []

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
                continue

            try:
                config = self.configs[provider]
                temp = temperature if temperature is not None else config.temperature
                max_tok = max_tokens if max_tokens is not None else config.max_tokens

                start_time = datetime.now(UTC)
                total_text = ""
                chunk_count = 0

                if provider == LLMProvider.OLLAMA:
                    stream = self._stream_ollama(prompt, system_prompt, temp, max_tok)
                elif provider == LLMProvider.ANTHROPIC:
                    stream = self._stream_anthropic(prompt, system_prompt, temp, max_tok)
                elif provider == LLMProvider.OPENAI:
                    stream = self._stream_openai(prompt, system_prompt, temp, max_tok)
                elif provider == LLMProvider.GOOGLE:
                    stream = self._stream_google(prompt, system_prompt, temp, max_tok)
                elif provider == LLMProvider.DEEPSEEK:
                    stream = self._stream_deepseek(prompt, system_prompt, temp, max_tok)
                else:
                    errors.append((provider, f"Streaming not supported for {provider.value}"))
                    continue

                async for chunk in stream:
                    total_text += chunk
                    chunk_count += 1
                    yield chunk

                # Record success after stream completes
                latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
                if breaker:
                    breaker._record_success()

                if self._metrics:
                    estimated_output_tokens = len(total_text) // 4
                    self._metrics.record_llm_call(
                        provider=provider.value,
                        model=config.model,
                        latency_ms=latency_ms,
                        tokens_input=len(prompt) // 4,
                        tokens_output=estimated_output_tokens,
                        cost_usd=calculate_cost(
                            provider.value,
                            config.model,
                            len(prompt) // 4,
                            estimated_output_tokens,
                        ),
                        success=True,
                    )

                if self._audit_logger:
                    latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
                    self._audit_logger.log_llm_response(
                        correlation_id=correlation_id or "",
                        llm_provider=provider.value,
                        model_name=config.model,
                        output_data={"text": total_text[:500], "streamed": True, "chunks": chunk_count},
                        latency_ms=latency_ms,
                        token_count_input=len(prompt) // 4,
                        token_count_output=len(total_text) // 4,
                    )

                return  # Stream completed successfully

            except Exception as e:
                errors.append((provider, str(e)))
                if breaker:
                    breaker._record_failure()
                continue

        raise AllProvidersFailedError(errors)

    async def _stream_ollama(
        self, prompt: str, system_prompt: str | None, temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        """Stream from Ollama API."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for Ollama streaming", LLMProvider.OLLAMA) from None

        config = self.configs[LLMProvider.OLLAMA]

        async with (
            httpx.AsyncClient(timeout=config.timeout) as client,
            client.stream(
                "POST",
                f"{config.base_url}/api/generate",
                json={
                    "model": config.model,
                    "prompt": prompt,
                    "system": system_prompt or "",
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            ) as response,
        ):
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        text = data.get("response", "")
                        if text:
                            yield text
                        if data.get("done", False):
                            return
                    except json.JSONDecodeError:
                        continue

    async def _stream_anthropic(
        self, prompt: str, system_prompt: str | None, temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        """Stream from Anthropic API using SSE."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for Anthropic streaming", LLMProvider.ANTHROPIC) from None

        config = self.configs[LLMProvider.ANTHROPIC]
        if not config.api_key:
            raise LLMProviderError("Anthropic API key not set", LLMProvider.ANTHROPIC)

        async with (
            httpx.AsyncClient(timeout=config.timeout) as client,
            client.stream(
                "POST",
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
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True,
                },
            ) as response,
        ):
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    return
                try:
                    data = json.loads(data_str)
                    if data.get("type") == "content_block_delta":
                        delta = data.get("delta", {})
                        text = delta.get("text", "")
                        if text:
                            yield text
                except json.JSONDecodeError:
                    continue

    async def _stream_openai(
        self, prompt: str, system_prompt: str | None, temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        """Stream from OpenAI API using SSE."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for OpenAI streaming", LLMProvider.OPENAI) from None

        config = self.configs[LLMProvider.OPENAI]
        if not config.api_key:
            raise LLMProviderError("OpenAI API key not set", LLMProvider.OPENAI)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with (
            httpx.AsyncClient(timeout=config.timeout) as client,
            client.stream(
                "POST",
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
                    "stream": True,
                },
            ) as response,
        ):
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    return
                try:
                    data = json.loads(data_str)
                    choices = data.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        text = delta.get("content", "")
                        if text:
                            yield text
                except json.JSONDecodeError:
                    continue

    async def _stream_google(
        self, prompt: str, system_prompt: str | None, temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        """Stream from Google Gemini API using SSE."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for Google streaming", LLMProvider.GOOGLE) from None

        config = self.configs[LLMProvider.GOOGLE]
        if not config.api_key:
            raise LLMProviderError("Google API key not set", LLMProvider.GOOGLE)

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        async with (
            httpx.AsyncClient(timeout=config.timeout) as client,
            client.stream(
                "POST",
                f"https://generativelanguage.googleapis.com/v1/models/{config.model}:streamGenerateContent",
                headers={"Content-Type": "application/json"},
                params={"key": config.api_key, "alt": "sse"},
                json={
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens,
                    },
                },
            ) as response,
        ):
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                try:
                    data = json.loads(data_str)
                    for candidate in data.get("candidates", []):
                        for part in candidate.get("content", {}).get("parts", []):
                            text = part.get("text", "")
                            if text:
                                yield text
                except json.JSONDecodeError:
                    continue

    async def _stream_deepseek(
        self, prompt: str, system_prompt: str | None, temperature: float, max_tokens: int
    ) -> AsyncIterator[str]:
        """Stream from DeepSeek API (OpenAI-compatible SSE)."""
        try:
            import httpx
        except ImportError:
            raise LLMProviderError("httpx required for DeepSeek streaming", LLMProvider.DEEPSEEK) from None

        config = self.configs[LLMProvider.DEEPSEEK]
        if not config.api_key:
            raise LLMProviderError("DeepSeek API key not set", LLMProvider.DEEPSEEK)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        base_url = config.base_url or "https://api.deepseek.com"

        async with (
            httpx.AsyncClient(timeout=config.timeout) as client,
            client.stream(
                "POST",
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
                    "stream": True,
                },
            ) as response,
        ):
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    return
                try:
                    data = json.loads(data_str)
                    choices = data.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        text = delta.get("content", "")
                        if text:
                            yield text
                except json.JSONDecodeError:
                    continue

    # ─────────────────────────────────────────────────────────────────────────
    # G-23: Cost Prediction and Tenant Budget Tracking
    # تقدير التكلفة وتتبع ميزانية المستأجر
    # ─────────────────────────────────────────────────────────────────────────

    def estimate_cost(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int | None = None,
        provider: LLMProvider | None = None,
    ) -> dict[str, Any]:
        """
        Estimate the cost of an LLM call before making it.

        تقدير تكلفة طلب LLM قبل إجرائه

        Estimates input tokens from prompt length and uses max_tokens for
        output estimation. Returns cost estimates for specified or all providers.

        Args:
            prompt: The prompt text to estimate cost for
            system_prompt: Optional system prompt
            max_tokens: Expected max output tokens (defaults to config)
            provider: Specific provider to estimate for (all if None)

        Returns:
            dict with per-provider cost estimates and recommendation

        Example:
            estimate = manager.estimate_cost(
                prompt="Analyze this field data...",
                max_tokens=1000
            )
            print(estimate["cheapest_provider"])  # "ollama"
            print(estimate["estimates"]["openai"]["estimated_cost_usd"])
        """
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n{prompt}"

        # Estimate input tokens (rough: ~4 chars per token for English)
        estimated_input_tokens = max(1, len(full_prompt) // 4)

        estimates: dict[str, Any] = {}
        cheapest_provider: str | None = None
        cheapest_cost = float("inf")

        providers_to_check = [provider] if provider else list(self.configs.keys())

        for prov in providers_to_check:
            if prov not in self.configs or not self.configs[prov].enabled:
                continue

            config = self.configs[prov]
            output_tokens = max_tokens or config.max_tokens
            estimated_cost = calculate_cost(
                prov.value,
                config.model,
                estimated_input_tokens,
                output_tokens,
            )

            estimates[prov.value] = {
                "model": config.model,
                "estimated_input_tokens": estimated_input_tokens,
                "estimated_output_tokens": output_tokens,
                "estimated_cost_usd": round(estimated_cost, 6),
                "is_local": prov in (LLMProvider.OLLAMA, LLMProvider.VLLM),
            }

            if estimated_cost < cheapest_cost:
                cheapest_cost = estimated_cost
                cheapest_provider = prov.value

        return {
            "estimates": estimates,
            "cheapest_provider": cheapest_provider,
            "cheapest_provider_ar": "المزود الأقل تكلفة",
            "cheapest_cost_usd": round(cheapest_cost, 6) if cheapest_cost < float("inf") else 0.0,
            "prompt_length": len(prompt),
            "estimated_input_tokens": estimated_input_tokens,
        }

    def set_tenant_budget(
        self,
        budget_usd: float,
        period: str = "monthly",
        hard_limit: bool = False,
    ) -> None:
        """
        Set a budget limit for the current tenant.

        تحديد حد الميزانية للمستأجر الحالي

        Args:
            budget_usd: Budget limit in USD
            period: Budget period ("daily", "monthly", "yearly")
            hard_limit: If True, block requests when budget exceeded

        Example:
            manager.set_tenant_budget(budget_usd=50.0, period="monthly", hard_limit=True)
        """
        budget_tracker = _get_budget_tracker()
        budget_tracker.set_budget(
            tenant_id=self.tenant_id,
            budget_usd=budget_usd,
            period=period,
            hard_limit=hard_limit,
        )
        logger.info(f"Budget set for tenant {self.tenant_id}: ${budget_usd:.2f}/{period} (hard_limit={hard_limit})")

    def get_tenant_budget_status(self) -> dict[str, Any]:
        """
        Get current budget usage status for the tenant.

        الحصول على حالة استخدام ميزانية المستأجر الحالية

        Returns:
            dict with budget, spent, remaining, and alert status
        """
        budget_tracker = _get_budget_tracker()
        return budget_tracker.get_status(self.tenant_id)

    def check_budget_before_call(
        self,
        provider: LLMProvider | None = None,
        estimated_tokens: int = 4096,
    ) -> dict[str, Any]:
        """
        Check if a call is within budget before making it.

        التحقق مما إذا كان الطلب ضمن الميزانية قبل إجرائه

        Args:
            provider: Provider to estimate cost for
            estimated_tokens: Estimated total tokens for the call

        Returns:
            dict with allowed status, remaining budget, and warnings

        Raises:
            LLMProviderError: If hard limit is set and budget is exceeded
        """
        budget_tracker = _get_budget_tracker()
        status = budget_tracker.get_status(self.tenant_id)

        if not status.get("budget_set"):
            return {"allowed": True, "budget_set": False}

        # Estimate cost for this call
        prov = provider or (self._provider_order[0] if self._provider_order else None)
        if not prov:
            return {"allowed": True, "budget_set": True, "warning": "No provider configured"}

        config = self.configs.get(prov)
        if not config:
            return {"allowed": True, "budget_set": True}

        estimated_cost = calculate_cost(
            prov.value,
            config.model,
            estimated_tokens // 2,
            estimated_tokens // 2,
        )

        remaining = status.get("remaining_usd", float("inf"))
        allowed = remaining >= estimated_cost

        result = {
            "allowed": allowed,
            "budget_set": True,
            "budget_usd": status.get("budget_usd", 0),
            "spent_usd": status.get("spent_usd", 0),
            "remaining_usd": round(remaining, 6),
            "estimated_cost_usd": round(estimated_cost, 6),
            "usage_percentage": status.get("usage_percentage", 0),
        }

        if not allowed and status.get("hard_limit"):
            raise LLMProviderError(
                f"Budget exceeded for tenant {self.tenant_id}. "
                f"Remaining: ${remaining:.4f}, Estimated cost: ${estimated_cost:.4f} "
                f"| تم تجاوز الميزانية للمستأجر {self.tenant_id}"
            )

        # Add warnings at thresholds
        usage_pct = status.get("usage_percentage", 0)
        if usage_pct >= 90:
            result["warning"] = "Budget nearly exhausted (>90%) | الميزانية شارفت على النفاد"
            result["warning_level"] = "critical"
        elif usage_pct >= 75:
            result["warning"] = "Budget usage high (>75%) | استخدام الميزانية مرتفع"
            result["warning_level"] = "warning"

        return result

    def record_spend(self, cost_usd: float) -> None:
        """
        Record a spend against the tenant budget.

        تسجيل إنفاق مقابل ميزانية المستأجر

        Args:
            cost_usd: Amount spent in USD
        """
        budget_tracker = _get_budget_tracker()
        budget_tracker.record_spend(self.tenant_id, cost_usd)

    # ─────────────────────────────────────────────────────────────────────────
    # G-06: Context Engineering Integration
    # تكامل هندسة السياق
    # ─────────────────────────────────────────────────────────────────────────

    async def generate_with_context(
        self,
        prompt: str,
        context_data: dict[str, Any] | list[dict[str, Any]] | None = None,
        context_type: str = "field",
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        preferred_provider: LLMProvider | None = None,
        fallback: bool = True,
        correlation_id: str | None = None,
        compression_strategy: str | None = None,
        max_context_tokens: int = 4000,
    ) -> LLMResponse:
        """
        Generate text with compressed context from ContextCompressor.

        توليد نص مع سياق مضغوط من ضاغط السياق

        Accepts raw context data (field data, weather data, or history),
        compresses it using ContextCompressor, and prepends the compressed
        context to the system prompt before calling the LLM.

        Args:
            prompt: User prompt
            context_data: Raw context data (field dict, weather dict, or history list)
            context_type: Type of context data ("field", "weather", "history")
            system_prompt: Base system prompt (compressed context will be appended)
            temperature: Override temperature
            max_tokens: Override max tokens
            preferred_provider: Try this provider first
            fallback: Enable fallback to other providers
            correlation_id: Correlation ID for audit
            compression_strategy: Override compression strategy
                ("extractive", "abstractive", "hybrid", "selective")
            max_context_tokens: Maximum tokens to allocate for context

        Returns:
            LLMResponse with context metadata in raw_response

        Example:
            field_data = {"name": "North Field", "area": 50, "crop": "wheat",
                          "ndvi": 0.72, "soil_moisture": 38}

            response = await manager.generate_with_context(
                prompt="What irrigation advice do you have?",
                context_data=field_data,
                context_type="field",
                system_prompt="You are an agricultural advisor.",
            )
        """
        from .context_engineering.compression import (
            CompressionStrategy,
            ContextCompressor,
        )

        compressor = ContextCompressor(
            max_tokens=max_context_tokens,
        )

        # Set compression strategy
        strategy = None
        if compression_strategy:
            strategy_map = {
                "extractive": CompressionStrategy.EXTRACTIVE,
                "abstractive": CompressionStrategy.ABSTRACTIVE,
                "hybrid": CompressionStrategy.HYBRID,
                "selective": CompressionStrategy.SELECTIVE,
            }
            strategy = strategy_map.get(compression_strategy)

        # Compress context based on type
        compressed_context = ""
        compression_metadata: dict[str, Any] = {}

        if context_data is not None:
            if context_type == "field":
                result = compressor.compress_field_data(context_data, strategy=strategy)
            elif context_type == "weather":
                result = compressor.compress_weather_data(context_data, strategy=strategy)
            elif context_type == "history":
                if not isinstance(context_data, list):
                    context_data = [context_data]
                result = compressor.compress_history(context_data, strategy=strategy)
            else:
                # Generic compression: treat as field data
                result = compressor.compress_field_data(
                    context_data if isinstance(context_data, (dict, list)) else {"data": context_data},
                    strategy=strategy,
                )

            compressed_context = result.compressed_text
            compression_metadata = {
                "context_type": context_type,
                "original_tokens": result.original_tokens,
                "compressed_tokens": result.compressed_tokens,
                "compression_ratio": round(result.compression_ratio, 3),
                "tokens_saved": result.tokens_saved,
                "savings_percentage": round(result.savings_percentage, 1),
                "strategy": result.strategy.value,
            }

            logger.info(
                f"Context compressed: {result.original_tokens} -> {result.compressed_tokens} tokens "
                f"({result.savings_percentage:.1f}% saved) | "
                f"تم ضغط السياق: {result.original_tokens} -> {result.compressed_tokens} رمز"
            )

        # Build enriched system prompt with compressed context
        enriched_system_prompt = self._build_context_system_prompt(
            base_system_prompt=system_prompt,
            compressed_context=compressed_context,
            context_type=context_type,
        )

        # Generate with the enriched prompt
        response = await self.generate(
            prompt=prompt,
            system_prompt=enriched_system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            preferred_provider=preferred_provider,
            fallback=fallback,
            correlation_id=correlation_id,
        )

        # Attach context compression metadata to response
        response.raw_response["context_compression"] = compression_metadata

        return response

    def _build_context_system_prompt(
        self,
        base_system_prompt: str | None,
        compressed_context: str,
        context_type: str,
    ) -> str:
        """
        Build a system prompt with compressed context prepended.

        بناء موجه النظام مع السياق المضغوط

        Args:
            base_system_prompt: Original system prompt
            compressed_context: Compressed context text
            context_type: Type of context for labeling

        Returns:
            Enriched system prompt string
        """
        context_labels = {
            "field": "Field Data / بيانات الحقل",
            "weather": "Weather Data / بيانات الطقس",
            "history": "Operational History / سجل العمليات",
        }
        label = context_labels.get(context_type, f"Context Data / بيانات السياق ({context_type})")

        parts = []

        if base_system_prompt:
            parts.append(base_system_prompt)

        if compressed_context:
            parts.append(f"\n\n--- {label} ---\n{compressed_context}\n--- End Context / نهاية السياق ---")

        return "\n".join(parts) if parts else "You are a helpful agricultural assistant. أنت مساعد زراعي مفيد."


# ─────────────────────────────────────────────────────────────────────────────
# G-21: LRU Response Cache
# ذاكرة التخزين المؤقت LRU للاستجابات
# ─────────────────────────────────────────────────────────────────────────────


def _build_cache_key(prompt: str, system_prompt: str | None, provider: str, temperature: str) -> str:
    """
    Build a deterministic cache key from prompt parameters.

    بناء مفتاح تخزين مؤقت حتمي من معاملات الطلب
    """
    raw = f"{prompt}|{system_prompt or ''}|{provider}|{temperature}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class _LRUResponseCache:
    """
    Thread-safe in-memory LRU cache for LLM responses with TTL support.

    ذاكرة تخزين مؤقت LRU آمنة للخيوط في الذاكرة لاستجابات LLM مع دعم TTL

    Entries are evicted when the cache exceeds max_size (least recently used first)
    or when their TTL expires.
    """

    def __init__(self, max_size: int = 256):
        """
        Initialize the LRU cache.

        Args:
            max_size: Maximum number of entries to store
        """
        self._max_size = max_size
        self._cache: OrderedDict[str, tuple[LLMResponse, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: str, ttl_seconds: float = 300.0) -> LLMResponse | None:
        """
        Get a cached response if it exists and hasn't expired.

        الحصول على استجابة مخزنة مؤقتاً إذا كانت موجودة ولم تنتهِ صلاحيتها
        """
        if key not in self._cache:
            self._misses += 1
            return None

        response, cached_at = self._cache[key]

        # Check TTL
        if (time.time() - cached_at) > ttl_seconds:
            del self._cache[key]
            self._misses += 1
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        self._hits += 1
        return response

    def put(self, key: str, response: LLMResponse) -> None:
        """
        Store a response in the cache.

        تخزين استجابة في الذاكرة المؤقتة
        """
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = (response, time.time())
        else:
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)  # Remove LRU entry
            self._cache[key] = (response, time.time())

    def clear(self) -> int:
        """Clear all cached entries. Returns number of entries cleared."""
        count = len(self._cache)
        self._cache.clear()
        return count

    def stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        الحصول على إحصائيات التخزين المؤقت
        """
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 4) if total > 0 else 0.0,
            "hit_rate_ar": "نسبة الإصابة",
            "total_requests": total,
        }


# Global cache instance
_global_cache: _LRUResponseCache | None = None


def _get_response_cache(max_size: int = 256) -> _LRUResponseCache:
    """Get or create the global response cache."""
    global _global_cache
    if _global_cache is None:
        cache_size = int(os.getenv("LLM_CACHE_MAX_SIZE", str(max_size)))
        _global_cache = _LRUResponseCache(max_size=cache_size)
    return _global_cache


# ─────────────────────────────────────────────────────────────────────────────
# G-23: Tenant Budget Tracker
# متتبع ميزانية المستأجر
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class _TenantBudget:
    """Budget configuration for a tenant."""

    budget_usd: float
    period: str  # "daily", "monthly", "yearly"
    hard_limit: bool = False
    spent_usd: float = 0.0
    period_start: float = field(default_factory=time.time)

    @property
    def remaining_usd(self) -> float:
        return max(0.0, self.budget_usd - self.spent_usd)

    @property
    def usage_percentage(self) -> float:
        if self.budget_usd <= 0:
            return 0.0
        return round((self.spent_usd / self.budget_usd) * 100, 2)

    def is_period_expired(self) -> bool:
        """Check if the current budget period has expired."""
        elapsed = time.time() - self.period_start
        period_seconds = {
            "daily": 86400,
            "monthly": 2592000,  # 30 days
            "yearly": 31536000,  # 365 days
        }
        return elapsed >= period_seconds.get(self.period, 2592000)


class _TenantBudgetTracker:
    """
    Tracks LLM spending per tenant against configured budgets.

    يتتبع إنفاق LLM لكل مستأجر مقابل الميزانيات المُهيئة

    Supports daily, monthly, and yearly budget periods with automatic
    period reset and hard/soft budget limits.
    """

    def __init__(self) -> None:
        self._budgets: dict[str, _TenantBudget] = {}

    def set_budget(
        self,
        tenant_id: str,
        budget_usd: float,
        period: str = "monthly",
        hard_limit: bool = False,
    ) -> None:
        """Set budget for a tenant. Resets spent amount."""
        self._budgets[tenant_id] = _TenantBudget(
            budget_usd=budget_usd,
            period=period,
            hard_limit=hard_limit,
            spent_usd=0.0,
            period_start=time.time(),
        )

    def record_spend(self, tenant_id: str, cost_usd: float) -> None:
        """Record a spend for a tenant."""
        if tenant_id not in self._budgets:
            return

        budget = self._budgets[tenant_id]

        # Auto-reset if period expired
        if budget.is_period_expired():
            budget.spent_usd = 0.0
            budget.period_start = time.time()

        budget.spent_usd += cost_usd

    def get_status(self, tenant_id: str) -> dict[str, Any]:
        """
        Get budget status for a tenant.

        الحصول على حالة الميزانية للمستأجر
        """
        if tenant_id not in self._budgets:
            return {
                "budget_set": False,
                "budget_set_ar": "لم يتم تحديد الميزانية",
                "tenant_id": tenant_id,
            }

        budget = self._budgets[tenant_id]

        # Auto-reset if period expired
        if budget.is_period_expired():
            budget.spent_usd = 0.0
            budget.period_start = time.time()

        # Determine alert level
        usage_pct = budget.usage_percentage
        if usage_pct >= 100:
            alert_level = "exceeded"
            alert_level_ar = "تم التجاوز"
        elif usage_pct >= 90:
            alert_level = "critical"
            alert_level_ar = "حرج"
        elif usage_pct >= 75:
            alert_level = "warning"
            alert_level_ar = "تحذير"
        elif usage_pct >= 50:
            alert_level = "notice"
            alert_level_ar = "ملاحظة"
        else:
            alert_level = "normal"
            alert_level_ar = "عادي"

        return {
            "budget_set": True,
            "tenant_id": tenant_id,
            "budget_usd": round(budget.budget_usd, 4),
            "spent_usd": round(budget.spent_usd, 6),
            "remaining_usd": round(budget.remaining_usd, 6),
            "usage_percentage": usage_pct,
            "period": budget.period,
            "hard_limit": budget.hard_limit,
            "alert_level": alert_level,
            "alert_level_ar": alert_level_ar,
            "period_start": datetime.fromtimestamp(budget.period_start, tz=UTC).isoformat(),
        }


# Global budget tracker instance
_global_budget_tracker: _TenantBudgetTracker | None = None


def _get_budget_tracker() -> _TenantBudgetTracker:
    """Get or create the global budget tracker."""
    global _global_budget_tracker
    if _global_budget_tracker is None:
        _global_budget_tracker = _TenantBudgetTracker()
    return _global_budget_tracker


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
