"""
SAHOOL Context Builder Service
Builds context for AI recommendations
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from .models import FieldContext, WeatherContext, HistoricalContext


class ContextBuilder:
    """Service for building AI context"""

    def __init__(self):
        # In production, these would be injected dependencies
        self._weather_cache: dict[str, WeatherContext] = {}

    def build_field_context(
        self,
        field_id: str,
        field_data: dict,
        farm_data: dict,
        crop_data: Optional[dict] = None,
        include_weather: bool = True,
        include_history: bool = True,
    ) -> FieldContext:
        """Build complete context for a field"""
        # Extract location
        location = {
            "latitude": field_data.get("boundary", {}).get("center_latitude"),
            "longitude": field_data.get("boundary", {}).get("center_longitude"),
        }

        # Get weather if requested
        weather = None
        if include_weather and location.get("latitude"):
            weather = self._get_weather_context(
                location["latitude"],
                location["longitude"],
            )

        # Get history if requested
        history = None
        if include_history:
            history = self._get_historical_context(field_id)

        return FieldContext(
            field_id=field_id,
            field_name=field_data.get("name", "Unknown"),
            farm_name=farm_data.get("name", "Unknown"),
            area_hectares=field_data.get("area_hectares", 0),
            soil_type=field_data.get("soil_type", "unknown"),
            irrigation_type=field_data.get("irrigation_type", "unknown"),
            current_crop=crop_data.get("crop_type") if crop_data else None,
            growth_stage=crop_data.get("growth_stage") if crop_data else None,
            planting_date=crop_data.get("planting_date") if crop_data else None,
            location=location,
            weather=weather,
            history=history,
            additional_notes=None,
        )

    def _get_weather_context(
        self,
        latitude: float,
        longitude: float,
    ) -> WeatherContext:
        """
        Get weather context for location.

        In production, this would call a weather API.
        This is a placeholder implementation.
        """
        cache_key = f"{latitude:.2f},{longitude:.2f}"

        if cache_key in self._weather_cache:
            return self._weather_cache[cache_key]

        # Placeholder weather data
        weather = WeatherContext(
            temperature_c=28.0,
            humidity_percent=45.0,
            precipitation_mm=0.0,
            wind_speed_kmh=12.0,
            conditions="Sunny",
            forecast_days=7,
            forecast_data=[],
        )

        self._weather_cache[cache_key] = weather
        return weather

    def _get_historical_context(self, field_id: str) -> HistoricalContext:
        """
        Get historical context for field.

        In production, this would query the database.
        This is a placeholder implementation.
        """
        return HistoricalContext(
            previous_crops=[],
            average_yield_kg_per_hectare=None,
            common_issues=[],
            successful_practices=[],
            last_soil_test_date=None,
            soil_test_results=None,
        )

    def build_minimal_context(
        self,
        tenant_id: str,
        query: str,
    ) -> dict:
        """Build minimal context when no field is specified"""
        return {
            "tenant_id": tenant_id,
            "query": query,
            "timestamp": date.today().isoformat(),
        }
