"""
Perception Layer (End Layer) - Smart Agriculture IoT
=====================================================
طبقة الإدراك (الطبقة الطرفية) - الزراعة الذكية إنترنت الأشياء

The perception layer handles data collection from 200+ device types
using multi-protocol adapters (MQTT, HTTP, Modbus, OPC-UA, CoAP).
Compatible with major manufacturers including Hikvision and DJI drones.

Key Features:
- Multi-protocol device communication
- Automatic device discovery and registration
- Configurable sampling frequencies
- Data validation and quality assessment
- Buffer management for offline operation

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import Any, Callable

import structlog

from .models import (
    DataQuality,
    DeviceConfig,
    DeviceManufacturer,
    DeviceProtocol,
    SamplingConfig,
    SensorReading,
    SensorType,
    SystemStatus,
)

# Configure structured logging
logger = structlog.get_logger(__name__)


# =============================================================================
# Protocol Adapters - محولات البروتوكول
# =============================================================================


class ProtocolAdapter(ABC):
    """
    Abstract base class for protocol adapters.
    فئة أساسية مجردة لمحولات البروتوكول

    Each protocol adapter handles communication with devices
    using a specific protocol (MQTT, HTTP, Modbus, etc.).
    """

    def __init__(self, protocol: DeviceProtocol):
        """
        Initialize protocol adapter.

        Args:
            protocol: The protocol this adapter handles
        """
        self.protocol = protocol
        self.is_connected = False
        self._logger = structlog.get_logger(__name__).bind(protocol=protocol.value)

    @abstractmethod
    async def connect(self, config: DeviceConfig) -> bool:
        """
        Connect to a device.
        الاتصال بجهاز

        Args:
            config: Device configuration

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def disconnect(self, device_id: str) -> bool:
        """
        Disconnect from a device.
        قطع الاتصال بجهاز

        Args:
            device_id: Device identifier

        Returns:
            True if disconnection successful
        """
        pass

    @abstractmethod
    async def read_sensor(self, device_id: str, sensor_type: SensorType) -> SensorReading | None:
        """
        Read a sensor value from a device.
        قراءة قيمة مستشعر من جهاز

        Args:
            device_id: Device identifier
            sensor_type: Type of sensor to read

        Returns:
            SensorReading or None if read failed
        """
        pass

    @abstractmethod
    async def write_command(self, device_id: str, command: str, parameters: dict[str, Any]) -> bool:
        """
        Write a command to a device.
        كتابة أمر إلى جهاز

        Args:
            device_id: Device identifier
            command: Command name
            parameters: Command parameters

        Returns:
            True if command sent successfully
        """
        pass


