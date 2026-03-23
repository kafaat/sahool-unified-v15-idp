// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Core Dependency Injection Providers
// مزودات حقن التبعيات الأساسية
// ═══════════════════════════════════════════════════════════════════════════
//
// This file defines the base providers that sahool_mobile_core exposes.
// يُعرِّف هذا الملف المزودات الأساسية التي تُصدّرها حزمة النواة.
//
// Apps must override these providers in their ProviderScope.overrides
// to supply concrete implementations (database, sync engine, etc.).
// يجب على التطبيقات تجاوز هذه المزودات في ProviderScope.overrides
// لتوفير التنفيذات الفعلية (قاعدة البيانات، محرك المزامنة، إلخ).
//
// Example usage in main.dart / مثال الاستخدام في main.dart:
// ```dart
// runApp(
//   ProviderScope(
//     overrides: [
//       databaseProvider.overrideWithValue(database),
//       syncEngineProvider.overrideWithValue(syncEngine),
//       envConfigProvider.overrideWithValue(EnvConfig()),
//       crashReporterProvider.overrideWithValue(CrashReporter.instance),
//     ],
//     child: const SahoolApp(),
//   ),
// );
// ```
// ═══════════════════════════════════════════════════════════════════════════

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../storage/database.dart';
import '../sync/sync_engine.dart';
import '../auth/auth_service.dart';
import '../auth/secure_storage_service.dart';
import '../auth/token_manager.dart';
import '../auth/biometric_service.dart';
import '../config/env_config.dart';
import '../crash/crash_reporter.dart';
import '../http/api_client.dart';
import '../security/signing_key_service.dart';

// ─────────────────────────────────────────────────────────────────────────────
// DATABASE PROVIDER
// مزود قاعدة البيانات
// ─────────────────────────────────────────────────────────────────────────────

/// Local encrypted database (Drift + SQLCipher).
/// قاعدة البيانات المحلية المشفرة (Drift + SQLCipher).
///
/// Must be overridden by the host app with an initialized [AppDatabase].
/// يجب تجاوزه من التطبيق المضيف بنسخة مهيأة من [AppDatabase].
///
/// Override example:
/// ```dart
/// databaseProvider.overrideWithValue(AppDatabase(executor))
/// ```
final databaseProvider = Provider<AppDatabase>((ref) {
  throw UnimplementedError(
    'databaseProvider must be overridden in ProviderScope.overrides. '
    'يجب تجاوز مزود قاعدة البيانات في ProviderScope.overrides.',
  );
});

// ─────────────────────────────────────────────────────────────────────────────
// SYNC ENGINE PROVIDER
// مزود محرك المزامنة
// ─────────────────────────────────────────────────────────────────────────────

/// Offline-first sync engine with ETag support and exponential backoff.
/// محرك المزامنة للعمل بدون اتصال مع دعم ETag والتراجع الأسي.
///
/// Must be overridden by the host app with an initialized [SyncEngine].
/// يجب تجاوزه من التطبيق المضيف بنسخة مهيأة من [SyncEngine].
///
/// Override example:
/// ```dart
/// syncEngineProvider.overrideWithValue(SyncEngine(database: db))
/// ```
final syncEngineProvider = Provider<SyncEngine>((ref) {
  throw UnimplementedError(
    'syncEngineProvider must be overridden in ProviderScope.overrides. '
    'يجب تجاوز مزود محرك المزامنة في ProviderScope.overrides.',
  );
});

// ─────────────────────────────────────────────────────────────────────────────
// AUTH PROVIDER
// مزود المصادقة
// ─────────────────────────────────────────────────────────────────────────────

