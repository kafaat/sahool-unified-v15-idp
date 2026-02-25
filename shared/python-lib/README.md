# shared/python-lib - Python Library Utilities

مكتبة بايثون المشتركة

Core Python utility library for SAHOOL services. Provides fault-tolerant inter-service communication via a Circuit Breaker pattern that manages Kong API Gateway failover across primary, secondary, and tertiary endpoints.

## File Structure

```
shared/python-lib/
├── __init__.py
├── sahool_core/
│   ├── __init__.py          # Exports CircuitBreaker, CircuitState, circuit_breaker
│   └── resilient_client.py  # CircuitBreaker implementation
└── tests/
    ├── __init__.py
    └── test_circuit_breaker.py
```

## Key Components

### Circuit Breaker (`sahool_core/resilient_client.py`)

**`CircuitState`** (StrEnum):
- `CLOSED` - Normal operation, requests pass through
- `OPEN` - Circuit tripped, requests rejected immediately
- `HALF_OPEN` - Recovery probe in progress

**`CircuitBreaker`** - Fault-tolerant API caller with Kong failover:

Constructor parameters:
- `failure_threshold: int = 5` - Failures before opening circuit
- `recovery_timeout: int = 60` - Seconds before attempting HALF_OPEN recovery
- `endpoints: list[str]` - Kong endpoint URLs to try (default: primary, secondary, tertiary)

Default endpoints:
```
http://kong-primary:8000
http://kong-secondary:8000
http://kong-tertiary:8000
```

**`call(service, path, method, timeout, **kwargs)`** - Makes API calls with:
1. Circuit state check (rejects immediately if OPEN and timeout not elapsed)
2. Sequential endpoint failover (tries primary → secondary → tertiary)
3. Failure counting and automatic circuit opening
4. In-memory response cache as last-resort fallback when all endpoints fail
5. HALF_OPEN recovery: single probe attempt, closes circuit on success

**`circuit_breaker`** - Pre-configured singleton instance for convenience.

## Usage Example

```python
from shared.python_lib.sahool_core import CircuitBreaker, CircuitState, circuit_breaker

# Using the singleton
result = await circuit_breaker.call(
    service="field-management-service",
    path="/api/v1/fields",
    method="GET",
    timeout=5.0,
)

# Or a custom instance with different thresholds
breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=30,
    endpoints=[
        "http://kong-primary:8000",
        "http://kong-secondary:8000",
    ],
)

# Check current state
state = breaker._states.get("field-management-service", CircuitState.CLOSED)
if state == CircuitState.OPEN:
    print("Circuit is open - service temporarily unavailable")

# Make a service call with the circuit breaker
response = await breaker.call(
    service="advisory-service",
    path="/api/v1/recommendations",
    method="POST",
    json={"field_id": "FIELD-001", "crop": "wheat"},
    timeout=10.0,
)
```

## Circuit Breaker Behavior

```
Normal flow (CLOSED):
  Request → Kong Primary → Success → reset failure count

Failure flow:
  Request → Kong Primary fails → Kong Secondary fails → Kong Tertiary fails
          → Increment failure count
          → failure_count >= threshold → Open circuit

OPEN state:
  Request → Immediate rejection (no network call)
  → Return cached response if available

Recovery (after recovery_timeout):
  Circuit → HALF_OPEN → Single probe request
  → Success → CLOSED (reset)
  → Failure → OPEN (restart timer)
```

## Dependencies

- `aiohttp` (optional): Used for async HTTP calls. Gracefully handled if not installed (import guard with `None` fallback).

## Notes

- **Version**: 15.5.0 (this library predates the v16.0.0 platform unification)
- The in-memory cache provides stale-data resilience when all Kong nodes are unreachable
- Per-service circuit state is tracked independently (keyed by `service` parameter)
- This package is intended as a lightweight drop-in for services that need Kong failover without the full `shared/cache/` or `shared/ai/circuit_breaker.py` stacks
- For AI service circuit breaking, use `shared/ai/circuit_breaker.py` which includes Prometheus metrics
