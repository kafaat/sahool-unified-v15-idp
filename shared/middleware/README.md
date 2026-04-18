# Middleware Package | حزمة الوسائط

HTTP middleware components for FastAPI services in the SAHOOL platform.

## Components

| Middleware | File | Purpose |
|-----------|------|---------|
| **CORS** | `cors.py` | Secure cross-origin configuration |
| **Rate Limiting** | `rate_limit.py` | Tiered API rate limiting (token bucket) |
| **Request Size** | `request_size.py` | Payload size validation |
| **Tenant Context** | `tenant_context.py` | Multi-tenancy isolation from JWT `tid` claim |
| **Request Logging** | `request_logging.py` | Structured JSON logging with correlation IDs |
| **API Versioning** | `api_versioning.py` | URL-based API versioning (`/api/v1/`, `/api/v2/`) |
| **Security Headers** | `security_headers.py` | HTTP security headers (CSP, HSTS, X-Frame-Options) |
| **Input Sanitization** | `input_sanitizer.py` | XSS and injection prevention |
| **Idempotency** | `idempotency.py` | Cache responses for `Idempotency-Key` on POST/PATCH/DELETE (in-memory, 10-min TTL — swap to Redis for prod) |

## Quick Start

```python
from fastapi import FastAPI
from shared.middleware import (
    setup_cors,
    rate_limit_middleware,
    RequestLoggingMiddleware,
    TenantContextMiddleware,
    setup_security_headers,
    setup_input_sanitization,
)

app = FastAPI()

# Apply middleware (order matters - last added runs first)
setup_cors(app)
setup_security_headers(app)
setup_input_sanitization(app)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TenantContextMiddleware)
rate_limit_middleware(app)
```

## Rate Limiting Tiers

```python
from shared.middleware import rate_limit, rate_limit_by_tenant

# Decorator-based rate limiting
@router.get("/fields")
@rate_limit(requests_per_minute=60)
async def list_fields():
    ...

# Tenant-scoped rate limiting
@router.get("/advisory")
@rate_limit_by_tenant(requests_per_minute=30)
async def get_advisory():
    ...
```

| Tier | Requests/min | Requests/hour |
|------|-------------|---------------|
| Starter | 30 | 500 |
| Professional | 60 | 2,000 |
| Enterprise | 120 | 5,000 |

## Correlation ID Tracking

```python
from shared.middleware import get_correlation_id, get_request_context

# Access in any async handler
correlation_id = get_correlation_id()
context = get_request_context()  # {correlation_id, method, path, user_id, tenant_id}
```

## Additional Documentation

- `RATE_LIMITING_GUIDE.md` — Detailed rate limiting configuration
- `REQUEST_LOGGING_GUIDE.md` — Logging setup and customization
- `REQUEST_LOGGING_ARCHITECTURE.md` — Architecture overview
- `REQUEST_LOGGING_README.md` — Request logging reference
- `IMPLEMENTATION_SUMMARY.md` — Implementation details
