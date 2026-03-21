"""Tests for NotificationPreferencesManager"""

import pytest
from datetime import time

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
    UserNotificationPreferences,
    create_default_preferences,
)

# Default tenant ID for tests
T = "test-tenant"


@pytest.fixture
def storage():
    return InMemoryStorage()


@pytest.fixture
def manager(storage):
    return NotificationPreferencesManager(storage=storage)


class TestInMemoryStorage:
    @pytest.mark.asyncio
    async def test_save_and_get(self, storage):
        prefs = create_default_preferences("user1", T)
        await storage.save(prefs)
        retrieved = await storage.get("user1", T)
        assert retrieved is not None
        assert retrieved.user_id == "user1"

    @pytest.mark.asyncio
    async def test_get_not_found(self, storage):
        result = await storage.get("nonexistent", T)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, storage):
        prefs = create_default_preferences("user1", T)
        await storage.save(prefs)
        result = await storage.delete("user1", T)
        assert result is True
        assert await storage.get("user1", T) is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, storage):
        result = await storage.delete("nonexistent", T)
        assert result is False

    @pytest.mark.asyncio
    async def test_list_all(self, storage):
        await storage.save(create_default_preferences("u1", T))
        await storage.save(create_default_preferences("u2", T))
        await storage.save(create_default_preferences("u3", "t2"))
        all_prefs = await storage.list_all(T)
        assert len(all_prefs) == 2

    @pytest.mark.asyncio
    async def test_list_all_by_tenant(self, storage):
        await storage.save(create_default_preferences("u1", T))
        await storage.save(create_default_preferences("u2", T))
        await storage.save(create_default_preferences("u3", "t2"))
        t1_prefs = await storage.list_all(tenant_id=T)
        assert len(t1_prefs) == 2

    @pytest.mark.asyncio
    async def test_save_increments_version(self, storage):
        prefs = create_default_preferences("user1", T)
        assert prefs.version == 1
        await storage.save(prefs)
        assert prefs.version == 2
        await storage.save(prefs)
        assert prefs.version == 3


class TestNotificationPreferencesManagerCRUD:
    @pytest.mark.asyncio
    async def test_get_preferences_creates_default(self, manager):
        prefs = await manager.get_preferences("user1", T)
        assert prefs is not None
        assert prefs.user_id == "user1"
        assert prefs.notifications_enabled is True

    @pytest.mark.asyncio
    async def test_get_preferences_no_create(self, manager):
        prefs = await manager.get_preferences("user1", T, create_if_missing=False)
        assert prefs is None

    @pytest.mark.asyncio
    async def test_save_preferences(self, manager):
        prefs = create_default_preferences("user1", T)
        saved = await manager.save_preferences(prefs)
        assert saved.version >= 1

    @pytest.mark.asyncio
    async def test_delete_preferences(self, manager):
        await manager.get_preferences("user1", T)
        result = await manager.delete_preferences("user1", T)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, manager):
        result = await manager.delete_preferences("nonexistent", T)
        assert result is False

    @pytest.mark.asyncio
    async def test_reset_to_defaults(self, manager):
        prefs = await manager.get_preferences("user1", T)
        prefs.notifications_enabled = False
        await manager.save_preferences(prefs)

        reset = await manager.reset_to_defaults("user1", T)
        assert reset.notifications_enabled is True


class TestMasterToggle:
    @pytest.mark.asyncio
    async def test_enable_notifications(self, manager):
        prefs = await manager.disable_notifications("user1", T)
        assert prefs.notifications_enabled is False
        prefs = await manager.enable_notifications("user1", T)
        assert prefs.notifications_enabled is True

    @pytest.mark.asyncio
    async def test_disable_notifications(self, manager):
        prefs = await manager.disable_notifications("user1", T)
        assert prefs.notifications_enabled is False


class TestLanguageOperations:
    @pytest.mark.asyncio
    async def test_set_language(self, manager):
        prefs = await manager.set_language("user1", Language.ENGLISH, T)
        assert prefs.language == Language.ENGLISH

        prefs = await manager.set_language("user1", Language.ARABIC, T)
        assert prefs.language == Language.ARABIC


