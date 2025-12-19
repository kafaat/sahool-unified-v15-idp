// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'virtual_sensor_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$WeatherInputImpl _$$WeatherInputImplFromJson(Map<String, dynamic> json) =>
    _$WeatherInputImpl(
      temperatureMax: (json['temperatureMax'] as num).toDouble(),
      temperatureMin: (json['temperatureMin'] as num).toDouble(),
      humidity: (json['humidity'] as num).toDouble(),
      windSpeed: (json['windSpeed'] as num).toDouble(),
      solarRadiation: (json['solarRadiation'] as num?)?.toDouble(),
      sunshineHours: (json['sunshineHours'] as num?)?.toDouble(),
      latitude: (json['latitude'] as num).toDouble(),
      altitude: (json['altitude'] as num?)?.toDouble() ?? 0,
      date:
          json['date'] == null ? null : DateTime.parse(json['date'] as String),
    );

Map<String, dynamic> _$$WeatherInputImplToJson(_$WeatherInputImpl instance) =>
    <String, dynamic>{
      'temperatureMax': instance.temperatureMax,
      'temperatureMin': instance.temperatureMin,
      'humidity': instance.humidity,
      'windSpeed': instance.windSpeed,
      'solarRadiation': instance.solarRadiation,
      'sunshineHours': instance.sunshineHours,
      'latitude': instance.latitude,
      'altitude': instance.altitude,
      'date': instance.date?.toIso8601String(),
    };

_$ET0ResponseImpl _$$ET0ResponseImplFromJson(Map<String, dynamic> json) =>
    _$ET0ResponseImpl(
      et0: (json['et0'] as num).toDouble(),
      et0Ar: json['et0Ar'] as String,
      method: json['method'] as String,
      weatherSummary: json['weatherSummary'] as Map<String, dynamic>,
      calculationDate: DateTime.parse(json['calculationDate'] as String),
    );

Map<String, dynamic> _$$ET0ResponseImplToJson(_$ET0ResponseImpl instance) =>
    <String, dynamic>{
      'et0': instance.et0,
      'et0Ar': instance.et0Ar,
      'method': instance.method,
      'weatherSummary': instance.weatherSummary,
      'calculationDate': instance.calculationDate.toIso8601String(),
    };

_$CropETcResponseImpl _$$CropETcResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$CropETcResponseImpl(
      cropType: json['cropType'] as String,
      cropNameAr: json['cropNameAr'] as String,
      growthStage: json['growthStage'] as String,
      kc: (json['kc'] as num).toDouble(),
      et0: (json['et0'] as num).toDouble(),
      etc: (json['etc'] as num).toDouble(),
      dailyWaterNeedLiters: (json['dailyWaterNeedLiters'] as num).toDouble(),
      dailyWaterNeedM3: (json['dailyWaterNeedM3'] as num).toDouble(),
      weeklyWaterNeedM3: (json['weeklyWaterNeedM3'] as num).toDouble(),
      criticalPeriod: json['criticalPeriod'] as bool,
      notes: json['notes'] as String,
      notesAr: json['notesAr'] as String,
    );

Map<String, dynamic> _$$CropETcResponseImplToJson(
        _$CropETcResponseImpl instance) =>
    <String, dynamic>{
      'cropType': instance.cropType,
      'cropNameAr': instance.cropNameAr,
      'growthStage': instance.growthStage,
      'kc': instance.kc,
      'et0': instance.et0,
      'etc': instance.etc,
      'dailyWaterNeedLiters': instance.dailyWaterNeedLiters,
      'dailyWaterNeedM3': instance.dailyWaterNeedM3,
      'weeklyWaterNeedM3': instance.weeklyWaterNeedM3,
      'criticalPeriod': instance.criticalPeriod,
      'notes': instance.notes,
      'notesAr': instance.notesAr,
    };

