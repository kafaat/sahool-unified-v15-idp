"""
SAHOOL Irrigation Smart Service - Unit Tests
اختبارات خدمة الري الذكي

Tests the actual API endpoints and calculation functions defined in src/main.py.
"""

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

import sys
import os

# Ensure the service src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


# ---------------------------------------------------------------------------
# Pure calculation function tests (no app/auth required)
# ---------------------------------------------------------------------------


class TestCalculateET0:
    """Test reference evapotranspiration calculation."""

    def test_et0_basic(self):
        from main import calculate_et0

        result = calculate_et0(temperature=30, humidity=50, wind_speed=10)
        assert isinstance(result, float)
        assert result > 0

    def test_et0_higher_temp_increases_et(self):
        from main import calculate_et0

        low = calculate_et0(temperature=20, humidity=50, wind_speed=10)
        high = calculate_et0(temperature=40, humidity=50, wind_speed=10)
        assert high > low

    def test_et0_lower_humidity_increases_et(self):
        from main import calculate_et0

        humid = calculate_et0(temperature=30, humidity=80, wind_speed=10)
        dry = calculate_et0(temperature=30, humidity=20, wind_speed=10)
        assert dry > humid


class TestCalculateCropET:
    """Test crop evapotranspiration calculation."""

    def test_crop_et_basic(self):
        from main import CropType, GrowthStage, calculate_crop_et

        result = calculate_crop_et(et0=5.0, crop=CropType.WHEAT, stage=GrowthStage.FLOWERING)
        assert isinstance(result, float)
        assert result > 0

    def test_crop_et_fruiting_higher_than_seedling(self):
        from main import CropType, GrowthStage, calculate_crop_et

        seedling = calculate_crop_et(et0=5.0, crop=CropType.TOMATO, stage=GrowthStage.SEEDLING)
        fruiting = calculate_crop_et(et0=5.0, crop=CropType.TOMATO, stage=GrowthStage.FRUITING)
        assert fruiting > seedling

    def test_crop_et_date_palm_has_high_coefficient(self):
        from main import CropType, GrowthStage, calculate_crop_et

        palm = calculate_crop_et(et0=5.0, crop=CropType.DATE_PALM, stage=GrowthStage.FRUITING)
        wheat = calculate_crop_et(et0=5.0, crop=CropType.WHEAT, stage=GrowthStage.FRUITING)
        assert palm > wheat


class TestCalculateWaterNeed:
    """Test irrigation water need calculation."""

    def test_water_need_returns_expected_keys(self):
        from main import (
            CropType,
            GrowthStage,
            IrrigationMethod,
            SoilType,
            calculate_water_need,
        )

        result = calculate_water_need(
            crop=CropType.TOMATO,
            stage=GrowthStage.VEGETATIVE,
            area_ha=1.0,
            soil_type=SoilType.LOAMY,
            method=IrrigationMethod.DRIP,
            current_moisture=None,
            days_since_irrigation=3,
        )
        assert "daily_et_mm" in result
        assert "water_m3" in result
        assert "water_liters" in result
        assert "urgency" in result
        assert "efficiency" in result

    def test_water_need_increases_with_days_since_irrigation(self):
        from main import (
            CropType,
            GrowthStage,
            IrrigationMethod,
            SoilType,
            calculate_water_need,
        )

        kwargs = {
            "crop": CropType.TOMATO,
            "stage": GrowthStage.VEGETATIVE,
            "area_ha": 1.0,
            "soil_type": SoilType.LOAMY,
            "method": IrrigationMethod.DRIP,
            "current_moisture": None,
            "temperature": 30,
            "humidity": 50,
            "rainfall_forecast": 0,
        }
        short = calculate_water_need(days_since_irrigation=1, **kwargs)
        long = calculate_water_need(days_since_irrigation=7, **kwargs)
        assert long["water_m3"] > short["water_m3"]

    def test_drip_has_zero_savings(self):
        from main import (
            CropType,
            GrowthStage,
            IrrigationMethod,
            SoilType,
            calculate_water_need,
        )

        result = calculate_water_need(
            crop=CropType.WHEAT,
            stage=GrowthStage.FLOWERING,
            area_ha=1.0,
            soil_type=SoilType.LOAMY,
            method=IrrigationMethod.DRIP,
            current_moisture=None,
            days_since_irrigation=3,
        )
        assert result["savings_percent"] == 0

    def test_flood_has_positive_savings_vs_drip(self):
        from main import (
            CropType,
            GrowthStage,
            IrrigationMethod,
            SoilType,
            calculate_water_need,
        )

        result = calculate_water_need(
            crop=CropType.WHEAT,
            stage=GrowthStage.FLOWERING,
            area_ha=1.0,
            soil_type=SoilType.LOAMY,
            method=IrrigationMethod.FLOOD,
            current_moisture=None,
            days_since_irrigation=3,
        )
        assert result["savings_percent"] > 0


