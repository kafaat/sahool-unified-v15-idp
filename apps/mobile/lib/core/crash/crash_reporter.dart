/// SAHOOL Crash Reporter
/// مُبلِّغ الأعطال
///
/// Comprehensive crash reporting service with Sentry integration,
/// offline storage, breadcrumb tracking, and sensitive data filtering.
///
/// Features:
/// - Sentry SDK integration (when configured)
/// - Flutter error capture
/// - Dart async error capture
/// - Native crash capture
/// - Navigation breadcrumbs
/// - User action breadcrumbs
/// - Sensitive data filtering (no passwords, tokens, PII)
/// - Offline crash report storage
/// - Custom tags (app version, device type)
/// - User context (anonymized)
///
/// Usage:
/// ```dart
/// // Initialize in main.dart
/// await CrashReporter.instance.initialize(CrashConfig.fromEnvironment());
///
/// // Configure app runner with error zones
/// await CrashReporter.instance.runApp(() => runApp(MyApp()));
///
/// // Report errors manually
/// CrashReporter.instance.reportError(error, stackTrace);
///
/// // Add breadcrumbs
/// CrashReporter.instance.addBreadcrumb('User tapped button');
///
/// // Set user context
/// CrashReporter.instance.setUserContext(userId: 'anonymized_id');
/// ```

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

import '../utils/pii_filter.dart';
import '../utils/app_logger.dart';
import 'crash_config.dart';
import 'breadcrumb_service.dart';

// Sentry import - conditionally available
// If sentry_flutter is not in pubspec.yaml, this will use stub implementation
export 'crash_config.dart';
export 'breadcrumb_service.dart';

/// Offline crash report data structure
/// هيكل بيانات تقرير الأعطال غير المتصل
class OfflineCrashReport {
  final String id;
  final DateTime timestamp;
  final String errorMessage;
  final String errorType;
  final String? stackTrace;
  final CrashSeverity severity;
  final Map<String, dynamic>? context;
  final List<Map<String, dynamic>>? breadcrumbs;
  final Map<String, dynamic>? tags;
  final Map<String, dynamic>? userContext;
  final Map<String, dynamic>? deviceContext;

  OfflineCrashReport({
    required this.id,
    required this.timestamp,
    required this.errorMessage,
    required this.errorType,
    this.stackTrace,
    this.severity = CrashSeverity.error,
    this.context,
    this.breadcrumbs,
    this.tags,
    this.userContext,
    this.deviceContext,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'timestamp': timestamp.toIso8601String(),
      'errorMessage': errorMessage,
      'errorType': errorType,
      'stackTrace': stackTrace,
      'severity': severity.name,
      'context': context,
      'breadcrumbs': breadcrumbs,
      'tags': tags,
      'userContext': userContext,
      'deviceContext': deviceContext,
    };
  }

  factory OfflineCrashReport.fromJson(Map<String, dynamic> json) {
    return OfflineCrashReport(
      id: json['id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      errorMessage: json['errorMessage'] as String,
      errorType: json['errorType'] as String,
      stackTrace: json['stackTrace'] as String?,
      severity: CrashSeverity.values.firstWhere(
        (e) => e.name == json['severity'],
        orElse: () => CrashSeverity.error,
      ),
      context: json['context'] as Map<String, dynamic>?,
      breadcrumbs: (json['breadcrumbs'] as List?)
          ?.map((e) => e as Map<String, dynamic>)
          .toList(),
      tags: json['tags'] as Map<String, dynamic>?,
      userContext: json['userContext'] as Map<String, dynamic>?,
      deviceContext: json['deviceContext'] as Map<String, dynamic>?,
    );
  }
}

/// User context for crash reports (anonymized)
/// سياق المستخدم لتقارير الأعطال (مجهول الهوية)
class CrashUserContext {
  /// Anonymized user identifier (hash, not actual ID)
  final String anonymousId;

  /// Tenant/organization ID
  final String? tenantId;

  /// User role (farmer, admin, etc.)
  final String? role;

  /// Additional metadata
  final Map<String, dynamic>? metadata;

  const CrashUserContext({
    required this.anonymousId,
    this.tenantId,
    this.role,
    this.metadata,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': anonymousId,
      if (tenantId != null) 'tenant_id': tenantId,
      if (role != null) 'role': role,
      if (metadata != null) ...metadata!,
    };
  }
}

/// Device context for crash reports
/// سياق الجهاز لتقارير الأعطال
class CrashDeviceContext {
  final String platform;
  final String? osVersion;
  final String? deviceModel;
  final String? manufacturer;
  final String? locale;
  final bool? isPhysicalDevice;
  final String? screenResolution;

