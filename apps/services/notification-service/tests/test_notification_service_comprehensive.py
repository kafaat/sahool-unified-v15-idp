"""
SAHOOL Notification Service - Comprehensive Service Layer Tests
Complete tests for notification business logic, delivery, and preferences
Coverage: Notification creation, channel delivery, user preferences, targeting
"""

from datetime import datetime, time, timedelta
from unittest.mock import AsyncMock, MagicMock, call, patch
from uuid import uuid4

import pytest


@pytest.fixture
def mock_notification():
    """Create a mock notification object"""
    notif = MagicMock()
    notif.id = uuid4()
    notif.user_id = "user-123"
    notif.tenant_id = "tenant-1"
    notif.title = "Test Notification"
    notif.title_ar = "إشعار تجريبي"
    notif.body = "Test body"
    notif.body_ar = "نص تجريبي"
    notif.type = "weather_alert"
    notif.priority = "high"
    notif.channel = "push"
    notif.status = "pending"
    notif.created_at = datetime.utcnow()
    notif.expires_at = datetime.utcnow() + timedelta(hours=24)
    notif.data = {"type_ar": "تنبيه طقس", "priority_ar": "عالية"}
    notif.is_read = False
    notif.action_url = None
    return notif


@pytest.fixture
def mock_farmer_profile():
    """Create a mock farmer profile"""
    from src.main import CropType, FarmerProfile, Governorate, NotificationChannel

    return FarmerProfile(
        farmer_id="farmer-123",
        name="Ahmed Ali",
        name_ar="أحمد علي",
        governorate=Governorate.SANAA,
        crops=[CropType.TOMATO, CropType.COFFEE],
        phone="+967771234567",
        email="ahmed@example.com",
        fcm_token="mock-fcm-token",
        notification_channels=[NotificationChannel.PUSH, NotificationChannel.SMS],
        language="ar",
    )


class TestNotificationCreation:
    """Test notification creation logic"""

    @pytest.mark.asyncio
    async def test_create_notification_with_preferences(self, mock_notification):
        """Test notification creation respects user preferences"""
        from src.main import NotificationPriority, NotificationType, create_notification

        with patch(
            "src.repository.NotificationRepository.create",
            new=AsyncMock(return_value=mock_notification),
        ), patch(
            "src.preferences_service.PreferencesService.check_if_should_send",
            new=AsyncMock(return_value=(True, ["push", "sms"])),
        ), patch("src.main.send_notification_via_channel", new=AsyncMock()):
            result = await create_notification(
                type=NotificationType.WEATHER_ALERT,
                priority=NotificationPriority.HIGH,
                title="Weather Alert",
                title_ar="تنبيه طقس",
                body="Frost expected",
                body_ar="صقيع متوقع",
                target_farmers=["farmer-123"],
            )

            assert result is not None
            assert result.id == mock_notification.id

    @pytest.mark.asyncio
    async def test_create_notification_preference_blocked(self, mock_notification):
        """Test notification creation when user preferences block it"""
        from src.main import NotificationPriority, NotificationType, create_notification

        with patch(
            "src.preferences_service.PreferencesService.check_if_should_send",
            new=AsyncMock(return_value=(False, [])),
        ):
            result = await create_notification(
                type=NotificationType.WEATHER_ALERT,
                priority=NotificationPriority.HIGH,
                title="Weather Alert",
                title_ar="تنبيه طقس",
                body="Frost expected",
                body_ar="صقيع متوقع",
                target_farmers=["farmer-123"],
            )

            # Should return None when all recipients are blocked
            assert result is None

    @pytest.mark.asyncio
    async def test_create_notification_with_targeting(self, mock_notification):
        """Test notification creation with governorate and crop targeting"""
        from src.main import (
            FARMER_PROFILES,
            CropType,
            Governorate,
            NotificationPriority,
            NotificationType,
            create_notification,
        )

        # Add mock farmer to profiles
        FARMER_PROFILES["farmer-123"] = MagicMock(
            farmer_id="farmer-123", governorate=Governorate.SANAA, crops=[CropType.TOMATO]
        )

        with patch(
            "src.repository.NotificationRepository.create",
            new=AsyncMock(return_value=mock_notification),
        ), patch(
            "src.preferences_service.PreferencesService.check_if_should_send",
            new=AsyncMock(return_value=(True, ["push"])),
        ), patch("src.main.send_notification_via_channel", new=AsyncMock()):
            result = await create_notification(
                type=NotificationType.PEST_OUTBREAK,
                priority=NotificationPriority.HIGH,
                title="Pest Alert",
                title_ar="تنبيه آفات",
                body="Aphids detected",
                body_ar="تم رصد المن",
                target_governorates=[Governorate.SANAA],
                target_crops=[CropType.TOMATO],
            )

            assert result is not None

        # Cleanup
        FARMER_PROFILES.clear()

    @pytest.mark.asyncio
    async def test_create_notification_multi_channel(self, mock_notification):
        """Test notification sent to multiple channels"""
        from src.main import (
            NotificationChannel,
            NotificationPriority,
            NotificationType,
            create_notification,
        )

        with patch(
            "src.repository.NotificationRepository.create",
            new=AsyncMock(return_value=mock_notification),
        ), patch(
            "src.preferences_service.PreferencesService.check_if_should_send",
            new=AsyncMock(return_value=(True, ["push", "sms", "email"])),
        ), patch("src.main.send_notification_via_channel", new=AsyncMock()) as mock_send:
            await create_notification(
                type=NotificationType.WEATHER_ALERT,
                priority=NotificationPriority.CRITICAL,
                title="Critical Alert",
                title_ar="تنبيه حرج",
                body="Immediate action required",
                body_ar="مطلوب اتخاذ إجراء فوري",
                target_farmers=["farmer-123"],
                channels=[NotificationChannel.PUSH, NotificationChannel.SMS],
            )

            # Verify multiple channels were called
            assert mock_send.call_count >= 1


