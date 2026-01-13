"""
SAHOOL Alert Service - Main API
خدمة التنبيهات الزراعية
Port: 8113
Version: 16.0.0
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path as PathLib

from fastapi import Depends, FastAPI, Header, HTTPException, Path, Query

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sqlalchemy.orm import Session

# Add path to shared modules
# In Docker, shared is at /app/shared
SHARED_PATH = PathLib("/app/shared")
if not SHARED_PATH.exists():
    # Fallback for local development
    SHARED_PATH = PathLib(__file__).parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))
try:
    from config.cors_config import setup_cors_middleware
except ImportError:
    # Fallback if shared module not available
    def setup_cors_middleware(app):
        pass


from shared.errors_py import add_request_id_middleware, setup_exception_handlers

from .database import SessionLocal, check_db_connection, get_db
from .db_models import Alert as DBAlert
from .db_models import AlertRule as DBAlertRule
from .events import AlertTopics, get_publisher, get_subscriber
from .models import (
    AlertCreate,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertSeverity,
    AlertStats,
    AlertStatus,
    AlertType,
    AlertUpdate,
    PaginatedResponse,
)
from .repository import (
    create_alert,
    create_alert_rule,
    delete_alert,
    delete_alert_rule,
    get_alert,
    get_alert_rules_by_field,
    get_alert_statistics,
    get_alerts_by_field,
    update_alert_status,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Logging Configuration
# ═══════════════════════════════════════════════════════════════════════════════


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def sanitize_log_input(value: str) -> str:
    """
    Sanitize user input for safe logging to prevent log injection attacks.
    Removes/escapes newlines, carriage returns, and other control characters.
    """
    if not isinstance(value, str):
        value = str(value)
    # Replace newlines and carriage returns to prevent log injection
    return value.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════════════════════


def get_tenant_id(x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")) -> str:
    """Extract and validate tenant ID from X-Tenant-Id header"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


# ═══════════════════════════════════════════════════════════════════════════════
# Database Storage
# ═══════════════════════════════════════════════════════════════════════════════

# ✅ MIGRATED TO POSTGRESQL
# - Alerts stored in 'alerts' table
# - Alert rules stored in 'alert_rules' table
# - Multi-tenancy support
# - Persistent storage with full audit trail
# - Support for complex time-series queries
# - Multi-instance support via shared database


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Management
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    logger.info("Starting Alert Service...")

    # Check if running in CI/test environment (no database required for smoke tests)
    environment = os.getenv("ENVIRONMENT", "development").lower()
    is_ci_or_test = environment in ("test", "ci", "testing")

    # Check database connection
    try:
        db_ok = check_db_connection()
        if db_ok:
            logger.info("Database connection verified")
            app.state.db_available = True
        else:
            if is_ci_or_test:
                logger.warning("Database not available in CI/test environment - continuing without database")
                app.state.db_available = False
            else:
                logger.error("Database connection failed")
                raise RuntimeError("Database connection failed")
    except Exception as e:
        if is_ci_or_test:
            logger.warning(f"Database connection error in CI/test: {e} - continuing without database")
            app.state.db_available = False
        else:
            logger.error(f"Database connection error: {e}")
            raise

    # Initialize NATS publisher
    try:
        publisher = await get_publisher()
        app.state.publisher = publisher
        logger.info("NATS publisher connected")
    except Exception as e:
        logger.warning(f"NATS publisher connection failed: {e}")
        app.state.publisher = None

    # Initialize NATS subscriber for external alerts
    try:
        subscriber = await get_subscriber()
        subscriber.register_handler(AlertTopics.NDVI_ANOMALY, handle_ndvi_anomaly)
        subscriber.register_handler(AlertTopics.WEATHER_ALERT, handle_weather_alert)
        subscriber.register_handler(AlertTopics.IOT_THRESHOLD, handle_iot_threshold)
        await subscriber.subscribe_to_external_alerts()
        app.state.subscriber = subscriber
        logger.info("NATS subscriber connected and listening")
    except Exception as e:
        logger.warning(f"NATS subscriber connection failed: {e}")
        app.state.subscriber = None

    logger.info("Alert Service ready on port 8113")
    yield

    # Cleanup
    if app.state.publisher:
        await app.state.publisher.close()
    if app.state.subscriber:
        await app.state.subscriber.close()
    logger.info("Alert Service shutting down")


