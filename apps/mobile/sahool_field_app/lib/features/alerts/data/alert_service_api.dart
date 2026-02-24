import '../../../core/api/kong_gateway_client.dart';

/// Alert Service API - خدمة التنبيهات
/// Connects to alert-service (port 8113) via Kong gateway
class AlertServiceApi {
  final KongGatewayClient _gateway;

  AlertServiceApi({KongGatewayClient? gateway})
      : _gateway = gateway ?? kongGateway;

  /// Get alerts for a specific field
  /// جلب التنبيهات لحقل معين
  Future<ApiResponse<AlertsPageResponse>> getFieldAlerts({
    required String fieldId,
    String? status,
    String? severity,
    String? type,
    int skip = 0,
    int limit = 20,
  }) async {
    final queryParams = <String, dynamic>{
      'skip': skip,
      'limit': limit,
    };
    if (status != null) queryParams['status'] = status;
    if (severity != null) queryParams['severity'] = severity;
    if (type != null) queryParams['type'] = type;

    return _gateway.get<AlertsPageResponse>(
      KongServices.alerts,
      '/field/$fieldId',
      queryParams: queryParams,
      fromJson: (data) =>
          AlertsPageResponse.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get a single alert by ID
  /// جلب تنبيه واحد بالمعرف
  Future<ApiResponse<AlertModel>> getAlert(String alertId) async {
    return _gateway.get<AlertModel>(
      KongServices.alerts,
      '/$alertId',
      fromJson: (data) => AlertModel.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Create a new alert
  /// إنشاء تنبيه جديد
  Future<ApiResponse<AlertModel>> createAlert({
    required String fieldId,
    required String type,
    required String severity,
    required String title,
    required String message,
    List<String>? recommendations,
    Map<String, dynamic>? metadata,
  }) async {
    return _gateway.post<AlertModel>(
      KongServices.alerts,
      '',
      data: {
        'field_id': fieldId,
        'type': type,
        'severity': severity,
        'title': title,
        'message': message,
        if (recommendations != null) 'recommendations': recommendations,
        if (metadata != null) 'metadata': metadata,
      },
      fromJson: (data) => AlertModel.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Acknowledge an alert
  /// الإقرار بتنبيه
  Future<ApiResponse<AlertModel>> acknowledgeAlert({
    required String alertId,
    required String userId,
  }) async {
    return _gateway.post<AlertModel>(
      KongServices.alerts,
      '/$alertId/acknowledge',
      data: {'user_id': userId},
      fromJson: (data) => AlertModel.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Resolve an alert
  /// حل تنبيه
  Future<ApiResponse<AlertModel>> resolveAlert({
    required String alertId,
    required String userId,
    String? note,
  }) async {
    return _gateway.post<AlertModel>(
      KongServices.alerts,
      '/$alertId/resolve',
      data: {
        'user_id': userId,
        if (note != null) 'note': note,
      },
      fromJson: (data) => AlertModel.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Dismiss an alert
  /// رفض تنبيه
  Future<ApiResponse<AlertModel>> dismissAlert({
    required String alertId,
    required String userId,
  }) async {
    return _gateway.post<AlertModel>(
      KongServices.alerts,
      '/$alertId/dismiss',
      data: {'user_id': userId},
      fromJson: (data) => AlertModel.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Delete an alert
  /// حذف تنبيه
  Future<ApiResponse<void>> deleteAlert(String alertId) async {
    return _gateway.delete<void>(
      KongServices.alerts,
      '/$alertId',
    );
  }

  /// Get alert statistics
  /// جلب إحصائيات التنبيهات
  Future<ApiResponse<AlertStats>> getAlertStats({
    String? fieldId,
    String period = '30d',
  }) async {
    final queryParams = <String, dynamic>{
      'period': period,
    };
    if (fieldId != null) queryParams['field_id'] = fieldId;

    return _gateway.get<AlertStats>(
      KongServices.alerts,
      '/stats',
      queryParams: queryParams,
      fromJson: (data) => AlertStats.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Get alert rules
  /// جلب قواعد التنبيهات
  Future<ApiResponse<List<AlertRule>>> getAlertRules({
    String? fieldId,
    bool? enabled,
  }) async {
    final queryParams = <String, dynamic>{};
    if (fieldId != null) queryParams['field_id'] = fieldId;
    if (enabled != null) queryParams['enabled'] = enabled;

    return _gateway.get<List<AlertRule>>(
      KongServices.alerts,
      '/rules',
      queryParams: queryParams,
      fromJson: (data) => (data as List)
          .map((e) => AlertRule.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Models - نماذج البيانات
// ═══════════════════════════════════════════════════════════════════════════

class AlertsPageResponse {
  final List<AlertModel> alerts;
  final int total;
  final int skip;
  final int limit;

  const AlertsPageResponse({
    required this.alerts,
    required this.total,
    required this.skip,
    required this.limit,
  });

  factory AlertsPageResponse.fromJson(Map<String, dynamic> json) {
    final alertsList = json['alerts'] as List? ?? json['items'] as List? ?? [];
    return AlertsPageResponse(
      alerts: alertsList
          .map((e) => AlertModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: json['total'] ?? alertsList.length,
      skip: json['skip'] ?? 0,
      limit: json['limit'] ?? 20,
    );
  }
}

class AlertModel {
  final String id;
  final String fieldId;
  final String type;
  final String severity;
  final String title;
  final String? message;
  final String status;
  final List<String> recommendations;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime? acknowledgedAt;
  final DateTime? resolvedAt;
  final String? acknowledgedBy;
  final String? resolvedBy;

  const AlertModel({
    required this.id,
    required this.fieldId,
    required this.type,
    required this.severity,
    required this.title,
    this.message,
    required this.status,
    this.recommendations = const [],
    this.metadata,
    required this.createdAt,
    this.acknowledgedAt,
    this.resolvedAt,
    this.acknowledgedBy,
    this.resolvedBy,
  });

  factory AlertModel.fromJson(Map<String, dynamic> json) {
    return AlertModel(
      id: json['id']?.toString() ?? '',
      fieldId: json['field_id']?.toString() ?? '',
      type: json['type']?.toString() ?? 'system',
      severity: json['severity']?.toString() ?? 'info',
      title: json['title']?.toString() ?? '',
      message: json['message']?.toString(),
      status: json['status']?.toString() ?? 'active',
      recommendations: (json['recommendations'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      metadata: json['metadata'] as Map<String, dynamic>?,
      createdAt: DateTime.tryParse(json['created_at']?.toString() ?? '') ??
          DateTime.now(),
      acknowledgedAt:
          DateTime.tryParse(json['acknowledged_at']?.toString() ?? ''),
      resolvedAt: DateTime.tryParse(json['resolved_at']?.toString() ?? ''),
      acknowledgedBy: json['acknowledged_by']?.toString(),
      resolvedBy: json['resolved_by']?.toString(),
    );
  }

  bool get isActive => status == 'active';
  bool get isAcknowledged => status == 'acknowledged';
  bool get isResolved => status == 'resolved';
  bool get isDismissed => status == 'dismissed';
  bool get isCritical => severity == 'critical';
  bool get isWarning => severity == 'warning';
}

class AlertStats {
  final int total;
  final int active;
  final int acknowledged;
  final int resolved;
  final int dismissed;
  final Map<String, int> bySeverity;
  final Map<String, int> byType;

  const AlertStats({
    required this.total,
    required this.active,
    required this.acknowledged,
    required this.resolved,
    required this.dismissed,
    required this.bySeverity,
    required this.byType,
  });

  factory AlertStats.fromJson(Map<String, dynamic> json) {
    return AlertStats(
      total: json['total'] ?? 0,
      active: json['active'] ?? 0,
      acknowledged: json['acknowledged'] ?? 0,
      resolved: json['resolved'] ?? 0,
      dismissed: json['dismissed'] ?? 0,
      bySeverity: (json['by_severity'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v as int)) ??
          {},
      byType: (json['by_type'] as Map<String, dynamic>?)
              ?.map((k, v) => MapEntry(k, v as int)) ??
          {},
    );
  }
}

class AlertRule {
  final String id;
  final String fieldId;
  final String name;
  final Map<String, dynamic> condition;
  final Map<String, dynamic> alertConfig;
  final bool enabled;
  final int cooldownMinutes;

  const AlertRule({
    required this.id,
    required this.fieldId,
    required this.name,
    required this.condition,
    required this.alertConfig,
    required this.enabled,
    required this.cooldownMinutes,
  });

  factory AlertRule.fromJson(Map<String, dynamic> json) {
    return AlertRule(
      id: json['id']?.toString() ?? '',
      fieldId: json['field_id']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      condition: json['condition'] as Map<String, dynamic>? ?? {},
      alertConfig: json['alert_config'] as Map<String, dynamic>? ?? {},
      enabled: json['enabled'] as bool? ?? true,
      cooldownMinutes: json['cooldown_minutes'] as int? ?? 60,
    );
  }
}
