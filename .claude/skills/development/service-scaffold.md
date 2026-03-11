# Service Scaffold Skill | مهارة إنشاء الخدمات

## Purpose

Scaffold new microservices following SAHOOL platform conventions. This skill generates
production-ready service boilerplate for both Python FastAPI and Node.js NestJS services,
including Docker configuration, event integration, health endpoints, and platform registration.

---

## Pre-Scaffold Checklist

Before generating a new service, confirm the following:

| Step | Detail |
|------|--------|
| **Service Name** | kebab-case (e.g., `soil-mapping-service`). Must be unique across `governance/services.yaml`. |
| **Port Assignment** | Reserve a port in `packages/shared-types/src/contracts/service-ports.ts` via `SERVICE_PORTS`. |
| **Event Layer** | Choose one: `acquisition`, `intelligence`, `decision`, or `business`. |
| **Technology** | Python FastAPI (recommended for AI/data services) or Node.js NestJS (recommended for CRUD/real-time). |
| **Domain** | The NATS event domain slug (e.g., `soil`, `vision`, `irrigation`). |
| **Description** | One-line English and Arabic description for the service registry. |

---

## Python FastAPI Service Template

### Directory Structure

```
apps/services/{service-name}/
├── Dockerfile
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── {resource}.py
│   └── events/
│       ├── __init__.py
│       ├── publishers.py
│       └── subscribers.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_{resource}.py
```

### main.py (Lifespan Pattern)

```python
import os
import json
from contextlib import asynccontextmanager

import asyncpg
import nats
import structlog
from fastapi import FastAPI

from shared.errors_py import add_request_id_middleware, setup_exception_handlers

logger = structlog.get_logger()

SERVICE_NAME = "{service-name}"
SERVICE_VERSION = "16.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting_service", service=SERVICE_NAME, version=SERVICE_VERSION)

    # Database connection pool
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
        app.state.db_connected = True
        logger.info("database_connected")
    else:
        app.state.db_pool = None
        app.state.db_connected = False

    # NATS connection
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        app.state.nc = await nats.connect(nats_url)
        app.state.nats_connected = True
        logger.info("nats_connected")
    else:
        app.state.nc = None
        app.state.nats_connected = False

    yield

    # Shutdown
    if app.state.db_pool:
        await app.state.db_pool.close()
    if app.state.nc:
        await app.state.nc.close()
    logger.info("service_stopped", service=SERVICE_NAME)


app = FastAPI(
    title=SERVICE_NAME,
    version=SERVICE_VERSION,
    lifespan=lifespan,
)

setup_exception_handlers(app)
add_request_id_middleware(app)


@app.get("/healthz")
def health():
    return {"status": "ok", "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get("/readyz")
def readiness():
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }
```

### API Endpoint Example

```python
from fastapi import APIRouter, Depends
from shared.auth.dependencies import get_current_user
from shared.auth.models import User

router = APIRouter(prefix="/api/v1/{resource}", tags=["{resource}"])


@router.get("/")
async def list_items(user: User = Depends(get_current_user)):
    return {"items": [], "total": 0}
```

### NATS Event Publishing

```python
import json

async def publish_event(nc, domain: str, action: str, payload: dict):
    subject = f"sahool.{domain}.{action}"
    await nc.publish(subject, json.dumps(payload).encode())
```

### requirements.txt

```
fastapi>=0.135.1,<1.0.0
uvicorn[standard]>=0.34.0,<1.0.0
asyncpg>=0.31.0,<1.0.0
nats-py>=2.6.0,<3.0.0
pydantic>=2.10.0,<3.0.0
structlog>=24.0.0,<25.0.0
```

Install with: `pip install --no-cache-dir -c constraints.txt -r requirements.txt`

---

## Node.js NestJS Service Template

### Directory Structure

```
apps/services/{service-name}/
├── Dockerfile
├── package.json
├── tsconfig.json
├── prisma/
│   ├── schema.prisma
│   └── seed.ts
├── src/
│   ├── index.ts
│   ├── app.module.ts
│   ├── app.controller.ts
│   ├── {resource}/
│   │   ├── {resource}.module.ts
│   │   ├── {resource}.controller.ts
│   │   └── {resource}.service.ts
│   └── __tests__/
│       └── {resource}.spec.ts
└── tests/
    └── app.e2e-spec.ts
```

### package.json (Key Fields)

```json
{
  "name": "@sahool/{service-name}",
  "version": "16.0.0",
  "private": true,
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "lint": "eslint src/",
    "test": "vitest",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@nestjs/core": "^10.0.0",
    "@nestjs/common": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "@prisma/client": "^5.0.0",
    "@sahool/nestjs-auth": "workspace:*",
    "@sahool/shared-types": "workspace:*"
  }
}
```

### tsconfig.json

