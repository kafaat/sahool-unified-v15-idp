# SAHOOL Unified App - Integration Tests

# اختبارات التكامل لتطبيق سهول الموحد

## Running Tests

```bash
# Run all integration tests on a connected device/emulator
flutter test integration_test/

# Run a specific test file
flutter test integration_test/app_test.dart

# Run with verbose output
flutter test integration_test/ --reporter expanded
```

## Test Categories

| Category | Description | الوصف |
|----------|-------------|-------|
| **App Launch** | Startup, rendering, RTL layout | بدء التشغيل والعرض والاتجاه |
| **Authentication** | Login, logout, session management | تسجيل الدخول والخروج وإدارة الجلسة |
| **Navigation** | Tab switching, screen routing | تبديل علامات التبويب والتوجيه |
| **Offline Mode** | Offline-first behavior, cached data | السلوك بدون اتصال والبيانات المخزنة |
| **Features** | Advisory, irrigation, NDVI, weather | الاستشارات والري والمؤشرات والطقس |

## Prerequisites

- Flutter SDK 3.27.x or later
- Connected Android/iOS device or running emulator
- `integration_test` SDK package in `pubspec.yaml` dev_dependencies

## Adding New Tests

1. Add test groups in `app_test.dart` or create feature-specific files (e.g., `fields_test.dart`)
2. Follow the bilingual comment pattern (English + Arabic)
3. Use `_TestSahoolApp` wrapper for consistent app setup
4. Mark TODO sections for tests that depend on unfinished screen wiring
