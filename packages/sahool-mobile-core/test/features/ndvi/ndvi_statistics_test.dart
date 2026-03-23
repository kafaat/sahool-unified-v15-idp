/// NDVI Statistics Tests - اختبارات إحصائيات NDVI
///
/// Comprehensive unit tests for:
/// - NdviStatistics calculations
/// - Trend analysis (improving, stable, declining)
/// - Historical NDVI trends
/// - Statistics from time series data
/// - Edge cases (empty data, single point)
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/ndvi/domain/ndvi_value.dart';
import 'package:sahool_field_app/features/analytics/domain/entities/field_history.dart'
    hide TrendDirection;
import 'package:sahool_field_app/features/analytics/domain/entities/field_history.dart'
    as fh show TrendDirection;

import 'ndvi_fixtures.dart';
import 'ndvi_mocks.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // NdviStatistics Tests - اختبارات إحصائيات NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviStatistics', () {
    group('constructor - المنشئ', () {
      test('should create with all required fields', () {
        // Arrange & Act
        final stats = NdviStatistics(
          current: 0.72,
          average: 0.65,
          min: 0.35,
          max: 0.85,
          trend: 0.08,
          history: [],
          lastUpdated: DateTime(2026, 1, 15),
        );

        // Assert
        expect(stats.current, equals(0.72));
        expect(stats.average, equals(0.65));
        expect(stats.min, equals(0.35));
        expect(stats.max, equals(0.85));
        expect(stats.trend, equals(0.08));
        expect(stats.history, isEmpty);
        expect(stats.lastUpdated, equals(DateTime(2026, 1, 15)));
      });
    });

    group('trendDirection - اتجاه الاتجاه', () {
      test('should return improving for trend > 0.05', () {
        // Arrange
        final stats = createMockStatistics(
          current: 0.72,
          average: 0.65,
          min: 0.35,
          max: 0.85,
          trend: 0.08,
        );

        // Assert
        expect(stats.trendDirection, equals(TrendDirection.improving));
      });

      test('should return declining for trend < -0.05', () {
        // Arrange
        final stats = createMockStatistics(
          current: 0.45,
          average: 0.55,
          min: 0.35,
          max: 0.75,
          trend: -0.10,
        );

        // Assert
        expect(stats.trendDirection, equals(TrendDirection.declining));
      });

      test('should return stable for trend between -0.05 and 0.05', () {
        // Arrange
        final stats = createMockStatistics(
          current: 0.65,
          average: 0.63,
          min: 0.55,
          max: 0.70,
          trend: 0.02,
        );

        // Assert
        expect(stats.trendDirection, equals(TrendDirection.stable));
      });

      test('should return stable for zero trend', () {
        // Arrange
        final stats = createMockStatistics(
          current: 0.65,
          average: 0.65,
          min: 0.55,
          max: 0.70,
          trend: 0.0,
        );

        // Assert
        expect(stats.trendDirection, equals(TrendDirection.stable));
      });

      test('should return stable for trend exactly at 0.05', () {
        // Arrange
        final stats = createMockStatistics(
          current: 0.65,
          average: 0.65,
          min: 0.55,
          max: 0.70,
          trend: 0.05,
        );

        // Assert
        expect(stats.trendDirection, equals(TrendDirection.stable));
      });

      test('should return improving for trend at 0.051', () {
        // Arrange
        final stats = createMockStatistics(
          current: 0.65,
          average: 0.65,
          min: 0.55,
          max: 0.70,
          trend: 0.051,
        );

        // Assert
        expect(stats.trendDirection, equals(TrendDirection.improving));
      });
    });

    group('currentCategory - الفئة الحالية', () {
      test('should return correct category for current value', () {
        // Arrange
        final stats = createMockStatistics(
          current: 0.72,
          average: 0.65,
          min: 0.35,
          max: 0.85,
          trend: 0.05,
        );

        // Assert
        expect(stats.currentCategory, equals(NdviHealthCategory.healthy));
      });

      test('should return veryHealthy for current >= 0.8', () {
        // Arrange
        final stats = createMockStatistics(
          current: 0.85,
          average: 0.75,
          min: 0.55,
          max: 0.90,
          trend: 0.08,
        );

        // Assert
        expect(stats.currentCategory, equals(NdviHealthCategory.veryHealthy));
      });

      test('should return stressed for current 0.2-0.4', () {
        // Arrange
        final stats = createMockStatistics(
          current: 0.28,
          average: 0.35,
          min: 0.20,
          max: 0.45,
          trend: -0.03,
        );

        // Assert
        expect(stats.currentCategory, equals(NdviHealthCategory.stressed));
      });
    });

    group('daysSinceUpdate - أيام منذ التحديث', () {
      test('should calculate days since last update', () {
        // Arrange
        final yesterday = DateTime.now().subtract(const Duration(days: 1));
        final stats = NdviStatistics(
          current: 0.65,
          average: 0.60,
          min: 0.50,
          max: 0.70,
          trend: 0.02,
          history: [],
          lastUpdated: yesterday,
        );

        // Assert
        expect(stats.daysSinceUpdate, equals(1));
      });

      test('should return 0 for today', () {
        // Arrange
        final stats = NdviStatistics(
          current: 0.65,
          average: 0.60,
          min: 0.50,
          max: 0.70,
          trend: 0.02,
          history: [],
          lastUpdated: DateTime.now(),
        );

        // Assert
        expect(stats.daysSinceUpdate, equals(0));
      });
    });

    group('fromHistory - من السجل', () {
      test('should create statistics from time series', () {
        // Arrange
        final history = createMockTimePoints(NdviFixtures.improvingTrendJson);

        // Act
        final stats = NdviStatistics.fromHistory(history);

        // Assert
        expect(stats.current, equals(0.72)); // Last value
        expect(stats.min, equals(0.35)); // First value
        expect(stats.max, equals(0.72)); // Last value (highest)
        expect(stats.history.length, equals(7));
      });

      test('should calculate average correctly', () {
        // Arrange
        final history = [
          NdviTimePoint(date: DateTime(2026, 1, 1), value: 0.4),
          NdviTimePoint(date: DateTime(2026, 1, 3), value: 0.5),
          NdviTimePoint(date: DateTime(2026, 1, 5), value: 0.6),
        ];

        // Act
        final stats = NdviStatistics.fromHistory(history);

        // Assert
        expect(stats.average, equals(0.5));
      });

      test('should calculate positive trend for improving values', () {
        // Arrange
        final history = createMockTimePoints(NdviFixtures.improvingTrendJson);

        // Act
        final stats = NdviStatistics.fromHistory(history);

        // Assert
        expect(stats.trend, greaterThan(0));
        expect(stats.trendDirection, equals(TrendDirection.improving));
      });

      test('should calculate negative trend for declining values', () {
        // Arrange
        final history = createMockTimePoints(NdviFixtures.decliningTrendJson);

        // Act
        final stats = NdviStatistics.fromHistory(history);

        // Assert
        expect(stats.trend, lessThan(0));
        expect(stats.trendDirection, equals(TrendDirection.declining));
      });

      test('should calculate near-zero trend for stable values', () {
        // Arrange
        final history = createMockTimePoints(NdviFixtures.stableTrendJson);

        // Act
        final stats = NdviStatistics.fromHistory(history);

        // Assert
        expect(stats.trend.abs(), lessThan(0.05));
        expect(stats.trendDirection, equals(TrendDirection.stable));
      });

      test('should handle empty history', () {
        // Arrange
        final history = <NdviTimePoint>[];

        // Act
        final stats = NdviStatistics.fromHistory(history);

        // Assert
        expect(stats.current, equals(0));
        expect(stats.average, equals(0));
        expect(stats.min, equals(0));
        expect(stats.max, equals(0));
        expect(stats.trend, equals(0));
        expect(stats.history, isEmpty);
      });

      test('should handle single point history', () {
        // Arrange
        final history = [
          NdviTimePoint(date: DateTime(2026, 1, 15), value: 0.65),
        ];

        // Act
        final stats = NdviStatistics.fromHistory(history);

        // Assert
        expect(stats.current, equals(0.65));
        expect(stats.average, equals(0.65));
        expect(stats.min, equals(0.65));
        expect(stats.max, equals(0.65));
        expect(stats.trend, equals(0)); // No trend with single point
      });

      test('should handle two points history', () {
        // Arrange
        final history = [
          NdviTimePoint(date: DateTime(2026, 1, 1), value: 0.5),
          NdviTimePoint(date: DateTime(2026, 1, 3), value: 0.7),
        ];

        // Act
        final stats = NdviStatistics.fromHistory(history);

        // Assert
        expect(stats.current, equals(0.7));
        expect(stats.min, equals(0.5));
        expect(stats.max, equals(0.7));
        expect(stats.trend, closeTo(0.2, 1e-10)); // (0.7 - 0.5) / 1
      });

      test('should sort history by date', () {
        // Arrange - Out of order
        final history = [
          NdviTimePoint(date: DateTime(2026, 1, 5), value: 0.6),
          NdviTimePoint(date: DateTime(2026, 1, 1), value: 0.4),
          NdviTimePoint(date: DateTime(2026, 1, 3), value: 0.5),
        ];

        // Act
        final stats = NdviStatistics.fromHistory(history);

        // Assert - History should be sorted, current should be latest
        expect(stats.current, equals(0.6));
        expect(stats.lastUpdated, equals(DateTime(2026, 1, 5)));
      });

      test('should clamp trend to -1.0 to 1.0', () {
        // Arrange - Extreme values
        final history = [
          NdviTimePoint(date: DateTime(2026, 1, 1), value: 0.0),
          NdviTimePoint(date: DateTime(2026, 1, 3), value: 1.0),
        ];

        // Act
        final stats = NdviStatistics.fromHistory(history);

        // Assert
        expect(stats.trend, lessThanOrEqualTo(1.0));
        expect(stats.trend, greaterThanOrEqualTo(-1.0));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviRecord Tests (from field_history.dart) - اختبارات سجل NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviRecord', () {
    group('constructor - المنشئ', () {
      test('should create with required fields', () {
        // Arrange & Act
        final record = NdviRecord(
          date: DateTime(2026, 1, 15),
          value: 0.72,
        );

        // Assert
        expect(record.date, equals(DateTime(2026, 1, 15)));
        expect(record.value, equals(0.72));
      });
    });

    group('isHealthy - هل صحي؟', () {
      test('should return true for NDVI >= 0.6', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.65);

        // Assert
        expect(record.isHealthy, isTrue);
      });

      test('should return false for NDVI < 0.6', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.55);

        // Assert
        expect(record.isHealthy, isFalse);
      });

      test('should return true for NDVI exactly 0.6', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.6);

        // Assert
        expect(record.isHealthy, isTrue);
      });
    });

    group('isCritical - هل حرج؟', () {
      test('should return true for NDVI < 0.3', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.25);

        // Assert
        expect(record.isCritical, isTrue);
      });

      test('should return false for NDVI >= 0.3', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.35);

        // Assert
        expect(record.isCritical, isFalse);
      });

      test('should return false for NDVI exactly 0.3', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.3);

        // Assert
        expect(record.isCritical, isFalse);
      });
    });

    group('level - المستوى', () {
      test('should return excellent for NDVI >= 0.7', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.75);

        // Assert
        expect(record.level, equals(NdviLevel.excellent));
      });

      test('should return good for NDVI 0.5-0.7', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.55);

        // Assert
        expect(record.level, equals(NdviLevel.good));
      });

      test('should return moderate for NDVI 0.3-0.5', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.35);

        // Assert
        expect(record.level, equals(NdviLevel.moderate));
      });

      test('should return poor for NDVI < 0.3', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.25);

        // Assert
        expect(record.level, equals(NdviLevel.poor));
      });
    });

    group('fromJson - من JSON', () {
      test('should parse from JSON', () {
        // Arrange
        final json = {
          'date': '2026-01-15T10:00:00Z',
          'value': 0.72,
        };

        // Act
        final record = NdviRecord.fromJson(json);

        // Assert
        expect(record.value, equals(0.72));
        expect(record.date, equals(DateTime.utc(2026, 1, 15, 10)));
      });
    });

    group('toJson - إلى JSON', () {
      test('should convert to JSON', () {
        // Arrange
        final record = NdviRecord(
          date: DateTime.utc(2026, 1, 15, 10),
          value: 0.72,
        );

        // Act
        final json = record.toJson();

        // Assert
        expect(json['value'], equals(0.72));
        expect(json['date'], contains('2026-01-15'));
      });
    });

    group('toString', () {
      test('should format correctly', () {
        // Arrange
        final record = NdviRecord(date: DateTime(2026, 1, 15), value: 0.72);

        // Act
        final str = record.toString();

        // Assert
        expect(str, contains('NdviRecord'));
        expect(str, contains('0.72'));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FieldAnalytics Tests - اختبارات تحليلات الحقل
  // ═══════════════════════════════════════════════════════════════════════════

  group('FieldAnalytics', () {
    group('isImproving - هل في تحسن؟', () {
      test('should return true when last value is higher than average of previous', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.4),
          NdviRecord(date: DateTime(2026, 1, 3), value: 0.5),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.7),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 4.5,
        );

        // Assert - Last (0.7) >= avg of previous (0.45)
        expect(analytics.isImproving, isTrue);
      });

      test('should return false when last value is lower than average', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.7),
          NdviRecord(date: DateTime(2026, 1, 3), value: 0.6),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.4),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 3.5,
        );

        // Assert - Last (0.4) < avg of previous (0.65)
        expect(analytics.isImproving, isFalse);
      });

      test('should return false for less than 2 records', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.5),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 4.0,
        );

        // Assert
        expect(analytics.isImproving, isFalse);
      });
    });

    group('changeRate - معدل التغير', () {
      test('should calculate positive change rate', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.5),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.6),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 4.0,
        );

        // Assert - (0.6 - 0.5) / 0.5 * 100 = 20%
        expect(analytics.changeRate, closeTo(20.0, 1e-10));
      });

      test('should calculate negative change rate', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.6),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.5),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 3.5,
        );

        // Assert - (0.5 - 0.6) / 0.6 * 100 = -16.67%
        expect(analytics.changeRate, closeTo(-16.67, 0.1));
      });

      test('should return 0 for less than 2 records', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.5),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 4.0,
        );

        // Assert
        expect(analytics.changeRate, equals(0));
      });

      test('should handle zero first value', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.0),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.5),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 4.0,
        );

        // Assert
        expect(analytics.changeRate, equals(0));
      });
    });

    group('averageNdvi - متوسط NDVI', () {
      test('should calculate average correctly', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.4),
          NdviRecord(date: DateTime(2026, 1, 3), value: 0.5),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.6),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 4.0,
        );

        // Assert
        expect(analytics.averageNdvi, equals(0.5));
      });

      test('should return 0 for empty history', () {
        // Arrange
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: [],
          yieldForecast: 0,
        );

        // Assert
        expect(analytics.averageNdvi, equals(0));
      });
    });

    group('peakRecord - أعلى سجل', () {
      test('should return record with highest value', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.5),
          NdviRecord(date: DateTime(2026, 1, 3), value: 0.8),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.6),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 4.5,
        );

        // Assert
        expect(analytics.peakRecord?.value, equals(0.8));
        expect(analytics.peakRecord?.date, equals(DateTime(2026, 1, 3)));
      });

      test('should return null for empty history', () {
        // Arrange
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: [],
          yieldForecast: 0,
        );

        // Assert
        expect(analytics.peakRecord, isNull);
      });
    });

    group('lowestRecord - أدنى سجل', () {
      test('should return record with lowest value', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.5),
          NdviRecord(date: DateTime(2026, 1, 3), value: 0.3),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.6),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 3.5,
        );

        // Assert
        expect(analytics.lowestRecord?.value, equals(0.3));
        expect(analytics.lowestRecord?.date, equals(DateTime(2026, 1, 3)));
      });

      test('should return null for empty history', () {
        // Arrange
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: [],
          yieldForecast: 0,
        );

        // Assert
        expect(analytics.lowestRecord, isNull);
      });
    });

    group('trend - الاتجاه', () {
      test('should return improving for changeRate > 5%', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.5),
          NdviRecord(date: DateTime(2026, 1, 3), value: 0.55),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.6),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 4.0,
        );

        // Assert - 20% change rate
        expect(analytics.trend, equals(fh.TrendDirection.improving));
      });

      test('should return declining for changeRate < -5%', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.6),
          NdviRecord(date: DateTime(2026, 1, 3), value: 0.55),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.5),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 3.5,
        );

        // Assert - -16.67% change rate
        expect(analytics.trend, equals(fh.TrendDirection.declining));
      });

      test('should return stable for changeRate between -5% and 5%', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.5),
          NdviRecord(date: DateTime(2026, 1, 3), value: 0.51),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.52),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 4.0,
        );

        // Assert - 4% change rate
        expect(analytics.trend, equals(fh.TrendDirection.stable));
      });

      test('should return stable for less than 3 records', () {
        // Arrange
        final history = [
          NdviRecord(date: DateTime(2026, 1, 1), value: 0.5),
          NdviRecord(date: DateTime(2026, 1, 5), value: 0.8),
        ];
        final analytics = FieldAnalytics(
          fieldId: 'field-001',
          history: history,
          yieldForecast: 4.0,
        );

        // Assert
        expect(analytics.trend, equals(fh.TrendDirection.stable));
      });
    });

    group('fromJson/toJson - من/إلى JSON', () {
      test('should round-trip correctly', () {
        // Arrange
        final original = FieldAnalytics(
          fieldId: 'field-001',
          history: [
            NdviRecord(date: DateTime(2026, 1, 1), value: 0.5),
            NdviRecord(date: DateTime(2026, 1, 3), value: 0.6),
          ],
          yieldForecast: 4.5,
          periodDays: 14,
        );

        // Act
        final json = original.toJson();
        final restored = FieldAnalytics.fromJson(json);

        // Assert
        expect(restored.fieldId, equals(original.fieldId));
        expect(restored.yieldForecast, equals(original.yieldForecast));
        expect(restored.periodDays, equals(original.periodDays));
        expect(restored.history.length, equals(original.history.length));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NdviLevel Tests - اختبارات مستوى NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  group('NdviLevel', () {
    test('should have correct values', () {
      expect(NdviLevel.values.length, equals(4));
      expect(NdviLevel.values, contains(NdviLevel.excellent));
      expect(NdviLevel.values, contains(NdviLevel.good));
      expect(NdviLevel.values, contains(NdviLevel.moderate));
      expect(NdviLevel.values, contains(NdviLevel.poor));
    });
  });
}
