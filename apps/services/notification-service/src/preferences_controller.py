"""
SAHOOL Notification Service - Preferences Controller
وحدة التحكم في تفضيلات الإشعارات - FastAPI Routes

Handles HTTP endpoints for managing user notification preferences
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from .preferences_service import PreferencesService

logger = logging.getLogger("sahool-notifications.preferences-controller")

# Create router
router = APIRouter(prefix="/v1/preferences", tags=["Preferences"])


# =============================================================================
# Request/Response Models
# =============================================================================


class UpdateEventPreferenceRequest(BaseModel):
    """طلب تحديث تفضيلات حدث - Update Event Preference Request"""

    user_id: str = Field(..., description="User ID")
    event_type: str = Field(
        ..., description="Event type (weather_alert, pest_outbreak, etc.)"
    )
    channels: List[str] = Field(..., description="List of channel types to use")
    enabled: bool = Field(True, description="Whether this event type is enabled")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenancy")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "farmer-123",
                "event_type": "weather_alert",
                "channels": ["email", "sms", "push"],
                "enabled": True,
                "tenant_id": "tenant-1",
            }
        }


class SetQuietHoursRequest(BaseModel):
    """طلب تحديد ساعات الهدوء - Set Quiet Hours Request"""

    user_id: str = Field(..., description="User ID")
    quiet_hours_start: Optional[str] = Field(
        None, description="Start time in HH:MM format (e.g., '22:00')"
    )
    quiet_hours_end: Optional[str] = Field(
        None, description="End time in HH:MM format (e.g., '06:00')"
    )
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenancy")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "farmer-123",
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "06:00",
                "tenant_id": "tenant-1",
            }
        }


class BulkUpdatePreferencesRequest(BaseModel):
    """طلب تحديث تفضيلات متعددة - Bulk Update Preferences Request"""

    user_id: str = Field(..., description="User ID")
    preferences: List[Dict[str, Any]] = Field(
        ..., description="List of preference updates"
    )
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenancy")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "farmer-123",
                "tenant_id": "tenant-1",
                "preferences": [
                    {
                        "event_type": "weather_alert",
                        "channels": ["email", "sms", "push"],
                        "enabled": True,
                    },
                    {
                        "event_type": "pest_outbreak",
                        "channels": ["sms", "push"],
                        "enabled": True,
                    },
                    {
                        "event_type": "irrigation_reminder",
                        "channels": ["push"],
                        "enabled": False,
                    },
                ],
            }
        }


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/", summary="الحصول على تفضيلات المستخدم - Get User Preferences")
async def get_preferences(
    user_id: str = Query(..., description="User ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID"),
):
    """
    الحصول على جميع تفضيلات الإشعارات للمستخدم
    Get all notification preferences for a user

    Returns preferences for all event types with their configured channels.
    """
    try:
        preferences = await PreferencesService.get_user_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        return {
            "success": True,
            "user_id": user_id,
            "total": len(preferences),
            "preferences": preferences,
        }

    except Exception as e:
        logger.error(f"Error in get_preferences endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get(
    "/event/{event_type}", summary="الحصول على تفضيلات حدث معين - Get Event Preference"
) from e
async def get_event_preference(
    event_type: str,
    user_id: str = Query(..., description="User ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID"),
):
    """
    الحصول على تفضيلات نوع حدث معين
    Get preference for a specific event type

    Event types:
    - weather_alert
    - pest_outbreak
    - irrigation_reminder
    - crop_health
    - market_price
    - task_reminder
    - system
    """
    try:
        preference = await PreferencesService.get_event_preference(
            user_id=user_id,
            event_type=event_type,
            tenant_id=tenant_id,
        )

        if not preference:
            return {
                "success": True,
                "message": "لا توجد تفضيلات لهذا الحدث - No preference found for this event",
                "user_id": user_id,
                "event_type": event_type,
                "preference": None,
            }

        return {
            "success": True,
            "user_id": user_id,
            "event_type": event_type,
            "preference": preference,
        }

    except Exception as e:
        logger.error(f"Error in get_event_preference endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/update", summary="تحديث تفضيلات حدث - Update Event Preference")
async def update_preference(request: UpdateEventPreferenceRequest):
    """
    تحديث تفضيلات نوع حدث معين
    Update preferences for a specific event type

    Configure which channels to use for each event type.
    Available channels: email, sms, push, whatsapp, in_app
    """
    try:
        result = await PreferencesService.update_event_preference(
            user_id=request.user_id,
            event_type=request.event_type,
            channels=request.channels,
            enabled=request.enabled,
            tenant_id=request.tenant_id,
            metadata=request.metadata,
        )

        return {
            "success": True,
            "message": "تم تحديث التفضيلات بنجاح - Preferences updated successfully",
            "message_en": "Preferences updated successfully",
            "data": result,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error in update_preference endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/quiet-hours", summary="تحديد ساعات الهدوء - Set Quiet Hours")
async def set_quiet_hours(request: SetQuietHoursRequest):
    """
    تحديد ساعات الهدوء (عدم الإزعاج)
    Set quiet hours (do not disturb period)

    During quiet hours, notifications will not be sent unless they are critical priority.
    Time format: HH:MM (24-hour format)
    Example: 22:00 to 06:00 (10 PM to 6 AM)
    """
    try:
        result = await PreferencesService.set_quiet_hours(
            user_id=request.user_id,
            quiet_hours_start=request.quiet_hours_start,
            quiet_hours_end=request.quiet_hours_end,
            tenant_id=request.tenant_id,
        )

        return {
            "success": result["success"],
            "message": (
                "تم تحديث ساعات الهدوء بنجاح - Quiet hours updated successfully"
                if result["success"]
                else "فشل تحديث ساعات الهدوء - Failed to update quiet hours"
            ),
            "message_en": result["message"],
            "data": result,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error in set_quiet_hours endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/bulk-update", summary="تحديث تفضيلات متعددة - Bulk Update Preferences")
async def bulk_update_preferences(request: BulkUpdatePreferencesRequest):
    """
    تحديث تفضيلات متعددة دفعة واحدة
    Bulk update multiple preferences at once

    Useful for initial setup or updating all preferences together.
    """
    try:
        result = await PreferencesService.bulk_update_preferences(
            user_id=request.user_id,
            preferences=request.preferences,
            tenant_id=request.tenant_id,
        )

        return {
            "success": result["success"],
            "message": f"تم تحديث {result['updated_count']} تفضيل - Updated {result['updated_count']} preferences",
            "message_en": result["message"],
            "data": result,
        }

    except Exception as e:
        logger.error(f"Error in bulk_update_preferences endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
