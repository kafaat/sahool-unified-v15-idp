"""
SAHOOL Context Models
Data models for AI context
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


@dataclass
class WeatherContext:
    """Weather information for context"""

    temperature_c: float
    humidity_percent: float
    precipitation_mm: float
    wind_speed_kmh: float
    conditions: str
    forecast_days: int = 7
    forecast_data: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "temperature_c": self.temperature_c,
            "humidity_percent": self.humidity_percent,
            "precipitation_mm": self.precipitation_mm,
            "wind_speed_kmh": self.wind_speed_kmh,
            "conditions": self.conditions,
            "forecast_days": self.forecast_days,
            "forecast_data": self.forecast_data,
        }


@dataclass
class HistoricalContext:
    """Historical data for context"""

    previous_crops: list[str]
    average_yield_kg_per_hectare: Optional[float]
    common_issues: list[str]
    successful_practices: list[str]
    last_soil_test_date: Optional[date]
    soil_test_results: Optional[dict]

    def to_dict(self) -> dict:
        return {
            "previous_crops": self.previous_crops,
            "average_yield_kg_per_hectare": self.average_yield_kg_per_hectare,
            "common_issues": self.common_issues,
            "successful_practices": self.successful_practices,
            "last_soil_test_date": self.last_soil_test_date.isoformat() if self.last_soil_test_date else None,
            "soil_test_results": self.soil_test_results,
        }


@dataclass
class FieldContext:
    """Complete field context for AI"""

    field_id: str
    field_name: str
    farm_name: str
    area_hectares: float
    soil_type: str
    irrigation_type: str
    current_crop: Optional[str]
    growth_stage: Optional[str]
    planting_date: Optional[date]
    location: dict
    weather: Optional[WeatherContext]
    history: Optional[HistoricalContext]
    additional_notes: Optional[str]

    def to_dict(self) -> dict:
        return {
            "field_id": self.field_id,
            "field_name": self.field_name,
            "farm_name": self.farm_name,
            "area_hectares": self.area_hectares,
            "soil_type": self.soil_type,
            "irrigation_type": self.irrigation_type,
            "current_crop": self.current_crop,
            "growth_stage": self.growth_stage,
            "planting_date": self.planting_date.isoformat() if self.planting_date else None,
            "location": self.location,
            "weather": self.weather.to_dict() if self.weather else None,
            "history": self.history.to_dict() if self.history else None,
            "additional_notes": self.additional_notes,
        }

    def to_prompt_text(self) -> str:
        """Convert context to text for AI prompt"""
        lines = [
            f"Field: {self.field_name} ({self.area_hectares} hectares)",
            f"Farm: {self.farm_name}",
            f"Soil: {self.soil_type}, Irrigation: {self.irrigation_type}",
        ]

        if self.current_crop:
            lines.append(f"Current Crop: {self.current_crop} ({self.growth_stage})")

        if self.weather:
            lines.append(
                f"Weather: {self.weather.conditions}, "
                f"{self.weather.temperature_c}°C, "
                f"{self.weather.humidity_percent}% humidity"
            )

        if self.history:
            lines.append(f"Previous crops: {', '.join(self.history.previous_crops)}")

        return "\n".join(lines)
