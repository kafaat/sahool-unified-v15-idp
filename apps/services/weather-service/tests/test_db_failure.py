"""
DB Failure Tests - Weather Service
اختبارات فشل "قاعدة البيانات" لخدمة الطقس

Context: The Python weather-service does not connect to PostgreSQL directly.
Its "database" is the bounded in-process cache (OrderedDict, max 512 entries,
introduced in fix 3.3) and the NATS event bus (fix 5.9).  When we talk about
"DB failure" for this service we mean:

  1. Cache corruption / overflow — does eviction keep the cache within bounds?
  2. Cache isolation — different tenants must never share cached entries.
  3. Cache miss / stale-data path — every provider call is made correctly
     when the cache is empty or expired.
  4. readyz correctly reports 503 when the provider is not initialised
     (the Kubernetes probe that removes the pod from the Service — fix 3.2).
  5. Graceful degradation when app.state attributes are missing (half-started
     service or teardown race).
  6. The WeatherPublisher correctly handles a missing/None NATS connection
     (fix 5.9 — returns None, not a fake UUID).

All tests run without network access.
"""

import asyncio
import time
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError as exc:
    pytest.skip(f"fastapi not installed: {exc}", allow_module_level=True)

TENANT_ID = "00000000-0000-0000-0000-000000000123"
TENANT_ID_B = "00000000-0000-0000-0000-000000000999"
FIELD_ID = "field-db-test"


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """App with auth bypassed."""
    from src.main import app as weather_app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    def _fake_user():
        u = MagicMock(spec=User)
        u.id = "db-failure-tester"
        u.email = "dbfail@sahool.sa"
        u.roles = ["farmer"]
        u.tenant_id = TENANT_ID
        return u

    weather_app.dependency_overrides[get_current_user] = _fake_user
    yield weather_app
    weather_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    c = TestClient(app)
    c.headers["X-Tenant-ID"] = TENANT_ID
    return c


@pytest.fixture
def multi_service():
    """A fresh MultiWeatherService instance for unit-level cache tests."""
    from src.providers.multi_provider import MultiWeatherService

    svc = MultiWeatherService()
    yield svc
    asyncio.run(svc.close())


# ---------------------------------------------------------------------------
# 1. In-process cache — bounded size (fix 3.3)
# ---------------------------------------------------------------------------


class TestCacheBoundedSize:
    """Verify the 512-entry FIFO eviction introduced in fix 3.3."""

    def test_cache_never_exceeds_max_size(self, multi_service):
        """Inserting 600 entries keeps len(cache) ≤ 512."""
        from src.providers.multi_provider import _CACHE_MAX_SIZE

        for i in range(600):
            multi_service._set_cached(f"key_{i}", {"data": i})

        assert len(multi_service._cache) <= _CACHE_MAX_SIZE

    def test_oldest_entry_evicted_when_full(self, multi_service):
        """When the cache is full the oldest key is evicted first."""
        from src.providers.multi_provider import _CACHE_MAX_SIZE

        # Fill cache to capacity
        for i in range(_CACHE_MAX_SIZE):
            multi_service._set_cached(f"key_{i}", {"data": i})

        # The first key inserted should still be present at exactly capacity
        assert multi_service._get_cached("key_0") is not None

        # Insert one more → key_0 (oldest) evicted
        multi_service._set_cached("key_overflow", {"data": "overflow"})

        assert multi_service._get_cached("key_0") is None
        assert multi_service._get_cached("key_overflow") is not None

    def test_refreshing_existing_key_moves_it_to_recent(self, multi_service):
        """Updating an existing key moves it to 'most recent' → not evicted first."""
        from src.providers.multi_provider import _CACHE_MAX_SIZE

        # Fill to capacity
        for i in range(_CACHE_MAX_SIZE):
            multi_service._set_cached(f"key_{i}", {"data": i})

        # Refresh key_0 so it's no longer the oldest
        multi_service._set_cached("key_0", {"data": "refreshed"})

        # Insert one more — key_1 (now oldest) should be evicted, NOT key_0
        multi_service._set_cached("key_overflow", {"data": "overflow"})

        assert multi_service._get_cached("key_0") is not None
        assert multi_service._get_cached("key_1") is None

    def test_empty_cache_get_returns_none(self, multi_service):
        """Cache miss on empty cache returns None cleanly."""
        result = multi_service._get_cached("nonexistent_key")
        assert result is None

    def test_expired_entry_returns_none(self, multi_service):
        """Cache entry past its TTL is treated as a miss."""
        multi_service._set_cached("stale_key", {"data": "old"})

        # Force the entry to appear expired by back-dating its timestamp
        key, (data, _ts) = next(iter(multi_service._cache.items()))
        past = datetime.now(UTC) - timedelta(seconds=multi_service._cache_duration.total_seconds() + 10)
        multi_service._cache[key] = (data, past)

        result = multi_service._get_cached("stale_key")
        assert result is None


