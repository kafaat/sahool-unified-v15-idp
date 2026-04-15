---
title: "SAHOOL v16.0.0 — Complete Platform Guide"
version: "16.0.0"
date: "2026-04-02"
author: "SAHOOL Platform Team"
---

# SAHOOL v16.0.0 — Complete Platform Guide

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Quick Start Guide](#quick-start-guide)
4. [Developer Guide](#developer-guide)
5. [DevOps Guide](#devops-guide)
6. [Security Guide](#security-guide)
7. [Troubleshooting](#troubleshooting)
8. [API Reference](#api-reference)
9. [Glossary](#glossary)

---

## Executive Summary

SAHOOL v16.0.0 is a production-ready, enterprise-grade multi-tenant SaaS platform for smart agriculture. It provides complete tenant isolation across all infrastructure layers: database, cache, storage, and events.

### Key Metrics

| Metric              | Value           |
|---------------------|-----------------|
| Services            | 72 microservices|
| Platform Health     | 80.5/100        |
| Tenant Isolation    | 100% enforced   |
| Test Coverage       | 25% (target)    |
| CI/CD Workflows     | 73              |
| Deployment Time     | < 10 minutes    |

### Critical Features

- ✅ **Zero Trust Security** — Every operation verified
- ✅ **Automatic Tenant Isolation** — RLS, key prefixing, bucket isolation
- ✅ **Context Propagation** — HTTP → Events → Workers → Database
- ✅ **Observability** — Per-tenant metrics, logs, traces
- ✅ **Billing & Metering** — Usage tracking per tenant
- ✅ **Disaster Recovery** — Point-in-time recovery per tenant

---

## Architecture Overview

### Multi-Layer Tenant Isolation

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 7: Application (Your Code)                           │
│  • FastAPI / NestJS controllers                             │
│  • Business logic                                           │
│  • Domain services                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  LAYER 6: Platform SDK (shared/platform.py)                 │
│  • TenantRepository — Auto RLS enforcement                  │
│  • TenantRedis — Auto key prefixing                         │
│  • TenantStorage — Auto bucket isolation                    │
│  • TenantNATSPublisher — Auto header injection              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  LAYER 5: Context System (RequestContext)                    │
│  • JWT/Header extraction                                    │
│  • Context propagation                                      │
│  • Validation & enforcement                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  LAYER 4: Infrastructure                                    │
│  • PostgreSQL + RLS                                         │
│  • Redis (tenant-prefixed)                                  │
│  • MinIO/S3 (tenant-bucket)                                 │
│  • NATS (tenant headers)                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  LAYER 3: Kubernetes                                        │
│  • Pod isolation                                            │
│  • Network policies                                         │
│  • Service mesh (mTLS)                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  LAYER 2: API Gateway (Kong)                                │
│  • JWT validation                                           │
│  • Rate limiting                                            │
│  • Request routing                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│  LAYER 1: Client                                            │
│  • Mobile app (Flutter)                                     │
│  • Web dashboard                                            │
│  • IoT devices                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow with Tenant Context

```
Client Request
    ↓
Kong (JWT validation)
    ↓
Service A (ContextMiddleware extracts tenant)
    ↓
Database Query (RLS: SET app.current_tenant = 't-123')
    ↓
Redis Cache (Key: t-123:service:resource:key)
    ↓
Storage Upload (Bucket: sahool-tenant-{hash})
    ↓
Event Publish (NATS Headers: Nats-Tenant-ID: t-123)
    ↓
Worker B (Restores context from headers)
    ↓
Database Query (RLS enforces tenant isolation)
```

---

## Quick Start Guide

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/kafaat/sahool-unified-v15-idp.git
cd sahool-unified-v15-idp

# Install dependencies
pip install -r requirements.txt
npm install  # For TypeScript services

# Start infrastructure
docker-compose up -d postgres redis minio nats

# Run migrations
python scripts/migrate.py up

# Verify installation
python scripts/verify-installation.py
```

### 2. Create Your First Service

```python
# apps/services/my-service/main.py
from fastapi import FastAPI
from shared.platform import (
    ContextMiddleware, tenant_db, TenantRepository,
    TenantRedis, TenantCache, TenantMetrics
)

app = FastAPI()
app.add_middleware(ContextMiddleware, service_name='my-service')

# Initialize services
redis = TenantRedis(redis_client, 'my-service')
cache = TenantCache(redis)
metrics = TenantMetrics('my-service')

# Define repository
class MyModelRepository(TenantRepository):
    _table = 'my_models'
    _model_class = MyModel

@app.get("/items")
async def list_items():
    """Automatic tenant isolation — no manual tenant_id handling"""
    return await cache.get_or_set(
        'items',
        lambda: MyModelRepository().find_many(),
        ttl=300
    )

@app.post("/items")
async def create_item(data: ItemCreate):
    """Automatic tenant_id injection"""
    item = await MyModelRepository().create({
        'name': data.name,
        'value': data.value
        # tenant_id auto-injected by repository
    })

    await cache.invalidate('items')
    return item
```

### 3. Deploy to Staging

```bash
# Build and deploy
sahool-cli deploy \
    --service my-service \
    --version 1.0.0 \
    --environment staging \
    --verify-isolation

# Verify deployment
sahool-cli verify \
    --environment staging \
    --service my-service
```

---

## Developer Guide

### Core Principle: Never Handle `tenant_id` Manually

**❌ WRONG — Manual tenant handling:**

```python
# NEVER DO THIS
@app.get("/fields")
async def list_fields(tenant_id: str):  # ❌ Manual parameter
    rows = await conn.fetch(
        "SELECT * FROM fields WHERE tenant_id = $1",  # ❌ Manual filter
        tenant_id
    )
    return rows
```

**✅ CORRECT — Automatic tenant isolation:**

```python
# CORRECT WAY
@app.get("/fields")
async def list_fields():  # ✅ No tenant parameter
    async with tenant_db() as conn:  # ✅ Context sets tenant
        rows = await conn.fetch("SELECT * FROM fields")  # ✅ RLS filters
        return rows
```

### Context Access Patterns

```python
from shared.platform import (
    get_current_context,      # Get full context
    get_current_tenant_id,    # Get tenant ID only
    has_context,              # Check if context exists
    require_context           # Decorator for enforcement
)

# Pattern 1: Check context exists
if has_context():
    tenant_id = get_current_tenant_id()

# Pattern 2: Require context (raises if missing)
@require_context()
async def sensitive_operation():
    ctx = get_current_context()
    # ...

# Pattern 3: Require specific role
@require_context(allowed_roles=[UserRole.ADMIN, UserRole.SUPER_ADMIN])
async def admin_only_operation():
    # ...

# Pattern 4: System operations (no user context)
from shared.platform import create_system_context, ContextManager

async def background_job():
    system_ctx = create_system_context('background-service')
    with ContextManager(system_ctx):
        # Can access database as system
        async with tenant_db() as conn:
            ...
```

### Repository Patterns

```python
from shared.platform import TenantRepository

# Basic CRUD
class FieldRepository(TenantRepository):
    _table = 'fields'
    _model_class = Field

repo = FieldRepository()

# Create — tenant_id auto-injected
field = await repo.create({
    'name': 'North Field',
    'area': 150.5
})

# Read — RLS filters automatically
fields = await repo.find_many(area__gt=100)
single = await repo.find_one('field-uuid')

# Update — RLS ensures tenant can only update own data
updated = await repo.update('field-uuid', {'name': 'Updated Name'})

# Delete — RLS ensures tenant can only delete own data
deleted = await repo.delete('field-uuid')
```

### Cache Patterns

```python
from shared.platform import TenantRedis, TenantCache

redis = TenantRedis(redis_client, 'my-service')
cache = TenantCache(redis)

# Pattern 1: Cache-aside
data = await cache.get_or_set(
    'expensive-query',
    lambda: expensive_database_query(),
    ttl=300
)

# Pattern 2: Explicit cache operations
await redis.set('session', 'user-123', {'logged_in': True}, ttl=3600)
session = await redis.get('session', 'user-123')

# Pattern 3: Cache invalidation
await redis.delete('cache', 'expensive-query')
```

### Event Publishing Patterns

```python
from shared.platform import TenantNATSPublisher, SubjectBuilder

publisher = TenantNATSPublisher(nats_client, 'my-service')

# Pattern 1: Simple event
await publisher.publish(
    'field.created',
    {'field_id': '123', 'name': 'North Field'}
)
# Headers automatically include tenant context

# Pattern 2: Structured subject
await publisher.publish(
    SubjectBuilder.build('agriculture', 'field', 'created'),
    {'field_id': '123'}
)
# Subject: sahool.agriculture.t_123abc.field.created

# Pattern 3: Cross-service communication
await publisher.publish(
    'billing.invoice.generate',
    {'field_id': '123', 'usage': 150.5},
    event_type='invoice.generate'
)
```

### Storage Patterns

```python
from shared.platform import TenantStorage

storage = TenantStorage('http://minio:9000', 'key', 'secret')

# Upload with automatic tenant isolation
result = await storage.upload(
    path='fields/123/photo.jpg',
    data=file_bytes,
    content_type='image/jpeg',
    metadata={'field_id': '123'}
)

# Generate presigned URL
url = await storage.get_url('fields/123/photo.jpg', expires=3600)

# Download with tenant verification
data = await storage.download('fields/123/photo.jpg')
# Raises TenantIsolationError if object belongs to different tenant
```

---

## DevOps Guide

### Deployment Pipeline

```
Commit → Lint & Test → Build Images → Deploy Staging
                                          ↓
                                     Integration Tests
                                          ↓
                                      Load Tests
                                          ↓
                                  Deploy Production
                                          ↓
                                  Verify Isolation
```

### CLI Commands

```bash
# Deploy service
sahool-cli deploy \
    --service field-service \
    --version 16.0.1 \
    --environment production \
    --replicas 5 \
    --verify-isolation

# Run load tests
sahool-cli load-test \
    --environment production \
    --duration 300 \
    --tenants 50 \
    --requests-per-tenant 1000 \
    --verify-isolation

# Analyze performance
sahool-cli analyze-performance \
    --environment production \
    --output report.json

# Auto-scale based on load
sahool-cli auto-scale \
    --environment production

# Rollback
sahool-cli rollback \
    --service field-service \
    --to-version 16.0.0 \
    --environment production
```

### Kubernetes Configuration

```yaml
# k8s/base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: "{{SERVICE_NAME}}"
  labels:
    app: "{{SERVICE_NAME}}"
    tenant-isolation: "enabled"
    version: "{{VERSION}}"
spec:
  replicas: "{{REPLICAS}}"
  selector:
    matchLabels:
      app: "{{SERVICE_NAME}}"
  template:
    metadata:
      labels:
        app: "{{SERVICE_NAME}}"
        version: "{{VERSION}}"
    spec:
      securityContext:
        runAsNonRoot: true
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: "{{SERVICE_NAME}}"
          image: "sahool/{{SERVICE_NAME}}:{{VERSION}}"
          env:
            - name: SAHOOL_TENANT_ISOLATION
              value: "enabled"
            - name: SAHOOL_RLS_ENFORCED
              value: "true"
            - name: SAHOOL_SERVICE_NAME
              value: "{{SERVICE_NAME}}"
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
```

### Monitoring & Alerting

```yaml
# prometheus/alerts.yml
groups:
  - name: tenant_isolation
    rules:
      - alert: TenantIsolationBreach
        expr: |
          sum by (tenant_id) (
            sahool_requests_total{status=~"403|500"}
          ) > 100
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Potential tenant isolation breach"

      - alert: HighTenantLatency
        expr: |
          histogram_quantile(0.95,
            sahool_request_duration_seconds_bucket
          ) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High latency for tenant {{ $labels.tenant }}"
```

---

## Security Guide

### Tenant Isolation Verification

```python
# scripts/verify-isolation.py
from shared.platform import tenant_db, TenantRedis, TenantStorage

async def verify_complete_isolation():
    """Verify all layers have tenant isolation"""

    # 1. Database RLS
    async with tenant_db() as conn:
        try:
            await conn.execute("RESET app.current_tenant")
            await conn.fetch("SELECT * FROM fields")
            print("❌ DATABASE: RLS bypass possible!")
        except Exception:
            print("✅ DATABASE: RLS enforced")

    # 2. Redis isolation
    redis = TenantRedis(redis_client, 'test')
    try:
        await redis.get('test', 'key')
        print("❌ REDIS: No context required!")
    except ContextRequiredError:
        print("✅ REDIS: Context required")

    # 3. Storage isolation
    storage = TenantStorage('...', 'key', 'secret')
    try:
        await storage.download('test.txt')
        print("❌ STORAGE: No context required!")
    except ContextRequiredError:
        print("✅ STORAGE: Context required")
```

### Security Checklist

- [ ] RLS enabled on all tenant tables
- [ ] `FORCE ROW LEVEL SECURITY` on all tables
- [ ] No direct DB connections outside SDK
- [ ] Redis keys prefixed with tenant
- [ ] Storage buckets isolated per tenant
- [ ] NATS headers include tenant context
- [ ] JWT validation at API Gateway
- [ ] mTLS between services
- [ ] Audit logging enabled
- [ ] Rate limiting per tenant

---

## Troubleshooting

### Issue: "No request context" error

**Symptoms:**
```
ContextRequiredError: No request context. Use ContextManager or middleware.
```

**Solution:**
```python
# Ensure middleware is first
app = FastAPI()
app.add_middleware(ContextMiddleware, service_name='my-service')  # MUST be first

# Or use ContextManager for background tasks
async def background_job():
    system_ctx = create_system_context('my-service')
    with ContextManager(system_ctx):
        # Your code here
        pass
```

### Issue: Cross-tenant data visible

**Symptoms:** Tenant A sees data from Tenant B.

**Diagnosis:**
```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity, forcerowsecurity
FROM pg_tables WHERE schemaname = 'public';

-- Check policy exists
SELECT * FROM pg_policies WHERE tablename = 'fields';
```

**Solution:**
```sql
-- Enable RLS
ALTER TABLE fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE fields FORCE ROW LEVEL SECURITY;

-- Recreate policy
DROP POLICY IF EXISTS tenant_isolation_fields ON fields;
CREATE POLICY tenant_isolation_fields ON fields
USING (tenant_id = current_setting('app.current_tenant', true)
       OR current_setting('app.is_super_admin', true) = 'true');
```

### Issue: Cache returns wrong tenant data

**Symptoms:** Cache hit returns data from different tenant.

**Diagnosis:**
```python
# Check key generation
ctx = get_current_context()
expected_key = f"{ctx.tenant_id}:my-service:cache:my-key"
actual_key = redis._get_key("cache", "my-key")
assert expected_key == actual_key
```

**Solution:** Ensure `TenantRedis` is used, not raw Redis client.

---

## API Reference

### Key Classes

| Class                   | Purpose                    | File                |
|-------------------------|----------------------------|---------------------|
| `RequestContext`        | Tenant context container   | `shared/platform.py`|
| `ContextManager`       | Context lifecycle manager  | `shared/platform.py`|
| `tenant_db()`          | Database access            | `shared/platform.py`|
| `TenantRepository`     | Base repository            | `shared/platform.py`|
| `TenantRedis`          | Redis client               | `shared/platform.py`|
| `TenantStorage`        | Object storage             | `shared/platform.py`|
| `TenantNATSPublisher`  | Event publisher            | `shared/platform.py`|
| `TenantMetrics`        | Metrics collection         | `shared/platform.py`|
| `UsageMeter`           | Billing metering           | `shared/platform.py`|

See `docs/API_REFERENCE.md` for complete API documentation.

---

## Glossary

| Term    | Definition                                                              |
|---------|-------------------------------------------------------------------------|
| Tenant  | A customer/organization using the platform                              |
| RLS     | Row Level Security — PostgreSQL feature for row-level access control    |
| Context | Request-scoped container for tenant, user, trace info                   |
| SDK     | Software Development Kit — reusable code libraries                      |
| mTLS    | Mutual TLS — encrypted service-to-service communication                 |
| PITR    | Point-in-Time Recovery — database restore capability                    |

---

## Support

- **Documentation:** https://docs.sahool.dev
- **Slack:** #sahool-platform
- **Issues:** https://github.com/kafaat/sahool/issues
- **Emergency:** platform-oncall@sahool.dev
