# SAHOOL Platform Gap Analysis Report

**Date**: 2026-02-23
**Scope**: Full platform audit across 56 Python services
**Reference**: Event pipeline hardening completed in `crop-intelligence-service` and `notification-service`

---

## Executive Summary

After the successful 8-point event pipeline hardening of `crop-intelligence-service`, a comprehensive audit was conducted across all 56 Python FastAPI services. **The same categories of gaps found and fixed in crop-intelligence-service exist across virtually every other service on the platform.**

### Gap Statistics

| Category | Severity | Services Affected | Services Compliant |
|----------|----------|-------------------|-------------------|
| Raw NATS publish (no headers) | **CRITICAL** | ~30 services | 5 (via EventPublisher adapter) |
| No outbox pattern | **CRITICAL** | 55 services | 1 (crop-intelligence-service) |
| No DB idempotency (processed_events) | **HIGH** | 54 services | 2 (crop-intelligence-service, agro-rules*) |
| No `ensure_streams` call | **HIGH** | 55 services | 1 (crop-intelligence-service) |
| Missing unified error handling | **MEDIUM** | 12 services | 44 services |
| `print()` in production code | **MEDIUM** | 10 services | 46 services |
| NATS connection leak (no close) | **MEDIUM** | 2 services | ~36 services |
| No NATS subscriber headers extraction | **HIGH** | ~25 services | 1 (crop-intelligence-service) |

*agro-rules uses in-memory set dedup only, no DB-level idempotency*

---

## GAP-1: Raw NATS Publish Without Headers (CRITICAL)

### Problem

~30 services publish NATS events using raw `nc.publish()` without injecting the 7 canonical headers:
- `traceparent` (W3C Trace Context)
- `tracestate`
- `x-correlation-id`
- `x-causation-id`
- `x-event-id`
- `x-tenant-id`
- `x-schema-version`

This breaks distributed tracing, correlation analysis, and audit trails across the event-driven architecture.

### Affected Services (using raw nc.publish)

| Service | Location | Publish Count |
|---------|----------|---------------|
| cooperative-service | `src/api/v1/cooperatives.py` | 2 |
| drone-service | `src/api/v1/missions.py`, `flights.py` | 4 |
| pest-detection-service | `src/api/v1/pests.py` | 1 |
| digital-twin-engine | `src/main.py` | 1 |
| fertigation-engine | `src/main.py` | 1 |
| irrigation-smart | `src/main.py` | 1 |
| irrigation-cycle-engine | `src/main.py` | 1 |
| iot-sensor-hub | `src/main.py` | 3 |
| indicators-service | `src/main.py` | 1 |
| hydrology-service | `src/main.py` | 1 |
| field-intelligence | `src/api/routes.py` | 1 |
| leveling-optimizer-service | `src/api/endpoints/leveling.py` | 2 |
| terrain-core-service | `src/main.py` | 1 |
| soil-analysis-service | `src/api/v1/soil_tests.py` | 4 |
| traceability-service | `src/api/v1/batches.py` | 2 |
| skills-service | `src/main.py` | 1 |
| ussd-gateway | `src/main.py` | 1 |
| provider-config | `src/main.py` | 2 |
| edge-orchestrator-service | `src/main.py` | 1 |
| crop-intelligence-service | `src/calibration_router.py`, `twin_router.py` | 2 (outside main subscriber) |

### Services Using EventPublisher (Compliant)

| Service | Pattern |
|---------|---------|
| inventory-service | Shared EventPublisher adapter |
| globalgap-compliance | Shared EventPublisher adapter |
| field-management-service | Shared EventPublisher adapter |
| task-service | Shared EventPublisher adapter |
| crm-service | `get_publisher()` from shared |

### Services With Custom Publishers (Partial Compliance)