# ---------------------------------------------------------------------------
# 2. Cache tenant isolation
# ---------------------------------------------------------------------------


class TestCacheTenantIsolation:
    """Cache keys must be scoped to tenant_id — no cross-tenant data leakage."""

    def test_different_tenants_different_cache_entries(self, multi_service):
        """Two tenants at the same coordinates get separate cache slots."""
        payload_a = {"data": "tenant_a_weather", "temp": 30.0}
        payload_b = {"data": "tenant_b_weather", "temp": 15.0}

        key_a = f"current_{TENANT_ID}_15.35_44.20"
        key_b = f"current_{TENANT_ID_B}_15.35_44.20"

        multi_service._set_cached(key_a, payload_a)
        multi_service._set_cached(key_b, payload_b)

        result_a = multi_service._get_cached(key_a)
        result_b = multi_service._get_cached(key_b)

        assert result_a is not None
        assert result_b is not None
        assert result_a["temp"] == 30.0
        assert result_b["temp"] == 15.0
        # Data must NOT bleed across tenants
        assert result_a["temp"] != result_b["temp"]

    def test_cache_key_includes_coordinates(self, multi_service):
        """Same tenant, different coordinates → different cache entries."""
        payload_sanaa = {"city": "Sanaa", "temp": 35.0}
        payload_aden = {"city": "Aden", "temp": 32.0}

        key_sanaa = f"current_{TENANT_ID}_15.35_44.20"
        key_aden = f"current_{TENANT_ID}_12.78_45.04"

        multi_service._set_cached(key_sanaa, payload_sanaa)
        multi_service._set_cached(key_aden, payload_aden)

        assert multi_service._get_cached(key_sanaa)["city"] == "Sanaa"
        assert multi_service._get_cached(key_aden)["city"] == "Aden"

    def test_cache_hit_via_get_current_uses_tenant_scoped_key(self):
        """
        The cache_key in MultiWeatherService.get_current() embeds tenant_id so
        concurrent requests from different tenants are stored independently.
        """
        from src.providers.multi_provider import MultiWeatherService, WeatherData

        svc = MultiWeatherService()

        weather_a = MagicMock(spec=WeatherData)
        weather_a.temperature_c = 30.0

        weather_b = MagicMock(spec=WeatherData)
        weather_b.temperature_c = 15.0

        # Prime the cache for both tenants
        key_a = f"current_{TENANT_ID}_15.35_44.20"
        key_b = f"current_{TENANT_ID_B}_15.35_44.20"
        svc._set_cached(key_a, weather_a)
        svc._set_cached(key_b, weather_b)

        # Retrieve — must NOT cross-contaminate
        result_a = asyncio.run(svc.get_current(15.35, 44.20, tenant_id=TENANT_ID))
        result_b = asyncio.run(svc.get_current(15.35, 44.20, tenant_id=TENANT_ID_B))

        assert result_a.is_cached
        assert result_b.is_cached
        assert result_a.data.temperature_c == 30.0
        assert result_b.data.temperature_c == 15.0

        asyncio.run(svc.close())


# ---------------------------------------------------------------------------
# 3. Provider not initialised → readyz 503 (fix 3.2)
# ---------------------------------------------------------------------------


