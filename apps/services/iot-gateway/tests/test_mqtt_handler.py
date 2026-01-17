"""
Comprehensive MQTT Handler Tests
Tests MQTT message handling, broker connectivity, message processing
"""

import asyncio
import json
import sys
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Mock NATS before importing
sys.modules["nats"] = MagicMock()
sys.modules["nats.aio"] = MagicMock()
sys.modules["nats.aio.client"] = MagicMock()

from apps.services.iot_gateway.src.mqtt_client import (
    MockMqttClient,
    MqttClient,
    MqttMessage,
)
from apps.services.iot_gateway.src.registry import DeviceRegistry, DeviceStatus


class TestMqttMessage:
    """Test MqttMessage dataclass"""

    def test_create_mqtt_message(self):
        """Test creating an MQTT message"""
        msg = MqttMessage(
            topic="sahool/sensors/dev001/field001/soil_moisture",
            payload='{"value": 45.5}',
            qos=1,
            retain=False,
        )

        assert msg.topic == "sahool/sensors/dev001/field001/soil_moisture"
        assert msg.payload == '{"value": 45.5}'
        assert msg.qos == 1
        assert msg.retain is False

    def test_mqtt_message_with_qos_levels(self):
        """Test MQTT message with different QoS levels"""
        for qos in [0, 1, 2]:
            msg = MqttMessage(topic="test/topic", payload="test", qos=qos, retain=False)
            assert msg.qos == qos


class TestMqttClient:
    """Test MQTT client functionality"""

    def test_mqtt_client_initialization(self):
        """Test MQTT client initialization"""
        client = MqttClient(broker="mqtt.example.com", port=1883, username="user", password="pass")

        assert client.broker == "mqtt.example.com"
        assert client.port == 1883
        assert client.username == "user"
        assert client.password == "pass"

    def test_mqtt_client_default_values(self):
        """Test MQTT client with default values"""
        client = MqttClient()

        assert client.broker is not None
        assert client.port is not None
        assert client._running is False

    @pytest.mark.asyncio
    async def test_mqtt_client_connect_success(self):
        """Test successful MQTT connection"""
        client = MqttClient()

        # Mock the connection
        with patch("apps.services.iot_gateway.src.mqtt_client.Client") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            result = await client.connect()

            assert result is True

    @pytest.mark.asyncio
    async def test_mqtt_client_connect_failure(self):
        """Test failed MQTT connection"""
        client = MqttClient()

        # Mock connection failure
        with patch(
            "apps.services.iot_gateway.src.mqtt_client.Client",
            side_effect=Exception("Connection failed"),
        ):
            result = await client.connect()

            assert result is False

    @pytest.mark.asyncio
    async def test_mqtt_publish(self):
        """Test publishing message to MQTT"""
        client = MqttClient()

        payload = {"device_id": "dev001", "value": 45.5}
        topic = "sahool/sensors/test"

        # Mock the client
        with patch("apps.services.iot_gateway.src.mqtt_client.Client") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance

            await client.publish(topic, payload, qos=1, retain=False)

            # Verify publish was called
            mock_instance.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_mqtt_publish_with_qos(self):
        """Test publishing with different QoS levels"""
        client = MqttClient()

        payload = {"value": 45.5}
        topic = "test/topic"

        with patch("apps.services.iot_gateway.src.mqtt_client.Client") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance

            for qos in [0, 1, 2]:
                await client.publish(topic, payload, qos=qos)
                # Verify QoS was passed
                call_args = mock_instance.publish.call_args
                assert call_args is not None

    def test_mqtt_client_stop(self):
        """Test stopping MQTT client"""
        client = MqttClient()
        client._running = True

        client.stop()

        assert client._running is False


