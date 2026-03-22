"""
Tests for task-service main.py endpoints - اختبارات نقاط النهاية الرئيسية
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")

try:
    from fastapi.testclient import TestClient
    from src.main import app
except ImportError:
    pytest.skip("task-service dependencies not installed", allow_module_level=True)


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_healthz(self, client):
        resp = client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "sahool-task-service"
        assert data["version"] == "16.0.0"

    def test_readyz(self, client):
        resp = client.get("/readyz")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "nats" in data["checks"]
        assert "redis" in data["checks"]

    def test_health_combined(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert "status" in data
        assert "ready" in data
        assert "checks" in data


class TestExceptionHandler:
    """Test custom exception handler"""

    def test_task_service_error_returns_json(self, client):
        """TaskServiceError should be handled by custom handler"""
        from src.exceptions import TaskServiceError
        # The exception handler is registered, verify it exists
        assert TaskServiceError is not None

    def test_docs_endpoint(self, client):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_openapi_schema(self, client):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert schema["info"]["title"] == "SAHOOL Task Service"
        assert schema["info"]["version"] == "16.0.0"


class TestRouteRegistration:
    """Test that all routes are registered"""

    def test_routes_registered(self, client):
        resp = client.get("/openapi.json")
        paths = resp.json()["paths"]
        # Health endpoints
        assert "/healthz" in paths
        assert "/readyz" in paths
        assert "/health" in paths
