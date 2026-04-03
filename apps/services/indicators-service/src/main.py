"""
📊 SAHOOL Agricultural Indicators Service v16.0
خدمة المؤشرات الزراعية - Dashboard & Analytics
"""

import json
import os
import re
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta, timezone
from enum import Enum, StrEnum
from typing import Any

import asyncpg
import nats
import structlog
from fastapi import Depends, FastAPI, HTTPException, Query

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel, field_validator

from shared.errors_py import add_request_id_middleware, setup_exception_handlers
from shared.middleware.tenant_context import TenantContextMiddleware

try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:  # type: ignore[no-redef]
        tenant_id: str | None = None
        roles: list[str] = []

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


def _enforce_tenant(user: Any, requested_tenant_id: str) -> None:
    """Validate JWT tenant matches the requested tenant - فرض عزل المستأجر."""
    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "authentication_required",
                "message_ar": "المصادقة مطلوبة",
                "message_en": "Authentication required",
            },
        )
    user_tenant = getattr(user, "tenant_id", None)
    if user_tenant and user_tenant != requested_tenant_id:
        # Admin users can access any tenant
        user_roles = getattr(user, "roles", []) or []
        if "admin" not in user_roles and "super_admin" not in user_roles:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "tenant_mismatch",
                    "message_ar": "لا يمكنك الوصول إلى بيانات مستأجر آخر",
                    "message_en": "Cannot access another tenant's data",
                },
            )


# Prometheus metrics
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

# Prometheus metric definitions
if HAS_PROMETHEUS:
    REQUEST_COUNT = Counter(
        "indicators_requests_total",
        "Total indicators API requests",
        ["endpoint", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "indicators_request_duration_seconds",
        "Indicators API request latency",
        ["endpoint"],
    )

# Prometheus middleware to record metrics per request
if HAS_PROMETHEUS:
    from starlette.middleware.base import BaseHTTPMiddleware

    class PrometheusMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            import time as _time

            endpoint = request.url.path
            start = _time.time()
            response = await call_next(request)
            duration = _time.time() - start
            REQUEST_COUNT.labels(endpoint=endpoint, status=response.status_code).inc()
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
            return response


logger = structlog.get_logger()

# Field ID validation: alphanumeric, hyphens, underscores; 1-100 chars
_FIELD_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,100}$")


def _validate_field_id(field_id: str) -> None:
    """Validate field_id format - must be non-empty, max 100 chars, alphanumeric/hyphens/underscores."""
    if not field_id or not _FIELD_ID_RE.match(field_id):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_field_id",
                "message_ar": "معرّف الحقل غير صالح: يجب أن يكون من 1 إلى 100 حرف (أحرف وأرقام وشرطات فقط)",
                "message_en": "Invalid field_id: must be 1-100 characters (alphanumeric, hyphens, underscores only)",
            },
        )


def _validate_tenant_id(tenant_id: str | None) -> None:
    """Validate tenant_id if provided - must be non-empty, max 255 chars."""
    if tenant_id is not None:
        if not tenant_id or not tenant_id.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_tenant_id",
                    "message_ar": "معرّف المستأجر لا يمكن أن يكون فارغًا",
                    "message_en": "Tenant ID cannot be empty",
                },
            )
        if len(tenant_id) > 255:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_tenant_id",
                    "message_ar": "معرّف المستأجر طويل جدًا (الحد الأقصى 255 حرفًا)",
                    "message_en": "Tenant ID too long (max 255 characters)",
                },
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    # Database connection
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            import asyncpg

            # Validate SSL mode is present in DATABASE_URL for security
            ssl_mode = os.getenv("POSTGRES_SSL_MODE", "disable")
            if ssl_mode != "disable" and "sslmode=" not in db_url:
                db_url = f"{db_url}{'&' if '?' in db_url else '?'}sslmode={ssl_mode}"

            app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
            logger.info("database_connected", pool_size=10, ssl_mode=ssl_mode)
        except Exception as e:
            logger.warning("database_connection_failed", error=str(e))
            app.state.db_pool = None
    else:
        app.state.db_pool = None
        logger.info("database_not_configured")

    # NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats as nats_lib

            app.state.nc = await nats_lib.connect(nats_url)
            logger.info("nats_connected")
        except Exception as e:
            logger.warning("nats_connection_failed", error=str(e))
            app.state.nc = None
    else:
        app.state.nc = None

    # Subscribe to NATS events
    if app.state.nc:
        # Subscribe to field events
        async def handle_field_created(msg):
            try:
                data = json.loads(msg.data.decode())
                tenant_id = data.get("tenant_id")
                field_id = data.get("field_id")
                logger.info("field_created_event_received", field_id=field_id, tenant_id=tenant_id)
                # Initialize default indicators for new field
                # Validate IDs to prevent storing malformed/spoofed values
                if (
                    field_id
                    and tenant_id
                    and _FIELD_ID_RE.match(field_id)
                    and len(tenant_id) <= 255
                    and app.state.db_pool
                ):
                    default_indicators = {
                        "ndvi": 0.0,
                        "evi": 0.0,
                        "lai": 0.0,
                        "ndwi": 0.0,
                        "soil_moisture": 0.0,
                        "irrigation_efficiency": 0.0,
                        "soil_ph": 7.0,
                        "nitrogen_level": 0.0,
                    }
                    for ind_type, default_value in default_indicators.items():
                        defn = INDICATOR_DEFINITIONS.get(ind_type)
                        if not defn:
                            continue
                        status = determine_status(
                            default_value,
                            defn.get("optimal_min", defn["min"]),
                            defn.get("optimal_max", defn["max"]),
                            defn["min"],
                            defn["max"],
                        )
                        indicator_data = {
                            "value": default_value,
                            "trend": TrendDirection.STABLE.value,
                            "trend_percent": 0.0,
                            "status": status,
                        }
                        await save_indicator(field_id, ind_type, indicator_data, tenant_id)
                    logger.info(
                        "default_indicators_initialized", field_id=field_id, indicator_count=len(default_indicators)
                    )
            except Exception as e:
                logger.error("event_handler_failed", subject="field.created", error=str(e))

        async def handle_ndvi_calculated(msg):
            try:
                data = json.loads(msg.data.decode())
                tenant_id = data.get("tenant_id")
                field_id = data.get("field_id")
                logger.info("ndvi_calculated_received", field_id=field_id, tenant_id=tenant_id)
                # Update NDVI indicator for field
                ndvi_value = data.get("ndvi_value") or data.get("value") or data.get("mean_ndvi")
                if (
                    field_id
                    and tenant_id
                    and _FIELD_ID_RE.match(field_id)
                    and len(tenant_id) <= 255
                    and ndvi_value is not None
                    and app.state.db_pool
                ):
                    ndvi_value = float(ndvi_value)
                    defn = INDICATOR_DEFINITIONS["ndvi"]
                    status = determine_status(
                        ndvi_value,
                        defn["optimal_min"],
                        defn["optimal_max"],
                        defn["min"],
                        defn["max"],
                    )
                    # Check previous value for trend calculation
                    previous = await get_indicator(field_id, "ndvi", tenant_id)
                    trend = TrendDirection.STABLE
                    trend_percent = 0.0
                    if previous and previous.get("value") is not None:
                        prev_val = float(previous["value"])
                        if prev_val != 0:
                            trend_percent = round(((ndvi_value - prev_val) / abs(prev_val)) * 100, 2)
                        if ndvi_value > prev_val:
                            trend = TrendDirection.UP
                        elif ndvi_value < prev_val:
                            trend = TrendDirection.DOWN
                    indicator_data = {
                        "value": ndvi_value,
                        "trend": trend.value,
                        "trend_percent": trend_percent,
                        "status": status,
                    }
                    await save_indicator(field_id, "ndvi", indicator_data, tenant_id)
                    logger.info("ndvi_indicator_updated", field_id=field_id, ndvi_value=ndvi_value, status=status)
            except Exception as e:
                logger.error("event_handler_failed", subject="ndvi.calculated", error=str(e))

        await app.state.nc.subscribe("sahool.field.created", cb=handle_field_created)
        await app.state.nc.subscribe("sahool.satellite.ndvi.computed", cb=handle_ndvi_calculated)
        logger.info("nats_subscriptions_registered", count=2)

    yield

    # Cleanup
    if getattr(app.state, "db_pool", None):
        await app.state.db_pool.close()
    if getattr(app.state, "nc", None):
        await app.state.nc.close()


