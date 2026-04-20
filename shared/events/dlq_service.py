"""
SAHOOL Dead Letter Queue Management Service
============================================
خدمة إدارة قائمة انتظار الرسائل الفاشلة - DLQ Management

FastAPI service for managing, monitoring, and replaying failed messages
from the Dead Letter Queue.

Features:
- View DLQ messages with filtering and pagination
- Replay individual or bulk messages
- Archive old messages
- Monitor DLQ accumulation with alerts
- Export DLQ messages for analysis

Endpoints:
    GET  /dlq/messages              - List DLQ messages
    GET  /dlq/messages/{msg_id}     - Get specific message
    POST /dlq/replay/{msg_id}       - Replay single message
    POST /dlq/replay/bulk           - Replay multiple messages
    POST /dlq/archive               - Archive old messages
    GET  /dlq/stats                 - Get DLQ statistics
    DELETE /dlq/messages/{msg_id}   - Delete message from DLQ

Usage:
    # Run as standalone service
    uvicorn shared.events.dlq_service:app --host 0.0.0.0 --port 8000

    # Or integrate into existing FastAPI app
    from shared.events.dlq_service import create_dlq_router
    app.include_router(create_dlq_router(), prefix="/api/v1")
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .dlq_config import DLQConfig, DLQMessageMetadata
from .publisher import EventPublisher

logger = logging.getLogger(__name__)


def _sanitize_for_log(value: str, max_len: int = 256) -> str:
    """Strip CR/LF/tab from user-influenced strings before logging.

    The DLQ replay path reads subjects/errors that originated from remote
    publishers. Forwarding those into the logger without sanitisation lets
    an attacker forge additional log lines by embedding ``\\n`` in a
    subject or payload (CodeQL log-injection rule). Keep this cheap — we
    only escape the three characters that break one-line-per-event logs.
    """
    if not isinstance(value, str):
        value = str(value)
    if len(value) > max_len:
        value = value[:max_len] + "…"
    return value.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")


# NATS client - lazy import
_nats_available = False

try:
    import nats
    from nats.js import JetStreamContext

    _nats_available = True
except ImportError:
    logger.warning("NATS not available for DLQ service")


# ─────────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────────────────────


class DLQMessage(BaseModel):
    """DLQ message representation."""

    seq: int = Field(..., description="Message sequence number in DLQ stream")
    subject: str = Field(..., description="DLQ subject")
    timestamp: datetime = Field(..., description="Message timestamp")
    size: int = Field(..., description="Message size in bytes")
    metadata: DLQMessageMetadata = Field(..., description="DLQ metadata")
    original_data: str | None = Field(None, description="Original message payload")


class DLQMessageList(BaseModel):
    """List of DLQ messages with pagination."""

    messages: list[DLQMessage] = Field(default_factory=list)
    total_count: int = Field(..., description="Total message count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    has_more: bool = Field(..., description="More messages available")


class DLQStats(BaseModel):
    """DLQ statistics."""

    stream_name: str
    total_messages: int
    total_bytes: int
    oldest_message_age_seconds: int | None = None
    consumers: int
    subjects: list[str]

    # Aggregated stats
    messages_by_subject: dict[str, int] = Field(default_factory=dict)
    messages_by_error_type: dict[str, int] = Field(default_factory=dict)
    messages_by_service: dict[str, int] = Field(default_factory=dict)

    # Alert status
    alert_triggered: bool = False
    alert_threshold: int = 0


class ReplayRequest(BaseModel):
    """Request to replay message(s)."""

    message_seqs: list[int] = Field(..., description="Message sequence numbers to replay")
    delete_after_replay: bool = Field(default=True, description="Delete from DLQ after successful replay")


class ReplayResponse(BaseModel):
    """Response from replay operation."""

    success_count: int
    failure_count: int
    results: list[dict[str, Any]] = Field(default_factory=list)


class ArchiveRequest(BaseModel):
    """Request to archive old messages."""

    older_than_days: int = Field(..., ge=1, description="Archive messages older than N days")
    delete_after_archive: bool = Field(default=False, description="Delete after archiving")


class ArchiveResponse(BaseModel):
    """Response from archive operation."""

    archived_count: int
    deleted_count: int
    oldest_archived: datetime | None = None


# ─────────────────────────────────────────────────────────────────────────────
# DLQ Manager Class
# ─────────────────────────────────────────────────────────────────────────────


class DLQManager:
    """
    Manager for Dead Letter Queue operations.
    مدير قائمة انتظار الرسائل الفاشلة
    """

    def __init__(self, config: DLQConfig | None = None):
        self.config = config or DLQConfig()
        self._nc = None
        self._js: JetStreamContext | None = None
        self._connected = False
        self._publisher: EventPublisher | None = None

    async def connect(self):
        """Connect to NATS and JetStream."""
        if not _nats_available:
            raise RuntimeError("NATS not available")

        if self._connected:
            return

        try:
            nats_url = os.getenv("NATS_URL", "nats://localhost:4222")
            self._nc = await nats.connect(
                servers=[nats_url],
            )
            self._js = self._nc.jetstream()
            self._connected = True

            # Initialize publisher for replay
            self._publisher = EventPublisher()
            await self._publisher.connect()

            logger.info("✅ DLQ Manager connected to NATS")

        except Exception as e:
            logger.error(f"❌ Failed to connect DLQ Manager: {e}")
            raise

    async def close(self):
        """Close connections."""
        if self._publisher:
            await self._publisher.close()
        if self._nc:
            await self._nc.close()
        self._connected = False

    async def get_messages(
        self,
        page: int = 1,
        page_size: int = 50,
        subject_filter: str | None = None,
        error_type_filter: str | None = None,
        service_filter: str | None = None,
    ) -> DLQMessageList:
        """
        Get DLQ messages with filtering and pagination.

        Args:
            page: Page number (1-based)
            page_size: Messages per page
            subject_filter: Filter by original subject pattern
            error_type_filter: Filter by error type
            service_filter: Filter by consumer service

        Returns:
            List of DLQ messages
        """
        if not self._connected:
            await self.connect()

        try:
            # Get stream info
            stream_info = await self._js.stream_info(self.config.dlq_stream_name)
            total_count = stream_info.state.messages

            messages = []

            # Fetch messages from stream
            # Note: This is a simplified implementation
            # In production, you'd use a consumer with filtering
            consumer = await self._js.pull_subscribe(
                f"{self.config.dlq_subject_prefix}.>",
                durable="dlq_viewer",
            )

            fetched = await consumer.fetch(batch=page_size, timeout=5)

            for msg in fetched:
                try:
                    # Parse message
                    data = json.loads(msg.data.decode("utf-8"))
                    metadata = DLQMessageMetadata(**data.get("metadata", {}))

                    # Apply filters
                    if subject_filter and subject_filter not in metadata.original_subject:
                        continue
                    if error_type_filter and metadata.error_type != error_type_filter:
                        continue
                    if service_filter and metadata.consumer_service != service_filter:
                        continue

                    dlq_msg = DLQMessage(
                        seq=msg.metadata.sequence.stream,
                        subject=msg.subject,
                        timestamp=datetime.fromisoformat(metadata.failure_timestamp),
                        size=len(msg.data),
                        metadata=metadata,
                        original_data=data.get("original_message"),
                    )
                    messages.append(dlq_msg)

                except Exception as e:
                    logger.warning(f"Failed to parse DLQ message: {e}")

            return DLQMessageList(
                messages=messages,
                total_count=total_count,
                page=page,
                page_size=page_size,
                has_more=(page * page_size) < total_count,
            )

        except Exception as e:
            logger.error(f"Failed to get DLQ messages: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_stats(self) -> DLQStats:
        """Get DLQ statistics."""
        if not self._connected:
            await self.connect()

        try:
            stream_info = await self._js.stream_info(self.config.dlq_stream_name)

            # Calculate oldest message age
            oldest_age = None
            if stream_info.state.first_ts:
                oldest_age = int((datetime.now(UTC) - stream_info.state.first_ts).total_seconds())

            # Get aggregated stats (simplified - would need to scan messages)
            stats = DLQStats(
                stream_name=self.config.dlq_stream_name,
                total_messages=stream_info.state.messages,
                total_bytes=stream_info.state.bytes,
                oldest_message_age_seconds=oldest_age,
                consumers=stream_info.state.consumer_count,
                subjects=stream_info.config.subjects,
                alert_triggered=stream_info.state.messages > self.config.alert_threshold,
                alert_threshold=self.config.alert_threshold,
            )

            return stats

        except Exception as e:
            logger.error(f"Failed to get DLQ stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def replay_message(self, seq: int, delete_after: bool = True) -> bool:
        """
        Replay a message from DLQ to its original subject.

        Args:
            seq: Stream sequence number of the DLQ message to replay.
                 This is the JetStream `stream_seq`, not a consumer offset.
            delete_after: Delete from DLQ after successful replay

        Returns:
            True if replayed successfully

        Note: the previous implementation ignored `seq` and instead pulled
        whichever message the `dlq_replayer` consumer cursor returned next,
        which silently replayed the WRONG message. We now address the
        message directly by stream sequence via `js.get_msg(stream, seq)`.
        """
        if not self._connected:
            await self.connect()

        try:
            # Address the message by stream sequence — this is the whole
            # point of the `seq` parameter. `get_msg` returns a RawStreamMsg
            # (not a consumer message) so `ack()` is not applicable; we use
            # the stream's `delete_msg` API for the delete_after path.
            stream_name = self.config.dlq_stream_name
            try:
                raw_msg = await self._js.get_msg(stream_name, seq)
            except Exception as fetch_err:  # nats raises on not-found
                raise HTTPException(
                    status_code=404,
                    detail=f"DLQ message seq={seq} not found: {fetch_err}",
                ) from fetch_err

            data = json.loads(raw_msg.data.decode("utf-8"))
            metadata = DLQMessageMetadata(**data.get("metadata", {}))

            # Publish via JetStream so we get a PubAck before deleting the DLQ
            # row. Using core NATS publish here (fire-and-forget) would risk
            # deleting the DLQ copy while the replay never landed on the
            # destination stream — replay would look successful but the
            # event would be lost.
            original_payload = data.get("original_message", "")
            await self._js.publish(
                metadata.original_subject,
                original_payload.encode("utf-8"),
            )

            # original_subject is read back from the DLQ row payload — treat
            # it as user-influenced data. Strip CR/LF/tabs before logging so
            # an attacker who managed to write a DLQ entry cannot forge
            # additional log lines (CodeQL log-injection rule).
            safe_subject = _sanitize_for_log(metadata.original_subject)
            logger.info("Replayed message seq=%d to %s", seq, safe_subject)

            # Delete the DLQ row if requested (stream-level delete, not ack).
            # Only reached after js.publish() above returned a PubAck, so the
            # destination stream has durably persisted the replayed message.
            if delete_after:
                try:
                    await self._js.delete_msg(stream_name, seq)
                except Exception as del_err:  # best-effort; replay already succeeded
                    logger.warning(
                        "Failed to delete DLQ msg seq=%d: %s",
                        seq,
                        _sanitize_for_log(str(del_err)),
                    )

            return True

        except HTTPException:
            # Re-raise HTTPException (e.g. 404 for missing seq) unchanged —
            # otherwise the generic except below would downgrade it to 500.
            raise
        except Exception as e:
            logger.error("Failed to replay message: %s", _sanitize_for_log(str(e)))
            raise HTTPException(status_code=500, detail=str(e))

    async def replay_bulk(self, request: ReplayRequest) -> ReplayResponse:
        """Replay multiple messages."""
        success_count = 0
        failure_count = 0
        results = []

        for seq in request.message_seqs:
            try:
                await self.replay_message(seq, request.delete_after_replay)
                success_count += 1
                results.append({"seq": seq, "status": "success"})
            except Exception as e:
                failure_count += 1
                results.append({"seq": seq, "status": "failed", "error": str(e)})

        return ReplayResponse(
            success_count=success_count,
            failure_count=failure_count,
            results=results,
        )

    async def archive_old_messages(self, request: ArchiveRequest) -> ArchiveResponse:
        """Archive old messages from DLQ."""
        # This would involve:
        # 1. Fetching old messages
        # 2. Writing to archive storage (S3, file system, etc.)
        # 3. Optionally deleting from DLQ

        # Simplified implementation
        cutoff_date = datetime.now(UTC) - timedelta(days=request.older_than_days)

        # In production, implement actual archiving logic
        logger.info(f"Would archive messages older than {cutoff_date}")

        return ArchiveResponse(
            archived_count=0,
            deleted_count=0,
            oldest_archived=None,
        )


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI Router
# ─────────────────────────────────────────────────────────────────────────────


def create_dlq_router(manager: DLQManager | None = None) -> APIRouter:
    """
    Create FastAPI router for DLQ management endpoints.

    All endpoints require admin authentication.

    Args:
        manager: DLQ manager instance (creates new one if None)

    Returns:
        FastAPI router
    """
    router = APIRouter(prefix="/dlq", tags=["Dead Letter Queue"])

    dlq_manager = manager or DLQManager()

    # Auth dependency - DLQ management requires admin role
    try:
        from shared.auth.dependencies import require_roles
    except ImportError as exc:
        logger.exception(
            "DLQ endpoints require shared.auth.dependencies.require_roles; refusing to create unprotected router"
        )
        raise RuntimeError(
            "DLQ router requires admin authentication dependency 'shared.auth.dependencies.require_roles'"
        ) from exc

    admin_required = Depends(require_roles("admin", "super_admin"))

    # Build common dependencies list
    _deps = [admin_required]

    # NOTE: Lifecycle management (connect/close) is handled by the application
    # lifespan in create_app(), not via deprecated router.on_event hooks.

    @router.get("/messages", response_model=DLQMessageList, dependencies=_deps)
    async def list_dlq_messages(
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=200),
        subject: str | None = Query(None),
        error_type: str | None = Query(None),
        service: str | None = Query(None),
    ):
        """List DLQ messages with filtering and pagination."""
        return await dlq_manager.get_messages(
            page=page,
            page_size=page_size,
            subject_filter=subject,
            error_type_filter=error_type,
            service_filter=service,
        )

    @router.get("/stats", response_model=DLQStats, dependencies=_deps)
    async def get_dlq_stats():
        """Get DLQ statistics and health metrics."""
        return await dlq_manager.get_stats()

    @router.post("/replay/{seq}", response_model=dict[str, Any], dependencies=_deps)
    async def replay_single_message(
        seq: int,
        delete_after: bool = Query(True),
    ):
        """Replay a single message from DLQ."""
        success = await dlq_manager.replay_message(seq, delete_after)
        return {"seq": seq, "success": success}

    @router.post("/replay/bulk", response_model=ReplayResponse, dependencies=_deps)
    async def replay_bulk_messages(request: ReplayRequest):
        """Replay multiple messages from DLQ."""
        return await dlq_manager.replay_bulk(request)

    @router.post("/archive", response_model=ArchiveResponse, dependencies=_deps)
    async def archive_messages(request: ArchiveRequest):
        """Archive old DLQ messages."""
        return await dlq_manager.archive_old_messages(request)

    return router


# ─────────────────────────────────────────────────────────────────────────────
# Standalone FastAPI App
# ─────────────────────────────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Create standalone FastAPI application for DLQ management."""
    dlq_manager = DLQManager()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Application lifespan: connect DLQ on startup, close on shutdown."""
        await dlq_manager.connect()
        try:
            yield
        finally:
            await dlq_manager.close()

    app = FastAPI(
        title="SAHOOL DLQ Management API",
        description="Dead Letter Queue management and monitoring",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(create_dlq_router(manager=dlq_manager))

    return app


# For running directly via uvicorn. Guarded so services that import event subjects
# don't crash when auth dependencies (PyJWT) are unavailable in the container.
try:
    app = create_app()
except RuntimeError as _dlq_init_err:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "DLQ standalone app not initialized: %s — "
        "event subject imports will still work normally.", _dlq_init_err
    )
    app = None  # type: ignore[assignment]


if __name__ == "__main__":
    import uvicorn

    # Use environment variable for host binding, default to localhost for security
    # In production/containers, set DLQ_HOST=0.0.0.0
    host = os.getenv("DLQ_HOST", "127.0.0.1")
    port = int(os.getenv("DLQ_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
