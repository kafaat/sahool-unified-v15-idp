/// SAHOOL Notifications Controller
/// متحكم الإشعارات
///
/// State management for notifications using Riverpod StateNotifier
library;

import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/notifications_repository.dart';
import '../domain/models/notification.dart';
import '../domain/models/notification_action.dart';
import '../domain/models/notification_category.dart';
import '../domain/models/notification_settings.dart';
import 'notifications_providers.dart';

/// Notifications controller - manages notification state and operations
class NotificationsController extends StateNotifier<NotificationsState> {
  final NotificationsRepository _repository;

  StreamSubscription<List<AppNotification>>? _notificationsSubscription;
  StreamSubscription<int>? _unreadCountSubscription;
  StreamSubscription<AppNotification>? _newNotificationSubscription;

  NotificationsController(this._repository)
      : super(const NotificationsState()) {
    _initialize();
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Initialization
  // ─────────────────────────────────────────────────────────────────────────────

  void _initialize() {
    // Listen to notifications stream
    _notificationsSubscription = _repository.notificationsStream.listen(
      (notifications) {
        state = state.copyWith(
          notifications: notifications,
          isLoading: false,
          isRefreshing: false,
        );
      },
      onError: (Object error) {
        debugPrint('Notifications stream error: $error');
        state = state.copyWith(
          error: error.toString(),
          isLoading: false,
          isRefreshing: false,
        );
      },
    );

    // Listen to unread count stream
    _unreadCountSubscription = _repository.unreadCountStream.listen(
      (count) {
        state = state.copyWith(unreadCount: count);
      },
    );

    // Listen to new notifications
    _newNotificationSubscription = _repository.newNotificationStream.listen(
      (notification) {
        _handleNewNotification(notification);
      },
    );
  }

  /// Initialize repository with user
  Future<void> initializeForUser(String userId) async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      await _repository.initialize(userId: userId);
      await loadNotifications();
    } catch (e) {
      state = state.copyWith(
        error: e.toString(),
        isLoading: false,
      );
    }
  }

  void _handleNewNotification(AppNotification notification) {
    // Could trigger a local notification or update UI
    debugPrint('New notification received: ${notification.title}');
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Load Operations
  // ─────────────────────────────────────────────────────────────────────────────

  /// Load notifications with optional filters
  Future<void> loadNotifications({
    NotificationCategory? category,
    NotificationStatus? status,
    bool forceRefresh = false,
  }) async {
    state = state.copyWith(
      isLoading: state.notifications.isEmpty,
      clearError: true,
      selectedCategory: category,
    );

    try {
      final notifications = await _repository.getNotifications(
        category: category,
        status: status,
        forceRefresh: forceRefresh,
      );

      final unreadCount = await _repository.getUnreadCount(category: category);

      state = state.copyWith(
        notifications: notifications,
        unreadCount: unreadCount,
        isLoading: false,
        hasMore: notifications.length >= 100,
      );
    } catch (e) {
      state = state.copyWith(
        error: e.toString(),
        isLoading: false,
      );
    }
  }

  /// Refresh notifications (pull to refresh)
  Future<void> refreshNotifications({NotificationCategory? category}) async {
    state = state.copyWith(isRefreshing: true, clearError: true);

    try {
      await loadNotifications(
        category: category ?? state.selectedCategory,
        forceRefresh: true,
      );
    } finally {
      state = state.copyWith(isRefreshing: false);
    }
  }

  /// Load more notifications (pagination)
  Future<void> loadMoreNotifications() async {
    if (state.isLoading || !state.hasMore) return;

    state = state.copyWith(isLoading: true);

    try {
      final moreNotifications = await _repository.getNotifications(
        category: state.selectedCategory,
        limit: 100,
        offset: state.notifications.length,
      );

      state = state.copyWith(
        notifications: [...state.notifications, ...moreNotifications],
        isLoading: false,
        hasMore: moreNotifications.length >= 100,
      );
    } catch (e) {
      state = state.copyWith(
        error: e.toString(),
        isLoading: false,
      );
    }
  }

  /// Get single notification
  Future<AppNotification?> getNotification(String id) async {
    return _repository.getNotification(id);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Update Operations
  // ─────────────────────────────────────────────────────────────────────────────

  /// Mark notification as read
  Future<void> markAsRead(String id) async {
    try {
      await _repository.markAsRead(id);

      // Update local state
      final updated = state.notifications.map((n) {
        if (n.id == id) return n.markAsRead();
        return n;
      }).toList();

      state = state.copyWith(
        notifications: updated,
        unreadCount: state.unreadCount > 0 ? state.unreadCount - 1 : 0,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  /// Mark notification as unread
  Future<void> markAsUnread(String id) async {
    try {
      await _repository.markAsUnread(id);

      final updated = state.notifications.map((n) {
        if (n.id == id) return n.markAsUnread();
        return n;
      }).toList();

      state = state.copyWith(
        notifications: updated,
        unreadCount: state.unreadCount + 1,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  /// Mark all notifications as read
  Future<void> markAllAsRead({NotificationCategory? category}) async {
    try {
      await _repository.markAllAsRead(category: category);

      final updated = state.notifications.map((n) {
        if (category == null || n.category == category) {
          return n.markAsRead();
        }
        return n;
      }).toList();

      final unreadInCategory = category != null
          ? state.notifications
              .where((n) => n.category == category && n.isUnread)
              .length
          : state.unreadCount;

      state = state.copyWith(
        notifications: updated,
        unreadCount: state.unreadCount - unreadInCategory,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  /// Archive notification
  Future<void> archiveNotification(String id) async {
    try {
      await _repository.archiveNotification(id);

      final notification =
          state.notifications.firstWhere((n) => n.id == id);
      final wasUnread = notification.isUnread;

      final updated = state.notifications.where((n) => n.id != id).toList();

      state = state.copyWith(
        notifications: updated,
        unreadCount:
            wasUnread && state.unreadCount > 0 ? state.unreadCount - 1 : state.unreadCount,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  /// Delete notification
  Future<void> deleteNotification(String id) async {
    try {
      final notification =
          state.notifications.firstWhere((n) => n.id == id);
      final wasUnread = notification.isUnread;

      await _repository.deleteNotification(id);

      final updated = state.notifications.where((n) => n.id != id).toList();

      state = state.copyWith(
        notifications: updated,
        unreadCount:
            wasUnread && state.unreadCount > 0 ? state.unreadCount - 1 : state.unreadCount,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  /// Restore a previously deleted notification at its original position.
  /// Used by the undo action after a dismiss.
  void restoreNotification(AppNotification notification, int originalIndex) {
    final restoredList = List<AppNotification>.from(state.notifications);
    final insertIndex =
        originalIndex >= 0 && originalIndex <= restoredList.length
            ? originalIndex
            : 0;
    restoredList.insert(insertIndex, notification);

    state = state.copyWith(
      notifications: restoredList,
      unreadCount: notification.isUnread
          ? state.unreadCount + 1
          : state.unreadCount,
    );
  }

  /// Delete multiple notifications
  Future<void> deleteNotifications(List<String> ids) async {
    try {
      await _repository.deleteNotifications(ids);

      final unreadCount = state.notifications
          .where((n) => ids.contains(n.id) && n.isUnread)
          .length;

      final updated =
          state.notifications.where((n) => !ids.contains(n.id)).toList();

      state = state.copyWith(
        notifications: updated,
        unreadCount: state.unreadCount - unreadCount,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  /// Snooze notification
  Future<void> snoozeNotification(
    String id, {
    required Duration duration,
  }) async {
    try {
      await _repository.snoozeNotification(id, duration: duration);

      final notification =
          state.notifications.firstWhere((n) => n.id == id);
      final wasUnread = notification.isUnread;

      final updated = state.notifications.map((n) {
        if (n.id == id) return n.snooze(duration);
        return n;
      }).toList();

      state = state.copyWith(
        notifications: updated,
        unreadCount:
            wasUnread && state.unreadCount > 0 ? state.unreadCount - 1 : state.unreadCount,
      );
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Actions
  // ─────────────────────────────────────────────────────────────────────────────

  /// Execute notification action
  Future<void> executeAction(
    String notificationId,
    NotificationAction action, {
    Map<String, dynamic>? params,
  }) async {
    try {
      await _repository.executeAction(
        notificationId,
        action,
        params: params,
      );

      // Handle post-action state updates based on action type
      switch (action.type) {
        case NotificationActionType.dismiss:
          await deleteNotification(notificationId);
          break;

        case NotificationActionType.markDone:
        case NotificationActionType.acknowledge:
          await markAsRead(notificationId);
          break;

        case NotificationActionType.snooze:
          final minutes = (action.params?['duration_minutes'] as int?) ?? 30;
          await snoozeNotification(
            notificationId,
            duration: Duration(minutes: minutes),
          );
          break;

        default:
          // For other actions, just mark as read
          await markAsRead(notificationId);
          break;
      }
    } catch (e) {
      state = state.copyWith(error: e.toString());
      rethrow;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Settings
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get notification settings
  Future<NotificationSettingsModel> getSettings() async {
    return _repository.getSettings();
  }

  /// Save notification settings
  Future<void> saveSettings(NotificationSettingsModel settings) async {
    await _repository.saveSettings(settings);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Sync
  // ─────────────────────────────────────────────────────────────────────────────

  /// Set online status
  void setOnlineStatus(bool isOnline) {
    _repository.setOnlineStatus(isOnline);
  }

  /// Manual sync
  Future<void> sync() async {
    state = state.copyWith(isRefreshing: true);

    try {
      await _repository.syncWithServer();
      await loadNotifications(forceRefresh: true);
    } finally {
      state = state.copyWith(isRefreshing: false);
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Push Notifications
  // ─────────────────────────────────────────────────────────────────────────────

  /// Handle incoming push notification
  Future<void> handlePushNotification(Map<String, dynamic> data) async {
    await _repository.handlePushNotification(data);
  }

  /// Handle incoming WebSocket notification
  Future<void> handleWebSocketNotification(Map<String, dynamic> data) async {
    await _repository.handleWebSocketNotification(data);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Filter & Selection
  // ─────────────────────────────────────────────────────────────────────────────

  /// Filter by category
  void filterByCategory(NotificationCategory? category) {
    loadNotifications(category: category);
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(clearError: true);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Cleanup
  // ─────────────────────────────────────────────────────────────────────────────

  @override
  void dispose() {
    _notificationsSubscription?.cancel();
    _unreadCountSubscription?.cancel();
    _newNotificationSubscription?.cancel();
    _repository.dispose();
    super.dispose();
  }
}
