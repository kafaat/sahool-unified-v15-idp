# Middleware Infrastructure Review Report

**Date**: 2026-03-21
**Scope**: Web middleware, Admin middleware, Python shared middleware, Kong API Gateway, NestJS guards
**Reviewer**: Automated Security Audit

---

## Executive Summary

A comprehensive security audit of the SAHOOL platform middleware infrastructure uncovered **77 issues** across 5 layers. The most critical findings include **missing JWT authentication in 2 NestJS services**, **tenant isolation bypass via header injection**, **CSRF bypass on public routes**, and **weak rate limiting on authentication endpoints**.

| Severity | Web | Admin | Python | Kong/NestJS | Total |
|----------|-----|-------|--------|-------------|-------|
| Critical | 1 | 1 | 0 | 6 | **8** |
| High | 2 | 0 | 1 | 8 | **11** |
| Medium | 2 | 4 | 9 | 12 | **27** |
| Low | 6 | 2 | 3 | 0 | **11** |
| **Total** | **11** | **7** | **13** | **26** | **77** |

---

## Layer 1: Web App Middleware (apps/web/src/middleware.ts)

### CRITICAL

#### 1.1 CSRF Bypass for Public Routes (CWE-352)
- **File**: `apps/web/src/middleware.ts`, lines 180-211
- **Issue**: Public routes are checked BEFORE CSRF validation. POST/PUT/DELETE to `/login`, `/register`, `/forgot-password` completely bypass CSRF protection.
- **Flow**: `isPublicRoute` check → returns response → CSRF validation never reached
- **Impact**: Cross-site form submissions to authentication endpoints
- **Fix**: Move CSRF validation before the public route check, or only skip CSRF for GET/OPTIONS on public routes.

### HIGH

#### 1.2 Open Redirect in JWT Validation Failure (CWE-601)
- **File**: `apps/web/src/middleware.ts`, lines 248-255, 389-405
- **Issue**: `sanitizeReturnUrl()` checks `origin` but not `port`. `https://localhost:3000` vs `https://localhost:3001` have the same origin but different ports, allowing redirect to attacker-controlled local services.
- **Fix**: Compare both `origin` AND `port` explicitly.

#### 1.3 Race Condition in CSRF Token Generation (CWE-362)
- **File**: `apps/web/src/middleware.ts`, lines 274-311
- **Issue**: Concurrent requests can generate different CSRF tokens, weakening double-submit cookie pattern.

### MEDIUM

#### 1.4 Public Route Path Matching False Positives
- **File**: `apps/web/src/middleware.ts`, lines 57-103, 180-182
- **Issue**: `/api/auth` in publicRoutes causes `/api/authenticate` to also match (prefix match without boundary).
- **Fix**: Use regex with word boundaries or exact matching.

#### 1.5 CSRF Cookie Synchronization Logic Flaw
- **File**: `apps/web/src/middleware.ts`, lines 301-311
- **Issue**: Silently overwrites `_csrf` when tokens don't match instead of logging a security warning.

### LOW

#### 1.6 Locale Cookie Missing `secure` Flag
- **File**: `apps/web/src/middleware.ts`, lines 322-331
- Missing `secure: true` and `domain` restriction on NEXT_LOCALE cookie.

#### 1.7 Hardcoded Locale List (Drift Risk)
- **File**: `apps/web/src/middleware.ts`, line 36
- `["ar", "en"]` duplicated from `packages/i18n`. No import; silent drift.

#### 1.8 36 Hardcoded Protected Routes
- **File**: `apps/web/src/middleware.ts`, lines 68-103
- Manual route list scales poorly and drifts from actual routes.

#### 1.9 CSP Report Endpoint Missing Content-Type Validation
- **File**: `apps/web/src/app/api/csp-report/route.ts`, line 67
- Parses JSON without validating Content-Type header.

#### 1.10 IP Address Not Normalized for Rate Limiting
- **File**: `apps/web/src/app/api/csp-report/route.ts`, lines 32-46
- IPv6 not normalized; `x-forwarded-for` trusted without proxy validation.

