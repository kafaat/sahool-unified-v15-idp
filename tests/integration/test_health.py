"""
SAHOOL Health Check Integration Tests
Tests for service health endpoints
"""

import pytest

# We need to import the app from each service
import sys

sys.path.insert(0, "kernel/services/field_ops/src")


class TestFieldOpsHealth:
    """Health check tests for Field Operations service"""

    @pytest.fixture
    def client(self):
        """Create test client for field_ops"""
        from fastapi.testclient import TestClient
        from main import app

        return TestClient(app)

    def test_health_endpoint_returns_200(self, client):
        """Health endpoint should return 200 OK"""
        response = client.get("/healthz")

        assert response.status_code == 200

    def test_health_returns_status_ok(self, client):
        """Health endpoint should return status ok"""
        response = client.get("/healthz")
        body = response.json()

        assert body["status"] == "ok"

    def test_health_returns_service_name(self, client):
        """Health endpoint should return service name"""
        response = client.get("/healthz")
        body = response.json()

        assert body["service"] == "field_ops"

    def test_health_returns_version(self, client):
        """Health endpoint should return version"""
        response = client.get("/healthz")
        body = response.json()

        assert "version" in body
        assert body["version"] is not None

    def test_health_returns_timestamp(self, client):
        """Health endpoint should return timestamp"""
        response = client.get("/healthz")
        body = response.json()

        assert "timestamp" in body

    def test_readiness_endpoint_returns_200(self, client):
        """Readiness endpoint should return 200"""
        response = client.get("/readyz")

        assert response.status_code == 200

    def test_readiness_returns_status(self, client):
        """Readiness endpoint should return status"""
        response = client.get("/readyz")
        body = response.json()

        assert body["status"] == "ok"

    def test_readiness_shows_db_status(self, client):
        """Readiness should show database connection status"""
        response = client.get("/readyz")
        body = response.json()

        assert "database" in body
        # In test mode, database may not be connected
        assert isinstance(body["database"], bool)

    def test_readiness_shows_nats_status(self, client):
        """Readiness should show NATS connection status"""
        response = client.get("/readyz")
        body = response.json()

        assert "nats" in body
        assert isinstance(body["nats"], bool)
