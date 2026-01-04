"""
Unit Tests for Multi-Provider LLM Service
اختبارات الوحدة لخدمة نماذج اللغة متعددة المزودين
"""

import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_anthropic_package():
    """Mock anthropic package"""
    with patch.dict("sys.modules", {"anthropic": MagicMock()}):
        yield


@pytest.fixture
def mock_openai_package():
    """Mock openai package"""
    with patch.dict("sys.modules", {"openai": MagicMock()}):
        yield


class TestAnthropicProvider:
    """Test suite for Anthropic Claude provider"""

    @pytest.mark.asyncio
    async def test_chat_with_anthropic(self, mock_env_vars, mock_anthropic_client):
        """Test chat completion with Anthropic"""
        from src.llm.multi_provider import AnthropicProvider, LLMMessage

        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_anthropic:
            mock_anthropic.return_value = mock_anthropic_client

            provider = AnthropicProvider()
            assert provider.is_configured is True

            messages = [
                LLMMessage(role="system", content="You are a helpful assistant."),
                LLMMessage(role="user", content="Hello!"),
            ]

            response = await provider.chat(messages)

            assert response.content == "This is a test response from Claude."
            assert response.provider == "Anthropic Claude"
            assert response.tokens_used == 150
            assert response.latency_ms > 0

    @pytest.mark.asyncio
    async def test_complete_with_anthropic(self, mock_env_vars, mock_anthropic_client):
        """Test completion with Anthropic"""
        from src.llm.multi_provider import AnthropicProvider

        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_anthropic:
            mock_anthropic.return_value = mock_anthropic_client

            provider = AnthropicProvider()

            response = await provider.complete("What is agriculture?")

            assert "test response" in response.content.lower()
            assert response.provider == "Anthropic Claude"

    def test_anthropic_not_configured(self):
        """Test Anthropic provider when API key is missing"""
        from src.llm.multi_provider import AnthropicProvider

        with patch.dict(os.environ, {}, clear=True):
            provider = AnthropicProvider()
            assert provider.is_configured is False


class TestOpenAIProvider:
    """Test suite for OpenAI GPT provider"""

    @pytest.mark.asyncio
    async def test_chat_with_openai(self, mock_env_vars, mock_openai_client):
        """Test chat completion with OpenAI"""
        from src.llm.multi_provider import LLMMessage, OpenAIProvider

        with patch("src.llm.multi_provider.AsyncOpenAI") as mock_openai:
            mock_openai.return_value = mock_openai_client

            provider = OpenAIProvider()
            assert provider.is_configured is True

            messages = [LLMMessage(role="user", content="Hello!")]

            response = await provider.chat(messages)

            assert response.content == "This is a test response from GPT."
            assert response.provider == "OpenAI GPT"
            assert response.tokens_used == 200

    @pytest.mark.asyncio
    async def test_complete_with_openai(self, mock_env_vars, mock_openai_client):
        """Test completion with OpenAI"""
        from src.llm.multi_provider import OpenAIProvider

        with patch("src.llm.multi_provider.AsyncOpenAI") as mock_openai:
            mock_openai.return_value = mock_openai_client

            provider = OpenAIProvider()

            response = await provider.complete("What is farming?")

            assert "test response" in response.content.lower()

    def test_openai_not_configured(self):
        """Test OpenAI provider when API key is missing"""
        from src.llm.multi_provider import OpenAIProvider

        with patch.dict(os.environ, {}, clear=True):
            provider = OpenAIProvider()
            assert provider.is_configured is False


