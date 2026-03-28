"""
SAHOOL Notification Service - Preferences Controller
وحدة التحكم في تفضيلات الإشعارات - FastAPI Routes

Handles HTTP endpoints for managing user notification preferences
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .preferences_service import PreferencesService

# Import authentication dependencies
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from pydantic import BaseModel as _BaseModel

    class User(_BaseModel):  # type: ignore[no-redef]
        id: str = ""
        tenant_id: str = ""

    async def get_current_user():
        # Fail-secure: reject requests when auth module is unavailable
        raise HTTPException(
            status_code=503,
            detail="Authentication backend unavailable",
        )


logger = logging.getLogger("sahool-notifications.preferences-controller")

# Create router
# Note: No prefix - Kong handles /api/v1/preferences routing with strip_path: true
# Kong strips /api/v1/preferences, so service receives /, /update, etc.
router = APIRouter(prefix="", tags=["Preferences"])


def get_tenant_id(x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")) -> str:
    """Extract and validate tenant ID from X-Tenant-Id header - استخراج معرف المستأجر من الهيدر"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


# =============================================================================
# Request/Response Models
# =============================================================================


ALLOWED_CHANNEL_TYPES = {"email", "sms", "push", "whatsapp", "in_app"}
ALLOWED_EVENT_TYPES = {
    "weather_alert",
    "pest_outbreak",
    "irrigation_reminder",
    "crop_health",
    "market_price",
    "system",
    "task_reminder",
}


class UpdateEventPreferenceRequest(BaseModel):
    """طلب ت��ديث تفضيلات حدث - Update Event Preference Request"""

    user_id: str = Field(..., min_length=1, max_length=100, description="User ID")
    event_type: str = Field(
        ..., min_length=1, max_length=50, description="Event type (weather_alert, pest_outbreak, etc.)"
    )
    channels: list[str] = Field(..., min_length=1, description="List of channel types to use")
    enabled: bool = Field(True, description="Whether this event type is enabled")
    tenant_id: str | None = Field(None, max_length=100, description="Tenant ID for multi-tenancy")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")

    @field_validator("channels")
    @classmethod
    def validate_channels(cls, v: list[str]) -> list[str]:
        for ch in v:
            if ch not in ALLOWED_CHANNEL_TYPES:
                raise ValueError(f"Invalid channel type '{ch}'. Allowed: {', '.join(sorted(ALLOWED_CHANNEL_TYPES))}")
        return v

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, v: str) -> str:
        if v not in ALLOWED_EVENT_TYPES:
            raise ValueError(f"Invalid event type '{v}'. Allowed: {', '.join(sorted(ALLOWED_EVENT_TYPES))}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "farmer-123",
                "event_type": "weather_alert",
                "channels": ["email", "sms", "push"],
                "enabled": True,
                "tenant_id": "tenant-1",
            }
        }
    )


class SetQuietHoursRequest(BaseModel):
    """طلب تحديد ساعات الهدوء - Set Quiet Hours Request"""

    user_id: str = Field(..., min_length=1, max_length=100, description="User ID")
    quiet_hours_start: str | None = Field(
        None, pattern=r"^\d{2}:\d{2}$", description="Start time in HH:MM format (e.g., '22:00')"
    )
    quiet_hours_end: str | None = Field(
        None, pattern=r"^\d{2}:\d{2}$", description="End time in HH:MM format (e.g., '06:00')"
    )
    tenant_id: str | None = Field(None, max_length=100, description="Tenant ID for multi-tenancy")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "farmer-123",
                "quiet_hours_start": "22:00",
                "quiet_hours_end": "06:00",
                "tenant_id": "tenant-1",
            }
        }
    )


class BulkUpdatePreferencesRequest(BaseModel):
    """طلب تحديث تفضيلات متعد��ة - Bulk Update Preferences Request"""

    user_id: str = Field(..., min_length=1, max_length=100, description="User ID")
    preferences: list[dict[str, Any]] = Field(..., min_length=1, description="List of preference updates")
    tenant_id: str | None = Field(None, max_length=100, description="Tenant ID for multi-tenancy")

    model_config = ConfigDict(
        json_schema_extra={
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
    )


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/", summary="الحصول على تفضيلات المستخدم - Get User Preferences")
async def get_preferences(
    user_id: str = Query(..., description="User ID"),
    tenant_id: str = Depends(get_tenant_id),
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


@router.get("/event/{event_type}", summary="الحصول على تفضيلات حدث معين - Get Event Preference")
async def get_event_preference(
    event_type: str,
    user_id: str = Query(..., description="User ID"),
    tenant_id: str = Depends(get_tenant_id),
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
async def update_preference(
    request: UpdateEventPreferenceRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """
    تحديث تفضيلات نوع حدث معين
    Update preferences for a specific event type

    Configure which channels to use for each event type.
    Available channels: email, sms, push, whatsapp, in_app
    """
    # Enforce tenant isolation
    if hasattr(current_user, "tenant_id") and current_user.tenant_id and current_user.tenant_id != tenant_id:
        raise HTTPException(403, "Tenant mismatch")
    if hasattr(request, "user_id") and request.user_id and request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    # Enforce ownership: use authenticated user's ID
    effective_user_id = current_user.id
    try:
        result = await PreferencesService.update_event_preference(
            user_id=effective_user_id,
            event_type=request.event_type,
            channels=request.channels,
            enabled=request.enabled,
            tenant_id=tenant_id,
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
async def set_quiet_hours(
    request: SetQuietHoursRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """
    تحديد ساعات الهدوء (عدم الإزعاج)
    Set quiet hours (do not disturb period)

    During quiet hours, notifications will not be sent unless they are critical priority.
    Time format: HH:MM (24-hour format)
    Example: 22:00 to 06:00 (10 PM to 6 AM)
    """
    # Enforce tenant isolation
    if hasattr(current_user, "tenant_id") and current_user.tenant_id and current_user.tenant_id != tenant_id:
        raise HTTPException(403, "Tenant mismatch")
    if hasattr(request, "user_id") and request.user_id and request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    # Enforce ownership: use authenticated user's ID
    effective_user_id = current_user.id
    try:
        result = await PreferencesService.set_quiet_hours(
            user_id=effective_user_id,
            quiet_hours_start=request.quiet_hours_start,
            quiet_hours_end=request.quiet_hours_end,
            tenant_id=tenant_id,
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
async def bulk_update_preferences(
    request: BulkUpdatePreferencesRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user: User = Depends(get_current_user),
):
    """
    تحديث تفضيلات متعددة دفعة واحدة
    Bulk update multiple preferences at once

    Useful for initial setup or updating all preferences together.
    """
    # Enforce tenant isolation
    if hasattr(current_user, "tenant_id") and current_user.tenant_id and current_user.tenant_id != tenant_id:
        raise HTTPException(403, "Tenant mismatch")
    if hasattr(request, "user_id") and request.user_id and request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="User ID mismatch")
    # Enforce ownership: use authenticated user's ID
    effective_user_id = current_user.id
    try:
        result = await PreferencesService.bulk_update_preferences(
            user_id=effective_user_id,
            preferences=request.preferences,
            tenant_id=tenant_id,
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
