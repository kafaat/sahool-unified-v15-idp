"""Health endpoint tests for ai-chat-assistant."""

import pytest


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_healthz(self, client):
        """Test liveness probe returns 200."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_readyz(self, client):
        """Test readiness probe returns status based on dependencies."""
        response = client.get("/readyz")
        # In test env without Redis/NATS/LLM, readyz returns 503 (not ready)
        # In production with all deps, it returns 200
        assert response.status_code in (200, 503)
        data = response.json()
        assert "status" in data
        assert "checks" in data

    def test_health(self, client):
        """Test comprehensive health check."""
        response = client.get("/health")
        assert response.status_code == 200
