// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'span_zone_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$SpanConfigurationImpl _$$SpanConfigurationImplFromJson(
        Map<String, dynamic> json) =>
    _$SpanConfigurationImpl(
      id: json['id'] as String,
      spanNumber: (json['spanNumber'] as num).toInt(),
      distanceFromCenter: (json['distanceFromCenter'] as num).toDouble(),
      spanLengthMeters: (json['spanLengthMeters'] as num).toDouble(),
      nozzleCount: (json['nozzleCount'] as num?)?.toInt() ?? 10,
      nozzlePackage:
          $enumDecodeNullable(_$NozzlePackageEnumMap, json['nozzlePackage']) ??
              NozzlePackage.standard,
      baseApplicationRateMmHr:
          (json['baseApplicationRateMmHr'] as num?)?.toDouble() ?? 6.0,
      zones: (json['zones'] as List<dynamic>?)
              ?.map((e) => SpanZone.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      isOperational: json['isOperational'] as bool? ?? true,
      lastMaintenanceDate: json['lastMaintenanceDate'] == null
          ? null
          : DateTime.parse(json['lastMaintenanceDate'] as String),
    );

Map<String, dynamic> _$$SpanConfigurationImplToJson(
        _$SpanConfigurationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'spanNumber': instance.spanNumber,
      'distanceFromCenter': instance.distanceFromCenter,
      'spanLengthMeters': instance.spanLengthMeters,
      'nozzleCount': instance.nozzleCount,
      'nozzlePackage': _$NozzlePackageEnumMap[instance.nozzlePackage]!,
      'baseApplicationRateMmHr': instance.baseApplicationRateMmHr,
      'zones': instance.zones.map((e) => e.toJson()).toList(),
      'isOperational': instance.isOperational,
      if (instance.lastMaintenanceDate?.toIso8601String() case final value?)
        'lastMaintenanceDate': value,
    };

const _$NozzlePackageEnumMap = {
  NozzlePackage.standard: 'standard',
  NozzlePackage.lowPressure: 'low_pressure',
  NozzlePackage.highCapacity: 'high_capacity',
  NozzlePackage.precision: 'precision',
  NozzlePackage.lesa: 'lesa',
  NozzlePackage.lepa: 'lepa',
};

_$SpanZoneImpl _$$SpanZoneImplFromJson(Map<String, dynamic> json) =>
    _$SpanZoneImpl(
      id: json['id'] as String,
      spanNumber: (json['spanNumber'] as num).toInt(),
      zoneNumber: (json['zoneNumber'] as num).toInt(),
      startAngle: (json['startAngle'] as num).toDouble(),
      endAngle: (json['endAngle'] as num).toDouble(),
      applicationRatePercent:
          (json['applicationRatePercent'] as num?)?.toDouble() ?? 100,
      prescriptionId: json['prescriptionId'] as String?,
      ndviValue: (json['ndviValue'] as num?)?.toDouble(),
      soilType: json['soilType'] as String? ?? '',
      cropType: json['cropType'] as String? ?? '',
      isEnabled: json['isEnabled'] as bool? ?? true,
      color: json['color'] as String? ?? '#4CAF50',
      notes: json['notes'] as String? ?? '',
      notesAr: json['notesAr'] as String? ?? '',
    );

Map<String, dynamic> _$$SpanZoneImplToJson(_$SpanZoneImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'spanNumber': instance.spanNumber,
      'zoneNumber': instance.zoneNumber,
      'startAngle': instance.startAngle,
      'endAngle': instance.endAngle,
      'applicationRatePercent': instance.applicationRatePercent,
      if (instance.prescriptionId case final value?) 'prescriptionId': value,
      if (instance.ndviValue case final value?) 'ndviValue': value,
      'soilType': instance.soilType,
      'cropType': instance.cropType,
      'isEnabled': instance.isEnabled,
      'color': instance.color,
      'notes': instance.notes,
      'notesAr': instance.notesAr,
    };

_$VRIZoneGridImpl _$$VRIZoneGridImplFromJson(Map<String, dynamic> json) =>
    _$VRIZoneGridImpl(
      pivotId: json['pivotId'] as String,
      spanCount: (json['spanCount'] as num).toInt(),
      angularDivisions: (json['angularDivisions'] as num).toInt(),
      grid: (json['grid'] as List<dynamic>)
          .map((e) => (e as List<dynamic>)
              .map((e) => SpanZone.fromJson(e as Map<String, dynamic>))
              .toList())
          .toList(),
      totalZones: (json['totalZones'] as num?)?.toInt(),
      angularResolution: (json['angularResolution'] as num?)?.toDouble(),
      createdAt: json['createdAt'] == null
          ? null
          : DateTime.parse(json['createdAt'] as String),
      updatedAt: json['updatedAt'] == null
          ? null
          : DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$$VRIZoneGridImplToJson(_$VRIZoneGridImpl instance) =>
    <String, dynamic>{
      'pivotId': instance.pivotId,
      'spanCount': instance.spanCount,
      'angularDivisions': instance.angularDivisions,
      'grid':
          instance.grid.map((e) => e.map((e) => e.toJson()).toList()).toList(),
      if (instance.totalZones case final value?) 'totalZones': value,
      if (instance.angularResolution case final value?)
        'angularResolution': value,
      if (instance.createdAt?.toIso8601String() case final value?)
        'createdAt': value,
      if (instance.updatedAt?.toIso8601String() case final value?)
        'updatedAt': value,
    };

_$PrescriptionMapImpl _$$PrescriptionMapImplFromJson(
        Map<String, dynamic> json) =>
    _$PrescriptionMapImpl(
      id: json['id'] as String,
      pivotId: json['pivotId'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String? ?? '',
      prescriptionType:
          $enumDecode(_$PrescriptionTypeEnumMap, json['prescriptionType']),
      source: $enumDecode(_$PrescriptionSourceEnumMap, json['source']),
      zoneValues: (json['zoneValues'] as Map<String, dynamic>).map(
        (k, e) => MapEntry(k, (e as num).toDouble()),
      ),
      minValue: (json['minValue'] as num?)?.toDouble() ?? 0,
      maxValue: (json['maxValue'] as num?)?.toDouble() ?? 150,
      unit: json['unit'] as String? ?? '%',
      validFrom: json['validFrom'] == null
          ? null
          : DateTime.parse(json['validFrom'] as String),
      validUntil: json['validUntil'] == null
          ? null
          : DateTime.parse(json['validUntil'] as String),
      isActive: json['isActive'] as bool? ?? true,
      createdAt: json['createdAt'] == null
          ? null
          : DateTime.parse(json['createdAt'] as String),
      notes: json['notes'] as String? ?? '',
      notesAr: json['notesAr'] as String? ?? '',
    );

Map<String, dynamic> _$$PrescriptionMapImplToJson(
        _$PrescriptionMapImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'pivotId': instance.pivotId,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'prescriptionType': _$PrescriptionTypeEnumMap[instance.prescriptionType]!,
      'source': _$PrescriptionSourceEnumMap[instance.source]!,
      'zoneValues': instance.zoneValues,
      'minValue': instance.minValue,
      'maxValue': instance.maxValue,
      'unit': instance.unit,
      if (instance.validFrom?.toIso8601String() case final value?)
        'validFrom': value,
      if (instance.validUntil?.toIso8601String() case final value?)
        'validUntil': value,
      'isActive': instance.isActive,
      if (instance.createdAt?.toIso8601String() case final value?)
        'createdAt': value,
      'notes': instance.notes,
      'notesAr': instance.notesAr,
    };

const _$PrescriptionTypeEnumMap = {
  PrescriptionType.irrigation: 'irrigation',
  PrescriptionType.fertigation: 'fertigation',
  PrescriptionType.chemigation: 'chemigation',
};

const _$PrescriptionSourceEnumMap = {
  PrescriptionSource.manual: 'manual',
  PrescriptionSource.ndvi: 'ndvi',
  PrescriptionSource.soilMap: 'soil_map',
  PrescriptionSource.yieldMap: 'yield_map',
  PrescriptionSource.sensorData: 'sensor_data',
  PrescriptionSource.aiRecommendation: 'ai_recommendation',
};

_$VRIZoneStatisticsImpl _$$VRIZoneStatisticsImplFromJson(
        Map<String, dynamic> json) =>
    _$VRIZoneStatisticsImpl(
      totalZones: (json['totalZones'] as num).toInt(),
      activeZones: (json['activeZones'] as num).toInt(),
      offZones: (json['offZones'] as num).toInt(),
      avgApplicationRate: (json['avgApplicationRate'] as num).toDouble(),
      minApplicationRate: (json['minApplicationRate'] as num).toDouble(),
      maxApplicationRate: (json['maxApplicationRate'] as num).toDouble(),
      rateDistribution: Map<String, int>.from(json['rateDistribution'] as Map),
      waterSavingsPercent: (json['waterSavingsPercent'] as num).toDouble(),
    );

Map<String, dynamic> _$$VRIZoneStatisticsImplToJson(
        _$VRIZoneStatisticsImpl instance) =>
    <String, dynamic>{
      'totalZones': instance.totalZones,
      'activeZones': instance.activeZones,
      'offZones': instance.offZones,
      'avgApplicationRate': instance.avgApplicationRate,
      'minApplicationRate': instance.minApplicationRate,
      'maxApplicationRate': instance.maxApplicationRate,
      'rateDistribution': instance.rateDistribution,
      'waterSavingsPercent': instance.waterSavingsPercent,
    };
