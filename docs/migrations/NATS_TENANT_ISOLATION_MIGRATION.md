# NATS Tenant Isolation Migration Plan

# خطة ترحيل عزل المستأجرين في NATS

> **Status**: Planned
> **Priority**: HIGH - Security & Data Isolation
> **Estimated Effort**: 4-6 sprints (8-12 weeks)
> **Owner**: Platform Engineering Team
> **Created**: 2026-02-16
> **Last Updated**: 2026-02-16

---

## Executive Summary | ملخص تنفيذي

All 72+ active SAHOOL microservices currently publish NATS events using **flat subjects** (`sahool.{domain}.{action}`) with `tenant_id` embedded only in the JSON payload. This means **NATS-level tenant isolation does not exist** — any subscriber receives events from ALL tenants, and filtering relies entirely on application-level code.

This migration plan transitions the platform to **subject-level tenant isolation** using the pattern `sahool.tenant.{tenant_id}.{domain}.{action}`, which already has infrastructure support in `shared/events/subjects.py` but is not used by any service.

### Risk Assessment

| Risk | Level | Description |
|------|-------|-------------|
| **Cross-tenant data leakage** | HIGH | A subscriber bug could process another tenant's events |
| **No NATS ACL per tenant** | HIGH | Cannot enforce access control at the messaging layer |
| **Performance overhead** | MEDIUM | Every subscriber must deserialize + filter every message |
| **Audit gap** | MEDIUM | Cannot trace event flow per-tenant at infrastructure level |

---

## 1. Current State Analysis | تحليل الوضع الحالي

### 1.1 Subject Pattern (Current - Flat)

```
sahool.field.created          ← ALL tenants' field events on same channel
sahool.task.updated           ← ALL tenants' task events on same channel
sahool.vision.pest_detected   ← ALL tenants' vision events on same channel
```

### 1.2 Target Pattern (Tenant-Scoped)

```
sahool.tenant.{tenant_id}.field.created       ← Isolated per tenant
sahool.tenant.{tenant_id}.task.updated        ← Isolated per tenant
sahool.tenant.{tenant_id}.vision.pest_detected ← Isolated per tenant
```

### 1.3 Existing Infrastructure (Unused)

The following functions exist in `shared/events/subjects.py` (lines 548-699) but are **never called** by any service:

| Function | Purpose |
|----------|---------|
| `get_tenant_subject(tenant_id, domain, action)` | Build tenant-scoped subject |
| `get_tenant_wildcard(tenant_id, domain)` | Subscribe to all tenant events |
| `get_all_tenants_subject(domain, action)` | Admin: cross-tenant subscription |
| `TenantSubjectBuilder(tenant_id)` | Fluent builder for tenant subjects |

### 1.4 Services Inventory by Publishing Pattern

**Total publishing services**: ~37 actively publishing NATS events

#### Type A: Using `shared/events/publisher.py` (Recommended Pattern)
- field-management-service
- task-service
- globalgap-compliance

#### Type B: Custom inline publishers
- advisory-service
- weather-service
- iot-gateway
- yolo26-vision-service
- alert-service
- copilot-api
- ai-chat-assistant

#### Type C: Domain libraries in `shared/`
- shared/irrigation/
- shared/pest_scouting/
- shared/weather_alerts/
- shared/fertilizer_management/
- shared/soil_testing/
- shared/water_management/
- shared/equipment_maintenance/
- shared/crop_rotation/
- shared/harvest_quality/
- shared/drone_integration/
- shared/traceability/
- shared/market_prices/

#### Type D: Other services with NATS events
- notification-service (subscriber)
- ws-gateway (subscriber)
- edge-orchestrator-service
- ground-vision-service
- agro-rules
- ndvi-processor
- billing-core
- crm-service
- wechat-service
- lowcode-engine
- inventory-service

### 1.5 Active Subscribers

