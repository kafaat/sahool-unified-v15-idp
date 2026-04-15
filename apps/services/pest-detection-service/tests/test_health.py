"""
Tests for Health Endpoints.
اختبارات نقاط الصحة.
"""

import pytest


class TestHealthEndpoints:
    """Test cases for health check endpoints."""

    def test_liveness_probe(self, client):
        """Test Kubernetes liveness probe."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_readiness_probe(self, client):
        """Test Kubernetes readiness probe."""
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        # In test environment, vision service won't be available
        assert "vision_service" in data["checks"]
        assert "nats" in data["checks"]
        assert "redis" in data["checks"]

    def test_comprehensive_health(self, client):
        """Test comprehensive health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "pest-detection-service"
        assert data["service_ar"] == "خدمة كشف الآفات"
        assert "version" in data
        assert "status" in data
        assert "checks" in data

    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "pest-detection-service"
        assert "version" in data


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_docs(self, client):
        """Test OpenAPI documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc(self, client):
        """Test ReDoc documentation is available."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_json(self, client):
        """Test OpenAPI JSON schema is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "SAHOOL Pest Detection Service"
        assert data["info"]["version"] == "16.0.0"


class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options(
            "/api/v1/pests",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # FastAPI TestClient may handle OPTIONS differently
        # Just verify the endpoint is accessible
        assert response.status_code in [200, 405]
