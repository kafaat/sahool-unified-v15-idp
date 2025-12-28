# SAHOOL Observability Infrastructure

**Production-ready observability stack following Google Cloud best practices**

## Overview

Comprehensive observability infrastructure for SAHOOL microservices, providing:

- **Distributed Tracing** with OpenTelemetry
- **Metrics Collection** with Prometheus
- **Structured Logging** with sensitive data masking
- **FastAPI Middleware** for auto-instrumentation
- **AI/Agent Metrics** with token usage and cost tracking
- **Health Checks** for dependencies
- **Google Cloud Integration** (Cloud Trace, Cloud Logging, Cloud Monitoring)

## Components

### 1. Distributed Tracing (`tracing.py`)

**Features:**
- OpenTelemetry SDK integration
- Google Cloud Trace exporter
- OTLP exporter support
- Auto-instrumentation for FastAPI, HTTPX, Redis, AsyncPG
- Context propagation (W3C Trace Context + Google Cloud Trace format)
- Custom span attributes for agent calls
- Token usage tracking in spans

**Key Classes:**
- `TracingConfig` - Configuration for tracing setup
- `DistributedTracer` - Main tracer class with auto-instrumentation
- `trace_function` - Decorator for tracing functions
- `get_tracer()` - Get global tracer instance

**Usage:**
```python
from shared.observability import setup_tracing

tracer = setup_tracing(
    service_name="my-service",
    service_version="1.0.0",
    gcp_project_id="your-project-id"
)
tracer.instrument_fastapi(app)
```

### 2. Metrics Collection (`metrics.py`)

**Features:**
- Prometheus-compatible metrics
- Request latency histograms
- Token usage counters
- Cost tracking for AI/LLM services
- Agent success/failure rates
- Cache hit/miss rates
- Custom metrics support

**Key Classes:**
- `MetricsCollector` - Base metrics collector
- `AgentMetrics` - AI/Agent-specific metrics
- `CostTracker` - LLM cost calculation utility
- `NDVIMetrics` - NDVI-specific metrics

**Metrics Exposed:**
- `{service}_requests_total` - Request counter by method/endpoint/status
- `{service}_request_duration_seconds` - Request latency histogram
- `{service}_errors_total` - Error counter by type/severity
- `ai_agent_tokens_used_total` - Token usage by agent/model/type
- `ai_agent_cost_usd_total` - Cumulative cost in USD
- `ai_agent_calls_total` - Agent call counter
- `ai_agent_cache_hits_total` - Cache hit counter

**Usage:**
```python
from shared.observability import AgentMetrics, CostTracker

agent_metrics = AgentMetrics()

# Record AI call
agent_metrics.record_agent_call(
    agent_name="crop_advisor",
    model="gpt-4",
    duration=2.5,
    prompt_tokens=150,
    completion_tokens=500,
    cost=CostTracker.calculate_cost("gpt-4", 150, 500),
    success=True
)
```

### 3. Structured Logging (`logging.py`)

**Features:**
- JSON formatted logs for production
- Colored output for development
- Request context propagation (request_id, tenant_id, user_id)
- Correlation IDs
- Sensitive data masking
- Automatic exception tracking

**Key Classes:**
- `ServiceLogger` - Service-specific logger with context
- `SensitiveDataMasker` - Automatic PII/credential masking
- `JSONFormatter` - Production JSON log formatter
- `ColoredFormatter` - Development colored formatter

**Masked Data:**
- API keys and tokens
- Passwords
- Authorization headers
- Database URLs with credentials
- AWS/GCP keys
- JWT tokens
- Credit card numbers
- Email addresses (partial)
- Phone numbers

**Usage:**
```python
from shared.observability import get_logger, set_request_context

logger = get_logger("my-service")

# Set request context
set_request_context(
    request_id="req-123",
    tenant_id="tenant-456",
    user_id="user-789"
)

# All logs include context
logger.info("Processing request", field_id="field-123")
```

### 4. FastAPI Middleware (`middleware.py`)

**Features:**
- Automatic tracing for all requests
- Request/response capture
- Trace header injection
- Metrics collection
- Request logging
- Error tracking

**Key Classes:**
- `ObservabilityMiddleware` - All-in-one observability middleware
- `RequestLoggingMiddleware` - Detailed request/response logging
- `MetricsMiddleware` - HTTP metrics collection
- `setup_observability_middleware()` - Helper function

**Usage:**
```python
from shared.observability import setup_observability_middleware

setup_observability_middleware(
    app,
    service_name="my-service",
    metrics_collector=metrics,
    enable_request_logging=False  # Only enable for debugging
)
```

### 5. Health Checks (`health.py`)

Pre-existing comprehensive health check system for monitoring service dependencies.

### 6. Endpoints (`endpoints.py`)

Pre-existing observability endpoints for metrics and debugging.

## Installation

```bash
cd /home/user/sahool-unified-v15-idp
pip install -r shared/observability/requirements.txt
```

## Quick Start

See [USAGE_EXAMPLE.md](./USAGE_EXAMPLE.md) for comprehensive examples.

### Minimal Setup

```python
from fastapi import FastAPI
from shared.observability import (
    setup_logging,
    setup_tracing,
    setup_observability_middleware,
    MetricsCollector,
    create_metrics_router,
)

app = FastAPI(title="My Service")

# Logging
logger = setup_logging("my-service", mask_sensitive=True)

# Tracing
tracer = setup_tracing("my-service", "1.0.0")
tracer.instrument_fastapi(app)

# Metrics
metrics = MetricsCollector("my_service")

# Middleware
setup_observability_middleware(app, "my-service", metrics)

# Endpoints
app.include_router(create_metrics_router(metrics.registry))

@app.get("/")
async def root():
    logger.info("Request received")
    return {"status": "ok"}
```

