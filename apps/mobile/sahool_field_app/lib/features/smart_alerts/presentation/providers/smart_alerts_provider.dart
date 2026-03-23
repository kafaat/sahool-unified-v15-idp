import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../alerts/data/alert_service_api.dart';

/// Smart Alerts Provider
/// موفر التنبيهات الذكية - متصل بـ alert-service

/// Provider for AlertServiceApi instance
final alertServiceApiProvider = Provider<AlertServiceApi>((ref) {
  return AlertServiceApi();
});

/// Fetches alerts for a specific field from alert-service
/// Uses autoDispose to clean up when no longer watched
final smartAlertsProvider = FutureProvider.autoDispose
    .family<List<SmartAlert>, String?>((ref, fieldId) async {
  final api = ref.watch(alertServiceApiProvider);

  // If no fieldId, fetch all active alerts
  if (fieldId == null || fieldId.isEmpty) {
    // Use stats endpoint to check for alerts, then fetch recent
    final response = await api.getFieldAlerts(
      fieldId: 'all',
      status: 'active',
      limit: 50,
    );

    if (!response.success || response.data == null) {
      return _getFallbackAlerts();
    }

    return response.data!.alerts.map(_mapToSmartAlert).toList();
  }

  final response = await api.getFieldAlerts(
    fieldId: fieldId,
    status: 'active',
    limit: 50,
  );

  if (!response.success || response.data == null) {
    // Return fallback mock data when API is unavailable (offline-first)
    return _getFallbackAlerts();
  }

  return response.data!.alerts.map(_mapToSmartAlert).toList();
});

/// Provider for all alerts (no field filter)
final allAlertsProvider =
    FutureProvider.autoDispose<List<SmartAlert>>((ref) async {
  return ref.watch(smartAlertsProvider(null).future);
});

/// Provider for alert statistics
final alertStatsProvider = FutureProvider.autoDispose
    .family<AlertStats?, String?>((ref, fieldId) async {
  final api = ref.watch(alertServiceApiProvider);
  final response = await api.getAlertStats(fieldId: fieldId);
  return response.data;
});

/// Stream provider for real-time alerts (polls every 30s)
/// Uses autoDispose to clean up subscription when no longer watched
final alertsStreamProvider = StreamProvider.autoDispose
    .family<List<SmartAlert>, String?>((ref, fieldId) async* {
  // Initial data
  yield await ref.read(smartAlertsProvider(fieldId).future);

  // Poll for updates every 30 seconds
  while (true) {
    await Future.delayed(const Duration(seconds: 30));
    try {
      final api = ref.read(alertServiceApiProvider);
      final response = await api.getFieldAlerts(
        fieldId: fieldId ?? 'all',
        status: 'active',
        limit: 50,
      );
      if (response.success && response.data != null) {
        yield response.data!.alerts.map(_mapToSmartAlert).toList();
      }
    } catch (_) {
      // Keep showing last data on error
    }
  }
});

/// Acknowledge alert action provider
final acknowledgeAlertProvider = FutureProvider.autoDispose
    .family<bool, ({String alertId, String userId})>((ref, params) async {
  final api = ref.read(alertServiceApiProvider);
  final response = await api.acknowledgeAlert(
    alertId: params.alertId,
    userId: params.userId,
  );
  if (response.success) {
    // Invalidate alerts to refresh
    ref.invalidate(smartAlertsProvider);
  }
  return response.success;
});

/// Dismiss alert action provider
final dismissAlertProvider = FutureProvider.autoDispose
    .family<bool, ({String alertId, String userId})>((ref, params) async {
  final api = ref.read(alertServiceApiProvider);
  final response = await api.dismissAlert(
    alertId: params.alertId,
    userId: params.userId,
  );
  if (response.success) {
    ref.invalidate(smartAlertsProvider);
  }
  return response.success;
});

// ═══════════════════════════════════════════════════════════════════════════
// Mapping & Fallback
// ═══════════════════════════════════════════════════════════════════════════

/// Map AlertModel from API to SmartAlert for UI
SmartAlert _mapToSmartAlert(AlertModel alert) {
  return SmartAlert(
    id: alert.id,
    title: alert.title,
    message: alert.message,
    type: _mapAlertType(alert.type),
    severity: _mapAlertSeverity(alert.severity),
    source: alert.metadata?['source']?.toString() ?? alert.fieldId,
    timeAgo: _formatTimeAgo(alert.createdAt),
    action: alert.recommendations.isNotEmpty
        ? AlertAction(
            label: alert.recommendations.first,
            type: AlertActionType.viewDetails,
            route: '/alerts/${alert.id}',
          )
        : null,
    isRead: !alert.isActive,
    createdAt: alert.createdAt,
  );
}

AlertType _mapAlertType(String type) {
  switch (type) {
    case 'irrigation':
      return AlertType.irrigation;
    case 'weather':
      return AlertType.weather;
    case 'ndvi':
      return AlertType.ndvi;
    case 'sensor':
      return AlertType.sensor;
    case 'task':
      return AlertType.task;
    case 'pest':
      return AlertType.pest;
    default:
      return AlertType.system;
  }
}

AlertSeverity _mapAlertSeverity(String severity) {
  switch (severity) {
    case 'critical':
      return AlertSeverity.critical;
    case 'warning':
      return AlertSeverity.warning;
    case 'info':
      return AlertSeverity.info;
    case 'success':
      return AlertSeverity.success;
    default:
      return AlertSeverity.info;
  }
}

String _formatTimeAgo(DateTime time) {
  final diff = DateTime.now().difference(time);
  if (diff.inMinutes < 1) return 'الآن';
  if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
  if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
  if (diff.inDays < 7) return 'منذ ${diff.inDays} يوم';
  return 'منذ ${(diff.inDays / 7).floor()} أسبوع';
}

/// Fallback alerts when API is unavailable (offline-first pattern)
List<SmartAlert> _getFallbackAlerts() {
  return [
    SmartAlert(
      id: 'offline_1',
      title: 'غير متصل بالخدمة',
      message: 'تعذر الاتصال بخدمة التنبيهات - سيتم التحديث عند الاتصال',
      type: AlertType.system,
      severity: AlertSeverity.info,
      source: 'النظام',
      timeAgo: 'الآن',
      isRead: false,
      createdAt: DateTime.now(),
    ),
  ];
}

// ═══════════════════════════════════════════════════════════════════════════
// Models
// ═══════════════════════════════════════════════════════════════════════════

class SmartAlert {
  final String id;
  final String title;
  final String? message;
  final AlertType type;
  final AlertSeverity severity;
  final String source;
  final String timeAgo;
  final AlertAction? action;
  final bool isRead;
  final DateTime? createdAt;

  const SmartAlert({
    required this.id,
    required this.title,
    this.message,
    required this.type,
    required this.severity,
    required this.source,
    required this.timeAgo,
    this.action,
    this.isRead = false,
    this.createdAt,
  });
}

class AlertAction {
  final String label;
  final AlertActionType type;
  final String? route;
  final Map<String, dynamic>? params;

  const AlertAction({
    required this.label,
    required this.type,
    this.route,
    this.params,
  });
}

enum AlertType {
  irrigation,
  weather,
  ndvi,
  sensor,
  task,
  pest,
  system,
}

enum AlertSeverity {
  critical,
  warning,
  info,
  success,
}

enum AlertActionType {
  irrigate,
  inspect,
  createTask,
  viewDetails,
  dismiss,
}