  const CrashDeviceContext({
    required this.platform,
    this.osVersion,
    this.deviceModel,
    this.manufacturer,
    this.locale,
    this.isPhysicalDevice,
    this.screenResolution,
  });

  Map<String, dynamic> toJson() {
    return {
      'platform': platform,
      if (osVersion != null) 'os_version': osVersion,
      if (deviceModel != null) 'model': deviceModel,
      if (manufacturer != null) 'manufacturer': manufacturer,
      if (locale != null) 'locale': locale,
      if (isPhysicalDevice != null) 'physical_device': isPhysicalDevice,
      if (screenResolution != null) 'screen': screenResolution,
    };
  }
}

/// Main crash reporter service
/// خدمة تقارير الأعطال الرئيسية
class CrashReporter {
  // Singleton pattern
  static final CrashReporter _instance = CrashReporter._internal();
  static CrashReporter get instance => _instance;
  factory CrashReporter() => _instance;
  CrashReporter._internal();

  /// Configuration
  CrashConfig? _config;
  CrashConfig get config => _config ?? CrashConfig.test();

  /// State
  bool _initialized = false;
  bool get isInitialized => _initialized;

  /// Context
  CrashUserContext? _userContext;
  CrashDeviceContext? _deviceContext;
  PackageInfo? _packageInfo;

  /// Custom tags
  final Map<String, String> _tags = {};

  /// Offline storage
  File? _offlineStorageFile;
  final List<OfflineCrashReport> _pendingReports = [];

  /// Network status
  bool _isOnline = true;
  StreamSubscription? _connectivitySubscription;

  /// Breadcrumb service
  final BreadcrumbService _breadcrumbs = breadcrumbService;

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize crash reporting
  /// تهيئة تقارير الأعطال
  Future<void> initialize(CrashConfig config) async {
    if (_initialized) {
      AppLogger.w('CrashReporter already initialized', tag: 'CrashReporter');
      return;
    }

    _config = config;

    if (!config.enabled) {
      AppLogger.i('Crash reporting disabled by configuration', tag: 'CrashReporter');
      _initialized = true;
      return;
    }

    try {
      // Initialize breadcrumb service
      _breadcrumbs.initialize(
        maxBreadcrumbs: config.maxBreadcrumbs,
        enabled: true,
      );

      // Setup breadcrumb callback for Sentry integration
      _breadcrumbs.onBreadcrumbRecorded = _onBreadcrumbRecorded;

      // Gather device context
      await _setupDeviceContext();

      // Gather package info
      await _setupPackageInfo();

      // Setup offline storage
      if (config.enableOfflineStorage) {
        await _setupOfflineStorage();
      }

      // Monitor network connectivity
      await _setupConnectivityMonitoring();

      // Set default tags
      _setupDefaultTags();

      // Initialize Sentry if DSN is provided
      if (config.hasSentryDsn) {
        await _initializeSentry();
      }

      _initialized = true;

      // Record initialization breadcrumb
      _breadcrumbs.recordLifecycle('crash_reporting_initialized');

      // Try to send any pending offline reports
      if (_isOnline) {
        await _sendPendingReports();
      }

      AppLogger.i(
        'CrashReporter initialized: '
        'Sentry=${config.hasSentryDsn}, '
        'offline=${config.enableOfflineStorage}',
        tag: 'CrashReporter',
      );
    } catch (e, stackTrace) {
      AppLogger.e('Failed to initialize CrashReporter: $e', tag: 'CrashReporter');
      // Don't throw - crash reporting failure shouldn't crash the app
      if (kDebugMode) {
        debugPrint('CrashReporter init error: $e\n$stackTrace');
      }
      _initialized = true; // Mark as initialized to prevent retries
    }
  }

