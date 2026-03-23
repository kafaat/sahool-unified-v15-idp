/// Scanner Repository - Disease Detection via YOLO26 Vision Service
/// مستودع الماسح - كشف الأمراض عبر خدمة الرؤية
///
/// Sends images to yolo26-vision-service (port 8150) using multipart upload.
/// POST /api/v1/detect/disease
library;

import 'dart:io';
import 'package:dio/dio.dart';
import '../../../core/config/api_config.dart';
import '../../../core/network/api_result.dart';
import '../../../core/utils/app_logger.dart';

/// Result model for a disease detection scan
/// نموذج نتيجة فحص الكشف عن الأمراض
class ScanDetectionResult {
  final String disease;
  final String diseaseEn;
  final double confidence;
  final String severity;
  final String severityEn;
  final String treatment;
  final String prevention;
  final String? imagePath;
  final DateTime scannedAt;

  const ScanDetectionResult({
    required this.disease,
    required this.diseaseEn,
    required this.confidence,
    required this.severity,
    required this.severityEn,
    required this.treatment,
    required this.prevention,
    this.imagePath,
    required this.scannedAt,
  });

  factory ScanDetectionResult.fromJson(
    Map<String, dynamic> json, {
    String? imagePath,
  }) {
    // The vision service returns a list of detections; pick the top one
    final detections = json['detections'] as List?;
    final top = detections != null && detections.isNotEmpty
        ? detections.first as Map<String, dynamic>
        : json;

    final confidenceRaw = top['confidence'] ?? top['score'] ?? 0.0;
    final confidence = (confidenceRaw as num).toDouble();

    final diseaseName = (top['class_name'] ?? top['disease'] ?? top['label'] ?? '') as String;
    final diseaseNameAr = (top['class_name_ar'] ?? top['disease_ar'] ?? diseaseName) as String;

    // Severity mapping based on confidence
    final String severity;
    final String severityEn;
    if (confidence >= 0.85) {
      severity = 'شديد';
      severityEn = 'severe';
    } else if (confidence >= 0.60) {
      severity = 'متوسط';
      severityEn = 'moderate';
    } else {
      severity = 'خفيف';
      severityEn = 'mild';
    }

    final recommendations = top['recommendations'] as Map<String, dynamic>?;
    final treatment = (recommendations?['treatment'] ??
            top['treatment'] ??
            top['treatment_ar'] ??
            'راجع مختصاً زراعياً للحصول على توصيات العلاج المناسبة')
        as String;
    final prevention = (recommendations?['prevention'] ??
            top['prevention'] ??
            top['prevention_ar'] ??
            'اتبع ممارسات الزراعة الجيدة لمنع انتشار المرض')
        as String;

    return ScanDetectionResult(
      disease: diseaseNameAr.isNotEmpty ? diseaseNameAr : diseaseName,
      diseaseEn: diseaseName,
      confidence: confidence,
      severity: severity,
      severityEn: severityEn,
      treatment: treatment,
      prevention: prevention,
      imagePath: imagePath,
      scannedAt: DateTime.now(),
    );
  }
}

/// Scanner repository - handles image upload and disease detection
/// مستودع الماسح - يدير رفع الصور وكشف الأمراض
class ScannerRepository {
  final Dio _dio;

  ScannerRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.longOperationTimeout,
              headers: {
                'Accept': 'application/json',
              },
            ));

  /// Detect disease in an image file using YOLO26 vision service
  /// POST /api/v1/detect/disease with multipart image upload
  ///
  /// Returns [ApiResult.Success] with detection results on success,
  /// or [ApiResult.Failure] on network/server error.
  /// كشف الأمراض في صورة باستخدام خدمة YOLO26
  Future<ApiResult<ScanDetectionResult>> detectDisease(
    File imageFile, {
    double confidenceThreshold = 0.25,
    double iouThreshold = 0.45,
  }) async {
    try {
      final formData = FormData.fromMap({
        'image': await MultipartFile.fromFile(
          imageFile.path,
          filename: 'scan_${DateTime.now().millisecondsSinceEpoch}.jpg',
        ),
        'confidence_threshold': confidenceThreshold,
        'iou_threshold': iouThreshold,
        'model_variant': 'm',
      });

      final response = await _dio.post(
        '/api/v1/detect/disease',
        data: formData,
        options: Options(
          contentType: 'multipart/form-data',
        ),
      );

      if (response.statusCode == 200 && response.data != null) {
        final data = response.data as Map<String, dynamic>;
        final result = ScanDetectionResult.fromJson(
          data,
          imagePath: imageFile.path,
        );
        return Success(result);
      }

      return const Failure(
        'استجابة غير متوقعة من خدمة التحليل',
        statusCode: 200,
      );
    } on DioException catch (e) {
      AppLogger.warning('Vision service error: ${e.message}');
      return Failure(
        _dioErrorMessage(e),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      AppLogger.error('Scanner repository unexpected error: $e');
      return Failure(
        'حدث خطأ غير متوقع أثناء التحليل',
        originalError: e,
      );
    }
  }

  String _dioErrorMessage(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return 'انتهت مهلة الاتصال - تحقق من اتصالك بالإنترنت';
    }
    if (e.type == DioExceptionType.connectionError) {
      return 'تعذر الاتصال بخدمة التحليل';
    }
    final status = e.response?.statusCode;
    if (status != null && status >= 500) {
      return 'خطأ في خادم خدمة التحليل ($status)';
    }
    if (status == 413) {
      return 'حجم الصورة كبير جداً - الحد الأقصى 50MB';
    }
    if (status == 400) {
      return 'صيغة الصورة غير مدعومة';
    }
    return 'فشل التحليل - يرجى المحاولة مرة أخرى';
  }
}

/// Riverpod provider for ScannerRepository
/// مزود Riverpod لمستودع الماسح
import 'package:flutter_riverpod/flutter_riverpod.dart';

final scannerRepositoryProvider = Provider.autoDispose<ScannerRepository>((ref) {
  return ScannerRepository();
});