_$CropKcOptionImpl _$$CropKcOptionImplFromJson(Map<String, dynamic> json) =>
    _$CropKcOptionImpl(
      cropId: json['cropId'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String,
      kcInitial: (json['kcInitial'] as num).toDouble(),
      kcMid: (json['kcMid'] as num).toDouble(),
      kcEnd: (json['kcEnd'] as num).toDouble(),
      rootDepthMax: (json['rootDepthMax'] as num).toDouble(),
      criticalPeriods: (json['criticalPeriods'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$CropKcOptionImplToJson(_$CropKcOptionImpl instance) =>
    <String, dynamic>{
      'cropId': instance.cropId,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'kcInitial': instance.kcInitial,
      'kcMid': instance.kcMid,
      'kcEnd': instance.kcEnd,
      'rootDepthMax': instance.rootDepthMax,
      'criticalPeriods': instance.criticalPeriods,
    };

_$VirtualSoilMoistureResponseImpl _$$VirtualSoilMoistureResponseImplFromJson(
        Map<String, dynamic> json) =>
    _$VirtualSoilMoistureResponseImpl(
      calculationId: json['calculationId'] as String,
      estimatedMoisture: (json['estimatedMoisture'] as num).toDouble(),
      moisturePercentage: (json['moisturePercentage'] as num).toDouble(),
      daysSinceIrrigation: (json['daysSinceIrrigation'] as num).toInt(),
      totalEtLoss: (json['totalEtLoss'] as num).toDouble(),
      availableWater: (json['availableWater'] as num).toDouble(),
      totalAvailableWater: (json['totalAvailableWater'] as num).toDouble(),
      status: json['status'] as String,
      statusAr: json['statusAr'] as String,
      urgency: $enumDecode(_$UrgencyLevelEnumMap, json['urgency']),
    );

Map<String, dynamic> _$$VirtualSoilMoistureResponseImplToJson(
        _$VirtualSoilMoistureResponseImpl instance) =>
    <String, dynamic>{
      'calculationId': instance.calculationId,
      'estimatedMoisture': instance.estimatedMoisture,
      'moisturePercentage': instance.moisturePercentage,
      'daysSinceIrrigation': instance.daysSinceIrrigation,
      'totalEtLoss': instance.totalEtLoss,
      'availableWater': instance.availableWater,
      'totalAvailableWater': instance.totalAvailableWater,
      'status': instance.status,
      'statusAr': instance.statusAr,
      'urgency': _$UrgencyLevelEnumMap[instance.urgency]!,
    };

const _$UrgencyLevelEnumMap = {
  UrgencyLevel.none: 'none',
  UrgencyLevel.low: 'low',
  UrgencyLevel.medium: 'medium',
  UrgencyLevel.high: 'high',
  UrgencyLevel.critical: 'critical',
};

_$IrrigationRecommendationImpl _$$IrrigationRecommendationImplFromJson(
        Map<String, dynamic> json) =>
    _$IrrigationRecommendationImpl(
      recommendationId: json['recommendationId'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      cropType: json['cropType'] as String,
      cropNameAr: json['cropNameAr'] as String,
      growthStage: json['growthStage'] as String,
      fieldAreaHectares: (json['fieldAreaHectares'] as num).toDouble(),
      et0: (json['et0'] as num).toDouble(),
      kc: (json['kc'] as num).toDouble(),
      etc: (json['etc'] as num).toDouble(),
      soilType: json['soilType'] as String,
      soilTypeAr: json['soilTypeAr'] as String,
      estimatedMoisture: (json['estimatedMoisture'] as num).toDouble(),
      moistureDepletionPercent:
          (json['moistureDepletionPercent'] as num).toDouble(),
      irrigationNeeded: json['irrigationNeeded'] as bool,
      urgency: $enumDecode(_$UrgencyLevelEnumMap, json['urgency']),
      urgencyAr: json['urgencyAr'] as String,
      recommendedAmountMm: (json['recommendedAmountMm'] as num).toDouble(),
      recommendedAmountLiters:
          (json['recommendedAmountLiters'] as num).toDouble(),
      recommendedAmountM3: (json['recommendedAmountM3'] as num).toDouble(),
      grossIrrigationMm: (json['grossIrrigationMm'] as num).toDouble(),
      optimalTime: json['optimalTime'] as String,
      optimalTimeAr: json['optimalTimeAr'] as String,
      nextIrrigationDays: (json['nextIrrigationDays'] as num).toInt(),
      advice: json['advice'] as String,
      adviceAr: json['adviceAr'] as String,
      warnings: (json['warnings'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      warningsAr: (json['warningsAr'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$IrrigationRecommendationImplToJson(
        _$IrrigationRecommendationImpl instance) =>
    <String, dynamic>{
      'recommendationId': instance.recommendationId,
      'timestamp': instance.timestamp.toIso8601String(),
      'cropType': instance.cropType,
      'cropNameAr': instance.cropNameAr,
      'growthStage': instance.growthStage,
      'fieldAreaHectares': instance.fieldAreaHectares,
      'et0': instance.et0,
      'kc': instance.kc,
      'etc': instance.etc,
      'soilType': instance.soilType,
      'soilTypeAr': instance.soilTypeAr,
      'estimatedMoisture': instance.estimatedMoisture,
      'moistureDepletionPercent': instance.moistureDepletionPercent,
      'irrigationNeeded': instance.irrigationNeeded,
      'urgency': _$UrgencyLevelEnumMap[instance.urgency]!,
      'urgencyAr': instance.urgencyAr,
      'recommendedAmountMm': instance.recommendedAmountMm,
      'recommendedAmountLiters': instance.recommendedAmountLiters,
      'recommendedAmountM3': instance.recommendedAmountM3,
      'grossIrrigationMm': instance.grossIrrigationMm,
      'optimalTime': instance.optimalTime,
      'optimalTimeAr': instance.optimalTimeAr,
      'nextIrrigationDays': instance.nextIrrigationDays,
      'advice': instance.advice,
      'adviceAr': instance.adviceAr,
      'warnings': instance.warnings,
      'warningsAr': instance.warningsAr,
    };

_$QuickIrrigationCheckImpl _$$QuickIrrigationCheckImplFromJson(
        Map<String, dynamic> json) =>
    _$QuickIrrigationCheckImpl(
      cropType: json['cropType'] as String,
      cropNameAr: json['cropNameAr'] as String,
      growthStage: json['growthStage'] as String,
      daysSinceIrrigation: (json['daysSinceIrrigation'] as num).toInt(),
      estimatedEt0: (json['estimatedEt0'] as num).toDouble(),
      kc: (json['kc'] as num).toDouble(),
      estimatedEtc: (json['estimatedEtc'] as num).toDouble(),
      estimatedWaterLossMm: (json['estimatedWaterLossMm'] as num).toDouble(),
      estimatedDepletionPercent:
          (json['estimatedDepletionPercent'] as num).toDouble(),
      status: json['status'] as String,
      statusAr: json['statusAr'] as String,
      needsIrrigation: json['needsIrrigation'] as bool,
      recommendation: json['recommendation'] as String,
      recommendationAr: json['recommendationAr'] as String,
    );

Map<String, dynamic> _$$QuickIrrigationCheckImplToJson(
        _$QuickIrrigationCheckImpl instance) =>
    <String, dynamic>{
      'cropType': instance.cropType,
      'cropNameAr': instance.cropNameAr,
      'growthStage': instance.growthStage,
      'daysSinceIrrigation': instance.daysSinceIrrigation,
      'estimatedEt0': instance.estimatedEt0,
      'kc': instance.kc,
      'estimatedEtc': instance.estimatedEtc,
      'estimatedWaterLossMm': instance.estimatedWaterLossMm,
      'estimatedDepletionPercent': instance.estimatedDepletionPercent,
      'status': instance.status,
      'statusAr': instance.statusAr,
      'needsIrrigation': instance.needsIrrigation,
      'recommendation': instance.recommendation,
      'recommendationAr': instance.recommendationAr,
    };

_$SoilTypeInfoImpl _$$SoilTypeInfoImplFromJson(Map<String, dynamic> json) =>
    _$SoilTypeInfoImpl(
      soilType: json['soilType'] as String,
      nameAr: json['nameAr'] as String,
      fieldCapacity: (json['fieldCapacity'] as num).toDouble(),
      wiltingPoint: (json['wiltingPoint'] as num).toDouble(),
      availableWaterCapacity:
          (json['availableWaterCapacity'] as num).toDouble(),
      infiltrationRateMmHr: (json['infiltrationRateMmHr'] as num).toDouble(),
    );

Map<String, dynamic> _$$SoilTypeInfoImplToJson(_$SoilTypeInfoImpl instance) =>
    <String, dynamic>{
      'soilType': instance.soilType,
      'nameAr': instance.nameAr,
      'fieldCapacity': instance.fieldCapacity,
      'wiltingPoint': instance.wiltingPoint,
      'availableWaterCapacity': instance.availableWaterCapacity,
      'infiltrationRateMmHr': instance.infiltrationRateMmHr,
    };

_$IrrigationMethodInfoImpl _$$IrrigationMethodInfoImplFromJson(
        Map<String, dynamic> json) =>
    _$IrrigationMethodInfoImpl(
      method: json['method'] as String,
      efficiency: (json['efficiency'] as num).toDouble(),
      efficiencyPercent: json['efficiencyPercent'] as String,
    );

Map<String, dynamic> _$$IrrigationMethodInfoImplToJson(
        _$IrrigationMethodInfoImpl instance) =>
    <String, dynamic>{
      'method': instance.method,
      'efficiency': instance.efficiency,
      'efficiencyPercent': instance.efficiencyPercent,
    };