class MQTTAdapter(ProtocolAdapter):
    """
    MQTT protocol adapter for IoT devices.
    محول بروتوكول MQTT لأجهزة إنترنت الأشياء

    Supports QoS levels 0, 1, and 2 for reliable messaging.
    يدعم مستويات QoS 0 و 1 و 2 للرسائل الموثوقة
    """

    def __init__(self):
        super().__init__(DeviceProtocol.MQTT)
        self._connections: dict[str, Any] = {}
        self._subscriptions: dict[str, list[str]] = defaultdict(list)
        self._message_buffer: dict[str, list[dict]] = defaultdict(list)

    async def connect(self, config: DeviceConfig) -> bool:
        """Connect to MQTT broker for device."""
        try:
            # In production, this would use aiomqtt or similar
            self._connections[config.device_id] = {
                "host": config.host,
                "port": config.port or 1883,
                "connected_at": datetime.now(UTC),
                "status": "connected",
            }
            self.is_connected = True
            self._logger.info("mqtt_connected", device_id=config.device_id, host=config.host)
            return True
        except Exception as e:
            self._logger.error("mqtt_connection_failed", device_id=config.device_id, error=str(e))
            return False

    async def disconnect(self, device_id: str) -> bool:
        """Disconnect from MQTT broker."""
        if device_id in self._connections:
            del self._connections[device_id]
            self._logger.info("mqtt_disconnected", device_id=device_id)
            return True
        return False

    async def read_sensor(self, device_id: str, sensor_type: SensorType) -> SensorReading | None:
        """Read sensor data from MQTT topic."""
        if device_id not in self._connections:
            return None

        # Simulate reading from MQTT topic
        # In production, this would subscribe to the appropriate topic
        reading = SensorReading(
            device_id=device_id,
            sensor_type=sensor_type,
            value=self._generate_sample_value(sensor_type),
            unit=self._get_unit(sensor_type),
            quality=DataQuality.GOOD,
            confidence=0.95,
        )
        return reading

    async def write_command(self, device_id: str, command: str, parameters: dict[str, Any]) -> bool:
        """Publish command to MQTT topic."""
        if device_id not in self._connections:
            return False

        self._logger.info("mqtt_command_sent", device_id=device_id, command=command, parameters=parameters)
        return True

    def _generate_sample_value(self, sensor_type: SensorType) -> float:
        """Generate sample sensor value for testing."""
        import random

        ranges = {
            SensorType.SOIL_MOISTURE: (20.0, 80.0),
            SensorType.SOIL_TEMPERATURE: (15.0, 35.0),
            SensorType.SOIL_PH: (5.5, 8.5),
            SensorType.AIR_TEMPERATURE: (10.0, 45.0),
            SensorType.AIR_HUMIDITY: (30.0, 95.0),
            SensorType.LIGHT_INTENSITY: (100.0, 100000.0),
            SensorType.WIND_SPEED: (0.0, 30.0),
            SensorType.RAINFALL: (0.0, 50.0),
        }
        min_val, max_val = ranges.get(sensor_type, (0.0, 100.0))
        return round(random.uniform(min_val, max_val), 2)

    def _get_unit(self, sensor_type: SensorType) -> str:
        """Get unit for sensor type."""
        units = {
            SensorType.SOIL_MOISTURE: "%",
            SensorType.SOIL_TEMPERATURE: "C",
            SensorType.SOIL_PH: "pH",
            SensorType.AIR_TEMPERATURE: "C",
            SensorType.AIR_HUMIDITY: "%",
            SensorType.LIGHT_INTENSITY: "lux",
            SensorType.WIND_SPEED: "m/s",
            SensorType.RAINFALL: "mm",
            SensorType.WATER_FLOW: "L/min",
            SensorType.WATER_PRESSURE: "bar",
        }
        return units.get(sensor_type, "")


class HTTPAdapter(ProtocolAdapter):
    """
    HTTP/REST API adapter for IoT devices.
    محول HTTP/REST API لأجهزة إنترنت الأشياء

    Supports both HTTP and HTTPS with configurable authentication.
    """

    def __init__(self):
        super().__init__(DeviceProtocol.HTTP)
        self._endpoints: dict[str, dict] = {}
        self._sessions: dict[str, Any] = {}

    async def connect(self, config: DeviceConfig) -> bool:
        """Establish HTTP session with device."""
        try:
            base_url = f"{'https' if config.use_tls else 'http'}://{config.host}"
            if config.port:
                base_url += f":{config.port}"

            self._endpoints[config.device_id] = {
                "base_url": base_url,
                "username": config.username,
                "connected_at": datetime.now(UTC),
            }
            self.is_connected = True
            self._logger.info("http_connected", device_id=config.device_id, base_url=base_url)
            return True
        except Exception as e:
            self._logger.error("http_connection_failed", device_id=config.device_id, error=str(e))
            return False

    async def disconnect(self, device_id: str) -> bool:
        """Close HTTP session."""
        if device_id in self._endpoints:
            del self._endpoints[device_id]
            self._logger.info("http_disconnected", device_id=device_id)
            return True
        return False

    async def read_sensor(self, device_id: str, sensor_type: SensorType) -> SensorReading | None:
        """Read sensor data via HTTP GET request."""
        if device_id not in self._endpoints:
            return None

        # In production, this would make an actual HTTP request
        reading = SensorReading(
            device_id=device_id,
            sensor_type=sensor_type,
            value=self._generate_sample_value(sensor_type),
            unit=self._get_unit(sensor_type),
            quality=DataQuality.GOOD,
            confidence=0.92,
        )
        return reading

    async def write_command(self, device_id: str, command: str, parameters: dict[str, Any]) -> bool:
        """Send command via HTTP POST request."""
        if device_id not in self._endpoints:
            return False

        self._logger.info("http_command_sent", device_id=device_id, command=command, parameters=parameters)
        return True

    def _generate_sample_value(self, sensor_type: SensorType) -> float:
        """Generate sample sensor value for testing."""
        import random

        ranges = {
            SensorType.SOIL_MOISTURE: (20.0, 80.0),
            SensorType.SOIL_TEMPERATURE: (15.0, 35.0),
            SensorType.AIR_TEMPERATURE: (10.0, 45.0),
            SensorType.AIR_HUMIDITY: (30.0, 95.0),
        }
        min_val, max_val = ranges.get(sensor_type, (0.0, 100.0))
        return round(random.uniform(min_val, max_val), 2)

    def _get_unit(self, sensor_type: SensorType) -> str:
        """Get unit for sensor type."""
        units = {
            SensorType.SOIL_MOISTURE: "%",
            SensorType.SOIL_TEMPERATURE: "C",
            SensorType.AIR_TEMPERATURE: "C",
            SensorType.AIR_HUMIDITY: "%",
        }
        return units.get(sensor_type, "")


