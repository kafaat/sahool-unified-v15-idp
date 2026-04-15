# SAHOOL NATS / Event Bus Audit

**Branch:** `claude/test-web-services-e2e-7OiHV`
**Date:** 2026-04-13
**Scope:** NATS infrastructure, event subject conventions, publishers,
subscribers, DLQ, and cross-language (Python ↔ TypeScript) interop.

> تدقيق شامل لبنية NATS وقنوات الأحداث في منصة سهول.

---

## 1. Executive Summary

| Item | Value |
|---|---|
| NATS broker | `nats:2.10.24-alpine` (docker-compose.yml:270) |
| Python services touching NATS | 56 / 94 |
| TypeScript services touching NATS | 3 (field-management, marketplace, iot) |
| Subject constants registered (Python `subjects.py`) | **379** |
| Subject constants registered (TS `EventSubjects`) | 14 |
| **Critical bugs found** | **2** |
| Critical bugs fixed in this commit | **2** ✅ |
| Recommendations remaining | 3 |

---

## 2. Topology

```
┌────────────────────┐    ┌────────────────────┐    ┌────────────────────┐
│ Python services    │    │ NATS 2.10.24       │    │ TS services        │
│ (FastAPI · 56)     │───▶│ JetStream + DLQ    │◀───│ (NestJS · 3)       │
│ shared/events/*    │    │ port 4222          │    │ @sahool/shared-events│
└────────────────────┘    └────────────────────┘    └────────────────────┘
        ▲                          │
        │                          ▼
        │                  ┌────────────────────┐
        └──────────────────│ Prometheus exporter│
                           │ port 7777          │
                           └────────────────────┘
```

- **Subject naming convention:** `sahool.<domain>.<entity>.<action>`
- **Tenant-scoped variants:** `sahool.tenant.<tenant_id>.<domain>.<action>`
  via `get_tenant_subject()`.
- **Wildcards:** `sahool.field.>` (recursive), `sahool.notification.*` (one level).
- **DLQ:** `shared/events/dlq_*.py` — auto-replay, monitoring, config.
- **Outbox pattern:** `shared/events/outbox.py` + `OutboxEvent` table in
  `field-management-service`.

---

## 3. Critical Bugs Found & Fixed

### 🔴 Bug #1 — Cross-language subject prefix drift (silent data loss)

**Severity:** Critical.

The TypeScript event-bus package `@sahool/shared-events` published events
**without** the mandatory `sahool.` prefix that every Python subscriber
listens for. End result: TypeScript-published events were silently
dropped at the broker level — they had no subscribers because no Python
service listens on `notification.send`, only on `sahool.notification.send`.

| Side | Subject published / subscribed | Match? |
|---|---|---|
| Python publisher (`shared/events/subjects.py`) | `sahool.notification.send` | — |
| Python subscriber (`notification-service` `nats_subscriber.py:65`) | `sahool.notification.*` | ✅ |
| TS publisher (`@sahool/shared-events` `publisher.ts:329`) | `notification.send` | ❌ **dropped** |
| TS convenience subscriber (`subscriber.ts:200`) | `notification.*` | ❌ would also miss every Python publish |

**Concrete impact:** `iot-service` publishes high-priority sensor alerts
(low/high moisture, frost, etc.) via `publishNotificationSend()`. Those
alerts went to subject `notification.send` and were never delivered to
notification-service. Push notifications for sensor anomalies silently
disappeared in production.

**Fix applied** in `packages/shared-events/`:
- `events.ts` — every `eventType` literal and the `EventSubjects` map
  prefixed with `sahool.`
- `publisher.ts` — every `publishEvent('<X>', …)` call prefixed
- `subscriber.ts` — every convenience subscriber's wildcard pattern
  prefixed (`'sahool.field.*'` not `'field.*'`)
- `__tests__/publisher.spec.ts` — updated all 14 expectations
- Tests pass: **21 / 21** ✓

### 🔴 Bug #2 — `iot-service` never initialises NATS

