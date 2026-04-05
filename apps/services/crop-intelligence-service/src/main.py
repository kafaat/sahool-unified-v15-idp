"""
SAHOOL Crop Intelligence Service
خدمة ذكاء المحاصيل - تشخيص ذكي للحقول الزراعية
Port: 8095
"""

from __future__ import annotations

import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timezone
from typing import Any, Literal
from uuid import uuid4

import asyncpg
import nats
from fastapi import Depends, FastAPI, HTTPException, Query, Request

# Shared middleware imports - add apps/services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from shared.db.simple_migrations import Migration, SimpleMigrationRunner
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# Authentication imports - مصادقة JWT
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False

    class User:  # type: ignore[no-redef]
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise HTTPException(status_code=503, detail="Authentication backend unavailable")


# Security headers middleware
try:
    from shared.middleware.security_headers import setup_security_headers

    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False

    def setup_security_headers(app):
        pass


from shared.middleware.tenant_context import TenantContextMiddleware

from .decision_engine import (
    GrowthStage,
    Indices,
    ZoneObservation,
    classify_zone_status,
    diagnose_zone,
    generate_vrt_properties,
)
from .disease_detection import (
    CropType,
    DiseaseDetection,
    DiseaseSeverity,
    detect_diseases,
    get_overall_health_status,
)
from .nutrient_deficiency import (
    DeficiencySeverity,
    NutrientDeficiency,
    NutrientType,
    detect_nutrient_deficiencies,
    generate_fertilizer_plan,
    get_nutrient_status_summary,
)
from .pest_assessment import (
    RiskLevel,
    assess_pest_risks,
    get_pest_summary,
    get_pest_types,
)
from .yield_prediction import (
    CropType as YieldCropType,
)
from .yield_prediction import (
    get_crop_parameters,
    predict_yield,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Logging Configuration
# إعداد السجلات
# ═══════════════════════════════════════════════════════════════════════════════

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Database Migrations
# ═══════════════════════════════════════════════════════════════════════════════

MIGRATIONS = [
    Migration(
        version=1,
        description="Create crop_health_observations table",
        up="""
            CREATE TABLE IF NOT EXISTS crop_health_observations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                field_id VARCHAR(255) NOT NULL,
                zone_id VARCHAR(255) NOT NULL,
                captured_at TIMESTAMP WITH TIME ZONE,
                source VARCHAR(50),
                growth_stage VARCHAR(50),
                ndvi FLOAT,
                evi FLOAT,
                ndre FLOAT,
                lci FLOAT,
                ndwi FLOAT,
                savi FLOAT,
                cloud_pct FLOAT DEFAULT 0,
                notes TEXT,
                tenant_id VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """,
        down="DROP TABLE IF EXISTS crop_health_observations",
    ),
    Migration(
        version=2,
        description="Create crop_zones table",
        up="""
            CREATE TABLE IF NOT EXISTS crop_zones (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                zone_id VARCHAR(255) NOT NULL,
                field_id VARCHAR(255) NOT NULL,
                name VARCHAR(255),
                name_ar VARCHAR(255),
                geometry JSONB,
                area_hectares FLOAT,
                tenant_id VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(zone_id, field_id)
            )
        """,
        down="DROP TABLE IF EXISTS crop_zones",
    ),
    Migration(
        version=3,
        description="Create disease_detections table",
        up="""
            CREATE TABLE IF NOT EXISTS disease_detections (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                field_id VARCHAR(255) NOT NULL,
                disease_name VARCHAR(255) NOT NULL,
                disease_name_ar VARCHAR(255),
                confidence FLOAT,
                severity VARCHAR(50),
                detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                tenant_id VARCHAR(255)
            )
        """,
        down="DROP TABLE IF EXISTS disease_detections",
    ),
    Migration(
        version=4,
        description="Create processed_events table for NATS idempotency",
        up="""
            CREATE TABLE IF NOT EXISTS processed_events (
                tenant_id      TEXT        NOT NULL DEFAULT '_global',
                event_id       TEXT        NOT NULL,
                subject        TEXT        NOT NULL,
                service        TEXT        NOT NULL,
                correlation_id TEXT,
                status         TEXT        NOT NULL DEFAULT 'processed',
                processed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                PRIMARY KEY (tenant_id, event_id)
            )
        """,
        down="DROP TABLE IF EXISTS processed_events",
    ),
    Migration(
        version=5,
        description="Add indexes for observations, zones, diseases, and events",
        up="""
            CREATE INDEX IF NOT EXISTS idx_observations_field_zone
                ON crop_health_observations(field_id, zone_id);
            CREATE INDEX IF NOT EXISTS idx_zones_field
                ON crop_zones(field_id);
            CREATE INDEX IF NOT EXISTS idx_disease_field
                ON disease_detections(field_id);
            CREATE INDEX IF NOT EXISTS idx_processed_events_ttl
                ON processed_events (processed_at);
            CREATE INDEX IF NOT EXISTS idx_processed_events_correlation
                ON processed_events (correlation_id)
                WHERE correlation_id IS NOT NULL;
        """,
        down="""
            DROP INDEX IF EXISTS idx_processed_events_correlation;
            DROP INDEX IF EXISTS idx_processed_events_ttl;
            DROP INDEX IF EXISTS idx_disease_field;
            DROP INDEX IF EXISTS idx_zones_field;
            DROP INDEX IF EXISTS idx_observations_field_zone;
        """,
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# Feature Schema Definition (v1.0)
# تعريف مخطط المدخلات للكشف عن انحراف البيانات
# ═══════════════════════════════════════════════════════════════════════════════

FEATURE_SCHEMA = {
    "version": "1.0.0",
    "service": "crop-intelligence-service",
    "features": {
        "ndvi": {"type": "float", "min": -1.0, "max": 1.0, "unit": "index", "typical_healthy": (0.3, 0.9)},
        "evi": {"type": "float", "min": -1.0, "max": 1.0, "unit": "index", "typical_healthy": (0.2, 0.8)},
        "ndre": {"type": "float", "min": -1.0, "max": 1.0, "unit": "index", "typical_healthy": (0.1, 0.6)},
        "lci": {"type": "float", "min": -1.0, "max": 1.0, "unit": "index", "typical_healthy": (0.1, 0.5)},
        "ndwi": {"type": "float", "min": -1.0, "max": 1.0, "unit": "index", "typical_healthy": (-0.3, 0.4)},
        "savi": {"type": "float", "min": -1.0, "max": 1.0, "unit": "index", "typical_healthy": (0.2, 0.7)},
        "crop_type": {"type": "enum", "values": [e.value for e in CropType]},
        "growth_stage": {"type": "enum", "values": [e.value for e in GrowthStage]},
        "humidity_pct": {"type": "float", "min": 0, "max": 100, "unit": "%", "optional": True},
        "temp_c": {"type": "float", "min": -20, "max": 60, "unit": "°C", "optional": True},
    },
    "quality_requirements": {
        "min_cloud_free_pct": 70,
        "max_observation_age_days": 10,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Schemas
# ═══════════════════════════════════════════════════════════════════════════════


class IndicesIn(BaseModel):
    """مؤشرات الغطاء النباتي المدخلة"""

    ndvi: float = Field(..., ge=-1, le=1, description="Normalized Difference Vegetation Index")
    evi: float = Field(..., ge=-1, le=1, description="Enhanced Vegetation Index")
    ndre: float = Field(..., ge=-1, le=1, description="Normalized Difference Red Edge")
    lci: float = Field(..., ge=-1, le=1, description="Leaf Chlorophyll Index")
    ndwi: float = Field(..., ge=-1, le=1, description="Normalized Difference Water Index")
    savi: float = Field(..., ge=-1, le=1, description="Soil-Adjusted Vegetation Index")


class ObservationIn(BaseModel):
    """طلب تسجيل رصد جديد"""

    captured_at: datetime = Field(..., description="وقت الالتقاط")
    source: Literal["sentinel-2", "drone", "planet", "landsat", "other"] = Field(..., description="مصدر البيانات")
    growth_stage: GrowthStage = Field(..., description="مرحلة النمو")
    indices: IndicesIn = Field(..., description="المؤشرات")
    cloud_pct: float = Field(default=0.0, ge=0, le=100, description="نسبة الغيوم")
    notes: str | None = Field(default=None, description="ملاحظات")


class ObservationOut(BaseModel):
    """استجابة تسجيل الرصد"""

    observation_id: str
    status: Literal["stored"]
    zone_id: str
    field_id: str


class ActionOut(BaseModel):
    """إجراء موصى به"""

    zone_id: str
    type: Literal["irrigation", "fertilization", "scouting", "none"]
    priority: Literal["P0", "P1", "P2", "P3"]
    title: str
    title_en: str | None = None
    reason: str
    reason_en: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    recommended_window_hours: int | None = None
    recommended_dose_hint: Literal["low", "medium", "high"] | None = None
    severity: str | None = None


class SummaryOut(BaseModel):
    """ملخص تشخيص الحقل"""

    zones_total: int
    zones_critical: int
    zones_warning: int
    zones_ok: int


class MapLayersOut(BaseModel):
    """روابط طبقات الخريطة"""

    ndvi_raster_url: str | None = None
    ndwi_raster_url: str | None = None
    ndre_raster_url: str | None = None
    zones_geojson_url: str


class FieldDiagnosisOut(BaseModel):
    """استجابة تشخيص الحقل الكاملة"""

    field_id: str
    date: str
    summary: SummaryOut
    actions: list[ActionOut]
    map_layers: MapLayersOut


class TimelinePoint(BaseModel):
    """نقطة في السلسلة الزمنية"""

    date: str
    ndvi: float
    evi: float | None = None
    ndre: float | None = None
    ndwi: float | None = None
    lci: float | None = None
    savi: float | None = None


class ZoneTimelineOut(BaseModel):
    """السلسلة الزمنية للمنطقة"""

    zone_id: str
    field_id: str
    series: list[TimelinePoint]


class ZoneCreate(BaseModel):
    """إنشاء منطقة جديدة"""

    name: str
    name_ar: str | None = None
    geometry: dict[str, Any] | None = None
    area_hectares: float | None = None


class VRTFeature(BaseModel):
    """خاصية VRT للتصدير"""

    type: str = "Feature"
    properties: dict[str, Any]
    geometry: dict[str, Any] | None = None


class VRTExportOut(BaseModel):
    """تصدير VRT كـ GeoJSON FeatureCollection"""

    type: str = "FeatureCollection"
    features: list[VRTFeature]
    metadata: dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════════
# In-Memory Storage (fallback when database is not available)
# التخزين المؤقت في الذاكرة (احتياطي عند عدم توفر قاعدة البيانات)
# ═══════════════════════════════════════════════════════════════════════════════

# field_id -> zone_id -> list of observations
OBSERVATIONS: dict[str, dict[str, list[dict[str, Any]]]] = {}

# field_id -> zone_id -> zone_metadata
ZONES: dict[str, dict[str, dict[str, Any]]] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# Database Helper Functions
# دوال مساعدة لقاعدة البيانات
# ═══════════════════════════════════════════════════════════════════════════════

# Reference to app for database pool access
_app_ref = None


def get_db_pool() -> asyncpg.Pool | None:
    """Get database pool from app state"""
    if _app_ref is None:
        return None
    return getattr(_app_ref.state, "db_pool", None)


async def db_store_observation(
    field_id: str,
    zone_id: str,
    obs_data: dict[str, Any],
    tenant_id: str,
) -> str | None:
    """
    Store observation in database with mandatory tenant isolation.
    تخزين الرصد في قاعدة البيانات مع عزل إلزامي للمستأجر
    """
    pool = get_db_pool()
    if not pool:
        return None

    try:
        async with pool.acquire() as conn:
            result = await conn.fetchrow(
                """
                INSERT INTO crop_health_observations
                (field_id, zone_id, captured_at, source, growth_stage,
                 ndvi, evi, ndre, lci, ndwi, savi, cloud_pct, notes, tenant_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                RETURNING id
                """,
                field_id,
                zone_id,
                obs_data.get("captured_at"),
                obs_data.get("source"),
                obs_data.get("growth_stage"),
                obs_data["indices"]["ndvi"],
                obs_data["indices"]["evi"],
                obs_data["indices"]["ndre"],
                obs_data["indices"]["lci"],
                obs_data["indices"]["ndwi"],
                obs_data["indices"]["savi"],
                obs_data.get("cloud_pct", 0.0),
                obs_data.get("notes"),
                tenant_id,
            )
            return str(result["id"]) if result else None
    except Exception as e:
        logger.warning("Failed to store observation in database", error=str(e))
        return None


async def db_get_observations(
    field_id: str,
    zone_id: str,
    limit: int = 50,
    tenant_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Get observations from database with optional tenant isolation.
    استرجاع الأرصاد من قاعدة البيانات مع عزل اختياري للمستأجر
    """
    pool = get_db_pool()
    if not pool:
        return []

    try:
        async with pool.acquire() as conn:
            if tenant_id:
                rows = await conn.fetch(
                    """
                    SELECT id, field_id, zone_id, captured_at, source, growth_stage,
                           ndvi, evi, ndre, lci, ndwi, savi, cloud_pct, notes
                    FROM crop_health_observations
                    WHERE field_id = $1 AND zone_id = $2 AND tenant_id = $3
                    ORDER BY captured_at DESC
                    LIMIT $4
                    """,
                    field_id,
                    zone_id,
                    tenant_id,
                    limit,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT id, field_id, zone_id, captured_at, source, growth_stage,
                           ndvi, evi, ndre, lci, ndwi, savi, cloud_pct, notes
                    FROM crop_health_observations
                    WHERE field_id = $1 AND zone_id = $2
                    ORDER BY captured_at DESC
                    LIMIT $3
                    """,
                    field_id,
                    zone_id,
                    limit,
                )
            observations = []
            for row in rows:
                observations.append(
                    {
                        "id": str(row["id"]),
                        "captured_at": row["captured_at"].isoformat() if row["captured_at"] else None,
                        "source": row["source"],
                        "growth_stage": row["growth_stage"],
                        "indices": {
                            "ndvi": row["ndvi"],
                            "evi": row["evi"],
                            "ndre": row["ndre"],
                            "lci": row["lci"],
                            "ndwi": row["ndwi"],
                            "savi": row["savi"],
                        },
                        "cloud_pct": row["cloud_pct"],
                        "notes": row["notes"],
                    }
                )
            return observations
    except Exception as e:
        logger.warning("Failed to get observations from database", error=str(e))
        return []


async def db_get_field_observations(
    field_id: str,
    tenant_id: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """
    Get all observations for a field grouped by zone with optional tenant isolation.
    استرجاع جميع أرصاد الحقل مجمعة حسب المنطقة مع عزل اختياري للمستأجر
    """
    pool = get_db_pool()
    if not pool:
        return {}

    try:
        async with pool.acquire() as conn:
            if tenant_id:
                rows = await conn.fetch(
                    """
                    SELECT DISTINCT zone_id, field_id, captured_at, source, growth_stage,
                           ndvi, evi, ndre, lci, ndwi, savi, cloud_pct, notes
                    FROM crop_health_observations
                    WHERE field_id = $1 AND tenant_id = $2
                    ORDER BY zone_id, captured_at DESC
                    """,
                    field_id,
                    tenant_id,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT DISTINCT zone_id, field_id, captured_at, source, growth_stage,
                           ndvi, evi, ndre, lci, ndwi, savi, cloud_pct, notes
                    FROM crop_health_observations
                    WHERE field_id = $1
                    ORDER BY zone_id, captured_at DESC
                    """,
                    field_id,
                )
            result: dict[str, list[dict[str, Any]]] = {}
            for row in rows:
                zone_id = row["zone_id"]
                if zone_id not in result:
                    result[zone_id] = []
                result[zone_id].append(
                    {
                        "captured_at": row["captured_at"].isoformat() if row["captured_at"] else None,
                        "source": row["source"],
                        "growth_stage": row["growth_stage"],
                        "indices": {
                            "ndvi": row["ndvi"],
                            "evi": row["evi"],
                            "ndre": row["ndre"],
                            "lci": row["lci"],
                            "ndwi": row["ndwi"],
                            "savi": row["savi"],
                        },
                        "cloud_pct": row["cloud_pct"],
                        "notes": row["notes"],
                    }
                )
            return result
    except Exception as e:
        logger.warning("Failed to get field observations from database", error=str(e))
        return {}


async def db_store_zone(
    field_id: str,
    zone_id: str,
    zone_data: dict[str, Any],
    tenant_id: str,
) -> bool:
    """
    Store zone in database with mandatory tenant isolation.
    تخزين المنطقة في قاعدة البيانات مع عزل إلزامي للمستأجر
    """
    pool = get_db_pool()
    if not pool:
        return False

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO crop_zones
                (zone_id, field_id, name, name_ar, geometry, area_hectares, tenant_id, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                ON CONFLICT (zone_id, field_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    name_ar = EXCLUDED.name_ar,
                    geometry = EXCLUDED.geometry,
                    area_hectares = EXCLUDED.area_hectares
                """,
                zone_id,
                field_id,
                zone_data.get("name"),
                zone_data.get("name_ar"),
                json.dumps(zone_data.get("geometry")) if zone_data.get("geometry") else None,
                zone_data.get("area_hectares"),
                tenant_id,
            )
            return True
    except Exception as e:
        logger.warning("Failed to store zone in database", error=str(e))
        return False


async def db_get_zones(
    field_id: str,
    tenant_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    """
    Get zones for a field from database with optional tenant isolation.
    استرجاع مناطق الحقل من قاعدة البيانات مع عزل اختياري للمستأجر
    """
    pool = get_db_pool()
    if not pool:
        return {}

    try:
        async with pool.acquire() as conn:
            if tenant_id:
                rows = await conn.fetch(
                    """
                    SELECT zone_id, name, name_ar, geometry, area_hectares, created_at
                    FROM crop_zones
                    WHERE field_id = $1 AND tenant_id = $2
                    """,
                    field_id,
                    tenant_id,
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT zone_id, name, name_ar, geometry, area_hectares, created_at
                    FROM crop_zones
                    WHERE field_id = $1
                    """,
                    field_id,
                )
            result = {}
            for row in rows:
                geometry = None
                if row["geometry"]:
                    try:
                        geometry = json.loads(row["geometry"]) if isinstance(row["geometry"], str) else row["geometry"]
                    except (json.JSONDecodeError, TypeError):
                        geometry = None
                result[row["zone_id"]] = {
                    "name": row["name"],
                    "name_ar": row["name_ar"],
                    "geometry": geometry,
                    "area_hectares": row["area_hectares"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                }
            return result
    except Exception as e:
        logger.warning("Failed to get zones from database", error=str(e))
        return {}


async def db_store_disease_detection(
    field_id: str,
    disease_name: str,
    disease_name_ar: str | None,
    confidence: float,
    severity: str | None,
    tenant_id: str,
) -> bool:
    """
    Store disease detection in database with mandatory tenant isolation.
    تخزين كشف المرض في قاعدة البيانات
    """
    pool = get_db_pool()
    if not pool:
        return False

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO disease_detections
                (field_id, disease_name, disease_name_ar, confidence, severity, tenant_id)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                field_id,
                disease_name,
                disease_name_ar,
                confidence,
                severity,
                tenant_id,
            )
            return True
    except Exception as e:
        logger.warning("Failed to store disease detection in database", error=str(e))
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Application Setup
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _app_ref
    _app_ref = app

    logger.info("Starting Crop Intelligence Service...")

    # Initialize connection status flags
    app.state.nats_connected = False
    app.state.nc = None
    app.state.db_pool = None
    app.state.db_connected = False

    # Initialize PostgreSQL database connection
    db_url = os.getenv("DATABASE_URL")
    # Enforce sslmode for non-development database connections
    if db_url and os.getenv("ENVIRONMENT", "development") != "development":
        if "sslmode" not in db_url:
            # Use sslmode=disable for PgBouncer (port 6432) which does not support SSL
            ssl_mode = "disable" if ":6432" in db_url else "require"
            db_url += f"?sslmode={ssl_mode}" if "?" not in db_url else f"&sslmode={ssl_mode}"
    if db_url:
        try:
            await asyncpg.create_pool(
                db_url, min_size=2, max_size=10,
                statement_cache_size=0,  # PgBouncer transaction mode compatibility
            )
            app.state.db_connected = True
            logger.info("Connected to database")

            # Run versioned migrations
            migration_runner = SimpleMigrationRunner(app.state.db_pool, service_name="crop-intelligence-service")
            await migration_runner.run(MIGRATIONS)
            logger.info("Database migrations applied")
        except Exception as e:
            logger.warning("Failed to connect to database", error=str(e))
            app.state.db_pool = None
            app.state.db_connected = False
    else:
        logger.info("DATABASE_URL not configured - using in-memory storage")

    # Initialize sample data for demo (only if no database)
    if not app.state.db_connected:
        _init_sample_data()

    # Initialize NATS connection for event publishing
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            app.state.nc = await nats.connect(nats_url)
            app.state.nats_connected = True
            logger.info("Connected to NATS", nats_url=nats_url)
        except Exception as e:
            logger.warning("Failed to connect to NATS", error=str(e))
            app.state.nc = None
    else:
        logger.info("NATS_URL not configured - event publishing disabled")

    # Ensure JetStream domain streams exist (C1 fix — streams must exist before durable consumers)
    if app.state.nats_connected and app.state.nc:
        try:
            js = app.state.nc.jetstream()
            from shared.events.streams import ensure_streams

            stream_count = await ensure_streams(js)
            logger.info("jetstream_streams_ensured", count=stream_count)
        except Exception as _stream_err:
            logger.warning("jetstream_streams_ensure_failed", error=str(_stream_err))

    # Register NATS event subscribers (Intelligence→Decision wiring)
    if app.state.nats_connected and app.state.nc:
        try:
            from .event_subscribers import setup_nats_subscriptions

            app.state.nats_subs = await setup_nats_subscriptions(app.state.nc, app.state)
            logger.info("nats_subscribers_registered", count=len(app.state.nats_subs))
        except Exception as _sub_err:
            logger.warning("nats_subscribers_failed", error=str(_sub_err))

    # Initialize calibration worker (processes queued runs on startup)
    try:
        from shared.calibration.worker import CalibrationWorker

        cal_worker = CalibrationWorker(
            db_pool=app.state.db_pool,
            nats_client=app.state.nc,
        )
        app.state.calibration_worker = cal_worker
        # Process any pending runs from previous shutdown
        if app.state.db_connected:
            processed = await cal_worker.process_pending(max_runs=3)
            if processed:
                logger.info("calibration_startup_processed", run_ids=processed)
    except Exception as _cal_err:
        logger.warning("calibration_worker_init_failed", error=str(_cal_err))

    port = os.getenv("PORT", "8095")
    logger.info("Crop Intelligence Service ready", port=port)
    yield

    # Shutdown: Close connections
    logger.info("Shutting down Crop Intelligence Service...")

    # Close database pool
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("Database connection closed")

    # Close NATS connection
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("NATS connection closed")

    _app_ref = None
    logger.info("Crop Intelligence Service stopped")


def _init_sample_data():
    """تهيئة بيانات تجريبية للعرض"""
    field_id = "field_demo"
    ZONES[field_id] = {
        "zone_a": {"name": "Zone A", "name_ar": "المنطقة أ", "area_hectares": 5.2},
        "zone_b": {"name": "Zone B", "name_ar": "المنطقة ب", "area_hectares": 4.8},
        "zone_c": {"name": "Zone C", "name_ar": "المنطقة ج", "area_hectares": 6.1},
    }

    # Sample observations
    OBSERVATIONS[field_id] = {
        "zone_a": [
            {
                "captured_at": "2025-12-14T10:00:00Z",
                "source": "sentinel-2",
                "growth_stage": "mid",
                "indices": {
                    "ndvi": 0.78,
                    "evi": 0.62,
                    "ndre": 0.21,
                    "lci": 0.32,
                    "ndwi": -0.05,
                    "savi": 0.65,
                },
                "cloud_pct": 5.0,
            }
        ],
        "zone_b": [
            {
                "captured_at": "2025-12-14T10:00:00Z",
                "source": "sentinel-2",
                "growth_stage": "mid",
                "indices": {
                    "ndvi": 0.65,
                    "evi": 0.52,
                    "ndre": 0.35,
                    "lci": 0.28,
                    "ndwi": 0.02,
                    "savi": 0.55,
                },
                "cloud_pct": 5.0,
            }
        ],
        "zone_c": [
            {
                "captured_at": "2025-12-14T10:00:00Z",
                "source": "sentinel-2",
                "growth_stage": "mid",
                "indices": {
                    "ndvi": 0.41,
                    "evi": 0.32,
                    "ndre": 0.18,
                    "lci": 0.15,
                    "ndwi": -0.12,
                    "savi": 0.35,
                },
                "cloud_pct": 5.0,
            }
        ],
    }


app = FastAPI(
    title="SAHOOL Crop Health Service",
    description="خدمة تشخيص صحة المحاصيل - Intelligent crop health diagnostics with decision support",
    version="16.0.0",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# CORS - Secure configuration
try:
    from shared.cors_config import CORS_SETTINGS

    app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
except ImportError:
    ALLOWED_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "https://sahool.io,https://admin.sahool.io,http://localhost:3000",
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id"],
    )

# Security headers - رؤوس الأمان
if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)

# Tenant context middleware - عزل المستأجرين
app.add_middleware(TenantContextMiddleware)

# ── Digital Twin Router ────────────────────────────────────────────────────
try:
    from .twin_router import router as twin_router

    app.include_router(twin_router, prefix="/api/v1")
except Exception as _twin_import_error:  # pragma: no cover
    import logging

    logging.getLogger(__name__).warning("Digital Twin router not loaded: %s", _twin_import_error)

# ── Process Models Router ──────────────────────────────────────────────────
try:
    from .models_router import router as models_router

    app.include_router(models_router, prefix="/api/v1")
except Exception as _models_import_error:  # pragma: no cover
    import logging

    logging.getLogger(__name__).warning("Process Models router not loaded: %s", _models_import_error)

# ── Calibration Router ────────────────────────────────────────────────────
try:
    from .calibration_router import router as calibration_router

    app.include_router(calibration_router, prefix="/api/v1")
except Exception as _cal_import_error:  # pragma: no cover
    import logging

    logging.getLogger(__name__).warning("Calibration router not loaded: %s", _cal_import_error)

# ── Soil & Fertility Router ──────────────────────────────────────────────
try:
    from .soil_fertility_router import router as soil_fertility_router

    app.include_router(soil_fertility_router, prefix="/api/v1")
except Exception as _sf_import_error:  # pragma: no cover
    import logging

    logging.getLogger(__name__).warning("Soil & Fertility router not loaded: %s", _sf_import_error)


# ═══════════════════════════════════════════════════════════════════════════════
# Health Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/v1/feature-schema")
def get_feature_schema():
    """Return the ML feature schema for data drift monitoring."""
    return FEATURE_SCHEMA


@app.get("/healthz")
def health():
    """Health check endpoint (liveness probe)"""
    return {
        "status": "ok",
        "service": "crop-intelligence-service",
        "version": "16.0.0",
    }


@app.get("/readyz")
def readiness():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    nats_connected = getattr(app.state, "nats_connected", False)
    db_connected = getattr(app.state, "db_connected", False)

    # Determine NATS status
    if nats_connected:
        nats_status = "connected"
    elif os.getenv("NATS_URL"):
        nats_status = "disconnected"
    else:
        nats_status = "not_configured"

    # Determine database status
    if db_connected:
        db_status = "connected"
    elif os.getenv("DATABASE_URL"):
        db_status = "disconnected"
    else:
        db_status = "not_configured"

    return {
        "status": "ready",
        "service": "crop-intelligence-service",
        "version": "16.0.0",
        "checks": {
            "service": "ready",
            "nats": nats_status,
            "database": db_status,
        },
    }


@app.get("/")
def root():
    return {
        "service": "SAHOOL Crop Health",
        "version": "16.0.0",
        "description_ar": "خدمة تشخيص صحة المحاصيل",
        "description_en": "Crop health diagnostic service",
        "endpoints": {
            "observations": "/api/v1/fields/{field_id}/zones/{zone_id}/observations",
            "diagnosis": "/api/v1/fields/{field_id}/diagnosis",
            "timeline": "/api/v1/fields/{field_id}/zones/{zone_id}/timeline",
            "vrt_export": "/api/v1/fields/{field_id}/vrt",
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NATS Event Publishing Helpers
# مساعدات نشر الأحداث
# ═══════════════════════════════════════════════════════════════════════════════


async def publish_event(subject: str, data: dict[str, Any]) -> bool:
    """
    Publish an event to NATS
    نشر حدث إلى NATS

    Args:
        subject: NATS subject (e.g., "sahool.crop.disease_detected")
        data: Event data dictionary

    Returns:
        True if published successfully, False otherwise
    """
    nc = getattr(app.state, "nc", None)
    if nc is None:
        return False

    try:
        payload = json.dumps(data).encode("utf-8")
        await nc.publish(subject, payload)
        logger.info("Published NATS event", subject=subject, data_keys=list(data.keys()))
        return True
    except Exception as e:
        logger.warning("Failed to publish NATS event", subject=subject, error=str(e))
        return False


async def publish_disease_detected(
    field_id: str,
    disease: str,
    confidence: float,
    severity: str | None = None,
    zone_id: str | None = None,
    tenant_id: str | None = None,
) -> bool:
    """
    Publish disease detection event
    نشر حدث اكتشاف مرض

    Uses tenant-scoped subject when tenant_id is available for multi-tenant isolation.
    يستخدم موضوع مخصص للمستأجر عند توفر معرف المستأجر لعزل البيانات.

    Subject (global): sahool.crop.disease_detected
    Subject (tenant): sahool.tenant.{tenant_id}.crop.disease_detected
    """
    data = {
        "field_id": field_id,
        "disease": disease,
        "confidence": confidence,
        "severity": severity,
        "zone_id": zone_id,
        "tenant_id": tenant_id,
        "timestamp": datetime.now(UTC).isoformat() + "Z",
    }
    # Use tenant-scoped subject for data isolation | استخدام موضوع مخصص للمستأجر لعزل البيانات
    if tenant_id:
        from shared.events.subjects import get_tenant_subject

        subject = get_tenant_subject(tenant_id, "crop", "disease_detected")
    else:
        # SECURITY FIX: Log warning and use global subject as fallback,
        # but include warning in event data for downstream consumers
        logger.warning("Publishing disease_detected event without tenant_id - tenant isolation gap")
        subject = "sahool.crop.disease_detected"
    return await publish_event(subject, data)


async def publish_health_assessed(
    field_id: str,
    health_score: str,
    health_score_ar: str,
    issues: list[str],
    zone_id: str | None = None,
    tenant_id: str | None = None,
) -> bool:
    """
    Publish health assessment event
    نشر حدث تقييم الصحة

    Uses tenant-scoped subject when tenant_id is available for multi-tenant isolation.
    يستخدم موضوع مخصص للمستأجر عند توفر معرف المستأجر لعزل البيانات.

    Subject (global): sahool.crop.health_assessed
    Subject (tenant): sahool.tenant.{tenant_id}.crop.health_assessed
    """
    data = {
        "field_id": field_id,
        "health_score": health_score,
        "health_score_ar": health_score_ar,
        "issues": issues,
        "zone_id": zone_id,
        "tenant_id": tenant_id,
        "timestamp": datetime.now(UTC).isoformat() + "Z",
    }
    # Use tenant-scoped subject for data isolation | استخدام موضوع مخصص للمستأجر لعزل البيانات
    if tenant_id:
        from shared.events.subjects import get_tenant_subject

        subject = get_tenant_subject(tenant_id, "crop", "health_assessed")
    else:
        # SECURITY FIX: Log warning when publishing without tenant scoping
        logger.warning("Publishing health_assessed event without tenant_id - tenant isolation gap")
        subject = "sahool.crop.health_assessed"
    return await publish_event(subject, data)


# ═══════════════════════════════════════════════════════════════════════════════
# Helper to get observations (from DB or memory)
# ═══════════════════════════════════════════════════════════════════════════════


async def get_field_observations_data(
    field_id: str,
    tenant_id: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Get observations for a field from database or memory"""
    # Try database first
    db_obs = await db_get_field_observations(field_id, tenant_id=tenant_id)
    if db_obs:
        return db_obs
    # Fall back to memory
    return OBSERVATIONS.get(field_id, {})


async def get_zones_data(
    field_id: str,
    tenant_id: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Get zones for a field from database or memory"""
    # Try database first
    db_zones = await db_get_zones(field_id, tenant_id=tenant_id)
    if db_zones:
        return db_zones
    # Fall back to memory
    return ZONES.get(field_id, {})


# ═══════════════════════════════════════════════════════════════════════════════
# Zone Management
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/fields/{field_id}/zones")
async def create_zone(
    field_id: str,
    zone: ZoneCreate,
    user: User | None = Depends(get_current_user),
):
    """إنشاء منطقة جديدة في الحقل"""
    if not user or not getattr(user, "tenant_id", None):
        raise HTTPException(status_code=401, detail="Tenant context required")
    tenant_id = str(user.tenant_id)

    zone_id = f"zone_{uuid4().hex[:8]}"

    zone_data = {
        "name": zone.name,
        "name_ar": zone.name_ar,
        "geometry": zone.geometry,
        "area_hectares": zone.area_hectares,
        "created_at": datetime.now(UTC).isoformat(),
    }

    # Try to store in database first with tenant isolation
    stored_in_db = await db_store_zone(field_id, zone_id, zone_data, tenant_id)

    # Always store in memory as fallback
    if field_id not in ZONES:
        ZONES[field_id] = {}
    ZONES[field_id][zone_id] = zone_data

    return {
        "zone_id": zone_id,
        "status": "created",
        "storage": "database" if stored_in_db else "memory",
    }


@app.get("/api/v1/fields/{field_id}/zones")
async def list_zones(
    field_id: str,
    user: User | None = Depends(get_current_user),
):
    """قائمة المناطق في الحقل"""
    tenant_id = str(user.tenant_id) if user and getattr(user, "tenant_id", None) else None
    # Try to get from database first
    db_zones = await db_get_zones(field_id, tenant_id=tenant_id)
    if db_zones:
        zones = [{"zone_id": zid, **zdata} for zid, zdata in db_zones.items()]
        return {"zones": zones, "count": len(zones), "source": "database"}

    # Fall back to in-memory storage
    if field_id not in ZONES:
        return {"zones": [], "count": 0, "source": "memory"}

    zones = [{"zone_id": zid, **zdata} for zid, zdata in ZONES[field_id].items()]
    return {"zones": zones, "count": len(zones), "source": "memory"}


@app.get("/api/v1/fields/{field_id}/zones.geojson")
async def get_zones_geojson(
    field_id: str,
    user: User | None = Depends(get_current_user),
):
    """تصدير المناطق كـ GeoJSON"""
    tenant_id = str(user.tenant_id) if user and getattr(user, "tenant_id", None) else None
    # Try to get from database first
    db_zones = await db_get_zones(field_id, tenant_id=tenant_id)
    zone_data = db_zones if db_zones else ZONES.get(field_id, {})

    if not zone_data:
        raise HTTPException(status_code=404, detail="Field not found")

    features = []
    for zone_id, zdata in zone_data.items():
        features.append(
            {
                "type": "Feature",
                "id": zone_id,
                "properties": {
                    "zone_id": zone_id,
                    "name": zdata.get("name"),
                    "name_ar": zdata.get("name_ar"),
                    "area_hectares": zdata.get("area_hectares"),
                },
                "geometry": zdata.get("geometry"),
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Observations (Ingest)
# ═══════════════════════════════════════════════════════════════════════════════


@app.post(
    "/api/v1/fields/{field_id}/zones/{zone_id}/observations",
    response_model=ObservationOut,
)
async def ingest_observation(
    field_id: str,
    zone_id: str,
    body: ObservationIn,
    user: User | None = Depends(get_current_user),
):
    """
    تسجيل رصد جديد لمؤشرات الغطاء النباتي

    يستقبل بيانات من Sentinel-2 أو الدرونز أو مصادر أخرى
    """
    if not user or not getattr(user, "tenant_id", None):
        raise HTTPException(status_code=401, detail="Tenant context required")
    tenant_id = str(user.tenant_id)

    obs = body.model_dump()
    obs["captured_at"] = body.captured_at.isoformat()
    obs["indices"] = body.indices.model_dump()

    # Try to store in database with tenant isolation
    db_obs_id = await db_store_observation(
        field_id,
        zone_id,
        {
            "captured_at": body.captured_at,
            "source": body.source,
            "growth_stage": body.growth_stage.value,
            "indices": body.indices.model_dump(),
            "cloud_pct": body.cloud_pct,
            "notes": body.notes,
        },
        tenant_id,
    )

    # Always store in memory as fallback
    if field_id not in OBSERVATIONS:
        OBSERVATIONS[field_id] = {}
    if zone_id not in OBSERVATIONS[field_id]:
        OBSERVATIONS[field_id][zone_id] = []
    OBSERVATIONS[field_id][zone_id].append(obs)

    observation_id = db_obs_id or f"obs_{field_id}_{zone_id}_{int(body.captured_at.timestamp())}"

    return ObservationOut(
        observation_id=observation_id,
        status="stored",
        zone_id=zone_id,
        field_id=field_id,
    )


@app.get("/api/v1/fields/{field_id}/zones/{zone_id}/observations")
async def list_observations(
    field_id: str,
    zone_id: str,
    limit: int = Query(default=50, le=200),
    user: User | None = Depends(get_current_user),
):
    """قائمة الأرصاد للمنطقة"""
    tenant_id = str(user.tenant_id) if user and getattr(user, "tenant_id", None) else None
    # Try to get from database first
    db_obs = await db_get_observations(field_id, zone_id, limit, tenant_id=tenant_id)
    if db_obs:
        return {"observations": db_obs, "count": len(db_obs), "source": "database"}

    # Fall back to in-memory storage
    if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
        return {"observations": [], "count": 0, "source": "memory"}

    obs_list = OBSERVATIONS[field_id][zone_id][-limit:]
    return {"observations": obs_list, "count": len(obs_list), "source": "memory"}


# ═══════════════════════════════════════════════════════════════════════════════
# Diagnosis (Decision Engine Output)
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/fields/{field_id}/diagnosis")
async def get_field_diagnosis(
    field_id: str,
    date_str: str = Query(..., alias="date", description="التاريخ (YYYY-MM-DD)"),
    user: User | None = Depends(get_current_user),
):
    """
    تشخيص كامل للحقل - "الطبيب الزراعي"

    يُرجع:
    - ملخص حالة المناطق
    - قائمة الإجراءات المطلوبة مرتبة بالأولوية
    - روابط طبقات الخريطة
    """
    tenant_id = str(user.tenant_id) if user and getattr(user, "tenant_id", None) else None

    try:
        target = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="تنسيق تاريخ غير صالح، استخدم YYYY-MM-DD")

    # Get observations from database or memory
    zones = await get_field_observations_data(field_id, tenant_id=tenant_id)

    if not zones:
        raise HTTPException(status_code=404, detail="الحقل غير موجود أو لا توجد أرصاد")

    all_actions: list[dict[str, Any]] = []

    for zone_id, obs_list in zones.items():
        if not obs_list:
            continue

        # اختر آخر رصد في التاريخ المطلوب أو آخر رصد متاح
        same_day = [o for o in obs_list if datetime.fromisoformat(o["captured_at"]).date() == target]
        chosen = same_day[-1] if same_day else obs_list[-1]

        # بناء كائن المؤشرات
        idx_in = chosen["indices"]
        idx = Indices(
            ndvi=idx_in["ndvi"],
            evi=idx_in["evi"],
            ndre=idx_in["ndre"],
            lci=idx_in["lci"],
            ndwi=idx_in["ndwi"],
            savi=idx_in["savi"],
        )

        zone_obs = ZoneObservation(
            zone_id=zone_id,
            growth_stage=GrowthStage(chosen["growth_stage"]),
            indices=idx,
        )

        # تشخيص المنطقة
        actions = diagnose_zone(zone_obs)
        all_actions.extend(actions)

    # حساب الملخص
    zones_total = len(zones)
    zone_statuses = {}
    for action in all_actions:
        zid = action["zone_id"]
        if zid not in zone_statuses:
            zone_statuses[zid] = "ok"
        if action["priority"] == "P0":
            zone_statuses[zid] = "critical"
        elif action["priority"] in ("P1", "P2") and zone_statuses[zid] != "critical":
            zone_statuses[zid] = "warning"

    crit = sum(1 for s in zone_statuses.values() if s == "critical")
    warn = sum(1 for s in zone_statuses.values() if s == "warning")
    ok_count = zones_total - crit - warn

    # ترتيب الإجراءات حسب الأولوية
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    all_actions.sort(key=lambda a: priority_order.get(a["priority"], 9))

    base_url = os.getenv("CDN_BASE_URL", "https://cdn.sahool.io")

    return {
        "field_id": field_id,
        "date": target.isoformat(),
        "summary": {
            "zones_total": zones_total,
            "zones_critical": crit,
            "zones_warning": warn,
            "zones_ok": max(ok_count, 0),
        },
        "actions": all_actions,
        "map_layers": {
            "ndvi_raster_url": f"{base_url}/maps/{field_id}/{target}/ndvi.tiff",
            "ndwi_raster_url": f"{base_url}/maps/{field_id}/{target}/ndwi.tiff",
            "ndre_raster_url": f"{base_url}/maps/{field_id}/{target}/ndre.tiff",
            "zones_geojson_url": f"/api/v1/fields/{field_id}/zones.geojson",
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Timeline
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/fields/{field_id}/zones/{zone_id}/timeline")
async def get_zone_timeline(
    field_id: str,
    zone_id: str,
    from_date: str = Query(..., alias="from", description="من تاريخ (YYYY-MM-DD)"),
    to_date: str = Query(..., alias="to", description="إلى تاريخ (YYYY-MM-DD)"),
    user: User | None = Depends(get_current_user),
):
    """
    السلسلة الزمنية لمؤشرات المنطقة

    مفيدة لتتبع التغيرات وعرضها في رسم بياني
    """
    tenant_id = str(user.tenant_id) if user and getattr(user, "tenant_id", None) else None

    try:
        start = date.fromisoformat(from_date)
        end = date.fromisoformat(to_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="تنسيق تاريخ غير صالح")

    # Try to get from database first
    db_obs = await db_get_observations(field_id, zone_id, 1000, tenant_id=tenant_id)
    obs_list = db_obs if db_obs else OBSERVATIONS.get(field_id, {}).get(zone_id, [])

    if not obs_list:
        return {"zone_id": zone_id, "field_id": field_id, "series": []}

    # فلترة حسب النطاق الزمني
    series = []
    for obs in obs_list:
        obs_date = datetime.fromisoformat(obs["captured_at"]).date()
        if start <= obs_date <= end:
            idx = obs["indices"]
            series.append(
                {
                    "date": obs_date.isoformat(),
                    "ndvi": idx["ndvi"],
                    "evi": idx.get("evi"),
                    "ndre": idx.get("ndre"),
                    "ndwi": idx.get("ndwi"),
                    "lci": idx.get("lci"),
                    "savi": idx.get("savi"),
                }
            )

    # ترتيب زمني
    series.sort(key=lambda x: x["date"])

    return {
        "zone_id": zone_id,
        "field_id": field_id,
        "series": series,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# VRT Export (Variable Rate Technology)
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/api/v1/fields/{field_id}/vrt")
async def export_vrt(
    field_id: str,
    date_str: str = Query(..., alias="date", description="التاريخ (YYYY-MM-DD)"),
    action_type: str | None = Query(default=None, description="نوع الإجراء: irrigation, fertilization, all"),
):
    """
    تصدير VRT للعمليات الزراعية الدقيقة

    يُنتج GeoJSON مع خصائص قابلة للاستخدام مباشرة في:
    - أنظمة الري الذكي
    - آلات التسميد المتغير (VRT)
    - تطبيقات الطيران الزراعي
    """
    try:
        target = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="تنسيق تاريخ غير صالح")

    # Get data from database or memory
    zones = await get_field_observations_data(field_id)
    zone_metadata = await get_zones_data(field_id)

    if not zones:
        raise HTTPException(status_code=404, detail="الحقل غير موجود")

    features = []

    for zone_id, obs_list in zones.items():
        if not obs_list:
            continue

        # آخر رصد
        same_day = [o for o in obs_list if datetime.fromisoformat(o["captured_at"]).date() == target]
        chosen = same_day[-1] if same_day else obs_list[-1]

        idx_in = chosen["indices"]
        idx = Indices(
            ndvi=idx_in["ndvi"],
            evi=idx_in["evi"],
            ndre=idx_in["ndre"],
            lci=idx_in["lci"],
            ndwi=idx_in["ndwi"],
            savi=idx_in["savi"],
        )

        zone_obs = ZoneObservation(
            zone_id=zone_id,
            growth_stage=GrowthStage(chosen["growth_stage"]),
            indices=idx,
        )

        actions = diagnose_zone(zone_obs)

        # فلترة حسب نوع الإجراء
        if action_type and action_type != "all":
            actions = [a for a in actions if a["type"] == action_type]

        # توليد خصائص VRT
        vrt_props = generate_vrt_properties(zone_id, actions)

        # إضافة معلومات المنطقة
        z_meta = zone_metadata.get(zone_id, {})
        vrt_props["name"] = z_meta.get("name", zone_id)
        vrt_props["name_ar"] = z_meta.get("name_ar")
        vrt_props["area_hectares"] = z_meta.get("area_hectares")

        # إضافة المؤشرات الخام
        vrt_props["indices"] = {
            "ndvi": idx.ndvi,
            "ndre": idx.ndre,
            "ndwi": idx.ndwi,
        }

        features.append(
            {
                "type": "Feature",
                "id": zone_id,
                "properties": vrt_props,
                "geometry": z_meta.get("geometry"),
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {
            "field_id": field_id,
            "date": target.isoformat(),
            "export_type": "vrt",
            "generated_at": datetime.now(UTC).isoformat(),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Quick Diagnosis (Single Zone)
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/diagnose")
def quick_diagnose(
    body: ObservationIn, zone_id: str = Query(default="zone_temp"), current_user: User = Depends(get_current_user)
):
    """
    تشخيص سريع بدون حفظ

    مفيد للاختبار أو التشخيص الفوري
    """
    idx = Indices(
        ndvi=body.indices.ndvi,
        evi=body.indices.evi,
        ndre=body.indices.ndre,
        lci=body.indices.lci,
        ndwi=body.indices.ndwi,
        savi=body.indices.savi,
    )

    zone_obs = ZoneObservation(
        zone_id=zone_id,
        growth_stage=body.growth_stage,
        indices=idx,
    )

    actions = diagnose_zone(zone_obs)

    return {
        "zone_id": zone_id,
        "status": classify_zone_status(actions),
        "actions": actions,
        "indices_received": body.indices.model_dump(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Disease Detection Endpoints
# نقاط نهاية كشف الأمراض
# ═══════════════════════════════════════════════════════════════════════════════


class DiseaseDetectionRequest(BaseModel):
    """طلب كشف الأمراض"""

    ndvi: float = Field(..., ge=-1, le=1, description="NDVI value")
    evi: float = Field(..., ge=-1, le=1, description="EVI value")
    ndre: float = Field(..., ge=-1, le=1, description="NDRE value")
    ndwi: float = Field(..., ge=-1, le=1, description="NDWI value")
    lci: float = Field(..., ge=-1, le=1, description="LCI value")
    savi: float = Field(..., ge=-1, le=1, description="SAVI value")
    crop_type: CropType = Field(default=CropType.UNKNOWN, description="نوع المحصول")
    humidity_pct: float | None = Field(default=None, ge=0, le=100, description="الرطوبة %")
    temp_c: float | None = Field(default=None, ge=-50, le=60, description="الحرارة °C")


@app.post("/api/v1/disease/detect")
async def detect_crop_diseases(
    body: DiseaseDetectionRequest,
    field_id: str | None = Query(default=None, description="Optional field ID for event publishing"),
    user: User | None = Depends(get_current_user),
):
    """
    كشف الأمراض المحتملة من المؤشرات النباتية
    Detect potential diseases from vegetation indices

    Returns diseases with severity, confidence, and treatment recommendations.
    Publishes sahool.crop.disease_detected events to NATS if field_id is provided.
    """
    detections = detect_diseases(
        ndvi=body.ndvi,
        evi=body.evi,
        ndre=body.ndre,
        ndwi=body.ndwi,
        lci=body.lci,
        savi=body.savi,
        crop_type=body.crop_type,
        humidity_pct=body.humidity_pct,
        temp_c=body.temp_c,
    )

    health_en, health_ar = get_overall_health_status(detections)

    # Publish disease detection events to NATS and store in database
    if not user or not getattr(user, "tenant_id", None):
        raise HTTPException(status_code=401, detail="Tenant context required")
    tenant_id = str(user.tenant_id)
    if field_id and detections:
        for detection in detections:
            await publish_disease_detected(
                field_id=field_id,
                disease=detection.disease_type.value,
                confidence=detection.confidence,
                severity=detection.severity.value if detection.severity else None,
                tenant_id=tenant_id,
            )
            # Store in database with tenant isolation
            await db_store_disease_detection(
                field_id=field_id,
                disease_name=detection.disease_type.value,
                disease_name_ar=getattr(detection, "disease_type_ar", None),
                confidence=detection.confidence,
                severity=detection.severity.value if detection.severity else None,
                tenant_id=tenant_id,
            )

        # Publish health assessment event
        issues = [d.disease_type.value for d in detections]
        await publish_health_assessed(
            field_id=field_id,
            health_score=health_en,
            health_score_ar=health_ar,
            issues=issues,
            tenant_id=tenant_id,
        )

    return {
        "overall_health": {
            "status_en": health_en,
            "status_ar": health_ar,
        },
        "detection_count": len(detections),
        "detections": [d.to_dict() for d in detections],
        "input_indices": {
            "ndvi": body.ndvi,
            "evi": body.evi,
            "ndre": body.ndre,
            "ndwi": body.ndwi,
            "lci": body.lci,
            "savi": body.savi,
        },
        "environmental_context": {
            "crop_type": body.crop_type.value,
            "humidity_pct": body.humidity_pct,
            "temp_c": body.temp_c,
        },
    }


@app.post("/api/v1/fields/{field_id}/zones/{zone_id}/disease-analysis")
async def analyze_zone_diseases(
    field_id: str,
    zone_id: str,
    humidity_pct: float | None = Query(default=None, ge=0, le=100),
    temp_c: float | None = Query(default=None, ge=-50, le=60),
    crop_type: CropType = Query(default=CropType.UNKNOWN),
    tenant_id: str | None = Query(
        default=None, description="Tenant ID for scoped events | معرف المستأجر للأحداث المعزولة"
    ),
    current_user: User = Depends(get_current_user),
):
    """
    تحليل أمراض المنطقة من آخر رصد
    Analyze zone diseases from latest observation
    """
    user_tenant_id = str(current_user.tenant_id) if getattr(current_user, "tenant_id", None) else None
    # Try to get from database first
    db_obs = await db_get_observations(field_id, zone_id, 1, tenant_id=user_tenant_id)
    if db_obs:
        obs_list = db_obs
    else:
        if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
            raise HTTPException(status_code=404, detail="Zone not found or no observations")
        obs_list = OBSERVATIONS[field_id][zone_id]

    if not obs_list:
        raise HTTPException(status_code=404, detail="No observations for this zone")

    # Get latest observation
    latest = obs_list[-1]
    idx = latest["indices"]

    # Detect diseases
    detections = detect_diseases(
        ndvi=idx["ndvi"],
        evi=idx["evi"],
        ndre=idx["ndre"],
        ndwi=idx["ndwi"],
        lci=idx["lci"],
        savi=idx["savi"],
        crop_type=crop_type,
        humidity_pct=humidity_pct,
        temp_c=temp_c,
    )

    health_en, health_ar = get_overall_health_status(detections)

    # Publish disease detection events to NATS with tenant isolation
    # نشر أحداث اكتشاف الأمراض مع عزل المستأجر
    if detections:
        for detection in detections:
            await publish_disease_detected(
                field_id=field_id,
                disease=detection.disease_type.value,
                confidence=detection.confidence,
                severity=detection.severity.value if detection.severity else None,
                zone_id=zone_id,
                tenant_id=tenant_id,
            )

    # Publish health assessment event
    issues = [d.disease_type.value for d in detections] if detections else []
    await publish_health_assessed(
        field_id=field_id,
        health_score=health_en,
        health_score_ar=health_ar,
        issues=issues,
        zone_id=zone_id,
        tenant_id=tenant_id,
    )

    # Get zone metadata
    zone_metadata = await get_zones_data(field_id, tenant_id=user_tenant_id)
    zone_meta = zone_metadata.get(zone_id, {})

    return {
        "field_id": field_id,
        "zone_id": zone_id,
        "zone_name": zone_meta.get("name", zone_id),
        "zone_name_ar": zone_meta.get("name_ar"),
        "observation_date": latest.get("captured_at"),
        "overall_health": {
            "status_en": health_en,
            "status_ar": health_ar,
        },
        "detection_count": len(detections),
        "detections": [d.to_dict() for d in detections],
        "indices": idx,
    }


@app.get("/api/v1/disease/types")
def list_disease_types():
    """قائمة أنواع الأمراض المدعومة"""
    from .disease_detection import DiseaseType, TreatmentType

    return {
        "disease_types": [{"value": dt.value, "name": dt.name} for dt in DiseaseType],
        "treatment_types": [{"value": tt.value, "name": tt.name} for tt in TreatmentType],
        "crop_types": [{"value": ct.value, "name": ct.name} for ct in CropType],
        "severity_levels": [{"value": ds.value, "name": ds.name} for ds in DiseaseSeverity],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Nutrient Deficiency Endpoints
# نقاط نهاية كشف نقص العناصر الغذائية
# ═══════════════════════════════════════════════════════════════════════════════


class NutrientDetectionRequest(BaseModel):
    """طلب كشف نقص العناصر الغذائية"""

    ndvi: float = Field(..., ge=-1, le=1, description="NDVI value")
    evi: float = Field(..., ge=-1, le=1, description="EVI value")
    ndre: float = Field(..., ge=-1, le=1, description="NDRE value")
    ndwi: float = Field(..., ge=-1, le=1, description="NDWI value")
    lci: float = Field(..., ge=-1, le=1, description="LCI value")
    savi: float = Field(..., ge=-1, le=1, description="SAVI value")
    growth_stage: str = Field(default="vegetative", description="مرحلة النمو")


class FertilizerPlanRequest(BaseModel):
    """طلب خطة التسميد"""

    ndvi: float = Field(..., ge=-1, le=1)
    evi: float = Field(..., ge=-1, le=1)
    ndre: float = Field(..., ge=-1, le=1)
    ndwi: float = Field(..., ge=-1, le=1)
    lci: float = Field(..., ge=-1, le=1)
    savi: float = Field(..., ge=-1, le=1)
    field_area_hectares: float = Field(default=1.0, gt=0, description="مساحة الحقل بالهكتار")
    budget_usd: float | None = Field(default=None, ge=0, description="الميزانية بالدولار")


@app.post("/api/v1/nutrients/detect")
def detect_nutrients(body: NutrientDetectionRequest, current_user: User = Depends(get_current_user)):
    """كشف نقص العناصر الغذائية من المؤشرات النباتية"""
    deficiencies = detect_nutrient_deficiencies(
        ndvi=body.ndvi,
        evi=body.evi,
        ndre=body.ndre,
        ndwi=body.ndwi,
        lci=body.lci,
        savi=body.savi,
        growth_stage=body.growth_stage,
    )

    summary = get_nutrient_status_summary(deficiencies)

    return {
        "nutrient_status": summary,
        "deficiency_count": len(deficiencies),
        "deficiencies": [d.to_dict() for d in deficiencies],
        "input_indices": {
            "ndvi": body.ndvi,
            "evi": body.evi,
            "ndre": body.ndre,
            "ndwi": body.ndwi,
            "lci": body.lci,
            "savi": body.savi,
        },
        "growth_stage": body.growth_stage,
    }


@app.post("/api/v1/nutrients/fertilizer-plan")
def create_fertilizer_plan(body: FertilizerPlanRequest, current_user: User = Depends(get_current_user)):
    """إنشاء خطة تسميد مخصصة"""
    deficiencies = detect_nutrient_deficiencies(
        ndvi=body.ndvi,
        evi=body.evi,
        ndre=body.ndre,
        ndwi=body.ndwi,
        lci=body.lci,
        savi=body.savi,
    )

    plan = generate_fertilizer_plan(
        deficiencies=deficiencies,
        field_area_hectares=body.field_area_hectares,
        budget_usd=body.budget_usd,
    )

    summary = get_nutrient_status_summary(deficiencies)

    return {
        "nutrient_status": summary,
        "fertilizer_plan": plan,
        "deficiencies_detected": len(deficiencies),
        "field_area_hectares": body.field_area_hectares,
        "budget_usd": body.budget_usd,
    }


@app.post("/api/v1/fields/{field_id}/zones/{zone_id}/nutrient-analysis")
async def analyze_zone_nutrients(
    field_id: str,
    zone_id: str,
    field_area_hectares: float = Query(default=1.0, gt=0),
    current_user: User = Depends(get_current_user),
):
    """تحليل العناصر الغذائية في المنطقة من آخر رصد"""
    user_tenant_id = str(current_user.tenant_id) if getattr(current_user, "tenant_id", None) else None
    # Try to get from database first
    db_obs = await db_get_observations(field_id, zone_id, 1, tenant_id=user_tenant_id)
    if db_obs:
        obs_list = db_obs
    else:
        if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
            raise HTTPException(status_code=404, detail="Zone not found or no observations")
        obs_list = OBSERVATIONS[field_id][zone_id]

    if not obs_list:
        raise HTTPException(status_code=404, detail="No observations for this zone")

    latest = obs_list[-1]
    idx = latest["indices"]

    deficiencies = detect_nutrient_deficiencies(
        ndvi=idx["ndvi"],
        evi=idx["evi"],
        ndre=idx["ndre"],
        ndwi=idx["ndwi"],
        lci=idx["lci"],
        savi=idx["savi"],
        growth_stage=latest.get("growth_stage", "vegetative"),
    )

    summary = get_nutrient_status_summary(deficiencies)
    plan = generate_fertilizer_plan(
        deficiencies=deficiencies,
        field_area_hectares=field_area_hectares,
    )

    zone_metadata = await get_zones_data(field_id, tenant_id=user_tenant_id)
    zone_meta = zone_metadata.get(zone_id, {})

    return {
        "field_id": field_id,
        "zone_id": zone_id,
        "zone_name": zone_meta.get("name", zone_id),
        "zone_name_ar": zone_meta.get("name_ar"),
        "observation_date": latest.get("captured_at"),
        "nutrient_status": summary,
        "deficiency_count": len(deficiencies),
        "deficiencies": [d.to_dict() for d in deficiencies],
        "fertilizer_plan": plan,
        "indices": idx,
    }


@app.get("/api/v1/nutrients/types")
def list_nutrient_types():
    """قائمة أنواع العناصر الغذائية المدعومة"""
    return {
        "nutrient_types": [{"value": nt.value, "name": nt.name} for nt in NutrientType],
        "severity_levels": [{"value": ds.value, "name": ds.name} for ds in DeficiencySeverity],
        "macronutrients": [
            {"value": nt.value, "name_en": nt.name, "name_ar": _get_nutrient_name_ar(nt)}
            for nt in [
                NutrientType.NITROGEN,
                NutrientType.PHOSPHORUS,
                NutrientType.POTASSIUM,
                NutrientType.CALCIUM,
                NutrientType.MAGNESIUM,
                NutrientType.SULFUR,
            ]
        ],
        "micronutrients": [
            {"value": nt.value, "name_en": nt.name, "name_ar": _get_nutrient_name_ar(nt)}
            for nt in [
                NutrientType.IRON,
                NutrientType.ZINC,
                NutrientType.MANGANESE,
                NutrientType.COPPER,
                NutrientType.BORON,
                NutrientType.MOLYBDENUM,
            ]
        ],
    }


def _get_nutrient_name_ar(nutrient: NutrientType) -> str:
    """Get Arabic name for nutrient"""
    names = {
        NutrientType.NITROGEN: "نيتروجين",
        NutrientType.PHOSPHORUS: "فوسفور",
        NutrientType.POTASSIUM: "بوتاسيوم",
        NutrientType.CALCIUM: "كالسيوم",
        NutrientType.MAGNESIUM: "مغنيسيوم",
        NutrientType.SULFUR: "كبريت",
        NutrientType.IRON: "حديد",
        NutrientType.ZINC: "زنك",
        NutrientType.MANGANESE: "منجنيز",
        NutrientType.COPPER: "نحاس",
        NutrientType.BORON: "بورون",
        NutrientType.MOLYBDENUM: "موليبدنوم",
    }
    return names.get(nutrient, nutrient.value)


# ═══════════════════════════════════════════════════════════════════════════════
# Yield Prediction Endpoints
# نقاط نهاية تنبؤ المحصول
# ═══════════════════════════════════════════════════════════════════════════════


class YieldPredictionRequest(BaseModel):
    """طلب تنبؤ المحصول"""

    crop_type: str = Field(..., description="نوع المحصول")
    ndvi: float = Field(..., ge=-1, le=1)
    evi: float = Field(..., ge=-1, le=1)
    ndwi: float = Field(..., ge=-1, le=1)
    ndre: float = Field(..., ge=-1, le=1)
    lci: float = Field(..., ge=-1, le=1)
    savi: float = Field(..., ge=-1, le=1)
    field_area_hectares: float = Field(default=1.0, gt=0, description="مساحة الحقل بالهكتار")
    growth_stage_percent: float = Field(default=50.0, ge=0, le=100, description="نسبة مرحلة النمو")
    historical_yield_kg_ha: float | None = Field(default=None, description="المحصول التاريخي")


@app.post("/api/v1/yield/predict")
def predict_crop_yield(body: YieldPredictionRequest, current_user: User = Depends(get_current_user)):
    """تنبؤ المحصول من المؤشرات النباتية"""
    try:
        crop = YieldCropType(body.crop_type.lower())
    except ValueError:
        crop = YieldCropType.WHEAT

    prediction = predict_yield(
        crop_type=crop,
        ndvi=body.ndvi,
        evi=body.evi,
        ndwi=body.ndwi,
        ndre=body.ndre,
        lci=body.lci,
        savi=body.savi,
        field_area_hectares=body.field_area_hectares,
        growth_stage_percent=body.growth_stage_percent,
        historical_yield_kg_ha=body.historical_yield_kg_ha,
    )

    return {
        "prediction": prediction.to_dict(),
        "field_area_hectares": body.field_area_hectares,
        "total_predicted_yield_kg": round(prediction.predicted_yield_kg_ha * body.field_area_hectares),
        "input_indices": {
            "ndvi": body.ndvi,
            "evi": body.evi,
            "ndwi": body.ndwi,
            "ndre": body.ndre,
            "lci": body.lci,
            "savi": body.savi,
        },
    }


@app.post("/api/v1/fields/{field_id}/zones/{zone_id}/yield-prediction")
async def predict_zone_yield(
    field_id: str,
    zone_id: str,
    crop_type: str = Query(default="wheat", description="نوع المحصول"),
    field_area_hectares: float = Query(default=1.0, gt=0),
    growth_stage_percent: float = Query(default=50.0, ge=0, le=100),
    current_user: User = Depends(get_current_user),
):
    """تنبؤ محصول المنطقة من آخر رصد"""
    user_tenant_id = str(current_user.tenant_id) if getattr(current_user, "tenant_id", None) else None
    db_obs = await db_get_observations(field_id, zone_id, 1, tenant_id=user_tenant_id)
    if db_obs:
        obs_list = db_obs
    else:
        if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
            raise HTTPException(status_code=404, detail="Zone not found or no observations")
        obs_list = OBSERVATIONS[field_id][zone_id]

    if not obs_list:
        raise HTTPException(status_code=404, detail="No observations for this zone")

    latest = obs_list[-1]
    idx = latest["indices"]

    try:
        crop = YieldCropType(crop_type.lower())
    except ValueError:
        crop = YieldCropType.WHEAT

    prediction = predict_yield(
        crop_type=crop,
        ndvi=idx["ndvi"],
        evi=idx["evi"],
        ndwi=idx["ndwi"],
        ndre=idx["ndre"],
        lci=idx["lci"],
        savi=idx["savi"],
        field_area_hectares=field_area_hectares,
        growth_stage_percent=growth_stage_percent,
    )

    zone_metadata = await get_zones_data(field_id, tenant_id=user_tenant_id)
    zone_meta = zone_metadata.get(zone_id, {})

    return {
        "field_id": field_id,
        "zone_id": zone_id,
        "zone_name": zone_meta.get("name", zone_id),
        "observation_date": latest.get("captured_at"),
        "prediction": prediction.to_dict(),
        "indices": idx,
    }


@app.get("/api/v1/yield/crop-parameters")
def get_all_crop_parameters(crop_type: str | None = Query(default=None)):
    """الحصول على معاملات المحاصيل"""
    if crop_type:
        try:
            crop = YieldCropType(crop_type.lower())
            return get_crop_parameters(crop)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Unknown crop type: {crop_type}")

    return get_crop_parameters()


# ═══════════════════════════════════════════════════════════════════════════════
# Pest Risk Assessment Endpoints
# نقاط نهاية تقييم مخاطر الآفات
# ═══════════════════════════════════════════════════════════════════════════════


class PestAssessmentRequest(BaseModel):
    """طلب تقييم مخاطر الآفات"""

    temp_c: float = Field(..., ge=-50, le=60, description="الحرارة °م")
    humidity_pct: float = Field(..., ge=0, le=100, description="الرطوبة %")
    ndvi: float = Field(..., ge=-1, le=1, description="NDVI")
    crop_type: str = Field(default="general", description="نوع المحصول")
    season: str = Field(default="summer", description="الموسم")


@app.post("/api/v1/pests/assess")
def assess_pests(body: PestAssessmentRequest, current_user: User = Depends(get_current_user)):
    """تقييم مخاطر الآفات بناءً على الظروف البيئية"""
    risks = assess_pest_risks(
        temp_c=body.temp_c,
        humidity_pct=body.humidity_pct,
        ndvi=body.ndvi,
        crop_type=body.crop_type,
        season=body.season,
    )

    summary = get_pest_summary(risks)

    return {
        "pest_assessment": summary,
        "risks_count": len(risks),
        "risks": [r.to_dict() for r in risks],
        "environmental_conditions": {
            "temp_c": body.temp_c,
            "humidity_pct": body.humidity_pct,
            "ndvi": body.ndvi,
        },
    }


@app.post("/api/v1/fields/{field_id}/zones/{zone_id}/pest-assessment")
async def assess_zone_pests(
    field_id: str,
    zone_id: str,
    temp_c: float = Query(..., ge=-50, le=60),
    humidity_pct: float = Query(..., ge=0, le=100),
    crop_type: str = Query(default="general"),
    season: str = Query(default="summer"),
    current_user: User = Depends(get_current_user),
):
    """تقييم مخاطر الآفات في المنطقة"""
    user_tenant_id = str(current_user.tenant_id) if getattr(current_user, "tenant_id", None) else None
    db_obs = await db_get_observations(field_id, zone_id, 1, tenant_id=user_tenant_id)
    if db_obs:
        obs_list = db_obs
    else:
        if field_id not in OBSERVATIONS or zone_id not in OBSERVATIONS[field_id]:
            raise HTTPException(status_code=404, detail="Zone not found or no observations")
        obs_list = OBSERVATIONS[field_id][zone_id]

    if not obs_list:
        raise HTTPException(status_code=404, detail="No observations for this zone")

    latest = obs_list[-1]
    idx = latest["indices"]

    risks = assess_pest_risks(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        ndvi=idx["ndvi"],
        crop_type=crop_type,
        season=season,
    )

    summary = get_pest_summary(risks)
    zone_metadata = await get_zones_data(field_id, tenant_id=user_tenant_id)
    zone_meta = zone_metadata.get(zone_id, {})

    return {
        "field_id": field_id,
        "zone_id": zone_id,
        "zone_name": zone_meta.get("name", zone_id),
        "observation_date": latest.get("captured_at"),
        "pest_assessment": summary,
        "risks_count": len(risks),
        "risks": [r.to_dict() for r in risks],
        "indices": idx,
    }


@app.get("/api/v1/pests/types")
def list_pest_types():
    """قائمة أنواع الآفات المدعومة"""
    return {
        "pest_types": get_pest_types(),
        "risk_levels": [{"value": rl.value, "name": rl.name} for rl in RiskLevel],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Comprehensive Analysis Endpoint
# نقطة نهاية التحليل الشامل
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/api/v1/comprehensive-analysis")
async def comprehensive_analysis(
    ndvi: float = Query(..., ge=-1, le=1),
    evi: float = Query(..., ge=-1, le=1),
    ndre: float = Query(..., ge=-1, le=1),
    ndwi: float = Query(..., ge=-1, le=1),
    lci: float = Query(..., ge=-1, le=1),
    savi: float = Query(..., ge=-1, le=1),
    crop_type: str = Query(default="wheat"),
    temp_c: float = Query(default=25, ge=-50, le=60),
    humidity_pct: float = Query(default=50, ge=0, le=100),
    field_area_hectares: float = Query(default=1.0, gt=0),
    field_id: str | None = Query(default=None, description="Optional field ID for event publishing"),
    tenant_id: str | None = Query(
        default=None, description="Tenant ID for scoped events | معرف المستأجر للأحداث المعزولة"
    ),
    current_user: User = Depends(get_current_user),
):
    """تحليل شامل للحقل"""
    try:
        yield_crop = YieldCropType(crop_type.lower())
    except ValueError:
        yield_crop = YieldCropType.WHEAT

    try:
        disease_crop = CropType(crop_type.lower())
    except ValueError:
        disease_crop = CropType.UNKNOWN

    diseases = detect_diseases(
        ndvi=ndvi,
        evi=evi,
        ndre=ndre,
        ndwi=ndwi,
        lci=lci,
        savi=savi,
        crop_type=disease_crop,
        humidity_pct=humidity_pct,
        temp_c=temp_c,
    )
    health_en, health_ar = get_overall_health_status(diseases)

    deficiencies = detect_nutrient_deficiencies(
        ndvi=ndvi,
        evi=evi,
        ndre=ndre,
        ndwi=ndwi,
        lci=lci,
        savi=savi,
    )
    nutrient_summary = get_nutrient_status_summary(deficiencies)

    yield_pred = predict_yield(
        crop_type=yield_crop,
        ndvi=ndvi,
        evi=evi,
        ndwi=ndwi,
        ndre=ndre,
        lci=lci,
        savi=savi,
        field_area_hectares=field_area_hectares,
    )

    pest_risks = assess_pest_risks(
        temp_c=temp_c,
        humidity_pct=humidity_pct,
        ndvi=ndvi,
        crop_type=crop_type,
    )
    pest_summary = get_pest_summary(pest_risks)

    if health_en in ["critical", "poor"] or nutrient_summary["overall_status_en"] == "Critical":
        overall_status = "critical"
    elif health_en == "fair" or nutrient_summary["overall_status_en"] == "Deficient":
        overall_status = "warning"
    else:
        overall_status = "good"

    if field_id:
        # Publish events with tenant isolation | نشر الأحداث مع عزل المستأجر
        if diseases:
            for disease in diseases:
                await publish_disease_detected(
                    field_id=field_id,
                    disease=disease.disease_type.value,
                    confidence=disease.confidence,
                    severity=disease.severity.value if disease.severity else None,
                    tenant_id=tenant_id,
                )

        all_issues = []
        all_issues.extend([d.disease_type.value for d in diseases])
        all_issues.extend([d.nutrient.value for d in deficiencies])
        all_issues.extend([r.pest_type for r in pest_risks if r.risk_level.value in ["high", "critical"]])

        await publish_health_assessed(
            field_id=field_id,
            health_score=overall_status,
            health_score_ar=health_ar,
            issues=all_issues,
            tenant_id=tenant_id,
        )

    return {
        "overall_status": overall_status,
        "crop_type": crop_type,
        "field_area_hectares": field_area_hectares,
        "health_assessment": {
            "status_en": health_en,
            "status_ar": health_ar,
            "disease_count": len(diseases),
            "diseases": [d.to_dict() for d in diseases[:3]],
        },
        "nutrient_assessment": {
            **nutrient_summary,
            "deficiency_count": len(deficiencies),
            "deficiencies": [d.to_dict() for d in deficiencies[:3]],
        },
        "yield_prediction": yield_pred.to_dict(),
        "pest_assessment": {
            **pest_summary,
            "risks": [r.to_dict() for r in pest_risks[:3]],
        },
        "input_indices": {
            "ndvi": ndvi,
            "evi": evi,
            "ndre": ndre,
            "ndwi": ndwi,
            "lci": lci,
            "savi": savi,
        },
        "environmental_context": {
            "temp_c": temp_c,
            "humidity_pct": humidity_pct,
        },
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")  # noqa: S104 -- bind all interfaces for Docker  # nosec B104 - binding to all interfaces required for Docker container
    port = int(os.getenv("PORT", 8095))
    uvicorn.run(app, host=host, port=port)
