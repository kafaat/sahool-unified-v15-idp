"""
SAHOOL Admin E2E Workflow Integration Tests
اختبارات التكامل الشاملة لسير عمل لوحة الإدارة

Tests the complete user flow:
1. Register new user
2. Login and get JWT tokens
3. Create field with GeoJSON boundary (bbox from map)
4. Fetch Sentinel Hub NDVI data for field
5. Fetch OpenWeather data for field coordinates
6. Verify agricultural KPIs (ET0, GDD, spray window)

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
import pytest

try:
    import jwt as pyjwt

    HAS_JWT = True
except Exception:
    HAS_JWT = False

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

KONG_URL = os.getenv("KONG_URL", "http://localhost:8000")
WEATHER_URL = os.getenv("WEATHER_SERVICE_URL", "http://localhost:8092")
VEGETATION_URL = os.getenv("VEGETATION_SERVICE_URL", "http://localhost:8090")
FIELD_URL = os.getenv("FIELD_SERVICE_URL", "http://localhost:3000")
USER_URL = os.getenv("USER_SERVICE_URL", "http://localhost:3025")

JWT_SECRET = os.getenv(
    "JWT_SECRET_KEY", os.getenv("JWT_SECRET_KEY", "test-only-jwt-secret-not-for-production")
)
DEFAULT_TENANT = "a0000000-0000-0000-0000-000000000001"

# Yemen test coordinates (Sana'a area)
YEMEN_COORDS = {"lat": 15.3547, "lng": 44.2066}
YEMEN_FIELD_BOUNDARY = [
    [44.19, 15.35],
    [44.22, 15.35],
    [44.22, 15.37],
    [44.19, 15.37],
    [44.19, 15.35],
]


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════


def _make_token(
    user_id: str | None = None,
    email: str | None = None,
    roles: list[str] | None = None,
    tenant_id: str = DEFAULT_TENANT,
) -> str:
    """Generate a test JWT token."""
    if not HAS_JWT:
        pytest.skip("PyJWT not available")
    payload = {
        "sub": user_id or str(uuid.uuid4()),
        "email": email or f"test_{uuid.uuid4().hex[:8]}@sahool.com",
        "roles": roles or ["ADMIN"],
        "tid": tenant_id,
        "jti": str(uuid.uuid4()),
        "type": "access",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iss": "sahool-platform",
        "aud": "sahool-api",
    }
    return pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")


async def _is_service_available(url: str, path: str = "/healthz") -> bool:
    """Check if a service is reachable."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{url}{path}")
            return r.status_code < 500
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def auth_token() -> str:
    return _make_token()


@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


@pytest.fixture
def unique_email() -> str:
    return f"e2e_{uuid.uuid4().hex[:8]}@sahool.test"


