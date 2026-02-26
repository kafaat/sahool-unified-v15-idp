# shared/monitoring - SAHOOL Agricultural Monitoring Module

Comprehensive monitoring infrastructure for the SAHOOL Agricultural Intelligence
Platform. Covers Prometheus metrics, SLI/SLO definitions, Kubernetes-compatible
health checks, agricultural domain types for remote sensing, and structured JSON
logging.

**Version**: 16.0.0 | **Python**: >= 3.11

---

## Components

### metrics.py - Prometheus Metrics Registry

Lightweight Prometheus-format metrics registry that instruments FastAPI
services with HTTP request counters, latency histograms, and active-request
gauges. Also provides decorators for tracking database queries and external
service calls.

```python
from shared.monitoring.metrics import setup_metrics, get_registry, track_db_query

# Attach to FastAPI app - adds /metrics endpoint + HTTP middleware
from fastapi import FastAPI
app = FastAPI()
setup_metrics(app, service_name="advisory-service")

# Custom metric via the global registry
registry = get_registry("advisory-service")
advisory_counter = registry.counter(
    "advisories_generated_total",
    "Total advisory recommendations generated",
    labels={"service": "advisory-service"},
)
advisory_counter.inc()

latency_histogram = registry.histogram(
    "advisory_generation_seconds",
    "Time to generate an advisory",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0],
)
latency_histogram.observe(0.42)

# Decorator for database queries
@track_db_query
async def fetch_crop_data(field_id: str):
    ...

# Decorator for external calls
from shared.monitoring.metrics import track_external_call

@track_external_call("sentinel-hub")
async def fetch_ndvi(field_id: str):
    ...
```

The `/metrics` endpoint emits standard Prometheus text format including
counters, gauges, histograms with cumulative buckets, and an uptime gauge.

---

### agricultural_metrics.py - Agricultural Domain Metrics

Domain-specific Prometheus metrics for the full agricultural stack: NDVI,
weather, irrigation, crop health, yield, IoT sensors, and AI inference.
Requires `prometheus_client` to be installed; degrades gracefully if absent.

```python
from shared.monitoring.agricultural_metrics import get_agricultural_metrics

agri = get_agricultural_metrics()   # singleton

# Record an NDVI calculation from Sentinel-2
agri.record_ndvi_calculation(
    field_id="FIELD-003",
    ndvi_value=0.72,
    crop_type="wheat",
    satellite_source="sentinel-2",
    tenant_id="tenant-uuid",
    region="riyadh",
)

# Record weather data
agri.record_weather_update(
    region="riyadh",
    temperature=28.5,
    humidity=35.0,
    et0=5.5,        # Reference evapotranspiration mm/day
)

# Record disease detection from YOLO vision service
agri.record_disease_detection(
    disease_type="wheat_rust",
    crop_type="wheat",
    severity="high",
)

# Record irrigation event
agri.record_irrigation_event(
    field_id="FIELD-003",
    water_volume_liters=25000,
    irrigation_type="drip",
    crop_type="wheat",
)

# Set crop health score (0-100)
agri.set_crop_health_score(field_id="FIELD-003", crop_type="wheat", score=82.5)

# Record AI model inference
agri.record_ai_inference(
    model_name="yolo26-medium",
    duration_seconds=0.0055,
    success=True,
)

# Context manager for timing field operations
with agri.measure_operation("ndvi_analysis"):
    result = run_ndvi_pipeline(field_id)
```

**Metric categories** (all prefixed `sahool_`):