app = FastAPI(
    title="SAHOOL Agricultural Indicators | خدمة المؤشرات الزراعية",
    version="16.0.0",
    description="Comprehensive agricultural indicators dashboard - KPIs, trends, alerts",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)
app.add_middleware(TenantContextMiddleware)

# Prometheus request metrics middleware
if HAS_PROMETHEUS:
    app.add_middleware(PrometheusMiddleware)


async def publish_event(subject: str, data: dict, tenant_id: str | None = None):
    """Publish event to NATS if connected, using tenant-scoped subject when available.

    Uses tenant-scoped subject when tenant_id is provided for multi-tenant isolation.
    يستخدم موضوع مخصص للمستأجر عند توفر معرف المستأجر لعزل البيانات.

    Args:
        subject: Base NATS subject (e.g., "sahool.indicators.computed")
        data: Event payload dictionary
        tenant_id: Optional tenant ID; when provided, subject becomes
                   sahool.tenant.{tenant_id}.indicators.{action}
    """
    # Resolve tenant-scoped subject | تحويل الموضوع إلى نطاق المستأجر
    if tenant_id:
        from shared.events.subjects import get_tenant_subject

        # Extract domain and action from subject like "sahool.indicators.computed"
        parts = subject.split(".", 2)  # ["sahool", "indicators", "computed"]
        if len(parts) >= 3:
            domain = parts[1]
            action = parts[2]
            subject = get_tenant_subject(tenant_id, domain, action)

    if hasattr(app.state, "nc") and app.state.nc:
        try:
            await app.state.nc.publish(subject, json.dumps(data).encode())
            logger.debug("Published event", subject=subject, data=data)
        except Exception as e:
            logger.warning("Failed to publish event", subject=subject, error=str(e))


# =============================================================================
# Database Helper Functions
# =============================================================================


