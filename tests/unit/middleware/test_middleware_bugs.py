"""
Bug-hunting tests for SAHOOL Middleware Chain.

Tests target:
- shared/middleware/tenant_context.py: TenantContextMiddleware, get_current_tenant
- shared/middleware/rate_limit.py: RateLimiter, LRUDict, TokenBucket

Run:
    ENVIRONMENT=test PYTHONPATH=. pytest tests/unit/middleware/test_middleware_bugs.py -v --timeout=30
"""

from __future__ import annotations

import asyncio
import os
import time
from unittest.mock import MagicMock, PropertyMock
from uuid import uuid4

import pytest
from starlette.testclient import TestClient

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")

from fastapi import FastAPI, Request  # noqa: E402
from starlette.responses import JSONResponse  # noqa: E402

from shared.middleware.rate_limit import (  # noqa: E402
    LRUDict,
    RateLimitConfig,
    RateLimiter,
    TierConfig,
    TokenBucket,
)
from shared.middleware.tenant_context import (  # noqa: E402
    TenantContext,
    TenantContextMiddleware,
    _tenant_context,
    get_current_tenant,
    get_current_tenant_id,
    get_optional_tenant,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Build test FastAPI app with TenantContextMiddleware
# ─────────────────────────────────────────────────────────────────────────────


def _build_tenant_app(require_tenant=True, exempt_paths=None):
    """Build a FastAPI app with TenantContextMiddleware for testing."""
    app = FastAPI()
    app.add_middleware(
        TenantContextMiddleware,
        require_tenant=require_tenant,
        exempt_paths=exempt_paths or ["/healthz", "/readyz"],
    )

    @app.get("/test")
    async def test_endpoint(request: Request):
        ctx = get_optional_tenant()
        if ctx:
            return {"tenant_id": ctx.id, "user_id": ctx.user_id}
        return {"tenant_id": None}

    @app.get("/healthz")
    async def health():
        return {"status": "ok"}

    @app.get("/tenant-required")
    async def tenant_required(request: Request):
        tenant = get_current_tenant()
        return {"tenant_id": tenant.id}

    return app


# ─────────────────────────────────────────────────────────────────────────────
# 1. Tenant Context Middleware - Empty X-Tenant-ID
# ─────────────────────────────────────────────────────────────────────────────


class TestTenantContextEmptyHeader:
    """BUG HUNT: Middleware with empty or missing X-Tenant-ID header."""

    def test_missing_tenant_header_returns_400(self):
        """Request without X-Tenant-ID should return 400 when require_tenant=True."""
        app = _build_tenant_app(require_tenant=True)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test")
        assert response.status_code == 400
        body = response.json()
        assert body["error"] == "missing_tenant"

    def test_empty_string_tenant_header_returns_400(self):
        """BUG HUNT: Empty string X-Tenant-ID should be rejected."""
        app = _build_tenant_app(require_tenant=True)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test", headers={"X-Tenant-ID": ""})
        # Empty string is falsy, so require_tenant should trigger 400
        assert response.status_code == 400

    def test_whitespace_tenant_header_returns_400(self):
        """BUG HUNT: Whitespace-only X-Tenant-ID should be rejected."""
        app = _build_tenant_app(require_tenant=True)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test", headers={"X-Tenant-ID": "   "})
        # "   " is truthy but not a valid UUID, should fail UUID validation
        assert response.status_code == 400

    def test_missing_tenant_allowed_when_not_required(self):
        """When require_tenant=False, missing tenant should proceed normally."""
        app = _build_tenant_app(require_tenant=False)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json()["tenant_id"] is None

    def test_exempt_path_skips_tenant_check(self):
        """Health endpoints should skip tenant check."""
        app = _build_tenant_app(require_tenant=True)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# ─────────────────────────────────────────────────────────────────────────────
# 2. Tenant Context Middleware - Malformed UUID
# ─────────────────────────────────────────────────────────────────────────────


class TestTenantContextMalformedUUID:
    """BUG HUNT: Middleware must reject malformed UUIDs."""

    def test_non_uuid_string_rejected(self):
        """A plain string (not UUID) must be rejected."""
        app = _build_tenant_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test", headers={"X-Tenant-ID": "not-a-uuid"})
        assert response.status_code == 400
        assert response.json()["error"] == "invalid_tenant_id"

    def test_short_uuid_rejected(self):
        """Truncated UUID must be rejected."""
        app = _build_tenant_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test", headers={"X-Tenant-ID": "12345678-1234"})
        assert response.status_code == 400

    def test_uuid_with_extra_chars_rejected(self):
        """UUID with extra characters must be rejected."""
        app = _build_tenant_app()
        client = TestClient(app, raise_server_exceptions=False)
        valid_uuid = str(uuid4())
        response = client.get("/test", headers={"X-Tenant-ID": valid_uuid + "-extra"})
        assert response.status_code == 400

    def test_valid_uuid_accepted(self):
        """A valid UUID should be accepted."""
        app = _build_tenant_app()
        client = TestClient(app, raise_server_exceptions=False)
        valid_uuid = str(uuid4())
        response = client.get("/test", headers={"X-Tenant-ID": valid_uuid})
        assert response.status_code == 200
        assert response.json()["tenant_id"] == valid_uuid

    def test_uppercase_uuid_accepted(self):
        """UUID with uppercase hex chars should be accepted (regex is case-insensitive)."""
        app = _build_tenant_app()
        client = TestClient(app, raise_server_exceptions=False)
        upper_uuid = str(uuid4()).upper()
        response = client.get("/test", headers={"X-Tenant-ID": upper_uuid})
        assert response.status_code == 200

    def test_sql_injection_in_tenant_id_rejected(self):
        """BUG HUNT: SQL injection attempt in tenant_id must be rejected by UUID validation."""
        app = _build_tenant_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/test",
            headers={"X-Tenant-ID": "'; DROP TABLE users; --"},
        )
        assert response.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# 3. Very Long Tenant ID (Buffer Overflow Attempt)
