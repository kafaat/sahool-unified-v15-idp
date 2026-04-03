"""
SAHOOL Personalized Notification Service v15.4
خدمة الإشعارات المخصصة - تنبيهات ذكية لكل مزارع

Features:
- Personalized alerts based on farmer's crops and location
- Weather warnings (frost, heat waves, storms)
- Pest outbreak alerts in nearby areas
- Irrigation reminders
- Market price notifications
- NATS integration for real-time analysis events (Field-First)

Field-First Architecture:
- تحليل → NATS → notification-service → mobile
- Decoupling بين خدمات التحليل والإشعارات
"""

import asyncio
import html
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime
from enum import Enum, StrEnum
from typing import Any
from uuid import UUID

import structlog
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel, Field, field_validator

# Add shared middleware to path
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
sys.path.insert(0, shared_path)
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# DLQ support for failed notification delivery
try:
    from shared.events.dlq_config import DLQConfig, DLQMessageMetadata

    _dlq_config = DLQConfig.from_env()
    _dlq_available = True
except ImportError:
    _dlq_available = False
    _dlq_config = None


def sanitize_log_input(value: str) -> str:
    """Sanitize user input for safe logging to prevent log injection attacks."""
    if not isinstance(value, str):
        value = str(value)
    return value.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")


# =============================================================================
# Prometheus Metrics
# =============================================================================

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

