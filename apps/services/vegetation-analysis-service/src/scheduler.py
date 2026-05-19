"""
Satellite Acquisition Scheduler
مجدول الاستحواذ على صور الأقمار الصناعية

Three scheduled jobs:
  1. sync_acquisition_plan   — every 10 days at 01:00 AM
     Queries CDSE STAC for next 15 days per field, updates satellite_acquisition_plan.

  2. daily_imagery_update    — every day at 00:00 AM
     Downloads + processes indices for fields scheduled today.
     Marks 'retry_pending' if CDSE data not yet available.

  3. retry_missed_job        — at 06:00 and 12:00 daily
     Retries fields still in 'planned' state for today.
     After 12:00 attempt, marks remaining as 'missed'.

NATS subscriber:
  sahool.field.created → triggers async 12-month backfill for new field.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date
from typing import Any

import asyncpg
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .acquisition_plan_manager import AcquisitionPlanManager
from .backfill import backfill_field, bbox_from_geometry_wkt
from .cdse_client import CdseClient
from .index_processor import IndexProcessor
from .satellite_storage import SatelliteStorage

logger = structlog.get_logger(__name__)


class SatelliteScheduler:
    """
    Owns the APScheduler instance and NATS subscription for satellite jobs.
    Instantiate once in main.py lifespan; call start() / stop().
    """

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        cdse_client: CdseClient,
        minio_client: Any | None,
        nats_conn: Any | None,
        bucket_name: str = "sahool-satellite",
    ) -> None:
        self._pool = db_pool
        self._cdse = cdse_client
        self._nats = nats_conn

        self._storage = SatelliteStorage(db_pool, minio_client, bucket_name)
        self._processor = IndexProcessor()
        self._plan_mgr = AcquisitionPlanManager(db_pool, cdse_client)

        self._scheduler = AsyncIOScheduler()
        self._nats_sub = None

    # ------------------------------------------------------------------ #
    # Lifecycle                                                            #
    # ------------------------------------------------------------------ #

    async def start(self) -> None:
        self._register_jobs()
        self._scheduler.start()
        logger.info("satellite_scheduler_started")

        if self._nats:
            await self._subscribe_field_created()

    async def stop(self) -> None:
        self._scheduler.shutdown(wait=False)
        if self._nats_sub:
            try:
                await self._nats_sub.unsubscribe()
            except Exception:
                pass
        logger.info("satellite_scheduler_stopped")

    # ------------------------------------------------------------------ #
    # Job registration                                                     #
    # ------------------------------------------------------------------ #

    def _register_jobs(self) -> None:
        # Job 1: sync acquisition plan every 10 days at 01:00 AM
        self._scheduler.add_job(
            self._job_sync_acquisition_plan,
            CronTrigger(day="*/10", hour=1, minute=0),
            id="sync_acquisition_plan",
            name="Sync CDSE acquisition plan (every 10 days)",
            replace_existing=True,
            misfire_grace_time=3600,
        )

        # Job 2: daily imagery update at 00:00 AM
        self._scheduler.add_job(
            self._job_daily_imagery_update,
            CronTrigger(hour=0, minute=0),
            id="daily_imagery_update",
            name="Daily satellite imagery download",
            replace_existing=True,
            misfire_grace_time=3600,
        )

        # Job 3: retry at 06:00 and 12:00
        self._scheduler.add_job(
            self._job_retry_missed,
            CronTrigger(hour="6,12", minute=0),
            id="retry_missed",
            name="Retry missing satellite imagery (06:00 and 12:00)",
            replace_existing=True,
            misfire_grace_time=1800,
        )

        logger.info("satellite_scheduler_jobs_registered", job_count=3)

    # ------------------------------------------------------------------ #
    # Job implementations                                                  #
    # ------------------------------------------------------------------ #

    async def _job_sync_acquisition_plan(self) -> None:
        logger.info("job_sync_acquisition_plan_start")
        try:
            await self._plan_mgr.sync_all_fields()
        except Exception as exc:
            logger.error("job_sync_acquisition_plan_error", error=str(exc))
        logger.info("job_sync_acquisition_plan_done")

    async def _job_daily_imagery_update(self) -> None:
        today = date.today()
        logger.info("job_daily_imagery_start", date=str(today))

        try:
            fields = await self._plan_mgr.get_todays_fields(today)
        except Exception as exc:
            logger.error("job_daily_imagery_get_fields_error", error=str(exc))
            return

        if not fields:
            logger.info("job_daily_imagery_no_fields_today", date=str(today))
            return

        logger.info("job_daily_imagery_fields", count=len(fields), date=str(today))

        for row in fields:
            await self._process_field_for_date(
                tenant_id=row["tenant_id"],
                field_id=row["field_id"],
                acq_date=today,
                is_last_retry=False,
            )

        logger.info("job_daily_imagery_done", date=str(today))

    async def _job_retry_missed(self) -> None:
        from datetime import datetime

        today = date.today()
        current_hour = datetime.now().hour
        is_last_retry = current_hour >= 12  # 12:00 PM is the final attempt

        logger.info(
            "job_retry_missed_start",
            date=str(today),
            is_last_retry=is_last_retry,
        )

        try:
            fields = await self._plan_mgr.get_retry_fields(today)
        except Exception as exc:
            logger.error("job_retry_get_fields_error", error=str(exc))
            return

        if not fields:
            logger.info("job_retry_no_pending_fields", date=str(today))
            return

        for row in fields:
            await self._process_field_for_date(
                tenant_id=row["tenant_id"],
                field_id=row["field_id"],
                acq_date=today,
                is_last_retry=is_last_retry,
            )

        logger.info("job_retry_done", date=str(today), fields_retried=len(fields))

    # ------------------------------------------------------------------ #
    # Core per-field processing                                            #
    # ------------------------------------------------------------------ #

    async def _process_field_for_date(
        self,
        tenant_id: str,
        field_id: str,
        acq_date: date,
        is_last_retry: bool,
    ) -> None:
        # Skip if already done
        try:
            if await self._storage.has_data_for_date(tenant_id, field_id, acq_date):
                await self._plan_mgr.mark_completed(tenant_id, field_id, acq_date)
                return
        except Exception:
            pass

        # Retrieve bbox from existing satellite data for this field
        bbox = await self._get_field_bbox(tenant_id, field_id)
        if not bbox:
            logger.warning("field_bbox_not_found", field_id=field_id)
            if is_last_retry:
                await self._plan_mgr.mark_missed(tenant_id, field_id, acq_date)
            return

        # Download
        tiff_bytes = await self._cdse.download_bands(
            bbox=bbox,
            acquisition_date=acq_date,
        )

        if tiff_bytes is None:
            if is_last_retry:
                await self._plan_mgr.mark_missed(tenant_id, field_id, acq_date)
                logger.warning(
                    "satellite_imagery_missed",
                    field_id=field_id,
                    date=str(acq_date),
                )
            return

        # Process
        result = self._processor.process(
            field_id=field_id,
            tenant_id=tenant_id,
            acquisition_date=acq_date,
            tiff_bytes=tiff_bytes,
        )
        if result is None:
            if is_last_retry:
                await self._plan_mgr.mark_missed(tenant_id, field_id, acq_date)
            return

        # Store
        try:
            await self._storage.save_field_data(
                tenant_id=tenant_id,
                field_id=field_id,
                acquisition_date=acq_date,
                stats=result.to_dict(),
                geotiff_bytes=result.geotiff_bytes,
                png_bytes=result.png_bytes,
                stac_metadata=None,
                bbox=bbox,
            )
            await self._plan_mgr.mark_completed(tenant_id, field_id, acq_date)
            logger.info(
                "satellite_imagery_stored",
                field_id=field_id,
                date=str(acq_date),
                ndvi_mean=result.ndvi.mean,
            )
        except Exception as exc:
            logger.error(
                "satellite_store_error",
                field_id=field_id,
                date=str(acq_date),
                error=str(exc),
            )

    # ------------------------------------------------------------------ #
    # NATS: sahool.field.created → backfill                               #
    # ------------------------------------------------------------------ #

    async def _subscribe_field_created(self) -> None:
        try:
            self._nats_sub = await self._nats.subscribe(
                "sahool.field.created",
                cb=self._handle_field_created,
            )
            logger.info("nats_subscribed", subject="sahool.field.created")
        except Exception as exc:
            logger.error("nats_subscribe_error", subject="sahool.field.created", error=str(exc))

    async def _handle_field_created(self, msg: Any) -> None:
        try:
            payload = json.loads(msg.data.decode())
            field_id = payload.get("field_id") or payload.get("fieldId")
            tenant_id = payload.get("tenant_id") or payload.get("tenantId")
            geometry_wkt = payload.get("geometry_wkt") or payload.get("geometryWkt")

            if not field_id or not tenant_id:
                logger.warning("field_created_missing_ids", payload=payload)
                return

            bbox: list[float] | None = None
            if geometry_wkt:
                bbox = bbox_from_geometry_wkt(geometry_wkt)

            if not bbox:
                logger.warning(
                    "field_created_no_bbox",
                    field_id=field_id,
                    geometry_wkt=geometry_wkt,
                )
                return

            logger.info(
                "field_created_backfill_triggered",
                field_id=field_id,
                tenant_id=tenant_id,
                bbox=bbox,
            )

            # Fire and forget — non-blocking
            asyncio.create_task(
                backfill_field(
                    tenant_id=tenant_id,
                    field_id=field_id,
                    bbox=bbox,
                    cdse_client=self._cdse,
                    index_processor=self._processor,
                    satellite_storage=self._storage,
                    acquisition_plan_manager=self._plan_mgr,
                )
            )

        except Exception as exc:
            logger.error("field_created_handler_error", error=str(exc))

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    async def _get_field_bbox(
        self, tenant_id: str, field_id: str
    ) -> list[float] | None:
        """Retrieve bbox from existing satellite_field_data stac_metadata."""
        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT stac_metadata->'bbox' AS bbox
                    FROM satellite_field_data
                    WHERE tenant_id = $1 AND field_id = $2
                      AND stac_metadata ? 'bbox'
                    LIMIT 1
                    """,
                    tenant_id,
                    field_id,
                )
            if row and row["bbox"]:
                raw = row["bbox"]
                if isinstance(raw, str):
                    raw = json.loads(raw)
                if isinstance(raw, list) and len(raw) == 4:
                    return [float(v) for v in raw]
        except Exception as exc:
            logger.warning("get_field_bbox_error", field_id=field_id, error=str(exc))
        return None
