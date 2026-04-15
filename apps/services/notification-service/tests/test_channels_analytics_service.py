"""
Tests for src/channels_service.py and src/analytics_service.py

Covers:
- ChannelsService.generate_verification_code
- ChannelsService.add_channel validation
- NotificationAnalytics TimeRange enum
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from src.analytics_service import TimeRange
    from src.channels_service import ChannelsService
    from src.models import ChannelType
except BaseException as e:
    if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
        raise
    pytest.skip("notification-service dependencies not available", allow_module_level=True)


# ─────────────────────────────────────────────────────────────────────────────
# TimeRange Enum
# ─────────────────────────────────────────────────────────────────────────────


class TestTimeRange:
    def test_all_values(self):
        assert TimeRange.HOUR == "hour"
        assert TimeRange.DAY == "day"
        assert TimeRange.WEEK == "week"
        assert TimeRange.MONTH == "month"
        assert TimeRange.QUARTER == "quarter"
        assert TimeRange.YEAR == "year"


# ─────────────────────────────────────────────────────────────────────────────
# ChannelsService
# ─────────────────────────────────────────────────────────────────────────────


class TestGenerateVerificationCode:
    def test_default_length_6(self):
        code = ChannelsService.generate_verification_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_custom_length(self):
        code = ChannelsService.generate_verification_code(length=8)
        assert len(code) == 8
        assert code.isdigit()

    def test_unique_codes(self):
        codes = set()
        for _ in range(100):
            codes.add(ChannelsService.generate_verification_code())
        # With 6-digit codes, 100 attempts should yield mostly unique codes
        assert len(codes) > 90


class TestAddChannel:
    def test_invalid_channel_type_raises(self):
        with pytest.raises(ValueError, match="Invalid channel type"):
            asyncio.run(
                ChannelsService.add_channel(
                    user_id="user-123",
                    channel_type="invalid_channel",
                    address="test@example.com",
                )
            )

    def test_valid_push_channel(self):
        mock_channel = MagicMock()
        mock_channel.id = "ch-1"
        mock_channel.user_id = "user-123"
        mock_channel.channel = ChannelType.PUSH
        mock_channel.address = "fcm-token-123"
        mock_channel.verified = True
        mock_channel.enabled = True
        mock_channel.metadata = {}
        mock_channel.created_at = MagicMock()
        mock_channel.created_at.isoformat.return_value = "2026-01-01T00:00:00"

        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.create = AsyncMock(return_value=mock_channel)
            result = asyncio.run(
                ChannelsService.add_channel(
                    user_id="user-123",
                    channel_type="push",
                    address="fcm-token-123",
                )
            )
            assert result["channel"] == "push"
            assert result["verified"] is True

    def test_email_channel_needs_verification(self):
        mock_channel = MagicMock()
        mock_channel.id = "ch-2"
        mock_channel.user_id = "user-123"
        mock_channel.channel = ChannelType.EMAIL
        mock_channel.address = "test@example.com"
        mock_channel.verified = False
        mock_channel.enabled = True
        mock_channel.metadata = {}
        mock_channel.created_at = MagicMock()
        mock_channel.created_at.isoformat.return_value = "2026-01-01T00:00:00"

        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.create = AsyncMock(return_value=mock_channel)
            mock_repo.update_channel = AsyncMock(return_value=True)
            result = asyncio.run(
                ChannelsService.add_channel(
                    user_id="user-123",
                    channel_type="email",
                    address="test@example.com",
                )
            )
            assert result["verified"] is False
            assert "verification_code" in result
