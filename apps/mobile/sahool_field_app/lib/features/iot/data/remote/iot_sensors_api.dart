import 'dart:async';
import 'package:dio/dio.dart';
import '../../../core/config/api_config.dart';

/// IoT Sensors Service API Integration
/// تكامل خدمة مستشعرات إنترنت الأشياء
///
/// Port: 8100 (configurable)
/// Features: Real-time sensor data, actuator control, alerts
class IoTSensorsApi {
  final Dio _dio;
  final String _baseUrl;
  final String _wsUrl;

  IoTSensorsApi({
    Dio? dio,
    String? baseUrl,
    String? wsUrl,
  })  : _dio = dio ?? Dio(),
        _baseUrl = baseUrl ?? '${ApiConfig.baseUrl}:8100',
        _wsUrl = wsUrl ?? 'ws://${ApiConfig.host}:8100/ws';

  // ─────────────────────────────────────────────────────────────────────────
  // Sensors - المستشعرات
  // ─────────────────────────────────────────────────────────────────────────

  /// Get all sensors for field
  /// جلب جميع المستشعرات للحقل
  Future<ApiResult<List<Sensor>>> getFieldSensors(String fieldId) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/sensors',
      );
      final List<dynamic> data = response.data['sensors'] ?? response.data;
      return ApiResult.success(
        data.map((e) => Sensor.fromJson(e)).toList(),
      );
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get sensor by ID
  /// جلب مستشعر بالمعرف
  Future<ApiResult<Sensor>> getSensor(String sensorId) async {
    try {
      final response = await _dio.get('$_baseUrl/sensors/$sensorId');
      return ApiResult.success(Sensor.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get current sensor reading
  /// جلب قراءة المستشعر الحالية
  Future<ApiResult<SensorReading>> getCurrentReading(String sensorId) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/sensors/$sensorId/reading',
      );
      return ApiResult.success(SensorReading.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get sensor readings history
  /// جلب سجل قراءات المستشعر
  Future<ApiResult<List<SensorReading>>> getReadingsHistory({
    required String sensorId,
    DateTime? startDate,
    DateTime? endDate,
    int? limit,
    String? interval, // '1h', '6h', '1d', '1w'
  }) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/sensors/$sensorId/readings',
        queryParameters: {
          if (startDate != null) 'start_date': startDate.toIso8601String(),
          if (endDate != null) 'end_date': endDate.toIso8601String(),
          if (limit != null) 'limit': limit,
          if (interval != null) 'interval': interval,
        },
      );
      final List<dynamic> data = response.data['readings'] ?? response.data;
      return ApiResult.success(
        data.map((e) => SensorReading.fromJson(e)).toList(),
      );
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get aggregated sensor statistics
  /// جلب إحصائيات المستشعر المجمعة
  Future<ApiResult<SensorStatistics>> getSensorStatistics({
    required String sensorId,
    required String period, // 'day', 'week', 'month'
  }) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/sensors/$sensorId/statistics',
        queryParameters: {'period': period},
      );
      return ApiResult.success(SensorStatistics.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Actuators - المحركات
  // ─────────────────────────────────────────────────────────────────────────

  /// Get all actuators for field
  /// جلب جميع المحركات للحقل
  Future<ApiResult<List<Actuator>>> getFieldActuators(String fieldId) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/actuators',
      );
      final List<dynamic> data = response.data['actuators'] ?? response.data;
      return ApiResult.success(
        data.map((e) => Actuator.fromJson(e)).toList(),
      );
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Control actuator (turn on/off)
  /// التحكم في المحرك (تشغيل/إيقاف)
  Future<ApiResult<ActuatorStatus>> controlActuator({
    required String actuatorId,
    required bool turnOn,
    int? durationMinutes,
    String? reason,
  }) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/actuators/$actuatorId/control',
        data: {
          'action': turnOn ? 'on' : 'off',
          if (durationMinutes != null) 'duration_minutes': durationMinutes,
          if (reason != null) 'reason': reason,
        },
      );
      return ApiResult.success(ActuatorStatus.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Schedule actuator operation
  /// جدولة عملية المحرك
  Future<ApiResult<ScheduledOperation>> scheduleActuator({
    required String actuatorId,
    required DateTime startTime,
    required int durationMinutes,
    String? repeatPattern, // 'daily', 'weekly', 'custom'
  }) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/actuators/$actuatorId/schedule',
        data: {
          'start_time': startTime.toIso8601String(),
          'duration_minutes': durationMinutes,
          if (repeatPattern != null) 'repeat_pattern': repeatPattern,
        },
      );
      return ApiResult.success(ScheduledOperation.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get actuator history
  /// جلب سجل عمليات المحرك
  Future<ApiResult<List<ActuatorOperation>>> getActuatorHistory({
    required String actuatorId,
    int? limit,
  }) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/actuators/$actuatorId/history',
        queryParameters: {if (limit != null) 'limit': limit},
      );
      final List<dynamic> data = response.data['operations'] ?? response.data;
      return ApiResult.success(
        data.map((e) => ActuatorOperation.fromJson(e)).toList(),
      );
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Alerts & Monitoring - التنبيهات والمراقبة
  // ─────────────────────────────────────────────────────────────────────────

  /// Get active alerts for field
  /// جلب التنبيهات النشطة للحقل
  Future<ApiResult<List<IoTAlert>>> getActiveAlerts(String fieldId) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/alerts',
        queryParameters: {'status': 'active'},
      );
      final List<dynamic> data = response.data['alerts'] ?? response.data;
      return ApiResult.success(
        data.map((e) => IoTAlert.fromJson(e)).toList(),
      );
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Acknowledge alert
  /// تأكيد استلام التنبيه
  Future<ApiResult<IoTAlert>> acknowledgeAlert(String alertId) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/alerts/$alertId/acknowledge',
      );
      return ApiResult.success(IoTAlert.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Set alert threshold
  /// تعيين عتبة التنبيه
  Future<ApiResult<AlertThreshold>> setAlertThreshold({
    required String sensorId,
    required String metric,
    double? minValue,
    double? maxValue,
  }) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/sensors/$sensorId/thresholds',
        data: {
          'metric': metric,
          if (minValue != null) 'min_value': minValue,
          if (maxValue != null) 'max_value': maxValue,
        },
      );
      return ApiResult.success(AlertThreshold.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Dashboard & Summary - لوحة التحكم والملخص
  // ─────────────────────────────────────────────────────────────────────────

  /// Get field IoT dashboard summary
  /// جلب ملخص لوحة تحكم IoT للحقل
  Future<ApiResult<IoTDashboard>> getFieldDashboard(String fieldId) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/dashboard',
      );
      return ApiResult.success(IoTDashboard.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get device health status
  /// جلب حالة صحة الأجهزة
  Future<ApiResult<List<DeviceHealth>>> getDevicesHealth(String fieldId) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/fields/$fieldId/devices/health',
      );
      final List<dynamic> data = response.data['devices'] ?? response.data;
      return ApiResult.success(
        data.map((e) => DeviceHealth.fromJson(e)).toList(),
      );
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // WebSocket URL for real-time updates
  // ─────────────────────────────────────────────────────────────────────────

  /// Get WebSocket URL for field
  /// جلب رابط WebSocket للحقل
  ///
  /// Security Note: Token should be passed via Authorization header when connecting,
  /// not in the URL. Use: headers: {'Authorization': 'Bearer $token'}
  /// ملاحظة أمنية: يجب تمرير الرمز عبر رأس التفويض وليس في عنوان URL
  String getWebSocketUrl(String fieldId) {
    return '$_wsUrl/fields/$fieldId';
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Error Handling
  // ─────────────────────────────────────────────────────────────────────────

  String _handleError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.receiveTimeout:
        return 'انتهت مهلة الاتصال بخدمة المستشعرات';
      case DioExceptionType.connectionError:
        return 'لا يمكن الاتصال بخدمة المستشعرات - تحقق من اتصال الشبكة';
      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode ?? 0;
        if (statusCode == 404) {
          return 'المستشعر أو الحقل غير موجود';
        } else if (statusCode == 403) {
          return 'ليس لديك صلاحية للتحكم في هذا الجهاز';
        }
        return 'خطأ في الخادم: $statusCode';
      default:
        return 'حدث خطأ غير متوقع في خدمة المستشعرات';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Data Models - نماذج البيانات
// ─────────────────────────────────────────────────────────────────────────────

class ApiResult<T> {
  final T? data;
  final String? error;
  final bool isSuccess;

  ApiResult._({this.data, this.error, required this.isSuccess});

  factory ApiResult.success(T data) => ApiResult._(data: data, isSuccess: true);
  factory ApiResult.failure(String error) => ApiResult._(error: error, isSuccess: false);
}

/// IoT Sensor device
class Sensor {
  final String id;
  final String fieldId;
  final String name;
  final String type; // soil_moisture, temperature, humidity, ph, ec, light
  final String status; // online, offline, maintenance
  final double? latitude;
  final double? longitude;
  final String? zone;
  final DateTime lastReading;
  final double? batteryLevel;
  final String unit;

  Sensor({
    required this.id,
    required this.fieldId,
    required this.name,
    required this.type,
    required this.status,
    this.latitude,
    this.longitude,
    this.zone,
    required this.lastReading,
    this.batteryLevel,
    required this.unit,
  });

  factory Sensor.fromJson(Map<String, dynamic> json) {
    return Sensor(
      id: json['id'] ?? '',
      fieldId: json['field_id'] ?? '',
      name: json['name'] ?? '',
      type: json['type'] ?? 'unknown',
      status: json['status'] ?? 'offline',
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      zone: json['zone'],
      lastReading: DateTime.parse(
        json['last_reading'] ?? DateTime.now().toIso8601String(),
      ),
      batteryLevel: (json['battery_level'] as num?)?.toDouble(),
      unit: json['unit'] ?? '',
    );
  }

  String get typeAr {
    switch (type) {
      case 'soil_moisture':
        return 'رطوبة التربة';
      case 'temperature':
        return 'درجة الحرارة';
      case 'humidity':
        return 'الرطوبة الجوية';
      case 'ph':
        return 'حموضة التربة';
      case 'ec':
        return 'الموصلية الكهربائية';
      case 'light':
        return 'شدة الإضاءة';
      case 'wind':
        return 'سرعة الرياح';
      case 'rain':
        return 'هطول الأمطار';
      default:
        return type;
    }
  }

  bool get isOnline => status == 'online';
  bool get needsBattery => (batteryLevel ?? 100) < 20;
}

/// Sensor reading
class SensorReading {
  final String sensorId;
  final double value;
  final String unit;
  final DateTime timestamp;
  final String? quality; // good, fair, poor

  SensorReading({
    required this.sensorId,
    required this.value,
    required this.unit,
    required this.timestamp,
    this.quality,
  });

  factory SensorReading.fromJson(Map<String, dynamic> json) {
    return SensorReading(
      sensorId: json['sensor_id'] ?? '',
      value: (json['value'] as num?)?.toDouble() ?? 0,
      unit: json['unit'] ?? '',
      timestamp: DateTime.parse(
        json['timestamp'] ?? DateTime.now().toIso8601String(),
      ),
      quality: json['quality'],
    );
  }
}

/// Sensor statistics
class SensorStatistics {
  final String sensorId;
  final String period;
  final double min;
  final double max;
  final double average;
  final double current;
  final String trend; // rising, falling, stable
  final int readingsCount;

  SensorStatistics({
    required this.sensorId,
    required this.period,
    required this.min,
    required this.max,
    required this.average,
    required this.current,
    required this.trend,
    required this.readingsCount,
  });

  factory SensorStatistics.fromJson(Map<String, dynamic> json) {
    return SensorStatistics(
      sensorId: json['sensor_id'] ?? '',
      period: json['period'] ?? 'day',
      min: (json['min'] as num?)?.toDouble() ?? 0,
      max: (json['max'] as num?)?.toDouble() ?? 0,
      average: (json['average'] as num?)?.toDouble() ?? 0,
      current: (json['current'] as num?)?.toDouble() ?? 0,
      trend: json['trend'] ?? 'stable',
      readingsCount: json['readings_count'] ?? 0,
    );
  }
}

/// Actuator device (pump, valve, etc.)
class Actuator {
  final String id;
  final String fieldId;
  final String name;
  final String type; // pump, valve, sprinkler
  final bool isOn;
  final DateTime? lastOperation;
  final String status; // online, offline, error

  Actuator({
    required this.id,
    required this.fieldId,
    required this.name,
    required this.type,
    required this.isOn,
    this.lastOperation,
    required this.status,
  });

  factory Actuator.fromJson(Map<String, dynamic> json) {
    return Actuator(
      id: json['id'] ?? '',
      fieldId: json['field_id'] ?? '',
      name: json['name'] ?? '',
      type: json['type'] ?? 'unknown',
      isOn: json['is_on'] ?? false,
      lastOperation: json['last_operation'] != null
          ? DateTime.parse(json['last_operation'])
          : null,
      status: json['status'] ?? 'offline',
    );
  }

  String get typeAr {
    switch (type) {
      case 'pump':
        return 'مضخة';
      case 'valve':
        return 'صمام';
      case 'sprinkler':
        return 'رشاش';
      default:
        return type;
    }
  }
}

/// Actuator status after control
class ActuatorStatus {
  final String actuatorId;
  final bool isOn;
  final DateTime operatedAt;
  final int? remainingMinutes;

  ActuatorStatus({
    required this.actuatorId,
    required this.isOn,
    required this.operatedAt,
    this.remainingMinutes,
  });

  factory ActuatorStatus.fromJson(Map<String, dynamic> json) {
    return ActuatorStatus(
      actuatorId: json['actuator_id'] ?? '',
      isOn: json['is_on'] ?? false,
      operatedAt: DateTime.parse(
        json['operated_at'] ?? DateTime.now().toIso8601String(),
      ),
      remainingMinutes: json['remaining_minutes'],
    );
  }
}

/// Scheduled actuator operation
class ScheduledOperation {
  final String id;
  final String actuatorId;
  final DateTime startTime;
  final int durationMinutes;
  final String? repeatPattern;
  final String status; // scheduled, running, completed, cancelled

  ScheduledOperation({
    required this.id,
    required this.actuatorId,
    required this.startTime,
    required this.durationMinutes,
    this.repeatPattern,
    required this.status,
  });

  factory ScheduledOperation.fromJson(Map<String, dynamic> json) {
    return ScheduledOperation(
      id: json['id'] ?? '',
      actuatorId: json['actuator_id'] ?? '',
      startTime: DateTime.parse(json['start_time']),
      durationMinutes: json['duration_minutes'] ?? 0,
      repeatPattern: json['repeat_pattern'],
      status: json['status'] ?? 'scheduled',
    );
  }
}

/// Actuator operation history
class ActuatorOperation {
  final String id;
  final String actuatorId;
  final String action; // on, off
  final DateTime timestamp;
  final int? durationMinutes;
  final String triggeredBy; // manual, schedule, automation

  ActuatorOperation({
    required this.id,
    required this.actuatorId,
    required this.action,
    required this.timestamp,
    this.durationMinutes,
    required this.triggeredBy,
  });

  factory ActuatorOperation.fromJson(Map<String, dynamic> json) {
    return ActuatorOperation(
      id: json['id'] ?? '',
      actuatorId: json['actuator_id'] ?? '',
      action: json['action'] ?? 'off',
      timestamp: DateTime.parse(
        json['timestamp'] ?? DateTime.now().toIso8601String(),
      ),
      durationMinutes: json['duration_minutes'],
      triggeredBy: json['triggered_by'] ?? 'manual',
    );
  }
}

/// IoT Alert
class IoTAlert {
  final String id;
  final String sensorId;
  final String type; // threshold_exceeded, device_offline, low_battery
  final String severity; // info, warning, critical
  final String message;
  final DateTime triggeredAt;
  final bool acknowledged;
  final double? value;
  final double? threshold;

  IoTAlert({
    required this.id,
    required this.sensorId,
    required this.type,
    required this.severity,
    required this.message,
    required this.triggeredAt,
    required this.acknowledged,
    this.value,
    this.threshold,
  });

  factory IoTAlert.fromJson(Map<String, dynamic> json) {
    return IoTAlert(
      id: json['id'] ?? '',
      sensorId: json['sensor_id'] ?? '',
      type: json['type'] ?? 'unknown',
      severity: json['severity'] ?? 'info',
      message: json['message'] ?? '',
      triggeredAt: DateTime.parse(
        json['triggered_at'] ?? DateTime.now().toIso8601String(),
      ),
      acknowledged: json['acknowledged'] ?? false,
      value: (json['value'] as num?)?.toDouble(),
      threshold: (json['threshold'] as num?)?.toDouble(),
    );
  }
}

/// Alert threshold configuration
class AlertThreshold {
  final String sensorId;
  final String metric;
  final double? minValue;
  final double? maxValue;

  AlertThreshold({
    required this.sensorId,
    required this.metric,
    this.minValue,
    this.maxValue,
  });

  factory AlertThreshold.fromJson(Map<String, dynamic> json) {
    return AlertThreshold(
      sensorId: json['sensor_id'] ?? '',
      metric: json['metric'] ?? '',
      minValue: (json['min_value'] as num?)?.toDouble(),
      maxValue: (json['max_value'] as num?)?.toDouble(),
    );
  }
}

/// IoT Dashboard summary
class IoTDashboard {
  final String fieldId;
  final int totalSensors;
  final int onlineSensors;
  final int totalActuators;
  final int activeActuators;
  final int activeAlerts;
  final Map<String, double> currentReadings;
  final DateTime lastUpdate;

  IoTDashboard({
    required this.fieldId,
    required this.totalSensors,
    required this.onlineSensors,
    required this.totalActuators,
    required this.activeActuators,
    required this.activeAlerts,
    required this.currentReadings,
    required this.lastUpdate,
  });

  factory IoTDashboard.fromJson(Map<String, dynamic> json) {
    return IoTDashboard(
      fieldId: json['field_id'] ?? '',
      totalSensors: json['total_sensors'] ?? 0,
      onlineSensors: json['online_sensors'] ?? 0,
      totalActuators: json['total_actuators'] ?? 0,
      activeActuators: json['active_actuators'] ?? 0,
      activeAlerts: json['active_alerts'] ?? 0,
      currentReadings: Map<String, double>.from(
        (json['current_readings'] ?? {}).map(
          (k, v) => MapEntry(k.toString(), (v as num).toDouble()),
        ),
      ),
      lastUpdate: DateTime.parse(
        json['last_update'] ?? DateTime.now().toIso8601String(),
      ),
    );
  }

  double get sensorHealthPercent =>
      totalSensors > 0 ? (onlineSensors / totalSensors) * 100 : 0;
}

/// Device health status
class DeviceHealth {
  final String deviceId;
  final String deviceType;
  final String status; // healthy, warning, critical
  final double? signalStrength;
  final double? batteryLevel;
  final DateTime lastSeen;
  final List<String> issues;

  DeviceHealth({
    required this.deviceId,
    required this.deviceType,
    required this.status,
    this.signalStrength,
    this.batteryLevel,
    required this.lastSeen,
    required this.issues,
  });

  factory DeviceHealth.fromJson(Map<String, dynamic> json) {
    return DeviceHealth(
      deviceId: json['device_id'] ?? '',
      deviceType: json['device_type'] ?? '',
      status: json['status'] ?? 'unknown',
      signalStrength: (json['signal_strength'] as num?)?.toDouble(),
      batteryLevel: (json['battery_level'] as num?)?.toDouble(),
      lastSeen: DateTime.parse(
        json['last_seen'] ?? DateTime.now().toIso8601String(),
      ),
      issues: List<String>.from(json['issues'] ?? []),
    );
  }
}
