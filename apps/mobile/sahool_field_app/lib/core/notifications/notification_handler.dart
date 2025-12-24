/// SAHOOL Notification Handler
/// معالج الإشعارات
///
/// Features:
/// - Handle notification tap actions
/// - Deep link to specific screens based on notification data
/// - Parse notification payload
/// - Route to appropriate screens using go_router

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:go_router/go_router.dart';

/// Notification action types
enum NotificationAction {
  openField,
  openTask,
  openAlert,
  openWeather,
  openIrrigation,
  openNdvi,
  openSync,
  openProfile,
  openAdvisor,
  none,
}

/// Notification Handler for managing notification tap actions and deep linking
class NotificationHandler {
  static final NotificationHandler _instance = NotificationHandler._internal();
  factory NotificationHandler() => _instance;
  NotificationHandler._internal();

  GoRouter? _router;

  /// تهيئة معالج الإشعارات مع الموجه
  void initialize(GoRouter router) {
    _router = router;
    debugPrint('✅ NotificationHandler initialized');
  }

  /// معالجة النقر على الإشعار
  Future<void> handleNotificationTap(Map<String, dynamic>? payload) async {
    if (payload == null) {
      debugPrint('⚠️ Notification payload is null');
      return;
    }

    if (_router == null) {
      debugPrint('⚠️ Router not initialized in NotificationHandler');
      return;
    }

    debugPrint('📱 Handling notification tap: $payload');

    try {
      final action = _parseAction(payload);
      final route = _getRouteForAction(action, payload);

      if (route != null) {
        debugPrint('🔗 Navigating to: $route');
        _router!.go(route);
      } else {
        debugPrint('⚠️ No route found for action: $action');
      }
    } catch (e) {
      debugPrint('❌ Error handling notification tap: $e');
    }
  }

  /// تحليل نوع الإجراء من البيانات
  NotificationAction _parseAction(Map<String, dynamic> payload) {
    final type = payload['type'] as String?;
    final action = payload['action'] as String?;

    // Check explicit action first
    if (action != null) {
      switch (action.toLowerCase()) {
        case 'open_field':
          return NotificationAction.openField;
        case 'open_task':
          return NotificationAction.openTask;
        case 'open_alert':
          return NotificationAction.openAlert;
        case 'open_weather':
          return NotificationAction.openWeather;
        case 'open_irrigation':
          return NotificationAction.openIrrigation;
        case 'open_ndvi':
          return NotificationAction.openNdvi;
        case 'open_sync':
          return NotificationAction.openSync;
        case 'open_profile':
          return NotificationAction.openProfile;
        case 'open_advisor':
          return NotificationAction.openAdvisor;
      }
    }

    // Fallback to type-based routing
    if (type != null) {
      switch (type.toLowerCase()) {
        case 'field':
        case 'field_alert':
          return NotificationAction.openField;
        case 'task':
        case 'task_reminder':
          return NotificationAction.openTask;
        case 'alert':
        case 'high_alert':
        case 'medium_alert':
        case 'low_alert':
          return NotificationAction.openAlert;
        case 'weather':
        case 'weather_alert':
          return NotificationAction.openWeather;
        case 'irrigation':
        case 'irrigation_due':
          return NotificationAction.openIrrigation;
        case 'ndvi':
        case 'ndvi_change':
          return NotificationAction.openNdvi;
        case 'sync':
        case 'sync_complete':
          return NotificationAction.openSync;
      }
    }

    return NotificationAction.none;
  }

