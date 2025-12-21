/// SAHOOL Notification Service
/// خدمة الإشعارات

import 'dart:convert';
import 'dart:io';

import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

import 'notification_types.dart';

/// Callback for handling notification taps
typedef NotificationTapCallback = void Function(Map<String, dynamic>? payload);

abstract class NotificationService {
  Future<void> initialize({NotificationTapCallback? onTap});
  Future<bool> requestPermission();
  Future<String?> getToken();
  Future<void> showLocal({
    required NotificationType type,
    required String title,
    required String body,
    Map<String, dynamic>? data,
  });
  Future<void> showScheduled({
    required NotificationType type,
    required String title,
    required String body,
    required DateTime scheduledTime,
    Map<String, dynamic>? data,
  });
  Future<void> cancelAll();
  Future<void> cancelById(int id);
  Future<void> subscribeToTopic(String topic);
  Future<void> unsubscribeFromTopic(String topic);
  Future<List<PendingNotificationRequest>> getPendingNotifications();
}

class NotificationServiceImpl implements NotificationService {
  static final NotificationServiceImpl _instance = NotificationServiceImpl._internal();
  factory NotificationServiceImpl() => _instance;
  NotificationServiceImpl._internal();

  final FlutterLocalNotificationsPlugin _localNotifications = FlutterLocalNotificationsPlugin();
  bool _initialized = false;
  NotificationTapCallback? _onTapCallback;

  // Notification channels for Android
  static const _alertsChannel = AndroidNotificationChannel(
    'alerts',
    'التنبيهات',
    description: 'تنبيهات المزرعة',
    importance: Importance.high,
  );

  static const _tasksChannel = AndroidNotificationChannel(
    'tasks',
    'المهام',
    description: 'إشعارات المهام',
    importance: Importance.defaultImportance,
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
    description: 'جدولة الري',
    importance: Importance.high,
  );

  static const _weatherChannel = AndroidNotificationChannel(
    'weather',
    'الطقس',
    description: 'تحذيرات الطقس',
    importance: Importance.high,
  );

  static const _systemChannel = AndroidNotificationChannel(
    'system',
    'النظام',
    description: 'إشعارات النظام',
    importance: Importance.low,
  );

