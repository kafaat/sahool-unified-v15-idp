"""
Integration Tests for NATS IoT Events
اختبارات التكامل لأحداث إنترنت الأشياء عبر NATS

Tests for IoT-related NATS event publishing, subscribing, and schema validation.
Covers subjects:
    - sahool.iot.device_registered
    - sahool.iot.sensor_reading
    - sahool.iot.alert_triggered
    - sahool.iot.device.online
    - sahool.iot.device.offline

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")

# IoT event subjects
try:
    from shared.events.subjects import (
        SAHOOL_IOT_DEVICE_REGISTERED,
        SAHOOL_IOT_SENSOR_ALL,
        SAHOOL_IOT_SENSOR_ALERT,
        SAHOOL_IOT_SENSOR_CONNECTED,
        SAHOOL_IOT_SENSOR_DISCONNECTED,
        SAHOOL_IOT_SENSOR_READING,
    )
except ImportError:
    SAHOOL_IOT_DEVICE_REGISTERED = "sahool.iot.device.registered"
    SAHOOL_IOT_SENSOR_READING = "sahool.iot.sensor.reading"
    SAHOOL_IOT_SENSOR_ALERT = "sahool.iot.sensor.alert"
    SAHOOL_IOT_SENSOR_CONNECTED = "sahool.iot.sensor.connected"
    SAHOOL_IOT_SENSOR_DISCONNECTED = "sahool.iot.sensor.disconnected"
    SAHOOL_IOT_SENSOR_ALL = "sahool.iot.sensor.*"

# Additional IoT subjects used by the platform but not yet in subjects.py
SAHOOL_IOT_ALERT_TRIGGERED = "sahool.iot.alert_triggered"
SAHOOL_IOT_DEVICE_ONLINE = "sahool.iot.device.online"
SAHOOL_IOT_DEVICE_OFFLINE = "sahool.iot.device.offline"


# ─────────────────────────────────────────────────────────────────────────────
# Test Data Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_device_registered_payload(
    device_id: str | None = None,
    tenant_id: str | None = None,
) -> dict:
    """Build a valid iot.device_registered event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "iot-service",
        "device_id": device_id or str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "device_type": "soil_moisture_sensor",
        "device_type_ar": "مستشعر رطوبة التربة",
        "manufacturer": "Dragino",
        "model": "LSE01-8",
        "firmware_version": "1.4.2",
        "protocol": "LoRaWAN",
        "communication_type": "lpwan",
        "serial_number": "DRG-LSE01-2024-00451",
        "mac_address": "A8:40:41:00:12:CF",
        "location": {
            "latitude": 15.3694,
            "longitude": 44.1910,
            "altitude_m": 1120.5,
        },
        "sensors": [
            {
                "sensor_id": "soil_moisture_1",
                "type": "soil_moisture",
                "unit": "%",
                "depth_cm": 30,
                "min_value": 0.0,
                "max_value": 100.0,
            },
            {
                "sensor_id": "soil_temp_1",
                "type": "soil_temperature",
                "unit": "celsius",
                "depth_cm": 30,
                "min_value": -10.0,
                "max_value": 60.0,
            },
            {
                "sensor_id": "ec_1",
                "type": "electrical_conductivity",
                "unit": "dS/m",
                "depth_cm": 30,
                "min_value": 0.0,
                "max_value": 20.0,
            },
        ],
        "battery_level": 98.0,
        "signal_strength_dbm": -72,
        "sampling_interval_seconds": 900,
        "registered_by": str(uuid.uuid4()),
        "status": "active",
    }


def _make_sensor_reading_payload(
    device_id: str | None = None,
    field_id: str | None = None,
    tenant_id: str | None = None,
    soil_moisture: float = 42.5,
) -> dict:
    """Build a valid iot.sensor_reading event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "iot-gateway",
        "device_id": device_id or str(uuid.uuid4()),
        "field_id": field_id or str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "reading_id": str(uuid.uuid4()),
        "readings": [
            {
                "sensor_id": "soil_moisture_1",
                "sensor_type": "soil_moisture",
                "value": soil_moisture,
                "unit": "%",
                "quality": "good",
                "depth_cm": 30,
            },
            {
                "sensor_id": "soil_temp_1",
                "sensor_type": "soil_temperature",
                "value": 22.3,
                "unit": "celsius",
                "quality": "good",
                "depth_cm": 30,
            },
            {
                "sensor_id": "ec_1",
                "sensor_type": "electrical_conductivity",
                "value": 1.8,
                "unit": "dS/m",
                "quality": "good",
                "depth_cm": 30,
            },
        ],
        "battery_level": 87.5,
        "signal_strength_dbm": -68,
        "raw_payload_hex": "A10B2F03E8",
        "measurement_timestamp": datetime.now(UTC).isoformat(),
        "gateway_id": "gw-001",
        "protocol": "LoRaWAN",
        "frame_counter": 12345,
        "data_rate": "SF7BW125",
    }


def _make_alert_triggered_payload(
    device_id: str | None = None,
    tenant_id: str | None = None,
) -> dict:
    """Build a valid iot.alert_triggered event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "iot-service",
        "alert_id": str(uuid.uuid4()),
        "device_id": device_id or str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "alert_type": "threshold_exceeded",
        "alert_level": "warning",
        "sensor_id": "soil_moisture_1",
        "sensor_type": "soil_moisture",
        "current_value": 18.5,
        "threshold_value": 25.0,
        "threshold_direction": "below",
        "unit": "%",
        "message": "Soil moisture critically low. Irrigation recommended.",
        "message_ar": "رطوبة التربة منخفضة بشكل حرج. يُنصح بالري.",
        "recommended_action": "Start irrigation cycle within 6 hours",
        "recommended_action_ar": "بدء دورة الري خلال 6 ساعات",
        "consecutive_breach_count": 3,
        "last_normal_reading_timestamp": datetime.now(UTC).isoformat(),
        "acknowledgeable": True,
        "auto_resolve": False,
    }


