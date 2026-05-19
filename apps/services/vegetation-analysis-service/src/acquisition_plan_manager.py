"""
Acquisition Plan Manager
مدير خطة الاستحواذ

Queries CDSE STAC catalog to discover when Sentinel-2 will overfly
each registered field, then stores/updates satellite_acquisition_plan rows.

10-day refresh cycle keeps the look-ahead window 15 days out.
"""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from typing import Any

import asyncpg
import structlog

from .cdse_client import CdseClient

logger = structlog.get_logger(__name__)

# Days ahead to search for planned acquisitions
_LOOKAHEAD_DAYS = 15


class AcquisitionPlanManager:
    def __init__(self, db_pool: asyncpg.Pool, cdse_client: CdseClient) -> None:
        self._pool = db_pool
        self._cdse = cdse_client

    # ------------------------------------------------------------------ #
    # 10-day scheduler job entry point                                     #
    # ------------------------------------------------------------------ #

    async def sync_all_fields(self) -> None:
        """
        Refresh acquisition plan for every registered field.
        Called every 10 days by the scheduler.
        """
        fields = await self._get_all_fields()
        if not fields:
            logger.info("acquisition_plan_sync_no_fields")
            return

        logger.info("acquisition_plan_sync_start", field_count=len(fields))

        # Process in small batches to avoid overwhelming CDSE
        batch_size = 10
        for i in range(0, len(fields), batch_size):
            batch = fields[i : i + batch_size]
            await asyncio.gather(
                *[
                    self._sync_field_plan(
                        row["tenant_id"], row["field_id"], row["bbox"]
                    )
                    for row in batch
                ],
                return_exceptions=True,
            )
            await asyncio.sleep(1)  # gentle rate limiting between batches

        logger.info("acquisition_plan_sync_complete", field_count=len(fields))

    # ------------------------------------------------------------------ #
    # Per-field plan refresh                                               #
    # ------------------------------------------------------------------ #

    async def sync_field_plan(
        self, tenant_id: str, field_id: str, bbox: list[float]
    ) -> None:
        await self._sync_field_plan(tenant_id, field_id, bbox)

    async def _sync_field_plan(
        self, tenant_id: str, field_id: str, bbox: list[float]
    ) -> None:
        today = date.today()
        date_to = today + timedelta(days=_LOOKAHEAD_DAYS)

        try:
            features = await self._cdse.search_scenes(
                bbox=bbox,
                date_from=today,
                date_to=date_to,
                cloud_max=100.0,
            )
        except Exception as exc:
            logger.error(
                "acquisition_plan_search_error",
                field_id=field_id,
                error=str(exc),
            )
            return

        if not features:
            logger.debug("acquisition_plan_no_scenes", field_id=field_id)
            return

        # Upsert planned dates
        planned_dates = {
            self._cdse.scene_date(f)
            for f in features
            if self._cdse.scene_date(f)
        }

        async with self._pool.acquire() as conn:
            for planned_date in planned_dates:
                if planned_date is None:
                    continue
                await conn.execute(
                    """
                    INSERT INTO satellite_acquisition_plan
                        (tenant_id, field_id, planned_date, plan_fetched_at, status)
                    VALUES ($1, $2, $3, NOW(), 'planned')
                    ON CONFLICT (tenant_id, field_id, planned_date)
                    DO UPDATE SET
                        plan_fetched_at = EXCLUDED.plan_fetched_at,
                        status = CASE
                            WHEN satellite_acquisition_plan.status = 'completed' THEN 'completed'
                            ELSE 'planned'
                        END
                    """,
                    tenant_id,
                    field_id,
                    planned_date,
                )

        logger.info(
            "acquisition_plan_updated",
            field_id=field_id,
            dates_planned=len(planned_dates),
        )

    # ------------------------------------------------------------------ #
    # Query helpers for the daily scheduler                                #
    # ------------------------------------------------------------------ #

    async def get_todays_fields(self, today: date) -> list[dict[str, Any]]:
        """
        Return fields that have a 'planned' acquisition for today.
        Each row: {tenant_id, field_id, planned_date}
        """
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT tenant_id::text, field_id::text, planned_date
                FROM satellite_acquisition_plan
                WHERE planned_date = $1
                  AND status = 'planned'
                """,
                today,
            )
        return [dict(r) for r in rows]

    async def get_retry_fields(self, today: date) -> list[dict[str, Any]]:
        """
        Fields still in 'planned' state for today — need retry.
        """
        return await self.get_todays_fields(today)

    async def mark_completed(
        self, tenant_id: str, field_id: str, planned_date: date
    ) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE satellite_acquisition_plan
                SET status = 'completed'
                WHERE tenant_id = $1 AND field_id = $2 AND planned_date = $3
                """,
                tenant_id,
                field_id,
                planned_date,
            )

    async def mark_missed(
        self, tenant_id: str, field_id: str, planned_date: date
    ) -> None:
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE satellite_acquisition_plan
                SET status = 'missed'
                WHERE tenant_id = $1 AND field_id = $2 AND planned_date = $3
                """,
                tenant_id,
                field_id,
                planned_date,
            )

    # ------------------------------------------------------------------ #
    # Internal: load all registered fields from satellite_field_data       #
    # (fields appear here after their first successful data insert)        #
    # ------------------------------------------------------------------ #

    async def _get_all_fields(self) -> list[dict[str, Any]]:
        """
        Returns distinct (tenant_id, field_id, bbox) rows.

        bbox is stored as a JSONB array [min_lon, min_lat, max_lon, max_lat]
        in the satellite_field_data.stac_metadata->>'bbox' column.
        Falls back to a dedicated field_bboxes table if it exists.
        """
        async with self._pool.acquire() as conn:
            # Try the dedicated bbox registry first (populated by backfill / scheduler)
            try:
                rows = await conn.fetch(
                    """
                    SELECT DISTINCT
                        tenant_id::text,
                        field_id::text,
                        (stac_metadata->'bbox') AS bbox_json
                    FROM satellite_field_data
                    WHERE stac_metadata ? 'bbox'
                    """
                )
            except Exception:
                return []

        result = []
        for row in rows:
            import json

            bbox_raw = row["bbox_json"]
            if isinstance(bbox_raw, str):
                try:
                    bbox = json.loads(bbox_raw)
                except Exception:
                    continue
            else:
                bbox = bbox_raw  # asyncpg may return list directly for JSONB

            if isinstance(bbox, list) and len(bbox) == 4:
                result.append(
                    {
                        "tenant_id": row["tenant_id"],
                        "field_id": row["field_id"],
                        "bbox": [float(v) for v in bbox],
                    }
                )

        return result