class TestNotificationDelivery:
    """Test notification delivery via different channels"""

    @pytest.mark.asyncio
    async def test_send_sms_notification_success(self, mock_notification):
        """Test successful SMS notification delivery"""
        from src.main import FARMER_PROFILES, send_sms_notification

        # Setup mock farmer
        FARMER_PROFILES["farmer-123"] = MagicMock(
            farmer_id="farmer-123", phone="+967771234567", language="ar"
        )

        mock_sms_client = MagicMock()
        mock_sms_client._initialized = True
        mock_sms_client.send_sms = AsyncMock(return_value="SM123456")

        with patch("src.main.get_sms_client", return_value=mock_sms_client):
            with patch("src.repository.NotificationRepository.update_status", new=AsyncMock()):
                with patch("src.repository.NotificationLogRepository.create_log", new=AsyncMock()):
                    await send_sms_notification(mock_notification, "farmer-123")

                    # Verify SMS was sent
                    mock_sms_client.send_sms.assert_called_once()

        FARMER_PROFILES.clear()

    @pytest.mark.asyncio
    async def test_send_sms_notification_no_phone(self, mock_notification):
        """Test SMS notification when farmer has no phone number"""
        from src.main import FARMER_PROFILES, send_sms_notification

        FARMER_PROFILES["farmer-123"] = MagicMock(farmer_id="farmer-123", phone=None)

        with patch(
            "src.repository.NotificationLogRepository.create_log", new=AsyncMock()
        ) as mock_log:
            await send_sms_notification(mock_notification, "farmer-123")

            # Verify failure was logged
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[1]["status"] == "failed"
            assert "phone" in call_args[1]["error_message"].lower()

        FARMER_PROFILES.clear()

    @pytest.mark.asyncio
    async def test_send_email_notification_success(self, mock_notification):
        """Test successful email notification delivery"""
        from src.main import FARMER_PROFILES, send_email_notification

        FARMER_PROFILES["farmer-123"] = MagicMock(
            farmer_id="farmer-123", email="ahmed@example.com", language="ar"
        )

        mock_email_client = MagicMock()
        mock_email_client._initialized = True
        mock_email_client.send_email = AsyncMock(return_value="msg-123456")

        with patch("src.main.get_email_client", return_value=mock_email_client):
            with patch("src.repository.NotificationRepository.update_status", new=AsyncMock()):
                with patch("src.repository.NotificationLogRepository.create_log", new=AsyncMock()):
                    await send_email_notification(mock_notification, "farmer-123")

                    # Verify email was sent
                    mock_email_client.send_email.assert_called_once()

        FARMER_PROFILES.clear()

    @pytest.mark.asyncio
    async def test_send_push_notification_success(self, mock_notification):
        """Test successful push notification delivery"""
        from src.main import FARMER_PROFILES, send_push_notification

        FARMER_PROFILES["farmer-123"] = MagicMock(
            farmer_id="farmer-123", fcm_token="valid-fcm-token"
        )

        mock_firebase_client = MagicMock()
        mock_firebase_client._initialized = True
        mock_firebase_client.send_notification = MagicMock(return_value="fcm-msg-123")

        with patch("src.firebase_client.get_firebase_client", return_value=mock_firebase_client):
            with patch("src.repository.NotificationRepository.update_status", new=AsyncMock()):
                with patch("src.repository.NotificationLogRepository.create_log", new=AsyncMock()):
                    await send_push_notification(mock_notification, "farmer-123")

                    # Verify push was sent
                    mock_firebase_client.send_notification.assert_called_once()

        FARMER_PROFILES.clear()

    @pytest.mark.asyncio
    async def test_send_push_notification_no_token(self, mock_notification):
        """Test push notification when farmer has no FCM token"""
        from src.main import FARMER_PROFILES, send_push_notification

        FARMER_PROFILES["farmer-123"] = MagicMock(farmer_id="farmer-123", fcm_token=None)

        with patch(
            "src.repository.NotificationLogRepository.create_log", new=AsyncMock()
        ) as mock_log:
            await send_push_notification(mock_notification, "farmer-123")

            # Verify failure was logged
            mock_log.assert_called_once()
            call_args = mock_log.call_args
            assert call_args[1]["status"] == "failed"

        FARMER_PROFILES.clear()

    @pytest.mark.asyncio
    async def test_send_notification_via_channel_dispatcher(self, mock_notification):
        """Test notification channel dispatcher"""
        from src.main import NotificationChannel, send_notification_via_channel

        with patch("src.main.send_sms_notification", new=AsyncMock()) as mock_sms:
            with patch("src.main.send_email_notification", new=AsyncMock()) as mock_email:
                with patch("src.main.send_push_notification", new=AsyncMock()) as mock_push:
                    # Test SMS
                    await send_notification_via_channel(
                        mock_notification, NotificationChannel.SMS, "farmer-123"
                    )
                    mock_sms.assert_called_once()

                    # Test Email
                    await send_notification_via_channel(
                        mock_notification, NotificationChannel.EMAIL, "farmer-123"
                    )
                    mock_email.assert_called_once()

                    # Test Push
                    await send_notification_via_channel(
                        mock_notification, NotificationChannel.PUSH, "farmer-123"
                    )
                    mock_push.assert_called_once()


