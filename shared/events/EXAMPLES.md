# SAHOOL Events - Usage Examples

# أمثلة استخدام نظام الأحداث

This document provides comprehensive examples for using the SAHOOL event system with NATS.

## Table of Contents

1. [Basic Publisher Example](#basic-publisher-example)
2. [Basic Subscriber Example](#basic-subscriber-example)
3. [Publishing Different Event Types](#publishing-different-event-types)
4. [Advanced Subscriber Patterns](#advanced-subscriber-patterns)
5. [Using Context Managers](#using-context-managers)
6. [JetStream Support](#jetstream-support)
7. [Error Handling](#error-handling)
8. [Service Integration](#service-integration)

---

## Basic Publisher Example

### Simple Event Publishing

```python
import asyncio
from uuid import uuid4
from shared.events import (
    EventPublisher,
    FieldCreatedEvent,
    SAHOOL_FIELD_CREATED,
)

async def main():
    # Create publisher
    publisher = EventPublisher(
        service_name="field-service",
        service_version="1.0.0"
    )

    # Connect to NATS
    await publisher.connect()

    # Create event
    event = FieldCreatedEvent(
        field_id=uuid4(),
        farm_id=uuid4(),
        tenant_id=uuid4(),
        name="North Field",
        name_ar="الحقل الشمالي",
        geometry_wkt="POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))",
        area_hectares=25.5,
        soil_type="clay",
        irrigation_type="drip",
    )

    # Publish event
    success = await publisher.publish_event(
        SAHOOL_FIELD_CREATED,
        event
    )

    if success:
        print(f"✅ Event published: {event.event_id}")
    else:
        print("❌ Failed to publish event")

    # Close connection
    await publisher.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using Singleton Publisher

```python
from shared.events import get_publisher, SAHOOL_FIELD_UPDATED, FieldUpdatedEvent

async def update_field():
    # Get singleton publisher (auto-connects)
    publisher = await get_publisher(
        service_name="field-service",
        service_version="1.0.0"
    )

    event = FieldUpdatedEvent(
        field_id=uuid4(),
        ndvi_value=0.75,
        updated_by=uuid4()
    )

    await publisher.publish_event(SAHOOL_FIELD_UPDATED, event)
```

---

## Basic Subscriber Example

### Simple Event Subscription

```python
import asyncio
from shared.events import (
    EventSubscriber,
    FieldCreatedEvent,
    SAHOOL_FIELD_CREATED,
)

async def handle_field_created(event: FieldCreatedEvent):
    """
    معالج إنشاء حقل جديد
    Handler for new field creation
    """
    print(f"📨 New field created: {event.name} ({event.name_ar})")
    print(f"   Area: {event.area_hectares} hectares")
    print(f"   Farm ID: {event.farm_id}")

async def main():
    # Create subscriber
    subscriber = EventSubscriber(
        service_name="notification-service",
        service_version="1.0.0"
    )

    # Connect to NATS
    await subscriber.connect()

    # Subscribe to field created events
    await subscriber.subscribe(
        subject=SAHOOL_FIELD_CREATED,
        handler=handle_field_created,
        event_class=FieldCreatedEvent  # Auto-deserialize to this class
    )

    print("🚀 Subscriber running... Press Ctrl+C to stop")

    # Keep running
    await subscriber.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Subscribing to Multiple Subjects

```python
from shared.events import (
    EventSubscriber,
    SAHOOL_FIELD_ALL,
    SAHOOL_WEATHER_ALL,
    FieldCreatedEvent,
    WeatherAlertEvent,
)

async def handle_field_event(event):
    print(f"📨 Field event: {event}")

async def handle_weather_event(event):
    print(f"🌦️  Weather event: {event}")

async def main():
    subscriber = EventSubscriber()
    await subscriber.connect()

    # Subscribe to all field events
    await subscriber.subscribe(
        SAHOOL_FIELD_ALL,  # Wildcard: sahool.field.*
        handle_field_event
    )

    # Subscribe to all weather events
    await subscriber.subscribe(
        SAHOOL_WEATHER_ALL,  # Wildcard: sahool.weather.*
        handle_weather_event
    )

    await subscriber.run()
```

---

## Publishing Different Event Types

### Weather Events

```python
from shared.events import (
    WeatherAlertEvent,
    SAHOOL_WEATHER_ALERT,
    get_publisher,
)
from datetime import datetime, timedelta

async def publish_weather_alert():
    publisher = await get_publisher()

    event = WeatherAlertEvent(
        tenant_id=uuid4(),
        field_ids=[uuid4(), uuid4()],
        alert_type="frost",
        severity="critical",
        title="Frost Warning",
        title_ar="تحذير من الصقيع",
        message="Frost expected tonight. Protect sensitive crops.",
        message_ar="يتوقع حدوث صقيع الليلة. احمِ المحاصيل الحساسة.",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(hours=12),
        affected_area_radius_km=50.0
    )

    await publisher.publish_event(SAHOOL_WEATHER_ALERT, event)
```

### Satellite Events

```python
from shared.events import (
    SatelliteDataReadyEvent,
    SatelliteAnomalyEvent,
    SAHOOL_SATELLITE_DATA_READY,
    SAHOOL_SATELLITE_ANOMALY,
    get_publisher,
)

async def publish_satellite_events():
    publisher = await get_publisher()

    # Satellite data ready
    data_event = SatelliteDataReadyEvent(
        field_id=uuid4(),
        tenant_id=uuid4(),
        satellite_source="Sentinel-2",
        capture_date=datetime.utcnow(),
        cloud_coverage=5.2,
        ndvi_mean=0.68,
        ndvi_min=0.32,
        ndvi_max=0.89,
        image_url="https://s3.example.com/images/field123.tif",
        resolution_meters=10.0,
        bands=["B4", "B8", "B3", "B2"]
    )

    await publisher.publish_event(SAHOOL_SATELLITE_DATA_READY, data_event)

    # Anomaly detected
    anomaly_event = SatelliteAnomalyEvent(
        field_id=uuid4(),
        tenant_id=uuid4(),
        anomaly_type="ndvi_drop",
        severity="high",
        confidence_score=0.92,
        affected_area_hectares=3.5,
        affected_area_percentage=14.0,
        current_value=0.45,
        baseline_value=0.72,
        deviation=-0.27,
        recommended_action="Inspect area for disease or pest damage",
        recommended_action_ar="فحص المنطقة للكشف عن الأمراض أو الآفات"
    )

    await publisher.publish_event(SAHOOL_SATELLITE_ANOMALY, anomaly_event)
```

### Inventory Events

```python
from shared.events import (
    LowStockEvent,
    BatchExpiredEvent,
    SAHOOL_INVENTORY_LOW_STOCK,
    SAHOOL_INVENTORY_BATCH_EXPIRED,
    get_publisher,
)

async def publish_inventory_events():
    publisher = await get_publisher()

    # Low stock alert
    low_stock = LowStockEvent(
        tenant_id=uuid4(),
        product_id=uuid4(),
        product_name="Nitrogen Fertilizer",
        product_name_ar="سماد نيتروجيني",
        product_category="fertilizer",
        sku="FERT-N-001",
        current_quantity=150.0,
        unit_of_measure="kg",
        threshold_quantity=500.0,
        reorder_quantity=1000.0,
        severity="medium",
        estimated_cost=2500.0,
        currency="SAR"
    )

    await publisher.publish_event(SAHOOL_INVENTORY_LOW_STOCK, low_stock)

    # Batch expired
    batch_expired = BatchExpiredEvent(
        tenant_id=uuid4(),
        batch_id=uuid4(),
        batch_number="BATCH-2024-001",
        product_id=uuid4(),
        product_name="Pesticide XYZ",
        product_name_ar="مبيد حشري XYZ",
        expiry_date=datetime.utcnow(),
        quantity=50.0,
        unit_of_measure="L",
        status="expired",
        days_until_expiry=-5,  # Negative = already expired
        value_at_risk=1500.0,
        currency="SAR",
        recommended_action="Dispose of expired pesticide safely",
        recommended_action_ar="التخلص من المبيد منتهي الصلاحية بشكل آمن"
    )

    await publisher.publish_event(SAHOOL_INVENTORY_BATCH_EXPIRED, batch_expired)
```

### Billing Events

```python
from shared.events import (
    SubscriptionCreatedEvent,
    PaymentCompletedEvent,
    SAHOOL_BILLING_SUBSCRIPTION_CREATED,
    SAHOOL_BILLING_PAYMENT_COMPLETED,
    get_publisher,
)

async def publish_billing_events():
    publisher = await get_publisher()

    # Subscription created
    subscription = SubscriptionCreatedEvent(
        subscription_id=uuid4(),
        tenant_id=uuid4(),
        user_id=uuid4(),
        plan_id="pro-annual",
        plan_name="Professional Plan",
        plan_tier="professional",
        billing_cycle="annual",
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=365),
        price_amount=9999.00,
        currency="SAR",
        max_fields=100,
        max_area_hectares=1000.0,
        features_enabled=[
            "satellite_imagery",
            "weather_alerts",
            "ai_recommendations",
            "inventory_management"
        ],
        auto_renew=True
    )

    await publisher.publish_event(SAHOOL_BILLING_SUBSCRIPTION_CREATED, subscription)

    # Payment completed
    payment = PaymentCompletedEvent(
        payment_id=uuid4(),
        subscription_id=subscription.subscription_id,
        tenant_id=subscription.tenant_id,
        amount=9999.00,
        currency="SAR",
        payment_method="credit_card",
        payment_provider="Stripe",
        transaction_id="txn_abc123xyz",
        description="Annual subscription payment",
        description_ar="دفع الاشتراك السنوي",
        subtotal=8695.22,
        tax_amount=1303.78,
        tax_percentage=15.0,
        receipt_url="https://receipts.sahool.io/12345"
    )

    await publisher.publish_event(SAHOOL_BILLING_PAYMENT_COMPLETED, payment)
```

---

## Advanced Subscriber Patterns

### Queue Groups for Load Balancing

```python
async def main():
    subscriber = EventSubscriber(service_name="worker-1")
    await subscriber.connect()

    # Multiple instances with same queue group share the load
    await subscriber.subscribe(
        SAHOOL_SATELLITE_DATA_READY,
        handle_satellite_data,
        queue_group="satellite-processors",  # Load balancing
        event_class=SatelliteDataReadyEvent
    )

    await subscriber.run()
```

### Durable Consumers (JetStream)

```python
async def main():
    subscriber = EventSubscriber(service_name="analytics-service")
    await subscriber.connect()

    # Durable consumer - survives restarts
    await subscriber.subscribe(
        SAHOOL_FIELD_CREATED,
        handle_field_for_analytics,
        durable_name="analytics-field-consumer",  # Persistent consumer
        event_class=FieldCreatedEvent
    )

    await subscriber.run()
```

### Multiple Handlers

```python
from shared.events import (
    SAHOOL_HEALTH_DISEASE_DETECTED,
    SAHOOL_HEALTH_STRESS_DETECTED,
    DiseaseDetectedEvent,
    CropStressEvent,
)

async def handle_disease(event: DiseaseDetectedEvent):
    print(f"🦠 Disease detected: {event.disease_name}")
    # Send alert, create task, etc.

async def handle_stress(event: CropStressEvent):
    print(f"⚠️  Crop stress: {event.stress_type}")
    # Adjust irrigation, create recommendation, etc.

async def main():
    subscriber = EventSubscriber()
    await subscriber.connect()

    await subscriber.subscribe(
        SAHOOL_HEALTH_DISEASE_DETECTED,
        handle_disease,
        event_class=DiseaseDetectedEvent
    )

    await subscriber.subscribe(
        SAHOOL_HEALTH_STRESS_DETECTED,
        handle_stress,
        event_class=CropStressEvent
    )

    await subscriber.run()
```

---

## Using Context Managers

### Publisher Context Manager

```python
from shared.events import EventPublisher, SAHOOL_FIELD_CREATED, FieldCreatedEvent

async def create_field():
    # Automatically connects and disconnects
    async with EventPublisher(service_name="field-service") as publisher:
        event = FieldCreatedEvent(...)
        await publisher.publish_event(SAHOOL_FIELD_CREATED, event)
    # Connection automatically closed
```

### Subscriber Context Manager

```python
from shared.events import EventSubscriber

async def main():
    async with EventSubscriber(service_name="my-service") as subscriber:
        await subscriber.subscribe(...)
        await subscriber.run()
    # Automatically unsubscribes and closes
```

---

## JetStream Support

### Enable JetStream for Guaranteed Delivery

```python
from shared.events import EventPublisher, PublisherConfig

async def main():
    config = PublisherConfig(
        enable_jetstream=True,  # Enable JetStream
        servers=["nats://localhost:4222"]
    )

    publisher = EventPublisher(config=config)
    await publisher.connect()

    # This message will be persisted and delivered at least once
    await publisher.publish_event(
        SAHOOL_BILLING_PAYMENT_COMPLETED,
        payment_event,
        use_jetstream=True  # Explicitly use JetStream
    )
```

---

## Error Handling

### Publisher Error Handling

```python
from shared.events import EventPublisher

async def publish_with_error_handling():
    publisher = EventPublisher()

    if not await publisher.connect():
        print("Failed to connect to NATS")
        return

    try:
        success = await publisher.publish_event(subject, event)

        if not success:
            print("Failed to publish event")
            # Log error, retry, or alert

    except Exception as e:
        print(f"Error publishing event: {e}")

    finally:
        await publisher.close()
```

### Subscriber Error Handling

```python
async def robust_handler(event):
    try:
        # Process event
        process_event(event)
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        # The subscriber will automatically retry based on config
```

---

## Service Integration

### Complete Microservice Example

```python
# satellite_service.py
import asyncio
from shared.events import (
    EventPublisher,
    EventSubscriber,
    FieldCreatedEvent,
    SatelliteDataReadyEvent,
    SAHOOL_FIELD_CREATED,
    SAHOOL_SATELLITE_DATA_READY,
)

class SatelliteService:
    def __init__(self):
        self.publisher = EventPublisher(
            service_name="satellite-service",
            service_version="2.0.0"
        )
        self.subscriber = EventSubscriber(
            service_name="satellite-service",
            service_version="2.0.0"
        )

    async def start(self):
        # Connect to NATS
        await self.publisher.connect()
        await self.subscriber.connect()

        # Subscribe to field creation events
        await self.subscriber.subscribe(
            SAHOOL_FIELD_CREATED,
            self.handle_new_field,
            event_class=FieldCreatedEvent,
            queue_group="satellite-processors"
        )

        print("✅ Satellite service started")
        await self.subscriber.run()

    async def handle_new_field(self, event: FieldCreatedEvent):
        """Process new field - request satellite imagery"""
        print(f"📨 New field: {event.name} - requesting satellite data")

        # Simulate satellite data processing
        await asyncio.sleep(2)

        # Publish satellite data ready event
        satellite_event = SatelliteDataReadyEvent(
            field_id=event.field_id,
            tenant_id=event.tenant_id,
            satellite_source="Sentinel-2",
            capture_date=datetime.utcnow(),
            ndvi_mean=0.65,
            image_url=f"https://s3.example.com/{event.field_id}.tif"
        )

        await self.publisher.publish_event(
            SAHOOL_SATELLITE_DATA_READY,
            satellite_event
        )

        print(f"✅ Satellite data published for field {event.field_id}")

    async def stop(self):
        await self.subscriber.close()
        await self.publisher.close()

if __name__ == "__main__":
    service = SatelliteService()

    try:
        asyncio.run(service.start())
    except KeyboardInterrupt:
        print("🛑 Stopping service...")
        asyncio.run(service.stop())
```

---

## Environment Variables

Configure NATS connection using environment variables:

```bash
# NATS server URL
export NATS_URL="nats://localhost:4222"

# Service identification
export SERVICE_NAME="my-service"
export SERVICE_VERSION="1.0.0"
```

---

## Best Practices

1. **Use Type Hints**: Always specify `event_class` in subscribers for automatic validation
2. **Handle Errors**: Wrap handlers in try-except for resilience
3. **Use Queue Groups**: For load balancing across multiple instances
4. **Use Durable Consumers**: For critical events that must not be lost
5. **Monitor Stats**: Check `publisher.stats` and `subscriber.stats` regularly
6. **Graceful Shutdown**: Always close connections properly
7. **Use Context Managers**: For automatic resource cleanup
8. **Validate Events**: Let Pydantic handle validation automatically
9. **Add Arabic Translations**: Include Arabic fields where applicable
10. **Log Important Events**: Use proper logging for debugging and monitoring

---

## Testing

### Unit Test Example

```python
import pytest
from shared.events import FieldCreatedEvent

def test_field_created_event():
    event = FieldCreatedEvent(
        field_id=uuid4(),
        farm_id=uuid4(),
        tenant_id=uuid4(),
        name="Test Field",
        geometry_wkt="POLYGON((0 0, 0 1, 1 1, 1 0, 0 0))",
        area_hectares=10.5
    )

    assert event.name == "Test Field"
    assert event.area_hectares == 10.5
    assert event.event_id is not None
    assert event.timestamp is not None
```

---

For more information, see the individual module documentation:

- `/home/user/sahool-unified-v15-idp/shared/events/contracts.py`
- `/home/user/sahool-unified-v15-idp/shared/events/subjects.py`
- `/home/user/sahool-unified-v15-idp/shared/events/publisher.py`
- `/home/user/sahool-unified-v15-idp/shared/events/subscriber.py`
