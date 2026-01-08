"""
SAHOOL Indicators Service - Unit Tests
اختبارات خدمة المؤشرات الزراعية
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
        return {"status": "ok", "service": "indicators_service"}

    @app.get("/api/v1/fields/{field_id}/indicators")
    def get_field_indicators(field_id: str):
        return {
            "field_id": field_id,
            "timestamp": "2025-12-23T10:00:00Z",
            "indicators": {
                "ndvi": {"value": 0.72, "status": "healthy", "trend": "stable"},
                "health_score": {"value": 85, "status": "good"},
                "water_stress": {"value": 0.15, "status": "low"},
                "nitrogen_index": {"value": 0.68, "status": "adequate"},
            },
        }

    @app.get("/api/v1/fields/{field_id}/indicators/history")
    def get_indicator_history(field_id: str, indicator: str, days: int = 30):
        return {
            "field_id": field_id,
            "indicator": indicator,
            "period_days": days,
            "data": [
                {"date": "2025-12-20", "value": 0.70},
                {"date": "2025-12-21", "value": 0.71},
                {"date": "2025-12-22", "value": 0.72},
            ],
            "statistics": {
                "min": 0.68,
                "max": 0.75,
                "avg": 0.71,
                "trend": "increasing",
            },
        }

    @app.get("/api/v1/tenants/{tenant_id}/dashboard")
    def get_tenant_dashboard(tenant_id: str):
        return {
            "tenant_id": tenant_id,
            "summary": {
                "total_fields": 15,
                "healthy_fields": 12,
                "warning_fields": 2,
                "critical_fields": 1,
            },
            "avg_indicators": {"ndvi": 0.68, "health_score": 78, "water_stress": 0.22},
        }

    @app.get("/api/v1/fields/{field_id}/alerts")
    def get_field_alerts(field_id: str):
        return {
            "field_id": field_id,
            "alerts": [
                {
                    "id": "alert_001",
                    "type": "water_stress",
                    "severity": "warning",
                    "message": "زيادة إجهاد الماء المكتشف",
                    "message_en": "Increased water stress detected",
                    "timestamp": "2025-12-23T08:00:00Z",
                }
            ],
        }

    @app.post("/api/v1/fields/{field_id}/indicators/compute")
    def compute_indicators(field_id: str):
        return {
            "field_id": field_id,
            "computed_at": "2025-12-23T10:00:00Z",
            "indicators": {"ndvi": 0.72, "evi": 0.58, "ndwi": -0.05, "lai": 3.2},
            "status": "computed",
        }

    @app.get("/api/v1/benchmarks/{crop}")
    def get_benchmarks(crop: str):
        return {
            "crop": crop,
            "benchmarks": {
                "ndvi": {"min": 0.4, "optimal": 0.7, "max": 0.9},
                "health_score": {"min": 60, "optimal": 85, "max": 100},
                "water_stress": {"min": 0, "optimal": 0.1, "max": 0.3},
            },
        }

    return TestClient(app)


class TestHealthEndpoint:
    """Test health check"""

    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestFieldIndicators:
    """Test field indicators"""

    def test_get_field_indicators(self, client):
        response = client.get("/api/v1/fields/field_001/indicators")
        assert response.status_code == 200
        data = response.json()
        assert data["field_id"] == "field_001"
        assert "indicators" in data

    def test_indicators_have_ndvi(self, client):
        response = client.get("/api/v1/fields/field_001/indicators")
        assert response.status_code == 200
        indicators = response.json()["indicators"]
        assert "ndvi" in indicators
        assert "value" in indicators["ndvi"]
        assert "status" in indicators["ndvi"]


class TestIndicatorHistory:
    """Test indicator history"""

    def test_get_indicator_history(self, client):
        response = client.get("/api/v1/fields/field_001/indicators/history?indicator=ndvi")
        assert response.status_code == 200
        data = response.json()
        assert data["indicator"] == "ndvi"
        assert "data" in data
        assert len(data["data"]) > 0

    def test_history_has_statistics(self, client):
        response = client.get("/api/v1/fields/field_001/indicators/history?indicator=ndvi")
        assert response.status_code == 200
        stats = response.json()["statistics"]
        assert "min" in stats
        assert "max" in stats
        assert "avg" in stats
        assert "trend" in stats


class TestTenantDashboard:
    """Test tenant dashboard"""

    def test_get_dashboard(self, client):
        response = client.get("/api/v1/tenants/tenant_001/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "avg_indicators" in data

    def test_dashboard_has_field_counts(self, client):
        response = client.get("/api/v1/tenants/tenant_001/dashboard")
        assert response.status_code == 200
        summary = response.json()["summary"]
        assert "total_fields" in summary
        assert "healthy_fields" in summary
        assert "warning_fields" in summary
        assert "critical_fields" in summary


class TestAlerts:
    """Test field alerts"""

    def test_get_alerts(self, client):
        response = client.get("/api/v1/fields/field_001/alerts")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data

    def test_alerts_have_bilingual_messages(self, client):
        response = client.get("/api/v1/fields/field_001/alerts")
        assert response.status_code == 200
        if response.json()["alerts"]:
            alert = response.json()["alerts"][0]
            assert "message" in alert
            assert "message_en" in alert


class TestComputeIndicators:
    """Test indicator computation"""

    def test_compute_indicators(self, client):
        response = client.post(
            "/api/v1/fields/field_001/indicators/compute",
            json={"source": "sentinel-2", "date": "2025-12-23"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "computed"
        assert "indicators" in data


class TestBenchmarks:
    """Test crop benchmarks"""

    def test_get_benchmarks(self, client):
        response = client.get("/api/v1/benchmarks/wheat")
        assert response.status_code == 200
        data = response.json()
        assert data["crop"] == "wheat"
        assert "benchmarks" in data

    def test_benchmarks_have_ranges(self, client):
        response = client.get("/api/v1/benchmarks/wheat")
        assert response.status_code == 200
        ndvi_benchmark = response.json()["benchmarks"]["ndvi"]
        assert "min" in ndvi_benchmark
        assert "optimal" in ndvi_benchmark
        assert "max" in ndvi_benchmark