if HAS_PROMETHEUS:
    REQUEST_COUNT = Counter(
        "notification_requests_total",
        "Total notification API requests",
        ["endpoint", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "notification_request_duration_seconds",
        "Notification API latency",
        ["endpoint"],
    )
    NOTIFICATIONS_SENT = Counter(
        "notifications_sent_total",
        "Notifications sent by channel",
        ["channel", "status"],
    )
    NOTIFICATIONS_FAILED = Counter(
        "notifications_failed_total",
        "Failed notification deliveries",
        ["channel", "reason"],
    )


# Security headers middleware
try:
    from shared.middleware.security_headers import setup_security_headers

    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False

    def setup_security_headers(app):
        pass


# CORS configuration via shared module
try:
    from shared.cors_config import setup_cors_middleware

    CORS_SETUP_AVAILABLE = True
except ImportError:
    CORS_SETUP_AVAILABLE = False


from shared.middleware.tenant_context import TenantContextMiddleware

# Import authentication dependencies
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    AUTH_AVAILABLE = True
except ImportError:
    # Fallback if auth module not available
    AUTH_AVAILABLE = False

    from fastapi import HTTPException as _HTTPException

    class User(BaseModel):  # type: ignore[no-redef]
        id: str = ""
        tenant_id: str | None = None

    async def get_current_user():
        """Placeholder when auth not available"""
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


# Database imports
# Multi-channel support
# New enhanced components (v16.0)
from .analytics_controller import router as analytics_router
from .channels_controller import router as channels_router
from .database import check_db_health, close_db, get_db_stats, init_notification_db
from .delivery_tracker import get_delivery_tracker
from .email_client import get_email_client
from .history_controller import router as history_router
from .otp_controller import router as otp_router
from .preferences_controller import router as preferences_router
from .preferences_service import PreferencesService
from .queue_processor import get_queue_processor
from .repository import (
    FarmerProfileRepository,
    NotificationLogRepository,
    NotificationPreferenceRepository,
    NotificationRepository,
)

# Notification clients
from .sms_client import get_sms_client
from .sms_providers import get_multi_sms_client
from .telegram_client import get_telegram_client
from .whatsapp_client import get_whatsapp_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = structlog.get_logger("sahool-notifications")

# =============================================================================
# Enums & Models
# =============================================================================


class NotificationType(StrEnum):
    WEATHER_ALERT = "weather_alert"
    PEST_OUTBREAK = "pest_outbreak"
    IRRIGATION_REMINDER = "irrigation_reminder"
    CROP_HEALTH = "crop_health"
    MARKET_PRICE = "market_price"
    SYSTEM = "system"
    TASK_REMINDER = "task_reminder"


class NotificationPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(StrEnum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"


class DevicePlatform(StrEnum):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


# Allowed notification channel types for validation
ALLOWED_CHANNEL_TYPES = {ch.value for ch in NotificationChannel}


def sanitize_notification_content(text: str) -> str:
    """Sanitize notification content to prevent XSS in push notifications."""
    if not isinstance(text, str):
        text = str(text)
    return html.escape(text)


class Governorate(StrEnum):
    SANAA = "sanaa"
    ADEN = "aden"
    TAIZ = "taiz"
    HODEIDAH = "hodeidah"
    IBB = "ibb"
    DHAMAR = "dhamar"
    HADRAMAUT = "hadramaut"
    MARIB = "marib"
    HAJJAH = "hajjah"
    SAADA = "saada"
    LAHJ = "lahj"
    ABYAN = "abyan"


class CropType(StrEnum):
    TOMATO = "tomato"
    WHEAT = "wheat"
    COFFEE = "coffee"
    QAT = "qat"
    BANANA = "banana"
    DATE_PALM = "date_palm"
    MANGO = "mango"
    GRAPES = "grapes"
    CORN = "corn"
    POTATO = "potato"


# Arabic translations
NOTIFICATION_TYPE_AR = {
    NotificationType.WEATHER_ALERT: "تنبيه طقس",
    NotificationType.PEST_OUTBREAK: "انتشار آفات",
    NotificationType.IRRIGATION_REMINDER: "تذكير ري",
    NotificationType.CROP_HEALTH: "صحة المحصول",
    NotificationType.MARKET_PRICE: "أسعار السوق",
    NotificationType.SYSTEM: "نظام",
    NotificationType.TASK_REMINDER: "تذكير مهمة",
}

PRIORITY_AR = {
    NotificationPriority.LOW: "منخفضة",
    NotificationPriority.MEDIUM: "متوسطة",
    NotificationPriority.HIGH: "عالية",
    NotificationPriority.CRITICAL: "حرجة",
}

GOVERNORATE_AR = {
    Governorate.SANAA: "صنعاء",
    Governorate.ADEN: "عدن",
    Governorate.TAIZ: "تعز",
    Governorate.HODEIDAH: "الحديدة",
    Governorate.IBB: "إب",
    Governorate.DHAMAR: "ذمار",
    Governorate.HADRAMAUT: "حضرموت",
    Governorate.MARIB: "مأرب",
    Governorate.HAJJAH: "حجة",
    Governorate.SAADA: "صعدة",
    Governorate.LAHJ: "لحج",
    Governorate.ABYAN: "أبين",
}

CROP_AR = {
    CropType.TOMATO: "طماطم",
    CropType.WHEAT: "قمح",
    CropType.COFFEE: "بن",
    CropType.QAT: "قات",
    CropType.BANANA: "موز",
    CropType.DATE_PALM: "نخيل",
    CropType.MANGO: "مانجو",
    CropType.GRAPES: "عنب",
    CropType.CORN: "ذرة",
    CropType.POTATO: "بطاطس",
}


# =============================================================================
# Request/Response Models
# =============================================================================


class FarmerProfile(BaseModel):
    """ملف المزارع للإشعارات المخصصة"""

    farmer_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str = Field(..., min_length=1, max_length=200)
    governorate: Governorate
    district: str | None = Field(None, max_length=200)
    crops: list[CropType]
    field_ids: list[str] = []
    phone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=254)
    fcm_token: str | None = Field(None, min_length=10, max_length=500)  # Firebase Cloud Messaging
    device_platform: DevicePlatform | None = None
    notification_channels: list[NotificationChannel] = [NotificationChannel.IN_APP]
    language: str = Field("ar", max_length=10)

    @field_validator("name", "name_ar")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        return sanitize_notification_content(v)


class NotificationPreferences(BaseModel):
    """تفضيلات الإشعارات"""

    farmer_id: str = Field(..., min_length=1, max_length=100)
    weather_alerts: bool = True
    pest_alerts: bool = True
    irrigation_reminders: bool = True
    crop_health_alerts: bool = True
    market_prices: bool = True
    quiet_hours_start: str | None = "22:00"  # HH:MM
    quiet_hours_end: str | None = "06:00"
    min_priority: NotificationPriority = NotificationPriority.LOW


class Notification(BaseModel):
    """إشعار"""

    id: str
    type: NotificationType
    type_ar: str = Field(..., max_length=200)
    priority: NotificationPriority
    priority_ar: str = Field(..., max_length=200)
    title: str = Field(..., max_length=200)
    title_ar: str = Field(..., max_length=200)
    body: str = Field(..., max_length=2000)
    body_ar: str = Field(..., max_length=2000)
    data: dict[str, Any] = {}
    target_farmers: list[str] = []  # Empty = broadcast
    target_governorates: list[Governorate] = []
    target_crops: list[CropType] = []
    channels: list[NotificationChannel] = [NotificationChannel.IN_APP]
    created_at: datetime
    expires_at: datetime | None = None
    is_read: bool = False
    action_url: str | None = Field(None, max_length=2000)


class CreateNotificationRequest(BaseModel):
    """طلب إنشاء إشعار"""

    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str = Field(..., min_length=1, max_length=200)
    title_ar: str = Field(..., min_length=1, max_length=200)
    body: str = Field(..., min_length=1, max_length=2000)
    body_ar: str = Field(..., min_length=1, max_length=2000)
    data: dict[str, Any] = {}
    target_farmers: list[str] = Field(default=[])
    target_governorates: list[Governorate] = []
    target_crops: list[CropType] = []
    channels: list[NotificationChannel] = [NotificationChannel.IN_APP]
    expires_in_hours: int | None = Field(24, ge=1, le=8760)

    @field_validator("title", "title_ar", "body", "body_ar")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Sanitize notification content to prevent XSS in push notifications."""
        return sanitize_notification_content(v)

    @field_validator("target_farmers")
    @classmethod
    def validate_target_farmers(cls, v: list[str]) -> list[str]:
        for fid in v:
            if not fid or len(fid) > 100:
                raise ValueError("Each farmer_id must be between 1 and 100 characters")
        return v


class WeatherAlertRequest(BaseModel):
    """طلب تنبيه طقس"""

    governorates: list[Governorate] = Field(..., min_length=1)
    alert_type: str = Field(..., min_length=1, max_length=50)
    severity: NotificationPriority
    expected_date: date
    details: dict[str, Any] = {}

    @field_validator("alert_type")
    @classmethod
    def sanitize_alert_type(cls, v: str) -> str:
        return sanitize_notification_content(v)


class PestAlertRequest(BaseModel):
    """طلب تنبيه آفات"""

    governorate: Governorate
    pest_name: str = Field(..., min_length=1, max_length=200)
    pest_name_ar: str = Field(..., min_length=1, max_length=200)
    affected_crops: list[CropType] = Field(..., min_length=1)
    severity: NotificationPriority
    recommendations: list[str] = []
    recommendations_ar: list[str] = []

    @field_validator("pest_name", "pest_name_ar")
    @classmethod
    def sanitize_pest_names(cls, v: str) -> str:
        return sanitize_notification_content(v)

    @field_validator("recommendations", "recommendations_ar")
    @classmethod
    def sanitize_recommendations(cls, v: list[str]) -> list[str]:
        return [sanitize_notification_content(r) for r in v]


class IrrigationReminderRequest(BaseModel):
    """طلب تذكير ري"""

    farmer_id: str = Field(..., min_length=1, max_length=100)
    field_id: str = Field(..., min_length=1, max_length=100)
    field_name: str = Field(..., min_length=1, max_length=200)
    crop: CropType
    water_needed_mm: float = Field(..., gt=0, le=500)
    urgency: NotificationPriority

    @field_validator("field_name")
    @classmethod
    def sanitize_field_name(cls, v: str) -> str:
        return sanitize_notification_content(v)


# =============================================================================
# Database Storage - MIGRATED TO POSTGRESQL ✅
# =============================================================================

# ✅ MIGRATION COMPLETED - All farmer data now stored in PostgreSQL
#
# Previous in-memory storage has been migrated to the following database tables:
#   - farmer_profiles: Main farmer information (id, farmer_id, name, governorate, etc.)
#   - farmer_crops: Junction table for farmer's crops (farmer_id, crop_type)
#   - farmer_fields: Junction table for farmer's fields (farmer_id, field_id)
#
# Database operations are handled by FarmerProfileRepository in repository.py
#
# Changes made:
#   ✅ Created FarmerProfile, FarmerCrop, FarmerField models in models.py
#   ✅ Created FarmerProfileRepository in repository.py
#   ✅ Updated /v1/farmers/register endpoint to use FarmerProfileRepository.create()
#   ✅ Updated determine_recipients_by_criteria() to query database
#   ✅ Updated all send_*_notification() functions to query database
#   ✅ Updated /healthz and /v1/stats endpoints to query database
#
# Note: NOTIFICATIONS and FARMER_NOTIFICATIONS were already using NotificationRepository
# and have been removed as they were redundant legacy code.
#
# Migration completed: 2026-01-08

# Legacy compatibility: in-memory cache used by send_*_notification functions
# when database is unavailable (e.g., during testing)
FARMER_PROFILES: dict[str, Any] = {}

# =============================================================================
# Notification Logic
# =============================================================================


async def _publish_to_dlq(send_func_name: str, error: Exception, max_retries: int, kwargs: dict[str, Any]):
    """Publish failed notification to dead-letter queue for manual retry."""
    import json
    import traceback

    dlq_subject = "sahool.dlq.notification.delivery.failed"
    notification = kwargs.get("notification")
    channel = kwargs.get("channel")
    farmer_id = kwargs.get("farmer_id")

    # Build DLQ payload
    if _dlq_available:
        metadata = DLQMessageMetadata(
            original_subject="sahool.notification.send",
            retry_count=max_retries,
            failure_reason=str(error),
            failure_timestamp=datetime.now(UTC).isoformat(),
            error_type=error.__class__.__name__,
            error_traceback=traceback.format_exc()[:1000],
            consumer_service="notification-service",
            consumer_version="16.0.0",
            handler_function=send_func_name,
        )
        dlq_subject = _dlq_config.get_dlq_subject("sahool.notification.delivery.failed")
        dlq_payload = {
            "metadata": metadata.model_dump(),
            "original_message": json.dumps(
                {
                    "notification_id": str(getattr(notification, "id", "")),
                    "channel": str(channel) if channel else None,
                    "farmer_id": farmer_id,
                },
                default=str,
            ),
        }
    else:
        dlq_payload = {
            "metadata": {
                "original_subject": "sahool.notification.send",
                "retry_count": max_retries,
                "failure_reason": str(error),
                "failure_timestamp": datetime.now(UTC).isoformat(),
                "error_type": error.__class__.__name__,
                "consumer_service": "notification-service",
                "handler_function": send_func_name,
            },
            "original_message": json.dumps(
                {
                    "notification_id": str(getattr(notification, "id", "")),
                    "channel": str(channel) if channel else None,
                    "farmer_id": farmer_id,
                },
                default=str,
            ),
        }

    # Try to publish to NATS DLQ stream
    published = False
    if _nats_subscriber and hasattr(_nats_subscriber, "_nc") and _nats_subscriber._nc:
        try:
            await _nats_subscriber._nc.publish(
                dlq_subject,
                json.dumps(dlq_payload, default=str).encode("utf-8"),
            )
            published = True
            logger.warning(
                "notification_moved_to_dlq",
                dlq_subject=dlq_subject,
                notification_id=str(getattr(notification, "id", "")),
                channel=str(channel) if channel else None,
                farmer_id=farmer_id,
                error_type=error.__class__.__name__,
            )
        except Exception as dlq_error:
            logger.error(
                "notification_dlq_publish_failed",
                dlq_error=str(dlq_error),
                original_error=str(error),
            )

    if not published:
        # Fallback: structured log for manual recovery when NATS is unavailable
        logger.error(
            "notification_dlq_fallback",
            dlq_subject=dlq_subject,
            notification_id=str(getattr(notification, "id", "")),
            channel=str(channel) if channel else None,
            farmer_id=farmer_id,
            error_type=error.__class__.__name__,
            error=str(error),
            retries=max_retries,
            dlq_payload=json.dumps(dlq_payload, default=str),
        )


async def _send_with_retry(send_func, *args, max_retries=3, **kwargs):
    """Send notification with retry on failure."""
    for attempt in range(max_retries):
        try:
            result = await send_func(*args, **kwargs)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2**attempt  # exponential backoff: 1, 2, 4 seconds
                logger.warning(
                    "notification_send_retry",
                    attempt=attempt + 1,
                    max=max_retries,
                    wait=wait,
                    error=str(e),
                )
                await asyncio.sleep(wait)
            else:
                logger.error(
                    "notification_send_failed_all_retries",
                    error=str(e),
                    retries=max_retries,
                )
                await _publish_to_dlq(
                    send_func_name=getattr(send_func, "__name__", "unknown"),
                    error=e,
                    max_retries=max_retries,
                    kwargs=kwargs,
                )
                raise


async def create_notification(
    type: NotificationType,
    priority: NotificationPriority,
    title: str,
    title_ar: str,
    body: str,
    body_ar: str,
    data: dict[str, Any] = None,
    target_farmers: list[str] = None,
    target_governorates: list[Governorate] = None,
    target_crops: list[CropType] = None,
    channels: list[NotificationChannel] = None,
    expires_in_hours: int | None = 24,
    tenant_id: str | None = None,
):
    """إنشاء إشعار جديد - Database version with preference checking"""

    # Sanitize notification content to prevent XSS (defense in depth)
    title = sanitize_notification_content(title)
    title_ar = sanitize_notification_content(title_ar)
    body = sanitize_notification_content(body)
    body_ar = sanitize_notification_content(body_ar)

    # Determine target farmers based on criteria
    if channels is None:
        channels = [NotificationChannel.IN_APP]
    if target_crops is None:
        target_crops = []
    if target_governorates is None:
        target_governorates = []
    if target_farmers is None:
        target_farmers = []
    if data is None:
        data = {}
    recipients = await determine_recipients_by_criteria(
        target_farmers=target_farmers,
        target_governorates=target_governorates,
        target_crops=target_crops,
    )

    # Create notification for each recipient
    notifications = []
    for farmer_id in recipients:
        # Check user preferences for this event type
        should_send, preferred_channels = await PreferencesService.check_if_should_send(
            user_id=farmer_id,
            event_type=type.value,
            tenant_id=tenant_id,
        )

        if not should_send:
            logger.debug(
                f"Skipping notification for user {sanitize_log_input(farmer_id)} - event type disabled in preferences"
            )
            continue

        # Use preferred channels if available, otherwise use provided channels
        final_channels = preferred_channels if preferred_channels else [ch.value for ch in channels]

        # Get primary channel from list
        channel = final_channels[0] if final_channels else "in_app"

        notification = await NotificationRepository.create(
            user_id=farmer_id,
            title=title,
            title_ar=title_ar,
            body=body,
            body_ar=body_ar,
            type=type.value,
            channel=channel,
            priority=priority.value,
            tenant_id=tenant_id,
            data={
                **data,
                "type_ar": NOTIFICATION_TYPE_AR[type],
                "priority_ar": PRIORITY_AR[priority],
                "channels": final_channels,
            },
            target_governorates=([g.value for g in target_governorates] if target_governorates else None),
            target_crops=[c.value for c in target_crops] if target_crops else None,
            expires_in_hours=expires_in_hours,
        )
        notifications.append(notification)

        # Send notifications via appropriate channels (async background task with retry)
        for channel_name in final_channels:
            try:
                # Convert channel name string to enum
                channel_enum = NotificationChannel(channel_name)
                task = asyncio.create_task(
                    _send_with_retry(
                        send_notification_via_channel,
                        notification=notification,
                        channel=channel_enum,
                        farmer_id=notification.user_id,
                    ),
                    name=f"send_{channel_name}_{notification.id}",
                )
                # Log if all retries exhausted
                task.add_done_callback(
                    lambda t: (
                        logger.error(
                            "notification_delivery_exhausted",
                            error=str(t.exception()),
                        )
                        if t.exception()
                        else None
                    )
                )
            except ValueError:
                logger.warning(f"Invalid channel type: {channel_name}")
                continue

    logger.info(f"📬 Created {len(notifications)} notification(s) for {len(recipients)} farmer(s)")

    # Return first notification for API response compatibility
    return notifications[0] if notifications else None


async def send_notification_via_channel(
    notification,
    channel: NotificationChannel,
    farmer_id: str,
):
    """
    إرسال إشعار عبر قناة معينة
    Send notification via specific channel (SMS, Email, Push, or WhatsApp)
    """
    try:
        if channel == NotificationChannel.SMS:
            await send_sms_notification(notification, farmer_id)
        elif channel == NotificationChannel.EMAIL:
            await send_email_notification(notification, farmer_id)
        elif channel == NotificationChannel.PUSH:
            await send_push_notification(notification, farmer_id)
        elif channel == NotificationChannel.WHATSAPP:
            await send_whatsapp_notification(notification, farmer_id)
        # IN_APP notifications are already stored in database, no action needed

    except Exception as e:
        logger.error(f"Failed to send notification via {channel.value}: {e}")
        # Log the failure
        await NotificationLogRepository.create_log(
            notification_id=notification.id,
            channel=channel.value,
            status="failed",
            error_message=str(e),
        )


async def send_sms_notification(notification, farmer_id: str):
    """إرسال إشعار عبر SMS - Database version"""
    try:
        # Get farmer profile from database to get phone number
        farmer_profile = await FarmerProfileRepository.get_by_farmer_id(farmer_id)
        if not farmer_profile or not farmer_profile.phone:
            logger.warning(f"No phone number for farmer {sanitize_log_input(farmer_id)}")
            await NotificationLogRepository.create_log(
                notification_id=notification.id,
                channel="sms",
                status="failed",
                error_message="No phone number available",
            )
            return

        # Get SMS client
        sms_client = get_sms_client()
        if not sms_client._initialized:
            logger.warning("SMS client not initialized, skipping SMS notification")
            return

        # Send SMS
        language = farmer_profile.language if hasattr(farmer_profile, "language") else "ar"
        message_sid = await sms_client.send_sms(
            to=farmer_profile.phone,
            body=notification.title + "\n" + notification.body,
            body_ar=notification.title_ar + "\n" + notification.body_ar,
            language=language,
        )

        if message_sid:
            # Update notification status
            await NotificationRepository.update_status(
                notification.id,
                status="sent",
                sent_at=datetime.now(UTC),
            )
            # Log success
            await NotificationLogRepository.create_log(
                notification_id=notification.id,
                channel="sms",
                status="sent",
                provider_message_id=message_sid,
            )
            logger.info(
                f"✅ SMS sent to ***{farmer_profile.phone[-4:] if farmer_profile.phone else '****'}: {message_sid}"
            )
        else:
            raise Exception("Failed to send SMS (no message_sid returned)")

    except Exception as e:
        logger.error(f"Error sending SMS notification: {e}")
        await NotificationLogRepository.create_log(
            notification_id=notification.id,
            channel="sms",
            status="failed",
            error_message=str(e),
        )


async def send_email_notification(notification, farmer_id: str):
    """إرسال إشعار عبر البريد الإلكتروني - Database version"""
    try:
        # Get farmer profile from database to get email address
        farmer_profile = await FarmerProfileRepository.get_by_farmer_id(farmer_id)
        if not farmer_profile or not farmer_profile.email:
            logger.warning(f"No email address for farmer {sanitize_log_input(farmer_id)}")
            await NotificationLogRepository.create_log(
                notification_id=notification.id,
                channel="email",
                status="failed",
                error_message="No email address available",
            )
            return

        # Get Email client
        email_client = get_email_client()
        if not email_client._initialized:
            logger.warning("Email client not initialized, skipping email notification")
            return

        # Send Email
        language = farmer_profile.language if hasattr(farmer_profile, "language") else "ar"

        # Build separate HTML bodies for each language.
        # Notification title/body were sanitised with html.escape() during creation,
        # so they must be unescape'd before insertion into the HTML template to avoid
        # double-escaping (e.g. "&amp;" appearing in rendered email).
        title_en = html.unescape(notification.title)
        title_ar_text = html.unescape(notification.title_ar or notification.title)
        body_en = html.unescape(notification.body)
        body_ar_text = html.unescape(notification.body_ar or notification.body)

        html_body_en = f"""
        <html>
            <body dir="ltr">
                <h2>{html.escape(title_en)}</h2>
                <p>{html.escape(body_en)}</p>
                <br>
                <p style="color: #666; font-size: 12px;">
                    This is an automated message from SAHOOL Agriculture Platform
                </p>
            </body>
        </html>
        """

        html_body_ar = f"""
        <html>
            <body dir="rtl">
                <h2>{html.escape(title_ar_text)}</h2>
                <p>{html.escape(body_ar_text)}</p>
                <br>
                <p style="color: #666; font-size: 12px;">
                    هذه رسالة آلية من منصة SAHOOL الزراعية
                </p>
            </body>
        </html>
        """

        message_id = await email_client.send_email(
            to=farmer_profile.email,
            subject=notification.title,
            subject_ar=notification.title_ar,
            body=html_body_en,
            body_ar=html_body_ar,
            language=language,
            is_html=True,
        )

        if message_id:
            # Update notification status
            await NotificationRepository.update_status(
                notification.id,
                status="sent",
                sent_at=datetime.now(UTC),
            )
            # Log success
            await NotificationLogRepository.create_log(
                notification_id=notification.id,
                channel="email",
                status="sent",
                provider_message_id=message_id,
            )
            logger.info(
                f"✅ Email sent to ***@{farmer_profile.email.split('@')[-1] if farmer_profile.email and '@' in farmer_profile.email else '***'}: {message_id}"
            )
        else:
            raise Exception("Failed to send email (no message_id returned)")

    except Exception as e:
        logger.error(f"Error sending email notification: {e}")
        await NotificationLogRepository.create_log(
            notification_id=notification.id,
            channel="email",
            status="failed",
            error_message=str(e),
        )


async def send_push_notification(notification, farmer_id: str):
    """إرسال إشعار عبر Firebase Push - Database version"""
    try:
        # Get farmer profile from database to get FCM token
        farmer_profile = await FarmerProfileRepository.get_by_farmer_id(farmer_id)
        if not farmer_profile or not farmer_profile.fcm_token:
            logger.warning(f"No FCM token for farmer {sanitize_log_input(farmer_id)}")
            await NotificationLogRepository.create_log(
                notification_id=notification.id,
                channel="push",
                status="failed",
                error_message="No FCM token available",
            )
            return

        # Get Firebase client (assuming it's available from firebase_client.py)
        from .firebase_client import get_firebase_client

        firebase_client = get_firebase_client()
        if not firebase_client._initialized:
            logger.warning("Firebase client not initialized, skipping push notification")
            return

        # Determine priority
        from .notification_types import NotificationPriority as NPriority

        priority_map = {
            "low": NPriority.LOW,
            "medium": NPriority.MEDIUM,
            "high": NPriority.HIGH,
            "critical": NPriority.CRITICAL,
        }
        priority = priority_map.get(notification.priority, NPriority.MEDIUM)

        # Send push notification — Firebase Admin SDK is synchronous; run in thread pool
        # to avoid blocking the asyncio event loop.
        message_id = await asyncio.to_thread(
            firebase_client.send_notification,
            token=farmer_profile.fcm_token,
            title=notification.title,
            body=notification.body,
            title_ar=notification.title_ar,
            body_ar=notification.body_ar,
            # FCM data payload only accepts string values (Firebase API requirement)
            data={k: str(v) for k, v in (notification.data or {}).items()},
            priority=priority,
        )

        if message_id:
            # Update notification status
            await NotificationRepository.update_status(
                notification.id,
                status="sent",
                sent_at=datetime.now(UTC),
            )
            # Log success
            await NotificationLogRepository.create_log(
                notification_id=notification.id,
                channel="push",
                status="sent",
                provider_message_id=message_id,
            )
            logger.info(
                f"Push notification sent to {sanitize_log_input(farmer_id)}: {sanitize_log_input(str(message_id))}"
            )
        else:
            raise Exception("Failed to send push notification")

    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        await NotificationLogRepository.create_log(
            notification_id=notification.id,
            channel="push",
            status="failed",
            error_message=str(e),
        )


async def send_whatsapp_notification(notification, farmer_id: str):
    """إرسال إشعار عبر WhatsApp - Database version"""
    try:
        # Get farmer profile from database to get WhatsApp number
        farmer_profile = await FarmerProfileRepository.get_by_farmer_id(farmer_id)
        if not farmer_profile or not farmer_profile.phone:
            logger.warning(f"No WhatsApp number for farmer {sanitize_log_input(farmer_id)}")
            await NotificationLogRepository.create_log(
                notification_id=notification.id,
                channel="whatsapp",
                status="failed",
                error_message="No WhatsApp number available",
            )
            return

        # Get WhatsApp client
        whatsapp_client = get_whatsapp_client()
        if not whatsapp_client._initialized:
            logger.warning("WhatsApp client not initialized, skipping WhatsApp notification")
            await NotificationLogRepository.create_log(
                notification_id=notification.id,
                channel="whatsapp",
                status="pending",
                error_message="WhatsApp client not configured",
            )
            return

        # Send WhatsApp message
        language = farmer_profile.language if hasattr(farmer_profile, "language") else "ar"
        message_sid = await whatsapp_client.send_message(
            to=farmer_profile.phone,
            body=notification.title + "\n" + notification.body,
            body_ar=notification.title_ar + "\n" + notification.body_ar,
            language=language,
        )

        if message_sid:
            # Update notification status
            await NotificationRepository.update_status(
                notification.id,
                status="sent",
                sent_at=datetime.now(UTC),
            )
            # Log success
            await NotificationLogRepository.create_log(
                notification_id=notification.id,
                channel="whatsapp",
                status="sent",
                provider_message_id=message_sid,
            )
            logger.info(
                f"✅ WhatsApp sent to ***{farmer_profile.phone[-4:] if farmer_profile.phone else '****'}: {message_sid}"
            )
        else:
            raise Exception("Failed to send WhatsApp message (no message_sid returned)")

    except Exception as e:
        logger.error(f"Error sending WhatsApp notification: {e}")
        await NotificationLogRepository.create_log(
            notification_id=notification.id,
            channel="whatsapp",
            status="failed",
            error_message=str(e),
        )


async def determine_recipients_by_criteria(
    target_farmers: list[str] = None,
    target_governorates: list[Governorate] = None,
    target_crops: list[CropType] = None,
) -> list[str]:
    """تحديد المستلمين بناءً على معايير الإشعار - Database version"""
    # If specific farmers targeted, return them
    if target_crops is None:
        target_crops = []
    if target_governorates is None:
        target_governorates = []
    if target_farmers is None:
        target_farmers = []
    if target_farmers:
        return target_farmers

    # Convert enums to strings for database query
    governorates_list = [g.value for g in target_governorates] if target_governorates else None
    crops_list = [c.value for c in target_crops] if target_crops else None

    # Query database for matching farmers
    try:
        profiles = await FarmerProfileRepository.find_by_criteria(
            governorates=governorates_list,
            crops=crops_list,
            is_active=True,
        )

        # Extract farmer IDs
        recipients = [profile.farmer_id for profile in profiles]

        # If no farmers match and no criteria specified, return all registered farmers (broadcast)
        if not recipients and not target_governorates and not target_crops:
            all_profiles = await FarmerProfileRepository.get_all(is_active=True, limit=1000)
            recipients = [profile.farmer_id for profile in all_profiles]

        return recipients

    except Exception as e:
        logger.error(f"Error determining recipients from database: {e}")
        # Fallback to empty list if database query fails
        return []


def get_weather_alert_message(alert_type: str, governorate: Governorate) -> tuple:
    """الحصول على رسالة تنبيه الطقس"""
    gov_ar = GOVERNORATE_AR[governorate]

    messages = {
        "frost": (
            f"Frost Warning in {governorate.value}",
            f"⚠️ تحذير من الصقيع في {gov_ar}",
            "Expected frost tonight. Protect your crops by covering them or using heating methods.",
            "يُتوقع صقيع الليلة. قم بحماية محاصيلك بتغطيتها أو استخدام طرق التدفئة. درجات الحرارة قد تنخفض إلى ما دون الصفر.",
        ),
        "heat_wave": (
            f"Heat Wave Alert in {governorate.value}",
            f"🌡️ تنبيه موجة حر في {gov_ar}",
            "Extreme heat expected. Increase irrigation and provide shade for sensitive crops.",
            "متوقع حرارة شديدة. زِد من الري ووفر الظل للمحاصيل الحساسة. تجنب العمل في الحقل خلال ساعات الذروة.",
        ),
        "storm": (
            f"Storm Warning in {governorate.value}",
            f"🌧️ تحذير من عاصفة في {gov_ar}",
            "Heavy rain and strong winds expected. Secure equipment and protect vulnerable crops.",
            "متوقع أمطار غزيرة ورياح قوية. أمّن المعدات واحمِ المحاصيل المعرضة للخطر.",
        ),
        "flood": (
            f"Flood Risk in {governorate.value}",
            f"🌊 خطر فيضان في {gov_ar}",
            "Flood risk due to heavy rainfall. Move equipment to higher ground and check drainage.",
            "خطر فيضان بسبب الأمطار الغزيرة. انقل المعدات لمناطق مرتفعة وتحقق من الصرف.",
        ),
        "drought": (
            f"Drought Alert in {governorate.value}",
            f"☀️ تنبيه جفاف في {gov_ar}",
            "Extended dry period expected. Conserve water and prioritize essential irrigation.",
            "متوقع فترة جفاف ممتدة. حافظ على المياه وأعطِ الأولوية للري الضروري.",
        ),
    }

    return messages.get(
        alert_type,
        (
            f"Weather Alert in {governorate.value}",
            f"⚠️ تنبيه طقس في {gov_ar}",
            "Check weather conditions and take necessary precautions.",
            "تحقق من حالة الطقس واتخذ الاحتياطات اللازمة.",
        ),
    )


# =============================================================================
# NATS Integration (Field-First Architecture)
# =============================================================================

# NATS subscriber (optional)
_nats_subscriber = None
try:
    from .nats_subscriber import start_subscription, stop_subscription

    _nats_available = True
except ImportError:
    _nats_available = False
    logger.info("NATS subscriber not available - running in REST-only mode")


async def create_notification_from_nats(notification_data: dict[str, Any]):
    """Callback for NATS subscriber to create notifications"""
    try:
        # Map notification type string to enum
        type_mapping = {
            "weather_alert": NotificationType.WEATHER_ALERT,
            "pest_outbreak": NotificationType.PEST_OUTBREAK,
            "irrigation_reminder": NotificationType.IRRIGATION_REMINDER,
            "crop_health": NotificationType.CROP_HEALTH,
            "market_price": NotificationType.MARKET_PRICE,
            "system": NotificationType.SYSTEM,
            "task_reminder": NotificationType.TASK_REMINDER,
        }

        priority_mapping = {
            "low": NotificationPriority.LOW,
            "medium": NotificationPriority.MEDIUM,
            "high": NotificationPriority.HIGH,
            "critical": NotificationPriority.CRITICAL,
        }

        channel_mapping = {
            "push": NotificationChannel.PUSH,
            "sms": NotificationChannel.SMS,
            "email": NotificationChannel.EMAIL,
            "in_app": NotificationChannel.IN_APP,
        }

        ntype = type_mapping.get(notification_data.get("type", "system"), NotificationType.SYSTEM)
        priority = priority_mapping.get(notification_data.get("priority", "medium"), NotificationPriority.MEDIUM)
        channels = [
            channel_mapping.get(ch, NotificationChannel.IN_APP) for ch in notification_data.get("channels", ["in_app"])
        ]

        await create_notification(
            type=ntype,
            priority=priority,
            title=notification_data.get("title", "Notification"),
            title_ar=notification_data.get("title_ar", "إشعار"),
            body=notification_data.get("body", ""),
            body_ar=notification_data.get("body_ar", ""),
            data=notification_data.get("data", {}),
            target_farmers=notification_data.get("target_farmers", []),
            channels=channels,
            expires_in_hours=notification_data.get("expires_in_hours", 24),
            tenant_id=notification_data.get("tenant_id"),
        )
        logger.info("NATS: Created notification from analysis event")
    except Exception as e:
        logger.error(f"NATS: Failed to create notification: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - manage database and NATS connections"""
    global _nats_subscriber

    # Startup
    logger.info("🚀 Starting Notification Service...")

    # Initialize database (non-blocking - service can still start)
    try:
        # In production, set CREATE_DB_SCHEMA=false and use migrations
        create_schema = os.getenv("CREATE_DB_SCHEMA", "false").lower() == "true"
        await init_notification_db(create_schema=create_schema)
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning("⚠️ Database initialization failed (service will continue): %s", e)
        # Don't raise - allow service to start in degraded mode

    # Start NATS subscriber (optional)
    if _nats_available:
        try:
            _nats_subscriber = await start_subscription(create_notification_from_nats)
            logger.info("✅ NATS subscriber started")
        except Exception as e:
            logger.warning("⚠️  Failed to start NATS subscriber: %s", e)

    # Initialize SMS client (optional)
    try:
        sms_client = get_sms_client()
        if sms_client._initialized:
            logger.info("✅ SMS client initialized")
        else:
            logger.info("ℹ️  SMS client not configured (set TWILIO_* env vars to enable)")
    except Exception as e:
        logger.warning(f"⚠️  Failed to initialize SMS client: {e}")

    # Initialize Email client (optional)
    try:
        email_client = get_email_client()
        if email_client._initialized:
            logger.info("✅ Email client initialized")
        else:
            logger.info("ℹ️  Email client not configured (set SENDGRID_* env vars to enable)")
    except Exception as e:
        logger.warning(f"⚠️  Failed to initialize Email client: {e}")

    # Initialize WhatsApp client (optional)
    try:
        whatsapp_client = get_whatsapp_client()
        if whatsapp_client._initialized:
            logger.info("✅ WhatsApp client initialized")
        else:
            logger.info("ℹ️  WhatsApp client not configured (set TWILIO_WHATSAPP_NUMBER or META_WHATSAPP_* env vars)")
    except Exception as e:
        logger.warning(f"⚠️  Failed to initialize WhatsApp client: {e}")

    # Initialize Telegram client (optional)
    try:
        telegram_client = get_telegram_client()
        if telegram_client._initialized:
            logger.info("✅ Telegram client initialized")
        else:
            logger.info("ℹ️  Telegram client not configured (set TELEGRAM_BOT_TOKEN env var)")
    except Exception as e:
        logger.warning(f"⚠️  Failed to initialize Telegram client: {e}")

    # Initialize multi-provider SMS client
    try:
        multi_sms = get_multi_sms_client()
        if multi_sms._initialized:
            available = multi_sms.get_available_providers()
            logger.info(f"✅ Multi-provider SMS initialized with: {', '.join(available)}")
    except Exception as e:
        logger.warning(f"⚠️  Failed to initialize multi-provider SMS: {e}")

    # Initialize delivery tracker (v16.0)
    try:
        delivery_tracker = get_delivery_tracker()
        await delivery_tracker.start()
        logger.info("✅ Delivery tracker initialized")
    except Exception as e:
        logger.warning(f"⚠️  Failed to initialize delivery tracker: {e}")

    # Initialize Redis queue processor (v16.0 - optional)
    queue_processor = None
    if os.getenv("REDIS_URL"):
        try:
            queue_processor = get_queue_processor()
            connected = await queue_processor.connect()
            if connected:
                await queue_processor.start(num_workers=4)
                logger.info("✅ Redis queue processor started with 4 workers")
            else:
                logger.warning("⚠️  Redis queue processor failed to connect")
        except Exception as e:
            logger.warning(f"⚠️  Failed to initialize queue processor: {e}")
    else:
        logger.info("ℹ️  Redis queue processor not configured (set REDIS_URL to enable)")

    logger.info("✅ Notification Service v16.0 ready")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Notification Service...")

    # Stop queue processor (v16.0)
    if queue_processor:
        try:
            await queue_processor.stop()
            await queue_processor.disconnect()
            logger.info("✅ Queue processor stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping queue processor: {e}")

    # Stop delivery tracker (v16.0)
    try:
        delivery_tracker = get_delivery_tracker()
        await delivery_tracker.stop()
        logger.info("✅ Delivery tracker stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping delivery tracker: {e}")

    # Stop NATS subscriber
    if _nats_available and _nats_subscriber:
        try:
            await stop_subscription()
            logger.info("✅ NATS subscriber stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping NATS subscriber: {e}")

    # Close database connections
    try:
        await close_db()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")

    logger.info("✅ Notification Service stopped")


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="SAHOOL Notification Service | خدمة الإشعارات",
    version="16.0.0",
    description="Enhanced personalized agricultural notifications for Yemeni farmers. Field-First Architecture with NATS integration, Redis queue, and comprehensive analytics.",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# CORS middleware - use centralized config to prevent wildcard in production
try:
    from shared.cors_config import setup_cors_middleware

    setup_cors_middleware(app)
except ImportError:
    cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
    allow_credentials = "*" not in cors_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Authorization",
            "Content-Type",
            "Content-Language",
            "X-Request-ID",
            "X-Correlation-ID",
            "X-Tenant-ID",
            "X-API-Key",
            "X-User-ID",
        ],
    )

