"""
OpenAI-Compatible Provider Module
=================================
وحدة مزود متوافق مع OpenAI

Provider for OpenAI-compatible endpoints.
Works with Ollama's OpenAI API, vLLM, LM Studio, LocalAI, etc.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, AsyncIterator

from .config import OpenAICompatConfig, get_config
from .provider import (
    GenerationOptions,
    GenerationResponse,
    GenerationStatus,
    LLMProvider,
    LLMProviderError,
    Message,
    ModelNotFoundError,
    ProviderType,
    ProviderUnavailableError,
    StreamChunk,
)

# Optional httpx import
try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class OpenAICompatError(LLMProviderError):
    """OpenAI-compatible provider error."""

    def __init__(self, message: str, status: GenerationStatus = GenerationStatus.ERROR):
        super().__init__(message, provider=ProviderType.OPENAI_COMPAT, status=status)


class OpenAICompatProvider(LLMProvider):
    """
    OpenAI-compatible API provider.

    مزود واجهة برمجة تطبيقات متوافقة مع OpenAI

    Works with any server implementing the OpenAI chat/completions API:
        - Ollama (http://localhost:11434/v1)
        - vLLM (http://localhost:8000/v1)
        - LM Studio (http://localhost:1234/v1)
        - LocalAI (http://localhost:8080/v1)
        - Text Generation Inference
        - Any OpenAI-compatible server

    Example:
        # Use with Ollama's OpenAI endpoint
        provider = OpenAICompatProvider(OpenAICompatConfig(
            base_url="http://localhost:11434/v1",
            api_key="ollama",  # Ollama doesn't require a real key
            default_model="llama3.2"
        ))

        response = await provider.generate("Hello, how are you?")

        # Use with vLLM
        provider = OpenAICompatProvider(OpenAICompatConfig(
            base_url="http://localhost:8000/v1",
            default_model="meta-llama/Llama-3.2-3B-Instruct"
        ))
    """

    def __init__(self, config: OpenAICompatConfig | None = None):
        """
        Initialize OpenAI-compatible provider.

        Args:
            config: Configuration (uses global config if None)
        """
        if not HTTPX_AVAILABLE:
            raise ImportError(
                "httpx is required for OpenAICompatProvider. Install with: pip install httpx"
            )

        self._config = config or get_config().openai_compat
        self._client: httpx.AsyncClient | None = None

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.OPENAI_COMPAT

    @property
    def default_model(self) -> str:
        """Get default model."""
        return self._config.default_model

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._config.base_url

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
        }
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"
        if self._config.organization:
            headers["OpenAI-Organization"] = self._config.organization
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._config.base_url,
                headers=self._get_headers(),
                timeout=httpx.Timeout(self._config.timeout),
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def is_available(self) -> bool:
        """
        Check if the server is available.

        التحقق من توفر الخادم
        """
        try:
            client = await self._get_client()
            response = await client.get("/models", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """
        List available models.

        قائمة النماذج المتاحة
        """
        try:
            client = await self._get_client()
            response = await client.get("/models")
            response.raise_for_status()
            data = response.json()
            return [model.get("id", "") for model in data.get("data", [])]
        except httpx.HTTPError as e:
            raise OpenAICompatError(f"Failed to list models: {e}") from e

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        options: GenerationOptions | None = None,
    ) -> GenerationResponse:
        """
        Generate text using chat completion.

        توليد نص باستخدام إكمال الدردشة

        Args:
            prompt: User prompt
            model: Model to use
            system_prompt: Optional system prompt
            options: Generation options

        Returns:
            GenerationResponse with generated text
        """
        # Build messages from prompt
        messages = []
        if system_prompt:
            messages.append(Message.system(system_prompt))
        messages.append(Message.user(prompt))

        return await self.chat(messages, model=model, options=options)

    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        options: GenerationOptions | None = None,
    ) -> GenerationResponse:
        """
        Chat completion.

        إكمال الدردشة

        Args:
            messages: List of chat messages
            model: Model to use
            options: Generation options

        Returns:
            GenerationResponse with assistant reply
        """
        model = model or self._config.default_model
        options = options or GenerationOptions()
        client = await self._get_client()

        # Build request payload
        payload: dict[str, Any] = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": options.temperature,
            "max_tokens": options.max_tokens,
            "top_p": options.top_p,
            "stream": False,
        }

        if options.stop:
            payload["stop"] = options.stop
        if options.presence_penalty != 0.0:
            payload["presence_penalty"] = options.presence_penalty
        if options.frequency_penalty != 0.0:
            payload["frequency_penalty"] = options.frequency_penalty
        if options.seed is not None:
            payload["seed"] = options.seed
        if options.json_mode:
            payload["response_format"] = {"type": "json_object"}

        start_time = datetime.now(UTC)

        try:
            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

            # Extract response
            choice = data.get("choices", [{}])[0]
            text = choice.get("message", {}).get("content", "")
            finish_reason = choice.get("finish_reason")

            # Extract usage
            usage = data.get("usage", {})
            tokens_input = usage.get("prompt_tokens", 0)
            tokens_output = usage.get("completion_tokens", 0)

            return GenerationResponse(
                text=text,
                model=model,
                provider=ProviderType.OPENAI_COMPAT,
                status=GenerationStatus.SUCCESS,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                latency_ms=latency_ms,
                cost_usd=0.0,  # Local models are free
                finish_reason=finish_reason,
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ModelNotFoundError(model, ProviderType.OPENAI_COMPAT) from e
            if e.response.status_code == 429:
                raise OpenAICompatError("Rate limited", status=GenerationStatus.RATE_LIMITED) from e
            raise OpenAICompatError(f"Chat failed: {e}") from e
        except Exception as e:
            raise OpenAICompatError(f"Chat failed: {e}") from e

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
            prompt: User prompt
            model: Model to use
            system_prompt: Optional system prompt
            options: Generation options

        Yields:
            StreamChunk objects with text fragments
        """
        messages = []
        if system_prompt:
            messages.append(Message.system(system_prompt))
        messages.append(Message.user(prompt))

        async for chunk in self.chat_stream(messages, model=model, options=options):
            yield chunk

    async def chat_stream(
        self,
        messages: list[Message],
        model: str | None = None,
        options: GenerationOptions | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """
        Chat completion with streaming.

        إكمال الدردشة مع التدفق

        Args:
            messages: List of chat messages
            model: Model to use
            options: Generation options

        Yields:
            StreamChunk objects with text fragments
        """
        model = model or self._config.default_model
        options = options or GenerationOptions()
        client = await self._get_client()

        payload: dict[str, Any] = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": options.temperature,
            "max_tokens": options.max_tokens,
            "top_p": options.top_p,
            "stream": True,
        }

        if options.stop:
            payload["stop"] = options.stop

        try:
            async with client.stream(
                "POST",
                "/chat/completions",
                json=payload,
                timeout=httpx.Timeout(300.0),
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    data_str = line[6:]  # Remove "data: " prefix
                    if data_str == "[DONE]":
                        yield StreamChunk(text="", is_final=True, finish_reason="stop")
                        break

                    try:
                        data = json.loads(data_str)
                        choice = data.get("choices", [{}])[0]
                        delta = choice.get("delta", {})
                        content = delta.get("content", "")
                        finish_reason = choice.get("finish_reason")

                        if content or finish_reason:
                            yield StreamChunk(
                                text=content,
                                is_final=finish_reason is not None,
                                tokens=1 if content else 0,
                                finish_reason=finish_reason,
                            )

                    except json.JSONDecodeError:
                        continue

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ModelNotFoundError(model, ProviderType.OPENAI_COMPAT) from e
            raise OpenAICompatError(f"Streaming failed: {e}") from e
        except Exception as e:
            raise OpenAICompatError(f"Streaming failed: {e}") from e

    async def embeddings(
        self,
        text: str | list[str],
        model: str = "nomic-embed-text",
    ) -> list[list[float]]:
        """
        Generate embeddings for text.

        توليد التضمينات للنص

        Args:
            text: Text or list of texts to embed
            model: Embedding model to use

        Returns:
            List of embedding vectors
        """
        client = await self._get_client()

        input_texts = [text] if isinstance(text, str) else text

        try:
            response = await client.post(
                "/embeddings",
                json={
                    "model": model,
                    "input": input_texts,
                },
            )
            response.raise_for_status()
            data = response.json()

            # Extract embeddings
            embeddings = []
            for item in data.get("data", []):
                embeddings.append(item.get("embedding", []))
            return embeddings

        except Exception as e:
            raise OpenAICompatError(f"Embeddings failed: {e}") from e


# Convenience functions
async def get_openai_compat_provider(
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> OpenAICompatProvider:
    """
    Get an OpenAI-compatible provider instance.

    الحصول على مثيل مزود متوافق مع OpenAI

    Args:
        base_url: Server base URL (defaults to Ollama)
        api_key: API key (optional for local servers)
        model: Default model

    Returns:
        Configured OpenAICompatProvider
    """
    config = OpenAICompatConfig()
    if base_url:
        config.base_url = base_url
    if api_key:
        config.api_key = api_key
    if model:
        config.default_model = model

    provider = OpenAICompatProvider(config)
    if not await provider.is_available():
        raise ProviderUnavailableError(
            f"OpenAI-compatible server is not available at {config.base_url}"
        )
    return provider


async def get_vllm_provider(
    base_url: str = "http://localhost:8000/v1",
    model: str = "deepseek-ai/deepseek-coder-6.7b-instruct",
) -> OpenAICompatProvider:
    """
    Get a vLLM provider instance.

    الحصول على مثيل مزود vLLM
    """
    return await get_openai_compat_provider(
        base_url=base_url,
        model=model,
    )


async def get_deepseek_vllm_provider(
    base_url: str = "http://sahool-vllm:8000/v1",
    model: str = "deepseek-ai/deepseek-coder-6.7b-instruct",
) -> OpenAICompatProvider:
    """
    Get a DeepSeek Coder vLLM provider instance (Docker service).

    الحصول على مثيل مزود ديب سيك كودر عبر vLLM (خدمة Docker)
    """
    return await get_openai_compat_provider(
        base_url=base_url,
        model=model,
    )


async def get_lm_studio_provider(
    base_url: str = "http://localhost:1234/v1",
    model: str = "local-model",
) -> OpenAICompatProvider:
    """
    Get an LM Studio provider instance.

    الحصول على مثيل مزود LM Studio
    """
    return await get_openai_compat_provider(
        base_url=base_url,
        model=model,
    )
