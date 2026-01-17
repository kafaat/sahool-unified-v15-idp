# SAHOOL Admin Middleware Security Audit Report

**Date:** 2026-01-06
**Auditor:** Security Analysis System
**Middleware File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/middleware.ts`
**Related Files Reviewed:** CSP Config, Auth Store, Auth Guard, API Routes

---

## Executive Summary

The SAHOOL Admin middleware implements basic authentication and strong security headers, but lacks several critical security features for production admin panels. The middleware provides good protection against XSS and injection attacks through CSP, but has gaps in authorization, rate limiting, CSRF protection, and audit logging.

**Overall Security Rating:** 6.5/10

---

## 1. Authentication Middleware ✅ GOOD

### Current Implementation

**File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/middleware.ts` (Lines 42-49)

```typescript
// Check for auth token
const token = request.cookies.get("sahool_admin_token")?.value;

if (!token) {
  // Redirect to login with return URL
  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("returnTo", pathname);
  return NextResponse.redirect(loginUrl);
}
```

### Strengths

1. **HttpOnly Cookie Storage**: Tokens stored in httpOnly cookies (set in `/app/api/auth/login/route.ts`)
2. **Automatic Redirect**: Missing tokens trigger redirect to login with return URL
3. **Public Routes Whitelist**: Properly exempts `/login` and `/api/auth` routes
4. **Static Files Exception**: Correctly allows `/_next`, `/static`, and files with extensions

### Weaknesses

1. **No Token Validation**: Middleware only checks if token exists, doesn't validate JWT structure or signature
2. **No Token Expiry Check**: Expired tokens are not detected until backend API call fails
3. **No Token Refresh Logic**: Token refresh happens client-side only (auth.store.tsx)

### Recommendations

- **HIGH PRIORITY**: Add JWT validation to check token structure and expiry in middleware
- **MEDIUM**: Implement automatic token refresh in middleware when token is close to expiry
- **LOW**: Add token signature verification for critical admin routes

---

## 2. Authorization & Role Checks ❌ CRITICAL GAP

### Current Implementation

**Authorization is NOT enforced in middleware.**

Role checks exist only in client-side components:

- **File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/components/auth/AuthGuard.tsx` (Lines 18-22, 40-51)

```typescript
const roleHierarchy: Record<"admin" | "supervisor" | "viewer", number> = {
  admin: 3,
  supervisor: 2,
  viewer: 1,
};

// Check role-based access (client-side only)
if (userRoleLevel < requiredRoleLevel) {
  router.push("/dashboard");
}
```

### Critical Issues

1. **NO SERVER-SIDE AUTHORIZATION**: Middleware does not check user roles at all
2. **CLIENT-SIDE ONLY**: AuthGuard can be bypassed by direct API calls
3. **NO ROUTE-TO-ROLE MAPPING**: No configuration mapping admin routes to required roles
4. **MISSING API PROTECTION**: API routes under `/api/` have no role checks

### Security Risks

- **SEVERITY: CRITICAL** - Any authenticated user (even 'viewer' role) can access admin-only routes by:
  - Making direct API calls
  - Bypassing client-side router guards
  - Manipulating URL navigation

### Recommendations

1. **CRITICAL - IMMEDIATE ACTION REQUIRED**:

   ```typescript
   // Add to middleware.ts
   const roleProtectedRoutes = {
     "/settings": ["admin"],
     "/users": ["admin", "supervisor"],
     "/api/admin": ["admin"],
   };

   // Decode JWT token to get user role
   const userRole = decodeTokenRole(token);

   // Check if route requires specific role
   if (!hasRequiredRole(pathname, userRole, roleProtectedRoutes)) {
     return NextResponse.redirect(new URL("/unauthorized", request.url));
   }
   ```

2. **HIGH PRIORITY**: Create middleware wrapper for API routes to check roles
3. **HIGH PRIORITY**: Implement server-side role validation for all protected endpoints

---

## 3. Security Headers ✅ EXCELLENT

### Current Implementation

**File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/middleware.ts` (Lines 82-101)

```typescript
// Add security headers
response.headers.set("X-Frame-Options", "DENY");
response.headers.set("X-Content-Type-Options", "nosniff");
response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
response.headers.set("X-XSS-Protection", "1; mode=block");

// HSTS - only in production with HTTPS
if (process.env.NODE_ENV === "production") {
  response.headers.set(
    "Strict-Transport-Security",
    "max-age=31536000; includeSubDomains",
  );
}

// Content Security Policy with nonce-based security
const cspConfig = getCSPConfig(nonce);
const cspHeader = getCSPHeader(nonce);
response.headers.set(cspHeaderName, cspHeader);
```

### Strengths

