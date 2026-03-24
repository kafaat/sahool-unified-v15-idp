/// SAHOOL Lab Repository
/// مستودع المختبر - تتبع العينات المخبرية
///
/// يتصل بـ soil-analysis-service (port 8134)
/// و research-core (port 3015) للعينات البحثية

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/config/api_config.dart';
import '../../../core/network/api_result.dart';
import '../ui/sample_tracking_screen.dart';

// =============================================================================
// Providers
// =============================================================================

/// مزود Repository المختبر
final labRepoProvider = Provider<LabRepository>((ref) {
  return LabRepository();
});

/// مزود قائمة العينات
final samplesProvider = FutureProvider.autoDispose<List<LabSample>>((ref) async {
  final repo = ref.read(labRepoProvider);
  final result = await repo.getSamples();
  return result.when(
    success: (samples) => samples,
    failure: (message, statusCode) => throw Exception(message),
  );
});

// =============================================================================
// Repository
// =============================================================================

/// مستودع العينات المخبرية
class LabRepository {
  final Dio _dio;

  LabRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  /// جلب جميع العينات
  Future<ApiResult<List<LabSample>>> getSamples({
    SampleStatus? status,
    String? type,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (status != null) queryParams['status'] = status.name;
      if (type != null) queryParams['type'] = type;

      final response = await _dio.get(
        '/api/v1/lab/samples',
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      final List data = response.data is List
          ? response.data as List
          : (response.data as Map<String, dynamic>)['samples'] as List? ?? [];

      return Success(
        data
            .map((e) => LabSample.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل العينات'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// إنشاء عينة جديدة
  Future<ApiResult<LabSample>> createSample({
    required String type,
    required String experimentName,
    required String plotCode,
    String? notes,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/lab/samples',
        data: {
          'type': type,
          'experimentName': experimentName,
          'plotCode': plotCode,
          'notes': notes,
        },
      );
      return Success(
        LabSample.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل إنشاء العينة'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// جلب عينة بالباركود
  Future<ApiResult<LabSample>> getSampleByBarcode(String barcode) async {
    try {
      final response = await _dio.get('/api/v1/lab/samples/barcode/$barcode');
      return Success(
        LabSample.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return Failure('لم يتم العثور على عينة بهذا الباركود', statusCode: 404);
      }
      return Failure(
        _getErrorMessage(e, 'فشل البحث عن العينة'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  String _getErrorMessage(DioException e, String defaultMessage) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return 'انتهت مهلة الاتصال. تحقق من اتصالك بالإنترنت.';
    }
    if (e.type == DioExceptionType.connectionError) {
      return 'لا يمكن الاتصال بالخادم. تأكد من اتصالك بالإنترنت.';
    }
    if (e.response?.data != null && e.response?.data is Map) {
      final data = e.response?.data as Map;
      return (data['message'] ?? data['detail'] ?? defaultMessage).toString();
    }
    return defaultMessage;
  }
}
