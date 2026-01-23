import 'package:flutter/foundation.dart';

/// Crop Family Enumeration - 15 major plant families
enum CropFamily {
  solanaceae, // Nightshades: tomatoes, potatoes, peppers, eggplants
  fabaceae, // Legumes: beans, peas, lentils, alfalfa, fava beans
  poaceae, // Grasses: wheat, corn, sorghum, rice, barley
  brassicaceae, // Crucifers: cabbage, broccoli, cauliflower, radish
  cucurbitaceae, // Cucurbits: cucumber, squash, melon, pumpkin
  amaranthaceae, // Amaranths: beets, spinach, chard, quinoa
  apiaceae, // Umbellifers: carrots, celery, parsley, fennel
  alliaceae, // Alliums: onion, garlic, leeks, shallots
  asteraceae, // Composites: lettuce, sunflower, artichoke
  malvaceae, // Mallows: cotton, okra, hibiscus
  convolvulaceae, // Morning glories: sweet potato
  rubiaceae, // Coffee family: coffee (qahwa/بن)
  celastraceae, // Qat family: qat (قات)
  rosaceae, // Rose family: strawberries, apples
  lamiaceae, // Mint family: basil, mint, oregano
}

/// Crop Family Information
class CropFamilyInfo {
  final CropFamily family;
  final String nameEn;
  final String nameAr;
  final List<String> commonCrops;
  final List<String> commonCropsAr;
  final List<String> nutrientDemands; // High, Medium, Low for N, P, K
  final int rotationYears; // Recommended years before replanting same family

  const CropFamilyInfo({
    required this.family,
    required this.nameEn,
    required this.nameAr,
    required this.commonCrops,
    required this.commonCropsAr,
    required this.nutrientDemands,
    required this.rotationYears,
  });

