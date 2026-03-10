"""Tests for multi-channel notification routing."""

import pytest
from shared.notification_routing import (
    NotificationRouter,
    NotificationPriority,
    NotificationChannel,
    ROUTING_RULES,
    ALERT_TYPES,
    CHANNEL_SERVICES,
)


class TestRoutingRules:
    def test_critical_has_three_channels(self):
        channels = ROUTING_RULES[NotificationPriority.CRITICAL]
        assert len(channels) == 3
        assert NotificationChannel.PUSH in channels
        assert NotificationChannel.WHATSAPP in channels
        assert NotificationChannel.SMS in channels

    def test_warning_has_two_channels(self):
        channels = ROUTING_RULES[NotificationPriority.WARNING]
        assert len(channels) == 2

    def test_advisory_has_push_and_inapp(self):
        channels = ROUTING_RULES[NotificationPriority.ADVISORY]
        assert NotificationChannel.PUSH in channels
        assert NotificationChannel.IN_APP in channels

    def test_info_has_inapp_only(self):
        channels = ROUTING_RULES[NotificationPriority.INFO]
        assert channels == [NotificationChannel.IN_APP]


class TestAlertTypes:
    def test_rpw_is_critical(self):
        assert ALERT_TYPES["rpw_detected"]["priority"] == NotificationPriority.CRITICAL

    def test_frost_is_critical(self):
        assert ALERT_TYPES["frost_warning"]["priority"] == NotificationPriority.CRITICAL

    def test_pest_threshold_is_warning(self):
        assert ALERT_TYPES["pest_threshold"]["priority"] == NotificationPriority.WARNING

    def test_irrigation_is_advisory(self):
        assert ALERT_TYPES["irrigation_advice"]["priority"] == NotificationPriority.ADVISORY

    def test_market_is_info(self):
        assert ALERT_TYPES["market_update"]["priority"] == NotificationPriority.INFO

    def test_all_alerts_have_arabic(self):
        for name, config in ALERT_TYPES.items():
            assert "title_ar" in config, f"{name} missing title_ar"


class TestNotificationRouter:
    def setup_method(self):
        self.router = NotificationRouter()

    def test_get_channels_critical(self):
        channels = self.router.get_channels(NotificationPriority.CRITICAL)
        assert len(channels) == 3

    def test_build_notification(self):
        payload = self.router.build_notification(
            notification_id="test-001",
            tenant_id="tenant-001",
            user_id="user-001",
            alert_type="rpw_detected",
            body="RPW detected in Field-003",
            body_ar="سوسة النخيل في الحقل 003",
        )
        assert payload.priority == NotificationPriority.CRITICAL
        assert len(payload.channels) == 3
        assert payload.title_ar == "تم اكتشاف سوسة النخيل الحمراء"

    def test_build_notification_unknown_type(self):
        payload = self.router.build_notification(
            notification_id="test-002",
            tenant_id="tenant-001",
            user_id="user-001",
            alert_type="unknown_type",
        )
        assert payload.priority == NotificationPriority.INFO

    def test_payload_to_dict(self):
        payload = self.router.build_notification(
            notification_id="test-003",
            tenant_id="tenant-001",
            user_id="user-001",
            alert_type="frost_warning",
        )
        d = payload.to_dict()
        assert d["priority"] == "critical"
        assert "push" in d["channels"]

    @pytest.mark.asyncio
    async def test_route_notification(self):
        payload = self.router.build_notification(
            notification_id="test-004",
            tenant_id="tenant-001",
            user_id="user-001",
            alert_type="market_update",
        )
        results = await self.router.route_notification(payload)
        assert "in_app" in results
        assert results["in_app"]["status"] == "routed"


class TestChannelServices:
    def test_all_channels_have_service(self):
        for channel in NotificationChannel:
            assert channel in CHANNEL_SERVICES

    def test_whatsapp_points_to_correct_service(self):
        config = CHANNEL_SERVICES[NotificationChannel.WHATSAPP]
        assert config["service"] == "whatsapp-bot-service"
        assert config["port"] == 8240

    def test_sms_points_to_ussd(self):
        config = CHANNEL_SERVICES[NotificationChannel.SMS]
        assert config["service"] == "ussd-gateway"
        assert config["port"] == 8183
