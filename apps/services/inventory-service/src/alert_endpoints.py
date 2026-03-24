"""
Alert Endpoints for Inventory Service
Manages low stock alerts, expiry warnings, and notifications
"""

import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from shared.auth.dependencies import get_current_user
from shared.auth.models import User

from .alert_manager import (
    AlertManager,
    AlertPriority,
    AlertType,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/alerts", tags=["Alerts"])


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
    action_url: str | None = None
    created_at: str
    acknowledged_at: str | None = None
    acknowledged_by: str | None = None
    resolved_at: str | None = None
    resolved_by: str | None = None
    resolution_notes: str | None = None
    snooze_until: str | None = None


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
    resolution_notes: str | None = None


class SnoozeAlertRequest(BaseModel):
    """Snooze alert request"""

    snooze_hours: int = Field(24, ge=1, le=168)


# Global alert manager (will be initialized by main app)
_alert_manager: AlertManager | None = None


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
    priority: str | None = Query(None, description="Filter by priority"),
    alert_type: str | None = Query(None, description="Filter by type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _user: User = Depends(get_current_user),
):
    """Get all active alerts"""
    try:
        manager = get_alert_manager()

        # Safely convert to enum with proper error handling
        priority_enum = None
        if priority:
            try:
                priority_enum = AlertPriority[priority.upper()]
            except KeyError:
                raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")

        type_enum = None
        if alert_type:
            try:
                type_enum = AlertType[alert_type.upper()]
            except KeyError:
                raise HTTPException(status_code=400, detail=f"Invalid alert type: {alert_type}")

        alerts = await manager.get_active_alerts(priority=priority_enum, alert_type=type_enum)

        total = len(alerts)
        paginated = alerts[offset : offset + limit]

        return {
            "alerts": [alert.to_dict() for alert in paginated],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error getting alerts: {e}")
        raise HTTPException(status_code=400, detail="Invalid filter parameter value") from e
    except RuntimeError as e:
        logger.error(f"Runtime error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    except Exception as e:
        logger.error(f"Unexpected error getting alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/summary")
async def get_alerts_summary(_user: User = Depends(get_current_user)):
    """Get alert summary statistics"""
    try:
        manager = get_alert_manager()
        return await manager.get_alert_summary()
    except RuntimeError as e:
        logger.error(f"Runtime error getting alert summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    except Exception as e:
        logger.error(f"Unexpected error getting alert summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, data: AcknowledgeAlertRequest, _user: User = Depends(get_current_user)):
    """Acknowledge an alert"""
    try:
        manager = get_alert_manager()
        alert = await manager.acknowledge_alert(alert_id, data.acknowledged_by)

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return alert.to_dict()
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Runtime error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    except Exception as e:
        logger.error(f"Unexpected error acknowledging alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: str, data: ResolveAlertRequest, _user: User = Depends(get_current_user)):
    """Resolve an alert"""
    try:
        manager = get_alert_manager()
        alert = await manager.resolve_alert(alert_id, data.resolved_by, data.resolution_notes)

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return alert.to_dict()
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Runtime error resolving alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    except Exception as e:
        logger.error(f"Unexpected error resolving alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/{alert_id}/snooze")
async def snooze_alert(alert_id: str, data: SnoozeAlertRequest, _user: User = Depends(get_current_user)):
    """Snooze an alert"""
    try:
        manager = get_alert_manager()
        alert = await manager.snooze_alert(alert_id, data.snooze_hours)

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        return alert.to_dict()
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Runtime error snoozing alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    except Exception as e:
        logger.error(f"Unexpected error snoozing alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/check-now")
async def check_alerts_now(background_tasks: BackgroundTasks, _user: User = Depends(get_current_user)):
    """Trigger immediate alert check"""

    async def run_check():
        manager = get_alert_manager()
        await manager.check_all_alerts()

    background_tasks.add_task(run_check)
    return {"message": "Alert check initiated", "status": "processing"}


# ═══════════════════════════════════════════════════════════════════════════
# Alert Settings Endpoints
# ═══════════════════════════════════════════════════════════════════════════

settings_db = {}  # In-memory settings storage


@router.get("/settings")
async def get_alert_settings(_user: User = Depends(get_current_user)):
    """Get alert settings"""
    tenant_id = getattr(_user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant context required")
    settings = settings_db.get(
        tenant_id,
        {
            "expiry_warning_days": 30,
            "expiry_critical_days": 7,
            "enable_email_alerts": True,
            "enable_push_alerts": True,
            "alert_check_interval": 60,
        },
    )
    return settings


@router.put("/settings")
async def update_alert_settings(data: AlertSettingsModel, _user: User = Depends(get_current_user)):
    """Update alert settings"""
    settings = data.model_dump()
    tenant_id = getattr(_user, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="Tenant context required")
    settings_db[tenant_id] = settings
    return settings


@router.get("/{alert_id}", response_model=InventoryAlertResponse)
async def get_alert(alert_id: str, _user: User = Depends(get_current_user)):
    """Get specific alert by ID"""
    try:
        manager = get_alert_manager()
        alert = manager.alerts_db.get(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return alert.to_dict()
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Runtime error getting alert: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    except Exception as e:
        logger.error(f"Unexpected error getting alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e
