/// NDVI Value Tests - اختبارات قيمة NDVI
///
/// Comprehensive unit tests for:
/// - NdviValue value object
/// - NdviHealthCategory enum
/// - NdviTimePoint model
/// - NdviStatistics calculations
/// - TrendDirection enum
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile_core/features/ndvi/domain/ndvi_value.dart';

import 'ndvi_fixtures.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // NdviValue Tests - اختبارات كائن قيمة NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviValue', () {
    group('constructor - المنشئ', () {
      test('should create NdviValue with valid positive value', () {
        // Arrange & Act
        final ndvi = NdviValue(
          value: NdviFixtures.healthyNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.value, equals(NdviFixtures.healthyNdvi));
        expect(ndvi.capturedAt, equals(DateTime(2026, 1, 15)));
      });

      test('should create NdviValue with valid negative value (water)', () {
        // Arrange & Act
        final ndvi = NdviValue(
          value: NdviFixtures.waterNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.value, equals(NdviFixtures.waterNdvi));
      });

      test('should create NdviValue with source', () {
        // Arrange & Act
        final ndvi = NdviValue(
          value: 0.65,
          capturedAt: DateTime(2026, 1, 15),
          source: 'sentinel-2',
        );

        // Assert
        expect(ndvi.source, equals('sentinel-2'));
      });

      test('should create NdviValue at boundary -1.0', () {
        // Arrange & Act
        final ndvi = NdviValue(
          value: -1.0,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.value, equals(-1.0));
      });

      test('should create NdviValue at boundary 1.0', () {
        // Arrange & Act
        final ndvi = NdviValue(
          value: 1.0,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.value, equals(1.0));
      });

      test('should create NdviValue at boundary 0.0', () {
        // Arrange & Act
        final ndvi = NdviValue(
          value: 0.0,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.value, equals(0.0));
      });
    });

    group('category - تصنيف الفئة', () {
      test('should return nonVegetation for negative values', () {
        // Arrange
        final ndvi = NdviValue(
          value: NdviFixtures.waterNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.category, equals(NdviHealthCategory.nonVegetation));
      });

      test('should return bareSoil for values 0.0-0.2', () {
        // Arrange
        final ndvi = NdviValue(
          value: NdviFixtures.bareSoilNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.category, equals(NdviHealthCategory.bareSoil));
      });

      test('should return stressed for values 0.2-0.4', () {
        // Arrange
        final ndvi = NdviValue(
          value: NdviFixtures.stressedNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.category, equals(NdviHealthCategory.stressed));
      });

      test('should return moderate for values 0.4-0.6', () {
        // Arrange
        final ndvi = NdviValue(
          value: NdviFixtures.moderateNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.category, equals(NdviHealthCategory.moderate));
      });

      test('should return healthy for values 0.6-0.8', () {
        // Arrange
        final ndvi = NdviValue(
          value: NdviFixtures.healthyNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.category, equals(NdviHealthCategory.healthy));
      });

      test('should return veryHealthy for values 0.8-1.0', () {
        // Arrange
        final ndvi = NdviValue(
          value: NdviFixtures.veryHealthyNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.category, equals(NdviHealthCategory.veryHealthy));
      });

      test('should handle boundary value at 0.2 exactly', () {
        // Arrange - 0.2 should be stressed (0.2-0.4 range)
        final ndvi = NdviValue(
          value: 0.2,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.category, equals(NdviHealthCategory.stressed));
      });

      test('should handle value just below 0.2', () {
        // Arrange
        final ndvi = NdviValue(
          value: 0.199,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.category, equals(NdviHealthCategory.bareSoil));
      });
    });

    group('percentage - النسبة المئوية', () {
      test('should return 0% for -1.0', () {
        // Arrange
        final ndvi = NdviValue(
          value: -1.0,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.percentage, equals(0.0));
      });

      test('should return 50% for 0.0', () {
        // Arrange
        final ndvi = NdviValue(
          value: 0.0,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.percentage, equals(50.0));
      });

      test('should return 100% for 1.0', () {
        // Arrange
        final ndvi = NdviValue(
          value: 1.0,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.percentage, equals(100.0));
      });

      test('should return correct percentage for 0.5', () {
        // Arrange
        final ndvi = NdviValue(
          value: 0.5,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.percentage, equals(75.0));
      });
    });

    group('vegetationPercentage - نسبة النباتات', () {
      test('should return 0% for values below 0.2', () {
        // Arrange
        final ndvi = NdviValue(
          value: 0.1,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.vegetationPercentage, equals(0.0));
      });

      test('should return 100% for values above 0.8', () {
        // Arrange
        final ndvi = NdviValue(
          value: 0.9,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.vegetationPercentage, equals(100.0));
      });

      test('should return 50% for 0.5', () {
        // Arrange
        final ndvi = NdviValue(
          value: 0.5,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.vegetationPercentage, equals(50.0));
      });

      test('should return 0% for exactly 0.2', () {
        // Arrange
        final ndvi = NdviValue(
          value: 0.2,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.vegetationPercentage, equals(0.0));
      });

      test('should return 100% for exactly 0.8', () {
        // Arrange
        final ndvi = NdviValue(
          value: 0.8,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.vegetationPercentage, equals(100.0));
      });
    });

    group('color - اللون', () {
      test('should return color from category', () {
        // Arrange
        final ndvi = NdviValue(
          value: NdviFixtures.healthyNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.color, isA<Color>());
        expect(ndvi.color, equals(NdviHealthCategory.healthy.color));
      });
    });

    group('labels - التسميات', () {
      test('should return Arabic label', () {
        // Arrange
        final ndvi = NdviValue(
          value: NdviFixtures.healthyNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.labelAr, equals('صحي'));
      });

      test('should return English label', () {
        // Arrange
        final ndvi = NdviValue(
          value: NdviFixtures.healthyNdvi,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.labelEn, equals('Healthy'));
      });
    });

    group('toString', () {
      test('should return formatted string', () {
        // Arrange
        final ndvi = NdviValue(
          value: 0.72,
          capturedAt: DateTime(2026, 1, 15),
        );

        // Assert
        expect(ndvi.toString(), contains('NDVI'));
        expect(ndvi.toString(), contains('0.72'));
        expect(ndvi.toString(), contains('Healthy'));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviHealthCategory Tests - اختبارات فئات صحة NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviHealthCategory', () {
    group('values - القيم', () {
      test('should have correct min/max values for nonVegetation', () {
        expect(NdviHealthCategory.nonVegetation.minValue, equals(-1.0));
        expect(NdviHealthCategory.nonVegetation.maxValue, equals(0.0));
      });

      test('should have correct min/max values for bareSoil', () {
        expect(NdviHealthCategory.bareSoil.minValue, equals(0.0));
        expect(NdviHealthCategory.bareSoil.maxValue, equals(0.2));
      });

      test('should have correct min/max values for stressed', () {
        expect(NdviHealthCategory.stressed.minValue, equals(0.2));
        expect(NdviHealthCategory.stressed.maxValue, equals(0.4));
      });

      test('should have correct min/max values for moderate', () {
        expect(NdviHealthCategory.moderate.minValue, equals(0.4));
        expect(NdviHealthCategory.moderate.maxValue, equals(0.6));
      });

      test('should have correct min/max values for healthy', () {
        expect(NdviHealthCategory.healthy.minValue, equals(0.6));
        expect(NdviHealthCategory.healthy.maxValue, equals(0.8));
      });

      test('should have correct min/max values for veryHealthy', () {
        expect(NdviHealthCategory.veryHealthy.minValue, equals(0.8));
        expect(NdviHealthCategory.veryHealthy.maxValue, equals(1.0));
      });
    });

    group('labels - التسميات', () {
      test('all categories should have Arabic labels', () {
        for (final category in NdviHealthCategory.values) {
          expect(category.labelAr, isNotEmpty);
        }
      });

      test('all categories should have English labels', () {
        for (final category in NdviHealthCategory.values) {
          expect(category.labelEn, isNotEmpty);
        }
      });

      test('should have correct Arabic labels', () {
        expect(NdviHealthCategory.nonVegetation.labelAr, equals('غير نباتي'));
        expect(NdviHealthCategory.bareSoil.labelAr, equals('تربة جرداء'));
        expect(NdviHealthCategory.stressed.labelAr, equals('إجهاد'));
        expect(NdviHealthCategory.moderate.labelAr, equals('متوسط'));
        expect(NdviHealthCategory.healthy.labelAr, equals('صحي'));
        expect(NdviHealthCategory.veryHealthy.labelAr, equals('ممتاز'));
      });
    });

    group('colors - الألوان', () {
      test('all categories should have colors', () {
        for (final category in NdviHealthCategory.values) {
          expect(category.color, isA<Color>());
        }
      });

      test('should have distinct colors', () {
        final colors = NdviHealthCategory.values.map((c) => c.color).toSet();
        expect(colors.length, equals(NdviHealthCategory.values.length));
      });
    });

    group('icons - الأيقونات', () {
      test('all categories should have icons', () {
        for (final category in NdviHealthCategory.values) {
          expect(category.icon, isA<IconData>());
        }
      });
    });

    group('fromValue - من القيمة', () {
      test('should return correct category for each range', () {
        expect(
          NdviHealthCategory.fromValue(-0.5),
          equals(NdviHealthCategory.nonVegetation),
        );
        expect(
          NdviHealthCategory.fromValue(0.1),
          equals(NdviHealthCategory.bareSoil),
        );
        expect(
          NdviHealthCategory.fromValue(0.3),
          equals(NdviHealthCategory.stressed),
        );
        expect(
          NdviHealthCategory.fromValue(0.5),
          equals(NdviHealthCategory.moderate),
        );
        expect(
          NdviHealthCategory.fromValue(0.7),
          equals(NdviHealthCategory.healthy),
        );
        expect(
          NdviHealthCategory.fromValue(0.9),
          equals(NdviHealthCategory.veryHealthy),
        );
      });

      test('should handle boundary values correctly', () {
        expect(
          NdviHealthCategory.fromValue(-1.0),
          equals(NdviHealthCategory.nonVegetation),
        );
        expect(
          NdviHealthCategory.fromValue(0.0),
          equals(NdviHealthCategory.bareSoil),
        );
        expect(
          NdviHealthCategory.fromValue(0.2),
          equals(NdviHealthCategory.stressed),
        );
        expect(
          NdviHealthCategory.fromValue(0.4),
          equals(NdviHealthCategory.moderate),
        );
        expect(
          NdviHealthCategory.fromValue(0.6),
          equals(NdviHealthCategory.healthy),
        );
        expect(
          NdviHealthCategory.fromValue(0.8),
          equals(NdviHealthCategory.veryHealthy),
        );
        expect(
          NdviHealthCategory.fromValue(1.0),
          equals(NdviHealthCategory.veryHealthy),
        );
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviTimePoint Tests - اختبارات نقطة الوقت
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviTimePoint', () {
    test('should create with required fields', () {
      // Arrange & Act
      final point = NdviTimePoint(
        date: DateTime(2026, 1, 15),
        value: 0.65,
      );

      // Assert
      expect(point.date, equals(DateTime(2026, 1, 15)));
      expect(point.value, equals(0.65));
      expect(point.cloudCover, isNull);
    });

    test('should create with cloud cover', () {
      // Arrange & Act
      final point = NdviTimePoint(
        date: DateTime(2026, 1, 15),
        value: 0.65,
        cloudCover: 15.0,
      );

      // Assert
      expect(point.cloudCover, equals(15.0));
    });

    test('toNdviValue should convert correctly', () {
      // Arrange
      final point = NdviTimePoint(
        date: DateTime(2026, 1, 15),
        value: 0.65,
      );

      // Act
      final ndviValue = point.toNdviValue();

      // Assert
      expect(ndviValue.value, equals(0.65));
      expect(ndviValue.capturedAt, equals(DateTime(2026, 1, 15)));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // TrendDirection Tests - اختبارات اتجاه الاتجاه
  // ═══════════════════════════════════════════════════════════════════════════

  group('TrendDirection', () {
    test('should have correct labels', () {
      expect(TrendDirection.improving.labelAr, equals('تحسن'));
      expect(TrendDirection.improving.labelEn, equals('Improving'));

      expect(TrendDirection.stable.labelAr, equals('مستقر'));
      expect(TrendDirection.stable.labelEn, equals('Stable'));

      expect(TrendDirection.declining.labelAr, equals('تراجع'));
      expect(TrendDirection.declining.labelEn, equals('Declining'));
    });

    test('should have icons', () {
      expect(TrendDirection.improving.icon, equals(Icons.trending_up));
      expect(TrendDirection.stable.icon, equals(Icons.trending_flat));
      expect(TrendDirection.declining.icon, equals(Icons.trending_down));
    });

    test('should have colors', () {
      expect(TrendDirection.improving.color, isA<Color>());
      expect(TrendDirection.stable.color, isA<Color>());
      expect(TrendDirection.declining.color, isA<Color>());
    });
  });
}
