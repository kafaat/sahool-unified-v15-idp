import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Smart Alerts Provider
/// موفر التنبيهات الذكية

final smartAlertsProvider = FutureProvider<List<SmartAlert>>((ref) async {
  // In production, this would fetch from API/WebSocket
  await Future.delayed(const Duration(milliseconds: 300));

  return [
    SmartAlert(
      id: '1',
      title: 'رطوبة التربة منخفضة',
      message: 'مستوى الرطوبة في حقل الشمال وصل إلى 25% - يوصى بالري',
      type: AlertType.irrigation,
      severity: AlertSeverity.warning,
      source: 'حقل الشمال - جهاز الاستشعار S1',
      timeAgo: 'منذ 15 دقيقة',
      action: AlertAction(
        label: 'جدولة الري',
        type: AlertActionType.irrigate,
        route: '/irrigation/schedule',
      ),
    ),
    SmartAlert(
      id: '2',
      title: 'تحذير: درجة حرارة مرتفعة',
      message: 'درجة الحرارة في البيت المحمي وصلت إلى 38°C',
      type: AlertType.sensor,
      severity: AlertSeverity.critical,
      source: 'البيت المحمي 1',
      timeAgo: 'منذ 5 دقائق',
      action: AlertAction(
        label: 'فتح التهوية',
        type: AlertActionType.viewDetails,
        route: '/iot/greenhouse/1',
      ),
    ),
    SmartAlert(
      id: '3',
      title: 'انخفاض مؤشر NDVI',
      message: 'لوحظ انخفاض في صحة المحصول بالمنطقة الشرقية',
      type: AlertType.ndvi,
      severity: AlertSeverity.warning,
      source: 'حقل الجنوب - المنطقة E2',
      timeAgo: 'منذ ساعة',
      action: AlertAction(
        label: 'افحص الآن',
        type: AlertActionType.inspect,
        route: '/scouting/start',
      ),
    ),
    SmartAlert(
      id: '4',
      title: 'توقعات أمطار',
      message: 'احتمال هطول أمطار غداً - قم بتأجيل عملية التسميد',
      type: AlertType.weather,
      severity: AlertSeverity.info,
      source: 'خدمة الطقس',
      timeAgo: 'منذ ساعتين',
    ),
    SmartAlert(
      id: '5',
      title: 'مهمة متأخرة',
      message: 'موعد حصاد القمح تجاوز الموعد المحدد',
      type: AlertType.task,
      severity: AlertSeverity.warning,
      source: 'نظام المهام',
      timeAgo: 'منذ يوم',
      action: AlertAction(
        label: 'عرض المهمة',
        type: AlertActionType.viewDetails,
        route: '/tasks/123',
      ),
    ),
  ];
});

/// Stream provider for real-time alerts
final alertsStreamProvider = StreamProvider<List<SmartAlert>>((ref) async* {
  // Initial data
  yield await ref.read(smartAlertsProvider.future);

  // Simulate real-time updates
  await Future.delayed(const Duration(seconds: 30));

  // Would connect to WebSocket in production
});

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
