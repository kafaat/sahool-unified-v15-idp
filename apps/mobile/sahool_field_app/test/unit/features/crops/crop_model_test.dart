import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/crops/data/models/crop_model.dart';

void main() {
  group('CropCategory enum', () {
    test('has 11 categories', () {
      expect(CropCategory.values, hasLength(11));
    });

    test('has Arabic names', () {
      expect(CropCategory.cereals.nameAr, 'الحبوب');
      expect(CropCategory.legumes.nameAr, 'البقوليات');
      expect(CropCategory.vegetables.nameAr, 'الخضروات');
      expect(CropCategory.fruits.nameAr, 'الفواكه');
      expect(CropCategory.stimulants.nameAr, 'المنبهات');
    });

    test('has code strings', () {
      expect(CropCategory.cereals.code, 'cereals');
      expect(CropCategory.tubers.code, 'tubers');
    });
  });

  group('GrowthHabit enum', () {
    test('has 3 habits', () {
      expect(GrowthHabit.values, hasLength(3));
    });

    test('has Arabic names', () {
      expect(GrowthHabit.annual.nameAr, 'حولي');
      expect(GrowthHabit.perennial.nameAr, 'معمر');
      expect(GrowthHabit.biennial.nameAr, 'ثنائي الحول');
    });
  });

  group('WaterRequirement enum', () {
    test('has 5 levels', () {
      expect(WaterRequirement.values, hasLength(5));
    });

    test('has Arabic names', () {
      expect(WaterRequirement.veryLow.nameAr, 'منخفضة جداً');
      expect(WaterRequirement.high.nameAr, 'عالية');
    });

    test('has code strings', () {
      expect(WaterRequirement.veryLow.code, 'very_low');
      expect(WaterRequirement.medium.code, 'medium');
    });
  });

  group('Crop model', () {
    late Crop wheat;

    setUp(() {
      wheat = const Crop(
        code: 'WHEAT_001',
        nameEn: 'Wheat',
        nameAr: 'قمح',
        scientificName: 'Triticum aestivum',
        category: CropCategory.cereals,
        growthHabit: GrowthHabit.annual,
        growingSeasonDays: 120,
        optimalTempMin: 10.0,
        optimalTempMax: 25.0,
        waterRequirement: WaterRequirement.medium,
        baseYieldTonHa: 3.0,
        yemenRegions: ['Highlands', 'Tihama'],
        localVarieties: ['Sakha 95', 'Misr 1'],
        kcIni: 0.3,
        kcMid: 1.15,
        kcEnd: 0.4,
      );
    });

    test('fromJson and toJson round-trip', () {
      final json = wheat.toJson();
      final restored = Crop.fromJson(json);

      expect(restored.code, 'WHEAT_001');
      expect(restored.nameEn, 'Wheat');
      expect(restored.nameAr, 'قمح');
      expect(restored.scientificName, 'Triticum aestivum');
      expect(restored.category, CropCategory.cereals);
      expect(restored.growthHabit, GrowthHabit.annual);
      expect(restored.growingSeasonDays, 120);
      expect(restored.optimalTempMin, 10.0);
      expect(restored.optimalTempMax, 25.0);
      expect(restored.waterRequirement, WaterRequirement.medium);
      expect(restored.baseYieldTonHa, 3.0);
      expect(restored.yemenRegions, hasLength(2));
      expect(restored.localVarieties, hasLength(2));
      expect(restored.kcIni, 0.3);
      expect(restored.kcMid, 1.15);
      expect(restored.kcEnd, 0.4);
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'code': 'CROP_MIN',
        'name_en': 'Minimal',
        'name_ar': 'أدنى',
        'scientific_name': 'Test species',
        'category': 'vegetables',
        'growth_habit': 'annual',
        'growing_season_days': 60,
        'optimal_temp_min': 15.0,
        'optimal_temp_max': 30.0,
        'water_requirement': 'medium',
        'base_yield_ton_ha': 2.0,
      };

      final crop = Crop.fromJson(json);
      expect(crop.yemenRegions, isNull);
      expect(crop.localVarieties, isNull);
      expect(crop.kcIni, isNull);
      expect(crop.priceUsdPerTon, isNull);
      expect(crop.yieldUnit, 'ton/ha'); // default
    });

    test('fromJson defaults to vegetables for unknown category', () {
      final json = {
        'code': 'UNKNOWN',
        'name_en': 'Unknown',
        'name_ar': 'غير معروف',
        'scientific_name': 'Unknown sp.',
        'category': 'invalid_category',
        'growth_habit': 'annual',
        'growing_season_days': 60,
        'optimal_temp_min': 15.0,
        'optimal_temp_max': 30.0,
        'water_requirement': 'medium',
        'base_yield_ton_ha': 1.0,
      };

      final crop = Crop.fromJson(json);
      expect(crop.category, CropCategory.vegetables);
    });

    test('equality is based on code', () {
      final same = wheat.copyWith(nameEn: 'Different Name');
      expect(wheat, same);

      final different = wheat.copyWith(code: 'BARLEY_001');
      expect(wheat, isNot(different));
    });

    test('hashCode is based on code', () {
      expect(wheat.hashCode, 'WHEAT_001'.hashCode);
    });

    test('toString contains code and names', () {
      final str = wheat.toString();
      expect(str, contains('WHEAT_001'));
      expect(str, contains('قمح'));
      expect(str, contains('Wheat'));
    });

    test('copyWith creates modified copy', () {
      final modified = wheat.copyWith(
        baseYieldTonHa: 4.5,
        waterRequirement: WaterRequirement.high,
      );
      expect(modified.baseYieldTonHa, 4.5);
      expect(modified.waterRequirement, WaterRequirement.high);
      expect(modified.code, wheat.code); // unchanged
    });
  });
}
