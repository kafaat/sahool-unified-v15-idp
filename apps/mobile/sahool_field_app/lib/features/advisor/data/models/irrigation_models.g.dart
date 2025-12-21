// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'irrigation_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$IrrigationRequestImpl _$$IrrigationRequestImplFromJson(
        Map<String, dynamic> json) =>
    _$IrrigationRequestImpl(
      cropType: json['cropType'] as String,
      growthStage: json['growthStage'] as String,
      fieldArea: (json['fieldArea'] as num).toDouble(),
      soilType: json['soilType'] as String,
      irrigationMethod: json['irrigationMethod'] as String,
      currentSoilMoisture:
          (json['currentSoilMoisture'] as num?)?.toDouble() ?? 0,
      temperature: (json['temperature'] as num?)?.toDouble() ?? 0,
      humidity: (json['humidity'] as num?)?.toDouble() ?? 0,
      governorate: json['governorate'] as String? ?? '',
    );

Map<String, dynamic> _$$IrrigationRequestImplToJson(
        _$IrrigationRequestImpl instance) =>
    <String, dynamic>{
      'cropType': instance.cropType,
      'growthStage': instance.growthStage,
      'fieldArea': instance.fieldArea,
      'soilType': instance.soilType,
      'irrigationMethod': instance.irrigationMethod,
      'currentSoilMoisture': instance.currentSoilMoisture,
      'temperature': instance.temperature,
      'humidity': instance.humidity,
      'governorate': instance.governorate,
    };

_$IrrigationCalculationImpl _$$IrrigationCalculationImplFromJson(
        Map<String, dynamic> json) =>
    _$IrrigationCalculationImpl(
      waterRequirementMm: (json['waterRequirementMm'] as num).toDouble(),
      waterRequirementLiters:
          (json['waterRequirementLiters'] as num).toDouble(),
      totalWaterLiters: (json['totalWaterLiters'] as num).toDouble(),
      etCrop: (json['etCrop'] as num).toDouble(),
      irrigationEfficiency: (json['irrigationEfficiency'] as num).toDouble(),
      recommendedFrequency: json['recommendedFrequency'] as String,
      recommendedFrequencyAr: json['recommendedFrequencyAr'] as String,
      durationMinutes: (json['durationMinutes'] as num).toInt(),
      notes: json['notes'] as String? ?? '',
      notesAr: json['notesAr'] as String? ?? '',
    );

Map<String, dynamic> _$$IrrigationCalculationImplToJson(
        _$IrrigationCalculationImpl instance) =>
    <String, dynamic>{
      'waterRequirementMm': instance.waterRequirementMm,
      'waterRequirementLiters': instance.waterRequirementLiters,
      'totalWaterLiters': instance.totalWaterLiters,
      'etCrop': instance.etCrop,
      'irrigationEfficiency': instance.irrigationEfficiency,
      'recommendedFrequency': instance.recommendedFrequency,
      'recommendedFrequencyAr': instance.recommendedFrequencyAr,
      'durationMinutes': instance.durationMinutes,
      'notes': instance.notes,
      'notesAr': instance.notesAr,
    };

_$IrrigationScheduleImpl _$$IrrigationScheduleImplFromJson(
        Map<String, dynamic> json) =>
    _$IrrigationScheduleImpl(
      scheduleId: json['scheduleId'] as String,
      fieldId: json['fieldId'] as String,
      events: (json['events'] as List<dynamic>)
          .map((e) => IrrigationEvent.fromJson(e as Map<String, dynamic>))
          .toList(),
      startDate: DateTime.parse(json['startDate'] as String),
      endDate: DateTime.parse(json['endDate'] as String),
      totalWaterPlanned: (json['totalWaterPlanned'] as num).toDouble(),
      notes: json['notes'] as String? ?? '',
      notesAr: json['notesAr'] as String? ?? '',
    );

Map<String, dynamic> _$$IrrigationScheduleImplToJson(
        _$IrrigationScheduleImpl instance) =>
    <String, dynamic>{
      'scheduleId': instance.scheduleId,
      'fieldId': instance.fieldId,
      'events': instance.events,
      'startDate': instance.startDate.toIso8601String(),
      'endDate': instance.endDate.toIso8601String(),
      'totalWaterPlanned': instance.totalWaterPlanned,
      'notes': instance.notes,
      'notesAr': instance.notesAr,
    };

_$IrrigationEventImpl _$$IrrigationEventImplFromJson(
        Map<String, dynamic> json) =>
    _$IrrigationEventImpl(
      eventId: json['eventId'] as String,
      scheduledTime: DateTime.parse(json['scheduledTime'] as String),
      durationMinutes: (json['durationMinutes'] as num).toInt(),
      waterLiters: (json['waterLiters'] as num).toDouble(),
      status: json['status'] as String,
      statusAr: json['statusAr'] as String,
      notes: json['notes'] as String? ?? '',
    );

Map<String, dynamic> _$$IrrigationEventImplToJson(
        _$IrrigationEventImpl instance) =>
    <String, dynamic>{
      'eventId': instance.eventId,
      'scheduledTime': instance.scheduledTime.toIso8601String(),
      'durationMinutes': instance.durationMinutes,
      'waterLiters': instance.waterLiters,
      'status': instance.status,
      'statusAr': instance.statusAr,
      'notes': instance.notes,
    };

