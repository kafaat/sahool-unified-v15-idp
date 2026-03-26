"""
Ollama Client Module
====================
وحدة عميل Ollama

Client for interacting with locally-hosted Ollama models.
Provides support for code analysis, generation, and fixing tasks.

Supported Models:
    - codellama:13b - General code understanding and generation
    - deepseek-coder:6.7b - Code completion and fixing
    - mistral:7b - General purpose with code capabilities
    - llama2:7b - Fast inference for simple tasks

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class OllamaModel(StrEnum):
    """Available Ollama models for code tasks."""

    CODELLAMA_13B = "codellama:13b"
    CODELLAMA_7B = "codellama:7b"
    DEEPSEEK_CODER = "deepseek-coder:6.7b"
    MISTRAL_7B = "mistral:7b"
    LLAMA2_7B = "llama2:7b"
    QWEN_CODER = "qwen2.5-coder:7b"


@dataclass
class OllamaConfig:
    """Configuration for Ollama client."""

    base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    default_model: str = field(default_factory=lambda: os.getenv("OLLAMA_DEFAULT_MODEL", "codellama:13b"))
    timeout: float = 120.0
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class OllamaResponse:
    """Response from Ollama API."""

    model: str
    response: str
    done: bool
    created_at: datetime
    total_duration_ns: int | None = None
    load_duration_ns: int | None = None
    eval_count: int | None = None
    eval_duration_ns: int | None = None
    context: list[int] | None = None

    @property
    def tokens_per_second(self) -> float | None:
        """Calculate tokens per second."""
        if self.eval_count and self.eval_duration_ns:
            return self.eval_count / (self.eval_duration_ns / 1e9)
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "response": self.response,
            "done": self.done,
            "created_at": self.created_at.isoformat(),
            "total_duration_ns": self.total_duration_ns,
            "tokens_per_second": self.tokens_per_second,
        }


class OllamaError(Exception):
    """Exception raised for Ollama errors."""

    pass


class OllamaClient:
    """
    Client for Ollama API.

    عميل Ollama API

    Provides methods for code analysis, generation, and fixing
    using locally-hosted Ollama models.

    Example:
        client = OllamaClient()

        # Check if model is available
        if await client.is_model_available("codellama:13b"):
            # Generate code fix
            response = await client.generate(
                prompt="Fix this Python code: ...",
                model="codellama:13b"
            )
            print(response.response)
    """

    def __init__(self, config: OllamaConfig | None = None):
        """
        Initialize OllamaClient.

        Args:
            config: Ollama configuration
        """
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx is required for OllamaClient. Install with: pip install httpx")

        self.config = config or OllamaConfig()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def is_available(self) -> bool:
        """
        Check if Ollama server is available.

        التحقق من توفر خادم Ollama
        """
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[dict[str, Any]]:
        """
        List available models.

        قائمة النماذج المتاحة
        """
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            raise OllamaError(f"Failed to list models: {e}") from e

    async def is_model_available(self, model: str) -> bool:
        """
        Check if a specific model is available.

        التحقق من توفر نموذج محدد
        """
        try:
            models = await self.list_models()
            model_names = [m.get("name", "") for m in models]
            return model in model_names or any(model in name for name in model_names)
        except OllamaError:
            return False

    async def pull_model(self, model: str) -> bool:
        """
        Pull a model from Ollama registry.

        سحب نموذج من سجل Ollama
        """
        try:
            client = await self._get_client()
            response = await client.post(
                "/api/pull",
                json={"name": model},
                timeout=600.0,  # Model pulls can take a while
            )
            return response.status_code == 200
        except Exception as e:
            raise OllamaError(f"Failed to pull model {model}: {e}") from e

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        context: list[int] | None = None,
        options: dict[str, Any] | None = None,
    ) -> OllamaResponse:
        """
        Generate a response from the model.

        توليد استجابة من النموذج

        Args:
            prompt: The prompt to send
            model: Model to use (defaults to config default)
            system: System prompt
            context: Context from previous response
            options: Model options (temperature, top_p, etc.)

        Returns:
            OllamaResponse with generated text
        """
        model = model or self.config.default_model
        client = await self._get_client()

        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        if system:
            payload["system"] = system
        if context:
            payload["context"] = context
        if options:
            payload["options"] = options

        for attempt in range(self.config.max_retries):
            try:
                response = await client.post("/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()

                return OllamaResponse(
                    model=data.get("model", model),
                    response=data.get("response", ""),
                    done=data.get("done", True),
                    created_at=datetime.fromisoformat(data.get("created_at", datetime.now(UTC).isoformat())),
                    total_duration_ns=data.get("total_duration"),
                    load_duration_ns=data.get("load_duration"),
                    eval_count=data.get("eval_count"),
                    eval_duration_ns=data.get("eval_duration"),
                    context=data.get("context"),
                )

            except httpx.TimeoutException:
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))
                    continue
                raise OllamaError(f"Timeout after {self.config.max_retries} attempts")
            except httpx.HTTPStatusError as e:
                raise OllamaError(f"HTTP error: {e}") from e
            except Exception as e:
                raise OllamaError(f"Generation failed: {e}") from e

        # This should not be reached, but as a safety measure
        raise OllamaError("Max retries exceeded")

    async def generate_stream(
        self,
        prompt: str,
        model: str | None = None,
        system: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response from the model.

        توليد استجابة متدفقة من النموذج

        Args:
            prompt: The prompt to send
            model: Model to use
            system: System prompt
            options: Model options

        Yields:
            Response text chunks
        """
        model = model or self.config.default_model
        client = await self._get_client()

        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": True,
        }

        if system:
            payload["system"] = system
        if options:
            payload["options"] = options

        try:
            async with client.stream("POST", "/api/generate", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if text := data.get("response"):
                            yield text
                        if data.get("done"):
                            break
        except Exception as e:
            raise OllamaError(f"Streaming generation failed: {e}") from e

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> OllamaResponse:
        """
        Chat with the model using message history.

        الدردشة مع النموذج باستخدام سجل الرسائل

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            model: Model to use
            options: Model options

        Returns:
            OllamaResponse with generated text
        """
        model = model or self.config.default_model
        client = await self._get_client()

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }

        if options:
            payload["options"] = options

        try:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            return OllamaResponse(
                model=data.get("model", model),
                response=data.get("message", {}).get("content", ""),
                done=data.get("done", True),
                created_at=datetime.fromisoformat(data.get("created_at", datetime.now(UTC).isoformat())),
                total_duration_ns=data.get("total_duration"),
                eval_count=data.get("eval_count"),
                eval_duration_ns=data.get("eval_duration"),
            )

        except Exception as e:
            raise OllamaError(f"Chat failed: {e}") from e

    async def embeddings(
        self,
        prompt: str,
        model: str | None = None,
    ) -> list[float]:
        """
        Generate embeddings for text.

        توليد التضمينات للنص

        Args:
            prompt: Text to embed
            model: Model to use (default: nomic-embed-text)

        Returns:
            List of embedding values
        """
        model = model or "nomic-embed-text"
        client = await self._get_client()

        try:
            response = await client.post(
                "/api/embeddings",
                json={"model": model, "prompt": prompt},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])

        except Exception as e:
            raise OllamaError(f"Embeddings failed: {e}") from e


