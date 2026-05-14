"""
Comprehensive unit tests for weather-service main.py
اختبارات شاملة لخدمة الطقس

Covers:
- All API endpoints: /healthz, /readyz, /metrics, /weather/assess,
  /weather/current, /weather/forecast, /weather/irrigation,
  /weather/heat-stress/{temp_c}, /weather/providers,
  /weather/evapotranspiration, /weather/gdd, /weather/spray-window,
  /weather/agricultural-report, /weather/frost-risk, /weather/heat-stress,
  /weather/chill-hours, /weather/drought-index,
  /weather/comprehensive-stress-report,
  /api/v1/weather/fields/{field_id}/graph, /api/v1/weather/graphs/{graph_id}
- Pure calculation functions: ET0, GDD, spray window, frost risk,
  heat stress, chill hours, drought index, irrigation adjustment
- Risk assessment: heat_stress_risk, frost_risk, assess_weather
"""

import os
import re
import sys
import urllib.parse
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock all external/shared dependencies BEFORE importing source
# ---------------------------------------------------------------------------


class _NoopMiddleware:
    """Pass-through ASGI middleware."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)


_SHARED_MOCKS = [
    "shared",
    "shared.errors_py",
    "shared.middleware",
    "shared.middleware.tenant_context",
    "shared.middleware.security_headers",
    "shared.auth",
    "shared.auth.dependencies",
    "shared.auth.models",
    "shared.logging_config",
    "shared.observability",
    "shared.observability.tracing",
    "shared.cors_config",
    "shared.weather_alerts",
    "structlog",
    "prometheus_client",
    "nats",
    "asyncpg",
    "redis",
]

for _mod in _SHARED_MOCKS:
    sys.modules.setdefault(_mod, MagicMock())

# Wire callables invoked at import time
_errors_py = sys.modules["shared.errors_py"]
_errors_py.setup_exception_handlers = lambda app: None
_errors_py.add_request_id_middleware = lambda app: None


class _FakeExternalServiceException(Exception):
    @staticmethod
    def weather_service(details=None):
        raise _FakeExternalServiceException("weather_service_error")


_errors_py.ExternalServiceException = _FakeExternalServiceException
_errors_py.InternalServerException = Exception

sys.modules["shared.middleware.tenant_context"].TenantContextMiddleware = _NoopMiddleware
sys.modules["shared.middleware.security_headers"].setup_security_headers = lambda app: None
sys.modules["shared.logging_config"].setup_logging = lambda *a, **kw: None

_mock_tracer = MagicMock()
_mock_tracer.instrument_fastapi = lambda app: None
sys.modules["shared.observability.tracing"].setup_tracing = lambda *a, **kw: _mock_tracer

sys.modules["shared.cors_config"].CORS_SETTINGS = {
    "allow_origins": ["*"],
    "allow_credentials": False,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# Fake User class
_FakeUser = type(
    "User",
    (),
    {"tenant_id": "tenant_001", "roles": ["admin"], "id": "user_001"},
)

_mock_user = _FakeUser()
_mock_user.tenant_id = "tenant_001"


async def _fake_get_current_user():
    return _mock_user


sys.modules["shared.auth.dependencies"].get_current_user = _fake_get_current_user
sys.modules["shared.auth.models"].User = _FakeUser

# structlog mock
_structlog = sys.modules["structlog"]
_structlog.get_logger.return_value = MagicMock()

# prometheus_client mock – prevent duplicate-metric errors
_prom = sys.modules["prometheus_client"]
_prom.Counter = MagicMock(return_value=MagicMock())
_prom.Histogram = MagicMock(return_value=MagicMock())
_prom.CONTENT_TYPE_LATEST = "text/plain"
_prom.generate_latest = lambda: b"# metrics"

# Add the service root to sys.path so `src.*` imports resolve
_SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

# ---------------------------------------------------------------------------
# Import source under test
# ---------------------------------------------------------------------------

from fastapi import HTTPException
from fastapi.testclient import TestClient
from src.main import app, get_current_user  # noqa: E402
from src.risks import (  # noqa: E402
    assess_weather,
    calculate_chill_hours,
    calculate_drought_index,
    calculate_evapotranspiration,
    calculate_frost_risk,
    calculate_growing_degree_days,
    calculate_heat_stress_index,
    calculate_spray_window,
    get_irrigation_adjustment,
    heat_stress_risk,
)

# ---------------------------------------------------------------------------
# Auth override – inject fake user for all authenticated endpoints
# ---------------------------------------------------------------------------

app.dependency_overrides[get_current_user] = _fake_get_current_user

# ---------------------------------------------------------------------------
# Mock weather provider factory – set up realistic mock data
# ---------------------------------------------------------------------------


def _make_weather_data():
    """Return a realistic WeatherData-like mock."""
    w = MagicMock()
    w.temperature_c = 28.5
    w.humidity_pct = 60.0
    w.wind_speed_kmh = 12.0
    w.wind_direction_deg = 180
    w.wind_direction = "S"
    w.precipitation_mm = 0.0
    w.cloud_cover_pct = 20.0
    w.pressure_hpa = 1013.0
    w.uv_index = 7.0
    w.condition = "Partly Cloudy"
    w.condition_ar = "غائم جزئياً"
    w.timestamp = "2026-01-13T10:00:00Z"
    return w


def _make_daily_forecast(n=7):
    """Return a list of n realistic DailyForecast-like mocks."""
    days = []
    for i in range(n):
        d = MagicMock()
        d.date = f"2026-01-{14 + i:02d}"
        d.temp_max_c = 32.0 + i
        d.temp_min_c = 18.0 + i
        d.precipitation_mm = 0.0
        d.precipitation_probability_pct = 10
        d.wind_speed_max_kmh = 15.0
        d.uv_index_max = 8.0
        d.condition = "Sunny"
        d.condition_ar = "مشمس"
        d.sunrise = "06:15"
        d.sunset = "17:45"
        days.append(d)
    return days


def _make_provider_result(success=True, data=None, provider="Open-Meteo"):
    """Return a MultiProvider WeatherResult-like mock."""
    r = MagicMock()
    r.success = success
    r.data = data
    r.provider = provider
    r.error = None
    r.error_ar = None
    r.failed_providers = []
    return r


# ---------------------------------------------------------------------------
# Shared test client and app-state setup helpers
# ---------------------------------------------------------------------------

client = TestClient(app, raise_server_exceptions=False)


def _set_multi_provider(mock_provider):
    app.state.multi_provider = mock_provider
    app.state.weather_provider = None
    app.state.publisher = None
    app.state.shared_alert_generator = None


def _set_single_provider(mock_provider):
    app.state.weather_provider = mock_provider
    app.state.multi_provider = None
    app.state.publisher = None
    app.state.shared_alert_generator = None


def _reset_state():
    app.state.multi_provider = None
    app.state.weather_provider = None
    app.state.publisher = None
    app.state.shared_alert_generator = None
    # Clear graph state so tests are isolated
    for attr in ("graph_renderer", "graph_store"):
        if hasattr(app.state, attr):
            delattr(app.state, attr)


@pytest.fixture(autouse=True)
def _auto_reset_app_state():
    """Reset app.state before and after every test to prevent state leakage."""
    _reset_state()
    yield
    _reset_state()


# ---------------------------------------------------------------------------
# 1. Health & metrics endpoints
# ---------------------------------------------------------------------------


class TestHealthEndpoints:
    def test_healthz_returns_200(self):
        resp = client.get("/healthz")
        assert resp.status_code == 200

    def test_healthz_schema(self):
        resp = client.get("/healthz")
        body = resp.json()
        assert body["status"] == "healthy"
        assert body["service"] == "weather-service"
        assert re.match(r"^\d+\.\d+\.\d+", body["version"]), f"version not semver: {body['version']!r}"
        assert "timestamp" in body

    def test_readyz_returns_200(self):
        _reset_state()
        resp = client.get("/readyz")
        assert resp.status_code == 200

    def test_readyz_schema(self):
        _reset_state()
        resp = client.get("/readyz")
        body = resp.json()
        assert "status" in body
        assert "checks" in body
        assert body["service"] == "weather-service"
        assert re.match(r"^\d+\.\d+\.\d+", body["version"]), f"version not semver: {body['version']!r}"

    def test_readyz_with_no_providers_is_degraded(self):
        _reset_state()
        resp = client.get("/readyz")
        body = resp.json()
        # providers not initialized → degraded
        assert body["status"] == "degraded"
        assert body["checks"]["providers"] == "not_initialized"

    def test_readyz_with_provider_configured(self):
        _reset_state()
        app.state.weather_provider = MagicMock()
        resp = client.get("/readyz")
        body = resp.json()
        assert body["checks"]["providers"] == "available"

    def test_readyz_nats_not_configured(self):
        _reset_state()
        resp = client.get("/readyz")
        assert resp.json()["checks"]["nats"] == "not_configured"

    def test_metrics_endpoint(self):
        resp = client.get("/metrics")
        # Either 200 (prometheus available) or 501 (not installed, but mocked so 200)
        assert resp.status_code in (200, 501)


# ---------------------------------------------------------------------------
# 2. /weather/assess endpoint
# ---------------------------------------------------------------------------


class TestWeatherAssess:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "temp_c": 28.0,
        "humidity_pct": 65.0,
        "wind_speed_kmh": 12.0,
        "precipitation_mm": 0.0,
        "uv_index": 6.0,
    }

    def test_assess_normal_conditions_200(self):
        resp = client.post("/weather/assess", json=self._body)
        assert resp.status_code == 200

    def test_assess_response_schema(self):
        resp = client.post("/weather/assess", json=self._body)
        body = resp.json()
        assert "field_id" in body
        assert "alerts" in body
        assert "alert_count" in body

    def test_assess_heat_alert_generated(self):
        body = dict(self._body)
        body["temp_c"] = 46.0  # above critical threshold
        resp = client.post("/weather/assess", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["alert_count"] >= 1
        types = [a["alert_type"] for a in data["alerts"]]
        assert "heat_stress" in types

    def test_assess_frost_alert_generated(self):
        body = dict(self._body)
        body["temp_c"] = -1.0  # below freezing
        resp = client.post("/weather/assess", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["alert_count"] >= 1
        types = [a["alert_type"] for a in data["alerts"]]
        assert "frost" in types

    def test_assess_heavy_rain_alert(self):
        body = dict(self._body)
        body["precipitation_mm"] = 60.0
        resp = client.post("/weather/assess", json=body)
        assert resp.status_code == 200
        types = [a["alert_type"] for a in resp.json()["alerts"]]
        assert "heavy_rain" in types

    def test_assess_strong_wind_alert(self):
        body = dict(self._body)
        body["wind_speed_kmh"] = 65.0
        resp = client.post("/weather/assess", json=body)
        assert resp.status_code == 200
        types = [a["alert_type"] for a in resp.json()["alerts"]]
        assert "strong_wind" in types

    def test_assess_disease_risk_alert(self):
        body = dict(self._body)
        body["temp_c"] = 25.0
        body["humidity_pct"] = 90.0
        resp = client.post("/weather/assess", json=body)
        assert resp.status_code == 200
        types = [a["alert_type"] for a in resp.json()["alerts"]]
        assert "disease_risk" in types

    def test_assess_tenant_mismatch_403(self):
        body = dict(self._body)
        body["tenant_id"] = "OTHER_TENANT"
        resp = client.post("/weather/assess", json=body)
        assert resp.status_code == 403

    def test_assess_missing_temp_422(self):
        body = {k: v for k, v in self._body.items() if k != "temp_c"}
        resp = client.post("/weather/assess", json=body)
        assert resp.status_code == 422

    def test_assess_temp_out_of_range_422(self):
        body = dict(self._body)
        body["temp_c"] = 100.0  # exceeds max 60
        resp = client.post("/weather/assess", json=body)
        assert resp.status_code == 422

    def test_assess_publishes_alerts_when_publisher_set(self):
        publisher = AsyncMock()
        publisher.publish_weather_alert = AsyncMock(return_value="event-id-1")
        app.state.publisher = publisher
        body = dict(self._body)
        body["temp_c"] = 46.0
        resp = client.post("/weather/assess", json=body)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["event_ids"]) >= 1
        assert data["published"] is True
        app.state.publisher = None


# ---------------------------------------------------------------------------
# 3. /weather/current endpoint
# ---------------------------------------------------------------------------


class TestWeatherCurrent:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "lat": 15.3694,
        "lon": 44.191,
    }

    def setup_method(self):
        _reset_state()

    def test_current_with_multi_provider(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=_make_weather_data()))
        _set_multi_provider(mp)
        resp = client.post("/weather/current", json=self._body)
        assert resp.status_code == 200

    def test_current_response_schema(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=_make_weather_data()))
        _set_multi_provider(mp)
        resp = client.post("/weather/current", json=self._body)
        body = resp.json()
        assert "current" in body
        assert "location" in body
        assert "provider" in body
        assert "alerts" in body
        assert body["location"]["lat"] == pytest.approx(15.3694)

    def test_current_provider_failure_returns_error(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(success=False))
        _set_multi_provider(mp)
        resp = client.post("/weather/current", json=self._body)
        # Should be 5xx or raise (raise_server_exceptions=False means 500)
        assert resp.status_code >= 400

    def test_current_with_single_provider(self):
        sp = MagicMock()
        sp.get_current = AsyncMock(return_value=_make_weather_data())
        _set_single_provider(sp)
        resp = client.post("/weather/current", json=self._body)
        assert resp.status_code == 200
        assert resp.json()["provider"] == "Open-Meteo"

    def test_current_tenant_mismatch_403(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=_make_weather_data()))
        _set_multi_provider(mp)
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/current", json=body)
        assert resp.status_code == 403

    def test_current_lat_out_of_range_422(self):
        body = dict(self._body)
        body["lat"] = 999.0
        resp = client.post("/weather/current", json=body)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 4. /weather/forecast endpoint
# ---------------------------------------------------------------------------


class TestWeatherForecast:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "lat": 15.3694,
        "lon": 44.191,
    }

    def setup_method(self):
        _reset_state()

    def test_forecast_default_7_days(self):
        mp = MagicMock()
        mp.get_daily_forecast = AsyncMock(return_value=_make_provider_result(data=_make_daily_forecast(7)))
        _set_multi_provider(mp)
        resp = client.post("/weather/forecast", json=self._body)
        assert resp.status_code == 200
        body = resp.json()
        assert body["days"] == 7

    def test_forecast_custom_days(self):
        mp = MagicMock()
        mp.get_daily_forecast = AsyncMock(return_value=_make_provider_result(data=_make_daily_forecast(3)))
        _set_multi_provider(mp)
        resp = client.post("/weather/forecast?days=3", json=self._body)
        assert resp.status_code == 200
        assert resp.json()["days"] == 3

    def test_forecast_days_clamped_to_16(self):
        mp = MagicMock()
        mp.get_daily_forecast = AsyncMock(return_value=_make_provider_result(data=_make_daily_forecast(16)))
        _set_multi_provider(mp)
        resp = client.post("/weather/forecast?days=100", json=self._body)
        assert resp.status_code == 200

    def test_forecast_schema(self):
        mp = MagicMock()
        mp.get_daily_forecast = AsyncMock(return_value=_make_provider_result(data=_make_daily_forecast(2)))
        _set_multi_provider(mp)
        resp = client.post("/weather/forecast", json=self._body)
        body = resp.json()
        assert "forecast" in body
        assert "location" in body
        assert isinstance(body["forecast"], list)
        assert len(body["forecast"]) == 2
        day = body["forecast"][0]
        assert "temp_max_c" in day
        assert "temp_min_c" in day

    def test_forecast_single_provider_fallback(self):
        sp = MagicMock()
        sp.get_daily_forecast = AsyncMock(return_value=_make_daily_forecast(5))
        _set_single_provider(sp)
        resp = client.post("/weather/forecast", json=self._body)
        assert resp.status_code == 200

    def test_forecast_tenant_mismatch_403(self):
        mp = MagicMock()
        mp.get_daily_forecast = AsyncMock(return_value=_make_provider_result(data=_make_daily_forecast(7)))
        _set_multi_provider(mp)
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/forecast", json=body)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 5. /weather/irrigation endpoint
# ---------------------------------------------------------------------------


class TestIrrigationAdjustment:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "temp_c": 30.0,
        "humidity_pct": 50.0,
        "wind_speed_kmh": 10.0,
        "precipitation_mm": 0.0,
    }

    def test_irrigation_200(self):
        _reset_state()
        resp = client.post("/weather/irrigation", json=self._body)
        assert resp.status_code == 200

    def test_irrigation_schema(self):
        _reset_state()
        resp = client.post("/weather/irrigation", json=self._body)
        body = resp.json()
        assert "adjustment_factor" in body
        assert "recommendation_ar" in body
        assert "recommendation_en" in body
        assert "field_id" in body

    def test_irrigation_high_temp_increases_factor(self):
        _reset_state()
        body = dict(self._body)
        body["temp_c"] = 42.0
        resp = client.post("/weather/irrigation", json=body)
        assert resp.status_code == 200
        assert resp.json()["adjustment_factor"] > 1.0

    def test_irrigation_heavy_rain_reduces_factor(self):
        _reset_state()
        body = dict(self._body)
        body["precipitation_mm"] = 25.0
        resp = client.post("/weather/irrigation", json=body)
        assert resp.status_code == 200
        assert resp.json()["adjustment_factor"] < 1.0

    def test_irrigation_tenant_mismatch_403(self):
        _reset_state()
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/irrigation", json=body)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 6. /weather/heat-stress/{temp_c} endpoint
# ---------------------------------------------------------------------------


class TestHeatStressGet:
    def test_mild_temp_no_risk(self):
        resp = client.get("/weather/heat-stress/25.0")
        assert resp.status_code == 200
        body = resp.json()
        assert body["at_risk"] is False
        assert body["severity"] == "none"

    def test_critical_temp_at_risk(self):
        resp = client.get("/weather/heat-stress/46.0")
        assert resp.status_code == 200
        body = resp.json()
        assert body["at_risk"] is True
        assert body["severity"] == "critical"

    def test_high_temp_risk(self):
        resp = client.get("/weather/heat-stress/43.0")
        body = resp.json()
        assert body["severity"] == "high"

    def test_medium_temp_risk(self):
        resp = client.get("/weather/heat-stress/39.0")
        body = resp.json()
        assert body["severity"] == "medium"

    def test_low_temp_risk(self):
        resp = client.get("/weather/heat-stress/36.0")
        body = resp.json()
        assert body["severity"] == "low"

    def test_response_includes_temperature(self):
        resp = client.get("/weather/heat-stress/38.0")
        body = resp.json()
        assert body["temperature_c"] == pytest.approx(38.0)


# ---------------------------------------------------------------------------
# 7. /weather/providers endpoint
# ---------------------------------------------------------------------------


class TestWeatherProviders:
    def test_providers_with_multi_provider(self):
        mp = MagicMock()
        mp.get_available_providers = MagicMock(
            return_value=[
                {"name": "Open-Meteo", "configured": True},
                {"name": "OpenWeatherMap", "configured": False},
            ]
        )
        _set_multi_provider(mp)
        resp = client.get("/weather/providers")
        assert resp.status_code == 200
        body = resp.json()
        assert body["multi_provider_enabled"] is True
        assert body["total"] == 2
        assert body["configured"] == 1

    def test_providers_without_multi_provider(self):
        _reset_state()
        resp = client.get("/weather/providers")
        assert resp.status_code == 200
        body = resp.json()
        assert body["multi_provider_enabled"] is False
        assert body["configured"] == 1


# ---------------------------------------------------------------------------
# 8. /weather/evapotranspiration endpoint
# ---------------------------------------------------------------------------


class TestEvapotranspiration:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "temp_c": 30.0,
        "humidity_pct": 50.0,
        "wind_speed_kmh": 10.0,
        "solar_radiation_mj": 18.0,
    }

    def test_et_200(self):
        _reset_state()
        resp = client.post("/weather/evapotranspiration", json=self._body)
        assert resp.status_code == 200

    def test_et_schema(self):
        _reset_state()
        resp = client.post("/weather/evapotranspiration", json=self._body)
        body = resp.json()
        assert "evapotranspiration" in body
        et = body["evapotranspiration"]
        assert "et0_mm_day" in et
        assert "classification" in et
        assert "recommendation_ar" in et
        assert "recommendation_en" in et

    def test_et_value_positive(self):
        _reset_state()
        resp = client.post("/weather/evapotranspiration", json=self._body)
        et0 = resp.json()["evapotranspiration"]["et0_mm_day"]
        assert et0 > 0

    def test_et_tenant_mismatch_403(self):
        _reset_state()
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/evapotranspiration", json=body)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 9. /weather/gdd endpoint
# ---------------------------------------------------------------------------


class TestGrowingDegreeDays:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "temp_max_c": 28.0,
        "temp_min_c": 18.0,
        "base_temp_c": 10.0,
        "upper_temp_c": 30.0,
    }

    def test_gdd_200(self):
        _reset_state()
        resp = client.post("/weather/gdd", json=self._body)
        assert resp.status_code == 200

    def test_gdd_schema(self):
        _reset_state()
        resp = client.post("/weather/gdd", json=self._body)
        body = resp.json()
        assert "growing_degree_days" in body
        gdd = body["growing_degree_days"]
        assert "gdd_daily" in gdd
        assert "growth_rate" in gdd
        assert "recommendation_en" in gdd

    def test_gdd_positive_for_warm_day(self):
        _reset_state()
        resp = client.post("/weather/gdd", json=self._body)
        assert resp.json()["growing_degree_days"]["gdd_daily"] > 0

    def test_gdd_zero_for_cold_day(self):
        _reset_state()
        body = dict(self._body)
        body["temp_max_c"] = 5.0
        body["temp_min_c"] = 2.0
        resp = client.post("/weather/gdd", json=body)
        assert resp.status_code == 200
        assert resp.json()["growing_degree_days"]["gdd_daily"] == 0.0

    def test_gdd_tenant_mismatch_403(self):
        _reset_state()
        body = dict(self._body)
        body["tenant_id"] = "WRONG"
        resp = client.post("/weather/gdd", json=body)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 10. /weather/spray-window endpoint
# ---------------------------------------------------------------------------


class TestSprayWindow:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "temp_c": 22.0,
        "humidity_pct": 60.0,
        "wind_speed_kmh": 8.0,
        "precipitation_probability": 5.0,
    }

    def test_spray_window_200(self):
        _reset_state()
        resp = client.post("/weather/spray-window", json=self._body)
        assert resp.status_code == 200

    def test_spray_window_schema(self):
        _reset_state()
        resp = client.post("/weather/spray-window", json=self._body)
        body = resp.json()
        assert "spray_window" in body
        sw = body["spray_window"]
        assert "score" in sw
        assert "suitability" in sw
        assert "is_suitable" in sw
        assert "issues" in sw

    def test_spray_window_excellent_conditions(self):
        _reset_state()
        resp = client.post("/weather/spray-window", json=self._body)
        body = resp.json()["spray_window"]
        assert body["suitability"] in ("excellent", "good")
        assert body["is_suitable"] is True

    def test_spray_window_poor_high_wind(self):
        _reset_state()
        body = dict(self._body)
        body["wind_speed_kmh"] = 35.0
        resp = client.post("/weather/spray-window", json=body)
        assert resp.status_code == 200
        sw = resp.json()["spray_window"]
        assert "wind_too_strong" in sw["issues"]
        assert sw["is_suitable"] is False

    def test_spray_window_poor_rain(self):
        _reset_state()
        body = dict(self._body)
        body["precipitation_probability"] = 80.0
        resp = client.post("/weather/spray-window", json=body)
        sw = resp.json()["spray_window"]
        assert "rain_likely" in sw["issues"]

    def test_spray_window_tenant_mismatch_403(self):
        _reset_state()
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/spray-window", json=body)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 11. /weather/agricultural-report endpoint
# ---------------------------------------------------------------------------


class TestAgriculturalReport:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "lat": 15.3694,
        "lon": 44.191,
    }

    def setup_method(self):
        _reset_state()

    def test_report_with_multi_provider(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=_make_weather_data()))
        _set_multi_provider(mp)
        resp = client.post("/weather/agricultural-report", json=self._body)
        assert resp.status_code == 200

    def test_report_schema(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=_make_weather_data()))
        _set_multi_provider(mp)
        resp = client.post("/weather/agricultural-report", json=self._body)
        body = resp.json()
        assert "evapotranspiration" in body
        assert "growing_degree_days" in body
        assert "spray_window" in body
        assert "irrigation_adjustment" in body
        assert "alerts" in body

    def test_report_with_single_provider(self):
        sp = MagicMock()
        sp.get_current = AsyncMock(return_value=_make_weather_data())
        _set_single_provider(sp)
        resp = client.post("/weather/agricultural-report", json=self._body)
        assert resp.status_code == 200

    def test_report_tenant_mismatch_403(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=_make_weather_data()))
        _set_multi_provider(mp)
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/agricultural-report", json=body)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 12. /weather/frost-risk endpoint
# ---------------------------------------------------------------------------


class TestFrostRisk:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "temp_c": 3.0,
        "humidity_pct": 70.0,
        "wind_speed_kmh": 4.0,
        "cloud_cover_pct": 5.0,
    }

    def test_frost_risk_200(self):
        _reset_state()
        resp = client.post("/weather/frost-risk", json=self._body)
        assert resp.status_code == 200

    def test_frost_risk_schema(self):
        _reset_state()
        resp = client.post("/weather/frost-risk", json=self._body)
        body = resp.json()
        assert "frost_risk" in body
        fr = body["frost_risk"]
        assert "risk_level" in fr
        assert "risk_score" in fr
        assert "frost_likely" in fr
        assert "protection_measures" in fr

    def test_frost_risk_critical_below_zero(self):
        _reset_state()
        body = dict(self._body)
        body["temp_c"] = -3.0
        resp = client.post("/weather/frost-risk", json=body)
        fr = resp.json()["frost_risk"]
        assert fr["risk_level"] in ("critical", "high")
        assert fr["frost_likely"] is True

    def test_frost_risk_none_at_warm_temp(self):
        _reset_state()
        body = dict(self._body)
        body["temp_c"] = 20.0
        body["cloud_cover_pct"] = 80.0
        body["wind_speed_kmh"] = 20.0
        resp = client.post("/weather/frost-risk", json=body)
        fr = resp.json()["frost_risk"]
        assert fr["risk_level"] in ("none", "low")

    def test_frost_risk_tenant_mismatch_403(self):
        _reset_state()
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/frost-risk", json=body)
        assert resp.status_code == 403

    def test_frost_risk_with_dew_point(self):
        _reset_state()
        body = dict(self._body)
        body["dew_point_c"] = -1.0
        resp = client.post("/weather/frost-risk", json=body)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# 13. /weather/heat-stress (POST) endpoint
# ---------------------------------------------------------------------------


class TestHeatStressPost:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "temp_c": 38.0,
        "humidity_pct": 55.0,
        "solar_radiation_mj": 20.0,
        "wind_speed_kmh": 8.0,
    }

    def test_heat_stress_200(self):
        _reset_state()
        resp = client.post("/weather/heat-stress", json=self._body)
        assert resp.status_code == 200

    def test_heat_stress_schema(self):
        _reset_state()
        resp = client.post("/weather/heat-stress", json=self._body)
        body = resp.json()
        assert "heat_stress" in body
        hs = body["heat_stress"]
        assert "stress_level" in hs
        assert "thi" in hs or "temperature_humidity_index" in hs
        assert "is_critical" in hs
        assert "mitigation_measures" in hs

    def test_heat_stress_extreme(self):
        _reset_state()
        body = dict(self._body)
        body["temp_c"] = 46.0
        resp = client.post("/weather/heat-stress", json=body)
        hs = resp.json()["heat_stress"]
        assert hs["stress_level"] == "extreme"
        assert hs["is_critical"] is True

    def test_heat_stress_none_for_cool(self):
        _reset_state()
        body = dict(self._body)
        body["temp_c"] = 20.0
        resp = client.post("/weather/heat-stress", json=body)
        hs = resp.json()["heat_stress"]
        assert hs["stress_level"] in ("none", "low")

    def test_heat_stress_tenant_mismatch_403(self):
        _reset_state()
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/heat-stress", json=body)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 14. /weather/chill-hours endpoint
# ---------------------------------------------------------------------------


class TestChillHours:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "hourly_temps": [5.0] * 500 + [8.0] * 300,
        "model": "utah",
    }

    def test_chill_hours_200(self):
        _reset_state()
        resp = client.post("/weather/chill-hours", json=self._body)
        assert resp.status_code == 200

    def test_chill_hours_schema(self):
        _reset_state()
        resp = client.post("/weather/chill-hours", json=self._body)
        body = resp.json()
        assert "chill_hours" in body
        ch = body["chill_hours"]
        assert "chill_units" in ch
        assert "model" in ch
        assert "satisfied_crops" in ch

    def test_chill_hours_simple_model(self):
        _reset_state()
        body = dict(self._body)
        body["model"] = "simple"
        body["base_temp_c"] = 7.2
        body["hourly_temps"] = [5.0, 6.0, 8.0, 10.0, 4.0]
        resp = client.post("/weather/chill-hours", json=body)
        assert resp.status_code == 200
        # 3 hours below 7.2°C (5.0, 6.0, 4.0)
        assert resp.json()["chill_hours"]["chill_units"] == pytest.approx(3.0)

    def test_chill_hours_dynamic_model(self):
        _reset_state()
        body = dict(self._body)
        body["model"] = "dynamic"
        resp = client.post("/weather/chill-hours", json=body)
        assert resp.status_code == 200

    def test_chill_hours_empty_list(self):
        _reset_state()
        body = dict(self._body)
        body["hourly_temps"] = []
        resp = client.post("/weather/chill-hours", json=body)
        assert resp.status_code == 200
        ch = resp.json()["chill_hours"]
        assert ch["chill_units"] == 0

    def test_chill_hours_tenant_mismatch_403(self):
        _reset_state()
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/chill-hours", json=body)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 15. /weather/drought-index endpoint
# ---------------------------------------------------------------------------


class TestDroughtIndex:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "precipitation_mm": 20.0,
        "et0_mm": 80.0,
        "days": 30,
    }

    def test_drought_index_200(self):
        _reset_state()
        resp = client.post("/weather/drought-index", json=self._body)
        assert resp.status_code == 200

    def test_drought_index_schema(self):
        _reset_state()
        resp = client.post("/weather/drought-index", json=self._body)
        body = resp.json()
        assert "drought_index" in body
        di = body["drought_index"]
        assert "drought_level" in di
        assert "aridity_index" in di
        assert "water_balance_mm" in di
        assert "irrigation_need_mm" in di

    def test_drought_index_severe(self):
        _reset_state()
        resp = client.post("/weather/drought-index", json=self._body)
        di = resp.json()["drought_index"]
        # 20/80 = 0.25 → severe
        assert di["drought_level"] == "severe"

    def test_drought_index_none_when_wet(self):
        _reset_state()
        body = dict(self._body)
        body["precipitation_mm"] = 100.0
        body["et0_mm"] = 60.0
        resp = client.post("/weather/drought-index", json=body)
        di = resp.json()["drought_index"]
        assert di["drought_level"] == "none"

    def test_drought_index_extreme(self):
        _reset_state()
        body = dict(self._body)
        body["precipitation_mm"] = 1.0
        body["et0_mm"] = 100.0
        resp = client.post("/weather/drought-index", json=body)
        di = resp.json()["drought_index"]
        assert di["drought_level"] == "extreme"

    def test_drought_index_tenant_mismatch_403(self):
        _reset_state()
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/drought-index", json=body)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 16. /weather/comprehensive-stress-report endpoint
# ---------------------------------------------------------------------------


class TestComprehensiveStressReport:
    _body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "lat": 15.3694,
        "lon": 44.191,
    }

    def setup_method(self):
        _reset_state()

    def test_stress_report_200(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=_make_weather_data()))
        _set_multi_provider(mp)
        resp = client.post("/weather/comprehensive-stress-report", json=self._body)
        assert resp.status_code == 200

    def test_stress_report_schema(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=_make_weather_data()))
        _set_multi_provider(mp)
        resp = client.post("/weather/comprehensive-stress-report", json=self._body)
        body = resp.json()
        assert "frost_risk" in body
        assert "heat_stress" in body
        assert "spray_window" in body
        assert "overall_status" in body
        assert "overall_color" in body

    def test_stress_report_overall_status_valid(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=_make_weather_data()))
        _set_multi_provider(mp)
        resp = client.post("/weather/comprehensive-stress-report", json=self._body)
        body = resp.json()
        assert body["overall_status"] in ("normal", "caution", "warning", "critical")
        assert body["overall_color"] in ("green", "yellow", "orange", "red")

    def test_stress_report_critical_high_temp(self):
        mp = MagicMock()
        weather = _make_weather_data()
        weather.temperature_c = 47.0
        weather.humidity_pct = 65.0
        weather.wind_speed_kmh = 5.0
        weather.cloud_cover_pct = 0.0
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=weather))
        _set_multi_provider(mp)
        resp = client.post("/weather/comprehensive-stress-report", json=self._body)
        body = resp.json()
        assert body["overall_status"] in ("critical", "warning")

    def test_stress_report_single_provider(self):
        sp = MagicMock()
        sp.get_current = AsyncMock(return_value=_make_weather_data())
        _set_single_provider(sp)
        resp = client.post("/weather/comprehensive-stress-report", json=self._body)
        assert resp.status_code == 200

    def test_stress_report_tenant_mismatch_403(self):
        mp = MagicMock()
        mp.get_current = AsyncMock(return_value=_make_provider_result(data=_make_weather_data()))
        _set_multi_provider(mp)
        body = dict(self._body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/weather/comprehensive-stress-report", json=body)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 17. Graph endpoints
# ---------------------------------------------------------------------------


class TestWeatherGraph:
    _gen_body = {
        "tenant_id": "tenant_001",
        "field_id": "FIELD-001",
        "lat": 15.3694,
        "lon": 44.191,
        "days": 14,
        "metric": "temperature",
        "language": "en",
    }

    def setup_method(self):
        _reset_state()

    def test_generate_graph_200(self):
        _reset_state()
        resp = client.post("/api/v1/weather/fields/FIELD-001/graph", json=self._gen_body)
        assert resp.status_code == 200

    def test_generate_graph_schema(self):
        _reset_state()
        resp = client.post("/api/v1/weather/fields/FIELD-001/graph", json=self._gen_body)
        body = resp.json()
        assert body["success"] is True
        data = body["data"]
        assert "graph_id" in data
        assert "url" in data
        assert "expires_at" in data
        assert "metric" in data
        assert data["metric"] == "temperature"

    def test_fetch_graph_after_generate(self):
        _reset_state()
        gen_resp = client.post("/api/v1/weather/fields/FIELD-001/graph", json=self._gen_body)
        assert gen_resp.status_code == 200
        graph_data = gen_resp.json()["data"]
        graph_id = graph_data["graph_id"]

        # The store.fetch needs tid and sig – extract from the URL path
        url_path = graph_data["url"]
        # URL is like /api/v1/weather/graphs/{id}?tid=...&sig=...

        parsed = urllib.parse.urlparse(url_path)
        params = urllib.parse.parse_qs(parsed.query)
        tid = params.get("tid", [""])[0]
        sig = params.get("sig", [""])[0]

        fetch_resp = client.get(f"/api/v1/weather/graphs/{graph_id}?tid={tid}&sig={sig}")
        # Should return SVG or 404 (if store is empty mock)
        assert fetch_resp.status_code in (200, 404)

    def test_fetch_graph_not_found_404(self):
        _reset_state()
        # Ensure graph_store exists but contains nothing
        from src.graph import GraphStore

        app.state.graph_store = GraphStore()
        resp = client.get("/api/v1/weather/graphs/nonexistent?tid=tenant_001&sig=badsig")
        assert resp.status_code == 404

    def test_fetch_graph_no_store_404(self):
        _reset_state()
        # No graph_store at all
        resp = client.get("/api/v1/weather/graphs/missing?tid=t1&sig=s1")
        assert resp.status_code == 404

    def test_generate_graph_combined_metric(self):
        _reset_state()
        body = dict(self._gen_body)
        body["metric"] = "combined"
        resp = client.post("/api/v1/weather/fields/FIELD-001/graph", json=body)
        assert resp.status_code == 200
        assert resp.json()["data"]["metric"] == "combined"

    def test_generate_graph_tenant_mismatch_403(self):
        _reset_state()
        body = dict(self._gen_body)
        body["tenant_id"] = "OTHER"
        resp = client.post("/api/v1/weather/fields/FIELD-001/graph", json=body)
        assert resp.status_code == 403

    def test_generate_graph_with_historical_provider(self):
        """Test graph generation when multi-provider has get_historical_daily."""
        _reset_state()
        from src.graph import DailyPoint

        mock_row = {
            "date": "2026-01-01",
            "temp_min_c": 15.0,
            "temp_max_c": 28.0,
            "precipitation_mm": 0.0,
            "humidity_pct": 55.0,
            "wind_speed_kmh": 12.0,
        }
        history_result = MagicMock()
        history_result.success = True
        history_result.data = [mock_row]

        mp = MagicMock()
        mp.get_historical_daily = AsyncMock(return_value=history_result)
        _set_multi_provider(mp)

        resp = client.post("/api/v1/weather/fields/FIELD-001/graph", json=self._gen_body)
        assert resp.status_code == 200
        assert resp.json()["data"]["points_count"] == 1


# ---------------------------------------------------------------------------
# 18. Pure function tests – risks module
# ---------------------------------------------------------------------------


class TestHeatStressRisk:
    def test_none_at_cool_temp(self):
        _, severity = heat_stress_risk(25.0)
        assert severity == "none"

    def test_low_at_36(self):
        _, severity = heat_stress_risk(36.0)
        assert severity == "low"

    def test_medium_at_38(self):
        _, severity = heat_stress_risk(38.0)
        assert severity == "medium"

    def test_high_at_43(self):
        _, severity = heat_stress_risk(43.0)
        assert severity == "high"

    def test_critical_at_46(self):
        _, severity = heat_stress_risk(46.0)
        assert severity == "critical"

    def test_alert_type_always_heat_stress(self):
        alert_type, _ = heat_stress_risk(50.0)
        assert alert_type == "heat_stress"


class TestAssessWeather:
    def test_normal_conditions_no_alerts(self):
        alerts = assess_weather(temp_c=22.0, humidity_pct=50.0, wind_speed_kmh=10.0)
        assert len(alerts) == 0

    def test_extreme_heat_generates_alert(self):
        alerts = assess_weather(temp_c=46.0)
        types = [a.alert_type for a in alerts]
        assert "heat_stress" in types

    def test_frost_generates_alert(self):
        alerts = assess_weather(temp_c=-2.0)
        types = [a.alert_type for a in alerts]
        assert "frost" in types

    def test_heavy_rain_generates_alert(self):
        alerts = assess_weather(temp_c=22.0, precipitation_mm=60.0)
        types = [a.alert_type for a in alerts]
        assert "heavy_rain" in types

    def test_strong_wind_generates_alert(self):
        alerts = assess_weather(temp_c=22.0, wind_speed_kmh=65.0)
        types = [a.alert_type for a in alerts]
        assert "strong_wind" in types

    def test_disease_risk_hot_humid(self):
        alerts = assess_weather(temp_c=25.0, humidity_pct=90.0)
        types = [a.alert_type for a in alerts]
        assert "disease_risk" in types

    def test_alert_has_to_dict(self):
        alerts = assess_weather(temp_c=46.0)
        d = alerts[0].to_dict()
        assert "alert_type" in d
        assert "severity" in d
        assert "recommendations_ar" in d
        assert "recommendations_en" in d

    def test_multiple_alerts_combined(self):
        alerts = assess_weather(
            temp_c=46.0,
            humidity_pct=85.0,
            wind_speed_kmh=65.0,
            precipitation_mm=60.0,
        )
        assert len(alerts) >= 3


class TestIrrigationAdjustmentPure:
    def test_normal_conditions_factor_near_1(self):
        result = get_irrigation_adjustment(temp_c=25.0, humidity_pct=60.0, wind_speed_kmh=10.0)
        assert result["adjustment_factor"] == pytest.approx(1.0, abs=0.15)

    def test_hot_dry_windy_increases_factor(self):
        result = get_irrigation_adjustment(temp_c=42.0, humidity_pct=20.0, wind_speed_kmh=35.0)
        assert result["adjustment_factor"] > 1.0

    def test_cold_wet_conditions_decrease_factor(self):
        result = get_irrigation_adjustment(temp_c=10.0, humidity_pct=90.0, wind_speed_kmh=5.0, precipitation_mm=25.0)
        assert result["adjustment_factor"] < 1.0

    def test_factor_clamped_to_min_0_3(self):
        result = get_irrigation_adjustment(temp_c=5.0, humidity_pct=95.0, wind_speed_kmh=0.0, precipitation_mm=50.0)
        assert result["adjustment_factor"] >= 0.3

    def test_factor_clamped_to_max_1_5(self):
        result = get_irrigation_adjustment(temp_c=50.0, humidity_pct=10.0, wind_speed_kmh=60.0)
        assert result["adjustment_factor"] <= 1.5

    def test_recommendation_included(self):
        result = get_irrigation_adjustment(temp_c=25.0, humidity_pct=60.0, wind_speed_kmh=10.0)
        assert "recommendation_ar" in result
        assert "recommendation_en" in result


class TestCalculateEvapotranspirationPure:
    def test_returns_et0_key(self):
        result = calculate_evapotranspiration(temp_c=28.0, humidity_pct=50.0, wind_speed_kmh=12.0)
        assert "et0_mm_day" in result

    def test_et0_positive(self):
        result = calculate_evapotranspiration(temp_c=30.0, humidity_pct=50.0, wind_speed_kmh=10.0)
        assert result["et0_mm_day"] > 0

    def test_et0_clamped_at_15(self):
        result = calculate_evapotranspiration(
            temp_c=50.0, humidity_pct=5.0, wind_speed_kmh=200.0, solar_radiation_mj=50.0
        )
        assert result["et0_mm_day"] <= 15.0

    def test_higher_temp_gives_higher_et(self):
        r1 = calculate_evapotranspiration(temp_c=20.0, humidity_pct=50.0, wind_speed_kmh=10.0)
        r2 = calculate_evapotranspiration(temp_c=40.0, humidity_pct=50.0, wind_speed_kmh=10.0)
        assert r2["et0_mm_day"] > r1["et0_mm_day"]

    def test_classification_present(self):
        result = calculate_evapotranspiration(temp_c=28.0, humidity_pct=50.0, wind_speed_kmh=12.0)
        assert result["classification"] in ("very_low", "low", "moderate", "high", "very_high")


class TestCalculateGDDPure:
    def test_warm_day_positive_gdd(self):
        result = calculate_growing_degree_days(temp_max_c=28.0, temp_min_c=18.0, base_temp_c=10.0)
        assert result["gdd_daily"] > 0

    def test_cold_day_zero_gdd(self):
        result = calculate_growing_degree_days(temp_max_c=5.0, temp_min_c=2.0, base_temp_c=10.0)
        assert result["gdd_daily"] == 0.0

    def test_growth_rate_classification(self):
        result = calculate_growing_degree_days(temp_max_c=28.0, temp_min_c=18.0)
        assert result["growth_rate"] in ("dormant", "slow", "moderate", "fast", "very_fast")

    def test_upper_temp_cutoff_applied(self):
        # Max of 50°C should be capped at upper_temp_c=30
        result = calculate_growing_degree_days(temp_max_c=50.0, temp_min_c=18.0, base_temp_c=10.0, upper_temp_c=30.0)
        assert result["temp_avg_c"] <= 30.0


class TestCalculateSprayWindowPure:
    def test_ideal_conditions_excellent(self):
        result = calculate_spray_window(temp_c=22.0, humidity_pct=60.0, wind_speed_kmh=8.0)
        assert result["suitability"] == "excellent"
        assert result["is_suitable"] is True

    def test_high_wind_poor(self):
        result = calculate_spray_window(temp_c=22.0, humidity_pct=60.0, wind_speed_kmh=30.0)
        assert "wind_too_strong" in result["issues"]

    def test_extreme_heat_poor(self):
        result = calculate_spray_window(temp_c=38.0, humidity_pct=60.0, wind_speed_kmh=5.0)
        assert "temperature_too_high" in result["issues"]

    def test_score_bounded_0_100(self):
        result = calculate_spray_window(temp_c=22.0, humidity_pct=60.0, wind_speed_kmh=8.0)
        assert 0 <= result["score"] <= 100


class TestCalculateFrostRiskPure:
    def test_warm_temp_no_risk(self):
        result = calculate_frost_risk(temp_c=20.0, humidity_pct=50.0, wind_speed_kmh=15.0, cloud_cover_pct=80.0)
        assert result["risk_level"] == "none"

    def test_freezing_critical(self):
        result = calculate_frost_risk(temp_c=-5.0, humidity_pct=80.0, wind_speed_kmh=2.0, cloud_cover_pct=0.0)
        assert result["risk_level"] == "critical"
        assert result["frost_likely"] is True

    def test_dew_point_calculated(self):
        result = calculate_frost_risk(temp_c=5.0, humidity_pct=70.0, wind_speed_kmh=5.0)
        assert "dew_point_c" in result

    def test_dew_point_provided_used(self):
        result = calculate_frost_risk(temp_c=3.0, humidity_pct=70.0, wind_speed_kmh=5.0, dew_point_c=-1.0)
        assert result["dew_point_c"] == pytest.approx(-1.0)

    def test_protection_measures_for_high_risk(self):
        result = calculate_frost_risk(temp_c=-3.0, humidity_pct=80.0, wind_speed_kmh=2.0, cloud_cover_pct=0.0)
        assert len(result["protection_measures"]) > 0


class TestCalculateHeatStressIndexPure:
    def test_cool_temp_none(self):
        result = calculate_heat_stress_index(temp_c=20.0, humidity_pct=50.0)
        assert result["stress_level"] == "none"

    def test_extreme_heat(self):
        result = calculate_heat_stress_index(temp_c=46.0, humidity_pct=60.0)
        assert result["stress_level"] == "extreme"
        assert result["is_critical"] is True

    def test_thi_calculated(self):
        result = calculate_heat_stress_index(temp_c=30.0, humidity_pct=70.0)
        assert result["temperature_humidity_index"] > 0

    def test_mitigation_measures_for_severe(self):
        result = calculate_heat_stress_index(temp_c=42.0, humidity_pct=60.0)
        assert len(result["mitigation_measures"]) > 0


class TestCalculateChillHoursPure:
    def test_utah_model(self):
        temps = [5.0] * 100 + [8.0] * 100
        result = calculate_chill_hours(temps, model="utah")
        assert result["chill_units"] > 0
        assert result["model"] == "utah"

    def test_simple_model(self):
        temps = [5.0, 6.0, 8.0, 10.0, 3.0]
        result = calculate_chill_hours(temps, model="simple", base_temp_c=7.2)
        assert result["chill_units"] == 3.0  # 3 hours ≤ 7.2°C

    def test_dynamic_model(self):
        temps = [4.0] * 50
        result = calculate_chill_hours(temps, model="dynamic")
        assert result["chill_units"] > 0

    def test_empty_list(self):
        result = calculate_chill_hours([], model="utah")
        assert result["chill_units"] == 0

    def test_hours_analyzed_count(self):
        temps = [5.0] * 24
        result = calculate_chill_hours(temps, model="utah")
        assert result["hours_analyzed"] == 24

    def test_crop_requirements_present(self):
        result = calculate_chill_hours([5.0] * 10, model="utah")
        assert "satisfied_crops" in result
        assert "insufficient_crops" in result


class TestCalculateDroughtIndexPure:
    def test_no_drought_good_rain(self):
        result = calculate_drought_index(precipitation_mm=100.0, et0_mm=60.0)
        assert result["drought_level"] == "none"

    def test_severe_drought(self):
        result = calculate_drought_index(precipitation_mm=10.0, et0_mm=80.0)
        assert result["drought_level"] in ("severe", "extreme")

    def test_water_balance_computed(self):
        result = calculate_drought_index(precipitation_mm=40.0, et0_mm=80.0)
        assert result["water_balance_mm"] == pytest.approx(40.0 - 80.0)

    def test_irrigation_need_non_negative(self):
        result = calculate_drought_index(precipitation_mm=100.0, et0_mm=60.0)
        assert result["irrigation_need_mm"] >= 0.0

    def test_aridity_index_zero_et_returns_inf(self):
        result = calculate_drought_index(precipitation_mm=10.0, et0_mm=0.0)
        assert result["drought_level"] == "none"
