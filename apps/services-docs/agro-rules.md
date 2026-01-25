# Agro Rules Service Analysis

## Service Overview

| Attribute | Value |
|-----------|-------|
| **Service Name** | agro-rules |
| **Arabic Name** | عامل القواعد الزراعية |
| **Service Type** | Python NATS Worker (No HTTP API) |
| **Layer** | Intelligence |
| **Category** | Crop |
| **Version** | 16.0.0 (Dockerfile) / 15.3.3 (code) |
| **Path** | `/home/user/sahool-unified-v15-idp/apps/services/agro-rules` |
| **Port** | None (NATS-only worker) |
| **Protocol** | NATS (not HTTP) |
| **Status** | Active |

## Purpose

Event-driven rules engine that automatically generates agricultural tasks based on:
- NDVI (Normalized Difference Vegetation Index) data and anomalies
- Weather alerts and forecasts
- IoT sensor readings (soil moisture, temperature, salinity, etc.)
- Irrigation adjustment recommendations

The service subscribes to events from the Acquisition layer, evaluates agronomic rules, and creates tasks via the FieldOps API.

---

## Architecture

### Workers

The service contains two independent worker classes:

#### 1. AgroRulesWorker (`src/worker.py`)
Primary worker for NDVI and weather-based rules.

```
┌─────────────────────────────────────────────────────────────────┐
│                      AgroRulesWorker                            │
├─────────────────────────────────────────────────────────────────┤
│  Subscribes to:                                                 │
│    - sahool.ndvi.computed                                       │
│    - sahool.ndvi.anomaly                                        │
│    - sahool.weather.alert                                       │
│    - sahool.weather.irrigation_adjustment                       │
├─────────────────────────────────────────────────────────────────┤
│  Internal State:                                                │
│    - _recent_ndvi: dict[field_id, NDVI data]                   │
│    - _recent_weather: dict[field_id, weather data]             │
│    - _processed_events: set[event_id] (deduplication)          │
├─────────────────────────────────────────────────────────────────┤
│  Output:                                                        │
│    - Creates tasks via HTTP to field-management-service         │
└─────────────────────────────────────────────────────────────────┘
```

#### 2. IoTRulesWorker (`src/iot_worker.py`)
Secondary worker for IoT sensor-based rules.

