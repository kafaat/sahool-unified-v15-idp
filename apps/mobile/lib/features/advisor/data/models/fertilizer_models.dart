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

// ═══════════════════════════════════════════════════════════════════════════
// FAO Standards Data - بيانات معايير منظمة الأغذية والزراعة
// FAO Paper 29 (Ayers & Westcot, 1985) + FAO-56 (Allen et al., 1998)
// ═══════════════════════════════════════════════════════════════════════════

/// FAO-29 Crop Salinity Tolerance Table
/// جدول تحمل المحاصيل للملوحة (FAO-29)
class CropSalinityTolerance {
  final String cropCode;
  final String nameAr;
  final double ecThreshold; // ECe dS/m - عتبة بدء فقدان المحصول
  final double yieldDeclinePercent; // %/dS/m - نسبة الفقدان لكل وحدة

  const CropSalinityTolerance({
    required this.cropCode,
    required this.nameAr,
    required this.ecThreshold,
    required this.yieldDeclinePercent,
  });

  /// حساب نسبة فقدان المحصول عند ملوحة معينة
  double yieldReduction(double soilEC) {
    if (soilEC <= ecThreshold) return 0;
    return ((soilEC - ecThreshold) * yieldDeclinePercent).clamp(0, 100);
  }

  /// حساب المحصول المتوقع كنسبة مئوية
  double expectedYieldPercent(double soilEC) => (100 - yieldReduction(soilEC)).clamp(0, 100);

  static const Map<String, CropSalinityTolerance> faoTable = {
    'wheat': CropSalinityTolerance(cropCode: 'wheat', nameAr: 'قمح', ecThreshold: 6.0, yieldDeclinePercent: 7.1),
    'barley': CropSalinityTolerance(cropCode: 'barley', nameAr: 'شعير', ecThreshold: 8.0, yieldDeclinePercent: 5.0),
    'maize': CropSalinityTolerance(cropCode: 'maize', nameAr: 'ذرة', ecThreshold: 1.7, yieldDeclinePercent: 12.0),
    'sorghum': CropSalinityTolerance(cropCode: 'sorghum', nameAr: 'ذرة رفيعة', ecThreshold: 6.8, yieldDeclinePercent: 16.0),
    'rice': CropSalinityTolerance(cropCode: 'rice', nameAr: 'أرز', ecThreshold: 3.0, yieldDeclinePercent: 12.0),
    'tomato': CropSalinityTolerance(cropCode: 'tomato', nameAr: 'طماطم', ecThreshold: 2.5, yieldDeclinePercent: 9.9),
    'date_palm': CropSalinityTolerance(cropCode: 'date_palm', nameAr: 'نخيل', ecThreshold: 4.0, yieldDeclinePercent: 3.6),
    'citrus': CropSalinityTolerance(cropCode: 'citrus', nameAr: 'حمضيات', ecThreshold: 1.7, yieldDeclinePercent: 16.0),
    'cotton': CropSalinityTolerance(cropCode: 'cotton', nameAr: 'قطن', ecThreshold: 7.7, yieldDeclinePercent: 5.2),
    'alfalfa': CropSalinityTolerance(cropCode: 'alfalfa', nameAr: 'برسيم حجازي', ecThreshold: 2.0, yieldDeclinePercent: 7.3),
    'onion': CropSalinityTolerance(cropCode: 'onion', nameAr: 'بصل', ecThreshold: 1.2, yieldDeclinePercent: 16.0),
    'potato': CropSalinityTolerance(cropCode: 'potato', nameAr: 'بطاطس', ecThreshold: 1.7, yieldDeclinePercent: 12.0),
    'pepper': CropSalinityTolerance(cropCode: 'pepper', nameAr: 'فلفل', ecThreshold: 1.5, yieldDeclinePercent: 14.0),
    'cucumber': CropSalinityTolerance(cropCode: 'cucumber', nameAr: 'خيار', ecThreshold: 2.5, yieldDeclinePercent: 13.0),
    'lettuce': CropSalinityTolerance(cropCode: 'lettuce', nameAr: 'خس', ecThreshold: 1.3, yieldDeclinePercent: 13.0),
  };
}

/// FAO-29 Water Quality Classification for Irrigation
/// تصنيف جودة المياه للري (FAO-29)
class FAOWaterClassification {
  /// تصنيف خطر الملوحة
  static String salinityRisk(double ecW) {
    if (ecW < 0.7) return 'لا يوجد'; // None
    if (ecW <= 3.0) return 'طفيف-متوسط'; // Slight-Moderate
    return 'شديد'; // Severe
  }

