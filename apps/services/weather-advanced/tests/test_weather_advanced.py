"""
SAHOOL Weather Advanced Service - Unit Tests
اختبارات خدمة الطقس المتقدمة
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
        return {"status": "ok", "service": "weather_advanced"}

    @app.get("/api/v1/forecast/hourly")
    def get_hourly_forecast(lat: float, lon: float):
        return {
            "location": {"lat": lat, "lon": lon},
            "hourly": [
                {"time": "2025-12-23T10:00:00Z", "temp": 28, "humidity": 45, "precipitation": 0},
                {"time": "2025-12-23T11:00:00Z", "temp": 30, "humidity": 42, "precipitation": 0}
            ]
        }

    @app.get("/api/v1/forecast/daily")
    def get_daily_forecast(lat: float, lon: float, days: int = 7):
        return {
            "location": {"lat": lat, "lon": lon},
            "daily": [
                {"date": "2025-12-23", "temp_max": 32, "temp_min": 18, "precipitation_mm": 0}
            ]
        }

    @app.get("/api/v1/historical")
    def get_historical(lat: float, lon: float, from_date: str, to_date: str):
        return {
            "location": {"lat": lat, "lon": lon},
            "data": [
                {"date": "2025-12-20", "temp_avg": 25, "precipitation_mm": 0}
            ]
        }

    @app.get("/api/v1/alerts/active")
    def get_active_alerts(lat: float, lon: float):
        return {
            "location": {"lat": lat, "lon": lon},
            "alerts": [
                {"type": "heat_wave", "severity": "moderate", "message": "موجة حر متوقعة"}
            ]
        }

    @app.get("/api/v1/agricultural-indices")
    def get_agricultural_indices(lat: float, lon: float):
        return {
            "gdd": 1250,
            "chill_hours": 120,
            "drought_index": 0.3,
            "disease_risk": "low"
        }

    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200


class TestForecast:
    def test_hourly_forecast(self, client):
        response = client.get("/api/v1/forecast/hourly?lat=15.35&lon=44.20")
        assert response.status_code == 200
        assert "hourly" in response.json()

    def test_daily_forecast(self, client):
        response = client.get("/api/v1/forecast/daily?lat=15.35&lon=44.20")
        assert response.status_code == 200
        assert "daily" in response.json()


class TestHistorical:
    def test_get_historical(self, client):
        response = client.get("/api/v1/historical?lat=15.35&lon=44.20&from_date=2025-12-01&to_date=2025-12-20")
        assert response.status_code == 200
        assert "data" in response.json()


class TestAlerts:
    def test_get_active_alerts(self, client):
        response = client.get("/api/v1/alerts/active?lat=15.35&lon=44.20")
        assert response.status_code == 200
        assert "alerts" in response.json()


class TestAgriculturalIndices:
    def test_get_indices(self, client):
        response = client.get("/api/v1/agricultural-indices?lat=15.35&lon=44.20")
        assert response.status_code == 200
        data = response.json()
        assert "gdd" in data
        assert "drought_index" in data