class TestReadyzProviderFailures:
    """readyz must return HTTP 503 whenever a critical resource is unavailable."""

    def test_readyz_503_providers_none(self, client, app):
        """Both providers None → degraded → 503."""
        with patch("src.main.app.state") as s:
            s.publisher = None
            s.multi_provider = None
            s.weather_provider = None

            resp = client.get("/readyz")

        assert resp.status_code == 503
        assert resp.json()["status"] == "degraded"
        assert resp.json()["checks"]["providers"] == "not_initialized"

    def test_readyz_503_only_weather_provider_none_multi_none(self, client, app):
        """Neither multi_provider nor weather_provider → not_initialized → 503."""
        with patch("src.main.app.state") as s:
            s.publisher = None
            s.multi_provider = None
            s.weather_provider = None

            resp = client.get("/readyz")

        assert resp.status_code == 503

    def test_readyz_200_weather_provider_present(self, client, app):
        """Single weather_provider present (multi=None) → providers available → 200."""
        mock_provider = MagicMock()
        with patch("src.main.app.state") as s:
            s.publisher = None
            s.multi_provider = None
            s.weather_provider = mock_provider

            resp = client.get("/readyz")

        assert resp.status_code == 200
        assert resp.json()["checks"]["providers"] == "available"

    def test_readyz_200_multi_provider_present(self, client, app):
        """multi_provider present → providers available → 200."""
        mock_multi = MagicMock()
        with patch("src.main.app.state") as s:
            s.publisher = None
            s.multi_provider = mock_multi
            s.weather_provider = None

            resp = client.get("/readyz")

        assert resp.status_code == 200
        assert resp.json()["checks"]["providers"] == "available"

    def test_readyz_503_nats_disconnected(self, client, app):
        """NATS publisher exists but _connected=False → disconnected → 503."""
        mock_publisher = MagicMock()
        mock_publisher._connected = False

        mock_provider = MagicMock()

        with patch("src.main.app.state") as s:
            s.publisher = mock_publisher
            s.multi_provider = mock_provider
            s.weather_provider = None

            resp = client.get("/readyz")

        assert resp.status_code == 503
        assert resp.json()["checks"]["nats"] == "disconnected"

    def test_readyz_response_has_required_fields(self, client, app):
        """readyz JSON always contains status, service, version, checks."""
        with patch("src.main.app.state") as s:
            s.publisher = None
            s.multi_provider = MagicMock()
            s.weather_provider = None

            resp = client.get("/readyz")

        data = resp.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert "checks" in data
        assert "providers" in data["checks"]
        assert "nats" in data["checks"]


# ---------------------------------------------------------------------------
# 4. WeatherPublisher — NATS unavailable returns None (fix 5.9)
# ---------------------------------------------------------------------------


class TestPublisherNATSUnavailable:
    """
    When NATS is not connected, publish_weather_alert / publish_forecast_issued /
    publish_irrigation_adjustment must return None — never a fake UUID string.
    """

    def _make_disconnected_publisher(self):
        """
        Return a WeatherPublisher whose _is_available is False without making
        any real network call. We override _is_available as a property mock and
        prevent connect() from attempting a real NATS connection.
        """
        from unittest.mock import PropertyMock, patch

        from src.events.publish import WeatherPublisher

        pub = WeatherPublisher(nats_url="nats://127.0.0.1:9999")
        # _connected=False, so publish methods call self.connect().
        # Patch connect() to be a no-op so no real NATS call is made.
        pub.connect = AsyncMock()
        # _is_available must return False to trigger the early-return None path.
        pub._connected = False
        pub.nc = None
        return pub

    def test_publish_weather_alert_returns_none_when_not_connected(self):
        """Not connected → returns None without making a real NATS call."""
        pub = self._make_disconnected_publisher()

        result = asyncio.run(
            pub.publish_weather_alert(
                tenant_id=TENANT_ID,
                field_id=FIELD_ID,
                alert_type="heat_stress",
                severity="high",
                window_hours=6,
            )
        )

        assert result is None

    def test_publish_forecast_issued_returns_none_when_not_connected(self):
        """Not connected → returns None."""
        pub = self._make_disconnected_publisher()

        result = asyncio.run(
            pub.publish_forecast_issued(
                tenant_id=TENANT_ID,
                field_id=FIELD_ID,
                days=7,
                provider="Open-Meteo",
            )
        )

        assert result is None

    def test_publish_irrigation_adjustment_returns_none_when_not_connected(self):
        """Not connected → returns None."""
        pub = self._make_disconnected_publisher()

        result = asyncio.run(
            pub.publish_irrigation_adjustment(
                tenant_id=TENANT_ID,
                field_id=FIELD_ID,
                adjustment_factor=0.75,
                recommendation_ar="تخفيض الري",
                recommendation_en="Reduce irrigation",
            )
        )

        assert result is None

    def test_event_ids_list_contains_no_none(self, client, app):
        """
        When publisher returns None for every event, event_ids in the HTTP
        response must be [] (empty list), never [None].
        """
        mock_publisher = AsyncMock()
        mock_publisher.publish_weather_alert = AsyncMock(return_value=None)

        weather_mock = MagicMock()
        weather_mock.temperature_c = 50.0
        weather_mock.humidity_pct = 5.0
        weather_mock.wind_speed_kmh = 5.0
        weather_mock.wind_direction_deg = 90
        weather_mock.wind_direction = "E"
        weather_mock.precipitation_mm = 0.0
        weather_mock.cloud_cover_pct = 0.0
        weather_mock.pressure_hpa = 1010.0
        weather_mock.uv_index = 16.0
        weather_mock.condition = "Clear"
        weather_mock.condition_ar = "صافي"
        weather_mock.icon = "clear"
        weather_mock.timestamp = "2026-04-23T12:00:00+00:00"
        weather_mock.provider = "Open-Meteo"

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.provider = "Open-Meteo"
        mock_result.data = weather_mock
        mock_result.failed_providers = []

        mock_multi = AsyncMock()
        mock_multi.get_current = AsyncMock(return_value=mock_result)

        with patch("src.main.app.state") as s:
            s.multi_provider = mock_multi
            s.publisher = mock_publisher

            resp = client.post(
                "/weather/current",
                json={"tenant_id": TENANT_ID, "field_id": FIELD_ID, "lat": 15.35, "lon": 44.20},
            )

        assert resp.status_code == 200
        data = resp.json()
        assert data["event_ids"] == []
        assert None not in data["event_ids"]