1. **Comprehensive CSP**: Strong Content Security Policy implementation
   - Nonce-based script execution
   - Strict-dynamic in production
   - Blocks unsafe-inline and unsafe-eval (except dev)
   - Report-URI for violation monitoring

2. **Clickjacking Protection**:
   - X-Frame-Options: DENY
   - CSP frame-ancestors: 'none'

3. **MIME Sniffing Prevention**: X-Content-Type-Options: nosniff

4. **HSTS in Production**: 1-year max-age with includeSubDomains

5. **XSS Protection**: X-XSS-Protection header (defense in depth)

6. **Secure Referrer Policy**: strict-origin-when-cross-origin

### CSP Configuration Analysis

**File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/lib/security/csp-config.ts`

**Excellent Features:**

- Cryptographically secure nonce generation using Web Crypto API
- Environment-aware directives (strict in production, relaxed in dev)
- Upgrade insecure requests in production
- Block mixed content in production
- Proper external domain whitelisting (Google Fonts, OpenStreetMap)
- CSP violation reporting endpoint

**Minor Improvements:**

- Consider adding `Permissions-Policy` header to control browser features
- Add `X-Permitted-Cross-Domain-Policies: none` for Adobe products

### Recommendations

- **LOW PRIORITY**: Add Permissions-Policy header:
  ```typescript
  response.headers.set(
    "Permissions-Policy",
    "geolocation=(), microphone=(), camera=(), payment=()",
  );
  ```

---

## 4. Session Handling ✅ GOOD

### Current Implementation

**Idle Timeout in Middleware:**
**File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/middleware.ts` (Lines 51-71)

```typescript
// Idle timeout: 30 minutes
const IDLE_TIMEOUT = 30 * 60 * 1000;

const lastActivityStr = request.cookies.get(
  "sahool_admin_last_activity",
)?.value;
if (lastActivityStr) {
  const lastActivity = parseInt(lastActivityStr, 10);
  const now = Date.now();
  const timeSinceLastActivity = now - lastActivity;

  if (timeSinceLastActivity >= IDLE_TIMEOUT) {
    // Session expired - clear cookies and redirect
    const response = NextResponse.redirect(loginUrl);
    response.cookies.delete("sahool_admin_token");
    response.cookies.delete("sahool_admin_refresh_token");
    response.cookies.delete("sahool_admin_last_activity");
    return response;
  }
}
```

**Client-Side Activity Tracking:**
**File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/stores/auth.store.tsx` (Lines 31-36, 99-112)

```typescript
const IDLE_TIMEOUT = 30 * 60 * 1000;
const REFRESH_CHECK_INTERVAL = 5 * 60 * 1000;
const ACTIVITY_UPDATE_INTERVAL = 30 * 1000;

// Track user activity
const events = ["mousedown", "keydown", "scroll", "touchstart", "click"];
```

### Strengths

1. **Idle Timeout Enforcement**: 30-minute server-side timeout
2. **Activity Tracking**: Client monitors user interactions and updates server
3. **Automatic Cookie Cleanup**: Expired sessions clear all auth cookies
4. **Token Refresh**: Automatic refresh every 5 minutes
5. **Secure Cookie Settings**:
   - httpOnly: true
   - sameSite: 'strict'
   - secure: true (production)
   - Proper maxAge settings (1 day access, 7 days refresh)

### Weaknesses

1. **NO ABSOLUTE SESSION LIMIT**: Sessions can last indefinitely with activity
2. **NO CONCURRENT SESSION CONTROL**: Users can have unlimited simultaneous sessions
3. **MISSING SESSION STORAGE**: No server-side session tracking/revocation
4. **NO SESSION FINGERPRINTING**: Sessions not bound to device/browser characteristics

### Security Risks

- **MEDIUM**: Stolen refresh tokens can maintain persistent access
- **MEDIUM**: No way to remotely terminate compromised sessions
- **LOW**: Session fixation attacks possible (though mitigated by httpOnly cookies)

### Recommendations

1. **HIGH PRIORITY**: Add absolute session limit (e.g., 24 hours regardless of activity)

   ```typescript
   const SESSION_ABSOLUTE_LIMIT = 24 * 60 * 60 * 1000; // 24 hours
   const sessionStartStr = request.cookies.get(
     "sahool_admin_session_start",
   )?.value;
   ```

2. **HIGH PRIORITY**: Implement server-side session store (Redis) for revocation capability

3. **MEDIUM**: Add concurrent session limiting (max 3 devices per user)

4. **MEDIUM**: Implement session fingerprinting (IP + User-Agent hashing)

5. **LOW**: Add session activity logging for security monitoring

---

## 5. CSRF Protection ⚠️ PARTIAL

### Current Implementation

**Relies solely on SameSite cookies:**
**File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/app/api/auth/login/route.ts` (Lines 50-56)

