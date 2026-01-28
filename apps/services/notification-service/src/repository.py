"""
SAHOOL Notification Service - Data Repository Layer
طبقة الوصول للبيانات - Repository Pattern
"""

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from tortoise.expressions import Q

from .models import (
    ChannelType,
    Notification,
    NotificationChannel,
    NotificationLog,
    NotificationPreference,
    NotificationTemplate,
)

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
        tenant_id: str | None = None,
        title_ar: str | None = None,
        body_ar: str | None = None,
        data: dict[str, Any] | None = None,
        action_url: str | None = None,
        target_governorates: list[str] | None = None,
        target_crops: list[str] | None = None,
        expires_in_hours: int | None = 24,
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
            expires_at=(
                datetime.utcnow() + timedelta(hours=expires_in_hours) if expires_in_hours else None
            ),
        )

        logger.info(f"Created notification {notification.id} for user {user_id}")
        return notification

    @staticmethod
    async def create_bulk(
        notifications_data: list[dict[str, Any]],
    ) -> list[Notification]:
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
    async def get_by_id(notification_id: UUID) -> Notification | None:
        """
        الحصول على إشعار بواسطة المعرف
        Get notification by ID
        """
        return await Notification.filter(id=notification_id).first()

    @staticmethod
    async def get_by_user(
        user_id: str,
        tenant_id: str | None = None,
        unread_only: bool = False,
        type: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
        include_expired: bool = False,
    ) -> list[Notification]:
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
            query = query.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=datetime.utcnow()))

        # Order by creation date
        query = query.order_by("-created_at")

        # Pagination
        notifications = await query.offset(offset).limit(limit).all()

        return notifications

    @staticmethod
    async def get_unread_count(user_id: str, tenant_id: str | None = None) -> int:
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
        query = query.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=datetime.utcnow()))

        count = await query.count()
        return count

    @staticmethod
    async def mark_as_read(notification_id: UUID, read_at: datetime | None = None) -> bool:
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
        notification_ids: list[UUID], read_at: datetime | None = None
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
    async def mark_all_as_read(user_id: str, tenant_id: str | None = None) -> int:
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
        notification_id: UUID, status: str, sent_at: datetime | None = None
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
        channel: str | None = None,
    ) -> list[Notification]:
        """
        الحصول على الإشعارات المعلقة للإرسال
        Get pending notifications for sending
        """
        query = Notification.filter(status="pending")

        if channel:
            query = query.filter(channel=channel)

        # Only get non-expired
        query = query.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=datetime.utcnow()))

        notifications = await query.order_by("created_at").limit(limit).all()
        return notifications

    @staticmethod
    async def get_broadcast_notifications(
        governorate: str | None = None,
        crop: str | None = None,
        limit: int = 20,
    ) -> list[Notification]:
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
        query = query.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=datetime.utcnow()))

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
        title_template_ar: str | None = None,
        body_template_ar: str | None = None,
        priority: str = "medium",
        channel: str = "in_app",
        variables: list[str] | None = None,
        tenant_id: str | None = None,
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
    async def get_by_name(name: str) -> NotificationTemplate | None:
        """الحصول على قالب بواسطة الاسم"""
        return await NotificationTemplate.filter(name=name, is_active=True).first()

    @staticmethod
    async def get_all_active(
        tenant_id: str | None = None,
    ) -> list[NotificationTemplate]:
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
        tenant_id: str | None = None,
        verified: bool = False,
        enabled: bool = True,
        metadata: dict[str, Any] | None = None,
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
        tenant_id: str | None = None,
        channel_type: ChannelType | None = None,
        enabled_only: bool = False,
    ) -> list[NotificationChannel]:
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
    async def get_by_id(channel_id: UUID) -> NotificationChannel | None:
        """الحصول على قناة بواسطة المعرف"""
        return await NotificationChannel.filter(id=channel_id).first()

    @staticmethod
    async def verify_channel(
        channel_id: UUID,
        verification_code: str | None = None,
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
        tenant_id: str | None = None,
    ) -> list[NotificationChannel]:
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
        channels: list[str],
        enabled: bool = True,
        tenant_id: str | None = None,
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
        user_id: str, tenant_id: str | None = None
    ) -> list[NotificationPreference]:
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
        user_id: str, event_type: str, tenant_id: str | None = None
    ) -> NotificationPreference | None:
        """الحصول على تفضيلات نوع حدث معين"""
        query = NotificationPreference.filter(user_id=user_id, event_type=event_type)

        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        return await query.first()

    @staticmethod
    async def is_event_enabled(user_id: str, event_type: str, tenant_id: str | None = None) -> bool:
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
        user_id: str, event_type: str, tenant_id: str | None = None
    ) -> list[str]:
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
        quiet_hours_start: str | None = None,
        quiet_hours_end: str | None = None,
        tenant_id: str | None = None,
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
        error_message: str | None = None,
        provider_response: dict[str, Any] | None = None,
        provider_message_id: str | None = None,
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
    async def get_notification_logs(notification_id: UUID) -> list[NotificationLog]:
        """الحصول على سجلات إشعار معين"""
        return await NotificationLog.filter(notification_id=notification_id).all()

    @staticmethod
    async def get_failed_logs(limit: int = 100) -> list[NotificationLog]:
        """الحصول على السجلات الفاشلة للمحاولة مرة أخرى"""
        return (
            await NotificationLog.filter(
                status="failed",
                retry_count__lt=3,  # Max 3 retries
            )
            .order_by("attempted_at")
            .limit(limit)
            .all()
        )

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


