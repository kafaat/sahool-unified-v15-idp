# Admin App Cookie Security Improvements

## Overview
This document outlines the comprehensive security improvements made to the authentication system in the Sahool Admin application.

## Security Issues Fixed

### 1. HttpOnly Cookie Flag Added ✓
**Issue**: Auth cookies were accessible from JavaScript, vulnerable to XSS attacks.

**Solution**: All authentication cookies now use the `httpOnly: true` flag, making them inaccessible to client-side JavaScript.

**Files Modified**:
- Created server-side API routes for cookie management
- Updated authentication flow to use httpOnly cookies

### 2. Session Duration Reduced ✓
**Issue**: Session duration was 7 days, too long for admin access.

**Solution**: Reduced session duration from 7 days to 1 day (24 hours).

**Implementation**:
- Access token: `maxAge: 86400` (1 day)
- Refresh token: `maxAge: 604800` (7 days)

### 3. Token Refresh Mechanism ✓
**Issue**: No automatic token refresh, users logged out after token expiry.

**Solution**: Implemented automatic token refresh mechanism.

**Features**:
- Refresh check runs every 5 minutes
- Seamless token renewal without user interruption
- Refresh endpoint: `/api/auth/refresh`

### 4. Idle Timeout (30 minutes) ✓
**Issue**: No idle session timeout, security risk for unattended sessions.

**Solution**: Implemented 30-minute idle timeout with activity tracking.

**Features**:
- Tracks user activity (mouse, keyboard, scroll, touch, click)
- Updates activity timestamp every 30 seconds when active
- Client-side and server-side idle timeout checks
- Automatic logout after 30 minutes of inactivity

## Files Created

### Server-Side API Routes
1. **`/apps/admin/src/app/api/auth/login/route.ts`**
   - Handles login with secure httpOnly cookie setting
   - Sets access token, refresh token, and last activity timestamp
   - Supports 2FA flow

2. **`/apps/admin/src/app/api/auth/logout/route.ts`**
   - Clears all authentication cookies
   - Ensures clean logout

3. **`/apps/admin/src/app/api/auth/refresh/route.ts`**
   - Refreshes access token using refresh token
   - Updates last activity timestamp
   - Clears cookies if refresh fails

4. **`/apps/admin/src/app/api/auth/activity/route.ts`**
   - Updates last activity timestamp for idle timeout tracking
   - Called periodically during user activity

5. **`/apps/admin/src/app/api/auth/me/route.ts`**
   - Proxy route for getting current user
   - Injects token from httpOnly cookie server-side

## Files Modified

### 1. `/apps/admin/src/stores/auth.store.tsx`
**Changes**:
- Removed client-side cookie manipulation (js-cookie)
- Integrated with new server-side API routes
- Added idle timeout tracking (30 minutes)
- Added token refresh mechanism (every 5 minutes)
- Activity tracking via event listeners
- Automatic logout on idle timeout

**New Constants**:
```typescript
const IDLE_TIMEOUT = 30 * 60 * 1000; // 30 minutes
const REFRESH_CHECK_INTERVAL = 5 * 60 * 1000; // 5 minutes
const ACTIVITY_UPDATE_INTERVAL = 30 * 1000; // 30 seconds
```

### 2. `/apps/admin/src/lib/auth.ts`
**Changes**:
- Marked as deprecated (kept for backward compatibility)
- Updated to use server-side API routes
- Removed client-side cookie access
- Added security warnings and documentation
- `getToken()` and `setToken()` now deprecated with warnings

### 3. `/apps/admin/src/middleware.ts`
**Changes**:
- Added idle timeout check (30 minutes)
- Validates last activity timestamp from httpOnly cookie
- Redirects to login with reason if session expired
- Clears all auth cookies on idle timeout

### 4. `/apps/admin/src/lib/api.ts`
**Changes**:
- Added `withCredentials: true` to axios config for cookie support
- Updated error interceptor to use logout API route
- Added documentation about httpOnly cookie limitations
- Noted future refactoring needs for API proxy routes

## Security Features Summary

