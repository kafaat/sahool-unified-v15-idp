/// Irrigation API Client - Integrated with Irrigation Smart Service (port 8094)
/// عميل API الري الذكي - متكامل مع خدمة الري
library;

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';

/// Irrigation Crop Data
/// بيانات محصول الري
class IrrigationCrop {
  final String id;
  final String nameAr;
  final String nameEn;
  final double kc;
  final Map<String, double>? kcStages;
  final int rootDepthMm;
  final double madFraction;

  IrrigationCrop({
    required this.id,
    required this.nameAr,
    required this.nameEn,
    required this.kc,
    this.kcStages,
    required this.rootDepthMm,
    required this.madFraction,
  });

  factory IrrigationCrop.fromJson(Map<String, dynamic> json) {
    return IrrigationCrop(
      id: json['id'] as String,
      nameAr: json['name_ar'] as String,
      nameEn: json['name_en'] as String,
      kc: (json['kc'] as num).toDouble(),
      kcStages: json['kc_stages'] != null
          ? Map<String, double>.from(
              (json['kc_stages'] as Map).map(
                (k, v) => MapEntry(k.toString(), (v as num).toDouble()),
              ),
            )
          : null,
      rootDepthMm: json['root_depth_mm'] as int,
      madFraction: (json['mad_fraction'] as num).toDouble(),
    );
  }
}

/// Irrigation Method
/// طريقة الري
class IrrigationMethod {
  final String id;
  final String nameAr;
  final String nameEn;
  final double efficiency;
  final String description;

  IrrigationMethod({
    required this.id,
    required this.nameAr,
    required this.nameEn,
    required this.efficiency,
    required this.description,
  });

  factory IrrigationMethod.fromJson(Map<String, dynamic> json) {
    return IrrigationMethod(
      id: json['id'] as String,
      nameAr: json['name_ar'] as String,
      nameEn: json['name_en'] as String,
      efficiency: (json['efficiency'] as num).toDouble(),
      description: json['description'] as String? ?? '',
    );
  }
}

/// Irrigation Calculation Request
/// طلب حساب الري
class IrrigationCalculationRequest {
  final String cropId;
  final String methodId;
  final double areaHectares;
  final double et0;
  final double? soilMoistureCurrent;
  final double? soilMoistureFieldCapacity;
  final String? growthStage;

  IrrigationCalculationRequest({
    required this.cropId,
    required this.methodId,
    required this.areaHectares,
    required this.et0,
    this.soilMoistureCurrent,
    this.soilMoistureFieldCapacity,
    this.growthStage,
  });

  Map<String, dynamic> toJson() => {
        'crop_id': cropId,
        'method_id': methodId,
        'area_hectares': areaHectares,
        'et0': et0,
        if (soilMoistureCurrent != null)
          'soil_moisture_current': soilMoistureCurrent,
        if (soilMoistureFieldCapacity != null)
          'soil_moisture_field_capacity': soilMoistureFieldCapacity,
        if (growthStage != null) 'growth_stage': growthStage,
      };
}

/// Irrigation Calculation Result
/// نتيجة حساب الري
class IrrigationCalculation {
  final double waterNeedMm;
  final double waterNeedLiters;
  final double waterNeedM3;
  final double irrigationDurationMinutes;
  final double etc;
  final String recommendation;
  final String recommendationAr;
  final DateTime nextIrrigationDate;

  IrrigationCalculation({
    required this.waterNeedMm,
    required this.waterNeedLiters,
    required this.waterNeedM3,
    required this.irrigationDurationMinutes,
    required this.etc,
    required this.recommendation,
    required this.recommendationAr,
    required this.nextIrrigationDate,
  });

  factory IrrigationCalculation.fromJson(Map<String, dynamic> json) {
    return IrrigationCalculation(
      waterNeedMm: (json['water_need_mm'] as num).toDouble(),
      waterNeedLiters: (json['water_need_liters'] as num).toDouble(),
      waterNeedM3: (json['water_need_m3'] as num).toDouble(),
      irrigationDurationMinutes:
          (json['irrigation_duration_minutes'] as num).toDouble(),
      etc: (json['etc'] as num).toDouble(),
      recommendation: json['recommendation'] as String,
      recommendationAr: json['recommendation_ar'] as String,
      nextIrrigationDate:
          DateTime.parse(json['next_irrigation_date'] as String),
    );
  }
}

/// Irrigation Schedule
/// جدول الري
class IrrigationSchedule {
  final String fieldId;
  final List<IrrigationEvent> events;
  final DateTime generatedAt;

  IrrigationSchedule({
    required this.fieldId,
    required this.events,
    required this.generatedAt,
  });

  factory IrrigationSchedule.fromJson(Map<String, dynamic> json) {
    return IrrigationSchedule(
      fieldId: json['field_id'] as String,
      events: (json['events'] as List)
          .map((e) => IrrigationEvent.fromJson(e))
          .toList(),
      generatedAt: DateTime.parse(json['generated_at'] as String),
    );
  }
}

/// Irrigation Event
/// حدث ري
class IrrigationEvent {
  final DateTime scheduledAt;
  final double durationMinutes;
  final double waterAmountLiters;
  final String status;
  final String? notes;

  IrrigationEvent({
    required this.scheduledAt,
    required this.durationMinutes,
    required this.waterAmountLiters,
    required this.status,
    this.notes,
  });