```
┌─────────────────────────────────────────────────────────────────┐
│                      IoTRulesWorker                             │
├─────────────────────────────────────────────────────────────────┤
│  Subscribes to:                                                 │
│    - sahool.iot.sensor_reading                                  │
│    - sahool.iot.sensor.soil_moisture                            │
│    - sahool.iot.sensor.air_temperature                          │
│    - sahool.iot.sensor.soil_ec                                  │
├─────────────────────────────────────────────────────────────────┤
│  Internal State:                                                │
│    - _recent_readings: dict[field_id, list[readings]]          │
│    - _recent_tasks: dict[task_key, timestamp] (cooldown)       │
│    - _cooldown_minutes: 30 (duplicate prevention)              │
├─────────────────────────────────────────────────────────────────┤
│  Periodic:                                                      │
│    - Combined rule evaluation every 5 minutes                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## NATS Events Subscribed

### AgroRulesWorker Subscriptions

| Subject | Handler | Description |
|---------|---------|-------------|
| `sahool.ndvi.computed` | `_handle_ndvi_computed` | NDVI calculation results from vegetation-analysis-service |
| `sahool.ndvi.anomaly` | `_handle_ndvi_anomaly` | NDVI anomaly detection alerts |
| `sahool.weather.alert` | `_handle_weather_alert` | Weather alerts (heat, frost, rain, wind, disease risk) |
| `sahool.weather.irrigation_adjustment` | `_handle_irrigation_adjustment` | Irrigation adjustment recommendations |

### IoTRulesWorker Subscriptions

| Subject | Handler | Description |
|---------|---------|-------------|
| `sahool.iot.sensor_reading` | `_handle_sensor_reading` | Generic sensor readings |
| `sahool.iot.sensor.soil_moisture` | `_handle_sensor_reading` | Soil moisture readings |
| `sahool.iot.sensor.air_temperature` | `_handle_sensor_reading` | Air temperature readings |
| `sahool.iot.sensor.soil_ec` | `_handle_sensor_reading` | Soil electrical conductivity readings |

### Expected Event Payload Format

```json
{
  "event_id": "uuid",
  "tenant_id": "tenant-001",
  "aggregate_id": "field-001",
  "correlation_id": "uuid",
  "payload": {
    // Event-specific data
  }
}
```

---

## NATS Events Published

**IMPORTANT: This service does NOT publish any NATS events.**

Despite the README claiming it publishes `task.created` events, the actual implementation creates tasks via HTTP API calls to `field-management-service`, not NATS events.

---

## Agronomic Rule Processing

### 1. NDVI Rules (`src/rules.py`)

| Rule | Condition | Priority | Urgency | Task Type |
|------|-----------|----------|---------|-----------|
| Severe NDVI Drop | trend_7d <= -0.15 | urgent | 6 hours | inspection |
| Moderate NDVI Drop | trend_7d <= -0.10 | high | 24 hours | inspection |
| Very Low NDVI | ndvi_mean < 0.2 | high | 24 hours | inspection |
| Low NDVI | ndvi_mean < 0.35 | medium | 48 hours | inspection |
| Healthy Crop | trend_7d >= 0.05 AND ndvi_mean >= 0.5 | - | - | No task |

### 2. Weather Rules (`src/rules.py`)

| Alert Type | Severity | Priority | Urgency | Task Type |
|------------|----------|----------|---------|-----------|
| heat_stress | critical | urgent | 2 hours | emergency |
| heat_stress | high | urgent | 6 hours | irrigation |
| heat_stress | medium | high | 12 hours | monitoring |
| frost | critical/high | urgent | 2 hours | emergency |
| frost | medium | high | 6 hours | preparation |
| heavy_rain | critical/high | high | 6 hours | preparation |
| heavy_rain | medium | medium | 24 hours | inspection |
| strong_wind | critical/high | high | 4 hours | preparation |
| disease_risk | critical/high | high | 12 hours | inspection |
| disease_risk | medium | medium | 24 hours | monitoring |

### 3. Combined Rules (`src/rules.py`)

| Condition | Priority | Urgency | Task Type | Description |
|-----------|----------|---------|-----------|-------------|
| temp_c >= 35 AND ndvi_trend <= -0.08 | urgent | 4 hours | emergency | Compound heat + vegetation stress |
| humidity_pct >= 80 AND ndvi_mean < 0.4 | high | 12 hours | spray | Disease risk with weak plants |

### 4. Irrigation Adjustment Rules (`src/rules.py`)

| Condition | Priority | Urgency | Task Type | Description |
|-----------|----------|---------|-----------|-------------|
| adjustment_factor >= 1.3 | high | 6 hours | irrigation | Increase irrigation for dry conditions |
| adjustment_factor <= 0.6 | medium | 12 hours | irrigation | Reduce irrigation for wet conditions |

### 5. IoT Sensor Rules (`src/iot_rules.py`)

#### Single Sensor Rules

| Sensor Type | Condition | Priority | Urgency | Task Type |
|-------------|-----------|----------|---------|-----------|
| soil_moisture | < critical_low (10%) | urgent | 2 hours | irrigation |
| soil_moisture | < low (20%) | high | 6 hours | irrigation |
| soil_moisture | > high (80%) | medium | 24 hours | inspection |
| air_temperature | > critical_high (42C) | urgent | 1 hour | emergency |
| air_temperature | > high (38C) | high | 4 hours | inspection |
| air_temperature | < low (5C) | urgent | 2 hours | emergency |
| soil_temperature | > critical_high (40C) | high | 6 hours | manual |
| soil_temperature | > high (35C) | medium | 12 hours | irrigation |
| soil_ec | > critical_high (6.0 mS/cm) | urgent | 4 hours | irrigation |
| soil_ec | > high (4.0 mS/cm) | high | 12 hours | irrigation |
| air_humidity | > high (90%) | medium | 24 hours | inspection |
| air_humidity | < low (30%) | low | 48 hours | inspection |
| water_flow | = 0 | urgent | 2 hours | maintenance |
| water_level | < 20% | high | 6 hours | maintenance |

#### Crop-Specific Thresholds

| Crop | Soil Moisture (low/critical/high) | Soil Temp (low/high/critical) | Air Temp (low/high/critical) |
|------|-----------------------------------|------------------------------|------------------------------|
| default | 20 / 10 / 80 | 10 / 35 / 40 | 5 / 38 / 42 |
| tomato | 25 / 15 / 75 | 15 / 30 / 35 | 10 / 32 / 38 |
| wheat | 15 / 8 / 70 | 5 / 28 / 35 | - |
| coffee | 30 / 20 / 70 | 18 / 28 / 32 | 15 / 28 / 32 |

#### Combined IoT Rules

| Condition | Priority | Urgency | Task Type |
|-----------|----------|---------|-----------|
| air_temp >= high AND soil_moisture < low | urgent | 2 hours | irrigation |
| air_humidity > 85% AND leaf_wetness > 80% | high | 6 hours | spray |

---

## Task Types Generated

| Task Type | Arabic | Description |
|-----------|--------|-------------|
| inspection | فحص | Field inspection required |
| emergency | طوارئ | Immediate emergency action |
| irrigation | ري | Irrigation operation |
| spray | رش | Pesticide/fungicide application |
| preparation | تحضير | Preparation for weather event |
| monitoring | مراقبة | Ongoing monitoring |
| maintenance | صيانة | Equipment maintenance |
| manual | يدوي | Manual intervention |

---

## Priority Levels

| Priority | Arabic | Response Time |
|----------|--------|---------------|
| urgent | عاجل | < 6 hours |
| high | مرتفع | < 24 hours |
| medium | متوسط | < 48 hours |
| low | منخفض | < 1 week |

---

## Dependencies

### Python Dependencies (`requirements.txt`)

| Package | Version | Purpose |
|---------|---------|---------|
| nats-py | 2.9.0 | NATS client for event subscription |
| httpx | 0.28.1 | Async HTTP client for FieldOps API |
| python-dotenv | 1.0.1 | Environment variable loading |

### External Service Dependencies

| Service | Protocol | Endpoint | Purpose |
|---------|----------|----------|---------|
| NATS | nats:// | nats:4222 | Event subscription |
| field-management-service | HTTP | :3000 | Task creation via API |

### Docker-Compose Dependencies

```yaml
depends_on:
  nats:
    condition: service_healthy
  field-management-service:
    condition: service_healthy
