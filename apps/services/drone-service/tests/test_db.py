"""
Tests for database repository module - اختبارات وحدة مستودع قاعدة البيانات
"""

import sys
import os
import uuid
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.db import DroneRepository, _generate_id, _safe_uuid


class TestHelperFunctions:
    """Test module-level helper functions."""

    def test_generate_id_returns_valid_uuid(self):
        result = _generate_id()
        uuid.UUID(result)  # should not raise

    def test_generate_id_returns_unique(self):
        ids = {_generate_id() for _ in range(100)}
        assert len(ids) == 100

    def test_safe_uuid_valid(self):
        valid = "12345678-1234-1234-1234-123456789abc"
        result = _safe_uuid(valid)
        assert result == uuid.UUID(valid)

    def test_safe_uuid_invalid_string(self):
        assert _safe_uuid("not-a-uuid") is None

    def test_safe_uuid_none(self):
        assert _safe_uuid(None) is None

    def test_safe_uuid_empty_string(self):
        assert _safe_uuid("") is None

    def test_safe_uuid_integer(self):
        assert _safe_uuid(123) is None


def _make_pool():
    """Create a mock asyncpg pool with proper async context manager."""
    conn = AsyncMock()

    @asynccontextmanager
    async def acquire():
        yield conn

    pool = MagicMock()
    pool.acquire = acquire
    return pool, conn


