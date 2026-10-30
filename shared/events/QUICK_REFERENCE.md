# SAHOOL Events - Quick Reference Card

# مرجع سريع لنظام الأحداث

## Import Statement

```python
from shared.events import (
    # Publisher & Subscriber
    EventPublisher, EventSubscriber,

    # Field Events
    FieldCreatedEvent, FieldUpdatedEvent, FieldDeletedEvent,

    # Weather Events
    WeatherForecastEvent, WeatherAlertEvent,

    # Satellite Events
    SatelliteDataReadyEvent, SatelliteAnomalyEvent,

    # Health Events
    DiseaseDetectedEvent, CropStressEvent,

    # Inventory Events
    LowStockEvent, BatchExpiredEvent,

    # Billing Events
    SubscriptionCreatedEvent, PaymentCompletedEvent,

    # NATS Subjects
    SAHOOL_FIELD_CREATED, SAHOOL_FIELD_ALL,
    SAHOOL_WEATHER_ALERT, SAHOOL_SATELLITE_DATA_READY,
    SAHOOL_HEALTH_DISEASE_DETECTED, SAHOOL_INVENTORY_LOW_STOCK,
    SAHOOL_BILLING_PAYMENT_COMPLETED,
)
```

## Publish Event (3 Lines)

```python
publisher = EventPublisher(service_name="my-service")
await publisher.connect()
await publisher.publish_event(SAHOOL_FIELD_CREATED, event)
```

## Subscribe to Event (4 Lines)

```python
subscriber = EventSubscriber(service_name="my-service")
await subscriber.connect()
await subscriber.subscribe(SAHOOL_FIELD_CREATED, handler, event_class=FieldCreatedEvent)
await subscriber.run()
```

## Common Event Patterns

### Field Created

```python
event = FieldCreatedEvent(
    field_id=uuid4(), farm_id=uuid4(), tenant_id=uuid4(),
    name="Field Name", name_ar="اسم الحقل",
    geometry_wkt="POLYGON(...)", area_hectares=25.0
)
await publisher.publish_event(SAHOOL_FIELD_CREATED, event)
```

### Weather Alert

```python
event = WeatherAlertEvent(
    tenant_id=uuid4(), field_ids=[uuid4()],
    alert_type="frost", severity="critical",
    title="Frost Warning", title_ar="تحذير من الصقيع",
    message="...", start_time=datetime.utcnow()
)
await publisher.publish_event(SAHOOL_WEATHER_ALERT, event)
```

### Satellite Data Ready

```python
event = SatelliteDataReadyEvent(
    field_id=uuid4(), tenant_id=uuid4(),
    satellite_source="Sentinel-2", capture_date=datetime.utcnow(),
    ndvi_mean=0.68, cloud_coverage=5.0
)
await publisher.publish_event(SAHOOL_SATELLITE_DATA_READY, event)
```

### Low Stock Alert

```python
event = LowStockEvent(
    tenant_id=uuid4(), product_id=uuid4(),
    product_name="Fertilizer", product_name_ar="سماد",
    current_quantity=150.0, unit_of_measure="kg",
    threshold_quantity=500.0, severity="medium"
)
await publisher.publish_event(SAHOOL_INVENTORY_LOW_STOCK, event)
```

### Payment Completed

```python
event = PaymentCompletedEvent(
    payment_id=uuid4(), tenant_id=uuid4(),
    amount=9999.00, currency="SAR",
    payment_method="credit_card", transaction_id="txn_123"
)
await publisher.publish_event(SAHOOL_BILLING_PAYMENT_COMPLETED, event)
```

## Subject Wildcards

```python
SAHOOL_FIELD_ALL = "sahool.field.*"           # All field events
SAHOOL_WEATHER_ALL = "sahool.weather.*"       # All weather events
SAHOOL_SATELLITE_ALL = "sahool.satellite.*"   # All satellite events
SAHOOL_HEALTH_ALL = "sahool.health.*"         # All health events
SAHOOL_INVENTORY_ALL = "sahool.inventory.*"   # All inventory events
SAHOOL_BILLING_ALL = "sahool.billing.*"       # All billing events
```

## Advanced Features

### Context Manager

```python
async with EventPublisher() as pub:
    await pub.publish_event(subject, event)
```

### Queue Group (Load Balancing)

```python
await subscriber.subscribe(subject, handler, queue_group="workers")
```

### Durable Consumer (JetStream)

```python
await subscriber.subscribe(subject, handler, durable_name="my-consumer")
```

### Batch Publishing

```python
events = [(SAHOOL_FIELD_CREATED, event1), (SAHOOL_FIELD_UPDATED, event2)]
success_count = await publisher.publish_events(events)
```

## Environment Variables

```bash
export NATS_URL="nats://localhost:4222"
export SERVICE_NAME="my-service"
export SERVICE_VERSION="1.0.0"
```

## File Locations

| File            | Description        | Size |
| --------------- | ------------------ | ---- |
| `contracts.py`  | Event definitions  | 26KB |
| `subjects.py`   | NATS subjects      | 19KB |
| `publisher.py`  | Publisher class    | 19KB |
| `subscriber.py` | Subscriber class   | 24KB |
| `EXAMPLES.md`   | Usage examples     | 18KB |
| `README.md`     | Full documentation | 8KB  |

## Installation

```bash
pip install nats-py pydantic
```

---

**Full Examples:** See `/home/user/sahool-unified-v15-idp/shared/events/EXAMPLES.md`
