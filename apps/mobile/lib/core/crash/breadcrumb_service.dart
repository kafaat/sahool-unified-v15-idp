/// SAHOOL Breadcrumb Service
/// خدمة مسار التنقل للتصحيح
///
/// Provides breadcrumb tracking for debugging and crash analysis.
/// Breadcrumbs are recorded events that lead up to an error,
/// helping developers understand what the user did before a crash.
///
/// Features:
/// - Navigation breadcrumbs
/// - User action breadcrumbs
/// - Network request breadcrumbs
/// - System event breadcrumbs
/// - Custom breadcrumbs
/// - PII filtering
///
/// Usage:
/// ```dart
/// final breadcrumbs = BreadcrumbService();
///
/// // Record navigation
/// breadcrumbs.recordNavigation('/home', '/fields');
///
/// // Record user action
/// breadcrumbs.recordUserAction('tapped_button', data: {'button': 'save'});
///
/// // Record network request
/// breadcrumbs.recordHttpRequest('GET', '/api/fields', statusCode: 200);
/// ```
library;

import 'dart:collection';
import 'package:flutter/foundation.dart';
import '../utils/pii_filter.dart';

/// Breadcrumb category types
/// أنواع فئات مسار التنقل
enum BreadcrumbCategory {
  /// Navigation events (screen changes, route changes)
  navigation,

  /// User interaction events (taps, gestures, inputs)
  userAction,

  /// HTTP/network requests and responses
  http,

  /// Database operations
  database,

  /// Authentication events (login, logout, token refresh)
  auth,

  /// Lifecycle events (app start, background, resume)
  lifecycle,

  /// System events (memory warnings, low battery)
  system,

  /// Error events
  error,

  /// Debug/info events
  info,

  /// Custom events
  custom,
}

/// Breadcrumb severity level
/// مستوى خطورة مسار التنقل
enum BreadcrumbLevel {
  debug,
  info,
  warning,
  error,
  fatal,
}

/// Represents a single breadcrumb event
/// يمثل حدث مسار تنقل واحد
class Breadcrumb {
  /// Human-readable message describing the event
  final String message;

  /// When this breadcrumb was recorded
  final DateTime timestamp;

  /// Category of the breadcrumb
  final BreadcrumbCategory category;

  /// Severity level
  final BreadcrumbLevel level;

  /// Additional data associated with the breadcrumb
  /// (automatically sanitized for PII)
  final Map<String, dynamic>? data;

  /// Type identifier (e.g., 'http', 'navigation', 'user')
  final String? type;

  Breadcrumb({
    required this.message,
    DateTime? timestamp,
    this.category = BreadcrumbCategory.custom,
    this.level = BreadcrumbLevel.info,
    this.data,
    this.type,
  }) : timestamp = timestamp ?? DateTime.now();

  /// Convert to JSON for serialization
  Map<String, dynamic> toJson() {
    return {
      'message': message,
      'timestamp': timestamp.toIso8601String(),
      'category': category.name,
      'level': level.name,
      if (data != null) 'data': data,
      if (type != null) 'type': type,
    };
  }

  /// Create from JSON
  factory Breadcrumb.fromJson(Map<String, dynamic> json) {
    return Breadcrumb(
      message: json['message'] as String,
      timestamp: DateTime.tryParse(json['timestamp'] as String) ?? DateTime.now(),
      category: BreadcrumbCategory.values.firstWhere(
        (e) => e.name == json['category'],
        orElse: () => BreadcrumbCategory.custom,
      ),
      level: BreadcrumbLevel.values.firstWhere(
        (e) => e.name == json['level'],
        orElse: () => BreadcrumbLevel.info,
      ),
      data: json['data'] as Map<String, dynamic>?,
      type: json['type'] as String?,
    );
  }

  @override
  String toString() {
    return 'Breadcrumb(${category.name}): $message';
  }
}

