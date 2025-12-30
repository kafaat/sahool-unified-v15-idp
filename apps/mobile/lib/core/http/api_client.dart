import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:flutter/foundation.dart';
import 'package:crypto/crypto.dart';
import '../config/config.dart';
import '../utils/app_logger.dart';

/// SAHOOL API Client with offline handling and SSL Certificate Pinning
class ApiClient {
  late final Dio _dio;
  String? _authToken;
  String _tenantId = AppConfig.defaultTenantId;

  /// SSL Certificate Pinning - Enable/Disable via environment flag
  /// Set to false in development/testing, true in production
  static const bool _enableSslPinning = bool.fromEnvironment(
    'ENABLE_SSL_PINNING',
    defaultValue: !kDebugMode, // Enabled by default in release mode
  );

  /// Production API Certificate SHA-256 Fingerprints (Base64-encoded)
  ///
  /// Certificate Pinning Strategy:
  /// - Always maintain at least 2-3 backup hashes to prevent service disruption
  /// - Update backup hashes 30 days before certificate expiration
  /// - After deploying new certificate, keep old hash for 90 days for gradual rollout
  /// - Test pinning in staging environment before production deployment
  ///
  /// To generate certificate hash:
  /// 1. For certificate hash:
  ///    openssl s_client -connect api.sahool.com:443 -servername api.sahool.com < /dev/null | \
  ///    openssl x509 -outform DER | openssl dgst -sha256 -binary | openssl enc -base64
  ///
  /// 2. For public key hash (recommended, more resilient to certificate renewal):
  ///    echo | openssl s_client -connect api.sahool.com:443 2>/dev/null | \
  ///    openssl x509 -pubkey -noout | openssl pkey -pubin -outform der | \
  ///    openssl dgst -sha256 -binary | base64
  ///
  /// TODO: Replace these placeholder hashes with actual production certificate hashes
  static const List<String> _pinnedCertificates = [
    // Primary production certificate (expires: TBD)
    'sha256/X3pGTSOuJeEVw989IJ/cEtXUEmy52zs1TZQrU06KUKg=',

    // Backup certificate for rotation (pre-deployed backup, expires: TBD)
    'sha256/Y4RhSGu8jF3Xx891KL/dFuYVFnz63At2UaRsV17LVLh=',

    // Secondary backup certificate (intermediate CA or alternative cert)
    'sha256/Z5SiTHv9kG4Yy902LM/eFvZWGo074Bu3VbStW28MWMi=',

    // Tertiary backup (for emergency certificate replacement)
    'sha256/W6TjUIw0lH5Zz013MN/fGwaxHp185Cv4WcTuX39NXNj=',
  ];

  ApiClient({String? baseUrl}) {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl ?? AppConfig.apiBaseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    // Configure SSL Certificate Pinning
    _configureCertificatePinning();

    // Add interceptors
    _dio.interceptors.add(_AuthInterceptor(this));
    _dio.interceptors.add(_LoggingInterceptor());
  }

  /// Configure SSL Certificate Pinning to prevent MITM attacks
  void _configureCertificatePinning() {
    if (!_enableSslPinning) {
      if (kDebugMode) {
        AppLogger.w(
          'SSL Certificate Pinning is DISABLED (Development Mode)',
          tag: 'SECURITY',
        );
      }
      return;
    }

    if (kDebugMode) {
      AppLogger.i('SSL Certificate Pinning ENABLED', tag: 'SECURITY');
    }

    (_dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
      final client = HttpClient();

      client.badCertificateCallback = (X509Certificate cert, String host, int port) {
        // Validate the certificate against pinned hashes
        final isValid = _isValidCertificate(cert, host);

        if (!isValid && kDebugMode) {
          AppLogger.e(
            'Certificate validation failed',
            tag: 'SECURITY',
            data: {'host': host, 'port': port},
          );
        }

        return isValid;
      };

      return client;
    };
  }

