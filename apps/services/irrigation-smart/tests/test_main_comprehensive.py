"""
Comprehensive tests for irrigation-smart service main.py
Tests cover: enums, models, calculation functions, API endpoints, NATS publishing
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import math
from datetime import UTC, date, datetime, timedelta, time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# We need to mock heavy shared imports before importing main
# ---------------------------------------------------------------------------

# Mock shared modules that are imported at module level
sys.modules.setdefault("structlog", MagicMock())
sys.modules.setdefault("nats", MagicMock())
sys.modules.setdefault("jwt", MagicMock())

# Mock shared.errors_py
_mock_errors = MagicMock()
_mock_errors.add_request_id_middleware = MagicMock()
_mock_errors.setup_exception_handlers = MagicMock()
sys.modules.setdefault("shared", MagicMock())
sys.modules.setdefault("shared.errors_py", _mock_errors)
sys.modules.setdefault("shared.middleware", MagicMock())
sys.modules.setdefault("shared.middleware.security_headers", MagicMock())

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class _FakeTenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        return await call_next(request)


_mock_tenant = MagicMock()
_mock_tenant.TenantContextMiddleware = _FakeTenantMiddleware
sys.modules["shared.middleware.tenant_context"] = _mock_tenant

sys.modules.setdefault("shared.contracts", MagicMock())
sys.modules.setdefault("shared.contracts.actions", MagicMock())

# Now import the source module
from src.main import (
    CropType,
    GrowthStage,
    SoilType,
    IrrigationMethod,
    UrgencyLevel,
    IrrigationRequest,
    IrrigationSchedule,
    IrrigationPlan,
    SoilMoistureReading,
    WaterBalance,
    IrrigationExecution,
    CROP_TRANSLATIONS,
    STAGE_TRANSLATIONS,
    METHOD_TRANSLATIONS,
    URGENCY_TRANSLATIONS,
    CROP_WATER_REQUIREMENTS,
    SOIL_WATER_CAPACITY,
    IRRIGATION_EFFICIENCY,
    WATER_COST_PER_M3,
    calculate_et0,
    calculate_crop_et,
    calculate_water_need,
    determine_irrigation_time,
    calculate_duration,
    generate_reasoning,
    publish_event,
    get_current_user,
    app,
)


# ============================================================================
# Enum Tests
# ============================================================================


class TestCropTypeEnum:
    """Test CropType string enum values."""

    def test_all_crops_defined(self):
        assert len(CropType) == 15

    def test_crop_values(self):
        assert CropType.TOMATO == "tomato"
        assert CropType.WHEAT == "wheat"
        assert CropType.COFFEE == "coffee"
        assert CropType.QAT == "qat"
        assert CropType.BANANA == "banana"
        assert CropType.DATE_PALM == "date_palm"
        assert CropType.ALFALFA == "alfalfa"

    def test_crop_is_str(self):
        assert isinstance(CropType.TOMATO, str)
        assert CropType.TOMATO.upper() == "TOMATO"


class TestGrowthStageEnum:
    def test_all_stages_defined(self):
        assert len(GrowthStage) == 5

    def test_stage_values(self):
        assert GrowthStage.SEEDLING == "seedling"
        assert GrowthStage.FLOWERING == "flowering"
        assert GrowthStage.MATURITY == "maturity"


class TestSoilTypeEnum:
    def test_all_soil_types(self):
        expected = {"sandy", "clay", "loamy", "silt", "rocky"}
        actual = {s.value for s in SoilType}
        assert actual == expected


class TestIrrigationMethodEnum:
    def test_all_methods(self):
        assert len(IrrigationMethod) == 5

    def test_method_values(self):
        assert IrrigationMethod.DRIP == "drip"
        assert IrrigationMethod.FLOOD == "flood"
        assert IrrigationMethod.SPRINKLER == "sprinkler"


class TestUrgencyLevelEnum:
    def test_urgency_values(self):
        assert UrgencyLevel.LOW == "low"
        assert UrgencyLevel.CRITICAL == "critical"


# ============================================================================
# Translation Dictionary Tests
# ============================================================================


class TestTranslations:
    def test_all_crops_have_translations(self):
        for crop in CropType:
            assert crop in CROP_TRANSLATIONS, f"Missing Arabic translation for {crop}"

    def test_all_stages_have_translations(self):
        for stage in GrowthStage:
            assert stage in STAGE_TRANSLATIONS

    def test_all_methods_have_translations(self):
        for method in IrrigationMethod:
            assert method in METHOD_TRANSLATIONS

    def test_all_urgencies_have_translations(self):
        for urgency in UrgencyLevel:
            assert urgency in URGENCY_TRANSLATIONS

    def test_specific_translations(self):
        assert CROP_TRANSLATIONS[CropType.WHEAT] == "قمح"
        assert STAGE_TRANSLATIONS[GrowthStage.FLOWERING] == "إزهار"
        assert METHOD_TRANSLATIONS[IrrigationMethod.DRIP] == "ري بالتنقيط"
        assert URGENCY_TRANSLATIONS[UrgencyLevel.CRITICAL] == "حرج"


# ============================================================================
# Data Constants Tests
# ============================================================================


class TestConstants:
    def test_crop_water_requirements_covers_all_crops(self):
        for crop in CropType:
            assert crop in CROP_WATER_REQUIREMENTS

    def test_crop_water_requirements_covers_all_stages(self):
        for crop in CropType:
            for stage in GrowthStage:
                assert stage in CROP_WATER_REQUIREMENTS[crop]

    def test_soil_water_capacity(self):
        assert SOIL_WATER_CAPACITY[SoilType.SANDY] < SOIL_WATER_CAPACITY[SoilType.CLAY]
        assert SOIL_WATER_CAPACITY[SoilType.ROCKY] < SOIL_WATER_CAPACITY[SoilType.SANDY]

    def test_irrigation_efficiency(self):
        assert IRRIGATION_EFFICIENCY[IrrigationMethod.DRIP] == 0.90
        assert IRRIGATION_EFFICIENCY[IrrigationMethod.FLOOD] == 0.50
        # Drip should be most efficient
        for method in IrrigationMethod:
            assert IRRIGATION_EFFICIENCY[method] <= IRRIGATION_EFFICIENCY[IrrigationMethod.DRIP]

    def test_water_cost_is_positive(self):
        assert WATER_COST_PER_M3 > 0


# ============================================================================
# Calculation Function Tests
# ============================================================================


class TestCalculateET0:
    def test_basic_calculation(self):
        result = calculate_et0(temperature=30, humidity=50, wind_speed=10)
        assert isinstance(result, float)
        assert result > 0

    def test_higher_temp_increases_et0(self):
        low = calculate_et0(temperature=20, humidity=50, wind_speed=10)
        high = calculate_et0(temperature=40, humidity=50, wind_speed=10)
        assert high > low

    def test_lower_humidity_increases_et0(self):
        dry = calculate_et0(temperature=30, humidity=20, wind_speed=10)
        wet = calculate_et0(temperature=30, humidity=80, wind_speed=10)
        assert dry > wet

    def test_higher_wind_increases_et0(self):
        calm = calculate_et0(temperature=30, humidity=50, wind_speed=2)
        windy = calculate_et0(temperature=30, humidity=50, wind_speed=20)
        assert windy > calm

    def test_custom_solar_radiation(self):
        low_rad = calculate_et0(30, 50, 10, solar_radiation=10)
        high_rad = calculate_et0(30, 50, 10, solar_radiation=30)
        assert high_rad > low_rad

    def test_result_is_rounded(self):
        result = calculate_et0(30, 50, 10)
        # Rounded to 2 decimal places
        assert result == round(result, 2)


class TestCalculateCropET:
    def test_basic_calculation(self):
        et0 = 5.0
        result = calculate_crop_et(et0, CropType.TOMATO, GrowthStage.FLOWERING)
        assert isinstance(result, float)
        assert result > 0

    def test_flowering_kc_is_1(self):
        et0 = 5.0
        result = calculate_crop_et(et0, CropType.TOMATO, GrowthStage.FLOWERING)
        # Flowering Kc=1.0 for tomato (no crop adjustment), so result == et0
        assert result == 5.0

    def test_seedling_lower_than_fruiting(self):
        et0 = 5.0
        seedling = calculate_crop_et(et0, CropType.TOMATO, GrowthStage.SEEDLING)
        fruiting = calculate_crop_et(et0, CropType.TOMATO, GrowthStage.FRUITING)
        assert seedling < fruiting

    def test_banana_adjustment(self):
        et0 = 5.0
        banana = calculate_crop_et(et0, CropType.BANANA, GrowthStage.FLOWERING)
        tomato = calculate_crop_et(et0, CropType.TOMATO, GrowthStage.FLOWERING)
        # Banana gets 1.1x multiplier
        assert banana > tomato

    def test_date_palm_adjustment(self):
        et0 = 5.0
        palm = calculate_crop_et(et0, CropType.DATE_PALM, GrowthStage.FLOWERING)
        tomato = calculate_crop_et(et0, CropType.TOMATO, GrowthStage.FLOWERING)
        assert palm > tomato

    def test_wheat_adjustment(self):
        et0 = 5.0
        wheat = calculate_crop_et(et0, CropType.WHEAT, GrowthStage.FLOWERING)
        tomato = calculate_crop_et(et0, CropType.TOMATO, GrowthStage.FLOWERING)
        # Wheat gets 0.9x multiplier
        assert wheat < tomato

    def test_result_rounded(self):
        result = calculate_crop_et(5.123, CropType.TOMATO, GrowthStage.VEGETATIVE)
        assert result == round(result, 2)


class TestCalculateWaterNeed:
    def test_basic_calculation(self):
        result = calculate_water_need(
            crop=CropType.WHEAT,
            stage=GrowthStage.VEGETATIVE,
            area_ha=2.0,
            soil_type=SoilType.LOAMY,
            method=IrrigationMethod.DRIP,
            current_moisture=None,
            days_since_irrigation=3,
        )
        assert "daily_et_mm" in result
        assert "accumulated_need_mm" in result
        assert "gross_water_mm" in result
        assert "water_m3" in result
        assert "water_liters" in result
        assert "urgency" in result
        assert "efficiency" in result
        assert "savings_percent" in result

    def test_higher_area_more_water(self):
        small = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 1.0, SoilType.LOAMY, IrrigationMethod.DRIP, None, 3)
        large = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 5.0, SoilType.LOAMY, IrrigationMethod.DRIP, None, 3)
        assert large["water_m3"] > small["water_m3"]

    def test_more_days_higher_urgency(self):
        recent = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 1.0, SoilType.LOAMY, IrrigationMethod.DRIP, None, 1)
        old = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 1.0, SoilType.LOAMY, IrrigationMethod.DRIP, None, 10)
        assert old["accumulated_need_mm"] >= recent["accumulated_need_mm"]

    def test_urgency_critical_for_high_deficit(self):
        result = calculate_water_need(CropType.BANANA, GrowthStage.FRUITING, 5.0, SoilType.SANDY, IrrigationMethod.FLOOD, None, 10)
        assert result["urgency"] in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]

    def test_urgency_low_for_recently_irrigated(self):
        result = calculate_water_need(CropType.WHEAT, GrowthStage.SEEDLING, 1.0, SoilType.LOAMY, IrrigationMethod.DRIP, 65.0, 1)
        assert result["urgency"] == UrgencyLevel.LOW

    def test_drip_no_savings(self):
        result = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 1.0, SoilType.LOAMY, IrrigationMethod.DRIP, None, 3)
        assert result["savings_percent"] == 0

    def test_non_drip_has_savings(self):
        result = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 1.0, SoilType.LOAMY, IrrigationMethod.FLOOD, None, 3)
        assert result["savings_percent"] > 0

    def test_rainfall_reduces_need(self):
        no_rain = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 1.0, SoilType.LOAMY, IrrigationMethod.DRIP, None, 3, rainfall_forecast=0)
        with_rain = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 1.0, SoilType.LOAMY, IrrigationMethod.DRIP, None, 3, rainfall_forecast=50)
        assert with_rain["accumulated_need_mm"] <= no_rain["accumulated_need_mm"]

    def test_soil_moisture_deficit(self):
        # Low moisture should produce higher need
        result = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 1.0, SoilType.LOAMY, IrrigationMethod.DRIP, 20.0, 3)
        assert result["accumulated_need_mm"] > 0

    def test_efficiency_matches_method(self):
        result = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 1.0, SoilType.LOAMY, IrrigationMethod.SPRINKLER, None, 3)
        assert result["efficiency"] == IRRIGATION_EFFICIENCY[IrrigationMethod.SPRINKLER]

    def test_water_volume_conversion(self):
        # water_m3 = gross_water_mm * area_ha * 10
        result = calculate_water_need(CropType.WHEAT, GrowthStage.VEGETATIVE, 2.0, SoilType.LOAMY, IrrigationMethod.DRIP, None, 3)
        expected_m3 = result["gross_water_mm"] * 2.0 * 10
        assert abs(result["water_m3"] - round(expected_m3, 2)) < 0.15


class TestDetermineIrrigationTime:
    def test_very_hot(self):
        assert determine_irrigation_time(CropType.WHEAT, 40) == "05:00"

    def test_hot(self):
        assert determine_irrigation_time(CropType.WHEAT, 32) == "06:00"

    def test_moderate(self):
        assert determine_irrigation_time(CropType.WHEAT, 25) == "07:00"

    def test_boundary_35(self):
        assert determine_irrigation_time(CropType.WHEAT, 35) == "06:00"

    def test_boundary_30(self):
        assert determine_irrigation_time(CropType.WHEAT, 30) == "07:00"


class TestCalculateDuration:
    def test_basic_duration(self):
        # 2000 liters at 2000 lph = 1 hour = 60 min
        assert calculate_duration(2000, 2000) == 60

    def test_half_flow(self):
        # 1000 liters at 2000 lph = 0.5 hour = 30 min
        assert calculate_duration(1000, 2000) == 30

    def test_custom_flow_rate(self):
        # 3000 liters at 1000 lph = 3 hours = 180 min
        assert calculate_duration(3000, 1000) == 180

    def test_default_flow_rate(self):
        result = calculate_duration(4000)
        assert result == 120  # 4000/2000 = 2 hours = 120 min

    def test_returns_int(self):
        assert isinstance(calculate_duration(1500), int)


class TestGenerateReasoning:
    def test_critical_reasoning(self):
        water_need = {"accumulated_need_mm": 50, "daily_et_mm": 5}
        ar, en = generate_reasoning(CropType.WHEAT, GrowthStage.FLOWERING, UrgencyLevel.CRITICAL, water_need, 7)
        assert "حاد" in ar or "فوري" in ar
        assert "severe" in en.lower() or "immediate" in en.lower()

    def test_high_reasoning(self):
        water_need = {"accumulated_need_mm": 30, "daily_et_mm": 5}
        ar, en = generate_reasoning(CropType.TOMATO, GrowthStage.FRUITING, UrgencyLevel.HIGH, water_need, 5)
        assert "عاجل" in ar
        assert "urgent" in en.lower()

    def test_medium_reasoning(self):
        water_need = {"accumulated_need_mm": 10, "daily_et_mm": 5}
        ar, en = generate_reasoning(CropType.COFFEE, GrowthStage.VEGETATIVE, UrgencyLevel.MEDIUM, water_need, 2)
        assert "24" in ar
        assert "24 hours" in en

    def test_low_reasoning(self):
        water_need = {"accumulated_need_mm": 3, "daily_et_mm": 3}
        ar, en = generate_reasoning(CropType.BANANA, GrowthStage.SEEDLING, UrgencyLevel.LOW, water_need, 1)
        assert "جيدة" in ar
        assert "good condition" in en.lower()

    def test_returns_tuple_of_strings(self):
        water_need = {"accumulated_need_mm": 10, "daily_et_mm": 5}
        result = generate_reasoning(CropType.WHEAT, GrowthStage.FLOWERING, UrgencyLevel.MEDIUM, water_need, 2)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)


# ============================================================================
# Pydantic Model Tests
# ============================================================================


class TestIrrigationRequestModel:
    def test_valid_request(self):
        req = IrrigationRequest(
            field_id="field_001",
            crop=CropType.WHEAT,
            growth_stage=GrowthStage.VEGETATIVE,
            area_hectares=5.0,
        )
        assert req.field_id == "field_001"
        assert req.soil_type == SoilType.LOAMY  # default
        assert req.irrigation_method == IrrigationMethod.DRIP  # default

    def test_area_must_be_positive(self):
        with pytest.raises(Exception):
            IrrigationRequest(
                field_id="f1",
                crop=CropType.WHEAT,
                growth_stage=GrowthStage.SEEDLING,
                area_hectares=0,
            )

    def test_moisture_bounds(self):
        # Valid bounds
        req = IrrigationRequest(
            field_id="f1",
            crop=CropType.WHEAT,
            growth_stage=GrowthStage.SEEDLING,
            area_hectares=1.0,
            current_soil_moisture=50.0,
        )
        assert req.current_soil_moisture == 50.0

    def test_optional_fields_default_none(self):
        req = IrrigationRequest(
            field_id="f1",
            crop=CropType.WHEAT,
            growth_stage=GrowthStage.SEEDLING,
            area_hectares=1.0,
        )
        assert req.current_soil_moisture is None
        assert req.last_irrigation_date is None
        assert req.weather_forecast is None


class TestIrrigationExecutionModel:
    def test_valid_execution(self):
        exe = IrrigationExecution(
            field_id="f1",
            amount_mm=25.0,
            duration_minutes=45,
        )
        assert exe.method == IrrigationMethod.DRIP
        assert exe.schedule_id is None

    def test_amount_must_be_positive(self):
        with pytest.raises(Exception):
            IrrigationExecution(
                field_id="f1",
                amount_mm=0,
                duration_minutes=45,
            )

    def test_duration_must_be_positive(self):
        with pytest.raises(Exception):
            IrrigationExecution(
                field_id="f1",
                amount_mm=10.0,
                duration_minutes=0,
            )


class TestSoilMoistureReadingModel:
    def test_valid_reading(self):
        reading = SoilMoistureReading(
            field_id="f1",
            sensor_id="s1",
            reading_time=datetime.now(UTC),
            depth_cm=30,
            moisture_percent=45.0,
            temperature_c=28.0,
            ec_ds_m=1.2,
        )
        assert reading.moisture_percent == 45.0


class TestWaterBalanceModel:
    def test_valid_balance(self):
        wb = WaterBalance(
            field_id="f1",
            date=date.today(),
            et_mm=5.0,
            rainfall_mm=2.0,
            irrigation_mm=10.0,
            soil_moisture_change_mm=7.0,
            water_deficit_mm=0.0,
            cumulative_deficit_mm=0.0,
        )
        assert wb.et_mm == 5.0


# ============================================================================
# NATS Event Publishing Tests
# ============================================================================


class TestPublishEvent:
    @pytest.mark.asyncio
    async def test_publish_when_connected(self):
        mock_nc = AsyncMock()
        mock_nc.is_connected = True
        app.state.nc = mock_nc

        result = await publish_event("sahool.irrigation.test", {"field_id": "f1"})
        assert result is True
        mock_nc.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_when_not_connected(self):
        mock_nc = MagicMock()
        mock_nc.is_connected = False
        app.state.nc = mock_nc

        result = await publish_event("sahool.irrigation.test", {"field_id": "f1"})
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_when_nc_is_none(self):
        app.state.nc = None
        result = await publish_event("sahool.irrigation.test", {"field_id": "f1"})
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_handles_exception(self):
        mock_nc = AsyncMock()
        mock_nc.is_connected = True
        mock_nc.publish.side_effect = Exception("connection lost")
        app.state.nc = mock_nc

        result = await publish_event("sahool.irrigation.test", {"field_id": "f1"})
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_correct_payload(self):
        mock_nc = AsyncMock()
        mock_nc.is_connected = True
        app.state.nc = mock_nc

        data = {"field_id": "f1", "amount": 25}
        await publish_event("sahool.irrigation.executed", data)

        call_args = mock_nc.publish.call_args
        subject_arg = call_args[0][0]
        payload_arg = call_args[0][1]

        assert subject_arg == "sahool.irrigation.executed"
        decoded = json.loads(payload_arg.decode())
        assert decoded["field_id"] == "f1"
        assert decoded["amount"] == 25


# ============================================================================
# API Endpoint Tests (using TestClient)
# ============================================================================

try:
    from fastapi.testclient import TestClient

    HAS_TESTCLIENT = True
except ImportError:
    HAS_TESTCLIENT = False


@pytest.fixture
def auth_headers():
    """Provide fake auth token for protected endpoints."""
    return {"Authorization": "Bearer fake-token"}


@pytest.fixture
def client():
    """Create a test client with dependency overrides for auth."""
    if not HAS_TESTCLIENT:
        pytest.skip("fastapi test client not available")

    # Override the auth dependency
    app.dependency_overrides[get_current_user] = lambda: {"sub": "user1", "tid": "tenant1"}
    # Ensure NATS is mocked as disconnected for endpoint tests
    app.state.nc = None

    from fastapi.testclient import TestClient as TC

    yield TC(app)

    # Cleanup overrides
    app.dependency_overrides.clear()


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="fastapi not installed")
class TestHealthEndpoints:
    def test_healthz(self, client):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "irrigation-smart"
        assert data["version"] == "16.0.0"

    def test_readyz(self, client):
        resp = client.get("/readyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert "checks" in data
        assert data["crops_supported"] == len(CropType)


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="fastapi not installed")
class TestCropsEndpoint:
    def test_list_crops(self, client, auth_headers):
        resp = client.get("/v1/crops", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "crops" in data
        assert len(data["crops"]) == len(CropType)

    def test_crop_has_arabic_name(self, client, auth_headers):
        resp = client.get("/v1/crops", headers=auth_headers)
        for crop in resp.json()["crops"]:
            assert "name_ar" in crop
            assert "id" in crop
            assert "water_requirements_mm_day" in crop


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="fastapi not installed")
class TestMethodsEndpoint:
    def test_list_methods(self, client, auth_headers):
        resp = client.get("/v1/methods", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "methods" in data
        assert len(data["methods"]) == len(IrrigationMethod)

    def test_method_has_efficiency(self, client, auth_headers):
        resp = client.get("/v1/methods", headers=auth_headers)
        for method in resp.json()["methods"]:
            assert "efficiency_percent" in method
            assert 0 < method["efficiency_percent"] <= 100


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="fastapi not installed")
class TestCalculateEndpoint:
    def test_calculate_irrigation(self, client, auth_headers):
        resp = client.post(
            "/v1/calculate",
            headers=auth_headers,
            json={
                "field_id": "field_001",
                "crop": "wheat",
                "growth_stage": "vegetative",
                "area_hectares": 2.0,
                "soil_type": "loamy",
                "irrigation_method": "drip",
                "current_soil_moisture": 40.0,
                "weather_forecast": {"temperature": 30, "humidity": 50, "rainfall_mm": 0},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["field_id"] == "field_001"
        assert data["crop"] == "wheat"
        assert len(data["schedules"]) >= 1
        assert data["total_water_m3"] > 0
        assert data["estimated_cost_yer"] > 0

    def test_calculate_with_no_weather(self, client, auth_headers):
        resp = client.post(
            "/v1/calculate",
            headers=auth_headers,
            json={
                "field_id": "field_002",
                "crop": "tomato",
                "growth_stage": "flowering",
                "area_hectares": 1.0,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "schedules" in data

    def test_calculate_with_last_irrigation_date(self, client, auth_headers):
        resp = client.post(
            "/v1/calculate",
            headers=auth_headers,
            json={
                "field_id": "field_003",
                "crop": "banana",
                "growth_stage": "fruiting",
                "area_hectares": 3.0,
                "irrigation_method": "flood",
                "last_irrigation_date": str(date.today() - timedelta(days=5)),
                "weather_forecast": {"temperature": 35, "humidity": 40, "rainfall_mm": 0},
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["water_savings_m3"] > 0  # flood vs drip savings


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="fastapi not installed")
class TestSensorReadingEndpoint:
    def test_critical_moisture(self, client, auth_headers):
        resp = client.post(
            "/v1/sensor-reading",
            headers=auth_headers,
            json={
                "field_id": "f1",
                "sensor_id": "s1",
                "reading_time": datetime.now(UTC).isoformat(),
                "depth_cm": 30,
                "moisture_percent": 20.0,
                "temperature_c": 30.0,
                "ec_ds_m": 1.5,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "critical"

    def test_low_moisture(self, client, auth_headers):
        resp = client.post(
            "/v1/sensor-reading",
            headers=auth_headers,
            json={
                "field_id": "f1",
                "sensor_id": "s1",
                "reading_time": datetime.now(UTC).isoformat(),
                "depth_cm": 30,
                "moisture_percent": 35.0,
                "temperature_c": 28.0,
                "ec_ds_m": 1.0,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "low"

    def test_optimal_moisture(self, client, auth_headers):
        resp = client.post(
            "/v1/sensor-reading",
            headers=auth_headers,
            json={
                "field_id": "f1",
                "sensor_id": "s1",
                "reading_time": datetime.now(UTC).isoformat(),
                "depth_cm": 30,
                "moisture_percent": 55.0,
                "temperature_c": 25.0,
                "ec_ds_m": 0.8,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "optimal"

    def test_high_moisture(self, client, auth_headers):
        resp = client.post(
            "/v1/sensor-reading",
            headers=auth_headers,
            json={
                "field_id": "f1",
                "sensor_id": "s1",
                "reading_time": datetime.now(UTC).isoformat(),
                "depth_cm": 30,
                "moisture_percent": 80.0,
                "temperature_c": 22.0,
                "ec_ds_m": 0.5,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "high"


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="fastapi not installed")
class TestIrrigationExecutedEndpoint:
    def test_record_execution(self, client, auth_headers):
        resp = client.post(
            "/v1/irrigation-executed",
            headers=auth_headers,
            json={
                "field_id": "f1",
                "amount_mm": 25.0,
                "duration_minutes": 45,
                "method": "drip",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "recorded"
        assert data["field_id"] == "f1"
        assert data["amount_mm"] == 25.0
        assert "execution_id" in data
        assert "method_ar" in data


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="fastapi not installed")
class TestEfficiencyReportEndpoint:
    def test_report_traditional(self, client, auth_headers):
        resp = client.get(
            "/v1/efficiency-report/field_001?current_method=traditional&area_hectares=2.0",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["field_id"] == "field_001"
        assert data["current_method"]["method"] == "traditional"
        assert len(data["alternatives"]) == 4  # all other methods
        # First alternative should save the most water
        assert data["alternatives"][0]["water_saved_m3"] > 0

    def test_report_drip_best(self, client, auth_headers):
        resp = client.get(
            "/v1/efficiency-report/f1?current_method=drip&area_hectares=1.0",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        # Drip is the best, so all alternatives should save negative or zero
        for alt in data["alternatives"]:
            assert alt["water_saved_m3"] <= 0

    def test_report_has_roi(self, client, auth_headers):
        resp = client.get(
            "/v1/efficiency-report/f1?current_method=flood&area_hectares=5.0",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["roi_months"] is not None


@pytest.mark.skipif(not HAS_TESTCLIENT, reason="fastapi not installed")
class TestWaterBalanceEndpoint:
    def test_water_balance(self, client, auth_headers):
        resp = client.get(
            "/v1/water-balance/field_001?crop=wheat&days=14",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["field_id"] == "field_001"
        assert data["period_days"] == 14
        assert "summary" in data
        assert "daily_data" in data
        assert len(data["daily_data"]) == 14
