/// Crop Data Model
/// نموذج بيانات المحصول
///
/// Based on SAHOOL Unified Crop Catalog
/// يطابق كتالوج المحاصيل الموحد في السيرفر
library;

/// تصنيفات المحاصيل الرئيسية
enum CropCategory {
  cereals('cereals', 'الحبوب'),
  legumes('legumes', 'البقوليات'),
  vegetables('vegetables', 'الخضروات'),
  fruits('fruits', 'الفواكه'),
  oilseeds('oilseeds', 'البذور الزيتية'),
  fiber('fiber', 'الألياف'),
  sugar('sugar', 'السكريات'),
  stimulants('stimulants', 'المنبهات'),
  spices('spices', 'التوابل والأعشاب'),
  fodder('fodder', 'الأعلاف'),
  tubers('tubers', 'الدرنيات');

  final String code;
  final String nameAr;

  const CropCategory(this.code, this.nameAr);
}

/// طريقة النمو
enum GrowthHabit {
  annual('annual', 'حولي'),
  perennial('perennial', 'معمر'),
  biennial('biennial', 'ثنائي الحول');

  final String code;
  final String nameAr;

  const GrowthHabit(this.code, this.nameAr);
}

/// متطلبات المياه
enum WaterRequirement {
  veryLow('very_low', 'منخفضة جداً'),
  low('low', 'منخفضة'),
  medium('medium', 'متوسطة'),
  high('high', 'عالية'),
  veryHigh('very_high', 'عالية جداً');

  final String code;
  final String nameAr;

  const WaterRequirement(this.code, this.nameAr);
}

/// نموذج المحصول الكامل
class Crop {
  /// رمز المحصول (FAO-based)
  final String code;

  /// الاسم بالإنجليزية
  final String nameEn;

  /// الاسم بالعربية
  final String nameAr;

  /// الاسم العلمي
  final String scientificName;

  /// التصنيف
  final CropCategory category;

  /// طريقة النمو
  final GrowthHabit growthHabit;

  /// مدة الموسم (أيام)
  final int growingSeasonDays;

  /// درجة الحرارة المثلى (الصغرى)
  final double optimalTempMin;

  /// درجة الحرارة المثلى (الكبرى)
  final double optimalTempMax;

  /// متطلبات المياه
  final WaterRequirement waterRequirement;

  /// الإنتاجية الأساسية (طن/هكتار)
  final double baseYieldTonHa;

  /// وحدة القياس
  final String yieldUnit;

  /// المناطق اليمنية المناسبة
  final List<String>? yemenRegions;

  /// الأصناف المحلية
  final List<String>? localVarieties;

  /// معامل المحصول الأولي
  final double? kcIni;

  /// معامل المحصول الأقصى
  final double? kcMid;

  /// معامل المحصول النهائي
  final double? kcEnd;

  /// السعر (USD/طن)
  final double? priceUsdPerTon;

  /// أيقونة المحصول (اختياري - للعرض في التطبيق)
  final String? icon;

  // ═══════════════════════════════════════════════════════════════════
  // Extended Agricultural Fields - حقول زراعية متقدمة
  // Matching backend shared/crop_rotation/models.py + FAO standards
  // ═══════════════════════════════════════════════════════════════════

  /// العائلة النباتية (مهمة لدورة المحاصيل)
  final CropFamily? family;

  /// معدل البذور (كجم/هكتار) - FAO recommended
  final double? seedRateKgPerHa;

  /// معدل البذور (كجم/فدان) - للشرق الأوسط
  final double? seedRateKgPerFeddan;

  /// عمق الزراعة (سم)
  final double? plantingDepthCm;

  /// مسافة بين الصفوف (سم)
  final double? rowSpacingCm;

  /// مسافة بين النباتات (سم)
  final double? plantSpacingCm;

  /// حرارة الأساس لـ GDD (°C)
  final double? baseTemperature;

  /// GDD للنضج (درجة-يوم)
  final double? gddToMaturity;

  /// تحمل الملوحة ECe (dS/m) - FAO-29
  final double? salinityThresholdEC;

  /// نسبة فقدان المحصول بالملوحة (%/dS/m)
  final double? salinityYieldDeclinePercent;

  /// مراحل النمو الرئيسية (BBCH scale)
  final List<GrowthStageInfo>? growthStages;

  /// الاحتياج المائي الكلي (مم/موسم)
  final double? waterRequirementMm;

  /// متطلبات NPK (كجم/هكتار) - N
  final double? nitrogenRequirementKgHa;

  /// متطلبات NPK (كجم/هكتار) - P2O5
  final double? phosphorusRequirementKgHa;

  /// متطلبات NPK (كجم/هكتار) - K2O
  final double? potassiumRequirementKgHa;

