/// Sahool Dio Error Handler
/// معالج أخطاء Dio لتحويلها لرسائل عربية مفهومة
library;

import 'package:dio/dio.dart';
import 'api_result.dart';

/// معالج أخطاء Dio الموحد
class DioErrorHandler {
  /// تحويل DioException لـ Failure مع رسالة عربية
  static Failure<T> handle<T>(DioException e) {
    final message = _getErrorMessage(e);
    final statusCode = e.response?.statusCode;

    return Failure<T>(
      message,
      statusCode: statusCode,
      originalError: e,
    );
  }

  /// الحصول على رسالة الخطأ بالعربية
  static String _getErrorMessage(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
        return 'انتهت مهلة الاتصال، تحقق من سرعة الإنترنت';

      case DioExceptionType.sendTimeout:
        return 'انتهت مهلة إرسال البيانات، حاول مرة أخرى';

      case DioExceptionType.receiveTimeout:
        return 'انتهت مهلة استقبال البيانات، السيرفر بطيء';

      case DioExceptionType.connectionError:
        return 'لا يوجد اتصال بالإنترنت 🔌';

      case DioExceptionType.badCertificate:
        return 'خطأ في شهادة الأمان';

      case DioExceptionType.cancel:
        return 'تم إلغاء الطلب';

      case DioExceptionType.badResponse:
        return _handleStatusCode(e.response?.statusCode);

      case DioExceptionType.unknown:
        if (e.message?.contains('SocketException') ?? false) {
          return 'لا يوجد اتصال بالإنترنت 🔌';
        }
        return 'حدث خطأ غير متوقع';
    }
  }

  /// معالجة أكواد الحالة HTTP
  static String _handleStatusCode(int? statusCode) {
    if (statusCode == null) return 'خطأ في الاتصال';

    return switch (statusCode) {
      400 => 'طلب غير صحيح، تحقق من البيانات',
      401 => 'يرجى تسجيل الدخول مجدداً',
      403 => 'غير مصرح لك بهذا الإجراء',
      404 => 'البيانات غير موجودة',
      408 => 'انتهت مهلة الطلب',
      409 => 'تعارض في البيانات',
      413 => 'حجم الملف كبير جداً، يرجى اختيار ملف أصغر',
      422 => 'بيانات غير صالحة',
      429 => 'طلبات كثيرة، انتظر قليلاً',
      >= 500 && < 600 => 'خطأ في السيرفر، حاول لاحقاً',
      _ => 'خطأ في الاتصال ($statusCode)',
    };
  }

  /// التحقق من كون الخطأ قابل لإعادة المحاولة
  static bool isRetryable(DioException e) {
    return switch (e.type) {
      DioExceptionType.connectionTimeout => true,
      DioExceptionType.sendTimeout => true,
      DioExceptionType.receiveTimeout => true,
      DioExceptionType.connectionError => true,
      DioExceptionType.badResponse => switch (e.response?.statusCode) {
        408 => true,  // Request Timeout
        429 => true,  // Too Many Requests
        503 => true,  // Service Unavailable
        504 => true,  // Gateway Timeout
        _ => false,
      },
      _ => false,
    };
  }
}

/// Extension على Dio للاستخدام السهل
extension DioExtension on Dio {
  /// طلب GET آمن يرجع ApiResult
  Future<ApiResult<T>> safeGet<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    required T Function(dynamic data) fromJson,
  }) async {
    try {
      final response = await get(path, queryParameters: queryParameters, options: options);
      return Success(fromJson(response.data));
    } on DioException catch (e) {
      return DioErrorHandler.handle(e);
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }

  /// طلب POST آمن يرجع ApiResult
  Future<ApiResult<T>> safePost<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    required T Function(dynamic data) fromJson,
  }) async {
    try {
      final response = await post(path, data: data, queryParameters: queryParameters, options: options);
      return Success(fromJson(response.data));
    } on DioException catch (e) {
      return DioErrorHandler.handle(e);
    } catch (e) {
      return Failure('حدث خطأ غير متوقع: $e');
    }
  }
}
