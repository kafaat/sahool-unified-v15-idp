"""Tests for notification utilities in Supply Chain Service."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")

import pytest
from datetime import datetime, timedelta
from uuid import uuid4


@pytest.fixture
def notification_service():
    from src.utils.notifications import NotificationService

    return NotificationService()


class TestNotificationServiceInit:
    """Tests for NotificationService initialization."""

    def test_default_settings(self, notification_service):
        assert notification_service.sms_enabled is True
        assert notification_service.push_enabled is True
        assert notification_service.email_enabled is True

    def test_notification_url(self, notification_service):
        assert "notification-service" in notification_service.notification_url


class TestSendOrderConfirmation:
    """Tests for send_order_confirmation."""

    @pytest.mark.asyncio
    async def test_with_all_channels(self, notification_service):
        result = await notification_service.send_order_confirmation(
            farmer_id=uuid4(),
            order_id=uuid4(),
            order_total=350.0,
            estimated_delivery=datetime.utcnow() + timedelta(days=3),
            phone="+966123456789",
            email="farmer@test.com",
        )
        assert result["sms"] is not None
        assert result["sms"]["status"] == "sent"
        assert result["push"] is not None
        assert result["push"]["status"] == "sent"
        assert result["email"] is not None
        assert result["email"]["status"] == "sent"

    @pytest.mark.asyncio
    async def test_without_phone_no_sms(self, notification_service):
        result = await notification_service.send_order_confirmation(
            farmer_id=uuid4(),
            order_id=uuid4(),
            order_total=350.0,
            estimated_delivery=datetime.utcnow() + timedelta(days=3),
        )
        assert result["sms"] is None
        assert result["push"] is not None

    @pytest.mark.asyncio
    async def test_without_email_no_email(self, notification_service):
        result = await notification_service.send_order_confirmation(
            farmer_id=uuid4(),
            order_id=uuid4(),
            order_total=100.0,
            estimated_delivery=datetime.utcnow() + timedelta(days=2),
            phone="+966111111111",
        )
        assert result["email"] is None

    @pytest.mark.asyncio
    async def test_sms_disabled(self):
        from src.utils.notifications import NotificationService
        from unittest.mock import patch

        with patch.object(NotificationService, "__init__", lambda self: None):
            ns = NotificationService()
            ns.notification_url = "http://test"
            ns.sms_enabled = False
            ns.push_enabled = True
            ns.email_enabled = True

            result = await ns.send_order_confirmation(
                farmer_id=uuid4(),
                order_id=uuid4(),
                order_total=100.0,
                estimated_delivery=datetime.utcnow(),
                phone="+966111111111",
            )
            assert result["sms"] is None


class TestSendDeliveryUpdate:
    """Tests for send_delivery_update."""

    @pytest.mark.asyncio
    async def test_with_phone_and_eta(self, notification_service):
        result = await notification_service.send_delivery_update(
            farmer_id=uuid4(),
            order_id=uuid4(),
            status="shipped",
            status_ar="تم الشحن",
            eta=datetime.utcnow() + timedelta(hours=3),
            phone="+966123456789",
        )
        assert result["sms"] is not None
        assert result["push"] is not None

    @pytest.mark.asyncio
    async def test_without_eta(self, notification_service):
        result = await notification_service.send_delivery_update(
            farmer_id=uuid4(),
            order_id=uuid4(),
            status="processing",
            status_ar="قيد المعالجة",
        )
        assert result["push"] is not None
        assert result["sms"] is None  # no phone

    @pytest.mark.asyncio
    async def test_without_phone(self, notification_service):
        result = await notification_service.send_delivery_update(
            farmer_id=uuid4(),
            order_id=uuid4(),
            status="shipped",
            status_ar="تم الشحن",
        )
        assert result["sms"] is None


class TestSendOrderShipped:
    """Tests for send_order_shipped."""

    @pytest.mark.asyncio
    async def test_with_phone(self, notification_service):
        result = await notification_service.send_order_shipped(
            farmer_id=uuid4(),
            order_id=uuid4(),
            tracking_url="https://track.test/123",
            phone="+966111111111",
        )
        assert result["sms"] is not None
        assert result["push"] is not None

    @pytest.mark.asyncio
    async def test_without_phone(self, notification_service):
        result = await notification_service.send_order_shipped(
            farmer_id=uuid4(),
            order_id=uuid4(),
            tracking_url="https://track.test/123",
        )
        assert result["sms"] is None
        assert result["push"] is not None


class TestSendOrderDelivered:
    """Tests for send_order_delivered."""

    @pytest.mark.asyncio
    async def test_with_phone(self, notification_service):
        result = await notification_service.send_order_delivered(
            farmer_id=uuid4(),
            order_id=uuid4(),
            phone="+966111111111",
        )
        assert result["sms"] is not None
        assert result["push"] is not None

    @pytest.mark.asyncio
    async def test_without_phone(self, notification_service):
        result = await notification_service.send_order_delivered(
            farmer_id=uuid4(),
            order_id=uuid4(),
        )
        assert result["sms"] is None
        assert result["push"] is not None


class TestSendPriceAlert:
    """Tests for send_price_alert."""

    @pytest.mark.asyncio
    async def test_price_alert(self, notification_service):
        result = await notification_service.send_price_alert(
            farmer_id=uuid4(),
            product_name="Urea 46%",
            product_name_ar="يوريا 46%",
            old_price=100.0,
            new_price=80.0,
            supplier_name="Test Supplier",
        )
        assert result is not None
        assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_price_alert_push_disabled(self):
        from src.utils.notifications import NotificationService
        from unittest.mock import patch

        with patch.object(NotificationService, "__init__", lambda self: None):
            ns = NotificationService()
            ns.notification_url = "http://test"
            ns.sms_enabled = True
            ns.push_enabled = False
            ns.email_enabled = True

            result = await ns.send_price_alert(
                farmer_id=uuid4(),
                product_name="Urea",
                product_name_ar="يوريا",
                old_price=100.0,
                new_price=80.0,
                supplier_name="Test",
            )
            assert result == {"push": None}


class TestPrivateMethods:
    """Tests for private notification methods."""

    @pytest.mark.asyncio
    async def test_send_sms(self, notification_service):
        result = await notification_service._send_sms("+966123456789", "Test message")
        assert result["status"] == "sent"
        assert "message_id" in result
        assert result["phone"] == "+966123456789"

    @pytest.mark.asyncio
    async def test_send_push(self, notification_service):
        farmer_id = uuid4()
        result = await notification_service._send_push(farmer_id, "Title", "Body", {"key": "value"})
        assert result["status"] == "sent"
        assert result["farmer_id"] == str(farmer_id)
        assert "notification_id" in result

    @pytest.mark.asyncio
    async def test_send_email(self, notification_service):
        result = await notification_service._send_email("test@example.com", "Subject", "Body EN", "Body AR")
        assert result["status"] == "sent"
        assert result["email"] == "test@example.com"
        assert "message_id" in result
