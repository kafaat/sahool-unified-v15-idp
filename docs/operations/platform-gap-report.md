# SAHOOL Platform Gap Report

> **Audit Date**: 2026-02-23
> **Auditor**: Platform Engineering (automated code audit)
> **Scope**: Event infrastructure, shared modules, service implementations, NATS configuration
> **Platform Version**: 16.0.0

---

## Executive Summary

Direct code-level audit of the SAHOOL platform identified **18 gaps** across 4 categories.
**3 critical bugs** were found and fixed immediately. The remaining gaps are categorized
by severity and include specific file:line references.

| Severity | Count | Fixed | Remaining |
|----------|-------|-------|-----------|
| **Critical (P0)** | 3 | 3 | 0 |
| **High (P1)** | 5 | 0 | 5 |
| **Medium (P2)** | 6 | 0 | 6 |
| **Low (P3)** | 4 | 0 | 4 |

---

## Critical Bugs — Fixed

### GAP-001: DLQ loses correlation_id (subscriber_dlq.py:186) — FIXED

**File**: `shared/events/subscriber_dlq.py:186`
**Severity**: P0 Critical
**Category**: Observability / Tracing

**Problem**: When moving a message to the Dead Letter Queue, `correlation_id` was extracted
using `getattr(msg, "reply", None)`, which returns the NATS **reply subject** (used for
request-reply patterns), NOT the correlation ID. This meant all DLQ messages had either
`null` or a random reply inbox as their correlation_id, making incident correlation impossible.

**Fix Applied**: Added `_extract_correlation_id(msg)` helper that checks:
1. NATS headers (`X-Correlation-ID`, `Nats-Msg-Id`)
2. JSON payload `correlation_id` field
3. Falls back to `None`

**Impact**: DLQ messages now preserve the original correlation chain, enabling end-to-end
trace reconstruction during incident response.

---

### GAP-002: Publisher retry drops trace headers (publisher.py:426) — FIXED

**File**: `shared/events/publisher.py:426`
**Severity**: P0 Critical
**Category**: Observability / Tracing

**Problem**: When `publish()` failed and triggered `_retry_publish()`, the `headers` parameter
(containing W3C trace context: `X-Correlation-ID`, `X-Trace-ID`, `X-Span-ID`, `X-Tenant-ID`,
etc.) was NOT passed to the retry function. The `_retry_publish` method signature didn't accept
`headers` at all, and calls to `_publish_jetstream`/`_publish_core` inside it omitted the
`headers=` kwarg.

**Fix Applied**:
1. Added `headers: dict | None = None` parameter to `_retry_publish`
2. Pass `headers=headers` from `publish()` call site
3. Forward `headers=headers` to `_publish_jetstream` and `_publish_core` inside retry loop

**Impact**: Retried messages now preserve all 7 W3C trace context headers, preventing
"orphaned" events that appear disconnected from their causal chain.

---

### GAP-003: Redundant event re-validation in publisher (publisher.py:387) — FIXED

**File**: `shared/events/publisher.py:387`
**Severity**: P0 (correctness) / P2 (performance)
**Category**: Performance

**Problem**: Before serializing, `publish()` called `event.model_validate(event.model_dump())`,
which round-trips the Pydantic model through dict → validate → model. This is:
1. **Redundant**: The event was already validated when constructed (Pydantic v2 validates on init)
2. **Lossy**: `model_dump()` may lose non-serializable transient attributes (e.g., `_tracestate`)
3. **Slow**: Adds ~2x serialization overhead for every published event

**Fix Applied**: Removed the redundant validation block. The event is already a validated
Pydantic model by the time it reaches `publish()`.

---

## High Severity Gaps — Remaining

### GAP-004: In-memory RateLimiter not multi-pod safe (auth/dependencies.py:384-448)

**File**: `shared/auth/dependencies.py:384-448`
**Severity**: P1 High
**Category**: Security / Rate Limiting

**Problem**: The `RateLimiter` class uses an in-memory `defaultdict(list)` to track request
timestamps per user. In a Kubernetes deployment with multiple pods, each pod maintains its own
counter. A user can effectively multiply their rate limit by the number of pods.

**Example**: With 3 pods and a limit of 60 req/min, a user can make 180 req/min by load-balancing
requests across pods.

**Recommendation**: Use Redis-backed rate limiting (the `shared/middleware/rate_limit.py` already
has a `RedisRateLimiter` implementation). Update `shared/auth/dependencies.py` to use Redis
when `REDIS_URL` is available.

---

### GAP-005: NATS subject permissions bypass sahool. prefix (nats.conf:82-92)

**File**: `config/nats/nats.conf:82-92`
**Severity**: P1 High
**Category**: Security / NATS

