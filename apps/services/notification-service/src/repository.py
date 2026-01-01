"""
SAHOOL Notification Service - Data Repository Layer
طبقة الوصول للبيانات - Repository Pattern
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID, uuid4
import logging

from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from .models import Notification, NotificationTemplate, NotificationPreference, NotificationLog, NotificationChannel, ChannelType

logger = logging.getLogger("sahool-notifications.repository")


class NotificationRepository:
    """
    مستودع الإشعارات
    Repository for managing notifications with CRUD operations
    """

    @staticmethod
    async def create(
        user_id: str,
        title: str,
        body: str,
        type: str,
        channel: str = "in_app",
        priority: str = "medium",
        tenant_id: Optional[str] = None,
        title_ar: Optional[str] = None,
        body_ar: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        action_url: Optional[str] = None,
        target_governorates: Optional[List[str]] = None,
        target_crops: Optional[List[str]] = None,
        expires_in_hours: Optional[int] = 24,
    ) -> Notification:
        """
        إنشاء إشعار جديد
        Create a new notification
        """
        notification = await Notification.create(
            id=uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            title=title,
            title_ar=title_ar or title,
            body=body,
            body_ar=body_ar or body,
            type=type,
            priority=priority,
            channel=channel,
            status="pending",
            data=data or {},
            action_url=action_url,
            target_governorates=target_governorates,
            target_crops=target_crops,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours) if expires_in_hours else None,
        )

        logger.info(f"Created notification {notification.id} for user {user_id}")
        return notification

    @staticmethod
    async def create_bulk(notifications_data: List[Dict[str, Any]]) -> List[Notification]:
        """
        إنشاء إشعارات متعددة دفعة واحدة
        Create multiple notifications in bulk
        """
        notifications = []
        for data in notifications_data:
            # Set default values
            if "id" not in data:
                data["id"] = uuid4()
            if "status" not in data:
                data["status"] = "pending"
            if "title_ar" not in data:
                data["title_ar"] = data.get("title", "")
            if "body_ar" not in data:
                data["body_ar"] = data.get("body", "")
            if "data" not in data:
                data["data"] = {}

            notification = Notification(**data)
            notifications.append(notification)

        await Notification.bulk_create(notifications)
        logger.info(f"Created {len(notifications)} notifications in bulk")
        return notifications

    @staticmethod
    async def get_by_id(notification_id: UUID) -> Optional[Notification]:
        """
        الحصول على إشعار بواسطة المعرف
        Get notification by ID
        """
        return await Notification.filter(id=notification_id).first()

    @staticmethod
    async def get_by_user(
        user_id: str,
        tenant_id: Optional[str] = None,
        unread_only: bool = False,
        type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        include_expired: bool = False,
    ) -> List[Notification]:
        """
        الحصول على إشعارات مستخدم معين
        Get notifications for a specific user
        """
        query = Notification.filter(user_id=user_id)

        # Filter by tenant
        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        # Filter by read status
        if unread_only:
            query = query.filter(read_at__isnull=True)

        # Filter by type
        if type:
            query = query.filter(type=type)

        # Filter by status
        if status:
            query = query.filter(status=status)

        # Filter expired notifications
        if not include_expired:
            query = query.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=datetime.utcnow())
            )

        # Order by creation date
        query = query.order_by("-created_at")

        # Pagination
        notifications = await query.offset(offset).limit(limit).all()

        return notifications

    @staticmethod
    async def get_unread_count(user_id: str, tenant_id: Optional[str] = None) -> int:
        """
        الحصول على عدد الإشعارات غير المقروءة
        Get count of unread notifications
        """
        query = Notification.filter(
            user_id=user_id,
            read_at__isnull=True,
        )

        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        # Exclude expired
        query = query.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=datetime.utcnow())
        )

        count = await query.count()
        return count

    @staticmethod
    async def mark_as_read(notification_id: UUID, read_at: Optional[datetime] = None) -> bool:
        """
        تحديد إشعار كمقروء
        Mark notification as read
        """
        if read_at is None:
            read_at = datetime.utcnow()

        updated = await Notification.filter(id=notification_id).update(
            read_at=read_at,
            status="read",
        )

        if updated:
            logger.info(f"Marked notification {notification_id} as read")
            return True
        return False

    @staticmethod
    async def mark_multiple_as_read(
        notification_ids: List[UUID], read_at: Optional[datetime] = None
    ) -> int:
        """
        تحديد إشعارات متعددة كمقروءة
        Mark multiple notifications as read
        """
        if read_at is None:
            read_at = datetime.utcnow()

        updated = await Notification.filter(id__in=notification_ids).update(
            read_at=read_at,
            status="read",
        )

        logger.info(f"Marked {updated} notifications as read")
        return updated

    @staticmethod
    async def mark_all_as_read(user_id: str, tenant_id: Optional[str] = None) -> int:
        """
        تحديد جميع إشعارات المستخدم كمقروءة
        Mark all user notifications as read
        """
        query = Notification.filter(user_id=user_id, read_at__isnull=True)

        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        updated = await query.update(
            read_at=datetime.utcnow(),
            status="read",
        )

        logger.info(f"Marked {updated} notifications as read for user {user_id}")
        return updated

    @staticmethod
    async def update_status(
        notification_id: UUID, status: str, sent_at: Optional[datetime] = None
    ) -> bool:
        """
        تحديث حالة الإشعار
        Update notification status
        """
        update_data = {"status": status}
        if sent_at:
            update_data["sent_at"] = sent_at

        updated = await Notification.filter(id=notification_id).update(**update_data)

        if updated:
            logger.info(f"Updated notification {notification_id} status to {status}")
            return True
        return False

    @staticmethod
    async def delete(notification_id: UUID) -> bool:
        """
        حذف إشعار
        Delete a notification
        """
        deleted = await Notification.filter(id=notification_id).delete()
        if deleted:
            logger.info(f"Deleted notification {notification_id}")
            return True
        return False

    @staticmethod
    async def delete_old_notifications(days: int = 30) -> int:
        """
        حذف الإشعارات القديمة
        Delete notifications older than specified days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = await Notification.filter(created_at__lt=cutoff_date).delete()

        logger.info(f"Deleted {deleted} notifications older than {days} days")
        return deleted

    @staticmethod
    async def get_pending_notifications(
        limit: int = 100,
        channel: Optional[str] = None,
    ) -> List[Notification]:
        """
        الحصول على الإشعارات المعلقة للإرسال
        Get pending notifications for sending
        """
        query = Notification.filter(status="pending")

        if channel:
            query = query.filter(channel=channel)

        # Only get non-expired
        query = query.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=datetime.utcnow())
        )

        notifications = await query.order_by("created_at").limit(limit).all()
        return notifications

    @staticmethod
    async def get_broadcast_notifications(
        governorate: Optional[str] = None,
        crop: Optional[str] = None,
        limit: int = 20,
    ) -> List[Notification]:
        """
        الحصول على الإشعارات العامة
        Get broadcast notifications
        """
        query = Notification.filter()

        # Filter by governorate
        if governorate:
            query = query.filter(target_governorates__contains=[governorate])

        # Filter by crop
        if crop:
            query = query.filter(target_crops__contains=[crop])

        # Only non-expired
        query = query.filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=datetime.utcnow())
        )

        notifications = await query.order_by("-created_at").limit(limit).all()
        return notifications


