# Web & Admin Frontend Code Review Summary
# ملخص مراجعة الواجهات الأمامية (ويب + إدارة)

**Date:** 2026-03-18
**Scope:** `apps/web/` and `apps/admin/` source code
**Branch:** `claude/review-web-admin-bugs-ks09r`

---

## Overview

Comprehensive code review of both frontend applications focusing on:
- Authentication and credential handling
- Multi-tenant isolation
- React hook correctness (memory leaks, stale closures, dependency arrays)
- Middleware error handling
- SSR safety

## Bugs Found and Fixed

### High Severity (3)

| ID | App | File | Issue |
|----|-----|------|-------|
| BUG-004 | Admin | `lib/api/services.ts`, `lib/api/extended-services.ts` | 20 fetch calls missing `credentials: "same-origin"` — auth cookies not sent |
| BUG-005 | Web | `lib/api/client.ts` | Weather API hardcoded `tenant_id: "default"` instead of extracting from JWT |
| BUG-006 | Web | `hooks/ai/useContextCompression.ts` | `decompress()` always applied RLE even for LOW/MEDIUM compression levels |

### Medium Severity (4)

| ID | App | File | Issue |
|----|-----|------|-------|
| BUG-007 | Admin | `hooks/api/use-api-query.ts` | No abort mechanism for in-flight requests on unmount |
| BUG-008 | Admin | `hooks/api/use-realtime.ts` | `events` array reference in useEffect deps caused re-subscriptions every render |
| BUG-009 | Web | `middleware.ts` | `validateJwtToken()` not wrapped in try-catch — unhandled exception crashes edge middleware |
| BUG-010 | Admin | `components/common/ErrorBoundary.tsx` | `window.location.href` and `navigator.userAgent` accessed without SSR guards |

## Files Modified (8 files, +81 -36)

```
apps/admin/src/lib/api/services.ts              (+6  -5)   # fetchDefaults added to 5 calls
apps/admin/src/lib/api/extended-services.ts      (+15 -8)   # fetchDefaults added to 15 calls
apps/admin/src/hooks/api/use-api-query.ts        (+16 -7)   # AbortController support
apps/admin/src/hooks/api/use-realtime.ts         (+11 -4)   # Stable eventsKey pattern
apps/admin/src/components/common/ErrorBoundary.tsx (+2  -2)  # SSR-safe window/navigator
apps/web/src/lib/api/client.ts                   (+6  -3)   # JWT tenant extraction
apps/web/src/hooks/ai/useContextCompression.ts   (+14 -6)   # Safe decompression
apps/web/src/middleware.ts                       (+11 -1)    # JWT try-catch
```

## Test Results

| App | Tests | Status |
|-----|-------|--------|
| Admin | 1032/1032 | All passing |
| Web | 1236/1236 | All passing |
| TypeScript (Admin) | 0 errors | Clean |
| TypeScript (Web) | 0 errors | Clean |

## Key Patterns Established

### 1. Always include credentials in fetch calls (Admin)
```typescript
const fetchDefaults: RequestInit = { credentials: "same-origin" };

// Every fetch call MUST spread fetchDefaults:
const response = await fetch(url, { ...fetchDefaults, method: "GET" });
```

### 2. Extract tenant from JWT, never hardcode (Web)
```typescript
const tenantId = this.token ? this.extractTenantFromToken(this.token) : null;
body: JSON.stringify({ tenant_id: tenantId || "default" });
```

### 3. Use AbortController for async effects
```typescript
useEffect(() => {
  const controller = new AbortController();
  fetchData(controller.signal);
  return () => controller.abort();
}, [deps]);
```

### 4. Use stable keys for array dependencies
```typescript
const eventsRef = useRef(events);
eventsRef.current = events;
const eventsKey = events.join(",");  // Stable string key

useEffect(() => { /* use eventsRef.current */ }, [eventsKey]);
```

### 5. Guard window/navigator for SSR
```typescript
const url = typeof window !== "undefined" ? window.location.href : "unknown";
```

## Documentation Updated

- `apps/services-docs/BUGS-AND-FIXES.md` — Added BUG-004 through BUG-010
- `CHANGELOG.md` — Added Unreleased > Fixed entry
- `docs/summaries/WEB_ADMIN_REVIEW_SUMMARY.md` — This file

---

**Commits:**
- `7357c39` — fix(web,admin): fix auth credentials, tenant isolation, and React hook bugs
- `d20abd6` — fix(admin): guard window/navigator access in ErrorBoundary.logErrorToServer