# Setup security headers
if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)

# Include routers for multi-channel support
# Note: Kong gateway uses strip_path: true, so upstream receives paths
# without the /api/v1/notifications prefix. Do not add prefixes here.
app.include_router(channels_router)
app.include_router(preferences_router)
app.include_router(otp_router)

# Include enhanced routers (v16.0)
app.include_router(analytics_router)
app.include_router(history_router)

# Setup rate limiting middleware
try:
    from middleware.rate_limiter import setup_rate_limiting

    setup_rate_limiting(app, use_redis=os.getenv("REDIS_URL") is not None)
    logger.info("Rate limiting enabled")
except ImportError as e:
    logger.warning(f"Rate limiting not available: {e}")
except Exception as e:
    logger.warning(f"Failed to setup rate limiting: {e}")

# Tenant context middleware - عزل المستأجرين
app.add_middleware(TenantContextMiddleware)


# Prometheus metrics middleware - مقاييس الأداء
if HAS_PROMETHEUS:
    import time as _time

    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request as _Request
    from starlette.responses import Response as _Response

    class PrometheusMiddleware(BaseHTTPMiddleware):
        """Middleware to collect request count and latency metrics."""

        async def dispatch(self, request: _Request, call_next) -> _Response:
            endpoint = request.url.path
            start = _time.perf_counter()
            try:
                response = await call_next(request)
                REQUEST_COUNT.labels(endpoint=endpoint, status=response.status_code).inc()
                return response
            except Exception:
                REQUEST_COUNT.labels(endpoint=endpoint, status=500).inc()
                raise
            finally:
                elapsed = _time.perf_counter() - start
                REQUEST_LATENCY.labels(endpoint=endpoint).observe(elapsed)

    app.add_middleware(PrometheusMiddleware)
    logger.info("Prometheus metrics middleware enabled")


