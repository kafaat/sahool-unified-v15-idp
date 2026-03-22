/// SAHOOL Local Notification Service
/// خدمة الإشعارات المحلية
///
/// Features:
/// - Local notifications using flutter_local_notifications
/// - Multiple notification channels (tasks, weather, alerts)
/// - Arabic notification support
/// - Scheduled notifications
/// - Notification actions and buttons
library;

import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'notification_types.dart';

/// Callback for handling notification taps
typedef NotificationTapCallback = void Function(Map<String, dynamic>? payload);

/// Local Notification Service for in-app alerts
class LocalNotificationService {
  static final LocalNotificationService _instance =
      LocalNotificationService._internal();
  factory LocalNotificationService() => _instance;
  LocalNotificationService._internal();

  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();
  bool _initialized = false;
  NotificationTapCallback? _onTapCallback;

  // Notification channels for Android
  static const _alertsChannel = AndroidNotificationChannel(
    'alerts',
    'التنبيهات',
    description: 'تنبيهات المزرعة والحقول',
    importance: Importance.high,
    enableVibration: true,
    playSound: true,
  );

  static const _tasksChannel = AndroidNotificationChannel(
    'tasks',
    'المهام',
    description: 'إشعارات المهام والتذكيرات',
    importance: Importance.defaultImportance,
    enableVibration: true,
  );

  static const _ndviChannel = AndroidNotificationChannel(
    'ndvi',
    'NDVI',
    description: 'تغييرات مؤشر NDVI',
    importance: Importance.defaultImportance,
  );

  static const _irrigationChannel = AndroidNotificationChannel(
    'irrigation',
    'الري',
    description: 'جدولة الري وتذكيرات الري',
    importance: Importance.high,
    enableVibration: true,
    playSound: true,
  );

  static const _weatherChannel = AndroidNotificationChannel(
    'weather',
    'الطقس',
    description: 'تحذيرات وتنبيهات الطقس',
    importance: Importance.high,
    enableVibration: true,
    playSound: true,
  );

  static const _systemChannel = AndroidNotificationChannel(
    'system',
    'النظام',
    description: 'إشعارات النظام والمزامنة',
    importance: Importance.low,
  );

  /// تهيئة خدمة الإشعارات المحلية
  Future<void> initialize({NotificationTapCallback? onTap}) async {
    if (_initialized) return;

    _onTapCallback = onTap;

    // Android initialization
    const androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');

    // iOS/macOS initialization
    const darwinSettings = DarwinInitializationSettings(
      requestAlertPermission: false,
      requestBadgePermission: false,
      requestSoundPermission: false,
    );

    final initSettings = InitializationSettings(
      android: androidSettings,
      iOS: darwinSettings,
      macOS: darwinSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _handleNotificationTap,
      onDidReceiveBackgroundNotificationResponse:
          _handleBackgroundNotificationTap,
    );

    // Create notification channels on Android
    if (Platform.isAndroid) {
      final androidPlugin =
          _localNotifications.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();

      if (androidPlugin != null) {
        await androidPlugin.createNotificationChannel(_alertsChannel);
        await androidPlugin.createNotificationChannel(_tasksChannel);
        await androidPlugin.createNotificationChannel(_ndviChannel);
        await androidPlugin.createNotificationChannel(_irrigationChannel);
        await androidPlugin.createNotificationChannel(_weatherChannel);
        await androidPlugin.createNotificationChannel(_systemChannel);
      }
    }

    _initialized = true;
    if (kDebugMode) {
      debugPrint('✅ LocalNotificationService initialized');
    }
  }

  /// معالجة النقر على الإشعار
  void _handleNotificationTap(NotificationResponse response) {
    if (_onTapCallback != null && response.payload != null) {
      try {
        final data = jsonDecode(response.payload!) as Map<String, dynamic>;
        _onTapCallback!(data);
      } catch (e) {
        if (kDebugMode) {
          debugPrint('Error parsing notification payload: $e');
        }
        _onTapCallback!(null);
      }
    }
  }

  /// معالجة النقر على الإشعار في الخلفية
  @pragma('vm:entry-point')
  static void _handleBackgroundNotificationTap(NotificationResponse response) {
    // Handle background notification tap
    if (kDebugMode) {
      debugPrint('Background notification tapped: ${response.payload}');
    }
  }

  /// طلب إذن الإشعارات
  Future<bool> requestPermission() async {
    if (Platform.isAndroid) {
      final androidPlugin =
          _localNotifications.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();

      if (androidPlugin != null) {
        final granted = await androidPlugin.requestNotificationsPermission();
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
        return granted ?? false;
      }
    }
    return false;
  }

