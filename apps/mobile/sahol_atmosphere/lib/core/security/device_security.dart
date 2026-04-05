import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:safe_device/safe_device.dart';
import 'package:device_info_plus/device_info_plus.dart';

/// Device Security Service for SAHOOL Atmosphere
/// خدمة أمان الجهاز لتطبيق ساهول أتموسفير
///
/// Provides basic security checks:
/// - Root/Jailbreak detection
/// - Emulator detection
/// - Debug mode detection
class DeviceSecurityService {
  static final DeviceSecurityService _instance = DeviceSecurityService._internal();
  factory DeviceSecurityService() => _instance;
  DeviceSecurityService._internal();

  final DeviceInfoPlugin _deviceInfo = DeviceInfoPlugin();

  /// Security threat levels
  SecurityThreatLevel? _lastThreatLevel;

  /// Get last detected threat level
  SecurityThreatLevel? get lastThreatLevel => _lastThreatLevel;

  /// Check device security status
  /// فحص حالة أمان الجهاز
  Future<SecurityCheckResult> checkSecurity() async {
    try {
      bool isCompromised = false;
      bool isEmulator = false;
      const bool isDebugMode = kDebugMode;
      final List<String> threats = [];
      Map<String, dynamic> deviceInfo = {};

      // Debug mode check
      if (isDebugMode) {
        threats.add('Debug mode active');
      }

      // Platform-specific checks
      if (Platform.isAndroid) {
        final androidInfo = await _deviceInfo.androidInfo;
        deviceInfo = {
          'platform': 'Android',
          'manufacturer': androidInfo.manufacturer,
          'model': androidInfo.model,
          'version': androidInfo.version.release,
          'isPhysicalDevice': androidInfo.isPhysicalDevice,
        };

        isEmulator = !androidInfo.isPhysicalDevice;
        if (isEmulator) {
          threats.add('Running on emulator');
        }

        try {
          isCompromised = await SafeDevice.isJailBroken;
          if (isCompromised) {
            threats.add('Device is rooted');
          }
        } catch (e) {
          debugPrint('Root detection failed: $e');
          // Treat detection failure as potential threat in production
          if (!kDebugMode) {
            threats.add('Root detection unavailable');
          }
        }
      } else if (Platform.isIOS) {
        final iosInfo = await _deviceInfo.iosInfo;
        deviceInfo = {
          'platform': 'iOS',
          'model': iosInfo.model,
          'systemVersion': iosInfo.systemVersion,
          'isPhysicalDevice': iosInfo.isPhysicalDevice,
        };

        isEmulator = !iosInfo.isPhysicalDevice;
        if (isEmulator) {
          threats.add('Running on simulator');
        }

        try {
          isCompromised = await SafeDevice.isJailBroken;
          if (isCompromised) {
            threats.add('Device is jailbroken');
          }
        } catch (e) {
          debugPrint('Jailbreak detection failed: $e');
          // Treat detection failure as potential threat in production
          if (!kDebugMode) {
            threats.add('Jailbreak detection unavailable');
          }
        }
      }

      // Calculate threat level
      final threatLevel = _calculateThreatLevel(
        isCompromised: isCompromised,
        isEmulator: isEmulator,
        isDebugMode: isDebugMode,
      );

      _lastThreatLevel = threatLevel;

      return SecurityCheckResult(
        isCompromised: isCompromised,
        isEmulator: isEmulator,
        isDebugMode: isDebugMode,
        threatLevel: threatLevel,
        threats: threats,
        deviceInfo: deviceInfo,
      );
    } catch (e) {
      debugPrint('Security check failed: $e');
      return SecurityCheckResult(
        isCompromised: false,
        isEmulator: false,
        isDebugMode: kDebugMode,
        threatLevel: SecurityThreatLevel.unknown,
        threats: ['Security check failed: $e'],
        deviceInfo: {},
      );
    }
  }

  SecurityThreatLevel _calculateThreatLevel({
    required bool isCompromised,
    required bool isEmulator,
    required bool isDebugMode,
  }) {
    if (isCompromised) {
      return SecurityThreatLevel.high;
    }
    if (isEmulator && !isDebugMode) {
      return SecurityThreatLevel.medium;
    }
    if (isEmulator || isDebugMode) {
      return SecurityThreatLevel.low;
    }
    return SecurityThreatLevel.none;
  }

  /// Get localized threat message
  String getThreatMessage(SecurityThreatLevel level, {bool arabic = true}) {
    switch (level) {
      case SecurityThreatLevel.high:
        return arabic
          ? 'تحذير: جهاز غير آمن - تم كشف روت/جيلبريك'
          : 'Warning: Unsafe device - Root/Jailbreak detected';
      case SecurityThreatLevel.medium:
        return arabic
          ? 'تنبيه: يتم التشغيل على محاكي'
          : 'Notice: Running on emulator';
      case SecurityThreatLevel.low:
        return arabic
          ? 'وضع التطوير نشط'
          : 'Development mode active';
      case SecurityThreatLevel.none:
        return arabic
          ? 'الجهاز آمن'
          : 'Device is secure';
      case SecurityThreatLevel.unknown:
        return arabic
          ? 'لم يتم فحص الأمان'
          : 'Security not checked';
    }
  }
}

/// Security threat level enum
enum SecurityThreatLevel {
  none,     // No threats
  low,      // Debug/development mode
  medium,   // Emulator detected
  high,     // Root/Jailbreak detected
  unknown,  // Check failed
}

/// Security check result
class SecurityCheckResult {
  final bool isCompromised;
  final bool isEmulator;
  final bool isDebugMode;
  final SecurityThreatLevel threatLevel;
  final List<String> threats;
  final Map<String, dynamic> deviceInfo;

  const SecurityCheckResult({
    required this.isCompromised,
    required this.isEmulator,
    required this.isDebugMode,
    required this.threatLevel,
    required this.threats,
    required this.deviceInfo,
  });

  bool get hasIssues => threats.isNotEmpty;

  @override
  String toString() {
    return 'SecurityCheckResult(compromised: $isCompromised, emulator: $isEmulator, debug: $isDebugMode, level: $threatLevel)';
  }
}
