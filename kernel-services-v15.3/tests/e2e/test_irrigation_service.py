"""
E2E Tests for Irrigation Smart Service - خدمة الري الذكي
Tests irrigation scheduling, water balance, and efficiency analysis
"""

import pytest
import httpx
from conftest import IRRIGATION_URL, TEST_FIELD_ID


class TestIrrigationServiceHealth:
    """Health check tests for irrigation service."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: httpx.AsyncClient):
        """Test /healthz returns healthy status."""
        response = await async_client.get(f"{IRRIGATION_URL}/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "crop_count" in data
        assert data["crop_count"] >= 15  # At least 15 crops supported


class TestCropWaterRequirements:
    """Tests for /v1/crops endpoint - water requirements."""

    @pytest.mark.asyncio
    async def test_get_crop_water_requirements(self, async_client: httpx.AsyncClient):
        """Test listing crop water requirements."""
        response = await async_client.get(f"{IRRIGATION_URL}/v1/crops")
        assert response.status_code == 200
        data = response.json()

        assert "crops" in data
        crops = data["crops"]

        # Should have at least 15 crops
        assert len(crops) >= 15

        # Check crop structure
        for crop in crops:
            assert "id" in crop
            assert "name_ar" in crop
            assert "daily_water_mm" in crop
            assert "kc" in crop  # Crop coefficient

            # Water requirement should be positive
            assert crop["daily_water_mm"] > 0
            # Kc typically 0.3 - 1.2
            assert 0.2 <= crop["kc"] <= 1.5


class TestIrrigationMethods:
    """Tests for /v1/methods endpoint."""

    @pytest.mark.asyncio
    async def test_get_irrigation_methods(self, async_client: httpx.AsyncClient):
        """Test listing irrigation methods with efficiency."""
        response = await async_client.get(f"{IRRIGATION_URL}/v1/methods")
        assert response.status_code == 200
        data = response.json()

        assert "methods" in data
        methods = data["methods"]

        # Should have at least 5 methods
        assert len(methods) >= 5

        # Check for expected methods
        method_ids = [m["id"] for m in methods]
        expected_methods = ["drip", "sprinkler", "furrow", "flood", "traditional"]
        for expected in expected_methods:
            assert expected in method_ids

        # Validate structure and efficiency
        drip = next(m for m in methods if m["id"] == "drip")
        assert "name_ar" in drip
        assert "efficiency" in drip
        assert drip["efficiency"] >= 0.85  # Drip should be 85%+ efficient

        # Efficiency should be ordered
        traditional = next(m for m in methods if m["id"] == "traditional")
        assert drip["efficiency"] > traditional["efficiency"]


class TestIrrigationCalculation:
    """Tests for /v1/calculate endpoint - irrigation planning."""

    @pytest.mark.asyncio
    async def test_calculate_irrigation_plan(self, async_client: httpx.AsyncClient, test_field_data):
        """Test irrigation plan calculation."""
        request_data = {
            "field_id": test_field_data["field_id"],
            "crop": "tomato",
            "area_hectares": test_field_data["area_hectares"],
            "irrigation_method": "drip",
            "soil_type": "loamy",
            "current_soil_moisture": 35,  # %
            "weather": {
                "temperature": 32,
                "humidity": 45,
                "wind_speed": 8
            }
        }

        response = await async_client.post(
            f"{IRRIGATION_URL}/v1/calculate",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()

        # Check plan structure
        assert "field_id" in data
        assert "crop" in data
        assert "et0" in data  # Reference evapotranspiration
        assert "etc" in data  # Crop evapotranspiration
        assert "water_requirement_mm" in data
        assert "water_requirement_liters" in data
        assert "irrigation_duration_minutes" in data
        assert "schedule" in data

        # Water requirement should be positive
        assert data["water_requirement_mm"] > 0
        assert data["water_requirement_liters"] > 0

    @pytest.mark.asyncio
    async def test_calculate_with_recent_rainfall(self, async_client: httpx.AsyncClient, test_field_data):
        """Test irrigation adjusts for recent rainfall."""
        # Without rain
        request_no_rain = {
            "field_id": test_field_data["field_id"],
            "crop": "wheat",
            "area_hectares": 10,
            "irrigation_method": "sprinkler",
            "soil_type": "clay",
            "current_soil_moisture": 30,
            "recent_rainfall_mm": 0,
            "weather": {"temperature": 28, "humidity": 50}
        }

        response_no_rain = await async_client.post(
            f"{IRRIGATION_URL}/v1/calculate",
            json=request_no_rain
        )
        data_no_rain = response_no_rain.json()

        # With rain
        request_with_rain = {**request_no_rain, "recent_rainfall_mm": 15}
        response_with_rain = await async_client.post(
            f"{IRRIGATION_URL}/v1/calculate",
            json=request_with_rain
        )
        data_with_rain = response_with_rain.json()

        # Water requirement should be lower with rain
        assert data_with_rain["water_requirement_mm"] < data_no_rain["water_requirement_mm"]

    @pytest.mark.asyncio
    async def test_calculate_urgency_levels(self, async_client: httpx.AsyncClient, test_field_data):
        """Test irrigation urgency classification."""
        # Low moisture - should be urgent
        request_urgent = {
            "field_id": test_field_data["field_id"],
            "crop": "tomato",
            "area_hectares": 5,
            "irrigation_method": "drip",
            "soil_type": "sandy",
            "current_soil_moisture": 15,  # Very low
            "weather": {"temperature": 35, "humidity": 30}
        }

        response = await async_client.post(
            f"{IRRIGATION_URL}/v1/calculate",
            json=request_urgent
        )
        data = response.json()

        assert "urgency" in data
        assert data["urgency"] in ["low", "medium", "high", "critical"]
        # Low moisture + high temp should be high or critical
        assert data["urgency"] in ["high", "critical"]

    @pytest.mark.asyncio
    async def test_calculate_multiday_schedule(self, async_client: httpx.AsyncClient, test_field_data):
        """Test multi-day irrigation schedule."""
        request_data = {
            "field_id": test_field_data["field_id"],
            "crop": "banana",
            "area_hectares": 3,
            "irrigation_method": "drip",
            "soil_type": "loamy",
            "current_soil_moisture": 40,
            "schedule_days": 7,
            "weather": {"temperature": 30, "humidity": 60}
        }

        response = await async_client.post(
            f"{IRRIGATION_URL}/v1/calculate",
            json=request_data
        )
        data = response.json()

        assert "schedule" in data
        schedule = data["schedule"]
        assert len(schedule) <= 7

        for day in schedule:
            assert "date" in day or "day" in day
            assert "water_mm" in day
            assert "duration_minutes" in day


class TestWaterBalance:
    """Tests for /v1/water-balance/{field_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_water_balance(self, async_client: httpx.AsyncClient):
        """Test water balance tracking."""
        response = await async_client.get(
            f"{IRRIGATION_URL}/v1/water-balance/{TEST_FIELD_ID}",
            params={"days": 30}
        )
        assert response.status_code == 200
        data = response.json()

        assert "field_id" in data
        assert "period_days" in data
        assert "balance" in data

        balance = data["balance"]
        assert "total_irrigation_mm" in balance
        assert "total_rainfall_mm" in balance
        assert "total_et_mm" in balance
        assert "net_balance_mm" in balance

    @pytest.mark.asyncio
    async def test_water_balance_different_periods(self, async_client: httpx.AsyncClient):
        """Test water balance for different time periods."""
        for days in [14, 30, 60]:
            response = await async_client.get(
                f"{IRRIGATION_URL}/v1/water-balance/{TEST_FIELD_ID}",
                params={"days": days}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["period_days"] == days


class TestSensorReading:
    """Tests for /v1/sensor-reading endpoint."""

    @pytest.mark.asyncio
    async def test_record_sensor_reading(self, async_client: httpx.AsyncClient):
        """Test recording soil moisture sensor data."""
        sensor_data = {
            "field_id": TEST_FIELD_ID,
            "sensor_id": "SM001",
            "soil_moisture_percent": 42.5,
            "soil_temperature": 24.3,
            "depth_cm": 30
        }

        response = await async_client.post(
            f"{IRRIGATION_URL}/v1/sensor-reading",
            json=sensor_data
        )
        assert response.status_code in [200, 201]
        data = response.json()

        assert "status" in data
        assert "reading_id" in data or "recorded" in data

    @pytest.mark.asyncio
    async def test_sensor_reading_triggers_recommendation(self, async_client: httpx.AsyncClient):
        """Test that low sensor reading triggers irrigation recommendation."""
        sensor_data = {
            "field_id": TEST_FIELD_ID,
            "sensor_id": "SM002",
            "soil_moisture_percent": 18.0,  # Very low
            "depth_cm": 30
        }

        response = await async_client.post(
            f"{IRRIGATION_URL}/v1/sensor-reading",
            json=sensor_data
        )
        assert response.status_code in [200, 201]
        data = response.json()

        # Should include recommendation or alert
        assert "recommendation" in data or "alert" in data or "action_needed" in data


class TestEfficiencyReport:
    """Tests for /v1/efficiency-report/{field_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_efficiency_report(self, async_client: httpx.AsyncClient):
        """Test irrigation efficiency comparison report."""
        response = await async_client.get(
            f"{IRRIGATION_URL}/v1/efficiency-report/{TEST_FIELD_ID}"
        )
        assert response.status_code == 200
        data = response.json()

        assert "field_id" in data
        assert "current_method" in data
        assert "efficiency_comparison" in data
        assert "roi_analysis" in data

        # Efficiency comparison should show all methods
        comparison = data["efficiency_comparison"]
        assert len(comparison) >= 3

        for method in comparison:
            assert "method_id" in method
            assert "efficiency" in method
            assert "water_saved_percent" in method or "water_usage_factor" in method

    @pytest.mark.asyncio
    async def test_efficiency_roi_calculation(self, async_client: httpx.AsyncClient):
        """Test ROI calculation for method switching."""
        response = await async_client.get(
            f"{IRRIGATION_URL}/v1/efficiency-report/{TEST_FIELD_ID}"
        )
        data = response.json()

        roi = data["roi_analysis"]
        assert "recommended_method" in roi
        assert "payback_period_months" in roi or "annual_savings" in roi
        assert "water_cost_per_m3" in roi
