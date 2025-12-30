"""
SAHOOL Alert Service - Main API
خدمة التنبيهات الزراعية
Port: 8113
Version: 16.0.0
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Path, Depends, Header
from pydantic import BaseModel

# Add path to shared config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../shared/config"))
from cors_config import setup_cors_middleware

from .models import (
    AlertType,
    AlertSeverity,
    AlertStatus,
    AlertCreate,
    AlertUpdate,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertStats,
    PaginatedResponse,
)
from .events import get_publisher, get_subscriber, AlertTopics, AlertEventPublisher


# ═══════════════════════════════════════════════════════════════════════════════
# Logging Configuration
# ═══════════════════════════════════════════════════════════════════════════════


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════════════════════


def get_tenant_id(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id")) -> str:
    """Extract and validate tenant ID from X-Tenant-Id header"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


# ═══════════════════════════════════════════════════════════════════════════════
# In-Memory Storage (Replace with Database in Production)
# ═══════════════════════════════════════════════════════════════════════════════


_alerts: dict[str, dict] = {}
_rules: dict[str, dict] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Management
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    logger.info("Starting Alert Service...")

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
        alert = await create_alert_internal(AlertCreate(
            field_id=data.get("field_id", "unknown"),
            tenant_id=data.get("tenant_id"),
            type=AlertType.NDVI_ANOMALY,
            severity=AlertSeverity.HIGH if data.get("severity") == "high" else AlertSeverity.MEDIUM,
            title=f"شذوذ في مؤشر NDVI - {data.get('anomaly_type', 'غير محدد')}",
            title_en=f"NDVI Anomaly Detected - {data.get('anomaly_type', 'unknown')}",
            message=f"تم اكتشاف شذوذ في قيمة NDVI. القيمة الحالية: {data.get('current_ndvi', 'N/A')}",
            message_en=f"NDVI anomaly detected. Current value: {data.get('current_ndvi', 'N/A')}",
            recommendations=["فحص الحقل ميدانياً", "التحقق من نظام الري", "فحص الآفات والأمراض"],
            recommendations_en=["Inspect field", "Check irrigation", "Check for pests/diseases"],
            metadata=data,
            source_service="ndvi-engine",
            correlation_id=data.get("correlation_id")
        ))
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
            "minor": AlertSeverity.LOW
        }
        alert = await create_alert_internal(AlertCreate(
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
            source_service="weather-core",
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
        ))
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

        alert = await create_alert_internal(AlertCreate(
            field_id=data.get("field_id", "unknown"),
            tenant_id=data.get("tenant_id"),
            type=alert_type,
            severity=AlertSeverity.MEDIUM,
            title=f"تجاوز عتبة {metric}",
            title_en=f"{metric} Threshold Exceeded",
            message=f"القيمة الحالية ({value}) تجاوزت العتبة ({threshold})",
            message_en=f"Current value ({value}) exceeded threshold ({threshold})",
            metadata=data,
            source_service="iot-gateway"
        ))
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
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": {
            "nats": "connected" if getattr(app.state, "publisher", None) is not None else "disconnected"
        }
    }


@app.get("/healthz", tags=["Health"])
def healthz():
    """فحص صحة الخدمة - Kubernetes liveness probe"""
    return {
        "status": "healthy",
        "service": "alert-service",
        "version": "16.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/readyz", tags=["Health"])
