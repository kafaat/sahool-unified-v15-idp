"""
Notification Preferences Data Models
====================================
نماذج بيانات تفضيلات الإشعارات

Data models for notification preferences, channels, schedules, and routing rules.
Supports per-user settings with bilingual Arabic/English content.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, time
from enum import StrEnum
from typing import Any


class NotificationChannel(StrEnum):
    """
    Notification delivery channels
    قنوات تسليم الإشعارات
    """

    PUSH = "push"  # إشعار فوري - Firebase/APNs
    SMS = "sms"  # رسالة نصية
    EMAIL = "email"  # بريد إلكتروني
    WHATSAPP = "whatsapp"  # واتساب
    IN_APP = "in_app"  # داخل التطبيق
    TELEGRAM = "telegram"  # تيليجرام


class AlertType(StrEnum):
    """
    Types of alerts/notifications
    أنواع التنبيهات والإشعارات
    """

    # Weather alerts | تنبيهات الطقس
    WEATHER_FROST = "weather_frost"  # صقيع
    WEATHER_HEAT = "weather_heat"  # موجة حر
    WEATHER_STORM = "weather_storm"  # عاصفة
    WEATHER_RAIN = "weather_rain"  # أمطار
    WEATHER_WIND = "weather_wind"  # رياح
    WEATHER_GENERAL = "weather_general"  # عام

    # Agricultural alerts | تنبيهات زراعية
    CROP_HEALTH = "crop_health"  # صحة المحصول
    PEST_OUTBREAK = "pest_outbreak"  # انتشار آفات
    DISEASE_DETECTED = "disease_detected"  # مرض مكتشف
    IRRIGATION_REMINDER = "irrigation_reminder"  # تذكير ري
    SPRAY_WINDOW = "spray_window"  # وقت الرش
    HARVEST_REMINDER = "harvest_reminder"  # تذكير حصاد
    FERTILIZER_REMINDER = "fertilizer_reminder"  # تذكير سماد

    # Business alerts | تنبيهات تجارية
    MARKET_PRICE = "market_price"  # أسعار السوق
    PAYMENT_DUE = "payment_due"  # دفعة مستحقة
    LOW_STOCK = "low_stock"  # نقص مخزون

    # System alerts | تنبيهات النظام
    SATELLITE_READY = "satellite_ready"  # صور أقمار جاهزة
    FIELD_UPDATE = "field_update"  # تحديث حقل
    TASK_REMINDER = "task_reminder"  # تذكير مهمة
    SYSTEM = "system"  # نظام

    # Critical alerts | تنبيهات حرجة
    EMERGENCY = "emergency"  # طوارئ
    RPW_DETECTION = "rpw_detection"  # اكتشاف سوسة النخيل


class AlertUrgency(StrEnum):
    """
    Alert urgency levels
    مستويات إلحاح التنبيهات
    """

    CRITICAL = "critical"  # حرج - فوري، يتجاوز الساعات الهادئة
    HIGH = "high"  # عالي - خلال ساعة
    MEDIUM = "medium"  # متوسط - خلال يوم
    LOW = "low"  # منخفض - تجميعي
    INFORMATIONAL = "info"  # معلوماتي - غير إلزامي


class Language(StrEnum):
    """
    Supported languages
    اللغات المدعومة
    """

    ARABIC = "ar"  # العربية
    ENGLISH = "en"  # English
    BOTH = "both"  # كلاهما


class DayOfWeek(StrEnum):
    """Days of the week for scheduling | أيام الأسبوع"""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


@dataclass
class QuietHours:
    """
    Quiet hours configuration
    إعدادات الساعات الهادئة (عدم الإزعاج)

    During quiet hours, non-critical notifications are held until the quiet period ends.
    خلال الساعات الهادئة، يتم تأجيل الإشعارات غير الحرجة حتى انتهاء الفترة.
    """

    enabled: bool = True
    start_time: time = field(default_factory=lambda: time(22, 0))  # 10:00 PM
    end_time: time = field(default_factory=lambda: time(6, 0))  # 6:00 AM

    # Timezone for quiet hours calculation
    timezone: str = "Asia/Riyadh"

    # Days when quiet hours apply (empty = all days)
    days: list[DayOfWeek] = field(default_factory=list)

    # Minimum urgency to bypass quiet hours
    bypass_urgency: AlertUrgency = AlertUrgency.CRITICAL

    # Channel-specific settings (some channels may bypass quiet hours)
    bypass_channels: list[NotificationChannel] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "enabled": self.enabled,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "timezone": self.timezone,
            "days": [d.value for d in self.days] if self.days else [],
            "bypass_urgency": self.bypass_urgency.value,
            "bypass_channels": [c.value for c in self.bypass_channels],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuietHours:
        """Create from dictionary"""
        return cls(
            enabled=data.get("enabled", True),
            start_time=time.fromisoformat(data["start_time"]) if data.get("start_time") else time(22, 0),
            end_time=time.fromisoformat(data["end_time"]) if data.get("end_time") else time(6, 0),
            timezone=data.get("timezone", "Asia/Riyadh"),
            days=[DayOfWeek(d) for d in data.get("days", [])],
            bypass_urgency=AlertUrgency(data.get("bypass_urgency", "critical")),
            bypass_channels=[NotificationChannel(c) for c in data.get("bypass_channels", [])],
        )


@dataclass
class ChannelConfig:
    """
    Channel-specific configuration
    إعدادات خاصة بالقناة
    """

    channel: NotificationChannel
    enabled: bool = True

    # Address for this channel (phone, email, token, etc.)
    address: str | None = None

    # Verified status
    verified: bool = False
    verified_at: datetime | None = None

    # Channel-specific quiet hours override
    quiet_hours: QuietHours | None = None

    # Maximum notifications per hour (rate limiting)
    max_per_hour: int = 10

    # Batch notifications of this urgency or lower
    batch_urgency: AlertUrgency = AlertUrgency.LOW
    batch_interval_minutes: int = 60  # Batch window

    # Channel metadata (device info, provider settings, etc.)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "channel": self.channel.value,
            "enabled": self.enabled,
            "address": self.address,
            "verified": self.verified,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "quiet_hours": self.quiet_hours.to_dict() if self.quiet_hours else None,
            "max_per_hour": self.max_per_hour,
            "batch_urgency": self.batch_urgency.value,
            "batch_interval_minutes": self.batch_interval_minutes,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChannelConfig:
        """Create from dictionary"""
        return cls(
            channel=NotificationChannel(data["channel"]),
            enabled=data.get("enabled", True),
            address=data.get("address"),
            verified=data.get("verified", False),
            verified_at=datetime.fromisoformat(data["verified_at"]) if data.get("verified_at") else None,
            quiet_hours=QuietHours.from_dict(data["quiet_hours"]) if data.get("quiet_hours") else None,
            max_per_hour=data.get("max_per_hour", 10),
            batch_urgency=AlertUrgency(data.get("batch_urgency", "low")),
            batch_interval_minutes=data.get("batch_interval_minutes", 60),
            metadata=data.get("metadata", {}),
        )


@dataclass
class AlertTypePreference:
    """
    Preference for a specific alert type
    تفضيلات لنوع تنبيه معين
    """

    alert_type: AlertType
    enabled: bool = True

    # Channels to use for this alert type (overrides default)
    channels: list[NotificationChannel] = field(default_factory=list)

    # Minimum urgency to send notifications for this type
    min_urgency: AlertUrgency = AlertUrgency.LOW

    # Custom quiet hours for this alert type
    quiet_hours: QuietHours | None = None

    # Whether to batch notifications of this type
    batch_enabled: bool = False
    batch_interval_minutes: int = 60

    # Custom sound/vibration for this alert type
    sound_enabled: bool = True
    vibration_enabled: bool = True
    custom_sound: str | None = None

    # Tags/categories for filtering
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_type": self.alert_type.value,
            "enabled": self.enabled,
            "channels": [c.value for c in self.channels],
            "min_urgency": self.min_urgency.value,
            "quiet_hours": self.quiet_hours.to_dict() if self.quiet_hours else None,
            "batch_enabled": self.batch_enabled,
            "batch_interval_minutes": self.batch_interval_minutes,
            "sound_enabled": self.sound_enabled,
            "vibration_enabled": self.vibration_enabled,
            "custom_sound": self.custom_sound,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AlertTypePreference:
        """Create from dictionary"""
        return cls(
            alert_type=AlertType(data["alert_type"]),
            enabled=data.get("enabled", True),
            channels=[NotificationChannel(c) for c in data.get("channels", [])],
            min_urgency=AlertUrgency(data.get("min_urgency", "low")),
            quiet_hours=QuietHours.from_dict(data["quiet_hours"]) if data.get("quiet_hours") else None,
            batch_enabled=data.get("batch_enabled", False),
            batch_interval_minutes=data.get("batch_interval_minutes", 60),
            sound_enabled=data.get("sound_enabled", True),
            vibration_enabled=data.get("vibration_enabled", True),
            custom_sound=data.get("custom_sound"),
            tags=data.get("tags", []),
        )


@dataclass
class TimeBasedRule:
    """
    Time-based notification rule
    قاعدة إشعارات حسب الوقت

    Example: "No SMS between 10 PM and 6 AM"
    مثال: "لا رسائل نصية بين الساعة 10 مساءً و6 صباحاً"
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    name_ar: str = ""

    enabled: bool = True

    # Time window
    start_time: time = field(default_factory=lambda: time(22, 0))
    end_time: time = field(default_factory=lambda: time(6, 0))

    # Days this rule applies
    days: list[DayOfWeek] = field(default_factory=list)  # Empty = all days

    # Channels affected by this rule
    channels: list[NotificationChannel] = field(default_factory=list)

    # Alert types affected (empty = all types)
    alert_types: list[AlertType] = field(default_factory=list)

    # Action to take
    action: str = "hold"  # "hold", "drop", "channel_fallback", "batch"

    # Fallback channel if action is "channel_fallback"
    fallback_channel: NotificationChannel | None = None

    # Urgency levels exempt from this rule
    exempt_urgencies: list[AlertUrgency] = field(default_factory=lambda: [AlertUrgency.CRITICAL])

    # Priority (higher = evaluated first)
    priority: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "enabled": self.enabled,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "days": [d.value for d in self.days],
            "channels": [c.value for c in self.channels],
            "alert_types": [a.value for a in self.alert_types],
            "action": self.action,
            "fallback_channel": self.fallback_channel.value if self.fallback_channel else None,
            "exempt_urgencies": [u.value for u in self.exempt_urgencies],
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimeBasedRule:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            name_ar=data.get("name_ar", ""),
            enabled=data.get("enabled", True),
            start_time=time.fromisoformat(data["start_time"]) if data.get("start_time") else time(22, 0),
            end_time=time.fromisoformat(data["end_time"]) if data.get("end_time") else time(6, 0),
            days=[DayOfWeek(d) for d in data.get("days", [])],
            channels=[NotificationChannel(c) for c in data.get("channels", [])],
            alert_types=[AlertType(a) for a in data.get("alert_types", [])],
            action=data.get("action", "hold"),
            fallback_channel=NotificationChannel(data["fallback_channel"]) if data.get("fallback_channel") else None,
            exempt_urgencies=[AlertUrgency(u) for u in data.get("exempt_urgencies", ["critical"])],
            priority=data.get("priority", 0),
        )