  @override
  Future<void> initialize({NotificationTapCallback? onTap}) async {
    if (_initialized) return;

    _onTapCallback = onTap;

    // Android initialization
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');

    // iOS/macOS initialization
    final darwinSettings = DarwinInitializationSettings(
      requestAlertPermission: false,
      requestBadgePermission: false,
      requestSoundPermission: false,
      onDidReceiveLocalNotification: (id, title, body, payload) async {
        // Handle iOS foreground notification (older iOS versions)
        debugPrint('iOS Notification: $title - $body');
      },
    );

    final initSettings = InitializationSettings(
      android: androidSettings,
      iOS: darwinSettings,
      macOS: darwinSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _handleNotificationTap,
      onDidReceiveBackgroundNotificationResponse: _handleBackgroundNotificationTap,
    );

    // Create notification channels on Android
    if (Platform.isAndroid) {
      final androidPlugin = _localNotifications
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();

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
    debugPrint('✅ NotificationService initialized');
  }

  void _handleNotificationTap(NotificationResponse response) {
    if (_onTapCallback != null && response.payload != null) {
      try {
        final data = jsonDecode(response.payload!) as Map<String, dynamic>;
        _onTapCallback!(data);
      } catch (e) {
        debugPrint('Error parsing notification payload: $e');
        _onTapCallback!(null);
      }
    }
  }

  @pragma('vm:entry-point')
  static void _handleBackgroundNotificationTap(NotificationResponse response) {
    // Handle background notification tap
    debugPrint('Background notification tapped: ${response.payload}');
  }

  @override
  Future<bool> requestPermission() async {
    if (Platform.isAndroid) {
      final androidPlugin = _localNotifications
          .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();

      if (androidPlugin != null) {
        final granted = await androidPlugin.requestNotificationsPermission();
        return granted ?? false;
      }
      return true;
    } else if (Platform.isIOS) {
      final iosPlugin = _localNotifications
          .resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>();

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

  @override
  Future<String?> getToken() async {
    // Local notifications don't have tokens
    // This would be used with Firebase Cloud Messaging
    return null;
  }

  @override
  Future<void> showLocal({
    required NotificationType type,
    required String title,
    required String body,
    Map<String, dynamic>? data,
  }) async {
    if (!_initialized) {
      debugPrint('⚠️ NotificationService not initialized');
      return;
    }

    final androidDetails = AndroidNotificationDetails(
      type.channelId,
      type.channelName,
      channelDescription: type.channelDescription,
      importance: type.isUrgent ? Importance.high : Importance.defaultImportance,
      priority: type.isUrgent ? Priority.high : Priority.defaultPriority,
      icon: '@mipmap/ic_launcher',
      styleInformation: BigTextStyleInformation(body),
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

    final notificationId = DateTime.now().millisecondsSinceEpoch % 2147483647;

    await _localNotifications.show(
      notificationId,
      title,
      body,
      details,
      payload: data != null ? jsonEncode(data) : null,
    );

    debugPrint('📬 Notification shown: $title');
  }

  @override
  Future<void> showScheduled({
    required NotificationType type,
    required String title,
    required String body,
    required DateTime scheduledTime,
    Map<String, dynamic>? data,
  }) async {
    if (!_initialized) {
      debugPrint('⚠️ NotificationService not initialized');
      return;
    }

    final androidDetails = AndroidNotificationDetails(
      type.channelId,
      type.channelName,
      channelDescription: type.channelDescription,
      importance: type.isUrgent ? Importance.high : Importance.defaultImportance,
      priority: type.isUrgent ? Priority.high : Priority.defaultPriority,
      icon: '@mipmap/ic_launcher',
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

    final notificationId = DateTime.now().millisecondsSinceEpoch % 2147483647;

    await _localNotifications.zonedSchedule(
      notificationId,
      title,
      body,
      _convertToTZDateTime(scheduledTime),
      details,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
      payload: data != null ? jsonEncode(data) : null,
    );

    debugPrint('⏰ Scheduled notification: $title at $scheduledTime');
  }

  TZDateTime _convertToTZDateTime(DateTime dateTime) {
    // Simple conversion - in production, use timezone package
    return TZDateTime.from(dateTime, local);
  }

  @override
  Future<void> cancelAll() async {
    await _localNotifications.cancelAll();
    debugPrint('🗑️ All notifications cancelled');
  }

  @override
  Future<void> cancelById(int id) async {
    await _localNotifications.cancel(id);
    debugPrint('🗑️ Notification $id cancelled');
  }

  @override
  Future<void> subscribeToTopic(String topic) async {
    // Would be implemented with Firebase Cloud Messaging
    debugPrint('📢 Subscribed to topic: $topic');
  }

  @override
  Future<void> unsubscribeFromTopic(String topic) async {
    // Would be implemented with Firebase Cloud Messaging
    debugPrint('🔕 Unsubscribed from topic: $topic');
  }

  @override
  Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return await _localNotifications.pendingNotificationRequests();
  }
}

/// Simple TZDateTime implementation for scheduling
/// In production, use the timezone package for proper timezone handling
class TZDateTime extends DateTime {
  TZDateTime(super.year, [
    super.month,
    super.day,
    super.hour,
    super.minute,
    super.second,
    super.millisecond,
    super.microsecond,
  ]);

  factory TZDateTime.from(DateTime dateTime, Location location) {
    return TZDateTime(
      dateTime.year,
      dateTime.month,
      dateTime.day,
      dateTime.hour,
      dateTime.minute,
      dateTime.second,
      dateTime.millisecond,
      dateTime.microsecond,
    );
  }

  factory TZDateTime.now(Location location) {
    final now = DateTime.now();
    return TZDateTime.from(now, location);
  }
}

/// Simple Location class for timezone
class Location {
  final String name;
  const Location(this.name);
}

/// Local timezone
const local = Location('local');
