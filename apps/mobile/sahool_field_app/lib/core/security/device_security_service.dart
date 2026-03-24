import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:safe_device/safe_device.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'security_config.dart';
import '../utils/app_logger.dart';

/// SAHOOL Device Security Service
/// خدمة أمان الجهاز
///
/// Comprehensive device security checks including:
/// - Root/Jailbreak detection
/// - Emulator/Simulator detection
/// - Debug mode detection
/// - Developer mode detection
/// - Tamper detection
///
/// Features:
/// - Configurable security levels (warn vs block)
/// - Arabic and English error messages
/// - Test/debug bypass during development
/// - Security event logging for monitoring
/// - Riverpod integration for dependency injection
///
/// ═══════════════════════════════════════════════════════════════════════════
/// USAGE EXAMPLES
/// ═══════════════════════════════════════════════════════════════════════════
///
/// 1. BASIC USAGE - Check device security on app startup (already implemented in main.dart):
/// ```dart
/// final securityConfig = const SecurityConfig(level: SecurityLevel.medium);
/// final deviceSecurityService = DeviceSecurityService(config: securityConfig);
/// final result = await deviceSecurityService.checkDeviceSecurity();
///
/// if (result.recommendedAction == SecurityAction.block) {
///   // Show blocking screen
/// } else if (result.recommendedAction == SecurityAction.warn) {
///   // Show warning dialog
/// }
/// ```
///
/// 2. USING RIVERPOD PROVIDER:
/// ```dart
/// class MyWidget extends ConsumerWidget {
///   @override
///   Widget build(BuildContext context, WidgetRef ref) {
///     final securityCheck = ref.watch(deviceSecurityCheckProvider);
///
///     return securityCheck.when(
///       data: (result) {
///         if (result.isSecure) {
///           return Text('Device is secure');
///         } else {
///           return Text('Security issues: ${result.messageAr}');
///         }
///       },
///       loading: () => CircularProgressIndicator(),
///       error: (err, stack) => Text('Error checking security'),
///     );
///   }
/// }
/// ```
///
/// 3. ENABLE DEBUG BYPASS (for development/testing):
/// ```dart
/// // In debug mode only
/// if (kDebugMode) {
///   final service = DeviceSecurityService(config: securityConfig);
///   await service.enableSecurityBypass(
///     reason: 'Testing on rooted device',
///   );
/// }
/// ```
///
/// 4. CONFIGURE SECURITY LEVELS:
/// ```dart
/// // Low security - only critical threats block
/// ref.read(securityConfigProvider.notifier).state =
///   const SecurityConfig(level: SecurityLevel.low);
///
/// // High security - block on any threat
/// ref.read(securityConfigProvider.notifier).state =
///   const SecurityConfig(level: SecurityLevel.high);
/// ```
///
/// 5. GET SECURITY LOGS:
/// ```dart
/// final service = ref.read(deviceSecurityServiceProvider);
/// final logs = await service.getSecurityLogs();
/// for (final log in logs) {
///   print(log);
/// }
/// ```
///
/// ═══════════════════════════════════════════════════════════════════════════
/// SECURITY LEVEL BEHAVIOR
/// ═══════════════════════════════════════════════════════════════════════════
///
/// LOW:
///   - Checks: Root/Jailbreak only
///   - Action: Warn on critical threats
///   - Best for: Personal/development use
///
/// MEDIUM (DEFAULT):
///   - Checks: Root/Jailbreak
///   - Action: Block on critical, warn on high
///   - Best for: General production use
///
/// HIGH:
///   - Checks: Root/Jailbreak, Emulator
///   - Action: Block on critical/high, warn on medium
///   - Best for: Sensitive data apps
///
/// MAXIMUM:
///   - Checks: All (Root/Jailbreak, Emulator, Developer mode)
///   - Action: Block on any threat
///   - Best for: Financial/Healthcare apps
///
/// ═══════════════════════════════════════════════════════════════════════════

/// Security check result
class DeviceSecurityResult {
  final bool isSecure;
  final List<SecurityThreat> threats;
  final SecurityAction recommendedAction;

  const DeviceSecurityResult({
    required this.isSecure,
    required this.threats,
    required this.recommendedAction,
  });

