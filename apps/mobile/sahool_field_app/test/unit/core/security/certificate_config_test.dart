/// Certificate Config Tests
/// اختبارات إعدادات الشهادات الرقمية
///
/// Tests for CertificateConfig and CertificateRotationHelper classes:
/// - Placeholder hash detection
/// - Environment-specific pin retrieval
/// - Pin merging
/// - Certificate rotation (add, remove expired, detect expiring)
/// - Pin configuration validation
/// - Configuration status reporting
/// - CertificatePin expiry logic
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/security/certificate_config.dart';
import 'package:sahool_field_app/core/security/certificate_pinning_service.dart';

void main() {
  group('CertificateConfig', () {
    group('getProductionPins', () {
      test('should return pins for api.sahool.app', () {
        final pins = CertificateConfig.getProductionPins();
        expect(pins.containsKey('api.sahool.app'), isTrue);
        expect(pins['api.sahool.app']!.length, equals(3));
      });

      test('should return pins for ws.sahool.app', () {
        final pins = CertificateConfig.getProductionPins();
        expect(pins.containsKey('ws.sahool.app'), isTrue);
        expect(pins['ws.sahool.app']!.length, equals(2));
      });

      test('should return pins for *.sahool.io wildcard domain', () {
        final pins = CertificateConfig.getProductionPins();
        expect(pins.containsKey('*.sahool.io'), isTrue);
        expect(pins['*.sahool.io']!.length, equals(2));
      });

      test('should contain exactly 3 production domains', () {
        final pins = CertificateConfig.getProductionPins();
        expect(pins.keys.length, equals(3));
      });

      test('should use sha256 pin type for all production pins', () {
        final pins = CertificateConfig.getProductionPins();
        for (final domainPins in pins.values) {
          for (final pin in domainPins) {
            expect(pin.type, equals(PinType.sha256));
          }
        }
      });
    });

    group('getStagingPins', () {
      test('should return pins for api-staging.sahool.app', () {
        final pins = CertificateConfig.getStagingPins();
        expect(pins.containsKey('api-staging.sahool.app'), isTrue);
        expect(pins['api-staging.sahool.app']!.length, equals(2));
      });

      test('should return pins for ws-staging.sahool.app', () {
        final pins = CertificateConfig.getStagingPins();
        expect(pins.containsKey('ws-staging.sahool.app'), isTrue);
        expect(pins['ws-staging.sahool.app']!.length, equals(2));
      });

      test('should contain exactly 2 staging domains', () {
        final pins = CertificateConfig.getStagingPins();
        expect(pins.keys.length, equals(2));
      });
    });

    group('getDevelopmentPins', () {
      test('should return an empty map', () {
        final pins = CertificateConfig.getDevelopmentPins();
        expect(pins, isEmpty);
      });
    });

    group('getPinsForEnvironment', () {
      test('should return production pins for "production"', () {
        final pins = CertificateConfig.getPinsForEnvironment('production');
        expect(pins.containsKey('api.sahool.app'), isTrue);
      });

      test('should return production pins for "prod"', () {
        final pins = CertificateConfig.getPinsForEnvironment('prod');
        expect(pins.containsKey('api.sahool.app'), isTrue);
      });

      test('should return staging pins for "staging"', () {
        final pins = CertificateConfig.getPinsForEnvironment('staging');
        expect(pins.containsKey('api-staging.sahool.app'), isTrue);
      });

      test('should return staging pins for "stage"', () {
        final pins = CertificateConfig.getPinsForEnvironment('stage');
        expect(pins.containsKey('api-staging.sahool.app'), isTrue);
      });

      test('should return development pins for "development"', () {
        final pins = CertificateConfig.getPinsForEnvironment('development');
        expect(pins, isEmpty);
      });

      test('should return development pins for "dev"', () {
        final pins = CertificateConfig.getPinsForEnvironment('dev');
        expect(pins, isEmpty);
      });

      test('should be case-insensitive', () {
        final pins = CertificateConfig.getPinsForEnvironment('PRODUCTION');
        expect(pins.containsKey('api.sahool.app'), isTrue);
      });

      test('should return development pins for unknown environment', () {
        final pins = CertificateConfig.getPinsForEnvironment('unknown');
        expect(pins, isEmpty);
      });
    });

    group('mergePins', () {
      test('should merge pins from multiple maps', () {
        final map1 = <String, List<CertificatePin>>{
          'domain1.com': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aabb' * 16,
              expiryDate: DateTime(2027, 1, 1),
            ),
          ],
        };
        final map2 = <String, List<CertificatePin>>{
          'domain2.com': [
            CertificatePin(
              type: PinType.sha256,
              value: 'ccdd' * 16,
              expiryDate: DateTime(2027, 1, 1),
            ),
          ],
        };

        final merged = CertificateConfig.mergePins([map1, map2]);
        expect(merged.containsKey('domain1.com'), isTrue);
        expect(merged.containsKey('domain2.com'), isTrue);
      });

      test('should combine pins for the same domain', () {
        final map1 = <String, List<CertificatePin>>{
          'shared.com': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aaaa' * 16,
              expiryDate: DateTime(2027, 1, 1),
            ),
          ],
        };
        final map2 = <String, List<CertificatePin>>{
          'shared.com': [
            CertificatePin(
              type: PinType.sha256,
              value: 'bbbb' * 16,
              expiryDate: DateTime(2027, 6, 1),
            ),
          ],
        };

        final merged = CertificateConfig.mergePins([map1, map2]);
        expect(merged['shared.com']!.length, equals(2));
      });

      test('should return empty map when merging empty list', () {
        final merged = CertificateConfig.mergePins([]);
        expect(merged, isEmpty);
      });

      test('should handle merging a single map', () {
        final map1 = <String, List<CertificatePin>>{
          'solo.com': [
            CertificatePin(
              type: PinType.sha256,
              value: 'ffff' * 16,
            ),
          ],
        };

        final merged = CertificateConfig.mergePins([map1]);
        expect(merged.keys.length, equals(1));
        expect(merged['solo.com']!.length, equals(1));
      });
    });
  });

  group('CertificateRotationHelper', () {
    group('addRotationPin', () {
      test('should add a new pin to an existing domain', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aaaa' * 16,
              expiryDate: DateTime(2027, 1, 1),
            ),
          ],
        };

        CertificateRotationHelper.addRotationPin(
          currentPins: pins,
          domain: 'api.sahool.app',
          newFingerprint: 'bbbb' * 16,
          newExpiryDate: DateTime(2028, 1, 1),
        );

        expect(pins['api.sahool.app']!.length, equals(2));
        expect(pins['api.sahool.app']!.last.value, equals('bbbb' * 16));
      });

      test('should create domain entry if it does not exist', () {
        final pins = <String, List<CertificatePin>>{};

        CertificateRotationHelper.addRotationPin(
          currentPins: pins,
          domain: 'new-domain.com',
          newFingerprint: 'cccc' * 16,
          newExpiryDate: DateTime(2028, 6, 1),
        );

        expect(pins.containsKey('new-domain.com'), isTrue);
        expect(pins['new-domain.com']!.length, equals(1));
      });

      test('should set sha256 pin type on added pin', () {
        final pins = <String, List<CertificatePin>>{};

        CertificateRotationHelper.addRotationPin(
          currentPins: pins,
          domain: 'test.com',
          newFingerprint: 'dddd' * 16,
          newExpiryDate: DateTime(2028, 1, 1),
        );

        expect(pins['test.com']!.first.type, equals(PinType.sha256));
      });
    });

    group('removeExpiredPins', () {
      test('should remove expired pins and keep valid ones', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aaaa' * 16,
              expiryDate: DateTime(2020, 1, 1), // expired
            ),
            CertificatePin(
              type: PinType.sha256,
              value: 'bbbb' * 16,
              expiryDate: DateTime(2099, 12, 31), // valid
            ),
          ],
        };

        CertificateRotationHelper.removeExpiredPins(pins);

        expect(pins['api.sahool.app']!.length, equals(1));
        expect(pins['api.sahool.app']!.first.value, equals('bbbb' * 16));
      });

      test('should remove domain entry if all pins are expired', () {
        final pins = <String, List<CertificatePin>>{
          'old-domain.com': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aaaa' * 16,
              expiryDate: DateTime(2020, 1, 1),
            ),
          ],
        };

        CertificateRotationHelper.removeExpiredPins(pins);

        expect(pins.containsKey('old-domain.com'), isFalse);
      });

      test('should not remove pins without expiry date', () {
        final pins = <String, List<CertificatePin>>{
          'no-expiry.com': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aaaa' * 16,
              // no expiryDate => isExpired returns false
            ),
          ],
        };

        CertificateRotationHelper.removeExpiredPins(pins);

        expect(pins['no-expiry.com']!.length, equals(1));
      });
    });

    group('getExpiringPins', () {
      test('should return pins expiring within threshold', () {
        final soonExpiry = DateTime.now().add(const Duration(days: 15));
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aaaa' * 16,
              expiryDate: soonExpiry,
            ),
            CertificatePin(
              type: PinType.sha256,
              value: 'bbbb' * 16,
              expiryDate: DateTime(2099, 12, 31), // far future
            ),
          ],
        };

        final expiring = CertificateRotationHelper.getExpiringPins(
          pins: pins,
          daysThreshold: 30,
        );

        expect(expiring.containsKey('api.sahool.app'), isTrue);
        expect(expiring['api.sahool.app']!.length, equals(1));
        expect(expiring['api.sahool.app']!.first.value, equals('aaaa' * 16));
      });

      test('should not return already expired pins', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aaaa' * 16,
              expiryDate: DateTime(2020, 1, 1), // already expired
            ),
          ],
        };

        final expiring = CertificateRotationHelper.getExpiringPins(
          pins: pins,
          daysThreshold: 30,
        );

        expect(expiring, isEmpty);
      });

      test('should return empty map when no pins are expiring', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aaaa' * 16,
              expiryDate: DateTime(2099, 12, 31),
            ),
          ],
        };

        final expiring = CertificateRotationHelper.getExpiringPins(
          pins: pins,
          daysThreshold: 30,
        );

        expect(expiring, isEmpty);
      });

      test('should respect custom daysThreshold', () {
        final expiresIn50Days = DateTime.now().add(const Duration(days: 50));
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aaaa' * 16,
              expiryDate: expiresIn50Days,
            ),
          ],
        };

        // With 30-day threshold, should not appear
        final expiring30 = CertificateRotationHelper.getExpiringPins(
          pins: pins,
          daysThreshold: 30,
        );
        expect(expiring30, isEmpty);

        // With 60-day threshold, should appear
        final expiring60 = CertificateRotationHelper.getExpiringPins(
          pins: pins,
          daysThreshold: 60,
        );
        expect(expiring60.containsKey('api.sahool.app'), isTrue);
      });
    });

    group('validatePinConfiguration', () {
      test('should detect placeholder certificate fingerprints', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value:
                  'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
              expiryDate: DateTime(2027, 1, 1),
            ),
          ],
        };

        final issues =
            CertificateRotationHelper.validatePinConfiguration(pins);
        expect(
          issues.any((issue) => issue.contains('CRITICAL')),
          isTrue,
        );
      });

      test('should detect pin values containing AAAA', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value:
                  'AAAA0000000000000000000000000000000000000000000000000000000000ff',
              expiryDate: DateTime(2099, 1, 1),
            ),
            // Add a second valid pin to avoid the backup-pin warning
            CertificatePin(
              type: PinType.sha256,
              value:
                  '1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff',
              expiryDate: DateTime(2099, 1, 1),
            ),
          ],
        };

        final issues =
            CertificateRotationHelper.validatePinConfiguration(pins);
        expect(
          issues.any((issue) => issue.contains('placeholder')),
          isTrue,
        );
      });

      test('should detect pin values containing REPLACE', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value:
                  'REPLACE_ME_00000000000000000000000000000000000000000000000000',
              expiryDate: DateTime(2099, 1, 1),
            ),
            CertificatePin(
              type: PinType.sha256,
              value:
                  '1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff',
              expiryDate: DateTime(2099, 1, 1),
            ),
          ],
        };

        final issues =
            CertificateRotationHelper.validatePinConfiguration(pins);
        expect(
          issues.any((issue) => issue.contains('placeholder')),
          isTrue,
        );
      });

      test('should warn when all pins for a domain are expired', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aabb' * 16,
              expiryDate: DateTime(2020, 1, 1),
            ),
          ],
        };

        final issues =
            CertificateRotationHelper.validatePinConfiguration(pins);
        expect(
          issues.any((issue) => issue.contains('expired')),
          isTrue,
        );
      });

      test('should warn when domain has fewer than 2 valid pins', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aabb' * 16,
              expiryDate: DateTime(2099, 12, 31),
            ),
          ],
        };

        final issues =
            CertificateRotationHelper.validatePinConfiguration(pins);
        expect(
          issues.any((issue) => issue.contains('at least 2 pins')),
          isTrue,
        );
      });

      test('should warn when domain has empty pins list', () {
        final pins = <String, List<CertificatePin>>{
          'empty.com': <CertificatePin>[],
        };

        final issues =
            CertificateRotationHelper.validatePinConfiguration(pins);
        expect(
          issues.any((issue) => issue.contains('no certificate pins')),
          isTrue,
        );
      });

      test('should return no issues for valid configuration', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value:
                  '1d40606fb292f95c55ca85debd7c7df339f260c9724640932cd96dfc89fdf877',
              expiryDate: DateTime(2099, 12, 31),
            ),
            CertificatePin(
              type: PinType.sha256,
              value:
                  'd2e91efcd39a87e0ef8c9744853c3dd47197b0c540fa448d04ca462613c96c9b',
              expiryDate: DateTime(2099, 12, 31),
            ),
          ],
        };

        final issues =
            CertificateRotationHelper.validatePinConfiguration(pins);
        expect(issues, isEmpty);
      });
    });

    group('getConfigurationStatus', () {
      test('should return formatted status containing domain names', () {
        final pins = <String, List<CertificatePin>>{
          'api.sahool.app': [
            CertificatePin(
              type: PinType.sha256,
              value:
                  '1d40606fb292f95c55ca85debd7c7df339f260c9724640932cd96dfc89fdf877',
              expiryDate: DateTime(2099, 12, 31),
              description: 'Primary cert',
            ),
            CertificatePin(
              type: PinType.sha256,
              value:
                  'd2e91efcd39a87e0ef8c9744853c3dd47197b0c540fa448d04ca462613c96c9b',
              expiryDate: DateTime(2099, 12, 31),
              description: 'Backup cert',
            ),
          ],
        };

        final status =
            CertificateRotationHelper.getConfigurationStatus(pins);

        expect(status, contains('Certificate Pin Configuration Status:'));
        expect(status, contains('api.sahool.app'));
        expect(status, contains('Total Pins: 2'));
        expect(status, contains('Valid Pins: 2'));
        expect(status, contains('Expired Pins: 0'));
        expect(status, contains('Primary cert'));
        expect(status, contains('Backup cert'));
      });

      test('should include validation issues in status output', () {
        final pins = <String, List<CertificatePin>>{
          'single-pin.com': [
            CertificatePin(
              type: PinType.sha256,
              value: 'aabb' * 16,
              expiryDate: DateTime(2099, 12, 31),
            ),
          ],
        };

        final status =
            CertificateRotationHelper.getConfigurationStatus(pins);

        expect(status, contains('Configuration Issues:'));
        expect(status, contains('at least 2 pins'));
      });

      test('should show truncated pin values', () {
        final pins = <String, List<CertificatePin>>{
          'test.com': [
            CertificatePin(
              type: PinType.sha256,
              value:
                  '1d40606fb292f95c55ca85debd7c7df339f260c9724640932cd96dfc89fdf877',
              expiryDate: DateTime(2099, 12, 31),
            ),
            CertificatePin(
              type: PinType.sha256,
              value:
                  'd2e91efcd39a87e0ef8c9744853c3dd47197b0c540fa448d04ca462613c96c9b',
              expiryDate: DateTime(2099, 12, 31),
            ),
          ],
        };

        final status =
            CertificateRotationHelper.getConfigurationStatus(pins);

        // Should show first 16 chars followed by ...
        expect(status, contains('1d40606fb292f95c...'));
      });
    });
  });

  group('CertificatePin', () {
    group('isExpired', () {
      test('should return true for a past expiry date', () {
        final pin = CertificatePin(
          type: PinType.sha256,
          value: 'aabb' * 16,
          expiryDate: DateTime(2020, 1, 1),
        );
        expect(pin.isExpired, isTrue);
      });

      test('should return false for a future expiry date', () {
        final pin = CertificatePin(
          type: PinType.sha256,
          value: 'aabb' * 16,
          expiryDate: DateTime(2099, 12, 31),
        );
        expect(pin.isExpired, isFalse);
      });

      test('should return false when expiryDate is null', () {
        final pin = CertificatePin(
          type: PinType.sha256,
          value: 'aabb' * 16,
        );
        expect(pin.isExpired, isFalse);
      });
    });

    group('daysUntilExpiry', () {
      test('should return null when expiryDate is null', () {
        final pin = CertificatePin(
          type: PinType.sha256,
          value: 'aabb' * 16,
        );
        expect(pin.daysUntilExpiry, isNull);
      });

      test('should return negative value for expired pin', () {
        final pin = CertificatePin(
          type: PinType.sha256,
          value: 'aabb' * 16,
          expiryDate: DateTime(2020, 1, 1),
        );
        expect(pin.daysUntilExpiry, isNegative);
      });

      test('should return positive value for future expiry', () {
        final pin = CertificatePin(
          type: PinType.sha256,
          value: 'aabb' * 16,
          expiryDate: DateTime(2099, 12, 31),
        );
        expect(pin.daysUntilExpiry, isPositive);
      });

      test('should approximate correct day count for known future date', () {
        final futureDate = DateTime.now().add(const Duration(days: 100));
        final pin = CertificatePin(
          type: PinType.sha256,
          value: 'aabb' * 16,
          expiryDate: futureDate,
        );
        // Allow +-1 day tolerance due to time-of-day rounding
        expect(pin.daysUntilExpiry, closeTo(100, 1));
      });
    });

    group('toString', () {
      test('should contain truncated value and type', () {
        final pin = CertificatePin(
          type: PinType.sha256,
          value:
              '1d40606fb292f95c55ca85debd7c7df339f260c9724640932cd96dfc89fdf877',
          expiryDate: DateTime(2027, 1, 1),
        );
        final str = pin.toString();
        expect(str, contains('sha256'));
        expect(str, contains('1d40606fb292f95c'));
        expect(str, contains('...'));
      });
    });
  });
}
