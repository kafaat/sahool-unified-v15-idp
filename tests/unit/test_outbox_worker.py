"""
Tests for SAHOOL Outbox Worker and NATS Client
===============================================
اختبارات عامل الـ Outbox وعميل NATS

Tests:
- NATSOutboxAsyncClient publish with JetStream ack
- OutboxWorker lifecycle (start, poll, stop)
- OutboxWorker batch publishing
- OutboxWorker error handling and retry tracking
- OutboxWorker graceful shutdown
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from shared.libs.outbox.models import OutboxEvent
from shared.libs.outbox.nats_client import NATSOutboxAsyncClient
from shared.libs.outbox.worker import OutboxWorker, OutboxWorkerConfig


# ---------------------------------------------------------------------------
# NATSOutboxAsyncClient tests
# ---------------------------------------------------------------------------


class TestNATSOutboxAsyncClient:
    """Tests for the async NATS JetStream outbox client."""

    @pytest.mark.asyncio
    async def test_publish_calls_jetstream_with_correct_subject(self):
        """Publish should call JetStream with sahool.outbox.{topic} subject."""
        mock_js = AsyncMock()
        mock_ack = MagicMock()
        mock_ack.stream = "SAHOOL_EVENTS"
        mock_ack.seq = 42
        mock_js.publish = AsyncMock(return_value=mock_ack)

        client = NATSOutboxAsyncClient.__new__(NATSOutboxAsyncClient)
        client._js = mock_js

        await client.publish("field.created", '{"field_id": "123"}')

        mock_js.publish.assert_called_once_with(
            "sahool.outbox.field.created",
            b'{"field_id": "123"}',
        )

    @pytest.mark.asyncio
    async def test_publish_propagates_nats_errors(self):
        """If JetStream publish fails, error should propagate (not swallowed)."""
        mock_js = AsyncMock()
        mock_js.publish = AsyncMock(side_effect=ConnectionError("NATS down"))

        client = NATSOutboxAsyncClient.__new__(NATSOutboxAsyncClient)
        client._js = mock_js

        with pytest.raises(ConnectionError, match="NATS down"):
            await client.publish("field.created", "{}")


# ---------------------------------------------------------------------------
# OutboxWorker tests
# ---------------------------------------------------------------------------


def _make_outbox_event(
    event_type: str = "field.created",
    published: bool = False,
    retry_count: int = 0,
) -> OutboxEvent:
    """Create a mock OutboxEvent for testing."""
    event = MagicMock(spec=OutboxEvent)
    event.id = uuid4()
    event.event_type = event_type
    event.payload_json = f'{{"type": "{event_type}"}}'
    event.published = published
    event.published_at = None
    event.retry_count = retry_count
    event.last_error = None
    event.created_at = datetime.now(UTC)
    return event


class TestOutboxWorker:
    """Tests for the outbox background worker."""

    def _make_worker(
        self, events: list | None = None, nats_error: Exception | None = None
    ) -> tuple[OutboxWorker, AsyncMock, MagicMock]:
        """Create a worker with mocked dependencies."""
        # Mock DB session
        mock_db = MagicMock()
        mock_result = MagicMock()
        mock_scalars = MagicMock()
        mock_scalars.return_value = events or []
        mock_result.scalars = mock_scalars
        mock_db.execute = MagicMock(return_value=mock_result)

        def db_factory():
            return mock_db

        # Mock NATS client
        mock_nats = AsyncMock()
        if nats_error:
            mock_nats.publish = AsyncMock(side_effect=nats_error)
        else:
            mock_nats.publish = AsyncMock()

        config = OutboxWorkerConfig(
            poll_interval_seconds=0.1,
            batch_size=50,
            max_retries=3,
            service_name="test-service",
        )

        worker = OutboxWorker(
            db_factory=db_factory,
            nats_client=mock_nats,
            config=config,
        )

        return worker, mock_nats, mock_db

    @pytest.mark.asyncio
    async def test_worker_starts_and_stops(self):
        """Worker should start a background task and stop gracefully."""
        worker, _, _ = self._make_worker()

        task = await worker.start()
        assert worker.is_running
        assert task is not None

        await asyncio.sleep(0.05)
        await worker.stop()

        assert not worker.is_running

    @pytest.mark.asyncio
    async def test_worker_publishes_pending_events(self):
        """Worker should publish events and mark them as published."""
        events = [_make_outbox_event("field.created"), _make_outbox_event("billing.charged")]
        worker, mock_nats, mock_db = self._make_worker(events=events)

        count = await worker._publish_batch()

        assert count == 2
        assert mock_nats.publish.call_count == 2
        assert events[0].published is True
        assert events[1].published is True
        assert events[0].published_at is not None
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_worker_handles_nats_failure_per_event(self):
        """If NATS fails for one event, it should increment retry_count."""
        events = [_make_outbox_event("field.created")]
        worker, _, mock_db = self._make_worker(
            events=events,
            nats_error=ConnectionError("NATS unavailable"),
        )

        count = await worker._publish_batch()

        assert count == 0
        assert events[0].retry_count == 1
        assert "NATS unavailable" in events[0].last_error
        assert events[0].published is False
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_worker_returns_zero_for_empty_outbox(self):
        """When no pending events, publish_batch returns 0."""
        worker, mock_nats, _ = self._make_worker(events=[])

        count = await worker._publish_batch()

        assert count == 0
        mock_nats.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_worker_stats_tracking(self):
        """Worker should track publish stats."""
        events = [_make_outbox_event()]
        worker, _, _ = self._make_worker(events=events)

        await worker._publish_batch()

        # Stats are updated in the poll loop, not _publish_batch directly
        assert worker.stats["total_published"] == 0  # Not updated in _publish_batch
        assert worker.stats["started_at"] is None  # Not started yet

    @pytest.mark.asyncio
    async def test_worker_db_rollback_on_error(self):
        """Worker should rollback DB on unexpected errors."""
        mock_db = MagicMock()
        mock_db.execute = MagicMock(side_effect=RuntimeError("DB connection lost"))

        worker = OutboxWorker(
            db_factory=lambda: mock_db,
            nats_client=AsyncMock(),
            config=OutboxWorkerConfig(service_name="test"),
        )

        with pytest.raises(RuntimeError, match="DB connection lost"):
            await worker._publish_batch()

        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()


# ---------------------------------------------------------------------------
# Startup validation tests
# ---------------------------------------------------------------------------


class TestStartupChecks:
    """Tests for environment validation at startup."""

    def test_validate_startup_passes_with_all_vars(self, monkeypatch):
        """Should pass when all required vars are set."""
        from shared.startup_checks import ServiceProfile, validate_startup

        monkeypatch.setenv("ENVIRONMENT", "test")
        monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/test")
        monkeypatch.setenv("NATS_URL", "nats://localhost:4222")

        result = validate_startup(
            service_name="test-service",
            profile=ServiceProfile.DATABASE | ServiceProfile.NATS,
        )

        assert result["DATABASE_URL"] == "postgresql://localhost/test"
        assert result["NATS_URL"] == "nats://localhost:4222"

    def test_validate_startup_fails_on_missing_var(self, monkeypatch):
        """Should fail fast when a required var is missing."""
        from shared.startup_checks import ServiceProfile, validate_startup

        monkeypatch.setenv("ENVIRONMENT", "test")
        # DATABASE_URL deliberately not set
        monkeypatch.delenv("DATABASE_URL", raising=False)

        with pytest.raises(SystemExit):
            validate_startup(
                service_name="test-service",
                profile=ServiceProfile.DATABASE,
            )

    def test_validate_startup_fails_on_invalid_environment(self, monkeypatch):
        """Should reject invalid ENVIRONMENT values."""
        from shared.startup_checks import ServiceProfile, validate_startup

        monkeypatch.setenv("ENVIRONMENT", "banana")

        with pytest.raises(SystemExit):
            validate_startup(
                service_name="test-service",
                profile=ServiceProfile.MINIMAL,
            )

    def test_validate_startup_fails_on_short_jwt_key(self, monkeypatch):
        """Should reject JWT keys shorter than 32 chars."""
        from shared.startup_checks import ServiceProfile, validate_startup

        monkeypatch.setenv("ENVIRONMENT", "test")
        monkeypatch.setenv("JWT_SECRET_KEY", "tooshort")

        with pytest.raises(SystemExit):
            validate_startup(
                service_name="test-service",
                profile=ServiceProfile.JWT_AUTH,
            )

    def test_require_env_returns_value(self, monkeypatch):
        """require_env should return the value when set."""
        from shared.startup_checks import require_env

        monkeypatch.setenv("MY_VAR", "hello")
        assert require_env("MY_VAR") == "hello"

    def test_require_env_raises_on_missing(self, monkeypatch):
        """require_env should raise when var is missing."""
        from shared.startup_checks import require_env

        monkeypatch.delenv("MISSING_VAR", raising=False)

        with pytest.raises(SystemExit):
            require_env("MISSING_VAR")