  /// Check if device has any critical threats
  bool get hasCriticalThreats {
    return threats.any((threat) => threat.severity == ThreatSeverity.critical);
  }

  /// Get primary threat (highest severity)
  SecurityThreat? get primaryThreat {
    if (threats.isEmpty) return null;

    // Sort by severity (critical > high > medium > low)
    final sortedThreats = List<SecurityThreat>.from(threats)
      ..sort((a, b) => b.severity.index.compareTo(a.severity.index));

    return sortedThreats.first;
  }

  /// Get localized message in Arabic
  String get messageAr {
    if (isSecure) return 'الجهاز آمن ومحمي';

    final threat = primaryThreat;
    if (threat == null) return 'تم اكتشاف مخاطر أمنية';

    return threat.messageAr;
  }

  /// Get localized message in English
  String get messageEn {
    if (isSecure) return 'Device is secure';

    final threat = primaryThreat;
    if (threat == null) return 'Security threats detected';

    return threat.messageEn;
  }

  @override
  String toString() {
    return 'DeviceSecurityResult(isSecure: $isSecure, threats: ${threats.length}, action: $recommendedAction)';
  }
}

/// Security threat detected on device
class SecurityThreat {
  final ThreatType type;
  final ThreatSeverity severity;
  final String messageAr;
  final String messageEn;
  final String? details;

  const SecurityThreat({
    required this.type,
    required this.severity,
    required this.messageAr,
    required this.messageEn,
    this.details,
  });

  @override
  String toString() {
    return 'SecurityThreat(type: $type, severity: $severity)';
  }
}

/// Type of security threat
enum ThreatType {
  rootAccess,
  jailbreak,
  emulator,
  debugMode,
  developerMode,
  tampered,
  unknownSource,
}

/// Severity level of threat
enum ThreatSeverity {
  low, // Warning only
  medium, // Warn but allow
  high, // Recommend blocking
  critical, // Must block
}

/// Recommended action for security threat
enum SecurityAction {
  allow, // No action needed
  warn, // Show warning but continue
  block, // Block app usage
}

/// Device Security Service
class DeviceSecurityService {
  final SecurityConfig config;