class NotificationTemplateRepository:
    """
    مستودع قوالب الإشعارات
    Repository for notification templates
    """

    @staticmethod
    async def create(
        name: str,
        title_template: str,
        body_template: str,
        type: str,
        title_template_ar: Optional[str] = None,
        body_template_ar: Optional[str] = None,
        priority: str = "medium",
        channel: str = "in_app",
        variables: Optional[List[str]] = None,
        tenant_id: Optional[str] = None,
    ) -> NotificationTemplate:
        """
        إنشاء قالب جديد
        Create a new notification template
        """
        template = await NotificationTemplate.create(
            id=uuid4(),
            tenant_id=tenant_id,
            name=name,
            title_template=title_template,
            title_template_ar=title_template_ar or title_template,
            body_template=body_template,
            body_template_ar=body_template_ar or body_template,
            type=type,
            priority=priority,
            channel=channel,
            variables=variables or [],
        )

        logger.info(f"Created notification template: {name}")
        return template

    @staticmethod
    async def get_by_name(name: str) -> Optional[NotificationTemplate]:
        """الحصول على قالب بواسطة الاسم"""
        return await NotificationTemplate.filter(name=name, is_active=True).first()

    @staticmethod
    async def get_all_active(tenant_id: Optional[str] = None) -> List[NotificationTemplate]:
        """الحصول على جميع القوالب النشطة"""
        query = NotificationTemplate.filter(is_active=True)

        if tenant_id:
            query = query.filter(Q(tenant_id=tenant_id) | Q(tenant_id__isnull=True))

        return await query.all()

    @staticmethod
    async def update(template_id: UUID, **kwargs) -> bool:
        """تحديث قالب"""
        updated = await NotificationTemplate.filter(id=template_id).update(**kwargs)
        return updated > 0

    @staticmethod
    async def deactivate(template_id: UUID) -> bool:
        """إلغاء تفعيل قالب"""
        return await NotificationTemplateRepository.update(template_id, is_active=False)