| Subscriber Service | Subject Pattern | Purpose |
|-------------------|----------------|---------|
| notification-service | `sahool.field.*`, `sahool.weather.*`, `sahool.billing.*` | Push notifications |
| ws-gateway | `sahool.field.*`, `sahool.task.*` | WebSocket relay |
| alert-service | `sahool.weather.*`, `sahool.health.*`, `sahool.satellite.*` | Alert generation |
| ground-vision-service | `sahool.*.satellite.*` | Vision pipeline |
| agro-rules | `sahool.weather.*`, `sahool.health.*` | Rule evaluation |
| edge-orchestrator | `sahool.*.edge.*` | Edge device mgmt |
| ndvi-processor | `sahool.satellite.*` | NDVI pipeline |

### 1.6 Event Domains (12 total, 80+ subjects)

| Domain | Subjects | Publishing Services |
|--------|----------|-------------------|
| `field` | 3 | field-management-service |
| `farm` | 3 | field-management-service |
| `weather` | 10 | weather-service |
| `satellite` | 12 | vegetation-analysis-service, ndvi-processor |
| `health` | 8 | crop-intelligence-service |
| `task` | 6 | task-service |
| `billing` | 6 | billing-core |
| `iot` | 6 | iot-gateway, iot-service |
| `vision` | 8 | yolo26-vision-service |
| `terrain` | 10 | terrain-core-service |
| `edge` | 19 | edge-orchestrator-service |
| `alerts` | 5 | alert-service |

---

## 2. Migration Strategy | استراتيجية الترحيل

### Approach: Dual-Publish with Gradual Subscriber Migration

```
Phase 1: Infrastructure    → Prepare shared libraries + JetStream streams
Phase 2: Dual Publishing   → Publishers emit on BOTH old and new subjects
Phase 3: Subscriber Migration → Migrate subscribers one-by-one to new subjects
Phase 4: Cleanup           → Remove old flat subjects, enforce tenant-only
```

### Why Dual-Publish?

- **Zero downtime**: No service interruption during migration
- **Rollback safe**: Subscribers can fall back to old subjects instantly
- **Independent pace**: Each subscriber migrates on its own schedule
- **Verifiable**: Can compare event counts on old vs new subjects

---

## 3. Phase 1: Infrastructure Preparation (Sprint 1-2)

### 3.1 Enhance `BaseEvent` Contract

**File**: `shared/events/contracts.py`

Add `tenant_id` as a **required** field in `BaseEvent` (currently only in domain events):

```python
class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=...)
    timestamp: datetime = Field(default_factory=...)
    version: str = Field(default="1.0")
    source_service: str | None = Field(None)
    correlation_id: str | None = Field(None)
    tenant_id: str = Field(..., description="Tenant identifier (required)")  # NEW
```

**Impact**: All event contracts already have `tenant_id` in their domain-specific fields, but making it part of `BaseEvent` ensures it's always present.

### 3.2 Enhance `EventPublisher` for Dual Publishing

**File**: `shared/events/publisher.py`

Add a `publish_tenant_event()` method that publishes to both subjects:

```python
async def publish_tenant_event(
    self,
    domain: str,
    action: str,
    event: BaseEvent,
    tenant_id: str | None = None,
    dual_publish: bool = True,  # Transition flag
) -> bool:
    """
    Publish event with tenant-scoped subject.
    During migration (dual_publish=True): publishes to BOTH subjects.
    After migration (dual_publish=False): publishes only to tenant subject.
    """
    tenant_id = tenant_id or event.tenant_id

    # New tenant-scoped subject
    tenant_subject = get_tenant_subject(tenant_id, domain, action)
    result = await self.publish_event(tenant_subject, event)

    # Legacy flat subject (during migration)
    if dual_publish:
        legacy_subject = f"sahool.{domain}.{action}"
        await self.publish_event(legacy_subject, event)

    return result
```

### 3.3 Enhance `EventSubscriber` for Tenant Filtering

**File**: `shared/events/subscriber.py`

Add tenant-aware subscription:

```python
async def subscribe_tenant(
    self,
    tenant_id: str | None,  # None = all tenants (admin services)
    domain: str,
    action: str = "*",
    handler: Callable,
    **kwargs,
) -> bool:
    """
    Subscribe to tenant-scoped events.
    If tenant_id is None, subscribes to all tenants (admin/system use).
    """
    if tenant_id:
        subject = get_tenant_subject(tenant_id, domain, action)
    else:
        subject = get_all_tenants_subject(domain, action)

    return await self.subscribe(subject, handler, **kwargs)
```

### 3.4 Create JetStream Streams for Tenant Events

**File**: `config/nats/jetstream-tenant-streams.conf` (new)

```
# Tenant-scoped streams (one per domain)
STREAM sahool-tenant-field {
    subjects = ["sahool.tenant.*.field.>"]
    retention = limits
    max_age = 72h
    max_bytes = 1GB
    storage = file
    replicas = 1
    discard = old
}

STREAM sahool-tenant-task {
    subjects = ["sahool.tenant.*.task.>"]
    ...
}

# Repeat for each domain...
```

### 3.5 NATS Authorization (Optional - Phase 1b)

If NATS auth is enabled, configure per-tenant publish/subscribe permissions:

```json
{
  "tenant_user_org_123": {
    "publish": {
      "allow": ["sahool.tenant.org_123.>"]
    },
    "subscribe": {
      "allow": ["sahool.tenant.org_123.>"]
    }
  }
}
```

### 3.6 Create Migration Validation Script

**File**: `scripts/validate-nats-tenant-migration.py` (new)

Script that:
- Subscribes to both old and new subjects
- Counts events on each
- Compares payloads
- Reports gaps
- Verifies tenant_id consistency

---

## 4. Phase 2: Dual Publishing (Sprint 3-4)

### Migration Order (Publishers)

Migrate publishers in order of **risk** (lowest risk first):

#### Batch 1 - Low Traffic, Low Risk (Week 1)
| Service | Domain | Subjects | Notes |
|---------|--------|----------|-------|
| astronomical-calendar | calendar | 2 | No subscribers depend on it |
| globalgap-compliance | compliance | 3 | Isolated domain |
| crm-service | crm | 6 | Internal only |
| wechat-service | wechat | 5 | External integration |

#### Batch 2 - Moderate Traffic (Week 2)
| Service | Domain | Subjects | Notes |
|---------|--------|----------|-------|
| alert-service | alerts | 5 | Subscriber: notification-service |
| billing-core | billing | 6 | Subscriber: notification-service |
| inventory-service | inventory | 3 | Subscriber: alert-service |
| lowcode-engine | lowcode | 4 | Isolated |
| copilot-api | copilot | 7 | Isolated |

#### Batch 3 - Core Services (Week 3)
| Service | Domain | Subjects | Notes |
|---------|--------|----------|-------|
| task-service | task | 6 | Subscriber: ws-gateway, notification |
| weather-service | weather | 10 | Subscriber: alert, agro-rules |
| advisory-service | advisory | 3 | Subscriber: notification |

#### Batch 4 - High Traffic, Critical (Week 4)
| Service | Domain | Subjects | Notes |
|---------|--------|----------|-------|
| field-management-service | field, farm | 6 | Subscriber: ws-gateway, notification |
| iot-gateway | iot | 6 | Subscriber: edge-orchestrator |
| yolo26-vision-service | vision | 8 | Subscriber: alert, notification |
| vegetation-analysis-service | satellite | 12 | Subscriber: ndvi-processor, alert |

#### Batch 5 - Shared Libraries (Week 4)
| Library | Domain | Location |
|---------|--------|----------|
| shared/irrigation/ | irrigation | `shared/irrigation/` |
| shared/pest_scouting/ | pest | `shared/pest_scouting/` |
| shared/weather_alerts/ | weather | `shared/weather_alerts/` |
| shared/fertilizer_management/ | fertilizer | `shared/fertilizer_management/` |
| (+ 8 more shared modules) | various | `shared/*/` |

### Per-Service Migration Steps

For each service:

1. **Update publisher calls** to use `publish_tenant_event()`:

   ```python
   # Before
   await publisher.publish_event(SAHOOL_FIELD_CREATED, event)

   # After (dual-publish mode)
   await publisher.publish_tenant_event("field", "created", event)
   ```

2. **Ensure `tenant_id` is always available** in the event payload

3. **Add metrics** to track dual-publish success rates:
   ```python
   nats_tenant_publish_total.labels(domain="field", mode="dual").inc()
   ```

4. **Test** with integration tests that verify both subjects receive the event

5. **Deploy** and monitor for 48 hours before proceeding to next batch

---

## 5. Phase 3: Subscriber Migration (Sprint 5-6)

### Migration Order (Subscribers)

Migrate subscribers **after** their publishers are all in dual-publish mode:

#### Step 1 - Internal/Admin Subscribers
| Subscriber | Current Subject | New Subject | Notes |
|-----------|----------------|-------------|-------|
| agro-rules | `sahool.weather.*` | `sahool.tenant.*.weather.*` | Admin: all tenants |

#### Step 2 - Pipeline Subscribers
| Subscriber | Current Subject | New Subject | Notes |
|-----------|----------------|-------------|-------|
| ndvi-processor | `sahool.satellite.*` | `sahool.tenant.*.satellite.*` | Processing pipeline |
| ground-vision | `sahool.*.satellite.*` | `sahool.tenant.*.satellite.*` | Already uses wildcard |
| edge-orchestrator | `sahool.*.edge.*` | `sahool.tenant.*.edge.*` | Already uses wildcard |

#### Step 3 - Core Subscribers
| Subscriber | Current Subject | New Subject | Notes |
|-----------|----------------|-------------|-------|
| alert-service | `sahool.weather.*`, `sahool.health.*` | `sahool.tenant.*.weather.*`, etc. | Critical service |
| notification-service | `sahool.field.*`, etc. | `sahool.tenant.*.field.*`, etc. | User-facing |
| ws-gateway | `sahool.field.*`, `sahool.task.*` | `sahool.tenant.{id}.field.*` | Per-connection tenant |

### Per-Subscriber Migration Steps

1. **Add new subscription** alongside old one (dual-subscribe):
   ```python
   # Old (keep temporarily)
   await subscriber.subscribe("sahool.field.*", handler)
   # New
   await subscriber.subscribe_tenant(None, "field", "*", handler)
   ```

2. **Add deduplication** in handler (events arrive on both subjects):
   ```python
   _seen_events: set[str] = set()

   async def handler(event):
       if event.event_id in _seen_events:
           return  # Skip duplicate
       _seen_events.add(event.event_id)
       # Process event...
   ```

3. **Monitor** for 48h that new subscriptions receive all events

4. **Remove old subscription** once confirmed

5. **Remove deduplication** once all publishers stop dual-publishing

### Special Case: ws-gateway

The WebSocket gateway needs **per-connection tenant scoping**:

```python
# When a user connects with JWT containing tenant_id
async def on_ws_connect(ws, user):
    tenant_id = user.tenant_id
    # Subscribe only to this tenant's events
    await subscriber.subscribe_tenant(
        tenant_id, "field", "*", ws.send_event
    )
    await subscriber.subscribe_tenant(
        tenant_id, "task", "*", ws.send_event
    )
```

This is the **highest value** migration — eliminates cross-tenant WebSocket leakage.

---

## 6. Phase 4: Cleanup (Sprint 7-8)

### 6.1 Remove Dual Publishing

Update all publishers to `dual_publish=False`:

```python
# Configuration flag (environment variable)
NATS_DUAL_PUBLISH = os.getenv("NATS_DUAL_PUBLISH", "false").lower() == "true"

await publisher.publish_tenant_event("field", "created", event,
    dual_publish=NATS_DUAL_PUBLISH)
```

### 6.2 Remove Legacy Subject Constants

Mark flat subjects as deprecated in `shared/events/subjects.py`:

```python
import warnings

# DEPRECATED: Use get_tenant_subject() instead
SAHOOL_FIELD_CREATED = "sahool.field.created"  # ⚠️ Deprecated v17.0.0
```

### 6.3 Delete Legacy JetStream Streams

Remove flat-subject streams after confirming zero traffic:

```bash
nats stream delete sahool-field
nats stream delete sahool-task
# ... etc
```

### 6.4 Enforce Tenant-Only Publishing

Add validation in `EventPublisher.publish_event()`:

```python
async def publish_event(self, subject: str, event: BaseEvent, **kwargs):
    if not subject.startswith("sahool.tenant."):
        if os.getenv("NATS_ENFORCE_TENANT_SUBJECTS", "false") == "true":
            raise ValueError(
                f"Flat subject '{subject}' is not allowed. "
                f"Use publish_tenant_event() instead."
            )
        else:
            logger.warning(f"DEPRECATED: Flat subject used: {subject}")
    ...
```

---

## 7. Testing Strategy | استراتيجية الاختبار

### 7.1 Unit Tests

For each migrated service:

```python
@pytest.mark.unit
async def test_publish_tenant_event():
    publisher = EventPublisher()
    event = FieldCreatedEvent(
        field_id=uuid4(), farm_id=uuid4(),
        tenant_id=uuid4(), name="Test Field",
        geometry_wkt="POLYGON(...)"
    )

    # Verify dual-publish
    await publisher.publish_tenant_event("field", "created", event)

    assert publisher._publish_count == 2  # Both subjects
    # Verify subjects
    assert "sahool.tenant." in published_subjects[0]
    assert "sahool.field.created" == published_subjects[1]
```

### 7.2 Integration Tests

```python
@pytest.mark.integration
async def test_tenant_isolation():
    """Verify tenant A cannot see tenant B's events."""
    tenant_a = str(uuid4())
    tenant_b = str(uuid4())

    received_a = []
    received_b = []

    # Subscribe to tenant A's events only
    await subscriber.subscribe_tenant(tenant_a, "field", "*",
        lambda e: received_a.append(e))

    # Publish events for both tenants
    await publisher.publish_tenant_event("field", "created",
        event_a, tenant_id=tenant_a)
    await publisher.publish_tenant_event("field", "created",
        event_b, tenant_id=tenant_b)

    await asyncio.sleep(0.5)

    assert len(received_a) == 1
    assert received_a[0].tenant_id == tenant_a
    # tenant B's event should NOT arrive
```

### 7.3 Load Test

Verify no performance regression:

```python
# k6 test: compare latency of flat vs tenant-scoped subjects
# Target: <5% latency increase at 1000 msg/sec
```

### 7.4 Smoke Test for Each Batch

```bash
# After deploying batch N, verify:
# 1. Events arrive on new subjects
nats sub "sahool.tenant.>" --count=10

# 2. Events still arrive on old subjects (dual-publish)
nats sub "sahool.field.>" --count=10

# 3. No event loss
python scripts/validate-nats-tenant-migration.py --domain=field --duration=60s
```

---

## 8. Monitoring & Observability | المراقبة

### 8.1 Prometheus Metrics

```python
# New metrics for migration tracking
nats_tenant_publish_total = Counter(
    "nats_tenant_publish_total",
    "Total tenant-scoped publishes",
    ["domain", "action", "mode"]  # mode: tenant_only, dual, legacy
)

nats_tenant_subscribe_total = Counter(
    "nats_tenant_subscribe_total",
    "Total tenant-scoped subscriptions",
    ["domain", "subscriber_service"]
)

nats_legacy_publish_total = Counter(
    "nats_legacy_publish_total",
    "Legacy flat-subject publishes (should decrease to 0)",
    ["domain", "action"]
)
```

### 8.2 Grafana Dashboard

Create a migration dashboard showing:
- Legacy vs tenant-scoped publish rates (should converge)
- Per-domain migration progress
- Event loss detection (compare pub/sub counts)
- Subscriber migration status per service

