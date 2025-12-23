# SAHOOL Field App - Project Structure
# هيكلة مشروع تطبيق ساهول الميداني

## Architecture Overview | نظرة عامة على الهيكلة

```
┌─────────────────────────────────────────────────────────────────┐
│                        SAHOOL Field App                          │
├─────────────────────────────────────────────────────────────────┤
│  Presentation Layer (UI)                                         │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Screens │ Widgets │ Providers (Riverpod)                   │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Domain Layer (Business Logic)                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Entities │ Use Cases │ Repository Interfaces               │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Models │ Repositories │ Data Sources (Local/Remote)        │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Core Layer (Shared)                                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Services │ Utils │ Theme │ Constants │ Extensions          │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure | هيكل المجلدات

```
lib/
├── main.dart                          # Entry point | نقطة البداية
├── app.dart                           # App configuration | إعدادات التطبيق
│
├── core/                              # Shared functionality | الوظائف المشتركة
│   ├── auth/                          # Authentication services
│   │   ├── auth_service.dart
│   │   ├── biometric_service.dart
│   │   └── secure_storage_service.dart
│   │
│   ├── config/                        # App configuration
│   │   ├── env_config.dart
│   │   ├── app_config.dart
│   │   └── theme.dart
│   │
│   ├── constants/                     # App constants
│   │   ├── api_constants.dart
│   │   ├── app_constants.dart
│   │   └── asset_constants.dart
│   │
│   ├── di/                            # Dependency injection
│   │   └── injection.dart
│   │
│   ├── extensions/                    # Dart extensions
│   │   ├── context_extensions.dart
│   │   ├── string_extensions.dart
│   │   └── date_extensions.dart
│   │
│   ├── http/                          # HTTP client & interceptors
│   │   ├── dio_client.dart
│   │   ├── auth_interceptor.dart
│   │   └── logging_interceptor.dart
│   │
│   ├── l10n/                          # Localization
│   │   ├── app_ar.arb
│   │   └── app_en.arb
│   │
│   ├── network/                       # Network utilities
│   │   ├── network_info.dart
│   │   └── connectivity_service.dart
│   │
│   ├── notifications/                 # Push notifications
│   │   ├── push_notification_service.dart
│   │   ├── notification_settings.dart
│   │   └── local_notification_service.dart
│   │
│   ├── performance/                   # Performance optimizations
│   │   ├── image_cache_manager.dart
│   │   ├── memory_manager.dart
│   │   ├── network_cache.dart
│   │   └── optimized_list.dart
│   │
│   ├── providers/                     # Global Riverpod providers
│   │   ├── app_providers.dart
│   │   └── connectivity_provider.dart
│   │
│   ├── routes/                        # Navigation & routing
│   │   ├── app_router.dart
│   │   └── route_names.dart
│   │
│   ├── services/                      # Core services
│   │   ├── api_service.dart
│   │   ├── cache_service.dart
│   │   └── analytics_service.dart
│   │
│   ├── storage/                       # Local database (Drift)
│   │   ├── database.dart
│   │   ├── database.g.dart           # Generated
│   │   ├── converters/
│   │   │   └── geo_converter.dart
│   │   └── mixins/
│   │       └── database_mixin.dart
│   │
│   ├── sync/                          # Offline sync
│   │   ├── sync_service.dart
│   │   ├── sync_manager.dart
│   │   └── conflict_resolver.dart
│   │
│   ├── theme/                         # App theming
│   │   ├── sahool_theme.dart
│   │   ├── sahool_pro_theme.dart
│   │   ├── colors.dart
│   │   └── typography.dart
│   │
│   ├── utils/                         # Utilities
│   │   ├── app_logger.dart
│   │   ├── date_utils.dart
│   │   ├── validators.dart
│   │   └── formatters.dart
│   │
│   └── widgets/                       # Shared widgets
│       ├── buttons/
│       │   ├── primary_button.dart
│       │   └── icon_button.dart
│       ├── cards/
│       │   └── info_card.dart
│       ├── dialogs/
│       │   ├── confirm_dialog.dart
│       │   └── loading_dialog.dart
│       ├── inputs/
│       │   ├── text_field.dart
│       │   └── dropdown_field.dart
│       ├── loading/
│       │   ├── loading_indicator.dart
│       │   └── shimmer_loading.dart
│       ├── empty_states/
│       │   └── empty_state_widget.dart
│       └── error_boundary.dart
│
└── features/                          # Feature modules | الميزات
    │
    ├── auth/                          # Authentication feature
    │   ├── data/
    │   │   ├── models/
    │   │   │   ├── user_model.dart
    │   │   │   └── auth_response.dart
    │   │   ├── datasources/
    │   │   │   ├── auth_local_datasource.dart
    │   │   │   └── auth_remote_datasource.dart
    │   │   └── repositories/
    │   │       └── auth_repository_impl.dart
    │   ├── domain/
    │   │   ├── entities/
    │   │   │   └── user.dart
    │   │   ├── repositories/
    │   │   │   └── auth_repository.dart
    │   │   └── usecases/
    │   │       ├── login_usecase.dart
    │   │       ├── logout_usecase.dart
    │   │       └── register_usecase.dart
    │   └── presentation/
    │       ├── providers/
    │       │   └── auth_provider.dart
    │       ├── screens/
    │       │   ├── login_screen.dart
    │       │   └── register_screen.dart
    │       └── widgets/
    │           ├── login_form.dart
    │           └── social_login_buttons.dart
    │
    ├── field/                         # Field management
    │   ├── data/
    │   │   ├── models/
    │   │   │   └── field_model.dart
    │   │   ├── datasources/
    │   │   │   ├── field_local_datasource.dart
    │   │   │   └── field_remote_datasource.dart
    │   │   └── repositories/
    │   │       └── field_repository_impl.dart
    │   ├── domain/
    │   │   ├── entities/
    │   │   │   └── field.dart
    │   │   ├── repositories/
    │   │   │   └── field_repository.dart
    │   │   └── usecases/
    │   │       ├── get_fields_usecase.dart
    │   │       ├── create_field_usecase.dart
    │   │       └── update_field_usecase.dart
    │   └── presentation/
    │       ├── providers/
    │       │   └── field_provider.dart
    │       ├── screens/
    │       │   ├── fields_list_screen.dart
    │       │   └── field_detail_screen.dart
    │       └── widgets/
    │           ├── field_card.dart
    │           └── field_map_preview.dart
    │
    ├── tasks/                         # Task management
    │   ├── data/
    │   ├── domain/
    │   └── presentation/
    │
    ├── weather/                       # Weather feature
    │   ├── data/
    │   ├── domain/
    │   └── presentation/
    │
    ├── iot/                           # IoT sensors
    │   ├── data/
    │   ├── domain/
    │   └── presentation/
    │
    ├── maps/                          # Maps & GIS
    │   ├── data/
    │   ├── domain/
    │   └── presentation/
    │
    ├── analytics/                     # Analytics & reports
    │   ├── data/
    │   ├── domain/
    │   └── presentation/
    │
    ├── notifications/                 # Notification center
    │   ├── data/
    │   ├── domain/
    │   └── presentation/
    │
    ├── settings/                      # App settings
    │   └── presentation/
    │
    └── profile/                       # User profile
        ├── data/
        ├── domain/
        └── presentation/
