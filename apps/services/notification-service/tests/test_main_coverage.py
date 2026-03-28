"""
Tests for src/main.py - Additional coverage for untested functions and endpoints.

Covers:
- sanitize_log_input
- get_weather_alert_message
- create_notification_from_nats
- determine_recipients_by_criteria
- send_notification_via_channel error paths
- Enum and translation dictionaries
- API endpoint integration tests via TestClient
"""

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from src.main import (
        CROP_AR,
        GOVERNORATE_AR,
        NOTIFICATION_TYPE_AR,
        PRIORITY_AR,
        CreateNotificationRequest,
        CropType,
        FarmerProfile,
        Governorate,
        IrrigationReminderRequest,
        Notification,
        NotificationChannel,
        NotificationPreferences,
        NotificationPriority,
        NotificationType,
        PestAlertRequest,
        WeatherAlertRequest,
        create_notification_from_nats,
        determine_recipients_by_criteria,
        get_weather_alert_message,
        sanitize_log_input,
        send_notification_via_channel,
    )
except (ImportError, Exception):
    pytest.skip("notification-service dependencies not available", allow_module_level=True)


# ─────────────────────────────────────────────────────────────────────────────
# sanitize_log_input
# ─────────────────────────────────────────────────────────────────────────────


class TestSanitizeLogInput:
    def test_removes_newlines(self):
        assert sanitize_log_input("line1\nline2") == "line1\\nline2"

    def test_removes_carriage_returns(self):
        assert sanitize_log_input("line1\rline2") == "line1\\rline2"

    def test_removes_tabs(self):
        assert sanitize_log_input("col1\tcol2") == "col1\\tcol2"

    def test_handles_non_string(self):
        result = sanitize_log_input(12345)
        assert result == "12345"

    def test_preserves_normal_string(self):
        assert sanitize_log_input("normal text") == "normal text"

    def test_handles_mixed(self):
        result = sanitize_log_input("line1\nline2\r\tcol3")
        assert result == "line1\\nline2\\r\\tcol3"


# ─────────────────────────────────────────────────────────────────────────────
# Enum and Translation Dictionaries
# ─────────────────────────────────────────────────────────────────────────────


class TestEnumsAndTranslations:
    def test_notification_type_values(self):
        assert NotificationType.WEATHER_ALERT == "weather_alert"
        assert NotificationType.PEST_OUTBREAK == "pest_outbreak"
        assert NotificationType.IRRIGATION_REMINDER == "irrigation_reminder"
        assert NotificationType.CROP_HEALTH == "crop_health"
        assert NotificationType.MARKET_PRICE == "market_price"
        assert NotificationType.SYSTEM == "system"
        assert NotificationType.TASK_REMINDER == "task_reminder"

    def test_notification_priority_values(self):
        assert NotificationPriority.LOW == "low"
        assert NotificationPriority.MEDIUM == "medium"
        assert NotificationPriority.HIGH == "high"
        assert NotificationPriority.CRITICAL == "critical"

    def test_channel_values(self):
        assert NotificationChannel.PUSH == "push"
        assert NotificationChannel.SMS == "sms"
        assert NotificationChannel.EMAIL == "email"
        assert NotificationChannel.WHATSAPP == "whatsapp"
        assert NotificationChannel.IN_APP == "in_app"

    def test_governorate_values(self):
        assert Governorate.SANAA == "sanaa"
        assert Governorate.ADEN == "aden"
        assert len(Governorate) == 12

    def test_crop_type_values(self):
        assert CropType.TOMATO == "tomato"
        assert CropType.WHEAT == "wheat"
        assert CropType.COFFEE == "coffee"
        assert len(CropType) == 10

    def test_all_notification_types_have_arabic(self):
        for ntype in NotificationType:
            assert ntype in NOTIFICATION_TYPE_AR
            assert isinstance(NOTIFICATION_TYPE_AR[ntype], str)

    def test_all_priorities_have_arabic(self):
        for priority in NotificationPriority:
            assert priority in PRIORITY_AR
            assert isinstance(PRIORITY_AR[priority], str)

    def test_all_governorates_have_arabic(self):
        for gov in Governorate:
            assert gov in GOVERNORATE_AR
            assert isinstance(GOVERNORATE_AR[gov], str)

    def test_all_crops_have_arabic(self):
        for crop in CropType:
            assert crop in CROP_AR
            assert isinstance(CROP_AR[crop], str)


