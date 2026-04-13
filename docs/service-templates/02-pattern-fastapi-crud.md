# 02 · FastAPI CRUD Service Template

**Gold standard:** `apps/services/notification-service/`
**Use when:** Python service that owns tenant data in Postgres, exposes
HTTP REST, subscribes to NATS events and publishes its own.

> القالب الذهبي لخدمات Python FastAPI التي تدير بيانات دائمة وتشترك
> في أحداث NATS.

---

## Why `notification-service`?

- Full NATS subscriber with **DLQ** (`nats_subscriber.py` +
  `shared/events/dlq_*`).
- Multi-channel delivery (push, email, SMS, in-app) with retry and
  delivery tracking (`delivery_tracker.py`).
- Structured `structlog` logging throughout.
- OTP flow demonstrates security-sensitive code patterns (rate limits,
  cryptographic nonces).
- Bilingual templates (`preferences_service.py`, `history_controller.py`).
- Scheduler (`notification_scheduler.py`) shows periodic background
  tasks pattern.

If a simpler starter is needed, `alert-service` is a good second pick
(smaller surface, same conventions).

---

## Canonical directory layout

```
apps/services/<service-name>/
├── Dockerfile                         # python:3.11-slim-bookworm, multi-stage
├── .dockerignore
├── requirements.txt
├── pyproject.toml                     # [tool.ruff], [tool.pytest.ini_options]
├── README.md                          # bilingual Purpose · Architecture · API · Events · Ops
└── src/
    ├── __init__.py
    ├── main.py                        # FastAPI app + lifespan — see §"Bootstrap"
    ├── database.py                    # asyncpg pool lifecycle
    ├── models.py                      # Pydantic request/response schemas
    ├── <domain>_controller.py         # one APIRouter per aggregate
    ├── <domain>_service.py            # pure business logic, no HTTP types
    ├── nats_subscriber.py             # NATS subscribe + DLQ + retry
    ├── nats_publisher.py              # outgoing events
    ├── scheduler.py                   # APScheduler / asyncio tasks
    ├── queue_processor.py             # if using Redis/NATS queues
    └── tests/
        ├── unit/
        ├── integration/
        └── conftest.py
```

**Rule of thumb:** one `*_controller.py` + one `*_service.py` pair per
aggregate. No generic `routes/` or `services/` god-directories.

---

## Bootstrap (`src/main.py`)

```python
import os
from contextlib import asynccontextmanager

import asyncpg
import nats
import structlog
from fastapi import FastAPI

from shared.errors_py import add_request_id_middleware, setup_exception_handlers
from shared.logging_config import configure_structlog
from shared.middleware.rate_limiter import setup_rate_limiter
from shared.monitoring.metrics import PrometheusMiddleware, metrics_endpoint

configure_structlog(service_name="<service>")
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────────
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
        app.state.db_connected = True
        logger.info("db_pool_ready")

    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            app.state.nc = await nats.connect(nats_url, name="<service>")
            app.state.nats_connected = True
            logger.info("nats_connected", url=nats_url)
            # subscribers
            from .nats_subscriber import start_subscription
            app.state.subscriber = await start_subscription(app)
        except Exception as exc:
            logger.warning("nats_degraded", error=str(exc))
            app.state.nats_connected = False

    yield

    # ── Shutdown ───────────────────────────────────────────────────
    if getattr(app.state, "subscriber", None):
        await app.state.subscriber.drain()
    if getattr(app.state, "nc", None):
        await app.state.nc.drain()
        await app.state.nc.close()
    if getattr(app.state, "db_pool", None):
        await app.state.db_pool.close()
    logger.info("shutdown_complete")


app = FastAPI(
    title="<Service>",
    version="16.0.0",
    lifespan=lifespan,
    # OpenAPI in development only
    openapi_url="/openapi.json" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Cross-cutting middleware — ORDER MATTERS:
#   1. request-id  (so all other middleware can log it)
#   2. structured logging
#   3. CORS
#   4. rate-limit
#   5. auth
#   6. prometheus
add_request_id_middleware(app)
setup_exception_handlers(app)        # unified error envelope
setup_rate_limiter(app)
app.add_middleware(PrometheusMiddleware)

from . import <domain>_controller     # noqa: E402  routers imported last
app.include_router(<domain>_controller.router, prefix="/api/v1/<domain>")

# Health probes NEVER under /api/v1
@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "<service>", "version": "16.0.0"}


@app.get("/readyz")
async def readyz():
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats":     getattr(app.state, "nats_connected", False),
    }


app.add_api_route("/metrics", metrics_endpoint, include_in_schema=False)
```

---

## Database — `src/database.py`

```python
import asyncpg

async def get_pool(app) -> asyncpg.Pool:
    return app.state.db_pool


async def get_connection(app):
    async with app.state.db_pool.acquire() as conn:
        yield conn
```

Tenant scoping is **not optional** — every query takes `tenant_id` as the
first filter:

```python
rows = await conn.fetch(
    "SELECT id, name FROM notifications WHERE tenant_id = $1 AND status = $2",
    tenant_id, status,
)
```

