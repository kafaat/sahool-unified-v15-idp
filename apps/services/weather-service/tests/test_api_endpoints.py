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

# Tenant UUID for X-Tenant-ID header (middleware requires valid UUID)
TID = "00000000-0000-0000-0000-000000000001"
H = {"X-Tenant-ID": TID}


def _make_user(tenant_id=TID):
    user = MagicMock()
    user.id = "user-1"
    user.tenant_id = tenant_id
    user.email = "farmer@sahool.io"
    user.role = "farmer"
    return user


@pytest.fixture()
def client():
    from shared.auth.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: _make_user()
    app.state.weather_provider = MockWeatherProvider()
    app.state.multi_provider = None
    app.state.publisher = None
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def pub_client():
    from shared.auth.dependencies import get_current_user
    app.dependency_overrides[get_current_user] = lambda: _make_user()
    pub = AsyncMock()
    pub.publish_weather_alert = AsyncMock(return_value="evt-123")
    pub.publish_forecast_issued = AsyncMock(return_value="evt-456")
    pub.publish_irrigation_adjustment = AsyncMock(return_value="evt-789")
    app.state.weather_provider = MockWeatherProvider()
    app.state.multi_provider = None
    app.state.publisher = pub
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# ── Health ────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_healthz(self, client):
        r = client.get("/healthz")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"
        assert r.json()["version"] == "16.0.0"

    def test_readyz(self, client):
        r = client.get("/readyz")
        assert r.status_code == 200
        assert r.json()["status"] == "ready"


# ── Tenant Enforcement ────────────────────────────────────────────────────────

class TestTenant:
    def test_same_tenant(self):
        _enforce_tenant(_make_user("t1"), "t1")

    def test_mismatch(self):
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            _enforce_tenant(_make_user("t1"), "t999")
        assert exc.value.status_code == 403

    def test_none_tenant_passes(self):
        u = _make_user()
        u.tenant_id = None
        _enforce_tenant(u, "any")


# ── /weather/assess ───────────────────────────────────────────────────────────

class TestAssess:
    def test_normal(self, client):
        r = client.post("/weather/assess", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "temp_c": 25, "humidity_pct": 50, "wind_speed_kmh": 10,
            "precipitation_mm": 0, "uv_index": 5,
        })
        assert r.status_code == 200
        d = r.json()
        assert d["field_id"] == "f1"
        assert "alerts" in d

    def test_extreme_heat(self, client):
        r = client.post("/weather/assess", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "temp_c": 48, "humidity_pct": 20,
        })
        assert r.status_code == 200
        assert r.json()["alert_count"] >= 1

    def test_frost(self, client):
        r = client.post("/weather/assess", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "temp_c": -2,
        })
        assert r.status_code == 200
        types = [a["alert_type"] for a in r.json()["alerts"]]
        assert "frost" in types

    def test_with_publisher(self, pub_client):
        r = pub_client.post("/weather/assess", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "temp_c": 48, "humidity_pct": 20,
        })
        assert r.status_code == 200
        assert r.json()["published"] is True


# ── /weather/current ──────────────────────────────────────────────────────────

class TestCurrent:
    def test_current(self, client):
        r = client.post("/weather/current", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "lat": 15.35, "lon": 44.21,
        })
        assert r.status_code == 200
        d = r.json()
        assert d["current"]["temperature_c"] == 32.5
        assert d["provider"] == "Open-Meteo"

    def test_current_alerts(self, pub_client):
        r = pub_client.post("/weather/current", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "lat": 15.35, "lon": 44.21,
        })
        assert r.status_code == 200
        assert "alerts" in r.json()


# ── /weather/forecast ─────────────────────────────────────────────────────────

class TestForecast:
    def test_forecast(self, client):
        r = client.post("/weather/forecast?days=3", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "lat": 15.35, "lon": 44.21,
        })
        assert r.status_code == 200
        assert r.json()["days"] == 3

    def test_forecast_publisher(self, pub_client):
        r = pub_client.post("/weather/forecast?days=2", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "lat": 15.35, "lon": 44.21,
        })
        assert r.status_code == 200
        assert r.json()["event_id"] is not None


# ── /weather/irrigation ───────────────────────────────────────────────────────

class TestIrrigation:
    def test_normal(self, client):
        r = client.post("/weather/irrigation", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "temp_c": 28, "humidity_pct": 50, "wind_speed_kmh": 10, "precipitation_mm": 0,
        })
        assert r.status_code == 200
        d = r.json()
        assert "adjustment_factor" in d
        assert d["published"] is False

    def test_with_publisher(self, pub_client):
        r = pub_client.post("/weather/irrigation", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "temp_c": 28, "humidity_pct": 50, "wind_speed_kmh": 10, "precipitation_mm": 0,
        })
        assert r.status_code == 200
        assert r.json()["published"] is True


# ── /weather/heat-stress/{temp_c} ─────────────────────────────────────────────

class TestHeatStressGet:
    def test_none(self, client):
        r = client.get("/weather/heat-stress/25", headers=H)
        assert r.status_code == 200
        assert r.json()["at_risk"] is False

    def test_critical(self, client):
        r = client.get("/weather/heat-stress/46", headers=H)
        assert r.status_code == 200
        assert r.json()["severity"] == "critical"

    def test_medium(self, client):
        r = client.get("/weather/heat-stress/39", headers=H)
        assert r.status_code == 200
        assert r.json()["severity"] == "medium"


# ── /weather/providers ────────────────────────────────────────────────────────

