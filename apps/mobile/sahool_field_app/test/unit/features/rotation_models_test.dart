import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/rotation/models/rotation_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // CropFamily Enum Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropFamily enum', () {
    test('should have 15 crop families', () {
      expect(CropFamily.values.length, 15);
    });

    test('should contain all expected families', () {
      expect(CropFamily.values, contains(CropFamily.solanaceae));
      expect(CropFamily.values, contains(CropFamily.fabaceae));
      expect(CropFamily.values, contains(CropFamily.poaceae));
      expect(CropFamily.values, contains(CropFamily.brassicaceae));
      expect(CropFamily.values, contains(CropFamily.cucurbitaceae));
      expect(CropFamily.values, contains(CropFamily.amaranthaceae));
      expect(CropFamily.values, contains(CropFamily.apiaceae));
      expect(CropFamily.values, contains(CropFamily.alliaceae));
      expect(CropFamily.values, contains(CropFamily.asteraceae));
      expect(CropFamily.values, contains(CropFamily.malvaceae));
      expect(CropFamily.values, contains(CropFamily.convolvulaceae));
      expect(CropFamily.values, contains(CropFamily.rubiaceae));
      expect(CropFamily.values, contains(CropFamily.celastraceae));
      expect(CropFamily.values, contains(CropFamily.rosaceae));
      expect(CropFamily.values, contains(CropFamily.lamiaceae));
    });

    test('should have correct name strings', () {
      expect(CropFamily.solanaceae.name, 'solanaceae');
      expect(CropFamily.fabaceae.name, 'fabaceae');
      expect(CropFamily.poaceae.name, 'poaceae');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CropFamilyInfo Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropFamilyInfo', () {
    test('familyData should contain all 15 families', () {
      expect(CropFamilyInfo.familyData.length, 15);
    });

    test('familyData should map every CropFamily enum value', () {
      for (final family in CropFamily.values) {
        expect(CropFamilyInfo.familyData.containsKey(family), isTrue,
            reason: 'Missing family data for ${family.name}');
      }
    });

    test('solanaceae should have correct English and Arabic names', () {
      final info = CropFamilyInfo.familyData[CropFamily.solanaceae]!;
      expect(info.nameEn, 'Nightshades');
      expect(info.nameAr, 'الباذنجانيات');
    });

    test('solanaceae should have correct common crops', () {
      final info = CropFamilyInfo.familyData[CropFamily.solanaceae]!;
      expect(info.commonCrops, contains('Tomato'));
      expect(info.commonCrops, contains('Potato'));
      expect(info.commonCropsAr, contains('طماطم'));
      expect(info.commonCropsAr, contains('بطاطس'));
    });

    test('solanaceae should have 3 year rotation', () {
      final info = CropFamilyInfo.familyData[CropFamily.solanaceae]!;
      expect(info.rotationYears, 3);
    });

    test('fabaceae should have low nitrogen demand (fixes nitrogen)', () {
      final info = CropFamilyInfo.familyData[CropFamily.fabaceae]!;
      expect(info.nutrientDemands[0], 'Low');
    });

    test('fabaceae should have 2 year rotation', () {
      final info = CropFamilyInfo.familyData[CropFamily.fabaceae]!;
      expect(info.rotationYears, 2);
    });

    test('perennial crops (rubiaceae) should have 0 rotation years', () {
      final info = CropFamilyInfo.familyData[CropFamily.rubiaceae]!;
      expect(info.rotationYears, 0);
    });

    test('perennial crops (celastraceae) should have 0 rotation years', () {
      final info = CropFamilyInfo.familyData[CropFamily.celastraceae]!;
      expect(info.rotationYears, 0);
    });

    test('rosaceae should have 4 year rotation (longest non-perennial)', () {
      final info = CropFamilyInfo.familyData[CropFamily.rosaceae]!;
      expect(info.rotationYears, 4);
    });

    test('nutrientDemands should always have exactly 3 elements (N, P, K)',
        () {
      for (final entry in CropFamilyInfo.familyData.entries) {
        expect(entry.value.nutrientDemands.length, 3,
            reason:
                'Family ${entry.key.name} should have 3 nutrient demands (N, P, K)');
      }
    });

    test('all family names in Arabic should be non-empty', () {
      for (final entry in CropFamilyInfo.familyData.entries) {
        expect(entry.value.nameAr.isNotEmpty, isTrue,
            reason: 'Family ${entry.key.name} missing Arabic name');
      }
    });

    test('all family names in English should be non-empty', () {
      for (final entry in CropFamilyInfo.familyData.entries) {
        expect(entry.value.nameEn.isNotEmpty, isTrue,
            reason: 'Family ${entry.key.name} missing English name');
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Crop Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('Crop', () {
    const testCrop = Crop(
      id: 'test_crop',
      nameEn: 'Test Crop',
      nameAr: 'محصول اختبار',
      family: CropFamily.poaceae,
      growingDays: 120,
      season: 'Winter',
    );

    test('should create with required fields', () {
      expect(testCrop.id, 'test_crop');
      expect(testCrop.nameEn, 'Test Crop');
      expect(testCrop.nameAr, 'محصول اختبار');
      expect(testCrop.family, CropFamily.poaceae);
      expect(testCrop.growingDays, 120);
      expect(testCrop.season, 'Winter');
      expect(testCrop.isPerennial, false);
    });

    test('should create perennial crop', () {
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

    test('toJson should serialize correctly', () {
      final json = testCrop.toJson();
      expect(json['id'], 'test_crop');
      expect(json['nameEn'], 'Test Crop');
      expect(json['nameAr'], 'محصول اختبار');
      expect(json['family'], 'poaceae');
      expect(json['growingDays'], 120);
      expect(json['season'], 'Winter');
      expect(json['isPerennial'], false);
    });

    test('fromJson should deserialize correctly', () {
      final json = testCrop.toJson();
      final deserialized = Crop.fromJson(json);
      expect(deserialized.id, testCrop.id);
      expect(deserialized.nameEn, testCrop.nameEn);
      expect(deserialized.nameAr, testCrop.nameAr);
      expect(deserialized.family, testCrop.family);
      expect(deserialized.growingDays, testCrop.growingDays);
      expect(deserialized.season, testCrop.season);
      expect(deserialized.isPerennial, testCrop.isPerennial);
    });

    test('fromJson should handle unknown family with fallback to poaceae', () {
      final json = {
        'id': 'x',
        'nameEn': 'X',
        'nameAr': 'اكس',
        'family': 'unknown_family',
        'growingDays': 100,
        'season': 'Summer',
      };
      final crop = Crop.fromJson(json);
      expect(crop.family, CropFamily.poaceae);
    });

    test('fromJson should default isPerennial to false when missing', () {
      final json = {
        'id': 'x',
        'nameEn': 'X',
        'nameAr': 'اكس',
        'family': 'poaceae',
        'growingDays': 100,
        'season': 'Summer',
      };
      final crop = Crop.fromJson(json);
      expect(crop.isPerennial, false);
    });

    test('roundtrip toJson/fromJson preserves perennial flag', () {
      const perennial = Crop(
        id: 'coffee',
        nameEn: 'Coffee',
        nameAr: 'بن',
        family: CropFamily.rubiaceae,
        growingDays: 365,
        season: 'Perennial',
        isPerennial: true,
      );
      final roundtrip = Crop.fromJson(perennial.toJson());
      expect(roundtrip.isPerennial, true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // YemenCrops Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('YemenCrops', () {
    test('should contain 7 crops', () {
      expect(YemenCrops.crops.length, 7);
    });

    test('should contain wheat', () {
      final wheat = YemenCrops.crops.firstWhere((c) => c.id == 'wheat');
      expect(wheat.nameEn, 'Wheat');
      expect(wheat.nameAr, 'قمح');
      expect(wheat.family, CropFamily.poaceae);
      expect(wheat.growingDays, 120);
      expect(wheat.season, 'Winter');
      expect(wheat.isPerennial, false);
    });

    test('should contain coffee as perennial', () {
      final coffee = YemenCrops.crops.firstWhere((c) => c.id == 'coffee');
      expect(coffee.isPerennial, true);
      expect(coffee.family, CropFamily.rubiaceae);
      expect(coffee.growingDays, 365);
    });

    test('should contain qat as perennial', () {
      final qat = YemenCrops.crops.firstWhere((c) => c.id == 'qat');
      expect(qat.isPerennial, true);
      expect(qat.family, CropFamily.celastraceae);
    });

    test('all crops should have non-empty Arabic names', () {
      for (final crop in YemenCrops.crops) {
        expect(crop.nameAr.isNotEmpty, isTrue,
            reason: 'Crop ${crop.id} missing Arabic name');
      }
    });

    test('all non-perennial crops should have growingDays <= 120', () {
      for (final crop in YemenCrops.crops) {
        if (!crop.isPerennial) {
          expect(crop.growingDays, lessThanOrEqualTo(120),
              reason: 'Non-perennial crop ${crop.id} has unusual growing days');
        }
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CompatibilityScore Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('CompatibilityScore', () {
    const wheat = Crop(
      id: 'wheat',
      nameEn: 'Wheat',
      nameAr: 'قمح',
      family: CropFamily.poaceae,
      growingDays: 120,
      season: 'Winter',
    );
    const beans = Crop(
      id: 'beans',
      nameEn: 'Fava Beans',
      nameAr: 'فول',
      family: CropFamily.fabaceae,
      growingDays: 90,
      season: 'Winter',
    );

    test('isGood should be true when score >= 0.7', () {
      const score = CompatibilityScore(
        crop1: wheat,
        crop2: beans,
        score: 0.85,
        level: 'Excellent',
        reason: 'Good rotation',
        reasonAr: 'تناوب جيد',
      );
      expect(score.isGood, true);
      expect(score.isFair, false);
      expect(score.isPoor, false);
    });

    test('isFair should be true when score >= 0.5 and < 0.7', () {
      const score = CompatibilityScore(
        crop1: wheat,
        crop2: beans,
        score: 0.6,
        level: 'Fair',
        reason: 'Acceptable',
        reasonAr: 'مقبول',
      );
      expect(score.isGood, false);
      expect(score.isFair, true);
      expect(score.isPoor, false);
    });

    test('isPoor should be true when score < 0.5', () {
      const score = CompatibilityScore(
        crop1: wheat,
        crop2: wheat,
        score: 0.3,
        level: 'Poor',
        reason: 'Same family',
        reasonAr: 'نفس العائلة',
      );
      expect(score.isGood, false);
      expect(score.isFair, false);
      expect(score.isPoor, true);
    });

    test('boundary: score 0.7 should be isGood', () {
      const score = CompatibilityScore(
        crop1: wheat,
        crop2: beans,
        score: 0.7,
        level: 'Good',
        reason: 'Good',
        reasonAr: 'جيد',
      );
      expect(score.isGood, true);
      expect(score.isFair, false);
    });

    test('boundary: score 0.5 should be isFair', () {
      const score = CompatibilityScore(
        crop1: wheat,
        crop2: beans,
        score: 0.5,
        level: 'Fair',
        reason: 'Fair',
        reasonAr: 'مقبول',
      );
      expect(score.isFair, true);
      expect(score.isPoor, false);
    });

    test('toJson should serialize all fields', () {
      const score = CompatibilityScore(
        crop1: wheat,
        crop2: beans,
        score: 0.85,
        level: 'Excellent',
        reason: 'Legume rotation',
        reasonAr: 'تناوب البقوليات',
      );
      final json = score.toJson();
      expect(json['score'], 0.85);
      expect(json['level'], 'Excellent');
      expect(json['reason'], 'Legume rotation');
      expect(json['reasonAr'], 'تناوب البقوليات');
      expect(json['crop1'], isA<Map<String, dynamic>>());
      expect(json['crop2'], isA<Map<String, dynamic>>());
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SoilHealth Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SoilHealth', () {
    final now = DateTime(2026, 3, 1);

    test('overallScore should be average of 5 indicators', () {
      final soil = SoilHealth(
        nitrogen: 80,
        phosphorus: 60,
        potassium: 70,
        organicMatter: 50,
        ph: 7.0,
        waterRetention: 40,
        measuredAt: now,
      );
      // (80 + 60 + 70 + 50 + 40) / 5 = 60.0
      expect(soil.overallScore, 60.0);
    });

    test('healthLevel should be Excellent when overallScore >= 80', () {
      final soil = SoilHealth(
        nitrogen: 90,
        phosphorus: 85,
        potassium: 80,
        organicMatter: 85,
        ph: 7.0,
        waterRetention: 80,
        measuredAt: now,
      );
      expect(soil.healthLevel, 'Excellent');
    });

    test('healthLevel should be Good when overallScore >= 60', () {
      final soil = SoilHealth(
        nitrogen: 70,
        phosphorus: 65,
        potassium: 60,
        organicMatter: 60,
        ph: 7.0,
        waterRetention: 55,
        measuredAt: now,
      );
      expect(soil.healthLevel, 'Good');
    });

    test('healthLevel should be Fair when overallScore >= 40', () {
      final soil = SoilHealth(
        nitrogen: 50,
        phosphorus: 45,
        potassium: 40,
        organicMatter: 40,
        ph: 7.0,
        waterRetention: 35,
        measuredAt: now,
      );
      expect(soil.healthLevel, 'Fair');
    });

    test('healthLevel should be Poor when overallScore < 40', () {
      final soil = SoilHealth(
        nitrogen: 20,
        phosphorus: 25,
        potassium: 30,
        organicMatter: 10,
        ph: 5.0,
        waterRetention: 15,
        measuredAt: now,
      );
      expect(soil.healthLevel, 'Poor');
    });

    test('toJson should include overallScore and healthLevel', () {
      final soil = SoilHealth(
        nitrogen: 80,
        phosphorus: 70,
        potassium: 60,
        organicMatter: 50,
        ph: 6.5,
        waterRetention: 40,
        measuredAt: now,
      );
      final json = soil.toJson();
      expect(json['overallScore'], soil.overallScore);
      expect(json['healthLevel'], soil.healthLevel);
      expect(json['ph'], 6.5);
      expect(json['measuredAt'], now.toIso8601String());
    });

    test('fromJson should deserialize correctly', () {
      final soil = SoilHealth(
        nitrogen: 75,
        phosphorus: 65,
        potassium: 55,
        organicMatter: 45,
        ph: 7.2,
        waterRetention: 60,
        measuredAt: now,
      );
      final json = soil.toJson();
      final restored = SoilHealth.fromJson(json);
      expect(restored.nitrogen, soil.nitrogen);
      expect(restored.phosphorus, soil.phosphorus);
      expect(restored.potassium, soil.potassium);
      expect(restored.organicMatter, soil.organicMatter);
      expect(restored.ph, soil.ph);
      expect(restored.waterRetention, soil.waterRetention);
      expect(restored.measuredAt, soil.measuredAt);
    });

    test('fromJson should handle integer numeric values', () {
      final json = {
        'nitrogen': 80,
        'phosphorus': 70,
        'potassium': 60,
        'organicMatter': 50,
        'ph': 7,
        'waterRetention': 40,
        'measuredAt': now.toIso8601String(),
      };
      final soil = SoilHealth.fromJson(json);
      expect(soil.nitrogen, 80.0);
      expect(soil.ph, 7.0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // RotationYear Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('RotationYear', () {
    const wheat = Crop(
      id: 'wheat',
      nameEn: 'Wheat',
      nameAr: 'قمح',
      family: CropFamily.poaceae,
      growingDays: 120,
      season: 'Winter',
    );

    test('isPlanned should be true when crop is not null', () {
      const ry = RotationYear(year: 2026, season: 'Winter', crop: wheat);
      expect(ry.isPlanned, true);
    });

    test('isPlanned should be false when crop is null', () {
      const ry = RotationYear(year: 2026, season: 'Winter');
      expect(ry.isPlanned, false);
    });

    test('isCompleted should be true for past harvest date', () {
      final ry = RotationYear(
        year: 2025,
        season: 'Winter',
        crop: wheat,
        harvestDate: DateTime(2025, 6, 1),
      );
      expect(ry.isCompleted, true);
    });

    test('isCompleted should be false when harvestDate is null', () {
      const ry = RotationYear(year: 2026, season: 'Winter', crop: wheat);
      expect(ry.isCompleted, false);
    });

    test('isCurrent should be true when now is between planting and harvest',
        () {
      final now = DateTime.now();
      final ry = RotationYear(
        year: now.year,
        season: 'Winter',
        crop: wheat,
        plantingDate: now.subtract(const Duration(days: 30)),
        harvestDate: now.add(const Duration(days: 30)),
      );
      expect(ry.isCurrent, true);
    });

    test('isCurrent should be false when dates are null', () {
      const ry = RotationYear(year: 2026, season: 'Winter', crop: wheat);
      expect(ry.isCurrent, false);
    });

    test('toJson and fromJson roundtrip with all fields', () {
      final soilBefore = SoilHealth(
        nitrogen: 50,
        phosphorus: 40,
        potassium: 60,
        organicMatter: 30,
        ph: 7.0,
        waterRetention: 50,
        measuredAt: DateTime(2026, 1, 1),
      );
      final ry = RotationYear(
        year: 2026,
        season: 'Winter',
        crop: wheat,
        soilHealthBefore: soilBefore,
        plantingDate: DateTime(2026, 1, 15),
        harvestDate: DateTime(2026, 5, 15),
        yieldAmount: 4.5,
        notes: 'Good season',
      );
      final json = ry.toJson();
      final restored = RotationYear.fromJson(json);
      expect(restored.year, 2026);
      expect(restored.season, 'Winter');
      expect(restored.crop?.id, 'wheat');
      expect(restored.soilHealthBefore?.nitrogen, 50);
      expect(restored.yieldAmount, 4.5);
      expect(restored.notes, 'Good season');
    });

    test('fromJson handles null optional fields', () {
      final json = {'year': 2026, 'season': 'Summer'};
      final ry = RotationYear.fromJson(json);
      expect(ry.crop, isNull);
      expect(ry.soilHealthBefore, isNull);
      expect(ry.soilHealthAfter, isNull);
      expect(ry.plantingDate, isNull);
      expect(ry.harvestDate, isNull);
      expect(ry.yieldAmount, isNull);
      expect(ry.notes, isNull);
    });

    test('copyWith should update specified fields only', () {
      const ry = RotationYear(year: 2026, season: 'Winter', crop: wheat);
      final updated = ry.copyWith(year: 2027, notes: 'Updated');
      expect(updated.year, 2027);
      expect(updated.season, 'Winter');
      expect(updated.crop?.id, 'wheat');
      expect(updated.notes, 'Updated');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // RotationPlan Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('RotationPlan', () {
    const wheat = Crop(
      id: 'wheat',
      nameEn: 'Wheat',
      nameAr: 'قمح',
      family: CropFamily.poaceae,
      growingDays: 120,
      season: 'Winter',
    );
    const beans = Crop(
      id: 'beans',
      nameEn: 'Fava Beans',
      nameAr: 'فول',
      family: CropFamily.fabaceae,
      growingDays: 90,
      season: 'Winter',
    );

    final now = DateTime.now();
    final plan = RotationPlan(
      id: 'plan-1',
      fieldId: 'field-1',
      fieldName: 'Al-Rashid Field',
      rotationYears: [
        RotationYear(
          year: 2024,
          season: 'Winter',
          crop: wheat,
          plantingDate: DateTime(2024, 1, 1),
          harvestDate: DateTime(2024, 5, 1),
        ),
        RotationYear(
          year: 2025,
          season: 'Winter',
          crop: beans,
          plantingDate: DateTime(2025, 1, 1),
          harvestDate: DateTime(2025, 4, 1),
        ),
        RotationYear(
          year: 2027,
          season: 'Winter',
          crop: wheat,
        ),
      ],
      createdAt: now,
      updatedAt: now,
    );

    test('totalYears should return count of rotation years', () {
      expect(plan.totalYears, 3);
    });

    test('pastRotations should return completed rotations', () {
      final past = plan.pastRotations;
      expect(past.length, 2);
    });

    test('familiesUsed should return unique families', () {
      final families = plan.familiesUsed;
      expect(families, contains(CropFamily.poaceae));
      expect(families, contains(CropFamily.fabaceae));
      expect(families.length, 2);
    });

    test('toJson and fromJson roundtrip', () {
      final json = plan.toJson();
      final restored = RotationPlan.fromJson(json);
      expect(restored.id, plan.id);
      expect(restored.fieldId, plan.fieldId);
      expect(restored.fieldName, plan.fieldName);
      expect(restored.rotationYears.length, plan.rotationYears.length);
      expect(restored.rotationYears[0].crop?.id, 'wheat');
      expect(restored.rotationYears[1].crop?.id, 'beans');
    });

    test('fromJson should handle null preferences', () {
      final json = plan.toJson();
      json.remove('preferences');
      final restored = RotationPlan.fromJson(json);
      expect(restored.preferences, isNull);
    });

    test('should handle plan with no crops (empty rotations)', () {
      final emptyPlan = RotationPlan(
        id: 'plan-empty',
        fieldId: 'field-2',
        fieldName: 'Empty Field',
        rotationYears: [
          const RotationYear(year: 2026, season: 'Winter'),
        ],
        createdAt: now,
        updatedAt: now,
      );
      expect(emptyPlan.familiesUsed, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CropRecommendation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropRecommendation', () {
    const wheat = Crop(
      id: 'wheat',
      nameEn: 'Wheat',
      nameAr: 'قمح',
      family: CropFamily.poaceae,
      growingDays: 120,
      season: 'Winter',
    );

    test('isHighlySuitable when suitabilityScore >= 80', () {
      const rec = CropRecommendation(
        crop: wheat,
        suitabilityScore: 90,
        reasons: ['Good soil'],
        reasonsAr: ['تربة جيدة'],
      );
      expect(rec.isHighlySuitable, true);
      expect(rec.isSuitable, true);
    });

    test('isSuitable but not highly when score in [60, 80)', () {
      const rec = CropRecommendation(
        crop: wheat,
        suitabilityScore: 65,
        reasons: ['Acceptable'],
        reasonsAr: ['مقبول'],
      );
      expect(rec.isHighlySuitable, false);
      expect(rec.isSuitable, true);
    });

    test('not suitable when score < 60', () {
      const rec = CropRecommendation(
        crop: wheat,
        suitabilityScore: 40,
        reasons: ['Poor match'],
        reasonsAr: ['غير مناسب'],
      );
      expect(rec.isHighlySuitable, false);
      expect(rec.isSuitable, false);
    });

    test('hasWarning returns true when warning is set', () {
      const rec = CropRecommendation(
        crop: wheat,
        suitabilityScore: 70,
        reasons: ['OK'],
        reasonsAr: ['موافق'],
        warning: 'Watch for rust',
        warningAr: 'انتبه للصدأ',
      );
      expect(rec.hasWarning, true);
    });

    test('hasWarning returns false when warning is null', () {
      const rec = CropRecommendation(
        crop: wheat,
        suitabilityScore: 70,
        reasons: ['OK'],
        reasonsAr: ['موافق'],
      );
      expect(rec.hasWarning, false);
    });

    test('toJson and fromJson roundtrip', () {
      const rec = CropRecommendation(
        crop: wheat,
        suitabilityScore: 85,
        reasons: ['Good soil', 'Right season'],
        reasonsAr: ['تربة جيدة', 'موسم مناسب'],
        warning: 'Check pests',
        warningAr: 'تحقق من الآفات',
      );
      final json = rec.toJson();
      final restored = CropRecommendation.fromJson(json);
      expect(restored.crop.id, 'wheat');
      expect(restored.suitabilityScore, 85);
      expect(restored.reasons.length, 2);
      expect(restored.reasonsAr.length, 2);
      expect(restored.warning, 'Check pests');
      expect(restored.warningAr, 'تحقق من الآفات');
    });

    test('fromJson handles null warning fields', () {
      final json = {
        'crop': wheat.toJson(),
        'suitabilityScore': 75,
        'reasons': ['OK'],
        'reasonsAr': ['موافق'],
      };
      final rec = CropRecommendation.fromJson(json);
      expect(rec.warning, isNull);
      expect(rec.warningAr, isNull);
    });

    test('copyWith should update specified fields only', () {
      const rec = CropRecommendation(
        crop: wheat,
        suitabilityScore: 70,
        reasons: ['OK'],
        reasonsAr: ['موافق'],
      );
      final updated = rec.copyWith(
        suitabilityScore: 90,
        warning: 'New warning',
      );
      expect(updated.suitabilityScore, 90);
      expect(updated.warning, 'New warning');
      expect(updated.crop.id, 'wheat');
      expect(updated.reasons, ['OK']);
    });
  });
}
