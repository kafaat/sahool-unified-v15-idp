# Admin App Authentication Migration

## Overview

The admin app authentication has been migrated from direct axios interceptor usage to a React Context-based approach, consistent with the web app implementation.

## Changes Made

### 1. New Authentication Store (`/src/stores/auth.store.tsx`)

A React Context-based authentication store that provides:

- **`AuthProvider`**: Wraps the app to provide authentication context
- **`useAuth` hook**: Access authentication state and methods anywhere in the app

#### Available Methods and State:

```typescript
const {
  user, // Current user object (null if not authenticated)
  isAuthenticated, // Boolean indicating if user is logged in
  isLoading, // Boolean indicating if auth check is in progress
  login, // Function to log in: (email: string, password: string) => Promise<void>
  logout, // Function to log out: () => void
  checkAuth, // Function to verify current auth state: () => Promise<void>
} = useAuth();
```

### 2. New API Client (`/src/lib/api-client.ts`)

A centralized API client that:

- Handles all authentication-related API calls
- Manages token storage and retrieval
- Provides retry logic and error handling
- Supports generic HTTP methods (GET, POST, PATCH, PUT, DELETE)

#### Features:

- **Automatic token management**: Tokens are automatically added to requests
- **Security**: XSS prevention, input sanitization, HTTPS enforcement in production
- **Retry logic**: Automatic retry for network and server errors (5xx)
- **401 handling**: Automatic redirect to login on unauthorized requests

### 3. Auth Guard Component (`/src/components/auth/AuthGuard.tsx`)

A component to protect routes that require authentication:

```typescript
<AuthGuard requiredRole="admin">
  <ProtectedContent />
</AuthGuard>
```

#### Role Hierarchy:

- `admin` (level 3) - Full access
- `supervisor` (level 2) - Can access supervisor and viewer routes
- `viewer` (level 1) - Can only access viewer routes

### 4. Updated Components

#### Root Layout (`/src/app/layout.tsx`)

```typescript
// Before: No provider
<body>{children}</body>

// After: Wrapped with Providers
<body>
  <Providers>{children}</Providers>
</body>
```

#### Login Page (`/src/app/login/page.tsx`)

```typescript
// Before: Direct import from auth utilities
import { login } from "@/lib/auth";

// After: Use auth context
import { useAuth } from "@/stores/auth.store";
const { login } = useAuth();
```

#### Protected Layouts

All protected route layouts now use `AuthGuard`:

```typescript
// dashboard, farms, diseases layouts
<AuthGuard requiredRole="viewer">
  <Sidebar />
  <main>{children}</main>
</AuthGuard>

// settings layout (admin only)
<AuthGuard requiredRole="admin">
  <Sidebar />
  <main>{children}</main>
</AuthGuard>
```

#### Header & Sidebar Components

```typescript
// Before: Direct auth utilities
import { getUser, logout } from "@/lib/auth";

// After: Use auth context
import { useAuth } from "@/stores/auth.store";
const { user, logout } = useAuth();
```

### 5. Updated API Configuration (`/src/lib/api.ts`)

The existing axios-based API client has been updated to:

- Use centralized token management from cookies
- Sync with the new API client on auth errors
- Maintain backward compatibility with existing API calls

## Migration Benefits

### 1. **Consistency**

- Admin app now uses the same auth pattern as the web app
- Easier to maintain and understand

### 2. **Centralized State Management**

- Single source of truth for authentication state
- No need to manually sync localStorage and cookies
- React Context automatically propagates changes

### 3. **Better Security**

- Centralized token management
- Automatic cleanup on logout
- Consistent 401 error handling
- XSS protection with input sanitization

### 4. **Improved Developer Experience**

- Simple `useAuth()` hook for accessing auth state
- Type-safe with TypeScript
- Clear separation of concerns
- Easy to test and mock

### 5. **Role-Based Access Control**

