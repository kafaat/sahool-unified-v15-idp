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

from jsonschema import ValidationError

from .analytics_events import NDVICalculatedEvent, YieldPredictedEvent
from .base import BaseEvent, EventMetadata
from .consumer import EventConsumer
from .crop_events import CropDiseaseDetectedEvent, CropHarvestedEvent, CropPlantedEvent
from .field_events import FieldCreatedEvent, FieldUpdatedEvent
from .iot_events import SensorAlertEvent, SensorReadingEvent
from .publisher import EventPublisher
from .registry import EventRegistry
from .weather_events import WeatherAlertIssuedEvent, WeatherForecastUpdatedEvent

__all__ = [
    # Base
    "BaseEvent",
    "EventMetadata",
    "ValidationError",
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
