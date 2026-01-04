"""
SAHOOL Notification Service - Database Models
نماذج قاعدة البيانات - Tortoise ORM
"""

from datetime import datetime
from enum import Enum

from tortoise import fields
from tortoise.models import Model


class ChannelType(str, Enum):
    """
    نوع القناة - Channel Type Enum
    """

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"
    IN_APP = "in_app"


class Notification(Model):
    """
    نموذج الإشعار
    Notification Model - stores all notifications sent to farmers
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(
        max_length=100,
        index=True,
        null=True,
        description="Tenant/Organization ID for multi-tenancy",
    )
    user_id = fields.CharField(
        max_length=100,
        index=True,
        description="Farmer/User ID who receives this notification",
    )

    # Content
    title = fields.CharField(max_length=255, description="Notification title (English)")
    title_ar = fields.CharField(
        max_length=255, null=True, description="Notification title (Arabic)"
    )
    body = fields.TextField(description="Notification body/content (English)")
    body_ar = fields.TextField(
        null=True, description="Notification body/content (Arabic)"
    )

    # Categorization
    type = fields.CharField(
        max_length=50,
        index=True,
        description="weather_alert, pest_outbreak, irrigation_reminder, etc.",
    )
    priority = fields.CharField(
        max_length=20, default="medium", description="low, medium, high, critical"
    )
    channel = fields.CharField(
        max_length=20, default="in_app", description="push, sms, in_app, email"
    )

    # Status tracking
    status = fields.CharField(
        max_length=20,
        default="pending",
        index=True,
        description="pending, sent, failed, read",
    )
    sent_at = fields.DatetimeField(
        null=True, description="When the notification was sent"
    )
    read_at = fields.DatetimeField(
        null=True, description="When the user read the notification"
    )

    # Metadata
    data = fields.JSONField(
        null=True, description="Additional data/context for the notification"
    )
    action_url = fields.CharField(
        max_length=500, null=True, description="Deep link or action URL"
    )

    # Targeting
    target_governorates = fields.JSONField(
        null=True, description="List of governorates this applies to"
    )
    target_crops = fields.JSONField(
        null=True, description="List of crop types this applies to"
    )

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True, index=True)
    updated_at = fields.DatetimeField(auto_now=True)
    expires_at = fields.DatetimeField(
        null=True, index=True, description="When this notification expires"
    )

    class Meta:
        table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            ("user_id", "status"),
            ("user_id", "created_at"),
            ("type", "created_at"),
            ("tenant_id", "user_id"),
        ]

    def __str__(self):
        return f"Notification({self.id}, {self.type}, {self.user_id})"

    @property
    def is_read(self) -> bool:
        """Check if notification has been read"""
        return self.read_at is not None

    @property
    def is_expired(self) -> bool:
        """Check if notification is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


class NotificationTemplate(Model):
    """
    نموذج قالب الإشعار
    Notification Template - reusable templates for common notifications
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=100, index=True, null=True)

    # Template identification
    name = fields.CharField(
        max_length=100, unique=True, description="Template name/slug"
    )
    description = fields.CharField(max_length=255, null=True)

    # Template content (supports Jinja2-style variables)
    title_template = fields.CharField(
        max_length=255, description="Title template with {{variables}}"
    )
    title_template_ar = fields.CharField(
        max_length=255, null=True, description="Arabic title template"
    )
    body_template = fields.TextField(description="Body template with {{variables}}")
    body_template_ar = fields.TextField(null=True, description="Arabic body template")

    # Default settings
    type = fields.CharField(max_length=50, description="Default notification type")
    priority = fields.CharField(max_length=20, default="medium")
    channel = fields.CharField(max_length=20, default="in_app")

    # Metadata
    variables = fields.JSONField(
        null=True, description="List of available variables for this template"
    )
    default_data = fields.JSONField(null=True, description="Default data to include")

    # Status
    is_active = fields.BooleanField(default=True, index=True)

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notification_templates"
        ordering = ["name"]

    def __str__(self):
        return f"NotificationTemplate({self.name})"


class NotificationChannel(Model):
    """
    نموذج قناة الإشعار
    Notification Channel - stores user's communication channels and addresses
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=100, index=True, null=True)
    user_id = fields.CharField(max_length=100, index=True, description="Farmer/User ID")

    # Channel information
    channel = fields.CharEnumField(
        ChannelType, description="Channel type: EMAIL, SMS, PUSH, WHATSAPP, IN_APP"
    )
    address = fields.CharField(
        max_length=255, description="Channel address (email, phone, FCM token, etc.)"
    )

    # Verification
    verified = fields.BooleanField(
        default=False, description="Whether this channel is verified"
    )
    verified_at = fields.DatetimeField(
        null=True, description="When the channel was verified"
    )
    verification_code = fields.CharField(
        max_length=10,
        null=True,
        description="Verification code for unverified channels",
    )

    # Status
    enabled = fields.BooleanField(
        default=True, description="Whether this channel is enabled for notifications"
    )

    # Metadata
    metadata = fields.JSONField(
        null=True, description="Additional channel metadata (device info, etc.)"
    )

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notification_channels"
        unique_together = (("user_id", "channel", "address"),)
        indexes = [
            ("tenant_id", "user_id"),
            ("user_id", "channel"),
        ]

    def __str__(self):
        return f"NotificationChannel({self.user_id}, {self.channel}, {self.address})"


