import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/rotation/models/rotation_models.dart';

void main() {
  group('CropFamily', () {
    test('should have all expected crop families', () {
      expect(CropFamily.values.length, 15);
      expect(CropFamily.values.contains(CropFamily.solanaceae), true);
      expect(CropFamily.values.contains(CropFamily.fabaceae), true);
      expect(CropFamily.values.contains(CropFamily.poaceae), true);
    });
  });

  group('CropFamilyInfo', () {
    test('should have data for all crop families', () {
      for (final family in CropFamily.values) {
        expect(CropFamilyInfo.familyData.containsKey(family), true);
      }
    });

    test('should have valid rotation years', () {
      for (final info in CropFamilyInfo.familyData.values) {
        expect(info.rotationYears, greaterThanOrEqualTo(0));
      }
    });

    test('should have nutrient demands for each family', () {
      for (final info in CropFamilyInfo.familyData.values) {
        expect(info.nutrientDemands.length, 3);
        for (final demand in info.nutrientDemands) {
          expect(['High', 'Medium', 'Low'].contains(demand), true);
        }
      }
    });
  });

  group('Crop', () {
    test('should serialize to JSON and back', () {
      const crop = Crop(
        id: 'test_crop',
        nameEn: 'Test Crop',
        nameAr: 'محصول اختبار',
        family: CropFamily.poaceae,
        growingDays: 90,
        season: 'Spring',
      );

      final json = crop.toJson();
      final restored = Crop.fromJson(json);

      expect(restored.id, crop.id);
      expect(restored.nameEn, crop.nameEn);
      expect(restored.nameAr, crop.nameAr);
      expect(restored.family, crop.family);
      expect(restored.growingDays, crop.growingDays);
      expect(restored.season, crop.season);
      expect(restored.isPerennial, false);
    });

    test('should handle perennial crops', () {
      const crop = Crop(
        id: 'coffee',
        nameEn: 'Coffee',
        nameAr: 'بن',
        family: CropFamily.rubiaceae,
        growingDays: 365,
        season: 'Perennial',
        isPerennial: true,
      );

      final json = crop.toJson();
      final restored = Crop.fromJson(json);

      expect(restored.isPerennial, true);
    });
  });

  group('YemenCrops', () {
    test('should have expected crops', () {
      expect(YemenCrops.crops.length, greaterThan(0));

      final cropIds = YemenCrops.crops.map((c) => c.id).toList();
      expect(cropIds.contains('wheat'), true);
      expect(cropIds.contains('sorghum'), true);
      expect(cropIds.contains('coffee'), true);
      expect(cropIds.contains('tomato'), true);
    });

    test('should have at least one nitrogen-fixing legume', () {
      final legumes = YemenCrops.crops.where(
        (c) => c.family == CropFamily.fabaceae,
      );
      expect(legumes.isNotEmpty, true);
    });
  });

  group('CompatibilityScore', () {
    test('should classify good compatibility', () {
      final crop1 = YemenCrops.crops.first;
      final crop2 = YemenCrops.crops.last;

      const score = CompatibilityScore(
        crop1: Crop(
          id: 'test1',
          nameEn: 'Test 1',
          nameAr: 'اختبار 1',
          family: CropFamily.fabaceae,
          growingDays: 90,
          season: 'Spring',
        ),
        crop2: Crop(
          id: 'test2',
          nameEn: 'Test 2',
          nameAr: 'اختبار 2',
          family: CropFamily.poaceae,
          growingDays: 120,
          season: 'Winter',
        ),
        score: 0.85,
        level: 'Good',
        reason: 'Different families',
        reasonAr: 'فصائل مختلفة',
      );

      expect(score.isGood, true);
      expect(score.isFair, false);
      expect(score.isPoor, false);
    });

    test('should classify fair compatibility', () {
      const score = CompatibilityScore(
        crop1: Crop(
          id: 'test1',
          nameEn: 'Test 1',
          nameAr: 'اختبار 1',
          family: CropFamily.poaceae,
          growingDays: 90,
          season: 'Spring',
        ),
        crop2: Crop(
          id: 'test2',
          nameEn: 'Test 2',
          nameAr: 'اختبار 2',
          family: CropFamily.poaceae,
          growingDays: 120,
          season: 'Winter',
        ),
        score: 0.55,
        level: 'Fair',
        reason: 'Same family but different crops',
        reasonAr: 'نفس الفصيلة لكن محاصيل مختلفة',
      );

      expect(score.isGood, false);
      expect(score.isFair, true);
      expect(score.isPoor, false);
    });

    test('should classify poor compatibility', () {
      const score = CompatibilityScore(
        crop1: Crop(
          id: 'test1',
          nameEn: 'Tomato',
          nameAr: 'طماطم',
          family: CropFamily.solanaceae,
          growingDays: 90,
          season: 'Spring',
        ),
        crop2: Crop(
          id: 'test2',
          nameEn: 'Potato',
          nameAr: 'بطاطس',
          family: CropFamily.solanaceae,
          growingDays: 100,
          season: 'Spring',
        ),
        score: 0.25,
        level: 'Avoid',
        reason: 'Same family - increases disease risk',
        reasonAr: 'نفس الفصيلة - يزيد من خطر الأمراض',
      );

      expect(score.isGood, false);
      expect(score.isFair, false);
      expect(score.isPoor, true);
    });
  });

  group('SoilHealth', () {
    test('should calculate overall score correctly', () {
      final health = SoilHealth(
        nitrogen: 80,
        phosphorus: 60,
        potassium: 70,
        organicMatter: 50,
        ph: 7.0,
        waterRetention: 40,
        measuredAt: DateTime.now(),
      );

      // (80 + 60 + 70 + 50 + 40) / 5 = 60
      expect(health.overallScore, 60.0);
    });

    test('should classify health levels correctly', () {
      final excellent = SoilHealth(
        nitrogen: 85,
        phosphorus: 85,
        potassium: 85,
        organicMatter: 85,
        ph: 7.0,
        waterRetention: 85,
        measuredAt: DateTime.now(),
      );
      expect(excellent.healthLevel, 'Excellent');

      final good = SoilHealth(
        nitrogen: 65,
        phosphorus: 65,
        potassium: 65,
        organicMatter: 65,
        ph: 7.0,
        waterRetention: 65,
        measuredAt: DateTime.now(),
      );
      expect(good.healthLevel, 'Good');

      final fair = SoilHealth(
        nitrogen: 45,
        phosphorus: 45,
        potassium: 45,
        organicMatter: 45,
        ph: 7.0,
        waterRetention: 45,
        measuredAt: DateTime.now(),
      );
      expect(fair.healthLevel, 'Fair');

      final poor = SoilHealth(
        nitrogen: 25,
        phosphorus: 25,
        potassium: 25,
        organicMatter: 25,
        ph: 7.0,
        waterRetention: 25,
        measuredAt: DateTime.now(),
      );
      expect(poor.healthLevel, 'Poor');
    });

    test('should serialize to JSON and back', () {
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
      final restored = SoilHealth.fromJson(json);

      expect(restored.nitrogen, health.nitrogen);
      expect(restored.phosphorus, health.phosphorus);
      expect(restored.potassium, health.potassium);
      expect(restored.organicMatter, health.organicMatter);
      expect(restored.ph, health.ph);
      expect(restored.waterRetention, health.waterRetention);
    });
  });

  group('RotationYear', () {
    test('should serialize to JSON and back', () {
      final year = RotationYear(
        year: 2024,
        season: 'Spring',
        crop: YemenCrops.crops.first,
        plantingDate: DateTime(2024, 3, 15),
        harvestDate: DateTime(2024, 6, 15),
        yieldAmount: 3.5,
        notes: 'Test notes',
      );

      final json = year.toJson();
      final restored = RotationYear.fromJson(json);

      expect(restored.year, year.year);
      expect(restored.season, year.season);
      expect(restored.crop?.id, year.crop?.id);
      expect(restored.yieldAmount, year.yieldAmount);
      expect(restored.notes, year.notes);
    });

    test('should detect current status', () {
      final now = DateTime.now();
      final currentYear = RotationYear(
        year: now.year,
        season: 'Current',
        crop: YemenCrops.crops.first,
        plantingDate: now.subtract(const Duration(days: 30)),
        harvestDate: now.add(const Duration(days: 30)),
      );

      expect(currentYear.isCurrent, true);
      expect(currentYear.isCompleted, false);
    });

    test('should detect completed status', () {
      final pastYear = RotationYear(
        year: DateTime.now().year - 1,
        season: 'Winter',
        crop: YemenCrops.crops.first,
        plantingDate: DateTime(2023, 11, 1),
        harvestDate: DateTime(2024, 2, 15),
        yieldAmount: 4.0,
      );

      expect(pastYear.isCompleted, true);
    });

    test('copyWith should work correctly', () {
      const year = RotationYear(
        year: 2024,
        season: 'Spring',
      );

      final updated = year.copyWith(
        yieldAmount: 5.0,
        notes: 'New notes',
      );

      expect(updated.year, year.year);
      expect(updated.season, year.season);
      expect(updated.yieldAmount, 5.0);
      expect(updated.notes, 'New notes');
    });
  });

  group('RotationPlan', () {
    test('should serialize to JSON and back', () {
      final plan = RotationPlan(
        id: 'plan_001',
        fieldId: 'field_001',
        fieldName: 'Test Field',
        rotationYears: [
          RotationYear(
            year: 2024,
            season: 'Spring',
            crop: YemenCrops.crops.first,
          ),
          RotationYear(
            year: 2025,
            season: 'Winter',
            crop: YemenCrops.crops.last,
          ),
        ],
        createdAt: DateTime(2024, 1, 1),
        updatedAt: DateTime(2024, 1, 15),
      );

      final json = plan.toJson();
      final restored = RotationPlan.fromJson(json);

      expect(restored.id, plan.id);
      expect(restored.fieldId, plan.fieldId);
      expect(restored.fieldName, plan.fieldName);
      expect(restored.rotationYears.length, plan.rotationYears.length);
      expect(restored.totalYears, 2);
    });

    test('should track families used', () {
      final plan = RotationPlan(
        id: 'plan_001',
        fieldId: 'field_001',
        fieldName: 'Test Field',
        rotationYears: [
          RotationYear(
            year: 2024,
            season: 'Spring',
            crop: YemenCrops.crops.firstWhere((c) => c.id == 'wheat'),
          ),
          RotationYear(
            year: 2025,
            season: 'Winter',
            crop: YemenCrops.crops.firstWhere((c) => c.id == 'fava_beans'),
          ),
        ],
        createdAt: DateTime(2024, 1, 1),
        updatedAt: DateTime(2024, 1, 15),
      );

      final families = plan.familiesUsed;
      expect(families.contains(CropFamily.poaceae), true);
      expect(families.contains(CropFamily.fabaceae), true);
    });
  });

  group('CropRecommendation', () {
    test('should serialize to JSON and back', () {
      final recommendation = CropRecommendation(
        crop: YemenCrops.crops.first,
        suitabilityScore: 85,
        reasons: ['Good soil match', 'Breaks pest cycle'],
        reasonsAr: ['توافق جيد مع التربة', 'يكسر دورة الآفات'],
        warning: 'Monitor water levels',
        warningAr: 'راقب مستويات المياه',
      );

      final json = recommendation.toJson();
      final restored = CropRecommendation.fromJson(json);

      expect(restored.crop.id, recommendation.crop.id);
      expect(restored.suitabilityScore, recommendation.suitabilityScore);
      expect(restored.reasons, recommendation.reasons);
      expect(restored.reasonsAr, recommendation.reasonsAr);
      expect(restored.warning, recommendation.warning);
      expect(restored.warningAr, recommendation.warningAr);
    });

    test('should classify suitability correctly', () {
      final highlySuitable = CropRecommendation(
        crop: YemenCrops.crops.first,
        suitabilityScore: 85,
        reasons: ['Excellent match'],
        reasonsAr: ['توافق ممتاز'],
      );
      expect(highlySuitable.isHighlySuitable, true);
      expect(highlySuitable.isSuitable, true);

      final suitable = CropRecommendation(
        crop: YemenCrops.crops.first,
        suitabilityScore: 70,
        reasons: ['Good match'],
        reasonsAr: ['توافق جيد'],
      );
      expect(suitable.isHighlySuitable, false);
      expect(suitable.isSuitable, true);

      final notSuitable = CropRecommendation(
        crop: YemenCrops.crops.first,
        suitabilityScore: 45,
        reasons: ['Poor match'],
        reasonsAr: ['توافق ضعيف'],
      );
      expect(notSuitable.isHighlySuitable, false);
      expect(notSuitable.isSuitable, false);
    });

    test('should detect warnings', () {
      final withWarning = CropRecommendation(
        crop: YemenCrops.crops.first,
        suitabilityScore: 70,
        reasons: ['Good match'],
        reasonsAr: ['توافق جيد'],
        warning: 'Requires extra irrigation',
        warningAr: 'يتطلب ري إضافي',
      );
      expect(withWarning.hasWarning, true);

      final withoutWarning = CropRecommendation(
        crop: YemenCrops.crops.first,
        suitabilityScore: 85,
        reasons: ['Excellent match'],
        reasonsAr: ['توافق ممتاز'],
      );
      expect(withoutWarning.hasWarning, false);
    });
  });
}
