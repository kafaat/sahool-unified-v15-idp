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

    @pytest.mark.asyncio
    async def test_init_db(self):
        """Test database initialization"""
        with patch("src.database.create_async_engine") as mock_engine:
            mock_engine_instance = AsyncMock()
            mock_engine.return_value = mock_engine_instance

            from src.database import init_db

            # Should not raise error
            await init_db()

    @pytest.mark.asyncio
    async def test_close_db(self):
        """Test database closure"""
        with patch("src.database.engine") as mock_engine:
            mock_engine.dispose = AsyncMock()

            from src.database import close_db

            await close_db()
            mock_engine.dispose.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_db_health(self):
        """Test database health check"""
        with patch("src.database.AsyncSession") as mock_session_class:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock()
            mock_session_class.return_value.__aenter__.return_value = mock_session

            from src.database import check_db_health

            result = await check_db_health()

            assert isinstance(result, bool)
