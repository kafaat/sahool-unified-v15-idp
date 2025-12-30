/// Sentry Usage Examples
/// أمثلة استخدام Sentry
///
/// This file demonstrates how to use the SentryService for error tracking,
/// performance monitoring, and debugging throughout the SAHOOL Field App.

import 'package:flutter/material.dart';
import 'sentry_service.dart';
import 'package:sentry_flutter/sentry_flutter.dart';

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 1: Basic Error Capture
// ═══════════════════════════════════════════════════════════════════════════

class ErrorCaptureExample {
  /// Capture exceptions in try-catch blocks
  Future<void> performRiskyOperation() async {
    try {
      // Risky operation that might fail
      await _syncData();
    } catch (e, stackTrace) {
      // Capture the error and send to Sentry
      SentryService.captureException(e, stackTrace: stackTrace);

      // Still handle the error locally
      debugPrint('Sync failed: $e');
      rethrow; // Or handle gracefully
    }
  }

  /// Capture errors with additional context
  Future<void> performOperationWithContext() async {
    try {
      await _processPayment();
    } catch (e, stackTrace) {
      // Add custom scope with additional context
      SentryService.captureException(
        e,
        stackTrace: stackTrace,
        withScope: (scope) {
          scope.setTag('operation', 'payment');
          scope.setContexts('payment', {
            'amount': '1000',
            'currency': 'YER',
            'method': 'wallet',
          });
        },
      );
      rethrow;
    }
  }

  Future<void> _syncData() async {
    // Simulate sync operation
  }

