# SAHOOL Shared Middleware Guide
**دليل البرمجيات الوسيطة المشتركة لمنصة سهول**

## Overview | نظرة عامة

This guide covers the shared middleware libraries available across all SAHOOL services for consistent observability, security, and multi-tenancy support.

تغطي هذه الوثيقة مكتبات البرمجيات الوسيطة المشتركة المتاحة عبر جميع خدمات سهول لدعم متسق للمراقبة والأمان والتعدد المستأجرين.

---

## Table of Contents | جدول المحتويات

1. [Available Middleware](#available-middleware)
2. [Python FastAPI Integration](#python-fastapi-integration)
3. [TypeScript NestJS Integration](#typescript-nestjs-integration)
4. [Middleware Configuration](#middleware-configuration)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Available Middleware

### 1. RequestLoggingMiddleware
**Correlation IDs & Structured Logging**

- ✅ Generates or extracts correlation IDs (X-Correlation-ID)
- ✅ Logs all requests with structured JSON format
- ✅ Tracks request duration and status codes
- ✅ Extracts tenant and user IDs from headers or JWT
- ✅ Filters sensitive data (passwords, tokens, etc.)

**Location:**
- Python: `shared/middleware/request_logging.py`
- TypeScript: `apps/services/shared/middleware/request-logging.ts`

---

### 2. ObservabilityMiddleware
**Tracing, Metrics & Monitoring**

- ✅ OpenTelemetry distributed tracing support
- ✅ Automatic span creation for each request
- ✅ Prometheus metrics collection
- ✅ Error tracking and reporting
- ✅ Performance monitoring

**Location:**
- Python: `shared/observability/middleware.py`

---

### 3. TenantContextMiddleware
**Multi-Tenancy Isolation**

- ✅ Extracts tenant ID from JWT or headers
- ✅ Provides async-safe context for tenant isolation
- ✅ Tenant-scoped database query helpers
- ✅ Validates tenant presence on protected endpoints

**Location:**
- Python: `shared/middleware/tenant_context.py`

---

### 4. MetricsMiddleware
**HTTP Metrics Collection**

- ✅ Request counts by method and endpoint
- ✅ Response time histograms
- ✅ Active connection tracking
- ✅ Error rate monitoring

**Location:**
- Python: `shared/observability/middleware.py`

---

### 5. RateLimitMiddleware
**API Rate Limiting**

- ✅ Tiered rate limiting (by user, tenant, API key)
- ✅ Token bucket algorithm
- ✅ Redis-backed distributed rate limiting
- ✅ Customizable limits per endpoint

**Location:**
- Python: `shared/middleware/rate_limit.py`

---

### 6. SecurityHeadersMiddleware
**HTTP Security Headers**

- ✅ HSTS (Strict-Transport-Security)
- ✅ Content-Security-Policy
- ✅ X-Frame-Options
- ✅ X-Content-Type-Options
- ✅ Referrer-Policy

**Location:**
- Python: `shared/middleware/security_headers.py`

---

## Python FastAPI Integration

### Basic Setup

```python
import os
import sys
from fastapi import FastAPI

# Add shared path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# Import middleware
from shared.middleware import (
    RequestLoggingMiddleware,
    TenantContextMiddleware,
    setup_cors,
)
from shared.observability.middleware import (
    ObservabilityMiddleware,
    MetricsMiddleware,
)

# Create app
app = FastAPI(title="My Service")

# ============== Middleware Setup ==============
# Middleware order: Last added = First executed
# Execution order: CORS -> Observability -> Logging -> Tenant -> Routes

# 1. CORS - Secure cross-origin configuration
setup_cors(app)

# 2. Observability - Tracing, metrics, and monitoring
app.add_middleware(
    ObservabilityMiddleware,
    service_name="my-service",
    metrics_collector=None,  # Optional metrics collector
)

# 3. Request Logging - Correlation IDs and structured logging
app.add_middleware(
    RequestLoggingMiddleware,
    service_name="my-service",
    log_request_body=os.getenv("LOG_REQUEST_BODY", "false").lower() == "true",
    log_response_body=False,
)

# 4. Tenant Context - Multi-tenancy isolation
app.add_middleware(
    TenantContextMiddleware,
    require_tenant=True,  # Require tenant for all endpoints
    exempt_paths=["/health", "/healthz", "/readyz", "/docs", "/openapi.json"],
)
```

### Using Tenant Context

```python
from fastapi import Request
from shared.middleware.tenant_context import get_current_tenant, get_current_tenant_id

@app.get("/fields")
async def list_fields(request: Request):
    # Get tenant ID from context
    tenant_id = get_current_tenant_id()

    # Get full tenant context (includes user_id, roles)
    tenant = get_current_tenant()

    # Query with tenant isolation
    fields = await db.query(Field).filter(Field.tenant_id == tenant_id).all()

    return {"fields": fields}
```

### Using Correlation IDs

```python
from shared.middleware.request_logging import get_correlation_id, get_request_context

@app.post("/process")
async def process_data(request: Request):
    # Get correlation ID for logging and tracing
    correlation_id = get_correlation_id(request)

    # Get full request context
    context = get_request_context(request)
    # Returns: {"correlation_id": "...", "tenant_id": "...", "user_id": "..."}

    # Use in downstream service calls
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://other-service/api/endpoint",
            headers={"X-Correlation-ID": correlation_id},
        )

    return {"status": "processed", "correlation_id": correlation_id}
```

---

## TypeScript NestJS Integration

### Basic Setup

```typescript
import { NestFactory } from '@nestjs/core';
import { RequestLoggingInterceptor } from '../../shared/middleware/request-logging';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // ============== Middleware Setup ==============
  // Global request logging interceptor with correlation IDs
  app.useGlobalInterceptors(new RequestLoggingInterceptor('my-service'));

  // Enable CORS
  app.enableCors({
    origin: process.env.CORS_ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Tenant-ID', 'X-Correlation-ID'],
    credentials: true,
  });

  await app.listen(3000);
}

bootstrap();
```

### Using in Services

```typescript
import { Injectable } from '@nestjs/common';
import { StructuredLogger } from '../../shared/middleware/request-logging';

@Injectable()
export class MyService {
  private readonly logger = new StructuredLogger('my-service', 'MyService');

  async processData(data: any, correlationId: string, tenantId: string) {
    this.logger.log('Processing data', {
      correlationId,
      tenantId,
      operation: 'processData',
    });

    try {
      // Process data...

      this.logger.log('Data processed successfully', {
        correlationId,
        tenantId,
        operation: 'processData',
        recordCount: data.length,
      });
    } catch (error) {
      this.logger.error('Failed to process data', {
        correlationId,
        tenantId,
        operation: 'processData',
        error: error.message,
      });
      throw error;
    }
  }
}
```

### Using in Controllers

```typescript
import { Controller, Get, Req } from '@nestjs/common';
import { Request } from 'express';
import { getCorrelationId, getRequestContext } from '../../shared/middleware/request-logging';

@Controller('api/v1/items')
export class ItemsController {
  @Get()
  async list(@Req() request: Request) {
    const correlationId = getCorrelationId(request);
    const { tenantId, userId } = getRequestContext(request);

    const items = await this.itemsService.findAll(tenantId, correlationId);

    return {
      items,
      correlation_id: correlationId,
    };
  }
}
```

---

## Middleware Configuration

### Environment Variables

```bash
# Logging
LOG_REQUEST_BODY=false              # Log request bodies (debug only)
LOG_RESPONSE_BODY=false             # Log response bodies (debug only)

# CORS
CORS_ALLOWED_ORIGINS=https://sahool.app,https://admin.sahool.app,http://localhost:3000

# Observability
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318
OTEL_SERVICE_NAME=my-service

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_WINDOW_MS=60000

# Multi-tenancy
REQUIRE_TENANT=true                 # Require tenant for all endpoints
```

### Middleware Order

**IMPORTANT:** Middleware execution order matters!

For FastAPI (Last added = First executed):
```python
setup_cors(app)                     # Executed FIRST
app.add_middleware(ObservabilityMiddleware, ...)
app.add_middleware(RequestLoggingMiddleware, ...)
app.add_middleware(TenantContextMiddleware, ...)  # Executed LAST
```

Execution flow:
```
Request → CORS → Observability → Logging → Tenant → Your Routes → Response
```

---

## Best Practices

### 1. Always Use Correlation IDs
✅ **DO:**
```python
correlation_id = get_correlation_id(request)
logger.info("Processing request", extra={"correlation_id": correlation_id})
```

❌ **DON'T:**
```python
logger.info("Processing request")  # No correlation ID for tracing
```

---

### 2. Propagate Correlation IDs to Downstream Services
✅ **DO:**
```python
async with httpx.AsyncClient() as client:
    await client.post(
        "http://other-service/api/endpoint",
        headers={
            "X-Correlation-ID": correlation_id,
            "X-Tenant-ID": tenant_id,
        },
    )
```

---

### 3. Use Tenant Context for Data Isolation
✅ **DO:**
```python
tenant_id = get_current_tenant_id()
fields = await Field.filter(tenant_id=tenant_id).all()
```

❌ **DON'T:**
```python
fields = await Field.all()  # No tenant isolation - security risk!
```

---

### 4. Configure Exempt Paths Appropriately
```python
app.add_middleware(
    TenantContextMiddleware,
    require_tenant=True,
    exempt_paths=[
        "/health",       # Health checks
        "/healthz",      # Kubernetes liveness
        "/readyz",       # Kubernetes readiness
        "/metrics",      # Prometheus metrics
        "/docs",         # API documentation
        "/openapi.json", # OpenAPI spec
    ],
)
```

---

### 5. Enable Request Body Logging Only for Debugging
```python
# Development
app.add_middleware(
    RequestLoggingMiddleware,
    service_name="my-service",
    log_request_body=True,  # ⚠️ Only in development!
)

# Production
app.add_middleware(
    RequestLoggingMiddleware,
    service_name="my-service",
    log_request_body=False,  # ✅ Disabled in production
)
```

---

## Troubleshooting

### Issue: "Tenant context not available"

**Solution:** Ensure `TenantContextMiddleware` is added:
```python
app.add_middleware(TenantContextMiddleware)
```

And that the request includes `X-Tenant-ID` header or JWT with `tid` claim.

---

### Issue: Correlation IDs not appearing in logs

**Solution:** Ensure `RequestLoggingMiddleware` is added **before** your custom logging:
```python
app.add_middleware(RequestLoggingMiddleware, service_name="my-service")
```

---

### Issue: CORS errors

**Solution:** Use the shared `setup_cors()` function:
```python
from shared.middleware import setup_cors

setup_cors(app)  # Uses environment-based configuration
```

---

### Issue: Middleware not executing

**Solution:** Check middleware order. Last added = First executed in FastAPI:
```python
# This middleware executes LAST
app.add_middleware(TenantContextMiddleware)

# This middleware executes FIRST
setup_cors(app)
```

---

## Migration Checklist

When migrating a service to use shared middleware:

- [ ] Remove custom CORS configuration
- [ ] Remove custom request ID generation
- [ ] Remove custom logging middleware
- [ ] Add `RequestLoggingMiddleware`
- [ ] Add `ObservabilityMiddleware`
- [ ] Add `TenantContextMiddleware` (if multi-tenant)
- [ ] Update tenant ID extraction to use `get_current_tenant_id()`
- [ ] Update correlation ID usage to use `get_correlation_id(request)`
- [ ] Configure exempt paths appropriately
- [ ] Test with `X-Correlation-ID` and `X-Tenant-ID` headers

---

## Support & Resources

- **Examples:**
  - Python: `shared/middleware/examples/fastapi_example.py`
  - TypeScript: `apps/services/shared/middleware/examples/nestjs_example.ts`

- **Documentation:**
  - Request Logging: `shared/middleware/REQUEST_LOGGING_GUIDE.md`
  - Rate Limiting: `shared/middleware/RATE_LIMITING_GUIDE.md`

- **Slack Channels:**
  - `#platform-middleware`
  - `#platform-observability`

---

**Last Updated:** 2026-01-06
**Version:** 1.0.0
