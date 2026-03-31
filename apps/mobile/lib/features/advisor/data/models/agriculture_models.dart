/// Agriculture Domain Models - نماذج المجال الزراعي
///
/// Standalone agriculture domain models (no freezed dependencies).
/// Contains: soil analysis, water quality, FAO standards, GDD, BBCH, SSNM
library;

// ═══════════════════════════════════════════════════════════════════════════
// Extended Soil Analysis - تحليل تربة موسع
// ═══════════════════════════════════════════════════════════════════════════

class ExtendedSoilAnalysis {
  final double ph, nitrogen, phosphorus, potassium;
  final double organicMatter;
  final String soilType, soilTypeAr;
  final double electricalConductivity, cec;
  final double sandPercent, siltPercent, clayPercent;
  final double calcium, magnesium, sulfur, sodium;
  final double iron, zinc, manganese, boron;

  const ExtendedSoilAnalysis({
    required this.ph, required this.nitrogen,
    required this.phosphorus, required this.potassium,
    this.organicMatter = 0, this.soilType = '', this.soilTypeAr = '',
    this.electricalConductivity = 0, this.cec = 0,
    this.sandPercent = 0, this.siltPercent = 0, this.clayPercent = 0,
    this.calcium = 0, this.magnesium = 0, this.sulfur = 0, this.sodium = 0,
    this.iron = 0, this.zinc = 0, this.manganese = 0, this.boron = 0,
  });

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
// Validators - التحقق من الصحة
// ═══════════════════════════════════════════════════════════════════════════

class SoilAnalysisValidator {
  static String? validatePh(double? v) =>
      v == null ? 'مطلوب' : (v < 0 || v > 14) ? 'pH: 0-14' : null;
  static String? validateNitrogen(double? v) =>
      v == null ? 'مطلوب' : (v < 0 || v > 2000) ? 'N: 0-2000 mg/kg' : null;
  static String? validatePhosphorus(double? v) =>
      v == null ? 'مطلوب' : (v < 0 || v > 500) ? 'P: 0-500 mg/kg' : null;
  static String? validatePotassium(double? v) =>
      v == null ? 'مطلوب' : (v < 0 || v > 1000) ? 'K: 0-1000 mg/kg' : null;
  static String? validateEC(double? v) =>
      v != null && (v < 0 || v > 50) ? 'EC: 0-50 dS/m' : null;
  static String? validateTexturePercent(double? sand, double? silt, double? clay) {
    if (sand == null && silt == null && clay == null) return null;
    final total = (sand ?? 0) + (silt ?? 0) + (clay ?? 0);
    return (total > 0 && (total < 99 || total > 101)) ? 'مجموع القوام = 100%' : null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Water Quality - جودة المياه
// ═══════════════════════════════════════════════════════════════════════════

double _sqrtSafe(double x) {
  if (x <= 0) return 0;
  double g = x;
  for (int i = 0; i < 15; i++) { g = (g + x / g) / 2; }
  return g;
}

class WaterQualityAnalysis {
  final double ph, ec, tds, sar;
  final double sodium, calcium, magnesium;
  final double chloride, bicarbonate, sulfate, nitrate, boron;
  final String source, sourceAr;
  final DateTime? testDate;

  const WaterQualityAnalysis({
    required this.ph, required this.ec,
    this.tds = 0, this.sar = 0, this.sodium = 0, this.calcium = 0,
    this.magnesium = 0, this.chloride = 0, this.bicarbonate = 0,
    this.sulfate = 0, this.nitrate = 0, this.boron = 0,
    this.source = '', this.sourceAr = '', this.testDate,
  });

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

  factory WaterQualityAnalysis.fromJson(Map<String, dynamic> json) =>
      WaterQualityAnalysis(
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

  Map<String, dynamic> toJson() => {
    'ph': ph, 'ec': ec, 'tds': tds, 'sar': sar,
    'sodium': sodium, 'calcium': calcium, 'magnesium': magnesium,
    'chloride': chloride, 'bicarbonate': bicarbonate, 'sulfate': sulfate,
    'nitrate': nitrate, 'boron': boron, 'source': source,
    'source_ar': sourceAr, 'test_date': testDate?.toIso8601String(),
  };
}

class WaterQualityValidator {
  static String? validatePh(double? v) =>
      v == null ? 'مطلوب' : (v < 0 || v > 14) ? 'pH: 0-14' : null;
  static String? validateEC(double? v) =>
      v == null ? 'مطلوب' : (v < 0 || v > 30) ? 'EC: 0-30 dS/m' : null;
}

// ═══════════════════════════════════════════════════════════════════════════
// FAO Standards - معايير FAO
// ═══════════════════════════════════════════════════════════════════════════

class CropSalinityTolerance {
  final String cropCode, nameAr;
  final double ecThreshold, yieldDeclinePercent;

  const CropSalinityTolerance({
    required this.cropCode, required this.nameAr,
    required this.ecThreshold, required this.yieldDeclinePercent,
  });

  double yieldReduction(double ec) =>
      ec <= ecThreshold ? 0 : ((ec - ecThreshold) * yieldDeclinePercent).clamp(0, 100);
  double expectedYieldPercent(double ec) => (100 - yieldReduction(ec)).clamp(0, 100);

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
  static String salinityRisk(double ecW) =>
      ecW < 0.7 ? 'لا يوجد' : ecW <= 3.0 ? 'طفيف-متوسط' : 'شديد';
  static String chlorideToxicity(double cl) =>
      cl < 4 ? 'لا يوجد' : cl <= 10 ? 'طفيف-متوسط' : 'شديد';
  static String boronToxicity(double b) =>
      b < 0.7 ? 'لا يوجد' : b <= 3.0 ? 'طفيف-متوسط' : 'شديد';
  static double calculateRSC(double co3, double hco3, double ca, double mg) =>
      (co3 + hco3) - (ca + mg);
  static String rscClassification(double rsc) =>
      rsc < 1.25 ? 'آمنة' : rsc <= 2.5 ? 'هامشية' : 'غير صالحة';
}

class NutrientUptakeCoefficients {
  final String cropCode;
  final double nPerTon, p2o5PerTon, k2oPerTon;

  const NutrientUptakeCoefficients({
    required this.cropCode, required this.nPerTon,
    required this.p2o5PerTon, required this.k2oPerTon,
  });

  ({double nKgHa, double p2o5KgHa, double k2oKgHa}) calculateFertilizerNeed({
    required double targetYield,
    double soilN = 0, double soilP = 0, double soilK = 0,
    double nEfficiency = 0.40, double pEfficiency = 0.20, double kEfficiency = 0.50,
  }) => (
    nKgHa: nEfficiency > 0 ? ((targetYield * nPerTon - soilN) / nEfficiency).clamp(0, 500) : 0,
    p2o5KgHa: pEfficiency > 0 ? ((targetYield * p2o5PerTon - soilP) / pEfficiency).clamp(0, 200) : 0,
    k2oKgHa: kEfficiency > 0 ? ((targetYield * k2oPerTon - soilK) / kEfficiency).clamp(0, 300) : 0,
  );

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
  final double baseTemp, upperTemp, gddToMaturity;

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
