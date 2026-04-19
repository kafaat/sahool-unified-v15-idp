"""Tests for ported weather-advanced endpoints.

Covers:
  GET /weather/v1/alerts/{location_id}              (ported)
  GET /weather/v1/agricultural-calendar/{location_id}  (ported)

These endpoints were migrated from the archived weather-advanced service
with tenant scope tightened (JWT-sourced instead of query param).
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    # Narrow to ImportError instead of BaseException — addresses CodeQL
    # advice against catching BaseException-family control-flow signals
    # (KeyboardInterrupt / SystemExit / GeneratorExit) in module-level
    # import guards.
    pytest.skip("fastapi not installed", allow_module_level=True)


TENANT_ID = "00000000-0000-0000-0000-000000000123"
VALID_LOCATION = "sanaa"


@pytest.fixture
def app():
    from src.main import app as weather_app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    def fake_current_user():
        user = MagicMock(spec=User)
        user.id = "test-user-001"
        user.email = "test@sahool.sa"
        user.roles = ["farmer"]
        user.tenant_id = TENANT_ID
        return user

    weather_app.dependency_overrides[get_current_user] = fake_current_user
    yield weather_app
    weather_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    c = TestClient(app)
    c.headers["X-Tenant-ID"] = TENANT_ID
    return c


def _stub_forecast(temp_max=42.0, humidity=20.0, wind=15.0, precip=0.0, uv=11.0, days=3):
    """Build a fake daily-forecast list with attributes the handler reads."""
    return [
        MagicMock(
            date=f"2026-04-2{i}",
            temp_max_c=temp_max,
            temp_min_c=temp_max - 10,
            precipitation_mm=precip,
            precipitation_probability_pct=0,
            wind_speed_max_kmh=wind,
            uv_index_max=uv,
            humidity_pct=humidity,
            condition="clear",
            condition_ar="صافي",
            sunrise="06:00",
            sunset="18:00",
        )
        for i in range(days)
    ]


# ============== /weather/v1/alerts/{location_id} ==============


class TestAlertsByLocation:
    def test_returns_alerts_for_heat_wave(self, app, client):
        forecast_result = MagicMock(success=True, data=_stub_forecast(temp_max=45.0, uv=11.0))
        app.state.multi_provider = MagicMock()
        app.state.multi_provider.get_daily_forecast = AsyncMock(return_value=forecast_result)

        response = client.get(f"/weather/v1/alerts/{VALID_LOCATION}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["location"]["id"] == VALID_LOCATION
        assert body["data"]["horizon_days"] == 3
        assert body["data"]["alerts_count"] >= 1
        types = {a["alert_type"] for a in body["data"]["alerts"]}
        # Heat stress is the canonical risk for temp_max=45; exact tag depends
        # on assess_weather's taxonomy — just assert non-empty alert payload.
        assert types
        # De-dup: each (alert_type, severity) appears at most once even though
        # all 3 days trigger the same risk.
        keys = [(a["alert_type"], a["severity"]) for a in body["data"]["alerts"]]
        assert len(keys) == len(set(keys))

    def test_clamps_days_range(self, client):
        response = client.get(f"/weather/v1/alerts/{VALID_LOCATION}?days=0")
        assert response.status_code == 422

        response = client.get(f"/weather/v1/alerts/{VALID_LOCATION}?days=20")
        assert response.status_code == 422

    def test_unknown_location_returns_404(self, client):
        response = client.get("/weather/v1/alerts/atlantis")
        assert response.status_code == 404
        # shared/errors_py wraps HTTPException into a structured response.
        assert "Yemen location" in response.json()["error"]["message"]

    def test_requires_tenant_in_jwt(self, app, client):
        from shared.auth.dependencies import get_current_user

        def user_without_tenant():
            user = MagicMock()
            user.id = "u1"
            user.email = "t@x.com"
            user.roles = []
            user.tenant_id = None
            return user

        app.dependency_overrides[get_current_user] = user_without_tenant
        response = client.get(f"/weather/v1/alerts/{VALID_LOCATION}")
        assert response.status_code == 403
        # The unified error handler flattens the HTTPException.detail dict into
        # its own envelope; the original "missing_tenant" marker survives in
        # the message field.
        assert "missing_tenant" in response.text


# ============== /weather/v1/agricultural-calendar/{location_id} ==============


class TestAgriculturalCalendar:
    def test_default_crop_is_tomato(self, client):
        response = client.get(f"/weather/v1/agricultural-calendar/{VALID_LOCATION}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["crop"] == "tomato"
        assert data["crop_name_ar"] == "طماطم"
        assert data["location"]["id"] == VALID_LOCATION
        assert "tomato" in data["supported_crops"]
        assert "wheat" in data["supported_crops"]
        assert 1 <= data["current_month"] <= 12

    def test_wheat_calendar(self, client):
        response = client.get(f"/weather/v1/agricultural-calendar/{VALID_LOCATION}?crop=wheat")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["crop"] == "wheat"
        assert data["crop_name_ar"] == "قمح"
        assert data["planting_months"] == [10, 11]
        assert data["harvest_months"] == [4, 5]
        assert data["water_requirement"] == "medium"

    def test_unknown_crop_falls_back_to_tomato(self, client):
        """Archived behaviour parity: unknown crop silently falls back to tomato."""
        response = client.get(f"/weather/v1/agricultural-calendar/{VALID_LOCATION}?crop=alien_grass")
        assert response.status_code == 200
        data = response.json()["data"]
        # crop echoes the request; crop_info comes from tomato
        assert data["crop"] == "alien_grass"
        assert data["crop_name_ar"] == "طماطم"

    def test_unknown_location_returns_404(self, client):
        response = client.get("/weather/v1/agricultural-calendar/atlantis")
        assert response.status_code == 404

    def test_requires_tenant_in_jwt(self, app, client):
        from shared.auth.dependencies import get_current_user

        def user_without_tenant():
            user = MagicMock()
            user.id = "u1"
            user.email = "t@x.com"
            user.roles = []
            user.tenant_id = None
            return user

        app.dependency_overrides[get_current_user] = user_without_tenant
        response = client.get(f"/weather/v1/agricultural-calendar/{VALID_LOCATION}")
        assert response.status_code == 403
