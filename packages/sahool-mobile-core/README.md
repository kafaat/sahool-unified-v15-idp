# SAHOOL Mobile Core (sahool_mobile_core)

**Version**: 16.0.0 | **License**: Proprietary | **Owner**: KAFAAT

## Description

**English**: Shared Flutter package providing core infrastructure, feature modules, and UI components for all SAHOOL mobile applications. Built with an offline-first architecture, bilingual support (Arabic/English), and enterprise-grade security including SQLCipher encryption, certificate pinning, and biometric authentication.

**Arabic**: الحزمة الأساسية المشتركة لتطبيقات سهول الهاتف. توفر البنية التحتية الأساسية ووحدات الميزات ومكونات واجهة المستخدم لجميع تطبيقات سهول. مبنية بمعمارية تعمل بدون اتصال أولاً، ودعم ثنائي اللغة (عربي/إنجليزي)، وأمان على مستوى المؤسسات.

## Architecture

```
sahool_mobile_core/
├── lib/
│   ├── sahool_mobile_core.dart    # Package barrel export
│   ├── core/                      # 51 core infrastructure modules
│   │   ├── api/                   # API client & interceptors
│   │   ├── auth/                  # JWT, 2FA authentication
│   │   ├── database/              # Drift + SQLCipher encrypted storage
│   │   ├── http/                  # Dio client, retry, rate limiter
│   │   ├── offline/               # Offline-first sync engine
│   │   ├── security/              # Certificate pinning, device integrity
│   │   ├── sync/                  # Background sync (Workmanager)
│   │   └── ...                    # 44 more core modules
│   ├── features/                  # 59 feature modules
│   │   ├── field/                 # Core field operations
│   │   ├── irrigation/            # Irrigation management
│   │   ├── crop_health/           # Crop health monitoring
│   │   ├── ndvi/                  # NDVI analysis
│   │   ├── advisor/               # Agricultural advisory
│   │   ├── marketplace/           # Marketplace
│   │   └── ...                    # 53 more feature modules
│   ├── generated/                 # Auto-generated code
│   ├── l10n/                      # Localization (AR/EN)
│   └── services/                  # Service layer
├── test/                          # Unit & widget tests
├── pubspec.yaml                   # Package manifest
├── analysis_options.yaml          # Lint rules
├── build.yaml                     # Code generation config
└── import_sorter.yaml             # Import ordering config
```

## Core Modules (51)

| Module | Purpose |
|--------|---------|
| `accessibility` | Accessibility support & semantic labels |
| `ai` | On-device AI utilities |
| `analytics` | Usage analytics & event tracking |
| `animations` | Shared animation controllers & curves |
| `api` | API client, interceptors, request/response handling |
| `auth` | JWT authentication, 2FA, token management |
| `config` | App configuration & environment settings |
| `constants` | Application-wide constants |
| `contracts` | API contracts (generated from TypeScript) |
| `crash` | Crash reporting (Sentry integration) |
| `dashboard` | Dashboard widgets & utilities |
| `database` | Drift database with SQLCipher encryption |
| `deeplink` | Deep link routing & handling |
| `di` | Dependency injection setup |
| `domain` | Core domain models & entities |
| `error` | Error types & codes |
| `error_handling` | Global error handling & recovery |
| `feature_flags` | Feature flag management |
| `geo` | Geolocation, geofencing, coordinate utilities |
| `haptics` | Haptic feedback patterns |
| `http` | Dio HTTP client, retry logic, rate limiting |
| `iam` | Identity & access management |
| `l10n` | Localization utilities (Arabic/English) |
| `logging` | Structured logging |
| `map` | Map utilities & tile management |
| `maps` | Map widgets & layers (flutter_map) |
| `ml` | On-device ML inference |
| `motion` | Motion detection & gesture handling |
| `network` | Network connectivity monitoring |
| `notifications` | Push & local notification handling |
| `offline` | Offline-first sync engine & conflict resolution |
| `onboarding` | Onboarding flow utilities |
| `performance` | Performance monitoring & profiling |
| `persistence` | Key-value & secure storage |
| `providers` | Riverpod providers & state management |
| `rbac` | Role-based access control |
| `release` | Release management utilities |
| `routes` | Navigation routing & guards |
| `security` | Certificate pinning, device integrity, biometrics |
| `services` | Service layer abstractions |
| `state` | State management utilities |
| `storage` | Drift database tables & DAOs |
| `sync` | Background sync with Workmanager |
| `theme` | Theming, colors, typography (RTL-aware) |
| `ui` | Reusable UI components |
| `update` | App update & version management |
| `utils` | General utility functions |
| `validation` | Form & input validation |
| `voice` | Speech-to-text & TTS |
| `websocket` | Real-time WebSocket connection |
| `widgets` | Shared widget library |