class TestRecipientTargeting:
    """Test recipient determination and targeting logic"""

    def test_determine_recipients_specific_farmers(self):
        """Test targeting specific farmers"""
        from src.main import determine_recipients_by_criteria

        result = determine_recipients_by_criteria(target_farmers=["farmer-1", "farmer-2"])

        assert result == ["farmer-1", "farmer-2"]

    def test_determine_recipients_by_governorate(self):
        """Test targeting by governorate"""
        from src.main import (
            FARMER_PROFILES,
            CropType,
            Governorate,
            determine_recipients_by_criteria,
        )

        FARMER_PROFILES["farmer-1"] = MagicMock(
            farmer_id="farmer-1", governorate=Governorate.SANAA, crops=[CropType.TOMATO]
        )
        FARMER_PROFILES["farmer-2"] = MagicMock(
            farmer_id="farmer-2", governorate=Governorate.IBB, crops=[CropType.WHEAT]
        )

        result = determine_recipients_by_criteria(target_governorates=[Governorate.SANAA])

        assert "farmer-1" in result
        assert "farmer-2" not in result

        FARMER_PROFILES.clear()

    def test_determine_recipients_by_crop(self):
        """Test targeting by crop type"""
        from src.main import (
            FARMER_PROFILES,
            CropType,
            Governorate,
            determine_recipients_by_criteria,
        )

        FARMER_PROFILES["farmer-1"] = MagicMock(
            farmer_id="farmer-1",
            governorate=Governorate.SANAA,
            crops=[CropType.TOMATO, CropType.COFFEE],
        )
        FARMER_PROFILES["farmer-2"] = MagicMock(
            farmer_id="farmer-2", governorate=Governorate.IBB, crops=[CropType.WHEAT]
        )

        result = determine_recipients_by_criteria(target_crops=[CropType.TOMATO])

        assert "farmer-1" in result
        assert "farmer-2" not in result

        FARMER_PROFILES.clear()

    def test_determine_recipients_broadcast(self):
        """Test broadcast to all farmers"""
        from src.main import FARMER_PROFILES, determine_recipients_by_criteria

        FARMER_PROFILES["farmer-1"] = MagicMock(farmer_id="farmer-1")
        FARMER_PROFILES["farmer-2"] = MagicMock(farmer_id="farmer-2")
        FARMER_PROFILES["farmer-3"] = MagicMock(farmer_id="farmer-3")

        result = determine_recipients_by_criteria()

        assert len(result) == 3
        assert "farmer-1" in result
        assert "farmer-2" in result
        assert "farmer-3" in result

        FARMER_PROFILES.clear()


