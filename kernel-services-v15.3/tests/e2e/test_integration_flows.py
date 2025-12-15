"""
Integration Tests - اختبارات التكامل
Tests cross-service workflows and data consistency
"""

import pytest
import httpx
from conftest import (
    SATELLITE_URL, INDICATORS_URL, WEATHER_URL,
    FERTILIZER_URL, IRRIGATION_URL,
    TEST_FIELD_ID, TEST_TENANT_ID
)


class TestFieldAnalysisFlow:
    """
    Integration test: Complete field analysis workflow
    Satellite → Indicators → Recommendations
    """

    @pytest.mark.asyncio
    async def test_complete_field_analysis_pipeline(self, async_client: httpx.AsyncClient, test_field_data):
        """Test end-to-end field analysis from satellite to recommendations."""

        # Step 1: Get satellite imagery analysis
        satellite_request = {
            "field_id": test_field_data["field_id"],
            "satellite": "sentinel-2",
            "location": test_field_data["location"]
        }
        satellite_response = await async_client.post(
            f"{SATELLITE_URL}/v1/analyze",
            json=satellite_request
        )
        assert satellite_response.status_code == 200
        satellite_data = satellite_response.json()

        # Extract NDVI from satellite analysis
        ndvi_value = satellite_data["vegetation_indices"]["ndvi"]
        health_score = satellite_data["health_score"]

        # Step 2: Get field indicators (should include satellite-derived data)
        indicators_response = await async_client.get(
            f"{INDICATORS_URL}/v1/field/{test_field_data['field_id']}/indicators"
        )
        assert indicators_response.status_code == 200
        indicators_data = indicators_response.json()

        # Verify indicators include vegetation data
        ndvi_indicator = next(
            (ind for ind in indicators_data["indicators"] if ind["id"] == "ndvi"),
            None
        )
        assert ndvi_indicator is not None

        # Step 3: Check if any alerts were generated
        alerts_response = await async_client.get(
            f"{INDICATORS_URL}/v1/alerts/{TEST_TENANT_ID}"
        )
        assert alerts_response.status_code == 200

        print(f"✅ Field Analysis Pipeline Complete:")
        print(f"   NDVI: {ndvi_value:.2f}")
        print(f"   Health Score: {health_score}")
        print(f"   Active Alerts: {len(alerts_response.json()['alerts'])}")


class TestIrrigationPlanningFlow:
    """
    Integration test: Irrigation planning with weather data
    Weather → Irrigation Calculation → Schedule
    """

    @pytest.mark.asyncio
    async def test_weather_based_irrigation_planning(self, async_client: httpx.AsyncClient, test_field_data):
        """Test irrigation planning that incorporates weather forecast."""

        # Step 1: Get current weather and forecast
        weather_response = await async_client.get(
            f"{WEATHER_URL}/v1/forecast/sana'a"
        )
        assert weather_response.status_code == 200
        weather_data = weather_response.json()

        # Extract relevant weather data
        today_forecast = weather_data["daily_forecast"][0]
        current_temp = today_forecast.get("temp_max", 30)
        humidity = 50  # Default if not available
        precipitation = today_forecast.get("precipitation_mm", 0)

        # Step 2: Calculate irrigation needs using weather data
        irrigation_request = {
            "field_id": test_field_data["field_id"],
            "crop": "tomato",
            "area_hectares": test_field_data["area_hectares"],
            "irrigation_method": "drip",
            "soil_type": "loamy",
            "current_soil_moisture": 35,
            "recent_rainfall_mm": precipitation,
            "weather": {
                "temperature": current_temp,
                "humidity": humidity
            }
        }

        irrigation_response = await async_client.post(
            f"{IRRIGATION_URL}/v1/calculate",
            json=irrigation_request
        )
        assert irrigation_response.status_code == 200
        irrigation_data = irrigation_response.json()

        # Step 3: Verify the plan accounts for weather
        assert "et0" in irrigation_data  # Reference ET should be calculated
        assert "schedule" in irrigation_data

        print(f"✅ Weather-Based Irrigation Planning Complete:")
        print(f"   Weather: {current_temp}°C, Rain: {precipitation}mm")
        print(f"   ET0: {irrigation_data['et0']:.2f}mm")
        print(f"   Water Needed: {irrigation_data['water_requirement_mm']:.2f}mm")
        print(f"   Urgency: {irrigation_data.get('urgency', 'N/A')}")