class TestChannelOperations:
    @pytest.mark.asyncio
    async def test_set_default_channels(self, manager):
        prefs = await manager.set_default_channels(
            "user1",
            [NotificationChannel.PUSH, NotificationChannel.EMAIL],
            T,
        )
        assert NotificationChannel.PUSH in prefs.default_channels

    @pytest.mark.asyncio
    async def test_set_default_channels_empty_raises(self, manager):
        with pytest.raises(ValueError):
            await manager.set_default_channels("user1", [], T)

    @pytest.mark.asyncio
    async def test_add_channel(self, manager):
        prefs = await manager.add_channel(
            "user1",
            NotificationChannel.WHATSAPP,
            address="+966501234567",
            verified=True,
            tenant_id=T,
        )
        config = prefs.get_channel_config(NotificationChannel.WHATSAPP)
        assert config is not None
        assert config.address == "+966501234567"
        assert config.verified is True

    @pytest.mark.asyncio
    async def test_add_channel_update_existing(self, manager):
        await manager.add_channel("user1", NotificationChannel.SMS, address="old", tenant_id=T)
        prefs = await manager.add_channel("user1", NotificationChannel.SMS, address="new", tenant_id=T)
        config = prefs.get_channel_config(NotificationChannel.SMS)
        assert config.address == "new"

    @pytest.mark.asyncio
    async def test_remove_channel(self, manager):
        await manager.add_channel("user1", NotificationChannel.WHATSAPP, address="test", tenant_id=T)
        prefs = await manager.remove_channel("user1", NotificationChannel.WHATSAPP, T)
        config = prefs.get_channel_config(NotificationChannel.WHATSAPP)
        assert config is None

    @pytest.mark.asyncio
    async def test_enable_disable_channel(self, manager):
        await manager.add_channel("user1", NotificationChannel.SMS, address="test", tenant_id=T)
        prefs = await manager.disable_channel("user1", NotificationChannel.SMS, T)
        config = prefs.get_channel_config(NotificationChannel.SMS)
        assert config.enabled is False

        prefs = await manager.enable_channel("user1", NotificationChannel.SMS, T)
        config = prefs.get_channel_config(NotificationChannel.SMS)
        assert config.enabled is True

    @pytest.mark.asyncio
    async def test_verify_channel(self, manager):
        await manager.add_channel("user1", NotificationChannel.SMS, address="test", tenant_id=T)
        prefs = await manager.verify_channel("user1", NotificationChannel.SMS, T)
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
            tenant_id=T,
        )
        pref = prefs.get_alert_preference(AlertType.IRRIGATION_REMINDER)
        assert pref is not None
        assert pref.min_urgency == AlertUrgency.MEDIUM

    @pytest.mark.asyncio
    async def test_disable_alert_type(self, manager):
        prefs = await manager.disable_alert_type("user1", AlertType.MARKET_PRICE, T)
        pref = prefs.get_alert_preference(AlertType.MARKET_PRICE)
        assert pref is not None
        assert pref.enabled is False

    @pytest.mark.asyncio
    async def test_enable_alert_type(self, manager):
        await manager.disable_alert_type("user1", AlertType.MARKET_PRICE, T)
        prefs = await manager.enable_alert_type("user1", AlertType.MARKET_PRICE, T)
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
            tenant_id=T,
        )
        assert prefs.quiet_hours.enabled is True
        assert prefs.quiet_hours.start_time == time(22, 0)
        assert DayOfWeek.FRIDAY in prefs.quiet_hours.days

    @pytest.mark.asyncio
    async def test_disable_quiet_hours(self, manager):
        await manager.set_quiet_hours("user1", time(22, 0), time(6, 0), enabled=True, tenant_id=T)
        prefs = await manager.disable_quiet_hours("user1", T)
        assert prefs.quiet_hours.enabled is False

    @pytest.mark.asyncio
    async def test_enable_quiet_hours(self, manager):
        await manager.set_quiet_hours("user1", time(22, 0), time(6, 0), enabled=False, tenant_id=T)
        prefs = await manager.enable_quiet_hours("user1", T)
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
        prefs = await manager.add_time_rule("user1", rule, T)
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
        await manager.add_time_rule("user1", rule, T)
        prefs = await manager.remove_time_rule("user1", "rule1", T)
        assert all(r.id != "rule1" for r in prefs.time_rules)

    @pytest.mark.asyncio
    async def test_create_no_sms_at_night(self, manager):
        prefs = await manager.create_no_sms_at_night_rule("user1", tenant_id=T)
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
        prefs = await manager.set_urgency_override("user1", override, T)
        assert len(prefs.urgency_overrides) >= 1

    @pytest.mark.asyncio
    async def test_remove_urgency_override(self, manager):
        override = UrgencyOverride(
            urgency=AlertUrgency.CRITICAL,
            force_channels=[NotificationChannel.SMS],
        )
        await manager.set_urgency_override("user1", override, T)
        prefs = await manager.remove_urgency_override("user1", AlertUrgency.CRITICAL, T)
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
            T,
        )
        assert prefs.notifications_enabled is False
        assert prefs.sound_enabled is False
        assert prefs.language == Language.ENGLISH

    @pytest.mark.asyncio
    async def test_export_preferences(self, manager):
        await manager.get_preferences("user1", T)
        exported = await manager.export_preferences("user1", T)
        assert exported["user_id"] == "user1"

    @pytest.mark.asyncio
    async def test_export_nonexistent(self, manager):
        exported = await manager.export_preferences("nonexistent", T)
        assert exported == {}

    @pytest.mark.asyncio
    async def test_import_preferences(self, manager):
        original = create_default_preferences("user1", T)
        data = original.to_dict()
        imported = await manager.import_preferences("user2", data, T)
        assert imported.user_id == "user2"
        assert imported.tenant_id == T

    @pytest.mark.asyncio
    async def test_import_merge(self, manager):
        # Create existing preferences
        await manager.get_preferences("user1", T)
        # Import with merge
        new_data = create_default_preferences("other", T)
        new_data.channel_configs.append(
            ChannelConfig(channel=NotificationChannel.WHATSAPP, address="test"),
        )
        data = new_data.to_dict()
        merged = await manager.import_preferences("user1", data, T, merge=True)
        assert merged.user_id == "user1"


class TestValidation:
    @pytest.mark.asyncio
    async def test_validate_empty_user_id(self, manager):
        prefs = create_default_preferences("", T)
        with pytest.raises(ValueError, match="User ID"):
            await manager.save_preferences(prefs)

    @pytest.mark.asyncio
    async def test_validate_quiet_hours_same_time(self, manager):
        prefs = create_default_preferences("user1", T)
        prefs.quiet_hours = QuietHours(
            enabled=True,
            start_time=time(10, 0),
            end_time=time(10, 0),
        )
        with pytest.raises(ValueError, match="(?i)quiet hours"):
            await manager.save_preferences(prefs)