# ═══════════════════════════════════════════════════════════════════════════════
# External Event Handlers
# ═══════════════════════════════════════════════════════════════════════════════


async def handle_ndvi_anomaly(data: dict):
    """معالجة شذوذ NDVI من خدمة NDVI"""
    logger.info(f"Received NDVI anomaly event: {data.get('event_id')}")
    try:
        alert = await create_alert_internal(
            AlertCreate(
                field_id=data.get("field_id", "unknown"),
                tenant_id=data.get("tenant_id"),
                type=AlertType.NDVI_ANOMALY,
                severity=(
                    AlertSeverity.HIGH if data.get("severity") == "high" else AlertSeverity.MEDIUM
                ),
                title=f"شذوذ في مؤشر NDVI - {data.get('anomaly_type', 'غير محدد')}",
                title_en=f"NDVI Anomaly Detected - {data.get('anomaly_type', 'unknown')}",
                message=f"تم اكتشاف شذوذ في قيمة NDVI. القيمة الحالية: {data.get('current_ndvi', 'N/A')}",
                message_en=f"NDVI anomaly detected. Current value: {data.get('current_ndvi', 'N/A')}",
                recommendations=[
                    "فحص الحقل ميدانياً",
                    "التحقق من نظام الري",
                    "فحص الآفات والأمراض",
                ],
                recommendations_en=[
                    "Inspect field",
                    "Check irrigation",
                    "Check for pests/diseases",
                ],
                metadata=data,
                source_service="ndvi-engine",
                correlation_id=data.get("correlation_id"),
            )
        )
        logger.info(f"Created alert {alert['id']} from NDVI anomaly")
    except Exception as e:
        logger.error(f"Failed to create alert from NDVI anomaly: {e}")


async def handle_weather_alert(data: dict):
    """معالجة تنبيه الطقس"""
    logger.info(f"Received weather alert event: {data.get('event_id')}")
    try:
        severity_map = {
            "extreme": AlertSeverity.CRITICAL,
            "severe": AlertSeverity.HIGH,
            "moderate": AlertSeverity.MEDIUM,
            "minor": AlertSeverity.LOW,
        }
        alert = await create_alert_internal(
            AlertCreate(
                field_id=data.get("field_id", "unknown"),
                tenant_id=data.get("tenant_id"),
                type=AlertType.WEATHER,
                severity=severity_map.get(data.get("severity"), AlertSeverity.MEDIUM),
                title=data.get("title", "تنبيه طقس"),
                title_en=data.get("title_en", "Weather Alert"),
                message=data.get("message", "تنبيه طقس من الخدمة"),
                message_en=data.get("message_en", "Weather alert from service"),
                recommendations=data.get("recommendations", []),
                recommendations_en=data.get("recommendations_en", []),
                metadata=data,
                source_service="weather-service",
                expires_at=(
                    datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
                ),
            )
        )
        logger.info(f"Created alert {alert['id']} from weather event")
    except Exception as e:
        logger.error(f"Failed to create alert from weather event: {e}")


