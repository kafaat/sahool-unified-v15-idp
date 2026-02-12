"""
Notification Preferences Module
===============================
وحدة تفضيلات الإشعارات

A comprehensive notification preferences module for the SAHOOL platform.
Provides per-user notification settings with bilingual Arabic/English support.

Features:
- Per-user notification settings
- Channel preferences (push, SMS, email, WhatsApp, Telegram, in-app)
- Alert type filtering
- Quiet hours management (do not disturb)
- Language preferences
- Time-based routing rules
- Urgency overrides for critical notifications

Author: SAHOOL Platform Team
Updated: January 2026

Usage Examples
--------------

1. Create and manage user preferences:

    from shared.notification_preferences import (
        NotificationPreferencesManager,
        NotificationChannel,
        AlertType,
        AlertUrgency,
        Language,
    )

    # Initialize manager
    manager = NotificationPreferencesManager()

    # Get or create preferences for a user
    prefs = await manager.get_preferences(
        user_id="farmer-001",
        tenant_id="sahool",
    )

    # Set language preference
    await manager.set_language(
        user_id="farmer-001",
        language=Language.ARABIC,
    )

    # Add a verified SMS channel
    await manager.add_channel(
        user_id="farmer-001",
        channel=NotificationChannel.SMS,
        address="+966501234567",
        verified=True,
    )

    # Set quiet hours (10 PM to 6 AM)
    from datetime import time
    await manager.set_quiet_hours(
        user_id="farmer-001",
        start_time=time(22, 0),
        end_time=time(6, 0),
        timezone="Asia/Riyadh",
        bypass_urgency=AlertUrgency.CRITICAL,
    )

2. Configure alert type preferences:

    # Disable market price notifications
    await manager.disable_alert_type(
        user_id="farmer-001",
        alert_type=AlertType.MARKET_PRICE,
    )

    # Set specific channels for weather alerts
    await manager.set_alert_preference(
        user_id="farmer-001",
        alert_type=AlertType.WEATHER_FROST,
        enabled=True,
        channels=[NotificationChannel.PUSH, NotificationChannel.SMS],
        min_urgency=AlertUrgency.HIGH,
    )

3. Add time-based rules:

    from shared.notification_preferences import TimeBasedRule

    # Create "no SMS at night" rule
    await manager.create_no_sms_at_night_rule(
        user_id="farmer-001",
        start_hour=22,
        end_hour=6,
    )

    # Or create a custom rule
    rule = TimeBasedRule(
        name="No email on weekends",
        name_ar="لا بريد في عطلة نهاية الأسبوع",
        enabled=True,
        start_time=time(0, 0),
        end_time=time(23, 59),
        days=[DayOfWeek.FRIDAY, DayOfWeek.SATURDAY],
        channels=[NotificationChannel.EMAIL],
        action="channel_fallback",
        fallback_channel=NotificationChannel.PUSH,
        exempt_urgencies=[AlertUrgency.CRITICAL, AlertUrgency.HIGH],
    )
    await manager.add_time_rule(user_id="farmer-001", rule=rule)

4. Route notifications based on preferences:

    from shared.notification_preferences import (
        NotificationRouter,
        NotificationRequest,
        route_notification,
    )

    # Create a notification request
    request = NotificationRequest(
        user_id="farmer-001",
        alert_type=AlertType.WEATHER_FROST,
        urgency=AlertUrgency.HIGH,
        title="Frost Warning",
        title_ar="تحذير من الصقيع",
        body="Frost expected tonight. Protect your crops.",
        body_ar="صقيع متوقع الليلة. احمِ محاصيلك.",
    )

    # Route the notification
    decision = await route_notification(request, manager)

    print(f"Should deliver: {decision.should_deliver}")
    print(f"Channels: {[c.value for c in decision.channels]}")
    print(f"Immediate: {decision.immediate}")
    print(f"Language: {decision.language.value}")

    if not decision.immediate:
        print(f"Deliver at: {decision.deliver_at}")

5. Handle urgency overrides:

    from shared.notification_preferences import UrgencyOverride

    # Configure critical alerts to bypass all restrictions
    override = UrgencyOverride(
        urgency=AlertUrgency.CRITICAL,
        force_channels=[NotificationChannel.PUSH, NotificationChannel.SMS],
        bypass_quiet_hours=True,
        bypass_time_rules=True,
        force_immediate=True,
        max_retries=5,
    )
    await manager.set_urgency_override(
        user_id="farmer-001",
        override=override,
    )

6. Export/import preferences:

    # Export preferences as JSON
    data = await manager.export_preferences(user_id="farmer-001")

    # Import preferences (optionally merge with existing)
    await manager.import_preferences(
        user_id="farmer-002",
        data=data,
        merge=True,
    )

7. Get localized content:

    from shared.notification_preferences import get_localized_content

    content = get_localized_content(request, Language.ARABIC)
    print(content["title"])  # Prints Arabic title
    print(content["body"])   # Prints Arabic body

8. Query users by preferences:

    # Get users with SMS enabled
    user_ids = await manager.get_users_by_channel(
        channel=NotificationChannel.SMS,
        verified_only=True,
    )

    # Get users subscribed to frost alerts
    user_ids = await manager.get_users_subscribed_to_alert(
        alert_type=AlertType.WEATHER_FROST,
    )

Default Preferences
-------------------

New users get the following default preferences:
- Language: Arabic
- Default channels: Push, In-app
- Quiet hours: 10 PM - 6 AM (Asia/Riyadh timezone)
- Critical alerts bypass quiet hours
- "No SMS at night" rule (10 PM - 6 AM)

Critical Alerts
---------------

The following alert types are considered critical and may bypass preferences:
- AlertType.EMERGENCY - Emergency situations
- AlertType.RPW_DETECTION - Red Palm Weevil detection
- AlertType.WEATHER_FROST - Frost warnings (when high urgency)

Bilingual Support
-----------------

All models support Arabic (ar) and English (en) content:
- title / title_ar
- body / body_ar
- name / name_ar
- description / description_ar

Use Language.BOTH to receive content in both languages.
"""

