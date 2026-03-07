"""
Notification Router
===================
موجه الإشعارات

Routes notifications based on user preferences, applying quiet hours,
time-based rules, urgency overrides, and channel filtering.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from .manager import NotificationPreferencesManager
from .models import (
    AlertType,
    AlertUrgency,
    DayOfWeek,
    Language,
    NotificationChannel,
    NotificationRequest,
    QuietHours,
    RoutingDecision,
    TimeBasedRule,
    UserNotificationPreferences,
)

logger = logging.getLogger(__name__)


class NotificationRouter:
    """
    Routes notifications based on user preferences
    يوجه الإشعارات بناءً على تفضيلات المستخدم

    Applies the following routing logic in order:
    1. Master toggle check (notifications_enabled)
    2. Alert type enablement check
    3. Minimum urgency check
    4. Urgency overrides
    5. Quiet hours check
    6. Time-based rules
    7. Channel selection
    """

    def __init__(self, preferences_manager: NotificationPreferencesManager):
        """
        Initialize the router

        Args:
            preferences_manager: Manager for accessing user preferences
        """
        self.preferences_manager = preferences_manager

    async def route(
        self,
        request: NotificationRequest,
        current_time: datetime | None = None,
    ) -> RoutingDecision:
        """
        Route a notification request based on user preferences
        توجيه طلب إشعار بناءً على تفضيلات المستخدم

        Args:
            request: Notification request to route
            current_time: Current time (for testing). Uses now if not provided.

        Returns:
            RoutingDecision with channels and delivery timing
        """
        decision = RoutingDecision(
            request_id=request.id,
            should_deliver=True,
            channels=[],
            immediate=True,
        )

        # Get user preferences
        preferences = await self.preferences_manager.get_preferences(
            request.user_id,
            request.tenant_id,
            create_if_missing=True,
        )
        decision.preferences_version = preferences.version
        decision.language = preferences.language

        # Current time with timezone
        now = current_time or datetime.now(UTC)

        # Step 1: Master toggle check
        if not preferences.notifications_enabled:
            # Check if urgency allows bypass
            urgency_override = preferences.get_urgency_override(request.urgency)
            if not urgency_override or not urgency_override.bypass_quiet_hours:
                decision.should_deliver = False
                decision.rejection_reasons.append("Notifications disabled")
                decision.rejection_reasons_ar.append("الإشعارات معطلة")
                logger.debug(f"Notification {request.id} rejected: notifications disabled for user {request.user_id}")
                return decision

        # Step 2: Alert type check
        alert_pref = preferences.get_alert_preference(request.alert_type)
        if alert_pref and not alert_pref.enabled:
            # Check urgency override
            urgency_override = preferences.get_urgency_override(request.urgency)
            if not urgency_override:
                decision.should_deliver = False
                decision.rejection_reasons.append(f"Alert type '{request.alert_type.value}' disabled")
                decision.rejection_reasons_ar.append(f"نوع التنبيه '{request.alert_type.value}' معطل")
                logger.debug(f"Notification {request.id} rejected: alert type disabled")
                return decision

        # Step 3: Minimum urgency check
        if alert_pref and not self._meets_minimum_urgency(request.urgency, alert_pref.min_urgency):
            decision.should_deliver = False
            decision.rejection_reasons.append(
                f"Urgency '{request.urgency.value}' below minimum '{alert_pref.min_urgency.value}'"
            )
            decision.rejection_reasons_ar.append(
                f"الإلحاح '{request.urgency.value}' أقل من الحد الأدنى '{alert_pref.min_urgency.value}'"
            )
            logger.debug(f"Notification {request.id} rejected: below minimum urgency")
            return decision

        # Step 4: Apply urgency overrides
        urgency_override = preferences.get_urgency_override(request.urgency)
        if urgency_override:
            decision.applied_rules.append(f"urgency_override:{request.urgency.value}")

            if urgency_override.force_immediate:
                decision.immediate = True

            if urgency_override.force_channels:
                decision.channels = list(urgency_override.force_channels)

        # Step 5: Quiet hours check
        in_quiet_hours, should_bypass = self._check_quiet_hours(
            preferences=preferences,
            urgency=request.urgency,
            now=now,
        )

        if in_quiet_hours:
            if should_bypass:
                decision.quiet_hours_bypassed = True
                decision.bypass_reason = f"Urgency '{request.urgency.value}' bypasses quiet hours"
                decision.applied_rules.append("quiet_hours_bypassed")
            else:
                # Hold notification until quiet hours end
                decision.immediate = False
                decision.deliver_at = self._calculate_quiet_hours_end(preferences.quiet_hours, now)
                decision.applied_rules.append("quiet_hours_hold")
                logger.debug(f"Notification {request.id} held until {decision.deliver_at} (quiet hours)")

        # Step 6: Apply time-based rules
        time_rules_result = self._apply_time_rules(
            preferences=preferences,
            request=request,
            current_channels=decision.channels or list(preferences.default_channels),
            now=now,
        )

        if time_rules_result["action_taken"]:
            decision.channels = time_rules_result["channels"]
            decision.applied_rules.extend(time_rules_result["applied_rules"])

            if time_rules_result["hold_until"]:
                decision.immediate = False
                decision.deliver_at = time_rules_result["hold_until"]

        # Step 7: Determine final channels
        if not decision.channels:
            # Use alert-specific channels if defined, otherwise defaults
            if alert_pref and alert_pref.channels:
                decision.channels = list(alert_pref.channels)
            else:
                decision.channels = list(preferences.default_channels)

        # Filter channels to only enabled and verified ones
        decision.channels = self._filter_channels(
            channels=decision.channels,
            preferences=preferences,
            require_verified=False,  # Allow unverified for push/in-app
        )

        if not decision.channels:
            decision.should_deliver = False
            decision.rejection_reasons.append("No enabled channels available")
            decision.rejection_reasons_ar.append("لا توجد قنوات مفعلة متاحة")
            logger.debug(f"Notification {request.id} rejected: no channels available")
            return decision

        logger.info(
            f"Notification {request.id} routed: channels={[c.value for c in decision.channels]}, "
            f"immediate={decision.immediate}, rules={decision.applied_rules}"
        )

        return decision

    async def route_batch(
        self,
        requests: list[NotificationRequest],
        current_time: datetime | None = None,
    ) -> list[RoutingDecision]:
        """
        Route multiple notifications
        توجيه إشعارات متعددة

        Args:
            requests: List of notification requests
            current_time: Current time (for testing)

        Returns:
            List of routing decisions
        """
        decisions = []
        for request in requests:
            decision = await self.route(request, current_time)
            decisions.append(decision)
        return decisions

    def _meets_minimum_urgency(
        self,
        actual: AlertUrgency,
        minimum: AlertUrgency,
    ) -> bool:
        """
        Check if actual urgency meets minimum requirement
        التحقق مما إذا كان الإلحاح الفعلي يلبي الحد الأدنى
        """
        urgency_order = {
            AlertUrgency.CRITICAL: 4,
            AlertUrgency.HIGH: 3,
            AlertUrgency.MEDIUM: 2,
            AlertUrgency.LOW: 1,
            AlertUrgency.INFORMATIONAL: 0,
        }
        return urgency_order.get(actual, 0) >= urgency_order.get(minimum, 0)

    def _check_quiet_hours(
        self,
        preferences: UserNotificationPreferences,
        urgency: AlertUrgency,
        now: datetime,
    ) -> tuple[bool, bool]:
        """
        Check if current time is in quiet hours and if should bypass

        Returns:
            Tuple of (is_in_quiet_hours, should_bypass)
        """
        quiet = preferences.quiet_hours

        if not quiet.enabled:
            return False, False

        # Convert to user timezone
        try:
            tz = ZoneInfo(quiet.timezone)
            local_now = now.astimezone(tz) if now.tzinfo else now.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)
        except Exception:
            local_now = now

        current_time = local_now.time()
        current_day = DayOfWeek(local_now.strftime("%A").lower())

        # Check if quiet hours apply today
        if quiet.days and current_day not in quiet.days:
            return False, False

        # Check if current time is in quiet hours
        in_quiet = self._time_in_range(current_time, quiet.start_time, quiet.end_time)

        if not in_quiet:
            return False, False

        # Check if urgency bypasses quiet hours
        should_bypass = self._meets_minimum_urgency(urgency, quiet.bypass_urgency)

        return True, should_bypass

    def _time_in_range(
        self,
        check_time: time,
        start: time,
        end: time,
    ) -> bool:
        """
        Check if time is within a range (handles overnight ranges)
        التحقق مما إذا كان الوقت ضمن نطاق (يتعامل مع النطاقات الليلية)
        """
        if start <= end:
            # Normal range (e.g., 09:00 - 17:00)
            return start <= check_time <= end
        else:
            # Overnight range (e.g., 22:00 - 06:00)
            return check_time >= start or check_time <= end

    def _calculate_quiet_hours_end(
        self,
        quiet: QuietHours,
        now: datetime,
    ) -> datetime:
        """
        Calculate when quiet hours end
        حساب وقت انتهاء الساعات الهادئة
        """
        try:
            tz = ZoneInfo(quiet.timezone)
            local_now = now.astimezone(tz) if now.tzinfo else now.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)
        except Exception:
            local_now = now

        current_time = local_now.time()
        end_time = quiet.end_time

        # If current time is before end time today, quiet hours end today
        if current_time <= end_time:
            end_datetime = local_now.replace(
                hour=end_time.hour,
                minute=end_time.minute,
                second=0,
                microsecond=0,
            )
        else:
            # Quiet hours end tomorrow
            end_datetime = (local_now + timedelta(days=1)).replace(
                hour=end_time.hour,
                minute=end_time.minute,
                second=0,
                microsecond=0,
            )

        # Convert back to UTC
        return end_datetime.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

    def _apply_time_rules(
        self,
        preferences: UserNotificationPreferences,
        request: NotificationRequest,
        current_channels: list[NotificationChannel],
        now: datetime,
    ) -> dict[str, Any]:
        """
        Apply time-based routing rules
        تطبيق قواعد التوجيه حسب الوقت
        """
        result = {
            "action_taken": False,
            "channels": current_channels,
            "applied_rules": [],
            "hold_until": None,
        }

        # Sort rules by priority
        rules = sorted(preferences.time_rules, key=lambda r: r.priority, reverse=True)

        for rule in rules:
            if not rule.enabled:
                continue

            # Check if rule applies to current time
            try:
                tz = ZoneInfo(preferences.quiet_hours.timezone)
                local_now = now.astimezone(tz) if now.tzinfo else now.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)
            except Exception:
                local_now = now

            current_time = local_now.time()
            current_day = DayOfWeek(local_now.strftime("%A").lower())

            # Check day restriction
            if rule.days and current_day not in rule.days:
                continue

            # Check time restriction
            if not self._time_in_range(current_time, rule.start_time, rule.end_time):
                continue

            # Check alert type restriction
            if rule.alert_types and request.alert_type not in rule.alert_types:
                continue

            # Check exemption by urgency
            if request.urgency in rule.exempt_urgencies:
                continue

            # Check channel restriction
            affected_channels = (
                [c for c in result["channels"] if c in rule.channels] if rule.channels else result["channels"]
            )

            if not affected_channels:
                continue

            # Apply rule action
            result["action_taken"] = True
            result["applied_rules"].append(f"time_rule:{rule.id}:{rule.action}")

            if rule.action == "hold":
                # Calculate when rule ends
                result["hold_until"] = self._calculate_rule_end(rule, now, preferences.quiet_hours.timezone)
                logger.debug(f"Rule '{rule.name}' holding until {result['hold_until']}")

            elif rule.action == "drop":
                # Remove affected channels
                result["channels"] = [c for c in result["channels"] if c not in affected_channels]
                logger.debug(f"Rule '{rule.name}' dropped channels: {[c.value for c in affected_channels]}")

            elif rule.action == "channel_fallback":
                # Replace affected channels with fallback
                if rule.fallback_channel:
                    result["channels"] = [
                        rule.fallback_channel if c in affected_channels else c for c in result["channels"]
                    ]
                    # Remove duplicates
                    result["channels"] = list(dict.fromkeys(result["channels"]))
                    logger.debug(f"Rule '{rule.name}' fallback to {rule.fallback_channel.value}")

            elif rule.action == "batch":
                # Mark for batching (handled by delivery system)
                result["applied_rules"].append("batch_requested")

        return result

    def _calculate_rule_end(
        self,
        rule: TimeBasedRule,
        now: datetime,
        timezone: str,
    ) -> datetime:
        """
        Calculate when a time-based rule ends
        حساب وقت انتهاء قاعدة حسب الوقت
        """
        try:
            tz = ZoneInfo(timezone)
            local_now = now.astimezone(tz) if now.tzinfo else now.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)
        except Exception:
            local_now = now

        current_time = local_now.time()
        end_time = rule.end_time

        # If current time is before end time today, rule ends today
        if current_time <= end_time:
            end_datetime = local_now.replace(
                hour=end_time.hour,
                minute=end_time.minute,
                second=0,
                microsecond=0,
            )
        else:
            # Rule ends tomorrow
            end_datetime = (local_now + timedelta(days=1)).replace(
                hour=end_time.hour,
                minute=end_time.minute,
                second=0,
                microsecond=0,
            )

        # Convert back to UTC
        return end_datetime.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)

    def _filter_channels(
        self,
        channels: list[NotificationChannel],
        preferences: UserNotificationPreferences,
        require_verified: bool = False,
    ) -> list[NotificationChannel]:
        """
        Filter channels to only enabled (and optionally verified) ones
        تصفية القنوات إلى المفعلة فقط (والمتحقق منها اختيارياً)
        """
        filtered = []

        for channel in channels:
            # Push and in-app don't require explicit config
            if channel in [NotificationChannel.PUSH, NotificationChannel.IN_APP]:
                filtered.append(channel)
                continue

            config = preferences.get_channel_config(channel)
            if config and config.enabled:
                if not require_verified or config.verified:
                    filtered.append(channel)

        return filtered


# =============================================================================
# Convenience Functions
# =============================================================================


async def route_notification(
    request: NotificationRequest,
    preferences_manager: NotificationPreferencesManager,
    current_time: datetime | None = None,
) -> RoutingDecision:
    """
    Route a single notification
    توجيه إشعار واحد

    Args:
        request: Notification request
        preferences_manager: Preferences manager instance
        current_time: Current time (for testing)

    Returns:
        Routing decision
    """
    router = NotificationRouter(preferences_manager)
    return await router.route(request, current_time)


def get_localized_content(
    request: NotificationRequest,
    language: Language,
) -> dict[str, str]:
    """
    Get localized notification content based on language preference
    الحصول على محتوى الإشعار المترجم بناءً على تفضيل اللغة

    Args:
        request: Notification request
        language: Language preference

    Returns:
        Dictionary with 'title' and 'body' in the preferred language
    """
    if language == Language.ARABIC:
        return {
            "title": request.title_ar or request.title,
            "body": request.body_ar or request.body,
        }
    elif language == Language.ENGLISH:
        return {
            "title": request.title or request.title_ar,
            "body": request.body or request.body_ar,
        }
    else:  # BOTH
        return {
            "title": f"{request.title}\n{request.title_ar}" if request.title_ar else request.title,
            "body": f"{request.body}\n{request.body_ar}" if request.body_ar else request.body,
            "title_en": request.title,
            "title_ar": request.title_ar,
            "body_en": request.body,
            "body_ar": request.body_ar,
        }


def should_send_immediately(
    urgency: AlertUrgency,
    alert_type: AlertType,
) -> bool:
    """
    Determine if a notification should be sent immediately based on type and urgency
    تحديد ما إذا كان يجب إرسال الإشعار فوراً بناءً على النوع والإلحاح

    Args:
        urgency: Alert urgency
        alert_type: Alert type

    Returns:
        True if should send immediately
    """
    # Critical alerts always go immediately
    if urgency == AlertUrgency.CRITICAL:
        return True

    # Emergency and RPW detection always immediate
    if alert_type in [AlertType.EMERGENCY, AlertType.RPW_DETECTION]:
        return True

    # Frost warnings are time-sensitive
    if alert_type == AlertType.WEATHER_FROST and urgency in [
        AlertUrgency.HIGH,
        AlertUrgency.CRITICAL,
    ]:
        return True

    # High urgency generally goes immediately
    if urgency == AlertUrgency.HIGH:
        return True

    return False


def get_channels_for_urgency(
    urgency: AlertUrgency,
) -> list[NotificationChannel]:
    """
    Get recommended channels based on urgency
    الحصول على القنوات الموصى بها بناءً على الإلحاح

    Args:
        urgency: Alert urgency

    Returns:
        List of recommended channels
    """
    if urgency == AlertUrgency.CRITICAL:
        return [
            NotificationChannel.PUSH,
            NotificationChannel.SMS,
            NotificationChannel.WHATSAPP,
            NotificationChannel.IN_APP,
        ]
    elif urgency in [AlertUrgency.HIGH, AlertUrgency.MEDIUM]:
        return [
            NotificationChannel.PUSH,
            NotificationChannel.IN_APP,
        ]
    else:
        return [
            NotificationChannel.IN_APP,
        ]


# =============================================================================
# Bilingual Messages
# =============================================================================

ROUTING_MESSAGES = {
    "notifications_disabled": {
        "en": "Notifications are disabled",
        "ar": "الإشعارات معطلة",
    },
    "alert_type_disabled": {
        "en": "This alert type is disabled",
        "ar": "هذا النوع من التنبيهات معطل",
    },
    "below_minimum_urgency": {
        "en": "Alert urgency is below your minimum threshold",
        "ar": "إلحاح التنبيه أقل من الحد الأدنى المحدد",
    },
    "quiet_hours_active": {
        "en": "Quiet hours are active. Notification will be delivered later.",
        "ar": "الساعات الهادئة نشطة. سيتم تسليم الإشعار لاحقاً.",
    },
    "quiet_hours_bypassed": {
        "en": "Quiet hours bypassed due to high urgency",
        "ar": "تم تجاوز الساعات الهادئة بسبب الإلحاح العالي",
    },
    "no_channels_available": {
        "en": "No notification channels are available",
        "ar": "لا توجد قنوات إشعارات متاحة",
    },
    "channel_fallback_applied": {
        "en": "Notification redirected to alternative channel",
        "ar": "تم تحويل الإشعار إلى قناة بديلة",
    },
}


def get_routing_message(
    key: str,
    language: Language = Language.ARABIC,
) -> str:
    """
    Get a localized routing message
    الحصول على رسالة توجيه مترجمة

    Args:
        key: Message key
        language: Language preference

    Returns:
        Localized message
    """
    messages = ROUTING_MESSAGES.get(key, {"en": key, "ar": key})

    if language == Language.ARABIC:
        return messages.get("ar", messages.get("en", key))
    elif language == Language.ENGLISH:
        return messages.get("en", messages.get("ar", key))
    else:
        return f"{messages.get('en', key)} | {messages.get('ar', key)}"