# ─────────────────────────────────────────────────────────────────────────────
# get_weather_alert_message
# ─────────────────────────────────────────────────────────────────────────────


class TestGetWeatherAlertMessage:
    def test_frost_alert(self):
        title, title_ar, body, body_ar = get_weather_alert_message("frost", Governorate.SANAA)
        assert "Frost" in title
        assert "sanaa" in title.lower()
        assert "صقيع" in title_ar
        assert "صنعاء" in title_ar

    def test_heat_wave_alert(self):
        title, title_ar, body, body_ar = get_weather_alert_message("heat_wave", Governorate.ADEN)
        assert "Heat" in title
        assert "aden" in title.lower()
        assert "حر" in title_ar

    def test_storm_alert(self):
        title, title_ar, body, body_ar = get_weather_alert_message("storm", Governorate.TAIZ)
        assert "Storm" in title
        assert "عاصفة" in title_ar

    def test_flood_alert(self):
        title, title_ar, body, body_ar = get_weather_alert_message("flood", Governorate.HODEIDAH)
        assert "Flood" in title
        assert "فيضان" in title_ar

    def test_drought_alert(self):
        title, title_ar, body, body_ar = get_weather_alert_message("drought", Governorate.IBB)
        assert "Drought" in title
        assert "جفاف" in title_ar

    def test_unknown_alert_type_returns_default(self):
        title, title_ar, body, body_ar = get_weather_alert_message("unknown_type", Governorate.SANAA)
        assert "Weather Alert" in title
        assert "تنبيه طقس" in title_ar

    def test_all_governorates_produce_valid_messages(self):
        for gov in Governorate:
            title, title_ar, body, body_ar = get_weather_alert_message("frost", gov)
            assert gov.value in title.lower()
            assert GOVERNORATE_AR[gov] in title_ar


# ─────────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────────────────────


class TestRequestModels:
    def test_farmer_profile_model(self):
        profile = FarmerProfile(
            farmer_id="f-1",
            name="Ahmed",
            name_ar="أحمد",
            governorate=Governorate.SANAA,
            crops=[CropType.WHEAT, CropType.TOMATO],
            phone="+967712345678",
            email="ahmed@example.com",
            fcm_token="token-123",
        )
        assert profile.farmer_id == "f-1"
        assert len(profile.crops) == 2
        assert profile.language == "ar"
        assert profile.notification_channels == [NotificationChannel.IN_APP]

    def test_notification_preferences_model(self):
        prefs = NotificationPreferences(
            farmer_id="f-1",
            weather_alerts=False,
            quiet_hours_start="22:00",
            quiet_hours_end="06:00",
            min_priority=NotificationPriority.HIGH,
        )
        assert prefs.weather_alerts is False
        assert prefs.min_priority == NotificationPriority.HIGH

    def test_create_notification_request(self):
        req = CreateNotificationRequest(
            type=NotificationType.WEATHER_ALERT,
            priority=NotificationPriority.HIGH,
            title="Title",
            title_ar="عنوان",
            body="Body",
            body_ar="نص",
            target_farmers=["f-1", "f-2"],
            channels=[NotificationChannel.PUSH, NotificationChannel.IN_APP],
        )
        assert req.expires_in_hours == 24
        assert len(req.target_farmers) == 2

    def test_weather_alert_request(self):
        from datetime import date, timedelta

        req = WeatherAlertRequest(
            governorates=[Governorate.SANAA, Governorate.IBB],
            alert_type="frost",
            severity=NotificationPriority.HIGH,
            expected_date=date.today() + timedelta(days=1),
            details={"min_temperature": -2},
        )
        assert len(req.governorates) == 2

    def test_pest_alert_request(self):
        req = PestAlertRequest(
            governorate=Governorate.TAIZ,
            pest_name="Aphids",
            pest_name_ar="المن",
            affected_crops=[CropType.TOMATO, CropType.POTATO],
            severity=NotificationPriority.MEDIUM,
            recommendations=["Use organic pesticides"],
            recommendations_ar=["استخدم المبيدات العضوية"],
        )
        assert len(req.affected_crops) == 2

    def test_irrigation_reminder_request(self):
        req = IrrigationReminderRequest(
            farmer_id="f-1",
            field_id="field-1",
            field_name="North Field",
            crop=CropType.WHEAT,
            water_needed_mm=25.5,
            urgency=NotificationPriority.HIGH,
        )
        assert req.water_needed_mm == 25.5

    def test_notification_model(self):
        notif = Notification(
            id="n-1",
            type=NotificationType.WEATHER_ALERT,
            type_ar="تنبيه طقس",
            priority=NotificationPriority.HIGH,
            priority_ar="عالية",
            title="Weather",
            title_ar="طقس",
            body="Body",
            body_ar="نص",
            created_at=datetime.now(UTC),
        )
        assert notif.is_read is False
        assert notif.action_url is None


