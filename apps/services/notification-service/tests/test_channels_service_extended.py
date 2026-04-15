"""
Tests for src/channels_service.py - Extended Coverage

Covers:
- ChannelsService.verify_channel
- ChannelsService.remove_channel
- ChannelsService.list_user_channels
- ChannelsService.update_channel_status
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

try:
    from src.channels_service import ChannelsService
    from src.models import ChannelType
except BaseException as e:
    if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
        raise
    pytest.skip("notification-service dependencies not available", allow_module_level=True)


def _mock_channel(**overrides):
    ch = MagicMock()
    ch.id = overrides.get("id", uuid4())
    ch.user_id = overrides.get("user_id", "user-123")
    ch.channel = overrides.get("channel", ChannelType.PUSH)
    ch.address = overrides.get("address", "token-abc")
    ch.verified = overrides.get("verified", True)
    ch.verified_at = overrides.get("verified_at")
    ch.enabled = overrides.get("enabled", True)
    ch.metadata = overrides.get("metadata", {})
    ch.created_at = MagicMock()
    ch.created_at.isoformat.return_value = "2026-01-01T00:00:00"
    ch.updated_at = MagicMock()
    ch.updated_at.isoformat.return_value = "2026-01-02T00:00:00"
    return ch


class TestVerifyChannel:
    def test_channel_not_found(self):
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=None)
            with pytest.raises(ValueError, match="not found"):
                asyncio.run(ChannelsService.verify_channel(str(uuid4()), "123456", "user-123"))

    def test_unauthorized_user(self):
        ch = _mock_channel(user_id="other-user")
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            with pytest.raises(ValueError, match="Unauthorized"):
                asyncio.run(ChannelsService.verify_channel(str(ch.id), "123456", "user-123"))

    def test_already_verified(self):
        ch = _mock_channel(verified=True)
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            result = asyncio.run(ChannelsService.verify_channel(str(ch.id), "123456", "user-123"))
            assert result["success"] is True
            assert result["message"] == "Channel already verified"

    def test_successful_verification(self):
        ch = _mock_channel(verified=False)
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            mock_repo.verify_channel = AsyncMock(return_value=True)
            result = asyncio.run(ChannelsService.verify_channel(str(ch.id), "123456", "user-123"))
            assert result["success"] is True
            assert result["verified"] is True

    def test_failed_verification(self):
        ch = _mock_channel(verified=False)
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            mock_repo.verify_channel = AsyncMock(return_value=False)
            result = asyncio.run(ChannelsService.verify_channel(str(ch.id), "wrong-code", "user-123"))
            assert result["success"] is False


class TestRemoveChannel:
    def test_channel_not_found(self):
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=None)
            with pytest.raises(ValueError, match="not found"):
                asyncio.run(ChannelsService.remove_channel(str(uuid4()), "user-123"))

    def test_unauthorized(self):
        ch = _mock_channel(user_id="other-user")
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            with pytest.raises(ValueError, match="Unauthorized"):
                asyncio.run(ChannelsService.remove_channel(str(ch.id), "user-123"))

    def test_successful_removal(self):
        ch = _mock_channel()
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            mock_repo.delete_channel = AsyncMock(return_value=True)
            result = asyncio.run(ChannelsService.remove_channel(str(ch.id), "user-123"))
            assert result["success"] is True

    def test_failed_removal(self):
        ch = _mock_channel()
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            mock_repo.delete_channel = AsyncMock(return_value=False)
            result = asyncio.run(ChannelsService.remove_channel(str(ch.id), "user-123"))
            assert result["success"] is False


class TestListUserChannels:
    def test_list_all_channels(self):
        ch1 = _mock_channel(channel=ChannelType.PUSH, address="token-1")
        ch2 = _mock_channel(channel=ChannelType.EMAIL, address="test@example.com")
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_user_channels = AsyncMock(return_value=[ch1, ch2])
            result = asyncio.run(ChannelsService.list_user_channels("user-123"))
            assert len(result) == 2

    def test_list_empty(self):
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_user_channels = AsyncMock(return_value=[])
            result = asyncio.run(ChannelsService.list_user_channels("user-123"))
            assert result == []

    def test_invalid_channel_type(self):
        with pytest.raises(ValueError, match="Invalid channel type"):
            asyncio.run(ChannelsService.list_user_channels("user-123", channel_type="invalid"))


class TestUpdateChannelStatus:
    def test_enable_channel(self):
        ch = _mock_channel()
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            mock_repo.update_channel = AsyncMock(return_value=True)
            result = asyncio.run(ChannelsService.update_channel_status(str(ch.id), "user-123", True))
            assert result["success"] is True
            assert result["enabled"] is True

    def test_disable_channel(self):
        ch = _mock_channel()
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            mock_repo.update_channel = AsyncMock(return_value=True)
            result = asyncio.run(ChannelsService.update_channel_status(str(ch.id), "user-123", False))
            assert result["success"] is True
            assert "disabled" in result["message"]

    def test_channel_not_found(self):
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=None)
            with pytest.raises(ValueError, match="not found"):
                asyncio.run(ChannelsService.update_channel_status(str(uuid4()), "user-123", True))

    def test_unauthorized(self):
        ch = _mock_channel(user_id="other-user")
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            with pytest.raises(ValueError, match="Unauthorized"):
                asyncio.run(ChannelsService.update_channel_status(str(ch.id), "user-123", True))

    def test_update_failed(self):
        ch = _mock_channel()
        with patch("src.channels_service.NotificationChannelRepository") as mock_repo:
            mock_repo.get_by_id = AsyncMock(return_value=ch)
            mock_repo.update_channel = AsyncMock(return_value=False)
            result = asyncio.run(ChannelsService.update_channel_status(str(ch.id), "user-123", True))
            assert result["success"] is False
