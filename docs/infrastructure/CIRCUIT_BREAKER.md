# Circuit Breaker Pattern

## نمط قاطع الدائرة

**Version:** 15.5.0
**Last Updated:** 2024-12-22

---

## Overview | نظرة عامة

The Circuit Breaker pattern prevents cascading failures in distributed systems by:

- **Detecting failures** across Kong endpoints
- **Opening circuit** after threshold exceeded
- **Providing fallback** data when services unavailable
- **Auto-recovery** after timeout period

---

## States | الحالات

```
    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │   ┌─────────┐    failures     ┌─────────┐               │
    │   │ CLOSED  │ ──────────────▶ │  OPEN   │               │
    │   │(Normal) │                 │(Failing)│               │
    │   └────▲────┘                 └────┬────┘               │
    │        │                           │                     │
    │        │ success              timeout                    │
    │        │                           │                     │
    │        │         ┌─────────┐       │                     │
    │        └─────────│HALF_OPEN│◀──────┘                     │
    │                  │(Testing)│                             │
    │                  └─────────┘                             │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
```

| State         | Description                | Behavior                             |
| ------------- | -------------------------- | ------------------------------------ |
| **CLOSED**    | Normal operation           | All requests pass through            |
| **OPEN**      | Failure threshold exceeded | Requests return fallback immediately |
| **HALF_OPEN** | Testing recovery           | One request allowed to test service  |

---

## Installation | التثبيت

### Python

```python
from sahool_core import circuit_breaker

# Or create custom instance
from sahool_core import CircuitBreaker

breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    endpoints=[
        "http://kong-primary:8000",
        "http://kong-secondary:8000",
        "http://kong-tertiary:8000",
    ]
)
```

---

## Usage | الاستخدام

### Basic API Call

```python
import asyncio
from sahool_core import circuit_breaker

async def get_fields():
    result = await circuit_breaker.call(
        service="field-ops",
        path="/api/v1/fields",
        method="GET",
        timeout=5.0
    )

    if result.get("_fallback"):
        print("Using cached/fallback data")

    return result

# Run
fields = asyncio.run(get_fields())
```

### With Custom Headers

```python
result = await circuit_breaker.call(
    service="satellite-service",
    path="/api/v1/ndvi/field/123",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10.0
)
```

### Health Check

```python
# Check all endpoint health
health = await circuit_breaker.health_check()
# Returns: {"http://kong-primary:8000": True, ...}

# Get circuit status
status = circuit_breaker.get_status()
print(status)
```

---

## Configuration | الإعداد

| Parameter           | Default      | Description                     |
| ------------------- | ------------ | ------------------------------- |
| `failure_threshold` | 5            | Failures before opening circuit |
| `recovery_timeout`  | 60           | Seconds to wait before testing  |
| `endpoints`         | Kong cluster | List of Kong endpoints          |

### Environment Variables

```bash
export CIRCUIT_FAILURE_THRESHOLD=5
export CIRCUIT_RECOVERY_TIMEOUT=60
export KONG_ENDPOINTS="http://kong-primary:8000,http://kong-secondary:8000"
```

---

## Fallback Behavior | سلوك الـFallback

When circuit is open or all endpoints fail:

### 1. Cache Check

Returns cached response if available:

```python
{
    "_fallback": True,
    "_cached_at": "2024-12-22T10:00:00",
    "data": [...]  # Cached data
}
```

### 2. Service-Specific Defaults

| Service              | Fallback Data                |
| -------------------- | ---------------------------- |
| field-ops            | Empty list with message      |
| weather-service      | Average temperature (25°C)   |
| notification-service | Queue notification for later |

### Custom Fallback

```python
class CustomCircuitBreaker(CircuitBreaker):
    async def _fallback(self, service: str, path: str):
        if service == "my-service":
            return {"custom": "fallback"}
        return await super()._fallback(service, path)
```

---

## Monitoring | المراقبة

### Logging

Circuit breaker logs important events:

```
[INFO] Circuit half-open for field-ops, attempting recovery
[CRITICAL] Circuit OPEN for field-ops after 5 failures
[INFO] Returning cached data for field-ops:/api/v1/fields
```

### Metrics

```python
status = circuit_breaker.get_status()
print(status)
# {
#     "services": {
#         "field-ops": {
#             "state": "closed",
#             "failures": 0,
#             "last_failure": "N/A"
#         }
#     },
#     "endpoints": ["http://kong-primary:8000", ...],
#     "config": {
#         "failure_threshold": 5,
#         "recovery_timeout": 60
#     }
# }
```

---

## Integration Examples | أمثلة التكامل

### FastAPI Service

```python
from fastapi import FastAPI, HTTPException
from sahool_core import circuit_breaker

app = FastAPI()

@app.get("/api/v1/analysis/{field_id}")
async def get_analysis(field_id: int):
    # Get NDVI data with circuit breaker
    ndvi = await circuit_breaker.call(
        service="satellite-service",
        path=f"/api/v1/ndvi/field/{field_id}"
    )

    # Get weather with circuit breaker
    weather = await circuit_breaker.call(
        service="weather-service",
        path=f"/api/v1/weather/field/{field_id}"
    )

    return {
        "field_id": field_id,
        "ndvi": ndvi,
        "weather": weather,
        "using_fallback": ndvi.get("_fallback") or weather.get("_fallback")
    }
```

### Background Task

```python
from sahool_core import circuit_breaker
import asyncio

async def sync_task():
    while True:
        try:
            result = await circuit_breaker.call(
                service="notification-service",
                path="/api/v1/notifications/pending"
            )

            if not result.get("_fallback"):
                # Process notifications
                pass

        except Exception as e:
            print(f"Sync error: {e}")

        await asyncio.sleep(60)
```

---

## Best Practices | أفضل الممارسات

1. **Always check `_fallback` flag** to handle degraded mode
2. **Set appropriate timeouts** per service type
3. **Implement service-specific fallbacks** for critical paths
4. **Monitor circuit states** in production
5. **Cache successful responses** for fallback use

---

## Troubleshooting | استكشاف الأخطاء

| Symptom                   | Cause               | Solution                              |
| ------------------------- | ------------------- | ------------------------------------- |
| Always returning fallback | Circuit stuck open  | Check Kong health, wait for recovery  |
| Slow responses            | High timeout values | Reduce timeout for non-critical calls |
| No caching                | Cache not populated | Ensure successful calls happen first  |
| All endpoints failing     | Network issue       | Check Docker network connectivity     |

---

**Related Documents:**

- [Kong HA Setup](./KONG_HA_SETUP.md)
- [Engineering Recovery Plan](../engineering/ENGINEERING_RECOVERY_PLAN.md)
