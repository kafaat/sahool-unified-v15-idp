/// Crop Data Model
/// نموذج بيانات المحصول
///
/// Based on SAHOOL Unified Crop Catalog
/// يطابق كتالوج المحاصيل الموحد في السيرفر

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
