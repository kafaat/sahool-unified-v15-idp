# Flutter 3.41.5 Migration Guide | دليل ترقية Flutter 3.41.5

> **Status**: Planning | **Priority**: Medium | **Target**: Sprint 2026-Q2
>
> Migrating SAHOOL mobile apps from Flutter 3.27.1 to 3.41.5 (Dart 3.6 → 3.8)

---

## Executive Summary | الملخص التنفيذي

SAHOOL's mobile app has 708 Dart files with heavy dependencies on SQLCipher encryption,
Riverpod state management, and Drift offline database. This guide provides a **3-phase
migration plan** to minimize risk while reaching the latest Flutter stable.

**Key constraint**: Flutter 3.41.5 does NOT support AGP 9 — our current AGP 8.13.2
is already the maximum compatible version.

---

## Current vs Target Versions | الإصدارات الحالية والمستهدفة

| Component        | Current (v16.0.0) | Target          | Notes                          |
|------------------|-------------------|-----------------|--------------------------------|
| **Flutter**      | 3.27.1            | **3.41.5**      | Latest stable (Feb 2026)       |
| **Dart SDK**     | 3.6.0             | **3.8.0**       | Enhanced patterns, stricter types |
| **AGP**          | 8.13.2            | 8.13.2          | No change (max Flutter-compatible) |
| **Kotlin**       | 2.3.20            | 2.3.20          | No change (already latest)     |
| **Gradle**       | 8.14              | 8.14            | No change                      |
| **NDK**          | 27.2 (r27c LTS)  | 27.2            | No change                      |
| **compileSdk**   | 36                | 36              | No change                      |

---

## Phase 1: Safe Upgrades (No Code Changes)

**Risk**: LOW | **Effort**: 3-4 hours | **Files changed**: 2 (pubspec.yaml only)

These packages are backward-compatible within their major version:

```yaml
# pubspec.yaml — safe version bumps
dependencies:
  flutter_riverpod: ^2.8.0          # from 2.6.1
  riverpod: ^2.8.0                  # from 2.6.1
  riverpod_annotation: ^2.8.0       # from 2.6.1
  drift: ^2.28.0                    # from 2.24.0
  geolocator: ^13.2.0               # from 13.0.2
  dio: ^5.8.0                       # from 5.7.0
  flutter_map: ^8.3.0               # from ">=8.1.1 <8.2.0" (unpin)
  freezed_annotation: ^2.6.0        # from 2.4.4

dev_dependencies:
  riverpod_generator: ^2.8.0        # from 2.6.3
  drift_dev: ^2.28.0                # from 2.24.0
  build_runner: ^2.5.0              # from 2.4.13
  freezed: ^2.6.0                   # from 2.5.8

environment:
  sdk: '>=3.2.0 <4.0.0'            # No change needed (Dart 3.8 is within range)
```

### Execution Steps

```bash
# 1. Update Flutter SDK
flutter upgrade --force  # or: fvm use 3.41.5

# 2. Update pubspec.yaml (both apps)
# Edit apps/mobile/pubspec.yaml
# Edit apps/mobile/sahool_field_app/pubspec.yaml

# 3. Clean and fetch
flutter clean && flutter pub get

# 4. Regenerate code
dart run build_runner build --delete-conflicting-outputs

# 5. Analyze
flutter analyze  # must be zero errors

# 6. Run tests
flutter test

# 7. Build
flutter build apk --debug
```

### What NOT to Change in Phase 1

| Package               | Current  | Why Keep                                       |
|-----------------------|----------|-------------------------------------------------|
| `sqlcipher_flutter_libs` | 0.6.1 | Works with Dart 3.8; migration is Phase 3       |
| `sqlite3`             | 2.4.6    | 3.x changes encryption API; Phase 3             |
| `camera`              | 0.11.0+2 | 0.12.x needs code changes; Phase 2              |

### Testing Checklist — Phase 1

- [ ] `flutter analyze` — zero errors
- [ ] `flutter test` — all pass
- [ ] `flutter build apk --debug` — success
- [ ] App launches and login works
- [ ] Offline database opens correctly (SQLCipher)
- [ ] Map renders fields (flutter_map)
- [ ] Background sync triggers

---

## Phase 2: Minor Code Changes

**Risk**: MODERATE | **Effort**: 6-8 hours | **Files changed**: ~10-15

### 2A. Camera Plugin (Conditional)

Current `camera: ^0.11.0+2` → target `camera: ^0.12.0`

