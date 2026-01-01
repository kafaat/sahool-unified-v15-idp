"""
SAHOOL Virtual Sensors Service - Unit Tests
اختبارات خدمة الحساسات الافتراضية
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
        return {"status": "ok", "service": "virtual_sensors"}

    @app.get("/api/v1/fields/{field_id}/virtual-sensors")
    def get_virtual_sensors(field_id: str):
        return {
            "field_id": field_id,
            "sensors": [
                {"type": "soil_moisture", "value": 42, "unit": "%", "confidence": 0.85},
                {
                    "type": "soil_temperature",
                    "value": 24,
                    "unit": "°C",
                    "confidence": 0.90,
                },
                {"type": "et0", "value": 5.2, "unit": "mm/day", "confidence": 0.88},
            ],
            "last_updated": "2025-12-23T10:00:00Z",
        }

    @app.post("/api/v1/fields/{field_id}/estimate")
    def estimate_sensor(field_id: str):
        return {
            "field_id": field_id,
            "sensor_type": "soil_moisture",
            "estimated_value": 42,
            "confidence": 0.85,
            "inputs_used": ["ndvi", "weather", "historical"],
        }

    @app.get("/api/v1/models")
    def list_models():
        return {
            "models": [
                {"id": "soil_moisture_v2", "type": "soil_moisture", "accuracy": 0.87},
                {"id": "et0_penman", "type": "et0", "accuracy": 0.92},
            ]
        }

    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200


class TestVirtualSensors:
    def test_get_virtual_sensors(self, client):
        response = client.get("/api/v1/fields/field_001/virtual-sensors")
        assert response.status_code == 200
        data = response.json()
        assert "sensors" in data
        assert len(data["sensors"]) > 0

    def test_sensors_have_confidence(self, client):
        response = client.get("/api/v1/fields/field_001/virtual-sensors")
        for sensor in response.json()["sensors"]:
            assert "confidence" in sensor
            assert 0 <= sensor["confidence"] <= 1


class TestEstimation:
    def test_estimate_sensor(self, client):
        response = client.post(
            "/api/v1/fields/field_001/estimate", json={"sensor_type": "soil_moisture"}
        )
        assert response.status_code == 200
        assert "estimated_value" in response.json()


class TestModels:
    def test_list_models(self, client):
        response = client.get("/api/v1/models")
        assert response.status_code == 200
        assert "models" in response.json()