```typescript
cookieStore.set("sahool_admin_token", data.access_token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "strict", // ← CSRF protection
  maxAge: 86400,
  path: "/",
});
```

### Current Protection Level

1. **SameSite=Strict**: Cookies not sent with cross-site requests
2. **HttpOnly**: Prevents JavaScript access to tokens
3. **CORS Implicit**: No explicit CORS configuration found

### Issues

1. **NO CSRF TOKENS**: No explicit CSRF token validation for state-changing operations
2. **NO DOUBLE-SUBMIT COOKIES**: Missing additional CSRF defense layer
3. **SAMSITE ONLY**: Relies on single protection mechanism
4. **NO ORIGIN VALIDATION**: Origin/Referer headers not checked
5. **API ROUTES UNPROTECTED**: No CSRF tokens for POST/PUT/DELETE to `/api/*`

### Security Risks

- **SEVERITY: MEDIUM-HIGH** - SameSite=Strict is good but:
  - May not work in all browsers/contexts
  - Broken by user navigation patterns
  - Not defense-in-depth
  - No protection for logged-in CSRF scenarios

### Attack Scenarios

```html
<!-- Attacker site could potentially: -->
<form action="https://admin.sahool.io/api/users/delete" method="POST">
  <input name="user_id" value="victim123" />
</form>
<script>
  document.forms[0].submit();
</script>
```

Currently blocked by SameSite, but should have additional protection.

### Recommendations

1. **HIGH PRIORITY**: Implement CSRF token generation in middleware:

   ```typescript
   // Generate CSRF token
   const csrfToken = generateCsrfToken();
   response.cookies.set("sahool_csrf_token", csrfToken, {
     httpOnly: false, // Needs to be readable by JS
     sameSite: "strict",
     secure: true,
   });
   response.headers.set("X-CSRF-Token", csrfToken);
   ```

2. **HIGH PRIORITY**: Validate CSRF tokens in API routes:

   ```typescript
   // In each POST/PUT/DELETE API route
   const csrfToken = request.headers.get("X-CSRF-Token");
   const csrfCookie = request.cookies.get("sahool_csrf_token")?.value;

   if (csrfToken !== csrfCookie) {
     return NextResponse.json(
       { error: "CSRF token mismatch" },
       { status: 403 },
     );
   }
   ```

3. **MEDIUM**: Add Origin/Referer header validation:

   ```typescript
   const origin = request.headers.get("origin");
   const referer = request.headers.get("referer");
   if (!isValidOrigin(origin, referer)) {
     return NextResponse.json({ error: "Invalid origin" }, { status: 403 });
   }
   ```

4. **MEDIUM**: Add CORS configuration with explicit allowed origins

---

## 6. Rate Limiting ❌ NOT IMPLEMENTED

### Current State

**NO RATE LIMITING EXISTS** in the middleware or API routes.

### Files Checked

- `/home/user/sahool-unified-v15-idp/apps/admin/src/middleware.ts` - No rate limiting
- `/home/user/sahool-unified-v15-idp/apps/admin/src/app/api/auth/login/route.ts` - No rate limiting
- No rate limiting library dependencies found

### Security Risks

**SEVERITY: HIGH** - Without rate limiting, the admin panel is vulnerable to:

1. **Brute Force Attacks**: Unlimited login attempts possible
2. **DoS/DDoS**: No protection against request flooding
3. **Credential Stuffing**: Automated attacks can test many credentials
4. **API Abuse**: No limits on API endpoint calls
5. **Resource Exhaustion**: Backend can be overwhelmed

### Attack Scenarios

```bash
# Attacker can brute force admin login:
for password in $(cat wordlist.txt); do
  curl -X POST https://admin.sahool.io/api/auth/login \
    -d "{\"email\":\"admin@sahool.io\",\"password\":\"$password\"}"
done
# No rate limit = unlimited attempts
```

### Recommendations

1. **CRITICAL - IMMEDIATE ACTION REQUIRED**: Implement rate limiting middleware using Redis or memory store

   **Option A - Use Upstash Rate Limit (Recommended):**

   ```typescript
   import { Ratelimit } from "@upstash/ratelimit";
   import { Redis } from "@upstash/redis";

   const ratelimit = new Ratelimit({
     redis: Redis.fromEnv(),
     limiter: Ratelimit.slidingWindow(10, "10 s"),
     analytics: true,
   });

   // In middleware
   const identifier =
     request.ip ?? request.headers.get("x-forwarded-for") ?? "anonymous";
   const { success, limit, reset, remaining } =
     await ratelimit.limit(identifier);

   if (!success) {
     return new NextResponse("Too Many Requests", {
       status: 429,
       headers: {
         "X-RateLimit-Limit": limit.toString(),
         "X-RateLimit-Remaining": remaining.toString(),
         "X-RateLimit-Reset": reset.toString(),
       },
     });
   }
   ```

   **Option B - In-Memory Rate Limiting (for testing/dev):**

   ```typescript
   import rateLimit from "express-rate-limit";
   // Note: Doesn't work across multiple instances
   ```

