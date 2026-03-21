/// Advisory Context Model
/// نموذج سياق التوصية
///
/// Contains field, weather, crop, and soil data for AI context
library;

import 'package:flutter/foundation.dart';

/// Advisory Context - Data the AI knows about
/// سياق المستشار - البيانات المتاحة للذكاء الاصطناعي
@immutable
class AdvisoryContext {
  /// Field context
  final FieldContext? field;

  /// Weather context
  final WeatherContext? weather;

  /// Crop context
  final CropContext? crop;

  /// Soil context
  final SoilContext? soil;

  /// Historical data context
  final HistoricalContext? history;

  /// Last updated timestamp
  final DateTime? lastUpdated;

  const AdvisoryContext({
    this.field,
    this.weather,
    this.crop,
    this.soil,
    this.history,
    this.lastUpdated,
  });

  factory AdvisoryContext.fromJson(Map<String, dynamic> json) {
    return AdvisoryContext(
      field: json['field'] != null
          ? FieldContext.fromJson(json['field'] as Map<String, dynamic>)
          : null,
      weather: json['weather'] != null
          ? WeatherContext.fromJson(json['weather'] as Map<String, dynamic>)
          : null,
      crop: json['crop'] != null
          ? CropContext.fromJson(json['crop'] as Map<String, dynamic>)
          : null,
      soil: json['soil'] != null
          ? SoilContext.fromJson(json['soil'] as Map<String, dynamic>)
          : null,
      history: json['history'] != null
          ? HistoricalContext.fromJson(json['history'] as Map<String, dynamic>)
          : null,
      lastUpdated: json['last_updated'] != null
          ? DateTime.parse(json['last_updated'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'field': field?.toJson(),
    'weather': weather?.toJson(),
    'crop': crop?.toJson(),
    'soil': soil?.toJson(),
    'history': history?.toJson(),
    'last_updated': lastUpdated?.toIso8601String(),
  };

  /// Check if context has field data
  bool get hasFieldData => field != null;

  /// Check if context has weather data
  bool get hasWeatherData => weather != null;

  /// Check if context has crop data
  bool get hasCropData => crop != null;

  /// Check if context has soil data
  bool get hasSoilData => soil != null;

  /// Get list of available context types
  List<ContextType> get availableContextTypes {
    final types = <ContextType>[];
    if (hasFieldData) types.add(ContextType.field);
    if (hasWeatherData) types.add(ContextType.weather);
    if (hasCropData) types.add(ContextType.crop);
    if (hasSoilData) types.add(ContextType.soil);
    if (history != null) types.add(ContextType.history);
    return types;
  }

  /// Get context completeness percentage
  double get completeness {
    const int total = 5;
    int available = 0;
    if (hasFieldData) available++;
    if (hasWeatherData) available++;
    if (hasCropData) available++;
    if (hasSoilData) available++;
    if (history != null) available++;
    return available / total;
  }

  /// Get context summary in Arabic
  String get summaryAr {
    final parts = <String>[];
    if (hasFieldData) parts.add('معلومات الحقل');
    if (hasWeatherData) parts.add('الطقس');
    if (hasCropData) parts.add('المحصول');
    if (hasSoilData) parts.add('التربة');
    if (history != null) parts.add('السجل التاريخي');
    return parts.isEmpty ? 'لا توجد بيانات' : parts.join('، ');
  }

  AdvisoryContext copyWith({
    FieldContext? field,
    WeatherContext? weather,
    CropContext? crop,
    SoilContext? soil,
    HistoricalContext? history,
    DateTime? lastUpdated,
  }) {
    return AdvisoryContext(
      field: field ?? this.field,
      weather: weather ?? this.weather,
      crop: crop ?? this.crop,
      soil: soil ?? this.soil,
      history: history ?? this.history,
      lastUpdated: lastUpdated ?? this.lastUpdated,
    );
  }
}

/// Context type enum
enum ContextType {
  field,
  weather,
  crop,
  soil,
  history,
}

/// Field Context
/// سياق الحقل
@immutable
class FieldContext {
  final String id;
  final String name;
  final String? nameAr;
  final double? areaHectares;
  final String? irrigationType;
  final String? irrigationTypeAr;
  final double? latitude;
  final double? longitude;
  final String? governorate;
  final String? governorateAr;
  final double? ndvi;
  final DateTime? ndviDate;
  final String? healthStatus;
  final String? healthStatusAr;

  const FieldContext({
    required this.id,
    required this.name,
    this.nameAr,
    this.areaHectares,
    this.irrigationType,
    this.irrigationTypeAr,
    this.latitude,
    this.longitude,
    this.governorate,
    this.governorateAr,
    this.ndvi,
    this.ndviDate,
    this.healthStatus,
    this.healthStatusAr,
  });

  factory FieldContext.fromJson(Map<String, dynamic> json) {
    return FieldContext(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      nameAr: json['name_ar'] as String?,
      areaHectares: (json['area_hectares'] as num?)?.toDouble(),
      irrigationType: json['irrigation_type'] as String?,
      irrigationTypeAr: json['irrigation_type_ar'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      governorate: json['governorate'] as String?,
      governorateAr: json['governorate_ar'] as String?,
      ndvi: (json['ndvi'] as num?)?.toDouble(),
      ndviDate: json['ndvi_date'] != null
          ? DateTime.parse(json['ndvi_date'] as String)
          : null,
      healthStatus: json['health_status'] as String?,
      healthStatusAr: json['health_status_ar'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'name_ar': nameAr,
    'area_hectares': areaHectares,
    'irrigation_type': irrigationType,
    'irrigation_type_ar': irrigationTypeAr,
    'latitude': latitude,
    'longitude': longitude,
    'governorate': governorate,
    'governorate_ar': governorateAr,
    'ndvi': ndvi,
    'ndvi_date': ndviDate?.toIso8601String(),
    'health_status': healthStatus,
    'health_status_ar': healthStatusAr,
  };

  /// Get NDVI health description
  String get ndviHealthAr {
    if (ndvi == null) return 'غير متوفر';
    if (ndvi! >= 0.7) return 'ممتاز';
    if (ndvi! >= 0.5) return 'جيد';
    if (ndvi! >= 0.3) return 'متوسط';
    return 'ضعيف';
  }
}

/// Weather Context
/// سياق الطقس
@immutable
class WeatherContext {
  final double? currentTemperature;
  final double? minTemperature;
  final double? maxTemperature;
  final double? humidity;
  final double? windSpeed;
  final String? windDirection;
  final double? rainfall;
  final double? rainfallProbability;
  final double? evapotranspiration;
  final String? condition;
  final String? conditionAr;
  final List<WeatherForecastDay>? forecast;
  final DateTime? lastUpdated;

  const WeatherContext({
    this.currentTemperature,
    this.minTemperature,
    this.maxTemperature,
    this.humidity,
    this.windSpeed,
    this.windDirection,
    this.rainfall,
    this.rainfallProbability,
    this.evapotranspiration,
    this.condition,
    this.conditionAr,
    this.forecast,
    this.lastUpdated,
  });

  factory WeatherContext.fromJson(Map<String, dynamic> json) {
    return WeatherContext(
      currentTemperature: (json['current_temperature'] as num?)?.toDouble(),
      minTemperature: (json['min_temperature'] as num?)?.toDouble(),
      maxTemperature: (json['max_temperature'] as num?)?.toDouble(),
      humidity: (json['humidity'] as num?)?.toDouble(),
      windSpeed: (json['wind_speed'] as num?)?.toDouble(),
      windDirection: json['wind_direction'] as String?,
      rainfall: (json['rainfall'] as num?)?.toDouble(),
      rainfallProbability: (json['rainfall_probability'] as num?)?.toDouble(),
      evapotranspiration: (json['evapotranspiration'] as num?)?.toDouble(),
      condition: json['condition'] as String?,
      conditionAr: json['condition_ar'] as String?,
      forecast: (json['forecast'] as List?)
          ?.map((e) => WeatherForecastDay.fromJson(e as Map<String, dynamic>))
          .toList(),
      lastUpdated: json['last_updated'] != null
          ? DateTime.parse(json['last_updated'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'current_temperature': currentTemperature,
    'min_temperature': minTemperature,
    'max_temperature': maxTemperature,
    'humidity': humidity,
    'wind_speed': windSpeed,
    'wind_direction': windDirection,
    'rainfall': rainfall,
    'rainfall_probability': rainfallProbability,
    'evapotranspiration': evapotranspiration,
    'condition': condition,
    'condition_ar': conditionAr,
    'forecast': forecast?.map((e) => e.toJson()).toList(),
    'last_updated': lastUpdated?.toIso8601String(),
  };

  /// Get temperature summary
  String get temperatureSummaryAr {
    if (currentTemperature == null) return 'غير متوفر';
    final min = minTemperature?.toStringAsFixed(0) ?? '-';
    final max = maxTemperature?.toStringAsFixed(0) ?? '-';
    return '${currentTemperature!.toStringAsFixed(0)}° ($min°-$max°)';
  }

  /// Check if rain is expected
  bool get isRainExpected {
    return (rainfallProbability ?? 0) > 30 || (rainfall ?? 0) > 0;
  }
}

/// Weather Forecast Day
@immutable
class WeatherForecastDay {
  final DateTime date;
  final double? minTemperature;
  final double? maxTemperature;
  final double? rainfall;
  final double? rainfallProbability;
  final String? condition;
  final String? conditionAr;

  const WeatherForecastDay({
    required this.date,
    this.minTemperature,
    this.maxTemperature,
    this.rainfall,
    this.rainfallProbability,
    this.condition,
    this.conditionAr,
  });

  factory WeatherForecastDay.fromJson(Map<String, dynamic> json) {
    return WeatherForecastDay(
      date: DateTime.parse(json['date'] as String),
      minTemperature: (json['min_temperature'] as num?)?.toDouble(),
      maxTemperature: (json['max_temperature'] as num?)?.toDouble(),
      rainfall: (json['rainfall'] as num?)?.toDouble(),
      rainfallProbability: (json['rainfall_probability'] as num?)?.toDouble(),
      condition: json['condition'] as String?,
      conditionAr: json['condition_ar'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'date': date.toIso8601String(),
    'min_temperature': minTemperature,
    'max_temperature': maxTemperature,
    'rainfall': rainfall,
    'rainfall_probability': rainfallProbability,
    'condition': condition,
    'condition_ar': conditionAr,
  };
}

/// Crop Context
/// سياق المحصول
@immutable
class CropContext {
  final String type;
  final String typeAr;
  final String? variety;
  final String? varietyAr;
  final String? growthStage;
  final String? growthStageAr;
  final DateTime? plantingDate;
  final DateTime? expectedHarvestDate;
  final int? daysAfterPlanting;
  final double? gdd; // Growing Degree Days
  final double? lai; // Leaf Area Index
  final double? healthScore;
  final List<String>? activeIssues;
  final List<String>? activeIssuesAr;

  const CropContext({
    required this.type,
    required this.typeAr,
    this.variety,
    this.varietyAr,
    this.growthStage,
    this.growthStageAr,
    this.plantingDate,
    this.expectedHarvestDate,
    this.daysAfterPlanting,
    this.gdd,
    this.lai,
    this.healthScore,
    this.activeIssues,
    this.activeIssuesAr,
  });

  factory CropContext.fromJson(Map<String, dynamic> json) {
    return CropContext(
      type: json['type'] as String? ?? '',
      typeAr: json['type_ar'] as String? ?? json['type'] as String? ?? '',
      variety: json['variety'] as String?,
      varietyAr: json['variety_ar'] as String?,
      growthStage: json['growth_stage'] as String?,
      growthStageAr: json['growth_stage_ar'] as String?,
      plantingDate: json['planting_date'] != null
          ? DateTime.parse(json['planting_date'] as String)
          : null,
      expectedHarvestDate: json['expected_harvest_date'] != null
          ? DateTime.parse(json['expected_harvest_date'] as String)
          : null,
      daysAfterPlanting: json['days_after_planting'] as int?,
      gdd: (json['gdd'] as num?)?.toDouble(),
      lai: (json['lai'] as num?)?.toDouble(),
      healthScore: (json['health_score'] as num?)?.toDouble(),
      activeIssues: (json['active_issues'] as List?)?.cast<String>(),
      activeIssuesAr: (json['active_issues_ar'] as List?)?.cast<String>(),
    );
  }

  Map<String, dynamic> toJson() => {
    'type': type,
    'type_ar': typeAr,
    'variety': variety,
    'variety_ar': varietyAr,
    'growth_stage': growthStage,
    'growth_stage_ar': growthStageAr,
    'planting_date': plantingDate?.toIso8601String(),
    'expected_harvest_date': expectedHarvestDate?.toIso8601String(),
    'days_after_planting': daysAfterPlanting,
    'gdd': gdd,
    'lai': lai,
    'health_score': healthScore,
    'active_issues': activeIssues,
    'active_issues_ar': activeIssuesAr,
  };

  /// Get days until harvest
  int? get daysUntilHarvest {
    if (expectedHarvestDate == null) return null;
    return expectedHarvestDate!.difference(DateTime.now()).inDays;
  }

  /// Get health status text
  String get healthStatusAr {
    if (healthScore == null) return 'غير متوفر';
    if (healthScore! >= 80) return 'ممتاز';
    if (healthScore! >= 60) return 'جيد';
    if (healthScore! >= 40) return 'متوسط';
    return 'ضعيف';
  }
}

/// Soil Context
/// سياق التربة
@immutable
class SoilContext {
  final String? soilType;
  final String? soilTypeAr;
  final double? moisture; // Percentage
  final double? ph;
  final double? nitrogen; // ppm
  final double? phosphorus; // ppm
  final double? potassium; // ppm
  final double? organicMatter; // Percentage
  final double? electricalConductivity; // dS/m
  final DateTime? lastSoilTest;
  final String? irrigationRecommendation;
  final String? irrigationRecommendationAr;

  const SoilContext({
    this.soilType,
    this.soilTypeAr,
    this.moisture,
    this.ph,
    this.nitrogen,
    this.phosphorus,
    this.potassium,
    this.organicMatter,
    this.electricalConductivity,
    this.lastSoilTest,
    this.irrigationRecommendation,
    this.irrigationRecommendationAr,
  });

  factory SoilContext.fromJson(Map<String, dynamic> json) {
    return SoilContext(
      soilType: json['soil_type'] as String?,
      soilTypeAr: json['soil_type_ar'] as String?,
      moisture: (json['moisture'] as num?)?.toDouble(),
      ph: (json['ph'] as num?)?.toDouble(),
      nitrogen: (json['nitrogen'] as num?)?.toDouble(),
      phosphorus: (json['phosphorus'] as num?)?.toDouble(),
      potassium: (json['potassium'] as num?)?.toDouble(),
      organicMatter: (json['organic_matter'] as num?)?.toDouble(),
      electricalConductivity: (json['electrical_conductivity'] as num?)?.toDouble(),
      lastSoilTest: json['last_soil_test'] != null
          ? DateTime.parse(json['last_soil_test'] as String)
          : null,
      irrigationRecommendation: json['irrigation_recommendation'] as String?,
      irrigationRecommendationAr: json['irrigation_recommendation_ar'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'soil_type': soilType,
    'soil_type_ar': soilTypeAr,
    'moisture': moisture,
    'ph': ph,
    'nitrogen': nitrogen,
    'phosphorus': phosphorus,
    'potassium': potassium,
    'organic_matter': organicMatter,
    'electrical_conductivity': electricalConductivity,
    'last_soil_test': lastSoilTest?.toIso8601String(),
    'irrigation_recommendation': irrigationRecommendation,
    'irrigation_recommendation_ar': irrigationRecommendationAr,
  };

  /// Get moisture status
  String get moistureStatusAr {
    if (moisture == null) return 'غير متوفر';
    if (moisture! >= 70) return 'مرتفعة';
    if (moisture! >= 40) return 'مناسبة';
    if (moisture! >= 20) return 'منخفضة';
    return 'جافة';
  }

  /// Get pH status
  String get phStatusAr {
    if (ph == null) return 'غير متوفر';
    if (ph! < 6.0) return 'حمضية';
    if (ph! <= 7.5) return 'معتدلة';
    return 'قلوية';
  }

  /// Check if nitrogen is deficient
  bool get isNitrogenDeficient {
    if (nitrogen == null) return false;
    return nitrogen! < 25; // ppm threshold
  }
}

/// Historical Context
/// السياق التاريخي
@immutable
class HistoricalContext {
  final List<PastTreatment>? recentTreatments;
  final List<PastHarvest>? pastHarvests;
  final List<PastIssue>? pastIssues;
  final double? averageYield;
  final String? bestPractices;
  final String? bestPracticesAr;

  const HistoricalContext({
    this.recentTreatments,
    this.pastHarvests,
    this.pastIssues,
    this.averageYield,
    this.bestPractices,
    this.bestPracticesAr,
  });

  factory HistoricalContext.fromJson(Map<String, dynamic> json) {
    return HistoricalContext(
      recentTreatments: (json['recent_treatments'] as List?)
          ?.map((e) => PastTreatment.fromJson(e as Map<String, dynamic>))
          .toList(),
      pastHarvests: (json['past_harvests'] as List?)
          ?.map((e) => PastHarvest.fromJson(e as Map<String, dynamic>))
          .toList(),
      pastIssues: (json['past_issues'] as List?)
          ?.map((e) => PastIssue.fromJson(e as Map<String, dynamic>))
          .toList(),
      averageYield: (json['average_yield'] as num?)?.toDouble(),
      bestPractices: json['best_practices'] as String?,
      bestPracticesAr: json['best_practices_ar'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'recent_treatments': recentTreatments?.map((e) => e.toJson()).toList(),
    'past_harvests': pastHarvests?.map((e) => e.toJson()).toList(),
    'past_issues': pastIssues?.map((e) => e.toJson()).toList(),
    'average_yield': averageYield,
    'best_practices': bestPractices,
    'best_practices_ar': bestPracticesAr,
  };
}

/// Past Treatment Record
@immutable
class PastTreatment {
  final DateTime date;
  final String type;
  final String typeAr;
  final String? product;
  final double? amount;
  final String? unit;

  const PastTreatment({
    required this.date,
    required this.type,
    required this.typeAr,
    this.product,
    this.amount,
    this.unit,
  });

  factory PastTreatment.fromJson(Map<String, dynamic> json) {
    return PastTreatment(
      date: DateTime.parse(json['date'] as String),
      type: json['type'] as String? ?? '',
      typeAr: json['type_ar'] as String? ?? json['type'] as String? ?? '',
      product: json['product'] as String?,
      amount: (json['amount'] as num?)?.toDouble(),
      unit: json['unit'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'date': date.toIso8601String(),
    'type': type,
    'type_ar': typeAr,
    'product': product,
    'amount': amount,
    'unit': unit,
  };
}

/// Past Harvest Record
@immutable
class PastHarvest {
  final DateTime date;
  final String crop;
  final String cropAr;
  final double yield;
  final String unit;
  final String? quality;

  const PastHarvest({
    required this.date,
    required this.crop,
    required this.cropAr,
    required this.yield,
    required this.unit,
    this.quality,
  });

  factory PastHarvest.fromJson(Map<String, dynamic> json) {
    return PastHarvest(
      date: DateTime.parse(json['date'] as String),
      crop: json['crop'] as String? ?? '',
      cropAr: json['crop_ar'] as String? ?? json['crop'] as String? ?? '',
      yield: (json['yield'] as num? ?? 0).toDouble(),
      unit: json['unit'] as String? ?? 'kg/ha',
      quality: json['quality'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'date': date.toIso8601String(),
    'crop': crop,
    'crop_ar': cropAr,
    'yield': yield,
    'unit': unit,
    'quality': quality,
  };
}

/// Past Issue Record
@immutable
class PastIssue {
  final DateTime date;
  final String issue;
  final String issueAr;
  final String? resolution;
  final String? resolutionAr;

  const PastIssue({
    required this.date,
    required this.issue,
    required this.issueAr,
    this.resolution,
    this.resolutionAr,
  });

  factory PastIssue.fromJson(Map<String, dynamic> json) {
    return PastIssue(
      date: DateTime.parse(json['date'] as String),
      issue: json['issue'] as String? ?? '',
      issueAr: json['issue_ar'] as String? ?? json['issue'] as String? ?? '',
      resolution: json['resolution'] as String?,
      resolutionAr: json['resolution_ar'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'date': date.toIso8601String(),
    'issue': issue,
    'issue_ar': issueAr,
    'resolution': resolution,
    'resolution_ar': resolutionAr,
  };
}
