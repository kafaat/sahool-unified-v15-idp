import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/api/kong_gateway_client.dart';

void main() {
  // ===========================================================================
  // ApiResponse Tests
  // ===========================================================================

  group('ApiResponse.success()', () {
    test('sets success to true', () {
      final response = ApiResponse<String>.success('hello');
      expect(response.success, isTrue);
    });

    test('sets data correctly', () {
      final response = ApiResponse<String>.success('test-data');
      expect(response.data, 'test-data');
    });

    test('errorCode is null on success', () {
      final response = ApiResponse<String>.success('data');
      expect(response.errorCode, isNull);
    });

    test('errorMessage is null on success', () {
      final response = ApiResponse<String>.success('data');
      expect(response.errorMessage, isNull);
    });

    test('errorMessageAr is null on success', () {
      final response = ApiResponse<String>.success('data');
      expect(response.errorMessageAr, isNull);
    });

    test('requestId is set when provided', () {
      final response =
          ApiResponse<String>.success('data', requestId: 'req-123');
      expect(response.requestId, 'req-123');
    });

    test('requestId is null when not provided', () {
      final response = ApiResponse<String>.success('data');
      expect(response.requestId, isNull);
    });

    test('works with int data type', () {
      final response = ApiResponse<int>.success(42);
      expect(response.data, 42);
      expect(response.success, isTrue);
    });

    test('works with Map data type', () {
      final data = {'key': 'value', 'count': 5};
      final response = ApiResponse<Map<String, dynamic>>.success(data);
      expect(response.data, data);
      expect(response.success, isTrue);
    });

    test('works with List data type', () {
      final data = [1, 2, 3];
      final response = ApiResponse<List<int>>.success(data);
      expect(response.data, data);
      expect(response.success, isTrue);
    });

    test('works with null data on success', () {
      final response = ApiResponse<String?>.success(null);
      expect(response.success, isTrue);
      expect(response.data, isNull);
    });

    test('works with bool data type', () {
      final response = ApiResponse<bool>.success(true);
      expect(response.data, isTrue);
    });
  });

  group('ApiResponse.error()', () {
    test('sets success to false', () {
      final response = ApiResponse<String>.error('E001', 'Something failed');
      expect(response.success, isFalse);
    });

    test('sets errorCode correctly', () {
      final response =
          ApiResponse<String>.error('E1001', 'Invalid request');
      expect(response.errorCode, 'E1001');
    });

    test('sets errorMessage correctly', () {
      final response =
          ApiResponse<String>.error('E001', 'Request failed');
      expect(response.errorMessage, 'Request failed');
    });

    test('data is null on error', () {
      final response = ApiResponse<String>.error('E001', 'fail');
      expect(response.data, isNull);
    });

    test('sets messageAr when provided', () {
      final response = ApiResponse<String>.error(
        'E001',
        'Failed',
        messageAr: 'فشل الطلب',
      );
      expect(response.errorMessageAr, 'فشل الطلب');
    });

    test('messageAr is null when not provided', () {
      final response = ApiResponse<String>.error('E001', 'Failed');
      expect(response.errorMessageAr, isNull);
    });

    test('sets requestId when provided', () {
      final response = ApiResponse<String>.error(
        'E001',
        'Failed',
        requestId: 'req-456',
      );
      expect(response.requestId, 'req-456');
    });

    test('requestId is null when not provided', () {
      final response = ApiResponse<String>.error('E001', 'Failed');
      expect(response.requestId, isNull);
    });

    test('supports all error parameters together', () {
      final response = ApiResponse<int>.error(
        'E4001',
        'Resource exhausted',
        messageAr: 'الموارد مستنفدة',
        requestId: 'req-789',
      );
      expect(response.success, isFalse);
      expect(response.errorCode, 'E4001');
      expect(response.errorMessage, 'Resource exhausted');
      expect(response.errorMessageAr, 'الموارد مستنفدة');
      expect(response.requestId, 'req-789');
      expect(response.data, isNull);
    });

    test('works with any generic type parameter', () {
      final response = ApiResponse<Map<String, dynamic>>.error(
        'E500',
        'Internal error',
      );
      expect(response.success, isFalse);
      expect(response.data, isNull);
    });
  });

  // ===========================================================================
  // ServiceHealthStatus Tests
  // ===========================================================================

  group('ServiceHealthStatus', () {
    test('has exactly 4 values', () {
      expect(ServiceHealthStatus.values.length, 4);
    });

    test('contains healthy value', () {
      expect(ServiceHealthStatus.values, contains(ServiceHealthStatus.healthy));
    });

    test('contains degraded value', () {
      expect(
          ServiceHealthStatus.values, contains(ServiceHealthStatus.degraded));
    });

    test('contains unhealthy value', () {
      expect(
          ServiceHealthStatus.values, contains(ServiceHealthStatus.unhealthy));
    });

    test('contains unknown value', () {
      expect(
          ServiceHealthStatus.values, contains(ServiceHealthStatus.unknown));
    });
  });

  // ===========================================================================
  // ServiceHealth Tests
  // ===========================================================================

  group('ServiceHealth', () {
    test('isHealthy returns true when status is healthy', () {
      final health = ServiceHealth(
        serviceName: 'field-management',
        status: ServiceHealthStatus.healthy,
        latencyMs: 50,
        timestamp: DateTime.now(),
      );
      expect(health.isHealthy, isTrue);
    });

    test('isHealthy returns false when status is degraded', () {
      final health = ServiceHealth(
        serviceName: 'weather-service',
        status: ServiceHealthStatus.degraded,
        latencyMs: 500,
        timestamp: DateTime.now(),
      );
      expect(health.isHealthy, isFalse);
    });

    test('isHealthy returns false when status is unhealthy', () {
      final health = ServiceHealth(
        serviceName: 'auth',
        status: ServiceHealthStatus.unhealthy,
        latencyMs: 0,
        timestamp: DateTime.now(),
      );
      expect(health.isHealthy, isFalse);
    });

    test('isHealthy returns false when status is unknown', () {
      final health = ServiceHealth(
        serviceName: 'iot-service',
        status: ServiceHealthStatus.unknown,
        latencyMs: 0,
        timestamp: DateTime.now(),
      );
      expect(health.isHealthy, isFalse);
    });

    test('stores serviceName correctly', () {
      final health = ServiceHealth(
        serviceName: 'advisory-service',
        status: ServiceHealthStatus.healthy,
        latencyMs: 100,
        timestamp: DateTime.now(),
      );
      expect(health.serviceName, 'advisory-service');
    });

    test('stores latencyMs correctly', () {
      final health = ServiceHealth(
        serviceName: 'test',
        status: ServiceHealthStatus.healthy,
        latencyMs: 250,
        timestamp: DateTime.now(),
      );
      expect(health.latencyMs, 250);
    });

    test('stores timestamp correctly', () {
      final now = DateTime(2026, 3, 23, 10, 30);
      final health = ServiceHealth(
        serviceName: 'test',
        status: ServiceHealthStatus.healthy,
        latencyMs: 50,
        timestamp: now,
      );
      expect(health.timestamp, now);
    });

    test('errorMessage is null by default', () {
      final health = ServiceHealth(
        serviceName: 'test',
        status: ServiceHealthStatus.healthy,
        latencyMs: 50,
        timestamp: DateTime.now(),
      );
      expect(health.errorMessage, isNull);
    });

    test('errorMessage is stored when provided', () {
      final health = ServiceHealth(
        serviceName: 'test',
        status: ServiceHealthStatus.unhealthy,
        latencyMs: 0,
        timestamp: DateTime.now(),
        errorMessage: 'Connection refused',
      );
      expect(health.errorMessage, 'Connection refused');
    });
  });

  // ===========================================================================
  // KongService Tests
  // ===========================================================================

  group('KongService', () {
    test('stores name correctly', () {
      const service = KongService(
        name: 'test-service',
        nameAr: 'خدمة اختبار',
        basePath: '/api/v1/test',
      );
      expect(service.name, 'test-service');
    });

    test('stores nameAr correctly', () {
      const service = KongService(
        name: 'test-service',
        nameAr: 'خدمة اختبار',
        basePath: '/api/v1/test',
      );
      expect(service.nameAr, 'خدمة اختبار');
    });

    test('stores basePath correctly', () {
      const service = KongService(
        name: 'test-service',
        nameAr: 'خدمة اختبار',
        basePath: '/api/v1/test',
      );
      expect(service.basePath, '/api/v1/test');
    });

    test('default timeout is 30 seconds', () {
      const service = KongService(
        name: 'test-service',
        nameAr: 'خدمة اختبار',
        basePath: '/api/v1/test',
      );
      expect(service.timeout, const Duration(seconds: 30));
    });

    test('default maxRetries is 3', () {
      const service = KongService(
        name: 'test-service',
        nameAr: 'خدمة اختبار',
        basePath: '/api/v1/test',
      );
      expect(service.maxRetries, 3);
    });

    test('custom timeout is stored', () {
      const service = KongService(
        name: 'test-service',
        nameAr: 'خدمة اختبار',
        basePath: '/api/v1/test',
        timeout: Duration(seconds: 60),
      );
      expect(service.timeout, const Duration(seconds: 60));
    });

    test('custom maxRetries is stored', () {
      const service = KongService(
        name: 'test-service',
        nameAr: 'خدمة اختبار',
        basePath: '/api/v1/test',
        maxRetries: 5,
      );
      expect(service.maxRetries, 5);
    });
  });

  // ===========================================================================
  // KongServices Registry Tests
  // ===========================================================================

  group('KongServices registry', () {
    test('fields service exists with correct name', () {
      expect(KongServices.fields.name, 'field-management');
    });

    test('fields service has correct basePath', () {
      expect(KongServices.fields.basePath, '/api/v1/fields');
    });

    test('auth service exists with correct name', () {
      expect(KongServices.auth.name, 'user-service');
    });

    test('auth service has correct basePath', () {
      expect(KongServices.auth.basePath, '/api/v1/auth');
    });

    test('weather service exists with correct name', () {
      expect(KongServices.weather.name, 'weather-service');
    });

    test('weather service has correct basePath', () {
      expect(KongServices.weather.basePath, '/api/v1/weather');
    });

    test('vegetation service exists', () {
      expect(KongServices.vegetation.name, 'vegetation-analysis');
    });

    test('satellite service exists', () {
      expect(KongServices.satellite.name, 'satellite');
    });

    test('ndvi service exists', () {
      expect(KongServices.ndvi.name, 'ndvi');
    });

    test('irrigation service exists', () {
      expect(KongServices.irrigation.name, 'irrigation-smart');
    });

    test('advisory service exists', () {
      expect(KongServices.advisory.name, 'advisory-service');
    });

    test('cropHealth service exists', () {
      expect(KongServices.cropHealth.name, 'crop-intelligence');
    });

    test('tasks service exists', () {
      expect(KongServices.tasks.name, 'task-service');
    });

    test('equipment service exists', () {
      expect(KongServices.equipment.name, 'equipment-service');
    });

    test('alerts service exists', () {
      expect(KongServices.alerts.name, 'alert-service');
    });

    test('notifications service exists', () {
      expect(KongServices.notifications.name, 'notification-service');
    });

    test('marketplace service exists', () {
      expect(KongServices.marketplace.name, 'marketplace');
    });

    test('iot service exists', () {
      expect(KongServices.iot.name, 'iot-service');
    });

    test('yield service exists', () {
      expect(KongServices.yield_.name, 'yield-engine');
    });

    test('billing service exists', () {
      expect(KongServices.billing.name, 'billing-core');
    });

    test('inventory service exists', () {
      expect(KongServices.inventory.name, 'inventory-service');
    });

    test('copilot service exists with extended timeout', () {
      expect(KongServices.copilot.name, 'copilot-api');
      expect(KongServices.copilot.timeout, const Duration(seconds: 120));
    });

    test('aiAdvisor service exists with extended timeout', () {
      expect(KongServices.aiAdvisor.name, 'ai-advisor');
      expect(KongServices.aiAdvisor.timeout, const Duration(seconds: 60));
    });

    test('pestDetection service exists', () {
      expect(KongServices.pestDetection.name, 'pest-detection-service');
    });

    test('soilAnalysis service exists', () {
      expect(KongServices.soilAnalysis.name, 'soil-analysis-service');
    });

    test('astronomicalCalendar service exists', () {
      expect(KongServices.astronomicalCalendar.name, 'astronomical-calendar');
    });

    test('all list contains all registered services', () {
      final all = KongServices.all;
      expect(all.length, greaterThanOrEqualTo(20));
    });

    test('all services have non-empty name', () {
      for (final service in KongServices.all) {
        expect(service.name, isNotEmpty,
            reason: 'Service at basePath ${service.basePath} has empty name');
      }
    });

    test('all services have non-empty nameAr', () {
      for (final service in KongServices.all) {
        expect(service.nameAr, isNotEmpty,
            reason: 'Service ${service.name} has empty nameAr');
      }
    });

    test('all services have basePath starting with /api/', () {
      for (final service in KongServices.all) {
        expect(service.basePath, startsWith('/api/'),
            reason:
                'Service ${service.name} basePath does not start with /api/');
      }
    });

    test('getByName returns correct service', () {
      final service = KongServices.getByName('weather-service');
      expect(service, isNotNull);
      expect(service!.name, 'weather-service');
    });

    test('getByName returns null for unknown service', () {
      final service = KongServices.getByName('nonexistent-service');
      expect(service, isNull);
    });

    test('all services have positive timeout', () {
      for (final service in KongServices.all) {
        expect(service.timeout.inSeconds, greaterThan(0),
            reason: 'Service ${service.name} has zero timeout');
      }
    });

    test('all services have positive maxRetries', () {
      for (final service in KongServices.all) {
        expect(service.maxRetries, greaterThan(0),
            reason: 'Service ${service.name} has zero maxRetries');
      }
    });
  });
}