async def save_indicator(field_id: str, indicator_type: str, value: dict, tenant_id: str | None = None) -> bool:
    """Save indicator value to database.

    Args:
        field_id: The field identifier
        indicator_type: Type of indicator (e.g., 'ndvi', 'soil_moisture')
        value: Dictionary containing indicator data
        tenant_id: Optional tenant identifier

    Returns:
        True if saved successfully, False otherwise
    """
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        try:
            async with app.state.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO field_indicators (field_id, indicator_type, value, tenant_id)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (tenant_id, field_id, indicator_type)
                    DO UPDATE SET value = $3, calculated_at = NOW()
                """,
                    field_id,
                    indicator_type,
                    json.dumps(value),
                    tenant_id,
                )
            logger.debug("Saved indicator", field_id=field_id, indicator_type=indicator_type)
            return True
        except Exception as e:
            logger.warning(
                "Failed to save indicator",
                field_id=field_id,
                indicator_type=indicator_type,
                error=str(e),
            )
            return False
    return False


async def get_indicator(field_id: str, indicator_type: str, tenant_id: str | None = None) -> dict | None:
    """Retrieve indicator value from database.

    Args:
        field_id: The field identifier
        indicator_type: Type of indicator
        tenant_id: Optional tenant identifier for isolation

    Returns:
        Indicator data dictionary or None if not found
    """
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        try:
            async with app.state.db_pool.acquire() as conn:
                if tenant_id:
                    sql = "SELECT value, calculated_at FROM field_indicators WHERE field_id = $1 AND indicator_type = $2 AND tenant_id = $3"
                    row = await conn.fetchrow(sql, field_id, indicator_type, tenant_id)
                else:
                    sql = (
                        "SELECT value, calculated_at FROM field_indicators WHERE field_id = $1 AND indicator_type = $2"
                    )
                    row = await conn.fetchrow(sql, field_id, indicator_type)
                if row:
                    try:
                        data = json.loads(row["value"])
                    except (json.JSONDecodeError, TypeError):
                        logger.warning("corrupted_indicator_data", row_id=str(row.get("id", "")), field_id=field_id)
                        return None
                    data["calculated_at"] = row["calculated_at"].isoformat()
                    return data
        except Exception as e:
            logger.warning(
                "Failed to get indicator",
                field_id=field_id,
                indicator_type=indicator_type,
                error=str(e),
            )
    return None


async def get_all_field_indicators(field_id: str, tenant_id: str | None = None) -> list[dict]:
    """Retrieve all indicators for a field from database.

    Args:
        field_id: The field identifier
        tenant_id: Optional tenant identifier for isolation

    Returns:
        List of indicator data dictionaries
    """
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        try:
            async with app.state.db_pool.acquire() as conn:
                if tenant_id:
                    sql = """
                        SELECT indicator_type, value, calculated_at FROM field_indicators
                        WHERE field_id = $1 AND tenant_id = $2
                        ORDER BY indicator_type
                    """
                    rows = await conn.fetch(sql, field_id, tenant_id)
                else:
                    sql = """
                        SELECT indicator_type, value, calculated_at FROM field_indicators
                        WHERE field_id = $1
                        ORDER BY indicator_type
                    """
                    rows = await conn.fetch(sql, field_id)
                result = []
                for row in rows:
                    try:
                        data = json.loads(row["value"])
                    except (json.JSONDecodeError, TypeError):
                        logger.warning("corrupted_indicator_data", row_id=str(row.get("id", "")), field_id=field_id)
                        continue
                    data["indicator_type"] = row["indicator_type"]
                    data["calculated_at"] = row["calculated_at"].isoformat()
                    result.append(data)
                return result
        except Exception as e:
            logger.warning("Failed to get field indicators", field_id=field_id, error=str(e))
    return []


async def get_tenant_indicators(tenant_id: str, limit: int = 100) -> list[dict]:
    """Retrieve all indicators for a tenant from database.

    Args:
        tenant_id: The tenant identifier
        limit: Maximum number of records to return

    Returns:
        List of indicator data dictionaries
    """
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        try:
            async with app.state.db_pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT field_id, indicator_type, value, calculated_at
                    FROM field_indicators
                    WHERE tenant_id = $1
                    ORDER BY calculated_at DESC
                    LIMIT $2
                """,
                    tenant_id,
                    limit,
                )
                result = []
                for row in rows:
                    try:
                        data = json.loads(row["value"])
                    except (json.JSONDecodeError, TypeError):
                        logger.warning("corrupted_indicator_data", row_id=str(row.get("id", "")))
                        continue
                    data["field_id"] = row["field_id"]
                    data["indicator_type"] = row["indicator_type"]
                    data["calculated_at"] = row["calculated_at"].isoformat()
                    result.append(data)
                return result
        except Exception as e:
            logger.warning("Failed to get tenant indicators", tenant_id=tenant_id, error=str(e))
    return []


