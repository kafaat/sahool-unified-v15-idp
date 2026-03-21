/// SAHOOL Notification Service Integration
/// تكامل خدمة الإشعارات
///
/// Handles notification-related operations:
/// - Notification listing
/// - Preferences management
/// - Subscribe/unsubscribe
/// - Mark as read
/// - Push notification registration
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../network/api_result.dart';
import '../service_connector.dart';

/// Notification priority levels
enum NotificationPriority { low, normal, high, critical }

/// Notification model
class AppNotification {
  final String id;
  final String type;
  final String title;
  final String? titleAr;
  final String? body;
  final String? bodyAr;
  final NotificationPriority priority;
  final bool isRead;
  final DateTime createdAt;
  final DateTime? readAt;
  final String? actionUrl;
  final String? actionType;
  final Map<String, dynamic>? data;
  final Map<String, dynamic>? metadata;

  const AppNotification({
    required this.id,
    required this.type,
    required this.title,
    this.titleAr,
    this.body,
    this.bodyAr,
    this.priority = NotificationPriority.normal,
    this.isRead = false,
    required this.createdAt,
    this.readAt,
    this.actionUrl,
    this.actionType,
    this.data,
    this.metadata,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] as String? ?? '',
      type: json['type'] as String? ?? 'general',
      title: json['title'] as String? ?? '',
      titleAr: json['title_ar'] as String?,
      body: json['body'] as String?,
      bodyAr: json['body_ar'] as String?,
      priority: _parsePriority(json['priority'] as String?),
      isRead: json['is_read'] as bool? ?? false,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      readAt: json['read_at'] != null ? DateTime.tryParse(json['read_at'] as String) : null,
      actionUrl: json['action_url'] as String?,
      actionType: json['action_type'] as String?,
      data: json['data'] as Map<String, dynamic>?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  static NotificationPriority _parsePriority(String? priority) {
    switch (priority?.toLowerCase()) {
      case 'low':
        return NotificationPriority.low;
      case 'high':
        return NotificationPriority.high;
      case 'critical':
        return NotificationPriority.critical;
      default:
        return NotificationPriority.normal;
    }
  }

  AppNotification copyWith({
    bool? isRead,
    DateTime? readAt,
  }) {
    return AppNotification(
      id: id,
      type: type,
      title: title,
      titleAr: titleAr,
      body: body,
      bodyAr: bodyAr,
      priority: priority,
      isRead: isRead ?? this.isRead,
      createdAt: createdAt,
      readAt: readAt ?? this.readAt,
      actionUrl: actionUrl,
      actionType: actionType,
      data: data,
      metadata: metadata,
    );
  }
}

/// Notification preferences model
class NotificationPreferences {
  final bool pushEnabled;
  final bool emailEnabled;
  final bool smsEnabled;
  final Map<String, bool> categories;
  final String? quietHoursStart;
  final String? quietHoursEnd;
  final List<String>? disabledTypes;

  const NotificationPreferences({
    this.pushEnabled = true,
    this.emailEnabled = true,
    this.smsEnabled = false,
    this.categories = const {},
    this.quietHoursStart,
    this.quietHoursEnd,
    this.disabledTypes,
  });

  factory NotificationPreferences.fromJson(Map<String, dynamic> json) {
    return NotificationPreferences(
      pushEnabled: json['push_enabled'] as bool? ?? true,
      emailEnabled: json['email_enabled'] as bool? ?? true,
      smsEnabled: json['sms_enabled'] as bool? ?? false,
      categories: (json['categories'] as Map<String, dynamic>?)?.map(
            (key, value) => MapEntry(key, value as bool),
          ) ??
          {},
      quietHoursStart: json['quiet_hours_start'] as String?,
      quietHoursEnd: json['quiet_hours_end'] as String?,
      disabledTypes: (json['disabled_types'] as List?)?.cast<String>(),
    );
  }

  Map<String, dynamic> toJson() => {
        'push_enabled': pushEnabled,
        'email_enabled': emailEnabled,
        'sms_enabled': smsEnabled,
        'categories': categories,
        if (quietHoursStart != null) 'quiet_hours_start': quietHoursStart,
        if (quietHoursEnd != null) 'quiet_hours_end': quietHoursEnd,
        if (disabledTypes != null) 'disabled_types': disabledTypes,
      };

