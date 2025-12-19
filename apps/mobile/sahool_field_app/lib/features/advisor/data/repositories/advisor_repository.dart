/// Advisor Repository - Fertilizer & Irrigation APIs
/// مستودع المستشار - واجهات التسميد والري
library;

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';
import '../models/fertilizer_models.dart';
import '../models/irrigation_models.dart';

/// Exception for advisor API errors
/// استثناء أخطاء واجهة المستشار
class AdvisorException implements Exception {
  final String message;
  final String messageAr;
  final int? statusCode;

  AdvisorException(this.message, {this.messageAr = '', this.statusCode});

  @override
  String toString() => 'AdvisorException: $message';
}

/// Repository for fertilizer and irrigation advisor services
/// مستودع خدمات مستشار التسميد والري
class AdvisorRepository {
  final http.Client _client;
  final String? _authToken;
  final String? _tenantId;

  AdvisorRepository({
    http.Client? client,
    String? authToken,
    String? tenantId,
  })  : _client = client ?? http.Client(),
        _authToken = authToken,
        _tenantId = tenantId;

  Map<String, String> get _headers => {
        ...ApiConfig.defaultHeaders,
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
        if (_tenantId != null) 'X-Tenant-Id': _tenantId!,
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Fertilizer Advisor APIs (port 8093)
  // واجهات مستشار التسميد
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get available crop types for fertilizer recommendations
  /// الحصول على أنواع المحاصيل المتاحة لتوصيات التسميد
  Future<List<CropTypeOption>> getFertilizerCrops() async {
    try {
      final response = await _client.get(
        Uri.parse(ApiConfig.fertilizerCrops),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as List;
        return data.map((e) => CropTypeOption.fromJson(e)).toList();
      }
      throw AdvisorException(
        'Failed to fetch crops',
        messageAr: 'فشل في جلب المحاصيل',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Get fertilizer recommendation for a field
  /// الحصول على توصية التسميد للحقل
  Future<FertilizerRecommendation> getFertilizerRecommendation(
    FertilizerRequest request,
  ) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.fertilizerRecommendation),
        headers: _headers,
        body: json.encode(request.toJson()),
      );

      if (response.statusCode == 200) {
        return FertilizerRecommendation.fromJson(json.decode(response.body));
      }
      throw AdvisorException(
        'Failed to get recommendation',
        messageAr: 'فشل في الحصول على التوصية',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Interpret soil analysis results
  /// تفسير نتائج تحليل التربة
  Future<SoilInterpretation> interpretSoil(SoilAnalysis soilData) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.soilInterpretation),
        headers: _headers,
        body: json.encode(soilData.toJson()),
      );

      if (response.statusCode == 200) {
        return SoilInterpretation.fromJson(json.decode(response.body));
      }
      throw AdvisorException(
        'Failed to interpret soil',
        messageAr: 'فشل في تفسير التربة',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Get deficiency symptoms for a nutrient
  /// الحصول على أعراض النقص لعنصر غذائي
  Future<List<DeficiencySymptom>> getDeficiencySymptoms({
    String? nutrient,
    String? cropType,
  }) async {
    try {
      final queryParams = <String, String>{};
      if (nutrient != null) queryParams['nutrient'] = nutrient;
      if (cropType != null) queryParams['crop'] = cropType;

      final uri = Uri.parse(ApiConfig.deficiencySymptoms)
          .replace(queryParameters: queryParams.isNotEmpty ? queryParams : null);

      final response = await _client.get(uri, headers: _headers);

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as List;
        return data.map((e) => DeficiencySymptom.fromJson(e)).toList();
      }
      throw AdvisorException(
        'Failed to fetch symptoms',
        messageAr: 'فشل في جلب الأعراض',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation Smart APIs (port 8094)
  // واجهات الري الذكي
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get crop water requirements
  /// الحصول على متطلبات المحصول المائية
  Future<List<CropWaterRequirement>> getIrrigationCrops() async {
    try {
      final response = await _client.get(
        Uri.parse(ApiConfig.irrigationCrops),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as List;
        return data.map((e) => CropWaterRequirement.fromJson(e)).toList();
      }
      throw AdvisorException(
        'Failed to fetch irrigation crops',
        messageAr: 'فشل في جلب محاصيل الري',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Get available irrigation methods
  /// الحصول على طرق الري المتاحة
  Future<List<IrrigationMethodOption>> getIrrigationMethods() async {
    try {
      final response = await _client.get(
        Uri.parse(ApiConfig.irrigationMethods),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as List;
        return data.map((e) => IrrigationMethodOption.fromJson(e)).toList();
      }
      throw AdvisorException(
        'Failed to fetch irrigation methods',
        messageAr: 'فشل في جلب طرق الري',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Calculate irrigation requirements
  /// حساب متطلبات الري
  Future<IrrigationCalculation> calculateIrrigation(
    IrrigationRequest request,
  ) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.irrigationCalculate),
        headers: _headers,
        body: json.encode(request.toJson()),
      );

      if (response.statusCode == 200) {
        return IrrigationCalculation.fromJson(json.decode(response.body));
      }
      throw AdvisorException(
        'Failed to calculate irrigation',
        messageAr: 'فشل في حساب الري',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Get water balance for a field
  /// الحصول على التوازن المائي للحقل
  Future<WaterBalance> getWaterBalance({
    required String fieldId,
    required double soilMoisture,
    required String soilType,
    required String cropType,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.waterBalance),
        headers: _headers,
        body: json.encode({
          'field_id': fieldId,
          'soil_moisture': soilMoisture,
          'soil_type': soilType,
          'crop_type': cropType,
        }),
      );

      if (response.statusCode == 200) {
        return WaterBalance.fromJson(json.decode(response.body));
      }
      throw AdvisorException(
        'Failed to get water balance',
        messageAr: 'فشل في الحصول على التوازن المائي',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Submit sensor reading
  /// إرسال قراءة المستشعر
  Future<WaterBalance> submitSensorReading(SensorReading reading) async {
    try {
      final response = await _client.post(
        Uri.parse(ApiConfig.sensorReading),
        headers: _headers,
        body: json.encode(reading.toJson()),
      );

      if (response.statusCode == 200) {
        return WaterBalance.fromJson(json.decode(response.body));
      }
      throw AdvisorException(
        'Failed to submit sensor reading',
        messageAr: 'فشل في إرسال قراءة المستشعر',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Get irrigation efficiency report
  /// الحصول على تقرير كفاءة الري
  Future<IrrigationEfficiencyReport> getEfficiencyReport({
    required String fieldId,
    String period = 'monthly',
  }) async {
    try {
      final uri = Uri.parse(ApiConfig.irrigationEfficiency).replace(
        queryParameters: {
          'field_id': fieldId,
          'period': period,
        },
      );

      final response = await _client.get(uri, headers: _headers);

      if (response.statusCode == 200) {
        return IrrigationEfficiencyReport.fromJson(json.decode(response.body));
      }
      throw AdvisorException(
        'Failed to get efficiency report',
        messageAr: 'فشل في الحصول على تقرير الكفاءة',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Get irrigation schedule for a field
  /// الحصول على جدول الري للحقل
  Future<IrrigationSchedule> getIrrigationSchedule(String fieldId) async {
    try {
      final uri = Uri.parse('${ApiConfig.irrigationSchedule}/$fieldId');
      final response = await _client.get(uri, headers: _headers);

      if (response.statusCode == 200) {
        return IrrigationSchedule.fromJson(json.decode(response.body));
      }
      throw AdvisorException(
        'Failed to get irrigation schedule',
        messageAr: 'فشل في الحصول على جدول الري',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is AdvisorException) rethrow;
      throw AdvisorException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Dispose the HTTP client
  void dispose() {
    _client.close();
  }
}
