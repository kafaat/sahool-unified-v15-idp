/// SAHOOL Crash Reporting Usage Examples
/// أمثلة استخدام خدمة تتبع الأعطال
///
/// This file demonstrates how to use the crash reporting service
/// throughout the application.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'crash_reporting_service.dart';

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 1: Manual Error Reporting
// ═══════════════════════════════════════════════════════════════════════════

class ExampleErrorReporting extends ConsumerWidget {
  const ExampleErrorReporting({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ElevatedButton(
      onPressed: () async {
        try {
          // Some operation that might fail
          await riskyOperation();
        } catch (e, stackTrace) {
          // Report error to crash reporting service
          final crashReporting = CrashReportingService();
          await crashReporting.reportError(
            e,
            stackTrace,
            severity: ErrorSeverity.error,
            reason: 'Failed to perform risky operation',
            customData: {
              'operation': 'riskyOperation',
              'userId': 'anonymous_123',
            },
          );

          // Show user-friendly error message
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Operation failed')),
            );
          }
        }
      },
      child: const Text('Perform Risky Operation'),
    );
  }

  Future<void> riskyOperation() async {
    // Simulated operation
    throw Exception('Something went wrong');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 2: Recording Breadcrumbs for User Actions
// ═══════════════════════════════════════════════════════════════════════════

class ExampleBreadcrumbs extends ConsumerWidget {
  const ExampleBreadcrumbs({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final crashReporting = CrashReportingService();

    return Column(
      children: [
        ElevatedButton(
          onPressed: () {
            // Record user action
            crashReporting.recordBreadcrumb(
              message: 'User clicked submit button',
              category: 'user_action',
              data: {'screen': 'form_page'},
              level: BreadcrumbLevel.info,
            );

            // Perform action
            submitForm();
          },
          child: const Text('Submit'),
        ),
        ElevatedButton(
          onPressed: () {
            // Record navigation
            crashReporting.recordBreadcrumb(
              message: 'User navigated to settings',
              category: 'navigation',
              data: {'from': 'home', 'to': 'settings'},
              level: BreadcrumbLevel.info,
            );

            // Navigate
            Navigator.pushNamed(context, '/settings');
          },
          child: const Text('Go to Settings'),
        ),
      ],
    );
  }

  void submitForm() {
    // Form submission logic
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 3: Setting User Context on Login
// ═══════════════════════════════════════════════════════════════════════════

class ExampleUserContext {
  Future<void> onUserLogin(String userId, String tenantId, String role) async {
    final crashReporting = CrashReportingService();

    // Set user context (anonymized)
    await crashReporting.setUserContext(
      anonymousId: 'user_${userId.hashCode}', // Anonymize user ID
      tenantId: tenantId,
      role: role,
      metadata: {
        'platform': 'mobile',
        'app_version': '15.5.0',
      },
    );

    // Record login event
    crashReporting.recordBreadcrumb(
      message: 'User logged in',
      category: 'auth',
      level: BreadcrumbLevel.info,
    );
  }

  Future<void> onUserLogout() async {
    final crashReporting = CrashReportingService();

    // Record logout event
    crashReporting.recordBreadcrumb(
      message: 'User logged out',
      category: 'auth',
      level: BreadcrumbLevel.info,
    );

    // Clear user context
    await crashReporting.clearUserContext();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 4: Network Error Handling
// ═══════════════════════════════════════════════════════════════════════════

class ExampleNetworkErrors {
  Future<void> fetchData() async {
    final crashReporting = CrashReportingService();

    try {
      // Record API call breadcrumb
      crashReporting.recordBreadcrumb(
        message: 'Fetching data from API',
        category: 'network',
        data: {'endpoint': '/api/v1/data'},
        level: BreadcrumbLevel.info,
      );

      // Simulated API call
      // final response = await dio.get('/api/v1/data');

      throw Exception('Network error: Connection timeout');
    } catch (e, stackTrace) {
      // Report network error (will be filtered if too common)
      await crashReporting.reportError(
        e,
        stackTrace,
        severity: ErrorSeverity.warning,
        reason: 'API data fetch failed',
        customData: {
          'endpoint': '/api/v1/data',
          'method': 'GET',
        },
      );

      rethrow;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 5: Custom Keys for Debugging
// ═══════════════════════════════════════════════════════════════════════════

class ExampleCustomKeys {
  Future<void> setDebugInfo() async {
    final crashReporting = CrashReportingService();

    // Set custom keys for debugging
    await crashReporting.setCustomKey('sync_status', 'active');
    await crashReporting.setCustomKey('offline_mode', true);
    await crashReporting.setCustomKey('data_size', 1024);
    await crashReporting.setCustomKey('last_sync', DateTime.now().toIso8601String());
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 6: Using Riverpod Provider
// ═══════════════════════════════════════════════════════════════════════════

class ExampleWithProvider extends ConsumerWidget {
  const ExampleWithProvider({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ElevatedButton(
      onPressed: () async {
        try {
          // Get crash reporting service from provider
          // Note: You can also use CrashReportingService() directly (singleton)
          final crashReporting = CrashReportingService();

          // Record breadcrumb
          crashReporting.recordBreadcrumb(
            message: 'Processing data',
            category: 'data',
            level: BreadcrumbLevel.info,
          );

          // Perform operation
          await processData();
        } catch (e, stackTrace) {
          final crashReporting = CrashReportingService();
          await crashReporting.reportError(
            e,
            stackTrace,
            severity: ErrorSeverity.error,
            reason: 'Data processing failed',
          );
        }
      },
      child: const Text('Process Data'),
    );
  }

  Future<void> processData() async {
    // Data processing logic
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 7: Configuration Options
// ═══════════════════════════════════════════════════════════════════════════

/// Configure crash reporting in main.dart or during app initialization
class ExampleConfiguration {
  Future<void> configureAdvanced() async {
    final crashReporting = CrashReportingService();

    // Initialize with custom settings
    await crashReporting.initialize(
      samplingRate: 0.5, // Report 50% of errors (for high-volume apps)
      maxBreadcrumbs: 50, // Keep last 50 breadcrumbs
    );

    // Enable/disable at runtime
    await crashReporting.setEnabled(true);

    // Check status
    if (crashReporting.isEnabled) {
      debugPrint('Crash reporting is enabled');
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// BEST PRACTICES
// ═══════════════════════════════════════════════════════════════════════════

/*
1. RECORD BREADCRUMBS for user actions, navigation, and important events
   - Helps understand the sequence of events leading to a crash
   - Use appropriate categories: 'user_action', 'navigation', 'network', etc.

2. REPORT ERRORS with proper severity levels:
   - debug: Development-only information
   - info: Informational messages
   - warning: Non-critical errors
   - error: Errors that should be investigated
   - fatal: Critical errors that crash the app

3. SANITIZE DATA automatically:
   - PII (emails, phones, etc.) is automatically removed
   - Sensitive keys (passwords, tokens) are automatically redacted
   - Always review custom data before reporting

4. SET USER CONTEXT:
   - Use anonymized IDs instead of real user identifiers
   - Set context on login, clear on logout
   - Include tenant ID and role for multi-tenant apps

5. USE CUSTOM KEYS:
   - Add relevant debugging information
   - Keep keys concise and meaningful
   - Update as app state changes

6. CONFIGURE WISELY:
   - Use sampling for high-volume apps
   - Adjust breadcrumb limit based on needs
   - Disable in development if needed

7. PROVIDER EXTENSIONS:
   - To add Firebase Crashlytics, implement CrashReportingProvider
   - To add Sentry, implement CrashReportingProvider
   - Multiple providers can run simultaneously

Example Firebase Crashlytics Provider:

class FirebaseCrashlyticsProvider implements CrashReportingProvider {
  @override
  String get name => 'Firebase Crashlytics';

  @override
  Future<void> initialize() async {
    // Initialize Firebase Crashlytics
  }

  @override
  Future<void> reportError(ErrorReport report) async {
    // await FirebaseCrashlytics.instance.recordError(...)
  }

  // ... implement other methods
}

Then in main.dart:
await crashReporting.initialize(
  providers: [
    FirebaseCrashlyticsProvider(),
    SentryProvider(),
  ],
);
*/