2. **CRITICAL**: Implement stricter rate limits for auth endpoints:
   - Login: 5 attempts per 15 minutes per IP
   - Password reset: 3 attempts per hour per email
   - Token refresh: 10 attempts per minute per token

3. **HIGH PRIORITY**: Add progressive delays after failed login attempts:

   ```typescript
   // Implement exponential backoff
   const failedAttempts = await getFailedLoginAttempts(email);
   if (failedAttempts > 0) {
     const delay = Math.min(1000 * Math.pow(2, failedAttempts - 1), 30000);
     await sleep(delay);
   }
   ```

4. **HIGH PRIORITY**: Add IP-based blocking after repeated violations:
   - Temporary block after 20 failed attempts (1 hour)
   - Permanent block after persistent abuse (requires manual review)

5. **MEDIUM**: Implement CAPTCHA after N failed login attempts

6. **MEDIUM**: Add rate limiting headers to all responses:
   ```
   X-RateLimit-Limit: 100
   X-RateLimit-Remaining: 87
   X-RateLimit-Reset: 1641024000
   ```

---

## 7. Admin-Specific Protections ⚠️ INSUFFICIENT

### Current Implementation

**Client-Side Role Guards:**
**File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/components/auth/AuthGuard.tsx`

```typescript
const roleHierarchy = { admin: 3, supervisor: 2, viewer: 1 };

// Client-side check only
if (userRoleLevel < requiredRoleLevel) {
  router.push("/dashboard");
}
```

**Role Types:**
**File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/lib/auth.ts` (Line 30)

```typescript
role: "admin" | "supervisor" | "viewer";
```

### Current Protections

1. **Role Hierarchy**: Three-tier role system (admin > supervisor > viewer)
2. **Client-Side Guards**: AuthGuard component for route protection
3. **HttpOnly Cookies**: Prevents client-side token theft

### Critical Gaps

1. **NO SERVER-SIDE ROLE ENFORCEMENT**: All role checks are client-side only
2. **NO PERMISSION SYSTEM**: No granular permissions beyond roles
3. **NO ADMIN ACTION LOGGING**: Critical admin actions not logged
4. **NO MULTI-FACTOR AUTH REQUIREMENT**: MFA not enforced for admin role
5. **NO ADMIN IP WHITELISTING**: No network-level admin access control
6. **NO SUDO MODE**: No re-authentication for critical actions
7. **NO SESSION ELEVATION**: No temporary permission elevation mechanism

### Security Risks

**SEVERITY: CRITICAL** - Current implementation allows:

1. **Authorization Bypass**: Direct API calls bypass client-side role checks
2. **Privilege Escalation**: No server validation of role changes
3. **No Audit Trail**: Admin actions not tracked for compliance/forensics
4. **Account Compromise**: No MFA requirement for high-privilege accounts
5. **No Recovery**: Stolen admin tokens have full, unlimited access

### Recommendations

1. **CRITICAL - Server-Side Role Middleware**:

   ```typescript
   // Create /lib/middleware/requireRole.ts
   export function requireRole(allowedRoles: string[]) {
     return async (request: NextRequest) => {
       const token = request.cookies.get("sahool_admin_token")?.value;
       const payload = await verifyJWT(token);

       if (!allowedRoles.includes(payload.role)) {
         return NextResponse.json(
           { error: "Insufficient permissions" },
           { status: 403 },
         );
       }

       return null; // Allow request
     };
   }
   ```

2. **CRITICAL - Route-to-Role Mapping**:

   ```typescript
   const protectedRoutes = {
     "/settings": ["admin"],
     "/settings/security": ["admin"],
     "/users": ["admin", "supervisor"],
     "/farms": ["admin", "supervisor", "viewer"],
     "/api/users": ["admin"],
     "/api/settings": ["admin"],
   };
   ```

3. **HIGH PRIORITY - Enforce MFA for Admin Role**:

   ```typescript
   // In middleware after token check
   if (userRole === "admin" && !hasMFAVerified(token)) {
     return NextResponse.redirect(new URL("/verify-mfa", request.url));
   }
   ```

