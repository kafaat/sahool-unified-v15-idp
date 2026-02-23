# SAHOOL API Interface Audit Report

> **Audit Date**: 2026-02-23
> **Scope**: All Python service endpoints, Kong gateway configuration, auth coverage, input validation
> **Platform Version**: 16.0.0

---

## Executive Summary

Direct audit of all API interfaces across 56 Python services and the Kong gateway configuration.
Identified **22 findings** including critical authentication gaps and route inconsistencies.

| Severity | Count | Description |
|----------|-------|-------------|
| **Critical (P0)** | 3 | Unauthenticated mutation endpoints on public-facing services |
| **High (P1)** | 6 | Kong gateway auth gaps, CORS wildcard, missing rate limits |
| **Medium (P2)** | 8 | Route inconsistencies, missing response models, readiness probes |
| **Low (P3)** | 5 | Naming inconsistencies, deprecated route artifacts |

---

## Critical Findings (P0)

### API-001: 35+ services have mutation endpoints with NO authentication

**Severity**: P0 Critical
**Category**: Security / Authentication

Of 56 Python services with API endpoints, only **21 services** use `get_current_user` for
authentication. The remaining **35 services** expose POST/PUT/PATCH/DELETE endpoints with
no authentication at the service level.

**Services with unprotected mutation endpoints** (sample):

| Service | Unprotected Endpoints | Risk |
|---------|----------------------|------|
| `alert-service` | POST /alerts, PATCH /alerts/{id}, DELETE /alerts/{id}, POST /alerts/rules | Creates/modifies/deletes alert rules |
| `code-review-service` | POST /review, POST /review/file, POST /review/pr, POST /cache/clear | Triggers code reviews, clears cache |
| `code-fix-agent` | POST /api/v1/analyze, POST /api/v1/fix, POST /api/v1/review | Executes code analysis/fixing |
| `agent-registry` | POST /api/v1/agents, PUT /api/v1/agents/{id}, DELETE /api/v1/agents/{id} | Manages AI agent registry |
| `ai-agents-core` | POST /api/v1/tasks, POST /api/v1/agents/{id}/execute | Executes AI agent tasks |
| `ground-vision-service` | POST /api/v1/cameras, POST /api/v1/frames/process | Creates cameras, processes frames |
| `fertigation-engine` | POST /api/v1/fertigation/plan | Creates fertigation plans |
| `globalgap-compliance` | POST /api/v1/audits, PUT /api/v1/audits/{id} | Manages GlobalGAP audits |
| `provider-config` | POST /api/v1/providers, PUT /api/v1/providers/{id} | Modifies provider configurations |
| `ussd-gateway` | POST /api/v1/ussd/session, POST /api/v1/ussd/respond | Creates USSD sessions |
| `iot-sensor-hub` | POST /api/v1/sensors, POST /api/v1/readings | Creates sensors and readings |
| `mcp-server` | POST /api/v1/tools/execute | Executes MCP tools |

**Why this matters**: Even though Kong sits in front, the Kong JWT plugin is only enabled on
5 services (vision, terrain, hydrology, leveling, edge). The other 50+ routes pass through
Kong **without JWT validation**. If any service is accidentally exposed (port forwarding,
misconfigured network policy), the endpoints are completely open.

**Recommendation**:
1. Enable Kong JWT plugin globally or on all service routes (not just 5)
2. Add `Depends(get_current_user)` to all service-level endpoints as defense-in-depth
3. Use the shared `require_roles()` dependency for authorization

---

### API-002: Kong JWT plugin enabled on only 5 of 50+ service routes

**File**: `infrastructure/gateway/kong/kong.yml`
**Severity**: P0 Critical
**Category**: Security / Gateway

Only these 5 services have the `jwt` plugin configured at the Kong route level:
- `yolo26-vision-service` (line 1225)
- `terrain-core-service` (line 1297)
- `hydrology-service` (line 1354)
- `leveling-optimizer-service` (line 1411)
- `edge-orchestrator-service` (line 1468)

**All other services** (including billing, advisory, weather, notification, inventory,
equipment, CRM, logistics, etc.) have **no Kong-level JWT validation**.

This means:
- Anyone who can reach Kong can call billing-core, advisory-service, alert-service, etc.
- The `ip-restriction` plugin is only set on billing-core and iot-gateway
- Defense depends entirely on service-level auth (which is also missing on many services)

**Recommendation**: Add global JWT plugin to Kong with exceptions only for:
- `/api/v1/auth/login`, `/api/v1/auth/register` (public auth routes)
- `/healthz`, `/readyz`, `/health` (health checks)
- Webhook endpoints (WhatsApp, GitHub)

---

### API-003: CORS origin set to wildcard "*" in production config

**File**: `infrastructure/gateway/kong/kong.yml:28`
**Severity**: P0 Critical
**Category**: Security / CORS

```yaml
origins:
  - "*"  # Replace with ${KONG_CORS_ORIGINS:-*} in production
```

The CORS origin is set to `"*"` (wildcard) and relies on a comment instructing operators
to change it in production. If this file is deployed as-is, any website can make
authenticated API requests to the platform (especially when combined with `credentials: true`
if switched later).

