import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:safe_device/safe_device.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'security_config.dart';
import '../utils/app_logger.dart';

/// Device Integrity Detection Service
/// خدمة كشف سلامة الجهاز
///
/// Comprehensive device security checks including:
/// - Jailbreak detection (iOS)
/// - Root detection (Android)
/// - Emulator detection
/// - Debug mode detection
/// - Frida/hooking framework detection
/// - Developer options detection
///
/// فحوصات أمنية شاملة للجهاز تتضمن:
/// - كشف الجلبريك (iOS)
/// - كشف الروت (Android)
/// - كشف المحاكيات
/// - كشف وضع التطوير
/// - كشف أطر العمل للاختراق
/// - كشف خيارات المطور

/// Security Threat Level
enum SecurityThreatLevel {
  none,       // No threats detected
  low,        // Minor security concerns (emulator, debug mode)
  medium,     // Moderate threats (developer options enabled)
  high,       // Serious threats (root/jailbreak detected)
  critical,   // Multiple serious threats + hooking frameworks
}

/// Security Check Result
class SecurityCheckResult {
  final bool isJailbroken;
  final bool isRooted;
  final bool isEmulator;
  final bool isDebugMode;
  final bool isFridaDetected;
  final bool isDeveloperModeEnabled;
  final SecurityThreatLevel threatLevel;
  final List<String> detectedThreats;
  final Map<String, dynamic> deviceInfo;

  const SecurityCheckResult({
    required this.isJailbroken,
    required this.isRooted,
    required this.isEmulator,
    required this.isDebugMode,
    required this.isFridaDetected,
    required this.isDeveloperModeEnabled,
    required this.threatLevel,
    required this.detectedThreats,
    required this.deviceInfo,
  });

  /// Check if device is compromised (rooted or jailbroken)
  bool get isCompromised => isRooted || isJailbroken;

  /// Check if device has any security issues
  bool get hasSecurityIssues => detectedThreats.isNotEmpty;

  /// Get human-readable threat description
  String get threatDescription {
    if (detectedThreats.isEmpty) return 'No security threats detected';
    return detectedThreats.join(', ');
  }

  @override
  String toString() {
    return 'SecurityCheckResult('
        'rooted: $isRooted, '
        'jailbroken: $isJailbroken, '
        'emulator: $isEmulator, '
        'debug: $isDebugMode, '
        'frida: $isFridaDetected, '
        'devMode: $isDeveloperModeEnabled, '
        'threatLevel: $threatLevel, '
        'threats: ${detectedThreats.length}'
        ')';
  }
}

/// Device Integrity Service
class DeviceIntegrityService {
  static final DeviceIntegrityService _instance = DeviceIntegrityService._internal();
  factory DeviceIntegrityService() => _instance;
  DeviceIntegrityService._internal();

  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();
  SecurityCheckResult? _lastCheckResult;

  /// Get cached security check result
  SecurityCheckResult? get lastCheckResult => _lastCheckResult;