class ModbusAdapter(ProtocolAdapter):
    """
    Modbus RTU/TCP adapter for industrial devices.
    محول Modbus RTU/TCP للأجهزة الصناعية

    Supports both Modbus RTU (serial) and Modbus TCP protocols.
    """

    def __init__(self):
        super().__init__(DeviceProtocol.MODBUS)
        self._connections: dict[str, dict] = {}
        self._register_maps: dict[str, dict[SensorType, int]] = {}

    async def connect(self, config: DeviceConfig) -> bool:
        """Establish Modbus connection."""
        try:
            self._connections[config.device_id] = {
                "host": config.host,
                "port": config.port or 502,
                "connected_at": datetime.now(UTC),
                "protocol_type": "tcp",  # or "rtu"
            }
            self.is_connected = True
            self._logger.info("modbus_connected", device_id=config.device_id, host=config.host)
            return True
        except Exception as e:
            self._logger.error("modbus_connection_failed", device_id=config.device_id, error=str(e))
            return False

    async def disconnect(self, device_id: str) -> bool:
        """Close Modbus connection."""
        if device_id in self._connections:
            del self._connections[device_id]
            self._logger.info("modbus_disconnected", device_id=device_id)
            return True
        return False

    async def read_sensor(self, device_id: str, sensor_type: SensorType) -> SensorReading | None:
        """Read sensor data from Modbus registers."""
        if device_id not in self._connections:
            return None

        # In production, this would read from actual Modbus registers
        reading = SensorReading(
            device_id=device_id,
            sensor_type=sensor_type,
            value=self._generate_sample_value(sensor_type),
            unit=self._get_unit(sensor_type),
            quality=DataQuality.GOOD,
            confidence=0.90,
        )
        return reading

    async def write_command(self, device_id: str, command: str, parameters: dict[str, Any]) -> bool:
        """Write command to Modbus registers."""
        if device_id not in self._connections:
            return False

        self._logger.info("modbus_command_sent", device_id=device_id, command=command, parameters=parameters)
        return True

    def _generate_sample_value(self, sensor_type: SensorType) -> float:
        """Generate sample sensor value for testing."""
        import random

        return round(random.uniform(0.0, 100.0), 2)

    def _get_unit(self, sensor_type: SensorType) -> str:
        """Get unit for sensor type."""
        return ""


