"""
Tests for weather service error handling - اختبارات معالجة الأخطاء

Covers provider failover, malformed responses, authentication errors,
tenant isolation, rate limiting, and NATS failure scenarios.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)


@pytest.fixture
def app():
    """Create FastAPI test app instance with auth dependency overridden"""
    from src.main import app as weather_app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    def fake_current_user():
        user = MagicMock(spec=User)
        user.id = "test-user-001"
        user.email = "test@sahool.sa"
        user.roles = ["farmer"]
        user.tenant_id = "00000000-0000-0000-0000-000000000123"
        return user

    weather_app.dependency_overrides[get_current_user] = fake_current_user
    yield weather_app
    weather_app.dependency_overrides.clear()


@pytest.fixture
def app_no_auth():
    """Create FastAPI test app instance without auth override (auth required)"""
    from src.main import app as weather_app

    # Clear any existing overrides so real auth dependency runs
    weather_app.dependency_overrides.clear()
    yield weather_app
    weather_app.dependency_overrides.clear()


@pytest.fixture
def app_wrong_tenant():
    """Create FastAPI test app with a user belonging to a different tenant"""
    from src.main import app as weather_app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    def fake_wrong_tenant_user():
        user = MagicMock(spec=User)
        user.id = "test-user-002"
        user.email = "other@sahool.sa"
        user.roles = ["farmer"]
        user.tenant_id = "00000000-0000-0000-0000-000000000999"
        return user

    weather_app.dependency_overrides[get_current_user] = fake_wrong_tenant_user
    yield weather_app
    weather_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """Create test client with tenant context"""
    c = TestClient(app)
    c.headers["X-Tenant-ID"] = "00000000-0000-0000-0000-000000000123"
    return c


@pytest.fixture
def client_no_auth(app_no_auth):
    """Create test client without authentication"""
    c = TestClient(app_no_auth)
    c.headers["X-Tenant-ID"] = "00000000-0000-0000-0000-000000000123"
    return c


@pytest.fixture
def client_wrong_tenant(app_wrong_tenant):
    """Create test client with wrong tenant user"""
    c = TestClient(app_wrong_tenant)
    c.headers["X-Tenant-ID"] = "00000000-0000-0000-0000-000000000999"
    return c


@pytest.fixture
def mock_weather_response():
    """Build a mock WeatherData-like object for successful responses"""

    def _build(**overrides):
        defaults = {
            "temperature_c": 28.5,
            "humidity_pct": 55.0,
            "wind_speed_kmh": 12.5,
            "wind_direction_deg": 180,
            "wind_direction": "S",
            "precipitation_mm": 0.0,
            "cloud_cover_pct": 25.0,
            "pressure_hpa": 1013.0,
            "uv_index": 8.0,
            "condition": "Clear",
            "condition_ar": "صافي",
            "icon": "clear",
            "timestamp": datetime.now(UTC).isoformat(),
            "provider": "Open-Meteo",
        }
        defaults.update(overrides)
        return MagicMock(**defaults)

    return _build


def _location_payload(tenant_id="00000000-0000-0000-0000-000000000123"):
    """Standard location request payload"""
    return {
        "tenant_id": tenant_id,
        "field_id": "field-456",
        "lat": 15.35,
        "lon": 44.20,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Provider Failover Tests - اختبارات التبديل التلقائي بين المزودين
# ═══════════════════════════════════════════════════════════════════════════════


class TestProviderFailover:
    """Test multi-provider failover behaviour"""

    @pytest.mark.asyncio
    async def test_primary_provider_fails_uses_fallback(self, client, mock_weather_response):
        """When primary provider fails, fallback provider is used"""
        with patch("src.main.app.state") as mock_state:
            mock_multi = AsyncMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.provider = "OpenWeatherMap"
            mock_result.data = mock_weather_response(provider="OpenWeatherMap")
            mock_result.failed_providers = ["Open-Meteo: Connection timeout"]
            mock_multi.get_current = AsyncMock(return_value=mock_result)
            mock_state.multi_provider = mock_multi
            mock_state.publisher = None

            response = client.post("/weather/current", json=_location_payload())

            assert response.status_code == 200
            data = response.json()
            assert data["provider"] == "OpenWeatherMap"

    @pytest.mark.asyncio
    async def test_all_providers_fail_returns_503(self, client):
        """When all providers fail, return service unavailable"""
        with patch("src.main.app.state") as mock_state:
            mock_multi = AsyncMock()
            mock_result = MagicMock()
            mock_result.success = False
            mock_result.data = None
            mock_result.error = "All weather providers failed"
            mock_result.error_ar = "فشل جميع مزودي الطقس"
            mock_result.failed_providers = [
                "Open-Meteo: Connection timeout",
                "OpenWeatherMap: 502 Bad Gateway",
            ]
            mock_multi.get_current = AsyncMock(return_value=mock_result)
            mock_state.multi_provider = mock_multi
            mock_state.publisher = None

            response = client.post("/weather/current", json=_location_payload())

            # ExternalServiceException maps to 502/503 via unified error handling
            assert response.status_code in (502, 503)

    @pytest.mark.asyncio
    async def test_provider_timeout_triggers_fallback(self, client, mock_weather_response):
        """Provider timeout triggers fallback to next provider"""
        with patch("src.main.app.state") as mock_state:
            mock_multi = AsyncMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.provider = "WeatherAPI"
            mock_result.data = mock_weather_response(provider="WeatherAPI")
            mock_result.failed_providers = [
                "Open-Meteo: TimeoutException",
                "OpenWeatherMap: TimeoutException",
            ]
            mock_multi.get_current = AsyncMock(return_value=mock_result)
            mock_state.multi_provider = mock_multi
            mock_state.publisher = None

            response = client.post("/weather/current", json=_location_payload())

            assert response.status_code == 200
            data = response.json()
            assert data["provider"] == "WeatherAPI"

    @pytest.mark.asyncio
    async def test_single_provider_network_error_returns_error(self, client):
        """Single provider mode raises error on network failure"""
        with patch("src.main.app.state") as mock_state:
            mock_provider = AsyncMock()
            mock_provider.get_current = AsyncMock(
                side_effect=httpx.RequestError("Connection refused")
            )
            mock_state.weather_provider = mock_provider
            mock_state.multi_provider = None
            mock_state.publisher = None

            response = client.post("/weather/current", json=_location_payload())

            # ExternalServiceException wraps the error
            assert response.status_code in (502, 503)

    @pytest.mark.asyncio
    async def test_forecast_all_providers_fail(self, client):
        """Forecast endpoint handles all providers failing"""
        with patch("src.main.app.state") as mock_state:
            mock_multi = AsyncMock()
            mock_result = MagicMock()
            mock_result.success = False
            mock_result.data = None
            mock_result.error = "All forecast providers failed"
            mock_result.error_ar = "فشل جميع مزودي التوقعات"
            mock_result.failed_providers = ["Open-Meteo: 500 Internal Server Error"]
            mock_multi.get_daily_forecast = AsyncMock(return_value=mock_result)
            mock_state.multi_provider = mock_multi
            mock_state.publisher = None

            response = client.post("/weather/forecast?days=7", json=_location_payload())

            assert response.status_code in (502, 503)


# ═══════════════════════════════════════════════════════════════════════════════
# Malformed Response Tests - اختبارات الاستجابات المشوهة
# ═══════════════════════════════════════════════════════════════════════════════


class TestMalformedResponses:
    """Test handling of malformed or unexpected external API responses"""

    @pytest.mark.asyncio
    async def test_invalid_json_from_provider(self):
        """Handle invalid JSON from external weather API"""
        from src.providers.open_meteo import OpenMeteoProvider

        provider = OpenMeteoProvider()

        with patch.object(provider, "_get_client") as mock_client_getter:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            # Simulate invalid JSON by raising on .json()
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_getter.return_value = mock_client

            with pytest.raises((ValueError, Exception)):
                await provider.get_current(15.35, 44.20)

        await provider.close()

    @pytest.mark.asyncio
    async def test_missing_fields_in_provider_response(self):
        """Handle missing required fields in API response"""
        from src.providers.open_meteo import OpenMeteoProvider

        provider = OpenMeteoProvider()

        with patch.object(provider, "_get_client") as mock_client_getter:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            # Return empty current block - all fields will use defaults
            mock_response.json.return_value = {"current": {}}
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_getter.return_value = mock_client

            weather = await provider.get_current(15.35, 44.20)

            # Provider uses .get() with defaults, so missing fields yield 0
            assert weather.temperature_c == 0
            assert weather.humidity_pct == 0
            assert weather.wind_speed_kmh == 0
            assert weather.pressure_hpa == 0

        await provider.close()

    @pytest.mark.asyncio
    async def test_empty_forecast_response(self):
        """Handle empty forecast data from provider"""
        from src.providers.open_meteo import OpenMeteoProvider

        provider = OpenMeteoProvider()

        with patch.object(provider, "_get_client") as mock_client_getter:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.json.return_value = {"daily": {}}
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_getter.return_value = mock_client

            forecast = await provider.get_daily_forecast(15.35, 44.20, 7)

            assert forecast == []

        await provider.close()

    @pytest.mark.asyncio
    async def test_http_500_from_provider(self):
        """Handle HTTP 500 from external weather API"""
        from src.providers.open_meteo import OpenMeteoProvider

        provider = OpenMeteoProvider()

        with patch.object(provider, "_get_client") as mock_client_getter:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "Internal Server Error",
                    request=MagicMock(),
                    response=MagicMock(status_code=500),
                )
            )
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_getter.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await provider.get_current(15.35, 44.20)

        await provider.close()

    @pytest.mark.asyncio
    async def test_http_429_rate_limited_from_provider(self):
        """Handle HTTP 429 rate limit response from provider"""
        from src.providers.open_meteo import OpenMeteoProvider

        provider = OpenMeteoProvider()

        with patch.object(provider, "_get_client") as mock_client_getter:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock(
                side_effect=httpx.HTTPStatusError(
                    "Too Many Requests",
                    request=MagicMock(),
                    response=MagicMock(status_code=429),
                )
            )
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_getter.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await provider.get_current(15.35, 44.20)

        await provider.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication Error Tests - اختبارات أخطاء المصادقة
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuthenticationErrors:
    """Test authentication error handling"""

    def test_missing_auth_token_returns_401(self, client_no_auth):
        """Missing JWT token returns 401"""
        response = client_no_auth.post(
            "/weather/current",
            json=_location_payload(),
        )
        assert response.status_code in (401, 403)

    def test_expired_token_returns_401(self):
        """Expired JWT token returns 401"""
        from src.main import app as weather_app

        from shared.auth.dependencies import get_current_user
        from shared.auth.models import User

        def raise_expired():
            from fastapi import HTTPException

            raise HTTPException(status_code=401, detail="Token expired")

        weather_app.dependency_overrides[get_current_user] = raise_expired

        try:
            c = TestClient(weather_app)
            c.headers["X-Tenant-ID"] = "00000000-0000-0000-0000-000000000123"
            response = c.post("/weather/current", json=_location_payload())
            assert response.status_code == 401
        finally:
            weather_app.dependency_overrides.clear()

    def test_unauthenticated_user_cannot_assess_weather(self, client_no_auth):
        """Unauthenticated user cannot access weather assessment"""
        response = client_no_auth.post(
            "/weather/assess",
            json={
                "tenant_id": "00000000-0000-0000-0000-000000000123",
                "field_id": "field-456",
                "temp_c": 25.0,
            },
        )
        assert response.status_code in (401, 403)

    def test_unauthenticated_user_cannot_access_irrigation(self, client_no_auth):
        """Unauthenticated user cannot access irrigation endpoint"""
        response = client_no_auth.post(
            "/weather/irrigation",
            json={
                "tenant_id": "00000000-0000-0000-0000-000000000123",
                "field_id": "field-456",
                "temp_c": 25.0,
                "humidity_pct": 55.0,
                "wind_speed_kmh": 10.0,
            },
        )
        assert response.status_code in (401, 403)


# ═══════════════════════════════════════════════════════════════════════════════
# Tenant Isolation Tests - اختبارات عزل المستأجرين
# ═══════════════════════════════════════════════════════════════════════════════


class TestTenantIsolation:
    """Test tenant data isolation enforcement"""

    def test_tenant_mismatch_returns_403(self, client_wrong_tenant):
        """User cannot access another tenant's data"""
        # User belongs to tenant ...999 but requests data for tenant ...123
        response = client_wrong_tenant.post(
            "/weather/current",
            json=_location_payload(tenant_id="00000000-0000-0000-0000-000000000123"),
        )
        assert response.status_code == 403
        data = response.json()
        assert "tenant_mismatch" in str(data).lower() or "tenant" in str(data).lower()

    def test_tenant_mismatch_on_assess_returns_403(self, client_wrong_tenant):
        """Tenant mismatch on assess endpoint returns 403"""
        response = client_wrong_tenant.post(
            "/weather/assess",
            json={
                "tenant_id": "00000000-0000-0000-0000-000000000123",
                "field_id": "field-456",
                "temp_c": 25.0,
            },
        )
        assert response.status_code == 403

    def test_tenant_mismatch_on_irrigation_returns_403(self, client_wrong_tenant):
        """Tenant mismatch on irrigation endpoint returns 403"""
        response = client_wrong_tenant.post(
            "/weather/irrigation",
            json={
                "tenant_id": "00000000-0000-0000-0000-000000000123",
                "field_id": "field-456",
                "temp_c": 25.0,
                "humidity_pct": 55.0,
                "wind_speed_kmh": 10.0,
            },
        )
        assert response.status_code == 403

    def test_tenant_mismatch_on_forecast_returns_403(self, client_wrong_tenant):
        """Tenant mismatch on forecast endpoint returns 403"""
        response = client_wrong_tenant.post(
            "/weather/forecast?days=3",
            json=_location_payload(tenant_id="00000000-0000-0000-0000-000000000123"),
        )
        assert response.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════════
