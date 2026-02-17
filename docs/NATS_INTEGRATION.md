# NATS Integration Guide | دليل تكامل NATS

## Overview | نظرة عامة

SAHOOL platform uses NATS as its core messaging infrastructure for event-driven communication between services. This document provides comprehensive guidance on NATS integration, including the shared event library, configuration, and best practices.

تستخدم منصة سهول NATS كبنية تحتية أساسية للرسائل للتواصل القائم على الأحداث بين الخدمات. يوفر هذا المستند إرشادات شاملة حول تكامل NATS.

---

## Architecture | البنية المعمارية

### Event Flow | تدفق الأحداث

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Service   │────▶│    NATS      │────▶│   Service   │
│  Publisher  │     │  JetStream   │     │  Subscriber │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │                    │
       ▼                   ▼                    ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ EventPublisher    │  Persistence │     │EventSubscriber
│ (shared/events)   │   + DLQ      │     │(shared/events)
└─────────────┘     └──────────────┘     └─────────────┘
```

### 4-Layer Event Architecture | بنية الأحداث ذات 4 طبقات

| Layer | Services | Purpose |
|-------|----------|---------|
| **Acquisition** | satellite, iot, weather, virtual-sensors | Data ingestion |
| **Intelligence** | indicators, lai, crop-intelligence, ndvi | Feature extraction & AI |
| **Decision** | crop-growth-model, advisory, irrigation, yield | Recommendations |
| **Business** | notification, marketplace, billing, task | User operations |

---

## Shared Event Library | مكتبة الأحداث المشتركة

The platform provides a shared event library in `shared/events/` that all services should use for consistency.

### EventPublisher

```python
from shared.events.publisher import EventPublisher, PublisherConfig
from shared.events.contracts import BaseEvent

# Configuration
config = PublisherConfig(
    servers=["nats://localhost:4222"],
    name="my-service",
    enable_jetstream=True,
    jetstream_domain="sahool",  # Default domain
    enable_retry=True,
    max_retry_attempts=3,
)

# Initialize publisher
publisher = EventPublisher(
    config=config,
    service_name="my-service",
    service_version="1.0.0",
)

# Connect and publish
async with publisher:
    # Publish typed event
    event = MyEvent(field_id="123", action="created")
    await publisher.publish_event("sahool.field.created", event)

    # Publish raw JSON
    await publisher.publish_json("sahool.alerts.new", {"level": "warning"})

    # Batch publish
    events = [
        ("sahool.task.created", task_event_1),
        ("sahool.task.created", task_event_2),
    ]
    await publisher.publish_events(events)
```

### EventSubscriber

```python
from shared.events.subscriber import EventSubscriber, SubscriberConfig

# Configuration
config = SubscriberConfig(
    servers=["nats://localhost:4222"],
    name="my-service-subscriber",
    enable_jetstream=True,
    jetstream_domain="sahool",
    enable_dlq=True,  # Dead Letter Queue
    max_dlq_size=10000,
)

# Initialize subscriber
subscriber = EventSubscriber(
    config=config,
    service_name="my-service",
)

# Message handler
async def handle_field_event(msg):
    data = json.loads(msg.data.decode())
    print(f"Received: {data}")
    await msg.ack()

# Subscribe with JetStream
async with subscriber:
    await subscriber.subscribe(
        subject="sahool.field.>",
        handler=handle_field_event,
        stream_name="SAHOOL_FIELDS",
        durable_name="my-service-fields",
    )

    # Health check for Kubernetes readiness
    health = await subscriber.health_check()
    print(f"Status: {health['status']}")  # healthy, degraded, warning, unhealthy