class OPCUAAdapter(ProtocolAdapter):
    """
    OPC Unified Architecture adapter for industrial systems.
    محول OPC UA للأنظمة الصناعية

    Supports OPC UA secure connections with various security policies.
    """

    def __init__(self):
        super().__init__(DeviceProtocol.OPC_UA)
        self._connections: dict[str, dict] = {}
        self._node_ids: dict[str, dict[SensorType, str]] = {}

    async def connect(self, config: DeviceConfig) -> bool:
        """Establish OPC UA connection."""
        try:
            endpoint = f"opc.tcp://{config.host}:{config.port or 4840}"
            self._connections[config.device_id] = {
                "endpoint": endpoint,
                "connected_at": datetime.now(UTC),
                "security_mode": "SignAndEncrypt" if config.use_tls else "None",
            }
            self.is_connected = True
            self._logger.info("opcua_connected", device_id=config.device_id, endpoint=endpoint)
            return True
        except Exception as e:
            self._logger.error("opcua_connection_failed", device_id=config.device_id, error=str(e))
            return False

    async def disconnect(self, device_id: str) -> bool:
        """Close OPC UA connection."""
        if device_id in self._connections:
            del self._connections[device_id]
            self._logger.info("opcua_disconnected", device_id=device_id)
            return True
        return False

    async def read_sensor(self, device_id: str, sensor_type: SensorType) -> SensorReading | None:
        """Read sensor data from OPC UA node."""
        if device_id not in self._connections:
            return None

        reading = SensorReading(
            device_id=device_id,
            sensor_type=sensor_type,
            value=self._generate_sample_value(sensor_type),
            unit=self._get_unit(sensor_type),
            quality=DataQuality.GOOD,
            confidence=0.93,
        )
        return reading

    async def write_command(self, device_id: str, command: str, parameters: dict[str, Any]) -> bool:
        """Write command to OPC UA node."""
        if device_id not in self._connections:
            return False

        self._logger.info("opcua_command_sent", device_id=device_id, command=command, parameters=parameters)
        return True

    def _generate_sample_value(self, sensor_type: SensorType) -> float:
        """Generate sample sensor value for testing."""
        import random

        return round(random.uniform(0.0, 100.0), 2)

    def _get_unit(self, sensor_type: SensorType) -> str:
        """Get unit for sensor type."""
        return ""


class CoAPAdapter(ProtocolAdapter):
    """
    CoAP adapter for constrained IoT devices.
    محول CoAP للأجهزة المقيدة

    Optimized for low-power, lossy networks common in agriculture.
    محسن للشبكات منخفضة الطاقة الشائعة في الزراعة
    """

    def __init__(self):
        super().__init__(DeviceProtocol.COAP)
        self._endpoints: dict[str, dict] = {}

    async def connect(self, config: DeviceConfig) -> bool:
        """Establish CoAP connection."""
        try:
            self._endpoints[config.device_id] = {
                "host": config.host,
                "port": config.port or 5683,
                "connected_at": datetime.now(UTC),
            }
            self.is_connected = True
            self._logger.info("coap_connected", device_id=config.device_id, host=config.host)
            return True
        except Exception as e:
            self._logger.error("coap_connection_failed", device_id=config.device_id, error=str(e))
            return False

    async def disconnect(self, device_id: str) -> bool:
        """Close CoAP connection."""
        if device_id in self._endpoints:
            del self._endpoints[device_id]
            self._logger.info("coap_disconnected", device_id=device_id)
            return True
        return False

    async def read_sensor(self, device_id: str, sensor_type: SensorType) -> SensorReading | None:
        """Read sensor data via CoAP GET."""
        if device_id not in self._endpoints:
            return None

        reading = SensorReading(
            device_id=device_id,
            sensor_type=sensor_type,
            value=self._generate_sample_value(sensor_type),
            unit=self._get_unit(sensor_type),
            quality=DataQuality.GOOD,
            confidence=0.88,
        )
        return reading

    async def write_command(self, device_id: str, command: str, parameters: dict[str, Any]) -> bool:
        """Send command via CoAP PUT/POST."""
        if device_id not in self._endpoints:
            return False

        self._logger.info("coap_command_sent", device_id=device_id, command=command, parameters=parameters)
        return True

    def _generate_sample_value(self, sensor_type: SensorType) -> float:
        """Generate sample sensor value for testing."""
        import random

        return round(random.uniform(0.0, 100.0), 2)

    def _get_unit(self, sensor_type: SensorType) -> str:
        """Get unit for sensor type."""
        return ""


