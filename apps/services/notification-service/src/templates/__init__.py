"""
SAHOOL Notification Templates Package
حزمة قوالب الإشعارات

Bilingual notification templating system with channel-specific formatting.
"""

from .notification_templates import (
    NotificationTemplateManager,
    NotificationTemplate,
    TemplateCategory,
    NotificationChannel,
    get_template_manager,
    render_notification
)

__all__ = [
    "NotificationTemplateManager",
    "NotificationTemplate",
    "TemplateCategory",
    "NotificationChannel",
    "get_template_manager",
    "render_notification"
]