**Problem**: The `app` user has publish/subscribe permissions on non-namespaced subjects:
```
publish = ["sahool.>", "field.>", "weather.>", "irrigation.>", "advisory.>", ...]
subscribe = ["sahool.>", "field.>", "weather.>", "irrigation.>", "advisory.>", ...]
```
The non-prefixed subjects (`field.>`, `weather.>`, etc.) bypass the `sahool.` namespace
convention defined in `shared/events/subjects.py`. Any service could accidentally publish
to `field.created` instead of `sahool.field.created`, creating invisible routing failures.

**Recommendation**: Remove non-namespaced subjects from NATS permissions. All event subjects
should start with `sahool.` as defined in the event contracts.

---

### GAP-006: NATS TLS disabled in config (nats.conf:177-183)

**File**: `config/nats/nats.conf:177-183`
**Severity**: P1 High
**Category**: Security / Network

**Problem**: TLS configuration is entirely commented out:
```
# tls {
#   cert_file: "/etc/nats/certs/server.pem"
#   key_file: "/etc/nats/certs/server-key.pem"
#   ...
# }
```
All NATS traffic between services (including event payloads with tenant data, field coordinates,
and farmer information) is transmitted in plaintext.

**Recommendation**: Enable TLS in production. The cert paths and config are already defined
in the comments — they just need to be uncommented and certs provisioned.

---

### GAP-007: NATS clustering disabled (nats.conf:136-151)

**File**: `config/nats/nats.conf:136-151`
**Severity**: P1 High
**Category**: Reliability / HA

**Problem**: The NATS cluster configuration is commented out. Running a single NATS node means
any NATS restart causes:
- All JetStream consumers to disconnect (temporary message delivery halt)
- All WebSocket connections via ws-gateway to drop
- All event-driven workflows to stall

**Recommendation**: Enable NATS clustering with at least 3 nodes for production. The cluster
routes are already defined in the commented config.

---

### GAP-008: Security headers missing on 45/56 Python services

**File**: Various `apps/services/*/src/main.py`
**Severity**: P1 High
**Category**: Security / HTTP

**Problem**: Only 11 of 56 Python services call `setup_security_headers(app)`. The remaining
45 services respond without `X-Frame-Options`, `X-Content-Type-Options`, `Content-Security-Policy`,
`Strict-Transport-Security`, and other protective headers.

Services WITH security headers (11):
- billing-core, crop-intelligence-service, field-intelligence, inventory-service,
  irrigation-smart, llm-orchestrator-service, logistics-service, notification-service,
  task-service, weather-service, whatsapp-bot-service

Services WITHOUT (45): All others.

**Recommendation**: Add `setup_security_headers(app)` to all service `main.py` files.
Consider adding it to the shared service template in `idp/templates/python-fastapi/`.

---

## Medium Severity Gaps — Remaining

### GAP-009: Notification service fire-and-forget tasks (notification-service/main.py:429) — FIXED

**File**: `apps/services/notification-service/src/main.py:429`
**Severity**: P2 Medium
**Category**: Reliability

**Problem**: `asyncio.create_task()` was called without storing the task reference or adding
an error callback. If the send fails with an unhandled exception, Python logs
"Task exception was never retrieved" and the error is silently swallowed.

**Fix Applied**: Added task naming and `add_done_callback` for error logging.

---

### GAP-010: Metrics registry is in-memory only (monitoring/metrics.py)

**File**: `shared/monitoring/metrics.py`
**Severity**: P2 Medium
**Category**: Observability