| Category | Key Metrics |
|----------|------------|
| Fields | `fields_total`, `field_area_hectares_total`, `field_operations_total` |
| NDVI | `ndvi_calculations_total`, `ndvi_value`, `ndvi_anomalies_total`, `ndvi_last_update_timestamp_seconds` |
| Weather | `weather_temperature_celsius`, `weather_humidity_percent`, `et0_mm_per_day`, `weather_alerts_total` |
| Irrigation | `irrigation_events_total`, `irrigation_water_volume_liters_total`, `soil_moisture_percent` |
| Crop Health | `crop_health_score`, `disease_detections_total`, `pest_detections_total`, `weed_detections_total` |
| Yield | `yield_predictions_total`, `yield_predicted_tons_per_hectare`, `yield_prediction_accuracy_percent` |
| IoT | `iot_devices_total`, `iot_readings_total`, `iot_battery_level_percent`, `iot_offline_devices_total` |
| AI/ML | `ai_inference_total`, `ai_inference_duration_seconds`, `ai_advisory_total`, `vision_detections_total` |
| Business | `active_users_gauge`, `api_requests_total`, `notifications_sent_total` |

---

### sli_slo.py - Service Level Indicators and Objectives

Google SRE-style SLI/SLO definitions for all SAHOOL services, with a central
registry, tier-based targets, error budget calculations, and Prometheus
burn-rate alert rule export.

```python
from shared.monitoring.sli_slo import (
    get_slo_registry, get_service_slos,
    ServiceTier, SLIType,
)

# Platform-wide registry (pre-populated for all known services)
registry = get_slo_registry()

# Look up SLOs for a service
slos = get_service_slos("field-management-service")
print(slos.tier)           # ServiceTier.ESSENTIAL
for slo in slos.slos:
    print(slo.name, slo.target, slo.error_budget_percent)
    # field-management-service_availability  0.995  0.5%

# Filter by tier
critical = registry.get_slos_by_tier(ServiceTier.CRITICAL)
# [postgres, redis, nats]

# Export Prometheus alerting rules (YAML)
rules_yaml = registry.export_prometheus_rules()
```

**Service tier targets** (30-day rolling window):

| Tier | Availability | Latency P95 | Error Rate | Examples |
|------|-------------|-------------|------------|---------|
| CRITICAL | 99.9% | 99.9% < 100ms | < 0.1% | PostgreSQL, Redis, NATS |
| ESSENTIAL | 99.5% | 99% < 300ms | < 0.5% | field-management, user-service |
| STANDARD | 99.0% | 95% < 500ms | < 1% | advisory, weather, irrigation |
| ANALYTICS | 95.0% | 90% < 5s | < 2% | YOLO26, NDVI, terrain, yield |

**Agricultural domain SLIs** included out of the box: NDVI data freshness
(hours), weather data freshness (minutes), IoT sensor freshness (minutes), AI
inference latency P95, and advisory correctness ratio.

---

### health_enhanced.py - Kubernetes Health Probes

Three-probe health architecture (liveness, readiness, startup) with dependency
tracking, circuit breakers (5-consecutive-failure threshold), graceful shutdown
signaling, and optional `psutil`-based performance metrics.

```python
from shared.monitoring.health_enhanced import (
    EnhancedHealthChecker, DependencyType, CheckSeverity,
    check_postgres, check_redis, check_nats, check_disk_space,
    create_health_router,
)

checker = EnhancedHealthChecker(
    service_name="advisory-service",
    service_name_ar="خدمة الاستشارات",
    version="16.0.0",
)

# Register liveness check (is the process alive?)
checker.register_liveness_check(
    name="self",
    check_func=lambda: True,
    severity=CheckSeverity.CRITICAL,
)

# Register readiness checks (can the service handle traffic?)
checker.register_readiness_check(
    name="postgres",
    check_func=lambda: check_postgres(db_pool),
    dependency_type=DependencyType.DATABASE,
    name_ar="قاعدة البيانات",
    severity=CheckSeverity.CRITICAL,
)
checker.register_readiness_check(
    name="redis",
    check_func=lambda: check_redis(redis_client),
    dependency_type=DependencyType.CACHE,
)
checker.register_readiness_check(
    name="nats",
    check_func=lambda: check_nats(nc),
    dependency_type=DependencyType.MESSAGE_QUEUE,
)
checker.register_readiness_check(
    name="disk",
    check_func=check_disk_space,      # threshold_percent=85 default
    dependency_type=DependencyType.STORAGE,
    severity=CheckSeverity.WARNING,
)

# Mount FastAPI router - exposes /health/live, /health/ready,
#                         /health/startup, /health, /healthz, /readyz
app.include_router(create_health_router(checker))

# Graceful shutdown (stops readiness from returning 200)
import signal
signal.signal(signal.SIGTERM, lambda *_: checker.begin_graceful_shutdown())
```

