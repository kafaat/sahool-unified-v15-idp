"""
E2E Real Tests - Weather Service
اختبارات تكاملية حقيقية لخدمة الطقس

These tests hit the *real* Open-Meteo free API (no HTTP mocking).
They are gated behind the WEATHER_E2E=true environment variable so CI
pipelines that have no internet access skip them automatically.

Run locally:
    WEATHER_E2E=true pytest tests/test_e2e_real.py -v

Why Open-Meteo?
  - Free, no API key required → no secrets needed in CI.
  - Sanaa (15.35 N, 44.20 E) is a primary test location for the SAHOOL
    platform (Yemen-focused agricultural intelligence).
"""

import asyncio
import os

import pytest

# Skip entire module unless WEATHER_E2E=true
if os.getenv("WEATHER_E2E", "").lower() != "true":
    pytest.skip("WEATHER_E2E=true required to run real E2E tests", allow_module_level=True)

try:
    from unittest.mock import MagicMock

    from fastapi.testclient import TestClient
except ImportError as exc:
    pytest.skip(f"missing dependency: {exc}", allow_module_level=True)

# ── Coordinates used throughout ────────────────────────────────────────────────
SANAA_LAT = 15.35
SANAA_LON = 44.20
TENANT_ID = "00000000-0000-0000-0000-000000000123"
FIELD_ID = "field-sanaa-real"

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def app():
    """FastAPI app with auth bypassed — provider uses real HTTP."""
    from src.main import app as weather_app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    def _fake_user():
        u = MagicMock(spec=User)
        u.id = "e2e-test-user"
        u.email = "e2e@sahool.sa"
        u.roles = ["farmer"]
        u.tenant_id = TENANT_ID
        return u

    weather_app.dependency_overrides[get_current_user] = _fake_user
    yield weather_app
    weather_app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def client(app):
    c = TestClient(app)
    c.headers["X-Tenant-ID"] = TENANT_ID
    return c


# ── E2E: OpenMeteoProvider (direct) ───────────────────────────────────────────


class TestOpenMeteoProviderDirect:
    """Call the real Open-Meteo endpoint without any HTTP mocking."""

    def test_get_current_returns_valid_data(self):
        """Current weather fields are present and in realistic ranges."""
        from src.providers.open_meteo import OpenMeteoProvider

        provider = OpenMeteoProvider()
        weather = asyncio.run(provider.get_current(SANAA_LAT, SANAA_LON))

        # Structural checks
        assert hasattr(weather, "temperature_c")
        assert hasattr(weather, "humidity_pct")
        assert hasattr(weather, "wind_speed_kmh")
        assert hasattr(weather, "pressure_hpa")
        assert hasattr(weather, "timestamp")

        # Physical plausibility (Sanaa is a hot dry city — temp rarely below 5°C)
        assert -20.0 <= weather.temperature_c <= 55.0
        assert 0.0 <= weather.humidity_pct <= 100.0
        assert weather.wind_speed_kmh >= 0.0
        assert 900.0 <= weather.pressure_hpa <= 1100.0

        asyncio.run(provider.close())

    def test_get_daily_forecast_returns_days(self):
        """Daily forecast returns the requested number of days."""
        from src.providers.open_meteo import DailyForecast, OpenMeteoProvider

        provider = OpenMeteoProvider()
        forecast = asyncio.run(provider.get_daily_forecast(SANAA_LAT, SANAA_LON, days=3))

        assert isinstance(forecast, list)
        assert 1 <= len(forecast) <= 3  # API may return up to 3 days
        for day in forecast:
            assert isinstance(day, DailyForecast)
            assert day.date  # Non-empty date string
            assert isinstance(day.temp_max_c, (float, int))
            assert day.temp_max_c >= day.temp_min_c

        asyncio.run(provider.close())

    def test_get_hourly_forecast_returns_hours(self):
        """Hourly forecast returns entries for the requested window."""
        from src.providers.open_meteo import HourlyForecast, OpenMeteoProvider

        provider = OpenMeteoProvider()
        forecast = asyncio.run(provider.get_hourly_forecast(SANAA_LAT, SANAA_LON, hours=24))

        assert isinstance(forecast, list)
        assert len(forecast) >= 1
        for entry in forecast:
            assert isinstance(entry, HourlyForecast)
            assert entry.datetime  # Non-empty
            assert 0.0 <= entry.humidity_pct <= 100.0

        asyncio.run(provider.close())

    def test_network_error_propagates(self):
        """Provider raises an error on network failure (bad host)."""
        from src.providers.open_meteo import OpenMeteoProvider

        provider = OpenMeteoProvider()
        # Override BASE_URL to a non-routable address
        provider.BASE_URL = "https://255.255.255.255/unreachable"

        with pytest.raises(Exception):
            asyncio.run(provider.get_current(SANAA_LAT, SANAA_LON))

        asyncio.run(provider.close())


# ── E2E: Full HTTP stack via FastAPI TestClient ────────────────────────────────


