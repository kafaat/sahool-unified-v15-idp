"""
Tests for Copilot API Configuration (core/config.py)
"""

import pytest

pytestmark = [pytest.mark.unit]
class TestSettings:
    def test_default_service_name(self):
        from src.core.config import Settings

        s = Settings()
        assert s.service_name == "copilot-api"

    def test_default_port(self):
        from src.core.config import Settings

        s = Settings()
        assert s.port == 8088

    def test_default_copilot_mode_is_offline(self):
        from src.core.config import Settings

        s = Settings()
        assert s.copilot_mode == "offline"

    def test_default_jwt_algorithm(self):
        from src.core.config import Settings

        s = Settings()
        assert s.jwt_algorithm == "HS256"

    def test_cors_origins_list(self):
        from src.core.config import Settings

        s = Settings(cors_origins="http://a.com , http://b.com")
        origins = s.cors_origins_list
        assert len(origins) == 2
        assert "http://a.com" in origins
        assert "http://b.com" in origins

    def test_cors_origins_list_empty_strings_filtered(self):
        from src.core.config import Settings

        s = Settings(cors_origins="http://a.com,,")
        origins = s.cors_origins_list
        assert len(origins) == 1

    def test_is_production_true(self):
        from src.core.config import Settings

        s = Settings(environment="production")
        assert s.is_production is True

    def test_is_production_false(self):
        from src.core.config import Settings

        s = Settings(environment="development")
        assert s.is_production is False

    def test_is_production_case_insensitive(self):
        from src.core.config import Settings

        s = Settings(environment="Production")
        assert s.is_production is True

    def test_is_offline_mode_default(self):
        from src.core.config import Settings

        s = Settings()
        assert s.is_offline_mode is True

    def test_is_offline_mode_when_external_disabled(self):
        from src.core.config import Settings

        s = Settings(copilot_mode="online", enable_external=False)
        assert s.is_offline_mode is True

    def test_is_not_offline_when_online_and_external_enabled(self):
        from src.core.config import Settings

        s = Settings(copilot_mode="online", enable_external=True)
        assert s.is_offline_mode is False

    def test_default_embedding_provider(self):
        from src.core.config import Settings

        s = Settings()
        assert s.embedding_provider == "sentence_transformers"

    def test_default_ollama_model(self):
        from src.core.config import Settings

        s = Settings()
        assert s.ollama_model == "codellama:7b"

    def test_default_qdrant_settings(self):
        from src.core.config import Settings

        s = Settings()
        assert s.qdrant_host == "localhost"
        assert s.qdrant_port == 6333
        assert s.use_qdrant is True
class TestServiceVersion:
    def test_version_constant(self):
        from src.core.config import SERVICE_VERSION

        assert SERVICE_VERSION == "16.0.0"

    def test_settings_version_matches(self):
        from src.core.config import SERVICE_VERSION, Settings

        s = Settings()
        assert s.service_version == SERVICE_VERSION
class TestGetSettings:
    def test_get_settings_returns_settings(self):
        from src.core.config import Settings, get_settings

        get_settings.cache_clear()
        s = get_settings()
        assert isinstance(s, Settings)

    def test_get_settings_cached(self):
        from src.core.config import get_settings

        get_settings.cache_clear()
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2
        get_settings.cache_clear()
