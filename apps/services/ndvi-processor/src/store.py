"""
SAHOOL NDVI Processor – Persistence Store
==========================================
Replaces the pure in-memory dicts from processing.py with a store that:

  • Writes NDVI results to Postgres (asyncpg pool) when a pool is available.
  • Falls back silently to in-memory dicts when DB is not configured (dev/test).
  • Publishes a NATS event (sahool.satellite.ndvi.computed) and a Digital-Twin
    observation event (sahool.field.observation.ingested.v1) after each result
    is persisted, so the assimilation pipeline can consume it.

The three in-memory dicts (_jobs / _results / _composites) are still exported
so that processing.py can import them directly — the old code paths continue
to work without modification during a gradual migration.

Environment variables
---------------------
DATABASE_URL   – asyncpg-compatible Postgres URL (optional)
NATS_URL       – nats:// URL (optional)
"""

from __future__ import annotations

import dataclasses
import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# ── Shared in-memory stores (same objects as before, re-exported) ──────────
_jobs: dict[str, dict] = {}
_results: dict[str, list[dict]] = {}   # field_id -> [NDVIResult dict]
_composites: dict[str, dict] = {}      # composite_id -> composite dict

# ── Runtime configuration (injected by main.py on startup) ─────────────────


@dataclasses.dataclass
class _StoreConfig:
    """Encapsulates live DB/NATS connections so they can be swapped atomically."""
    db_pool: object = None    # asyncpg.Pool | None
    nats_client: object = None  # nats.aio.client.Client | None


_cfg = _StoreConfig()


def configure(db_pool=None, nats_client=None) -> None:
    """
    Called once during application startup to inject live DB/NATS connections.
    Both arguments are optional; omitting them keeps the in-memory fallback.
    """
    _cfg.db_pool = db_pool
    _cfg.nats_client = nats_client
    if db_pool:
        logger.info("NDVIStore: DB pool connected – results will be persisted")
    if nats_client:
        logger.info("NDVIStore: NATS client connected – events will be published")


# ── Result persistence ──────────────────────────────────────────────────────

async def save_result(field_id: str, tenant_id: str, result_dict: dict) -> None:
    """
    Persist an NDVIResult to:
      1. In-memory cache (always).
      2. Postgres table ``ndvi_result`` (when DB pool is set).
      3. NATS events (when NATS client is set).
    """
    # 1. In-memory
    if field_id not in _results:
        _results[field_id] = []
    _results[field_id].append(result_dict)

    # 2. Postgres
    if _cfg.db_pool is not None:
        try:
            await _cfg.db_pool.execute(
                """
                INSERT INTO ndvi_result (
                    id, tenant_id, field_id, acquisition_date,
                    ndvi_mean, ndvi_min, ndvi_max, ndvi_std,
                    cloud_cover_percent, valid_pixels_percent,
                    satellite, resolution_meters,
                    geotiff_url, png_url, thumbnail_url,
                    quality, raw_payload, created_at
                ) VALUES (
                    $1, $2, $3, $4,
                    $5, $6, $7, $8,
                    $9, $10,
                    $11, $12,
                    $13, $14, $15,
                    $16, $17, now()
                )
                ON CONFLICT (tenant_id, field_id, acquisition_date) DO UPDATE
                    SET ndvi_mean = EXCLUDED.ndvi_mean,
                        ndvi_min  = EXCLUDED.ndvi_min,
                        ndvi_max  = EXCLUDED.ndvi_max,
                        raw_payload = EXCLUDED.raw_payload,
                        created_at  = now()
                """,
                result_dict.get("id"),
                tenant_id,
                field_id,
                result_dict.get("date"),
                result_dict["statistics"]["mean"],
                result_dict["statistics"]["min"],
                result_dict["statistics"]["max"],
                result_dict["statistics"]["std"],
                result_dict["quality"]["cloud_cover_percent"],
                result_dict["quality"]["valid_pixels_percent"],
                result_dict["source"]["satellite"],
                result_dict["source"]["resolution_meters"],
                result_dict.get("files", {}).get("geotiff"),
                result_dict.get("files", {}).get("png"),
                result_dict.get("files", {}).get("thumbnail"),
                result_dict["quality"]["valid_pixels_percent"] / 100.0,
                json.dumps(result_dict),
            )
        except Exception:
            logger.exception("NDVIStore: failed to persist result to DB (field=%s)", field_id)

    # 3. NATS events
    if _cfg.nats_client is not None:
        await _publish_ndvi_events(field_id, tenant_id, result_dict)