- Built-in role hierarchy
- Easy to protect routes with `AuthGuard`
- Automatic redirection for unauthorized access

## Usage Examples

### 1. Using Authentication in a Component

```typescript
'use client';
import { useAuth } from '@/stores/auth.store';

export default function MyComponent() {
  const { user, isAuthenticated, logout } = useAuth();

  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <h1>Welcome, {user?.name}!</h1>
      <p>Role: {user?.role}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### 2. Protecting a Route

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

### 3. Making Authenticated API Calls

```typescript
import { apiClient } from "@/lib/api-client";

// The token is automatically added to the request
const response = await apiClient.get("/api/v1/users");

if (response.success) {
  console.log(response.data);
} else {
  console.error(response.error);
}
```

## Token Storage

Tokens are now stored in cookies with the following configuration:

```typescript
Cookies.set("sahool_admin_token", token, {
  expires: 7, // 7 days
  secure: process.env.NODE_ENV === "production", // HTTPS only in production
  sameSite: "strict", // CSRF protection
});
```

## Backward Compatibility

The old authentication utilities in `/src/lib/auth.ts` are kept for backward compatibility but are marked as deprecated. Existing code will continue to work, but new code should use the `useAuth()` hook.

## Testing Recommendations

1. **Login Flow**: Test that login properly sets tokens and user state
2. **Logout Flow**: Test that logout clears tokens and redirects to login
3. **Protected Routes**: Test that unauthenticated users are redirected
4. **Role-Based Access**: Test that users can only access routes for their role
5. **Token Expiration**: Test that expired tokens trigger re-authentication

## Next Steps

1. ✅ Authentication system migrated to React Context
2. ✅ All layouts updated to use AuthGuard
3. ✅ Components updated to use useAuth hook
4. ✅ Centralized API client created
5. 🔄 Consider adding refresh token support
6. 🔄 Add authentication tests
7. 🔄 Consider adding session timeout warning

## File Structure

```
apps/admin/src/
├── stores/
│   └── auth.store.tsx         # New: Auth context and provider
├── lib/
│   ├── api-client.ts          # New: Centralized API client
│   ├── auth.ts                # Updated: Deprecated utilities (backward compat)
│   └── api.ts                 # Updated: Synced with new auth system
├── components/
│   ├── auth/
│   │   └── AuthGuard.tsx      # New: Route protection component
│   └── layout/
│       ├── Header.tsx         # Updated: Uses useAuth hook
│       └── Sidebar.tsx        # Updated: Uses useAuth hook
└── app/
    ├── providers.tsx          # New: App providers
    ├── layout.tsx             # Updated: Wrapped with Providers
    ├── login/
    │   └── page.tsx           # Updated: Uses useAuth hook
    ├── dashboard/
    │   └── layout.tsx         # Updated: Uses AuthGuard
    ├── farms/
    │   └── layout.tsx         # Updated: Uses AuthGuard
    ├── diseases/
    │   └── layout.tsx         # Updated: Uses AuthGuard
    └── settings/
        └── layout.tsx         # Updated: Uses AuthGuard (admin only)
```

## Environment Variables

Ensure the following environment variable is set:

```bash
NEXT_PUBLIC_API_URL=https://your-api-url.com
```

In development, it defaults to `http://localhost:3000`.

## Security Considerations

1. **HTTPS**: Always use HTTPS in production
2. **Cookie Security**: Cookies are marked as `secure` in production
3. **CSRF Protection**: Cookies use `sameSite: 'strict'`
4. **XSS Prevention**: Input sanitization on all user inputs
5. **Token Expiration**: Tokens expire after 7 days
6. **401 Handling**: Automatic token cleanup and redirect on unauthorized

## Support

For questions or issues, please refer to:

- Web app auth implementation: `/apps/web/src/stores/auth.store.tsx`
- API client documentation: `/apps/admin/src/lib/api-client.ts`
- Auth guard usage: `/apps/admin/src/components/auth/AuthGuard.tsx`