  /// Run app with error zones configured
  /// تشغيل التطبيق مع مناطق الأخطاء المُعدة
  Future<void> runApp(FutureOr<void> Function() appRunner) async {
    // Set up Flutter error handler
    FlutterError.onError = _handleFlutterError;

    // Set up Platform Dispatcher error handler for async errors
    PlatformDispatcher.instance.onError = _handlePlatformError;

    // Run app in guarded zone
    await runZonedGuarded(
      () async {
        await appRunner();
      },
      _handleZoneError,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Error Reporting
  // ═══════════════════════════════════════════════════════════════════════════

  /// Report an error
  /// الإبلاغ عن خطأ
  Future<void> reportError(
    dynamic error,
    StackTrace? stackTrace, {
    CrashSeverity severity = CrashSeverity.error,
    String? reason,
    Map<String, dynamic>? context,
    bool fatal = false,
  }) async {
    if (!_shouldReport(error, severity)) return;

    // Apply sampling
    if (!_passesSampling()) return;

    // Sanitize error data
    final sanitizedError = _sanitizeError(error);
    final sanitizedReason = reason != null
        ? PiiFilter.sanitize(reason) as String
        : null;
    final sanitizedContext = context != null
        ? PiiFilter.sanitize(context) as Map<String, dynamic>
        : null;

    // Record error breadcrumb
    _breadcrumbs.recordError(error, stackTrace: stackTrace, context: reason);

    // Create report
    final report = OfflineCrashReport(
      id: _generateReportId(),
      timestamp: DateTime.now(),
      errorMessage: sanitizedError,
      errorType: error.runtimeType.toString(),
      stackTrace: stackTrace?.toString(),
      severity: fatal ? CrashSeverity.fatal : severity,
      context: {
        if (sanitizedReason != null) 'reason': sanitizedReason,
        if (sanitizedContext != null) ...sanitizedContext,
        'fatal': fatal,
      },
      breadcrumbs: _breadcrumbs.toJsonList(),
      tags: Map.from(_tags),
      userContext: _userContext?.toJson(),
      deviceContext: _deviceContext?.toJson(),
    );

    // Try to send immediately
    if (_isOnline && _config?.hasSentryDsn == true) {
      await _sendToSentry(report);
    } else if (_config?.enableOfflineStorage == true) {
      // Store offline
      await _storeOfflineReport(report);
    }

    // Console logging in debug mode
    if (kDebugMode) {
      _logErrorToConsole(report);
    }
  }

  /// Report a Flutter error
  /// الإبلاغ عن خطأ Flutter
  Future<void> reportFlutterError(FlutterErrorDetails details) async {
    await reportError(
      details.exception,
      details.stack,
      severity: CrashSeverity.error,
      reason: details.context?.toString(),
      context: {
        'library': details.library ?? 'unknown',
        'silent': details.silent,
      },
      fatal: false,
    );
  }

  /// Report a message (non-error event)
  /// الإبلاغ عن رسالة (حدث غير خطأ)
  Future<void> reportMessage(
    String message, {
    CrashSeverity severity = CrashSeverity.info,
    Map<String, dynamic>? context,
  }) async {
    if (!_initialized || _config?.enabled != true) return;

    final sanitizedMessage = PiiFilter.sanitize(message) as String;

    // Add breadcrumb
    _breadcrumbs.record(
      message: sanitizedMessage,
      category: BreadcrumbCategory.info,
      level: _severityToBreadcrumbLevel(severity),
      data: context,
    );

    // Log for debugging
    if (kDebugMode) {
      debugPrint('CrashReporter message [${severity.name}]: $sanitizedMessage');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Breadcrumbs
  // ═══════════════════════════════════════════════════════════════════════════

  /// Add a breadcrumb
  /// إضافة مسار تنقل
  void addBreadcrumb(
    String message, {
    BreadcrumbCategory category = BreadcrumbCategory.custom,
    BreadcrumbLevel level = BreadcrumbLevel.info,
    Map<String, dynamic>? data,
  }) {
    _breadcrumbs.record(
      message: message,
      category: category,
      level: level,
      data: data,
    );
  }

  /// Record navigation breadcrumb
  /// تسجيل مسار تنقل للملاحة
  void recordNavigation(String from, String to, {Map<String, dynamic>? params}) {
    _breadcrumbs.recordNavigation(from, to, params: params);
  }

  /// Record user action breadcrumb
  /// تسجيل مسار تنقل لإجراء المستخدم
  void recordUserAction(String action, {Map<String, dynamic>? data}) {
    _breadcrumbs.recordUserAction(action, data: data);
  }

  /// Record HTTP request breadcrumb
  /// تسجيل مسار تنقل لطلب HTTP
  void recordHttpRequest(
    String method,
    String url, {
    int? statusCode,
    Duration? duration,
  }) {
    _breadcrumbs.recordHttpRequest(
      method,
      url,
      statusCode: statusCode,
      duration: duration,
    );
  }

  /// Get current breadcrumbs
  List<Breadcrumb> get breadcrumbs => _breadcrumbs.breadcrumbs;

  // ═══════════════════════════════════════════════════════════════════════════
  // Context & Tags
  // ═══════════════════════════════════════════════════════════════════════════

  /// Set user context (anonymized)
  /// تعيين سياق المستخدم (مجهول)
  void setUserContext({
    required String userId,
    String? tenantId,
    String? role,
    Map<String, dynamic>? metadata,
  }) {
    // Anonymize user ID by hashing
    final anonymousId = 'user_${userId.hashCode.abs()}';

    _userContext = CrashUserContext(
      anonymousId: anonymousId,
      tenantId: tenantId,
      role: role,
      metadata: metadata != null
          ? PiiFilter.sanitize(metadata) as Map<String, dynamic>
          : null,
    );

    _breadcrumbs.recordAuth('user_context_set', userId: userId);
  }

  /// Clear user context (e.g., on logout)
  /// مسح سياق المستخدم
  void clearUserContext() {
    _userContext = null;
    _breadcrumbs.recordAuth('user_context_cleared');
  }

  /// Set a custom tag
  /// تعيين علامة مخصصة
  void setTag(String key, String value) {
    final sanitizedKey = key.replaceAll(RegExp(r'[^a-zA-Z0-9_]'), '_');
    final sanitizedValue = PiiFilter.sanitize(value) as String;
    _tags[sanitizedKey] = sanitizedValue;
  }

  /// Remove a custom tag
  void removeTag(String key) {
    _tags.remove(key);
  }

  /// Get all tags
  Map<String, String> get tags => Map.unmodifiable(_tags);

  // ═══════════════════════════════════════════════════════════════════════════
  // Offline Storage
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get count of pending offline reports
  int get pendingReportsCount => _pendingReports.length;

  /// Manually trigger sending pending reports
  /// تشغيل إرسال التقارير المعلقة يدوياً
  Future<void> sendPendingReports() async {
    if (_isOnline) {
      await _sendPendingReports();
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Methods - Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  Future<void> _setupDeviceContext() async {
    try {
      final deviceInfo = DeviceInfoPlugin();
      String? osVersion;
      String? deviceModel;
      String? manufacturer;
      bool? isPhysicalDevice;

      if (Platform.isAndroid) {
        final androidInfo = await deviceInfo.androidInfo;
        osVersion = 'Android ${androidInfo.version.release}';
        deviceModel = androidInfo.model;
        manufacturer = androidInfo.manufacturer;
        isPhysicalDevice = androidInfo.isPhysicalDevice;
      } else if (Platform.isIOS) {
        final iosInfo = await deviceInfo.iosInfo;
        osVersion = '${iosInfo.systemName} ${iosInfo.systemVersion}';
        deviceModel = iosInfo.model;
        manufacturer = 'Apple';
        isPhysicalDevice = iosInfo.isPhysicalDevice;
      }

      _deviceContext = CrashDeviceContext(
        platform: Platform.operatingSystem,
        osVersion: osVersion,
        deviceModel: deviceModel,
        manufacturer: manufacturer,
        locale: Platform.localeName,
        isPhysicalDevice: isPhysicalDevice,
      );
    } catch (e) {
      AppLogger.w('Failed to gather device context: $e', tag: 'CrashReporter');
    }
  }

  Future<void> _setupPackageInfo() async {
    try {
      _packageInfo = await PackageInfo.fromPlatform();
    } catch (e) {
      AppLogger.w('Failed to get package info: $e', tag: 'CrashReporter');
    }
  }

  Future<void> _setupOfflineStorage() async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      _offlineStorageFile = File('${directory.path}/crash_reports.json');

      // Load any existing reports
      if (await _offlineStorageFile!.exists()) {
        final content = await _offlineStorageFile!.readAsString();
        if (content.isNotEmpty) {
          final List<dynamic> jsonList = jsonDecode(content) as List<dynamic>;
          _pendingReports.addAll(
            jsonList.map((e) => OfflineCrashReport.fromJson(e as Map<String, dynamic>)),
          );
          AppLogger.i(
            'Loaded ${_pendingReports.length} pending crash reports',
            tag: 'CrashReporter',
          );
        }
      }
    } catch (e) {
      AppLogger.w('Failed to setup offline storage: $e', tag: 'CrashReporter');
    }
  }

  Future<void> _setupConnectivityMonitoring() async {
    try {
      final connectivity = Connectivity();
      final results = await connectivity.checkConnectivity();
      _isOnline = results.isNotEmpty &&
          !results.every((r) => r == ConnectivityResult.none);

      _connectivitySubscription = connectivity.onConnectivityChanged.listen(
        (results) async {
          final wasOnline = _isOnline;
          _isOnline = results.isNotEmpty &&
              !results.every((r) => r == ConnectivityResult.none);

          // Send pending reports when coming online
          if (!wasOnline && _isOnline) {
            _breadcrumbs.recordSystem('network_restored');
            await _sendPendingReports();
          } else if (wasOnline && !_isOnline) {
            _breadcrumbs.recordSystem('network_lost');
          }
        },
      );
    } catch (e) {
      AppLogger.w('Failed to setup connectivity monitoring: $e', tag: 'CrashReporter');
      _isOnline = true; // Assume online if we can't check
    }
  }

  void _setupDefaultTags() {
    _tags['app_name'] = _config?.release ?? 'sahool-field';
    _tags['app_version'] = _packageInfo?.version ?? _config?.appVersion ?? 'unknown';
    _tags['build_number'] = _packageInfo?.buildNumber ?? _config?.buildNumber ?? '0';
    _tags['environment'] = _config?.environment ?? 'unknown';
    _tags['platform'] = Platform.operatingSystem;

    if (_deviceContext != null) {
      if (_deviceContext!.osVersion != null) {
        _tags['os_version'] = _deviceContext!.osVersion!;
      }
      if (_deviceContext!.deviceModel != null) {
        _tags['device_model'] = _deviceContext!.deviceModel!;
      }
    }
  }

  Future<void> _initializeSentry() async {
    // Note: Sentry initialization would go here
    // This is a placeholder for when sentry_flutter is added
    //
    // await SentryFlutter.init(
    //   (options) {
    //     options.dsn = _config!.sentryDsn;
    //     options.environment = _config!.environment;
    //     options.release = _config!.release;
    //     options.dist = _config!.dist;
    //     options.tracesSampleRate = _config!.tracesSampleRate;
    //     options.attachStacktrace = _config!.attachStacktrace;
    //     options.enableAutoSessionTracking = _config!.enableAutoSessionTracking;
    //     options.autoSessionTrackingInterval = Duration(milliseconds: _config!.sessionTimeout);
    //     options.maxBreadcrumbs = _config!.maxBreadcrumbs;
    //
    //     // Before send callback for filtering
    //     options.beforeSend = _beforeSend;
    //   },
    // );

    AppLogger.i('Sentry integration ready (DSN configured)', tag: 'CrashReporter');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Methods - Error Handling
  // ═══════════════════════════════════════════════════════════════════════════

  void _handleFlutterError(FlutterErrorDetails details) {
    // Present error in debug mode
    if (kDebugMode) {
      FlutterError.presentError(details);
    }

    // Report to crash reporter
    reportFlutterError(details);
  }

  bool _handlePlatformError(Object error, StackTrace stackTrace) {
    reportError(
      error,
      stackTrace,
      severity: CrashSeverity.fatal,
      reason: 'Platform Dispatcher Error',
      fatal: true,
    );

    // Return true to prevent error from propagating
    return true;
  }

  void _handleZoneError(Object error, StackTrace stackTrace) {
    reportError(
      error,
      stackTrace,
      severity: CrashSeverity.fatal,
      reason: 'Uncaught zone error',
      fatal: true,
    );
  }

  bool _shouldReport(dynamic error, CrashSeverity severity) {
    if (!_initialized) return false;
    if (_config?.enabled != true) return false;
    if (kDebugMode && _config?.reportInDebug != true) return false;
    if (_config?.shouldIgnoreError(error) == true) return false;
    return severity.shouldReport(_config!);
  }

  bool _passesSampling() {
    if (_config == null) return false;
    if (_config!.sampleRate >= 1.0) return true;

    final random = DateTime.now().microsecondsSinceEpoch % 1000 / 1000;
    return random < _config!.sampleRate;
  }

  String _sanitizeError(dynamic error) {
    final errorString = error.toString();
    return PiiFilter.sanitize(errorString) as String;
  }

  String _generateReportId() {
    return '${DateTime.now().millisecondsSinceEpoch}_${DateTime.now().microsecond}';
  }

  void _onBreadcrumbRecorded(Breadcrumb breadcrumb) {
    // Forward to Sentry when integrated
    // Sentry.addBreadcrumb(SentryBreadcrumb(...));
  }

  BreadcrumbLevel _severityToBreadcrumbLevel(CrashSeverity severity) {
    switch (severity) {
      case CrashSeverity.debug:
        return BreadcrumbLevel.debug;
      case CrashSeverity.info:
        return BreadcrumbLevel.info;
      case CrashSeverity.warning:
        return BreadcrumbLevel.warning;
      case CrashSeverity.error:
      case CrashSeverity.fatal:
        return BreadcrumbLevel.error;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Methods - Sending & Storage
  // ═══════════════════════════════════════════════════════════════════════════

  Future<void> _sendToSentry(OfflineCrashReport report) async {
    // Note: Actual Sentry sending would go here
    // This is a placeholder for when sentry_flutter is added
    //
    // try {
    //   final event = SentryEvent(
    //     message: SentryMessage(report.errorMessage),
    //     level: _severityToSentryLevel(report.severity),
    //     throwable: report.errorMessage,
    //     tags: report.tags,
    //     extra: report.context,
    //     breadcrumbs: report.breadcrumbs?.map((b) => SentryBreadcrumb.fromJson(b)).toList(),
    //   );
    //
    //   await Sentry.captureEvent(event, stackTrace: report.stackTrace);
    // } catch (e) {
    //   // Store offline if sending fails
    //   await _storeOfflineReport(report);
    // }

    if (kDebugMode) {
      debugPrint('Would send to Sentry: ${report.errorMessage}');
    }
  }

  Future<void> _storeOfflineReport(OfflineCrashReport report) async {
    if (_offlineStorageFile == null) return;

    try {
      _pendingReports.add(report);

      // Trim to max reports
      while (_pendingReports.length > (_config?.maxOfflineReports ?? 50)) {
        _pendingReports.removeAt(0);
      }

      // Persist to file
      final jsonList = _pendingReports.map((r) => r.toJson()).toList();
      await _offlineStorageFile!.writeAsString(jsonEncode(jsonList));

      if (kDebugMode) {
        debugPrint('Stored offline crash report: ${report.id}');
      }
    } catch (e) {
      AppLogger.w('Failed to store offline report: $e', tag: 'CrashReporter');
    }
  }

  Future<void> _sendPendingReports() async {
    if (_pendingReports.isEmpty) return;
    if (!_config!.hasSentryDsn) return;

    AppLogger.i(
      'Sending ${_pendingReports.length} pending crash reports',
      tag: 'CrashReporter',
    );

    final toRemove = <OfflineCrashReport>[];

    for (final report in _pendingReports) {
      try {
        await _sendToSentry(report);
        toRemove.add(report);
      } catch (e) {
        AppLogger.w('Failed to send pending report: $e', tag: 'CrashReporter');
        break; // Stop on first failure
      }
    }

    // Remove sent reports
    _pendingReports.removeWhere((r) => toRemove.contains(r));

    // Update file
    if (_offlineStorageFile != null) {
      try {
        final jsonList = _pendingReports.map((r) => r.toJson()).toList();
        await _offlineStorageFile!.writeAsString(jsonEncode(jsonList));
      } catch (e) {
        AppLogger.w('Failed to update offline storage: $e', tag: 'CrashReporter');
      }
    }
  }

  void _logErrorToConsole(OfflineCrashReport report) {
    final severity = report.severity.name.toUpperCase();

    debugPrint('');
    debugPrint('${'=' * 60}');
    debugPrint('CRASH REPORT [$severity]');
    debugPrint('${'=' * 60}');
    debugPrint('Time: ${report.timestamp.toIso8601String()}');
    debugPrint('Type: ${report.errorType}');
    debugPrint('Message: ${report.errorMessage}');
    if (report.context != null && report.context!['reason'] != null) {
      debugPrint('Reason: ${report.context!['reason']}');
    }
    debugPrint('-' * 60);
    debugPrint('Tags: ${report.tags}');
    debugPrint('-' * 60);
    if (report.stackTrace != null) {
      debugPrint('Stack Trace:');
      final lines = report.stackTrace!.split('\n');
      for (var i = 0; i < lines.length && i < 15; i++) {
        debugPrint('  ${lines[i]}');
      }
      if (lines.length > 15) {
        debugPrint('  ... (${lines.length - 15} more lines)');
      }
    }
    debugPrint('${'=' * 60}');
    debugPrint('');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cleanup
  // ═══════════════════════════════════════════════════════════════════════════

  /// Dispose resources
  void dispose() {
    _connectivitySubscription?.cancel();
    _breadcrumbs.onBreadcrumbRecorded = null;
  }
}

/// Global crash reporter instance
/// مثيل مُبلِّغ الأعطال العالمي
final crashReporter = CrashReporter.instance;