```

### Health Check Response | استجابة فحص الصحة

```python
health = await subscriber.health_check()
# Returns:
{
    "status": "healthy",  # healthy, degraded, warning, unhealthy
    "nats_connected": True,
    "jetstream_enabled": True,
    "dlq_initialized": True,
    "active_subscriptions": 3,
    "error_count": 0,
    "dlq_count": 15,
    "details": {
        "nats": {
            "connected": True,
            "server_id": "NATS-123",
            "max_payload": 8388608
        },
        "jetstream": {
            "memory_used": 1024000,
            "storage_used": 5120000,
            "streams": 5,
            "consumers": 12
        },
        "dlq": {
            "stream": "SAHOOL_DLQ",
            "messages": 15,
            "bytes": 4096
        }
    }
}
```

---

## Subject Naming Convention | اصطلاح تسمية المواضيع

All NATS subjects must follow this pattern:

```
sahool.{domain}.{entity}.{action}
sahool.tenant.{tenant_id}.{domain}.{action}
```

### Examples | أمثلة

| Subject | Description |
|---------|-------------|
| `sahool.field.created` | Field creation event |
| `sahool.field.updated` | Field update event |
| `sahool.tenant.T001.field.created` | Tenant-scoped field creation |
| `sahool.task.assigned` | Task assignment event |
| `sahool.compliance.audit.completed` | Compliance audit completed |
| `sahool.alerts.inventory` | Inventory alert notification |

### Wildcards | الأحرف البديلة

- `sahool.field.*` - Match single token (created, updated, deleted)
- `sahool.field.>` - Match all tokens (created, updated, boundary.changed)
- `sahool.tenant.*.field.>` - Match all tenants, all field events

---

## JetStream Configuration | تكوين JetStream

### Domain | النطاق

All services use the `sahool` JetStream domain by default:

```python
config = PublisherConfig(
    jetstream_domain="sahool",  # or set JETSTREAM_DOMAIN env var
)
```

### Stream Definitions | تعريفات التدفقات

| Stream Name | Subjects | Retention | Description |
|-------------|----------|-----------|-------------|
| `SAHOOL_EVENTS` | `sahool.>` | Limits | All platform events |
| `SAHOOL_TENANT_*` | `sahool.tenant.{id}.>` | Limits | Per-tenant events |
| `SAHOOL_DLQ` | `sahool.dlq.>` | WorkQueue | Failed messages |
| `SAHOOL_ALERTS` | `sahool.alerts.>` | Interest | Alert notifications |

### Consumer Configuration | تكوين المستهلكين

```python
# Durable consumer for reliable delivery
await subscriber.subscribe(
    subject="sahool.field.>",
    stream_name="SAHOOL_EVENTS",
    durable_name="field-service-consumer",
    deliver_policy="all",  # or "new", "last"
    ack_policy="explicit",
    max_deliver=3,  # Max redelivery attempts
)
```

---

## Service Integration Patterns | أنماط تكامل الخدمات

### Pattern 1: Adapter for Backward Compatibility | محول للتوافق مع الإصدارات السابقة

For services with existing NATS publishers, use an adapter pattern:

```python
from shared.events.publisher import EventPublisher, PublisherConfig

class NatsPublisher:
    """Adapter wrapping shared EventPublisher for backward compatibility."""

    def __init__(self, service_name: str = "my-service"):
        self._publisher: EventPublisher | None = None
        self._service_name = service_name

    async def connect(self, nats_url: str) -> bool:
        config = PublisherConfig(servers=[nats_url], name=self._service_name)
        self._publisher = EventPublisher(config=config, service_name=self._service_name)
        return await self._publisher.connect()

    async def publish_event(self, subject: str, event_type: str, payload: dict) -> bool:
        # Ensure sahool. prefix
        if not subject.startswith("sahool."):
            subject = f"sahool.{subject}"

        event = {
            "eventId": str(uuid4()),
            "eventType": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sourceService": self._service_name,
            "payload": payload,
        }
        return await self._publisher.publish_json(subject, event)
```

### Pattern 2: Direct EventPublisher Usage | الاستخدام المباشر

```python
from shared.events.publisher import EventPublisher, get_publisher, close_publisher

# In service startup
publisher = await get_publisher(
    service_name="advisory-service",
    service_version="16.0.0",
)

# In endpoint
await publisher.publish_event("sahool.advisory.generated", event)

