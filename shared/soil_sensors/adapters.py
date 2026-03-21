"""
Sensor Protocol Adapters - محولات بروتوكولات المجسات
Support for MQTT, LoRaWAN, HTTP protocols
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable

from .models import (
    SensorProtocol,
    SensorReading,
    SensorType,
    SoilSensor,
)

logger = logging.getLogger(__name__)


@dataclass
class AdapterConfig:
    """Base adapter configuration"""

    protocol: SensorProtocol
    # Connection settings
    host: str = "localhost"
    port: int = 1883
    username: str | None = None
    password: str | None = None
    # TLS
    use_tls: bool = False
    ca_cert: str | None = None
    # Timeouts
    connect_timeout: int = 30
    read_timeout: int = 60


class SensorAdapter(ABC):
    """
    Abstract base class for sensor protocol adapters
    فئة أساسية مجردة لمحولات بروتوكولات المجسات
    """

    def __init__(self, config: AdapterConfig):
        self.config = config
        self.connected = False
        self._callbacks: list[Callable[[SensorReading], None]] = []

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the sensor network"""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from the sensor network"""
        pass

    @abstractmethod
    async def subscribe(self, sensor: SoilSensor):
        """Subscribe to sensor data"""
        pass

    @abstractmethod
    async def unsubscribe(self, sensor: SoilSensor):
        """Unsubscribe from sensor data"""
        pass

    def on_reading(self, callback: Callable[[SensorReading], None]):
        """Register callback for new readings"""
        self._callbacks.append(callback)

    def _emit_reading(self, reading: SensorReading):
        """Emit reading to all callbacks"""
        for callback in self._callbacks:
            try:
                callback(reading)
            except Exception as e:
                logger.warning("Callback error during sensor reading emission", exc_info=True)

    @abstractmethod
    def parse_payload(self, payload: bytes, sensor: SoilSensor) -> SensorReading | None:
        """Parse raw payload into SensorReading"""
        pass


class MQTTAdapter(SensorAdapter):
    """
    MQTT Protocol Adapter - محول بروتوكول MQTT
    For sensors using MQTT protocol (most common)
    """

    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self.client = None
        self._subscriptions: dict[str, SoilSensor] = {}

    async def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            # In production, use aiomqtt or asyncio-mqtt
            # import aiomqtt
            # self.client = aiomqtt.Client(
            #     hostname=self.config.host,
            #     port=self.config.port,
            #     username=self.config.username,
            #     password=self.config.password,
            # )
            # await self.client.connect()

            self.connected = True
            return True
        except Exception as e:
            print(f"MQTT connection failed: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            # await self.client.disconnect()
            pass
        self.connected = False

    async def subscribe(self, sensor: SoilSensor):
        """Subscribe to sensor MQTT topic"""
        if not sensor.mqtt_topic:
            topic = f"sahool/sensors/{sensor.tenant_id}/{sensor.field_id}/{sensor.id}"
        else:
            topic = sensor.mqtt_topic

        self._subscriptions[topic] = sensor

        if self.client:
            # await self.client.subscribe(topic)
            pass

    async def unsubscribe(self, sensor: SoilSensor):
        """Unsubscribe from sensor topic"""
        topic = sensor.mqtt_topic or f"sahool/sensors/{sensor.tenant_id}/{sensor.field_id}/{sensor.id}"

        if topic in self._subscriptions:
            del self._subscriptions[topic]

        if self.client:
            # await self.client.unsubscribe(topic)
            pass

    def parse_payload(self, payload: bytes, sensor: SoilSensor) -> SensorReading | None:
        """
        Parse MQTT payload into SensorReading
        Supports multiple payload formats
        """
        try:
            data = json.loads(payload.decode())

            # Standard SAHOOL format
            if "value" in data and "type" in data:
                return SensorReading(
                    sensor_id=sensor.id,
                    timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now(UTC).isoformat())),
                    reading_type=SensorType(data.get("type", sensor.sensor_type.value)),
                    value=float(data["value"]),
                    unit=data.get("unit", "%"),
                    quality=float(data.get("quality", 1.0)),
                    is_valid=data.get("valid", True),
                    battery_percent=data.get("battery"),
                    signal_strength=data.get("rssi"),
                    raw_value=data.get("raw_value"),
                    raw_unit=data.get("raw_unit"),
                )

            # CropX format
            if "moisture" in data:
                return SensorReading(
                    sensor_id=sensor.id,
                    timestamp=datetime.now(UTC),
                    reading_type=SensorType.MOISTURE,
                    value=float(data["moisture"]),
                    unit="%",
                    depth_cm=data.get("depth", sensor.depth_cm),
                    battery_percent=data.get("battery"),
                )

            # Generic numeric format
            if isinstance(data, (int, float)):
                return SensorReading(
                    sensor_id=sensor.id,
                    timestamp=datetime.now(UTC),
                    reading_type=sensor.sensor_type,
                    value=float(data),
                    unit="%",
                )

        except Exception as e:
            print(f"Payload parse error: {e}")

        return None


class LoRaWANAdapter(SensorAdapter):
    """
    LoRaWAN Protocol Adapter - محول بروتوكول LoRaWAN
    For long-range, low-power sensors
    """

    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self._devices: dict[str, SoilSensor] = {}  # device_eui -> sensor

    async def connect(self) -> bool:
        """Connect to LoRaWAN network server"""
        try:
            # Connect to TTN, ChirpStack, or other LoRaWAN network server
            # This typically involves MQTT or HTTP integration
            self.connected = True
            return True
        except Exception as e:
            print(f"LoRaWAN connection failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect from LoRaWAN network server"""
        self.connected = False

    async def subscribe(self, sensor: SoilSensor):
        """Register device for uplink messages"""
        if sensor.device_eui:
            self._devices[sensor.device_eui] = sensor

    async def unsubscribe(self, sensor: SoilSensor):
        """Unregister device"""
        if sensor.device_eui and sensor.device_eui in self._devices:
            del self._devices[sensor.device_eui]

    def parse_payload(self, payload: bytes, sensor: SoilSensor) -> SensorReading | None:
        """
        Parse LoRaWAN payload (typically binary encoded)
        تحليل حمولة LoRaWAN (مشفرة بشكل ثنائي عادة)
        """
        try:
            # LoRaWAN payloads are often binary to minimize airtime
            # Common format: 2 bytes moisture (0-10000 = 0-100%), 1 byte battery, 1 byte flags

            if len(payload) >= 2:
                # Decode moisture (big-endian, scaled by 100)
                moisture_raw = int.from_bytes(payload[0:2], "big")
                moisture = moisture_raw / 100.0

                battery = None
                if len(payload) >= 3:
                    battery = payload[2]

                return SensorReading(
                    sensor_id=sensor.id,
                    timestamp=datetime.now(UTC),
                    reading_type=SensorType.MOISTURE,
                    value=moisture,
                    unit="%",
                    battery_percent=battery,
                    raw_value=moisture_raw,
                )

        except Exception as e:
            print(f"LoRaWAN payload parse error: {e}")

        return None