_$WaterBalanceImpl _$$WaterBalanceImplFromJson(Map<String, dynamic> json) =>
    _$WaterBalanceImpl(
      soilMoisturePercent: (json['soilMoisturePercent'] as num).toDouble(),
      fieldCapacity: (json['fieldCapacity'] as num).toDouble(),
      wiltingPoint: (json['wiltingPoint'] as num).toDouble(),
      availableWater: (json['availableWater'] as num).toDouble(),
      depletionPercent: (json['depletionPercent'] as num).toDouble(),
      status: json['status'] as String,
      statusAr: json['statusAr'] as String,
      irrigationNeeded: json['irrigationNeeded'] as bool,
      recommendedWaterMm: (json['recommendedWaterMm'] as num?)?.toDouble() ?? 0,
    );

Map<String, dynamic> _$$WaterBalanceImplToJson(_$WaterBalanceImpl instance) =>
    <String, dynamic>{
      'soilMoisturePercent': instance.soilMoisturePercent,
      'fieldCapacity': instance.fieldCapacity,
      'wiltingPoint': instance.wiltingPoint,
      'availableWater': instance.availableWater,
      'depletionPercent': instance.depletionPercent,
      'status': instance.status,
      'statusAr': instance.statusAr,
      'irrigationNeeded': instance.irrigationNeeded,
      'recommendedWaterMm': instance.recommendedWaterMm,
    };

_$SensorReadingImpl _$$SensorReadingImplFromJson(Map<String, dynamic> json) =>
    _$SensorReadingImpl(
      sensorId: json['sensorId'] as String,
      sensorType: json['sensorType'] as String,
      value: (json['value'] as num).toDouble(),
      unit: json['unit'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
      fieldId: json['fieldId'] as String,
      location: json['location'] as String? ?? '',
    );

Map<String, dynamic> _$$SensorReadingImplToJson(_$SensorReadingImpl instance) =>
    <String, dynamic>{
      'sensorId': instance.sensorId,
      'sensorType': instance.sensorType,
      'value': instance.value,
      'unit': instance.unit,
      'timestamp': instance.timestamp.toIso8601String(),
      'fieldId': instance.fieldId,
      'location': instance.location,
    };

_$IrrigationEfficiencyReportImpl _$$IrrigationEfficiencyReportImplFromJson(
        Map<String, dynamic> json) =>
    _$IrrigationEfficiencyReportImpl(
      reportId: json['reportId'] as String,
      fieldId: json['fieldId'] as String,
      period: json['period'] as String,
      waterUsedLiters: (json['waterUsedLiters'] as num).toDouble(),
      waterSavedLiters: (json['waterSavedLiters'] as num).toDouble(),
      efficiencyPercent: (json['efficiencyPercent'] as num).toDouble(),
      costSaved: (json['costSaved'] as num).toDouble(),
      dailyUsage: (json['dailyUsage'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, (e as num).toDouble()),
      ),
      recommendations: (json['recommendations'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      recommendationsAr: (json['recommendationsAr'] as List<dynamic>)
          .map((e) => e as String)
          .toList(),
      generatedAt: DateTime.parse(json['generatedAt'] as String),
    );

Map<String, dynamic> _$$IrrigationEfficiencyReportImplToJson(
        _$IrrigationEfficiencyReportImpl instance) =>
    <String, dynamic>{
      'reportId': instance.reportId,
      'fieldId': instance.fieldId,
      'period': instance.period,
      'waterUsedLiters': instance.waterUsedLiters,
      'waterSavedLiters': instance.waterSavedLiters,
      'efficiencyPercent': instance.efficiencyPercent,
      'costSaved': instance.costSaved,
      'dailyUsage': instance.dailyUsage,
      'recommendations': instance.recommendations,
      'recommendationsAr': instance.recommendationsAr,
      'generatedAt': instance.generatedAt.toIso8601String(),
    };

_$IrrigationMethodOptionImpl _$$IrrigationMethodOptionImplFromJson(
        Map<String, dynamic> json) =>
    _$IrrigationMethodOptionImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String,
      efficiency: (json['efficiency'] as num).toDouble(),
      description: json['description'] as String,
      descriptionAr: json['descriptionAr'] as String,
      suitableCrops: (json['suitableCrops'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      suitableCropsAr: (json['suitableCropsAr'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$IrrigationMethodOptionImplToJson(
        _$IrrigationMethodOptionImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'efficiency': instance.efficiency,
      'description': instance.description,
      'descriptionAr': instance.descriptionAr,
      'suitableCrops': instance.suitableCrops,
      'suitableCropsAr': instance.suitableCropsAr,
    };

_$CropWaterRequirementImpl _$$CropWaterRequirementImplFromJson(
        Map<String, dynamic> json) =>
    _$CropWaterRequirementImpl(
      cropId: json['cropId'] as String,
      cropName: json['cropName'] as String,
      cropNameAr: json['cropNameAr'] as String,
      stageRequirements:
          (json['stageRequirements'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, (e as num).toDouble()),
      ),
      kcInitial: (json['kcInitial'] as num).toDouble(),
      kcMid: (json['kcMid'] as num).toDouble(),
      kcEnd: (json['kcEnd'] as num).toDouble(),
      rootDepthCm: (json['rootDepthCm'] as num).toInt(),
      criticalDepletionFraction:
          (json['criticalDepletionFraction'] as num).toDouble(),
    );

Map<String, dynamic> _$$CropWaterRequirementImplToJson(
        _$CropWaterRequirementImpl instance) =>
    <String, dynamic>{
      'cropId': instance.cropId,
      'cropName': instance.cropName,
      'cropNameAr': instance.cropNameAr,
      'stageRequirements': instance.stageRequirements,
      'kcInitial': instance.kcInitial,
      'kcMid': instance.kcMid,
      'kcEnd': instance.kcEnd,
      'rootDepthCm': instance.rootDepthCm,
      'criticalDepletionFraction': instance.criticalDepletionFraction,
    };
