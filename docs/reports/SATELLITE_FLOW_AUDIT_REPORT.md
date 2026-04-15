# SAHOOL Satellite Flow — End-to-End Audit Report
## تقرير التدقيق الشامل لمسار بيانات الأقمار الصناعية

**Date**: 2026-04-10
**Branch**: `claude/nextjs-deep-diagnostics-4mwfe`
**Scope**: UI → Next.js API proxies → Python/Node services → PostGIS/Prisma schema → NATS event pipeline → Redis/MinIO cache layer
**Methodology**: 6 parallel specialist audit agents, each scoped to one architectural layer
**Total findings**: **69** (3 CRITICAL, 17 HIGH, 30 MEDIUM, 19 LOW)

---

## 1. Architecture Map — خريطة التدفق

```
┌─────────────────────── Browser ───────────────────────┐
│ apps/web/.../satellite/SatelliteClient.tsx           │
│ apps/admin/.../analytics/satellite/page.tsx          │
│ (Leaflet / MapLibre / Google Maps)                   │
└──────────────────────────┬────────────────────────────┘
                           │ fetch('/api/satellite?…')
┌──────────────────────────▼────────────────────────────┐
│  Next.js 15 proxy routes                              │
│  apps/web/src/app/api/satellite/route.ts              │
│  apps/admin/src/app/api/satellite/route.ts   ⚠ NO AUTH│
└──────────────────────────┬────────────────────────────┘
                           │ HTTP → Kong
┌──────────────────────────▼────────────────────────────┐
│  Python FastAPI services                              │
│  vegetation-analysis-service (8090)  — primary        │
│  indicators-service          (8091)  — aggregation    │
│  ndvi-processor              (8118)  — DEPRECATED     │
│  crop-intelligence-service   (8095)  — disease/pests  │
└──────────┬─────────────────────────┬──────────────────┘
           │                         │
┌──────────▼─────────┐    ┌──────────▼──────────────────┐
│ Provider clients   │    │  Redis cache                │
│ • Sentinel Hub     │    │  satellite:ndvi:{field_id}… │
│ • Planet (stub)    │    │  ⚠ NO tenant prefix         │
│ • Copernicus STAC  │    └─────────────────────────────┘
│ • SimulatedProvider│
└──────────┬─────────┘
           │
┌──────────▼───────────────────────────────────────────┐
│  NATS JetStream events (4-layer architecture)        │
│  Acquisition → Intelligence → Decision → Business    │
│  ⚠ subjects NOT tenant-scoped in vegetation-analysis │
└──────────┬───────────────────────────────────────────┘
           │
┌──────────▼───────────────────────────────────────────┐
│  Postgres + PostGIS (field-management-service DB)    │
│  • Field            (boundary, centroid, ndviValue)  │
│  • NdviReading      ⚠ no provider/scene_id/UNIQUE    │
│  • FieldKpiSnapshot ⚠ no retention, no dedup         │
└───────────────────────────────────────────────────────┘
```

---

## 2. Critical Findings (must fix) — حرجة

| # | Layer | File:line | Issue | Impact |
|---|---|---|---|---|
| **C1** | Next.js proxy | `apps/admin/src/app/api/satellite/route.ts` | **No JWT verification**, no tenant extraction, no rate limiting | Unauthenticated browser can hit backend satellite service via admin proxy; arbitrary data access + DoS vector |
| **C2** | Provider integration | `apps/services/vegetation-analysis-service/src/multi_provider.py:185-188, 200, 219` | Sentinel Hub OAuth2 token cached in **process memory only**, credentials read from bare `os.getenv()` with no Vault fallback | Horizontal scale triggers thundering-herd on token endpoint; credential rotation requires full restart |
| **C3** | Provider integration | `apps/services/vegetation-analysis-service/src/multi_provider.py:1034-1200` | `SimulatedProvider` returns **deterministic fake NDVI** (day-of-year × sine + noise) when credentials missing, and callers don't check `is_simulated` | Farmers may make irrigation/fertilizer decisions on synthetic data with no visible warning in the UI |

---

## 3. High Findings — عالية (abridged to top 17)

### Provider integration (vegetation-analysis-service)
- **H1** No retry/backoff on provider HTTP failures; 429/5xx silently falls through to the next provider → `multi_provider.py:1149-1200`
- **H2** No request-quota accounting → Sentinel Hub free tier (30k PU/month) can burn in minutes
- **H3** AOI size unbounded → a 100°×100° bbox is legally accepted → `multi_provider.py:251,325-329`
- **H4** `ndvi-processor` still listens on port 8118 with no `X-API-Deprecated` / `Sunset` headers despite being marked deprecated in `CLAUDE.md` → `apps/services/ndvi-processor/src/main.py`