# Rate Limiting Tests - اختبارات تحديد المعدل
# ═══════════════════════════════════════════════════════════════════════════════


class TestRateLimiting:
    """Test that the service handles rapid successive requests gracefully"""

    def test_rapid_requests_handled(self, client):
        """Service handles rapid successive requests without crashing"""
        # Fire 20 rapid assess requests (no external provider needed)
        responses = []
        for _ in range(20):
            resp = client.post(
                "/weather/assess",
                json={
                    "tenant_id": "00000000-0000-0000-0000-000000000123",
                    "field_id": "field-456",
                    "temp_c": 25.0,
                },
            )
            responses.append(resp)

        # All should succeed (assess endpoint is stateless)
        for resp in responses:
            assert resp.status_code == 200

    def test_rapid_health_checks(self, client):
        """Health endpoint handles rapid requests"""
        for _ in range(50):
            response = client.get("/healthz")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rapid_current_weather_requests(self, client, mock_weather_response):
        """Current weather handles rapid requests using cached multi-provider"""
        with patch("src.main.app.state") as mock_state:
            mock_multi = AsyncMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.provider = "Open-Meteo"
            mock_result.data = mock_weather_response()
            mock_result.failed_providers = []
            mock_multi.get_current = AsyncMock(return_value=mock_result)
            mock_state.multi_provider = mock_multi
            mock_state.publisher = None

            responses = []
            for _ in range(10):
                resp = client.post("/weather/current", json=_location_payload())
                responses.append(resp)

            for resp in responses:
                assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# NATS Failure Tests - اختبارات فشل NATS
