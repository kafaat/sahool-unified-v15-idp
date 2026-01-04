"""
Unit Tests for Multi-Provider LLM Service
اختبارات الوحدة لخدمة نماذج اللغة متعددة المزودين

Tests the multi-provider LLM functionality including:
- Provider initialization
- Fallback mechanism
- Individual provider functionality
"""

from unittest.mock import AsyncMock, patch

import pytest
from llm.multi_provider import (
    AnthropicProvider,
    GoogleGeminiProvider,
    LLMMessage,
    MultiLLMService,
    OpenAIProvider,
)


class TestAnthropicProvider:
    """Test Anthropic Claude provider"""

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_provider_configured(self):
        """Test provider is configured when API key is set"""
        provider = AnthropicProvider()
        assert provider.is_configured is True
        assert provider.name == "Anthropic Claude"

    @patch.dict("os.environ", {}, clear=True)
    def test_provider_not_configured(self):
        """Test provider is not configured without API key"""
        provider = AnthropicProvider()
        assert provider.is_configured is False

    @patch.dict(
        "os.environ", {"ANTHROPIC_API_KEY": "test_key", "CLAUDE_MODEL": "claude-3-opus"}
    )
    def test_default_model(self):
        """Test default model configuration"""
        provider = AnthropicProvider()
        assert provider.default_model == "claude-3-opus"

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_chat_success(self, mock_anthropic_client):
        """Test successful chat completion"""
        with patch("llm.multi_provider.AsyncAnthropic") as mock_class:
            mock_class.return_value = mock_anthropic_client

            provider = AnthropicProvider()
            messages = [
                LLMMessage(role="system", content="You are a helpful assistant"),
                LLMMessage(role="user", content="Hello"),
            ]

            response = await provider.chat(messages)

            assert response.content == "Test response from Claude"
            assert response.provider == "Anthropic Claude"
            assert response.tokens_used == 150
            assert mock_anthropic_client.messages.create.called

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_complete_success(self, mock_anthropic_client):
        """Test successful text completion"""
        with patch("llm.multi_provider.AsyncAnthropic") as mock_class:
            mock_class.return_value = mock_anthropic_client

            provider = AnthropicProvider()
            response = await provider.complete("What is photosynthesis?")

            assert response.content == "Test response from Claude"
            assert mock_anthropic_client.messages.create.called


class TestOpenAIProvider:
    """Test OpenAI GPT provider"""

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_provider_configured(self):
        """Test provider is configured when API key is set"""
        provider = OpenAIProvider()
        assert provider.is_configured is True
        assert provider.name == "OpenAI GPT"

    @patch.dict("os.environ", {}, clear=True)
    def test_provider_not_configured(self):
        """Test provider is not configured without API key"""
        provider = OpenAIProvider()
        assert provider.is_configured is False

    @patch.dict(
        "os.environ", {"OPENAI_API_KEY": "test_key", "OPENAI_MODEL": "gpt-4-turbo"}
    )
    def test_default_model(self):
        """Test default model configuration"""
        provider = OpenAIProvider()
        assert provider.default_model == "gpt-4-turbo"

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    async def test_chat_success(self, mock_openai_client):
        """Test successful chat completion"""
        with patch("llm.multi_provider.AsyncOpenAI") as mock_class:
            mock_class.return_value = mock_openai_client

            provider = OpenAIProvider()
            messages = [LLMMessage(role="user", content="Hello")]

            response = await provider.chat(messages)

            assert response.content == "Test response from GPT"
            assert response.provider == "OpenAI GPT"
            assert response.tokens_used == 150
            assert mock_openai_client.chat.completions.create.called


class TestGoogleGeminiProvider:
    """Test Google Gemini provider"""

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"})
    def test_provider_configured(self):
        """Test provider is configured when API key is set"""
        provider = GoogleGeminiProvider()
        assert provider.is_configured is True
        assert provider.name == "Google Gemini"

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"})
    def test_provider_configured_alt_key(self):
        """Test provider works with alternate API key name"""
        provider = GoogleGeminiProvider()
        assert provider.is_configured is True

    @patch.dict("os.environ", {}, clear=True)
    def test_provider_not_configured(self):
        """Test provider is not configured without API key"""
        provider = GoogleGeminiProvider()
        assert provider.is_configured is False