class NotificationPreference(Model):
    """
    نموذج تفضيلات الإشعارات
    Notification Preferences - event-specific user preferences for notification channels
    """

    id = fields.UUIDField(pk=True)
    tenant_id = fields.CharField(max_length=100, index=True, null=True)
    user_id = fields.CharField(max_length=100, index=True, description="Farmer/User ID")

    # Event type for this preference
    event_type = fields.CharField(
        max_length=50, description="Event type: weather_alert, pest_outbreak, etc."
    )

    # Channels to use for this event type
    channels = fields.JSONField(
        default=list,
        description="List of channel types to use: ['email', 'sms', 'push']",
    )

    # General settings
    enabled = fields.BooleanField(
        default=True,
        description="Whether notifications for this event type are enabled",
    )

    # Quiet hours (do not disturb) - applies to all event types for this user
    quiet_hours_start = fields.TimeField(
        null=True, description="Start of quiet hours (e.g., 22:00)"
    )
    quiet_hours_end = fields.TimeField(
        null=True, description="End of quiet hours (e.g., 06:00)"
    )

    # Metadata
    metadata = fields.JSONField(
        null=True, description="Additional preferences metadata"
    )

    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "notification_preferences"
        unique_together = (("user_id", "event_type"),)
        indexes = [
            ("tenant_id", "user_id"),
            ("user_id", "event_type"),
        ]

    def __str__(self):
        return f"NotificationPreference({self.user_id}, {self.event_type})"

    def is_in_quiet_hours(self, check_time: datetime | None = None) -> bool:
        """Check if current time is in quiet hours"""
        if not self.quiet_hours_start or not self.quiet_hours_end:
            return False

        check_time = datetime.utcnow().time() if check_time is None else check_time.time()

        # Handle overnight quiet hours (e.g., 22:00 to 06:00)
        if self.quiet_hours_start > self.quiet_hours_end:
            return (
                check_time >= self.quiet_hours_start
                or check_time <= self.quiet_hours_end
            )
        else:
            return self.quiet_hours_start <= check_time <= self.quiet_hours_end


class NotificationLog(Model):
    """
    نموذج سجل الإشعارات
    Notification Log - tracks delivery attempts and status
    """

    id = fields.UUIDField(pk=True)
    notification = fields.ForeignKeyField(
        "models.Notification", related_name="logs", on_delete=fields.CASCADE
    )

    # Delivery information
    channel = fields.CharField(max_length=20, description="Channel used for delivery")
    status = fields.CharField(
        max_length=20, index=True, description="success, failed, pending, retry"
    )

    # Error tracking
    error_message = fields.TextField(
        null=True, description="Error message if delivery failed"
    )
    error_code = fields.CharField(max_length=50, null=True)

    # Provider response
    provider_response = fields.JSONField(
        null=True, description="Response from FCM, SMS gateway, etc."
    )
    provider_message_id = fields.CharField(
        max_length=255, null=True, description="Message ID from provider"
    )

    # Retry information
    retry_count = fields.IntField(default=0, description="Number of retry attempts")
    next_retry_at = fields.DatetimeField(null=True, description="When to retry next")

    # Timestamps
    attempted_at = fields.DatetimeField(auto_now_add=True, index=True)
    completed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "notification_logs"
        ordering = ["-attempted_at"]
        indexes = [
            ("status", "attempted_at"),
        ]

    def __str__(self):
        return f"NotificationLog({self.notification_id}, {self.channel}, {self.status})"
