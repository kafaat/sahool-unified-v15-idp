"""
Tests for main module (health, metrics, root endpoints) - اختبارات الوحدة الرئيسية
"""

import pytest
from httpx import ASGITransport, AsyncClient
from src.main import _metrics, app


@pytest.fixture(autouse=True)
def reset_metrics():
    """Reset metrics and app state before each test."""
    _metrics["requests_total"] = 0
    _metrics["requests_errors"] = 0
    _metrics["request_duration_sum"] = 0.0
    _metrics["request_duration_count"] = 0
    app.state.db_connected = False
    app.state.nats_connected = False
    yield
    app.state.db_connected = False
    app.state.nats_connected = False


@pytest.mark.asyncio
async def test_healthz():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/healthz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "drone-service"
        assert "version" in data


@pytest.mark.asyncio
async def test_readyz_not_ready():
    """Without DB or NATS, readiness should return 503."""
    app.state.db_connected = False
    app.state.nats_connected = False
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/readyz")
        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "not_ready"


@pytest.mark.asyncio
async def test_readyz_db_connected():
    app.state.db_connected = True
    app.state.nats_connected = False
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/readyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"
        assert data["checks"]["database"] == "connected"
        assert data["checks"]["nats"] == "disconnected"


@pytest.mark.asyncio
async def test_readyz_nats_connected():
    app.state.db_connected = False
    app.state.nats_connected = True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/readyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_health_degraded():
    app.state.db_connected = False
    app.state.nats_connected = False
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "degraded"


@pytest.mark.asyncio
async def test_health_ok():
    app.state.db_connected = True
    app.state.nats_connected = True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
        data = resp.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_metrics_endpoint():
    app.state.db_connected = False
    app.state.nats_connected = False
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/metrics")
        assert resp.status_code == 200
        text = resp.text
        assert "drone_service_info" in text
        assert "drone_service_up 1" in text
        assert "drone_service_db_up 0" in text
        assert "drone_service_nats_up 0" in text
        assert "drone_service_requests_total" in text


@pytest.mark.asyncio
async def test_metrics_with_connections():
    app.state.db_connected = True
    app.state.nats_connected = True
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/metrics")
        text = resp.text
        assert "drone_service_db_up 1" in text
        assert "drone_service_nats_up 1" in text


@pytest.mark.asyncio
async def test_metrics_with_request_data():
    _metrics["requests_total"] = 50
    _metrics["requests_errors"] = 5
    _metrics["request_duration_sum"] = 10.0
    _metrics["request_duration_count"] = 50
    app.state.db_connected = False
    app.state.nats_connected = False
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/metrics")
        text = resp.text
        assert "drone_service_requests_total 50" in text
        assert "drone_service_requests_errors_total 5" in text
        assert "0.200000" in text  # avg duration


@pytest.mark.asyncio
async def test_root_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Include X-Tenant-Id header required by TenantContextMiddleware (must be valid UUID)
        resp = await client.get("/", headers={"X-Tenant-Id": "12345678-1234-1234-1234-123456789abc"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["service"] == "drone-service"
        assert "version" in data
        assert "documentation" in data
        assert "health" in data