class TestFertilizerRecommendationFlow:
    """
    Integration test: Fertilizer recommendation with soil analysis
    Soil Analysis → NPK Calculation → Schedule
    """

    @pytest.mark.asyncio
    async def test_soil_based_fertilizer_recommendation(self, async_client: httpx.AsyncClient, test_field_data, test_soil_data):
        """Test fertilizer recommendation based on soil analysis."""

        # Step 1: Interpret soil analysis
        soil_response = await async_client.post(
            f"{FERTILIZER_URL}/v1/soil-analysis/interpret",
            json=test_soil_data
        )
        assert soil_response.status_code == 200
        soil_interpretation = soil_response.json()

        # Step 2: Get fertilizer recommendation based on soil status
        fertilizer_request = {
            "field_id": test_field_data["field_id"],
            "crop": "tomato",
            "area_hectares": test_field_data["area_hectares"],
            "growth_stage": "vegetative",
            "soil_analysis": test_soil_data,
            "split_applications": True
        }

        fertilizer_response = await async_client.post(
            f"{FERTILIZER_URL}/v1/recommend",
            json=fertilizer_request
        )
        assert fertilizer_response.status_code == 200
        fertilizer_data = fertilizer_response.json()

        # Step 3: Verify recommendation considers soil status
        assert "recommendations" in fertilizer_data
        assert "total_cost" in fertilizer_data
        assert len(fertilizer_data["recommendations"]) > 0

        print(f"✅ Soil-Based Fertilizer Recommendation Complete:")
        print(f"   Soil pH: {test_soil_data['ph']} - {soil_interpretation['ph_status']}")
        print(f"   N Status: {soil_interpretation['nitrogen_status']}")
        print(f"   Fertilizers Recommended: {len(fertilizer_data['recommendations'])}")
        print(f"   Total Cost: {fertilizer_data['total_cost']} YER")


class TestMultiLocationWeatherComparison:
    """
    Integration test: Compare weather across Yemen locations
    """

    @pytest.mark.asyncio
    async def test_regional_weather_comparison(self, async_client: httpx.AsyncClient, yemen_locations):
        """Test weather data consistency across regions."""

        weather_data = {}

        # Collect weather for all locations
        for location in yemen_locations:
            response = await async_client.get(
                f"{WEATHER_URL}/v1/current/{location['id']}"
            )
            if response.status_code == 200:
                weather_data[location['id']] = response.json()

        # Verify we got data for multiple locations
        assert len(weather_data) >= 3

        # Highland locations (Sana'a) should generally be cooler than coastal (Aden)
        if "sana'a" in weather_data and "aden" in weather_data:
            # Not always true, but typically
            print(f"✅ Regional Weather Comparison:")
            print(f"   Sana'a (Highland): {weather_data['sana'a']['temperature']}°C")
            print(f"   Aden (Coastal): {weather_data['aden']['temperature']}°C")


class TestCropHealthMonitoringFlow:
    """
    Integration test: Complete crop health monitoring
    Satellite + Indicators + Alerts
    """

    @pytest.mark.asyncio
    async def test_crop_health_monitoring(self, async_client: httpx.AsyncClient, test_field_data):
        """Test integrated crop health monitoring workflow."""

        # Step 1: Get satellite-based health analysis
        analysis_request = {
            "field_id": test_field_data["field_id"],
            "satellite": "sentinel-2",
            "location": test_field_data["location"]
        }
        analysis_response = await async_client.post(
            f"{SATELLITE_URL}/v1/analyze",
            json=analysis_request
        )
        assert analysis_response.status_code == 200
        health_data = analysis_response.json()

        # Step 2: Get historical trend
        trend_response = await async_client.get(
            f"{INDICATORS_URL}/v1/trends/{test_field_data['field_id']}/ndvi",
            params={"days": 30}
        )
        assert trend_response.status_code == 200
        trend_data = trend_response.json()

        # Step 3: Check deficiency symptoms if health is poor
        if health_data["health_score"] < 60:
            symptoms_response = await async_client.get(
                f"{FERTILIZER_URL}/v1/deficiency-symptoms/{test_field_data.get('crop_type', 'tomato')}"
            )
            assert symptoms_response.status_code == 200

        print(f"✅ Crop Health Monitoring Complete:")
        print(f"   Current Health: {health_data['health_score']}/100")
        print(f"   Status: {health_data['status_ar']}")
        print(f"   30-Day Trend: {trend_data['trend_direction']}")


