# Changelog - SAHOOL Field App

All notable changes to the SAHOOL Field mobile application.

## [16.2.0] - 2026-02-11 - Mobile Sync Engine Improvements 🔄

### 🔄 Sync Engine Enhancements

#### Endpoint Validation
- **Empty endpoint detection** - Prevents crashes from malformed sync data
- **Format validation** - Validates API endpoint structure before processing
- **Error logging** - Invalid items logged with `outbox_invalid_endpoint` type
- **Graceful degradation** - Failed items marked and skipped without crashing

#### Network Configuration
- **Extended timeouts for mobile** - Connection: 60s, Send/Receive: 90s
- **forMobileSync() factory** - Optimized configuration for poor connectivity
- **Increased retry attempts** - Up to 5 retries with exponential backoff
- **Max backoff delay** - Up to 5 minutes for connection recovery
- **Rate limiting** - 30 requests/minute per endpoint

#### Sync Priority System
- **Priority-based ordering** - Critical (30) > High (20) > Normal (10) > Low (0)
- **Scheduled sync support** - `scheduled_at` field for delayed operations
- **Error tracking** - `last_error` field captures sync failures
- **Batch processing** - 50 items per batch for optimal performance

### 🗄️ Database Improvements

#### Migration V5
- **migration_history table** - Full audit trail of all schema changes
- **fields table enhancements**:
  - `last_sync_at` - Track last successful sync timestamp
  - `sync_error` - Store detailed error messages
  - `sync_attempts` - Counter for retry logic
- **outbox table enhancements**:
  - `sync_priority` - Priority-based sync ordering (0-30)
  - `scheduled_at` - Delayed sync support
  - `last_error` - Error message storage
- **Performance indices** - Optimized lookups for priority and scheduling

### 🛡️ Build & Release Fixes

#### ProGuard Configuration
- **flutter_local_notifications** - Prevents crashes in release builds
- **mobile_scanner** - QR/Barcode scanning code preservation
- **Google ML Kit Vision** - Computer vision library rules
- **Android compatibility** - NotificationCompat rules added

### 📚 Documentation

#### New Documentation Files
- **MOBILE_SYNC_API.md** - Complete API contract specification
  - Base URLs for production/staging/development
  - Required headers (Authorization, X-Tenant-ID, X-Device-ID)
  - Timeout recommendations for mobile devices
  - Rate limiting configuration
- **SETUP.md** - Comprehensive setup guide
  - Prerequisites and installation steps
  - Build instructions for debug and release
  - Common issues and solutions
  - Security checklist
- **MOBILE_INTEGRATION_FIX_SUMMARY.md** - Detailed fix documentation
- **Integration test templates** - 11 test groups covering all sync scenarios

### 🧪 Testing Infrastructure

#### Integration Tests (mobile_sync_test.dart)
- **Endpoint validation tests** - Empty and malformed endpoint handling
- **Network timeout tests** - Verify extended mobile timeouts
- **Conflict resolution tests** - 409 status code handling
- **Rate limiting tests** - 30 requests/minute enforcement
- **Exponential backoff tests** - Retry delay verification
- **Batch processing tests** - 10+ items batch handling
- **Offline recovery tests** - Outbox processing after reconnection
- **Sync health checks** - Status monitoring and error tracking

### ⚙️ Environment Configuration

#### New Environment Variables
- `CONNECT_TIMEOUT_SECONDS` - Mobile API connection timeout (default: 60)
- `SEND_TIMEOUT_SECONDS` - Large batch send timeout (default: 90)
- `RECEIVE_TIMEOUT_SECONDS` - Response receive timeout (default: 90)
- `SYNC_INTERVAL_SECONDS` - Foreground sync interval (default: 30)
- `BG_SYNC_INTERVAL_MINUTES` - Background sync interval (default: 15)
- `MAX_RETRY_COUNT` - Failed sync retry attempts (default: 5)
- `OUTBOX_BATCH_SIZE` - Bulk sync batch size (default: 50)
- `ENABLE_OFFLINE_MODE` - Offline-first operation (default: true)
- `ENABLE_BACKGROUND_SYNC` - Background synchronization (default: true)

### 📊 Impact Summary

- **Improved reliability** - Endpoint validation prevents crashes
- **Better connectivity** - Extended timeouts for rural/low-connectivity areas
- **Production-ready** - ProGuard rules ensure release build stability
- **Comprehensive testing** - 11 test groups with bilingual test names
- **Full documentation** - API contract, setup guide, and troubleshooting