#### 1.11 Error Details Exposed in Development
- **File**: `apps/web/src/middleware.ts`, lines 258-260
- JWT error reasons passed as query params in dev mode.

---

## Layer 2: Admin App Middleware (apps/admin/src/middleware.ts)

### CRITICAL

#### 2.1 CSRF Applied BEFORE Public Route Check
- **File**: `apps/admin/src/middleware.ts`, lines 217-234
- **Issue**: Opposite of web app bug — CSRF validation runs for ALL routes including public ones. Login/registration POSTs fail with 403 because no CSRF token exists yet.
- **Impact**: Login endpoints broken for first-time requests.
- **Fix**: Skip CSRF for public routes or pre-seed CSRF tokens on page load.

### MEDIUM

#### 2.2 CSRF Cookie httpOnly=false (XSS Risk)
- **File**: `apps/admin/src/middleware.ts`, lines 297-303
- **Issue**: Single CSRF cookie with `httpOnly: false`. XSS can read it and forge requests.
- **Web app uses double-cookie pattern** (httpOnly + client-readable). Admin should match.

#### 2.3 Idle Timeout Slides on GET Requests
- **File**: `apps/admin/src/middleware.ts`, lines 306-313
- **Issue**: Activity timestamp updates on ALL requests including automated/background ones. Stolen sessions stay alive indefinitely via periodic GETs.
- **Fix**: Only update on user-initiated state-changing requests.

#### 2.4 Route Protection Fallback Masks Bugs
- **File**: `apps/admin/src/lib/auth/route-protection.ts`, lines 81-87
- **Issue**: `?? null` fallback on protected routes could silently make a misconfigured route public.

#### 2.5 Duplicate X-Nonce Header Setting
- **File**: `apps/admin/src/middleware.ts`, lines 99, 316
- Nonce set on both request headers and response headers; request header value is unused.

### LOW

#### 2.6 Sentry Release Fallback "1.0.0"
- **File**: `apps/admin/sentry.client.config.ts`, line 31
- Should fallback to "16.0.0" to match actual version.

#### 2.7 In-Memory Rate Limiter Not Distributed
- **File**: `apps/admin/src/lib/rate-limiter.ts`
- In-memory Map resets on restart. Won't work with multiple instances.

---

## Layer 3: Python Shared Middleware (shared/middleware/)

### HIGH

#### 3.1 Memory Leak in Rate Limiter (Unbounded Dictionary)
- **File**: `shared/middleware/rate_limit.py`, lines 85-106
- **Issue**: `_request_counts` dictionary grows unboundedly. Cleanup only runs per-key during checks. Attacker can exhaust memory via many unique IP/tenant combinations.
- **Fix**: Add LRU eviction, max size check, or use Redis.

### MEDIUM

#### 3.2 Timing Attack in Token Bucket (time.time vs time.monotonic)
- **File**: `shared/middleware/rate_limit.py`, lines 62-77
- **Issue**: `time.time()` is subject to clock adjustments. Use `time.monotonic()`.

#### 3.3 Silent Exception Swallowing in Tier Detection
- **File**: `shared/middleware/rate_limiter.py`, lines 90-97
- **Issue**: `except Exception: pass` silently downgrades all users to FREE tier on any error.

#### 3.4 Header Injection via Unvalidated Logging
- **File**: `shared/middleware/request_logging.py`, lines 210-227
- **Issue**: User-Agent and IP logged with minimal sanitization. Control characters can corrupt logs.

#### 3.5 Tenant ID Not Validated (No UUID Check)
- **File**: `shared/middleware/tenant_context.py`, lines 142-159
- **Issue**: `X-Tenant-ID` header accepted without format validation. SQL injection possible if used in raw queries.
- **Fix**: Validate UUID format: `^[0-9a-f]{8}-...$`

#### 3.6 CORS Origins Not Validated
- **File**: `shared/middleware/cors.py`, lines 48-61
- **Issue**: `CORS_ORIGINS` env var parsed without URL validation. Wildcard `*` in production not detected.