class TestMultiLLMService:
    """Test multi-provider LLM service"""

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    def test_initialization_anthropic_primary(self):
        """Test service initializes with Anthropic as primary"""
        service = MultiLLMService()
        assert len(service.providers) >= 1
        assert service.get_primary_provider() == "Anthropic Claude"

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_initialization_openai_primary(self):
        """Test service initializes with OpenAI as primary when specified"""
        service = MultiLLMService(primary_provider="openai")
        assert len(service.providers) >= 1
        # First provider should be OpenAI
        configured_providers = [p for p in service.providers if p.is_configured]
        if configured_providers:
            assert "OpenAI" in configured_providers[0].name

    @patch.dict(
        "os.environ",
        {
            "ANTHROPIC_API_KEY": "test_key1",
            "OPENAI_API_KEY": "test_key2",
            "GOOGLE_API_KEY": "test_key3",
        },
    )
    def test_multiple_providers_configured(self):
        """Test service with multiple providers configured"""
        service = MultiLLMService()
        configured = [p for p in service.providers if p.is_configured]
        assert len(configured) == 3

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_chat_success_primary(self, mock_anthropic_client):
        """Test chat with primary provider succeeds"""
        with patch("llm.multi_provider.AsyncAnthropic") as mock_class:
            mock_class.return_value = mock_anthropic_client

            service = MultiLLMService()
            messages = [LLMMessage(role="user", content="Hello")]

            result = await service.chat(messages)

            assert result.success is True
            assert result.data is not None
            assert result.data.content == "Test response from Claude"
            assert result.provider == "Anthropic Claude"
            assert len(result.failed_providers) == 0

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ", {"ANTHROPIC_API_KEY": "test_key", "OPENAI_API_KEY": "test_key2"}
    )
    async def test_fallback_mechanism(self, mock_openai_client):
        """Test fallback to secondary provider when primary fails"""
        with patch("llm.multi_provider.AsyncAnthropic") as mock_anthropic_class:
            # Make Anthropic fail
            mock_anthropic = AsyncMock()
            mock_anthropic.messages.create = AsyncMock(
                side_effect=Exception("Anthropic API error")
            )
            mock_anthropic_class.return_value = mock_anthropic

            with patch("llm.multi_provider.AsyncOpenAI") as mock_openai_class:
                mock_openai_class.return_value = mock_openai_client

                service = MultiLLMService()
                messages = [LLMMessage(role="user", content="Hello")]

                result = await service.chat(messages)

                # Should fallback to OpenAI
                assert result.success is True
                assert result.provider == "OpenAI GPT"
                assert len(result.failed_providers) == 1
                assert "Anthropic" in result.failed_providers[0]

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_all_providers_fail(self):
        """Test behavior when all providers fail"""
        with patch("llm.multi_provider.AsyncAnthropic") as mock_class:
            mock_client = AsyncMock()
            mock_client.messages.create = AsyncMock(side_effect=Exception("API error"))
            mock_class.return_value = mock_client

            service = MultiLLMService()
            messages = [LLMMessage(role="user", content="Hello")]

            result = await service.chat(messages)

            assert result.success is False
            assert result.data is None
            assert result.error == "All LLM providers failed"
            assert len(result.failed_providers) > 0

    @pytest.mark.asyncio
    @patch.dict(
        "os.environ", {"ANTHROPIC_API_KEY": "test_key", "OPENAI_API_KEY": "test_key2"}
    )
    async def test_specific_provider_selection(self, mock_openai_client):
        """Test forcing specific provider"""
        with patch("llm.multi_provider.AsyncOpenAI") as mock_class:
            mock_class.return_value = mock_openai_client

            service = MultiLLMService()
            messages = [LLMMessage(role="user", content="Hello")]

            # Force OpenAI even though Anthropic is primary
            result = await service.chat(messages, specific_provider="openai")

            assert result.success is True
            assert "OpenAI" in result.provider

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_complete_method(self, mock_anthropic_client):
        """Test simple complete method"""
        with patch("llm.multi_provider.AsyncAnthropic") as mock_class:
            mock_class.return_value = mock_anthropic_client

            service = MultiLLMService()
            result = await service.complete("What is AI?")

            assert result.success is True
            assert result.data.content == "Test response from Claude"

    @patch.dict(
        "os.environ", {"ANTHROPIC_API_KEY": "test_key1", "OPENAI_API_KEY": "test_key2"}
    )
    def test_get_available_providers(self):
        """Test getting available providers information"""
        service = MultiLLMService()
        providers = service.get_available_providers()

        assert len(providers) == 3  # Anthropic, OpenAI, Google
        assert all("name" in p for p in providers)
        assert all("configured" in p for p in providers)

        # Check Anthropic is configured
        anthropic = next(p for p in providers if "Anthropic" in p["name"])
        assert anthropic["configured"] is True