  /// تصنيف خطر الصوديوم (SAR + EC)
  static String sodiumRisk(double sar, double ecW) {
    if (sar < 3 && ecW > 0.7) return 'لا يوجد';
    if (sar < 9 && ecW > 0.3) return 'طفيف-متوسط';
    return 'شديد';
  }

  /// تصنيف سمية الكلور
  static String chlorideToxicity(double clMeqL) {
    if (clMeqL < 4) return 'لا يوجد';
    if (clMeqL <= 10) return 'طفيف-متوسط';
    return 'شديد';
  }

  /// تصنيف سمية البورون
  static String boronToxicity(double boronMgL) {
    if (boronMgL < 0.7) return 'لا يوجد';
    if (boronMgL <= 3.0) return 'طفيف-متوسط';
    return 'شديد';
  }

  /// حساب كربونات الصوديوم المتبقية RSC
  static double calculateRSC(double co3, double hco3, double ca, double mg) {
    return (co3 + hco3) - (ca + mg);
  }

  /// تصنيف RSC
  static String rscClassification(double rsc) {
    if (rsc < 1.25) return 'آمنة'; // Safe
    if (rsc <= 2.5) return 'هامشية'; // Marginal
    return 'غير صالحة'; // Not suitable
  }
}

/// Nutrient Uptake Coefficients (kg nutrient per ton of grain)
/// معاملات امتصاص العناصر (كجم/طن حبوب) - FAO + IPNI
class NutrientUptakeCoefficients {
  final String cropCode;
  final double nPerTon; // kg N per ton grain
  final double p2o5PerTon; // kg P2O5 per ton grain
  final double k2oPerTon; // kg K2O per ton grain

  const NutrientUptakeCoefficients({
    required this.cropCode,
    required this.nPerTon,
    required this.p2o5PerTon,
    required this.k2oPerTon,
  });

  /// حساب الاحتياج لهدف محصول محدد (SSNM)
  /// targetYield: طن/هكتار
  /// soilN/P/K: المتاح في التربة (كجم/هكتار)
  /// efficiency: كفاءة استخدام السماد (0-1)
  ({double nKgHa, double p2o5KgHa, double k2oKgHa}) calculateFertilizerNeed({
    required double targetYield,
    double soilN = 0,
    double soilP = 0,
    double soilK = 0,
    double nEfficiency = 0.40,
    double pEfficiency = 0.20,
    double kEfficiency = 0.50,
  }) {
    final nDemand = targetYield * nPerTon;
    final pDemand = targetYield * p2o5PerTon;
    final kDemand = targetYield * k2oPerTon;

    return (
      nKgHa: nEfficiency > 0 ? ((nDemand - soilN) / nEfficiency).clamp(0, 500) : 0,
      p2o5KgHa: pEfficiency > 0 ? ((pDemand - soilP) / pEfficiency).clamp(0, 200) : 0,
      k2oKgHa: kEfficiency > 0 ? ((kDemand - soilK) / kEfficiency).clamp(0, 300) : 0,
    );
  }

  static const Map<String, NutrientUptakeCoefficients> table = {
    'wheat': NutrientUptakeCoefficients(cropCode: 'wheat', nPerTon: 27, p2o5PerTon: 11, k2oPerTon: 22),
    'barley': NutrientUptakeCoefficients(cropCode: 'barley', nPerTon: 23, p2o5PerTon: 10, k2oPerTon: 20),
    'maize': NutrientUptakeCoefficients(cropCode: 'maize', nPerTon: 22, p2o5PerTon: 9, k2oPerTon: 20),
    'rice': NutrientUptakeCoefficients(cropCode: 'rice', nPerTon: 20, p2o5PerTon: 9, k2oPerTon: 22),
    'sorghum': NutrientUptakeCoefficients(cropCode: 'sorghum', nPerTon: 25, p2o5PerTon: 10, k2oPerTon: 20),
    'tomato': NutrientUptakeCoefficients(cropCode: 'tomato', nPerTon: 2.7, p2o5PerTon: 0.9, k2oPerTon: 4.0),
    'potato': NutrientUptakeCoefficients(cropCode: 'potato', nPerTon: 5.5, p2o5PerTon: 1.8, k2oPerTon: 9.0),
    'onion': NutrientUptakeCoefficients(cropCode: 'onion', nPerTon: 2.5, p2o5PerTon: 1.0, k2oPerTon: 2.0),
    'cotton': NutrientUptakeCoefficients(cropCode: 'cotton', nPerTon: 55, p2o5PerTon: 22, k2oPerTon: 45),
    'alfalfa': NutrientUptakeCoefficients(cropCode: 'alfalfa', nPerTon: 27, p2o5PerTon: 6, k2oPerTon: 25),
  };
}

