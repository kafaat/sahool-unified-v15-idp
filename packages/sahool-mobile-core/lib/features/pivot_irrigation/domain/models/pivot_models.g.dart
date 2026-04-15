// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pivot_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$PivotConfigurationImpl _$$PivotConfigurationImplFromJson(
        Map<String, dynamic> json) =>
    _$PivotConfigurationImpl(
      id: json['id'] as String,
      fieldId: json['fieldId'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String? ?? '',
      centerLat: (json['centerLat'] as num).toDouble(),
      centerLng: (json['centerLng'] as num).toDouble(),
      lengthMeters: (json['lengthMeters'] as num).toDouble(),
      overhangMeters: (json['overhangMeters'] as num?)?.toDouble() ?? 0,
      spansCount: (json['spansCount'] as num).toInt(),
      rotationDirection: $enumDecodeNullable(
              _$RotationDirectionEnumMap, json['rotationDirection']) ??
          RotationDirection.clockwise,
      areaHectares: (json['areaHectares'] as num).toDouble(),
      pivotType: $enumDecodeNullable(_$PivotTypeEnumMap, json['pivotType']) ??
          PivotType.fullCircle,
      startAngle: (json['startAngle'] as num?)?.toDouble() ?? 0,
      endAngle: (json['endAngle'] as num?)?.toDouble() ?? 360,
      flowRateLph: (json['flowRateLph'] as num).toDouble(),
      operatingPressureBar:
          (json['operatingPressureBar'] as num?)?.toDouble() ?? 2.5,
      hasVRI: json['hasVRI'] as bool? ?? false,
      hasEndGun: json['hasEndGun'] as bool? ?? false,
      hasCornerSystem: json['hasCornerSystem'] as bool? ?? false,
      sectors: (json['sectors'] as List<dynamic>?)
              ?.map((e) => PivotSector.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      vriZones: (json['vriZones'] as List<dynamic>?)
              ?.map((e) => VRIZone.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      createdAt: json['createdAt'] == null
          ? null
          : DateTime.parse(json['createdAt'] as String),
      updatedAt: json['updatedAt'] == null
          ? null
          : DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$$PivotConfigurationImplToJson(
        _$PivotConfigurationImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'fieldId': instance.fieldId,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'centerLat': instance.centerLat,
      'centerLng': instance.centerLng,
      'lengthMeters': instance.lengthMeters,
      'overhangMeters': instance.overhangMeters,
      'spansCount': instance.spansCount,
      'rotationDirection':
          _$RotationDirectionEnumMap[instance.rotationDirection]!,
      'areaHectares': instance.areaHectares,
      'pivotType': _$PivotTypeEnumMap[instance.pivotType]!,
      'startAngle': instance.startAngle,
      'endAngle': instance.endAngle,
      'flowRateLph': instance.flowRateLph,
      'operatingPressureBar': instance.operatingPressureBar,
      'hasVRI': instance.hasVRI,
      'hasEndGun': instance.hasEndGun,
      'hasCornerSystem': instance.hasCornerSystem,
      'sectors': instance.sectors.map((e) => e.toJson()).toList(),
      'vriZones': instance.vriZones.map((e) => e.toJson()).toList(),
      if (instance.createdAt?.toIso8601String() case final value?)
        'createdAt': value,
      if (instance.updatedAt?.toIso8601String() case final value?)
        'updatedAt': value,
    };

const _$RotationDirectionEnumMap = {
  RotationDirection.clockwise: 'clockwise',
  RotationDirection.counterclockwise: 'counterclockwise',
};

const _$PivotTypeEnumMap = {
  PivotType.fullCircle: 'full_circle',
  PivotType.partialCircle: 'partial_circle',
  PivotType.corner: 'corner',
  PivotType.linear: 'linear',
};

_$PivotSectorImpl _$$PivotSectorImplFromJson(Map<String, dynamic> json) =>
    _$PivotSectorImpl(
      id: json['id'] as String,
      sectorNumber: (json['sectorNumber'] as num).toInt(),
      name: json['name'] as String? ?? '',
      nameAr: json['nameAr'] as String? ?? '',
      startAngle: (json['startAngle'] as num).toDouble(),
      endAngle: (json['endAngle'] as num).toDouble(),
      irrigationDepthMm: (json['irrigationDepthMm'] as num?)?.toDouble() ?? 25,
      applicationRateMmHr:
          (json['applicationRateMmHr'] as num?)?.toDouble() ?? 6.0,
      isEnabled: json['isEnabled'] as bool? ?? true,
      speedPercent: (json['speedPercent'] as num?)?.toDouble() ?? 100,
      cropType: json['cropType'] as String? ?? '',
      soilType: json['soilType'] as String? ?? '',
      ndviValue: (json['ndviValue'] as num?)?.toDouble(),
      soilMoisturePercent: (json['soilMoisturePercent'] as num?)?.toDouble(),
      color: json['color'] as String? ?? '#4CAF50',
    );

Map<String, dynamic> _$$PivotSectorImplToJson(_$PivotSectorImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'sectorNumber': instance.sectorNumber,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'startAngle': instance.startAngle,
      'endAngle': instance.endAngle,
      'irrigationDepthMm': instance.irrigationDepthMm,
      'applicationRateMmHr': instance.applicationRateMmHr,
      'isEnabled': instance.isEnabled,
      'speedPercent': instance.speedPercent,
      'cropType': instance.cropType,
      'soilType': instance.soilType,
      if (instance.ndviValue case final value?) 'ndviValue': value,
      if (instance.soilMoisturePercent case final value?)
        'soilMoisturePercent': value,
      'color': instance.color,
    };

_$VRIZoneImpl _$$VRIZoneImplFromJson(Map<String, dynamic> json) =>
    _$VRIZoneImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String? ?? '',
      coordinates: (json['coordinates'] as List<dynamic>)
          .map((e) =>
              (e as List<dynamic>).map((e) => (e as num).toDouble()).toList())
          .toList(),
      rateMultiplier: (json['rateMultiplier'] as num?)?.toDouble() ?? 1.0,
      targetSoilMoisturePercent:
          (json['targetSoilMoisturePercent'] as num?)?.toDouble() ?? 60,
      zoneType: $enumDecodeNullable(_$VRIZoneTypeEnumMap, json['zoneType']) ??
          VRIZoneType.normal,
      color: json['color'] as String? ?? '#2196F3',
      isActive: json['isActive'] as bool? ?? true,
    );

Map<String, dynamic> _$$VRIZoneImplToJson(_$VRIZoneImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'coordinates': instance.coordinates,
      'rateMultiplier': instance.rateMultiplier,
      'targetSoilMoisturePercent': instance.targetSoilMoisturePercent,
      'zoneType': _$VRIZoneTypeEnumMap[instance.zoneType]!,
      'color': instance.color,
      'isActive': instance.isActive,
    };

const _$VRIZoneTypeEnumMap = {
  VRIZoneType.normal: 'normal',
  VRIZoneType.highNeed: 'high_need',
  VRIZoneType.lowNeed: 'low_need',
  VRIZoneType.noIrrigation: 'no_irrigation',
  VRIZoneType.drainage: 'drainage',
};

_$PivotStatusImpl _$$PivotStatusImplFromJson(Map<String, dynamic> json) =>
    _$PivotStatusImpl(
      pivotId: json['pivotId'] as String,
      currentAngle: (json['currentAngle'] as num).toDouble(),
      operatingStatus:
          $enumDecode(_$PivotOperatingStatusEnumMap, json['operatingStatus']),
      direction: $enumDecode(_$PivotDirectionEnumMap, json['direction']),
      speedPercent: (json['speedPercent'] as num).toDouble(),
      timerHours: (json['timerHours'] as num?)?.toDouble() ?? 0,
      elapsedMinutes: (json['elapsedMinutes'] as num?)?.toDouble() ?? 0,
      currentFlowRateLph: (json['currentFlowRateLph'] as num?)?.toDouble() ?? 0,
      currentPressureBar: (json['currentPressureBar'] as num?)?.toDouble() ?? 0,
      endGunActive: json['endGunActive'] as bool? ?? false,
      cornerSystemActive: json['cornerSystemActive'] as bool? ?? false,
      waterAppliedM3: (json['waterAppliedM3'] as num?)?.toDouble() ?? 0,
      energyConsumedKwh: (json['energyConsumedKwh'] as num?)?.toDouble() ?? 0,
      estimatedCompletionTime: json['estimatedCompletionTime'] == null
          ? null
          : DateTime.parse(json['estimatedCompletionTime'] as String),
      lastUpdated: DateTime.parse(json['lastUpdated'] as String),
      activeAlerts: (json['activeAlerts'] as List<dynamic>?)
              ?.map((e) => PivotAlert.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      armEndLat: (json['armEndLat'] as num?)?.toDouble(),
      armEndLng: (json['armEndLng'] as num?)?.toDouble(),
    );

Map<String, dynamic> _$$PivotStatusImplToJson(_$PivotStatusImpl instance) =>
    <String, dynamic>{
      'pivotId': instance.pivotId,
      'currentAngle': instance.currentAngle,
      'operatingStatus':
          _$PivotOperatingStatusEnumMap[instance.operatingStatus]!,
      'direction': _$PivotDirectionEnumMap[instance.direction]!,
      'speedPercent': instance.speedPercent,
      'timerHours': instance.timerHours,
      'elapsedMinutes': instance.elapsedMinutes,
      'currentFlowRateLph': instance.currentFlowRateLph,
      'currentPressureBar': instance.currentPressureBar,
      'endGunActive': instance.endGunActive,
      'cornerSystemActive': instance.cornerSystemActive,
      'waterAppliedM3': instance.waterAppliedM3,
      'energyConsumedKwh': instance.energyConsumedKwh,
      if (instance.estimatedCompletionTime?.toIso8601String() case final value?)
        'estimatedCompletionTime': value,
      'lastUpdated': instance.lastUpdated.toIso8601String(),
      'activeAlerts': instance.activeAlerts.map((e) => e.toJson()).toList(),
      if (instance.armEndLat case final value?) 'armEndLat': value,
      if (instance.armEndLng case final value?) 'armEndLng': value,
    };

const _$PivotOperatingStatusEnumMap = {
  PivotOperatingStatus.stopped: 'stopped',
  PivotOperatingStatus.running: 'running',
  PivotOperatingStatus.paused: 'paused',
  PivotOperatingStatus.fault: 'fault',
  PivotOperatingStatus.maintenance: 'maintenance',
  PivotOperatingStatus.scheduled: 'scheduled',
};

const _$PivotDirectionEnumMap = {
  PivotDirection.forward: 'forward',
  PivotDirection.reverse: 'reverse',
  PivotDirection.stopped: 'stopped',
};

_$PivotAlertImpl _$$PivotAlertImplFromJson(Map<String, dynamic> json) =>
    _$PivotAlertImpl(
      id: json['id'] as String,
      pivotId: json['pivotId'] as String,
      alertType: $enumDecode(_$PivotAlertTypeEnumMap, json['alertType']),
      severity: $enumDecode(_$AlertSeverityEnumMap, json['severity']),
      message: json['message'] as String,
      messageAr: json['messageAr'] as String,
      towerNumber: (json['towerNumber'] as num?)?.toInt(),
      isAcknowledged: json['isAcknowledged'] as bool? ?? false,
      timestamp: DateTime.parse(json['timestamp'] as String),
      resolvedAt: json['resolvedAt'] == null
          ? null
          : DateTime.parse(json['resolvedAt'] as String),
    );

Map<String, dynamic> _$$PivotAlertImplToJson(_$PivotAlertImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'pivotId': instance.pivotId,
      'alertType': _$PivotAlertTypeEnumMap[instance.alertType]!,
      'severity': _$AlertSeverityEnumMap[instance.severity]!,
      'message': instance.message,
      'messageAr': instance.messageAr,
      if (instance.towerNumber case final value?) 'towerNumber': value,
      'isAcknowledged': instance.isAcknowledged,
      'timestamp': instance.timestamp.toIso8601String(),
      if (instance.resolvedAt?.toIso8601String() case final value?)
        'resolvedAt': value,
    };

const _$PivotAlertTypeEnumMap = {
  PivotAlertType.lowPressure: 'low_pressure',
  PivotAlertType.highPressure: 'high_pressure',
  PivotAlertType.powerFailure: 'power_failure',
  PivotAlertType.motorOverload: 'motor_overload',
  PivotAlertType.towerAlignment: 'tower_alignment',
  PivotAlertType.endGunFault: 'end_gun_fault',
  PivotAlertType.cornerSystemFault: 'corner_system_fault',
  PivotAlertType.lowFlow: 'low_flow',
  PivotAlertType.highFlow: 'high_flow',
  PivotAlertType.obstacleDetected: 'obstacle_detected',
  PivotAlertType.pipelineLeak: 'pipeline_leak',
  PivotAlertType.scheduledMaintenance: 'scheduled_maintenance',
  PivotAlertType.communicationLost: 'communication_lost',
};

const _$AlertSeverityEnumMap = {
  AlertSeverity.info: 'info',
  AlertSeverity.warning: 'warning',
  AlertSeverity.critical: 'critical',
  AlertSeverity.emergency: 'emergency',
};

_$PivotScheduleImpl _$$PivotScheduleImplFromJson(Map<String, dynamic> json) =>
    _$PivotScheduleImpl(
      id: json['id'] as String,
      pivotId: json['pivotId'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String? ?? '',
      scheduleType: $enumDecode(_$ScheduleTypeEnumMap, json['scheduleType']),
      runs: (json['runs'] as List<dynamic>)
          .map((e) => ScheduledRun.fromJson(e as Map<String, dynamic>))
          .toList(),
      isActive: json['isActive'] as bool? ?? true,
      createdAt: json['createdAt'] == null
          ? null
          : DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$PivotScheduleImplToJson(_$PivotScheduleImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'pivotId': instance.pivotId,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'scheduleType': _$ScheduleTypeEnumMap[instance.scheduleType]!,
      'runs': instance.runs.map((e) => e.toJson()).toList(),
      'isActive': instance.isActive,
      if (instance.createdAt?.toIso8601String() case final value?)
        'createdAt': value,
    };

const _$ScheduleTypeEnumMap = {
  ScheduleType.daily: 'daily',
  ScheduleType.weekly: 'weekly',
  ScheduleType.custom: 'custom',
  ScheduleType.sensorTriggered: 'sensor_triggered',
};

_$ScheduledRunImpl _$$ScheduledRunImplFromJson(Map<String, dynamic> json) =>
    _$ScheduledRunImpl(
      id: json['id'] as String,
      dayOfWeek: (json['dayOfWeek'] as num?)?.toInt(),
      startTime: json['startTime'] as String,
      durationHours: (json['durationHours'] as num).toDouble(),
      speedPercent: (json['speedPercent'] as num?)?.toDouble() ?? 100,
      direction:
          $enumDecodeNullable(_$PivotDirectionEnumMap, json['direction']) ??
              PivotDirection.forward,
      startAngle: (json['startAngle'] as num?)?.toDouble() ?? 0,
      endAngle: (json['endAngle'] as num?)?.toDouble() ?? 360,
      irrigationDepthMm: (json['irrigationDepthMm'] as num?)?.toDouble() ?? 25,
      isEnabled: json['isEnabled'] as bool? ?? true,
    );

Map<String, dynamic> _$$ScheduledRunImplToJson(_$ScheduledRunImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      if (instance.dayOfWeek case final value?) 'dayOfWeek': value,
      'startTime': instance.startTime,
      'durationHours': instance.durationHours,
      'speedPercent': instance.speedPercent,
      'direction': _$PivotDirectionEnumMap[instance.direction]!,
      'startAngle': instance.startAngle,
      'endAngle': instance.endAngle,
      'irrigationDepthMm': instance.irrigationDepthMm,
      'isEnabled': instance.isEnabled,
    };

_$PivotRunHistoryImpl _$$PivotRunHistoryImplFromJson(
        Map<String, dynamic> json) =>
    _$PivotRunHistoryImpl(
      id: json['id'] as String,
      pivotId: json['pivotId'] as String,
      startTime: DateTime.parse(json['startTime'] as String),
      endTime: json['endTime'] == null
          ? null
          : DateTime.parse(json['endTime'] as String),
      startAngle: (json['startAngle'] as num).toDouble(),
      endAngle: (json['endAngle'] as num?)?.toDouble(),
      direction: $enumDecode(_$PivotDirectionEnumMap, json['direction']),
      avgSpeedPercent: (json['avgSpeedPercent'] as num).toDouble(),
      waterAppliedM3: (json['waterAppliedM3'] as num).toDouble(),
      energyConsumedKwh: (json['energyConsumedKwh'] as num?)?.toDouble() ?? 0,
      status: $enumDecode(_$RunStatusEnumMap, json['status']),
      stopReason: json['stopReason'] as String?,
      alerts: (json['alerts'] as List<dynamic>?)
              ?.map((e) => PivotAlert.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
    );

Map<String, dynamic> _$$PivotRunHistoryImplToJson(
        _$PivotRunHistoryImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'pivotId': instance.pivotId,
      'startTime': instance.startTime.toIso8601String(),
      if (instance.endTime?.toIso8601String() case final value?)
        'endTime': value,
      'startAngle': instance.startAngle,
      if (instance.endAngle case final value?) 'endAngle': value,
      'direction': _$PivotDirectionEnumMap[instance.direction]!,
      'avgSpeedPercent': instance.avgSpeedPercent,
      'waterAppliedM3': instance.waterAppliedM3,
      'energyConsumedKwh': instance.energyConsumedKwh,
      'status': _$RunStatusEnumMap[instance.status]!,
      if (instance.stopReason case final value?) 'stopReason': value,
      'alerts': instance.alerts.map((e) => e.toJson()).toList(),
    };

const _$RunStatusEnumMap = {
  RunStatus.completed: 'completed',
  RunStatus.inProgress: 'in_progress',
  RunStatus.stopped: 'stopped',
  RunStatus.faulted: 'faulted',
};

_$PivotStatisticsImpl _$$PivotStatisticsImplFromJson(
        Map<String, dynamic> json) =>
    _$PivotStatisticsImpl(
      pivotId: json['pivotId'] as String,
      period: json['period'] as String,
      totalWaterM3: (json['totalWaterM3'] as num).toDouble(),
      totalEnergyKwh: (json['totalEnergyKwh'] as num).toDouble(),
      totalRunHours: (json['totalRunHours'] as num).toDouble(),
      completeCircles: (json['completeCircles'] as num).toInt(),
      avgIrrigationDepthMm: (json['avgIrrigationDepthMm'] as num).toDouble(),
      avgSpeedPercent: (json['avgSpeedPercent'] as num).toDouble(),
      efficiencyPercent: (json['efficiencyPercent'] as num).toDouble(),
      waterCost: (json['waterCost'] as num?)?.toDouble() ?? 0,
      energyCost: (json['energyCost'] as num?)?.toDouble() ?? 0,
      faultCount: (json['faultCount'] as num?)?.toInt() ?? 0,
      downtimeHours: (json['downtimeHours'] as num?)?.toDouble() ?? 0,
      periodStart: DateTime.parse(json['periodStart'] as String),
      periodEnd: DateTime.parse(json['periodEnd'] as String),
    );

Map<String, dynamic> _$$PivotStatisticsImplToJson(
        _$PivotStatisticsImpl instance) =>
    <String, dynamic>{
      'pivotId': instance.pivotId,
      'period': instance.period,
      'totalWaterM3': instance.totalWaterM3,
      'totalEnergyKwh': instance.totalEnergyKwh,
      'totalRunHours': instance.totalRunHours,
      'completeCircles': instance.completeCircles,
      'avgIrrigationDepthMm': instance.avgIrrigationDepthMm,
      'avgSpeedPercent': instance.avgSpeedPercent,
      'efficiencyPercent': instance.efficiencyPercent,
      'waterCost': instance.waterCost,
      'energyCost': instance.energyCost,
      'faultCount': instance.faultCount,
      'downtimeHours': instance.downtimeHours,
      'periodStart': instance.periodStart.toIso8601String(),
      'periodEnd': instance.periodEnd.toIso8601String(),
    };

_$PivotControlCommandImpl _$$PivotControlCommandImplFromJson(
        Map<String, dynamic> json) =>
    _$PivotControlCommandImpl(
      pivotId: json['pivotId'] as String,
      commandType: $enumDecode(_$PivotCommandTypeEnumMap, json['commandType']),
      speedPercent: (json['speedPercent'] as num?)?.toDouble(),
      targetAngle: (json['targetAngle'] as num?)?.toDouble(),
      direction:
          $enumDecodeNullable(_$PivotDirectionEnumMap, json['direction']),
      endGunEnabled: json['endGunEnabled'] as bool?,
      timerHours: (json['timerHours'] as num?)?.toDouble(),
      sectorNumbers: (json['sectorNumbers'] as List<dynamic>?)
          ?.map((e) => (e as num).toInt())
          .toList(),
      issuedBy: json['issuedBy'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );

Map<String, dynamic> _$$PivotControlCommandImplToJson(
        _$PivotControlCommandImpl instance) =>
    <String, dynamic>{
      'pivotId': instance.pivotId,
      'commandType': _$PivotCommandTypeEnumMap[instance.commandType]!,
      if (instance.speedPercent case final value?) 'speedPercent': value,
      if (instance.targetAngle case final value?) 'targetAngle': value,
      if (_$PivotDirectionEnumMap[instance.direction] case final value?)
        'direction': value,
      if (instance.endGunEnabled case final value?) 'endGunEnabled': value,
      if (instance.timerHours case final value?) 'timerHours': value,
      if (instance.sectorNumbers case final value?) 'sectorNumbers': value,
      'issuedBy': instance.issuedBy,
      'timestamp': instance.timestamp.toIso8601String(),
    };

const _$PivotCommandTypeEnumMap = {
  PivotCommandType.start: 'start',
  PivotCommandType.stop: 'stop',
  PivotCommandType.pause: 'pause',
  PivotCommandType.resume: 'resume',
  PivotCommandType.setSpeed: 'set_speed',
  PivotCommandType.setDirection: 'set_direction',
  PivotCommandType.moveToAngle: 'move_to_angle',
  PivotCommandType.toggleEndGun: 'toggle_end_gun',
  PivotCommandType.setTimer: 'set_timer',
  PivotCommandType.enableSectors: 'enable_sectors',
  PivotCommandType.disableSectors: 'disable_sectors',
  PivotCommandType.emergencyStop: 'emergency_stop',
};
