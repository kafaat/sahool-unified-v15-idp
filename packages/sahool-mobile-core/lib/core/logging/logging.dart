/// SAHOOL Structured Logging Module
/// نظام التسجيل المهيكل لتطبيق سهول
///
/// Provides comprehensive logging capabilities:
/// - Log levels: debug, info, warning, error, fatal
/// - Structured metadata support (userId, fieldId, action, etc.)
/// - File-based logging for offline mode
/// - Log rotation (max 5 files, 2MB each)
/// - Automatic sync when online
/// - Arabic language support
/// - JSON structured logs
///
/// ## Quick Start
///
/// ```dart
/// import 'package:sahool_mobile_core/core/logging/logging.dart';
///
/// // Initialize at app startup
/// await Logger.initialize();
///
/// // Set user context after login
/// Logger.setGlobalContext(userId: 'user123', tenantId: 'farm001');
///
/// // Basic logging
/// Logger.debug('Debug message');
/// Logger.info('Info message', messageAr: 'رسالة معلومات');
/// Logger.warning('Warning message');
/// Logger.error('Error occurred', error: exception, stackTrace: stack);
/// Logger.fatal('Critical failure');
///
/// // Shorthand methods
/// Logger.d('Debug');
/// Logger.i('Info');
/// Logger.w('Warning');
/// Logger.e('Error', error: e);
///
/// // Category-based logging
/// Logger.field('Field updated', fieldId: 'field_001', action: 'update');
/// Logger.network('GET', '/api/fields', statusCode: 200, durationMs: 150);
/// Logger.sync('Sync completed', success: true, recordCount: 50);
/// Logger.user('Button tap', screen: 'home', action: 'refresh');
/// Logger.auth('Login', userId: 'user123', success: true);
/// Logger.navigation('/field-details', fromRoute: '/home');
/// Logger.performance('Load fields', durationMs: 250);
/// Logger.advisory('Irrigation needed', fieldId: 'field_001', confidence: 0.92);
///
/// // Use mixin in classes
/// class MyService with LoggerMixin {
///   void doSomething() {
///     logInfo('Operation started');
///     try {
///       // ...
///       logDebug('Step completed');
///     } catch (e, stack) {
///       logError('Operation failed', error: e, stackTrace: stack);
///     }
///   }
/// }
///
/// // Time operations
/// final result = await LoggerTiming.timeAsync('Load data', () async {
///   return await api.fetchData();
/// });
///
/// // Manual sync
/// await Logger.syncNow();
///
/// // Get log info
/// final files = await Logger.getLogFilesInfo();
/// final size = await Logger.getTotalStorageSize();
///
/// // Cleanup
/// await Logger.clearSyncedLogs(keepDays: 7);
///
/// // Dispose at app shutdown
/// await Logger.dispose();
/// ```
library;

export 'log_models.dart';
export 'file_logger.dart';
export 'log_sync_service.dart';
export 'logger.dart';
