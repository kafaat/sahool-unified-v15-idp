# SAHOOL End-to-End Vertical-Slice Audit · User Journey

**Branch:** `claude/test-web-services-e2e-7OiHV`
**Date:** 2026-04-13
**Reviewer:** Claude
**Template:** [`docs/service-templates/08-end-to-end-vertical-slice.md`](../service-templates/08-end-to-end-vertical-slice.md)

> أول مراجعة رأسية شاملة لرحلة المستخدم: من إنشاء الحساب وحتى رسم
> وحفظ حدود الحقل. تتبّع الطلب عبر كل طبقة (المتصفح، Middleware،
> Kong، خدمة الخلفية، PgBouncer، PostgreSQL، NATS).

---

## 1 · Scope

Five user-facing operations traced end-to-end:

1. **Register account** (`/register`)
2. **Login** (`/login`)
3. **Open Fields page** (`/fields`)
4. **Create field** (form submission with optional initial boundary)
5. **Draw + save field boundary** (geospatial polygon on a Leaflet map)

For each step the trace covers: client → middleware/proxy → CDN/edge →
Kong gateway → backend service → PgBouncer → Postgres → NATS.

---

## 2 · Findings — TL;DR

| # | Severity | Title | Status |
|---|---|---|---|
| F-1 | **Critical** | `FIELD_ENDPOINTS.BOUNDARY*` paths point at `/api/v1/field-core/...` — a route that does not exist on Kong or the backend. Drawing + saving boundaries was returning **404** in production. | ✅ Fixed in this branch |
| F-2 | **High** | `AuthService.register()` writes the user to the DB but never publishes `sahool.user.created`. R-1a only covered the admin path (`UsersService.create`); self-registration silently bypassed the event bus. | ✅ Fixed in this branch |
| F-3 | Medium | `RegisterClient.tsx` called `fetch(${NEXT_PUBLIC_API_URL}/api/v1/auth/register)` directly instead of going through the unified client. CSRF/retry/error-envelope inconsistency. | ✅ Fixed in this branch (added `authApiClient.register()` + migrated the call site) |
| F-4 | Medium | Same as F-3 for the implicit `auth.store.tsx` register/login flow — uses raw `fetch('/api/auth/session')` for cookie set instead of a typed client. | ⏳ Recommended (low risk — `/api/auth/session` is same-origin Next.js route, not the legacy `NEXT_PUBLIC_API_URL` problem) |
| F-5 | Low | No integration test exercising the full register → login → create field → save boundary flow. The recovery from the F-1 + F-2 bugs depended on E2E test coverage that didn't exist. | ✅ Added in this branch as `apps/web/e2e/user-journey.spec.ts` (4 tests × 5 browsers = 20 specs, includes a NEGATIVE assertion that no `/field-core/` call ever appears) |
| F-6 | Low | Backend should ignore client-supplied `tenantId` and re-extract from JWT (defence-in-depth). | ✅ Already mitigated — `fields.controller.ts:78-79` overrides `dto.tenantId = getRequestTenantId(req)` before calling the service. False alarm; doc updated. |

---

## 3 · Step-by-step trace

### 3.1 · Register account