# Code-specific helper functions
async def analyze_code_with_ollama(
    code: str,
    language: str = "python",
    model: str = "codellama:13b",
    ollama_url: str | None = None,
) -> dict[str, Any]:
    """
    Analyze code using Ollama model.

    تحليل الكود باستخدام نموذج Ollama

    Args:
        code: Source code to analyze
        language: Programming language
        model: Ollama model to use
        ollama_url: Ollama server URL

    Returns:
        Analysis results
    """
    config = OllamaConfig()
    if ollama_url:
        config.base_url = ollama_url
    config.default_model = model

    client = OllamaClient(config)

    try:
        system_prompt = f"""You are an expert code analyzer for {language}.
Analyze the provided code and identify:
1. Bugs and errors
2. Security vulnerabilities
3. Performance issues
4. Style/best practice violations

Output your analysis as JSON with the following structure:
{{
    "issues": [
        {{
            "type": "bug|security|performance|style",
            "severity": "error|warning|info",
            "line": <line_number>,
            "message": "<description>",
            "suggestion": "<fix suggestion>"
        }}
    ],
    "summary": "<brief summary>"
}}"""

        response = await client.generate(
            prompt=f"Analyze this {language} code:\n\n```{language}\n{code}\n```",
            system=system_prompt,
            options={"temperature": 0.0},
        )

        # Try to parse JSON from response
        try:
            # Find JSON in response
            response_text = response.response
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response_text[start:end])
        except json.JSONDecodeError:
            # JSON parsing failed - LLM response may not be valid JSON.
            # Fall through to return raw response in fallback format below.
            pass

        return {
            "issues": [],
            "summary": response.response,
            "raw_response": response.response,
        }

    finally:
        await client.close()


async def fix_code_with_ollama(
    code: str,
    error: str,
    language: str = "python",
    model: str = "deepseek-coder:6.7b",
    ollama_url: str | None = None,
) -> str:
    """
    Fix code using Ollama model.

    إصلاح الكود باستخدام نموذج Ollama

    Args:
        code: Source code with error
        error: Error message or description
        language: Programming language
        model: Ollama model to use
        ollama_url: Ollama server URL

    Returns:
        Fixed code
    """
    config = OllamaConfig()
    if ollama_url:
        config.base_url = ollama_url
    config.default_model = model

    client = OllamaClient(config)

    try:
        system_prompt = f"""You are an expert {language} developer.
Fix the provided code based on the error description.
Return ONLY the fixed code without any explanation or markdown formatting."""

        response = await client.generate(
            prompt=f"""Fix this {language} code:

```{language}
{code}
```

Error: {error}

Return only the fixed code:""",
            system=system_prompt,
            options={"temperature": 0.0},
        )

        # Extract code from response
        response_text = response.response.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # Skip first and last lines (code block markers)
            lines = [line for line in lines[1:-1] if not line.startswith("```")]
            response_text = "\n".join(lines)

        return response_text

    finally:
        await client.close()


async def generate_tests_with_ollama(
    code: str,
    language: str = "python",
    framework: str = "pytest",
    model: str = "codellama:13b",
    ollama_url: str | None = None,
) -> str:
    """
    Generate tests using Ollama model.

    توليد الاختبارات باستخدام نموذج Ollama

    Args:
        code: Source code to test
        language: Programming language
        framework: Test framework
        model: Ollama model to use
        ollama_url: Ollama server URL

    Returns:
        Generated test code
    """
    config = OllamaConfig()
    if ollama_url:
        config.base_url = ollama_url
    config.default_model = model

    client = OllamaClient(config)

    try:
        system_prompt = f"""You are an expert {language} developer.
Generate comprehensive unit tests for the provided code using {framework}.
Include edge cases, error handling, and typical use cases.
Return ONLY the test code without any explanation."""

        response = await client.generate(
            prompt=f"""Generate {framework} tests for this {language} code:

```{language}
{code}
```

Return only the test code:""",
            system=system_prompt,
            options={"temperature": 0.1},
        )

        # Extract code from response
        response_text = response.response.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            lines = [line for line in lines[1:-1] if not line.startswith("```")]
            response_text = "\n".join(lines)

        return response_text

    finally:
        await client.close()