class TestMultiLLMService:
    """Test suite for Multi-LLM service with fallback"""

    @pytest.mark.asyncio
    async def test_chat_with_primary_provider(
        self, mock_env_vars, mock_anthropic_client
    ):
        """Test chat with primary provider (Anthropic)"""
        from src.llm.multi_provider import LLMMessage, MultiLLMService

        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_anthropic:
            mock_anthropic.return_value = mock_anthropic_client

            service = MultiLLMService()

            messages = [LLMMessage(role="user", content="Test message")]

            result = await service.chat(messages)

            assert result.success is True
            assert result.data is not None
            assert result.data.content == "This is a test response from Claude."
            assert result.provider == "Anthropic Claude"
            assert len(result.failed_providers) == 0

    @pytest.mark.asyncio
    async def test_fallback_to_secondary_provider(
        self, mock_env_vars, mock_openai_client
    ):
        """Test fallback when primary provider fails"""
        from src.llm.multi_provider import LLMMessage, MultiLLMService

        # Mock Anthropic to fail
        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_anthropic:
            mock_anthropic.side_effect = Exception("Anthropic API error")

            # Mock OpenAI to succeed
            with patch("src.llm.multi_provider.AsyncOpenAI") as mock_openai:
                mock_openai.return_value = mock_openai_client

                service = MultiLLMService()

                messages = [LLMMessage(role="user", content="Test")]

                result = await service.chat(messages)

                assert result.success is True
                assert result.data.provider == "OpenAI GPT"
                assert len(result.failed_providers) >= 1

    @pytest.mark.asyncio
    async def test_all_providers_fail(self, mock_env_vars):
        """Test when all providers fail"""
        from src.llm.multi_provider import LLMMessage, MultiLLMService

        # Mock all providers to fail
        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_anthropic:
            mock_anthropic.side_effect = Exception("Anthropic failed")

            with patch("src.llm.multi_provider.AsyncOpenAI") as mock_openai:
                mock_openai.side_effect = Exception("OpenAI failed")

                service = MultiLLMService()

                messages = [LLMMessage(role="user", content="Test")]

                result = await service.chat(messages)

                assert result.success is False
                assert result.data is None
                assert result.error == "All LLM providers failed"
                assert len(result.failed_providers) >= 2

    @pytest.mark.asyncio
    async def test_specific_provider_selection(self, mock_env_vars, mock_openai_client):
        """Test forcing a specific provider"""
        from src.llm.multi_provider import LLMMessage, MultiLLMService

        with patch("src.llm.multi_provider.AsyncOpenAI") as mock_openai:
            mock_openai.return_value = mock_openai_client

            service = MultiLLMService()

            messages = [LLMMessage(role="user", content="Test")]

            result = await service.chat(messages, specific_provider="openai")

            assert result.success is True
            assert "openai" in result.provider.lower()

    @pytest.mark.asyncio
    async def test_complete_method(self, mock_env_vars, mock_anthropic_client):
        """Test simple completion method"""
        from src.llm.multi_provider import MultiLLMService

        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_anthropic:
            mock_anthropic.return_value = mock_anthropic_client

            service = MultiLLMService()

            result = await service.complete("What is agriculture?")

            assert result.success is True
            assert result.data is not None

    def test_get_available_providers(self, mock_env_vars):
        """Test getting list of available providers"""
        from src.llm.multi_provider import MultiLLMService

        service = MultiLLMService()

        providers = service.get_available_providers()

        assert len(providers) == 3
        assert any(p["name"] == "Anthropic Claude" for p in providers)
        assert any(p["name"] == "OpenAI GPT" for p in providers)
        assert any(p["name"] == "Google Gemini" for p in providers)

    def test_get_primary_provider(self, mock_env_vars):
        """Test getting primary provider"""
        from src.llm.multi_provider import MultiLLMService

        service = MultiLLMService()

        primary = service.get_primary_provider()

        assert primary == "Anthropic Claude"

    def test_provider_priority_override(self, mock_env_vars):
        """Test overriding provider priority"""
        from src.llm.multi_provider import MultiLLMService

        service = MultiLLMService(primary_provider="openai")

        # Check that OpenAI is first in providers list
        assert len(service.providers) > 0
        if service.providers[0].is_configured:
            assert service.providers[0].name == "OpenAI GPT"


class TestLLMDataModels:
    """Test LLM data models"""

    def test_llm_message_creation(self):
        """Test LLMMessage creation"""
        from src.llm.multi_provider import LLMMessage

        msg = LLMMessage(role="user", content="Hello")

        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_llm_response_creation(self):
        """Test LLMResponse creation"""
        from src.llm.multi_provider import LLMResponse

        response = LLMResponse(
            content="Test response",
            provider="Test Provider",
            model="test-model-v1",
            tokens_used=100,
            latency_ms=250.5,
        )

        assert response.content == "Test response"
        assert response.provider == "Test Provider"
        assert response.tokens_used == 100
        assert response.latency_ms == 250.5

    def test_llm_result_success(self):
        """Test LLMResult success property"""
        from src.llm.multi_provider import LLMResponse, LLMResult

        response = LLMResponse(content="Success", provider="Test", model="test-1")

        result = LLMResult(data=response, provider="Test")

        assert result.success is True
        assert result.error is None

    def test_llm_result_failure(self):
        """Test LLMResult failure property"""
        from src.llm.multi_provider import LLMResult

        result = LLMResult(data=None, provider="None", error="Test error")

        assert result.success is False
        assert result.error == "Test error"
