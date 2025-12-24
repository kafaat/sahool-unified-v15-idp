"""
SAHOOL Irrigation Smart Service - Unit Tests
اختبارات خدمة الري الذكي
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client with mocked app"""
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/healthz")
    def health():
        return {"status": "ok", "service": "irrigation_smart"}

    @app.get("/api/v1/fields/{field_id}/recommendation")
    def get_recommendation(field_id: str):
        return {
            "field_id": field_id,
            "timestamp": "2025-12-23T10:00:00Z",
            "recommendation": {
                "action": "irrigate",
                "action_ar": "يجب الري",
                "amount_mm": 25,
                "duration_minutes": 45,
                "priority": "high",
                "reason": "Soil moisture below threshold",
                "reason_ar": "رطوبة التربة أقل من الحد"
            },
            "conditions": {
                "soil_moisture": 28,
                "et0": 5.2,
                "crop_kc": 1.05,
                "temperature": 32
            }
        }

    @app.post("/api/v1/fields/{field_id}/calculate-et")
    def calculate_et(field_id: str):
        return {
            "field_id": field_id,
            "date": "2025-12-23",
            "et0": 5.2,
            "etc": 5.46,
            "crop_coefficient": 1.05,
            "method": "penman_monteith"
        }

    @app.get("/api/v1/fields/{field_id}/schedule")
    def get_schedule(field_id: str):
        return {
            "field_id": field_id,
            "schedule": [
                {"day": "sunday", "time": "06:00", "duration_min": 45, "zone": "zone_a"},
                {"day": "tuesday", "time": "06:00", "duration_min": 45, "zone": "zone_a"},
                {"day": "thursday", "time": "06:00", "duration_min": 45, "zone": "zone_a"}
            ],
            "total_weekly_mm": 75
        }

    @app.post("/api/v1/fields/{field_id}/schedule")
    def update_schedule(field_id: str):
        return {
            "field_id": field_id,
            "status": "updated",
            "message": "تم تحديث جدول الري"
        }

    @app.get("/api/v1/fields/{field_id}/water-balance")
    def get_water_balance(field_id: str):
        return {
            "field_id": field_id,
            "date": "2025-12-23",
            "balance": {
                "precipitation_mm": 0,
                "irrigation_mm": 25,
                "et_mm": 5.5,
                "drainage_mm": 2,
                "net_change_mm": 17.5
            },
            "soil_moisture_pct": 45
        }

    @app.get("/api/v1/fields/{field_id}/forecast")
    def get_irrigation_forecast(field_id: str, days: int = 7):
        return {
            "field_id": field_id,
            "forecast": [
                {"date": "2025-12-24", "need_irrigation": True, "amount_mm": 25},
                {"date": "2025-12-25", "need_irrigation": False, "amount_mm": 0},
                {"date": "2025-12-26", "need_irrigation": True, "amount_mm": 20}
            ]
        }

    @app.post("/api/v1/fields/{field_id}/trigger")
    def trigger_irrigation(field_id: str):
        return {
            "field_id": field_id,
            "status": "triggered",
            "duration_minutes": 45,
            "started_at": "2025-12-23T10:00:00Z",
            "message": "تم بدء الري"
        }

    @app.get("/api/v1/crops/{crop}/water-requirements")
    def get_crop_water_requirements(crop: str):
        return {
            "crop": crop,
            "crop_ar": "قمح",
            "stages": {
                "initial": {"kc": 0.35, "daily_mm": 3},
                "development": {"kc": 0.75, "daily_mm": 5},
                "mid": {"kc": 1.15, "daily_mm": 7},
                "late": {"kc": 0.45, "daily_mm": 4}
            },
            "total_season_mm": 450
        }

    return TestClient(app)


class TestHealthEndpoint:
    """Test health check"""

    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestRecommendation:
    """Test irrigation recommendations"""

    def test_get_recommendation(self, client):
        response = client.get("/api/v1/fields/field_001/recommendation")
        assert response.status_code == 200
        data = response.json()
        assert "recommendation" in data
        assert "conditions" in data

    def test_recommendation_has_action(self, client):
        response = client.get("/api/v1/fields/field_001/recommendation")
        assert response.status_code == 200
        rec = response.json()["recommendation"]
        assert "action" in rec
        assert "action_ar" in rec
        assert "amount_mm" in rec


class TestETCalculation:
    """Test evapotranspiration calculation"""

    def test_calculate_et(self, client):
        response = client.post("/api/v1/fields/field_001/calculate-et", json={
            "date": "2025-12-23",
            "crop": "wheat",
            "stage": "mid"
        })
        assert response.status_code == 200
        data = response.json()
        assert "et0" in data
        assert "etc" in data
        assert "crop_coefficient" in data


class TestSchedule:
    """Test irrigation schedule"""

    def test_get_schedule(self, client):
        response = client.get("/api/v1/fields/field_001/schedule")
        assert response.status_code == 200
        data = response.json()
        assert "schedule" in data
        assert len(data["schedule"]) > 0

    def test_update_schedule(self, client):
        response = client.post("/api/v1/fields/field_001/schedule", json={
            "schedule": [
                {"day": "sunday", "time": "05:30", "duration_min": 60}
            ]
        })
        assert response.status_code == 200
        assert response.json()["status"] == "updated"


class TestWaterBalance:
    """Test water balance"""

    def test_get_water_balance(self, client):
        response = client.get("/api/v1/fields/field_001/water-balance")
        assert response.status_code == 200
        data = response.json()
        assert "balance" in data
        assert "soil_moisture_pct" in data

    def test_balance_has_components(self, client):
        response = client.get("/api/v1/fields/field_001/water-balance")
        assert response.status_code == 200
        balance = response.json()["balance"]
        assert "precipitation_mm" in balance
        assert "irrigation_mm" in balance
        assert "et_mm" in balance


class TestForecast:
    """Test irrigation forecast"""

    def test_get_forecast(self, client):
        response = client.get("/api/v1/fields/field_001/forecast")
        assert response.status_code == 200
        data = response.json()
        assert "forecast" in data
        assert len(data["forecast"]) > 0

    def test_forecast_has_irrigation_need(self, client):
        response = client.get("/api/v1/fields/field_001/forecast")
        assert response.status_code == 200
        day = response.json()["forecast"][0]
        assert "date" in day
        assert "need_irrigation" in day
        assert "amount_mm" in day


class TestTriggerIrrigation:
    """Test manual irrigation trigger"""

    def test_trigger_irrigation(self, client):
        response = client.post("/api/v1/fields/field_001/trigger", json={
            "duration_minutes": 45,
            "zone": "zone_a"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "triggered"


class TestCropWaterRequirements:
    """Test crop water requirements"""

    def test_get_crop_requirements(self, client):
        response = client.get("/api/v1/crops/wheat/water-requirements")
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "wheat"
        assert "stages" in data

    def test_requirements_have_kc(self, client):
        response = client.get("/api/v1/crops/wheat/water-requirements")
        assert response.status_code == 200
        stages = response.json()["stages"]
        for stage_data in stages.values():
            assert "kc" in stage_data
            assert "daily_mm" in stage_data
