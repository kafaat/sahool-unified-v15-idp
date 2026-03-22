"""
Tests for src/queue_processor.py - Queue Processor

Covers:
- QueuePriority and NotificationStatus enums
- QueuedNotification dataclass (to_dict, from_dict)
- NotificationQueueProcessor init, connect, handlers
"""

import pytest
from datetime import UTC, datetime

from src.queue_processor import (
    NotificationQueueProcessor,
    NotificationStatus,
    QueuePriority,
    QueuedNotification,
    get_queue_processor,
)


# ─────────────────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────────────────


class TestQueuePriority:
    def test_all_priorities(self):
        assert QueuePriority.CRITICAL == "critical"
        assert QueuePriority.HIGH == "high"
        assert QueuePriority.MEDIUM == "medium"
        assert QueuePriority.LOW == "low"


class TestNotificationStatus:
    def test_all_statuses(self):
        assert NotificationStatus.QUEUED == "queued"
        assert NotificationStatus.PROCESSING == "processing"
        assert NotificationStatus.SENT == "sent"
        assert NotificationStatus.FAILED == "failed"
        assert NotificationStatus.RETRYING == "retrying"


# ─────────────────────────────────────────────────────────────────────────────
# QueuedNotification
# ─────────────────────────────────────────────────────────────────────────────


class TestQueuedNotification:
    def _make_notification(self, **overrides):
        defaults = {
            "id": "notif-1",
            "user_id": "user-123",
            "title": "Test",
            "title_ar": "اختبار",
            "body": "Body",
            "body_ar": "نص",
            "notification_type": "weather_alert",
            "channel": "push",
            "priority": QueuePriority.MEDIUM,
        }
        defaults.update(overrides)
        return QueuedNotification(**defaults)

    def test_create_notification(self):
        notif = self._make_notification()
        assert notif.id == "notif-1"
        assert notif.status == NotificationStatus.QUEUED
        assert notif.retry_count == 0
        assert notif.max_retries == 3
        assert notif.tenant_id is None

    def test_to_dict(self):
        notif = self._make_notification(
            tenant_id="tenant-1",
            data={"key": "value"},
        )
        data = notif.to_dict()
        assert data["id"] == "notif-1"
        assert data["priority"] == "medium"
        assert data["status"] == "queued"
        assert data["tenant_id"] == "tenant-1"
        assert data["data"]["key"] == "value"
        assert data["scheduled_at"] is None

    def test_to_dict_with_scheduled(self):
        scheduled = datetime(2026, 3, 22, 10, 0, tzinfo=UTC)
        notif = self._make_notification(scheduled_at=scheduled)
        data = notif.to_dict()
        assert data["scheduled_at"] is not None

    def test_from_dict(self):
        now = datetime.now(UTC)
        data = {
            "id": "notif-2",
            "user_id": "user-456",
            "title": "Alert",
            "title_ar": "تنبيه",
            "body": "Alert body",
            "body_ar": "نص التنبيه",
            "notification_type": "pest_outbreak",
            "channel": "sms",
            "priority": "high",
            "data": {"pest": "aphids"},
            "status": "queued",
            "retry_count": 1,
            "max_retries": 5,
            "created_at": now.isoformat(),
            "scheduled_at": None,
            "tenant_id": "t-1",
        }
        notif = QueuedNotification.from_dict(data)
        assert notif.id == "notif-2"
        assert notif.priority == QueuePriority.HIGH
        assert notif.status == NotificationStatus.QUEUED
        assert notif.retry_count == 1
        assert notif.max_retries == 5
        assert notif.tenant_id == "t-1"
        assert notif.data["pest"] == "aphids"

    def test_from_dict_with_scheduled(self):
        now = datetime.now(UTC)
        data = {
            "id": "notif-3",
            "user_id": "user-789",
            "title": "Sched",
            "title_ar": "مجدول",
            "body": "B",
            "body_ar": "ن",
            "notification_type": "system",
            "channel": "email",
            "priority": "low",
            "created_at": now.isoformat(),
            "scheduled_at": now.isoformat(),
        }
        notif = QueuedNotification.from_dict(data)
        assert notif.scheduled_at is not None

    def test_from_dict_defaults(self):
        now = datetime.now(UTC)
        data = {
            "id": "notif-4",
            "user_id": "user-abc",
            "title": "T",
            "title_ar": "ع",
            "body": "B",
            "body_ar": "ن",
            "notification_type": "system",
            "channel": "in_app",
            "priority": "medium",
            "created_at": now.isoformat(),
        }
        notif = QueuedNotification.from_dict(data)
        assert notif.retry_count == 0
        assert notif.max_retries == 3
        assert notif.status == NotificationStatus.QUEUED
        assert notif.data == {}

    def test_roundtrip(self):
        notif = self._make_notification(
            data={"field_id": "f-1"},
            tenant_id="tenant-x",
        )
        data = notif.to_dict()
        restored = QueuedNotification.from_dict(data)
        assert restored.id == notif.id
        assert restored.user_id == notif.user_id
        assert restored.priority == notif.priority
        assert restored.data == notif.data
        assert restored.tenant_id == notif.tenant_id

    def test_all_priorities(self):
        for priority in QueuePriority:
            notif = self._make_notification(priority=priority)
            assert notif.priority == priority
            data = notif.to_dict()
            assert data["priority"] == priority.value

    def test_all_statuses(self):
        for status in NotificationStatus:
            notif = self._make_notification()
            notif.status = status
            data = notif.to_dict()
            assert data["status"] == status.value