def readiness():
    """فحص جاهزية الخدمة - Kubernetes readiness probe"""
    return {
        "status": "ready",
        "nats_publisher": getattr(app.state, "publisher", None) is not None,
        "nats_subscriber": getattr(app.state, "subscriber", None) is not None,
        "alerts_count": len(_alerts),
        "rules_count": len(_rules)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Internal Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════


async def create_alert_internal(alert_data: AlertCreate) -> dict:
    """إنشاء تنبيه داخلياً"""
    alert_id = str(uuid4())
    now = datetime.now(timezone.utc)

    alert = {
        "id": alert_id,
        "field_id": alert_data.field_id,
        "tenant_id": alert_data.tenant_id,
        "type": alert_data.type.value,
        "severity": alert_data.severity.value,
        "status": AlertStatus.ACTIVE.value,
        "title": alert_data.title,
        "title_en": alert_data.title_en,
        "message": alert_data.message,
        "message_en": alert_data.message_en,
        "recommendations": alert_data.recommendations or [],
        "recommendations_en": alert_data.recommendations_en or [],
        "metadata": alert_data.metadata or {},
        "source_service": alert_data.source_service,
        "correlation_id": alert_data.correlation_id,
        "created_at": now.isoformat(),
        "expires_at": alert_data.expires_at.isoformat() if alert_data.expires_at else None,
        "acknowledged_at": None,
        "acknowledged_by": None,
        "dismissed_at": None,
        "dismissed_by": None,
        "resolved_at": None,
        "resolved_by": None,
        "resolution_note": None
    }

    _alerts[alert_id] = alert

    # Publish event
    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.publish_alert_created(
            alert_id=alert_id,
            field_id=alert_data.field_id,
            tenant_id=alert_data.tenant_id,
            alert_type=alert_data.type.value,
            severity=alert_data.severity.value,
            title=alert_data.title,
            correlation_id=alert_data.correlation_id
        )

    return alert


# ═══════════════════════════════════════════════════════════════════════════════
# Alert CRUD Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/alerts", response_model=AlertResponse, tags=["Alerts"])
async def create_alert(alert_data: AlertCreate, tenant_id: str = Depends(get_tenant_id)):
    """
    إنشاء تنبيه جديد
    Create a new alert
    """
    # Validate tenant matches request
    if alert_data.tenant_id and alert_data.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant ID mismatch")
    alert_data.tenant_id = tenant_id
    alert = await create_alert_internal(alert_data)
    logger.info(f"Created alert {alert['id']} for field {alert['field_id']}")
    return alert


@app.get("/alerts/{alert_id}", response_model=AlertResponse, tags=["Alerts"])
async def get_alert(
    alert_id: str = Path(..., description="معرف التنبيه"),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    جلب تنبيه محدد
    Get a specific alert
    """
    if alert_id not in _alerts:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert = _alerts[alert_id]
    # Validate tenant access
    if alert["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return alert


@app.get("/alerts/field/{field_id}", response_model=PaginatedResponse, tags=["Alerts"])
async def get_alerts_by_field(
    field_id: str = Path(..., description="معرف الحقل"),
    status: Optional[AlertStatus] = Query(None, description="تصفية حسب الحالة"),
    severity: Optional[AlertSeverity] = Query(None, description="تصفية حسب الخطورة"),
    alert_type: Optional[AlertType] = Query(None, alias="type", description="تصفية حسب النوع"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    جلب تنبيهات حقل معين
    Get alerts for a specific field
    """
    # Filter alerts by field AND tenant
    filtered = [a for a in _alerts.values() if a["field_id"] == field_id and a["tenant_id"] == tenant_id]

    if status:
        filtered = [a for a in filtered if a["status"] == status.value]
    if severity:
        filtered = [a for a in filtered if a["severity"] == severity.value]
    if alert_type:
        filtered = [a for a in filtered if a["type"] == alert_type.value]

    # Sort by created_at descending
    filtered.sort(key=lambda x: x["created_at"], reverse=True)

    # Paginate
    total = len(filtered)
    items = filtered[skip:skip + limit]

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total
    }


@app.patch("/alerts/{alert_id}", response_model=AlertResponse, tags=["Alerts"])
async def update_alert(
    alert_id: str = Path(..., description="معرف التنبيه"),
    update_data: AlertUpdate = None,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    تحديث حالة تنبيه
    Update alert status
    """
    if alert_id not in _alerts:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert = _alerts[alert_id]
    # Validate tenant access
    if alert["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    old_status = alert["status"]
    now = datetime.now(timezone.utc)

    if update_data.status:
        alert["status"] = update_data.status.value

        if update_data.status == AlertStatus.ACKNOWLEDGED:
            alert["acknowledged_at"] = now.isoformat()
            alert["acknowledged_by"] = update_data.acknowledged_by
        elif update_data.status == AlertStatus.DISMISSED:
            alert["dismissed_at"] = now.isoformat()
            alert["dismissed_by"] = update_data.dismissed_by
        elif update_data.status == AlertStatus.RESOLVED:
            alert["resolved_at"] = now.isoformat()
            alert["resolved_by"] = update_data.resolved_by
            alert["resolution_note"] = update_data.resolution_note

    _alerts[alert_id] = alert

    # Publish event
    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.publish_alert_updated(
            alert_id=alert_id,
            field_id=alert["field_id"],
            old_status=old_status,
            new_status=alert["status"],
            updated_by=update_data.acknowledged_by or update_data.dismissed_by or update_data.resolved_by
        )

    logger.info(f"Updated alert {alert_id}: {old_status} -> {alert['status']}")
    return alert


@app.delete("/alerts/{alert_id}", tags=["Alerts"])
async def delete_alert(
    alert_id: str = Path(..., description="معرف التنبيه"),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    حذف تنبيه
    Delete an alert
    """
    if alert_id not in _alerts:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert = _alerts[alert_id]
    # Validate tenant access
    if alert["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    del _alerts[alert_id]
    logger.info(f"Deleted alert {alert_id}")
    return {"status": "deleted", "alert_id": alert_id}


# ═══════════════════════════════════════════════════════════════════════════════
# Alert Actions
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/alerts/{alert_id}/acknowledge", response_model=AlertResponse, tags=["Alert Actions"])
async def acknowledge_alert(
    alert_id: str = Path(..., description="معرف التنبيه"),
    user_id: str = Query(..., description="معرف المستخدم"),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    الإقرار بتنبيه
    Acknowledge an alert
    """
    if alert_id not in _alerts:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert = _alerts[alert_id]
    # Validate tenant access
    if alert["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if alert["status"] != AlertStatus.ACTIVE.value:
        raise HTTPException(status_code=400, detail=f"Cannot acknowledge alert with status: {alert['status']}")

    alert["status"] = AlertStatus.ACKNOWLEDGED.value
    alert["acknowledged_at"] = datetime.now(timezone.utc).isoformat()
    alert["acknowledged_by"] = user_id

    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.publish_alert_acknowledged(alert_id, alert["field_id"], user_id)

    return alert


@app.post("/alerts/{alert_id}/resolve", response_model=AlertResponse, tags=["Alert Actions"])
async def resolve_alert(
    alert_id: str = Path(..., description="معرف التنبيه"),
    user_id: str = Query(..., description="معرف المستخدم"),
    note: Optional[str] = Query(None, description="ملاحظة الحل"),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    حل تنبيه
    Resolve an alert
    """
    if alert_id not in _alerts:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert = _alerts[alert_id]
    # Validate tenant access
    if alert["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if alert["status"] == AlertStatus.RESOLVED.value:
        raise HTTPException(status_code=400, detail="Alert is already resolved")

    alert["status"] = AlertStatus.RESOLVED.value
    alert["resolved_at"] = datetime.now(timezone.utc).isoformat()
    alert["resolved_by"] = user_id
    alert["resolution_note"] = note

    if hasattr(app.state, "publisher") and app.state.publisher:
        await app.state.publisher.publish_alert_resolved(alert_id, alert["field_id"], user_id, note)

    return alert


@app.post("/alerts/{alert_id}/dismiss", response_model=AlertResponse, tags=["Alert Actions"])
async def dismiss_alert(
    alert_id: str = Path(..., description="معرف التنبيه"),
    user_id: str = Query(..., description="معرف المستخدم"),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    رفض تنبيه
    Dismiss an alert
    """
    if alert_id not in _alerts:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert = _alerts[alert_id]
    # Validate tenant access
    if alert["tenant_id"] != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if alert["status"] == AlertStatus.DISMISSED.value:
        raise HTTPException(status_code=400, detail="Alert is already dismissed")

    alert["status"] = AlertStatus.DISMISSED.value
    alert["dismissed_at"] = datetime.now(timezone.utc).isoformat()
    alert["dismissed_by"] = user_id

    return alert


# ═══════════════════════════════════════════════════════════════════════════════
# Alert Rules
# ═══════════════════════════════════════════════════════════════════════════════


@app.post("/alerts/rules", response_model=AlertRuleResponse, tags=["Alert Rules"])
async def create_rule(rule_data: AlertRuleCreate):
    """
    إنشاء قاعدة تنبيه
    Create an alert rule
    """
    rule_id = str(uuid4())
    now = datetime.now(timezone.utc)

    rule = {
        "id": rule_id,
        "field_id": rule_data.field_id,
        "tenant_id": rule_data.tenant_id,
        "name": rule_data.name,
        "name_en": rule_data.name_en,
        "enabled": rule_data.enabled,
        "condition": rule_data.condition.model_dump(),
        "alert_config": rule_data.alert_config.model_dump(),
        "cooldown_hours": rule_data.cooldown_hours,
        "last_triggered_at": None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }

    _rules[rule_id] = rule
    logger.info(f"Created alert rule {rule_id} for field {rule_data.field_id}")
    return rule


@app.get("/alerts/rules", response_model=List[AlertRuleResponse], tags=["Alert Rules"])
async def get_rules(
    field_id: Optional[str] = Query(None, description="تصفية حسب الحقل"),
    enabled: Optional[bool] = Query(None, description="تصفية حسب الحالة")
):
    """
    جلب قواعد التنبيه
    Get alert rules
    """
    rules = list(_rules.values())

    if field_id:
        rules = [r for r in rules if r["field_id"] == field_id]
    if enabled is not None:
        rules = [r for r in rules if r["enabled"] == enabled]

    return rules


@app.delete("/alerts/rules/{rule_id}", tags=["Alert Rules"])
async def delete_rule(rule_id: str = Path(..., description="معرف القاعدة")):
    """
    حذف قاعدة تنبيه
    Delete an alert rule
    """
    if rule_id not in _rules:
        raise HTTPException(status_code=404, detail="Rule not found")

    del _rules[rule_id]
    logger.info(f"Deleted alert rule {rule_id}")
    return {"status": "deleted", "rule_id": rule_id}


# ═══════════════════════════════════════════════════════════════════════════════
# Statistics
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/alerts/stats", response_model=AlertStats, tags=["Statistics"])
async def get_stats(
    field_id: Optional[str] = Query(None, description="تصفية حسب الحقل"),
    period: str = Query("30d", description="الفترة الزمنية (7d, 30d, 90d)")
):
    """
    إحصائيات التنبيهات
    Get alert statistics
    """
    # Parse period
    days = int(period.replace("d", ""))
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    # Filter alerts
    filtered = list(_alerts.values())
    if field_id:
        filtered = [a for a in filtered if a["field_id"] == field_id]

    # Filter by date
    filtered = [a for a in filtered if datetime.fromisoformat(a["created_at"].replace("Z", "+00:00")) >= cutoff]

    # Calculate stats
    total = len(filtered)
    active = len([a for a in filtered if a["status"] == AlertStatus.ACTIVE.value])
    acknowledged = len([a for a in filtered if a["status"] == AlertStatus.ACKNOWLEDGED.value])
    resolved = len([a for a in filtered if a["status"] == AlertStatus.RESOLVED.value])

    by_type = {}
    by_severity = {}
    by_status = {}

    for alert in filtered:
        by_type[alert["type"]] = by_type.get(alert["type"], 0) + 1
        by_severity[alert["severity"]] = by_severity.get(alert["severity"], 0) + 1
        by_status[alert["status"]] = by_status.get(alert["status"], 0) + 1

    # Calculate rates
    acknowledged_rate = (acknowledged / total * 100) if total > 0 else 0
    resolved_rate = (resolved / total * 100) if total > 0 else 0

    # Calculate average resolution time
    resolution_times = []
    for alert in filtered:
        if alert["resolved_at"] and alert["created_at"]:
            created = datetime.fromisoformat(alert["created_at"].replace("Z", "+00:00"))
            resolved_at = datetime.fromisoformat(alert["resolved_at"].replace("Z", "+00:00"))
            hours = (resolved_at - created).total_seconds() / 3600
            resolution_times.append(hours)

    avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else None

    return AlertStats(
        total_alerts=total,
        active_alerts=active,
        by_type=by_type,
        by_severity=by_severity,
        by_status=by_status,
        acknowledged_rate=round(acknowledged_rate, 2),
        resolved_rate=round(resolved_rate, 2),
        average_resolution_hours=round(avg_resolution, 2) if avg_resolution else None
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8113))
    uvicorn.run(app, host="0.0.0.0", port=port)