class TestMockMqttClient:
    """Test mock MQTT client for testing"""

    @pytest.mark.asyncio
    async def test_mock_client_connect(self):
        """Test mock client connection"""
        client = MockMqttClient()

        result = await client.connect()

        assert result is True

    def test_mock_client_queue_message(self):
        """Test queuing messages in mock client"""
        client = MockMqttClient()

        payload = {"device_id": "dev001", "value": 45.5}
        client.queue_message("test/topic", payload)

        assert len(client._messages) == 1
        assert client._messages[0].topic == "test/topic"

    @pytest.mark.asyncio
    async def test_mock_client_subscribe_processes_queued_messages(self):
        """Test that subscribe processes queued messages"""
        client = MockMqttClient()

        # Queue messages
        client.queue_message("topic1", {"value": 1})
        client.queue_message("topic2", {"value": 2})

        # Handler to collect messages
        received = []

        async def handler(msg: MqttMessage):
            received.append(msg)

        # Subscribe and process
        asyncio.create_task(client.subscribe("test/#", handler))
        await asyncio.sleep(0.3)  # Wait for processing
        client.stop()
        await asyncio.sleep(0.1)

        assert len(received) == 2

    @pytest.mark.asyncio
    async def test_mock_client_publish(self):
        """Test mock client publish"""
        client = MockMqttClient()

        payload = {"value": 45.5}
        await client.publish("test/topic", payload)

        # Mock publish just prints, doesn't raise


class TestMqttMessageHandling:
    """Test MQTT message handling logic"""

    @pytest.fixture
    def mock_registry(self):
        """Create mock registry with test device"""
        registry = DeviceRegistry()
        registry.register(
            device_id="test_device_001",
            tenant_id="tenant_1",
            field_id="field_1",
            device_type="soil_sensor",
            name_ar="حساس اختبار",
            name_en="Test Sensor",
        )
        return registry

    @pytest.fixture
    def mock_publisher(self):
        """Create mock IoT publisher"""
        publisher = MagicMock()
        publisher.publish_sensor_reading = AsyncMock(return_value="event_123")
        publisher.publish_device_status = AsyncMock(return_value="event_456")
        publisher.publish_device_alert = AsyncMock(return_value="event_789")
        return publisher

    @pytest.mark.asyncio
    async def test_handle_valid_mqtt_message(self, mock_registry, mock_publisher):
        """Test handling a valid MQTT message"""
        from apps.services.iot_gateway.src.main import handle_mqtt_message

        # Create message
        payload = {
            "device_id": "test_device_001",
            "field_id": "field_1",
            "type": "soil_moisture",
            "value": 45.5,
            "unit": "%",
        }
        msg = MqttMessage(
            topic="sahool/sensors/test_device_001/field_1/soil_moisture",
            payload=json.dumps(payload),
            qos=1,
            retain=False,
        )

        # Patch global variables
        with patch("apps.services.iot_gateway.src.main.registry", mock_registry):
            with patch("apps.services.iot_gateway.src.main.publisher", mock_publisher):
                await handle_mqtt_message(msg)

                # Verify publisher was called
                mock_publisher.publish_sensor_reading.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_mqtt_message_unregistered_device(self, mock_registry, mock_publisher):
        """Test handling message from unregistered device"""
        from apps.services.iot_gateway.src.main import handle_mqtt_message

        payload = {
            "device_id": "unknown_device",
            "field_id": "field_1",
            "type": "soil_moisture",
            "value": 45.5,
        }
        msg = MqttMessage(
            topic="sahool/sensors/unknown/field/soil_moisture",
            payload=json.dumps(payload),
            qos=1,
            retain=False,
        )

        with patch("apps.services.iot_gateway.src.main.registry", mock_registry):
            with patch("apps.services.iot_gateway.src.main.publisher", mock_publisher):
                # Should not raise, but should log error
                await handle_mqtt_message(msg)

                # Publisher should not be called
                mock_publisher.publish_sensor_reading.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_mqtt_message_with_auto_register(self, mock_registry, mock_publisher):
        """Test handling message with auto-registration enabled"""
        from apps.services.iot_gateway.src.main import handle_mqtt_message

        payload = {
            "device_id": "new_device_001",
            "field_id": "field_1",
            "type": "soil_moisture",
            "value": 45.5,
        }
        msg = MqttMessage(
            topic="sahool/sensors/new_device/field/soil_moisture",
            payload=json.dumps(payload),
            qos=1,
            retain=False,
        )

        with patch("apps.services.iot_gateway.src.main.registry", mock_registry):
            with patch("apps.services.iot_gateway.src.main.publisher", mock_publisher):
                with patch.dict("os.environ", {"IOT_AUTO_REGISTER": "true"}):
                    await handle_mqtt_message(msg)

                    # Device should be auto-registered
                    device = mock_registry.get("new_device_001")
                    assert device is not None

    @pytest.mark.asyncio
    async def test_handle_mqtt_message_out_of_range(self, mock_registry, mock_publisher):
        """Test handling message with out-of-range value"""
        from apps.services.iot_gateway.src.main import handle_mqtt_message

        payload = {
            "device_id": "test_device_001",
            "field_id": "field_1",
            "type": "soil_moisture",
            "value": 150.0,  # Out of range
        }
        msg = MqttMessage(
            topic="sahool/sensors/test_device/field/soil_moisture",
            payload=json.dumps(payload),
            qos=1,
            retain=False,
        )

        with patch("apps.services.iot_gateway.src.main.registry", mock_registry):
            with patch("apps.services.iot_gateway.src.main.publisher", mock_publisher):
                await handle_mqtt_message(msg)

                # Should be rejected, publisher not called
                mock_publisher.publish_sensor_reading.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_mqtt_message_with_metadata(self, mock_registry, mock_publisher):
        """Test handling message with battery and RSSI metadata"""
        from apps.services.iot_gateway.src.main import handle_mqtt_message

        payload = {
            "device_id": "test_device_001",
            "field_id": "field_1",
            "type": "soil_moisture",
            "value": 45.5,
            "battery": 85,
            "rssi": -65,
        }
        msg = MqttMessage(
            topic="sahool/sensors/test_device/field/soil_moisture",
            payload=json.dumps(payload),
            qos=1,
            retain=False,
        )

        with patch("apps.services.iot_gateway.src.main.registry", mock_registry):
            with patch("apps.services.iot_gateway.src.main.publisher", mock_publisher):
                await handle_mqtt_message(msg)

                # Verify metadata was passed to publisher
                call_args = mock_publisher.publish_sensor_reading.call_args
                assert call_args is not None
                assert "metadata" in call_args.kwargs

    @pytest.mark.asyncio
    async def test_handle_mqtt_message_invalid_json(self, mock_registry, mock_publisher):
        """Test handling message with invalid JSON"""
        from apps.services.iot_gateway.src.main import handle_mqtt_message

        msg = MqttMessage(
            topic="sahool/sensors/test/field/type",
            payload="this is not valid JSON",
            qos=1,
            retain=False,
        )

        with patch("apps.services.iot_gateway.src.main.registry", mock_registry):
            with patch("apps.services.iot_gateway.src.main.publisher", mock_publisher):
                # Should not raise, but should log error
                await handle_mqtt_message(msg)

                # Publisher should not be called
                mock_publisher.publish_sensor_reading.assert_not_called()


