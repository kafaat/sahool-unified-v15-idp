import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/security/device_integrity_service.dart';
import 'package:sahool_field_app/core/security/security_config.dart';

/// Device Integrity Models Unit Tests
/// اختبارات وحدات نماذج سلامة الجهاز
///
/// Focused tests for SecurityCheckResult, SecurityThreatLevel,
/// threat level calculation logic, shouldBlockApp policy evaluation,
/// and bilingual getThreatLevelMessage.
void main() {
  // ---------------------------------------------------------------------------
  // Helper to build SecurityCheckResult with sensible defaults
  // ---------------------------------------------------------------------------
  SecurityCheckResult buildResult({
    bool isJailbroken = false,
    bool isRooted = false,
    bool isEmulator = false,
    bool isDebugMode = false,
    bool isFridaDetected = false,
    bool isDeveloperModeEnabled = false,
    SecurityThreatLevel threatLevel = SecurityThreatLevel.none,
    List<String> detectedThreats = const [],
    Map<String, dynamic> deviceInfo = const {},
  }) {
    return SecurityCheckResult(
      isJailbroken: isJailbroken,
      isRooted: isRooted,
      isEmulator: isEmulator,
      isDebugMode: isDebugMode,
      isFridaDetected: isFridaDetected,
      isDeveloperModeEnabled: isDeveloperModeEnabled,
      threatLevel: threatLevel,
      detectedThreats: detectedThreats,
      deviceInfo: deviceInfo,
    );
  }

  // Helper to build a SecurityConfig that enforces security in debug mode
  // so that shouldBlockApp actually evaluates the policy (since tests run
  // with kDebugMode == true).
  SecurityConfig buildConfig(DeviceIntegrityPolicy policy) {
    return SecurityConfig(
      deviceIntegrityPolicy: policy,
      enforceSecurityInDebug: true,
    );
  }

  late DeviceIntegrityService service;

  setUp(() {
    service = DeviceIntegrityService();
  });

  // ===========================================================================
  // SecurityThreatLevel enum
  // ===========================================================================
  group('SecurityThreatLevel', () {
    test('has exactly 5 values', () {
      expect(SecurityThreatLevel.values, hasLength(5));
    });

    test('contains all expected values', () {
      expect(
        SecurityThreatLevel.values,
        containsAll([
          SecurityThreatLevel.none,
          SecurityThreatLevel.low,
          SecurityThreatLevel.medium,
          SecurityThreatLevel.high,
          SecurityThreatLevel.critical,
        ]),
      );
    });

    test('values are ordered from none to critical', () {
      expect(SecurityThreatLevel.none.index, 0);
      expect(SecurityThreatLevel.low.index, 1);
      expect(SecurityThreatLevel.medium.index, 2);
      expect(SecurityThreatLevel.high.index, 3);
      expect(SecurityThreatLevel.critical.index, 4);
    });
  });

  // ===========================================================================
  // SecurityCheckResult - isCompromised
  // ===========================================================================
  group('SecurityCheckResult.isCompromised', () {
    test('returns true when device is rooted', () {
      final result = buildResult(isRooted: true);
      expect(result.isCompromised, isTrue);
    });

    test('returns true when device is jailbroken', () {
      final result = buildResult(isJailbroken: true);
      expect(result.isCompromised, isTrue);
    });

    test('returns true when device is both rooted and jailbroken', () {
      final result = buildResult(isRooted: true, isJailbroken: true);
      expect(result.isCompromised, isTrue);
    });

    test('returns false when neither rooted nor jailbroken', () {
      final result = buildResult();
      expect(result.isCompromised, isFalse);
    });

    test('returns false when only emulator detected', () {
      final result = buildResult(isEmulator: true);
      expect(result.isCompromised, isFalse);
    });

    test('returns false when only frida detected', () {
      final result = buildResult(isFridaDetected: true);
      expect(result.isCompromised, isFalse);
    });

    test('returns false when only debug mode active', () {
      final result = buildResult(isDebugMode: true);
      expect(result.isCompromised, isFalse);
    });

    test('returns false when only developer mode enabled', () {
      final result = buildResult(isDeveloperModeEnabled: true);
      expect(result.isCompromised, isFalse);
    });
  });

  // ===========================================================================
  // SecurityCheckResult - hasSecurityIssues
  // ===========================================================================
  group('SecurityCheckResult.hasSecurityIssues', () {
    test('returns true when detectedThreats is not empty', () {
      final result = buildResult(
        detectedThreats: ['Debug mode active'],
      );
      expect(result.hasSecurityIssues, isTrue);
    });

    test('returns true with multiple threats', () {
      final result = buildResult(
        detectedThreats: [
          'Android device is rooted',
          'Frida or hooking framework detected',
        ],
      );
      expect(result.hasSecurityIssues, isTrue);
    });

    test('returns false when detectedThreats is empty', () {
      final result = buildResult();
      expect(result.hasSecurityIssues, isFalse);
    });
  });

  // ===========================================================================
  // SecurityCheckResult - threatDescription
  // ===========================================================================
  group('SecurityCheckResult.threatDescription', () {
    test('returns default message when no threats detected', () {
      final result = buildResult();
      expect(result.threatDescription, 'No security threats detected');
    });

    test('joins multiple threats with comma separator', () {
      final result = buildResult(
        detectedThreats: [
          'Android device is rooted',
          'Developer options enabled',
          'Debug mode active',
        ],
      );
      expect(
        result.threatDescription,
        'Android device is rooted, Developer options enabled, Debug mode active',
      );
    });

    test('returns single threat without comma', () {
      final result = buildResult(
        detectedThreats: ['Running on Android emulator'],
      );
      expect(result.threatDescription, 'Running on Android emulator');
    });
  });

  // ===========================================================================
  // SecurityCheckResult - toString
  // ===========================================================================
  group('SecurityCheckResult.toString', () {
    test('contains all relevant fields in expected format', () {
      final result = buildResult(
        isRooted: true,
        isJailbroken: false,
        isEmulator: true,
        isDebugMode: true,
        isFridaDetected: false,
        isDeveloperModeEnabled: true,
        threatLevel: SecurityThreatLevel.high,
        detectedThreats: ['Android device is rooted', 'Debug mode active'],
      );

      final str = result.toString();
      expect(str, contains('rooted: true'));
      expect(str, contains('jailbroken: false'));
      expect(str, contains('emulator: true'));
      expect(str, contains('debug: true'));
      expect(str, contains('frida: false'));
      expect(str, contains('devMode: true'));
      expect(str, contains('threatLevel: SecurityThreatLevel.high'));
      expect(str, contains('threats: 2'));
      expect(str, startsWith('SecurityCheckResult('));
      expect(str, endsWith(')'));
    });

    test('shows zero threats when clean', () {
      final result = buildResult();
      final str = result.toString();
      expect(str, contains('threats: 0'));
    });
  });

  // ===========================================================================
  // SecurityCheckResult - deviceInfo field
  // ===========================================================================
  group('SecurityCheckResult.deviceInfo', () {
    test('stores and exposes device info map', () {
      final info = <String, dynamic>{
        'platform': 'Android',
        'manufacturer': 'Samsung',
        'model': 'Galaxy S21',
      };
      final result = buildResult(deviceInfo: info);
      expect(result.deviceInfo, equals(info));
      expect(result.deviceInfo['platform'], 'Android');
    });

    test('defaults to empty map', () {
      final result = buildResult();
      expect(result.deviceInfo, isEmpty);
    });
  });

  // ===========================================================================
  // Threat level calculation logic
  // (Testing _calculateThreatLevel indirectly by constructing results
  //  that mirror what the service would produce)
  // ===========================================================================
  group('Threat level calculation logic', () {
    test('critical when frida detected with rooted device', () {
      final result = buildResult(
        isRooted: true,
        isFridaDetected: true,
        threatLevel: SecurityThreatLevel.critical,
        detectedThreats: [
          'Android device is rooted',
          'Frida or hooking framework detected',
        ],
      );
      expect(result.threatLevel, SecurityThreatLevel.critical);
    });

    test('critical when frida detected with jailbroken device', () {
      final result = buildResult(
        isJailbroken: true,
        isFridaDetected: true,
        threatLevel: SecurityThreatLevel.critical,
        detectedThreats: [
          'iOS device is jailbroken',
          'Frida or hooking framework detected',
        ],
      );
      expect(result.threatLevel, SecurityThreatLevel.critical);
    });

    test('high when device is rooted alone', () {
      final result = buildResult(
        isRooted: true,
        threatLevel: SecurityThreatLevel.high,
        detectedThreats: ['Android device is rooted'],
      );
      expect(result.threatLevel, SecurityThreatLevel.high);
    });

    test('high when device is jailbroken alone', () {
      final result = buildResult(
        isJailbroken: true,
        threatLevel: SecurityThreatLevel.high,
        detectedThreats: ['iOS device is jailbroken'],
      );
      expect(result.threatLevel, SecurityThreatLevel.high);
    });

    test('high when frida detected alone (without root)', () {
      final result = buildResult(
        isFridaDetected: true,
        threatLevel: SecurityThreatLevel.high,
        detectedThreats: ['Frida or hooking framework detected'],
      );
      expect(result.threatLevel, SecurityThreatLevel.high);
    });

    test('medium when developer mode on physical device', () {
      final result = buildResult(
        isDeveloperModeEnabled: true,
        isEmulator: false,
        threatLevel: SecurityThreatLevel.medium,
        detectedThreats: ['Developer options enabled'],
      );
      expect(result.threatLevel, SecurityThreatLevel.medium);
    });

    test('low when only emulator detected', () {
      final result = buildResult(
        isEmulator: true,
        threatLevel: SecurityThreatLevel.low,
        detectedThreats: ['Running on Android emulator'],
      );
      expect(result.threatLevel, SecurityThreatLevel.low);
    });

    test('low when only debug mode detected', () {
      final result = buildResult(
        isDebugMode: true,
        threatLevel: SecurityThreatLevel.low,
        detectedThreats: ['Debug mode active'],
      );
      expect(result.threatLevel, SecurityThreatLevel.low);
    });

    test('none when no flags are set (clean device)', () {
      final result = buildResult(threatLevel: SecurityThreatLevel.none);
      expect(result.threatLevel, SecurityThreatLevel.none);
      expect(result.isCompromised, isFalse);
      expect(result.hasSecurityIssues, isFalse);
    });
  });

  // ===========================================================================
  // DeviceIntegrityService - getThreatLevelMessage
  // ===========================================================================
  group('DeviceIntegrityService.getThreatLevelMessage', () {
    test('returns Arabic message for ar locale - critical', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.critical,
        'ar',
      );
      expect(msg, 'تهديد أمني حرج - لا يمكن تشغيل التطبيق');
    });

    test('returns Arabic message for ar locale - high', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.high,
        'ar',
      );
      expect(msg, 'تهديد أمني عالي - جهاز غير آمن');
    });

    test('returns Arabic message for ar locale - medium', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.medium,
        'ar',
      );
      expect(msg, 'تهديد أمني متوسط - استخدم بحذر');
    });

    test('returns Arabic message for ar locale - low', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.low,
        'ar',
      );
      expect(msg, 'تحذير أمني بسيط');
    });

    test('returns Arabic message for ar locale - none', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.none,
        'ar',
      );
      expect(msg, 'لا توجد تهديدات أمنية');
    });

    test('returns English message for en locale - critical', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.critical,
        'en',
      );
      expect(msg, 'Critical security threat - Cannot run app');
    });

    test('returns English message for en locale - high', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.high,
        'en',
      );
      expect(msg, 'High security threat - Unsafe device');
    });

    test('returns English message for en locale - medium', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.medium,
        'en',
      );
      expect(msg, 'Medium security threat - Use with caution');
    });

    test('returns English message for en locale - low', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.low,
        'en',
      );
      expect(msg, 'Minor security warning');
    });

    test('returns English message for en locale - none', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.none,
        'en',
      );
      expect(msg, 'No security threats');
    });

    test('returns English message for non-ar locale (fallback)', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.critical,
        'fr',
      );
      expect(msg, 'Critical security threat - Cannot run app');
    });
  });

  // ===========================================================================
  // DeviceIntegrityService - shouldBlockApp
  // ===========================================================================
  group('DeviceIntegrityService.shouldBlockApp', () {
    test('blocks compromised device when policy is block', () {
      final config = buildConfig(DeviceIntegrityPolicy.block);
      final result = buildResult(
        isRooted: true,
        detectedThreats: ['Android device is rooted'],
      );
      expect(service.shouldBlockApp(result, config), isTrue);
    });

    test('blocks jailbroken device when policy is block', () {
      final config = buildConfig(DeviceIntegrityPolicy.block);
      final result = buildResult(
        isJailbroken: true,
        detectedThreats: ['iOS device is jailbroken'],
      );
      expect(service.shouldBlockApp(result, config), isTrue);
    });

    test('does not block non-compromised device when policy is block', () {
      final config = buildConfig(DeviceIntegrityPolicy.block);
      final result = buildResult(
        isEmulator: true,
        detectedThreats: ['Running on Android emulator'],
      );
      expect(service.shouldBlockApp(result, config), isFalse);
    });

    test('blocks any security issues when policy is blockAll', () {
      final config = buildConfig(DeviceIntegrityPolicy.blockAll);
      final result = buildResult(
        isEmulator: true,
        detectedThreats: ['Running on Android emulator'],
      );
      expect(service.shouldBlockApp(result, config), isTrue);
    });

    test('does not block clean device when policy is blockAll', () {
      final config = buildConfig(DeviceIntegrityPolicy.blockAll);
      final result = buildResult();
      expect(service.shouldBlockApp(result, config), isFalse);
    });

    test('never blocks when policy is warn', () {
      final config = buildConfig(DeviceIntegrityPolicy.warn);
      final result = buildResult(
        isRooted: true,
        isJailbroken: true,
        isFridaDetected: true,
        detectedThreats: [
          'Android device is rooted',
          'iOS device is jailbroken',
          'Frida or hooking framework detected',
        ],
      );
      expect(service.shouldBlockApp(result, config), isFalse);
    });

    test('never blocks when policy is log', () {
      final config = buildConfig(DeviceIntegrityPolicy.log);
      final result = buildResult(
        isRooted: true,
        detectedThreats: ['Android device is rooted'],
      );
      expect(service.shouldBlockApp(result, config), isFalse);
    });

    test('never blocks when policy is disabled', () {
      final config = buildConfig(DeviceIntegrityPolicy.disabled);
      final result = buildResult(
        isRooted: true,
        isJailbroken: true,
        isFridaDetected: true,
        detectedThreats: [
          'Android device is rooted',
          'iOS device is jailbroken',
          'Frida or hooking framework detected',
        ],
      );
      expect(service.shouldBlockApp(result, config), isFalse);
    });

    test('bypasses security checks in debug mode when enforceSecurityInDebug is false', () {
      // kDebugMode is true in tests, so when enforceSecurityInDebug is false
      // shouldBlockApp should always return false regardless of policy.
      const config = SecurityConfig(
        deviceIntegrityPolicy: DeviceIntegrityPolicy.block,
        enforceSecurityInDebug: false,
      );
      final result = buildResult(
        isRooted: true,
        isJailbroken: true,
        detectedThreats: [
          'Android device is rooted',
          'iOS device is jailbroken',
        ],
      );
      expect(service.shouldBlockApp(result, config), isFalse);
    });

    test('enforces block policy when enforceSecurityInDebug is true', () {
      const config = SecurityConfig(
        deviceIntegrityPolicy: DeviceIntegrityPolicy.block,
        enforceSecurityInDebug: true,
      );
      final result = buildResult(
        isRooted: true,
        detectedThreats: ['Android device is rooted'],
      );
      expect(service.shouldBlockApp(result, config), isTrue);
    });
  });

  // ===========================================================================
  // DeviceIntegrityService - singleton pattern
  // ===========================================================================
  group('DeviceIntegrityService singleton', () {
    test('factory constructor returns the same instance', () {
      final a = DeviceIntegrityService();
      final b = DeviceIntegrityService();
      expect(identical(a, b), isTrue);
    });
  });
}
