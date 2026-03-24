/// SAHOOL Notifications API
/// واجهة برمجة الإشعارات
///
/// Handles API communication for notifications
/// including fetching, updating status, and actions
library;

import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../domain/models/notification.dart';
import '../domain/models/notification_category.dart';

/// Notifications API client
class NotificationsApi {
  final Dio _dio;
  final String _baseUrl;

  NotificationsApi({
    required Dio dio,
    String baseUrl = '/api/v1/notifications',
  })  : _dio = dio,
        _baseUrl = baseUrl;

  // ─────────────────────────────────────────────────────────────────────────────
  // Fetch Notifications
  // ─────────────────────────────────────────────────────────────────────────────

  /// Fetch all notifications with optional filters
  Future<NotificationsResponse> getNotifications({
    NotificationCategory? category,
    NotificationStatus? status,
    int page = 1,
    int limit = 50,
    DateTime? since,
    DateTime? until,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'limit': limit,
      };

      if (category != null) {
        queryParams['category'] = category.name;
      }
      if (status != null) {
        queryParams['status'] = status.name;
      }
      if (since != null) {
        queryParams['since'] = since.toIso8601String();
      }
      if (until != null) {
        queryParams['until'] = until.toIso8601String();
      }

      final response = await _dio.get(
        _baseUrl,
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        return NotificationsResponse.fromJson(
          response.data as Map<String, dynamic>,
        );
      }

      throw NotificationsApiException(
        'Failed to fetch notifications',
        response.statusCode,
      );
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  /// Fetch unread count
  Future<UnreadCountResponse> getUnreadCount() async {
    try {
      final response = await _dio.get('$_baseUrl/unread-count');

      if (response.statusCode == 200) {
        return UnreadCountResponse.fromJson(
          response.data as Map<String, dynamic>,
        );
      }

      throw NotificationsApiException(
        'Failed to fetch unread count',
        response.statusCode,
      );
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  /// Fetch a single notification by ID
  Future<AppNotification> getNotification(String id) async {
    try {
      final response = await _dio.get('$_baseUrl/$id');

      if (response.statusCode == 200) {
        return AppNotification.fromJson(
          response.data as Map<String, dynamic>,
        );
      }

      throw NotificationsApiException(
        'Failed to fetch notification',
        response.statusCode,
      );
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Update Notifications
  // ─────────────────────────────────────────────────────────────────────────────

  /// Mark notification as read
  Future<AppNotification> markAsRead(String id) async {
    try {
      final response = await _dio.patch(
        '$_baseUrl/$id/read',
      );

      if (response.statusCode == 200) {
        return AppNotification.fromJson(
          response.data as Map<String, dynamic>,
        );
      }

      throw NotificationsApiException(
        'Failed to mark notification as read',
        response.statusCode,
      );
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  /// Mark notification as unread
  Future<AppNotification> markAsUnread(String id) async {
    try {
      final response = await _dio.patch(
        '$_baseUrl/$id/unread',
      );

      if (response.statusCode == 200) {
        return AppNotification.fromJson(
          response.data as Map<String, dynamic>,
        );
      }

      throw NotificationsApiException(
        'Failed to mark notification as unread',
        response.statusCode,
      );
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  /// Mark all notifications as read
  Future<void> markAllAsRead({NotificationCategory? category}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (category != null) {
        queryParams['category'] = category.name;
      }

      final response = await _dio.patch(
        '$_baseUrl/read-all',
        queryParameters: queryParams,
      );

      if (response.statusCode != 200) {
        throw NotificationsApiException(
          'Failed to mark all notifications as read',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  /// Archive a notification
  Future<AppNotification> archiveNotification(String id) async {
    try {
      final response = await _dio.patch(
        '$_baseUrl/$id/archive',
      );

      if (response.statusCode == 200) {
        return AppNotification.fromJson(
          response.data as Map<String, dynamic>,
        );
      }

      throw NotificationsApiException(
        'Failed to archive notification',
        response.statusCode,
      );
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  /// Delete a notification
  Future<void> deleteNotification(String id) async {
    try {
      final response = await _dio.delete('$_baseUrl/$id');

      if (response.statusCode != 200 && response.statusCode != 204) {
        throw NotificationsApiException(
          'Failed to delete notification',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  /// Delete multiple notifications
  Future<void> deleteNotifications(List<String> ids) async {
    try {
      final response = await _dio.delete(
        '$_baseUrl/batch',
        data: jsonEncode({'ids': ids}),
      );

      if (response.statusCode != 200 && response.statusCode != 204) {
        throw NotificationsApiException(
          'Failed to delete notifications',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  /// Snooze a notification
  Future<AppNotification> snoozeNotification(
    String id, {
    required int durationMinutes,
  }) async {
    try {
      final response = await _dio.patch(
        '$_baseUrl/$id/snooze',
        data: jsonEncode({'duration_minutes': durationMinutes}),
      );

      if (response.statusCode == 200) {
        return AppNotification.fromJson(
          response.data as Map<String, dynamic>,
        );
      }

      throw NotificationsApiException(
        'Failed to snooze notification',
        response.statusCode,
      );
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Actions
  // ─────────────────────────────────────────────────────────────────────────────

  /// Execute a notification action
  Future<ActionResponse> executeAction(
    String notificationId,
    String actionId, {
    Map<String, dynamic>? params,
  }) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/$notificationId/actions/$actionId',
        data: params != null ? jsonEncode(params) : null,
      );

      if (response.statusCode == 200) {
        return ActionResponse.fromJson(
          response.data as Map<String, dynamic>,
        );
      }

      throw NotificationsApiException(
        'Failed to execute action',
        response.statusCode,
      );
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Device Token
  // ─────────────────────────────────────────────────────────────────────────────

  /// Register device token for push notifications
  Future<void> registerDeviceToken({
    required String token,
    required String platform,
    String? deviceId,
  }) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/devices',
        data: jsonEncode({
          'token': token,
          'platform': platform,
          'device_id': deviceId,
        }),
      );

      if (response.statusCode != 200 && response.statusCode != 201) {
        throw NotificationsApiException(
          'Failed to register device token',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }

  /// Unregister device token
  Future<void> unregisterDeviceToken(String token) async {
    try {
      final response = await _dio.delete(
        '$_baseUrl/devices/$token',
      );

      if (response.statusCode != 200 && response.statusCode != 204) {
        throw NotificationsApiException(
          'Failed to unregister device token',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      debugPrint('NotificationsApi error: ${e.message}');
      throw NotificationsApiException(
        e.message ?? 'Network error',
        e.response?.statusCode,
      );
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Response Models
// ─────────────────────────────────────────────────────────────────────────────

/// Response for notifications list
class NotificationsResponse {
  final List<AppNotification> notifications;
  final int total;
  final int page;
  final int limit;
  final bool hasMore;

  const NotificationsResponse({
    required this.notifications,
    required this.total,
    required this.page,
    required this.limit,
    required this.hasMore,
  });

  factory NotificationsResponse.fromJson(Map<String, dynamic> json) {
    return NotificationsResponse(
      notifications: (json['data'] as List<dynamic>?)
              ?.map((e) => AppNotification.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      total: json['total'] as int? ?? 0,
      page: json['page'] as int? ?? 1,
      limit: json['limit'] as int? ?? 50,
      hasMore: json['has_more'] as bool? ?? false,
    );
  }
}

/// Response for unread count
class UnreadCountResponse {
  final int total;
  final Map<NotificationCategory, int> byCategory;

  const UnreadCountResponse({
    required this.total,
    required this.byCategory,
  });

  factory UnreadCountResponse.fromJson(Map<String, dynamic> json) {
    final byCategory = <NotificationCategory, int>{};

    final categoryCounts = json['by_category'] as Map<String, dynamic>?;
    if (categoryCounts != null) {
      for (final entry in categoryCounts.entries) {
        final category = NotificationCategoryExtension.fromString(entry.key);
        if (category != null) {
          byCategory[category] = entry.value as int;
        }
      }
    }

    return UnreadCountResponse(
      total: json['total'] as int? ?? 0,
      byCategory: byCategory,
    );
  }
}

/// Response for action execution
class ActionResponse {
  final bool success;
  final String? message;
  final String? redirectUrl;
  final Map<String, dynamic>? data;

  const ActionResponse({
    required this.success,
    this.message,
    this.redirectUrl,
    this.data,
  });

  factory ActionResponse.fromJson(Map<String, dynamic> json) {
    return ActionResponse(
      success: json['success'] as bool? ?? true,
      message: json['message'] as String?,
      redirectUrl: json['redirect_url'] as String?,
      data: json['data'] as Map<String, dynamic>?,
    );
  }
}

/// API Exception
class NotificationsApiException implements Exception {
  final String message;
  final int? statusCode;

  NotificationsApiException(this.message, [this.statusCode]);

  @override
  String toString() => 'NotificationsApiException: $message (code: $statusCode)';
}
