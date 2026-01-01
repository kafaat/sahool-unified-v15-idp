"""
SAHOOL Event Contracts Library
==============================

Provides strongly-typed event definitions with versioning support.

Usage:
    from shared.contracts.events import FieldCreatedEvent, EventPublisher

    # Create an event
    event = FieldCreatedEvent(
        field_id="...",
        tenant_id="...",
        name="My Field",
        geometry={...},
        area_hectares=10.5
    )

    # Publish
    await publisher.publish(event)
"""

from .base import BaseEvent, EventMetadata
from .field_events import FieldCreatedEvent, FieldUpdatedEvent
from .crop_events import CropPlantedEvent, CropDiseaseDetectedEvent, CropHarvestedEvent
from .weather_events import WeatherForecastUpdatedEvent, WeatherAlertIssuedEvent
from .iot_events import SensorReadingEvent, SensorAlertEvent
from .analytics_events import NDVICalculatedEvent, YieldPredictedEvent
from .publisher import EventPublisher
from .consumer import EventConsumer
from .registry import EventRegistry

__all__ = [
    # Base
    "BaseEvent",
    "EventMetadata",
    # Field Events
    "FieldCreatedEvent",
    "FieldUpdatedEvent",
    # Crop Events
    "CropPlantedEvent",
    "CropDiseaseDetectedEvent",
    "CropHarvestedEvent",
    # Weather Events
    "WeatherForecastUpdatedEvent",
    "WeatherAlertIssuedEvent",
    # IoT Events
    "SensorReadingEvent",
    "SensorAlertEvent",
    # Analytics Events
    "NDVICalculatedEvent",
    "YieldPredictedEvent",
    # Infrastructure
    "EventPublisher",
    "EventConsumer",
    "EventRegistry",
]
