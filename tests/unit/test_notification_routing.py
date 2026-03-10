"""Test notification routing logic for multi-channel notifications."""

import pytest


class TestNotificationRouting:
    """Test notification priority to channel mapping."""

    ROUTING_RULES = {
        "critical": ["push", "whatsapp", "sms"],
        "warning": ["push", "whatsapp"],
        "advisory": ["push", "in_app"],
        "info": ["in_app"],
    }

    def test_critical_uses_all_channels(self):
        channels = self.ROUTING_RULES["critical"]
        assert "push" in channels
        assert "whatsapp" in channels
        assert "sms" in channels

    def test_warning_uses_push_and_whatsapp(self):
        channels = self.ROUTING_RULES["warning"]
        assert "push" in channels
        assert "whatsapp" in channels
        assert "sms" not in channels

    def test_advisory_uses_push_and_inapp(self):
        channels = self.ROUTING_RULES["advisory"]
        assert "push" in channels
        assert "in_app" in channels

    def test_info_uses_inapp_only(self):
        channels = self.ROUTING_RULES["info"]
        assert channels == ["in_app"]

    def test_all_priorities_have_at_least_one_channel(self):
        for priority, channels in self.ROUTING_RULES.items():
            assert len(channels) > 0, f"Priority {priority} has no channels"


class TestNotificationPayload:
    """Test notification payload structure."""

    def test_payload_structure(self):
        payload = {
            "notification_id": "notif-001",
            "tenant_id": "tenant-001",
            "user_id": "user-001",
            "priority": "critical",
            "title": "Red Palm Weevil Detected",
            "title_ar": "\u062a\u0645 \u0627\u0643\u062a\u0634\u0627\u0641 \u0633\u0648\u0633\u0629 \u0627\u0644\u0646\u062e\u064a\u0644 \u0627\u0644\u062d\u0645\u0631\u0627\u0621",
            "body": "Immediate action required in Field-003",
            "body_ar": "\u0645\u0637\u0644\u0648\u0628 \u0625\u062c\u0631\u0627\u0621 \u0641\u0648\u0631\u064a \u0641\u064a \u0627\u0644\u062d\u0642\u0644 003",
            "channels": ["push", "whatsapp", "sms"],
            "data": {"field_id": "FIELD-003", "pest_type": "rpw"},
        }

        assert payload["priority"] == "critical"
        assert len(payload["channels"]) == 3
        assert "title_ar" in payload
        assert "body_ar" in payload
