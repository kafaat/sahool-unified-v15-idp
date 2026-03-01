"""
Multi-channel Notification Routing Module | وحدة توجيه الإشعارات متعددة القنوات

Routes notifications to appropriate channels based on priority:
- critical: push + whatsapp + sms    (سوسة النخيل، صقيع)
- warning:  push + whatsapp          (آفات، نقص مغذيات)
- advisory: push + in_app            (نصائح ري، تسميد)
- info:     in_app only              (تحديثات السوق)
"""
from __future__ import annotations

import os
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class NotificationPriority(str, Enum):
    """Notification priority levels | مستويات أولوية الإشعارات"""
    CRITICAL = "critical"   # فوري - خلال 6 ساعات
    WARNING = "warning"     # تحذير - خلال 24-48 ساعة
    ADVISORY = "advisory"   # استشارة - خلال أسبوع
    INFO = "info"           # معلومات - للعلم فقط


class NotificationChannel(str, Enum):
    """Available notification channels | قنوات الإشعارات المتاحة"""
    PUSH = "push"           # FCM push notifications
    WHATSAPP = "whatsapp"   # WhatsApp Business API
    SMS = "sms"             # USSD/SMS gateway
    EMAIL = "email"         # SMTP email
    IN_APP = "in_app"       # WebSocket in-app


# Channel routing rules based on priority
ROUTING_RULES: dict[NotificationPriority, list[NotificationChannel]] = {
    NotificationPriority.CRITICAL: [
        NotificationChannel.PUSH,
        NotificationChannel.WHATSAPP,
        NotificationChannel.SMS,
    ],
    NotificationPriority.WARNING: [
        NotificationChannel.PUSH,
        NotificationChannel.WHATSAPP,
    ],
    NotificationPriority.ADVISORY: [
        NotificationChannel.PUSH,
        NotificationChannel.IN_APP,
    ],
    NotificationPriority.INFO: [
        NotificationChannel.IN_APP,
    ],
}

# Service endpoints for each channel
CHANNEL_SERVICES = {
    NotificationChannel.PUSH: {
        "service": "notification-service",
        "port": 8110,
        "endpoint": "/api/v1/notifications/send",
    },
    NotificationChannel.WHATSAPP: {
        "service": "whatsapp-bot-service",
        "port": 8240,
        "endpoint": "/api/v1/whatsapp/send",
    },
    NotificationChannel.SMS: {
        "service": "ussd-gateway",
        "port": 8183,
        "endpoint": "/api/v1/ussd/send-sms",
    },
    NotificationChannel.EMAIL: {
        "service": "notification-service",
        "port": 8110,
        "endpoint": "/api/v1/notifications/email",
    },
    NotificationChannel.IN_APP: {
        "service": "ws-gateway",
        "port": 8081,
        "endpoint": "/api/v1/ws/notify",
    },
}

# Priority labels in Arabic
PRIORITY_LABELS_AR = {
    NotificationPriority.CRITICAL: "حرج - إجراء فوري",
    NotificationPriority.WARNING: "تحذير - خلال 24-48 ساعة",
    NotificationPriority.ADVISORY: "استشارة - خلال أسبوع",
    NotificationPriority.INFO: "معلومات - للعلم",
}

# Common agricultural alert types
ALERT_TYPES = {
    "rpw_detected": {
        "priority": NotificationPriority.CRITICAL,
        "title": "Red Palm Weevil Detected",
        "title_ar": "تم اكتشاف سوسة النخيل الحمراء",
        "response_window_hours": 48,
    },
    "frost_warning": {
        "priority": NotificationPriority.CRITICAL,
        "title": "Frost Warning",
        "title_ar": "تحذير من الصقيع",
        "response_window_hours": 6,
    },
    "water_stress": {
        "priority": NotificationPriority.CRITICAL,
        "title": "Acute Water Stress Detected",
        "title_ar": "إجهاد مائي حاد",
        "response_window_hours": 12,
    },
    "pest_threshold": {
        "priority": NotificationPriority.WARNING,
        "title": "Pest Threshold Exceeded",
        "title_ar": "تجاوز عتبة الآفات",
        "response_window_hours": 48,
    },
    "nutrient_deficiency": {
        "priority": NotificationPriority.WARNING,
        "title": "Nutrient Deficiency Detected",
        "title_ar": "نقص في المغذيات",
        "response_window_hours": 72,
    },
    "irrigation_advice": {
        "priority": NotificationPriority.ADVISORY,
        "title": "Irrigation Recommendation",
        "title_ar": "توصية ري",
        "response_window_hours": 168,
    },
    "fertilizer_advice": {
        "priority": NotificationPriority.ADVISORY,
        "title": "Fertilizer Recommendation",
        "title_ar": "توصية تسميد",
        "response_window_hours": 168,
    },
    "market_update": {
        "priority": NotificationPriority.INFO,
        "title": "Market Price Update",
        "title_ar": "تحديث أسعار السوق",
        "response_window_hours": None,
    },
    "weather_outlook": {
        "priority": NotificationPriority.INFO,
        "title": "Weekly Weather Outlook",
        "title_ar": "توقعات الطقس الأسبوعية",
        "response_window_hours": None,
    },
}