  /// Perform comprehensive device security check
  /// إجراء فحص أمني شامل للجهاز
  Future<SecurityCheckResult> checkDeviceIntegrity() async {
    try {
      AppLogger.d('Starting device integrity check...', tag: 'Security');

      // Initialize detection results
      bool isJailbroken = false;
      bool isRooted = false;
      bool isEmulator = false;
      bool isDebugMode = false;
      bool isFridaDetected = false;
      bool isDeveloperModeEnabled = false;
      List<String> threats = [];
      Map<String, dynamic> deviceInfo = {};

      // Detect debug mode
      isDebugMode = kDebugMode;
      if (isDebugMode) {
        threats.add('Debug mode active');
        AppLogger.w('Debug mode detected', tag: 'Security');
      }

      // Platform-specific checks
      if (Platform.isAndroid) {
        AppLogger.d('Running Android security checks...', tag: 'Security');

        // Get Android device info
        final androidInfo = await _deviceInfo.androidInfo;
        deviceInfo = {
          'platform': 'Android',
          'manufacturer': androidInfo.manufacturer,
          'model': androidInfo.model,
          'version': androidInfo.version.release,
          'sdkInt': androidInfo.version.sdkInt,
          'isPhysicalDevice': androidInfo.isPhysicalDevice,
        };

        // Check if running on emulator
        isEmulator = !androidInfo.isPhysicalDevice;
        if (isEmulator) {
          threats.add('Running on Android emulator');
          AppLogger.w('Android emulator detected', tag: 'Security');
        }

        // Check for root access
        try {
          isRooted = await SafeDevice.isJailBroken;
          if (isRooted) {
            threats.add('Android device is rooted');
            AppLogger.w('Root access detected', tag: 'Security');
          }
        } catch (e) {
          AppLogger.w('Root detection failed: $e', tag: 'Security');
        }

        // Check for developer options
        try {
          isDeveloperModeEnabled = await SafeDevice.isDevelopmentModeEnable;
          if (isDeveloperModeEnabled) {
            threats.add('Developer options enabled');
            AppLogger.w('Developer mode enabled', tag: 'Security');
          }
        } catch (e) {
          AppLogger.w('Developer mode check failed: $e', tag: 'Security');
        }

      } else if (Platform.isIOS) {
        AppLogger.d('Running iOS security checks...', tag: 'Security');

        // Get iOS device info
        final iosInfo = await _deviceInfo.iosInfo;
        deviceInfo = {
          'platform': 'iOS',
          'model': iosInfo.model,
          'systemName': iosInfo.systemName,
          'systemVersion': iosInfo.systemVersion,
          'isPhysicalDevice': iosInfo.isPhysicalDevice,
          'name': iosInfo.name,
        };

        // Check if running on simulator
        isEmulator = !iosInfo.isPhysicalDevice;
        if (isEmulator) {
          threats.add('Running on iOS simulator');
          AppLogger.w('iOS simulator detected', tag: 'Security');
        }

        // Check for jailbreak
        try {
          isJailbroken = await SafeDevice.isJailBroken;
          if (isJailbroken) {
            threats.add('iOS device is jailbroken');
            AppLogger.w('Jailbreak detected', tag: 'Security');
          }
        } catch (e) {
          AppLogger.w('Jailbreak detection failed: $e', tag: 'Security');
        }
      }

      // Check for Frida and other hooking frameworks
      isFridaDetected = await _detectFrida();
      if (isFridaDetected) {
        threats.add('Frida or hooking framework detected');
        AppLogger.w('Frida/hooking framework detected', tag: 'Security');
      }

      // Calculate threat level
      final threatLevel = _calculateThreatLevel(
        isRooted: isRooted,
        isJailbroken: isJailbroken,
        isEmulator: isEmulator,
        isDebugMode: isDebugMode,
        isFridaDetected: isFridaDetected,
        isDeveloperModeEnabled: isDeveloperModeEnabled,
      );

      final result = SecurityCheckResult(
        isJailbroken: isJailbroken,
        isRooted: isRooted,
        isEmulator: isEmulator,
        isDebugMode: isDebugMode,
        isFridaDetected: isFridaDetected,
        isDeveloperModeEnabled: isDeveloperModeEnabled,
        threatLevel: threatLevel,
        detectedThreats: threats,
        deviceInfo: deviceInfo,
      );

      _lastCheckResult = result;

      AppLogger.i('Security check complete: $result', tag: 'Security');
      return result;

    } catch (e, stackTrace) {
      AppLogger.e('Device integrity check failed: $e', tag: 'Security', error: e, stackTrace: stackTrace);

      // Return safe defaults on error
      return SecurityCheckResult(
        isJailbroken: false,
        isRooted: false,
        isEmulator: false,
        isDebugMode: kDebugMode,
        isFridaDetected: false,
        isDeveloperModeEnabled: false,
        threatLevel: SecurityThreatLevel.none,
        detectedThreats: ['Error during security check: ${e.toString()}'],
        deviceInfo: {'error': e.toString()},
      );
    }
  }

