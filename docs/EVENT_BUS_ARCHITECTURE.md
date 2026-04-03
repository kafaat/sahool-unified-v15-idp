# SAHOOL Event Bus Architecture

## Overview

SAHOOL uses NATS JetStream as its core event bus for service-to-service communication, providing guaranteed delivery, replay capability, and work queue patterns.

## Naming Convention

```
sahool.{type}.{domain}.{action}.{version}
```

### Examples

- `sahool.events.user.created.v1`
- `sahool.commands.irrigation.start.v1`
- `sahool.registry.service.register.v1`
- `sahool.health.field-service.heartbeat.v1`
- `sahool.audit.user.login.v1`

## Streams

| Stream | Purpose | Retention | Max Age |
|--------|---------|-----------|---------|
| `SAHOOL_EVENTS` | Domain events (field, weather, IoT) | Limits | 30 days |
| `SAHOOL_COMMANDS` | Async command execution | Work queue | 7 days |
| `SAHOOL_REGISTRY` | Service discovery & registration | Limits | 1 hour |
| `SAHOOL_HEALTH` | Health checks & metrics | Limits | 24 hours |
| `SAHOOL_AUDIT` | Compliance & audit trail | Limits (immutable) | 7 years |

## Usage

### Python (Event Bus SDK)

```python
from platform_bootstrap.src.event_bus import SAHOOLEventBus

bus = await SAHOOLEventBus.get_instance()
await bus.connect("nats://nats:4222", "my-service")

# Publish an event
await bus.publish_event("field", "sensor-data.received", {"moisture": 45.2})

# Subscribe to events
async def handler(msg):
    data = json.loads(msg.data)
    print(f"Received: {data}")

await bus.subscribe_events("field", handler)
```

### Tenant-Scoped Events

Events can include a `tenant_id` for multi-tenant isolation:

```python
await bus.publish_event(
    "field", "created",
    {"field_id": "f-123", "name": "North Field"},
    tenant_id="t-456"
)
```

## Configuration

- **Development**: `config/nats/nats.conf` (no TLS, bcrypt passwords)
- **Production**: `config/nats/nats-secure.conf` (mTLS, NKey auth)
- **Streams**: `config/nats/streams/sahool-streams.yaml`

## Setup

```powershell
# Initialize event bus streams
.\scripts\setup-event-bus.ps1
```