class TestDetermineIrrigationTime:
    """Test optimal irrigation time determination."""

    def test_hot_weather_early_time(self):
        from main import CropType, determine_irrigation_time

        result = determine_irrigation_time(CropType.TOMATO, temperature=40)
        assert result == "05:00"

    def test_moderate_weather_time(self):
        from main import CropType, determine_irrigation_time

        result = determine_irrigation_time(CropType.TOMATO, temperature=32)
        assert result == "06:00"

    def test_cool_weather_later_time(self):
        from main import CropType, determine_irrigation_time

        result = determine_irrigation_time(CropType.TOMATO, temperature=25)
        assert result == "07:00"


class TestCalculateDuration:
    """Test irrigation duration calculation."""

    def test_duration_basic(self):
        from main import calculate_duration

        # 2000 liters at 2000 lph = 1 hour = 60 minutes
        result = calculate_duration(water_liters=2000, flow_rate_lph=2000)
        assert result == 60

    def test_duration_half_flow(self):
        from main import calculate_duration

        # 1000 liters at 2000 lph = 0.5 hours = 30 minutes
        result = calculate_duration(water_liters=1000, flow_rate_lph=2000)
        assert result == 30


class TestGenerateReasoning:
    """Test bilingual reasoning generation."""

    def test_reasoning_returns_tuple(self):
        from main import CropType, GrowthStage, UrgencyLevel, generate_reasoning

        water_need = {"accumulated_need_mm": 15.0, "daily_et_mm": 5.0}
        reason_ar, reason_en = generate_reasoning(
            crop=CropType.WHEAT,
            stage=GrowthStage.FLOWERING,
            urgency=UrgencyLevel.HIGH,
            water_need=water_need,
            days_since_irrigation=3,
        )
        assert isinstance(reason_ar, str)
        assert isinstance(reason_en, str)
        assert len(reason_ar) > 0
        assert len(reason_en) > 0

    def test_critical_urgency_mentions_severe(self):
        from main import CropType, GrowthStage, UrgencyLevel, generate_reasoning

        water_need = {"accumulated_need_mm": 30.0, "daily_et_mm": 5.0}
        _reason_ar, reason_en = generate_reasoning(
            crop=CropType.WHEAT,
            stage=GrowthStage.FLOWERING,
            urgency=UrgencyLevel.CRITICAL,
            water_need=water_need,
            days_since_irrigation=7,
        )
        assert "severe" in reason_en.lower() or "immediate" in reason_en.lower()