### 8.3 Alerts

```yaml
# Alert if legacy subjects are still in use after deadline
- alert: NATSLegacySubjectStillActive
  expr: rate(nats_legacy_publish_total[5m]) > 0
  for: 24h
  labels:
    severity: warning
  annotations:
    summary: "Legacy NATS subject still in use after migration deadline"
```

---

## 9. Rollback Plan | خطة التراجع

### Per-Phase Rollback

| Phase | Rollback Action | Time to Rollback |
|-------|----------------|-----------------|
| Phase 1 (Infrastructure) | No rollback needed — additive changes only | N/A |
| Phase 2 (Dual Publishing) | Set `NATS_DUAL_PUBLISH=false` — reverts to legacy only | < 5 min |
| Phase 3 (Subscriber Migration) | Re-add old subscription alongside new | < 10 min |
| Phase 4 (Cleanup) | Re-enable `NATS_DUAL_PUBLISH=true` temporarily | < 5 min |

### Emergency Rollback

If critical issues are detected:

```bash
# 1. Revert all publishers to legacy mode
kubectl set env deployment --all NATS_DUAL_PUBLISH=false -n sahool

# 2. Restart subscribers to re-register old subscriptions
kubectl rollout restart deployment -l component=subscriber -n sahool

# 3. Verify event flow
python scripts/validate-nats-tenant-migration.py --mode=legacy
```

---

## 10. Success Criteria | معايير النجاح

| Criteria | Target | Measurement |
|----------|--------|-------------|
| All publishers use tenant subjects | 100% | `nats_legacy_publish_total == 0` |
| All subscribers use tenant subjects | 100% | No flat-subject subscriptions |
| Zero cross-tenant event leakage | 0 incidents | Integration tests + audit |
| Performance impact | < 5% latency increase | p99 latency comparison |
| Event delivery reliability | 99.99% | Compare pub/sub counts |
| Zero event loss during migration | 0 lost events | Validation script |

---

## 11. Timeline | الجدول الزمني

```
Sprint 1-2 (Weeks 1-4):   Phase 1 - Infrastructure Preparation
Sprint 3-4 (Weeks 5-8):   Phase 2 - Dual Publishing (5 batches)
Sprint 5-6 (Weeks 9-12):  Phase 3 - Subscriber Migration
Sprint 7-8 (Weeks 13-16): Phase 4 - Cleanup & Enforcement
```

### Milestones

| Milestone | Target Date | Gate |
|-----------|-------------|------|
| Infrastructure ready | End of Sprint 2 | Code review + tests pass |
| All publishers dual-publishing | End of Sprint 4 | 100% dual-publish rate |
| All subscribers migrated | End of Sprint 6 | 0 legacy subscriptions |
| Legacy subjects removed | End of Sprint 8 | `NATS_ENFORCE_TENANT_SUBJECTS=true` |

---

## 12. Dependencies & Risks | المخاطر والتبعيات

### Dependencies

| Dependency | Owner | Status |
|-----------|-------|--------|
| `shared/events/subjects.py` tenant functions | Platform | Ready (exists but unused) |
| `shared/events/publisher.py` enhancement | Platform | Planned |
| `shared/events/subscriber.py` enhancement | Platform | Planned |
| JetStream stream configuration | DevOps | Planned |
| NATS authorization (optional) | Security | Planned |

### Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Event loss during migration | Low | High | Dual-publish ensures both paths active |
| Performance degradation | Low | Medium | Load test before/after |
| Subscriber dedup complexity | Medium | Low | Use event_id-based dedup with TTL cache |
| Service team coordination | Medium | Medium | Batch approach, clear runbooks |
| JetStream stream limits | Low | Medium | Pre-calculate storage needs |

---

## Appendix A: Subject Mapping Table