  static const Map<CropFamily, CropFamilyInfo> familyData = {
    CropFamily.solanaceae: CropFamilyInfo(
      family: CropFamily.solanaceae,
      nameEn: 'Nightshades',
      nameAr: 'الباذنجانيات',
      commonCrops: ['Tomato', 'Potato', 'Pepper', 'Eggplant'],
      commonCropsAr: ['طماطم', 'بطاطس', 'فلفل', 'باذنجان'],
      nutrientDemands: ['High', 'High', 'High'],
      rotationYears: 3,
    ),
    CropFamily.fabaceae: CropFamilyInfo(
      family: CropFamily.fabaceae,
      nameEn: 'Legumes',
      nameAr: 'البقوليات',
      commonCrops: ['Fava Beans', 'Lentils', 'Peas', 'Alfalfa'],
      commonCropsAr: ['فول', 'عدس', 'بازلاء', 'برسيم'],
      nutrientDemands: ['Low', 'Medium', 'Medium'], // Fixes nitrogen
      rotationYears: 2,
    ),
    CropFamily.poaceae: CropFamilyInfo(
      family: CropFamily.poaceae,
      nameEn: 'Grasses',
      nameAr: 'النجيليات',
      commonCrops: ['Wheat', 'Sorghum', 'Corn', 'Barley'],
      commonCropsAr: ['قمح', 'ذرة رفيعة', 'ذرة', 'شعير'],
      nutrientDemands: ['High', 'Medium', 'High'],
      rotationYears: 2,
    ),
    CropFamily.brassicaceae: CropFamilyInfo(
      family: CropFamily.brassicaceae,
      nameEn: 'Crucifers',
      nameAr: 'الصليبيات',
      commonCrops: ['Cabbage', 'Broccoli', 'Cauliflower', 'Radish'],
      commonCropsAr: ['ملفوف', 'بروكلي', 'قرنبيط', 'فجل'],
      nutrientDemands: ['High', 'Medium', 'High'],
      rotationYears: 3,
    ),
    CropFamily.cucurbitaceae: CropFamilyInfo(
      family: CropFamily.cucurbitaceae,
      nameEn: 'Cucurbits',
      nameAr: 'القرعيات',
      commonCrops: ['Cucumber', 'Squash', 'Melon', 'Watermelon'],
      commonCropsAr: ['خيار', 'كوسة', 'شمام', 'بطيخ'],
      nutrientDemands: ['High', 'Medium', 'High'],
      rotationYears: 3,
    ),
    CropFamily.amaranthaceae: CropFamilyInfo(
      family: CropFamily.amaranthaceae,
      nameEn: 'Amaranths',
      nameAr: 'القطيفيات',
      commonCrops: ['Beet', 'Spinach', 'Chard'],
      commonCropsAr: ['شمندر', 'سبانخ', 'سلق'],
      nutrientDemands: ['Medium', 'Medium', 'High'],
      rotationYears: 2,
    ),
    CropFamily.apiaceae: CropFamilyInfo(
      family: CropFamily.apiaceae,
      nameEn: 'Umbellifers',
      nameAr: 'الخيميات',
      commonCrops: ['Carrot', 'Celery', 'Parsley'],
      commonCropsAr: ['جزر', 'كرفس', 'بقدونس'],
      nutrientDemands: ['Medium', 'Medium', 'Medium'],
      rotationYears: 2,
    ),
    CropFamily.alliaceae: CropFamilyInfo(
      family: CropFamily.alliaceae,
      nameEn: 'Alliums',
      nameAr: 'الثومیات',
      commonCrops: ['Onion', 'Garlic', 'Leek'],
      commonCropsAr: ['بصل', 'ثوم', 'كراث'],
      nutrientDemands: ['Medium', 'Medium', 'High'],
      rotationYears: 3,
    ),
    CropFamily.asteraceae: CropFamilyInfo(
      family: CropFamily.asteraceae,
      nameEn: 'Composites',
      nameAr: 'النجميات',
      commonCrops: ['Lettuce', 'Sunflower', 'Artichoke'],
      commonCropsAr: ['خس', 'عباد الشمس', 'خرشوف'],
      nutrientDemands: ['Medium', 'Medium', 'Medium'],
      rotationYears: 2,
    ),
    CropFamily.malvaceae: CropFamilyInfo(
      family: CropFamily.malvaceae,
      nameEn: 'Mallows',
      nameAr: 'الخبازيات',
      commonCrops: ['Cotton', 'Okra', 'Hibiscus'],
      commonCropsAr: ['قطن', 'بامية', 'كركديه'],
      nutrientDemands: ['High', 'High', 'High'],
      rotationYears: 3,
    ),
    CropFamily.convolvulaceae: CropFamilyInfo(
      family: CropFamily.convolvulaceae,
      nameEn: 'Morning Glories',
      nameAr: 'العليقيات',
      commonCrops: ['Sweet Potato'],
      commonCropsAr: ['بطاطا حلوة'],
      nutrientDemands: ['Medium', 'Medium', 'High'],
      rotationYears: 3,
    ),
    CropFamily.rubiaceae: CropFamilyInfo(
      family: CropFamily.rubiaceae,
      nameEn: 'Coffee Family',
      nameAr: 'الفوية',
      commonCrops: ['Coffee'],
      commonCropsAr: ['بن'],
      nutrientDemands: ['Medium', 'Medium', 'Medium'],
      rotationYears: 0, // Perennial - not typically rotated
    ),
    CropFamily.celastraceae: CropFamilyInfo(
      family: CropFamily.celastraceae,
      nameEn: 'Qat Family',
      nameAr: 'القاتيات',
      commonCrops: ['Qat'],
      commonCropsAr: ['قات'],
      nutrientDemands: ['Medium', 'Medium', 'Medium'],
      rotationYears: 0, // Perennial - not typically rotated
    ),
    CropFamily.rosaceae: CropFamilyInfo(
      family: CropFamily.rosaceae,
      nameEn: 'Rose Family',
      nameAr: 'الورديات',
      commonCrops: ['Strawberry', 'Apple'],
      commonCropsAr: ['فراولة', 'تفاح'],
      nutrientDemands: ['Medium', 'Medium', 'High'],
      rotationYears: 4,
    ),
    CropFamily.lamiaceae: CropFamilyInfo(
      family: CropFamily.lamiaceae,
      nameEn: 'Mint Family',
      nameAr: 'الشفويات',
      commonCrops: ['Basil', 'Mint', 'Oregano'],
      commonCropsAr: ['ريحان', 'نعناع', 'زعتر'],
      nutrientDemands: ['Low', 'Low', 'Medium'],
      rotationYears: 2,
    ),
  };
}

