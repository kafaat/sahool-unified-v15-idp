import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/ndvi/domain/ndvi_value.dart';

void main() {
  group('NdviValue', () {
    test('category returns nonVegetation for negative values', () {
      final v = NdviValue(value: -0.5, capturedAt: DateTime(2026, 1, 1));
      expect(v.category, NdviHealthCategory.nonVegetation);
    });

    test('category returns bareSoil for 0.0-0.2', () {
      final v = NdviValue(value: 0.1, capturedAt: DateTime(2026, 1, 1));
      expect(v.category, NdviHealthCategory.bareSoil);
    });

    test('category returns stressed for 0.2-0.4', () {
      final v = NdviValue(value: 0.3, capturedAt: DateTime(2026, 1, 1));
      expect(v.category, NdviHealthCategory.stressed);
    });

    test('category returns moderate for 0.4-0.6', () {
      final v = NdviValue(value: 0.5, capturedAt: DateTime(2026, 1, 1));
      expect(v.category, NdviHealthCategory.moderate);
    });

    test('category returns healthy for 0.6-0.8', () {
      final v = NdviValue(value: 0.7, capturedAt: DateTime(2026, 1, 1));
      expect(v.category, NdviHealthCategory.healthy);
    });

    test('category returns veryHealthy for >= 0.8', () {
      final v = NdviValue(value: 0.9, capturedAt: DateTime(2026, 1, 1));
      expect(v.category, NdviHealthCategory.veryHealthy);
    });

    test('percentage converts NDVI range to 0-100', () {
      final v0 = NdviValue(value: 0.0, capturedAt: DateTime(2026, 1, 1));
      expect(v0.percentage, 50.0);

      final vMax = NdviValue(value: 1.0, capturedAt: DateTime(2026, 1, 1));
      expect(vMax.percentage, 100.0);

      final vMin = NdviValue(value: -1.0, capturedAt: DateTime(2026, 1, 1));
      expect(vMin.percentage, 0.0);
    });

    test('vegetationPercentage normalizes 0.2-0.8 to 0-100', () {
      final low = NdviValue(value: 0.1, capturedAt: DateTime(2026, 1, 1));
      expect(low.vegetationPercentage, 0);

      final mid = NdviValue(value: 0.5, capturedAt: DateTime(2026, 1, 1));
      expect(mid.vegetationPercentage, 50.0);

      final high = NdviValue(value: 0.8, capturedAt: DateTime(2026, 1, 1));
      expect(high.vegetationPercentage, closeTo(100.0, 0.01));

      final over = NdviValue(value: 0.9, capturedAt: DateTime(2026, 1, 1));
      expect(over.vegetationPercentage, 100);
    });

    test('toString includes value and category label', () {
      final v = NdviValue(value: 0.65, capturedAt: DateTime(2026, 1, 1));
      expect(v.toString(), contains('0.65'));
      expect(v.toString(), contains('Healthy'));
    });
  });

  group('NdviHealthCategory', () {
    test('fromValue classifies correctly', () {
      expect(NdviHealthCategory.fromValue(-0.3), NdviHealthCategory.nonVegetation);
      expect(NdviHealthCategory.fromValue(0.15), NdviHealthCategory.bareSoil);
      expect(NdviHealthCategory.fromValue(0.35), NdviHealthCategory.stressed);
      expect(NdviHealthCategory.fromValue(0.55), NdviHealthCategory.moderate);
      expect(NdviHealthCategory.fromValue(0.75), NdviHealthCategory.healthy);
      expect(NdviHealthCategory.fromValue(0.95), NdviHealthCategory.veryHealthy);
    });

    test('has bilingual labels', () {
      expect(NdviHealthCategory.healthy.labelAr, 'صحي');
      expect(NdviHealthCategory.healthy.labelEn, 'Healthy');
      expect(NdviHealthCategory.veryHealthy.labelAr, 'ممتاز');
      expect(NdviHealthCategory.stressed.labelAr, 'إجهاد');
    });

    test('has 6 categories', () {
      expect(NdviHealthCategory.values, hasLength(6));
    });
  });

  group('NdviStatistics', () {
    test('fromHistory computes correct statistics', () {
      final history = [
        NdviTimePoint(date: DateTime(2026, 1, 1), value: 0.4),
        NdviTimePoint(date: DateTime(2026, 1, 15), value: 0.5),
        NdviTimePoint(date: DateTime(2026, 2, 1), value: 0.6),
        NdviTimePoint(date: DateTime(2026, 2, 15), value: 0.7),
      ];

      final stats = NdviStatistics.fromHistory(history);

      expect(stats.current, 0.7);
      expect(stats.min, 0.4);
      expect(stats.max, 0.7);
      expect(stats.average, 0.55);
      expect(stats.trend, greaterThan(0));
    });

    test('fromHistory handles empty list', () {
      final stats = NdviStatistics.fromHistory([]);
      expect(stats.current, 0);
      expect(stats.average, 0);
      expect(stats.min, 0);
      expect(stats.max, 0);
      expect(stats.trend, 0);
      expect(stats.history, isEmpty);
    });

    test('trendDirection returns improving for positive trend', () {
      final stats = NdviStatistics(
        current: 0.7,
        average: 0.5,
        min: 0.3,
        max: 0.7,
        trend: 0.1,
        history: [],
        lastUpdated: DateTime(2026, 1, 1),
      );
      expect(stats.trendDirection, TrendDirection.improving);
    });

    test('trendDirection returns stable for small trend', () {
      final stats = NdviStatistics(
        current: 0.5,
        average: 0.5,
        min: 0.48,
        max: 0.52,
        trend: 0.02,
        history: [],
        lastUpdated: DateTime(2026, 1, 1),
      );
      expect(stats.trendDirection, TrendDirection.stable);
    });

    test('trendDirection returns declining for negative trend', () {
      final stats = NdviStatistics(
        current: 0.3,
        average: 0.5,
        min: 0.3,
        max: 0.7,
        trend: -0.1,
        history: [],
        lastUpdated: DateTime(2026, 1, 1),
      );
      expect(stats.trendDirection, TrendDirection.declining);
    });

    test('currentCategory matches current value', () {
      final stats = NdviStatistics(
        current: 0.72,
        average: 0.6,
        min: 0.4,
        max: 0.8,
        trend: 0.05,
        history: [],
        lastUpdated: DateTime(2026, 1, 1),
      );
      expect(stats.currentCategory, NdviHealthCategory.healthy);
    });
  });

  group('TrendDirection', () {
    test('has bilingual labels', () {
      expect(TrendDirection.improving.labelAr, 'تحسن');
      expect(TrendDirection.stable.labelAr, 'مستقر');
      expect(TrendDirection.declining.labelAr, 'تراجع');
    });
  });
}
