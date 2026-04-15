# 03 · FastAPI Stateless Compute Template

**Gold standard:** `apps/services/irrigation-smart/`
**Use when:** the service has **no database**, performs calculations
on request, and optionally emits events with the result.
Typical examples: ET₀ / water-balance calculators, NDVI aggregators,
rule engines.

> قالب للخدمات التي لا تمتلك قاعدة بيانات — حسابات صافية تعمل عند
> الطلب وتنشر نتائجها عبر NATS.

---

## Why `irrigation-smart`?

- Pure compute — no persistence, no ORM, no migrations.
- Clean domain separation: `models.py` (Pydantic DTOs) →
  `calculator.py` (formulas) → `main.py` (HTTP glue).
- Short cold-start (<0.5 s) — ideal for autoscaling.
- Deterministic: the same input always produces the same output so
  integration tests don't need a real DB.
- Still publishes `sahool.irrigation.*` events for downstream
  consumers.

Another reasonable pick: `vegetation-analysis-service` (Sentinel Hub
NDVI computation).

---

## Delta from Pattern 02

This pattern reuses **almost every section** of
[`02-pattern-fastapi-crud.md`](./02-pattern-fastapi-crud.md). Only the
following items change:

### Bootstrap — remove the DB pool

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # No DB; just NATS (optional)
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        app.state.nc = await nats.connect(nats_url, name="<service>")
        app.state.nats_connected = True

    yield

    if getattr(app.state, "nc", None):
        await app.state.nc.drain()
        await app.state.nc.close()
```

### Readiness probe

```python
@app.get("/readyz")
async def readyz():
    # No DB to check; NATS is optional (degraded mode is OK for compute).
    return {"status": "ok", "nats": getattr(app.state, "nats_connected", False)}
```

### No migrations, no Prisma

Delete:
- `prisma/` directory
- `DATABASE_URL` / `DATABASE_URL_DIRECT` env vars
- `models.py` SQLAlchemy / asyncpg queries

Keep `models.py` for Pydantic request/response types only.

### Idempotency

Stateless services are naturally idempotent **on the request level**,
but if you publish events you must still deduplicate on the consumer
side using the `eventId`. Don't add an `IdempotencyKey` table — let the
consumer own the dedup state.

### Caching

Because every request is a pure function of its inputs, read-through
Redis caching is strongly recommended for expensive calls. Example:
`irrigation-smart`'s water-balance endpoint caches by
`(tenant_id, field_id, date)` with a 6-hour TTL.

---

## Dockerfile differences

- Base image stays `python:3.11-slim-bookworm`.
- `HEALTHCHECK` hits `/healthz` (no DB probe needed).
- Drop `prisma` / `asyncpg` / SQLAlchemy from `requirements.txt`.
- Typical image size: **~80 MB** (vs ~200 MB for a CRUD service).

---

## Scaling notes

Stateless services **scale horizontally with no coordination** —
Kubernetes HPA on CPU works perfectly. Do NOT add sticky sessions.
If the service takes a long time per request (> 5 s), switch to a
queue-worker pattern (pattern 07 below) instead of keeping the HTTP
connection open.

---

## Coverage matrix

| Service | Stateless? | Pure function | NATS publish | Cache-first | Integration tests |
|---|---|---|---|---|---|
| irrigation-smart | ✅ gold | ✅ | ✅ | ✅ | partial |
| vegetation-analysis-service | ✅ | ✅ (NDVI calc) | ✅ | ✅ | — |
| indicators-service | ✅ | ✅ | ✅ | — | — |
| lai-estimation | ✅ | ✅ | — | — | — |
| crop-growth-model | ✅ | ✅ | ✅ | — | — |
| agro-rules | ✅ | ✅ (rules engine) | — | — | — |
