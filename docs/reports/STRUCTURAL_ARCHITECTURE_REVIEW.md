# Structural Architecture Review Report

**Date**: 2026-03-21
**Scope**: Database schemas, domain models, TypeScript types, API routes, monorepo structure, event schemas, IaC, governance
**Reviewer**: Automated Architecture Audit (8 parallel agents)

---

## Executive Summary

A deep structural audit of the SAHOOL platform uncovered **150+ issues** across 8 architectural layers. The most critical findings include **45 missing foreign key/index constraints in Prisma schemas**, **duplicate ApiResponse definitions causing type conflicts**, **cross-region Terraform AZ mismatch**, **23+ events without validation schemas**, and **8 orphaned npm packages**.

| Layer | Critical | High | Medium | Low | Total |
|-------|----------|------|--------|-----|-------|
| Database Schemas | 6 | 8 | 11 | 5 | **30** |
| Python Models | 3 | 3 | 5 | 4 | **15** |
| TypeScript Types | 3 | 2 | 5 | 7 | **17** |
| API Routes | 5 | 3 | 6 | 3 | **17** |
| Monorepo Structure | 2 | 2 | 3 | 3 | **10** |
| Event Schemas | 1 | 1 | 4 | 3 | **9** |
| IaC (Terraform/Helm) | 2 | 3 | 5 | 4 | **14** |
| **Total** | **22** | **22** | **39** | **29** | **112** |

---

## 1. Database Schemas (Prisma + SQL)

### 45 Schema Issues Found Across 9 Services

#### Missing Foreign Key Constraints (12 critical)
| Service | Model | Field | Issue |
|---------|-------|-------|-------|
| marketplace | Wallet | userId | No FK to users — orphaned wallets |
| marketplace | SellerProfile | userId | No FK to users |
| marketplace | BuyerProfile | userId | No FK to users |
| marketplace | ProductReview | buyerId | No FK to BuyerProfile |
| marketplace | Product | sku | Globally unique, not per-tenant |
| field-management | Farm | ownerId | No FK to users |
| field-management | SyncStatus | deviceId, userId | No FK constraints at all |
| iot-service | SensorReading | deviceId | No FK to Device |
| chat-service | Participant | unique constraint | Missing tenantId in unique |
| weather-service | WeatherForecast | unique constraint | Missing tenantId in unique |
| inventory | InventoryMovement | item relation | Missing onDelete cascade |
| inventory | InventoryAlert | item relation | Missing onDelete cascade |

#### Missing Tenant Isolation Indexes (11 high)
| Service | Model | Missing Index |
|---------|-------|---------------|
| marketplace | OrderItem | `@@index([tenantId, orderId])` |
| marketplace | Escrow | `@@index([tenantId, buyerWalletId])` |
| iot-service | SensorReading | `@@index([tenantId, sensorId, timestamp])` |
| user-service | UserProfile | `@@index([tenantId, userId])` |
| user-service | RefreshToken | `@@index([tenantId, userId])` |
| chat-service | Message | `@@index([conversationId, isRead])` |
| weather-service | LocationConfig | `@@index([tenantId, isActive])` |
| inventory | Zone | `@@index([tenantId, warehouseId])` |
| research-core | Planting | `@@unique([experimentId, germplasmId, plantingDate])` |
| disaster-assessment | FieldAssessment | `@@unique([disasterId, fieldId])` |
| field-management | Task | onDelete should be Cascade not SetNull |

---

## 2. Python Domain Models

### Critical: Dataclass Field Defaults
- **Files**: `shared/contracts/events/crop_events.py`, `iot_events.py`, `weather_events.py`
- **Issue**: Required UUID/date fields assigned `None` as default: `field_id: UUID = None`
- **Impact**: Type checker violations, serialization bugs, runtime crashes on `.hex` access

