/// Fertilizer Recommendation Models
/// نماذج توصيات التسميد
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'fertilizer_models.freezed.dart';
part 'fertilizer_models.g.dart';

/// Soil analysis data
/// بيانات تحليل التربة
@freezed
class SoilAnalysis with _$SoilAnalysis {
  const factory SoilAnalysis({
    required double ph, // 0-14, typical: 4.0-9.0
    required double nitrogen, // mg/kg (ppm), range: 0-2000
    required double phosphorus, // mg/kg (ppm), range: 0-500
    required double potassium, // mg/kg (ppm), range: 0-1000
    @Default(0) double organicMatter, // %, range: 0-20
    @Default('') String soilType,
    @Default('') String soilTypeAr,
    // Extended soil analysis fields (matching backend shared/soil_testing/models.py)
    @Default(0) double electricalConductivity, // EC, dS/m
    @Default(0) double cec, // Cation Exchange Capacity, meq/100g
    @Default(0) double sandPercent, // %, USDA texture triangle
    @Default(0) double siltPercent, // %, USDA texture triangle
    @Default(0) double clayPercent, // %, USDA texture triangle
    @Default(0) double calcium, // Ca, mg/kg
    @Default(0) double magnesium, // Mg, mg/kg
    @Default(0) double sulfur, // S, mg/kg
    @Default(0) double sodium, // Na, meq/L
    @Default(0) double iron, // Fe, mg/kg
    @Default(0) double zinc, // Zn, mg/kg
    @Default(0) double manganese, // Mn, mg/kg
    @Default(0) double boron, // B, mg/kg
  }) = _SoilAnalysis;

  factory SoilAnalysis.fromJson(Map<String, dynamic> json) =>
      _$SoilAnalysisFromJson(json);
}

/// Soil analysis validation helper
/// أداة التحقق من صحة تحليل التربة
class SoilAnalysisValidator {
  static const phMin = 0.0, phMax = 14.0;
  static const nMin = 0.0, nMax = 2000.0;
  static const pMin = 0.0, pMax = 500.0;
  static const kMin = 0.0, kMax = 1000.0;
  static const omMin = 0.0, omMax = 20.0;
  static const ecMin = 0.0, ecMax = 50.0;
  static const cecMin = 0.0, cecMax = 100.0;

  static String? validatePh(double? v) {
    if (v == null) return 'مطلوب';
    if (v < phMin || v > phMax) return 'pH يجب أن يكون بين $phMin-$phMax';
    return null;
  }

  static String? validateNitrogen(double? v) {
    if (v == null) return 'مطلوب';
    if (v < nMin || v > nMax) return 'النيتروجين يجب أن يكون بين $nMin-$nMax mg/kg';
    return null;
  }

  static String? validatePhosphorus(double? v) {
    if (v == null) return 'مطلوب';
    if (v < pMin || v > pMax) return 'الفسفور يجب أن يكون بين $pMin-$pMax mg/kg';
    return null;
  }

  static String? validatePotassium(double? v) {
    if (v == null) return 'مطلوب';
    if (v < kMin || v > kMax) return 'البوتاسيوم يجب أن يكون بين $kMin-$kMax mg/kg';
    return null;
  }

  static String? validateEC(double? v) {
    if (v == null) return null; // optional
    if (v < ecMin || v > ecMax) return 'EC يجب أن يكون بين $ecMin-$ecMax dS/m';
    return null;
  }

  static String? validateTexturePercent(double? sand, double? silt, double? clay) {
    if (sand == null && silt == null && clay == null) return null;
    final total = (sand ?? 0) + (silt ?? 0) + (clay ?? 0);
    if (total > 0 && (total < 99 || total > 101)) {
      return 'مجموع الرمل+الطين+السلت يجب أن يساوي 100%';
    }
    return null;
  }

  static List<String> validateAll(SoilAnalysis a) {
    final errors = <String>[];
    final ph = validatePh(a.ph);
    if (ph != null) errors.add(ph);
    final n = validateNitrogen(a.nitrogen);
    if (n != null) errors.add(n);
    final p = validatePhosphorus(a.phosphorus);
    if (p != null) errors.add(p);
    final k = validatePotassium(a.potassium);
    if (k != null) errors.add(k);
    final ec = validateEC(a.electricalConductivity);
    if (ec != null) errors.add(ec);
    final tex = validateTexturePercent(a.sandPercent, a.siltPercent, a.clayPercent);
    if (tex != null) errors.add(tex);
    return errors;
  }
}

