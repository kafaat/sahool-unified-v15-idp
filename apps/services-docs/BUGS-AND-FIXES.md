# SAHOOL Platform - Bugs, Fixes, and Recommendations
# الأخطاء والإصلاحات والتوصيات

**Last Updated:** 2026-03-01
**Platform Version:** 16.0.0

---

## Table of Contents

1. [Critical Bugs](#critical-bugs)
2. [High Priority Fixes](#high-priority-fixes)
3. [Medium Priority Issues](#medium-priority-issues)
4. [Configuration Issues](#configuration-issues)
5. [Missing Features](#missing-features)
6. [Deprecated Services](#deprecated-services)
7. [Recommended Actions](#recommended-actions)

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

---

## Checklist for Coding Agent

- [ ] Read this document completely
- [ ] Identify which bugs affect current task
- [ ] Check environment variables are set
- [ ] Verify Kong routes exist for target services
- [ ] Use correct (non-deprecated) service names
- [ ] Implement proper error handling
- [ ] Add loading states to UI
- [ ] Test with services down to verify error handling

---

**Document Maintainer:** SAHOOL Platform Team
**Last Updated:** 2026-03-01
