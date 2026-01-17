# Observability Guide

## Overview

SAHOOL platform includes comprehensive observability features for monitoring, debugging, and maintaining services in production.

## Components

### 1. Health Checks

All services expose standardized health check endpoints:

#### Endpoints

- **`GET /health/live`** - Liveness probe
  - Returns 200 if service is running
  - Used by Kubernetes to restart crashed containers
- **`GET /health/ready`** - Readiness probe
  - Returns 200 if service can handle requests
  - Returns 503 if dependencies are unavailable
  - Used by Kubernetes to route traffic
- **`GET /health/startup`** - Startup probe
  - Returns 200 when service initialization is complete
  - Used by Kubernetes for slow-starting containers
- **`GET /health`** - Combined health check
  - Returns overall service health status
  - Includes all component checks

#### Example Response

```json
{
  "service": "crop-health-ai",
  "version": "2.2.0",
  "status": "healthy",
  "uptime_seconds": 3600.5,
  "timestamp": "2024-12-19T22:00:00.000Z",
  "components": [
    {
      "name": "database",
      "status": "healthy",
      "message": "Database connection OK"
    },
    {
      "name": "redis",
      "status": "healthy",
      "message": "Redis connection OK"
    }
  ]
}
```

#### Integration Example

```python
from shared.observability import HealthChecker, create_health_router

# Initialize health checker
health_checker = HealthChecker("my-service", "1.0.0")

# Add dependency checks
async def check_database():
    # Test database connection
    await db.execute("SELECT 1")
    return {"status": "healthy", "message": "Database OK"}

health_checker.add_readiness_check("database", check_database)

# Add health router to FastAPI app
app.include_router(create_health_router(health_checker))
```

### 2. Metrics (Prometheus)

Services expose metrics in Prometheus format at `/metrics`.

#### Default Metrics

All services automatically track:

- **Request count** - Total requests by method, endpoint, and status
- **Request duration** - Histogram of request latencies
- **Error count** - Total errors by type and severity
- **Active connections** - Current number of active requests

#### Custom Metrics

```python
from shared.observability import MetricsCollector

metrics = MetricsCollector("my-service")

# Create custom counter
cache_hits = metrics.create_counter(
    "cache_hits_total",
    "Total cache hits",
    labels=["cache_type"]
)

# Increment counter
cache_hits.labels(cache_type="redis").inc()

# Create histogram
processing_time = metrics.create_histogram(
    "processing_duration_seconds",
    "Processing time",
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0]
)

# Observe value
processing_time.observe(2.5)
```

#### Viewing Metrics

1. **Service metrics**: `curl http://localhost:8000/metrics`
2. **Prometheus UI**: http://localhost:9090
3. **Grafana dashboards**: http://localhost:3002

### 3. Structured Logging

All services use structured JSON logging for production and human-readable logs for development.

#### Configuration

```python
from shared.observability import setup_logging, set_request_context

# Initialize logger
logger = setup_logging(
    "my-service",
    level="INFO",
    json_output=True  # JSON for production, False for development
)

# Log with context
logger.info("Processing request", user_id="123", field_id="456")

# Set request context (propagated to all logs)
set_request_context(
    request_id="req_abc123",
    tenant_id="tenant_001",
    user_id="user_123"
)
```

#### Log Format

**Development (human-readable):**

```
[INFO    ] [2024-12-19 22:00:00] [my-service] [req:abc123] Processing request
```

**Production (JSON):**

```json
{
  "timestamp": "2024-12-19T22:00:00.000Z",
  "level": "INFO",
  "logger": "my-service",
  "message": "Processing request",
  "service": "my-service",
  "request_id": "req_abc123",
  "tenant_id": "tenant_001",
  "user_id": "user_123",
  "source": {
    "file": "/app/main.py",
    "line": 42,
    "function": "process_request"
  }
}
```

### 4. Distributed Tracing (OpenTelemetry)

Optional distributed tracing with OpenTelemetry.

#### Configuration

Set environment variable:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

#### Integration

```python
from shared.observability import setup_opentelemetry, instrument_fastapi

# Setup OpenTelemetry
tracer = setup_opentelemetry(
    service_name="my-service",
    service_version="1.0.0"
)

# Instrument FastAPI app
instrument_fastapi(app, "my-service")

# Manual instrumentation
with tracer.start_as_current_span("process_data") as span:
    span.set_attribute("data_size", len(data))
    result = process_data(data)
```

## Kubernetes Configuration

### Deployment with Health Checks

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crop-health-ai
spec:
  template:
    spec:
      containers:
        - name: app
          image: crop-health-ai:latest
          ports:
            - containerPort: 8095

          # Liveness probe
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8095
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3

          # Readiness probe
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8095
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 2

          # Startup probe (for slow-starting services)
          startupProbe:
            httpGet:
              path: /health/startup
              port: 8095
            initialDelaySeconds: 0
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 30
```

### ServiceMonitor for Prometheus

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: crop-health-ai
spec:
  selector:
    matchLabels:
      app: crop-health-ai
  endpoints:
    - port: metrics
      interval: 30s
      path: /metrics
```

## Alert Rules

Example Prometheus alert rules:

```yaml
groups:
  - name: service_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(service_errors_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on {{ $labels.service }}"
          description: "Error rate is {{ $value }} errors/sec"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(service_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time on {{ $labels.service }}"
          description: "95th percentile is {{ $value }}s"

      - alert: ServiceDown
        expr: up{job="sahool-services"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.service }} is down"
```

## Grafana Dashboards

### Key Metrics to Monitor

1. **Request Rate**: Requests per second by endpoint
2. **Error Rate**: Errors per second by type
3. **Response Time**: P50, P95, P99 latencies
4. **Active Connections**: Current concurrent requests
5. **Database Pool**: Connection pool usage
6. **Cache Hit Rate**: Cache hits vs misses

### Example PromQL Queries

```promql
# Request rate
rate(service_requests_total[5m])

# Error rate
rate(service_errors_total[5m])

# P95 latency
histogram_quantile(0.95, rate(service_request_duration_seconds_bucket[5m]))

# Active connections
service_active_connections

# Cache hit rate
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
```

## Troubleshooting

### High Error Rate

1. Check `/health` endpoint for unhealthy components
2. Review logs with `request_id` from failing requests
3. Check metrics for specific error types
4. Review traces in OpenTelemetry (if enabled)

### High Latency

1. Check database connection pool usage
2. Review slow query logs
3. Check cache hit rate
4. Analyze request traces
5. Review P95/P99 latency by endpoint

### Service Not Ready

1. Check `/health/ready` for component status
2. Verify database connectivity
3. Check Redis connectivity
4. Review startup logs
5. Verify environment configuration

## Best Practices

1. **Always add health checks** for critical dependencies
2. **Use structured logging** for all log messages
3. **Add custom metrics** for business-critical operations
4. **Set appropriate timeouts** for health checks
5. **Monitor cache hit rates** and adjust TTLs
6. **Use request IDs** for request tracing
7. **Set up alerts** for critical metrics
8. **Review metrics regularly** to identify trends