| Legacy Subject | Tenant-Scoped Subject |
|---------------|----------------------|
| `sahool.field.created` | `sahool.tenant.{tid}.field.created` |
| `sahool.field.updated` | `sahool.tenant.{tid}.field.updated` |
| `sahool.field.deleted` | `sahool.tenant.{tid}.field.deleted` |
| `sahool.task.created` | `sahool.tenant.{tid}.task.created` |
| `sahool.task.updated` | `sahool.tenant.{tid}.task.updated` |
| `sahool.task.assigned` | `sahool.tenant.{tid}.task.assigned` |
| `sahool.task.completed` | `sahool.tenant.{tid}.task.completed` |
| `sahool.weather.forecast` | `sahool.tenant.{tid}.weather.forecast` |
| `sahool.weather.alert` | `sahool.tenant.{tid}.weather.alert` |
| `sahool.weather.alert.*` | `sahool.tenant.{tid}.weather.alert.*` |
| `sahool.satellite.data.ready` | `sahool.tenant.{tid}.satellite.data.ready` |
| `sahool.satellite.anomaly.*` | `sahool.tenant.{tid}.satellite.anomaly.*` |
| `sahool.health.disease.detected` | `sahool.tenant.{tid}.health.disease.detected` |
| `sahool.health.pest.detected` | `sahool.tenant.{tid}.health.pest.detected` |
| `sahool.health.stress.*` | `sahool.tenant.{tid}.health.stress.*` |
| `sahool.billing.payment.*` | `sahool.tenant.{tid}.billing.payment.*` |
| `sahool.billing.subscription.*` | `sahool.tenant.{tid}.billing.subscription.*` |
| `sahool.iot.sensor.*` | `sahool.tenant.{tid}.iot.sensor.*` |
| `sahool.iot.device.*` | `sahool.tenant.{tid}.iot.device.*` |
| `sahool.vision.pest_detected` | `sahool.tenant.{tid}.vision.pest_detected` |
| `sahool.vision.disease_detected` | `sahool.tenant.{tid}.vision.disease_detected` |
| `sahool.vision.*` | `sahool.tenant.{tid}.vision.*` |
| `sahool.terrain.*` | `sahool.tenant.{tid}.terrain.*` |
| `sahool.edge.*` | `sahool.tenant.{tid}.edge.*` |
| `sahool.alerts.*` | `sahool.tenant.{tid}.alerts.*` |
| `sahool.copilot.*` | `sahool.tenant.{tid}.copilot.*` |
| `sahool.chat.*` | `sahool.tenant.{tid}.chat.*` |
| `sahool.crm.*` | `sahool.tenant.{tid}.crm.*` |
| `sahool.compliance.*` | `sahool.tenant.{tid}.compliance.*` |
| `sahool.wechat.*` | `sahool.tenant.{tid}.wechat.*` |
| `sahool.lowcode.*` | `sahool.tenant.{tid}.lowcode.*` |
| `sahool.inventory.*` | `sahool.tenant.{tid}.inventory.*` |
| `sahool.agent.*` | `sahool.tenant.{tid}.agent.*` |

### Wildcard Subscription Mapping

| Old Pattern | New Pattern | Use Case |
|-------------|-------------|----------|
| `sahool.field.*` | `sahool.tenant.{tid}.field.*` | Single tenant |
| `sahool.field.*` | `sahool.tenant.*.field.*` | Admin/system (all tenants) |
| `sahool.>` | `sahool.tenant.{tid}.>` | All events for one tenant |
| `sahool.>` | `sahool.tenant.*.>` | All events (admin only) |

---

## Appendix B: Related Documents

| Document | Path |
|----------|------|
| Event Subjects | `shared/events/subjects.py` |
| Event Publisher | `shared/events/publisher.py` |
| Event Subscriber | `shared/events/subscriber.py` |
| Event Contracts | `shared/events/contracts.py` |
| DLQ Configuration | `shared/events/dlq_config.py` |
| NATS Configuration | `config/nats/` |
| Event Catalog | `governance/events/catalog.yaml` |
| Event Schemas | `governance/events/schemas/` |
| Service Registry | `governance/services.yaml` |

---

_Last Updated: 2026-02-16_
