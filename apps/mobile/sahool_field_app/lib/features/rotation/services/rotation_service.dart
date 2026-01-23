import 'dart:math';
import 'package:flutter/foundation.dart';
import '../models/rotation_models.dart';

/// Service for managing crop rotation plans
class RotationService {
  // Simulate API delay
  Future<void> _simulateDelay() async {
    await Future.delayed(const Duration(milliseconds: 500));
  }

  /// Get rotation plan for a specific field
  Future<RotationPlan> getRotationPlan(String fieldId) async {
    await _simulateDelay();

    // Generate sample rotation plan
    final currentYear = DateTime.now().year;
    final rotationYears = <RotationYear>[];

    // Past rotations (2 years back)
    rotationYears.add(RotationYear(
      year: currentYear - 2,
      season: 'Winter',
      crop: YemenCrops.crops.firstWhere((c) => c.id == 'wheat'),
      plantingDate: DateTime(currentYear - 2, 11, 1),
      harvestDate: DateTime(currentYear - 1, 3, 15),
      yieldAmount: 3.5,
      soilHealthBefore: SoilHealth(
        nitrogen: 65,
        phosphorus: 55,
        potassium: 60,
        organicMatter: 45,
        ph: 6.8,
        waterRetention: 50,
        measuredAt: DateTime(currentYear - 2, 10, 15),
      ),
      soilHealthAfter: SoilHealth(
        nitrogen: 45,
        phosphorus: 50,
        potassium: 55,
        organicMatter: 42,
        ph: 6.7,
        waterRetention: 48,
        measuredAt: DateTime(currentYear - 1, 3, 20),
      ),
    ));

    rotationYears.add(RotationYear(
      year: currentYear - 1,
      season: 'Spring',
      crop: YemenCrops.crops.firstWhere((c) => c.id == 'fava_beans'),
      plantingDate: DateTime(currentYear - 1, 3, 20),
      harvestDate: DateTime(currentYear - 1, 6, 20),
      yieldAmount: 2.8,
      soilHealthBefore: SoilHealth(
        nitrogen: 45,
        phosphorus: 50,
        potassium: 55,
        organicMatter: 42,
        ph: 6.7,
        waterRetention: 48,
        measuredAt: DateTime(currentYear - 1, 3, 20),
      ),
      soilHealthAfter: SoilHealth(
        nitrogen: 72, // Nitrogen fixing!
        phosphorus: 52,
        potassium: 58,
        organicMatter: 48,
        ph: 6.9,
        waterRetention: 52,
        measuredAt: DateTime(currentYear - 1, 6, 25),
      ),
    ));

    // Current rotation
    rotationYears.add(RotationYear(
      year: currentYear,
      season: 'Spring',
      crop: YemenCrops.crops.firstWhere((c) => c.id == 'tomato'),
      plantingDate: DateTime(currentYear, 3, 15),
      harvestDate: DateTime(currentYear, 6, 15),
      soilHealthBefore: SoilHealth(
        nitrogen: 72,
        phosphorus: 52,
        potassium: 58,
        organicMatter: 48,
        ph: 6.9,
        waterRetention: 52,
        measuredAt: DateTime(currentYear, 3, 1),
      ),
    ));

    // Future rotations
    rotationYears.add(RotationYear(
      year: currentYear + 1,
      season: 'Winter',
      crop: YemenCrops.crops.firstWhere((c) => c.id == 'onion'),
      plantingDate: DateTime(currentYear + 1, 11, 1),
      harvestDate: DateTime(currentYear + 2, 2, 15),
    ));

    rotationYears.add(RotationYear(
      year: currentYear + 2,
      season: 'Summer',
      crop: YemenCrops.crops.firstWhere((c) => c.id == 'sorghum'),
      plantingDate: DateTime(currentYear + 2, 5, 1),
      harvestDate: DateTime(currentYear + 2, 8, 10),
    ));

    return RotationPlan(
      id: 'plan_$fieldId',
      fieldId: fieldId,
      fieldName: 'Field #$fieldId',
      rotationYears: rotationYears,
      createdAt: DateTime(currentYear - 2, 10, 1),
      updatedAt: DateTime.now(),
      preferences: {
        'prioritizeSoilHealth': true,
        'includeNitrogenFixers': true,
        'avoidSameFamily': true,
        'rotationCycleYears': 5,
      },
    );
  }

