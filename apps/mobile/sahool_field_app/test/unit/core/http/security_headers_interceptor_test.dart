/// Security Headers Interceptor Tests
/// اختبارات معترض رؤوس الأمان
///
/// Tests the SecurityHeadersInterceptor, SecurityHeaderConfig,
/// SecurityHeaderMode, and SecurityHeaderException classes.
///
/// Covers:
/// - Config defaults and custom overrides
/// - Strict / warn / info mode behavior
/// - Required header validation
/// - Specific header value checks (XCTO, XFO, HSTS)
/// - Content-Type, Content-Length, API version validation
/// - JSON structure validation
/// - Response size limits
/// - Tampering indicators (multiple headers, null bytes, body on 204/304)
/// - SecurityHeaderException formatting
library;

import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/http/security_headers_interceptor.dart';

// ---------------------------------------------------------------------------
// Mocks
// ---------------------------------------------------------------------------

class MockResponseInterceptorHandler extends Mock
    implements ResponseInterceptorHandler {}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// Build a Dio [Response] with the given [headers] map, [statusCode], and
/// optional [data] body.  Each value in [headers] may be a single string or
/// a list of strings (to simulate duplicate headers).
Response<dynamic> _buildResponse({
  Map<String, dynamic>? headers,
  int statusCode = 200,
  dynamic data,
  String requestPath = 'https://api.sahool.app/api/v1/fields',
}) {
  final headersMap = <String, List<String>>{};

  if (headers != null) {
    for (final entry in headers.entries) {
      if (entry.value is List) {
        headersMap[entry.key] = (entry.value as List).cast<String>();
      } else {
        headersMap[entry.key] = [entry.value.toString()];
      }
    }
  }

  return Response<dynamic>(
    requestOptions: RequestOptions(path: requestPath),
    statusCode: statusCode,
    headers: Headers.fromMap(headersMap),
    data: data,
  );
}

