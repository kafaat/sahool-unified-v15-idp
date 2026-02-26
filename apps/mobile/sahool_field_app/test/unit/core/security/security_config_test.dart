/// Security Config Tests
/// اختبارات إعدادات الأمان
///
/// Tests for centralized security configuration

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/security/security_config.dart';

void main() {
  group('SecurityConfig', () {
    group('Production Config', () {
      test('should enable certificate pinning', () {
        expect(SecurityConfig.production.enableCertificatePinning, isTrue);
        expect(SecurityConfig.production.strictCertificatePinning, isTrue);
        expect(SecurityConfig.production.allowPinningDebugBypass, isFalse);
      });

      test('should block rooted devices', () {
        expect(
          SecurityConfig.production.deviceIntegrityPolicy,
          DeviceIntegrityPolicy.block,
        );
      });

      test('should not allow emulators', () {
        expect(SecurityConfig.production.allowEmulators, isFalse);
      });

      test('should block mock locations', () {
        expect(SecurityConfig.production.blockMockLocation, isTrue);
      });

      test('should have standard session timeout', () {
        expect(
          SecurityConfig.production.sessionPolicy,
          SessionSecurityPolicy.standard,
        );
        expect(
          SecurityConfig.production.sessionTimeout,
          const Duration(minutes: 15),
        );
      });

      test('should enable screenshot prevention on sensitive screens', () {
        expect(
          SecurityConfig.production.screenshotPolicy,
          ScreenshotPolicy.sensitiveOnly,
        );
      });
    });

    group('Staging Config', () {
      test('should enable non-strict certificate pinning', () {
        expect(SecurityConfig.staging.enableCertificatePinning, isTrue);
        expect(SecurityConfig.staging.strictCertificatePinning, isFalse);
        expect(SecurityConfig.staging.allowPinningDebugBypass, isTrue);
      });

      test('should warn only for device integrity', () {
        expect(
          SecurityConfig.staging.deviceIntegrityPolicy,
          DeviceIntegrityPolicy.warn,
        );
      });

      test('should allow emulators', () {
        expect(SecurityConfig.staging.allowEmulators, isTrue);
      });
    });

    group('Development Config', () {
      test('should disable certificate pinning', () {
        expect(SecurityConfig.development.enableCertificatePinning, isFalse);
      });

      test('should disable device integrity checks', () {
        expect(
          SecurityConfig.development.deviceIntegrityPolicy,
          DeviceIntegrityPolicy.disabled,
        );
      });

      test('should disable screenshot prevention', () {
        expect(
          SecurityConfig.development.screenshotPolicy,
          ScreenshotPolicy.disabled,
        );
      });

      test('should disable session timeout', () {
        expect(
          SecurityConfig.development.sessionPolicy,
          SessionSecurityPolicy.disabled,
        );
      });
    });

    group('forEnvironment', () {
      test('should return production for prod strings', () {
        expect(
          SecurityConfig.forEnvironment('production').enableCertificatePinning,
          isTrue,
        );
        expect(
          SecurityConfig.forEnvironment('prod').enableCertificatePinning,
          isTrue,
        );
      });

      test('should return staging for stage strings', () {
        expect(
          SecurityConfig.forEnvironment('staging').deviceIntegrityPolicy,
          DeviceIntegrityPolicy.warn,
        );
        expect(
          SecurityConfig.forEnvironment('stage').deviceIntegrityPolicy,
          DeviceIntegrityPolicy.warn,
        );
      });

      test('should return development for dev and unknown strings', () {
        expect(
          SecurityConfig.forEnvironment('development').deviceIntegrityPolicy,
          DeviceIntegrityPolicy.disabled,
        );
        expect(
          SecurityConfig.forEnvironment('dev').deviceIntegrityPolicy,
          DeviceIntegrityPolicy.disabled,
        );
        expect(
          SecurityConfig.forEnvironment('unknown').deviceIntegrityPolicy,
          DeviceIntegrityPolicy.disabled,
        );
      });
    });

    group('getEffectiveSessionTimeout', () {
      test('disabled should return very long timeout', () {
        const config = SecurityConfig(sessionPolicy: SessionSecurityPolicy.disabled);
        expect(config.getEffectiveSessionTimeout(), const Duration(days: 365));
      });

      test('relaxed should return 2 hours', () {
        const config = SecurityConfig(sessionPolicy: SessionSecurityPolicy.relaxed);
        expect(config.getEffectiveSessionTimeout(), const Duration(hours: 2));
      });

      test('standard should return configured timeout', () {
        const config = SecurityConfig(
          sessionPolicy: SessionSecurityPolicy.standard,
          sessionTimeout: Duration(minutes: 20),
        );
        expect(config.getEffectiveSessionTimeout(), const Duration(minutes: 20));
      });

      test('strict should return 5 minutes', () {
        const config = SecurityConfig(sessionPolicy: SessionSecurityPolicy.strict);
        expect(config.getEffectiveSessionTimeout(), const Duration(minutes: 5));
      });
    });

    group('Helper Properties', () {
      test('isScreenshotPreventionEnabled', () {
        expect(
          const SecurityConfig(screenshotPolicy: ScreenshotPolicy.disabled)
              .isScreenshotPreventionEnabled,
          isFalse,
        );
        expect(
          const SecurityConfig(screenshotPolicy: ScreenshotPolicy.sensitiveOnly)
              .isScreenshotPreventionEnabled,
          isTrue,
        );
        expect(
          const SecurityConfig(screenshotPolicy: ScreenshotPolicy.allScreens)
              .isScreenshotPreventionEnabled,
          isTrue,
        );
      });

      test('isSessionTimeoutEnabled', () {
        expect(
          const SecurityConfig(sessionPolicy: SessionSecurityPolicy.disabled)
              .isSessionTimeoutEnabled,
          isFalse,
        );
        expect(
          const SecurityConfig(sessionPolicy: SessionSecurityPolicy.standard)
              .isSessionTimeoutEnabled,
          isTrue,
        );
      });
    });

    group('copyWith', () {
      test('should copy with new values', () {
        final config = SecurityConfig.development.copyWith(
          enableCertificatePinning: true,
          deviceIntegrityPolicy: DeviceIntegrityPolicy.block,
        );

        expect(config.enableCertificatePinning, isTrue);
        expect(config.deviceIntegrityPolicy, DeviceIntegrityPolicy.block);
        // Other values preserved from development
        expect(config.allowEmulators, isTrue);
      });
    });
  });
}