```

---

## Environment Variables

### Documented Variables

| Variable | Description | Default in Code | Docker-Compose Value |
|----------|-------------|-----------------|---------------------|
| `NATS_URL` | NATS server URL | `nats://nats:4222` | `nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222` |
| `FIELDOPS_URL` | FieldOps service URL | `http://field-management-service:3000` (fieldops_client.py) / `http://fieldops:8080` (worker.py) | `http://field-management-service:3000` |
| `LOG_LEVEL` | Logging level | - | `${LOG_LEVEL:-INFO}` |
| `ENVIRONMENT` | Environment name | - | `${ENVIRONMENT:-development}` |

### Missing Environment Variables

| Variable | Expected Purpose | Status |
|----------|-----------------|--------|
| `SERVICE_NAME` | Service identification for logs/metrics | Not implemented |
| `JWT_SECRET_KEY` | Authentication if calling protected endpoints | Not used (no auth) |
| `METRICS_ENABLED` | Prometheus metrics toggle | Not implemented |
| `SENTRY_DSN` | Error tracking | Not implemented |

---

## Bugs, Issues, and Recommended Fixes

### Critical Issues

#### 1. Inconsistent FIELDOPS_URL Defaults
**Location**: `src/worker.py` line 22 vs `src/fieldops_client.py` line 14

**Problem**:
- `worker.py`: `FIELDOPS_URL = os.getenv("FIELDOPS_URL", "http://fieldops:8080")` (deprecated)
- `fieldops_client.py`: `FIELDOPS_URL = os.getenv("FIELDOPS_URL", "http://field-management-service:3000")` (correct)

**Impact**: If `FIELDOPS_URL` is not set, `worker.py` will try to connect to the deprecated `fieldops:8080` service.

**Fix**: Update `worker.py` line 22:
```python
FIELDOPS_URL = os.getenv("FIELDOPS_URL", "http://field-management-service:3000")
```

