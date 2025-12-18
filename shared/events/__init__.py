"""
SAHOOL Events Module
====================
Event schemas, models, and publishers for event-driven architecture.

Exports:
    - Event models (Pydantic) for type-safe event handling
    - JSON schemas are in shared/contracts/events/
"""

from .models import (
    AdvisorRecommendationEvent,
    AlertCreatedEvent,
    BaseEvent,
    CropPlantedEvent,
    FarmCreatedEvent,
    FieldCreatedEvent,
    FieldUpdatedEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
)

__all__ = [
    "BaseEvent",
    "FieldCreatedEvent",
    "FieldUpdatedEvent",
    "FarmCreatedEvent",
    "CropPlantedEvent",
    "TaskCreatedEvent",
    "TaskCompletedEvent",
    "AdvisorRecommendationEvent",
    "AlertCreatedEvent",
]
