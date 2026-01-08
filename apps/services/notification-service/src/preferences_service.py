"""
SAHOOL Notification Service - Preferences Service
خدمة تفضيلات الإشعارات - Business Logic Layer

Handles business logic for managing user notification preferences
"""

import logging
from typing import Any

from .repository import NotificationPreferenceRepository

logger = logging.getLogger("sahool-notifications.preferences-service")


class PreferencesService:
    """
    خدمة إدارة تفضيلات الإشعارات
    Service for managing notification preferences
    """

    @staticmethod
    async def get_user_preferences(
        user_id: str,
        tenant_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        الحصول على تفضيلات المستخدم
        Get all notification preferences for a user

        Args:
            user_id: User ID
            tenant_id: Optional tenant ID

        Returns:
            List of preference dictionaries
        """
        try:
            preferences = await NotificationPreferenceRepository.get_user_preferences(
                user_id=user_id,
                tenant_id=tenant_id,
            )

            result = [
                {
                    "id": str(pref.id),
                    "user_id": pref.user_id,
                    "event_type": pref.event_type,
                    "channels": pref.channels or [],
                    "enabled": pref.enabled,
                    "quiet_hours_start": (
                        pref.quiet_hours_start.strftime("%H:%M") if pref.quiet_hours_start else None
                    ),
                    "quiet_hours_end": (
                        pref.quiet_hours_end.strftime("%H:%M") if pref.quiet_hours_end else None
                    ),
                    "metadata": pref.metadata,
                    "created_at": pref.created_at.isoformat(),
                    "updated_at": pref.updated_at.isoformat(),
                }
                for pref in preferences
            ]

            logger.info(f"Retrieved {len(result)} preferences for user {user_id}")
            return result

        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            raise

    @staticmethod
    async def update_event_preference(
        user_id: str,
        event_type: str,
        channels: list[str],
        enabled: bool = True,
        tenant_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        تحديث تفضيلات نوع حدث معين
        Update preferences for a specific event type

        Args:
            user_id: User ID
            event_type: Event type (weather_alert, pest_outbreak, etc.)
            channels: List of channel types to use for this event
            enabled: Whether this event type is enabled
            tenant_id: Optional tenant ID
            metadata: Optional metadata

        Returns:
            Dictionary with updated preference
        """
        try:
            # Validate channels
            valid_channels = ["email", "sms", "push", "whatsapp", "in_app"]
            for channel in channels:
                if channel not in valid_channels:
                    raise ValueError(f"Invalid channel type: {channel}")

            # Create or update preference
            preference = await NotificationPreferenceRepository.create_or_update(
                user_id=user_id,
                event_type=event_type,
                channels=channels,
                enabled=enabled,
                tenant_id=tenant_id,
                metadata=metadata,
            )

            logger.info(f"Updated preference for user {user_id}, event {event_type}")

            return {
                "id": str(preference.id),
                "user_id": preference.user_id,
                "event_type": preference.event_type,
                "channels": preference.channels,
                "enabled": preference.enabled,
                "quiet_hours_start": (
                    preference.quiet_hours_start.strftime("%H:%M")
                    if preference.quiet_hours_start
                    else None
                ),
                "quiet_hours_end": (
                    preference.quiet_hours_end.strftime("%H:%M")
                    if preference.quiet_hours_end
                    else None
                ),
                "metadata": preference.metadata,
                "updated_at": preference.updated_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error updating event preference: {e}")
            raise

    @staticmethod
    async def set_quiet_hours(
        user_id: str,
        quiet_hours_start: str | None = None,
        quiet_hours_end: str | None = None,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        تحديد ساعات الهدوء
        Set quiet hours for all user preferences

        Args:
            user_id: User ID
            quiet_hours_start: Start time in HH:MM format (e.g., "22:00")
            quiet_hours_end: End time in HH:MM format (e.g., "06:00")
            tenant_id: Optional tenant ID

        Returns:
            Dictionary with update result
        """
        try:
            # Validate time format
            if quiet_hours_start:
                try:
                    hour, minute = map(int, quiet_hours_start.split(":"))
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        raise ValueError
                except (ValueError, AttributeError):
                    raise ValueError(
                        f"Invalid time format for quiet_hours_start: {quiet_hours_start}. Expected HH:MM"
                    )

            if quiet_hours_end:
                try:
                    hour, minute = map(int, quiet_hours_end.split(":"))
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        raise ValueError
                except (ValueError, AttributeError):
                    raise ValueError(
                        f"Invalid time format for quiet_hours_end: {quiet_hours_end}. Expected HH:MM"
                    )

            # Update quiet hours
            success = await NotificationPreferenceRepository.update_quiet_hours(
                user_id=user_id,
                quiet_hours_start=quiet_hours_start,
                quiet_hours_end=quiet_hours_end,
                tenant_id=tenant_id,
            )

            if success:
                logger.info(f"Updated quiet hours for user {user_id}")
                return {
                    "success": True,
                    "message": "Quiet hours updated successfully",
                    "quiet_hours_start": quiet_hours_start,
                    "quiet_hours_end": quiet_hours_end,
                }
            else:
                return {
                    "success": False,
                    "message": "No preferences found to update",
                }

        except ValueError as e:
            logger.warning(f"Invalid quiet hours: {e}")
            raise
        except Exception as e:
            logger.error(f"Error setting quiet hours: {e}")
            raise

    @staticmethod
    async def bulk_update_preferences(
        user_id: str,
        preferences: list[dict[str, Any]],
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        تحديث تفضيلات متعددة دفعة واحدة
        Bulk update multiple preferences

        Args:
            user_id: User ID
            preferences: List of preference dictionaries
            tenant_id: Optional tenant ID

        Returns:
            Dictionary with update results
        """
        try:
            updated_count = 0
            updated_prefs = []

            for pref_data in preferences:
                event_type = pref_data.get("event_type")
                channels = pref_data.get("channels", [])
                enabled = pref_data.get("enabled", True)
                metadata = pref_data.get("metadata")

                if not event_type:
                    logger.warning("Skipping preference without event_type")
                    continue

                pref = await NotificationPreferenceRepository.create_or_update(
                    user_id=user_id,
                    event_type=event_type,
                    channels=channels,
                    enabled=enabled,
                    tenant_id=tenant_id,
                    metadata=metadata,
                )

                updated_prefs.append(
                    {
                        "event_type": pref.event_type,
                        "channels": pref.channels,
                        "enabled": pref.enabled,
                    }
                )
                updated_count += 1

            logger.info(f"Bulk updated {updated_count} preferences for user {user_id}")

            return {
                "success": True,
                "message": f"Updated {updated_count} preferences",
                "updated_count": updated_count,
                "preferences": updated_prefs,
            }

        except Exception as e:
            logger.error(f"Error in bulk update preferences: {e}")
            raise

    @staticmethod
    async def get_event_preference(
        user_id: str,
        event_type: str,
        tenant_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        الحصول على تفضيلات نوع حدث معين
        Get preference for a specific event type

        Args:
            user_id: User ID
            event_type: Event type
            tenant_id: Optional tenant ID

        Returns:
            Preference dictionary or None
        """
        try:
            preference = await NotificationPreferenceRepository.get_event_preference(
                user_id=user_id,
                event_type=event_type,
                tenant_id=tenant_id,
            )

            if not preference:
                return None

            return {
                "id": str(preference.id),
                "user_id": preference.user_id,
                "event_type": preference.event_type,
                "channels": preference.channels or [],
                "enabled": preference.enabled,
                "quiet_hours_start": (
                    preference.quiet_hours_start.strftime("%H:%M")
                    if preference.quiet_hours_start
                    else None
                ),
                "quiet_hours_end": (
                    preference.quiet_hours_end.strftime("%H:%M")
                    if preference.quiet_hours_end
                    else None
                ),
                "metadata": preference.metadata,
                "created_at": preference.created_at.isoformat(),
                "updated_at": preference.updated_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting event preference: {e}")
            raise

    @staticmethod
    async def check_if_should_send(
        user_id: str,
        event_type: str,
        tenant_id: str | None = None,
    ) -> tuple[bool, list[str]]:
        """
        التحقق من إمكانية إرسال إشعار
        Check if notification should be sent for this event type

        Args:
            user_id: User ID
            event_type: Event type
            tenant_id: Optional tenant ID

        Returns:
            Tuple of (should_send: bool, channels: List[str])
        """
        try:
            # Check if event is enabled
            is_enabled = await NotificationPreferenceRepository.is_event_enabled(
                user_id=user_id,
                event_type=event_type,
                tenant_id=tenant_id,
            )

            if not is_enabled:
                logger.debug(f"Event {event_type} disabled for user {user_id}")
                return False, []

            # Get preferred channels
            channels = await NotificationPreferenceRepository.get_preferred_channels(
                user_id=user_id,
                event_type=event_type,
                tenant_id=tenant_id,
            )

            # If no preference set, use default channels
            if not channels:
                channels = ["in_app", "push"]

            logger.debug(
                f"Notification allowed for user {user_id}, event {event_type}, channels: {channels}"
            )
            return True, channels

        except Exception as e:
            logger.error(f"Error checking if should send: {e}")
            # Default to allowing notification with in_app channel on error
            return True, ["in_app"]