  /// Generate a new rotation plan based on preferences
  Future<RotationPlan> generateRotationPlan(
    String fieldId,
    int years,
    Map<String, dynamic> preferences,
  ) async {
    await _simulateDelay();

    final currentYear = DateTime.now().year;
    final rotationYears = <RotationYear>[];
    final availableCrops = YemenCrops.crops.where((c) => !c.isPerennial).toList();

    final prioritizeSoilHealth = preferences['prioritizeSoilHealth'] as bool? ?? true;
    final includeNitrogenFixers = preferences['includeNitrogenFixers'] as bool? ?? true;

    // Generate rotation ensuring family diversity
    final usedFamilies = <CropFamily>[];
    var currentSoilHealth = SoilHealth(
      nitrogen: 60,
      phosphorus: 55,
      potassium: 58,
      organicMatter: 45,
      ph: 6.8,
      waterRetention: 50,
      measuredAt: DateTime.now(),
    );

    for (int i = 0; i < years; i++) {
      // Select crop based on rotation principles
      Crop? selectedCrop;

      if (includeNitrogenFixers && i % 3 == 1) {
        // Every 3rd year, try to plant a legume for nitrogen fixing
        selectedCrop = availableCrops
            .where((c) =>
                c.family == CropFamily.fabaceae &&
                !usedFamilies.contains(c.family))
            .firstOrNull;
      }

      // If no legume selected, pick best available crop
      if (selectedCrop == null) {
        selectedCrop = availableCrops
            .where((c) => !usedFamilies.contains(c.family))
            .firstOrNull ?? availableCrops.first;
      }

      // Update used families (keep last 3 years)
      usedFamilies.add(selectedCrop.family);
      if (usedFamilies.length > 3) {
        usedFamilies.removeAt(0);
      }

      // Calculate planting dates based on season
      DateTime? plantingDate;
      DateTime? harvestDate;

      if (selectedCrop.season == 'Winter') {
        plantingDate = DateTime(currentYear + i, 11, 1);
        harvestDate = plantingDate.add(Duration(days: selectedCrop.growingDays));
      } else if (selectedCrop.season == 'Spring') {
        plantingDate = DateTime(currentYear + i, 3, 15);
        harvestDate = plantingDate.add(Duration(days: selectedCrop.growingDays));
      } else if (selectedCrop.season == 'Summer') {
        plantingDate = DateTime(currentYear + i, 5, 1);
        harvestDate = plantingDate.add(Duration(days: selectedCrop.growingDays));
      }

      // Simulate soil health changes
      final soilHealthAfter = _calculateSoilHealthAfterCrop(
        currentSoilHealth,
        selectedCrop,
        prioritizeSoilHealth,
      );

      rotationYears.add(RotationYear(
        year: currentYear + i,
        season: selectedCrop.season,
        crop: selectedCrop,
        plantingDate: plantingDate,
        harvestDate: harvestDate,
        soilHealthBefore: currentSoilHealth,
      ));

      currentSoilHealth = soilHealthAfter;
    }

    return RotationPlan(
      id: 'plan_${fieldId}_${DateTime.now().millisecondsSinceEpoch}',
      fieldId: fieldId,
      fieldName: 'Field #$fieldId',
      rotationYears: rotationYears,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
      preferences: preferences,
    );
  }

