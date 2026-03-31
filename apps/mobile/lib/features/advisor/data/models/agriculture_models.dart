/// Agriculture Domain Models - نماذج المجال الزراعي
///
/// Contains: soil analysis, water quality, FAO standards, GDD, BBCH, SSNM
/// Separated from fertilizer_models.dart to avoid interfering with
/// freezed code generation (build_runner).
library;

import 'fertilizer_models.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Extended Soil Analysis - تحليل تربة موسع
// ═══════════════════════════════════════════════════════════════════════════

/// Extended soil analysis with all parameters
/// تحليل تربة موسع - matching backend shared/soil_testing/models.py
class ExtendedSoilAnalysis {
  final double ph;
  final double nitrogen; // mg/kg
  final double phosphorus; // mg/kg
  final double potassium; // mg/kg
  final double organicMatter; // %
  final String soilType;
  final String soilTypeAr;
  final double electricalConductivity; // EC, dS/m
  final double cec; // meq/100g
  final double sandPercent; // %
  final double siltPercent; // %
  final double clayPercent; // %
  final double calcium; // mg/kg
  final double magnesium; // mg/kg
  final double sulfur; // mg/kg
  final double sodium; // meq/L
  final double iron; // mg/kg
  final double zinc; // mg/kg
  final double manganese; // mg/kg
  final double boron; // mg/kg

  const ExtendedSoilAnalysis({
    required this.ph,
    required this.nitrogen,
    required this.phosphorus,
    required this.potassium,
    this.organicMatter = 0,
    this.soilType = '',
    this.soilTypeAr = '',
    this.electricalConductivity = 0,
    this.cec = 0,
    this.sandPercent = 0,
    this.siltPercent = 0,
    this.clayPercent = 0,
    this.calcium = 0,
    this.magnesium = 0,
    this.sulfur = 0,
    this.sodium = 0,
    this.iron = 0,
    this.zinc = 0,
    this.manganese = 0,
    this.boron = 0,
  });

  SoilAnalysis toBasic() => SoilAnalysis(
        ph: ph,
        nitrogen: nitrogen,
        phosphorus: phosphorus,
        potassium: potassium,
        organicMatter: organicMatter,
        soilType: soilType,
        soilTypeAr: soilTypeAr,
      );

