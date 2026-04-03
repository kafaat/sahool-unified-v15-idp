"""
Tests for TenantContext and TenantAwareNATS.

يغطي هذه الاختبارات:
- إعداد وتنظيف tenant contextvar
- set_config يُستدعى بالمعاملات الصحيحة
- تنظيف الاتصال عند فشل __aenter__
- التحقق من صحة tenant_id (UUID)
- TenantAwareNATS: فلترة الرسائل حسب tenant
- TenantAwareNATS: ACK للرسائل المشوهة
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tenant.context import (
    TenantAwareNATS,
    TenantContext,
    _tenant_context,
)


# ===========================================================================
# TenantContext — contextvar management
# ===========================================================================


class TestTenantContextVar:
    @pytest.mark.asyncio
    async def test_sets_and_resets_contextvar(self):
        assert TenantContext.get_current() is None
        async with TenantContext(tenant_id="t-1"):
            assert TenantContext.get_current() == "t-1"
        assert TenantContext.get_current() is None

    @pytest.mark.asyncio
    async def test_nested_contexts(self):
        async with TenantContext(tenant_id="outer"):
            assert TenantContext.get_current() == "outer"
            async with TenantContext(tenant_id="inner"):
                assert TenantContext.get_current() == "inner"
            assert TenantContext.get_current() == "outer"

    @pytest.mark.asyncio
    async def test_context_without_db_pool(self):
        async with TenantContext(tenant_id="t-1") as ctx:
            assert ctx.conn is None
            assert TenantContext.get_current() == "t-1"


# ===========================================================================
# TenantContext — database integration (mocked)
# ===========================================================================


class TestTenantContextDB:
    @pytest.mark.asyncio
    async def test_sets_config_on_enter(self):
        mock_conn = AsyncMock()
        mock_pool = AsyncMock()
        mock_pool.acquire.return_value = mock_conn

        async with TenantContext(tenant_id="t-123", db_pool=mock_pool) as ctx:
            assert ctx.conn is mock_conn
            mock_conn.execute.assert_any_await(
                "SELECT set_config('app.current_tenant', $1, false)",
                "t-123",
            )

    @pytest.mark.asyncio
    async def test_clears_config_on_exit(self):
        mock_conn = AsyncMock()
        mock_pool = AsyncMock()
        mock_pool.acquire.return_value = mock_conn

        async with TenantContext(tenant_id="t-123", db_pool=mock_pool):
            pass

        # Last execute call should clear the tenant
        mock_conn.execute.assert_any_await(
            "SELECT set_config('app.current_tenant', '', false)"
        )
        mock_pool.release.assert_awaited_once_with(mock_conn)

    @pytest.mark.asyncio
    async def test_releases_conn_on_enter_failure(self):
        mock_conn = AsyncMock()
        mock_conn.execute.side_effect = RuntimeError("pg down")
        mock_pool = AsyncMock()
        mock_pool.acquire.return_value = mock_conn

        with pytest.raises(RuntimeError, match="pg down"):
            async with TenantContext(tenant_id="t-1", db_pool=mock_pool):
                pass  # pragma: no cover

        mock_pool.release.assert_awaited_once_with(mock_conn)
        # contextvar must be reset
        assert TenantContext.get_current() is None

    @pytest.mark.asyncio
    async def test_releases_conn_even_if_clear_fails(self):
        mock_conn = AsyncMock()
        call_count = 0

        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:  # The clear call in __aexit__
                raise RuntimeError("clear failed")

        mock_conn.execute = AsyncMock(side_effect=side_effect)
        mock_pool = AsyncMock()
        mock_pool.acquire.return_value = mock_conn

        with pytest.raises(RuntimeError, match="clear failed"):
            async with TenantContext(tenant_id="t-1", db_pool=mock_pool):
                pass

        # Connection must still be released despite the error
        mock_pool.release.assert_awaited_once_with(mock_conn)


# ===========================================================================
# TenantContext.validate_tenant_id
# ===========================================================================


class TestValidateTenantId:
    def test_valid_uuid(self):
        assert TenantContext.validate_tenant_id("123e4567-e89b-12d3-a456-426614174000")

    def test_invalid_uuid(self):
        assert not TenantContext.validate_tenant_id("not-a-uuid")
        assert not TenantContext.validate_tenant_id("")

    def test_uuid_without_dashes(self):
        assert TenantContext.validate_tenant_id("123e4567e89b12d3a456426614174000")


# ===========================================================================
# TenantAwareNATS
# ===========================================================================


def _make_msg(data: dict, subject: str = "test.subject") -> MagicMock:
    msg = MagicMock()
    msg.data = json.dumps(data).encode()
    msg.subject = subject
    msg.ack = AsyncMock()
    return msg


class TestTenantAwareNATS:
    @pytest.mark.asyncio
    async def test_publish_adds_tenant_id(self):
        mock_bus = AsyncMock()
        nats = TenantAwareNATS(mock_bus, tenant_id="t-1")
        await nats.publish_event("field", "created", {"name": "F1"})
        mock_bus.publish_event.assert_awaited_once_with(
            domain="field", action="created", data={"name": "F1"}, tenant_id="t-1"
        )

    @pytest.mark.asyncio
    async def test_subscribe_filters_matching_tenant(self):
        mock_bus = AsyncMock()
        handler = AsyncMock()
        nats = TenantAwareNATS(mock_bus, tenant_id="t-1")

        await nats.subscribe_events("field", handler)

        # Get the wrapped handler
        wrapped = mock_bus.subscribe_events.call_args[1]["handler"]

        # Matching tenant — handler should be called
        msg = _make_msg({"tenant_id": "t-1", "data": {}})
        await wrapped(msg)
        handler.assert_awaited_once_with(msg)

    @pytest.mark.asyncio
    async def test_subscribe_acks_other_tenant(self):
        mock_bus = AsyncMock()
        handler = AsyncMock()
        nats = TenantAwareNATS(mock_bus, tenant_id="t-1")

        await nats.subscribe_events("field", handler)
        wrapped = mock_bus.subscribe_events.call_args[1]["handler"]

        # Different tenant — handler should NOT be called, msg should be ACKed
        msg = _make_msg({"tenant_id": "t-OTHER", "data": {}})
        await wrapped(msg)
        handler.assert_not_awaited()
        msg.ack.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_subscribe_acks_malformed_json(self):
        mock_bus = AsyncMock()
        handler = AsyncMock()
        nats = TenantAwareNATS(mock_bus, tenant_id="t-1")

        await nats.subscribe_events("field", handler)
        wrapped = mock_bus.subscribe_events.call_args[1]["handler"]

        # Malformed JSON
        msg = MagicMock()
        msg.data = b"NOT JSON{{"
        msg.subject = "test"
        msg.ack = AsyncMock()
        await wrapped(msg)
        handler.assert_not_awaited()
        msg.ack.assert_awaited_once()