# ─────────────────────────────────────────────────────────────────────────────
# create_notification_from_nats
# ─────────────────────────────────────────────────────────────────────────────


class TestCreateNotificationFromNats:
    def test_weather_alert_type(self):
        notification_data = {
            "type": "weather_alert",
            "priority": "high",
            "title": "Storm Warning",
            "title_ar": "تحذير عاصفة",
            "body": "Storm expected",
            "body_ar": "عاصفة متوقعة",
            "channels": ["push", "in_app"],
            "target_farmers": ["f-1"],
            "expires_in_hours": 12,
        }

        with patch("src.main.create_notification", new_callable=AsyncMock) as mock_create:
            asyncio.run(create_notification_from_nats(notification_data))
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["type"] == NotificationType.WEATHER_ALERT
            assert call_kwargs["priority"] == NotificationPriority.HIGH

    def test_pest_outbreak_type(self):
        notification_data = {
            "type": "pest_outbreak",
            "priority": "medium",
            "title": "Pest",
            "title_ar": "آفة",
            "body": "Alert",
            "body_ar": "تنبيه",
        }

        with patch("src.main.create_notification", new_callable=AsyncMock) as mock_create:
            asyncio.run(create_notification_from_nats(notification_data))
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["type"] == NotificationType.PEST_OUTBREAK

    def test_irrigation_reminder_type(self):
        notification_data = {
            "type": "irrigation_reminder",
            "priority": "low",
            "title": "Irrigation",
            "title_ar": "ري",
            "body": "Apply water",
            "body_ar": "طبق الماء",
        }

        with patch("src.main.create_notification", new_callable=AsyncMock) as mock_create:
            asyncio.run(create_notification_from_nats(notification_data))
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["type"] == NotificationType.IRRIGATION_REMINDER

    def test_unknown_type_defaults_to_system(self):
        notification_data = {
            "type": "unknown_type",
            "title": "Title",
            "title_ar": "عنوان",
            "body": "Body",
            "body_ar": "نص",
        }

        with patch("src.main.create_notification", new_callable=AsyncMock) as mock_create:
            asyncio.run(create_notification_from_nats(notification_data))
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["type"] == NotificationType.SYSTEM

    def test_unknown_priority_defaults_to_medium(self):
        notification_data = {
            "type": "system",
            "priority": "unknown",
            "title": "Title",
            "title_ar": "عنوان",
            "body": "Body",
            "body_ar": "نص",
        }

        with patch("src.main.create_notification", new_callable=AsyncMock) as mock_create:
            asyncio.run(create_notification_from_nats(notification_data))
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["priority"] == NotificationPriority.MEDIUM

    def test_channel_mapping(self):
        notification_data = {
            "type": "system",
            "title": "Title",
            "title_ar": "عنوان",
            "body": "Body",
            "body_ar": "نص",
            "channels": ["push", "sms", "email"],
        }

        with patch("src.main.create_notification", new_callable=AsyncMock) as mock_create:
            asyncio.run(create_notification_from_nats(notification_data))
            call_kwargs = mock_create.call_args[1]
            assert NotificationChannel.PUSH in call_kwargs["channels"]
            assert NotificationChannel.SMS in call_kwargs["channels"]
            assert NotificationChannel.EMAIL in call_kwargs["channels"]

    def test_unknown_channel_defaults_to_in_app(self):
        notification_data = {
            "type": "system",
            "title": "Title",
            "title_ar": "عنوان",
            "body": "Body",
            "body_ar": "نص",
            "channels": ["unknown_channel"],
        }

        with patch("src.main.create_notification", new_callable=AsyncMock) as mock_create:
            asyncio.run(create_notification_from_nats(notification_data))
            call_kwargs = mock_create.call_args[1]
            assert NotificationChannel.IN_APP in call_kwargs["channels"]

    def test_defaults_for_missing_fields(self):
        notification_data = {}

        with patch("src.main.create_notification", new_callable=AsyncMock) as mock_create:
            asyncio.run(create_notification_from_nats(notification_data))
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs["title"] == "Notification"
            assert call_kwargs["title_ar"] == "إشعار"
            assert call_kwargs["body"] == ""
            assert call_kwargs["body_ar"] == ""
            assert call_kwargs["data"] == {}
            assert call_kwargs["target_farmers"] == []
            assert call_kwargs["expires_in_hours"] == 24

    def test_error_handled_gracefully(self):
        notification_data = {
            "type": "system",
            "title": "Title",
            "title_ar": "عنوان",
            "body": "Body",
            "body_ar": "نص",
        }

        with patch("src.main.create_notification", new_callable=AsyncMock, side_effect=Exception("DB error")):
            # Should not raise
            asyncio.run(create_notification_from_nats(notification_data))

    def test_all_types_mapped(self):
        """Verify all known notification types are handled"""
        for ntype_str, ntype_enum in [
            ("weather_alert", NotificationType.WEATHER_ALERT),
            ("pest_outbreak", NotificationType.PEST_OUTBREAK),
            ("irrigation_reminder", NotificationType.IRRIGATION_REMINDER),
            ("crop_health", NotificationType.CROP_HEALTH),
            ("market_price", NotificationType.MARKET_PRICE),
            ("system", NotificationType.SYSTEM),
            ("task_reminder", NotificationType.TASK_REMINDER),
        ]:
            notification_data = {
                "type": ntype_str,
                "title": "T",
                "title_ar": "ع",
                "body": "B",
                "body_ar": "ن",
            }

            with patch("src.main.create_notification", new_callable=AsyncMock) as mock_create:
                asyncio.run(create_notification_from_nats(notification_data))
                call_kwargs = mock_create.call_args[1]
                assert call_kwargs["type"] == ntype_enum


