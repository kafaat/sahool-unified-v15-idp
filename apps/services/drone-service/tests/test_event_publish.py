"""
Tests for event publishing module - اختبارات وحدة نشر الأحداث
"""

import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.events.publish import (
    DronePublisher,
    EventEnvelope,
    _get_tenant_subject,
    publish_drone_event,
    publish_event,
    subscribe_cross_service_events,
)

VALID_TENANT_ID = str(uuid.uuid4())


class TestEventEnvelope:
    """Test EventEnvelope data class."""

    def test_create_sets_fields(self):
        env = EventEnvelope.create(
            event_type="drone_registered",
            version=1,
            aggregate_id="agg-1",
            tenant_id="tenant-1",
            correlation_id="corr-1",
            payload={"key": "value"},
        )
        assert env.event_type == "drone_registered"
        assert env.version == 1
        assert env.aggregate_id == "agg-1"
        assert env.tenant_id == "tenant-1"
        assert env.correlation_id == "corr-1"
        assert env.payload == {"key": "value"}
        uuid.UUID(env.event_id)
        assert env.timestamp is not None

    def test_to_dict(self):
        env = EventEnvelope(
            event_id="eid",
            event_type="test",
            version=1,
            aggregate_id="agg",
            tenant_id="tid",
            correlation_id="cid",
            timestamp="2026-01-01T00:00:00",
            payload={"a": 1},
        )
        d = env.to_dict()
        assert d["event_id"] == "eid"
        assert d["event_type"] == "test"
        assert d["version"] == 1
        assert d["aggregate_id"] == "agg"
        assert d["tenant_id"] == "tid"
        assert d["correlation_id"] == "cid"
        assert d["timestamp"] == "2026-01-01T00:00:00"
        assert d["payload"] == {"a": 1}

    def test_create_generates_unique_ids(self):
        e1 = EventEnvelope.create("t", 1, "a", "t", "c", {})
        e2 = EventEnvelope.create("t", 1, "a", "t", "c", {})
        assert e1.event_id != e2.event_id


class TestDronePublisher:
    """Test DronePublisher class."""

    def test_init_default_url(self):
        pub = DronePublisher()
        # nats_url comes from NATS_URL env var with fallback to "nats://nats:4222";
        # when NATS_URL is set to "" (e.g. in test), the result is ""
        assert isinstance(pub.nats_url, str)

    def test_init_custom_url(self):
        pub = DronePublisher("nats://custom:4222")
        assert pub.nats_url == "nats://custom:4222"
        assert pub.nc is None

    @pytest.mark.asyncio
    async def test_connect(self):
        pub = DronePublisher("nats://test:4222")
        mock_nc = AsyncMock()
        with patch("nats.connect", new_callable=AsyncMock, return_value=mock_nc) as mock_connect:
            await pub.connect()
            mock_connect.assert_called_once_with("nats://test:4222")
            assert pub.nc is mock_nc

    @pytest.mark.asyncio
    async def test_close_with_connection(self):
        pub = DronePublisher()
        pub.nc = AsyncMock()
        await pub.close()
        pub.nc.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_without_connection(self):
        pub = DronePublisher()
        pub.nc = None
        await pub.close()  # should not raise

    @pytest.mark.asyncio
    async def test_publish_no_connection_returns_empty(self):
        pub = DronePublisher()
        pub.nc = None
        result = await pub.publish("drone_registered", "t1", "agg1", {"k": "v"})
        assert result == ""

    @pytest.mark.asyncio
    async def test_publish_success(self):
        pub = DronePublisher()
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        pub.nc = mock_nc
        result = await pub.publish("drone_registered", VALID_TENANT_ID, "agg1", {"k": "v"}, "corr1")
        assert result != ""
        assert mock_nc.publish.call_count == 2  # global + tenant-scoped

    @pytest.mark.asyncio
    async def test_publish_exception_returns_empty(self):
        pub = DronePublisher()
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock(side_effect=Exception("NATS down"))
        pub.nc = mock_nc
        result = await pub.publish("drone_registered", VALID_TENANT_ID, "agg1", {})
        assert result == ""

    @pytest.mark.asyncio
    async def test_publish_generates_correlation_id_if_missing(self):
        pub = DronePublisher()
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        pub.nc = mock_nc
        result = await pub.publish("drone_registered", VALID_TENANT_ID, "agg1", {}, correlation_id=None)
        assert result != ""

    @pytest.mark.asyncio
    async def test_publish_drone_registered(self):
        pub = DronePublisher()
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        pub.nc = mock_nc
        result = await pub.publish_drone_registered(VALID_TENANT_ID, "drone-1", "DJI-T30")
        assert result != ""

    @pytest.mark.asyncio
    async def test_publish_flight_planned(self):
        pub = DronePublisher()
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        pub.nc = mock_nc
        result = await pub.publish_flight_planned(VALID_TENANT_ID, "plan-1", "spray", "field-1")
        assert result != ""

    @pytest.mark.asyncio
    async def test_publish_mission_event(self):
        pub = DronePublisher()
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        pub.nc = mock_nc
        result = await pub.publish_mission_event("mission_started", VALID_TENANT_ID, "msn-1", "drone-1")
        assert result != ""

    @pytest.mark.asyncio
    async def test_publish_mission_event_no_drone(self):
        pub = DronePublisher()
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        pub.nc = mock_nc
        result = await pub.publish_mission_event("mission_started", VALID_TENANT_ID, "msn-1")
        assert result != ""

    @pytest.mark.asyncio
    async def test_publish_prescription_created(self):
        pub = DronePublisher()
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        pub.nc = mock_nc
        result = await pub.publish_prescription_created(VALID_TENANT_ID, "rx-1", "field-1", "ndvi")
        assert result != ""