```

---

## Feature Module Structure | هيكل الميزة

كل ميزة تتبع نمط Clean Architecture:

```
feature_name/
├── data/                              # Data Layer | طبقة البيانات
│   ├── models/                        # Data models (JSON serializable)
│   │   └── feature_model.dart
│   ├── datasources/                   # Data sources
│   │   ├── feature_local_datasource.dart    # Local (Drift/SharedPrefs)
│   │   └── feature_remote_datasource.dart   # Remote (API)
│   └── repositories/                  # Repository implementations
│       └── feature_repository_impl.dart
│
├── domain/                            # Domain Layer | طبقة المنطق
│   ├── entities/                      # Business entities (pure Dart)
│   │   └── feature_entity.dart
│   ├── repositories/                  # Repository interfaces
│   │   └── feature_repository.dart
│   └── usecases/                      # Business logic
│       ├── get_feature_usecase.dart
│       └── update_feature_usecase.dart
│
└── presentation/                      # Presentation Layer | طبقة العرض
    ├── providers/                     # Riverpod providers
    │   └── feature_provider.dart
    ├── screens/                       # Full screens
    │   └── feature_screen.dart
    └── widgets/                       # Feature-specific widgets
        └── feature_widget.dart
```

---

## Naming Conventions | اصطلاحات التسمية

### Files | الملفات
```
# Models
user_model.dart              # Data model
user.dart                    # Entity

# Repositories
auth_repository.dart         # Interface
auth_repository_impl.dart    # Implementation

