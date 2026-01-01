"""IoT Domain Events"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID
from .base import BaseEvent


@dataclass
class SensorReadingEvent(BaseEvent):
    EVENT_TYPE = "iot.sensor_reading"
    EVENT_VERSION = "1.0.0"

    sensor_id: UUID = None
    field_id: UUID = None
    reading_type: str = ""
    value: float = 0.0
    unit: str = ""
    reading_timestamp: datetime = None
    battery_level: Optional[float] = None
    signal_strength: Optional[int] = None

    def _payload_to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": str(self.sensor_id),
            "field_id": str(self.field_id),
            "reading_type": self.reading_type,
            "value": self.value,
            "unit": self.unit,
            "timestamp": (
                self.reading_timestamp.isoformat() if self.reading_timestamp else None
            ),
            "battery_level": self.battery_level,
            "signal_strength": self.signal_strength,
        }


@dataclass
class SensorAlertEvent(BaseEvent):
    EVENT_TYPE = "iot.sensor_alert"
    EVENT_VERSION = "1.0.0"
    PRIORITY = "high"

    sensor_id: UUID = None
    alert_type: str = ""
    threshold_value: float = 0.0
    actual_value: float = 0.0
    alert_timestamp: datetime = None

    def _payload_to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": str(self.sensor_id),
            "alert_type": self.alert_type,
            "threshold_value": self.threshold_value,
            "actual_value": self.actual_value,
            "timestamp": (
                self.alert_timestamp.isoformat() if self.alert_timestamp else None
            ),
        }
