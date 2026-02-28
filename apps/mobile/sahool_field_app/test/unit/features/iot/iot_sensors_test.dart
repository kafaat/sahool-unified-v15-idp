import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:http/http.dart' as http;
import 'package:sahool_field_app/features/iot/data/remote/iot_api.dart';
import 'package:sahool_field_app/features/iot/data/remote/iot_sensors_api.dart'
    as sensors;

// ═══════════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════════

class MockHttpClient extends Mock implements http.Client {}

class FakeUri extends Fake implements Uri {}

void main() {
  setUpAll(() {
    registerFallbackValue(FakeUri());
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // IoTDevice Model Tests (iot_api.dart)
  // ═════════════════════════════════════════════════════════════════════════════

  group('IoTDevice model', () {
    test('fromJson parses all required fields', () {
      // Arrange
      final json = {
        'id': 'device-001',
        'name': 'Soil Sensor A',
        'type': 'soil_moisture',
        'field_id': 'field-001',
        'status': 'online',
        'last_seen': '2026-01-20T10:00:00Z',
        'is_online': true,
      };

      // Act
      final device = IoTDevice.fromJson(json);

      // Assert
      expect(device.id, 'device-001');
      expect(device.name, 'Soil Sensor A');
      expect(device.type, 'soil_moisture');
      expect(device.fieldId, 'field-001');
      expect(device.status, 'online');
      expect(device.isOnline, isTrue);
      expect(device.lastSeen, isNotNull);
      expect(device.lastSeen!.year, 2026);
    });

    test('fromJson parses metadata map', () {
      final json = {
        'id': 'device-001',
        'name': 'Sensor A',
        'type': 'temperature',
        'field_id': 'field-001',
        'status': 'online',
        'metadata': {'firmware_version': '2.1', 'model': 'SHT-30'},
      };

      final device = IoTDevice.fromJson(json);

      expect(device.metadata, isNotNull);
      expect(device.metadata!['firmware_version'], '2.1');
      expect(device.metadata!['model'], 'SHT-30');
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'id': 'device-002',
        'name': 'Sensor B',
        'type': 'humidity',
        'field_id': 'field-002',
        'status': 'offline',
      };

      final device = IoTDevice.fromJson(json);

      expect(device.metadata, isNull);
      expect(device.lastSeen, isNull);
      expect(device.isOnline, isFalse);
    });

    test('toJson produces correct map', () {
      final device = IoTDevice(
        id: 'device-003',
        name: 'Valve Controller',
        type: 'valve',
        fieldId: 'field-003',
        status: 'online',
        isOnline: true,
      );

      final json = device.toJson();

      expect(json['id'], 'device-003');
      expect(json['name'], 'Valve Controller');
      expect(json['type'], 'valve');
      expect(json['field_id'], 'field-003');
      expect(json['status'], 'online');
      expect(json['is_online'], isTrue);
      expect(json['metadata'], isNull);
      expect(json['last_seen'], isNull);
    });

    test('toJson roundtrip preserves data', () {
      final original = IoTDevice(
        id: 'device-004',
        name: 'pH Sensor',
        type: 'ph',
        fieldId: 'field-001',
        status: 'online',
        metadata: {'calibrated': 'true'},
        lastSeen: DateTime.utc(2026, 1, 20, 10, 0),
        isOnline: true,
      );

      final json = original.toJson();
      final restored = IoTDevice.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.name, original.name);
      expect(restored.type, original.type);
      expect(restored.fieldId, original.fieldId);
      expect(restored.isOnline, original.isOnline);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SensorReading Model Tests (iot_api.dart)
  // ═════════════════════════════════════════════════════════════════════════════

  group('SensorReading model (iot_api.dart)', () {
    test('fromJson parses all fields', () {
      final json = {
        'device_id': 'device-001',
        'sensor_type': 'soil_moisture',
        'value': 42.5,
        'unit': '%',
        'timestamp': '2026-01-20T10:30:00Z',
      };

      final reading = SensorReading.fromJson(json);

      expect(reading.deviceId, 'device-001');
      expect(reading.sensorType, 'soil_moisture');
      expect(reading.value, 42.5);
      expect(reading.unit, '%');
      expect(reading.timestamp.year, 2026);
    });

    test('fromJson handles integer value as double', () {
      final json = {
        'device_id': 'device-001',
        'sensor_type': 'temperature',
        'value': 28,
        'unit': 'C',
        'timestamp': '2026-01-20T10:30:00Z',
      };

      final reading = SensorReading.fromJson(json);

      expect(reading.value, 28.0);
      expect(reading.value, isA<double>());
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // IoTCommand Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('IoTCommand model', () {
    test('toJson includes action only when no parameters', () {
      final command = IoTCommand(action: 'turn_on');

      final json = command.toJson();

      expect(json['action'], 'turn_on');
      expect(json.containsKey('parameters'), isFalse);
    });

    test('toJson includes parameters when provided', () {
      final command = IoTCommand(
        action: 'set_value',
        parameters: {'value': 75.0, 'mode': 'auto'},
      );

      final json = command.toJson();

      expect(json['action'], 'set_value');
      expect(json['parameters'], isNotNull);
      expect(json['parameters']['value'], 75.0);
      expect(json['parameters']['mode'], 'auto');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // IoTApiException Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('IoTApiException', () {
    test('toString includes message and status code', () {
      final exception = IoTApiException('Connection failed', statusCode: 500);

      expect(exception.toString(),
          'IoTApiException: Connection failed (status: 500)');
    });

    test('handles null status code', () {
      final exception = IoTApiException('Unknown error');

      expect(exception.statusCode, isNull);
      expect(exception.message, 'Unknown error');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // IoTApi Client Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('IoTApi client', () {
    late MockHttpClient mockClient;
    late IoTApi iotApi;

    setUp(() {
      mockClient = MockHttpClient();
      iotApi = IoTApi(client: mockClient, authToken: 'test-token');
    });

    test('getDevices returns list of devices on success', () async {
      // Arrange
      final responseBody = jsonEncode({
        'data': [
          {
            'id': 'device-001',
            'name': 'Sensor A',
            'type': 'soil_moisture',
            'field_id': 'field-001',
            'status': 'online',
            'is_online': true,
          },
          {
            'id': 'device-002',
            'name': 'Sensor B',
            'type': 'temperature',
            'field_id': 'field-001',
            'status': 'offline',
            'is_online': false,
          },
        ],
      });

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final devices = await iotApi.getDevices();

      // Assert
      expect(devices.length, 2);
      expect(devices[0].id, 'device-001');
      expect(devices[0].isOnline, isTrue);
      expect(devices[1].id, 'device-002');
      expect(devices[1].isOnline, isFalse);
    });

    test('getDevices throws IoTApiException on non-200 response', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Server Error', 500));

      // Act & Assert
      expect(
        () => iotApi.getDevices(),
        throwsA(isA<IoTApiException>()),
      );
    });

    test('getDevice returns single device on success', () async {
      // Arrange
      final responseBody = jsonEncode({
        'data': {
          'id': 'device-001',
          'name': 'Soil Sensor A',
          'type': 'soil_moisture',
          'field_id': 'field-001',
          'status': 'online',
          'is_online': true,
        },
      });

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final device = await iotApi.getDevice('device-001');

      // Assert
      expect(device.id, 'device-001');
      expect(device.name, 'Soil Sensor A');
    });

    test('getSensorReadings returns list of readings', () async {
      // Arrange
      final responseBody = jsonEncode({
        'data': [
          {
            'device_id': 'device-001',
            'sensor_type': 'soil_moisture',
            'value': 42.5,
            'unit': '%',
            'timestamp': '2026-01-20T10:00:00Z',
          },
          {
            'device_id': 'device-001',
            'sensor_type': 'soil_moisture',
            'value': 43.1,
            'unit': '%',
            'timestamp': '2026-01-20T10:30:00Z',
          },
        ],
      });

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final readings = await iotApi.getSensorReadings('device-001');

      // Assert
      expect(readings.length, 2);
      expect(readings[0].value, 42.5);
      expect(readings[1].value, 43.1);
    });

    test('getLatestReading returns null when no readings', () async {
      // Arrange
      final responseBody = jsonEncode({'data': []});

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final reading = await iotApi.getLatestReading('device-001');

      // Assert
      expect(reading, isNull);
    });

    test('sendCommand returns response map on success', () async {
      // Arrange
      final responseBody = jsonEncode({
        'status': 'accepted',
        'device_id': 'device-001',
      });

      when(() => mockClient.post(
            any(),
            headers: any(named: 'headers'),
            body: any(named: 'body'),
          )).thenAnswer((_) async => http.Response(responseBody, 202));

      // Act
      final result = await iotApi.sendCommand(
        'device-001',
        IoTCommand(action: 'turn_on'),
      );

      // Assert
      expect(result['status'], 'accepted');
    });

    test('sendCommand throws on non-200/202 response', () async {
      // Arrange
      when(() => mockClient.post(
            any(),
            headers: any(named: 'headers'),
            body: any(named: 'body'),
          )).thenAnswer((_) async => http.Response('Forbidden', 403));

      // Act & Assert
      expect(
        () => iotApi.sendCommand(
          'device-001',
          IoTCommand(action: 'turn_on'),
        ),
        throwsA(isA<IoTApiException>()),
      );
    });

    test('checkHealth returns true on 200', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('ok', 200));

      // Act
      final isHealthy = await iotApi.checkHealth();

      // Assert
      expect(isHealthy, isTrue);
    });

    test('checkHealth returns false on exception', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenThrow(Exception('Connection refused'));

      // Act
      final isHealthy = await iotApi.checkHealth();

      // Assert
      expect(isHealthy, isFalse);
    });

    test('checkHealth returns false on non-200', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Service Unavailable', 503));

      // Act
      final isHealthy = await iotApi.checkHealth();

      // Assert
      expect(isHealthy, isFalse);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // IoT Sensors API Models (iot_sensors_api.dart)
  // ═════════════════════════════════════════════════════════════════════════════

  group('Sensor model (iot_sensors_api.dart)', () {
    test('fromJson parses all fields correctly', () {
      final json = {
        'id': 'sensor-001',
        'field_id': 'field-001',
        'name': 'Soil Moisture A',
        'type': 'soil_moisture',
        'status': 'online',
        'latitude': 15.3694,
        'longitude': 44.1910,
        'zone': 'zone-A',
        'last_reading': '2026-01-20T10:00:00Z',
        'battery_level': 85.5,
        'unit': '%',
      };

      final sensor = sensors.Sensor.fromJson(json);

      expect(sensor.id, 'sensor-001');
      expect(sensor.fieldId, 'field-001');
      expect(sensor.name, 'Soil Moisture A');
      expect(sensor.type, 'soil_moisture');
      expect(sensor.status, 'online');
      expect(sensor.latitude, 15.3694);
      expect(sensor.longitude, 44.1910);
      expect(sensor.zone, 'zone-A');
      expect(sensor.batteryLevel, 85.5);
      expect(sensor.unit, '%');
    });

    test('fromJson uses defaults for missing optional fields', () {
      final json = {
        'id': 'sensor-002',
        'field_id': 'field-001',
        'name': 'Temp Sensor B',
        'type': 'temperature',
        'status': 'offline',
        'last_reading': '2026-01-20T09:00:00Z',
        'unit': 'C',
      };

      final sensor = sensors.Sensor.fromJson(json);

      expect(sensor.latitude, isNull);
      expect(sensor.longitude, isNull);
      expect(sensor.zone, isNull);
      expect(sensor.batteryLevel, isNull);
    });

    test('isOnline returns true when status is "online"', () {
      final sensor = sensors.Sensor(
        id: 'sensor-001',
        fieldId: 'field-001',
        name: 'Sensor',
        type: 'soil_moisture',
        status: 'online',
        lastReading: DateTime.now(),
        unit: '%',
      );

      expect(sensor.isOnline, isTrue);
    });

    test('isOnline returns false when status is "offline"', () {
      final sensor = sensors.Sensor(
        id: 'sensor-001',
        fieldId: 'field-001',
        name: 'Sensor',
        type: 'soil_moisture',
        status: 'offline',
        lastReading: DateTime.now(),
        unit: '%',
      );

      expect(sensor.isOnline, isFalse);
    });

    test('needsBattery returns true when battery below 20%', () {
      final sensor = sensors.Sensor(
        id: 'sensor-001',
        fieldId: 'field-001',
        name: 'Sensor',
        type: 'soil_moisture',
        status: 'online',
        lastReading: DateTime.now(),
        batteryLevel: 15.0,
        unit: '%',
      );

      expect(sensor.needsBattery, isTrue);
    });

    test('needsBattery returns false when battery is null (defaults to 100)',
        () {
      final sensor = sensors.Sensor(
        id: 'sensor-001',
        fieldId: 'field-001',
        name: 'Sensor',
        type: 'soil_moisture',
        status: 'online',
        lastReading: DateTime.now(),
        unit: '%',
      );

      expect(sensor.needsBattery, isFalse);
    });

    test('typeAr returns Arabic label for known types', () {
      final sensorTypes = {
        'soil_moisture': 'رطوبة التربة',
        'temperature': 'درجة الحرارة',
        'humidity': 'الرطوبة الجوية',
        'ph': 'حموضة التربة',
        'ec': 'الموصلية الكهربائية',
        'light': 'شدة الإضاءة',
        'wind': 'سرعة الرياح',
        'rain': 'هطول الأمطار',
      };

      for (final entry in sensorTypes.entries) {
        final sensor = sensors.Sensor(
          id: 'sensor-001',
          fieldId: 'field-001',
          name: 'Sensor',
          type: entry.key,
          status: 'online',
          lastReading: DateTime.now(),
          unit: '',
        );
        expect(sensor.typeAr, entry.value,
            reason: 'Type "${entry.key}" should be "${entry.value}"');
      }
    });

    test('typeAr returns raw type for unknown types', () {
      final sensor = sensors.Sensor(
        id: 'sensor-001',
        fieldId: 'field-001',
        name: 'Sensor',
        type: 'custom_unknown',
        status: 'online',
        lastReading: DateTime.now(),
        unit: '',
      );

      expect(sensor.typeAr, 'custom_unknown');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SensorReading Model Tests (iot_sensors_api.dart)
  // ═════════════════════════════════════════════════════════════════════════════

  group('SensorReading model (iot_sensors_api.dart)', () {
    test('fromJson parses all fields', () {
      final json = {
        'sensor_id': 'sensor-001',
        'value': 42.5,
        'unit': '%',
        'timestamp': '2026-01-20T10:30:00Z',
        'quality': 'good',
      };

      final reading = sensors.SensorReading.fromJson(json);

      expect(reading.sensorId, 'sensor-001');
      expect(reading.value, 42.5);
      expect(reading.unit, '%');
      expect(reading.quality, 'good');
    });

    test('fromJson handles missing optional quality field', () {
      final json = {
        'sensor_id': 'sensor-001',
        'value': 28.0,
        'unit': 'C',
        'timestamp': '2026-01-20T10:30:00Z',
      };

      final reading = sensors.SensorReading.fromJson(json);

      expect(reading.quality, isNull);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // Actuator Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('Actuator model', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 'actuator-001',
        'field_id': 'field-001',
        'name': 'Main Pump',
        'type': 'pump',
        'is_on': true,
        'last_operation': '2026-01-20T08:00:00Z',
        'status': 'online',
      };

      final actuator = sensors.Actuator.fromJson(json);

      expect(actuator.id, 'actuator-001');
      expect(actuator.fieldId, 'field-001');
      expect(actuator.name, 'Main Pump');
      expect(actuator.type, 'pump');
      expect(actuator.isOn, isTrue);
      expect(actuator.lastOperation, isNotNull);
      expect(actuator.status, 'online');
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'id': 'actuator-002',
        'field_id': 'field-002',
        'name': 'Valve B',
        'type': 'valve',
      };

      final actuator = sensors.Actuator.fromJson(json);

      expect(actuator.isOn, isFalse);
      expect(actuator.lastOperation, isNull);
      expect(actuator.status, 'offline');
    });

    test('typeAr returns Arabic labels for known types', () {
      final types = {
        'pump': 'مضخة',
        'valve': 'صمام',
        'sprinkler': 'رشاش',
        'unknown_type': 'unknown_type',
      };

      for (final entry in types.entries) {
        final actuator = sensors.Actuator(
          id: 'a-001',
          fieldId: 'f-001',
          name: 'Test',
          type: entry.key,
          isOn: false,
          status: 'online',
        );
        expect(actuator.typeAr, entry.value);
      }
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // IoTAlert Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('IoTAlert model', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 'alert-001',
        'sensor_id': 'sensor-001',
        'type': 'threshold_exceeded',
        'severity': 'critical',
        'message': 'Soil moisture below threshold',
        'triggered_at': '2026-01-20T10:00:00Z',
        'acknowledged': false,
        'value': 15.0,
        'threshold': 20.0,
      };

      final alert = sensors.IoTAlert.fromJson(json);

      expect(alert.id, 'alert-001');
      expect(alert.sensorId, 'sensor-001');
      expect(alert.type, 'threshold_exceeded');
      expect(alert.severity, 'critical');
      expect(alert.acknowledged, isFalse);
      expect(alert.value, 15.0);
      expect(alert.threshold, 20.0);
    });

    test('fromJson handles missing optional value/threshold', () {
      final json = {
        'id': 'alert-002',
        'sensor_id': 'sensor-001',
        'type': 'device_offline',
        'severity': 'warning',
        'message': 'Device went offline',
        'triggered_at': '2026-01-20T10:00:00Z',
        'acknowledged': false,
      };

      final alert = sensors.IoTAlert.fromJson(json);

      expect(alert.value, isNull);
      expect(alert.threshold, isNull);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // IoTDashboard Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('IoTDashboard model', () {
    test('fromJson parses all fields', () {
      final json = {
        'field_id': 'field-001',
        'total_sensors': 10,
        'online_sensors': 8,
        'total_actuators': 4,
        'active_actuators': 2,
        'active_alerts': 3,
        'current_readings': {
          'soil_moisture': 42.5,
          'temperature': 28.0,
        },
        'last_update': '2026-01-20T10:00:00Z',
      };

      final dashboard = sensors.IoTDashboard.fromJson(json);

      expect(dashboard.fieldId, 'field-001');
      expect(dashboard.totalSensors, 10);
      expect(dashboard.onlineSensors, 8);
      expect(dashboard.totalActuators, 4);
      expect(dashboard.activeActuators, 2);
      expect(dashboard.activeAlerts, 3);
      expect(dashboard.currentReadings['soil_moisture'], 42.5);
    });

    test('sensorHealthPercent calculates correctly', () {
      final dashboard = sensors.IoTDashboard(
        fieldId: 'field-001',
        totalSensors: 10,
        onlineSensors: 8,
        totalActuators: 0,
        activeActuators: 0,
        activeAlerts: 0,
        currentReadings: {},
        lastUpdate: DateTime.now(),
      );

      expect(dashboard.sensorHealthPercent, 80.0);
    });

    test('sensorHealthPercent returns 0 when no sensors', () {
      final dashboard = sensors.IoTDashboard(
        fieldId: 'field-001',
        totalSensors: 0,
        onlineSensors: 0,
        totalActuators: 0,
        activeActuators: 0,
        activeAlerts: 0,
        currentReadings: {},
        lastUpdate: DateTime.now(),
      );

      expect(dashboard.sensorHealthPercent, 0.0);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SensorStatistics Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('SensorStatistics model', () {
    test('fromJson parses all fields', () {
      final json = {
        'sensor_id': 'sensor-001',
        'period': 'day',
        'min': 20.0,
        'max': 50.0,
        'average': 35.5,
        'current': 42.0,
        'trend': 'rising',
        'readings_count': 144,
      };

      final stats = sensors.SensorStatistics.fromJson(json);

      expect(stats.sensorId, 'sensor-001');
      expect(stats.period, 'day');
      expect(stats.min, 20.0);
      expect(stats.max, 50.0);
      expect(stats.average, 35.5);
      expect(stats.current, 42.0);
      expect(stats.trend, 'rising');
      expect(stats.readingsCount, 144);
    });

    test('fromJson uses defaults for missing fields', () {
      final json = <String, dynamic>{};

      final stats = sensors.SensorStatistics.fromJson(json);

      expect(stats.sensorId, '');
      expect(stats.period, 'day');
      expect(stats.min, 0.0);
      expect(stats.max, 0.0);
      expect(stats.average, 0.0);
      expect(stats.current, 0.0);
      expect(stats.trend, 'stable');
      expect(stats.readingsCount, 0);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // DeviceHealth Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('DeviceHealth model', () {
    test('fromJson parses all fields', () {
      final json = {
        'device_id': 'device-001',
        'device_type': 'sensor',
        'status': 'healthy',
        'signal_strength': 95.0,
        'battery_level': 82.0,
        'last_seen': '2026-01-20T10:00:00Z',
        'issues': ['firmware_outdated'],
      };

      final health = sensors.DeviceHealth.fromJson(json);

      expect(health.deviceId, 'device-001');
      expect(health.deviceType, 'sensor');
      expect(health.status, 'healthy');
      expect(health.signalStrength, 95.0);
      expect(health.batteryLevel, 82.0);
      expect(health.issues.length, 1);
      expect(health.issues[0], 'firmware_outdated');
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'device_id': 'device-002',
        'device_type': 'actuator',
        'last_seen': '2026-01-20T10:00:00Z',
      };

      final health = sensors.DeviceHealth.fromJson(json);

      expect(health.signalStrength, isNull);
      expect(health.batteryLevel, isNull);
      expect(health.status, 'unknown');
      expect(health.issues, isEmpty);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // IoTSensorsApi Endpoint Construction Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('IoTSensorsApi endpoint construction', () {
    test('getWebSocketUrl returns correct URL', () {
      final api = sensors.IoTSensorsApi(
        wsUrl: 'ws://localhost:8081/iot',
      );

      expect(
        api.getWebSocketUrl('field-001'),
        'ws://localhost:8081/iot/fields/field-001',
      );
    });

    test('getWebSocketUrl with custom base URL', () {
      final api = sensors.IoTSensorsApi(
        wsUrl: 'wss://sahool.app/ws/iot',
      );

      expect(
        api.getWebSocketUrl('field-abc'),
        'wss://sahool.app/ws/iot/fields/field-abc',
      );
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // ApiResult (iot_sensors_api.dart local) Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('ApiResult (iot_sensors_api.dart)', () {
    test('success factory creates successful result', () {
      final result = sensors.ApiResult.success('hello');

      expect(result.isSuccess, isTrue);
      expect(result.data, 'hello');
      expect(result.error, isNull);
    });

    test('failure factory creates failed result', () {
      final result = sensors.ApiResult<String>.failure('something went wrong');

      expect(result.isSuccess, isFalse);
      expect(result.data, isNull);
      expect(result.error, 'something went wrong');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // ScheduledOperation Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('ScheduledOperation model', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 'op-001',
        'actuator_id': 'actuator-001',
        'start_time': '2026-01-21T06:00:00Z',
        'duration_minutes': 30,
        'repeat_pattern': 'daily',
        'status': 'scheduled',
      };

      final operation = sensors.ScheduledOperation.fromJson(json);

      expect(operation.id, 'op-001');
      expect(operation.actuatorId, 'actuator-001');
      expect(operation.startTime.day, 21);
      expect(operation.durationMinutes, 30);
      expect(operation.repeatPattern, 'daily');
      expect(operation.status, 'scheduled');
    });

    test('fromJson handles missing optional repeat pattern', () {
      final json = {
        'id': 'op-002',
        'actuator_id': 'actuator-002',
        'start_time': '2026-01-21T06:00:00Z',
        'duration_minutes': 45,
      };

      final operation = sensors.ScheduledOperation.fromJson(json);

      expect(operation.repeatPattern, isNull);
      expect(operation.status, 'scheduled');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // ActuatorOperation Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('ActuatorOperation model', () {
    test('fromJson parses all fields', () {
      final json = {
        'id': 'history-001',
        'actuator_id': 'actuator-001',
        'action': 'on',
        'timestamp': '2026-01-20T06:00:00Z',
        'duration_minutes': 30,
        'triggered_by': 'schedule',
      };

      final operation = sensors.ActuatorOperation.fromJson(json);

      expect(operation.id, 'history-001');
      expect(operation.actuatorId, 'actuator-001');
      expect(operation.action, 'on');
      expect(operation.durationMinutes, 30);
      expect(operation.triggeredBy, 'schedule');
    });

    test('fromJson uses defaults for missing fields', () {
      final json = {
        'id': 'history-002',
        'actuator_id': 'actuator-002',
        'timestamp': '2026-01-20T06:00:00Z',
      };

      final operation = sensors.ActuatorOperation.fromJson(json);

      expect(operation.action, 'off');
      expect(operation.durationMinutes, isNull);
      expect(operation.triggeredBy, 'manual');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // AlertThreshold Model Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('AlertThreshold model', () {
    test('fromJson parses all fields', () {
      final json = {
        'sensor_id': 'sensor-001',
        'metric': 'soil_moisture',
        'min_value': 20.0,
        'max_value': 80.0,
      };

      final threshold = sensors.AlertThreshold.fromJson(json);

      expect(threshold.sensorId, 'sensor-001');
      expect(threshold.metric, 'soil_moisture');
      expect(threshold.minValue, 20.0);
      expect(threshold.maxValue, 80.0);
    });

    test('fromJson handles missing optional min/max values', () {
      final json = {
        'sensor_id': 'sensor-002',
        'metric': 'temperature',
      };

      final threshold = sensors.AlertThreshold.fromJson(json);

      expect(threshold.minValue, isNull);
      expect(threshold.maxValue, isNull);
    });
  });
}