# In service shutdown
await close_publisher()
```

### Pattern 3: FastAPI Lifespan Integration | تكامل FastAPI Lifespan

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from shared.events.publisher import EventPublisher, PublisherConfig
from shared.events.subscriber import EventSubscriber, SubscriberConfig

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    publisher_config = PublisherConfig(name=app.title)
    app.state.publisher = EventPublisher(config=publisher_config)
    await app.state.publisher.connect()

    subscriber_config = SubscriberConfig(name=f"{app.title}-subscriber")
    app.state.subscriber = EventSubscriber(config=subscriber_config)
    await app.state.subscriber.connect()

    yield

    # Shutdown
    await app.state.publisher.close()
    await app.state.subscriber.close()

app = FastAPI(title="my-service", lifespan=lifespan)
```

---

## Dead Letter Queue (DLQ) | قائمة انتظار الرسائل الفاشلة

### Configuration | التكوين

```python
config = SubscriberConfig(
    enable_dlq=True,
    max_dlq_size=10000,
    dlq_retention_days=7,
)
```

### DLQ Message Format | تنسيق رسالة DLQ

```json
{
    "original_subject": "sahool.field.created",
    "original_data": "...",
    "error": "Processing failed: database timeout",
    "failed_at": "2026-01-26T10:30:00Z",
    "retry_count": 3,
    "service": "field-service"
}
```

### Reprocessing DLQ Messages | إعادة معالجة رسائل DLQ

```python
# Get DLQ statistics
stats = subscriber.get_dlq_stats()
print(f"DLQ messages: {stats['count']}")

# Reprocess failed messages
reprocessed = await subscriber.reprocess_dlq(
    max_messages=100,
    handler=handle_field_event,
)
```

---

## Security Configuration | تكوين الأمان

### Authorization | التفويض

NATS authorization is configured in `config/nats/nats.conf`:

```conf
authorization {
    default_permissions = {
        publish = {
            allow = ["sahool.>", "_INBOX.>"]
            deny = ["$SYS.>", "$JS.API.STREAM.DELETE.>", "$JS.API.CONSUMER.DELETE.>"]
        }
        subscribe = {
            allow = ["sahool.>", "_INBOX.>"]
            deny = ["$SYS.>"]
        }
    }
}
```

### User Roles | أدوار المستخدمين

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | Full access (`>`) | Administrative tasks |
| **App User** | `sahool.>`, `field.>`, etc. | Service-to-service communication |
| **Monitor** | Subscribe only, no publish | Read-only monitoring |

### Environment Variables | متغيرات البيئة

```bash
# Required for NATS connection
NATS_URL=nats://localhost:4222
NATS_USER=service_user
NATS_PASSWORD=secure_password

# JetStream configuration
JETSTREAM_DOMAIN=sahool

# Service identification
SERVICE_NAME=my-service
```

---

## Monitoring & Observability | المراقبة والرصد

### Health Endpoint Integration | تكامل نقطة الصحة

```python
@app.get("/readyz")
async def readiness():
    health = await app.state.subscriber.health_check()

    if health["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health)

    return {
        "status": "ok",
        "nats": health["status"],
        "details": health["details"],
    }
```

### Prometheus Metrics | مقاييس Prometheus

```python
from prometheus_client import Counter, Gauge

# Publisher metrics
nats_publish_total = Counter(
    "nats_publish_total",
    "Total NATS messages published",
    ["service", "subject"],
)

nats_publish_errors = Counter(
    "nats_publish_errors_total",
    "Total NATS publish errors",
    ["service", "subject", "error_type"],
)

# Subscriber metrics
nats_subscribe_total = Counter(
    "nats_subscribe_total",
    "Total NATS messages received",
    ["service", "subject"],
)

nats_dlq_size = Gauge(
    "nats_dlq_size",
    "Current DLQ message count",
    ["service"],
)
```

### Logging | التسجيل

```python
import structlog

logger = structlog.get_logger()

# Publish logging
logger.info(
    "event_published",
    subject="sahool.field.created",
    event_id=event.event_id,
    service="field-service",
)

# Error logging
logger.error(
    "publish_failed",
    subject="sahool.field.created",
    error=str(e),
    retry_count=3,
)
```

