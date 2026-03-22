"""
Tests for VRA API endpoints - اختبارات نقاط نهاية التطبيق بالمعدل المتغير
"""

import sys
import os

import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.api.v1.vra import (
    BoundsInput,
    Coordinate,
    NDVIPrescriptionRequest,
    SpotSprayRequest,
    _prescriptions,
    _raise_not_found,
    router,
)


class TestVRAModels:
    """Test Pydantic models for VRA."""

    def test_coordinate(self):
        c = Coordinate(lat=24.7, lng=46.7)
        assert c.lat == 24.7

    def test_bounds_input(self):
        b = BoundsInput(min_lat=24.0, max_lat=25.0, min_lng=46.0, max_lng=47.0)
        assert b.min_lat == 24.0

    def test_ndvi_prescription_request_defaults(self):
        r = NDVIPrescriptionRequest(
            field_id="f1",
            ndvi_grid=[[0.5, 0.6], [0.7, 0.8]],
            bounds=BoundsInput(min_lat=24.0, max_lat=25.0, min_lng=46.0, max_lng=47.0),
        )
        assert r.base_rate_l_ha == 10.0
        assert r.name == "NDVI Prescription"
        assert r.name_ar == "وصفة NDVI"

    def test_spot_spray_request_defaults(self):
        r = SpotSprayRequest(
            field_id="f1",
            detection_points=[{"lat": 24.7, "lng": 46.7}],
            boundary=[Coordinate(lat=24.7, lng=46.7)],
        )
        assert r.detection_type == "weed"
        assert r.base_rate_l_ha == 5.0
        assert r.name == "Spot Spray Map"
        assert r.name_ar == "خريطة الرش النقطي"


class TestVRAHelpers:
    def test_raise_not_found(self):
        with pytest.raises(Exception):
            _raise_not_found()


def _create_test_app():
    from fastapi import FastAPI
    test_app = FastAPI()

    try:
        from shared.errors_py import setup_exception_handlers
        setup_exception_handlers(test_app)
    except ImportError:
        pass

    test_app.include_router(router)

    from src.api.v1.vra import get_current_user

    class FakeUser:
        id = "user-1"
        tenant_id = "test-tenant"

    async def fake_user():
        return FakeUser()

    test_app.dependency_overrides[get_current_user] = fake_user
    test_app.state.db_pool = None
    test_app.state.nc = None
    return test_app


@pytest.fixture
def app():
    return _create_test_app()


@pytest.fixture(autouse=True)
def clear_prescriptions():
    _prescriptions.clear()
    yield
    _prescriptions.clear()


@pytest.mark.asyncio
async def test_list_prescriptions_empty(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/vra/prescriptions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["prescriptions"] == []
        assert data["count"] == 0


@pytest.mark.asyncio
async def test_list_prescriptions_with_data(app):
    _prescriptions["rx-1"] = {"id": "rx-1", "tenant_id": "test-tenant", "field_id": "f1"}
    _prescriptions["rx-2"] = {"id": "rx-2", "tenant_id": "other-tenant", "field_id": "f2"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/vra/prescriptions")
        data = resp.json()
        assert data["count"] == 1
        assert data["prescriptions"][0]["id"] == "rx-1"


@pytest.mark.asyncio
async def test_list_prescriptions_filter_field_id(app):
    _prescriptions["rx-1"] = {"id": "rx-1", "tenant_id": "test-tenant", "field_id": "f1"}
    _prescriptions["rx-2"] = {"id": "rx-2", "tenant_id": "test-tenant", "field_id": "f2"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/vra/prescriptions?field_id=f1")
        data = resp.json()
        assert data["count"] == 1


@pytest.mark.asyncio
async def test_get_prescription(app):
    _prescriptions["rx-1"] = {"id": "rx-1", "tenant_id": "test-tenant", "name": "Test"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/vra/prescriptions/rx-1")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Test"


@pytest.mark.asyncio
async def test_get_prescription_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/vra/prescriptions/nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_prescription_wrong_tenant(app):
    _prescriptions["rx-1"] = {"id": "rx-1", "tenant_id": "other-tenant", "name": "Test"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/vra/prescriptions/rx-1")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_ndvi_prescription_success(app):
    """With shared.drone_integration available, NDVI prescription should succeed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/vra/prescription/ndvi", json={
            "field_id": "f1",
            "ndvi_grid": [[0.3, 0.5, 0.7], [0.4, 0.6, 0.8], [0.2, 0.5, 0.9]],
            "bounds": {"min_lat": 24.0, "max_lat": 24.01, "min_lng": 46.0, "max_lng": 46.01},
            "base_rate_l_ha": 10.0,
            "name": "Test NDVI",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["field_id"] == "f1"
        assert "id" in data
        assert "zones_count" in data
        assert "zones" in data


@pytest.mark.asyncio
async def test_spot_spray_success(app):
    """With shared.drone_integration available, spot spray should succeed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/vra/prescription/spot-spray", json={
            "field_id": "f1",
            "detection_points": [
                {"lat": 24.705, "lng": 46.705, "confidence": 0.9, "type": "weed"},
                {"lat": 24.706, "lng": 46.706, "confidence": 0.85, "type": "weed"},
            ],
            "boundary": [
                {"lat": 24.70, "lng": 46.70},
                {"lat": 24.71, "lng": 46.70},
                {"lat": 24.71, "lng": 46.71},
                {"lat": 24.70, "lng": 46.71},
            ],
            "detection_type": "weed",
            "base_rate_l_ha": 5.0,
            "name": "Test Spot Spray",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["field_id"] == "f1"
        assert data["detection_type"] == "weed"
        assert "id" in data
