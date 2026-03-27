import '../../../core/api/kong_gateway_client.dart';

/// Irrigation Cycle Engine API
/// محرك دورات الري - متصل بـ irrigation-cycle-engine (port 8250)
///
/// Endpoints:
///   GET  /pivots/:id/config  - Get pivot configuration
///   GET  /pivots/:id/status  - Get real-time pivot status
///   POST /pivots/:id/command - Send control command
///   GET  /pivots/:id/stats   - Get pivot statistics
///   GET  /pivots/:id/schedule - Get irrigation schedule
///   POST /pivots/:id/schedule - Create/update schedule
///   GET  /pivots/:id/history  - Get run history
class IrrigationEngineApi {
  final KongGatewayClient _gateway;

  IrrigationEngineApi({KongGatewayClient? gateway})
      : _gateway = gateway ?? kongGateway;

  /// Get pivot configuration
  /// الحصول على إعدادات المحوري
  Future<ApiResponse<Map<String, dynamic>>> getPivotConfig({
    required String pivotId,
  }) async {
    return _gateway.get<Map<String, dynamic>>(
      KongServices.irrigationEngine,
      '/pivots/$pivotId/config',
      fromJson: (data) => data as Map<String, dynamic>,
    );
  }

  /// Get real-time pivot status
  /// الحصول على حالة المحوري الحية
  Future<ApiResponse<Map<String, dynamic>>> getPivotStatus({
    required String pivotId,
  }) async {
    return _gateway.get<Map<String, dynamic>>(
      KongServices.irrigationEngine,
      '/pivots/$pivotId/status',
      fromJson: (data) => data as Map<String, dynamic>,
    );
  }

  /// Send control command to pivot
  /// إرسال أمر تحكم للمحوري
  Future<ApiResponse<Map<String, dynamic>>> sendCommand({
    required String pivotId,
    required String commandType,
    Map<String, dynamic>? params,
  }) async {
    return _gateway.post<Map<String, dynamic>>(
      KongServices.irrigationEngine,
      '/pivots/$pivotId/command',
      data: {
        'command': commandType,
        if (params != null) ...params,
      },
      fromJson: (data) => data as Map<String, dynamic>,
    );
  }

  /// Get pivot statistics
  /// الحصول على إحصائيات المحوري
  Future<ApiResponse<Map<String, dynamic>>> getPivotStats({
    required String pivotId,
    String period = 'week',
  }) async {
    return _gateway.get<Map<String, dynamic>>(
      KongServices.irrigationEngine,
      '/pivots/$pivotId/stats',
      queryParams: {'period': period},
      fromJson: (data) => data as Map<String, dynamic>,
    );
  }

  /// Get irrigation schedule
  /// الحصول على جدول الري
  Future<ApiResponse<Map<String, dynamic>>> getSchedule({
    required String pivotId,
  }) async {
    return _gateway.get<Map<String, dynamic>>(
      KongServices.irrigationEngine,
      '/pivots/$pivotId/schedule',
      fromJson: (data) => data as Map<String, dynamic>,
    );
  }

  /// Create or update irrigation schedule
  /// إنشاء أو تعديل جدول الري
  Future<ApiResponse<Map<String, dynamic>>> updateSchedule({
    required String pivotId,
    required Map<String, dynamic> schedule,
  }) async {
    return _gateway.post<Map<String, dynamic>>(
      KongServices.irrigationEngine,
      '/pivots/$pivotId/schedule',
      data: schedule,
      fromJson: (data) => data as Map<String, dynamic>,
    );
  }

  /// Get run history
  /// الحصول على سجل التشغيل
  Future<ApiResponse<List<dynamic>>> getRunHistory({
    required String pivotId,
    int limit = 20,
  }) async {
    return _gateway.get<List<dynamic>>(
      KongServices.irrigationEngine,
      '/pivots/$pivotId/history',
      queryParams: {'limit': limit},
      fromJson: (data) => data as List<dynamic>,
    );
  }

  /// Update sector settings
  /// تعديل إعدادات القطاع
  Future<ApiResponse<Map<String, dynamic>>> updateSector({
    required String pivotId,
    required String sectorId,
    required Map<String, dynamic> settings,
  }) async {
    return _gateway.put<Map<String, dynamic>>(
      KongServices.irrigationEngine,
      '/pivots/$pivotId/sectors/$sectorId',
      data: settings,
      fromJson: (data) => data as Map<String, dynamic>,
    );
  }
}