camera 0.12.x requires Android API 34+. Our `targetSdk = 36` satisfies this.

**Files to update:**
- `lib/features/vision/` — detection screens
- Any direct `CameraController` usage

**Code change example:**
```dart
// OLD (0.11.x)
final cameras = await availableCameras();
final controller = CameraController(cameras[0], ResolutionPreset.high);

// NEW (0.12.x) — same API, but init may throw on API < 34
final cameras = await availableCameras();
final controller = CameraController(cameras[0], ResolutionPreset.high);
// No code change needed if targetSdk >= 34
```

### 2B. CI Workflow Update

```yaml
# .github/workflows/mobile-ci.yml, flutter-apk.yml, etc.
env:
  FLUTTER_VERSION: '3.41.5'  # from 3.27.1
```

**All 7 workflow files that reference Flutter version:**
- `.github/workflows/mobile-ci.yml`
- `.github/workflows/flutter-apk.yml`
- `.github/workflows/mobile-release.yml`
- `.github/workflows/frontend-tests.yml`
- `.github/workflows/deploy-preview.yml`
- `.github/workflows/lighthouse-ci.yml`
- `.github/workflows/test.yml`

### 2C. Dart 3.8 Deprecation Fixes

Run `flutter analyze` — fix any new warnings from Dart 3.8:
- Stricter type inference in generic contexts
- Enhanced pattern matching (may suggest refactors)
- Null safety edge cases

**Estimated**: ~5-10 files with minor fixes

### Testing Checklist — Phase 2

- [ ] Camera capture works on Android device
- [ ] CI pipeline passes with Flutter 3.41.5
- [ ] No new analyzer warnings
- [ ] All integration tests pass

---

## Phase 3: Major Refactoring (Optional)

**Risk**: HIGH | **Effort**: 12-16 hours | **Files changed**: ~100-120

> **Recommendation**: Defer to a dedicated sprint. Not required for Flutter 3.41.5.

### 3A. SQLCipher → sqlite3 3.x Native Encryption

`sqlcipher_flutter_libs` is deprecated in favor of `sqlite3` 3.x with built-in
AES-256 encryption. This eliminates the external native dependency.

**Current architecture:**
```
App → Drift 2.x → sqlite3 2.x → sqlcipher_flutter_libs (native C)
```

**Target architecture:**
```
App → Drift 2.28+ → sqlite3 3.x (built-in encryption, no external lib)
```

**Critical files to refactor:**

| File | Changes |
|------|---------|
| `lib/core/storage/database.dart` | New `NativeDatabase.sqlite3()` init with `encryptionKey` param |
| `lib/core/storage/database_encryption.dart` | Return `Uint8List` instead of `String` |
| `lib/core/database/migrations/*.dart` | Verify 8 migration files compatible |
| `lib/features/*/data/*_local_db.dart` | ~15-20 feature DAOs (likely no changes) |
| `test/core/database/*.dart` | ~8 test files need encryption key format update |

**Database migration risk:**
> Old encrypted databases (SQLCipher format) are NOT directly readable by
> sqlite3 3.x. You MUST implement an export/re-import migration script.
> Users upgrading from v16 to v17 will need automatic data migration.

**Migration script outline:**
```dart
Future<void> migrateEncryption() async {
  // 1. Open old DB with sqlcipher_flutter_libs
  final oldDb = await openOldDatabase(oldKey);
  
  // 2. Export all tables to memory
  final data = await exportAllTables(oldDb);
  
  // 3. Create new DB with sqlite3 3.x encryption
  final newDb = await createNewDatabase(newKey);
  
  // 4. Import data
  await importAllTables(newDb, data);
  
  // 5. Verify integrity
  assert(await verifyDataIntegrity(oldDb, newDb));
  
  // 6. Delete old DB file
  await oldDb.close();
  await File(oldPath).delete();
}
```

### 3B. Riverpod 2.x → 3.x (NOT Recommended Now)

Riverpod 3.x is a **major rewrite** with breaking changes:
- `StateNotifier` → `Notifier` (all 10 StateNotifier classes)
- `ConsumerWidget` API changes (293 widgets)
- Stream filtering behavior changes
- New `updateShouldNotify` pattern

**Recommendation**: Stay on Riverpod 2.8.x. Migrate to 3.x only when the
ecosystem has fully stabilized (estimated: Q4 2026).

---

## Dependency Compatibility Matrix | مصفوفة التوافق

