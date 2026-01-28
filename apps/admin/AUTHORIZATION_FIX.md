# Admin Panel Authorization Fix

## Issue

After successful login, clicking on links like `/farms` or `/diseases` resulted in unauthorized redirects:
```
GET /dashboard?error=unauthorized&attempted_route=%2Ffarms
GET /dashboard?error=unauthorized&attempted_route=%2Fdiseases
```

## Root Cause

**JWT Payload Mismatch between Backend and Frontend:**

- **Backend (user-service)**: Generates JWT tokens with `roles` as an **array**:
  ```typescript
  {
    sub: "user-id",
    email: "user@example.com",
    roles: ["ADMIN"],  // <-- Array format
    tid: "tenant-id"
  }
  ```

- **Frontend (admin panel)**: Expected `role` as a **singular string**:
  ```typescript
  userRole = payload.role || "viewer";  // <-- Always defaulted to "viewer"
  ```

This caused all users to be assigned the `viewer` role, which doesn't have access to routes requiring `admin` or `supervisor` permissions.

## Solution

### 1. Updated `middleware.ts`

**File**: `apps/admin/src/middleware.ts`

**Changes**:
- Extract role from `roles` array (backend format)
- Fallback to `role` field for backward compatibility
- Normalize role names (e.g., "ADMIN" → "admin", "FARMER" → "viewer")
- Map backend roles to admin panel roles:
  - `ADMIN`, `ADMINISTRATOR` → `admin`
  - `SUPERVISOR`, `MANAGER` → `supervisor`
  - Everything else → `viewer`

```typescript
// Extract role from roles array or fallback to role field
let extractedRole: string;
if (payload.roles && Array.isArray(payload.roles) && payload.roles.length > 0) {
  extractedRole = payload.roles[0];
} else if (payload.role) {
  extractedRole = payload.role;
} else {
  extractedRole = "viewer";
}

// Normalize and map to admin panel roles
const normalizedRole = extractedRole.toLowerCase();
if (normalizedRole === "admin" || normalizedRole === "administrator") {
  userRole = "admin";
} else if (normalizedRole === "supervisor" || normalizedRole === "manager") {
  userRole = "supervisor";
} else {
  userRole = "viewer";
}
```

### 2. Updated `jwt-verify.ts`

**File**: `apps/admin/src/lib/auth/jwt-verify.ts`

**Changes**:

#### TokenPayload Interface
```typescript
export interface TokenPayload extends JWTPayload {
  sub: string;
  email: string;
  role?: "admin" | "supervisor" | "viewer"; // Singular (legacy/optional)
  roles?: string[]; // Array (backend format)
  name?: string;
  tenant_id?: string;
  tid?: string; // Alternative tenant ID field
}
```

#### getUserRole Function
Updated to extract from `roles` array with proper normalization.

#### getUserFromToken Function
Updated to extract from `roles` array and handle both `tenant_id` and `tid` fields.

## Testing

### Before Fix
- User logs in successfully
- JWT token contains `roles: ["ADMIN"]`
- Middleware extracts `payload.role` → `undefined`
- Defaults to `"viewer"`
- Routes requiring `admin`/`supervisor` → **UNAUTHORIZED**

### After Fix
- User logs in successfully
- JWT token contains `roles: ["ADMIN"]`
- Middleware extracts `payload.roles[0]` → `"ADMIN"`
- Normalizes to `"admin"`
- Routes requiring `admin`/`supervisor` → **AUTHORIZED** ✅

## Impact

### Fixed Routes
All routes requiring specific roles now work correctly:

**Admin + Supervisor Routes:**
- `/farms` - Farm management
- `/diseases` - Disease tracking
- `/alerts` - Alert management
- `/sensors` - Sensor monitoring
- `/irrigation` - Irrigation control
- `/yield` - Yield predictions

**All Authenticated Routes:**
- `/dashboard` - Main dashboard
- `/analytics/*` - Analytics pages
- `/precision-agriculture/*` - Precision agriculture tools
- `/epidemic` - Epidemic tracking
- `/lab` - Laboratory features
- `/support` - Support pages

## Backward Compatibility

The fix maintains backward compatibility by:
1. Checking for `roles` array first (new format)
2. Falling back to `role` field if array doesn't exist (old format)
3. Defaulting to `"viewer"` if neither exists

## Related Files

- `apps/admin/src/middleware.ts` - Main authorization middleware
- `apps/admin/src/lib/auth/jwt-verify.ts` - JWT verification utilities
- `apps/admin/src/lib/auth/route-protection.ts` - Route protection rules
- `apps/services/user-service/src/auth/auth.service.ts` - Backend JWT generation

## Recommendations

### For Production

1. **Standardize JWT Format**: Consider updating backend to use singular `role` field OR update all frontends to use `roles` array consistently

2. **Add Role Validation**: Add server-side validation to ensure only valid roles are assigned:
   ```typescript
   const VALID_ROLES = ["admin", "supervisor", "viewer"] as const;
   ```

3. **Add Logging**: Log role extraction for debugging:
   ```typescript
   logger.debug(`Extracted role: ${extractedRole} → ${userRole}`);
   ```

4. **Update Documentation**: Document the role mapping in API documentation

### For Development

1. **Test with Different Roles**: Test login with users having different roles:
   - ADMIN → should access all routes
   - SUPERVISOR → should access farm/disease routes
   - FARMER → should only access viewer routes

2. **Monitor Logs**: Check for unauthorized errors in development to catch any remaining issues

## Status

✅ **FIXED** - Users can now access routes according to their assigned roles
