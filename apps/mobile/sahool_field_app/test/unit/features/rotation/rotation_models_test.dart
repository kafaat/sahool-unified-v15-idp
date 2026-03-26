import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/rotation/models/rotation_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // CropFamily Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropFamily', () {
    test('should have exactly 15 crop families', () {
      expect(CropFamily.values.length, 15);
    });

    test('should contain all expected families', () {
      final expected = [
        CropFamily.solanaceae,
        CropFamily.fabaceae,
        CropFamily.poaceae,
        CropFamily.brassicaceae,
        CropFamily.cucurbitaceae,
        CropFamily.amaranthaceae,
        CropFamily.apiaceae,
        CropFamily.alliaceae,
        CropFamily.asteraceae,
        CropFamily.malvaceae,
        CropFamily.convolvulaceae,
        CropFamily.rubiaceae,
        CropFamily.celastraceae,
        CropFamily.rosaceae,
        CropFamily.lamiaceae,
      ];
      for (final family in expected) {
        expect(CropFamily.values.contains(family), isTrue,
            reason: '${family.name} should be in CropFamily');
      }
    });

    test('should resolve from name string', () {
      expect(CropFamily.values.byName('solanaceae'), CropFamily.solanaceae);
      expect(CropFamily.values.byName('fabaceae'), CropFamily.fabaceae);
      expect(CropFamily.values.byName('lamiaceae'), CropFamily.lamiaceae);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CropFamilyInfo
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropFamilyInfo', () {
    test('should have data for every CropFamily value', () {
      for (final family in CropFamily.values) {
        expect(CropFamilyInfo.familyData.containsKey(family), isTrue,
            reason: '${family.name} should have family data');
      }
    });

    test('each family info should have matching family field', () {
      for (final entry in CropFamilyInfo.familyData.entries) {
        expect(entry.value.family, entry.key);
      }
    });

    test('should have non-empty English and Arabic names', () {
      for (final info in CropFamilyInfo.familyData.values) {
        expect(info.nameEn, isNotEmpty,
            reason: '${info.family.name} should have English name');
        expect(info.nameAr, isNotEmpty,
            reason: '${info.family.name} should have Arabic name');
      }
    });

    test('should have non-empty common crops lists', () {
      for (final info in CropFamilyInfo.familyData.values) {
        expect(info.commonCrops, isNotEmpty,
            reason: '${info.family.name} should have common crops');
        expect(info.commonCropsAr, isNotEmpty,
            reason: '${info.family.name} should have Arabic common crops');
        expect(info.commonCrops.length, info.commonCropsAr.length,
            reason:
                '${info.family.name} EN/AR common crops should match in count');
      }
    });

    test('should have exactly 3 nutrient demands (N, P, K)', () {
      for (final info in CropFamilyInfo.familyData.values) {
        expect(info.nutrientDemands.length, 3,
            reason: '${info.family.name} should have 3 nutrient demands');
        for (final demand in info.nutrientDemands) {
          expect(['High', 'Medium', 'Low'].contains(demand), isTrue,
              reason:
                  '${info.family.name} demand "$demand" should be High/Medium/Low');
        }
      }
    });

    test('should have valid rotation years (>= 0)', () {
      for (final info in CropFamilyInfo.familyData.values) {
        expect(info.rotationYears, greaterThanOrEqualTo(0));
      }
    });

    test('perennial families should have 0 rotation years', () {
      final rubiaceae = CropFamilyInfo.familyData[CropFamily.rubiaceae]!;
      final celastraceae = CropFamilyInfo.familyData[CropFamily.celastraceae]!;
      expect(rubiaceae.rotationYears, 0);
      expect(celastraceae.rotationYears, 0);
    });

    test('solanaceae should have specific known values', () {
      final info = CropFamilyInfo.familyData[CropFamily.solanaceae]!;
      expect(info.nameEn, 'Nightshades');
      expect(info.rotationYears, 3);
      expect(info.commonCrops, contains('Tomato'));
    });

    test('fabaceae should be low nitrogen demand (nitrogen fixer)', () {
      final info = CropFamilyInfo.familyData[CropFamily.fabaceae]!;
      expect(info.nutrientDemands[0], 'Low');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Crop
  // ═══════════════════════════════════════════════════════════════════════════

  group('Crop', () {
    const testCrop = Crop(
      id: 'test_crop',
      nameEn: 'Test Crop',
      nameAr: 'محصول اختبار',
      family: CropFamily.poaceae,
      growingDays: 90,
      season: 'Spring',
    );

    test('should construct with required fields', () {
      expect(testCrop.id, 'test_crop');
      expect(testCrop.nameEn, 'Test Crop');
      expect(testCrop.nameAr, 'محصول اختبار');
      expect(testCrop.family, CropFamily.poaceae);
      expect(testCrop.growingDays, 90);
      expect(testCrop.season, 'Spring');
    });

    test('should default isPerennial to false', () {
      expect(testCrop.isPerennial, false);
    });

    test('should accept isPerennial = true', () {
      const perennial = Crop(
        id: 'coffee',
        nameEn: 'Coffee',
        nameAr: 'بن',
        family: CropFamily.rubiaceae,
        growingDays: 365,
        season: 'Perennial',
        isPerennial: true,
      );
      expect(perennial.isPerennial, true);
    });

    test('toJson should produce correct map', () {
      final json = testCrop.toJson();
      expect(json['id'], 'test_crop');
      expect(json['nameEn'], 'Test Crop');
      expect(json['nameAr'], 'محصول اختبار');
      expect(json['family'], 'poaceae');
      expect(json['growingDays'], 90);
      expect(json['season'], 'Spring');
      expect(json['isPerennial'], false);
    });

    test('fromJson should restore crop correctly', () {
      final json = testCrop.toJson();
      final restored = Crop.fromJson(json);

      expect(restored.id, testCrop.id);
      expect(restored.nameEn, testCrop.nameEn);
      expect(restored.nameAr, testCrop.nameAr);
      expect(restored.family, testCrop.family);
      expect(restored.growingDays, testCrop.growingDays);
      expect(restored.season, testCrop.season);
      expect(restored.isPerennial, testCrop.isPerennial);
    });

    test('fromJson roundtrip preserves all fields', () {
      const perennialCrop = Crop(
        id: 'coffee',
        nameEn: 'Coffee',
        nameAr: 'بن',
        family: CropFamily.rubiaceae,
        growingDays: 365,
        season: 'Perennial',
        isPerennial: true,
      );
      final restored = Crop.fromJson(perennialCrop.toJson());
      expect(restored.isPerennial, true);
      expect(restored.family, CropFamily.rubiaceae);
    });

    test('fromJson should default isPerennial to false when missing', () {
      final json = <String, dynamic>{
        'id': 'wheat',
        'nameEn': 'Wheat',
        'nameAr': 'قمح',
        'family': 'poaceae',
        'growingDays': 120,
        'season': 'Winter',
        // isPerennial intentionally missing
      };
      final crop = Crop.fromJson(json);
      expect(crop.isPerennial, false);
    });

    test('fromJson should fall back to poaceae for unknown family', () {
      final json = <String, dynamic>{
        'id': 'mystery',
        'nameEn': 'Mystery',
        'nameAr': 'غموض',
        'family': 'unknown_family',
        'growingDays': 60,
        'season': 'Spring',
        'isPerennial': false,
      };
      final crop = Crop.fromJson(json);
      expect(crop.family, CropFamily.poaceae);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // YemenCrops
  // ═══════════════════════════════════════════════════════════════════════════

  group('YemenCrops', () {
    test('should have 7 crops', () {
      expect(YemenCrops.crops.length, 7);
    });

    test('should contain all expected crop IDs', () {
      final ids = YemenCrops.crops.map((c) => c.id).toSet();
      expect(ids, containsAll([
        'wheat',
        'sorghum',
        'coffee',
        'qat',
        'tomato',
        'onion',
        'fava_beans',
      ]));
    });

    test('coffee and qat should be perennial', () {
      final coffee = YemenCrops.crops.firstWhere((c) => c.id == 'coffee');
      final qat = YemenCrops.crops.firstWhere((c) => c.id == 'qat');
      expect(coffee.isPerennial, true);
      expect(qat.isPerennial, true);
    });

    test('non-perennial crops should not be marked perennial', () {
      final nonPerennials = YemenCrops.crops.where((c) => !c.isPerennial);
      expect(nonPerennials.length, 5);
      for (final crop in nonPerennials) {
        expect(crop.isPerennial, false);
      }
    });

    test('should have at least one legume (fabaceae)', () {
      final legumes =
          YemenCrops.crops.where((c) => c.family == CropFamily.fabaceae);
      expect(legumes.isNotEmpty, true);
      expect(legumes.first.id, 'fava_beans');
    });

    test('all crops should have positive growing days', () {
      for (final crop in YemenCrops.crops) {
        expect(crop.growingDays, greaterThan(0));
      }
    });

    test('all crops should have non-empty bilingual names', () {
      for (final crop in YemenCrops.crops) {
        expect(crop.nameEn, isNotEmpty);
        expect(crop.nameAr, isNotEmpty);
      }
    });

    test('wheat should have correct properties', () {
      final wheat = YemenCrops.crops.firstWhere((c) => c.id == 'wheat');
      expect(wheat.nameEn, 'Wheat');
      expect(wheat.nameAr, 'قمح');
      expect(wheat.family, CropFamily.poaceae);
      expect(wheat.growingDays, 120);
      expect(wheat.season, 'Winter');
      expect(wheat.isPerennial, false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CompatibilityScore
  // ═══════════════════════════════════════════════════════════════════════════

  group('CompatibilityScore', () {
    const crop1 = Crop(
      id: 'c1',
      nameEn: 'Crop 1',
      nameAr: 'محصول 1',
      family: CropFamily.fabaceae,
      growingDays: 90,
      season: 'Spring',
    );
    const crop2 = Crop(
      id: 'c2',
      nameEn: 'Crop 2',
      nameAr: 'محصول 2',
      family: CropFamily.poaceae,
      growingDays: 120,
      season: 'Winter',
    );

    test('should construct with all required fields', () {
      const score = CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: 0.85,
        level: 'Good',
        reason: 'Different families',
        reasonAr: 'فصائل مختلفة',
      );
      expect(score.crop1.id, 'c1');
      expect(score.crop2.id, 'c2');
      expect(score.score, 0.85);
      expect(score.level, 'Good');
      expect(score.reason, 'Different families');
      expect(score.reasonAr, 'فصائل مختلفة');
    });

    test('isGood should be true when score >= 0.7', () {
      const good = CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: 0.7,
        level: 'Good',
        reason: '',
        reasonAr: '',
      );
      expect(good.isGood, true);
      expect(good.isFair, false);
      expect(good.isPoor, false);
    });

    test('isGood boundary at exactly 0.7', () {
      const boundary = CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: 0.7,
        level: 'Good',
        reason: '',
        reasonAr: '',
      );
      expect(boundary.isGood, true);
      expect(boundary.isFair, false);
    });

    test('isFair should be true when 0.5 <= score < 0.7', () {
      const fair = CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: 0.55,
        level: 'Fair',
        reason: '',
        reasonAr: '',
      );
      expect(fair.isGood, false);
      expect(fair.isFair, true);
      expect(fair.isPoor, false);
    });

    test('isFair boundary at exactly 0.5', () {
      const boundary = CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: 0.5,
        level: 'Fair',
        reason: '',
        reasonAr: '',
      );
      expect(boundary.isFair, true);
      expect(boundary.isPoor, false);
    });

    test('isPoor should be true when score < 0.5', () {
      const poor = CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: 0.25,
        level: 'Avoid',
        reason: 'Same family',
        reasonAr: 'نفس الفصيلة',
      );
      expect(poor.isGood, false);
      expect(poor.isFair, false);
      expect(poor.isPoor, true);
    });

    test('isPoor boundary at 0.49', () {
      const boundary = CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: 0.49,
        level: 'Poor',
        reason: '',
        reasonAr: '',
      );
      expect(boundary.isPoor, true);
      expect(boundary.isFair, false);
    });

    test('score of 0.0 should be poor', () {
      const zero = CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: 0.0,
        level: 'Avoid',
        reason: '',
        reasonAr: '',
      );
      expect(zero.isPoor, true);
    });

    test('score of 1.0 should be good', () {
      const perfect = CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: 1.0,
        level: 'Excellent',
        reason: '',
        reasonAr: '',
      );
      expect(perfect.isGood, true);
    });

    test('toJson should include crop JSON', () {
      const score = CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: 0.85,
        level: 'Good',
        reason: 'test reason',
        reasonAr: 'سبب اختبار',
      );
      final json = score.toJson();
      expect(json['score'], 0.85);
      expect(json['level'], 'Good');
      expect(json['reason'], 'test reason');
      expect(json['reasonAr'], 'سبب اختبار');
      expect(json['crop1'], isA<Map<String, dynamic>>());
      expect(json['crop2'], isA<Map<String, dynamic>>());
      expect((json['crop1'] as Map)['id'], 'c1');
      expect((json['crop2'] as Map)['id'], 'c2');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SoilHealth
  // ═══════════════════════════════════════════════════════════════════════════

  group('SoilHealth', () {
    test('should construct with all required fields', () {
      final health = SoilHealth(
        nitrogen: 70,
        phosphorus: 65,
        potassium: 60,
        organicMatter: 55,
        ph: 6.8,
        waterRetention: 50,
        measuredAt: DateTime(2024, 6, 15),
      );
      expect(health.nitrogen, 70);
      expect(health.phosphorus, 65);
      expect(health.potassium, 60);
      expect(health.organicMatter, 55);
      expect(health.ph, 6.8);
      expect(health.waterRetention, 50);
      expect(health.measuredAt, DateTime(2024, 6, 15));
    });

    test('overallScore should average N, P, K, OM, WR (not pH)', () {
      final health = SoilHealth(
        nitrogen: 80,
        phosphorus: 60,
        potassium: 70,
        organicMatter: 50,
        ph: 7.0,
        waterRetention: 40,
        measuredAt: DateTime.now(),
      );
      // (80 + 60 + 70 + 50 + 40) / 5 = 60.0
      expect(health.overallScore, 60.0);
    });

    test('overallScore with all zeros', () {
      final health = SoilHealth(
        nitrogen: 0,
        phosphorus: 0,
        potassium: 0,
        organicMatter: 0,
        ph: 7.0,
        waterRetention: 0,
        measuredAt: DateTime.now(),
      );
      expect(health.overallScore, 0.0);
    });

    test('overallScore with all 100', () {
      final health = SoilHealth(
        nitrogen: 100,
        phosphorus: 100,
        potassium: 100,
        organicMatter: 100,
        ph: 7.0,
        waterRetention: 100,
        measuredAt: DateTime.now(),
      );
      expect(health.overallScore, 100.0);
    });

    test('healthLevel Excellent when overallScore >= 80', () {
      final health = SoilHealth(
        nitrogen: 85,
        phosphorus: 85,
        potassium: 85,
        organicMatter: 85,
        ph: 7.0,
        waterRetention: 85,
        measuredAt: DateTime.now(),
      );
      expect(health.healthLevel, 'Excellent');
    });

    test('healthLevel Excellent at boundary 80', () {
      final health = SoilHealth(
        nitrogen: 80,
        phosphorus: 80,
        potassium: 80,
        organicMatter: 80,
        ph: 7.0,
        waterRetention: 80,
        measuredAt: DateTime.now(),
      );
      expect(health.healthLevel, 'Excellent');
    });

    test('healthLevel Good when 60 <= overallScore < 80', () {
      final health = SoilHealth(
        nitrogen: 65,
        phosphorus: 65,
        potassium: 65,
        organicMatter: 65,
        ph: 7.0,
        waterRetention: 65,
        measuredAt: DateTime.now(),
      );
      expect(health.healthLevel, 'Good');
    });

    test('healthLevel Good at boundary 60', () {
      final health = SoilHealth(
        nitrogen: 60,
        phosphorus: 60,
        potassium: 60,
        organicMatter: 60,
        ph: 7.0,
        waterRetention: 60,
        measuredAt: DateTime.now(),
      );
      expect(health.healthLevel, 'Good');
    });

    test('healthLevel Fair when 40 <= overallScore < 60', () {
      final health = SoilHealth(
        nitrogen: 45,
        phosphorus: 45,
        potassium: 45,
        organicMatter: 45,
        ph: 7.0,
        waterRetention: 45,
        measuredAt: DateTime.now(),
      );
      expect(health.healthLevel, 'Fair');
    });

    test('healthLevel Fair at boundary 40', () {
      final health = SoilHealth(
        nitrogen: 40,
        phosphorus: 40,
        potassium: 40,
        organicMatter: 40,
        ph: 7.0,
        waterRetention: 40,
        measuredAt: DateTime.now(),
      );
      expect(health.healthLevel, 'Fair');
    });

    test('healthLevel Poor when overallScore < 40', () {
      final health = SoilHealth(
        nitrogen: 25,
        phosphorus: 25,
        potassium: 25,
        organicMatter: 25,
        ph: 7.0,
        waterRetention: 25,
        measuredAt: DateTime.now(),
      );
      expect(health.healthLevel, 'Poor');
    });

    test('toJson should include all fields plus computed values', () {
      final health = SoilHealth(
        nitrogen: 70,
        phosphorus: 65,
        potassium: 60,
        organicMatter: 55,
        ph: 6.8,
        waterRetention: 50,
        measuredAt: DateTime(2024, 1, 15),
      );
      final json = health.toJson();
      expect(json['nitrogen'], 70.0);
      expect(json['phosphorus'], 65.0);
      expect(json['potassium'], 60.0);
      expect(json['organicMatter'], 55.0);
      expect(json['ph'], 6.8);
      expect(json['waterRetention'], 50.0);
      expect(json['measuredAt'], '2024-01-15T00:00:00.000');
      expect(json['overallScore'], 60.0);
      expect(json['healthLevel'], 'Good');
    });

    test('fromJson should restore all fields', () {
      final original = SoilHealth(
        nitrogen: 70,
        phosphorus: 65,
        potassium: 60,
        organicMatter: 55,
        ph: 6.8,
        waterRetention: 50,
        measuredAt: DateTime(2024, 1, 15),
      );
      final restored = SoilHealth.fromJson(original.toJson());
      expect(restored.nitrogen, original.nitrogen);
      expect(restored.phosphorus, original.phosphorus);
      expect(restored.potassium, original.potassium);
      expect(restored.organicMatter, original.organicMatter);
      expect(restored.ph, original.ph);
      expect(restored.waterRetention, original.waterRetention);
      expect(restored.measuredAt, original.measuredAt);
    });

    test('fromJson roundtrip preserves computed properties', () {
      final original = SoilHealth(
        nitrogen: 70,
        phosphorus: 65,
        potassium: 60,
        organicMatter: 55,
        ph: 6.8,
        waterRetention: 50,
        measuredAt: DateTime(2024, 1, 15),
      );
      final restored = SoilHealth.fromJson(original.toJson());
      expect(restored.overallScore, original.overallScore);
      expect(restored.healthLevel, original.healthLevel);
    });

    test('fromJson handles integer values cast to num', () {
      final json = <String, dynamic>{
        'nitrogen': 70,
        'phosphorus': 65,
        'potassium': 60,
        'organicMatter': 55,
        'ph': 7,
        'waterRetention': 50,
        'measuredAt': '2024-06-15T00:00:00.000',
      };
      final health = SoilHealth.fromJson(json);
      expect(health.nitrogen, 70.0);
      expect(health.ph, 7.0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // RotationYear
  // ═══════════════════════════════════════════════════════════════════════════

  group('RotationYear', () {
    test('should construct with required fields only', () {
      const ry = RotationYear(year: 2025, season: 'Winter');
      expect(ry.year, 2025);
      expect(ry.season, 'Winter');
      expect(ry.crop, isNull);
      expect(ry.soilHealthBefore, isNull);
      expect(ry.soilHealthAfter, isNull);
      expect(ry.plantingDate, isNull);
      expect(ry.harvestDate, isNull);
      expect(ry.yieldAmount, isNull);
      expect(ry.notes, isNull);
    });

    test('isPlanned should be true when crop is set', () {
      const ry = RotationYear(
        year: 2025,
        season: 'Winter',
        crop: Crop(
          id: 'wheat',
          nameEn: 'Wheat',
          nameAr: 'قمح',
          family: CropFamily.poaceae,
          growingDays: 120,
          season: 'Winter',
        ),
      );
      expect(ry.isPlanned, true);
    });

    test('isPlanned should be false when crop is null', () {
      const ry = RotationYear(year: 2025, season: 'Fallow');
      expect(ry.isPlanned, false);
    });

    test('isCompleted should be true when harvestDate is set', () {
      final ry = RotationYear(
        year: 2023,
        season: 'Winter',
        harvestDate: DateTime(2024, 2, 15),
      );
      expect(ry.isCompleted, true);
    });

    test('isCompleted should be false when harvestDate is null', () {
      const ry = RotationYear(year: 2025, season: 'Winter');
      expect(ry.isCompleted, false);
    });

    test('isCurrent returns true when now is between planting and harvest', () {
      final now = DateTime.now();
      final ry = RotationYear(
        year: now.year,
        season: 'Current',
        plantingDate: now.subtract(const Duration(days: 30)),
        harvestDate: now.add(const Duration(days: 30)),
      );
      expect(ry.isCurrent, true);
    });

    test('isCurrent returns false when both dates are in the past', () {
      final ry = RotationYear(
        year: 2020,
        season: 'Past',
        plantingDate: DateTime(2020, 1, 1),
        harvestDate: DateTime(2020, 6, 1),
      );
      expect(ry.isCurrent, false);
    });

    test('isCurrent returns false when dates are null', () {
      const ry = RotationYear(year: 2025, season: 'Winter');
      expect(ry.isCurrent, false);
    });

    test('isCurrent returns false when only plantingDate is set', () {
      final ry = RotationYear(
        year: 2025,
        season: 'Winter',
        plantingDate: DateTime.now().subtract(const Duration(days: 10)),
      );
      expect(ry.isCurrent, false);
    });

    test('copyWith should override specified fields', () {
      const original = RotationYear(
        year: 2024,
        season: 'Spring',
      );
      final updated = original.copyWith(
        yieldAmount: 5.0,
        notes: 'Good harvest',
      );
      expect(updated.year, 2024);
      expect(updated.season, 'Spring');
      expect(updated.yieldAmount, 5.0);
      expect(updated.notes, 'Good harvest');
    });

    test('copyWith should not change fields when no arguments', () {
      final original = RotationYear(
        year: 2024,
        season: 'Spring',
        yieldAmount: 3.5,
        notes: 'Original notes',
        plantingDate: DateTime(2024, 3, 15),
      );
      final copy = original.copyWith();
      expect(copy.year, original.year);
      expect(copy.season, original.season);
      expect(copy.yieldAmount, original.yieldAmount);
      expect(copy.notes, original.notes);
      expect(copy.plantingDate, original.plantingDate);
    });

    test('toJson should handle null optional fields', () {
      const ry = RotationYear(year: 2025, season: 'Fallow');
      final json = ry.toJson();
      expect(json['year'], 2025);
      expect(json['season'], 'Fallow');
      expect(json['crop'], isNull);
      expect(json['plantingDate'], isNull);
      expect(json['harvestDate'], isNull);
      expect(json['yieldAmount'], isNull);
      expect(json['notes'], isNull);
    });

    test('toJson/fromJson roundtrip with all fields populated', () {
      final wheat = YemenCrops.crops.firstWhere((c) => c.id == 'wheat');
      final soilBefore = SoilHealth(
        nitrogen: 65,
        phosphorus: 55,
        potassium: 60,
        organicMatter: 45,
        ph: 6.8,
        waterRetention: 50,
        measuredAt: DateTime(2024, 10, 15),
      );
      final soilAfter = SoilHealth(
        nitrogen: 45,
        phosphorus: 50,
        potassium: 55,
        organicMatter: 42,
        ph: 6.7,
        waterRetention: 48,
        measuredAt: DateTime(2025, 3, 20),
      );

      final original = RotationYear(
        year: 2024,
        season: 'Winter',
        crop: wheat,
        soilHealthBefore: soilBefore,
        soilHealthAfter: soilAfter,
        plantingDate: DateTime(2024, 11, 1),
        harvestDate: DateTime(2025, 3, 15),
        yieldAmount: 3.5,
        notes: 'Good season',
      );

      final json = original.toJson();
      final restored = RotationYear.fromJson(json);

      expect(restored.year, original.year);
      expect(restored.season, original.season);
      expect(restored.crop?.id, original.crop?.id);
      expect(restored.soilHealthBefore?.nitrogen, soilBefore.nitrogen);
      expect(restored.soilHealthAfter?.nitrogen, soilAfter.nitrogen);
      expect(restored.plantingDate, original.plantingDate);
      expect(restored.harvestDate, original.harvestDate);
      expect(restored.yieldAmount, original.yieldAmount);
      expect(restored.notes, original.notes);
    });

    test('fromJson with null optional fields', () {
      final json = <String, dynamic>{
        'year': 2025,
        'season': 'Summer',
        'crop': null,
        'soilHealthBefore': null,
        'soilHealthAfter': null,
        'plantingDate': null,
        'harvestDate': null,
        'yieldAmount': null,
        'notes': null,
      };
      final ry = RotationYear.fromJson(json);
      expect(ry.year, 2025);
      expect(ry.season, 'Summer');
      expect(ry.crop, isNull);
      expect(ry.plantingDate, isNull);
      expect(ry.harvestDate, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // RotationPlan
  // ═══════════════════════════════════════════════════════════════════════════

  group('RotationPlan', () {
    late RotationPlan plan;

    setUp(() {
      final now = DateTime.now();
      plan = RotationPlan(
        id: 'plan_001',
        fieldId: 'field_001',
        fieldName: 'Test Field',
        rotationYears: [
          RotationYear(
            year: now.year - 1,
            season: 'Winter',
            crop: YemenCrops.crops.firstWhere((c) => c.id == 'wheat'),
            plantingDate: DateTime(now.year - 1, 11, 1),
            harvestDate: DateTime(now.year, 2, 15),
          ),
          RotationYear(
            year: now.year,
            season: 'Spring',
            crop: YemenCrops.crops.firstWhere((c) => c.id == 'tomato'),
            plantingDate: now.subtract(const Duration(days: 30)),
            harvestDate: now.add(const Duration(days: 30)),
          ),
          RotationYear(
            year: now.year + 1,
            season: 'Winter',
            crop: YemenCrops.crops.firstWhere((c) => c.id == 'fava_beans'),
          ),
        ],
        createdAt: DateTime(2024, 1, 1),
        updatedAt: DateTime(2024, 6, 1),
        preferences: {'prioritizeSoilHealth': true},
      );
    });

    test('totalYears should return count of rotation years', () {
      expect(plan.totalYears, 3);
    });

    test('familiesUsed should return distinct families from crops', () {
      final families = plan.familiesUsed;
      expect(families, contains(CropFamily.poaceae));
      expect(families, contains(CropFamily.solanaceae));
      expect(families, contains(CropFamily.fabaceae));
      expect(families.length, 3);
    });

    test('familiesUsed should exclude null crops', () {
      final planWithNullCrop = RotationPlan(
        id: 'p2',
        fieldId: 'f2',
        fieldName: 'Field 2',
        rotationYears: [
          const RotationYear(year: 2025, season: 'Fallow'),
          RotationYear(
            year: 2026,
            season: 'Winter',
            crop: YemenCrops.crops.firstWhere((c) => c.id == 'wheat'),
          ),
        ],
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      expect(planWithNullCrop.familiesUsed, [CropFamily.poaceae]);
    });

    test('pastRotations should return completed rotations before now', () {
      final past = plan.pastRotations;
      expect(past.isNotEmpty, true);
      for (final r in past) {
        expect(r.harvestDate, isNotNull);
        expect(r.harvestDate!.isBefore(DateTime.now()), true);
      }
    });

    test('futureRotations should return rotations without planting date or after now', () {
      final future = plan.futureRotations;
      expect(future.isNotEmpty, true);
    });

    test('currentRotation should return a rotation year', () {
      final current = plan.currentRotation;
      expect(current, isNotNull);
    });

    test('preferences should be accessible', () {
      expect(plan.preferences, isNotNull);
      expect(plan.preferences!['prioritizeSoilHealth'], true);
    });

    test('preferences can be null', () {
      final planNoPrefs = RotationPlan(
        id: 'p3',
        fieldId: 'f3',
        fieldName: 'Field 3',
        rotationYears: [],
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      expect(planNoPrefs.preferences, isNull);
    });

    test('toJson/fromJson roundtrip', () {
      final json = plan.toJson();
      final restored = RotationPlan.fromJson(json);

      expect(restored.id, plan.id);
      expect(restored.fieldId, plan.fieldId);
      expect(restored.fieldName, plan.fieldName);
      expect(restored.rotationYears.length, plan.rotationYears.length);
      expect(restored.createdAt, plan.createdAt);
      expect(restored.updatedAt, plan.updatedAt);
      expect(restored.preferences, plan.preferences);
    });

    test('toJson includes serialized rotation years', () {
      final json = plan.toJson();
      expect(json['rotationYears'], isA<List>());
      expect((json['rotationYears'] as List).length, 3);
    });

    test('empty plan should have totalYears 0', () {
      final emptyPlan = RotationPlan(
        id: 'empty',
        fieldId: 'f',
        fieldName: 'Empty',
        rotationYears: [],
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      expect(emptyPlan.totalYears, 0);
      expect(emptyPlan.familiesUsed, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CropRecommendation
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropRecommendation', () {
    final crop = YemenCrops.crops.firstWhere((c) => c.id == 'wheat');

    test('should construct with all fields', () {
      final rec = CropRecommendation(
        crop: crop,
        suitabilityScore: 85,
        reasons: ['Good soil', 'Breaks pest cycle'],
        reasonsAr: ['تربة جيدة', 'يكسر دورة الآفات'],
        warning: 'Monitor water',
        warningAr: 'راقب المياه',
      );
      expect(rec.crop.id, 'wheat');
      expect(rec.suitabilityScore, 85);
      expect(rec.reasons.length, 2);
      expect(rec.reasonsAr.length, 2);
      expect(rec.warning, 'Monitor water');
      expect(rec.warningAr, 'راقب المياه');
    });

    test('isHighlySuitable should be true when score >= 80', () {
      final rec = CropRecommendation(
        crop: crop,
        suitabilityScore: 80,
        reasons: ['test'],
        reasonsAr: ['اختبار'],
      );
      expect(rec.isHighlySuitable, true);
      expect(rec.isSuitable, true);
    });

    test('isHighlySuitable should be false when score < 80', () {
      final rec = CropRecommendation(
        crop: crop,
        suitabilityScore: 79,
        reasons: ['test'],
        reasonsAr: ['اختبار'],
      );
      expect(rec.isHighlySuitable, false);
    });

    test('isSuitable should be true when score >= 60', () {
      final rec = CropRecommendation(
        crop: crop,
        suitabilityScore: 60,
        reasons: ['test'],
        reasonsAr: ['اختبار'],
      );
      expect(rec.isSuitable, true);
      expect(rec.isHighlySuitable, false);
    });

    test('isSuitable should be false when score < 60', () {
      final rec = CropRecommendation(
        crop: crop,
        suitabilityScore: 59,
        reasons: ['test'],
        reasonsAr: ['اختبار'],
      );
      expect(rec.isSuitable, false);
    });

    test('hasWarning should be true when warning is not null', () {
      final rec = CropRecommendation(
        crop: crop,
        suitabilityScore: 70,
        reasons: ['test'],
        reasonsAr: ['اختبار'],
        warning: 'Some warning',
        warningAr: 'تحذير',
      );
      expect(rec.hasWarning, true);
    });

    test('hasWarning should be false when warning is null', () {
      final rec = CropRecommendation(
        crop: crop,
        suitabilityScore: 85,
        reasons: ['test'],
        reasonsAr: ['اختبار'],
      );
      expect(rec.hasWarning, false);
    });

    test('toJson should include all fields', () {
      final rec = CropRecommendation(
        crop: crop,
        suitabilityScore: 85,
        reasons: ['r1', 'r2'],
        reasonsAr: ['س1', 'س2'],
        warning: 'w',
        warningAr: 'ت',
      );
      final json = rec.toJson();
      expect(json['suitabilityScore'], 85);
      expect(json['reasons'], ['r1', 'r2']);
      expect(json['reasonsAr'], ['س1', 'س2']);
      expect(json['warning'], 'w');
      expect(json['warningAr'], 'ت');
      expect(json['crop'], isA<Map<String, dynamic>>());
    });

    test('toJson should include null warning fields when absent', () {
      final rec = CropRecommendation(
        crop: crop,
        suitabilityScore: 85,
        reasons: ['test'],
        reasonsAr: ['اختبار'],
      );
      final json = rec.toJson();
      expect(json['warning'], isNull);
      expect(json['warningAr'], isNull);
    });
  });
}