async def handle_iot_threshold(data: dict):
    """معالجة تجاوز عتبة IoT"""
    logger.info(f"Received IoT threshold event: {data.get('event_id')}")
    try:
        metric = data.get("metric", "unknown")
        value = data.get("value", "N/A")
        threshold = data.get("threshold", "N/A")

        alert_type = AlertType.SOIL_MOISTURE if "moisture" in metric.lower() else AlertType.GENERAL

        alert = await create_alert_internal(
            AlertCreate(
                field_id=data.get("field_id", "unknown"),
                tenant_id=data.get("tenant_id"),
                type=alert_type,
                severity=AlertSeverity.MEDIUM,
                title=f"تجاوز عتبة {metric}",
                title_en=f"{metric} Threshold Exceeded",
                message=f"القيمة الحالية ({value}) تجاوزت العتبة ({threshold})",
                message_en=f"Current value ({value}) exceeded threshold ({threshold})",
                metadata=data,
                source_service="iot-gateway",
            )
        )
        logger.info(f"Created alert {alert['id']} from IoT threshold")
    except Exception as e:
        logger.error(f"Failed to create alert from IoT threshold: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI App
# ═══════════════════════════════════════════════════════════════════════════════


app = FastAPI(
    title="SAHOOL Alert Service",
    description="""
    خدمة إدارة التنبيهات والإنذارات الزراعية

    Agricultural Alerts and Warnings Management Service

    Features:
    - إنشاء وإدارة التنبيهات
    - قواعد التنبيه التلقائي
    - تكامل مع خدمات NDVI والطقس وIoT
    - إحصائيات وتقارير
    """,
    version="16.0.0",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# CORS - Use centralized secure configuration
setup_cors_middleware(app)


# ═══════════════════════════════════════════════════════════════════════════════
# Health Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/health", tags=["Health"])
def health():
    """فحص صحة الخدمة - Health check with dependencies"""
    return {
        "status": "healthy",
        "service": "alert-service",
        "version": "16.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
        "dependencies": {
            "nats": (
                "connected" if getattr(app.state, "publisher", None) is not None else "disconnected"
            )
        },
    }


@app.get("/healthz", tags=["Health"])
def healthz():
    """فحص صحة الخدمة - Kubernetes liveness probe with dependency check"""
    publisher_ok = getattr(app.state, "publisher", None) is not None
    subscriber_ok = getattr(app.state, "subscriber", None) is not None

    return {
        "status": "healthy" if (publisher_ok and subscriber_ok) else "degraded",
        "service": "alert-service",
        "version": "16.0.0",
        "nats_publisher": publisher_ok,
        "nats_subscriber": subscriber_ok,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/readyz", tags=["Health"])
def readiness():
    """فحص جاهزية الخدمة - Kubernetes readiness probe"""
    db_ok = check_db_connection()

    # Get counts from database if connected
    alerts_count = 0
    rules_count = 0
    if db_ok:
        try:
            db = SessionLocal()
            from sqlalchemy import func, select

            alerts_count = db.execute(select(func.count()).select_from(DBAlert)).scalar() or 0
            rules_count = db.execute(select(func.count()).select_from(DBAlertRule)).scalar() or 0
            db.close()
        except Exception:
            pass

    return {
        "status": "ready" if db_ok else "degraded",
        "database": db_ok,
        "nats_publisher": getattr(app.state, "publisher", None) is not None,
        "nats_subscriber": getattr(app.state, "subscriber", None) is not None,
        "alerts_count": alerts_count,
        "rules_count": rules_count,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Internal Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════


async def create_alert_internal(alert_data: AlertCreate) -> dict:
    """إنشاء تنبيه داخلياً"""
    db = SessionLocal()
    try:
        # Create database alert object
        db_alert = DBAlert(
            field_id=alert_data.field_id,
            tenant_id=alert_data.tenant_id,
            type=alert_data.type.value,
            severity=alert_data.severity.value,
            status=AlertStatus.ACTIVE.value,
            title=alert_data.title,
            title_en=alert_data.title_en,
            message=alert_data.message,
            message_en=alert_data.message_en,
            recommendations=alert_data.recommendations or [],
            recommendations_en=alert_data.recommendations_en or [],
            metadata=alert_data.metadata or {},
            source_service=alert_data.source_service,
            correlation_id=alert_data.correlation_id,
            expires_at=alert_data.expires_at,
        )

        # Save to database
        alert = create_alert(db, db_alert)
        db.commit()
        db.refresh(alert)

        # Convert to dict for API response
        alert_dict = alert.to_dict()

        # Publish event
        if hasattr(app.state, "publisher") and app.state.publisher:
            await app.state.publisher.publish_alert_created(
                alert_id=str(alert.id),
                field_id=alert_data.field_id,
                tenant_id=alert_data.tenant_id,
                alert_type=alert_data.type.value,
                severity=alert_data.severity.value,
                title=alert_data.title,
                correlation_id=alert_data.correlation_id,
            )

        return alert_dict
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
# Alert CRUD Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/alerts", response_model=AlertResponse, tags=["Alerts"])
async def create_alert_endpoint(alert_data: AlertCreate, tenant_id: str = Depends(get_tenant_id)):
    """
    إنشاء تنبيه جديد
    Create a new alert
    """
    # Validate tenant matches request
    if alert_data.tenant_id and alert_data.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    alert_data.tenant_id = tenant_id
    alert = await create_alert_internal(alert_data)
    logger.info(f"Created alert {alert['id']} for field {sanitize_log_input(alert['field_id'])}")
    return alert


@app.get("/alerts/{alert_id}", response_model=AlertResponse, tags=["Alerts"])
async def get_alert_endpoint(
    alert_id: str = Path(..., description="معرف التنبيه"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    جلب تنبيه محدد
    Get a specific alert
    """
    from uuid import UUID

    try:
        alert_uuid = UUID(alert_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")

    alert = get_alert(db, alert_id=alert_uuid, tenant_id=tenant_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert.to_dict()


@app.get("/alerts/field/{field_id}", response_model=PaginatedResponse, tags=["Alerts"])
async def get_alerts_by_field_endpoint(
    field_id: str = Path(..., description="معرف الحقل"),
    status: AlertStatus | None = Query(None, description="تصفية حسب الحالة"),
    severity: AlertSeverity | None = Query(None, description="تصفية حسب الخطورة"),
    alert_type: AlertType | None = Query(None, alias="type", description="تصفية حسب النوع"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    جلب تنبيهات حقل معين
    Get alerts for a specific field
    """
    alerts, total = get_alerts_by_field(
        db,
        field_id=field_id,
        tenant_id=tenant_id,
        status=status.value if status else None,
        alert_type=alert_type.value if alert_type else None,
        severity=severity.value if severity else None,
        skip=skip,
        limit=limit,
    )

    items = [alert.to_dict() for alert in alerts]

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


@app.patch("/alerts/{alert_id}", response_model=AlertResponse, tags=["Alerts"])
async def update_alert_endpoint(
    alert_id: str = Path(..., description="معرف التنبيه"),
    update_data: AlertUpdate = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    تحديث حالة تنبيه
    Update alert status
    """
    from uuid import UUID

    try:
        alert_uuid = UUID(alert_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")

    # Get alert first to check tenant access
    alert = get_alert(db, alert_id=alert_uuid, tenant_id=tenant_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    old_status = alert.status

    if update_data.status:
        user_id = update_data.acknowledged_by or update_data.dismissed_by or update_data.resolved_by

        updated_alert = update_alert_status(
            db,
            alert_id=alert_uuid,
            status=update_data.status.value,
            user_id=user_id,
            note=update_data.resolution_note,
        )

        if not updated_alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        db.commit()
        db.refresh(updated_alert)

        # Publish event
        if hasattr(app.state, "publisher") and app.state.publisher:
            await app.state.publisher.publish_alert_updated(
                alert_id=str(alert_uuid),
                field_id=updated_alert.field_id,
                old_status=old_status,
                new_status=updated_alert.status,
                updated_by=user_id,
            )

        logger.info(
            "Updated alert %s: %s -> %s",
            sanitize_log_input(alert_id),
            sanitize_log_input(old_status),
            sanitize_log_input(updated_alert.status),
        )
        return updated_alert.to_dict()

    return alert.to_dict()


@app.delete("/alerts/{alert_id}", tags=["Alerts"])
async def delete_alert_endpoint(
    alert_id: str = Path(..., description="معرف التنبيه"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    حذف تنبيه
    Delete an alert
    """
    from uuid import UUID

    try:
        alert_uuid = UUID(alert_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")

    # Get alert first to check tenant access
    alert = get_alert(db, alert_id=alert_uuid, tenant_id=tenant_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Delete the alert
    deleted = delete_alert(db, alert_uuid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.commit()
    logger.info(f"Deleted alert {sanitize_log_input(alert_id)}")
    return {"status": "deleted", "alert_id": alert_id}


# ═══════════════════════════════════════════════════════════════════════════════
# Alert Actions
# ═══════════════════════════════════════════════════════════════════════════════


@app.post(
    "/alerts/{alert_id}/acknowledge",
    response_model=AlertResponse,
    tags=["Alert Actions"],
)
async def acknowledge_alert(
    alert_id: str = Path(..., description="معرف التنبيه"),
    user_id: str = Query(..., description="معرف المستخدم"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    الإقرار بتنبيه
    Acknowledge an alert
    """
    from uuid import UUID

    try:
        alert_uuid = UUID(alert_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")

    alert = get_alert(db, alert_id=alert_uuid, tenant_id=tenant_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if alert.status != AlertStatus.ACTIVE.value:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot acknowledge alert with status: {alert.status}",
        )

    updated_alert = update_alert_status(
        db, alert_id=alert_uuid, status=AlertStatus.ACKNOWLEDGED.value, user_id=user_id
    )

    if not updated_alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.commit()
    db.refresh(updated_alert)

    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.publish_alert_acknowledged(
            str(alert_uuid), updated_alert.field_id, user_id
        )

    return updated_alert.to_dict()


@app.post("/alerts/{alert_id}/resolve", response_model=AlertResponse, tags=["Alert Actions"])
async def resolve_alert(
    alert_id: str = Path(..., description="معرف التنبيه"),
    user_id: str = Query(..., description="معرف المستخدم"),
    note: str | None = Query(None, description="ملاحظة الحل"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    حل تنبيه
    Resolve an alert
    """
    from uuid import UUID

    try:
        alert_uuid = UUID(alert_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")

    alert = get_alert(db, alert_id=alert_uuid, tenant_id=tenant_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if alert.status == AlertStatus.RESOLVED.value:
        raise HTTPException(status_code=400, detail="Alert is already resolved")

    updated_alert = update_alert_status(
        db,
        alert_id=alert_uuid,
        status=AlertStatus.RESOLVED.value,
        user_id=user_id,
        note=note,
    )

    if not updated_alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.commit()
    db.refresh(updated_alert)

    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.publish_alert_resolved(
            str(alert_uuid), updated_alert.field_id, user_id, note
        )

    return updated_alert.to_dict()


@app.post("/alerts/{alert_id}/dismiss", response_model=AlertResponse, tags=["Alert Actions"])
async def dismiss_alert(
    alert_id: str = Path(..., description="معرف التنبيه"),
    user_id: str = Query(..., description="معرف المستخدم"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    رفض تنبيه
    Dismiss an alert
    """
    from uuid import UUID

    try:
        alert_uuid = UUID(alert_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid alert ID format")

    alert = get_alert(db, alert_id=alert_uuid, tenant_id=tenant_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if alert.status == AlertStatus.DISMISSED.value:
        raise HTTPException(status_code=400, detail="Alert is already dismissed")

    updated_alert = update_alert_status(
        db, alert_id=alert_uuid, status=AlertStatus.DISMISSED.value, user_id=user_id
    )

    if not updated_alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.commit()
    db.refresh(updated_alert)

    return updated_alert.to_dict()


# ═══════════════════════════════════════════════════════════════════════════════
# Alert Rules
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/alerts/rules", response_model=AlertRuleResponse, tags=["Alert Rules"])
async def create_rule(
    rule_data: AlertRuleCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    إنشاء قاعدة تنبيه
    Create an alert rule
    """
    # Validate tenant matches request
    if rule_data.tenant_id and rule_data.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")

    db_rule = DBAlertRule(
        field_id=rule_data.field_id,
        tenant_id=tenant_id,  # Use validated tenant_id
        name=rule_data.name,
        name_en=rule_data.name_en,
        enabled=rule_data.enabled,
        condition=rule_data.condition.model_dump(),
        alert_config=rule_data.alert_config.model_dump(),
        cooldown_hours=rule_data.cooldown_hours,
    )

    rule = create_alert_rule(db, db_rule)
    db.commit()
    db.refresh(rule)

    logger.info(f"Created alert rule {rule.id} for field {sanitize_log_input(rule_data.field_id)}")
    return rule.to_dict()


@app.get("/alerts/rules", response_model=list[AlertRuleResponse], tags=["Alert Rules"])
async def get_rules(
    field_id: str | None = Query(None, description="تصفية حسب الحقل"),
    enabled: bool | None = Query(None, description="تصفية حسب الحالة"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    جلب قواعد التنبيه
    Get alert rules
    """
    from sqlalchemy import select

    from .db_models import AlertRule

    # Always filter by tenant_id for security
    query = select(AlertRule).where(AlertRule.tenant_id == tenant_id)

    if field_id:
        query = query.where(AlertRule.field_id == field_id)

    if enabled is not None:
        query = query.where(AlertRule.enabled == enabled)

    rules = list(db.execute(query).scalars())

    return [rule.to_dict() for rule in rules]


@app.delete("/alerts/rules/{rule_id}", tags=["Alert Rules"])
async def delete_rule(
    rule_id: str = Path(..., description="معرف القاعدة"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    حذف قاعدة تنبيه
    Delete an alert rule
    """
    from uuid import UUID

    from sqlalchemy import select

    from .db_models import AlertRule

    try:
        rule_uuid = UUID(rule_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid rule ID format")

    # Check if rule exists and belongs to tenant
    query = select(AlertRule).where(
        AlertRule.id == rule_uuid,
        AlertRule.tenant_id == tenant_id,
    )
    rule = db.execute(query).scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    deleted = delete_alert_rule(db, rule_uuid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")

    db.commit()
    logger.info(f"Deleted alert rule {sanitize_log_input(rule_id)}")
    return {"status": "deleted", "rule_id": rule_id}


# ═══════════════════════════════════════════════════════════════════════════════
# Statistics
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/alerts/stats", response_model=AlertStats, tags=["Statistics"])
async def get_stats(
    field_id: str | None = Query(None, description="تصفية حسب الحقل"),
    period: str = Query("30d", description="الفترة الزمنية (7d, 30d, 90d)"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """
    إحصائيات التنبيهات
    Get alert statistics
    """
    # Parse period
    days = int(period.replace("d", ""))

    # Get statistics from repository
    stats = get_alert_statistics(db, tenant_id=tenant_id, field_id=field_id, days=days)

    # Calculate rates
    total = stats["total_alerts"]
    acknowledged_count = stats.get("acknowledged_count", 0)
    resolved_count = stats.get("resolved_count", 0)

    acknowledged_rate = (acknowledged_count / total * 100) if total > 0 else 0
    resolved_rate = (resolved_count / total * 100) if total > 0 else 0

    return AlertStats(
        total_alerts=stats["total_alerts"],
        active_alerts=stats["active_alerts"],
        by_type=stats["by_type"],
        by_severity=stats["by_severity"],
        by_status=stats["by_status"],
        acknowledged_rate=round(acknowledged_rate, 2),
        resolved_rate=round(resolved_rate, 2),
        average_resolution_hours=stats.get("average_resolution_hours"),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8113))
    uvicorn.run(app, host="0.0.0.0", port=port)