4. **HIGH PRIORITY - Implement Sudo Mode**:

   ```typescript
   // For critical actions (delete user, change settings)
   if (isCriticalAction && !recentlyReauthenticated(session)) {
     return { requiresReauth: true };
   }
   ```

5. **MEDIUM - Admin IP Whitelist**:

   ```typescript
   if (userRole === "admin") {
     const ip = request.ip ?? request.headers.get("x-forwarded-for");
     if (!isWhitelistedIP(ip)) {
       await sendAlertEmail(user, ip);
       return NextResponse.json(
         { error: "Admin access from unauthorized IP" },
         { status: 403 },
       );
     }
   }
   ```

6. **MEDIUM - Time-Based Access Control**:

   ```typescript
   // Restrict admin access to business hours
   if (userRole === "admin" && !isBusinessHours()) {
     await sendAlertEmail(user, "Off-hours access attempt");
     // Optionally require additional verification
   }
   ```

7. **LOW - Admin Dashboard Watermark**: Add visible username/IP to prevent shoulder surfing

---

## 8. Audit Logging ❌ INSUFFICIENT

### Current Implementation

**Basic Console Logging Only:**
**File:** `/home/user/sahool-unified-v15-idp/apps/admin/src/lib/logger.ts`

```typescript
export const logger = {
  log: (...args: any[]) => {
    if (isDev) console.log(...args);
  },
  error: (...args: any[]) => {
    if (isDev) console.error(...args);
  },
  critical: (...args: any[]) => {
    console.error(...args);
  },
};
```

**No Structured Logging:**

- No timestamp standardization
- No request context
- No user identification
- No action categorization

### What Gets Logged

**Login Errors:**

```typescript
// /app/api/auth/login/route.ts
console.error("Login error:", error);
```

**Logout Errors:**

```typescript
// /app/api/auth/logout/route.ts
console.error("Logout error:", error);
```

**Token Refresh Errors:**

```typescript
// /app/api/auth/refresh/route.ts
console.error("Token refresh error:", error);
```

### Critical Gaps

1. **NO AUDIT TRAIL**: No persistent storage of security events
2. **NO AUTHENTICATION LOGGING**: Login success/failure not logged with context
3. **NO AUTHORIZATION LOGGING**: Access denial/grant not logged
4. **NO ADMIN ACTION LOGGING**: No record of admin operations (create, update, delete)
5. **NO DATA ACCESS LOGGING**: No tracking of sensitive data views
6. **NO SECURITY EVENT LOGGING**: No alerts for:
   - Multiple failed logins
   - Session hijacking attempts
   - Role escalation attempts
   - Unusual access patterns
7. **NO COMPLIANCE LOGGING**: Insufficient for GDPR, HIPAA, SOC2 requirements
8. **NO LOG ROTATION**: No log management strategy
9. **NO LOG ANALYSIS**: No automated threat detection

### Security & Compliance Risks

**SEVERITY: HIGH** - Lack of audit logging means:

1. **No Forensic Capability**: Cannot investigate security incidents
2. **No Compliance**: Fails regulatory requirements (GDPR Article 30, HIPAA §164.312)
3. **No Accountability**: Cannot trace who did what when
4. **No Threat Detection**: Cannot identify attack patterns
5. **No Incident Response**: Cannot determine breach scope

### What Should Be Logged

**Authentication Events:**

- Login attempts (success/failure) with IP, timestamp, user-agent
- Logout events
- Token refresh attempts
- MFA verification attempts
- Password reset requests
- Session timeout/expiry

**Authorization Events:**

- Access denied events (insufficient role)
- Role changes
- Permission grants/revokes
- Protected resource access

**Admin Actions:**

- User creation/modification/deletion
- Settings changes
- Role assignments
- System configuration changes
- Data exports
- Bulk operations

**Security Events:**

- Multiple failed login attempts
- Login from new location/device
- Unusual access patterns
- API rate limit violations
- CSRF token mismatches
- Invalid JWT signatures
- Session anomalies

### Recommendations

