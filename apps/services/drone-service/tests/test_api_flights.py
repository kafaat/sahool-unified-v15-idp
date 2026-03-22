"""
Tests for flight planning API endpoints - اختبارات نقاط نهاية تخطيط الرحلات
"""

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.v1.flights import (
    Coordinate,
    MappingFlightRequest,
    ResourceEstimateRequest,
    SprayFlightRequest,
    WeatherCheckRequest,
    _flight_plans,
    _get_tenant_id,
    router,
)


class TestFlightModels:
    """Test Pydantic models for flight planning."""

    def test_coordinate(self):
        c = Coordinate(lat=24.7, lng=46.7)
        assert c.lat == 24.7
        assert c.lng == 46.7

    def test_spray_flight_request_defaults(self):
        r = SprayFlightRequest(
            field_id="f1",
            boundary=[Coordinate(lat=24.7, lng=46.7)],
            name="Test",
        )
        assert r.spray_rate_l_ha == 10.0
        assert r.swath_width_m == 5.0
        assert r.altitude_m == 3.0
        assert r.name_ar is None

    def test_mapping_flight_request_defaults(self):
        r = MappingFlightRequest(
            field_id="f1",
            boundary=[Coordinate(lat=24.7, lng=46.7)],
            name="Test",
        )
        assert r.gsd_cm_px == 2.0
        assert r.frontal_overlap == 80.0
        assert r.side_overlap == 70.0

    def test_weather_check_request_defaults(self):
        r = WeatherCheckRequest(lat=24.7, lng=46.7)
        assert r.wind_speed_ms == 0.0
        assert r.temperature_c == 25.0
        assert r.humidity_percent == 50.0
        assert r.precipitation_mm == 0.0

    def test_resource_estimate_request_defaults(self):
        r = ResourceEstimateRequest(area_ha=10.0)
        assert r.spray_rate_l_ha == 10.0
        assert r.tank_capacity_l == 20.0
        assert r.flight_time_per_tank_min == 15.0


def _create_test_app():
    from fastapi import FastAPI

    test_app = FastAPI()

    try:
        from shared.errors_py import setup_exception_handlers

        setup_exception_handlers(test_app)
    except ImportError:
        pass

    test_app.include_router(router)

    from src.api.v1.flights import get_current_user

    class FakeUser:
        id = "user-1"
        tenant_id = "test-tenant"

    async def fake_user():
        return FakeUser()

    test_app.dependency_overrides[get_current_user] = fake_user
    test_app.state.db_pool = None
    return test_app


@pytest.fixture
def app():
    return _create_test_app()


@pytest.fixture(autouse=True)
def clear_plans():
    _flight_plans.clear()
    yield
    _flight_plans.clear()


@pytest.mark.asyncio
async def test_weather_check_safe(app):
    """Test weather check with safe conditions."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/flights/weather-check",
            json={
                "lat": 24.7,
                "lng": 46.7,
                "wind_speed_ms": 3.0,
                "temperature_c": 25.0,
                "humidity_percent": 50.0,
                "precipitation_mm": 0.0,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["safe_to_fly"] is True


@pytest.mark.asyncio
async def test_weather_check_high_wind(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/flights/weather-check",
            json={
                "lat": 24.7,
                "lng": 46.7,
                "wind_speed_ms": 10.0,
                "temperature_c": 25.0,
                "humidity_percent": 50.0,
                "precipitation_mm": 0.0,
            },
        )
        data = resp.json()
        assert data["safe_to_fly"] is False
        assert data["condition"] == "prohibited"


@pytest.mark.asyncio
async def test_weather_check_precipitation(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/flights/weather-check",
            json={
                "lat": 24.7,
                "lng": 46.7,
                "wind_speed_ms": 2.0,
                "temperature_c": 25.0,
                "humidity_percent": 80.0,
                "precipitation_mm": 5.0,
            },
        )
        data = resp.json()
        assert data["safe_to_fly"] is False


@pytest.mark.asyncio
async def test_weather_check_returns_condition(app):
    """Verify the weather check response has expected fields."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/flights/weather-check",
            json={
                "lat": 24.7,
                "lng": 46.7,
                "wind_speed_ms": 0.0,
                "temperature_c": 25.0,
                "humidity_percent": 50.0,
                "precipitation_mm": 0.0,
            },
        )
        data = resp.json()
        assert "safe_to_fly" in data
        assert "condition" in data
        assert "message" in data
        assert "message_ar" in data
        assert "warnings" in data
        assert "warnings_ar" in data


