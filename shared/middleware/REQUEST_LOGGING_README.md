# Request Logging Infrastructure

Comprehensive request logging middleware for SAHOOL backend services (FastAPI and NestJS).

## 📋 Overview

This infrastructure provides structured JSON logging for all HTTP requests with:

- ✅ **Request Details**: method, path, query parameters, user agent
- ✅ **Response Details**: status code, duration in milliseconds
- ✅ **Context Tracking**: correlation ID, tenant ID, user ID
- ✅ **Error Logging**: automatic error capture with stack traces
- ✅ **Sensitive Data Filtering**: automatic redaction of passwords, tokens, keys
- ✅ **Service-to-Service Tracing**: correlation ID propagation across services

## 📁 Files

### Python (FastAPI)

- **`request_logging.py`** - Main middleware implementation
- **`examples/fastapi_example.py`** - Complete working example
- **`REQUEST_LOGGING_GUIDE.md`** - Comprehensive usage guide

### TypeScript (NestJS)

- **`../apps/services/shared/middleware/request-logging.ts`** - Main interceptor implementation
- **`../apps/services/shared/middleware/examples/nestjs_example.ts`** - Complete working example

## 🚀 Quick Start

### Python (FastAPI)

```python
from fastapi import FastAPI
from shared.middleware.request_logging import RequestLoggingMiddleware

app = FastAPI(title="My Service")

app.add_middleware(
    RequestLoggingMiddleware,
    service_name="my-service",
)
```

### TypeScript (NestJS)

```typescript
import { NestFactory } from "@nestjs/core";
import { RequestLoggingInterceptor } from "../shared/middleware/request-logging";

const app = await NestFactory.create(AppModule);
app.useGlobalInterceptors(new RequestLoggingInterceptor("my-service"));
```

## 📊 Log Format

All logs are output in structured JSON format:

```json
{
  "timestamp": "2025-12-31T10:30:45.123Z",
  "service": "my-service",
  "type": "response",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "http": {
    "method": "POST",
    "path": "/api/v1/fields",
    "status_code": 201,
    "duration_ms": 123.45
  },
  "tenant_id": "tenant-123",
  "user_id": "user-456",
  "message": "POST /api/v1/fields 201 123.45ms"
}
```

## 🔑 Key Features

### 1. Correlation ID Tracking

Correlation IDs are automatically:

- Extracted from `X-Correlation-ID` or `X-Request-ID` headers
- Generated if not provided (UUID v4)
- Added to response headers
- Available in request state for downstream use

```python
# Python
from shared.middleware.request_logging import get_correlation_id
correlation_id = get_correlation_id(request)
```

```typescript
// TypeScript
import { getCorrelationId } from "../shared/middleware/request-logging";
const correlationId = getCorrelationId(request);
```

### 2. Tenant & User Tracking

Automatically extracts from:

- Headers: `X-Tenant-ID`, `X-User-ID`
- JWT claims: `tid` (tenant), `sub` (user)
- Request state (set by auth middleware)

### 3. Sensitive Data Filtering

Automatically redacts:

- Passwords, tokens, API keys
- Authorization headers
- Database connection strings
- Credit card numbers
- And more...

### 4. Error Logging

Exceptions are automatically logged with:

- Error type and message
- Stack trace
- Request context
- HTTP status code

## 📖 Documentation

- **[REQUEST_LOGGING_GUIDE.md](./REQUEST_LOGGING_GUIDE.md)** - Complete usage guide with examples
- **[examples/fastapi_example.py](./examples/fastapi_example.py)** - Full FastAPI integration example
- **[examples/nestjs_example.ts](../apps/services/shared/middleware/examples/nestjs_example.ts)** - Full NestJS integration example

## 🔧 Configuration

### Python (FastAPI)

```python
app.add_middleware(
    RequestLoggingMiddleware,
    service_name="my-service",          # Required: service name for logs
    log_request_body=False,             # Optional: log request bodies
    log_response_body=False,            # Optional: log response bodies
    exclude_paths=["/healthz"],         # Optional: paths to exclude
    max_body_length=1000,               # Optional: max body length to log
)
```

### TypeScript (NestJS)

```typescript
new RequestLoggingInterceptor(
  "my-service", // Required: service name
  false, // Optional: log request body
  false, // Optional: log response body
);
```

## 🌐 Service-to-Service Communication

When calling other services, propagate the correlation ID:

### Python

```python
async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://other-service/api/endpoint",
        headers={
            "X-Correlation-ID": get_correlation_id(request),
            "X-Tenant-ID": request.state.tenant_id,
        }
    )
```

### TypeScript

```typescript
const correlationId = getCorrelationId(request);
const { tenantId } = getRequestContext(request);

await fetch("http://other-service/api/endpoint", {
  headers: {
    "X-Correlation-ID": correlationId,
    "X-Tenant-ID": tenantId,
  },
});
```

## 🔍 Searching Logs

With structured JSON logging, you can easily search and filter:

```bash
# Find all logs for a request
kubectl logs -l app=my-service | grep "correlation-id-here"

# Find slow requests (>1s)
kubectl logs -l app=my-service | jq 'select(.http.duration_ms > 1000)'

# Find errors
kubectl logs -l app=my-service | jq 'select(.type == "error")'

# Count requests by tenant
kubectl logs -l app=my-service | jq -r '.tenant_id' | sort | uniq -c
```

## 🎯 Best Practices

1. **Always propagate correlation IDs** across service boundaries
2. **Don't enable body logging in production** (performance impact)
3. **Use structured logging** with request context
4. **Index correlation_id** in your log aggregation system
5. **Set appropriate log levels** (DEBUG for dev, INFO for prod)
6. **Monitor log volume** to avoid overwhelming storage

## 🔄 Migration Guide

### From Existing Logging

#### Python

```python
# Old way
logger.info(f"Processing for tenant {tenant_id}")

# New way
from shared.middleware.request_logging import get_request_context
context = get_request_context(request)
logger.info("Processing request", extra=context)
```

#### TypeScript

```typescript
// Old way
this.logger.log(`Processing for tenant ${tenantId}`);

// New way
import { StructuredLogger } from "../shared/middleware/request-logging";
const logger = new StructuredLogger("my-service");
logger.log("Processing request", { tenantId, correlationId });
```

## 📦 Dependencies

### Python

- `fastapi` - Web framework
- `starlette` - ASGI middleware support
- No additional dependencies required

### TypeScript

- `@nestjs/common` - NestJS framework
- `@nestjs/core` - NestJS interceptors
- `rxjs` - Reactive extensions
- No additional dependencies required

## 🧪 Testing

See example files for complete integration examples:

- `examples/fastapi_example.py` - Test with `uvicorn`
- `examples/nestjs_example.ts` - Test with `nest start`

## 📝 License

Internal use only - SAHOOL Platform

## 👥 Maintainers

SAHOOL DevOps & Backend Team

## 📞 Support

For questions or issues:

1. Check the [REQUEST_LOGGING_GUIDE.md](./REQUEST_LOGGING_GUIDE.md)
2. Review example implementations
3. Contact the platform team

---

**Last Updated**: 2025-12-31
**Version**: 1.0.0