Health reports include Kubernetes probe flags (`live`, `ready`,
`startup_complete`), per-dependency latency in milliseconds, circuit breaker
state, and optional memory/CPU metrics.

---

### structured_logging.py - JSON Structured Logger

Production-grade structured logging with JSON output, OpenTelemetry trace
correlation via context variables, automatic sensitive-data masking, and
domain-specific convenience methods.

```python
from shared.monitoring.structured_logging import (
    get_structured_logger, LogCategory,
    set_log_context, clear_log_context, log_operation,
)

logger = get_structured_logger("advisory-service")
# JSON output in production, colored console in development

# Set request-scoped context (propagates automatically to all log calls)
set_log_context(
    trace_id="abc123",
    request_id="req-456",
    tenant_id="tenant-uuid",
    field_id="FIELD-003",
)

# Domain-specific log methods
logger.log_request("POST", "/api/v1/advisory", 200, duration_ms=142.3)
logger.log_database_query("SELECT", "fields", duration_ms=5.2, rows_affected=1)
logger.log_field_event("ndvi_calculated", "FIELD-003", ndvi=0.72)
logger.log_ai_inference("crop-health-model", duration_ms=85.0, success=True)
logger.log_sensor_reading("SENSOR-01", "soil_moisture", 42.5, unit="%")

# Generic structured logging
logger.info("Advisory generated", LogCategory.ADVISORY,
            crop_type="wheat", field_id="FIELD-003", confidence=0.91)
logger.error("Inference failed", crop_type="wheat", model="yolo26")

# Timing decorator (sync + async)
@log_operation("ndvi_analysis", category=LogCategory.NDVI)
async def run_ndvi(field_id: str):
    ...

clear_log_context()
```

Sensitive keys (`password`, `token`, `api_key`, `secret`, etc.) are
automatically redacted to `***REDACTED***`. Email and phone fields are
partially masked. JSON output is compatible with ELK Stack, Grafana Loki,
Google Cloud Logging, and AWS CloudWatch.

---

### types.py - Agricultural Monitoring Domain Types

Pydantic/dataclass types for the 6 core monitoring products: crop distribution,
crop growth, crop maturity, seedling emergence, yield estimation, and vegetation
indices. Accuracy levels range from 95% (1-3m resolution economic crops) to
80% (30m regional analysis).

Key types: `VegetationIndices`, `CropGrowthStatus`, `CropMaturityStatus`,
`SeedlingStatus`, `YieldEstimate`, `SatelliteObservation`, `RiskAlert`.

Helper functions: `ndvi_to_growth_level()`, `growth_level_to_status()`,
`get_growth_status_ar()`, `get_maturity_stage_ar()`.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Controls JSON vs colored console logging |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `SERVICE_VERSION` | `1.0.0` | Injected into structured log records |

---

## File Reference

| File | Description |
|------|-------------|
| `metrics.py` | `MetricsRegistry`, `setup_metrics`, `track_db_query`, `track_external_call` |
| `agricultural_metrics.py` | `AgriculturalMetrics`, `get_agricultural_metrics`, 40+ domain metrics |
| `sli_slo.py` | `SLI`, `SLO`, `SAHOOLSLORegistry`, tier factories, Prometheus rule export |
| `health_enhanced.py` | `EnhancedHealthChecker`, K8s probes, `check_postgres/redis/nats`, `create_health_router` |
| `structured_logging.py` | `StructuredLogger`, `LogCategory`, `set_log_context`, `@log_operation` |
| `types.py` | Remote sensing types, vegetation indices, yield estimation, risk alerts |
