---
name: service-scaffolding
description: Use when creating a new SAHOOL microservice under apps/services/. Enforces the IDP template, lifespan pattern, 3-tier pip mirror, non-root container, contract registration, and governance entry. Triggers when the user says "create a new service", "scaffold a service", "add a microservice", or when a PR adds a new apps/services/* directory.
---

# Service Scaffolding — SAHOOL

You are acting as a platform engineer scaffolding a new SAHOOL microservice. This skill encodes the end-to-end checklist so nothing is forgotten.

## Pre-flight (always run first)

1. **Confirm the stack** with the user: Python FastAPI or Node.js NestJS.
2. **Confirm the port** does not collide:
   - Read `packages/shared-types/src/contracts/service-ports.ts`
   - Read `governance/services.yaml`
   - If the port is taken, stop and ask for a different one.
3. **Confirm the name** is not a revived deprecated service:
   - Check `archive/deprecated-services/`
   - Check `governance/DEDUP_MATRIX.md`
   - If it matches a deprecated name, stop and ask the user to pick a different name or explicitly confirm they want to revive it (which is almost always wrong).
4. **Choose the event-architecture layer** for the service:
   - Acquisition (data ingestion) — sensors, satellites, weather
   - Intelligence (feature extraction) — ML, indicators, NDVI
   - Decision (recommendations) — advisory, crop growth, irrigation
   - Business (user-facing operations) — notifications, marketplace, chat
   Record this — it affects the NATS subject namespace and placement in `governance/services.yaml`.

## Python (FastAPI) scaffold

### File layout

```
apps/services/<service-name>/
├── Dockerfile
├── requirements.txt
├── README.md                      # bilingual EN/AR, like other services
├── .dockerignore
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI entry, lifespan pattern
│   ├── config.py                  # pydantic-settings, env vars
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── <resource>.py
│   ├── events/                    # NATS handlers
│   │   ├── __init__.py
│   │   └── subscribers.py
│   └── domain/
│       ├── __init__.py
│       └── models.py
└── tests/
    ├── __init__.py
    ├── test_health.py
    └── test_<resource>.py
```

### `src/main.py` template

Follow the lifespan pattern documented in `CLAUDE.md`:

```python
import os
from contextlib import asynccontextmanager

import asyncpg
import nats
import structlog
from fastapi import Depends, FastAPI

from shared.auth.dependencies import get_current_user
from shared.auth.models import User
from shared.errors_py import add_request_id_middleware, setup_exception_handlers

logger = structlog.get_logger()

SERVICE_NAME = "<service-name>"
SERVICE_VERSION = "16.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("service_starting", service=SERVICE_NAME)

    db_url = os.getenv("DATABASE_URL")
    if db_url:
        app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
        app.state.db_connected = True
    else:
        app.state.db_pool = None
        app.state.db_connected = False

    nats_url = os.getenv("NATS_URL")
    if nats_url:
        app.state.nc = await nats.connect(nats_url)
        app.state.nats_connected = True
    else:
        app.state.nc = None
        app.state.nats_connected = False

    yield

    if getattr(app.state, "db_pool", None):
        await app.state.db_pool.close()
    if getattr(app.state, "nc", None):
        await app.state.nc.close()
    logger.info("service_stopped", service=SERVICE_NAME)


app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION, lifespan=lifespan)
setup_exception_handlers(app)
add_request_id_middleware(app)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/readyz")
def readyz():
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }


@app.get("/protected")
async def protected(user: User = Depends(get_current_user)):
    return {"user_id": user.id}
```

### Dockerfile (Pattern A — 3-tier mirror fallback)

```dockerfile
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd -r sahool && useradd -r -g sahool -u 1000 sahool

COPY requirements.txt constraints.txt ./

RUN pip install --no-cache-dir --timeout=600 --retries=5 \
      --index-url https://pypi.org/simple \
      --trusted-host pypi.org --trusted-host files.pythonhosted.org \
      -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
      -i https://mirrors.aliyun.com/pypi/simple/ \
      --trusted-host mirrors.aliyun.com \
      -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
      -i https://mirrors.cloud.tencent.com/pypi/simple \
      --trusted-host mirrors.cloud.tencent.com \
      -c constraints.txt -r requirements.txt

COPY --chown=sahool:sahool src/ ./src/

USER sahool
EXPOSE <PORT>

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:<PORT>/healthz')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "<PORT>"]
```

## Node.js (NestJS) scaffold

Copy `idp/templates/node-service/` and apply these tweaks:
- NPM mirror fallback: `npm config set registry https://registry.npmmirror.com` with fallback to `https://registry.npmjs.org`
- `npm install --legacy-peer-deps`
- Prisma client generated in build stage; schema in `prisma/schema.prisma`
- Non-root `sahool` user, HEALTHCHECK, multi-stage build
- Use `@nestjs/swagger` for OpenAPI; mount at `/docs`

## Registration (mandatory — do all of these)

1. **Service registry** — append to `governance/services.yaml`:
   ```yaml
   <service-name>:
     category: <acquisition|intelligence|decision|business>
     stack: <python|node>
     port: <PORT>
     version: 16.0.0
     owner: <team>
     description: <one-line summary>
     health: /healthz
     metrics: /metrics
     events:
       publishes: [sahool.<domain>.<action>]
       subscribes: [sahool.<domain>.<action>]
   ```

2. **Port contract** — `packages/shared-types/src/contracts/service-ports.ts`:
   ```typescript
   export const SERVICE_PORTS = {
     // ...existing
     <SERVICE_NAME_UPPER>: <PORT>,
   } as const;
   ```

3. **Contract version** — bump `CONTRACT_VERSION` in `packages/shared-types/src/contracts/index.ts` (patch for additive new port).

4. **Dart sync** — `npx tsx scripts/sync-contracts-to-dart.ts`.

5. **Docker Compose** — add to the appropriate file (`docker-compose.yml`, `docker-compose.prod.yml`, etc.).

6. **Kong route** — if the service is gateway-exposed, add the route under `infrastructure/gateway/kong/`.

7. **Helm chart** — scaffold `helm/<service-name>/` for K8s deployment (optional if not yet K8s-ready).

8. **CI workflow** — verify the service is picked up by the relevant workflow (`ci.yml` paths filter).

9. **Service doc** — create `apps/services-docs/<service-name>.md` with API endpoints, architecture, admin integration notes. Bilingual EN/AR.

## NATS subject namespace

Use the helpers from `shared/events/subjects.py`:

```python
from shared.events.subjects import get_tenant_subject

subject = get_tenant_subject(tenant_id, "<domain>", "<action>")
# → "sahool.tenant.<tid>.<domain>.<action>"
```

Register new subject constants in `shared/events/subjects.py` — do not use inline strings.

## Tests (minimum bar)

```
tests/test_health.py      — /healthz and /readyz return 200
tests/test_<resource>.py  — happy path + auth path for each endpoint
tests/smoke/test_import.py — verify `from src.main import app` works
```

Run `make test-unit` locally before committing.

## Security checklist

- [ ] No secrets in code (`git diff | grep -iE 'password|secret|token|key'` before commit)
- [ ] All env vars documented in `README.md`
- [ ] Input validation with Pydantic v2
- [ ] Rate limiting tier chosen (starter/professional/enterprise) — see CLAUDE.md → "Rate Limiting Tiers"
- [ ] RBAC enforced on all non-health endpoints via `get_current_user`
- [ ] Structured logging with request IDs (from `add_request_id_middleware`)
- [ ] Prometheus `/metrics` endpoint exposed
- [ ] OpenTelemetry traces wired via `shared/observability/`

## Done criteria

A new service is "done" only when:
1. Service runs green under `make health`.
2. `make test-python` (or `make test-node`) passes for the new service.
3. `governance/services.yaml` validates in CI.
4. Contract guard passes (use `contract-guard` subagent).
5. `apps/services-docs/<service-name>.md` is written.
6. At least one downstream consumer (web, admin, or mobile) has been updated to use the new service via contracts.

If any of these is missing, the service is **in progress**, not done.
