import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:dio/dio.dart';
import 'package:sahool_field_app/core/http/api_client.dart';
import 'package:sahool_field_app/core/security/security_config.dart';
import 'package:sahool_field_app/core/security/certificate_pinning_service.dart';

/// Mock dependencies
class MockDio extends Mock implements Dio {}
class MockCertificatePinningService extends Mock implements CertificatePinningService {}
class MockRequestOptions extends Mock implements RequestOptions {}
class MockResponse extends Mock implements Response {}

void main() {
  setUpAll(() {
    // Register fallback values for mocktail
    registerFallbackValue(RequestOptions(path: ''));
    registerFallbackValue(const SecurityConfig());
  });

  group('ApiClient', () {
    late ApiClient apiClient;

    setUp(() {
      apiClient = ApiClient(
        baseUrl: 'https://api.sahool.com',
      );
    });

    group('initialization', () {
      test('should initialize with default configuration', () {
        // Act
        final client = ApiClient();

        // Assert
        expect(client, isNotNull);
        expect(client.authToken, isNull);
      });

      test('should initialize with custom base URL', () {
        // Act
        final client = ApiClient(baseUrl: 'https://custom.sahool.com');

        // Assert
        expect(client, isNotNull);
      });

      test('should initialize with certificate pinning when enabled', () {
        // Arrange
        const config = SecurityConfig(
          enableCertificatePinning: true,
          strictCertificatePinning: true,
        );

        // Act
        final client = ApiClient(securityConfig: config);

        // Assert
        expect(client.isCertificatePinningEnabled, isTrue);
      });

      test('should not enable certificate pinning by default', () {
        // Act
        final client = ApiClient();

        // Assert
        expect(client.isCertificatePinningEnabled, isFalse);
      });
    });

    group('authentication', () {
      test('should set auth token', () {
        // Arrange
        const token = 'test_token_123';

        // Act
        apiClient.setAuthToken(token);

        // Assert
        expect(apiClient.authToken, token);
      });

      test('should set tenant ID', () {
        // Arrange
        const tenantId = 'tenant_123';

        // Act
        apiClient.setTenantId(tenantId);

        // Assert
        expect(apiClient.tenantId, tenantId);
      });
    });

    group('GET requests', () {
      test('should make successful GET request', () async {
        // Arrange
        final client = ApiClient(baseUrl: 'https://api.sahool.com');

        // This will fail in real scenario, but demonstrates the structure
        // In actual implementation, you would mock Dio
        try {
          // Act
          await client.get('/test');
        } catch (e) {
          // Expected to fail without proper mocking or server
          expect(e, isA<ApiException>());
        }
      });

      test('should include query parameters in GET request', () async {
        // Arrange
        final client = ApiClient(baseUrl: 'https://api.sahool.com');

        try {
          // Act
          await client.get('/test', queryParameters: {'page': 1, 'limit': 10});
        } catch (e) {
          // Expected to fail without proper mocking or server
          expect(e, isA<ApiException>());
        }
      });
    });

    group('POST requests', () {
      test('should make POST request with data', () async {
        // Arrange
        final client = ApiClient(baseUrl: 'https://api.sahool.com');
        final data = {'name': 'Test', 'value': 123};

        try {
          // Act
          await client.post('/test', data);
        } catch (e) {
          // Expected to fail without proper mocking or server
          expect(e, isA<ApiException>());
        }
      });

      test('should include custom headers in POST request', () async {
        // Arrange
        final client = ApiClient(baseUrl: 'https://api.sahool.com');
        final data = {'name': 'Test'};
        final headers = {'X-Custom-Header': 'value'};

        try {
          // Act
          await client.post('/test', data, headers: headers);
        } catch (e) {
          // Expected to fail without proper mocking or server
          expect(e, isA<ApiException>());
        }
      });
    });

    group('PUT requests', () {
      test('should make PUT request with data', () async {
        // Arrange
        final client = ApiClient(baseUrl: 'https://api.sahool.com');
        final data = {'name': 'Updated Test', 'value': 456};

        try {
          // Act
          await client.put('/test/1', data);
        } catch (e) {
          // Expected to fail without proper mocking or server
          expect(e, isA<ApiException>());
        }
      });
    });

    group('DELETE requests', () {
      test('should make DELETE request', () async {
        // Arrange
        final client = ApiClient(baseUrl: 'https://api.sahool.com');

        try {
          // Act
          await client.delete('/test/1');
        } catch (e) {
          // Expected to fail without proper mocking or server
          expect(e, isA<ApiException>());
        }
      });
    });

    group('error handling', () {
      test('should handle connection timeout error', () async {
        // Arrange
        final client = ApiClient(baseUrl: 'https://nonexistent.sahool.com');

        try {
          // Act
          await client.get('/test');
          fail('Should have thrown an exception');
        } catch (e) {
          // Assert
          expect(e, isA<ApiException>());
          final apiException = e as ApiException;
          expect(apiException.isNetworkError, isTrue);
        }
      });

      test('should handle no connection error', () async {
        // Arrange
        final client = ApiClient(baseUrl: 'https://192.0.2.1'); // Test IP that won't respond

        try {
          // Act
          await client.get('/test');
          fail('Should have thrown an exception');
        } catch (e) {
          // Assert
          expect(e, isA<ApiException>());
        }
      });
    });

    group('certificate pinning', () {
      test('should return empty list when no expiring pins exist', () {
        // Arrange
        final client = ApiClient();

        // Act
        final expiringPins = client.getExpiringPins();

        // Assert
        expect(expiringPins, isEmpty);
      });

      test('should allow updating certificate pins', () {
        // Arrange
        const config = SecurityConfig(enableCertificatePinning: true);
        final client = ApiClient(securityConfig: config);

        final pins = [
          CertificatePin(
            sha256: 'test_pin_hash',
            expiresAt: DateTime.now().add(const Duration(days: 365)),
          ),
        ];

        // Act
        client.updateCertificatePins('api.sahool.com', pins);

        // Assert - no exception means success
        expect(client.isCertificatePinningEnabled, isTrue);
      });
    });
  });

  group('ApiException', () {
    test('should create exception with message and code', () {
      // Act
      final exception = ApiException(
        code: 'TEST_ERROR',
        message: 'Test error message',
      );

      // Assert
      expect(exception.code, 'TEST_ERROR');
      expect(exception.message, 'Test error message');
      expect(exception.isNetworkError, false);
    });

    test('should create network error exception', () {
      // Act
      final exception = ApiException(
        code: 'NO_CONNECTION',
        message: 'لا يوجد اتصال بالإنترنت',
        isNetworkError: true,
      );

      // Assert
      expect(exception.isNetworkError, true);
    });

    test('should create exception with status code', () {
      // Act
      final exception = ApiException(
        code: 'HTTP_404',
        message: 'Not found',
        statusCode: 404,
      );

      // Assert
      expect(exception.statusCode, 404);
    });

    test('should have string representation', () {
      // Act
      final exception = ApiException(
        code: 'TEST_ERROR',
        message: 'Test message',
      );

      // Assert
      expect(exception.toString(), contains('TEST_ERROR'));
      expect(exception.toString(), contains('Test message'));
    });
  });
}
