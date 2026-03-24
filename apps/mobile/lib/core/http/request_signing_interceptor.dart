import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../security/signing_key_service.dart';
import '../utils/app_logger.dart';

/// SAHOOL Request Signing Interceptor
/// معترض توقيع الطلبات
///
/// Features:
/// - HMAC-SHA256 request signing
/// - Timestamp inclusion for replay protection
/// - Nonce generation for request uniqueness
/// - Automatic signature header injection
/// - Public endpoint bypass

class RequestSigningInterceptor extends Interceptor {
  final SigningKeyService _signingKeyService;

  // Replay attack protection window (5 minutes)
  static const int maxTimestampDriftSeconds = 300;

  RequestSigningInterceptor(this._signingKeyService);

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Skip signing for public endpoints
    if (_isPublicEndpoint(options.path)) {
      AppLogger.d(
        'Skipping signature for public endpoint',
        tag: 'RequestSigning',
        data: {'path': options.path},
      );
      return handler.next(options);
    }

    try {
      // Generate signature components
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final nonce = _generateNonce();

      // Sign the request
      final signature = await _signRequest(
        method: options.method,
        path: options.path,
        timestamp: timestamp,
        nonce: nonce,
        body: options.data,
        queryParameters: options.queryParameters,
      );

      // Add signature headers
      options.headers['X-Signature'] = signature;
      options.headers['X-Timestamp'] = timestamp.toString();
      options.headers['X-Nonce'] = nonce;
      options.headers['X-Signature-Version'] = '1';

      if (kDebugMode) {
        AppLogger.d(
          'Request signed',
          tag: 'RequestSigning',
          data: {
            'method': options.method,
            'path': options.path,
            'timestamp': timestamp,
            'nonce': nonce.substring(0, 8), // Only log first 8 chars
          },
        );
      }

      handler.next(options);
    } catch (e) {
      AppLogger.e(
        'Failed to sign request',
        tag: 'RequestSigning',
        error: e,
        data: {
          'method': options.method,
          'path': options.path,
        },
      );

      // On signing error, reject the request to prevent unsigned requests
      handler.reject(
        DioException(
          requestOptions: options,
          error: 'Failed to sign request: $e',
          type: DioExceptionType.unknown,
        ),
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Signing Logic
  // ═══════════════════════════════════════════════════════════════════════════

  /// Sign a request using HMAC-SHA256
  Future<String> _signRequest({
    required String method,
    required String path,
    required int timestamp,
    required String nonce,
    dynamic body,
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      // Get signing key
      final signingKey = await _signingKeyService.getSigningKey();

      // Calculate body hash
      final bodyHash = _calculateBodyHash(body);

      // Build canonical request string
      final canonicalRequest = _buildCanonicalRequest(
        method: method,
        path: path,
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        queryParameters: queryParameters,
      );

      // Sign using HMAC-SHA256
      final signature = _calculateHmac(canonicalRequest, signingKey);

      return signature;
    } catch (e) {
      AppLogger.e('Failed to sign request', tag: 'RequestSigning', error: e);
      rethrow;
    }
  }

  /// Build canonical request string for signing
  String _buildCanonicalRequest({
    required String method,
    required String path,
    required int timestamp,
    required String nonce,
    required String bodyHash,
    Map<String, dynamic>? queryParameters,
  }) {
    // Normalize query parameters
    final sortedParams = _normalizeQueryParameters(queryParameters);

    // Build canonical request
    final parts = [
      method.toUpperCase(),
      path,
      sortedParams,
      timestamp.toString(),
      nonce,
      bodyHash,
    ];

    return parts.join('\n');
  }

  /// Calculate HMAC-SHA256 signature
  String _calculateHmac(String data, String key) {
    final keyBytes = utf8.encode(key);
    final dataBytes = utf8.encode(data);

    final hmac = Hmac(sha256, keyBytes);
    final digest = hmac.convert(dataBytes);

    return base64Url.encode(digest.bytes);
  }

  /// Calculate SHA256 hash of request body
  String _calculateBodyHash(dynamic body) {
    if (body == null) {
      return _sha256Hash('');
    }

    String bodyString;

    if (body is String) {
      bodyString = body;
    } else if (body is Map || body is List) {
      bodyString = jsonEncode(body);
    } else if (body is FormData) {
      // Hash FormData fields as a JSON map for a deterministic, content-based
      // approximation.  File bytes are not included because they may be large
      // streams; file names and field counts are included so the signature still
      // varies meaningfully between distinct multipart payloads.
      //
      // NOTE: This is not a perfect SPKI-level hash of the raw multipart body
      // because Dio does not expose the serialised bytes at this point.  It is
      // nonetheless far more collision-resistant than the previous placeholder
      // string "FormData:N:M".
      final fieldMap = <String, dynamic>{};
      for (final kv in body.fields) {
        // Use a list to preserve duplicate keys (e.g. repeated checkbox values)
        final list = (fieldMap[kv.key] as List<dynamic>?) ?? <dynamic>[];
        list.add(kv.value);
        fieldMap[kv.key] = list;
      }
      // Include file metadata so payloads with different files produce a
      // different hash even when text fields are identical.
      final filesMeta = body.files.map((kv) => {
        'field': kv.key,
        'filename': kv.value.filename ?? '',
        'contentType': kv.value.contentType?.mimeType ?? '',
        'length': kv.value.length,
      }).toList();
      bodyString = jsonEncode({'fields': fieldMap, 'files': filesMeta});
    } else {
      bodyString = body.toString();
    }

    return _sha256Hash(bodyString);
  }

  /// Calculate SHA256 hash
  String _sha256Hash(String data) {
    final bytes = utf8.encode(data);
    final digest = sha256.convert(bytes);
    return base64Url.encode(digest.bytes);
  }

  /// Normalize query parameters for consistent signing
  String _normalizeQueryParameters(Map<String, dynamic>? queryParameters) {
    if (queryParameters == null || queryParameters.isEmpty) {
      return '';
    }

    // Sort parameters by key
    final sortedKeys = queryParameters.keys.toList()..sort();

    // Build query string
    final params = sortedKeys.map((key) {
      final value = queryParameters[key];
      return '$key=${Uri.encodeComponent(value.toString())}';
    }).join('&');

    return params;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Nonce Generation
  // ═══════════════════════════════════════════════════════════════════════════

  /// Generate a unique nonce for the request
  String _generateNonce() {
    final random = Random.secure();
    final bytes = List<int>.generate(16, (_) => random.nextInt(256));
    return base64Url.encode(bytes);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Public Endpoint Detection
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if endpoint is public (doesn't require signing)
  bool _isPublicEndpoint(String path) {
    // List of public endpoints that don't require signing
    const publicPaths = [
      '/auth/login',
      '/auth/register',
      '/auth/forgot-password',
      '/auth/reset-password',
      '/auth/verify-email',
      '/auth/resend-verification',
      '/health',
      '/version',
      '/api-docs',
    ];

    return publicPaths.any((publicPath) => path.contains(publicPath));
  }
}

/// Request Signing Exception
class RequestSigningException implements Exception {
  final String message;
  final dynamic error;

  RequestSigningException(this.message, [this.error]);

  @override
  String toString() {
    if (error != null) {
      return 'RequestSigningException: $message - $error';
    }
    return 'RequestSigningException: $message';
  }
}

/// Signature Verification Result (for server-side validation)
/// This is informational and not used on the client side
class SignatureVerificationResult {
  final bool isValid;
  final String? reason;
  final bool isReplayAttack;
  final bool isTimestampValid;

  SignatureVerificationResult({
    required this.isValid,
    this.reason,
    this.isReplayAttack = false,
    this.isTimestampValid = true,
  });

  @override
  String toString() {
    return 'SignatureVerificationResult('
        'isValid: $isValid, '
        'reason: $reason, '
        'isReplayAttack: $isReplayAttack, '
        'isTimestampValid: $isTimestampValid'
        ')';
  }
}