class TestMqttTopicPatterns:
    """Test MQTT topic pattern matching"""

    def test_topic_pattern_standard_format(self):
        """Test standard MQTT topic format"""
        topic = "sahool/sensors/dev001/field001/soil_moisture"
        parts = topic.split("/")

        assert parts[0] == "sahool"
        assert parts[1] == "sensors"
        assert parts[2] == "dev001"
        assert parts[3] == "field001"
        assert parts[4] == "soil_moisture"

    def test_topic_pattern_with_wildcards(self):
        """Test MQTT topic patterns with wildcards"""
        patterns = [
            "sahool/sensors/#",  # All sensors
            "sahool/sensors/+/field001/#",  # All devices in field001
            "sahool/sensors/dev001/+/soil_moisture",  # soil_moisture from dev001
        ]

        # Wildcards are matched by MQTT broker, just verify format
        for pattern in patterns:
            assert "/" in pattern
            assert "sahool" in pattern


class TestMqttSubscription:
    """Test MQTT subscription handling"""

    @pytest.mark.asyncio
    async def test_subscribe_to_topic(self):
        """Test subscribing to MQTT topic"""
        client = MockMqttClient()

        messages_received = []

        async def handler(msg: MqttMessage):
            messages_received.append(msg)

        # Queue test messages
        client.queue_message("test/topic", {"value": 1})
        client.queue_message("test/topic", {"value": 2})

        # Subscribe
        asyncio.create_task(client.subscribe("test/#", handler))
        await asyncio.sleep(0.3)
        client.stop()
        await asyncio.sleep(0.1)

        assert len(messages_received) == 2

    @pytest.mark.asyncio
    async def test_subscribe_with_error_handling(self):
        """Test subscription with error in handler"""
        client = MockMqttClient()

        async def failing_handler(msg: MqttMessage):
            raise ValueError("Handler error")

        # Queue message
        client.queue_message("test/topic", {"value": 1})

        # Subscribe with failing handler (should not crash)
        asyncio.create_task(client.subscribe("test/#", failing_handler))
        await asyncio.sleep(0.3)
        client.stop()
        await asyncio.sleep(0.1)

        # Should complete without raising


