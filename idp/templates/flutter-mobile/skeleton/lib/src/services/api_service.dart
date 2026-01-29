/// API Service for ${{ values.name }} module
/// خدمة API لوحدة ${{ values.name }}
///
/// Handles all HTTP communication with SAHOOL backend services.
/// يتعامل مع جميع اتصالات HTTP مع خدمات سهول الخلفية.

import 'package:dio/dio.dart';
import 'package:logger/logger.dart';

/// API Service for ${{ values.name }}
/// خدمة API لـ ${{ values.name }}
class ${{ values.name | pascal_case }}ApiService {
  late final Dio _dio;
  final Logger _logger = Logger();

  /// Base URL for the API
  /// عنوان URL الأساسي لـ API
  static const String baseUrl = 'https://api.sahool.app/v1';

  ${{ values.name | pascal_case }}ApiService({String? baseUrl}) {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl ?? ${{ values.name | pascal_case }}ApiService.baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _setupInterceptors();
  }

  void _setupInterceptors() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        _logger.d('API Request: ${options.method} ${options.path}');
        return handler.next(options);
      },
      onResponse: (response, handler) {
        _logger.d('API Response: ${response.statusCode}');
        return handler.next(response);
      },
      onError: (error, handler) {
        _logger.e('API Error: ${error.message}');
        return handler.next(error);
      },
    ));
  }

  /// Set authentication token
  /// تعيين رمز المصادقة
  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  /// GET request
  /// طلب GET
  Future<Response<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return _dio.get<T>(
      path,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// POST request
  /// طلب POST
  Future<Response<T>> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return _dio.post<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// PUT request
  /// طلب PUT
  Future<Response<T>> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return _dio.put<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }

  /// DELETE request
  /// طلب DELETE
  Future<Response<T>> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    return _dio.delete<T>(
      path,
      data: data,
      queryParameters: queryParameters,
      options: options,
    );
  }
}