class HTTPAdapter(SensorAdapter):
    """
    HTTP Protocol Adapter - محول بروتوكول HTTP
    For sensors that push data via HTTP webhooks
    """

    def __init__(self, config: AdapterConfig):
        super().__init__(config)
        self._sensors: dict[str, SoilSensor] = {}

    async def connect(self) -> bool:
        """HTTP adapter is always connected (webhook receiver)"""
        self.connected = True
        return True

    async def disconnect(self):
        """No persistent connection to close"""
        self.connected = False

    async def subscribe(self, sensor: SoilSensor):
        """Register sensor for HTTP callbacks"""
        self._sensors[sensor.id] = sensor

    async def unsubscribe(self, sensor: SoilSensor):
        """Unregister sensor"""
        if sensor.id in self._sensors:
            del self._sensors[sensor.id]

    def parse_payload(self, payload: bytes, sensor: SoilSensor) -> SensorReading | None:
        """Parse HTTP webhook payload"""
        try:
            data = json.loads(payload.decode())

            # Handle various webhook formats

            # Sensoterra format
            if "sensor_id" in data and "volumetric_water_content" in data:
                return SensorReading(
                    sensor_id=sensor.id,
                    timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now(UTC).isoformat())),
                    reading_type=SensorType.MOISTURE,
                    value=float(data["volumetric_water_content"]) * 100,  # Convert to %
                    unit="%",
                    lat=data.get("latitude"),
                    lng=data.get("longitude"),
                    depth_cm=data.get("depth"),
                    battery_percent=data.get("battery_level"),
                )

            # Libelium format
            if "id" in data and "sensor" in data:
                sensor_data = data["sensor"]
                return SensorReading(
                    sensor_id=sensor.id,
                    timestamp=datetime.now(UTC),
                    reading_type=SensorType.MOISTURE,
                    value=float(sensor_data.get("value", 0)),
                    unit=sensor_data.get("unit", "%"),
                )

            # Generic format
            if "moisture" in data or "value" in data:
                return SensorReading(
                    sensor_id=sensor.id,
                    timestamp=datetime.now(UTC),
                    reading_type=SensorType.MOISTURE,
                    value=float(data.get("moisture", data.get("value", 0))),
                    unit="%",
                )

        except Exception as e:
            print(f"HTTP payload parse error: {e}")

        return None

    async def poll_sensor(self, sensor: SoilSensor) -> SensorReading | None:
        """
        Poll sensor via HTTP GET (for pull-based sensors)
        استطلاع المجس عبر HTTP GET
        """
        if not sensor.api_endpoint:
            return None

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    sensor.api_endpoint,
                    timeout=self.config.read_timeout,
                )
                response.raise_for_status()

                return self.parse_payload(response.content, sensor)

        except Exception as e:
            print(f"HTTP poll error for sensor {sensor.id}: {e}")
            return None