/// Service for managing breadcrumbs
/// خدمة إدارة مسارات التنقل
class BreadcrumbService {
  static final BreadcrumbService _instance = BreadcrumbService._internal();
  factory BreadcrumbService() => _instance;
  BreadcrumbService._internal();

  /// Maximum number of breadcrumbs to keep
  int _maxBreadcrumbs = 100;

  /// Internal breadcrumb storage (circular buffer)
  final Queue<Breadcrumb> _breadcrumbs = Queue<Breadcrumb>();

  /// Whether breadcrumb recording is enabled
  bool _enabled = true;

  /// Callback when a breadcrumb is recorded
  void Function(Breadcrumb)? onBreadcrumbRecorded;

  /// Initialize the service with configuration
  void initialize({int maxBreadcrumbs = 100, bool enabled = true}) {
    _maxBreadcrumbs = maxBreadcrumbs;
    _enabled = enabled;
  }

  /// Enable or disable breadcrumb recording
  void setEnabled(bool enabled) {
    _enabled = enabled;
  }

  /// Set maximum breadcrumbs to store
  void setMaxBreadcrumbs(int max) {
    _maxBreadcrumbs = max;
    _trimBreadcrumbs();
  }

  /// Get all recorded breadcrumbs
  List<Breadcrumb> get breadcrumbs => List.unmodifiable(_breadcrumbs.toList());

  /// Get breadcrumbs as JSON list
  List<Map<String, dynamic>> toJsonList() {
    return _breadcrumbs.map((b) => b.toJson()).toList();
  }

  /// Clear all breadcrumbs
  void clear() {
    _breadcrumbs.clear();
  }

  /// Record a generic breadcrumb
  /// تسجيل مسار تنقل عام
  void record({
    required String message,
    BreadcrumbCategory category = BreadcrumbCategory.custom,
    BreadcrumbLevel level = BreadcrumbLevel.info,
    Map<String, dynamic>? data,
    String? type,
  }) {
    if (!_enabled) return;

    // Sanitize message and data for PII
    final sanitizedMessage = PiiFilter.sanitize(message) as String;
    final sanitizedData = data != null
        ? PiiFilter.sanitize(data) as Map<String, dynamic>
        : null;

    final breadcrumb = Breadcrumb(
      message: sanitizedMessage,
      category: category,
      level: level,
      data: sanitizedData,
      type: type ?? category.name,
    );

    _addBreadcrumb(breadcrumb);
  }

  /// Record a navigation event
  /// تسجيل حدث تنقل
  void recordNavigation(
    String from,
    String to, {
    Map<String, dynamic>? params,
  }) {
    record(
      message: 'Navigate: $from -> $to',
      category: BreadcrumbCategory.navigation,
      level: BreadcrumbLevel.info,
      type: 'navigation',
      data: {
        'from': from,
        'to': to,
        if (params != null) 'params': params,
      },
    );
  }

  /// Record a user action
  /// تسجيل إجراء مستخدم
  void recordUserAction(
    String action, {
    Map<String, dynamic>? data,
    BreadcrumbLevel level = BreadcrumbLevel.info,
  }) {
    record(
      message: 'User action: $action',
      category: BreadcrumbCategory.userAction,
      level: level,
      type: 'user',
      data: data,
    );
  }

  /// Record a button tap
  /// تسجيل نقرة زر
  void recordTap(String buttonName, {String? screen}) {
    recordUserAction(
      'tap',
      data: {
        'button': buttonName,
        if (screen != null) 'screen': screen,
      },
    );
  }

  /// Record form submission
  /// تسجيل إرسال نموذج
  void recordFormSubmit(String formName, {bool success = true}) {
    recordUserAction(
      'form_submit',
      level: success ? BreadcrumbLevel.info : BreadcrumbLevel.warning,
      data: {
        'form': formName,
        'success': success,
      },
    );
  }

