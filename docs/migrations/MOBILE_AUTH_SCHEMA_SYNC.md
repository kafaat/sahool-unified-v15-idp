# Mobile Auth Schema Synchronization

**Status**: COMPLETED (Phase 1 & 2)
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

### Phase 3 - Low (Backlog)
- [ ] Implement token rotation tracking (`jti`, `family`)
- [ ] Track account lockout state (`failedLoginAttempts`, `lockoutUntil`)
- [ ] Run Dart contract codegen sync (`npx tsx scripts/sync-contracts-to-dart.ts`)

---

## Files to Modify

| File | Changes |
|------|---------|
| `apps/mobile/sahool_field_app/lib/core/auth/permission_service.dart` | Update UserRole enum |
| `apps/mobile/lib/core/auth/auth_service.dart` | Add UserStatus, update User model |
| `apps/mobile/lib/core/api/kong_gateway_client.dart` | No changes needed |
| `apps/mobile/test/features/auth/auth_mocks.dart` | Update test fixtures |
| `apps/mobile/sahool_field_app/test/unit/core/auth/auth_models_test.dart` | Use enum values |