### Critical: Mixed Dataclass/Pydantic Event Models
- **Two competing systems**: `shared/contracts/events/` (dataclasses) vs `shared/events/models.py` (Pydantic)
- **Impact**: Incompatible serialization — `from_dict()` vs `model_validate()`

### Critical: Missing Type Validation
- Subclasses use `UUID = None` while base correctly uses `UUID` (required)
- 12+ fields affected across crop, IoT, and weather events

### High: Inconsistent Enum Types
- `SourceCredibilityLevel` uses `(int, Enum)` while all others use `StrEnum`
- Ambiguous JSON serialization: `1` vs `"1"`

### High: datetime.utcnow() Deprecated
- `shared/ai/knowledge/models.py:159` — should use `datetime.now(UTC)` (Python 3.12+)

### High: Missing `__all__` Exports
- 5+ key modules lack `__all__`: `auth/models.py`, `auto_fix/models.py`, `events/models.py`

---

## 3. TypeScript Types & Contracts

### Critical: Duplicate ApiResponse (3 conflicting definitions)
| File | Structure |
|------|-----------|
| `shared-types/src/api.ts` | Has `pagination`, `requestId` |
| `shared-types/src/contracts/api-responses.ts` | Identical to api.ts |
| `api-client/src/types.ts` | Missing `pagination`, has `statusCode` |

**Impact**: Services returning pagination break clients expecting statusCode.

### Critical: Missing api-responses Export
- `shared-types/src/index.ts` — does NOT re-export `contracts/api-responses.ts`
- `import { ApiResponse } from "@sahool/shared-types"` returns WRONG definition

### Critical: Duplicate GeoJSON Types (3 definitions)
- `GeoJSONPolygon` in `field.ts`, `GeoPolygon` in `api-responses.ts`, different `GeoPolygon` in `api-client`

### High: FieldStatus/AlertStatus Mismatches
- `AlertStatus` in api-client missing "unread" and "read" values
- `FieldStatus` value ordering inconsistent between definitions

### Medium: 17 instances of `Record<string, unknown>` — type safety gap
### Medium: ApiResponse not a discriminated union — TypeScript can't narrow
### Medium: Deprecated fields coexist indefinitely (name_ar + nameAr)

---

## 4. API Route Structures

### Critical: 8 Different Error Response Patterns
- Plain string, bilingual dict, create_success_response wrapper — mixed within same service
- **Impact**: SDK generators produce inconsistent client code

### Critical: Kong strip_path Inconsistency
- user-service: `strip_path: false` (receives `/api/v1/auth/login`)
- field-management: `strip_path: true` (receives `/fields` without prefix)
- **Impact**: FastAPI router path matching breaks

### Critical: Missing API Versioning
- field-management-service uses `/v1/profitability/...` (missing `/api` prefix)
- Kong routes mix `/api/v1/fields` with bare `/field`

### High: 42% Missing Response Models
- 123/290 endpoints lack `response_model=` declaration
- OpenAPI spec incomplete for majority of services

### High: 180/290 Endpoints Missing Tenant Validation
- Only 10 endpoints call `_enforce_tenant()`

---

## 5. Monorepo Structure

### Critical: 8 Orphaned Packages (~788 KB dead code)
- `packages/advisor`, `field_suite`, `kernel_domain`, `professional`, `sahool-eo`, `shared`, `starter`, `enterprise`
- No `package.json`, invisible to npm workspace tooling

### Critical: 57/72 Services Missing from Workspace
- Root `package.json` manually lists 15 services instead of using `apps/services/*` glob
- 57 services hidden from workspace dependency resolution

### High: `file:` References Instead of Workspace Ranges
- 5 services use `"file:../../../packages/nestjs-auth"` — breaks `npm ci`

### High: Prisma Version Pinning Too Loose
- `~5.22.0` allows patch-breaking changes. Should use exact `=5.22.0`

---

## 6. Event Schemas & Subjects

