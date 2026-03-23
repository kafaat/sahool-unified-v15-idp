"""
Tests for Ollama Client Module
==============================
اختبارات وحدة عميل Ollama

Tests for local LLM integration via Ollama.

Author: SAHOOL Platform Team
Updated: January 2026
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Skip all tests if httpx is not available
pytest.importorskip("httpx")

from shared.ai.ollama_client import (
    OllamaClient,
    OllamaConfig,
    OllamaModel,
    OllamaResponse,
    analyze_code_with_ollama,
    fix_code_with_ollama,
    generate_tests_with_ollama,
)

# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def ollama_config():
    """Create test Ollama configuration."""
    return OllamaConfig(
        base_url="http://test-ollama:11434",
        default_model="codellama:7b",
        timeout=30.0,
        max_retries=2,
    )


@pytest.fixture
def sample_response():
    """Create sample Ollama response data."""
    return {
        "model": "codellama:7b",
        "response": "def hello():\n    print('Hello')",
        "done": True,
        "created_at": datetime.utcnow().isoformat(),
        "total_duration": 1000000000,
        "load_duration": 100000000,
        "eval_count": 50,
        "eval_duration": 500000000,
        "context": [1, 2, 3, 4, 5],
    }


# ═══════════════════════════════════════════════════════════════════════════
# Test Configuration
# ═══════════════════════════════════════════════════════════════════════════


class TestOllamaConfig:
    """Tests for OllamaConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = OllamaConfig()

        assert "localhost:11434" in config.base_url
        assert config.timeout == 120.0
        assert config.max_retries == 3

    def test_custom_config(self, ollama_config):
        """Test custom configuration."""
        assert ollama_config.base_url == "http://test-ollama:11434"
        assert ollama_config.default_model == "codellama:7b"
        assert ollama_config.timeout == 30.0


# ═══════════════════════════════════════════════════════════════════════════
# Test Response
# ═══════════════════════════════════════════════════════════════════════════


class TestOllamaResponse:
    """Tests for OllamaResponse class."""

    def test_response_creation(self, sample_response):
        """Test OllamaResponse creation."""
        response = OllamaResponse(
            model=sample_response["model"],
            response=sample_response["response"],
            done=sample_response["done"],
            created_at=datetime.fromisoformat(sample_response["created_at"]),
            total_duration_ns=sample_response["total_duration"],
            eval_count=sample_response["eval_count"],
            eval_duration_ns=sample_response["eval_duration"],
        )

        assert response.model == "codellama:7b"
        assert "def hello()" in response.response
        assert response.done is True

    def test_tokens_per_second(self):
        """Test tokens per second calculation."""
        response = OllamaResponse(
            model="test",
            response="test",
            done=True,
            created_at=datetime.utcnow(),
            eval_count=100,
            eval_duration_ns=1_000_000_000,  # 1 second
        )

        assert response.tokens_per_second == 100.0

    def test_tokens_per_second_none(self):
        """Test tokens per second when data unavailable."""
        response = OllamaResponse(
            model="test",
            response="test",
            done=True,
            created_at=datetime.utcnow(),
        )

        assert response.tokens_per_second is None

    def test_to_dict(self, sample_response):
        """Test response to dictionary conversion."""
        response = OllamaResponse(
            model=sample_response["model"],
            response=sample_response["response"],
            done=sample_response["done"],
            created_at=datetime.fromisoformat(sample_response["created_at"]),
            total_duration_ns=sample_response["total_duration"],
            eval_count=sample_response["eval_count"],
            eval_duration_ns=sample_response["eval_duration"],
        )

        data = response.to_dict()

        assert data["model"] == "codellama:7b"
        assert data["done"] is True
        assert "created_at" in data


# ═══════════════════════════════════════════════════════════════════════════
# Test Client
# ═══════════════════════════════════════════════════════════════════════════


