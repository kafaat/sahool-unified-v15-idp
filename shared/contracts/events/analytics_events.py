"""Analytics Domain Events"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from uuid import UUID

from .base import BaseEvent


@dataclass
class NDVICalculatedEvent(BaseEvent):
    EVENT_TYPE = "analytics.ndvi_calculated"
    EVENT_VERSION = "1.0.0"

    field_id: UUID = None
    ndvi_value: float = 0.0
    satellite_source: str = ""
    acquisition_date: date = None
    calculation_date: datetime = None
    cloud_cover_percent: float | None = None
    quality_flag: str | None = None

    def _payload_to_dict(self) -> dict[str, Any]:
        return {
            "field_id": str(self.field_id),
            "ndvi_value": self.ndvi_value,
            "satellite_source": self.satellite_source,
            "acquisition_date": (
                self.acquisition_date.isoformat() if self.acquisition_date else None
            ),
            "calculation_date": (
                self.calculation_date.isoformat() if self.calculation_date else None
            ),
            "cloud_cover_percent": self.cloud_cover_percent,
            "quality_flag": self.quality_flag,
        }


@dataclass
class YieldPredictedEvent(BaseEvent):
    EVENT_TYPE = "analytics.yield_predicted"
    EVENT_VERSION = "1.0.0"

    field_id: UUID = None
    crop_id: UUID = None
    predicted_yield_kg: float = 0.0
    confidence_interval_low: float = 0.0
    confidence_interval_high: float = 0.0
    prediction_date: datetime = None
    model_version: str | None = None
    factors_considered: list | None = None

    def _payload_to_dict(self) -> dict[str, Any]:
        return {
            "field_id": str(self.field_id),
            "crop_id": str(self.crop_id) if self.crop_id else None,
            "predicted_yield_kg": self.predicted_yield_kg,
            "confidence_interval_low": self.confidence_interval_low,
            "confidence_interval_high": self.confidence_interval_high,
            "prediction_date": (
                self.prediction_date.isoformat() if self.prediction_date else None
            ),
            "model_version": self.model_version,
            "factors_considered": self.factors_considered,
        }
