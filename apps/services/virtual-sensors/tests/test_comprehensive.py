"""
Comprehensive unit tests for Virtual Sensors Service.
Tests cover: calculation functions, models, enums, validation, API endpoints.
Target: >60% code coverage.
"""

import math
import os
import sys
from datetime import date, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

# Add service directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

# Import source module (shared modules are available in this environment)
from src.main import (
    CROP_COEFFICIENTS,
    IRRIGATION_EFFICIENCY,
    SENSOR_VALUE_BOUNDS,
    SOIL_PROPERTIES,
    GrowthStage,
    IrrigationMethod,
    SoilType,
    UrgencyLevel,
    WeatherInput,
    calculate_available_water,
    calculate_et0_penman_monteith,
    calculate_irrigation_recommendation,
    estimate_soil_moisture,
    get_crop_kc,
    validate_sensor_value,
    app,
)

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class FakeUser:
    """Fake user for dependency injection override."""
    id = "test-user-id"
    tenant_id = None
    email = "test@test.com"
    role = "admin"


class _TenantClient:
    """Wrapper that adds X-Tenant-ID header to all requests."""

    def __init__(self, client):
        self._client = client

    def get(self, url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.setdefault("X-Tenant-ID", "00000000-0000-0000-0000-000000000001")
        return self._client.get(url, headers=headers, **kwargs)

    def post(self, url, **kwargs):
        headers = kwargs.pop("headers", {})
        headers.setdefault("X-Tenant-ID", "00000000-0000-0000-0000-000000000001")
        return self._client.post(url, headers=headers, **kwargs)


@pytest.fixture
def client():
    """Create TestClient with mocked auth dependency and tenant header."""
    from shared.auth.dependencies import get_current_user

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    tc = TestClient(app, raise_server_exceptions=False)
    yield _TenantClient(tc)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_weather() -> WeatherInput:
    """Standard weather input for testing."""
    return WeatherInput(
        temperature_max=35.0,
        temperature_min=20.0,
        humidity=45.0,
        wind_speed=2.5,
        solar_radiation=22.0,
        latitude=15.35,
        altitude=200,
        calculation_date=date(2025, 7, 15),
    )


# ---------------------------------------------------------------------------
# Test Enums
# ---------------------------------------------------------------------------

class TestEnums:
    def test_growth_stage_values(self):
        assert GrowthStage.INITIAL == "initial"
        assert GrowthStage.DEVELOPMENT == "development"
        assert GrowthStage.MID_SEASON == "mid_season"
        assert GrowthStage.LATE_SEASON == "late_season"

    def test_soil_type_values(self):
        assert SoilType.SANDY == "sandy"
        assert SoilType.CLAY == "clay"
        assert SoilType.LOAM == "loam"
        assert len(list(SoilType)) == 6

    def test_irrigation_method_values(self):
        assert IrrigationMethod.DRIP == "drip"
        assert IrrigationMethod.FLOOD == "flood"
        assert len(list(IrrigationMethod)) == 5

    def test_urgency_level_values(self):
        assert UrgencyLevel.NONE == "none"
        assert UrgencyLevel.CRITICAL == "critical"


# ---------------------------------------------------------------------------
# Test Sensor Value Validation
# ---------------------------------------------------------------------------

class TestValidateSensorValue:
    def test_valid_temperature(self):
        valid, err = validate_sensor_value("temperature", 25.0)
        assert valid is True
        assert err is None

    def test_invalid_temperature_too_high(self):
        valid, err = validate_sensor_value("temperature", 100.0)
        assert valid is False
        assert "out of bounds" in err

    def test_invalid_temperature_too_low(self):
        valid, err = validate_sensor_value("temperature", -60.0)
        assert valid is False

    def test_valid_et0(self):
        valid, err = validate_sensor_value("et0", 5.0)
        assert valid is True

    def test_invalid_et0_negative(self):
        valid, err = validate_sensor_value("et0", -1.0)
        assert valid is False

    def test_unknown_sensor_type_always_valid(self):
        valid, err = validate_sensor_value("unknown_sensor", 999.0)
        assert valid is True
        assert err is None

    def test_boundary_values(self):
        # Exact min
        valid, _ = validate_sensor_value("humidity", 0.0)
        assert valid is True
        # Exact max
        valid, _ = validate_sensor_value("humidity", 100.0)
        assert valid is True


# ---------------------------------------------------------------------------
# Test Constants / Data Tables
# ---------------------------------------------------------------------------

class TestConstants:
    def test_crop_coefficients_has_wheat(self):
        assert "wheat" in CROP_COEFFICIENTS
        wheat = CROP_COEFFICIENTS["wheat"]
        assert "kc_initial" in wheat
        assert "kc_mid" in wheat
        assert "kc_end" in wheat
        assert "name_ar" in wheat

    def test_crop_coefficients_has_all_expected_crops(self):
        expected = ["wheat", "barley", "tomato", "date_palm", "coffee", "qat"]
        for crop in expected:
            assert crop in CROP_COEFFICIENTS, f"Missing crop: {crop}"

    def test_soil_properties_has_all_types(self):
        for soil_type in SoilType:
            assert soil_type in SOIL_PROPERTIES

    def test_soil_properties_field_capacity_gt_wilting_point(self):
        for soil_type, props in SOIL_PROPERTIES.items():
            assert props["field_capacity"] > props["wilting_point"], (
                f"Invalid soil props for {soil_type}"
            )

    def test_irrigation_efficiency_range(self):
        for method, eff in IRRIGATION_EFFICIENCY.items():
            assert 0 < eff <= 1.0, f"Invalid efficiency for {method}: {eff}"

    def test_sensor_bounds_structure(self):
        for key, bounds in SENSOR_VALUE_BOUNDS.items():
            assert "min" in bounds
            assert "max" in bounds
            assert bounds["min"] <= bounds["max"]


# ---------------------------------------------------------------------------
# Test ET0 Calculation (Penman-Monteith)
# ---------------------------------------------------------------------------

class TestET0Calculation:
    def test_et0_positive_result(self, sample_weather):
        et0 = calculate_et0_penman_monteith(sample_weather)
        assert et0 > 0
        assert isinstance(et0, float)

    def test_et0_reasonable_range(self, sample_weather):
        """ET0 for hot arid conditions should be in range 3-12 mm/day."""
        et0 = calculate_et0_penman_monteith(sample_weather)
        assert 1.0 < et0 < 15.0

    def test_et0_higher_with_more_wind(self, sample_weather):
        et0_low_wind = calculate_et0_penman_monteith(sample_weather)
        sample_weather.wind_speed = 8.0
        et0_high_wind = calculate_et0_penman_monteith(sample_weather)
        assert et0_high_wind > et0_low_wind

    def test_et0_with_sunshine_hours_instead_of_radiation(self):
        weather = WeatherInput(
            temperature_max=30.0,
            temperature_min=18.0,
            humidity=50.0,
            wind_speed=2.0,
            solar_radiation=None,
            sunshine_hours=10.0,
            latitude=15.35,
            altitude=100,
            calculation_date=date(2025, 6, 15),
        )
        et0 = calculate_et0_penman_monteith(weather)
        assert et0 > 0

    def test_et0_without_radiation_or_sunshine(self):
        """Falls back to Hargreaves estimation."""
        weather = WeatherInput(
            temperature_max=32.0,
            temperature_min=20.0,
            humidity=40.0,
            wind_speed=2.0,
            solar_radiation=None,
            sunshine_hours=None,
            latitude=15.35,
            altitude=100,
            calculation_date=date(2025, 6, 15),
        )
        et0 = calculate_et0_penman_monteith(weather)
        assert et0 > 0

    def test_et0_cold_conditions_low_value(self):
        weather = WeatherInput(
            temperature_max=5.0,
            temperature_min=-2.0,
            humidity=80.0,
            wind_speed=1.0,
            solar_radiation=5.0,
            latitude=35.0,
            altitude=500,
            calculation_date=date(2025, 1, 15),
        )
        et0 = calculate_et0_penman_monteith(weather)
        assert et0 < 3.0

    def test_et0_cannot_be_negative(self):
        """ET0 should be clamped to >= 0."""
        weather = WeatherInput(
            temperature_max=2.0,
            temperature_min=-5.0,
            humidity=99.0,
            wind_speed=0.1,
            solar_radiation=1.0,
            latitude=60.0,
            altitude=0,
            calculation_date=date(2025, 12, 21),
        )
        et0 = calculate_et0_penman_monteith(weather)
        assert et0 >= 0


# ---------------------------------------------------------------------------
# Test Crop Kc
# ---------------------------------------------------------------------------

class TestGetCropKc:
    def test_kc_initial_stage(self):
        kc = get_crop_kc("wheat", GrowthStage.INITIAL)
        assert kc == CROP_COEFFICIENTS["wheat"]["kc_initial"]

    def test_kc_mid_season(self):
        kc = get_crop_kc("wheat", GrowthStage.MID_SEASON)
        assert kc == CROP_COEFFICIENTS["wheat"]["kc_mid"]

    def test_kc_development_interpolation(self):
        kc = get_crop_kc("wheat", GrowthStage.DEVELOPMENT, days_in_stage=15)
        kc_init = CROP_COEFFICIENTS["wheat"]["kc_initial"]
        kc_mid = CROP_COEFFICIENTS["wheat"]["kc_mid"]
        assert kc_init < kc < kc_mid

    def test_kc_development_no_days(self):
        """Without days_in_stage, returns average of initial and mid."""
        kc = get_crop_kc("wheat", GrowthStage.DEVELOPMENT)
        kc_init = CROP_COEFFICIENTS["wheat"]["kc_initial"]
        kc_mid = CROP_COEFFICIENTS["wheat"]["kc_mid"]
        expected = (kc_init + kc_mid) / 2
        assert abs(kc - expected) < 0.001

    def test_kc_late_season_interpolation(self):
        kc = get_crop_kc("wheat", GrowthStage.LATE_SEASON, days_in_stage=15)
        kc_mid = CROP_COEFFICIENTS["wheat"]["kc_mid"]
        kc_end = CROP_COEFFICIENTS["wheat"]["kc_end"]
        assert kc_end < kc < kc_mid

    def test_kc_late_season_no_days(self):
        kc = get_crop_kc("wheat", GrowthStage.LATE_SEASON)
        kc_mid = CROP_COEFFICIENTS["wheat"]["kc_mid"]
        kc_end = CROP_COEFFICIENTS["wheat"]["kc_end"]
        expected = (kc_mid + kc_end) / 2
        assert abs(kc - expected) < 0.001

    def test_kc_unknown_crop_returns_default(self):
        kc = get_crop_kc("unknown_crop", GrowthStage.INITIAL)
        assert kc == 1.0

    def test_kc_all_crops_positive(self):
        for crop in CROP_COEFFICIENTS:
            for stage in GrowthStage:
                kc = get_crop_kc(crop, stage)
                assert kc > 0, f"kc should be positive for {crop}/{stage}"


# ---------------------------------------------------------------------------
# Test Available Water Calculation
# ---------------------------------------------------------------------------

class TestAvailableWater:
    def test_sandy_soil(self):
        taw, fc_mm, wp_mm = calculate_available_water(SoilType.SANDY, 1.0)
        # TAW = (0.12 - 0.04) * 1.0 * 1000 = 80 mm
        assert abs(taw - 80.0) < 0.1

    def test_clay_soil(self):
        taw, fc_mm, wp_mm = calculate_available_water(SoilType.CLAY, 1.0)
        # TAW = (0.38 - 0.25) * 1.0 * 1000 = 130 mm
        assert abs(taw - 130.0) < 0.1

    def test_deeper_roots_more_water(self):
        taw_shallow, _, _ = calculate_available_water(SoilType.LOAM, 0.5)
        taw_deep, _, _ = calculate_available_water(SoilType.LOAM, 1.5)
        assert taw_deep > taw_shallow

    def test_fc_gt_wp(self):
        for soil_type in SoilType:
            taw, fc_mm, wp_mm = calculate_available_water(soil_type, 1.0)
            assert fc_mm > wp_mm
            assert taw > 0


# ---------------------------------------------------------------------------
# Test Soil Moisture Estimation
# ---------------------------------------------------------------------------

class TestEstimateSoilMoisture:
    def test_recently_irrigated_low_depletion(self):
        """Just irrigated today with large amount should have low depletion."""
        result = estimate_soil_moisture(
            soil_type=SoilType.LOAM,
            root_depth=1.0,
            last_irrigation_date=date.today(),
            last_irrigation_amount=150.0,  # Large amount to ensure TAW is filled
            rainfall_since=0,
            daily_etc=5.0,
        )
        # With 0 days elapsed, ET loss = 0, water_input = min(150, TAW)
        # Depletion should be 0% (all TAW available)
        assert result["depletion_percent"] < 5
        assert result["status"] == "optimal"
        assert result["urgency"] == UrgencyLevel.NONE

    def test_long_ago_irrigation_critical(self):
        result = estimate_soil_moisture(
            soil_type=SoilType.SANDY,
            root_depth=0.5,
            last_irrigation_date=date.today() - timedelta(days=30),
            last_irrigation_amount=20.0,
            rainfall_since=0,
            daily_etc=6.0,
        )
        assert result["urgency"] in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]
        assert result["depletion_percent"] > 70

    def test_rainfall_reduces_depletion(self):
        result_no_rain = estimate_soil_moisture(
            soil_type=SoilType.LOAM,
            root_depth=1.0,
            last_irrigation_date=date.today() - timedelta(days=5),
            last_irrigation_amount=30.0,
            rainfall_since=0,
            daily_etc=5.0,
        )
        result_with_rain = estimate_soil_moisture(
            soil_type=SoilType.LOAM,
            root_depth=1.0,
            last_irrigation_date=date.today() - timedelta(days=5),
            last_irrigation_amount=30.0,
            rainfall_since=20.0,
            daily_etc=5.0,
        )
        assert result_with_rain["depletion_percent"] <= result_no_rain["depletion_percent"]

    def test_all_urgency_levels_reachable(self):
        """Ensure different depletion levels map to different urgency levels."""
        urgencies = set()
        for days in [0, 2, 5, 10, 30]:
            result = estimate_soil_moisture(
                soil_type=SoilType.SANDY,
                root_depth=0.5,
                last_irrigation_date=date.today() - timedelta(days=days),
                last_irrigation_amount=30.0,
                rainfall_since=0,
                daily_etc=5.0,
            )
            urgencies.add(result["urgency"])
        assert len(urgencies) >= 2