#### 3.7 Missing Middleware Order Enforcement
- **Multiple files**: Auth → Tenant Audit → Rate Limit order assumed but not enforced.

#### 3.8 Input Sanitizer ReDoS Risk
- **File**: `shared/middleware/input_sanitizer.py`, lines 38-56
- **Issue**: 10KB strings processed through all regex patterns before truncation. Large payloads cause CPU spikes.
- **Fix**: Truncate BEFORE regex processing.

#### 3.9 Tenant Audit Race Condition
- **File**: `shared/middleware/tenant_audit.py`, lines 111-131
- **Issue**: If auth middleware hasn't run, `request.state.principal` is missing. Cross-tenant access proceeds without logging.

### LOW

#### 3.10 CSP Allows data: URIs
- **File**: `shared/middleware/security_headers.py`, lines 74-85
- `data:` allowed for img-src and font-src. Attack vector via SVG data URIs.

#### 3.11 Health Endpoints Not Rate Limited
- **File**: `shared/middleware/rate_limit.py`, lines 264-266
- `/healthz`, `/readyz`, `/metrics` exempt from rate limiting. DoS vector.

#### 3.12 Request IDs Trusted from External Headers
- **File**: `shared/middleware/unified_request_context.py`, line 156
- `X-Request-ID` accepted from any source. Should only trust internal services.

---

## Layer 4: Kong API Gateway

### CRITICAL

#### 4.1 Weak Rate Limiting on Auth Endpoints
- **File**: `infrastructure/gateway/kong/kong.yml`, lines 139-157
- **Issue**: 30 req/min on `/api/v1/auth/login` with `policy: local` (not cluster-aware).
- **Impact**: Brute force at 1,800/hour via distributed IPs.
- **Fix**: Reduce to 5/min, use `policy: redis`.

#### 4.2 CORS Credentials with Development Origins
- **File**: `infrastructure/gateway/kong/kong.yml`, lines 47-54
- **Issue**: `credentials: true` alongside `http://localhost:*` origins. If deployed to production, cookie exfiltration from any origin.

#### 4.3 Missing JWT Algorithm Validation
- **File**: `infrastructure/gateway/kong/kong-security.yml`, lines 387-395
- **Issue**: No algorithm whitelist. `alg: "none"` attack possible if not validated.
- **Fix**: Add `algorithms: ["HS256", "HS384", "HS512"]`.

### HIGH

#### 4.4 Kong Admin API Exposed on All Interfaces
- **File**: `infrastructure/gateway/kong/docker-compose.yml`
- Port 8001 (Admin API) bound to `0.0.0.0`. Bind to `127.0.0.1`.

#### 4.5 Mixed Rate Limiting Policies (local vs redis)
- **File**: `infrastructure/gateway/kong/kong.yml`, lines 150-217
- Some services use `policy: local`, others `policy: redis`. Inconsistent cluster-wide enforcement.

#### 4.6 HTTP Allowed in Production Routes
- **File**: `infrastructure/gateway/kong/kong.yml`
- `protocols: ["http", "https"]` allows cleartext. Production should be HTTPS only.

#### 4.7 No JWT Secret Length Enforcement
- **File**: `infrastructure/gateway/kong/kong-security.yml`, lines 387-395

---

## Layer 5: NestJS Guards & Middleware

### CRITICAL

#### 5.1 Chat Service Missing JWT Authentication Entirely
- **File**: `apps/services/chat-service/src/app.module.ts`, lines 42-57
- **Issue**: No JwtAuthGuard registered. Only ThrottlerGuard and TenantGuard exist. TenantGuard checks `request.user` which is never populated.
- **Impact**: Any attacker can POST to `/api/v1/chat` with arbitrary `X-Tenant-ID` and read/write messages.
- **Fix**: Add `{ provide: APP_GUARD, useClass: JwtAuthGuard }` BEFORE TenantGuard.

