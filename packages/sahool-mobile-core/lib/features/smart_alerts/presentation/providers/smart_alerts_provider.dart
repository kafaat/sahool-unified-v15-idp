import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/config/api_config.dart';
import '../../../../core/utils/app_logger.dart';

/// Smart Alerts Provider
/// موفر التنبيهات الذكية
///
/// Architecture:
/// 1. Try GET /api/v1/alerts/smart from alert-service (port 8113)
/// 2. On failure (offline/unavailable), fall back to built-in mock data

// =============================================================================
// Repository
// =============================================================================

class SmartAlertsRepository {
  final Dio _dio;

  SmartAlertsRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  /// جلب التنبيهات من API أو الرجوع للبيانات المحلية
  Future<List<SmartAlert>> fetchAlerts() async {
    try {
      final response = await _dio.get('/api/v1/alerts/smart');
      final List data = response.data as List;
      return data
          .map((e) => _parseAlert(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      AppLogger.w(
        'Smart alerts API unavailable (${e.type.name}), using local data',
        tag: 'SMART_ALERTS',
      );
      return _buildMockAlerts();
    } catch (e) {
      AppLogger.w('Smart alerts parse error: $e, using local data',
          tag: 'SMART_ALERTS');
      return _buildMockAlerts();
    }
  }

  SmartAlert _parseAlert(Map<String, dynamic> json) {
    AlertAction? action;
    final actionData = json['action'] as Map<String, dynamic>?;
    if (actionData != null) {
      action = AlertAction(
        label: actionData['label'] as String? ?? '',
        type: _parseActionType(actionData['type'] as String?),
        route: actionData['route'] as String?,
        params: actionData['params'] as Map<String, dynamic>?,
      );
    }

    return SmartAlert(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      message: json['message'] as String?,
      type: _parseAlertType(json['type'] as String?),
      severity: _parseSeverity(json['severity'] as String?),
      source: json['source'] as String? ?? '',
      timeAgo: json['timeAgo'] as String? ?? '',
      action: action,
      isRead: json['isRead'] as bool? ?? false,
      createdAt: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'] as String)
          : null,
    );
  }

  AlertType _parseAlertType(String? value) {
    switch (value) {
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

  AlertSeverity _parseSeverity(String? value) {
    switch (value) {
      case 'critical':
        return AlertSeverity.critical;
      case 'warning':
        return AlertSeverity.warning;
      case 'success':
        return AlertSeverity.success;
      default:
        return AlertSeverity.info;
    }
  }

  AlertActionType _parseActionType(String? value) {
    switch (value) {
      case 'irrigate':
        return AlertActionType.irrigate;
      case 'inspect':
        return AlertActionType.inspect;
      case 'createTask':
        return AlertActionType.createTask;
      case 'dismiss':
        return AlertActionType.dismiss;
      default:
        return AlertActionType.viewDetails;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Mock / offline fallback data
  // ─────────────────────────────────────────────────────────────────────────

  List<SmartAlert> _buildMockAlerts() {
    return const [
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
  }
}

// =============================================================================
// Providers
// =============================================================================

final smartAlertsRepositoryProvider = Provider<SmartAlertsRepository>((ref) {
  return SmartAlertsRepository();
});

/// Main smart alerts provider - tries API first, falls back to mock
/// يحاول جلب البيانات من API أولاً ثم يرجع للبيانات المحلية
/// Uses autoDispose to clean up when no longer watched
final smartAlertsProvider =
    FutureProvider.autoDispose<List<SmartAlert>>((ref) async {
  final repository = ref.read(smartAlertsRepositoryProvider);
  return repository.fetchAlerts();
});

/// Stream provider for real-time alerts
/// Uses autoDispose to clean up subscription when no longer watched
final alertsStreamProvider =
    StreamProvider.autoDispose<List<SmartAlert>>((ref) async* {
  // Initial data from API or fallback
  yield await ref.read(smartAlertsProvider.future);

  // Would connect to WebSocket in production for real-time updates:
  // final wsUrl = ApiConfig.effectiveBaseUrl
  //     .replaceFirst('http', 'ws') + '/ws/alerts';
  // final channel = WebSocketChannel.connect(Uri.parse(wsUrl));
  // await for (final message in channel.stream) { yield parseAlerts(message); }
});

// =============================================================================
// Models
// =============================================================================

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