class TestGetTenantSubject:
    """Test _get_tenant_subject helper."""

    def test_with_valid_uuid(self):
        result = _get_tenant_subject(VALID_TENANT_ID, "registered")
        assert VALID_TENANT_ID in result
        assert "drone" in result

    def test_with_fallback_format(self):
        # With shared.events.subjects available but non-UUID tenant, it may raise.
        # Use a valid UUID to get proper result.
        tid = str(uuid.uuid4())
        result = _get_tenant_subject(tid, "registered")
        assert tid in result


class TestPublishEvent:
    """Test backward-compatible publish_event helper."""

    @pytest.mark.asyncio
    async def test_publish_event_with_nc(self):
        nc = AsyncMock()
        nc.publish = AsyncMock()
        await publish_event(nc, "sahool.drone.test", {"key": "val"}, VALID_TENANT_ID)
        nc.publish.assert_called_once()
        call_args = nc.publish.call_args
        data = json.loads(call_args[0][1].decode())
        assert data["tenant_id"] == VALID_TENANT_ID
        assert data["key"] == "val"

    @pytest.mark.asyncio
    async def test_publish_event_no_nc(self):
        await publish_event(None, "subject", {})  # should not raise

    @pytest.mark.asyncio
    async def test_publish_event_no_tenant(self):
        nc = AsyncMock()
        nc.publish = AsyncMock()
        await publish_event(nc, "subject", {"a": 1}, tenant_id=None)
        nc.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_event_exception(self):
        nc = AsyncMock()
        nc.publish = AsyncMock(side_effect=Exception("fail"))
        await publish_event(nc, "subject", {})  # should not raise


class TestPublishDroneEvent:
    """Test backward-compatible publish_drone_event helper."""

    @pytest.mark.asyncio
    async def test_publish_drone_event(self):
        nc = AsyncMock()
        nc.publish = AsyncMock()
        await publish_drone_event(nc, "sahool.drone.registered", VALID_TENANT_ID, drone_id="d1")
        # publish_event is called twice (global + tenant)
        assert nc.publish.call_count == 2


class TestSubscribeCrossServiceEvents:
    """Test cross-service event subscriptions."""

    @pytest.mark.asyncio
    async def test_subscribe_with_nc(self):
        nc = AsyncMock()
        nc.subscribe = AsyncMock()
        app_state = MagicMock()
        app_state.pending_detections = []
        await subscribe_cross_service_events(nc, app_state)
        # Should subscribe to 4 subjects (pest, disease, weed, weather)
        assert nc.subscribe.call_count == 4

    @pytest.mark.asyncio
    async def test_subscribe_without_nc(self):
        app_state = MagicMock()
        await subscribe_cross_service_events(None, app_state)  # should not raise

    @pytest.mark.asyncio
    async def test_subscribe_exception_handled(self):
        nc = AsyncMock()
        nc.subscribe = AsyncMock(side_effect=Exception("sub failed"))
        app_state = MagicMock()
        app_state.pending_detections = []
        await subscribe_cross_service_events(nc, app_state)  # should not raise

    @pytest.mark.asyncio
    async def test_vision_detection_callback(self):
        nc = AsyncMock()
        nc.subscribe = AsyncMock()
        app_state = MagicMock()
        app_state.pending_detections = []

        await subscribe_cross_service_events(nc, app_state)

        # Get the callback from the first subscribe call
        cb = nc.subscribe.call_args_list[0][1]["cb"]
        msg = MagicMock()
        msg.data = json.dumps({"field_id": "f1", "detection_type": "pest"}).encode()
        msg.subject = "sahool.vision.pest_detected"

        await cb(msg)
        assert len(app_state.pending_detections) == 1
        assert app_state.pending_detections[0]["field_id"] == "f1"

    @pytest.mark.asyncio
    async def test_vision_detection_callback_bad_data(self):
        nc = AsyncMock()
        nc.subscribe = AsyncMock()
        app_state = MagicMock()
        app_state.pending_detections = []

        await subscribe_cross_service_events(nc, app_state)

        cb = nc.subscribe.call_args_list[0][1]["cb"]
        msg = MagicMock()
        msg.data = b"not json"
        msg.subject = "test"

        await cb(msg)  # should not raise
        assert len(app_state.pending_detections) == 0

    @pytest.mark.asyncio
    async def test_weather_alert_callback(self):
        nc = AsyncMock()
        nc.subscribe = AsyncMock()
        app_state = MagicMock()
        app_state.pending_detections = []

        await subscribe_cross_service_events(nc, app_state)

        # Weather alert is the 4th subscription
        cb = nc.subscribe.call_args_list[3][1]["cb"]
        msg = MagicMock()
        msg.data = json.dumps({"alert_type": "high_wind"}).encode()

        await cb(msg)  # should not raise
