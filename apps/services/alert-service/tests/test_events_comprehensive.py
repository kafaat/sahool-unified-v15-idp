"""
SAHOOL Alert Service - Comprehensive Events Tests
Tests for AlertEventPublisher, AlertEventSubscriber, singleton helpers, and message handling.
"""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

try:
    import nats  # noqa: F401
except ImportError:
    pytest.skip("nats not installed", allow_module_level=True)
# ═══════════════════════════════════════════════════════════════════════════════
# AlertTopics Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestAlertTopics:
    """Test NATS topic constants."""

    def test_publishing_topics(self):
        from src.events import AlertTopics

        assert AlertTopics.ALERT_CREATED == "sahool.alert.created"
        assert AlertTopics.ALERT_UPDATED == "sahool.alert.updated"
        assert AlertTopics.ALERT_ACKNOWLEDGED == "sahool.alert.acknowledged"
        assert AlertTopics.ALERT_RESOLVED == "sahool.alert.resolved"
        assert AlertTopics.ALERT_EXPIRED == "sahool.alert.expired"

    def test_subscription_topics(self):
        from src.events import AlertTopics

        assert AlertTopics.NDVI_ANOMALY == "sahool.satellite.ndvi.anomaly"
        assert AlertTopics.WEATHER_ALERT == "sahool.weather.alert"
        assert AlertTopics.IOT_THRESHOLD == "sahool.iot.threshold"
        assert AlertTopics.CROP_HEALTH_ALERT == "sahool.health.crop.alert"
        assert AlertTopics.IRRIGATION_ALERT == "sahool.irrigation.alert"
        assert AlertTopics.VISION_CRITICAL_ALERT == "sahool.vision.critical.alert"
