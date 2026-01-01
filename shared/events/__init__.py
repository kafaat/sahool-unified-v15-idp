"""
SAHOOL Events Module
====================
نظام الأحداث الموزع لمنصة سهول

Event schemas, models, publishers, and subscribers for event-driven architecture.

Exports:
    - Event contracts (Pydantic models) for type-safe event handling
    - NATS subject constants
    - EventPublisher for publishing events
    - EventSubscriber for consuming events
    - Legacy event models from models.py
    - JSON schemas are in shared/contracts/events/

Usage:
    # Publishing events
    from shared.events import EventPublisher, FieldCreatedEvent, SAHOOL_FIELD_CREATED

    publisher = EventPublisher()
    await publisher.connect()

    event = FieldCreatedEvent(field_id=..., farm_id=..., name="Field 1")
    await publisher.publish_event(SAHOOL_FIELD_CREATED, event)

    # Subscribing to events
    from shared.events import EventSubscriber, SAHOOL_FIELD_ALL

    subscriber = EventSubscriber()
    await subscriber.connect()

    async def handle_field_event(event):
        print(f"Field event: {event}")

    await subscriber.subscribe(SAHOOL_FIELD_ALL, handle_field_event)
    await subscriber.run()
"""

# Legacy event models (for backward compatibility)
from .models import (
    AdvisorRecommendationEvent,
    AlertCreatedEvent,
    BaseEvent as LegacyBaseEvent,
    CropPlantedEvent,
    FarmCreatedEvent,
    FieldCreatedEvent as LegacyFieldCreatedEvent,
    FieldUpdatedEvent as LegacyFieldUpdatedEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
)

# New event contracts
from .contracts import (
    BaseEvent,
    # Field events
    FieldCreatedEvent,
    FieldUpdatedEvent,
    FieldDeletedEvent,
    # Weather events
    WeatherForecastEvent,
    WeatherAlertEvent,
    # Satellite events
    SatelliteDataReadyEvent,
    SatelliteAnomalyEvent,
    # Health events
    DiseaseDetectedEvent,
    CropStressEvent,
    # Inventory events
    LowStockEvent,
    BatchExpiredEvent,
    # Billing events
    SubscriptionCreatedEvent,
    PaymentCompletedEvent,
    SubscriptionRenewedEvent,
    PaymentFailedEvent,
)

# NATS subject constants
from .subjects import (
    # Field subjects
    SAHOOL_FIELD_CREATED,
    SAHOOL_FIELD_UPDATED,
    SAHOOL_FIELD_DELETED,
    SAHOOL_FIELD_ALL,
    # Weather subjects
    SAHOOL_WEATHER_FORECAST,
    SAHOOL_WEATHER_ALERT,
    SAHOOL_WEATHER_ALL,
    # Satellite subjects
    SAHOOL_SATELLITE_DATA_READY,
    SAHOOL_SATELLITE_ANOMALY,
    SAHOOL_SATELLITE_ALL,
    SAHOOL_NDVI_COMPUTED,
    # Health subjects
    SAHOOL_HEALTH_DISEASE_DETECTED,
    SAHOOL_HEALTH_STRESS_DETECTED,
    SAHOOL_HEALTH_ALL,
    # Inventory subjects
    SAHOOL_INVENTORY_LOW_STOCK,
    SAHOOL_INVENTORY_BATCH_EXPIRED,
    SAHOOL_INVENTORY_ALL,
    # Billing subjects
    SAHOOL_BILLING_SUBSCRIPTION_CREATED,
    SAHOOL_BILLING_PAYMENT_COMPLETED,
    SAHOOL_BILLING_PAYMENT_FAILED,
    SAHOOL_BILLING_ALL,
    # Utility functions
    get_subject_for_event,
    lookup_subject,
)

# Publisher and Subscriber
from .publisher import (
    EventPublisher,
    PublisherConfig,
    get_publisher,
    close_publisher,
    publish_event,
)

from .subscriber import (
    EventSubscriber,
    SubscriberConfig,
    get_subscriber,
    close_subscriber,
)

# DLQ Support
from .dlq_config import (
    DLQConfig,
    DLQMessageMetadata,
    create_dlq_streams,
    is_retriable_error,
    should_retry,
)

from .dlq_service import (
    DLQManager,
    create_dlq_router,
)

from .dlq_monitoring import (
    DLQMonitor,
    DLQAlert,
)

__all__ = [
    # Base
    "BaseEvent",

    # Event Contracts - Field
    "FieldCreatedEvent",
    "FieldUpdatedEvent",
    "FieldDeletedEvent",

    # Event Contracts - Weather
    "WeatherForecastEvent",
    "WeatherAlertEvent",

    # Event Contracts - Satellite
    "SatelliteDataReadyEvent",
    "SatelliteAnomalyEvent",

    # Event Contracts - Health
    "DiseaseDetectedEvent",
    "CropStressEvent",

    # Event Contracts - Inventory
    "LowStockEvent",
    "BatchExpiredEvent",

    # Event Contracts - Billing
    "SubscriptionCreatedEvent",
    "PaymentCompletedEvent",
    "SubscriptionRenewedEvent",
    "PaymentFailedEvent",

    # Legacy events (backward compatibility)
    "LegacyBaseEvent",
    "LegacyFieldCreatedEvent",
    "LegacyFieldUpdatedEvent",
    "FarmCreatedEvent",
    "CropPlantedEvent",
    "TaskCreatedEvent",
    "TaskCompletedEvent",
    "AdvisorRecommendationEvent",
    "AlertCreatedEvent",

    # NATS Subjects - Field
    "SAHOOL_FIELD_CREATED",
    "SAHOOL_FIELD_UPDATED",
    "SAHOOL_FIELD_DELETED",
    "SAHOOL_FIELD_ALL",

    # NATS Subjects - Weather
    "SAHOOL_WEATHER_FORECAST",
    "SAHOOL_WEATHER_ALERT",
    "SAHOOL_WEATHER_ALL",

    # NATS Subjects - Satellite
    "SAHOOL_SATELLITE_DATA_READY",
    "SAHOOL_SATELLITE_ANOMALY",
    "SAHOOL_SATELLITE_ALL",
    "SAHOOL_NDVI_COMPUTED",

    # NATS Subjects - Health
    "SAHOOL_HEALTH_DISEASE_DETECTED",
    "SAHOOL_HEALTH_STRESS_DETECTED",
    "SAHOOL_HEALTH_ALL",

    # NATS Subjects - Inventory
    "SAHOOL_INVENTORY_LOW_STOCK",
    "SAHOOL_INVENTORY_BATCH_EXPIRED",
    "SAHOOL_INVENTORY_ALL",

    # NATS Subjects - Billing
    "SAHOOL_BILLING_SUBSCRIPTION_CREATED",
    "SAHOOL_BILLING_PAYMENT_COMPLETED",
    "SAHOOL_BILLING_PAYMENT_FAILED",
    "SAHOOL_BILLING_ALL",

    # Subject utilities
    "get_subject_for_event",
    "lookup_subject",

    # Publisher
    "EventPublisher",
    "PublisherConfig",
    "get_publisher",
    "close_publisher",
    "publish_event",

    # Subscriber
    "EventSubscriber",
    "SubscriberConfig",
    "get_subscriber",
    "close_subscriber",

    # DLQ Configuration
    "DLQConfig",
    "DLQMessageMetadata",
    "create_dlq_streams",
    "is_retriable_error",
    "should_retry",

    # DLQ Management
    "DLQManager",
    "create_dlq_router",

    # DLQ Monitoring
    "DLQMonitor",
    "DLQAlert",
]