1. **CRITICAL - Implement Structured Audit Logging**:

   ```typescript
   // Create /lib/audit/audit-logger.ts
   import { createClient } from "@supabase/supabase-js";

   interface AuditLogEntry {
     timestamp: string;
     event_type: "AUTH" | "AUTHZ" | "ADMIN_ACTION" | "SECURITY" | "DATA_ACCESS";
     event_name: string;
     user_id?: string;
     user_email?: string;
     user_role?: string;
     ip_address: string;
     user_agent: string;
     path: string;
     method: string;
     status_code: number;
     request_id: string;
     session_id?: string;
     resource_type?: string;
     resource_id?: string;
     action?: string;
     result: "SUCCESS" | "FAILURE" | "DENIED";
     error_message?: string;
     metadata?: Record<string, any>;
   }

   export class AuditLogger {
     private db: any; // Supabase, Prisma, or other DB client

     async log(entry: AuditLogEntry) {
       await this.db.from("audit_logs").insert({
         ...entry,
         timestamp: new Date().toISOString(),
       });
     }

     async logAuth(
       event: string,
       request: NextRequest,
       result: string,
       error?: string,
     ) {
       await this.log({
         event_type: "AUTH",
         event_name: event,
         ip_address: request.ip ?? "unknown",
         user_agent: request.headers.get("user-agent") ?? "unknown",
         path: request.nextUrl.pathname,
         method: request.method,
         result: result as any,
         error_message: error,
       });
     }

     async logAdminAction(
       action: string,
       user: User,
       request: NextRequest,
       resourceType: string,
       resourceId: string,
       result: string,
     ) {
       await this.log({
         event_type: "ADMIN_ACTION",
         event_name: action,
         user_id: user.id,
         user_email: user.email,
         user_role: user.role,
         ip_address: request.ip ?? "unknown",
         user_agent: request.headers.get("user-agent") ?? "unknown",
         path: request.nextUrl.pathname,
         method: request.method,
         resource_type: resourceType,
         resource_id: resourceId,
         action: action,
         result: result as any,
       });
     }
   }
   ```

2. **CRITICAL - Log Authentication Events in Middleware**:

   ```typescript
   // In middleware.ts
   const auditLogger = new AuditLogger();

   // Log auth check
   if (!token) {
     await auditLogger.logAuth("AUTH_TOKEN_MISSING", request, "FAILURE");
     return NextResponse.redirect(loginUrl);
   }

   // Log idle timeout
   if (timeSinceLastActivity >= IDLE_TIMEOUT) {
     await auditLogger.logAuth("AUTH_IDLE_TIMEOUT", request, "FAILURE");
     return response;
   }
   ```

3. **HIGH PRIORITY - Log All Login Attempts**:

   ```typescript
   // In /app/api/auth/login/route.ts
   const auditLogger = new AuditLogger();

   // Before login attempt
   await auditLogger.log({
     event_type: "AUTH",
     event_name: "LOGIN_ATTEMPT",
     user_email: email,
     ip_address: request.ip ?? "unknown",
     user_agent: request.headers.get("user-agent") ?? "unknown",
     result: "PENDING",
   });

   // After successful login
   await auditLogger.log({
     event_type: "AUTH",
     event_name: "LOGIN_SUCCESS",
     user_id: data.user.id,
     user_email: email,
     user_role: data.user.role,
     ip_address: request.ip ?? "unknown",
     result: "SUCCESS",
   });

   // After failed login
   await auditLogger.log({
     event_type: "AUTH",
     event_name: "LOGIN_FAILURE",
     user_email: email,
     result: "FAILURE",
     error_message: error.message,
   });
   ```

4. **HIGH PRIORITY - Create Audit Log Database Schema**:

   ```sql
   CREATE TABLE audit_logs (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
     event_type VARCHAR(50) NOT NULL,
     event_name VARCHAR(100) NOT NULL,
     user_id UUID,
     user_email VARCHAR(255),
     user_role VARCHAR(50),
     ip_address VARCHAR(45) NOT NULL,
     user_agent TEXT,
     path VARCHAR(255) NOT NULL,
     method VARCHAR(10) NOT NULL,
     status_code INTEGER,
     request_id VARCHAR(100),
     session_id VARCHAR(100),
     resource_type VARCHAR(100),
     resource_id VARCHAR(255),
     action VARCHAR(100),
     result VARCHAR(20) NOT NULL,
     error_message TEXT,
     metadata JSONB,

     -- Indexes for query performance
     INDEX idx_timestamp (timestamp),
     INDEX idx_event_type (event_type),
     INDEX idx_user_id (user_id),
     INDEX idx_user_email (user_email),
     INDEX idx_ip_address (ip_address),
     INDEX idx_result (result)
   );

   -- Retention policy: keep logs for 2 years for compliance
   -- Implement partitioning by month for performance
   ```

5. **HIGH PRIORITY - Log Authorization Decisions**:

   ```typescript
   // When checking roles
   if (userRoleLevel < requiredRoleLevel) {
     await auditLogger.log({
       event_type: "AUTHZ",
       event_name: "ACCESS_DENIED",
       user_id: user.id,
       user_role: user.role,
       path: pathname,
       result: "DENIED",
       metadata: {
         required_role: requiredRole,
         user_role: user.role,
       },
     });
   }
   ```

