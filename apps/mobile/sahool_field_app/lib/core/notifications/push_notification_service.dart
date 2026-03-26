/// SAHOOL Push Notification Service
/// خدمة الإشعارات الفورية
///
/// This service provides push notification functionality.
/// Currently operates in local-only mode (Firebase disabled).
/// When Firebase is enabled, this service will be updated to use FCM.
///
/// توفر هذه الخدمة وظائف الإشعارات الفورية.
/// حالياً تعمل في وضع الإشعارات المحلية فقط (Firebase معطل).
/// عند تفعيل Firebase، سيتم تحديث هذه الخدمة لاستخدام FCM.
library;

import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../utils/app_logger.dart';
import 'notification_types.dart';
import 'notification_manager.dart';
import 'notification_handler.dart';

/// Push notification configuration
/// إعدادات الإشعارات الفورية
class PushNotificationConfig {
  /// Whether Firebase is enabled
  /// هل Firebase مفعل
  static const bool firebaseEnabled = false;

  /// Default topics to subscribe to
  /// المواضيع الافتراضية للاشتراك
  static const List<String> defaultTopics = [
    'all_farmers',
    'system_announcements',
  ];
}

/// Push Notification Service
/// خدمة الإشعارات الفورية
///
/// Provides a unified interface for push notifications.
/// When Firebase is disabled, uses local notification fallback.
class PushNotificationService {
  static final PushNotificationService instance = PushNotificationService._();

  PushNotificationService._();

  /// FCM Token (null when Firebase is disabled)
  String? _fcmToken;
  String? get fcmToken => _fcmToken;

  /// Notification stream controller
  final _notificationController =
      StreamController<NotificationPayload>.broadcast();
  Stream<NotificationPayload> get onNotification =>
      _notificationController.stream;

  /// Token refresh stream controller
  final _tokenController = StreamController<String>.broadcast();
  Stream<String> get onTokenRefresh => _tokenController.stream;

  /// Subscribed topics
  final Set<String> _subscribedTopics = {};
  Set<String> get subscribedTopics => Set.unmodifiable(_subscribedTopics);

  bool _isInitialized = false;
  bool get isInitialized => _isInitialized;

  /// Initialize the push notification service
  /// تهيئة خدمة الإشعارات الفورية
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      if (PushNotificationConfig.firebaseEnabled) {
        // Firebase initialization would go here when enabled
        // await _initializeFirebase();
        AppLogger.i('Firebase push notifications not enabled', tag: 'PUSH');
      }

      // Always initialize local notification support
      await NotificationManager.instance.initialize();

      // Subscribe to default topics (simulated when Firebase is disabled)
      for (final topic in PushNotificationConfig.defaultTopics) {
        await subscribeToTopic(topic);
      }