#### 2. Version Mismatch
**Location**: `src/__init__.py` vs `Dockerfile`

**Problem**:
- `src/__init__.py`: `__version__ = "15.3.3"`
- `Dockerfile`: `SERVICE_VERSION=16.0.0`

**Fix**: Update `src/__init__.py`:
```python
__version__ = "16.0.0"
```

#### 3. Test Import Paths Incorrect
**Location**: `tests/test_rules.py` line 5, `tests/test_iot_rules.py` line 5

**Problem**: Tests import from `kernel.services.agro_rules.src.rules` but the actual path is `apps/services/agro-rules/src/rules`.

**Fix**: Update imports to:
```python
from src.rules import (...)
# or
from apps.services.agro_rules.src.rules import (...)
```

### Medium Issues

#### 4. README Documentation Incorrect - Events Published
**Location**: `README.md` line 89-91

**Problem**: README claims the service publishes `task.created` events, but it actually calls HTTP API to create tasks.

**Fix**: Update README to:
```markdown
## Events Published

None - Tasks are created via HTTP API to field-management-service
```

#### 5. Governance Configuration Mismatch
**Location**: `governance/services.yaml` lines 774-783

**Problem**: Governance specifies:
- `port: 8151` - Service has no HTTP port
- `protocol: http` - Service is NATS-only
- `health_endpoint: "/healthz"` - No HTTP endpoints

**Fix**: Update governance to:
```yaml
agro-rules:
  port: null
  protocol: nats
  health_endpoint: null  # Uses Docker healthcheck
```

#### 6. Duplicate FieldOpsClient Class
**Location**: `src/iot_worker.py` lines 20-71

**Problem**: IoT worker defines its own `FieldOpsClient` class but `fieldops_client.py` already provides one with more features.

**Fix**: Remove duplicate class and import from fieldops_client:
```python
from .fieldops_client import FieldOpsClient
```

#### 7. Missing Correlation ID in IoT Worker
**Location**: `src/iot_worker.py` line 200-203

**Problem**: IoT worker doesn't extract or pass `correlation_id` from events to created tasks, breaking traceability.

**Fix**: Extract and pass correlation_id in `_handle_sensor_reading`:
```python
correlation_id = data.get("correlation_id")
# Pass to _create_task_from_recommendation
```

### Low Issues

#### 8. Hardcoded Tenant ID in IoT Worker
**Location**: `src/iot_worker.py` lines 132, 200

**Problem**: Falls back to `tenant_id = "default"` which may cause issues in multi-tenant deployments.

**Fix**: Require tenant_id in event payload or raise error:
```python
tenant_id = data.get("tenant_id")
if not tenant_id:
    logger.warning("Missing tenant_id in event, skipping")
    return
```

#### 9. Memory Leak Potential in Processed Events Set
**Location**: `src/worker.py` lines 37, 261-265

**Problem**: `_processed_events` set can grow unbounded between 60-second cleanup intervals. In high-throughput scenarios, this could cause memory issues.

**Fix**: Use LRU cache or time-based expiry:
```python
from functools import lru_cache
# or use cachetools.TTLCache
```

#### 10. No NATS Reconnection Handling
**Location**: `src/worker.py`, `src/iot_worker.py`

**Problem**: No error handling or reconnection logic if NATS connection is lost.

**Fix**: Add NATS reconnection options:
```python
await self.nc.connect(
    NATS_URL,
    reconnect_time_wait=2,
    max_reconnect_attempts=-1,
    error_cb=self._error_cb,
    disconnected_cb=self._disconnected_cb,
    reconnected_cb=self._reconnected_cb,
)
```

#### 11. No Observability Integration
**Problem**: No Prometheus metrics, no structured logging, no OpenTelemetry tracing.

**Fix**: Add shared observability:
```python
from shared.monitoring import setup_metrics
from shared.observability import setup_logging
```

#### 12. Healthcheck May Fail During Normal Operation
**Location**: `Dockerfile` line 68-69

**Problem**: Healthcheck uses `pgrep -f "python.*worker"` which may not match if entry point changes.

**Fix**: Use more reliable healthcheck or add `/healthz` endpoint with metrics.

---

## Data Flow Diagram

