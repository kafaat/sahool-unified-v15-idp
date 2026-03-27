import 'dart:math';
import 'package:dio/dio.dart';
import '../../../core/config/api_config.dart';
import '../../../core/utils/app_logger.dart';
import '../models/rotation_models.dart';

/// Service for managing crop rotation plans.
///
/// Architecture:
/// 1. Try fetching from advisory-service API (port 8093)
///    - GET /api/v1/rotation/plans/{fieldId}
///    - POST /api/v1/rotation/generate
///    - GET /api/v1/rotation/compatibility
///    - GET /api/v1/rotation/soil-health/{fieldId}
/// 2. On network failure, fall back to locally computed plan
class RotationService {
  final Dio _dio;

  RotationService({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  /// Get rotation plan for a specific field.
  /// Tries API first, falls back to local computation.
  Future<RotationPlan> getRotationPlan(String fieldId) async {
    try {
      final response =
          await _dio.get('/api/v1/rotation/plans/$fieldId');
      final data = response.data as Map<String, dynamic>;
      return _parseRotationPlan(data, fieldId);
    } on DioException catch (e) {
      AppLogger.w(
        'Rotation API unavailable (${e.type.name}), using local computation',
        tag: 'ROTATION',
      );
      return _computeLocalRotationPlan(fieldId);
    } catch (e) {
      AppLogger.w('Rotation parse error: $e, using local computation',
          tag: 'ROTATION');
      return _computeLocalRotationPlan(fieldId);
    }
  }

  /// Generate a new rotation plan based on preferences.
  /// Tries advisory-service first, falls back to local computation.
  Future<RotationPlan> generateRotationPlan(
    String fieldId,
    int years,
    Map<String, dynamic> preferences,
  ) async {
    try {
      final response = await _dio.post(
        '/api/v1/rotation/generate',
        data: {
          'fieldId': fieldId,
          'years': years,
          'preferences': preferences,
        },
      );
      final data = response.data as Map<String, dynamic>;
      return _parseRotationPlan(data, fieldId);
    } on DioException catch (e) {
      AppLogger.w(
        'Rotation generate API unavailable (${e.type.name}), using local computation',
        tag: 'ROTATION',
      );
      return _computeGeneratedPlan(fieldId, years, preferences);
    } catch (e) {
      AppLogger.w('Rotation generate error: $e, using local computation',
          tag: 'ROTATION');
      return _computeGeneratedPlan(fieldId, years, preferences);
    }
  }

  /// Get compatibility score between two crops.
  /// Tries advisory-service first, falls back to local computation.
  Future<CompatibilityScore> getCropCompatibility(Crop crop1, Crop crop2) async {
    try {
      final response = await _dio.get(
        '/api/v1/rotation/compatibility',
        queryParameters: {
          'crop1': crop1.id,
          'crop2': crop2.id,
        },
      );
      final data = response.data as Map<String, dynamic>;
      return CompatibilityScore(
        crop1: crop1,
        crop2: crop2,
        score: (data['score'] as num?)?.toDouble() ?? 0.5,
        level: data['level'] as String? ?? 'Good',
        reason: data['reason'] as String? ?? '',
        reasonAr: data['reasonAr'] as String? ?? '',
      );
    } on DioException catch (e) {
      AppLogger.w(
        'Rotation compatibility API unavailable (${e.type.name}), using local computation',
        tag: 'ROTATION',
      );
      return _computeLocalCompatibility(crop1, crop2);
    } catch (e) {
      AppLogger.w('Rotation compatibility error: $e, using local computation',
          tag: 'ROTATION');
      return _computeLocalCompatibility(crop1, crop2);
    }
  }

  /// Get soil health trend over time for a field.
  /// Tries advisory-service first, falls back to local simulation.
  Future<List<SoilHealth>> getSoilHealthTrend(String fieldId) async {
    try {
      final response =
          await _dio.get('/api/v1/rotation/soil-health/$fieldId');
      final List data = response.data as List;
      return data
          .map((e) => _parseSoilHealth(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      AppLogger.w(
        'Soil health API unavailable (${e.type.name}), using local simulation',
        tag: 'ROTATION',
      );
      return _computeLocalSoilHealthTrend();
    } catch (e) {
      AppLogger.w('Soil health parse error: $e, using local simulation',
          tag: 'ROTATION');
      return _computeLocalSoilHealthTrend();
    }
  }

  /// Get recommended crops for a field and year based on rotation history.
  Future<List<CropRecommendation>> getRecommendedCrops(
    String fieldId,
    int year,
  ) async {
    // Get rotation plan to check history (uses API or local fallback)
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
    final availableCrops =
        YemenCrops.crops.where((c) => !c.isPerennial).toList();

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
    recommendations
        .sort((a, b) => b.suitabilityScore.compareTo(a.suitabilityScore));

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
          matrix[crop1.id]![crop2.id] =
              await getCropCompatibility(crop1, crop2);
        }
      }
    }

    return matrix;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // JSON Parsers
  // ─────────────────────────────────────────────────────────────────────────

  RotationPlan _parseRotationPlan(Map<String, dynamic> json, String fieldId) {
    final yearsList = (json['rotationYears'] as List? ?? [])
        .map((y) => _parseRotationYear(y as Map<String, dynamic>))
        .toList();
    return RotationPlan(
      id: json['id'] as String? ?? 'plan_$fieldId',
      fieldId: json['fieldId'] as String? ?? fieldId,
      fieldName: json['fieldName'] as String? ?? 'Field #$fieldId',
      rotationYears: yearsList,
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'] as String) ?? DateTime.now()
          : DateTime.now(),
      updatedAt: json['updatedAt'] != null
          ? DateTime.tryParse(json['updatedAt'] as String) ?? DateTime.now()
          : DateTime.now(),
      preferences: (json['preferences'] as Map<String, dynamic>?) ?? {},
    );
  }

  RotationYear _parseRotationYear(Map<String, dynamic> json) {
    Crop? crop;
    final cropData = json['crop'] as Map<String, dynamic>?;
    if (cropData != null) {
      final cropId = cropData['id'] as String? ?? '';
      crop = YemenCrops.crops.where((c) => c.id == cropId).firstOrNull;
    }

    return RotationYear(
      year: (json['year'] as num?)?.toInt() ?? DateTime.now().year,
      season: json['season'] as String? ?? 'Unknown',
      crop: crop,
      plantingDate: json['plantingDate'] != null
          ? DateTime.tryParse(json['plantingDate'] as String)
          : null,
      harvestDate: json['harvestDate'] != null
          ? DateTime.tryParse(json['harvestDate'] as String)
          : null,
      yieldAmount: (json['yieldAmount'] as num?)?.toDouble(),
      soilHealthBefore: json['soilHealthBefore'] != null
          ? _parseSoilHealth(json['soilHealthBefore'] as Map<String, dynamic>)
          : null,
      soilHealthAfter: json['soilHealthAfter'] != null
          ? _parseSoilHealth(json['soilHealthAfter'] as Map<String, dynamic>)
          : null,
    );
  }

  SoilHealth _parseSoilHealth(Map<String, dynamic> json) {
    return SoilHealth(
      nitrogen: (json['nitrogen'] as num?)?.toDouble() ?? 60.0,
      phosphorus: (json['phosphorus'] as num?)?.toDouble() ?? 55.0,
      potassium: (json['potassium'] as num?)?.toDouble() ?? 58.0,
      organicMatter: (json['organicMatter'] as num?)?.toDouble() ?? 45.0,
      ph: (json['ph'] as num?)?.toDouble() ?? 6.8,
      waterRetention: (json['waterRetention'] as num?)?.toDouble() ?? 50.0,
      measuredAt: json['measuredAt'] != null
          ? DateTime.tryParse(json['measuredAt'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Local Computation Fallbacks
  // ─────────────────────────────────────────────────────────────────────────

  RotationPlan _computeLocalRotationPlan(String fieldId) {
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
        nitrogen: 72,
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

  RotationPlan _computeGeneratedPlan(
    String fieldId,
    int years,
    Map<String, dynamic> preferences,
  ) {
    final currentYear = DateTime.now().year;
    final rotationYears = <RotationYear>[];
    final availableCrops =
        YemenCrops.crops.where((c) => !c.isPerennial).toList();

    final prioritizeSoilHealth =
        preferences['prioritizeSoilHealth'] as bool? ?? true;
    final includeNitrogenFixers =
        preferences['includeNitrogenFixers'] as bool? ?? true;

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
      Crop? selectedCrop;

      if (includeNitrogenFixers && i % 3 == 1) {
        selectedCrop = availableCrops
            .where((c) =>
                c.family == CropFamily.fabaceae &&
                !usedFamilies.contains(c.family))
            .firstOrNull;
      }

      selectedCrop ??= availableCrops
              .where((c) => !usedFamilies.contains(c.family))
              .firstOrNull ??
          availableCrops.first;

      usedFamilies.add(selectedCrop.family);
      if (usedFamilies.length > 3) {
        usedFamilies.removeAt(0);
      }

      DateTime? plantingDate;
      DateTime? harvestDate;

      if (selectedCrop.season == 'Winter') {
        plantingDate = DateTime(currentYear + i, 11, 1);
        harvestDate =
            plantingDate.add(Duration(days: selectedCrop.growingDays));
      } else if (selectedCrop.season == 'Spring') {
        plantingDate = DateTime(currentYear + i, 3, 15);
        harvestDate =
            plantingDate.add(Duration(days: selectedCrop.growingDays));
      } else if (selectedCrop.season == 'Summer') {
        plantingDate = DateTime(currentYear + i, 5, 1);
        harvestDate =
            plantingDate.add(Duration(days: selectedCrop.growingDays));
      }

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

  CompatibilityScore _computeLocalCompatibility(Crop crop1, Crop crop2) {
    double score = 1.0;
    String level;
    String reason;
    String reasonAr;

    if (crop1.family == crop2.family) {
      score = 0.2;
      level = 'Avoid';
      reason = 'Same crop family - increases disease and pest pressure';
      reasonAr = 'نفس الفصيلة - يزيد من خطر الأمراض والآفات';
    } else if (crop1.family == CropFamily.fabaceae &&
        _isHeavyFeeder(crop2.family)) {
      score = 0.95;
      level = 'Excellent';
      reason = 'Legume fixes nitrogen for next heavy feeder crop';
      reasonAr = 'البقوليات تثبت النيتروجين للمحصول التالي';
    } else if (_isHeavyFeeder(crop1.family) &&
        crop2.family == CropFamily.fabaceae) {
      score = 0.95;
      level = 'Excellent';
      reason = 'Heavy feeder benefits from nitrogen fixed by legumes';
      reasonAr = 'المحصول المستهلك يستفيد من النيتروجين المثبت';
    } else if (_isLightFeeder(crop1.family) && _isHeavyFeeder(crop2.family)) {
      score = 0.75;
      level = 'Good';
      reason = 'Light feeder gives soil time to recover';
      reasonAr = 'المحصول الخفيف يعطي التربة وقت للتعافي';
    } else {
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

  List<SoilHealth> _computeLocalSoilHealthTrend() {
    final currentYear = DateTime.now().year;
    final trend = <SoilHealth>[];

    for (int i = 4; i >= 0; i--) {
      final baseYear = currentYear - i;
      final improvement = (4 - i) * 3.0;

      trend.add(SoilHealth(
        nitrogen:
            (60 + improvement + Random().nextDouble() * 5).clamp(0, 100),
        phosphorus:
            (55 + improvement + Random().nextDouble() * 5).clamp(0, 100),
        potassium:
            (58 + improvement + Random().nextDouble() * 5).clamp(0, 100),
        organicMatter:
            (45 + improvement + Random().nextDouble() * 5).clamp(0, 100),
        ph: 6.8 + Random().nextDouble() * 0.3,
        waterRetention:
            (50 + improvement + Random().nextDouble() * 5).clamp(0, 100),
        measuredAt: DateTime(baseYear, 6, 15),
      ));
    }

    return trend;
  }

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

    if (crop.family == CropFamily.fabaceae) {
      nitrogenChange = 15;
    } else if (familyInfo.nutrientDemands[0] == 'High') {
      nitrogenChange = -15;
    } else if (familyInfo.nutrientDemands[0] == 'Medium') {
      nitrogenChange = -8;
    } else {
      nitrogenChange = -3;
    }

    if (familyInfo.nutrientDemands[1] == 'High') {
      phosphorusChange = -5;
    } else if (familyInfo.nutrientDemands[1] == 'Medium') {
      phosphorusChange = -3;
    } else {
      phosphorusChange = -1;
    }

    if (familyInfo.nutrientDemands[2] == 'High') {
      potassiumChange = -8;
    } else if (familyInfo.nutrientDemands[2] == 'Medium') {
      potassiumChange = -5;
    } else {
      potassiumChange = -2;
    }

    organicMatterChange = 2;

    if (prioritizeSoilHealth) {
      organicMatterChange += 1;
    }

    return SoilHealth(
      nitrogen: (before.nitrogen + nitrogenChange).clamp(0, 100),
      phosphorus: (before.phosphorus + phosphorusChange).clamp(0, 100),
      potassium: (before.potassium + potassiumChange).clamp(0, 100),
      organicMatter:
          (before.organicMatter + organicMatterChange).clamp(0, 100),
      ph: before.ph,
      waterRetention:
          (before.waterRetention + organicMatterChange * 0.5).clamp(0, 100),
      measuredAt: DateTime.now(),
    );
  }

  bool _isHeavyFeeder(CropFamily family) {
    final info = CropFamilyInfo.familyData[family]!;
    return info.nutrientDemands[0] == 'High';
  }

  bool _isLightFeeder(CropFamily family) {
    final info = CropFamilyInfo.familyData[family]!;
    return info.nutrientDemands[0] == 'Low';
  }
}