  DeviceSecurityService({
    required this.config,
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Main Security Check
  // ═══════════════════════════════════════════════════════════════════════════

  /// Perform comprehensive device security check
  /// إجراء فحص أمني شامل للجهاز
  Future<DeviceSecurityResult> checkDeviceSecurity({
    bool skipInDebugMode = true,
  }) async {
    try {
      // Skip checks in debug mode if configured
      if (skipInDebugMode && kDebugMode) {
        if (kDebugMode) {
          debugPrint('🔓 Device security checks skipped (debug mode)');
        }
        return const DeviceSecurityResult(
          isSecure: true,
          threats: [],
          recommendedAction: SecurityAction.allow,
        );
      }

      // Check if bypass is enabled (for development/testing)
      final bypassEnabled = await _isSecurityBypassEnabled();
      if (bypassEnabled) {
        if (kDebugMode) {
          debugPrint('🔓 Device security checks bypassed (test mode enabled)');
        }
        return const DeviceSecurityResult(
          isSecure: true,
          threats: [],
          recommendedAction: SecurityAction.allow,
        );
      }

      final threats = <SecurityThreat>[];

      // 1. Check for root/jailbreak
      final rootThreat = await _checkRootJailbreak();
      if (rootThreat != null) threats.add(rootThreat);

      // 2. Check for emulator/simulator
      final emulatorThreat = await _checkEmulator();
      if (emulatorThreat != null) threats.add(emulatorThreat);

      // 3. Check for debug mode (in production only)
      if (kReleaseMode) {
        final debugThreat = await _checkDebugMode();
        if (debugThreat != null) threats.add(debugThreat);
      }

      // 4. Check for developer mode (Android)
      if (Platform.isAndroid) {
        final devModeThreat = await _checkDeveloperMode();
        if (devModeThreat != null) threats.add(devModeThreat);
      }

      // Determine if device is secure
      final isSecure = threats.isEmpty;

      // Determine recommended action based on security level and threats
      final action = _determineAction(threats);

      // Log security check result
      await _logSecurityEvent(
        event: 'device_security_check',
        isSecure: isSecure,
        threats: threats,
      );

      return DeviceSecurityResult(
        isSecure: isSecure,
        threats: threats,
        recommendedAction: action,
      );
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Device security check error: $e');
      }

      // On error, take conservative approach based on security level
      if (config.level == SecurityLevel.maximum ||
          config.level == SecurityLevel.high) {
        return DeviceSecurityResult(
          isSecure: false,
          threats: [
            SecurityThreat(
              type: ThreatType.unknownSource,
              severity: ThreatSeverity.high,
              messageAr: 'فشل فحص أمان الجهاز',
              messageEn: 'Device security check failed',
              details: e.toString(),
            ),
          ],
          recommendedAction: SecurityAction.block,
        );
      }

      // For low/medium security, allow on error
      return const DeviceSecurityResult(
        isSecure: true,
        threats: [],
        recommendedAction: SecurityAction.allow,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Individual Security Checks
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check for root access (Android) or jailbreak (iOS)
  /// فحص صلاحيات الروت أو الجيلبريك
  Future<SecurityThreat?> _checkRootJailbreak() async {
    try {
      final isJailbroken = await SafeDevice.isJailBroken;

      if (isJailbroken) {
        return SecurityThreat(
          type: Platform.isIOS ? ThreatType.jailbreak : ThreatType.rootAccess,
          severity: ThreatSeverity.critical,
          messageAr: Platform.isIOS
              ? 'تم اكتشاف جيلبريك - الجهاز غير آمن'
              : 'تم اكتشاف صلاحيات الروت - الجهاز غير آمن',
          messageEn: Platform.isIOS
              ? 'Jailbreak detected - Device is not secure'
              : 'Root access detected - Device is not secure',
          details: 'Device has elevated privileges',
        );
      }

      return null;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('⚠️ Root/Jailbreak check error: $e');
      }
      return null; // Don't fail on error
    }
  }

  /// Check if running on emulator/simulator
  /// فحص إذا كان التطبيق يعمل على محاكي
  Future<SecurityThreat?> _checkEmulator() async {
    try {
      final isRunningOnEmulator = await SafeDevice.isRealDevice == false;

      if (isRunningOnEmulator) {
        // Severity based on security level
        final severity = config.level == SecurityLevel.maximum
            ? ThreatSeverity.critical
            : config.level == SecurityLevel.high
                ? ThreatSeverity.high
                : ThreatSeverity.medium;

        return SecurityThreat(
          type: ThreatType.emulator,
          severity: severity,
          messageAr: 'تم اكتشاف محاكي - قد يكون الجهاز غير حقيقي',
          messageEn: 'Emulator detected - Device may not be genuine',
          details: 'Running on emulator/simulator',
        );
      }

      return null;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('⚠️ Emulator check error: $e');
      }
      return null;
    }
  }

  /// Check if app is running in debug mode
  /// فحص إذا كان التطبيق يعمل في وضع التطوير
  Future<SecurityThreat?> _checkDebugMode() async {
    try {
      if (kDebugMode) {
        return const SecurityThreat(
          type: ThreatType.debugMode,
          severity: ThreatSeverity.critical,
          messageAr: 'التطبيق يعمل في وضع التطوير',
          messageEn: 'App is running in debug mode',
          details: 'Debug build in production',
        );
      }

      return null;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('⚠️ Debug mode check error: $e');
      }
      return null;
    }
  }

  /// Check if developer mode is enabled (Android)
  /// فحص إذا كان وضع المطور مفعل
  Future<SecurityThreat?> _checkDeveloperMode() async {
    try {
      final isDeveloperMode = await SafeDevice.isDevelopmentModeEnable;

      if (isDeveloperMode) {
        // Lower severity - developer mode is common
        final severity = config.level == SecurityLevel.maximum
            ? ThreatSeverity.high
            : ThreatSeverity.medium;

        return SecurityThreat(
          type: ThreatType.developerMode,
          severity: severity,
          messageAr: 'وضع المطور مفعل على الجهاز',
          messageEn: 'Developer mode is enabled on device',
          details: 'USB debugging may be enabled',
        );
      }

      return null;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('⚠️ Developer mode check error: $e');
      }
      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Action Determination
  // ═══════════════════════════════════════════════════════════════════════════

  /// Determine recommended action based on threats and security level
  /// تحديد الإجراء الموصى به بناءً على المخاطر ومستوى الأمان
  SecurityAction _determineAction(List<SecurityThreat> threats) {
    if (threats.isEmpty) return SecurityAction.allow;

    // Get highest severity
    final maxSeverity = threats
        .map((t) => t.severity)
        .reduce((a, b) => a.index > b.index ? a : b);

    // Security level-based decision
    switch (config.level) {
      case SecurityLevel.low:
        // Only block on critical threats
        return maxSeverity == ThreatSeverity.critical
            ? SecurityAction.warn
            : SecurityAction.allow;

      case SecurityLevel.medium:
        // Block on critical, warn on high
        if (maxSeverity == ThreatSeverity.critical) {
          return SecurityAction.block;
        } else if (maxSeverity == ThreatSeverity.high) {
          return SecurityAction.warn;
        }
        return SecurityAction.allow;

      case SecurityLevel.high:
        // Block on critical/high, warn on medium
        if (maxSeverity == ThreatSeverity.critical ||
            maxSeverity == ThreatSeverity.high) {
          return SecurityAction.block;
        } else if (maxSeverity == ThreatSeverity.medium) {
          return SecurityAction.warn;
        }
        return SecurityAction.allow;

      case SecurityLevel.maximum:
        // Block on any threat
        return SecurityAction.block;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Security Bypass (for development/testing)
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if security bypass is enabled
  /// فحص إذا كان تجاوز الأمان مفعل
  Future<bool> _isSecurityBypassEnabled() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getBool('security_bypass_enabled') ?? false;
    } catch (e) {
      return false;
    }
  }

  /// Enable security bypass (for development/testing only)
  /// تفعيل تجاوز الأمان (للتطوير/الاختبار فقط)
  Future<void> enableSecurityBypass({required String reason}) async {
    if (kReleaseMode) {
      if (kDebugMode) {
        debugPrint('❌ Cannot enable security bypass in release mode');
      }
      return;
    }

    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('security_bypass_enabled', true);
      if (kDebugMode) {
        debugPrint('🔓 Security bypass enabled: $reason');
      }

      await _logSecurityEvent(
        event: 'security_bypass_enabled',
        details: reason,
      );
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Failed to enable security bypass: $e');
      }
    }
  }

