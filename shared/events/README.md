# SAHOOL Events System

# نظام الأحداث الموزع لمنصة سهول

Complete event-driven architecture implementation for the SAHOOL agricultural platform using NATS messaging.

## 📦 Contents

```
/home/user/sahool-unified-v15-idp/shared/events/
├── contracts.py      # Pydantic event contracts (26KB)
├── subjects.py       # NATS subject constants (19KB)
├── publisher.py      # Async NATS publisher (19KB)
├── subscriber.py     # Async NATS subscriber (24KB)
├── models.py         # Legacy event models (7.5KB)
├── __init__.py       # Module exports (5.2KB)
├── EXAMPLES.md       # Comprehensive usage examples
└── README.md         # This file
```

## 🚀 Quick Start

### Installation

Install the NATS client library:

```bash
pip install nats-py
```

### Publishing Events

```python
from shared.events import (
    EventPublisher,
    FieldCreatedEvent,
    SAHOOL_FIELD_CREATED
)

# Create and connect publisher
publisher = EventPublisher(service_name="field-service")
await publisher.connect()

# Create event
event = FieldCreatedEvent(
    field_id=uuid4(),
    farm_id=uuid4(),
    tenant_id=uuid4(),
    name="North Field",
    name_ar="الحقل الشمالي",
    geometry_wkt="POLYGON(...)",
    area_hectares=25.5
)

# Publish
await publisher.publish_event(SAHOOL_FIELD_CREATED, event)
```

### Subscribing to Events

```python
from shared.events import (
    EventSubscriber,
    FieldCreatedEvent,
    SAHOOL_FIELD_CREATED
)

# Create handler
async def handle_field_created(event: FieldCreatedEvent):
    print(f"New field: {event.name}")

# Subscribe
subscriber = EventSubscriber(service_name="notification-service")
await subscriber.connect()
await subscriber.subscribe(
    SAHOOL_FIELD_CREATED,
    handle_field_created,
    event_class=FieldCreatedEvent
)

# Run
await subscriber.run()
```

## 📋 Event Contracts

### Available Event Types

#### Field Events

- `FieldCreatedEvent` - New field created
- `FieldUpdatedEvent` - Field updated
- `FieldDeletedEvent` - Field deleted

#### Weather Events

- `WeatherForecastEvent` - Weather forecast update
- `WeatherAlertEvent` - Weather alert/warning

#### Satellite Events

- `SatelliteDataReadyEvent` - Satellite imagery processed
- `SatelliteAnomalyEvent` - Anomaly detected in satellite data

#### Health Events

- `DiseaseDetectedEvent` - Crop disease detected
- `CropStressEvent` - Crop stress detected (water, nutrient, etc.)

#### Inventory Events

- `LowStockEvent` - Low inventory stock alert
- `BatchExpiredEvent` - Product batch expired/expiring

#### Billing Events

- `SubscriptionCreatedEvent` - New subscription created
- `PaymentCompletedEvent` - Payment successfully processed
- `SubscriptionRenewedEvent` - Subscription renewed
- `PaymentFailedEvent` - Payment failed

## 🎯 NATS Subjects

All subjects follow the pattern: `sahool.{domain}.{entity}.{action}`

### Field Subjects

```python
SAHOOL_FIELD_CREATED = "sahool.field.created"
SAHOOL_FIELD_UPDATED = "sahool.field.updated"
SAHOOL_FIELD_DELETED = "sahool.field.deleted"
SAHOOL_FIELD_ALL = "sahool.field.*"  # Wildcard
```

### Weather Subjects

```python
SAHOOL_WEATHER_FORECAST = "sahool.weather.forecast"
SAHOOL_WEATHER_ALERT = "sahool.weather.alert"
SAHOOL_WEATHER_ALL = "sahool.weather.*"
```

### Satellite Subjects

```python
SAHOOL_SATELLITE_DATA_READY = "sahool.satellite.data.ready"
SAHOOL_SATELLITE_ANOMALY = "sahool.satellite.anomaly"
SAHOOL_SATELLITE_ALL = "sahool.satellite.*"
```

### Health Subjects

```python
SAHOOL_HEALTH_DISEASE_DETECTED = "sahool.health.disease.detected"
SAHOOL_HEALTH_STRESS_DETECTED = "sahool.health.stress.detected"
SAHOOL_HEALTH_ALL = "sahool.health.*"
```

### Inventory Subjects

```python
SAHOOL_INVENTORY_LOW_STOCK = "sahool.inventory.low_stock"
SAHOOL_INVENTORY_BATCH_EXPIRED = "sahool.inventory.batch.expired"
SAHOOL_INVENTORY_ALL = "sahool.inventory.*"
```

### Billing Subjects