---

## Testing | الاختبار

### Unit Tests | اختبارات الوحدة

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_publish_event():
    publisher = EventPublisher()
    publisher._nc = AsyncMock()
    publisher._connected = True

    result = await publisher.publish_json("sahool.test", {"data": "test"})

    assert result is True
    publisher._nc.publish.assert_called_once()
```

### Integration Tests | اختبارات التكامل

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_pubsub_integration():
    received = []

    async def handler(msg):
        received.append(json.loads(msg.data))
        await msg.ack()

    subscriber = EventSubscriber()
    await subscriber.connect()
    await subscriber.subscribe("sahool.test.>", handler)

    publisher = EventPublisher()
    await publisher.connect()
    await publisher.publish_json("sahool.test.event", {"value": 42})

    await asyncio.sleep(0.1)
    assert len(received) == 1
    assert received[0]["value"] == 42
```

---

## Troubleshooting | استكشاف الأخطاء وإصلاحها

### Common Issues | المشاكل الشائعة

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection timeout | NATS server unreachable | Check NATS_URL, network connectivity |
| Permission denied | Invalid credentials | Verify NATS_USER/NATS_PASSWORD |
| Subject not allowed | Authorization restriction | Check subject matches allowed patterns |
| JetStream not available | JS not enabled | Enable JetStream in nats.conf |
| DLQ overflow | Too many failed messages | Increase max_dlq_size or reprocess DLQ |

### Debug Commands | أوامر التصحيح

```bash
# Check NATS server status
nats server info

# List streams
nats stream list

# View stream info
nats stream info SAHOOL_EVENTS

# Check consumer status
nats consumer info SAHOOL_EVENTS my-consumer

# View DLQ messages
nats stream view SAHOOL_DLQ

# Publish test message
nats pub sahool.test.ping '{"test": true}'

# Subscribe to all events
nats sub "sahool.>"
```

---

## Migration Guide | دليل الترحيل

### From Custom Publisher to Shared EventPublisher

1. **Replace imports**:
```python
# Before
from my_service.nats import NatsPublisher

# After
from shared.events.publisher import EventPublisher, PublisherConfig
```

2. **Update initialization**:
```python
# Before
publisher = NatsPublisher(nats_url="nats://localhost:4222")
await publisher.connect()

# After
config = PublisherConfig(servers=["nats://localhost:4222"])
publisher = EventPublisher(config=config, service_name="my-service")
await publisher.connect()
```

3. **Update publish calls**:
```python
# Before
await publisher.publish("field.created", data)

# After (ensure sahool. prefix)
await publisher.publish_json("sahool.field.created", data)
```

---

## Best Practices | أفضل الممارسات

1. **Always use sahool. prefix** for subjects to ensure proper authorization
2. **Enable JetStream** for reliable message delivery and persistence
3. **Implement health checks** for Kubernetes readiness probes
4. **Use DLQ** to capture and reprocess failed messages
5. **Set appropriate timeouts** for publish operations
6. **Use durable consumers** for reliable subscription
7. **Monitor DLQ size** to detect processing issues early
8. **Use structured logging** for debugging and observability
9. **Test with mocked NATS** for unit tests, real NATS for integration tests
10. **Version your events** to support backward compatibility

---

## Related Documentation | الوثائق ذات الصلة

<<<<<<< HEAD
- [Event Architecture](./EVENT_ARCHITECTURE.md)
- [Service Communication](./SERVICE_COMMUNICATION.md)
=======
- [Event Catalog](./EVENT_CATALOG.md)
- [Data Flow](./DATA_FLOW.md)
>>>>>>> 32fd5d55beabbbf36de4006c89fcda63cab80473
- [Deployment Guide](./DEPLOYMENT.md)
- [Security Guide](./SECURITY.md)
- [Monitoring & Observability](./OBSERVABILITY.md)

---

_Last Updated: January 2026_
