"""
Test Security Headers Middleware
اختبار middleware رؤوس الأمان

Tests to verify that security headers are correctly applied to all responses.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from shared.middleware.security_headers import (
    SecurityHeadersMiddleware,
    get_security_headers_config,
    setup_security_headers,
)


@pytest.fixture
def app():
    """Create a test FastAPI application"""
    app = FastAPI()

    @app.get("/test")
    def test_endpoint():
        return {"message": "test"}

    return app


@pytest.fixture
def client_with_headers(app):
    """Create a test client with security headers middleware"""
    setup_security_headers(app)
    return TestClient(app)


def test_security_headers_applied(client_with_headers):
    """Test that all security headers are applied to responses"""
    response = client_with_headers.get("/test")

    # Check that the response is successful
    assert response.status_code == 200

    # Essential security headers
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "DENY"

    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"

    assert "Referrer-Policy" in response.headers
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    assert "X-XSS-Protection" in response.headers
    assert response.headers["X-XSS-Protection"] == "1; mode=block"

    assert "X-Powered-By" in response.headers
    assert response.headers["X-Powered-By"] == "SAHOOL"


def test_csp_header_applied(client_with_headers):
    """Test that Content-Security-Policy is applied"""
    response = client_with_headers.get("/test")

    assert "Content-Security-Policy" in response.headers
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_permissions_policy_applied(client_with_headers):
    """Test that Permissions-Policy is applied"""
    response = client_with_headers.get("/test")

    assert "Permissions-Policy" in response.headers
    assert "geolocation=()" in response.headers["Permissions-Policy"]
    assert "microphone=()" in response.headers["Permissions-Policy"]
    assert "camera=()" in response.headers["Permissions-Policy"]


def test_cors_policies_applied(client_with_headers):
    """Test that Cross-Origin policies are applied"""
    response = client_with_headers.get("/test")

    assert "Cross-Origin-Resource-Policy" in response.headers
    assert response.headers["Cross-Origin-Resource-Policy"] == "same-origin"

    assert "Cross-Origin-Opener-Policy" in response.headers
    assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"

    assert "Cross-Origin-Embedder-Policy" in response.headers
    assert response.headers["Cross-Origin-Embedder-Policy"] == "require-corp"


def test_custom_csp_policy(app):
    """Test that custom CSP policy can be set"""
    custom_csp = "default-src 'none'; script-src 'self'"
    setup_security_headers(app, csp_policy=custom_csp)

    client = TestClient(app)
    response = client.get("/test")

    assert response.headers["Content-Security-Policy"] == custom_csp


def test_disable_csp(app, monkeypatch):
    """Test that CSP can be disabled"""
    monkeypatch.setenv("ENABLE_CSP", "false")

    app_no_csp = FastAPI()

    @app_no_csp.get("/test")
    def test_endpoint():
        return {"message": "test"}

    setup_security_headers(app_no_csp)
    client = TestClient(app_no_csp)
    response = client.get("/test")

    # CSP should not be present
    assert "Content-Security-Policy" not in response.headers
    # But other headers should still be present
    assert "X-Frame-Options" in response.headers


def test_hsts_not_in_development(app, monkeypatch):
    """Test that HSTS is not enabled in development"""
    monkeypatch.setenv("ENVIRONMENT", "development")

    app_dev = FastAPI()

    @app_dev.get("/test")
    def test_endpoint():
        return {"message": "test"}

    setup_security_headers(app_dev)
    client = TestClient(app_dev)
    response = client.get("/test")

    # HSTS should not be present in development
    assert "Strict-Transport-Security" not in response.headers


def test_hsts_in_production(app, monkeypatch):
    """Test that HSTS is enabled in production"""
    monkeypatch.setenv("ENVIRONMENT", "production")

    app_prod = FastAPI()

    @app_prod.get("/test")
    def test_endpoint():
        return {"message": "test"}

    setup_security_headers(app_prod)
    client = TestClient(app_prod)
    response = client.get("/test")

    # HSTS should be present in production
    assert "Strict-Transport-Security" in response.headers
    assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
    assert "includeSubDomains" in response.headers["Strict-Transport-Security"]


def test_get_security_headers_config(monkeypatch):
    """Test that configuration can be retrieved"""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("ENABLE_HSTS", "true")
    monkeypatch.setenv("ENABLE_CSP", "true")

    config = get_security_headers_config()

    assert config["environment"] == "production"
    assert config["hsts_enabled"] == "true"
    assert config["csp_enabled"] == "true"


def test_middleware_class_directly(app):
    """Test using the middleware class directly"""
    app.add_middleware(SecurityHeadersMiddleware)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert "X-Frame-Options" in response.headers
    assert "X-Content-Type-Options" in response.headers


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