# ---------------------------------------------------------------------------
# Test Irrigation Recommendation
# ---------------------------------------------------------------------------

class TestIrrigationRecommendation:
    def test_irrigation_needed_high_depletion(self):
        moisture_status = {
            "depletion_percent": 70.0,
            "total_aw": 100.0,
            "remaining_aw": 30.0,
            "urgency": UrgencyLevel.HIGH,
        }
        result = calculate_irrigation_recommendation(
            crop_type="wheat",
            growth_stage=GrowthStage.MID_SEASON,
            soil_type=SoilType.LOAM,
            irrigation_method=IrrigationMethod.DRIP,
            field_area_hectares=1.0,
            et0=5.0,
            moisture_status=moisture_status,
        )
        assert result["irrigation_needed"] is True
        assert result["recommended_amount_mm"] > 0
        assert result["gross_irrigation_mm"] > result["recommended_amount_mm"]

    def test_no_irrigation_low_depletion(self):
        moisture_status = {
            "depletion_percent": 20.0,
            "total_aw": 100.0,
            "remaining_aw": 80.0,
            "urgency": UrgencyLevel.NONE,
        }
        result = calculate_irrigation_recommendation(
            crop_type="wheat",
            growth_stage=GrowthStage.INITIAL,
            soil_type=SoilType.LOAM,
            irrigation_method=IrrigationMethod.DRIP,
            field_area_hectares=1.0,
            et0=5.0,
            moisture_status=moisture_status,
        )
        assert result["irrigation_needed"] is False
        assert result["recommended_amount_mm"] == 0

    def test_critical_urgency_optimal_time(self):
        moisture_status = {
            "depletion_percent": 90.0,
            "total_aw": 100.0,
            "remaining_aw": 10.0,
            "urgency": UrgencyLevel.CRITICAL,
        }
        result = calculate_irrigation_recommendation(
            crop_type="wheat",
            growth_stage=GrowthStage.MID_SEASON,
            soil_type=SoilType.LOAM,
            irrigation_method=IrrigationMethod.DRIP,
            field_area_hectares=1.0,
            et0=5.0,
            moisture_status=moisture_status,
        )
        assert "Immediately" in result["optimal_time"]
        assert "فوراً" in result["optimal_time_ar"]

    def test_sandy_soil_warning(self):
        """Sandy soil with high irrigation should produce a splitting warning."""
        moisture_status = {
            "depletion_percent": 80.0,
            "total_aw": 80.0,
            "remaining_aw": 16.0,
            "urgency": UrgencyLevel.HIGH,
        }
        result = calculate_irrigation_recommendation(
            crop_type="wheat",
            growth_stage=GrowthStage.MID_SEASON,
            soil_type=SoilType.SANDY,
            irrigation_method=IrrigationMethod.SURFACE,
            field_area_hectares=1.0,
            et0=7.0,
            moisture_status=moisture_status,
        )
        assert any("Sandy" in w or "splitting" in w for w in result["warnings"])

    def test_mid_season_stress_warning(self):
        moisture_status = {
            "depletion_percent": 65.0,
            "total_aw": 100.0,
            "remaining_aw": 35.0,
            "urgency": UrgencyLevel.MEDIUM,
        }
        result = calculate_irrigation_recommendation(
            crop_type="wheat",
            growth_stage=GrowthStage.MID_SEASON,
            soil_type=SoilType.CLAY,
            irrigation_method=IrrigationMethod.DRIP,
            field_area_hectares=1.0,
            et0=5.0,
            moisture_status=moisture_status,
        )
        assert any("Critical growth stage" in w for w in result["warnings"])

    def test_gross_irrigation_accounts_for_efficiency(self):
        moisture_status = {
            "depletion_percent": 70.0,
            "total_aw": 100.0,
            "remaining_aw": 30.0,
            "urgency": UrgencyLevel.HIGH,
        }
        result_drip = calculate_irrigation_recommendation(
            crop_type="wheat",
            growth_stage=GrowthStage.MID_SEASON,
            soil_type=SoilType.LOAM,
            irrigation_method=IrrigationMethod.DRIP,
            field_area_hectares=1.0,
            et0=5.0,
            moisture_status=moisture_status,
        )
        result_flood = calculate_irrigation_recommendation(
            crop_type="wheat",
            growth_stage=GrowthStage.MID_SEASON,
            soil_type=SoilType.LOAM,
            irrigation_method=IrrigationMethod.FLOOD,
            field_area_hectares=1.0,
            et0=5.0,
            moisture_status=moisture_status,
        )
        # Flood has lower efficiency, so gross should be higher
        assert result_flood["gross_irrigation_mm"] > result_drip["gross_irrigation_mm"]


