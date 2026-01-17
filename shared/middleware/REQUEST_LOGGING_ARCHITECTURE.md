# Request Logging Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Application                       │
│                    (Web, Mobile, API Consumer)                   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ HTTP Request
                               │ Headers: X-Correlation-ID (optional)
                               │          X-Tenant-ID
                               │          Authorization
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway / LB                         │
│                    (Nginx, Traefik, AWS ALB)                     │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
        ┌──────────────────────┴──────────────────────┐
        │                                              │
        ▼                                              ▼
┌────────────────────┐                      ┌────────────────────┐
│   FastAPI Service  │                      │  NestJS Service    │
│   (Python)         │                      │  (TypeScript)      │
└────────────────────┘                      └────────────────────┘
        │                                              │
        │ Middleware Stack                             │ Interceptor Stack
        ▼                                              ▼
┌────────────────────────────────────────────────────────────────┐
│                    Request Logging Layer                        │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ 1. Extract/Generate Correlation ID                         │ │
│ │ 2. Extract Tenant ID & User ID                             │ │
│ │ 3. Start Timer                                              │ │
│ │ 4. Log Incoming Request (JSON)                             │ │
│ └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│              Other Middleware / Guards                          │
│  - Authentication / JWT Validation                              │
│  - Tenant Context Middleware                                    │
│  - Rate Limiting                                                │
│  - CORS                                                         │
└──────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│                     Application Handlers                        │
│              (Controllers, Route Handlers)                      │
│  - Access correlation_id via helpers                            │
│  - Use structured logging with context                          │
│  - Propagate correlation_id to downstream services              │
└──────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                         │
│  - Services                                                     │
│  - Database Operations                                          │
│  - External API Calls (with correlation_id propagation)         │
└──────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│                    Response Generation                          │
└──────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────┐
│              Request Logging Layer (Response)                   │
│ ┌────────────────────────────────────────────────────────────┐ │
│ │ 1. Calculate Duration                                       │ │
│ │ 2. Add X-Correlation-ID to Response Headers                │ │
│ │ 3. Log Response with Metrics (JSON)                        │ │
│ │    - Status Code                                            │ │
│ │    - Duration (ms)                                          │ │
│ │    - Correlation ID                                         │ │
│ │    - Tenant ID                                              │ │
│ │    - User ID                                                │ │
│ └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬─────────────────────────────────┘
                               │
                               │ HTTP Response
                               │ Headers: X-Correlation-ID
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Client Application                       │
└─────────────────────────────────────────────────────────────────┘
```

## Log Flow Diagram

```
Request Received
    │
    ├─► Extract/Generate Correlation ID
    │   └─► X-Correlation-ID header
    │   └─► X-Request-ID header
    │   └─► Generate UUID v4 (if not provided)
    │
    ├─► Extract Context
    │   ├─► Tenant ID
    │   │   ├─► X-Tenant-ID header
    │   │   └─► JWT claim (tid)
    │   └─► User ID
    │       ├─► X-User-ID header
    │       └─► JWT claim (sub)
    │
    ├─► Start Timer (performance.now())
    │
    ├─► Log Request (JSON)
    │   {
    │     "timestamp": "2025-12-31T10:30:45.123Z",
    │     "service": "field-service",
    │     "type": "request",
    │     "correlation_id": "550e8400-...",
    │     "http": {
    │       "method": "POST",
    │       "path": "/api/v1/fields",
    │       "query": {...}
    │     },
    │     "tenant_id": "tenant-123",
    │     "user_id": "user-456"
    │   }
    │
    ▼
Process Request
    │
    ├─► Application Logic
    │   ├─► Use correlation_id in logging
    │   └─► Propagate to downstream services
    │
    ▼
Response Generated
    │
    ├─► Calculate Duration
    │   └─► duration_ms = (end_time - start_time) * 1000
    │
    ├─► Add Response Headers
    │   └─► X-Correlation-ID: 550e8400-...
    │
    ├─► Log Response (JSON)
    │   {
    │     "timestamp": "2025-12-31T10:30:45.789Z",
    │     "service": "field-service",
    │     "type": "response",
    │     "correlation_id": "550e8400-...",
    │     "http": {
    │       "method": "POST",
    │       "path": "/api/v1/fields",
    │       "status_code": 201,
    │       "duration_ms": 123.45
    │     },
    │     "tenant_id": "tenant-123",
    │     "user_id": "user-456"
    │   }
    │
    ▼