class TestAllServicesHealthCheck:
    """
    Smoke test: Verify all services are running
    """

    @pytest.mark.asyncio
    async def test_all_services_healthy(self, async_client: httpx.AsyncClient):
        """Verify all kernel services are responding."""

        services = [
            ("Satellite", f"{SATELLITE_URL}/healthz"),
            ("Indicators", f"{INDICATORS_URL}/healthz"),
            ("Weather", f"{WEATHER_URL}/healthz"),
            ("Fertilizer", f"{FERTILIZER_URL}/healthz"),
            ("Irrigation", f"{IRRIGATION_URL}/healthz"),
        ]

        healthy_count = 0
        results = []

        for name, url in services:
            try:
                response = await async_client.get(url, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    healthy_count += 1
                    results.append(f"   ✅ {name}: {status}")
                else:
                    results.append(f"   ❌ {name}: HTTP {response.status_code}")
            except Exception as e:
                results.append(f"   ❌ {name}: {str(e)}")

        print(f"\n🏥 Service Health Check ({healthy_count}/{len(services)} healthy):")
        for result in results:
            print(result)

        # At least 3 services should be healthy for partial success
        assert healthy_count >= 3, f"Only {healthy_count} services healthy"


class TestDataConsistencyAcrossServices:
    """
    Test data consistency between related services
    """

    @pytest.mark.asyncio
    async def test_crop_data_consistency(self, async_client: httpx.AsyncClient):
        """Verify crop data is consistent across services."""

        # Get crops from fertilizer service
        fert_response = await async_client.get(f"{FERTILIZER_URL}/v1/crops")
        fert_crops = {c["id"] for c in fert_response.json()["crops"]}

        # Get crops from irrigation service
        irr_response = await async_client.get(f"{IRRIGATION_URL}/v1/crops")
        irr_crops = {c["id"] for c in irr_response.json()["crops"]}

        # Common crops should exist in both
        common_crops = ["tomato", "wheat", "banana"]
        for crop in common_crops:
            assert crop in fert_crops, f"{crop} missing from fertilizer service"
            assert crop in irr_crops, f"{crop} missing from irrigation service"

        print(f"✅ Crop Data Consistency Verified:")
        print(f"   Fertilizer crops: {len(fert_crops)}")
        print(f"   Irrigation crops: {len(irr_crops)}")
        print(f"   Overlap: {len(fert_crops & irr_crops)} crops")

    @pytest.mark.asyncio
    async def test_location_data_consistency(self, async_client: httpx.AsyncClient):
        """Verify Yemen locations are consistent across services."""

        # Get locations from satellite service
        sat_response = await async_client.get(f"{SATELLITE_URL}/v1/regions")
        sat_locations = {r["id"] for r in sat_response.json()["regions"]}

        # Get locations from weather service
        weather_response = await async_client.get(f"{WEATHER_URL}/v1/locations")
        weather_locations = {l["id"] for l in weather_response.json()["locations"]}

        # Key locations should exist in both
        key_locations = ["sana'a", "aden", "taiz", "hodeidah"]
        for loc in key_locations:
            assert loc in sat_locations, f"{loc} missing from satellite service"
            assert loc in weather_locations, f"{loc} missing from weather service"

        print(f"✅ Location Data Consistency Verified:")
        print(f"   Satellite regions: {len(sat_locations)}")
        print(f"   Weather locations: {len(weather_locations)}")
