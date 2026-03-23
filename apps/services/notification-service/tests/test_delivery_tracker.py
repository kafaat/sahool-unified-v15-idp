"""
Tests for src/delivery_tracker.py - Delivery Tracker

Covers:
- DeliveryStatus and DeliveryEventType enums
- DeliveryEvent dataclass
- DeliveryTracker (start, stop, register, callbacks)
"""

import pytest
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

try:
    from src.delivery_tracker import (
        DeliveryEvent,
        DeliveryEventType,
        DeliveryStatus,
        DeliveryTracker,
        get_delivery_tracker,
    )
except (ImportError, Exception):
    pytest.skip("notification-service dependencies not available", allow_module_level=True)


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class TestDeliveryStatus:
    def test_all_statuses(self):
        assert DeliveryStatus.QUEUED == "queued"
        assert DeliveryStatus.SENDING == "sending"
        assert DeliveryStatus.SENT == "sent"
        assert DeliveryStatus.DELIVERED == "delivered"
        assert DeliveryStatus.READ == "read"
        assert DeliveryStatus.FAILED == "failed"
        assert DeliveryStatus.BOUNCED == "bounced"
        assert DeliveryStatus.EXPIRED == "expired"


class TestDeliveryEventType:
    def test_all_event_types(self):
        assert DeliveryEventType.STATUS_CHANGE == "status_change"
        assert DeliveryEventType.RETRY_SCHEDULED == "retry_scheduled"
        assert DeliveryEventType.DELIVERY_CONFIRMED == "delivery_confirmed"
        assert DeliveryEventType.READ_RECEIPT == "read_receipt"
        assert DeliveryEventType.FAILURE == "failure"
        assert DeliveryEventType.BOUNCE == "bounce"


# ─────────────────────────────────────────────────────────────────────────────
# DeliveryEvent
# ─────────────────────────────────────────────────────────────────────────────


class TestDeliveryEvent:
    def test_create_event(self):
        now = datetime.now(UTC)
        event = DeliveryEvent(
            notification_id="n-1",
            event_type=DeliveryEventType.STATUS_CHANGE,
            status=DeliveryStatus.SENT,
            channel="push",
            timestamp=now,
        )
        assert event.notification_id == "n-1"
        assert event.details is None
        assert event.provider_response is None

    def test_create_event_with_details(self):
        event = DeliveryEvent(
            notification_id="n-2",
            event_type=DeliveryEventType.FAILURE,
            status=DeliveryStatus.FAILED,
            channel="sms",
            timestamp=datetime.now(UTC),
            details={"error": "Invalid phone number"},
            provider_response={"code": 400, "message": "Invalid"},
        )
        assert event.details["error"] == "Invalid phone number"
        assert event.provider_response["code"] == 400

    def test_to_dict(self):
        now = datetime.now(UTC)
        event = DeliveryEvent(
            notification_id="n-3",
            event_type=DeliveryEventType.DELIVERY_CONFIRMED,
            status=DeliveryStatus.DELIVERED,
            channel="email",
            timestamp=now,
            details={"provider": "sendgrid"},
            provider_response={"id": "msg-123"},
        )
        data = event.to_dict()
        assert data["notification_id"] == "n-3"
        assert data["event_type"] == "delivery_confirmed"
        assert data["status"] == "delivered"
        assert data["channel"] == "email"
        assert data["timestamp"] == now.isoformat()
        assert data["details"]["provider"] == "sendgrid"

    def test_to_dict_without_optional_fields(self):
        event = DeliveryEvent(
            notification_id="n-4",
            event_type=DeliveryEventType.READ_RECEIPT,
            status=DeliveryStatus.READ,
            channel="in_app",
            timestamp=datetime.now(UTC),
        )
        data = event.to_dict()
        assert data["details"] is None
        assert data["provider_response"] is None


# ─────────────────────────────────────────────────────────────────────────────
# DeliveryTracker
# ─────────────────────────────────────────────────────────────────────────────


class TestDeliveryTracker:
    def test_init(self):
        tracker = DeliveryTracker()
        assert tracker._callbacks == []
        assert tracker._webhook_urls == []
        assert tracker._http_client is None

    @pytest.mark.asyncio
    async def test_start(self):
        tracker = DeliveryTracker()
        await tracker.start()
        assert tracker._http_client is not None
        await tracker.stop()

    @pytest.mark.asyncio
    async def test_stop(self):
        tracker = DeliveryTracker()
        await tracker.start()
        assert tracker._http_client is not None
        await tracker.stop()
        assert tracker._http_client is None

    @pytest.mark.asyncio
    async def test_stop_without_start(self):
        tracker = DeliveryTracker()
        await tracker.stop()
        assert tracker._http_client is None

    def test_register_callback(self):
        tracker = DeliveryTracker()

        async def my_callback(event):
            pass

        tracker.register_callback(my_callback)
        assert len(tracker._callbacks) == 1
        assert tracker._callbacks[0] is my_callback

    def test_register_webhook(self):
        tracker = DeliveryTracker()
        tracker.register_webhook("https://example.com/webhook")
        assert len(tracker._webhook_urls) == 1
        assert tracker._webhook_urls[0] == "https://example.com/webhook"

    def test_register_multiple_callbacks(self):
        tracker = DeliveryTracker()

        async def cb1(event):
            pass

        async def cb2(event):
            pass

        tracker.register_callback(cb1)
        tracker.register_callback(cb2)
        assert len(tracker._callbacks) == 2

    def test_register_multiple_webhooks(self):
        tracker = DeliveryTracker()
        tracker.register_webhook("https://example1.com")
        tracker.register_webhook("https://example2.com")
        assert len(tracker._webhook_urls) == 2


# ─────────────────────────────────────────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────────────────────────────────────────


class TestGetDeliveryTracker:
    def test_returns_singleton(self):
        import src.delivery_tracker as mod

        old = mod._delivery_tracker
        mod._delivery_tracker = None

        tracker1 = get_delivery_tracker()
        tracker2 = get_delivery_tracker()
        assert tracker1 is tracker2

        mod._delivery_tracker = old