  /// Record an HTTP request
  /// تسجيل طلب HTTP
  void recordHttpRequest(
    String method,
    String url, {
    int? statusCode,
    String? reason,
    int? requestSize,
    int? responseSize,
    Duration? duration,
  }) {
    final isError = statusCode != null && statusCode >= 400;

    record(
      message: '$method $url -> ${statusCode ?? 'pending'}',
      category: BreadcrumbCategory.http,
      level: isError ? BreadcrumbLevel.warning : BreadcrumbLevel.info,
      type: 'http',
      data: {
        'method': method,
        'url': _sanitizeUrl(url),
        if (statusCode != null) 'status_code': statusCode,
        if (reason != null) 'reason': reason,
        if (requestSize != null) 'request_body_size': requestSize,
        if (responseSize != null) 'response_body_size': responseSize,
        if (duration != null) 'duration_ms': duration.inMilliseconds,
      },
    );
  }

  /// Record a database operation
  /// تسجيل عملية قاعدة البيانات
  void recordDatabase(
    String operation,
    String table, {
    int? rowCount,
    Duration? duration,
    bool success = true,
  }) {
    record(
      message: 'DB: $operation on $table',
      category: BreadcrumbCategory.database,
      level: success ? BreadcrumbLevel.info : BreadcrumbLevel.warning,
      type: 'query',
      data: {
        'operation': operation,
        'table': table,
        if (rowCount != null) 'row_count': rowCount,
        if (duration != null) 'duration_ms': duration.inMilliseconds,
        'success': success,
      },
    );
  }

  /// Record an authentication event
  /// تسجيل حدث مصادقة
  void recordAuth(
    String event, {
    bool success = true,
    String? userId,
    Map<String, dynamic>? data,
  }) {
    record(
      message: 'Auth: $event',
      category: BreadcrumbCategory.auth,
      level: success ? BreadcrumbLevel.info : BreadcrumbLevel.warning,
      type: 'auth',
      data: {
        'event': event,
        'success': success,
        // Don't include actual userId, use anonymized version
        if (userId != null) 'user_id_hash': _hashUserId(userId),
        if (data != null) ...data,
      },
    );
  }

  /// Record app lifecycle event
  /// تسجيل حدث دورة حياة التطبيق
  void recordLifecycle(String event) {
    record(
      message: 'Lifecycle: $event',
      category: BreadcrumbCategory.lifecycle,
      level: BreadcrumbLevel.info,
      type: 'app',
      data: {'event': event},
    );
  }

  /// Record system event
  /// تسجيل حدث النظام
  void recordSystem(
    String event, {
    BreadcrumbLevel level = BreadcrumbLevel.info,
    Map<String, dynamic>? data,
  }) {
    record(
      message: 'System: $event',
      category: BreadcrumbCategory.system,
      level: level,
      type: 'system',
      data: data,
    );
  }

  /// Record an error occurrence
  /// تسجيل حدوث خطأ
  void recordError(
    dynamic error, {
    StackTrace? stackTrace,
    String? context,
  }) {
    final errorMessage = PiiFilter.sanitize(error.toString()) as String;

    record(
      message: 'Error: ${errorMessage.substring(0, errorMessage.length > 100 ? 100 : errorMessage.length)}',
      category: BreadcrumbCategory.error,
      level: BreadcrumbLevel.error,
      type: 'error',
      data: {
        'error_type': error.runtimeType.toString(),
        if (context != null) 'context': context,
        'has_stack_trace': stackTrace != null,
      },
    );
  }

  /// Record debug/info message
  /// تسجيل رسالة معلومات/تصحيح
  void recordInfo(String message, {Map<String, dynamic>? data}) {
    record(
      message: message,
      category: BreadcrumbCategory.info,
      level: BreadcrumbLevel.debug,
      type: 'debug',
      data: data,
    );
  }

