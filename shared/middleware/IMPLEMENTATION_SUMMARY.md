# Request Logging Infrastructure - Implementation Summary

## 📦 What Was Created

Comprehensive request logging infrastructure for both Python (FastAPI) and TypeScript (NestJS) backend services with structured JSON logging, correlation ID tracking, and observability support.

## 📂 File Structure

```
/home/user/sahool-unified-v15-idp/
│
├── shared/middleware/
│   ├── request_logging.py                    # ✅ FastAPI middleware implementation
│   ├── __init__.py                           # ✅ Updated with new exports
│   ├── REQUEST_LOGGING_README.md             # ✅ Quick start guide
│   ├── REQUEST_LOGGING_GUIDE.md              # ✅ Comprehensive usage guide
│   ├── IMPLEMENTATION_SUMMARY.md             # ✅ This file
│   └── examples/
│       └── fastapi_example.py                # ✅ Complete FastAPI example
│
└── apps/services/shared/middleware/
    ├── request-logging.ts                    # ✅ NestJS interceptor implementation
    ├── index.ts                              # ✅ TypeScript exports
    └── examples/
        └── nestjs_example.ts                 # ✅ Complete NestJS example
```

## ✨ Key Features Implemented

### 1. Structured JSON Logging
- All logs output in consistent JSON format
- Timestamp, service name, log type, and message
- Structured HTTP request/response data
- Error details with stack traces

### 2. Correlation ID Tracking
- Automatic generation (UUID v4) if not provided
- Extraction from `X-Correlation-ID` or `X-Request-ID` headers
- Propagation to response headers
- Available in request state for downstream use

### 3. Request Metrics
- **Method**: HTTP method (GET, POST, PUT, DELETE, etc.)
- **Path**: Request URL path
- **Status Code**: HTTP response status
- **Duration**: Request processing time in milliseconds
- **Query Parameters**: URL query string (optional)
- **User Agent**: Client user agent string

### 4. Context Tracking
- **Tenant ID**: Multi-tenant isolation support
- **User ID**: User authentication tracking
- **Correlation ID**: Request tracing across services

### 5. Sensitive Data Protection
- Automatic filtering of passwords, tokens, API keys
- Redaction of authorization headers
- Masking of database credentials
- Protection of credit card numbers
- JWT token filtering

### 6. Error Handling
- Automatic exception capture
- Error type and message logging
- Stack trace inclusion
- Request context preservation

## 🎯 Usage Examples

### Python (FastAPI) - Minimal Setup

```python
from fastapi import FastAPI
from shared.middleware import RequestLoggingMiddleware

app = FastAPI()
app.add_middleware(RequestLoggingMiddleware, service_name="my-service")
```

### TypeScript (NestJS) - Minimal Setup

```typescript
import { NestFactory } from '@nestjs/core';
import { RequestLoggingInterceptor } from '../shared/middleware';

const app = await NestFactory.create(AppModule);
app.useGlobalInterceptors(new RequestLoggingInterceptor('my-service'));
```

## 📊 Log Output Format

### Request Log
```json
{
  "timestamp": "2025-12-31T10:30:45.123Z",
  "service": "field-service",
  "type": "request",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "http": {
    "method": "POST",
    "path": "/api/v1/fields",
    "query": {"expand": "crop"},
    "user_agent": "Mozilla/5.0..."
  },
  "tenant_id": "tenant-123",
  "user_id": "user-456",
  "message": "Incoming request"
}
```

### Response Log
```json
{
  "timestamp": "2025-12-31T10:30:45.789Z",
  "service": "field-service",
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

### Error Log
```json
{
  "timestamp": "2025-12-31T10:30:46.456Z",
  "service": "field-service",
  "type": "error",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "http": {
    "method": "POST",
    "path": "/api/v1/fields",
    "status_code": 500,
    "duration_ms": 89.12
  },
  "tenant_id": "tenant-123",
  "user_id": "user-456",
  "error": {
    "type": "DatabaseError",
    "message": "Connection timeout",
    "stack": "..."
  },
  "message": "Request failed: Connection timeout"
}
```

## 🔧 Configuration Options

### Python (FastAPI)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `service_name` | `str` | Required | Name of the service for logging |
| `log_request_body` | `bool` | `False` | Enable request body logging |
| `log_response_body` | `bool` | `False` | Enable response body logging |
| `exclude_paths` | `list[str]` | `["/healthz", ...]` | Paths to exclude from logging |
| `max_body_length` | `int` | `1000` | Max body length to log (chars) |

### TypeScript (NestJS)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `serviceName` | `string` | Required | Name of the service for logging |
| `logRequestBody` | `boolean` | `false` | Enable request body logging |
| `logResponseBody` | `boolean` | `false` | Enable response body logging |

## 🚀 Integration Steps

### For Existing FastAPI Services

1. Import the middleware:
```python
from shared.middleware import RequestLoggingMiddleware
```

2. Add to your app:
```python
app.add_middleware(
    RequestLoggingMiddleware,
    service_name=os.getenv("SERVICE_NAME", "my-service"),
)
```

3. Use correlation ID in your code:
```python
from shared.middleware import get_correlation_id, get_request_context

