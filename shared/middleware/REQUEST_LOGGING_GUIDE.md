# Request Logging Infrastructure Guide

This guide explains how to use the request logging middleware for FastAPI and NestJS services in the SAHOOL platform.

## Overview

The request logging infrastructure provides:
- ✅ Structured JSON logging for all HTTP requests
- ✅ Request method, path, status code, and duration tracking
- ✅ User ID and Tenant ID extraction from headers or JWT
- ✅ Correlation ID generation and propagation
- ✅ Sensitive data filtering
- ✅ OpenTelemetry-compatible trace context

## Python (FastAPI) Usage

### Basic Setup

```python
from fastapi import FastAPI
from shared.middleware.request_logging import RequestLoggingMiddleware

app = FastAPI(title="My Service")

# Add request logging middleware
app.add_middleware(
    RequestLoggingMiddleware,
    service_name="my-service",
)
```

### Advanced Configuration

```python
from fastapi import FastAPI
from shared.middleware.request_logging import RequestLoggingMiddleware

app = FastAPI(title="My Service")

app.add_middleware(
    RequestLoggingMiddleware,
    service_name="my-service",
    log_request_body=True,  # Enable for debugging (not recommended in production)
    log_response_body=False,
    exclude_paths=["/healthz", "/metrics", "/docs"],  # Paths to skip
    max_body_length=1000,  # Maximum body length to log
)
```

### Using Correlation ID in Your Code

```python
from fastapi import Request
from shared.middleware.request_logging import get_correlation_id, get_request_context

@app.get("/example")
async def example_endpoint(request: Request):
    # Get correlation ID
    correlation_id = get_correlation_id(request)

    # Get full request context
    context = get_request_context(request)
    # context = {"correlation_id": "...", "tenant_id": "...", "user_id": "..."}

    # Use in logging or pass to downstream services
    logger.info(f"Processing request", extra=context)

    return {"correlation_id": correlation_id}
```

### Log Output Format (JSON)

```json
{
  "timestamp": "2025-12-31T10:30:45.123Z",
  "service": "my-service",
  "type": "request",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "http": {
    "method": "POST",
    "path": "/api/v1/fields",
    "query": {"page": "1"},
    "user_agent": "Mozilla/5.0..."
  },
  "tenant_id": "tenant-123",
  "user_id": "user-456",
  "message": "Incoming request"
}
```

```json
{
  "timestamp": "2025-12-31T10:30:45.789Z",
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

## TypeScript (NestJS) Usage

### Basic Setup

In your `main.ts`:

```typescript
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { RequestLoggingInterceptor } from '../shared/middleware/request-logging';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Add request logging interceptor
  app.useGlobalInterceptors(
    new RequestLoggingInterceptor('my-service')
  );

  await app.listen(3000);
}

bootstrap();
```

### Alternative: As a Provider

In your `app.module.ts`:

```typescript
import { Module } from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { RequestLoggingInterceptor } from '../shared/middleware/request-logging';

@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useValue: new RequestLoggingInterceptor('my-service'),
    },
  ],
})
export class AppModule {}
```

### Using Correlation ID in Your Code

```typescript
import { Controller, Get, Req } from '@nestjs/common';
import { Request } from 'express';
import { getCorrelationId, getRequestContext } from '../shared/middleware/request-logging';

@Controller('example')
export class ExampleController {
  @Get()
  async getExample(@Req() request: Request) {
    // Get correlation ID
    const correlationId = getCorrelationId(request);

    // Get full request context
    const context = getRequestContext(request);
    // context = { correlationId: "...", tenantId: "...", userId: "..." }

    // Use in logging or pass to downstream services
    this.logger.log('Processing request', context);

    return { correlationId };
  }
}
```

### Using Structured Logger

```typescript
import { Injectable } from '@nestjs/common';
import { StructuredLogger } from '../shared/middleware/request-logging';

@Injectable()
export class MyService {
  private readonly logger = new StructuredLogger('my-service', 'MyService');

  async doSomething(correlationId: string, tenantId: string) {
    this.logger.log('Starting operation', {
      correlationId,
      tenantId,
      operation: 'doSomething',
    });

    try {
      // Do work...
      this.logger.log('Operation completed', { correlationId, tenantId });
    } catch (error) {
      this.logger.error('Operation failed', {
        correlationId,
        tenantId,
        error: error.message,
      });
      throw error;
    }
  }
}
```

### Log Output Format (JSON)

```json
{
  "timestamp": "2025-12-31T10:30:45.123Z",
  "service": "my-service",
  "type": "request",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "http": {
    "method": "POST",
    "path": "/api/v1/conversations",
    "query": {"limit": "10"},
    "user_agent": "Mozilla/5.0..."
  },
  "tenant_id": "tenant-123",
  "user_id": "user-456",
  "message": "Incoming request: POST /api/v1/conversations"
}
```

```json
{
  "timestamp": "2025-12-31T10:30:45.789Z",
  "service": "my-service",
  "type": "response",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "http": {
    "method": "POST",
    "path": "/api/v1/conversations",
    "status_code": 201,
    "duration_ms": 98.76
  },
  "tenant_id": "tenant-123",
  "user_id": "user-456",
  "message": "POST /api/v1/conversations 201 98.76ms"
}
```

## Correlation ID Propagation

### Client-Side (Frontend)

When making requests from the frontend, you can:

1. **Generate and pass correlation ID**:
```typescript
const correlationId = crypto.randomUUID();

