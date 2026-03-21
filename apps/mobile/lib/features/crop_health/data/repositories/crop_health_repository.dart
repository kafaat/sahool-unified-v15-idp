/// Crop Health Repository - Sahool Vision API Integration
/// مستودع صحة المحاصيل - تكامل API سهول فيجن
///
/// استخدام نمط ApiResult للتعامل الآمن مع الأخطاء
library;

import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';
import '../../../../core/config/env_config.dart';
import '../../../../core/network/api_result.dart';
import '../models/diagnosis_models.dart';

/// Repository for Sahool Vision AI service
/// مستودع خدمة سهول فيجن للذكاء الاصطناعي
class CropHealthRepository {
  final http.Client _client;
  final String? _authToken;

  /// Base URL for crop health service (port 8095)
  static String get _baseUrl => ApiConfig.useDirectServices
      ? EnvConfig.cropHealthUrl
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
  // Error Handling Helpers
  // مساعدات معالجة الأخطاء
  // ═══════════════════════════════════════════════════════════════════════════

  /// تحويل كود الحالة لرسالة عربية
  String _getErrorMessage(int statusCode) {
    return switch (statusCode) {
      400 => 'طلب غير صحيح، تحقق من البيانات',
      401 => 'يرجى تسجيل الدخول مجدداً',
      403 => 'غير مصرح لك بهذا الإجراء',
      404 => 'البيانات غير موجودة',
      408 => 'انتهت مهلة الطلب',
      413 => 'حجم الصورة كبير جداً، يرجى اختيار صورة أصغر',
      422 => 'صيغة الصورة غير مدعومة',
      429 => 'طلبات كثيرة، انتظر قليلاً ثم حاول مجدداً',
      >= 500 && < 600 => 'خطأ في الخادم، حاول لاحقاً',
      _ => 'خطأ في الاتصال ($statusCode)',
    };
  }

  /// تحويل استثناء لـ Failure
  Failure<T> _handleError<T>(Object e, String defaultMessage) {
    if (e is SocketException) {
      return Failure<T>('لا يوجد اتصال بالإنترنت 🔌');
    }
    if (e is http.ClientException) {
      return Failure<T>('خطأ في الاتصال بالخادم');
    }
    if (e is FormatException) {
      return Failure<T>('خطأ في تنسيق البيانات');
    }
    return Failure<T>(defaultMessage);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Disease Diagnosis
  // تشخيص الأمراض
  // ═══════════════════════════════════════════════════════════════════════════

  /// Diagnose plant disease from image
  /// تشخيص مرض النبات من الصورة
  Future<ApiResult<DiagnosisResult>> diagnoseFromImage(
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
      request.headers.addAll(_headers);
      request.files.add(
        await http.MultipartFile.fromPath('image', imageFile.path),
      );

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return Success(DiagnosisResult.fromJson(data as Map<String, dynamic>));
      }

      return Failure(
        _getErrorMessage(response.statusCode),
        statusCode: response.statusCode,
      );
    } catch (e) {
      return _handleError(e, 'فشل في تشخيص الصورة');
    }
  }

  /// Diagnose from image bytes (for camera capture)
  /// تشخيص من بايتات الصورة (للتصوير بالكاميرا)
  Future<ApiResult<DiagnosisResult>> diagnoseFromBytes(
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
        return Success(DiagnosisResult.fromJson(json.decode(response.body) as Map<String, dynamic>));
      }

      return Failure(
        _getErrorMessage(response.statusCode),
        statusCode: response.statusCode,
      );
    } catch (e) {
      return _handleError(e, 'فشل في تشخيص الصورة');
    }
  }

  /// Batch diagnose multiple images
  /// تشخيص دفعة من الصور
  Future<ApiResult<BatchDiagnosisResult>> batchDiagnose(
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

      for (final image in images) {
        request.files.add(
          await http.MultipartFile.fromPath('images', image.path),
        );
      }

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return Success(BatchDiagnosisResult.fromJson(json.decode(response.body) as Map<String, dynamic>));
      }

      return Failure(
        _getErrorMessage(response.statusCode),
        statusCode: response.statusCode,
      );
    } catch (e) {
      return _handleError(e, 'فشل في تشخيص الدفعة');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Disease Information
  // معلومات الأمراض
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get list of supported diseases
  /// الحصول على قائمة الأمراض المدعومة
  Future<ApiResult<List<DiseaseInfo>>> getDiseases({String? cropType}) async {
    try {
      final uri = Uri.parse('$_baseUrl/v1/diseases').replace(
        queryParameters: {
          if (cropType != null) 'crop_type': cropType,
        },
      );

      final response = await _client.get(uri, headers: _headers);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body) as List<dynamic>;
        return Success(data.map((e) => DiseaseInfo.fromJson(e as Map<String, dynamic>)).toList());
      }

      return Failure(
        _getErrorMessage(response.statusCode),
        statusCode: response.statusCode,
      );
    } catch (e) {
      return _handleError(e, 'فشل في جلب الأمراض');
    }
  }

  /// Get list of supported crops
  /// الحصول على قائمة المحاصيل المدعومة
  Future<ApiResult<List<CropOption>>> getSupportedCrops() async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/v1/crops'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body) as List<dynamic>;
        return Success(data.map((e) => CropOption.fromJson(e as Map<String, dynamic>)).toList());
      }

      return Failure(
        _getErrorMessage(response.statusCode),
        statusCode: response.statusCode,
      );
    } catch (e) {
      return _handleError(e, 'فشل في جلب المحاصيل');
    }
  }

  /// Get treatment details for a disease
  /// الحصول على تفاصيل العلاج لمرض معين
  Future<ApiResult<Map<String, dynamic>>> getTreatmentDetails(String diseaseId) async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/v1/treatment/$diseaseId'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return Success(json.decode(response.body) as Map<String, dynamic>);
      }

      return Failure(
        _getErrorMessage(response.statusCode),
        statusCode: response.statusCode,
      );
    } catch (e) {
      return _handleError(e, 'فشل في جلب تفاصيل العلاج');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Expert Review
  // مراجعة الخبير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Request expert review for a diagnosis
  /// طلب مراجعة خبير للتشخيص
  Future<ApiResult<ExpertReviewResponse>> requestExpertReview(
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
        return Success(ExpertReviewResponse.fromJson(json.decode(response.body) as Map<String, dynamic>));
      }

      return Failure(
        _getErrorMessage(response.statusCode),
        statusCode: response.statusCode,
      );
    } catch (e) {
      return _handleError(e, 'فشل في طلب مراجعة الخبير');
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