  /// Validate certificate against pinned hashes
  /// Returns true if the certificate's public key hash matches any pinned certificate
  bool _isValidCertificate(X509Certificate cert, String host) {
    try {
      // Get the certificate's DER-encoded bytes
      final certBytes = cert.der;

      // Calculate SHA-256 hash of the certificate
      final certHash = sha256.convert(certBytes);
      final certHashBase64 = base64.encode(certHash.bytes);

      // Also calculate hash of the public key (more robust for certificate rotation)
      // Note: X509Certificate in Dart doesn't directly expose public key,
      // so we use the full certificate hash. In production, consider using
      // a package like 'x509' for proper public key pinning.

      // Check if the hash matches any of our pinned certificates
      final isMatch = _pinnedCertificates.contains(certHashBase64);

      if (kDebugMode && !isMatch) {
        AppLogger.w(
          'Certificate hash mismatch',
          tag: 'SECURITY',
          data: {
            'host': host,
            'actualHash': certHashBase64,
            'expectedHashes': _pinnedCertificates,
          },
        );
      }

      return isMatch;
    } catch (e) {
      if (kDebugMode) {
        AppLogger.e(
          'Error validating certificate',
          tag: 'SECURITY',
          error: e,
        );
      }
      // Fail closed - reject certificate if validation fails
      return false;
    }
  }

  void setAuthToken(String token) {
    _authToken = token;
  }

  void setTenantId(String tenantId) {
    _tenantId = tenantId;
  }

  String? get authToken => _authToken;
  String get tenantId => _tenantId;

  /// GET request
  Future<dynamic> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await _dio.get(
        path,
        queryParameters: queryParameters,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// POST request
  Future<dynamic> post(
    String path,
    dynamic data, {
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
  }) async {
    try {
      final response = await _dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: headers != null ? Options(headers: headers) : null,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// PUT request
  Future<dynamic> put(
    String path,
    dynamic data, {
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
  }) async {
    try {
      final response = await _dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: headers != null ? Options(headers: headers) : null,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// DELETE request
  Future<dynamic> delete(
    String path, {
    Map<String, dynamic>? queryParameters,
    Map<String, String>? headers,
  }) async {
    try {
      final response = await _dio.delete(
        path,
        queryParameters: queryParameters,
        options: headers != null ? Options(headers: headers) : null,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Upload file
  Future<dynamic> uploadFile(
    String path,
    String filePath, {
    String fieldName = 'file',
    Map<String, dynamic>? extraData,
  }) async {
    try {
      final formData = FormData.fromMap({
        fieldName: await MultipartFile.fromFile(filePath),
        ...?extraData,
      });

      final response = await _dio.post(path, data: formData);
      return response.data;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  ApiException _handleError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException(
          code: 'TIMEOUT',
          message: 'انتهت مهلة الاتصال',
          isNetworkError: true,
        );

      case DioExceptionType.connectionError:
        return ApiException(
          code: 'NO_CONNECTION',
          message: 'لا يوجد اتصال بالإنترنت',
          isNetworkError: true,
        );

      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode ?? 0;
        final data = e.response?.data;
        String message = 'حدث خطأ غير متوقع';

        if (data is Map) {
          message = data['message'] ?? data['error'] ?? message;
        }

        return ApiException(
          code: 'HTTP_$statusCode',
          message: message,
          statusCode: statusCode,
        );

      default:
        return ApiException(
          code: 'UNKNOWN',
          message: 'حدث خطأ غير متوقع',
        );
    }
  }
}

/// Auth Interceptor
class _AuthInterceptor extends Interceptor {
  final ApiClient _client;

  _AuthInterceptor(this._client);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // Add auth token
    if (_client.authToken != null) {
      options.headers['Authorization'] = 'Bearer ${_client.authToken}';
    }

    // Add tenant ID
    options.headers['X-Tenant-Id'] = _client.tenantId;

    handler.next(options);
  }
}

/// Logging Interceptor
/// Only logs in debug mode to prevent sensitive data exposure in production
class _LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (kDebugMode) {
      AppLogger.d(
        'HTTP Request: ${options.method} ${options.path}',
        tag: 'HTTP',
      );
      // Note: Authorization headers and request body are intentionally not logged
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (kDebugMode) {
      AppLogger.d(
        'HTTP Response: ${response.statusCode} ${response.requestOptions.path}',
        tag: 'HTTP',
      );
      // Note: Response body is intentionally not logged to prevent data leakage
    }
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (kDebugMode) {
      AppLogger.e(
        'HTTP Error: ${err.requestOptions.path}',
        tag: 'HTTP',
        error: err.type,
      );
    }
    handler.next(err);
  }
}

/// API Exception
class ApiException implements Exception {
  final String code;
  final String message;
  final int? statusCode;
  final bool isNetworkError;

  ApiException({
    required this.code,
    required this.message,
    this.statusCode,
    this.isNetworkError = false,
  });

  @override
  String toString() => 'ApiException($code): $message';
}