**Severity:** Critical (compounds Bug #1).

`iot-service/src/main.ts` did not call `initializeNatsClient()`
anywhere. It calls `publishNotificationSend()` from `iot.service.ts:1086`,
which internally does `NatsClient.getInstance(...).getConnection()` — and
because `connect()` was never called, `getConnection()` returned `null`
and the publisher threw `"NATS connection is not available"`. The
`.catch()` wrapper on the call site logs and swallows the error, so
**every sensor alert silently failed** even *after* fixing Bug #1.

**Fix applied** in `apps/services/iot-service/src/main.ts`:
```ts
import { initializeNatsClient, NatsClient } from "@sahool/shared-events";

async function bootstrap() {
  // Initialize NATS BEFORE Nest app starts so publishNotificationSend()
  // doesn't silently drop sensor alerts. Failure is non-fatal: HTTP/MQTT
  // still serve.
  try {
    await initializeNatsClient({
      servers: process.env.NATS_URL || "nats://nats:4222",
      name: "iot-service",
    });
  } catch (err) {
    console.warn(`[NATS] Connection failed (degraded mode): ${err}`);
  }
  // … existing app bootstrap …
}
```

Plus graceful drain on `SIGTERM` so in-flight publishes aren't lost.

---

## 4. NATS Wiring Coverage

### TypeScript services

| Service | NATS lib used | Subject convention | Init in main.ts | Verdict |
|---|---|---|---|---|
| field-management-service | raw `nats` | `sahool.field.*` (raw strings) | ✅ via `FieldEventsService.onModuleInit` | ✅ correct |
| marketplace-service | raw `nats` | `sahool.marketplace.*` (constants) | ✅ via own `EventsService` | ✅ correct |
| iot-service | `@sahool/shared-events` | now `sahool.*` (after fix) | ✅ (after fix) | ✅ fixed |
| user-service | — | n/a | ❌ no NATS | ⚠️ flagged in earlier audit |
| chat-service | — | n/a | ❌ no NATS | ⚠️ flagged |
| disaster-assessment | — | n/a | ❌ | OK (HTTP-only) |
| research-core | — | n/a | ❌ | OK (HTTP-only) |
| weather-service | — | n/a | ❌ | OK (read-through cache) |

### Python services

56 / 94 services connect to NATS via `shared/events/` — see `shared/events/subjects.py`
for the full subject catalogue (379 constants across 30+ domains).

Notable subscribers:
- `notification-service` → `sahool.notification.*`
- `indicators-service` → `sahool.field.created`, `sahool.satellite.ndvi.computed`
- `irrigation-smart` → `sahool.weather.forecast.issued`
- `ws-gateway` → `sahool.field.>` (fans out to WebSocket clients)
- `ussd-gateway` → `sahool.*.alert.*`
- `edge-orchestrator` → `sahool.tenant.*.edge.metrics`, `sahool.tenant.*.edge.detection`

---

## 5. DLQ & Reliability

| Capability | Implementation | Status |
|---|---|---|
| Dead Letter Queue | `shared/events/dlq_service.py`, `dlq_config.py` | ✅ active |
| Auto-replay | `shared/events/dlq_auto_replay.py` | ✅ |
| DLQ monitoring (Prometheus) | `shared/events/dlq_monitoring.py` | ✅ |
| Outbox / transactional publish | `shared/events/outbox.py` + `OutboxEvent` Prisma model | ✅ |
| Idempotency keys | `IdempotencyKey` model in field-management + marketplace | ✅ |
| TS reconnect-on-disconnect | `NatsClient.scheduleReconnect()` | ✅ infinite retries |
| TS connection-status logging | `setupEventHandlers` for `Disconnect`/`Reconnect`/`Error` | ✅ |
| Graceful drain on SIGTERM | field-management ✅ · marketplace ✅ · iot (after fix) ✅ | ✅ |

---

## 6. Best-Practice Verification

| Practice | Status | Note |
|---|---|---|
| Single subject convention `sahool.<domain>.<entity>.<action>` | ✅ (after fix) | Was broken on TS side |
| Tenant ID propagated in payload | ✅ | `tenantId` arg on every publish helper |
| OTel trace context propagated through events | ✅ | `_get_otel_trace_context()` in Python publisher |
| Correlation ID propagated | ✅ | `_get_current_correlation_id()` |
| Pydantic / TypeScript schema validation on payloads | ✅ | `BaseEvent` + `SahoolEvent` types in TS, `BaseEvent` in Python |
| DLQ for failed handlers | ✅ | configurable per subject |
| Bilingual error messages | ✅ | enforced in publish wrappers |
| Connection lifecycle managed (init + drain) | ✅ (after fix) | iot-service was missing init |

---

## 7. Remaining Recommendations (non-critical)

### R-1. Add NATS init to `user-service` and `chat-service` if cross-service events are needed
Both services use Prisma + NestJS but don't publish/subscribe to NATS.
- For **user-service**: it should publish `sahool.user.created`, `sahool.user.updated`, `sahool.user.role_changed` so audit-service and notification-service can react. Currently those events are emitted by no one.
- For **chat-service**: it should publish `sahool.chat.message.sent` so notification-service can route push notifications to offline users.

These are feature gaps, not bugs.

### R-2. Replace raw subject strings in `field-management-service/src/events/field-events.service.ts` with constants from `@sahool/shared-events.EventSubjects`
Currently the service uses string literals like `'sahool.field.created'`. After the Bug #1 fix, the constants in `EventSubjects.FIELD_CREATED` etc. now resolve to the correct values, so we can drop the raw strings and let the type-checker catch typos.

### R-3. Add CI guardrail forbidding event subjects without `sahool.` prefix
The `event-contracts-guard.yml` workflow already validates schema shape; extend it to grep for `publish('<not-sahool>...'` and fail the PR.

---

## 8. Files Changed in This Commit

| File | Change |
|---|---|
| `packages/shared-events/src/events.ts` | 14 `eventType` literals + `EventSubjects` map prefixed with `sahool.` |
| `packages/shared-events/src/publisher.ts` | 14 `publishEvent` calls prefixed |
| `packages/shared-events/src/subscriber.ts` | 7 wildcard patterns prefixed + JSDoc comment updated |
| `packages/shared-events/src/__tests__/publisher.spec.ts` | 14 `expect(subject).toBe('...')` updated |
| `apps/services/iot-service/src/main.ts` | Add `initializeNatsClient` on bootstrap + drain on SIGTERM |
| `apps/services/PRISMA_AUDIT.md` | (previous commit, kept here for navigation) |
| `apps/services/NATS_AUDIT.md` | this report |

---

## 9. Verification

```
$ cd packages/shared-events && npx tsc                  # build OK
$ npx vitest run packages/shared-events                  # 21 / 21 pass
$ cd apps/services/iot-service && npx tsc --noEmit       # 0 errors
$ cd apps/web && npx eslint .                            # ALL_CLEAN
$ ruff check apps/services shared                        # All checks passed
```

**Verdict:** The two critical cross-language bugs are fixed. Sensor alerts
from `iot-service` will now reach `notification-service` end-to-end on
the next deploy. All linters and type-checkers pass.