/// Water quality analysis model
/// نموذج تحليل جودة المياه - matching backend shared/water_management/models.py
class WaterQualityAnalysis {
  final double ph; // 0-14
  final double ec; // dS/m - Electrical Conductivity
  final double tds; // mg/L - Total Dissolved Solids
  final double sar; // Sodium Adsorption Ratio
  final double sodium; // Na, meq/L
  final double calcium; // Ca, meq/L
  final double magnesium; // Mg, meq/L
  final double chloride; // Cl, meq/L
  final double bicarbonate; // HCO3, meq/L
  final double sulfate; // SO4, meq/L
  final double nitrate; // mg/L
  final double boron; // mg/L
  final String source; // well, canal, treated_water, etc.
  final String sourceAr;
  final DateTime? testDate;

  const WaterQualityAnalysis({
    required this.ph,
    required this.ec,
    this.tds = 0,
    this.sar = 0,
    this.sodium = 0,
    this.calcium = 0,
    this.magnesium = 0,
    this.chloride = 0,
    this.bicarbonate = 0,
    this.sulfate = 0,
    this.nitrate = 0,
    this.boron = 0,
    this.source = '',
    this.sourceAr = '',
    this.testDate,
  });

  /// Calculate SAR from Na, Ca, Mg
  double get calculatedSAR {
    final caMg = calcium + magnesium;
    if (caMg <= 0) return 0;
    return sodium / (caMg / 2).clamp(0.001, double.infinity);
  }

  /// تصنيف جودة المياه للري
  String get irrigationClass {
    if (ec <= 0.7) return 'ممتازة'; // Excellent
    if (ec <= 2.0) return 'جيدة'; // Good
    if (ec <= 3.0) return 'مقبولة'; // Permissible
    if (ec <= 5.0) return 'مشكوك فيها'; // Doubtful
    return 'غير صالحة'; // Unsuitable
  }

