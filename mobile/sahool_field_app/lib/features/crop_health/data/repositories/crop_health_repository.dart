/// Crop Health Repository - Sahool Vision API Integration
/// مستودع صحة المحاصيل - تكامل API سهول فيجن
library;

import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';
import '../models/diagnosis_models.dart';

/// Exception for crop health API errors
/// استثناء أخطاء واجهة صحة المحاصيل
class CropHealthException implements Exception {
  final String message;
  final String messageAr;
  final int? statusCode;

  CropHealthException(this.message, {this.messageAr = '', this.statusCode});

  @override
  String toString() => 'CropHealthException: $message';
}

/// Repository for Sahool Vision AI service
/// مستودع خدمة سهول فيجن للذكاء الاصطناعي
class CropHealthRepository {
  final http.Client _client;
  final String? _authToken;

  /// Base URL for crop health service (port 8095)
  static String get _baseUrl => ApiConfig.useDirectServices
      ? 'http://${ApiConfig.useDirectServices ? "localhost" : "10.0.2.2"}:8095'
      : ApiConfig.effectiveBaseUrl;

  CropHealthRepository({
    http.Client? client,
    String? authToken,
  })  : _client = client ?? http.Client(),
        _authToken = authToken;

  Map<String, String> get _headers => {
        'Accept': 'application/json',
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Disease Diagnosis
  // تشخيص الأمراض
  // ═══════════════════════════════════════════════════════════════════════════

  /// Diagnose plant disease from image
  /// تشخيص مرض النبات من الصورة
  Future<DiagnosisResult> diagnoseFromImage(
    File imageFile, {
    String? fieldId,
    String? cropType,
    String? symptoms,
    String? governorate,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/v1/diagnose').replace(
        queryParameters: {
          if (fieldId != null) 'field_id': fieldId,
          if (cropType != null) 'crop_type': cropType,
          if (symptoms != null) 'symptoms': symptoms,
          if (governorate != null) 'governorate': governorate,
        },
      );

      final request = http.MultipartRequest('POST', uri);

      // Add headers
      request.headers.addAll(_headers);

      // Add image file
      request.files.add(
        await http.MultipartFile.fromPath('image', imageFile.path),
      );

      // Send request
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return DiagnosisResult.fromJson(data);
      }

      throw CropHealthException(
        'Failed to diagnose image',
        messageAr: 'فشل في تشخيص الصورة',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is CropHealthException) rethrow;
      throw CropHealthException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Diagnose from image bytes (for camera capture)
  /// تشخيص من بايتات الصورة (للتصوير بالكاميرا)
  Future<DiagnosisResult> diagnoseFromBytes(
    List<int> imageBytes,
    String filename, {
    String? fieldId,
    String? cropType,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/v1/diagnose').replace(
        queryParameters: {
          if (fieldId != null) 'field_id': fieldId,
          if (cropType != null) 'crop_type': cropType,
        },
      );

      final request = http.MultipartRequest('POST', uri);
      request.headers.addAll(_headers);
      request.files.add(
        http.MultipartFile.fromBytes('image', imageBytes, filename: filename),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return DiagnosisResult.fromJson(json.decode(response.body));
      }

      throw CropHealthException(
        'Failed to diagnose image',
        messageAr: 'فشل في تشخيص الصورة',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is CropHealthException) rethrow;
      throw CropHealthException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Batch diagnose multiple images
  /// تشخيص دفعة من الصور
  Future<BatchDiagnosisResult> batchDiagnose(
    List<File> images, {
    String? fieldId,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/v1/diagnose/batch').replace(
        queryParameters: {
          if (fieldId != null) 'field_id': fieldId,
        },
      );

      final request = http.MultipartRequest('POST', uri);
      request.headers.addAll(_headers);

      // Add all image files
      for (final image in images) {
        request.files.add(
          await http.MultipartFile.fromPath('images', image.path),
        );
      }

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return BatchDiagnosisResult.fromJson(json.decode(response.body));
      }

      throw CropHealthException(
        'Failed to batch diagnose',
        messageAr: 'فشل في تشخيص الدفعة',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is CropHealthException) rethrow;
      throw CropHealthException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Disease Information
  // معلومات الأمراض
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get list of supported diseases
  /// الحصول على قائمة الأمراض المدعومة
  Future<List<DiseaseInfo>> getDiseases({String? cropType}) async {
    try {
      final uri = Uri.parse('$_baseUrl/v1/diseases').replace(
        queryParameters: {
          if (cropType != null) 'crop_type': cropType,
        },
      );

      final response = await _client.get(uri, headers: _headers);

      if (response.statusCode == 200) {
        final List data = json.decode(response.body);
        return data.map((e) => DiseaseInfo.fromJson(e)).toList();
      }

      throw CropHealthException(
        'Failed to fetch diseases',
        messageAr: 'فشل في جلب الأمراض',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is CropHealthException) rethrow;
      throw CropHealthException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Get list of supported crops
  /// الحصول على قائمة المحاصيل المدعومة
  Future<List<CropOption>> getSupportedCrops() async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/v1/crops'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final List data = json.decode(response.body);
        return data.map((e) => CropOption.fromJson(e)).toList();
      }

      throw CropHealthException(
        'Failed to fetch crops',
        messageAr: 'فشل في جلب المحاصيل',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is CropHealthException) rethrow;
      throw CropHealthException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Get treatment details for a disease
  /// الحصول على تفاصيل العلاج لمرض معين
  Future<Map<String, dynamic>> getTreatmentDetails(String diseaseId) async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/v1/treatment/$diseaseId'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      }

      throw CropHealthException(
        'Failed to fetch treatment details',
        messageAr: 'فشل في جلب تفاصيل العلاج',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is CropHealthException) rethrow;
      throw CropHealthException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Expert Review
  // مراجعة الخبير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Request expert review for a diagnosis
  /// طلب مراجعة خبير للتشخيص
  Future<ExpertReviewResponse> requestExpertReview(
    String diagnosisId,
    File image, {
    String? farmerNotes,
    String urgency = 'normal',
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/v1/expert-review').replace(
        queryParameters: {
          'diagnosis_id': diagnosisId,
          if (farmerNotes != null) 'farmer_notes': farmerNotes,
          'urgency': urgency,
        },
      );

      final request = http.MultipartRequest('POST', uri);
      request.headers.addAll(_headers);
      request.files.add(
        await http.MultipartFile.fromPath('image', image.path),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return ExpertReviewResponse.fromJson(json.decode(response.body));
      }

      throw CropHealthException(
        'Failed to request expert review',
        messageAr: 'فشل في طلب مراجعة الخبير',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is CropHealthException) rethrow;
      throw CropHealthException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Check
  // فحص الصحة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if the AI service is available
  /// التحقق من توفر خدمة الذكاء الاصطناعي
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

  void dispose() {
    _client.close();
  }
}
