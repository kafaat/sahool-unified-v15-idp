import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'logging.dart';

/// SAHOOL Logger Usage Examples
/// امثلة استخدام المسجل في تطبيق سهول
///
/// This file demonstrates how to integrate the structured logging system
/// throughout the SAHOOL mobile application.

// ═══════════════════════════════════════════════════════════════════════════
// 1. INITIALIZATION EXAMPLE
// ═══════════════════════════════════════════════════════════════════════════

/// Initialize logger in main.dart
/// تهيئة المسجل في main.dart
///
/// ```dart
/// void main() async {
///   WidgetsFlutterBinding.ensureInitialized();
///
///   // Initialize logger early
///   await Logger.initialize(
///     config: kDebugMode
///         ? LoggerConfig.development()
///         : LoggerConfig.production(),
///     syncCallback: (logs) async {
///       // Optional: Custom sync implementation
///       final response = await api.post('/logs', body: {'logs': logs});
///       return response.statusCode == 200;
///     },
///   );
///
///   runApp(const MyApp());
/// }
/// ```

// ═══════════════════════════════════════════════════════════════════════════
// 2. HOME SCREEN EXAMPLE
// ═══════════════════════════════════════════════════════════════════════════

/// Example: HomeDashboard with logging
/// مثال: الشاشة الرئيسية مع التسجيل
class HomeDashboardWithLogging extends ConsumerStatefulWidget {
  const HomeDashboardWithLogging({super.key});

  @override
  ConsumerState<HomeDashboardWithLogging> createState() =>
      _HomeDashboardWithLoggingState();
}

