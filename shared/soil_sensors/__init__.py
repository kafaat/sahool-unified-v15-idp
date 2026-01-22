"""
SAHOOL Soil Sensors Module - وحدة مجسات التربة
IoT sensor integration for soil moisture and health monitoring

Features:
- Multi-protocol support (MQTT, LoRaWAN, HTTP)
- Sensor data normalization
- Alert generation on thresholds
- Historical data aggregation

Version: 1.0.0
"""

from .models import (
    SensorType,
    SensorProtocol,
    SensorReading,
    SoilSensor,
    SensorAlert,
    SensorCalibration,
    SensorStatus,
)
from .adapters import (
    SensorAdapter,
    MQTTAdapter,
    LoRaWANAdapter,
    HTTPAdapter,
    get_adapter,
)
from .processor import (
    SensorDataProcessor,
    aggregate_readings,
    detect_anomalies,
    interpolate_field_moisture,
)

__all__ = [
    # Models
    "SensorType",
    "SensorProtocol",
    "SensorReading",
    "SoilSensor",
    "SensorAlert",
    "SensorCalibration",
    "SensorStatus",
    # Adapters
    "SensorAdapter",
    "MQTTAdapter",
    "LoRaWANAdapter",
    "HTTPAdapter",
    "get_adapter",
    # Processor
    "SensorDataProcessor",
    "aggregate_readings",
    "detect_anomalies",
    "interpolate_field_moisture",
]
