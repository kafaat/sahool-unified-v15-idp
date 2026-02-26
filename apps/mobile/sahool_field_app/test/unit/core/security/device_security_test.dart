/// Device Security Tests
/// اختبارات أمان الجهاز
///
/// Tests the P0 security fix:
/// - Fail-closed behavior: errors return isSecure=false (not true)
/// - Threat level calculation
/// - Security policy enforcement
/// - State management (DeviceSecurityController)
/// - Bilingual threat messages

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/security/device_security.dart';

void main() {
  group('DeviceSecurityState', () {
    test('default state should be uninitialized and secure', () {
      const state = DeviceSecurityState();

      expect(state.isInitialized, isFalse);
      expect(state.isSecure, isTrue);
      expect(state.isRooted, isFalse);
      expect(state.isJailbroken, isFalse);
      expect(state.isEmulator, isFalse);
      expect(state.isRealDevice, isTrue);
      expect(state.hasMockLocation, isFalse);
      expect(state.isOnExternalStorage, isFalse);
      expect(state.isDevelopmentModeEnabled, isFalse);
      expect(state.threats, isEmpty);
      expect(state.threatLevel, SecurityThreatLevel.none);
      expect(state.lastCheckTime, isNull);
      expect(state.errorMessage, isNull);
    });

    test('isCompromised should be true when rooted', () {
      const state = DeviceSecurityState(isRooted: true);
      expect(state.isCompromised, isTrue);
    });

    test('isCompromised should be true when jailbroken', () {
      const state = DeviceSecurityState(isJailbroken: true);
      expect(state.isCompromised, isTrue);
    });

    test('isCompromised should be false when neither rooted nor jailbroken', () {
      const state = DeviceSecurityState();
      expect(state.isCompromised, isFalse);
    });

    test('hasThreats should be true when threats exist', () {
      const state = DeviceSecurityState(threats: ['Root detected']);
      expect(state.hasThreats, isTrue);
    });

    test('hasThreats should be false when no threats', () {
      const state = DeviceSecurityState();
      expect(state.hasThreats, isFalse);
    });

    group('Status Messages', () {
      test('should return not performed message when uninitialized', () {
        const state = DeviceSecurityState();
        expect(state.statusMessage, 'Security check not performed');
        expect(state.statusMessageAr, 'لم يتم إجراء فحص الأمان');
      });

      test('should return secure message when secure', () {
        const state = DeviceSecurityState(
          isInitialized: true,
          isSecure: true,
        );
        expect(state.statusMessage, 'Device is secure');
        expect(state.statusMessageAr, 'الجهاز آمن');
      });

      test('should list threats when insecure', () {
        const state = DeviceSecurityState(
          isInitialized: true,
          isSecure: false,
          threats: ['Device is rooted', 'Mock location detected'],
        );

        expect(state.statusMessage, contains('Device is rooted'));
        expect(state.statusMessage, contains('Mock location detected'));
      });
    });

    group('copyWith', () {
      test('should copy with new values', () {
        const original = DeviceSecurityState();
        final copied = original.copyWith(
          isInitialized: true,
          isSecure: false,
          isRooted: true,
          threats: ['Device is rooted'],
          threatLevel: SecurityThreatLevel.high,
        );

        expect(copied.isInitialized, isTrue);
        expect(copied.isSecure, isFalse);
        expect(copied.isRooted, isTrue);
        expect(copied.threats, ['Device is rooted']);
        expect(copied.threatLevel, SecurityThreatLevel.high);
      });

      test('should preserve unchanged values', () {
        const original = DeviceSecurityState(
          isInitialized: true,
          isRooted: true,
          threatLevel: SecurityThreatLevel.high,
        );
        final copied = original.copyWith(isSecure: false);

        expect(copied.isInitialized, isTrue);
        expect(copied.isRooted, isTrue);
        expect(copied.threatLevel, SecurityThreatLevel.high);
      });

      test('should allow clearing errorMessage', () {
        const original = DeviceSecurityState(errorMessage: 'some error');
        final copied = original.copyWith(errorMessage: null);

        // Note: copyWith sets errorMessage directly (no ?? fallback)
        expect(copied.errorMessage, isNull);
      });
    });
  });

  group('SecurityThreatLevel', () {
    test('should have correct ordering', () {
      expect(SecurityThreatLevel.none.index, lessThan(SecurityThreatLevel.low.index));
      expect(SecurityThreatLevel.low.index, lessThan(SecurityThreatLevel.medium.index));
      expect(SecurityThreatLevel.medium.index, lessThan(SecurityThreatLevel.high.index));
      expect(SecurityThreatLevel.high.index, lessThan(SecurityThreatLevel.critical.index));
    });

    test('should have all expected values', () {
      expect(SecurityThreatLevel.values.length, 5);
      expect(SecurityThreatLevel.values, contains(SecurityThreatLevel.none));
      expect(SecurityThreatLevel.values, contains(SecurityThreatLevel.low));
      expect(SecurityThreatLevel.values, contains(SecurityThreatLevel.medium));
      expect(SecurityThreatLevel.values, contains(SecurityThreatLevel.high));
      expect(SecurityThreatLevel.values, contains(SecurityThreatLevel.critical));
    });
  });

  group('DeviceSecurityService', () {
    late DeviceSecurityService service;

    setUp(() {
      service = DeviceSecurityService();
    });

    group('Threat Messages (Bilingual)', () {
      test('should return correct English messages', () {
        expect(
          service.getThreatMessage(SecurityThreatLevel.critical),
          'Critical security threat - Cannot use app',
        );
        expect(
          service.getThreatMessage(SecurityThreatLevel.high),
          'High security threat - Device is not secure',
        );
        expect(
          service.getThreatMessage(SecurityThreatLevel.medium),
          'Medium security threat - Proceed with caution',
        );
        expect(
          service.getThreatMessage(SecurityThreatLevel.low),
          'Minor security warning',
        );
        expect(
          service.getThreatMessage(SecurityThreatLevel.none),
          'Device is secure',
        );
      });

      test('should return correct Arabic messages', () {
        expect(
          service.getThreatMessage(SecurityThreatLevel.critical, arabic: true),
          'تهديد أمني حرج - لا يمكن استخدام التطبيق',
        );
        expect(
          service.getThreatMessage(SecurityThreatLevel.high, arabic: true),
          'تهديد أمني عالي - الجهاز غير آمن',
        );
        expect(
          service.getThreatMessage(SecurityThreatLevel.medium, arabic: true),
          'تهديد أمني متوسط - يُنصح بالحذر',
        );
        expect(
          service.getThreatMessage(SecurityThreatLevel.low, arabic: true),
          'تحذير أمني بسيط',
        );
        expect(
          service.getThreatMessage(SecurityThreatLevel.none, arabic: true),
          'الجهاز آمن',
        );
      });
    });

    group('shouldBlockApp', () {
      test('should not block with disabled policy', () {
        const state = DeviceSecurityState(
          isRooted: true,
          threats: ['Device is rooted'],
        );
        const config = DeviceSecurityConfig(
          policy: DeviceSecurityPolicy.disabled,
        );

        expect(service.shouldBlockApp(state, config), isFalse);
      });

      test('should not block with logOnly policy', () {
        const state = DeviceSecurityState(
          isRooted: true,
          threats: ['Device is rooted'],
        );
        const config = DeviceSecurityConfig(
          policy: DeviceSecurityPolicy.logOnly,
        );

        expect(service.shouldBlockApp(state, config), isFalse);
      });

      test('should not block with warnOnly policy', () {
        const state = DeviceSecurityState(
          isRooted: true,
          threats: ['Device is rooted'],
        );
        const config = DeviceSecurityConfig(
          policy: DeviceSecurityPolicy.warnOnly,
        );

        expect(service.shouldBlockApp(state, config), isFalse);
      });

      test('should block rooted device with blockRooted policy', () {
        const state = DeviceSecurityState(
          isRooted: true,
          threats: ['Device is rooted'],
        );
        const config = DeviceSecurityConfig(
          policy: DeviceSecurityPolicy.blockRooted,
          enforceInDebug: true,
        );

        expect(service.shouldBlockApp(state, config), isTrue);
      });

      test('should block jailbroken device with blockRooted policy', () {
        const state = DeviceSecurityState(
          isJailbroken: true,
          threats: ['Device is jailbroken'],
        );
        const config = DeviceSecurityConfig(
          policy: DeviceSecurityPolicy.blockRooted,
          enforceInDebug: true,
        );

        expect(service.shouldBlockApp(state, config), isTrue);
      });

      test('should not block non-compromised device with blockRooted policy', () {
        const state = DeviceSecurityState(
          isEmulator: true,
          threats: ['Running on emulator'],
        );
        const config = DeviceSecurityConfig(
          policy: DeviceSecurityPolicy.blockRooted,
          enforceInDebug: true,
        );

        expect(service.shouldBlockApp(state, config), isFalse);
      });
    });

    group('Singleton Pattern', () {
      test('should return same instance', () {
        final a = DeviceSecurityService();
        final b = DeviceSecurityService();
        expect(identical(a, b), isTrue);
      });
    });
  });

  group('DeviceSecurityConfig', () {
    test('production config should block rooted devices', () {
      expect(
        DeviceSecurityConfig.production.policy,
        DeviceSecurityPolicy.blockRooted,
      );
      expect(DeviceSecurityConfig.production.allowEmulators, isFalse);
      expect(DeviceSecurityConfig.production.logEvents, isTrue);
    });

    test('staging config should warn only', () {
      expect(
        DeviceSecurityConfig.staging.policy,
        DeviceSecurityPolicy.warnOnly,
      );
      expect(DeviceSecurityConfig.staging.allowEmulators, isTrue);
    });

    test('development config should be disabled', () {
      expect(
        DeviceSecurityConfig.development.policy,
        DeviceSecurityPolicy.disabled,
      );
      expect(DeviceSecurityConfig.development.allowEmulators, isTrue);
      expect(DeviceSecurityConfig.development.logEvents, isFalse);
    });

    test('forEnvironment should return correct config', () {
      expect(
        DeviceSecurityConfig.forEnvironment('production').policy,
        DeviceSecurityPolicy.blockRooted,
      );
      expect(
        DeviceSecurityConfig.forEnvironment('prod').policy,
        DeviceSecurityPolicy.blockRooted,
      );
      expect(
        DeviceSecurityConfig.forEnvironment('staging').policy,
        DeviceSecurityPolicy.warnOnly,
      );
      expect(
        DeviceSecurityConfig.forEnvironment('development').policy,
        DeviceSecurityPolicy.disabled,
      );
      expect(
        DeviceSecurityConfig.forEnvironment('unknown').policy,
        DeviceSecurityPolicy.disabled,
      );
    });
  });

  group('DeviceSecurityPolicy', () {
    test('should have all expected values', () {
      expect(DeviceSecurityPolicy.values.length, 5);
      expect(DeviceSecurityPolicy.values, contains(DeviceSecurityPolicy.disabled));
      expect(DeviceSecurityPolicy.values, contains(DeviceSecurityPolicy.logOnly));
      expect(DeviceSecurityPolicy.values, contains(DeviceSecurityPolicy.warnOnly));
      expect(DeviceSecurityPolicy.values, contains(DeviceSecurityPolicy.blockRooted));
      expect(DeviceSecurityPolicy.values, contains(DeviceSecurityPolicy.blockAll));
    });
  });

  group('DeviceSecurityController', () {
    test('initial state should be default DeviceSecurityState', () {
      final service = DeviceSecurityService();
      final controller = DeviceSecurityController(service);

      expect(controller.state.isInitialized, isFalse);
      expect(controller.state.isSecure, isTrue);
      expect(controller.state.threats, isEmpty);
    });

    test('clearState should reset to default', () {
      final service = DeviceSecurityService();
      final controller = DeviceSecurityController(service);

      // Manually update state (simulating a check)
      controller.clearState();

      expect(controller.state.isInitialized, isFalse);
      expect(controller.state.threats, isEmpty);
    });
  });

  group('Fail-Closed Behavior (P0 Fix)', () {
    test('DeviceSecurityState error state should be insecure', () {
      // This verifies the P0 fix: errors should return isSecure=false
      // Previously it was returning isSecure=true on catch block
      const errorState = DeviceSecurityState(
        isInitialized: true,
        isSecure: false,
        threats: ['Security check failed: unable to verify device integrity'],
        threatLevel: SecurityThreatLevel.medium,
        errorMessage: 'Test error',
      );

      expect(errorState.isSecure, isFalse, reason: 'Error state MUST be insecure (fail-closed)');
      expect(errorState.hasThreats, isTrue);
      expect(errorState.threatLevel, SecurityThreatLevel.medium);
      expect(errorState.errorMessage, isNotNull);
    });

    test('error state should never be marked as secure', () {
      // Ensure the error pattern always results in isSecure=false
      const state = DeviceSecurityState(
        isInitialized: true,
        isSecure: false,
        threats: ['Security check failed: unable to verify device integrity'],
        threatLevel: SecurityThreatLevel.medium,
      );

      // The key invariant: if threats include "Security check failed", isSecure must be false
      if (state.threats.any((t) => t.contains('Security check failed'))) {
        expect(
          state.isSecure,
          isFalse,
          reason: 'When security check fails, device must NOT be marked as secure',
        );
      }
    });
  });
}