async def delete_field_indicators(field_id: str, tenant_id: str) -> bool:
    """Delete all indicators for a field, scoped to tenant.

    Args:
        field_id: The field identifier
        tenant_id: Tenant ID for isolation (required)

    Returns:
        True if deleted successfully, False otherwise
    """
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        try:
            async with app.state.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    DELETE FROM field_indicators WHERE field_id = $1 AND tenant_id = $2
                """,
                    field_id,
                    tenant_id,
                )
            logger.info("Deleted field indicators", field_id=field_id, tenant_id=tenant_id)
            return True
        except Exception as e:
            logger.warning("Failed to delete field indicators", field_id=field_id, tenant_id=tenant_id, error=str(e))
            return False
    return False


# =============================================================================
# Enums & Models
# =============================================================================


class IndicatorCategory(StrEnum):
    VEGETATION = "vegetation"
    WATER = "water"
    SOIL = "soil"
    WEATHER = "weather"
    CROP_HEALTH = "crop_health"
    PRODUCTIVITY = "productivity"
    FINANCIAL = "financial"


class TrendDirection(StrEnum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Indicator(BaseModel):
    id: str
    name_ar: str
    name_en: str
    category: IndicatorCategory
    value: float
    unit: str
    min_value: float
    max_value: float
    optimal_min: float
    optimal_max: float
    trend: TrendDirection
    trend_percent: float
    status: str  # optimal, warning, critical
    last_updated: datetime


class FieldIndicators(BaseModel):
    field_id: str
    field_name: str
    area_hectares: float
    crop_type: str
    indicators: list[Indicator]
    overall_score: float
    alerts: list[dict[str, Any]]


class DashboardSummary(BaseModel):
    tenant_id: str
    total_fields: int
    total_area_hectares: float
    average_health_score: float
    indicators_summary: dict[str, Any]
    active_alerts: int
    critical_alerts: int
    top_performing_fields: list[dict[str, Any]]
    attention_needed_fields: list[dict[str, Any]]
    generated_at: datetime


class IndicatorAlert(BaseModel):
    alert_id: str
    field_id: str
    indicator_id: str
    indicator_name_ar: str
    severity: AlertSeverity
    message_ar: str
    message_en: str
    current_value: float
    threshold_value: float
    recommended_action_ar: str
    recommended_action_en: str
    created_at: datetime


# =============================================================================
# Indicator Definitions
# =============================================================================

INDICATOR_DEFINITIONS = {
    # Vegetation Indicators
    "ndvi": {
        "name_ar": "مؤشر الغطاء النباتي",
        "name_en": "NDVI",
        "category": IndicatorCategory.VEGETATION,
        "unit": "index",
        "min": -1.0,
        "max": 1.0,
        "optimal_min": 0.4,
        "optimal_max": 0.8,
    },
    "evi": {
        "name_ar": "مؤشر النباتات المحسن",
        "name_en": "Enhanced Vegetation Index",
        "category": IndicatorCategory.VEGETATION,
        "unit": "index",
        "min": -1.0,
        "max": 1.0,
        "optimal_min": 0.3,
        "optimal_max": 0.7,
    },
    "lai": {
        "name_ar": "مؤشر مساحة الأوراق",
        "name_en": "Leaf Area Index",
        "category": IndicatorCategory.VEGETATION,
        "unit": "m²/m²",
        "min": 0,
        "max": 8,
        "optimal_min": 2.5,
        "optimal_max": 5.0,
    },
    # Water Indicators
    "ndwi": {
        "name_ar": "مؤشر المياه",
        "name_en": "Water Index",
        "category": IndicatorCategory.WATER,
        "unit": "index",
        "min": -1.0,
        "max": 1.0,
        "optimal_min": 0.0,
        "optimal_max": 0.4,
    },
    "soil_moisture": {
        "name_ar": "رطوبة التربة",
        "name_en": "Soil Moisture",
        "category": IndicatorCategory.WATER,
        "unit": "%",
        "min": 0,
        "max": 100,
        "optimal_min": 40,
        "optimal_max": 70,
    },
    "irrigation_efficiency": {
        "name_ar": "كفاءة الري",
        "name_en": "Irrigation Efficiency",
        "category": IndicatorCategory.WATER,
        "unit": "%",
        "min": 0,
        "max": 100,
        "optimal_min": 75,
        "optimal_max": 95,
    },
    # Soil Indicators
    "soil_ph": {
        "name_ar": "حموضة التربة",
        "name_en": "Soil pH",
        "category": IndicatorCategory.SOIL,
        "unit": "pH",
        "min": 0,
        "max": 14,
        "optimal_min": 6.0,
        "optimal_max": 7.5,
    },
    "nitrogen_level": {
        "name_ar": "مستوى النيتروجين",
        "name_en": "Nitrogen Level",
        "category": IndicatorCategory.SOIL,
        "unit": "kg/ha",
        "min": 0,
        "max": 300,
        "optimal_min": 80,
        "optimal_max": 150,
    },
    "phosphorus_level": {
        "name_ar": "مستوى الفوسفور",
        "name_en": "Phosphorus Level",
        "category": IndicatorCategory.SOIL,
        "unit": "kg/ha",
        "min": 0,
        "max": 200,
        "optimal_min": 30,
        "optimal_max": 80,
    },
    "potassium_level": {
        "name_ar": "مستوى البوتاسيوم",
        "name_en": "Potassium Level",
        "category": IndicatorCategory.SOIL,
        "unit": "kg/ha",
        "min": 0,
        "max": 400,
        "optimal_min": 100,
        "optimal_max": 250,
    },
    # Weather Indicators
    "temperature": {
        "name_ar": "درجة الحرارة",
        "name_en": "Temperature",
        "category": IndicatorCategory.WEATHER,
        "unit": "°C",
        "min": -10,
        "max": 50,
        "optimal_min": 20,
        "optimal_max": 32,
    },
    "humidity": {
        "name_ar": "الرطوبة النسبية",
        "name_en": "Relative Humidity",
        "category": IndicatorCategory.WEATHER,
        "unit": "%",
        "min": 0,
        "max": 100,
        "optimal_min": 50,
        "optimal_max": 75,
    },
    "rainfall": {
        "name_ar": "هطول الأمطار",
        "name_en": "Rainfall",
        "category": IndicatorCategory.WEATHER,
        "unit": "mm",
        "min": 0,
        "max": 500,
        "optimal_min": 20,
        "optimal_max": 100,
    },
    # Crop Health Indicators
    "disease_risk": {
        "name_ar": "خطر الأمراض",
        "name_en": "Disease Risk",
        "category": IndicatorCategory.CROP_HEALTH,
        "unit": "%",
        "min": 0,
        "max": 100,
        "optimal_min": 0,
        "optimal_max": 20,
    },
    "pest_pressure": {
        "name_ar": "ضغط الآفات",
        "name_en": "Pest Pressure",
        "category": IndicatorCategory.CROP_HEALTH,
        "unit": "index",
        "min": 0,
        "max": 10,
        "optimal_min": 0,
        "optimal_max": 2,
    },
    "growth_rate": {
        "name_ar": "معدل النمو",
        "name_en": "Growth Rate",
        "category": IndicatorCategory.CROP_HEALTH,
        "unit": "cm/week",
        "min": 0,
        "max": 30,
        "optimal_min": 5,
        "optimal_max": 15,
    },
    # Productivity Indicators
    "yield_estimate": {
        "name_ar": "تقدير المحصول",
        "name_en": "Yield Estimate",
        "category": IndicatorCategory.PRODUCTIVITY,
        "unit": "kg/ha",
        "min": 0,
        "max": 50000,
        "optimal_min": 15000,
        "optimal_max": 35000,
    },
    "crop_stage_progress": {
        "name_ar": "تقدم مرحلة المحصول",
        "name_en": "Crop Stage Progress",
        "category": IndicatorCategory.PRODUCTIVITY,
        "unit": "%",
        "min": 0,
        "max": 100,
        "optimal_min": 0.0,
        "optimal_max": 100.0,  # Depends on expected timing
    },
    # Financial Indicators
    "cost_per_hectare": {
        "name_ar": "التكلفة لكل هكتار",
        "name_en": "Cost per Hectare",
        "category": IndicatorCategory.FINANCIAL,
        "unit": "YER",
        "min": 0,
        "max": 1000000,
        "optimal_min": 50000,
        "optimal_max": 200000,
    },
    "roi_estimate": {
        "name_ar": "العائد المتوقع",
        "name_en": "ROI Estimate",
        "category": IndicatorCategory.FINANCIAL,
        "unit": "%",
        "min": -100,
        "max": 500,
        "optimal_min": 50,
        "optimal_max": 200,
    },
}


# =============================================================================
# Helper Functions
# =============================================================================


def determine_status(value: float, optimal_min: float, optimal_max: float, min_val: float, max_val: float) -> str:
    """Determine indicator status based on value and thresholds"""
    if optimal_min is None or optimal_max is None:
        return "info"

    if optimal_min <= value <= optimal_max:
        return "optimal"
    elif value < optimal_min:
        distance = (optimal_min - value) / (optimal_min - min_val) if optimal_min != min_val else 0
        return "critical" if distance > 0.5 else "warning"
    else:  # value > optimal_max
        distance = (value - optimal_max) / (max_val - optimal_max) if max_val != optimal_max else 0
        return "critical" if distance > 0.5 else "warning"


def generate_indicator_value(definition: dict, base_health: float = 0.7) -> tuple[float, TrendDirection, float]:
    """Generate realistic indicator value based on definition and base health"""
    import random

    min_v = definition["min"]
    max_v = definition["max"]
    opt_min = definition.get("optimal_min", min_v)
    opt_max = definition.get("optimal_max", max_v)

    if opt_min is None:
        opt_min = min_v
    if opt_max is None:
        opt_max = max_v

    # Generate value influenced by base health
    optimal_mid = (opt_min + opt_max) / 2
    range_width = (opt_max - opt_min) / 2

    # Higher base_health means closer to optimal
    noise = random.gauss(0, range_width * (1.5 - base_health))
    value = optimal_mid + noise

    # Clamp to valid range
    value = max(min_v, min(max_v, value))

    # Generate trend
    trend_options = [TrendDirection.UP, TrendDirection.DOWN, TrendDirection.STABLE]
    weights = [0.4, 0.3, 0.3] if base_health > 0.6 else [0.2, 0.5, 0.3]
    trend = random.choices(trend_options, weights=weights)[0]
    trend_percent = random.uniform(0, 15) if trend != TrendDirection.STABLE else random.uniform(0, 3)

    return round(value, 2), trend, round(trend_percent, 1)


def create_alert_if_needed(indicator: Indicator, field_id: str) -> IndicatorAlert | None:
    """Create alert if indicator is in warning or critical state"""
    if indicator.status == "optimal":
        return None

    severity = AlertSeverity.CRITICAL if indicator.status == "critical" else AlertSeverity.WARNING

    # Find the threshold that was exceeded
    defn = INDICATOR_DEFINITIONS.get(indicator.id)
    if not defn:
        return None

    if indicator.value < defn["optimal_min"]:
        threshold = defn["optimal_min"]
        direction_ar = "أقل من"
        direction_en = "below"
    else:
        threshold = defn["optimal_max"]
        direction_ar = "أعلى من"
        direction_en = "above"

    return IndicatorAlert(
        alert_id=str(uuid.uuid4()),
        field_id=field_id,
        indicator_id=indicator.id,
        indicator_name_ar=indicator.name_ar,
        severity=severity,
        message_ar=f"{indicator.name_ar}: القيمة الحالية ({indicator.value} {indicator.unit}) {direction_ar} الحد المثالي ({threshold})",
        message_en=f"{indicator.name_en}: Current value ({indicator.value} {indicator.unit}) is {direction_en} optimal threshold ({threshold})",
        current_value=indicator.value,
        threshold_value=threshold,
        recommended_action_ar=get_recommendation_ar(indicator.id, indicator.value, threshold),
        recommended_action_en=get_recommendation_en(indicator.id, indicator.value, threshold),
        created_at=datetime.now(UTC),
    )


def get_recommendation_ar(indicator_id: str, value: float, threshold: float) -> str:
    """Get Arabic recommendation based on indicator"""
    recommendations = {
        "ndvi": "فحص صحة النباتات وزيادة التسميد إذا لزم الأمر",
        "soil_moisture": "تعديل جدول الري حسب مستوى الرطوبة",
        "nitrogen_level": "إضافة سماد نيتروجيني أو تقليله حسب المستوى",
        "disease_risk": "رش مبيدات وقائية ومراقبة الأعراض",
        "temperature": "توفير ظل للمحاصيل أو تحسين التهوية",
        "irrigation_efficiency": "فحص نظام الري وإصلاح التسريبات",
    }
    return recommendations.get(indicator_id, "مراجعة حالة الحقل واتخاذ الإجراء المناسب")


def get_recommendation_en(indicator_id: str, value: float, threshold: float) -> str:
    """Get English recommendation based on indicator"""
    recommendations = {
        "ndvi": "Inspect plant health and increase fertilization if needed",
        "soil_moisture": "Adjust irrigation schedule based on moisture level",
        "nitrogen_level": "Add or reduce nitrogen fertilizer based on level",
        "disease_risk": "Apply preventive pesticides and monitor symptoms",
        "temperature": "Provide shade for crops or improve ventilation",
        "irrigation_efficiency": "Check irrigation system and fix leaks",
    }
    return recommendations.get(indicator_id, "Review field condition and take appropriate action")


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/healthz")
def health():
    """Health check endpoint (liveness probe)"""
    return {
        "status": "ok",
        "service": "indicators-service",
        "version": "16.0.0",
    }


@app.get("/readyz")
async def readiness():
    """Kubernetes readiness probe - is the service ready to accept traffic?"""
    checks = {}
    db_pool = getattr(app.state, "db_pool", None)
    if db_pool:
        try:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            checks["database"] = "connected"
        except Exception:
            checks["database"] = "disconnected"
    else:
        checks["database"] = "not_configured"

    nc = getattr(app.state, "nc", None)
    checks["nats"] = "connected" if nc and not nc.is_closed else "not_configured"

    all_ready = all(v != "disconnected" for v in checks.values())
    return {
        "status": "ready" if all_ready else "degraded",
        "service": "indicators-service",
        "version": "16.0.0",
        "checks": checks,
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if not HAS_PROMETHEUS:
        from starlette.responses import Response

        return Response(content="prometheus_client not installed", status_code=501)
    from starlette.responses import Response

    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/v1/indicators/definitions")
def get_indicator_definitions():
    """الحصول على تعريفات جميع المؤشرات"""
    return {
        "indicators": [
            {
                "id": ind_id,
                "name_ar": defn["name_ar"],
                "name_en": defn["name_en"],
                "category": defn["category"].value,
                "unit": defn["unit"],
                "range": {"min": defn["min"], "max": defn["max"]},
                "optimal_range": {
                    "min": defn["optimal_min"],
                    "max": defn["optimal_max"],
                },
            }
            for ind_id, defn in INDICATOR_DEFINITIONS.items()
        ],
        "categories": [cat.value for cat in IndicatorCategory],
    }


@app.get("/v1/field/{field_id}/indicators", response_model=FieldIndicators)
async def get_field_indicators(
    field_id: str,
    category: IndicatorCategory | None = None,
    force_refresh: bool = False,
    user: Any = Depends(get_current_user),
):
    """الحصول على مؤشرات حقل معين

    Args:
        field_id: Field identifier
        category: Optional category filter
        force_refresh: If True, regenerate indicators even if cached
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", None) or ""
    _enforce_tenant(user, tenant_id)
    import random

    indicators = []
    alerts = []
    timestamp = datetime.now(UTC).isoformat()

    # Try to load existing indicators from database
    stored_indicators = await get_all_field_indicators(field_id, tenant_id=tenant_id) if not force_refresh else []
    stored_map = {ind["indicator_type"]: ind for ind in stored_indicators}

    # Check if we have fresh data (less than 1 hour old)
    use_stored = False
    if stored_indicators and not force_refresh:
        try:
            first_calc = datetime.fromisoformat(stored_indicators[0].get("calculated_at", "").replace("Z", "+00:00"))
            age = datetime.now(UTC).replace(tzinfo=first_calc.tzinfo) - first_calc
            use_stored = age.total_seconds() < 3600  # Use if less than 1 hour old
        except (ValueError, TypeError):
            use_stored = False

    # Generate base health for new indicators
    base_health = random.uniform(0.5, 0.9)

    for ind_id, defn in INDICATOR_DEFINITIONS.items():
        if category and defn["category"] != category:
            continue

        # Check if we have stored data for this indicator
        if use_stored and ind_id in stored_map:
            stored = stored_map[ind_id]
            value = stored.get("value", 0)
            trend = TrendDirection(stored.get("trend", "stable"))
            trend_percent = stored.get("trend_percent", 0)
            status = stored.get("status", "info")
            last_updated = datetime.fromisoformat(
                stored.get("calculated_at", timestamp).replace("Z", "+00:00")
            ).replace(tzinfo=None)
        else:
            # Generate new indicator value
            value, trend, trend_percent = generate_indicator_value(defn, base_health)
            status = determine_status(
                value,
                defn.get("optimal_min"),
                defn.get("optimal_max"),
                defn["min"],
                defn["max"],
            )
            last_updated = datetime.now(UTC)

            # Save to database
            indicator_data = {
                "value": value,
                "trend": trend.value,
                "trend_percent": trend_percent,
                "status": status,
            }
            await save_indicator(field_id, ind_id, indicator_data, tenant_id)

            # Publish event for newly computed indicator | نشر حدث المؤشر المحسوب مع عزل المستأجر
            await publish_event(
                "sahool.indicators.computed",
                {
                    "field_id": field_id,
                    "indicator_type": ind_id,
                    "value": value,
                    "status": status,
                    "trend": trend.value,
                    "timestamp": timestamp,
                },
                tenant_id=tenant_id,
            )

        indicator = Indicator(
            id=ind_id,
            name_ar=defn["name_ar"],
            name_en=defn["name_en"],
            category=defn["category"],
            value=value,
            unit=defn["unit"],
            min_value=defn["min"],
            max_value=defn["max"],
            optimal_min=defn.get("optimal_min", defn["min"]),
            optimal_max=defn.get("optimal_max", defn["max"]),
            trend=trend,
            trend_percent=trend_percent,
            status=status,
            last_updated=last_updated,
        )
        indicators.append(indicator)

        # Create alert if needed
        alert = create_alert_if_needed(indicator, field_id)
        if alert:
            alerts.append(alert.dict())

    # Calculate overall score
    optimal_count = sum(1 for ind in indicators if ind.status == "optimal")
    overall_score = (optimal_count / len(indicators)) * 100 if indicators else 0

    # Publish field indicators summary event | نشر ملخص مؤشرات الحقل مع عزل المستأجر
    await publish_event(
        "sahool.indicators.field_summary",
        {
            "field_id": field_id,
            "indicators_count": len(indicators),
            "overall_score": round(overall_score, 1),
            "alerts_count": len(alerts),
            "timestamp": timestamp,
        },
        tenant_id=tenant_id,
    )

    return FieldIndicators(
        field_id=field_id,
        field_name=f"حقل {field_id[-4:]}",
        area_hectares=round(random.uniform(1, 50), 2),
        crop_type=random.choice(["طماطم", "قمح", "بن", "قات", "خيار", "موز"]),
        indicators=indicators,
        overall_score=round(overall_score, 1),
        alerts=alerts,
    )


