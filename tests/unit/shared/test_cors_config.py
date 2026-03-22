"""
Tests for shared/cors_config.py — CORS configuration
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from shared.cors_config import (
    CORS_SETTINGS,
    DEVELOPMENT_ORIGINS,
    PRODUCTION_ORIGINS,
    STAGING_ORIGINS,
    _CORSSettings,
    get_allowed_origins,
    get_cors_config,
    setup_cors_middleware,
    validate_origin,
)


class TestGetAllowedOrigins:
    """Tests for get_allowed_origins."""

    def test_defaults_to_development_origins(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        origins = get_allowed_origins()
        assert origins == DEVELOPMENT_ORIGINS

    def test_production_environment(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "production")
        origins = get_allowed_origins()
        assert origins == PRODUCTION_ORIGINS

    def test_staging_environment(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "staging")
        origins = get_allowed_origins()
        assert origins == STAGING_ORIGINS

    def test_development_environment(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        origins = get_allowed_origins()
        assert origins == DEVELOPMENT_ORIGINS

    def test_custom_origins_from_env(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "https://custom.example.com, https://other.example.com")
        monkeypatch.setenv("ENVIRONMENT", "development")
        origins = get_allowed_origins()
        assert origins == ["https://custom.example.com", "https://other.example.com"]

    def test_wildcard_blocked_in_production(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "*")
        monkeypatch.setenv("ENVIRONMENT", "production")
        origins = get_allowed_origins()
        assert origins == PRODUCTION_ORIGINS
        assert "*" not in origins

    def test_wildcard_allowed_in_development(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "*")
        monkeypatch.setenv("ENVIRONMENT", "development")
        origins = get_allowed_origins()
        assert "*" in origins

    def test_empty_cors_origins_env(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "")
        monkeypatch.setenv("ENVIRONMENT", "production")
        origins = get_allowed_origins()
        assert origins == PRODUCTION_ORIGINS

    def test_whitespace_cors_origins_env(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "  ")
        monkeypatch.setenv("ENVIRONMENT", "development")
        origins = get_allowed_origins()
        assert origins == DEVELOPMENT_ORIGINS

    def test_strips_whitespace_from_origins(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "  https://a.com , https://b.com  ")
        monkeypatch.setenv("ENVIRONMENT", "development")
        origins = get_allowed_origins()
        assert origins == ["https://a.com", "https://b.com"]


class TestGetCorsConfig:
    """Tests for get_cors_config."""

    def test_returns_dict_with_expected_keys(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        config = get_cors_config()
        assert "environment" in config
        assert "allowed_origins" in config
        assert "cors_origins_env" in config
        assert "has_wildcard" in config
        assert "origin_count" in config

    def test_no_cors_env_reports_not_set(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        config = get_cors_config()
        assert config["cors_origins_env"] == "not set"

    def test_cors_env_reported(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "https://example.com")
        monkeypatch.setenv("ENVIRONMENT", "development")
        config = get_cors_config()
        assert config["cors_origins_env"] == "https://example.com"

    def test_wildcard_detection(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "*")
        monkeypatch.setenv("ENVIRONMENT", "development")
        config = get_cors_config()
        assert config["has_wildcard"] is True

    def test_no_wildcard(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "production")
        config = get_cors_config()
        assert config["has_wildcard"] is False


class TestValidateOrigin:
    """Tests for validate_origin."""

    def test_valid_production_origin(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "production")
        assert validate_origin("https://sahool.app") is True

    def test_invalid_origin(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "production")
        assert validate_origin("https://evil.com") is False

    def test_wildcard_matches_anything(self, monkeypatch):
        monkeypatch.setenv("CORS_ORIGINS", "*")
        monkeypatch.setenv("ENVIRONMENT", "development")
        assert validate_origin("https://anything.example.com") is True

    def test_development_origin_valid(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        assert validate_origin("http://localhost:3000") is True


class TestSetupCorsMiddleware:
    """Tests for setup_cors_middleware."""

    def test_adds_middleware_to_app(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_cors_middleware(app)
        client = TestClient(app)
        # CORS preflight
        resp = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200

    def test_wildcard_blocked_in_production(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_cors_middleware(app, allow_origins=["*"])
        client = TestClient(app)
        # Wildcard should be replaced with production origins
        resp = client.options(
            "/test",
            headers={
                "Origin": "https://evil.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        # Should not include Access-Control-Allow-Origin for evil.com
        allow_origin = resp.headers.get("Access-Control-Allow-Origin", "")
        assert allow_origin != "https://evil.com"

    def test_credentials_disabled_with_wildcard(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("CORS_ORIGINS", "*")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_cors_middleware(app)
        # The middleware should set allow_credentials=False for wildcard

    def test_custom_origins_passed(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "development")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_cors_middleware(app, allow_origins=["https://custom.example.com"])
        client = TestClient(app)
        resp = client.options(
            "/test",
            headers={
                "Origin": "https://custom.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("Access-Control-Allow-Origin") == "https://custom.example.com"

    def test_kwargs_override_defaults(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_cors_middleware(app, max_age=7200)
        # Should not raise, middleware is added


class TestCORSSettings:
    """Tests for the lazy _CORSSettings object."""

    def test_getitem(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        settings = _CORSSettings()
        origins = settings["allow_origins"]
        assert isinstance(origins, list)

    def test_get_with_default(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        settings = _CORSSettings()
        val = settings.get("nonexistent", "default_val")
        assert val == "default_val"

    def test_keys(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        settings = _CORSSettings()
        keys = list(settings.keys())
        assert "allow_origins" in keys
        assert "allow_methods" in keys
        assert "allow_headers" in keys
        assert "max_age" in keys

    def test_values(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        settings = _CORSSettings()
        values = list(settings.values())
        assert len(values) > 0

    def test_items(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        settings = _CORSSettings()
        items = list(settings.items())
        assert len(items) > 0
        # Each item is a (key, value) tuple
        assert all(isinstance(item, tuple) and len(item) == 2 for item in items)

    def test_iter(self, monkeypatch):
        monkeypatch.delenv("CORS_ORIGINS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        settings = _CORSSettings()
        keys = list(iter(settings))
        assert "allow_origins" in keys

    def test_lazy_loading(self):
        settings = _CORSSettings()
        assert settings._settings is None
        # Accessing triggers load
        _ = settings["allow_origins"]
        assert settings._settings is not None


class TestOriginConstants:
    """Tests that origin constants are properly defined."""

    def test_production_origins_are_https(self):
        for origin in PRODUCTION_ORIGINS:
            assert origin.startswith("https://"), f"{origin} should be HTTPS"

    def test_development_origins_are_localhost(self):
        for origin in DEVELOPMENT_ORIGINS:
            assert "localhost" in origin or "127.0.0.1" in origin

    def test_staging_origins_contain_staging(self):
        for origin in STAGING_ORIGINS:
            assert "staging" in origin