```
┌──────────────────────┐
│  vegetation-analysis │
│      service         │
└──────────┬───────────┘
           │ sahool.ndvi.computed
           │ sahool.ndvi.anomaly
           ▼
┌──────────────────────┐     ┌───────────────────────┐
│   weather-service    │     │      iot-gateway      │
└──────────┬───────────┘     └───────────┬───────────┘
           │ sahool.weather.*            │ sahool.iot.*
           ▼                             ▼
    ┌─────────────────────────────────────────────┐
    │              NATS Message Broker            │
    └─────────────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
┌───────────────────────┐   ┌───────────────────────┐
│   AgroRulesWorker     │   │    IoTRulesWorker     │
│                       │   │                       │
│  - NDVI rules         │   │  - Sensor rules       │
│  - Weather rules      │   │  - Combined rules     │
│  - Combined rules     │   │  - Crop thresholds    │
│  - Irrigation rules   │   │  - Cooldown logic     │
└───────────┬───────────┘   └───────────┬───────────┘
            │                           │
            └─────────────┬─────────────┘
                          │ HTTP POST /api/v1/operations
                          ▼
            ┌─────────────────────────────┐
            │  field-management-service   │
            │         :3000               │
            │                             │
            │  Creates tasks in database  │
            └─────────────────────────────┘
```

---

## File Structure

```
apps/services/agro-rules/
├── __init__.py              # Package marker
├── .dockerignore            # Docker ignore patterns
├── Dockerfile               # Container build (Python 3.11)
├── README.md                # Service documentation
├── requirements.txt         # Python dependencies
├── src/
│   ├── __init__.py         # Version: 15.3.3 (should be 16.0.0)
│   ├── worker.py           # Main AgroRulesWorker entry point
│   ├── rules.py            # NDVI, Weather, Combined, Irrigation rules
│   ├── iot_worker.py       # IoT sensor worker
│   ├── iot_rules.py        # IoT sensor threshold rules
│   └── fieldops_client.py  # HTTP client for field-management-service
└── tests/
    ├── __init__.py         # Test package marker
    ├── test_rules.py       # Tests for NDVI/Weather rules
    └── test_iot_rules.py   # Tests for IoT rules
```

---

## Docker Configuration

### Dockerfile Highlights

```dockerfile
# Base: Python 3.11 slim
# No HTTP port exposed (NATS-only worker)
# Runs as non-root user 'sahool'
# Healthcheck: pgrep -f "python.*worker"
# Entry point: python -m src.worker
```

### Resource Limits (docker-compose.yml)

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 384M
    reservations:
      cpus: '0.25'
      memory: 128M
```

---

## Testing

### Test Files

| File | Test Count | Coverage |
|------|------------|----------|
| `tests/test_rules.py` | 16 tests | NDVI, Weather, Combined, Irrigation rules |
| `tests/test_iot_rules.py` | 17 tests | Sensor rules, Crop thresholds, Combined rules |

### Running Tests

```bash
# Note: Tests have incorrect import paths that need fixing
cd apps/services/agro-rules
pytest tests/ -v
```

---

## Recommendations Summary

| Priority | Issue | Effort | Impact |
|----------|-------|--------|--------|
| Critical | Fix FIELDOPS_URL default | Low | High |
| Critical | Fix test import paths | Low | High |
| Medium | Update version to 16.0.0 | Low | Medium |
| Medium | Remove duplicate FieldOpsClient | Medium | Medium |
| Medium | Add correlation_id to IoT worker | Low | Medium |
| Medium | Fix README events documentation | Low | Low |
| Medium | Fix governance config | Low | Low |
| Low | Add NATS reconnection | Medium | Medium |
| Low | Add observability | High | Medium |
| Low | Improve memory management | Medium | Low |

---

## Related Services

| Service | Relationship |
|---------|-------------|
| vegetation-analysis-service | Produces NDVI events consumed by this service |
| weather-service | Produces weather alerts consumed by this service |
| iot-gateway | Produces sensor readings consumed by this service |
| field-management-service | Receives task creation requests from this service |
| indicators-service | May produce field indicators events |

---

*Document generated: 2026-01-25*
*Analysis based on: SAHOOL Platform v16.0.0*