@dataclass
class UrgencyOverride:
    """
    Urgency-based override configuration
    إعدادات تجاوز حسب الإلحاح

    Allows bypassing preferences for certain urgency levels.
    يسمح بتجاوز التفضيلات لمستويات إلحاح معينة.
    """

    urgency: AlertUrgency

    # Channels to always use for this urgency
    force_channels: list[NotificationChannel] = field(default_factory=list)

    # Bypass quiet hours
    bypass_quiet_hours: bool = False

    # Bypass all time-based rules
    bypass_time_rules: bool = False

    # Force immediate delivery (no batching)
    force_immediate: bool = False

    # Retry configuration for delivery failures
    max_retries: int = 3
    retry_interval_minutes: int = 5

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "urgency": self.urgency.value,
            "force_channels": [c.value for c in self.force_channels],
            "bypass_quiet_hours": self.bypass_quiet_hours,
            "bypass_time_rules": self.bypass_time_rules,
            "force_immediate": self.force_immediate,
            "max_retries": self.max_retries,
            "retry_interval_minutes": self.retry_interval_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UrgencyOverride:
        """Create from dictionary"""
        return cls(
            urgency=AlertUrgency(data["urgency"]),
            force_channels=[NotificationChannel(c) for c in data.get("force_channels", [])],
            bypass_quiet_hours=data.get("bypass_quiet_hours", False),
            bypass_time_rules=data.get("bypass_time_rules", False),
            force_immediate=data.get("force_immediate", False),
            max_retries=data.get("max_retries", 3),
            retry_interval_minutes=data.get("retry_interval_minutes", 5),
        )