## Environment Variables

### Required
- `SERVICE_NAME` - Service name for tracing and metrics
- `ENVIRONMENT` - Environment (development, staging, production)

### Optional - Tracing
- `OTEL_EXPORTER_OTLP_ENDPOINT` - OTLP collector endpoint
- `OTEL_SAMPLE_RATE` - Trace sampling rate (0.0-1.0, default: 1.0)
- `OTEL_CONSOLE_EXPORT` - Enable console export (default: false)
- `GCP_PROJECT_ID` - Google Cloud project ID for Cloud Trace

### Optional - Logging
- `LOG_LEVEL` - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `MASK_SENSITIVE_DATA` - Enable sensitive data masking (default: true)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │       ObservabilityMiddleware                       │    │
│  │  • Auto-tracing                                     │    │
│  │  • Request ID generation                            │    │
│  │  • Context propagation                              │    │
│  │  • Metrics collection                               │    │
│  └────────────────────────────────────────────────────┘    │
│                           │                                  │
│  ┌────────────┬───────────┴──────────┬───────────────┐     │
│  │            │                       │               │     │
│  ▼            ▼                       ▼               ▼     │
│ Logging   Tracing                 Metrics         Health    │
│  │            │                       │               │     │
│  ▼            ▼                       ▼               ▼     │
│ JSON      OpenTelemetry          Prometheus      Checks     │
│ Logs      Spans/Traces            Counters/      Status     │
│  │            │                    Histograms       │       │
└──┼────────────┼────────────────────────┼───────────┼───────┘
   │            │                        │           │
   ▼            ▼                        ▼           ▼
┌─────┐  ┌──────────┐             ┌──────────┐  ┌────────┐
│ GCP │  │  Google  │             │Prometheus│  │ Health │
│ Log │  │  Cloud   │             │  Server  │  │Monitor │
│ging │  │  Trace   │             │          │  │        │
└─────┘  └──────────┘             └──────────┘  └────────┘
```

## Metrics Dashboard

Access Prometheus metrics at: `http://localhost:8000/metrics`

### Key Metrics to Monitor

1. **Request Rate**: `rate(my_service_requests_total[5m])`
2. **Error Rate**: `rate(my_service_errors_total[5m])`
3. **Latency p95**: `histogram_quantile(0.95, my_service_request_duration_seconds)`
4. **AI Token Usage**: `rate(ai_agent_tokens_used_total[1h])`
5. **AI Cost**: `sum(increase(ai_agent_cost_usd_total[1d])) by (model)`
6. **Cache Hit Rate**: `cache_hits / (cache_hits + cache_misses)`

## Google Cloud Integration

### Cloud Trace

Distributed traces are automatically exported to Google Cloud Trace when `GCP_PROJECT_ID` is set.

**View traces:**
- Console: https://console.cloud.google.com/traces
- Filter by service: `my-service`

### Cloud Logging

Structured JSON logs can be exported to Cloud Logging.

**Setup:**
```python
from google.cloud import logging as cloud_logging

# Initialize Cloud Logging
client = cloud_logging.Client()
client.setup_logging()
```

### Cloud Monitoring

Custom metrics can be exported to Cloud Monitoring for alerting.

## Best Practices

### 1. Correlation IDs
Always use request IDs to correlate logs, traces, and metrics across services.

### 2. Sampling
Use appropriate sampling rates for high-traffic services:
- Development: 1.0 (100%)
- Staging: 0.5 (50%)
- Production (high traffic): 0.1 (10%)

### 3. Sensitive Data
Always enable masking in production:
```python
logger = setup_logging("service", mask_sensitive=True)
```

### 4. Cost Monitoring
Monitor AI/LLM costs regularly:
```python
agent_metrics.record_agent_call(..., cost=cost)
```

### 5. Health Checks
Implement health checks for all dependencies:
```python
app.include_router(create_health_router())
```

## Performance Impact

- **Tracing**: ~2-5ms overhead per request (with sampling)
- **Metrics**: ~0.5-1ms overhead per request
- **Logging**: ~0.1-0.5ms overhead per log entry
- **Total**: ~3-7ms typical overhead

Optimize by:
- Using appropriate sampling rates
- Avoiding high-cardinality labels
- Batching span exports
- Async logging

## Troubleshooting

See [USAGE_EXAMPLE.md](./USAGE_EXAMPLE.md#troubleshooting) for common issues and solutions.

## Files

- `tracing.py` (509 lines) - Distributed tracing implementation
- `middleware.py` (396 lines) - FastAPI middleware
- `metrics.py` (666 lines) - Metrics collection with AI/Agent support
- `logging.py` (447 lines) - Structured logging with masking
- `__init__.py` (128 lines) - Package exports
- `requirements.txt` (152 lines) - Dependencies
- `USAGE_EXAMPLE.md` (428 lines) - Comprehensive usage guide
- `README.md` - This file

## License

Internal SAHOOL project - All rights reserved

## Support

For questions or issues, contact the SAHOOL Platform Team.

---

**Version**: 15.3.3
**Last Updated**: December 2024
**Status**: Production Ready ✅