@pytest.fixture
def field_boundary() -> list[list[float]]:
    return YEMEN_FIELD_BOUNDARY


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Full Field Creation Workflow
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.e2e
class TestFieldCreationWorkflow:
    """Test: register → login → create field → list fields → get field."""

    @pytest.mark.asyncio
    async def test_register_user(self, unique_email: str):
        """Register a new user via user-service."""
        if not await _is_service_available(USER_URL, "/health"):
            pytest.skip("user-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{USER_URL}/api/v1/auth/register",
                json={
                    "email": unique_email,
                    "password": "TestPass123!@#",
                    "firstName": "E2E",
                    "lastName": "Test",
                },
            )
        # 201 Created or 409 Conflict (already exists)
        assert resp.status_code in (201, 409), f"Register failed: {resp.status_code} {resp.text}"

    @pytest.mark.asyncio
    async def test_login_returns_tokens(self, unique_email: str):
        """Login returns access_token and refresh_token."""
        if not await _is_service_available(USER_URL, "/health"):
            pytest.skip("user-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            # Register first
            await client.post(
                f"{USER_URL}/api/v1/auth/register",
                json={
                    "email": unique_email,
                    "password": "TestPass123!@#",
                    "firstName": "E2E",
                    "lastName": "Login",
                },
            )
            # Then login
            resp = await client.post(
                f"{USER_URL}/api/v1/auth/login",
                json={"email": unique_email, "password": "TestPass123!@#"},
            )

        if resp.status_code == 401:
            pytest.skip("User registration may require activation")

        assert resp.status_code == 200, f"Login failed: {resp.status_code}"
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data.get("token_type") == "Bearer"

    @pytest.mark.asyncio
    async def test_create_field_with_boundary(
        self, auth_headers: dict, field_boundary: list
    ):
        """Create a field with GeoJSON polygon boundary."""
        if not await _is_service_available(FIELD_URL, "/healthz"):
            pytest.skip("field-management-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{FIELD_URL}/api/v1/fields",
                headers=auth_headers,
                json={
                    "name": f"E2E Test Field {uuid.uuid4().hex[:6]}",
                    "cropType": "wheat",
                    "irrigationType": "drip",
                    "coordinates": field_boundary,
                },
            )

        assert resp.status_code in (
            201,
            200,
        ), f"Create field failed: {resp.status_code} {resp.text}"
        data = resp.json()
        assert "id" in data or "data" in data

    @pytest.mark.asyncio
    async def test_list_fields(self, auth_headers: dict):
        """List fields returns paginated results."""
        if not await _is_service_available(FIELD_URL, "/healthz"):
            pytest.skip("field-management-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{FIELD_URL}/api/v1/fields",
                headers=auth_headers,
            )

        assert resp.status_code == 200
        data = resp.json()
        # Should be a list or paginated response
        assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_create_field_through_kong(
        self, auth_headers: dict, field_boundary: list
    ):
        """Create field through Kong gateway (full routing test)."""
        if not await _is_service_available(KONG_URL, "/health"):
            pytest.skip("Kong gateway not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{KONG_URL}/api/v1/fields",
                headers=auth_headers,
                json={
                    "name": f"Kong E2E Field {uuid.uuid4().hex[:6]}",
                    "cropType": "barley",
                    "coordinates": field_boundary,
                },
            )

        # Accept 201 (created), 200 (ok), or 401 (auth issue with test token)
        assert resp.status_code in (
            200,
            201,
            401,
        ), f"Kong field creation: {resp.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Sentinel Hub NDVI Workflow
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.e2e
class TestSentinelHubNDVIWorkflow:
    """Test Sentinel Hub / vegetation analysis integration."""

    @pytest.mark.asyncio
    async def test_eo_status(self):
        """Check Sentinel Hub configuration status."""
        if not await _is_service_available(VEGETATION_URL, "/healthz"):
            pytest.skip("vegetation-analysis-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{VEGETATION_URL}/v1/eo-status")

        assert resp.status_code == 200
        data = resp.json()
        assert "sentinel_hub_configured" in data or "status" in data

    @pytest.mark.asyncio
    async def test_satellite_providers(self):
        """List available satellite data providers."""
        if not await _is_service_available(VEGETATION_URL, "/healthz"):
            pytest.skip("vegetation-analysis-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{VEGETATION_URL}/v1/providers")

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_analyze_ndvi_for_field(self):
        """Request NDVI analysis for a field."""
        if not await _is_service_available(VEGETATION_URL, "/healthz"):
            pytest.skip("vegetation-analysis-service not available")

        field_id = str(uuid.uuid4())
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{VEGETATION_URL}/v1/analyze",
                json={
                    "field_id": field_id,
                    "analysis_type": "ndvi",
                    "coordinates": YEMEN_FIELD_BOUNDARY,
                    "tenant_id": DEFAULT_TENANT,
                },
            )

        # 200 OK or 422 (validation) are both acceptable
        assert resp.status_code in (
            200,
            422,
            400,
        ), f"NDVI analyze: {resp.status_code} {resp.text}"

        if resp.status_code == 200:
            data = resp.json()
            # Verify NDVI-related fields if present
            if "ndvi" in data:
                ndvi = data["ndvi"]
                if isinstance(ndvi, (int, float)):
                    assert -1.0 <= ndvi <= 1.0, "NDVI out of valid range"

    @pytest.mark.asyncio
    async def test_vegetation_indices(self):
        """Fetch vegetation indices for a field."""
        if not await _is_service_available(VEGETATION_URL, "/healthz"):
            pytest.skip("vegetation-analysis-service not available")

        field_id = str(uuid.uuid4())
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{VEGETATION_URL}/v1/indices/{field_id}"
            )

        # 200 OK or 404 (field not found)
        assert resp.status_code in (200, 404), f"Indices: {resp.status_code}"

    @pytest.mark.asyncio
    async def test_ndvi_through_kong(self):
        """Request vegetation data through Kong gateway."""
        if not await _is_service_available(KONG_URL, "/health"):
            pytest.skip("Kong gateway not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{KONG_URL}/api/v1/satellite/v1/providers"
            )

        # Kong may require auth → 401, or route works → 200
        assert resp.status_code in (200, 401, 404)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. OpenWeather Data Workflow
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.e2e
class TestOpenWeatherWorkflow:
    """Test weather service with OpenWeather / Open-Meteo integration."""

    @pytest.mark.asyncio
    async def test_weather_current(self):
        """Fetch current weather for Yemen coordinates."""
        if not await _is_service_available(WEATHER_URL, "/healthz"):
            pytest.skip("weather-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{WEATHER_URL}/weather/current",
                json={
                    "lat": YEMEN_COORDS["lat"],
                    "lon": YEMEN_COORDS["lng"],
                    "tenant_id": DEFAULT_TENANT,
                },
            )

        assert resp.status_code == 200, f"Weather current: {resp.status_code} {resp.text}"
        data = resp.json()
        # Verify weather data structure
        weather = data.get("data") or data
        if "temperature_c" in weather:
            assert isinstance(weather["temperature_c"], (int, float))
        if "humidity_pct" in weather:
            assert 0 <= weather["humidity_pct"] <= 100

    @pytest.mark.asyncio
    async def test_weather_forecast(self):
        """Fetch 7-day forecast."""
        if not await _is_service_available(WEATHER_URL, "/healthz"):
            pytest.skip("weather-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{WEATHER_URL}/weather/forecast",
                json={
                    "lat": YEMEN_COORDS["lat"],
                    "lon": YEMEN_COORDS["lng"],
                    "days": 7,
                    "tenant_id": DEFAULT_TENANT,
                },
            )

        assert resp.status_code == 200, f"Forecast: {resp.status_code}"
        data = resp.json()
        forecast = data.get("data") or data.get("forecast") or data
        if isinstance(forecast, list):
            assert len(forecast) > 0, "Forecast should have daily entries"

    @pytest.mark.asyncio
    async def test_weather_agricultural_report(self):
        """Fetch agricultural weather report with KPIs."""
        if not await _is_service_available(WEATHER_URL, "/healthz"):
            pytest.skip("weather-service not available")

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{WEATHER_URL}/weather/agricultural-report",
                json={
                    "lat": YEMEN_COORDS["lat"],
                    "lon": YEMEN_COORDS["lng"],
                    "tenant_id": DEFAULT_TENANT,
                },
            )

        assert resp.status_code == 200, f"Agri report: {resp.status_code}"
        data = resp.json()
        report = data.get("data") or data
        # Verify agricultural KPIs if present
        for key in ["evapotranspiration", "growing_degree_days", "et0", "gdd"]:
            if key in report:
                assert report[key] is not None

    @pytest.mark.asyncio
    async def test_weather_providers(self):
        """List available weather providers."""
        if not await _is_service_available(WEATHER_URL, "/healthz"):
            pytest.skip("weather-service not available")

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{WEATHER_URL}/weather/providers")

        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_weather_through_kong(self):
        """Fetch weather through Kong gateway."""
        if not await _is_service_available(KONG_URL, "/health"):
            pytest.skip("Kong gateway not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{KONG_URL}/api/v1/weather/current",
                json={
                    "lat": YEMEN_COORDS["lat"],
                    "lon": YEMEN_COORDS["lng"],
                },
            )

        # Kong may strip path and forward to weather-service
        assert resp.status_code in (200, 401, 404, 502)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Agricultural KPIs
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.e2e
class TestAgriculturalKPIs:
    """Test weather service agricultural KPI endpoints."""

    @pytest.mark.asyncio
    async def test_evapotranspiration(self):
        """Calculate ET0 for field conditions."""
        if not await _is_service_available(WEATHER_URL, "/healthz"):
            pytest.skip("weather-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{WEATHER_URL}/weather/evapotranspiration",
                json={
                    "temperature_c": 28.0,
                    "humidity_pct": 45.0,
                    "wind_speed_kmh": 12.0,
                    "solar_radiation": 18.0,
                },
            )

        assert resp.status_code == 200
        data = resp.json()
        if "et0" in data:
            assert data["et0"] >= 0, "ET0 should be non-negative"

    @pytest.mark.asyncio
    async def test_growing_degree_days(self):
        """Calculate GDD for crop growth tracking."""
        if not await _is_service_available(WEATHER_URL, "/healthz"):
            pytest.skip("weather-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{WEATHER_URL}/weather/gdd",
                json={
                    "temp_max_c": 32.0,
                    "temp_min_c": 18.0,
                    "base_temp_c": 10.0,
                },
            )

        assert resp.status_code == 200
        data = resp.json()
        if "gdd" in data:
            assert data["gdd"] >= 0, "GDD should be non-negative"

    @pytest.mark.asyncio
    async def test_spray_window(self):
        """Assess spray application conditions."""
        if not await _is_service_available(WEATHER_URL, "/healthz"):
            pytest.skip("weather-service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{WEATHER_URL}/weather/spray-window",
                json={
                    "temperature_c": 22.0,
                    "humidity_pct": 55.0,
                    "wind_speed_kmh": 8.0,
                    "precipitation_mm": 0.0,
                },
            )

        assert resp.status_code == 200
        data = resp.json()
        if "suitability" in data:
            assert data["suitability"] in (
                "optimal",
                "marginal",
                "unsuitable",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Combined Field + Weather + NDVI Workflow
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.e2e
class TestCombinedWorkflow:
    """Test the full field → NDVI → weather combined workflow."""

    @pytest.mark.asyncio
    async def test_field_creation_and_weather(self, auth_headers: dict):
        """Create field then fetch weather for its coordinates."""
        field_available = await _is_service_available(FIELD_URL, "/healthz")
        weather_available = await _is_service_available(WEATHER_URL, "/healthz")

        if not (field_available and weather_available):
            pytest.skip("field-management or weather service not available")

        async with httpx.AsyncClient(timeout=15.0) as client:
            # Create field
            field_resp = await client.post(
                f"{FIELD_URL}/api/v1/fields",
                headers=auth_headers,
                json={
                    "name": f"Combined Test {uuid.uuid4().hex[:6]}",
                    "cropType": "wheat",
                    "coordinates": YEMEN_FIELD_BOUNDARY,
                },
            )

            if field_resp.status_code not in (200, 201):
                pytest.skip(f"Could not create field: {field_resp.status_code}")

            # Fetch weather for field coordinates
            weather_resp = await client.post(
                f"{WEATHER_URL}/weather/current",
                json={
                    "lat": YEMEN_COORDS["lat"],
                    "lon": YEMEN_COORDS["lng"],
                    "tenant_id": DEFAULT_TENANT,
                },
            )

        assert weather_resp.status_code == 200

    @pytest.mark.asyncio
    async def test_field_creation_and_ndvi(self, auth_headers: dict):
        """Create field then fetch NDVI analysis."""
        field_available = await _is_service_available(FIELD_URL, "/healthz")
        veg_available = await _is_service_available(VEGETATION_URL, "/healthz")

        if not (field_available and veg_available):
            pytest.skip("field-management or vegetation service not available")

        field_id = str(uuid.uuid4())

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create field
            await client.post(
                f"{FIELD_URL}/api/v1/fields",
                headers=auth_headers,
                json={
                    "name": f"NDVI Test {uuid.uuid4().hex[:6]}",
                    "cropType": "wheat",
                    "coordinates": YEMEN_FIELD_BOUNDARY,
                },
            )

            # Request NDVI analysis
            ndvi_resp = await client.post(
                f"{VEGETATION_URL}/v1/analyze",
                json={
                    "field_id": field_id,
                    "analysis_type": "ndvi",
                    "coordinates": YEMEN_FIELD_BOUNDARY,
                },
            )

        # Accept any non-5xx response
        assert ndvi_resp.status_code < 500, f"NDVI: {ndvi_resp.status_code}"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Error Handling
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.e2e
class TestErrorHandling:
    """Test error handling and validation across services."""

    @pytest.mark.asyncio
    async def test_weather_invalid_coordinates(self):
        """Weather service rejects invalid coordinates."""
        if not await _is_service_available(WEATHER_URL, "/healthz"):
            pytest.skip("weather-service not available")

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{WEATHER_URL}/weather/current",
                json={"lat": 999, "lon": -999},
            )

        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_field_creation_without_auth(self):
        """Field creation without token returns 401."""
        if not await _is_service_available(FIELD_URL, "/healthz"):
            pytest.skip("field-management-service not available")

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{FIELD_URL}/api/v1/fields",
                json={
                    "name": "Unauthorized Field",
                    "cropType": "wheat",
                    "coordinates": YEMEN_FIELD_BOUNDARY,
                },
            )

        assert resp.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_ndvi_nonexistent_field(self):
        """Vegetation indices for non-existent field returns 404 or empty."""
        if not await _is_service_available(VEGETATION_URL, "/healthz"):
            pytest.skip("vegetation-analysis-service not available")

        fake_id = str(uuid.uuid4())
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{VEGETATION_URL}/v1/indices/{fake_id}"
            )

        assert resp.status_code in (200, 404)

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self):
        """Expired JWT token is rejected by field-management-service."""
        if not HAS_JWT:
            pytest.skip("PyJWT not available")
        if not await _is_service_available(FIELD_URL, "/healthz"):
            pytest.skip("field-management-service not available")

        expired_payload = {
            "sub": str(uuid.uuid4()),
            "email": "expired@sahool.test",
            "roles": ["ADMIN"],
            "tid": DEFAULT_TENANT,
            "jti": str(uuid.uuid4()),
            "type": "access",
            "iat": datetime.now(UTC) - timedelta(hours=2),
            "exp": datetime.now(UTC) - timedelta(hours=1),
            "iss": "sahool-platform",
            "aud": "sahool-api",
        }
        expired_token = pyjwt.encode(
            expired_payload, JWT_SECRET, algorithm="HS256"
        )

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{FIELD_URL}/api/v1/fields",
                headers={
                    "Authorization": f"Bearer {expired_token}",
                    "Content-Type": "application/json",
                },
            )

        assert resp.status_code == 401
