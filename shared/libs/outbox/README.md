# SAHOOL Outbox Library

> مكتبة الصندوق الصادر — نشر موثوق للأحداث عبر NATS

Transactional outbox pattern for reliable event publishing. Guarantees
that domain writes and event publishes either both happen or neither
happens — no more "the row was saved but the event never fired" (or
vice versa).

## Two APIs in this package

| API | Module | Table | Use for |
|-----|--------|-------|---------|
| **Canonical (recommended)** — asyncpg | `asyncpg_publisher`, `relay`, `message` | `outbox_messages` | New FastAPI services using asyncpg |
| Legacy — SQLAlchemy | `publisher`, `worker`, `models` | `outbox_events` | Services already built on SQLAlchemy |

New services should use the canonical asyncpg API documented below. The
SQLAlchemy API is preserved for backwards compatibility and tests.

## Canonical API — Quick Start

### 1. Apply the migration

Execute `shared/libs/outbox/migration.sql` against your service's
database (once). The DDL is idempotent (`CREATE TABLE IF NOT EXISTS`).

### 2. In your service lifespan

```python
from shared.libs.outbox import OutboxPublisher, OutboxRelay

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... db_pool / nats_client init ...
    app.state.outbox = OutboxPublisher()
    app.state.outbox_relay = OutboxRelay()
    await app.state.outbox_relay.start(app.state.db_pool, app.state.nc)
    yield
    await app.state.outbox_relay.stop()
```

### 3. Replace direct publishes with enqueue

**Before** — race condition possible (NATS publish can succeed after DB
write fails, or vice versa):

```python
await db.execute("INSERT INTO fields ...")
await nc.publish("sahool.field.created", payload)  # not atomic!
```

**After** — atomic via outbox:

```python
async with app.state.db_pool.acquire() as conn:
    async with conn.transaction():
        await conn.execute("INSERT INTO fields ...")
        await app.state.outbox.enqueue(
            conn,
            subject="sahool.field.created",
            payload={"field_id": "f-123"},
            tenant_id=tenant_id,
        )
# Both rows commit together. The relay will pick up and publish
# within ~1s (configurable via poll_interval_seconds).
```

## Delivery semantics

- **At-least-once**: the relay retries failed publishes forever (with
  `retry_count` incremented each attempt). Consumers must be idempotent.
- **Ordered within a single tenant** in steady state, but not strictly
  guaranteed under contention — `FOR UPDATE SKIP LOCKED` lets multiple
  relay replicas work in parallel.
- **No ordering across tenants**.

## Operational notes

- `idx_outbox_unpublished` is a partial index on unpublished rows, so
  the relay's poll query stays O(batch_size) regardless of table size.
- Clean up published rows periodically (e.g. nightly job) to keep the
  table small. A simple `DELETE FROM outbox_messages WHERE published_at
  < NOW() - INTERVAL '7 days'` is usually fine.
- To run multiple relay replicas, just start more instances. The
  `SKIP LOCKED` clause prevents double-publishing.

## Reference exemplar

See `apps/services/advisory-service/src/main.py` for the first wired
example. Other services can migrate mechanically by following the same
pattern.