  const Crop({
    required this.code,
    required this.nameEn,
    required this.nameAr,
    required this.scientificName,
    required this.category,
    required this.growthHabit,
    required this.growingSeasonDays,
    required this.optimalTempMin,
    required this.optimalTempMax,
    required this.waterRequirement,
    required this.baseYieldTonHa,
    this.yieldUnit = 'ton/ha',
    this.yemenRegions,
    this.localVarieties,
    this.kcIni,
    this.kcMid,
    this.kcEnd,
    this.priceUsdPerTon,
    this.icon,
    this.family,
    this.seedRateKgPerHa,
    this.seedRateKgPerFeddan,
    this.plantingDepthCm,
    this.rowSpacingCm,
    this.plantSpacingCm,
    this.baseTemperature,
    this.gddToMaturity,
    this.salinityThresholdEC,
    this.salinityYieldDeclinePercent,
    this.growthStages,
    this.waterRequirementMm,
    this.nitrogenRequirementKgHa,
    this.phosphorusRequirementKgHa,
    this.potassiumRequirementKgHa,
  });

  /// إنشاء من JSON
  factory Crop.fromJson(Map<String, dynamic> json) {
    return Crop(
      code: json['code'] as String,
      nameEn: json['name_en'] as String,
      nameAr: json['name_ar'] as String,
      scientificName: json['scientific_name'] as String,
      category: _parseCropCategory(json['category'] as String),
      growthHabit: _parseGrowthHabit(json['growth_habit'] as String),
      growingSeasonDays: json['growing_season_days'] as int,
      optimalTempMin: (json['optimal_temp_min'] as num).toDouble(),
      optimalTempMax: (json['optimal_temp_max'] as num).toDouble(),
      waterRequirement: _parseWaterRequirement(json['water_requirement'] as String),
      baseYieldTonHa: (json['base_yield_ton_ha'] as num).toDouble(),
      yieldUnit: json['yield_unit'] as String? ?? 'ton/ha',
      yemenRegions: (json['yemen_regions'] as List?)?.map((e) => e.toString()).toList(),
      localVarieties: (json['local_varieties'] as List?)?.map((e) => e.toString()).toList(),
      kcIni: (json['kc_ini'] as num?)?.toDouble(),
      kcMid: (json['kc_mid'] as num?)?.toDouble(),
      kcEnd: (json['kc_end'] as num?)?.toDouble(),
      priceUsdPerTon: (json['price_usd_per_ton'] as num?)?.toDouble(),
      icon: json['icon'] as String?,
    );
  }

  /// تحويل إلى JSON
  Map<String, dynamic> toJson() => {
        'code': code,
        'name_en': nameEn,
        'name_ar': nameAr,
        'scientific_name': scientificName,
        'category': category.code,
        'growth_habit': growthHabit.code,
        'growing_season_days': growingSeasonDays,
        'optimal_temp_min': optimalTempMin,
        'optimal_temp_max': optimalTempMax,
        'water_requirement': waterRequirement.code,
        'base_yield_ton_ha': baseYieldTonHa,
        'yield_unit': yieldUnit,
        'yemen_regions': yemenRegions,
        'local_varieties': localVarieties,
        'kc_ini': kcIni,
        'kc_mid': kcMid,
        'kc_end': kcEnd,
        'price_usd_per_ton': priceUsdPerTon,
        'icon': icon,
      };