class _HomeDashboardWithLoggingState
    extends ConsumerState<HomeDashboardWithLogging> {
  @override
  void initState() {
    super.initState();

    // Log screen view
    Logger.navigation(
      '/home',
      routeNameAr: 'الرئيسية',
    );

    _loadInitialData();
  }

  Future<void> _loadInitialData() async {
    Logger.debug('Loading initial home data...', tag: 'HOME');

    try {
      // Use performance timing
      final data = await LoggerTiming.timeAsync(
        'Load home data',
        () async {
          // Simulate data loading
          await Future.delayed(const Duration(milliseconds: 500));
          return {'fields': 5, 'alerts': 2};
        },
        operationAr: 'تحميل بيانات الرئيسية',
      );

      Logger.info(
        'Home data loaded successfully',
        messageAr: 'تم تحميل بيانات الرئيسية بنجاح',
        tag: 'HOME',
        extra: {'fields_count': data['fields'], 'alerts_count': data['alerts']},
      );
    } catch (e, stack) {
      Logger.error(
        'Failed to load home data',
        messageAr: 'فشل في تحميل بيانات الرئيسية',
        tag: 'HOME',
        error: e,
        stackTrace: stack,
      );
    }
  }

  void _onRefresh() {
    Logger.user(
      'Pull to refresh',
      actionAr: 'سحب للتحديث',
      screen: 'home',
    );
    _loadInitialData();
  }

  void _onFieldTap(String fieldId, String fieldName) {
    Logger.user(
      'Field card tap',
      actionAr: 'الضغط على بطاقة الحقل',
      screen: 'home',
      targetId: fieldId,
      params: {'field_name': fieldName},
    );

    Logger.field(
      'Opening field details',
      messageAr: 'فتح تفاصيل الحقل',
      fieldId: fieldId,
      action: 'view',
      actionAr: 'عرض',
    );
  }

  void _onNotificationTap() {
    Logger.user(
      'Notification bell tap',
      actionAr: 'الضغط على جرس الإشعارات',
      screen: 'home',
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('سهول'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: _onNotificationTap,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => _onRefresh(),
        child: ListView(
          children: [
            // Example field card
            ListTile(
              title: const Text('حقل القمح الشمالي'),
              subtitle: const Text('45.5 هكتار - صحة: 78%'),
              onTap: () => _onFieldTap('field_1', 'حقل القمح الشمالي'),
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// 3. FIELD SERVICE EXAMPLE WITH MIXIN
// ═══════════════════════════════════════════════════════════════════════════

/// Example: Field service using LoggerMixin
/// مثال: خدمة الحقول باستخدام خليط التسجيل
class FieldServiceWithLogging with LoggerMixin {
  @override
  String get logTag => 'FieldService';

  Future<void> createField(Map<String, dynamic> fieldData) async {
    logInfo('Creating new field', data: {'name': fieldData['name']});

    try {
      // Simulate API call
      await Future.delayed(const Duration(milliseconds: 300));

      Logger.field(
        'Field created successfully',
        messageAr: 'تم إنشاء الحقل بنجاح',
        fieldId: 'new_field_id',
        action: 'create',
        actionAr: 'إنشاء',
        extra: {
          'name': fieldData['name'],
          'area': fieldData['area'],
          'crop': fieldData['crop'],
        },
      );

      logInfo('Field creation complete');
    } catch (e, stack) {
      logError('Failed to create field', error: e, stackTrace: stack);
      rethrow;
    }
  }

  Future<void> updateFieldHealth(String fieldId, double ndviValue) async {
    logDebug('Updating field health', data: {
      'field_id': fieldId,
      'ndvi': ndviValue,
    });

    Logger.field(
      'Field health updated',
      messageAr: 'تم تحديث صحة الحقل',
      fieldId: fieldId,
      action: 'update_health',
      actionAr: 'تحديث الصحة',
      extra: {'ndvi': ndviValue},
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// 4. API CLIENT EXAMPLE
// ═══════════════════════════════════════════════════════════════════════════

/// Example: API client with network logging
/// مثال: عميل API مع تسجيل الشبكة
class ApiClientWithLogging with LoggerMixin {
  @override
  String get logTag => 'API';

  Future<Map<String, dynamic>> get(String endpoint) async {
    final requestId = DateTime.now().millisecondsSinceEpoch.toString();
    final stopwatch = Stopwatch()..start();

    logDebug('Starting request', data: {
      'method': 'GET',
      'endpoint': endpoint,
      'request_id': requestId,
    });

    try {
      // Simulate API call
      await Future.delayed(const Duration(milliseconds: 200));
      stopwatch.stop();

      Logger.network(
        'GET',
        endpoint,
        statusCode: 200,
        durationMs: stopwatch.elapsedMilliseconds,
        requestId: requestId,
      );

      return {'success': true};
    } catch (e) {
      stopwatch.stop();

      Logger.network(
        'GET',
        endpoint,
        statusCode: 500,
        durationMs: stopwatch.elapsedMilliseconds,
        requestId: requestId,
        error: e,
      );

      rethrow;
    }
  }

  Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    final requestId = DateTime.now().millisecondsSinceEpoch.toString();
    final stopwatch = Stopwatch()..start();

    logDebug('Starting POST request', data: {
      'endpoint': endpoint,
      'request_id': requestId,
    });

    try {
      // Simulate API call
      await Future.delayed(const Duration(milliseconds: 300));
      stopwatch.stop();

      Logger.network(
        'POST',
        endpoint,
        statusCode: 201,
        durationMs: stopwatch.elapsedMilliseconds,
        requestId: requestId,
      );

      return {'success': true, 'id': 'new_id'};
    } catch (e) {
      stopwatch.stop();

      Logger.network(
        'POST',
        endpoint,
        statusCode: 500,
        durationMs: stopwatch.elapsedMilliseconds,
        requestId: requestId,
        error: e,
      );

      rethrow;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// 5. SYNC SERVICE EXAMPLE
// ═══════════════════════════════════════════════════════════════════════════

/// Example: Sync service with logging
/// مثال: خدمة المزامنة مع التسجيل
class SyncServiceWithLogging with LoggerMixin {
  @override
  String get logTag => 'SYNC';

  Future<void> syncAll() async {
    logInfo('Starting full sync');
    final stopwatch = Stopwatch()..start();

    try {
      // Sync fields
      await _syncFields();

      // Sync tasks
      await _syncTasks();

      // Sync observations
      await _syncObservations();

      stopwatch.stop();

      Logger.sync(
        'Full sync completed',
        success: true,
        details: 'All data synchronized',
        detailsAr: 'تمت مزامنة جميع البيانات',
        recordCount: 150,
        durationMs: stopwatch.elapsedMilliseconds,
      );
    } catch (e, stack) {
      stopwatch.stop();

      Logger.sync(
        'Full sync failed',
        success: false,
        details: e.toString(),
        durationMs: stopwatch.elapsedMilliseconds,
      );

      logError('Sync failed', error: e, stackTrace: stack);
    }
  }

  Future<void> _syncFields() async {
    logDebug('Syncing fields...');
    await Future.delayed(const Duration(milliseconds: 200));
    Logger.sync('Fields sync', success: true, recordCount: 5);
  }

  Future<void> _syncTasks() async {
    logDebug('Syncing tasks...');
    await Future.delayed(const Duration(milliseconds: 150));
    Logger.sync('Tasks sync', success: true, recordCount: 12);
  }

  Future<void> _syncObservations() async {
    logDebug('Syncing observations...');
    await Future.delayed(const Duration(milliseconds: 250));
    Logger.sync('Observations sync', success: true, recordCount: 8);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// 6. AUTHENTICATION EXAMPLE
// ═══════════════════════════════════════════════════════════════════════════

/// Example: Auth service with logging
/// مثال: خدمة المصادقة مع التسجيل
class AuthServiceWithLogging with LoggerMixin {
  @override
  String get logTag => 'AUTH';

  Future<bool> login(String phone, String otp) async {
    logInfo('Login attempt', data: {'phone': '***${phone.substring(phone.length - 4)}'});

    try {
      // Simulate login
      await Future.delayed(const Duration(milliseconds: 500));

      // Set global context after successful login
      Logger.setGlobalContext(
        userId: 'user_123',
        tenantId: 'farm_456',
        sessionId: 'session_${DateTime.now().millisecondsSinceEpoch}',
      );

      Logger.auth(
        'Login successful',
        eventAr: 'تسجيل الدخول ناجح',
        userId: 'user_123',
        success: true,
      );

      return true;
    } catch (e, stack) {
      Logger.auth(
        'Login failed',
        eventAr: 'فشل تسجيل الدخول',
        success: false,
        reason: e.toString(),
      );

      logError('Login error', error: e, stackTrace: stack);
      return false;
    }
  }

  Future<void> logout() async {
    logInfo('Logout initiated');

    Logger.auth(
      'Logout',
      eventAr: 'تسجيل الخروج',
      success: true,
    );

    // Clear global context
    Logger.clearGlobalContext();

    logInfo('Logout complete');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// 7. ADVISORY/AI EXAMPLE
// ═══════════════════════════════════════════════════════════════════════════

/// Example: Advisory service with logging
/// مثال: خدمة الاستشارات مع التسجيل
class AdvisoryServiceWithLogging with LoggerMixin {
  @override
  String get logTag => 'ADVISORY';

  Future<Map<String, dynamic>> getIrrigationAdvice(String fieldId) async {
    logDebug('Fetching irrigation advice', data: {'field_id': fieldId});

    try {
      // Simulate AI processing
      await Future.delayed(const Duration(milliseconds: 800));

      final advice = {
        'recommendation': 'Irrigate 25mm tomorrow morning',
        'recommendation_ar': 'الري بمقدار 25 ملم صباح الغد',
        'confidence': 0.92,
        'reasons': [
          'Low soil moisture (35%)',
          'No rain expected (10% chance)',
          'Crop at tillering stage',
        ],
      };

      Logger.advisory(
        'Irrigation recommendation generated',
        messageAr: 'تم إنشاء توصية الري',
        fieldId: fieldId,
        advisoryType: 'irrigation',
        confidence: advice['confidence'] as double,
        extra: {
          'recommended_mm': 25,
          'timing': 'morning',
        },
      );

      return advice;
    } catch (e, stack) {
      logError('Failed to get irrigation advice', error: e, stackTrace: stack);
      rethrow;
    }
  }

  Future<Map<String, dynamic>> getCropHealthAnalysis(
    String fieldId,
    double ndviValue,
  ) async {
    logDebug('Analyzing crop health', data: {
      'field_id': fieldId,
      'ndvi': ndviValue,
    });

    try {
      await Future.delayed(const Duration(milliseconds: 600));

      final analysis = {
        'status': ndviValue > 0.6 ? 'healthy' : 'needs_attention',
        'status_ar': ndviValue > 0.6 ? 'صحي' : 'يحتاج اهتمام',
        'ndvi': ndviValue,
        'confidence': 0.88,
      };

      Logger.advisory(
        'Crop health analysis complete',
        messageAr: 'اكتمل تحليل صحة المحصول',
        fieldId: fieldId,
        advisoryType: 'health_analysis',
        confidence: analysis['confidence'] as double,
        extra: {
          'ndvi': ndviValue,
          'status': analysis['status'],
        },
      );

      return analysis;
    } catch (e, stack) {
      logError('Crop health analysis failed', error: e, stackTrace: stack);
      rethrow;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// 8. LOG MANAGEMENT WIDGET EXAMPLE
// ═══════════════════════════════════════════════════════════════════════════

/// Example: Debug screen showing log status
/// مثال: شاشة تصحيح تعرض حالة السجلات
class LogManagementScreen extends StatefulWidget {
  const LogManagementScreen({super.key});

  @override
  State<LogManagementScreen> createState() => _LogManagementScreenState();
}

class _LogManagementScreenState extends State<LogManagementScreen> {
  List<LogFileInfo> _files = [];
  int _totalSize = 0;
  LogSyncStatus? _syncStatus;

  @override
  void initState() {
    super.initState();
    _loadLogInfo();
  }

  Future<void> _loadLogInfo() async {
    final files = await Logger.getLogFilesInfo();
    final size = await Logger.getTotalStorageSize();
    final status = Logger.getSyncStatus();

    setState(() {
      _files = files;
      _totalSize = size;
      _syncStatus = status;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Log Management | ادارة السجلات'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Storage info
          Card(
            child: ListTile(
              leading: const Icon(Icons.storage),
              title: const Text('Total Storage | الحجم الكلي'),
              subtitle: Text('${(_totalSize / 1024).toStringAsFixed(2)} KB'),
            ),
          ),

          const SizedBox(height: 8),

          // Sync status
          if (_syncStatus != null)
            Card(
              child: Column(
                children: [
                  ListTile(
                    leading: const Icon(Icons.sync),
                    title: const Text('Sync Status | حالة المزامنة'),
                    subtitle: Text(
                      'Pending: ${_syncStatus!.pendingCount} | '
                      'Synced: ${_syncStatus!.syncedCount}',
                    ),
                  ),
                  if (_syncStatus!.lastSyncAt != null)
                    ListTile(
                      leading: const Icon(Icons.access_time),
                      title: const Text('Last Sync | آخر مزامنة'),
                      subtitle: Text(_syncStatus!.lastSyncAt!.toString()),
                    ),
                ],
              ),
            ),

          const SizedBox(height: 8),

          // File list
          const Text(
            'Log Files | ملفات السجل',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          const SizedBox(height: 8),

          ..._files.map((file) => Card(
                child: ListTile(
                  leading: const Icon(Icons.description),
                  title: Text(file.name),
                  subtitle: Text(
                    'Size: ${file.sizeMB.toStringAsFixed(2)} MB | '
                    'Entries: ${file.entryCount}',
                  ),
                ),
              )),

          const SizedBox(height: 16),

          // Actions
          ElevatedButton.icon(
            onPressed: () async {
              await Logger.syncNow();
              _loadLogInfo();
            },
            icon: const Icon(Icons.sync),
            label: const Text('Sync Now | مزامنة الآن'),
          ),

          const SizedBox(height: 8),

          OutlinedButton.icon(
            onPressed: () async {
              final cleared = await Logger.clearSyncedLogs(keepDays: 7);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('Cleared $cleared synced logs')),
              );
              _loadLogInfo();
            },
            icon: const Icon(Icons.cleaning_services),
            label: const Text('Clear Synced | مسح المتزامنة'),
          ),
        ],
      ),
    );
  }
}