/// Crop information for rotation planning
class Crop {
  final String id;
  final String nameEn;
  final String nameAr;
  final CropFamily family;
  final int growingDays; // Days to maturity
  final String season; // Spring, Summer, Fall, Winter
  final bool isPerennial;

  const Crop({
    required this.id,
    required this.nameEn,
    required this.nameAr,
    required this.family,
    required this.growingDays,
    required this.season,
    this.isPerennial = false,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'nameEn': nameEn,
        'nameAr': nameAr,
        'family': family.name,
        'growingDays': growingDays,
        'season': season,
        'isPerennial': isPerennial,
      };

  factory Crop.fromJson(Map<String, dynamic> json) => Crop(
        id: json['id'] as String,
        nameEn: json['nameEn'] as String,
        nameAr: json['nameAr'] as String,
        family: CropFamily.values.firstWhere(
          (f) => f.name == json['family'],
          orElse: () => CropFamily.poaceae,
        ),
        growingDays: json['growingDays'] as int,
        season: json['season'] as String,
        isPerennial: json['isPerennial'] as bool? ?? false,
      );
}

/// Yemen-specific crops
class YemenCrops {
  static const List<Crop> crops = [
    Crop(
      id: 'wheat',
      nameEn: 'Wheat',
      nameAr: 'قمح',
      family: CropFamily.poaceae,
      growingDays: 120,
      season: 'Winter',
    ),
    Crop(
      id: 'sorghum',
      nameEn: 'Sorghum',
      nameAr: 'ذرة رفيعة',
      family: CropFamily.poaceae,
      growingDays: 100,
      season: 'Summer',
    ),
    Crop(
      id: 'coffee',
      nameEn: 'Coffee',
      nameAr: 'بن',
      family: CropFamily.rubiaceae,
      growingDays: 365,
      season: 'Perennial',
      isPerennial: true,
    ),
    Crop(
      id: 'qat',
      nameEn: 'Qat',
      nameAr: 'قات',
      family: CropFamily.celastraceae,
      growingDays: 365,
      season: 'Perennial',
      isPerennial: true,
    ),
    Crop(
      id: 'tomato',
      nameEn: 'Tomato',
      nameAr: 'طماطم',
      family: CropFamily.solanaceae,
      growingDays: 90,
      season: 'Spring',
    ),
    Crop(
      id: 'onion',
      nameEn: 'Onion',
      nameAr: 'بصل',
      family: CropFamily.alliaceae,
      growingDays: 110,
      season: 'Winter',
    ),
    Crop(
      id: 'fava_beans',
      nameEn: 'Fava Beans',
      nameAr: 'فول',
      family: CropFamily.fabaceae,
      growingDays: 90,
      season: 'Winter',
    ),
  ];
}

/// Compatibility score between two crops
class CompatibilityScore {
  final Crop crop1;
  final Crop crop2;
  final double score; // 0.0 to 1.0
  final String level; // Excellent, Good, Fair, Poor, Avoid
  final String reason;
  final String reasonAr;

  const CompatibilityScore({
    required this.crop1,
    required this.crop2,
    required this.score,
    required this.level,
    required this.reason,
    required this.reasonAr,
  });

  bool get isGood => score >= 0.7;
  bool get isFair => score >= 0.5 && score < 0.7;
  bool get isPoor => score < 0.5;

