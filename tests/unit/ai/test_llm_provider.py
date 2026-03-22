"""
Tests for LLM Provider Manager Module
=====================================
اختبارات وحدة مدير مزودي LLM

Comprehensive tests for LLM provider management and fallback mechanisms.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.ai.llm_provider import (
    AllProvidersFailedError,
    LLMConfig,
    LLMProvider,
    LLMProviderError,
    LLMProviderManager,
    LLMResponse,
    generate_text,
    generate_with_ollama_fallback,
    get_llm_manager,
)

# ═══════════════════════════════════════════════════════════════════════════
# Test Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def llm_config() -> LLMConfig:
    """Create a test LLM config."""
    return LLMConfig(
        provider=LLMProvider.OLLAMA,
        model="codellama:7b",
        temperature=0.1,
        max_tokens=1000,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Test LLMProvider Enum
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMProvider:
    """Tests for LLMProvider enum."""

    def test_providers_exist(self):
        """Test that all expected providers exist."""
        assert LLMProvider.OLLAMA
        assert LLMProvider.ANTHROPIC
        assert LLMProvider.OPENAI
        assert LLMProvider.GOOGLE

    def test_provider_values(self):
        """Test provider string values."""
        assert LLMProvider.OLLAMA.value == "ollama"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.OPENAI.value == "openai"


# ═══════════════════════════════════════════════════════════════════════════
# Test LLMConfig
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMConfig:
    """Tests for LLMConfig data class."""

    def test_config_creation(self, llm_config: LLMConfig):
        """Test creating LLM config."""
        assert llm_config.provider == LLMProvider.OLLAMA
        assert llm_config.model == "codellama:7b"
        assert llm_config.temperature == 0.1
        assert llm_config.max_tokens == 1000

    def test_config_defaults(self):
        """Test config default values."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-haiku",
        )

        assert config.temperature == 0.7  # default
        assert config.max_tokens == 4096  # default

    def test_config_from_env(self):
        """Test config from environment."""
        config = LLMConfig.from_env(LLMProvider.OLLAMA)

        assert config.provider == LLMProvider.OLLAMA
        assert "codellama" in config.model.lower()


# ═══════════════════════════════════════════════════════════════════════════
# Test LLMResponse
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMResponse:
    """Tests for LLMResponse data class."""

    def test_response_creation(self):
        """Test creating LLM response."""
        response = LLMResponse(
            text="Hello, world!",
            provider=LLMProvider.OLLAMA,
            model="codellama:7b",
            tokens_input=10,
            tokens_output=5,
            latency_ms=150.5,
            cost_usd=0.0,
        )

        assert response.text == "Hello, world!"
        assert response.provider == LLMProvider.OLLAMA
        assert response.tokens_output == 5

    def test_response_to_dict(self):
        """Test converting response to dictionary."""
        response = LLMResponse(
            text="Test response",
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-haiku",
            tokens_input=100,
            tokens_output=50,
            latency_ms=200,
            cost_usd=0.0005,
        )

        data = response.to_dict()

        assert data["text"] == "Test response"
        assert data["provider"] == "anthropic"
        assert data["cost_usd"] == 0.0005


# ═══════════════════════════════════════════════════════════════════════════
# Test LLMProviderError
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMProviderError:
    """Tests for LLMProviderError."""

    def test_error_creation(self):
        """Test creating provider error."""
        error = LLMProviderError(
            message="Connection failed",
            provider=LLMProvider.OLLAMA,
        )

        assert str(error) == "Connection failed"
        assert error.provider == LLMProvider.OLLAMA

    def test_error_without_provider(self):
        """Test error without provider."""
        error = LLMProviderError("Generic error")

        assert error.provider is None


class TestAllProvidersFailedError:
    """Tests for AllProvidersFailedError."""

    def test_error_with_errors(self):
        """Test error with provider errors."""
        errors = [
            (LLMProvider.OLLAMA, "Timeout"),
            (LLMProvider.ANTHROPIC, "Rate limited"),
        ]

        error = AllProvidersFailedError(errors=errors)

        assert len(error.errors) == 2
        assert "Timeout" in str(error)
        assert "Rate limited" in str(error)


# ═══════════════════════════════════════════════════════════════════════════
# Test LLMProviderManager
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMProviderManager:
    """Tests for LLMProviderManager class."""

    def test_initialization(self):
        """Test provider manager initialization."""
        manager = LLMProviderManager()

        assert manager is not None

    def test_configs_exist(self):
        """Test that provider configs are initialized."""
        manager = LLMProviderManager()

        # Manager should have configs
        assert hasattr(manager, "configs")

    @pytest.mark.asyncio
    async def test_generate_with_mock(self):
        """Test generate with mocked provider."""
        manager = LLMProviderManager()

        with patch.object(
            manager,
            "_call_ollama",
            new_callable=AsyncMock,
        ) as mock_ollama:
            mock_ollama.return_value = LLMResponse(
                text="Mocked response",
                provider=LLMProvider.OLLAMA,
                model="codellama:7b",
                tokens_input=10,
                tokens_output=5,
                latency_ms=100,
                cost_usd=0.0,
            )

            response = await manager.generate(
                prompt="Test prompt",
                preferred_provider=LLMProvider.OLLAMA,
            )

            assert response.text == "Mocked response"
            assert response.provider == LLMProvider.OLLAMA


# ═══════════════════════════════════════════════════════════════════════════
# Test Module Functions
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_get_llm_manager_returns_manager(self):
        """Test that get_llm_manager returns a manager."""
        manager = get_llm_manager()

        assert manager is not None
        assert isinstance(manager, LLMProviderManager)

    @pytest.mark.asyncio
    async def test_generate_text_function(self):
        """Test generate_text convenience function."""
        with patch("shared.ai.llm_provider.get_llm_manager") as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.generate = AsyncMock(
                return_value=LLMResponse(
                    text="Generated text",
                    provider=LLMProvider.OLLAMA,
                    model="codellama:7b",
                    tokens_input=10,
                    tokens_output=5,
                    latency_ms=100,
                    cost_usd=0.0,
                )
            )
            mock_get_manager.return_value = mock_manager

            response = await generate_text("Test prompt")

            assert response.text == "Generated text"

    @pytest.mark.asyncio
    async def test_generate_with_ollama_fallback(self):
        """Test generate_with_ollama_fallback function."""
        with patch("shared.ai.llm_provider.get_llm_manager") as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.generate = AsyncMock(
                return_value=LLMResponse(
                    text="Ollama response",
                    provider=LLMProvider.OLLAMA,
                    model="codellama:7b",
                    tokens_input=10,
                    tokens_output=5,
                    latency_ms=100,
                    cost_usd=0.0,
                )
            )
            mock_get_manager.return_value = mock_manager

            response = await generate_with_ollama_fallback("Test prompt")

            assert response.text == "Ollama response"


# ═══════════════════════════════════════════════════════════════════════════
# Test Edge Cases
# ═══════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests for edge cases."""

    def test_config_with_api_key(self):
        """Test config with API key."""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-haiku",
            api_key="test-key",
        )

        assert config.api_key == "test-key"

    def test_config_priority(self):
        """Test config priority setting."""
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="codellama:7b",
            priority=0,
        )

        assert config.priority == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
