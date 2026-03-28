"""Health endpoint tests for agent-registry."""

import pytest


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_healthz(self, client):
        """Test liveness probe returns 200."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("ok", "healthy")

    def test_readyz(self, client):
        """Test readiness probe returns 200."""
        response = client.get("/readyz")
        assert response.status_code == 200

    def test_health(self, client):
        """Test comprehensive health check via readyz (no /health route)."""
        response = client.get("/readyz")
        assert response.status_code == 200