  /// Calculate soil health after growing a crop
  SoilHealth _calculateSoilHealthAfterCrop(
    SoilHealth before,
    Crop crop,
    bool prioritizeSoilHealth,
  ) {
    final familyInfo = CropFamilyInfo.familyData[crop.family]!;
    double nitrogenChange = 0;
    double phosphorusChange = 0;
    double potassiumChange = 0;
    double organicMatterChange = 0;

    // Nitrogen demand/fixing
    if (crop.family == CropFamily.fabaceae) {
      nitrogenChange = 15; // Nitrogen fixing!
    } else if (familyInfo.nutrientDemands[0] == 'High') {
      nitrogenChange = -15;
    } else if (familyInfo.nutrientDemands[0] == 'Medium') {
      nitrogenChange = -8;
    } else {
      nitrogenChange = -3;
    }

    // Phosphorus demand
    if (familyInfo.nutrientDemands[1] == 'High') {
      phosphorusChange = -5;
    } else if (familyInfo.nutrientDemands[1] == 'Medium') {
      phosphorusChange = -3;
    } else {
      phosphorusChange = -1;
    }

    // Potassium demand
    if (familyInfo.nutrientDemands[2] == 'High') {
      potassiumChange = -8;
    } else if (familyInfo.nutrientDemands[2] == 'Medium') {
      potassiumChange = -5;
    } else {
      potassiumChange = -2;
    }

    // Organic matter (generally increases with crop residue)
    organicMatterChange = 2;

    // Apply soil health priority bonus
    if (prioritizeSoilHealth) {
      organicMatterChange += 1;
    }

    return SoilHealth(
      nitrogen: (before.nitrogen + nitrogenChange).clamp(0, 100),
      phosphorus: (before.phosphorus + phosphorusChange).clamp(0, 100),
      potassium: (before.potassium + potassiumChange).clamp(0, 100),
      organicMatter: (before.organicMatter + organicMatterChange).clamp(0, 100),
      ph: before.ph,
      waterRetention:
          (before.waterRetention + organicMatterChange * 0.5).clamp(0, 100),
      measuredAt: DateTime.now(),
    );
  }

  /// Get compatibility score between two crops
  Future<CompatibilityScore> getCropCompatibility(Crop crop1, Crop crop2) async {
    await _simulateDelay();

    double score = 1.0; // Start with perfect score
    String level;
    String reason;
    String reasonAr;

    // Same family - poor compatibility (disease/pest buildup)
    if (crop1.family == crop2.family) {
      score = 0.2;
      level = 'Avoid';
      reason = 'Same crop family - increases disease and pest pressure';
      reasonAr = 'نفس الفصيلة - يزيد من خطر الأمراض والآفات';
    }
    // Legume after heavy feeder - excellent
    else if (crop1.family == CropFamily.fabaceae &&
        _isHeavyFeeder(crop2.family)) {
      score = 0.95;
      level = 'Excellent';
      reason = 'Legume fixes nitrogen for next heavy feeder crop';
      reasonAr = 'البقوليات تثبت النيتروجين للمحصول التالي';
    }
    // Heavy feeder after legume - excellent
    else if (_isHeavyFeeder(crop1.family) &&
        crop2.family == CropFamily.fabaceae) {
      score = 0.95;
      level = 'Excellent';
      reason = 'Heavy feeder benefits from nitrogen fixed by legumes';
      reasonAr = 'المحصول المستهلك يستفيد من النيتروجين المثبت';
    }
    // Light feeder after heavy feeder - good
    else if (_isLightFeeder(crop1.family) && _isHeavyFeeder(crop2.family)) {
      score = 0.75;
      level = 'Good';
      reason = 'Light feeder gives soil time to recover';
      reasonAr = 'المحصول الخفيف يعطي التربة وقت للتعافي';
    }
    // Different families - good compatibility
    else {
      score = 0.80;
      level = 'Good';
      reason = 'Different families - breaks pest and disease cycles';
      reasonAr = 'فصائل مختلفة - يكسر دورة الآفات والأمراض';
    }

    return CompatibilityScore(
      crop1: crop1,
      crop2: crop2,
      score: score,
      level: level,
      reason: reason,
      reasonAr: reasonAr,
    );
  }

  /// Check if crop family is a heavy feeder
  bool _isHeavyFeeder(CropFamily family) {
    final info = CropFamilyInfo.familyData[family]!;
    return info.nutrientDemands[0] == 'High';
  }

  /// Check if crop family is a light feeder
  bool _isLightFeeder(CropFamily family) {
    final info = CropFamilyInfo.familyData[family]!;
    return info.nutrientDemands[0] == 'Low';
  }

