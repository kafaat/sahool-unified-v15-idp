"""
Tests for response models in analytics_controller.py and history_controller.py

Covers Pydantic model creation and validation for:
- DeliveryStatsResponse
- ChannelPerformanceResponse
- DashboardSummaryResponse
- NotificationHistoryResponse
- DeliveryLogResponse
"""

from datetime import UTC, datetime

import pytest

try:
    from src.analytics_controller import (
        ChannelPerformanceResponse,
        DashboardSummaryResponse,
        DeliveryStatsResponse,
    )
    from src.history_controller import (
        DeliveryLogResponse,
        HistoryStatsResponse,
        NotificationHistoryResponse,
        PaginatedHistoryResponse,
    )
except BaseException as e:
    if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
        raise
    pytest.skip("notification-service dependencies not available", allow_module_level=True)


class TestDeliveryStatsResponse:
    def test_create(self):
        resp = DeliveryStatsResponse(
            time_range="day",
            start_time="2026-03-21T00:00:00Z",
            end_time="2026-03-22T00:00:00Z",
            total_notifications=1000,
            sent=900,
            failed=50,
            pending=50,
            read=600,
            delivery_rate=90.0,
            failure_rate=5.0,
            read_rate=60.0,
        )
        assert resp.total_notifications == 1000
        assert resp.delivery_rate == 90.0


class TestChannelPerformanceResponse:
    def test_create(self):
        resp = ChannelPerformanceResponse(
            time_range="week",
            channels={
                "push": {"sent": 500, "failed": 10, "success_rate": 98.0},
                "sms": {"sent": 200, "failed": 5, "success_rate": 97.5},
            },
            best_performing_channel="push",
            best_success_rate=98.0,
        )
        assert resp.best_performing_channel == "push"
        assert len(resp.channels) == 2

    def test_no_best_channel(self):
        resp = ChannelPerformanceResponse(
            time_range="day",
            channels={},
            best_performing_channel=None,
            best_success_rate=0.0,
        )
        assert resp.best_performing_channel is None


class TestDashboardSummaryResponse:
    def test_create(self):
        resp = DashboardSummaryResponse(
            generated_at="2026-03-22T12:00:00Z",
            summary={"total": 5000, "active_users": 200},
            delivery={"rate": 95.0, "avg_latency_ms": 120},
            channels={"push": 60, "sms": 30, "email": 10},
            types={"weather_alert": 100, "pest_outbreak": 50},
            engagement={"active_users": 200, "read_rate": 65.0},
        )
        assert resp.summary["total"] == 5000
        assert resp.channels["push"] == 60
        assert resp.engagement["read_rate"] == 65.0


class TestNotificationHistoryResponse:
    def test_create(self):
        resp = NotificationHistoryResponse(
            id="n-1",
            user_id="user-123",
            title="Alert",
            title_ar="تنبيه",
            body="Body text",
            body_ar="نص",
            type="weather_alert",
            priority="high",
            channel="push",
            status="sent",
            is_read=False,
            created_at=datetime.now(UTC),
            sent_at=datetime.now(UTC),
            read_at=None,
            expires_at=None,
            data={"key": "value"},
        )
        assert resp.id == "n-1"
        assert resp.is_read is False

    def test_optional_fields(self):
        resp = NotificationHistoryResponse(
            id="n-2",
            user_id="user-456",
            title="Title",
            title_ar=None,
            body="Body",
            body_ar=None,
            type="system",
            priority="low",
            channel="in_app",
            status="pending",
            is_read=False,
            created_at=datetime.now(UTC),
            sent_at=None,
            read_at=None,
            expires_at=None,
            data=None,
        )
        assert resp.title_ar is None
        assert resp.data is None


class TestHistoryStatsResponse:
    def test_create(self):
        resp = HistoryStatsResponse(
            total_notifications=1000,
            sent=800,
            failed=50,
            pending=150,
            read=600,
            delivery_rate=80.0,
            read_rate=75.0,
        )
        assert resp.total_notifications == 1000
        assert resp.delivery_rate == 80.0


class TestPaginatedHistoryResponse:
    def test_create(self):
        resp = PaginatedHistoryResponse(
            total=100,
            page=1,
            page_size=20,
            total_pages=5,
            notifications=[
                NotificationHistoryResponse(
                    id="n-1",
                    user_id="u-1",
                    title="T",
                    title_ar="ع",
                    body="B",
                    body_ar="ن",
                    type="system",
                    priority="low",
                    channel="in_app",
                    status="sent",
                    is_read=True,
                    created_at=datetime.now(UTC),
                    sent_at=None,
                    read_at=None,
                    expires_at=None,
                    data=None,
                )
            ],
        )
        assert resp.total == 100
        assert resp.total_pages == 5
        assert len(resp.notifications) == 1

    def test_empty_page(self):
        resp = PaginatedHistoryResponse(
            total=0,
            page=1,
            page_size=20,
            total_pages=0,
            notifications=[],
        )
        assert resp.total == 0
        assert len(resp.notifications) == 0


class TestDeliveryLogResponse:
    def test_create(self):
        resp = DeliveryLogResponse(
            id="log-1",
            notification_id="n-1",
            channel="sms",
            status="sent",
            provider_message_id="SM123",
            error_message=None,
            retry_count=0,
            attempted_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
        )
        assert resp.id == "log-1"
        assert resp.status == "sent"
        assert resp.error_message is None

    def test_failed_log(self):
        resp = DeliveryLogResponse(
            id="log-2",
            notification_id="n-2",
            channel="email",
            status="failed",
            provider_message_id=None,
            error_message="SMTP timeout",
            retry_count=2,
            attempted_at=datetime.now(UTC),
            completed_at=None,
        )
        assert resp.status == "failed"
        assert resp.error_message == "SMTP timeout"
        assert resp.retry_count == 2