```json
{
  "extends": "@sahool/typescript-config/tsconfig.nestjs.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

---

## Docker Configuration

### Python Dockerfile (Multi-Stage, Pattern A Mirrors)

```dockerfile
# Stage 1: Base
FROM python:3.11-slim-bookworm AS base

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_RETRIES=10 \
    PYTHONUNBUFFERED=1

RUN groupadd -g 1000 sahool && useradd -u 1000 -g sahool -m sahool

WORKDIR /app

# Stage 2: Builder
FROM base AS builder

COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    --index-url https://pypi.org/simple \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com \
    -c constraints.txt -r requirements.txt || \
    pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://mirrors.cloud.tencent.com/pypi/simple \
    --trusted-host mirrors.cloud.tencent.com \
    -c constraints.txt -r requirements.txt

# Stage 3: Production
FROM base AS production

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src/ ./src/
COPY shared/ /app/shared/

USER sahool
EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:{port}/healthz')"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "{port}"]
```

### Node.js Dockerfile

```dockerfile
FROM node:20-slim AS base
RUN groupadd -g 1000 sahool && useradd -u 1000 -g sahool -m sahool
WORKDIR /app

FROM base AS builder
COPY package.json package-lock.json ./
RUN npm config set registry https://registry.npmmirror.com && \
    npm install --legacy-peer-deps || \
    (npm config set registry https://registry.npmjs.org && npm install --legacy-peer-deps)
COPY . .
RUN npm run build

FROM base AS production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
USER sahool
EXPOSE {port}

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:{port}/healthz', r => { process.exit(r.statusCode === 200 ? 0 : 1) })"

CMD ["node", "dist/index.js"]
```

---

## Registration Steps

After scaffolding the service files, complete these registration steps:

### 1. docker-compose.yml

```yaml
{service-name}:
  build:
    context: .
    dockerfile: apps/services/{service-name}/Dockerfile
  ports:
    - "{port}:{port}"
  environment:
    - DATABASE_URL=${DATABASE_URL}
    - NATS_URL=nats://nats:4222
    - REDIS_URL=redis://redis:6379
    - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    - ENVIRONMENT=${ENVIRONMENT:-development}
  depends_on:
    - postgres
    - nats
    - redis
  networks:
    - sahool-network
```

### 2. governance/services.yaml

```yaml
- name: {service-name}
  port: {port}
  type: {python|nodejs}
  layer: {acquisition|intelligence|decision|business}
  owner: KAFAAT
  status: active
  description: "{English description}"
  description_ar: "{Arabic description}"
```

### 3. packages/shared-types/src/contracts/service-ports.ts

```typescript
export const SERVICE_PORTS = {
  // ... existing ports
  {SERVICE_NAME_UPPER}: {port},
} as const;
```

### 4. Backstage Catalog (idp/catalog/)

Create `{service-name}.yaml`:

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: {service-name}
  description: "{description}"
  annotations:
    backstage.io/techdocs-ref: dir:.
spec:
  type: service
  lifecycle: production
  owner: kafaat
  providesApis:
    - {service-name}-api
```

### 5. API Definition (idp/catalog/apis/)

Create `{service-name}-api.yaml`:

```yaml
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: {service-name}-api
  description: "{service-name} REST API"
spec:
  type: openapi
  lifecycle: production
  owner: kafaat
  definition:
    $text: ./openapi/{service-name}.yaml
```

### 6. CI Workflow (.github/workflows/ci-{service-name}.yml)

```yaml
name: CI - {Service Name}
on:
  push:
    paths:
      - 'apps/services/{service-name}/**'
  pull_request:
    paths:
      - 'apps/services/{service-name}/**'
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Lint
        run: ruff check apps/services/{service-name}/
      - name: Test
        run: pytest apps/services/{service-name}/tests/ -v
      - name: Docker Build
        run: docker build -f apps/services/{service-name}/Dockerfile .
```

---

## Post-Scaffold Verification

Run these checks after scaffolding is complete:

```bash
# 1. Health check passes
curl -s http://localhost:{port}/healthz | jq .
# Expected: {"status": "ok", "service": "{service-name}", "version": "16.0.0"}

# 2. Lint passes
# Python
ruff check apps/services/{service-name}/
# Node.js
cd apps/services/{service-name} && npm run lint

# 3. Tests pass
# Python
pytest apps/services/{service-name}/tests/ -v
# Node.js
cd apps/services/{service-name} && npm test

# 4. Docker build succeeds
docker build -f apps/services/{service-name}/Dockerfile .
```

---

## Quick Reference

| Parameter | Convention |
|-----------|-----------|
| Service name | kebab-case, suffix with `-service` |
| Python version | 3.11 |
| Node.js version | 20 |
| Platform version | 16.0.0 |
| Base user | sahool (UID 1000) |
| Health endpoint | `/healthz` (liveness), `/readyz` (readiness) |
| API prefix | `/api/v1/{resource}` |
| Event subject | `sahool.{domain}.{action}` |
| Pip mirrors | PyPI -> Aliyun -> Tencent (Pattern A) |
| npm mirror | npmmirror.com -> npmjs.org |