### Backend services (FastAPI)
- **H5** Public endpoints without `Depends(get_current_user)`: `/v1/phenology/recommendations/*`, `/v1/phenology/crops`, `/v1/indices/guide`, `/v1/satellites`, `/v1/regions`, `/v1/providers` → `vegetation-analysis-service/src/main.py:997-2683`
- **H6** `GET /v1/timeseries/{field_id}`, `GET /v1/phenology/{field_id}` extract `tenant_id` from JWT but **don't verify the field belongs to that tenant** (IDOR) → `main.py:1534,1751`
- **H7** Long-running satellite processing runs **synchronously** inside the HTTP handler → 10+s blocks → `main.py:1161,1426`
- **H8** indicators-service `POST /v1/field/{field_id}/indicators` accepts `tenant_id` as optional body param; if omitted, INSERT happens with `NULL tenant_id` → `indicators-service/src/main.py:1199,381-391`

### Next.js proxy (admin + web)
- **H9** Admin satellite route is missing the rate limiter + trusted-proxy IP extractor used by the sibling weather route → `apps/admin/src/app/api/satellite/route.ts`
- **H10** JWT algorithm pinning on admin is indirect (inherits from `getUserFromToken`), not inlined with explicit `algorithms: ['HS256']`

### UI (Next.js App Router)
- **H11** Both admin and web satellite pages are `'use client'` with `useEffect` waterfall data fetching — no SSR, no Suspense boundaries → `apps/admin/src/app/analytics/satellite/page.tsx:1,98-125`

### DB schema
- **H12** `NdviReading` has **no provider/scene_id/request_id columns** → no data lineage, no re-fetch path → `apps/services/field-management-service/prisma/schema.prisma:289-317`