  /// Record a warning
  /// تسجيل تحذير
  void recordWarning(String message, {Map<String, dynamic>? data}) {
    record(
      message: message,
      category: BreadcrumbCategory.info,
      level: BreadcrumbLevel.warning,
      type: 'warning',
      data: data,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private methods
  // ═══════════════════════════════════════════════════════════════════════════

  void _addBreadcrumb(Breadcrumb breadcrumb) {
    _breadcrumbs.add(breadcrumb);
    _trimBreadcrumbs();

    // Notify listener
    onBreadcrumbRecorded?.call(breadcrumb);

    // Debug logging
    if (kDebugMode) {
      debugPrint('Breadcrumb: [${breadcrumb.category.name}] ${breadcrumb.message}');
    }
  }

  void _trimBreadcrumbs() {
    while (_breadcrumbs.length > _maxBreadcrumbs) {
      _breadcrumbs.removeFirst();
    }
  }

  /// Sanitize URL to remove sensitive query parameters
  String _sanitizeUrl(String url) {
    try {
      final uri = Uri.parse(url);
      final sanitizedParams = <String, String>{};

      for (final entry in uri.queryParameters.entries) {
        final key = entry.key.toLowerCase();
        if (_sensitiveQueryParams.contains(key)) {
          sanitizedParams[entry.key] = '[REDACTED]';
        } else {
          sanitizedParams[entry.key] = entry.value;
        }
      }

      return uri.replace(queryParameters: sanitizedParams.isEmpty ? null : sanitizedParams).toString();
    } catch (e) {
      return url;
    }
  }

  /// Hash user ID for anonymization
  String _hashUserId(String userId) {
    // Simple hash for anonymization - not for security
    final hash = userId.hashCode.abs();
    return 'user_$hash';
  }

  static const Set<String> _sensitiveQueryParams = {
    'token',
    'access_token',
    'api_key',
    'apikey',
    'auth',
    'password',
    'secret',
    'key',
  };
}

/// Global breadcrumb service instance
/// مثيل خدمة مسار التنقل العالمية
final breadcrumbService = BreadcrumbService();

/// Extension to easily record navigation breadcrumbs
extension NavigationBreadcrumbExtension on BreadcrumbService {
  /// Record screen view
  void recordScreenView(String screenName, {Map<String, dynamic>? params}) {
    record(
      message: 'Screen: $screenName',
      category: BreadcrumbCategory.navigation,
      level: BreadcrumbLevel.info,
      type: 'navigation',
      data: {
        'screen': screenName,
        if (params != null) 'params': params,
      },
    );
  }

  /// Record modal open
  void recordModalOpen(String modalName) {
    record(
      message: 'Modal opened: $modalName',
      category: BreadcrumbCategory.navigation,
      level: BreadcrumbLevel.info,
      type: 'navigation',
      data: {'modal': modalName},
    );
  }

  /// Record modal close
  void recordModalClose(String modalName) {
    record(
      message: 'Modal closed: $modalName',
      category: BreadcrumbCategory.navigation,
      level: BreadcrumbLevel.info,
      type: 'navigation',
      data: {'modal': modalName},
    );
  }
}

/// Extension for field-specific breadcrumbs
extension FieldBreadcrumbExtension on BreadcrumbService {
  /// Record field selection
  void recordFieldSelection(String fieldId) {
    recordUserAction(
      'field_selected',
      data: {'field_id': fieldId},
    );
  }

  /// Record field creation
  void recordFieldCreation(String fieldId, {String? cropType}) {
    recordUserAction(
      'field_created',
      data: {
        'field_id': fieldId,
        if (cropType != null) 'crop_type': cropType,
      },
    );
  }

  /// Record sync operation
  void recordSync(String type, {bool success = true, int? itemCount}) {
    record(
      message: 'Sync: $type ${success ? 'completed' : 'failed'}',
      category: BreadcrumbCategory.system,
      level: success ? BreadcrumbLevel.info : BreadcrumbLevel.warning,
      type: 'sync',
      data: {
        'sync_type': type,
        'success': success,
        if (itemCount != null) 'item_count': itemCount,
      },
    );
  }
}