class TestProviders:
    def test_single(self, client):
        r = client.get("/weather/providers", headers=H)
        assert r.status_code == 200
        assert r.json()["multi_provider_enabled"] is False


# ── /weather/evapotranspiration ───────────────────────────────────────────────

class TestET:
    def test_et(self, client):
        r = client.post("/weather/evapotranspiration", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "temp_c": 30, "humidity_pct": 40, "wind_speed_kmh": 12, "solar_radiation_mj": 20,
        })
        assert r.status_code == 200
        et = r.json()["evapotranspiration"]
        assert et["et0_mm_day"] > 0
        assert "classification" in et


# ── /weather/gdd ──────────────────────────────────────────────────────────────

class TestGDD:
    def test_gdd(self, client):
        r = client.post("/weather/gdd", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "temp_max_c": 32, "temp_min_c": 20,
        })
        assert r.status_code == 200
        assert r.json()["growing_degree_days"]["gdd_daily"] > 0


# ── /weather/spray-window ────────────────────────────────────────────────────

class TestSprayWindow:
    def test_spray(self, client):
        r = client.post("/weather/spray-window", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "temp_c": 22, "humidity_pct": 55, "wind_speed_kmh": 8, "precipitation_probability": 5,
        })
        assert r.status_code == 200
        assert r.json()["spray_window"]["suitability"] == "excellent"


# ── /weather/frost-risk ──────────────────────────────────────────────────────

class TestFrostRisk:
    def test_none(self, client):
        r = client.post("/weather/frost-risk", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "temp_c": 15, "humidity_pct": 50, "wind_speed_kmh": 10,
        })
        assert r.status_code == 200
        assert r.json()["frost_risk"]["risk_level"] == "none"

    def test_critical(self, pub_client):
        r = pub_client.post("/weather/frost-risk", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "temp_c": -6, "humidity_pct": 90, "wind_speed_kmh": 2, "cloud_cover_pct": 5,
        })
        assert r.status_code == 200
        assert r.json()["frost_risk"]["frost_likely"] is True
        assert r.json()["event_id"] is not None


# ── /weather/heat-stress (POST) ──────────────────────────────────────────────

class TestHeatStressPost:
    def test_severe(self, pub_client):
        r = pub_client.post("/weather/heat-stress", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "temp_c": 42, "humidity_pct": 30,
        })
        assert r.status_code == 200
        hs = r.json()["heat_stress"]
        assert hs["is_critical"] is True
        assert r.json()["event_id"] is not None

    def test_none(self, client):
        r = client.post("/weather/heat-stress", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "temp_c": 20, "humidity_pct": 50,
        })
        assert r.status_code == 200
        assert r.json()["heat_stress"]["is_critical"] is False


# ── /weather/chill-hours ─────────────────────────────────────────────────────

class TestChillHours:
    def test_utah(self, client):
        r = client.post("/weather/chill-hours", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "hourly_temps": [5.0] * 48, "model": "utah",
        })
        assert r.status_code == 200
        ch = r.json()["chill_hours"]
        assert ch["chill_units"] == 48.0

    def test_simple(self, client):
        r = client.post("/weather/chill-hours", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "hourly_temps": [3, 5, 8, 10, 6], "model": "simple", "base_temp_c": 7.2,
        })
        assert r.status_code == 200
        assert r.json()["chill_hours"]["chill_units"] == 3

    def test_empty(self, client):
        r = client.post("/weather/chill-hours", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "hourly_temps": [], "model": "utah",
        })
        assert r.status_code == 200
        assert r.json()["chill_hours"]["chill_units"] == 0


# ── /weather/drought-index ───────────────────────────────────────────────────

class TestDrought:
    def test_none(self, client):
        r = client.post("/weather/drought-index", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "precipitation_mm": 100, "et0_mm": 80, "days": 30,
        })
        assert r.status_code == 200
        assert r.json()["drought_index"]["drought_level"] == "none"

    def test_severe(self, pub_client):
        r = pub_client.post("/weather/drought-index", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "precipitation_mm": 20, "et0_mm": 100, "days": 30,
        })
        assert r.status_code == 200
        assert r.json()["drought_index"]["drought_level"] in ("severe", "extreme")
        assert r.json()["event_id"] is not None

    def test_extreme(self, pub_client):
        r = pub_client.post("/weather/drought-index", headers=H, json={
            "tenant_id": TID, "field_id": "f1",
            "precipitation_mm": 5, "et0_mm": 100, "days": 30,
        })
        assert r.status_code == 200
        assert r.json()["drought_index"]["drought_level"] == "extreme"


# ── /weather/agricultural-report ─────────────────────────────────────────────

class TestAgReport:
    def test_report(self, client):
        r = client.post("/weather/agricultural-report", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "lat": 15.35, "lon": 44.21,
        })
        assert r.status_code == 200
        d = r.json()
        assert "evapotranspiration" in d
        assert "growing_degree_days" in d
        assert "spray_window" in d
        assert "irrigation_adjustment" in d


# ── /weather/comprehensive-stress-report ─────────────────────────────────────

class TestStressReport:
    def test_report(self, client):
        r = client.post("/weather/comprehensive-stress-report", headers=H, json={
            "tenant_id": TID, "field_id": "f1", "lat": 15.35, "lon": 44.21,
        })
        assert r.status_code == 200
        d = r.json()
        assert "overall_status" in d
        assert "frost_risk" in d
        assert "heat_stress" in d
        assert "spray_window" in d
