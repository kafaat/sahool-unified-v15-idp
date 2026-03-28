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

import asyncio
from datetime import datetime, time
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

try:
    from src.preferences_service import PreferencesService
except BaseException as e:
    if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
        raise
    pytest.skip("notification-service dependencies not available", allow_module_level=True)


def _make_mock_preference(**overrides):
    pref = MagicMock()
    pref.id = overrides.get("id", uuid4())
    pref.user_id = overrides.get("user_id", "user-123")
    pref.event_type = overrides.get("event_type", "weather_alert")
    pref.channels = overrides.get("channels", ["push", "in_app"])
    pref.enabled = overrides.get("enabled", True)
    pref.quiet_hours_start = overrides.get("quiet_hours_start")
    pref.quiet_hours_end = overrides.get("quiet_hours_end")
    pref.metadata = overrides.get("metadata", {})
    pref.created_at = overrides.get("created_at", datetime(2026, 1, 1, 12, 0))
    pref.updated_at = overrides.get("updated_at", datetime(2026, 1, 2, 12, 0))
    return pref


class TestGetUserPreferences:
    def test_returns_formatted_preferences(self):
        mock_pref = _make_mock_preference()

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_user_preferences = AsyncMock(return_value=[mock_pref])
            result = asyncio.run(PreferencesService.get_user_preferences("user-123"))
            assert len(result) == 1
            assert result[0]["user_id"] == "user-123"
            assert result[0]["event_type"] == "weather_alert"
            assert result[0]["channels"] == ["push", "in_app"]
            assert result[0]["enabled"] is True

    def test_empty_list_when_no_preferences(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_user_preferences = AsyncMock(return_value=[])
            result = asyncio.run(PreferencesService.get_user_preferences("user-456"))
            assert result == []

    def test_with_quiet_hours(self):
        mock_pref = _make_mock_preference(
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(6, 0),
        )

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_user_preferences = AsyncMock(return_value=[mock_pref])
            result = asyncio.run(PreferencesService.get_user_preferences("user-123"))
            assert result[0]["quiet_hours_start"] == "22:00"
            assert result[0]["quiet_hours_end"] == "06:00"

    def test_raises_on_db_error(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_user_preferences = AsyncMock(side_effect=Exception("DB error"))
            with pytest.raises(Exception, match="DB error"):
                asyncio.run(PreferencesService.get_user_preferences("user-123"))

    def test_with_tenant_id(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_user_preferences = AsyncMock(return_value=[])
            asyncio.run(PreferencesService.get_user_preferences("user-123", tenant_id="tenant-1"))
            mock_repo.get_user_preferences.assert_called_once_with(user_id="user-123", tenant_id="tenant-1")


class TestUpdateEventPreference:
    def test_valid_update(self):
        mock_pref = _make_mock_preference(
            event_type="pest_outbreak",
            channels=["push"],
        )

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.create_or_update = AsyncMock(return_value=mock_pref)
            result = asyncio.run(
                PreferencesService.update_event_preference(
                    user_id="user-123",
                    event_type="pest_outbreak",
                    channels=["push"],
                )
            )
            assert result["event_type"] == "pest_outbreak"
            assert result["channels"] == ["push"]

    def test_invalid_channel_raises(self):
        with pytest.raises(ValueError, match="Invalid channel type"):
            asyncio.run(
                PreferencesService.update_event_preference(
                    user_id="user-123",
                    event_type="weather_alert",
                    channels=["invalid_channel"],
                )
            )

    def test_all_valid_channels(self):
        valid_channels = ["email", "sms", "push", "whatsapp", "in_app"]
        mock_pref = _make_mock_preference(channels=valid_channels)

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.create_or_update = AsyncMock(return_value=mock_pref)
            result = asyncio.run(
                PreferencesService.update_event_preference(
                    user_id="user-123",
                    event_type="weather_alert",
                    channels=valid_channels,
                )
            )
            assert result is not None


class TestSetQuietHours:
    def test_valid_quiet_hours(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.update_quiet_hours = AsyncMock(return_value=True)
            result = asyncio.run(
                PreferencesService.set_quiet_hours(
                    user_id="user-123",
                    quiet_hours_start="22:00",
                    quiet_hours_end="06:00",
                )
            )
            assert result["success"] is True
            assert result["quiet_hours_start"] == "22:00"
            assert result["quiet_hours_end"] == "06:00"

    def test_no_preferences_found(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.update_quiet_hours = AsyncMock(return_value=False)
            result = asyncio.run(
                PreferencesService.set_quiet_hours(
                    user_id="user-123",
                    quiet_hours_start="22:00",
                    quiet_hours_end="06:00",
                )
            )
            assert result["success"] is False

    def test_invalid_start_time(self):
        with pytest.raises(ValueError, match="Invalid time format"):
            asyncio.run(
                PreferencesService.set_quiet_hours(
                    user_id="user-123",
                    quiet_hours_start="25:00",
                )
            )

    def test_invalid_end_time(self):
        with pytest.raises(ValueError, match="Invalid time format"):
            asyncio.run(
                PreferencesService.set_quiet_hours(
                    user_id="user-123",
                    quiet_hours_end="12:99",
                )
            )

    def test_invalid_format_non_numeric(self):
        with pytest.raises(ValueError, match="Invalid time format"):
            asyncio.run(
                PreferencesService.set_quiet_hours(
                    user_id="user-123",
                    quiet_hours_start="abc",
                )
            )

    def test_none_quiet_hours(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.update_quiet_hours = AsyncMock(return_value=True)
            result = asyncio.run(PreferencesService.set_quiet_hours(user_id="user-123"))
            assert result["success"] is True


class TestBulkUpdatePreferences:
    def test_bulk_update(self):
        mock_prefs = [
            _make_mock_preference(event_type="weather_alert", channels=["push"]),
            _make_mock_preference(event_type="pest_outbreak", channels=["sms"]),
        ]

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.create_or_update = AsyncMock(side_effect=mock_prefs)
            result = asyncio.run(
                PreferencesService.bulk_update_preferences(
                    user_id="user-123",
                    preferences=[
                        {"event_type": "weather_alert", "channels": ["push"]},
                        {"event_type": "pest_outbreak", "channels": ["sms"]},
                    ],
                )
            )
            assert result["success"] is True
            assert result["updated_count"] == 2
            assert len(result["preferences"]) == 2

    def test_skips_missing_event_type(self):
        mock_pref = _make_mock_preference()

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.create_or_update = AsyncMock(return_value=mock_pref)
            result = asyncio.run(
                PreferencesService.bulk_update_preferences(
                    user_id="user-123",
                    preferences=[
                        {"channels": ["push"]},  # Missing event_type
                        {"event_type": "weather_alert", "channels": ["push"]},
                    ],
                )
            )
            assert result["updated_count"] == 1

    def test_empty_list(self):
        result = asyncio.run(
            PreferencesService.bulk_update_preferences(
                user_id="user-123",
                preferences=[],
            )
        )
        assert result["success"] is True
        assert result["updated_count"] == 0

    def test_raises_on_db_error(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.create_or_update = AsyncMock(side_effect=Exception("DB error"))
            with pytest.raises(Exception):
                asyncio.run(
                    PreferencesService.bulk_update_preferences(
                        user_id="user-123",
                        preferences=[{"event_type": "weather_alert", "channels": ["push"]}],
                    )
                )


class TestGetEventPreference:
    def test_found(self):
        mock_pref = _make_mock_preference()

        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_event_preference = AsyncMock(return_value=mock_pref)
            result = asyncio.run(PreferencesService.get_event_preference("user-123", "weather_alert"))
            assert result is not None
            assert result["event_type"] == "weather_alert"

    def test_not_found(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_event_preference = AsyncMock(return_value=None)
            result = asyncio.run(PreferencesService.get_event_preference("user-123", "unknown_type"))
            assert result is None

    def test_raises_on_error(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.get_event_preference = AsyncMock(side_effect=Exception("DB"))
            with pytest.raises(Exception):
                asyncio.run(PreferencesService.get_event_preference("user-123", "weather_alert"))


class TestCheckIfShouldSend:
    def test_enabled_with_channels(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.is_event_enabled = AsyncMock(return_value=True)
            mock_repo.get_preferred_channels = AsyncMock(return_value=["push", "sms"])
            should_send, channels = asyncio.run(PreferencesService.check_if_should_send("user-123", "weather_alert"))
            assert should_send is True
            assert channels == ["push", "sms"]

    def test_disabled_event(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.is_event_enabled = AsyncMock(return_value=False)
            should_send, channels = asyncio.run(PreferencesService.check_if_should_send("user-123", "market_price"))
            assert should_send is False
            assert channels == []

    def test_default_channels_when_none_set(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.is_event_enabled = AsyncMock(return_value=True)
            mock_repo.get_preferred_channels = AsyncMock(return_value=[])
            should_send, channels = asyncio.run(PreferencesService.check_if_should_send("user-123", "weather_alert"))
            assert should_send is True
            assert channels == ["in_app", "push"]

    def test_error_defaults_to_allow(self):
        with patch("src.preferences_service.NotificationPreferenceRepository") as mock_repo:
            mock_repo.is_event_enabled = AsyncMock(side_effect=Exception("DB error"))
            should_send, channels = asyncio.run(PreferencesService.check_if_should_send("user-123", "weather_alert"))
            assert should_send is True
            assert channels == ["in_app"]
