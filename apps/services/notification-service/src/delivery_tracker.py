"""
SAHOOL Notification Delivery Tracker
متتبع تسليم الإشعارات

Real-time delivery status tracking with webhooks, callbacks,
and comprehensive delivery analytics.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timezone
from enum import Enum, StrEnum
from typing import Any, Callable
from uuid import UUID

import httpx

from .models import Notification, NotificationLog
from .repository import NotificationLogRepository, NotificationRepository

logger = logging.getLogger("sahool-notifications.delivery-tracker")


class DeliveryStatus(StrEnum):
    """حالة التسليم"""

    QUEUED = "queued"  # في الطابور
    SENDING = "sending"  # جاري الإرسال
    SENT = "sent"  # تم الإرسال
    DELIVERED = "delivered"  # تم التسليم للجهاز
    READ = "read"  # تمت القراءة
    FAILED = "failed"  # فشل الإرسال
    BOUNCED = "bounced"  # ارتد (email/sms)
    EXPIRED = "expired"  # انتهت الصلاحية


class DeliveryEventType(StrEnum):
    """نوع حدث التسليم"""

    STATUS_CHANGE = "status_change"
    RETRY_SCHEDULED = "retry_scheduled"
    DELIVERY_CONFIRMED = "delivery_confirmed"
    READ_RECEIPT = "read_receipt"
    FAILURE = "failure"
    BOUNCE = "bounce"


@dataclass
class DeliveryEvent:
    """حدث تسليم"""

    notification_id: str
    event_type: DeliveryEventType
    status: DeliveryStatus
    channel: str
    timestamp: datetime
    details: dict[str, Any] | None = None
    provider_response: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "notification_id": self.notification_id,
            "event_type": self.event_type.value,
            "status": self.status.value,
            "channel": self.channel,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "provider_response": self.provider_response,
        }


class DeliveryTracker:
    """
    متتبع تسليم الإشعارات

    Features:
    - Real-time status tracking
    - Webhook callbacks for status updates
    - Provider response logging
    - Delivery analytics
    - Read receipt tracking
    """

    def __init__(self):
        self._callbacks: list[Callable[[DeliveryEvent], Any]] = []
        self._webhook_urls: list[str] = []
        self._http_client: httpx.AsyncClient | None = None

    async def start(self):
        """بدء المتتبع"""
        self._http_client = httpx.AsyncClient(timeout=10.0)
        logger.info("Delivery tracker started")

    async def stop(self):
        """إيقاف المتتبع"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        logger.info("Delivery tracker stopped")

    def register_callback(self, callback: Callable[[DeliveryEvent], Any]):
        """
        تسجيل callback لأحداث التسليم

        Args:
            callback: Async function to call on delivery events
        """
        self._callbacks.append(callback)
        logger.info(f"Registered delivery callback: {callback.__name__}")

    def register_webhook(self, url: str):
        """
        تسجيل webhook لأحداث التسليم

        Args:
            url: Webhook URL to call
        """
        self._webhook_urls.append(url)
        logger.info(f"Registered delivery webhook: {url}")

    async def track_status_change(
        self,
        notification_id: str,
        new_status: DeliveryStatus,
        channel: str,
        details: dict[str, Any] | None = None,
        provider_response: dict[str, Any] | None = None,
    ):
        """
        تتبع تغيير حالة التسليم

        Args:
            notification_id: Notification UUID
            new_status: New delivery status
            channel: Delivery channel
            details: Additional details
            provider_response: Response from provider (FCM, Twilio, etc.)
        """
        try:
            notif_uuid = UUID(notification_id)

            # Create delivery event
            event = DeliveryEvent(
                notification_id=notification_id,
                event_type=DeliveryEventType.STATUS_CHANGE,
                status=new_status,
                channel=channel,
                timestamp=datetime.now(UTC),
                details=details,
                provider_response=provider_response,
            )

            # Update notification status in database
            if new_status == DeliveryStatus.SENT:
                await NotificationRepository.update_status(notif_uuid, status="sent", sent_at=datetime.now(UTC))
            elif new_status == DeliveryStatus.FAILED:
                await NotificationRepository.update_status(notif_uuid, status="failed")
            elif new_status == DeliveryStatus.READ:
                await NotificationRepository.mark_as_read(notif_uuid)

            # Log delivery attempt
            await NotificationLogRepository.create_log(
                notification_id=notif_uuid,
                channel=channel,
                status=new_status.value,
                error_message=details.get("error") if details else None,
                provider_response=provider_response,
                provider_message_id=provider_response.get("message_id") if provider_response else None,
            )

            # Trigger callbacks and webhooks
            await self._trigger_event(event)

            logger.info(f"Tracked status change for {notification_id}: {new_status.value}")

        except Exception as e:
            logger.error(f"Error tracking status change: {e}")

    async def track_delivery_confirmation(
        self,
        notification_id: str,
        channel: str,
        provider_message_id: str,
        delivered_at: datetime | None = None,
    ):
        """
        تأكيد التسليم من المزود

        Args:
            notification_id: Notification UUID
            channel: Delivery channel
            provider_message_id: Message ID from provider
            delivered_at: Delivery timestamp
        """
        try:
            event = DeliveryEvent(
                notification_id=notification_id,
                event_type=DeliveryEventType.DELIVERY_CONFIRMED,
                status=DeliveryStatus.DELIVERED,
                channel=channel,
                timestamp=delivered_at or datetime.now(UTC),
                provider_response={"message_id": provider_message_id},
            )

            await self._trigger_event(event)

            logger.info(f"Delivery confirmed for {notification_id} via {channel}")

        except Exception as e:
            logger.error(f"Error tracking delivery confirmation: {e}")

    async def track_read_receipt(
        self,
        notification_id: str,
        channel: str,
        read_at: datetime | None = None,
    ):
        """
        تتبع تأكيد القراءة

        Args:
            notification_id: Notification UUID
            channel: Channel where notification was read
            read_at: Read timestamp
        """
        try:
            notif_uuid = UUID(notification_id)

            # Mark as read in database
            await NotificationRepository.mark_as_read(notif_uuid, read_at=read_at)

            event = DeliveryEvent(
                notification_id=notification_id,
                event_type=DeliveryEventType.READ_RECEIPT,
                status=DeliveryStatus.READ,
                channel=channel,
                timestamp=read_at or datetime.now(UTC),
            )

            await self._trigger_event(event)

            logger.info(f"Read receipt tracked for {notification_id}")

        except Exception as e:
            logger.error(f"Error tracking read receipt: {e}")

    async def track_failure(
        self,
        notification_id: str,
        channel: str,
        error_code: str | None = None,
        error_message: str | None = None,
        provider_response: dict[str, Any] | None = None,
    ):
        """
        تتبع فشل التسليم

        Args:
            notification_id: Notification UUID
            channel: Delivery channel
            error_code: Error code from provider
            error_message: Error message
            provider_response: Full provider response
        """
        try:
            notif_uuid = UUID(notification_id)

            # Update status to failed
            await NotificationRepository.update_status(notif_uuid, status="failed")

            # Log failure
            await NotificationLogRepository.create_log(
                notification_id=notif_uuid,
                channel=channel,
                status="failed",
                error_message=error_message,
                provider_response=provider_response,
            )

            event = DeliveryEvent(
                notification_id=notification_id,
                event_type=DeliveryEventType.FAILURE,
                status=DeliveryStatus.FAILED,
                channel=channel,
                timestamp=datetime.now(UTC),
                details={
                    "error_code": error_code,
                    "error_message": error_message,
                },
                provider_response=provider_response,
            )

            await self._trigger_event(event)

            logger.warning(f"Tracked failure for {notification_id}: {error_message}")

        except Exception as e:
            logger.error(f"Error tracking failure: {e}")

    async def track_bounce(
        self,
        notification_id: str,
        channel: str,
        bounce_type: str,  # hard, soft
        bounce_reason: str | None = None,
    ):
        """
        تتبع ارتداد الرسالة

        Args:
            notification_id: Notification UUID
            channel: Delivery channel (email, sms)
            bounce_type: Type of bounce (hard, soft)
            bounce_reason: Reason for bounce
        """
        try:
            notif_uuid = UUID(notification_id)

            # Log bounce
            await NotificationLogRepository.create_log(
                notification_id=notif_uuid,
                channel=channel,
                status="bounced",
                error_message=f"{bounce_type} bounce: {bounce_reason}",
            )

            event = DeliveryEvent(
                notification_id=notification_id,
                event_type=DeliveryEventType.BOUNCE,
                status=DeliveryStatus.BOUNCED,
                channel=channel,
                timestamp=datetime.now(UTC),
                details={
                    "bounce_type": bounce_type,
                    "bounce_reason": bounce_reason,
                },
            )

            await self._trigger_event(event)

            logger.warning(f"Tracked bounce for {notification_id}: {bounce_type} - {bounce_reason}")

        except Exception as e:
            logger.error(f"Error tracking bounce: {e}")

    async def get_delivery_timeline(self, notification_id: str) -> list[dict[str, Any]]:
        """
        الحصول على الجدول الزمني للتسليم

        Args:
            notification_id: Notification UUID

        Returns:
            List of delivery events in chronological order
        """
        try:
            notif_uuid = UUID(notification_id)

            # Get all logs for this notification
            logs = await NotificationLogRepository.get_notification_logs(notif_uuid)

            timeline = [
                {
                    "timestamp": log.attempted_at.isoformat(),
                    "channel": log.channel,
                    "status": log.status,
                    "error_message": log.error_message,
                    "provider_message_id": log.provider_message_id,
                    "retry_count": log.retry_count,
                }
                for log in sorted(logs, key=lambda x: x.attempted_at)
            ]

            return timeline

        except Exception as e:
            logger.error(f"Error getting delivery timeline: {e}")
            return []

    async def get_delivery_stats(
        self,
        channel: str | None = None,
        hours: int = 24,
    ) -> dict[str, Any]:
        """
        الحصول على إحصائيات التسليم

        Args:
            channel: Optional channel filter
            hours: Number of hours to analyze

        Returns:
            Delivery statistics
        """
        try:
            from datetime import timedelta

            start_time = datetime.now(UTC) - timedelta(hours=hours)

            # Build query
            query = NotificationLog.filter(attempted_at__gte=start_time)
            if channel:
                query = query.filter(channel=channel)

            # Get counts by status
            total = await query.count()
            sent = await query.filter(status="sent").count()
            failed = await query.filter(status="failed").count()
            bounced = await query.filter(status="bounced").count()

            return {
                "period_hours": hours,
                "channel": channel or "all",
                "total_attempts": total,
                "sent": sent,
                "failed": failed,
                "bounced": bounced,
                "success_rate": round((sent / total * 100) if total > 0 else 0, 2),
                "failure_rate": round((failed / total * 100) if total > 0 else 0, 2),
                "bounce_rate": round((bounced / total * 100) if total > 0 else 0, 2),
            }

        except Exception as e:
            logger.error(f"Error getting delivery stats: {e}")
            return {}

    async def _trigger_event(self, event: DeliveryEvent):
        """تفعيل callbacks و webhooks"""

        # Trigger callbacks
        for callback in self._callbacks:
            try:
                result = callback(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Error in delivery callback: {e}")

        # Trigger webhooks
        if self._http_client and self._webhook_urls:
            for url in self._webhook_urls:
                try:
                    await self._http_client.post(
                        url,
                        json=event.to_dict(),
                        headers={"Content-Type": "application/json"},
                    )
                except Exception as e:
                    logger.error(f"Error calling webhook {url}: {e}")


# =============================================================================
# FCM Delivery Callbacks
# =============================================================================


async def handle_fcm_callback(
    notification_id: str,
    message_id: str,
    status: str,
    error_code: str | None = None,
):
    """
    معالجة callback من Firebase

    Args:
        notification_id: Notification UUID
        message_id: FCM message ID
        status: Delivery status from FCM
        error_code: Optional error code
    """
    tracker = get_delivery_tracker()

    if status == "success":
        await tracker.track_status_change(
            notification_id=notification_id,
            new_status=DeliveryStatus.SENT,
            channel="push",
            provider_response={"message_id": message_id},
        )
    elif status == "failed":
        await tracker.track_failure(
            notification_id=notification_id,
            channel="push",
            error_code=error_code,
            provider_response={"message_id": message_id, "error_code": error_code},
        )


async def handle_sms_callback(
    notification_id: str,
    message_sid: str,
    status: str,
    error_code: str | None = None,
    error_message: str | None = None,
):
    """
    معالجة callback من Twilio

    Args:
        notification_id: Notification UUID
        message_sid: Twilio message SID
        status: Delivery status from Twilio
        error_code: Optional error code
        error_message: Optional error message
    """
    tracker = get_delivery_tracker()

    status_map = {
        "queued": DeliveryStatus.QUEUED,
        "sending": DeliveryStatus.SENDING,
        "sent": DeliveryStatus.SENT,
        "delivered": DeliveryStatus.DELIVERED,
        "undelivered": DeliveryStatus.FAILED,
        "failed": DeliveryStatus.FAILED,
    }

    delivery_status = status_map.get(status, DeliveryStatus.SENT)

    if delivery_status in [DeliveryStatus.FAILED]:
        await tracker.track_failure(
            notification_id=notification_id,
            channel="sms",
            error_code=error_code,
            error_message=error_message,
            provider_response={"message_sid": message_sid},
        )
    else:
        await tracker.track_status_change(
            notification_id=notification_id,
            new_status=delivery_status,
            channel="sms",
            provider_response={"message_sid": message_sid},
        )


async def handle_email_callback(
    notification_id: str,
    message_id: str,
    event_type: str,  # delivered, opened, bounced, dropped
    details: dict[str, Any] | None = None,
):
    """
    معالجة callback من SendGrid

    Args:
        notification_id: Notification UUID
        message_id: SendGrid message ID
        event_type: Event type from SendGrid
        details: Additional event details
    """
    tracker = get_delivery_tracker()

    if event_type == "delivered":
        await tracker.track_delivery_confirmation(
            notification_id=notification_id,
            channel="email",
            provider_message_id=message_id,
        )
    elif event_type == "opened":
        await tracker.track_read_receipt(
            notification_id=notification_id,
            channel="email",
        )
    elif event_type == "bounced":
        bounce_type = details.get("bounce_type", "unknown") if details else "unknown"
        await tracker.track_bounce(
            notification_id=notification_id,
            channel="email",
            bounce_type=bounce_type,
            bounce_reason=details.get("reason") if details else None,
        )
    elif event_type == "dropped":
        await tracker.track_failure(
            notification_id=notification_id,
            channel="email",
            error_message="Email dropped by provider",
            provider_response={
                "message_id": message_id,
                "reason": details.get("reason") if details else None,
            },
        )


# =============================================================================
# Global instance
# =============================================================================

_delivery_tracker: DeliveryTracker | None = None


def get_delivery_tracker() -> DeliveryTracker:
    """
    الحصول على متتبع التسليم العمومي

    Returns:
        DeliveryTracker instance
    """
    global _delivery_tracker

    if _delivery_tracker is None:
        _delivery_tracker = DeliveryTracker()

    return _delivery_tracker