### 🔜 Remaining Work (Out of Scope)

- Generate `pubspec.lock` - Requires Flutter SDK in CI/CD environment
- Backend sync endpoints - Implementation per API contract specification
- Certificate pinning - Replace placeholder fingerprints before production

---

## [16.1.0] - 2024-12-22 - Performance & Compatibility Release 🚀

### ⚡ Performance Improvements

#### Local Fonts Migration

- **Removed `google_fonts` dependency** - No more runtime font downloads
- **Bundled IBM Plex Sans Arabic fonts** (7 weights: 100-700)
- **Faster app startup** - Fonts load instantly from assets
- **Reduced APK size** - Saves ~6MB by eliminating font download code
- **Better offline support** - Fonts always available

#### APK Size Optimization

- **APK Split by ABI** - Separate APKs for arm64-v8a, armeabi-v7a, x86_64
- **Universal APK option** - For Play Store distribution
- **Expected size reduction** - ~15-20% smaller downloads for users

### 🔧 Build System Improvements

#### build.yaml Configuration

- Added `build.yaml` for proper code generation
- Configured `json_serializable`, `freezed`, and `drift_dev` builders
- Excluded test files from code generation
- Prevents unnecessary regeneration cycles

#### Gradle Configuration

- **minSdk raised to 23** - Required by `camera_android_camerax`
- **compileSdk/targetSdk 36** - Latest Android API
- **Java/Kotlin 17** - Modern toolchain
- **Core library desugaring** - Java 8+ APIs on older devices

### 🛠️ Dependency Fixes

#### Dart 3.6.0 Compatibility

- **Flutter 3.27.1** with Dart SDK 3.6.0
- **SDK constraint**: `>=3.2.0 <4.0.0`
- **freezed**: Pinned to 2.5.8 (last Dart 3.6.0 compatible version)
- **build_runner**: 2.4.13 (compatible with analyzer 7.x)

#### Removed Dependencies

- **mockito** - Removed due to analyzer 7.x incompatibility
  - Version 5.4.5: Uses internal `InterfaceElementImpl` (broken in analyzer 7.x)
  - Version 5.4.6+: Requires Dart 3.7.0+
  - Tests now use manual mocks where needed
- **google_fonts** - Replaced with local font assets

### 📱 Theme System Updates

#### IBM Plex Sans Arabic Integration

- Updated all theme files to use local font family
- Consistent font weights across themes:
  - Display/Body: 400 (Regular)
  - Headlines/Titles: 500-600 (Medium/SemiBold)
  - Labels: 500 (Medium)

#### Files Updated

- `lib/core/config/theme.dart`
- `lib/core/theme/sahool_theme.dart`
- `lib/core/theme/sahool_pro_theme.dart`

### 📊 Technical Details

#### Commits in This Release

```
3d054ae perf(mobile): Replace google_fonts with local IBM Plex Sans Arabic
6d3e3ef feat(mobile): Add build.yaml and APK split configuration
785cc13 fix(android): Set minSdk to 23 for camera library compatibility
970d0aa fix(test): Remove mockito imports from test files
8615607 fix(deps): Remove mockito - incompatible with analyzer 7.x
766a808 chore: Standardize Flutter 3.27.1 across all workflows
845e5de fix(deps): Revert to Dart 3.6.0 compatible versions
```

#### Compatibility Matrix

| Package            | Version | Notes                   |
| ------------------ | ------- | ----------------------- |
| Flutter            | 3.27.1  | Dart 3.6.0              |
| freezed            | 2.5.8   | Last 2.x for Dart 3.6.0 |
| freezed_annotation | ^2.4.4  | Compatible              |
| build_runner       | 2.4.13  | Compatible              |
| drift              | ^2.24.0 | Offline database        |
| drift_dev          | ^2.24.0 | Code generation         |

---

## [16.0.0] - Golden Release 🏆

### ✨ New Features

#### Smart Daily Brief

- **DailyBriefWidget**: Personalized morning/evening briefing
- Weather-based recommendations
- Priority task highlighting
- Quick action shortcuts for common operations

#### Smart Alerts Center

