import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_atmosphere/core/security/device_security.dart';

void main() {
  group('DeviceSecurityService Tests', () {
    late DeviceSecurityService securityService;

    setUp(() {
      securityService = DeviceSecurityService();
    });

    test('Service is singleton', () {
      final service1 = DeviceSecurityService();
      final service2 = DeviceSecurityService();

      expect(identical(service1, service2), isTrue);
    });

    test('getThreatMessage returns Arabic message when arabic=true', () {
      final message = securityService.getThreatMessage(
        SecurityThreatLevel.high,
        arabic: true,
      );

      expect(message, contains('روت'));
      expect(message, contains('جيلبريك'));
    });

    test('getThreatMessage returns English message when arabic=false', () {
      final message = securityService.getThreatMessage(
        SecurityThreatLevel.high,
        arabic: false,
      );

      expect(message.toLowerCase(), contains('root'));
      expect(message.toLowerCase(), contains('jailbreak'));
    });

    test('getThreatMessage handles all threat levels', () {
      for (final level in SecurityThreatLevel.values) {
        final arabicMessage = securityService.getThreatMessage(level, arabic: true);
        final englishMessage = securityService.getThreatMessage(level, arabic: false);

        expect(arabicMessage.isNotEmpty, isTrue);
        expect(englishMessage.isNotEmpty, isTrue);
      }
    });
  });

  group('SecurityCheckResult Tests', () {
    test('hasIssues returns true when threats exist', () {
      const result = SecurityCheckResult(
        isCompromised: false,
        isEmulator: false,
        isDebugMode: true,
        threatLevel: SecurityThreatLevel.low,
        threats: ['Debug mode active'],
        deviceInfo: {},
      );

      expect(result.hasIssues, isTrue);
    });

    test('hasIssues returns false when no threats', () {
      const result = SecurityCheckResult(
        isCompromised: false,
        isEmulator: false,
        isDebugMode: false,
        threatLevel: SecurityThreatLevel.none,
        threats: [],
        deviceInfo: {},
      );

      expect(result.hasIssues, isFalse);
    });

    test('toString contains relevant info', () {
      const result = SecurityCheckResult(
        isCompromised: true,
        isEmulator: false,
        isDebugMode: false,
        threatLevel: SecurityThreatLevel.high,
        threats: ['Device is rooted'],
        deviceInfo: {'platform': 'Android'},
      );

      final str = result.toString();
      expect(str, contains('compromised: true'));
      expect(str, contains('emulator: false'));
      expect(str, contains('high'));
    });
  });

  group('SecurityThreatLevel Tests', () {
    test('Threat levels are ordered correctly', () {
      expect(SecurityThreatLevel.none.index < SecurityThreatLevel.low.index, isTrue);
      expect(SecurityThreatLevel.low.index < SecurityThreatLevel.medium.index, isTrue);
      expect(SecurityThreatLevel.medium.index < SecurityThreatLevel.high.index, isTrue);
    });

    test('All threat levels have enum values', () {
      expect(SecurityThreatLevel.values.length, 5);
      expect(SecurityThreatLevel.values.contains(SecurityThreatLevel.none), isTrue);
      expect(SecurityThreatLevel.values.contains(SecurityThreatLevel.low), isTrue);
      expect(SecurityThreatLevel.values.contains(SecurityThreatLevel.medium), isTrue);
      expect(SecurityThreatLevel.values.contains(SecurityThreatLevel.high), isTrue);
      expect(SecurityThreatLevel.values.contains(SecurityThreatLevel.unknown), isTrue);
    });
  });
}
