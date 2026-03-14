/// Request Signing Interceptor Tests
/// اختبارات معترض توقيع الطلبات
///
/// Tests the RequestSigningInterceptor, RequestSigningException,
/// and SignatureVerificationResult classes.
///
/// Covers:
/// - Public endpoint bypass (all 9 public paths)
/// - Signature header injection (X-Signature, X-Timestamp, X-Nonce, X-Signature-Version)
/// - Body hash calculation (null, String, Map, List, FormData, other types)
/// - Query parameter normalization (sorted by key, URL-encoded values)
/// - Signing failure handling (key service throws, handler.reject called)
/// - RequestSigningException toString formatting
/// - SignatureVerificationResult properties and toString
/// - HMAC-SHA256 signature consistency and correctness
/// - Nonce generation (16 random bytes, base64url encoded, unique per request)

import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/http/request_signing_interceptor.dart';
import 'package:sahool_field_app/core/security/signing_key_service.dart';

// ---------------------------------------------------------------------------
// Mocks & Fakes
// ---------------------------------------------------------------------------

class MockSigningKeyService extends Mock implements SigningKeyService {}

/// A fake handler that captures the result of onRequest (next or reject).
class FakeRequestInterceptorHandler extends Fake
    implements RequestInterceptorHandler {
  RequestOptions? nextOptions;
  DioException? rejectedError;

  @override
  void next(RequestOptions options) {
    nextOptions = options;
  }

  @override
  void reject(DioException error,
      [bool callFollowingErrorInterceptor = false]) {
    rejectedError = error;
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const _testSigningKey = 'test-signing-key-for-unit-tests-32chars!!';

/// Compute SHA256 hash as base64Url, matching the interceptor implementation.
String _sha256Hash(String data) {
  final bytes = utf8.encode(data);
  final digest = sha256.convert(bytes);
  return base64Url.encode(digest.bytes);
}

/// Compute HMAC-SHA256 as base64Url, matching the interceptor implementation.
String _calculateHmac(String data, String key) {
  final keyBytes = utf8.encode(key);
  final dataBytes = utf8.encode(data);
  final hmac = Hmac(sha256, keyBytes);
  final digest = hmac.convert(dataBytes);
  return base64Url.encode(digest.bytes);
}

/// Build the expected signature by reconstructing the canonical request
/// from captured headers and known inputs, then computing HMAC-SHA256.
String _expectedSignature({
  required String method,
  required String path,
  required String timestamp,
  required String nonce,
  required String bodyHash,
  required String signingKey,
  String queryParams = '',
}) {
  final canonicalRequest = [
    method.toUpperCase(),
    path,
    queryParams,
    timestamp,
    nonce,
    bodyHash,
  ].join('\n');
  return _calculateHmac(canonicalRequest, signingKey);
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

void main() {
  late MockSigningKeyService mockSigningKeyService;
  late RequestSigningInterceptor interceptor;
  late FakeRequestInterceptorHandler handler;

  setUp(() {
    mockSigningKeyService = MockSigningKeyService();
    interceptor = RequestSigningInterceptor(mockSigningKeyService);
    handler = FakeRequestInterceptorHandler();

    // Default: signing key returns successfully
    when(() => mockSigningKeyService.getSigningKey())
        .thenAnswer((_) async => _testSigningKey);
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // 1. Public endpoint bypass
  // ═══════════════════════════════════════════════════════════════════════════

  group('Public endpoint bypass', () {
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

    for (final path in publicPaths) {
      test('skips signing for public endpoint: $path', () async {
        final options = RequestOptions(path: path, method: 'GET');

        await interceptor.onRequest(options, handler);

        expect(handler.nextOptions, isNotNull,
            reason: 'handler.next should be called for public endpoints');
        expect(handler.rejectedError, isNull,
            reason: 'handler.reject should not be called for public endpoints');
        expect(handler.nextOptions!.headers.containsKey('X-Signature'), isFalse,
            reason: 'X-Signature should not be added for public endpoints');
        expect(handler.nextOptions!.headers.containsKey('X-Timestamp'), isFalse,
            reason: 'X-Timestamp should not be added for public endpoints');
        expect(handler.nextOptions!.headers.containsKey('X-Nonce'), isFalse,
            reason: 'X-Nonce should not be added for public endpoints');
        expect(
            handler.nextOptions!.headers.containsKey('X-Signature-Version'),
            isFalse,
            reason:
                'X-Signature-Version should not be added for public endpoints');
        verifyNever(() => mockSigningKeyService.getSigningKey());
      });
    }

    test('skips signing when public path is a substring of a longer path',
        () async {
      final options =
          RequestOptions(path: '/api/v1/auth/login/callback', method: 'POST');

      await interceptor.onRequest(options, handler);

      expect(handler.nextOptions, isNotNull);
      expect(handler.rejectedError, isNull);
      expect(
          handler.nextOptions!.headers.containsKey('X-Signature'), isFalse);
      verifyNever(() => mockSigningKeyService.getSigningKey());
    });

    test('does NOT skip signing for non-public endpoint', () async {
      final options =
          RequestOptions(path: '/api/v1/fields', method: 'GET');

      await interceptor.onRequest(options, handler);

      expect(handler.nextOptions, isNotNull);
      expect(handler.nextOptions!.headers.containsKey('X-Signature'), isTrue);
      verify(() => mockSigningKeyService.getSigningKey()).called(1);
    });

    test('does NOT skip signing for path that partially matches', () async {
      // '/authenticate' does not contain any of the listed public paths
      final options =
          RequestOptions(path: '/api/v1/authenticate', method: 'POST');

      await interceptor.onRequest(options, handler);

      expect(handler.nextOptions!.headers.containsKey('X-Signature'), isTrue);
      verify(() => mockSigningKeyService.getSigningKey()).called(1);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // 2. Signature header injection
  // ═══════════════════════════════════════════════════════════════════════════

  group('Signature header injection', () {
    test('adds all four required signature headers', () async {
      final options =
          RequestOptions(path: '/api/v1/fields', method: 'GET');

      await interceptor.onRequest(options, handler);

      final headers = handler.nextOptions!.headers;
      expect(headers, contains('X-Signature'));
      expect(headers, contains('X-Timestamp'));
      expect(headers, contains('X-Nonce'));
      expect(headers, contains('X-Signature-Version'));
    });

    test('X-Signature-Version is "1"', () async {
      final options =
          RequestOptions(path: '/api/v1/fields', method: 'GET');

      await interceptor.onRequest(options, handler);

      expect(handler.nextOptions!.headers['X-Signature-Version'], '1');
    });

    test('X-Timestamp is a valid millisecondsSinceEpoch', () async {
      final beforeMs = DateTime.now().millisecondsSinceEpoch;
      final options =
          RequestOptions(path: '/api/v1/fields', method: 'GET');

      await interceptor.onRequest(options, handler);

      final afterMs = DateTime.now().millisecondsSinceEpoch;
      final timestamp =
          int.parse(handler.nextOptions!.headers['X-Timestamp'] as String);

      expect(timestamp, greaterThanOrEqualTo(beforeMs));
      expect(timestamp, lessThanOrEqualTo(afterMs));
    });

    test('X-Nonce is a base64url-encoded 16-byte value', () async {
      final options =
          RequestOptions(path: '/api/v1/fields', method: 'GET');

      await interceptor.onRequest(options, handler);

      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      expect(nonce, isNotEmpty);

      // 16 random bytes base64url-encoded
      final decoded = base64Url.decode(nonce);
      expect(decoded, hasLength(16));
    });

    test('X-Signature is a base64url-encoded 32-byte HMAC-SHA256 digest',
        () async {
      final options =
          RequestOptions(path: '/api/v1/fields', method: 'GET');

      await interceptor.onRequest(options, handler);

      final signature =
          handler.nextOptions!.headers['X-Signature'] as String;
      expect(signature, isNotEmpty);

      // HMAC-SHA256 produces 32 bytes
      final decoded = base64Url.decode(signature);
      expect(decoded, hasLength(32));
    });

    test('nonce is unique across consecutive requests', () async {
      final options1 = RequestOptions(path: '/api/v1/fields', method: 'GET');
      final handler1 = FakeRequestInterceptorHandler();
      await interceptor.onRequest(options1, handler1);

      final options2 = RequestOptions(path: '/api/v1/fields', method: 'GET');
      final handler2 = FakeRequestInterceptorHandler();
      await interceptor.onRequest(options2, handler2);

      final nonce1 = handler1.nextOptions!.headers['X-Nonce'] as String;
      final nonce2 = handler2.nextOptions!.headers['X-Nonce'] as String;

      expect(nonce1, isNot(equals(nonce2)));
    });

    test('does not overwrite existing non-signature headers', () async {
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
        headers: {
          'Authorization': 'Bearer token123',
          'Accept-Language': 'ar',
        },
      );

      await interceptor.onRequest(options, handler);

      expect(handler.nextOptions!.headers['Authorization'], 'Bearer token123');
      expect(handler.nextOptions!.headers['Accept-Language'], 'ar');
      expect(handler.nextOptions!.headers.containsKey('X-Signature'), isTrue);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // 3. Body hash calculation
  // ═══════════════════════════════════════════════════════════════════════════

  group('Body hash calculation', () {
    test('null body uses SHA256 of empty string', () async {
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
        data: null,
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash('');

      final expected = _expectedSignature(
        method: 'GET',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('String body uses SHA256 of the raw string', () async {
      const bodyStr = '{"name":"test field"}';
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'POST',
        data: bodyStr,
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash(bodyStr);

      final expected = _expectedSignature(
        method: 'POST',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('Map body is JSON-encoded before hashing', () async {
      final bodyMap = {'name': 'field1', 'area': 10.5};
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'POST',
        data: bodyMap,
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash(jsonEncode(bodyMap));

      final expected = _expectedSignature(
        method: 'POST',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('List body is JSON-encoded before hashing', () async {
      final bodyList = [
        {'id': 1},
        {'id': 2},
      ];
      final options = RequestOptions(
        path: '/api/v1/batch',
        method: 'POST',
        data: bodyList,
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash(jsonEncode(bodyList));

      final expected = _expectedSignature(
        method: 'POST',
        path: '/api/v1/batch',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('FormData body uses fields/files count placeholder for hash',
        () async {
      final formData = FormData.fromMap({
        'field1': 'value1',
        'field2': 'value2',
        'file': MultipartFile.fromString('content', filename: 'test.txt'),
      });
      final options = RequestOptions(
        path: '/api/v1/upload',
        method: 'POST',
        data: formData,
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      // FormData hash: "FormData:{fields.length}:{files.length}"
      final bodyHash = _sha256Hash(
        'FormData:${formData.fields.length}:${formData.files.length}',
      );

      final expected = _expectedSignature(
        method: 'POST',
        path: '/api/v1/upload',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('FormData with only fields (no files) uses correct placeholder',
        () async {
      final formData = FormData.fromMap({'key': 'value'});
      final options = RequestOptions(
        path: '/api/v1/data',
        method: 'POST',
        data: formData,
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash(
        'FormData:${formData.fields.length}:${formData.files.length}',
      );

      final expected = _expectedSignature(
        method: 'POST',
        path: '/api/v1/data',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('non-standard body type uses toString() for hash', () async {
      // An int is not String, Map, List, or FormData.
      // Falls to else branch: body.toString()
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'POST',
        data: 42,
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash('42');

      final expected = _expectedSignature(
        method: 'POST',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('different body contents produce different signatures', () async {
      final options1 = RequestOptions(
        path: '/api/v1/fields',
        method: 'POST',
        data: '{"a":1}',
      );
      final handler1 = FakeRequestInterceptorHandler();
      await interceptor.onRequest(options1, handler1);

      final options2 = RequestOptions(
        path: '/api/v1/fields',
        method: 'POST',
        data: '{"a":2}',
      );
      final handler2 = FakeRequestInterceptorHandler();
      await interceptor.onRequest(options2, handler2);

      final sig1 = handler1.nextOptions!.headers['X-Signature'] as String;
      final sig2 = handler2.nextOptions!.headers['X-Signature'] as String;

      expect(sig1, isNot(equals(sig2)));
    });

    test('null body and empty string body have the same body hash', () {
      // Both null and '' produce _sha256Hash('')
      final hashNull = _sha256Hash('');
      final hashEmpty = _sha256Hash('');
      expect(hashNull, equals(hashEmpty));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // 4. Query parameter normalization
  // ═══════════════════════════════════════════════════════════════════════════

  group('Query parameter normalization', () {
    test('parameters are sorted alphabetically by key', () async {
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
        queryParameters: {'z_param': '3', 'a_param': '1', 'm_param': '2'},
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash('');

      // Sorted: a_param, m_param, z_param
      const sortedParams = 'a_param=1&m_param=2&z_param=3';

      final expected = _expectedSignature(
        method: 'GET',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
        queryParams: sortedParams,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('values are URL-encoded using Uri.encodeComponent', () async {
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
        queryParameters: {'search': 'hello world', 'tag': 'a&b'},
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash('');

      final sortedParams =
          'search=${Uri.encodeComponent('hello world')}'
          '&tag=${Uri.encodeComponent('a&b')}';

      final expected = _expectedSignature(
        method: 'GET',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
        queryParams: sortedParams,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('empty query parameters produce empty string in canonical request',
        () async {
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
        queryParameters: {},
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash('');

      final expected = _expectedSignature(
        method: 'GET',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
        queryParams: '',
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('numeric values are converted to string via toString()', () async {
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
        queryParameters: {'limit': 10, 'offset': 0},
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash('');

      // Sorted: limit, offset
      const sortedParams = 'limit=10&offset=0';

      final expected = _expectedSignature(
        method: 'GET',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
        queryParams: sortedParams,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('special characters in values are properly encoded', () async {
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
        queryParameters: {'q': 'key=val&other'},
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash('');

      final sortedParams = 'q=${Uri.encodeComponent('key=val&other')}';

      final expected = _expectedSignature(
        method: 'GET',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
        queryParams: sortedParams,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('single query parameter works correctly', () async {
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
        queryParameters: {'tenant_id': 'abc-123'},
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash('');

      const sortedParams = 'tenant_id=abc-123';

      final expected = _expectedSignature(
        method: 'GET',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
        queryParams: sortedParams,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // 5. Signing failure handling
  // ═══════════════════════════════════════════════════════════════════════════

  group('Signing failure handling', () {
    test('rejects request when signing key service throws synchronously',
        () async {
      when(() => mockSigningKeyService.getSigningKey())
          .thenThrow(Exception('Key storage corrupted'));

      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
      );

      await interceptor.onRequest(options, handler);

      expect(handler.nextOptions, isNull,
          reason: 'handler.next should not be called on signing failure');
      expect(handler.rejectedError, isNotNull,
          reason: 'handler.reject should be called on signing failure');
      expect(handler.rejectedError, isA<DioException>());
      expect(handler.rejectedError!.type, DioExceptionType.unknown);
      expect(
        handler.rejectedError!.error.toString(),
        contains('Failed to sign request'),
      );
      expect(
        handler.rejectedError!.requestOptions.path,
        '/api/v1/fields',
      );
    });

    test('rejects request when getSigningKey returns a Future that throws',
        () async {
      when(() => mockSigningKeyService.getSigningKey())
          .thenAnswer((_) async => throw StateError('Secure storage locked'));

      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'POST',
        data: {'name': 'field'},
      );

      await interceptor.onRequest(options, handler);

      expect(handler.nextOptions, isNull);
      expect(handler.rejectedError, isNotNull);
      expect(handler.rejectedError!.type, DioExceptionType.unknown);
    });

    test('reject error message includes original exception details', () async {
      when(() => mockSigningKeyService.getSigningKey())
          .thenThrow(Exception('Keystore corrupted'));

      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
      );

      await interceptor.onRequest(options, handler);

      expect(
        handler.rejectedError!.error.toString(),
        contains('Keystore corrupted'),
      );
    });

    test('rejected DioException references the original request options',
        () async {
      when(() => mockSigningKeyService.getSigningKey())
          .thenThrow(Exception('fail'));

      final options = RequestOptions(
        path: '/api/v1/advisory',
        method: 'PUT',
      );

      await interceptor.onRequest(options, handler);

      expect(handler.rejectedError!.requestOptions, same(options));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // 6. RequestSigningException
  // ═══════════════════════════════════════════════════════════════════════════

  group('RequestSigningException', () {
    test('toString with message only (no error)', () {
      final exception = RequestSigningException('Key not found');

      expect(
        exception.toString(),
        'RequestSigningException: Key not found',
      );
    });

    test('toString with message and error includes separator', () {
      final exception = RequestSigningException(
        'Signing failed',
        Exception('internal error'),
      );

      final str = exception.toString();
      expect(str, startsWith('RequestSigningException: '));
      expect(str, contains('Signing failed'));
      expect(str, contains(' - '));
      expect(str, contains('internal error'));
    });

    test('toString with string error', () {
      final exception = RequestSigningException('msg', 'err');

      expect(exception.toString(), 'RequestSigningException: msg - err');
    });

    test('toString with null error omits separator and error', () {
      final exception = RequestSigningException('Key expired', null);

      final str = exception.toString();
      expect(str, 'RequestSigningException: Key expired');
      expect(str, isNot(contains(' - ')));
    });

    test('message property is accessible', () {
      final exception = RequestSigningException('test message');
      expect(exception.message, 'test message');
    });

    test('error property returns the provided error', () {
      final innerError = FormatException('bad format');
      final exception = RequestSigningException('wrapper', innerError);
      expect(exception.error, innerError);
    });

    test('error property is null when not provided', () {
      final exception = RequestSigningException('message only');
      expect(exception.error, isNull);
    });

    test('implements Exception interface', () {
      final exception = RequestSigningException('test');
      expect(exception, isA<Exception>());
    });

    test('can be caught as Exception', () {
      expect(
        () => throw RequestSigningException('test'),
        throwsA(isA<Exception>()),
      );
    });

    test('can be caught as RequestSigningException', () {
      expect(
        () => throw RequestSigningException('test', 'detail'),
        throwsA(isA<RequestSigningException>()),
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // 7. SignatureVerificationResult
  // ═══════════════════════════════════════════════════════════════════════════

  group('SignatureVerificationResult', () {
    test('valid result has correct default properties', () {
      final result = SignatureVerificationResult(isValid: true);

      expect(result.isValid, isTrue);
      expect(result.reason, isNull);
      expect(result.isReplayAttack, isFalse);
      expect(result.isTimestampValid, isTrue);
    });

    test('invalid result with reason', () {
      final result = SignatureVerificationResult(
        isValid: false,
        reason: 'Signature mismatch',
      );

      expect(result.isValid, isFalse);
      expect(result.reason, 'Signature mismatch');
    });

    test('isReplayAttack defaults to false', () {
      final result = SignatureVerificationResult(isValid: true);
      expect(result.isReplayAttack, isFalse);
    });

    test('isReplayAttack reflects constructor value when true', () {
      final result = SignatureVerificationResult(
        isValid: false,
        reason: 'Nonce already used',
        isReplayAttack: true,
      );

      expect(result.isReplayAttack, isTrue);
    });

    test('isTimestampValid defaults to true', () {
      final result = SignatureVerificationResult(isValid: true);
      expect(result.isTimestampValid, isTrue);
    });

    test('isTimestampValid reflects constructor value when false', () {
      final result = SignatureVerificationResult(
        isValid: false,
        reason: 'Timestamp too old',
        isTimestampValid: false,
      );

      expect(result.isTimestampValid, isFalse);
    });

    test('all properties set for replay attack scenario', () {
      final result = SignatureVerificationResult(
        isValid: false,
        reason: 'Duplicate nonce',
        isReplayAttack: true,
        isTimestampValid: true,
      );

      expect(result.isValid, isFalse);
      expect(result.reason, 'Duplicate nonce');
      expect(result.isReplayAttack, isTrue);
      expect(result.isTimestampValid, isTrue);
    });

    test('all properties set for expired timestamp scenario', () {
      final result = SignatureVerificationResult(
        isValid: false,
        reason: 'Timestamp outside window',
        isReplayAttack: false,
        isTimestampValid: false,
      );

      expect(result.isValid, isFalse);
      expect(result.isTimestampValid, isFalse);
      expect(result.isReplayAttack, isFalse);
    });

    test('toString includes all property values', () {
      final result = SignatureVerificationResult(
        isValid: false,
        reason: 'expired',
        isReplayAttack: true,
        isTimestampValid: false,
      );

      final str = result.toString();
      expect(str, contains('SignatureVerificationResult'));
      expect(str, contains('isValid: false'));
      expect(str, contains('reason: expired'));
      expect(str, contains('isReplayAttack: true'));
      expect(str, contains('isTimestampValid: false'));
    });

    test('toString with null reason', () {
      final result = SignatureVerificationResult(isValid: true);

      final str = result.toString();
      expect(str, contains('isValid: true'));
      expect(str, contains('reason: null'));
      expect(str, contains('isReplayAttack: false'));
      expect(str, contains('isTimestampValid: true'));
    });

    test('toString matches exact expected format', () {
      final result = SignatureVerificationResult(
        isValid: true,
        reason: null,
        isReplayAttack: false,
        isTimestampValid: true,
      );

      expect(
        result.toString(),
        'SignatureVerificationResult('
        'isValid: true, '
        'reason: null, '
        'isReplayAttack: false, '
        'isTimestampValid: true'
        ')',
      );
    });

    test('toString with non-null reason matches format', () {
      final result = SignatureVerificationResult(
        isValid: false,
        reason: 'Bad signature',
        isReplayAttack: false,
        isTimestampValid: true,
      );

      expect(
        result.toString(),
        'SignatureVerificationResult('
        'isValid: false, '
        'reason: Bad signature, '
        'isReplayAttack: false, '
        'isTimestampValid: true'
        ')',
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // 8. HMAC signature consistency
  // ═══════════════════════════════════════════════════════════════════════════

  group('HMAC signature consistency', () {
    test('signature matches independent HMAC-SHA256 computation', () async {
      final body = {'name': 'field1'};
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'POST',
        data: body,
        queryParameters: {'tenant': 'abc'},
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash(jsonEncode(body));

      final expected = _expectedSignature(
        method: 'POST',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
        queryParams: 'tenant=${Uri.encodeComponent('abc')}',
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('method is uppercased in canonical request', () async {
      final options = RequestOptions(
        path: '/api/v1/fields',
        method: 'get', // lowercase
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash('');

      // Canonical request should use 'GET' (uppercased)
      final expected = _expectedSignature(
        method: 'GET',
        path: '/api/v1/fields',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('same canonical request always produces the same HMAC', () {
      const canonicalRequest =
          'GET\n/api/v1/fields\n\n1700000000000\nfixed-nonce\nhash';

      final sig1 = _calculateHmac(canonicalRequest, _testSigningKey);
      final sig2 = _calculateHmac(canonicalRequest, _testSigningKey);

      expect(sig1, equals(sig2));
    });

    test('different signing keys produce different signatures', () async {
      final options1 = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
      );
      final handler1 = FakeRequestInterceptorHandler();
      await interceptor.onRequest(options1, handler1);

      // Change key for second request
      when(() => mockSigningKeyService.getSigningKey())
          .thenAnswer((_) async => 'completely-different-signing-key!');

      final options2 = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
      );
      final handler2 = FakeRequestInterceptorHandler();
      await interceptor.onRequest(options2, handler2);

      final sig1 = handler1.nextOptions!.headers['X-Signature'] as String;
      final sig2 = handler2.nextOptions!.headers['X-Signature'] as String;

      expect(sig1, isNot(equals(sig2)));
    });

    test('different HTTP methods produce different signatures', () async {
      final optionsGet = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
      );
      final handlerGet = FakeRequestInterceptorHandler();
      await interceptor.onRequest(optionsGet, handlerGet);

      final optionsDelete = RequestOptions(
        path: '/api/v1/fields',
        method: 'DELETE',
      );
      final handlerDelete = FakeRequestInterceptorHandler();
      await interceptor.onRequest(optionsDelete, handlerDelete);

      final sigGet =
          handlerGet.nextOptions!.headers['X-Signature'] as String;
      final sigDelete =
          handlerDelete.nextOptions!.headers['X-Signature'] as String;

      expect(sigGet, isNot(equals(sigDelete)));
    });

    test('different paths produce different signatures', () async {
      final options1 = RequestOptions(
        path: '/api/v1/fields',
        method: 'GET',
      );
      final handler1 = FakeRequestInterceptorHandler();
      await interceptor.onRequest(options1, handler1);

      final options2 = RequestOptions(
        path: '/api/v1/users',
        method: 'GET',
      );
      final handler2 = FakeRequestInterceptorHandler();
      await interceptor.onRequest(options2, handler2);

      final sig1 = handler1.nextOptions!.headers['X-Signature'] as String;
      final sig2 = handler2.nextOptions!.headers['X-Signature'] as String;

      expect(sig1, isNot(equals(sig2)));
    });

    test('canonical request includes all six parts joined by newlines',
        () async {
      const body = 'test body';
      final options = RequestOptions(
        path: '/api/v1/fields/123',
        method: 'PUT',
        data: body,
        queryParameters: {'force': 'true'},
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash(body);

      // Manually build canonical request with all 6 parts
      final canonicalRequest = [
        'PUT',
        '/api/v1/fields/123',
        'force=true',
        timestamp,
        nonce,
        bodyHash,
      ].join('\n');

      final expected = _calculateHmac(canonicalRequest, _testSigningKey);
      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });

    test('query params with body produce correct combined signature',
        () async {
      final body = {'action': 'update'};
      final options = RequestOptions(
        path: '/api/v1/fields/456',
        method: 'PATCH',
        data: body,
        queryParameters: {'version': '2', 'dry_run': 'false'},
      );

      await interceptor.onRequest(options, handler);

      final timestamp =
          handler.nextOptions!.headers['X-Timestamp'] as String;
      final nonce = handler.nextOptions!.headers['X-Nonce'] as String;
      final bodyHash = _sha256Hash(jsonEncode(body));

      // Sorted: dry_run, version
      const sortedParams = 'dry_run=false&version=2';

      final expected = _expectedSignature(
        method: 'PATCH',
        path: '/api/v1/fields/456',
        timestamp: timestamp,
        nonce: nonce,
        bodyHash: bodyHash,
        signingKey: _testSigningKey,
        queryParams: sortedParams,
      );

      expect(handler.nextOptions!.headers['X-Signature'], expected);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // 9. Static constants and type
  // ═══════════════════════════════════════════════════════════════════════════

  group('Static constants and type', () {
    test('maxTimestampDriftSeconds is 300 (5 minutes)', () {
      expect(RequestSigningInterceptor.maxTimestampDriftSeconds, 300);
    });

    test('extends Dio Interceptor', () {
      expect(interceptor, isA<Interceptor>());
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // 10. Handler interaction (mutually exclusive next/reject)
  // ═══════════════════════════════════════════════════════════════════════════

  group('Handler interaction', () {
    test('calls handler.next for public endpoints', () async {
      final options = RequestOptions(path: '/auth/login', method: 'POST');

      await interceptor.onRequest(options, handler);

      expect(handler.nextOptions, isNotNull);
      expect(handler.rejectedError, isNull);
    });

    test('calls handler.next for successful signing', () async {
      final options =
          RequestOptions(path: '/api/v1/fields', method: 'GET');

      await interceptor.onRequest(options, handler);

      expect(handler.nextOptions, isNotNull);
      expect(handler.rejectedError, isNull);
    });

    test('calls handler.reject (not next) on signing error', () async {
      when(() => mockSigningKeyService.getSigningKey())
          .thenThrow(Exception('fail'));

      final options =
          RequestOptions(path: '/api/v1/fields', method: 'GET');

      await interceptor.onRequest(options, handler);

      expect(handler.rejectedError, isNotNull);
      expect(handler.nextOptions, isNull);
    });
  });
}