```python
SAHOOL_BILLING_SUBSCRIPTION_CREATED = "sahool.billing.subscription.created"
SAHOOL_BILLING_PAYMENT_COMPLETED = "sahool.billing.payment.completed"
SAHOOL_BILLING_PAYMENT_FAILED = "sahool.billing.payment.failed"
SAHOOL_BILLING_ALL = "sahool.billing.*"
```

## ⚙️ Features

### Publisher Features

- ✅ Automatic JSON serialization from Pydantic models
- ✅ JetStream support for guaranteed delivery
- ✅ Automatic reconnection
- ✅ Retry logic with exponential backoff
- ✅ Event validation
- ✅ Connection health monitoring
- ✅ Batch publishing
- ✅ Statistics tracking

### Subscriber Features

- ✅ Automatic JSON deserialization to Pydantic models
- ✅ JetStream support with durable consumers
- ✅ Automatic reconnection
- ✅ Error handling and retry logic
- ✅ Queue groups for load balancing
- ✅ Message acknowledgment
- ✅ Concurrent message processing
- ✅ Statistics tracking

## 🔧 Configuration

### Environment Variables

```bash
# NATS server URL
NATS_URL=nats://localhost:4222

# Service identification
SERVICE_NAME=my-service
SERVICE_VERSION=1.0.0
```

### Publisher Configuration

```python
from shared.events import PublisherConfig, EventPublisher

config = PublisherConfig(
    servers=["nats://localhost:4222"],
    name="my-publisher",
    enable_jetstream=True,
    max_retry_attempts=3,
    retry_delay=0.5
)

publisher = EventPublisher(config=config)
```

### Subscriber Configuration

```python
from shared.events import SubscriberConfig, EventSubscriber

config = SubscriberConfig(
    servers=["nats://localhost:4222"],
    name="my-subscriber",
    enable_jetstream=True,
    max_concurrent_messages=10,
    enable_error_retry=True
)

subscriber = EventSubscriber(config=config)
```

## 📊 Monitoring

### Publisher Statistics

```python
stats = publisher.stats
print(f"Published: {stats['publish_count']}")
print(f"Errors: {stats['error_count']}")
print(f"Connected: {stats['connected']}")
```

### Subscriber Statistics

```python
stats = subscriber.stats
print(f"Messages: {stats['message_count']}")
print(f"Errors: {stats['error_count']}")
print(f"Subscriptions: {stats['active_subscriptions']}")
```

## 🎓 Advanced Usage

### Queue Groups for Load Balancing

```python
# Multiple instances share the load
await subscriber.subscribe(
    SAHOOL_SATELLITE_DATA_READY,
    handle_satellite_data,
    queue_group="satellite-processors"
)
```

### Durable Consumers (JetStream)

```python
# Consumer survives restarts
await subscriber.subscribe(
    SAHOOL_FIELD_CREATED,
    handle_field,
    durable_name="analytics-consumer"
)
```

### Context Managers

```python
# Automatic connection management
async with EventPublisher() as publisher:
    await publisher.publish_event(subject, event)

async with EventSubscriber() as subscriber:
    await subscriber.subscribe(subject, handler)
    await subscriber.run()
```

## 📚 Documentation

- **EXAMPLES.md** - Comprehensive usage examples
- **contracts.py** - Event contract definitions with docstrings
- **subjects.py** - Subject constants and naming conventions
- **publisher.py** - Publisher class documentation
- **subscriber.py** - Subscriber class documentation

## 🔗 Related Services

This event system is used by:

- `field-core` - Field management service
- `satellite-service` - Satellite imagery processing
- `weather-core` - Weather data and alerts
- `inventory-service` - Inventory management
- `billing-core` - Billing and subscriptions
- `notification-service` - Push notifications
- `agro-advisor` - AI recommendations

## 🐛 Troubleshooting

### NATS Connection Issues

```python
# Check connection
if not publisher.is_connected:
    print("Not connected to NATS")
    if not await publisher.connect():
        print("Failed to reconnect")
```

### Event Validation Errors

```python
from pydantic import ValidationError

try:
    event = FieldCreatedEvent(...)
except ValidationError as e:
    print(f"Validation error: {e}")
```

### Missing NATS Package

```bash
# Install NATS client
pip install nats-py

# Or add to requirements.txt
echo "nats-py>=2.2.0" >> requirements.txt
pip install -r requirements.txt
```

## 🤝 Contributing

When adding new event types:

1. Define the event contract in `contracts.py`
2. Add subject constants in `subjects.py`
3. Update `__init__.py` exports
4. Add examples to `EXAMPLES.md`
5. Update this README

## 📝 License

Part of the SAHOOL agricultural platform.

---

**المزيد من المعلومات:** See `EXAMPLES.md` for detailed usage examples.
