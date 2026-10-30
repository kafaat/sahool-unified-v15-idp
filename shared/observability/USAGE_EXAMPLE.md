# Observability Infrastructure - Usage Guide

## Overview

This document demonstrates how to integrate SAHOOL's comprehensive observability infrastructure into your FastAPI service.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r shared/observability/requirements.txt
```

### 2. Basic FastAPI Service Setup

```python
from fastapi import FastAPI
from shared.observability import (
    setup_logging,
    setup_tracing,
    setup_observability_middleware,
    MetricsCollector,
    AgentMetrics,
    create_metrics_router,
    create_health_router,
)

# Initialize FastAPI app
app = FastAPI(title="My SAHOOL Service")

# Setup logging with sensitive data masking
logger = setup_logging(
    service_name="my-service",
    level="INFO",
    json_output=True,  # Use JSON format in production
    mask_sensitive=True,  # Mask sensitive data
)

# Setup distributed tracing
tracer = setup_tracing(
    service_name="my-service",
    service_version="1.0.0",
    gcp_project_id="your-gcp-project",  # Optional: for Google Cloud Trace
)

# Instrument FastAPI app with tracing
tracer.instrument_fastapi(app)

# Setup metrics collector
metrics = MetricsCollector("my_service")
agent_metrics = AgentMetrics("my_service")

# Setup observability middleware
setup_observability_middleware(
    app,
    service_name="my-service",
    metrics_collector=metrics,
    enable_request_logging=False,  # Enable for debugging only
)

# Add metrics and health endpoints
app.include_router(create_metrics_router(metrics.registry))
app.include_router(create_health_router())

# Your service endpoints
@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Hello from SAHOOL!"}
```

## Advanced Usage

### 3. Custom Tracing with Spans

```python
from shared.observability import get_tracer, trace_function

# Using decorator
@trace_function("process_field_data")
async def process_field(field_id: str):
    logger.info(f"Processing field {field_id}")
    # Your processing logic
    return {"field_id": field_id, "status": "processed"}

# Using context manager
async def complex_operation(field_id: str):
    tracer = get_tracer()

    with tracer.span("fetch_field_data", attributes={"field_id": field_id}):
        # Fetch data
        data = await fetch_field_data(field_id)

    with tracer.span("analyze_data", attributes={"field_id": field_id}):
        # Analyze data
        result = analyze_data(data)

    return result
```

### 4. AI/Agent Call Tracking

```python
from shared.observability import get_tracer, AgentMetrics, CostTracker
import time

agent_metrics = AgentMetrics()

@app.post("/ai/crop-advice")
async def get_crop_advice(field_id: str):
    tracer = get_tracer()
    start_time = time.time()

    # AI call with tracing
    with tracer.span(
        "agent.crop_advisor",
        attributes={
            "agent.name": "crop_advisor",
            "agent.model": "gpt-4",
            "field.id": field_id,
        }
    ):
        # Make AI call
        response = await call_openai_api(
            model="gpt-4",
            prompt=f"Provide crop advice for field {field_id}"
        )

        # Calculate cost
        cost = CostTracker.calculate_cost(
            model="gpt-4",
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
        )

        # Record metrics
        agent_metrics.record_agent_call(
            agent_name="crop_advisor",
            model="gpt-4",
            duration=time.time() - start_time,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            cost=cost,
            success=True,
            response_length=len(response.choices[0].message.content),
        )

        logger.info(
            f"AI advice generated for field {field_id}",
            tokens=response.usage.total_tokens,
            cost=cost,
        )

        return {
            "advice": response.choices[0].message.content,
            "metadata": {
                "tokens_used": response.usage.total_tokens,
                "cost_usd": cost,
            }
        }
```

### 5. Custom Metrics

```python
from shared.observability import MetricsCollector

metrics = MetricsCollector("crop_service")

# Create custom metrics
irrigation_events = metrics.create_counter(
    "irrigation_events",
    "Total irrigation events",
    labels=["field_id", "event_type"]
)