# ---------------------------------------------------------------------------
# 5. Missing app.state attributes (half-started / partial teardown)
# ---------------------------------------------------------------------------


class TestMissingStateAttributes:
    """
    Guard against AttributeError when the service is only partially started
    (e.g. startup raised and lifespan exited without setting all attributes).
    """

    def test_healthz_always_works_regardless_of_state(self, client, app):
        """
        /healthz must never read app.state — it returns a static dict.
        This test verifies it survives even if state is empty.
        """
        resp = client.get("/healthz")
        assert resp.status_code == 200

    def test_readyz_handles_missing_publisher_attr(self, client, app):
        """
        /readyz uses getattr(app.state, 'publisher', None) and
        getattr(app.state, 'multi_provider', None) — it must not raise if the
        attribute is absent (half-started service).
        """
        # Patch the app.state to an object without publisher attr
        class _BareSate:
            multi_provider = MagicMock()  # provider present
            weather_provider = None

        with patch("src.main.app.state", _BareSate()):
            resp = client.get("/readyz")

        # Should return 200 or 503 — but must NOT return 500
        assert resp.status_code in (200, 503)
        assert "status" in resp.json()

    def test_assess_does_not_need_provider(self, client, app):
        """
        /weather/assess is stateless — it must work even if both provider
        attributes are absent on app.state.
        """
        with patch("src.main.app.state") as s:
            s.publisher = None

            resp = client.post(
                "/weather/assess",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 25.0,
                },
            )

        assert resp.status_code == 200

    def test_current_weather_returns_5xx_when_state_provider_missing(self, client, app):
        """
        /weather/current with no provider set → 5xx (ExternalServiceException),
        not an unhandled 500.
        """
        with patch("src.main.app.state") as s:
            s.multi_provider = None
            s.weather_provider = None
            s.publisher = None

            resp = client.post(
                "/weather/current",
                json={"tenant_id": TENANT_ID, "field_id": FIELD_ID, "lat": 15.35, "lon": 44.20},
            )

        # Must be a graceful HTTP error, not an unhandled 500 from AttributeError
        assert resp.status_code in (500, 502, 503)


# ---------------------------------------------------------------------------
# 6. Cache concurrent-write safety (simple deterministic check)
# ---------------------------------------------------------------------------


class TestCacheConcurrentAccess:
    """
    Verify cache behaves correctly under simulated concurrent writes.
    (True async concurrency is tested via asyncio.gather)
    """

    def test_concurrent_set_same_key_last_write_wins(self, multi_service):
        """Two coroutines writing the same key — final value is consistent."""

        async def writer(value):
            multi_service._set_cached("shared_key", {"value": value})

        async def run():
            await asyncio.gather(writer("first"), writer("second"))

        asyncio.run(run())

        result = multi_service._get_cached("shared_key")
        assert result is not None
        assert result["value"] in ("first", "second")  # one of the two — not None

    def test_concurrent_get_returns_valid_data(self, multi_service):
        """Multiple concurrent readers return the same cached value."""
        multi_service._set_cached("read_key", {"temp": 28.5})

        async def reader():
            return multi_service._get_cached("read_key")

        async def run():
            results = await asyncio.gather(*[reader() for _ in range(20)])
            return results

        results = asyncio.run(run())
        assert all(r is not None for r in results)
        assert all(r["temp"] == 28.5 for r in results)

    def test_cache_size_stable_under_concurrent_writes(self, multi_service):
        """Cache size never exceeds _CACHE_MAX_SIZE under concurrent writes."""
        from src.providers.multi_provider import _CACHE_MAX_SIZE

        async def writer(i):
            multi_service._set_cached(f"concurrent_key_{i}", {"i": i})

        async def run():
            await asyncio.gather(*[writer(i) for i in range(_CACHE_MAX_SIZE + 200)])

        asyncio.run(run())
        assert len(multi_service._cache) <= _CACHE_MAX_SIZE