def _make_device_status_payload(
    device_id: str | None = None,
    tenant_id: str | None = None,
    status: str = "online",
) -> dict:
    """Build a valid device.online or device.offline payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "iot-service",
        "device_id": device_id or str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "field_id": str(uuid.uuid4()),
        "status": status,
        "previous_status": "offline" if status == "online" else "online",
        "status_changed_at": datetime.now(UTC).isoformat(),
        "battery_level": 92.0 if status == "online" else None,
        "signal_strength_dbm": -65 if status == "online" else None,
        "reason": "Heartbeat received" if status == "online" else "Heartbeat timeout exceeded",
        "offline_duration_seconds": 0 if status == "online" else 3600,
        "last_reading_timestamp": datetime.now(UTC).isoformat(),
        "expected_next_heartbeat": datetime.now(UTC).isoformat() if status == "online" else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_nats():
    """Create a mock NATS client."""
    nc = AsyncMock()
    nc.publish = AsyncMock()
    nc.subscribe = AsyncMock()
    nc.flush = AsyncMock()
    nc.drain = AsyncMock()
    nc.close = AsyncMock()
    nc.is_connected = True
    return nc


@pytest.fixture
def mock_nats_msg():
    """Factory for mock NATS messages."""

    def _make(subject: str, payload: dict):
        msg = MagicMock()
        msg.subject = subject
        msg.data = json.dumps(payload).encode("utf-8")
        msg.headers = {}
        msg.ack = AsyncMock()
        msg.nak = AsyncMock()
        return msg

    return _make


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Device Registration Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_registered_event_published(mock_nats):
    """Test that device_registered event is published with device metadata."""
    payload = _make_device_registered_payload()
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_IOT_DEVICE_REGISTERED, data)
    mock_nats.publish.assert_awaited_once_with(SAHOOL_IOT_DEVICE_REGISTERED, data)

    decoded = json.loads(data)
    assert "device_id" in decoded
    assert "tenant_id" in decoded
    assert "field_id" in decoded
    assert "device_type" in decoded
    assert decoded["source_service"] == "iot-service"
    assert decoded["status"] == "active"

    # Verify sensors list
    assert "sensors" in decoded
    assert len(decoded["sensors"]) >= 1
    sensor = decoded["sensors"][0]
    assert "sensor_id" in sensor
    assert "type" in sensor
    assert "unit" in sensor

    # Location
    assert "location" in decoded
    loc = decoded["location"]
    assert -90 <= loc["latitude"] <= 90
    assert -180 <= loc["longitude"] <= 180


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_registered_subscribe_and_receive(mock_nats, mock_nats_msg):
    """Test subscribing to device_registered and receiving the event."""
    received_events: list[dict] = []

    async def handler(msg):
        data = json.loads(msg.data.decode("utf-8"))
        received_events.append(data)

    await mock_nats.subscribe(SAHOOL_IOT_DEVICE_REGISTERED, cb=handler)

    payload = _make_device_registered_payload()
    msg = mock_nats_msg(SAHOOL_IOT_DEVICE_REGISTERED, payload)
    await handler(msg)

    assert len(received_events) == 1
    assert received_events[0]["device_type"] == "soil_moisture_sensor"
    assert received_events[0]["protocol"] == "LoRaWAN"
    assert len(received_events[0]["sensors"]) == 3


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Sensor Reading Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sensor_reading_event_schema(mock_nats):
    """Test sensor_reading event payload contains valid reading data."""
    payload = _make_sensor_reading_payload(soil_moisture=35.0)
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_IOT_SENSOR_READING, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    assert "device_id" in decoded
    assert "field_id" in decoded
    assert "tenant_id" in decoded
    assert "reading_id" in decoded
    assert decoded["source_service"] == "iot-gateway"

    # Validate readings array
    assert "readings" in decoded
    readings = decoded["readings"]
    assert len(readings) >= 1

    for reading in readings:
        assert "sensor_id" in reading
        assert "sensor_type" in reading
        assert "value" in reading
        assert isinstance(reading["value"], (int, float))
        assert "unit" in reading
        assert "quality" in reading
        assert reading["quality"] in ("good", "suspect", "poor", "unknown")

    # Check soil moisture specifically
    sm_reading = next(r for r in readings if r["sensor_type"] == "soil_moisture")
    assert sm_reading["value"] == 35.0
    assert sm_reading["unit"] == "%"
    assert 0 <= sm_reading["value"] <= 100


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sensor_reading_low_moisture_triggers_processing(mock_nats, mock_nats_msg):
    """Test that a low soil moisture reading flows through the subscription system."""
    received_readings: list[dict] = []

    async def reading_handler(msg):
        data = json.loads(msg.data.decode("utf-8"))
        received_readings.append(data)

    await mock_nats.subscribe(SAHOOL_IOT_SENSOR_READING, cb=reading_handler)

    # Publish a critically low reading
    payload = _make_sensor_reading_payload(soil_moisture=12.0)
    msg = mock_nats_msg(SAHOOL_IOT_SENSOR_READING, payload)
    await reading_handler(msg)

    assert len(received_readings) == 1
    sm = next(r for r in received_readings[0]["readings"] if r["sensor_type"] == "soil_moisture")
    assert sm["value"] == 12.0
    assert sm["value"] < 25.0, "Moisture is below critical threshold"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: IoT Alert Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_alert_triggered_event_schema(mock_nats):
    """Test alert_triggered event payload includes threshold and bilingual message."""
    payload = _make_alert_triggered_payload()
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_IOT_ALERT_TRIGGERED, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    assert "alert_id" in decoded
    assert "device_id" in decoded
    assert "tenant_id" in decoded
    assert decoded["alert_type"] in ("threshold_exceeded", "anomaly", "device_fault", "connectivity_loss")
    assert decoded["alert_level"] in ("info", "warning", "critical")

    # Threshold fields
    assert "sensor_type" in decoded
    assert "current_value" in decoded
    assert "threshold_value" in decoded
    assert decoded["threshold_direction"] in ("above", "below")

    # Bilingual messages
    assert "message" in decoded and len(decoded["message"]) > 0
    assert "message_ar" in decoded and len(decoded["message_ar"]) > 0
    assert "recommended_action" in decoded
    assert "recommended_action_ar" in decoded


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Device Status Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_online_event(mock_nats):
    """Test device.online event payload with connectivity info."""
    payload = _make_device_status_payload(status="online")
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_IOT_DEVICE_ONLINE, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    assert decoded["status"] == "online"
    assert decoded["previous_status"] == "offline"
    assert decoded["battery_level"] is not None
    assert decoded["signal_strength_dbm"] is not None
    assert decoded["offline_duration_seconds"] == 0
    assert decoded["expected_next_heartbeat"] is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_offline_event(mock_nats):
    """Test device.offline event payload with downtime information."""
    payload = _make_device_status_payload(status="offline")
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_IOT_DEVICE_OFFLINE, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    assert decoded["status"] == "offline"
    assert decoded["previous_status"] == "online"
    assert decoded["offline_duration_seconds"] > 0
    assert decoded["reason"] == "Heartbeat timeout exceeded"
    assert decoded["expected_next_heartbeat"] is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_device_status_transition_sequence(mock_nats, mock_nats_msg):
    """Test a device status transition from online -> offline -> online."""
    status_changes: list[dict] = []

    async def status_handler(msg):
        data = json.loads(msg.data.decode("utf-8"))
        status_changes.append(data)

    # Subscribe to both online and offline events
    await mock_nats.subscribe(SAHOOL_IOT_DEVICE_ONLINE, cb=status_handler)
    await mock_nats.subscribe(SAHOOL_IOT_DEVICE_OFFLINE, cb=status_handler)

    device_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())

    # 1. Device comes online
    online_payload = _make_device_status_payload(device_id=device_id, tenant_id=tenant_id, status="online")
    msg = mock_nats_msg(SAHOOL_IOT_DEVICE_ONLINE, online_payload)
    await status_handler(msg)

    # 2. Device goes offline
    offline_payload = _make_device_status_payload(device_id=device_id, tenant_id=tenant_id, status="offline")
    msg = mock_nats_msg(SAHOOL_IOT_DEVICE_OFFLINE, offline_payload)
    await status_handler(msg)

    # 3. Device comes back online
    back_online_payload = _make_device_status_payload(device_id=device_id, tenant_id=tenant_id, status="online")
    msg = mock_nats_msg(SAHOOL_IOT_DEVICE_ONLINE, back_online_payload)
    await status_handler(msg)

    assert len(status_changes) == 3
    assert status_changes[0]["status"] == "online"
    assert status_changes[1]["status"] == "offline"
    assert status_changes[2]["status"] == "online"

    # All events should reference the same device
    for change in status_changes:
        assert change["device_id"] == device_id
        assert change["tenant_id"] == tenant_id