  Map<String, dynamic> toJson() => {
        'crop1': crop1.toJson(),
        'crop2': crop2.toJson(),
        'score': score,
        'level': level,
        'reason': reason,
        'reasonAr': reasonAr,
      };
}

/// Soil health indicators
class SoilHealth {
  final double nitrogen; // 0-100
  final double phosphorus; // 0-100
  final double potassium; // 0-100
  final double organicMatter; // 0-100
  final double ph; // 0-14
  final double waterRetention; // 0-100
  final DateTime measuredAt;

  const SoilHealth({
    required this.nitrogen,
    required this.phosphorus,
    required this.potassium,
    required this.organicMatter,
    required this.ph,
    required this.waterRetention,
    required this.measuredAt,
  });

  double get overallScore =>
      (nitrogen + phosphorus + potassium + organicMatter + waterRetention) /
      5.0;

  String get healthLevel {
    if (overallScore >= 80) return 'Excellent';
    if (overallScore >= 60) return 'Good';
    if (overallScore >= 40) return 'Fair';
    return 'Poor';
  }

  Map<String, dynamic> toJson() => {
        'nitrogen': nitrogen,
        'phosphorus': phosphorus,
        'potassium': potassium,
        'organicMatter': organicMatter,
        'ph': ph,
        'waterRetention': waterRetention,
        'measuredAt': measuredAt.toIso8601String(),
        'overallScore': overallScore,
        'healthLevel': healthLevel,
      };

  factory SoilHealth.fromJson(Map<String, dynamic> json) => SoilHealth(
        nitrogen: (json['nitrogen'] as num).toDouble(),
        phosphorus: (json['phosphorus'] as num).toDouble(),
        potassium: (json['potassium'] as num).toDouble(),
        organicMatter: (json['organicMatter'] as num).toDouble(),
        ph: (json['ph'] as num).toDouble(),
        waterRetention: (json['waterRetention'] as num).toDouble(),
        measuredAt: DateTime.parse(json['measuredAt'] as String),
      );
}

/// Crop rotation for a specific year
class RotationYear {
  final int year;
  final String season;
  final Crop? crop;
  final SoilHealth? soilHealthBefore;
  final SoilHealth? soilHealthAfter;
  final DateTime? plantingDate;
  final DateTime? harvestDate;
  final double? yieldAmount;
  final String? notes;

  const RotationYear({
    required this.year,
    required this.season,
    this.crop,
    this.soilHealthBefore,
    this.soilHealthAfter,
    this.plantingDate,
    this.harvestDate,
    this.yieldAmount,
    this.notes,
  });

  bool get isPlanned => crop != null;
  bool get isCompleted => harvestDate != null;
  bool get isCurrent {
    final now = DateTime.now();
    if (plantingDate != null && harvestDate != null) {
      return now.isAfter(plantingDate!) && now.isBefore(harvestDate!);
    }
    return false;
  }

  Map<String, dynamic> toJson() => {
        'year': year,
        'season': season,
        'crop': crop?.toJson(),
        'soilHealthBefore': soilHealthBefore?.toJson(),
        'soilHealthAfter': soilHealthAfter?.toJson(),
        'plantingDate': plantingDate?.toIso8601String(),
        'harvestDate': harvestDate?.toIso8601String(),
        'yieldAmount': yieldAmount,
        'notes': notes,
      };

  factory RotationYear.fromJson(Map<String, dynamic> json) => RotationYear(
        year: json['year'] as int,
        season: json['season'] as String,
        crop: json['crop'] != null
            ? Crop.fromJson(json['crop'] as Map<String, dynamic>)
            : null,
        soilHealthBefore: json['soilHealthBefore'] != null
            ? SoilHealth.fromJson(json['soilHealthBefore'] as Map<String, dynamic>)
            : null,
        soilHealthAfter: json['soilHealthAfter'] != null
            ? SoilHealth.fromJson(json['soilHealthAfter'] as Map<String, dynamic>)
            : null,
        plantingDate: json['plantingDate'] != null
            ? DateTime.parse(json['plantingDate'] as String)
            : null,
        harvestDate: json['harvestDate'] != null
            ? DateTime.parse(json['harvestDate'] as String)
            : null,
        yieldAmount: json['yieldAmount'] as double?,
        notes: json['notes'] as String?,
      );

