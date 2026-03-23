/// SAHOOL Notification Manager
/// مدير الإشعارات المركزي
///
/// Unified notification management for the SAHOOL platform.
/// Handles local notifications, scheduled notifications, and prepares
/// the structure for push notifications when Firebase is enabled.
///
/// Features:
/// الميزات:
/// - Local notification display (عرض الإشعارات المحلية)
/// - Scheduled notifications (الإشعارات المجدولة)
/// - Notification channels for Android (قنوات الإشعارات لأندرويد)
/// - Permission management (إدارة الأذونات)
/// - Notification preferences (تفضيلات الإشعارات)
/// - Notification tap handling (معالجة النقر على الإشعارات)
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:timezone/timezone.dart' as tz;

import '../utils/app_logger.dart';
import 'notification_types.dart';
import 'notification_handler.dart';
import 'notification_preferences.dart';

/// Background notification tap handler - must be top-level
@pragma('vm:entry-point')
void _onBackgroundNotificationTap(NotificationResponse response) {
  AppLogger.d('Background notification tapped: ${response.payload}',
      tag: 'NOTIFICATIONS');
}

/// SAHOOL Notification Manager
/// مدير إشعارات سهول المركزي
class NotificationManager {
  static final NotificationManager instance = NotificationManager._();

  NotificationManager._();

  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  bool _initialized = false;
  bool get isInitialized => _initialized;

  /// Notification preferences service
  final _preferencesService = NotificationPreferencesService.instance;

  /// Notification stream controller for app-wide notifications
  final _notificationStreamController =
      StreamController<NotificationPayload>.broadcast();
  Stream<NotificationPayload> get onNotification =>
      _notificationStreamController.stream;

  // ═══════════════════════════════════════════════════════════════════════════
  // Android Notification Channels
  // قنوات إشعارات أندرويد
  // ═══════════════════════════════════════════════════════════════════════════

  static const _alertsChannel = AndroidNotificationChannel(
    'sahool_alerts',
    'التنبيهات العاجلة',
    description: 'تنبيهات الطقس والأمراض والآفات',
    importance: Importance.max,
    enableVibration: true,
    playSound: true,
    showBadge: true,
  );

  static const _tasksChannel = AndroidNotificationChannel(
    'sahool_tasks',
    'المهام والتذكيرات',
    description: 'تذكيرات المهام والحصاد والري',
    importance: Importance.high,
    enableVibration: true,
    playSound: true,
  );

  static const _fieldUpdatesChannel = AndroidNotificationChannel(
    'sahool_field_updates',
    'تحديثات الحقل',
    description: 'تحديثات صحة المحصول وصور الأقمار',
    importance: Importance.defaultImportance,
  );

  static const _financialChannel = AndroidNotificationChannel(
    'sahool_financial',
    'المالية والأسواق',
    description: 'الدفعات وأسعار الأسواق',
    importance: Importance.defaultImportance,
  );

  static const _operationsChannel = AndroidNotificationChannel(
    'sahool_operations',
    'العمليات الزراعية',
    description: 'أوقات الرش والعمليات',
    importance: Importance.high,
    enableVibration: true,
    playSound: true,
  );

  static const _inventoryChannel = AndroidNotificationChannel(
    'sahool_inventory',
    'المخزون',
    description: 'إشعارات المخزون',
    importance: Importance.low,
  );

  static const _mainChannel = AndroidNotificationChannel(
    'sahool_main',
    'إشعارات سهول',
    description: 'إشعارات عامة',
    importance: Importance.defaultImportance,
  );