# ═══════════════════════════════════════════════════════════════════════════════
# AlertEventPublisher Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestAlertEventPublisher:
    """Tests for AlertEventPublisher."""

    def test_initial_state(self):
        from src.events import AlertEventPublisher

        pub = AlertEventPublisher()
        assert pub._nc is None
        assert pub._connected is False
        assert pub.is_connected is False

    @pytest.mark.asyncio
    async def test_connect_success(self):
        from src.events import AlertEventPublisher

        pub = AlertEventPublisher()
        mock_nc = AsyncMock()
        with patch("src.events.nats.connect", new=AsyncMock(return_value=mock_nc)):
            result = await pub.connect()
            assert result is True
            assert pub._connected is True
            assert pub.is_connected is True

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        from src.events import AlertEventPublisher

        pub = AlertEventPublisher()
        with patch("src.events.nats.connect", new=AsyncMock(side_effect=Exception("Connection refused"))):
            result = await pub.connect()
            assert result is False
            assert pub._connected is False

    @pytest.mark.asyncio
    async def test_close_when_connected(self):
        from src.events import AlertEventPublisher

        pub = AlertEventPublisher()
        pub._nc = AsyncMock()
        pub._connected = True

        await pub.close()

        pub._nc.close.assert_awaited_once()
        assert pub._connected is False

    @pytest.mark.asyncio
    async def test_close_when_not_connected(self):
        from src.events import AlertEventPublisher

        pub = AlertEventPublisher()
        pub._nc = None
        pub._connected = False

        # Should not raise
        await pub.close()

    @pytest.mark.asyncio
    async def test_is_connected_property(self):
        from src.events import AlertEventPublisher

        pub = AlertEventPublisher()

        # Both must be truthy
        pub._nc = None
        pub._connected = True
        assert pub.is_connected is False

        pub._nc = AsyncMock()
        pub._connected = False
        assert pub.is_connected is False

        pub._nc = AsyncMock()
        pub._connected = True
        assert pub.is_connected is True

    @pytest.mark.asyncio
    async def test_publish_when_not_connected(self):
        from src.events import AlertEventPublisher

        pub = AlertEventPublisher()
        pub._connected = False
        pub._nc = None

        result = await pub._publish("topic", {"key": "value"})
        assert result is None

    @pytest.mark.asyncio
    async def test_publish_success(self):
        from src.events import AlertEventPublisher

        pub = AlertEventPublisher()
        pub._nc = AsyncMock()
        pub._connected = True

        result = await pub._publish("sahool.test.topic", {"data": "test"})
        assert result is not None  # Returns event_id
        pub._nc.publish.assert_awaited_once()

        # Verify the published payload
        call_args = pub._nc.publish.call_args
        topic = call_args[0][0]
        payload = json.loads(call_args[0][1].decode())
        assert topic == "sahool.test.topic"
        assert payload["data"] == "test"
        assert "event_id" in payload
        assert "timestamp" in payload
        assert payload["topic"] == "sahool.test.topic"

    @pytest.mark.asyncio
    async def test_publish_failure(self):
        from src.events import AlertEventPublisher

        pub = AlertEventPublisher()
        pub._nc = AsyncMock()
        pub._nc.publish.side_effect = Exception("Publish failed")
        pub._connected = True

        result = await pub._publish("topic", {"data": "test"})
        assert result is None

    @pytest.mark.asyncio
    async def test_publish_alert_created(self):
        from src.events import AlertEventPublisher, AlertTopics

        pub = AlertEventPublisher()
        pub._nc = AsyncMock()
        pub._connected = True

        result = await pub.publish_alert_created(
            alert_id="a1",
            field_id="f1",
            tenant_id="t1",
            alert_type="weather",
            severity="high",
            title="Storm",
            correlation_id="corr-1",
        )

        assert result is not None
        call_args = pub._nc.publish.call_args
        topic = call_args[0][0]
        payload = json.loads(call_args[0][1].decode())
        assert topic == AlertTopics.ALERT_CREATED
        assert payload["alert_id"] == "a1"
        assert payload["correlation_id"] == "corr-1"

    @pytest.mark.asyncio
    async def test_publish_alert_updated(self):
        from src.events import AlertEventPublisher, AlertTopics

        pub = AlertEventPublisher()
        pub._nc = AsyncMock()
        pub._connected = True

        result = await pub.publish_alert_updated(
            alert_id="a1",
            field_id="f1",
            old_status="active",
            new_status="acknowledged",
            updated_by="user-1",
        )

        assert result is not None
        call_args = pub._nc.publish.call_args
        payload = json.loads(call_args[0][1].decode())
        assert payload["old_status"] == "active"
        assert payload["new_status"] == "acknowledged"

    @pytest.mark.asyncio
    async def test_publish_alert_acknowledged(self):
        from src.events import AlertEventPublisher, AlertTopics

        pub = AlertEventPublisher()
        pub._nc = AsyncMock()
        pub._connected = True

        result = await pub.publish_alert_acknowledged("a1", "f1", "user-1")

        assert result is not None
        call_args = pub._nc.publish.call_args
        topic = call_args[0][0]
        payload = json.loads(call_args[0][1].decode())
        assert topic == AlertTopics.ALERT_ACKNOWLEDGED
        assert payload["acknowledged_by"] == "user-1"

    @pytest.mark.asyncio
    async def test_publish_alert_resolved(self):
        from src.events import AlertEventPublisher, AlertTopics

        pub = AlertEventPublisher()
        pub._nc = AsyncMock()
        pub._connected = True

        result = await pub.publish_alert_resolved("a1", "f1", "user-1", "Fixed it")

        assert result is not None
        call_args = pub._nc.publish.call_args
        topic = call_args[0][0]
        payload = json.loads(call_args[0][1].decode())
        assert topic == AlertTopics.ALERT_RESOLVED
        assert payload["resolved_by"] == "user-1"
        assert payload["resolution_note"] == "Fixed it"

    @pytest.mark.asyncio
    async def test_publish_alert_resolved_without_note(self):
        from src.events import AlertEventPublisher

        pub = AlertEventPublisher()
        pub._nc = AsyncMock()
        pub._connected = True

        result = await pub.publish_alert_resolved("a1", "f1", "user-1")

        assert result is not None
        call_args = pub._nc.publish.call_args
        payload = json.loads(call_args[0][1].decode())
        assert payload["resolution_note"] is None
