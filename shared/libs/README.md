# shared/libs - SAHOOL Shared Libraries

Common infrastructure libraries used across all SAHOOL microservices. Provides
foundational patterns for audit logging, event publishing, caching, database
management, pagination, and security.

**Version**: 16.0.0 | **Python**: >= 3.11

---

## Components

### audit/ - Tamper-Evident Audit Trail

Append-only audit logging with SHA-256 hash chain for tamper detection. Every
write links to the previous entry's hash, forming a chain that breaks if any
record is altered. PII fields are automatically redacted before storage.

Files: `models.py`, `service.py`, `hashchain.py`, `middleware.py`, `redact.py`

```python
from shared.libs.audit import write_audit_log, query_audit_logs, verify_chain

# Write an audit entry (within a SQLAlchemy session)
entry = write_audit_log(
    db=session,
    tenant_id=tenant_id,
    actor_id=user_id,
    actor_type="user",           # "user" | "service" | "system"
    action="field.create",       # dot-separated domain.action
    resource_type="field",
    resource_id=str(field.id),
    correlation_id=correlation_id,
    ip=request.client.host,
    details={"name": field.name, "area_ha": 8.5},
)

# Query audit history for a resource
logs = query_audit_logs(
    db=session,
    tenant_id=tenant_id,
    resource_type="field",
    resource_id=str(field.id),
    limit=50,
)

# Verify chain integrity (offline forensics)
is_valid, errors = verify_chain(iter(raw_entries))
```

The `AuditContextMiddleware` automatically propagates `correlation_id`, IP,
and user agent from FastAPI requests into the audit context.

**Table**: `audit_logs` with composite indexes on `(tenant_id, created_at)`,
`(resource_type, resource_id)`, `(actor_id, created_at)`, and `correlation_id`.

---

### outbox/ - Transactional Outbox Pattern

Guarantees at-least-once event delivery by writing events to a local database
table within the same transaction as business data, then publishing them
asynchronously. Prevents event loss when the message bus is temporarily
unavailable.

Files: `models.py`, `publisher.py`

```python
from shared.libs.outbox import OutboxEvent, EventBusClient, publish_pending
from shared.libs.events import EventEnvelope

# Write an outbox event within a business transaction
envelope = EventEnvelope(
    event_type="field.created",
    tenant_id=tenant_id,
    correlation_id=correlation_id,
    schema_ref="events.field.created:v1",
    producer="field-management-service",
    payload={"field_id": str(field.id), "name": field.name},
)
event = OutboxEvent(
    event_type="field.created",
    schema_ref="events.field.created:v1",
    tenant_id=tenant_id,
    correlation_id=correlation_id,
    payload_json=json.dumps(envelope.to_json_dict()),
)
session.add(event)
session.commit()   # Atomic with business data change

# Background worker: publish pending events to NATS/Kafka
class NATSBusClient(EventBusClient):
    def publish(self, topic: str, message: str) -> None:
        nc.publish(topic, message.encode())
    def close(self) -> None:
        nc.close()

published = publish_pending(db=session, bus=NATSBusClient(), batch_size=100)
```

`publish_pending()` respects a `max_retries` limit and records `last_error`
for failed attempts. `get_failed_events()` and `retry_failed_events()` support
manual remediation.

---

### events/ - Event Envelope & Schema Registry

Standard envelope that wraps all event payloads, plus a NATS publisher and
schema validation registry for the field-first event architecture.

Files: `envelope.py`, `schema_registry.py`, `nats_publisher.py`, `producer.py`

```python
from shared.libs.events import EventEnvelope, NATSPublisher, NATSConfig

# Build a typed event envelope
envelope = EventEnvelope(
    event_type="analysis.completed",
    tenant_id=tenant_id,
    correlation_id=correlation_id,
    schema_ref="events.analysis.completed:v1",
    producer="vegetation-analysis-service",
    payload={"field_id": "...", "ndvi": 0.72},
)

# Publish directly via NATS
publisher = NATSPublisher(NATSConfig(url="nats://nats:4222"))
await publisher.connect()
await publisher.publish(envelope)

# Convenience helper
from shared.libs.events import publish_analysis_completed
await publish_analysis_completed(field_id="...", tenant_id="...", ndvi=0.72)
```

`NATS_AVAILABLE` is a module-level flag; if `nats-py` is not installed the
NATS symbols are set to `None` and the registry still functions.

---

### caching.py - Redis + In-Memory Cache

Unified caching layer with Redis primary and in-memory fallback. Supports TTL,
pattern-based invalidation, and a `@cached` decorator.

```python
from shared.libs.caching import (
    CacheConfig, CacheManager, get_cache_manager, cached,
    invalidate_field_cache, invalidate_tenant_cache,
)

# Global manager (auto-configured from ENV)
cache = get_cache_manager()
await cache.set("field:abc", field_data, ttl=600)
value = await cache.get("field:abc")
await cache.delete("field:abc")
await cache.invalidate_pattern("field:abc:*")

# Decorator - auto-generates key from function name + args hash
@cached(key_func=lambda field_id: f"field:{field_id}", ttl=600)
async def get_field(field_id: str) -> dict:
    return await db.fetch_field(field_id)

# Domain helpers
await invalidate_field_cache("field-uuid")
await invalidate_tenant_cache("tenant-uuid")
```

Redis URL is read from `REDIS_URL`. Falls back to in-memory if Redis is
unavailable or not configured. Key prefix defaults to `sahool:`.

---

### database.py - Async Database Pool Manager