### Events pipeline
- **H13** `vegetation-analysis-service` publishes `sahool.satellite.analysis_completed` but **no service subscribes** to it; the actual downstream subscriber (`indicators-service`) listens for `sahool.satellite.ndvi.computed` published by `ndvi-processor` only → orphaned events → `main.py:1353-1362` vs `indicators-service/src/main.py:295`
- **H14** NATS subjects in `vegetation-analysis-service` are **not tenant-scoped** (don't use `get_tenant_subject()`) — cross-tenant leakage risk on JetStream wildcard subs → `main.py:1354,2033,4212`

### Redis cache
- **H15** Cache keys for satellite results are `satellite:ndvi:{field_id}:{date}:{sat}` with **no tenant prefix** → multi-tenant collisions → `vegetation-analysis-service/src/cache.py:87-100`

### Database writes
- **H16** `indicators-service` raw `INSERT INTO field_indicators` can fire with `NULL tenant_id` → `indicators-service/src/main.py:381-391,543`
- **H17** No unique constraint on `NdviReading(field_id, captured_at, provider)` → duplicate imports on replay → `schema.prisma:289-317`

---

## 4. Medium Findings — متوسطة (30, summarized)

| Area | Count | Representative issue |
|---|---|---|
| **Validation** | 6 | No max area (km²) check, no date-range max, no file upload size limits, cloud-cover filter inconsistent (50 vs 30), loose `response_model=dict` |
| **Tenant isolation** | 4 | DB writes without enforced tenant, cache keys missing tenant, NATS subjects missing tenant, NdviReading soft-delete not cascaded from Field |
| **Observability** | 5 | Logs leak `field_id`, no PU cost accounting, no per-request tracing of provider latency, NATS publishes swallow errors, `/metrics` endpoint public |
| **Architecture drift** | 5 | NDVI formula defined in 3 places (vegetation-analysis / ndvi-processor / indicators-service), `sahool-eo` not in `requirements.txt`, Copernicus STAC provider returns `None`, Planet Labs only searches, ndvi-processor still active |
| **Error handling** | 4 | Raw exception messages in responses, dev-only `jose.decodeJwt` fallback fragile, silent fallback to simulated without logging field_id, path-traversal fieldId not `encodeURIComponent`-wrapped in admin proxy |
| **UI** | 6 | NDVI colormap defined 3 times with different hex values, RTL map controls hardcoded `right-4`, disabled non-NDVI index buttons in both apps, `Download` button stubbed, web analytics page ships hardcoded mock data, no polygon boundary rendered on map |

---

## 5. Low Findings — منخفضة (19, grouped)

- **Testing**: no `test_*satellite*.py` or HTTP-level satellite tests in any of the 4 services
- **Cache TTL**: hardcoded 1h in `multi_provider.py:1110` — not per-index/per-crop configurable
- **Token expiration buffer**: 60s clock-skew buffer may be insufficient
- **Retention**: no TTL / cron job for `NdviReading` or `FieldKpiSnapshot`
- **Hydration risk**: `new Date()` in some NDVI date formatters
- **Bbox/centroid consumption**: UI ignores the newly-added `bbox` and `centroidLat/Lng` fields from `FieldResponseDto` (commit `a6fa84e`) and re-derives from `location` instead
- **i18n**: date formats hardcoded to `ar-YE` locale in charts
- **Static assets**: Leaflet CSS still loaded from `unpkg.com` in root layout

---

## 6. Positive Findings — نقاط القوة

- ✅ `apps/web/src/app/api/satellite/route.ts` is the **reference pattern**: JWT pinned, tenant validated, IP extracted via trusted proxy helper, body parsed, fieldId URL-encoded, timeouts set, errors sanitized
- ✅ `shared/events/streams.py` JetStream config is 4-layer compliant (30d retention, 5 GB max, 120s dedup window)
- ✅ `ndvi-processor` correctly upserts on `(tenant_id, field_id, acquisition_date)` — idempotent replay
- ✅ No Sentinel Hub credentials leaked to client bundle — all tile requests go via server proxy
- ✅ `NdviReading` and `FieldKpiSnapshot` both carry `tenantId` columns with indexes
- ✅ Image bytes are NOT stored in Postgres — only metadata and aggregate values

---

## 7. Prioritized Remediation Plan

### Wave 1 (mechanical, safe — apply this sweep)
1. **Auth + rate limit + deprecation on admin satellite proxy** (C1) — mirror the web route
2. **Tenant-scoped Redis cache keys** (H15)
3. **Tenant-scoped NATS subjects** in vegetation-analysis (H14) via `get_tenant_subject()`
4. **Fix orphaned event subject**: vegetation-analysis should publish `sahool.satellite.ndvi.computed` (H13)
5. **URL-encode fieldId + X-Tenant-Id header + encode path params** in admin proxy (H10 tail, med issues)
6. **Deprecation headers** on `ndvi-processor` (H4)
7. **Cloud-cover filter** in `getTenantNdviSummary()` SQL (med #6)
8. **Unique constraint + provider/scene_id migration** for `NdviReading` (H12, H17)

### Wave 2 (architectural, plan-required)
- Redis-backed token cache for Sentinel Hub OAuth (C2)
- Vault integration for provider credentials (C2)
- Background-task queue for long-running satellite jobs (H7)
- Centralize NDVI formula into one shared module (med architecture drift)
- Consolidate / migrate callers off `ndvi-processor` and archive it (H4)
- Unified NDVI colormap constant in a shared package (med UI)
- Server-component refactor of satellite UI pages (H11)
- Retention job / partitioning for `NdviReading` (low retention)

---

## 8. Files referenced (for Wave-1 follow-through)

| File | Reason |
|---|---|
| `apps/admin/src/app/api/satellite/route.ts` | C1, H9, H10 |
| `apps/web/src/app/api/satellite/route.ts` | Reference pattern |
| `apps/services/vegetation-analysis-service/src/main.py` | H5, H6, H7, H13, H14 |
| `apps/services/vegetation-analysis-service/src/multi_provider.py` | C2, C3, H1, H2, H3 |
| `apps/services/vegetation-analysis-service/src/cache.py` | H15 |
| `apps/services/indicators-service/src/main.py` | H8, H16 |
| `apps/services/ndvi-processor/src/main.py` | H4 |
| `apps/services/field-management-service/prisma/schema.prisma` | H12, H17 |
| `apps/services/field-management-service/src/ndvi/ndvi.service.ts` | cloud-cover filter (med #6) |
| `apps/admin/src/app/analytics/satellite/page.tsx` | H11 |
| `apps/web/src/app/(dashboard)/satellite/SatelliteClient.tsx` | H11, UI med |

---

_Last updated: 2026-04-10. Remediation Wave 1 applied in follow-up commits on this branch._
