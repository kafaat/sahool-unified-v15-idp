"""
Tests for src/notification_scheduler.py - Notification Scheduler

Covers:
- ScheduleFrequency enum
- ScheduledNotification dataclass (validation, should_retry, get_next_scheduled_time)
- NotificationScheduler (schedule, batch, cancel, quiet hours, rate limiting)
"""

import pytest
from datetime import UTC, datetime, time, timedelta
from unittest.mock import MagicMock

from src.notification_types import NotificationPayload, NotificationPriority, NotificationType
from src.notification_scheduler import (
    NotificationScheduler,
    ScheduledNotification,
    ScheduleFrequency,
)


# ─────────────────────────────────────────────────────────────────────────────
# ScheduleFrequency
# ─────────────────────────────────────────────────────────────────────────────


class TestScheduleFrequency:
    def test_values(self):
        assert ScheduleFrequency.ONCE == "once"
        assert ScheduleFrequency.DAILY == "daily"
        assert ScheduleFrequency.WEEKLY == "weekly"
        assert ScheduleFrequency.MONTHLY == "monthly"


# ─────────────────────────────────────────────────────────────────────────────
# ScheduledNotification
# ─────────────────────────────────────────────────────────────────────────────


def _make_payload(**kwargs):
    defaults = {
        "notification_type": NotificationType.IRRIGATION_REMINDER,
        "priority": NotificationPriority.MEDIUM,
        "title": "Test",
        "title_ar": "اختبار",
        "body": "Test body",
        "body_ar": "نص اختبار",
    }
    defaults.update(kwargs)
    return NotificationPayload(**defaults)


class TestScheduledNotification:
    def test_create_valid(self):
        payload = _make_payload()
        notif = ScheduledNotification(
            scheduled_time=datetime.now(UTC),
            notification_id="n-1",
            payload=payload,
            recipient_token="token-abc",
        )
        assert notif.status == "pending"
        assert notif.retry_count == 0
        assert notif.max_retries == 3

    def test_validation_requires_notification_id(self):
        with pytest.raises(ValueError, match="notification_id"):
            ScheduledNotification(
                scheduled_time=datetime.now(UTC),
                notification_id="",
                payload=_make_payload(),
                recipient_token="token",
            )

    def test_validation_requires_payload(self):
        with pytest.raises(ValueError, match="payload"):
            ScheduledNotification(
                scheduled_time=datetime.now(UTC),
                notification_id="n-1",
                payload=None,
                recipient_token="token",
            )

    def test_validation_requires_recipient_token(self):
        with pytest.raises(ValueError, match="recipient_token"):
            ScheduledNotification(
                scheduled_time=datetime.now(UTC),
                notification_id="n-1",
                payload=_make_payload(),
                recipient_token="",
            )

    def test_cancelled_skips_validation(self):
        notif = ScheduledNotification(
            scheduled_time=datetime.now(UTC),
            status="cancelled",
        )
        assert notif.status == "cancelled"

    def test_sent_skips_validation(self):
        notif = ScheduledNotification(
            scheduled_time=datetime.now(UTC),
            status="sent",
        )
        assert notif.status == "sent"

    def test_should_retry_when_failed(self):
        notif = ScheduledNotification(
            scheduled_time=datetime.now(UTC),
            notification_id="n-1",
            payload=_make_payload(),
            recipient_token="token",
            status="failed",
            retry_count=1,
            max_retries=3,
        )
        assert notif.should_retry() is True

    def test_should_not_retry_when_max_reached(self):
        notif = ScheduledNotification(
            scheduled_time=datetime.now(UTC),
            notification_id="n-1",
            payload=_make_payload(),
            recipient_token="token",
            status="failed",
            retry_count=3,
            max_retries=3,
        )
        assert notif.should_retry() is False

    def test_should_not_retry_when_pending(self):
        notif = ScheduledNotification(
            scheduled_time=datetime.now(UTC),
            notification_id="n-1",
            payload=_make_payload(),
            recipient_token="token",
            status="pending",
        )
        assert notif.should_retry() is False

    def test_get_next_scheduled_time_once(self):
        notif = ScheduledNotification(
            scheduled_time=datetime.now(UTC),
            notification_id="n-1",
            payload=_make_payload(),
            recipient_token="token",
            frequency=ScheduleFrequency.ONCE,
        )
        assert notif.get_next_scheduled_time() is None

    def test_get_next_scheduled_time_daily(self):
        now = datetime.now(UTC)
        notif = ScheduledNotification(
            scheduled_time=now,
            notification_id="n-1",
            payload=_make_payload(),
            recipient_token="token",
            frequency=ScheduleFrequency.DAILY,
        )
        next_time = notif.get_next_scheduled_time()
        assert next_time == now + timedelta(days=1)

    def test_get_next_scheduled_time_weekly(self):
        now = datetime.now(UTC)
        notif = ScheduledNotification(
            scheduled_time=now,
            notification_id="n-1",
            payload=_make_payload(),
            recipient_token="token",
            frequency=ScheduleFrequency.WEEKLY,
        )
        next_time = notif.get_next_scheduled_time()
        assert next_time == now + timedelta(weeks=1)

    def test_get_next_scheduled_time_monthly(self):
        now = datetime.now(UTC)
        notif = ScheduledNotification(
            scheduled_time=now,
            notification_id="n-1",
            payload=_make_payload(),
            recipient_token="token",
            frequency=ScheduleFrequency.MONTHLY,
        )
        next_time = notif.get_next_scheduled_time()
        assert next_time == now + timedelta(days=30)

    def test_ordering_by_scheduled_time(self):
        now = datetime.now(UTC)
        payload = _make_payload()
        notif1 = ScheduledNotification(
            scheduled_time=now + timedelta(hours=1),
            notification_id="n-1",
            payload=payload,
            recipient_token="t1",
        )
        notif2 = ScheduledNotification(
            scheduled_time=now,
            notification_id="n-2",
            payload=payload,
            recipient_token="t2",
        )
        assert notif2 < notif1


