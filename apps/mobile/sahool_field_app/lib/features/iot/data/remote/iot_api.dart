/// IoT Gateway API Client - Integrated with IoT Service (port 8106)
/// عميل API بوابة إنترنت الأشياء
library;

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';

/// IoT Device Model
/// نموذج جهاز IoT
class IoTDevice {
  final String id;
  final String name;
  final String type;
  final String fieldId;
  final String status;
  final Map<String, dynamic>? metadata;
  final DateTime? lastSeen;
  final bool isOnline;

  IoTDevice({
    required this.id,
    required this.name,
    required this.type,
    required this.fieldId,
    required this.status,
    this.metadata,
    this.lastSeen,
    this.isOnline = false,
  });

  factory IoTDevice.fromJson(Map<String, dynamic> json) {
    return IoTDevice(
      id: json['id'] as String,
      name: json['name'] as String,
      type: json['type'] as String,
      fieldId: json['field_id'] as String,
      status: json['status'] as String,
      metadata: json['metadata'] as Map<String, dynamic>?,
      lastSeen: json['last_seen'] != null
          ? DateTime.parse(json['last_seen'] as String)
          : null,
      isOnline: json['is_online'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'type': type,
        'field_id': fieldId,
        'status': status,
        'metadata': metadata,
        'last_seen': lastSeen?.toIso8601String(),
        'is_online': isOnline,
      };
}

/// Sensor Reading Model
/// نموذج قراءة المستشعر
class SensorReading {
  final String deviceId;
  final String sensorType;
  final double value;
  final String unit;
  final DateTime timestamp;

  SensorReading({
    required this.deviceId,
    required this.sensorType,
    required this.value,
    required this.unit,
    required this.timestamp,
  });

  factory SensorReading.fromJson(Map<String, dynamic> json) {
    return SensorReading(
      deviceId: json['device_id'] as String,
      sensorType: json['sensor_type'] as String,
      value: (json['value'] as num).toDouble(),
      unit: json['unit'] as String,
      timestamp: DateTime.parse(json['timestamp'] as String),
    );
  }
}

/// IoT Command Model
/// نموذج أمر IoT
class IoTCommand {
  final String action;
  final Map<String, dynamic>? parameters;

  IoTCommand({
    required this.action,
    this.parameters,
  });

  Map<String, dynamic> toJson() => {
        'action': action,
        if (parameters != null) 'parameters': parameters,
      };
}

/// IoT API Exception
/// استثناء API IoT
class IoTApiException implements Exception {
  final String message;
  final int? statusCode;

  IoTApiException(this.message, {this.statusCode});

  @override
  String toString() => 'IoTApiException: $message (status: $statusCode)';
}

/// IoT Gateway API Client
/// عميل API بوابة إنترنت الأشياء
class IoTApi {
  final http.Client _client;
  final String? _authToken;

  IoTApi({
    http.Client? client,
    String? authToken,
  })  : _client = client ?? http.Client(),
        _authToken = authToken;

  Map<String, String> get _headers => {
        ...ApiConfig.defaultHeaders,
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Device Management
  // إدارة الأجهزة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get all devices for the authenticated user
  /// جلب جميع الأجهزة للمستخدم
  Future<List<IoTDevice>> getDevices() async {
    final response = await _client.get(
      Uri.parse(ApiConfig.iotDevices),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      final devices = json['data'] as List;
      return devices.map((d) => IoTDevice.fromJson(d)).toList();
    } else {
      throw IoTApiException(
        'فشل جلب قائمة الأجهزة',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get devices for a specific field
  /// جلب أجهزة حقل معين
  Future<List<IoTDevice>> getDevicesByField(String fieldId) async {
    final response = await _client.get(
      Uri.parse(ApiConfig.iotDevicesByField(fieldId)),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      final devices = json['data'] as List;
      return devices.map((d) => IoTDevice.fromJson(d)).toList();
    } else {
      throw IoTApiException(
        'فشل جلب أجهزة الحقل',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get a specific device by ID
  /// جلب جهاز بالمعرف
  Future<IoTDevice> getDevice(String deviceId) async {
    final response = await _client.get(
      Uri.parse(ApiConfig.iotDeviceById(deviceId)),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return IoTDevice.fromJson(json['data']);
    } else {
      throw IoTApiException(
        'فشل جلب الجهاز',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get available device types
  /// جلب أنواع الأجهزة المتاحة
  Future<List<Map<String, dynamic>>> getDeviceTypes() async {
    final response = await _client.get(
      Uri.parse(ApiConfig.iotDeviceTypes),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return List<Map<String, dynamic>>.from(json['data']);
    } else {
      throw IoTApiException(
        'فشل جلب أنواع الأجهزة',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sensor Readings
  // قراءات المستشعرات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get sensor readings for a device
  /// جلب قراءات مستشعر جهاز
  Future<List<SensorReading>> getSensorReadings(
    String deviceId, {
    DateTime? from,
    DateTime? to,
    int? limit,
  }) async {
    final uri = Uri.parse(ApiConfig.iotSensorReadings(deviceId)).replace(
      queryParameters: {
        if (from != null) 'from': from.toIso8601String(),
        if (to != null) 'to': to.toIso8601String(),
        if (limit != null) 'limit': limit.toString(),
      },
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      final readings = json['data'] as List;
      return readings.map((r) => SensorReading.fromJson(r)).toList();
    } else {
      throw IoTApiException(
        'فشل جلب قراءات المستشعر',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get latest reading for a device
  /// جلب آخر قراءة لجهاز
  Future<SensorReading?> getLatestReading(String deviceId) async {
    final readings = await getSensorReadings(deviceId, limit: 1);
    return readings.isNotEmpty ? readings.first : null;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Device Control
  // التحكم في الأجهزة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Send a command to a device
  /// إرسال أمر لجهاز
  Future<Map<String, dynamic>> sendCommand(
    String deviceId,
    IoTCommand command,
  ) async {
    final response = await _client.post(
      Uri.parse(ApiConfig.iotDeviceCommand(deviceId)),
      headers: _headers,
      body: jsonEncode(command.toJson()),
    );

    if (response.statusCode == 200 || response.statusCode == 202) {
      return jsonDecode(response.body);
    } else {
      throw IoTApiException(
        'فشل إرسال الأمر للجهاز',
        statusCode: response.statusCode,
      );
    }
  }

  /// Turn on a device
  /// تشغيل جهاز
  Future<void> turnOn(String deviceId) async {
    await sendCommand(deviceId, IoTCommand(action: 'turn_on'));
  }

  /// Turn off a device
  /// إيقاف جهاز
  Future<void> turnOff(String deviceId) async {
    await sendCommand(deviceId, IoTCommand(action: 'turn_off'));
  }

  /// Set device value (e.g., irrigation valve percentage)
  /// ضبط قيمة الجهاز
  Future<void> setValue(String deviceId, double value) async {
    await sendCommand(
      deviceId,
      IoTCommand(
        action: 'set_value',
        parameters: {'value': value},
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Check
  // فحص الصحة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check IoT service health
  /// فحص صحة خدمة IoT
  Future<bool> checkHealth() async {
    try {
      final response = await _client.get(
        Uri.parse(ApiConfig.iotHealthz),
        headers: _headers,
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Dispose the client
  void dispose() {
    _client.close();
  }
}