class TestOllamaClient:
    """Tests for OllamaClient class."""

    @pytest.mark.asyncio
    async def test_is_available_success(self, ollama_config):
        """Test server availability check - success case."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            client = OllamaClient(ollama_config)
            client._client = mock_client

            is_available = await client.is_available()

            assert is_available is True

    @pytest.mark.asyncio
    async def test_is_available_failure(self, ollama_config):
        """Test server availability check - failure case."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
            mock_client_class.return_value = mock_client

            client = OllamaClient(ollama_config)
            client._client = mock_client

            is_available = await client.is_available()

            assert is_available is False

    @pytest.mark.asyncio
    async def test_list_models(self, ollama_config):
        """Test listing available models."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "codellama:7b", "size": 3791730596},
                    {"name": "mistral:7b", "size": 4109865159},
                ]
            }
            mock_response.raise_for_status = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            client = OllamaClient(ollama_config)
            client._client = mock_client

            models = await client.list_models()

            assert len(models) == 2
            assert models[0]["name"] == "codellama:7b"

    @pytest.mark.asyncio
    async def test_is_model_available(self, ollama_config):
        """Test checking if a specific model is available."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "models": [
                    {"name": "codellama:7b"},
                    {"name": "mistral:7b"},
                ]
            }
            mock_response.raise_for_status = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            client = OllamaClient(ollama_config)
            client._client = mock_client

            assert await client.is_model_available("codellama:7b") is True
            assert await client.is_model_available("nonexistent:model") is False

    @pytest.mark.asyncio
    async def test_generate(self, ollama_config, sample_response):
        """Test text generation."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_response
            mock_response.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            client = OllamaClient(ollama_config)
            client._client = mock_client

            response = await client.generate(
                prompt="Write a hello world function",
                model="codellama:7b",
            )

            assert response.model == "codellama:7b"
            assert "def hello()" in response.response
            assert response.done is True

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, ollama_config, sample_response):
        """Test generation with system prompt."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_response
            mock_response.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            client = OllamaClient(ollama_config)
            client._client = mock_client

            response = await client.generate(
                prompt="Fix this code",
                system="You are a Python expert",
                options={"temperature": 0.0},
            )

            # Verify the call included system prompt
            call_args = mock_client.post.call_args
            payload = call_args[1]["json"]
            assert payload["system"] == "You are a Python expert"
            assert payload["options"]["temperature"] == 0.0

    @pytest.mark.asyncio
    async def test_chat(self, ollama_config):
        """Test chat interface."""
        chat_response = {
            "model": "codellama:7b",
            "message": {"role": "assistant", "content": "Here is the fixed code..."},
            "done": True,
            "created_at": datetime.utcnow().isoformat(),
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = chat_response
            mock_response.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            client = OllamaClient(ollama_config)
            client._client = mock_client

            response = await client.chat(
                messages=[
                    {"role": "user", "content": "Fix this Python code"},
                ]
            )

            assert "fixed code" in response.response.lower()

    @pytest.mark.asyncio
    async def test_embeddings(self, ollama_config):
        """Test embeddings generation."""
        embedding_response = {
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = embedding_response
            mock_response.raise_for_status = MagicMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            client = OllamaClient(ollama_config)
            client._client = mock_client

            embedding = await client.embeddings("Hello world")

            assert len(embedding) == 5
            assert embedding[0] == 0.1


# ═══════════════════════════════════════════════════════════════════════════
# Test Helper Functions
# ═══════════════════════════════════════════════════════════════════════════


class TestHelperFunctions:
    """Tests for helper functions."""

    @pytest.mark.asyncio
    async def test_analyze_code_with_ollama(self):
        """Test code analysis helper function."""
        analysis_response = {
            "model": "codellama:13b",
            "response": json.dumps(
                {
                    "issues": [
                        {
                            "type": "style",
                            "severity": "warning",
                            "line": 1,
                            "message": "Missing docstring",
                            "suggestion": "Add a docstring",
                        }
                    ],
                    "summary": "1 issue found",
                }
            ),
            "done": True,
            "created_at": datetime.utcnow().isoformat(),
        }

        with patch("shared.ai.ollama_client.OllamaClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = OllamaResponse(
                model="codellama:13b",
                response=analysis_response["response"],
                done=True,
                created_at=datetime.utcnow(),
            )
            mock_client.generate = AsyncMock(return_value=mock_response)
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            result = await analyze_code_with_ollama(
                code="def hello(): pass",
                language="python",
            )

            assert "issues" in result
            assert len(result["issues"]) == 1

    @pytest.mark.asyncio
    async def test_fix_code_with_ollama(self):
        """Test code fixing helper function."""
        fix_response = OllamaResponse(
            model="deepseek-coder:6.7b",
            response="def hello():\n    pass  # Fixed",
            done=True,
            created_at=datetime.utcnow(),
        )

        with patch("shared.ai.ollama_client.OllamaClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.generate = AsyncMock(return_value=fix_response)
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            result = await fix_code_with_ollama(
                code="def hello() pass",
                error="SyntaxError: invalid syntax",
            )

            assert "def hello():" in result

    @pytest.mark.asyncio
    async def test_generate_tests_with_ollama(self):
        """Test test generation helper function."""
        test_response = OllamaResponse(
            model="codellama:13b",
            response="""def test_hello():
    assert hello() is None

def test_hello_output(capsys):
    hello()
    captured = capsys.readouterr()
    assert "Hello" in captured.out
""",
            done=True,
            created_at=datetime.utcnow(),
        )

        with patch("shared.ai.ollama_client.OllamaClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.generate = AsyncMock(return_value=test_response)
            mock_client.close = AsyncMock()
            mock_client_class.return_value = mock_client

            result = await generate_tests_with_ollama(
                code="def hello():\n    print('Hello')",
                language="python",
                framework="pytest",
            )

            assert "def test_hello" in result


# ═══════════════════════════════════════════════════════════════════════════
# Test Model Enum
# ═══════════════════════════════════════════════════════════════════════════


class TestOllamaModel:
    """Tests for OllamaModel enum."""

    def test_model_values(self):
        """Test model enum values."""
        assert OllamaModel.CODELLAMA_13B.value == "codellama:13b"
        assert OllamaModel.DEEPSEEK_CODER.value == "deepseek-coder:6.7b"
        assert OllamaModel.MISTRAL_7B.value == "mistral:7b"

    def test_model_string_conversion(self):
        """Test model enum string conversion."""
        model = OllamaModel.CODELLAMA_7B

        # Test value access (consistent across Python versions)
        assert model.value == "codellama:7b"

        # Test name access
        assert model.name == "CODELLAMA_7B"

        # str() behavior varies between Python versions:
        # Python 3.11: returns value ("codellama:7b")
        # Python 3.12+: returns full enum name ("OllamaModel.CODELLAMA_7B")
        # So we test that it's one of the expected values
        str_result = str(model)
        assert str_result in ("codellama:7b", "OllamaModel.CODELLAMA_7B")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