6. **MEDIUM - Implement Real-Time Security Alerts**:

   ```typescript
   // Create /lib/audit/alert-monitor.ts
   export class SecurityAlertMonitor {
     async checkForThreats() {
       // Multiple failed logins from same IP
       const failedLogins = await db.query(`
         SELECT ip_address, COUNT(*) as count
         FROM audit_logs
         WHERE event_name = 'LOGIN_FAILURE'
           AND timestamp > NOW() - INTERVAL '15 minutes'
         GROUP BY ip_address
         HAVING COUNT(*) >= 5
       `);

       for (const { ip_address, count } of failedLogins) {
         await sendAlert({
           type: "BRUTE_FORCE_DETECTED",
           ip_address,
           attempt_count: count,
         });
       }

       // Admin access from new location
       // Session hijacking indicators
       // Unusual data access patterns
       // etc.
     }
   }
   ```

7. **MEDIUM - Add Audit Log API for Viewing**:

   ```typescript
   // Create /app/api/audit-logs/route.ts
   export async function GET(request: NextRequest) {
     // Require admin role
     const user = await getCurrentUser(request);
     if (user.role !== "admin") {
       return NextResponse.json({ error: "Forbidden" }, { status: 403 });
     }

     const { searchParams } = request.nextUrl;
     const logs = await db
       .from("audit_logs")
       .select("*")
       .order("timestamp", { ascending: false })
       .limit(100);

     return NextResponse.json({ logs });
   }
   ```

8. **LOW - Log Export for Compliance**:
   - Implement audit log export to immutable storage (S3 with versioning)
   - Generate monthly compliance reports
   - Provide log search and filtering UI for admins

---

## Summary of Findings

### Critical Issues (Require Immediate Attention)

| Issue                                             | Severity    | Priority  | File(s) Affected           |
| ------------------------------------------------- | ----------- | --------- | -------------------------- |
| No server-side role authorization                 | CRITICAL    | IMMEDIATE | middleware.ts, API routes  |
| No rate limiting on any endpoints                 | HIGH        | IMMEDIATE | middleware.ts, auth routes |
| Insufficient CSRF protection                      | MEDIUM-HIGH | HIGH      | middleware.ts, API routes  |
| No audit logging for security events              | HIGH        | HIGH      | All files                  |
| No admin-specific protections (MFA, IP whitelist) | HIGH        | HIGH      | middleware.ts, auth routes |

### Good Implementations (Keep)

| Feature                                       | Status | Quality   |
| --------------------------------------------- | ------ | --------- |
| Security Headers (CSP, HSTS, X-Frame-Options) | ✅     | EXCELLENT |
| HttpOnly Cookie Storage                       | ✅     | GOOD      |
| Idle Timeout (30 minutes)                     | ✅     | GOOD      |
| Activity Tracking                             | ✅     | GOOD      |
| Nonce-based CSP                               | ✅     | EXCELLENT |

### Medium Priority Issues

| Issue                            | Impact | Effort |
| -------------------------------- | ------ | ------ |
| No absolute session limit        | Medium | Low    |
| No session revocation capability | Medium | High   |
| Client-only role checks          | High   | Medium |
| No JWT validation in middleware  | Medium | Medium |

---

## Recommended Implementation Roadmap

### Phase 1: Critical Security Fixes (Week 1)

1. **Day 1-2**: Implement server-side role authorization in middleware
2. **Day 2-3**: Add rate limiting to all endpoints (especially auth)
3. **Day 3-4**: Implement CSRF token validation
4. **Day 4-5**: Set up audit logging infrastructure

### Phase 2: Admin Protections (Week 2)

1. **Day 6-7**: Enforce MFA for admin role
2. **Day 7-8**: Add admin IP whitelisting
3. **Day 8-9**: Implement sudo mode for critical actions
4. **Day 9-10**: Add JWT validation in middleware

### Phase 3: Monitoring & Alerting (Week 3)

1. **Day 11-12**: Build audit log viewing UI
2. **Day 12-13**: Implement security alert monitoring
3. **Day 13-14**: Add real-time threat detection
4. **Day 14-15**: Set up compliance reporting

### Phase 4: Advanced Features (Week 4)

1. Concurrent session management
2. Session fingerprinting
3. Absolute session limits
4. Time-based access controls
5. Automated incident response

---

## Code Snippets: Quick Wins

### 1. Add Role Check to Middleware (30 minutes)

