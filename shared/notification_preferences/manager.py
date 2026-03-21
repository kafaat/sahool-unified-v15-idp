"""
Notification Preferences Manager
================================
مدير تفضيلات الإشعارات

Manages CRUD operations and business logic for notification preferences.
Supports in-memory storage with optional database persistence.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, time
from typing import Any, Protocol

from .models import (
    AlertType,
    AlertTypePreference,
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

logger = logging.getLogger(__name__)


class PreferencesStorage(Protocol):
    """
    Protocol for preferences storage backend
    بروتوكول لتخزين التفضيلات
    """

    async def get(self, user_id: str, tenant_id: str) -> UserNotificationPreferences | None:
        """Get preferences for a user. tenant_id required for isolation."""
        ...

    async def save(self, preferences: UserNotificationPreferences) -> None:
        """Save preferences"""
        ...

    async def delete(self, user_id: str, tenant_id: str) -> bool:
        """Delete preferences. tenant_id required for isolation."""
        ...

    async def list_all(self, tenant_id: str) -> list[UserNotificationPreferences]:
        """List all preferences filtered by tenant."""
        ...


class InMemoryStorage:
    """
    In-memory storage for preferences (for testing/development)
    تخزين في الذاكرة للتفضيلات (للاختبار/التطوير)
    """

    def __init__(self):
        self._storage: dict[str, UserNotificationPreferences] = {}

    def _key(self, user_id: str, tenant_id: str) -> str:
        """Generate storage key. SECURITY: tenant_id is required for isolation."""
        if not tenant_id:
            raise ValueError("tenant_id is required for storage key to ensure tenant isolation")
        return f"{tenant_id}:{user_id}"

    async def get(self, user_id: str, tenant_id: str) -> UserNotificationPreferences | None:
        """Get preferences for a user. SECURITY: tenant_id required for isolation."""
        key = self._key(user_id, tenant_id)
        return self._storage.get(key)

    async def save(self, preferences: UserNotificationPreferences) -> None:
        """Save preferences"""
        key = self._key(preferences.user_id, preferences.tenant_id)
        preferences.updated_at = datetime.now(UTC)
        preferences.version += 1
        self._storage[key] = preferences

    async def delete(self, user_id: str, tenant_id: str) -> bool:
        """Delete preferences. SECURITY: tenant_id required for isolation."""
        key = self._key(user_id, tenant_id)
        if key in self._storage:
            del self._storage[key]
            return True
        return False

    async def list_all(self, tenant_id: str) -> list[UserNotificationPreferences]:
        """List all preferences filtered by tenant. SECURITY: tenant_id required."""
        if not tenant_id:
            raise ValueError("tenant_id is required to ensure tenant isolation")
        return [p for p in self._storage.values() if p.tenant_id == tenant_id]


class NotificationPreferencesManager:
    """
    Manager for notification preferences
    مدير تفضيلات الإشعارات

    Provides CRUD operations and business logic for managing user
    notification preferences, including validation and default handling.
    """

    def __init__(self, storage: PreferencesStorage | None = None):
        """
        Initialize the manager

        Args:
            storage: Storage backend. Uses InMemoryStorage if not provided.
        """
        self.storage = storage or InMemoryStorage()

    # =========================================================================
    # Core CRUD Operations
    # =========================================================================

    async def get_preferences(
        self,
        user_id: str,
        tenant_id: str | None = None,
        create_if_missing: bool = True,
    ) -> UserNotificationPreferences:
        """
        Get notification preferences for a user
        الحصول على تفضيلات الإشعارات للمستخدم

        Args:
            user_id: User identifier
            tenant_id: Optional tenant identifier
            create_if_missing: Create default preferences if not found

        Returns:
            User notification preferences
        """
        # Use default tenant for internal lookups when tenant_id not provided
        effective_tenant = tenant_id or "default"
        preferences = await self.storage.get(user_id, effective_tenant)

        if preferences is None and create_if_missing:
            logger.info(f"Creating default preferences for user {user_id}")
            preferences = create_default_preferences(user_id, effective_tenant)
            await self.storage.save(preferences)

        return preferences

    async def save_preferences(
        self,
        preferences: UserNotificationPreferences,
        validate: bool = True,
    ) -> UserNotificationPreferences:
        """
        Save notification preferences
        حفظ تفضيلات الإشعارات

        Args:
            preferences: Preferences to save
            validate: Whether to validate before saving

        Returns:
            Saved preferences
        """
        if validate:
            self._validate_preferences(preferences)

        await self.storage.save(preferences)
        logger.info(f"Saved preferences for user {preferences.user_id}, version {preferences.version}")
        return preferences

    async def delete_preferences(
        self,
        user_id: str,
        tenant_id: str | None = None,
    ) -> bool:
        """
        Delete notification preferences
        حذف تفضيلات الإشعارات

        Args:
            user_id: User identifier
            tenant_id: Optional tenant identifier

        Returns:
            True if deleted, False if not found
        """
        effective_tenant = tenant_id or "default"
        result = await self.storage.delete(user_id, effective_tenant)
        if result:
            logger.info(f"Deleted preferences for user {user_id}")
        return result

    async def reset_to_defaults(
        self,
        user_id: str,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Reset preferences to defaults
        إعادة تعيين التفضيلات إلى الافتراضية

        Args:
            user_id: User identifier
            tenant_id: Optional tenant identifier

        Returns:
            New default preferences
        """
        effective_tenant = tenant_id or "default"
        preferences = create_default_preferences(user_id, effective_tenant)
        await self.storage.save(preferences)
        logger.info(f"Reset preferences to defaults for user {user_id}")
        return preferences

    # =========================================================================
    # Master Toggle Operations
    # =========================================================================

    async def enable_notifications(
        self,
        user_id: str,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Enable all notifications for a user
        تفعيل جميع الإشعارات للمستخدم
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        preferences.notifications_enabled = True
        return await self.save_preferences(preferences, validate=False)

    async def disable_notifications(
        self,
        user_id: str,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Disable all notifications for a user (except critical)
        تعطيل جميع الإشعارات للمستخدم (باستثناء الحرجة)
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        preferences.notifications_enabled = False
        return await self.save_preferences(preferences, validate=False)

    # =========================================================================
    # Language Operations
    # =========================================================================

    async def set_language(
        self,
        user_id: str,
        language: Language,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Set language preference
        تعيين تفضيل اللغة

        Args:
            user_id: User identifier
            language: Language preference
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        preferences.language = language
        return await self.save_preferences(preferences, validate=False)

    # =========================================================================
    # Channel Operations
    # =========================================================================

    async def set_default_channels(
        self,
        user_id: str,
        channels: list[NotificationChannel],
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Set default notification channels
        تعيين قنوات الإشعارات الافتراضية

        Args:
            user_id: User identifier
            channels: List of channels to use by default
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        if not channels:
            raise ValueError("At least one channel must be specified | يجب تحديد قناة واحدة على الأقل")

        preferences = await self.get_preferences(user_id, tenant_id)
        preferences.default_channels = channels
        return await self.save_preferences(preferences)

    async def add_channel(
        self,
        user_id: str,
        channel: NotificationChannel,
        address: str,
        tenant_id: str | None = None,
        verified: bool = False,
    ) -> UserNotificationPreferences:
        """
        Add or update a notification channel
        إضافة أو تحديث قناة إشعارات

        Args:
            user_id: User identifier
            channel: Channel type
            address: Channel address (email, phone, token)
            tenant_id: Optional tenant identifier
            verified: Whether the channel is verified

        Returns:
            Updated preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id)

        # Check if channel already exists
        existing = preferences.get_channel_config(channel)
        if existing:
            existing.address = address
            existing.verified = verified
            if verified:
                existing.verified_at = datetime.now(UTC)
        else:
            config = ChannelConfig(
                channel=channel,
                enabled=True,
                address=address,
                verified=verified,
                verified_at=datetime.now(UTC) if verified else None,
            )
            preferences.channel_configs.append(config)

        return await self.save_preferences(preferences)

    async def remove_channel(
        self,
        user_id: str,
        channel: NotificationChannel,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Remove a notification channel
        إزالة قناة إشعارات

        Args:
            user_id: User identifier
            channel: Channel type to remove
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        preferences.channel_configs = [c for c in preferences.channel_configs if c.channel != channel]
        return await self.save_preferences(preferences, validate=False)

    async def enable_channel(
        self,
        user_id: str,
        channel: NotificationChannel,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Enable a notification channel
        تفعيل قناة إشعارات
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        config = preferences.get_channel_config(channel)
        if config:
            config.enabled = True
        return await self.save_preferences(preferences, validate=False)

    async def disable_channel(
        self,
        user_id: str,
        channel: NotificationChannel,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Disable a notification channel
        تعطيل قناة إشعارات
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        config = preferences.get_channel_config(channel)
        if config:
            config.enabled = False
        return await self.save_preferences(preferences, validate=False)

    async def verify_channel(
        self,
        user_id: str,
        channel: NotificationChannel,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Mark a channel as verified
        تعليم قناة كمتحقق منها
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        config = preferences.get_channel_config(channel)
        if config:
            config.verified = True
            config.verified_at = datetime.now(UTC)
        return await self.save_preferences(preferences, validate=False)

    # =========================================================================
    # Alert Type Operations
    # =========================================================================

    async def set_alert_preference(
        self,
        user_id: str,
        alert_type: AlertType,
        enabled: bool = True,
        channels: list[NotificationChannel] | None = None,
        min_urgency: AlertUrgency | None = None,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Set preference for a specific alert type
        تعيين تفضيل لنوع تنبيه معين

        Args:
            user_id: User identifier
            alert_type: Type of alert
            enabled: Whether to enable notifications for this type
            channels: Specific channels for this alert type
            min_urgency: Minimum urgency to receive notifications
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id)

        existing = preferences.get_alert_preference(alert_type)
        if existing:
            existing.enabled = enabled
            if channels is not None:
                existing.channels = channels
            if min_urgency is not None:
                existing.min_urgency = min_urgency
        else:
            pref = AlertTypePreference(
                alert_type=alert_type,
                enabled=enabled,
                channels=channels or [],
                min_urgency=min_urgency or AlertUrgency.LOW,
            )
            preferences.alert_preferences.append(pref)

        return await self.save_preferences(preferences)

    async def disable_alert_type(
        self,
        user_id: str,
        alert_type: AlertType,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Disable notifications for a specific alert type
        تعطيل الإشعارات لنوع تنبيه معين
        """
        return await self.set_alert_preference(user_id, alert_type, enabled=False, tenant_id=tenant_id)

    async def enable_alert_type(
        self,
        user_id: str,
        alert_type: AlertType,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Enable notifications for a specific alert type
        تفعيل الإشعارات لنوع تنبيه معين
        """
        return await self.set_alert_preference(user_id, alert_type, enabled=True, tenant_id=tenant_id)

    # =========================================================================
    # Quiet Hours Operations
    # =========================================================================

    async def set_quiet_hours(
        self,
        user_id: str,
        start_time: time,
        end_time: time,
        enabled: bool = True,
        timezone: str = "Asia/Riyadh",
        days: list[DayOfWeek] | None = None,
        bypass_urgency: AlertUrgency = AlertUrgency.CRITICAL,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Set quiet hours (do not disturb period)
        تعيين الساعات الهادئة (فترة عدم الإزعاج)

        Args:
            user_id: User identifier
            start_time: Start of quiet period
            end_time: End of quiet period
            enabled: Whether quiet hours are enabled
            timezone: User's timezone
            days: Specific days (empty = all days)
            bypass_urgency: Minimum urgency to bypass quiet hours
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id)

        preferences.quiet_hours = QuietHours(
            enabled=enabled,
            start_time=start_time,
            end_time=end_time,
            timezone=timezone,
            days=days or [],
            bypass_urgency=bypass_urgency,
        )

        return await self.save_preferences(preferences)

    async def disable_quiet_hours(
        self,
        user_id: str,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Disable quiet hours
        تعطيل الساعات الهادئة
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        preferences.quiet_hours.enabled = False
        return await self.save_preferences(preferences, validate=False)

    async def enable_quiet_hours(
        self,
        user_id: str,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Enable quiet hours
        تفعيل الساعات الهادئة
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        preferences.quiet_hours.enabled = True
        return await self.save_preferences(preferences, validate=False)

    # =========================================================================
    # Time-Based Rules Operations
    # =========================================================================

    async def add_time_rule(
        self,
        user_id: str,
        rule: TimeBasedRule,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Add a time-based routing rule
        إضافة قاعدة توجيه حسب الوقت

        Args:
            user_id: User identifier
            rule: Time-based rule to add
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id)

        # Remove existing rule with same ID
        preferences.time_rules = [r for r in preferences.time_rules if r.id != rule.id]
        preferences.time_rules.append(rule)

        # Sort by priority (descending)
        preferences.time_rules.sort(key=lambda r: r.priority, reverse=True)

        return await self.save_preferences(preferences)

    async def remove_time_rule(
        self,
        user_id: str,
        rule_id: str,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Remove a time-based routing rule
        إزالة قاعدة توجيه حسب الوقت

        Args:
            user_id: User identifier
            rule_id: ID of the rule to remove
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        preferences.time_rules = [r for r in preferences.time_rules if r.id != rule_id]
        return await self.save_preferences(preferences, validate=False)

    async def create_no_sms_at_night_rule(
        self,
        user_id: str,
        start_hour: int = 22,
        end_hour: int = 6,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Create a "no SMS at night" rule
        إنشاء قاعدة "لا رسائل نصية ليلاً"

        Args:
            user_id: User identifier
            start_hour: Hour when rule starts (default 22 = 10 PM)
            end_hour: Hour when rule ends (default 6 = 6 AM)
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        rule = TimeBasedRule(
            name="No SMS at night",
            name_ar="لا رسائل نصية ليلاً",
            enabled=True,
            start_time=time(start_hour, 0),
            end_time=time(end_hour, 0),
            channels=[NotificationChannel.SMS],
            action="channel_fallback",
            fallback_channel=NotificationChannel.PUSH,
            exempt_urgencies=[AlertUrgency.CRITICAL],
            priority=100,
        )
        return await self.add_time_rule(user_id, rule, tenant_id)

    # =========================================================================
    # Urgency Override Operations
    # =========================================================================

    async def set_urgency_override(
        self,
        user_id: str,
        override: UrgencyOverride,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Set or update an urgency override
        تعيين أو تحديث تجاوز الإلحاح

        Args:
            user_id: User identifier
            override: Urgency override configuration
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id)

        # Remove existing override for same urgency
        preferences.urgency_overrides = [o for o in preferences.urgency_overrides if o.urgency != override.urgency]
        preferences.urgency_overrides.append(override)

        return await self.save_preferences(preferences)

    async def remove_urgency_override(
        self,
        user_id: str,
        urgency: AlertUrgency,
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Remove an urgency override
        إزالة تجاوز الإلحاح

        Args:
            user_id: User identifier
            urgency: Urgency level to remove override for
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id)
        preferences.urgency_overrides = [o for o in preferences.urgency_overrides if o.urgency != urgency]
        return await self.save_preferences(preferences, validate=False)

    # =========================================================================
    # Bulk Operations
    # =========================================================================

    async def update_preferences(
        self,
        user_id: str,
        updates: dict[str, Any],
        tenant_id: str | None = None,
    ) -> UserNotificationPreferences:
        """
        Update multiple preference fields at once
        تحديث حقول تفضيلات متعددة مرة واحدة

        Args:
            user_id: User identifier
            updates: Dictionary of field updates
            tenant_id: Optional tenant identifier

        Returns:
            Updated preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id)

        # Update simple fields
        simple_fields = [
            "notifications_enabled",
            "sound_enabled",
            "vibration_enabled",
            "show_badge_count",
            "show_preview",
            "show_preview_on_lock_screen",
            "digest_enabled",
            "summary_enabled",
            "summary_interval_hours",
        ]

        for field in simple_fields:
            if field in updates:
                setattr(preferences, field, updates[field])

        # Update language
        if "language" in updates:
            preferences.language = Language(updates["language"])

        # Update default channels
        if "default_channels" in updates:
            preferences.default_channels = [NotificationChannel(c) for c in updates["default_channels"]]

        # Update quiet hours
        if "quiet_hours" in updates:
            preferences.quiet_hours = QuietHours.from_dict(updates["quiet_hours"])

        # Update digest settings
        if "digest_time" in updates and updates["digest_time"]:
            preferences.digest_time = time.fromisoformat(updates["digest_time"])
        if "digest_days" in updates:
            preferences.digest_days = [DayOfWeek(d) for d in updates["digest_days"]]
        if "digest_channel" in updates:
            preferences.digest_channel = NotificationChannel(updates["digest_channel"])

        return await self.save_preferences(preferences)

    async def export_preferences(
        self,
        user_id: str,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Export preferences as JSON-serializable dictionary
        تصدير التفضيلات كقاموس قابل للتسلسل JSON

        Args:
            user_id: User identifier
            tenant_id: Optional tenant identifier

        Returns:
            Dictionary of preferences
        """
        preferences = await self.get_preferences(user_id, tenant_id, create_if_missing=False)
        if preferences is None:
            return {}
        return preferences.to_dict()

    async def import_preferences(
        self,
        user_id: str,
        data: dict[str, Any],
        tenant_id: str | None = None,
        merge: bool = False,
    ) -> UserNotificationPreferences:
        """
        Import preferences from dictionary
        استيراد التفضيلات من قاموس

        Args:
            user_id: User identifier
            data: Dictionary of preferences
            tenant_id: Optional tenant identifier
            merge: If True, merge with existing preferences

        Returns:
            Imported preferences
        """
        imported = UserNotificationPreferences.from_dict(data)
        imported.user_id = user_id
        imported.tenant_id = tenant_id

        if merge:
            existing = await self.get_preferences(user_id, tenant_id, create_if_missing=False)
            if existing:
                # Merge channel configs
                existing_channels = {c.channel for c in existing.channel_configs}
                for config in imported.channel_configs:
                    if config.channel not in existing_channels:
                        existing.channel_configs.append(config)

                # Merge alert preferences
                existing_alerts = {p.alert_type for p in existing.alert_preferences}
                for pref in imported.alert_preferences:
                    if pref.alert_type not in existing_alerts:
                        existing.alert_preferences.append(pref)

                # Merge time rules
                existing_rule_ids = {r.id for r in existing.time_rules}
                for rule in imported.time_rules:
                    if rule.id not in existing_rule_ids:
                        existing.time_rules.append(rule)

                imported = existing

        return await self.save_preferences(imported)

    # =========================================================================
    # Validation
    # =========================================================================

    def _validate_preferences(self, preferences: UserNotificationPreferences) -> None:
        """
        Validate preferences
        التحقق من صحة التفضيلات
        """
        if not preferences.user_id:
            raise ValueError("User ID is required | معرف المستخدم مطلوب")

        # Validate quiet hours times
        if preferences.quiet_hours.enabled:
            if preferences.quiet_hours.start_time == preferences.quiet_hours.end_time:
                raise ValueError(
                    "Quiet hours start and end times cannot be the same | "
                    "لا يمكن أن يكون وقت بداية ونهاية الساعات الهادئة متساويين"
                )

        # Validate channel configs
        channel_types = set()
        for config in preferences.channel_configs:
            if config.channel in channel_types:
                raise ValueError(
                    f"Duplicate channel configuration: {config.channel.value} | "
                    f"إعدادات قناة مكررة: {config.channel.value}"
                )
            channel_types.add(config.channel)

        # Validate time rules
        for rule in preferences.time_rules:
            if rule.action == "channel_fallback" and not rule.fallback_channel:
                raise ValueError(
                    f"Fallback channel required for rule '{rule.name}' | "
                    f"قناة بديلة مطلوبة للقاعدة '{rule.name_ar or rule.name}'"
                )

        # Validate urgency overrides
        urgency_levels = set()
        for override in preferences.urgency_overrides:
            if override.urgency in urgency_levels:
                raise ValueError(
                    f"Duplicate urgency override: {override.urgency.value} | تجاوز إلحاح مكرر: {override.urgency.value}"
                )
            urgency_levels.add(override.urgency)

        logger.debug(f"Preferences validated for user {preferences.user_id}")

    # =========================================================================
    # Query Operations
    # =========================================================================

    async def get_users_by_channel(
        self,
        channel: NotificationChannel,
        tenant_id: str | None = None,
        verified_only: bool = True,
    ) -> list[str]:
        """
        Get user IDs that have a specific channel enabled
        الحصول على معرفات المستخدمين الذين لديهم قناة معينة مفعلة

        Args:
            channel: Channel type
            tenant_id: Optional tenant filter
            verified_only: Only return verified channels

        Returns:
            List of user IDs
        """
        all_prefs = await self.storage.list_all(tenant_id)
        user_ids = []

        for prefs in all_prefs:
            if not prefs.notifications_enabled:
                continue

            config = prefs.get_channel_config(channel)
            if config and config.enabled:
                if not verified_only or config.verified:
                    user_ids.append(prefs.user_id)

        return user_ids

    async def get_users_subscribed_to_alert(
        self,
        alert_type: AlertType,
        tenant_id: str | None = None,
    ) -> list[str]:
        """
        Get user IDs subscribed to a specific alert type
        الحصول على معرفات المستخدمين المشتركين في نوع تنبيه معين

        Args:
            alert_type: Alert type
            tenant_id: Optional tenant filter

        Returns:
            List of user IDs
        """
        all_prefs = await self.storage.list_all(tenant_id)
        user_ids = []

        for prefs in all_prefs:
            if not prefs.notifications_enabled:
                continue

            # Check if explicitly disabled
            pref = prefs.get_alert_preference(alert_type)
            if pref and not pref.enabled:
                continue

            # Otherwise, user is subscribed (default is enabled)
            user_ids.append(prefs.user_id)

        return user_ids