## Feature Modules (59)

| Module | Purpose |
|--------|---------|
| `advisor` | Agricultural advisory recommendations |
| `ai_advisor` | AI-powered advisory assistant |
| `alerts` | Alert management & display |
| `analytics` | Analytics dashboards & reports |
| `astronomical` | Astronomical calculations |
| `astronomical_calendar` | Islamic calendar & prayer times |
| `auth` | Authentication screens & flows |
| `billing` | Billing & subscription management |
| `chat` | Real-time field chat |
| `community` | Community & social features |
| `crm` | Farmer CRM |
| `crop_health` | Crop health monitoring & diagnostics |
| `crops` | Crop management & variety selection |
| `daily_brief` | Daily farm briefing |
| `equipment` | Equipment tracking & maintenance |
| `field` | Core field operations & management |
| `field_hub` | Field operations hub |
| `field_scout` | Field scouting & observations |
| `fields` | Field listing & overview |
| `gamification` | Gamification & achievements |
| `gdd` | Growing Degree Days calculation |
| `home` | Home screen |
| `home_v16` | Home screen v16 redesign |
| `inventory` | Inventory management |
| `iot` | IoT device management & sensor data |
| `irrigation` | Irrigation scheduling & control |
| `lab` | Laboratory & soil test results |
| `main_layout` | App shell & navigation layout |
| `map_home` | Map-centric home view |
| `maps` | Map views & field visualization |
| `market` | Market prices & trends |
| `marketplace` | Agricultural marketplace |
| `ndvi` | NDVI vegetation analysis |
| `notifications` | Notification center |
| `onboarding` | User onboarding flow |
| `payment` | Payment processing |
| `pivot_irrigation` | Center pivot irrigation management |
| `polygon_editor` | Field boundary polygon editor |
| `profile` | User profile management |
| `profitability` | Farm profitability analysis |
| `reports` | Report generation & export |
| `research` | Research trials & experiments |
| `rotation` | Crop rotation planning |
| `satellite` | Satellite imagery viewer |
| `scanner` | QR/barcode scanning |
| `scouting` | Pest & disease scouting |
| `settings` | App settings & preferences |
| `shared` | Shared feature utilities |
| `smart_alerts` | AI-powered smart alerts |
| `splash` | Splash screen |
| `spray` | Spray operations & PHI tracking |
| `sync` | Sync status & management UI |
| `tasks` | Task management & scheduling |
| `terrain` | Terrain analysis & visualization |
| `virtual_sensors` | Virtual sensor computation |
| `vision` | Computer vision (pest/disease detection) |
| `vra` | Variable Rate Application maps |
| `wallet` | Digital wallet |
| `weather` | Weather forecasts & alerts |

## Installation

Add as a path dependency in your app's `pubspec.yaml`:

```yaml
dependencies:
  sahool_mobile_core:
    path: ../../packages/sahool-mobile-core
```

## Usage

```dart
// Import the full package
import 'package:sahool_mobile_core/sahool_mobile_core.dart';

// Or import specific modules
import 'package:sahool_mobile_core/core/auth/auth.dart';
import 'package:sahool_mobile_core/core/offline/offline.dart';
import 'package:sahool_mobile_core/core/security/security.dart';
import 'package:sahool_mobile_core/features/field/field.dart';
import 'package:sahool_mobile_core/features/irrigation/irrigation.dart';
import 'package:sahool_mobile_core/features/crop_health/crop_health.dart';
```

### Example: Using in a SAHOOL Mobile App

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sahool_mobile_core/sahool_mobile_core.dart';

void main() {
  runApp(
    const ProviderScope(
      child: SahoolFieldApp(),
    ),
  );
}

class SahoolFieldApp extends ConsumerWidget {
  const SahoolFieldApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      title: 'SAHOOL Field App',
      theme: SahoolTheme.light(),
      darkTheme: SahoolTheme.dark(),
      localizationsDelegates: SahoolL10n.delegates,
      supportedLocales: SahoolL10n.supportedLocales,
      home: const HomeScreen(),
    );
  }
}
```

## Development

```bash
# Run code generation
dart run build_runner build --delete-conflicting-outputs

# Run analyzer
flutter analyze

# Sort imports
dart run import_sorter:main

# Run tests
flutter test
```

## Tech Stack

- **Framework**: Flutter 3.27.x (Dart SDK >=3.2.0)
- **State Management**: Riverpod 2.6.x
- **Local Database**: Drift 2.24+ with SQLCipher (256-bit AES)
- **Networking**: Dio 5.x with certificate pinning
- **Maps**: flutter_map 8.1.x, latlong2
- **Background Sync**: Workmanager