class FarmerProfileRepository:
    """
    مستودع ملفات المزارعين
    Repository for managing farmer profiles
    """

    @staticmethod
    async def create(
        farmer_id: str,
        name: str,
        governorate: str,
        crops: list[str],
        name_ar: str | None = None,
        district: str | None = None,
        field_ids: list[str] | None = None,
        phone: str | None = None,
        email: str | None = None,
        fcm_token: str | None = None,
        language: str = "ar",
        tenant_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        إنشاء ملف مزارع جديد
        Create a new farmer profile with crops and fields
        """
        from .models import FarmerCrop, FarmerField, FarmerProfile

        # Check if farmer already exists
        existing = await FarmerProfile.filter(farmer_id=farmer_id).first()
        if existing:
            logger.warning(f"Farmer {farmer_id} already exists, updating instead")
            return await FarmerProfileRepository.update(
                farmer_id=farmer_id,
                name=name,
                governorate=governorate,
                crops=crops,
                name_ar=name_ar,
                district=district,
                field_ids=field_ids,
                phone=phone,
                email=email,
                fcm_token=fcm_token,
                language=language,
                metadata=metadata,
            )

        # Create farmer profile
        profile = await FarmerProfile.create(
            id=uuid4(),
            tenant_id=tenant_id,
            farmer_id=farmer_id,
            name=name,
            name_ar=name_ar or name,
            governorate=governorate,
            district=district,
            phone=phone,
            email=email,
            fcm_token=fcm_token,
            language=language,
            metadata=metadata or {},
            is_active=True,
        )

        # Create crop associations
        if crops:
            for crop_type in crops:
                await FarmerCrop.create(
                    id=uuid4(),
                    farmer=profile,
                    crop_type=crop_type,
                    is_active=True,
                )

        # Create field associations
        if field_ids:
            for field_id in field_ids:
                await FarmerField.create(
                    id=uuid4(),
                    farmer=profile,
                    field_id=field_id,
                    is_active=True,
                )

        logger.info(
            f"Created farmer profile {farmer_id} with {len(crops or [])} crops and {len(field_ids or [])} fields"
        )
        return profile

    @staticmethod
    async def get_by_farmer_id(farmer_id: str) -> Any | None:
        """
        الحصول على ملف مزارع بواسطة المعرف
        Get farmer profile by farmer_id with prefetched crops and fields
        """
        from .models import FarmerProfile

        profile = (
            await FarmerProfile.filter(farmer_id=farmer_id)
            .prefetch_related("farmer_crops", "farmer_fields")
            .first()
        )
        return profile

    @staticmethod
    async def get_by_id(profile_id: UUID) -> Any | None:
        """Get farmer profile by UUID"""
        from .models import FarmerProfile

        return await FarmerProfile.filter(id=profile_id).first()

    @staticmethod
    async def update(
        farmer_id: str,
        name: str | None = None,
        governorate: str | None = None,
        crops: list[str] | None = None,
        name_ar: str | None = None,
        district: str | None = None,
        field_ids: list[str] | None = None,
        phone: str | None = None,
        email: str | None = None,
        fcm_token: str | None = None,
        language: str | None = None,
        metadata: dict[str, Any] | None = None,
        is_active: bool | None = None,
    ):
        """
        تحديث ملف مزارع
        Update farmer profile
        """
        from .models import FarmerCrop, FarmerField, FarmerProfile

        profile = await FarmerProfile.filter(farmer_id=farmer_id).first()
        if not profile:
            raise ValueError(f"Farmer {farmer_id} not found")

        # Update basic fields
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if name_ar is not None:
            update_data["name_ar"] = name_ar
        if governorate is not None:
            update_data["governorate"] = governorate
        if district is not None:
            update_data["district"] = district
        if phone is not None:
            update_data["phone"] = phone
        if email is not None:
            update_data["email"] = email
        if fcm_token is not None:
            update_data["fcm_token"] = fcm_token
        if language is not None:
            update_data["language"] = language
        if metadata is not None:
            update_data["metadata"] = metadata
        if is_active is not None:
            update_data["is_active"] = is_active

        if update_data:
            await FarmerProfile.filter(farmer_id=farmer_id).update(**update_data)

        # Update crops if provided
        if crops is not None:
            # Get existing crops
            existing_crops = await FarmerCrop.filter(farmer=profile).all()
            existing_crop_types = {c.crop_type for c in existing_crops}
            new_crop_types = set(crops)

            # Remove crops that are no longer in the list
            crops_to_remove = existing_crop_types - new_crop_types
            if crops_to_remove:
                await FarmerCrop.filter(
                    farmer=profile, crop_type__in=list(crops_to_remove)
                ).delete()

            # Add new crops
            crops_to_add = new_crop_types - existing_crop_types
            for crop_type in crops_to_add:
                await FarmerCrop.create(
                    id=uuid4(),
                    farmer=profile,
                    crop_type=crop_type,
                    is_active=True,
                )

        # Update fields if provided
        if field_ids is not None:
            # Get existing fields
            existing_fields = await FarmerField.filter(farmer=profile).all()
            existing_field_ids = {f.field_id for f in existing_fields}
            new_field_ids = set(field_ids)

            # Remove fields that are no longer in the list
            fields_to_remove = existing_field_ids - new_field_ids
            if fields_to_remove:
                await FarmerField.filter(
                    farmer=profile, field_id__in=list(fields_to_remove)
                ).delete()

            # Add new fields
            fields_to_add = new_field_ids - existing_field_ids
            for field_id in fields_to_add:
                await FarmerField.create(
                    id=uuid4(),
                    farmer=profile,
                    field_id=field_id,
                    is_active=True,
                )

        logger.info(f"Updated farmer profile {farmer_id}")

        # Return updated profile
        return await FarmerProfileRepository.get_by_farmer_id(farmer_id)

    @staticmethod
    async def delete(farmer_id: str) -> bool:
        """
        حذف ملف مزارع
        Delete farmer profile (also deletes associated crops and fields via CASCADE)
        """
        from .models import FarmerProfile

        deleted = await FarmerProfile.filter(farmer_id=farmer_id).delete()
        if deleted:
            logger.info(f"Deleted farmer profile {farmer_id}")
            return True
        return False

    @staticmethod
    async def get_all(
        tenant_id: str | None = None,
        governorate: str | None = None,
        is_active: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """
        الحصول على جميع ملفات المزارعين
        Get all farmer profiles with optional filters
        """
        from .models import FarmerProfile

        query = FarmerProfile.filter()

        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        if governorate:
            query = query.filter(governorate=governorate)

        if is_active is not None:
            query = query.filter(is_active=is_active)

        profiles = (
            await query.prefetch_related("farmer_crops", "farmer_fields")
            .offset(offset)
            .limit(limit)
            .all()
        )

        return profiles

    @staticmethod
    async def get_count(
        tenant_id: str | None = None,
        governorate: str | None = None,
        is_active: bool = True,
    ) -> int:
        """
        الحصول على عدد المزارعين
        Get count of farmer profiles
        """
        from .models import FarmerProfile

        query = FarmerProfile.filter()

        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        if governorate:
            query = query.filter(governorate=governorate)

        if is_active is not None:
            query = query.filter(is_active=is_active)

        return await query.count()

    @staticmethod
    async def find_by_criteria(
        governorates: list[str] | None = None,
        crops: list[str] | None = None,
        is_active: bool = True,
        tenant_id: str | None = None,
    ) -> list[Any]:
        """
        البحث عن مزارعين بناءً على معايير
        Find farmers by criteria (governorate, crops)
        """
        from .models import FarmerCrop, FarmerProfile

        query = FarmerProfile.filter(is_active=is_active)

        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        # Filter by governorate
        if governorates:
            query = query.filter(governorate__in=governorates)

        # Filter by crops (farmers who have at least one of these crops)
        if crops:
            # Get farmer IDs that have any of the specified crops
            farmer_ids_with_crops = await FarmerCrop.filter(
                crop_type__in=crops,
                is_active=True,
            ).values_list("farmer_id", flat=True)

            if farmer_ids_with_crops:
                query = query.filter(id__in=farmer_ids_with_crops)
            else:
                # No farmers found with these crops
                return []

        profiles = await query.prefetch_related("farmer_crops", "farmer_fields").all()
        return profiles

    @staticmethod
    async def update_last_login(farmer_id: str) -> bool:
        """
        تحديث آخر تسجيل دخول
        Update last login timestamp
        """
        from .models import FarmerProfile

        updated = await FarmerProfile.filter(farmer_id=farmer_id).update(
            last_login_at=datetime.utcnow()
        )
        return updated > 0

    @staticmethod
    async def get_farmer_crops(farmer_id: str) -> list[str]:
        """
        الحصول على محاصيل المزارع
        Get farmer's crop types
        """
        from .models import FarmerCrop, FarmerProfile

        profile = await FarmerProfile.filter(farmer_id=farmer_id).first()
        if not profile:
            return []

        crops = await FarmerCrop.filter(farmer=profile, is_active=True).all()
        return [crop.crop_type for crop in crops]

    @staticmethod
    async def get_farmer_fields(farmer_id: str) -> list[str]:
        """
        الحصول على حقول المزارع
        Get farmer's field IDs
        """
        from .models import FarmerField, FarmerProfile

        profile = await FarmerProfile.filter(farmer_id=farmer_id).first()
        if not profile:
            return []

        fields = await FarmerField.filter(farmer=profile, is_active=True).all()
        return [field.field_id for field in fields]
