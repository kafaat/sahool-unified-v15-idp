# SAHOOL Shared Middleware | البرمجيات الوسيطة المشتركة

> Unified middleware collection for SAHOOL microservices

[![Python](https://img.shields.io/badge/python-3.11-green.svg)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://typescriptlang.org)

## Overview | نظرة عامة

This module provides a comprehensive collection of middleware components for both Python (FastAPI) and TypeScript (NestJS) services in the SAHOOL platform.

هذه الوحدة توفر مجموعة شاملة من مكونات البرمجيات الوسيطة لخدمات Python (FastAPI) و TypeScript (NestJS) في منصة سهول.

## Middleware Components | المكونات

| Middleware | Language | Purpose | الوصف |
|------------|----------|---------|-------|
| Request Logging | Python/TS | Structured JSON logging with correlation IDs | تسجيل منظم مع معرفات الارتباط |
| CORS | Python | Secure cross-origin configuration | تكوين CORS آمن |
| Rate Limiter | Python | Tiered API rate limiting with Redis | تحديد المعدل متعدد المستويات |
| Exception Handler | Python | Global error handling with bilingual messages | معالجة الأخطاء ثنائية اللغة |
| Health Check | Python | Kubernetes probes (liveness/readiness) | فحوصات Kubernetes |
| Tenant Context | Python | Multi-tenant isolation | عزل المستأجرين |

---

## Quick Start | البداية السريعة

### Python (FastAPI)

```python
from fastapi import FastAPI
from apps.services.shared.middleware import (
    setup_cors,
    setup_exception_handlers,
    setup_health_endpoints,
    setup_rate_limiting,
    RequestLoggingMiddleware,
    TenantContextMiddleware,
)

app = FastAPI(title="My Service", version="1.0.0")

# Setup middleware stack
setup_exception_handlers(app)
setup_cors(app)

app.add_middleware(RequestLoggingMiddleware, service_name="my-service")
app.add_middleware(TenantContextMiddleware, require_tenant=True)

# Setup rate limiting with Redis
limiter = setup_rate_limiting(app, use_redis=True)

# Setup health endpoints
health_mgr = setup_health_endpoints(app, service_name="my-service", version="1.0.0")
```

### TypeScript (NestJS)

```typescript
import { NestFactory } from '@nestjs/core';
import { RequestLoggingInterceptor } from './shared/middleware';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Add request logging interceptor
  app.useGlobalInterceptors(new RequestLoggingInterceptor('my-service'));

  await app.listen(3000);
}
```

---

## Middleware Details | تفاصيل البرمجيات الوسيطة

### 1. Request Logging | تسجيل الطلبات

**Files**: `request_logging.py`, `request-logging.ts`

Structured JSON logging with correlation tracking, sensitive data redaction, and performance metrics.

**Features**:
- Correlation ID propagation
- Tenant/User context logging
- Request/Response body logging (optional)
- Sensitive data redaction (passwords, tokens, API keys)
- Performance timing (ms)

**Configuration**:
```python
app.add_middleware(
    RequestLoggingMiddleware,
    service_name="my-service",
    log_request_body=False,
    log_response_body=False,
    exclude_paths=["/healthz", "/metrics"],
    max_body_length=1000
)
```

**Log Output**:
```json
{
  "timestamp": "2026-01-24T10:30:00.000Z",
  "service": "my-service",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "http": {
    "method": "POST",
    "path": "/api/v1/fields",
    "status_code": 201,
    "duration_ms": 145.23
  },
  "tenant_id": "farm-001",
  "user_id": "user-123"
}
```

---

### 2. CORS Middleware | البرمجيات الوسيطة CORS

**File**: `cors.py`

Secure cross-origin resource sharing configuration with environment-aware defaults.

**Configuration**:
```python
from apps.services.shared.middleware import setup_cors

setup_cors(
    app,
    allowed_origins=["https://app.sahool.io"],
    allow_credentials=True,
    allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allowed_headers=["Authorization", "Content-Type", "X-Tenant-ID"],
    max_age=3600
)
```

**Environment Variables**:
- `CORS_ORIGINS` - Comma-separated allowed origins
- `ENVIRONMENT` - Determines default origins

---

### 3. Rate Limiter | محدد المعدل

**File**: `rate_limiter.py`

Production-grade rate limiting with Redis support and tiered configuration.

**Rate Limit Tiers**:

| Tier | Requests/min | Requests/hour |
|------|-------------|---------------|
| FREE | 30 | 500 |
| STANDARD | 60 | 2,000 |
| PREMIUM | 120 | 5,000 |
| INTERNAL | 1,000 | 50,000 |
| UNLIMITED | - | - |

**Configuration**:
```python
from apps.services.shared.middleware import setup_rate_limiting

limiter = setup_rate_limiting(
    app,
    use_redis=True,
    redis_url="redis://localhost:6379",
    exclude_paths=["/healthz", "/metrics"]
)
```

**Environment Variables**:
```bash
RATE_LIMIT_FREE_RPM=30
RATE_LIMIT_STANDARD_RPM=60
RATE_LIMIT_PREMIUM_RPM=120
REDIS_URL=redis://localhost:6379
```

**Response Headers**:
- `X-RateLimit-Limit` - Request limit
- `X-RateLimit-Remaining` - Requests remaining
- `X-RateLimit-Reset` - Reset time (seconds)
- `Retry-After` - When exceeded

---

### 4. Exception Handler | معالج الاستثناءات

**File**: `exception_handler.py`

Global exception handling with consistent error responses and bilingual messages.

**Error Classes**:
```python
from apps.services.shared.middleware.exception_handler import (
    AppError,           # Base error
    ValidationError,    # 400
    AuthenticationError, # 401
    AuthorizationError,  # 403
    NotFoundError,       # 404
    ConflictError,       # 409
    RateLimitError,      # 429
    InternalError,       # 500
)
```

**Setup**:
```python
from apps.services.shared.middleware import setup_exception_handlers
setup_exception_handlers(app)
```

**Error Response Format**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "message_ar": "مدخل غير صحيح",
    "error_id": "a1b2c3d4",
    "details": {}
  }
}
```

---

### 5. Health Check | فحص الصحة

**File**: `health.py`

Kubernetes liveness and readiness probes with custom health checks.

**Endpoints**:
- `GET /healthz` - Liveness check
- `GET /livez` - Kubernetes liveness probe
- `GET /readyz` - Readiness check

**Configuration**:
```python
from apps.services.shared.middleware import setup_health_endpoints

