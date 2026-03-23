/// SAHOOL Research Repository
/// مستودع التجارب البحثية
///
/// يتصل بـ research-core service (port 3015)
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/config/api_config.dart';
import '../../../core/network/api_result.dart';
import '../ui/experiments_list_screen.dart';

// =============================================================================
// Providers
// =============================================================================

/// مزود Repository البحث
final researchRepoProvider = Provider<ResearchRepository>((ref) {
  return ResearchRepository();
});

/// مزود قائمة التجارب
final experimentsProvider =
    FutureProvider.autoDispose<List<Experiment>>((ref) async {
  final repo = ref.read(researchRepoProvider);
  final result = await repo.getExperiments();
  return result.when(
    success: (experiments) => experiments,
    failure: (message, statusCode) => throw Exception(message),
  );
});

// =============================================================================
// Repository
// =============================================================================

/// مستودع التجارب البحثية
class ResearchRepository {
  final Dio _dio;

  ResearchRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  /// جلب جميع التجارب
  Future<ApiResult<List<Experiment>>> getExperiments({
    ExperimentStatus? status,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (status != null) queryParams['status'] = status.name;

      final response = await _dio.get(
        '/api/v1/research/experiments',
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      final List data = response.data is List
          ? response.data as List
          : (response.data as Map<String, dynamic>)['experiments'] as List? ??
              [];

      return Success(
        data
            .map((e) => Experiment.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل التجارب'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// جلب تجربة بالمعرف
  Future<ApiResult<Experiment>> getExperimentById(String experimentId) async {
    try {
      final response =
          await _dio.get('/api/v1/research/experiments/$experimentId');
      return Success(
        Experiment.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل التجربة'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// حفظ ملاحظة بحثية
  Future<ApiResult<bool>> saveObservation({
    required String experimentId,
    required String plotCode,
    required String category,
    required String notes,
    List<Map<String, dynamic>>? measurements,
  }) async {
    try {
      await _dio.post(
        '/api/v1/research/observations',
        data: {
          'experimentId': experimentId,
          'plotCode': plotCode,
          'category': category,
          'notes': notes,
          'measurements': measurements,
          'timestamp': DateTime.now().toIso8601String(),
        },
      );
      return const Success(true);
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل حفظ الملاحظة'),
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
