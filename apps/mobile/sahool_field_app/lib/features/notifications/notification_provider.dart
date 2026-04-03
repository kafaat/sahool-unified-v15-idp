library;

/// SAHOOL Notification Provider
/// مزود الإشعارات المخصصة - Riverpod State Management
///
/// Features:
/// - Real-time notifications
/// - Push notifications integration
/// - Personalized alerts based on farmer profile
/// - Unread count badge

import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;

// =============================================================================
// Models
// =============================================================================

/// أنواع الإشعارات
enum NotificationType {
  weatherAlert,
  pestOutbreak,
  irrigationReminder,
  cropHealth,
  marketPrice,
  system,
  taskReminder,
}

/// أولوية الإشعار
enum NotificationPriority {
  low,
  medium,
  high,
  critical,
}

/// الإشعار
class AppNotification {
  final String id;
  final NotificationType type;
  final String typeAr;
  final NotificationPriority priority;
  final String priorityAr;
  final String title;
  final String titleAr;
  final String body;
  final String bodyAr;
  final Map<String, dynamic> data;
  final DateTime createdAt;
  final DateTime? expiresAt;
  final bool isRead;
  final String? actionUrl;

  const AppNotification({
    required this.id,
    required this.type,
    required this.typeAr,
    required this.priority,
    required this.priorityAr,
    required this.title,
    required this.titleAr,
    required this.body,
    required this.bodyAr,
    this.data = const {},
    required this.createdAt,
    this.expiresAt,
    this.isRead = false,
    this.actionUrl,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] as String,
      type: _parseNotificationType(json['type'] as String),
      typeAr: json['type_ar'] as String? ?? '',
      priority: _parsePriority(json['priority'] as String),
      priorityAr: json['priority_ar'] as String? ?? '',
      title: json['title'] as String,
      titleAr: json['title_ar'] as String? ?? '',
      body: json['body'] as String,
      bodyAr: json['body_ar'] as String? ?? '',
      data: Map<String, dynamic>.from(json['data'] as Map? ?? {}),
      createdAt: DateTime.parse(json['created_at'] as String),
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'] as String)
          : null,
      isRead: json['is_read'] as bool? ?? false,
      actionUrl: json['action_url'] as String?,
    );
  }

  static NotificationType _parseNotificationType(String type) {
    switch (type) {
      case 'weather_alert':
        return NotificationType.weatherAlert;
      case 'pest_outbreak':
        return NotificationType.pestOutbreak;
      case 'irrigation_reminder':
        return NotificationType.irrigationReminder;
      case 'crop_health':
        return NotificationType.cropHealth;
      case 'market_price':
        return NotificationType.marketPrice;
      case 'task_reminder':
        return NotificationType.taskReminder;
      default:
        return NotificationType.system;
    }
  }

  static NotificationPriority _parsePriority(String priority) {
    switch (priority) {
      case 'critical':
        return NotificationPriority.critical;
      case 'high':
        return NotificationPriority.high;
      case 'medium':
        return NotificationPriority.medium;
      default:
        return NotificationPriority.low;
    }
  }

  AppNotification copyWith({bool? isRead}) {
    return AppNotification(
      id: id,
      type: type,
      typeAr: typeAr,
      priority: priority,
      priorityAr: priorityAr,
      title: title,
      titleAr: titleAr,
      body: body,
      bodyAr: bodyAr,
      data: data,
      createdAt: createdAt,
      expiresAt: expiresAt,
      isRead: isRead ?? this.isRead,
      actionUrl: actionUrl,
    );
  }

  /// الحصول على أيقونة الإشعار
  String get icon {
    switch (type) {
      case NotificationType.weatherAlert:
        return '🌤️';
      case NotificationType.pestOutbreak:
        return '🐛';
      case NotificationType.irrigationReminder:
        return '💧';
      case NotificationType.cropHealth:
        return '🌱';
      case NotificationType.marketPrice:
        return '💰';
      case NotificationType.taskReminder:
        return '📋';
      case NotificationType.system:
        return '⚙️';
    }
  }

  /// هل الإشعار عاجل؟
  bool get isUrgent =>
      priority == NotificationPriority.critical ||
      priority == NotificationPriority.high;
}

// =============================================================================
// State
// =============================================================================

/// حالة الإشعارات
class NotificationState {
  final List<AppNotification> notifications;
  final bool isLoading;
  final String? error;
  final int unreadCount;

  const NotificationState({
    this.notifications = const [],
    this.isLoading = false,
    this.error,
    this.unreadCount = 0,
  });

  NotificationState copyWith({
    List<AppNotification>? notifications,
    bool? isLoading,
    String? error,
    int? unreadCount,
  }) {
    return NotificationState(
      notifications: notifications ?? this.notifications,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      unreadCount: unreadCount ?? this.unreadCount,
    );
  }
}

