# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Calibration Repository - مستودع المعايرة
==========================================
asyncpg-backed persistence for calibration runs, parameter sets,
and activation audit trail.

Follows the same pool-injection + in-memory-fallback pattern used
by ``shared.digital_twin.repository.TwinRepository``.
"""

from __future__ import annotations

import json
from typing import Any

import structlog

logger = structlog.get_logger()

# Soft import — when asyncpg is not available we still define the class
try:
    import asyncpg
except ImportError:  # pragma: no cover
    asyncpg = None  # type: ignore[assignment]


class CalibrationRepository:
    """
    Persistence layer for calibration runs and parameter sets.
    طبقة الثبات لتشغيلات المعايرة ومجموعات المعاملات.

    Args:
        db_pool: asyncpg connection pool (``None`` → in-memory stub).
    """

    def __init__(self, db_pool: Any = None) -> None:
        self._pool = db_pool

    # ------------------------------------------------------------------
    # Calibration Runs
    # ------------------------------------------------------------------

    async def create_run(self, payload: dict[str, Any]) -> str:
        """
        Insert a new calibration run with status 'queued'.
        إدراج تشغيل معايرة جديد بحالة 'في الطابور'.

        Required keys in ``payload``:
            tenant_id, field_id, season_id, crop_type,
            model_name, model_version, method, dataset_fingerprint
        """
        if self._pool is None:
            logger.warning("calibration_repo_no_pool", action="create_run")
            return "no-db"

        sql = """
        INSERT INTO calibration_run
          (tenant_id, field_id, season_id, crop_type,
           model_name, model_version, method,
           status, dataset_fingerprint, metrics, objective_value)
        VALUES
          ($1, $2, $3, $4, $5, $6, $7, 'queued', $8, '{}'::jsonb, NULL)
        RETURNING id::text
        """
        async with self._pool.acquire() as conn:
            return await conn.fetchval(
                sql,
                payload["tenant_id"],
                payload["field_id"],
                payload["season_id"],
                payload["crop_type"],
                payload["model_name"],
                payload["model_version"],
                payload["method"],
                payload["dataset_fingerprint"],
            )

    async def update_run_status(
        self,
        run_id: str,
        status: str,
        *,
        metrics: dict[str, Any] | None = None,
        objective_value: float | None = None,
        notes: str | None = None,
    ) -> None:
        """
        Transition a run to a new status.
        نقل التشغيل إلى حالة جديدة.

        Terminal statuses (succeeded, failed, cancelled) set ``ended_at``.
        """
        if self._pool is None:
            return

        sql = """
        UPDATE calibration_run
        SET status          = $2,
            metrics         = COALESCE($3::jsonb, metrics),
            objective_value = COALESCE($4, objective_value),
            notes           = COALESCE($5, notes),
            ended_at        = CASE
                                WHEN $2 IN ('succeeded', 'failed', 'cancelled')
                                THEN now()
                                ELSE ended_at
                              END
        WHERE id = $1::uuid
        """
        metrics_json = json.dumps(metrics) if metrics else None
        async with self._pool.acquire() as conn:
            await conn.execute(sql, run_id, status, metrics_json, objective_value, notes)

    async def get_run(self, run_id: str) -> dict[str, Any] | None:
        """Fetch a single calibration run by ID."""
        if self._pool is None:
            return None

        sql = "SELECT * FROM calibration_run WHERE id = $1::uuid"
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(sql, run_id)
            return dict(row) if row else None

    async def list_runs(
        self,
        tenant_id: str,
        field_id: str,
        season_id: str,
        *,
        model_name: str = "crop_growth",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """List recent calibration runs for a field+season."""
        if self._pool is None:
            return []

        sql = """
        SELECT * FROM calibration_run
        WHERE tenant_id = $1 AND field_id = $2 AND season_id = $3 AND model_name = $4
        ORDER BY started_at DESC
        LIMIT $5
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, tenant_id, field_id, season_id, model_name, limit)
            return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # Parameter Sets
    # ------------------------------------------------------------------

    async def create_parameter_set(self, payload: dict[str, Any]) -> str:
        """
        Store a candidate parameter set produced by a calibration run.
        تخزين مجموعة معاملات مرشحة ناتجة عن تشغيل المعايرة.
        """
        if self._pool is None:
            logger.warning("calibration_repo_no_pool", action="create_parameter_set")
            return "no-db"

        sql = """
        INSERT INTO parameter_set
          (tenant_id, field_id, season_id, model_name, model_version,
           parameters, param_uncertainty, prior, posterior_summary,
           created_from_run_id, status)
        VALUES
          ($1, $2, $3, $4, $5,
           $6::jsonb, $7::jsonb, $8::jsonb, $9::jsonb,
           $10::uuid, 'candidate')
        RETURNING id::text
        """
        async with self._pool.acquire() as conn:
            return await conn.fetchval(
                sql,
                payload["tenant_id"],
                payload["field_id"],
                payload["season_id"],
                payload["model_name"],
                payload["model_version"],
                json.dumps(payload.get("parameters", {})),
                json.dumps(payload.get("param_uncertainty", {})),
                json.dumps(payload.get("prior", {})),
                json.dumps(payload.get("posterior_summary", {})),
                payload["created_from_run_id"],
            )

    async def get_active_parameter_set(
        self,
        tenant_id: str,
        field_id: str,
        season_id: str,
        model_name: str = "crop_growth",
    ) -> dict[str, Any] | None:
        """Return the currently active parameter set, if any."""
        if self._pool is None:
            return None

        sql = """
        SELECT * FROM parameter_set
        WHERE tenant_id = $1 AND field_id = $2
          AND season_id = $3 AND model_name = $4
          AND status = 'active'
        """
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(sql, tenant_id, field_id, season_id, model_name)
            return dict(row) if row else None

    async def activate_parameter_set(
        self,
        *,
        tenant_id: str,
        field_id: str,
        season_id: str,
        model_name: str,
        new_set_id: str,
        actor: str,
        reason: str,
    ) -> None:
        """
        Promote a candidate parameter set to active.
        ترقية مجموعة معاملات مرشحة إلى نشطة.

        Within a single transaction:
          1. Deprecate the current active set (if any)
          2. Activate the new set
          3. Write an audit entry to ``parameter_change_log``
        """
        if self._pool is None:
            logger.warning("calibration_repo_no_pool", action="activate_parameter_set")
            return

        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # 1. Find current active (for audit from_parameter_set_id)
                prev_id = await conn.fetchval(
                    """
                    SELECT id::text FROM parameter_set
                    WHERE tenant_id=$1 AND field_id=$2
                      AND season_id=$3 AND model_name=$4 AND status='active'
                    """,
                    tenant_id, field_id, season_id, model_name,
                )

                # 2. Deprecate current
                await conn.execute(
                    """
                    UPDATE parameter_set
                    SET status = 'deprecated', deactivated_at = now()
                    WHERE tenant_id=$1 AND field_id=$2
                      AND season_id=$3 AND model_name=$4 AND status='active'
                    """,
                    tenant_id, field_id, season_id, model_name,
                )

                # 3. Activate new
                await conn.execute(
                    """
                    UPDATE parameter_set
                    SET status = 'active', activated_at = now()
                    WHERE id=$1::uuid AND tenant_id=$2 AND field_id=$3
                      AND season_id=$4 AND model_name=$5
                    """,
                    new_set_id, tenant_id, field_id, season_id, model_name,
                )

                # 4. Audit log
                await conn.execute(
                    """
                    INSERT INTO parameter_change_log
                      (tenant_id, field_id, season_id, model_name,
                       from_parameter_set_id, to_parameter_set_id, actor, reason)
                    VALUES ($1, $2, $3, $4, $5::uuid, $6::uuid, $7, $8)
                    """,
                    tenant_id, field_id, season_id, model_name,
                    prev_id, new_set_id, actor, reason,
                )

        logger.info(
            "parameter_set_activated",
            tenant_id=tenant_id,
            field_id=field_id,
            new_set_id=new_set_id,
            prev_set_id=prev_id,
            actor=actor,
        )

    async def list_parameter_sets(
        self,
        tenant_id: str,
        field_id: str,
        season_id: str,
        *,
        model_name: str = "crop_growth",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """List parameter sets for a field+season (newest first)."""
        if self._pool is None:
            return []

        sql = """
        SELECT * FROM parameter_set
        WHERE tenant_id=$1 AND field_id=$2 AND season_id=$3 AND model_name=$4
        ORDER BY created_at DESC
        LIMIT $5
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(sql, tenant_id, field_id, season_id, model_name, limit)
            return [dict(r) for r in rows]
