"""
Tests for src/models.py - Database Model Enums and Types

Covers:
- ChannelType enum
- Model class attributes
"""

import pytest

try:
    from src.database import TORTOISE_ORM
    from src.models import (
        ChannelType,
        FarmerProfile,
        Notification,
        NotificationChannel,
        NotificationLog,
        NotificationPreference,
    )
except BaseException:
    pytest.skip("notification-service dependencies not available", allow_module_level=True)


class TestChannelTypeEnum:
    def test_all_channel_types(self):
        assert ChannelType.EMAIL == "email"
        assert ChannelType.SMS == "sms"
        assert ChannelType.PUSH == "push"
        assert ChannelType.WHATSAPP == "whatsapp"
        assert ChannelType.IN_APP == "in_app"


class TestModelClasses:
    def test_notification_model_exists(self):
        assert hasattr(Notification, "Meta")

    def test_notification_log_model_exists(self):
        assert hasattr(NotificationLog, "Meta")

    def test_notification_preference_exists(self):
        assert hasattr(NotificationPreference, "Meta")

    def test_notification_channel_exists(self):
        assert hasattr(NotificationChannel, "Meta")

    def test_farmer_profile_exists(self):
        assert hasattr(FarmerProfile, "Meta")


"""
Tests for database.py module-level configuration

Covers:
- DATABASE_URL config
- TORTOISE_ORM config
"""


class TestDatabaseConfig:
    def test_tortoise_orm_config_exists(self):
        assert "connections" in TORTOISE_ORM
        assert "apps" in TORTOISE_ORM

    def test_tortoise_orm_has_default_connection(self):
        assert "default" in TORTOISE_ORM["connections"]

    def test_tortoise_orm_has_models_app(self):
        assert "models" in TORTOISE_ORM["apps"]

    def test_uses_timezone(self):
        assert TORTOISE_ORM.get("use_tz") is True