class IndicatorInput(BaseModel):
    """Input model for storing indicator values"""

    indicator_type: str
    value: float
    trend: TrendDirection | None = None
    trend_percent: float | None = None


@app.post("/v1/field/{field_id}/indicators")
async def store_field_indicator(
    field_id: str,
    indicator_input: IndicatorInput,
    user: Any = Depends(get_current_user),
):
    """تخزين قيمة مؤشر لحقل معين

    Store an indicator value for a specific field. This is useful when
    indicator values are computed externally (e.g., from satellite imagery
    processing or IoT sensors).
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", None) or ""
    _validate_tenant_id(tenant_id)

    # Validate indicator type
    if indicator_input.indicator_type not in INDICATOR_DEFINITIONS:
        raise HTTPException(status_code=400, detail=f"Invalid indicator type: {indicator_input.indicator_type}")

    defn = INDICATOR_DEFINITIONS[indicator_input.indicator_type]

    # Validate value is within range
    if not (defn["min"] <= indicator_input.value <= defn["max"]):
        raise HTTPException(
            status_code=400,
            detail=f"Value {indicator_input.value} is outside valid range [{defn['min']}, {defn['max']}]",
        )

    # Calculate status
    status = determine_status(
        indicator_input.value,
        defn.get("optimal_min"),
        defn.get("optimal_max"),
        defn["min"],
        defn["max"],
    )

    # Prepare indicator data
    indicator_data = {
        "value": indicator_input.value,
        "trend": indicator_input.trend.value if indicator_input.trend else TrendDirection.STABLE.value,
        "trend_percent": indicator_input.trend_percent or 0.0,
        "status": status,
    }

    # Save to database
    success = await save_indicator(field_id, indicator_input.indicator_type, indicator_data, tenant_id)

    if not success:
        raise HTTPException(status_code=503, detail="Failed to save indicator. Database may not be available.")

    # Publish event with tenant isolation | نشر الحدث مع عزل المستأجر
    timestamp = datetime.now(UTC).isoformat()
    await publish_event(
        "sahool.indicators.stored",
        {
            "field_id": field_id,
            "indicator_type": indicator_input.indicator_type,
            "value": indicator_input.value,
            "status": status,
            "timestamp": timestamp,
        },
        tenant_id=tenant_id,
    )

    logger.info(
        "Indicator stored",
        field_id=field_id,
        indicator_type=indicator_input.indicator_type,
        value=indicator_input.value,
    )

    return {
        "status": "stored",
        "field_id": field_id,
        "indicator_type": indicator_input.indicator_type,
        "value": indicator_input.value,
        "computed_status": status,
        "stored_at": timestamp,
    }


@app.get("/v1/field/{field_id}/indicator/{indicator_type}")
async def get_single_indicator(
    field_id: str,
    indicator_type: str,
    user: Any = Depends(get_current_user),
):
    """الحصول على مؤشر واحد لحقل معين

    Retrieve a single indicator value from the database.
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", None) or ""
    _enforce_tenant(user, tenant_id)
    if indicator_type not in INDICATOR_DEFINITIONS:
        raise HTTPException(status_code=400, detail=f"Invalid indicator type: {indicator_type}")

    indicator_data = await get_indicator(field_id, indicator_type, tenant_id=tenant_id)

    if not indicator_data:
        raise HTTPException(
            status_code=404,
            detail=f"No stored indicator '{indicator_type}' found for field '{field_id}'",
        )

    defn = INDICATOR_DEFINITIONS[indicator_type]

    return {
        "field_id": field_id,
        "indicator": {
            "id": indicator_type,
            "name_ar": defn["name_ar"],
            "name_en": defn["name_en"],
            "category": defn["category"].value,
            "unit": defn["unit"],
            "value": indicator_data.get("value"),
            "status": indicator_data.get("status"),
            "trend": indicator_data.get("trend"),
            "trend_percent": indicator_data.get("trend_percent"),
            "calculated_at": indicator_data.get("calculated_at"),
        },
    }