# ─────────────────────────────────────────────────────────────────────────────


class TestTenantContextLongInput:
    """BUG HUNT: Very long tenant_id must be rejected, not cause crashes."""

    def test_very_long_tenant_id_rejected(self):
        """100KB string as tenant_id should be rejected."""
        app = _build_tenant_app()
        client = TestClient(app, raise_server_exceptions=False)
        long_id = "a" * 100_000
        response = client.get("/test", headers={"X-Tenant-ID": long_id})
        assert response.status_code == 400

    def test_1mb_tenant_id_rejected(self):
        """1MB string as tenant_id should be rejected without server crash."""
        app = _build_tenant_app()
        client = TestClient(app, raise_server_exceptions=False)
        long_id = "b" * 1_000_000
        response = client.get("/test", headers={"X-Tenant-ID": long_id})
        assert response.status_code == 400

    def test_null_bytes_in_tenant_id_rejected(self):
        """BUG HUNT: Null bytes in tenant_id must be rejected."""
        app = _build_tenant_app()
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(
            "/test",
            headers={"X-Tenant-ID": "12345678-1234-1234-1234-1234567890ab\x00evil"},
        )
        # Should be rejected because UUID regex won't match with trailing null + chars
        assert response.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# 4. Tenant Context Cleanup After Request
# ─────────────────────────────────────────────────────────────────────────────


class TestTenantContextCleanup:
    """BUG HUNT: Tenant context must be cleaned up after each request."""

    def test_context_not_leaked_between_requests(self):
        """After a request with tenant_id, the next request without it should not inherit."""
        app = _build_tenant_app(require_tenant=False)
        client = TestClient(app, raise_server_exceptions=False)

        tenant_uuid = str(uuid4())

        # First request: with tenant
        r1 = client.get("/test", headers={"X-Tenant-ID": tenant_uuid})
        assert r1.status_code == 200
        assert r1.json()["tenant_id"] == tenant_uuid

        # Second request: without tenant
        r2 = client.get("/test")
        assert r2.status_code == 200
        assert r2.json()["tenant_id"] is None, (
            "BUG: Tenant context leaked from previous request"
        )

    def test_get_current_tenant_raises_outside_request(self):
        """get_current_tenant() outside a request must raise RuntimeError."""
        # Reset context var to None (simulating no middleware)
        token = _tenant_context.set(None)
        try:
            with pytest.raises(RuntimeError, match="Tenant context not available"):
                get_current_tenant()
        finally:
            _tenant_context.reset(token)

    def test_get_optional_tenant_returns_none_outside_request(self):
        """get_optional_tenant() outside a request must return None."""
        token = _tenant_context.set(None)
        try:
            assert get_optional_tenant() is None
        finally:
            _tenant_context.reset(token)


# ─────────────────────────────────────────────────────────────────────────────
# 5. TenantContext Dataclass
# ─────────────────────────────────────────────────────────────────────────────


class TestTenantContextDataclass:
    """BUG HUNT: TenantContext dataclass edge cases."""

    def test_has_role_with_empty_roles(self):
        """has_role with None roles should not crash."""
        ctx = TenantContext(id="t1", roles=None)
        assert ctx.has_role("admin") is False

    def test_has_role_with_valid_roles(self):
        """has_role with matching role should return True."""
        ctx = TenantContext(id="t1", roles=["admin", "farmer"])
        assert ctx.has_role("admin") is True
        assert ctx.has_role("unknown") is False


# ─────────────────────────────────────────────────────────────────────────────
# 6. Rate Limiter - Token Bucket
# ─────────────────────────────────────────────────────────────────────────────