class NotificationChannelRepository:
    """
    مستودع قنوات الإشعارات
    Repository for user notification channels
    """

    @staticmethod
    async def create(
        user_id: str,
        channel: ChannelType,
        address: str,
        tenant_id: Optional[str] = None,
        verified: bool = False,
        enabled: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NotificationChannel:
        """
        إنشاء قناة إشعار جديدة
        Create a new notification channel
        """
        # Check if channel already exists
        existing = await NotificationChannel.filter(
            user_id=user_id,
            channel=channel,
            address=address,
        ).first()

        if existing:
            # Update existing channel
            existing.enabled = enabled
            existing.verified = verified
            existing.tenant_id = tenant_id
            if metadata:
                existing.metadata = metadata
            await existing.save()
            logger.info(f"Updated existing channel {channel} for user {user_id}")
            return existing

        channel_obj = await NotificationChannel.create(
            id=uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            channel=channel,
            address=address,
            verified=verified,
            enabled=enabled,
            metadata=metadata or {},
        )

        logger.info(f"Created notification channel {channel} for user {user_id}")
        return channel_obj

    @staticmethod
    async def get_user_channels(
        user_id: str,
        tenant_id: Optional[str] = None,
        channel_type: Optional[ChannelType] = None,
        enabled_only: bool = False,
    ) -> List[NotificationChannel]:
        """
        الحصول على قنوات المستخدم
        Get user's notification channels
        """
        query = NotificationChannel.filter(user_id=user_id)

        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        if channel_type:
            query = query.filter(channel=channel_type)

        if enabled_only:
            query = query.filter(enabled=True)

        return await query.all()

    @staticmethod
    async def get_by_id(channel_id: UUID) -> Optional[NotificationChannel]:
        """الحصول على قناة بواسطة المعرف"""
        return await NotificationChannel.filter(id=channel_id).first()

    @staticmethod
    async def verify_channel(
        channel_id: UUID,
        verification_code: Optional[str] = None,
    ) -> bool:
        """
        تحقق من قناة
        Verify a notification channel
        """
        channel = await NotificationChannel.filter(id=channel_id).first()

        if not channel:
            return False

        # If verification code is provided, check it
        if verification_code and channel.verification_code != verification_code:
            return False

        channel.verified = True
        channel.verified_at = datetime.utcnow()
        channel.verification_code = None
        await channel.save()

        logger.info(f"Verified channel {channel.channel} for user {channel.user_id}")
        return True

    @staticmethod
    async def update_channel(
        channel_id: UUID,
        **kwargs,
    ) -> bool:
        """
        تحديث قناة
        Update a notification channel
        """
        updated = await NotificationChannel.filter(id=channel_id).update(**kwargs)

        if updated:
            logger.info(f"Updated notification channel {channel_id}")
            return True
        return False

    @staticmethod
    async def delete_channel(channel_id: UUID) -> bool:
        """
        حذف قناة
        Delete a notification channel
        """
        deleted = await NotificationChannel.filter(id=channel_id).delete()

        if deleted:
            logger.info(f"Deleted notification channel {channel_id}")
            return True
        return False

    @staticmethod
    async def get_verified_channels(
        user_id: str,
        channel_type: ChannelType,
        tenant_id: Optional[str] = None,
    ) -> List[NotificationChannel]:
        """
        الحصول على القنوات المحققة
        Get verified channels for a user
        """
        query = NotificationChannel.filter(
            user_id=user_id,
            channel=channel_type,
            verified=True,
            enabled=True,
        )

        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        return await query.all()


class NotificationPreferenceRepository:
    """
    مستودع تفضيلات الإشعارات
    Repository for notification preferences
    """

    @staticmethod
    async def create_or_update(
        user_id: str,
        event_type: str,
        channels: List[str],
        enabled: bool = True,
        tenant_id: Optional[str] = None,
        **kwargs,
    ) -> NotificationPreference:
        """
        إنشاء أو تحديث تفضيلات
        Create or update notification preferences for an event type
        """
        preference, created = await NotificationPreference.get_or_create(
            user_id=user_id,
            event_type=event_type,
            defaults={
                "id": uuid4(),
                "tenant_id": tenant_id,
                "enabled": enabled,
                "channels": channels,
                **kwargs,
            },
        )

        if not created:
            # Update existing
            for key, value in kwargs.items():
                setattr(preference, key, value)
            preference.enabled = enabled
            preference.channels = channels
            await preference.save()

        action = "Created" if created else "Updated"
        logger.info(f"{action} preferences for user {user_id}, event {event_type}")

        return preference

    @staticmethod
    async def get_user_preferences(
        user_id: str, tenant_id: Optional[str] = None
    ) -> List[NotificationPreference]:
        """
        الحصول على تفضيلات المستخدم
        Get user notification preferences
        """
        query = NotificationPreference.filter(user_id=user_id)

        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        return await query.all()

    @staticmethod
    async def get_event_preference(
        user_id: str, event_type: str, tenant_id: Optional[str] = None
    ) -> Optional[NotificationPreference]:
        """الحصول على تفضيلات نوع حدث معين"""
        query = NotificationPreference.filter(user_id=user_id, event_type=event_type)

        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        return await query.first()

    @staticmethod
    async def is_event_enabled(
        user_id: str, event_type: str, tenant_id: Optional[str] = None
    ) -> bool:
        """التحقق من تفعيل نوع حدث معين"""
        preference = await NotificationPreferenceRepository.get_event_preference(
            user_id, event_type, tenant_id
        )

        if not preference:
            # Default to enabled if no preference set
            return True

        return preference.enabled

    @staticmethod
    async def get_preferred_channels(
        user_id: str, event_type: str, tenant_id: Optional[str] = None
    ) -> List[str]:
        """
        الحصول على القنوات المفضلة لنوع حدث
        Get preferred channels for an event type
        """
        preference = await NotificationPreferenceRepository.get_event_preference(
            user_id, event_type, tenant_id
        )

        if not preference or not preference.enabled:
            return []

        return preference.channels or []

    @staticmethod
    async def update_quiet_hours(
        user_id: str,
        quiet_hours_start: Optional[str] = None,
        quiet_hours_end: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """
        تحديث ساعات الهدوء
        Update quiet hours for all user preferences
        """
        from datetime import time

        # Parse time strings
        start_time = None
        end_time = None

        if quiet_hours_start:
            hour, minute = map(int, quiet_hours_start.split(":"))
            start_time = time(hour, minute)

        if quiet_hours_end:
            hour, minute = map(int, quiet_hours_end.split(":"))
            end_time = time(hour, minute)

        # Update all user preferences
        query = NotificationPreference.filter(user_id=user_id)
        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        updated = await query.update(
            quiet_hours_start=start_time,
            quiet_hours_end=end_time,
        )

        logger.info(f"Updated quiet hours for user {user_id}: {updated} preferences updated")
        return updated > 0


class NotificationLogRepository:
    """
    مستودع سجلات الإشعارات
    Repository for notification delivery logs
    """

    @staticmethod
    async def create_log(
        notification_id: UUID,
        channel: str,
        status: str,
        error_message: Optional[str] = None,
        provider_response: Optional[Dict[str, Any]] = None,
        provider_message_id: Optional[str] = None,
    ) -> NotificationLog:
        """
        إنشاء سجل توصيل
        Create a delivery log entry
        """
        log = await NotificationLog.create(
            id=uuid4(),
            notification_id=notification_id,
            channel=channel,
            status=status,
            error_message=error_message,
            provider_response=provider_response,
            provider_message_id=provider_message_id,
        )

        logger.info(f"Created log for notification {notification_id}: {status}")
        return log

    @staticmethod
    async def get_notification_logs(notification_id: UUID) -> List[NotificationLog]:
        """الحصول على سجلات إشعار معين"""
        return await NotificationLog.filter(notification_id=notification_id).all()

    @staticmethod
    async def get_failed_logs(limit: int = 100) -> List[NotificationLog]:
        """الحصول على السجلات الفاشلة للمحاولة مرة أخرى"""
        return await NotificationLog.filter(
            status="failed",
            retry_count__lt=3,  # Max 3 retries
        ).order_by("attempted_at").limit(limit).all()

    @staticmethod
    async def increment_retry(log_id: UUID) -> bool:
        """زيادة عدد المحاولات"""
        log = await NotificationLog.filter(id=log_id).first()
        if log:
            log.retry_count += 1
            log.next_retry_at = datetime.utcnow() + timedelta(minutes=5 * (log.retry_count))
            await log.save()
            return True
        return False
