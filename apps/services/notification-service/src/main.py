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
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pydantic import BaseModel

# Add shared middleware to path
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
sys.path.insert(0, shared_path)
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

# Import authentication dependencies
try:
    from auth.dependencies import get_current_user, get_optional_user
    from auth.models import User

    AUTH_AVAILABLE = True
except ImportError:
    # Fallback if auth module not available
    AUTH_AVAILABLE = False
    User = None

    def get_current_user():
        """Placeholder when auth not available"""
        return None

    def get_optional_user():
        """Placeholder when auth not available"""
        return None


# Database imports
# Multi-channel support
from .channels_controller import router as channels_router
from .database import check_db_health, close_db, get_db_stats, init_db
from .email_client import get_email_client
from .otp_controller import router as otp_router
from .preferences_controller import router as preferences_router
from .preferences_service import PreferencesService
from .repository import (
    FarmerProfileRepository,
    NotificationLogRepository,
    NotificationPreferenceRepository,
    NotificationRepository,
)

# Notification clients
from .sms_client import get_sms_client
from .whatsapp_client import get_whatsapp_client
from .telegram_client import get_telegram_client
from .sms_providers import get_multi_sms_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sahool-notifications")

# =============================================================================
# Enums & Models
# =============================================================================


class NotificationType(str, Enum):
    WEATHER_ALERT = "weather_alert"
    PEST_OUTBREAK = "pest_outbreak"
    IRRIGATION_REMINDER = "irrigation_reminder"
    CROP_HEALTH = "crop_health"
    MARKET_PRICE = "market_price"
    SYSTEM = "system"
    TASK_REMINDER = "task_reminder"


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationChannel(str, Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"


class Governorate(str, Enum):
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


class CropType(str, Enum):
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

    farmer_id: str
    name: str
    name_ar: str
    governorate: Governorate
    district: str | None = None
    crops: list[CropType]
    field_ids: list[str] = []
    phone: str | None = None
    email: str | None = None
    fcm_token: str | None = None  # Firebase Cloud Messaging
    notification_channels: list[NotificationChannel] = [NotificationChannel.IN_APP]
    language: str = "ar"


class NotificationPreferences(BaseModel):
    """تفضيلات الإشعارات"""

    farmer_id: str
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
    type_ar: str
    priority: NotificationPriority
    priority_ar: str
    title: str
    title_ar: str
    body: str
    body_ar: str
    data: dict[str, Any] = {}
    target_farmers: list[str] = []  # Empty = broadcast
    target_governorates: list[Governorate] = []
    target_crops: list[CropType] = []
    channels: list[NotificationChannel] = [NotificationChannel.IN_APP]
    created_at: datetime
    expires_at: datetime | None = None
    is_read: bool = False
    action_url: str | None = None


class CreateNotificationRequest(BaseModel):
    """طلب إنشاء إشعار"""

    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    title_ar: str
    body: str
    body_ar: str
    data: dict[str, Any] = {}
    target_farmers: list[str] = []
    target_governorates: list[Governorate] = []
    target_crops: list[CropType] = []
    channels: list[NotificationChannel] = [NotificationChannel.IN_APP]
    expires_in_hours: int | None = 24


class WeatherAlertRequest(BaseModel):
    """طلب تنبيه طقس"""

    governorates: list[Governorate]
    alert_type: str  # frost, heat_wave, storm, flood, drought
    severity: NotificationPriority
    expected_date: date
    details: dict[str, Any] = {}


class PestAlertRequest(BaseModel):
    """طلب تنبيه آفات"""

    governorate: Governorate
    pest_name: str
    pest_name_ar: str
    affected_crops: list[CropType]
    severity: NotificationPriority
    recommendations: list[str] = []
    recommendations_ar: list[str] = []


class IrrigationReminderRequest(BaseModel):
    """طلب تذكير ري"""

    farmer_id: str
    field_id: str
    field_name: str
    crop: CropType
    water_needed_mm: float
    urgency: NotificationPriority


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


# =============================================================================
# Notification Logic
# =============================================================================


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
                f"Skipping notification for user {farmer_id} - event type disabled in preferences"
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
            target_governorates=(
                [g.value for g in target_governorates] if target_governorates else None
            ),
            target_crops=[c.value for c in target_crops] if target_crops else None,
            expires_in_hours=expires_in_hours,
        )
        notifications.append(notification)

        # Send notifications via appropriate channels (async background task)
        for channel_name in final_channels:
            try:
                # Convert channel name string to enum
                channel_enum = NotificationChannel(channel_name)
                asyncio.create_task(
                    send_notification_via_channel(
                        notification=notification,
                        channel=channel_enum,
                        farmer_id=notification.user_id,
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
            logger.warning(f"No phone number for farmer {farmer_id}")
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
                sent_at=datetime.utcnow(),
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
            logger.warning(f"No email address for farmer {farmer_id}")
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

        # Create HTML email body
        html_body = f"""
        <html>
            <body dir="{"rtl" if language == "ar" else "ltr"}">
                <h2>{notification.title_ar if language == "ar" else notification.title}</h2>
                <p>{notification.body_ar if language == "ar" else notification.body}</p>
                <br>
                <p style="color: #666; font-size: 12px;">
                    {"هذه رسالة آلية من منصة SAHOOL الزراعية" if language == "ar" else "This is an automated message from SAHOOL Agriculture Platform"}
                </p>
            </body>
        </html>
        """

        message_id = await email_client.send_email(
            to=farmer_profile.email,
            subject=notification.title,
            subject_ar=notification.title_ar,
            body=html_body,
            body_ar=html_body,
            language=language,
            is_html=True,
        )

        if message_id:
            # Update notification status
            await NotificationRepository.update_status(
                notification.id,
                status="sent",
                sent_at=datetime.utcnow(),
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
            logger.warning(f"No FCM token for farmer {farmer_id}")
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

        # Send push notification
        message_id = firebase_client.send_notification(
            token=farmer_profile.fcm_token,
            title=notification.title,
            body=notification.body,
            title_ar=notification.title_ar,
            body_ar=notification.body_ar,
            data=notification.data or {},
            priority=priority,
        )

        if message_id:
            # Update notification status
            await NotificationRepository.update_status(
                notification.id,
                status="sent",
                sent_at=datetime.utcnow(),
            )
            # Log success
            await NotificationLogRepository.create_log(
                notification_id=notification.id,
                channel="push",
                status="sent",
                provider_message_id=message_id,
            )
            logger.info(f"✅ Push notification sent to {farmer_id}: {message_id}")
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
            logger.warning(f"No WhatsApp number for farmer {farmer_id}")
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
                sent_at=datetime.utcnow(),
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


def create_notification_from_nats(notification_data: dict[str, Any]):
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
        priority = priority_mapping.get(
            notification_data.get("priority", "medium"), NotificationPriority.MEDIUM
        )
        channels = [
            channel_mapping.get(ch, NotificationChannel.IN_APP)
            for ch in notification_data.get("channels", ["in_app"])
        ]

        create_notification(
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
        # In production, set create_db=False and use migrations
        create_db = os.getenv("CREATE_DB_SCHEMA", "false").lower() == "true"
        await init_db(create_db=create_db)
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.warning(f"⚠️ Database initialization failed (service will continue): {e}")
        # Don't raise - allow service to start in degraded mode

    # Start NATS subscriber (optional)
    if _nats_available:
        try:
            _nats_subscriber = await start_subscription(create_notification_from_nats)
            logger.info("✅ NATS subscriber started")
        except Exception as e:
            logger.warning(f"⚠️  Failed to start NATS subscriber: {e}")

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

    logger.info("✅ Notification Service ready")

    yield

    # Shutdown
    logger.info("🛑 Shutting down Notification Service...")

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
    version="15.4.0",
    description="Personalized agricultural notifications for Yemeni farmers. Field-First Architecture with NATS integration.",
    lifespan=lifespan,
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# Include routers for multi-channel support
app.include_router(channels_router)
app.include_router(preferences_router)
app.include_router(otp_router)

# Setup rate limiting middleware
try:
    from middleware.rate_limiter import setup_rate_limiting

    setup_rate_limiting(app, use_redis=os.getenv("REDIS_URL") is not None)
    logger.info("Rate limiting enabled")
except ImportError as e:
    logger.warning(f"Rate limiting not available: {e}")
except Exception as e:
    logger.warning(f"Failed to setup rate limiting: {e}")


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
    """Health check endpoint with database status"""
    try:
        db_health = await check_db_health()
        db_stats = await get_db_stats() if db_health.get("connected") else {}
    except Exception as e:
        logger.warning(f"Health check - database error: {e}")
        db_health = {"status": "unavailable", "connected": False, "error": str(e)}
        db_stats = {}

    # Determine health status based on critical dependencies
    nats_ok = _nats_available and _nats_subscriber is not None
    db_ok = db_health.get("connected", False)
    is_healthy = nats_ok or db_ok  # At least one critical dependency should work

    # Get farmer count from database
    try:
        farmer_count = await FarmerProfileRepository.get_count() if db_ok else 0
    except Exception:
        farmer_count = 0

    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": "notification-service",
        "version": "16.0.0",
        "mode": "normal" if db_ok else "degraded",
        "nats_connected": nats_ok,
        "database": db_health,
        "stats": db_stats,
        "registered_farmers": farmer_count,
    }


@app.post("/")
async def create_custom_notification(
    request: CreateNotificationRequest,
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
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
async def create_weather_alert(request: WeatherAlertRequest, background_tasks: BackgroundTasks):
    """إنشاء تنبيه طقس لمحافظات محددة"""

    # Get message for first governorate (can be customized per governorate)
    title, title_ar, body, body_ar = get_weather_alert_message(
        request.alert_type, request.governorates[0]
    )

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
async def create_pest_alert(request: PestAlertRequest):
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
async def create_irrigation_reminder(request: IrrigationReminderRequest):
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
    user: User = Depends(get_current_user) if AUTH_AVAILABLE else None,
):
    """الحصول على إشعارات مزارع معين"""
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
async def mark_notification_read(notification_id: str, farmer_id: str = Query(...)):
    """تحديد إشعار كمقروء"""
    try:
        # Convert string to UUID
        notif_uuid = UUID(notification_id)

        # Check if notification exists and belongs to farmer
        notification = await NotificationRepository.get_by_id(notif_uuid)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        if notification.user_id != farmer_id:
            raise HTTPException(status_code=403, detail="Not authorized to mark this notification")

        # Mark as read
        success = await NotificationRepository.mark_as_read(notif_uuid)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to mark notification as read")

        return {
            "success": True,
            "notification_id": notification_id,
            "is_read": True,
            "read_at": datetime.utcnow().isoformat(),
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid notification ID format")


@app.get("/broadcast")
async def get_broadcast_notifications(
    governorate: Governorate | None = None,
    crop: CropType | None = None,
    limit: int = Query(default=20, ge=1, le=50),
):
    """الحصول على الإشعارات العامة (البث)"""
    # Get broadcast notifications from database
    notifications = await NotificationRepository.get_broadcast_notifications(
        governorate=governorate.value if governorate else None,
        crop=crop.value if crop else None,
        limit=limit,
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
async def register_farmer(profile: FarmerProfile):
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

        logger.info(f"👨‍🌾 Farmer registered: {profile.farmer_id} ({profile.name_ar})")

        return {
            "success": True,
            "farmer_id": profile.farmer_id,
            "message": "تم تسجيل المزارع بنجاح",
            "message_en": "Farmer registered successfully",
        }
    except Exception as e:
        logger.error(f"Error registering farmer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register farmer: {str(e)}")


@app.put("/{farmer_id}/preferences")
async def update_preferences(farmer_id: str, preferences: NotificationPreferences):
    """تحديث تفضيلات الإشعارات"""
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
            channel=channel,
            enabled=enabled,
            quiet_hours_start=(
                datetime.strptime(preferences.quiet_hours_start, "%H:%M").time()
                if preferences.quiet_hours_start
                else None
            ),
            quiet_hours_end=(
                datetime.strptime(preferences.quiet_hours_end, "%H:%M").time()
                if preferences.quiet_hours_end
                else None
            ),
            min_priority=preferences.min_priority.value,
            notification_types={
                "weather_alerts": preferences.weather_alerts,
                "pest_alerts": preferences.pest_alerts,
                "irrigation_reminders": preferences.irrigation_reminders,
                "crop_health_alerts": preferences.crop_health_alerts,
                "market_prices": preferences.market_prices,
            },
        )
        updated_prefs.append(pref)

    return {
        "success": True,
        "farmer_id": farmer_id,
        "preferences": preferences.dict(),
        "message": "تم تحديث التفضيلات",
        "message_en": "Preferences updated successfully",
    }


@app.get("/stats")
async def get_notification_stats():
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
        expires_at__gt=datetime.utcnow(),
    ).count()

    active_pest = await NotificationModel.filter(
        type=NotificationType.PEST_OUTBREAK.value,
        expires_at__gt=datetime.utcnow(),
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

    uvicorn.run(app, host="0.0.0.0", port=8110)