Response Sent to Client
```

## Service-to-Service Communication

```
┌─────────────────┐
│  Field Service  │
│  (Origin)       │
└────────┬────────┘
         │
         │ 1. Receive request with correlation_id
         │    X-Correlation-ID: 550e8400-...
         │
         ├─► Log incoming request
         │
         ├─► Process business logic
         │
         │ 2. Call Weather Service
         ▼
┌─────────────────────────────────────────┐
│ HTTP Request to Weather Service         │
│ Headers:                                │
│   X-Correlation-ID: 550e8400-...        │  ◄── Propagated
│   X-Tenant-ID: tenant-123               │  ◄── Propagated
│   X-User-ID: user-456                   │  ◄── Propagated
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Weather Service │
│  (Downstream)   │
└────────┬────────┘
         │
         ├─► Log with SAME correlation_id
         │   (Traces back to origin)
         │
         ├─► Process weather data
         │
         ├─► Return response
         │
         ▼
┌─────────────────┐
│  Field Service  │
│  (Origin)       │
└────────┬────────┘
         │
         ├─► Log weather service response
         │   (With correlation_id)
         │
         ├─► Complete processing
         │
         ├─► Log final response
         │
         ▼
    Return to Client
```

## Data Flow: Correlation ID Tracking

```
Client Request
    │ correlation_id: 550e8400-e29b-41d4-a716-446655440000
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  Service A (Field Service)                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Request Log                                        │  │
│  │ correlation_id: 550e8400-...                       │  │
│  │ timestamp: 2025-12-31T10:30:45.123Z               │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Application Log                                    │  │
│  │ correlation_id: 550e8400-...                       │  │
│  │ message: "Fetching weather data"                   │  │
│  │ timestamp: 2025-12-31T10:30:45.200Z               │  │
│  └────────────────────────────────────────────────────┘  │
│      │                                                   │
│      │ HTTP Request to Service B                         │
│      │ X-Correlation-ID: 550e8400-...                    │
│      ▼                                                   │
└──────────────────────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│  Service B (Weather Service)                             │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Request Log                                        │  │
│  │ correlation_id: 550e8400-...   ◄── SAME ID        │  │
│  │ timestamp: 2025-12-31T10:30:45.300Z               │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Application Log                                    │  │
│  │ correlation_id: 550e8400-...   ◄── SAME ID        │  │
│  │ message: "Querying weather API"                    │  │
│  │ timestamp: 2025-12-31T10:30:45.350Z               │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Response Log                                       │  │
│  │ correlation_id: 550e8400-...   ◄── SAME ID        │  │
│  │ timestamp: 2025-12-31T10:30:45.500Z               │  │
│  │ duration_ms: 200                                   │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                  │
                  │ Response
                  ▼
┌──────────────────────────────────────────────────────────┐
│  Service A (Field Service)                               │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Application Log                                    │  │
│  │ correlation_id: 550e8400-...                       │  │
│  │ message: "Weather data received"                   │  │
│  │ timestamp: 2025-12-31T10:30:45.550Z               │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Response Log                                       │  │
│  │ correlation_id: 550e8400-...                       │  │
│  │ timestamp: 2025-12-31T10:30:45.789Z               │  │
│  │ duration_ms: 666                                   │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                  │
                  ▼
            Client Response
            X-Correlation-ID: 550e8400-...

Result: All logs across both services share the SAME correlation_id,
        enabling end-to-end request tracing
```

## Log Aggregation & Search

```
┌─────────────────────────────────────────────────────────────┐
│                   Application Services                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Field   │  │ Weather │  │ Chat    │  │ Market  │        │
│  │ Service │  │ Service │  │ Service │  │ Service │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │              │
│       │ Structured JSON Logs                 │              │
│       └────────────┼────────────┼────────────┘              │
└────────────────────┼────────────┼───────────────────────────┘
                     │            │
                     │ stdout     │
                     ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│              Log Collection Layer                            │
