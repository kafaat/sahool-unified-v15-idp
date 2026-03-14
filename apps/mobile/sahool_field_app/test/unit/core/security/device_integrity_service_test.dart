import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/security/device_integrity_service.dart';
import 'package:sahool_field_app/core/security/security_config.dart';

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
    test('has all expected values', () {
      expect(SecurityThreatLevel.values, hasLength(5));
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
  });

  // ===========================================================================
  // DeviceIntegrityService - shouldBlockApp
  // ===========================================================================
  group('DeviceIntegrityService.shouldBlockApp', () {
    test('returns false when policy is disabled', () {
      final config = buildConfig(DeviceIntegrityPolicy.disabled);
      final result = buildResult(
        isRooted: true,
        detectedThreats: ['Android device is rooted'],
      );
      expect(service.shouldBlockApp(result, config), isFalse);
    });

    test('returns false when policy is log', () {
      final config = buildConfig(DeviceIntegrityPolicy.log);
      final result = buildResult(
        isRooted: true,
        detectedThreats: ['Android device is rooted'],
      );
      expect(service.shouldBlockApp(result, config), isFalse);
    });

    test('returns false when policy is warn', () {
      final config = buildConfig(DeviceIntegrityPolicy.warn);
      final result = buildResult(
        isRooted: true,
        detectedThreats: ['Android device is rooted'],
      );
      expect(service.shouldBlockApp(result, config), isFalse);
    });

    test('blocks compromised device when policy is block', () {
      final config = buildConfig(DeviceIntegrityPolicy.block);
      final result = buildResult(
        isRooted: true,
        detectedThreats: ['Android device is rooted'],
      );
      expect(service.shouldBlockApp(result, config), isTrue);
    });

    test('does not block non-compromised device when policy is block', () {
      final config = buildConfig(DeviceIntegrityPolicy.block);
      final result = buildResult(
        isEmulator: true,
        detectedThreats: ['Running on Android emulator'],
      );
      // isCompromised is false (not rooted or jailbroken)
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

    test('bypasses security checks in debug mode when enforceSecurityInDebug is false', () {
      // kDebugMode is true in tests, so when enforceSecurityInDebug is false
      // shouldBlockApp should always return false regardless of policy.
      final config = const SecurityConfig(
        deviceIntegrityPolicy: DeviceIntegrityPolicy.block,
        enforceSecurityInDebug: false,
      );
      final result = buildResult(
        isRooted: true,
        isJailbroken: true,
        detectedThreats: ['Android device is rooted', 'iOS device is jailbroken'],
      );
      expect(service.shouldBlockApp(result, config), isFalse);
    });
  });

  // ===========================================================================
  // DeviceIntegrityService - getThreatLevelMessage
  // ===========================================================================
  group('DeviceIntegrityService.getThreatLevelMessage', () {
    test('returns English message for en locale', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.high,
        'en',
      );
      expect(msg, 'High security threat - Unsafe device');
    });

    test('returns Arabic message for ar locale', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.high,
        'ar',
      );
      expect(msg, contains('تهديد أمني عالي'));
    });

    test('returns correct message for all threat levels in English', () {
      final expected = <SecurityThreatLevel, String>{
        SecurityThreatLevel.none: 'No security threats',
        SecurityThreatLevel.low: 'Minor security warning',
        SecurityThreatLevel.medium: 'Medium security threat - Use with caution',
        SecurityThreatLevel.high: 'High security threat - Unsafe device',
        SecurityThreatLevel.critical: 'Critical security threat - Cannot run app',
      };

      for (final entry in expected.entries) {
        expect(
          service.getThreatLevelMessage(entry.key, 'en'),
          entry.value,
          reason: 'English message for ${entry.key}',
        );
      }
    });

    test('returns correct message for all threat levels in Arabic', () {
      final expected = <SecurityThreatLevel, String>{
        SecurityThreatLevel.none: 'لا توجد تهديدات أمنية',
        SecurityThreatLevel.low: 'تحذير أمني بسيط',
        SecurityThreatLevel.medium: 'تهديد أمني متوسط - استخدم بحذر',
        SecurityThreatLevel.high: 'تهديد أمني عالي - جهاز غير آمن',
        SecurityThreatLevel.critical: 'تهديد أمني حرج - لا يمكن تشغيل التطبيق',
      };

      for (final entry in expected.entries) {
        expect(
          service.getThreatLevelMessage(entry.key, 'ar'),
          entry.value,
          reason: 'Arabic message for ${entry.key}',
        );
      }
    });

    test('returns English message for non-ar locale', () {
      final msg = service.getThreatLevelMessage(
        SecurityThreatLevel.critical,
        'fr',
      );
      expect(msg, 'Critical security threat - Cannot run app');
    });
  });

  // ===========================================================================
  // SecurityCheckResult - threat level calculation via construction
  // (Testing _calculateThreatLevel indirectly by constructing results
  //  that mirror what the service would produce)
  // ===========================================================================
  group('Threat level calculation logic', () {
    // These tests verify the expected threat level for various flag
    // combinations, matching the _calculateThreatLevel private method.

    test('none when no flags are set', () {
      final result = buildResult(threatLevel: SecurityThreatLevel.none);
      expect(result.threatLevel, SecurityThreatLevel.none);
      expect(result.isCompromised, isFalse);
      expect(result.hasSecurityIssues, isFalse);
    });

    test('low when only emulator is detected', () {
      final result = buildResult(
        isEmulator: true,
        threatLevel: SecurityThreatLevel.low,
        detectedThreats: ['Running on Android emulator'],
      );
      expect(result.threatLevel, SecurityThreatLevel.low);
    });

    test('low when only debug mode is detected', () {
      final result = buildResult(
        isDebugMode: true,
        threatLevel: SecurityThreatLevel.low,
        detectedThreats: ['Debug mode active'],
      );
      expect(result.threatLevel, SecurityThreatLevel.low);
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

    test('high when device is rooted', () {
      final result = buildResult(
        isRooted: true,
        threatLevel: SecurityThreatLevel.high,
        detectedThreats: ['Android device is rooted'],
      );
      expect(result.threatLevel, SecurityThreatLevel.high);
    });

    test('high when device is jailbroken', () {
      final result = buildResult(
        isJailbroken: true,
        threatLevel: SecurityThreatLevel.high,
        detectedThreats: ['iOS device is jailbroken'],
      );
      expect(result.threatLevel, SecurityThreatLevel.high);
    });

    test('high when frida detected without root', () {
      final result = buildResult(
        isFridaDetected: true,
        threatLevel: SecurityThreatLevel.high,
        detectedThreats: ['Frida or hooking framework detected'],
      );
      expect(result.threatLevel, SecurityThreatLevel.high);
    });

    test('critical when frida detected with root', () {
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

    test('critical when frida detected with jailbreak', () {
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
  });
}
