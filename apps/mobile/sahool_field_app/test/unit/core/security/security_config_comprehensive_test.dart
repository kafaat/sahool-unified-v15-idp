import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/security/security_config.dart';

/// Comprehensive security configuration tests
/// اختبارات شاملة لإعدادات الأمان
void main() {
  group('DeviceIntegrityPolicy', () {
    test('has 5 values', () {
      expect(DeviceIntegrityPolicy.values.length, 5);
    });

    test('contains all expected values', () {
      expect(DeviceIntegrityPolicy.values, contains(DeviceIntegrityPolicy.disabled));
      expect(DeviceIntegrityPolicy.values, contains(DeviceIntegrityPolicy.log));
      expect(DeviceIntegrityPolicy.values, contains(DeviceIntegrityPolicy.warn));
      expect(DeviceIntegrityPolicy.values, contains(DeviceIntegrityPolicy.block));
      expect(DeviceIntegrityPolicy.values, contains(DeviceIntegrityPolicy.blockAll));
    });
  });

  group('ScreenshotPolicy', () {
    test('has 3 values', () {
      expect(ScreenshotPolicy.values.length, 3);
    });

    test('contains all expected values', () {
      expect(ScreenshotPolicy.values, contains(ScreenshotPolicy.disabled));
      expect(ScreenshotPolicy.values, contains(ScreenshotPolicy.sensitiveOnly));
      expect(ScreenshotPolicy.values, contains(ScreenshotPolicy.allScreens));
    });
  });

  group('SessionSecurityPolicy', () {
    test('has 4 values', () {
      expect(SessionSecurityPolicy.values.length, 4);
    });

    test('contains all expected values', () {
      expect(SessionSecurityPolicy.values, contains(SessionSecurityPolicy.disabled));
      expect(SessionSecurityPolicy.values, contains(SessionSecurityPolicy.relaxed));
      expect(SessionSecurityPolicy.values, contains(SessionSecurityPolicy.standard));
      expect(SessionSecurityPolicy.values, contains(SessionSecurityPolicy.strict));
    });
  });

  group('SecurityLevel', () {
    test('has 4 values', () {
      expect(SecurityLevel.values.length, 4);
    });

    test('has correct codes', () {
      expect(SecurityLevel.low.code, 'low');
      expect(SecurityLevel.medium.code, 'medium');
      expect(SecurityLevel.high.code, 'high');
      expect(SecurityLevel.maximum.code, 'maximum');
    });
  });

  group('SecurityConfig default', () {
    test('has safe defaults', () {
      const config = SecurityConfig();
      expect(config.enableCertificatePinning, isFalse);
      expect(config.strictCertificatePinning, isFalse);
      expect(config.allowPinningDebugBypass, isTrue);
      expect(config.requestTimeout, const Duration(seconds: 30));
      expect(config.deviceIntegrityPolicy, DeviceIntegrityPolicy.disabled);
      expect(config.enforceSecurityInDebug, isFalse);
      expect(config.allowEmulators, isTrue);
      expect(config.logSecurityEvents, isTrue);
      expect(config.blockMockLocation, isFalse);
      expect(config.sessionPolicy, SessionSecurityPolicy.disabled);
      expect(config.sessionTimeout, const Duration(minutes: 15));
      expect(config.screenshotPolicy, ScreenshotPolicy.disabled);
      expect(config.level, SecurityLevel.low);
      expect(config.logAuthEvents, isTrue);
      expect(config.showScreenSecurityWarning, isFalse);
    });
  });

  group('SecurityConfig.production', () {
    test('enables certificate pinning strictly', () {
      expect(SecurityConfig.production.enableCertificatePinning, isTrue);
      expect(SecurityConfig.production.strictCertificatePinning, isTrue);
      expect(SecurityConfig.production.allowPinningDebugBypass, isFalse);
    });

    test('blocks rooted/jailbroken devices', () {
      expect(SecurityConfig.production.deviceIntegrityPolicy,
          DeviceIntegrityPolicy.block);
    });

    test('disallows emulators', () {
      expect(SecurityConfig.production.allowEmulators, isFalse);
    });

    test('blocks mock location', () {
      expect(SecurityConfig.production.blockMockLocation, isTrue);
    });

    test('uses standard session policy', () {
      expect(SecurityConfig.production.sessionPolicy,
          SessionSecurityPolicy.standard);
      expect(SecurityConfig.production.sessionTimeout,
          const Duration(minutes: 15));
    });

    test('uses sensitive-only screenshot prevention', () {
      expect(SecurityConfig.production.screenshotPolicy,
          ScreenshotPolicy.sensitiveOnly);
    });

    test('has high security level', () {
      expect(SecurityConfig.production.level, SecurityLevel.high);
    });

    test('shows screen security warning', () {
      expect(SecurityConfig.production.showScreenSecurityWarning, isTrue);
    });

    test('has shorter request timeout', () {
      expect(SecurityConfig.production.requestTimeout,
          const Duration(seconds: 20));
    });

    test('logs security and auth events', () {
      expect(SecurityConfig.production.logSecurityEvents, isTrue);
      expect(SecurityConfig.production.logAuthEvents, isTrue);
    });
  });

  group('SecurityConfig.staging', () {
    test('enables certificate pinning but not strict', () {
      expect(SecurityConfig.staging.enableCertificatePinning, isTrue);
      expect(SecurityConfig.staging.strictCertificatePinning, isFalse);
      expect(SecurityConfig.staging.allowPinningDebugBypass, isTrue);
    });

    test('uses warn policy for device integrity', () {
      expect(SecurityConfig.staging.deviceIntegrityPolicy,
          DeviceIntegrityPolicy.warn);
    });

    test('allows emulators for testing', () {
      expect(SecurityConfig.staging.allowEmulators, isTrue);
    });

    test('uses relaxed session policy', () {
      expect(SecurityConfig.staging.sessionPolicy,
          SessionSecurityPolicy.relaxed);
      expect(SecurityConfig.staging.sessionTimeout,
          const Duration(minutes: 30));
    });

    test('has medium security level', () {
      expect(SecurityConfig.staging.level, SecurityLevel.medium);
    });
  });

  group('SecurityConfig.development', () {
    test('disables certificate pinning', () {
      const config = SecurityConfig(); // development defaults
      expect(config.enableCertificatePinning, isFalse);
    });

    test('disables device integrity checks', () {
      const config = SecurityConfig();
      expect(config.deviceIntegrityPolicy, DeviceIntegrityPolicy.disabled);
    });

    test('allows emulators', () {
      const config = SecurityConfig();
      expect(config.allowEmulators, isTrue);
    });

    test('disables session timeout', () {
      const config = SecurityConfig();
      expect(config.sessionPolicy, SessionSecurityPolicy.disabled);
    });
  });

  group('SecurityConfig custom', () {
    test('accepts custom values', () {
      const config = SecurityConfig(
        enableCertificatePinning: true,
        strictCertificatePinning: true,
        deviceIntegrityPolicy: DeviceIntegrityPolicy.blockAll,
        sessionTimeout: Duration(minutes: 5),
        screenshotPolicy: ScreenshotPolicy.allScreens,
        requestTimeout: Duration(seconds: 10),
        level: SecurityLevel.maximum,
      );

      expect(config.enableCertificatePinning, isTrue);
      expect(config.strictCertificatePinning, isTrue);
      expect(config.deviceIntegrityPolicy, DeviceIntegrityPolicy.blockAll);
      expect(config.sessionTimeout, const Duration(minutes: 5));
      expect(config.screenshotPolicy, ScreenshotPolicy.allScreens);
      expect(config.requestTimeout, const Duration(seconds: 10));
      expect(config.level, SecurityLevel.maximum);
    });
  });
}
