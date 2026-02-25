import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../auth/secure_storage_service.dart';
import '../utils/app_logger.dart';

/// SAHOOL Security Audit Service
/// خدمة تدقيق الأمان وتسجيل الأحداث الأمنية
///
/// Records security events locally for:
/// - Biometric authentication attempts (success/failure/lockout)
/// - Token refresh events (success/failure/backoff)
/// - Session lifecycle events (login/logout/expiry/idle)
/// - Device integrity checks (root detection, emulator, tamper)
/// - Certificate pinning events (validation pass/fail/expiry)
///
/// Events are stored locally and synced to server when online.
/// Supports retention policy (default 30 days) and summary statistics.

final securityAuditServiceProvider = Provider<SecurityAuditService>((ref) {
  return SecurityAuditService(
    secureStorage: ref.read(secureStorageProvider),
  );
});

/// Security event severity levels
enum SecuritySeverity {
  info,
  warning,
  critical,
}

/// Security event categories
enum SecurityEventCategory {
  biometric,
  tokenRefresh,
  session,
  deviceIntegrity,
  certificatePinning,
  encryption,
  requestSigning,
}

/// A recorded security event
class SecurityEvent {
  final String id;
  final DateTime timestamp;
  final SecurityEventCategory category;
  final SecuritySeverity severity;
  final String action;
  final bool success;
  final String? details;
  final String? errorCode;
  final Map<String, dynamic>? metadata;

  const SecurityEvent({
    required this.id,
    required this.timestamp,
    required this.category,
    required this.severity,
    required this.action,
    required this.success,
    this.details,
    this.errorCode,
    this.metadata,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'timestamp': timestamp.toIso8601String(),
      'category': category.name,
      'severity': severity.name,
      'action': action,
      'success': success,
      if (details != null) 'details': details,
      if (errorCode != null) 'errorCode': errorCode,
      if (metadata != null) 'metadata': metadata,
    };
  }

