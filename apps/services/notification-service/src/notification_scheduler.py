"""
SAHOOL Notification Scheduler
جدولة الإشعارات

Features:
- Schedule notifications (daily, weekly reminders)
- Batch processing for multiple recipients
- Retry logic for failed sends
- Priority queue management
- Quiet hours support
- Rate limiting
"""

import asyncio
import contextlib
import heapq
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, time, timedelta, timezone
from enum import Enum, StrEnum
from typing import Any

from .firebase_client import FirebaseClient, NotificationPriority, get_firebase_client
from .notification_types import NotificationPayload

logger = logging.getLogger(__name__)


class ScheduleFrequency(StrEnum):
    """تكرار الجدولة"""

    ONCE = "once"  # مرة واحدة
    DAILY = "daily"  # يومياً
    WEEKLY = "weekly"  # أسبوعياً
    MONTHLY = "monthly"  # شهرياً


@dataclass(order=True)
class ScheduledNotification:
    """إشعار مجدول"""

    # Priority queue ordering (compare=True for heap ordering)
    scheduled_time: datetime = field(compare=True)
    priority: int = field(compare=True, default=2)  # 0=critical, 1=high, 2=medium, 3=low

    # Notification data (all non-compare fields must have defaults after priority)
    notification_id: str = field(compare=False, default="")
    payload: NotificationPayload | None = field(compare=False, default=None)
    recipient_token: str = field(compare=False, default="")
    frequency: ScheduleFrequency = field(compare=False, default=ScheduleFrequency.ONCE)

    # Retry configuration
    max_retries: int = field(compare=False, default=3)
    retry_count: int = field(compare=False, default=0)
    last_attempt: datetime | None = field(compare=False, default=None)

    # Status
    status: str = field(compare=False, default="pending")  # pending, sent, failed, cancelled

    def __post_init__(self):
        """Validate required fields when status indicates active use."""
        if self.status == "pending" and not self.notification_id:
            raise ValueError("notification_id is required for pending notifications")

    def should_retry(self) -> bool:
        """هل يجب إعادة المحاولة؟"""
        return self.retry_count < self.max_retries and self.status == "failed"

    def get_next_scheduled_time(self) -> datetime | None:
        """الحصول على الوقت المجدول التالي"""
        if self.frequency == ScheduleFrequency.ONCE:
            return None
        elif self.frequency == ScheduleFrequency.DAILY:
            return self.scheduled_time + timedelta(days=1)
        elif self.frequency == ScheduleFrequency.WEEKLY:
            return self.scheduled_time + timedelta(weeks=1)
        elif self.frequency == ScheduleFrequency.MONTHLY:
            # Approximate month as 30 days
            return self.scheduled_time + timedelta(days=30)
        return None