| Package | Flutter 3.27 | Flutter 3.41 | Action |
|---------|-------------|-------------|--------|
| riverpod 2.8.x | ✅ | ✅ | Upgrade in Phase 1 |
| drift 2.28.x | ✅ | ✅ | Upgrade in Phase 1 |
| sqlcipher_flutter_libs 0.6.1 | ✅ | ✅ | Keep (Phase 3 optional) |
| sqlite3 2.4.6 | ✅ | ✅ | Keep (Phase 3 optional) |
| flutter_map 8.3.x | ✅ | ✅ | Upgrade in Phase 1 |
| dio 5.8.x | ✅ | ✅ | Upgrade in Phase 1 |
| camera 0.11.x | ✅ | ✅ | Keep or upgrade Phase 2 |
| camera 0.12.x | ❌ API 34+ | ✅ | Phase 2 (optional) |
| geolocator 13.2.x | ✅ | ✅ | Upgrade in Phase 1 |
| freezed 2.6.x | ✅ | ✅ | Upgrade in Phase 1 |
| riverpod 3.x | ❌ | ⚠️ | NOT recommended yet |
| sqlite3 3.x | ❌ | ✅ | Phase 3 (optional) |

---

## Risk Assessment | تقييم المخاطر

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SQLCipher incompatibility | Low | Critical | Keep 0.6.1 in Phase 1-2; test thoroughly |
| Drift schema corruption | Very Low | Critical | Existing migrations tested; no schema changes |
| Riverpod state regression | Low | High | Stay on 2.x; only minor version bump |
| flutter_map rendering | Very Low | Medium | Incremental version bump (8.1→8.3) |
| Camera API break | Low | Medium | Keep 0.11.x if issues; our targetSdk=36 is safe |
| Dart 3.8 type inference | Medium | Low | `flutter analyze` catches all issues |
| CI build failure | Low | Low | Flutter version pinned in workflows |

---

## Effort Summary | ملخص الجهد

| Phase | Duration | Code Files | Config Files | Risk | Can Ship? |
|-------|----------|------------|-------------|------|-----------|
| **Phase 1** | 3-4 hrs | 0 | 2 pubspec.yaml | LOW | ✅ Yes |
| **Phase 2** | 6-8 hrs | ~10-15 | 7 workflows | MODERATE | ✅ Yes |
| **Phase 3** | 12-16 hrs | ~100-120 | 0 | HIGH | ⚠️ With testing |
| **Total** | **21-28 hrs** | **~110-135** | **9** | | |

---

## Recommended Timeline | الجدول الزمني المقترح

```
Week 1 (Phase 1):
  Mon-Tue: Update pubspec.yaml, flutter pub get, code generation
  Wed-Thu: Full test suite, build APK, smoke test
  Fri:     Release to staging
  ✓ Checkpoint: Can merge to main

Week 2 (Phase 2):
  Mon:     Update CI workflows to Flutter 3.41.5
  Tue-Wed: Camera verification, Dart 3.8 analyzer fixes
  Thu:     Integration testing
  Fri:     Release to production
  ✓ Checkpoint: Migration complete for production use

Week 3-4 (Phase 3 — optional, separate sprint):
  Only if sqlite3 3.x migration is a strategic priority
  Requires dedicated QA cycle for database migration testing
```

---

## Rollback Plan | خطة التراجع

| Phase | Rollback Method | Time |
|-------|----------------|------|
| Phase 1 | `git revert` on pubspec changes + `flutter pub get` | 5 min |
| Phase 2 | Revert workflow files + pubspec | 10 min |
| Phase 3 | **Critical**: Must keep old DB backup; revert code + restore DB | 1-2 hrs |

---

## References | المراجع

- [Flutter 3.41 Release Notes](https://docs.flutter.dev/release/release-notes/release-notes-3.41.0)
- [Dart 3.8 Migration](https://dart.dev/guides/language/evolution)
- [Drift Changelog](https://drift.simonbinder.eu/docs/)
- [Riverpod 2.x Documentation](https://riverpod.dev)
- [Flutter Breaking Changes](https://docs.flutter.dev/release/breaking-changes)
- [sqlite3 3.x Encryption](https://pub.dev/packages/sqlite3)
- [Flutter AGP 9 Status](https://github.com/flutter/flutter/issues/181383)

---

_Created: 2026-04-12 | Author: Claude Code | Project: SAHOOL v16.0.0_