  static const _syncChannel = AndroidNotificationChannel(
    'sahool_sync',
    'المزامنة',
    description: 'حالة المزامنة',
    importance: Importance.low,
    showBadge: false,
  );

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // التهيئة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the notification manager
  /// تهيئة مدير الإشعارات
  Future<void> initialize({
    GlobalKey<NavigatorState>? navigatorKey,
  }) async {
    if (_initialized) return;

    try {
      // Initialize preferences
      await _preferencesService.initialize();

      // Initialize local notifications
      await _initializeLocalNotifications();

      // Create Android notification channels
      if (Platform.isAndroid) {
        await _createNotificationChannels();
      }

      // Initialize notification handler if navigator key is provided
      if (navigatorKey != null) {
        NotificationHandler.instance.initialize(navigatorKey);
      }

      _initialized = true;
      AppLogger.i('NotificationManager initialized', tag: 'NOTIFICATIONS');
    } catch (e, stackTrace) {
      AppLogger.e(
        'Failed to initialize NotificationManager',
        tag: 'NOTIFICATIONS',
        error: e,
        stackTrace: stackTrace,
      );
      rethrow;
    }
  }

  /// Initialize local notifications plugin
  /// تهيئة إضافة الإشعارات المحلية
  Future<void> _initializeLocalNotifications() async {
    // Android initialization
    const androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    // iOS/macOS initialization
    const darwinSettings = DarwinInitializationSettings(
      requestAlertPermission: false,
      requestBadgePermission: false,
      requestSoundPermission: false,
    );

    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: darwinSettings,
      macOS: darwinSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _handleNotificationTap,
      onDidReceiveBackgroundNotificationResponse: _onBackgroundNotificationTap,
    );
  }

  /// Create Android notification channels
  /// إنشاء قنوات إشعارات أندرويد
  Future<void> _createNotificationChannels() async {
    final androidPlugin =
        _localNotifications.resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>();

    if (androidPlugin == null) return;

    // Create all channels
    final channels = [
      _alertsChannel,
      _tasksChannel,
      _fieldUpdatesChannel,
      _financialChannel,
      _operationsChannel,
      _inventoryChannel,
      _mainChannel,
      _syncChannel,
    ];

    for (final channel in channels) {
      await androidPlugin.createNotificationChannel(channel);
    }

    AppLogger.d('Created ${channels.length} notification channels',
        tag: 'NOTIFICATIONS');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Permissions
  // الأذونات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Request notification permission
  /// طلب إذن الإشعارات
  Future<bool> requestPermission() async {
    if (Platform.isAndroid) {
      final androidPlugin =
          _localNotifications.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();

      if (androidPlugin != null) {
        final granted = await androidPlugin.requestNotificationsPermission();
        AppLogger.i(
          'Android notification permission: ${granted == true ? "granted" : "denied"}',
          tag: 'NOTIFICATIONS',
        );
        return granted ?? false;
      }
      return true;
    } else if (Platform.isIOS) {
      final iosPlugin =
          _localNotifications.resolvePlatformSpecificImplementation<
              IOSFlutterLocalNotificationsPlugin>();

      if (iosPlugin != null) {
        final granted = await iosPlugin.requestPermissions(
          alert: true,
          badge: true,
          sound: true,
        );
        AppLogger.i(
          'iOS notification permission: ${granted == true ? "granted" : "denied"}',
          tag: 'NOTIFICATIONS',
        );
        return granted ?? false;
      }
    }
    return false;
  }

  /// Check if notifications are enabled
  /// التحقق من تفعيل الإشعارات
  Future<bool> areNotificationsEnabled() async {
    if (Platform.isAndroid) {
      final androidPlugin =
          _localNotifications.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();

      if (androidPlugin != null) {
        return await androidPlugin.areNotificationsEnabled() ?? false;
      }
    }
    // For iOS, assume enabled if we've initialized
    return _initialized;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Show Notifications
  // عرض الإشعارات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Show a local notification
  /// عرض إشعار محلي
  Future<void> showNotification({
    required String title,
    required String body,
    SAHOOLNotificationType type = SAHOOLNotificationType.system,
    NotificationPriority priority = NotificationPriority.medium,
    Map<String, dynamic>? data,
    String? largeIcon,
    String? bigPicture,
    int? id,
  }) async {
    if (!_initialized) {
      AppLogger.w('NotificationManager not initialized', tag: 'NOTIFICATIONS');
      return;
    }

    // Check if notification should be shown based on preferences
    final prefs = _preferencesService.getPreferences();
    if (!prefs.shouldShowNotification(type, priority)) {
      AppLogger.d('Notification blocked by preferences: $type',
          tag: 'NOTIFICATIONS');
      return;
    }

    final androidDetails = AndroidNotificationDetails(
      type.channelId,
      type.channelName,
      channelDescription: type.channelDescription,
      importance: _getImportance(type, priority),
      priority: _getPriority(type, priority),
      icon: '@mipmap/ic_launcher',
      largeIcon:
          largeIcon != null ? DrawableResourceAndroidBitmap(largeIcon) : null,
      styleInformation: bigPicture != null
          ? BigPictureStyleInformation(
              FilePathAndroidBitmap(bigPicture),
              contentTitle: title,
              summaryText: body,
            )
          : BigTextStyleInformation(body),
      enableVibration: prefs.enableVibration &&
          (type.isUrgent || priority == NotificationPriority.critical),
      playSound: prefs.enableSound &&
          (type.isUrgent || priority == NotificationPriority.critical),
    );

    final iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: prefs.showBadge,
      presentSound: prefs.enableSound &&
          (type.isUrgent || priority == NotificationPriority.critical),
      subtitle: body,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    final notificationId =
        id ?? DateTime.now().millisecondsSinceEpoch % 2147483647;

    // Prepare payload
    final payload = <String, dynamic>{
      'id': notificationId.toString(),
      'type': type.value,
      'priority': priority.name,
      'title': title,
      'body': body,
      ...?data,
    };

    await _localNotifications.show(
      notificationId,
      title,
      body,
      details,
      payload: jsonEncode(payload),
    );

    AppLogger.d('Notification shown: $title (${type.value})',
        tag: 'NOTIFICATIONS');
  }

  /// Show a scheduled notification
  /// عرض إشعار مجدول
  Future<void> scheduleNotification({
    required String title,
    required String body,
    required DateTime scheduledTime,
    SAHOOLNotificationType type = SAHOOLNotificationType.taskReminder,
    NotificationPriority priority = NotificationPriority.medium,
    Map<String, dynamic>? data,
    int? id,
  }) async {
    if (!_initialized) {
      AppLogger.w('NotificationManager not initialized', tag: 'NOTIFICATIONS');
      return;
    }

    // Ensure scheduled time is in the future
    final now = DateTime.now();
    if (scheduledTime.isBefore(now)) {
      AppLogger.w('Scheduled time is in the past, showing immediately',
          tag: 'NOTIFICATIONS');
      await showNotification(
        title: title,
        body: body,
        type: type,
        priority: priority,
        data: data,
        id: id,
      );
      return;
    }

    final androidDetails = AndroidNotificationDetails(
      type.channelId,
      type.channelName,
      channelDescription: type.channelDescription,
      importance: _getImportance(type, priority),
      priority: _getPriority(type, priority),
      icon: '@mipmap/ic_launcher',
      styleInformation: BigTextStyleInformation(body),
    );

    final iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: type.isUrgent || priority == NotificationPriority.critical,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    final notificationId =
        id ?? DateTime.now().millisecondsSinceEpoch % 2147483647;

    // Prepare payload
    final payload = <String, dynamic>{
      'id': notificationId.toString(),
      'type': type.value,
      'priority': priority.name,
      'title': title,
      'body': body,
      'scheduled': true,
      ...?data,
    };

    await _localNotifications.zonedSchedule(
      notificationId,
      title,
      body,
      _toTZDateTime(scheduledTime),
      details,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      payload: jsonEncode(payload),
    );

    AppLogger.d('Notification scheduled: $title at $scheduledTime',
        tag: 'NOTIFICATIONS');
  }

  /// Show a progress notification (for sync, downloads, etc.)
  /// عرض إشعار التقدم (للمزامنة، التحميلات، إلخ)
  Future<void> showProgressNotification({
    required int id,
    required String title,
    required String body,
    required int progress,
    required int maxProgress,
    bool ongoing = true,
  }) async {
    if (!_initialized) return;

    final androidDetails = AndroidNotificationDetails(
      'sahool_sync',
      'المزامنة',
      channelDescription: 'حالة المزامنة',
      importance: Importance.low,
      priority: Priority.low,
      showProgress: true,
      maxProgress: maxProgress,
      progress: progress,
      onlyAlertOnce: true,
      ongoing: ongoing,
      icon: '@mipmap/ic_launcher',
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: false,
      presentBadge: false,
      presentSound: false,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(id, title, body, details);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cancel Notifications
  // إلغاء الإشعارات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Cancel a specific notification
  /// إلغاء إشعار معين
  Future<void> cancelNotification(int id) async {
    await _localNotifications.cancel(id);
    AppLogger.d('Notification cancelled: $id', tag: 'NOTIFICATIONS');
  }

  /// Cancel all notifications
  /// إلغاء جميع الإشعارات
  Future<void> cancelAllNotifications() async {
    await _localNotifications.cancelAll();
    AppLogger.d('All notifications cancelled', tag: 'NOTIFICATIONS');
  }

  /// Get pending notifications
  /// الحصول على الإشعارات المعلقة
  Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return _localNotifications.pendingNotificationRequests();
  }

  /// Get active notifications (Android only)
  /// الحصول على الإشعارات النشطة (أندرويد فقط)
  Future<List<ActiveNotification>> getActiveNotifications() async {
    if (Platform.isAndroid) {
      final androidPlugin =
          _localNotifications.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();

      if (androidPlugin != null) {
        return androidPlugin.getActiveNotifications();
      }
    }
    return [];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Notification Tap Handling
  // معالجة النقر على الإشعارات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Handle notification tap
  /// معالجة النقر على الإشعار
  void _handleNotificationTap(NotificationResponse response) {
    final payloadStr = response.payload;
    if (payloadStr == null) return;

    try {
      final data = jsonDecode(payloadStr) as Map<String, dynamic>;
      final payload = NotificationPayload.fromJson({
        ...data,
        'tapped': true,
      });

      // Emit to stream
      _notificationStreamController.add(payload);

      // Forward to notification handler
      NotificationHandler.instance.handleIncomingNotification(payload);

      AppLogger.d('Notification tapped: ${payload.type.value}',
          tag: 'NOTIFICATIONS');
    } catch (e) {
      AppLogger.e('Failed to parse notification payload',
          tag: 'NOTIFICATIONS', error: e);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Helper Methods
  // الدوال المساعدة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get Android importance based on notification type and priority
  Importance _getImportance(
      SAHOOLNotificationType type, NotificationPriority priority) {
    if (priority == NotificationPriority.critical || type.isUrgent) {
      return Importance.max;
    }
    if (priority == NotificationPriority.high) {
      return Importance.high;
    }
    if (priority == NotificationPriority.low) {
      return Importance.low;
    }
    return Importance.defaultImportance;
  }

  /// Get Android priority based on notification type and priority
  Priority _getPriority(
      SAHOOLNotificationType type, NotificationPriority priority) {
    if (priority == NotificationPriority.critical || type.isUrgent) {
      return Priority.high;
    }
    if (priority == NotificationPriority.high) {
      return Priority.high;
    }
    if (priority == NotificationPriority.low) {
      return Priority.low;
    }
    return Priority.defaultPriority;
  }

  /// Convert DateTime to TZDateTime for scheduling
  tz.TZDateTime _toTZDateTime(DateTime dateTime) {
    return tz.TZDateTime.from(dateTime, tz.local);
  }

  /// Dispose resources
  /// التخلص من الموارد
  void dispose() {
    _notificationStreamController.close();
    NotificationHandler.instance.dispose();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// مزودات Riverpod
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for NotificationManager
final notificationManagerProvider = Provider<NotificationManager>((ref) {
  return NotificationManager.instance;
});

/// Provider for notification initialization state
final notificationInitializedProvider = FutureProvider<bool>((ref) async {
  final manager = ref.watch(notificationManagerProvider);
  await manager.initialize();
  final granted = await manager.requestPermission();
  return granted;
});

/// Stream provider for notifications
final notificationStreamProvider = StreamProvider<NotificationPayload>((ref) {
  return NotificationManager.instance.onNotification;
});