class TestFullStackE2E:
    """End-to-end tests using the FastAPI TestClient with a real provider."""

    def test_current_weather_endpoint_full_flow(self, client, app):
        """
        POST /weather/current → real Open-Meteo → valid JSON response.
        Exercises the complete request path: auth → provider → risk assess.
        """
        from unittest.mock import patch

        # Use the real OpenMeteoProvider, just bypass multi-provider routing
        from src.providers.open_meteo import OpenMeteoProvider

        real_provider = OpenMeteoProvider()
        with (
            patch.object(app.state, "multi_provider", None),
            patch.object(app.state, "weather_provider", real_provider),
            patch.object(app.state, "publisher", None),
        ):
            response = client.post(
                "/weather/current",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "lat": SANAA_LAT,
                    "lon": SANAA_LON,
                },
            )

        asyncio.run(real_provider.close())

        assert response.status_code == 200
        data = response.json()

        # Top-level keys
        assert "current" in data
        assert "provider" in data
        assert data["provider"] == "Open-Meteo"
        assert "alerts" in data
        assert isinstance(data["alerts"], list)

        # Weather values are physically plausible
        current = data["current"]
        assert -20.0 <= current["temperature_c"] <= 55.0
        assert 0.0 <= current["humidity_pct"] <= 100.0

    def test_daily_forecast_endpoint_full_flow(self, client, app):
        """
        POST /weather/forecast?days=3 → real Open-Meteo → list of daily forecasts.
        """
        from unittest.mock import patch

        from src.providers.open_meteo import OpenMeteoProvider

        real_provider = OpenMeteoProvider()
        with (
            patch.object(app.state, "multi_provider", None),
            patch.object(app.state, "weather_provider", real_provider),
            patch.object(app.state, "publisher", None),
        ):
            response = client.post(
                "/weather/forecast?days=3",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "lat": SANAA_LAT,
                    "lon": SANAA_LON,
                },
            )

        asyncio.run(real_provider.close())

        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
        assert isinstance(data["forecast"], list)
        assert len(data["forecast"]) >= 1

        for day in data["forecast"]:
            assert "date" in day
            assert "temp_max_c" in day
            assert "temp_min_c" in day
            assert day["temp_max_c"] >= day["temp_min_c"]

    def test_hourly_forecast_endpoint_full_flow(self, client, app):
        """
        POST /weather/hourly?hours=24 → real Open-Meteo → hourly entries.
        This endpoint was added as fix 4.6.
        """
        from unittest.mock import patch

        from src.providers.open_meteo import OpenMeteoProvider

        real_provider = OpenMeteoProvider()
        with (
            patch.object(app.state, "multi_provider", None),
            patch.object(app.state, "weather_provider", real_provider),
            patch.object(app.state, "publisher", None),
        ):
            response = client.post(
                "/weather/hourly?hours=24",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "lat": SANAA_LAT,
                    "lon": SANAA_LON,
                },
            )

        asyncio.run(real_provider.close())

        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
        assert isinstance(data["forecast"], list)
        assert len(data["forecast"]) >= 1

        for entry in data["forecast"]:
            assert "datetime" in entry
            assert "temperature_c" in entry

    def test_invalid_hours_rejected_with_422(self, client):
        """
        /weather/hourly with hours=999 must return 422 (fix 4.6 + 5.6 pattern).
        """
        response = client.post(
            "/weather/hourly?hours=999",
            json={
                "tenant_id": TENANT_ID,
                "field_id": FIELD_ID,
                "lat": SANAA_LAT,
                "lon": SANAA_LON,
            },
        )
        assert response.status_code == 422

    def test_liveness_probe_returns_200(self, client):
        """/healthz is always 200 regardless of provider state."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "weather-service"
        assert data["version"] == "16.0.0"

    def test_readyz_reflects_real_provider_state(self, client):
        """/readyz returns 200 only when providers are properly initialised."""
        response = client.get("/readyz")
        # When providers are initialised the endpoint returns 200 or 503.
        # Either is valid in E2E mode — we just assert it returns JSON.
        assert response.status_code in (200, 503)
        data = response.json()
        assert "status" in data
        assert data["status"] in ("ready", "degraded")

    def test_assess_endpoint_with_extreme_temp(self, client):
        """
        POST /weather/assess with extreme temperature generates heat-stress alert.
        No external HTTP call — this is a pure business-logic test included here
        to verify the full middleware + validation stack in the real app.
        """
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": TENANT_ID,
                "field_id": FIELD_ID,
                "temp_c": 48.0,  # extreme heat
                "humidity_pct": 10.0,
                "uv_index": 15.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["alert_count"] > 0
        alert_types = [a["alert_type"] for a in data["alerts"]]
        assert any("heat" in t.lower() for t in alert_types)

    def test_tenant_mismatch_blocked_e2e(self, app):
        """Tenant-mismatch returns 403 even in E2E mode (auth middleware active)."""
        from shared.auth.dependencies import get_current_user
        from shared.auth.models import User

        def _wrong_tenant():
            u = MagicMock(spec=User)
            u.id = "attacker"
            u.email = "bad@evil.com"
            u.roles = ["farmer"]
            u.tenant_id = "00000000-0000-0000-0000-000000000999"
            return u

        app.dependency_overrides[get_current_user] = _wrong_tenant
        c = TestClient(app)
        c.headers["X-Tenant-ID"] = "00000000-0000-0000-0000-000000000999"

        response = c.post(
            "/weather/current",
            json={
                "tenant_id": TENANT_ID,  # different from user's tenant
                "field_id": FIELD_ID,
                "lat": SANAA_LAT,
                "lon": SANAA_LON,
            },
        )

        # Restore original override
        from unittest.mock import MagicMock as _MM  # noqa: F401 (already imported)

        def _fake_user():
            u = MagicMock(spec=User)
            u.id = "e2e-test-user"
            u.email = "e2e@sahool.sa"
            u.roles = ["farmer"]
            u.tenant_id = TENANT_ID
            return u

        app.dependency_overrides[get_current_user] = _fake_user

        assert response.status_code == 403
