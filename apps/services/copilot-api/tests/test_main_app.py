"""
Tests for Main Application (main.py) - create_app and helpers
"""

import os
from unittest.mock import MagicMock, patch

import pytest

pytestmark = [pytest.mark.unit]


class TestGetAvailableProviders:
    def test_always_includes_ollama(self):
        from src.core.config import Settings
        from src.main import _get_available_providers

        settings = Settings()
        providers = _get_available_providers(settings)
        ollama = [p for p in providers if p["name"] == "Ollama"]
        assert len(ollama) == 1
        assert ollama[0]["type"] == "local"
        assert ollama[0]["priority"] == 1

    def test_claude_included_when_api_key_set(self):
        from src.core.config import Settings
        from src.main import _get_available_providers

        settings = Settings(enable_external=True)
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            providers = _get_available_providers(settings)
            claude = [p for p in providers if p["name"] == "Claude"]
            assert len(claude) == 1
            assert claude[0]["available"] is True

    def test_claude_not_included_without_api_key(self):
        from src.core.config import Settings
        from src.main import _get_available_providers

        settings = Settings()
        with patch.dict(os.environ, {}, clear=True):
            # Ensure ANTHROPIC_API_KEY is not set
            os.environ.pop("ANTHROPIC_API_KEY", None)
            providers = _get_available_providers(settings)
            claude = [p for p in providers if p["name"] == "Claude"]
            assert len(claude) == 0

    def test_openai_included_when_configured(self):
        from src.core.config import Settings
        from src.main import _get_available_providers

        settings = Settings(
            enable_external=True,
            external_llm_api_key="test-key",
            external_llm_base_url="https://api.openai.com",
        )
        providers = _get_available_providers(settings)
        openai = [p for p in providers if p["name"] == "OpenAI"]
        assert len(openai) == 1

    def test_gemini_included_when_api_key_set(self):
        from src.core.config import Settings
        from src.main import _get_available_providers

        settings = Settings(enable_external=True)
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            providers = _get_available_providers(settings)
            gemini = [p for p in providers if p["name"] == "Gemini"]
            assert len(gemini) == 1

    def test_deepseek_included_when_api_key_set(self):
        from src.core.config import Settings
        from src.main import _get_available_providers

        settings = Settings(enable_external=True)
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
            providers = _get_available_providers(settings)
            ds = [p for p in providers if p["name"] == "DeepSeek"]
            assert len(ds) == 1


class TestCreateApp:
    def test_app_created_successfully(self):
        from src.core.config import get_settings

        get_settings.cache_clear()
        with patch("src.main.get_settings") as mock_gs:
            mock_settings = MagicMock()
            mock_settings.cors_origins_list = ["http://localhost:3000"]
            mock_settings.debug = False
            mock_settings.copilot_mode = "offline"
            mock_settings.environment = "test"
            mock_gs.return_value = mock_settings

            from src.main import create_app

            app = create_app()
            assert app is not None
            assert app.title == "SAHOOL Copilot API"

        get_settings.cache_clear()