For multi-statement writes, always use `async with conn.transaction():`.

---

## Events

### Publishing

Use `shared/events/subjects.py` constants + the `EventPublisher` helper:

```python
from shared.events.publisher import EventPublisher
from shared.events.subjects import SAHOOL_NOTIFICATION_SENT

publisher = EventPublisher(app.state.nc)
await publisher.publish(
    SAHOOL_NOTIFICATION_SENT,
    payload={"notification_id": n.id, "tenant_id": n.tenant_id, ...},
)
```

### Subscribing

Canonical pattern in `notification-service/src/nats_subscriber.py` —
copy the structure: connect → `subscribe(subject=..., queue="<service>-<domain>")`
→ dispatch → DLQ on failure.

```python
async def handle_message(msg: nats.aio.msg.Msg):
    try:
        payload = json.loads(msg.data.decode())
        await process(payload)
        await msg.ack()
    except Exception as exc:
        logger.error("handler_failed", subject=msg.subject, error=str(exc))
        await publish_to_dlq(msg, reason=str(exc))
        await msg.term()      # don't re-deliver — DLQ replay-er will.
```

Every subscriber uses a **queue group** named `<service>-<consumer>` so
parallel replicas load-balance instead of each receiving the same message.

---

## Auth & tenant isolation

```python
from shared.auth.dependencies import get_current_user
from shared.auth.models import User

@router.post("/")
async def create(
    dto: CreateNotificationDTO,
    user: User = Depends(get_current_user),
):
    return await service.create(tenant_id=user.tenant_id, user_id=user.id, dto=dto)
```

- Never read `tenant_id` from the request body.
- `get_current_user` validates JWT signature + expiration + revocation
  (Redis look-up).

---

## Error handling

All handlers return the unified envelope via `shared/errors_py.py`:

```python
{
  "success": false,
  "error": "Human-readable English message",
  "error_ar": "الرسالة بالعربية",
  "code": "E4001",                  # stable error code from shared/errors_py.ERROR_CODES
  "requestId": "...",               # from x-request-id
  "traceId": "..."                  # OTel trace id
}
```

Don't raise `HTTPException(status_code=400, detail="bad")` — raise a
domain exception subclass and let the handler format the envelope.

---

## Testing

```
tests/
├── unit/
│   ├── conftest.py             # fixture: mock asyncpg pool, mock nats
│   ├── test_<domain>_service.py
│   └── test_models.py
├── integration/
│   ├── conftest.py             # fixture: testcontainers Postgres + NATS
│   └── test_<domain>_flow.py   # real HTTP + real DB + real NATS
└── smoke/
    └── test_import.py          # `from src.main import app` — catches startup bugs
```

Pytest markers (already enforced in `pyproject.toml` root):

```python
@pytest.mark.unit         # fast, no I/O
@pytest.mark.integration  # real deps
@pytest.mark.smoke        # imports only
@pytest.mark.slow         # > 5 s
```

---

## Dockerfile skeleton (copy from notification-service)

```dockerfile
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bookworm AS base
WORKDIR /app
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_DEFAULT_TIMEOUT=300 PIP_RETRIES=10

FROM base AS builder
COPY requirements.txt .
# 3-tier mirror fallback — see CLAUDE.md §"Pip Mirror Configuration"
RUN pip install --index-url https://pypi.org/simple -r requirements.txt \
 || pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt \
 || pip install -i https://mirrors.cloud.tencent.com/pypi/simple --trusted-host mirrors.cloud.tencent.com -r requirements.txt

FROM base AS production
RUN groupadd -g 1000 sahool && useradd -m -u 1000 -g 1000 sahool
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --chown=sahool:sahool src/ /app/src/
USER sahool
EXPOSE 8110
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8110/healthz')" || exit 1
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8110"]
```

---

## Coverage matrix

| Service | Pattern 02? | DB pool lifecycle | NATS sub + DLQ | structlog | OTel | /metrics | Integration tests | Last audit |
|---|---|---|---|---|---|---|---|---|
| notification-service | ✅ gold | ✅ asyncpg | ✅ DLQ | ✅ | ✅ | ✅ | 28 | 2026-04 |
| alert-service | ✅ | ✅ SQLAlchemy | ✅ | ✅ | ⚠️ | ✅ | — | — |
| audit-service | ✅ | ✅ asyncpg | ✅ | ✅ | — | ✅ | — | — |
| task-service | ✅ | ✅ asyncpg | ✅ | ✅ | — | ✅ | — | — |
| equipment-service | ✅ | ✅ SQLAlchemy | ✅ | — | — | — | — | — |
| crop-intelligence-service | ✅ | ✅ asyncpg | ✅ | ✅ | ⚠️ | ✅ | — | — |
| advisory-service | ✅ (in-memory KB) | — | ✅ | ✅ | — | ✅ | — | — |
| billing-core | ✅ | ✅ asyncpg | ✅ | ✅ | — | — | — | — |
| cooperative-service | ✅ | — | ✅ | ⚠️ | — | — | — | — |
