# Platform Hardening Summary — PR #1316

**Date**: 2026-03-24
**Branch**: `claude/fix-review-issues-P7Xks`
**Total Commits**: 10
**Files Changed**: ~70
**PR**: #1316 — Comprehensive platform hardening

---

## Overview

This PR delivers comprehensive platform hardening across 4 categories:
security (tenant isolation & RLS), database improvements (indexes & migrations),
infrastructure (Helm, CI/CD, monitoring), and API/service fixes (validation & error handling).

---

## 1. Security — Tenant Isolation & RLS (6 commits)

### Cross-Tenant SQL Vulnerability Fixes

15+ SQL queries were missing `tenant_id` in WHERE clauses, allowing potential
cross-tenant data access at the database level.

| Service | Fix Applied |
|---------|-------------|
| `lowcode-engine` | Added tenant_id to UPDATE/DELETE/SELECT queries |
| `ground-vision-service` | Added tenant_id to UPDATE/DELETE/SELECT queries |
| `copilot-api` | Added tenant_id to session UUID seed (prevents collision) |
| `traceability-service` | Added tenant_id to UPDATE/DELETE/SELECT queries |
| `cooperative-service` | Added tenant_id to UPDATE/DELETE/SELECT queries |
| `billing-core` | Added tenant_id to 5 repository methods |
| `provider-config` | Added tenant_id to `get_config_version()` and rollback endpoint |
| `inventory-service` | Added tenant_id scoping |
| `globalgap-compliance` | Added tenant_id to `get_by_id()` methods |

### Row-Level Security (RLS) Policies

New RLS migrations enforce tenant isolation at the PostgreSQL level:

| Module | Tables Protected | Migration |
|--------|-----------------|-----------|
| `shared/digital_twin` | field_daily_state, field_observation, irrigation_recommendation | `002_rls_policies.sql` |
| `shared/calibration` | calibration_run, parameter_set, parameter_change_log | `s16_011_rls_policies.sql` |

**RLS Policy Details:**
- Tenant isolation via `current_setting('app.current_tenant', true)`
- Super-admin bypass via `current_setting('app.is_super_admin', true)`
- `nullif()` protection on UUID casts (digital_twin) to handle empty string resets
- Variable names aligned with `shared/db/tenant_connection.py` helper

### Session UUID Collision Fix (copilot-api)

**Before**: `uuid5(NAMESPACE_URL, f"sahool:copilot:session:{session_id}")`
**After**: `uuid5(NAMESPACE_URL, f"sahool:copilot:session:{tenant_id}:{session_id}")`

Two tenants using the same `session_id` would no longer collide on the same UUID.

---

## 2. Database Improvements (4 commits)

### New Compound Indexes (16+)

| Service | Indexes Added |
|---------|--------------|
| `chat-service` | [tenantId, createdAt], [tenantId, isRead, createdAt] |
| `field-management-service` | [tenantId, cropType, createdAt], [tenantId, plantingDate, status] |
| `disaster-assessment` | [tenantId, type, severity], [tenantId, startDate, status] |
| `weather-service` | [tenantId, locationId, timestamp] |
| `iot-service` | Tenant-scoped compounds on SensorReading, Sensor, Actuator, ActuatorCommand |
| `alert-service` | tenant+status+created_at, tenant+severity+created_at |
| `shared/libs/audit` | (resource_type, resource_id, tenant_id), (action, tenant_id) |
| `shared/libs/outbox` | (published, tenant_id), (retry_count, published) |

### Query Safety Caps (LIMIT)

| Module | Max Results | Purpose |
|--------|-------------|---------|
| `shared/ai/vector_store` | 50,000 | Prevent memory exhaustion on vector queries |
| `shared/digital_twin` | 3,660 | Cap daily state queries (10 years × 366 days) |
| `ussd-gateway` | 5,000 | Cap alert list queries |
| `drone-service` | 1,000 per page | Pagination limit on list endpoints |

### Financial Constraints (marketplace-service)

New CHECK constraints on financial tables:
- Wallet balance ≥ 0
- Transaction amount > 0
- Prevents negative balance and zero-amount transactions

### Schema Changes

| Service | Change | Reason |
|---------|--------|--------|
| `research-core` | `onDelete: Cascade` → `SetNull` on optional relations | Prevent unintended data loss |
| `inventory-service` | FK StockTransfer→InventoryItem with `onDelete: Restrict` | Prevent orphaned transfers |
| `hydrology-service` | `tenant_id` made NOT NULL (backfill existing NULLs) | Enforce tenant data integrity |