@dataclass
class UserNotificationPreferences:
    """
    Complete notification preferences for a user
    تفضيلات الإشعارات الكاملة للمستخدم
    """

    # Identification
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    tenant_id: str | None = None

    # Language preference
    language: Language = Language.ARABIC

    # Master notification toggle
    notifications_enabled: bool = True

    # Default channels (used when alert type has no specific channels)
    default_channels: list[NotificationChannel] = field(
        default_factory=lambda: [NotificationChannel.PUSH, NotificationChannel.IN_APP]
    )

    # Channel configurations
    channel_configs: list[ChannelConfig] = field(default_factory=list)

    # Global quiet hours
    quiet_hours: QuietHours = field(default_factory=QuietHours)

    # Alert type preferences
    alert_preferences: list[AlertTypePreference] = field(default_factory=list)

    # Time-based rules
    time_rules: list[TimeBasedRule] = field(default_factory=list)

    # Urgency overrides
    urgency_overrides: list[UrgencyOverride] = field(default_factory=list)

    # Digest settings
    digest_enabled: bool = False
    digest_time: time | None = None  # When to send daily digest
    digest_days: list[DayOfWeek] = field(default_factory=list)  # Days to send digest
    digest_channel: NotificationChannel = NotificationChannel.EMAIL

    # Summary settings
    summary_enabled: bool = True
    summary_interval_hours: int = 24  # How often to send summaries

    # Sound & vibration defaults
    sound_enabled: bool = True
    vibration_enabled: bool = True

    # Badge count
    show_badge_count: bool = True

    # Preview settings
    show_preview: bool = True  # Show notification content in preview
    show_preview_on_lock_screen: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Version for optimistic locking
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "language": self.language.value,
            "notifications_enabled": self.notifications_enabled,
            "default_channels": [c.value for c in self.default_channels],
            "channel_configs": [c.to_dict() for c in self.channel_configs],
            "quiet_hours": self.quiet_hours.to_dict(),
            "alert_preferences": [p.to_dict() for p in self.alert_preferences],
            "time_rules": [r.to_dict() for r in self.time_rules],
            "urgency_overrides": [o.to_dict() for o in self.urgency_overrides],
            "digest_enabled": self.digest_enabled,
            "digest_time": self.digest_time.isoformat() if self.digest_time else None,
            "digest_days": [d.value for d in self.digest_days],
            "digest_channel": self.digest_channel.value,
            "summary_enabled": self.summary_enabled,
            "summary_interval_hours": self.summary_interval_hours,
            "sound_enabled": self.sound_enabled,
            "vibration_enabled": self.vibration_enabled,
            "show_badge_count": self.show_badge_count,
            "show_preview": self.show_preview,
            "show_preview_on_lock_screen": self.show_preview_on_lock_screen,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserNotificationPreferences:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            user_id=data.get("user_id", ""),
            tenant_id=data.get("tenant_id"),
            language=Language(data.get("language", "ar")),
            notifications_enabled=data.get("notifications_enabled", True),
            default_channels=[NotificationChannel(c) for c in data.get("default_channels", ["push", "in_app"])],
            channel_configs=[ChannelConfig.from_dict(c) for c in data.get("channel_configs", [])],
            quiet_hours=QuietHours.from_dict(data["quiet_hours"]) if data.get("quiet_hours") else QuietHours(),
            alert_preferences=[AlertTypePreference.from_dict(p) for p in data.get("alert_preferences", [])],
            time_rules=[TimeBasedRule.from_dict(r) for r in data.get("time_rules", [])],
            urgency_overrides=[UrgencyOverride.from_dict(o) for o in data.get("urgency_overrides", [])],
            digest_enabled=data.get("digest_enabled", False),
            digest_time=time.fromisoformat(data["digest_time"]) if data.get("digest_time") else None,
            digest_days=[DayOfWeek(d) for d in data.get("digest_days", [])],
            digest_channel=NotificationChannel(data.get("digest_channel", "email")),
            summary_enabled=data.get("summary_enabled", True),
            summary_interval_hours=data.get("summary_interval_hours", 24),
            sound_enabled=data.get("sound_enabled", True),
            vibration_enabled=data.get("vibration_enabled", True),
            show_badge_count=data.get("show_badge_count", True),
            show_preview=data.get("show_preview", True),
            show_preview_on_lock_screen=data.get("show_preview_on_lock_screen", False),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
            version=data.get("version", 1),
        )

    def get_channel_config(self, channel: NotificationChannel) -> ChannelConfig | None:
        """Get configuration for a specific channel"""
        for config in self.channel_configs:
            if config.channel == channel:
                return config
        return None

    def get_alert_preference(self, alert_type: AlertType) -> AlertTypePreference | None:
        """Get preference for a specific alert type"""
        for pref in self.alert_preferences:
            if pref.alert_type == alert_type:
                return pref
        return None

    def get_urgency_override(self, urgency: AlertUrgency) -> UrgencyOverride | None:
        """Get override configuration for a specific urgency level"""
        for override in self.urgency_overrides:
            if override.urgency == urgency:
                return override
        return None


