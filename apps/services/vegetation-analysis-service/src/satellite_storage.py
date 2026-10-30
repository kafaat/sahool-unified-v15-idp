"""
Satellite Storage
تخزين البيانات الساتلية

DB CRUD for satellite_field_data + MinIO object store for GeoTIFF / PNG.

MinIO paths:
  satellite/{tenant_id}/{field_id}/{YYYY-MM-DD}/ndvi.tif
  satellite/{tenant_id}/{field_id}/{YYYY-MM-DD}/thumbnail.png
"""

from __future__ import annotations

import io
import json
from datetime import date
from typing import Any

import asyncpg
import structlog

logger = structlog.get_logger(__name__)


class SatelliteStorage:
    def __init__(
        self,
        db_pool: asyncpg.Pool,
        minio_client: Any | None,  # boto3 S3 client or None
        bucket_name: str = "sahool-satellite",
    ) -> None:
        self._pool = db_pool
        self._minio = minio_client
        self._bucket = bucket_name

    # ------------------------------------------------------------------ #
    # Write                                                                #
    # ------------------------------------------------------------------ #

    async def save_field_data(
        self,
        tenant_id: str,
        field_id: str,
        acquisition_date: date,
        stats: dict[str, Any],
        geotiff_bytes: bytes | None,
        png_bytes: bytes | None,
        stac_metadata: dict | None,
        bbox: list[float] | None = None,
    ) -> None:
        """
        Upload assets to MinIO (if available) then upsert index stats into DB.
        Skips asset upload silently if MinIO is not configured.
        """
        date_str = acquisition_date.isoformat()
        geotiff_url: str | None = None
        png_url: str | None = None

        # Upload to MinIO
        if self._minio and geotiff_bytes:
            geotiff_url = await self._upload(tenant_id, field_id, date_str, "ndvi.tif", geotiff_bytes, "image/tiff")
        if self._minio and png_bytes:
            png_url = await self._upload(tenant_id, field_id, date_str, "thumbnail.png", png_bytes, "image/png")

        # Embed bbox into stac_metadata so acquisition_plan_manager can find it
        meta = stac_metadata or {}
        if bbox and "bbox" not in meta:
            meta["bbox"] = bbox

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO satellite_field_data (
                    tenant_id, field_id, acquisition_date, satellite,
                    cloud_cover_percent,
                    ndvi_mean, ndvi_min, ndvi_max, ndvi_std,
                    evi_mean,  evi_min,  evi_max,  evi_std,
                    lai_mean,  lai_min,  lai_max,  lai_std,
                    ndwi_mean, ndwi_min, ndwi_max, ndwi_std,
                    geotiff_url, png_url, stac_metadata, processing_status
                ) VALUES (
                    $1, $2, $3, 'sentinel-2-l2a',
                    $4,
                    $5, $6, $7, $8,
                    $9, $10, $11, $12,
                    $13, $14, $15, $16,
                    $17, $18, $19, $20,
                    $21, $22, $23, 'completed'
                )
                ON CONFLICT (tenant_id, field_id, acquisition_date)
                DO UPDATE SET
                    cloud_cover_percent = EXCLUDED.cloud_cover_percent,
                    ndvi_mean = EXCLUDED.ndvi_mean, ndvi_min = EXCLUDED.ndvi_min,
                    ndvi_max  = EXCLUDED.ndvi_max,  ndvi_std = EXCLUDED.ndvi_std,
                    evi_mean  = EXCLUDED.evi_mean,  evi_min  = EXCLUDED.evi_min,
                    evi_max   = EXCLUDED.evi_max,   evi_std  = EXCLUDED.evi_std,
                    lai_mean  = EXCLUDED.lai_mean,  lai_min  = EXCLUDED.lai_min,
                    lai_max   = EXCLUDED.lai_max,   lai_std  = EXCLUDED.lai_std,
                    ndwi_mean = EXCLUDED.ndwi_mean, ndwi_min = EXCLUDED.ndwi_min,
                    ndwi_max  = EXCLUDED.ndwi_max,  ndwi_std = EXCLUDED.ndwi_std,
                    geotiff_url = COALESCE(EXCLUDED.geotiff_url, satellite_field_data.geotiff_url),
                    png_url     = COALESCE(EXCLUDED.png_url,     satellite_field_data.png_url),
                    stac_metadata = EXCLUDED.stac_metadata,
                    processing_status = 'completed'
                """,
                tenant_id,
                field_id,
                acquisition_date,
                stats.get("cloud_cover_percent"),
                stats.get("ndvi_mean"),
                stats.get("ndvi_min"),
                stats.get("ndvi_max"),
                stats.get("ndvi_std"),
                stats.get("evi_mean"),
                stats.get("evi_min"),
                stats.get("evi_max"),
                stats.get("evi_std"),
                stats.get("lai_mean"),
                stats.get("lai_min"),
                stats.get("lai_max"),
                stats.get("lai_std"),
                stats.get("ndwi_mean"),
                stats.get("ndwi_min"),
                stats.get("ndwi_max"),
                stats.get("ndwi_std"),
                geotiff_url,
                png_url,
                json.dumps(meta) if meta else None,
            )

        logger.info(
            "satellite_data_saved",
            tenant_id=tenant_id,
            field_id=field_id,
            date=date_str,
            ndvi_mean=stats.get("ndvi_mean"),
        )

    # ------------------------------------------------------------------ #
    # Read                                                                 #
    # ------------------------------------------------------------------ #

    async def get_timeseries(
        self,
        tenant_id: str,
        field_id: str,
        index_type: str = "ndvi",
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[dict[str, Any]]:
        """
        Return time-series rows for a field, ordered by acquisition_date ASC.
        index_type: ndvi | evi | lai | ndwi  (controls which mean/min/max columns)
        Returns only dates that have actual data (no empty rows).
        """
        idx = index_type.lower()
        if idx not in ("ndvi", "evi", "lai", "ndwi"):
            idx = "ndvi"

        clauses = ["tenant_id = $1", "field_id = $2", "processing_status = 'completed'"]
        params: list[Any] = [tenant_id, field_id]

        if date_from:
            params.append(date_from)
            clauses.append(f"acquisition_date >= ${len(params)}")
        if date_to:
            params.append(date_to)
            clauses.append(f"acquisition_date <= ${len(params)}")

        where = " AND ".join(clauses)
        query = f"""
            SELECT
                acquisition_date,
                cloud_cover_percent,
                {idx}_mean AS index_mean,
                {idx}_min  AS index_min,
                {idx}_max  AS index_max,
                {idx}_std  AS index_std,
                ndvi_mean, evi_mean, lai_mean, ndwi_mean,
                geotiff_url, png_url
            FROM satellite_field_data
            WHERE {where}
            ORDER BY acquisition_date ASC
        """

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [
            {
                "date": r["acquisition_date"].isoformat(),
                "cloud_cover": r["cloud_cover_percent"],
                "value": r["index_mean"],
                "min": r["index_min"],
                "max": r["index_max"],
                "std": r["index_std"],
                "ndvi_mean": r["ndvi_mean"],
                "evi_mean": r["evi_mean"],
                "lai_mean": r["lai_mean"],
                "ndwi_mean": r["ndwi_mean"],
                "thumbnail_url": r["png_url"],
            }
            for r in rows
        ]

    async def has_data_for_date(self, tenant_id: str, field_id: str, acquisition_date: date) -> bool:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 1 FROM satellite_field_data
                WHERE tenant_id = $1 AND field_id = $2 AND acquisition_date = $3
                """,
                tenant_id,
                field_id,
                acquisition_date,
            )
        return row is not None

    async def get_acquisition_plan(
        self,
        tenant_id: str,
        field_id: str,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[dict[str, Any]]:
        clauses = ["tenant_id = $1", "field_id = $2"]
        params: list[Any] = [tenant_id, field_id]

        if date_from:
            params.append(date_from)
            clauses.append(f"planned_date >= ${len(params)}")
        if date_to:
            params.append(date_to)
            clauses.append(f"planned_date <= ${len(params)}")

        where = " AND ".join(clauses)
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                f"""
                SELECT planned_date, status, plan_fetched_at
                FROM satellite_acquisition_plan
                WHERE {where}
                ORDER BY planned_date ASC
                """,
                *params,
            )
        return [
            {
                "date": r["planned_date"].isoformat(),
                "status": r["status"],
                "plan_fetched_at": r["plan_fetched_at"].isoformat(),
            }
            for r in rows
        ]

    # ------------------------------------------------------------------ #
    # MinIO upload helper                                                  #
    # ------------------------------------------------------------------ #

    async def _upload(
        self,
        tenant_id: str,
        field_id: str,
        date_str: str,
        filename: str,
        data: bytes,
        content_type: str,
    ) -> str | None:
        key = f"satellite/{tenant_id}/{field_id}/{date_str}/{filename}"
        try:
            import asyncio

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._minio.put_object(
                    Bucket=self._bucket,
                    Key=key,
                    Body=io.BytesIO(data),
                    ContentLength=len(data),
                    ContentType=content_type,
                ),
            )
            endpoint = getattr(self._minio, "_endpoint_url", "")
            return f"{endpoint}/{self._bucket}/{key}"
        except Exception as exc:
            logger.warning("minio_upload_error", key=key, error=str(exc))
            return None
