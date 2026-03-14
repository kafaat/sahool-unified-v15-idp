"""
Comprehensive JWT Config Tests for SAHOOL Platform
اختبارات شاملة لتكوين JWT لمنصة سهول

Tests cover:
- JWTConfig class initialization
- Configuration validation
- Signing/verification key retrieval
- Environment-specific validation behavior
- Rate limiting config
- Redis config validation
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from shared.auth.config import (
    JWTConfig,
    JWTConfigError,
    MAX_ACCESS_TOKEN_MINUTES,
    MAX_RATE_LIMIT_REQUESTS,
    MAX_REDIS_DB,
    MAX_REDIS_PORT,
    MAX_REFRESH_TOKEN_DAYS,
    MIN_ACCESS_TOKEN_MINUTES,
    MIN_RATE_LIMIT_REQUESTS,
    MIN_REDIS_DB,
    MIN_REDIS_PORT,
    MIN_REFRESH_TOKEN_DAYS,
    MIN_SECRET_KEY_LENGTH,
)


@pytest.mark.unit
class TestJWTConfigConstants:
    """Tests for JWT configuration constants"""

    def test_min_secret_key_length(self):
        """Test minimum secret key length is 32"""
        assert MIN_SECRET_KEY_LENGTH == 32

    def test_access_token_range(self):
        """Test access token expiration range"""
        assert MIN_ACCESS_TOKEN_MINUTES == 1
        assert MAX_ACCESS_TOKEN_MINUTES == 60

    def test_refresh_token_range(self):
        """Test refresh token expiration range"""
        assert MIN_REFRESH_TOKEN_DAYS == 1
        assert MAX_REFRESH_TOKEN_DAYS == 30

    def test_rate_limit_range(self):
        """Test rate limit requests range"""
        assert MIN_RATE_LIMIT_REQUESTS == 1
        assert MAX_RATE_LIMIT_REQUESTS == 10000

    def test_redis_port_range(self):
        """Test Redis port range"""
        assert MIN_REDIS_PORT == 1
        assert MAX_REDIS_PORT == 65535

    def test_redis_db_range(self):
        """Test Redis DB range"""
        assert MIN_REDIS_DB == 0
        assert MAX_REDIS_DB == 15


@pytest.mark.unit
class TestJWTConfigDefaults:
    """Tests for JWTConfig default values"""

    def test_algorithm_is_hs256(self):
        """Test that default algorithm is HS256"""
        assert JWTConfig.JWT_ALGORITHM == "HS256"

    def test_token_prefix(self):
        """Test token prefix"""
        assert JWTConfig.TOKEN_PREFIX == "Bearer"

    def test_token_header(self):
        """Test token header name"""
        assert JWTConfig.TOKEN_HEADER == "Authorization"


@pytest.mark.unit
class TestGetSigningKey:
    """Tests for get_signing_key method"""

    def test_get_signing_key_with_valid_secret(self):
        """Test getting signing key with valid secret"""
        original = JWTConfig.JWT_SECRET
        try:
            JWTConfig.JWT_SECRET = "test-secret-key-for-unit-tests-only-32chars"
            key = JWTConfig.get_signing_key()
            assert isinstance(key, str)
            assert len(key) >= MIN_SECRET_KEY_LENGTH
        finally:
            JWTConfig.JWT_SECRET = original

    def test_get_signing_key_too_short(self):
        """Test that short secret raises error"""
        original = JWTConfig.JWT_SECRET
        original_env = os.environ.pop("JWT_SECRET_KEY", None)
        try:
            JWTConfig.JWT_SECRET = "short"
            with pytest.raises(JWTConfigError):
                JWTConfig.get_signing_key()
        finally:
            JWTConfig.JWT_SECRET = original
            if original_env is not None:
                os.environ["JWT_SECRET_KEY"] = original_env

    def test_get_signing_key_empty(self):
        """Test that empty secret raises error"""
        original = JWTConfig.JWT_SECRET
        original_env = os.environ.pop("JWT_SECRET_KEY", None)
        try:
            JWTConfig.JWT_SECRET = ""
            with pytest.raises(JWTConfigError):
                JWTConfig.get_signing_key()
        finally:
            JWTConfig.JWT_SECRET = original
            if original_env is not None:
                os.environ["JWT_SECRET_KEY"] = original_env


@pytest.mark.unit
class TestGetVerificationKey:
    """Tests for get_verification_key method"""

    def test_get_verification_key_with_valid_secret(self):
        """Test getting verification key"""
        original = JWTConfig.JWT_SECRET
        try:
            JWTConfig.JWT_SECRET = "test-secret-key-for-unit-tests-only-32chars"
            key = JWTConfig.get_verification_key()
            assert isinstance(key, str)
            assert len(key) >= MIN_SECRET_KEY_LENGTH
        finally:
            JWTConfig.JWT_SECRET = original

    def test_signing_and_verification_keys_match(self):
        """Test that signing and verification keys are the same for HS256"""
        original = JWTConfig.JWT_SECRET
        try:
            JWTConfig.JWT_SECRET = "test-secret-key-for-unit-tests-only-32chars"
            signing = JWTConfig.get_signing_key()
            verification = JWTConfig.get_verification_key()
            assert signing == verification
        finally:
            JWTConfig.JWT_SECRET = original


@pytest.mark.unit
class TestValidateWithReport:
    """Tests for validate_with_report method"""

    def test_report_structure(self):
        """Test that report has correct structure"""
        report = JWTConfig.validate_with_report()
        assert "valid" in report
        assert "errors" in report
        assert "warnings" in report
        assert "environment" in report
        assert "summary" in report

    def test_report_summary_structure(self):
        """Test that summary has correct fields"""
        report = JWTConfig.validate_with_report()
        summary = report["summary"]
        assert "jwt_secret_configured" in summary
        assert "jwt_secret_length" in summary
        assert "access_token_minutes" in summary
        assert "refresh_token_days" in summary
        assert "rate_limiting_enabled" in summary
        assert "token_revocation_enabled" in summary
        assert "redis_configured" in summary

    def test_valid_config_report(self):
        """Test report with valid configuration"""
        report = JWTConfig.validate_with_report()
        assert isinstance(report["valid"], bool)
        assert isinstance(report["errors"], list)
        assert isinstance(report["warnings"], list)


@pytest.mark.unit
class TestJWTConfigError:
    """Tests for JWTConfigError exception"""

    def test_config_error_is_exception(self):
        """Test that JWTConfigError is an Exception"""
        assert issubclass(JWTConfigError, Exception)

    def test_config_error_message(self):
        """Test JWTConfigError message"""
        error = JWTConfigError("Test config error")
        assert str(error) == "Test config error"
