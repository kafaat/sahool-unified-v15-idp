"""
Tests for SAHOOLEventBus — singleton, publish, subscribe, close, validation.

يغطي هذه الاختبارات:
- Singleton thread-safety (asyncio.Lock)
- إعادة تعيين singleton بعد close()
- التحقق من message_type
- تنسيق الموضوعات (subject format)
- EventMessage JSON serialization
- معالجة أخطاء النشر
- اسم durable يتضمن message_type
- عدم الاتصال يرفع RuntimeError
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures — import the module under test with nats mocked out
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_singleton():
    """Reset the SAHOOLEventBus singleton before every test."""
    from event_bus.nats_client import SAHOOLEventBus
    SAHOOLEventBus._instance = None
    yield
    SAHOOLEventBus._instance = None


@pytest.fixture()
def event_bus_module():
    """Import the event_bus module."""
    from event_bus import nats_client
    return nats_client


@pytest.fixture()
def EventBus(event_bus_module):
    return event_bus_module.SAHOOLEventBus


@pytest.fixture()
def EventMessage(event_bus_module):
    return event_bus_module.EventMessage


# ===========================================================================
# EventMessage
# ===========================================================================


class TestEventMessage:
    def test_to_json_returns_bytes(self, EventMessage):
        msg = EventMessage(
            subject="sahool.events.field.created.v1",
            data={"field_id": "f-1"},
            source="test-svc",
            tenant_id="t-1",
        )
        raw = msg.to_json()
        assert isinstance(raw, bytes)

    def test_to_json_contains_required_fields(self, EventMessage):
        msg = EventMessage(
            subject="sahool.events.field.created.v1",
            data={"moisture": 45.2},
            source="test-svc",
            tenant_id="t-abc",
        )
        parsed = json.loads(msg.to_json())
        assert parsed["source"] == "test-svc"
        assert parsed["tenant_id"] == "t-abc"
        assert parsed["data"]["moisture"] == 45.2
        assert parsed["version"] == "v1"
        assert "event_id" in parsed
        assert "timestamp" in parsed

    def test_to_json_tenant_id_none(self, EventMessage):
        msg = EventMessage("s", {}, "svc")
        parsed = json.loads(msg.to_json())
        assert parsed["tenant_id"] is None


# ===========================================================================
# Singleton behaviour
# ===========================================================================


class TestSingleton:
    @pytest.mark.asyncio
    async def test_get_instance_returns_same_object(self, EventBus):
        a = await EventBus.get_instance()
        b = await EventBus.get_instance()
        assert a is b

    @pytest.mark.asyncio
    async def test_concurrent_get_instance_returns_same_object(self, EventBus):
        """Multiple concurrent get_instance() calls must return same instance."""
        results = await asyncio.gather(
            EventBus.get_instance(),
            EventBus.get_instance(),
            EventBus.get_instance(),
        )
        assert all(r is results[0] for r in results)

    @pytest.mark.asyncio
    async def test_close_resets_singleton(self, EventBus):
        bus_a = await EventBus.get_instance()
        await bus_a.close()
        bus_b = await EventBus.get_instance()
        assert bus_b is not bus_a


# ===========================================================================
# connect()
# ===========================================================================


class TestConnect:
    @pytest.mark.asyncio
    async def test_connect_sets_service_name(self, EventBus):
        bus = await EventBus.get_instance()
        mock_nc = AsyncMock()
        mock_nc.jetstream.return_value = MagicMock()
        with patch("event_bus.nats_client.nats") as mock_nats:
            mock_nats.connect = AsyncMock(return_value=mock_nc)
            await bus.connect("nats://localhost:4222", "my-service")
        assert bus.service_name == "my-service"
        assert bus.nc is mock_nc
        assert bus.js is not None

    @pytest.mark.asyncio
    async def test_connect_failure_raises_connection_error(self, EventBus):
        bus = await EventBus.get_instance()
        with patch("event_bus.nats_client.nats") as mock_nats:
            mock_nats.connect = AsyncMock(side_effect=OSError("refused"))
            with pytest.raises(ConnectionError, match="refused"):
                await bus.connect("nats://bad:4222", "svc")

    @pytest.mark.asyncio
    async def test_connect_passes_reconnection_params(self, EventBus):
        bus = await EventBus.get_instance()
        mock_nc = AsyncMock()
        mock_nc.jetstream.return_value = MagicMock()
        with patch("event_bus.nats_client.nats") as mock_nats:
            mock_nats.connect = AsyncMock(return_value=mock_nc)
            await bus.connect("nats://localhost:4222", "svc")
            call_kwargs = mock_nats.connect.call_args[1]
            assert call_kwargs["max_reconnect_attempts"] == 60
            assert call_kwargs["reconnect_time_wait"] == 2


# ===========================================================================
# publish_event()
# ===========================================================================


class TestPublish:
    @pytest.mark.asyncio
    async def test_publish_raises_when_not_connected(self, EventBus):
        bus = await EventBus.get_instance()
        with pytest.raises(RuntimeError, match="not connected"):
            await bus.publish_event("field", "created", {})

    @pytest.mark.asyncio
    async def test_publish_builds_correct_subject(self, EventBus):
        bus = await EventBus.get_instance()
        bus.js = AsyncMock()
        bus.service_name = "test"
        await bus.publish_event("field", "created", {"id": 1}, tenant_id="t-1")
        subject = bus.js.publish.call_args[0][0]
        assert subject == "sahool.events.field.created.v1"

    @pytest.mark.asyncio
    async def test_publish_with_custom_message_type(self, EventBus):
        bus = await EventBus.get_instance()
        bus.js = AsyncMock()
        bus.service_name = "test"
        await bus.publish_event("ai", "run", {}, message_type="commands")
        subject = bus.js.publish.call_args[0][0]
        assert subject == "sahool.commands.ai.run.v1"

    @pytest.mark.asyncio
    async def test_publish_rejects_invalid_message_type(self, EventBus):
        bus = await EventBus.get_instance()
        bus.js = AsyncMock()
        bus.service_name = "test"
        with pytest.raises(ValueError, match="Invalid message_type"):
            await bus.publish_event("field", "created", {}, message_type="INVALID")

    @pytest.mark.asyncio
    async def test_publish_payload_contains_tenant_id(self, EventBus):
        bus = await EventBus.get_instance()
        bus.js = AsyncMock()
        bus.service_name = "test"
        await bus.publish_event("field", "created", {"x": 1}, tenant_id="t-99")
        payload = json.loads(bus.js.publish.call_args[0][1])
        assert payload["tenant_id"] == "t-99"
        assert payload["data"]["x"] == 1

    @pytest.mark.asyncio
    async def test_publish_failure_is_logged_and_reraised(self, EventBus):
        bus = await EventBus.get_instance()
        bus.js = AsyncMock()
        bus.js.publish.side_effect = Exception("stream not found")
        bus.service_name = "test"
        with pytest.raises(Exception, match="stream not found"):
            await bus.publish_event("field", "created", {})


# ===========================================================================
# subscribe_events()
# ===========================================================================


class TestSubscribe:
    @pytest.mark.asyncio
    async def test_subscribe_raises_when_not_connected(self, EventBus):
        bus = await EventBus.get_instance()
        with pytest.raises(RuntimeError, match="not connected"):
            await bus.subscribe_events("field", AsyncMock())

    @pytest.mark.asyncio
    async def test_subscribe_builds_wildcard_subject(self, EventBus):
        bus = await EventBus.get_instance()
        bus.js = AsyncMock()
        bus.service_name = "my-svc"
        await bus.subscribe_events("field", AsyncMock())
        subject = bus.js.subscribe.call_args[0][0]
        assert subject == "sahool.events.field.>"

    @pytest.mark.asyncio
    async def test_default_durable_includes_message_type(self, EventBus):
        bus = await EventBus.get_instance()
        bus.js = AsyncMock()
        bus.service_name = "my-svc"
        await bus.subscribe_events("field", AsyncMock())
        durable = bus.js.subscribe.call_args[1]["durable"]
        assert durable == "my-svc_events_field"

    @pytest.mark.asyncio
    async def test_default_durable_commands(self, EventBus):
        bus = await EventBus.get_instance()
        bus.js = AsyncMock()
        bus.service_name = "ai-advisor"
        await bus.subscribe_events("ai", AsyncMock(), message_type="commands")
        durable = bus.js.subscribe.call_args[1]["durable"]
        assert durable == "ai-advisor_commands_ai"

    @pytest.mark.asyncio
    async def test_explicit_durable_is_used(self, EventBus):
        bus = await EventBus.get_instance()
        bus.js = AsyncMock()
        bus.service_name = "svc"
        await bus.subscribe_events("field", AsyncMock(), durable="custom_name")
        durable = bus.js.subscribe.call_args[1]["durable"]
        assert durable == "custom_name"


# ===========================================================================
# close()
# ===========================================================================


class TestClose:
    @pytest.mark.asyncio
    async def test_close_calls_nc_close(self, EventBus):
        bus = await EventBus.get_instance()
        mock_nc = AsyncMock()
        bus.nc = mock_nc
        bus.js = MagicMock()
        await bus.close()
        mock_nc.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_close_clears_nc_and_js(self, EventBus):
        bus = await EventBus.get_instance()
        bus.nc = AsyncMock()
        bus.js = MagicMock()
        await bus.close()
        assert bus.nc is None
        assert bus.js is None

    @pytest.mark.asyncio
    async def test_close_without_connection_is_safe(self, EventBus):
        bus = await EventBus.get_instance()
        await bus.close()  # Should not raise