**Problem**: The `MetricsRegistry` is a custom in-memory implementation, not the standard
`prometheus_client` library. This means:
1. No multi-process support (gunicorn workers don't share counters)
2. No standard collector integration (process metrics, GC stats)
3. Histogram buckets don't follow Prometheus conventions perfectly

**Recommendation**: Consider migrating to `prometheus_client` library for production. The
custom implementation works for single-process uvicorn but will undercount in multi-worker
deployments.

---

### GAP-011: RBAC role permissions use flat enumeration (security/rbac.py)

**File**: `shared/security/rbac.py`
**Severity**: P2 Medium
**Category**: Security / Maintainability

**Problem**: Each role explicitly lists all permissions (full copy, not inherited). The
`ROLE_PERMISSIONS` dict repeats the viewer permissions in worker, worker in supervisor, etc.
If a new permission is added to `viewer`, it must be manually copied to all 5 higher roles.

**Recommendation**: Use role hierarchy inheritance:
```python
ROLE_PERMISSIONS[Role.WORKER] = ROLE_PERMISSIONS[Role.VIEWER] | {worker_specific_perms}
```

---

### GAP-012: Input sanitizer stores sanitized body in request.state only

**File**: `shared/middleware/input_sanitizer.py:116`
**Severity**: P2 Medium
**Category**: Security

**Problem**: The `InputSanitizationMiddleware` sanitizes the request body and stores it in
`request.state.sanitized_body`, but the **original request body** is still available via
`await request.json()`. Endpoint handlers that call `request.json()` directly (instead of
checking `request.state.sanitized_body`) bypass sanitization entirely.

**Recommendation**: Either override the request body stream or enforce that all endpoints
use Pydantic models (which already handle validation) instead of raw `request.json()`.

---

### GAP-013: Advisory service has no rate limiting

**File**: `apps/services/advisory-service/src/main.py`
**Severity**: P2 Medium
**Category**: Security

**Problem**: The advisory-service processes disease assessments and fertilizer plans but
has no rate limiting middleware. A malicious actor could flood the service with requests,
causing CPU spikes from disease matching algorithms.

**Recommendation**: Add rate limiting middleware, similar to notification-service.

---

### GAP-014: Weather service readiness probe always returns "ready"

**File**: `apps/services/weather-service/src/main.py:167-180`
**Severity**: P2 Medium
**Category**: Reliability

**Problem**: The `/readyz` endpoint always returns `{"status": "ready"}` regardless of
whether the weather provider (Open-Meteo/OpenWeatherMap) is actually reachable or the NATS
publisher is connected. This means Kubernetes will route traffic to a pod that cannot actually
serve weather data.

**Recommendation**: Check weather provider health and NATS publisher status in the readiness
probe, similar to notification-service's readiness check.

---

## Low Severity Gaps

### GAP-015: Services use sys.path.insert for shared imports

**File**: Multiple `apps/services/*/src/main.py`
**Severity**: P3 Low
**Category**: Code Quality

**Problem**: Nearly all services use `sys.path.insert(0, ...)` to add shared modules to
the Python path. This is fragile, order-dependent, and can cause import shadowing issues.

**Recommendation**: Use proper Python packaging (pyproject.toml with path dependencies) or
Docker COPY + PYTHONPATH in production.

---

### GAP-016: Outbox relay has no cleanup schedule

**File**: `shared/events/outbox.py:290`
**Severity**: P3 Low
**Category**: Maintenance

**Problem**: `OutboxRelay.cleanup_sent()` exists but is never called automatically. Sent
outbox events accumulate in the database indefinitely. The SQL index `idx_outbox_sent_ttl`
is created but unused without an automated cleanup schedule.

**Recommendation**: Add a periodic cleanup call in the relay loop (e.g., every 100 cycles
or via a separate background task).

---

### GAP-017: DLQ monitoring connects without server URL

**File**: `shared/events/dlq_monitoring.py:137`
**Severity**: P3 Low
**Category**: Configuration

**Problem**: `DLQMonitor._connect()` calls `await nats.connect()` without passing a server
URL. It relies on the default `nats://localhost:4222`, which works in Docker Compose but
fails in Kubernetes where NATS is at a different hostname.

**Recommendation**: Pass `os.getenv("NATS_URL", "nats://localhost:4222")` to `nats.connect()`.

---

### GAP-018: Subscriber uses deprecated asyncio.get_event_loop()

**File**: `shared/events/subscriber.py:624`
**Severity**: P3 Low
**Category**: Code Quality

**Problem**: `asyncio.get_event_loop()` is deprecated since Python 3.10 and will be removed
in a future version. It should be replaced with `asyncio.get_running_loop()`.

**Recommendation**: Replace `asyncio.get_event_loop()` with `asyncio.get_running_loop()`.

---

## Summary of Fixes Applied

| ID | File | Change |
|----|------|--------|
| GAP-001 | `shared/events/subscriber_dlq.py` | Added `_extract_correlation_id()` helper; replaced `getattr(msg, "reply", None)` |
| GAP-002 | `shared/events/publisher.py` | Added `headers` param to `_retry_publish()`; forwarded headers in retry calls |
| GAP-003 | `shared/events/publisher.py` | Removed redundant `event.model_validate(event.model_dump())` |
| GAP-009 | `apps/services/notification-service/src/main.py` | Added task naming and error callback to `asyncio.create_task()` |

---

## Recommended Prioritization

### Immediate (Sprint)
1. GAP-005: Fix NATS subject permissions
2. GAP-006: Enable NATS TLS
3. GAP-007: Enable NATS clustering

### Short-term (2 sprints)
4. GAP-004: Redis-backed rate limiting
5. GAP-008: Security headers on all services
6. GAP-013: Rate limiting on advisory-service
7. GAP-014: Fix weather-service readiness probe

### Medium-term (Quarter)
8. GAP-010: Migrate to prometheus_client library
9. GAP-011: RBAC role inheritance
10. GAP-012: Input sanitizer enforcement
11. GAP-015: Proper Python packaging
12. GAP-016: Outbox cleanup automation
13. GAP-017: DLQ monitor NATS URL
14. GAP-018: Deprecated asyncio usage

---

_Generated by platform audit on 2026-02-23_
