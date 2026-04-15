/// SAHOOL Field App - Equipment & IoT Integration Tests
/// اختبارات تكامل المعدات وإنترنت الأشياء
///
/// Tests the MockServer with equipment and IoT-related endpoints:
/// - Equipment CRUD (list, create, update, delete)
/// - Equipment status tracking and telemetry
/// - Maintenance scheduling and history
/// - Fuel logging and consumption
/// - IoT device management
/// - Sensor readings
/// - Device control commands
/// - Offline equipment data caching via outbox
library;
import 'dart:convert';

import 'package:drift/drift.dart' show Value;
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/storage/database.dart';

import '../../../integration_test/helpers/mock_server.dart';
import '../mocks/mock_app_database.dart';

void main() {
  // ===========================================================================
  // Equipment API Integration
  // تكامل واجهة المعدات
  // ===========================================================================

  group('Equipment API Integration - تكامل واجهة المعدات', () {
    late MockHttpClient client;

    setUp(() {
      setupMockServer();
      client = MockHttpClient();

      // Stub equipment endpoints (not in default MockServer handlers)
      MockServer.instance.stub('/api/v1/equipment', (request) {
        if (request.method == 'GET' && !request.path.contains('/equipment/')) {
          return MockResponse.success({
            'data': [
              {
                'id': 'equip-001',
                'name': 'جرار المزرعة',
                'nameEn': 'Farm Tractor',
                'type': 'tractor',
                'status': 'active',
                'model': 'John Deere 5075E',
                'serialNumber': 'JD-2024-001',
                'purchaseDate': '2024-01-15',
                'location': {'lat': 15.37, 'lng': 44.19},
                'fuelType': 'diesel',
                'hoursUsed': 1250.5,
              },
              {
                'id': 'equip-002',
                'name': 'نظام ري بالتنقيط',
                'nameEn': 'Drip Irrigation System',
                'type': 'irrigation_system',
                'status': 'active',
                'model': 'Netafim UniRam',
                'serialNumber': 'NF-2023-045',
                'purchaseDate': '2023-06-01',
              },
              {
                'id': 'equip-003',
                'name': 'رشاش مبيدات',
                'nameEn': 'Pesticide Sprayer',
                'type': 'sprayer',
                'status': 'maintenance',
                'model': 'Solo 425',
                'serialNumber': 'SL-2024-012',
              },
            ],
            'total': 3,
            'page': 1,
          });
        }
        if (request.method == 'POST') {
          return MockResponse.created({
            'data': {
              'id': 'equip-new-${DateTime.now().millisecondsSinceEpoch}',
              ...?request.body,
              'status': 'active',
              'createdAt': DateTime.now().toIso8601String(),
            },
            'message': 'تم إضافة المعدة بنجاح',
          });
        }
        return MockResponse.notFound;
      });

      // Equipment by ID
      MockServer.instance.stub('/api/v1/equipment/equip-001', (request) {
        if (request.method == 'GET') {
          return MockResponse.success({
            'data': {
              'id': 'equip-001',
              'name': 'جرار المزرعة',
              'type': 'tractor',
              'status': 'active',
              'hoursUsed': 1250.5,
              'maintenanceHistory': [],
              'fuelLogs': [],
            },
          });
        }
        if (request.method == 'PUT' || request.method == 'PATCH') {
          return MockResponse.success({
            'data': {'id': 'equip-001', ...?request.body},
            'message': 'تم تحديث المعدة بنجاح',
          });
        }
        if (request.method == 'DELETE') {
          return MockResponse.success({'message': 'تم حذف المعدة بنجاح'});
        }
        return MockResponse.notFound;
      });

      // Maintenance endpoint
      MockServer.instance.stub('/api/v1/equipment/equip-001/maintenance',
          (request) {
        if (request.method == 'GET') {
          return MockResponse.success({
            'data': [
              {
                'id': 'maint-001',
                'equipmentId': 'equip-001',
                'type': 'oil_change',
                'description': 'تغيير زيت المحرك',
                'cost': 250.0,
                'currency': 'SAR',
                'performedAt': '2025-12-01T08:00:00Z',
                'nextDueAt': '2026-03-01T08:00:00Z',
                'performedBy': 'الفني أحمد',
              },
            ],
            'total': 1,
          });
        }
        if (request.method == 'POST') {
          return MockResponse.created({
            'data': {
              'id': 'maint-new-${DateTime.now().millisecondsSinceEpoch}',
              ...?request.body,
              'createdAt': DateTime.now().toIso8601String(),
            },
            'message': 'تم تسجيل الصيانة بنجاح',
          });
        }
        return MockResponse.notFound;
      });

      // Fuel log endpoint
      MockServer.instance.stub('/api/v1/equipment/equip-001/fuel', (request) {
        if (request.method == 'GET') {
          return MockResponse.success({
            'data': [
              {
                'id': 'fuel-001',
                'equipmentId': 'equip-001',
                'fuelType': 'diesel',
                'quantity': 50.0,
                'unit': 'liters',
                'cost': 175.0,
                'odometer': 1250.5,
                'loggedAt': '2026-03-10T06:30:00Z',
              },
            ],
            'summary': {
              'totalLiters': 350.0,
              'totalCost': 1225.0,
              'avgConsumption': 8.5,
            },
          });
        }
        if (request.method == 'POST') {
          return MockResponse.created({
            'data': {
              'id': 'fuel-new-${DateTime.now().millisecondsSinceEpoch}',
              ...?request.body,
            },
            'message': 'تم تسجيل التزود بالوقود',
          });
        }
        return MockResponse.notFound;
      });
    });

    tearDown(() {
      resetMockServer();
    });

    test('GET /equipment returns list of equipment', () async {
      final response = await client.get('/api/v1/equipment');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['data'].length, equals(3));
      expect(response.body['total'], equals(3));

      final tractor = response.body['data'][0];
      expect(tractor['name'], equals('جرار المزرعة'));
      expect(tractor['type'], equals('tractor'));
      expect(tractor['status'], equals('active'));
    });

    test('GET /equipment/:id returns equipment details', () async {
      final response = await client.get('/api/v1/equipment/equip-001');

      expect(response.statusCode, equals(200));
      expect(response.body['data']['id'], equals('equip-001'));
      expect(response.body['data']['hoursUsed'], equals(1250.5));
    });

    test('POST /equipment creates new equipment', () async {
      final response = await client.post(
        '/api/v1/equipment',
        body: {
          'name': 'حصادة جديدة',
          'type': 'harvester',
          'model': 'CLAAS Lexion 770',
        },
      );

      expect(response.statusCode, equals(201));
      expect(response.body['data']['id'], startsWith('equip-new-'));
      expect(response.body['data']['name'], equals('حصادة جديدة'));
      expect(response.body['data']['status'], equals('active'));
    });

    test('PUT /equipment/:id updates equipment', () async {
      final response = await client.put(
        '/api/v1/equipment/equip-001',
        body: {'status': 'maintenance', 'hoursUsed': 1300.0},
      );

      expect(response.statusCode, equals(200));
      expect(response.body['message'], contains('بنجاح'));
    });

    test('DELETE /equipment/:id removes equipment', () async {
      final response = await client.delete('/api/v1/equipment/equip-001');

      expect(response.statusCode, equals(200));
      expect(response.body['message'], contains('حذف'));
    });

    test('GET /equipment/:id/maintenance returns history', () async {
      final response =
          await client.get('/api/v1/equipment/equip-001/maintenance');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['data'].length, equals(1));

      final record = response.body['data'][0];
      expect(record['type'], equals('oil_change'));
      expect(record['cost'], equals(250.0));
    });

    test('POST /equipment/:id/maintenance logs maintenance', () async {
      final response = await client.post(
        '/api/v1/equipment/equip-001/maintenance',
        body: {
          'type': 'filter_change',
          'description': 'تغيير فلتر الهواء',
          'cost': 80.0,
          'currency': 'SAR',
        },
      );

      expect(response.statusCode, equals(201));
      expect(response.body['data']['type'], equals('filter_change'));
    });

    test('GET /equipment/:id/fuel returns fuel logs with summary', () async {
      final response = await client.get('/api/v1/equipment/equip-001/fuel');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['summary']['totalLiters'], equals(350.0));
      expect(response.body['summary']['avgConsumption'], equals(8.5));
    });

    test('POST /equipment/:id/fuel logs fuel entry', () async {
      final response = await client.post(
        '/api/v1/equipment/equip-001/fuel',
        body: {
          'fuelType': 'diesel',
          'quantity': 45.0,
          'unit': 'liters',
          'cost': 157.5,
        },
      );

      expect(response.statusCode, equals(201));
      expect(response.body['message'], contains('التزود'));
    });
  });

  // ===========================================================================
  // IoT Device API Integration
  // تكامل واجهة أجهزة إنترنت الأشياء
  // ===========================================================================

  group('IoT Device API Integration - تكامل واجهة أجهزة IoT', () {
    late MockHttpClient client;

    setUp(() {
      setupMockServer();
      client = MockHttpClient();

      // Stub IoT endpoints
      MockServer.instance.stub('/api/v1/iot/devices', (request) {
        if (request.method == 'GET') {
          return MockResponse.success({
            'data': [
              {
                'id': 'iot-001',
                'name': 'مستشعر رطوبة التربة - الحقل الشمالي',
                'nameEn': 'Soil Moisture Sensor - North Field',
                'type': 'soil_moisture',
                'status': 'online',
                'fieldId': 'field-test-001',
                'battery': 85,
                'lastReading': {
                  'value': 42.5,
                  'unit': '%',
                  'timestamp': '2026-03-14T06:00:00Z',
                },
                'firmware': '2.1.3',
              },
              {
                'id': 'iot-002',
                'name': 'محطة طقس',
                'nameEn': 'Weather Station',
                'type': 'weather_station',
                'status': 'online',
                'fieldId': 'field-test-001',
                'battery': 95,
                'lastReading': {
                  'temperature': 28.5,
                  'humidity': 45,
                  'windSpeed': 12.3,
                  'timestamp': '2026-03-14T06:15:00Z',
                },
              },
              {
                'id': 'iot-003',
                'name': 'صمام ري ذكي',
                'nameEn': 'Smart Irrigation Valve',
                'type': 'valve',
                'status': 'offline',
                'fieldId': 'field-test-002',
                'battery': 15,
                'lastReading': null,
              },
            ],
            'total': 3,
          });
        }
        return MockResponse.notFound;
      });

      // Single device
      MockServer.instance.stub('/api/v1/iot/devices/iot-001', (request) {
        if (request.method == 'GET') {
          return MockResponse.success({
            'data': {
              'id': 'iot-001',
              'name': 'مستشعر رطوبة التربة',
              'type': 'soil_moisture',
              'status': 'online',
              'calibration': {'offset': 0.5, 'factor': 1.02},
            },
          });
        }
        return MockResponse.notFound;
      });

      // Sensor readings
      MockServer.instance.stub('/api/v1/iot/devices/iot-001/readings',
          (request) {
        return MockResponse.success({
          'data': List.generate(24, (i) {
            return {
              'value': 35.0 + (i % 10) * 1.5,
              'unit': '%',
              'timestamp':
                  DateTime.now().subtract(Duration(hours: 23 - i)).toIso8601String(),
            };
          }),
          'deviceId': 'iot-001',
          'period': '24h',
        });
      });

      // Device commands
      MockServer.instance.stub('/api/v1/iot/devices/iot-003/command',
          (request) {
        if (request.method == 'POST') {
          final command = request.body?['command'] ?? 'unknown';
          return MockResponse.success({
            'data': {
              'commandId': 'cmd-${DateTime.now().millisecondsSinceEpoch}',
              'deviceId': 'iot-003',
              'command': command,
              'status': 'sent',
              'sentAt': DateTime.now().toIso8601String(),
            },
            'message': 'تم إرسال الأمر بنجاح',
          });
        }
        return MockResponse.notFound;
      });

      // Device types
      MockServer.instance.stub('/api/v1/iot/device-types', (request) {
        return MockResponse.success({
          'data': [
            {
              'type': 'soil_moisture',
              'nameAr': 'مستشعر رطوبة التربة',
              'nameEn': 'Soil Moisture Sensor',
              'metrics': ['moisture_percent'],
            },
            {
              'type': 'weather_station',
              'nameAr': 'محطة طقس',
              'nameEn': 'Weather Station',
              'metrics': [
                'temperature',
                'humidity',
                'wind_speed',
                'pressure',
              ],
            },
            {
              'type': 'valve',
              'nameAr': 'صمام ري',
              'nameEn': 'Irrigation Valve',
              'metrics': ['flow_rate', 'is_open'],
            },
          ],
        });
      });
    });

    tearDown(() {
      resetMockServer();
    });

    test('GET /iot/devices returns device list', () async {
      final response = await client.get('/api/v1/iot/devices');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['data'].length, equals(3));
      expect(response.body['total'], equals(3));
    });

    test('device list includes online/offline status', () async {
      final response = await client.get('/api/v1/iot/devices');
      final devices = response.body['data'] as List;

      final onlineDevices = devices.where((d) => d['status'] == 'online');
      final offlineDevices = devices.where((d) => d['status'] == 'offline');

      expect(onlineDevices.length, equals(2));
      expect(offlineDevices.length, equals(1));
    });

    test('device list includes battery levels', () async {
      final response = await client.get('/api/v1/iot/devices');
      final devices = response.body['data'] as List;

      final lowBattery = devices.where((d) => (d['battery'] as int) < 20);
      expect(lowBattery.length, equals(1));
      expect(lowBattery.first['id'], equals('iot-003'));
    });

    test('GET /iot/devices/:id returns device details', () async {
      final response = await client.get('/api/v1/iot/devices/iot-001');

      expect(response.statusCode, equals(200));
      expect(response.body['data']['id'], equals('iot-001'));
      expect(response.body['data']['calibration'], isNotNull);
    });

    test('GET /iot/devices/:id/readings returns sensor data', () async {
      final response =
          await client.get('/api/v1/iot/devices/iot-001/readings');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['data'].length, equals(24));
      expect(response.body['period'], equals('24h'));

      final firstReading = response.body['data'][0];
      expect(firstReading['value'], isA<num>());
      expect(firstReading['unit'], equals('%'));
      expect(firstReading['timestamp'], isNotNull);
    });

    test('POST /iot/devices/:id/command sends control command', () async {
      final response = await client.post(
        '/api/v1/iot/devices/iot-003/command',
        body: {'command': 'open', 'duration': 30},
      );

      expect(response.statusCode, equals(200));
      expect(response.body['data']['command'], equals('open'));
      expect(response.body['data']['status'], equals('sent'));
      expect(response.body['data']['deviceId'], equals('iot-003'));
      expect(response.body['message'], contains('بنجاح'));
    });

    test('GET /iot/device-types returns supported types', () async {
      final response = await client.get('/api/v1/iot/device-types');

      expect(response.statusCode, equals(200));
      expect(response.body['data'], isList);
      expect(response.body['data'].length, equals(3));

      final types =
          (response.body['data'] as List).map((d) => d['type']).toList();
      expect(types, containsAll(['soil_moisture', 'weather_station', 'valve']));
    });
  });

  // ===========================================================================
  // Equipment Offline Outbox Integration
  // تكامل صندوق الصادر للمعدات بدون اتصال
  // ===========================================================================

  group('Equipment Offline Outbox - صندوق صادر المعدات', () {
    late MockAppDatabase db;

    setUp(() {
      db = MockAppDatabase();
    });

    tearDown(() {
      db.clearAll();
      db.dispose();
    });

    test('equipment creation queued offline', () async {
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'equipment',
        entityId: 'equip-offline-001',
        apiEndpoint: '/api/v1/equipment',
        method: 'POST',
        payload: jsonEncode({
          'name': 'معدة جديدة بدون اتصال',
          'type': 'tractor',
          'model': 'Case IH',
        }),
      );

      final pending = await db.getPendingOutbox();
      expect(pending.length, equals(1));
      expect(pending.first.entityType, equals('equipment'));
      expect(pending.first.method, equals('POST'));

      final payload = jsonDecode(pending.first.payload) as Map<String, dynamic>;
      expect(payload['name'], equals('معدة جديدة بدون اتصال'));
    });

    test('maintenance record queued offline with ETag', () async {
      const etag = '"v2-equip-001"';
      final item = OutboxCompanion.insert(
        tenantId: 'tenant-001',
        entityType: 'maintenance',
        entityId: 'maint-offline-001',
        apiEndpoint: '/api/v1/equipment/equip-001/maintenance',
        method: const Value('POST'),
        payload: jsonEncode({
          'type': 'tire_change',
          'description': 'تغيير الإطارات',
          'cost': 1200.0,
          'currency': 'SAR',
        }),
        ifMatch: const Value(etag),
      );

      await db.addToOutbox(item);

      final pending = await db.getPendingOutbox();
      expect(pending.first.ifMatch, equals(etag));
      expect(pending.first.entityType, equals('maintenance'));
    });

    test('fuel log queued offline', () async {
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'fuel_log',
        entityId: 'fuel-offline-001',
        apiEndpoint: '/api/v1/equipment/equip-001/fuel',
        method: 'POST',
        payload: jsonEncode({
          'fuelType': 'diesel',
          'quantity': 60.0,
          'cost': 210.0,
          'odometer': 1350.0,
        }),
      );

      final pending = await db.getPendingOutbox();
      expect(pending.length, equals(1));
      expect(pending.first.entityType, equals('fuel_log'));
    });

    test('multiple equipment changes queued and processed in order', () async {
      // Queue create, then update, then maintenance
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'equipment',
        entityId: 'equip-001',
        apiEndpoint: '/api/v1/equipment',
        method: 'POST',
        payload: jsonEncode({'name': 'New Equipment'}),
      );

      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'equipment',
        entityId: 'equip-001',
        apiEndpoint: '/api/v1/equipment/equip-001',
        method: 'PUT',
        payload: jsonEncode({'status': 'maintenance'}),
      );

      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'maintenance',
        entityId: 'maint-001',
        apiEndpoint: '/api/v1/equipment/equip-001/maintenance',
        method: 'POST',
        payload: jsonEncode({'type': 'oil_change'}),
      );

      final pending = await db.getPendingOutbox();
      expect(pending.length, equals(3));

      // Process in order
      await db.markOutboxDone(pending[0].id);
      await db.markOutboxDone(pending[1].id);
      await db.markOutboxDone(pending[2].id);

      final remaining = await db.getPendingOutbox();
      expect(remaining.isEmpty, isTrue);
    });

    test('IoT command queued offline for later execution', () async {
      await db.queueOutboxItem(
        tenantId: 'tenant-001',
        entityType: 'iot_command',
        entityId: 'cmd-offline-001',
        apiEndpoint: '/api/v1/iot/devices/iot-003/command',
        method: 'POST',
        payload: jsonEncode({
          'command': 'open',
          'duration': 30,
          'scheduledAt': DateTime.now().add(const Duration(hours: 1)).toIso8601String(),
        }),
      );

      final pending = await db.getPendingOutbox();
      expect(pending.length, equals(1));
      expect(pending.first.entityType, equals('iot_command'));

      final payload = jsonDecode(pending.first.payload) as Map<String, dynamic>;
      expect(payload['command'], equals('open'));
      expect(payload['duration'], equals(30));
    });
  });
}