@app.delete("/v1/field/{field_id}/indicators")
async def delete_field_indicators_endpoint(field_id: str, user=Depends(get_current_user)):
    """حذف جميع مؤشرات حقل معين

    Delete all stored indicators for a specific field.
    Use with caution - this operation cannot be undone.
    """
    _validate_field_id(field_id)
    tenant_id = getattr(user, "tenant_id", None) if user else None
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant ID is required for this operation.")
    success = await delete_field_indicators(field_id, tenant_id)

    if not success:
        raise HTTPException(status_code=503, detail="Failed to delete indicators. Database may not be available.")

    # Publish event with tenant isolation | نشر الحدث مع عزل المستأجر
    timestamp = datetime.now(UTC).isoformat()
    await publish_event(
        "sahool.indicators.deleted",
        {
            "field_id": field_id,
            "timestamp": timestamp,
        },
        tenant_id=tenant_id,
    )

    logger.info("Field indicators deleted", field_id=field_id)

    return {
        "status": "deleted",
        "field_id": field_id,
        "deleted_at": timestamp,
    }


@app.get("/v1/dashboard/{tenant_id}", response_model=DashboardSummary)
async def get_dashboard_summary(
    tenant_id: str,
    num_fields: int = Query(default=10, ge=1, le=100),
    user: Any = Depends(get_current_user),
):
    """لوحة المعلومات الرئيسية للمستأجر"""
    _enforce_tenant(user, tenant_id)

    # Generate mock data for multiple fields
    fields_data = []
    total_area = 0
    total_health_score = 0
    all_alerts = []

    for _i in range(num_fields):
        field_id = f"field_{uuid.uuid4().hex[:8]}"
        field_indicators = await get_field_indicators(field_id)
        fields_data.append(field_indicators)
        total_area += field_indicators.area_hectares
        total_health_score += field_indicators.overall_score
        all_alerts.extend(field_indicators.alerts)

    # Calculate category summaries
    category_summary = {}
    for cat in IndicatorCategory:
        cat_indicators = []
        for field in fields_data:
            cat_indicators.extend([ind for ind in field.indicators if ind.category == cat])

        if cat_indicators:
            avg_value = sum(ind.value for ind in cat_indicators) / len(cat_indicators)
            optimal_pct = sum(1 for ind in cat_indicators if ind.status == "optimal") / len(cat_indicators) * 100
            category_summary[cat.value] = {
                "average_value": round(avg_value, 2),
                "optimal_percentage": round(optimal_pct, 1),
                "indicators_count": len(cat_indicators),
            }

    # Sort fields by score
    fields_data.sort(key=lambda x: x.overall_score, reverse=True)

    critical_alerts = sum(1 for a in all_alerts if a.get("severity") == "critical")
    avg_health = round(total_health_score / num_fields, 1)

    # Publish dashboard computed event with tenant isolation | نشر حدث لوحة المعلومات مع عزل المستأجر
    await publish_event(
        "sahool.indicators.dashboard_computed",
        {
            "tenant_id": tenant_id,
            "total_fields": num_fields,
            "total_area_hectares": round(total_area, 2),
            "average_health_score": avg_health,
            "active_alerts": len(all_alerts),
            "critical_alerts": critical_alerts,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        tenant_id=tenant_id,
    )

    return DashboardSummary(
        tenant_id=tenant_id,
        total_fields=num_fields,
        total_area_hectares=round(total_area, 2),
        average_health_score=avg_health,
        indicators_summary=category_summary,
        active_alerts=len(all_alerts),
        critical_alerts=critical_alerts,
        top_performing_fields=[
            {
                "field_id": f.field_id,
                "name": f.field_name,
                "score": f.overall_score,
                "crop": f.crop_type,
            }
            for f in fields_data[:3]
        ],
        attention_needed_fields=[
            {
                "field_id": f.field_id,
                "name": f.field_name,
                "score": f.overall_score,
                "crop": f.crop_type,
                "alerts": len(f.alerts),
            }
            for f in fields_data[-3:]
            if f.overall_score < 60
        ],
        generated_at=datetime.now(UTC),
    )


@app.get("/v1/alerts/{tenant_id}")
async def get_tenant_alerts(
    tenant_id: str,
    severity: AlertSeverity | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    user: Any = Depends(get_current_user),
):
    """الحصول على تنبيهات المستأجر"""
    _enforce_tenant(user, tenant_id)
    import random

    # Generate mock alerts
    alerts = []
    for _ in range(min(limit, random.randint(5, 30))):
        ind_id = random.choice(list(INDICATOR_DEFINITIONS.keys()))
        defn = INDICATOR_DEFINITIONS[ind_id]
        sev = severity or random.choice(list(AlertSeverity))

        alerts.append(
            {
                "alert_id": str(uuid.uuid4()),
                "field_id": f"field_{uuid.uuid4().hex[:8]}",
                "indicator_id": ind_id,
                "indicator_name_ar": defn["name_ar"],
                "indicator_name_en": defn["name_en"],
                "severity": sev.value,
                "message_ar": f"تنبيه: {defn['name_ar']} خارج النطاق المثالي",
                "message_en": f"Alert: {defn['name_en']} outside optimal range",
                "created_at": (datetime.now(UTC) - timedelta(hours=random.randint(0, 48))).isoformat(),
            }
        )

    # Publish alerts retrieved event with tenant isolation | نشر حدث التنبيهات مع عزل المستأجر
    critical_count = sum(1 for a in alerts if a["severity"] == "critical")
    warning_count = sum(1 for a in alerts if a["severity"] == "warning")
    await publish_event(
        "sahool.indicators.alerts_retrieved",
        {
            "tenant_id": tenant_id,
            "total_alerts": len(alerts),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        tenant_id=tenant_id,
    )

    return {"tenant_id": tenant_id, "total_alerts": len(alerts), "alerts": alerts}


@app.get("/v1/trends/{field_id}/{indicator_id}")
async def get_indicator_trends(
    field_id: str,
    indicator_id: str,
    days: int = Query(default=30, ge=7, le=365),
    user: Any = Depends(get_current_user),
):
    """الحصول على اتجاهات مؤشر معين"""
    _validate_field_id(field_id)
    import random

    tenant_id = getattr(user, "tenant_id", None) or ""
    _enforce_tenant(user, tenant_id)

    if indicator_id not in INDICATOR_DEFINITIONS:
        raise HTTPException(status_code=404, detail=f"Indicator {indicator_id} not found")

    defn = INDICATOR_DEFINITIONS[indicator_id]
    opt_min = defn.get("optimal_min", defn["min"])
    opt_max = defn.get("optimal_max", defn["max"])
    optimal_mid = (opt_min + opt_max) / 2

    # Generate trend data
    data_points = []
    current_value = optimal_mid + random.uniform(-0.2, 0.2) * (opt_max - opt_min)

    for i in range(days):
        date_point = datetime.now(UTC) - timedelta(days=days - i - 1)
        # Random walk with mean reversion
        change = random.gauss(0, (opt_max - opt_min) * 0.05)
        reversion = (optimal_mid - current_value) * 0.1
        current_value += change + reversion
        current_value = max(defn["min"], min(defn["max"], current_value))

        data_points.append(
            {
                "date": date_point.date().isoformat(),
                "value": round(current_value, 2),
                "status": determine_status(current_value, opt_min, opt_max, defn["min"], defn["max"]),
            }
        )

    # Calculate statistics
    values = [dp["value"] for dp in data_points]
    avg_value = sum(values) / len(values)
    min_value = min(values)
    max_value = max(values)

    overall_trend = (
        TrendDirection.UP.value
        if values[-1] > values[0]
        else (TrendDirection.DOWN.value if values[-1] < values[0] else TrendDirection.STABLE.value)
    )

    # Publish trend analysis event with tenant isolation | نشر حدث تحليل الاتجاهات مع عزل المستأجر
    await publish_event(
        "sahool.indicators.trend_analyzed",
        {
            "field_id": field_id,
            "indicator_type": indicator_id,
            "period_days": days,
            "average_value": round(avg_value, 2),
            "current_value": round(values[-1], 2),
            "overall_trend": overall_trend,
            "timestamp": datetime.now(UTC).isoformat(),
        },
        tenant_id=tenant_id,
    )

    return {
        "field_id": field_id,
        "indicator": {
            "id": indicator_id,
            "name_ar": defn["name_ar"],
            "name_en": defn["name_en"],
            "unit": defn["unit"],
        },
        "period_days": days,
        "statistics": {
            "average": round(avg_value, 2),
            "minimum": round(min_value, 2),
            "maximum": round(max_value, 2),
            "optimal_range": {"min": opt_min, "max": opt_max},
        },
        "data_points": data_points,
        "overall_trend": overall_trend,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8091))
    uvicorn.run(app, host="0.0.0.0", port=port)  # nosec B104 - binding to all interfaces required for Docker container