  NotificationPreferences copyWith({
    bool? pushEnabled,
    bool? emailEnabled,
    bool? smsEnabled,
    Map<String, bool>? categories,
    String? quietHoursStart,
    String? quietHoursEnd,
    List<String>? disabledTypes,
  }) {
    return NotificationPreferences(
      pushEnabled: pushEnabled ?? this.pushEnabled,
      emailEnabled: emailEnabled ?? this.emailEnabled,
      smsEnabled: smsEnabled ?? this.smsEnabled,
      categories: categories ?? this.categories,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
      disabledTypes: disabledTypes ?? this.disabledTypes,
    );
  }
}

/// Notification subscription model
class NotificationSubscription {
  final String topic;
  final String? topicAr;
  final bool isSubscribed;
  final DateTime? subscribedAt;

  const NotificationSubscription({
    required this.topic,
    this.topicAr,
    this.isSubscribed = false,
    this.subscribedAt,
  });

  factory NotificationSubscription.fromJson(Map<String, dynamic> json) {
    return NotificationSubscription(
      topic: json['topic'] as String? ?? '',
      topicAr: json['topic_ar'] as String?,
      isSubscribed: json['is_subscribed'] as bool? ?? false,
      subscribedAt: json['subscribed_at'] != null
          ? DateTime.tryParse(json['subscribed_at'] as String)
          : null,
    );
  }
}

/// Notification Service Connector
/// موصل خدمة الإشعارات
class NotificationServiceConnector extends ServiceConnector {
  NotificationServiceConnector({required super.ref}) : super(serviceId: 'notifications');

