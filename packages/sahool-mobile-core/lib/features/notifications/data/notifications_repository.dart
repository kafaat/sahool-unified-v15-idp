/// SAHOOL Notifications Repository
/// مستودع الإشعارات
///
/// Combines API and local database for offline-first notifications
/// with automatic sync and conflict resolution
library;

import 'dart:async';
import 'package:flutter/foundation.dart';

import '../domain/models/notification.dart';
import '../domain/models/notification_category.dart';
import '../domain/models/notification_action.dart';
import '../domain/models/notification_settings.dart';
import 'notifications_api.dart';
import 'notifications_local_db.dart';

/// Notifications repository with offline-first support
class NotificationsRepository {
  final NotificationsApi _api;
  final NotificationsLocalDb _localDb;

  // Stream controllers
  final _notificationsController =
      StreamController<List<AppNotification>>.broadcast();
  final _unreadCountController = StreamController<int>.broadcast();
  final _newNotificationController = StreamController<AppNotification>.broadcast();

  // Cache
  List<AppNotification> _cachedNotifications = [];
  int _cachedUnreadCount = 0;
  Map<NotificationCategory, int> _cachedUnreadByCategory = {};
  bool _isOnline = true;
  String? _currentUserId;

  NotificationsRepository({
    required NotificationsApi api,
    required NotificationsLocalDb localDb,
  })  : _api = api,
        _localDb = localDb;

  // ─────────────────────────────────────────────────────────────────────────────
  // Streams
  // ─────────────────────────────────────────────────────────────────────────────

  /// Stream of notifications
  Stream<List<AppNotification>> get notificationsStream =>
      _notificationsController.stream;

  /// Stream of unread count
  Stream<int> get unreadCountStream => _unreadCountController.stream;

  /// Stream of new notifications
  Stream<AppNotification> get newNotificationStream =>
      _newNotificationController.stream;

  /// Current cached notifications
  List<AppNotification> get cachedNotifications =>
      List.unmodifiable(_cachedNotifications);

  /// Current cached unread count
  int get cachedUnreadCount => _cachedUnreadCount;

  /// Unread count by category
  Map<NotificationCategory, int> get unreadByCategory =>
      Map.unmodifiable(_cachedUnreadByCategory);

  // ─────────────────────────────────────────────────────────────────────────────
  // Initialization
  // ─────────────────────────────────────────────────────────────────────────────

  /// Initialize repository for a user
  Future<void> initialize({required String userId}) async {
    _currentUserId = userId;

    // Initialize local database
    await _localDb.initialize();

    // Load from local first (offline-first)
    await _loadFromLocal();

    // Try to sync with server
    await syncWithServer();
  }

