/// SAHOOL API Configuration Tests
/// اختبارات إعدادات API
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_mobile_core/core/config/api_config.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('ServicePorts', () {
    test('should have correct field core port', () {
      expect(ServicePorts.fieldCore, 3000);
    });

    test('should have correct marketplace port', () {
      expect(ServicePorts.marketplace, 3010);
    });

    test('should have correct satellite service port', () {
      expect(ServicePorts.satellite, 8090);
    });

    test('should have correct indicators service port', () {
      expect(ServicePorts.indicators, 8091);
    });

    test('should have correct weather service port', () {
      expect(ServicePorts.weather, 8092);
    });

    test('should have correct fertilizer service port', () {
      expect(ServicePorts.fertilizer, 8093);
    });

    test('should have correct irrigation service port', () {
      expect(ServicePorts.irrigation, 8094);
    });

    test('should have correct crop health service port', () {
      expect(ServicePorts.cropHealth, 8095);
    });

    test('should have correct virtual sensors service port', () {
      expect(ServicePorts.virtualSensors, 8119);
    });

    test('should have correct chat service port', () {
      expect(ServicePorts.chat, 8115);
    });

    test('should have correct community chat service port', () {
      expect(ServicePorts.communityChat, 8115);
    });

    test('should have correct spray (yield-prediction) service port', () {
      expect(ServicePorts.spray, 8152);
    });

    test('should have correct equipment service port', () {
      expect(ServicePorts.equipment, 8101);
    });

    test('should have correct notifications service port', () {
      expect(ServicePorts.notifications, 8110);
    });

    test('should have correct gateway port', () {
      expect(ServicePorts.gateway, 8000);
    });
  });

  group('ApiConfig URLs', () {
    test('should generate correct field core base URL', () {
      expect(ApiConfig.baseUrl, contains(':${ServicePorts.fieldCore}'));
    });

    test('should generate correct satellite service URL', () {
      expect(ApiConfig.satelliteServiceUrl, contains(':${ServicePorts.satellite}'));
    });

    test('should generate correct weather service URL', () {
      expect(ApiConfig.weatherServiceUrl, contains(':${ServicePorts.weather}'));
    });

    test('should generate correct indicators service URL', () {
      expect(ApiConfig.indicatorsServiceUrl, contains(':${ServicePorts.indicators}'));
    });

    test('should generate correct fertilizer service URL', () {
      expect(ApiConfig.fertilizerServiceUrl, contains(':${ServicePorts.fertilizer}'));
    });

    test('should generate correct irrigation service URL', () {
      expect(ApiConfig.irrigationServiceUrl, contains(':${ServicePorts.irrigation}'));
    });

    test('should generate correct crop health service URL', () {
      expect(ApiConfig.cropHealthServiceUrl, contains(':${ServicePorts.cropHealth}'));
    });

    test('should generate correct virtual sensors service URL', () {
      expect(ApiConfig.virtualSensorsServiceUrl, contains(':${ServicePorts.virtualSensors}'));
    });

    test('should generate correct chat service URL', () {
      expect(ApiConfig.chatServiceUrl, contains(':${ServicePorts.chat}'));
    });

    test('should have production base URL', () {
      expect(ApiConfig.productionBaseUrl, 'https://api.sahool.io');
    });
  });

  group('ApiConfig Endpoints - Field Core', () {
    test('should have correct fields endpoint', () {
      expect(ApiConfig.fields, contains('/api/v1/fields'));
    });

    test('should generate correct field by id endpoint', () {
      expect(ApiConfig.fieldById('123'), contains('/api/v1/fields/123'));
    });

    test('should have correct tasks endpoint', () {
      expect(ApiConfig.tasks, contains('/api/v1/tasks'));
    });

    test('should generate correct task by id endpoint', () {
      expect(ApiConfig.taskById('456'), contains('/api/v1/tasks/456'));
    });

    test('should have correct login endpoint', () {
      expect(ApiConfig.login, contains('/api/v1/auth/login'));
    });

    test('should have correct register endpoint', () {
      expect(ApiConfig.register, contains('/api/v1/auth/register'));
    });

    test('should have correct refresh token endpoint', () {
      expect(ApiConfig.refreshToken, contains('/api/v1/auth/refresh'));
    });
  });

  group('ApiConfig Endpoints - Satellite Service', () {
    test('should have correct ndvi endpoint', () {
      expect(ApiConfig.ndvi, contains('/satellite/analyze'));
    });

    test('should generate correct ndvi by field id endpoint', () {
      expect(ApiConfig.ndviByFieldId('field-123'), contains('/satellite/analyze/field-123'));
    });

    test('should have correct ndvi timeseries endpoint', () {
      expect(ApiConfig.ndviTimeseries, contains('/satellite/timeseries'));
    });

    test('should have correct satellites endpoint', () {
      expect(ApiConfig.satellites, contains('/satellite/satellites'));
    });

    test('should have correct regions endpoint', () {
      expect(ApiConfig.regions, contains('/satellite/regions'));
    });

    test('should have correct imagery endpoint', () {
      expect(ApiConfig.imagery, contains('/satellite/imagery'));
    });
  });

  group('ApiConfig Endpoints - Weather Service', () {
    test('should have correct current weather endpoint', () {
      expect(ApiConfig.weather, contains('/weather/current'));
    });

    test('should generate correct weather by location endpoint', () {
      expect(ApiConfig.weatherByLocation('sanaa'), contains('/weather/current/sanaa'));
    });

    test('should have correct forecast endpoint', () {
      expect(ApiConfig.forecast, contains('/weather/forecast'));
    });

    test('should have correct weather alerts endpoint', () {
      expect(ApiConfig.weatherAlerts, contains('/weather/alerts'));
    });

    test('should have correct weather locations endpoint', () {
      expect(ApiConfig.weatherLocations, contains('/weather/locations'));
    });

    test('should have correct agricultural calendar endpoint', () {
      expect(ApiConfig.agriculturalCalendar, contains('/weather/agricultural-calendar'));
    });
  });

  group('ApiConfig Endpoints - Fertilizer Advisor', () {
    test('should have correct fertilizer crops endpoint', () {
      expect(ApiConfig.fertilizerCrops, contains('/fertilizer/crops'));
    });

    test('should have correct fertilizer types endpoint', () {
      expect(ApiConfig.fertilizerTypes, contains('/fertilizer/fertilizers'));
    });

    test('should have correct fertilizer recommendation endpoint', () {
      expect(ApiConfig.fertilizerRecommendation, contains('/fertilizer/recommend'));
    });

    test('should have correct soil interpretation endpoint', () {
      expect(ApiConfig.soilInterpretation, contains('/fertilizer/soil/interpret'));
    });

    test('should have correct deficiency symptoms endpoint', () {
      expect(ApiConfig.deficiencySymptoms, contains('/fertilizer/deficiency/symptoms'));
    });
  });

  group('ApiConfig Endpoints - Irrigation Smart', () {
    test('should have correct irrigation crops endpoint', () {
      expect(ApiConfig.irrigationCrops, contains('/irrigation/crops'));
    });

    test('should have correct irrigation methods endpoint', () {
      expect(ApiConfig.irrigationMethods, contains('/irrigation/methods'));
    });

    test('should have correct irrigation calculate endpoint', () {
      expect(ApiConfig.irrigationCalculate, contains('/irrigation/calculate'));
    });

    test('should have correct water balance endpoint', () {
      expect(ApiConfig.waterBalance, contains('/irrigation/water-balance'));
    });

    test('should have correct irrigation efficiency endpoint', () {
      expect(ApiConfig.irrigationEfficiency, contains('/irrigation/efficiency'));
    });
  });

  group('ApiConfig Endpoints - Crop Health AI', () {
    test('should have correct diagnose endpoint', () {
      expect(ApiConfig.diagnose, contains('/crop-health/diagnose'));
    });

    test('should have correct batch diagnose endpoint', () {
      expect(ApiConfig.diagnoseBatch, contains('/crop-health/diagnose/batch'));
    });

    test('should have correct supported crops endpoint', () {
      expect(ApiConfig.supportedCrops, contains('/crop-health/crops'));
    });

    test('should have correct diseases endpoint', () {
      expect(ApiConfig.diseases, contains('/crop-health/diseases'));
    });

    test('should generate correct treatment details endpoint', () {
      expect(ApiConfig.treatmentDetails('rust'), contains('/crop-health/treatment/rust'));
    });

    test('should have correct expert review endpoint', () {
      expect(ApiConfig.expertReview, contains('/crop-health/expert-review'));
    });
  });

  group('ApiConfig Endpoints - Virtual Sensors', () {
    test('should have correct et0 calculate endpoint', () {
      expect(ApiConfig.et0Calculate, contains('/virtual-sensors/et0/calculate'));
    });

    test('should have correct virtual sensors crops endpoint', () {
      expect(ApiConfig.virtualSensorsCrops, contains('/virtual-sensors/crops'));
    });

    test('should generate correct crop kc endpoint', () {
      expect(ApiConfig.cropKc('wheat'), contains('/virtual-sensors/crops/wheat/kc'));
    });

    test('should have correct etc calculate endpoint', () {
      expect(ApiConfig.etcCalculate, contains('/virtual-sensors/etc/calculate'));
    });

    test('should have correct soil moisture estimate endpoint', () {
      expect(ApiConfig.soilMoistureEstimate, contains('/virtual-sensors/soil-moisture/estimate'));
    });

    test('should have correct irrigation recommend endpoint', () {
      expect(ApiConfig.irrigationRecommend, contains('/virtual-sensors/irrigation/recommend'));
    });
  });

  group('ApiConfig Endpoints - Equipment Service', () {
    test('should have correct equipment endpoint', () {
      expect(ApiConfig.equipment, contains('/api/v1/equipment'));
    });

    test('should generate correct equipment by id endpoint', () {
      expect(ApiConfig.equipmentById('eq-123'), contains('/api/v1/equipment/eq-123'));
    });

    test('should generate correct equipment by QR endpoint', () {
      expect(ApiConfig.equipmentByQr('QR001'), contains('/api/v1/equipment/qr/QR001'));
    });

    test('should have correct equipment stats endpoint', () {
      expect(ApiConfig.equipmentStats, contains('/api/v1/equipment/stats'));
    });

    test('should have correct maintenance alerts endpoint', () {
      expect(ApiConfig.maintenanceAlerts, contains('/equipment/maintenance/alerts'));
    });
  });

  group('ApiConfig Endpoints - Marketplace', () {
    test('should generate correct wallet endpoint', () {
      expect(ApiConfig.wallet('user-123'), contains('/marketplace/fintech/wallet/user-123'));
    });

    test('should have correct credit score endpoint', () {
      expect(ApiConfig.calculateCreditScore, contains('/marketplace/fintech/calculate-score'));
    });

    test('should have correct loans endpoint', () {
      expect(ApiConfig.loans, contains('/marketplace/fintech/loans'));
    });

    test('should have correct market products endpoint', () {
      expect(ApiConfig.marketProducts, contains('/marketplace/products'));
    });

    test('should have correct list harvest endpoint', () {
      expect(ApiConfig.listHarvest, contains('/marketplace/harvest'));
    });
  });

  group('ApiConfig Timeouts', () {
    test('should have correct connect timeout', () {
      expect(ApiConfig.connectTimeout, const Duration(seconds: 30));
    });

    test('should have correct send timeout', () {
      expect(ApiConfig.sendTimeout, const Duration(seconds: 15));
    });

    test('should have correct receive timeout', () {
      expect(ApiConfig.receiveTimeout, const Duration(seconds: 15));
    });

    test('should have correct long operation timeout', () {
      expect(ApiConfig.longOperationTimeout, const Duration(seconds: 60));
    });
  });

  group('ApiConfig Headers', () {
    test('should have correct default headers', () {
      final headers = ApiConfig.defaultHeaders;
      expect(headers['Content-Type'], 'application/json');
      expect(headers['Accept'], 'application/json');
      expect(headers['Accept-Language'], 'ar,en');
    });

    test('should generate correct auth headers', () {
      final headers = ApiConfig.authHeaders('test-token');
      expect(headers['Authorization'], 'Bearer test-token');
      expect(headers['Content-Type'], 'application/json');
    });

    test('should generate correct tenant headers', () {
      final headers = ApiConfig.tenantHeaders('test-token', 'tenant-123');
      expect(headers['Authorization'], 'Bearer test-token');
      expect(headers['X-Tenant-Id'], 'tenant-123');
    });

    test('should generate correct etag headers', () {
      final headers = ApiConfig.etagHeaders('test-token', 'etag-abc');
      expect(headers['Authorization'], 'Bearer test-token');
      expect(headers['If-Match'], 'etag-abc');
    });
  });

  group('ApiConfig Health Checks', () {
    test('should generate correct health check URL', () {
      expect(
        ApiConfig.healthCheck('http://localhost:8090'),
        'http://localhost:8090/healthz',
      );
    });

    test('should have all services in health checks', () {
      final healthChecks = ApiConfig.allHealthChecks;
      expect(healthChecks.containsKey('satellite'), true);
      expect(healthChecks.containsKey('weather'), true);
      expect(healthChecks.containsKey('indicators'), true);
      expect(healthChecks.containsKey('fertilizer'), true);
      expect(healthChecks.containsKey('irrigation'), true);
      expect(healthChecks.containsKey('cropHealth'), true);
      expect(healthChecks.containsKey('virtualSensors'), true);
      expect(healthChecks.containsKey('equipment'), true);
      expect(healthChecks.containsKey('notifications'), true);
      expect(healthChecks.containsKey('marketplace'), true);
    });
  });
}
