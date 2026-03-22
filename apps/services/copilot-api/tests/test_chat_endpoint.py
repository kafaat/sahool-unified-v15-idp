"""
Tests for Chat Endpoint helpers (api/v1/chat.py)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = [pytest.mark.unit]


class TestDetectLanguage:
    def test_english_text(self):
        from src.api.v1.chat import _detect_language

        assert _detect_language("What is the weather today?") == "en"

    def test_arabic_text(self):
        from src.api.v1.chat import _detect_language

        assert _detect_language("ما هو الطقس اليوم؟") == "ar"

    def test_mixed_text_mostly_arabic(self):
        from src.api.v1.chat import _detect_language

        assert _detect_language("مرحبا hello مساء الخير كيف حالك") == "ar"

    def test_mixed_text_mostly_english(self):
        from src.api.v1.chat import _detect_language

        assert _detect_language("Hello world test مرحبا") == "en"

    def test_empty_text(self):
        from src.api.v1.chat import _detect_language

        assert _detect_language("") == "en"


class TestBuildSystemPrompt:
    def test_base_prompt_included(self):
        from src.api.v1.chat import _build_system_prompt

        prompt = _build_system_prompt(rag_context="", agent_type="general", language="en")
        assert "SAHOOL" in prompt

    def test_agent_instructions_included(self):
        from src.api.v1.chat import _build_system_prompt

        prompt = _build_system_prompt(rag_context="", agent_type="code_fix", language="en")
        assert "code analysis" in prompt.lower() or "bug" in prompt.lower()

    def test_rag_context_included(self):
        from src.api.v1.chat import _build_system_prompt

        prompt = _build_system_prompt(
            rag_context="Wheat needs 25mm irrigation during tillering.",
            agent_type="general",
            language="en",
        )
        assert "Wheat needs 25mm irrigation" in prompt
        assert "knowledge base context" in prompt.lower()

    def test_no_rag_context_section_when_empty(self):
        from src.api.v1.chat import _build_system_prompt

        prompt = _build_system_prompt(rag_context="", agent_type="general", language="en")
        assert "knowledge base context" not in prompt.lower()

    def test_all_agent_types_have_instructions(self):
        from src.api.v1.chat import _build_system_prompt

        for agent_type in ("code_fix", "code_review", "field_advisor", "weather_advisor", "irrigation_advisor", "general"):
            prompt = _build_system_prompt(rag_context="", agent_type=agent_type, language="en")
            assert len(prompt) > 100  # Non-trivial prompt


class TestGenerateResponse:
    @pytest.mark.asyncio
    async def test_fallback_response_english(self):
        """When both Ollama and external LLM fail, returns fallback."""
        from src.api.v1.chat import _generate_response
        from src.models.schemas import ChatMessage, MessageRole

        mock_settings = MagicMock()
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_model = "codellama:7b"
        mock_settings.enable_external = False
        mock_settings.external_llm_api_key = None

        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("connection refused")

        messages = [ChatMessage(role=MessageRole.USER, content="Hello")]

        result = await _generate_response(
            messages=messages,
            system_prompt="test",
            settings=mock_settings,
            http_client=mock_client,
        )
        assert "SAHOOL" in result
        assert "Ollama" in result

    @pytest.mark.asyncio
    async def test_fallback_response_arabic(self):
        """When LLMs fail and query is Arabic, returns Arabic fallback."""
        from src.api.v1.chat import _generate_response
        from src.models.schemas import ChatMessage, MessageRole

        mock_settings = MagicMock()
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_model = "test"
        mock_settings.enable_external = False
        mock_settings.external_llm_api_key = None

        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("err")

        messages = [ChatMessage(role=MessageRole.USER, content="مرحبا كيف حالك اليوم يا صديقي")]

        result = await _generate_response(
            messages=messages,
            system_prompt="test",
            settings=mock_settings,
            http_client=mock_client,
        )
        assert "SAHOOL" in result
        assert "Ollama" in result

    @pytest.mark.asyncio
    async def test_ollama_success(self):
        """When Ollama returns 200, uses its response."""
        from src.api.v1.chat import _generate_response
        from src.models.schemas import ChatMessage, MessageRole

        mock_settings = MagicMock()
        mock_settings.ollama_base_url = "http://localhost:11434"
        mock_settings.ollama_model = "codellama:7b"
        mock_settings.enable_external = False

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": {"content": "Here is the answer."}}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        messages = [ChatMessage(role=MessageRole.USER, content="Hello")]

        result = await _generate_response(
            messages=messages,
            system_prompt="test",
            settings=mock_settings,
            http_client=mock_client,
        )
        assert result == "Here is the answer."


class TestGetHttpClient:
    def test_raises_when_not_initialized(self):
        from src.api.v1.chat import _get_http_client

        mock_request = MagicMock()
        mock_request.app.state = MagicMock(spec=[])  # No http_client attribute

        with pytest.raises(RuntimeError, match="http_client not initialized"):
            _get_http_client(mock_request)

    def test_returns_client_when_present(self):
        from src.api.v1.chat import _get_http_client

        mock_client = MagicMock()
        mock_request = MagicMock()
        mock_request.app.state.http_client = mock_client

        result = _get_http_client(mock_request)
        assert result is mock_client
