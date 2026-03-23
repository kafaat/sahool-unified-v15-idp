"""
Unit Tests for Multi-Provider LLM Service
اختبارات الوحدة لخدمة نماذج اللغة متعددة المزودين

Tests the multi-provider LLM functionality including:
- Provider initialization
- Fallback mechanism
- Individual provider functionality
- Ollama local LLM provider
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add ai-advisor root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.llm.multi_provider import (
        AnthropicProvider,
        GoogleGeminiProvider,
        LLMMessage,
        MultiLLMService,
        OllamaProvider,
        OpenAIProvider,
    )
except ImportError:
    pytest.skip("ai-advisor dependencies not installed", allow_module_level=True)


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

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key", "CLAUDE_MODEL": "claude-3-opus"})
    def test_default_model(self):
        """Test default model configuration"""
        provider = AnthropicProvider()
        assert provider.default_model == "claude-3-opus"

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"})
    async def test_chat_success(self, mock_anthropic_client):
        """Test successful chat completion"""
        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_class:
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
        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_class:
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

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key", "OPENAI_MODEL": "gpt-4-turbo"})
    def test_default_model(self):
        """Test default model configuration"""
        provider = OpenAIProvider()
        assert provider.default_model == "gpt-4-turbo"

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    async def test_chat_success(self, mock_openai_client):
        """Test successful chat completion"""
        with patch("src.llm.multi_provider.AsyncOpenAI") as mock_class:
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
        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_class:
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
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key", "OPENAI_API_KEY": "test_key2"})
    async def test_fallback_mechanism(self, mock_openai_client):
        """Test fallback to secondary provider when primary fails"""
        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_anthropic_class:
            # Make Anthropic fail
            mock_anthropic = AsyncMock()
            mock_anthropic.messages.create = AsyncMock(side_effect=Exception("Anthropic API error"))
            mock_anthropic_class.return_value = mock_anthropic

            with patch("src.llm.multi_provider.AsyncOpenAI") as mock_openai_class:
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
        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_class:
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
    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key", "OPENAI_API_KEY": "test_key2"})
    async def test_specific_provider_selection(self, mock_openai_client):
        """Test forcing specific provider"""
        with patch("src.llm.multi_provider.AsyncOpenAI") as mock_class:
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
        with patch("src.llm.multi_provider.AsyncAnthropic") as mock_class:
            mock_class.return_value = mock_anthropic_client

            service = MultiLLMService()
            result = await service.complete("What is AI?")

            assert result.success is True
            assert result.data.content == "Test response from Claude"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key1", "OPENAI_API_KEY": "test_key2"})
    @patch("httpx.Client")
    def test_get_available_providers(self, mock_client_class):
        """Test getting available providers information"""
        # Mock Ollama server check
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        service = MultiLLMService()
        providers = service.get_available_providers()

        assert len(providers) == 4  # Anthropic, OpenAI, Google, Ollama
        assert all("name" in p for p in providers)
        assert all("configured" in p for p in providers)

        # Check Anthropic is configured
        anthropic = next(p for p in providers if "Anthropic" in p["name"])
        assert anthropic["configured"] is True


class TestOllamaProvider:
    """
    Test Ollama local LLM provider
    اختبارات مزود Ollama للنماذج المحلية
    """

    @patch("httpx.Client")
    def test_provider_configured_when_server_available(self, mock_client_class):
        """Test provider is configured when Ollama server is available"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()
        assert provider.is_configured is True
        assert provider.name == "Ollama Local"
        assert provider.name_ar == "أولاما المحلي"

    @patch("httpx.Client")
    def test_provider_not_configured_when_server_unavailable(self, mock_client_class):
        """Test provider is not configured when Ollama server is unavailable"""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = Exception("Connection refused")
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()
        assert provider.is_configured is False

    @patch.dict("os.environ", {"OLLAMA_MODEL": "mistral"})
    @patch("httpx.Client")
    def test_default_model_from_env(self, mock_client_class):
        """Test default model configuration from environment"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()
        assert provider.default_model == "mistral"

    @patch.dict("os.environ", {"OLLAMA_BASE_URL": "http://custom-ollama:11434"})
    @patch("httpx.Client")
    def test_custom_base_url(self, mock_client_class):
        """Test custom Ollama base URL configuration"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()
        assert provider.base_url == "http://custom-ollama:11434"

    @pytest.mark.asyncio
    @patch("httpx.Client")
    async def test_chat_success(self, mock_client_class):
        """Test successful chat completion with Ollama"""
        # Setup mock for availability check
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()

        # Mock the async HTTP client for chat
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client_instance = AsyncMock()
            mock_chat_response = MagicMock()
            mock_chat_response.status_code = 200
            mock_chat_response.json.return_value = {
                "message": {"content": "This is a response from Ollama"},
                "done": True,
                "done_reason": "stop",
                "prompt_eval_count": 50,
                "eval_count": 100,
            }
            mock_chat_response.raise_for_status = MagicMock()
            mock_async_client_instance.post = AsyncMock(return_value=mock_chat_response)
            mock_async_client_instance.__aenter__ = AsyncMock(return_value=mock_async_client_instance)
            mock_async_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_async_client_instance

            messages = [
                LLMMessage(role="system", content="You are a helpful assistant"),
                LLMMessage(role="user", content="Hello"),
            ]

            response = await provider.chat(messages)

            assert response.content == "This is a response from Ollama"
            assert response.provider == "Ollama Local"
            assert response.input_tokens == 50
            assert response.output_tokens == 100
            assert response.cost == 0.0  # Ollama is free

    @pytest.mark.asyncio
    @patch("httpx.Client")
    async def test_generate_success(self, mock_client_class):
        """Test successful text generation with Ollama"""
        # Setup mock for availability check
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()

        # Mock the async HTTP client for generate
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client_instance = AsyncMock()
            mock_gen_response = MagicMock()
            mock_gen_response.status_code = 200
            mock_gen_response.json.return_value = {
                "response": "Generated text from Ollama",
                "done": True,
                "prompt_eval_count": 30,
                "eval_count": 80,
            }
            mock_gen_response.raise_for_status = MagicMock()
            mock_async_client_instance.post = AsyncMock(return_value=mock_gen_response)
            mock_async_client_instance.__aenter__ = AsyncMock(return_value=mock_async_client_instance)
            mock_async_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_async_client_instance

            response = await provider.generate("Tell me about agriculture")

            assert response.content == "Generated text from Ollama"
            assert response.provider == "Ollama Local"
            assert response.input_tokens == 30
            assert response.output_tokens == 80

    @pytest.mark.asyncio
    @patch("httpx.Client")
    async def test_list_models(self, mock_client_class):
        """Test listing available Ollama models"""
        # Setup mock for availability check
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()

        # Mock the async HTTP client
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client_instance = AsyncMock()
            mock_list_response = MagicMock()
            mock_list_response.status_code = 200
            mock_list_response.json.return_value = {
                "models": [
                    {"name": "llama3.2", "size": 4000000000},
                    {"name": "mistral", "size": 5000000000},
                    {"name": "nomic-embed-text", "size": 500000000},
                ]
            }
            mock_list_response.raise_for_status = MagicMock()
            mock_async_client_instance.get = AsyncMock(return_value=mock_list_response)
            mock_async_client_instance.__aenter__ = AsyncMock(return_value=mock_async_client_instance)
            mock_async_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_async_client_instance

            models = await provider.list_models()

            assert len(models) == 3
            assert models[0]["name"] == "llama3.2"

    @pytest.mark.asyncio
    @patch("httpx.Client")
    async def test_pull_model_success(self, mock_client_class):
        """Test pulling a model from Ollama registry"""
        # Setup mock for availability check
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()

        # Mock the async HTTP client
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client_instance = AsyncMock()
            mock_pull_response = MagicMock()
            mock_pull_response.status_code = 200
            mock_pull_response.raise_for_status = MagicMock()
            mock_async_client_instance.post = AsyncMock(return_value=mock_pull_response)
            mock_async_client_instance.__aenter__ = AsyncMock(return_value=mock_async_client_instance)
            mock_async_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_async_client_instance

            result = await provider.pull_model("llama3.2")

            assert result is True

    @pytest.mark.asyncio
    @patch("httpx.Client")
    async def test_embeddings_success(self, mock_client_class):
        """Test generating embeddings with Ollama"""
        # Setup mock for availability check
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()

        # Mock the async HTTP client
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client_instance = AsyncMock()
            mock_embed_response = MagicMock()
            mock_embed_response.status_code = 200
            mock_embed_response.json.return_value = {
                "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dim vector
            }
            mock_embed_response.raise_for_status = MagicMock()
            mock_async_client_instance.post = AsyncMock(return_value=mock_embed_response)
            mock_async_client_instance.__aenter__ = AsyncMock(return_value=mock_async_client_instance)
            mock_async_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_async_client_instance

            embeddings = await provider.embeddings("Test text for embeddings")

            assert len(embeddings) == 1
            assert len(embeddings[0]) == 500

    @pytest.mark.asyncio
    @patch("httpx.Client")
    async def test_embeddings_batch(self, mock_client_class):
        """Test generating batch embeddings with Ollama"""
        # Setup mock for availability check
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()

        # Mock the async HTTP client
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client_instance = AsyncMock()
            mock_embed_response = MagicMock()
            mock_embed_response.status_code = 200
            mock_embed_response.json.return_value = {
                "embedding": [0.1, 0.2, 0.3] * 128  # 384-dim vector
            }
            mock_embed_response.raise_for_status = MagicMock()
            mock_async_client_instance.post = AsyncMock(return_value=mock_embed_response)
            mock_async_client_instance.__aenter__ = AsyncMock(return_value=mock_async_client_instance)
            mock_async_client_instance.__aexit__ = AsyncMock(return_value=None)
            mock_async_client.return_value = mock_async_client_instance

            texts = ["Text 1", "Text 2", "Text 3"]
            embeddings = await provider.embeddings(texts)

            assert len(embeddings) == 3
            # Each call should produce an embedding
            assert mock_async_client_instance.post.call_count == 3


