"""Health endpoint tests for traceability-service."""

import pytest


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_healthz(self, client):
        """Test liveness probe returns 200."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "traceability-service"
        assert data["version"] == "16.0.0"

    def test_readyz(self, client):
        """Test readiness probe returns 200."""
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert "database" in data
        assert "nats" in data

    def test_health_comprehensive(self, client):
        """Test comprehensive health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "checks" in data
        assert data["service"] == "traceability-service"

    def test_metrics(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "traceability_service_up 1" in response.text

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "traceability-service"
        assert data["version"] == "16.0.0"