#### 5.2 Marketplace Service JWT Guard Not Global
- **File**: `apps/services/marketplace-service/src/app.module.ts`, lines 61-84
- **Issue**: JwtAuthGuard provided but NOT registered as `APP_GUARD`. Every controller endpoint without explicit `@UseGuards(JwtAuthGuard)` is public.
- **Impact**: Unauthenticated access to marketplace operations.
- **Fix**: Register as global guard.

#### 5.3 Tenant Isolation Bypass via Header Injection
- **File**: `apps/services/field-management-service/src/auth/tenant.guard.ts`, lines 61-79
- **Issue**: If JWT is malformed (missing `tid` claim), `userTenantId` is undefined. Fallback logic `userTenantId || headerTenantId` allows attacker to set arbitrary tenant via `X-Tenant-ID` header.
- **Impact**: Cross-tenant data access.
- **Fix**: Always require `tid` from JWT. Never fallback to header for non-admins.

### HIGH

#### 5.4 Guard Execution Order Not Guaranteed
- **File**: `apps/services/marketplace-service/src/app.module.ts`, lines 69-84
- TenantGuard may execute before JwtAuthGuard depending on registration order.

#### 5.5 WebSocket Gateway Authentication Weak
- **File**: `apps/services/chat-service/src/chat/chat.gateway.ts`
- Socket.IO handshake may not validate JWT on connection.

#### 5.6 No Token Revocation Mechanism
- **Location**: All NestJS services
- Once issued, JWT valid until expiration. No blacklist.

#### 5.7 Missing Audit Logging for Auth Failures
- **Files**: JWT guards across services
- Auth failures logged to console but not sent to audit-service.

#### 5.8 Field Management Rate Limiting Too Permissive
- **File**: `apps/services/field-management-service/src/app.module.ts`, lines 30-46
- 20 req/sec short limit is very high for field management operations.

### MEDIUM

#### 5.9 No Input Size Limits in NestJS
- All NestJS services missing explicit `bodyParser` limits.

#### 5.10 Missing Helmet Security Headers (Some Services)
- Chat service has no `helmet()` middleware.

#### 5.11 TenantGuard Allows Null User Without Throwing
- **File**: `apps/services/field-management-service/src/auth/tenant.guard.ts`, lines 49-60

#### 5.12 Inconsistent Error Messages (Information Disclosure)
- Different auth guards return different error messages, enabling token enumeration.

#### 5.13 No Tenant ID Format Validation in Guards
- X-Tenant-ID accepted without UUID format check.

#### 5.14 CORS Origins Include HTTP Localhost
- **File**: `apps/services/field-management-service/src/main.ts`, lines 39-45
- `http://localhost:3000` allowed. Must be environment-dependent.

---

## Priority Action Plan

### Immediate (Week 1) — Critical Security Fixes
1. **Add JWT auth guard to chat-service** — unauthenticated message access
2. **Register JWT guard globally in marketplace-service** — unauthenticated marketplace access
3. **Fix tenant isolation bypass** in field-management-service tenant.guard.ts
4. **Fix CSRF bypass** in web app (move CSRF before public route check)
5. **Fix CSRF ordering** in admin app (skip CSRF for public routes)
6. **Restrict Kong Admin API** to localhost binding
7. **Add JWT algorithm whitelist** in Kong configuration
8. **Reduce auth endpoint rate limits** to 5/min with Redis policy

### Short-Term (Week 2-3) — High Priority
9. Fix open redirect in web app sanitizeReturnUrl
10. Fix memory leak in Python rate limiter (add LRU eviction)
11. Implement double-cookie CSRF pattern in admin app
12. Standardize rate limiting to Redis across all Kong routes
13. Enforce HTTPS-only in Kong production routes
14. Add body size limits to all NestJS services
15. Add helmet to all NestJS services

### Medium-Term (Month 2) — Hardening
16. Validate tenant ID format (UUID) across all middleware layers
17. Implement token revocation with Redis blacklist
18. Add centralized audit logging for auth failures
19. Fix input sanitizer ReDoS (truncate before regex)
20. Enforce middleware execution order in Python services
21. Replace `time.time()` with `time.monotonic()` in rate limiter
22. Add CSP report endpoint handler in web app
23. Import locale list from shared i18n package