│  (Fluent Bit, Filebeat, Vector, CloudWatch Logs)            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Ship logs
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Log Aggregation & Storage                       │
│  (Elasticsearch, Loki, CloudWatch, S3)                       │
│                                                              │
│  Indexed Fields:                                             │
│  - timestamp                                                 │
│  - service                                                   │
│  - correlation_id  ◄── Searchable                           │
│  - tenant_id       ◄── Searchable                           │
│  - user_id         ◄── Searchable                           │
│  - http.status_code                                          │
│  - http.duration_ms                                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Query & Visualize
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Observability Platform                          │
│  (Kibana, Grafana, CloudWatch Insights)                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Query: correlation_id:"550e8400-..."                  │ │
│  │                                                         │ │
│  │  Results:                                               │ │
│  │  1. [field-service] Request received                   │ │
│  │  2. [field-service] Calling weather service            │ │
│  │  3. [weather-service] Request received                 │ │
│  │  4. [weather-service] Response sent                    │ │
│  │  5. [field-service] Response sent                      │ │
│  │                                                         │ │
│  │  Total duration: 666ms                                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Middleware Order of Execution

### FastAPI (Python)

```
Client Request
    │
    ▼
┌─────────────────────────────────────┐
│ 1. RequestLoggingMiddleware         │ ◄── Added last, executes first
│    - Generate correlation_id        │
│    - Start timer                    │
│    - Log request                    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 2. TenantContextMiddleware          │
│    - Extract tenant_id              │
│    - Validate tenant                │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 3. AuthMiddleware (if any)          │
│    - Validate JWT                   │
│    - Extract user_id                │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 4. RateLimitMiddleware              │
│    - Check rate limits              │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 5. CORSMiddleware                   │
│    - Handle CORS                    │
└────────────┬────────────────────────┘
             │
             ▼
     Route Handler
             │
             ▼
     Response Generated
             │
             ▼ (Middleware executes in reverse order)
┌─────────────────────────────────────┐
│ 1. RequestLoggingMiddleware         │ ◄── Executes last
│    - Calculate duration             │
│    - Log response                   │
│    - Add X-Correlation-ID header    │
└─────────────────────────────────────┘
             │
             ▼
      Client Response
```

### NestJS (TypeScript)

```
Client Request
    │
    ▼
┌─────────────────────────────────────┐
│ 1. Middleware (if any)              │
│    - CORS                           │
│    - Body Parser                    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 2. Guards (if any)                  │
│    - AuthGuard                      │
│    - TenantGuard                    │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ 3. Interceptors (Pre-execution)     │
│    - RequestLoggingInterceptor      │ ◄── Starts here
│      - Generate correlation_id      │
│      - Start timer                  │
│      - Log request                  │
└────────────┬────────────────────────┘
             │
             ▼
     Route Handler
             │
             ▼
┌─────────────────────────────────────┐
│ 4. Interceptors (Post-execution)    │
│    - RequestLoggingInterceptor      │
│      - Calculate duration           │
│      - Log response                 │
│      - Add X-Correlation-ID header  │
└────────────┬────────────────────────┘
             │
             ▼
      Client Response
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Code                          │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Import and Use                                         │ │
│  │                                                         │ │
│  │ Python:                                                │ │
│  │ from shared.middleware import (                        │ │
│  │     RequestLoggingMiddleware,                          │ │
│  │     get_correlation_id,                                │ │
│  │     get_request_context,                               │ │
│  │ )                                                      │ │
│  │                                                         │ │
│  │ TypeScript:                                            │ │
│  │ import {                                               │ │
│  │   RequestLoggingInterceptor,                           │ │
│  │   getCorrelationId,                                    │ │
│  │   getRequestContext,                                   │ │
│  │   StructuredLogger,                                    │ │
│  │ } from '../shared/middleware';                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Use in Handlers                                        │ │
│  │                                                         │ │
│  │ const correlationId = getCorrelationId(request);       │ │
│  │ const context = getRequestContext(request);            │ │
│  │ // { correlationId, tenantId, userId }                │ │
│  │                                                         │ │
│  │ // Use in logging                                      │ │
│  │ logger.info("Processing", context);                    │ │
│  │                                                         │ │
│  │ // Propagate to downstream services                    │ │
│  │ await callService({                                    │ │
│  │   headers: {                                           │ │
│  │     'X-Correlation-ID': correlationId,                 │ │
│  │     'X-Tenant-ID': context.tenantId,                   │ │
│  │   }                                                    │ │
│  │ });                                                    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```
