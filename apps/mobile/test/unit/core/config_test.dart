/// Unit Tests for Configuration Classes
/// اختبارات وحدات التكوين
library;
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/config/api_config.dart';
import 'package:sahool_field_app/core/config/security_config.dart';
import 'package:sahool_field_app/core/contracts/service_ports.dart' as contracts;

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // ApiConfig Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('ApiConfig', () {
    group('Timeout Constants', () {
      test('connectTimeout is 30 seconds', () {
        expect(ApiConfig.connectTimeout, const Duration(seconds: 30));
      });

      test('sendTimeout is 15 seconds', () {
        expect(ApiConfig.sendTimeout, const Duration(seconds: 15));
      });

      test('receiveTimeout is 15 seconds', () {
        expect(ApiConfig.receiveTimeout, const Duration(seconds: 15));
      });

      test('longOperationTimeout is 60 seconds', () {
        expect(ApiConfig.longOperationTimeout, const Duration(seconds: 60));
      });
    });

    group('Default Headers', () {
      test('defaultHeaders contains required headers', () {
        final headers = ApiConfig.defaultHeaders;

        expect(headers['Content-Type'], 'application/json');
        expect(headers['Accept'], 'application/json');
        expect(headers['Accept-Language'], 'ar,en');
      });

      test('authHeaders includes Authorization bearer token', () {
        final headers = ApiConfig.authHeaders('test-token-123');

        expect(headers['Authorization'], 'Bearer test-token-123');
        expect(headers['Content-Type'], 'application/json');
        expect(headers['Accept'], 'application/json');
      });

      test('tenantHeaders includes X-Tenant-Id', () {
        final headers = ApiConfig.tenantHeaders('token', 'tenant-abc');

        expect(headers['X-Tenant-Id'], 'tenant-abc');
        expect(headers['Authorization'], 'Bearer token');
        expect(headers['Content-Type'], 'application/json');
      });

      test('etagHeaders includes If-Match header', () {
        final headers = ApiConfig.etagHeaders('token', 'etag-v1');

        expect(headers['If-Match'], 'etag-v1');
        expect(headers['Authorization'], 'Bearer token');
      });
    });

    group('Endpoint URL Construction', () {
      test('fieldById constructs correct URL', () {
        final url = ApiConfig.fieldById('field-123');
        expect(url, contains('/api/v1/fields/field-123'));
      });

      test('taskById constructs correct URL', () {
        final url = ApiConfig.taskById('task-456');
        expect(url, contains('/api/v1/tasks/task-456'));
      });

      test('ndviByFieldId constructs correct URL', () {
        final url = ApiConfig.ndviByFieldId('field-789');
        expect(url, contains('field-789'));
      });

      test('weatherByLocation constructs correct URL', () {
        final url = ApiConfig.weatherByLocation('riyadh');
        expect(url, contains('riyadh'));
      });

      test('treatmentDetails constructs correct URL', () {
        final url = ApiConfig.treatmentDetails('disease-001');
        expect(url, contains('treatment/disease-001'));
      });

      test('equipmentById constructs correct URL', () {
        final url = ApiConfig.equipmentById('eq-001');
        expect(url, contains('eq-001'));
      });

      test('iotDeviceById constructs correct URL', () {
        final url = ApiConfig.iotDeviceById('device-001');
        expect(url, contains('device-001'));
      });

      test('iotDevicesByField constructs correct URL', () {
        final url = ApiConfig.iotDevicesByField('field-001');
        expect(url, contains('field/field-001'));
      });

      test('iotSensorReadings constructs correct URL', () {
        final url = ApiConfig.iotSensorReadings('device-001');
        expect(url, contains('sensors/device-001/readings'));
      });

      test('iotDeviceCommand constructs correct URL', () {
        final url = ApiConfig.iotDeviceCommand('device-001');
        expect(url, contains('device-001/command'));
      });

      test('wallet constructs correct URL for userId', () {
        final url = ApiConfig.wallet('user-001');
        expect(url, contains('wallet/user-001'));
      });

      test('marketProductById constructs correct URL', () {
        final url = ApiConfig.marketProductById('prod-001');
        expect(url, contains('products/prod-001'));
      });

      test('aiAdvisorRecommendations constructs correct URL', () {
        final url = ApiConfig.aiAdvisorRecommendations('field-001');
        expect(url, contains('recommendations/field-001'));
      });

      test('billingPayInvoice constructs correct URL', () {
        final url = ApiConfig.billingPayInvoice('inv-001');
        expect(url, contains('invoices/inv-001/pay'));
      });
    });

    group('Health Check Configuration', () {
      test('healthCheck appends /healthz to service URL', () {
        final url = ApiConfig.healthCheck('http://localhost:8090');
        expect(url, 'http://localhost:8090/healthz');
      });

      test('allHealthChecks returns map of all services', () {
        final checks = ApiConfig.allHealthChecks;

        expect(checks, isA<Map<String, String>>());
        expect(checks.containsKey('satellite'), true);
        expect(checks.containsKey('weather'), true);
        expect(checks.containsKey('equipment'), true);
        expect(checks.containsKey('marketplace'), true);
        expect(checks.containsKey('notifications'), true);

        // All values should end with /healthz
        for (final url in checks.values) {
          expect(url, endsWith('/healthz'));
        }
      });
    });

    group('useDirectServices flag', () {
      test('useDirectServices is false by default', () {
        expect(ApiConfig.useDirectServices, false);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SecurityConfig Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SecurityConfig', () {
    group('Token Configuration', () {
      test('accessTokenExpiryMinutes defaults to 15', () {
        expect(SecurityConfig.accessTokenExpiryMinutes, 15);
      });

      test('refreshTokenExpiryDays defaults to 7', () {
        expect(SecurityConfig.refreshTokenExpiryDays, 7);
      });

      test('sessionIdleTimeoutMinutes defaults to 30', () {
        expect(SecurityConfig.sessionIdleTimeoutMinutes, 30);
      });
    });

    group('Authentication Configuration', () {
      test('maxFailedLoginAttempts defaults to 5', () {
        expect(SecurityConfig.maxFailedLoginAttempts, 5);
      });

      test('lockoutDurationMinutes defaults to 15', () {
        expect(SecurityConfig.lockoutDurationMinutes, 15);
      });
    });

    group('PIN & Password Configuration', () {
      test('minPinLength defaults to 6', () {
        expect(SecurityConfig.minPinLength, 6);
      });

      test('minPasswordLength defaults to 8', () {
        expect(SecurityConfig.minPasswordLength, 8);
      });

      test('requireNumbers is always true', () {
        expect(SecurityConfig.requireNumbers, true);
      });
    });

    group('Network Security', () {
      test('requestTimeoutSeconds defaults to 30', () {
        expect(SecurityConfig.requestTimeoutSeconds, 30);
      });

      test('maxRetryAttempts defaults to 3', () {
        expect(SecurityConfig.maxRetryAttempts, 3);
      });

      test('allowedHosts contains production hosts', () {
        final hosts = SecurityConfig.allowedHosts;

        expect(hosts, contains('api.sahool.app'));
        expect(hosts, contains('api-staging.sahool.app'));
        expect(hosts, contains('api.sahool.io'));
        expect(hosts, contains('*.sahool.io'));
      });
    });

    group('Security Features', () {
      test('enableSecureStorage is always true', () {
        expect(SecurityConfig.enableSecureStorage, true);
      });

      test('enableBiometricAuth defaults to true', () {
        expect(SecurityConfig.enableBiometricAuth, true);
      });
    });

    group('Debug Helpers', () {
      test('toDebugMap returns comprehensive security config', () {
        final map = SecurityConfig.toDebugMap();

        expect(map.containsKey('environment'), true);
        expect(map.containsKey('features'), true);
        expect(map.containsKey('debug'), true);
        expect(map.containsKey('tokens'), true);
        expect(map.containsKey('auth'), true);
        expect(map.containsKey('network'), true);

        final features = map['features'] as Map<String, dynamic>;
        expect(features.containsKey('secureStorage'), true);
        expect(features.containsKey('biometricAuth'), true);
        expect(features.containsKey('certificatePinning'), true);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ServicePorts (Contracts) Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('ServicePorts (contracts)', () {
    test('core service ports are correct', () {
      expect(contracts.ServicePorts.fieldManagement, 3000);
      expect(contracts.ServicePorts.userService, 3025);
      expect(contracts.ServicePorts.marketplace, 3010);
      expect(contracts.ServicePorts.researchCore, 3015);
    });

    test('intelligence layer ports are correct', () {
      expect(contracts.ServicePorts.vegetationAnalysis, 8090);
      expect(contracts.ServicePorts.indicators, 8091);
      expect(contracts.ServicePorts.weather, 8092);
      expect(contracts.ServicePorts.advisory, 8093);
      expect(contracts.ServicePorts.irrigationSmart, 8094);
      expect(contracts.ServicePorts.cropIntelligence, 8095);
    });

    test('business layer ports are correct', () {
      expect(contracts.ServicePorts.equipment, 8101);
      expect(contracts.ServicePorts.taskService, 8103);
      expect(contracts.ServicePorts.notifications, 8110);
      expect(contracts.ServicePorts.billingCore, 8089);
      expect(contracts.ServicePorts.inventory, 8116);
    });

    test('AI/agent service ports are correct', () {
      expect(contracts.ServicePorts.copilotApi, 8088);
      expect(contracts.ServicePorts.aiAdvisor, 8112);
      expect(contracts.ServicePorts.agentRegistry, 8160);
      expect(contracts.ServicePorts.llmOrchestrator, 8164);
      expect(contracts.ServicePorts.knowledgeGraph, 8140);
    });

    test('vision & terrain ports are correct', () {
      expect(contracts.ServicePorts.yoloVision, 8150);
      expect(contracts.ServicePorts.terrainCore, 8185);
      expect(contracts.ServicePorts.hydrology, 8165);
      expect(contracts.ServicePorts.levelingOptimizer, 8170);
      expect(contracts.ServicePorts.edgeOrchestrator, 8180);
    });

    test('infrastructure ports are correct', () {
      expect(contracts.ServicePorts.kongGateway, 8000);
      expect(contracts.ServicePorts.kongAdmin, 8001);
      expect(contracts.ServicePorts.nats, 4222);
      expect(contracts.ServicePorts.postgres, 5432);
      expect(contracts.ServicePorts.pgbouncer, 6432);
      expect(contracts.ServicePorts.redis, 6379);
    });

    test('IoT ports are correct', () {
      expect(contracts.ServicePorts.iotService, 8117);
      expect(contracts.ServicePorts.iotGateway, 8106);
      expect(contracts.ServicePorts.iotSensorHub, 8251);
    });

    test('getServiceUrl constructs correct URL', () {
      expect(
        contracts.getServiceUrl(3000),
        'http://localhost:3000',
      );

      expect(
        contracts.getServiceUrl(8090, host: 'http://10.0.2.2'),
        'http://10.0.2.2:8090',
      );
    });
  });
}