# ═══════════════════════════════════════════════════════════════════════════════


class TestNATSFailures:
    """Test that NATS failures do not break endpoint responses"""

    @pytest.mark.asyncio
    async def test_nats_publish_failure_doesnt_break_response(self, client, mock_weather_response):
        """NATS publish failure does not affect endpoint response"""
        with patch("src.main.app.state") as mock_state:
            mock_multi = AsyncMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.provider = "Open-Meteo"
            # Return weather that triggers an alert (heat stress)
            mock_result.data = mock_weather_response(
                temperature_c=45.0,
                humidity_pct=20.0,
                uv_index=12.0,
            )
            mock_result.failed_providers = []
            mock_multi.get_current = AsyncMock(return_value=mock_result)
            mock_state.multi_provider = mock_multi

            # Publisher exists but publish raises an error
            mock_publisher = AsyncMock()
            mock_publisher.publish_weather_alert = AsyncMock(
                side_effect=Exception("NATS connection lost")
            )
            mock_state.publisher = mock_publisher

            response = client.post("/weather/current", json=_location_payload())

            # Endpoint should still return 200 despite NATS failure
            assert response.status_code == 200
            data = response.json()
            assert "current" in data
            assert data["current"]["temperature_c"] == 45.0
            # event_ids should be empty since publishing failed
            assert data["event_ids"] == []

    @pytest.mark.asyncio
    async def test_nats_disconnected_service_still_works(self, client, mock_weather_response):
        """Service works when NATS is disconnected (publisher is None)"""
        with patch("src.main.app.state") as mock_state:
            mock_multi = AsyncMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.provider = "Open-Meteo"
            mock_result.data = mock_weather_response()
            mock_result.failed_providers = []
            mock_multi.get_current = AsyncMock(return_value=mock_result)
            mock_state.multi_provider = mock_multi
            mock_state.publisher = None  # NATS not connected

            response = client.post("/weather/current", json=_location_payload())

            assert response.status_code == 200
            data = response.json()
            assert "current" in data
            assert data["field_id"] == "field-456"

    @pytest.mark.asyncio
    async def test_nats_failure_on_assess_doesnt_break_response(self, client):
        """NATS failure on assess endpoint does not break the response"""
        with patch("src.main.app.state") as mock_state:
            mock_publisher = AsyncMock()
            mock_publisher.publish_weather_alert = AsyncMock(
                side_effect=Exception("NATS timeout")
            )
            mock_state.publisher = mock_publisher

            response = client.post(
                "/weather/assess",
                json={
                    "tenant_id": "00000000-0000-0000-0000-000000000123",
                    "field_id": "field-456",
                    "temp_c": 45.0,  # Triggers heat stress alert
                    "humidity_pct": 20.0,
                    "wind_speed_kmh": 5.0,
                    "precipitation_mm": 0.0,
                    "uv_index": 12.0,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "alerts" in data
            assert data["alert_count"] > 0
            # event_ids should be empty since NATS failed
            assert data["event_ids"] == []

    @pytest.mark.asyncio
    async def test_nats_none_on_assess_still_works(self, client):
        """Assess endpoint works when NATS publisher is None"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/assess",
                json={
                    "tenant_id": "00000000-0000-0000-0000-000000000123",
                    "field_id": "field-456",
                    "temp_c": 25.0,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "alerts" in data


# ═══════════════════════════════════════════════════════════════════════════════
# Input Validation Error Tests - اختبارات أخطاء التحقق من المدخلات
# ═══════════════════════════════════════════════════════════════════════════════


class TestInputValidationErrors:
    """Test request body validation edge cases"""

    def test_empty_request_body(self, client):
        """Empty request body returns 422"""
        response = client.post("/weather/current", json={})
        assert response.status_code == 422

    def test_invalid_latitude_range(self, client):
        """Latitude outside -90..90 returns 422"""
        response = client.post(
            "/weather/current",
            json={
                "tenant_id": "00000000-0000-0000-0000-000000000123",
                "field_id": "field-456",
                "lat": 91.0,
                "lon": 44.20,
            },
        )
        assert response.status_code == 422

    def test_invalid_longitude_range(self, client):
        """Longitude outside -180..180 returns 422"""
        response = client.post(
            "/weather/current",
            json={
                "tenant_id": "00000000-0000-0000-0000-000000000123",
                "field_id": "field-456",
                "lat": 15.35,
                "lon": 200.0,
            },
        )
        assert response.status_code == 422

    def test_invalid_temperature_range(self, client):
        """Temperature outside -60..60 returns 422"""
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": "00000000-0000-0000-0000-000000000123",
                "field_id": "field-456",
                "temp_c": 100.0,
            },
        )
        assert response.status_code == 422

    def test_empty_tenant_id_returns_422(self, client):
        """Empty tenant_id returns 422"""
        response = client.post(
            "/weather/current",
            json={
                "tenant_id": "",
                "field_id": "field-456",
                "lat": 15.35,
                "lon": 44.20,
            },
        )
        assert response.status_code == 422

    def test_negative_humidity_returns_422(self, client):
        """Negative humidity returns 422"""
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": "00000000-0000-0000-0000-000000000123",
                "field_id": "field-456",
                "temp_c": 25.0,
                "humidity_pct": -5.0,
            },
        )
        assert response.status_code == 422

    def test_humidity_over_100_returns_422(self, client):
        """Humidity > 100% returns 422"""
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": "00000000-0000-0000-0000-000000000123",
                "field_id": "field-456",
                "temp_c": 25.0,
                "humidity_pct": 150.0,
            },
        )
        assert response.status_code == 422