# ═══════════════════════════════════════════════════════════════════════════════
# AlertEventSubscriber Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestAlertEventSubscriber:
    """Tests for AlertEventSubscriber."""

    def test_initial_state(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()
        assert sub._nc is None
        assert sub._subscriptions == []
        assert sub._handlers == {}

    @pytest.mark.asyncio
    async def test_connect_success(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()
        mock_nc = AsyncMock()
        with patch("src.events.nats.connect", new=AsyncMock(return_value=mock_nc)):
            result = await sub.connect()
            assert result is True
            assert sub._nc is mock_nc

    @pytest.mark.asyncio
    async def test_connect_failure(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()
        with patch("src.events.nats.connect", new=AsyncMock(side_effect=Exception("Fail"))):
            result = await sub.connect()
            assert result is False

    @pytest.mark.asyncio
    async def test_close(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()
        sub._nc = AsyncMock()
        mock_sub1 = AsyncMock()
        mock_sub2 = AsyncMock()
        sub._subscriptions = [mock_sub1, mock_sub2]

        await sub.close()

        mock_sub1.unsubscribe.assert_awaited_once()
        mock_sub2.unsubscribe.assert_awaited_once()
        sub._nc.close.assert_awaited_once()

    def test_register_handler(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()
        handler = AsyncMock()
        sub.register_handler("sahool.test.topic", handler)
        assert "sahool.test.topic" in sub._handlers
        assert sub._handlers["sahool.test.topic"] is handler

    @pytest.mark.asyncio
    async def test_subscribe_to_external_alerts_no_connection(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()
        sub._nc = None

        # Should not raise
        await sub.subscribe_to_external_alerts()
        assert sub._subscriptions == []

    @pytest.mark.asyncio
    async def test_subscribe_to_external_alerts(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()
        sub._nc = AsyncMock()
        sub._nc.subscribe = AsyncMock(return_value=MagicMock())

        await sub.subscribe_to_external_alerts()

        # Should subscribe to 6 topics
        assert sub._nc.subscribe.call_count == 6
        assert len(sub._subscriptions) == 6

    @pytest.mark.asyncio
    async def test_message_handler_with_registered_handler(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()
        handler = AsyncMock()
        sub._handlers["sahool.test.topic"] = handler

        msg = MagicMock()
        msg.subject = "sahool.test.topic"
        msg.data = json.dumps({"event_id": "e1", "data": "value"}).encode()

        await sub._message_handler(msg)

        handler.assert_awaited_once()
        call_data = handler.call_args[0][0]
        assert call_data["event_id"] == "e1"

    @pytest.mark.asyncio
    async def test_message_handler_no_handler_registered(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()
        # No handler registered

        msg = MagicMock()
        msg.subject = "sahool.unknown.topic"
        msg.data = json.dumps({"event_id": "e1"}).encode()

        # Should not raise
        await sub._message_handler(msg)

    @pytest.mark.asyncio
    async def test_message_handler_invalid_json(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()

        msg = MagicMock()
        msg.subject = "sahool.test.topic"
        msg.data = b"not valid json"

        # Should not raise, just log error
        await sub._message_handler(msg)

    @pytest.mark.asyncio
    async def test_message_handler_handler_exception(self):
        from src.events import AlertEventSubscriber

        sub = AlertEventSubscriber()
        handler = AsyncMock(side_effect=Exception("Handler crashed"))
        sub._handlers["sahool.test.topic"] = handler

        msg = MagicMock()
        msg.subject = "sahool.test.topic"
        msg.data = json.dumps({"event_id": "e1"}).encode()

        # Should not raise, just log error
        await sub._message_handler(msg)
# ═══════════════════════════════════════════════════════════════════════════════
# Singleton Factory Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestSingletonFactories:
    """Tests for get_publisher and get_subscriber singletons."""

    @pytest.mark.asyncio
    async def test_get_publisher_creates_and_connects(self):
        import src.events as events_module

        # Reset singleton
        events_module._publisher = None

        mock_pub = MagicMock()
        mock_pub.connect = AsyncMock(return_value=True)

        with patch.object(events_module, "AlertEventPublisher", return_value=mock_pub):
            result = await events_module.get_publisher()
            assert result is mock_pub
            mock_pub.connect.assert_awaited_once()

        # Cleanup
        events_module._publisher = None

    @pytest.mark.asyncio
    async def test_get_subscriber_creates_and_connects(self):
        import src.events as events_module

        # Reset singleton
        events_module._subscriber = None

        mock_sub = MagicMock()
        mock_sub.connect = AsyncMock(return_value=True)

        with patch.object(events_module, "AlertEventSubscriber", return_value=mock_sub):
            result = await events_module.get_subscriber()
            assert result is mock_sub
            mock_sub.connect.assert_awaited_once()

        # Cleanup
        events_module._subscriber = None