| Service | Custom Publisher | Has Headers? |
|---------|-----------------|-------------|
| yolo26-vision-service | VisionEventPublisher | **No** |
| alert-service | AlertEventPublisher | **No** |
| weather-service | Custom publish module | **No** |
| advisory-service | Custom publish module | **No** |
| iot-gateway | Custom publish module | **No** |
| ground-vision-service | Custom publishers | **No** |
| copilot-api | Custom publisher | **No** |
| ai-chat-assistant | Custom publisher | **No** |

### Recommendation

Migrate all services to use `shared.events.publisher.EventPublisher` which already implements header injection. Priority:
1. **Decision Layer** (irrigation-smart, advisory-service, fertigation-engine) - affects farmer recommendations
2. **Intelligence Layer** (indicators-service, field-intelligence, terrain-core-service) - affects data pipeline
3. **IoT/Acquisition Layer** (iot-sensor-hub, iot-gateway, weather-service) - high event volume

---

## GAP-2: No Outbox Pattern (CRITICAL)

### Problem

Only `crop-intelligence-service` uses the transactional outbox pattern (`shared/events/outbox.py`). All other services publish events directly via NATS, meaning:
- If NATS is down, events are silently lost
- No at-least-once delivery guarantee
- No retry mechanism for failed publishes
- Database writes can succeed while event publish fails (data inconsistency)

### Impact

The `shared/events/outbox.py` module and `shared/libs/outbox/` both exist and are fully implemented, but **adoption is zero** outside of crop-intelligence-service's subscriber code.

### Recommendation

Priority adoption for services with transactional data + event publish:
1. **field-management-service** - Field CRUD → events (most critical business entity)
2. **task-service** - Task lifecycle → events
3. **billing-core** - Financial transactions → events
4. **inventory-service** - Inventory changes → events
5. **notification-service** - Already a subscriber, needs outbox for forwarding

---

## GAP-3: No DB-Level Idempotency (HIGH)

### Problem

Only 2 services implement event deduplication:
- `crop-intelligence-service`: Full DB-level (`processed_events` table with `_check_processed`/`_mark_processed`)
- `agro-rules`: In-memory set only (lost on restart, no persistence)

All other NATS subscribers will reprocess duplicate events on:
- JetStream redelivery after ack timeout
- Service restart during processing
- Network partition recovery

### Affected NATS Subscribers

| Service | Subscribes To | Has Dedup? |
|---------|---------------|------------|
| notification-service | `sahool.decision.recommendation.*` | **No** |
| vegetation-analysis-service | Field events | **No** |
| weather-service | Weather events | **No** |
| advisory-service | Advisory events | **No** |
| irrigation-smart | Irrigation events | **No** |
| alert-service | Alert events | **No** |
| virtual-sensors | Sensor events | **No** |
| iot-gateway | IoT events | **No** |
| ws-gateway | Multiple subjects | **No** |

### Migration Required

Each subscribing service needs:
1. `migrations/001_idempotency_constraints.sql` creating the `processed_events` table
2. `_check_processed()` / `_mark_processed()` calls in every handler
3. LRU in-memory cache for hot-path dedup before DB check

---

## GAP-4: No ensure_streams Call (HIGH)

### Problem

`shared/events/streams.py` defines JetStream stream configurations (FIELD, INTELLIGENCE, DECISION, BUSINESS) with proper dedup windows, retention policies, and subject mappings. However, only `crop-intelligence-service` calls `ensure_streams()` at startup.

Without `ensure_streams()`:
- Streams may not exist when services try to publish/subscribe
- Stream configuration drift between services
- No dedup window enforcement at JetStream level

### Recommendation

Every service that connects to NATS should call `ensure_streams(js)` in its lifespan startup. This is a single-line addition per service.

---

## GAP-5: Missing Unified Error Handling (MEDIUM)

### Problem

12 Python services do not use `shared.errors_py` for unified exception handling and request ID middleware:

| Service | `setup_exception_handlers` | `add_request_id_middleware` |
|---------|---------------------------|---------------------------|
| ai-advisor | Has setup | **Missing request ID** |
| ai-agents-service | **Missing** (custom impl) | Custom impl |
| ai-chat-assistant | **Missing** | **Missing** |
| code-fix-agent | **Missing** | **Missing** |
| copilot-api | **Missing** | **Missing** |
| crm-service | **Missing** (custom impl) | Custom impl |
| edge-orchestrator-service | **Missing** | **Missing** |
| leveling-optimizer-service | **Missing** | **Missing** |
| lowcode-engine | **Missing** (custom impl) | Custom impl |
| pest-detection-service | **Missing** | **Missing** |
| supply-chain-service | **Missing** | **Missing** |
| wechat-service | **Missing** (custom impl) | Custom impl |
| yolo26-vision-service | **Missing** | **Missing** |

### Impact

- Inconsistent error response format across services
- No request ID propagation for debugging
- Harder to correlate logs across service boundaries

---

## GAP-6: print() in Production Code (MEDIUM)

### Problem

10 services use `print()` statements in production code instead of `structlog`:

| Service | print() Count | Location |
|---------|--------------|----------|
| vegetation-analysis-service | 13 | `src/main.py` |
| lowcode-engine | 11 | `src/main.py` |
| wechat-service | 11 | `src/main.py` |
| iot-gateway | 20 | `src/main.py` |
| crm-service | 9 | `src/main.py` |
| ai-agents-service | 8 | `src/main.py` |
| weather-service | 7 | `src/main.py` |
| virtual-sensors | 6 | `src/main.py` |
| inventory-service | 1 | `src/main.py` |

### Impact

- No structured logging for these services
- Cannot be parsed by log aggregation (ELK/Loki)
- Missing context fields (tenant_id, request_id, trace_id)

---

## GAP-7: NATS Connection Resource Leak (MEDIUM)

### Problem

2 services connect to NATS but never close the connection on shutdown:

| Service | NATS connect | NATS close | Status |
|---------|-------------|------------|--------|
| globalgap-compliance | 1 | **0** | **LEAK** |
| ws-gateway | 3 | **0** | **LEAK** |

### Impact

- Connection pool exhaustion over time
- Stale consumers remaining after service restart
- NATS server resource waste

---

## GAP-8: No NATS Subscriber Header Extraction (HIGH)

### Problem

When NATS messages arrive with the 7 canonical headers, subscribers need to extract them for:
- Distributed tracing continuation
- Correlation ID propagation
- Tenant isolation verification

Only `crop-intelligence-service/src/event_subscribers.py` implements `_extract_headers()`. All other subscribers ignore incoming headers entirely.

---

## Priority Remediation Plan

### Phase 1: Critical (Week 1-2)

| Action | Services | Effort |
|--------|----------|--------|
| Migrate to EventPublisher | irrigation-smart, advisory-service, fertigation-engine, indicators-service | ~2h each |
| Add ensure_streams to lifespan | All 38 NATS-connected services | ~15min each |
| Add outbox to field-management-service | field-management-service | ~4h |

### Phase 2: High (Week 3-4)

| Action | Services | Effort |
|--------|----------|--------|
| Add processed_events + idempotency | notification-service, vegetation-analysis-service, alert-service | ~3h each |
| Migrate remaining raw publishers | 20+ services | ~1h each |
| Add header extraction to subscribers | All subscribing services | ~1h each |

### Phase 3: Medium (Week 5-6)

| Action | Services | Effort |
|--------|----------|--------|
| Add unified error handling | 12 services | ~30min each |
| Replace print() with structlog | 10 services | ~1h each |
| Fix NATS connection leaks | globalgap-compliance, ws-gateway | ~30min each |

---

## Summary

The event pipeline hardening applied to `crop-intelligence-service` established the correct pattern. The platform now has a **reference implementation** but needs systematic rollout to remaining services. The most critical gaps are:

1. **~30 services publish events without trace headers** → breaks observability
2. **55 services lack outbox pattern** → events can be silently lost
3. **54 services lack DB-level idempotency** → duplicate processing risk
4. **55 services don't call ensure_streams** → JetStream config drift

All the infrastructure code exists in `shared/events/` — the gap is **adoption**, not implementation.