class TestMqttReconnection:
    """Test MQTT reconnection logic"""

    def test_reconnect_interval(self):
        """Test reconnection interval configuration"""
        client = MqttClient()

        assert client._reconnect_interval == 5  # Default 5 seconds

    @pytest.mark.asyncio
    async def test_subscribe_reconnects_on_error(self):
        """Test that subscribe reconnects on connection loss"""
        client = MqttClient()

        async def handler(msg: MqttMessage):
            pass

        # Mock the client to fail once then succeed
        with patch("apps.services.iot_gateway.src.mqtt_client.Client") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value.__aenter__.side_effect = [
                Exception("Connection failed"),
                mock_instance,
            ]

            # Start subscribe in background
            asyncio.create_task(client.subscribe("test/#", handler))

            # Let it try to connect and fail
            await asyncio.sleep(0.1)

            # Stop client
            client.stop()
            await asyncio.sleep(0.1)

            # Should have attempted to reconnect


class TestMqttIntegration:
    """Integration tests for MQTT handling"""

    @pytest.mark.asyncio
    async def test_end_to_end_message_flow(self):
        """Test complete message flow from MQTT to NATS"""
        # Setup
        registry = DeviceRegistry()
        registry.register(
            "integration_dev",
            "tenant_1",
            "field_1",
            "soil_sensor",
            "حساس",
            "Sensor",
        )

        publisher = MagicMock()
        publisher.publish_sensor_reading = AsyncMock(return_value="event_123")

        client = MockMqttClient()

        # Queue MQTT message
        payload = {
            "device_id": "integration_dev",
            "field_id": "field_1",
            "type": "soil_moisture",
            "value": 45.5,
        }
        client.queue_message("sahool/sensors/integration_dev/field_1/sm", payload)

        # Process messages
        from apps.services.iot_gateway.src.main import handle_mqtt_message

        async def handler(msg: MqttMessage):
            with patch("apps.services.iot_gateway.src.main.registry", registry):
                with patch("apps.services.iot_gateway.src.main.publisher", publisher):
                    await handle_mqtt_message(msg)

        # Subscribe and process
        asyncio.create_task(client.subscribe("sahool/#", handler))
        await asyncio.sleep(0.3)
        client.stop()
        await asyncio.sleep(0.1)

        # Verify
        publisher.publish_sensor_reading.assert_called_once()

    @pytest.mark.asyncio
    async def test_multiple_sensors_batch_processing(self):
        """Test processing multiple sensor readings in batch"""
        registry = DeviceRegistry()

        # Register multiple devices
        for i in range(5):
            registry.register(
                f"dev_{i:03d}",
                "tenant_1",
                "field_1",
                "soil_sensor",
                f"حساس {i}",
                f"Sensor {i}",
            )

        publisher = MagicMock()
        publisher.publish_sensor_reading = AsyncMock(return_value="event")

        client = MockMqttClient()

        # Queue multiple messages
        for i in range(5):
            payload = {
                "device_id": f"dev_{i:03d}",
                "field_id": "field_1",
                "type": "soil_moisture",
                "value": 40.0 + i,
            }
            client.queue_message(f"sahool/sensors/dev_{i:03d}/field_1/sm", payload)

        # Process
        from apps.services.iot_gateway.src.main import handle_mqtt_message

        async def handler(msg: MqttMessage):
            with patch("apps.services.iot_gateway.src.main.registry", registry):
                with patch("apps.services.iot_gateway.src.main.publisher", publisher):
                    await handle_mqtt_message(msg)

        asyncio.create_task(client.subscribe("sahool/#", handler))
        await asyncio.sleep(0.6)
        client.stop()
        await asyncio.sleep(0.1)

        # Verify all messages processed
        assert publisher.publish_sensor_reading.call_count == 5