  /// Get soil health trend over time for a field
  Future<List<SoilHealth>> getSoilHealthTrend(String fieldId) async {
    await _simulateDelay();

    final currentYear = DateTime.now().year;
    final trend = <SoilHealth>[];

    // Generate 5 years of soil health data
    for (int i = 4; i >= 0; i--) {
      final baseYear = currentYear - i;

      // Simulate improving trend with rotation
      final improvement = (4 - i) * 3.0; // 3% improvement per year

      trend.add(SoilHealth(
        nitrogen: (60 + improvement + Random().nextDouble() * 5).clamp(0, 100),
        phosphorus: (55 + improvement + Random().nextDouble() * 5).clamp(0, 100),
        potassium: (58 + improvement + Random().nextDouble() * 5).clamp(0, 100),
        organicMatter: (45 + improvement + Random().nextDouble() * 5).clamp(0, 100),
        ph: 6.8 + Random().nextDouble() * 0.3,
        waterRetention:
            (50 + improvement + Random().nextDouble() * 5).clamp(0, 100),
        measuredAt: DateTime(baseYear, 6, 15),
      ));
    }

    return trend;
  }

  /// Get recommended crops for a field and year based on rotation history
  Future<List<CropRecommendation>> getRecommendedCrops(
    String fieldId,
    int year,
  ) async {
    await _simulateDelay();

    // Get rotation plan to check history
    final plan = await getRotationPlan(fieldId);

    // Get families used in recent years
    final recentFamilies = plan.rotationYears
        .where((r) => r.year >= year - 3 && r.crop != null)
        .map((r) => r.crop!.family)
        .toSet();

    // Get last crop
    final lastCrop = plan.rotationYears
        .where((r) => r.year < year && r.crop != null)
        .map((r) => r.crop!)
        .lastOrNull;

    final recommendations = <CropRecommendation>[];
    final availableCrops = YemenCrops.crops.where((c) => !c.isPerennial).toList();

    for (final crop in availableCrops) {
      double score = 70.0; // Base score
      final reasons = <String>[];
      final reasonsAr = <String>[];
      String? warning;
      String? warningAr;

      // Bonus for different family
      if (!recentFamilies.contains(crop.family)) {
        score += 15;
        reasons.add('New crop family - breaks pest cycles');
        reasonsAr.add('فصيلة جديدة - يكسر دورة الآفات');
      } else {
        score -= 25;
        warning = 'Family recently used - may increase disease risk';
        warningAr = 'الفصيلة استخدمت مؤخراً - قد تزيد خطر الأمراض';
      }

      // Bonus for nitrogen fixers
      if (crop.family == CropFamily.fabaceae) {
        score += 10;
        reasons.add('Fixes nitrogen - improves soil fertility');
        reasonsAr.add('يثبت النيتروجين - يحسن خصوبة التربة');
      }

      // Check compatibility with last crop
      if (lastCrop != null) {
        final compatibility = await getCropCompatibility(crop, lastCrop);
        if (compatibility.isGood) {
          score += 10;
          reasons.add('Good compatibility with previous crop');
          reasonsAr.add('توافق جيد مع المحصول السابق');
        } else if (compatibility.isPoor) {
          score -= 15;
          warning = compatibility.reason;
          warningAr = compatibility.reasonAr;
        }
      }

      recommendations.add(CropRecommendation(
        crop: crop,
        suitabilityScore: score.clamp(0, 100),
        reasons: reasons,
        reasonsAr: reasonsAr,
        warning: warning,
        warningAr: warningAr,
      ));
    }

    // Sort by suitability score
    recommendations.sort((a, b) => b.suitabilityScore.compareTo(a.suitabilityScore));

    return recommendations;
  }

  /// Get all crop families information
  List<CropFamilyInfo> getAllCropFamilies() {
    return CropFamilyInfo.familyData.values.toList();
  }

  /// Get compatibility matrix for all crops
  Future<Map<String, Map<String, CompatibilityScore>>>
      getCompatibilityMatrix() async {
    final matrix = <String, Map<String, CompatibilityScore>>{};
    final crops = YemenCrops.crops.where((c) => !c.isPerennial).toList();

    for (final crop1 in crops) {
      matrix[crop1.id] = {};
      for (final crop2 in crops) {
        if (crop1.id != crop2.id) {
          matrix[crop1.id]![crop2.id] = await getCropCompatibility(crop1, crop2);
        }
      }
    }

    return matrix;
  }
}
