# Mobile Auth Schema Synchronization

**Status**: COMPLETED (Phase 1, 2 & 3)
**Priority**: HIGH
**Created**: 2026-03-19
**Related**: user-service Prisma schema (`apps/services/user-service/prisma/schema.prisma`)
**Mobile**: `apps/mobile/lib/core/auth/`, `apps/mobile/sahool_field_app/lib/core/auth/`

## Summary

Static analysis revealed inconsistencies between the user-service Prisma schema and the Flutter mobile app's auth models. These are **pre-existing issues** not caused by the recent migration fixes, but need to be resolved to ensure full compatibility.

---

## Issues

### 1. UserRole Enum Mismatch (CRITICAL)

**Prisma Schema (source of truth):**

```prisma
enum UserRole {
  ADMIN
  MANAGER
  FARMER
  WORKER
  VIEWER
}
```

**Mobile (`sahool_field_app/lib/core/auth/permission_service.dart`):**

```dart
enum UserRole {
  viewer('viewer', 'مشاهد'),
  worker('worker', 'عامل ميداني'),
  supervisor('supervisor', 'مشرف'),      // NOT IN SCHEMA
  manager('manager', 'مدير'),
  admin('admin', 'مسؤول'),
  superAdmin('super_admin', 'مسؤول النظام') // NOT IN SCHEMA
}
```

**Problems:**
- `supervisor` and `superAdmin` exist in mobile but NOT in the schema
- `FARMER` exists in schema but NOT in mobile
- When backend returns `role: 'FARMER'`, mobile's `UserRole.fromString()` defaults to `VIEWER`

**Fix:**
- Add `farmer('farmer', 'مزارع')` to mobile enum
- Remove `supervisor` and `superAdmin`, or add them to the Prisma schema if needed
- Ensure case-insensitive matching in `UserRole.fromString()`

---

### 2. Missing UserStatus Enum (CRITICAL)

**Prisma Schema:**

```prisma
enum UserStatus {
  ACTIVE
  INACTIVE
  SUSPENDED
  PENDING
}
```

**Mobile:** No `UserStatus` enum exists. No `status` field on the User model.

**Impact:** Suspended or inactive users can still use the mobile app since status is never checked.

**Fix:**
- Create `UserStatus` enum in Dart
- Add `status` field to mobile User model
- Check status on login and token refresh

---

### 3. User Model Field Gaps (MEDIUM)

| Field | Prisma Schema | Mobile | Status |
|-------|--------------|--------|--------|
| `firstName` | Separate field | Separate field | DONE |
| `lastName` | Separate field | Separate field | DONE |
| `firstNameAr` | Separate field | Separate field | DONE |
| `lastNameAr` | Separate field | Separate field | DONE |
| `nameAr` | Separate field | Separate field | DONE |
| `status` | `UserStatus` enum | `UserStatus` enum | DONE |
| `emailVerified` | Boolean | Boolean (default: false) | DONE |
| `phoneVerified` | Boolean | Boolean (default: false) | DONE |
| `avatarUrl` | In `UserProfile` model | On `User` (no `UserProfile` model yet) | TODO |
| `failedLoginAttempts` | Integer | Not tracked | BACKLOG |
| `lockoutUntil` | DateTime? | Not tracked | BACKLOG |

---

### 4. Missing UserProfile Model (MEDIUM)

**Prisma Schema has a separate `UserProfile` model:**

```prisma
model UserProfile {
  userId      String   @unique
  nationalId  String?
  dateOfBirth DateTime?
  address     String?
  city        String?
  region      String?
  country     String?  @default("SA")
  avatarUrl   String?
}
```

**Mobile:** No separate profile model. `avatarUrl` is stored directly on the User object.

**Fix:**
- Create `UserProfile` model in Dart
- Add profile fetch endpoint integration
- Move `avatarUrl` to profile

---

### 5. Token Rotation Not Supported (LOW)

**Prisma `RefreshToken` model supports:**
- `jti` (JWT ID for rotation tracking)
- `family` (token family for rotation)
- `revoked` / `used` flags
- `replacedBy` (JTI of replacement token)

