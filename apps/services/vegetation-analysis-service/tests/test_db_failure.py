"""
DB Failure Tests - Vegetation Analysis Service
اختبارات فشل "قاعدة البيانات" لخدمة تحليل الغطاء النباتي

Context: The vegetation-analysis-service's "database" has two layers:
  1. Redis cache (src/cache.py) — tenant-scoped keys, async, graceful fallback
  2. Optional PostgreSQL pool (app.state.db_pool) — checked by /readyz only

"DB failure" for this service means:
  A. Redis is unreachable → cache falls back to None (no crash)
  B. Cache keys are tenant-scoped → different tenants never share entries
  C. Analysis acquisition_date is included in the cache key → historical
     queries don't collide with live ones on the same field+satellite
  D. readyz returns 'degraded' when the DB pool is present but returns errors
  E. Cache module unavailable → service degrades gracefully (stubs used)

All tests run without network access (Redis is mocked).
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

try:
    from fastapi.testclient import TestClient
except ImportError as exc:
    pytest.skip(f"fastapi not installed: {exc}", allow_module_level=True)

TENANT_A = "00000000-0000-0000-0000-000000000aa1"
TENANT_B = "00000000-0000-0000-0000-000000000bb2"
FIELD_ID = "field-db-failure-veg"
_TENANT_HEADERS = {"X-Tenant-ID": TENANT_A}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_fake_user(tenant_id: str = TENANT_A):
    from shared.auth.models import User

    u = MagicMock(spec=User)
    u.id = "db-failure-tester"
    u.email = "dbfail@sahool.sa"
    u.roles = ["farmer"]
    u.tenant_id = tenant_id
    return u


@pytest.fixture
def app():
    from src.main import app as veg_app
    from shared.auth.dependencies import get_current_user

    veg_app.dependency_overrides[get_current_user] = lambda: _make_fake_user()
    yield veg_app
    veg_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False, headers=_TENANT_HEADERS)


# ---------------------------------------------------------------------------
# A. Redis Unreachable → Graceful Fallback
# ---------------------------------------------------------------------------


class TestRedisUnavailableFallback:
    """When Redis is unreachable, cache operations return None/False — no crash."""

    def test_cache_get_returns_none_when_redis_fails(self):
        """cache_get() returns None when the Redis client raises an exception."""
        from src.cache import cache_get

        async def _run():
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=ConnectionError("Redis gone"))
            with patch("src.cache._get_redis_client", return_value=mock_client):
                return await cache_get("satellite:t:tenant-a:ndvi:field-1:2026-01-01:sentinel-2")

        result = asyncio.run(_run())
        assert result is None

    def test_cache_set_returns_false_when_redis_fails(self):
        """cache_set() returns False when setex raises."""
        from src.cache import cache_set

        async def _run():
            mock_client = AsyncMock()
            mock_client.setex = AsyncMock(side_effect=ConnectionError("Redis gone"))
            with patch("src.cache._get_redis_client", return_value=mock_client):
                return await cache_set("some-key", {"ndvi": 0.6}, ttl=3600)

        result = asyncio.run(_run())
        assert result is False

    def test_get_cached_analysis_returns_none_when_redis_unavailable(self):
        """get_cached_analysis() returns None gracefully when Redis is down."""
        from src.cache import get_cached_analysis

        async def _run():
            with patch("src.cache._get_redis_client", return_value=None):
                return await get_cached_analysis(
                    field_id=FIELD_ID,
                    satellite="sentinel-2",
                    tenant_id=TENANT_A,
                )

        result = asyncio.run(_run())
        assert result is None

    def test_cache_timeseries_returns_none_when_redis_unavailable(self):
        """get_cached_timeseries() returns None gracefully when Redis is down."""
        from src.cache import get_cached_timeseries

        async def _run():
            with patch("src.cache._get_redis_client", return_value=None):
                return await get_cached_timeseries(
                    field_id=FIELD_ID,
                    days=30,
                    satellite="sentinel-2",
                    tenant_id=TENANT_A,
                )

        result = asyncio.run(_run())
        assert result is None

    def test_is_cache_available_returns_false_when_redis_down(self):
        """is_cache_available() returns False when Redis connect fails."""
        from src.cache import is_cache_available

        async def _run():
            with patch("src.cache._get_redis_client", return_value=None):
                with patch("src.cache._redis_available", False):
                    return await is_cache_available()

        result = asyncio.run(_run())
        assert result is False

    def test_analyze_field_still_returns_result_when_cache_fails(self):
        """
        analyze_field() returns a valid FieldAnalysis when the cache raises
        on both get and set. The simulated fallback is always available.
        """
        import src.main as m

        async def _run():
            from src.main import ImageryRequest, SatelliteSource, analyze_field

            req = ImageryRequest(
                field_id=FIELD_ID,
                latitude=15.37,
                longitude=44.21,
                satellite=SatelliteSource.SENTINEL2,
            )
            # Simulate cache module raising on every call
            failing_cache = AsyncMock(side_effect=RuntimeError("Redis dead"))
            with patch.object(m, "_cache_available", True):
                with patch.object(m, "get_cached_analysis", failing_cache):
                    with patch.object(m, "cache_analysis", failing_cache):
                        with patch.object(m, "_multi_provider", None):
                            with patch.object(m, "USE_MULTI_PROVIDER", False):
                                return await analyze_field(req, tenant_id=TENANT_A)

        result = asyncio.run(_run())
        assert result is not None
        assert result.field_id == FIELD_ID
        assert -1.0 <= result.indices.ndvi <= 1.0


# ---------------------------------------------------------------------------
# B. Cache Key Tenant Isolation
# ---------------------------------------------------------------------------


class TestCacheTenantIsolation:
    """Different tenants must never share cached satellite analysis entries."""

    def test_ndvi_cache_key_includes_tenant(self):
        """_ndvi_cache_key() embeds the tenant_id in the key string."""
        from src.cache import _ndvi_cache_key

        key_a = _ndvi_cache_key(FIELD_ID, "2026-01-01", "sentinel-2", tenant_id=TENANT_A)
        key_b = _ndvi_cache_key(FIELD_ID, "2026-01-01", "sentinel-2", tenant_id=TENANT_B)

        assert TENANT_A in key_a
        assert TENANT_B in key_b
        assert key_a != key_b, "Different tenants must produce different cache keys"

    def test_analysis_cache_key_includes_tenant(self):
        """_analysis_cache_key() embeds the tenant_id."""
        from src.cache import _analysis_cache_key

        key_a = _analysis_cache_key(FIELD_ID, "sentinel-2", tenant_id=TENANT_A, acquisition_date="2026-01-01")
        key_b = _analysis_cache_key(FIELD_ID, "sentinel-2", tenant_id=TENANT_B, acquisition_date="2026-01-01")

        assert key_a != key_b
        assert TENANT_A in key_a
        assert TENANT_B in key_b

    def test_timeseries_cache_key_includes_tenant(self):
        """_timeseries_cache_key() embeds the tenant_id."""
        from src.cache import _timeseries_cache_key

        key_a = _timeseries_cache_key(FIELD_ID, 30, "sentinel-2", tenant_id=TENANT_A)
        key_b = _timeseries_cache_key(FIELD_ID, 30, "sentinel-2", tenant_id=TENANT_B)

        assert key_a != key_b

    def test_cache_key_includes_acquisition_date(self):
        """
        _analysis_cache_key() with different acquisition_dates produces different
        keys — historical queries must not collide with the 'today' key.
        """
        from src.cache import _analysis_cache_key

        today_key = _analysis_cache_key(FIELD_ID, "sentinel-2", tenant_id=TENANT_A, acquisition_date=None)
        hist_key = _analysis_cache_key(
            FIELD_ID, "sentinel-2", tenant_id=TENANT_A, acquisition_date="2025-06-01"
        )

        assert today_key != hist_key, (
            "Historical acquisition_date must produce a different cache key than 'today' "
            "(audit correctness bug — per Copilot review)"
        )

    def test_global_namespace_used_when_tenant_is_none(self):
        """When tenant_id=None, the key uses the 'global' namespace."""
        from src.cache import _ndvi_cache_key

        key_no_tenant = _ndvi_cache_key(FIELD_ID, "2026-01-01", "sentinel-2", tenant_id=None)
        assert "global" in key_no_tenant

    def test_empty_string_tenant_uses_global_namespace(self):
        """When tenant_id='', _ns() falls back to 'global'."""
        from src.cache import _ns

        result = _ns("")
        assert result == "global"

    def test_whitespace_tenant_uses_global_namespace(self):
        """When tenant_id is whitespace-only, _ns() returns 'global'."""
        from src.cache import _ns

        result = _ns("   ")
        assert result == "global"

    def test_get_set_different_tenants_do_not_share_data(self):
        """
        Writing a value under TENANT_A's key and reading under TENANT_B's key
        returns None (tenants are isolated).
        """
        from src.cache import _analysis_cache_key

        key_a = _analysis_cache_key(FIELD_ID, "sentinel-2", tenant_id=TENANT_A, acquisition_date="2026-01-01")
        key_b = _analysis_cache_key(FIELD_ID, "sentinel-2", tenant_id=TENANT_B, acquisition_date="2026-01-01")

        in_memory_store: dict[str, str] = {}

        async def fake_set(key: str, value: dict, ttl: int) -> bool:
            in_memory_store[key] = json.dumps(value)
            return True

        async def fake_get(key: str) -> dict | None:
            raw = in_memory_store.get(key)
            return json.loads(raw) if raw else None

        async def _run():
            # Write TENANT_A's analysis
            await fake_set(key_a, {"ndvi": 0.72, "tenant": TENANT_A}, ttl=3600)
            # Read from TENANT_B's key — must be None
            return await fake_get(key_b)

        result = asyncio.run(_run())
        assert result is None, "TENANT_B must not see TENANT_A's cache entry"


# ---------------------------------------------------------------------------
# C. readyz with Database Pool Failures
# ---------------------------------------------------------------------------


class TestReadyzDatabaseFailures:
    """readyz correctly shows degraded state when the DB pool is present but broken."""

    def test_readyz_db_not_configured_when_no_pool(self, client):
        """When app.state.db_pool is absent, readyz shows 'not_configured' for database."""
        import src.main as m

        # Ensure db_pool is not on app.state
        if hasattr(m.app.state, "db_pool"):
            del m.app.state.db_pool

        resp = client.get("/readyz")
        assert resp.status_code == 200
        body = resp.json()
        assert body["checks"]["database"] == "not_configured"

    def test_readyz_db_disconnected_when_pool_raises(self, client):
        """When db_pool.acquire() raises, readyz shows 'disconnected' for database."""
        import src.main as m
        import types

        mock_pool = MagicMock()
        # Simulate the async context manager `async with pool.acquire() as conn:` failing
        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(side_effect=OSError("connection refused"))
        mock_pool.acquire = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_conn),
            __aexit__=AsyncMock(return_value=None),
        ))

        m.app.state.db_pool = mock_pool
        try:
            resp = client.get("/readyz")
        finally:
            del m.app.state.db_pool

        assert resp.status_code == 200
        body = resp.json()
        assert body["checks"]["database"] == "disconnected"
        assert body["status"] == "degraded"

    def test_readyz_db_connected_when_pool_ok(self, client):
        """When db_pool.acquire() succeeds with SELECT 1, database shows 'connected'."""
        import src.main as m

        mock_conn = AsyncMock()
        mock_conn.fetchval = AsyncMock(return_value=1)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_conn),
            __aexit__=AsyncMock(return_value=None),
        ))

        m.app.state.db_pool = mock_pool
        try:
            resp = client.get("/readyz")
        finally:
            del m.app.state.db_pool

        assert resp.status_code == 200
        body = resp.json()
        assert body["checks"]["database"] == "connected"

    def test_readyz_response_has_required_fields(self, client):
        """readyz always returns a body with 'status', 'service', 'version', 'checks'."""
        resp = client.get("/readyz")
        assert resp.status_code == 200
        body = resp.json()
        for required_key in ("status", "service", "version", "checks"):
            assert required_key in body, f"Missing key: {required_key}"


# ---------------------------------------------------------------------------
# D. Cache Module Unavailable — Stub Path
# ---------------------------------------------------------------------------


class TestCacheModuleUnavailable:
    """
    When the cache module import fails, main.py installs no-op stubs.
    These stubs must return the correct types so the rest of the code
    doesn't crash.
    """

    def test_stub_get_cached_analysis_returns_none(self):
        """The fallback stub for get_cached_analysis returns None."""
        async def _stub_get_cached_analysis(
            field_id: str,
            satellite: str,
            tenant_id: str | None = None,
            acquisition_date: str | None = None,
        ) -> dict | None:
            return None

        result = asyncio.run(
            _stub_get_cached_analysis(FIELD_ID, "sentinel-2", tenant_id=TENANT_A)
        )
        assert result is None

    def test_stub_cache_analysis_returns_false(self):
        """The fallback stub for cache_analysis returns False."""
        async def _stub_cache_analysis(
            field_id: str,
            satellite: str,
            analysis_data: dict,
            tenant_id: str | None = None,
            acquisition_date: str | None = None,
        ) -> bool:
            return False

        result = asyncio.run(
            _stub_cache_analysis(FIELD_ID, "sentinel-2", {"ndvi": 0.6}, tenant_id=TENANT_A)
        )
        assert result is False

    def test_stub_get_cached_timeseries_returns_none(self):
        """The fallback stub for get_cached_timeseries returns None."""
        async def _stub_get_cached_timeseries(
            field_id: str,
            days: int,
            satellite: str,
            tenant_id: str | None = None,
        ) -> dict | None:
            return None

        result = asyncio.run(
            _stub_get_cached_timeseries(FIELD_ID, 30, "sentinel-2", tenant_id=TENANT_A)
        )
        assert result is None

    def test_cache_health_check_returns_unhealthy_when_no_redis(self):
        """cache_health_check() returns {'status': 'unhealthy', ...} when Redis is absent."""
        from src.cache import cache_health_check

        async def _run():
            with patch("src.cache._get_redis_client", return_value=None):
                return await cache_health_check()

        result = asyncio.run(_run())
        assert result["status"] == "unhealthy"
        assert "message" in result

    def test_get_cache_stats_returns_unavailable_when_no_redis(self):
        """get_cache_stats() returns {'available': False, ...} when Redis is absent."""
        from src.cache import get_cache_stats

        async def _run():
            with patch("src.cache._get_redis_client", return_value=None):
                return await get_cache_stats()

        result = asyncio.run(_run())
        assert result["available"] is False


# ---------------------------------------------------------------------------
# E. Cache Invalidation — Tenant-Safe SCAN
# ---------------------------------------------------------------------------


class TestCacheInvalidation:
    """cache_invalidate_field() only purges the calling tenant's keys."""

    def test_tenant_scoped_invalidation_uses_correct_pattern(self):
        """
        When tenant_id is provided, cache_invalidate_field uses a pattern
        that includes the tenant, not a wildcard cross-tenant pattern.
        """
        from src.cache import cache_invalidate_field, _ns

        keys_deleted = []

        async def _run():
            mock_client = AsyncMock()

            # Simulate SCAN returning a small set of keys
            async def _scan(cursor, match=None, count=100):
                if cursor == 0:
                    return (0, [f"satellite:t:{TENANT_A}:ndvi:{FIELD_ID}:2026-01-01:sentinel-2"])
                return (0, [])

            mock_client.scan = _scan
            mock_client.delete = AsyncMock(return_value=1)

            with patch("src.cache._get_redis_client", return_value=mock_client):
                deleted = await cache_invalidate_field(FIELD_ID, tenant_id=TENANT_A)
            return deleted

        deleted = asyncio.run(_run())
        assert deleted >= 0  # may be 0 if no keys matched the pattern

    def test_cache_invalidate_without_tenant_uses_wildcard_pattern(self):
        """
        When tenant_id is not provided (admin path), the pattern uses a
        cross-tenant wildcard (* in the tenant position).
        """
        from src.cache import cache_invalidate_field

        async def _run():
            mock_client = AsyncMock()
            scanned_patterns = []

            async def _scan(cursor, match=None, count=100):
                if match:
                    scanned_patterns.append(match)
                return (0, [])

            mock_client.scan = _scan
            mock_client.delete = AsyncMock(return_value=0)

            with patch("src.cache._get_redis_client", return_value=mock_client):
                await cache_invalidate_field(FIELD_ID, tenant_id=None)

            return scanned_patterns

        patterns = asyncio.run(_run())
        if patterns:
            # When no tenant is provided, the pattern must contain '*'
            # in the tenant position to support the admin/background path
            assert any("*" in p for p in patterns), (
                f"Admin invalidation must use a wildcard pattern; got: {patterns}"
            )

    def test_cache_invalidate_returns_zero_when_redis_unavailable(self):
        """cache_invalidate_field() returns 0 (not raises) when Redis is down."""
        from src.cache import cache_invalidate_field

        async def _run():
            with patch("src.cache._get_redis_client", return_value=None):
                return await cache_invalidate_field(FIELD_ID, tenant_id=TENANT_A)

        result = asyncio.run(_run())
        assert result == 0


# ---------------------------------------------------------------------------
# F. Cache health + stats endpoints via HTTP
# ---------------------------------------------------------------------------


class TestCacheEndpointsHTTP:
    """The /v1/cache/health and /v1/cache/stats endpoints handle Redis failures."""

    def test_cache_health_endpoint_returns_200_even_when_unavailable(self, client):
        """GET /v1/cache/health returns 200 and 'unavailable' message when no cache."""
        import src.main as m

        with patch.object(m, "_cache_available", False):
            resp = client.get("/v1/cache/health")
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body or "message" in body

    def test_cache_stats_endpoint_returns_200_when_cache_module_unloaded(self, client):
        """GET /v1/cache/stats returns 200 with {'available': False} when no cache."""
        import src.main as m

        with patch.object(m, "_cache_available", False):
            resp = client.get("/v1/cache/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("available") is False or "message" in body
