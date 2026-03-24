import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/spray/models/spray_models.dart';
import 'package:sahool_field_app/features/spray/providers/spray_provider.dart';

void main() {
  // ===========================================================================
  // SprayRecommendationFilter
  // ===========================================================================
  group('SprayRecommendationFilter', () {
    group('construction', () {
      test('default constructor has all null fields', () {
        const filter = SprayRecommendationFilter();
        expect(filter.fieldId, isNull);
        expect(filter.sprayType, isNull);
        expect(filter.status, isNull);
        expect(filter.startDate, isNull);
        expect(filter.endDate, isNull);
      });

      test('constructor accepts all parameters', () {
        final now = DateTime(2025, 6, 1);
        final later = DateTime(2025, 6, 30);
        final filter = SprayRecommendationFilter(
          fieldId: 'field-1',
          sprayType: SprayType.herbicide,
          status: RecommendationStatus.active,
          startDate: now,
          endDate: later,
        );
        expect(filter.fieldId, 'field-1');
        expect(filter.sprayType, SprayType.herbicide);
        expect(filter.status, RecommendationStatus.active);
        expect(filter.startDate, now);
        expect(filter.endDate, later);
      });
    });

    group('hasFilters', () {
      test('returns false when all fields are null', () {
        const filter = SprayRecommendationFilter();
        expect(filter.hasFilters, isFalse);
      });

      test('returns true when fieldId is set', () {
        const filter = SprayRecommendationFilter(fieldId: 'f1');
        expect(filter.hasFilters, isTrue);
      });

      test('returns true when sprayType is set', () {
        const filter = SprayRecommendationFilter(
          sprayType: SprayType.fungicide,
        );
        expect(filter.hasFilters, isTrue);
      });

      test('returns true when status is set', () {
        const filter = SprayRecommendationFilter(
          status: RecommendationStatus.completed,
        );
        expect(filter.hasFilters, isTrue);
      });

      test('returns true when startDate is set', () {
        final filter = SprayRecommendationFilter(
          startDate: DateTime(2025, 1, 1),
        );
        expect(filter.hasFilters, isTrue);
      });

      test('returns true when endDate is set', () {
        final filter = SprayRecommendationFilter(
          endDate: DateTime(2025, 12, 31),
        );
        expect(filter.hasFilters, isTrue);
      });

      test('returns true when multiple fields are set', () {
        const filter = SprayRecommendationFilter(
          fieldId: 'f1',
          sprayType: SprayType.insecticide,
        );
        expect(filter.hasFilters, isTrue);
      });
    });

    group('copyWith', () {
      test('updates fieldId', () {
        const original = SprayRecommendationFilter(fieldId: 'old');
        final copy = original.copyWith(fieldId: 'new');
        expect(copy.fieldId, 'new');
      });

      test('updates sprayType', () {
        const original = SprayRecommendationFilter();
        final copy = original.copyWith(sprayType: SprayType.foliar);
        expect(copy.sprayType, SprayType.foliar);
      });

      test('updates status', () {
        const original = SprayRecommendationFilter();
        final copy = original.copyWith(status: RecommendationStatus.expired);
        expect(copy.status, RecommendationStatus.expired);
      });

      test('updates startDate', () {
        final date = DateTime(2025, 3, 1);
        const original = SprayRecommendationFilter();
        final copy = original.copyWith(startDate: date);
        expect(copy.startDate, date);
      });

      test('updates endDate', () {
        final date = DateTime(2025, 6, 30);
        const original = SprayRecommendationFilter();
        final copy = original.copyWith(endDate: date);
        expect(copy.endDate, date);
      });

      test('preserves existing values when updating one field', () {
        const original = SprayRecommendationFilter(
          fieldId: 'f1',
          sprayType: SprayType.herbicide,
        );
        final copy = original.copyWith(status: RecommendationStatus.active);
        expect(copy.fieldId, 'f1');
        expect(copy.sprayType, SprayType.herbicide);
        expect(copy.status, RecommendationStatus.active);
      });

      test('clearFieldId sets fieldId to null', () {
        const original = SprayRecommendationFilter(fieldId: 'f1');
        final copy = original.copyWith(clearFieldId: true);
        expect(copy.fieldId, isNull);
      });

      test('clearSprayType sets sprayType to null', () {
        const original = SprayRecommendationFilter(
          sprayType: SprayType.fungicide,
        );
        final copy = original.copyWith(clearSprayType: true);
        expect(copy.sprayType, isNull);
      });

      test('clearStatus sets status to null', () {
        const original = SprayRecommendationFilter(
          status: RecommendationStatus.active,
        );
        final copy = original.copyWith(clearStatus: true);
        expect(copy.status, isNull);
      });

      test('clearStartDate sets startDate to null', () {
        final original = SprayRecommendationFilter(
          startDate: DateTime(2025, 1, 1),
        );
        final copy = original.copyWith(clearStartDate: true);
        expect(copy.startDate, isNull);
      });

      test('clearEndDate sets endDate to null', () {
        final original = SprayRecommendationFilter(
          endDate: DateTime(2025, 12, 31),
        );
        final copy = original.copyWith(clearEndDate: true);
        expect(copy.endDate, isNull);
      });

      test('clear flag takes precedence over new value', () {
        const original = SprayRecommendationFilter(fieldId: 'old');
        final copy = original.copyWith(
          fieldId: 'new',
          clearFieldId: true,
        );
        expect(copy.fieldId, isNull);
      });

      test('clearing all fields results in hasFilters false', () {
        final original = SprayRecommendationFilter(
          fieldId: 'f1',
          sprayType: SprayType.herbicide,
          status: RecommendationStatus.active,
          startDate: DateTime(2025, 1, 1),
          endDate: DateTime(2025, 12, 31),
        );
        final copy = original.copyWith(
          clearFieldId: true,
          clearSprayType: true,
          clearStatus: true,
          clearStartDate: true,
          clearEndDate: true,
        );
        expect(copy.hasFilters, isFalse);
      });

      test('copyWith with no arguments preserves all values', () {
        final original = SprayRecommendationFilter(
          fieldId: 'f1',
          sprayType: SprayType.insecticide,
          status: RecommendationStatus.completed,
          startDate: DateTime(2025, 1, 1),
          endDate: DateTime(2025, 6, 30),
        );
        final copy = original.copyWith();
        expect(copy.fieldId, original.fieldId);
        expect(copy.sprayType, original.sprayType);
        expect(copy.status, original.status);
        expect(copy.startDate, original.startDate);
        expect(copy.endDate, original.endDate);
      });
    });
  });

  // ===========================================================================
  // SprayWindowParams
  // ===========================================================================
  group('SprayWindowParams', () {
    group('construction', () {
      test('requires fieldId', () {
        const params = SprayWindowParams(fieldId: 'f1');
        expect(params.fieldId, 'f1');
      });

      test('defaults days to 7', () {
        const params = SprayWindowParams(fieldId: 'f1');
        expect(params.days, 7);
      });

      test('accepts custom days', () {
        const params = SprayWindowParams(fieldId: 'f1', days: 14);
        expect(params.days, 14);
      });
    });

    group('equality', () {
      test('equal when fieldId and days match', () {
        const a = SprayWindowParams(fieldId: 'f1', days: 7);
        const b = SprayWindowParams(fieldId: 'f1', days: 7);
        expect(a, b);
      });

      test('not equal when fieldId differs', () {
        const a = SprayWindowParams(fieldId: 'f1');
        const b = SprayWindowParams(fieldId: 'f2');
        expect(a, isNot(b));
      });

      test('not equal when days differ', () {
        const a = SprayWindowParams(fieldId: 'f1', days: 7);
        const b = SprayWindowParams(fieldId: 'f1', days: 14);
        expect(a, isNot(b));
      });

      test('identical instance is equal to itself', () {
        const params = SprayWindowParams(fieldId: 'f1');
        expect(params == params, isTrue);
      });

      test('not equal to a non-SprayWindowParams object', () {
        const params = SprayWindowParams(fieldId: 'f1');
        expect(params == 'string', isFalse);
      });
    });

    group('hashCode', () {
      test('same for equal instances', () {
        const a = SprayWindowParams(fieldId: 'f1', days: 7);
        const b = SprayWindowParams(fieldId: 'f1', days: 7);
        expect(a.hashCode, b.hashCode);
      });

      test('differs for instances with different fieldId', () {
        const a = SprayWindowParams(fieldId: 'f1');
        const b = SprayWindowParams(fieldId: 'f2');
        expect(a.hashCode, isNot(b.hashCode));
      });

      test('differs for instances with different days', () {
        const a = SprayWindowParams(fieldId: 'f1', days: 3);
        const b = SprayWindowParams(fieldId: 'f1', days: 10);
        expect(a.hashCode, isNot(b.hashCode));
      });
    });
  });

  // ===========================================================================
  // WeatherForecastParams
  // ===========================================================================
  group('WeatherForecastParams', () {
    group('construction', () {
      test('requires fieldId', () {
        const params = WeatherForecastParams(fieldId: 'field-abc');
        expect(params.fieldId, 'field-abc');
      });

      test('defaults days to 7', () {
        const params = WeatherForecastParams(fieldId: 'f1');
        expect(params.days, 7);
      });

      test('accepts custom days', () {
        const params = WeatherForecastParams(fieldId: 'f1', days: 3);
        expect(params.days, 3);
      });
    });

    group('equality', () {
      test('equal when fieldId and days match', () {
        const a = WeatherForecastParams(fieldId: 'f1', days: 5);
        const b = WeatherForecastParams(fieldId: 'f1', days: 5);
        expect(a, b);
      });

      test('not equal when fieldId differs', () {
        const a = WeatherForecastParams(fieldId: 'f1');
        const b = WeatherForecastParams(fieldId: 'f2');
        expect(a, isNot(b));
      });

      test('not equal when days differ', () {
        const a = WeatherForecastParams(fieldId: 'f1', days: 7);
        const b = WeatherForecastParams(fieldId: 'f1', days: 10);
        expect(a, isNot(b));
      });

      test('identical instance is equal to itself', () {
        const params = WeatherForecastParams(fieldId: 'f1');
        expect(params == params, isTrue);
      });

      test('not equal to a non-WeatherForecastParams object', () {
        const params = WeatherForecastParams(fieldId: 'f1');
        expect(params == 42, isFalse);
      });
    });

    group('hashCode', () {
      test('same for equal instances', () {
        const a = WeatherForecastParams(fieldId: 'f1', days: 7);
        const b = WeatherForecastParams(fieldId: 'f1', days: 7);
        expect(a.hashCode, b.hashCode);
      });

      test('differs for different fieldId', () {
        const a = WeatherForecastParams(fieldId: 'aaa');
        const b = WeatherForecastParams(fieldId: 'bbb');
        expect(a.hashCode, isNot(b.hashCode));
      });

      test('differs for different days', () {
        const a = WeatherForecastParams(fieldId: 'f1', days: 1);
        const b = WeatherForecastParams(fieldId: 'f1', days: 30);
        expect(a.hashCode, isNot(b.hashCode));
      });
    });
  });

  // ===========================================================================
  // SprayProductFilter
  // ===========================================================================
  group('SprayProductFilter', () {
    group('construction', () {
      test('default constructor has null optional fields and false boolean', () {
        const filter = SprayProductFilter();
        expect(filter.sprayType, isNull);
        expect(filter.yemenProductsOnly, isFalse);
        expect(filter.search, isNull);
      });

      test('accepts all parameters', () {
        const filter = SprayProductFilter(
          sprayType: SprayType.fungicide,
          yemenProductsOnly: true,
          search: 'roundup',
        );
        expect(filter.sprayType, SprayType.fungicide);
        expect(filter.yemenProductsOnly, isTrue);
        expect(filter.search, 'roundup');
      });
    });

    group('copyWith', () {
      test('updates sprayType', () {
        const original = SprayProductFilter();
        final copy = original.copyWith(sprayType: SprayType.insecticide);
        expect(copy.sprayType, SprayType.insecticide);
      });

      test('updates yemenProductsOnly', () {
        const original = SprayProductFilter();
        final copy = original.copyWith(yemenProductsOnly: true);
        expect(copy.yemenProductsOnly, isTrue);
      });

      test('updates search', () {
        const original = SprayProductFilter();
        final copy = original.copyWith(search: 'glyphosate');
        expect(copy.search, 'glyphosate');
      });

      test('clearSprayType sets sprayType to null', () {
        const original = SprayProductFilter(
          sprayType: SprayType.herbicide,
        );
        final copy = original.copyWith(clearSprayType: true);
        expect(copy.sprayType, isNull);
      });

      test('clearSearch sets search to null', () {
        const original = SprayProductFilter(search: 'test');
        final copy = original.copyWith(clearSearch: true);
        expect(copy.search, isNull);
      });

      test('clear flag takes precedence over new value for sprayType', () {
        const original = SprayProductFilter(
          sprayType: SprayType.herbicide,
        );
        final copy = original.copyWith(
          sprayType: SprayType.foliar,
          clearSprayType: true,
        );
        expect(copy.sprayType, isNull);
      });

      test('clear flag takes precedence over new value for search', () {
        const original = SprayProductFilter(search: 'old');
        final copy = original.copyWith(
          search: 'new',
          clearSearch: true,
        );
        expect(copy.search, isNull);
      });

      test('preserves existing values when updating one field', () {
        const original = SprayProductFilter(
          sprayType: SprayType.fungicide,
          yemenProductsOnly: true,
          search: 'copper',
        );
        final copy = original.copyWith(yemenProductsOnly: false);
        expect(copy.sprayType, SprayType.fungicide);
        expect(copy.yemenProductsOnly, isFalse);
        expect(copy.search, 'copper');
      });

      test('copyWith with no arguments preserves all values', () {
        const original = SprayProductFilter(
          sprayType: SprayType.insecticide,
          yemenProductsOnly: true,
          search: 'neem',
        );
        final copy = original.copyWith();
        expect(copy.sprayType, original.sprayType);
        expect(copy.yemenProductsOnly, original.yemenProductsOnly);
        expect(copy.search, original.search);
      });
    });

    group('equality', () {
      test('equal when all fields match', () {
        const a = SprayProductFilter(
          sprayType: SprayType.herbicide,
          yemenProductsOnly: true,
          search: 'test',
        );
        const b = SprayProductFilter(
          sprayType: SprayType.herbicide,
          yemenProductsOnly: true,
          search: 'test',
        );
        expect(a, b);
      });

      test('not equal when sprayType differs', () {
        const a = SprayProductFilter(sprayType: SprayType.herbicide);
        const b = SprayProductFilter(sprayType: SprayType.fungicide);
        expect(a, isNot(b));
      });

      test('not equal when yemenProductsOnly differs', () {
        const a = SprayProductFilter(yemenProductsOnly: true);
        const b = SprayProductFilter(yemenProductsOnly: false);
        expect(a, isNot(b));
      });

      test('not equal when search differs', () {
        const a = SprayProductFilter(search: 'abc');
        const b = SprayProductFilter(search: 'xyz');
        expect(a, isNot(b));
      });

      test('identical instance is equal to itself', () {
        const filter = SprayProductFilter(search: 'x');
        expect(filter == filter, isTrue);
      });

      test('not equal to a non-SprayProductFilter object', () {
        const filter = SprayProductFilter();
        expect(filter == 'string', isFalse);
      });

      test('equal for two default instances', () {
        const a = SprayProductFilter();
        const b = SprayProductFilter();
        expect(a, b);
      });
    });

    group('hashCode', () {
      test('same for equal instances', () {
        const a = SprayProductFilter(
          sprayType: SprayType.foliar,
          yemenProductsOnly: false,
          search: 'urea',
        );
        const b = SprayProductFilter(
          sprayType: SprayType.foliar,
          yemenProductsOnly: false,
          search: 'urea',
        );
        expect(a.hashCode, b.hashCode);
      });

      test('differs for different sprayType', () {
        const a = SprayProductFilter(sprayType: SprayType.herbicide);
        const b = SprayProductFilter(sprayType: SprayType.insecticide);
        expect(a.hashCode, isNot(b.hashCode));
      });

      test('same for two default instances', () {
        const a = SprayProductFilter();
        const b = SprayProductFilter();
        expect(a.hashCode, b.hashCode);
      });
    });
  });

  // ===========================================================================
  // SprayLogFilter
  // ===========================================================================
  group('SprayLogFilter', () {
    group('construction', () {
      test('default constructor has all null fields', () {
        const filter = SprayLogFilter();
        expect(filter.fieldId, isNull);
        expect(filter.sprayType, isNull);
        expect(filter.startDate, isNull);
        expect(filter.endDate, isNull);
      });

      test('accepts all parameters', () {
        final start = DateTime(2025, 1, 1);
        final end = DateTime(2025, 6, 30);
        final filter = SprayLogFilter(
          fieldId: 'field-abc',
          sprayType: SprayType.fungicide,
          startDate: start,
          endDate: end,
        );
        expect(filter.fieldId, 'field-abc');
        expect(filter.sprayType, SprayType.fungicide);
        expect(filter.startDate, start);
        expect(filter.endDate, end);
      });
    });

    group('hasFilters', () {
      test('returns false when all fields are null', () {
        const filter = SprayLogFilter();
        expect(filter.hasFilters, isFalse);
      });

      test('returns true when fieldId is set', () {
        const filter = SprayLogFilter(fieldId: 'f1');
        expect(filter.hasFilters, isTrue);
      });

      test('returns true when sprayType is set', () {
        const filter = SprayLogFilter(sprayType: SprayType.herbicide);
        expect(filter.hasFilters, isTrue);
      });

      test('returns true when startDate is set', () {
        final filter = SprayLogFilter(startDate: DateTime(2025, 3, 1));
        expect(filter.hasFilters, isTrue);
      });

      test('returns true when endDate is set', () {
        final filter = SprayLogFilter(endDate: DateTime(2025, 9, 1));
        expect(filter.hasFilters, isTrue);
      });

      test('returns true when all fields are set', () {
        final filter = SprayLogFilter(
          fieldId: 'f1',
          sprayType: SprayType.insecticide,
          startDate: DateTime(2025, 1, 1),
          endDate: DateTime(2025, 12, 31),
        );
        expect(filter.hasFilters, isTrue);
      });
    });

    group('copyWith', () {
      test('updates fieldId', () {
        const original = SprayLogFilter(fieldId: 'old');
        final copy = original.copyWith(fieldId: 'new');
        expect(copy.fieldId, 'new');
      });

      test('updates sprayType', () {
        const original = SprayLogFilter();
        final copy = original.copyWith(sprayType: SprayType.foliar);
        expect(copy.sprayType, SprayType.foliar);
      });

      test('updates startDate', () {
        final date = DateTime(2025, 5, 15);
        const original = SprayLogFilter();
        final copy = original.copyWith(startDate: date);
        expect(copy.startDate, date);
      });

      test('updates endDate', () {
        final date = DateTime(2025, 11, 20);
        const original = SprayLogFilter();
        final copy = original.copyWith(endDate: date);
        expect(copy.endDate, date);
      });

      test('clearFieldId sets fieldId to null', () {
        const original = SprayLogFilter(fieldId: 'f1');
        final copy = original.copyWith(clearFieldId: true);
        expect(copy.fieldId, isNull);
      });

      test('clearSprayType sets sprayType to null', () {
        const original = SprayLogFilter(sprayType: SprayType.herbicide);
        final copy = original.copyWith(clearSprayType: true);
        expect(copy.sprayType, isNull);
      });

      test('clearStartDate sets startDate to null', () {
        final original = SprayLogFilter(startDate: DateTime(2025, 1, 1));
        final copy = original.copyWith(clearStartDate: true);
        expect(copy.startDate, isNull);
      });

      test('clearEndDate sets endDate to null', () {
        final original = SprayLogFilter(endDate: DateTime(2025, 12, 31));
        final copy = original.copyWith(clearEndDate: true);
        expect(copy.endDate, isNull);
      });

      test('clear flag takes precedence over new value', () {
        const original = SprayLogFilter(fieldId: 'old');
        final copy = original.copyWith(fieldId: 'new', clearFieldId: true);
        expect(copy.fieldId, isNull);
      });

      test('clearing all fields results in hasFilters false', () {
        final original = SprayLogFilter(
          fieldId: 'f1',
          sprayType: SprayType.insecticide,
          startDate: DateTime(2025, 1, 1),
          endDate: DateTime(2025, 12, 31),
        );
        final copy = original.copyWith(
          clearFieldId: true,
          clearSprayType: true,
          clearStartDate: true,
          clearEndDate: true,
        );
        expect(copy.hasFilters, isFalse);
      });

      test('preserves existing values when updating one field', () {
        final original = SprayLogFilter(
          fieldId: 'f1',
          sprayType: SprayType.herbicide,
          startDate: DateTime(2025, 3, 1),
        );
        final copy = original.copyWith(
          endDate: DateTime(2025, 6, 30),
        );
        expect(copy.fieldId, 'f1');
        expect(copy.sprayType, SprayType.herbicide);
        expect(copy.startDate, DateTime(2025, 3, 1));
        expect(copy.endDate, DateTime(2025, 6, 30));
      });

      test('copyWith with no arguments preserves all values', () {
        final original = SprayLogFilter(
          fieldId: 'f-x',
          sprayType: SprayType.foliar,
          startDate: DateTime(2025, 2, 1),
          endDate: DateTime(2025, 8, 1),
        );
        final copy = original.copyWith();
        expect(copy.fieldId, original.fieldId);
        expect(copy.sprayType, original.sprayType);
        expect(copy.startDate, original.startDate);
        expect(copy.endDate, original.endDate);
      });
    });
  });
}