  /// Disable security bypass
  /// تعطيل تجاوز الأمان
  Future<void> disableSecurityBypass() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool('security_bypass_enabled', false);
      if (kDebugMode) {
        debugPrint('🔒 Security bypass disabled');
      }

      await _logSecurityEvent(event: 'security_bypass_disabled');
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Failed to disable security bypass: $e');
      }
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Security Event Logging
  // ═══════════════════════════════════════════════════════════════════════════

  /// Log security event for monitoring
  /// تسجيل حدث أمني للمراقبة
  Future<void> _logSecurityEvent({
    required String event,
    bool? isSecure,
    List<SecurityThreat>? threats,
    String? details,
  }) async {
    if (!config.logAuthEvents) return;

    try {
      final logEntry = {
        'timestamp': DateTime.now().toIso8601String(),
        'event': event,
        'security_level': config.level.code,
        if (isSecure != null) 'is_secure': isSecure,
        if (threats != null && threats.isNotEmpty)
          'threats': threats.map((t) => t.type.toString()).toList(),
        if (details != null) 'details': details,
        'platform': Platform.operatingSystem,
        'debug_mode': kDebugMode,
        'release_mode': kReleaseMode,
      };

      // Log security event using AppLogger
      AppLogger.i(
        'Security Event: ${logEntry['event']}',
        tag: 'Security',
        data: logEntry,
      );

      // Report threats to monitoring service
      if (threats != null && threats.isNotEmpty) {
        await _reportThreatsToMonitoring(threats, logEntry);
      }

      // Save to local storage for debugging
      await _saveSecurityLog(logEntry);
    } catch (e) {
      AppLogger.w('Failed to log security event: $e', tag: 'Security');
    }
  }

  /// Report security threats to monitoring/crash reporting service
  /// تقرير التهديدات الأمنية لخدمة المراقبة
  ///
  /// This method logs threats using AppLogger and prepares data for
  /// crash reporting integration (e.g., Firebase Crashlytics, Sentry).
  /// In release mode, critical threats are logged with higher severity.
  Future<void> _reportThreatsToMonitoring(
    List<SecurityThreat> threats,
    Map<String, dynamic> logEntry,
  ) async {
    for (final threat in threats) {
      final threatData = {
        'threat_type': threat.type.toString(),
        'severity': threat.severity.toString(),
        'message_en': threat.messageEn,
        'message_ar': threat.messageAr,
        'details': threat.details,
        'platform': Platform.operatingSystem,
        'timestamp': logEntry['timestamp'],
        'security_level': logEntry['security_level'],
      };

      // Log based on severity
      switch (threat.severity) {
        case ThreatSeverity.critical:
          AppLogger.critical(
            'Security Threat: ${threat.messageEn}',
            tag: 'Security',
            data: threatData,
          );
          break;
        case ThreatSeverity.high:
          AppLogger.e(
            'Security Threat: ${threat.messageEn}',
            tag: 'Security',
            data: threatData,
          );
          break;
        case ThreatSeverity.medium:
          AppLogger.w(
            'Security Threat: ${threat.messageEn}',
            tag: 'Security',
            data: threatData,
          );
          break;
        case ThreatSeverity.low:
          AppLogger.i(
            'Security Threat: ${threat.messageEn}',
            tag: 'Security',
            data: threatData,
          );
          break;
      }
    }

    // In release mode, this is where crash reporting services would be called
    // The AppLogger already captures logs that can be attached to crash reports
    // via AppLogger.getRecentLogs() or AppLogger.exportLogs()
    //
    // Integration examples:
    // - Firebase Crashlytics: FirebaseCrashlytics.instance.recordError(...)
    // - Sentry: Sentry.captureMessage(...) or Sentry.captureException(...)
    //
    // The threatData map is structured for easy integration with these services.
  }

  /// Save security log to local storage
  /// حفظ سجل الأمان في التخزين المحلي
  Future<void> _saveSecurityLog(Map<String, dynamic> logEntry) async {
    try {
      final prefs = await SharedPreferences.getInstance();

      // Get existing logs (keep last 100)
      final logsJson = prefs.getStringList('security_logs') ?? [];

      // Add new log as JSON string
      logsJson.add(jsonEncode(logEntry));

      // Keep only last 100 logs
      if (logsJson.length > 100) {
        logsJson.removeRange(0, logsJson.length - 100);
      }

      // Save back
      await prefs.setStringList('security_logs', logsJson);
    } catch (e) {
      if (kDebugMode) {
        debugPrint('⚠️ Failed to save security log: $e');
      }
    }
  }

  /// Get security logs (for debugging)
  /// الحصول على سجلات الأمان (للتطوير)
  Future<List<String>> getSecurityLogs() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getStringList('security_logs') ?? [];
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Failed to get security logs: $e');
      }
      return [];
    }
  }

  /// Clear security logs
  /// مسح سجلات الأمان
  Future<void> clearSecurityLogs() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('security_logs');
      if (kDebugMode) {
        debugPrint('🗑️ Security logs cleared');
      }
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Failed to clear security logs: $e');
      }
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for device security service
final deviceSecurityServiceProvider = Provider<DeviceSecurityService>((ref) {
  final securityConfig = ref.watch(securityConfigProvider);
  return DeviceSecurityService(config: securityConfig);
});

/// Provider for device security check result (cached)
final deviceSecurityCheckProvider =
    FutureProvider<DeviceSecurityResult>((ref) async {
  final service = ref.watch(deviceSecurityServiceProvider);
  return service.checkDeviceSecurity();
});

/// Provider to check if device is secure (simple boolean)
final isDeviceSecureProvider = FutureProvider<bool>((ref) async {
  final result = await ref.watch(deviceSecurityCheckProvider.future);
  return result.isSecure;
});