  /// الحصول على المسار المناسب للإجراء
  String? _getRouteForAction(NotificationAction action, Map<String, dynamic> payload) {
    final targetId = payload['targetId'] as String?;
    final fieldId = payload['fieldId'] as String?;
    final taskId = payload['taskId'] as String?;

    switch (action) {
      case NotificationAction.openField:
        // Navigate to field details if fieldId is provided
        if (fieldId != null) {
          return '/field/$fieldId';
        } else if (targetId != null) {
          return '/field/$targetId';
        }
        // Otherwise, go to fields list
        return '/fields';

      case NotificationAction.openTask:
        // Navigate to field with task if both IDs are provided
        if (fieldId != null && taskId != null) {
          return '/field/$fieldId?taskId=$taskId';
        } else if (fieldId != null) {
          return '/field/$fieldId';
        }
        // Otherwise, go to map (tasks are shown there)
        return '/map';

      case NotificationAction.openAlert:
        // Navigate to alerts screen
        return '/alerts';

      case NotificationAction.openWeather:
        // Navigate to field with weather info if fieldId is provided
        if (fieldId != null) {
          return '/field/$fieldId?tab=weather';
        }
        // Otherwise, go to map
        return '/map';

      case NotificationAction.openIrrigation:
        // Navigate to field irrigation tab if fieldId is provided
        if (fieldId != null) {
          return '/field/$fieldId?tab=irrigation';
        }
        // Otherwise, go to fields list
        return '/fields';

      case NotificationAction.openNdvi:
        // Navigate to field NDVI/analytics tab if fieldId is provided
        if (fieldId != null) {
          return '/field/$fieldId?tab=analytics';
        }
        // Otherwise, go to map
        return '/map';

      case NotificationAction.openSync:
        // Navigate to sync screen
        return '/sync';

      case NotificationAction.openProfile:
        // Navigate to profile screen
        return '/profile';

      case NotificationAction.openAdvisor:
        // Navigate to AI advisor
        return '/advisor';

      case NotificationAction.none:
        // Default to map screen
        return '/map';
    }
  }

  /// تحليل payload من نص JSON
  Map<String, dynamic>? parsePayload(String? payloadString) {
    if (payloadString == null || payloadString.isEmpty) {
      return null;
    }

    try {
      return jsonDecode(payloadString) as Map<String, dynamic>;
    } catch (e) {
      debugPrint('Error parsing payload JSON: $e');
      return null;
    }
  }

  /// بناء payload للإشعار
  String buildPayload({
    required String type,
    String? action,
    String? targetId,
    String? fieldId,
    String? taskId,
    Map<String, dynamic>? additionalData,
  }) {
    final payload = <String, dynamic>{
      'type': type,
      'timestamp': DateTime.now().toIso8601String(),
    };

    if (action != null) payload['action'] = action;
    if (targetId != null) payload['targetId'] = targetId;
    if (fieldId != null) payload['fieldId'] = fieldId;
    if (taskId != null) payload['taskId'] = taskId;

    if (additionalData != null) {
      payload.addAll(additionalData);
    }

    return jsonEncode(payload);
  }

  /// إنشاء payload لإشعار حقل
  String createFieldNotificationPayload({
    required String fieldId,
    String? action,
    Map<String, dynamic>? additionalData,
  }) {
    return buildPayload(
      type: 'field',
      action: action ?? 'open_field',
      fieldId: fieldId,
      additionalData: additionalData,
    );
  }

  /// إنشاء payload لإشعار مهمة
  String createTaskNotificationPayload({
    required String taskId,
    String? fieldId,
    String? action,
    Map<String, dynamic>? additionalData,
  }) {
    return buildPayload(
      type: 'task',
      action: action ?? 'open_task',
      targetId: taskId,
      fieldId: fieldId,
      additionalData: additionalData,
    );
  }

  /// إنشاء payload لإشعار تنبيه
  String createAlertNotificationPayload({
    required String alertId,
    String? fieldId,
    String? action,
    Map<String, dynamic>? additionalData,
  }) {
    return buildPayload(
      type: 'alert',
      action: action ?? 'open_alert',
      targetId: alertId,
      fieldId: fieldId,
      additionalData: additionalData,
    );
  }

  /// إنشاء payload لإشعار الطقس
  String createWeatherNotificationPayload({
    String? fieldId,
    String? action,
    Map<String, dynamic>? additionalData,
  }) {
    return buildPayload(
      type: 'weather',
      action: action ?? 'open_weather',
      fieldId: fieldId,
      additionalData: additionalData,
    );
  }

  /// إنشاء payload لإشعار الري
  String createIrrigationNotificationPayload({
    required String fieldId,
    String? action,
    Map<String, dynamic>? additionalData,
  }) {
    return buildPayload(
      type: 'irrigation',
      action: action ?? 'open_irrigation',
      fieldId: fieldId,
      additionalData: additionalData,
    );
  }

  /// إنشاء payload لإشعار NDVI
  String createNdviNotificationPayload({
    required String fieldId,
    String? action,
    Map<String, dynamic>? additionalData,
  }) {
    return buildPayload(
      type: 'ndvi',
      action: action ?? 'open_ndvi',
      fieldId: fieldId,
      additionalData: additionalData,
    );
  }
}
