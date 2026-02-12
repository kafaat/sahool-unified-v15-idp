# Admin Dashboard — Authorization & Security

> **Security Score: 8.5/10** · Server-side JWT verification · RBAC · httpOnly cookies · CSRF protection

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Authentication Flow](#authentication-flow)
- [Cookie Security](#cookie-security)
- [JWT Verification](#jwt-verification)
- [Role-Based Access Control](#role-based-access-control)
- [Route Protection](#route-protection)
- [API Route Protection](#api-route-protection)
- [Developer Quick Reference](#developer-quick-reference)
- [Troubleshooting](#troubleshooting)
- [Security Checklist](#security-checklist)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Browser Request                                            │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Next.js Middleware (src/middleware.ts)                      │
│                                                             │
│  1. ✅ Check token exists (httpOnly cookie)                 │
│  2. ✅ Verify JWT signature (jose library)                  │
│  3. ✅ Validate token expiry                                │
│  4. ✅ Check idle timeout (30 min)                          │
│  5. ✅ Extract user role from verified token                │
│  6. ✅ Check route protection rules                         │
│  7. ✅ CSRF validation on mutating requests                 │
│                                                             │
│  Result:                                                    │
│  - Valid token + correct role    → Allow                    │
│  - Invalid/expired token         → 401 + redirect to login │
│  - Insufficient role             → 403 Forbidden           │
│  - Idle timeout exceeded         → Redirect to login       │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  API Route (withAdmin/withRole/withAuth wrapper)            │
│  ✅ Double-verification of role                             │
│  ✅ Only proceeds if authorized                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Files

| File | Purpose |
|------|---------|
| `src/middleware.ts` | Global middleware — auth, CSRF, idle timeout, security headers |
| `src/lib/auth/jwt-verify.ts` | JWT signature verification and token parsing |
| `src/lib/auth/route-protection.ts` | Route-to-role mapping configuration |
| `src/lib/auth/api-middleware.ts` | `withAdmin()`, `withRole()`, `withAuth()` wrappers |
| `src/stores/auth.store.tsx` | React auth context, idle tracking, token refresh |
| `src/lib/api-client.ts` | Centralized HTTP client with token management |
| `src/components/auth/AuthGuard.tsx` | Client-side route protection (UX only) |
| `src/lib/security/csp-config.ts` | Content Security Policy headers |
| `src/lib/security/csrf-server.ts` | CSRF token utilities |
| `src/lib/sanitize.ts` | Input sanitization (XSS prevention) |

---

## Authentication Flow

### Login

```
User submits credentials
  → POST /api/auth/login (Next.js API route)
    → Forwards to user-service via Kong: POST http://localhost:8000/api/v1/auth/login
      → Returns JWT tokens
  → Sets 3 httpOnly cookies:
    1. sahool_admin_token (access token, 1 day)
    2. sahool_admin_refresh_token (refresh token, 7 days)
    3. sahool_admin_last_activity (timestamp, 1 day)
```

### Token Refresh (automatic)

```
Every 5 minutes → POST /api/auth/refresh
  → Uses refresh token from httpOnly cookie
  → Updates access token + last activity
  → On failure: clears cookies, redirects to login
```

### Idle Timeout

```
User activity (click, type, scroll)
  → Updates lastActivityRef (client-side)
  → Every 30 seconds → POST /api/auth/activity (updates cookie)
  → Middleware checks last_activity on every request
  → If 30+ minutes idle → auto logout + redirect to login
```

### Auth Hook Usage

```typescript
import { useAuth } from "@/stores/auth.store";

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();

  // Login
  await login(email, password);

  // Check auth
  if (isAuthenticated) {
    console.log(user?.role); // "admin" | "supervisor" | "viewer"
  }

  // Logout
  logout();
}
```

---

## Cookie Security

All auth cookies use secure settings:

| Cookie | httpOnly | secure | sameSite | maxAge |
|--------|----------|--------|----------|--------|
| `sahool_admin_token` | ✅ | prod only | strict | 1 day (86400s) |
| `sahool_admin_refresh_token` | ✅ | prod only | strict | 7 days (604800s) |
| `sahool_admin_last_activity` | ✅ | prod only | strict | 1 day (86400s) |

### Important

```typescript
// ❌ WRONG — httpOnly cookies NOT accessible from JavaScript
import Cookies from "js-cookie";
const token = Cookies.get("sahool_admin_token"); // Returns undefined

// ✅ CORRECT — use the auth hook
const { login, logout } = useAuth();
```

---

## JWT Verification

### Token Format

The middleware handles both JWT formats:

```typescript
// Current format (user-service)
{
  sub: "user-id",
  email: "user@example.com",
  roles: ["ADMIN"],       // Array
  tid: "tenant-id"
}

// Legacy format (also supported)
{
  sub: "user-id",
  email: "user@example.com",
  role: "admin",           // String
  tenant_id: "tenant-id"
}
```

### Role Extraction Logic

```typescript
// 1. Try roles array first (current backend format)
if (payload.roles && Array.isArray(payload.roles) && payload.roles.length > 0) {
  extractedRole = payload.roles[0];
}
// 2. Fallback to role field (legacy format)
else if (payload.role) {
  extractedRole = payload.role;
}
// 3. Default to viewer
else {
  extractedRole = "viewer";
}

// Normalize to admin panel roles
const normalizedRole = extractedRole.toLowerCase();
if (normalizedRole === "admin" || normalizedRole === "administrator") → "admin"
if (normalizedRole === "supervisor" || normalizedRole === "manager") → "supervisor"
otherwise → "viewer"
```

### Configuration

```env
JWT_SECRET=<must match JWT_SECRET_KEY in root .env>
JWT_ISSUER=sahool-platform
JWT_AUDIENCE=sahool-users
JWT_ALGORITHM=HS256
```

See [JWT_SETUP.md](./JWT_SETUP.md) for quick setup instructions.

---

## Role-Based Access Control

### Role Hierarchy

```
admin (level 3) — Full access
  ↓ inherits
supervisor (level 2) — Read + limited write
  ↓ inherits
viewer (level 1) — Read-only
```

### Route Protection Map

| Route Pattern | Required Role | Description |
|---------------|--------------|-------------|
| `/dashboard` | viewer+ | Main dashboard |
| `/farms` | supervisor+ | Farm management |
| `/diseases` | supervisor+ | Disease tracking |
| `/alerts` | supervisor+ | Alert management |
| `/sensors` | supervisor+ | Sensor monitoring |
| `/irrigation` | supervisor+ | Irrigation control |
| `/yield` | supervisor+ | Yield predictions |
| `/users` | admin | User management |
| `/settings` | admin | System settings |
| `/analytics/*` | viewer+ | Analytics dashboards |
| `/precision-agriculture/*` | viewer+ | Precision agriculture tools |
| `/epidemic` | viewer+ | Epidemic tracking |
| `/lab` | viewer+ | Laboratory features |
| `/support` | viewer+ | Support pages |
| `/marketplace` | viewer+ | Marketplace |
| `/inventory` | viewer+ | Inventory |
| `/logistics` | viewer+ | Logistics |
| `/research` | viewer+ | Research tools |
| `/crop-health` | viewer+ | Crop health |
| `/disasters` | viewer+ | Disaster assessment |
| `/community` | viewer+ | Community features |
| `/compliance` | viewer+ | Compliance |
| `/login` | public | Login page |
| `/register` | public | Registration |
| `/forgot-password` | public | Password recovery |
| `/reset-password` | public | Password reset |
| `/verify-otp` | public | OTP verification |

---

## API Route Protection

### Wrapper Functions

Protect API routes with role-specific middleware wrappers:

```typescript
// Admin-only endpoint
import { withAdmin } from "@/lib/auth";

export const POST = withAdmin(async (request, { user }) => {
  // ✅ Only admins reach this code
  // user.role is guaranteed to be "admin"
  const body = await request.json();
  await updateSettings(body);
  return NextResponse.json({ success: true });
});

// Multi-role endpoint
import { withRole } from "@/lib/auth";

export const GET = withRole(["admin", "supervisor"])(async (request, { user }) => {
  // ✅ Only admins and supervisors reach this code
  return NextResponse.json({ data: await getData() });
});

// Any authenticated user
import { withAuth } from "@/lib/auth";

export const GET = withAuth(async (request, { user }) => {
  // ✅ Any authenticated user
  return NextResponse.json({ user });
});
```

### Error Responses

```typescript
// 401 Unauthorized — invalid/expired/missing token
{ "error": "Unauthorized", "message": "Invalid or expired token" }

// 403 Forbidden — insufficient role
{
  "error": "Forbidden",
  "message": "You do not have permission to access this resource",
  "required_roles": ["admin"],
  "your_role": "viewer"
}
```

---

## Developer Quick Reference

### Protecting a Client Route

```typescript
'use client';
import { AuthGuard } from '@/components/auth/AuthGuard';

export default function AdminSettingsPage() {
  return (
    <AuthGuard requiredRole="admin">
      <div>
        <h1>Admin Settings</h1>
        {/* Admin-only content */}
      </div>
    </AuthGuard>
  );
}
```

### Making API Calls

```typescript
import { apiClient } from "@/lib/api-client";

// Token is automatically included via httpOnly cookie
const response = await apiClient.get("/api/v1/users");

if (response.success) {
  console.log(response.data);
} else {
  console.error(response.error);
}
```

### Auth Server API Routes

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/login` | Login, sets httpOnly cookies |
| POST | `/api/auth/logout` | Clears all auth cookies |
| POST | `/api/auth/refresh` | Refreshes access token |
| POST | `/api/auth/activity` | Updates last activity timestamp |
| GET | `/api/auth/me` | Gets current user (proxies to backend) |

---

## Troubleshooting

### Unauthorized Redirects After Login

**Symptom:** `GET /dashboard?error=unauthorized&attempted_route=%2Ffarms`

**Cause:** JWT uses `roles` array but middleware expected `role` string (fixed).

**Fix:** Clear browser cookies and re-login. If persists, verify the middleware handles both `roles` (array) and `role` (string).

### Can't Access Token from JavaScript

**Expected behavior.** Cookies are httpOnly for XSS protection. Use the `useAuth()` hook or server-side API routes.

### User Logged Out Unexpectedly

Check in order:
1. **Idle timeout** — 30 minutes of inactivity triggers logout
2. **Token expiry** — access token expires after 1 day
3. **Refresh failure** — check if `/api/auth/refresh` returns errors in Network tab

### API Calls Failing with 401

- Backend must accept cookies OR proxy calls through Next.js API routes
- Ensure `withCredentials: true` is set on axios requests

### JWT_SECRET Mismatch

- Admin app's `JWT_SECRET` must match root `.env` `JWT_SECRET_KEY`
- Restart dev server after changing env vars

---

## Security Checklist

| Feature | Status |
|---------|--------|
| **Authentication** | |
| httpOnly cookies | ✅ |
| Secure flag (production) | ✅ |
| SameSite=strict (CSRF) | ✅ |
| JWT signature verification | ✅ |
| Token expiry validation | ✅ |
| 1-day session duration | ✅ |
| 30-minute idle timeout | ✅ |
| Auto token refresh (5 min) | ✅ |
| **Authorization** | |
| Server-side role check (middleware) | ✅ |
| Server-side role check (API wrappers) | ✅ |
| Route protection rules | ✅ |
| Role hierarchy enforcement | ✅ |
| Proper 403 Forbidden responses | ✅ |
| **Security Headers** | |
| Content Security Policy (nonce-based) | ✅ |
| HSTS (31536000s in production) | ✅ |
| X-Frame-Options: DENY | ✅ |
| X-Content-Type-Options: nosniff | ✅ |
| Referrer-Policy | ✅ |
| **Input Validation** | |
| XSS prevention (sanitize.ts) | ✅ |
| CSRF protection (double-submit) | ✅ |
| Input validation (validation.ts) | ✅ |

### Remaining Improvements

| Item | Priority | Status |
|------|----------|--------|
| Rate limiting on `/api/auth/login` | High | Planned |
| Restrict CORS on CSP report endpoint | Medium | Planned |
| API proxy routes for all backend calls | Low | Planned |
| Session dashboard (view/revoke sessions) | Low | Planned |
| MFA/2FA enforcement for sensitive ops | Low | Planned |

---

**Last Updated:** February 2026 · **Version:** 16.0.0
