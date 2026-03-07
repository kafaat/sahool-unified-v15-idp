"""
Ollama Provider Module
======================
وحدة مزود Ollama

Local LLM provider using Ollama server.
Supports llama3.2, codellama, mistral, qwen2.5 and other models.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from typing import Any, AsyncIterator

from .config import OllamaConfig, get_config
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


class OllamaError(LLMProviderError):
    """Ollama-specific error."""

    def __init__(self, message: str, status: GenerationStatus = GenerationStatus.ERROR):
        super().__init__(message, provider=ProviderType.OLLAMA, status=status)


class OllamaProvider(LLMProvider):
    """
    Ollama local LLM provider.

    مزود Ollama المحلي لنماذج اللغة الكبيرة

    Connects to a local Ollama server for cost-free LLM inference.
    Supports text generation, chat completion, and streaming.

    Supported models:
        - llama3.2, llama3.2:1b, llama3.2:3b
        - codellama, codellama:7b, codellama:13b
        - mistral, mistral:7b
        - qwen2.5, qwen2.5:7b, qwen2.5-coder

    Example:
        provider = OllamaProvider()

        # Check availability
        if await provider.is_available():
            # Generate text
            response = await provider.generate(
                prompt="Explain photosynthesis in Arabic",
                model="llama3.2"
            )
            print(response.text)

            # Stream response
            async for chunk in provider.generate_stream("Hello!"):
                print(chunk.text, end="", flush=True)
    """

    def __init__(self, config: OllamaConfig | None = None):
        """
        Initialize Ollama provider.

        Args:
            config: Ollama configuration (uses global config if None)
        """
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx is required for OllamaProvider. Install with: pip install httpx")

        self._config = config or get_config().ollama
        self._client: httpx.AsyncClient | None = None

    @property
    def provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.OLLAMA

    @property
    def default_model(self) -> str:
        """Get default model."""
        return self._config.default_model

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._config.base_url

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._config.base_url,
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
        Check if Ollama server is available.

        التحقق من توفر خادم Ollama
        """
        try:
            client = await self._get_client()
            response = await client.get("/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """
        List available models on Ollama server.

        قائمة النماذج المتاحة على خادم Ollama
        """
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model.get("name", "") for model in data.get("models", [])]
        except httpx.HTTPError as e:
            raise OllamaError(f"Failed to list models: {e}") from e

    async def pull_model(self, model: str) -> bool:
        """
        Pull a model from Ollama registry.

        سحب نموذج من سجل Ollama

        Args:
            model: Model name to pull

        Returns:
            True if pull was successful
        """
        try:
            client = await self._get_client()
            response = await client.post(
                "/api/pull",
                json={"name": model},
                timeout=httpx.Timeout(600.0),  # Models can be large
            )
            return response.status_code == 200
        except Exception as e:
            raise OllamaError(f"Failed to pull model '{model}': {e}") from e

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        options: GenerationOptions | None = None,
    ) -> GenerationResponse:
        """
        Generate text using Ollama.

        توليد نص باستخدام Ollama

        Args:
            prompt: User prompt
            model: Model to use (defaults to config default)
            system_prompt: Optional system prompt
            options: Generation options

        Returns:
            GenerationResponse with generated text
        """
        model = model or self._config.default_model
        options = options or GenerationOptions()
        client = await self._get_client()

        # Build request payload
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": options.temperature,
                "num_predict": options.max_tokens,
                "top_p": options.top_p,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt
        if options.top_k is not None:
            payload["options"]["top_k"] = options.top_k
        if options.stop:
            payload["options"]["stop"] = options.stop
        if options.seed is not None:
            payload["options"]["seed"] = options.seed

        start_time = datetime.now(UTC)

        # Retry logic
        last_error: Exception | None = None
        for attempt in range(self._config.max_retries):
            try:
                response = await client.post("/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()

                latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

                # Calculate tokens per second
                tokens_per_second = None
                eval_count = data.get("eval_count", 0)
                eval_duration = data.get("eval_duration", 0)
                if eval_count and eval_duration:
                    tokens_per_second = eval_count / (eval_duration / 1e9)

                return GenerationResponse(
                    text=data.get("response", ""),
                    model=model,
                    provider=ProviderType.OLLAMA,
                    status=GenerationStatus.SUCCESS,
                    tokens_input=data.get("prompt_eval_count", 0),
                    tokens_output=eval_count,
                    latency_ms=latency_ms,
                    tokens_per_second=tokens_per_second,
                    cost_usd=0.0,  # Local, free
                    finish_reason="stop" if data.get("done") else None,
                    raw_response=data,
                )

            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self._config.max_retries - 1:
                    await asyncio.sleep(self._config.retry_delay * (attempt + 1))
                    continue
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise ModelNotFoundError(model, ProviderType.OLLAMA) from e
                raise OllamaError(f"HTTP error: {e}") from e
            except Exception as e:
                raise OllamaError(f"Generation failed: {e}") from e

        raise OllamaError(
            f"Timeout after {self._config.max_retries} attempts: {last_error}",
            status=GenerationStatus.TIMEOUT,
        )

    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        options: GenerationOptions | None = None,
    ) -> GenerationResponse:
        """
        Chat completion using Ollama.

        إكمال الدردشة باستخدام Ollama

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

        # Convert messages to Ollama format
        ollama_messages = [msg.to_dict() for msg in messages]

        payload: dict[str, Any] = {
            "model": model,
            "messages": ollama_messages,
            "stream": False,
            "options": {
                "temperature": options.temperature,
                "num_predict": options.max_tokens,
                "top_p": options.top_p,
            },
        }

        if options.top_k is not None:
            payload["options"]["top_k"] = options.top_k
        if options.stop:
            payload["options"]["stop"] = options.stop

        start_time = datetime.now(UTC)

        try:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

            # Extract assistant message
            text = data.get("message", {}).get("content", "")

            return GenerationResponse(
                text=text,
                model=model,
                provider=ProviderType.OLLAMA,
                status=GenerationStatus.SUCCESS,
                tokens_input=data.get("prompt_eval_count", 0),
                tokens_output=data.get("eval_count", 0),
                latency_ms=latency_ms,
                cost_usd=0.0,
                finish_reason="stop" if data.get("done") else None,
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ModelNotFoundError(model, ProviderType.OLLAMA) from e
            raise OllamaError(f"Chat failed: {e}") from e
        except Exception as e:
            raise OllamaError(f"Chat failed: {e}") from e

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
        model = model or self._config.default_model
        options = options or GenerationOptions()
        client = await self._get_client()

        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": options.temperature,
                "num_predict": options.max_tokens,
                "top_p": options.top_p,
            },
        }

        if system_prompt:
            payload["system"] = system_prompt
        if options.top_k is not None:
            payload["options"]["top_k"] = options.top_k
        if options.stop:
            payload["options"]["stop"] = options.stop

        try:
            async with client.stream(
                "POST",
                "/api/generate",
                json=payload,
                timeout=httpx.Timeout(self._config.stream_timeout),
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        text = data.get("response", "")
                        is_done = data.get("done", False)

                        yield StreamChunk(
                            text=text,
                            is_final=is_done,
                            tokens=1 if text else 0,  # Approximate
                            finish_reason="stop" if is_done else None,
                        )

                        if is_done:
                            break

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ModelNotFoundError(model, ProviderType.OLLAMA) from e
            raise OllamaError(f"Streaming failed: {e}") from e
        except Exception as e:
            raise OllamaError(f"Streaming failed: {e}") from e

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

        ollama_messages = [msg.to_dict() for msg in messages]

        payload: dict[str, Any] = {
            "model": model,
            "messages": ollama_messages,
            "stream": True,
            "options": {
                "temperature": options.temperature,
                "num_predict": options.max_tokens,
                "top_p": options.top_p,
            },
        }

        try:
            async with client.stream(
                "POST",
                "/api/chat",
                json=payload,
                timeout=httpx.Timeout(self._config.stream_timeout),
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        text = data.get("message", {}).get("content", "")
                        is_done = data.get("done", False)

                        yield StreamChunk(
                            text=text,
                            is_final=is_done,
                            tokens=1 if text else 0,
                            finish_reason="stop" if is_done else None,
                        )

                        if is_done:
                            break

        except Exception as e:
            raise OllamaError(f"Chat streaming failed: {e}") from e

    async def embeddings(
        self,
        text: str,
        model: str = "nomic-embed-text",
    ) -> list[float]:
        """
        Generate embeddings for text.

        توليد التضمينات للنص

        Args:
            text: Text to embed
            model: Embedding model to use

        Returns:
            List of embedding values
        """
        client = await self._get_client()

        try:
            response = await client.post(
                "/api/embeddings",
                json={"model": model, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])

        except Exception as e:
            raise OllamaError(f"Embeddings failed: {e}") from e


# Convenience function
async def get_ollama_provider() -> OllamaProvider:
    """
    Get an Ollama provider instance.

    الحصول على مثيل مزود Ollama
    """
    provider = OllamaProvider()
    if not await provider.is_available():
        raise ProviderUnavailableError(
            f"Ollama server is not available. Please ensure Ollama is running at {provider.base_url}"
        )
    return provider