fetch('/api/v1/fields', {
  headers: {
    'X-Correlation-ID': correlationId,
    'X-Tenant-ID': tenantId,
  },
});
```

2. **Receive correlation ID from response**:
```typescript
const response = await fetch('/api/v1/fields');
const correlationId = response.headers.get('X-Correlation-ID');
```

### Service-to-Service Communication

When one service calls another, propagate the correlation ID:

#### Python (FastAPI)
```python
import httpx
from fastapi import Request

@app.get("/external-call")
async def call_external_service(request: Request):
    correlation_id = get_correlation_id(request)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://other-service/api/endpoint",
            headers={
                "X-Correlation-ID": correlation_id,
                "X-Tenant-ID": request.state.tenant_id,
            }
        )

    return response.json()
```

#### TypeScript (NestJS)
```typescript
import { HttpService } from '@nestjs/axios';
import { getCorrelationId } from '../shared/middleware/request-logging';

@Injectable()
export class MyService {
  constructor(private httpService: HttpService) {}

  async callExternalService(request: Request) {
    const correlationId = getCorrelationId(request);
    const { tenantId } = getRequestContext(request);

    return this.httpService.get('http://other-service/api/endpoint', {
      headers: {
        'X-Correlation-ID': correlationId,
        'X-Tenant-ID': tenantId,
      },
    }).toPromise();
  }
}
```

## Log Aggregation and Search

With structured JSON logging, you can easily search and filter logs:

### Search by correlation ID
```bash
# Find all logs for a specific request
kubectl logs -l app=my-service | grep "550e8400-e29b-41d4-a716-446655440000"
```

### Search by tenant
```bash
# Find all requests from a specific tenant
kubectl logs -l app=my-service | jq 'select(.tenant_id == "tenant-123")'
```

### Find slow requests
```bash
# Find requests taking longer than 1 second
kubectl logs -l app=my-service | jq 'select(.http.duration_ms > 1000)'
```

### Count errors by type
```bash
# Count errors by type
kubectl logs -l app=my-service | jq -r 'select(.type == "error") | .error.type' | sort | uniq -c
```

## Best Practices

1. **Always use correlation IDs** - Pass them through your entire request chain
2. **Don't log sensitive data** - The middleware filters common sensitive fields, but be careful with custom data
3. **Use structured logging** - Always log with context (correlation_id, tenant_id, user_id)
4. **Monitor log volume** - Disable request/response body logging in production unless debugging
5. **Set appropriate log levels** - Use DEBUG for development, INFO for production
6. **Index correlation_id** - Make sure your log aggregation system indexes correlation_id for fast searches

## Integration with Observability Stack

### OpenTelemetry
The middleware is compatible with OpenTelemetry trace context. Correlation IDs can be used as trace IDs.

### Log Aggregation (ELK, Loki, etc.)
The structured JSON format is ready for ingestion by log aggregation systems:

```yaml
# Example Loki config
- job_name: sahool-services
  static_configs:
    - targets:
        - localhost
      labels:
        job: sahool-services
  pipeline_stages:
    - json:
        expressions:
          service: service
          correlation_id: correlation_id
          tenant_id: tenant_id
          status_code: http.status_code
          duration_ms: http.duration_ms
```

## Troubleshooting

### Correlation ID not appearing
- Make sure the middleware is added **after** CORS middleware
- Check that excluded paths don't include your endpoint
- Verify the request is actually hitting the middleware

### User/Tenant ID missing
- Ensure authentication middleware runs **before** logging middleware
- Check that JWT claims include `sub` (user_id) and `tid` (tenant_id)
- Verify headers `X-User-ID` and `X-Tenant-ID` are being sent

### Logs not in JSON format
- Check Python: `ENVIRONMENT=production` environment variable
- Check NestJS: Logs should always be JSON with this middleware

## Migration from Existing Logging

If you have existing logging code:

### Python
```python
# Old way
logger.info(f"Processing request for tenant {tenant_id}")

# New way (with context)
from shared.middleware.request_logging import get_request_context

context = get_request_context(request)
logger.info("Processing request", extra=context)
```

### TypeScript
```typescript
// Old way
this.logger.log(`Processing request for tenant ${tenantId}`);

// New way (with structured logger)
import { StructuredLogger } from '../shared/middleware/request-logging';

const logger = new StructuredLogger('my-service');
logger.log('Processing request', { tenantId, correlationId });
```