class TestDroneRepositoryDrones:
    """Test DroneRepository drone operations."""

    @pytest.mark.asyncio
    async def test_list_drones_no_filter(self):
        pool, conn = _make_pool()
        conn.fetch.return_value = [
            {"id": uuid.uuid4(), "name": "Drone1", "status": "active", "tenant_id": "t1"}
        ]
        repo = DroneRepository(pool)
        result = await repo.list_drones("t1")
        assert len(result) == 1
        conn.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_drones_with_status_filter(self):
        pool, conn = _make_pool()
        conn.fetch.return_value = []
        repo = DroneRepository(pool)
        result = await repo.list_drones("t1", status="active")
        assert result == []
        call_args = conn.fetch.call_args
        assert "$2" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_get_drone_valid_id(self):
        pool, conn = _make_pool()
        drone_id = str(uuid.uuid4())
        conn.fetchrow.return_value = {"id": drone_id, "name": "D1"}
        repo = DroneRepository(pool)
        result = await repo.get_drone(drone_id, "t1")
        assert result is not None
        assert result["name"] == "D1"

    @pytest.mark.asyncio
    async def test_get_drone_invalid_id(self):
        pool, conn = _make_pool()
        repo = DroneRepository(pool)
        result = await repo.get_drone("bad-id", "t1")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_drone_not_found(self):
        pool, conn = _make_pool()
        conn.fetchrow.return_value = None
        repo = DroneRepository(pool)
        result = await repo.get_drone(str(uuid.uuid4()), "t1")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_drone(self):
        pool, conn = _make_pool()
        conn.fetchrow.return_value = {"id": uuid.uuid4(), "name": "New", "status": "active"}
        repo = DroneRepository(pool)
        result = await repo.create_drone("t1", {
            "name": "New",
            "model": "DJI-T30",
            "serial_number": "SN001",
            "drone_type": "sprayer",
        })
        assert result["name"] == "New"
        conn.fetchrow.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_drone_valid(self):
        pool, conn = _make_pool()
        drone_id = str(uuid.uuid4())
        conn.fetchrow.return_value = {"id": drone_id, "name": "Updated"}
        repo = DroneRepository(pool)
        result = await repo.update_drone(drone_id, "t1", {
            "name": "Updated",
            "model": "DJI-T40",
            "serial_number": "SN002",
        })
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_drone_invalid_id(self):
        pool, conn = _make_pool()
        repo = DroneRepository(pool)
        result = await repo.update_drone("bad", "t1", {})
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_drone_success(self):
        pool, conn = _make_pool()
        conn.execute.return_value = "DELETE 1"
        repo = DroneRepository(pool)
        result = await repo.delete_drone(str(uuid.uuid4()), "t1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_drone_not_found(self):
        pool, conn = _make_pool()
        conn.execute.return_value = "DELETE 0"
        repo = DroneRepository(pool)
        result = await repo.delete_drone(str(uuid.uuid4()), "t1")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_drone_invalid_id(self):
        pool, conn = _make_pool()
        repo = DroneRepository(pool)
        result = await repo.delete_drone("bad-id", "t1")
        assert result is False

    @pytest.mark.asyncio
    async def test_update_drone_status_valid(self):
        pool, conn = _make_pool()
        drone_id = str(uuid.uuid4())
        conn.fetchrow.return_value = {"id": drone_id, "status": "maintenance"}
        repo = DroneRepository(pool)
        result = await repo.update_drone_status(drone_id, "t1", "maintenance")
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_drone_status_invalid_id(self):
        pool, conn = _make_pool()
        repo = DroneRepository(pool)
        result = await repo.update_drone_status("bad", "t1", "active")
        assert result is None


class TestDroneRepositoryFlightPlans:
    """Test DroneRepository flight plan operations."""

    @pytest.mark.asyncio
    async def test_list_flight_plans_no_filter(self):
        pool, conn = _make_pool()
        conn.fetch.return_value = []
        repo = DroneRepository(pool)
        result = await repo.list_flight_plans("t1")
        assert result == []

    @pytest.mark.asyncio
    async def test_list_flight_plans_with_field_id(self):
        pool, conn = _make_pool()
        conn.fetch.return_value = [{"id": "p1", "plan_type": "spray"}]
        repo = DroneRepository(pool)
        result = await repo.list_flight_plans("t1", field_id="f1")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_flight_plans_with_both_filters(self):
        pool, conn = _make_pool()
        conn.fetch.return_value = []
        repo = DroneRepository(pool)
        result = await repo.list_flight_plans("t1", field_id="f1", plan_type="spray")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_flight_plan_valid(self):
        pool, conn = _make_pool()
        plan_id = str(uuid.uuid4())
        conn.fetchrow.return_value = {"id": plan_id, "name": "Plan1"}
        repo = DroneRepository(pool)
        result = await repo.get_flight_plan(plan_id, "t1")
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_flight_plan_invalid_id(self):
        pool, conn = _make_pool()
        repo = DroneRepository(pool)
        result = await repo.get_flight_plan("bad", "t1")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_flight_plan(self):
        pool, conn = _make_pool()
        conn.fetchrow.return_value = {"id": uuid.uuid4(), "name": "Plan1", "plan_type": "spray"}
        repo = DroneRepository(pool)
        result = await repo.create_flight_plan("t1", {
            "name": "Plan1",
            "field_id": "f1",
            "plan_type": "spray",
            "waypoints": [{"lat": 24.7, "lng": 46.7}],
        })
        assert result["name"] == "Plan1"


class TestDroneRepositoryMissions:
    """Test DroneRepository mission operations."""

    @pytest.mark.asyncio
    async def test_list_missions_no_filter(self):
        pool, conn = _make_pool()
        conn.fetch.return_value = []
        repo = DroneRepository(pool)
        result = await repo.list_missions("t1")
        assert result == []

    @pytest.mark.asyncio
    async def test_list_missions_with_status(self):
        pool, conn = _make_pool()
        conn.fetch.return_value = [{"id": "m1", "status": "active"}]
        repo = DroneRepository(pool)
        result = await repo.list_missions("t1", status="active")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_missions_with_drone_id(self):
        pool, conn = _make_pool()
        conn.fetch.return_value = []
        repo = DroneRepository(pool)
        drone_id = str(uuid.uuid4())
        result = await repo.list_missions("t1", drone_id=drone_id)
        assert result == []

    @pytest.mark.asyncio
    async def test_list_missions_with_invalid_drone_id(self):
        pool, conn = _make_pool()
        conn.fetch.return_value = []
        repo = DroneRepository(pool)
        result = await repo.list_missions("t1", drone_id="bad-id")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_mission_valid(self):
        pool, conn = _make_pool()
        mid = str(uuid.uuid4())
        conn.fetchrow.return_value = {"id": mid, "status": "planned"}
        repo = DroneRepository(pool)
        result = await repo.get_mission(mid, "t1")
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_mission_invalid_id(self):
        pool, conn = _make_pool()
        repo = DroneRepository(pool)
        result = await repo.get_mission("bad", "t1")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_mission_success(self):
        pool, conn = _make_pool()
        conn.fetchrow.return_value = {"id": uuid.uuid4(), "name": "M1", "status": "planned"}
        repo = DroneRepository(pool)
        result = await repo.create_mission("t1", {
            "name": "M1",
            "drone_id": str(uuid.uuid4()),
            "flight_plan_id": str(uuid.uuid4()),
            "mission_type": "spray",
        })
        assert result is not None

    @pytest.mark.asyncio
    async def test_create_mission_invalid_drone_id(self):
        pool, conn = _make_pool()
        repo = DroneRepository(pool)
        result = await repo.create_mission("t1", {
            "name": "M1",
            "drone_id": "bad-uuid",
            "mission_type": "spray",
        })
        assert result is None

    @pytest.mark.asyncio
    async def test_create_mission_invalid_plan_id(self):
        pool, conn = _make_pool()
        repo = DroneRepository(pool)
        result = await repo.create_mission("t1", {
            "name": "M1",
            "drone_id": str(uuid.uuid4()),
            "flight_plan_id": "bad-uuid",
            "mission_type": "spray",
        })
        assert result is None

    @pytest.mark.asyncio
    async def test_create_mission_no_drone_id(self):
        pool, conn = _make_pool()
        conn.fetchrow.return_value = {"id": uuid.uuid4(), "name": "M1", "status": "planned"}
        repo = DroneRepository(pool)
        result = await repo.create_mission("t1", {
            "name": "M1",
            "mission_type": "mapping",
        })
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_mission_status_active(self):
        pool, conn = _make_pool()
        mid = str(uuid.uuid4())
        conn.fetchrow.return_value = {"id": mid, "status": "active"}
        repo = DroneRepository(pool)
        result = await repo.update_mission_status(mid, "t1", "active")
        assert result is not None
        assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_update_mission_status_completed(self):
        pool, conn = _make_pool()
        mid = str(uuid.uuid4())
        conn.fetchrow.return_value = {"id": mid, "status": "completed"}
        repo = DroneRepository(pool)
        result = await repo.update_mission_status(mid, "t1", "completed")
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_mission_status_aborted(self):
        pool, conn = _make_pool()
        mid = str(uuid.uuid4())
        conn.fetchrow.return_value = {"id": mid, "status": "aborted"}
        repo = DroneRepository(pool)
        result = await repo.update_mission_status(mid, "t1", "aborted")
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_mission_status_other(self):
        pool, conn = _make_pool()
        mid = str(uuid.uuid4())
        conn.fetchrow.return_value = {"id": mid, "status": "paused"}
        repo = DroneRepository(pool)
        result = await repo.update_mission_status(mid, "t1", "paused")
        assert result is not None

    @pytest.mark.asyncio
    async def test_update_mission_status_invalid_id(self):
        pool, conn = _make_pool()
        repo = DroneRepository(pool)
        result = await repo.update_mission_status("bad", "t1", "active")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_mission_status_not_found(self):
        pool, conn = _make_pool()
        conn.fetchrow.return_value = None
        repo = DroneRepository(pool)
        result = await repo.update_mission_status(str(uuid.uuid4()), "t1", "active")
        assert result is None