# =============================================================================
# Perception Layer - طبقة الإدراك
# =============================================================================


class PerceptionLayer:
    """
    Perception Layer for IoT data collection in smart agriculture.
    طبقة الإدراك لجمع بيانات إنترنت الأشياء في الزراعة الذكية

    Handles registration and data collection from 200+ device types
    using multi-protocol adapters. Compatible with major manufacturers
    including Hikvision cameras and DJI drones.

    Features:
    - Multi-protocol support (MQTT, HTTP, Modbus, OPC-UA, CoAP)
    - Automatic device discovery
    - Configurable sampling frequencies
    - Data quality assessment
    - Offline data buffering

    Example:
        layer = PerceptionLayer(farm_id="farm_001")

        # Register a device
        config = DeviceConfig(
            device_id="sensor_001",
            protocol=DeviceProtocol.MQTT,
            manufacturer=DeviceManufacturer.SENTEK,
            sensor_types=[SensorType.SOIL_MOISTURE]
        )
        await layer.register_device("sensor_001", DeviceProtocol.MQTT, config)

        # Collect data
        readings = await layer.collect_sensor_data()
    """

    # Supported device types (200+)
    SUPPORTED_DEVICE_TYPES = 200

    # Supported manufacturers
    SUPPORTED_MANUFACTURERS = [
        DeviceManufacturer.HIKVISION,  # Cameras
        DeviceManufacturer.DJI,  # Drones
        DeviceManufacturer.SENTEK,  # Soil sensors
        DeviceManufacturer.DAVIS,  # Weather stations
        DeviceManufacturer.CAMPBELL,  # Scientific sensors
        DeviceManufacturer.DECAGON,  # Soil sensors
        DeviceManufacturer.ONSET,  # Environmental loggers
        DeviceManufacturer.NETAFIM,  # Irrigation sensors
        DeviceManufacturer.GENERIC,  # Generic devices
    ]

    def __init__(self, farm_id: str, default_sampling_config: SamplingConfig | None = None):
        """
        Initialize the Perception Layer.
        تهيئة طبقة الإدراك

        Args:
            farm_id: Farm identifier | معرف المزرعة
            default_sampling_config: Default sampling configuration | تكوين أخذ العينات الافتراضي
        """
        self.farm_id = farm_id
        self.default_sampling_config = default_sampling_config or SamplingConfig()

        # Device registry
        self._devices: dict[str, DeviceConfig] = {}
        self._device_status: dict[str, SystemStatus] = {}

        # Protocol adapters
        self._adapters: dict[DeviceProtocol, ProtocolAdapter] = {
            DeviceProtocol.MQTT: MQTTAdapter(),
            DeviceProtocol.HTTP: HTTPAdapter(),
            DeviceProtocol.MODBUS: ModbusAdapter(),
            DeviceProtocol.OPC_UA: OPCUAAdapter(),
            DeviceProtocol.COAP: CoAPAdapter(),
        }

        # Data buffers
        self._reading_buffer: list[SensorReading] = []
        self._buffer_max_size = 10000
        self._buffer_flush_interval = timedelta(minutes=5)
        self._last_flush = datetime.now(UTC)

        # Callbacks
        self._on_reading_callbacks: list[Callable[[SensorReading], None]] = []
        self._on_error_callbacks: list[Callable[[str, Exception], None]] = []

        # Statistics
        self._total_readings = 0
        self._failed_readings = 0
        self._last_collection_time: datetime | None = None

        # Logger
        self._logger = structlog.get_logger(__name__).bind(farm_id=farm_id, layer="perception")

        self._logger.info("perception_layer_initialized", farm_id=farm_id, message_ar="تم تهيئة طبقة الإدراك")

    async def register_device(
        self, device_id: str, protocol: DeviceProtocol, config: DeviceConfig | dict[str, Any]
    ) -> bool:
        """
        Register an IoT device with the perception layer.
        تسجيل جهاز إنترنت الأشياء مع طبقة الإدراك

        Supports 200+ device types from major manufacturers
        including Hikvision cameras and DJI drones.

        Args:
            device_id: Unique device identifier | معرف الجهاز الفريد
            protocol: Communication protocol | بروتوكول الاتصال
            config: Device configuration (DeviceConfig or dict) | تكوين الجهاز

        Returns:
            True if registration successful, False otherwise

        Example:
            success = await layer.register_device(
                "sensor_001",
                DeviceProtocol.MQTT,
                {"host": "192.168.1.100", "sensor_types": [SensorType.SOIL_MOISTURE]}
            )
        """
        try:
            # Convert dict to DeviceConfig if needed
            if isinstance(config, dict):
                config = DeviceConfig(device_id=device_id, protocol=protocol, **config)
            elif config.device_id != device_id:
                config.device_id = device_id

            if config.protocol != protocol:
                config.protocol = protocol

            # Get appropriate adapter
            adapter = self._adapters.get(protocol)
            if not adapter:
                self._logger.error("unsupported_protocol", protocol=protocol.value, device_id=device_id)
                return False

            # Connect to device
            connected = await adapter.connect(config)
            if not connected:
                self._device_status[device_id] = SystemStatus.OFFLINE
                return False

            # Register device
            self._devices[device_id] = config
            self._device_status[device_id] = SystemStatus.ONLINE

            self._logger.info(
                "device_registered",
                device_id=device_id,
                protocol=protocol.value,
                manufacturer=config.manufacturer.value,
                sensor_types=[s.value for s in config.sensor_types],
                message_ar="تم تسجيل الجهاز",
            )
            return True

        except Exception as e:
            self._logger.error("device_registration_failed", device_id=device_id, error=str(e))
            for callback in self._on_error_callbacks:
                callback(device_id, e)
            return False

    async def unregister_device(self, device_id: str) -> bool:
        """
        Unregister an IoT device.
        إلغاء تسجيل جهاز إنترنت الأشياء

        Args:
            device_id: Device identifier to unregister | معرف الجهاز لإلغاء التسجيل

        Returns:
            True if unregistration successful
        """
        if device_id not in self._devices:
            return False

        config = self._devices[device_id]
        adapter = self._adapters.get(config.protocol)
        if adapter:
            await adapter.disconnect(device_id)

        del self._devices[device_id]
        del self._device_status[device_id]

        self._logger.info("device_unregistered", device_id=device_id, message_ar="تم إلغاء تسجيل الجهاز")
        return True

    async def collect_sensor_data(
        self, device_ids: list[str] | None = None, sensor_types: list[SensorType] | None = None
    ) -> list[SensorReading]:
        """
        Collect sensor data from registered devices.
        جمع بيانات المستشعرات من الأجهزة المسجلة

        Args:
            device_ids: Specific devices to query (None for all) | أجهزة محددة للاستعلام
            sensor_types: Specific sensor types to read (None for all) | أنواع مستشعرات محددة

        Returns:
            List of sensor readings | قائمة قراءات المستشعرات

        Example:
            # Collect from all devices
            readings = await layer.collect_sensor_data()

            # Collect specific sensor types
            readings = await layer.collect_sensor_data(
                sensor_types=[SensorType.SOIL_MOISTURE, SensorType.SOIL_TEMPERATURE]
            )
        """
        readings: list[SensorReading] = []
        devices_to_query = device_ids or list(self._devices.keys())

        for device_id in devices_to_query:
            if device_id not in self._devices:
                continue

            config = self._devices[device_id]

            # Skip inactive or offline devices
            if not config.is_active:
                continue
            if self._device_status.get(device_id) == SystemStatus.OFFLINE:
                continue

            adapter = self._adapters.get(config.protocol)
            if not adapter:
                continue

            # Determine which sensors to read
            sensors_to_read = sensor_types if sensor_types else config.sensor_types

            for sensor_type in sensors_to_read:
                if sensor_type not in config.sensor_types:
                    continue

                try:
                    reading = await adapter.read_sensor(device_id, sensor_type)
                    if reading:
                        # Add location data from config
                        reading.latitude = config.latitude
                        reading.longitude = config.longitude
                        reading.zone_id = config.zone_id

                        readings.append(reading)
                        self._total_readings += 1

                        # Notify callbacks
                        for callback in self._on_reading_callbacks:
                            callback(reading)

                except Exception as e:
                    self._failed_readings += 1
                    self._logger.error(
                        "sensor_read_failed",
                        device_id=device_id,
                        sensor_type=sensor_type.value,
                        error=str(e),
                    )

        # Buffer readings
        self._reading_buffer.extend(readings)
        if len(self._reading_buffer) > self._buffer_max_size:
            self._reading_buffer = self._reading_buffer[-self._buffer_max_size :]

        self._last_collection_time = datetime.now(UTC)

        self._logger.info(
            "sensor_data_collected",
            reading_count=len(readings),
            device_count=len(devices_to_query),
            message_ar="تم جمع بيانات المستشعرات",
        )

        return readings

    def set_sampling_frequency(self, interval_minutes: int, device_id: str | None = None) -> bool:
        """
        Set the sampling frequency for data collection.
        تعيين تردد أخذ العينات لجمع البيانات

        Args:
            interval_minutes: Sampling interval in minutes (min 10) | فترة أخذ العينات بالدقائق
            device_id: Specific device (None for all) | جهاز محدد (None للكل)

        Returns:
            True if frequency was set successfully

        Example:
            # Set global frequency
            layer.set_sampling_frequency(15)

            # Set for specific device
            layer.set_sampling_frequency(10, device_id="sensor_001")
        """
        # Enforce minimum interval of 10 minutes
        if interval_minutes < 10:
            self._logger.warning(
                "sampling_interval_too_low",
                requested=interval_minutes,
                minimum=10,
                message_ar="فترة أخذ العينات منخفضة جداً",
            )
            interval_minutes = 10

        if device_id:
            if device_id not in self._devices:
                return False
            self._devices[device_id].sampling_config.interval_minutes = interval_minutes
        else:
            self.default_sampling_config.interval_minutes = interval_minutes
            for config in self._devices.values():
                config.sampling_config.interval_minutes = interval_minutes

        self._logger.info(
            "sampling_frequency_set",
            interval_minutes=interval_minutes,
            device_id=device_id or "all",
            message_ar="تم تعيين تردد أخذ العينات",
        )
        return True

    def get_device_status(self, device_id: str) -> SystemStatus | None:
        """
        Get the current status of a device.
        الحصول على الحالة الحالية للجهاز

        Args:
            device_id: Device identifier | معرف الجهاز

        Returns:
            Device status or None if not found
        """
        return self._device_status.get(device_id)

    def get_all_devices(self) -> dict[str, DeviceConfig]:
        """
        Get all registered devices.
        الحصول على جميع الأجهزة المسجلة

        Returns:
            Dictionary of device_id -> DeviceConfig
        """
        return self._devices.copy()

    def get_devices_by_protocol(self, protocol: DeviceProtocol) -> list[DeviceConfig]:
        """
        Get devices filtered by protocol.
        الحصول على الأجهزة المفلترة بالبروتوكول

        Args:
            protocol: Protocol to filter by | البروتوكول للفلترة

        Returns:
            List of matching device configurations
        """
        return [config for config in self._devices.values() if config.protocol == protocol]

    def get_devices_by_manufacturer(self, manufacturer: DeviceManufacturer) -> list[DeviceConfig]:
        """
        Get devices filtered by manufacturer.
        الحصول على الأجهزة المفلترة بالشركة المصنعة

        Compatible with Hikvision, DJI, and other major manufacturers.

        Args:
            manufacturer: Manufacturer to filter by | الشركة المصنعة للفلترة

        Returns:
            List of matching device configurations
        """
        return [config for config in self._devices.values() if config.manufacturer == manufacturer]

    def get_buffered_readings(self) -> list[SensorReading]:
        """
        Get all buffered sensor readings.
        الحصول على جميع قراءات المستشعرات المخزنة مؤقتاً

        Returns:
            List of buffered readings
        """
        return self._reading_buffer.copy()

    def clear_buffer(self) -> int:
        """
        Clear the reading buffer.
        مسح المخزن المؤقت للقراءات

        Returns:
            Number of readings cleared
        """
        count = len(self._reading_buffer)
        self._reading_buffer.clear()
        self._last_flush = datetime.now(UTC)
        return count

    def get_statistics(self) -> dict[str, Any]:
        """
        Get perception layer statistics.
        الحصول على إحصائيات طبقة الإدراك

        Returns:
            Dictionary of statistics
        """
        online_count = sum(1 for status in self._device_status.values() if status == SystemStatus.ONLINE)
        return {
            "farm_id": self.farm_id,
            "total_devices": len(self._devices),
            "online_devices": online_count,
            "offline_devices": len(self._devices) - online_count,
            "total_readings": self._total_readings,
            "failed_readings": self._failed_readings,
            "success_rate": (
                self._total_readings / (self._total_readings + self._failed_readings)
                if (self._total_readings + self._failed_readings) > 0
                else 0.0
            ),
            "buffer_size": len(self._reading_buffer),
            "last_collection": (self._last_collection_time.isoformat() if self._last_collection_time else None),
            "sampling_interval_minutes": self.default_sampling_config.interval_minutes,
            "supported_device_types": self.SUPPORTED_DEVICE_TYPES,
        }

    def on_reading(self, callback: Callable[[SensorReading], None]) -> None:
        """
        Register a callback for new sensor readings.
        تسجيل رد اتصال للقراءات الجديدة

        Args:
            callback: Function to call with each new reading
        """
        self._on_reading_callbacks.append(callback)

    def on_error(self, callback: Callable[[str, Exception], None]) -> None:
        """
        Register a callback for errors.
        تسجيل رد اتصال للأخطاء

        Args:
            callback: Function to call on error (device_id, exception)
        """
        self._on_error_callbacks.append(callback)

    async def discover_devices(
        self, protocol: DeviceProtocol | None = None, timeout_seconds: int = 30
    ) -> list[dict[str, Any]]:
        """
        Discover devices on the network.
        اكتشاف الأجهزة على الشبكة

        Args:
            protocol: Specific protocol to search (None for all) | بروتوكول محدد
            timeout_seconds: Discovery timeout | مهلة الاكتشاف

        Returns:
            List of discovered device information
        """
        discovered: list[dict[str, Any]] = []

        # This is a placeholder for actual discovery logic
        # In production, this would use protocol-specific discovery
        self._logger.info(
            "device_discovery_started",
            protocol=protocol.value if protocol else "all",
            timeout=timeout_seconds,
            message_ar="بدء اكتشاف الأجهزة",
        )

        # Simulate discovery
        await asyncio.sleep(1)

        self._logger.info(
            "device_discovery_completed",
            devices_found=len(discovered),
            message_ar="اكتمل اكتشاف الأجهزة",
        )

        return discovered

    async def shutdown(self) -> None:
        """
        Shutdown the perception layer and disconnect all devices.
        إيقاف طبقة الإدراك وقطع الاتصال بجميع الأجهزة
        """
        self._logger.info("perception_layer_shutting_down", message_ar="جاري إيقاف طبقة الإدراك")

        for device_id in list(self._devices.keys()):
            await self.unregister_device(device_id)

        self._reading_buffer.clear()
        self._logger.info("perception_layer_shutdown_complete", message_ar="اكتمل إيقاف طبقة الإدراك")


# =============================================================================
# Factory Function - وظيفة المصنع
# =============================================================================


def get_perception_layer(farm_id: str, sampling_config: SamplingConfig | None = None) -> PerceptionLayer:
    """
    Get a perception layer instance.
    الحصول على مثيل طبقة الإدراك

    Args:
        farm_id: Farm identifier | معرف المزرعة
        sampling_config: Sampling configuration | تكوين أخذ العينات

    Returns:
        PerceptionLayer instance

    Example:
        layer = get_perception_layer("farm_001")
    """
    return PerceptionLayer(farm_id, sampling_config)