**Recommendation**: Use environment variable substitution:
```yaml
origins:
  - ${KONG_CORS_ORIGINS:-https://app.sahool.com,https://admin.sahool.com}
```

---

## High Severity Findings (P1)

### API-004: Inconsistent strip_path behavior across Kong routes

**File**: `infrastructure/gateway/kong/kong.yml`
**Severity**: P1 High
**Category**: Routing Consistency

76 routes use `strip_path: true`, 28 routes use `strip_path: false`. This inconsistency
means services receive different URL prefixes depending on the route.

**Examples of confusion**:
- `weather-service`: strip_path=true → service receives `/current` (path: `/api/v1/weather`)
- `soil-analysis-service`: strip_path=false → service receives `/api/v1/soil/...` (path: `/api/v1/soil`)
- `yolo26-vision-service`: Mixed! Base route strips, specific detection routes don't

This creates confusion for developers implementing new endpoints.

**Recommendation**: Standardize to `strip_path: false` for all routes, ensuring all
services handle their full `/api/v1/*` prefix consistently.

---

### API-005: Rate limiting uses "local" policy on most services (not Redis)

**File**: `infrastructure/gateway/kong/kong.yml`
**Severity**: P1 High
**Category**: Security / Rate Limiting

Only marketplace-service, billing-core, and iot-gateway use `policy: redis` for rate limiting.
All other services use `policy: local`, which means each Kong instance maintains its own
counter. With multiple Kong instances behind a load balancer, effective rate limits are
multiplied by the number of Kong replicas.

**Recommendation**: Configure all rate limiting to use `policy: redis` with the kong-redis
instance already defined in the config.

---

### API-006: 17 services have no Kong rate limiting at all

**Severity**: P1 High
**Category**: Security / DoS

These services have Kong routes but **no rate-limiting plugin**:

- field-management-service, chat-service, iot-service, community-chat, field-ops, ws-gateway,
  vegetation-analysis-service, indicators-service, advisory-service, irrigation-smart,
  crop-intelligence-service, virtual-sensors, yield-prediction-service, equipment-service,
  task-service, field-intelligence, mcp-server, skills-service, audit-service, astronomical-calendar,
  ai-advisor, alert-service, crm-service, lowcode-engine, wechat-service, globalgap-compliance,
  logistics-service, agent-registry, ai-agents-core, knowledge-graph, yield-engine,
  ai-agents-service, field-core, ndvi-processor

**Recommendation**: Add rate limiting to all Kong routes. Use tiered limits matching the
platform's rate limiting tiers (Starter: 30/min, Professional: 60/min, Enterprise: 120/min).

---

### API-007: Deprecated services still have active Kong routes

**File**: `infrastructure/gateway/kong/kong.yml`
**Severity**: P1 High
**Category**: Maintenance

These deprecated services still have active routes in Kong:
- `field-ops` → `/field-ops-legacy` (deprecated, should be field-management-service)
- `yield-prediction` → `/yield-legacy` (deprecated)
- `lai-estimation` → `/lai-legacy` (deprecated)
- `crop-growth-model` → `/crop-growth-legacy` (deprecated)
- `satellite-service` → `/api/v1/satellite-legacy` (deprecated)
- `weather-advanced` → `/api/v1/weather-advanced` (deprecated)
- `crop-health-ai` → `/api/v1/crop-health-ai` (deprecated)
- `fertilizer-advisor` → `/api/v1/fertilizer-advisor` (deprecated)
- `field-core` → `/api/v1/field-core` (deprecated)
- `field-service` → `/field-service-legacy` (deprecated)

**Recommendation**: Remove deprecated routes or add deprecation headers and sunset dates
via Kong response-transformer plugin.

---

### API-008: No request validation plugin on most Kong routes

**Severity**: P1 High
**Category**: Security / Input Validation

Only `pest-detection-service` and `ground-vision-service` have `request-size-limiting`
configured at the route level (25MB and 50MB respectively). The global limit is 10MB.

Services like `code-fix-agent` and `code-review-service` accept code payloads that could be
very large but have no size limits beyond the global 10MB.

---

### API-009: notification-service routes expose /api/v1/farmers without scoping

**File**: `infrastructure/gateway/kong/kong.yml:604-607`
**Severity**: P1 High
**Category**: Security / Data Exposure

```yaml
- name: notification-farmers-route
  paths: ["/api/v1/farmers"]
```

This route maps `/api/v1/farmers` to the notification-service, which could conflict with
the user-service's farmer management. More critically, it exposes farmer data through the
notification service without JWT validation at the Kong level.

---

## Medium Severity Findings (P2)

### API-010: 7 services don't use response_model on endpoints

**Severity**: P2 Medium

Services like `irrigation-smart`, `iot-sensor-hub`, and `inventory-service` have endpoints
that return raw dicts without `response_model=`, which means:
1. No automatic response validation
2. No OpenAPI schema generation for those endpoints
3. Risk of leaking internal data structures

---