---

## 3. Infrastructure (2 commits)

### CI/CD Job Timeouts

Added `timeout-minutes` to 17 GitHub Actions workflows to prevent hung jobs:

| Workflow | Timeout |
|----------|---------|
| `load-testing.yml` | 30 min |
| `mobile-ci.yml` | 20 min |
| `release.yml` | 30 min |
| `test.yml` | 20 min |
| `security-audit.yml` | 30 min |
| `ci-yolo26-vision.yml` | 25 min |
| `ci-terrain-services.yml` | 20 min |
| `ci-edge-orchestrator.yml` | 20 min |
| ...and 9 more | 15-30 min |

### NetworkPolicy Templates (7 services)

New Kubernetes NetworkPolicies for network isolation:

- `crop-intelligence-service`
- `edge-orchestrator-service`
- `hydrology-service`
- `inventory-service`
- `leveling-optimizer-service`
- `terrain-core-service`
- `yolo26-vision-service`

### Vision Service Monitoring (11 alerts)

New Prometheus alert rules in `vision-alerts.yml`:

| Group | Alerts | Examples |
|-------|--------|---------|
| Availability (3) | Service down, high latency (>5s), high error rate (>5%) |
| Detection Quality (3) | Low confidence (<0.3), high false positive rate, model load failure |
| GPU Resources (3) | GPU memory >90%, >95% critical, batch queue backlog |
| Critical Pest (2) | RPW/Locust detection alert, disease outbreak pattern |

### Supply Chain Security

Pinned `trivy-action` to verified SHA (`6e7e780`) in `quality-orchestrator.yml`
to mitigate the March 19, 2026 tag hijack attack (76 of 77 tags compromised).

---

## 4. API & Service Fixes (2 commits)

### Input Validation

| Service | Fix |
|---------|-----|
| `drone-service` | `offset: Query(0, ge=0)`, `limit: Query(500, ge=1, le=1000)` |
| `ussd-gateway` | Pydantic models for USSD, SMS, WhatsApp endpoints |

### Error Handling

| Service | Fix |
|---------|-----|
| `ussd-gateway` | Return 413 for oversized payloads (was 200), return 400 for invalid JSON |
| `task-service` | Fix `/health` endpoint crash (readiness_check returns JSONResponse, not dict) |
| `ussd-gateway` | Fix `RateLimiter()` init with unsupported keyword args |

### Health Check Improvements

| Service | Fix |
|---------|-----|
| `task-service` | `/readyz` now actually verifies DB connectivity (returns 503 when unhealthy) |
| `task-service` | `/health` extracts payload from JSONResponse correctly |

---

## Review Findings Addressed

### High-Confidence (from CodeQL & Copilot)

| Finding | Severity | Resolution |
|---------|----------|-----------|
| RateLimiter wrong keyword args | Error | Use default constructor |
| Cross-tenant session UUID collision | Critical | Include tenant_id in UUID seed |
| RLS variable name mismatches (×4) | High | Align with tenant_connection.py |
| readiness_check return type mismatch | High | Extract payload via helper |

### Low-Confidence (verified and fixed)

| Finding | Real? | Resolution |
|---------|-------|-----------|
| Empty string → uuid cast in RLS | Yes | Added `nullif()` wrapper |
| drone-service negative offset | Yes | Added `Query(ge=0)` validation |
| ussd-gateway json.loads + 413 | Yes | Added error handling + proper status codes |
| provider-config cross-tenant reads | Yes | Added tenant_id to get_config_version |
| research-core cascade on optional | Yes | Changed to SetNull |
| hydrology 'unknown' on UUID column | No | Column is VARCHAR(255), not UUID |
| task-service sync SQLAlchemy | Valid but pre-existing | Not in scope |
| NetworkPolicy egress too broad | Low priority | Not in scope |

---

## Files Changed Summary

| Category | Files | Key Impact |
|----------|-------|-----------|
| Security | ~20 | Closed 15+ cross-tenant vulnerabilities, 2 RLS migrations |
| Database | ~18 | 16+ compound indexes, financial constraints, schema fixes |
| Infrastructure | ~25 | 17 CI timeouts, 7 NetworkPolicies, 11 monitoring alerts |
| API/Service | ~7 | Input validation, error handling, health checks |
| **Total** | **~70** | **Comprehensive platform hardening** |

---

_Last Updated: 2026-03-24_
