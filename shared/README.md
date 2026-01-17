# SAHOOL Shared Libraries (Python)

## Overview

مكتبات Python المشتركة للخدمات الخلفية.

---

## Structure

```
shared/
├── __init__.py
│
├── contracts/              # API and Event Contracts
│   ├── ai/                 # AI prompt templates
│   │   └── prompt_templates/
│   ├── events/             # Event schemas
│   │   ├── base.py
│   │   ├── publisher.py
│   │   ├── consumer.py
│   │   └── *.v1.json       # Event JSON schemas
│   ├── openapi/            # OpenAPI specs
│   └── schemas/            # JSON schemas
│
├── domain/                 # Domain models
│   ├── auth/               # Authentication
│   │   └── passwords.py
│   ├── tenancy/            # Multi-tenancy
│   │   ├── models.py
│   │   └── service.py
│   └── users/              # User management
│       ├── models.py
│       └── service.py
│
├── events/                 # Event definitions
│   ├── models.py
│   └── schemas/            # Event JSON schemas
│       ├── audit_logged.v1.json
│       ├── chat_message_sent.v1.json
│       ├── device_status.v1.json
│       ├── fertilizer_plan_issued.v1.json
│       ├── irrigation_adjustment.v1.json
│       ├── ndvi_anomaly.v1.json
│       ├── ndvi_computed.v1.json
│       ├── recommendation_issued.v1.json
│       ├── sensor_reading.v1.json
│       └── weather_alert.v1.json
│
├── libs/                   # Utility libraries
│   ├── audit/              # Audit logging
│   │   ├── hashchain.py    # Hash chain integrity
│   │   ├── middleware.py   # Audit middleware
│   │   ├── models.py       # Audit models
│   │   ├── redact.py       # PII redaction
│   │   └── service.py      # Audit service
│   │
│   ├── events/             # Event handling
│   │   ├── envelope.py     # Event envelope
│   │   ├── producer.py     # Event producer
│   │   └── schema_registry.py
│   │
│   ├── outbox/             # Outbox pattern
│   │   ├── models.py
│   │   ├── publisher.py
│   │   └── alembic/        # Migrations
│   │
│   ├── security/           # Security utilities
│   │   ├── tls.py          # TLS helpers
│   │   └── vault_client.py # Vault integration
│   │
│   ├── caching.py          # Redis caching
│   ├── database.py         # Database utilities
│   └── pagination.py       # Pagination helpers
│
├── middleware/             # FastAPI middleware
│   ├── cors.py             # CORS configuration
│   ├── rate_limit.py       # Rate limiting
│   ├── request_size.py     # Request size limits
│   └── tenant_context.py   # Tenant context
│
├── monitoring/             # Monitoring
│   └── metrics.py          # Prometheus metrics
│
├── observability/          # Observability
│   ├── endpoints.py        # Health endpoints
│   ├── health.py           # Health checks
│   ├── logging.py          # Structured logging
│   └── metrics.py          # Metrics export
│
├── security/               # Security
│   ├── config.py           # Security config
│   ├── deps.py             # FastAPI dependencies
│   ├── guard.py            # Permission guard
│   ├── jwt.py              # JWT handling
│   ├── policy_engine.py    # Policy engine
│   ├── rbac.py             # Role-based access
│   ├── token_revocation.py # Token blacklist
│   ├── audit.py            # Audit logging
│   ├── audit_models.py     # Audit models
│   └── tests/              # Security tests
│
└── templates/              # Service templates
    └── service_template.py # Base service template
```

---

## Modules

### contracts/events

Event-driven messaging contracts:

```python
from shared.contracts.events.base import BaseEvent
from shared.contracts.events.publisher import EventPublisher

# Define event
class FieldCreated(BaseEvent):
    field_id: str
    tenant_id: str
    geometry: dict

# Publish event
publisher = EventPublisher()
await publisher.publish("field.created.v1", event)
```

### domain

Domain models and services:

```python
from shared.domain.users.service import UserService
from shared.domain.tenancy.service import TenancyService

# User operations
user = await user_service.get_by_id(user_id)

# Tenant context
tenant = await tenancy_service.get_current()
```

### libs/audit

Audit logging with hash chain:

```python
from shared.libs.audit.service import AuditService
from shared.libs.audit.redact import redact_pii

# Log action
await audit.log(
    action="field.created",
    actor_id=user.id,
    resource_id=field.id,
    details=redact_pii(details)
)
```

### libs/events

Event production and schema validation:

```python
from shared.libs.events.producer import EventProducer
from shared.libs.events.envelope import EventEnvelope

producer = EventProducer(nats_client)
envelope = EventEnvelope(
    event_type="ndvi.computed.v1",
    data={"field_id": "...", "value": 0.75}
)
await producer.publish(envelope)
```

### libs/outbox

Transactional outbox pattern:

```python
from shared.libs.outbox.publisher import OutboxPublisher

# Within transaction
async with db.transaction():
    await db.insert(field)
    await outbox.schedule(
        event_type="field.created.v1",
        payload=field.dict()
    )
```

### middleware

FastAPI middleware:

```python
from shared.middleware.cors import get_cors_middleware
from shared.middleware.rate_limit import RateLimitMiddleware
from shared.middleware.tenant_context import TenantContextMiddleware

app.add_middleware(get_cors_middleware())
app.add_middleware(RateLimitMiddleware)
app.add_middleware(TenantContextMiddleware)
```

### security

Authentication and authorization:

```python
from shared.security.jwt import create_access_token, verify_token
from shared.security.rbac import require_permission
from shared.security.guard import PermissionGuard

# JWT operations
token = create_access_token({"sub": user.id})
claims = verify_token(token)

# Permission check
@require_permission("fields:write")
async def create_field(...):
    pass
```

### observability

Metrics and health checks:

```python
from shared.observability.health import HealthCheck
from shared.observability.metrics import MetricsMiddleware

# Health endpoint
@app.get("/health")
async def health():
    return await HealthCheck().run()

# Metrics
app.add_middleware(MetricsMiddleware)
```

---

## Event Schemas

Events follow versioned JSON schemas:

| Event                       | Schema                  |
| --------------------------- | ----------------------- |
| `audit_logged.v1`           | Audit log entry         |
| `chat_message_sent.v1`      | Chat message            |
| `device_status.v1`          | IoT device status       |
| `fertilizer_plan_issued.v1` | Fertilization plan      |
| `irrigation_adjustment.v1`  | Irrigation change       |
| `ndvi_anomaly.v1`           | NDVI anomaly detected   |
| `ndvi_computed.v1`          | NDVI computation result |
| `recommendation_issued.v1`  | System recommendation   |
| `sensor_reading.v1`         | Sensor data             |
| `weather_alert.v1`          | Weather alert           |

---

## Installation

```bash
# Add to requirements.txt
-e ../shared

# Or install editable
pip install -e shared/
```

---

## Testing

```bash
# Run security tests
pytest shared/security/tests/

# All tests
pytest shared/
```

---

## Related Documentation

- [Services Map](../docs/SERVICES_MAP.md)
- [Architecture Principles](../docs/architecture/PRINCIPLES.md)

---

<p align="center">
  <sub>SAHOOL Shared Libraries</sub>
  <br>
  <sub>December 2025</sub>
</p>