# ---------------------------------------------------------------------------
# Test WeatherInput Validation
# ---------------------------------------------------------------------------

class TestWeatherInputValidation:
    def test_valid_weather_input(self):
        w = WeatherInput(
            temperature_max=35.0,
            temperature_min=20.0,
            humidity=50.0,
            wind_speed=2.0,
            latitude=15.0,
        )
        assert w.temperature_max == 35.0

    def test_temp_max_less_than_min_raises(self):
        with pytest.raises(ValueError):
            WeatherInput(
                temperature_max=10.0,
                temperature_min=20.0,
                humidity=50.0,
                wind_speed=2.0,
                latitude=15.0,
            )


# ---------------------------------------------------------------------------
# Test API Endpoints (unauthenticated routes)
# ---------------------------------------------------------------------------

class TestHealthEndpoints:
    def test_healthz(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "virtual-sensors"
        assert data["version"] == "16.0.0"

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        assert response.json()["status"] == "ready"


class TestInfoEndpoints:
    def test_service_info(self, client):
        response = client.get("/v1/info")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "virtual-sensors"
        assert data["supported_crops"] == len(CROP_COEFFICIENTS)

    def test_supported_crops(self, client):
        response = client.get("/v1/crops")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == len(CROP_COEFFICIENTS)
        assert len(data["crops"]) == len(CROP_COEFFICIENTS)

    def test_crop_kc_all_values(self, client):
        response = client.get("/v1/crops/wheat/kc")
        assert response.status_code == 200
        data = response.json()
        assert "kc_initial" in data
        assert "kc_mid" in data
        assert "kc_end" in data

    def test_crop_kc_specific_stage(self, client):
        response = client.get(
            "/v1/crops/wheat/kc",
            params={"growth_stage": "mid_season"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "kc" in data
        assert data["growth_stage"] == "mid_season"

    def test_crop_kc_not_found(self, client):
        response = client.get("/v1/crops/unknown_crop/kc")
        assert response.status_code == 404

    def test_soil_types(self, client):
        response = client.get("/v1/soils")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == len(SOIL_PROPERTIES)

    def test_irrigation_methods(self, client):
        response = client.get("/v1/irrigation-methods")
        assert response.status_code == 200
        methods = response.json()["methods"]
        assert len(methods) == len(IRRIGATION_EFFICIENCY)
        for m in methods:
            assert 0 < m["efficiency"] <= 1.0

    def test_quick_irrigation_check(self, client):
        response = client.get(
            "/v1/irrigation/quick-check",
            params={
                "crop_type": "wheat",
                "growth_stage": "mid_season",
                "soil_type": "loam",
                "days_since_irrigation": 5,
                "temperature": 30.0,
                "humidity": 40.0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "needs_irrigation" in data
        assert "estimated_etc" in data

    def test_quick_check_unknown_crop(self, client):
        response = client.get(
            "/v1/irrigation/quick-check",
            params={
                "crop_type": "nonexistent",
                "growth_stage": "mid_season",
                "days_since_irrigation": 3,
                "temperature": 25.0,
            },
        )
        assert response.status_code == 404