class TestMultiLLMServiceWithOllama:
    """
    Test multi-provider LLM service with Ollama integration
    اختبارات خدمة نماذج اللغة متعددة المزودين مع تكامل Ollama
    """

    @patch("httpx.Client")
    def test_ollama_primary_initialization(self, mock_client_class):
        """Test service initializes with Ollama as primary"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        service = MultiLLMService(primary_provider="ollama")
        configured_providers = [p for p in service.providers if p.is_configured]
        if configured_providers:
            assert "Ollama" in configured_providers[0].name

    @patch.dict(
        "os.environ",
        {
            "ANTHROPIC_API_KEY": "test_key1",
            "OPENAI_API_KEY": "test_key2",
        },
    )
    @patch("httpx.Client")
    def test_ollama_in_available_providers(self, mock_client_class):
        """Test Ollama appears in available providers list"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        service = MultiLLMService()
        providers = service.get_available_providers()

        # Should now have 4 providers: Anthropic, OpenAI, Google, Ollama
        assert len(providers) == 4
        ollama_provider = next((p for p in providers if "Ollama" in p["name"]), None)
        assert ollama_provider is not None
        assert ollama_provider["type"] == "OllamaProvider"

    @pytest.mark.asyncio
    @patch("httpx.Client")
    async def test_fallback_to_ollama(self, mock_client_class):
        """Test fallback to Ollama when cloud providers fail"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            # Mock Anthropic to fail
            with patch("src.llm.multi_provider.AsyncAnthropic") as mock_anthropic:
                mock_anthropic_client = AsyncMock()
                mock_anthropic_client.messages.create = AsyncMock(side_effect=Exception("Anthropic API error"))
                mock_anthropic.return_value = mock_anthropic_client

                # Mock Ollama to succeed
                with patch("httpx.AsyncClient") as mock_async_client:
                    mock_async_client_instance = AsyncMock()
                    mock_chat_response = MagicMock()
                    mock_chat_response.status_code = 200
                    mock_chat_response.json.return_value = {
                        "message": {"content": "Ollama fallback response"},
                        "done": True,
                        "done_reason": "stop",
                        "prompt_eval_count": 50,
                        "eval_count": 100,
                    }
                    mock_chat_response.raise_for_status = MagicMock()
                    mock_async_client_instance.post = AsyncMock(return_value=mock_chat_response)
                    mock_async_client_instance.__aenter__ = AsyncMock(return_value=mock_async_client_instance)
                    mock_async_client_instance.__aexit__ = AsyncMock(return_value=None)
                    mock_async_client.return_value = mock_async_client_instance

                    service = MultiLLMService()
                    messages = [LLMMessage(role="user", content="Hello")]

                    result = await service.chat(messages)

                    # Should fallback to Ollama
                    assert result.success is True
                    assert result.provider == "Ollama Local"
                    assert "Anthropic" in result.failed_providers[0]
