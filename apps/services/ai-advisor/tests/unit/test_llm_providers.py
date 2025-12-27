"""
Unit Tests for LLM Providers
اختبارات وحدة لمزودي LLM
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.llm.multi_provider import MultiProviderLLM


class TestMultiProviderLLM:
    """Test suite for MultiProviderLLM class"""

    def test_init_with_default_provider(self):
        """Test initialization with default provider"""
        llm = MultiProviderLLM()
        assert llm.default_provider in ["anthropic", "openai", "google"]

    def test_init_with_custom_provider(self):
        """Test initialization with custom provider"""
        llm = MultiProviderLLM(default_provider="openai")
        assert llm.default_provider == "openai"

    def test_init_with_invalid_provider(self):
        """Test initialization with invalid provider raises error"""
        with pytest.raises(ValueError):
            MultiProviderLLM(default_provider="invalid_provider")

    @pytest.mark.asyncio
    async def test_generate_with_anthropic(self, mock_anthropic_client):
        """Test text generation with Anthropic Claude"""
        with patch("src.llm.multi_provider.anthropic.AsyncAnthropic", return_value=mock_anthropic_client):
            llm = MultiProviderLLM(default_provider="anthropic")

            response = await llm.generate(
                prompt="What is the best time to plant wheat?",
                max_tokens=500
            )

            assert response is not None
            assert "text" in response
            assert response["provider"] == "anthropic"
            mock_anthropic_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_openai(self, mock_openai_client):
        """Test text generation with OpenAI GPT"""
        with patch("src.llm.multi_provider.openai.AsyncOpenAI", return_value=mock_openai_client):
            llm = MultiProviderLLM(default_provider="openai")

            response = await llm.generate(
                prompt="What is the best fertilizer for tomatoes?",
                max_tokens=500
            )

            assert response is not None
            assert "text" in response
            assert response["provider"] == "openai"
            mock_openai_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_with_context(self, mock_anthropic_client):
        """Test text generation with conversation context"""
        with patch("src.llm.multi_provider.anthropic.AsyncAnthropic", return_value=mock_anthropic_client):
            llm = MultiProviderLLM()

            context = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi, how can I help you?"}
            ]

            response = await llm.generate(
                prompt="Tell me about wheat diseases",
                context=context,
                max_tokens=500
            )

            assert response is not None
            assert "text" in response

    @pytest.mark.asyncio
    async def test_generate_with_system_message(self, mock_anthropic_client):
        """Test text generation with custom system message"""
        with patch("src.llm.multi_provider.anthropic.AsyncAnthropic", return_value=mock_anthropic_client):
            llm = MultiProviderLLM()

            response = await llm.generate(
                prompt="What is photosynthesis?",
                system_message="You are an expert agricultural scientist.",
                max_tokens=500
            )

            assert response is not None
            assert "text" in response

    @pytest.mark.asyncio
    async def test_generate_handles_api_error(self):
        """Test error handling when API call fails"""
        mock_client = AsyncMock()
        mock_client.messages.create.side_effect = Exception("API Error")

        with patch("src.llm.multi_provider.anthropic.AsyncAnthropic", return_value=mock_client):
            llm = MultiProviderLLM()

            with pytest.raises(Exception):
                await llm.generate(
                    prompt="Test prompt",
                    max_tokens=500
                )

    @pytest.mark.asyncio
    async def test_fallback_to_secondary_provider(self, mock_openai_client):
        """Test fallback mechanism when primary provider fails"""
        # Mock primary provider failure
        mock_failing_client = AsyncMock()
        mock_failing_client.messages.create.side_effect = Exception("Anthropic API Error")

        with patch("src.llm.multi_provider.anthropic.AsyncAnthropic", return_value=mock_failing_client):
            with patch("src.llm.multi_provider.openai.AsyncOpenAI", return_value=mock_openai_client):
                llm = MultiProviderLLM(default_provider="anthropic", fallback_providers=["openai"])

                response = await llm.generate(
                    prompt="Test prompt",
                    max_tokens=500
                )

                assert response is not None
                assert response["provider"] == "openai"

    def test_token_counting(self):
        """Test token estimation functionality"""
        llm = MultiProviderLLM()

        text = "This is a test sentence for token counting."
        tokens = llm.estimate_tokens(text)

        assert isinstance(tokens, int)
        assert tokens > 0

    @pytest.mark.asyncio
    async def test_streaming_generation(self, mock_anthropic_client):
        """Test streaming text generation"""
        async def mock_stream():
            yield {"text": "Partial "}
            yield {"text": "response "}
            yield {"text": "text"}

        mock_anthropic_client.messages.stream = AsyncMock(return_value=mock_stream())

        with patch("src.llm.multi_provider.anthropic.AsyncAnthropic", return_value=mock_anthropic_client):
            llm = MultiProviderLLM()

            chunks = []
            async for chunk in llm.generate_stream(
                prompt="Tell me about agriculture",
                max_tokens=500
            ):
                chunks.append(chunk)

            assert len(chunks) > 0
