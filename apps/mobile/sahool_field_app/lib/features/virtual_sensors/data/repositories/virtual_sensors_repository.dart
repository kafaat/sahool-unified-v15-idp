/// Virtual Sensors Repository - API Integration
/// مستودع المستشعرات الافتراضية - تكامل API
library;

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';
import '../models/virtual_sensor_models.dart';

/// Exception for virtual sensors API errors
/// استثناء أخطاء واجهة المستشعرات الافتراضية
class VirtualSensorsException implements Exception {
  final String message;
  final String messageAr;
  final int? statusCode;

  VirtualSensorsException(this.message, {this.messageAr = '', this.statusCode});

  @override
  String toString() => 'VirtualSensorsException: $message';
}

/// Repository for Virtual Sensors service
/// مستودع خدمة المستشعرات الافتراضية
class VirtualSensorsRepository {
  final http.Client _client;
  final String? _authToken;

  /// Base URL for virtual sensors service (port 8119 - Kong route)
  static String get _baseUrl => ApiConfig.useDirectServices
      ? ApiConfig.virtualSensorsServiceUrl
      : ApiConfig.effectiveBaseUrl;

  VirtualSensorsRepository({
    http.Client? client,
    String? authToken,
  })  : _client = client ?? http.Client(),
        _authToken = authToken;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // ET0 Calculations
  // حسابات التبخر-نتح المرجعي
  // ═══════════════════════════════════════════════════════════════════════════

  /// Calculate reference evapotranspiration (ET0)
  /// حساب التبخر-نتح المرجعي
  Future<ET0Response> calculateET0(WeatherInput weather) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/v1/et0/calculate'),
        headers: _headers,
        body: json.encode({
          'temperature_max': weather.temperatureMax,
          'temperature_min': weather.temperatureMin,
          'humidity': weather.humidity,
          'wind_speed': weather.windSpeed,
          if (weather.solarRadiation != null)
            'solar_radiation': weather.solarRadiation,
          if (weather.sunshineHours != null)
            'sunshine_hours': weather.sunshineHours,
          'latitude': weather.latitude,
          'altitude': weather.altitude,
          'date': (weather.date ?? DateTime.now()).toIso8601String().split('T')[0],
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return ET0Response(
          et0: (data['et0'] as num).toDouble(),
          et0Ar: data['et0_ar'] ?? '',
          method: data['method'] ?? 'FAO-56 Penman-Monteith',
          weatherSummary: data['weather_summary'] ?? {},
          calculationDate: DateTime.parse(data['calculation_date']),
        );
      }

      throw VirtualSensorsException(
        'Failed to calculate ET0',
        messageAr: 'فشل في حساب التبخر-نتح',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is VirtualSensorsException) rethrow;
      throw VirtualSensorsException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Crop Data
  // بيانات المحاصيل
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get supported crops with Kc values
  /// الحصول على المحاصيل المدعومة مع قيم Kc
  Future<List<CropKcOption>> getSupportedCrops() async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/v1/crops'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List crops = data['crops'] ?? [];
        return crops.map((e) => CropKcOption(
          cropId: e['crop_id'] ?? '',
          name: e['name'] ?? '',
          nameAr: e['name_ar'] ?? '',
          kcInitial: (e['kc_initial'] as num?)?.toDouble() ?? 0.3,
          kcMid: (e['kc_mid'] as num?)?.toDouble() ?? 1.0,
          kcEnd: (e['kc_end'] as num?)?.toDouble() ?? 0.5,
          rootDepthMax: (e['root_depth_max'] as num?)?.toDouble() ?? 1.0,
          criticalPeriods: List<String>.from(e['critical_periods'] ?? []),
        )).toList();
      }