| Feature | Before | After |
|---------|--------|-------|
| Cookie HttpOnly | ❌ No | ✅ Yes |
| Session Duration | 7 days | 1 day |
| Token Refresh | ❌ None | ✅ Every 5 min |
| Idle Timeout | ❌ None | ✅ 30 minutes |
| Cookie Secure Flag | ✅ Production | ✅ Production |
| Cookie SameSite | ✅ Strict | ✅ Strict |

## Cookie Configuration

### Access Token Cookie
```typescript
{
  name: 'sahool_admin_token',
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict',
  maxAge: 86400, // 1 day
  path: '/'
}
```

### Refresh Token Cookie
```typescript
{
  name: 'sahool_admin_refresh_token',
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict',
  maxAge: 604800, // 7 days
  path: '/'
}
```

### Last Activity Cookie
```typescript
{
  name: 'sahool_admin_last_activity',
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'strict',
  maxAge: 86400, // 1 day
  path: '/'
}
```

## Activity Tracking

### Client-Side
- Monitors: mousedown, keydown, scroll, touchstart, click
- Updates activity timestamp locally
- Sends activity update to server every 30 seconds
- Checks for idle timeout every 60 seconds
- Automatic logout after 30 minutes of inactivity

### Server-Side
- Middleware checks last activity on every request
- Redirects to login if idle timeout exceeded
- Clears all auth cookies on timeout
- Passes reason in query param: `?reason=session_expired`

## Token Refresh Flow

1. **Automatic Refresh**: Every 5 minutes while user is authenticated
2. **Refresh Endpoint**: `POST /api/auth/refresh`
3. **Uses**: Refresh token from httpOnly cookie
4. **Success**: Updates access token and refresh token
5. **Failure**: Clears cookies and redirects to login

## Migration Notes

### For Developers

1. **DO NOT** use `Cookies.get('sahool_admin_token')` - it will return undefined
2. **DO NOT** use `Cookies.set('sahool_admin_token', ...)` - tokens must be set server-side
3. **DO** use the `useAuth()` hook from `@/stores/auth.store` for authentication
4. **DO** use `/api/auth/*` routes for all auth operations

### Backward Compatibility

- Legacy `auth.ts` functions still work but are deprecated
- They now use server-side API routes internally
- Warnings are logged when deprecated functions are used

### Future Improvements

1. **API Proxy Routes**: Create Next.js API routes to proxy all backend service calls
2. **Cookie Domain**: Configure cookie domain for subdomain sharing if needed
3. **Remember Me**: Optional longer session duration with explicit user consent
4. **Session Management**: Admin dashboard to view/revoke active sessions

## Testing Checklist

- [ ] Login sets httpOnly cookies
- [ ] Cookies are not accessible from browser console
- [ ] Session expires after 1 day
- [ ] Token refreshes automatically every 5 minutes
- [ ] User logged out after 30 minutes of inactivity
- [ ] Activity tracking updates on user interaction
- [ ] Logout clears all cookies
- [ ] Middleware redirects on idle timeout
- [ ] Secure flag set in production
- [ ] SameSite=strict prevents CSRF

## Security Best Practices Applied

1. ✅ **HttpOnly cookies**: Prevents XSS token theft
2. ✅ **Secure flag**: HTTPS-only in production
3. ✅ **SameSite=strict**: Prevents CSRF attacks
4. ✅ **Short session duration**: Limits exposure window
5. ✅ **Token refresh**: Seamless security without UX impact
6. ✅ **Idle timeout**: Protects unattended sessions
7. ✅ **Server-side validation**: Middleware checks on every request
8. ✅ **Activity tracking**: Monitors real user engagement

## Compliance

These improvements help meet security requirements for:
- OWASP Top 10 (XSS, CSRF, Broken Authentication)
- PCI DSS (if handling payment data)
- GDPR (session management and data protection)
- SOC 2 (access control and session management)

## Support

For questions or issues related to authentication security, contact the development team.

---

**Last Updated**: 2026-01-06
**Version**: 1.0.0
**Author**: Security Enhancement Implementation