class TestTokenBucket:
    """BUG HUNT: Token bucket algorithm correctness."""

    def test_bucket_allows_up_to_capacity(self):
        """Bucket with capacity N should allow N requests."""
        bucket = TokenBucket(capacity=5, refill_rate=1.0)
        for _ in range(5):
            assert bucket.consume() is True
        assert bucket.consume() is False

    def test_bucket_refills_over_time(self):
        """After draining, bucket should refill based on rate."""
        bucket = TokenBucket(capacity=2, refill_rate=100.0)  # fast refill
        assert bucket.consume() is True
        assert bucket.consume() is True
        assert bucket.consume() is False

        time.sleep(0.05)  # Wait for refill (100 tokens/sec * 0.05s = 5 tokens)
        assert bucket.consume() is True  # Should have tokens again

    def test_bucket_never_exceeds_capacity(self):
        """Even after long wait, tokens should not exceed capacity."""
        bucket = TokenBucket(capacity=3, refill_rate=100.0)
        time.sleep(0.1)  # Would add 10 tokens but cap is 3
        count = 0
        while bucket.consume():
            count += 1
        assert count == 3, f"Bucket exceeded capacity: got {count} tokens"


# ─────────────────────────────────────────────────────────────────────────────
# 7. Rate Limiter - LRU Eviction
# ─────────────────────────────────────────────────────────────────────────────


class TestLRUDict:
    """BUG HUNT: LRUDict memory cleanup and eviction correctness."""

    def test_evicts_oldest_when_full(self):
        """LRUDict with maxsize=3 must evict oldest entry when adding 4th."""
        d = LRUDict(maxsize=3)
        d["a"] = 1
        d["b"] = 2
        d["c"] = 3
        d["d"] = 4  # Should evict "a"
        assert "a" not in d
        assert "d" in d
        assert len(d) == 3

    def test_access_moves_to_end(self):
        """Accessing a key should make it the most recently used."""
        d = LRUDict(maxsize=3)
        d["a"] = 1
        d["b"] = 2
        d["c"] = 3

        # Access "a" to make it recently used
        _ = d["a"]

        # Now adding "d" should evict "b" (oldest not accessed), not "a"
        d["d"] = 4
        assert "a" in d, "BUG: Recently accessed key was evicted"
        assert "b" not in d, "Oldest key should have been evicted"

    def test_maxsize_enforced_consistently(self):
        """Adding many items should never exceed maxsize."""
        d = LRUDict(maxsize=10)
        for i in range(1000):
            d[f"key-{i}"] = i
        assert len(d) == 10

    def test_missing_key_auto_creates_list(self):
        """__missing__ should auto-create empty list."""
        d = LRUDict(maxsize=10)
        val = d["nonexistent"]
        assert val == []
        assert "nonexistent" in d

    def test_get_with_default_does_not_auto_create(self):
        """get() should return default without creating entry."""
        d = LRUDict(maxsize=10)
        val = d.get("missing", "default")
        assert val == "default"
        assert "missing" not in d

    def test_update_existing_key_moves_to_end(self):
        """Updating an existing key should move it to the end."""
        d = LRUDict(maxsize=3)
        d["a"] = 1
        d["b"] = 2
        d["c"] = 3

        # Update "a"
        d["a"] = 10

        # Adding new key should evict "b", not "a"
        d["d"] = 4
        assert "a" in d
        assert "b" not in d


# ─────────────────────────────────────────────────────────────────────────────
# 8. Rate Limiter - Concurrent Request Simulation
# ─────────────────────────────────────────────────────────────────────────────


class TestRateLimiterConcurrency:
    """BUG HUNT: Rate limiter under concurrent load."""

    @pytest.mark.asyncio
    async def test_rate_limiter_enforces_limit(self):
        """Rate limiter must reject requests exceeding per-minute limit."""
        config = TierConfig(
            free=RateLimitConfig(
                requests_per_minute=5,
                requests_per_hour=100,
                burst_limit=5,
            ),
        )
        limiter = RateLimiter(tier_config=config)

        # Build mock requests using a simple namespace instead of MagicMock
        # to avoid MagicMock's __getattr__ interfering with hasattr checks
        class MockState:
            user = None
            is_service_request = False

        class MockClient:
            host = "127.0.0.1"

        class MockUrl:
            path = "/test"

        class MockRequest:
            client = MockClient()
            url = MockUrl()
            method = "GET"
            headers = {}
            state = MockState()

        async def make_request():
            return await limiter.check_rate_limit(MockRequest())

        allowed_count = 0
        rejected_count = 0
        for _ in range(10):
            allowed, headers = await make_request()
            if allowed:
                allowed_count += 1
            else:
                rejected_count += 1

        assert allowed_count == 5, f"Expected 5 allowed, got {allowed_count}"
        assert rejected_count == 5, f"Expected 5 rejected, got {rejected_count}"

    def test_rate_limiter_memory_bounded(self):
        """Rate limiter internal dicts must be bounded by MAX_ENTRIES."""
        limiter = RateLimiter()
        # Verify the LRU dicts have proper maxsize
        assert limiter._buckets._maxsize == RateLimiter.MAX_ENTRIES
        assert limiter._request_counts._maxsize == RateLimiter.MAX_ENTRIES