- **SmartAlertsCenter**: Real-time alerts from IoT sensors
- Severity-based alert categorization (Critical, Warning, Info)
- Actionable recommendations with one-tap actions
- Support for irrigation, weather, NDVI, sensor, task, and pest alerts

#### Push Notifications

- **Firebase Cloud Messaging (FCM)** integration
- Background and foreground notification handling
- Topic-based subscriptions (user, tenant, all_users)
- Customizable notification channels (Android)
- **Notification Settings**: Per-type toggles, quiet hours, sound/vibration control

### 🔐 Security Improvements

#### Authentication

- **AuthService**: Complete auth flow with automatic token refresh
- **SecureStorageService**: Encrypted token storage using flutter_secure_storage
- **BiometricService**: Fingerprint and Face ID authentication
- **AuthInterceptor**: Dio interceptor with 401 handling and request queuing

### ⚡ Performance Optimizations

#### Image Caching

- **SahoolImageCacheManager**: LRU-based image caching
- Configurable cache size limits
- Background preloading support

#### List Optimization

- **SahoolOptimizedListView**: Lazy loading with pagination
- **SahoolOptimizedGridView**: Memory-efficient grid rendering
- RepaintBoundary optimization for smooth scrolling

#### Memory Management

- **MemoryManager**: Memory pressure monitoring
- Automatic cache cleanup on low memory
- Image cache size configuration

#### Network Caching

- **NetworkCache**: API response caching with TTL
- Offline fallback support
- Pattern-based cache invalidation

### 🛠️ Developer Experience

#### Testing Infrastructure

- Comprehensive test helpers and utilities
- Mock providers for Riverpod testing
- Test fixtures with sample data
- Integration tests for auth flow, offline sync, and notifications

#### Code Quality

- Enhanced lint rules (80+ rules in analysis_options.yaml)
- Structured logging with AppLogger
- Error boundaries for graceful error handling
- Loading state widgets for consistent UX

#### CI/CD

- GitHub Actions workflow for mobile builds
- Automated analysis, testing, and APK generation
- Flutter version pinning for reproducible builds

### 📁 File Structure

```
lib/
├── core/
│   ├── auth/
│   │   ├── auth_service.dart
│   │   ├── biometric_service.dart
│   │   └── secure_storage_service.dart
│   ├── http/
│   │   └── auth_interceptor.dart
│   ├── notifications/
│   │   ├── push_notification_service.dart
│   │   ├── notification_settings.dart
│   │   └── notifications.dart
│   ├── performance/
│   │   ├── image_cache_manager.dart
│   │   ├── memory_manager.dart
│   │   ├── network_cache.dart
│   │   ├── optimized_list.dart
│   │   └── performance.dart
│   ├── widgets/
│   │   ├── error_boundary.dart
│   │   ├── loading_states.dart
│   │   └── empty_states.dart
│   └── utils/
│       └── app_logger.dart
├── features/
│   ├── daily_brief/
│   │   └── presentation/
│   │       ├── widgets/daily_brief_widget.dart
│   │       └── providers/daily_brief_provider.dart
│   └── smart_alerts/
│       └── presentation/
│           ├── widgets/smart_alerts_center.dart
│           └── providers/smart_alerts_provider.dart
test/
├── helpers/
│   └── test_helpers.dart
├── mocks/
│   └── mock_providers.dart
├── fixtures/
│   └── test_data.dart
├── unit/
│   └── core/
│       ├── env_config_test.dart
│       └── app_logger_test.dart
├── widget/
│   └── core/
│       ├── empty_states_test.dart
│       └── loading_states_test.dart
└── integration/
    ├── auth_flow_test.dart
    ├── offline_sync_test.dart
    └── notification_test.dart
```

### 📊 Statistics

- **New Files**: 25+
- **Lines of Code Added**: 5,500+
- **Test Coverage Improvement**: From ~5% to ~30%
- **Lint Rules**: 80+

### 🔧 Dependencies Added

```yaml
# Security
flutter_secure_storage: ^9.0.0
local_auth: ^2.1.6

# Notifications
firebase_messaging: ^14.7.0
flutter_local_notifications: ^16.0.0

# Caching
flutter_cache_manager: ^3.3.0
```

---

## [15.1.0] - Previous Release

- Initial offline-first architecture
- Basic field and task management
- IoT sensor integration
- Map functionality with offline tiles

---

© 2024 SAHOOL - Smart Agriculture Solutions