// =============================================================================
// Provider
// =============================================================================

/// مزود الإشعارات
class NotificationNotifier extends StateNotifier<NotificationState> {
  final String _baseUrl;
  final String _farmerId;
  Timer? _refreshTimer;

  NotificationNotifier({
    required String baseUrl,
    required String farmerId,
  })  : _baseUrl = baseUrl,
        _farmerId = farmerId,
        super(const NotificationState()) {
    _startAutoRefresh();
  }

  /// جلب الإشعارات
  Future<void> fetchNotifications({bool unreadOnly = false}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final queryParams = {
        if (unreadOnly) 'unread_only': 'true',
        'limit': '50',
      };

      final uri = Uri.parse(
        '$_baseUrl/v1/notifications/farmer/$_farmerId',
      ).replace(queryParameters: queryParams);

      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final notificationsList = data['notifications'] as List<dynamic>;
        final notifications = notificationsList
            .map((json) =>
                AppNotification.fromJson(json as Map<String, dynamic>))
            .toList();

        state = state.copyWith(
          notifications: notifications,
          unreadCount: data['unread_count'] as int? ?? 0,
          isLoading: false,
        );
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'فشل في جلب الإشعارات',
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'خطأ في الاتصال: ${e.toString()}',
      );
    }
  }

  /// تحديد إشعار كمقروء
  Future<void> markAsRead(String notificationId) async {
    try {
      final uri = Uri.parse(
        '$_baseUrl/v1/notifications/$notificationId/read?farmer_id=$_farmerId',
      );

      final response = await http.patch(uri);

      if (response.statusCode == 200) {
        final updatedNotifications = state.notifications.map((n) {
          if (n.id == notificationId) {
            return n.copyWith(isRead: true);
          }
          return n;
        }).toList();

        state = state.copyWith(
          notifications: updatedNotifications,
          unreadCount: state.unreadCount > 0 ? state.unreadCount - 1 : 0,
        );
      }
    } catch (e) {
      // صمت - لا تظهر خطأ للمستخدم
    }
  }

  /// تحديد جميع الإشعارات كمقروءة
  Future<void> markAllAsRead() async {
    final unreadIds =
        state.notifications.where((n) => !n.isRead).map((n) => n.id).toList();

    for (final id in unreadIds) {
      await markAsRead(id);
    }
  }

  /// تحديث تلقائي
  void _startAutoRefresh() {
    _refreshTimer?.cancel();
    _refreshTimer = Timer.periodic(
      const Duration(minutes: 2),
      (_) => fetchNotifications(),
    );
    // جلب فوري
    fetchNotifications();
  }

  /// الحصول على الإشعارات العاجلة
  List<AppNotification> get urgentNotifications =>
      state.notifications.where((n) => n.isUrgent && !n.isRead).toList();

  /// الحصول على إشعارات حسب النوع
  List<AppNotification> getByType(NotificationType type) =>
      state.notifications.where((n) => n.type == type).toList();

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }
}

// =============================================================================
// Riverpod Providers
// =============================================================================

/// مزود معرف المزارع (يجب تعريفه في التطبيق)
final farmerIdProvider = StateProvider<String>((ref) => '');

/// مزود رابط API
final apiBaseUrlProvider = Provider<String>((ref) {
  // يمكن تغييره حسب البيئة
  const isProduction = bool.fromEnvironment('dart.vm.product');
  return isProduction ? 'https://api.sahool.io' : 'http://localhost:8109';
});

/// مزود الإشعارات الرئيسي
final notificationProvider =
    StateNotifierProvider<NotificationNotifier, NotificationState>((ref) {
  final baseUrl = ref.watch(apiBaseUrlProvider);
  final farmerId = ref.watch(farmerIdProvider);

  return NotificationNotifier(
    baseUrl: baseUrl,
    farmerId: farmerId,
  );
});

/// عدد الإشعارات غير المقروءة
final unreadCountProvider = Provider<int>((ref) {
  return ref.watch(notificationProvider).unreadCount;
});

/// الإشعارات العاجلة
final urgentNotificationsProvider = Provider<List<AppNotification>>((ref) {
  final notifier = ref.read(notificationProvider.notifier);
  return notifier.urgentNotifications;
});

/// إشعارات الطقس
final weatherAlertsProvider = Provider<List<AppNotification>>((ref) {
  final state = ref.watch(notificationProvider);
  return state.notifications
      .where((n) => n.type == NotificationType.weatherAlert)
      .toList();
});

/// تذكيرات الري
final irrigationRemindersProvider = Provider<List<AppNotification>>((ref) {
  final state = ref.watch(notificationProvider);
  return state.notifications
      .where((n) => n.type == NotificationType.irrigationReminder)
      .toList();
});