/// A convenience set of headers that satisfy the default required-headers
/// config and include Content-Type + API version so no violations fire.
Map<String, dynamic> _validHeaders({
  String contentType = 'application/json; charset=utf-8',
  String apiVersion = 'v1',
}) {
  return {
    'x-content-type-options': 'nosniff',
    'x-frame-options': 'DENY',
    'strict-transport-security': 'max-age=31536000; includeSubDomains',
    'content-type': contentType,
    'x-api-version': apiVersion,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  setUpAll(() {
    registerFallbackValue(Response<dynamic>(
      requestOptions: RequestOptions(path: '/'),
    ));
    registerFallbackValue(DioException(
      requestOptions: RequestOptions(path: '/'),
    ));
  });

  late MockResponseInterceptorHandler handler;

  setUp(() {
    handler = MockResponseInterceptorHandler();
    // Stubs so calls never throw
    when(() => handler.next(any())).thenReturn(null);
    when(() => handler.reject(any())).thenReturn(null);
  });

  // -----------------------------------------------------------------------
  // 1. SecurityHeaderConfig defaults
  // -----------------------------------------------------------------------
  group('SecurityHeaderConfig', () {
    test('1 - has expected default values', () {
      const config = SecurityHeaderConfig();

      expect(config.mode, SecurityHeaderMode.warn);
      expect(
        config.requiredHeaders,
        containsAll([
          'x-content-type-options',
          'x-frame-options',
          'strict-transport-security',
        ]),
      );
      expect(config.expectedHeaderValues['x-content-type-options'], 'nosniff');
      expect(config.validateContentLength, isTrue);
      expect(config.validateApiVersion, isTrue);
      expect(config.expectedApiVersion, isNull);
      expect(config.validateJsonStructure, isTrue);
      expect(config.maxResponseSize, 10 * 1024 * 1024);
    });

    // ---------------------------------------------------------------------
    // 20. Custom config overrides defaults
    // ---------------------------------------------------------------------
    test('20 - custom config overrides defaults', () {
      const config = SecurityHeaderConfig(
        mode: SecurityHeaderMode.strict,
        requiredHeaders: {'x-custom-header'},
        expectedHeaderValues: {'x-custom-header': 'expected-value'},
        validateContentLength: false,
        validateApiVersion: false,
        validateJsonStructure: false,
        maxResponseSize: 999,
      );

      expect(config.mode, SecurityHeaderMode.strict);
      expect(config.requiredHeaders, {'x-custom-header'});
      expect(config.expectedHeaderValues['x-custom-header'], 'expected-value');
      expect(config.validateContentLength, isFalse);
      expect(config.validateApiVersion, isFalse);
      expect(config.validateJsonStructure, isFalse);
      expect(config.maxResponseSize, 999);
    });
  });

  // -----------------------------------------------------------------------
  // 2. SecurityHeaderMode enum values
  // -----------------------------------------------------------------------
  group('SecurityHeaderMode', () {
    test('2 - has strict, warn, and info values', () {
      expect(SecurityHeaderMode.values, hasLength(3));
      expect(
        SecurityHeaderMode.values,
        containsAll([
          SecurityHeaderMode.strict,
          SecurityHeaderMode.warn,
          SecurityHeaderMode.info,
        ]),
      );
    });
  });

  // -----------------------------------------------------------------------
  // 19. SecurityHeaderException toString
  // -----------------------------------------------------------------------
  group('SecurityHeaderException', () {
    test('19 - toString includes code, message, and violations', () {
      final exception = SecurityHeaderException(
        code: 'TEST_CODE',
        message: 'Test message',
        violations: ['violation 1', 'violation 2'],
      );

      final str = exception.toString();
      expect(str, contains('SecurityHeaderException'));
      expect(str, contains('TEST_CODE'));
      expect(str, contains('Test message'));
      expect(str, contains('violation 1'));
      expect(str, contains('violation 2'));
    });

    test('toString works with empty violations list', () {
      final exception = SecurityHeaderException(
        code: 'EMPTY',
        message: 'No violations',
      );

      final str = exception.toString();
      expect(str, contains('SecurityHeaderException'));
      expect(str, contains('EMPTY'));
      expect(str, contains('No violations'));
    });
  });

  // -----------------------------------------------------------------------
  // Interceptor behaviour
  // -----------------------------------------------------------------------
  group('SecurityHeadersInterceptor', () {
    // -------------------------------------------------------------------
    // 3. Passes valid response in strict mode
    // -------------------------------------------------------------------
    test('3 - passes valid response in strict mode', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          validateContentLength: false,
        ),
      );

      final response = _buildResponse(
        headers: _validHeaders(),
        data: {'status': 'ok'},
      );

      interceptor.onResponse(response, handler);

      verify(() => handler.next(response)).called(1);
      verifyNever(() => handler.reject(any()));
    });

    // -------------------------------------------------------------------
    // 4. Rejects response missing required headers in strict mode
    // -------------------------------------------------------------------
    test('4 - rejects response missing required headers in strict mode', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          validateContentLength: false,
          validateApiVersion: false,
        ),
      );

      // Missing all required security headers
      final response = _buildResponse(
        headers: {
          'content-type': 'application/json; charset=utf-8',
        },
        data: {'status': 'ok'},
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      verify(() => handler.reject(any())).called(1);
    });

    // -------------------------------------------------------------------
    // 5. Warns about missing headers in warn mode
    // -------------------------------------------------------------------
    test('5 - warns about missing headers in warn mode (passes through)', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.warn,
          validateContentLength: false,
          validateApiVersion: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'application/json; charset=utf-8',
        },
        data: {'status': 'ok'},
      );

      interceptor.onResponse(response, handler);

      // Warn mode passes through despite violations
      verify(() => handler.next(response)).called(1);
      verifyNever(() => handler.reject(any()));
    });

    // -------------------------------------------------------------------
    // 6. Info mode passes through
    // -------------------------------------------------------------------
    test('6 - info mode passes through with violations', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.info,
          validateContentLength: false,
          validateApiVersion: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'application/json; charset=utf-8',
        },
        data: {'status': 'ok'},
      );

      interceptor.onResponse(response, handler);

      verify(() => handler.next(response)).called(1);
      verifyNever(() => handler.reject(any()));
    });

    // -------------------------------------------------------------------
    // 7. Detects invalid X-Content-Type-Options value
    // -------------------------------------------------------------------
    test('7 - detects invalid X-Content-Type-Options value', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {'x-content-type-options'},
          validateContentLength: false,
          validateApiVersion: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'x-content-type-options': 'invalid-value',
          'content-type': 'application/json; charset=utf-8',
        },
        data: {'ok': true},
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      expect(captured, hasLength(1));

      final dioException = captured.first as DioException;
      final secException = dioException.error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('X-Content-Type-Options')),
      );
    });

    // -------------------------------------------------------------------
    // 8. Detects invalid X-Frame-Options value
    // -------------------------------------------------------------------
    test('8 - detects invalid X-Frame-Options value', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {'x-frame-options'},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'x-frame-options': 'ALLOW-FROM http://evil.com',
          'content-type': 'application/json; charset=utf-8',
        },
        data: {'ok': true},
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('X-Frame-Options')),
      );
    });

    // -------------------------------------------------------------------
    // 9. Detects missing max-age in HSTS
    // -------------------------------------------------------------------
    test('9 - detects missing max-age in Strict-Transport-Security', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {'strict-transport-security'},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'strict-transport-security': 'includeSubDomains',
          'content-type': 'application/json; charset=utf-8',
        },
        data: {'ok': true},
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('max-age')),
      );
    });

    // -------------------------------------------------------------------
    // 10. Validates Content-Type header
    // -------------------------------------------------------------------
    test('10 - detects unexpected Content-Type', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'application/x-malicious',
        },
        data: 'hello',
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('Content-Type')),
      );
    });

    // -------------------------------------------------------------------
    // 11. Detects Content-Length mismatch
    // -------------------------------------------------------------------
    test('11 - detects Content-Length mismatch', () {
      const body = '{"status":"ok"}';
      final wrongLength = utf8.encode(body).length + 100;

      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: true,
          validateApiVersion: false,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
          'content-length': wrongLength.toString(),
        },
        data: body,
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('Content-Length mismatch')),
      );
    });

    // -------------------------------------------------------------------
    // 12. Detects missing API version header
    // -------------------------------------------------------------------
    test('12 - detects missing API version header', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: true,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
        },
        data: 'hello',
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('API version')),
      );
    });

    // -------------------------------------------------------------------
    // 13. Detects invalid API version format
    // -------------------------------------------------------------------
    test('13 - detects invalid API version format', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: true,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
          'x-api-version': 'not-a-version!!',
        },
        data: 'hello',
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('Invalid API version format')),
      );
    });

    // -------------------------------------------------------------------
    // 14. Validates JSON structure
    // -------------------------------------------------------------------
    test('14 - detects invalid JSON structure', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: true,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'application/json; charset=utf-8',
        },
        data: '{not valid json!!!',
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      // Should have violations about invalid JSON and possibly tampering
      expect(
        secException.violations,
        anyElement(contains('JSON')),
      );
    });

    // -------------------------------------------------------------------
    // 15. Detects oversized response
    // -------------------------------------------------------------------
    test('15 - detects oversized response', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
          maxResponseSize: 10, // 10 bytes
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
        },
        data: 'This string is definitely longer than 10 bytes',
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('exceeds maximum')),
      );
    });

    // -------------------------------------------------------------------
    // 16. Detects multiple Content-Type headers (tampering)
    // -------------------------------------------------------------------
    test('16 - detects multiple Content-Type headers', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': [
            'application/json; charset=utf-8',
            'text/html',
          ],
        },
        data: {'ok': true},
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('Multiple Content-Type')),
      );
    });

    // -------------------------------------------------------------------
    // 17. Detects null bytes in headers
    // -------------------------------------------------------------------
    test('17 - detects null bytes in headers', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
          'x-custom': 'value\u0000injected',
        },
        data: 'test',
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('Null byte')),
      );
    });

    // -------------------------------------------------------------------
    // 18. Detects body on 204 status
    // -------------------------------------------------------------------
    test('18 - detects body on 204 No Content status', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
        },
        statusCode: 204,
        data: 'should not have a body',
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('should not have response body')),
      );
    });

    // -------------------------------------------------------------------
    // Additional tests for thoroughness
    // -------------------------------------------------------------------

    test('detects body on 304 Not Modified status', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
        },
        statusCode: 304,
        data: 'should not have a body',
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('304')),
      );
    });

    test('detects multiple Content-Length headers', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
          'content-length': ['100', '200'],
        },
        data: 'test',
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('Multiple Content-Length')),
      );
    });

    test('accepts valid X-Frame-Options SAMEORIGIN', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {'x-frame-options'},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'x-frame-options': 'SAMEORIGIN',
          'content-type': 'text/plain; charset=utf-8',
        },
        data: 'ok',
      );

      interceptor.onResponse(response, handler);

      verify(() => handler.next(response)).called(1);
      verifyNever(() => handler.reject(any()));
    });

    test('accepts valid date-based API version format', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: true,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
          'x-api-version': '2025-01-15',
        },
        data: 'ok',
      );

      interceptor.onResponse(response, handler);

      verify(() => handler.next(response)).called(1);
      verifyNever(() => handler.reject(any()));
    });

    test('accepts already-parsed JSON (Map) without violation', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: true,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'application/json; charset=utf-8',
        },
        data: {'status': 'ok', 'count': 42},
      );

      interceptor.onResponse(response, handler);

      verify(() => handler.next(response)).called(1);
      verifyNever(() => handler.reject(any()));
    });

    test('skips JSON validation for non-JSON content type', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: true,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
        },
        data: 'This is not JSON and that is fine',
      );

      interceptor.onResponse(response, handler);

      verify(() => handler.next(response)).called(1);
      verifyNever(() => handler.reject(any()));
    });

    test('unlimited response size when maxResponseSize is 0', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
          maxResponseSize: 0,
        ),
      );

      final largeData = 'x' * 100000;
      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
        },
        data: largeData,
      );

      interceptor.onResponse(response, handler);

      verify(() => handler.next(response)).called(1);
      verifyNever(() => handler.reject(any()));
    });

    test('null data results in zero calculated response size', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
          maxResponseSize: 10,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
        },
        data: null,
      );

      interceptor.onResponse(response, handler);

      verify(() => handler.next(response)).called(1);
      verifyNever(() => handler.reject(any()));
    });

    test('Content-Length validation is skipped when not enabled', () {
      const body = '{"status":"ok"}';
      final wrongLength = utf8.encode(body).length + 999;

      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
        ),
      );

      final response = _buildResponse(
        headers: {
          'content-type': 'text/plain; charset=utf-8',
          'content-length': wrongLength.toString(),
        },
        data: body,
      );

      interceptor.onResponse(response, handler);

      // Should pass because validateContentLength is false
      verify(() => handler.next(response)).called(1);
      verifyNever(() => handler.reject(any()));
    });

    test('missing Content-Type header is flagged', () {
      final interceptor = SecurityHeadersInterceptor(
        config: const SecurityHeaderConfig(
          mode: SecurityHeaderMode.strict,
          requiredHeaders: {},
          expectedHeaderValues: {},
          validateContentLength: false,
          validateApiVersion: false,
          validateJsonStructure: false,
        ),
      );

      // No content-type header at all
      final response = _buildResponse(
        headers: {},
        data: 'test',
      );

      interceptor.onResponse(response, handler);

      verifyNever(() => handler.next(any()));
      final captured = verify(() => handler.reject(captureAny())).captured;
      final secException =
          (captured.first as DioException).error as SecurityHeaderException;
      expect(
        secException.violations,
        anyElement(contains('Content-Type')),
      );
    });
  });
}
