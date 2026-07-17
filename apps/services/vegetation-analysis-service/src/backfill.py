"""
Field Backfill
ملء البيانات التاريخية للحقل

When a new field is created (NATS sahool.field.created), this module
fetches all Sentinel-2 L2A scenes from the past 12 months and stores
index statistics for each available acquisition date.

Rate-limiting: 1-second sleep between scene downloads to respect CDSE limits.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date, timedelta
from typing import Any

import structlog

from .acquisition_plan_manager import AcquisitionPlanManager
from .cdse_client import CdseClient
from .index_processor import IndexProcessor
from .satellite_storage import SatelliteStorage

logger = structlog.get_logger(__name__)

_BACKFILL_MONTHS = 12
_RATE_LIMIT_SLEEP = 1.0  # seconds between downloads


async def backfill_field(
    tenant_id: str,
    field_id: str,
    bbox: list[float],
    cdse_client: CdseClient,
    index_processor: IndexProcessor,
    satellite_storage: SatelliteStorage,
    acquisition_plan_manager: AcquisitionPlanManager | None = None,
) -> None:
    """
    Fetch and store all Sentinel-2 scenes for the past 12 months.

    Skips dates that already have data in satellite_field_data.
    Logs progress every 10 scenes.
    """
    today = date.today()
    date_from = today - timedelta(days=_BACKFILL_MONTHS * 30)

    logger.info(
        "backfill_start",
        field_id=field_id,
        tenant_id=tenant_id,
        date_from=str(date_from),
        date_to=str(today),
    )

    # Discover all scenes in the 12-month window
    try:
        features = await cdse_client.search_scenes(
            bbox=bbox,
            date_from=date_from,
            date_to=today,
            cloud_max=100.0,
        )
    except Exception as exc:
        logger.error("backfill_search_error", field_id=field_id, error=str(exc))
        return

    if not features:
        logger.info("backfill_no_scenes", field_id=field_id)
        return

    # Group by acquisition date (keep the scene with lowest cloud cover per day)
    by_date: dict[date, dict] = {}
    for feat in features:
        acq_date = cdse_client.scene_date(feat)
        if acq_date is None:
            continue
        existing = by_date.get(acq_date)
        if existing is None or cdse_client.scene_cloud_cover(feat) < cdse_client.scene_cloud_cover(existing):
            by_date[acq_date] = feat

    sorted_dates = sorted(by_date.keys())
    total = len(sorted_dates)
    logger.info("backfill_scenes_discovered", field_id=field_id, scene_count=total)

    processed = 0
    skipped = 0

    for i, acq_date in enumerate(sorted_dates):
        # Skip if already stored
        try:
            has_data = await satellite_storage.has_data_for_date(tenant_id, field_id, acq_date)
        except Exception:
            has_data = False

        if has_data:
            skipped += 1
            continue

        feature = by_date[acq_date]

        # Download band data
        try:
            tiff_bytes = await cdse_client.download_bands(
                bbox=bbox,
                acquisition_date=acq_date,
            )
        except Exception as exc:
            logger.warning(
                "backfill_download_error",
                field_id=field_id,
                date=str(acq_date),
                error=str(exc),
            )
            await asyncio.sleep(_RATE_LIMIT_SLEEP)
            continue

        if tiff_bytes is None:
            await asyncio.sleep(_RATE_LIMIT_SLEEP)
            continue

        # Compute indices
        result = index_processor.process(
            field_id=field_id,
            tenant_id=tenant_id,
            acquisition_date=acq_date,
            tiff_bytes=tiff_bytes,
        )

        if result is None:
            logger.warning("backfill_process_error", field_id=field_id, date=str(acq_date))
            await asyncio.sleep(_RATE_LIMIT_SLEEP)
            continue

        # Store
        try:
            await satellite_storage.save_field_data(
                tenant_id=tenant_id,
                field_id=field_id,
                acquisition_date=acq_date,
                stats=result.to_dict(),
                geotiff_bytes=result.geotiff_bytes,
                png_bytes=result.png_bytes,
                stac_metadata=feature,
                bbox=bbox,
            )

            # Also register this date in the acquisition plan as completed
            if acquisition_plan_manager:
                await acquisition_plan_manager.mark_completed(tenant_id, field_id, acq_date)
        except Exception as exc:
            logger.error(
                "backfill_store_error",
                field_id=field_id,
                date=str(acq_date),
                error=str(exc),
            )

        processed += 1

        if processed % 10 == 0:
            logger.info(
                "backfill_progress",
                field_id=field_id,
                processed=processed,
                total=total,
                skipped=skipped,
            )

        # Rate limit between downloads
        await asyncio.sleep(_RATE_LIMIT_SLEEP)

    logger.info(
        "backfill_complete",
        field_id=field_id,
        tenant_id=tenant_id,
        processed=processed,
        skipped=skipped,
        total=total,
    )


def bbox_from_geometry_wkt(geometry_wkt: str) -> list[float] | None:
    """
    Extract bounding box [min_lon, min_lat, max_lon, max_lat] from WKT polygon.
    Handles: POLYGON((lon lat, ...))
    Returns None if parsing fails.
    """
    try:
        # Strip prefix and parentheses
        inner = geometry_wkt.strip()
        if inner.upper().startswith("POLYGON"):
            inner = inner[inner.index("(") + 1 :].rstrip(")")
            inner = inner.strip("()")
        coords_str = inner.split(",")
        lons, lats = [], []
        for pair in coords_str:
            parts = pair.strip().split()
            if len(parts) >= 2:
                lons.append(float(parts[0]))
                lats.append(float(parts[1]))
        if not lons:
            return None
        return [min(lons), min(lats), max(lons), max(lats)]
    except Exception:
        return None