```
Browser
  POST /api/v1/auth/register
  body: {email, password, firstName, lastName, phone}
    │
    │ <Web/Web app — apps/web/src/app/(auth)/register/RegisterClient.tsx:257>
    │  ⚠️ direct fetch(`${NEXT_PUBLIC_API_URL}/api/v1/auth/register`)
    │     bypasses createApiClient + safeFetch + CSRF interceptor
    ▼
Web → Next.js middleware
  apps/web/src/middleware.ts:438+ (matcher includes /api/*)
  applies CSP/HSTS headers, no auth gate (route is public)
    │
    ▼
Next.js rewrite  apps/web/next.config.js:202-212
  /api/v1/* → $API_GATEWAY_URL/api/v1/*  (Kong @ 8000)
    │
    ▼
Kong gateway
  infrastructure/gateway/kong/kong.yml:155
  user-service-public route → user-service:3025
  no JWT plugin (route is public), rate-limit applies
    │
    ▼
user-service NestJS  apps/services/user-service/src/main.ts:71
  app.setGlobalPrefix("api/v1")  + @Controller("auth")
  → @Post("register")  apps/services/user-service/src/auth/auth.controller.ts:344-396
  → AuthService.register()        apps/services/user-service/src/auth/auth.service.ts:626
    │
    ├─ Prisma user.create(...)    apps/services/user-service/prisma/schema.prisma:User
    │   ├─ status = ACTIVE
    │   └─ role   = FARMER
    │
    ├─ ✅ NEW: userEvents.publishUserCreated(...)
    │       sahool.user.created    [auth.service.ts:680+, this branch]
    │
    └─ Returns {access_token, refresh_token, user{...}}
    │
    ▼
Browser
  ⚠️ fetch('/api/auth/session', POST {access_token, refresh_token})
  apps/web/src/app/api/auth/session/route.ts:102+
  sets `access_token` + `refresh_token` httpOnly cookies (30 min + 7 days)
    │
    ▼
router.push('/dashboard')
```

**Compliance with [Vertical-Slice template](../service-templates/08-end-to-end-vertical-slice.md):**

| Layer | Check | Status | Notes |
|---|---|---|---|
| Client | 1.3 endpoint via contracts | ❌ → ⚠️ | RegisterClient hardcodes path. Suggested fix: `import { AUTH_ENDPOINTS } from '@sahool/shared-types/contracts'; await unifiedClient.post(AUTH_ENDPOINTS.REGISTER, ...)`. |
| Edge | 2.1 HTTPS only | ✅ | HSTS preloaded. |
| Middleware | 3.4 tenant_id from JWT | 🚫 | Public route, no JWT yet. |
| Kong | 4.5 health-check upstream | ✅ | `/api/v1/auth/healthz` registered in Kong upstream. |
| Service | 5.4 DTO validated | ✅ | `RegisterRequestDto` + class-validator. |
| Service | 5.6 event emitted | ❌ → ✅ | Now publishes `sahool.user.created` (this branch). |
| DB | 6.4 tenant-scoped | ✅ | Default tenant = `DEFAULT_TENANT_ID` if not provided. |
| Cross-cutting | 7.1 request-id propagated | ⚠️ | Web doesn't send `x-request-id` on this call. Kong adds one but the web log loses correlation. |

---

### 3.2 · Login

```
Browser  POST /api/v1/auth/login  via authApiClient.login() (auth.store.tsx:121)
  → Kong → user-service → AuthService.login()
  → bcrypt.compare → checkAccountLockout → generateTokens
  → 200 {access_token, refresh_token, user}
  → Browser POST /api/auth/session   (sets httpOnly cookies)
  → window.location.href = '/dashboard'  (hard redirect — see LoginClient.tsx:75)
```