```typescript
// In middleware.ts
import { verify } from "jsonwebtoken";

const PROTECTED_ROUTES = {
  "/settings": ["admin"],
  "/users": ["admin", "supervisor"],
  "/farms": ["admin", "supervisor", "viewer"],
};

// After token check
try {
  const decoded = verify(token, process.env.JWT_SECRET!) as { role: string };
  const requiredRoles = getRequiredRoles(pathname, PROTECTED_ROUTES);

  if (requiredRoles && !requiredRoles.includes(decoded.role)) {
    return NextResponse.redirect(new URL("/unauthorized", request.url));
  }
} catch (err) {
  // Invalid token
  return NextResponse.redirect(loginUrl);
}
```

### 2. Add Basic Rate Limiting (1 hour)

```typescript
// Create /lib/rate-limit.ts
const rateLimitMap = new Map<string, { count: number; resetTime: number }>();

export function checkRateLimit(
  identifier: string,
  limit: number,
  windowMs: number,
): boolean {
  const now = Date.now();
  const record = rateLimitMap.get(identifier);

  if (!record || now > record.resetTime) {
    rateLimitMap.set(identifier, { count: 1, resetTime: now + windowMs });
    return true;
  }

  if (record.count >= limit) {
    return false;
  }

  record.count++;
  return true;
}

// In middleware.ts
const identifier = request.ip ?? "unknown";
if (!checkRateLimit(identifier, 100, 60000)) {
  return new NextResponse("Too Many Requests", { status: 429 });
}
```

### 3. Add Login Attempt Logging (30 minutes)

```typescript
// In /app/api/auth/login/route.ts
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_KEY!,
);

// Log login attempt
await supabase.from("audit_logs").insert({
  event_type: "AUTH",
  event_name: response.ok ? "LOGIN_SUCCESS" : "LOGIN_FAILURE",
  user_email: email,
  ip_address: request.headers.get("x-forwarded-for") ?? "unknown",
  timestamp: new Date().toISOString(),
});
```

---

## Testing Recommendations

### Security Testing Checklist

- [ ] Test authentication bypass attempts
- [ ] Test role escalation attempts
- [ ] Test CSRF attacks with and without valid origin
- [ ] Test rate limiting under load
- [ ] Test session timeout and refresh
- [ ] Test concurrent session handling
- [ ] Verify all audit logs are written
- [ ] Test MFA enforcement for admin role
- [ ] Test IP whitelist for admin access
- [ ] Verify security headers in all responses

### Penetration Testing Areas

1. **Authentication**: Brute force, credential stuffing, session fixation
2. **Authorization**: Privilege escalation, horizontal access control bypass
3. **CSRF**: Cross-site request forgery on all state-changing operations
4. **XSS**: Despite CSP, test for bypasses
5. **Rate Limiting**: DoS, API abuse
6. **Session Management**: Session hijacking, fixation, timeout bypass

---

## Compliance Considerations

### GDPR Article 30 - Records of Processing Activities

- **Current Status**: ❌ NON-COMPLIANT
- **Required**: Audit logs of data access and processing
- **Gap**: No logging of data access or admin actions

### HIPAA §164.312(b) - Audit Controls

- **Current Status**: ❌ NON-COMPLIANT
- **Required**: Audit trail of security-relevant events
- **Gap**: No persistent audit logging

### SOC 2 Type II - Logical Access Controls

- **Current Status**: ⚠️ PARTIAL
- **Required**: Strong authentication, role-based access, audit logging
- **Gap**: Missing server-side authorization and audit logs

### ISO 27001 - Access Control (A.9)

- **Current Status**: ⚠️ PARTIAL
- **Required**: Secure authentication, authorization, privilege management
- **Gap**: No MFA enforcement, insufficient admin protections

---

## Conclusion

The SAHOOL Admin middleware provides a solid foundation with excellent security headers and basic authentication, but requires significant enhancements for production use in an admin context. The critical gaps in authorization, rate limiting, and audit logging pose substantial security risks.

**Immediate Actions Required:**

1. Implement server-side role-based authorization
2. Add rate limiting to prevent abuse
3. Enhance CSRF protection
4. Implement comprehensive audit logging
5. Enforce MFA for admin accounts

**Estimated Effort:**

- Critical fixes: 2-3 weeks (1 developer)
- Full implementation: 4-6 weeks (1-2 developers)

**Risk Assessment:**

- Current risk level: MEDIUM-HIGH
- Post-implementation risk level: LOW
- Business impact of breach: HIGH (admin panel compromise)

---

## References

- OWASP Top 10 2021: https://owasp.org/Top10/
- OWASP ASVS 4.0: https://owasp.org/www-project-application-security-verification-standard/
- Next.js Security Best Practices: https://nextjs.org/docs/app/building-your-application/authentication
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- CWE Top 25: https://cwe.mitre.org/top25/

---

**Report Generated:** 2026-01-06
**Next Review Date:** 2026-02-06 (or after critical fixes implementation)
**Contact:** Security Team - security@sahool.io
