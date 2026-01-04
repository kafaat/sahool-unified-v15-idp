"""
SAHOOL Notification Service - Channels Controller
وحدة التحكم في قنوات الإشعارات - FastAPI Routes

Handles HTTP endpoints for managing user notification channels
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

from .channels_service import ChannelsService

logger = logging.getLogger("sahool-notifications.channels-controller")

# Create router
router = APIRouter(prefix="/v1/channels", tags=["Channels"])


# =============================================================================
# Request/Response Models
# =============================================================================


class AddChannelRequest(BaseModel):
    """طلب إضافة قناة - Add Channel Request"""

    user_id: str = Field(..., description="User ID")
    channel_type: str = Field(
        ..., description="Channel type: email, sms, push, whatsapp, in_app"
    )
    address: str = Field(
        ..., description="Channel address (email, phone, FCM token, etc.)"
    )
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenancy")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "farmer-123",
                "channel_type": "email",
                "address": "farmer@example.com",
                "tenant_id": "tenant-1",
                "metadata": {"device": "web"},
            }
        }


class VerifyChannelRequest(BaseModel):
    """طلب تحقق من قناة - Verify Channel Request"""

    channel_id: str = Field(..., description="Channel ID")
    verification_code: str = Field(..., description="Verification code")
    user_id: str = Field(..., description="User ID")

    class Config:
        json_schema_extra = {
            "example": {
                "channel_id": "550e8400-e29b-41d4-a716-446655440000",
                "verification_code": "123456",
                "user_id": "farmer-123",
            }
        }


class UpdateChannelStatusRequest(BaseModel):
    """طلب تحديث حالة قناة - Update Channel Status Request"""

    channel_id: str = Field(..., description="Channel ID")
    user_id: str = Field(..., description="User ID")
    enabled: bool = Field(..., description="Whether channel should be enabled")

    class Config:
        json_schema_extra = {
            "example": {
                "channel_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "farmer-123",
                "enabled": True,
            }
        }


# =============================================================================
# API Endpoints
# =============================================================================


@router.post("/add", summary="إضافة قناة إشعار - Add Notification Channel")
async def add_channel(request: AddChannelRequest):
    """
    إضافة قناة إشعار جديدة للمستخدم
    Add a new notification channel for a user

    - **email**: Requires verification via email
    - **sms**: Requires verification via SMS code
    - **whatsapp**: Requires verification via WhatsApp
    - **push**: No verification needed (FCM token)
    - **in_app**: No verification needed
    """
    try:
        result = await ChannelsService.add_channel(
            user_id=request.user_id,
            channel_type=request.channel_type,
            address=request.address,
            tenant_id=request.tenant_id,
            metadata=request.metadata,
        )

        return {
            "success": True,
            "message": "تم إضافة القناة بنجاح - Channel added successfully",
            "message_en": "Channel added successfully",
            "data": result,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error in add_channel endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/verify", summary="تحقق من قناة - Verify Channel")
async def verify_channel(request: VerifyChannelRequest):
    """
    تحقق من قناة إشعار باستخدام رمز التحقق
    Verify a notification channel using verification code

    Required for: email, sms, whatsapp channels
    """
    try:
        result = await ChannelsService.verify_channel(
            channel_id=request.channel_id,
            verification_code=request.verification_code,
            user_id=request.user_id,
        )

        return {
            "success": result["success"],
            "message": (
                "تم التحقق من القناة بنجاح - Channel verified successfully"
                if result["success"]
                else "رمز التحقق غير صحيح - Invalid verification code"
            ),
            "message_en": result["message"],
            "data": result,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error in verify_channel endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.delete("/remove", summary="حذف قناة - Remove Channel")
async def remove_channel(
    channel_id: str = Query(..., description="Channel ID"),
    user_id: str = Query(..., description="User ID"),
):
    """
    حذف قناة إشعار
    Remove a notification channel
    """
    try:
        result = await ChannelsService.remove_channel(
            channel_id=channel_id,
            user_id=user_id,
        )

        return {
            "success": result["success"],
            "message": (
                "تم حذف القناة بنجاح - Channel removed successfully"
                if result["success"]
                else "فشل حذف القناة - Failed to remove channel"
            ),
            "message_en": result["message"],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error in remove_channel endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/list", summary="قائمة قنوات المستخدم - List User Channels")
async def list_channels(
    user_id: str = Query(..., description="User ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID"),
    channel_type: Optional[str] = Query(None, description="Filter by channel type"),
    enabled_only: bool = Query(False, description="Show only enabled channels"),
):
    """
    الحصول على قائمة قنوات الإشعار للمستخدم
    Get list of notification channels for a user

    Filters:
    - **channel_type**: email, sms, push, whatsapp, in_app
    - **enabled_only**: Show only enabled channels
    """
    try:
        channels = await ChannelsService.list_user_channels(
            user_id=user_id,
            tenant_id=tenant_id,
            channel_type=channel_type,
            enabled_only=enabled_only,
        )

        return {
            "success": True,
            "user_id": user_id,
            "total": len(channels),
            "channels": channels,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error in list_channels endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.patch("/update-status", summary="تحديث حالة قناة - Update Channel Status")
async def update_channel_status(request: UpdateChannelStatusRequest):
    """
    تحديث حالة قناة (تفعيل/تعطيل)
    Update channel status (enable/disable)
    """
    try:
        result = await ChannelsService.update_channel_status(
            channel_id=request.channel_id,
            user_id=request.user_id,
            enabled=request.enabled,
        )

        return {
            "success": result["success"],
            "message": result["message"],
            "message_en": result["message"],
            "data": result,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error in update_channel_status endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e