  factory IrrigationEvent.fromJson(Map<String, dynamic> json) {
    return IrrigationEvent(
      scheduledAt: DateTime.parse(json['scheduled_at'] as String),
      durationMinutes: (json['duration_minutes'] as num).toDouble(),
      waterAmountLiters: (json['water_amount_liters'] as num).toDouble(),
      status: json['status'] as String,
      notes: json['notes'] as String?,
    );
  }
}

/// Irrigation API Exception
/// استثناء API الري
class IrrigationApiException implements Exception {
  final String message;
  final int? statusCode;

  IrrigationApiException(this.message, {this.statusCode});

  @override
  String toString() =>
      'IrrigationApiException: $message (status: $statusCode)';
}

/// Irrigation Smart API Client
/// عميل API الري الذكي
class IrrigationApi {
  final http.Client _client;
  final String? _authToken;

  IrrigationApi({
    http.Client? client,
    String? authToken,
  })  : _client = client ?? http.Client(),
        _authToken = authToken;

  Map<String, String> get _headers => {
        ...ApiConfig.defaultHeaders,
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Reference Data
  // البيانات المرجعية
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get available crops for irrigation
  /// جلب المحاصيل المتاحة للري
  Future<List<IrrigationCrop>> getCrops() async {
    final response = await _client.get(
      Uri.parse(ApiConfig.irrigationCrops),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      final crops = json['data'] as List;
      return crops.map((c) => IrrigationCrop.fromJson(c)).toList();
    } else {
      throw IrrigationApiException(
        'فشل جلب قائمة المحاصيل',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get available irrigation methods
  /// جلب طرق الري المتاحة
  Future<List<IrrigationMethod>> getMethods() async {
    final response = await _client.get(
      Uri.parse(ApiConfig.irrigationMethods),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      final methods = json['data'] as List;
      return methods.map((m) => IrrigationMethod.fromJson(m)).toList();
    } else {
      throw IrrigationApiException(
        'فشل جلب طرق الري',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Calculations
  // الحسابات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate irrigation needs
  /// حساب احتياجات الري
  Future<IrrigationCalculation> calculate(
    IrrigationCalculationRequest request,
  ) async {
    final response = await _client.post(
      Uri.parse(ApiConfig.irrigationCalculate),
      headers: _headers,
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return IrrigationCalculation.fromJson(json['data']);
    } else {
      throw IrrigationApiException(
        'فشل حساب احتياجات الري',
        statusCode: response.statusCode,
      );
    }
  }

  /// Calculate water balance
  /// حساب توازن المياه
  Future<Map<String, dynamic>> calculateWaterBalance({
    required String fieldId,
    required DateTime from,
    required DateTime to,
  }) async {
    final uri = Uri.parse(ApiConfig.waterBalance).replace(
      queryParameters: {
        'field_id': fieldId,
        'from': from.toIso8601String(),
        'to': to.toIso8601String(),
      },
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return json['data'];
    } else {
      throw IrrigationApiException(
        'فشل حساب توازن المياه',
        statusCode: response.statusCode,
      );
    }
  }

  /// Calculate irrigation efficiency
  /// حساب كفاءة الري
  Future<Map<String, dynamic>> calculateEfficiency({
    required String methodId,
    required double appliedWaterMm,
    required double consumedWaterMm,
  }) async {
    final response = await _client.post(
      Uri.parse(ApiConfig.irrigationEfficiency),
      headers: _headers,
      body: jsonEncode({
        'method_id': methodId,
        'applied_water_mm': appliedWaterMm,
        'consumed_water_mm': consumedWaterMm,
      }),
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return json['data'];
    } else {
      throw IrrigationApiException(
        'فشل حساب كفاءة الري',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Schedule
  // الجدولة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get irrigation schedule for a field
  /// جلب جدول الري لحقل
  Future<IrrigationSchedule> getSchedule(String fieldId) async {
    final uri = Uri.parse(ApiConfig.irrigationSchedule).replace(
      queryParameters: {'field_id': fieldId},
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return IrrigationSchedule.fromJson(json['data']);
    } else {
      throw IrrigationApiException(
        'فشل جلب جدول الري',
        statusCode: response.statusCode,
      );
    }
  }

  /// Generate irrigation schedule
  /// إنشاء جدول ري
  Future<IrrigationSchedule> generateSchedule({
    required String fieldId,
    required String cropId,
    required String methodId,
    required int days,
  }) async {
    final response = await _client.post(
      Uri.parse(ApiConfig.irrigationSchedule),
      headers: _headers,
      body: jsonEncode({
        'field_id': fieldId,
        'crop_id': cropId,
        'method_id': methodId,
        'days': days,
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      final json = jsonDecode(response.body);
      return IrrigationSchedule.fromJson(json['data']);
    } else {
      throw IrrigationApiException(
        'فشل إنشاء جدول الري',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sensor Integration
  // تكامل المستشعرات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Record sensor reading
  /// تسجيل قراءة مستشعر
  Future<void> recordSensorReading({
    required String fieldId,
    required String sensorType,
    required double value,
    required String unit,
  }) async {
    final response = await _client.post(
      Uri.parse(ApiConfig.sensorReading),
      headers: _headers,
      body: jsonEncode({
        'field_id': fieldId,
        'sensor_type': sensorType,
        'value': value,
        'unit': unit,
        'timestamp': DateTime.now().toIso8601String(),
      }),
    );

    if (response.statusCode != 200 && response.statusCode != 201) {
      throw IrrigationApiException(
        'فشل تسجيل قراءة المستشعر',
        statusCode: response.statusCode,
      );
    }
  }

  /// Dispose the client
  void dispose() {
    _client.close();
  }
}
