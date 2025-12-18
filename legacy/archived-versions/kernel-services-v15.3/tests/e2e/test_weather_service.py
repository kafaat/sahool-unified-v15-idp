"""
E2E Tests for Weather Advanced Service - خدمة الطقس المتقدمة
Tests weather forecasts, alerts, and agricultural calendar
"""

import pytest
import httpx
from conftest import WEATHER_URL


class TestWeatherServiceHealth:
    """Health check tests for weather service."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: httpx.AsyncClient):
        """Test /healthz returns healthy status."""
        response = await async_client.get(f"{WEATHER_URL}/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "location_count" in data
        assert data["location_count"] >= 22  # All Yemen governorates


class TestLocationsEndpoint:
    """Tests for /v1/locations endpoint."""

    @pytest.mark.asyncio
    async def test_get_all_yemen_locations(self, async_client: httpx.AsyncClient):
        """Test listing all Yemen locations with coordinates."""
        response = await async_client.get(f"{WEATHER_URL}/v1/locations")
        assert response.status_code == 200
        data = response.json()

        assert "locations" in data
        locations = data["locations"]

        # Should have all 22 Yemen governorates
        assert len(locations) >= 22

        # Check location structure
        for loc in locations:
            assert "id" in loc
            assert "name_ar" in loc
            assert "lat" in loc
            assert "lon" in loc
            assert "elevation" in loc

        # Verify specific locations
        location_ids = [loc["id"] for loc in locations]
        expected_locations = ["sana'a", "aden", "taiz", "hodeidah", "socotra", "marib"]
        for expected in expected_locations:
            assert expected in location_ids

    @pytest.mark.asyncio
    async def test_locations_have_elevation(self, async_client: httpx.AsyncClient):
        """Test that locations include elevation data."""
        response = await async_client.get(f"{WEATHER_URL}/v1/locations")
        data = response.json()

        # Sana'a should be highland (>2000m)
        sanaa = next(loc for loc in data["locations"] if loc["id"] == "sana'a")
        assert sanaa["elevation"] >= 2000

        # Aden should be coastal (<100m)
        aden = next(loc for loc in data["locations"] if loc["id"] == "aden")
        assert aden["elevation"] < 100


class TestCurrentWeather:
    """Tests for /v1/current/{location_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_current_weather_sanaa(self, async_client: httpx.AsyncClient):
        """Test current weather for Sana'a."""
        response = await async_client.get(f"{WEATHER_URL}/v1/current/sana'a")
        assert response.status_code == 200
        data = response.json()

        # Required fields
        assert "location_id" in data
        assert "temperature" in data
        assert "humidity" in data
        assert "wind_speed" in data
        assert "condition" in data
        assert "condition_ar" in data

        # Temperature should be reasonable
        assert -10 <= data["temperature"] <= 50

        # Humidity between 0-100%
        assert 0 <= data["humidity"] <= 100

    @pytest.mark.asyncio
    async def test_current_weather_invalid_location(self, async_client: httpx.AsyncClient):
        """Test current weather for invalid location."""
        response = await async_client.get(f"{WEATHER_URL}/v1/current/invalid_location")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_current_weather_multiple_locations(self, async_client: httpx.AsyncClient, yemen_locations):
        """Test current weather for multiple Yemen locations."""
        for loc in yemen_locations:
            response = await async_client.get(f"{WEATHER_URL}/v1/current/{loc['id']}")
            assert response.status_code == 200
            data = response.json()
            assert data["location_id"] == loc["id"]


class TestWeatherForecast:
    """Tests for /v1/forecast/{location_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_7day_forecast(self, async_client: httpx.AsyncClient):
        """Test 7-day weather forecast."""
        response = await async_client.get(f"{WEATHER_URL}/v1/forecast/sana'a")
        assert response.status_code == 200
        data = response.json()

        assert "location_id" in data
        assert "daily_forecast" in data
        assert "hourly_forecast" in data

        # Should have 7 days
        daily = data["daily_forecast"]
        assert len(daily) == 7

        # Each day should have required fields
        for day in daily:
            assert "date" in day
            assert "temp_max" in day
            assert "temp_min" in day
            assert "precipitation_mm" in day
            assert "condition" in day

            # Max should be >= Min
            assert day["temp_max"] >= day["temp_min"]

    @pytest.mark.asyncio
    async def test_forecast_includes_agricultural_data(self, async_client: httpx.AsyncClient):
        """Test that forecast includes agricultural recommendations."""
        response = await async_client.get(f"{WEATHER_URL}/v1/forecast/sana'a")
        data = response.json()

        # Check for agricultural data
        assert "et0" in data or "evapotranspiration" in data
        assert "gdd" in data or "growing_degree_days" in data

        # Check daily data has spray windows
        for day in data["daily_forecast"]:
            assert "spray_window" in day or "suitable_for_spraying" in day

    @pytest.mark.asyncio
    async def test_hourly_forecast(self, async_client: httpx.AsyncClient):
        """Test hourly forecast data (48 hours)."""
        response = await async_client.get(f"{WEATHER_URL}/v1/forecast/aden")
        data = response.json()

        hourly = data["hourly_forecast"]
        assert len(hourly) >= 24  # At least 24 hours

        for hour in hourly[:24]:
            assert "datetime" in hour
            assert "temperature" in hour
            assert "humidity" in hour


class TestWeatherAlerts:
    """Tests for /v1/alerts/{location_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_weather_alerts(self, async_client: httpx.AsyncClient):
        """Test weather alerts endpoint."""
        response = await async_client.get(f"{WEATHER_URL}/v1/alerts/sana'a")
        assert response.status_code == 200
        data = response.json()

        assert "location_id" in data
        assert "alerts" in data
        assert isinstance(data["alerts"], list)

        # If there are alerts, check structure
        for alert in data["alerts"]:
            assert "type" in alert
            assert "severity" in alert
            assert "message" in alert
            assert "message_ar" in alert
            assert alert["severity"] in ["info", "warning", "critical"]

    @pytest.mark.asyncio
    async def test_alert_types(self, async_client: httpx.AsyncClient):
        """Test that known alert types are supported."""
        response = await async_client.get(f"{WEATHER_URL}/v1/alerts/hodeidah")
        data = response.json()

        valid_alert_types = [
            "heat_wave", "frost", "heavy_rain", "drought",
            "high_wind", "high_humidity", "low_humidity", "dust_storm"
        ]

        for alert in data["alerts"]:
            assert alert["type"] in valid_alert_types


class TestAgriculturalCalendar:
    """Tests for /v1/agricultural-calendar/{location_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_agricultural_calendar(self, async_client: httpx.AsyncClient):
        """Test agricultural calendar by month."""
        response = await async_client.get(
            f"{WEATHER_URL}/v1/agricultural-calendar/sana'a",
            params={"month": 3}  # March
        )
        assert response.status_code == 200
        data = response.json()

        assert "location_id" in data
        assert "month" in data
        assert "crops" in data

        # Check crop recommendations
        crops = data["crops"]
        assert len(crops) > 0

        for crop in crops:
            assert "name" in crop
            assert "name_ar" in crop
            assert "activities" in crop
            assert isinstance(crop["activities"], list)

    @pytest.mark.asyncio
    async def test_calendar_all_months(self, async_client: httpx.AsyncClient):
        """Test calendar is available for all months."""
        for month in range(1, 13):
            response = await async_client.get(
                f"{WEATHER_URL}/v1/agricultural-calendar/taiz",
                params={"month": month}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["month"] == month