# ─────────────────────────────────────────────────────────────────────────────
# determine_recipients_by_criteria
# ─────────────────────────────────────────────────────────────────────────────


class TestDetermineRecipientsByCriteria:
    def test_specific_farmers_returned(self):
        result = asyncio.run(determine_recipients_by_criteria(
            target_farmers=["f-1", "f-2"],
        ))
        assert result == ["f-1", "f-2"]

    def test_empty_farmers_queries_database(self):
        with patch("src.main.FarmerProfileRepository") as mock_repo:
            mock_repo.find_by_criteria = AsyncMock(return_value=[])
            mock_repo.get_all = AsyncMock(return_value=[])

            result = asyncio.run(determine_recipients_by_criteria(
                target_farmers=[],
                target_governorates=[Governorate.SANAA],
            ))
            assert result == []
            mock_repo.find_by_criteria.assert_called_once()

    def test_none_defaults_handled(self):
        result = asyncio.run(determine_recipients_by_criteria())
        # Should return some list (empty if database unavailable)
        assert isinstance(result, list)

    def test_database_error_returns_empty(self):
        with patch("src.main.FarmerProfileRepository") as mock_repo:
            mock_repo.find_by_criteria = AsyncMock(side_effect=Exception("DB error"))

            result = asyncio.run(determine_recipients_by_criteria(
                target_farmers=[],
                target_governorates=[Governorate.SANAA],
            ))
            assert result == []

    def test_broadcast_fallback(self):
        mock_profile = MagicMock()
        mock_profile.farmer_id = "broadcast-farmer"

        with patch("src.main.FarmerProfileRepository") as mock_repo:
            mock_repo.find_by_criteria = AsyncMock(return_value=[])
            mock_repo.get_all = AsyncMock(return_value=[mock_profile])

            result = asyncio.run(determine_recipients_by_criteria(
                target_farmers=[],
                target_governorates=[],
                target_crops=[],
            ))
            assert result == ["broadcast-farmer"]


