import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../utils/app_logger.dart';
import '../config/env_config.dart';

/// Security validation mode for response headers
enum SecurityHeaderMode {
  /// Reject responses missing required security headers
  strict,

  /// Log warnings but accept responses
  warn,

  /// Only log info (no warnings or errors)
  info,
}

/// Configuration for security header validation
class SecurityHeaderConfig {
  /// Validation mode
  final SecurityHeaderMode mode;

  /// Required security headers
  final Set<String> requiredHeaders;

  /// Expected values for specific headers (null means any value is acceptable)
  final Map<String, String?> expectedHeaderValues;

  /// Whether to validate Content-Length matches body
  final bool validateContentLength;

  /// Whether to check API version header
  final bool validateApiVersion;

  /// Expected API version (null means any version is acceptable)
  final String? expectedApiVersion;

  /// Whether to validate JSON structure
  final bool validateJsonStructure;

  /// Maximum allowed response size in bytes (0 = unlimited)
  final int maxResponseSize;

  const SecurityHeaderConfig({
    this.mode = SecurityHeaderMode.warn,
    this.requiredHeaders = const {
      'x-content-type-options',
      'x-frame-options',
      'strict-transport-security',
    },
    this.expectedHeaderValues = const {
      'x-content-type-options': 'nosniff',
    },
    this.validateContentLength = true,
    this.validateApiVersion = true,
    this.expectedApiVersion = null,
    this.validateJsonStructure = true,
    this.maxResponseSize = 10 * 1024 * 1024, // 10MB default
  });

  /// Create config based on environment
  factory SecurityHeaderConfig.fromEnvironment() {
    if (EnvConfig.isProduction) {
      return const SecurityHeaderConfig(
        mode: SecurityHeaderMode.strict,
        requiredHeaders: {
          'x-content-type-options',
          'x-frame-options',
          'strict-transport-security',
          'x-xss-protection',
        },
        expectedHeaderValues: {
          'x-content-type-options': 'nosniff',
        },
        validateContentLength: true,
        validateApiVersion: true,
        validateJsonStructure: true,
        maxResponseSize: 10 * 1024 * 1024,
      );
    } else if (EnvConfig.isStaging) {
      return const SecurityHeaderConfig(
        mode: SecurityHeaderMode.warn,
        requiredHeaders: {
          'x-content-type-options',
          'x-frame-options',
          'strict-transport-security',
        },
        expectedHeaderValues: {
          'x-content-type-options': 'nosniff',
        },
        validateContentLength: true,
        validateApiVersion: true,
        validateJsonStructure: true,
        maxResponseSize: 10 * 1024 * 1024,
      );
    } else {
      // Development mode - more lenient
      return const SecurityHeaderConfig(
        mode: SecurityHeaderMode.info,
        requiredHeaders: {},
        expectedHeaderValues: {},
        validateContentLength: false,
        validateApiVersion: false,
        validateJsonStructure: false,
        maxResponseSize: 50 * 1024 * 1024, // 50MB in dev
      );
    }
  }
}

/// Exception thrown when security header validation fails
class SecurityHeaderException implements Exception {
  final String code;
  final String message;
  final List<String> violations;

  SecurityHeaderException({
    required this.code,
    required this.message,
    this.violations = const [],
  });

  @override
  String toString() => 'SecurityHeaderException($code): $message\n${violations.join('\n')}';
}

/// Interceptor for validating security headers on responses
class SecurityHeadersInterceptor extends Interceptor {
  final SecurityHeaderConfig config;