  /// نسخة معدلة
  Crop copyWith({
    String? code,
    String? nameEn,
    String? nameAr,
    String? scientificName,
    CropCategory? category,
    GrowthHabit? growthHabit,
    int? growingSeasonDays,
    double? optimalTempMin,
    double? optimalTempMax,
    WaterRequirement? waterRequirement,
    double? baseYieldTonHa,
    String? yieldUnit,
    List<String>? yemenRegions,
    List<String>? localVarieties,
    double? kcIni,
    double? kcMid,
    double? kcEnd,
    double? priceUsdPerTon,
    String? icon,
  }) {
    return Crop(
      code: code ?? this.code,
      nameEn: nameEn ?? this.nameEn,
      nameAr: nameAr ?? this.nameAr,
      scientificName: scientificName ?? this.scientificName,
      category: category ?? this.category,
      growthHabit: growthHabit ?? this.growthHabit,
      growingSeasonDays: growingSeasonDays ?? this.growingSeasonDays,
      optimalTempMin: optimalTempMin ?? this.optimalTempMin,
      optimalTempMax: optimalTempMax ?? this.optimalTempMax,
      waterRequirement: waterRequirement ?? this.waterRequirement,
      baseYieldTonHa: baseYieldTonHa ?? this.baseYieldTonHa,
      yieldUnit: yieldUnit ?? this.yieldUnit,
      yemenRegions: yemenRegions ?? this.yemenRegions,
      localVarieties: localVarieties ?? this.localVarieties,
      kcIni: kcIni ?? this.kcIni,
      kcMid: kcMid ?? this.kcMid,
      kcEnd: kcEnd ?? this.kcEnd,
      priceUsdPerTon: priceUsdPerTon ?? this.priceUsdPerTon,
      icon: icon ?? this.icon,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Crop && runtimeType == other.runtimeType && code == other.code;

  @override
  int get hashCode => code.hashCode;

  @override
  String toString() => 'Crop($code: $nameAr / $nameEn)';
}

// Helper functions for parsing enums

CropCategory _parseCropCategory(String value) {
  return CropCategory.values.firstWhere(
    (e) => e.code == value,
    orElse: () => CropCategory.vegetables,
  );
}

GrowthHabit _parseGrowthHabit(String value) {
  return GrowthHabit.values.firstWhere(
    (e) => e.code == value,
    orElse: () => GrowthHabit.annual,
  );
}

WaterRequirement _parseWaterRequirement(String value) {
  return WaterRequirement.values.firstWhere(
    (e) => e.code == value,
    orElse: () => WaterRequirement.medium,
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// العائلات النباتية - Crop Families
// Matches backend shared/crop_rotation/models.py CropFamily
// ═══════════════════════════════════════════════════════════════════════════

/// العائلات النباتية الرئيسية للدورة الزراعية
enum CropFamily {
  poaceae('poaceae', 'النجيليات', 'Grasses'), // قمح، شعير، ذرة، أرز
  fabaceae('fabaceae', 'البقوليات', 'Legumes'), // فول، عدس، برسيم
  solanaceae('solanaceae', 'الباذنجانيات', 'Nightshades'), // طماطم، فلفل، باذنجان
  cucurbitaceae('cucurbitaceae', 'القرعيات', 'Cucurbits'), // بطيخ، خيار، قرع
  brassicaceae('brassicaceae', 'الصليبيات', 'Brassicas'), // ملفوف، قرنبيط
  apiaceae('apiaceae', 'الخيميات', 'Umbellifers'), // جزر، كرفس
  liliaceae('liliaceae', 'الزنبقيات', 'Lilies'), // بصل، ثوم
  chenopodiaceae('chenopodiaceae', 'الرمراميات', 'Goosefoots'), // بنجر، سبانخ
  arecaceae('arecaceae', 'النخيليات', 'Palms'), // نخيل التمر
  malvaceae('malvaceae', 'الخبازيات', 'Mallows'), // قطن، بامية
  other('other', 'أخرى', 'Other');

  final String code;
  final String nameAr;
  final String nameEn;

  const CropFamily(this.code, this.nameAr, this.nameEn);
}

/// مرحلة نمو المحصول (BBCH Scale)
/// Based on BBCH Monograph: Growth stages of mono- and dicotyledonous plants
class GrowthStageInfo {
  /// رمز BBCH (00-99)
  final int bbchCode;

  /// اسم المرحلة بالعربية
  final String nameAr;

  /// اسم المرحلة بالإنجليزية
  final String nameEn;

  /// بداية GDD لهذه المرحلة
  final double gddStart;

  /// نهاية GDD لهذه المرحلة
  final double gddEnd;

  /// معامل المحصول (Kc) في هذه المرحلة
  final double kc;

  /// العمليات الموصى بها في هذه المرحلة
  final List<String> recommendedActions;

  /// الآفات الشائعة في هذه المرحلة
  final List<String> commonPests;

  const GrowthStageInfo({
    required this.bbchCode,
    required this.nameAr,
    required this.nameEn,
    required this.gddStart,
    required this.gddEnd,
    required this.kc,
    this.recommendedActions = const [],
    this.commonPests = const [],
  });

  factory GrowthStageInfo.fromJson(Map<String, dynamic> json) {
    return GrowthStageInfo(
      bbchCode: json['bbch_code'] as int? ?? 0,
      nameAr: json['name_ar'] as String? ?? '',
      nameEn: json['name_en'] as String? ?? '',
      gddStart: (json['gdd_start'] as num?)?.toDouble() ?? 0,
      gddEnd: (json['gdd_end'] as num?)?.toDouble() ?? 0,
      kc: (json['kc'] as num?)?.toDouble() ?? 1.0,
      recommendedActions: (json['recommended_actions'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      commonPests: (json['common_pests'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() => {
        'bbch_code': bbchCode,
        'name_ar': nameAr,
        'name_en': nameEn,
        'gdd_start': gddStart,
        'gdd_end': gddEnd,
        'kc': kc,
        'recommended_actions': recommendedActions,
        'common_pests': commonPests,
      };
}

// ═══════════════════════════════════════════════════════════════════════════
// كتالوج البذور - Seed Rate Catalog
// FAO recommendations + regional adaptations for Middle East
// ═══════════════════════════════════════════════════════════════════════════

/// معدلات البذور القياسية (كجم/هكتار)
class SeedRateCatalog {
  static const Map<String, SeedRateInfo> rates = {
    'wheat': SeedRateInfo(
      cropCode: 'wheat',
      rateKgPerHa: 120,
      rateRangeMin: 100,
      rateRangeMax: 150,
      thousandSeedWeightG: 35,
      germinationPercent: 85,
      notes: 'Irrigated wheat in Yemen/Saudi',
      notesAr: 'قمح مروي في اليمن/السعودية',
    ),
    'barley': SeedRateInfo(
      cropCode: 'barley',
      rateKgPerHa: 100,
      rateRangeMin: 80,
      rateRangeMax: 130,
      thousandSeedWeightG: 40,
      germinationPercent: 85,
      notes: 'Rainfed barley in highland areas',
      notesAr: 'شعير بعلي في المناطق المرتفعة',
    ),
    'maize': SeedRateInfo(
      cropCode: 'maize',
      rateKgPerHa: 25,
      rateRangeMin: 20,
      rateRangeMax: 30,
      thousandSeedWeightG: 300,
      germinationPercent: 90,
      notes: 'Hybrid maize under irrigation',
      notesAr: 'ذرة هجين تحت الري',
    ),
    'tomato': SeedRateInfo(
      cropCode: 'tomato',
      rateKgPerHa: 0.3,
      rateRangeMin: 0.2,
      rateRangeMax: 0.5,
      thousandSeedWeightG: 3,
      germinationPercent: 85,
      notes: 'Transplanted tomato (seedling)',
      notesAr: 'طماطم مشتلة (شتلات)',
    ),
    'date_palm': SeedRateInfo(
      cropCode: 'date_palm',
      rateKgPerHa: 0, // planted as offshoots
      rateRangeMin: 0,
      rateRangeMax: 0,
      thousandSeedWeightG: 0,
      germinationPercent: 0,
      notes: '100-150 offshoots/ha, spacing 8-10m',
      notesAr: '100-150 فسيلة/هكتار، مسافة 8-10م',
    ),
    'alfalfa': SeedRateInfo(
      cropCode: 'alfalfa',
      rateKgPerHa: 25,
      rateRangeMin: 20,
      rateRangeMax: 30,
      thousandSeedWeightG: 2,
      germinationPercent: 80,
      notes: 'Perennial alfalfa under irrigation',
      notesAr: 'برسيم حجازي معمر تحت الري',
    ),
    'onion': SeedRateInfo(
      cropCode: 'onion',
      rateKgPerHa: 8,
      rateRangeMin: 6,
      rateRangeMax: 10,
      thousandSeedWeightG: 4,
      germinationPercent: 75,
      notes: 'Direct seeding or transplant',
      notesAr: 'زراعة مباشرة أو شتل',
    ),
    'potato': SeedRateInfo(
      cropCode: 'potato',
      rateKgPerHa: 2500,
      rateRangeMin: 2000,
      rateRangeMax: 3000,
      thousandSeedWeightG: 0, // tuber-based
      germinationPercent: 95,
      notes: 'Seed tubers 30-50g each, spacing 25-30cm',
      notesAr: 'درنات بذرية 30-50جم، مسافة 25-30سم',
    ),
    'cotton': SeedRateInfo(
      cropCode: 'cotton',
      rateKgPerHa: 25,
      rateRangeMin: 20,
      rateRangeMax: 35,
      thousandSeedWeightG: 80,
      germinationPercent: 80,
      notes: 'Upland cotton, irrigated',
      notesAr: 'قطن مرتفع، مروي',
    ),
    'sorghum': SeedRateInfo(
      cropCode: 'sorghum',
      rateKgPerHa: 10,
      rateRangeMin: 8,
      rateRangeMax: 15,
      thousandSeedWeightG: 25,
      germinationPercent: 85,
      notes: 'Grain sorghum, traditional variety',
      notesAr: 'ذرة رفيعة حبوب، صنف محلي',
    ),
  };
}

/// معلومات معدل البذور
class SeedRateInfo {
  final String cropCode;
  final double rateKgPerHa;
  final double rateRangeMin;
  final double rateRangeMax;
  final double thousandSeedWeightG;
  final double germinationPercent;
  final String notes;
  final String notesAr;

  const SeedRateInfo({
    required this.cropCode,
    required this.rateKgPerHa,
    required this.rateRangeMin,
    required this.rateRangeMax,
    required this.thousandSeedWeightG,
    required this.germinationPercent,
    required this.notes,
    required this.notesAr,
  });

  /// حساب كمية البذور المطلوبة لمساحة محددة
  double calculateSeedQuantity(double areaHa) => rateKgPerHa * areaHa;

  /// حساب كمية البذور بالفدان (4200 م²)
  double get rateKgPerFeddan => rateKgPerHa * 0.42;
}
