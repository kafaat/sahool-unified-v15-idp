import 'package:flutter/foundation.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import '../config/env_config.dart';

/// Sentry Error Tracking and Performance Monitoring Service
/// خدمة تتبع الأخطاء ومراقبة الأداء
///
/// Features:
/// - Automatic error capture and reporting
/// - Performance monitoring with transactions
/// - Breadcrumb tracking for debugging context
/// - User context for error attribution
/// - Environment-aware configuration
///
/// Usage:
/// ```dart
/// // Initialize in main.dart
/// await SentryService.initialize();
///
/// // Capture exceptions
/// SentryService.captureException(error, stackTrace: stackTrace);
///
/// // Add breadcrumbs
/// SentryService.addBreadcrumb('User logged in', category: 'auth');
///
/// // Set user context
/// SentryService.setUser(userId, email: 'user@example.com');
///
/// // Track performance
/// final transaction = SentryService.startTransaction('sync', 'task');
/// await syncData();
/// await transaction.finish();
/// ```
class SentryService {
  static bool _initialized = false;
  static bool _enabled = false;

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize Sentry with configuration from environment
  static Future<void> initialize() async {
    if (_initialized) {
      debugPrint('⚠️ Sentry already initialized');
      return;
    }

    // Check if Sentry is enabled via configuration
    if (!EnvConfig.isSentryEnabled) {
      debugPrint('ℹ️ Sentry disabled (enableCrashReporting=${EnvConfig.enableCrashReporting}, dsn=${EnvConfig.sentryDsn.isNotEmpty ? "provided" : "missing"})');
      _initialized = true;
      _enabled = false;
      return;
    }

    try {
      await SentryFlutter.init(
        (options) {
          // DSN from environment
          options.dsn = EnvConfig.sentryDsn;

          // Environment tagging
          options.environment = EnvConfig.environment.name;

          // Release version tracking
          options.release = '${EnvConfig.appName}@${EnvConfig.fullVersion}';

          // Performance monitoring
          // 1.0 = 100% of transactions are sent (adjust in production)
          options.tracesSampleRate = EnvConfig.isProduction ? 0.1 : 1.0;

          // Debug settings
          options.debug = kDebugMode;

          // Automatically capture errors
          options.attachStacktrace = true;
          options.enableAutoSessionTracking = true;

          // Privacy & data filtering
          options.sendDefaultPii = false; // Don't send personally identifiable info
          options.beforeSend = _beforeSend; // Filter sensitive data

          // Performance monitoring options
          options.enableAutoPerformanceTracing = true;
          options.profilesSampleRate = EnvConfig.isProduction ? 0.1 : 1.0;

          // Breadcrumbs
          options.maxBreadcrumbs = 100;

          // Network tracking
          options.captureFailedRequests = true;

          if (kDebugMode) {
            debugPrint('✅ Sentry initialized: ${options.environment}');
            debugPrint('   DSN: ${options.dsn?.substring(0, 20)}...');
            debugPrint('   Release: ${options.release}');
            debugPrint('   Traces Sample Rate: ${options.tracesSampleRate}');
          }
        },
      );

      _initialized = true;
      _enabled = true;
    } catch (e) {
      debugPrint('❌ Failed to initialize Sentry: $e');
      _initialized = true;
      _enabled = false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Error Capture
  // ═══════════════════════════════════════════════════════════════════════════

  /// Capture an exception and send it to Sentry
  ///
  /// Example:
  /// ```dart
  /// try {
  ///   await riskyOperation();
  /// } catch (e, stackTrace) {
  ///   SentryService.captureException(e, stackTrace: stackTrace);
  /// }
  /// ```
  static Future<SentryId> captureException(
    dynamic exception, {
    StackTrace? stackTrace,
    String? hint,
    ScopeCallback? withScope,
  }) async {
    if (!_enabled) {
      if (kDebugMode) {
        debugPrint('⚠️ Sentry not enabled, exception not captured: $exception');
      }
      return SentryId.empty();
    }

    try {
      return await Sentry.captureException(
        exception,
        stackTrace: stackTrace,
        hint: hint,
        withScope: withScope,
      );
    } catch (e) {
      debugPrint('❌ Failed to capture exception in Sentry: $e');
      return SentryId.empty();
    }
  }

  /// Capture a message (not an exception)
  ///
  /// Example:
  /// ```dart
  /// SentryService.captureMessage(
  ///   'Unusual behavior detected',
  ///   level: SentryLevel.warning,
  /// );
  /// ```
  static Future<SentryId> captureMessage(
    String message, {
    SentryLevel? level = SentryLevel.info,
    String? hint,
    ScopeCallback? withScope,
  }) async {
    if (!_enabled) {
      if (kDebugMode) {
        debugPrint('⚠️ Sentry not enabled, message not captured: $message');
      }
      return SentryId.empty();
    }

    try {
      return await Sentry.captureMessage(
        message,
        level: level,
        hint: hint,
        withScope: withScope,
      );
    } catch (e) {
      debugPrint('❌ Failed to capture message in Sentry: $e');
      return SentryId.empty();
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Breadcrumbs
  // ═══════════════════════════════════════════════════════════════════════════

  /// Add a breadcrumb for debugging context
  ///
  /// Breadcrumbs are events that lead up to an error, helping you understand
  /// what the user was doing when the error occurred.
  ///
  /// Example:
  /// ```dart
  /// SentryService.addBreadcrumb('User opened settings', category: 'navigation');
  /// SentryService.addBreadcrumb('Data sync started', category: 'sync');
  /// ```
  static void addBreadcrumb(
    String message, {
    String? category,
    SentryLevel? level = SentryLevel.info,
    Map<String, dynamic>? data,
  }) {
    if (!_enabled) return;

    try {
      Sentry.addBreadcrumb(
        Breadcrumb(
          message: message,
          category: category,
          level: level,
          data: data,
          timestamp: DateTime.now().toUtc(),
        ),
      );
    } catch (e) {
      debugPrint('❌ Failed to add breadcrumb: $e');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // User Context
  // ═══════════════════════════════════════════════════════════════════════════

  /// Set user context for error attribution
  ///
  /// Example:
  /// ```dart
  /// SentryService.setUser(
  ///   'user-123',
  ///   email: 'user@example.com',
  ///   username: 'farmer_ahmed',
  ///   extras: {'role': 'field_agent', 'tenant': 'sahool-demo'},
  /// );
  /// ```
  static Future<void> setUser(
    String userId, {
    String? email,
    String? username,
    Map<String, dynamic>? extras,
  }) async {
    if (!_enabled) return;

    try {
      await Sentry.configureScope((scope) {
        scope.setUser(
          SentryUser(
            id: userId,
            email: email,
            username: username,
            data: extras,
          ),
        );
      });

      if (kDebugMode) {
        debugPrint('✅ Sentry user set: $userId');
      }
    } catch (e) {
      debugPrint('❌ Failed to set user in Sentry: $e');
    }
  }

  /// Clear user context (e.g., on logout)
  static Future<void> clearUser() async {
    if (!_enabled) return;

    try {
      await Sentry.configureScope((scope) {
        scope.setUser(null);
      });

      if (kDebugMode) {
        debugPrint('✅ Sentry user cleared');
      }
    } catch (e) {
      debugPrint('❌ Failed to clear user in Sentry: $e');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Performance Monitoring
  // ═══════════════════════════════════════════════════════════════════════════

  /// Start a performance transaction
  ///
  /// Transactions help you measure the performance of operations.
  ///
  /// Example:
  /// ```dart
  /// final transaction = SentryService.startTransaction('sync_data', 'task');
  /// try {
  ///   await performSync();
  ///   transaction.status = SpanStatus.ok();
  /// } catch (e) {
  ///   transaction.status = SpanStatus.internalError();
  ///   rethrow;
  /// } finally {
  ///   await transaction.finish();
  /// }
  /// ```
  static ISentrySpan startTransaction(
    String name,
    String operation, {
    String? description,
    Map<String, dynamic>? data,
  }) {
    if (!_enabled) {
      // Return a no-op transaction if Sentry is disabled
      return NoOpSentrySpan();
    }

    try {
      final transaction = Sentry.startTransaction(
        name,
        operation,
        description: description,
        bindToScope: true,
      );

      if (data != null) {
        for (final entry in data.entries) {
          transaction.setData(entry.key, entry.value);
        }
      }

      return transaction;
    } catch (e) {
      debugPrint('❌ Failed to start transaction: $e');
      return NoOpSentrySpan();
    }
  }

  /// Start a child span within the current transaction
  ///
  /// Example:
  /// ```dart
  /// final transaction = SentryService.startTransaction('checkout', 'task');
  /// final span = SentryService.startSpan('validate_cart', 'validation');
  /// await validateCart();
  /// await span.finish();
  /// await transaction.finish();
  /// ```
  static Future<ISentrySpan> startSpan(
    String operation, {
    String? description,
  }) async {
    if (!_enabled) {
      return NoOpSentrySpan();
    }

    try {
      final span = Sentry.getSpan();
      if (span != null) {
        return span.startChild(operation, description: description);
      }
      // If no active transaction, create a new one
      return Sentry.startTransaction(operation, operation, description: description);
    } catch (e) {
      debugPrint('❌ Failed to start span: $e');
      return NoOpSentrySpan();
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Custom Context & Tags
  // ═══════════════════════════════════════════════════════════════════════════

  /// Set custom context data
  ///
  /// Example:
  /// ```dart
  /// SentryService.setContext('device', {
  ///   'battery_level': '75%',
  ///   'network': 'WiFi',
  ///   'storage_available': '2.5GB',
  /// });
  /// ```
  static Future<void> setContext(String key, Map<String, dynamic> data) async {
    if (!_enabled) return;

    try {
      await Sentry.configureScope((scope) {
        scope.setContexts(key, data);
      });
    } catch (e) {
      debugPrint('❌ Failed to set context in Sentry: $e');
    }
  }

  /// Set a tag for filtering in Sentry
  ///
  /// Example:
  /// ```dart
  /// SentryService.setTag('tenant', 'sahool-demo');
  /// SentryService.setTag('feature', 'offline_sync');
  /// ```
  static Future<void> setTag(String key, String value) async {
    if (!_enabled) return;

    try {
      await Sentry.configureScope((scope) {
        scope.setTag(key, value);
      });
    } catch (e) {
      debugPrint('❌ Failed to set tag in Sentry: $e');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Privacy & Data Filtering
  // ═══════════════════════════════════════════════════════════════════════════

  /// Filter sensitive data before sending to Sentry
  static SentryEvent? _beforeSend(SentryEvent event, {Hint? hint}) {
    try {
      // Filter out sensitive request headers
      if (event.request != null) {
        final filteredHeaders = <String, String>{};
        event.request?.headers?.forEach((key, value) {
          // Remove authorization tokens and API keys
          if (key.toLowerCase().contains('authorization') ||
              key.toLowerCase().contains('token') ||
              key.toLowerCase().contains('api-key')) {
            filteredHeaders[key] = '[Filtered]';
          } else {
            filteredHeaders[key] = value;
          }
        });

        event = event.copyWith(
          request: event.request?.copyWith(headers: filteredHeaders),
        );
      }

      // Filter breadcrumbs with sensitive data
      if (event.breadcrumbs != null) {
        final filteredBreadcrumbs = event.breadcrumbs!.where((breadcrumb) {
          // Skip breadcrumbs from auth or sensitive operations
          return breadcrumb.category?.toLowerCase() != 'password' &&
              breadcrumb.category?.toLowerCase() != 'secret';
        }).toList();

        event = event.copyWith(breadcrumbs: filteredBreadcrumbs);
      }

      return event;
    } catch (e) {
      debugPrint('❌ Error in beforeSend filter: $e');
      return event;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Status & Utilities
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if Sentry is initialized and enabled
  static bool get isEnabled => _enabled;

  /// Close Sentry (call on app dispose)
  static Future<void> close() async {
    if (!_enabled) return;

    try {
      await Sentry.close();
      if (kDebugMode) {
        debugPrint('✅ Sentry closed');
      }
    } catch (e) {
      debugPrint('❌ Failed to close Sentry: $e');
    }
  }
}