      throw VirtualSensorsException(
        'Failed to fetch crops',
        messageAr: 'فشل في جلب المحاصيل',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is VirtualSensorsException) rethrow;
      throw VirtualSensorsException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Calculate crop evapotranspiration (ETc)
  /// حساب التبخر-نتح للمحصول
  Future<CropETcResponse> calculateCropETc({
    required WeatherInput weather,
    required String cropType,
    required GrowthStage growthStage,
    double fieldAreaHectares = 1.0,
    int? daysInStage,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/v1/etc/calculate').replace(
        queryParameters: {
          'crop_type': cropType,
          'growth_stage': growthStage.name,
          'field_area_hectares': fieldAreaHectares.toString(),
          if (daysInStage != null) 'days_in_stage': daysInStage.toString(),
        },
      );

      final response = await _client.post(
        uri,
        headers: _headers,
        body: json.encode({
          'temperature_max': weather.temperatureMax,
          'temperature_min': weather.temperatureMin,
          'humidity': weather.humidity,
          'wind_speed': weather.windSpeed,
          if (weather.solarRadiation != null)
            'solar_radiation': weather.solarRadiation,
          if (weather.sunshineHours != null)
            'sunshine_hours': weather.sunshineHours,
          'latitude': weather.latitude,
          'altitude': weather.altitude,
          'date': (weather.date ?? DateTime.now()).toIso8601String().split('T')[0],
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return CropETcResponse(
          cropType: data['crop_type'] ?? '',
          cropNameAr: data['crop_name_ar'] ?? '',
          growthStage: data['growth_stage'] ?? '',
          kc: (data['kc'] as num?)?.toDouble() ?? 1.0,
          et0: (data['et0'] as num?)?.toDouble() ?? 0.0,
          etc: (data['etc'] as num?)?.toDouble() ?? 0.0,
          dailyWaterNeedLiters: (data['daily_water_need_liters'] as num?)?.toDouble() ?? 0.0,
          dailyWaterNeedM3: (data['daily_water_need_m3'] as num?)?.toDouble() ?? 0.0,
          weeklyWaterNeedM3: (data['weekly_water_need_m3'] as num?)?.toDouble() ?? 0.0,
          criticalPeriod: data['critical_period'] ?? false,
          notes: data['notes'] ?? '',
          notesAr: data['notes_ar'] ?? '',
        );
      }

      throw VirtualSensorsException(
        'Failed to calculate ETc',
        messageAr: 'فشل في حساب التبخر-نتح للمحصول',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is VirtualSensorsException) rethrow;
      throw VirtualSensorsException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Soil Data
  // بيانات التربة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get supported soil types
  /// الحصول على أنواع التربة المدعومة
  Future<List<SoilTypeInfo>> getSoilTypes() async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/v1/soils'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List soils = data['soils'] ?? [];
        return soils.map((e) => SoilTypeInfo(
          soilType: e['soil_type'] ?? '',
          nameAr: e['name_ar'] ?? '',
          fieldCapacity: (e['field_capacity'] as num?)?.toDouble() ?? 0.27,
          wiltingPoint: (e['wilting_point'] as num?)?.toDouble() ?? 0.12,
          availableWaterCapacity: (e['available_water_capacity'] as num?)?.toDouble() ?? 0.15,
          infiltrationRateMmHr: (e['infiltration_rate_mm_hr'] as num?)?.toDouble() ?? 13.0,
        )).toList();
      }

      throw VirtualSensorsException(
        'Failed to fetch soil types',
        messageAr: 'فشل في جلب أنواع التربة',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is VirtualSensorsException) rethrow;
      throw VirtualSensorsException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation Methods
  // طرق الري
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get irrigation methods with efficiencies
  /// الحصول على طرق الري مع كفاءاتها
  Future<List<IrrigationMethodInfo>> getIrrigationMethods() async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/v1/irrigation-methods'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List methods = data['methods'] ?? [];
        return methods.map((e) => IrrigationMethodInfo(
          method: e['method'] ?? '',
          efficiency: (e['efficiency'] as num?)?.toDouble() ?? 0.7,
          efficiencyPercent: e['efficiency_percent'] ?? '70%',
        )).toList();
      }

      throw VirtualSensorsException(
        'Failed to fetch irrigation methods',
        messageAr: 'فشل في جلب طرق الري',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is VirtualSensorsException) rethrow;
      throw VirtualSensorsException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation Recommendation
  // توصيات الري
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get complete irrigation recommendation
  /// الحصول على توصية ري شاملة
  Future<IrrigationRecommendation> getIrrigationRecommendation({
    required String cropType,
    required GrowthStage growthStage,
    required SoilType soilType,
    required IrrigationMethod irrigationMethod,
    required WeatherInput weather,
    double fieldAreaHectares = 1.0,
    DateTime? lastIrrigationDate,
    double? lastIrrigationAmount,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/v1/irrigation/recommend'),
        headers: _headers,
        body: json.encode({
          'crop_type': cropType,
          'growth_stage': growthStage.name,
          'soil_type': soilType.name,
          'irrigation_method': irrigationMethod.name,
          'field_area_hectares': fieldAreaHectares,
          if (lastIrrigationDate != null)
            'last_irrigation_date': lastIrrigationDate.toIso8601String().split('T')[0],
          if (lastIrrigationAmount != null)
            'last_irrigation_amount': lastIrrigationAmount,
          'weather': {
            'temperature_max': weather.temperatureMax,
            'temperature_min': weather.temperatureMin,
            'humidity': weather.humidity,
            'wind_speed': weather.windSpeed,
            if (weather.solarRadiation != null)
              'solar_radiation': weather.solarRadiation,
            if (weather.sunshineHours != null)
              'sunshine_hours': weather.sunshineHours,
            'latitude': weather.latitude,
            'altitude': weather.altitude,
            'date': (weather.date ?? DateTime.now()).toIso8601String().split('T')[0],
          },
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return IrrigationRecommendation(
          recommendationId: data['recommendation_id'] ?? '',
          timestamp: DateTime.parse(data['timestamp']),
          cropType: data['crop_type'] ?? '',
          cropNameAr: data['crop_name_ar'] ?? '',
          growthStage: data['growth_stage'] ?? '',
          fieldAreaHectares: (data['field_area_hectares'] as num?)?.toDouble() ?? 1.0,
          et0: (data['et0'] as num?)?.toDouble() ?? 0.0,
          kc: (data['kc'] as num?)?.toDouble() ?? 1.0,
          etc: (data['etc'] as num?)?.toDouble() ?? 0.0,
          soilType: data['soil_type'] ?? '',
          soilTypeAr: data['soil_type_ar'] ?? '',
          estimatedMoisture: (data['estimated_moisture'] as num?)?.toDouble() ?? 0.0,
          moistureDepletionPercent: (data['moisture_depletion_percent'] as num?)?.toDouble() ?? 0.0,
          irrigationNeeded: data['irrigation_needed'] ?? false,
          urgency: _parseUrgency(data['urgency']),
          urgencyAr: data['urgency_ar'] ?? '',
          recommendedAmountMm: (data['recommended_amount_mm'] as num?)?.toDouble() ?? 0.0,
          recommendedAmountLiters: (data['recommended_amount_liters'] as num?)?.toDouble() ?? 0.0,
          recommendedAmountM3: (data['recommended_amount_m3'] as num?)?.toDouble() ?? 0.0,
          grossIrrigationMm: (data['gross_irrigation_mm'] as num?)?.toDouble() ?? 0.0,
          optimalTime: data['optimal_time'] ?? '',
          optimalTimeAr: data['optimal_time_ar'] ?? '',
          nextIrrigationDays: data['next_irrigation_days'] ?? 0,
          advice: data['advice'] ?? '',
          adviceAr: data['advice_ar'] ?? '',
          warnings: List<String>.from(data['warnings'] ?? []),
          warningsAr: List<String>.from(data['warnings_ar'] ?? []),
        );
      }

      throw VirtualSensorsException(
        'Failed to get irrigation recommendation',
        messageAr: 'فشل في الحصول على توصية الري',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is VirtualSensorsException) rethrow;
      throw VirtualSensorsException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Quick irrigation check
  /// فحص سريع للري
  Future<QuickIrrigationCheck> quickIrrigationCheck({
    required String cropType,
    required GrowthStage growthStage,
    SoilType soilType = SoilType.loam,
    required int daysSinceIrrigation,
    required double temperature,
    double humidity = 50,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/v1/irrigation/quick-check').replace(
        queryParameters: {
          'crop_type': cropType,
          'growth_stage': growthStage.name,
          'soil_type': soilType.name,
          'days_since_irrigation': daysSinceIrrigation.toString(),
          'temperature': temperature.toString(),
          'humidity': humidity.toString(),
        },
      );

      final response = await _client.get(uri, headers: _headers);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return QuickIrrigationCheck(
          cropType: data['crop_type'] ?? '',
          cropNameAr: data['crop_name_ar'] ?? '',
          growthStage: data['growth_stage'] ?? '',
          daysSinceIrrigation: data['days_since_irrigation'] ?? 0,
          estimatedEt0: (data['estimated_et0'] as num?)?.toDouble() ?? 0.0,
          kc: (data['kc'] as num?)?.toDouble() ?? 1.0,
          estimatedEtc: (data['estimated_etc'] as num?)?.toDouble() ?? 0.0,
          estimatedWaterLossMm: (data['estimated_water_loss_mm'] as num?)?.toDouble() ?? 0.0,
          estimatedDepletionPercent: (data['estimated_depletion_percent'] as num?)?.toDouble() ?? 0.0,
          status: data['status'] ?? '',
          statusAr: data['status_ar'] ?? '',
          needsIrrigation: data['needs_irrigation'] ?? false,
          recommendation: data['recommendation'] ?? '',
          recommendationAr: data['recommendation_ar'] ?? '',
        );
      }

      throw VirtualSensorsException(
        'Failed to perform quick check',
        messageAr: 'فشل في إجراء الفحص السريع',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is VirtualSensorsException) rethrow;
      throw VirtualSensorsException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Service Health
  // صحة الخدمة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if service is available
  /// التحقق من توفر الخدمة
  Future<bool> isServiceAvailable() async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/healthz'),
        headers: _headers,
      ).timeout(const Duration(seconds: 5));

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Helpers
  // ═══════════════════════════════════════════════════════════════════════════

  UrgencyLevel _parseUrgency(String? value) {
    switch (value) {
      case 'none':
        return UrgencyLevel.none;
      case 'low':
        return UrgencyLevel.low;
      case 'medium':
        return UrgencyLevel.medium;
      case 'high':
        return UrgencyLevel.high;
      case 'critical':
        return UrgencyLevel.critical;
      default:
        return UrgencyLevel.none;
    }
  }

  void dispose() {
    _client.close();
  }
}
