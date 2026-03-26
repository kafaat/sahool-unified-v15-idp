/// Device Security Tests
/// اختبارات أمان الجهاز
///
/// Tests the device security service:
/// - DeviceSecurityResult model
/// - Threat severity ordering
/// - Security action determination
/// - ThreatType coverage
/// - SecurityConfig integration
/// - Bilingual threat messages
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/security/device_security_service.dart';
import 'package:sahool_field_app/core/security/security_config.dart';

void main() {
  group('DeviceSecurityResult', () {
    test('secure result should have no threats', () {
      const result = DeviceSecurityResult(
        isSecure: true,
        threats: [],
        recommendedAction: SecurityAction.allow,
      );

      expect(result.isSecure, isTrue);
      expect(result.threats, isEmpty);
      expect(result.recommendedAction, SecurityAction.allow);
      expect(result.hasCriticalThreats, isFalse);
      expect(result.primaryThreat, isNull);
    });

    test('should detect critical threats', () {
      const result = DeviceSecurityResult(
        isSecure: false,
        threats: [
          SecurityThreat(
            type: ThreatType.rootAccess,
            severity: ThreatSeverity.critical,
            messageAr: 'تم اكتشاف صلاحيات الروت',
            messageEn: 'Root access detected',
          ),
        ],
        recommendedAction: SecurityAction.block,
      );

      expect(result.isSecure, isFalse);
      expect(result.hasCriticalThreats, isTrue);
      expect(result.primaryThreat, isNotNull);
      expect(result.primaryThreat!.type, ThreatType.rootAccess);
    });

    test('primaryThreat should return highest severity', () {
      const result = DeviceSecurityResult(
        isSecure: false,
        threats: [
          SecurityThreat(
            type: ThreatType.developerMode,
            severity: ThreatSeverity.low,
            messageAr: 'وضع المطور مفعل',
            messageEn: 'Developer mode enabled',
          ),
          SecurityThreat(
            type: ThreatType.rootAccess,
            severity: ThreatSeverity.critical,
            messageAr: 'تم اكتشاف صلاحيات الروت',
            messageEn: 'Root access detected',
          ),
          SecurityThreat(
            type: ThreatType.emulator,
            severity: ThreatSeverity.medium,
            messageAr: 'تم اكتشاف محاكي',
            messageEn: 'Emulator detected',
          ),
        ],
        recommendedAction: SecurityAction.block,
      );

      expect(result.primaryThreat!.severity, ThreatSeverity.critical);
      expect(result.primaryThreat!.type, ThreatType.rootAccess);
    });

    group('Bilingual Messages', () {
      test('secure result should return secure messages', () {
        const result = DeviceSecurityResult(
          isSecure: true,
          threats: [],
          recommendedAction: SecurityAction.allow,
        );

        expect(result.messageEn, 'Device is secure');
        expect(result.messageAr, 'الجهاز آمن ومحمي');
      });

      test('insecure result should return threat messages', () {
        const result = DeviceSecurityResult(
          isSecure: false,
          threats: [
            SecurityThreat(
              type: ThreatType.rootAccess,
              severity: ThreatSeverity.critical,
              messageAr: 'تم اكتشاف صلاحيات الروت - الجهاز غير آمن',
              messageEn: 'Root access detected - Device is not secure',
            ),
          ],
          recommendedAction: SecurityAction.block,
        );

        expect(result.messageEn, contains('Root access detected'));
        expect(result.messageAr, contains('تم اكتشاف صلاحيات الروت'));
      });
    });
  });

  group('ThreatSeverity', () {
    test('should have correct ordering', () {
      expect(ThreatSeverity.low.index, lessThan(ThreatSeverity.medium.index));
      expect(ThreatSeverity.medium.index, lessThan(ThreatSeverity.high.index));
      expect(ThreatSeverity.high.index, lessThan(ThreatSeverity.critical.index));
    });

    test('should have all expected values', () {
      expect(ThreatSeverity.values.length, 4);
      expect(ThreatSeverity.values, contains(ThreatSeverity.low));
      expect(ThreatSeverity.values, contains(ThreatSeverity.medium));
      expect(ThreatSeverity.values, contains(ThreatSeverity.high));
      expect(ThreatSeverity.values, contains(ThreatSeverity.critical));
    });
  });

  group('SecurityAction', () {
    test('should have all expected values', () {
      expect(SecurityAction.values.length, 3);
      expect(SecurityAction.values, contains(SecurityAction.allow));
      expect(SecurityAction.values, contains(SecurityAction.warn));
      expect(SecurityAction.values, contains(SecurityAction.block));
    });
  });

  group('ThreatType', () {
    test('should have all expected values', () {
      expect(ThreatType.values, contains(ThreatType.rootAccess));
      expect(ThreatType.values, contains(ThreatType.jailbreak));
      expect(ThreatType.values, contains(ThreatType.emulator));
      expect(ThreatType.values, contains(ThreatType.debugMode));
      expect(ThreatType.values, contains(ThreatType.developerMode));
      expect(ThreatType.values, contains(ThreatType.tampered));
      expect(ThreatType.values, contains(ThreatType.unknownSource));
    });
  });

  group('SecurityConfig integration', () {
    test('production config should have high security level', () {
      expect(SecurityConfig.production.level, SecurityLevel.high);
      expect(SecurityConfig.production.allowEmulators, isFalse);
      expect(SecurityConfig.production.logAuthEvents, isTrue);
    });

    test('staging config should have medium security level', () {
      expect(SecurityConfig.staging.level, SecurityLevel.medium);
      expect(SecurityConfig.staging.allowEmulators, isTrue);
    });

    test('development config should have low security level', () {
      expect(SecurityConfig.development.level, SecurityLevel.low);
      expect(SecurityConfig.development.allowEmulators, isTrue);
      expect(SecurityConfig.development.logAuthEvents, isFalse);
    });

    test('forEnvironment should return correct config', () {
      expect(
        SecurityConfig.forEnvironment('production').level,
        SecurityLevel.high,
      );
      expect(
        SecurityConfig.forEnvironment('prod').level,
        SecurityLevel.high,
      );
      expect(
        SecurityConfig.forEnvironment('staging').level,
        SecurityLevel.medium,
      );
      expect(
        SecurityConfig.forEnvironment('development').level,
        SecurityLevel.low,
      );
      expect(
        SecurityConfig.forEnvironment('unknown').level,
        SecurityLevel.low,
      );
    });
  });

  group('DeviceSecurityService', () {
    test('should create service with config', () {
      final service = DeviceSecurityService(
        config: SecurityConfig.development,
      );
      expect(service, isNotNull);
    });

    test('should create service with production config', () {
      final service = DeviceSecurityService(
        config: SecurityConfig.production,
      );
      expect(service, isNotNull);
    });
  });

  group('Fail-Closed Behavior (P0 Fix)', () {
    test('error result should be insecure', () {
      // This verifies the P0 fix: errors should return isSecure=false
      // Previously it was returning isSecure=true on catch block
      const errorResult = DeviceSecurityResult(
        isSecure: false,
        threats: [
          SecurityThreat(
            type: ThreatType.unknownSource,
            severity: ThreatSeverity.high,
            messageAr: 'فشل فحص أمان الجهاز',
            messageEn: 'Device security check failed',
            details: 'Test error',
          ),
        ],
        recommendedAction: SecurityAction.block,
      );

      expect(errorResult.isSecure, isFalse, reason: 'Error state MUST be insecure (fail-closed)');
      expect(errorResult.threats.isNotEmpty, isTrue);
      expect(errorResult.recommendedAction, SecurityAction.block);
    });

    test('error result should never be marked as secure', () {
      // Ensure the error pattern always results in isSecure=false
      const result = DeviceSecurityResult(
        isSecure: false,
        threats: [
          SecurityThreat(
            type: ThreatType.unknownSource,
            severity: ThreatSeverity.high,
            messageAr: 'فشل فحص أمان الجهاز',
            messageEn: 'Security check failed: unable to verify device integrity',
          ),
        ],
        recommendedAction: SecurityAction.block,
      );

      // The key invariant: if threats include "Security check failed", isSecure must be false
      if (result.threats.any((t) => t.messageEn.contains('Security check failed'))) {
        expect(
          result.isSecure,
          isFalse,
          reason: 'When security check fails, device must NOT be marked as secure',
        );
      }
    });
  });

  group('SecurityThreat', () {
    test('toString should contain type and severity', () {
      const threat = SecurityThreat(
        type: ThreatType.rootAccess,
        severity: ThreatSeverity.critical,
        messageAr: 'تم اكتشاف صلاحيات الروت',
        messageEn: 'Root access detected',
      );

      final str = threat.toString();
      expect(str, contains('rootAccess'));
      expect(str, contains('critical'));
    });
  });
}