@app.get("/endpoint")
async def my_endpoint(request: Request):
    correlation_id = get_correlation_id(request)
    context = get_request_context(request)
    # Use in logging or pass to other services
```

### For Existing NestJS Services

1. Import the interceptor:
```typescript
import { RequestLoggingInterceptor } from '../shared/middleware';
```

2. Add to main.ts:
```typescript
app.useGlobalInterceptors(new RequestLoggingInterceptor('my-service'));
```

3. Use correlation ID in your code:
```typescript
import { getCorrelationId, getRequestContext } from '../shared/middleware';

@Get()
async myEndpoint(@Req() request: Request) {
  const correlationId = getCorrelationId(request);
  const context = getRequestContext(request);
  // Use in logging or pass to other services
}
```

## 🔍 Querying Logs

### Find all logs for a specific request
```bash
kubectl logs -l app=field-service | grep "550e8400-e29b-41d4-a716-446655440000"
```

### Find slow requests (>500ms)
```bash
kubectl logs -l app=field-service | jq 'select(.http.duration_ms > 500)'
```

### Find errors
```bash
kubectl logs -l app=field-service | jq 'select(.type == "error")'
```

### Count requests by tenant
```bash
kubectl logs -l app=field-service | jq -r '.tenant_id' | sort | uniq -c
```

### Find 5xx errors
```bash
kubectl logs -l app=field-service | jq 'select(.http.status_code >= 500)'
```

## 📈 Benefits

1. **Improved Debugging**: Trace requests across microservices using correlation IDs
2. **Performance Monitoring**: Track request duration and identify slow endpoints
3. **Security**: Automatic sensitive data filtering
4. **Compliance**: Structured audit logs with user and tenant tracking
5. **Observability**: JSON format ready for log aggregation tools (ELK, Loki, etc.)
6. **Troubleshooting**: Complete request/response context for issue investigation

## 🔐 Security Features

- Automatic redaction of sensitive fields (passwords, tokens, keys)
- Authorization header filtering
- Database credential masking
- JWT token protection
- Credit card number masking
- Configurable sensitive field patterns

## 🎓 Next Steps

1. **Review Documentation**:
   - Read [REQUEST_LOGGING_GUIDE.md](./REQUEST_LOGGING_GUIDE.md) for detailed usage
   - Check example files for integration patterns

2. **Integrate into Services**:
   - Add middleware to FastAPI services
   - Add interceptor to NestJS services
   - Test with sample requests

3. **Configure Log Aggregation**:
   - Set up centralized logging (ELK, Loki, etc.)
   - Create dashboards for request metrics
   - Set up alerts for errors and slow requests

4. **Adopt Best Practices**:
   - Always propagate correlation IDs
   - Use structured logging with context
   - Monitor log volume and performance

## 📚 Additional Resources

- **REQUEST_LOGGING_README.md** - Quick start guide
- **REQUEST_LOGGING_GUIDE.md** - Comprehensive documentation
- **examples/fastapi_example.py** - Full FastAPI integration example
- **examples/nestjs_example.ts** - Full NestJS integration example

## ✅ Testing

To test the implementation:

### Python
```bash
cd /home/user/sahool-unified-v15-idp/shared/middleware/examples
python fastapi_example.py
```

Then in another terminal:
```bash
curl -H "X-Tenant-ID: test-tenant" http://localhost:8000/api/v1/fields
```

### TypeScript
```bash
cd /home/user/sahool-unified-v15-idp/apps/services/chat-service
npm run start:dev
```

Then in another terminal:
```bash
curl -H "X-Tenant-ID: test-tenant" http://localhost:8114/api/v1/conversations
```

## 🎉 Summary

You now have a complete request logging infrastructure that provides:
- ✅ Structured JSON logging
- ✅ Correlation ID tracking
- ✅ Request/response metrics (method, path, status, duration)
- ✅ User and tenant tracking
- ✅ Sensitive data filtering
- ✅ Error logging with context
- ✅ Service-to-service tracing
- ✅ Production-ready with examples

All components are ready to use in your FastAPI and NestJS services!