@pytest.mark.asyncio
async def test_estimate_resources(app):
    """Test resource estimation (uses shared.drone_integration)."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/flights/estimate",
            json={
                "area_ha": 10.0,
                "spray_rate_l_ha": 10.0,
                "tank_capacity_l": 20.0,
                "flight_time_per_tank_min": 15.0,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["area_ha"] == 10.0
        assert data["total_volume_l"] == 100
        assert data["tank_fills"] == 5
        assert data["batteries_needed"] == 4
        assert data["total_flight_time_min"] == 75


@pytest.mark.asyncio
async def test_estimate_resources_small_area(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/flights/estimate",
            json={
                "area_ha": 0.5,
                "spray_rate_l_ha": 10.0,
                "tank_capacity_l": 20.0,
                "flight_time_per_tank_min": 15.0,
            },
        )
        data = resp.json()
        assert data["total_volume_l"] > 0
        assert data["tank_fills"] >= 1
        assert data["batteries_needed"] >= 1


@pytest.mark.asyncio
async def test_list_flight_plans_empty(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/flights/plans")
        assert resp.status_code == 200
        data = resp.json()
        assert data["plans"] == []
        assert data["count"] == 0


@pytest.mark.asyncio
async def test_list_flight_plans_with_data(app):
    _flight_plans["FP-1"] = {"id": "FP-1", "tenant_id": "test-tenant", "field_id": "f1", "plan_type": "spray"}
    _flight_plans["FP-2"] = {"id": "FP-2", "tenant_id": "other-tenant", "field_id": "f2", "plan_type": "mapping"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/flights/plans")
        data = resp.json()
        assert data["count"] == 1
        assert data["plans"][0]["id"] == "FP-1"


@pytest.mark.asyncio
async def test_list_flight_plans_filter_field_id(app):
    _flight_plans["FP-1"] = {"id": "FP-1", "tenant_id": "test-tenant", "field_id": "f1", "plan_type": "spray"}
    _flight_plans["FP-2"] = {"id": "FP-2", "tenant_id": "test-tenant", "field_id": "f2", "plan_type": "spray"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/flights/plans?field_id=f1")
        data = resp.json()
        assert data["count"] == 1


@pytest.mark.asyncio
async def test_list_flight_plans_filter_plan_type(app):
    _flight_plans["FP-1"] = {"id": "FP-1", "tenant_id": "test-tenant", "field_id": "f1", "plan_type": "spray"}
    _flight_plans["FP-2"] = {"id": "FP-2", "tenant_id": "test-tenant", "field_id": "f1", "plan_type": "mapping"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/flights/plans?plan_type=mapping")
        data = resp.json()
        assert data["count"] == 1
        assert data["plans"][0]["plan_type"] == "mapping"


@pytest.mark.asyncio
async def test_get_flight_plan(app):
    _flight_plans["FP-1"] = {"id": "FP-1", "tenant_id": "test-tenant", "name": "Plan1"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/flights/plans/FP-1")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Plan1"


@pytest.mark.asyncio
async def test_get_flight_plan_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/flights/plans/nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_flight_plan_wrong_tenant(app):
    _flight_plans["FP-1"] = {"id": "FP-1", "tenant_id": "other-tenant", "name": "Plan1"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/flights/plans/FP-1")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_spray_flight_plan_success(app):
    """With shared.drone_integration available, spray planning should succeed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/flights/plan/spray",
            json={
                "field_id": "f1",
                "boundary": [
                    {"lat": 24.70, "lng": 46.70},
                    {"lat": 24.71, "lng": 46.70},
                    {"lat": 24.71, "lng": 46.71},
                    {"lat": 24.70, "lng": 46.71},
                ],
                "spray_rate_l_ha": 10.0,
                "swath_width_m": 5.0,
                "altitude_m": 3.0,
                "name": "Test Spray",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "spray"
        assert data["field_id"] == "f1"
        assert "id" in data
        assert "success" in data


@pytest.mark.asyncio
async def test_mapping_flight_plan_success(app):
    """With shared.drone_integration available, mapping planning should succeed."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/flights/plan/mapping",
            json={
                "field_id": "f1",
                "boundary": [
                    {"lat": 24.70, "lng": 46.70},
                    {"lat": 24.71, "lng": 46.70},
                    {"lat": 24.71, "lng": 46.71},
                    {"lat": 24.70, "lng": 46.71},
                ],
                "name": "Test Mapping",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "mapping"
        assert data["field_id"] == "f1"
        assert "id" in data