ndvi_processing_time = metrics.create_histogram(
    "ndvi_processing_seconds",
    "NDVI processing duration",
    labels=["field_size"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Use custom metrics
@app.post("/irrigation/start")
async def start_irrigation(field_id: str):
    irrigation_events.labels(
        field_id=field_id,
        event_type="start"
    ).inc()

    # Your logic
    return {"status": "irrigation started"}

@app.post("/ndvi/process")
async def process_ndvi(field_id: str, field_size: str):
    with metrics.measure_time("ndvi_processing_seconds", {"field_size": field_size}):
        # Process NDVI
        result = await process_ndvi_data(field_id)

    return result
```

### 6. Structured Logging with Context

```python
from shared.observability import get_logger, set_request_context

logger = get_logger("my-service")

@app.middleware("http")
async def add_request_context(request, call_next):
    # Extract context from headers or auth
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    tenant_id = request.state.tenant_id if hasattr(request.state, "tenant_id") else None
    user_id = request.state.user_id if hasattr(request.state, "user_id") else None

    # Set context for logging
    set_request_context(
        request_id=request_id,
        tenant_id=tenant_id,
        user_id=user_id,
    )

    response = await call_next(request)
    return response

# All logs will include request_id, tenant_id, user_id
@app.get("/fields/{field_id}")
async def get_field(field_id: str):
    logger.info(
        f"Fetching field data",
        field_id=field_id,
        operation="get_field"
    )
    # Your logic
    return {"field_id": field_id}
```

### 7. Sensitive Data Masking

```python
from shared.observability import SensitiveDataMasker

# Mask sensitive data before logging
user_data = {
    "username": "farmer@example.com",
    "password": "secret123",
    "api_key": "sk_live_1234567890abcdef",
    "phone": "+1234567890",
}

# Automatically masks passwords, API keys, etc.
safe_data = SensitiveDataMasker.mask_dict(user_data)
logger.info("User data", **safe_data)

# Output: {"username": "farmer@***", "password": "***REDACTED***", ...}
```

### 8. Cache Metrics

```python
from shared.observability import AgentMetrics

agent_metrics = AgentMetrics()

@app.get("/ai/cached-advice/{field_id}")
async def get_cached_advice(field_id: str):
    # Check cache
    cached = await redis.get(f"advice:{field_id}")

    if cached:
        agent_metrics.record_cache_hit("crop_advisor")
        return {"advice": cached, "from_cache": True}

    # Cache miss - call AI
    agent_metrics.record_cache_miss("crop_advisor")

    advice = await call_ai_service(field_id)
    await redis.set(f"advice:{field_id}", advice, expire=3600)

    return {"advice": advice, "from_cache": False}
```

## Environment Variables

```bash
# Service Configuration
SERVICE_NAME=my-service
SERVICE_VERSION=1.0.0
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO
MASK_SENSITIVE_DATA=true

# OpenTelemetry Tracing
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=my-service
OTEL_SAMPLE_RATE=1.0
OTEL_CONSOLE_EXPORT=false

# Google Cloud (if using GCP)
GCP_PROJECT_ID=your-gcp-project
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Context Propagation
REQUEST_ID_HEADER=X-Request-ID
TENANT_ID_HEADER=X-Tenant-ID
USER_ID_HEADER=X-User-ID
```

## Monitoring Dashboards

### Grafana Dashboard Example

```json
{
  "dashboard": {
    "title": "SAHOOL Service Observability",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(my_service_requests_total[5m])"
          }
        ]
      },
      {
        "title": "AI Token Usage",
        "targets": [
          {
            "expr": "rate(ai_agent_tokens_used_total[1h])"
          }
        ]
      },
      {
        "title": "AI Cost",
        "targets": [
          {
            "expr": "sum(increase(ai_agent_cost_usd_total[1d])) by (model)"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "targets": [
          {
            "expr": "rate(ai_agent_cache_hits_total[5m]) / (rate(ai_agent_cache_hits_total[5m]) + rate(ai_agent_cache_misses_total[5m]))"
          }
        ]
      }
    ]
  }
}
```

## Best Practices

1. **Always use structured logging** - Include relevant context in log messages
2. **Mask sensitive data** - Enable `mask_sensitive=True` in production
3. **Use correlation IDs** - Track requests across services
4. **Monitor costs** - Track AI/LLM token usage and costs
5. **Set appropriate sampling rates** - Use lower rates for high-traffic services
6. **Add custom metrics** - Track business-specific metrics
7. **Implement health checks** - Monitor all critical dependencies
8. **Use context managers** - For automatic span management
9. **Log exceptions properly** - Use `logger.exception()` for full tracebacks
10. **Review traces regularly** - Identify performance bottlenecks

## Testing

```python
import pytest
from shared.observability import setup_logging, MetricsCollector

def test_logging():
    logger = setup_logging("test-service", json_output=False)
    logger.info("Test message")
    # No exceptions = success

def test_metrics():
    metrics = MetricsCollector("test-service")
    metrics.record_request("GET", "/test", 200, 0.1)
    # Verify metrics are recorded

def test_sensitive_masking():
    from shared.observability import SensitiveDataMasker

    data = {"password": "secret123", "username": "test"}
    masked = SensitiveDataMasker.mask_dict(data)

    assert masked["password"] == "***REDACTED***"
    assert masked["username"] == "test"
```

## Troubleshooting

### Issue: Traces not appearing in Google Cloud Trace

**Solution:**

- Verify `GCP_PROJECT_ID` is set correctly
- Ensure service account has Cloud Trace Agent role
- Check `GOOGLE_APPLICATION_CREDENTIALS` points to valid service account key

### Issue: High memory usage

**Solution:**

- Reduce trace sampling rate: `OTEL_SAMPLE_RATE=0.1`
- Use batch span processor (default)
- Monitor metric cardinality (avoid high-cardinality labels)

### Issue: Sensitive data in logs

**Solution:**

- Enable masking: `mask_sensitive=True`
- Add custom patterns to `SensitiveDataMasker.PATTERNS`
- Review logs in development before production deployment

## Additional Resources

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Google Cloud Observability](https://cloud.google.com/products/operations)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