# Providers
auth_provider.dart           # Riverpod provider

# Screens
login_screen.dart            # Full screen

# Widgets
login_form.dart              # Reusable widget
```

### Classes | الكلاسات
```dart
// Models
class UserModel { }

// Entities
class User { }

// Repositories
abstract class AuthRepository { }
class AuthRepositoryImpl implements AuthRepository { }

// Providers
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>(...);

// Screens
class LoginScreen extends ConsumerWidget { }

// Widgets
class LoginForm extends StatelessWidget { }
```

---

## Import Order | ترتيب الاستيرادات

```dart
// 1. Dart imports
import 'dart:async';
import 'dart:convert';

// 2. Flutter imports
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// 3. Package imports (alphabetical)
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

// 4. Project imports - Core
import 'package:sahool_field_app/core/config/env_config.dart';
import 'package:sahool_field_app/core/utils/app_logger.dart';

// 5. Project imports - Features
import 'package:sahool_field_app/features/auth/domain/entities/user.dart';
import 'package:sahool_field_app/features/auth/presentation/providers/auth_provider.dart';

// 6. Relative imports (same feature only)
import '../widgets/login_form.dart';
```

---

## State Management | إدارة الحالة

Using **Riverpod** for state management:

```dart
// Provider types used:
// - Provider: Read-only values
// - StateProvider: Simple mutable state
// - StateNotifierProvider: Complex state with logic
// - FutureProvider: Async data
// - StreamProvider: Real-time data

// Example:
final fieldsProvider = StateNotifierProvider<FieldsNotifier, AsyncValue<List<Field>>>((ref) {
  return FieldsNotifier(ref.watch(fieldRepositoryProvider));
});
```

---

## Offline-First Architecture | بنية العمل بدون اتصال

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Repository Layer                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  1. Try local cache first                               ││
│  │  2. If online, sync with server                         ││
│  │  3. Queue offline changes in Outbox                     ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│   Local DataSource   │    │  Remote DataSource   │
│   (Drift SQLite)     │    │  (REST API + Dio)    │
└──────────────────────┘    └──────────────────────┘
              │                           │
              ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│   SQLite Database    │    │   SAHOOL API Server  │
│   (sahool_field.db)  │    │   (api.sahool.app)   │
└──────────────────────┘    └──────────────────────┘
```

---

## Build & Code Generation | البناء وتوليد الكود

```bash
# Generate Drift, Freezed, JSON Serializable files
dart run build_runner build --delete-conflicting-outputs

# Watch mode (development)
dart run build_runner watch --delete-conflicting-outputs

# Clean generated files
dart run build_runner clean
```

### Generated Files | الملفات المولدة
```
*.g.dart           # JSON serializable, Drift
*.freezed.dart     # Freezed models
```

---

## Testing Structure | هيكل الاختبارات

```
test/
├── unit/                              # Unit tests
│   ├── core/
│   │   └── utils/
│   │       └── validators_test.dart
│   └── features/
│       └── auth/
│           ├── data/
│           │   └── auth_repository_impl_test.dart
│           └── domain/
│               └── usecases/
│                   └── login_usecase_test.dart
│
├── widget/                            # Widget tests
│   └── features/
│       └── auth/
│           └── presentation/
│               └── widgets/
│                   └── login_form_test.dart
│
├── integration/                       # Integration tests
│   ├── auth_flow_test.dart
│   └── offline_sync_test.dart
│
├── fixtures/                          # Test data
│   └── test_data.dart
│
├── mocks/                             # Mock implementations
│   └── mock_providers.dart
│
└── helpers/                           # Test utilities
    └── test_helpers.dart
```

---

## Key Technologies | التقنيات الرئيسية

| Category | Technology | Purpose |
|----------|------------|---------|
| State Management | Riverpod | Reactive state |
| Database | Drift (SQLite) | Offline storage |
| Networking | Dio | HTTP client |
| Navigation | GoRouter | Declarative routing |
| Maps | flutter_map | GIS & mapping |
| Code Gen | Freezed, JSON Serializable | Immutable models |
| Testing | flutter_test | Unit & widget tests |

---

## Version Information | معلومات الإصدار

- **Flutter**: 3.27.1
- **Dart SDK**: 3.6.0
- **Min Android SDK**: 23 (Android 6.0)
- **Target Android SDK**: 36

---

© 2024 SAHOOL - Smart Agriculture Solutions
