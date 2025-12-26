"""
Alert Endpoints for Inventory Service
Manages low stock alerts, expiry warnings, and notifications
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
import logging

from alert_manager import (
    AlertManager,
    AlertType,
    AlertPriority,
    AlertStatus,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/v1/alerts", tags=["Alerts"])


# ═══════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════


class InventoryAlertResponse(BaseModel):
    """Alert response model"""
    id: str
    alert_type: str
    priority: str
    status: str
    item_id: str
    item_name: str
    item_name_ar: str
    title_en: str
    title_ar: str
    message_en: str
    message_ar: str
    current_value: float
    threshold_value: float
    recommended_action_en: str
    recommended_action_ar: str
    action_url: Optional[str] = None
    created_at: str
    acknowledged_at: Optional[str] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    snooze_until: Optional[str] = None


class AlertSettingsModel(BaseModel):
    """Alert settings"""
    expiry_warning_days: int = 30
    expiry_critical_days: int = 7
    enable_email_alerts: bool = True
    enable_push_alerts: bool = True
    alert_check_interval: int = 60  # minutes


class AcknowledgeAlertRequest(BaseModel):
    """Acknowledge alert request"""
    acknowledged_by: str


class ResolveAlertRequest(BaseModel):
    """Resolve alert request"""
    resolved_by: str
    resolution_notes: Optional[str] = None


class SnoozeAlertRequest(BaseModel):
    """Snooze alert request"""
    snooze_hours: int = Field(24, ge=1, le=168)


# Global alert manager (will be initialized by main app)
_alert_manager: Optional[AlertManager] = None


def init_alert_manager(manager: AlertManager):
    """Initialize the alert manager"""
    global _alert_manager
    _alert_manager = manager


def get_alert_manager() -> AlertManager:
    """Get the alert manager instance"""
    if _alert_manager is None:
        raise RuntimeError("Alert manager not initialized")
    return _alert_manager


# ═══════════════════════════════════════════════════════════════════════════
# Alert Endpoints
# ═══════════════════════════════════════════════════════════════════════════


@router.get("", response_model=dict)
async def get_alerts(
    priority: Optional[str] = Query(None, description="Filter by priority"),
    alert_type: Optional[str] = Query(None, description="Filter by type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all active alerts"""
    try:
        manager = get_alert_manager()

        priority_enum = AlertPriority[priority.upper()] if priority else None
        type_enum = AlertType[alert_type.upper()] if alert_type else None

        alerts = await manager.get_active_alerts(
            priority=priority_enum,
            alert_type=type_enum
        )

        total = len(alerts)
        paginated = alerts[offset:offset + limit]

        return {
            "alerts": [alert.to_dict() for alert in paginated],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{alert_id}", response_model=InventoryAlertResponse)
async def get_alert(alert_id: str):
    """Get specific alert by ID"""
    try:
        manager = get_alert_manager()
        alert = manager.alerts_db.get(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return alert.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/summary")
async def get_alerts_summary():
    """Get alert summary statistics"""
    try:
        manager = get_alert_manager()
        return await manager.get_alert_summary()
    except Exception as e:
        logger.error(f"Error getting alert summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    data: AcknowledgeAlertRequest
):
    """Acknowledge an alert"""
    try:
        manager = get_alert_manager()
        alert = await manager.acknowledge_alert(
            alert_id,
            data.acknowledged_by
        )

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return alert.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    data: ResolveAlertRequest
):
    """Resolve an alert"""
    try:
        manager = get_alert_manager()
        alert = await manager.resolve_alert(
            alert_id,
            data.resolved_by,
            data.resolution_notes
        )

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return alert.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{alert_id}/snooze")
async def snooze_alert(
    alert_id: str,
    data: SnoozeAlertRequest
):
    """Snooze an alert"""
    try:
        manager = get_alert_manager()
        alert = await manager.snooze_alert(
            alert_id,
            data.snooze_hours
        )

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return alert.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error snoozing alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/check-now")
async def check_alerts_now(background_tasks: BackgroundTasks):
    """Trigger immediate alert check"""
    async def run_check():
        manager = get_alert_manager()
        await manager.check_all_alerts()

    background_tasks.add_task(run_check)
    return {
        "message": "Alert check initiated",
        "status": "processing"
    }


# ═══════════════════════════════════════════════════════════════════════════
# Alert Settings Endpoints
# ═══════════════════════════════════════════════════════════════════════════

settings_db = {}  # In-memory settings storage


@router.get("/settings")
async def get_alert_settings(tenant_id: str = "tenant_demo"):
    """Get alert settings"""
    settings = settings_db.get(tenant_id, {
        "expiry_warning_days": 30,
        "expiry_critical_days": 7,
        "enable_email_alerts": True,
        "enable_push_alerts": True,
        "alert_check_interval": 60,
    })
    return settings


@router.put("/settings")
async def update_alert_settings(
    data: AlertSettingsModel,
    tenant_id: str = "tenant_demo"
):
    """Update alert settings"""
    settings = data.model_dump()
    settings_db[tenant_id] = settings
    return settings
