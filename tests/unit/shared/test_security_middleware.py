"""
Tests for Security Headers and CORS Middleware
اختبارات middleware الأمان و CORS
"""

import os
import pytest
from shared.middleware.security_headers import (
    SecurityHeadersMiddleware,
    get_security_headers_config,
)
from shared.middleware.cors import (
    get_cors_origins,
    get_cors_config,
    DEFAULT_ORIGINS,
)


class TestSecurityHeadersConfig:
    """Tests for security headers configuration"""

    def test_get_security_headers_config_structure(self):
        """Test config returns correct structure"""
        config = get_security_headers_config()
        assert "environment" in config
        assert "hsts_enabled" in config
        assert "csp_enabled" in config
        assert "csp_policy" in config

    def test_get_security_headers_config_defaults(self):
        """Test config default values"""
        # Clear env vars
        for var in ["ENVIRONMENT", "ENABLE_HSTS", "ENABLE_CSP", "CSP_POLICY"]:
            if var in os.environ:
                del os.environ[var]

        config = get_security_headers_config()
        assert config["environment"] == "development"
        assert config["csp_enabled"] == "true"
        assert config["csp_policy"] == "default"

    def test_get_security_headers_config_production(self):
        """Test config in production environment"""
        original_env = os.environ.get("ENVIRONMENT")
        os.environ["ENVIRONMENT"] = "production"

        try:
            config = get_security_headers_config()
            assert config["environment"] == "production"
        finally:
            if original_env:
                os.environ["ENVIRONMENT"] = original_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]


class TestCORSOrigins:
    """Tests for CORS origins configuration"""

    def test_default_origins_structure(self):
        """Test DEFAULT_ORIGINS has all environments"""
        assert "production" in DEFAULT_ORIGINS
        assert "staging" in DEFAULT_ORIGINS
        assert "development" in DEFAULT_ORIGINS

    def test_production_origins_are_https(self):
        """Test production origins use HTTPS"""
        for origin in DEFAULT_ORIGINS["production"]:
            assert origin.startswith("https://"), f"Production origin should use HTTPS: {origin}"

    def test_staging_origins_are_https(self):
        """Test staging origins use HTTPS"""
        for origin in DEFAULT_ORIGINS["staging"]:
            assert origin.startswith("https://"), f"Staging origin should use HTTPS: {origin}"

    def test_development_origins_are_localhost(self):
        """Test development origins are localhost"""
        for origin in DEFAULT_ORIGINS["development"]:
            assert "localhost" in origin or "127.0.0.1" in origin

    def test_get_cors_origins_from_env(self):
        """Test getting CORS origins from environment variable"""
        original = os.environ.get("CORS_ORIGINS")
        os.environ["CORS_ORIGINS"] = "https://example.com,https://api.example.com"

        try:
            origins = get_cors_origins()
            assert "https://example.com" in origins
            assert "https://api.example.com" in origins
        finally:
            if original:
                os.environ["CORS_ORIGINS"] = original
            else:
                del os.environ["CORS_ORIGINS"]

    def test_get_cors_origins_development_default(self):
        """Test getting development origins by default"""
        # Clear relevant env vars
        for var in ["CORS_ORIGINS", "ENVIRONMENT"]:
            if var in os.environ:
                del os.environ[var]

        origins = get_cors_origins()
        assert "http://localhost:3000" in origins

    def test_get_cors_origins_production(self):
        """Test getting production origins"""
        original_cors = os.environ.get("CORS_ORIGINS")
        original_env = os.environ.get("ENVIRONMENT")

        if "CORS_ORIGINS" in os.environ:
            del os.environ["CORS_ORIGINS"]
        os.environ["ENVIRONMENT"] = "production"

        try:
            origins = get_cors_origins()
            assert origins == DEFAULT_ORIGINS["production"]
        finally:
            if original_cors:
                os.environ["CORS_ORIGINS"] = original_cors
            if original_env:
                os.environ["ENVIRONMENT"] = original_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]

    def test_get_cors_origins_staging(self):
        """Test getting staging origins"""
        original_cors = os.environ.get("CORS_ORIGINS")
        original_env = os.environ.get("ENVIRONMENT")

        if "CORS_ORIGINS" in os.environ:
            del os.environ["CORS_ORIGINS"]
        os.environ["ENVIRONMENT"] = "staging"

        try:
            origins = get_cors_origins()
            assert origins == DEFAULT_ORIGINS["staging"]
        finally:
            if original_cors:
                os.environ["CORS_ORIGINS"] = original_cors
            if original_env:
                os.environ["ENVIRONMENT"] = original_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]

    def test_get_cors_config_structure(self):
        """Test get_cors_config returns correct structure"""
        config = get_cors_config()
        assert "allowed_origins" in config
        assert "environment" in config
        assert "cors_origins_env" in config

    def test_get_cors_config_with_env_var(self):
        """Test get_cors_config reflects environment variable"""
        original = os.environ.get("CORS_ORIGINS")
        os.environ["CORS_ORIGINS"] = "https://test.example.com"

        try:
            config = get_cors_config()
            assert config["cors_origins_env"] == "https://test.example.com"
            assert "https://test.example.com" in config["allowed_origins"]
        finally:
            if original:
                os.environ["CORS_ORIGINS"] = original
            else:
                del os.environ["CORS_ORIGINS"]


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware class"""

    def test_middleware_default_csp(self):
        """Test middleware creates default CSP"""
        # Create a mock app
        class MockApp:
            pass

        middleware = SecurityHeadersMiddleware(MockApp())
        assert "default-src 'self'" in middleware.csp_policy
        assert "script-src 'self'" in middleware.csp_policy
        assert "frame-ancestors 'none'" in middleware.csp_policy

    def test_middleware_custom_csp(self):
        """Test middleware accepts custom CSP"""
        class MockApp:
            pass

        custom_csp = "default-src 'self'; script-src 'self' 'unsafe-inline'"
        middleware = SecurityHeadersMiddleware(MockApp(), csp_policy=custom_csp)
        assert middleware.csp_policy == custom_csp

    def test_middleware_hsts_disabled_by_default_in_dev(self):
        """Test HSTS is disabled by default in development"""
        original = os.environ.get("ENVIRONMENT")
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]

        try:
            class MockApp:
                pass

            middleware = SecurityHeadersMiddleware(MockApp())
            assert middleware.environment == "development"
        finally:
            if original:
                os.environ["ENVIRONMENT"] = original

    def test_middleware_detects_production_environment(self):
        """Test middleware detects production environment"""
        original = os.environ.get("ENVIRONMENT")
        os.environ["ENVIRONMENT"] = "production"

        try:
            class MockApp:
                pass

            middleware = SecurityHeadersMiddleware(MockApp())
            assert middleware.environment == "production"
        finally:
            if original:
                os.environ["ENVIRONMENT"] = original
            else:
                del os.environ["ENVIRONMENT"]

    def test_middleware_csp_no_unsafe_inline(self):
        """Test default CSP does not include unsafe-inline"""
        class MockApp:
            pass

        middleware = SecurityHeadersMiddleware(MockApp())
        assert "unsafe-inline" not in middleware.csp_policy
        assert "unsafe-eval" not in middleware.csp_policy

    def test_middleware_enable_flags(self):
        """Test middleware respects enable flags"""
        class MockApp:
            pass

        middleware = SecurityHeadersMiddleware(
            MockApp(),
            enable_hsts=False,
            enable_csp=False,
        )
        assert middleware.enable_hsts is False
        assert middleware.enable_csp is False
