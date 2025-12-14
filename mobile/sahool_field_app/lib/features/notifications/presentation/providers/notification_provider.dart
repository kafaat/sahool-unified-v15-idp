import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/services/notification_service.dart';
import '../../domain/entities/notification_entities.dart';

/// Notification Service Provider
final notificationServiceProvider = Provider<NotificationService>((ref) {
  final service = NotificationService();
  service.init();
  return service;
});

/// حالة الإشعارات
class NotificationsState {
  final bool isLoading;
  final List<AppNotification> notifications;
  final int unreadCount;
  final String? error;

  const NotificationsState({
    this.isLoading = false,
    this.notifications = const [],
    this.unreadCount = 0,
    this.error,
  });

  NotificationsState copyWith({
    bool? isLoading,
    List<AppNotification>? notifications,
    int? unreadCount,
    String? error,
  }) {
    return NotificationsState(
      isLoading: isLoading ?? this.isLoading,
      notifications: notifications ?? this.notifications,
      unreadCount: unreadCount ?? this.unreadCount,
      error: error,
    );
  }
}

/// Notifications State Notifier
class NotificationsNotifier extends StateNotifier<NotificationsState> {
  final NotificationService _service;

  NotificationsNotifier(this._service) : super(const NotificationsState());

  Future<void> loadNotifications() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final notifications = await _service.getLocalNotifications();
      final unreadCount = await _service.getUnreadCount();

      state = state.copyWith(
        isLoading: false,
        notifications: notifications,
        unreadCount: unreadCount,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> addNotification(AppNotification notification) async {
    await _service.saveNotification(notification);
    await loadNotifications();
  }

  Future<void> markAsRead(String notificationId) async {
    await _service.markAsRead(notificationId);
    await loadNotifications();
  }

  Future<void> markAllAsRead() async {
    await _service.markAllAsRead();
    await loadNotifications();
  }

  Future<void> deleteNotification(String notificationId) async {
    await _service.deleteNotification(notificationId);
    await loadNotifications();
  }

  Future<void> clearAll() async {
    await _service.clearAllNotifications();
    await loadNotifications();
  }
}

/// Notifications Provider
final notificationsProvider =
    StateNotifierProvider<NotificationsNotifier, NotificationsState>((ref) {
  final service = ref.watch(notificationServiceProvider);
  return NotificationsNotifier(service);
});

/// حالة الإعدادات
class SettingsState {
  final bool isLoading;
  final NotificationSettings settings;
  final String? error;

  const SettingsState({
    this.isLoading = false,
    this.settings = const NotificationSettings(),
    this.error,
  });

  SettingsState copyWith({
    bool? isLoading,
    NotificationSettings? settings,
    String? error,
  }) {
    return SettingsState(
      isLoading: isLoading ?? this.isLoading,
      settings: settings ?? this.settings,
      error: error,
    );
  }
}

/// Settings State Notifier
class SettingsNotifier extends StateNotifier<SettingsState> {
  final NotificationService _service;

  SettingsNotifier(this._service) : super(const SettingsState());

  void loadSettings() {
    final settings = _service.getSettings();
    state = state.copyWith(settings: settings);
  }

  Future<void> updateSettings(NotificationSettings settings) async {
    await _service.saveSettings(settings);
    state = state.copyWith(settings: settings);
  }

  Future<void> toggleEnabled(bool value) async {
    final updated = state.settings.copyWith(enabled: value);
    await updateSettings(updated);
  }

  Future<void> toggleAlerts(bool value) async {
    final updated = state.settings.copyWith(alertsEnabled: value);
    await updateSettings(updated);
  }

  Future<void> toggleActions(bool value) async {
    final updated = state.settings.copyWith(actionsEnabled: value);
    await updateSettings(updated);
  }

  Future<void> toggleWeather(bool value) async {
    final updated = state.settings.copyWith(weatherEnabled: value);
    await updateSettings(updated);
  }

  Future<void> toggleCropHealth(bool value) async {
    final updated = state.settings.copyWith(cropHealthEnabled: value);
    await updateSettings(updated);
  }

  Future<void> toggleSound(bool value) async {
    final updated = state.settings.copyWith(soundEnabled: value);
    await updateSettings(updated);
  }

  Future<void> toggleVibration(bool value) async {
    final updated = state.settings.copyWith(vibrationEnabled: value);
    await updateSettings(updated);
  }
}

/// Settings Provider
final settingsProvider =
    StateNotifierProvider<SettingsNotifier, SettingsState>((ref) {
  final service = ref.watch(notificationServiceProvider);
  return SettingsNotifier(service);
});

/// Unread Count Provider (للاستخدام في الـ AppBar)
final unreadCountProvider = Provider<int>((ref) {
  return ref.watch(notificationsProvider).unreadCount;
});

/// Filtered Notifications Provider
final filteredNotificationsProvider =
    Provider<List<AppNotification>>((ref) {
  final notifications = ref.watch(notificationsProvider).notifications;
  final filter = ref.watch(notificationFilterProvider);

  if (filter == null) return notifications;
  return notifications.where((n) => n.type == filter).toList();
});

/// Notification Filter Provider
final notificationFilterProvider = StateProvider<String?>((ref) => null);