SQLAlchemy async engine with `QueuePool`, connection health checks, exponential
backoff retries, FastAPI lifespan integration, and pool status reporting.

```python
from shared.libs.database import (
    DatabaseConfig, DatabaseManager, init_db, close_db,
    get_db_session, database_lifespan,
)

# FastAPI app with managed DB lifecycle
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)

# FastAPI dependency injection
@app.get("/fields")
async def list_fields(session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(Field))
    return result.scalars().all()

# Pool status
manager = get_db_manager()
status = await manager.get_pool_status()
# {"size": 20, "checked_in": 18, "checked_out": 2, "overflow": 0}
```

---

### pagination.py - Cursor & Offset Pagination

Two pagination strategies with streaming support for large result sets.

```python
from shared.libs.pagination import (
    OffsetPage, Page, PaginationHelper, Cursor,
    create_pagination_params, StreamingResponse,
)

# Offset-based (for admin/reporting queries)
page = OffsetPage(
    items=results,
    total=total_count,
    page=1,
    page_size=50,
    total_pages=PaginationHelper.calculate_total_pages(total_count, 50),
)
response = page.to_dict()  # includes pagination.has_next, has_previous

# Cursor-based (for large/append-heavy datasets)
cursor = Cursor.encode("2025-01-20T10:00:00Z")  # base64-encoded
decoded = Cursor.decode(cursor)

# FastAPI dependency
@app.get("/events")
async def list_events(params=Depends(create_pagination_params)):
    offset = PaginationHelper.calculate_offset(params["page"], params["page_size"])
    ...

# Streaming NDJSON for very large exports
async def generate():
    async for item in db.stream_all_records():
        yield item

return StreamingResponse.stream_ndjson(generate())
```

---

### security/ - TLS and Vault Integration

mTLS context builder and HashiCorp Vault client with AppRole authentication
and Vault-to-ENV fallback for secrets migration.

Files: `tls.py`, `vault_client.py`

```python
from shared.libs.security import VaultClient, vault_from_env, build_mtls_ssl_context

# Auto-configure from environment variables
client = vault_from_env()
# Requires: VAULT_ADDR + (VAULT_TOKEN or VAULT_ROLE_ID + VAULT_SECRET_ID)

# Read a secret (KV v2)
db_creds = client.read_kv("database/postgres")
db_url = f"postgresql://{db_creds['username']}:{db_creds['password']}@..."

# Dynamic database credentials via Vault DB secrets engine
creds = client.read_database_creds(role="field-management-service")

# Vault-first with ENV fallback (useful during migration)
api_key = client.get_secret_or_env(
    vault_path="services/advisory",
    vault_key="api_key",
    env_var="ADVISORY_API_KEY",
)

# mTLS context for service-to-service calls
ssl_ctx = build_mtls_ssl_context(TlsConfig(
    ca_cert="/certs/ca.pem",
    client_cert="/certs/service.crt",
    client_key="/certs/service.key",
))
```

For testing use `MockVaultClient(secrets={"secret/database/postgres": {...}})`.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | required | PostgreSQL connection URL |
| `DB_POOL_SIZE` | `20` | SQLAlchemy pool size |
| `DB_MAX_OVERFLOW` | `10` | Pool overflow connections |
| `DB_POOL_TIMEOUT` | `30` | Pool checkout timeout (seconds) |
| `DB_POOL_RECYCLE` | `3600` | Connection recycle interval (seconds) |
| `DB_MAX_RETRIES` | `3` | Database retry attempts |
| `REDIS_URL` | `None` | Redis connection URL (optional) |
| `CACHE_ENABLED` | `true` | Enable/disable caching |
| `CACHE_TTL_SECONDS` | `300` | Default cache TTL |
| `CACHE_MAX_SIZE` | `10000` | In-memory cache max entries |
| `CACHE_KEY_PREFIX` | `sahool:` | Cache key namespace prefix |
| `VAULT_ADDR` | `http://localhost:8200` | HashiCorp Vault address |
| `VAULT_TOKEN` | `None` | Vault root/service token |
| `VAULT_ROLE_ID` | `None` | AppRole role ID |
| `VAULT_SECRET_ID` | `None` | AppRole secret ID |

---

## File Reference

| File/Directory | Description |
|---------------|-------------|
| `audit/models.py` | `AuditLog` SQLAlchemy model (append-only) |
| `audit/service.py` | `write_audit_log`, `query_audit_logs` |
| `audit/hashchain.py` | SHA-256 hash chain computation & verification |
| `audit/middleware.py` | `AuditContextMiddleware` for FastAPI |
| `audit/redact.py` | PII redaction for audit details |
| `outbox/models.py` | `OutboxEvent` SQLAlchemy model |
| `outbox/publisher.py` | `EventBusClient` ABC, `publish_pending` |
| `events/envelope.py` | `EventEnvelope` Pydantic model |
| `events/schema_registry.py` | `SchemaRegistry` for event validation |
| `events/nats_publisher.py` | `NATSPublisher`, convenience helpers |
| `caching.py` | `CacheManager`, `RedisCache`, `@cached` decorator |
| `database.py` | `DatabaseManager`, `get_db_session`, `database_lifespan` |
| `pagination.py` | `OffsetPage`, `Page`, `Cursor`, `StreamingResponse` |
| `security/tls.py` | `build_mtls_ssl_context`, `TlsConfig` |
| `security/vault_client.py` | `VaultClient`, `vault_from_env`, `MockVaultClient` |
