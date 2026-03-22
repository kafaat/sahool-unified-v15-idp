"""
Tests for Hydrology Service API endpoints.
اختبارات نقاط نهاية API لخدمة الهيدرولوجيا
"""

import os
import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_shared_modules(monkeypatch):
    """Mock shared modules that aren't available in test environment."""
    shared = types.ModuleType("shared")
    errors_py = types.ModuleType("shared.errors_py")
    errors_py.add_request_id_middleware = lambda app: None
    errors_py.setup_exception_handlers = lambda app: None
    shared.errors_py = errors_py

    middleware = types.ModuleType("shared.middleware")
    tenant_ctx = types.ModuleType("shared.middleware.tenant_context")

    # Create a proper ASGI middleware class
    class FakeTenantMiddleware:
        def __init__(self, app, **kwargs):
            self.app = app

        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)

    tenant_ctx.TenantContextMiddleware = FakeTenantMiddleware
    shared.middleware = middleware
    shared.middleware.tenant_context = tenant_ctx

    monkeypatch.setitem(sys.modules, "shared", shared)
    monkeypatch.setitem(sys.modules, "shared.errors_py", errors_py)
    monkeypatch.setitem(sys.modules, "shared.middleware", middleware)
    monkeypatch.setitem(sys.modules, "shared.middleware.tenant_context", tenant_ctx)
@pytest.fixture
def client(mock_shared_modules):
    """Create a test client for the FastAPI app."""
    from src.core.config import get_settings
    get_settings.cache_clear()

    with patch.dict(os.environ, {
        "DATABASE_URL": "",
        "NATS_URL": "",
        "ENVIRONMENT": "test",
    }):
        # Patch asyncpg and nats so lifespan doesn't fail
        # Also patch the endpoint logger to accept structlog-style kwargs
        with patch("src.main.asyncpg") as mock_asyncpg, \
             patch("src.main.nats") as mock_nats, \
             patch("src.api.endpoints.hydrology.logger"):
            from importlib import reload

            import src.main
            reload(src.main)

            from fastapi.testclient import TestClient
            from src.main import app

            with TestClient(app) as c:
                yield c

        get_settings.cache_clear()
# ==============================================================================
# Health Endpoint Tests
# ==============================================================================
class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_healthz(self, client):
        """Test liveness probe endpoint."""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "hydrology-service"
        assert "version" in data
        assert "timestamp" in data

    def test_readyz(self, client):
        """Test readiness probe endpoint."""
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "hydrology-service"
        assert "checks" in data

    def test_combined_health(self, client):
        """Test combined health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
        assert data["components"]["api"]["status"] == "healthy"

    def test_metrics(self, client):
        """Test metrics endpoint returns Prometheus format."""
        response = client.get("/metrics")
        assert response.status_code == 200
        content = response.text
        assert "hydrology_service_up 1" in content
        assert "hydrology_database_connected" in content
        assert "hydrology_nats_connected" in content
        assert "hydrology_service_info" in content
# ==============================================================================
# Hydrology API Endpoint Tests
# ==============================================================================
class TestDrainageEndpoint:
    """Tests for drainage network endpoint."""

    def test_get_drainage_network(self, client):
        """Test GET drainage network returns valid response."""
        response = client.get(
            "/api/v1/hydrology/drainage/FIELD-001",
            headers={"X-Tenant-Id": "TENANT-001"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["field_id"] == "FIELD-001"
        assert "total_length_m" in data["data"]
        assert "drainage_density" in data["data"]
        assert "segments" in data["data"]

    def test_get_drainage_missing_tenant(self, client):
        """Test drainage endpoint requires X-Tenant-Id header."""
        response = client.get("/api/v1/hydrology/drainage/FIELD-001")
        assert response.status_code == 400
class TestWetnessEndpoint:
    """Tests for wetness analysis endpoint."""

    def test_get_wetness_analysis(self, client):
        """Test GET wetness analysis returns valid response."""
        response = client.get(
            "/api/v1/hydrology/wetness/FIELD-001",
            headers={"X-Tenant-Id": "TENANT-001"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["field_id"] == "FIELD-001"
        assert "twi_mean" in data["data"]
        assert "zones" in data["data"]

    def test_get_wetness_with_rainfall(self, client):
        """Test wetness analysis with rainfall prediction."""
        response = client.get(
            "/api/v1/hydrology/wetness/FIELD-001?rainfall_mm=50.0",
            headers={"X-Tenant-Id": "TENANT-001"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["waterlogging_prediction"] is not None
class TestDepressionsEndpoint:
    """Tests for depression analysis endpoint."""

    def test_get_depressions(self, client):
        """Test GET depressions returns valid response."""
        response = client.get(
            "/api/v1/hydrology/depressions/FIELD-001",
            headers={"X-Tenant-Id": "TENANT-001"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["field_id"] == "FIELD-001"
        assert "total_depressions" in data["data"]
class TestStreamsEndpoint:
    """Tests for stream detection endpoint."""

    def test_get_streams(self, client):
        """Test GET streams returns valid response."""
        response = client.get(
            "/api/v1/hydrology/streams/FIELD-001",
            headers={"X-Tenant-Id": "TENANT-001"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["field_id"] == "FIELD-001"
        assert "total_streams" in data["data"]
class TestBasinsEndpoint:
    """Tests for basin delineation endpoint."""

    def test_get_basins(self, client):
        """Test GET basins returns valid response."""
        response = client.get(
            "/api/v1/hydrology/basins/FIELD-001",
            headers={"X-Tenant-Id": "TENANT-001"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["field_id"] == "FIELD-001"
        assert "total_basins" in data["data"]
class TestAnalyzeEndpoint:
    """Tests for full hydrology analysis endpoint."""

    def test_analyze_hydrology(self, client):
        """Test POST full analysis endpoint."""
        response = client.post(
            "/api/v1/hydrology/analyze",
            json={
                "field_id": "FIELD-001",
                "tenant_id": "TENANT-001",
                "resolution_m": 30.0,
                "include_rainfall": False,
            },
            headers={"X-Tenant-Id": "TENANT-001"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        result = data["data"]
        assert result["field_id"] == "FIELD-001"
        assert "drainage" in result
        assert "wetness" in result
        assert "depressions" in result
        assert "streams" in result
        assert "basins" in result
        assert "flood_risk_level" in result
        assert "recommendations_ar" in result
        assert "recommendations_en" in result
        assert data["processing_time_ms"] > 0

    def test_analyze_invalid_request(self, client):
        """Test POST analysis with invalid request body."""
        response = client.post(
            "/api/v1/hydrology/analyze",
            json={
                "field_id": "",
                "tenant_id": "T1",
            },
            headers={"X-Tenant-Id": "T1"},
        )
        assert response.status_code == 422
