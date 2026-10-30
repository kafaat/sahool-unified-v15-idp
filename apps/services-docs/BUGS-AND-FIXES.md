# SAHOOL Platform - Bugs, Fixes, and Recommendations
# الأخطاء والإصلاحات والتوصيات

**Last Updated:** 2026-03-18
**Platform Version:** 16.0.0

---

## Table of Contents

1. [Critical Bugs](#critical-bugs)
2. [High Priority Fixes](#high-priority-fixes)
3. [Medium Priority Issues](#medium-priority-issues)
4. [Configuration Issues](#configuration-issues)
5. [Missing Features](#missing-features)
6. [Deprecated Services](#deprecated-services)
7. [Recently Fixed - Web & Admin Review (March 2026)](#recently-fixed---web--admin-review-march-2026)
8. [Recommended Actions](#recommended-actions)

---

## Critical Bugs

### BUG-001: Port Conflict - audit-service vs chat-service

**Severity:** CRITICAL
**Affected Services:** audit-service, chat-service

**Issue:**
Both services were configured to use port 8114:
- `audit-service` → 8114
- `chat-service` → 8114

**Impact:**
Only one service can run at a time. The second service fails to start.

**Fix Applied:**
Chat-service moved to port 8115. Audit-service remains on 8114.
Docker-compose and service-ports.ts now reflect correct ports:
- `audit-service` → 8114 (SERVICE_PORTS.AUDIT_SERVICE)
- `chat-service` → 8115 (SERVICE_PORTS.CHAT_SERVICE)

**Status:** FIXED (chat-service moved to 8115)

---

### BUG-002: MCP Server Duplicate Port Mapping

**Severity:** HIGH
**Affected Services:** mcp-server

**Issue:**
MCP server had duplicate port mappings in docker-compose:
- Port 8200 (external) - conflicted with Vault
- Port 8201 (external)

**Impact:**
Confusion about which port to use; conflict with Vault on 8200.

**Fix Applied:**
Standardized on port 8201. Port 8200 now exclusively used by Vault.
Docker-compose uses only `127.0.0.1:8201:8201`.
Service-ports.ts comment: "changed from 8200 to avoid Vault conflict".

**Status:** FIXED

---

### BUG-003: Admin App Static Data Fallback

**Severity:** CRITICAL
**Affected Files:** `apps/admin/src/lib/api.ts`

**Issue:**
All API functions silently fell back to mock data on error, hiding service failures.

**Code Location:** `apps/admin/src/lib/api.ts` - `fetchDashboardStats()`

```typescript
// Previous problematic pattern:
} catch (error) {
  return {
    totalFarms: 156,  // Static mock data
    activeFarms: 142,
    // ...
  };
}
```

**Impact:**
- Users see fake data without knowing services are down
- Hard to debug production issues
- Data inconsistency

**Fix Applied:**
Mock data removed from `fetchDashboardStats()`. Errors are now thrown
for React Query to handle with proper error boundaries.
List-type functions still return empty arrays for graceful degradation.

```typescript
// Fixed pattern:
} catch (error) {
  logger.error("fetchDashboardStats failed", { error });
  throw error;
}
```

**Status:** FIXED

---

## High Priority Fixes

### FIX-001: Missing Services in Kong Gateway

**Severity:** HIGH
**Affected Services:** Multiple

**Issue:**
Several services are defined in docker-compose but not registered in Kong Gateway:

| Service | Docker Port | Kong Route |
|---------|-------------|------------|
| knowledge-graph | 8140 | MISSING |
| yield-engine | 8098 | MISSING |
| agent-registry | 8160 | MISSING |
| globalgap-compliance | 8120 | MISSING (conflicts with field-intelligence) |
| logistics-service | 8115 | MISSING |
| ussd-gateway | 8180 | MISSING |

**Fix:**
Add missing routes to `kong/kong.yaml`:

```yaml
services:
  - name: knowledge-graph
    url: http://knowledge-graph:8140
    routes:
      - name: knowledge-graph-route
        paths:
          - /api/v1/knowledge
        strip_path: false

  - name: yield-engine
    url: http://yield-engine:8098
    routes:
      - name: yield-engine-route
        paths:
          - /api/v1/yield
        strip_path: false
```

**Status:** NEEDS FIX

---

### FIX-002: Inconsistent Health Check Endpoints

**Severity:** HIGH
**Affected Services:** Multiple Python services

**Issue:**
Some services use `/healthz`, others use `/health`, and some use `/health/live`.

**Current State:**
- FastAPI services: `/healthz`, `/readyz`
- NestJS services: `/health`, `/health/live`, `/health/ready`
- Some services: Only `/health`

**Impact:**
Kubernetes/Docker health checks may fail for inconsistent services.

**Fix:**
Standardize all services to implement:
- `/healthz` - Liveness probe
- `/readyz` - Readiness probe
- `/health` - Combined status (for backward compatibility)

**Python FastAPI Template:**
```python
@app.get("/healthz")
def liveness():
    return {"status": "ok"}

@app.get("/readyz")
def readiness():
    return {
        "status": "ok",
        "database": getattr(app.state, "db_connected", False),
        "nats": getattr(app.state, "nats_connected", False),
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "service-name",
        "version": "16.0.0",
    }
```

**Status:** FIXED (98.2% compliance - 56/57 Python services have /healthz + /readyz.
Only demo-data lacks endpoints, which is expected as it's a utility script.)

---

### FIX-003: Missing Database Migrations

**Severity:** HIGH
**Affected Services:** Multiple services using Tortoise ORM

**Issue:**
Several Python services using Tortoise ORM don't have proper migration files.

**Affected Services:**
- notification-service
- task-service
- equipment-service
- inventory-service
- billing-core

**Fix:**
Add Aerich migrations to each service:

```bash
# For each service:
cd apps/services/<service-name>
aerich init -t src.db.TORTOISE_ORM
aerich init-db
aerich migrate --name initial
```

**Status:** NEEDS FIX

---

### FIX-004: Redis Connection Pooling

**Severity:** HIGH
**Affected Services:** All services using Redis

**Issue:**
Many services create new Redis connections per request instead of using connection pools.

**Impact:**
- Connection exhaustion under load
- Memory leaks
- Slow performance

**Current Pattern:**
```python
# Bad: Creates new connection per request
redis = Redis(host='redis', port=6379)
```

**Fix:**
```python
# Good: Use connection pool
from redis import ConnectionPool, Redis

pool = ConnectionPool(
    host='redis',
    port=6379,
    max_connections=10,
    decode_responses=True,
)
redis = Redis(connection_pool=pool)
```

**Status:** NEEDS FIX

---

## Medium Priority Issues

### ISSUE-001: Deprecated Service References

**Severity:** MEDIUM

Several deprecated services are still referenced in code:

| Deprecated Service | Replacement | Status |
|-------------------|-------------|--------|
| satellite-service | vegetation-analysis-service | References still exist |
| weather-advanced | weather-service | References still exist |
| crop-health-ai | crop-intelligence-service | References still exist |
| fertilizer-advisor | advisory-service | References still exist |
| field-ops | field-management-service | References still exist |
| field-core | field-management-service | References still exist |
| field-service | field-management-service | References still exist |

**Fix Applied:**
- Kong gateway: Deprecated routes removed and documented in `kong.yml` (lines 1454-1469)
- Admin config: Uses UNIFIED_PORTS from `@sahool/shared-types/contracts`
- Docker-compose: Deprecated services moved to `--profile deprecated`
- Service-ports.ts: SERVICE_PORT_ALIASES maps old names to new ports

**Status:** FIXED

---

### ISSUE-002: Missing Error Boundaries

**Severity:** MEDIUM
**Affected Files:** `apps/admin/src/app/**/*.tsx`

**Issue:**
Most pages don't have error boundaries, causing entire app to crash on component errors.

**Fix:**
Add error boundaries to all major pages:

```typescript
// apps/admin/src/components/common/PageErrorBoundary.tsx
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class PageErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-6 text-center">
          <h2 className="text-xl font-bold text-red-600">Something went wrong</h2>
          <p className="text-gray-600 mt-2">{this.state.error?.message}</p>
          <button
            onClick={() => this.setState({ hasError: false })}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded"
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

### ISSUE-003: No Rate Limiting on Admin API Routes

**Severity:** MEDIUM
**Affected Files:** `apps/admin/src/app/api/**/*.ts`

**Issue:**
Admin Next.js API routes don't have rate limiting, making them vulnerable to abuse.

**Fix:**
Add rate limiting middleware:

```typescript
// apps/admin/src/lib/rate-limit.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const rateLimit = new Map();

export function rateLimitMiddleware(request: NextRequest, limit = 60) {
  const ip = request.ip ?? 'anonymous';
  const now = Date.now();
  const windowStart = now - 60000; // 1 minute window

  const requests = rateLimit.get(ip) || [];
  const recentRequests = requests.filter((time: number) => time > windowStart);

  if (recentRequests.length >= limit) {
    return NextResponse.json(
      { error: 'Too many requests' },
      { status: 429 }
    );
  }

  rateLimit.set(ip, [...recentRequests, now]);
  return null;
}
```

---

### ISSUE-004: Hardcoded API Timeouts

**Severity:** MEDIUM

**Issue:**
API timeouts were hardcoded to 30000ms, which is too short for some operations.

**Fix Applied:**
Added `TIMEOUT_TIERS` in `apps/admin/src/config/api.ts`:

```typescript
export const TIMEOUT_TIERS = {
  default: 30000,
  upload: 120000,    // File uploads
  analysis: 180000,  // AI analysis
  report: 60000,     // Report generation
  healthCheck: 5000, // Health checks
} as const;
```

Health check function now uses `TIMEOUT_TIERS.healthCheck` instead of hardcoded `5000`.

**Status:** FIXED

---

## Configuration Issues

### CONFIG-001: Missing Environment Variables

**Severity:** HIGH

Many services require environment variables that are not documented:

#### notification-service (8110)
```bash
# Required but often missing:
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
FCM_SERVER_KEY=
FIREBASE_CREDENTIALS_JSON=
SENDGRID_API_KEY=
META_WHATSAPP_ACCESS_TOKEN=
TELEGRAM_BOT_TOKEN=
```

#### vegetation-analysis-service (8090)
```bash
SENTINEL_HUB_CLIENT_ID=
SENTINEL_HUB_CLIENT_SECRET=
NASA_EARTHDATA_USERNAME=
NASA_EARTHDATA_PASSWORD=
```

#### ai-advisor (8112)
```bash
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
OLLAMA_BASE_URL=http://ollama:11434
QDRANT_URL=http://qdrant:6333
```

#### billing-core (8089)
```bash
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=
THARWATT_API_KEY=
THARWATT_MERCHANT_ID=
```

#### weather-service (8092)
```bash
OPENWEATHERMAP_API_KEY=
WEATHERAPI_KEY=
```

---

### CONFIG-002: Database URL Inconsistency

**Issue:**
Some services use `DATABASE_URL`, others use `POSTGRES_*` individual variables.

**Fix:**
Standardize all services to use `DATABASE_URL`:

```bash
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
```

---

## Missing Features

### MISSING-001: Admin App - User Management CRUD

**File:** `apps/admin/src/app/users/page.tsx`

**Current State:** Read-only user list
**Required:** Full CRUD operations

**Implementation:**
- Create user form
- Edit user modal
- Delete user confirmation
- Role management
- Password reset

---

### MISSING-002: Admin App - Real-time Notifications

**Current State:** Static notification list
**Required:** WebSocket-based real-time notifications

**Implementation:**
- Connect to ws-gateway:8081
- Subscribe to notification events
- Show toast on new notification
- Badge counter in header

---

### MISSING-003: Admin App - Export Functionality

**Current State:** No data export
**Required:** Export to CSV/Excel/PDF

**Implementation:**
- Add export buttons to data tables
- Implement client-side CSV generation
- Add server-side PDF generation for reports

---

### MISSING-004: Admin App - Audit Logging

**Current State:** No audit logs visible
**Required:** Admin action audit trail

**Implementation:**
- Connect to audit-service
- Display action history
- Filter by user, action type, date

---

## Deprecated Services

The following services should NOT be used:

| Service | Status | Replacement | Action |
|---------|--------|-------------|--------|
| satellite-service | DEPRECATED | vegetation-analysis-service | Remove references |
| weather-advanced | DEPRECATED | weather-service | Remove references |
| crop-health-ai | DEPRECATED | crop-intelligence-service | Remove references |
| fertilizer-advisor | DEPRECATED | advisory-service | Remove references |
| field-ops | DEPRECATED | field-management-service | Remove references |
| field-core | DEPRECATED | field-management-service | Remove references |
| field-service | DEPRECATED | field-management-service | Remove references |
| community-chat | DEPRECATED | chat-service | Update references |

---

## Recently Fixed - Web & Admin Review (March 2026)

The following bugs were identified and fixed during a comprehensive code review
of the Web and Admin frontend applications on 2026-03-18.

### BUG-004: Missing Auth Credentials in Admin API Service Calls

**Severity:** HIGH
**Affected Files:** `apps/admin/src/lib/api/services.ts`, `apps/admin/src/lib/api/extended-services.ts`

**Issue:**
20 `fetch()` calls across IoT, Irrigation, Alert, Equipment, Task, Inventory,
Research, and Marketplace services were missing `credentials: "same-origin"`.
This prevented httpOnly authentication cookies from being sent with requests.

**Affected Services:**
| Service | Missing Calls |
|---------|--------------|
| iotService | `getAll()`, `getReadings()` |
| irrigationService | `getAll()` |
| alertService | `getAll()` |
| equipmentService | `getAll()` |
| taskService | `getAll()` |
| inventoryService | `getAll()`, `getTransactions()`, `adjustQuantity()` |
| researchService | `getAllProjects()`, `getProjectById()`, `createProject()`, `updateProject()`, `deleteProject()`, `getAllExperiments()`, `createExperiment()` |
| marketplaceService | `getAll()`, `getById()`, `update()`, `delete()` |

**Impact:**
API calls fail authentication in production when using cookie-based auth.
Users would see unauthorized errors on list/read operations.

**Fix Applied:**
Added `fetchDefaults` (with `credentials: "same-origin"`) to all 20 fetch calls.

**Status:** FIXED

---

### BUG-005: Hardcoded tenant_id in Web Weather API

**Severity:** HIGH
**Affected Files:** `apps/web/src/lib/api/client.ts`

**Issue:**
Three weather API methods (`getWeather`, `getWeatherForecast`, `getAgriculturalRisks`)
hardcoded `tenant_id: "default"` instead of extracting it from the JWT token.

```typescript
// Before (broken):
body: JSON.stringify({
  tenant_id: "default",  // Always sends "default"
  ...
});

// After (fixed):
const tenantId = this.token ? this.extractTenantFromToken(this.token) : null;
body: JSON.stringify({
  tenant_id: tenantId || "default",  // Uses actual tenant from JWT
  ...
});
```

**Impact:**
Multi-tenant isolation was bypassed for weather data. All tenants received
the same weather data regardless of their tenant context.

**Status:** FIXED

---

### BUG-006: useContextCompression Decompression Bug

**Severity:** HIGH
**Affected Files:** `apps/web/src/hooks/ai/useContextCompression.ts`

**Issue:**
The `decompress()` function always applied RLE (Run-Length Encoding) decompression,
but `compress()` only applies RLE at `CompressionLevel.HIGH`. Data compressed at
LOW or MEDIUM levels would fail to decompress or produce corrupted output.

**Fix Applied:**
Decompress now tries plain JSON parse first (works for LOW/MEDIUM), and falls
back to RLE decompression only if plain parse fails (for HIGH level).

**Status:** FIXED

---

### BUG-007: useApiQuery State Updates After Unmount

**Severity:** MEDIUM
**Affected Files:** `apps/admin/src/hooks/api/use-api-query.ts`

**Issue:**
The `fetchData` callback in `useApiQuery` had no mechanism to cancel in-flight
requests. If a component unmounts while a fetch is in progress, `setState` calls
would execute after unmount, causing React warnings and potential memory leaks.

**Fix Applied:**
Added `AbortController` support. The effect cleanup aborts pending requests,
and all setState calls check `signal.aborted` before executing.

**Status:** FIXED

---

### BUG-008: useRealtimeSync Events Array Re-subscription

**Severity:** MEDIUM
**Affected Files:** `apps/admin/src/hooks/api/use-realtime.ts`

**Issue:**
The `events` array parameter was included directly in the useEffect dependency
array. Since arrays are recreated on every render, this caused unnecessary
WebSocket re-subscriptions on every render cycle.

**Fix Applied:**
Used a `useRef` to store the events array and a stable string key (`events.join(",")`)
for the dependency array. Re-subscriptions now only happen when the actual event
types change.

**Status:** FIXED

---

### BUG-009: Middleware JWT Validation Missing Error Handling

**Severity:** MEDIUM
**Affected Files:** `apps/web/src/middleware.ts`

**Issue:**
The `validateJwtToken()` call in the Edge middleware was not wrapped in try-catch.
If the function threw an unhandled exception (e.g., malformed token causing a
crypto error), the entire middleware would crash, returning a 500 error instead
of redirecting to login.

**Fix Applied:**
Wrapped `validateJwtToken()` in try-catch. On exception, logs the error and
treats it as an invalid token, redirecting to login gracefully.

**Status:** FIXED

---

### BUG-010: ErrorBoundary Unsafe Window/Navigator Access

**Severity:** MEDIUM
**Affected Files:** `apps/admin/src/components/common/ErrorBoundary.tsx`

**Issue:**
The `logErrorToServer()` method accessed `window.location.href` and
`navigator.userAgent` without SSR-safety guards. In server-side rendering
contexts, these globals are undefined and would throw.

**Fix Applied:**
Added `typeof window !== "undefined"` and `typeof navigator !== "undefined"`
guards with `"unknown"` fallback values.

**Status:** FIXED

### BUG-011: Admin Weather API Hardcoded tenant_id

**Severity:** HIGH
**Affected Files:** `apps/admin/src/lib/api.ts`, `apps/admin/src/app/api/weather/route.ts`

**Issue:**
Three weather API functions (`getWeatherCurrent`, `getWeatherForecast`,
`getAgriculturalReport`) hardcoded `tenant_id: "default"` in POST bodies
instead of extracting from the JWT token. Same class of bug as BUG-005
(web app), causing incorrect tenant context for multi-tenant deployments.

Initial fix attempted client-side JWT decoding via `getTenantFromToken()`,
but this cannot work because `sahool_admin_token` is stored as an httpOnly
cookie (set in `/api/auth/login/route.ts` with `httpOnly: true`), making it
inaccessible to client-side JavaScript (`Cookies.get()` returns `undefined`).

**Fix Applied:**
Created a server-side Next.js API proxy route (`/api/weather`) that:
1. Reads the httpOnly cookie server-side via `cookies()` API
2. Extracts `tenant_id` from the JWT using `getUserFromToken()`
3. Validates the tenant_id is a valid UUID (injection prevention)
4. Forwards the request to the backend weather-service with the real tenant_id

All 3 weather client functions now call `/api/weather` with `credentials: "same-origin"`
instead of directly hitting the backend weather-service.

**Status:** FIXED

### BUG-012: NdviTileLayer Callback Props in useEffect Dependencies

**Severity:** MEDIUM
**Affected Files:** `apps/web/src/features/fields/components/NdviTileLayer.tsx`

**Issue:**
The main `useEffect` that manages the NDVI raster layer included `onLoad`,
`onError`, and `isLayerLoaded` in its dependency array. Since `onLoad`/`onError`
are callback props, parent re-renders create new function references, causing
the effect to re-run and unnecessarily remove/re-add the NDVI tile layer.

**Fix Applied:**
Used `useRef` for `onLoad` and `onError` callbacks (same pattern as BUG-008).
Removed `onLoad`, `onError`, and `isLayerLoaded` from deps array.

**Status:** FIXED

### BUG-013: SatelliteMap onFieldClick Causes Full Marker Rebuild

**Severity:** MEDIUM
**Affected Files:** `apps/admin/src/components/maps/SatelliteMap.tsx`

**Issue:**
The `updateMarkers` `useEffect` included `onFieldClick` in its dependency
array. Since this callback is a prop, every parent re-render caused all
map markers to be destroyed and rebuilt (clear → recreate → fitBounds),
resulting in visible flickering and wasted computation.

**Fix Applied:**
Used `useRef` for `onFieldClick` callback and removed it from deps array.

**Status:** FIXED

---

## Recommended Actions

### Immediate (This Week)

1. ~~**Fix port conflicts** (BUG-001, BUG-002)~~ ✅ DONE
2. ~~**Remove mock data fallbacks** (BUG-003)~~ ✅ DONE
3. **Add missing Kong routes** (FIX-001)

### Short Term (This Month)

4. ~~**Standardize health checks** (FIX-002)~~ ✅ DONE (98.2% compliance)
5. **Add database migrations** (FIX-003)
6. **Implement Redis connection pooling** (FIX-004)
7. ~~**Update deprecated service references** (ISSUE-001)~~ ✅ DONE

### Medium Term (This Quarter)

8. **Add error boundaries** (ISSUE-002)
9. **Implement rate limiting** (ISSUE-003)
10. ~~**Make timeouts configurable** (ISSUE-004)~~ ✅ DONE
11. **Document all required environment variables** (CONFIG-001)
12. **Implement missing admin features** (MISSING-001 to MISSING-004)

### Completed (March 2026 - Web & Admin Review)

13. ~~**Fix missing auth credentials in admin API** (BUG-004)~~ ✅ DONE
14. ~~**Fix hardcoded tenant_id in weather API** (BUG-005)~~ ✅ DONE
15. ~~**Fix decompression bug in context compression** (BUG-006)~~ ✅ DONE
16. ~~**Fix useApiQuery state updates after unmount** (BUG-007)~~ ✅ DONE
17. ~~**Fix useRealtimeSync re-subscription** (BUG-008)~~ ✅ DONE
18. ~~**Fix middleware JWT error handling** (BUG-009)~~ ✅ DONE
19. ~~**Fix ErrorBoundary SSR-safety** (BUG-010)~~ ✅ DONE

### Completed (March 2026 - Map & Field Tools Review)

20. ~~**Fix admin weather API hardcoded tenant_id** (BUG-011)~~ ✅ DONE
21. ~~**Fix NdviTileLayer callback deps causing layer rebuild** (BUG-012)~~ ✅ DONE
22. ~~**Fix SatelliteMap onFieldClick causing marker rebuild** (BUG-013)~~ ✅ DONE

### Completed (March 2026 - Multi-Index Satellite Enhancement)

23. ~~**Wire satellite index selector to display selected index data** (FEAT-001)~~ ✅ DONE
    - SatelliteClient.tsx: Index selector now switches field list, stats, legend, and progress bars between NDVI/NDWI/EVI/SAVI/NDRE/LAI
    - Added INDEX_CONFIG with per-index color stops, labels, and descriptions
24. ~~**Generalize NdviTileLayer for multi-index support** (FEAT-002)~~ ✅ DONE
    - Added `indexType` prop to NdviTileLayer component
    - Added per-index color gradient scales (NDVI, NDWI, EVI, SAVI, NDRE, LAI)
    - NdviColorLegend now accepts `indexType` prop for dynamic legend display
    - Dynamic layer/source IDs per index type to support concurrent layers
25. ~~**Add index selector to Admin satellite page** (FEAT-003)~~ ✅ DONE
    - Added NDVI/SAVI/NDWI/NDRE/EVI tab switcher with icons
    - Stats card label and icon update dynamically based on selected index
    - Table header reflects selected index
26. ~~**Yemen-specific SAVI L parameter** (FEAT-004)~~ ✅ DONE
    - Added YEMEN_SAVI_L_PARAMS dict in sahool-eo/tasks/indices.py
    - 7 regions: Tihama (0.75), Southern Coast (0.70), Hadhramaut (0.65), Eastern Plateau (0.60), Socotra (0.55), Northern Highlands (0.45), Highlands (0.40)
    - SahoolSAVITask accepts `region` parameter for automatic L selection
27. ~~**NDWI water stress alerts in satellite dashboard** (FEAT-005)~~ ✅ DONE
    - Added water stress detection section (fields with NDWI < 0)
    - Displays affected field name, NDWI value, and irrigation recommendation
28. ~~**Fix admin api.ts TypeScript error in getTenantFromToken** (BUG-014)~~ ✅ DONE
    - Added non-null assertion for `parts[1]` in `atob()` call

---

## Checklist for Coding Agent

- [ ] Read this document completely
- [ ] Identify which bugs affect current task
- [ ] Check environment variables are set
- [ ] Verify Kong routes exist for target services
- [ ] Use correct (non-deprecated) service names
- [ ] Implement proper error handling (see BUG-004 pattern: always include `credentials: "same-origin"`)
- [ ] Add loading states to UI
- [ ] Test with services down to verify error handling
- [ ] Ensure `fetchDefaults` is spread in all fetch calls (admin app)
- [ ] Extract tenant_id from JWT, never hardcode (web app)
- [ ] Use AbortController in useEffect async operations
- [ ] Guard `window`/`navigator` access for SSR safety

---

**Document Maintainer:** SAHOOL Platform Team
**Last Updated:** 2026-03-18
