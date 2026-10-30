# shared/notification_preferences

Notification Preferences Module | وحدة تفضيلات الإشعارات

Per-user notification preference management for the SAHOOL platform. Controls which alert types reach each user, through which delivery channels, at what urgency thresholds, and during which time windows. Includes a routing engine that applies quiet hours, time-based rules, and urgency overrides before deciding whether and how to deliver a notification.

## File Structure

```
shared/notification_preferences/
├── __init__.py    # Module exports and extensive usage documentation
├── models.py      # All data models, enums, and factory functions
├── manager.py     # NotificationPreferencesManager: CRUD operations on preferences
└── router.py      # NotificationRouter: routing decision engine
```

## Key Components

### Data Models (`models.py`)

| Model | Purpose |
|-------|---------|
| `UserNotificationPreferences` | Root preferences object per user: channels, alert types, quiet hours, time rules, urgency overrides, language |
| `ChannelConfig` | Per-channel configuration: address (phone/email), verified flag, enabled flag |
| `AlertTypePreference` | Per-alert-type settings: enabled, channels, min_urgency |
| `QuietHours` | Do-not-disturb window with timezone and bypass urgency level |
| `TimeBasedRule` | Scheduled channel restriction (e.g. "no SMS on Fri-Sat") with fallback channel |
| `UrgencyOverride` | Per-urgency override: forced channels, bypass flags, immediate delivery, max retries |
| `NotificationRequest` | Inbound notification to route: user_id, alert_type, urgency, bilingual title/body |
| `RoutingDecision` | Output of routing: should_deliver, channels, immediate, deliver_at, language |

Enums:
- `NotificationChannel`: PUSH / SMS / EMAIL / WHATSAPP / TELEGRAM / IN_APP
- `AlertType`: 20+ types including WEATHER_FROST / WEATHER_HEAT / WEATHER_WIND / RPW_DETECTION / PEST_ALERT / DISEASE_ALERT / IRRIGATION_NEEDED / SOIL_MOISTURE_LOW / MARKET_PRICE / EQUIPMENT_ALERT / TASK_DUE / EMERGENCY
- `AlertUrgency`: CRITICAL / HIGH / MEDIUM / LOW / INFO
- `Language`: ARABIC / ENGLISH / BOTH
- `DayOfWeek`: SATURDAY through FRIDAY

Factory functions: `create_default_preferences(user_id, tenant_id)` and `create_minimal_preferences(user_id, tenant_id)`.

Default preferences for new users: Arabic language, Push + In-app channels, quiet hours 10 PM - 6 AM (Asia/Riyadh), critical alerts bypass quiet hours, "no SMS at night" time rule.

### Preferences Manager (`manager.py`)

`NotificationPreferencesManager` provides async CRUD operations for user preferences. Uses a pluggable `PreferencesStorage` protocol, with `InMemoryStorage` as the default implementation (suitable for testing or single-process deployments; replace with a database-backed implementation in production).

Key methods:

```python
await manager.get_preferences(user_id, tenant_id) -> UserNotificationPreferences
await manager.set_language(user_id, language)
await manager.add_channel(user_id, channel, address, verified)
await manager.set_quiet_hours(user_id, start_time, end_time, timezone, bypass_urgency)
await manager.enable_alert_type(user_id, alert_type)
await manager.disable_alert_type(user_id, alert_type)
await manager.set_alert_preference(user_id, alert_type, enabled, channels, min_urgency)
await manager.create_no_sms_at_night_rule(user_id, start_hour, end_hour)
await manager.add_time_rule(user_id, rule)
await manager.set_urgency_override(user_id, override)
await manager.export_preferences(user_id) -> dict
await manager.import_preferences(user_id, data, merge)
await manager.get_users_by_channel(channel, verified_only) -> list[str]
await manager.get_users_subscribed_to_alert(alert_type) -> list[str]
```

### Notification Router (`router.py`)

`NotificationRouter` applies a seven-step decision pipeline to each `NotificationRequest`:

1. Master toggle check (`notifications_enabled`)
2. Alert type enablement
3. Minimum urgency threshold
4. Urgency overrides (force channels, bypass all restrictions)
5. Quiet hours check (with bypass for critical urgency)
6. Time-based rules (channel restrictions with fallback)
7. Channel selection and language determination