# ---------------------------------------------------------------------------
# API endpoint tests using TestClient against the real app
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    """Create test client against the real FastAPI app with auth overridden."""
    # Patch environment so shared imports don't fail at module level
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
    os.environ.setdefault("JWT_ALGORITHM", "HS256")
    os.environ.setdefault("DATABASE_URL", "")
    os.environ.setdefault("NATS_URL", "")

    try:
        from main import app, get_current_user
    except Exception:
        pytest.skip("Cannot import app (missing shared dependencies)")

    # Override auth dependency to bypass JWT for testing
    async def mock_user():
        return {"sub": "test-user", "tid": "test-tenant", "role": "admin"}

    app.dependency_overrides[get_current_user] = mock_user

    yield TestClient(app, raise_server_exceptions=False)

    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Test health check endpoints (no auth required)."""

    def test_healthz(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "irrigation-smart"

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert "checks" in data


class TestListCrops:
    """Test GET /v1/crops endpoint."""

    def test_list_crops(self, client):
        response = client.get("/v1/crops")
        assert response.status_code == 200
        data = response.json()
        assert "crops" in data
        assert len(data["crops"]) > 0
        # Each crop should have id and Arabic name
        crop = data["crops"][0]
        assert "id" in crop
        assert "name_ar" in crop


class TestListMethods:
    """Test GET /v1/methods endpoint."""

    def test_list_methods(self, client):
        response = client.get("/v1/methods")
        assert response.status_code == 200
        data = response.json()
        assert "methods" in data
        assert len(data["methods"]) > 0
        method = data["methods"][0]
        assert "id" in method
        assert "name_ar" in method
        assert "efficiency_percent" in method


class TestCalculateEndpoint:
    """Test POST /v1/calculate endpoint."""

    def test_calculate_irrigation_plan(self, client):
        response = client.post(
            "/v1/calculate",
            json={
                "field_id": "field_001",
                "crop": "wheat",
                "growth_stage": "flowering",
                "area_hectares": 2.0,
                "soil_type": "loamy",
                "irrigation_method": "drip",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_001"
        assert data["crop"] == "wheat"
        assert "schedules" in data
        assert "total_water_m3" in data
        assert "recommendations_ar" in data

    def test_calculate_with_soil_moisture(self, client):
        response = client.post(
            "/v1/calculate",
            json={
                "field_id": "field_002",
                "crop": "tomato",
                "growth_stage": "vegetative",
                "area_hectares": 1.0,
                "current_soil_moisture": 30.0,
            },
        )
        assert response.status_code == 200

    def test_calculate_invalid_crop_returns_422(self, client):
        response = client.post(
            "/v1/calculate",
            json={
                "field_id": "field_001",
                "crop": "invalid_crop",
                "growth_stage": "flowering",
                "area_hectares": 1.0,
            },
        )
        assert response.status_code == 422


class TestSensorReading:
    """Test POST /v1/sensor-reading endpoint."""

    def test_sensor_reading_critical(self, client):
        response = client.post(
            "/v1/sensor-reading",
            json={
                "field_id": "field_001",
                "sensor_id": "sensor_01",
                "reading_time": "2025-12-23T10:00:00Z",
                "depth_cm": 30,
                "moisture_percent": 20.0,
                "temperature_c": 25.0,
                "ec_ds_m": 1.5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "critical"
        assert data["field_id"] == "field_001"

    def test_sensor_reading_optimal(self, client):
        response = client.post(
            "/v1/sensor-reading",
            json={
                "field_id": "field_001",
                "sensor_id": "sensor_01",
                "reading_time": "2025-12-23T10:00:00Z",
                "depth_cm": 30,
                "moisture_percent": 55.0,
                "temperature_c": 25.0,
                "ec_ds_m": 1.5,
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "optimal"


class TestIrrigationExecuted:
    """Test POST /v1/irrigation-executed endpoint."""

    def test_record_execution(self, client):
        response = client.post(
            "/v1/irrigation-executed",
            json={
                "field_id": "field_001",
                "amount_mm": 25.0,
                "duration_minutes": 45,
                "method": "drip",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "recorded"
        assert data["field_id"] == "field_001"
        assert "execution_id" in data
        assert "method_ar" in data


class TestWaterBalanceEndpoint:
    """Test GET /v1/water-balance/{field_id} endpoint."""

    def test_water_balance(self, client):
        response = client.get("/v1/water-balance/field_001?crop=wheat&days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_001"
        assert "summary" in data
        assert "daily_data" in data
        assert len(data["daily_data"]) == 7


class TestEfficiencyReport:
    """Test GET /v1/efficiency-report/{field_id} endpoint."""

    def test_efficiency_report(self, client):
        response = client.get(
            "/v1/efficiency-report/field_001?current_method=traditional&area_hectares=2.0"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_001"
        assert "current_method" in data
        assert "comparisons" in data
        assert len(data["comparisons"]) > 0
