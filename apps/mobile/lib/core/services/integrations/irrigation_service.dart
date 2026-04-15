/// SAHOOL Irrigation Service Integration
/// تكامل خدمة الري الذكي
///
/// Handles irrigation-related operations:
/// - Irrigation calculations
/// - Water balance tracking
/// - Irrigation scheduling
/// - Sensor readings
/// - Efficiency analysis
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../network/api_result.dart';
import '../service_connector.dart';

/// Irrigation calculation result model
class IrrigationCalculation {
  final String fieldId;
  final double recommendedAmount;
  final String unit;
  final double? etc;
  final double? et0;
  final double? kc;
  final int? duration;
  final String? durationUnit;
  final String? method;
  final String? methodAr;
  final String? recommendation;
  final String? recommendationAr;
  final DateTime calculationDate;
  final Map<String, dynamic>? factors;

  const IrrigationCalculation({
    required this.fieldId,
    required this.recommendedAmount,
    required this.unit,
    this.etc,
    this.et0,
    this.kc,
    this.duration,
    this.durationUnit,
    this.method,
    this.methodAr,
    this.recommendation,
    this.recommendationAr,
    required this.calculationDate,
    this.factors,
  });

  factory IrrigationCalculation.fromJson(Map<String, dynamic> json) {
    return IrrigationCalculation(
      fieldId: json['field_id'] as String? ?? '',
      recommendedAmount: (json['recommended_amount'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit'] as String? ?? 'mm',
      etc: (json['etc'] as num?)?.toDouble(),
      et0: (json['et0'] as num?)?.toDouble(),
      kc: (json['kc'] as num?)?.toDouble(),
      duration: (json['duration'] as num?)?.toInt(),
      durationUnit: json['duration_unit'] as String?,
      method: json['method'] as String?,
      methodAr: json['method_ar'] as String?,
      recommendation: json['recommendation'] as String?,
      recommendationAr: json['recommendation_ar'] as String?,
      calculationDate: json['calculation_date'] != null
          ? DateTime.tryParse(json['calculation_date'] as String) ?? DateTime.now()
          : DateTime.now(),
      factors: json['factors'] as Map<String, dynamic>?,
    );
  }
}

/// Water balance model
class WaterBalance {
  final String fieldId;
  final double currentMoisture;
  final double fieldCapacity;
  final double wiltingPoint;
  final double availableWater;
  final double deficitAmount;
  final String? status;
  final String? statusAr;
  final int? daysUntilStress;
  final DateTime measurementDate;

  const WaterBalance({
    required this.fieldId,
    required this.currentMoisture,
    required this.fieldCapacity,
    required this.wiltingPoint,
    required this.availableWater,
    required this.deficitAmount,
    this.status,
    this.statusAr,
    this.daysUntilStress,
    required this.measurementDate,
  });

  factory WaterBalance.fromJson(Map<String, dynamic> json) {
    return WaterBalance(
      fieldId: json['field_id'] as String? ?? '',
      currentMoisture: (json['current_moisture'] as num?)?.toDouble() ?? 0.0,
      fieldCapacity: (json['field_capacity'] as num?)?.toDouble() ?? 0.0,
      wiltingPoint: (json['wilting_point'] as num?)?.toDouble() ?? 0.0,
      availableWater: (json['available_water'] as num?)?.toDouble() ?? 0.0,
      deficitAmount: (json['deficit_amount'] as num?)?.toDouble() ?? 0.0,
      status: json['status'] as String?,
      statusAr: json['status_ar'] as String?,
      daysUntilStress: (json['days_until_stress'] as num?)?.toInt(),
      measurementDate: json['measurement_date'] != null
          ? DateTime.tryParse(json['measurement_date'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  /// Get moisture percentage
  double get moisturePercentage => (currentMoisture / fieldCapacity) * 100;

  /// Is irrigation needed
  bool get needsIrrigation => status?.toLowerCase() == 'deficit' || deficitAmount > 0;
}

/// Irrigation schedule item model
class IrrigationScheduleItem {
  final String id;
  final String fieldId;
  final DateTime scheduledTime;
  final double amount;
  final String unit;
  final int? duration;
  final String? durationUnit;
  final String? method;
  final String? status;
  final String? statusAr;
  final bool isAutomatic;
  final DateTime? completedAt;
  final Map<String, dynamic>? metadata;

  const IrrigationScheduleItem({
    required this.id,
    required this.fieldId,
    required this.scheduledTime,
    required this.amount,
    required this.unit,
    this.duration,
    this.durationUnit,
    this.method,
    this.status,
    this.statusAr,
    this.isAutomatic = false,
    this.completedAt,
    this.metadata,
  });

  factory IrrigationScheduleItem.fromJson(Map<String, dynamic> json) {
    return IrrigationScheduleItem(
      id: json['id'] as String? ?? '',
      fieldId: json['field_id'] as String? ?? '',
      scheduledTime: DateTime.tryParse(json['scheduled_time'] as String) ?? DateTime.now(),
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit'] as String? ?? 'mm',
      duration: (json['duration'] as num?)?.toInt(),
      durationUnit: json['duration_unit'] as String?,
      method: json['method'] as String?,
      status: json['status'] as String?,
      statusAr: json['status_ar'] as String?,
      isAutomatic: json['is_automatic'] as bool? ?? false,
      completedAt: json['completed_at'] != null
          ? DateTime.tryParse(json['completed_at'] as String)
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'field_id': fieldId,
        'scheduled_time': scheduledTime.toIso8601String(),
        'amount': amount,
        'unit': unit,
        if (duration != null) 'duration': duration,
        if (durationUnit != null) 'duration_unit': durationUnit,
        if (method != null) 'method': method,
        if (status != null) 'status': status,
        'is_automatic': isAutomatic,
        if (metadata != null) 'metadata': metadata,
      };
}

/// Irrigation method model
class IrrigationMethod {
  final String id;
  final String name;
  final String? nameAr;
  final String? description;
  final String? descriptionAr;
  final double efficiency;
  final String? applicability;
  final List<String>? pros;
  final List<String>? cons;

  const IrrigationMethod({
    required this.id,
    required this.name,
    this.nameAr,
    this.description,
    this.descriptionAr,
    required this.efficiency,
    this.applicability,
    this.pros,
    this.cons,
  });

  factory IrrigationMethod.fromJson(Map<String, dynamic> json) {
    return IrrigationMethod(
      id: json['id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      nameAr: json['name_ar'] as String?,
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      efficiency: (json['efficiency'] as num?)?.toDouble() ?? 0.0,
      applicability: json['applicability'] as String?,
      pros: (json['pros'] as List?)?.cast<String>(),
      cons: (json['cons'] as List?)?.cast<String>(),
    );
  }
}

/// Sensor reading model
class SensorReading {
  final String sensorId;
  final String type;
  final double value;
  final String unit;
  final DateTime timestamp;
  final String? fieldId;
  final Map<String, dynamic>? location;
  final String? status;

  const SensorReading({
    required this.sensorId,
    required this.type,
    required this.value,
    required this.unit,
    required this.timestamp,
    this.fieldId,
    this.location,
    this.status,
  });

  factory SensorReading.fromJson(Map<String, dynamic> json) {
    return SensorReading(
      sensorId: json['sensor_id'] as String? ?? '',
      type: json['type'] as String? ?? '',
      value: (json['value'] as num?)?.toDouble() ?? 0.0,
      unit: json['unit'] as String? ?? '',
      timestamp: DateTime.tryParse(json['timestamp'] as String) ?? DateTime.now(),
      fieldId: json['field_id'] as String?,
      location: json['location'] as Map<String, dynamic>?,
      status: json['status'] as String?,
    );
  }
}

/// Irrigation efficiency analysis
class IrrigationEfficiency {
  final String fieldId;
  final double applicationEfficiency;
  final double distributionUniformity;
  final double waterUseEfficiency;
  final String? rating;
  final String? ratingAr;
  final List<String>? recommendations;
  final List<String>? recommendationsAr;
  final DateTime analysisDate;

  const IrrigationEfficiency({
    required this.fieldId,
    required this.applicationEfficiency,
    required this.distributionUniformity,
    required this.waterUseEfficiency,
    this.rating,
    this.ratingAr,
    this.recommendations,
    this.recommendationsAr,
    required this.analysisDate,
  });

  factory IrrigationEfficiency.fromJson(Map<String, dynamic> json) {
    return IrrigationEfficiency(
      fieldId: json['field_id'] as String? ?? '',
      applicationEfficiency: (json['application_efficiency'] as num?)?.toDouble() ?? 0.0,
      distributionUniformity: (json['distribution_uniformity'] as num?)?.toDouble() ?? 0.0,
      waterUseEfficiency: (json['water_use_efficiency'] as num?)?.toDouble() ?? 0.0,
      rating: json['rating'] as String?,
      ratingAr: json['rating_ar'] as String?,
      recommendations: (json['recommendations'] as List?)?.cast<String>(),
      recommendationsAr: (json['recommendations_ar'] as List?)?.cast<String>(),
      analysisDate: json['analysis_date'] != null
          ? DateTime.tryParse(json['analysis_date'] as String) ?? DateTime.now()
          : DateTime.now(),
    );
  }
}

/// Irrigation Service Connector
/// موصل خدمة الري الذكي
class IrrigationServiceConnector extends ServiceConnector {
  IrrigationServiceConnector({required super.ref}) : super(serviceId: 'irrigation');

  /// Calculate irrigation requirements
  /// حساب متطلبات الري
  Future<ApiResult<IrrigationCalculation>> calculate({
    required String fieldId,
    String? cropType,
    String? growthStage,
    String? irrigationMethod,
    double? soilMoisture,
    Map<String, dynamic>? weatherData,
  }) async {
    return post(
      getEndpoint('calculate') ?? '/api/v1/irrigation/calculate',
      data: {
        'field_id': fieldId,
        if (cropType != null) 'crop_type': cropType,
        if (growthStage != null) 'growth_stage': growthStage,
        if (irrigationMethod != null) 'irrigation_method': irrigationMethod,
        if (soilMoisture != null) 'soil_moisture': soilMoisture,
        if (weatherData != null) 'weather_data': weatherData,
      },
      parser: (data) => IrrigationCalculation.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get water balance for field
  /// الحصول على توازن المياه للحقل
  Future<ApiResult<WaterBalance>> getWaterBalance(String fieldId) async {
    return get(
      getEndpoint('water-balance') ?? '/api/v1/irrigation/water-balance',
      queryParameters: {'field_id': fieldId},
      parser: (data) => WaterBalance.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get irrigation schedule
  /// الحصول على جدول الري
  Future<ApiResult<List<IrrigationScheduleItem>>> getSchedule({
    String? fieldId,
    DateTime? startDate,
    DateTime? endDate,
    String? status,
  }) async {
    final queryParams = <String, dynamic>{
      if (fieldId != null) 'field_id': fieldId,
      if (startDate != null) 'start_date': startDate.toIso8601String(),
      if (endDate != null) 'end_date': endDate.toIso8601String(),
      if (status != null) 'status': status,
    };

    return get(
      getEndpoint('schedule') ?? '/api/v1/irrigation/schedule',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data
              .map((e) => IrrigationScheduleItem.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        if (data is Map && data['schedule'] != null) {
          return (data['schedule'] as List? ?? [])
              .map((e) => IrrigationScheduleItem.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <IrrigationScheduleItem>[];
      },
    );
  }

  /// Create irrigation schedule
  /// إنشاء جدول ري
  Future<ApiResult<IrrigationScheduleItem>> createSchedule(IrrigationScheduleItem item) async {
    return post(
      getEndpoint('schedule') ?? '/api/v1/irrigation/schedule',
      data: item.toJson(),
      parser: (data) => IrrigationScheduleItem.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Update irrigation schedule
  /// تحديث جدول الري
  Future<ApiResult<IrrigationScheduleItem>> updateSchedule(
    String scheduleId,
    Map<String, dynamic> updates,
  ) async {
    return patch(
      '${getEndpoint('schedule') ?? '/api/v1/irrigation/schedule'}/$scheduleId',
      data: updates,
      parser: (data) => IrrigationScheduleItem.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Delete irrigation schedule
  /// حذف جدول الري
  Future<ApiResult<bool>> deleteSchedule(String scheduleId) async {
    return delete(
      '${getEndpoint('schedule') ?? '/api/v1/irrigation/schedule'}/$scheduleId',
      parser: (_) => true,
    );
  }

  /// Get irrigation methods
  /// الحصول على طرق الري
  Future<ApiResult<List<IrrigationMethod>>> getMethods() async {
    return get(
      getEndpoint('methods') ?? '/api/v1/irrigation/methods',
      parser: (data) {
        if (data is List) {
          return data.map((e) => IrrigationMethod.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['methods'] != null) {
          return (data['methods'] as List? ?? [])
              .map((e) => IrrigationMethod.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <IrrigationMethod>[];
      },
    );
  }

  /// Get supported crops for irrigation
  /// الحصول على المحاصيل المدعومة للري
  Future<ApiResult<List<Map<String, dynamic>>>> getCrops() async {
    return get(
      getEndpoint('crops') ?? '/api/v1/irrigation/crops',
      parser: (data) {
        if (data is List) {
          return data.cast<Map<String, dynamic>>();
        }
        if (data is Map && data['crops'] != null) {
          return (data['crops'] as List? ?? []).cast<Map<String, dynamic>>();
        }
        return <Map<String, dynamic>>[];
      },
    );
  }

  /// Submit sensor reading
  /// إرسال قراءة المستشعر
  Future<ApiResult<SensorReading>> submitSensorReading(SensorReading reading) async {
    return post(
      getEndpoint('sensor-reading') ?? '/api/v1/irrigation/sensor-reading',
      data: {
        'sensor_id': reading.sensorId,
        'type': reading.type,
        'value': reading.value,
        'unit': reading.unit,
        'timestamp': reading.timestamp.toIso8601String(),
        if (reading.fieldId != null) 'field_id': reading.fieldId,
        if (reading.location != null) 'location': reading.location,
      },
      parser: (data) => SensorReading.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get irrigation efficiency analysis
  /// الحصول على تحليل كفاءة الري
  Future<ApiResult<IrrigationEfficiency>> getEfficiency(String fieldId) async {
    return get(
      getEndpoint('efficiency') ?? '/api/v1/irrigation/efficiency',
      queryParameters: {'field_id': fieldId},
      parser: (data) => IrrigationEfficiency.fromJson(data as Map<String, dynamic>),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Irrigation Service Provider
final irrigationServiceProvider = Provider<IrrigationServiceConnector>((ref) {
  return IrrigationServiceConnector(ref: ref);
});

/// Water Balance Provider
final waterBalanceProvider = FutureProvider.family<WaterBalance?, String>((ref, fieldId) async {
  final service = ref.watch(irrigationServiceProvider);
  final result = await service.getWaterBalance(fieldId);
  return result.dataOrNull;
});

/// Irrigation Schedule Provider
final irrigationScheduleProvider =
    FutureProvider.family<List<IrrigationScheduleItem>, String?>((ref, fieldId) async {
  final service = ref.watch(irrigationServiceProvider);
  final result = await service.getSchedule(fieldId: fieldId);
  return result.dataOrNull ?? [];
});

/// Upcoming Irrigation Provider
final upcomingIrrigationProvider =
    FutureProvider.family<List<IrrigationScheduleItem>, String?>((ref, fieldId) async {
  final service = ref.watch(irrigationServiceProvider);
  final result = await service.getSchedule(
    fieldId: fieldId,
    startDate: DateTime.now(),
    status: 'scheduled',
  );
  return result.dataOrNull ?? [];
});

/// Irrigation Methods Provider
final irrigationMethodsProvider = FutureProvider<List<IrrigationMethod>>((ref) async {
  final service = ref.watch(irrigationServiceProvider);
  final result = await service.getMethods();
  return result.dataOrNull ?? [];
});

/// Irrigation Efficiency Provider
final irrigationEfficiencyProvider =
    FutureProvider.family<IrrigationEfficiency?, String>((ref, fieldId) async {
  final service = ref.watch(irrigationServiceProvider);
  final result = await service.getEfficiency(fieldId);
  return result.dataOrNull;
});

/// Fields Needing Irrigation Provider
final fieldsNeedingIrrigationProvider = FutureProvider<List<String>>((ref) async {
  // This would typically check water balance for all fields
  // For now, return empty list - implement based on actual requirements
  return [];
});
