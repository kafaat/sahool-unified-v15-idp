# SAHOOL Integration Tests

# اختبارات التكامل لتطبيق سهول

Comprehensive end-to-end integration tests for the SAHOOL Flutter mobile application.

## Overview

This directory contains integration tests that verify the complete functionality of the SAHOOL mobile app, including:

- User authentication and session management
- Field management (CRUD operations)
- Satellite imagery viewing and analysis
- Variable Rate Application (VRA) prescriptions
- Inventory management
- Offline mode functionality
- Arabic UI/UX elements

## Test Structure

```
integration_test/
├── app_test.dart                    # Main integration tests
├── features/                        # Feature-specific tests
│   ├── auth_test.dart              # Authentication tests
│   ├── fields_test.dart            # Field management tests
│   ├── satellite_test.dart         # Satellite imagery tests
│   ├── vra_test.dart              # VRA prescription tests
│   └── inventory_test.dart         # Inventory management tests
├── helpers/                         # Test helper functions
│   └── test_helpers.dart           # Common test utilities
├── fixtures/                        # Test data and fixtures
│   └── test_data.dart              # Mock data for tests
├── run_tests.sh                     # Test runner script
└── README.md                        # This file
```

## Prerequisites

- Flutter SDK (3.27.x or later)
- Dart SDK (3.6.0 or later)
- Android Studio / Xcode (for device/emulator)
- Connected device or running emulator

## Installation

1. Ensure Flutter is installed and in your PATH:

```bash
flutter --version
```

2. Install dependencies:

```bash
cd /path/to/sahool-unified-v15-idp/apps/mobile
flutter pub get
```

3. Make the test runner executable:

```bash
chmod +x integration_test/run_tests.sh
```

## Running Tests

### Option 1: Using the Test Runner Script (Recommended)

**Run all tests:**

```bash
./integration_test/run_tests.sh --all
```

**Run all tests with emulator and report:**

```bash
./integration_test/run_tests.sh --all --emulator --report
```

**Run specific test file:**

```bash
./integration_test/run_tests.sh --test integration_test/features/auth_test.dart
```

**Run on specific device:**

```bash
./integration_test/run_tests.sh --all --device emulator-5554
```

**Show help:**

```bash
./integration_test/run_tests.sh --help
```

### Option 2: Using Flutter Command Directly

**Run all integration tests:**

```bash
flutter test integration_test/
```

**Run specific test file:**

```bash
flutter test integration_test/features/auth_test.dart
```

**Run on specific device:**

```bash
flutter test -d emulator-5554 integration_test/app_test.dart
```

### Option 3: Using Flutter Driver (for advanced scenarios)

```bash
flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/app_test.dart
```

## Test Coverage

### 1. Main App Tests (`app_test.dart`)

- ✅ App launch and initialization
- ✅ Arabic RTL layout verification
- ✅ Login/logout flows
- ✅ Bottom navigation
- ✅ Field CRUD operations
- ✅ Offline mode
- ✅ Quick actions
- ✅ Search functionality
- ✅ Performance tests
- ✅ Accessibility tests

### 2. Authentication Tests (`features/auth_test.dart`)

- ✅ Login with email/phone
- ✅ Login validation (invalid credentials)
- ✅ Biometric authentication
- ✅ Password reset
- ✅ Token refresh
- ✅ Logout functionality
- ✅ Session persistence
- ✅ Security features

### 3. Fields Management Tests (`features/fields_test.dart`)

- ✅ View fields list
- ✅ Create new field
- ✅ Edit field details
- ✅ Delete field
- ✅ View field on map
- ✅ Field map drawing
- ✅ Search and filter fields
- ✅ Field statistics
- ✅ Offline field management

### 4. Satellite Imagery Tests (`features/satellite_test.dart`)

- ✅ View satellite imagery
- ✅ NDVI values and color scale
- ✅ Historical data timeline
- ✅ NDVI trend charts
- ✅ Export data (image, PDF, CSV)
- ✅ Cloud coverage indicator
- ✅ Image comparison
- ✅ Zoom and pan functionality
- ✅ Offline cached imagery

### 5. VRA Tests (`features/vra_test.dart`)

- ✅ View VRA prescriptions list
- ✅ Create prescription
- ✅ View zones on map
- ✅ Zone management
- ✅ Edit application rates
- ✅ Export prescription (PDF, Shapefile)
- ✅ Prescription status workflow
- ✅ Filter and sort prescriptions
- ✅ Offline prescription creation

### 6. Inventory Tests (`features/inventory_test.dart`)

- ✅ View inventory list
- ✅ Add stock movements (in/out)
- ✅ Low stock alerts
- ✅ Filter and search inventory
- ✅ Item details
- ✅ Add/edit/delete items
- ✅ Inventory statistics
- ✅ Barcode scanning
- ✅ Export reports
- ✅ Offline inventory management

## Test Data

Test data is defined in `fixtures/test_data.dart` and includes:

- **Test Users**: Valid/invalid credentials for different scenarios
- **Test Fields**: Sample field data with locations and polygons
- **Test Inventory**: Fertilizers, pesticides, seeds with quantities
- **Test VRA**: Sample prescriptions with zones
- **Test Satellite**: Mock imagery data with NDVI values
- **Arabic Strings**: UI element identifiers in Arabic

## Helper Functions

The `helpers/test_helpers.dart` file provides utilities for:

- **Authentication**: `login()`, `logout()`, biometric auth
- **Navigation**: `navigateToBottomNavItem()`, `navigateBack()`
- **Interactions**: `tapElement()`, `enterText()`, `scrollUntilVisible()`
- **Waiting**: `waitForElement()`, `pumpAndSettle()`
- **Assertions**: `verifyElementExists()`, `verifyTextExists()`
- **Screenshots**: `takeScreenshot()`, `captureOnFailure()`
- **Field Management**: `createField()`, `editField()`, `deleteField()`

## Screenshots

Screenshots are automatically captured during test execution:

- Location: `screenshots/integration/`
- Naming: `{test_name}_{timestamp}.png`
- Failures: Automatically captured on test failure
- Success: Configurable in `TestConfig.captureScreenshotsOnSuccess`

## Test Reports

HTML test reports are generated when using the `--report` flag:

- Location: `test_reports/`
- Format: HTML with Arabic RTL support
- Contents: Test summary, pass/fail counts, timestamps
- Screenshots: Linked from the report

## Configuration

Test configuration is in `fixtures/test_data.dart` (`TestConfig` class):

```dart
// Timeouts
static const Duration shortTimeout = Duration(seconds: 5);
static const Duration mediumTimeout = Duration(seconds: 10);
static const Duration longTimeout = Duration(seconds: 30);

// Screenshot settings
static const bool captureScreenshotsOnFailure = true;
static const bool captureScreenshotsOnSuccess = false;

// Test modes
static const bool useMockData = true;
static const bool enableNetworkStubbing = true;
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  integration_tests:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: "3.27.0"

      - name: Install dependencies
        run: flutter pub get
        working-directory: apps/mobile

      - name: Run integration tests
        run: ./integration_test/run_tests.sh --all --report
        working-directory: apps/mobile

      - name: Upload test reports
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-reports
          path: apps/mobile/test_reports/

      - name: Upload screenshots
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: failure-screenshots
          path: apps/mobile/screenshots/
```

## Debugging Tests

### Enable Verbose Logging

```bash
flutter test --verbose integration_test/app_test.dart
```

### Run Specific Test

```bash
flutter test integration_test/app_test.dart --name "Login with valid credentials"
```

### Keep App Running After Test

```bash
flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/app_test.dart \
  --keep-app-running
```

### View Test Output in Real-Time

```bash
flutter test integration_test/app_test.dart 2>&1 | tee test_output.log
```

## Troubleshooting

### Common Issues

**1. No devices found**

```bash
# Check connected devices
flutter devices

# Start an emulator
emulator -avd Pixel_4_API_30

# Or use the script
./integration_test/run_tests.sh --emulator
```

**2. Test timeout**

- Increase timeout in `TestConfig`
- Check device performance
- Verify network connectivity

**3. Element not found**

- Check Arabic text encoding
- Verify widget hierarchy
- Use `find.textContaining()` for partial matches

**4. Screenshot failures**

- Ensure directory exists: `mkdir -p screenshots/integration`
- Check write permissions
- Disable on web platform (not supported)

**5. Flaky tests**

- Add appropriate waits: `await helpers.wait(TestConfig.shortDelay)`
- Use `pumpAndSettle()` after interactions
- Check for animation completion

## Best Practices

1. **Use Test Helpers**: Leverage helper functions for consistency
2. **Meaningful Names**: Use descriptive test names in Arabic and English
3. **Independent Tests**: Each test should be self-contained
4. **Clean Up**: Use `tearDown()` for cleanup
5. **Assertions**: Always verify expected outcomes
6. **Screenshots**: Capture key states for debugging
7. **Arabic Support**: Test RTL layout and Arabic text rendering
8. **Offline Mode**: Test offline functionality thoroughly
9. **Performance**: Monitor test execution time
10. **Documentation**: Keep tests well-documented

## Contributing

When adding new tests:

1. Follow existing file structure
2. Use test helpers for common operations
3. Add test data to fixtures
4. Update this README
5. Ensure tests pass before committing
6. Add appropriate Arabic translations

## Resources

- [Flutter Integration Testing](https://docs.flutter.dev/testing/integration-tests)
- [flutter_test Package](https://api.flutter.dev/flutter/flutter_test/flutter_test-library.html)
- [integration_test Package](https://pub.dev/packages/integration_test)
- [SAHOOL Mobile App Documentation](../README.md)

## License

Copyright © 2025 SAHOOL. All rights reserved.

---

For questions or issues, contact the SAHOOL development team.