# =============================================================================
# API Endpoints
# =============================================================================
# NOTE: Routes use no prefix (e.g., "/" instead of "/v1/notifications")
# because Kong API Gateway uses strip_path: true.
#
# Kong routing table:
#   /api/v1/notifications/*  → strips to /*  → service receives /*, /farmer/{id}, /broadcast, etc.
#   /api/v1/alerts/*         → strips to /*  → service receives /weather, /pest
#   /api/v1/reminders/*      → strips to /*  → service receives /irrigation
#   /api/v1/farmers/*        → strips to /*  → service receives /register, /{id}/preferences
#   /api/v1/channels/*       → strips to /*  → service receives /add, /list, etc. (channels_controller)
#   /api/v1/preferences/*    → strips to /*  → service receives /, /update, etc. (preferences_controller)
#   /api/v1/notification-stats → strips to /* → service receives /stats
# =============================================================================


@app.get("/healthz")
async def health_check():
    """Health check endpoint (liveness probe)"""
    return {
        "status": "ok",
        "service": "notification-service",
        "version": "16.0.0",
    }


@app.get("/readyz")
async def readiness():
    checks = {}

    # Use Tortoise ORM health check (service uses Tortoise, not a raw asyncpg pool)
    try:
        db_ok = await check_db_health()
        checks["database"] = "connected" if db_ok else "disconnected"
    except Exception:
        checks["database"] = "disconnected"

    nc = getattr(app.state, "nc", None)
    checks["nats"] = "connected" if nc and not nc.is_closed else "not_configured"

    all_ready = all(v != "disconnected" for v in checks.values())
    response = {
        "status": "ready" if all_ready else "degraded",
        "service": "notification-service",
        "version": "16.0.0",
        "checks": checks,
    }
    if not all_ready:
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=503, content=response)
    return response


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint - نقطة نهاية مقاييس بروميثيوس"""
    if not HAS_PROMETHEUS:
        return {"error": "prometheus_client not installed"}
    from starlette.responses import Response as _MetricsResponse

    return _MetricsResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post("/")
async def create_custom_notification(
    request: CreateNotificationRequest,
    user: User | None = Depends(get_current_user),
):
    """إنشاء إشعار مخصص"""
    notification = await create_notification(
        type=request.type,
        priority=request.priority,
        title=request.title,
        title_ar=request.title_ar,
        body=request.body,
        body_ar=request.body_ar,
        data=request.data,
        target_farmers=request.target_farmers,
        target_governorates=request.target_governorates,
        target_crops=request.target_crops,
        channels=request.channels,
        expires_in_hours=request.expires_in_hours,
    )

    if not notification:
        raise HTTPException(status_code=400, detail="Failed to create notification")

    # Return in expected format
    return {
        "id": str(notification.id),
        "type": notification.type,
        "type_ar": notification.data.get("type_ar", ""),
        "priority": notification.priority,
        "priority_ar": notification.data.get("priority_ar", ""),
        "title": notification.title,
        "title_ar": notification.title_ar,
        "body": notification.body,
        "body_ar": notification.body_ar,
        "data": notification.data,
        "created_at": notification.created_at,
        "expires_at": notification.expires_at,
        "status": notification.status,
    }


@app.post("/weather")
async def create_weather_alert(
    request: WeatherAlertRequest,
    user: User | None = Depends(get_current_user),
):
    """إنشاء تنبيه طقس لمحافظات محددة"""

    # Get message for first governorate (can be customized per governorate)
    title, title_ar, body, body_ar = get_weather_alert_message(request.alert_type, request.governorates[0])

    notification = await create_notification(
        type=NotificationType.WEATHER_ALERT,
        priority=request.severity,
        title=title,
        title_ar=title_ar,
        body=body,
        body_ar=body_ar,
        data={
            "alert_type": request.alert_type,
            "expected_date": request.expected_date.isoformat(),
            **request.details,
        },
        target_governorates=request.governorates,
        channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP],
        expires_in_hours=48,
    )

    if not notification:
        raise HTTPException(
            status_code=400,
            detail="No matching farmers found for this weather alert | لا يوجد مزارعون مطابقون لهذا التنبيه الجوي",
        )

    logger.info(f"🌤️ Weather alert created for {len(request.governorates)} governorates")

    return {
        "id": str(notification.id),
        "type": notification.type,
        "title": notification.title,
        "title_ar": notification.title_ar,
        "body": notification.body,
        "body_ar": notification.body_ar,
        "created_at": notification.created_at,
    }


@app.post("/pest")
async def create_pest_alert(
    request: PestAlertRequest,
    user: User | None = Depends(get_current_user),
):
    """إنشاء تنبيه انتشار آفات"""
    gov_ar = GOVERNORATE_AR[request.governorate]
    crops_ar = ", ".join([CROP_AR[c] for c in request.affected_crops])

    notification = await create_notification(
        type=NotificationType.PEST_OUTBREAK,
        priority=request.severity,
        title=f"Pest Outbreak: {request.pest_name}",
        title_ar=f"🐛 انتشار آفة: {request.pest_name_ar}",
        body=f"Pest outbreak reported in {request.governorate.value}. Affected crops: {', '.join([c.value for c in request.affected_crops])}",
        body_ar=f"تم رصد انتشار {request.pest_name_ar} في {gov_ar}. المحاصيل المتأثرة: {crops_ar}. تحقق من حقولك واتخذ الإجراءات الوقائية.",
        data={
            "pest_name": request.pest_name,
            "pest_name_ar": request.pest_name_ar,
            "affected_crops": [c.value for c in request.affected_crops],
            "recommendations": request.recommendations,
            "recommendations_ar": request.recommendations_ar,
        },
        target_governorates=[request.governorate],
        target_crops=request.affected_crops,
        channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP],
        expires_in_hours=72,
    )

    if not notification:
        raise HTTPException(
            status_code=400,
            detail="No matching farmers found for this pest alert | لا يوجد مزارعون مطابقون لتنبيه الآفات هذا",
        )

    logger.info(f"🐛 Pest alert created for {request.governorate.value}")

    return {
        "id": str(notification.id),
        "type": notification.type,
        "title": notification.title,
        "title_ar": notification.title_ar,
        "body": notification.body,
        "body_ar": notification.body_ar,
        "created_at": notification.created_at,
    }


@app.post("/irrigation")
async def create_irrigation_reminder(
    request: IrrigationReminderRequest,
    user: User | None = Depends(get_current_user),
):
    """إنشاء تذكير ري مخصص"""
    crop_ar = CROP_AR.get(request.crop, request.crop.value)

    notification = await create_notification(
        type=NotificationType.IRRIGATION_REMINDER,
        priority=request.urgency,
        title=f"Irrigation Reminder: {request.field_name}",
        title_ar=f"💧 تذكير ري: {request.field_name}",
        body=f"Your {request.crop.value} field needs {request.water_needed_mm}mm of water.",
        body_ar=f"حقل {crop_ar} يحتاج {request.water_needed_mm} ملم من المياه. يُنصح بالري في الصباح الباكر لتقليل التبخر.",
        data={
            "field_id": request.field_id,
            "field_name": request.field_name,
            "crop": request.crop.value,
            "water_needed_mm": request.water_needed_mm,
        },
        target_farmers=[request.farmer_id],
        channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP],
        expires_in_hours=12,
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Farmer not found or has no active profile | المزارع غير موجود أو ليس لديه ملف نشط",
        )

    return {
        "id": str(notification.id),
        "type": notification.type,
        "title": notification.title,
        "title_ar": notification.title_ar,
        "body": notification.body,
        "body_ar": notification.body_ar,
        "created_at": notification.created_at,
    }


@app.get("/farmer/{farmer_id}")
async def get_farmer_notifications(
    farmer_id: str,
    unread_only: bool = Query(default=False),
    type: NotificationType | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User | None = Depends(get_current_user),
):
    """الحصول على إشعارات مزارع معين"""
    # Security: Verify the authenticated user can only access their own notifications
    # التحقق من أن المستخدم المصادق يصل فقط إلى إشعاراته الخاصة
    if AUTH_AVAILABLE and user is not None:
        if str(user.id) != farmer_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access notifications for another user",
            )

    # Get notifications from database
    notifications = await NotificationRepository.get_by_user(
        user_id=farmer_id,
        unread_only=unread_only,
        type=type.value if type else None,
        limit=limit,
        offset=offset,
        include_expired=False,
    )

    # Get unread count
    unread_count = await NotificationRepository.get_unread_count(user_id=farmer_id)

    # Format response
    notification_list = [
        {
            "id": str(n.id),
            "type": n.type,
            "type_ar": n.data.get("type_ar", ""),
            "priority": n.priority,
            "priority_ar": n.data.get("priority_ar", ""),
            "title": n.title,
            "title_ar": n.title_ar,
            "body": n.body,
            "body_ar": n.body_ar,
            "data": n.data,
            "is_read": n.is_read,
            "created_at": n.created_at,
            "expires_at": n.expires_at,
            "action_url": n.action_url,
        }
        for n in notifications
    ]

    return {
        "farmer_id": farmer_id,
        "total": len(notification_list),
        "unread_count": unread_count,
        "notifications": notification_list,
    }


@app.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    farmer_id: str = Query(...),
    user: User | None = Depends(get_current_user),
):
    """تحديد إشعار كمقروء"""
    try:
        # Security: Use authenticated user ID when auth is available
        # الأمان: استخدام معرف المستخدم المصادق عندما يكون المصادقة متاحة
        authorized_farmer_id = farmer_id
        if AUTH_AVAILABLE and user is not None:
            authorized_farmer_id = str(user.id)

        # Convert string to UUID
        notif_uuid = UUID(notification_id)

        # Check if notification exists and belongs to farmer
        notification = await NotificationRepository.get_by_id(notif_uuid)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        if notification.user_id != authorized_farmer_id:
            raise HTTPException(status_code=403, detail="Not authorized to mark this notification")

        # Mark as read
        success = await NotificationRepository.mark_as_read(notif_uuid)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to mark notification as read")

        return {
            "success": True,
            "notification_id": notification_id,
            "is_read": True,
            "read_at": datetime.now(UTC).isoformat(),
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid notification ID format")


@app.get("/broadcast")
async def get_broadcast_notifications(
    governorate: Governorate | None = None,
    crop: CropType | None = None,
    limit: int = Query(default=20, ge=1, le=50),
    user: User | None = Depends(get_current_user),
):
    """الحصول على الإشعارات العامة (البث)"""
    # Get broadcast notifications from database
    tenant_id = user.tenant_id if user else None
    notifications = await NotificationRepository.get_broadcast_notifications(
        governorate=governorate.value if governorate else None,
        crop=crop.value if crop else None,
        limit=limit,
        tenant_id=tenant_id,
    )

    # Format response
    notification_list = [
        {
            "id": str(n.id),
            "type": n.type,
            "type_ar": n.data.get("type_ar", ""),
            "priority": n.priority,
            "priority_ar": n.data.get("priority_ar", ""),
            "title": n.title,
            "title_ar": n.title_ar,
            "body": n.body,
            "body_ar": n.body_ar,
            "data": n.data,
            "created_at": n.created_at,
            "expires_at": n.expires_at,
            "target_governorates": n.target_governorates,
            "target_crops": n.target_crops,
        }
        for n in notifications
    ]

    return {
        "total": len(notification_list),
        "notifications": notification_list,
    }


@app.post("/register")
async def register_farmer(
    profile: FarmerProfile,
    user: User | None = Depends(get_current_user),
):
    """تسجيل مزارع للإشعارات - Database version"""
    try:
        # Convert CropType enums to strings
        crops_list = [crop.value for crop in profile.crops]

        # Create or update farmer profile in database
        await FarmerProfileRepository.create(
            farmer_id=profile.farmer_id,
            name=profile.name,
            name_ar=profile.name_ar,
            governorate=profile.governorate.value,
            district=profile.district,
            crops=crops_list,
            field_ids=profile.field_ids,
            phone=profile.phone,
            email=profile.email,
            fcm_token=profile.fcm_token,
            language=profile.language,
        )

        logger.info(
            f"Farmer registered: {sanitize_log_input(profile.farmer_id)} ({sanitize_log_input(profile.name_ar or '')})"
        )

        return {
            "success": True,
            "farmer_id": profile.farmer_id,
            "message": "تم تسجيل المزارع بنجاح",
            "message_en": "Farmer registered successfully",
        }
    except Exception as e:
        logger.error(f"Error registering farmer: {e}")
        raise HTTPException(status_code=500, detail="Failed to register farmer")


@app.put("/{farmer_id}/preferences")
async def update_preferences(
    farmer_id: str,
    preferences: NotificationPreferences,
    user: User | None = Depends(get_current_user),
):
    """تحديث تفضيلات الإشعارات"""
    # Security: Verify the authenticated user can only update their own preferences
    if AUTH_AVAILABLE and user is not None:
        if str(user.id) != farmer_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to update preferences for another user | غير مصرح لك بتحديث تفضيلات مستخدم آخر",
            )

    # Update preferences for each channel
    channels = ["push", "sms", "in_app"]
    updated_prefs = []

    for channel in channels:
        # Determine if channel is enabled based on preferences
        enabled = True
        if channel == "push":
            enabled = preferences.weather_alerts or preferences.pest_alerts
        elif channel == "sms":
            enabled = preferences.irrigation_reminders

        pref = await NotificationPreferenceRepository.create_or_update(
            user_id=farmer_id,
            event_type=channel,
            channels=[channel],
            enabled=enabled,
            quiet_hours_start=(
                datetime.strptime(preferences.quiet_hours_start, "%H:%M").time()
                if preferences.quiet_hours_start
                else None
            ),
            quiet_hours_end=(
                datetime.strptime(preferences.quiet_hours_end, "%H:%M").time() if preferences.quiet_hours_end else None
            ),
            metadata={
                "min_priority": preferences.min_priority.value,
                "notification_types": {
                    "weather_alerts": preferences.weather_alerts,
                    "pest_alerts": preferences.pest_alerts,
                    "irrigation_reminders": preferences.irrigation_reminders,
                    "crop_health_alerts": preferences.crop_health_alerts,
                    "market_prices": preferences.market_prices,
                },
            },
        )
        updated_prefs.append(pref)

    return {
        "success": True,
        "farmer_id": farmer_id,
        "preferences": preferences.model_dump(),
        "message": "تم تحديث التفضيلات",
        "message_en": "Preferences updated successfully",
    }


@app.get("/stats")
async def get_notification_stats(
    user: User | None = Depends(get_current_user),
):
    """إحصائيات الإشعارات - Database version"""
    db_stats = await get_db_stats()

    # Get additional stats from database
    from .models import Notification as NotificationModel

    total_by_type = {}
    for ntype in NotificationType:
        count = await NotificationModel.filter(type=ntype.value).count()
        total_by_type[ntype.value] = count

    active_weather = await NotificationModel.filter(
        type=NotificationType.WEATHER_ALERT.value,
        expires_at__gt=datetime.now(UTC),
    ).count()

    active_pest = await NotificationModel.filter(
        type=NotificationType.PEST_OUTBREAK.value,
        expires_at__gt=datetime.now(UTC),
    ).count()

    # Get farmer count from database
    try:
        farmer_count = await FarmerProfileRepository.get_count()
    except Exception as e:
        logger.error(f"Error getting farmer count: {e}")
        farmer_count = 0

    return {
        "total_notifications": db_stats.get("total_notifications", 0),
        "pending_notifications": db_stats.get("pending_notifications", 0),
        "registered_farmers": farmer_count,
        "total_templates": db_stats.get("total_templates", 0),
        "total_preferences": db_stats.get("total_preferences", 0),
        "by_type": total_by_type,
        "active_weather_alerts": active_weather,
        "active_pest_alerts": active_pest,
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")  # nosec B104 - binding to all interfaces required for Docker
    port = int(os.getenv("PORT", 8110))
    uvicorn.run(app, host=host, port=port)