@dataclass
class NotificationPayload:
    """Notification payload structure | هيكل حمولة الإشعار"""
    notification_id: str = ""
    tenant_id: str = ""
    user_id: str = ""
    priority: NotificationPriority = NotificationPriority.INFO
    alert_type: str = ""
    title: str = ""
    title_ar: str = ""
    body: str = ""
    body_ar: str = ""
    channels: list[NotificationChannel] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    response_window_hours: int | None = None

    def to_dict(self) -> dict:
        return {
            "notification_id": self.notification_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "priority": self.priority.value,
            "alert_type": self.alert_type,
            "title": self.title,
            "title_ar": self.title_ar,
            "body": self.body,
            "body_ar": self.body_ar,
            "channels": [c.value for c in self.channels],
            "data": self.data,
            "created_at": self.created_at,
            "response_window_hours": self.response_window_hours,
        }


class NotificationRouter:
    """Routes notifications to appropriate channels based on priority and user preferences.

    يوجه الإشعارات إلى القنوات المناسبة بناءً على الأولوية وتفضيلات المستخدم.
    """

    def __init__(self):
        self._sent_count = 0
        self._failed_count = 0

    def get_channels(self, priority: NotificationPriority) -> list[NotificationChannel]:
        """Get channels for a given priority level."""
        return ROUTING_RULES.get(priority, [NotificationChannel.IN_APP])

    def get_service_endpoint(self, channel: NotificationChannel) -> dict:
        """Get the service endpoint configuration for a channel."""
        return CHANNEL_SERVICES.get(channel, {})

    def build_notification(
        self,
        notification_id: str,
        tenant_id: str,
        user_id: str,
        alert_type: str,
        body: str = "",
        body_ar: str = "",
        extra_data: dict | None = None,
    ) -> NotificationPayload:
        """Build a notification payload from an alert type.

        بناء حمولة إشعار من نوع التنبيه.
        """
        alert_config = ALERT_TYPES.get(alert_type, {})
        priority = alert_config.get("priority", NotificationPriority.INFO)
        channels = self.get_channels(priority)

        return NotificationPayload(
            notification_id=notification_id,
            tenant_id=tenant_id,
            user_id=user_id,
            priority=priority,
            alert_type=alert_type,
            title=alert_config.get("title", alert_type),
            title_ar=alert_config.get("title_ar", alert_type),
            body=body,
            body_ar=body_ar,
            channels=channels,
            data=extra_data or {},
            created_at=datetime.now(timezone.utc).isoformat(),
            response_window_hours=alert_config.get("response_window_hours"),
        )

    async def route_notification(self, payload: NotificationPayload) -> dict:
        """Route notification to all target channels.

        توجيه الإشعار إلى جميع القنوات المستهدفة.

        Returns dict with channel results.
        """
        results = {}

        for channel in payload.channels:
            service = self.get_service_endpoint(channel)
            try:
                # In production, this would make HTTP calls to the service
                # For now, log the routing decision
                logger.info(
                    "Routing notification",
                    extra={
                        "notification_id": payload.notification_id,
                        "channel": channel.value,
                        "service": service.get("service", "unknown"),
                        "priority": payload.priority.value,
                    }
                )
                results[channel.value] = {
                    "status": "routed",
                    "service": service.get("service", "unknown"),
                    "endpoint": f"http://{service.get('service', 'localhost')}:{service.get('port', 8080)}{service.get('endpoint', '/')}",
                }
                self._sent_count += 1
            except Exception as e:
                logger.error(f"Failed to route to {channel.value}: {e}")
                results[channel.value] = {"status": "failed", "error": str(e)}
                self._failed_count += 1

        return results

    def get_stats(self) -> dict:
        """Get routing statistics."""
        return {
            "sent": self._sent_count,
            "failed": self._failed_count,
            "total": self._sent_count + self._failed_count,
        }