Returns a `RoutingDecision` with `should_deliver`, `channels`, `immediate`, `deliver_at`, and `language`. When delivery is not immediate, `deliver_at` is set to the end of the quiet/restricted window.

Standalone functions:
- `route_notification(request, manager)` - convenience async function
- `get_localized_content(request, language)` - extract `{"title": ..., "body": ...}` in chosen language
- `get_channels_for_urgency(urgency)` - default channels by urgency level
- `should_send_immediately(urgency)` - True for CRITICAL / HIGH
- `get_routing_message(decision)` - human-readable routing explanation

## Usage Example

```python
from datetime import time
from shared.notification_preferences import (
    NotificationPreferencesManager,
    NotificationRouter,
    NotificationRequest,
    NotificationChannel,
    AlertType,
    AlertUrgency,
    Language,
    TimeBasedRule,
    DayOfWeek,
    UrgencyOverride,
    route_notification,
    get_localized_content,
)

manager = NotificationPreferencesManager()

# Configure preferences for a farmer
prefs = await manager.get_preferences("farmer-001", tenant_id="sahool")

await manager.set_language("farmer-001", Language.ARABIC)

await manager.add_channel(
    user_id="farmer-001",
    channel=NotificationChannel.SMS,
    address="+966501234567",
    verified=True,
)

# Quiet hours: 10 PM to 6 AM, critical alerts bypass
await manager.set_quiet_hours(
    user_id="farmer-001",
    start_time=time(22, 0),
    end_time=time(6, 0),
    timezone="Asia/Riyadh",
    bypass_urgency=AlertUrgency.CRITICAL,
)

# Opt out of market price notifications
await manager.disable_alert_type("farmer-001", AlertType.MARKET_PRICE)

# Custom channels for frost alerts
await manager.set_alert_preference(
    user_id="farmer-001",
    alert_type=AlertType.WEATHER_FROST,
    enabled=True,
    channels=[NotificationChannel.PUSH, NotificationChannel.SMS],
    min_urgency=AlertUrgency.MEDIUM,
)

# No SMS on weekends
await manager.add_time_rule(
    user_id="farmer-001",
    rule=TimeBasedRule(
        name="No SMS on weekends",
        name_ar="لا رسائل في عطلة نهاية الأسبوع",
        enabled=True,
        start_time=time(0, 0),
        end_time=time(23, 59),
        days=[DayOfWeek.FRIDAY, DayOfWeek.SATURDAY],
        channels=[NotificationChannel.SMS],
        action="channel_fallback",
        fallback_channel=NotificationChannel.PUSH,
        exempt_urgencies=[AlertUrgency.CRITICAL],
    ),
)

# Force critical alerts through immediately regardless of all restrictions
await manager.set_urgency_override(
    user_id="farmer-001",
    override=UrgencyOverride(
        urgency=AlertUrgency.CRITICAL,
        force_channels=[NotificationChannel.PUSH, NotificationChannel.SMS],
        bypass_quiet_hours=True,
        bypass_time_rules=True,
        force_immediate=True,
        max_retries=5,
    ),
)

# Route a notification
request = NotificationRequest(
    user_id="farmer-001",
    alert_type=AlertType.WEATHER_FROST,
    urgency=AlertUrgency.HIGH,
    title="Frost Warning",
    title_ar="تحذير من الصقيع",
    body="Frost expected tonight. Protect your crops.",
    body_ar="صقيع متوقع الليلة. احمِ محاصيلك.",
)

decision = await route_notification(request, manager)
print(f"Deliver: {decision.should_deliver}")
print(f"Channels: {[c.value for c in decision.channels]}")
print(f"Immediate: {decision.immediate}")
print(f"Language: {decision.language.value}")

# Get localized content
content = get_localized_content(request, Language.ARABIC)
print(content["title"])   # Arabic title
print(content["body"])    # Arabic body

# Query all users subscribed to frost alerts
subscribers = await manager.get_users_subscribed_to_alert(AlertType.WEATHER_FROST)
```

## Critical Alert Types

The following alert types may bypass quiet hours when urgency is CRITICAL:
- `AlertType.EMERGENCY`
- `AlertType.RPW_DETECTION` (Red Palm Weevil)
- `AlertType.WEATHER_FROST` (when urgency is HIGH+)

## Version

16.0.0 | Author: SAHOOL Platform Team | Updated: January 2026