  /// Get notifications list
  /// الحصول على قائمة الإشعارات
  Future<ApiResult<List<AppNotification>>> getNotifications({
    int? page,
    int? limit,
    String? type,
    bool? unreadOnly,
  }) async {
    final queryParams = <String, dynamic>{
      if (page != null) 'page': page,
      if (limit != null) 'limit': limit,
      if (type != null) 'type': type,
      if (unreadOnly == true) 'unread_only': true,
    };

    return get(
      getEndpoint('list') ?? '/api/v1/notifications',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data.map((e) => AppNotification.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['notifications'] != null) {
          return (data['notifications'] as List)
              .map((e) => AppNotification.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        if (data is Map && data['data'] != null) {
          return (data['data'] as List)
              .map((e) => AppNotification.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <AppNotification>[];
      },
    );
  }

  /// Get notification by ID
  /// الحصول على إشعار بالمعرف
  Future<ApiResult<AppNotification>> getNotificationById(String notificationId) async {
    return get(
      '${getEndpoint('list') ?? '/api/v1/notifications'}/$notificationId',
      parser: (data) => AppNotification.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Mark notification as read
  /// تحديد الإشعار كمقروء
  Future<ApiResult<bool>> markAsRead(String notificationId) async {
    return post(
      getEndpoint('mark-read') ?? '/api/v1/notifications/mark-read',
      data: {'notification_id': notificationId},
      parser: (_) => true,
    );
  }

  /// Mark all notifications as read
  /// تحديد جميع الإشعارات كمقروءة
  Future<ApiResult<bool>> markAllAsRead() async {
    return post(
      getEndpoint('mark-read') ?? '/api/v1/notifications/mark-read',
      data: {'all': true},
      parser: (_) => true,
    );
  }

  /// Delete notification
  /// حذف إشعار
  Future<ApiResult<bool>> deleteNotification(String notificationId) async {
    return delete(
      '${getEndpoint('list') ?? '/api/v1/notifications'}/$notificationId',
      parser: (_) => true,
    );
  }

  /// Get unread count
  /// الحصول على عدد غير المقروءة
  Future<ApiResult<int>> getUnreadCount() async {
    return get(
      '${getEndpoint('list') ?? '/api/v1/notifications'}/unread-count',
      parser: (data) {
        if (data is int) return data;
        if (data is Map && data['count'] != null) {
          return (data['count'] as num).toInt();
        }
        return 0;
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Preferences Management
  // ═══════════════════════════════════════════════════════════════════════════════

  /// Get notification preferences
  /// الحصول على تفضيلات الإشعارات
  Future<ApiResult<NotificationPreferences>> getPreferences() async {
    return get(
      getEndpoint('preferences') ?? '/api/v1/notifications/preferences',
      parser: (data) => NotificationPreferences.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Update notification preferences
  /// تحديث تفضيلات الإشعارات
  Future<ApiResult<NotificationPreferences>> updatePreferences(
    NotificationPreferences preferences,
  ) async {
    return put(
      getEndpoint('preferences') ?? '/api/v1/notifications/preferences',
      data: preferences.toJson(),
      parser: (data) => NotificationPreferences.fromJson(data as Map<String, dynamic>),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Subscription Management
  // ═══════════════════════════════════════════════════════════════════════════════

  /// Subscribe to topic
  /// الاشتراك في موضوع
  Future<ApiResult<bool>> subscribe(String topic) async {
    return post(
      getEndpoint('subscribe') ?? '/api/v1/notifications/subscribe',
      data: {'topic': topic},
      parser: (_) => true,
    );
  }

  /// Subscribe to multiple topics
  /// الاشتراك في مواضيع متعددة
  Future<ApiResult<bool>> subscribeToTopics(List<String> topics) async {
    return post(
      getEndpoint('subscribe') ?? '/api/v1/notifications/subscribe',
      data: {'topics': topics},
      parser: (_) => true,
    );
  }

  /// Unsubscribe from topic
  /// إلغاء الاشتراك من موضوع
  Future<ApiResult<bool>> unsubscribe(String topic) async {
    return post(
      getEndpoint('unsubscribe') ?? '/api/v1/notifications/unsubscribe',
      data: {'topic': topic},
      parser: (_) => true,
    );
  }

  /// Unsubscribe from multiple topics
  /// إلغاء الاشتراك من مواضيع متعددة
  Future<ApiResult<bool>> unsubscribeFromTopics(List<String> topics) async {
    return post(
      getEndpoint('unsubscribe') ?? '/api/v1/notifications/unsubscribe',
      data: {'topics': topics},
      parser: (_) => true,
    );
  }

  /// Get subscriptions
  /// الحصول على الاشتراكات
  Future<ApiResult<List<NotificationSubscription>>> getSubscriptions() async {
    return get(
      '${getEndpoint('subscribe') ?? '/api/v1/notifications/subscribe'}/list',
      parser: (data) {
        if (data is List) {
          return data
              .map((e) => NotificationSubscription.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        if (data is Map && data['subscriptions'] != null) {
          return (data['subscriptions'] as List)
              .map((e) => NotificationSubscription.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <NotificationSubscription>[];
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Device Registration
  // ═══════════════════════════════════════════════════════════════════════════════

  /// Register device for push notifications
  /// تسجيل الجهاز للإشعارات الفورية
  Future<ApiResult<bool>> registerDevice({
    required String token,
    required String platform,
    String? deviceId,
    String? deviceName,
  }) async {
    return post(
      '/api/v1/notifications/device/register',
      data: {
        'token': token,
        'platform': platform,
        if (deviceId != null) 'device_id': deviceId,
        if (deviceName != null) 'device_name': deviceName,
      },
      parser: (_) => true,
    );
  }

  /// Unregister device
  /// إلغاء تسجيل الجهاز
  Future<ApiResult<bool>> unregisterDevice(String token) async {
    return post(
      '/api/v1/notifications/device/unregister',
      data: {'token': token},
      parser: (_) => true,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Notification Service Provider
final notificationServiceProvider = Provider<NotificationServiceConnector>((ref) {
  return NotificationServiceConnector(ref: ref);
});

/// Notifications List Provider
final notificationsProvider = FutureProvider<List<AppNotification>>((ref) async {
  final service = ref.watch(notificationServiceProvider);
  final result = await service.getNotifications();
  return result.dataOrNull ?? [];
});

/// Unread Notifications Provider
final unreadNotificationsProvider = FutureProvider<List<AppNotification>>((ref) async {
  final service = ref.watch(notificationServiceProvider);
  final result = await service.getNotifications(unreadOnly: true);
  return result.dataOrNull ?? [];
});

/// Unread Count Provider
final unreadCountProvider = FutureProvider<int>((ref) async {
  final service = ref.watch(notificationServiceProvider);
  final result = await service.getUnreadCount();
  return result.dataOrNull ?? 0;
});

/// Notification Preferences Provider
final notificationPreferencesProvider = FutureProvider<NotificationPreferences>((ref) async {
  final service = ref.watch(notificationServiceProvider);
  final result = await service.getPreferences();
  return result.dataOrNull ?? const NotificationPreferences();
});

/// Notification Subscriptions Provider
final notificationSubscriptionsProvider =
    FutureProvider<List<NotificationSubscription>>((ref) async {
  final service = ref.watch(notificationServiceProvider);
  final result = await service.getSubscriptions();
  return result.dataOrNull ?? [];
});

/// Has Unread Notifications Provider
final hasUnreadNotificationsProvider = FutureProvider<bool>((ref) async {
  final count = await ref.watch(unreadCountProvider.future);
  return count > 0;
});
