/// SAHOOL API Client Tests
/// اختبارات عميل API
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/http/api_client.dart';

// Note: mockito removed due to analyzer 7.x incompatibility
// Tests use real objects where possible

void main() {
  late ApiClient apiClient;

  setUp(() {
    apiClient = ApiClient();
  });

  group('ApiClient Initialization', () {
    test('should create ApiClient with default config', () {
      expect(apiClient, isNotNull);
    });

    test('should create ApiClient with custom base URL', () {
      final customClient = ApiClient(baseUrl: 'https://custom.api.io');
      expect(customClient, isNotNull);
    });
  });

  group('ApiClient Token Management', () {
    test('should set auth token', () {
      apiClient.setAuthToken('test-token-123');
      expect(apiClient.authToken, 'test-token-123');
    });

    test('should update auth token', () {
      apiClient.setAuthToken('initial-token');
      expect(apiClient.authToken, 'initial-token');

      apiClient.setAuthToken('updated-token');
      expect(apiClient.authToken, 'updated-token');
    });

    test('should initially have null auth token', () {
      final freshClient = ApiClient();
      expect(freshClient.authToken, isNull);
    });
  });

  group('ApiClient Tenant Management', () {
    test('should set tenant ID', () {
      apiClient.setTenantId('tenant-abc');
      expect(apiClient.tenantId, 'tenant-abc');
    });

    test('should update tenant ID', () {
      apiClient.setTenantId('tenant-1');
      apiClient.setTenantId('tenant-2');
      expect(apiClient.tenantId, 'tenant-2');
    });
  });

  group('ApiException', () {
    test('should create ApiException with required fields', () {
      final exception = ApiException(
        code: 'TEST_ERROR',
        message: 'Test error message',
      );

      expect(exception.code, 'TEST_ERROR');
      expect(exception.message, 'Test error message');
      expect(exception.statusCode, isNull);
      expect(exception.isNetworkError, false);
    });

    test('should create ApiException with all fields', () {
      final exception = ApiException(
        code: 'HTTP_401',
        message: 'Unauthorized',
        statusCode: 401,
        isNetworkError: false,
      );

      expect(exception.code, 'HTTP_401');
      expect(exception.message, 'Unauthorized');
      expect(exception.statusCode, 401);
      expect(exception.isNetworkError, false);
    });

    test('should create network error exception', () {
      final exception = ApiException(
        code: 'NO_CONNECTION',
        message: 'لا يوجد اتصال بالإنترنت',
        isNetworkError: true,
      );

      expect(exception.isNetworkError, true);
      expect(exception.code, 'NO_CONNECTION');
    });

    test('should create timeout exception', () {
      final exception = ApiException(
        code: 'TIMEOUT',
        message: 'انتهت مهلة الاتصال',
        isNetworkError: true,
      );

      expect(exception.isNetworkError, true);
      expect(exception.code, 'TIMEOUT');
    });

    test('should have correct toString representation', () {
      final exception = ApiException(
        code: 'TEST',
        message: 'Test message',
      );

      expect(exception.toString(), 'ApiException(TEST): Test message');
    });
  });

  group('ApiException HTTP Status Codes', () {
    test('should handle 400 Bad Request', () {
      final exception = ApiException(
        code: 'HTTP_400',
        message: 'طلب غير صالح',
        statusCode: 400,
      );

      expect(exception.statusCode, 400);
    });

    test('should handle 401 Unauthorized', () {
      final exception = ApiException(
        code: 'HTTP_401',
        message: 'غير مصرح',
        statusCode: 401,
      );

      expect(exception.statusCode, 401);
    });

    test('should handle 403 Forbidden', () {
      final exception = ApiException(
        code: 'HTTP_403',
        message: 'محظور',
        statusCode: 403,
      );

      expect(exception.statusCode, 403);
    });

    test('should handle 404 Not Found', () {
      final exception = ApiException(
        code: 'HTTP_404',
        message: 'غير موجود',
        statusCode: 404,
      );

      expect(exception.statusCode, 404);
    });

    test('should handle 500 Internal Server Error', () {
      final exception = ApiException(
        code: 'HTTP_500',
        message: 'خطأ في الخادم',
        statusCode: 500,
      );

      expect(exception.statusCode, 500);
    });

    test('should handle 502 Bad Gateway', () {
      final exception = ApiException(
        code: 'HTTP_502',
        message: 'بوابة غير صالحة',
        statusCode: 502,
      );

      expect(exception.statusCode, 502);
    });

    test('should handle 503 Service Unavailable', () {
      final exception = ApiException(
        code: 'HTTP_503',
        message: 'الخدمة غير متاحة',
        statusCode: 503,
      );

      expect(exception.statusCode, 503);
    });
  });

  group('Arabic Error Messages', () {
    test('should have Arabic message for timeout', () {
      final exception = ApiException(
        code: 'TIMEOUT',
        message: 'انتهت مهلة الاتصال',
        isNetworkError: true,
      );

      expect(exception.message, contains('انتهت'));
    });

    test('should have Arabic message for no connection', () {
      final exception = ApiException(
        code: 'NO_CONNECTION',
        message: 'لا يوجد اتصال بالإنترنت',
        isNetworkError: true,
      );

      expect(exception.message, contains('اتصال'));
    });

    test('should have Arabic message for unknown error', () {
      final exception = ApiException(
        code: 'UNKNOWN',
        message: 'حدث خطأ غير متوقع',
      );

      expect(exception.message, contains('خطأ'));
    });
  });
}