  factory SecurityEvent.fromJson(Map<String, dynamic> json) {
    return SecurityEvent(
      id: json['id'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      category: SecurityEventCategory.values.firstWhere(
        (e) => e.name == json['category'],
        orElse: () => SecurityEventCategory.session,
      ),
      severity: SecuritySeverity.values.firstWhere(
        (e) => e.name == json['severity'],
        orElse: () => SecuritySeverity.info,
      ),
      action: json['action'] as String,
      success: json['success'] as bool,
      details: json['details'] as String?,
      errorCode: json['errorCode'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }
}

/// Security audit summary statistics
class SecurityAuditSummary {
  final int totalEvents;
  final int biometricAttempts;
  final int biometricSuccesses;
  final int biometricFailures;
  final int biometricLockouts;
  final int tokenRefreshAttempts;
  final int tokenRefreshSuccesses;
  final int tokenRefreshFailures;
  final int sessionLogins;
  final int sessionLogouts;
  final int sessionExpiries;
  final int criticalEvents;
  final DateTime? lastEventTime;

  const SecurityAuditSummary({
    this.totalEvents = 0,
    this.biometricAttempts = 0,
    this.biometricSuccesses = 0,
    this.biometricFailures = 0,
    this.biometricLockouts = 0,
    this.tokenRefreshAttempts = 0,
    this.tokenRefreshSuccesses = 0,
    this.tokenRefreshFailures = 0,
    this.sessionLogins = 0,
    this.sessionLogouts = 0,
    this.sessionExpiries = 0,
    this.criticalEvents = 0,
    this.lastEventTime,
  });

  /// Biometric success rate (0.0 - 1.0)
  double get biometricSuccessRate =>
      biometricAttempts > 0 ? biometricSuccesses / biometricAttempts : 0.0;

  /// Token refresh success rate (0.0 - 1.0)
  double get tokenRefreshSuccessRate => tokenRefreshAttempts > 0
      ? tokenRefreshSuccesses / tokenRefreshAttempts
      : 0.0;
}

class SecurityAuditService {
  final SecureStorageService secureStorage;

  // Local event buffer (in-memory for current session)
  final List<SecurityEvent> _eventBuffer = [];

  // Storage key for persisted events
  static const _eventsKey = 'security_audit_events';

  // Retention policy
  static const _maxLocalEvents = 500;
  static const _retentionDays = 30;

  SecurityAuditService({required this.secureStorage});

  // ═══════════════════════════════════════════════════════════════════════════
  // Event Logging
  // ═══════════════════════════════════════════════════════════════════════════

  /// Record a biometric authentication event
  Future<void> logBiometricAttempt({
    required bool success,
    String? errorCode,
    String? biometricType,
    int? remainingAttempts,
  }) async {
    final severity = success
        ? SecuritySeverity.info
        : (errorCode == 'LOCKED_OUT'
            ? SecuritySeverity.critical
            : SecuritySeverity.warning);

    await _recordEvent(SecurityEvent(
      id: _generateId(),
      timestamp: DateTime.now(),
      category: SecurityEventCategory.biometric,
      severity: severity,
      action: success ? 'biometric_success' : 'biometric_failure',
      success: success,
      errorCode: errorCode,
      details: success ? 'تم التحقق من البصمة بنجاح' : 'فشل التحقق من البصمة',
      metadata: {
        if (biometricType != null) 'type': biometricType,
        if (remainingAttempts != null) 'remainingAttempts': remainingAttempts,
      },
    ));
  }

  /// Record a biometric lockout event
  Future<void> logBiometricLockout({
    required Duration lockoutDuration,
    required int failedAttempts,
  }) async {
    await _recordEvent(SecurityEvent(
      id: _generateId(),
      timestamp: DateTime.now(),
      category: SecurityEventCategory.biometric,
      severity: SecuritySeverity.critical,
      action: 'biometric_lockout',
      success: false,
      details: 'تم قفل البصمة بعد $failedAttempts محاولات فاشلة',
      metadata: {
        'lockoutDurationMinutes': lockoutDuration.inMinutes,
        'failedAttempts': failedAttempts,
      },
    ));
  }

  /// Record a token refresh event
  Future<void> logTokenRefresh({
    required bool success,
    String? errorCode,
    int? retryAttempt,
    Duration? backoffDelay,
  }) async {
    await _recordEvent(SecurityEvent(
      id: _generateId(),
      timestamp: DateTime.now(),
      category: SecurityEventCategory.tokenRefresh,
      severity: success ? SecuritySeverity.info : SecuritySeverity.warning,
      action: success ? 'token_refresh_success' : 'token_refresh_failure',
      success: success,
      errorCode: errorCode,
      details: success ? 'تم تجديد التوكن بنجاح' : 'فشل تجديد التوكن',
      metadata: {
        if (retryAttempt != null) 'retryAttempt': retryAttempt,
        if (backoffDelay != null) 'backoffDelayMs': backoffDelay.inMilliseconds,
      },
    ));
  }

  /// Record a session lifecycle event
  Future<void> logSessionEvent({
    required String action,
    required bool success,
    String? reason,
  }) async {
    final severity = action.contains('expired') || action.contains('forced')
        ? SecuritySeverity.warning
        : SecuritySeverity.info;

    await _recordEvent(SecurityEvent(
      id: _generateId(),
      timestamp: DateTime.now(),
      category: SecurityEventCategory.session,
      severity: severity,
      action: action,
      success: success,
      details: reason,
    ));
  }

  /// Record a device integrity check event
  Future<void> logDeviceIntegrityCheck({
    required bool passed,
    List<String>? threats,
  }) async {
    await _recordEvent(SecurityEvent(
      id: _generateId(),
      timestamp: DateTime.now(),
      category: SecurityEventCategory.deviceIntegrity,
      severity: passed ? SecuritySeverity.info : SecuritySeverity.critical,
      action: passed ? 'integrity_check_passed' : 'integrity_check_failed',
      success: passed,
      details: passed ? 'فحص سلامة الجهاز ناجح' : 'تم اكتشاف تهديدات أمنية',
      metadata: {
        if (threats != null && threats.isNotEmpty) 'threats': threats,
      },
    ));
  }

  /// Record a certificate pinning event
  Future<void> logCertificatePinning({
    required bool success,
    String? domain,
    String? reason,
  }) async {
    await _recordEvent(SecurityEvent(
      id: _generateId(),
      timestamp: DateTime.now(),
      category: SecurityEventCategory.certificatePinning,
      severity: success ? SecuritySeverity.info : SecuritySeverity.critical,
      action: success ? 'pin_validation_passed' : 'pin_validation_failed',
      success: success,
      details: reason,
      metadata: {
        if (domain != null) 'domain': domain,
      },
    ));
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Query & Summary
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get recent security events
  List<SecurityEvent> getRecentEvents({int limit = 50}) {
    final events = List<SecurityEvent>.from(_eventBuffer);
    events.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return events.take(limit).toList();
  }

  /// Get events by category
  List<SecurityEvent> getEventsByCategory(SecurityEventCategory category) {
    return _eventBuffer.where((e) => e.category == category).toList()
      ..sort((a, b) => b.timestamp.compareTo(a.timestamp));
  }

  /// Get critical events
  List<SecurityEvent> getCriticalEvents() {
    return _eventBuffer
        .where((e) => e.severity == SecuritySeverity.critical)
        .toList()
      ..sort((a, b) => b.timestamp.compareTo(a.timestamp));
  }

  /// Generate summary statistics from current session events
  SecurityAuditSummary getSummary() {
    int biometricAttempts = 0;
    int biometricSuccesses = 0;
    int biometricFailures = 0;
    int biometricLockouts = 0;
    int tokenRefreshAttempts = 0;
    int tokenRefreshSuccesses = 0;
    int tokenRefreshFailures = 0;
    int sessionLogins = 0;
    int sessionLogouts = 0;
    int sessionExpiries = 0;
    int criticalEvents = 0;
    DateTime? lastEventTime;

    for (final event in _eventBuffer) {
      if (lastEventTime == null || event.timestamp.isAfter(lastEventTime)) {
        lastEventTime = event.timestamp;
      }

      if (event.severity == SecuritySeverity.critical) criticalEvents++;

      switch (event.category) {
        case SecurityEventCategory.biometric:
          if (event.action == 'biometric_lockout') {
            biometricLockouts++;
          } else {
            biometricAttempts++;
            if (event.success) {
              biometricSuccesses++;
            } else {
              biometricFailures++;
            }
          }
          break;

        case SecurityEventCategory.tokenRefresh:
          tokenRefreshAttempts++;
          if (event.success) {
            tokenRefreshSuccesses++;
          } else {
            tokenRefreshFailures++;
          }
          break;

        case SecurityEventCategory.session:
          if (event.action.contains('login')) sessionLogins++;
          if (event.action.contains('logout')) sessionLogouts++;
          if (event.action.contains('expired')) sessionExpiries++;
          break;

        default:
          break;
      }
    }

    return SecurityAuditSummary(
      totalEvents: _eventBuffer.length,
      biometricAttempts: biometricAttempts,
      biometricSuccesses: biometricSuccesses,
      biometricFailures: biometricFailures,
      biometricLockouts: biometricLockouts,
      tokenRefreshAttempts: tokenRefreshAttempts,
      tokenRefreshSuccesses: tokenRefreshSuccesses,
      tokenRefreshFailures: tokenRefreshFailures,
      sessionLogins: sessionLogins,
      sessionLogouts: sessionLogouts,
      sessionExpiries: sessionExpiries,
      criticalEvents: criticalEvents,
      lastEventTime: lastEventTime,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Persistence
  // ═══════════════════════════════════════════════════════════════════════════

  /// Save events to secure storage
  Future<void> persistEvents() async {
    try {
      // Apply retention policy
      _applyRetentionPolicy();

      final eventsJson = _eventBuffer.map((e) => e.toJson()).toList();
      await secureStorage.write(
        _eventsKey,
        jsonEncode(eventsJson),
      );

      AppLogger.d(
        'Persisted ${_eventBuffer.length} security events',
        tag: 'SECURITY_AUDIT',
      );
    } catch (e) {
      AppLogger.e('Failed to persist security events',
          error: e, tag: 'SECURITY_AUDIT');
    }
  }

  /// Load events from secure storage
  Future<void> loadEvents() async {
    try {
      final stored = await secureStorage.read(_eventsKey);
      if (stored == null) return;

      final eventsJson = jsonDecode(stored) as List<dynamic>;
      _eventBuffer.clear();
      _eventBuffer.addAll(
        eventsJson
            .map((e) => SecurityEvent.fromJson(e as Map<String, dynamic>)),
      );

      // Apply retention after loading
      _applyRetentionPolicy();

      AppLogger.d(
        'Loaded ${_eventBuffer.length} security events',
        tag: 'SECURITY_AUDIT',
      );
    } catch (e) {
      AppLogger.e('Failed to load security events',
          error: e, tag: 'SECURITY_AUDIT');
    }
  }

  /// Export events for server sync
  Future<List<Map<String, dynamic>>> exportForSync() async {
    return _eventBuffer.map((e) => e.toJson()).toList();
  }

  /// Clear all events after successful sync
  Future<void> clearSyncedEvents() async {
    _eventBuffer.clear();
    await secureStorage.write(_eventsKey, jsonEncode([]));
    AppLogger.i('Security events cleared after sync', tag: 'SECURITY_AUDIT');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Internal
  // ═══════════════════════════════════════════════════════════════════════════

  Future<void> _recordEvent(SecurityEvent event) async {
    _eventBuffer.add(event);

    // Log to AppLogger for immediate visibility
    final logMsg = '[${event.category.name}] ${event.action}'
        '${event.success ? ' ✓' : ' ✗'}'
        '${event.errorCode != null ? ' (${event.errorCode})' : ''}';

    switch (event.severity) {
      case SecuritySeverity.critical:
        AppLogger.e(logMsg, tag: 'SECURITY_AUDIT');
        break;
      case SecuritySeverity.warning:
        AppLogger.w(logMsg, tag: 'SECURITY_AUDIT');
        break;
      case SecuritySeverity.info:
        AppLogger.d(logMsg, tag: 'SECURITY_AUDIT');
        break;
    }

    // Trim buffer if too large
    if (_eventBuffer.length > _maxLocalEvents) {
      _eventBuffer.removeRange(0, _eventBuffer.length - _maxLocalEvents);
    }
  }

  void _applyRetentionPolicy() {
    final cutoff =
        DateTime.now().subtract(const Duration(days: _retentionDays));
    _eventBuffer.removeWhere((e) => e.timestamp.isBefore(cutoff));
  }

  String _generateId() {
    final now = DateTime.now();
    return 'sec_${now.millisecondsSinceEpoch}_${now.microsecond}';
  }
}
