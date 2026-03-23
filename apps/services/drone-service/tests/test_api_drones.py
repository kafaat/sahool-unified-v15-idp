"""
Tests for drone management API endpoints - اختبارات نقاط نهاية إدارة الطائرات
"""

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient
from src.api.v1.drones import (
    DroneCreate,
    DroneResponse,
    _drone_to_response,
    _drones,
    _get_tenant_id,
    _raise_not_found,
    router,
)


class TestDroneModels:
    """Test Pydantic models."""

    def test_drone_create_defaults(self):
        d = DroneCreate(name="Test", model="DJI-T30", serial_number="SN1")
        assert d.drone_type == "custom"
        assert d.name_ar is None
        assert d.max_payload_kg is None

    def test_drone_create_all_fields(self):
        d = DroneCreate(
            name="Test",
            name_ar="اختبار",
            model="DJI-T40",
            serial_number="SN2",
            drone_type="sprayer",
            max_payload_kg=40.0,
            tank_capacity_l=30.0,
            max_flight_time_min=25.0,
        )
        assert d.name_ar == "اختبار"
        assert d.max_payload_kg == 40.0

    def test_drone_response_defaults(self):
        d = DroneResponse(id="1", name="D", model="M", serial_number="S", drone_type="custom")
        assert d.status == "active"
        assert d.tenant_id is None


class TestHelpers:
    """Test helper functions."""

    def test_get_tenant_id_with_attr(self):
        class U:
            tenant_id = "t1"

        assert _get_tenant_id(U()) == "t1"

    def test_get_tenant_id_default(self):
        assert _get_tenant_id(object()) == "default"

    def test_drone_to_response(self):
        d = {
            "id": "123",
            "name": "D1",
            "model": "M1",
            "serial_number": "S1",
            "drone_type": "custom",
            "status": "active",
            "extra_field": "ignore",
        }
        result = _drone_to_response(d)
        assert result["id"] == "123"
        assert result["name"] == "D1"
        assert "extra_field" not in result

    def test_raise_not_found(self):
        with pytest.raises(HTTPException) as exc_info:
            _raise_not_found()
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()


# --- API endpoint tests using httpx AsyncClient ---


def _create_test_app():
    """Create a test FastAPI app with the drones router and exception handlers."""
    from fastapi import FastAPI

    test_app = FastAPI()

    # Register shared exception handlers (since shared.errors_py is available)
    try:
        from shared.errors_py import setup_exception_handlers

        setup_exception_handlers(test_app)
    except ImportError:
        pass

    test_app.include_router(router)

    from src.api.v1.drones import get_current_user

    class FakeUser:
        id = "user-1"
        tenant_id = "test-tenant"
        roles = []

    async def fake_user():
        return FakeUser()

    test_app.dependency_overrides[get_current_user] = fake_user
    test_app.state.db_pool = None

    return test_app


@pytest.fixture
def app():
    return _create_test_app()


@pytest.fixture(autouse=True)
def clear_drones():
    _drones.clear()
    yield
    _drones.clear()


@pytest.mark.asyncio
async def test_list_drones_empty(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/drones/")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.asyncio
async def test_register_and_list_drone(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/drones/",
            json={
                "name": "TestDrone",
                "model": "DJI-T30",
                "serial_number": "SN001",
            },
        )
        assert create_resp.status_code == 201
        data = create_resp.json()
        assert data["name"] == "TestDrone"
        assert data["status"] == "active"

        list_resp = await client.get("/api/v1/drones/")
        assert len(list_resp.json()) == 1


@pytest.mark.asyncio
async def test_get_drone(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/drones/",
            json={
                "name": "D1",
                "model": "M1",
                "serial_number": "S1",
            },
        )
        drone_id = create_resp.json()["id"]

        get_resp = await client.get(f"/api/v1/drones/{drone_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == drone_id


@pytest.mark.asyncio
async def test_get_drone_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/drones/nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_drone(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/drones/",
            json={
                "name": "D1",
                "model": "M1",
                "serial_number": "S1",
            },
        )
        drone_id = create_resp.json()["id"]

        update_resp = await client.put(
            f"/api/v1/drones/{drone_id}",
            json={
                "name": "Updated",
                "model": "M2",
                "serial_number": "S2",
            },
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_update_drone_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.put(
            "/api/v1/drones/nonexistent",
            json={
                "name": "X",
                "model": "M",
                "serial_number": "S",
            },
        )
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_drone(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/drones/",
            json={
                "name": "D1",
                "model": "M1",
                "serial_number": "S1",
            },
        )
        drone_id = create_resp.json()["id"]

        del_resp = await client.delete(f"/api/v1/drones/{drone_id}")
        assert del_resp.status_code == 204

        get_resp = await client.get(f"/api/v1/drones/{drone_id}")
        assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_drone_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.delete("/api/v1/drones/nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_drone_status(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/drones/",
            json={
                "name": "D1",
                "model": "M1",
                "serial_number": "S1",
            },
        )
        drone_id = create_resp.json()["id"]

        status_resp = await client.get(f"/api/v1/drones/{drone_id}/status")
        assert status_resp.status_code == 200
        data = status_resp.json()
        assert data["drone_id"] == drone_id
        assert data["status"] == "active"
        assert "battery_percent" in data


@pytest.mark.asyncio
async def test_get_drone_status_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/drones/nonexistent/status")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_drone_telemetry(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/drones/",
            json={
                "name": "D1",
                "model": "M1",
                "serial_number": "S1",
            },
        )
        drone_id = create_resp.json()["id"]

        tel_resp = await client.get(f"/api/v1/drones/{drone_id}/telemetry")
        assert tel_resp.status_code == 200
        data = tel_resp.json()
        assert data["drone_id"] == drone_id
        assert "telemetry" in data


@pytest.mark.asyncio
async def test_get_drone_telemetry_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/drones/nonexistent/telemetry")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_drones_with_status_filter(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/api/v1/drones/",
            json={
                "name": "D1",
                "model": "M1",
                "serial_number": "S1",
            },
        )
        resp = await client.get("/api/v1/drones/?status=active")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        resp2 = await client.get("/api/v1/drones/?status=maintenance")
        assert resp2.status_code == 200
        assert len(resp2.json()) == 0