  SecurityHeadersInterceptor({
    SecurityHeaderConfig? config,
  }) : config = config ?? SecurityHeaderConfig.fromEnvironment();

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    try {
      final violations = <String>[];

      // Validate security headers
      violations.addAll(_validateSecurityHeaders(response));

      // Validate Content-Type
      violations.addAll(_validateContentType(response));

      // Validate Content-Length
      if (config.validateContentLength) {
        violations.addAll(_validateContentLength(response));
      }

      // Validate API version
      if (config.validateApiVersion) {
        violations.addAll(_validateApiVersion(response));
      }

      // Validate JSON structure
      if (config.validateJsonStructure) {
        violations.addAll(_validateJsonStructure(response));
      }

      // Validate response size
      violations.addAll(_validateResponseSize(response));

      // Check for response tampering indicators
      violations.addAll(_checkTamperingIndicators(response));

      // Handle violations based on mode
      if (violations.isNotEmpty) {
        _handleViolations(response, violations, handler);
      } else {
        handler.next(response);
      }
    } catch (e) {
      AppLogger.e('Error in security header validation',
        tag: 'SecurityHeaders',
        error: e
      );
      // Don't block request on validation errors in warn/info modes
      if (config.mode == SecurityHeaderMode.strict) {
        handler.reject(
          DioException(
            requestOptions: response.requestOptions,
            error: SecurityHeaderException(
              code: 'VALIDATION_ERROR',
              message: 'Failed to validate security headers',
            ),
          ),
        );
      } else {
        handler.next(response);
      }
    }
  }

  /// Validate required security headers
  List<String> _validateSecurityHeaders(Response response) {
    final violations = <String>[];
    final headers = _normalizeHeaders(response.headers.map);

    // Check required headers
    for (final requiredHeader in config.requiredHeaders) {
      final headerKey = requiredHeader.toLowerCase();
      if (!headers.containsKey(headerKey)) {
        violations.add('Missing required security header: $requiredHeader');
      }
    }

    // Check expected header values
    for (final entry in config.expectedHeaderValues.entries) {
      final headerKey = entry.key.toLowerCase();
      final expectedValue = entry.value;

      if (headers.containsKey(headerKey)) {
        final actualValue = headers[headerKey]?.first.toLowerCase();
        if (expectedValue != null && actualValue != expectedValue.toLowerCase()) {
          violations.add(
            'Header $headerKey has unexpected value: $actualValue (expected: $expectedValue)'
          );
        }
      }
    }

    // Specific header validations

    // X-Content-Type-Options
    if (headers.containsKey('x-content-type-options')) {
      final value = headers['x-content-type-options']?.first.toLowerCase();
      if (value != 'nosniff') {
        violations.add(
          'X-Content-Type-Options should be "nosniff", got: $value'
        );
      }
    }

    // X-Frame-Options
    if (headers.containsKey('x-frame-options')) {
      final value = headers['x-frame-options']?.first.toLowerCase();
      if (!['deny', 'sameorigin'].contains(value)) {
        violations.add(
          'X-Frame-Options should be "DENY" or "SAMEORIGIN", got: $value'
        );
      }
    }

    // Strict-Transport-Security
    if (headers.containsKey('strict-transport-security')) {
      final value = headers['strict-transport-security']?.first ?? '';
      if (!value.contains('max-age=')) {
        violations.add(
          'Strict-Transport-Security must include max-age directive'
        );
      }
    }

    // X-XSS-Protection (if present)
    if (headers.containsKey('x-xss-protection')) {
      final value = headers['x-xss-protection']?.first ?? '';
      if (!value.startsWith('1')) {
        violations.add(
          'X-XSS-Protection should be enabled (1), got: $value'
        );
      }
    }

    return violations;
  }

  /// Validate Content-Type header
  List<String> _validateContentType(Response response) {
    final violations = <String>[];
    final headers = _normalizeHeaders(response.headers.map);

    if (!headers.containsKey('content-type')) {
      violations.add('Missing Content-Type header');
      return violations;
    }

    final contentType = headers['content-type']?.first.toLowerCase() ?? '';

    // Check for valid content types
    final validPrefixes = [
      'application/json',
      'application/xml',
      'text/plain',
      'text/html',
      'multipart/form-data',
      'application/octet-stream',
    ];

    final isValid = validPrefixes.any((prefix) => contentType.startsWith(prefix));
    if (!isValid) {
      violations.add('Unexpected Content-Type: $contentType');
    }

    // Warn about missing charset for text types
    if (contentType.startsWith('application/json') ||
        contentType.startsWith('text/')) {
      if (!contentType.contains('charset')) {
        violations.add('Content-Type missing charset specification: $contentType');
      }
    }

    return violations;
  }

  /// Validate Content-Length matches actual body size
  List<String> _validateContentLength(Response response) {
    final violations = <String>[];
    final headers = _normalizeHeaders(response.headers.map);

    if (!headers.containsKey('content-length')) {
      // Content-Length may not be present for chunked encoding
      return violations;
    }

    try {
      final declaredLength = int.parse(headers['content-length']?.first ?? '0');
      final actualLength = _calculateResponseSize(response);

      if (declaredLength != actualLength) {
        violations.add(
          'Content-Length mismatch: declared=$declaredLength, actual=$actualLength'
        );
      }
    } catch (e) {
      violations.add('Invalid Content-Length header: ${e.toString()}');
    }

    return violations;
  }

  /// Validate API version header
  List<String> _validateApiVersion(Response response) {
    final violations = <String>[];
    final headers = _normalizeHeaders(response.headers.map);

    // Check for API version header
    if (!headers.containsKey('x-api-version') &&
        !headers.containsKey('api-version')) {
      violations.add('Missing API version header');
      return violations;
    }

    // Get version from either header
    final version = headers['x-api-version']?.first ??
                   headers['api-version']?.first;

    if (version == null || version.isEmpty) {
      violations.add('Empty API version header');
      return violations;
    }

    // Validate against expected version if configured
    if (config.expectedApiVersion != null &&
        version != config.expectedApiVersion) {
      violations.add(
        'API version mismatch: expected=${config.expectedApiVersion}, got=$version'
      );
    }

    // Validate version format (e.g., v1, 1.0, 2023-01-01)
    final versionPattern = RegExp(r'^(v?\d+(\.\d+)*|\d{4}-\d{2}-\d{2})$');
    if (!versionPattern.hasMatch(version)) {
      violations.add('Invalid API version format: $version');
    }

    return violations;
  }

  /// Validate JSON structure for JSON responses
  List<String> _validateJsonStructure(Response response) {
    final violations = <String>[];
    final headers = _normalizeHeaders(response.headers.map);

    final contentType = headers['content-type']?.first.toLowerCase() ?? '';
    if (!contentType.startsWith('application/json')) {
      return violations; // Only validate JSON responses
    }

    try {
      // Check if data is already parsed
      if (response.data is Map || response.data is List) {
        return violations; // Already valid JSON
      }

      // Try to parse as JSON
      if (response.data is String) {
        jsonDecode(response.data as String);
      }
    } catch (e) {
      violations.add('Invalid JSON structure: ${e.toString()}');
    }

    return violations;
  }

  /// Validate response size doesn't exceed maximum
  List<String> _validateResponseSize(Response response) {
    final violations = <String>[];

    if (config.maxResponseSize <= 0) {
      return violations; // No size limit
    }

    final size = _calculateResponseSize(response);
    if (size > config.maxResponseSize) {
      violations.add(
        'Response size ($size bytes) exceeds maximum (${config.maxResponseSize} bytes)'
      );
    }

    return violations;
  }

  /// Check for potential response tampering indicators
  List<String> _checkTamperingIndicators(Response response) {
    final violations = <String>[];
    final headers = _normalizeHeaders(response.headers.map);

    // Check for suspicious header combinations

    // 1. Content-Type mismatch with actual data
    final contentType = headers['content-type']?.first.toLowerCase() ?? '';
    if (contentType.startsWith('application/json')) {
      if (response.data is! Map && response.data is! List) {
        if (response.data is String) {
          try {
            jsonDecode(response.data as String);
          } catch (e) {
            violations.add('Content-Type claims JSON but body is not valid JSON');
          }
        }
      }
    }

    // 2. Multiple Content-Type headers (possible HTTP response splitting)
    if (headers['content-type'] != null && headers['content-type']!.length > 1) {
      violations.add('Multiple Content-Type headers detected');
    }

    // 3. Multiple Content-Length headers
    if (headers['content-length'] != null && headers['content-length']!.length > 1) {
      violations.add('Multiple Content-Length headers detected');
    }

    // 4. Suspicious status code with body
    if (response.statusCode == 204 || response.statusCode == 304) {
      final size = _calculateResponseSize(response);
      if (size > 0) {
        violations.add(
          'Status ${response.statusCode} should not have response body'
        );
      }
    }

    // 5. Check for null bytes in headers (possible injection)
    for (final entry in headers.entries) {
      for (final value in entry.value) {
        if (value.contains('\u0000')) {
          violations.add('Null byte detected in header: ${entry.key}');
        }
      }
    }

    return violations;
  }

  /// Handle violations based on configured mode
  void _handleViolations(
    Response response,
    List<String> violations,
    ResponseInterceptorHandler handler,
  ) {
    final url = response.requestOptions.uri.toString();
    final logData = {
      'url': url,
      'statusCode': response.statusCode,
      'violations': violations,
    };

    switch (config.mode) {
      case SecurityHeaderMode.strict:
        AppLogger.e(
          'Security header validation failed - rejecting response',
          tag: 'SecurityHeaders',
          data: logData,
        );
        handler.reject(
          DioException(
            requestOptions: response.requestOptions,
            error: SecurityHeaderException(
              code: 'SECURITY_HEADERS_INVALID',
              message: 'Response failed security header validation',
              violations: violations,
            ),
          ),
        );
        break;

      case SecurityHeaderMode.warn:
        AppLogger.w(
          'Security header validation warnings',
          tag: 'SecurityHeaders',
          data: logData,
        );
        handler.next(response);
        break;

      case SecurityHeaderMode.info:
        if (kDebugMode) {
          AppLogger.i(
            'Security header validation info',
            tag: 'SecurityHeaders',
            data: logData,
          );
        }
        handler.next(response);
        break;
    }
  }

  /// Normalize headers to lowercase keys for case-insensitive comparison
  Map<String, List<String>> _normalizeHeaders(Map<String, List<String>> headers) {
    return Map.fromEntries(
      headers.entries.map(
        (entry) => MapEntry(entry.key.toLowerCase(), entry.value),
      ),
    );
  }

  /// Calculate response size in bytes
  int _calculateResponseSize(Response response) {
    if (response.data == null) {
      return 0;
    }

    if (response.data is String) {
      return utf8.encode(response.data as String).length;
    }

    if (response.data is List<int>) {
      return (response.data as List<int>).length;
    }

    if (response.data is Map || response.data is List) {
      // Estimate size from JSON encoding
      try {
        final encoded = jsonEncode(response.data);
        return utf8.encode(encoded).length;
      } catch (e) {
        return 0;
      }
    }

    return 0;
  }
}
