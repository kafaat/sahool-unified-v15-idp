import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/gdd/providers/gdd_provider.dart';

void main() {
  // ===========================================================================
  // GDDRecordsParams
  // ===========================================================================
  group('GDDRecordsParams', () {
    group('construction', () {
      test('requires fieldId', () {
        const params = GDDRecordsParams(fieldId: 'field-001');
        expect(params.fieldId, 'field-001');
      });

      test('defaults limit to 100', () {
        const params = GDDRecordsParams(fieldId: 'f1');
        expect(params.limit, 100);
      });

      test('defaults startDate to null', () {
        const params = GDDRecordsParams(fieldId: 'f1');
        expect(params.startDate, isNull);
      });

      test('defaults endDate to null', () {
        const params = GDDRecordsParams(fieldId: 'f1');
        expect(params.endDate, isNull);
      });

      test('accepts all parameters', () {
        final start = DateTime(2025, 1, 1);
        final end = DateTime(2025, 6, 30);
        final params = GDDRecordsParams(
          fieldId: 'field-xyz',
          startDate: start,
          endDate: end,
          limit: 50,
        );
        expect(params.fieldId, 'field-xyz');
        expect(params.startDate, start);
        expect(params.endDate, end);
        expect(params.limit, 50);
      });
    });

    group('equality', () {
      test('equal when all fields match', () {
        final start = DateTime(2025, 3, 1);
        final end = DateTime(2025, 6, 30);
        final a = GDDRecordsParams(
          fieldId: 'f1',
          startDate: start,
          endDate: end,
          limit: 50,
        );
        final b = GDDRecordsParams(
          fieldId: 'f1',
          startDate: start,
          endDate: end,
          limit: 50,
        );
        expect(a, b);
      });

      test('equal when fieldId and defaults match', () {
        const a = GDDRecordsParams(fieldId: 'f1');
        const b = GDDRecordsParams(fieldId: 'f1');
        expect(a, b);
      });

      test('not equal when fieldId differs', () {
        const a = GDDRecordsParams(fieldId: 'f1');
        const b = GDDRecordsParams(fieldId: 'f2');
        expect(a, isNot(b));
      });

      test('not equal when startDate differs', () {
        final a = GDDRecordsParams(
          fieldId: 'f1',
          startDate: DateTime(2025, 1, 1),
        );
        final b = GDDRecordsParams(
          fieldId: 'f1',
          startDate: DateTime(2025, 2, 1),
        );
        expect(a, isNot(b));
      });

      test('not equal when endDate differs', () {
        final a = GDDRecordsParams(
          fieldId: 'f1',
          endDate: DateTime(2025, 6, 30),
        );
        final b = GDDRecordsParams(
          fieldId: 'f1',
          endDate: DateTime(2025, 7, 31),
        );
        expect(a, isNot(b));
      });

      test('not equal when limit differs', () {
        const a = GDDRecordsParams(fieldId: 'f1', limit: 50);
        const b = GDDRecordsParams(fieldId: 'f1', limit: 200);
        expect(a, isNot(b));
      });

      test('identical instance is equal to itself', () {
        const params = GDDRecordsParams(fieldId: 'f1');
        expect(params == params, isTrue);
      });

      test('not equal to a non-GDDRecordsParams object', () {
        const params = GDDRecordsParams(fieldId: 'f1');
        expect(params == 'string', isFalse);
      });

      test('not equal when one has startDate and other does not', () {
        const a = GDDRecordsParams(fieldId: 'f1');
        final b = GDDRecordsParams(
          fieldId: 'f1',
          startDate: DateTime(2025, 1, 1),
        );
        expect(a, isNot(b));
      });
    });

    group('hashCode', () {
      test('same for equal instances', () {
        const a = GDDRecordsParams(fieldId: 'f1', limit: 100);
        const b = GDDRecordsParams(fieldId: 'f1', limit: 100);
        expect(a.hashCode, b.hashCode);
      });

      test('same for equal instances with dates', () {
        final start = DateTime(2025, 3, 1);
        final a = GDDRecordsParams(fieldId: 'f1', startDate: start);
        final b = GDDRecordsParams(fieldId: 'f1', startDate: start);
        expect(a.hashCode, b.hashCode);
      });

      test('differs for different fieldId', () {
        const a = GDDRecordsParams(fieldId: 'aaa');
        const b = GDDRecordsParams(fieldId: 'bbb');
        expect(a.hashCode, isNot(b.hashCode));
      });

      test('differs for different limit', () {
        const a = GDDRecordsParams(fieldId: 'f1', limit: 10);
        const b = GDDRecordsParams(fieldId: 'f1', limit: 500);
        expect(a.hashCode, isNot(b.hashCode));
      });
    });
  });

  // ===========================================================================
  // GDDForecastParams
  // ===========================================================================
  group('GDDForecastParams', () {
    group('construction', () {
      test('requires fieldId', () {
        const params = GDDForecastParams(fieldId: 'field-abc');
        expect(params.fieldId, 'field-abc');
      });

      test('defaults days to 7', () {
        const params = GDDForecastParams(fieldId: 'f1');
        expect(params.days, 7);
      });

      test('accepts custom days', () {
        const params = GDDForecastParams(fieldId: 'f1', days: 14);
        expect(params.days, 14);
      });
    });

    group('equality', () {
      test('equal when fieldId and days match', () {
        const a = GDDForecastParams(fieldId: 'f1', days: 7);
        const b = GDDForecastParams(fieldId: 'f1', days: 7);
        expect(a, b);
      });

      test('equal with default days', () {
        const a = GDDForecastParams(fieldId: 'f1');
        const b = GDDForecastParams(fieldId: 'f1');
        expect(a, b);
      });

      test('not equal when fieldId differs', () {
        const a = GDDForecastParams(fieldId: 'f1');
        const b = GDDForecastParams(fieldId: 'f2');
        expect(a, isNot(b));
      });

      test('not equal when days differ', () {
        const a = GDDForecastParams(fieldId: 'f1', days: 7);
        const b = GDDForecastParams(fieldId: 'f1', days: 14);
        expect(a, isNot(b));
      });

      test('identical instance is equal to itself', () {
        const params = GDDForecastParams(fieldId: 'f1');
        expect(params == params, isTrue);
      });

      test('not equal to a non-GDDForecastParams object', () {
        const params = GDDForecastParams(fieldId: 'f1');
        expect(params == 42, isFalse);
      });

      test('not equal to GDDRecordsParams with same fieldId', () {
        const forecast = GDDForecastParams(fieldId: 'f1');
        const records = GDDRecordsParams(fieldId: 'f1');
        expect(forecast == records, isFalse);
      });
    });

    group('hashCode', () {
      test('same for equal instances', () {
        const a = GDDForecastParams(fieldId: 'f1', days: 7);
        const b = GDDForecastParams(fieldId: 'f1', days: 7);
        expect(a.hashCode, b.hashCode);
      });

      test('differs for different fieldId', () {
        const a = GDDForecastParams(fieldId: 'alpha');
        const b = GDDForecastParams(fieldId: 'beta');
        expect(a.hashCode, isNot(b.hashCode));
      });

      test('differs for different days', () {
        const a = GDDForecastParams(fieldId: 'f1', days: 3);
        const b = GDDForecastParams(fieldId: 'f1', days: 30);
        expect(a.hashCode, isNot(b.hashCode));
      });
    });
  });

  // ===========================================================================
  // GDDChartParams
  // ===========================================================================
  group('GDDChartParams', () {
    group('construction', () {
      test('requires fieldId', () {
        const params = GDDChartParams(fieldId: 'field-chart');
        expect(params.fieldId, 'field-chart');
      });

      test('defaults limit to 100', () {
        const params = GDDChartParams(fieldId: 'f1');
        expect(params.limit, 100);
      });

      test('defaults includeForecast to true', () {
        const params = GDDChartParams(fieldId: 'f1');
        expect(params.includeForecast, isTrue);
      });

      test('defaults forecastDays to 7', () {
        const params = GDDChartParams(fieldId: 'f1');
        expect(params.forecastDays, 7);
      });

      test('defaults includeStages to true', () {
        const params = GDDChartParams(fieldId: 'f1');
        expect(params.includeStages, isTrue);
      });

      test('defaults startDate to null', () {
        const params = GDDChartParams(fieldId: 'f1');
        expect(params.startDate, isNull);
      });

      test('defaults endDate to null', () {
        const params = GDDChartParams(fieldId: 'f1');
        expect(params.endDate, isNull);
      });

      test('accepts all parameters', () {
        final start = DateTime(2025, 1, 1);
        final end = DateTime(2025, 12, 31);
        final params = GDDChartParams(
          fieldId: 'f1',
          startDate: start,
          endDate: end,
          limit: 200,
          includeForecast: false,
          forecastDays: 14,
          includeStages: false,
        );
        expect(params.fieldId, 'f1');
        expect(params.startDate, start);
        expect(params.endDate, end);
        expect(params.limit, 200);
        expect(params.includeForecast, isFalse);
        expect(params.forecastDays, 14);
        expect(params.includeStages, isFalse);
      });
    });

    group('equality', () {
      test('equal when all fields match', () {
        final start = DateTime(2025, 1, 1);
        final a = GDDChartParams(
          fieldId: 'f1',
          startDate: start,
          limit: 50,
          includeForecast: false,
          forecastDays: 10,
          includeStages: false,
        );
        final b = GDDChartParams(
          fieldId: 'f1',
          startDate: start,
          limit: 50,
          includeForecast: false,
          forecastDays: 10,
          includeStages: false,
        );
        expect(a, b);
      });

      test('equal with defaults', () {
        const a = GDDChartParams(fieldId: 'f1');
        const b = GDDChartParams(fieldId: 'f1');
        expect(a, b);
      });

      test('not equal when fieldId differs', () {
        const a = GDDChartParams(fieldId: 'f1');
        const b = GDDChartParams(fieldId: 'f2');
        expect(a, isNot(b));
      });

      test('not equal when limit differs', () {
        const a = GDDChartParams(fieldId: 'f1', limit: 50);
        const b = GDDChartParams(fieldId: 'f1', limit: 200);
        expect(a, isNot(b));
      });

      test('not equal when includeForecast differs', () {
        const a = GDDChartParams(fieldId: 'f1', includeForecast: true);
        const b = GDDChartParams(fieldId: 'f1', includeForecast: false);
        expect(a, isNot(b));
      });

      test('not equal when forecastDays differs', () {
        const a = GDDChartParams(fieldId: 'f1', forecastDays: 7);
        const b = GDDChartParams(fieldId: 'f1', forecastDays: 14);
        expect(a, isNot(b));
      });

      test('not equal when includeStages differs', () {
        const a = GDDChartParams(fieldId: 'f1', includeStages: true);
        const b = GDDChartParams(fieldId: 'f1', includeStages: false);
        expect(a, isNot(b));
      });

      test('not equal when startDate differs', () {
        final a = GDDChartParams(
          fieldId: 'f1',
          startDate: DateTime(2025, 1, 1),
        );
        final b = GDDChartParams(
          fieldId: 'f1',
          startDate: DateTime(2025, 2, 1),
        );
        expect(a, isNot(b));
      });

      test('not equal when endDate differs', () {
        final a = GDDChartParams(
          fieldId: 'f1',
          endDate: DateTime(2025, 6, 30),
        );
        final b = GDDChartParams(
          fieldId: 'f1',
          endDate: DateTime(2025, 7, 31),
        );
        expect(a, isNot(b));
      });

      test('identical instance is equal to itself', () {
        const params = GDDChartParams(fieldId: 'f1');
        expect(params == params, isTrue);
      });

      test('not equal to a non-GDDChartParams object', () {
        const params = GDDChartParams(fieldId: 'f1');
        expect(params == 'string', isFalse);
      });
    });

    group('hashCode', () {
      test('same for equal instances', () {
        const a = GDDChartParams(fieldId: 'f1');
        const b = GDDChartParams(fieldId: 'f1');
        expect(a.hashCode, b.hashCode);
      });

      test('same for equal instances with all params', () {
        final start = DateTime(2025, 3, 1);
        final end = DateTime(2025, 9, 30);
        final a = GDDChartParams(
          fieldId: 'f1',
          startDate: start,
          endDate: end,
          limit: 75,
          includeForecast: true,
          forecastDays: 5,
          includeStages: false,
        );
        final b = GDDChartParams(
          fieldId: 'f1',
          startDate: start,
          endDate: end,
          limit: 75,
          includeForecast: true,
          forecastDays: 5,
          includeStages: false,
        );
        expect(a.hashCode, b.hashCode);
      });

      test('differs for different fieldId', () {
        const a = GDDChartParams(fieldId: 'alpha');
        const b = GDDChartParams(fieldId: 'beta');
        expect(a.hashCode, isNot(b.hashCode));
      });

      test('differs for different includeForecast', () {
        const a = GDDChartParams(fieldId: 'f1', includeForecast: true);
        const b = GDDChartParams(fieldId: 'f1', includeForecast: false);
        expect(a.hashCode, isNot(b.hashCode));
      });
    });
  });

  // ===========================================================================
  // GDDChartData
  // ===========================================================================
  group('GDDChartData', () {
    test('can be constructed with empty lists', () {
      const data = GDDChartData(
        records: [],
        forecasts: [],
        stages: [],
      );
      expect(data.records, isEmpty);
      expect(data.forecasts, isEmpty);
      expect(data.stages, isEmpty);
    });

    test('stores records list', () {
      const data = GDDChartData(
        records: [],
        forecasts: [],
        stages: [],
      );
      expect(data.records, isA<List>());
    });

    test('stores forecasts list', () {
      const data = GDDChartData(
        records: [],
        forecasts: [],
        stages: [],
      );
      expect(data.forecasts, isA<List>());
    });

    test('stores stages list', () {
      const data = GDDChartData(
        records: [],
        forecasts: [],
        stages: [],
      );
      expect(data.stages, isA<List>());
    });
  });

  // ===========================================================================
  // DateRange
  // ===========================================================================
  group('DateRange', () {
    group('construction', () {
      test('requires start and end', () {
        final range = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 12, 31),
        );
        expect(range.start, DateTime(2025, 1, 1));
        expect(range.end, DateTime(2025, 12, 31));
      });

      test('allows same start and end date', () {
        final date = DateTime(2025, 6, 15);
        final range = DateRange(start: date, end: date);
        expect(range.start, range.end);
      });

      test('allows end before start (no validation)', () {
        final range = DateRange(
          start: DateTime(2025, 12, 31),
          end: DateTime(2025, 1, 1),
        );
        expect(range.start.isAfter(range.end), isTrue);
      });
    });

    group('equality', () {
      test('equal when start and end match', () {
        final a = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 6, 30),
        );
        final b = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 6, 30),
        );
        expect(a, b);
      });

      test('not equal when start differs', () {
        final a = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 6, 30),
        );
        final b = DateRange(
          start: DateTime(2025, 2, 1),
          end: DateTime(2025, 6, 30),
        );
        expect(a, isNot(b));
      });

      test('not equal when end differs', () {
        final a = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 6, 30),
        );
        final b = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 7, 31),
        );
        expect(a, isNot(b));
      });

      test('identical instance is equal to itself', () {
        final range = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 12, 31),
        );
        expect(range == range, isTrue);
      });

      test('not equal to a non-DateRange object', () {
        final range = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 12, 31),
        );
        expect(range == 'string', isFalse);
      });

      test('not equal when both start and end differ', () {
        final a = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 3, 31),
        );
        final b = DateRange(
          start: DateTime(2025, 6, 1),
          end: DateTime(2025, 9, 30),
        );
        expect(a, isNot(b));
      });

      test('equal for same-day range', () {
        final date = DateTime(2025, 5, 20);
        final a = DateRange(start: date, end: date);
        final b = DateRange(start: date, end: date);
        expect(a, b);
      });
    });

    group('hashCode', () {
      test('same for equal instances', () {
        final a = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 6, 30),
        );
        final b = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 6, 30),
        );
        expect(a.hashCode, b.hashCode);
      });

      test('differs for different start', () {
        final a = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 12, 31),
        );
        final b = DateRange(
          start: DateTime(2025, 2, 1),
          end: DateTime(2025, 12, 31),
        );
        expect(a.hashCode, isNot(b.hashCode));
      });

      test('differs for different end', () {
        final a = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 6, 30),
        );
        final b = DateRange(
          start: DateTime(2025, 1, 1),
          end: DateTime(2025, 9, 30),
        );
        expect(a.hashCode, isNot(b.hashCode));
      });

      test('same for same-day range instances', () {
        final date = DateTime(2025, 8, 15);
        final a = DateRange(start: date, end: date);
        final b = DateRange(start: date, end: date);
        expect(a.hashCode, b.hashCode);
      });
    });
  });
}