      _isInitialized = true;
      AppLogger.i('Push notification service initialized (local mode)',
          tag: 'PUSH');
    } catch (e, stackTrace) {
      AppLogger.e(
        'Failed to initialize push notifications',
        tag: 'PUSH',
        error: e,
        stackTrace: stackTrace,
      );
    }
  }

  /// Request push notification permission
  /// طلب إذن الإشعارات الفورية
  Future<bool> requestPermission() async {
    return NotificationManager.instance.requestPermission();
  }

  /// Get the push notification token
  /// الحصول على رمز الإشعارات الفورية
  ///
  /// When Firebase is disabled, this returns a device-specific identifier
  /// that can be used for local notification scheduling.
  Future<String?> getToken() async {
    if (PushNotificationConfig.firebaseEnabled) {
      // Firebase token retrieval would go here
      return null;
    }

    // Generate a pseudo-token for local notifications
    // This could be used for backend registration when Firebase is unavailable
    _fcmToken ??= 'local-${DateTime.now().millisecondsSinceEpoch}';
    return _fcmToken;
  }

  /// Subscribe to a notification topic
  /// الاشتراك في موضوع إشعارات
  ///
  /// When Firebase is disabled, this tracks topics locally for when
  /// Firebase is enabled later or for backend notification routing.
  Future<void> subscribeToTopic(String topic) async {
    try {
      if (PushNotificationConfig.firebaseEnabled) {
        // Firebase topic subscription would go here
        // await FirebaseMessaging.instance.subscribeToTopic(topic);
      }

      _subscribedTopics.add(topic);
      AppLogger.d('Subscribed to topic: $topic', tag: 'PUSH');
    } catch (e) {
      AppLogger.e('Failed to subscribe to topic: $topic',
          tag: 'PUSH', error: e);
    }
  }

  /// Unsubscribe from a notification topic
  /// إلغاء الاشتراك من موضوع إشعارات
  Future<void> unsubscribeFromTopic(String topic) async {
    try {
      if (PushNotificationConfig.firebaseEnabled) {
        // Firebase topic unsubscription would go here
        // await FirebaseMessaging.instance.unsubscribeFromTopic(topic);
      }

      _subscribedTopics.remove(topic);
      AppLogger.d('Unsubscribed from topic: $topic', tag: 'PUSH');
    } catch (e) {
      AppLogger.e('Failed to unsubscribe from topic: $topic',
          tag: 'PUSH', error: e);
    }
  }

  /// Subscribe to user-specific topics
  /// الاشتراك في مواضيع المستخدم
  Future<void> subscribeToUserTopics({
    required String userId,
    String? tenantId,
    String? governorate,
    List<String>? crops,
  }) async {
    // User-specific topic
    await subscribeToTopic('user_$userId');

    // Tenant topic
    if (tenantId != null) {
      await subscribeToTopic('tenant_$tenantId');
    }

    // Governorate topic
    if (governorate != null) {
      await subscribeToTopic('gov_$governorate');
    }

    // Crop topics
    if (crops != null) {
      for (final crop in crops) {
        await subscribeToTopic('crop_$crop');
      }
    }
  }

  /// Unsubscribe from user-specific topics
  /// إلغاء الاشتراك من مواضيع المستخدم
  Future<void> unsubscribeFromUserTopics({
    required String userId,
    String? tenantId,
    String? governorate,
    List<String>? crops,
  }) async {
    await unsubscribeFromTopic('user_$userId');

    if (tenantId != null) {
      await unsubscribeFromTopic('tenant_$tenantId');
    }

    if (governorate != null) {
      await unsubscribeFromTopic('gov_$governorate');
    }

    if (crops != null) {
      for (final crop in crops) {
        await unsubscribeFromTopic('crop_$crop');
      }
    }
  }

  /// Simulate receiving a push notification (for testing)
  /// محاكاة استلام إشعار فوري (للاختبار)
  @visibleForTesting
  Future<void> simulatePushNotification({
    required String title,
    required String body,
    SAHOOLNotificationType type = SAHOOLNotificationType.system,
    NotificationPriority priority = NotificationPriority.medium,
    Map<String, dynamic>? data,
  }) async {
    // Show local notification
    await NotificationManager.instance.showNotification(
      title: title,
      body: body,
      type: type,
      priority: priority,
      data: data,
    );

    // Emit to stream
    final payload = NotificationPayload(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      type: type,
      priority: priority,
      title: title,
      body: body,
      data: data ?? {},
      receivedAt: DateTime.now(),
      tapped: false,
    );
    _notificationController.add(payload);
  }

  /// Delete the push notification token
  /// حذف رمز الإشعارات الفورية
  Future<void> deleteToken() async {
    try {
      if (PushNotificationConfig.firebaseEnabled) {
        // Firebase token deletion would go here
        // await FirebaseMessaging.instance.deleteToken();
      }

      _fcmToken = null;
      AppLogger.i('Push notification token deleted', tag: 'PUSH');
    } catch (e) {
      AppLogger.e('Failed to delete push notification token',
          tag: 'PUSH', error: e);
    }
  }

  /// Dispose resources
  /// التخلص من الموارد
  void dispose() {
    _notificationController.close();
    _tokenController.close();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// مزودات Riverpod
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for PushNotificationService
final pushNotificationServiceProvider =
    Provider<PushNotificationService>((ref) {
  return PushNotificationService.instance;
});

/// Provider for push notification initialization
final pushNotificationInitProvider = FutureProvider<bool>((ref) async {
  final service = ref.watch(pushNotificationServiceProvider);
  await service.initialize();
  return service.requestPermission();
});

/// Stream provider for push notifications
final pushNotificationStreamProvider =
    StreamProvider<NotificationPayload>((ref) {
  return PushNotificationService.instance.onNotification;
});

/// Provider for subscribed topics
final subscribedTopicsProvider = Provider<Set<String>>((ref) {
  return PushNotificationService.instance.subscribedTopics;
});
