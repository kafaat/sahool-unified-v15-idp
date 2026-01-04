"""
SAHOOL AI Advisor - Multi-Provider LLM Service
خدمة نماذج اللغة متعددة المزودين

Supported Providers:
1. Anthropic Claude (Primary - Recommended)
2. OpenAI GPT (Fallback)
3. Google Gemini (Optional)
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ..monitoring.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)

# Retry configuration for LLM API calls
RETRY_CONFIG = {
    "stop": stop_after_attempt(3),
    "wait": wait_exponential(multiplier=1, min=2, max=30),
    "retry": retry_if_exception_type((Exception,)),
    "before_sleep": before_sleep_log(logger, logging.WARNING),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Circuit Breaker Pattern
# ═══════════════════════════════════════════════════════════════════════════════


class CircuitBreaker:
    """
    Circuit Breaker pattern to prevent cascading failures
    نمط قاطع الدائرة لمنع الفشل المتتالي

    States:
    - CLOSED: Normal operation (requests pass through)
    - OPEN: Circuit is open (requests fail immediately)
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: datetime | None = None
        self.state = "CLOSED"

    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception(
                    f"Circuit breaker is OPEN. Service unavailable. "
                    f"Will retry after {self.recovery_timeout}s"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    async def call_async(self, func, *args, **kwargs):
        """Execute async function through circuit breaker"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception(
                    f"Circuit breaker is OPEN. Service unavailable. "
                    f"Will retry after {self.recovery_timeout}s"
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.recovery_timeout

    def _on_success(self):
        """Reset circuit breaker on success"""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Record failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures. "
                f"Will recover in {self.recovery_timeout}s"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Data Models
# ═══════════════════════════════════════════════════════════════════════════════


class LLMProviderType(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"


@dataclass
class LLMMessage:
    """Chat message"""

    role: str  # system, user, assistant
    content: str


@dataclass
class LLMResponse:
    """LLM response with metadata"""

    content: str
    provider: str
    model: str
    tokens_used: int = 0
    latency_ms: float = 0
    finish_reason: str = "stop"
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0


@dataclass
class LLMResult:
    """Result wrapper with fallback info"""

    data: LLMResponse | None
    provider: str
    failed_providers: list[str] = field(default_factory=list)
    error: str | None = None
    error_ar: str | None = None

    @property
    def success(self) -> bool:
        return self.data is not None and self.error is None


# ═══════════════════════════════════════════════════════════════════════════════
# Base Provider Interface
# ═══════════════════════════════════════════════════════════════════════════════


class LLMProvider(ABC):
    """Base class for LLM providers"""

    def __init__(self, name: str, name_ar: str):
        self.name = name
        self.name_ar = name_ar

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        pass

    @abstractmethod
    async def chat(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# Anthropic Claude Provider
# ═══════════════════════════════════════════════════════════════════════════════


class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude API
    https://www.anthropic.com/
    """

    def __init__(self):
        super().__init__("Anthropic Claude", "أنثروبيك كلود")
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self._client = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5, recovery_timeout=60
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @property
    def default_model(self) -> str:
        return os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    def _get_client(self):
        if self._client is None and self.is_configured:
            try:
                from anthropic import AsyncAnthropic

                self._client = AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                logger.error("anthropic package not installed")
                return None
        return self._client

    @retry(**RETRY_CONFIG)
    async def chat(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        return await self.circuit_breaker.call_async(
            self._chat_impl, messages, model, max_tokens, temperature
        )

    async def _chat_impl(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Internal chat implementation with retry and circuit breaker"""
        client = self._get_client()
        if not client:
            raise ValueError("Anthropic client not configured")

        import time

        start = time.time()

        # Separate system message
        system_msg = ""
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content
            else:
                chat_messages.append({"role": msg.role, "content": msg.content})

        response = await client.messages.create(
            model=model or self.default_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_msg,
            messages=chat_messages,
        )

        latency = (time.time() - start) * 1000

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Calculate cost
        cost = cost_tracker.calculate_cost(response.model, input_tokens, output_tokens)

        # Record usage (async, don't await to avoid blocking)
        asyncio.create_task(
            cost_tracker.record_usage(
                model=response.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        )

        return LLMResponse(
            content=response.content[0].text,
            provider=self.name,
            model=response.model,
            tokens_used=input_tokens + output_tokens,
            latency_ms=latency,
            finish_reason=response.stop_reason or "stop",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
        )

    async def complete(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        messages = [LLMMessage(role="user", content=prompt)]
        return await self.chat(messages, model, max_tokens, temperature)


# ═══════════════════════════════════════════════════════════════════════════════
# OpenAI Provider
# ═══════════════════════════════════════════════════════════════════════════════


class OpenAIProvider(LLMProvider):
    """
    OpenAI GPT API
    https://platform.openai.com/
    """

    def __init__(self):
        super().__init__("OpenAI GPT", "أوبن إيه آي")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self._client = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5, recovery_timeout=60
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @property
    def default_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "gpt-4o")

    def _get_client(self):
        if self._client is None and self.is_configured:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("openai package not installed")
                return None
        return self._client

    @retry(**RETRY_CONFIG)
    async def chat(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        return await self.circuit_breaker.call_async(
            self._chat_impl, messages, model, max_tokens, temperature
        )

    async def _chat_impl(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Internal chat implementation with retry and circuit breaker"""
        client = self._get_client()
        if not client:
            raise ValueError("OpenAI client not configured")

        import time

        start = time.time()

        chat_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        response = await client.chat.completions.create(
            model=model or self.default_model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=chat_messages,
        )

        latency = (time.time() - start) * 1000

        input_tokens = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0

        # Calculate cost
        cost = cost_tracker.calculate_cost(response.model, input_tokens, output_tokens)

        # Record usage (async, don't await to avoid blocking)
        asyncio.create_task(
            cost_tracker.record_usage(
                model=response.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            provider=self.name,
            model=response.model,
            tokens_used=input_tokens + output_tokens,
            latency_ms=latency,
            finish_reason=response.choices[0].finish_reason or "stop",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
        )

    async def complete(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        messages = [LLMMessage(role="user", content=prompt)]
        return await self.chat(messages, model, max_tokens, temperature)


# ═══════════════════════════════════════════════════════════════════════════════
# Google Gemini Provider
# ═══════════════════════════════════════════════════════════════════════════════


class GoogleGeminiProvider(LLMProvider):
    """
    Google Gemini API
    https://ai.google.dev/
    """

    def __init__(self):
        super().__init__("Google Gemini", "جوجل جيميني")
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        self._client = None
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5, recovery_timeout=60
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @property
    def default_model(self) -> str:
        return os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

    def _get_client(self):
        if self._client is None and self.is_configured:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._client = genai
            except ImportError:
                logger.error("google-generativeai package not installed")
                return None
        return self._client

    @retry(**RETRY_CONFIG)
    async def chat(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        return await self.circuit_breaker.call_async(
            self._chat_impl, messages, model, max_tokens, temperature
        )

    async def _chat_impl(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Internal chat implementation with retry and circuit breaker"""
        client = self._get_client()
        if not client:
            raise ValueError("Gemini client not configured")

        import time

        start = time.time()

        # Convert messages to Gemini format
        gemini_model = client.GenerativeModel(
            model_name=model or self.default_model,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            },
        )

        # Build chat history
        chat = gemini_model.start_chat(history=[])

        system_instruction = ""
        response = None
        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            elif msg.role == "user":
                prompt = (
                    f"{system_instruction}\n\n{msg.content}"
                    if system_instruction
                    else msg.content
                )
                response = await chat.send_message_async(prompt)
                system_instruction = ""

        latency = (time.time() - start) * 1000

        if response is None:
            raise ValueError("No user messages found in the conversation")

        # Estimate token counts (Gemini doesn't provide them easily)
        # Rough estimate: 1 token ≈ 4 characters
        input_text = " ".join([msg.content for msg in messages])
        input_tokens = len(input_text) // 4
        output_tokens = len(response.text) // 4

        # Calculate cost
        model_name = model or self.default_model
        cost = cost_tracker.calculate_cost(model_name, input_tokens, output_tokens)

        # Record usage (async, don't await to avoid blocking)
        asyncio.create_task(
            cost_tracker.record_usage(
                model=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
        )

        return LLMResponse(
            content=response.text,
            provider=self.name,
            model=model_name,
            tokens_used=input_tokens + output_tokens,
            latency_ms=latency,
            finish_reason="stop",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
        )

    async def complete(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        messages = [LLMMessage(role="user", content=prompt)]
        return await self.chat(messages, model, max_tokens, temperature)


# ═══════════════════════════════════════════════════════════════════════════════
# Multi-Provider LLM Service
# ═══════════════════════════════════════════════════════════════════════════════


class MultiLLMService:
    """
    Multi-provider LLM service with automatic fallback
    خدمة نماذج اللغة متعددة المزودين مع التبديل التلقائي

    Priority:
    1. Anthropic Claude (if ANTHROPIC_API_KEY set)
    2. OpenAI GPT (if OPENAI_API_KEY set)
    3. Google Gemini (if GOOGLE_API_KEY or GEMINI_API_KEY set)
    """

    def __init__(self, primary_provider: str | None = None):
        """
        Initialize multi-provider service

        Args:
            primary_provider: Override primary provider (anthropic, openai, google)
        """
        self.providers: list[LLMProvider] = []

        # Determine provider order
        if primary_provider == "openai":
            self._add_openai_first()
        elif primary_provider == "google":
            self._add_google_first()
        else:
            self._add_anthropic_first()

        configured = [p.name for p in self.providers if p.is_configured]
        logger.info(
            f"Multi-LLM Service initialized with providers: {', '.join(configured)}"
        )

    def _add_anthropic_first(self):
        anthropic = AnthropicProvider()
        if anthropic.is_configured:
            self.providers.append(anthropic)

        openai = OpenAIProvider()
        if openai.is_configured:
            self.providers.append(openai)

        google = GoogleGeminiProvider()
        if google.is_configured:
            self.providers.append(google)

    def _add_openai_first(self):
        openai = OpenAIProvider()
        if openai.is_configured:
            self.providers.append(openai)

        anthropic = AnthropicProvider()
        if anthropic.is_configured:
            self.providers.append(anthropic)

        google = GoogleGeminiProvider()
        if google.is_configured:
            self.providers.append(google)

    def _add_google_first(self):
        google = GoogleGeminiProvider()
        if google.is_configured:
            self.providers.append(google)

        anthropic = AnthropicProvider()
        if anthropic.is_configured:
            self.providers.append(anthropic)

        openai = OpenAIProvider()
        if openai.is_configured:
            self.providers.append(openai)

    async def chat(
        self,
        messages: list[LLMMessage],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        specific_provider: str | None = None,
    ) -> LLMResult:
        """
        Send chat messages with automatic fallback

        Args:
            messages: List of chat messages
            model: Optional model override
            max_tokens: Max response tokens
            temperature: Sampling temperature
            specific_provider: Force specific provider (anthropic, openai, google)

        Returns:
            LLMResult with response or error
        """
        failed_providers = []

        # Filter providers if specific one requested
        providers_to_try = self.providers
        if specific_provider:
            providers_to_try = [
                p for p in self.providers if specific_provider.lower() in p.name.lower()
            ]

        for provider in providers_to_try:
            if not provider.is_configured:
                continue

            try:
                response = await provider.chat(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                return LLMResult(
                    data=response,
                    provider=provider.name,
                    failed_providers=failed_providers,
                )
            except Exception as e:
                failed_providers.append(f"{provider.name}: {str(e)}")
                logger.warning(f"Provider {provider.name} failed: {e}")

        return LLMResult(
            data=None,
            provider="none",
            failed_providers=failed_providers,
            error="All LLM providers failed",
            error_ar="فشل جميع مزودي نماذج اللغة",
        )

    async def complete(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        specific_provider: str | None = None,
    ) -> LLMResult:
        """Simple completion with fallback"""
        messages = [LLMMessage(role="user", content=prompt)]
        return await self.chat(
            messages, model, max_tokens, temperature, specific_provider
        )

    def get_available_providers(self) -> list[dict[str, Any]]:
        """Get list of available providers"""
        all_providers = [
            AnthropicProvider(),
            OpenAIProvider(),
            GoogleGeminiProvider(),
        ]
        return [
            {
                "name": p.name,
                "name_ar": p.name_ar,
                "configured": p.is_configured,
                "default_model": p.default_model if p.is_configured else None,
                "type": p.__class__.__name__,
            }
            for p in all_providers
        ]

    def get_primary_provider(self) -> str | None:
        """Get the primary (first configured) provider name"""
        for p in self.providers:
            if p.is_configured:
                return p.name
        return None