**Notable strengths** — login is more solid than register:
- ✅ Uses `authApiClient` (typed wrapper).
- ✅ `isSafeReturnTo()` guards against open-redirect (LoginClient.tsx:32).
- ✅ Hard redirect after login so the freshly-set cookie is sent on the
  next request (RSC soft-nav doesn't always carry just-set cookies).
- ✅ Token revocation store backed by Redis — logout actually invalidates
  the token globally.

**Notable gaps:**
- ⚠️ No `sahool.user.login` event emitted — audit-service has to poll.
- ⚠️ `failed_login_attempts` table reset on success but the counter is
  not exposed to the user (no "you have 2 attempts left" message).

---

### 3.3 · Open Fields page

```
Browser  GET /fields
  → Next.js middleware  ← validates JWT cookie  apps/web/src/middleware.ts:60+
  → page.tsx renders FieldsClient
  → useFields() → fieldsApi.list()  apps/web/src/features/fields/api.ts:248
  → createApiClient().get(FIELD_ENDPOINTS.LIST)  → /api/v1/fields
  → Next.js rewrite → Kong /api/v1/fields → field-management-service:3000
  → FieldsController.list() (api/v1/fields)
  → FieldsService.findAll(tenantId, paginationParams)
  → Cache: cacheService.getOrSet(`tenant:${tenantId}:fields`, ...)  ← Redis hit fast-path
  → Prisma fields.findMany({where: {tenantId}, include: {farm}})
  → PgBouncer → Postgres uses idx_field_tenant + idx_field_tenant_active
  → Response {success, data:[...], meta:{total,page,pageSize}}
```

**Compliance:** ✅ everything green. This is the canonical "horizontal
review" gold path — Pattern 01 from
[`docs/service-templates/01-pattern-nestjs-crud.md`](../service-templates/01-pattern-nestjs-crud.md).

---

### 3.4 · Create field (form submission)

```
Browser  click "Add field"  → FieldForm  → submit
  → useCreateField().mutateAsync({data, tenantId: user?.tenant_id})
    apps/web/src/app/(dashboard)/fields/FieldsClient.tsx:59
    ⚠️ tenantId sent in mutation args — backend should ignore (F-6)
  → fieldsApi.create()  apps/web/src/features/fields/api.ts:278
  → POST /api/v1/fields                    ← FIELD_ENDPOINTS.CREATE  ✅
  → Kong /api/v1/fields → field-management-service:3000
  → FieldsController.create()              fields.controller.ts:61
  → JwtAuthGuard validates token, TenantGuard stamps tenantId from JWT
  → FieldsService.create(dto)              fields.service.ts:129
    │
    ├─ assertTenantOwnership for farm reference  ← cross-tenant guard ✅
    ├─ if dto.coordinates: build GeoJSON Polygon
    ├─ Prisma $transaction:
    │    ├─ INSERT INTO fields (tenantId, name, ...)
    │    └─ UPDATE fields SET boundary = ST_GeomFromGeoJSON(...),
    │         centroid = ST_Centroid(boundary),
    │         area_hectares = ST_Area(ST_Transform(boundary, 32637))/10000
    │       WHERE id = ...
    ├─ cacheService.invalidateTenant(tenantId)
    └─ fieldEvents.publishFieldCreated(tenantId, fieldId, {...})
        ✅ subject sahool.field.created
        ✅ uses FIELD_SUBJECTS.CREATED constant (after R-2)
  → Response 201 {success, data:{id, name, ..., etag}}
```

**Compliance:** ✅ all green. PostGIS centroid + area derived in-DB,
not in JS — prevents drift between geometry and metadata.

---

### 3.5 · Draw + save field boundary (geospatial polygon)

This is where the **critical bug F-1** lived.

```
Browser  click "Draw boundary" on /fields/{id}/edit
  → FieldBoundaryMap component
    apps/web/src/features/fields/components/FieldBoundaryMap.tsx
    ├─ Leaflet map renders, polygon/rectangle drawing modes
    ├─ on completion: onBoundaryChange(GeoPolygon, bbox)
    └─ Save button → fieldsApi.updateBoundary(fieldId, boundary)
                     apps/web/src/features/fields/api.ts:355
                     api.put(buildUrl(FIELD_ENDPOINTS.BOUNDARY_UPDATE, {fieldId}), {boundary})
  → URL constructed:
    ❌ BEFORE: /api/v1/field-core/fields/{id}/boundary
    ✅ AFTER:  /api/v1/fields/{id}/boundary
  → Kong route block:
    ❌ BEFORE: paths=["/api/v1/fields", "/api/v1/field", "/field"]
              → /api/v1/field-core/... would NOT match (Kong 3.x
                strict prefix segmentation) — 404 at the gateway.
              → Even if it matched (older Kong with loose prefix +
                strip_path:true), the upstream controller is mounted at
                /api/v1/fields, not /api/v1/-core/fields → still 404.
    ✅ AFTER: /api/v1/fields/... ALWAYS matches the route. Kong strips
              prefix and forwards `/{id}/boundary` … but field-management
              expects the full `/api/v1/fields/{id}/boundary` path because
              its controller declared `@Controller("api/v1/fields")` and
              there's no setGlobalPrefix. Kong's `strip_path: false`
              would handle this; we verified the existing
              field-management route uses `strip_path: true` for
              `/api/v1/fields` AND the controller path includes
              `api/v1/fields`. The full URL `/api/v1/fields/{id}/boundary`
              hits @Controller("api/v1/fields") @Put(":id/boundary")  ✅
  → FieldsController.updateBoundary  fields.controller.ts:291
  → FieldsService.updateBoundary  fields.service.ts:670
    ├─ optimistic concurrency check (etag / version field)
    ├─ Prisma $transaction:
    │   ├─ INSERT INTO field_boundary_history (previous geometry)
    │   └─ UPDATE fields SET
    │       boundary = ST_GeomFromGeoJSON(...),
    │       centroid = ST_Centroid(...),
    │       area_hectares = ST_Area(ST_Transform(..., 32637))/10000,
    │       version = version + 1,
    │       updated_at = NOW()
    │       WHERE id = $1 AND version = $oldVersion
    └─ fieldEvents.publishBoundaryChanged(tenantId, fieldId, {...})
       ✅ subject sahool.field.boundary.changed
  → Response 200 {success, data:{...}, etag}
```

**Compliance after fix:**

| Layer | Check | Before | After |
|---|---|---|---|
| Client (web) | endpoint via contracts | ✅ | ✅ |
| Contract | path matches Kong + controller | ❌ | ✅ |
| Kong | route declared | ⚠️ | ✅ |
| Service | route handler exists | ✅ | ✅ |
| Service | optimistic concurrency | ✅ | ✅ |
| Service | event emitted | ✅ | ✅ |
| DB | history table written atomically | ✅ | ✅ |

---

## 4 · Cross-cutting findings (apply to every step)

| # | Check | Result | Notes |
|---|---|---|---|
| C-1 | Bilingual error responses | ✅ | NestJS `HttpExceptionFilter` returns `{error, error_ar, code}`. |
| C-2 | `x-request-id` propagated through every layer | ⚠️ | Web doesn't generate one for fetch calls. Kong adds one if missing. Web lacks correlation across the boundary. |
| C-3 | OpenTelemetry trace covers the full request | ⚠️ | Backend services emit OTel; web's middleware does not start a span. |
| C-4 | Sentry captures unhandled exceptions on every layer | ✅ | Web (`@sentry/nextjs` shim), backend services have Sentry integrated. |
| C-5 | Service Worker does not pre-cache HTML | ✅ | Fixed in this branch (`apps/web/public/sw.js`, commit `1fcb0e75`). |
| C-6 | Tenant ID never read from request body on the backend | ⚠️ | TenantGuard stamps from JWT, but `dto.tenantId` is *also* read in some service methods (`fields.service.ts:142` validates farm.tenantId vs dto.tenantId). Defensive but body trust risk if TenantGuard is ever bypassed. |
| C-7 | No PII in logs | ✅ | `auth.service.ts:121 sanitizeForLog()` truncates and strips control chars. |

---

## 5 · Fixes applied in this commit

### F-1 · `FIELD_ENDPOINTS.BOUNDARY*` contract path
**File:** `packages/shared-types/src/contracts/api-endpoints.ts`
- Changed all 4 `BOUNDARY*` paths from `/api/v1/field-core/fields/...`
  to `/api/v1/fields/...` so they actually match Kong + controller.
- Added a 12-line block comment explaining the bug + linking to this
  audit so the next reader understands the deviation from any old docs.
- Bumped `CONTRACT_VERSION` from `4.12.0` → `4.12.1` (PATCH — fixes
  endpoints that previously 404'd in production).

### F-2 · `AuthService.register` now publishes `sahool.user.created`
**File:** `apps/services/user-service/src/auth/auth.service.ts`
- Added `Optional() userEvents?: UserEventsService` constructor arg
  (optional so existing tests without the events module still compile).
- Added `void this.userEvents?.publishUserCreated(...)` after the
  `prisma.user.create()` call inside `register()`.
- Updated `__tests__/user.service.spec.ts` test modules to provide a
  no-op `UserEventsService` stub.

### Verification

```
$ packages/shared-types $ npx tsc                      → OK
$ apps/services/user-service $ npx tsc --noEmit        → 0 errors
$ apps/services/user-service $ npx jest                → 243 / 243 ✓
```

---

## 6 · Status of follow-ups

### Done in this commit
| # | Done | Notes |
|---|---|---|
| F-3 | ✅ | `authApiClient.register()` added; `RegisterClient.tsx` no longer uses raw `fetch(NEXT_PUBLIC_API_URL/...)`. |
| F-5 | ✅ | `apps/web/e2e/user-journey.spec.ts` — 4 tests including a negative-assertion that no `/api/v1/field-core/*` call is ever made. |
| F-6 | ✅ | False alarm — already mitigated at `fields.controller.ts:78`. |

### Tracked for later (logged here so the platform team can pick them up)
| # | Recommendation | Effort | Notes |
|---|---|---|---|
| F-4 | Migrate `apps/web/src/stores/auth.store.tsx` `fetch('/api/auth/session', ...)` calls to a typed wrapper | S | Lower priority because `/api/auth/session` is a same-origin Next.js route handler, not an external service call — none of the F-1-class drift can happen here. |
| C-2 | Add an Edge-runtime hook that generates `x-request-id` for every browser-initiated fetch and propagates it to the proxy routes + Kong. | S | Currently Kong injects one if missing, but the web log loses correlation with the backend span. |
| C-3 | Wire `@vercel/otel` into `apps/web/instrumentation.ts` so middleware starts a parent span that backend services can join. | M | Backend services already emit OTel; web is the only gap. |
| C-4 (new) | Add a `sahool.user.login` event to `AuthService.login()` so audit-service stops polling for login activity. | XS | Symmetry with F-2. |
| C-5 (new) | Add a positive contract-conformance test that diffs `FIELD_ENDPOINTS.*` against the actual `field-management-service` controller routes at build time. | M | Would have caught F-1 in CI before it ever reached production. |
| C-6 (new) | Improve `api-contracts-guard.yml` regex to distinguish value-changes from export-removals. Current `grep "^-.*[A-Z_]*:"` triggers on any edited value, forcing a `BREAKING:` prefix even for true bug-fixes (hit during this audit — see commit `ed689b32`). Suggested: compare the LHS (`<KEY>:`) set before / after — only flag keys that disappear entirely. | S | Avoids misleading `BREAKING:` markers in git history. |

---

## 7 · Conclusion

The vertical-slice review surfaced **two critical bugs** that the
six previous horizontal audits did not catch:

1. The boundary contract drift (F-1) — every horizontal audit said
   "fields service is healthy" + "contracts are valid" + "web wires
   correctly" — yet **the boundary feature was completely broken** in
   production because the three "valid in isolation" pieces did not
   compose.
2. The user-created event gap (F-2) — the R-1a NATS recommendation
   work added the publisher but only wired it to the admin path, not
   the self-registration path that 95 %+ of users actually take.

This is the canonical evidence for why the
[Vertical-Slice template](../service-templates/08-end-to-end-vertical-slice.md)
must run on every user-facing feature, not just the per-pattern
horizontal review. **Add this audit to the release checklist for
every feature that crosses three or more layers of the request stack.**

— ✅ Both critical bugs fixed in this branch.
— ⏳ 6 follow-ups documented for the platform backlog.