  factory ExtendedSoilAnalysis.fromJson(Map<String, dynamic> json) {
    return ExtendedSoilAnalysis(
      ph: (json['ph'] as num?)?.toDouble() ?? 7.0,
      nitrogen: (json['nitrogen'] as num?)?.toDouble() ?? 0,
      phosphorus: (json['phosphorus'] as num?)?.toDouble() ?? 0,
      potassium: (json['potassium'] as num?)?.toDouble() ?? 0,
      organicMatter: (json['organic_matter'] as num?)?.toDouble() ?? 0,
      soilType: json['soil_type'] as String? ?? '',
      soilTypeAr: json['soil_type_ar'] as String? ?? '',
      electricalConductivity: (json['ec'] as num?)?.toDouble() ?? 0,
      cec: (json['cec'] as num?)?.toDouble() ?? 0,
      sandPercent: (json['sand_percent'] as num?)?.toDouble() ?? 0,
      siltPercent: (json['silt_percent'] as num?)?.toDouble() ?? 0,
      clayPercent: (json['clay_percent'] as num?)?.toDouble() ?? 0,
      calcium: (json['calcium'] as num?)?.toDouble() ?? 0,
      magnesium: (json['magnesium'] as num?)?.toDouble() ?? 0,
      sulfur: (json['sulfur'] as num?)?.toDouble() ?? 0,
      sodium: (json['sodium'] as num?)?.toDouble() ?? 0,
      iron: (json['iron'] as num?)?.toDouble() ?? 0,
      zinc: (json['zinc'] as num?)?.toDouble() ?? 0,
      manganese: (json['manganese'] as num?)?.toDouble() ?? 0,
      boron: (json['boron'] as num?)?.toDouble() ?? 0,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Soil Analysis Validator - التحقق من صحة تحليل التربة
// ═══════════════════════════════════════════════════════════════════════════

class SoilAnalysisValidator {
  static const phMin = 0.0, phMax = 14.0;
  static const nMin = 0.0, nMax = 2000.0;
  static const pMin = 0.0, pMax = 500.0;
  static const kMin = 0.0, kMax = 1000.0;
  static const ecMin = 0.0, ecMax = 50.0;

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
    if (v == null) return null;
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
    return errors;
  }

  static List<String> validateExtended(ExtendedSoilAnalysis a) {
    final errors = validateAll(a.toBasic());
    final ec = validateEC(a.electricalConductivity);
    if (ec != null) errors.add(ec);
    final tex = validateTexturePercent(a.sandPercent, a.siltPercent, a.clayPercent);
    if (tex != null) errors.add(tex);
    return errors;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Water Quality Analysis - تحليل جودة المياه
// ═══════════════════════════════════════════════════════════════════════════

/// Newton's method sqrt
double _sqrtSafe(double x) {
  if (x <= 0) return 0;
  double g = x;
  for (int i = 0; i < 15; i++) {
    g = (g + x / g) / 2;
  }
  return g;
}

class WaterQualityAnalysis {
  final double ph;
  final double ec; // dS/m
  final double tds; // mg/L
  final double sar;
  final double sodium; // meq/L
  final double calcium; // meq/L
  final double magnesium; // meq/L
  final double chloride; // meq/L
  final double bicarbonate; // meq/L
  final double sulfate; // meq/L
  final double nitrate; // mg/L
  final double boron; // mg/L
  final String source;
  final String sourceAr;
  final DateTime? testDate;

  const WaterQualityAnalysis({
    required this.ph,
    required this.ec,
    this.tds = 0, this.sar = 0, this.sodium = 0, this.calcium = 0,
    this.magnesium = 0, this.chloride = 0, this.bicarbonate = 0,
    this.sulfate = 0, this.nitrate = 0, this.boron = 0,
    this.source = '', this.sourceAr = '', this.testDate,
  });

  /// SAR = Na / sqrt((Ca+Mg)/2)
  double get calculatedSAR {
    final caMg = calcium + magnesium;
    if (caMg <= 0) return 0;
    return sodium / _sqrtSafe(caMg / 2);
  }

  String get irrigationClass {
    if (ec <= 0.7) return 'ممتازة';
    if (ec <= 2.0) return 'جيدة';
    if (ec <= 3.0) return 'مقبولة';
    if (ec <= 5.0) return 'مشكوك فيها';
    return 'غير صالحة';
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
      testDate: json['test_date'] != null ? DateTime.tryParse(json['test_date'] as String) : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'ph': ph, 'ec': ec, 'tds': tds, 'sar': sar,
    'sodium': sodium, 'calcium': calcium, 'magnesium': magnesium,
    'chloride': chloride, 'bicarbonate': bicarbonate, 'sulfate': sulfate,
    'nitrate': nitrate, 'boron': boron, 'source': source,
    'source_ar': sourceAr, 'test_date': testDate?.toIso8601String(),
  };
}

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
}

// ═══════════════════════════════════════════════════════════════════════════
// FAO Standards - معايير FAO
// ═══════════════════════════════════════════════════════════════════════════

class CropSalinityTolerance {
  final String cropCode;
  final String nameAr;
  final double ecThreshold;
  final double yieldDeclinePercent;

  const CropSalinityTolerance({
    required this.cropCode, required this.nameAr,
    required this.ecThreshold, required this.yieldDeclinePercent,
  });

  double yieldReduction(double soilEC) {
    if (soilEC <= ecThreshold) return 0;
    return ((soilEC - ecThreshold) * yieldDeclinePercent).clamp(0, 100);
  }

  double expectedYieldPercent(double soilEC) => (100 - yieldReduction(soilEC)).clamp(0, 100);

  static const Map<String, CropSalinityTolerance> faoTable = {
    'wheat': CropSalinityTolerance(cropCode: 'wheat', nameAr: 'قمح', ecThreshold: 6.0, yieldDeclinePercent: 7.1),
    'barley': CropSalinityTolerance(cropCode: 'barley', nameAr: 'شعير', ecThreshold: 8.0, yieldDeclinePercent: 5.0),
    'maize': CropSalinityTolerance(cropCode: 'maize', nameAr: 'ذرة', ecThreshold: 1.7, yieldDeclinePercent: 12.0),
    'tomato': CropSalinityTolerance(cropCode: 'tomato', nameAr: 'طماطم', ecThreshold: 2.5, yieldDeclinePercent: 9.9),
    'date_palm': CropSalinityTolerance(cropCode: 'date_palm', nameAr: 'نخيل', ecThreshold: 4.0, yieldDeclinePercent: 3.6),
    'citrus': CropSalinityTolerance(cropCode: 'citrus', nameAr: 'حمضيات', ecThreshold: 1.7, yieldDeclinePercent: 16.0),
    'cotton': CropSalinityTolerance(cropCode: 'cotton', nameAr: 'قطن', ecThreshold: 7.7, yieldDeclinePercent: 5.2),
    'alfalfa': CropSalinityTolerance(cropCode: 'alfalfa', nameAr: 'برسيم حجازي', ecThreshold: 2.0, yieldDeclinePercent: 7.3),
    'onion': CropSalinityTolerance(cropCode: 'onion', nameAr: 'بصل', ecThreshold: 1.2, yieldDeclinePercent: 16.0),
    'potato': CropSalinityTolerance(cropCode: 'potato', nameAr: 'بطاطس', ecThreshold: 1.7, yieldDeclinePercent: 12.0),
  };
}

class FAOWaterClassification {
  static String salinityRisk(double ecW) {
    if (ecW < 0.7) return 'لا يوجد';
    if (ecW <= 3.0) return 'طفيف-متوسط';
    return 'شديد';
  }

  static String chlorideToxicity(double clMeqL) {
    if (clMeqL < 4) return 'لا يوجد';
    if (clMeqL <= 10) return 'طفيف-متوسط';
    return 'شديد';
  }

  static String boronToxicity(double boronMgL) {
    if (boronMgL < 0.7) return 'لا يوجد';
    if (boronMgL <= 3.0) return 'طفيف-متوسط';
    return 'شديد';
  }

  static double calculateRSC(double co3, double hco3, double ca, double mg) {
    return (co3 + hco3) - (ca + mg);
  }

  static String rscClassification(double rsc) {
    if (rsc < 1.25) return 'آمنة';
    if (rsc <= 2.5) return 'هامشية';
    return 'غير صالحة';
  }
}

class NutrientUptakeCoefficients {
  final String cropCode;
  final double nPerTon;
  final double p2o5PerTon;
  final double k2oPerTon;

  const NutrientUptakeCoefficients({
    required this.cropCode, required this.nPerTon,
    required this.p2o5PerTon, required this.k2oPerTon,
  });

  ({double nKgHa, double p2o5KgHa, double k2oKgHa}) calculateFertilizerNeed({
    required double targetYield,
    double soilN = 0, double soilP = 0, double soilK = 0,
    double nEfficiency = 0.40, double pEfficiency = 0.20, double kEfficiency = 0.50,
  }) {
    return (
      nKgHa: nEfficiency > 0 ? ((targetYield * nPerTon - soilN) / nEfficiency).clamp(0, 500) : 0,
      p2o5KgHa: pEfficiency > 0 ? ((targetYield * p2o5PerTon - soilP) / pEfficiency).clamp(0, 200) : 0,
      k2oKgHa: kEfficiency > 0 ? ((targetYield * k2oPerTon - soilK) / kEfficiency).clamp(0, 300) : 0,
    );
  }

  static const Map<String, NutrientUptakeCoefficients> table = {
    'wheat': NutrientUptakeCoefficients(cropCode: 'wheat', nPerTon: 27, p2o5PerTon: 11, k2oPerTon: 22),
    'barley': NutrientUptakeCoefficients(cropCode: 'barley', nPerTon: 23, p2o5PerTon: 10, k2oPerTon: 20),
    'maize': NutrientUptakeCoefficients(cropCode: 'maize', nPerTon: 22, p2o5PerTon: 9, k2oPerTon: 20),
    'tomato': NutrientUptakeCoefficients(cropCode: 'tomato', nPerTon: 2.7, p2o5PerTon: 0.9, k2oPerTon: 4.0),
    'potato': NutrientUptakeCoefficients(cropCode: 'potato', nPerTon: 5.5, p2o5PerTon: 1.8, k2oPerTon: 9.0),
    'cotton': NutrientUptakeCoefficients(cropCode: 'cotton', nPerTon: 55, p2o5PerTon: 22, k2oPerTon: 45),
    'alfalfa': NutrientUptakeCoefficients(cropCode: 'alfalfa', nPerTon: 27, p2o5PerTon: 6, k2oPerTon: 25),
  };
}

class GDDCropConfig {
  final String cropCode;
  final double baseTemp;
  final double upperTemp;
  final double gddToMaturity;

  const GDDCropConfig({
    required this.cropCode, required this.baseTemp,
    required this.upperTemp, required this.gddToMaturity,
  });

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
    'alfalfa': GDDCropConfig(cropCode: 'alfalfa', baseTemp: 5, upperTemp: 30, gddToMaturity: 350),
    'date_palm': GDDCropConfig(cropCode: 'date_palm', baseTemp: 18, upperTemp: 45, gddToMaturity: 0),
  };
}

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