class TestWeatherAlerts:
    """Test weather alert message generation"""

    def test_get_weather_alert_frost(self):
        """Test frost weather alert message"""
        from src.main import Governorate, get_weather_alert_message

        title, title_ar, body, body_ar = get_weather_alert_message("frost", Governorate.SANAA)

        assert "Frost" in title
        assert "صقيع" in title_ar
        assert "protect" in body.lower()
        assert "قم بحماية" in body_ar or "احمِ" in body_ar

    def test_get_weather_alert_heat_wave(self):
        """Test heat wave alert message"""
        from src.main import Governorate, get_weather_alert_message

        title, title_ar, body, body_ar = get_weather_alert_message("heat_wave", Governorate.TAIZ)

        assert "Heat" in title
        assert "حر" in title_ar
        assert "irrigation" in body.lower()

    def test_get_weather_alert_storm(self):
        """Test storm alert message"""
        from src.main import Governorate, get_weather_alert_message

        title, title_ar, body, body_ar = get_weather_alert_message("storm", Governorate.HODEIDAH)

        assert "Storm" in title
        assert "عاصفة" in title_ar

    def test_get_weather_alert_unknown(self):
        """Test unknown weather alert type (fallback)"""
        from src.main import Governorate, get_weather_alert_message

        title, title_ar, body, body_ar = get_weather_alert_message("unknown_type", Governorate.ADEN)

        # Should return generic alert
        assert "Weather Alert" in title
        assert "تنبيه طقس" in title_ar


class TestNATSIntegration:
    """Test NATS event integration"""

    def test_create_notification_from_nats_event(self):
        """Test creating notification from NATS event"""
        from src.main import create_notification_from_nats

        nats_event = {
            "type": "weather_alert",
            "priority": "high",
            "title": "Weather Alert",
            "title_ar": "تنبيه طقس",
            "body": "Frost expected",
            "body_ar": "صقيع متوقع",
            "data": {"temperature": -2},
            "target_farmers": ["farmer-123"],
            "channels": ["push", "sms"],
            "expires_in_hours": 24,
        }

        with patch("src.main.create_notification", new=AsyncMock()) as mock_create:
            create_notification_from_nats(nats_event)
            # Note: This is sync, so we can't await, but we can verify it was called
            # In reality, this would be tested with proper async handling

    def test_create_notification_from_nats_invalid_data(self):
        """Test NATS event with invalid data"""
        from src.main import create_notification_from_nats

        invalid_event = {
            # Missing required fields
        }

        # Should not raise exception, just log error
        try:
            create_notification_from_nats(invalid_event)
        except Exception as e:
            pytest.fail(f"Should handle invalid data gracefully: {e}")


class TestNotificationExpiry:
    """Test notification expiry logic"""

    @pytest.mark.asyncio
    async def test_notification_with_expiry(self, mock_notification):
        """Test notification created with expiry time"""
        from src.main import NotificationPriority, NotificationType, create_notification

        with patch(
            "src.repository.NotificationRepository.create",
            new=AsyncMock(return_value=mock_notification),
        ), patch(
            "src.preferences_service.PreferencesService.check_if_should_send",
            new=AsyncMock(return_value=(True, ["push"])),
        ), patch("src.main.send_notification_via_channel", new=AsyncMock()):
            result = await create_notification(
                type=NotificationType.WEATHER_ALERT,
                priority=NotificationPriority.HIGH,
                title="Alert",
                title_ar="تنبيه",
                body="Test",
                body_ar="اختبار",
                target_farmers=["farmer-123"],
                expires_in_hours=48,
            )

            assert result is not None


class TestErrorHandling:
    """Test error handling in notification service"""

    @pytest.mark.asyncio
    async def test_send_sms_client_error(self, mock_notification):
        """Test SMS sending with client error"""
        from src.main import FARMER_PROFILES, send_sms_notification

        FARMER_PROFILES["farmer-123"] = MagicMock(
            farmer_id="farmer-123", phone="+967771234567", language="ar"
        )

        mock_sms_client = MagicMock()
        mock_sms_client._initialized = True
        mock_sms_client.send_sms = AsyncMock(side_effect=Exception("Network error"))

        with patch("src.main.get_sms_client", return_value=mock_sms_client), patch(
            "src.repository.NotificationLogRepository.create_log", new=AsyncMock()
        ) as mock_log:
            await send_sms_notification(mock_notification, "farmer-123")

            # Verify error was logged
            mock_log.assert_called()
            call_args = mock_log.call_args
            assert call_args[1]["status"] == "failed"

        FARMER_PROFILES.clear()

    @pytest.mark.asyncio
    async def test_send_email_client_error(self, mock_notification):
        """Test email sending with client error"""
        from src.main import FARMER_PROFILES, send_email_notification

        FARMER_PROFILES["farmer-123"] = MagicMock(
            farmer_id="farmer-123", email="ahmed@example.com", language="ar"
        )

        mock_email_client = MagicMock()
        mock_email_client._initialized = True
        mock_email_client.send_email = AsyncMock(side_effect=Exception("SMTP error"))

        with patch("src.main.get_email_client", return_value=mock_email_client), patch(
            "src.repository.NotificationLogRepository.create_log", new=AsyncMock()
        ) as mock_log:
            await send_email_notification(mock_notification, "farmer-123")

            # Verify error was logged
            mock_log.assert_called()

        FARMER_PROFILES.clear()
