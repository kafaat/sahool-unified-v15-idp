# Drift/Flutter_Test Naming Conflict Fix

## المشكلة (Problem)

فشلت اختبارات الوحدة بسبب تضارب في الأسماء بين مكتبتين:
- `package:drift/drift.dart` تصدّر `isNull` و `isNotNull`
- `package:matcher/matcher.dart` (عبر `flutter_test`) تصدّر نفس الأسماء

The unit tests were failing due to naming conflicts between two packages:
- `package:drift/drift.dart` exports `isNull` and `isNotNull`
- `package:matcher/matcher.dart` (via `flutter_test`) exports the same names

### خطأ التحليل (Analysis Error)
```
error • The name 'isNotNull' is defined in the libraries 
  'package:drift/src/runtime/query_builder/query_builder.dart (via package:drift/drift.dart)' and 
  'package:matcher/src/core_matchers.dart (via package:flutter_test/flutter_test.dart)'

error • The name 'isNull' is defined in the libraries 
  'package:drift/src/runtime/query_builder/query_builder.dart (via package:drift/drift.dart)' and 
  'package:matcher/src/core_matchers.dart (via package:flutter_test/flutter_test.dart)'
```

## الحل (Solution)

Added `hide isNull, isNotNull` clause to drift imports in all affected test files.

### الاستراتيجية (Strategy)

```dart
// قبل (Before)
import 'package:drift/drift.dart';
import 'package:flutter_test/flutter_test.dart';

// بعد (After)
import 'package:drift/drift.dart' hide isNull, isNotNull;
import 'package:flutter_test/flutter_test.dart';
```

هذا الحل يفضل لأن:
1. ملفات الاختبار تستخدم `isNull`/`isNotNull` من `matcher` (للتحقق من النتائج)
2. `drift` يوفر نفس الدوال لبناء الاستعلامات SQL، لكنها غير مستخدمة في سياق الاختبار
3. حل بسيط وواضح بدون تغييرات في الكود

This solution is preferred because:
1. Test files use `isNull`/`isNotNull` from `matcher` (for assertions)
2. `drift` provides the same functions for SQL query building, but they're not used in test context
3. Simple and clear solution without code changes

## الملفات المعدلة (Modified Files)

### ✅ apps/mobile/test/core/database/
1. `migration_test.dart` - Database migration tests
2. `migration_integration_test.dart` - Integration tests for migrations
3. `sync_queue_dao_test.dart` - Sync queue and outbox operations
4. `weather_dao_test.dart` - Weather data caching tests
5. `field_dao_test.dart` - Field CRUD operations tests
6. `database_test.dart` - Database initialization tests

### ✅ apps/mobile/sahool_field_app/test/
7. `unit/features/tasks/tasks_repo_test.dart` - Tasks repository tests (already had fix)

## التحقق (Verification)

### Check All Files
```bash
find apps/mobile -name "*.dart" -path "*/test/*" -exec grep -l "drift/drift.dart" {} \; | \
  while read file; do 
    if grep -q "flutter_test" "$file"; then 
      echo "File: $file"
      grep "drift/drift.dart" "$file" | head -1
      echo ""
    fi
  done
```

### Expected Output
All 7 files should show the `hide isNull, isNotNull` clause:
```
File: apps/mobile/test/core/database/migration_integration_test.dart
import 'package:drift/drift.dart' hide isNull, isNotNull;

File: apps/mobile/test/core/database/field_dao_test.dart
import 'package:drift/drift.dart' hide isNull, isNotNull;

File: apps/mobile/test/core/database/migration_test.dart
import 'package:drift/drift.dart' hide isNull, isNotNull;

File: apps/mobile/test/core/database/sync_queue_dao_test.dart
import 'package:drift/drift.dart' hide isNull, isNotNull;

File: apps/mobile/test/core/database/database_test.dart
import 'package:drift/drift.dart' hide isNull, isNotNull;

File: apps/mobile/test/core/database/weather_dao_test.dart
import 'package:drift/drift.dart' hide isNull, isNotNull;

File: apps/mobile/sahool_field_app/test/unit/features/tasks/tasks_repo_test.dart
import 'package:drift/drift.dart' hide isNotNull, isNull;
```

### Run Flutter Analyze
```bash
cd apps/mobile/sahool_field_app
flutter analyze
```

Expected: No errors related to `isNull` or `isNotNull` naming conflicts.

### Run Tests
```bash
cd apps/mobile/sahool_field_app
flutter test
```

Expected: All tests should run successfully without import conflicts.

## ملاحظات إضافية (Additional Notes)

- ✅ No logic changes, only import conflict resolution
- ✅ Solution is compatible with Dart 3.x and Flutter 3.27.x
- ✅ Only affects test files, not production code
- ✅ All 7 files verified to have the fix applied
- ✅ No other test files require this fix

## التاريخ (History)

- **2026-02-17**: Fixed all 7 test files in `apps/mobile/` directory
- **Commit**: 5e60a4b - "Fix drift/flutter_test naming conflicts by adding hide isNull, isNotNull to 6 test files"

## المراجع (References)

- Issue: Job #63928967693 unit test failures
- Drift Package: https://pub.dev/packages/drift
- Flutter Test Package: https://api.flutter.dev/flutter/flutter_test/flutter_test-library.html
- Dart Language Guide - Importing Libraries: https://dart.dev/guides/language/language-tour#importing-only-part-of-a-library