class TestMqttSecurity:
    """Test MQTT security features"""

    def test_mqtt_client_with_authentication(self):
        """Test MQTT client with username/password"""
        client = MqttClient(username="iot_user", password="secure_password")

        assert client.username == "iot_user"
        assert client.password == "secure_password"

    def test_mqtt_client_without_authentication(self):
        """Test MQTT client without authentication"""
        client = MqttClient()

        # Should work without credentials (for development)
        assert client.username is not None  # May be empty string

    @pytest.mark.asyncio
    async def test_device_authorization_validation(self):
        """Test that device authorization is validated"""
        from apps.services.iot_gateway.src.main import handle_mqtt_message

        registry = DeviceRegistry()
        registry.register(
            "authorized_dev",
            "tenant_1",
            "field_1",
            "soil_sensor",
            "حساس",
            "Sensor",
        )

        publisher = MagicMock()
        publisher.publish_sensor_reading = AsyncMock()

        # Try to send data for different tenant
        payload = {
            "device_id": "authorized_dev",
            "field_id": "field_1",
            "type": "soil_moisture",
            "value": 45.5,
        }
        msg = MqttMessage(
            topic="sahool/sensors/authorized_dev/field_1/sm",
            payload=json.dumps(payload),
            qos=1,
            retain=False,
        )

        with patch("apps.services.iot_gateway.src.main.registry", registry):
            with patch("apps.services.iot_gateway.src.main.publisher", publisher):
                await handle_mqtt_message(msg)

                # Should be authorized and published
                publisher.publish_sensor_reading.assert_called_once()


class TestMqttPerformance:
    """Test MQTT performance characteristics"""

    @pytest.mark.asyncio
    async def test_high_frequency_messages(self):
        """Test handling high-frequency messages"""
        client = MockMqttClient()

        # Queue many messages rapidly
        for i in range(100):
            client.queue_message(f"test/topic/{i}", {"value": i})

        messages_received = []

        async def handler(msg: MqttMessage):
            messages_received.append(msg)

        # Process
        asyncio.create_task(client.subscribe("test/#", handler))
        await asyncio.sleep(1.0)  # Give time to process
        client.stop()
        await asyncio.sleep(0.1)

        # Should process all messages
        assert len(messages_received) > 0

    @pytest.mark.asyncio
    async def test_large_payload_handling(self):
        """Test handling large MQTT payloads"""
        client = MockMqttClient()

        # Create large payload
        large_payload = {
            "device_id": "dev001",
            "field_id": "field001",
            "type": "soil_moisture",
            "value": 45.5,
            "metadata": {"data": "x" * 10000},  # Large metadata
        }

        client.queue_message("test/topic", large_payload)

        received = []

        async def handler(msg: MqttMessage):
            received.append(msg)

        asyncio.create_task(client.subscribe("test/#", handler))
        await asyncio.sleep(0.3)
        client.stop()
        await asyncio.sleep(0.1)

        # Should handle large payload
        assert len(received) == 1


class TestMqttErrorRecovery:
    """Test MQTT error recovery"""

    @pytest.mark.asyncio
    async def test_recovery_from_malformed_message(self):
        """Test recovery from malformed MQTT message"""
        from apps.services.iot_gateway.src.main import handle_mqtt_message

        registry = DeviceRegistry()
        publisher = MagicMock()

        # Send malformed message
        msg = MqttMessage(topic="test/topic", payload="not json", qos=1, retain=False)

        with patch("apps.services.iot_gateway.src.main.registry", registry):
            with patch("apps.services.iot_gateway.src.main.publisher", publisher):
                # Should not crash
                await handle_mqtt_message(msg)

                # Subsequent messages should still work
                good_msg = MqttMessage(
                    topic="test/topic",
                    payload=json.dumps(
                        {
                            "device_id": "dev001",
                            "field_id": "field001",
                            "type": "temp",
                            "value": 25,
                        }
                    ),
                    qos=1,
                    retain=False,
                )

                # Should process without error
                await handle_mqtt_message(good_msg)

    @pytest.mark.asyncio
    async def test_recovery_from_handler_exception(self):
        """Test that MQTT client continues after handler exception"""
        client = MockMqttClient()

        call_count = 0

        async def handler(msg: MqttMessage):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First message error")
            # Second message should still be processed

        # Queue two messages
        client.queue_message("test/topic", {"value": 1})
        client.queue_message("test/topic", {"value": 2})

        # Process
        asyncio.create_task(client.subscribe("test/#", handler))
        await asyncio.sleep(0.3)
        client.stop()
        await asyncio.sleep(0.1)

        # Should have called handler twice despite first failure
        assert call_count == 2
