"""
SAHOOL Fertilizer Advisor Service - Unit Tests
اختبارات خدمة مستشار التسميد
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
        return {"status": "ok", "service": "fertilizer_advisor", "version": "15.3.0"}

    @app.post("/api/v1/recommend")
    def get_recommendation():
        return {
            "field_id": "field_001",
            "crop": "tomato",
            "stage": "flowering",
            "recommendations": [
                {
                    "fertilizer": "NPK 15-15-15",
                    "fertilizer_ar": "سماد NPK متوازن",
                    "amount_kg_per_ha": 150,
                    "application_method": "broadcasting",
                    "timing": "morning",
                    "priority": "high",
                },
                {
                    "fertilizer": "Potassium Sulfate",
                    "fertilizer_ar": "سلفات البوتاسيوم",
                    "amount_kg_per_ha": 50,
                    "application_method": "fertigation",
                    "timing": "weekly",
                    "priority": "medium",
                },
            ],
            "total_cost_estimate": {"usd": 125.50, "yer": 31375},
        }

    @app.post("/api/v1/soil-analysis")
    def analyze_soil():
        return {
            "field_id": "field_001",
            "analysis": {
                "nitrogen": {
                    "value": 45,
                    "unit": "ppm",
                    "status": "low",
                    "status_ar": "منخفض",
                },
                "phosphorus": {
                    "value": 28,
                    "unit": "ppm",
                    "status": "adequate",
                    "status_ar": "كافي",
                },
                "potassium": {
                    "value": 180,
                    "unit": "ppm",
                    "status": "adequate",
                    "status_ar": "كافي",
                },
                "ph": {"value": 6.8, "status": "optimal", "status_ar": "مثالي"},
                "organic_matter": {
                    "value": 2.1,
                    "unit": "%",
                    "status": "low",
                    "status_ar": "منخفض",
                },
            },
            "deficiencies": ["nitrogen", "organic_matter"],
            "recommendations": [
                "Apply nitrogen-rich fertilizer",
                "Add organic compost",
            ],
        }

    @app.get("/api/v1/fertilizers")
    def list_fertilizers():
        return {
            "fertilizers": [
                {"id": "urea", "name": "Urea", "name_ar": "يوريا", "npk": "46-0-0"},
                {"id": "dap", "name": "DAP", "name_ar": "داب", "npk": "18-46-0"},
                {
                    "id": "npk_15",
                    "name": "NPK 15-15-15",
                    "name_ar": "NPK متوازن",
                    "npk": "15-15-15",
                },
            ]
        }

    @app.get("/api/v1/fertilizers/{fertilizer_id}")
    def get_fertilizer(fertilizer_id: str):
        return {
            "id": fertilizer_id,
            "name": "Urea",
            "name_ar": "يوريا",
            "npk": "46-0-0",
            "price_per_kg": {"usd": 0.45, "yer": 112.5},
            "application_rate": {"min": 100, "max": 200, "unit": "kg/ha"},
            "best_for": ["vegetative_stage", "nitrogen_deficiency"],
        }

    @app.get("/api/v1/crops/{crop}/requirements")
    def get_crop_requirements(crop: str):
        return {
            "crop": crop,
            "crop_ar": "طماطم",
            "stages": {
                "seedling": {"n": 50, "p": 30, "k": 30},
                "vegetative": {"n": 100, "p": 50, "k": 80},
                "flowering": {"n": 80, "p": 80, "k": 120},
                "fruiting": {"n": 60, "p": 60, "k": 150},
            },
            "total_season": {"n": 290, "p": 220, "k": 380},
        }

    @app.post("/api/v1/schedule")
    def create_schedule():
        return {
            "field_id": "field_001",
            "crop": "tomato",
            "schedule": [
                {"week": 1, "application": "Base fertilizer", "amount_kg": 50},
                {"week": 3, "application": "Nitrogen boost", "amount_kg": 25},
                {"week": 6, "application": "Potassium boost", "amount_kg": 30},
            ],
            "total_applications": 3,
            "season_duration_weeks": 16,
        }

    @app.post("/api/v1/calculate-dose")
    def calculate_dose():
        return {
            "field_size_ha": 5.0,
            "fertilizer": "NPK 15-15-15",
            "dose_per_ha_kg": 150,
            "total_required_kg": 750,
            "bags_50kg": 15,
            "estimated_cost": {"usd": 337.50, "yer": 84375},
        }

    return TestClient(app)


class TestHealthEndpoint:
    """Test health check"""

    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestRecommendations:
    """Test fertilizer recommendations"""

    def test_get_recommendation(self, client):
        response = client.post(
            "/api/v1/recommend",
            json={
                "field_id": "field_001",
                "crop": "tomato",
                "stage": "flowering",
                "soil_type": "loamy",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0

    def test_recommendation_has_cost_estimate(self, client):
        response = client.post(
            "/api/v1/recommend",
            json={"field_id": "field_001", "crop": "tomato", "stage": "flowering"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_cost_estimate" in data
        assert "usd" in data["total_cost_estimate"]
        assert "yer" in data["total_cost_estimate"]

    def test_recommendation_has_arabic(self, client):
        response = client.post(
            "/api/v1/recommend",
            json={"field_id": "field_001", "crop": "tomato", "stage": "flowering"},
        )
        assert response.status_code == 200
        rec = response.json()["recommendations"][0]
        assert "fertilizer_ar" in rec


class TestSoilAnalysis:
    """Test soil analysis"""

    def test_analyze_soil(self, client):
        response = client.post(
            "/api/v1/soil-analysis",
            json={
                "field_id": "field_001",
                "nitrogen_ppm": 45,
                "phosphorus_ppm": 28,
                "potassium_ppm": 180,
                "ph": 6.8,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "deficiencies" in data

    def test_soil_analysis_has_nutrients(self, client):
        response = client.post("/api/v1/soil-analysis", json={"field_id": "field_001"})
        assert response.status_code == 200
        analysis = response.json()["analysis"]
        assert "nitrogen" in analysis
        assert "phosphorus" in analysis
        assert "potassium" in analysis
        assert "ph" in analysis


class TestFertilizers:
    """Test fertilizer database"""

    def test_list_fertilizers(self, client):
        response = client.get("/api/v1/fertilizers")
        assert response.status_code == 200
        data = response.json()
        assert "fertilizers" in data
        assert len(data["fertilizers"]) > 0

    def test_get_fertilizer_details(self, client):
        response = client.get("/api/v1/fertilizers/urea")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "urea"
        assert "npk" in data
        assert "price_per_kg" in data


class TestCropRequirements:
    """Test crop nutrient requirements"""

    def test_get_crop_requirements(self, client):
        response = client.get("/api/v1/crops/tomato/requirements")
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "tomato"
        assert "stages" in data

    def test_crop_has_stage_requirements(self, client):
        response = client.get("/api/v1/crops/tomato/requirements")
        assert response.status_code == 200
        stages = response.json()["stages"]
        assert "seedling" in stages
        assert "vegetative" in stages
        assert "flowering" in stages


class TestSchedule:
    """Test fertilization schedule"""

    def test_create_schedule(self, client):
        response = client.post(
            "/api/v1/schedule",
            json={
                "field_id": "field_001",
                "crop": "tomato",
                "planting_date": "2025-12-01",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "schedule" in data
        assert len(data["schedule"]) > 0


class TestDoseCalculation:
    """Test dose calculations"""

    def test_calculate_dose(self, client):
        response = client.post(
            "/api/v1/calculate-dose",
            json={
                "field_size_ha": 5.0,
                "fertilizer": "NPK 15-15-15",
                "dose_per_ha_kg": 150,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_required_kg"] == 750
        assert data["bags_50kg"] == 15