### API-011: Inconsistent API versioning across services

**Severity**: P2 Medium

| Pattern | Count | Services |
|---------|-------|----------|
| `/api/v1/*` | 38 | Most services (standard) |
| `/*` (no version) | 18 | notification-service, weather-service, code-review-service, ndvi-processor, etc. |

Notification-service uses `/`, `/weather`, `/pest`, `/irrigation` without version prefix.
Code-review-service uses `/review`, `/cache/stats` without prefix.
NDVI-processor uses `/process`, `/fields/*` without prefix.

**Recommendation**: Standardize all endpoints to `/api/v1/*` prefix.

---

### API-012: Weather service readiness always returns "ready"

**File**: `apps/services/weather-service/src/main.py:167-180`
**Severity**: P2 Medium (duplicate of GAP-014 in platform gap report)

The `/readyz` endpoint always returns `{"status": "ready"}` regardless of provider health.

---

### API-013: Health endpoint inconsistency across services

**Severity**: P2 Medium

| Pattern | Service Count |
|---------|--------------|
| `/healthz` + `/readyz` | 38 (standard) |
| `/health` + `/healthz` + `/readyz` | 15 (triple) |
| `/health/live` + `/health/ready` | 5 (alternative) |
| Only `/healthz` | 3 (missing readyz) |

Standard K8s convention is `/healthz` (liveness) + `/readyz` (readiness). Some services
also expose `/health` (which overlaps). 5 services use `/health/live` and `/health/ready`.

---

### API-014: Missing tenant isolation on several services

**Severity**: P2 Medium

Services that handle tenant data but don't enforce `_enforce_tenant()`:
- `notification-service`: Uses tenant_id in requests but no enforcement helper
- `fertigation-engine`: No tenant_id enforcement
- `astronomical-calendar`: No tenant_id at all

---

### API-015: Kong routes for non-existent services

**Severity**: P2 Medium

These Kong routes point to services that don't exist in `docker-compose.yml`:
- `community-chat` (port 8097) — archived, moved to chat-service
- `field-chat` (port 8099) — archived, moved to chat-service
- `crop-health` (port 8100) — archived, moved to crop-intelligence-service

---

### API-016: Inconsistent error response format

**Severity**: P2 Medium

Services using `shared.errors_py` return the unified format:
```json
{"success": false, "error": {"code": "E1001", "message": "...", "message_ar": "..."}}
```

But 18+ services also raise raw `HTTPException` directly, returning:
```json
{"detail": "..."}
```

This creates inconsistent error formats for API consumers.

---

### API-017: GET endpoints used for mutation operations

**Severity**: P2 Medium

- `weather-service`: GET `/weather/heat-stress/{temp_c}` — should be POST
- Some services use GET for operations that should be POST (side effects like event publishing)

---

## Low Severity Findings (P3)

### API-018: Kong http-log plugin points to non-existent logging-service

**File**: `infrastructure/gateway/kong/kong.yml` (lines 1251, 1318, 1375, 1432, 1489)
**Severity**: P3 Low

`http_endpoint: http://logging-service:8080/logs` — there is no `logging-service` in
docker-compose.yml. These log shipping configurations will silently fail.

---

### API-019: Duplicate route paths could cause Kong conflicts

**Severity**: P3 Low

- `/api/v1/field-core` maps to both `field-intelligence` and `field-core` (deprecated)
- `/api/v1/alerts` maps to `notification-service` AND `alert-service` has `/alerts/*` routes

---

### API-020: OpenAPI documentation not standardized

**Severity**: P3 Low

- 15 services use `tags=["..."]` on endpoints, 40+ don't
- 8 services have `description` on the FastAPI app, others don't
- OpenAPI schemas are incomplete for response models

---

### API-021: Kong proxy-cache on weather and vegetation could serve stale data

**Severity**: P3 Low

Weather data cached for 15 minutes and vegetation data for 30 minutes. If an alert is
published (frost, pest), the cached response won't reflect the new alert until TTL expires.

---

### API-022: Missing PATCH support on most CRUD services

**Severity**: P3 Low

Most services that support UPDATE use PUT (full replace). PATCH (partial update) is only
used by notification-service and alert-service. Standard REST practice recommends
supporting both.

---

## Recommended Priority Actions

### Immediate (P0 — this sprint)
1. **API-002**: Enable Kong JWT plugin globally with path exceptions
2. **API-003**: Replace CORS wildcard with environment-variable-driven origins
3. **API-001**: Add `get_current_user` to all service mutation endpoints

### Short-term (P1 — next 2 sprints)
4. **API-006**: Add rate limiting to all Kong routes
5. **API-005**: Migrate rate limiting from `local` to `redis` policy
6. **API-007**: Remove or sunset deprecated Kong routes
7. **API-008**: Review request size limits per service

### Medium-term (P2 — quarter)
8. **API-011**: Standardize API versioning to `/api/v1/*`
9. **API-016**: Migrate all error handling to unified `shared.errors_py`
10. **API-013**: Standardize health check endpoint patterns

---

_Generated by API interface audit on 2026-02-23_
