"""
Tests for mission management API endpoints - اختبارات نقاط نهاية إدارة المهام
"""

import pytest
from httpx import ASGITransport, AsyncClient
from src.api.v1.missions import (
    VALID_TRANSITIONS,
    MissionCreate,
    MissionResponse,
    _mission_to_response,
    _missions,
    _validate_transition,
    router,
)


class TestMissionModels:
    """Test Pydantic models."""

    def test_mission_create_defaults(self):
        m = MissionCreate(drone_id="d1", name="Test")
        assert m.mission_type == "spray"
        assert m.flight_plan_id is None
        assert m.name_ar is None
        assert m.field_id is None

    def test_mission_response(self):
        m = MissionResponse(id="1", mission_type="spray", name="T", status="planned")
        assert m.drone_id is None
        assert m.tenant_id is None


class TestValidTransitions:
    """Test mission state transition rules."""

    def test_planned_can_go_active(self):
        assert "active" in VALID_TRANSITIONS["planned"]

    def test_active_can_go_paused_completed_aborted(self):
        assert set(VALID_TRANSITIONS["active"]) == {"paused", "completed", "aborted"}

    def test_paused_can_go_active_aborted(self):
        assert set(VALID_TRANSITIONS["paused"]) == {"active", "aborted"}

    def test_completed_is_terminal(self):
        assert VALID_TRANSITIONS["completed"] == []

    def test_aborted_is_terminal(self):
        assert VALID_TRANSITIONS["aborted"] == []


class TestValidateTransition:
    """Test _validate_transition helper."""

    def test_valid_transition(self):
        _validate_transition("planned", "active")  # should not raise

    def test_invalid_transition_raises(self):
        with pytest.raises((ValueError, Exception)):  # ValidationException
            _validate_transition("planned", "completed")

    def test_invalid_from_completed(self):
        with pytest.raises((ValueError, Exception)):  # ValidationException
            _validate_transition("completed", "active")

    def test_unknown_current_state(self):
        with pytest.raises((ValueError, Exception)):  # ValidationException
            _validate_transition("unknown", "active")


class TestMissionToResponse:
    """Test _mission_to_response helper."""

    def test_basic_conversion(self):
        m = {
            "id": "123",
            "drone_id": "d1",
            "mission_type": "spray",
            "name": "M1",
            "status": "planned",
            "tenant_id": "t1",
        }
        result = _mission_to_response(m)
        assert result["id"] == "123"
        assert result["drone_id"] == "d1"

    def test_conversion_with_none_drone_id(self):
        m = {"id": "123", "drone_id": None, "mission_type": "spray", "name": "M1", "status": "planned"}
        result = _mission_to_response(m)
        assert result["drone_id"] is None


def _create_test_app():
    from fastapi import FastAPI

    test_app = FastAPI()

    try:
        from shared.errors_py import setup_exception_handlers

        setup_exception_handlers(test_app)
    except ImportError:
        pass

    test_app.include_router(router)

    from src.api.v1.missions import get_current_user

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
def clear_missions():
    _missions.clear()
    yield
    _missions.clear()


@pytest.mark.asyncio
async def test_list_missions_empty(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/missions/")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.asyncio
async def test_create_mission(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "drone-1",
                "name": "Test Mission",
                "mission_type": "spray",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Mission"
        assert data["status"] == "planned"
        assert data["mission_type"] == "spray"


@pytest.mark.asyncio
async def test_get_mission(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "d1",
                "name": "M1",
            },
        )
        mission_id = create_resp.json()["id"]

        get_resp = await client.get(f"/api/v1/missions/{mission_id}")
        assert get_resp.status_code == 200


@pytest.mark.asyncio
async def test_get_mission_not_found(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/v1/missions/nonexistent")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_start_mission(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "d1",
                "name": "M1",
            },
        )
        mission_id = create_resp.json()["id"]

        start_resp = await client.post(f"/api/v1/missions/{mission_id}/start")
        assert start_resp.status_code == 200
        data = start_resp.json()
        assert data["status"] == "active"
        assert data["message"] == "Mission started"


@pytest.mark.asyncio
async def test_pause_mission(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "d1",
                "name": "M1",
            },
        )
        mission_id = create_resp.json()["id"]

        await client.post(f"/api/v1/missions/{mission_id}/start")
        pause_resp = await client.post(f"/api/v1/missions/{mission_id}/pause")
        assert pause_resp.status_code == 200
        assert pause_resp.json()["status"] == "paused"


@pytest.mark.asyncio
async def test_resume_mission(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "d1",
                "name": "M1",
            },
        )
        mission_id = create_resp.json()["id"]

        await client.post(f"/api/v1/missions/{mission_id}/start")
        await client.post(f"/api/v1/missions/{mission_id}/pause")
        resume_resp = await client.post(f"/api/v1/missions/{mission_id}/resume")
        assert resume_resp.status_code == 200
        assert resume_resp.json()["status"] == "active"


@pytest.mark.asyncio
async def test_complete_mission(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "d1",
                "name": "M1",
            },
        )
        mission_id = create_resp.json()["id"]

        await client.post(f"/api/v1/missions/{mission_id}/start")
        complete_resp = await client.post(f"/api/v1/missions/{mission_id}/complete")
        assert complete_resp.status_code == 200
        assert complete_resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_abort_mission(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "d1",
                "name": "M1",
            },
        )
        mission_id = create_resp.json()["id"]

        await client.post(f"/api/v1/missions/{mission_id}/start")
        abort_resp = await client.post(f"/api/v1/missions/{mission_id}/abort")
        assert abort_resp.status_code == 200
        assert abort_resp.json()["status"] == "aborted"


@pytest.mark.asyncio
async def test_invalid_transition_planned_to_completed(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "d1",
                "name": "M1",
            },
        )
        mission_id = create_resp.json()["id"]

        resp = await client.post(f"/api/v1/missions/{mission_id}/complete")
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_invalid_transition_completed_to_active(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "d1",
                "name": "M1",
            },
        )
        mission_id = create_resp.json()["id"]

        await client.post(f"/api/v1/missions/{mission_id}/start")
        await client.post(f"/api/v1/missions/{mission_id}/complete")
        resp = await client.post(f"/api/v1/missions/{mission_id}/start")
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_start_nonexistent_mission(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/missions/nonexistent/start")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_missions_with_status_filter(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/v1/missions/", json={"drone_id": "d1", "name": "M1"})
        await client.post("/api/v1/missions/", json={"drone_id": "d2", "name": "M2"})

        resp = await client.get("/api/v1/missions/?status=planned")
        assert len(resp.json()) == 2

        resp2 = await client.get("/api/v1/missions/?status=active")
        assert len(resp2.json()) == 0


@pytest.mark.asyncio
async def test_list_missions_with_drone_id_filter(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post("/api/v1/missions/", json={"drone_id": "d1", "name": "M1"})
        await client.post("/api/v1/missions/", json={"drone_id": "d2", "name": "M2"})

        resp = await client.get("/api/v1/missions/?drone_id=d1")
        assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_abort_paused_mission(app):
    """Paused missions can be aborted."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_resp = await client.post(
            "/api/v1/missions/",
            json={
                "drone_id": "d1",
                "name": "M1",
            },
        )
        mission_id = create_resp.json()["id"]

        await client.post(f"/api/v1/missions/{mission_id}/start")
        await client.post(f"/api/v1/missions/{mission_id}/pause")
        abort_resp = await client.post(f"/api/v1/missions/{mission_id}/abort")
        assert abort_resp.status_code == 200
        assert abort_resp.json()["status"] == "aborted"
