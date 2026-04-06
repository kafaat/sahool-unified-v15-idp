"""
SAHOOL DLQ Auto-Replay Worker
===============================
عامل إعادة تشغيل تلقائي لقائمة انتظار الرسائل الفاشلة

Background worker that automatically retries failed DLQ messages
using intelligent backoff and error classification.

Unlike the manual replay API (dlq_service.py), this worker runs
continuously and replays retriable messages automatically with
exponential backoff, while leaving non-retriable messages for
manual inspection.

Architecture:
    DLQ Stream → Auto-Replay Worker (poll every N seconds)
                    ↓
        Retriable error? ──Yes──→ Republish to original subject
                    │                    ↓
                    No              Update replay metadata
                    ↓
                Skip (manual review needed)

Usage:
    from shared.events.dlq_auto_replay import DLQAutoReplayWorker

    # In service lifespan
    worker = DLQAutoReplayWorker(js=jetstream_context)
    await worker.start()
    yield
    await worker.stop()
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from .dlq_config import DLQConfig, DLQMessageMetadata

logger = logging.getLogger(__name__)

# Lazy import
_nats_available = False
try:
    from nats.js import JetStreamContext

    _nats_available = True
except ImportError:
    JetStreamContext = None


@dataclass
class AutoReplayConfig:
    """Configuration for automatic DLQ replay."""

    poll_interval_seconds: float = 30.0
    batch_size: int = 20
    max_replay_attempts: int = 5
    min_age_seconds: float = 60.0
    max_age_hours: float = 24.0
    service_name: str = "dlq-auto-replay"


@dataclass
class AutoReplayStats:
    """Runtime statistics for the auto-replay worker."""

    started_at: str | None = None
    total_replayed: int = 0
    total_skipped: int = 0
    total_errors: int = 0
    total_expired: int = 0
    last_poll: str | None = None
    last_replay_subject: str | None = None


class DLQAutoReplayWorker:
    """
    Automatic DLQ replay worker.

    Polls the DLQ stream for retriable messages and republishes
    them to their original subjects with proper backoff.

    Only replays messages that:
    1. Had retriable errors (ConnectionError, TimeoutError, etc.)
    2. Haven't exceeded max_replay_attempts
    3. Are older than min_age_seconds (gives services time to recover)
    4. Are younger than max_age_hours (don't replay ancient failures)

    Non-retriable errors (ValidationError, ValueError, etc.) are
    skipped for manual inspection via the DLQ management API.

    Args:
        js: NATS JetStream context
        dlq_config: DLQ configuration
        replay_config: Auto-replay configuration
    """

    def __init__(
        self,
        js: JetStreamContext,
        dlq_config: DLQConfig | None = None,
        replay_config: AutoReplayConfig | None = None,
    ):
        self._js = js
        self._dlq_config = dlq_config or DLQConfig()
        self._config = replay_config or AutoReplayConfig()
        self._task: asyncio.Task | None = None
        self._running = False
        self._stats = AutoReplayStats()

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def stats(self) -> AutoReplayStats:
        return self._stats

    async def start(self) -> asyncio.Task:
        """Start the auto-replay worker."""
        if self._running:
            logger.warning("dlq_auto_replay_already_running")
            return self._task

        self._running = True
        self._stats.started_at = datetime.now(UTC).isoformat()
        self._task = asyncio.create_task(
            self._poll_loop(),
            name=f"dlq-auto-replay-{self._config.service_name}",
        )
        self._task.add_done_callback(self._on_task_done)

        logger.info(
            "dlq_auto_replay_started",
            extra={
                "poll_interval": self._config.poll_interval_seconds,
                "batch_size": self._config.batch_size,
                "max_replay_attempts": self._config.max_replay_attempts,
            },
        )
        return self._task

    async def stop(self) -> None:
        """Stop the worker gracefully."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info(
            "dlq_auto_replay_stopped",
            extra={
                "total_replayed": self._stats.total_replayed,
                "total_skipped": self._stats.total_skipped,
                "total_errors": self._stats.total_errors,
            },
        )

    def _on_task_done(self, task: asyncio.Task) -> None:
        """Log unexpected task death."""
        if task.cancelled():
            return
        exc = task.exception()
        if exc:
            logger.error(
                "dlq_auto_replay_crashed",
                extra={"error": str(exc), "error_type": type(exc).__name__},
                exc_info=exc,
            )

    async def _poll_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                await self._process_batch()
                self._stats.last_poll = datetime.now(UTC).isoformat()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                self._stats.total_errors += 1
                logger.error(
                    "dlq_auto_replay_poll_error",
                    extra={"error": str(e)},
                    exc_info=True,
                )
            await asyncio.sleep(self._config.poll_interval_seconds)

    async def _process_batch(self) -> None:
        """Fetch and process a batch of DLQ messages."""
        try:
            sub = await self._js.pull_subscribe(
                f"{self._dlq_config.dlq_subject_prefix}.>",
                durable=f"dlq_auto_replay_{self._config.service_name}",
            )
        except Exception as e:
            logger.warning("dlq_subscribe_failed", extra={"error": str(e)})
            return

        try:
            messages = await sub.fetch(batch=self._config.batch_size, timeout=5)
        except Exception:
            # No messages or timeout — normal
            return

        for msg in messages:
            try:
                await self._process_message(msg)
            except Exception as e:
                self._stats.total_errors += 1
                logger.error(
                    "dlq_auto_replay_message_error",
                    extra={"error": str(e), "subject": msg.subject},
                )
                # NAK to retry later
                await msg.nak()

    async def _process_message(self, msg) -> None:
        """
        Process a single DLQ message.

        Decision tree:
        1. Parse metadata
        2. Check if retriable error → skip if not
        3. Check replay count → skip if exceeded
        4. Check age → skip if too young or too old
        5. Calculate backoff delay → skip if not yet due
        6. Republish to original subject
        7. ACK from DLQ
        """
        try:
            data = json.loads(msg.data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning("dlq_message_unparseable", extra={"error": str(e)})
            self._stats.total_skipped += 1
            await msg.ack()  # Remove corrupt message
            return

        raw_metadata = data.get("metadata", {})
        try:
            metadata = DLQMessageMetadata(**raw_metadata)
        except Exception:
            logger.warning("dlq_metadata_invalid", extra={"raw": str(raw_metadata)[:200]})
            self._stats.total_skipped += 1
            await msg.ack()
            return

        # 1. Check if error is retriable
        error_type = metadata.error_type or ""
        non_retriable_types = {"ValidationError", "ValueError", "KeyError", "TypeError"}
        if error_type in non_retriable_types:
            self._stats.total_skipped += 1
            # Don't ACK — leave for manual review via DLQ API
            await msg.nak()
            return

        # 2. Check replay count
        if metadata.replay_count >= self._config.max_replay_attempts:
            self._stats.total_skipped += 1
            logger.info(
                "dlq_replay_exhausted",
                extra={
                    "subject": metadata.original_subject,
                    "replay_count": metadata.replay_count,
                },
            )
            await msg.nak()
            return

        # 3. Check age
        try:
            failure_time = datetime.fromisoformat(metadata.failure_timestamp)
        except (ValueError, TypeError):
            failure_time = datetime.now(UTC)

        age = (
            datetime.now(UTC) - failure_time.replace(tzinfo=UTC)
            if failure_time.tzinfo is None
            else datetime.now(UTC) - failure_time
        )

        if age.total_seconds() < self._config.min_age_seconds:
            # Too young — wait for service recovery
            await msg.nak()
            return

        if age.total_seconds() > self._config.max_age_hours * 3600:
            self._stats.total_expired += 1
            logger.info(
                "dlq_message_expired",
                extra={
                    "subject": metadata.original_subject,
                    "age_hours": age.total_seconds() / 3600,
                },
            )
            await msg.nak()
            return

        # 4. Calculate backoff — don't replay too frequently
        expected_delay = self._dlq_config.get_retry_delay(metadata.replay_count + 1)
        if metadata.last_replay_timestamp:
            try:
                last_replay = datetime.fromisoformat(metadata.last_replay_timestamp)
                since_last = datetime.now(UTC) - (
                    last_replay.replace(tzinfo=UTC) if last_replay.tzinfo is None else last_replay
                )
                if since_last.total_seconds() < expected_delay:
                    await msg.nak()
                    return
            except (ValueError, TypeError):
                pass

        # 5. Republish to original subject
        original_payload = data.get("original_message", "")
        if not original_payload:
            self._stats.total_skipped += 1
            await msg.ack()
            return

        try:
            await self._js.publish(
                metadata.original_subject,
                original_payload.encode("utf-8") if isinstance(original_payload, str) else original_payload,
            )
        except Exception as e:
            logger.warning(
                "dlq_replay_publish_failed",
                extra={
                    "subject": metadata.original_subject,
                    "error": str(e),
                },
            )
            await msg.nak()
            self._stats.total_errors += 1
            return

        # 6. Update metadata and ACK
        self._stats.total_replayed += 1
        self._stats.last_replay_subject = metadata.original_subject

        logger.info(
            "dlq_message_replayed",
            extra={
                "subject": metadata.original_subject,
                "replay_count": metadata.replay_count + 1,
                "error_type": error_type,
                "age_minutes": age.total_seconds() / 60,
            },
        )

        await msg.ack()