# ─────────────────────────────────────────────────────────────────────────────
# NotificationScheduler
# ─────────────────────────────────────────────────────────────────────────────


class TestNotificationScheduler:
    def setup_method(self):
        self.mock_firebase = MagicMock()
        self.mock_firebase._initialized = True
        self.scheduler = NotificationScheduler(
            firebase_client=self.mock_firebase,
            rate_limit_per_minute=5,
        )

    def test_init(self):
        assert self.scheduler.batch_size == 500
        assert self.scheduler.rate_limit_per_minute == 5
        assert self.scheduler._running is False
        assert len(self.scheduler._queue) == 0

    def test_schedule_notification(self):
        payload = _make_payload(priority=NotificationPriority.HIGH)
        result = self.scheduler.schedule_notification(
            notification_id="n-1",
            payload=payload,
            recipient_token="token-abc",
            scheduled_time=datetime.now(UTC) + timedelta(hours=1),
        )
        assert result is True
        assert len(self.scheduler._queue) == 1
        assert "n-1" in self.scheduler._notification_map

    def test_schedule_batch(self):
        payload = _make_payload()
        tokens = ["token-1", "token-2", "token-3"]
        count = self.scheduler.schedule_batch(
            payload=payload,
            recipient_tokens=tokens,
            scheduled_time=datetime.now(UTC) + timedelta(hours=1),
        )
        assert count == 3
        assert len(self.scheduler._queue) == 3

    def test_cancel_notification(self):
        payload = _make_payload()
        self.scheduler.schedule_notification(
            notification_id="n-cancel",
            payload=payload,
            recipient_token="token",
            scheduled_time=datetime.now(UTC) + timedelta(hours=1),
        )
        result = self.scheduler.cancel_notification("n-cancel")
        assert result is True
        assert self.scheduler._notification_map["n-cancel"].status == "cancelled"

    def test_cancel_nonexistent(self):
        result = self.scheduler.cancel_notification("nonexistent")
        assert result is False


# ─────────────────────────────────────────────────────────────────────────────
# Quiet Hours
# ─────────────────────────────────────────────────────────────────────────────