# ─────────────────────────────────────────────────────────────────────────────
# NotificationQueueProcessor
# ─────────────────────────────────────────────────────────────────────────────


class TestNotificationQueueProcessor:
    def test_init(self):
        processor = NotificationQueueProcessor()
        assert processor.batch_size == 100
        assert processor.processing_timeout == 60
        assert processor.rate_limit_per_second == 50
        assert processor._running is False
        assert processor._redis is None
        assert processor._handlers == {}

    def test_init_custom_params(self):
        processor = NotificationQueueProcessor(
            redis_url="redis://custom:6379",
            batch_size=50,
            processing_timeout=30,
            rate_limit_per_second=100,
        )
        assert processor.redis_url == "redis://custom:6379"
        assert processor.batch_size == 50
        assert processor.processing_timeout == 30
        assert processor.rate_limit_per_second == 100

    def test_queue_names(self):
        assert "critical" in NotificationQueueProcessor.PRIORITY_QUEUES[QueuePriority.CRITICAL]
        assert "high" in NotificationQueueProcessor.PRIORITY_QUEUES[QueuePriority.HIGH]
        assert "medium" in NotificationQueueProcessor.PRIORITY_QUEUES[QueuePriority.MEDIUM]
        assert "low" in NotificationQueueProcessor.PRIORITY_QUEUES[QueuePriority.LOW]

    def test_processing_set_key(self):
        assert "processing" in NotificationQueueProcessor.PROCESSING_SET

    def test_dead_letter_queue_key(self):
        assert "dead_letter" in NotificationQueueProcessor.DEAD_LETTER_QUEUE

    @pytest.mark.asyncio
    async def test_connect_without_redis(self):
        import src.queue_processor as mod
        old = mod._REDIS_AVAILABLE
        mod._REDIS_AVAILABLE = False

        processor = NotificationQueueProcessor()
        result = await processor.connect()
        assert result is False

        mod._REDIS_AVAILABLE = old


# ─────────────────────────────────────────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────────────────────────────────────────


class TestQueueProcessorMethods:
    def test_register_handler(self):
        processor = NotificationQueueProcessor()
        async def handler(notif):
            pass
        processor.register_handler("push", handler)
        assert "push" in processor._handlers

    def test_register_multiple_handlers(self):
        processor = NotificationQueueProcessor()
        async def push_handler(n): pass
        async def sms_handler(n): pass
        processor.register_handler("push", push_handler)
        processor.register_handler("sms", sms_handler)
        assert len(processor._handlers) == 2

    @pytest.mark.asyncio
    async def test_disconnect_without_connection(self):
        processor = NotificationQueueProcessor()
        await processor.disconnect()
        assert processor._redis is None

    @pytest.mark.asyncio
    async def test_enqueue_without_redis_raises(self):
        processor = NotificationQueueProcessor()
        with pytest.raises(RuntimeError, match="Not connected"):
            await processor.enqueue(
                user_id="u-1",
                title="T",
                title_ar="ع",
                body="B",
                body_ar="ن",
                notification_type="system",
                channel="push",
            )


class TestGetQueueProcessor:
    def test_returns_singleton(self):
        import src.queue_processor as mod
        old = mod._queue_processor
        mod._queue_processor = None

        proc1 = get_queue_processor()
        proc2 = get_queue_processor()
        assert proc1 is proc2

        mod._queue_processor = old