# Enums
# Manager
from .manager import (
    InMemoryStorage,
    NotificationPreferencesManager,
    PreferencesStorage,
)

# Core data models
# Factory functions
from .models import (
    AlertType,
    AlertTypePreference,
    AlertUrgency,
    ChannelConfig,
    DayOfWeek,
    Language,
    NotificationChannel,
    NotificationRequest,
    QuietHours,
    RoutingDecision,
    TimeBasedRule,
    UrgencyOverride,
    UserNotificationPreferences,
    create_default_preferences,
    create_minimal_preferences,
)

# Router
from .router import (
    ROUTING_MESSAGES,
    NotificationRouter,
    get_channels_for_urgency,
    get_localized_content,
    get_routing_message,
    route_notification,
    should_send_immediately,
)

__all__ = [
    # Enums
    "NotificationChannel",
    "AlertType",
    "AlertUrgency",
    "Language",
    "DayOfWeek",
    # Core data models
    "QuietHours",
    "ChannelConfig",
    "AlertTypePreference",
    "TimeBasedRule",
    "UrgencyOverride",
    "UserNotificationPreferences",
    "NotificationRequest",
    "RoutingDecision",
    # Factory functions
    "create_default_preferences",
    "create_minimal_preferences",
    # Manager
    "NotificationPreferencesManager",
    "PreferencesStorage",
    "InMemoryStorage",
    # Router
    "NotificationRouter",
    "route_notification",
    "get_localized_content",
    "should_send_immediately",
    "get_channels_for_urgency",
    "get_routing_message",
    "ROUTING_MESSAGES",
]

__version__ = "16.0.0"
