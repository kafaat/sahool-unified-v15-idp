"""
Tests for src/preferences_service.py - Preferences Service Business Logic

Covers:
- PreferencesService.get_user_preferences
- PreferencesService.update_event_preference
- PreferencesService.set_quiet_hours
- PreferencesService.bulk_update_preferences
- PreferencesService.get_event_preference
- PreferencesService.check_if_should_send
"""

import pytest
from datetime import datetime, time
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from src.preferences_service import PreferencesService


def _make_mock_preference(**overrides):
    pref = MagicMock()
    pref.id = overrides.get("id", uuid4())
    pref.user_id = overrides.get("user_id", "user-123")
    pref.event_type = overrides.get("event_type", "weather_alert")
    pref.channels = overrides.get("channels", ["push", "in_app"])
    pref.enabled = overrides.get("enabled", True)
    pref.quiet_hours_start = overrides.get("quiet_hours_start", None)
    pref.quiet_hours_end = overrides.get("quiet_hours_end", None)
    pref.metadata = overrides.get("metadata", {})
    pref.created_at = overrides.get("created_at", datetime(2026, 1, 1, 12, 0))
    pref.updated_at = overrides.get("updated_at", datetime(2026, 1, 2, 12, 0))
    return pref


class TestGetUserPreferences:
    @pytest.mark.asyncio
    async def test_returns_formatted_preferences(self):
        mock_pref = _make_mock_preference()

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_user_preferences = AsyncMock(return_value=[mock_pref])
            result = await PreferencesService.get_user_preferences("user-123")
            assert len(result) == 1
            assert result[0]["user_id"] == "user-123"
            assert result[0]["event_type"] == "weather_alert"
            assert result[0]["channels"] == ["push", "in_app"]
            assert result[0]["enabled"] is True

    @pytest.mark.asyncio
    async def test_empty_list_when_no_preferences(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_user_preferences = AsyncMock(return_value=[])
            result = await PreferencesService.get_user_preferences("user-456")
            assert result == []

    @pytest.mark.asyncio
    async def test_with_quiet_hours(self):
        mock_pref = _make_mock_preference(
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(6, 0),
        )

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_user_preferences = AsyncMock(return_value=[mock_pref])
            result = await PreferencesService.get_user_preferences("user-123")
            assert result[0]["quiet_hours_start"] == "22:00"
            assert result[0]["quiet_hours_end"] == "06:00"

    @pytest.mark.asyncio
    async def test_raises_on_db_error(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_user_preferences = AsyncMock(side_effect=Exception("DB error"))
            with pytest.raises(Exception, match="DB error"):
                await PreferencesService.get_user_preferences("user-123")

    @pytest.mark.asyncio
    async def test_with_tenant_id(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_user_preferences = AsyncMock(return_value=[])
            await PreferencesService.get_user_preferences("user-123", tenant_id="tenant-1")
            mock_repo.get_user_preferences.assert_called_once_with(
                user_id="user-123", tenant_id="tenant-1"
            )


class TestUpdateEventPreference:
    @pytest.mark.asyncio
    async def test_valid_update(self):
        mock_pref = _make_mock_preference(
            event_type="pest_outbreak",
            channels=["push"],
        )

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.create_or_update = AsyncMock(return_value=mock_pref)
            result = await PreferencesService.update_event_preference(
                user_id="user-123",
                event_type="pest_outbreak",
                channels=["push"],
            )
            assert result["event_type"] == "pest_outbreak"
            assert result["channels"] == ["push"]

    @pytest.mark.asyncio
    async def test_invalid_channel_raises(self):
        with pytest.raises(ValueError, match="Invalid channel type"):
            await PreferencesService.update_event_preference(
                user_id="user-123",
                event_type="weather_alert",
                channels=["invalid_channel"],
            )

    @pytest.mark.asyncio
    async def test_all_valid_channels(self):
        valid_channels = ["email", "sms", "push", "whatsapp", "in_app"]
        mock_pref = _make_mock_preference(channels=valid_channels)

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.create_or_update = AsyncMock(return_value=mock_pref)
            result = await PreferencesService.update_event_preference(
                user_id="user-123",
                event_type="weather_alert",
                channels=valid_channels,
            )
            assert result is not None


class TestSetQuietHours:
    @pytest.mark.asyncio
    async def test_valid_quiet_hours(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.update_quiet_hours = AsyncMock(return_value=True)
            result = await PreferencesService.set_quiet_hours(
                user_id="user-123",
                quiet_hours_start="22:00",
                quiet_hours_end="06:00",
            )
            assert result["success"] is True
            assert result["quiet_hours_start"] == "22:00"
            assert result["quiet_hours_end"] == "06:00"

    @pytest.mark.asyncio
    async def test_no_preferences_found(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.update_quiet_hours = AsyncMock(return_value=False)
            result = await PreferencesService.set_quiet_hours(
                user_id="user-123",
                quiet_hours_start="22:00",
                quiet_hours_end="06:00",
            )
            assert result["success"] is False

    @pytest.mark.asyncio
    async def test_invalid_start_time(self):
        with pytest.raises(ValueError, match="Invalid time format"):
            await PreferencesService.set_quiet_hours(
                user_id="user-123",
                quiet_hours_start="25:00",
            )

    @pytest.mark.asyncio
    async def test_invalid_end_time(self):
        with pytest.raises(ValueError, match="Invalid time format"):
            await PreferencesService.set_quiet_hours(
                user_id="user-123",
                quiet_hours_end="12:99",
            )

    @pytest.mark.asyncio
    async def test_invalid_format_non_numeric(self):
        with pytest.raises(ValueError, match="Invalid time format"):
            await PreferencesService.set_quiet_hours(
                user_id="user-123",
                quiet_hours_start="abc",
            )

    @pytest.mark.asyncio
    async def test_none_quiet_hours(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.update_quiet_hours = AsyncMock(return_value=True)
            result = await PreferencesService.set_quiet_hours(user_id="user-123")
            assert result["success"] is True


class TestBulkUpdatePreferences:
    @pytest.mark.asyncio
    async def test_bulk_update(self):
        mock_prefs = [
            _make_mock_preference(event_type="weather_alert", channels=["push"]),
            _make_mock_preference(event_type="pest_outbreak", channels=["sms"]),
        ]

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.create_or_update = AsyncMock(side_effect=mock_prefs)
            result = await PreferencesService.bulk_update_preferences(
                user_id="user-123",
                preferences=[
                    {"event_type": "weather_alert", "channels": ["push"]},
                    {"event_type": "pest_outbreak", "channels": ["sms"]},
                ],
            )
            assert result["success"] is True
            assert result["updated_count"] == 2
            assert len(result["preferences"]) == 2

    @pytest.mark.asyncio
    async def test_skips_missing_event_type(self):
        mock_pref = _make_mock_preference()

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.create_or_update = AsyncMock(return_value=mock_pref)
            result = await PreferencesService.bulk_update_preferences(
                user_id="user-123",
                preferences=[
                    {"channels": ["push"]},  # Missing event_type
                    {"event_type": "weather_alert", "channels": ["push"]},
                ],
            )
            assert result["updated_count"] == 1

    @pytest.mark.asyncio
    async def test_empty_list(self):
        result = await PreferencesService.bulk_update_preferences(
            user_id="user-123",
            preferences=[],
        )
        assert result["success"] is True
        assert result["updated_count"] == 0

    @pytest.mark.asyncio
    async def test_raises_on_db_error(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.create_or_update = AsyncMock(side_effect=Exception("DB error"))
            with pytest.raises(Exception):
                await PreferencesService.bulk_update_preferences(
                    user_id="user-123",
                    preferences=[{"event_type": "weather_alert", "channels": ["push"]}],
                )


class TestGetEventPreference:
    @pytest.mark.asyncio
    async def test_found(self):
        mock_pref = _make_mock_preference()

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_event_preference = AsyncMock(return_value=mock_pref)
            result = await PreferencesService.get_event_preference("user-123", "weather_alert")
            assert result is not None
            assert result["event_type"] == "weather_alert"

    @pytest.mark.asyncio
    async def test_not_found(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_event_preference = AsyncMock(return_value=None)
            result = await PreferencesService.get_event_preference("user-123", "unknown_type")
            assert result is None

    @pytest.mark.asyncio
    async def test_raises_on_error(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_event_preference = AsyncMock(side_effect=Exception("DB"))
            with pytest.raises(Exception):
                await PreferencesService.get_event_preference("user-123", "weather_alert")


class TestCheckIfShouldSend:
    @pytest.mark.asyncio
    async def test_enabled_with_channels(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.is_event_enabled = AsyncMock(return_value=True)
            mock_repo.get_preferred_channels = AsyncMock(return_value=["push", "sms"])
            should_send, channels = await PreferencesService.check_if_should_send(
                "user-123", "weather_alert"
            )
            assert should_send is True
            assert channels == ["push", "sms"]

    @pytest.mark.asyncio
    async def test_disabled_event(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.is_event_enabled = AsyncMock(return_value=False)
            should_send, channels = await PreferencesService.check_if_should_send(
                "user-123", "market_price"
            )
            assert should_send is False
            assert channels == []

    @pytest.mark.asyncio
    async def test_default_channels_when_none_set(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.is_event_enabled = AsyncMock(return_value=True)
            mock_repo.get_preferred_channels = AsyncMock(return_value=[])
            should_send, channels = await PreferencesService.check_if_should_send(
                "user-123", "weather_alert"
            )
            assert should_send is True
            assert channels == ["in_app", "push"]

    @pytest.mark.asyncio
    async def test_error_defaults_to_allow(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.is_event_enabled = AsyncMock(side_effect=Exception("DB error"))
            should_send, channels = await PreferencesService.check_if_should_send(
                "user-123", "weather_alert"
            )
            assert should_send is True
            assert channels == ["in_app"]