@dataclass
class NotificationRequest:
    """
    A notification request to be routed
    طلب إشعار للتوجيه
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Target user
    user_id: str = ""
    tenant_id: str | None = None

    # Notification content
    alert_type: AlertType = AlertType.SYSTEM
    urgency: AlertUrgency = AlertUrgency.MEDIUM

    # Title and body (bilingual)
    title: str = ""
    title_ar: str = ""
    body: str = ""
    body_ar: str = ""

    # Optional image
    image_url: str | None = None

    # Deep link / action URL
    action_url: str | None = None

    # Additional data payload
    data: dict[str, Any] = field(default_factory=dict)

    # Scheduling
    scheduled_at: datetime | None = None  # None = immediate
    expires_at: datetime | None = None

    # Request metadata
    source_service: str = ""
    correlation_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "alert_type": self.alert_type.value,
            "urgency": self.urgency.value,
            "title": self.title,
            "title_ar": self.title_ar,
            "body": self.body,
            "body_ar": self.body_ar,
            "image_url": self.image_url,
            "action_url": self.action_url,
            "data": self.data,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "source_service": self.source_service,
            "correlation_id": self.correlation_id,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class RoutingDecision:
    """
    Decision about how to route a notification
    قرار حول كيفية توجيه الإشعار
    """

    # Original request
    request_id: str = ""

    # Should the notification be delivered?
    should_deliver: bool = True

    # Reasons if not delivering
    rejection_reasons: list[str] = field(default_factory=list)
    rejection_reasons_ar: list[str] = field(default_factory=list)

    # Channels to use
    channels: list[NotificationChannel] = field(default_factory=list)

    # Delivery mode
    immediate: bool = True  # False = batched or scheduled

    # If not immediate, when to deliver
    deliver_at: datetime | None = None

    # Language to use
    language: Language = Language.ARABIC

    # Whether quiet hours were bypassed
    quiet_hours_bypassed: bool = False
    bypass_reason: str | None = None

    # Applied rules
    applied_rules: list[str] = field(default_factory=list)

    # Original user preferences (for reference)
    preferences_version: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "should_deliver": self.should_deliver,
            "rejection_reasons": self.rejection_reasons,
            "rejection_reasons_ar": self.rejection_reasons_ar,
            "channels": [c.value for c in self.channels],
            "immediate": self.immediate,
            "deliver_at": self.deliver_at.isoformat() if self.deliver_at else None,
            "language": self.language.value,
            "quiet_hours_bypassed": self.quiet_hours_bypassed,
            "bypass_reason": self.bypass_reason,
            "applied_rules": self.applied_rules,
            "preferences_version": self.preferences_version,
        }


# =============================================================================
# Default Preferences Templates
# =============================================================================


def create_default_preferences(user_id: str, tenant_id: str | None = None) -> UserNotificationPreferences:
    """
    Create default notification preferences for a new user
    إنشاء تفضيلات إشعارات افتراضية لمستخدم جديد
    """
    return UserNotificationPreferences(
        user_id=user_id,
        tenant_id=tenant_id,
        language=Language.ARABIC,
        notifications_enabled=True,
        default_channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP],
        quiet_hours=QuietHours(
            enabled=True,
            start_time=time(22, 0),
            end_time=time(6, 0),
            timezone="Asia/Riyadh",
            bypass_urgency=AlertUrgency.CRITICAL,
        ),
        urgency_overrides=[
            UrgencyOverride(
                urgency=AlertUrgency.CRITICAL,
                force_channels=[NotificationChannel.PUSH, NotificationChannel.SMS],
                bypass_quiet_hours=True,
                bypass_time_rules=True,
                force_immediate=True,
                max_retries=5,
            ),
            UrgencyOverride(
                urgency=AlertUrgency.HIGH,
                force_channels=[NotificationChannel.PUSH],
                bypass_quiet_hours=False,
                force_immediate=True,
                max_retries=3,
            ),
        ],
        time_rules=[
            TimeBasedRule(
                name="No SMS at night",
                name_ar="لا رسائل نصية ليلاً",
                enabled=True,
                start_time=time(22, 0),
                end_time=time(6, 0),
                channels=[NotificationChannel.SMS],
                action="channel_fallback",
                fallback_channel=NotificationChannel.PUSH,
                exempt_urgencies=[AlertUrgency.CRITICAL],
                priority=100,
            ),
        ],
    )


def create_minimal_preferences(user_id: str, tenant_id: str | None = None) -> UserNotificationPreferences:
    """
    Create minimal notification preferences (critical only)
    إنشاء تفضيلات إشعارات بسيطة (حرجة فقط)
    """
    return UserNotificationPreferences(
        user_id=user_id,
        tenant_id=tenant_id,
        language=Language.ARABIC,
        notifications_enabled=True,
        default_channels=[NotificationChannel.PUSH],
        quiet_hours=QuietHours(
            enabled=True,
            start_time=time(21, 0),
            end_time=time(7, 0),
            bypass_urgency=AlertUrgency.CRITICAL,
        ),
        alert_preferences=[
            AlertTypePreference(
                alert_type=AlertType.EMERGENCY,
                enabled=True,
                channels=[NotificationChannel.PUSH, NotificationChannel.SMS],
                min_urgency=AlertUrgency.CRITICAL,
            ),
            AlertTypePreference(
                alert_type=AlertType.RPW_DETECTION,
                enabled=True,
                channels=[NotificationChannel.PUSH, NotificationChannel.SMS],
                min_urgency=AlertUrgency.HIGH,
            ),
            AlertTypePreference(
                alert_type=AlertType.WEATHER_FROST,
                enabled=True,
                channels=[NotificationChannel.PUSH],
                min_urgency=AlertUrgency.HIGH,
            ),
        ],
    )
