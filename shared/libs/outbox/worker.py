"""
SAHOOL Outbox Background Worker
================================
عامل خلفية لنشر أحداث الـ Outbox بشكل دوري

Background worker that polls the outbox table and publishes
pending events to NATS JetStream. Designed to integrate with
FastAPI's lifespan context manager.

Architecture:
    Outbox Table → Worker (poll every N seconds) → NATS JetStream
                                                    ↓
                                                  ACK received
                                                    ↓
                                              Mark as published

Usage:
    from shared.libs.outbox.worker import OutboxWorker

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        worker = OutboxWorker(db_factory=get_session, nats_client=async_client)
        await worker.start()
        try:
            yield
        finally:
            await worker.stop()
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import OutboxEvent

logger = logging.getLogger(__name__)


@dataclass
class OutboxWorkerConfig:
    """Configuration for the outbox background worker."""

    poll_interval_seconds: float = 5.0
    batch_size: int = 100
    max_retries: int = 3
    service_name: str = "unknown"


class OutboxWorker:
    """
    Background worker that polls the outbox table and publishes
    events via an async NATS client.

    This worker uses the existing publish_pending() logic but
    wraps it in a managed background task with proper lifecycle.

    Args:
        db_factory: Callable that returns a SQLAlchemy Session
        nats_client: NATSOutboxAsyncClient instance
        config: Worker configuration
    """

    def __init__(
        self,
        db_factory: Callable[[], Session],
        nats_client: Any,
        config: OutboxWorkerConfig | None = None,
    ):
        self._db_factory = db_factory
        self._nats_client = nats_client
        self._config = config or OutboxWorkerConfig()
        self._task: asyncio.Task | None = None
        self._running = False
        self._stats = {
            "total_published": 0,
            "total_errors": 0,
            "last_poll": None,
            "started_at": None,
        }

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    async def start(self) -> asyncio.Task:
        """Start the background worker. Returns the task for tracking."""
        if self._running:
            logger.warning("outbox_worker_already_running")
            return self._task

        self._running = True
        self._stats["started_at"] = datetime.now(UTC).isoformat()
        self._task = asyncio.create_task(
            self._poll_loop(),
            name=f"outbox-worker-{self._config.service_name}",
        )
        # Ensure task exceptions are logged, not silently swallowed
        self._task.add_done_callback(self._task_done_callback)

        logger.info(
            "outbox_worker_started",
            extra={
                "service": self._config.service_name,
                "poll_interval": self._config.poll_interval_seconds,
                "batch_size": self._config.batch_size,
            },
        )
        return self._task

    async def stop(self) -> None:
        """Gracefully stop the worker."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(
            "outbox_worker_stopped",
            extra={"stats": self._stats},
        )

    def _task_done_callback(self, task: asyncio.Task) -> None:
        """Log if the worker task dies unexpectedly."""
        if task.cancelled():
            return
        exc = task.exception()
        if exc:
            logger.error(
                "outbox_worker_crashed",
                extra={"error": str(exc), "error_type": type(exc).__name__},
                exc_info=exc,
            )

    async def _poll_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                published = await self._publish_batch()
                self._stats["total_published"] += published
                self._stats["last_poll"] = datetime.now(UTC).isoformat()

                if published > 0:
                    logger.info(
                        "outbox_batch_published",
                        extra={
                            "count": published,
                            "total": self._stats["total_published"],
                        },
                    )
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self._stats["total_errors"] += 1
                logger.error(
                    "outbox_poll_error",
                    extra={"error": str(e), "error_type": type(e).__name__},
                    exc_info=True,
                )

            await asyncio.sleep(self._config.poll_interval_seconds)

    async def _publish_batch(self) -> int:
        """
        Fetch unpublished events from outbox and publish via NATS.

        Uses the same query pattern as publish_pending() but with
        async NATS publishing and proper ack handling.

        Returns:
            Number of events successfully published
        """
        db = self._db_factory()
        try:
            stmt = (
                select(OutboxEvent)
                .where(OutboxEvent.published.is_(False))
                .where(OutboxEvent.retry_count < self._config.max_retries)
                .order_by(OutboxEvent.created_at.asc())
                .limit(self._config.batch_size)
            )
            events = list(db.execute(stmt).scalars())

            if not events:
                return 0

            published_count = 0
            for event in events:
                try:
                    await self._nats_client.publish(event.event_type, event.payload_json)
                    event.published = True
                    event.published_at = datetime.now(UTC)
                    event.last_error = None
                    published_count += 1

                except Exception as e:
                    event.retry_count += 1
                    event.last_error = str(e)[:500]
                    logger.warning(
                        "outbox_event_publish_failed",
                        extra={
                            "event_id": str(event.id),
                            "event_type": event.event_type,
                            "retry_count": event.retry_count,
                            "error": str(e),
                        },
                    )

            db.commit()
            return published_count

        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
