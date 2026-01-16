import 'package:dio/dio.dart';
import '../../../core/config/api_config.dart';

/// Notifications Service API Integration
/// تكامل خدمة الإشعارات
///
/// Routes through Kong Gateway on port 8000
/// Features: Push notifications, in-app notifications, preferences
class NotificationsApi {
  final Dio _dio;
  final String _baseUrl;

  NotificationsApi({Dio? dio, String? baseUrl})
      : _dio = dio ?? Dio(),
        _baseUrl = baseUrl ?? '${ApiConfig.baseUrl}/api/v1/notifications';

  // ─────────────────────────────────────────────────────────────────────────
  // Notifications - الإشعارات
  // ─────────────────────────────────────────────────────────────────────────

  /// Get user notifications
  /// جلب إشعارات المستخدم
  Future<ApiResult<NotificationList>> getNotifications({
    int page = 1,
    int limit = 20,
    bool? unreadOnly,
    String? category,
  }) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/notifications',
        queryParameters: {
          'page': page,
          'limit': limit,
          if (unreadOnly != null) 'unread_only': unreadOnly,
          if (category != null) 'category': category,
        },
      );
      return ApiResult.success(NotificationList.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get unread count
  /// جلب عدد الإشعارات غير المقروءة
  Future<ApiResult<int>> getUnreadCount() async {
    try {
      final response = await _dio.get('$_baseUrl/notifications/unread/count');
      return ApiResult.success(response.data['count'] ?? 0);
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Mark notification as read
  /// تحديد الإشعار كمقروء
  Future<ApiResult<bool>> markAsRead(String notificationId) async {
    try {
      await _dio.post('$_baseUrl/notifications/$notificationId/read');
      return ApiResult.success(true);
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Mark all notifications as read
  /// تحديد جميع الإشعارات كمقروءة
  Future<ApiResult<int>> markAllAsRead() async {
    try {
      final response = await _dio.post('$_baseUrl/notifications/read-all');
      return ApiResult.success(response.data['count'] ?? 0);
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Delete notification
  /// حذف إشعار
  Future<ApiResult<bool>> deleteNotification(String notificationId) async {
    try {
      await _dio.delete('$_baseUrl/notifications/$notificationId');
      return ApiResult.success(true);
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Clear all notifications
  /// مسح جميع الإشعارات
  Future<ApiResult<int>> clearAll() async {
    try {
      final response = await _dio.delete('$_baseUrl/notifications/clear-all');
      return ApiResult.success(response.data['count'] ?? 0);
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Push Notifications - إشعارات الدفع
  // ─────────────────────────────────────────────────────────────────────────

  /// Register FCM token
  /// تسجيل رمز FCM
  Future<ApiResult<bool>> registerFcmToken({
    required String token,
    required String platform, // 'android', 'ios'
    String? deviceId,
  }) async {
    try {
      await _dio.post(
        '$_baseUrl/push/register',
        data: {
          'token': token,
          'platform': platform,
          if (deviceId != null) 'device_id': deviceId,
        },
      );
      return ApiResult.success(true);
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Unregister FCM token
  /// إلغاء تسجيل رمز FCM
  Future<ApiResult<bool>> unregisterFcmToken(String token) async {
    try {
      await _dio.post(
        '$_baseUrl/push/unregister',
        data: {'token': token},
      );
      return ApiResult.success(true);
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Preferences - التفضيلات
  // ─────────────────────────────────────────────────────────────────────────

  /// Get notification preferences
  /// جلب تفضيلات الإشعارات
  Future<ApiResult<NotificationPreferences>> getPreferences() async {
    try {
      final response = await _dio.get('$_baseUrl/preferences');
      return ApiResult.success(NotificationPreferences.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Update notification preferences
  /// تحديث تفضيلات الإشعارات
  Future<ApiResult<NotificationPreferences>> updatePreferences(
    NotificationPreferences prefs,
  ) async {
    try {
      final response = await _dio.put(
        '$_baseUrl/preferences',
        data: prefs.toJson(),
      );
      return ApiResult.success(NotificationPreferences.fromJson(response.data));
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Toggle category notifications
  /// تبديل إشعارات فئة معينة
  Future<ApiResult<bool>> toggleCategory({
    required String category,
    required bool enabled,
  }) async {
    try {
      await _dio.post(
        '$_baseUrl/preferences/category',
        data: {
          'category': category,
          'enabled': enabled,
        },
      );
      return ApiResult.success(true);
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Subscriptions - الاشتراكات
  // ─────────────────────────────────────────────────────────────────────────

  /// Subscribe to field notifications
  /// الاشتراك في إشعارات الحقل
  Future<ApiResult<bool>> subscribeToField(String fieldId) async {
    try {
      await _dio.post('$_baseUrl/subscriptions/fields/$fieldId');
      return ApiResult.success(true);
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Unsubscribe from field notifications
  /// إلغاء الاشتراك من إشعارات الحقل
  Future<ApiResult<bool>> unsubscribeFromField(String fieldId) async {
    try {
      await _dio.delete('$_baseUrl/subscriptions/fields/$fieldId');
      return ApiResult.success(true);
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  /// Get subscribed fields
  /// جلب الحقول المشترك فيها
  Future<ApiResult<List<String>>> getSubscribedFields() async {
    try {
      final response = await _dio.get('$_baseUrl/subscriptions/fields');
      return ApiResult.success(
        List<String>.from(response.data['field_ids'] ?? []),
      );
    } on DioException catch (e) {
      return ApiResult.failure(_handleError(e));
    }
  }

  String _handleError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.receiveTimeout:
        return 'انتهت مهلة الاتصال بخدمة الإشعارات';
      case DioExceptionType.connectionError:
        return 'لا يمكن الاتصال بخدمة الإشعارات';
      default:
        return 'حدث خطأ في خدمة الإشعارات';
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Data Models
// ─────────────────────────────────────────────────────────────────────────────

class ApiResult<T> {
  final T? data;
  final String? error;
  final bool isSuccess;

  ApiResult._({this.data, this.error, required this.isSuccess});

  factory ApiResult.success(T data) => ApiResult._(data: data, isSuccess: true);
  factory ApiResult.failure(String error) => ApiResult._(error: error, isSuccess: false);
}

/// Notification list with pagination
class NotificationList {
  final List<AppNotification> notifications;
  final int total;
  final int unreadCount;
  final int page;
  final int totalPages;

  NotificationList({
    required this.notifications,
    required this.total,
    required this.unreadCount,
    required this.page,
    required this.totalPages,
  });

  factory NotificationList.fromJson(Map<String, dynamic> json) {
    return NotificationList(
      notifications: (json['notifications'] as List<dynamic>?)
              ?.map((e) => AppNotification.fromJson(e))
              .toList() ??
          [],
      total: json['total'] ?? 0,
      unreadCount: json['unread_count'] ?? 0,
      page: json['page'] ?? 1,
      totalPages: json['total_pages'] ?? 1,
    );
  }
}

/// App notification
class AppNotification {
  final String id;
  final String title;
  final String body;
  final String category; // weather, task, alert, irrigation, crop_health, system
  final String priority; // low, normal, high, urgent
  final bool isRead;
  final DateTime createdAt;
  final String? actionType;
  final Map<String, dynamic>? data;
  final String? imageUrl;

  AppNotification({
    required this.id,
    required this.title,
    required this.body,
    required this.category,
    required this.priority,
    required this.isRead,
    required this.createdAt,
    this.actionType,
    this.data,
    this.imageUrl,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      body: json['body'] ?? '',
      category: json['category'] ?? 'system',
      priority: json['priority'] ?? 'normal',
      isRead: json['is_read'] ?? false,
      createdAt: DateTime.parse(
        json['created_at'] ?? DateTime.now().toIso8601String(),
      ),
      actionType: json['action_type'],
      data: json['data'],
      imageUrl: json['image_url'],
    );
  }

  String get categoryAr {
    switch (category) {
      case 'weather':
        return 'الطقس';
      case 'task':
        return 'المهام';
      case 'alert':
        return 'التنبيهات';
      case 'irrigation':
        return 'الري';
      case 'crop_health':
        return 'صحة المحصول';
      case 'system':
        return 'النظام';
      case 'marketplace':
        return 'السوق';
      case 'payment':
        return 'المدفوعات';
      default:
        return category;
    }
  }

  String get categoryIcon {
    switch (category) {
      case 'weather':
        return '🌤️';
      case 'task':
        return '📋';
      case 'alert':
        return '⚠️';
      case 'irrigation':
        return '💧';
      case 'crop_health':
        return '🌱';
      case 'system':
        return '⚙️';
      case 'marketplace':
        return '🛒';
      case 'payment':
        return '💳';
      default:
        return '📬';
    }
  }
}

/// Notification preferences
class NotificationPreferences {
  final bool pushEnabled;
  final bool emailEnabled;
  final bool smsEnabled;
  final Map<String, bool> categories;
  final QuietHours? quietHours;
  final String language; // 'ar', 'en'

  NotificationPreferences({
    required this.pushEnabled,
    required this.emailEnabled,
    required this.smsEnabled,
    required this.categories,
    this.quietHours,
    required this.language,
  });

  factory NotificationPreferences.fromJson(Map<String, dynamic> json) {
    return NotificationPreferences(
      pushEnabled: json['push_enabled'] ?? true,
      emailEnabled: json['email_enabled'] ?? false,
      smsEnabled: json['sms_enabled'] ?? false,
      categories: Map<String, bool>.from(json['categories'] ?? {}),
      quietHours: json['quiet_hours'] != null
          ? QuietHours.fromJson(json['quiet_hours'])
          : null,
      language: json['language'] ?? 'ar',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'push_enabled': pushEnabled,
      'email_enabled': emailEnabled,
      'sms_enabled': smsEnabled,
      'categories': categories,
      if (quietHours != null) 'quiet_hours': quietHours!.toJson(),
      'language': language,
    };
  }
}

/// Quiet hours configuration
class QuietHours {
  final bool enabled;
  final String startTime; // HH:mm
  final String endTime; // HH:mm

  QuietHours({
    required this.enabled,
    required this.startTime,
    required this.endTime,
  });

  factory QuietHours.fromJson(Map<String, dynamic> json) {
    return QuietHours(
      enabled: json['enabled'] ?? false,
      startTime: json['start_time'] ?? '22:00',
      endTime: json['end_time'] ?? '07:00',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'start_time': startTime,
      'end_time': endTime,
    };
  }
}
