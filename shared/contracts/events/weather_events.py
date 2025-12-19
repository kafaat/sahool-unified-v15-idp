"""Weather Domain Events"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any, Dict, List, Optional
from uuid import UUID
from .base import BaseEvent


@dataclass
class WeatherForecastUpdatedEvent(BaseEvent):
    EVENT_TYPE = "weather.forecast_updated"
    EVENT_VERSION = "1.0.0"

    location_id: str = ""
    forecast_date: date = None
    temperature_min: float = 0.0
    temperature_max: float = 0.0
    precipitation_mm: float = 0.0
    humidity_percent: float = 0.0
    wind_speed_kmh: Optional[float] = None
    uv_index: Optional[int] = None
    conditions: Optional[str] = None

    def _payload_to_dict(self) -> Dict[str, Any]:
        return {
            "location_id": self.location_id,
            "forecast_date": self.forecast_date.isoformat() if self.forecast_date else None,
            "temperature_min": self.temperature_min,
            "temperature_max": self.temperature_max,
            "precipitation_mm": self.precipitation_mm,
            "humidity_percent": self.humidity_percent,
            "wind_speed_kmh": self.wind_speed_kmh,
            "uv_index": self.uv_index,
            "conditions": self.conditions,
        }


@dataclass
class WeatherAlertIssuedEvent(BaseEvent):
    EVENT_TYPE = "weather.alert_issued"
    EVENT_VERSION = "1.0.0"
    PRIORITY = "high"

    alert_id: UUID = None
    alert_type: str = ""
    severity: str = ""
    affected_regions: List[str] = field(default_factory=list)
    valid_from: datetime = None
    valid_until: datetime = None
    description: Optional[str] = None
    recommended_actions: Optional[List[str]] = None

    def _payload_to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": str(self.alert_id),
            "alert_type": self.alert_type,
            "severity": self.severity,
            "affected_regions": self.affected_regions,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "description": self.description,
            "recommended_actions": self.recommended_actions,
        }