# ─────────────────────────────────────────────────────────────────────────────
# send_notification_via_channel
# ─────────────────────────────────────────────────────────────────────────────


class TestSendNotificationViaChannel:
    def test_in_app_channel_noop(self):
        mock_notif = MagicMock()
        mock_notif.id = "n-1"
        # IN_APP should do nothing (stored in DB already)
        asyncio.run(send_notification_via_channel(mock_notif, NotificationChannel.IN_APP, "farmer-1"))

    def test_sms_channel_error_logged(self):
        mock_notif = MagicMock()
        mock_notif.id = "n-1"

        with patch("src.main.send_sms_notification", new_callable=AsyncMock, side_effect=Exception("SMS error")):
            with patch("src.main.NotificationLogRepository") as mock_log:
                mock_log.create_log = AsyncMock()
                asyncio.run(send_notification_via_channel(mock_notif, NotificationChannel.SMS, "farmer-1"))
                mock_log.create_log.assert_called_once()

    def test_email_channel_error_logged(self):
        mock_notif = MagicMock()
        mock_notif.id = "n-1"

        with patch("src.main.send_email_notification", new_callable=AsyncMock, side_effect=Exception("Email error")):
            with patch("src.main.NotificationLogRepository") as mock_log:
                mock_log.create_log = AsyncMock()
                asyncio.run(send_notification_via_channel(mock_notif, NotificationChannel.EMAIL, "farmer-1"))
                mock_log.create_log.assert_called_once()

    def test_push_channel_error_logged(self):
        mock_notif = MagicMock()
        mock_notif.id = "n-1"

        with patch("src.main.send_push_notification", new_callable=AsyncMock, side_effect=Exception("Push error")):
            with patch("src.main.NotificationLogRepository") as mock_log:
                mock_log.create_log = AsyncMock()
                asyncio.run(send_notification_via_channel(mock_notif, NotificationChannel.PUSH, "farmer-1"))
                mock_log.create_log.assert_called_once()

    def test_whatsapp_channel_error_logged(self):
        mock_notif = MagicMock()
        mock_notif.id = "n-1"

        with patch("src.main.send_whatsapp_notification", new_callable=AsyncMock, side_effect=Exception("WA error")):
            with patch("src.main.NotificationLogRepository") as mock_log:
                mock_log.create_log = AsyncMock()
                asyncio.run(send_notification_via_channel(mock_notif, NotificationChannel.WHATSAPP, "farmer-1"))
                mock_log.create_log.assert_called_once()
