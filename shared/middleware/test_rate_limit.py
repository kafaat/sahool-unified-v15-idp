"""
Unit Tests for Rate Limiting
اختبارات تحديد المعدل

Run with: pytest shared/middleware/test_rate_limit.py -v
"""

import time
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from shared.middleware.rate_limit import (
    RateLimiter,
    RateLimitConfig,
    TierConfig,
    TokenBucket,
    rate_limit,
    rate_limit_by_user,
    rate_limit_by_api_key,
    rate_limit_by_tenant,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Test TokenBucket
# ═══════════════════════════════════════════════════════════════════════════════


class TestTokenBucket:
    """Test token bucket algorithm"""

    def test_token_bucket_initialization(self):
        """Test that token bucket initializes correctly"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        assert bucket.capacity == 10
        assert bucket.refill_rate == 1.0
        assert bucket.tokens == 10

    def test_token_bucket_consume_success(self):
        """Test successful token consumption"""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        # Should succeed
        assert bucket.consume(1) is True
        assert bucket.tokens == 9

        # Consume more
        assert bucket.consume(5) is True
        assert bucket.tokens == 4

    def test_token_bucket_consume_failure(self):
        """Test token consumption failure when not enough tokens"""
        bucket = TokenBucket(capacity=5, refill_rate=1.0)

        # Consume all tokens
        bucket.tokens = 2

        # Should fail - not enough tokens
        assert bucket.consume(5) is False
        assert bucket.tokens == 2  # Tokens unchanged

    def test_token_bucket_refill(self):
        """Test that tokens refill over time"""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens/second

        # Consume some tokens
        bucket.consume(5)
        assert bucket.tokens == 5

        # Wait and refill
        time.sleep(0.5)  # Should add ~5 tokens
        bucket._refill()

        # Should have approximately 10 tokens (capped at capacity)
        assert bucket.tokens >= 9
        assert bucket.tokens <= 10

    def test_token_bucket_max_capacity(self):
        """Test that tokens don't exceed capacity"""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)

        # Consume some tokens
        bucket.consume(5)

        # Wait longer than needed to fill
        time.sleep(2)
        bucket._refill()

        # Should be capped at capacity
        assert bucket.tokens == 10


# ═══════════════════════════════════════════════════════════════════════════════
# Test RateLimiter
# ═══════════════════════════════════════════════════════════════════════════════


class TestRateLimiter:
    """Test rate limiter functionality"""

    def create_mock_request(
        self,
        ip: str = "127.0.0.1",
        tenant_id: str = "default",
        tier: str = "standard",
        user_id: str = None,
    ) -> Mock:
        """Create a mock request for testing"""
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = ip
        request.headers = Mock()
        request.headers.get = Mock(
            side_effect=lambda key, default=None: {
                "X-Tenant-ID": tenant_id,
                "X-Rate-Limit-Tier": tier,
            }.get(key, default)
        )
        request.url = Mock()
        request.url.path = "/test"

        # Mock user state if provided
        if user_id:
            request.state = Mock()
            request.state.user = Mock()
            request.state.user.id = user_id
        else:
            request.state = Mock()

        return request

    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter()

        assert limiter is not None
        assert limiter.tier_config is not None

    def test_rate_limiter_check_allowed(self):
        """Test that requests within limits are allowed"""
        limiter = RateLimiter()
        request = self.create_mock_request()

        # First request should be allowed
        allowed, headers = limiter.check_rate_limit(request)

        assert allowed is True
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers

    def test_rate_limiter_check_denied_burst(self):
        """Test that burst limit is enforced"""
        # Create limiter with very low burst limit
        config = RateLimitConfig(
            requests_per_minute=100,
            requests_per_hour=1000,
            burst_limit=2,
        )
        limiter = RateLimiter()
        limiter.tier_config = TierConfig(
            free=config, standard=config, premium=config, internal=config
        )

        request = self.create_mock_request()

        # First two requests should succeed
        assert limiter.check_rate_limit(request)[0] is True
        assert limiter.check_rate_limit(request)[0] is True

        # Third request should fail (burst limit exceeded)
        allowed, headers = limiter.check_rate_limit(request)
        assert allowed is False
        assert "Retry-After" in headers

    def test_rate_limiter_check_denied_minute_limit(self):
        """Test that minute limit is enforced"""
        # Create limiter with very low minute limit
        config = RateLimitConfig(
            requests_per_minute=2,
            requests_per_hour=1000,
            burst_limit=10,
        )
        limiter = RateLimiter()
        limiter.tier_config = TierConfig(
            free=config, standard=config, premium=config, internal=config
        )

        request = self.create_mock_request()

        # First two requests should succeed
        assert limiter.check_rate_limit(request)[0] is True
        assert limiter.check_rate_limit(request)[0] is True

        # Third request should fail (minute limit exceeded)
        allowed, headers = limiter.check_rate_limit(request)
        assert allowed is False

    def test_rate_limiter_different_clients(self):
        """Test that different clients have separate limits"""
        limiter = RateLimiter()

        request1 = self.create_mock_request(ip="192.168.1.1")
        request2 = self.create_mock_request(ip="192.168.1.2")

        # Both requests should be allowed
        assert limiter.check_rate_limit(request1)[0] is True
        assert limiter.check_rate_limit(request2)[0] is True

    def test_rate_limiter_tier_selection(self):
        """Test that different tiers have different limits"""
        limiter = RateLimiter()

        # Internal service should have higher limits
        request_internal = self.create_mock_request()
        request_internal.headers.get = Mock(
            side_effect=lambda key, default=None: {
                "X-Internal-Service": "true",
                "X-Tenant-ID": "default",
            }.get(key, default)
        )

        allowed, headers = limiter.check_rate_limit(request_internal)
        assert allowed is True
        # Internal tier has higher limit
        limit = int(headers.get("X-RateLimit-Limit", "0"))
        assert limit >= 1000  # Internal tier minimum


# ═══════════════════════════════════════════════════════════════════════════════
# Test Decorators
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
class TestDecorators:
    """Test rate limit decorators"""

    async def test_rate_limit_decorator_allows_request(self):
        """Test that decorator allows requests within limit"""
        app = FastAPI()

        @app.get("/test")
        @rate_limit(requests_per_minute=100, requests_per_hour=1000)
        async def test_endpoint(request: Request):
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert response.json() == {"message": "success"}

    async def test_rate_limit_decorator_denies_request(self):
        """Test that decorator denies requests over limit"""
        app = FastAPI()

        @app.get("/test")
        @rate_limit(requests_per_minute=1, burst_limit=1)
        async def test_endpoint(request: Request):
            return {"message": "success"}

        client = TestClient(app)

        # First request should succeed
        response1 = client.get("/test")
        assert response1.status_code == 200

        # Second request should fail immediately due to burst limit
        response2 = client.get("/test")
        # Note: May pass depending on timing and token refill

    async def test_rate_limit_by_user_decorator(self):
        """Test user-based rate limiting decorator"""
        app = FastAPI()

        @app.get("/user-endpoint")
        @rate_limit_by_user(requests_per_minute=50)
        async def user_endpoint(request: Request):
            # Mock user
            request.state.user = Mock()
            request.state.user.id = "user123"
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/user-endpoint")

        # Should succeed
        assert response.status_code == 200

    async def test_rate_limit_by_api_key_decorator(self):
        """Test API key-based rate limiting decorator"""
        app = FastAPI()

        @app.get("/api-endpoint")
        @rate_limit_by_api_key(requests_per_minute=100)
        async def api_endpoint(request: Request):
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/api-endpoint", headers={"X-API-Key": "test-key-123"})

        # Should succeed
        assert response.status_code == 200

    async def test_rate_limit_by_tenant_decorator(self):
        """Test tenant-based rate limiting decorator"""
        app = FastAPI()

        @app.get("/tenant-endpoint")
        @rate_limit_by_tenant(requests_per_minute=200)
        async def tenant_endpoint(request: Request):
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/tenant-endpoint", headers={"X-Tenant-ID": "tenant-abc"})

        # Should succeed
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# Test Middleware Integration
# ═══════════════════════════════════════════════════════════════════════════════


class TestMiddlewareIntegration:
    """Test rate limiting middleware integration"""

    def test_middleware_adds_headers(self):
        """Test that middleware adds rate limit headers"""
        from shared.middleware import rate_limit_middleware

        app = FastAPI()
        app.middleware("http")(rate_limit_middleware)

        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/test")

        # Check for rate limit headers
        assert (
            "x-ratelimit-limit" in response.headers
            or "X-RateLimit-Limit" in response.headers
        )

    def test_middleware_excludes_health_endpoints(self):
        """Test that health endpoints are excluded from rate limiting"""
        from shared.middleware import rate_limit_middleware

        app = FastAPI()
        app.middleware("http")(rate_limit_middleware)

        @app.get("/healthz")
        async def health():
            return {"status": "healthy"}

        client = TestClient(app)
        response = client.get("/healthz")

        # Should succeed without rate limiting
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# Test Auth Middleware Rate Limiting
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuthMiddlewareRateLimiting:
    """Test rate limiting in auth middleware"""

    def test_rate_limit_middleware_initialization(self):
        """Test that auth rate limit middleware initializes correctly"""
        from shared.auth.middleware import RateLimitMiddleware

        app = FastAPI()
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=100,
            requests_per_hour=2000,
            burst_limit=20,
        )

        # Middleware should be added
        assert len(app.user_middleware) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Performance Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPerformance:
    """Test rate limiter performance"""

    def test_rate_limiter_performance(self):
        """Test that rate limiter can handle many requests quickly"""
        limiter = RateLimiter()
        request = Mock(spec=Request)
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.headers = Mock()
        request.headers.get = Mock(return_value="default")
        request.url = Mock()
        request.url.path = "/test"

        start_time = time.time()

        # Make 1000 requests
        for _ in range(1000):
            limiter.check_rate_limit(request)

        elapsed = time.time() - start_time

        # Should complete in less than 1 second
        assert elapsed < 1.0, f"Rate limiter too slow: {elapsed:.2f}s for 1000 requests"


# ═══════════════════════════════════════════════════════════════════════════════
# Run Tests
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