async def _publish_ndvi_events(
    field_id: str, tenant_id: str, result_dict: dict
) -> None:
    """Publish sahool.satellite.ndvi.computed and sahool.field.observation.ingested.v1."""
    now = datetime.now(UTC).isoformat()
    ndvi_mean = result_dict["statistics"]["mean"]

    # ── sahool.satellite.ndvi.computed ──────────────────────────────────────
    computed_payload = json.dumps({
        "schema_version": "1.0",
        "event_type": "ndvi.computed",
        "correlation_id": result_dict.get("id"),
        "tenant_id": tenant_id,
        "field_id": field_id,
        "date": result_dict.get("date"),
        "ndvi_mean": ndvi_mean,
        "ndvi_min": result_dict["statistics"]["min"],
        "ndvi_max": result_dict["statistics"]["max"],
        "cloud_cover_percent": result_dict["quality"]["cloud_cover_percent"],
        "satellite": result_dict["source"]["satellite"],
        "produced_at": now,
    }).encode()

    try:
        await _cfg.nats_client.publish("sahool.satellite.ndvi.computed", computed_payload)
    except Exception:
        logger.warning("NDVIStore: failed to publish ndvi.computed event")

    # ── sahool.field.observation.ingested.v1 ────────────────────────────────
    obs_payload = json.dumps({
        "schema_version": "1.0",
        "event_type": "field.observation.ingested",
        "tenant_id": tenant_id,
        "field_id": field_id,
        "ts": result_dict.get("processing", {}).get("processed_at", now),
        "source": "sentinel",
        "obs_type": "ndvi",
        "value": ndvi_mean,
        "quality": result_dict["quality"]["valid_pixels_percent"] / 100.0,
        "meta": {
            "satellite": result_dict["source"]["satellite"],
            "scene_id": result_dict["source"]["scene_id"],
            "cloud_cover_percent": result_dict["quality"]["cloud_cover_percent"],
        },
        "produced_at": now,
    }).encode()

    try:
        await _cfg.nats_client.publish(
            "sahool.field.observation.ingested.v1", obs_payload
        )
    except Exception:
        logger.warning("NDVIStore: failed to publish observation.ingested event")


# ── Composite persistence ───────────────────────────────────────────────────

async def save_composite(composite_id: str, tenant_id: str, composite_dict: dict) -> None:
    """Persist a monthly composite (in-memory + DB)."""
    _composites[composite_id] = composite_dict

    if _cfg.db_pool is not None:
        try:
            await _cfg.db_pool.execute(
                """
                INSERT INTO ndvi_composite (
                    composite_id, tenant_id, field_id, year, month,
                    composite_method, satellite,
                    ndvi_mean, ndvi_min, ndvi_max, ndvi_std,
                    images_used, geotiff_url, png_url, thumbnail_url,
                    raw_payload, created_at
                ) VALUES (
                    $1, $2, $3, $4, $5,
                    $6, $7,
                    $8, $9, $10, $11,
                    $12, $13, $14, $15,
                    $16, now()
                )
                ON CONFLICT (tenant_id, field_id, year, month) DO UPDATE
                    SET ndvi_mean = EXCLUDED.ndvi_mean,
                        raw_payload = EXCLUDED.raw_payload,
                        created_at  = now()
                """,
                composite_id,
                tenant_id,
                composite_dict.get("field_id"),
                composite_dict.get("year"),
                composite_dict.get("month"),
                composite_dict.get("method"),
                composite_dict.get("source"),
                composite_dict["statistics"]["mean"],
                composite_dict["statistics"]["min"],
                composite_dict["statistics"]["max"],
                composite_dict["statistics"]["std"],
                composite_dict.get("images_used", 0),
                composite_dict.get("files", {}).get("geotiff"),
                composite_dict.get("files", {}).get("png"),
                composite_dict.get("files", {}).get("thumbnail"),
                json.dumps(composite_dict),
            )
        except Exception:
            logger.exception(
                "NDVIStore: failed to persist composite to DB (id=%s)", composite_id
            )


# ── DB table creation helper (run once at startup if tables missing) ────────

_CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS ndvi_result (
    id                    text           NOT NULL,
    tenant_id             uuid           NOT NULL,
    field_id              text           NOT NULL,
    acquisition_date      date           NOT NULL,
    ndvi_mean             double precision NOT NULL,
    ndvi_min              double precision NOT NULL,
    ndvi_max              double precision NOT NULL,
    ndvi_std              double precision NOT NULL DEFAULT 0,
    cloud_cover_percent   double precision NOT NULL DEFAULT 0,
    valid_pixels_percent  double precision NOT NULL DEFAULT 100,
    satellite             text           NOT NULL,
    resolution_meters     int            NOT NULL DEFAULT 10,
    geotiff_url           text,
    png_url               text,
    thumbnail_url         text,
    quality               double precision NOT NULL DEFAULT 1.0,
    raw_payload           jsonb,
    created_at            timestamptz    NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, field_id, acquisition_date)
);
CREATE INDEX IF NOT EXISTS idx_ndvi_result_field_date
    ON ndvi_result (tenant_id, field_id, acquisition_date DESC);

CREATE TABLE IF NOT EXISTS ndvi_composite (
    composite_id    text           NOT NULL,
    tenant_id       uuid           NOT NULL,
    field_id        text           NOT NULL,
    year            int            NOT NULL,
    month           int            NOT NULL,
    composite_method text          NOT NULL,
    satellite       text           NOT NULL,
    ndvi_mean       double precision NOT NULL,
    ndvi_min        double precision NOT NULL,
    ndvi_max        double precision NOT NULL,
    ndvi_std        double precision NOT NULL DEFAULT 0,
    images_used     int            NOT NULL DEFAULT 0,
    geotiff_url     text,
    png_url         text,
    thumbnail_url   text,
    raw_payload     jsonb,
    created_at      timestamptz    NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, field_id, year, month)
);
"""


async def ensure_tables(db_pool) -> None:
    """Create ndvi_result and ndvi_composite tables if they do not yet exist."""
    try:
        await db_pool.execute(_CREATE_TABLES_SQL)
        logger.info("NDVIStore: DB tables verified/created")
    except Exception:
        logger.exception("NDVIStore: could not create DB tables – continuing without persistence")
