/// Unit Tests for IoT Feature - API Client and Models
/// اختبارات وحدات ميزة إنترنت الأشياء
import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:http/http.dart' as http;
import 'package:sahool_mobile_core/features/iot/data/remote/iot_api.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════

class MockHttpClient extends Mock implements http.Client {}

class FakeUri extends Fake implements Uri {}

void main() {
  setUpAll(() {
    registerFallbackValue(FakeUri());
    registerFallbackValue(<String, String>{});
    registerFallbackValue(''); // Fallback for http body (String) parameters
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IoTDevice Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('IoTDevice', () {
    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'id': 'DEVICE-001',
        'name': 'Soil Moisture Sensor A',
        'type': 'soil_moisture',
        'field_id': 'FIELD-001',
        'status': 'active',
        'metadata': {'firmware': '2.1.0', 'battery': 85},
        'last_seen': '2025-06-15T10:30:00Z',
        'is_online': true,
      };

      // Act
      final device = IoTDevice.fromJson(json);

      // Assert
      expect(device.id, 'DEVICE-001');
      expect(device.name, 'Soil Moisture Sensor A');
      expect(device.type, 'soil_moisture');
      expect(device.fieldId, 'FIELD-001');
      expect(device.status, 'active');
      expect(device.metadata, isNotNull);
      expect(device.metadata!['firmware'], '2.1.0');
      expect(device.lastSeen, DateTime.utc(2025, 6, 15, 10, 30, 0));
      expect(device.isOnline, true);
    });

    test('fromJson handles null optional fields', () {
      // Arrange
      final json = {
        'id': 'DEVICE-002',
        'name': 'Temperature Sensor',
        'type': 'temperature',
        'field_id': 'FIELD-002',
        'status': 'inactive',
      };

      // Act
      final device = IoTDevice.fromJson(json);

      // Assert
      expect(device.metadata, isNull);
      expect(device.lastSeen, isNull);
      expect(device.isOnline, false);
    });

    test('toJson produces correct map', () {
      // Arrange
      final now = DateTime.utc(2025, 6, 15, 10, 0, 0);
      final device = IoTDevice(
        id: 'DEVICE-003',
        name: 'Humidity Sensor',
        type: 'humidity',
        fieldId: 'FIELD-001',
        status: 'active',
        metadata: {'battery': 92},
        lastSeen: now,
        isOnline: true,
      );

      // Act
      final json = device.toJson();

      // Assert
      expect(json['id'], 'DEVICE-003');
      expect(json['name'], 'Humidity Sensor');
      expect(json['type'], 'humidity');
      expect(json['field_id'], 'FIELD-001');
      expect(json['status'], 'active');
      expect(json['metadata'], {'battery': 92});
      expect(json['last_seen'], now.toIso8601String());
      expect(json['is_online'], true);
    });

    test('fromJson/toJson round-trip preserves data', () {
      // Arrange
      final original = IoTDevice(
        id: 'DEVICE-RT',
        name: 'Roundtrip Sensor',
        type: 'wind',
        fieldId: 'FIELD-003',
        status: 'active',
        isOnline: true,
        lastSeen: DateTime.utc(2025, 1, 1),
      );

      // Act
      final restored = IoTDevice.fromJson(original.toJson());

      // Assert
      expect(restored.id, original.id);
      expect(restored.name, original.name);
      expect(restored.type, original.type);
      expect(restored.fieldId, original.fieldId);
      expect(restored.isOnline, original.isOnline);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SensorReading Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SensorReading', () {
    test('fromJson parses all fields correctly', () {
      // Arrange
      final json = {
        'device_id': 'DEVICE-001',
        'sensor_type': 'soil_moisture',
        'value': 45.3,
        'unit': '%',
        'timestamp': '2025-06-15T10:30:00Z',
      };

      // Act
      final reading = SensorReading.fromJson(json);

      // Assert
      expect(reading.deviceId, 'DEVICE-001');
      expect(reading.sensorType, 'soil_moisture');
      expect(reading.value, 45.3);
      expect(reading.unit, '%');
      expect(reading.timestamp, DateTime.utc(2025, 6, 15, 10, 30, 0));
    });

    test('fromJson handles integer value as double', () {
      // Arrange
      final json = {
        'device_id': 'DEVICE-002',
        'sensor_type': 'temperature',
        'value': 28, // Integer, not double
        'unit': 'C',
        'timestamp': '2025-06-15T12:00:00Z',
      };

      // Act
      final reading = SensorReading.fromJson(json);

      // Assert
      expect(reading.value, 28.0);
      expect(reading.value, isA<double>());
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IoTCommand Model Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('IoTCommand', () {
    test('toJson with action only', () {
      // Arrange
      final command = IoTCommand(action: 'turn_on');

      // Act
      final json = command.toJson();

      // Assert
      expect(json['action'], 'turn_on');
      expect(json.containsKey('parameters'), false);
    });

    test('toJson with action and parameters', () {
      // Arrange
      final command = IoTCommand(
        action: 'set_value',
        parameters: {'value': 75.0, 'unit': '%'},
      );

      // Act
      final json = command.toJson();

      // Assert
      expect(json['action'], 'set_value');
      expect(json['parameters'], {'value': 75.0, 'unit': '%'});
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IoTApiException Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('IoTApiException', () {
    test('toString includes message and status code', () {
      final ex = IoTApiException('Device not found', statusCode: 404);
      expect(ex.toString(), contains('Device not found'));
      expect(ex.toString(), contains('404'));
    });

    test('message and statusCode properties', () {
      final ex = IoTApiException('Error', statusCode: 500);
      expect(ex.message, 'Error');
      expect(ex.statusCode, 500);
    });

    test('handles null statusCode', () {
      final ex = IoTApiException('Network error');
      expect(ex.statusCode, isNull);
      expect(ex.toString(), contains('Network error'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IoTApi Client Tests (with mocked http.Client)
  // ═══════════════════════════════════════════════════════════════════════════

  group('IoTApi', () {
    late MockHttpClient mockClient;
    late IoTApi api;

    setUp(() {
      mockClient = MockHttpClient();
      api = IoTApi(client: mockClient, authToken: 'test-token-123');
    });

    tearDown(() {
      // Do not call api.dispose() since we mock the client
    });

    test('getDevices returns list of devices on success', () async {
      // Arrange
      final responseBody = jsonEncode({
        'data': [
          {
            'id': 'D1',
            'name': 'Sensor 1',
            'type': 'soil_moisture',
            'field_id': 'F1',
            'status': 'active',
          },
          {
            'id': 'D2',
            'name': 'Sensor 2',
            'type': 'temperature',
            'field_id': 'F1',
            'status': 'active',
          },
        ]
      });

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final devices = await api.getDevices();

      // Assert
      expect(devices, hasLength(2));
      expect(devices.first.id, 'D1');
      expect(devices.first.name, 'Sensor 1');
      expect(devices.last.id, 'D2');
    });

    test('getDevices throws IoTApiException on error', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('{"error": "forbidden"}', 403));

      // Act & Assert
      expect(
        () => api.getDevices(),
        throwsA(isA<IoTApiException>()),
      );
    });

    test('getDevicesByField returns filtered devices', () async {
      // Arrange
      final responseBody = jsonEncode({
        'data': [
          {
            'id': 'D3',
            'name': 'Sensor 3',
            'type': 'humidity',
            'field_id': 'FIELD-002',
            'status': 'active',
          },
        ]
      });

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final devices = await api.getDevicesByField('FIELD-002');

      // Assert
      expect(devices, hasLength(1));
      expect(devices.first.fieldId, 'FIELD-002');
    });

    test('getDevice returns single device', () async {
      // Arrange
      final responseBody = jsonEncode({
        'data': {
          'id': 'D1',
          'name': 'Sensor 1',
          'type': 'soil_moisture',
          'field_id': 'F1',
          'status': 'active',
        }
      });

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final device = await api.getDevice('D1');

      // Assert
      expect(device.id, 'D1');
      expect(device.name, 'Sensor 1');
    });

    test('getDevice throws on not found', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('{"error": "not found"}', 404));

      // Act & Assert
      expect(
        () => api.getDevice('nonexistent'),
        throwsA(isA<IoTApiException>()),
      );
    });

    test('getDeviceTypes returns list of types', () async {
      // Arrange
      final responseBody = jsonEncode({
        'data': [
          {'type': 'soil_moisture', 'label': 'Soil Moisture'},
          {'type': 'temperature', 'label': 'Temperature'},
        ]
      });

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final types = await api.getDeviceTypes();

      // Assert
      expect(types, hasLength(2));
      expect(types.first['type'], 'soil_moisture');
    });

    test('getSensorReadings returns readings list', () async {
      // Arrange
      final responseBody = jsonEncode({
        'data': [
          {
            'device_id': 'D1',
            'sensor_type': 'soil_moisture',
            'value': 45.3,
            'unit': '%',
            'timestamp': '2025-06-15T10:00:00Z',
          },
          {
            'device_id': 'D1',
            'sensor_type': 'soil_moisture',
            'value': 43.1,
            'unit': '%',
            'timestamp': '2025-06-15T09:00:00Z',
          },
        ]
      });

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final readings = await api.getSensorReadings('D1');

      // Assert
      expect(readings, hasLength(2));
      expect(readings.first.value, 45.3);
    });

    test('getLatestReading returns first reading', () async {
      // Arrange
      final responseBody = jsonEncode({
        'data': [
          {
            'device_id': 'D1',
            'sensor_type': 'soil_moisture',
            'value': 45.3,
            'unit': '%',
            'timestamp': '2025-06-15T10:00:00Z',
          },
        ]
      });

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final reading = await api.getLatestReading('D1');

      // Assert
      expect(reading, isNotNull);
      expect(reading!.value, 45.3);
    });

    test('getLatestReading returns null when no readings', () async {
      // Arrange
      final responseBody = jsonEncode({'data': []});

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response(responseBody, 200));

      // Act
      final reading = await api.getLatestReading('D1');

      // Assert
      expect(reading, isNull);
    });

    test('sendCommand sends POST and returns response', () async {
      // Arrange
      final responseBody = jsonEncode({'status': 'accepted', 'commandId': 'CMD-001'});

      when(() => mockClient.post(
            any(),
            headers: any(named: 'headers'),
            body: any(named: 'body'),
          )).thenAnswer((_) async => http.Response(responseBody, 202));

      // Act
      final result = await api.sendCommand(
        'D1',
        IoTCommand(action: 'turn_on'),
      );

      // Assert
      expect(result['status'], 'accepted');
      expect(result['commandId'], 'CMD-001');
    });

    test('sendCommand throws on error', () async {
      // Arrange
      when(() => mockClient.post(
            any(),
            headers: any(named: 'headers'),
            body: any(named: 'body'),
          )).thenAnswer((_) async => http.Response('{"error": "offline"}', 503));

      // Act & Assert
      expect(
        () => api.sendCommand('D1', IoTCommand(action: 'turn_on')),
        throwsA(isA<IoTApiException>()),
      );
    });

    test('turnOn sends turn_on command', () async {
      // Arrange
      when(() => mockClient.post(
            any(),
            headers: any(named: 'headers'),
            body: any(named: 'body'),
          )).thenAnswer((_) async => http.Response('{"status":"ok"}', 200));

      // Act & Assert - should not throw
      await api.turnOn('D1');

      // Verify the command was sent
      final captured = verify(
        () => mockClient.post(
          any(),
          headers: any(named: 'headers'),
          body: captureAny(named: 'body'),
        ),
      ).captured;

      final body = jsonDecode(captured.first as String);
      expect(body['action'], 'turn_on');
    });

    test('turnOff sends turn_off command', () async {
      // Arrange
      when(() => mockClient.post(
            any(),
            headers: any(named: 'headers'),
            body: any(named: 'body'),
          )).thenAnswer((_) async => http.Response('{"status":"ok"}', 200));

      // Act
      await api.turnOff('D1');

      // Verify
      final captured = verify(
        () => mockClient.post(
          any(),
          headers: any(named: 'headers'),
          body: captureAny(named: 'body'),
        ),
      ).captured;

      final body = jsonDecode(captured.first as String);
      expect(body['action'], 'turn_off');
    });

    test('setValue sends set_value command with parameters', () async {
      // Arrange
      when(() => mockClient.post(
            any(),
            headers: any(named: 'headers'),
            body: any(named: 'body'),
          )).thenAnswer((_) async => http.Response('{"status":"ok"}', 200));

      // Act
      await api.setValue('D1', 75.0);

      // Verify
      final captured = verify(
        () => mockClient.post(
          any(),
          headers: any(named: 'headers'),
          body: captureAny(named: 'body'),
        ),
      ).captured;

      final body = jsonDecode(captured.first as String);
      expect(body['action'], 'set_value');
      expect(body['parameters']['value'], 75.0);
    });

    test('checkHealth returns true on 200', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('{"status":"ok"}', 200));

      // Act
      final healthy = await api.checkHealth();

      // Assert
      expect(healthy, true);
    });

    test('checkHealth returns false on non-200', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('', 503));

      // Act
      final healthy = await api.checkHealth();

      // Assert
      expect(healthy, false);
    });

    test('checkHealth returns false on network error', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenThrow(Exception('Network unavailable'));

      // Act
      final healthy = await api.checkHealth();

      // Assert
      expect(healthy, false);
    });
  });
}