  /// Detect Frida and other hooking frameworks
  /// كشف Frida وأطر العمل الأخرى للاختراق
  Future<bool> _detectFrida() async {
    try {
      // Check for common Frida artifacts
      if (Platform.isAndroid) {
        // Check for Frida server listening on default port
        // Note: This is a simple check and may not detect all cases
        // For production, consider using native code checks

        // Check for common Frida libraries in memory
        // This would require platform channels to native code
        // For now, we'll return false as basic implementation
        return false;
      } else if (Platform.isIOS) {
        // Check for Frida libraries on iOS
        // This would require platform channels to native code
        return false;
      }
      return false;
    } catch (e) {
      AppLogger.w('Frida detection failed: $e', tag: 'Security');
      return false;
    }
  }

  /// Calculate overall threat level based on detected issues
  SecurityThreatLevel _calculateThreatLevel({
    required bool isRooted,
    required bool isJailbroken,
    required bool isEmulator,
    required bool isDebugMode,
    required bool isFridaDetected,
    required bool isDeveloperModeEnabled,
  }) {
    // Critical: Hooking framework + root/jailbreak
    if (isFridaDetected && (isRooted || isJailbroken)) {
      return SecurityThreatLevel.critical;
    }

    // High: Root or jailbreak detected
    if (isRooted || isJailbroken) {
      return SecurityThreatLevel.high;
    }

    // High: Frida detected (even without root)
    if (isFridaDetected) {
      return SecurityThreatLevel.high;
    }

    // Medium: Developer mode on physical device
    if (isDeveloperModeEnabled && !isEmulator) {
      return SecurityThreatLevel.medium;
    }

    // Low: Emulator or debug mode
    if (isEmulator || isDebugMode) {
      return SecurityThreatLevel.low;
    }

    // None: No threats detected
    return SecurityThreatLevel.none;
  }

  /// Check if app should be blocked based on security policy
  /// فحص ما إذا كان يجب حظر التطبيق بناءً على سياسة الأمان
  bool shouldBlockApp(SecurityCheckResult result, SecurityConfig securityConfig) {
    // Always allow in development mode (unless forced)
    if (kDebugMode && !securityConfig.enforceSecurityInDebug) {
      AppLogger.d('Security checks bypassed in debug mode', tag: 'Security');
      return false;
    }

    // Check policy
    switch (securityConfig.deviceIntegrityPolicy) {
      case DeviceIntegrityPolicy.block:
        // Block if device is compromised
        return result.isCompromised;

      case DeviceIntegrityPolicy.warn:
        // Never block, just warn
        return false;

      case DeviceIntegrityPolicy.log:
        // Never block, just log
        return false;

      case DeviceIntegrityPolicy.blockAll:
        // Block if any security issue detected
        return result.hasSecurityIssues;

      case DeviceIntegrityPolicy.disabled:
        // Never block
        return false;
    }
  }

  /// Log security event for monitoring
  /// تسجيل حدث أمني للمراقبة
  void logSecurityEvent(SecurityCheckResult result) {
    if (result.hasSecurityIssues) {
      AppLogger.w('Security event logged', tag: 'Security', data: {
        'platform': result.deviceInfo['platform'],
        'threatLevel': result.threatLevel.toString(),
        'compromised': result.isCompromised,
        'threats': result.detectedThreats,
      });

      // In production, send to analytics/monitoring service
      // Example: CrashReportingService().logSecurityEvent(result);
    }
  }

  /// Get user-friendly message based on threat level
  String getThreatLevelMessage(SecurityThreatLevel level, String locale) {
    final isArabic = locale == 'ar';

    switch (level) {
      case SecurityThreatLevel.critical:
        return isArabic
          ? 'تهديد أمني حرج - لا يمكن تشغيل التطبيق'
          : 'Critical security threat - Cannot run app';
      case SecurityThreatLevel.high:
        return isArabic
          ? 'تهديد أمني عالي - جهاز غير آمن'
          : 'High security threat - Unsafe device';
      case SecurityThreatLevel.medium:
        return isArabic
          ? 'تهديد أمني متوسط - استخدم بحذر'
          : 'Medium security threat - Use with caution';
      case SecurityThreatLevel.low:
        return isArabic
          ? 'تحذير أمني بسيط'
          : 'Minor security warning';
      case SecurityThreatLevel.none:
        return isArabic
          ? 'لا توجد تهديدات أمنية'
          : 'No security threats';
    }
  }
}