  RotationYear copyWith({
    int? year,
    String? season,
    Crop? crop,
    SoilHealth? soilHealthBefore,
    SoilHealth? soilHealthAfter,
    DateTime? plantingDate,
    DateTime? harvestDate,
    double? yieldAmount,
    String? notes,
  }) {
    return RotationYear(
      year: year ?? this.year,
      season: season ?? this.season,
      crop: crop ?? this.crop,
      soilHealthBefore: soilHealthBefore ?? this.soilHealthBefore,
      soilHealthAfter: soilHealthAfter ?? this.soilHealthAfter,
      plantingDate: plantingDate ?? this.plantingDate,
      harvestDate: harvestDate ?? this.harvestDate,
      yieldAmount: yieldAmount ?? this.yieldAmount,
      notes: notes ?? this.notes,
    );
  }
}

/// Complete rotation plan for a field
class RotationPlan {
  final String id;
  final String fieldId;
  final String fieldName;
  final List<RotationYear> rotationYears;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? preferences;

  const RotationPlan({
    required this.id,
    required this.fieldId,
    required this.fieldName,
    required this.rotationYears,
    required this.createdAt,
    required this.updatedAt,
    this.preferences,
  });

  int get totalYears => rotationYears.length;

  List<RotationYear> get pastRotations => rotationYears
      .where((r) => r.harvestDate != null && r.harvestDate!.isBefore(DateTime.now()))
      .toList();

  RotationYear? get currentRotation => rotationYears.firstWhere(
        (r) => r.isCurrent,
        orElse: () => rotationYears.first,
      );

  List<RotationYear> get futureRotations => rotationYears
      .where((r) =>
          r.plantingDate == null || r.plantingDate!.isAfter(DateTime.now()))
      .toList();

  List<CropFamily> get familiesUsed =>
      rotationYears
          .where((r) => r.crop != null)
          .map((r) => r.crop!.family)
          .toSet()
          .toList();

  Map<String, dynamic> toJson() => {
        'id': id,
        'fieldId': fieldId,
        'fieldName': fieldName,
        'rotationYears': rotationYears.map((r) => r.toJson()).toList(),
        'createdAt': createdAt.toIso8601String(),
        'updatedAt': updatedAt.toIso8601String(),
        'preferences': preferences,
      };

  factory RotationPlan.fromJson(Map<String, dynamic> json) => RotationPlan(
        id: json['id'] as String,
        fieldId: json['fieldId'] as String,
        fieldName: json['fieldName'] as String,
        rotationYears: (json['rotationYears'] as List)
            .map((r) => RotationYear.fromJson(r as Map<String, dynamic>))
            .toList(),
        createdAt: DateTime.parse(json['createdAt'] as String),
        updatedAt: DateTime.parse(json['updatedAt'] as String),
        preferences: json['preferences'] as Map<String, dynamic>?,
      );
}

/// Crop recommendation for a specific field and year
class CropRecommendation {
  final Crop crop;
  final double suitabilityScore; // 0-100
  final List<String> reasons;
  final List<String> reasonsAr;
  final String? warning;
  final String? warningAr;

  const CropRecommendation({
    required this.crop,
    required this.suitabilityScore,
    required this.reasons,
    required this.reasonsAr,
    this.warning,
    this.warningAr,
  });

  bool get isHighlySuitable => suitabilityScore >= 80;
  bool get isSuitable => suitabilityScore >= 60;
  bool get hasWarning => warning != null;

  Map<String, dynamic> toJson() => {
        'crop': crop.toJson(),
        'suitabilityScore': suitabilityScore,
        'reasons': reasons,
        'reasonsAr': reasonsAr,
        'warning': warning,
        'warningAr': warningAr,
      };
}
