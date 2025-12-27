"""
SAHOOL AI Advisor - Multi-Provider LLM Service
خدمة نماذج اللغة متعددة المزودين

Supported Providers:
1. Anthropic Claude (Primary - Recommended)
2. OpenAI GPT (Fallback)
3. Google Gemini (Optional)
"""

import os
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from enum import Enum

logger = logging.getLogger(__name__)


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


@dataclass
class LLMResult:
    """Result wrapper with fallback info"""
    data: Optional[LLMResponse]
    provider: str
    failed_providers: List[str] = field(default_factory=list)
    error: Optional[str] = None
    error_ar: Optional[str] = None

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
        messages: List[LLMMessage],
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
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

    async def chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
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
                chat_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        response = await client.messages.create(
            model=model or self.default_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_msg,
            messages=chat_messages
        )

        latency = (time.time() - start) * 1000

        return LLMResponse(
            content=response.content[0].text,
            provider=self.name,
            model=response.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            latency_ms=latency,
            finish_reason=response.stop_reason or "stop"
        )

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
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

    async def chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        client = self._get_client()
        if not client:
            raise ValueError("OpenAI client not configured")

        import time
        start = time.time()

        chat_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await client.chat.completions.create(
            model=model or self.default_model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=chat_messages
        )

        latency = (time.time() - start) * 1000

        return LLMResponse(
            content=response.choices[0].message.content,
            provider=self.name,
            model=response.model,
            tokens_used=response.usage.total_tokens if response.usage else 0,
            latency_ms=latency,
            finish_reason=response.choices[0].finish_reason or "stop"
        )

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
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

    async def chat(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
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
            }
        )

        # Build chat history
        chat = gemini_model.start_chat(history=[])

        system_instruction = ""
        response = None
        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            elif msg.role == "user":
                prompt = f"{system_instruction}\n\n{msg.content}" if system_instruction else msg.content
                response = await chat.send_message_async(prompt)
                system_instruction = ""

        latency = (time.time() - start) * 1000

        if response is None:
            raise ValueError("No user messages found in the conversation")

        return LLMResponse(
            content=response.text,
            provider=self.name,
            model=model or self.default_model,
            tokens_used=0,  # Gemini doesn't provide token count easily
            latency_ms=latency,
            finish_reason="stop"
        )

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
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

    def __init__(self, primary_provider: Optional[str] = None):
        """
        Initialize multi-provider service

        Args:
            primary_provider: Override primary provider (anthropic, openai, google)
        """
        self.providers: List[LLMProvider] = []

        # Determine provider order
        if primary_provider == "openai":
            self._add_openai_first()
        elif primary_provider == "google":
            self._add_google_first()
        else:
            self._add_anthropic_first()

        configured = [p.name for p in self.providers if p.is_configured]
        logger.info(f"Multi-LLM Service initialized with providers: {', '.join(configured)}")

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
        messages: List[LLMMessage],
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        specific_provider: Optional[str] = None,
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
                p for p in self.providers
                if specific_provider.lower() in p.name.lower()
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
                    failed_providers=failed_providers
                )
            except Exception as e:
                failed_providers.append(f"{provider.name}: {str(e)}")
                logger.warning(f"Provider {provider.name} failed: {e}")

        return LLMResult(
            data=None,
            provider="none",
            failed_providers=failed_providers,
            error="All LLM providers failed",
            error_ar="فشل جميع مزودي نماذج اللغة"
        )

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        specific_provider: Optional[str] = None,
    ) -> LLMResult:
        """Simple completion with fallback"""
        messages = [LLMMessage(role="user", content=prompt)]
        return await self.chat(messages, model, max_tokens, temperature, specific_provider)

    def get_available_providers(self) -> List[Dict[str, Any]]:
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
                "type": p.__class__.__name__
            }
            for p in all_providers
        ]

    def get_primary_provider(self) -> Optional[str]:
        """Get the primary (first configured) provider name"""
        for p in self.providers:
            if p.is_configured:
                return p.name
        return None
