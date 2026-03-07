"""
SAHOOL Notification Queue Processor
معالج طابور الإشعارات

Redis-based notification queue for reliable, scalable notification delivery.
Supports batch processing, retry logic, and priority queuing.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta, timezone
from enum import Enum, StrEnum
from typing import Any, Callable
from uuid import uuid4

logger = logging.getLogger("sahool-notifications.queue")

# Redis client imports
try:
    import redis.asyncio as redis
    from redis.asyncio import Redis

    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False
    logger.warning("Redis not installed. Install with: pip install redis")


class QueuePriority(StrEnum):
    """أولوية الطابور"""

    CRITICAL = "critical"  # Immediate processing
    HIGH = "high"  # Process within 1 minute
    MEDIUM = "medium"  # Standard processing
    LOW = "low"  # Process when resources available


class NotificationStatus(StrEnum):
    """حالة الإشعار في الطابور"""

    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class QueuedNotification:
    """إشعار في الطابور"""

    id: str
    user_id: str
    title: str
    title_ar: str
    body: str
    body_ar: str
    notification_type: str
    channel: str
    priority: QueuePriority
    data: dict[str, Any] = field(default_factory=dict)
    status: NotificationStatus = NotificationStatus.QUEUED
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    scheduled_at: datetime | None = None
    tenant_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "title_ar": self.title_ar,
            "body": self.body,
            "body_ar": self.body_ar,
            "notification_type": self.notification_type,
            "channel": self.channel,
            "priority": self.priority.value,
            "data": self.data,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat(),
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "tenant_id": self.tenant_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QueuedNotification":
        """إنشاء من قاموس"""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            title=data["title"],
            title_ar=data["title_ar"],
            body=data["body"],
            body_ar=data["body_ar"],
            notification_type=data["notification_type"],
            channel=data["channel"],
            priority=QueuePriority(data["priority"]),
            data=data.get("data", {}),
            status=NotificationStatus(data.get("status", "queued")),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            scheduled_at=datetime.fromisoformat(data["scheduled_at"]) if data.get("scheduled_at") else None,
            tenant_id=data.get("tenant_id"),
        )


class NotificationQueueProcessor:
    """
    معالج طابور الإشعارات المبني على Redis

    Features:
    - Priority-based queuing (critical, high, medium, low)
    - Batch processing for efficiency
    - Automatic retry with exponential backoff
    - Dead letter queue for failed notifications
    - Rate limiting per channel
    - Scheduled notifications support
    - Queue statistics and monitoring
    """

    # Queue names
    QUEUE_PREFIX = "sahool:notifications"
    PRIORITY_QUEUES = {
        QueuePriority.CRITICAL: f"{QUEUE_PREFIX}:critical",
        QueuePriority.HIGH: f"{QUEUE_PREFIX}:high",
        QueuePriority.MEDIUM: f"{QUEUE_PREFIX}:medium",
        QueuePriority.LOW: f"{QUEUE_PREFIX}:low",
    }
    PROCESSING_SET = f"{QUEUE_PREFIX}:processing"
    DEAD_LETTER_QUEUE = f"{QUEUE_PREFIX}:dead_letter"
    SCHEDULED_SET = f"{QUEUE_PREFIX}:scheduled"
    STATS_KEY = f"{QUEUE_PREFIX}:stats"

    def __init__(
        self,
        redis_url: str | None = None,
        batch_size: int = 100,
        processing_timeout: int = 60,  # seconds
        rate_limit_per_second: int = 50,
    ):
        """
        Initialize the queue processor

        Args:
            redis_url: Redis connection URL
            batch_size: Number of notifications to process per batch
            processing_timeout: Timeout for processing a notification
            rate_limit_per_second: Maximum notifications per second
        """
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.batch_size = batch_size
        self.processing_timeout = processing_timeout
        self.rate_limit_per_second = rate_limit_per_second

        self._redis: Redis | None = None
        self._running = False
        self._worker_tasks: list[asyncio.Task] = []
        self._handlers: dict[str, Callable] = {}

        logger.info("NotificationQueueProcessor initialized")

    async def connect(self) -> bool:
        """
        الاتصال بـ Redis

        Returns:
            True if connected successfully
        """
        if not _REDIS_AVAILABLE:
            logger.error("Redis package not available")
            return False

        try:
            self._redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await self._redis.ping()
            logger.info("Connected to Redis")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False

    async def disconnect(self):
        """قطع الاتصال بـ Redis"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Disconnected from Redis")

    def register_handler(self, channel: str, handler: Callable):
        """
        تسجيل معالج لقناة

        Args:
            channel: Channel name (push, sms, email, whatsapp)
            handler: Async function to handle notification sending
        """
        self._handlers[channel] = handler
        logger.info(f"Registered handler for channel: {channel}")

    async def enqueue(
        self,
        user_id: str,
        title: str,
        title_ar: str,
        body: str,
        body_ar: str,
        notification_type: str,
        channel: str,
        priority: QueuePriority = QueuePriority.MEDIUM,
        data: dict[str, Any] | None = None,
        scheduled_at: datetime | None = None,
        tenant_id: str | None = None,
    ) -> str:
        """
        إضافة إشعار للطابور

        Args:
            user_id: User ID
            title: Notification title (English)
            title_ar: Notification title (Arabic)
            body: Notification body (English)
            body_ar: Notification body (Arabic)
            notification_type: Type of notification
            channel: Delivery channel
            priority: Queue priority
            data: Additional data
            scheduled_at: Optional scheduled delivery time
            tenant_id: Optional tenant ID

        Returns:
            Notification ID
        """
        if not self._redis:
            raise RuntimeError("Not connected to Redis")

        notification = QueuedNotification(
            id=str(uuid4()),
            user_id=user_id,
            title=title,
            title_ar=title_ar,
            body=body,
            body_ar=body_ar,
            notification_type=notification_type,
            channel=channel,
            priority=priority,
            data=data or {},
            scheduled_at=scheduled_at,
            tenant_id=tenant_id,
        )

        # Serialize notification
        notification_json = json.dumps(notification.to_dict())

        if scheduled_at and scheduled_at > datetime.now(UTC):
            # Add to scheduled set with score as timestamp
            await self._redis.zadd(self.SCHEDULED_SET, {notification_json: scheduled_at.timestamp()})
            logger.debug(f"Scheduled notification {notification.id} for {scheduled_at}")
        else:
            # Add to priority queue
            queue_key = self.PRIORITY_QUEUES[priority]
            await self._redis.lpush(queue_key, notification_json)
            logger.debug(f"Enqueued notification {notification.id} to {priority.value} queue")

        # Update stats
        await self._increment_stat("enqueued")

        return notification.id

    async def enqueue_batch(
        self,
        notifications: list[dict[str, Any]],
        priority: QueuePriority = QueuePriority.MEDIUM,
    ) -> list[str]:
        """
        إضافة دفعة من الإشعارات

        Args:
            notifications: List of notification dictionaries
            priority: Queue priority for all notifications

        Returns:
            List of notification IDs
        """
        if not self._redis:
            raise RuntimeError("Not connected to Redis")

        ids = []
        queue_key = self.PRIORITY_QUEUES[priority]
        pipeline = self._redis.pipeline()

        for notif_data in notifications:
            notification = QueuedNotification(
                id=str(uuid4()),
                user_id=notif_data["user_id"],
                title=notif_data["title"],
                title_ar=notif_data["title_ar"],
                body=notif_data["body"],
                body_ar=notif_data["body_ar"],
                notification_type=notif_data["notification_type"],
                channel=notif_data["channel"],
                priority=priority,
                data=notif_data.get("data", {}),
                tenant_id=notif_data.get("tenant_id"),
            )

            notification_json = json.dumps(notification.to_dict())
            pipeline.lpush(queue_key, notification_json)
            ids.append(notification.id)

        await pipeline.execute()

        # Update stats
        await self._increment_stat("enqueued", count=len(ids))

        logger.info(f"Enqueued batch of {len(ids)} notifications")
        return ids

    async def process_one(self) -> QueuedNotification | None:
        """
        معالجة إشعار واحد

        Returns:
            Processed notification or None if queue is empty
        """
        if not self._redis:
            return None

        # Try queues in priority order
        for priority in [
            QueuePriority.CRITICAL,
            QueuePriority.HIGH,
            QueuePriority.MEDIUM,
            QueuePriority.LOW,
        ]:
            queue_key = self.PRIORITY_QUEUES[priority]

            # Move from queue to processing set atomically
            notification_json = await self._redis.rpoplpush(queue_key, self.PROCESSING_SET)

            if notification_json:
                try:
                    notification = QueuedNotification.from_dict(json.loads(notification_json))
                    notification.status = NotificationStatus.PROCESSING

                    # Process notification
                    success = await self._process_notification(notification)

                    # Remove from processing set
                    await self._redis.lrem(self.PROCESSING_SET, 1, notification_json)

                    if success:
                        notification.status = NotificationStatus.SENT
                        await self._increment_stat("sent")
                    else:
                        # Handle failure
                        await self._handle_failure(notification)

                    return notification

                except Exception as e:
                    logger.error(f"Error processing notification: {e}")
                    await self._increment_stat("errors")
                    return None

        return None

    async def _process_notification(self, notification: QueuedNotification) -> bool:
        """معالجة إشعار"""
        try:
            # Get handler for channel
            handler = self._handlers.get(notification.channel)

            if not handler:
                logger.warning(f"No handler for channel: {notification.channel}")
                return False

            # Call handler
            result = await handler(notification)

            if result:
                logger.info(f"Sent notification {notification.id} via {notification.channel}")
                return True
            else:
                logger.warning(f"Handler returned False for notification {notification.id}")
                return False

        except Exception as e:
            logger.error(f"Error in handler for {notification.channel}: {e}")
            return False

    async def _handle_failure(self, notification: QueuedNotification):
        """معالجة فشل الإرسال"""
        notification.retry_count += 1

        if notification.retry_count < notification.max_retries:
            # Schedule retry with exponential backoff
            notification.status = NotificationStatus.RETRYING
            delay = 2**notification.retry_count * 60  # 2, 4, 8 minutes
            retry_at = datetime.now(UTC) + timedelta(seconds=delay)

            notification_json = json.dumps(notification.to_dict())
            await self._redis.zadd(self.SCHEDULED_SET, {notification_json: retry_at.timestamp()})

            await self._increment_stat("retries")
            logger.info(f"Scheduled retry {notification.retry_count}/{notification.max_retries} for {notification.id}")

        else:
            # Move to dead letter queue
            notification.status = NotificationStatus.FAILED
            notification_json = json.dumps(notification.to_dict())
            await self._redis.lpush(self.DEAD_LETTER_QUEUE, notification_json)

            await self._increment_stat("dead_lettered")
            logger.warning(f"Moved notification {notification.id} to dead letter queue")

    async def process_scheduled(self):
        """معالجة الإشعارات المجدولة"""
        if not self._redis:
            return

        now = datetime.now(UTC).timestamp()

        # Get scheduled notifications that are due
        due_notifications = await self._redis.zrangebyscore(
            self.SCHEDULED_SET, "-inf", now, start=0, num=self.batch_size
        )

        if due_notifications:
            # Move to priority queues
            for notification_json in due_notifications:
                notification = QueuedNotification.from_dict(json.loads(notification_json))

                # Remove from scheduled set
                await self._redis.zrem(self.SCHEDULED_SET, notification_json)

                # Reset status and add to queue
                notification.status = NotificationStatus.QUEUED
                queue_key = self.PRIORITY_QUEUES[notification.priority]
                await self._redis.lpush(queue_key, json.dumps(notification.to_dict()))

            logger.info(f"Moved {len(due_notifications)} scheduled notifications to queues")

    async def _worker(self, worker_id: int):
        """عامل معالجة"""
        logger.info(f"Worker {worker_id} started")

        while self._running:
            try:
                # Process scheduled notifications first
                await self.process_scheduled()

                # Process queue
                notification = await self.process_one()

                if notification is None:
                    # No notifications, wait a bit
                    await asyncio.sleep(0.5)
                else:
                    # Rate limiting
                    await asyncio.sleep(1 / self.rate_limit_per_second)

            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(5)

        logger.info(f"Worker {worker_id} stopped")

    async def start(self, num_workers: int = 4):
        """
        بدء معالجة الطابور

        Args:
            num_workers: Number of worker tasks
        """
        if self._running:
            logger.warning("Queue processor already running")
            return

        # Connect to Redis if not connected
        if not self._redis:
            connected = await self.connect()
            if not connected:
                logger.error("Cannot start: Redis connection failed")
                return

        self._running = True

        # Start workers
        for i in range(num_workers):
            task = asyncio.create_task(self._worker(i))
            self._worker_tasks.append(task)

        logger.info(f"Started queue processor with {num_workers} workers")

    async def stop(self):
        """إيقاف معالجة الطابور"""
        if not self._running:
            return

        self._running = False

        # Wait for workers to finish
        for task in self._worker_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._worker_tasks.clear()

        logger.info("Stopped queue processor")

    async def get_queue_stats(self) -> dict[str, Any]:
        """
        الحصول على إحصائيات الطابور

        Returns:
            Queue statistics
        """
        if not self._redis:
            return {}

        stats = {
            "connected": True,
            "queues": {},
            "processing": 0,
            "scheduled": 0,
            "dead_letter": 0,
        }

        # Get queue lengths
        for priority, queue_key in self.PRIORITY_QUEUES.items():
            stats["queues"][priority.value] = await self._redis.llen(queue_key)

        # Get processing count
        stats["processing"] = await self._redis.llen(self.PROCESSING_SET)

        # Get scheduled count
        stats["scheduled"] = await self._redis.zcard(self.SCHEDULED_SET)

        # Get dead letter count
        stats["dead_letter"] = await self._redis.llen(self.DEAD_LETTER_QUEUE)

        # Get cumulative stats
        cumulative = await self._redis.hgetall(self.STATS_KEY)
        stats["cumulative"] = {k: int(v) for k, v in cumulative.items()} if cumulative else {}

        return stats

    async def _increment_stat(self, stat_name: str, count: int = 1):
        """زيادة إحصائية"""
        if self._redis:
            await self._redis.hincrby(self.STATS_KEY, stat_name, count)

    async def get_dead_letter_notifications(self, limit: int = 100) -> list[QueuedNotification]:
        """
        الحصول على الإشعارات في طابور الرسائل الميتة

        Args:
            limit: Maximum number to return

        Returns:
            List of failed notifications
        """
        if not self._redis:
            return []

        notifications_json = await self._redis.lrange(self.DEAD_LETTER_QUEUE, 0, limit - 1)

        return [QueuedNotification.from_dict(json.loads(n)) for n in notifications_json]

    async def requeue_dead_letter(self, notification_id: str) -> bool:
        """
        إعادة إشعار من طابور الرسائل الميتة

        Args:
            notification_id: Notification ID

        Returns:
            True if requeued successfully
        """
        if not self._redis:
            return False

        # Find notification in dead letter queue
        all_dead = await self._redis.lrange(self.DEAD_LETTER_QUEUE, 0, -1)

        for notification_json in all_dead:
            notification = QueuedNotification.from_dict(json.loads(notification_json))

            if notification.id == notification_id:
                # Remove from dead letter queue
                await self._redis.lrem(self.DEAD_LETTER_QUEUE, 1, notification_json)

                # Reset retry count and status
                notification.retry_count = 0
                notification.status = NotificationStatus.QUEUED

                # Add back to queue
                queue_key = self.PRIORITY_QUEUES[notification.priority]
                await self._redis.lpush(queue_key, json.dumps(notification.to_dict()))

                logger.info(f"Requeued notification {notification_id} from dead letter queue")
                return True

        return False

    async def clear_dead_letter(self) -> int:
        """
        مسح طابور الرسائل الميتة

        Returns:
            Number of notifications cleared
        """
        if not self._redis:
            return 0

        count = await self._redis.llen(self.DEAD_LETTER_QUEUE)
        await self._redis.delete(self.DEAD_LETTER_QUEUE)

        logger.info(f"Cleared {count} notifications from dead letter queue")
        return count


# =============================================================================
# Global instance
# =============================================================================

_queue_processor: NotificationQueueProcessor | None = None


def get_queue_processor() -> NotificationQueueProcessor:
    """
    الحصول على معالج الطابور العمومي

    Returns:
        NotificationQueueProcessor instance
    """
    global _queue_processor

    if _queue_processor is None:
        _queue_processor = NotificationQueueProcessor()

    return _queue_processor
