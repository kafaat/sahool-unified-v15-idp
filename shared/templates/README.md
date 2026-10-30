# shared/templates - Service Configuration Templates

قوالب خدمات سهول

Reference implementation template demonstrating best practices for SAHOOL Python FastAPI services. Provides a working example that integrates all standard platform components: health checks, Prometheus metrics, OpenTelemetry tracing, structured logging, rate limiting, secrets management, and request context propagation.

## File Structure

```
shared/templates/
├── __init__.py          # Minimal package init
└── service_template.py  # Full reference service implementation
```

## What `service_template.py` Demonstrates

The template is a complete, runnable FastAPI service that shows how to wire together all SAHOOL shared modules. It is intended as a copy-and-adapt starting point when creating a new microservice.

### Integrated Components

| Component | From Module | Description |
|-----------|-------------|-------------|
| Health checks | `shared/observability` | `/healthz`, `/readyz`, `/startup` liveness/readiness probes |
| Prometheus metrics | `shared/observability` | `MetricsCollector`, `/metrics` endpoint |
| OpenTelemetry | `shared/observability` | `setup_opentelemetry`, `instrument_fastapi` |
| Structured logging | `shared/observability` | `setup_logging` with JSON output in production |
| Rate limiting | `shared/middleware/rate_limit` | `RateLimiter` with tier-based configs (`TierConfig`) |
| Security config | `shared/security/config` | `get_config`, `is_production`, `get_cors_origins` |
| Request context | `shared/observability` | `set_request_context`, `get_trace_context`, `clear_request_context` |

### Service Constants Pattern

```python
SERVICE_NAME = "example-service"
SERVICE_VERSION = "1.0.0"
SERVICE_PORT = int(get_config("SERVICE_PORT", default="8000", cast_type=int))
```

### Initialization Pattern

```python
# Logging
logger = setup_logging(SERVICE_NAME, level=get_log_level(), json_output=is_production())

# Metrics
metrics = MetricsCollector(SERVICE_NAME)
metrics.set_info(version=SERVICE_VERSION, environment=get_environment())

# OpenTelemetry
setup_opentelemetry(SERVICE_NAME)

# Lifespan context manager pattern
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: db pool, nats, warm-up
    yield
    # shutdown: close connections

app = FastAPI(title=SERVICE_NAME, version=SERVICE_VERSION, lifespan=lifespan)
instrument_fastapi(app)  # Auto-instrument all routes with OTel

# Health and metrics routers
app.include_router(create_health_router(checker))
app.include_router(create_metrics_router(metrics))
```

### Rate Limiter Setup

```python
limiter = RateLimiter(
    tiers={
        "starter":      TierConfig(requests_per_minute=30),
        "professional": TierConfig(requests_per_minute=60),
        "enterprise":   TierConfig(requests_per_minute=120),
    }
)
app.add_middleware(limiter.as_middleware())
```

### Request Context Per-Request

```python
@app.middleware("http")
async def context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    set_request_context(request_id=request_id, service=SERVICE_NAME)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        clear_request_context()
```

## How to Use This Template

1. Copy `service_template.py` to your new service directory as `src/main.py`
2. Replace `SERVICE_NAME` and `SERVICE_PORT` with your service's values
3. Add your domain-specific routes using `APIRouter`
4. Remove the `sys.path.insert` hacks - use proper package imports once the service is integrated
5. Update the `lifespan` function with your database and NATS connection logic

## Notes

- The template uses `sys.path.insert(0, "../../../../shared")` as a temporary workaround for standalone testing. In production services, import via the installed `shared` package or Docker volume mount.
- See `idp/templates/python-fastapi/skeleton/` for the IDP (Backstage) scaffolding version of this template, which generates a complete service directory from scratch.
- The `governance/templates/` directory contains additional templates for API definitions, backend workers, and data pipeline services.
- All new Python services must implement `/healthz` and `/readyz` endpoints as shown in this template (required by Kubernetes probes and Kong health checks).
