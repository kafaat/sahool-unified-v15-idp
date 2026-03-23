"""
Extended Tests for Notification Service
اختبارات موسعة لخدمة الإشعارات
"""

from unittest.mock import AsyncMock, patch

import pytest


class TestNotificationTypes:
    """Test notification type handling"""

    def test_notification_type_enum(self):
        """Test NotificationType enum"""
        from src.main import NotificationType

        assert NotificationType.WEATHER_ALERT == "weather_alert"
        assert NotificationType.PEST_OUTBREAK == "pest_outbreak"
        assert NotificationType.IRRIGATION_REMINDER == "irrigation_reminder"

    def test_notification_priority_enum(self):
        """Test NotificationPriority enum"""
        from src.main import NotificationPriority

        assert NotificationPriority.LOW == "low"
        assert NotificationPriority.CRITICAL == "critical"

    def test_notification_channel_enum(self):
        """Test NotificationChannel enum"""
        from src.main import NotificationChannel

        assert NotificationChannel.PUSH == "push"
        assert NotificationChannel.SMS == "sms"
        assert NotificationChannel.IN_APP == "in_app"


class TestGeographicEnums:
    """Test geographic enumerations"""

    def test_governorate_enum(self):
        """Test Governorate enum for Yemen"""
        from src.main import Governorate

        assert Governorate.SANAA == "sanaa"
        assert Governorate.ADEN == "aden"
        assert Governorate.TAIZ == "taiz"
        assert hasattr(Governorate, "HODEIDAH")

    def test_crop_type_enum(self):
        """Test CropType enum"""
        from src.main import CropType

        assert CropType.TOMATO == "tomato"
        assert CropType.WHEAT == "wheat"
        assert CropType.COFFEE == "coffee"
        assert CropType.QAT == "qat"


class TestDatabaseIntegration:
    """Test database integration"""

    def test_database_url_configured(self):
        """Test DATABASE_URL is available in database module"""
        from src.database import DATABASE_URL

        assert DATABASE_URL is not None
        assert len(DATABASE_URL) > 0

    def test_tortoise_orm_config_structure(self):
        """Test Tortoise ORM config has expected keys"""
        from src.database import TORTOISE_ORM

        assert "connections" in TORTOISE_ORM
        assert "apps" in TORTOISE_ORM
        assert "default" in TORTOISE_ORM["connections"]

    def test_init_notification_db_function_exists(self):
        """Test init_notification_db function is defined"""
        from src.database import init_notification_db

        assert callable(init_notification_db)
