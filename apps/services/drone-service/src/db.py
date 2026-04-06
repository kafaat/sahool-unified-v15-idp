"""
Database repository for drone service - مستودع قاعدة البيانات لخدمة الطائرات
Provides async database operations with tenant isolation.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

logger = structlog.get_logger()


def _generate_id() -> str:
    return str(uuid.uuid4())


def _safe_uuid(value: str) -> uuid.UUID | None:
    """Parse a string as UUID, returning None if invalid."""
    try:
        return uuid.UUID(value)
    except (ValueError, TypeError, AttributeError):
        return None


class DroneRepository:
    """Database operations for drones, flight plans, and missions."""

    def __init__(self, db_pool):
        self.pool = db_pool

    # ─────────────────────────────────────────────────────────────────────
    # Drones - الطائرات
    # ─────────────────────────────────────────────────────────────────────

    async def list_drones(
        self, tenant_id: str, status: str | None = None, limit: int = 500, offset: int = 0
    ) -> list[dict]:
        query = "SELECT * FROM drones WHERE tenant_id = $1"
        params: list[Any] = [tenant_id]
        idx = 2
        if status:
            query += f" AND status = ${idx}"
            params.append(status)
            idx += 1
        query += f" ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx + 1}"
        params.extend([limit, offset])
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)  # nosemgrep: asyncpg-sqli -- query uses $N parameterized placeholders
            return [dict(r) for r in rows]

    async def get_drone(self, drone_id: str, tenant_id: str) -> dict | None:
        parsed = _safe_uuid(drone_id)
        if not parsed:
            return None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM drones WHERE id = $1 AND tenant_id = $2",
                parsed,
                tenant_id,
            )
            return dict(row) if row else None

    async def create_drone(self, tenant_id: str, data: dict) -> dict:
        drone_id = _generate_id()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO drones (id, tenant_id, name, name_ar, model, serial_number,
                   drone_type, max_payload_kg, tank_capacity_l, max_flight_time_min, status)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'active')
                   RETURNING *""",
                uuid.UUID(drone_id),
                tenant_id,
                data["name"],
                data.get("name_ar"),
                data["model"],
                data["serial_number"],
                data.get("drone_type", "custom"),
                data.get("max_payload_kg"),
                data.get("tank_capacity_l"),
                data.get("max_flight_time_min"),
            )
            return dict(row)

    async def update_drone(self, drone_id: str, tenant_id: str, data: dict) -> dict | None:
        parsed = _safe_uuid(drone_id)
        if not parsed:
            return None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """UPDATE drones SET name=$3, name_ar=$4, model=$5, serial_number=$6, drone_type=$7
                   WHERE id=$1 AND tenant_id=$2 RETURNING *""",
                parsed,
                tenant_id,
                data["name"],
                data.get("name_ar"),
                data["model"],
                data["serial_number"],
                data.get("drone_type", "custom"),
            )
            return dict(row) if row else None

    async def delete_drone(self, drone_id: str, tenant_id: str) -> bool:
        parsed = _safe_uuid(drone_id)
        if not parsed:
            return False
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM drones WHERE id=$1 AND tenant_id=$2",
                parsed,
                tenant_id,
            )
            return result == "DELETE 1"

    async def update_drone_status(self, drone_id: str, tenant_id: str, status: str) -> dict | None:
        parsed = _safe_uuid(drone_id)
        if not parsed:
            return None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "UPDATE drones SET status=$3 WHERE id=$1 AND tenant_id=$2 RETURNING *",
                parsed,
                tenant_id,
                status,
            )
            return dict(row) if row else None

    # ─────────────────────────────────────────────────────────────────────
    # Flight Plans - خطط الرحلات
    # ─────────────────────────────────────────────────────────────────────

    async def list_flight_plans(
        self,
        tenant_id: str,
        field_id: str | None = None,
        plan_type: str | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> list[dict]:
        query = "SELECT * FROM flight_plans WHERE tenant_id = $1"
        params: list[Any] = [tenant_id]
        idx = 2
        if field_id:
            query += f" AND field_id = ${idx}"
            params.append(field_id)
            idx += 1
        if plan_type:
            query += f" AND plan_type = ${idx}"
            params.append(plan_type)
            idx += 1
        query += f" ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx + 1}"
        params.extend([limit, offset])
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)  # nosemgrep: asyncpg-sqli -- query uses $N parameterized placeholders
            return [dict(r) for r in rows]

    async def get_flight_plan(self, plan_id: str, tenant_id: str) -> dict | None:
        parsed = _safe_uuid(plan_id)
        if not parsed:
            return None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM flight_plans WHERE id=$1 AND tenant_id=$2",
                parsed,
                tenant_id,
            )
            return dict(row) if row else None

    async def create_flight_plan(self, tenant_id: str, data: dict) -> dict:
        plan_id = _generate_id()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO flight_plans (id, tenant_id, field_id, name, name_ar, plan_type,
                   success, total_distance_m, estimated_duration_min, waypoints_count,
                   total_spray_volume_l, area_ha, waypoints, boundary)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
                   RETURNING *""",
                uuid.UUID(plan_id),
                tenant_id,
                data.get("field_id"),
                data["name"],
                data.get("name_ar"),
                data.get("plan_type", "spray"),
                data.get("success", True),
                data.get("total_distance_m"),
                data.get("estimated_duration_min"),
                data.get("waypoints_count", 0),
                data.get("total_spray_volume_l"),
                data.get("area_ha"),
                json.dumps(data.get("waypoints", [])),
                json.dumps(data.get("boundary")) if data.get("boundary") else None,
            )
            return dict(row)

    # ─────────────────────────────────────────────────────────────────────
    # Missions - المهام
    # ─────────────────────────────────────────────────────────────────────

    async def list_missions(
        self,
        tenant_id: str,
        status: str | None = None,
        drone_id: str | None = None,
        limit: int = 500,
        offset: int = 0,
    ) -> list[dict]:
        query = "SELECT * FROM missions WHERE tenant_id = $1"
        params: list[Any] = [tenant_id]
        idx = 2
        if status:
            query += f" AND status = ${idx}"
            params.append(status)
            idx += 1
        if drone_id:
            parsed_drone = _safe_uuid(drone_id)
            if parsed_drone:
                query += f" AND drone_id = ${idx}"
                params.append(parsed_drone)
                idx += 1
        query += f" ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx + 1}"
        params.extend([limit, offset])
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)  # nosemgrep: asyncpg-sqli -- query uses $N parameterized placeholders
            return [dict(r) for r in rows]

    async def get_mission(self, mission_id: str, tenant_id: str) -> dict | None:
        parsed = _safe_uuid(mission_id)
        if not parsed:
            return None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM missions WHERE id=$1 AND tenant_id=$2",
                parsed,
                tenant_id,
            )
            return dict(row) if row else None

    async def create_mission(self, tenant_id: str, data: dict) -> dict | None:
        mission_id = _generate_id()
        drone_uuid = _safe_uuid(data["drone_id"]) if data.get("drone_id") else None
        plan_uuid = _safe_uuid(data["flight_plan_id"]) if data.get("flight_plan_id") else None
        if data.get("drone_id") and not drone_uuid:
            logger.warning("invalid_drone_uuid", drone_id=data.get("drone_id"))
            return None
        if data.get("flight_plan_id") and not plan_uuid:
            logger.warning("invalid_plan_uuid", flight_plan_id=data.get("flight_plan_id"))
            return None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO missions (id, tenant_id, drone_id, flight_plan_id,
                   name, name_ar, mission_type, field_id, status)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,'planned')
                   RETURNING *""",
                uuid.UUID(mission_id),
                tenant_id,
                drone_uuid,
                plan_uuid,
                data["name"],
                data.get("name_ar"),
                data.get("mission_type", "spray"),
                data.get("field_id"),
            )
            return dict(row)

    async def update_mission_status(self, mission_id: str, tenant_id: str, status: str) -> dict | None:
        parsed = _safe_uuid(mission_id)
        if not parsed:
            return None
        now = datetime.now(UTC)
        async with self.pool.acquire() as conn:
            if status == "active":
                row = await conn.fetchrow(
                    """UPDATE missions SET status=$3, started_at=COALESCE(started_at, $4)
                       WHERE id=$1 AND tenant_id=$2 RETURNING *""",
                    parsed,
                    tenant_id,
                    status,
                    now,
                )
            elif status in ("completed", "aborted"):
                row = await conn.fetchrow(
                    """UPDATE missions SET status=$3, completed_at=$4
                       WHERE id=$1 AND tenant_id=$2 RETURNING *""",
                    parsed,
                    tenant_id,
                    status,
                    now,
                )
            else:
                row = await conn.fetchrow(
                    "UPDATE missions SET status=$3 WHERE id=$1 AND tenant_id=$2 RETURNING *",
                    parsed,
                    tenant_id,
                    status,
                )
            return dict(row) if row else None
