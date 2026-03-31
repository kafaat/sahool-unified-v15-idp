/// SAHOOL Notifications Providers
/// مزودات الإشعارات
///
/// Riverpod providers for notifications feature
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/notifications_api.dart';
import '../data/notifications_local_db.dart';
import '../data/notifications_repository.dart';
import '../domain/models/notification.dart';
import '../domain/models/notification_category.dart';
import '../domain/models/notification_settings.dart';
import 'notifications_controller.dart';

// ─────────────────────────────────────────────────────────────────────────────
// Core Providers
// ─────────────────────────────────────────────────────────────────────────────

/// Dio provider (should be provided from app level)
final dioProvider = Provider<Dio>((ref) {
  // This should be overridden at app level with configured Dio
  return Dio(BaseOptions(
    baseUrl: 'https://api.sahool.app',
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
  ));
});

/// Notifications API provider
final notificationsApiProvider = Provider<NotificationsApi>((ref) {
  final dio = ref.watch(dioProvider);
  return NotificationsApi(dio: dio);
});

/// Notifications local database provider
final notificationsLocalDbProvider = Provider<NotificationsLocalDb>((ref) {
  return NotificationsLocalDb();
});

/// Notifications repository provider
final notificationsRepositoryProvider = Provider<NotificationsRepository>((ref) {
  final api = ref.watch(notificationsApiProvider);
  final localDb = ref.watch(notificationsLocalDbProvider);
  return NotificationsRepository(api: api, localDb: localDb);
});

// ─────────────────────────────────────────────────────────────────────────────
// State Providers
// ─────────────────────────────────────────────────────────────────────────────

/// Notifications state
class NotificationsState {
  final List<AppNotification> notifications;
  final bool isLoading;
  final bool isRefreshing;
  final String? error;
  final int unreadCount;
  final NotificationCategory? selectedCategory;
  final bool hasMore;

  const NotificationsState({
    this.notifications = const [],
    this.isLoading = false,
    this.isRefreshing = false,
    this.error,
    this.unreadCount = 0,
    this.selectedCategory,
    this.hasMore = false,
  });

  NotificationsState copyWith({
    List<AppNotification>? notifications,
    bool? isLoading,
    bool? isRefreshing,
    String? error,
    int? unreadCount,
    NotificationCategory? selectedCategory,
    bool? hasMore,
    bool clearError = false,
    bool clearSelectedCategory = false,
  }) {
    return NotificationsState(
      notifications: notifications ?? this.notifications,
      isLoading: isLoading ?? this.isLoading,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      error: clearError ? null : (error ?? this.error),
      unreadCount: unreadCount ?? this.unreadCount,
      selectedCategory: clearSelectedCategory
          ? null
          : (selectedCategory ?? this.selectedCategory),
      hasMore: hasMore ?? this.hasMore,
    );
  }
}

/// Main notifications controller provider
final notificationsControllerProvider =
    StateNotifierProvider<NotificationsController, NotificationsState>((ref) {
  final repository = ref.watch(notificationsRepositoryProvider);
  return NotificationsController(repository);
});

// ─────────────────────────────────────────────────────────────────────────────
// Derived Providers
// ─────────────────────────────────────────────────────────────────────────────

/// Unread count provider
final unreadCountProvider = Provider<int>((ref) {
  return ref.watch(
    notificationsControllerProvider.select((state) => state.unreadCount),
  );
});

/// Unread count by category provider
final unreadCountByCategoryProvider =
    Provider<Map<NotificationCategory, int>>((ref) {
  final notifications = ref.watch(
    notificationsControllerProvider.select((state) => state.notifications),
  );

  final counts = <NotificationCategory, int>{};
  for (final notification in notifications) {
    if (notification.isUnread) {
      counts[notification.category] =
          (counts[notification.category] ?? 0) + 1;
    }
  }
  return counts;
});

/// Filtered notifications by category provider
final filteredNotificationsProvider =
    Provider.family<List<AppNotification>, NotificationCategory?>((ref, category) {
  final notifications = ref.watch(
    notificationsControllerProvider.select((state) => state.notifications),
  );

  if (category == null) return notifications;
  return notifications.where((n) => n.category == category).toList();
});

/// Unread notifications provider
final unreadNotificationsProvider = Provider<List<AppNotification>>((ref) {
  final notifications = ref.watch(
    notificationsControllerProvider.select((state) => state.notifications),
  );
  return notifications.where((n) => n.isUnread).toList();
});

/// High priority notifications provider
final highPriorityNotificationsProvider = Provider<List<AppNotification>>((ref) {
  final notifications = ref.watch(
    notificationsControllerProvider.select((state) => state.notifications),
  );
  return notifications.where((n) => n.isHighPriority).toList();
});

/// Recent notifications (last 24 hours)
final recentNotificationsProvider = Provider<List<AppNotification>>((ref) {
  final notifications = ref.watch(
    notificationsControllerProvider.select((state) => state.notifications),
  );
  final yesterday = DateTime.now().subtract(const Duration(days: 1));
  return notifications.where((n) => n.createdAt.isAfter(yesterday)).toList();
});

// ─────────────────────────────────────────────────────────────────────────────
// Stream Providers
// ─────────────────────────────────────────────────────────────────────────────

/// Notifications stream provider
final notificationsStreamProvider = StreamProvider<List<AppNotification>>((ref) {
  final repository = ref.watch(notificationsRepositoryProvider);
  return repository.notificationsStream;
});

/// Unread count stream provider
final unreadCountStreamProvider = StreamProvider<int>((ref) {
  final repository = ref.watch(notificationsRepositoryProvider);
  return repository.unreadCountStream;
});

/// New notification stream provider
final newNotificationStreamProvider = StreamProvider<AppNotification>((ref) {
  final repository = ref.watch(notificationsRepositoryProvider);
  return repository.newNotificationStream;
});

// ─────────────────────────────────────────────────────────────────────────────
// Settings Providers
// ─────────────────────────────────────────────────────────────────────────────

/// Notification settings provider
final notificationSettingsProvider =
    FutureProvider<NotificationSettingsModel>((ref) async {
  final controller = ref.watch(notificationsControllerProvider.notifier);
  return controller.getSettings();
});

/// Quiet hours status provider
final isInQuietHoursProvider = Provider<bool>((ref) {
  final settingsAsync = ref.watch(notificationSettingsProvider);
  return settingsAsync.when(
    data: (settings) => settings.isInQuietHours,
    loading: () => false,
    error: (_, __) => false,
  );
});

// ─────────────────────────────────────────────────────────────────────────────
// Single Notification Provider
// ─────────────────────────────────────────────────────────────────────────────

/// Get single notification by ID
final notificationByIdProvider =
    Provider.family<AppNotification?, String>((ref, id) {
  final notifications = ref.watch(
    notificationsControllerProvider.select((state) => state.notifications),
  );
  try {
    return notifications.firstWhere((n) => n.id == id);
  } catch (e) {
    return null;
  }
});

/// Fetch notification by ID (async)
final fetchNotificationProvider =
    FutureProvider.family<AppNotification?, String>((ref, id) async {
  final controller = ref.watch(notificationsControllerProvider.notifier);
  return controller.getNotification(id);
});