class NotificationScheduler:
    """
    جدولة وإدارة الإشعارات

    Features:
    - Priority-based scheduling
    - Batch processing
    - Retry failed notifications
    - Respect quiet hours
    - Rate limiting per user
    """

    def __init__(
        self,
        firebase_client: FirebaseClient | None = None,
        batch_size: int = 500,  # Firebase multicast limit
        rate_limit_per_minute: int = 100,
        quiet_hours_start: time = time(22, 0),  # 10 PM
        quiet_hours_end: time = time(6, 0),  # 6 AM
    ):
        self.firebase_client = firebase_client or get_firebase_client()
        self.batch_size = batch_size
        self.rate_limit_per_minute = rate_limit_per_minute
        self.quiet_hours_start = quiet_hours_start
        self.quiet_hours_end = quiet_hours_end

        # Priority queue for scheduled notifications
        self._queue: list[ScheduledNotification] = []
        self._notification_map: dict[str, ScheduledNotification] = {}

        # Rate limiting
        self._send_timestamps: dict[str, list[datetime]] = defaultdict(list)

        # Running state
        self._running = False
        self._worker_task: asyncio.Task | None = None

        logger.info("NotificationScheduler initialized")

    def schedule_notification(
        self,
        notification_id: str,
        payload: NotificationPayload,
        recipient_token: str,
        scheduled_time: datetime,
        frequency: ScheduleFrequency = ScheduleFrequency.ONCE,
        max_retries: int = 3,
    ) -> bool:
        """
        جدولة إشعار

        Args:
            notification_id: معرف فريد للإشعار
            payload: حمولة الإشعار
            recipient_token: FCM token للمستلم
            scheduled_time: وقت الإرسال المجدول
            frequency: تكرار الإشعار
            max_retries: عدد المحاولات عند الفشل

        Returns:
            True if scheduled successfully
        """
        # Convert priority to int for queue ordering
        priority_map = {
            NotificationPriority.CRITICAL: 0,
            NotificationPriority.HIGH: 1,
            NotificationPriority.MEDIUM: 2,
            NotificationPriority.LOW: 3,
        }
        priority_int = priority_map.get(payload.priority, 2)

        scheduled_notif = ScheduledNotification(
            notification_id=notification_id,
            scheduled_time=scheduled_time,
            priority=priority_int,
            payload=payload,
            recipient_token=recipient_token,
            frequency=frequency,
            max_retries=max_retries,
        )

        # Add to queue
        heapq.heappush(self._queue, scheduled_notif)
        self._notification_map[notification_id] = scheduled_notif

        logger.info(
            f"📅 Scheduled notification {notification_id} for {scheduled_time} "
            f"(priority: {payload.priority}, frequency: {frequency})"
        )
        return True

    def schedule_batch(
        self,
        payload: NotificationPayload,
        recipient_tokens: list[str],
        scheduled_time: datetime,
        frequency: ScheduleFrequency = ScheduleFrequency.ONCE,
    ) -> int:
        """
        جدولة إشعار لعدة مستلمين

        Args:
            payload: حمولة الإشعار
            recipient_tokens: قائمة FCM tokens
            scheduled_time: وقت الإرسال
            frequency: تكرار الإشعار

        Returns:
            Number of notifications scheduled
        """
        count = 0
        for i, token in enumerate(recipient_tokens):
            notification_id = f"{payload.notification_type}_{scheduled_time.timestamp()}_{i}"
            if self.schedule_notification(
                notification_id=notification_id,
                payload=payload,
                recipient_token=token,
                scheduled_time=scheduled_time,
                frequency=frequency,
            ):
                count += 1

        logger.info(f"📅 Scheduled batch of {count} notifications")
        return count

    def cancel_notification(self, notification_id: str) -> bool:
        """
        إلغاء إشعار مجدول

        Args:
            notification_id: معرف الإشعار

        Returns:
            True if cancelled
        """
        if notification_id in self._notification_map:
            notif = self._notification_map[notification_id]
            notif.status = "cancelled"
            logger.info(f"🚫 Cancelled notification {notification_id}")
            return True
        return False

    def is_quiet_hours(self, check_time: datetime | None = None) -> bool:
        """
        هل الوقت الحالي ضمن ساعات الهدوء؟

        Args:
            check_time: الوقت للتحقق منه (الافتراضي: الآن)

        Returns:
            True if in quiet hours
        """
        if check_time is None:
            check_time = datetime.now()

        current_time = check_time.time()

        # Handle quiet hours that span midnight
        if self.quiet_hours_start > self.quiet_hours_end:
            return current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end
        else:
            return self.quiet_hours_start <= current_time <= self.quiet_hours_end

    def can_send_to_user(self, recipient_token: str) -> bool:
        """
        هل يمكن الإرسال للمستخدم؟ (فحص حد المعدل)

        Args:
            recipient_token: FCM token

        Returns:
            True if within rate limit
        """
        now = datetime.now(UTC)
        one_minute_ago = now - timedelta(minutes=1)

        # Clean old timestamps
        self._send_timestamps[recipient_token] = [
            ts for ts in self._send_timestamps[recipient_token] if ts > one_minute_ago
        ]

        # Check rate limit
        return len(self._send_timestamps[recipient_token]) < self.rate_limit_per_minute

    def record_send(self, recipient_token: str):
        """تسجيل إرسال للمستخدم"""
        self._send_timestamps[recipient_token].append(datetime.now(UTC))

    async def _send_notification(self, scheduled_notif: ScheduledNotification) -> bool:
        """
        إرسال إشعار مجدول

        Args:
            scheduled_notif: الإشعار المجدول

        Returns:
            True if sent successfully
        """
        payload = scheduled_notif.payload
        token = scheduled_notif.recipient_token

        # Check rate limit
        if not self.can_send_to_user(token):
            logger.warning(f"Rate limit exceeded for {token[:20]}...")
            return False

        try:
            # Send via Firebase
            result = self.firebase_client.send_notification(
                token=token,
                title=payload.title,
                body=payload.body,
                title_ar=payload.title_ar,
                body_ar=payload.body_ar,
                data=payload.data,
                image_url=payload.image_url,
                priority=payload.priority,
            )

            if result:
                scheduled_notif.status = "sent"
                scheduled_notif.last_attempt = datetime.now(UTC)
                self.record_send(token)
                logger.info(f"✅ Sent notification {scheduled_notif.notification_id}")

                # Schedule next occurrence if recurring
                next_time = scheduled_notif.get_next_scheduled_time()
                if next_time:
                    self.schedule_notification(
                        notification_id=f"{scheduled_notif.notification_id}_next",
                        payload=payload,
                        recipient_token=token,
                        scheduled_time=next_time,
                        frequency=scheduled_notif.frequency,
                        max_retries=scheduled_notif.max_retries,
                    )

                return True
            else:
                raise Exception("Firebase send returned None")

        except Exception as e:
            logger.error(f"❌ Failed to send notification {scheduled_notif.notification_id}: {e}")
            scheduled_notif.status = "failed"
            scheduled_notif.retry_count += 1
            scheduled_notif.last_attempt = datetime.now(UTC)

            # Retry if possible
            if scheduled_notif.should_retry():
                # Reschedule with exponential backoff
                retry_delay = timedelta(minutes=2**scheduled_notif.retry_count)
                scheduled_notif.scheduled_time = datetime.now(UTC) + retry_delay
                heapq.heappush(self._queue, scheduled_notif)
                logger.info(
                    f"🔄 Retry {scheduled_notif.retry_count}/{scheduled_notif.max_retries} scheduled in {retry_delay}"
                )

            return False

    async def _process_batch(self, notifications: list[ScheduledNotification]) -> dict[str, int]:
        """
        معالجة دفعة من الإشعارات

        Args:
            notifications: قائمة الإشعارات

        Returns:
            Stats dict with success/failure counts
        """
        # Group by payload (same notification content)
        grouped: dict[str, list[ScheduledNotification]] = defaultdict(list)
        for notif in notifications:
            # Create a key from notification content
            key = f"{notif.payload.notification_type}_{notif.payload.title_ar}"
            grouped[key].append(notif)

        stats = {"success": 0, "failed": 0, "rate_limited": 0}

        # Send each group using multicast
        for _group_key, group_notifs in grouped.items():
            # Filter by rate limit
            sendable = [n for n in group_notifs if self.can_send_to_user(n.recipient_token)]
            rate_limited = len(group_notifs) - len(sendable)
            stats["rate_limited"] += rate_limited

            if not sendable:
                continue

            # Extract tokens
            tokens = [n.recipient_token for n in sendable]

            # Send multicast
            payload = sendable[0].payload
            result = self.firebase_client.send_multicast(
                tokens=tokens,
                title=payload.title,
                body=payload.body,
                title_ar=payload.title_ar,
                body_ar=payload.body_ar,
                data=payload.data,
                priority=payload.priority,
            )

            # Update stats
            stats["success"] += result.get("success_count", 0)
            stats["failed"] += result.get("failure_count", 0)

            # Update notification statuses
            for i, notif in enumerate(sendable):
                if i < len(result.get("responses", [])):
                    resp = result["responses"][i]
                    if resp.get("success"):
                        notif.status = "sent"
                        self.record_send(notif.recipient_token)
                    else:
                        notif.status = "failed"
                        notif.retry_count += 1

        return stats

    async def _worker(self):
        """عامل معالجة الإشعارات"""
        logger.info("📱 Notification worker started")

        while self._running:
            try:
                now = datetime.now(UTC)
                batch: list[ScheduledNotification] = []

                # Collect due notifications
                while self._queue and self._queue[0].scheduled_time <= now:
                    notif = heapq.heappop(self._queue)

                    # Skip cancelled notifications
                    if notif.status == "cancelled":
                        continue

                    # Skip if in quiet hours and not critical
                    if self.is_quiet_hours() and notif.priority > 0:
                        # Reschedule for after quiet hours
                        next_morning = now.replace(
                            hour=self.quiet_hours_end.hour,
                            minute=self.quiet_hours_end.minute,
                            second=0,
                        )
                        if next_morning <= now:
                            next_morning += timedelta(days=1)

                        notif.scheduled_time = next_morning
                        heapq.heappush(self._queue, notif)
                        continue

                    batch.append(notif)

                    # Process in batches
                    if len(batch) >= self.batch_size:
                        break

                # Send batch
                if batch:
                    stats = await self._process_batch(batch)
                    logger.info(
                        f"📊 Batch processed: {stats['success']} sent, "
                        f"{stats['failed']} failed, {stats['rate_limited']} rate-limited"
                    )

                # Sleep before next check
                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(30)

        logger.info("📱 Notification worker stopped")

    async def start(self):
        """بدء جدولة الإشعارات"""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._worker())
        logger.info("✅ Notification scheduler started")

    async def stop(self):
        """إيقاف جدولة الإشعارات"""
        if not self._running:
            return

        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._worker_task

        logger.info("⏹️ Notification scheduler stopped")

    def get_stats(self) -> dict[str, Any]:
        """الحصول على إحصائيات الجدولة"""
        pending = sum(1 for n in self._notification_map.values() if n.status == "pending")
        sent = sum(1 for n in self._notification_map.values() if n.status == "sent")
        failed = sum(1 for n in self._notification_map.values() if n.status == "failed")
        cancelled = sum(1 for n in self._notification_map.values() if n.status == "cancelled")

        return {
            "total_scheduled": len(self._notification_map),
            "pending": pending,
            "sent": sent,
            "failed": failed,
            "cancelled": cancelled,
            "queue_size": len(self._queue),
            "is_running": self._running,
            "in_quiet_hours": self.is_quiet_hours(),
        }


# Global scheduler instance
_scheduler: NotificationScheduler | None = None


def get_scheduler() -> NotificationScheduler:
    """
    الحصول على instance عام من NotificationScheduler

    Returns:
        NotificationScheduler instance
    """
    global _scheduler

    if _scheduler is None:
        _scheduler = NotificationScheduler()

    return _scheduler
