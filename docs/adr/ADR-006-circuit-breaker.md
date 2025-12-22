# ADR-006: Circuit Breaker Pattern

## Status

Accepted

## Context

SAHOOL's distributed architecture requires fault tolerance for:

1. **Cascading failures**: One service failure can bring down others
2. **Network unreliability**: Yemen's infrastructure has intermittent connectivity
3. **Graceful degradation**: Users should see cached data vs errors
4. **Self-healing**: Services should recover automatically

We needed a pattern to prevent system-wide failures when individual services fail.

## Decision

We implemented the **Circuit Breaker Pattern** with a custom Python client.

### Key Features

1. **Three states**: CLOSED (normal), OPEN (failing), HALF_OPEN (testing)
2. **Multi-endpoint failover**: Tries all Kong nodes before failing
3. **Automatic recovery**: Resets after recovery timeout
4. **Fallback cache**: Returns cached data when circuit is open
5. **Service-specific defaults**: Sensible fallbacks per service type

### Implementation Pattern

```python
from sahool_core import circuit_breaker

# Simple API call with automatic failover
result = await circuit_breaker.call(
    service="field-ops",
    path="/api/v1/fields",
    method="GET",
    timeout=5.0
)

# Check if result is fallback data
if result.get("_fallback"):
    logger.warning("Using cached/fallback data")
```

### State Machine

```
                 ┌───────────────────────────┐
                 │                           │
    Success      │                           │  Failure
    ┌────────────┴────┐                 ┌────┴─────────────┐
    │                 │   Failures ≥    │                  │
    │     CLOSED      │   threshold     │      OPEN        │
    │  (Normal flow)  ├────────────────▶│ (Reject calls)   │
    │                 │                 │                  │
    └────────────────┬┘                 └─────────┬────────┘
             ▲       │                            │
             │       │                            │ Recovery
             │       │                            │ timeout
             │       │         ┌──────────────────┘
             │       │         │
             │       │         ▼
             │       │  ┌─────────────────┐
             │       │  │                 │
             │       └──│   HALF_OPEN     │
             │          │ (Test recovery) │
             │          │                 │
             │          └────────┬────────┘
             │                   │
             └───────────────────┘
                  Success
```

### Configuration

```python
circuit_breaker = CircuitBreaker(
    failure_threshold=5,      # Open after 5 failures
    recovery_timeout=60,      # Try again after 60 seconds
    endpoints=[               # Kong HA endpoints
        "http://kong-primary:8000",
        "http://kong-secondary:8000",
        "http://kong-tertiary:8000",
    ]
)
```

## Consequences

### Positive

- **Fault isolation**: Failed services don't crash callers
- **Graceful degradation**: Users see cached data, not errors
- **Self-healing**: Automatic recovery when service returns
- **Observability**: Status endpoint for monitoring
- **Performance**: Fast failure when circuit is open

### Negative

- **Complexity**: Additional abstraction layer
- **Stale data**: Fallback data may be outdated
- **Tuning required**: Thresholds need adjustment per service
- **Memory usage**: Caches consume additional memory

### Neutral

- Requires aiohttp for async HTTP calls
- Each service needs appropriate fallback data

## Alternatives Considered

### Alternative 1: Kong Health Checks Only

**Rejected because:**
- Only handles node-level failures
- Client still sees errors during failover
- No fallback data capability

### Alternative 2: Istio/Envoy Circuit Breaker

**Considered because:**
- Infrastructure-level solution
- No application code changes

**Rejected because:**
- Heavyweight infrastructure dependency
- Complex configuration
- Overkill for current deployment

### Alternative 3: resilience4j/Polly

**Rejected because:**
- Not native to Python ecosystem
- Additional dependency complexity
- Our needs are simpler

## Monitoring

```python
# Get circuit breaker status
status = circuit_breaker.get_status()
# {
#     "services": {
#         "field-ops": {
#             "state": "closed",
#             "failures": 0,
#             "last_failure": "N/A"
#         }
#     },
#     "endpoints": [...],
#     "config": {...}
# }

# Health check all endpoints
health = await circuit_breaker.health_check()
# {"http://kong-primary:8000": True, ...}
```

## References

- [Martin Fowler - Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Microsoft - Circuit Breaker Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker)
- [SAHOOL Circuit Breaker Implementation](../../shared/python-lib/sahool_core/resilient_client.py)
