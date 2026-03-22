"""
Tests for shared/events/dlq_service.py — Dead Letter Queue management service
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.events.dlq_config import DLQConfig, DLQMessageMetadata
from shared.events.dlq_service import (
    ArchiveRequest,
    ArchiveResponse,
    DLQManager,
    DLQMessage,
    DLQMessageList,
    DLQStats,
    ReplayRequest,
    ReplayResponse,
    create_app,
    create_dlq_router,
)


class TestPydanticModels:
    """Tests for request/response Pydantic models."""

    def test_dlq_message_model(self):
        meta = DLQMessageMetadata(
            original_subject="sahool.field.created",
            failure_reason="handler timeout",
            failure_timestamp="2026-01-01T00:00:00Z",
        )
        msg = DLQMessage(
            seq=1,
            subject="sahool.dlq.sahool.field.created",
            timestamp=datetime(2026, 1, 1, tzinfo=UTC),
            size=256,
            metadata=meta,
        )
        assert msg.seq == 1
        assert msg.original_data is None

    def test_dlq_message_list_model(self):
        ml = DLQMessageList(
            messages=[],
            total_count=0,
            page=1,
            page_size=50,
            has_more=False,
        )
        assert ml.total_count == 0
        assert ml.has_more is False

    def test_dlq_stats_model(self):
        stats = DLQStats(
            stream_name="SAHOOL_DLQ",
            total_messages=10,
            total_bytes=4096,
            consumers=1,
            subjects=["sahool.dlq.>"],
        )
        assert stats.alert_triggered is False
        assert stats.messages_by_subject == {}

    def test_replay_request_model(self):
        req = ReplayRequest(message_seqs=[1, 2, 3])
        assert len(req.message_seqs) == 3
        assert req.delete_after_replay is True

    def test_replay_response_model(self):
        resp = ReplayResponse(success_count=2, failure_count=1, results=[])
        assert resp.success_count == 2

    def test_archive_request_validation(self):
        req = ArchiveRequest(older_than_days=7)
        assert req.delete_after_archive is False

    def test_archive_request_rejects_zero_days(self):
        with pytest.raises(Exception):
            ArchiveRequest(older_than_days=0)

    def test_archive_response_model(self):
        resp = ArchiveResponse(archived_count=5, deleted_count=0)
        assert resp.oldest_archived is None


class TestDLQManager:
    """Tests for DLQManager."""

    def test_init_defaults(self):
        manager = DLQManager()
        assert manager.config is not None
        assert manager._connected is False
        assert manager._nc is None
        assert manager._js is None

    def test_init_with_custom_config(self):
        config = DLQConfig(max_retry_attempts=5, alert_threshold=200)
        manager = DLQManager(config=config)
        assert manager.config.max_retry_attempts == 5
        assert manager.config.alert_threshold == 200

    @pytest.mark.asyncio
    async def test_close_resets_state(self):
        manager = DLQManager()
        manager._nc = AsyncMock()
        manager._publisher = AsyncMock()
        manager._connected = True

        await manager.close()

        assert manager._connected is False
        manager._nc.close.assert_awaited_once()
        manager._publisher.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_handles_no_connections(self):
        manager = DLQManager()
        await manager.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_archive_old_messages(self):
        manager = DLQManager()
        request = ArchiveRequest(older_than_days=30)
        response = await manager.archive_old_messages(request)
        assert isinstance(response, ArchiveResponse)
        assert response.archived_count == 0
        assert response.deleted_count == 0

    @pytest.mark.asyncio
    async def test_replay_bulk(self):
        manager = DLQManager()
        manager._connected = True

        # Mock replay_message to succeed for seq=1 and fail for seq=2
        async def mock_replay(seq, delete_after=True):
            if seq == 2:
                raise RuntimeError("replay failed")
            return True

        manager.replay_message = mock_replay

        request = ReplayRequest(message_seqs=[1, 2])
        response = await manager.replay_bulk(request)
        assert response.success_count == 1
        assert response.failure_count == 1
        assert len(response.results) == 2
        assert response.results[0]["status"] == "success"
        assert response.results[1]["status"] == "failed"


class TestDLQRouter:
    """Tests for create_dlq_router."""

    def test_creates_router_with_default_manager(self):
        router = create_dlq_router()
        assert router is not None
        assert router.prefix == "/dlq"

    def test_creates_router_with_custom_manager(self):
        manager = DLQManager()
        router = create_dlq_router(manager=manager)
        assert router is not None

    def test_router_has_expected_routes(self):
        router = create_dlq_router()
        route_paths = [r.path for r in router.routes]
        assert "/dlq/messages" in route_paths
        assert "/dlq/stats" in route_paths
        assert "/dlq/archive" in route_paths


class TestCreateApp:
    """Tests for standalone app creation."""

    def test_create_app_returns_fastapi(self):
        app = create_app()
        assert app is not None
        assert app.title == "SAHOOL DLQ Management API"
        assert app.version == "1.0.0"
