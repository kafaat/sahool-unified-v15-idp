"""
Tests for shared/middleware/security_headers.py — Security headers middleware
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from shared.middleware.security_headers import (
    SecurityHeadersMiddleware,
    get_security_headers_config,
    setup_security_headers,
)


def _make_app(**middleware_kwargs) -> FastAPI:
    """Create a test FastAPI app with SecurityHeadersMiddleware."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware, **middleware_kwargs)

    @app.get("/test")
    def endpoint():
        return {"ok": True}

    return app


class TestSecurityHeadersMiddleware:
    """Test security headers are set correctly."""

    def test_essential_headers_present(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/test")
        assert resp.status_code == 200
        assert resp.headers["X-Frame-Options"] == "DENY"
        assert resp.headers["X-Content-Type-Options"] == "nosniff"
        assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert resp.headers["X-XSS-Protection"] == "1; mode=block"
        assert resp.headers["X-Powered-By"] == "SAHOOL"
        assert resp.headers["Cross-Origin-Resource-Policy"] == "same-origin"
        assert resp.headers["Cross-Origin-Opener-Policy"] == "same-origin"
        assert resp.headers["Cross-Origin-Embedder-Policy"] == "require-corp"

    def test_permissions_policy_present(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/test")
        pp = resp.headers["Permissions-Policy"]
        assert "geolocation=()" in pp
        assert "camera=()" in pp
        assert "microphone=()" in pp

    def test_csp_enabled_by_default(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/test")
        csp = resp.headers.get("Content-Security-Policy")
        assert csp is not None
        assert "default-src 'self'" in csp

    def test_csp_disabled(self):
        app = _make_app(enable_csp=False)
        client = TestClient(app)
        resp = client.get("/test")
        assert "Content-Security-Policy" not in resp.headers

    def test_custom_csp_policy(self):
        custom = "default-src 'none'"
        app = _make_app(csp_policy=custom)
        client = TestClient(app)
        resp = client.get("/test")
        assert resp.headers["Content-Security-Policy"] == custom

    def test_hsts_not_set_in_development(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "development")
        app = _make_app(enable_hsts=True)
        client = TestClient(app)
        resp = client.get("/test")
        assert "Strict-Transport-Security" not in resp.headers

    def test_hsts_set_in_production(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        app = _make_app(enable_hsts=True)
        client = TestClient(app)
        resp = client.get("/test")
        hsts = resp.headers.get("Strict-Transport-Security")
        assert hsts is not None
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts

    def test_hsts_disabled_explicitly(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        app = _make_app(enable_hsts=False)
        client = TestClient(app)
        resp = client.get("/test")
        assert "Strict-Transport-Security" not in resp.headers


class TestSetupSecurityHeaders:
    """Test the setup_security_headers helper function."""

    def test_setup_adds_middleware(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "development")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_security_headers(app)
        client = TestClient(app)
        resp = client.get("/test")
        assert resp.headers["X-Frame-Options"] == "DENY"

    def test_setup_hsts_auto_detect_production(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.delenv("ENABLE_HSTS", raising=False)
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_security_headers(app)
        client = TestClient(app)
        resp = client.get("/test")
        assert "Strict-Transport-Security" in resp.headers

    def test_setup_hsts_env_override_true(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("ENABLE_HSTS", "true")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_security_headers(app)
        client = TestClient(app)
        resp = client.get("/test")
        assert "Strict-Transport-Security" in resp.headers

    def test_setup_hsts_env_override_false(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("ENABLE_HSTS", "false")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_security_headers(app)
        client = TestClient(app)
        resp = client.get("/test")
        assert "Strict-Transport-Security" not in resp.headers

    def test_setup_csp_disabled_via_env(self, monkeypatch):
        monkeypatch.setenv("ENABLE_CSP", "false")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_security_headers(app)
        client = TestClient(app)
        resp = client.get("/test")
        assert "Content-Security-Policy" not in resp.headers


class TestGetSecurityHeadersConfig:
    """Test the config introspection function."""

    def test_returns_dict(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "staging")
        monkeypatch.delenv("ENABLE_HSTS", raising=False)
        monkeypatch.delenv("ENABLE_CSP", raising=False)
        monkeypatch.delenv("CSP_POLICY", raising=False)

        config = get_security_headers_config()
        assert config["environment"] == "staging"
        assert config["hsts_enabled"] == "auto"
        assert config["csp_enabled"] == "true"
        assert config["csp_policy"] == "default"

    def test_returns_custom_csp_policy_from_env(self, monkeypatch):
        monkeypatch.setenv("CSP_POLICY", "default-src 'none'")
        config = get_security_headers_config()
        assert config["csp_policy"] == "default-src 'none'"

    def test_returns_env_overrides(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("ENABLE_HSTS", "true")
        monkeypatch.setenv("ENABLE_CSP", "false")
        config = get_security_headers_config()
        assert config["environment"] == "production"
        assert config["hsts_enabled"] == "true"
        assert config["csp_enabled"] == "false"


class TestSetupSecurityHeadersEdgeCases:
    """Additional edge cases for setup_security_headers."""

    def test_setup_csp_policy_from_env(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.delenv("ENABLE_CSP", raising=False)
        monkeypatch.setenv("CSP_POLICY", "default-src 'none'")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_security_headers(app)
        client = TestClient(app)
        resp = client.get("/test")
        assert resp.headers["Content-Security-Policy"] == "default-src 'none'"

    def test_setup_hsts_env_yes(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("ENABLE_HSTS", "yes")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_security_headers(app)
        client = TestClient(app)
        resp = client.get("/test")
        assert "Strict-Transport-Security" in resp.headers

    def test_setup_hsts_env_no(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("ENABLE_HSTS", "no")
        app = FastAPI()

        @app.get("/test")
        def endpoint():
            return {"ok": True}

        setup_security_headers(app)
        client = TestClient(app)
        resp = client.get("/test")
        assert "Strict-Transport-Security" not in resp.headers

    def test_default_csp_contains_all_directives(self):
        """Verify all expected CSP directives in default policy."""
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/test")
        csp = resp.headers["Content-Security-Policy"]
        assert "script-src 'self'" in csp
        assert "style-src 'self'" in csp
        assert "frame-ancestors 'none'" in csp
        assert "object-src 'none'" in csp
        assert "upgrade-insecure-requests" in csp
