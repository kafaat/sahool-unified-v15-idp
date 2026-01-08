"""
Comprehensive Weather Service API Tests
Tests for weather API endpoints, external provider integration, and error handling
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_weather_data():
    """Mock weather data for testing"""
    return {
        "temperature_c": 28.5,
        "humidity_pct": 55.0,
        "wind_speed_kmh": 12.5,
        "wind_direction_deg": 180,
        "precipitation_mm": 0.0,
        "cloud_cover_pct": 25.0,
        "pressure_hpa": 1013.0,
        "uv_index": 8.0,
        "timestamp": datetime.utcnow().isoformat(),
    }


@pytest.fixture
def mock_daily_forecast():
    """Mock daily forecast data"""
    return [
        {
            "date": "2026-01-08",
            "temp_max_c": 32.5,
            "temp_min_c": 18.2,
            "precipitation_mm": 0.0,
            "precipitation_probability_pct": 10.0,
            "wind_speed_max_kmh": 18.5,
            "uv_index_max": 9.5,
            "sunrise": "06:15",
            "sunset": "18:00",
        },
        {
            "date": "2026-01-09",
            "temp_max_c": 33.8,
            "temp_min_c": 19.5,
            "precipitation_mm": 2.5,
            "precipitation_probability_pct": 30.0,
            "wind_speed_max_kmh": 15.0,
            "uv_index_max": 8.5,
            "sunrise": "06:15",
            "sunset": "18:01",
        },
    ]


@pytest.fixture
def app():
    """Create FastAPI test app instance"""
    from src.main import app as weather_app

    return weather_app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_returns_healthy(self, client):
        """Test health endpoint returns healthy status"""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "weather-service"
        assert "version" in data
        assert "timestamp" in data

    def test_health_check_structure(self, client):
        """Test health endpoint response structure"""
        response = client.get("/healthz")
        data = response.json()
        required_keys = ["status", "service", "version", "timestamp"]
        for key in required_keys:
            assert key in data


class TestCurrentWeatherEndpoint:
    """Test current weather endpoint"""

    @pytest.mark.asyncio
    async def test_get_current_weather_success(self, client):
        """Test successful current weather retrieval"""
        with patch("src.main.app.state") as mock_state:
            # Mock weather provider
            mock_provider = AsyncMock()
            mock_provider.get_current = AsyncMock(
                return_value=MagicMock(
                    temperature_c=28.5,
                    humidity_pct=55.0,
                    wind_speed_kmh=12.5,
                    wind_direction_deg=180,
                    precipitation_mm=0.0,
                    cloud_cover_pct=25.0,
                    pressure_hpa=1013.0,
                    uv_index=8.0,
                    timestamp=datetime.utcnow().isoformat(),
                )
            )
            mock_state.weather_provider = mock_provider
            mock_state.multi_provider = None
            mock_state.publisher = None

            response = client.post(
                "/weather/current",
                json={
                    "tenant_id": "tenant-123",
                    "field_id": "field-456",
                    "lat": 15.35,
                    "lon": 44.20,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "current" in data
            assert data["field_id"] == "field-456"

    @pytest.mark.asyncio
    async def test_get_current_weather_invalid_coordinates(self, client):
        """Test current weather with invalid coordinates"""
        response = client.post(
            "/weather/current",
            json={
                "tenant_id": "tenant-123",
                "field_id": "field-456",
                "lat": 95.0,  # Invalid latitude
                "lon": 44.20,
            },
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_current_weather_multi_provider(self, client):
        """Test current weather with multi-provider service"""
        with patch("src.main.app.state") as mock_state:
            # Mock multi-provider
            mock_multi = AsyncMock()
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.provider = "OpenWeatherMap"
            mock_result.data = MagicMock(
                temperature_c=29.0,
                humidity_pct=52.0,
                wind_speed_kmh=10.0,
                wind_direction_deg=200,
                precipitation_mm=0.0,
                cloud_cover_pct=30.0,
                pressure_hpa=1012.0,
                uv_index=7.5,
                timestamp=datetime.utcnow().isoformat(),
            )
            mock_multi.get_current = AsyncMock(return_value=mock_result)
            mock_state.multi_provider = mock_multi
            mock_state.publisher = None

            response = client.post(
                "/weather/current",
                json={
                    "tenant_id": "tenant-123",
                    "field_id": "field-789",
                    "lat": 13.58,
                    "lon": 44.02,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["provider"] == "OpenWeatherMap"

    def test_get_current_weather_missing_fields(self, client):
        """Test current weather with missing required fields"""
        response = client.post(
            "/weather/current",
            json={
                "tenant_id": "tenant-123",
                # Missing field_id, lat, lon
            },
        )
        assert response.status_code == 422


class TestForecastEndpoint:
    """Test weather forecast endpoint"""

    @pytest.mark.asyncio
    async def test_get_forecast_success(self, client, mock_daily_forecast):
        """Test successful forecast retrieval"""
        with patch("src.main.app.state") as mock_state:
            # Mock weather provider
            mock_provider = AsyncMock()
            mock_forecasts = [MagicMock(**forecast) for forecast in mock_daily_forecast]
            mock_provider.get_daily_forecast = AsyncMock(return_value=mock_forecasts)
            mock_state.weather_provider = mock_provider
            mock_state.multi_provider = None
            mock_state.publisher = None

            response = client.post(
                "/weather/forecast?days=7",
                json={
                    "tenant_id": "tenant-123",
                    "field_id": "field-456",
                    "lat": 15.35,
                    "lon": 44.20,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert "forecast" in data
            assert data["days"] >= 1

    @pytest.mark.asyncio
    async def test_get_forecast_custom_days(self, client):
        """Test forecast with custom number of days"""
        with patch("src.main.app.state") as mock_state:
            mock_provider = AsyncMock()
            mock_provider.get_daily_forecast = AsyncMock(return_value=[])
            mock_state.weather_provider = mock_provider
            mock_state.multi_provider = None
            mock_state.publisher = None

            # Test different day ranges
            for days in [1, 3, 7, 14]:
                response = client.post(
                    f"/weather/forecast?days={days}",
                    json={
                        "tenant_id": "tenant-123",
                        "field_id": "field-456",
                        "lat": 15.35,
                        "lon": 44.20,
                    },
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_forecast_max_days_limit(self, client):
        """Test forecast respects maximum days limit"""
        with patch("src.main.app.state") as mock_state:
            mock_provider = AsyncMock()
            mock_provider.get_daily_forecast = AsyncMock(return_value=[])
            mock_state.weather_provider = mock_provider
            mock_state.multi_provider = None
            mock_state.publisher = None

            # Request more than 16 days (API limit)
            response = client.post(
                "/weather/forecast?days=30",
                json={
                    "tenant_id": "tenant-123",
                    "field_id": "field-456",
                    "lat": 15.35,
                    "lon": 44.20,
                },
            )

            assert response.status_code == 200
            # Should be clamped to 16 days max


class TestWeatherAssessEndpoint:
    """Test weather assessment endpoint"""

    def test_assess_weather_normal_conditions(self, client):
        """Test weather assessment with normal conditions"""
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": "tenant-123",
                "field_id": "field-456",
                "temp_c": 25.0,
                "humidity_pct": 55.0,
                "wind_speed_kmh": 10.0,
                "precipitation_mm": 0.0,
                "uv_index": 6.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "alert_count" in data
        assert data["field_id"] == "field-456"

    def test_assess_weather_heat_stress(self, client):
        """Test weather assessment detects heat stress"""
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": "tenant-123",
                "field_id": "field-456",
                "temp_c": 42.0,
                "humidity_pct": 30.0,
                "wind_speed_kmh": 15.0,
                "precipitation_mm": 0.0,
                "uv_index": 11.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["alert_count"] > 0

        # Check for heat stress alert
        alerts = data["alerts"]
        heat_alerts = [a for a in alerts if a["alert_type"] == "heat_stress"]
        assert len(heat_alerts) > 0

    def test_assess_weather_heavy_rain(self, client):
        """Test weather assessment detects heavy rain"""
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": "tenant-123",
                "field_id": "field-456",
                "temp_c": 22.0,
                "humidity_pct": 85.0,
                "wind_speed_kmh": 20.0,
                "precipitation_mm": 40.0,
                "uv_index": 2.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["alert_count"] > 0

        # Check for heavy rain alert
        alerts = data["alerts"]
        rain_alerts = [a for a in alerts if a["alert_type"] == "heavy_rain"]
        assert len(rain_alerts) > 0

    def test_assess_weather_optional_fields(self, client):
        """Test weather assessment with optional fields omitted"""
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": "tenant-123",
                "field_id": "field-456",
                "temp_c": 25.0,
                # Optional fields omitted
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data


class TestIrrigationEndpoint:
    """Test irrigation adjustment endpoint"""

    def test_irrigation_normal_conditions(self, client):
        """Test irrigation adjustment for normal conditions"""
        response = client.post(
            "/weather/irrigation",
            json={
                "tenant_id": "tenant-123",
                "field_id": "field-456",
                "temp_c": 25.0,
                "humidity_pct": 55.0,
                "wind_speed_kmh": 10.0,
                "precipitation_mm": 0.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "adjustment_factor" in data
        assert "recommendation_ar" in data
        assert "recommendation_en" in data
        assert 0.3 <= data["adjustment_factor"] <= 1.5

    def test_irrigation_hot_dry_conditions(self, client):
        """Test irrigation adjustment for hot, dry conditions"""
        response = client.post(
            "/weather/irrigation",
            json={
                "tenant_id": "tenant-123",
                "field_id": "field-456",
                "temp_c": 38.0,
                "humidity_pct": 25.0,
                "wind_speed_kmh": 20.0,
                "precipitation_mm": 0.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        # Should recommend increased irrigation
        assert data["adjustment_factor"] > 1.0

    def test_irrigation_after_rain(self, client):
        """Test irrigation adjustment after rainfall"""
        response = client.post(
            "/weather/irrigation",
            json={
                "tenant_id": "tenant-123",
                "field_id": "field-456",
                "temp_c": 22.0,
                "humidity_pct": 75.0,
                "wind_speed_kmh": 5.0,
                "precipitation_mm": 25.0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        # Should recommend decreased irrigation
        assert data["adjustment_factor"] < 1.0


class TestProvidersEndpoint:
    """Test weather providers listing endpoint"""

    def test_get_providers_multi_enabled(self, client):
        """Test providers endpoint with multi-provider enabled"""
        with patch("src.main.app.state") as mock_state:
            mock_multi = MagicMock()
            mock_multi.get_available_providers = MagicMock(
                return_value=[
                    {"name": "Open-Meteo", "configured": True, "type": "OpenMeteoProvider"},
                    {
                        "name": "OpenWeatherMap",
                        "configured": True,
                        "type": "OpenWeatherMapProvider",
                    },
                    {"name": "WeatherAPI", "configured": False, "type": "WeatherAPIProvider"},
                ]
            )
            mock_state.multi_provider = mock_multi

            response = client.get("/weather/providers")

            assert response.status_code == 200
            data = response.json()
            assert data["multi_provider_enabled"] is True
            assert "providers" in data
            assert data["total"] == 3
            assert data["configured"] == 2

    def test_get_providers_single_provider(self, client):
        """Test providers endpoint with single provider"""
        with patch("src.main.app.state") as mock_state:
            mock_state.multi_provider = None

            response = client.get("/weather/providers")

            assert response.status_code == 200
            data = response.json()
            assert data["multi_provider_enabled"] is False
            assert data["total"] == 1
            assert data["configured"] == 1


class TestHeatStressEndpoint:
    """Test heat stress check endpoint"""

    def test_heat_stress_critical(self, client):
        """Test heat stress at critical temperature"""
        response = client.get("/weather/heat-stress/46")

        assert response.status_code == 200
        data = response.json()
        assert data["temperature_c"] == 46.0
        assert data["severity"] == "critical"
        assert data["at_risk"] is True

    def test_heat_stress_normal(self, client):
        """Test heat stress at normal temperature"""
        response = client.get("/weather/heat-stress/25")

        assert response.status_code == 200
        data = response.json()
        assert data["temperature_c"] == 25.0
        assert data["severity"] == "none"
        assert data["at_risk"] is False

    def test_heat_stress_various_temperatures(self, client):
        """Test heat stress at various temperature levels"""
        temperatures = [
            (30, False),  # Normal
            (36, True),  # Low risk
            (39, True),  # Medium risk
            (43, True),  # High risk
            (47, True),  # Critical risk
        ]

        for temp, should_be_at_risk in temperatures:
            response = client.get(f"/weather/heat-stress/{temp}")
            assert response.status_code == 200
            data = response.json()
            assert data["at_risk"] == should_be_at_risk


class TestExternalAPIIntegration:
    """Test external weather API integration"""

    @pytest.mark.asyncio
    async def test_open_meteo_api_call(self):
        """Test Open-Meteo API integration"""
        from src.providers.open_meteo import OpenMeteoProvider

        provider = OpenMeteoProvider()

        # Mock the HTTP client
        with patch.object(provider, "_get_client") as mock_client_getter:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "current": {
                    "temperature_2m": 28.5,
                    "relative_humidity_2m": 55,
                    "wind_speed_10m": 12,
                    "wind_direction_10m": 180,
                    "precipitation": 0,
                    "cloud_cover": 25,
                    "pressure_msl": 1013,
                    "uv_index": 8,
                    "time": "2026-01-07T12:00:00Z",
                }
            }
            mock_response.raise_for_status = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_getter.return_value = mock_client

            # Test API call
            weather = await provider.get_current(15.35, 44.20)

            assert weather.temperature_c == 28.5
            assert weather.humidity_pct == 55
            assert weather.wind_speed_kmh == 12

        await provider.close()

    @pytest.mark.asyncio
    async def test_open_meteo_forecast_call(self):
        """Test Open-Meteo forecast API integration"""
        from src.providers.open_meteo import OpenMeteoProvider

        provider = OpenMeteoProvider()

        with patch.object(provider, "_get_client") as mock_client_getter:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "daily": {
                    "time": ["2026-01-08", "2026-01-09"],
                    "temperature_2m_max": [32.5, 33.8],
                    "temperature_2m_min": [18.2, 19.5],
                    "precipitation_sum": [0.0, 2.5],
                    "precipitation_probability_max": [10, 30],
                    "wind_speed_10m_max": [18.5, 15.0],
                    "uv_index_max": [9.5, 8.5],
                    "sunrise": ["2026-01-08T06:15:00", "2026-01-09T06:15:00"],
                    "sunset": ["2026-01-08T18:00:00", "2026-01-09T18:01:00"],
                }
            }
            mock_response.raise_for_status = MagicMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_getter.return_value = mock_client

            # Test API call
            forecast = await provider.get_daily_forecast(15.35, 44.20, 7)

            assert len(forecast) == 2
            assert forecast[0].temp_max_c == 32.5
            assert forecast[1].temp_max_c == 33.8

        await provider.close()

    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test API error handling"""
        from src.providers.open_meteo import OpenMeteoProvider

        provider = OpenMeteoProvider()

        with patch.object(provider, "_get_client") as mock_client_getter:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=httpx.RequestError("Network error"))
            mock_client_getter.return_value = mock_client

            # Should raise exception
            with pytest.raises(Exception):
                await provider.get_current(15.35, 44.20)

        await provider.close()


class TestCorrelationID:
    """Test correlation ID handling"""

    @pytest.mark.asyncio
    async def test_correlation_id_in_request(self, client):
        """Test correlation ID is accepted in requests"""
        with patch("src.main.app.state") as mock_state:
            mock_provider = AsyncMock()
            mock_provider.get_current = AsyncMock(
                return_value=MagicMock(
                    temperature_c=28.5,
                    humidity_pct=55.0,
                    wind_speed_kmh=12.5,
                    wind_direction_deg=180,
                    precipitation_mm=0.0,
                    cloud_cover_pct=25.0,
                    pressure_hpa=1013.0,
                    uv_index=8.0,
                    timestamp=datetime.utcnow().isoformat(),
                )
            )
            mock_state.weather_provider = mock_provider
            mock_state.multi_provider = None
            mock_state.publisher = None

            correlation_id = "test-correlation-123"
            response = client.post(
                "/weather/current",
                json={
                    "tenant_id": "tenant-123",
                    "field_id": "field-456",
                    "lat": 15.35,
                    "lon": 44.20,
                    "correlation_id": correlation_id,
                },
            )

            assert response.status_code == 200
