/// Notification API Client - Integrated with Notification Service (port 8110)
/// عميل API الإشعارات - متكامل مع خدمة الإشعارات
library;

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../../core/config/api_config.dart';

/// Notification Model for API
/// نموذج الإشعار للـ API
class ApiNotification {
  final String id;
  final String type;
  final String title;
  final String body;
  final Map<String, dynamic>? data;
  final bool isRead;
  final DateTime createdAt;
  final DateTime? readAt;

  ApiNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    this.data,
    this.isRead = false,
    required this.createdAt,
    this.readAt,
  });

  factory ApiNotification.fromJson(Map<String, dynamic> json) {
    return ApiNotification(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      body: json['body'] as String,
      data: json['data'] as Map<String, dynamic>?,
      isRead: json['is_read'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
      readAt: json['read_at'] != null
          ? DateTime.parse(json['read_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type,
        'title': title,
        'body': body,
        'data': data,
        'is_read': isRead,
        'created_at': createdAt.toIso8601String(),
        'read_at': readAt?.toIso8601String(),
      };
}

/// Notification Preferences Model
/// نموذج تفضيلات الإشعارات
class NotificationPreferences {
  final bool pushEnabled;
  final bool emailEnabled;
  final bool smsEnabled;
  final Map<String, bool> categories;

  NotificationPreferences({
    this.pushEnabled = true,
    this.emailEnabled = true,
    this.smsEnabled = false,
    this.categories = const {},
  });

  factory NotificationPreferences.fromJson(Map<String, dynamic> json) {
    return NotificationPreferences(
      pushEnabled: json['push_enabled'] as bool? ?? true,
      emailEnabled: json['email_enabled'] as bool? ?? true,
      smsEnabled: json['sms_enabled'] as bool? ?? false,
      categories: Map<String, bool>.from(json['categories'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() => {
        'push_enabled': pushEnabled,
        'email_enabled': emailEnabled,
        'sms_enabled': smsEnabled,
        'categories': categories,
      };
}

/// Notification API Exception
/// استثناء API الإشعارات
class NotificationApiException implements Exception {
  final String message;
  final int? statusCode;

  NotificationApiException(this.message, {this.statusCode});

  @override
  String toString() =>
      'NotificationApiException: $message (status: $statusCode)';
}

/// Notification API Client
/// عميل API الإشعارات
class NotificationApi {
  final http.Client _client;
  final String? _authToken;

  NotificationApi({
    http.Client? client,
    String? authToken,
  })  : _client = client ?? http.Client(),
        _authToken = authToken;

  Map<String, String> get _headers => {
        ...ApiConfig.defaultHeaders,
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Notifications CRUD
  // عمليات الإشعارات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get all notifications for the authenticated user
  /// جلب جميع الإشعارات للمستخدم
  Future<List<ApiNotification>> getNotifications({
    int? limit,
    int? offset,
    bool? unreadOnly,
    String? type,
  }) async {
    final uri = Uri.parse(ApiConfig.notifications).replace(
      queryParameters: {
        if (limit != null) 'limit': limit.toString(),
        if (offset != null) 'offset': offset.toString(),
        if (unreadOnly == true) 'unread_only': 'true',
        if (type != null) 'type': type,
      },
    );

    final response = await _client.get(uri, headers: _headers);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      final notifications = json['data'] as List;
      return notifications.map((n) => ApiNotification.fromJson(n)).toList();
    } else {
      throw NotificationApiException(
        'فشل جلب الإشعارات',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get a specific notification by ID
  /// جلب إشعار بالمعرف
  Future<ApiNotification> getNotification(String id) async {
    final response = await _client.get(
      Uri.parse(ApiConfig.notificationById(id)),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return ApiNotification.fromJson(json['data']);
    } else {
      throw NotificationApiException(
        'فشل جلب الإشعار',
        statusCode: response.statusCode,
      );
    }
  }

  /// Get unread notifications count
  /// جلب عدد الإشعارات غير المقروءة
  Future<int> getUnreadCount() async {
    final notifications = await getNotifications(unreadOnly: true, limit: 1000);
    return notifications.length;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Mark as Read
  // تعليم كمقروء
  // ═══════════════════════════════════════════════════════════════════════════

  /// Mark a notification as read
  /// تعليم إشعار كمقروء
  Future<void> markAsRead(String id) async {
    final response = await _client.put(
      Uri.parse('${ApiConfig.notificationById(id)}/read'),
      headers: _headers,
    );

    if (response.statusCode != 200 && response.statusCode != 204) {
      throw NotificationApiException(
        'فشل تعليم الإشعار كمقروء',
        statusCode: response.statusCode,
      );
    }
  }

  /// Mark all notifications as read
  /// تعليم جميع الإشعارات كمقروءة
  Future<void> markAllAsRead() async {
    final response = await _client.put(
      Uri.parse(ApiConfig.notificationMarkRead),
      headers: _headers,
      body: jsonEncode({'all': true}),
    );

    if (response.statusCode != 200 && response.statusCode != 204) {
      throw NotificationApiException(
        'فشل تعليم جميع الإشعارات كمقروءة',
        statusCode: response.statusCode,
      );
    }
  }

  /// Mark multiple notifications as read
  /// تعليم إشعارات متعددة كمقروءة
  Future<void> markMultipleAsRead(List<String> ids) async {
    final response = await _client.put(
      Uri.parse(ApiConfig.notificationMarkRead),
      headers: _headers,
      body: jsonEncode({'ids': ids}),
    );

    if (response.statusCode != 200 && response.statusCode != 204) {
      throw NotificationApiException(
        'فشل تعليم الإشعارات كمقروءة',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Push Subscription
  // الاشتراك في الإشعارات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Subscribe to push notifications with FCM token
  /// الاشتراك في الإشعارات بـ FCM token
  Future<void> subscribePush(String fcmToken, {String? deviceId}) async {
    final response = await _client.post(
      Uri.parse(ApiConfig.notificationSubscribe),
      headers: _headers,
      body: jsonEncode({
        'fcm_token': fcmToken,
        'platform': 'mobile',
        if (deviceId != null) 'device_id': deviceId,
      }),
    );

    if (response.statusCode != 200 && response.statusCode != 201) {
      throw NotificationApiException(
        'فشل الاشتراك في الإشعارات',
        statusCode: response.statusCode,
      );
    }
  }

  /// Unsubscribe from push notifications
  /// إلغاء الاشتراك من الإشعارات
  Future<void> unsubscribePush(String fcmToken) async {
    final response = await _client.post(
      Uri.parse(ApiConfig.notificationUnsubscribe),
      headers: _headers,
      body: jsonEncode({'fcm_token': fcmToken}),
    );

    if (response.statusCode != 200 && response.statusCode != 204) {
      throw NotificationApiException(
        'فشل إلغاء الاشتراك',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Preferences
  // التفضيلات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get notification preferences
  /// جلب تفضيلات الإشعارات
  Future<NotificationPreferences> getPreferences() async {
    final response = await _client.get(
      Uri.parse(ApiConfig.notificationPreferences),
      headers: _headers,
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return NotificationPreferences.fromJson(json['data']);
    } else {
      throw NotificationApiException(
        'فشل جلب تفضيلات الإشعارات',
        statusCode: response.statusCode,
      );
    }
  }

  /// Update notification preferences
  /// تحديث تفضيلات الإشعارات
  Future<NotificationPreferences> updatePreferences(
    NotificationPreferences preferences,
  ) async {
    final response = await _client.put(
      Uri.parse(ApiConfig.notificationPreferences),
      headers: _headers,
      body: jsonEncode(preferences.toJson()),
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return NotificationPreferences.fromJson(json['data']);
    } else {
      throw NotificationApiException(
        'فشل تحديث تفضيلات الإشعارات',
        statusCode: response.statusCode,
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Health Check
  // فحص الصحة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check notification service health
  /// فحص صحة خدمة الإشعارات
  Future<bool> checkHealth() async {
    try {
      final response = await _client.get(
        Uri.parse(ApiConfig.notificationsHealthz),
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