health_mgr = setup_health_endpoints(
    app,
    service_name="my-service",
    version="1.0.0",
    include_livez=True,
    include_readyz=True
)

# Register custom health checks
health_mgr.register_check("database", create_database_check(db.ping))
health_mgr.register_check("redis", create_redis_check("redis://localhost:6379"))

# Control readiness
health_mgr.set_ready(False)  # Pause traffic
health_mgr.set_ready(True)   # Resume traffic
```

**Health Response**:
```json
{
  "status": "healthy",
  "service": "my-service",
  "version": "1.0.0",
  "uptime_seconds": 3600.5,
  "checks": [
    {
      "name": "database",
      "status": "healthy",
      "latency_ms": 2.5,
      "message": "Connection OK"
    }
  ]
}
```

---

### 6. Tenant Context | سياق المستأجر

**File**: `tenant_context.py`

Multi-tenant isolation and context management.

**Extraction Priority**:
1. JWT token claim (`tid`)
2. `X-Tenant-ID` header
3. Query parameter (`?tenant_id=`)

**Configuration**:
```python
from apps.services.shared.middleware import TenantContextMiddleware

app.add_middleware(
    TenantContextMiddleware,
    require_tenant=True,
    allow_query_param=False,
    exempt_paths=["/healthz", "/docs"]
)
```

**Usage in Routes**:
```python
from apps.services.shared.middleware.tenant_context import (
    get_current_tenant,
    get_current_tenant_id,
    tenant_filter,
)

@app.get("/fields")
async def list_fields(tenant: TenantContext = Depends(get_current_tenant)):
    # Tenant is automatically available
    return {"tenant_id": tenant.id}

# SQLAlchemy filter
query = session.query(Field).filter(tenant_filter(Field))
```

---

## Directory Structure | هيكل المجلدات

```
apps/services/shared/middleware/
├── __init__.py              # Exports all middleware
├── cors.py                  # CORS configuration
├── exception_handler.py     # Global error handling
├── health.py                # Health check endpoints
├── rate_limiter.py          # Rate limiting
├── request_logging.py       # Request logging (Python)
├── tenant_context.py        # Multi-tenant context
├── index.ts                 # TypeScript exports
├── request-logging.ts       # Request logging (TypeScript)
├── examples/
│   └── nestjs_example.ts    # NestJS integration example
└── README.md                # This file
```

---

## Integration Checklist | قائمة التكامل

### For New FastAPI Service

- [ ] Import from `apps.services.shared.middleware`
- [ ] Add `setup_exception_handlers(app)` for error handling
- [ ] Add `setup_cors(app)` for cross-origin support
- [ ] Add `RequestLoggingMiddleware` for observability
- [ ] Add `TenantContextMiddleware` for multi-tenancy
- [ ] Add `setup_rate_limiting(app)` for protection
- [ ] Add `setup_health_endpoints(app)` for Kubernetes probes
- [ ] Configure environment variables

### For New NestJS Service

- [ ] Import `RequestLoggingInterceptor` from shared middleware
- [ ] Register as global interceptor
- [ ] Set service name for logging context
- [ ] Use `StructuredLogger` in services
- [ ] Ensure correlation ID propagation

---

## Environment Variables | متغيرات البيئة

```bash
# General
ENVIRONMENT=development|staging|production
LOG_LEVEL=INFO|DEBUG

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate Limiting
REDIS_URL=redis://redis:6379
RATE_LIMIT_ENABLED=true
RATE_LIMIT_FREE_RPM=30
RATE_LIMIT_STANDARD_RPM=60
RATE_LIMIT_PREMIUM_RPM=120
RATE_LIMIT_INTERNAL_RPM=1000
```

---

## Related Documentation | التوثيق ذو الصلة

- [Request Logging Guide](../../../shared/middleware/REQUEST_LOGGING_GUIDE.md)
- [Rate Limiting Guide](../../../shared/middleware/RATE_LIMITING_GUIDE.md)
- [Implementation Summary](../../../shared/middleware/IMPLEMENTATION_SUMMARY.md)

---

## License | الترخيص

Proprietary - KAFAAT © 2026
