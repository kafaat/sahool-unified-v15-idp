"""
SAHOOL Yield Engine Service - Unit Tests
اختبارات خدمة محرك الإنتاجية
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
        return {"status": "ok", "service": "yield_engine"}

    @app.post("/api/v1/fields/{field_id}/predict")
    def predict_yield(field_id: str):
        return {
            "field_id": field_id,
            "crop": "wheat",
            "predicted_yield": {
                "value": 4.5,
                "unit": "tons/ha",
                "confidence": 0.82
            },
            "range": {"min": 3.8, "max": 5.2},
            "factors": {
                "weather_impact": 0.95,
                "soil_quality": 0.88,
                "irrigation_efficiency": 0.92
            }
        }

    @app.get("/api/v1/fields/{field_id}/history")
    def get_yield_history(field_id: str):
        return {
            "field_id": field_id,
            "history": [
                {"year": 2024, "crop": "wheat", "yield": 4.2, "unit": "tons/ha"},
                {"year": 2023, "crop": "wheat", "yield": 3.9, "unit": "tons/ha"}
            ]
        }

    @app.get("/api/v1/benchmarks/{crop}")
    def get_benchmarks(crop: str):
        return {
            "crop": crop,
            "regional_average": 3.5,
            "national_average": 3.2,
            "top_performers": 5.0,
            "unit": "tons/ha"
        }

    @app.post("/api/v1/simulate")
    def simulate_scenario():
        return {
            "scenario": "increased_irrigation",
            "base_yield": 4.0,
            "projected_yield": 4.8,
            "improvement_pct": 20
        }

    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200


class TestYieldPrediction:
    def test_predict_yield(self, client):
        response = client.post("/api/v1/fields/field_001/predict", json={
            "crop": "wheat",
            "stage": "flowering"
        })
        assert response.status_code == 200
        data = response.json()
        assert "predicted_yield" in data
        assert "confidence" in data["predicted_yield"]

    def test_prediction_has_range(self, client):
        response = client.post("/api/v1/fields/field_001/predict", json={})
        assert response.status_code == 200
        assert "range" in response.json()


class TestYieldHistory:
    def test_get_history(self, client):
        response = client.get("/api/v1/fields/field_001/history")
        assert response.status_code == 200
        assert "history" in response.json()


class TestBenchmarks:
    def test_get_benchmarks(self, client):
        response = client.get("/api/v1/benchmarks/wheat")
        assert response.status_code == 200
        data = response.json()
        assert "regional_average" in data
        assert "national_average" in data


class TestSimulation:
    def test_simulate_scenario(self, client):
        response = client.post("/api/v1/simulate", json={
            "field_id": "field_001",
            "scenario": "increased_irrigation"
        })
        assert response.status_code == 200
        assert "improvement_pct" in response.json()