  /// Set online status
  void setOnlineStatus(bool isOnline) {
    _isOnline = isOnline;
    if (isOnline) {
      // Sync when coming back online
      syncWithServer();
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Fetch Notifications
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get notifications with optional filters
  Future<List<AppNotification>> getNotifications({
    NotificationCategory? category,
    NotificationStatus? status,
    bool forceRefresh = false,
    int limit = 100,
    int offset = 0,
  }) async {
    if (_currentUserId == null) {
      throw StateError('Repository not initialized');
    }

    // If force refresh and online, fetch from API first
    if (forceRefresh && _isOnline) {
      try {
        final response = await _api.getNotifications(
          category: category,
          status: status,
          limit: limit,
          page: (offset ~/ limit) + 1,
        );

        // Save to local database
        await _localDb.upsertNotifications(response.notifications);

        // Update cache
        _cachedNotifications = response.notifications;
      } catch (e) {
        debugPrint('Failed to fetch from API, using local: $e');
      }
    }

    // Always read from local database for consistency
    final notifications = await _localDb.getNotifications(
      userId: _currentUserId!,
      category: category,
      status: status,
      limit: limit,
      offset: offset,
    );

    // Update cache if fetching all
    if (category == null && status == null && offset == 0) {
      _cachedNotifications = notifications;
      _notificationsController.add(notifications);
    }

    return notifications;
  }

  /// Get a single notification
  Future<AppNotification?> getNotification(String id) async {
    // Try local first
    var notification = await _localDb.getNotification(id);

    // If not found locally and online, try API
    if (notification == null && _isOnline) {
      try {
        notification = await _api.getNotification(id);
        await _localDb.upsertNotification(notification);
            } catch (e) {
        debugPrint('Failed to fetch notification from API: $e');
      }
    }

    return notification;
  }

  /// Get unread count
  Future<int> getUnreadCount({NotificationCategory? category}) async {
    if (_currentUserId == null) return 0;

    // Get from local
    final count = await _localDb.getUnreadCount(
      userId: _currentUserId!,
      category: category,
    );

    if (category == null) {
      _cachedUnreadCount = count;
      _unreadCountController.add(count);
    }

    return count;
  }

  /// Get unread count by category
  Future<Map<NotificationCategory, int>> getUnreadCountByCategory() async {
    if (_currentUserId == null) return {};

    final counts = await _localDb.getUnreadCountByCategory(
      userId: _currentUserId!,
    );

    _cachedUnreadByCategory = counts;
    return counts;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Update Notifications
  // ─────────────────────────────────────────────────────────────────────────────

  /// Mark notification as read
  Future<AppNotification?> markAsRead(String id) async {
    // Update local first
    await _localDb.updateStatus(id, NotificationStatus.read);

    // Update cache
    final index = _cachedNotifications.indexWhere((n) => n.id == id);
    if (index != -1) {
      _cachedNotifications[index] = _cachedNotifications[index].markAsRead();
      _notificationsController.add(_cachedNotifications);
    }

    // Update unread count
    await _updateUnreadCount();

    // Sync with server if online
    if (_isOnline) {
      try {
        final updated = await _api.markAsRead(id);
        await _localDb.upsertNotification(updated.copyWith(synced: true));
        return updated;
      } catch (e) {
        debugPrint('Failed to mark as read on server: $e');
      }
    }

    return _localDb.getNotification(id);
  }

  /// Mark notification as unread
  Future<AppNotification?> markAsUnread(String id) async {
    await _localDb.updateStatus(id, NotificationStatus.unread);

    final index = _cachedNotifications.indexWhere((n) => n.id == id);
    if (index != -1) {
      _cachedNotifications[index] = _cachedNotifications[index].markAsUnread();
      _notificationsController.add(_cachedNotifications);
    }

    await _updateUnreadCount();

    if (_isOnline) {
      try {
        final updated = await _api.markAsUnread(id);
        await _localDb.upsertNotification(updated.copyWith(synced: true));
        return updated;
      } catch (e) {
        debugPrint('Failed to mark as unread on server: $e');
      }
    }

    return _localDb.getNotification(id);
  }

  /// Mark all as read
  Future<int> markAllAsRead({NotificationCategory? category}) async {
    if (_currentUserId == null) return 0;

    final count = await _localDb.markAllAsRead(
      userId: _currentUserId!,
      category: category,
    );

    // Update cache
    for (var i = 0; i < _cachedNotifications.length; i++) {
      if (_cachedNotifications[i].isUnread) {
        if (category == null ||
            _cachedNotifications[i].category == category) {
          _cachedNotifications[i] = _cachedNotifications[i].markAsRead();
        }
      }
    }
    _notificationsController.add(_cachedNotifications);

    await _updateUnreadCount();

    if (_isOnline) {
      try {
        await _api.markAllAsRead(category: category);
      } catch (e) {
        debugPrint('Failed to mark all as read on server: $e');
      }
    }

    return count;
  }

  /// Archive notification
  Future<AppNotification?> archiveNotification(String id) async {
    await _localDb.updateStatus(id, NotificationStatus.archived);

    _cachedNotifications.removeWhere((n) => n.id == id);
    _notificationsController.add(_cachedNotifications);

    await _updateUnreadCount();

    if (_isOnline) {
      try {
        final updated = await _api.archiveNotification(id);
        await _localDb.upsertNotification(updated.copyWith(synced: true));
        return updated;
      } catch (e) {
        debugPrint('Failed to archive on server: $e');
      }
    }

    return _localDb.getNotification(id);
  }

  /// Delete notification
  Future<void> deleteNotification(String id) async {
    await _localDb.deleteNotification(id);

    _cachedNotifications.removeWhere((n) => n.id == id);
    _notificationsController.add(_cachedNotifications);

    await _updateUnreadCount();

    if (_isOnline) {
      try {
        await _api.deleteNotification(id);
      } catch (e) {
        debugPrint('Failed to delete on server: $e');
      }
    }
  }

  /// Delete multiple notifications
  Future<void> deleteNotifications(List<String> ids) async {
    for (final id in ids) {
      await _localDb.deleteNotification(id);
    }

    _cachedNotifications.removeWhere((n) => ids.contains(n.id));
    _notificationsController.add(_cachedNotifications);

    await _updateUnreadCount();

    if (_isOnline) {
      try {
        await _api.deleteNotifications(ids);
      } catch (e) {
        debugPrint('Failed to delete on server: $e');
      }
    }
  }

  /// Snooze notification
  Future<AppNotification?> snoozeNotification(
    String id, {
    required Duration duration,
  }) async {
    final until = DateTime.now().add(duration);
    await _localDb.snoozeNotification(id, until);

    final index = _cachedNotifications.indexWhere((n) => n.id == id);
    if (index != -1) {
      _cachedNotifications[index] = _cachedNotifications[index].snooze(duration);
      _notificationsController.add(_cachedNotifications);
    }

    await _updateUnreadCount();

    if (_isOnline) {
      try {
        final updated = await _api.snoozeNotification(
          id,
          durationMinutes: duration.inMinutes,
        );
        await _localDb.upsertNotification(updated.copyWith(synced: true));
        return updated;
      } catch (e) {
        debugPrint('Failed to snooze on server: $e');
      }
    }

    return _localDb.getNotification(id);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Actions
  // ─────────────────────────────────────────────────────────────────────────────

  /// Execute notification action
  Future<ActionResponse?> executeAction(
    String notificationId,
    NotificationAction action, {
    Map<String, dynamic>? params,
  }) async {
    // Handle local actions first
    switch (action.type) {
      case NotificationActionType.dismiss:
        await deleteNotification(notificationId);
        return const ActionResponse(success: true);

      case NotificationActionType.snooze:
        final minutes = (action.params?['duration_minutes'] as int?) ?? 30;
        await snoozeNotification(
          notificationId,
          duration: Duration(minutes: minutes),
        );
        return const ActionResponse(success: true);

      case NotificationActionType.markDone:
        await markAsRead(notificationId);
        return const ActionResponse(success: true);

      case NotificationActionType.acknowledge:
        await markAsRead(notificationId);
        break;

      default:
        break;
    }

    // Execute on server if online
    if (_isOnline) {
      try {
        return await _api.executeAction(
          notificationId,
          action.id,
          params: params ?? action.params,
        );
      } catch (e) {
        debugPrint('Failed to execute action on server: $e');
      }
    }

    return null;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Settings
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get notification settings
  Future<NotificationSettingsModel> getSettings() async {
    if (_currentUserId == null) {
      return NotificationSettingsModel.defaultSettings();
    }

    final settings = await _localDb.getSettings(userId: _currentUserId!);
    return settings ?? NotificationSettingsModel.defaultSettings();
  }

  /// Save notification settings
  Future<void> saveSettings(NotificationSettingsModel settings) async {
    if (_currentUserId == null) return;

    await _localDb.saveSettings(
      userId: _currentUserId!,
      settings: settings,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Sync
  // ─────────────────────────────────────────────────────────────────────────────

  /// Sync with server
  Future<void> syncWithServer() async {
    if (!_isOnline || _currentUserId == null) return;

    try {
      // Push local changes
      await _pushLocalChanges();

      // Pull server changes
      await _pullServerChanges();
    } catch (e) {
      debugPrint('Sync failed: $e');
    }
  }

  Future<void> _pushLocalChanges() async {
    if (_currentUserId == null) return;

    final unsynced = await _localDb.getUnsyncedNotifications(
      userId: _currentUserId!,
    );

    if (unsynced.isEmpty) return;

    debugPrint('Pushing ${unsynced.length} local changes');

    for (final notification in unsynced) {
      try {
        switch (notification.status) {
          case NotificationStatus.read:
            await _api.markAsRead(notification.id);
            break;
          case NotificationStatus.archived:
            await _api.archiveNotification(notification.id);
            break;
          case NotificationStatus.deleted:
            await _api.deleteNotification(notification.id);
            break;
          case NotificationStatus.snoozed:
            if (notification.snoozedUntil != null) {
              final duration =
                  notification.snoozedUntil!.difference(DateTime.now());
              if (duration.isNegative) continue;
              await _api.snoozeNotification(
                notification.id,
                durationMinutes: duration.inMinutes,
              );
            }
            break;
          default:
            break;
        }

        await _localDb.markAsSynced([notification.id]);
      } catch (e) {
        debugPrint('Failed to sync notification ${notification.id}: $e');
      }
    }
  }

  Future<void> _pullServerChanges() async {
    try {
      final response = await _api.getNotifications(limit: 100);
      await _localDb.upsertNotifications(
        response.notifications.map((n) => n.copyWith(synced: true)).toList(),
      );

      // Update unread counts
      final unreadResponse = await _api.getUnreadCount();
      _cachedUnreadCount = unreadResponse.total;
      _cachedUnreadByCategory = unreadResponse.byCategory;
      _unreadCountController.add(_cachedUnreadCount);

      // Reload from local
      await _loadFromLocal();
    } catch (e) {
      debugPrint('Failed to pull server changes: $e');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Incoming Notifications
  // ─────────────────────────────────────────────────────────────────────────────

  /// Handle incoming push notification
  Future<void> handlePushNotification(Map<String, dynamic> data) async {
    try {
      final notification = AppNotification.fromJson({
        ...data,
        'source': 'push',
        'synced': true,
      });

      await _localDb.upsertNotification(notification);

      _cachedNotifications.insert(0, notification);
      _notificationsController.add(_cachedNotifications);

      await _updateUnreadCount();

      _newNotificationController.add(notification);
    } catch (e) {
      debugPrint('Failed to handle push notification: $e');
    }
  }

  /// Handle incoming WebSocket notification
  Future<void> handleWebSocketNotification(Map<String, dynamic> data) async {
    try {
      final notification = AppNotification.fromJson({
        ...data,
        'source': 'websocket',
        'synced': true,
      });

      await _localDb.upsertNotification(notification);

      // Check if already exists
      final existingIndex =
          _cachedNotifications.indexWhere((n) => n.id == notification.id);
      if (existingIndex != -1) {
        _cachedNotifications[existingIndex] = notification;
      } else {
        _cachedNotifications.insert(0, notification);
      }
      _notificationsController.add(_cachedNotifications);

      await _updateUnreadCount();

      if (existingIndex == -1) {
        _newNotificationController.add(notification);
      }
    } catch (e) {
      debugPrint('Failed to handle WebSocket notification: $e');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Helpers
  // ─────────────────────────────────────────────────────────────────────────────

  Future<void> _loadFromLocal() async {
    if (_currentUserId == null) return;

    _cachedNotifications = await _localDb.getNotifications(
      userId: _currentUserId!,
      limit: 100,
    );
    _notificationsController.add(_cachedNotifications);

    await _updateUnreadCount();
  }

  Future<void> _updateUnreadCount() async {
    if (_currentUserId == null) return;

    _cachedUnreadCount = await _localDb.getUnreadCount(
      userId: _currentUserId!,
    );
    _unreadCountController.add(_cachedUnreadCount);

    _cachedUnreadByCategory = await _localDb.getUnreadCountByCategory(
      userId: _currentUserId!,
    );
  }

  /// Clear all cached data
  void clearCache() {
    _cachedNotifications = [];
    _cachedUnreadCount = 0;
    _cachedUnreadByCategory = {};
    _notificationsController.add([]);
    _unreadCountController.add(0);
  }

  /// Dispose resources
  Future<void> dispose() async {
    await _notificationsController.close();
    await _unreadCountController.close();
    await _newNotificationController.close();
    await _localDb.close();
  }
}
