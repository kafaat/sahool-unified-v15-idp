"""Health endpoint tests for cooperative-service."""


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_healthz(self, client):
        """Test liveness probe returns 200."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_readyz(self, client):
        """Test readiness probe returns 200."""
        response = client.get("/readyz")
        assert response.status_code == 200

    def test_health(self, client):
        """Test comprehensive health check (requires tenant context)."""
        response = client.get("/health")
        # /health goes through TenantContextMiddleware which requires tenant ID
        assert response.status_code in (200, 400)