  factory WaterQualityAnalysis.fromJson(Map<String, dynamic> json) {
    return WaterQualityAnalysis(
      ph: (json['ph'] as num?)?.toDouble() ?? 7.0,
      ec: (json['ec'] as num?)?.toDouble() ?? 0,
      tds: (json['tds'] as num?)?.toDouble() ?? 0,
      sar: (json['sar'] as num?)?.toDouble() ?? 0,
      sodium: (json['sodium'] as num?)?.toDouble() ?? 0,
      calcium: (json['calcium'] as num?)?.toDouble() ?? 0,
      magnesium: (json['magnesium'] as num?)?.toDouble() ?? 0,
      chloride: (json['chloride'] as num?)?.toDouble() ?? 0,
      bicarbonate: (json['bicarbonate'] as num?)?.toDouble() ?? 0,
      sulfate: (json['sulfate'] as num?)?.toDouble() ?? 0,
      nitrate: (json['nitrate'] as num?)?.toDouble() ?? 0,
      boron: (json['boron'] as num?)?.toDouble() ?? 0,
      source: json['source'] as String? ?? '',
      sourceAr: json['source_ar'] as String? ?? '',
      testDate: json['test_date'] != null
          ? DateTime.tryParse(json['test_date'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'ph': ph,
        'ec': ec,
        'tds': tds,
        'sar': sar,
        'sodium': sodium,
        'calcium': calcium,
        'magnesium': magnesium,
        'chloride': chloride,
        'bicarbonate': bicarbonate,
        'sulfate': sulfate,
        'nitrate': nitrate,
        'boron': boron,
        'source': source,
        'source_ar': sourceAr,
        'test_date': testDate?.toIso8601String(),
      };
}

/// Water quality validation
class WaterQualityValidator {
  static String? validatePh(double? v) {
    if (v == null) return 'مطلوب';
    if (v < 0 || v > 14) return 'pH يجب أن يكون بين 0-14';
    return null;
  }

  static String? validateEC(double? v) {
    if (v == null) return 'مطلوب';
    if (v < 0 || v > 30) return 'EC يجب أن يكون بين 0-30 dS/m';
    return null;
  }

  static String? validateTDS(double? v) {
    if (v == null) return null;
    if (v < 0 || v > 50000) return 'TDS يجب أن يكون بين 0-50000 mg/L';
    return null;
  }
}

/// Fertilizer recommendation request
/// طلب توصية التسميد
@freezed
class FertilizerRequest with _$FertilizerRequest {
  const factory FertilizerRequest({
    required String cropType,
    required double fieldArea, // hectares
    required SoilAnalysis soilAnalysis,
    required String growthStage,
    @Default('') String governorate,
    @Default('') String irrigationType,
  }) = _FertilizerRequest;

  factory FertilizerRequest.fromJson(Map<String, dynamic> json) =>
      _$FertilizerRequestFromJson(json);
}

/// NPK Recommendation
/// توصية السماد NPK
@freezed
class NpkRecommendation with _$NpkRecommendation {
  const factory NpkRecommendation({
    required double nitrogenKg, // كجم/هكتار
    required double phosphorusKg,
    required double potassiumKg,
    required double totalKgPerHectare,
    required double totalKgForField,
    @Default('') String applicationMethod,
    @Default('') String applicationMethodAr,
    @Default('') String timing,
    @Default('') String timingAr,
  }) = _NpkRecommendation;

  factory NpkRecommendation.fromJson(Map<String, dynamic> json) =>
      _$NpkRecommendationFromJson(json);
}

/// Fertilizer product suggestion
/// اقتراح منتج السماد
@freezed
class FertilizerProduct with _$FertilizerProduct {
  const factory FertilizerProduct({
    required String productId,
    required String name,
    required String nameAr,
    required String npkRatio, // e.g., "15-15-15"
    required double quantityKg,
    @Default(0) double pricePerKg,
    @Default('') String applicationNotes,
    @Default('') String applicationNotesAr,
  }) = _FertilizerProduct;

  factory FertilizerProduct.fromJson(Map<String, dynamic> json) =>
      _$FertilizerProductFromJson(json);
}

/// Complete fertilizer recommendation
/// توصية التسميد الكاملة
@freezed
class FertilizerRecommendation with _$FertilizerRecommendation {
  const factory FertilizerRecommendation({
    required String recommendationId,
    required String fieldId,
    required String cropType,
    required String cropTypeAr,
    required NpkRecommendation npkRecommendation,
    required List<FertilizerProduct> suggestedProducts,
    required String soilHealthStatus,
    required String soilHealthStatusAr,
    @Default([]) List<String> deficiencies,
    @Default([]) List<String> deficienciesAr,
    @Default([]) List<String> warnings,
    @Default([]) List<String> warningsAr,
    required DateTime generatedAt,
    @Default('') String seasonalNote,
    @Default('') String seasonalNoteAr,
  }) = _FertilizerRecommendation;

  factory FertilizerRecommendation.fromJson(Map<String, dynamic> json) =>
      _$FertilizerRecommendationFromJson(json);
}

/// Deficiency symptom
/// أعراض النقص
@freezed
class DeficiencySymptom with _$DeficiencySymptom {
  const factory DeficiencySymptom({
    required String nutrient,
    required String nutrientAr,
    required String severity, // low, medium, high, critical
    required List<String> visualSymptoms,
    required List<String> visualSymptomsAr,
    required String recommendation,
    required String recommendationAr,
    @Default('') String imageUrl,
  }) = _DeficiencySymptom;

  factory DeficiencySymptom.fromJson(Map<String, dynamic> json) =>
      _$DeficiencySymptomFromJson(json);
}

/// Soil interpretation result
/// نتيجة تفسير التربة
@freezed
class SoilInterpretation with _$SoilInterpretation {
  const factory SoilInterpretation({
    required String overallHealth, // excellent, good, fair, poor
    required String overallHealthAr,
    required Map<String, String> nutrientLevels, // nutrient -> level
    required Map<String, String> nutrientLevelsAr,
    required List<String> recommendations,
    required List<String> recommendationsAr,
    required double fertilitySCore, // 0-100
  }) = _SoilInterpretation;

  factory SoilInterpretation.fromJson(Map<String, dynamic> json) =>
      _$SoilInterpretationFromJson(json);
}

/// Available crop types for fertilizer advisor
/// أنواع المحاصيل المتاحة لمستشار التسميد
@freezed
class CropTypeOption with _$CropTypeOption {
  const factory CropTypeOption({
    required String id,
    required String name,
    required String nameAr,
    required String category,
    required String categoryAr,
    @Default([]) List<String> growthStages,
    @Default([]) List<String> growthStagesAr,
  }) = _CropTypeOption;

  factory CropTypeOption.fromJson(Map<String, dynamic> json) =>
      _$CropTypeOptionFromJson(json);
}