class NBIoTAdapter(SensorAdapter):
    """
    NB-IoT Protocol Adapter - محول بروتوكول NB-IoT
    For cellular IoT sensors
    """

    def __init__(self, config: AdapterConfig):
        super().__init__(config)

    async def connect(self) -> bool:
        """Connect to NB-IoT backend (typically via CoAP or HTTP)"""
        self.connected = True
        return True

    async def disconnect(self):
        self.connected = False

    async def subscribe(self, sensor: SoilSensor):
        """Register for NB-IoT device updates"""
        pass

    async def unsubscribe(self, sensor: SoilSensor):
        """Unregister from updates"""
        pass

    def parse_payload(self, payload: bytes, sensor: SoilSensor) -> SensorReading | None:
        """Parse NB-IoT payload (similar to LoRaWAN, often binary)"""
        return LoRaWANAdapter.parse_payload(self, payload, sensor)


def get_adapter(protocol: SensorProtocol, config: AdapterConfig) -> SensorAdapter:
    """
    Factory function to get appropriate adapter
    دالة مصنع للحصول على المحول المناسب
    """
    adapters = {
        SensorProtocol.MQTT: MQTTAdapter,
        SensorProtocol.LORAWAN: LoRaWANAdapter,
        SensorProtocol.HTTP: HTTPAdapter,
        SensorProtocol.NBIOT: NBIoTAdapter,
        SensorProtocol.CELLULAR: NBIoTAdapter,  # Similar handling
    }

    adapter_class = adapters.get(protocol, HTTPAdapter)
    return adapter_class(config)


class SensorManager:
    """
    Unified sensor manager for all protocols
    مدير مجسات موحد لجميع البروتوكولات
    """

    def __init__(self):
        self._adapters: dict[SensorProtocol, SensorAdapter] = {}
        self._sensors: dict[str, SoilSensor] = {}
        self._callbacks: list[Callable[[SensorReading], None]] = []

    async def add_adapter(self, protocol: SensorProtocol, config: AdapterConfig):
        """Add and connect an adapter"""
        adapter = get_adapter(protocol, config)
        await adapter.connect()
        adapter.on_reading(self._handle_reading)
        self._adapters[protocol] = adapter

    async def register_sensor(self, sensor: SoilSensor):
        """Register sensor with appropriate adapter"""
        self._sensors[sensor.id] = sensor

        adapter = self._adapters.get(sensor.protocol)
        if adapter:
            await adapter.subscribe(sensor)

    async def unregister_sensor(self, sensor_id: str):
        """Unregister sensor"""
        sensor = self._sensors.pop(sensor_id, None)
        if sensor:
            adapter = self._adapters.get(sensor.protocol)
            if adapter:
                await adapter.unsubscribe(sensor)

    def on_reading(self, callback: Callable[[SensorReading], None]):
        """Register callback for readings from any sensor"""
        self._callbacks.append(callback)

    def _handle_reading(self, reading: SensorReading):
        """Handle reading from any adapter"""
        for callback in self._callbacks:
            try:
                callback(reading)
            except Exception as e:
                print(f"Reading callback error: {e}")

    async def shutdown(self):
        """Disconnect all adapters"""
        for adapter in self._adapters.values():
            await adapter.disconnect()
        self._adapters.clear()
        self._sensors.clear()
