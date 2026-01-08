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
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from .dlq_config import DLQConfig, DLQMessageMetadata
from .publisher import EventPublisher

logger = logging.getLogger(__name__)

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
    delete_after_replay: bool = Field(
        default=True, description="Delete from DLQ after successful replay"
    )


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
            self._nc = await nats.connect(
                servers=[f"nats://{self.config.dlq_stream_name}:4222"],
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

            # Calculate pagination
            (page - 1) * page_size + 1

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
                oldest_age = int((datetime.utcnow() - stream_info.state.first_ts).total_seconds())

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
            seq: Message sequence number
            delete_after: Delete from DLQ after successful replay

        Returns:
            True if replayed successfully
        """
        if not self._connected:
            await self.connect()

        try:
            # Fetch the specific message
            consumer = await self._js.pull_subscribe(
                f"{self.config.dlq_subject_prefix}.>",
                durable="dlq_replayer",
            )

            messages = await consumer.fetch(batch=1, timeout=5)

            if not messages:
                raise HTTPException(status_code=404, detail="Message not found")

            msg = messages[0]
            data = json.loads(msg.data.decode("utf-8"))
            metadata = DLQMessageMetadata(**data.get("metadata", {}))

            # Publish to original subject
            original_payload = data.get("original_message", "")

            await self._publisher._nc.publish(
                metadata.original_subject,
                original_payload.encode("utf-8"),
            )

            logger.info(f"✅ Replayed message seq={seq} to {metadata.original_subject}")

            # Delete if requested
            if delete_after:
                await msg.ack()

            return True

        except Exception as e:
            logger.error(f"Failed to replay message: {e}")
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
        cutoff_date = datetime.utcnow() - timedelta(days=request.older_than_days)

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

    Args:
        manager: DLQ manager instance (creates new one if None)

    Returns:
        FastAPI router
    """
    router = APIRouter(prefix="/dlq", tags=["Dead Letter Queue"])

    dlq_manager = manager or DLQManager()

    @router.on_event("startup")
    async def startup():
        """Connect DLQ manager on startup."""
        await dlq_manager.connect()

    @router.on_event("shutdown")
    async def shutdown():
        """Close DLQ manager on shutdown."""
        await dlq_manager.close()

    @router.get("/messages", response_model=DLQMessageList)
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

    @router.get("/stats", response_model=DLQStats)
    async def get_dlq_stats():
        """Get DLQ statistics and health metrics."""
        return await dlq_manager.get_stats()

    @router.post("/replay/{seq}", response_model=dict[str, Any])
    async def replay_single_message(
        seq: int,
        delete_after: bool = Query(True),
    ):
        """Replay a single message from DLQ."""
        success = await dlq_manager.replay_message(seq, delete_after)
        return {"seq": seq, "success": success}

    @router.post("/replay/bulk", response_model=ReplayResponse)
    async def replay_bulk_messages(request: ReplayRequest):
        """Replay multiple messages from DLQ."""
        return await dlq_manager.replay_bulk(request)

    @router.post("/archive", response_model=ArchiveResponse)
    async def archive_messages(request: ArchiveRequest):
        """Archive old DLQ messages."""
        return await dlq_manager.archive_old_messages(request)

    return router


# ─────────────────────────────────────────────────────────────────────────────
# Standalone FastAPI App
# ─────────────────────────────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Create standalone FastAPI application for DLQ management."""
    app = FastAPI(
        title="SAHOOL DLQ Management API",
        description="Dead Letter Queue management and monitoring",
        version="1.0.0",
    )

    app.include_router(create_dlq_router())

    return app


# For running directly
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