  /// عرض إشعار محلي
  Future<void> showNotification({
    required NotificationType type,
    required String title,
    required String body,
    Map<String, dynamic>? data,
    String? largeIcon,
    String? bigPicture,
  }) async {
    if (!_initialized) {
      if (kDebugMode) {
        debugPrint('⚠️ LocalNotificationService not initialized');
      }
      return;
    }

    final androidDetails = AndroidNotificationDetails(
      type.channelId,
      type.channelName,
      channelDescription: type.channelDescription,
      importance:
          type.isUrgent ? Importance.high : Importance.defaultImportance,
      priority: type.isUrgent ? Priority.high : Priority.defaultPriority,
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
      enableVibration: type.isUrgent,
      playSound: type.isUrgent,
    );

    final iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: type.isUrgent,
      subtitle: body,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    final notificationId = DateTime.now().millisecondsSinceEpoch % 2147483647;

    await _localNotifications.show(
      notificationId,
      title,
      body,
      details,
      payload: data != null ? jsonEncode(data) : null,
    );

    if (kDebugMode) {
      debugPrint('📬 Local notification shown: $title');
    }
  }

  /// عرض إشعار مجدول
  Future<void> showScheduledNotification({
    required NotificationType type,
    required String title,
    required String body,
    required DateTime scheduledTime,
    Map<String, dynamic>? data,
    int? id,
  }) async {
    if (!_initialized) {
      if (kDebugMode) {
        debugPrint('⚠️ LocalNotificationService not initialized');
      }
      return;
    }

    final androidDetails = AndroidNotificationDetails(
      type.channelId,
      type.channelName,
      channelDescription: type.channelDescription,
      importance:
          type.isUrgent ? Importance.high : Importance.defaultImportance,
      priority: type.isUrgent ? Priority.high : Priority.defaultPriority,
      icon: '@mipmap/ic_launcher',
      styleInformation: BigTextStyleInformation(body),
      enableVibration: type.isUrgent,
      playSound: type.isUrgent,
    );

    final iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: type.isUrgent,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    final notificationId =
        id ?? DateTime.now().millisecondsSinceEpoch % 2147483647;

    // Note: For full timezone support, add the timezone package
    // For now, using simple DateTime scheduling
    final scheduledDate = scheduledTime.isAfter(DateTime.now())
        ? scheduledTime
        : DateTime.now().add(const Duration(seconds: 5));

    await _localNotifications.zonedSchedule(
      notificationId,
      title,
      body,
      tz.TZDateTime.from(scheduledDate, tz.local),
      details,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      payload: data != null ? jsonEncode(data) : null,
    );

    if (kDebugMode) {
      debugPrint('⏰ Scheduled notification: $title at $scheduledTime');
    }
  }

  /// عرض إشعار تقدم (Progress notification)
  Future<void> showProgressNotification({
    required int id,
    required String title,
    required String body,
    required int progress,
    required int maxProgress,
  }) async {
    if (!_initialized) return;

    final androidDetails = AndroidNotificationDetails(
      'system',
      'النظام',
      channelDescription: 'إشعارات التقدم',
      importance: Importance.low,
      priority: Priority.low,
      showProgress: true,
      maxProgress: maxProgress,
      progress: progress,
      onlyAlertOnce: true,
      icon: '@mipmap/ic_launcher',
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: false,
      presentSound: false,
    );

    final details = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );

    await _localNotifications.show(id, title, body, details);
  }

  /// إلغاء جميع الإشعارات
  Future<void> cancelAll() async {
    await _localNotifications.cancelAll();
    if (kDebugMode) {
      debugPrint('🗑️ All notifications cancelled');
    }
  }

  /// إلغاء إشعار معين
  Future<void> cancelById(int id) async {
    await _localNotifications.cancel(id);
    if (kDebugMode) {
      debugPrint('🗑️ Notification $id cancelled');
    }
  }

  /// الحصول على الإشعارات المعلقة
  Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return _localNotifications.pendingNotificationRequests();
  }

  /// الحصول على الإشعارات النشطة
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

  /// مسح بادج الإشعارات على iOS
  Future<void> clearBadge() async {
    if (Platform.isIOS) {
      final iosPlugin =
          _localNotifications.resolvePlatformSpecificImplementation<
              IOSFlutterLocalNotificationsPlugin>();

      if (iosPlugin != null) {
        // Clear badge count
        const details = DarwinNotificationDetails(
          badgeNumber: 0,
        );
        await _localNotifications.show(
          0,
          '',
          '',
          const NotificationDetails(iOS: details),
        );
      }
    }
  }
}

