# Security Implementation Quick Reference

## What Was Fixed

### 1. HttpOnly Cookie Flag ✓

- **Before**: Cookies accessible from JavaScript (XSS vulnerable)
- **After**: HttpOnly cookies set server-side only
- **Impact**: Protects against XSS token theft

### 2. Session Duration ✓

- **Before**: 7 days
- **After**: 1 day (24 hours)
- **Impact**: Reduces token exposure window

### 3. Token Refresh ✓

- **Before**: No automatic refresh
- **After**: Auto-refresh every 5 minutes
- **Impact**: Seamless security without user disruption

### 4. Idle Timeout ✓

- **Before**: No timeout
- **After**: 30 minutes of inactivity
- **Impact**: Protects unattended admin sessions

## Files Changed

### New API Routes (5 files)

```
/apps/admin/src/app/api/auth/
├── login/route.ts      - Sets httpOnly cookies on login
├── logout/route.ts     - Clears all auth cookies
├── refresh/route.ts    - Refreshes access token
├── activity/route.ts   - Updates last activity timestamp
└── me/route.ts         - Gets current user (proxy)
```

### Modified Files (4 files)

```
/apps/admin/src/
├── stores/auth.store.tsx  - New auth flow with idle timeout
├── lib/auth.ts            - Deprecated, uses new API routes
├── lib/api.ts             - Updated for httpOnly cookies
└── middleware.ts          - Added idle timeout check
```

## Key Configuration

### Timeouts

```typescript
Session Duration:    1 day (86400 seconds)
Refresh Token:       7 days (604800 seconds)
Idle Timeout:        30 minutes
Refresh Interval:    5 minutes
Activity Update:     30 seconds
```

### Cookie Settings

```typescript
httpOnly: true; // ✓ Cannot be accessed by JavaScript
secure: production; // ✓ HTTPS only in production
sameSite: "strict"; // ✓ CSRF protection
maxAge: 86400; // ✓ 1 day expiration
```

## How It Works

### Login Flow

```
User Login → /api/auth/login → Backend API
                ↓
    Sets 3 httpOnly cookies:
    1. sahool_admin_token (access token)
    2. sahool_admin_refresh_token (refresh token)
    3. sahool_admin_last_activity (timestamp)
```

### Token Refresh Flow

```
Every 5 minutes → /api/auth/refresh
                ↓
    Uses refresh token from httpOnly cookie
                ↓
    Updates access token and last activity
```

### Idle Timeout Flow

```
User Activity → Updates lastActivityRef (client)
                ↓
    Every 30 seconds → /api/auth/activity
                ↓
    Updates sahool_admin_last_activity cookie
                ↓
    Every 1 minute → Check idle timeout
                ↓
    If 30+ minutes → Auto logout
```

### Middleware Flow

```
Every Request → middleware.ts
                ↓
    Checks sahool_admin_token exists
                ↓
    Checks last_activity < 30 minutes
                ↓
    If expired → Redirect to login
```

## Developer Usage

### Use the Auth Hook

```typescript
import { useAuth } from "@/stores/auth.store";

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();

  // Login
  await login(email, password);

  // Logout
  logout();

  // Check auth
  if (isAuthenticated) {
    // User is logged in
  }
}
```

### DO NOT Do This Anymore

```typescript
// ❌ WRONG - Won't work with httpOnly cookies
import Cookies from "js-cookie";
const token = Cookies.get("sahool_admin_token"); // Returns undefined

// ❌ WRONG - Can't set httpOnly from client
Cookies.set("sahool_admin_token", token, { httpOnly: true }); // Ignored

// ✅ CORRECT - Use the auth hook
const { login, logout } = useAuth();
```

## Testing

### Verify HttpOnly Cookie

1. Open browser DevTools → Application/Storage → Cookies
2. Find `sahool_admin_token`
3. Verify "HttpOnly" column is checked ✓
4. Try `document.cookie` in console - should NOT see token

### Verify Session Duration

1. Login
2. Check cookie expiration in DevTools
3. Should be ~24 hours from login time

### Verify Token Refresh

1. Login
2. Wait 5+ minutes
3. Check Network tab - should see calls to `/api/auth/refresh`
4. Verify no logout occurs

### Verify Idle Timeout

1. Login
2. Leave browser idle for 30+ minutes
3. Try to navigate - should redirect to login
4. URL should include `?reason=session_expired`

### Verify Activity Tracking

1. Login
2. Watch Network tab
3. Interact with page (click, type, scroll)
4. Should see periodic calls to `/api/auth/activity`

## Troubleshooting

### Issue: Can't access token from JavaScript

**Expected**: This is the intended behavior for security
**Solution**: Use server-side API routes or the useAuth hook

### Issue: API calls failing with 401

**Cause**: HttpOnly cookie not being sent to backend services
**Solution**: Backend must accept cookies OR proxy calls through Next.js API routes

### Issue: User logged out unexpectedly

**Check**:

1. Last activity timestamp - might be idle timeout
2. Token expiration - might need to refresh
3. Network errors - refresh might have failed

### Issue: Refresh token not working

**Check**:

1. Backend `/api/v1/auth/refresh` endpoint exists
2. Backend accepts refresh token in request body
3. Refresh token cookie is being sent

## Security Checklist

- [x] HttpOnly flag on all auth cookies
- [x] Secure flag in production
- [x] SameSite=strict for CSRF protection
- [x] 1-day session duration
- [x] 30-minute idle timeout
- [x] Automatic token refresh
- [x] Server-side cookie management
- [x] Activity tracking
- [x] Middleware validation
- [x] Clean logout (clears all cookies)

## Next Steps

### Optional Enhancements

1. **API Proxy Routes**: Create Next.js proxies for all backend calls
2. **Session Dashboard**: Admin view of active sessions
3. **Remember Me**: Optional longer sessions with user consent
4. **Device Tracking**: Log devices and locations for security
5. **2FA Enhancement**: Time-based OTP for sensitive operations

---

**Status**: ✅ All security improvements implemented
**Date**: 2026-01-06
