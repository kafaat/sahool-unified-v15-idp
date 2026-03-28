"""
Tests for Rate Limiter - advisory-service
"""

import asyncio
import time
from unittest.mock import MagicMock, PropertyMock

import pytest
from fastapi import HTTPException
from src.rate_limiter import (
    TIERS,
    AdvisoryRateLimiter,
    RateLimitTier,
    get_rate_limiter,
    rate_limit,
)


def _make_mock_request(tenant_id=None, client_ip="127.0.0.1", is_service=False):
    """Create a mock FastAPI request"""
    request = MagicMock()
    request.state = MagicMock()
    request.state.tenant_id = tenant_id
    request.state.is_service_request = is_service
    # Remove user attr to avoid fallback
    if not tenant_id:
        request.state.tenant_id = None
        request.state.user = MagicMock()
        request.state.user.tenant_id = None
    else:
        request.state.user = MagicMock()
        request.state.user.tenant_id = tenant_id
    request.headers = {"X-Tenant-ID": tenant_id or "default"}
    request.client = MagicMock()
    request.client.host = client_ip
    return request


class TestRateLimitTier:
    """Tests for RateLimitTier dataclass"""

    def test_tier_creation(self):
        tier = RateLimitTier(requests_per_minute=30, requests_per_hour=500, burst_limit=5)
        assert tier.requests_per_minute == 30
        assert tier.requests_per_hour == 500
        assert tier.burst_limit == 5


class TestTiers:
    """Tests for tier definitions"""

    def test_all_tiers_defined(self):
        expected = ["disease_assess", "symptom_assess", "fertilizer_plan", "ndvi_assess", "lookup", "default"]
        for tier_name in expected:
            assert tier_name in TIERS

    def test_lookup_has_highest_limits(self):
        assert TIERS["lookup"].requests_per_minute > TIERS["disease_assess"].requests_per_minute


class TestAdvisoryRateLimiter:
    """Tests for AdvisoryRateLimiter class"""

    def test_allows_first_request(self):
        limiter = AdvisoryRateLimiter()
        request = _make_mock_request(tenant_id="t1")
        allowed, headers = limiter.check(request, "default")
        assert allowed is True
        assert "X-RateLimit-Limit" in headers

    def test_internal_service_bypass(self):
        limiter = AdvisoryRateLimiter()
        request = _make_mock_request(is_service=True)
        allowed, headers = limiter.check(request, "default")
        assert allowed is True
        assert headers.get("X-RateLimit-Bypass") == "internal"

    def test_burst_limit(self):
        limiter = AdvisoryRateLimiter()
        request = _make_mock_request(tenant_id="t1")
        # Exceed burst limit (ndvi_assess has burst_limit=3)
        results = []
        for _ in range(10):
            allowed, headers = limiter.check(request, "ndvi_assess")
            results.append(allowed)
        # Some should be rejected
        assert False in results

    def test_per_minute_limit(self):
        limiter = AdvisoryRateLimiter()
        request = _make_mock_request(tenant_id="t1", client_ip="10.0.0.1")
        # Use a tier with low per-minute limit
        tier_name = "ndvi_assess"  # 20/min
        allowed_count = 0
        for _ in range(30):
            allowed, _ = limiter.check(request, tier_name)
            if allowed:
                allowed_count += 1
        assert allowed_count <= TIERS[tier_name].requests_per_minute

    def test_different_tenants_separate_limits(self):
        limiter = AdvisoryRateLimiter()
        req1 = _make_mock_request(tenant_id="tenant_a")
        req2 = _make_mock_request(tenant_id="tenant_b")
        # Both should be allowed
        allowed1, _ = limiter.check(req1, "default")
        allowed2, _ = limiter.check(req2, "default")
        assert allowed1 is True
        assert allowed2 is True

    def test_headers_include_retry_after_when_exceeded(self):
        limiter = AdvisoryRateLimiter()
        request = _make_mock_request(tenant_id="t1")
        # Exhaust burst
        for _ in range(20):
            allowed, headers = limiter.check(request, "ndvi_assess")
            if not allowed:
                assert "Retry-After" in headers
                break

    def test_client_key_from_jwt_tenant(self):
        limiter = AdvisoryRateLimiter()
        request = _make_mock_request(tenant_id="jwt_tenant")
        key = limiter._get_client_key(request, "default")
        assert "jwt_tenant" in key

    def test_client_key_fallback_to_header(self):
        limiter = AdvisoryRateLimiter()
        request = MagicMock()
        request.state = MagicMock(spec=[])  # No tenant_id or user attributes
        request.headers = {"X-Tenant-ID": "header_tenant"}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        key = limiter._get_client_key(request, "default")
        assert "header_tenant" in key

    def test_clean_window(self):
        limiter = AdvisoryRateLimiter()
        now = time.time()
        window = [now - 120, now - 90, now - 30, now - 5]
        cleaned = limiter._clean_window(window, 60)
        assert len(cleaned) == 2  # Only last 2 within 60s

    def test_check_burst_refill(self):
        limiter = AdvisoryRateLimiter()
        tier = RateLimitTier(requests_per_minute=60, requests_per_hour=1000, burst_limit=5)
        # First request should pass
        assert limiter._check_burst("test_key", tier) is True


class TestRateLimitDecorator:
    """Tests for rate_limit decorator"""

    def test_async_decorator_allows(self):
        import src.rate_limiter as rl

        rl._rate_limiter = None

        @rate_limit(tier="lookup")
        async def my_endpoint(request):
            return {"ok": True}

        request = _make_mock_request(tenant_id="t1")
        result = asyncio.run(my_endpoint(request))
        assert result == {"ok": True}

    def test_sync_decorator_allows(self):
        import src.rate_limiter as rl

        rl._rate_limiter = None

        @rate_limit(tier="lookup")
        def my_sync_endpoint(request):
            return {"ok": True}

        request = _make_mock_request(tenant_id="t1")
        result = my_sync_endpoint(request)
        assert result == {"ok": True}

    def test_async_decorator_no_request_skips(self):
        @rate_limit(tier="lookup")
        async def no_request_endpoint():
            return {"ok": True}

        result = asyncio.run(no_request_endpoint())
        assert result == {"ok": True}

    def test_sync_decorator_no_request_skips(self):
        @rate_limit(tier="lookup")
        def no_request_sync():
            return {"ok": True}

        result = no_request_sync()
        assert result == {"ok": True}