/// GDD Base Temperatures by Crop
/// درجات الحرارة الأساسية لحساب وحدات الحرارة المتراكمة
class GDDCropConfig {
  final String cropCode;
  final double baseTemp; // °C
  final double upperTemp; // °C
  final double gddToMaturity;

  const GDDCropConfig({
    required this.cropCode,
    required this.baseTemp,
    required this.upperTemp,
    required this.gddToMaturity,
  });

  /// حساب GDD يومي (طريقة المتوسط البسيط مع حدود)
  double dailyGDD(double tMax, double tMin) {
    final adjMax = tMax.clamp(baseTemp, upperTemp);
    final adjMin = tMin.clamp(baseTemp, upperTemp);
    return ((adjMax + adjMin) / 2 - baseTemp).clamp(0, double.infinity);
  }

  static const Map<String, GDDCropConfig> table = {
    'wheat_winter': GDDCropConfig(cropCode: 'wheat_winter', baseTemp: 0, upperTemp: 30, gddToMaturity: 2100),
    'wheat_spring': GDDCropConfig(cropCode: 'wheat_spring', baseTemp: 5, upperTemp: 30, gddToMaturity: 1500),
    'barley': GDDCropConfig(cropCode: 'barley', baseTemp: 5, upperTemp: 30, gddToMaturity: 1350),
    'maize': GDDCropConfig(cropCode: 'maize', baseTemp: 10, upperTemp: 30, gddToMaturity: 2500),
    'sorghum': GDDCropConfig(cropCode: 'sorghum', baseTemp: 10, upperTemp: 38, gddToMaturity: 2750),
    'tomato': GDDCropConfig(cropCode: 'tomato', baseTemp: 10, upperTemp: 35, gddToMaturity: 1350),
    'alfalfa': GDDCropConfig(cropCode: 'alfalfa', baseTemp: 5, upperTemp: 30, gddToMaturity: 350), // per cut
    'date_palm': GDDCropConfig(cropCode: 'date_palm', baseTemp: 18, upperTemp: 45, gddToMaturity: 0), // perennial
  };
}

/// BBCH Growth Stages for Wheat (Zadoks cross-reference)
/// مراحل نمو القمح حسب نظام BBCH
class WheatBBCHStages {
  static const List<Map<String, dynamic>> stages = [
    {'bbch': 0, 'zadoks': 0, 'nameEn': 'Germination', 'nameAr': 'الإنبات', 'gddStart': 0, 'gddEnd': 100, 'kc': 0.3},
    {'bbch': 10, 'zadoks': 10, 'nameEn': 'Seedling', 'nameAr': 'البادرة', 'gddStart': 100, 'gddEnd': 200, 'kc': 0.4},
    {'bbch': 20, 'zadoks': 21, 'nameEn': 'Tillering', 'nameAr': 'التفريع', 'gddStart': 200, 'gddEnd': 500, 'kc': 0.7},
    {'bbch': 30, 'zadoks': 30, 'nameEn': 'Stem Elongation', 'nameAr': 'استطالة الساق', 'gddStart': 500, 'gddEnd': 800, 'kc': 0.9},
    {'bbch': 40, 'zadoks': 41, 'nameEn': 'Booting', 'nameAr': 'التبويب', 'gddStart': 800, 'gddEnd': 1000, 'kc': 1.1},
    {'bbch': 50, 'zadoks': 55, 'nameEn': 'Heading', 'nameAr': 'الطرد', 'gddStart': 1000, 'gddEnd': 1200, 'kc': 1.15},
    {'bbch': 60, 'zadoks': 65, 'nameEn': 'Flowering', 'nameAr': 'الإزهار', 'gddStart': 1200, 'gddEnd': 1400, 'kc': 1.15},
    {'bbch': 70, 'zadoks': 73, 'nameEn': 'Grain Fill (Milk)', 'nameAr': 'امتلاء الحبوب (لبني)', 'gddStart': 1400, 'gddEnd': 1600, 'kc': 1.0},
    {'bbch': 80, 'zadoks': 85, 'nameEn': 'Grain Fill (Dough)', 'nameAr': 'امتلاء الحبوب (عجيني)', 'gddStart': 1600, 'gddEnd': 1900, 'kc': 0.7},
    {'bbch': 90, 'zadoks': 92, 'nameEn': 'Ripening', 'nameAr': 'النضج', 'gddStart': 1900, 'gddEnd': 2100, 'kc': 0.3},
  ];
}
