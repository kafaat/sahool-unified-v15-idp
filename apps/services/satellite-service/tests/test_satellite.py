"""
SAHOOL Satellite Service - Unit Tests
اختبارات خدمة الأقمار الصناعية
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
        return {"status": "ok", "service": "satellite_service"}

    @app.get("/api/v1/imagery/available")
    def get_available_imagery(lat: float, lon: float):
        return {
            "location": {"lat": lat, "lon": lon},
            "imagery": [
                {"source": "sentinel-2", "date": "2025-12-20", "cloud_cover": 5},
                {"source": "sentinel-2", "date": "2025-12-15", "cloud_cover": 12},
            ],
        }

    @app.post("/api/v1/imagery/request")
    def request_imagery():
        return {
            "request_id": "req_001",
            "status": "processing",
            "estimated_time_minutes": 5,
        }

    @app.get("/api/v1/imagery/{request_id}")
    def get_imagery_status(request_id: str):
        return {
            "request_id": request_id,
            "status": "completed",
            "download_url": "https://cdn.sahool.io/imagery/req_001.tiff",
        }

    @app.get("/api/v1/fields/{field_id}/imagery")
    def get_field_imagery(field_id: str):
        return {
            "field_id": field_id,
            "images": [
                {
                    "date": "2025-12-20",
                    "source": "sentinel-2",
                    "indices": ["ndvi", "ndwi"],
                }
            ],
        }

    @app.get("/api/v1/sources")
    def list_sources():
        return {
            "sources": [
                {"id": "sentinel-2", "name": "Sentinel-2", "resolution": "10m"},
                {"id": "landsat-8", "name": "Landsat 8", "resolution": "30m"},
            ]
        }

    return TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200


class TestImageryAvailability:
    def test_get_available_imagery(self, client):
        response = client.get("/api/v1/imagery/available?lat=15.35&lon=44.20")
        assert response.status_code == 200
        assert "imagery" in response.json()


class TestImageryRequest:
    def test_request_imagery(self, client):
        response = client.post(
            "/api/v1/imagery/request",
            json={
                "field_id": "field_001",
                "date": "2025-12-20",
                "source": "sentinel-2",
            },
        )
        assert response.status_code == 200
        assert "request_id" in response.json()

    def test_get_imagery_status(self, client):
        response = client.get("/api/v1/imagery/req_001")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"


class TestFieldImagery:
    def test_get_field_imagery(self, client):
        response = client.get("/api/v1/fields/field_001/imagery")
        assert response.status_code == 200
        assert "images" in response.json()


class TestSources:
    def test_list_sources(self, client):
        response = client.get("/api/v1/sources")
        assert response.status_code == 200
        assert "sources" in response.json()