  Future<void> _processPayment() async {
    // Simulate payment processing
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 2: Breadcrumb Tracking
// ═══════════════════════════════════════════════════════════════════════════

class BreadcrumbExample {
  /// Track user navigation
  void navigateToScreen(String screenName) {
    SentryService.addBreadcrumb(
      'Navigated to $screenName',
      category: 'navigation',
      level: SentryLevel.info,
    );
  }

  /// Track user actions
  void onUserAction(String action, Map<String, dynamic>? data) {
    SentryService.addBreadcrumb(
      action,
      category: 'user.action',
      level: SentryLevel.info,
      data: data,
    );
  }

  /// Track state changes
  void onDataSync(String status) {
    SentryService.addBreadcrumb(
      'Data sync: $status',
      category: 'sync',
      level: status == 'success' ? SentryLevel.info : SentryLevel.warning,
      data: {'timestamp': DateTime.now().toIso8601String()},
    );
  }

  /// Example usage in a widget
  void example() {
    // User opened settings
    SentryService.addBreadcrumb('User opened settings', category: 'navigation');

    // User changed theme
    SentryService.addBreadcrumb(
      'Theme changed',
      category: 'user.action',
      data: {'theme': 'dark'},
    );

    // Data loaded successfully
    SentryService.addBreadcrumb(
      'Fields data loaded',
      category: 'data',
      level: SentryLevel.info,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 3: User Context
// ═══════════════════════════════════════════════════════════════════════════

class UserContextExample {
  /// Set user context after login
  Future<void> onUserLogin(String userId, String email, String role) async {
    await SentryService.setUser(
      userId,
      email: email,
      username: email.split('@').first,
      extras: {
        'role': role,
        'tenant': 'sahool-demo',
        'login_time': DateTime.now().toIso8601String(),
      },
    );

    SentryService.addBreadcrumb('User logged in', category: 'auth');
  }

  /// Clear user context on logout
  Future<void> onUserLogout() async {
    SentryService.addBreadcrumb('User logged out', category: 'auth');
    await SentryService.clearUser();
  }

  /// Update user context with additional info
  Future<void> updateUserContext(Map<String, dynamic> profileData) async {
    await SentryService.setContext('user_profile', profileData);

    SentryService.addBreadcrumb(
      'User profile updated',
      category: 'user.action',
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 4: Performance Monitoring
// ═══════════════════════════════════════════════════════════════════════════

class PerformanceMonitoringExample {
  /// Monitor sync operation performance
  Future<void> syncDataWithMonitoring() async {
    final transaction = SentryService.startTransaction(
      'sync_data',
      'task',
      description: 'Sync all fields and tasks data',
    );

    try {
      // Start a span for fetching data
      final fetchSpan = await SentryService.startSpan(
        'fetch',
        description: 'Fetch data from API',
      );
      await _fetchDataFromAPI();
      fetchSpan.status = SpanStatus.ok();
      await fetchSpan.finish();

      // Start a span for saving to database
      final saveSpan = await SentryService.startSpan(
        'save',
        description: 'Save data to local database',
      );
      await _saveToDatabase();
      saveSpan.status = SpanStatus.ok();
      await saveSpan.finish();

      transaction.status = SpanStatus.ok();
    } catch (e, stackTrace) {
      transaction.status = SpanStatus.internalError();
      SentryService.captureException(e, stackTrace: stackTrace);
      rethrow;
    } finally {
      await transaction.finish();
    }
  }

  /// Monitor screen load time
  Future<void> loadScreenWithMonitoring(String screenName) async {
    final transaction = SentryService.startTransaction(
      'screen_load',
      'ui',
      description: 'Load $screenName screen',
      data: {'screen': screenName},
    );

    try {
      await _loadScreenData(screenName);
      transaction.status = SpanStatus.ok();
    } catch (e) {
      transaction.status = SpanStatus.internalError();
      rethrow;
    } finally {
      await transaction.finish();
    }
  }

  Future<void> _fetchDataFromAPI() async {
    await Future.delayed(const Duration(milliseconds: 500));
  }

  Future<void> _saveToDatabase() async {
    await Future.delayed(const Duration(milliseconds: 200));
  }

  Future<void> _loadScreenData(String screenName) async {
    await Future.delayed(const Duration(milliseconds: 300));
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 5: Custom Context and Tags
// ═══════════════════════════════════════════════════════════════════════════

class CustomContextExample {
  /// Set custom context for device info
  Future<void> setDeviceContext() async {
    await SentryService.setContext('device', {
      'battery_level': '75%',
      'network_type': 'WiFi',
      'storage_available': '2.5GB',
      'location_enabled': true,
    });
  }

  /// Set tags for filtering in Sentry
  Future<void> setAppTags() async {
    await SentryService.setTag('tenant', 'sahool-demo');
    await SentryService.setTag('feature', 'offline_sync');
    await SentryService.setTag('app_version', '15.5.0');
  }

  /// Set context before an operation
  Future<void> performOperationWithContext() async {
    // Set operation context
    await SentryService.setContext('operation', {
      'type': 'field_update',
      'field_id': 'field-123',
      'user_role': 'farmer',
    });

    await SentryService.setTag('operation_type', 'field_update');

    try {
      await _updateField();
    } catch (e, stackTrace) {
      // Error will include the context we set above
      SentryService.captureException(e, stackTrace: stackTrace);
      rethrow;
    }
  }

  Future<void> _updateField() async {
    // Update field logic
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 6: Integration with Repositories
// ═══════════════════════════════════════════════════════════════════════════

class FieldRepository {
  /// Example: Track errors in repository methods
  Future<List<Map<String, dynamic>>> getFields() async {
    final transaction = SentryService.startTransaction(
      'get_fields',
      'db.query',
    );

    try {
      SentryService.addBreadcrumb('Fetching fields from database', category: 'db');

      // Simulate database query
      final fields = await _queryDatabase();

      SentryService.addBreadcrumb(
        'Fields fetched successfully',
        category: 'db',
        data: {'count': fields.length},
      );

      transaction.status = SpanStatus.ok();
      return fields;
    } catch (e, stackTrace) {
      SentryService.addBreadcrumb('Failed to fetch fields', category: 'db');
      SentryService.captureException(e, stackTrace: stackTrace);
      transaction.status = SpanStatus.internalError();
      rethrow;
    } finally {
      await transaction.finish();
    }
  }

  Future<List<Map<String, dynamic>>> _queryDatabase() async {
    // Simulate query
    return [];
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 7: Integration with UI Widgets
// ═══════════════════════════════════════════════════════════════════════════

class MonitoredButtonWidget extends StatelessWidget {
  final VoidCallback onPressed;
  final String label;
  final String actionName;

  const MonitoredButtonWidget({
    super.key,
    required this.onPressed,
    required this.label,
    required this.actionName,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: () {
        // Track user interaction
        SentryService.addBreadcrumb(
          'Button pressed: $actionName',
          category: 'user.action',
        );

        // Execute the action
        try {
          onPressed();
        } catch (e, stackTrace) {
          SentryService.captureException(
            e,
            stackTrace: stackTrace,
            withScope: (scope) {
              scope.setTag('action', actionName);
            },
          );
          rethrow;
        }
      },
      child: Text(label),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 8: Network Request Monitoring
// ═══════════════════════════════════════════════════════════════════════════

class ApiService {
  /// Monitor API requests
  Future<Map<String, dynamic>> makeApiRequest(String endpoint) async {
    final transaction = SentryService.startTransaction(
      'api_request',
      'http',
      description: 'API Request to $endpoint',
    );

    try {
      SentryService.addBreadcrumb(
        'Making API request',
        category: 'http',
        data: {'endpoint': endpoint},
      );

      // Make the actual request
      final response = await _httpRequest(endpoint);

      SentryService.addBreadcrumb(
        'API request successful',
        category: 'http',
        data: {'status': 200},
      );

      transaction.status = SpanStatus.ok();
      return response;
    } catch (e, stackTrace) {
      SentryService.addBreadcrumb(
        'API request failed',
        category: 'http',
        level: SentryLevel.error,
        data: {'endpoint': endpoint, 'error': e.toString()},
      );

      SentryService.captureException(
        e,
        stackTrace: stackTrace,
        withScope: (scope) {
          scope.setTag('endpoint', endpoint);
        },
      );

      transaction.status = SpanStatus.internalError();
      rethrow;
    } finally {
      await transaction.finish();
    }
  }

  Future<Map<String, dynamic>> _httpRequest(String endpoint) async {
    // Simulate HTTP request
    return {};
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// EXAMPLE 9: Message Capture (Non-Exception Logging)
// ═══════════════════════════════════════════════════════════════════════════

class MessageCaptureExample {
  /// Capture important events that aren't errors
  void logImportantEvent() {
    SentryService.captureMessage(
      'User completed onboarding',
      level: SentryLevel.info,
    );
  }

  /// Capture warnings
  void logWarning() {
    SentryService.captureMessage(
      'Low battery detected during field visit',
      level: SentryLevel.warning,
    );
  }

  /// Capture unusual behavior
  void logUnusualBehavior() {
    SentryService.captureMessage(
      'User attempted to access feature without permission',
      level: SentryLevel.warning,
      withScope: (scope) {
        scope.setTag('security', 'permission_denied');
        scope.setContexts('attempt', {
          'feature': 'admin_panel',
          'user_role': 'farmer',
        });
      },
    );
  }
}
