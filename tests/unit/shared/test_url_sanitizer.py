"""
Tests for URL Credential Sanitization in Logging
اختبارات تنظيف بيانات الاعتماد من عناوين URL في السجلات

Ensures credentials are never logged in connection URLs.
"""

import pytest

from shared.logging_config import (
    correlation_id_var,
    get_correlation_id,
    sanitize_url,
    sanitize_urls,
    set_correlation_id,
    set_tenant_id,
    set_user_id,
    tenant_id_var,
    user_id_var,
)

# ═══════════════════════════════════════════════════════════════════════════════
# URL Sanitization Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSanitizeUrl:
    """Test URL credential masking."""

    def test_postgres_url_masked(self):
        """PostgreSQL credentials are masked."""
        url = "postgresql://sahool:secret_password@pgbouncer:6432/sahool"
        result = sanitize_url(url)
        assert "secret_password" not in result
        assert "***@" in result
        assert "pgbouncer:6432/sahool" in result

    def test_nats_url_masked(self):
        """NATS credentials are masked."""
        url = "nats://user:password@nats:4222"
        result = sanitize_url(url)
        assert "password" not in result
        assert "***@nats:4222" in result

    def test_redis_url_masked(self):
        """Redis password-only auth is masked."""
        url = "redis://:mypassword@redis:6379/0"
        result = sanitize_url(url)
        assert "mypassword" not in result
        assert "***@redis:6379/0" in result

    def test_url_without_credentials_unchanged(self):
        """URLs without credentials are not modified."""
        url = "http://localhost:8080/api/v1/health"
        result = sanitize_url(url)
        assert result == url

    def test_non_string_returns_str(self):
        """Non-string input returns str representation."""
        result = sanitize_url(123)
        assert result == "123"

    def test_empty_string(self):
        """Empty string returns empty."""
        assert sanitize_url("") == ""

    def test_complex_password_masked(self):
        """Complex passwords with special chars are masked."""
        url = "postgresql://admin:p%40ss!w0rd%23%26@db.example.com:5432/db"
        result = sanitize_url(url)
        assert result == "postgresql://***@db.example.com:5432/db"
        assert "admin" not in result
        assert "p%40ss" not in result

    def test_amqp_url_masked(self):
        """AMQP/RabbitMQ credentials are masked."""
        url = "amqp://guest:guest@rabbitmq:5672/"
        result = sanitize_url(url)
        assert "guest:guest" not in result
        assert "***@" in result


class TestSanitizeUrls:
    """Test batch URL sanitization."""

    def test_single_string(self):
        """Single string is sanitized and returned as string."""
        url = "nats://user:pass@nats:4222"
        result = sanitize_urls(url)
        assert isinstance(result, str)
        assert "pass" not in result

    def test_list_of_urls(self):
        """List of URLs are all sanitized."""
        urls = [
            "nats://user:pass@nats1:4222",
            "nats://user:pass@nats2:4222",
            "http://localhost:8080",
        ]
        result = sanitize_urls(urls)
        assert isinstance(result, list)
        assert len(result) == 3
        assert "pass" not in result[0]
        assert "pass" not in result[1]
        assert result[2] == "http://localhost:8080"


# ═══════════════════════════════════════════════════════════════════════════════
# Context Variable Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestContextVariables:
    """Test correlation ID and context variable management."""

    def test_set_and_get_correlation_id(self):
        """Correlation ID can be set and retrieved."""
        set_correlation_id("test-corr-123")
        assert get_correlation_id() == "test-corr-123"
        # Cleanup
        correlation_id_var.set(None)

    def test_default_correlation_id_is_none(self):
        """Default correlation ID is None."""
        correlation_id_var.set(None)
        assert get_correlation_id() is None

    def test_set_tenant_id(self):
        """Tenant ID can be set in context."""
        set_tenant_id("tenant-abc")
        assert tenant_id_var.get() == "tenant-abc"
        # Cleanup
        tenant_id_var.set(None)

    def test_set_user_id(self):
        """User ID can be set in context."""
        set_user_id("user-xyz")
        assert user_id_var.get() == "user-xyz"
        # Cleanup
        user_id_var.set(None)
