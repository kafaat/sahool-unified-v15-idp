# Test Coverage Documentation

## Overview

This document describes the test coverage for the SAHOOL Field App mobile application.
The tests are organized into unit tests, widget tests, and integration tests.

## Test Directory Structure

```
test/
├── fixtures/              # Sample test data
│   ├── sample_fields.dart
│   └── sample_tasks.dart
├── helpers/               # Test utilities
│   └── test_helpers.dart
├── mocks/                 # Mock implementations
│   ├── mocks.dart         # Export file for all mocks
│   ├── mock_app_database.dart
│   ├── mock_auth_service.dart
│   ├── mock_network_status.dart
│   ├── mock_providers.dart
│   └── mock_sync_engine.dart
├── unit/                  # Unit tests
│   ├── auth/
│   │   └── auth_service_test.dart
│   ├── core/
│   │   ├── error_handling_test.dart
│   │   └── sync_engine_test.dart
│   ├── features/
│   │   ├── fields/
│   │   │   └── fields_repo_test.dart
│   │   └── tasks/
│   │       └── tasks_repo_test.dart
│   ├── http/
│   │   └── api_client_test.dart
│   ├── network/
│   │   ├── api_result_test.dart
│   │   └── dio_error_handler_test.dart
│   └── equipment_models_test.dart
└── widget/                # Widget tests
    ├── field_card_test.dart
    ├── home_screen_test.dart
    ├── login_screen_test.dart
    └── weather_widget_test.dart
```

## Test Categories

### 1. Unit Tests (`test/unit/`)

#### Authentication (`auth/`)
- **auth_service_test.dart**: Tests for AuthService
  - Login/logout functionality
  - Token management (getTokenExpiry, validateSession)
  - Biometric authentication
  - User data persistence
  - AuthStateNotifier state management

#### Core (`core/`)
- **error_handling_test.dart**: Tests for error handling
  - Exception handling
  - Error message localization (Arabic/English)
  - ErrorHandler utility

- **sync_engine_test.dart**: Tests for SyncEngine
  - Initialization and lifecycle
  - Sync status management
  - Backoff status tracking
  - Statistics and health checks
  - SyncResult and SyncStatistics models

#### Features

##### Fields (`features/fields/`)
- **fields_repo_test.dart**: Tests for FieldsRepo
  - CRUD operations (create, read, update, delete)
  - Offline-first data persistence
  - Server refresh with network status check
  - GeoJSON handling
  - Outbox queue management

##### Tasks (`features/tasks/`)
- **tasks_repo_test.dart**: Tests for TasksRepo
  - Task retrieval (all, by field, pending)
  - Task creation with validation
  - Task completion (offline-first)
  - Status updates
  - Outbox queue management

#### HTTP (`http/`)
- **api_client_test.dart**: Tests for API client
  - Request/response handling
  - Error handling
  - Authentication headers

#### Network (`network/`)
- **api_result_test.dart**: Tests for ApiResult
  - Success/failure states
  - Type safety

- **dio_error_handler_test.dart**: Tests for DioErrorHandler
  - HTTP error mapping
  - Network error handling
  - Timeout handling

#### Models
- **equipment_models_test.dart**: Tests for equipment models
  - Serialization/deserialization
  - Validation

### 2. Widget Tests (`test/widget/`)

- **login_screen_test.dart**: Login screen widget tests
  - Form validation
  - Input handling
  - Login button states

- **home_screen_test.dart**: Home screen widget tests
  - Layout rendering
  - Navigation

- **field_card_test.dart**: Field card widget tests
  - Data display
  - NDVI indicator

- **weather_widget_test.dart**: Weather widget tests
  - Data display
  - Loading states

## Mock Classes

### MockAppDatabase
Full in-memory implementation of AppDatabase for testing.
- Task operations (CRUD, status updates)
- Field operations (CRUD, boundary updates)
- Outbox management
- Sync log operations
- Health checks

### MockAuthService
Mock implementation of AuthService.
- Configurable login success/failure
- Token management
- User data handling

### MockNetworkStatus
Mock implementation of NetworkStatus.
- Configurable online/offline status
- Stream-based status updates

### MockSyncEngine
Mock implementation of SyncEngine.
- Sync status simulation
- Backoff status tracking
- Rate limit status
- Statistics

## Test Fixtures

### SampleTasks
Factory methods for creating test task data:
- `createPendingTask()`: Task with status 'open'
- `createInProgressTask()`: Task with status 'in_progress'
- `createCompletedTask()`: Task with status 'done'
- `createOverdueTask()`: Task past due date
- `createUnsyncedTask()`: Task not yet synced

### SampleFields
Factory methods for creating test field data:
- `createWheatField()`: Wheat crop field
- `createDatePalmField()`: Date palm field
- `createVegetableField()`: Vegetable field
- `createFallowField()`: Fallow/inactive field
- `createUnsyncedField()`: Field not yet synced
- `createDeletedField()`: Soft-deleted field

## Running Tests

```bash
# Run all tests
flutter test

# Run with coverage
flutter test --coverage

# Run specific test file
flutter test test/unit/auth/auth_service_test.dart

# Run with verbose output
flutter test --reporter expanded
```

## Coverage Targets

| Category | Target | Description |
|----------|--------|-------------|
| Core Services | 80% | Authentication, sync, error handling |
| Repositories | 70% | Data access layer |
| Models | 90% | Data models and serialization |
| Widgets | 60% | UI components |
| Utils | 70% | Utility functions |

## Test Best Practices

### 1. Arrange-Act-Assert Pattern
All tests follow the AAA pattern for clarity.

### 2. Bilingual Test Descriptions
Tests include Arabic comments where relevant for localization context.

### 3. Offline-First Testing
Tests verify both online and offline scenarios.

### 4. Mock Isolation
Each test uses fresh mock instances to prevent state leakage.

### 5. Error Case Coverage
Tests include both success and failure scenarios.

## Known Limitations

1. **Flutter SDK Required**: Tests require Flutter SDK for execution
2. **No Integration Tests in Unit Directory**: Integration tests are separate
3. **Database Mocking**: Uses in-memory mock, not actual Drift database

## Future Improvements

1. Add more widget tests for new screens
2. Implement golden tests for UI consistency
3. Add performance benchmarks
4. Expand integration test coverage
5. Add accessibility tests

---

Last Updated: 2026-01-24
