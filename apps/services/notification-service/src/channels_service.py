"""
SAHOOL Notification Service - Channels Service
خدمة قنوات الإشعارات - Business Logic Layer

Handles business logic for managing user notification channels
"""

import logging
import random
import string
from typing import Any
from uuid import UUID

from .models import ChannelType
from .repository import NotificationChannelRepository

logger = logging.getLogger("sahool-notifications.channels-service")


class ChannelsService:
    """
    خدمة إدارة قنوات الإشعارات
    Service for managing notification channels
    """

    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """Generate a random verification code"""
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    async def add_channel(
        user_id: str,
        channel_type: str,
        address: str,
        tenant_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        إضافة قناة إشعار جديدة
        Add a new notification channel for a user

        Args:
            user_id: User ID
            channel_type: Channel type (email, sms, push, whatsapp, in_app)
            address: Channel address (email, phone, token, etc.)
            tenant_id: Optional tenant ID
            metadata: Optional metadata

        Returns:
            Dictionary with channel information
        """
        try:
            # Validate channel type
            try:
                channel_enum = ChannelType(channel_type)
            except ValueError:
                raise ValueError(f"Invalid channel type: {channel_type}")

            # Determine if verification is needed
            needs_verification = channel_type in [
                ChannelType.EMAIL,
                ChannelType.SMS,
                ChannelType.WHATSAPP,
            ]
            verification_code = None

            if needs_verification:
                verification_code = ChannelsService.generate_verification_code()

            # Create channel
            channel = await NotificationChannelRepository.create(
                user_id=user_id,
                channel=channel_enum,
                address=address,
                tenant_id=tenant_id,
                verified=not needs_verification,  # Push and in-app don't need verification
                enabled=True,
                metadata=metadata or {},
            )

            # Store verification code if needed
            if needs_verification and verification_code:
                await NotificationChannelRepository.update_channel(
                    channel.id,
                    verification_code=verification_code,
                )

            logger.info(f"Added channel {channel_type} for user {user_id}")

            return {
                "id": str(channel.id),
                "user_id": channel.user_id,
                "channel": channel.channel.value,
                "address": channel.address,
                "verified": channel.verified,
                "enabled": channel.enabled,
                "created_at": channel.created_at.isoformat(),
                "verification_required": needs_verification,
                "verification_code": verification_code if needs_verification else None,
            }

        except Exception as e:
            logger.error(f"Error adding channel: {e}")
            raise

    @staticmethod
    async def verify_channel(
        channel_id: str,
        verification_code: str,
        user_id: str,
    ) -> dict[str, Any]:
        """
        تحقق من قناة إشعار
        Verify a notification channel

        Args:
            channel_id: Channel ID
            verification_code: Verification code
            user_id: User ID (for security check)

        Returns:
            Dictionary with verification result
        """
        try:
            channel_uuid = UUID(channel_id)

            # Get channel
            channel = await NotificationChannelRepository.get_by_id(channel_uuid)

            if not channel:
                raise ValueError("Channel not found")

            if channel.user_id != user_id:
                raise ValueError("Unauthorized: Channel does not belong to user")

            if channel.verified:
                return {
                    "success": True,
                    "message": "Channel already verified",
                    "verified": True,
                }

            # Verify channel
            success = await NotificationChannelRepository.verify_channel(
                channel_uuid,
                verification_code=verification_code,
            )

            if success:
                logger.info(f"Verified channel {channel_id} for user {user_id}")
                return {
                    "success": True,
                    "message": "Channel verified successfully",
                    "verified": True,
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid verification code",
                    "verified": False,
                }

        except ValueError as e:
            logger.warning(f"Verification failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error verifying channel: {e}")
            raise

    @staticmethod
    async def remove_channel(
        channel_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        """
        حذف قناة إشعار
        Remove a notification channel

        Args:
            channel_id: Channel ID
            user_id: User ID (for security check)

        Returns:
            Dictionary with removal result
        """
        try:
            channel_uuid = UUID(channel_id)

            # Get channel to verify ownership
            channel = await NotificationChannelRepository.get_by_id(channel_uuid)

            if not channel:
                raise ValueError("Channel not found")

            if channel.user_id != user_id:
                raise ValueError("Unauthorized: Channel does not belong to user")

            # Delete channel
            success = await NotificationChannelRepository.delete_channel(channel_uuid)

            if success:
                logger.info(f"Removed channel {channel_id} for user {user_id}")
                return {
                    "success": True,
                    "message": "Channel removed successfully",
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to remove channel",
                }

        except ValueError as e:
            logger.warning(f"Remove channel failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error removing channel: {e}")
            raise

    @staticmethod
    async def list_user_channels(
        user_id: str,
        tenant_id: str | None = None,
        channel_type: str | None = None,
        enabled_only: bool = False,
    ) -> list[dict[str, Any]]:
        """
        الحصول على قنوات المستخدم
        Get user's notification channels

        Args:
            user_id: User ID
            tenant_id: Optional tenant ID
            channel_type: Optional channel type filter
            enabled_only: Whether to return only enabled channels

        Returns:
            List of channel dictionaries
        """
        try:
            # Parse channel type if provided
            channel_enum = None
            if channel_type:
                try:
                    channel_enum = ChannelType(channel_type)
                except ValueError:
                    raise ValueError(f"Invalid channel type: {channel_type}")

            # Get channels
            channels = await NotificationChannelRepository.get_user_channels(
                user_id=user_id,
                tenant_id=tenant_id,
                channel_type=channel_enum,
                enabled_only=enabled_only,
            )

            # Format response
            result = [
                {
                    "id": str(channel.id),
                    "channel": channel.channel.value,
                    "address": channel.address,
                    "verified": channel.verified,
                    "verified_at": (
                        channel.verified_at.isoformat() if channel.verified_at else None
                    ),
                    "enabled": channel.enabled,
                    "metadata": channel.metadata,
                    "created_at": channel.created_at.isoformat(),
                    "updated_at": channel.updated_at.isoformat(),
                }
                for channel in channels
            ]

            logger.info(f"Retrieved {len(result)} channels for user {user_id}")
            return result

        except Exception as e:
            logger.error(f"Error listing channels: {e}")
            raise

    @staticmethod
    async def update_channel_status(
        channel_id: str,
        user_id: str,
        enabled: bool,
    ) -> dict[str, Any]:
        """
        تحديث حالة قناة
        Update channel enabled/disabled status

        Args:
            channel_id: Channel ID
            user_id: User ID (for security check)
            enabled: Whether channel should be enabled

        Returns:
            Dictionary with update result
        """
        try:
            channel_uuid = UUID(channel_id)

            # Get channel to verify ownership
            channel = await NotificationChannelRepository.get_by_id(channel_uuid)

            if not channel:
                raise ValueError("Channel not found")

            if channel.user_id != user_id:
                raise ValueError("Unauthorized: Channel does not belong to user")

            # Update channel
            success = await NotificationChannelRepository.update_channel(
                channel_uuid,
                enabled=enabled,
            )

            if success:
                logger.info(f"Updated channel {channel_id} status to {enabled}")
                return {
                    "success": True,
                    "message": f"Channel {'enabled' if enabled else 'disabled'} successfully",
                    "enabled": enabled,
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to update channel status",
                }

        except ValueError as e:
            logger.warning(f"Update channel status failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating channel status: {e}")
            raise
