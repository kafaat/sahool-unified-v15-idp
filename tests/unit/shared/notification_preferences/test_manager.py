"""
Tests for notification_preferences manager module
اختبارات وحدة مدير تفضيلات الإشعارات
"""

from __future__ import annotations

from datetime import time

import pytest

from shared.notification_preferences.manager import (
    InMemoryStorage,
    NotificationPreferencesManager,
)
from shared.notification_preferences.models import (
    AlertType,
    AlertUrgency,
    ChannelConfig,
    DayOfWeek,
    Language,
    NotificationChannel,
    QuietHours,
    TimeBasedRule,
    UrgencyOverride,
    create_default_preferences,
)


@pytest.fixture
def storage():
    return InMemoryStorage()


@pytest.fixture
def manager(storage):
    return NotificationPreferencesManager(storage=storage)


class TestInMemoryStorage:
    @pytest.mark.asyncio
    async def test_save_and_get(self, storage):
        prefs = create_default_preferences("user1", "t1")
        await storage.save(prefs)
        retrieved = await storage.get("user1", "t1")
        assert retrieved is not None
        assert retrieved.user_id == "user1"

    @pytest.mark.asyncio
    async def test_get_not_found(self, storage):
        result = await storage.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, storage):
        prefs = create_default_preferences("user1", "t1")
        await storage.save(prefs)
        result = await storage.delete("user1", "t1")
        assert result is True
        assert await storage.get("user1", "t1") is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, storage):
        result = await storage.delete("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_list_all(self, storage):
        await storage.save(create_default_preferences("u1", "t1"))
        await storage.save(create_default_preferences("u2", "t1"))
        await storage.save(create_default_preferences("u3", "t2"))
        all_prefs = await storage.list_all()
        assert len(all_prefs) == 3

    @pytest.mark.asyncio
    async def test_list_all_by_tenant(self, storage):
        await storage.save(create_default_preferences("u1", "t1"))
        await storage.save(create_default_preferences("u2", "t1"))
        await storage.save(create_default_preferences("u3", "t2"))
        t1_prefs = await storage.list_all(tenant_id="t1")
        assert len(t1_prefs) == 2

    @pytest.mark.asyncio
    async def test_save_increments_version(self, storage):
        prefs = create_default_preferences("user1")
        assert prefs.version == 1
        await storage.save(prefs)
        assert prefs.version == 2
        await storage.save(prefs)
        assert prefs.version == 3


class TestNotificationPreferencesManagerCRUD:
    @pytest.mark.asyncio
    async def test_get_preferences_creates_default(self, manager):
        prefs = await manager.get_preferences("user1", "t1")
        assert prefs is not None
        assert prefs.user_id == "user1"
        assert prefs.notifications_enabled is True

    @pytest.mark.asyncio
    async def test_get_preferences_no_create(self, manager):
        prefs = await manager.get_preferences("user1", create_if_missing=False)
        assert prefs is None

    @pytest.mark.asyncio
    async def test_save_preferences(self, manager):
        prefs = create_default_preferences("user1", "t1")
        saved = await manager.save_preferences(prefs)
        assert saved.version >= 1

    @pytest.mark.asyncio
    async def test_delete_preferences(self, manager):
        await manager.get_preferences("user1", "t1")
        result = await manager.delete_preferences("user1", "t1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, manager):
        result = await manager.delete_preferences("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_reset_to_defaults(self, manager):
        prefs = await manager.get_preferences("user1")
        prefs.notifications_enabled = False
        await manager.save_preferences(prefs)

        reset = await manager.reset_to_defaults("user1")
        assert reset.notifications_enabled is True


class TestMasterToggle:
    @pytest.mark.asyncio
    async def test_enable_notifications(self, manager):
        prefs = await manager.disable_notifications("user1")
        assert prefs.notifications_enabled is False
        prefs = await manager.enable_notifications("user1")
        assert prefs.notifications_enabled is True

    @pytest.mark.asyncio
    async def test_disable_notifications(self, manager):
        prefs = await manager.disable_notifications("user1")
        assert prefs.notifications_enabled is False


class TestLanguageOperations:
    @pytest.mark.asyncio
    async def test_set_language(self, manager):
        prefs = await manager.set_language("user1", Language.ENGLISH)
        assert prefs.language == Language.ENGLISH

        prefs = await manager.set_language("user1", Language.ARABIC)
        assert prefs.language == Language.ARABIC


class TestChannelOperations:
    @pytest.mark.asyncio
    async def test_set_default_channels(self, manager):
        prefs = await manager.set_default_channels(
            "user1",
            [NotificationChannel.PUSH, NotificationChannel.EMAIL],
        )
        assert NotificationChannel.PUSH in prefs.default_channels

    @pytest.mark.asyncio
    async def test_set_default_channels_empty_raises(self, manager):
        with pytest.raises(ValueError):
            await manager.set_default_channels("user1", [])

    @pytest.mark.asyncio
    async def test_add_channel(self, manager):
        prefs = await manager.add_channel(
            "user1",
            NotificationChannel.WHATSAPP,
            address="+966501234567",
            verified=True,
        )
        config = prefs.get_channel_config(NotificationChannel.WHATSAPP)
        assert config is not None
        assert config.address == "+966501234567"
        assert config.verified is True

    @pytest.mark.asyncio
    async def test_add_channel_update_existing(self, manager):
        await manager.add_channel("user1", NotificationChannel.SMS, address="old")
        prefs = await manager.add_channel("user1", NotificationChannel.SMS, address="new")
        config = prefs.get_channel_config(NotificationChannel.SMS)
        assert config.address == "new"

    @pytest.mark.asyncio
    async def test_remove_channel(self, manager):
        await manager.add_channel("user1", NotificationChannel.WHATSAPP, address="test")
        prefs = await manager.remove_channel("user1", NotificationChannel.WHATSAPP)
        config = prefs.get_channel_config(NotificationChannel.WHATSAPP)
        assert config is None

    @pytest.mark.asyncio
    async def test_enable_disable_channel(self, manager):
        await manager.add_channel("user1", NotificationChannel.SMS, address="test")
        prefs = await manager.disable_channel("user1", NotificationChannel.SMS)
        config = prefs.get_channel_config(NotificationChannel.SMS)
        assert config.enabled is False

        prefs = await manager.enable_channel("user1", NotificationChannel.SMS)
        config = prefs.get_channel_config(NotificationChannel.SMS)
        assert config.enabled is True

    @pytest.mark.asyncio
    async def test_verify_channel(self, manager):
        await manager.add_channel("user1", NotificationChannel.SMS, address="test")
        prefs = await manager.verify_channel("user1", NotificationChannel.SMS)
        config = prefs.get_channel_config(NotificationChannel.SMS)
        assert config.verified is True
        assert config.verified_at is not None


class TestAlertTypeOperations:
    @pytest.mark.asyncio
    async def test_set_alert_preference(self, manager):
        prefs = await manager.set_alert_preference(
            "user1",
            AlertType.IRRIGATION_REMINDER,
            channels=[NotificationChannel.PUSH],
            min_urgency=AlertUrgency.MEDIUM,
        )
        pref = prefs.get_alert_preference(AlertType.IRRIGATION_REMINDER)
        assert pref is not None
        assert pref.min_urgency == AlertUrgency.MEDIUM

    @pytest.mark.asyncio
    async def test_disable_alert_type(self, manager):
        prefs = await manager.disable_alert_type("user1", AlertType.MARKET_PRICE)
        pref = prefs.get_alert_preference(AlertType.MARKET_PRICE)
        assert pref is not None
        assert pref.enabled is False

    @pytest.mark.asyncio
    async def test_enable_alert_type(self, manager):
        await manager.disable_alert_type("user1", AlertType.MARKET_PRICE)
        prefs = await manager.enable_alert_type("user1", AlertType.MARKET_PRICE)
        pref = prefs.get_alert_preference(AlertType.MARKET_PRICE)
        assert pref.enabled is True


class TestQuietHoursOperations:
    @pytest.mark.asyncio
    async def test_set_quiet_hours(self, manager):
        prefs = await manager.set_quiet_hours(
            "user1",
            start_time=time(22, 0),
            end_time=time(6, 0),
            enabled=True,
            days=[DayOfWeek.FRIDAY, DayOfWeek.SATURDAY],
        )
        assert prefs.quiet_hours.enabled is True
        assert prefs.quiet_hours.start_time == time(22, 0)
        assert DayOfWeek.FRIDAY in prefs.quiet_hours.days

    @pytest.mark.asyncio
    async def test_disable_quiet_hours(self, manager):
        await manager.set_quiet_hours("user1", time(22, 0), time(6, 0), enabled=True)
        prefs = await manager.disable_quiet_hours("user1")
        assert prefs.quiet_hours.enabled is False

    @pytest.mark.asyncio
    async def test_enable_quiet_hours(self, manager):
        await manager.set_quiet_hours("user1", time(22, 0), time(6, 0), enabled=False)
        prefs = await manager.enable_quiet_hours("user1")
        assert prefs.quiet_hours.enabled is True


class TestTimeRuleOperations:
    @pytest.mark.asyncio
    async def test_add_time_rule(self, manager):
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
        prefs = await manager.add_time_rule("user1", rule)
        assert len(prefs.time_rules) >= 1

    @pytest.mark.asyncio
    async def test_remove_time_rule(self, manager):
        rule = TimeBasedRule(
            id="rule1",
            name="Test",
            name_ar="اختبار",
            channels=[NotificationChannel.SMS],
            action="block",
        )
        await manager.add_time_rule("user1", rule)
        prefs = await manager.remove_time_rule("user1", "rule1")
        assert all(r.id != "rule1" for r in prefs.time_rules)

    @pytest.mark.asyncio
    async def test_create_no_sms_at_night(self, manager):
        prefs = await manager.create_no_sms_at_night_rule("user1")
        sms_rules = [r for r in prefs.time_rules if NotificationChannel.SMS in r.channels]
        assert len(sms_rules) >= 1


class TestUrgencyOverrideOperations:
    @pytest.mark.asyncio
    async def test_set_urgency_override(self, manager):
        override = UrgencyOverride(
            urgency=AlertUrgency.CRITICAL,
            force_channels=[NotificationChannel.SMS, NotificationChannel.PUSH],
            bypass_quiet_hours=True,
        )
        prefs = await manager.set_urgency_override("user1", override)
        assert len(prefs.urgency_overrides) >= 1

    @pytest.mark.asyncio
    async def test_remove_urgency_override(self, manager):
        override = UrgencyOverride(
            urgency=AlertUrgency.CRITICAL,
            force_channels=[NotificationChannel.SMS],
        )
        await manager.set_urgency_override("user1", override)
        prefs = await manager.remove_urgency_override("user1", AlertUrgency.CRITICAL)
        assert all(o.urgency != AlertUrgency.CRITICAL for o in prefs.urgency_overrides)


class TestBulkOperations:
    @pytest.mark.asyncio
    async def test_update_preferences(self, manager):
        prefs = await manager.update_preferences(
            "user1",
            {
                "notifications_enabled": False,
                "sound_enabled": False,
                "language": "en",
            },
        )
        assert prefs.notifications_enabled is False
        assert prefs.sound_enabled is False
        assert prefs.language == Language.ENGLISH

    @pytest.mark.asyncio
    async def test_export_preferences(self, manager):
        await manager.get_preferences("user1", "t1")
        exported = await manager.export_preferences("user1", "t1")
        assert exported["user_id"] == "user1"

    @pytest.mark.asyncio
    async def test_export_nonexistent(self, manager):
        exported = await manager.export_preferences("nonexistent")
        assert exported == {}

    @pytest.mark.asyncio
    async def test_import_preferences(self, manager):
        original = create_default_preferences("user1", "t1")
        data = original.to_dict()
        imported = await manager.import_preferences("user2", data, "t1")
        assert imported.user_id == "user2"
        assert imported.tenant_id == "t1"

    @pytest.mark.asyncio
    async def test_import_merge(self, manager):
        # Create existing preferences
        await manager.get_preferences("user1", "t1")
        # Import with merge
        new_data = create_default_preferences("other", "t1")
        new_data.channel_configs.append(
            ChannelConfig(channel=NotificationChannel.WHATSAPP, address="test"),
        )
        data = new_data.to_dict()
        merged = await manager.import_preferences("user1", data, "t1", merge=True)
        assert merged.user_id == "user1"


class TestValidation:
    @pytest.mark.asyncio
    async def test_validate_empty_user_id(self, manager):
        prefs = create_default_preferences("", "t1")
        with pytest.raises(ValueError, match="User ID"):
            await manager.save_preferences(prefs)

    @pytest.mark.asyncio
    async def test_validate_quiet_hours_same_time(self, manager):
        prefs = create_default_preferences("user1")
        prefs.quiet_hours = QuietHours(
            enabled=True,
            start_time=time(22, 0),
            end_time=time(22, 0),
        )
        with pytest.raises(ValueError, match="same"):
            await manager.save_preferences(prefs)

    @pytest.mark.asyncio
    async def test_validate_duplicate_channel(self, manager):
        prefs = create_default_preferences("user1")
        prefs.channel_configs = [
            ChannelConfig(channel=NotificationChannel.SMS, address="+966501234567"),
            ChannelConfig(channel=NotificationChannel.SMS, address="+966509876543"),
        ]
        with pytest.raises(ValueError, match="Duplicate channel"):
            await manager.save_preferences(prefs)

    @pytest.mark.asyncio
    async def test_validate_fallback_rule(self, manager):
        prefs = create_default_preferences("user1")
        prefs.time_rules.append(
            TimeBasedRule(
                name="Bad",
                name_ar="سيء",
                channels=[NotificationChannel.SMS],
                action="channel_fallback",
                fallback_channel=None,
            )
        )
        with pytest.raises(ValueError, match="Fallback"):
            await manager.save_preferences(prefs)

    @pytest.mark.asyncio
    async def test_validate_duplicate_urgency_override(self, manager):
        prefs = create_default_preferences("user1")
        prefs.urgency_overrides = [
            UrgencyOverride(urgency=AlertUrgency.CRITICAL, force_channels=[NotificationChannel.SMS]),
            UrgencyOverride(urgency=AlertUrgency.CRITICAL, force_channels=[NotificationChannel.PUSH]),
        ]
        with pytest.raises(ValueError, match="Duplicate urgency"):
            await manager.save_preferences(prefs)


class TestQueryOperations:
    @pytest.mark.asyncio
    async def test_get_users_by_channel(self, manager):
        # Create users with verified push channel
        prefs1 = await manager.get_preferences("u1", "t1")
        await manager.add_channel("u1", NotificationChannel.PUSH, address="token1", tenant_id="t1", verified=True)

        prefs2 = await manager.get_preferences("u2", "t1")
        await manager.add_channel("u2", NotificationChannel.PUSH, address="token2", tenant_id="t1", verified=True)

        users = await manager.get_users_by_channel(NotificationChannel.PUSH, tenant_id="t1")
        assert "u1" in users
        assert "u2" in users

    @pytest.mark.asyncio
    async def test_get_users_by_channel_verified_only(self, manager):
        await manager.get_preferences("u1", "t1")
        await manager.add_channel("u1", NotificationChannel.SMS, address="phone", tenant_id="t1", verified=False)

        users = await manager.get_users_by_channel(
            NotificationChannel.SMS,
            tenant_id="t1",
            verified_only=True,
        )
        assert "u1" not in users

    @pytest.mark.asyncio
    async def test_get_users_subscribed_to_alert(self, manager):
        await manager.get_preferences("u1", "t1")
        await manager.get_preferences("u2", "t1")
        await manager.disable_alert_type("u2", AlertType.MARKET_PRICE, "t1")

        users = await manager.get_users_subscribed_to_alert(AlertType.MARKET_PRICE, "t1")
        assert "u1" in users
        assert "u2" not in users

    @pytest.mark.asyncio
    async def test_disabled_user_not_in_query(self, manager):
        await manager.get_preferences("u1", "t1")
        await manager.disable_notifications("u1", "t1")

        users = await manager.get_users_subscribed_to_alert(AlertType.IRRIGATION_REMINDER, "t1")
        assert "u1" not in users
