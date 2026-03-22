"""
Tests for Weather Service API Endpoints
Tests all FastAPI endpoints using TestClient with mocked dependencies.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

# Mock NATS before importing main
with patch("src.events.publish.NATS"), \
     patch("src.events.get_publisher", new_callable=AsyncMock, return_value=None):
    from src.main import app, _enforce_tenant
    from src.providers.open_meteo import DailyForecast, MockWeatherProvider, WeatherData


# ── Auth fixture ──────────────────────────────────────────────────────────────

def _make_user(tenant_id="tenant-1"):
    """Create a mock User for dependency override."""
    user = MagicMock()
    user.id = "user-1"
    user.tenant_id = tenant_id
    user.email = "farmer@sahool.io"
    user.role = "farmer"
    return user


@pytest.fixture()
def client():
    """TestClient with mocked auth and providers."""
    from shared.auth.dependencies import get_current_user

    mock_user = _make_user()
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Set up mock providers on app state
    app.state.weather_provider = MockWeatherProvider()
    app.state.multi_provider = None
    app.state.publisher = None

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def client_with_publisher():
    """TestClient with mocked publisher for event tests."""
    from shared.auth.dependencies import get_current_user

    mock_user = _make_user()
    app.dependency_overrides[get_current_user] = lambda: mock_user

    mock_publisher = AsyncMock()
    mock_publisher.publish_weather_alert = AsyncMock(return_value="evt-123")
    mock_publisher.publish_forecast_issued = AsyncMock(return_value="evt-456")
    mock_publisher.publish_irrigation_adjustment = AsyncMock(return_value="evt-789")

    app.state.weather_provider = MockWeatherProvider()
    app.state.multi_provider = None
    app.state.publisher = mock_publisher

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


# ── Health Endpoints ──────────────────────────────────────────────────────────


class TestHealthEndpoints:
    def test_healthz(self, client):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "weather-service"
        assert data["version"] == "16.0.0"

    def test_readyz(self, client):
        resp = client.get("/readyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"


# ── Tenant Enforcement ────────────────────────────────────────────────────────


class TestTenantEnforcement:
    def test_enforce_tenant_same(self):
        """Matching tenant passes."""
        user = _make_user("t-1")
        _enforce_tenant(user, "t-1")  # no exception

    def test_enforce_tenant_mismatch(self):
        """Mismatched tenant raises 403."""
        from fastapi import HTTPException

        user = _make_user("t-1")
        with pytest.raises(HTTPException) as exc:
            _enforce_tenant(user, "t-999")
        assert exc.value.status_code == 403

    def test_enforce_tenant_none_passes(self):
        """User with no tenant_id can access any tenant."""
        user = _make_user()
        user.tenant_id = None
        _enforce_tenant(user, "any-tenant")  # no exception


# ── /weather/assess ───────────────────────────────────────────────────────────


class TestWeatherAssess:
    def test_assess_normal(self, client):
        resp = client.post("/weather/assess", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": 25.0,
            "humidity_pct": 50.0,
            "wind_speed_kmh": 10.0,
            "precipitation_mm": 0.0,
            "uv_index": 5.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["field_id"] == "field-1"
        assert "alerts" in data
        assert "alert_count" in data

    def test_assess_extreme_heat(self, client):
        resp = client.post("/weather/assess", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": 48.0,
            "humidity_pct": 20.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["alert_count"] >= 1
        types = [a["alert_type"] for a in data["alerts"]]
        assert "heat_stress" in types

    def test_assess_frost(self, client):
        resp = client.post("/weather/assess", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": -2.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        frost = [a for a in data["alerts"] if a["alert_type"] == "frost"]
        assert len(frost) >= 1

    def test_assess_with_publisher(self, client_with_publisher):
        resp = client_with_publisher.post("/weather/assess", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": 48.0,
            "humidity_pct": 20.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["published"] is True
        assert len(data["event_ids"]) >= 1


# ── /weather/current ──────────────────────────────────────────────────────────


class TestWeatherCurrent:
    def test_current_weather(self, client):
        resp = client.post("/weather/current", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "lat": 15.35,
            "lon": 44.21,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["field_id"] == "field-1"
        assert "current" in data
        assert data["current"]["temperature_c"] == 32.5  # from MockWeatherProvider
        assert data["provider"] == "Open-Meteo"

    def test_current_weather_with_alerts(self, client_with_publisher):
        """Mock provider returns 32.5C - no alerts at that temp, but test flow."""
        resp = client_with_publisher.post("/weather/current", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "lat": 15.35,
            "lon": 44.21,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "alerts" in data


# ── /weather/forecast ─────────────────────────────────────────────────────────


class TestWeatherForecast:
    def test_forecast_default_days(self, client):
        resp = client.post("/weather/forecast?days=3", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "lat": 15.35,
            "lon": 44.21,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["days"] == 3
        assert len(data["forecast"]) == 3
        assert data["provider"] == "Open-Meteo"

    def test_forecast_with_publisher(self, client_with_publisher):
        resp = client_with_publisher.post("/weather/forecast?days=2", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "lat": 15.35,
            "lon": 44.21,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["event_id"] is not None


# ── /weather/irrigation ───────────────────────────────────────────────────────


class TestIrrigation:
    def test_irrigation_normal(self, client):
        resp = client.post("/weather/irrigation", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": 28.0,
            "humidity_pct": 50.0,
            "wind_speed_kmh": 10.0,
            "precipitation_mm": 0.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "adjustment_factor" in data
        assert "recommendation_ar" in data
        assert "recommendation_en" in data
        assert data["published"] is False  # no publisher

    def test_irrigation_with_publisher(self, client_with_publisher):
        resp = client_with_publisher.post("/weather/irrigation", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": 28.0,
            "humidity_pct": 50.0,
            "wind_speed_kmh": 10.0,
            "precipitation_mm": 0.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["published"] is True
        assert data["event_id"] is not None


# ── /weather/heat-stress/{temp_c} ─────────────────────────────────────────────


class TestHeatStressEndpoint:
    def test_heat_stress_none(self, client):
        resp = client.get("/weather/heat-stress/25")
        assert resp.status_code == 200
        data = resp.json()
        assert data["at_risk"] is False
        assert data["severity"] == "none"

    def test_heat_stress_critical(self, client):
        resp = client.get("/weather/heat-stress/46")
        assert resp.status_code == 200
        data = resp.json()
        assert data["at_risk"] is True
        assert data["severity"] == "critical"

    def test_heat_stress_medium(self, client):
        resp = client.get("/weather/heat-stress/39")
        assert resp.status_code == 200
        data = resp.json()
        assert data["at_risk"] is True
        assert data["severity"] == "medium"


# ── /weather/providers ────────────────────────────────────────────────────────


class TestProvidersEndpoint:
    def test_providers_single(self, client):
        resp = client.get("/weather/providers")
        assert resp.status_code == 200
        data = resp.json()
        assert data["multi_provider_enabled"] is False
        assert data["total"] == 1


# ── /weather/evapotranspiration ───────────────────────────────────────────────


class TestETEndpoint:
    def test_et_calculation(self, client):
        resp = client.post("/weather/evapotranspiration", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": 30.0,
            "humidity_pct": 40.0,
            "wind_speed_kmh": 12.0,
            "solar_radiation_mj": 20.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        et = data["evapotranspiration"]
        assert et["et0_mm_day"] > 0
        assert "classification" in et
        assert "recommendation_ar" in et


# ── /weather/gdd ──────────────────────────────────────────────────────────────


class TestGDDEndpoint:
    def test_gdd_calculation(self, client):
        resp = client.post("/weather/gdd", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_max_c": 32.0,
            "temp_min_c": 20.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        gdd = data["growing_degree_days"]
        assert gdd["gdd_daily"] > 0
        assert "growth_rate" in gdd


# ── /weather/spray-window ────────────────────────────────────────────────────


class TestSprayWindowEndpoint:
    def test_spray_window(self, client):
        resp = client.post("/weather/spray-window", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": 22.0,
            "humidity_pct": 55.0,
            "wind_speed_kmh": 8.0,
            "precipitation_probability": 5.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        sw = data["spray_window"]
        assert sw["suitability"] == "excellent"
        assert sw["is_suitable"] is True


# ── /weather/frost-risk ──────────────────────────────────────────────────────


class TestFrostRiskEndpoint:
    def test_frost_risk_none(self, client):
        resp = client.post("/weather/frost-risk", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": 15.0,
            "humidity_pct": 50.0,
            "wind_speed_kmh": 10.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["frost_risk"]["risk_level"] == "none"

    def test_frost_risk_critical(self, client_with_publisher):
        resp = client_with_publisher.post("/weather/frost-risk", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": -6.0,
            "humidity_pct": 90.0,
            "wind_speed_kmh": 2.0,
            "cloud_cover_pct": 5.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["frost_risk"]["risk_level"] == "critical"
        assert data["frost_risk"]["frost_likely"] is True
        # Event should have been published for critical frost
        assert data["event_id"] is not None


# ── /weather/heat-stress (POST) ──────────────────────────────────────────────


class TestHeatStressPostEndpoint:
    def test_heat_stress_severe(self, client_with_publisher):
        resp = client_with_publisher.post("/weather/heat-stress", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": 42.0,
            "humidity_pct": 30.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        hs = data["heat_stress"]
        assert hs["stress_level"] in ("severe", "extreme")
        assert hs["is_critical"] is True
        assert data["event_id"] is not None

    def test_heat_stress_none(self, client):
        resp = client.post("/weather/heat-stress", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "temp_c": 20.0,
            "humidity_pct": 50.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["heat_stress"]["stress_level"] == "none"
        assert data["heat_stress"]["is_critical"] is False


# ── /weather/chill-hours ─────────────────────────────────────────────────────


class TestChillHoursEndpoint:
    def test_chill_hours_utah(self, client):
        # Hourly temps that accumulate chill hours (3-9 C range scores 1.0 in utah)
        temps = [5.0] * 48  # 48 hours at 5C
        resp = client.post("/weather/chill-hours", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "hourly_temps": temps,
            "model": "utah",
        })
        assert resp.status_code == 200
        data = resp.json()
        ch = data["chill_hours"]
        assert ch["chill_units"] == 48.0
        assert ch["model"] == "utah"
        assert ch["hours_analyzed"] == 48
        assert len(ch["satisfied_crops"]) >= 0

    def test_chill_hours_simple(self, client):
        temps = [3.0, 5.0, 8.0, 10.0, 6.0]
        resp = client.post("/weather/chill-hours", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "hourly_temps": temps,
            "model": "simple",
            "base_temp_c": 7.2,
        })
        assert resp.status_code == 200
        data = resp.json()
        ch = data["chill_hours"]
        assert ch["model"] == "simple"
        # temps <= 7.2: 3.0, 5.0, 6.0 => 3 chill hours
        assert ch["chill_units"] == 3

    def test_chill_hours_empty(self, client):
        resp = client.post("/weather/chill-hours", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "hourly_temps": [],
            "model": "utah",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["chill_hours"]["chill_units"] == 0


# ── /weather/drought-index ───────────────────────────────────────────────────


class TestDroughtIndexEndpoint:
    def test_drought_none(self, client):
        resp = client.post("/weather/drought-index", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "precipitation_mm": 100.0,
            "et0_mm": 80.0,
            "days": 30,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["drought_index"]["drought_level"] == "none"

    def test_drought_severe(self, client_with_publisher):
        resp = client_with_publisher.post("/weather/drought-index", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "precipitation_mm": 20.0,
            "et0_mm": 100.0,
            "days": 30,
        })
        assert resp.status_code == 200
        data = resp.json()
        di = data["drought_index"]
        assert di["drought_level"] in ("severe", "extreme")
        assert di["irrigation_need_mm"] > 0
        # Should publish alert for severe drought
        assert data["event_id"] is not None

    def test_drought_extreme(self, client_with_publisher):
        resp = client_with_publisher.post("/weather/drought-index", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "precipitation_mm": 5.0,
            "et0_mm": 100.0,
            "days": 30,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["drought_index"]["drought_level"] == "extreme"


# ── /weather/agricultural-report ─────────────────────────────────────────────


class TestAgriculturalReport:
    def test_report(self, client):
        resp = client.post("/weather/agricultural-report", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "lat": 15.35,
            "lon": 44.21,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "evapotranspiration" in data
        assert "growing_degree_days" in data
        assert "spray_window" in data
        assert "irrigation_adjustment" in data
        assert "alerts" in data


# ── /weather/comprehensive-stress-report ─────────────────────────────────────


class TestStressReport:
    def test_stress_report(self, client):
        resp = client.post("/weather/comprehensive-stress-report", json={
            "tenant_id": "tenant-1",
            "field_id": "field-1",
            "lat": 15.35,
            "lon": 44.21,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_status" in data
        assert "overall_color" in data
        assert "frost_risk" in data
        assert "heat_stress" in data
        assert "spray_window" in data