**Mobile:** Basic token storage only, no rotation tracking.

---

### 6. Test Fixtures Use String Roles (LOW)

Test files use hardcoded string roles instead of the enum:

```dart
// auth_models_test.dart
role: 'admin',   // Should use UserRole enum
role: 'farmer',  // Should use UserRole enum
```

---

## Consistent Items (No Action Needed)

- API paths: `/api/v1/auth/*` match between mobile and backend
- Kong gateway configuration is correct
- JWT token structure is compatible
- Tenant ID handling is consistent

---

## Action Plan

### Phase 1 - Critical (DONE)
- [x] Update `UserRole` enum in mobile to match Prisma schema (added `farmer` role)
- [x] Add `UserStatus` enum to mobile (active, inactive, suspended, pending)
- [x] Add `status` field to User model
- [x] Add `canLogin` check on UserStatus (login-time status validation)

### Phase 2 - Medium (DONE)
- [x] Add `firstName` / `lastName` fields (backend sends separate fields)
- [x] Add Arabic name fields (`firstNameAr`, `lastNameAr`, `nameAr`)
- [x] Create `UserProfile` model in Dart
- [x] Add `emailVerified` / `phoneVerified` fields

### Phase 3 - Security & Schema Alignment (DONE)
- [x] Implement token rotation tracking models (`TokenRotationInfo` with `jti`, `family`, `revoked`, `used`, `replacedBy`)
- [x] Add account lockout models (`AccountLockoutInfo` with `failedLoginAttempts`, `lockoutUntil`, `lastFailedLoginAt`)
- [x] Add `CachedUsers` and `CachedUserProfiles` tables to Drift DB for offline access
- [x] Document mobile-only roles (`supervisor`, `superAdmin`) with comments
- [x] Add deprecation notice to `UserIdentity` IAM model referencing `User` model
- [x] Add token revocation check in Python `get_current_user()` dependency
- [x] Align NestJS token revocation to fail-closed (matching Python behavior)
- [x] Add JWT token support to WebSocket connections (hook + client)
- [x] Implement `AsyncpgUserRepository` for FastAPI services
- [x] Add `require_2fa_verified` dependency for sensitive endpoints
- [x] Fix NestJS `forRootAsync()` to support `TokenRevocationGuard` export
- [x] Invalidate 2FA backup codes after use (return remaining codes)
- [x] Add security audit logging for failed 2FA attempts
- [x] Add WebSocket auth failure detection (codes 4001/4003)
- [x] Create `useWebSocket` hook tests
- [x] Enhance WebSocket client auth + error tests
- [ ] Run Dart contract codegen sync (`npx tsx scripts/sync-contracts-to-dart.ts`)

---

## Files Modified

| File | Changes |
|------|---------|
| `shared/auth/dependencies.py` | Token revocation check, 2FA enforcement, optional user revocation |
| `shared/auth/user_repository.py` | `AsyncpgUserRepository` implementation, SQLAlchemy fallback |
| `shared/auth/twofa_service.py` | Backup code invalidation, security audit logging |
| `packages/nestjs-auth/src/services/token-revocation.ts` | Fail-closed on Redis errors |
| `packages/nestjs-auth/src/auth.module.ts` | `forRootAsync` with token revocation exports |
| `apps/web/src/hooks/useWebSocket.ts` | JWT token param, auth failure detection |
| `apps/web/src/lib/ws/index.ts` | `setToken()`, auth failure handling |
| `apps/mobile/lib/core/storage/database.dart` | `CachedUsers`, `CachedUserProfiles` tables |
| `apps/mobile/lib/core/auth/permission_service.dart` | Role documentation |
| `apps/mobile/lib/core/auth/token_manager.dart` | `TokenRotationInfo`, `AccountLockoutInfo` |
| `apps/mobile/lib/core/iam/models/iam_models.dart` | `UserIdentity` deprecation note |
| `apps/web/src/hooks/__tests__/useWebSocket.test.ts` | New test file |
| `apps/web/src/lib/ws/__tests__/websocket-client.test.ts` | Auth + error tests |
