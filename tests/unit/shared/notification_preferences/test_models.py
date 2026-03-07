"""
Tests for notification_preferences models
اختبارات نماذج تفضيلات الإشعارات
"""

from __future__ import annotations

from datetime import UTC, datetime, time, timedelta

import pytest

from shared.notification_preferences.models import (
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


class TestEnums:
    def test_notification_channel_values(self):
        assert NotificationChannel.EMAIL == "email"
        assert NotificationChannel.SMS == "sms"
        assert NotificationChannel.PUSH == "push"
        assert NotificationChannel.WHATSAPP == "whatsapp"
        assert NotificationChannel.IN_APP == "in_app"

    def test_alert_type_values(self):
        assert AlertType.WEATHER_FROST == "weather_frost"
        assert AlertType.PEST_OUTBREAK == "pest_outbreak"
        assert AlertType.IRRIGATION_REMINDER == "irrigation_reminder"
        assert AlertType.MARKET_PRICE == "market_price"
        assert AlertType.EMERGENCY == "emergency"

    def test_alert_urgency_values(self):
        assert AlertUrgency.CRITICAL == "critical"
        assert AlertUrgency.LOW == "low"
        assert AlertUrgency.INFORMATIONAL == "info"

    def test_language_values(self):
        assert Language.ARABIC == "ar"
        assert Language.ENGLISH == "en"
        assert Language.BOTH == "both"

    def test_day_of_week_values(self):
        assert DayOfWeek.MONDAY == "monday"
        assert DayOfWeek.FRIDAY == "friday"


class TestQuietHours:
    def test_defaults(self):
        qh = QuietHours()
        assert qh.enabled is True
        assert qh.start_time == time(22, 0)
        assert qh.end_time == time(6, 0)
        assert qh.bypass_urgency == AlertUrgency.CRITICAL

    def test_to_dict_and_from_dict(self):
        qh = QuietHours(
            enabled=True,
            start_time=time(23, 0),
            end_time=time(7, 0),
            timezone="Asia/Riyadh",
            days=[DayOfWeek.FRIDAY, DayOfWeek.SATURDAY],
        )
        d = qh.to_dict()
        restored = QuietHours.from_dict(d)
        assert restored.enabled is True
        assert restored.start_time == time(23, 0)
        assert restored.end_time == time(7, 0)
        assert DayOfWeek.FRIDAY in restored.days


class TestChannelConfig:
    def test_defaults(self):
        config = ChannelConfig(channel=NotificationChannel.EMAIL)
        assert config.enabled is True
        assert config.verified is False
        assert config.address is None

    def test_to_dict_and_from_dict(self):
        config = ChannelConfig(
            channel=NotificationChannel.SMS,
            enabled=True,
            address="+966501234567",
            verified=True,
            verified_at=datetime(2025, 1, 1, tzinfo=UTC),
        )
        d = config.to_dict()
        restored = ChannelConfig.from_dict(d)
        assert restored.channel == NotificationChannel.SMS
        assert restored.address == "+966501234567"
        assert restored.verified is True


class TestAlertTypePreference:
    def test_defaults(self):
        pref = AlertTypePreference(alert_type=AlertType.IRRIGATION_REMINDER)
        assert pref.enabled is True
        assert pref.min_urgency == AlertUrgency.LOW

    def test_to_dict_and_from_dict(self):
        pref = AlertTypePreference(
            alert_type=AlertType.PEST_OUTBREAK,
            enabled=True,
            channels=[NotificationChannel.PUSH, NotificationChannel.SMS],
            min_urgency=AlertUrgency.MEDIUM,
        )
        d = pref.to_dict()
        restored = AlertTypePreference.from_dict(d)
        assert restored.alert_type == AlertType.PEST_OUTBREAK
        assert NotificationChannel.PUSH in restored.channels
        assert restored.min_urgency == AlertUrgency.MEDIUM


class TestTimeBasedRule:
    def test_defaults(self):
        rule = TimeBasedRule(name="Test", name_ar="اختبار")
        assert rule.enabled is True
        assert rule.priority == 0

    def test_to_dict_and_from_dict(self):
        rule = TimeBasedRule(
            name="No SMS at night",
            name_ar="لا رسائل نصية ليلاً",
            start_time=time(22, 0),
            end_time=time(6, 0),
            channels=[NotificationChannel.SMS],
            action="channel_fallback",
            fallback_channel=NotificationChannel.PUSH,
            priority=100,
        )
        d = rule.to_dict()
        restored = TimeBasedRule.from_dict(d)
        assert restored.name == "No SMS at night"
        assert restored.fallback_channel == NotificationChannel.PUSH
        assert restored.priority == 100


class TestUrgencyOverride:
    def test_to_dict_and_from_dict(self):
        override = UrgencyOverride(
            urgency=AlertUrgency.CRITICAL,
            force_channels=[NotificationChannel.SMS, NotificationChannel.PUSH],
            bypass_quiet_hours=True,
            bypass_time_rules=True,
        )
        d = override.to_dict()
        restored = UrgencyOverride.from_dict(d)
        assert restored.urgency == AlertUrgency.CRITICAL
        assert restored.bypass_quiet_hours is True
        assert NotificationChannel.SMS in restored.force_channels


class TestUserNotificationPreferences:
    def test_create_default(self):
        prefs = create_default_preferences("user1", "tenant1")
        assert prefs.user_id == "user1"
        assert prefs.tenant_id == "tenant1"
        assert prefs.notifications_enabled is True
        assert prefs.language == Language.ARABIC
        assert len(prefs.default_channels) >= 2

    def test_create_minimal(self):
        prefs = create_minimal_preferences("user2", "tenant1")
        assert prefs.user_id == "user2"
        assert prefs.notifications_enabled is True
        assert len(prefs.default_channels) >= 1

    def test_get_channel_config_missing(self):
        prefs = create_default_preferences("user1")
        # Default prefs have no channel_configs
        config = prefs.get_channel_config(NotificationChannel.WHATSAPP)
        assert config is None

    def test_get_alert_preference_exists(self):
        prefs = create_minimal_preferences("user1")
        # Minimal prefs have EMERGENCY alert preference
        pref = prefs.get_alert_preference(AlertType.EMERGENCY)
        assert pref is not None
        assert pref.enabled is True

    def test_get_alert_preference_missing(self):
        prefs = create_minimal_preferences("user1")
        pref = prefs.get_alert_preference(AlertType.MARKET_PRICE)
        assert pref is None

    def test_get_urgency_override(self):
        prefs = create_default_preferences("user1")
        override = prefs.get_urgency_override(AlertUrgency.CRITICAL)
        assert override is not None
        assert override.bypass_quiet_hours is True

    def test_to_dict_and_from_dict(self):
        prefs = create_default_preferences("user1", "tenant1")
        d = prefs.to_dict()
        assert d["user_id"] == "user1"
        assert d["tenant_id"] == "tenant1"

        restored = UserNotificationPreferences.from_dict(d)
        assert restored.user_id == "user1"
        assert restored.tenant_id == "tenant1"
        assert restored.language == prefs.language

    def test_version_starts_at_one(self):
        prefs = create_default_preferences("user1")
        assert prefs.version == 1


class TestNotificationRequest:
    def test_to_dict(self):
        req = NotificationRequest(
            alert_type=AlertType.IRRIGATION_REMINDER,
            urgency=AlertUrgency.HIGH,
            title="Water Alert",
            title_ar="تنبيه مياه",
            body="Irrigation needed",
            body_ar="يلزم الري",
        )
        d = req.to_dict()
        assert d["alert_type"] == "irrigation_reminder"
        assert d["urgency"] == "high"


class TestRoutingDecision:
    def test_to_dict(self):
        decision = RoutingDecision(
            request_id="n1",
            channels=[NotificationChannel.PUSH],
            language=Language.ARABIC,
            should_deliver=True,
        )
        d = decision.to_dict()
        assert d["should_deliver"] is True
        assert "push" in d["channels"]
