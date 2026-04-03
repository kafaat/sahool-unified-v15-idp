"""
SAHOOL E2E Workflow Tests with Mock Services
اختبارات سير العمل الشاملة مع خدمات المحاكاة

Runs the complete admin workflow against in-memory mock servers:
  register → login → create field (bbox) → fetch NDVI → fetch weather → KPIs

No Docker required — all services run in-process on localhost.

Usage:
    pytest tests/e2e/test_e2e_mock.py -v
"""

from __future__ import annotations

import sys
import time
import uuid
from pathlib import Path

import httpx
import pytest

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tests.e2e.mock_services import start_all_servers

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

USER_URL = "http://127.0.0.1:3025"
FIELD_URL = "http://127.0.0.1:3000"
WEATHER_URL = "http://127.0.0.1:8092"
VEGETATION_URL = "http://127.0.0.1:8090"

YEMEN_BOUNDARY = [
    [44.19, 15.35],
    [44.22, 15.35],
    [44.22, 15.37],
    [44.19, 15.37],
    [44.19, 15.35],
]
YEMEN_LAT = 15.36
YEMEN_LNG = 44.205

# ═══════════════════════════════════════════════════════════════════════════════
# Session-scoped fixtures: start mock servers once
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="session", autouse=True)
def mock_servers():
    """Start all mock servers for the test session."""
    start_all_servers()
    # Give servers time to bind
    time.sleep(1)
    yield
    # Daemon threads die with the process


@pytest.fixture
def client():
    """HTTP client for tests."""
    with httpx.Client(timeout=10.0) as c:
        yield c


@pytest.fixture
def unique_email():
    return f"e2e_{uuid.uuid4().hex[:8]}@sahool.test"


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Service Health Checks
# ═══════════════════════════════════════════════════════════════════════════════


