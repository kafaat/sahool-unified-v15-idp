/// SAHOOL Notification Provider
/// مزود الإشعارات
///
/// Provides notification services and state management for the app.
/// يوفر خدمات الإشعارات وإدارة الحالة للتطبيق.

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'notification_service.dart';
import 'notification_manager.dart';
import 'notification_handler.dart';
import 'notification_types.dart';
import 'push_notification_service.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Core Service Providers
// مزودات الخدمات الأساسية
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for NotificationService (local notifications)
final notificationServiceProvider = Provider<NotificationService>((ref) {
  return NotificationServiceImpl();
});

/// Provider for NotificationManager (unified manager)
final notificationManagerProvider = Provider<NotificationManager>((ref) {
  return NotificationManager.instance;
});

/// Provider for PushNotificationService
final pushServiceProvider = Provider<PushNotificationService>((ref) {
  return PushNotificationService.instance;
});

// ═══════════════════════════════════════════════════════════════════════════
// Initialization Providers
// مزودات التهيئة
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for notification initialization state
/// مزود لحالة تهيئة الإشعارات
final notificationInitializedProvider = FutureProvider<bool>((ref) async {
  final manager = ref.watch(notificationManagerProvider);

  try {
    await manager.initialize();
    final granted = await manager.requestPermission();
    return granted;
  } catch (e) {
    // Log error but don't crash the app
    return false;
  }
});

/// Provider for push notification initialization
/// مزود لتهيئة الإشعارات الفورية
final pushNotificationInitializedProvider = FutureProvider<bool>((ref) async {
  final service = ref.watch(pushServiceProvider);

  try {
    await service.initialize();
    return await service.requestPermission();
  } catch (e) {
    return false;
  }
});

// ═══════════════════════════════════════════════════════════════════════════
// Stream Providers
// مزودات البث
// ═══════════════════════════════════════════════════════════════════════════

/// Stream provider for incoming notifications
/// مزود بث للإشعارات الواردة
final notificationStreamProvider = StreamProvider<NotificationPayload>((ref) {
  return NotificationManager.instance.onNotification;
});

/// Stream provider for notification count changes
/// مزود بث لتغييرات عدد الإشعارات
final notificationCountStreamProvider = StreamProvider<int>((ref) {
  return NotificationHandler.instance.onCountChanged;
});

// ═══════════════════════════════════════════════════════════════════════════
// State Providers
// مزودات الحالة
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for unread notification count
/// مزود لعدد الإشعارات غير المقروءة
final unreadNotificationCountProvider = Provider<int>((ref) {
  return NotificationHandler.instance.unreadCount;
});

/// Provider for checking if notifications are enabled
/// مزود للتحقق من تفعيل الإشعارات
final notificationsEnabledProvider = FutureProvider<bool>((ref) async {
  final manager = ref.watch(notificationManagerProvider);
  return await manager.areNotificationsEnabled();
});

/// Provider for subscribed topics
/// مزود للمواضيع المشترك بها
final subscribedTopicsProvider = Provider<Set<String>>((ref) {
  return PushNotificationService.instance.subscribedTopics;
});

// ═══════════════════════════════════════════════════════════════════════════
// Action Providers (StateNotifier)
// مزودات الإجراءات
// ═══════════════════════════════════════════════════════════════════════════

/// Notification actions notifier
class NotificationActionsNotifier extends StateNotifier<AsyncValue<void>> {
  final NotificationManager _manager;

  NotificationActionsNotifier(this._manager)
      : super(const AsyncValue.data(null));

  /// Show a notification
  Future<void> showNotification({
    required String title,
    required String body,
    SAHOOLNotificationType type = SAHOOLNotificationType.system,
    NotificationPriority priority = NotificationPriority.medium,
    Map<String, dynamic>? data,
  }) async {
    state = const AsyncValue.loading();
    try {
      await _manager.showNotification(
        title: title,
        body: body,
        type: type,
        priority: priority,
        data: data,
      );
      state = const AsyncValue.data(null);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// Schedule a notification
  Future<void> scheduleNotification({
    required String title,
    required String body,
    required DateTime scheduledTime,
    SAHOOLNotificationType type = SAHOOLNotificationType.taskReminder,
    NotificationPriority priority = NotificationPriority.medium,
    Map<String, dynamic>? data,
  }) async {
    state = const AsyncValue.loading();
    try {
      await _manager.scheduleNotification(
        title: title,
        body: body,
        scheduledTime: scheduledTime,
        type: type,
        priority: priority,
        data: data,
      );
      state = const AsyncValue.data(null);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// Cancel all notifications
  Future<void> cancelAllNotifications() async {
    state = const AsyncValue.loading();
    try {
      await _manager.cancelAllNotifications();
      state = const AsyncValue.data(null);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  /// Mark all as read
  Future<void> markAllAsRead() async {
    state = const AsyncValue.loading();
    try {
      await NotificationHandler.instance.markAllAsRead();
      state = const AsyncValue.data(null);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}

/// Provider for notification actions
final notificationActionsProvider =
    StateNotifierProvider<NotificationActionsNotifier, AsyncValue<void>>((ref) {
  final manager = ref.watch(notificationManagerProvider);
  return NotificationActionsNotifier(manager);
});
