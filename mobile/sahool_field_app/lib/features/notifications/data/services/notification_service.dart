import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../domain/entities/notification_entities.dart';

/// خدمة الإشعارات المحلية
/// Local Notification Service
class NotificationService {
  static const String _notificationsKey = 'sahool_notifications';
  static const String _settingsKey = 'sahool_notification_settings';
  static const String _fcmTokenKey = 'sahool_fcm_token';

  SharedPreferences? _prefs;

  Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();
  }

  /// حفظ FCM Token
  Future<void> saveFcmToken(String token) async {
    await _prefs?.setString(_fcmTokenKey, token);
  }

  /// جلب FCM Token
  String? getFcmToken() {
    return _prefs?.getString(_fcmTokenKey);
  }

  /// جلب الإشعارات المحفوظة محلياً
  Future<List<AppNotification>> getLocalNotifications() async {
    final json = _prefs?.getString(_notificationsKey);
    if (json == null) return [];

    try {
      final List<dynamic> list = jsonDecode(json);
      return list.map((e) => AppNotification.fromJson(e)).toList();
    } catch (e) {
      debugPrint('Error loading notifications: $e');
      return [];
    }
  }

  /// حفظ إشعار جديد محلياً
  Future<void> saveNotification(AppNotification notification) async {
    final notifications = await getLocalNotifications();
    notifications.insert(0, notification);

    // الاحتفاظ بآخر 100 إشعار فقط
    final trimmed = notifications.take(100).toList();

    await _prefs?.setString(
      _notificationsKey,
      jsonEncode(trimmed.map((e) => e.toJson()).toList()),
    );
  }

  /// تحديث حالة القراءة
  Future<void> markAsRead(String notificationId) async {
    final notifications = await getLocalNotifications();
    final updated = notifications.map((n) {
      if (n.id == notificationId) {
        return n.copyWith(isRead: true);
      }
      return n;
    }).toList();

    await _prefs?.setString(
      _notificationsKey,
      jsonEncode(updated.map((e) => e.toJson()).toList()),
    );
  }

  /// تحديد الكل كمقروء
  Future<void> markAllAsRead() async {
    final notifications = await getLocalNotifications();
    final updated = notifications.map((n) => n.copyWith(isRead: true)).toList();

    await _prefs?.setString(
      _notificationsKey,
      jsonEncode(updated.map((e) => e.toJson()).toList()),
    );
  }

  /// حذف إشعار
  Future<void> deleteNotification(String notificationId) async {
    final notifications = await getLocalNotifications();
    final updated = notifications.where((n) => n.id != notificationId).toList();

    await _prefs?.setString(
      _notificationsKey,
      jsonEncode(updated.map((e) => e.toJson()).toList()),
    );
  }

  /// مسح كل الإشعارات
  Future<void> clearAllNotifications() async {
    await _prefs?.remove(_notificationsKey);
  }

  /// جلب إعدادات الإشعارات
  NotificationSettings getSettings() {
    final json = _prefs?.getString(_settingsKey);
    if (json == null) return const NotificationSettings();

    try {
      return NotificationSettings.fromJson(jsonDecode(json));
    } catch (e) {
      debugPrint('Error loading notification settings: $e');
      return const NotificationSettings();
    }
  }

  /// حفظ إعدادات الإشعارات
  Future<void> saveSettings(NotificationSettings settings) async {
    await _prefs?.setString(
      _settingsKey,
      jsonEncode(settings.toJson()),
    );
  }

  /// عدد الإشعارات غير المقروءة
  Future<int> getUnreadCount() async {
    final notifications = await getLocalNotifications();
    return notifications.where((n) => !n.isRead).length;
  }

  /// معالجة إشعار Firebase (من payload)
  AppNotification parseFirebaseMessage(Map<String, dynamic> message) {
    final notification = message['notification'] as Map<String, dynamic>?;
    final data = message['data'] as Map<String, dynamic>? ?? {};

    return AppNotification(
      id: data['id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      type: data['type'] ?? 'system',
      title: notification?['title'] ?? data['title'] ?? 'إشعار',
      titleAr: notification?['title'] ?? data['title_ar'] ?? 'إشعار',
      body: notification?['body'] ?? data['body'] ?? '',
      bodyAr: notification?['body'] ?? data['body_ar'] ?? '',
      imageUrl: notification?['image'] ?? data['image_url'],
      data: data,
      createdAt: DateTime.now(),
      isRead: false,
      actionUrl: data['action_url'],
    );
  }
}