/// Authentication service with JWT refresh, biometric support, and session
/// management. Depends on [apiClientProvider], [tokenManagerProvider],
/// [secureStorageProvider], and [biometricServiceProvider].
/// خدمة المصادقة مع تجديد JWT، دعم البصمة، وإدارة الجلسات.
///
/// This provider resolves its dependencies from the container.
/// If [apiClientProvider] is unavailable it falls back to mock mode.
/// يستخدم هذا المزود التبعيات من الحاوية. في حال عدم توفر apiClient
/// يتراجع إلى وضع المحاكاة.
final coreAuthServiceProvider = Provider<AuthService>((ref) {
  final tokenManager = ref.read(tokenManagerProvider);
  final secureStorage = ref.read(secureStorageProvider);
  final biometricService = ref.read(biometricServiceProvider);

  try {
    final apiClient = ref.read(coreApiClientProvider);
    return AuthService(
      secureStorage: secureStorage,
      biometricService: biometricService,
      tokenManager: tokenManager,
      apiClient: apiClient,
    );
  } catch (_) {
    // Fallback without API client (mock/offline mode)
    // التراجع بدون عميل API (وضع المحاكاة/عدم الاتصال)
    return AuthService(
      secureStorage: secureStorage,
      biometricService: biometricService,
      tokenManager: tokenManager,
    );
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// ENV CONFIG PROVIDER
// مزود تكوين البيئة
// ─────────────────────────────────────────────────────────────────────────────

/// Application environment configuration.
/// تكوين بيئة التطبيق.
///
/// Provides the current [AppEnvironment] and all configuration values
/// loaded from .env files or dart-define flags.
/// يوفر بيئة التطبيق الحالية وجميع قيم التكوين المحمّلة من ملفات .env
/// أو خيارات dart-define.
///
/// Override example:
/// ```dart
/// envConfigProvider.overrideWithValue(AppEnvironment.production)
/// ```
final envConfigProvider = Provider<AppEnvironment>((ref) {
  // Default to development; override in ProviderScope for other environments.
  // القيمة الافتراضية هي بيئة التطوير؛ يمكن التجاوز عبر ProviderScope.
  return EnvConfig.environment;
});

// ─────────────────────────────────────────────────────────────────────────────
// CRASH REPORTER PROVIDER
// مزود مُبلِّغ الأعطال
// ─────────────────────────────────────────────────────────────────────────────

/// Crash reporting service (Sentry integration, offline storage, breadcrumbs).
/// خدمة الإبلاغ عن الأعطال (تكامل Sentry، تخزين محلي، مسار التتبع).
///
/// Must be overridden by the host app after calling
/// `CrashReporter.instance.initialize(config)`.
/// يجب تجاوزه من التطبيق المضيف بعد تهيئة CrashReporter.
///
/// Override example:
/// ```dart
/// crashReporterProvider.overrideWithValue(CrashReporter.instance)
/// ```
final crashReporterProvider = Provider<CrashReporter>((ref) {
  throw UnimplementedError(
    'crashReporterProvider must be overridden in ProviderScope.overrides. '
    'يجب تجاوز مزود مُبلِّغ الأعطال في ProviderScope.overrides.',
  );
});

// ─────────────────────────────────────────────────────────────────────────────
// API CLIENT PROVIDER
// مزود عميل الطلبات
// ─────────────────────────────────────────────────────────────────────────────

/// HTTP client with certificate pinning, request signing, and token refresh.
/// عميل HTTP مع تثبيت الشهادات، توقيع الطلبات، وتجديد الرمز المميز.
///
/// Automatically configures security features based on build mode:
/// - Debug: certificate pinning disabled
/// - Release: certificate pinning and request signing enabled
/// يُهيئ ميزات الأمان تلقائياً حسب وضع البناء.
final coreApiClientProvider = Provider<ApiClient>((ref) {
  final signingKeyService = ref.watch(signingKeyServiceProvider);
  final tokenManager = ref.read(tokenManagerProvider);
  final secureStorage = ref.read(secureStorageProvider);

  final apiClient = ApiClient(
    signingKeyService: signingKeyService,
    enableRequestSigning: true,
  );

  // Configure token interceptor for proactive refresh, retry, and queueing
  // تكوين معترض الرمز المميز للتجديد الاستباقي والمحاولة وقائمة الانتظار
  apiClient.configureTokenInterceptor(
    tokenManager: tokenManager,
    secureStorage: secureStorage,
  );

  return apiClient;
});