class TestQuietHours:
    def test_during_quiet_hours_midnight_span(self):
        scheduler = NotificationScheduler(
            firebase_client=MagicMock(),
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(6, 0),
        )
        # 23:00 should be quiet
        check_time = datetime(2026, 1, 15, 23, 0)
        assert scheduler.is_quiet_hours(check_time) is True

    def test_during_quiet_hours_early_morning(self):
        scheduler = NotificationScheduler(
            firebase_client=MagicMock(),
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(6, 0),
        )
        # 3:00 AM should be quiet
        check_time = datetime(2026, 1, 15, 3, 0)
        assert scheduler.is_quiet_hours(check_time) is True

    def test_outside_quiet_hours(self):
        scheduler = NotificationScheduler(
            firebase_client=MagicMock(),
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(6, 0),
        )
        # 12:00 PM should not be quiet
        check_time = datetime(2026, 1, 15, 12, 0)
        assert scheduler.is_quiet_hours(check_time) is False

    def test_same_day_quiet_hours(self):
        scheduler = NotificationScheduler(
            firebase_client=MagicMock(),
            quiet_hours_start=time(8, 0),
            quiet_hours_end=time(12, 0),
        )
        # 10:00 AM should be quiet
        check_time = datetime(2026, 1, 15, 10, 0)
        assert scheduler.is_quiet_hours(check_time) is True

    def test_default_check_time_is_now(self):
        scheduler = NotificationScheduler(
            firebase_client=MagicMock(),
            quiet_hours_start=time(22, 0),
            quiet_hours_end=time(6, 0),
        )
        # Should not raise
        result = scheduler.is_quiet_hours()
        assert isinstance(result, bool)


# ─────────────────────────────────────────────────────────────────────────────
# Rate Limiting
# ─────────────────────────────────────────────────────────────────────────────


class TestRateLimiting:
    def test_can_send_within_limit(self):
        scheduler = NotificationScheduler(
            firebase_client=MagicMock(),
            rate_limit_per_minute=5,
        )
        assert scheduler.can_send_to_user("token-1") is True

    def test_rate_limit_exceeded(self):
        scheduler = NotificationScheduler(
            firebase_client=MagicMock(),
            rate_limit_per_minute=3,
        )
        for _ in range(3):
            scheduler.record_send("token-1")
        assert scheduler.can_send_to_user("token-1") is False

    def test_rate_limit_per_user_independent(self):
        scheduler = NotificationScheduler(
            firebase_client=MagicMock(),
            rate_limit_per_minute=2,
        )
        for _ in range(2):
            scheduler.record_send("token-1")
        assert scheduler.can_send_to_user("token-1") is False
        assert scheduler.can_send_to_user("token-2") is True

    def test_old_timestamps_cleaned(self):
        scheduler = NotificationScheduler(
            firebase_client=MagicMock(),
            rate_limit_per_minute=2,
        )
        # Add old timestamps
        old_time = datetime.now(UTC) - timedelta(minutes=2)
        scheduler._send_timestamps["token-1"] = [old_time, old_time]
        # Should clean old timestamps and allow sending
        assert scheduler.can_send_to_user("token-1") is True

    def test_record_send(self):
        scheduler = NotificationScheduler(
            firebase_client=MagicMock(),
        )
        scheduler.record_send("token-1")
        assert len(scheduler._send_timestamps["token-1"]) == 1


# ─────────────────────────────────────────────────────────────────────────────
# Priority Ordering
# ─────────────────────────────────────────────────────────────────────────────


class TestPriorityOrdering:
    def test_critical_scheduled_before_low(self):
        scheduler = NotificationScheduler(firebase_client=MagicMock())
        now = datetime.now(UTC) + timedelta(hours=1)

        scheduler.schedule_notification(
            notification_id="low-priority",
            payload=_make_payload(priority=NotificationPriority.LOW),
            recipient_token="token-1",
            scheduled_time=now,
        )
        scheduler.schedule_notification(
            notification_id="critical-priority",
            payload=_make_payload(priority=NotificationPriority.CRITICAL),
            recipient_token="token-2",
            scheduled_time=now,
        )

        # Heap should have critical first (lower number = higher priority)
        import heapq
        top = heapq.heappop(scheduler._queue)
        assert top.priority == 0  # CRITICAL = 0

    def test_schedule_with_frequency(self):
        scheduler = NotificationScheduler(firebase_client=MagicMock())
        result = scheduler.schedule_notification(
            notification_id="daily-reminder",
            payload=_make_payload(),
            recipient_token="token",
            scheduled_time=datetime.now(UTC) + timedelta(hours=1),
            frequency=ScheduleFrequency.DAILY,
        )
        assert result is True
        assert scheduler._notification_map["daily-reminder"].frequency == ScheduleFrequency.DAILY