class TestServiceHealth:
    """Verify all mock services are running and healthy."""

    def test_user_service_health(self, client: httpx.Client):
        r = client.get(f"{USER_URL}/healthz")
        assert r.status_code == 200
        assert r.json()["service"] == "user-service"

    def test_field_service_health(self, client: httpx.Client):
        r = client.get(f"{FIELD_URL}/healthz")
        assert r.status_code == 200
        assert r.json()["service"] == "field-management-service"

    def test_weather_service_health(self, client: httpx.Client):
        r = client.get(f"{WEATHER_URL}/healthz")
        assert r.status_code == 200
        assert r.json()["service"] == "weather-service"

    def test_vegetation_service_health(self, client: httpx.Client):
        r = client.get(f"{VEGETATION_URL}/healthz")
        assert r.status_code == 200
        assert r.json()["service"] == "vegetation-analysis-service"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. User Registration & Login Flow
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuthWorkflow:
    """Test: register → login → get me → refresh token."""

    def test_register_new_user(self, client: httpx.Client, unique_email: str):
        r = client.post(
            f"{USER_URL}/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": "TestPass123!@#",
                "firstName": "أحمد",
                "lastName": "محمد",
            },
        )
        assert r.status_code == 201
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["user"]["email"] == unique_email
        assert data["user"]["role"] == "FARMER"

    def test_register_duplicate_fails(self, client: httpx.Client, unique_email: str):
        # Register first
        client.post(
            f"{USER_URL}/api/v1/auth/register",
            json={"email": unique_email, "password": "Test123!@#", "firstName": "A", "lastName": "B"},
        )
        # Duplicate
        r = client.post(
            f"{USER_URL}/api/v1/auth/register",
            json={"email": unique_email, "password": "Test123!@#", "firstName": "A", "lastName": "B"},
        )
        assert r.status_code == 409

    def test_login_success(self, client: httpx.Client, unique_email: str):
        # Register
        client.post(
            f"{USER_URL}/api/v1/auth/register",
            json={"email": unique_email, "password": "SecurePass1!", "firstName": "Test", "lastName": "User"},
        )
        # Login
        r = client.post(
            f"{USER_URL}/api/v1/auth/login",
            json={"email": unique_email, "password": "SecurePass1!"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert data["expires_in"] == 1800

    def test_login_wrong_password(self, client: httpx.Client, unique_email: str):
        client.post(
            f"{USER_URL}/api/v1/auth/register",
            json={"email": unique_email, "password": "Correct1!", "firstName": "A", "lastName": "B"},
        )
        r = client.post(
            f"{USER_URL}/api/v1/auth/login",
            json={"email": unique_email, "password": "WrongPassword"},
        )
        assert r.status_code == 401

    def test_get_me_with_token(self, client: httpx.Client, unique_email: str):
        reg = client.post(
            f"{USER_URL}/api/v1/auth/register",
            json={"email": unique_email, "password": "Pass123!@#", "firstName": "Me", "lastName": "Test"},
        )
        token = reg.json()["access_token"]
        r = client.get(f"{USER_URL}/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["email"] == unique_email

    def test_get_me_without_token(self, client: httpx.Client):
        r = client.get(f"{USER_URL}/api/v1/auth/me")
        assert r.status_code == 401

    def test_refresh_token(self, client: httpx.Client, unique_email: str):
        reg = client.post(
            f"{USER_URL}/api/v1/auth/register",
            json={"email": unique_email, "password": "Pass123!", "firstName": "R", "lastName": "T"},
        )
        refresh = reg.json()["refresh_token"]
        r = client.post(f"{USER_URL}/api/v1/auth/refresh", json={"refreshToken": refresh})
        assert r.status_code == 200
        assert "access_token" in r.json()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Field Creation with Bbox
# ═══════════════════════════════════════════════════════════════════════════════


class TestFieldCreationWorkflow:
    """Test: create field with boundary → list → get → delete."""

    def _get_token(self, client: httpx.Client) -> str:
        email = f"field_{uuid.uuid4().hex[:6]}@test.com"
        reg = client.post(
            f"{USER_URL}/api/v1/auth/register",
            json={"email": email, "password": "Pass123!", "firstName": "F", "lastName": "T"},
        )
        return reg.json()["access_token"]

    def test_create_field_with_boundary(self, client: httpx.Client):
        token = self._get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        r = client.post(
            f"{FIELD_URL}/api/v1/fields",
            headers=headers,
            json={
                "name": "حقل القمح التجريبي",
                "nameAr": "حقل القمح",
                "cropType": "wheat",
                "irrigationType": "drip",
                "coordinates": YEMEN_BOUNDARY,
            },
        )
        assert r.status_code == 201
        field = r.json()
        assert field["name"] == "حقل القمح التجريبي"
        assert field["cropType"] == "wheat"
        assert field["areaHectares"] > 0
        assert field["boundary"] is not None
        assert field["bbox"] is not None
        assert len(field["bbox"]) == 4
        assert field["coordinates"]["lat"] is not None
        assert field["status"] == "active"
        return field

    def test_list_fields_after_creation(self, client: httpx.Client):
        token = self._get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        # Create
        client.post(
            f"{FIELD_URL}/api/v1/fields",
            headers=headers,
            json={"name": "List Test", "cropType": "barley", "coordinates": YEMEN_BOUNDARY},
        )
        # List
        r = client.get(f"{FIELD_URL}/api/v1/fields", headers=headers)
        assert r.status_code == 200
        data = r.json()
        assert data["meta"]["total"] >= 1
        assert len(data["data"]) >= 1

    def test_get_field_by_id(self, client: httpx.Client):
        token = self._get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        create_resp = client.post(
            f"{FIELD_URL}/api/v1/fields",
            headers=headers,
            json={"name": "Get Test", "cropType": "tomato", "coordinates": YEMEN_BOUNDARY},
        )
        field_id = create_resp.json()["id"]
        r = client.get(f"{FIELD_URL}/api/v1/fields/{field_id}", headers=headers)
        assert r.status_code == 200
        assert r.json()["id"] == field_id

    def test_delete_field(self, client: httpx.Client):
        token = self._get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        create_resp = client.post(
            f"{FIELD_URL}/api/v1/fields",
            headers=headers,
            json={"name": "Delete Test", "cropType": "corn", "coordinates": YEMEN_BOUNDARY},
        )
        field_id = create_resp.json()["id"]
        r = client.delete(f"{FIELD_URL}/api/v1/fields/{field_id}", headers=headers)
        assert r.status_code == 200

    def test_create_field_without_auth(self, client: httpx.Client):
        r = client.post(
            f"{FIELD_URL}/api/v1/fields",
            json={"name": "No Auth", "cropType": "wheat", "coordinates": YEMEN_BOUNDARY},
        )
        assert r.status_code == 401

    def test_create_field_without_name_fails(self, client: httpx.Client):
        token = self._get_token(client)
        r = client.post(
            f"{FIELD_URL}/api/v1/fields",
            headers={"Authorization": f"Bearer {token}"},
            json={"cropType": "wheat", "coordinates": YEMEN_BOUNDARY},
        )
        assert r.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Sentinel Hub / NDVI Workflow
# ═══════════════════════════════════════════════════════════════════════════════


class TestNDVIWorkflow:
    """Test: EO status → analyze → indices → timeseries."""

    def test_eo_status(self, client: httpx.Client):
        r = client.get(f"{VEGETATION_URL}/v1/eo-status")
        assert r.status_code == 200
        data = r.json()
        assert "sentinel_hub_configured" in data
        assert "status" in data

    def test_satellite_providers(self, client: httpx.Client):
        r = client.get(f"{VEGETATION_URL}/v1/providers")
        assert r.status_code == 200
        providers = r.json()["providers"]
        assert len(providers) >= 1
        assert any(p["name"] == "sentinel-2" for p in providers)

    def test_available_satellites(self, client: httpx.Client):
        r = client.get(f"{VEGETATION_URL}/v1/satellites")
        assert r.status_code == 200
        sats = r.json()["satellites"]
        assert "Sentinel-2A" in sats

    def test_analyze_ndvi(self, client: httpx.Client):
        field_id = str(uuid.uuid4())
        r = client.post(
            f"{VEGETATION_URL}/v1/analyze",
            json={"field_id": field_id, "analysis_type": "ndvi", "coordinates": YEMEN_BOUNDARY},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["field_id"] == field_id
        assert -1.0 <= data["ndvi"] <= 1.0
        assert data["health_status"] in ("healthy", "moderate", "stressed", "critical")
        assert data["health_status_ar"] in ("صحي", "معتدل", "مجهد", "حرج")
        assert data["lai"] >= 0

    def test_analyze_without_field_id(self, client: httpx.Client):
        r = client.post(f"{VEGETATION_URL}/v1/analyze", json={"analysis_type": "ndvi"})
        assert r.status_code == 400

    def test_vegetation_indices(self, client: httpx.Client):
        field_id = str(uuid.uuid4())
        r = client.get(f"{VEGETATION_URL}/v1/indices/{field_id}")
        assert r.status_code == 200
        data = r.json()
        indices = data["indices"]
        assert "ndvi" in indices
        assert "ndwi" in indices
        assert "evi" in indices
        assert "lai" in indices
        assert data["health_status"] in ("healthy", "moderate", "stressed", "critical")
        assert data["trend"] in ("up", "stable", "down")

    def test_ndvi_timeseries(self, client: httpx.Client):
        field_id = str(uuid.uuid4())
        r = client.get(f"{VEGETATION_URL}/v1/timeseries/{field_id}?days=30")
        assert r.status_code == 200
        data = r.json()
        assert data["field_id"] == field_id
        assert len(data["timeseries"]) > 0
        for point in data["timeseries"]:
            assert "date" in point
            assert -1.0 <= point["ndvi"] <= 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# 5. OpenWeather / Weather Workflow
# ═══════════════════════════════════════════════════════════════════════════════


class TestWeatherWorkflow:
    """Test: current → forecast → agricultural report → KPIs."""

    def test_current_weather(self, client: httpx.Client):
        r = client.post(
            f"{WEATHER_URL}/weather/current",
            json={"lat": YEMEN_LAT, "lon": YEMEN_LNG},
        )
        assert r.status_code == 200
        w = r.json()["data"]
        assert isinstance(w["temperature_c"], (int, float))
        assert 0 <= w["humidity_pct"] <= 100
        assert w["wind_speed_kmh"] >= 0
        assert w["condition_ar"]  # Arabic condition exists

    def test_invalid_coordinates(self, client: httpx.Client):
        r = client.post(f"{WEATHER_URL}/weather/current", json={"lat": 999, "lon": -999})
        assert r.status_code == 400

    def test_weather_forecast_7days(self, client: httpx.Client):
        r = client.post(
            f"{WEATHER_URL}/weather/forecast",
            json={"lat": YEMEN_LAT, "lon": YEMEN_LNG, "days": 7},
        )
        assert r.status_code == 200
        forecast = r.json()["data"]["forecast"]
        assert len(forecast) == 7
        for day in forecast:
            assert "date" in day
            assert day["temp_max_c"] >= day["temp_min_c"]
            assert day["precipitation_probability"] >= 0

    def test_agricultural_report(self, client: httpx.Client):
        r = client.post(
            f"{WEATHER_URL}/weather/agricultural-report",
            json={"lat": YEMEN_LAT, "lon": YEMEN_LNG},
        )
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["evapotranspiration"]["et0"] >= 0
        assert data["growing_degree_days"]["gdd"] >= 0
        assert "suitable" in data["spray_window"]
        assert data["spray_window"]["suitability"] in ("optimal", "marginal", "unsuitable")

    def test_weather_providers(self, client: httpx.Client):
        r = client.get(f"{WEATHER_URL}/weather/providers")
        assert r.status_code == 200
        providers = r.json()["providers"]
        assert any(p["name"] == "open-meteo" for p in providers)

    def test_evapotranspiration_kpi(self, client: httpx.Client):
        r = client.post(
            f"{WEATHER_URL}/weather/evapotranspiration",
            json={"temperature_c": 28, "humidity_pct": 45, "wind_speed_kmh": 12, "solar_radiation": 18},
        )
        assert r.status_code == 200
        assert r.json()["et0"] > 0
        assert r.json()["unit"] == "mm/day"

    def test_growing_degree_days_kpi(self, client: httpx.Client):
        r = client.post(
            f"{WEATHER_URL}/weather/gdd",
            json={"temp_max_c": 32, "temp_min_c": 18, "base_temp_c": 10},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["gdd"] == 15.0  # (32+18)/2 - 10 = 15
        assert data["growth_rate"] in ("normal", "rapid")

    def test_spray_window_optimal(self, client: httpx.Client):
        r = client.post(
            f"{WEATHER_URL}/weather/spray-window",
            json={"temperature_c": 22, "humidity_pct": 55, "wind_speed_kmh": 8, "precipitation_mm": 0},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["suitable"] is True
        assert data["suitability"] == "optimal"

    def test_spray_window_unsuitable(self, client: httpx.Client):
        r = client.post(
            f"{WEATHER_URL}/weather/spray-window",
            json={"temperature_c": 40, "humidity_pct": 20, "wind_speed_kmh": 35, "precipitation_mm": 10},
        )
        assert r.status_code == 200
        assert r.json()["suitable"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Full Combined Workflow
# ═══════════════════════════════════════════════════════════════════════════════


class TestCombinedWorkflow:
    """Test complete flow: register → login → create field → NDVI → weather."""

    def test_full_e2e_workflow(self, client: httpx.Client):
        """The main E2E scenario — tests the complete user journey."""

        # Step 1: Register
        email = f"full_e2e_{uuid.uuid4().hex[:6]}@sahool.test"
        reg = client.post(
            f"{USER_URL}/api/v1/auth/register",
            json={"email": email, "password": "E2EPass123!@#", "firstName": "اختبار", "lastName": "شامل"},
        )
        assert reg.status_code == 201, "Registration failed"
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Login (verify credentials work)
        login = client.post(
            f"{USER_URL}/api/v1/auth/login",
            json={"email": email, "password": "E2EPass123!@#"},
        )
        assert login.status_code == 200, "Login failed"

        # Step 3: Create field with bbox from map
        field_resp = client.post(
            f"{FIELD_URL}/api/v1/fields",
            headers=headers,
            json={
                "name": "E2E Full Workflow Field",
                "nameAr": "حقل اختبار شامل",
                "cropType": "wheat",
                "irrigationType": "drip",
                "coordinates": YEMEN_BOUNDARY,
            },
        )
        assert field_resp.status_code == 201, "Field creation failed"
        field = field_resp.json()
        field_id = field["id"]
        assert field["areaHectares"] > 0
        assert field["bbox"] is not None

        # Step 4: Verify field in list
        list_resp = client.get(f"{FIELD_URL}/api/v1/fields", headers=headers)
        assert list_resp.status_code == 200
        assert list_resp.json()["meta"]["total"] >= 1

        # Step 5: Get field by ID
        get_resp = client.get(f"{FIELD_URL}/api/v1/fields/{field_id}", headers=headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == field_id

        # Step 6: Fetch NDVI for the field
        ndvi_resp = client.post(
            f"{VEGETATION_URL}/v1/analyze",
            json={"field_id": field_id, "analysis_type": "ndvi", "coordinates": YEMEN_BOUNDARY},
        )
        assert ndvi_resp.status_code == 200
        ndvi_data = ndvi_resp.json()
        assert -1.0 <= ndvi_data["ndvi"] <= 1.0
        assert ndvi_data["health_status"] in ("healthy", "moderate", "stressed", "critical")
        assert ndvi_data["health_status_ar"]  # Arabic status exists

        # Step 7: Fetch vegetation indices
        indices_resp = client.get(f"{VEGETATION_URL}/v1/indices/{field_id}")
        assert indices_resp.status_code == 200
        assert "ndvi" in indices_resp.json()["indices"]

        # Step 8: Fetch current weather for field coordinates
        lat = field["coordinates"]["lat"]
        lng = field["coordinates"]["lng"]
        weather_resp = client.post(
            f"{WEATHER_URL}/weather/current",
            json={"lat": lat, "lon": lng},
        )
        assert weather_resp.status_code == 200
        weather = weather_resp.json()["data"]
        assert isinstance(weather["temperature_c"], (int, float))

        # Step 9: Fetch 7-day forecast
        forecast_resp = client.post(
            f"{WEATHER_URL}/weather/forecast",
            json={"lat": lat, "lon": lng, "days": 7},
        )
        assert forecast_resp.status_code == 200
        assert len(forecast_resp.json()["data"]["forecast"]) == 7

        # Step 10: Fetch agricultural report (KPIs)
        agri_resp = client.post(
            f"{WEATHER_URL}/weather/agricultural-report",
            json={"lat": lat, "lon": lng},
        )
        assert agri_resp.status_code == 200
        agri = agri_resp.json()["data"]
        assert agri["evapotranspiration"]["et0"] > 0
        assert agri["growing_degree_days"]["gdd"] >= 0
        assert "suitable" in agri["spray_window"]

        # ✅ Full E2E workflow complete!

    def test_multi_field_workflow(self, client: httpx.Client):
        """Create multiple fields and verify independent data."""
        email = f"multi_{uuid.uuid4().hex[:6]}@test.com"
        reg = client.post(
            f"{USER_URL}/api/v1/auth/register",
            json={"email": email, "password": "Multi123!", "firstName": "M", "lastName": "F"},
        )
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        field_ids = []
        crops = ["wheat", "barley", "tomato"]
        for crop in crops:
            r = client.post(
                f"{FIELD_URL}/api/v1/fields",
                headers=headers,
                json={
                    "name": f"Field {crop}",
                    "cropType": crop,
                    "coordinates": [
                        [44.19 + len(field_ids) * 0.01, 15.35],
                        [44.22 + len(field_ids) * 0.01, 15.35],
                        [44.22 + len(field_ids) * 0.01, 15.37],
                        [44.19 + len(field_ids) * 0.01, 15.37],
                        [44.19 + len(field_ids) * 0.01, 15.35],
                    ],
                },
            )
            assert r.status_code == 201
            field_ids.append(r.json()["id"])

        # Verify all 3 fields in list
        list_resp = client.get(f"{FIELD_URL}/api/v1/fields", headers=headers)
        assert list_resp.json()["meta"]["total"] >= 3

        # Fetch NDVI for each
        for fid in field_ids:
            r = client.post(f"{VEGETATION_URL}/v1/analyze", json={"field_id": fid, "analysis_type": "ndvi"})
            assert r.status_code == 200
            assert -1.0 <= r.json()["ndvi"] <= 1.0

        # Delete one
        client.delete(f"{FIELD_URL}/api/v1/fields/{field_ids[0]}", headers=headers)

        # Verify count unchanged (soft delete)
        list_resp2 = client.get(f"{FIELD_URL}/api/v1/fields", headers=headers)
        assert list_resp2.json()["meta"]["total"] >= 3  # soft delete keeps in list