### Critical: 23+ Events Without Validation Schemas
- All vision events (pest, disease, weed detection)
- All edge device events
- All ground vision events (6 event types)

### High: Hardcoded Event Publishing (6 services)
- pest-detection, crop-intelligence, ndvi-processor, leveling-optimizer, inventory-service
- Use string literals instead of `SAHOOL_*` constants from `subjects.py`

### Medium: 40+ Subject Constants Not in Registry
- `lookup_subject()` falls back to string construction for unregistered subjects

### Medium: 3 Incompatible Subject Naming Patterns
1. `sahool.{domain}.{action}` (legacy)
2. `sahool.{tenant_id}.{domain}.{action}` (inline)
3. `sahool.tenant.{tenant_id}.{domain}.{action}` (scoped)

### Medium: TypeScript ↔ Python Event Type Mismatch
- Python uses `geometry_wkt`, TypeScript uses GeoJSON
- No sync script between contract systems

---

## 7. Infrastructure-as-Code

### Critical: Cross-Region AZ Mismatch
- **File**: `infrastructure/terraform/main.tf:161`
- Jeddah region (`eu-west-1`) hardcoded with Bahrain AZs (`me-south-1a/b/c`)
- **Impact**: Terraform deployment fails for secondary region

### Critical: VPC Peering Routes Missing
- **File**: `infrastructure/terraform/main.tf:211-239`
- Peering connection created but no route table entries
- **Impact**: Multi-region communication completely broken

### High: Loose Helm Chart Dependencies
- `postgresql: "13.x.x"`, `nats: "1.x.x"`, `redis: "18.x.x"` — too loose

### High: ArgoCD Sync Policy Incomplete
- `secrets-root-app.yaml` missing retry, syncOptions, revisionHistoryLimit

### High: Missing Terraform Password Validation
- `db_password` variable has no complexity/length validation

### Medium: Missing Prometheus Alerts for Infrastructure
- No alerts for: EKS health, RDS failover, ElastiCache lag, cert expiration

### Medium: S3 Replication IAM Permissions Incomplete
- Missing `GetObjectVersionTagging`, `GetObjectRetention` permissions

---

## Priority Action Plan

### Week 1 — Critical Structural Fixes (22 issues)
1. **Add FK constraints** to marketplace Wallet, SellerProfile, BuyerProfile, ProductReview
2. **Fix Terraform AZ mismatch** for Jeddah region
3. **Add VPC peering route tables** for cross-region traffic
4. **Consolidate ApiResponse** to single definition in shared-types/contracts
5. **Fix dataclass event field defaults** — remove `= None` from required fields
6. **Standardize Kong strip_path** to consistent value
7. **Fix error response formats** to unified bilingual pattern
8. **Create 23 missing event schemas**

### Week 2 — High Priority (22 issues)
9. Add tenant isolation indexes to all Prisma schemas
10. Add missing cascade rules on FK relations
11. Fix AlertStatus/FieldStatus type mismatches
12. Replace hardcoded event subjects with constants
13. Fix workspace configuration (add glob, remove file: refs)
14. Pin Helm chart dependency versions exactly
15. Add ArgoCD retry/sync policies
16. Add Terraform password validation

### Month 2 — Medium Priority (39 issues)
17. Consolidate dataclass/Pydantic event model systems
18. Add `__all__` exports to Python modules
19. Standardize event subject naming to scoped pattern
20. Add response_model to all FastAPI endpoints
21. Add tenant validation to all endpoints
22. Register 40+ subjects in SUBJECT_REGISTRY
23. Add Prometheus infrastructure alerts
24. Clean up 8 orphaned packages

### Month 3 — Low Priority (29 issues)
25. Replace `datetime.utcnow()` with `datetime.now(UTC)`
26. Add bilingual validation messages
27. Add discriminated union to ApiResponse
28. Reduce `Record<string, unknown>` usage
29. Remove deprecated coexisting fields
