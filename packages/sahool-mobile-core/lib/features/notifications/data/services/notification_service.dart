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
      final List<dynamic> list = jsonDecode(json) as List<dynamic>;
      return list.map((e) => AppNotification.fromJson(e as Map<String, dynamic>)).toList();
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
      return NotificationSettings.fromJson(jsonDecode(json) as Map<String, dynamic>);
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
      id: (data['id'] as String?) ?? DateTime.now().millisecondsSinceEpoch.toString(),
      type: (data['type'] as String?) ?? 'system',
      title: (notification?['title'] as String?) ?? (data['title'] as String?) ?? 'إشعار',
      titleAr: (notification?['title'] as String?) ?? (data['title_ar'] as String?) ?? 'إشعار',
      body: (notification?['body'] as String?) ?? (data['body'] as String?) ?? '',
      bodyAr: (notification?['body'] as String?) ?? (data['body_ar'] as String?) ?? '',
      imageUrl: (notification?['image'] as String?) ?? (data['image_url'] as String?),
      data: data,
      createdAt: DateTime.now(),
      isRead: false,
      actionUrl: data['action_url'] as String?,
    );
  }

  /// Clean up resources. Currently a no-op since SharedPreferences is a
  /// singleton, but provides a hook for future resource cleanup.
  void dispose() {
    _prefs = null;
  }
}
