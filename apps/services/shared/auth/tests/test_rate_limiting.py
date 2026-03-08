"""
SAHOOL Authentication Rate Limiting Unit Tests
اختبارات التحكم في معدل طلبات المصادقة

Comprehensive unit tests for AuthRateLimiter class including:
- Rate limit configuration validation
- Authentication key generation
- Login rate limiting
- Password reset rate limiting
- Registration rate limiting
- Token refresh rate limiting
- Rate limit headers
- Error handling and HTTPException scenarios
"""

import asyncio
import os
import sys
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Request, status

# Add parent module path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from middleware.rate_limiter import (
    InMemoryRateLimiter,
    RateLimitConfig,
    RateLimiter,
)
from rate_limiting import (
    AUTH_RATE_CONFIGS,
    AuthRateLimitConfigs,
    AuthRateLimiter,
    get_auth_rate_limiter,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_request():
    """Create a mock FastAPI Request object."""
    request = MagicMock(spec=Request)
    request.client.host = "192.168.1.100"
    request.headers.get.return_value = None
    return request


@pytest.fixture
def mock_request_with_forwarded():
    """Create a mock FastAPI Request object with X-Forwarded-For header."""
    request = MagicMock(spec=Request)
    request.client.host = "192.168.1.100"

    def headers_get(key, default=None):
        if key == "X-Forwarded-For":
            return "10.0.0.50, 192.168.1.1"
        return default

    request.headers.get.side_effect = headers_get
    return request


@pytest.fixture
def mock_request_no_client():
    """Create a mock Request with no client info."""
    request = MagicMock(spec=Request)
    request.client = None
    request.headers.get.return_value = None
    return request


@pytest.fixture
def auth_rate_limiter():
    """Create a fresh AuthRateLimiter instance."""
    return AuthRateLimiter()


@pytest.fixture
def auth_rate_limiter_with_base():
    """Create an AuthRateLimiter with custom base limiter."""
    base_limiter = RateLimiter(use_redis=False)
    return AuthRateLimiter(base_limiter=base_limiter)


# ═══════════════════════════════════════════════════════════════════════════════
# Test AuthRateLimitConfigs
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuthRateLimitConfigs:
    """Test authentication-specific rate limit configurations."""

    def test_login_config_exists(self):
        """Test that LOGIN configuration is defined."""
        assert hasattr(AuthRateLimitConfigs, "LOGIN")
        assert AuthRateLimitConfigs.LOGIN.requests_per_minute == 5
        assert AuthRateLimitConfigs.LOGIN.requests_per_hour == 20
        assert AuthRateLimitConfigs.LOGIN.burst_limit == 2
        assert AuthRateLimitConfigs.LOGIN.enabled is True

    def test_password_reset_config_exists(self):
        """Test that PASSWORD_RESET configuration is defined."""
        assert hasattr(AuthRateLimitConfigs, "PASSWORD_RESET")
        assert AuthRateLimitConfigs.PASSWORD_RESET.requests_per_minute == 3
        assert AuthRateLimitConfigs.PASSWORD_RESET.requests_per_hour == 10
        assert AuthRateLimitConfigs.PASSWORD_RESET.burst_limit == 1
        assert AuthRateLimitConfigs.PASSWORD_RESET.enabled is True

    def test_registration_config_exists(self):
        """Test that REGISTRATION configuration is defined."""
        assert hasattr(AuthRateLimitConfigs, "REGISTRATION")
        assert AuthRateLimitConfigs.REGISTRATION.requests_per_minute == 10
        assert AuthRateLimitConfigs.REGISTRATION.requests_per_hour == 50
        assert AuthRateLimitConfigs.REGISTRATION.burst_limit == 5
        assert AuthRateLimitConfigs.REGISTRATION.enabled is True

    def test_token_refresh_config_exists(self):
        """Test that TOKEN_REFRESH configuration is defined."""
        assert hasattr(AuthRateLimitConfigs, "TOKEN_REFRESH")
        assert AuthRateLimitConfigs.TOKEN_REFRESH.requests_per_minute == 10
        assert AuthRateLimitConfigs.TOKEN_REFRESH.requests_per_hour == 100
        assert AuthRateLimitConfigs.TOKEN_REFRESH.burst_limit == 5
        assert AuthRateLimitConfigs.TOKEN_REFRESH.enabled is True

    def test_email_verification_config_exists(self):
        """Test that EMAIL_VERIFICATION configuration is defined."""
        assert hasattr(AuthRateLimitConfigs, "EMAIL_VERIFICATION")
        assert AuthRateLimitConfigs.EMAIL_VERIFICATION.requests_per_minute == 5
        assert AuthRateLimitConfigs.EMAIL_VERIFICATION.requests_per_hour == 30
        assert AuthRateLimitConfigs.EMAIL_VERIFICATION.burst_limit == 3
        assert AuthRateLimitConfigs.EMAIL_VERIFICATION.enabled is True

    def test_two_factor_auth_config_exists(self):
        """Test that TWO_FACTOR_AUTH configuration is defined."""
        assert hasattr(AuthRateLimitConfigs, "TWO_FACTOR_AUTH")
        assert AuthRateLimitConfigs.TWO_FACTOR_AUTH.requests_per_minute == 5
        assert AuthRateLimitConfigs.TWO_FACTOR_AUTH.requests_per_hour == 20
        assert AuthRateLimitConfigs.TWO_FACTOR_AUTH.burst_limit == 2
        assert AuthRateLimitConfigs.TWO_FACTOR_AUTH.enabled is True

    def test_singleton_instance_exists(self):
        """Test that AUTH_RATE_CONFIGS singleton exists."""
        assert AUTH_RATE_CONFIGS is not None
        assert isinstance(AUTH_RATE_CONFIGS, AuthRateLimitConfigs)


# ═══════════════════════════════════════════════════════════════════════════════
# Test AuthRateLimiter Initialization
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuthRateLimiterInit:
    """Test AuthRateLimiter initialization."""

    def test_initialization_with_default_limiter(self, auth_rate_limiter):
        """Test initialization creates default RateLimiter."""
        assert auth_rate_limiter._limiter is not None
        assert isinstance(auth_rate_limiter._limiter, RateLimiter)

    def test_initialization_with_custom_limiter(self):
        """Test initialization with custom RateLimiter."""
        custom_limiter = RateLimiter(use_redis=False)
        limiter = AuthRateLimiter(base_limiter=custom_limiter)
        assert limiter._limiter is custom_limiter

    def test_initialization_with_none_uses_default(self):
        """Test that passing None creates default limiter."""
        limiter = AuthRateLimiter(base_limiter=None)
        assert limiter._limiter is not None
        assert isinstance(limiter._limiter, RateLimiter)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Authentication Key Generation
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuthKeyGeneration:
    """Test _get_auth_key method."""

    def test_get_auth_key_with_client_ip(self, auth_rate_limiter, mock_request):
        """Test key generation with client IP."""
        key = auth_rate_limiter._get_auth_key(mock_request)
        assert key == "auth:192.168.1.100"

    def test_get_auth_key_with_identifier(self, auth_rate_limiter, mock_request):
        """Test key generation with IP and identifier."""
        key = auth_rate_limiter._get_auth_key(mock_request, "user@example.com")
        assert key == "auth:192.168.1.100:user@example.com"

    def test_get_auth_key_with_forwarded_for_header(self, auth_rate_limiter, mock_request_with_forwarded):
        """Test key generation with X-Forwarded-For header."""
        key = auth_rate_limiter._get_auth_key(mock_request_with_forwarded)
        assert key == "auth:10.0.0.50"

    def test_get_auth_key_with_forwarded_for_and_identifier(self, auth_rate_limiter, mock_request_with_forwarded):
        """Test key generation with X-Forwarded-For header and identifier."""
        key = auth_rate_limiter._get_auth_key(mock_request_with_forwarded, "testuser")
        assert key == "auth:10.0.0.50:testuser"

    def test_get_auth_key_no_client(self, auth_rate_limiter, mock_request_no_client):
        """Test key generation when client is None."""
        key = auth_rate_limiter._get_auth_key(mock_request_no_client)
        assert key == "auth:unknown"

    def test_get_auth_key_no_client_with_identifier(self, auth_rate_limiter, mock_request_no_client):
        """Test key generation when client is None but identifier provided."""
        key = auth_rate_limiter._get_auth_key(mock_request_no_client, "admin")
        assert key == "auth:unknown:admin"

    def test_get_auth_key_whitespace_handling_in_forwarded_for(self, auth_rate_limiter):
        """Test that whitespace is properly handled in X-Forwarded-For."""
        request = MagicMock(spec=Request)
        request.client.host = "192.168.1.100"

        def headers_get(key, default=None):
            if key == "X-Forwarded-For":
                return "  10.0.0.50  ,  192.168.1.1  "
            return default

        request.headers.get.side_effect = headers_get
        key = auth_rate_limiter._get_auth_key(request)
        assert key == "auth:10.0.0.50"


# ═══════════════════════════════════════════════════════════════════════════════
# Test Login Rate Limiting
# ═══════════════════════════════════════════════════════════════════════════════


class TestCheckLoginLimit:
    """Test check_login_limit method."""

    @pytest.mark.asyncio
    async def test_login_limit_allows_first_request(self, auth_rate_limiter, mock_request):
        """Test that first login attempt is allowed."""
        allowed, remaining, limit, reset = await auth_rate_limiter.check_login_limit(mock_request, "user@example.com")

        assert allowed is True
        assert limit == 5  # LOGIN config: 5 per minute
        assert remaining >= 0
        assert reset > 0

    @pytest.mark.asyncio
    async def test_login_limit_tracks_attempts(self, auth_rate_limiter, mock_request):
        """Test that login attempts are tracked."""
        username = "user@example.com"

        for attempt in range(1, 4):
            allowed, remaining, limit, reset = await auth_rate_limiter.check_login_limit(mock_request, username)
            assert allowed is True
            assert remaining == 5 - attempt

    @pytest.mark.asyncio
    async def test_login_limit_exceeded_raises_exception(self, auth_rate_limiter, mock_request):
        """Test that exceeding login limit raises HTTPException."""
        username = "user@example.com"

        # Make 5 successful attempts
        for _ in range(5):
            await auth_rate_limiter.check_login_limit(mock_request, username)

        # 6th attempt should fail
        with pytest.raises(HTTPException) as exc_info:
            await auth_rate_limiter.check_login_limit(mock_request, username)

        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert exc_info.value.detail["error"] == "rate_limit_exceeded"

    @pytest.mark.asyncio
    async def test_login_limit_exception_has_retry_after(self, auth_rate_limiter, mock_request):
        """Test that rate limit exception includes retry_after."""
        username = "user@example.com"

        # Exceed limit
        for _ in range(5):
            await auth_rate_limiter.check_login_limit(mock_request, username)

        with pytest.raises(HTTPException) as exc_info:
            await auth_rate_limiter.check_login_limit(mock_request, username)

        assert "retry_after" in exc_info.value.detail
        assert exc_info.value.detail["retry_after"] > 0

    @pytest.mark.asyncio
    async def test_login_limit_different_users_independent(self, auth_rate_limiter, mock_request):
        """Test that rate limits for different users are independent."""
        # User 1 makes 4 attempts
        for _ in range(4):
            await auth_rate_limiter.check_login_limit(mock_request, "user1@example.com")

        # User 2 should still be able to make a request
        allowed, _, _, _ = await auth_rate_limiter.check_login_limit(mock_request, "user2@example.com")
        assert allowed is True

    @pytest.mark.asyncio
    async def test_login_limit_different_ips_independent(self, auth_rate_limiter):
        """Test that rate limits for different IPs are independent."""
        username = "user@example.com"

        request1 = MagicMock(spec=Request)
        request1.client.host = "192.168.1.100"
        request1.headers.get.return_value = None

        request2 = MagicMock(spec=Request)
        request2.client.host = "192.168.1.101"
        request2.headers.get.return_value = None

        # Both IPs make requests
        for _ in range(2):
            allowed1, _, _, _ = await auth_rate_limiter.check_login_limit(request1, username)
            allowed2, _, _, _ = await auth_rate_limiter.check_login_limit(request2, username)
            assert allowed1 is True
            assert allowed2 is True


# ═══════════════════════════════════════════════════════════════════════════════
# Test Password Reset Rate Limiting
# ═══════════════════════════════════════════════════════════════════════════════


class TestCheckPasswordResetLimit:
    """Test check_password_reset_limit method."""

    @pytest.mark.asyncio
    async def test_password_reset_limit_allows_first_request(self, auth_rate_limiter, mock_request):
        """Test that first password reset request is allowed."""
        allowed, remaining, limit, reset = await auth_rate_limiter.check_password_reset_limit(
            mock_request, "user@example.com"
        )

        assert allowed is True
        assert limit == 3  # PASSWORD_RESET config: 3 per minute
        assert remaining >= 0
        assert reset > 0

    @pytest.mark.asyncio
    async def test_password_reset_limit_tracks_attempts(self, auth_rate_limiter, mock_request):
        """Test that password reset attempts are tracked."""
        email = "user@example.com"

        for attempt in range(1, 3):
            allowed, remaining, limit, reset = await auth_rate_limiter.check_password_reset_limit(mock_request, email)
            assert allowed is True
            assert remaining == 3 - attempt

    @pytest.mark.asyncio
    async def test_password_reset_limit_exceeded_raises_exception(self, auth_rate_limiter, mock_request):
        """Test that exceeding password reset limit raises HTTPException."""
        email = "user@example.com"

        # Make 3 successful attempts
        for _ in range(3):
            await auth_rate_limiter.check_password_reset_limit(mock_request, email)

        # 4th attempt should fail
        with pytest.raises(HTTPException) as exc_info:
            await auth_rate_limiter.check_password_reset_limit(mock_request, email)

        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "password reset" in exc_info.value.detail["message"].lower()

    @pytest.mark.asyncio
    async def test_password_reset_has_stricter_limits_than_login(self, auth_rate_limiter):
        """Test that password reset has stricter limits than login."""
        password_reset_config = AUTH_RATE_CONFIGS.PASSWORD_RESET
        login_config = AUTH_RATE_CONFIGS.LOGIN

        assert password_reset_config.requests_per_minute < login_config.requests_per_minute
        assert password_reset_config.requests_per_hour < login_config.requests_per_hour


# ═══════════════════════════════════════════════════════════════════════════════
# Test Registration Rate Limiting
# ═══════════════════════════════════════════════════════════════════════════════


class TestCheckRegistrationLimit:
    """Test check_registration_limit method."""

    @pytest.mark.asyncio
    async def test_registration_limit_allows_first_request(self, auth_rate_limiter, mock_request):
        """Test that first registration request is allowed."""
        allowed, remaining, limit, reset = await auth_rate_limiter.check_registration_limit(mock_request)

        assert allowed is True
        assert limit == 10  # REGISTRATION config: 10 per minute
        assert remaining >= 0
        assert reset > 0

    @pytest.mark.asyncio
    async def test_registration_limit_with_email(self, auth_rate_limiter, mock_request):
        """Test registration limit with email identifier."""
        email = "newuser@example.com"
        allowed, remaining, limit, reset = await auth_rate_limiter.check_registration_limit(mock_request, email)

        assert allowed is True
        assert limit == 10

    @pytest.mark.asyncio
    async def test_registration_limit_tracks_attempts(self, auth_rate_limiter, mock_request):
        """Test that registration attempts are tracked."""
        email = "newuser@example.com"

        for attempt in range(1, 6):
            allowed, remaining, limit, reset = await auth_rate_limiter.check_registration_limit(mock_request, email)
            assert allowed is True
            assert remaining == 10 - attempt

    @pytest.mark.asyncio
    async def test_registration_limit_exceeded_raises_exception(self, auth_rate_limiter, mock_request):
        """Test that exceeding registration limit raises HTTPException."""
        # Make 10 successful attempts
        for _ in range(10):
            await auth_rate_limiter.check_registration_limit(mock_request, "new@example.com")

        # 11th attempt should fail
        with pytest.raises(HTTPException) as exc_info:
            await auth_rate_limiter.check_registration_limit(mock_request, "new@example.com")

        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "registration" in exc_info.value.detail["message"].lower()

    @pytest.mark.asyncio
    async def test_registration_limit_ip_based_tracking(self, auth_rate_limiter):
        """Test that registration limits are tracked by IP."""
        request1 = MagicMock(spec=Request)
        request1.client.host = "192.168.1.100"
        request1.headers.get.return_value = None

        request2 = MagicMock(spec=Request)
        request2.client.host = "192.168.1.101"
        request2.headers.get.return_value = None

        # Both IPs should be able to make separate registrations
        for _ in range(5):
            allowed1, _, _, _ = await auth_rate_limiter.check_registration_limit(request1)
            allowed2, _, _, _ = await auth_rate_limiter.check_registration_limit(request2)
            assert allowed1 is True
            assert allowed2 is True


# ═══════════════════════════════════════════════════════════════════════════════
# Test Token Refresh Rate Limiting
# ═══════════════════════════════════════════════════════════════════════════════


class TestCheckTokenRefreshLimit:
    """Test check_token_refresh_limit method."""

    @pytest.mark.asyncio
    async def test_token_refresh_limit_allows_first_request(self, auth_rate_limiter, mock_request):
        """Test that first token refresh is allowed."""
        allowed, remaining, limit, reset = await auth_rate_limiter.check_token_refresh_limit(mock_request, "user123")

        assert allowed is True
        assert limit == 10  # TOKEN_REFRESH config: 10 per minute
        assert remaining >= 0
        assert reset > 0

    @pytest.mark.asyncio
    async def test_token_refresh_limit_tracks_attempts(self, auth_rate_limiter, mock_request):
        """Test that token refresh attempts are tracked."""
        user_id = "user123"

        for attempt in range(1, 6):
            allowed, remaining, limit, reset = await auth_rate_limiter.check_token_refresh_limit(mock_request, user_id)
            assert allowed is True
            assert remaining == 10 - attempt

    @pytest.mark.asyncio
    async def test_token_refresh_limit_exceeded_raises_exception(self, auth_rate_limiter, mock_request):
        """Test that exceeding token refresh limit raises HTTPException."""
        user_id = "user123"

        # Make 10 successful attempts
        for _ in range(10):
            await auth_rate_limiter.check_token_refresh_limit(mock_request, user_id)

        # 11th attempt should fail
        with pytest.raises(HTTPException) as exc_info:
            await auth_rate_limiter.check_token_refresh_limit(mock_request, user_id)

        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "token refresh" in exc_info.value.detail["message"].lower()

    @pytest.mark.asyncio
    async def test_token_refresh_limit_different_users_independent(self, auth_rate_limiter, mock_request):
        """Test that token refresh limits for different users are independent."""
        # User 1 makes 8 refreshes
        for _ in range(8):
            await auth_rate_limiter.check_token_refresh_limit(mock_request, "user1")

        # User 2 should still be able to make a refresh
        allowed, _, _, _ = await auth_rate_limiter.check_token_refresh_limit(mock_request, "user2")
        assert allowed is True


# ═══════════════════════════════════════════════════════════════════════════════
# Test Rate Limit Headers
# ═══════════════════════════════════════════════════════════════════════════════


class TestRateLimitHeaders:
    """Test that rate limit headers are properly included in exceptions."""

    @pytest.mark.asyncio
    async def test_login_limit_exception_includes_headers(self, auth_rate_limiter, mock_request):
        """Test that login rate limit exception includes RateLimit headers."""
        username = "user@example.com"

        # Exceed limit
        for _ in range(5):
            await auth_rate_limiter.check_login_limit(mock_request, username)

        with pytest.raises(HTTPException) as exc_info:
            await auth_rate_limiter.check_login_limit(mock_request, username)

        headers = exc_info.value.headers
        assert headers is not None
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers

    @pytest.mark.asyncio
    async def test_password_reset_exception_includes_headers(self, auth_rate_limiter, mock_request):
        """Test that password reset exception includes RateLimit headers."""
        email = "user@example.com"

        # Exceed limit
        for _ in range(3):
            await auth_rate_limiter.check_password_reset_limit(mock_request, email)

        with pytest.raises(HTTPException) as exc_info:
            await auth_rate_limiter.check_password_reset_limit(mock_request, email)

        headers = exc_info.value.headers
        assert headers is not None
        assert "X-RateLimit-Limit" in headers


# ═══════════════════════════════════════════════════════════════════════════════
# Test Dependency Injection
# ═══════════════════════════════════════════════════════════════════════════════


class TestDependencyInjection:
    """Test get_auth_rate_limiter dependency function."""

    def test_get_auth_rate_limiter_returns_singleton(self):
        """Test that get_auth_rate_limiter returns singleton instance."""
        limiter1 = get_auth_rate_limiter()
        limiter2 = get_auth_rate_limiter()

        assert limiter1 is limiter2
        assert isinstance(limiter1, AuthRateLimiter)

    def test_get_auth_rate_limiter_can_be_called_multiple_times(self):
        """Test that get_auth_rate_limiter can be called repeatedly."""
        limiters = [get_auth_rate_limiter() for _ in range(5)]
        assert all(l is limiters[0] for l in limiters)


# ═══════════════════════════════════════════════════════════════════════════════
# Test Integration and Edge Cases
# ═══════════════════════════════════════════════════════════════════════════════


class TestIntegrationAndEdgeCases:
    """Test integration scenarios and edge cases."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_same_user(self, auth_rate_limiter, mock_request):
        """Test handling of concurrent requests from same user."""
        username = "user@example.com"

        # Create multiple concurrent tasks
        tasks = [auth_rate_limiter.check_login_limit(mock_request, username) for _ in range(3)]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        successful = sum(1 for r in results if not isinstance(r, Exception))
        assert successful == 3

    @pytest.mark.asyncio
    async def test_multiple_auth_operations_different_methods(self, auth_rate_limiter, mock_request):
        """Test that different rate limit checks are independent."""
        # Login attempts
        login_allowed, _, _, _ = await auth_rate_limiter.check_login_limit(mock_request, "user1")
        assert login_allowed is True

        # Password reset attempts (different endpoint/config)
        reset_allowed, _, _, _ = await auth_rate_limiter.check_password_reset_limit(mock_request, "user1@example.com")
        assert reset_allowed is True

        # Registration attempts (different endpoint/config)
        reg_allowed, _, _, _ = await auth_rate_limiter.check_registration_limit(mock_request, "newuser@example.com")
        assert reg_allowed is True

    @pytest.mark.asyncio
    async def test_rate_limit_config_strictness_hierarchy(self, auth_rate_limiter):
        """Test that rate limits follow strictness hierarchy: password_reset > login > registration."""
        configs = {
            "login": AUTH_RATE_CONFIGS.LOGIN,
            "password_reset": AUTH_RATE_CONFIGS.PASSWORD_RESET,
            "registration": AUTH_RATE_CONFIGS.REGISTRATION,
        }

        # Password reset should be strictest
        assert configs["password_reset"].requests_per_minute <= configs["login"].requests_per_minute
        # Login should be stricter than registration
        assert configs["login"].requests_per_minute <= configs["registration"].requests_per_minute

    def test_authrate_limiter_config_is_enabled(self):
        """Test that all auth rate limiting configs are enabled."""
        configs = [
            AUTH_RATE_CONFIGS.LOGIN,
            AUTH_RATE_CONFIGS.PASSWORD_RESET,
            AUTH_RATE_CONFIGS.REGISTRATION,
            AUTH_RATE_CONFIGS.TOKEN_REFRESH,
            AUTH_RATE_CONFIGS.EMAIL_VERIFICATION,
            AUTH_RATE_CONFIGS.TWO_FACTOR_AUTH,
        ]

        for config in configs:
            assert config.enabled is True, f"Config {config} is not enabled"


# ═══════════════════════════════════════════════════════════════════════════════
# Test Error Scenarios
# ═══════════════════════════════════════════════════════════════════════════════


class TestErrorScenarios:
    """Test error handling and exception scenarios."""

    @pytest.mark.asyncio
    async def test_empty_username_is_allowed(self, auth_rate_limiter, mock_request):
        """Test that empty username string is handled."""
        allowed, _, _, _ = await auth_rate_limiter.check_login_limit(mock_request, "")
        assert allowed is True

    @pytest.mark.asyncio
    async def test_very_long_identifier(self, auth_rate_limiter, mock_request):
        """Test that very long identifiers are handled."""
        long_identifier = "a" * 1000
        allowed, _, _, _ = await auth_rate_limiter.check_login_limit(mock_request, long_identifier)
        assert allowed is True

    @pytest.mark.asyncio
    async def test_special_characters_in_identifier(self, auth_rate_limiter, mock_request):
        """Test that special characters in identifiers are handled."""
        special_identifiers = [
            "user@example.com",
            "user+tag@example.com",
            "user.name@example.com",
            "user123!@#$%",
        ]

        for identifier in special_identifiers:
            allowed, _, _, _ = await auth_rate_limiter.check_login_limit(mock_request, identifier)
            assert allowed is True


# ═══════════════════════════════════════════════════════════════════════════════
# Test Entry Point
# ═══════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
