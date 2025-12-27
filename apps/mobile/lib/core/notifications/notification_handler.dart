/// SAHOOL Notification Handler
/// معالج الإشعارات
///
/// Handles notification taps and routes to appropriate screens
/// Manages notification badge counts and read status

import 'package:flutter/material.dart';

import 'firebase_messaging_service.dart';

/// Navigation action for notifications
class NotificationAction {
  final String route;
  final Map<String, dynamic>? arguments;

  const NotificationAction({
    required this.route,
    this.arguments,
  });
}

/// Notification Handler
/// Routes notifications to appropriate screens and manages state
class NotificationHandler {
  static NotificationHandler? _instance;
  static NotificationHandler get instance {
    _instance ??= NotificationHandler._();
    return _instance!;
  }

  NotificationHandler._();

  /// Global navigator key for routing
  GlobalKey<NavigatorState>? _navigatorKey;

  /// Unread notification count
  int _unreadCount = 0;
  int get unreadCount => _unreadCount;

  /// Notification count stream
  final _countController = Stream<int>.empty();
  Stream<int> get onCountChanged => _countController;

  /// Initialize with navigator key
  void initialize(GlobalKey<NavigatorState> navigatorKey) {
    _navigatorKey = navigatorKey;
    _listenToNotifications();
  }

  /// Listen to notification stream
  void _listenToNotifications() {
    FirebaseMessagingService.instance.onNotification.listen((payload) {
      // Increment unread count for background notifications
      if (!payload.tapped) {
        _incrementUnreadCount();
      }

      // Handle notification tap
      if (payload.tapped) {
        handleNotificationTap(payload);
      }
    });
  }

  /// Handle notification tap
  Future<void> handleNotificationTap(SAHOOLNotificationPayload payload) async {
    final action = _getActionForNotification(payload);

    if (action == null) {
      debugPrint('⚠️ No action defined for notification type: ${payload.type}');
      return;
    }

    // Navigate to appropriate screen
    await navigateToScreen(action.route, arguments: action.arguments);

    // Mark as read
    _decrementUnreadCount();
  }

  /// Get navigation action for notification type
  NotificationAction? _getActionForNotification(SAHOOLNotificationPayload payload) {
    // Check for custom action URL
    if (payload.actionUrl != null) {
      return _parseActionUrl(payload.actionUrl!);
    }

    // Default routes based on notification type
    switch (payload.type) {
      // Weather alerts
      case SAHOOLNotificationType.weatherAlert:
        return const NotificationAction(
          route: '/weather',
          arguments: {'tab': 'alerts'},
        );

      // Field-related notifications
      case SAHOOLNotificationType.fieldUpdate:
      case SAHOOLNotificationType.cropHealth:
      case SAHOOLNotificationType.satelliteReady:
        if (payload.fieldId != null) {
          return NotificationAction(
            route: '/field/details',
            arguments: {
              'fieldId': payload.fieldId,
              'tab': _getFieldTab(payload.type),
            },
          );
        }
        return const NotificationAction(route: '/fields');

      // Disease detection
      case SAHOOLNotificationType.diseaseDetected:
        if (payload.fieldId != null) {
          return NotificationAction(
            route: '/field/details',
            arguments: {
              'fieldId': payload.fieldId,
              'tab': 'health',
            },
          );
        }
        return const NotificationAction(route: '/fields');

      // Pest outbreak
      case SAHOOLNotificationType.pestOutbreak:
        return NotificationAction(
          route: '/alerts',
          arguments: {
            'type': 'pest',
            'data': payload.data,
          },
        );

      // Spray window
      case SAHOOLNotificationType.sprayWindow:
        if (payload.fieldId != null) {
          return NotificationAction(
            route: '/field/spray',
            arguments: {
              'fieldId': payload.fieldId,
              'data': payload.data,
            },
          );
        }
        return const NotificationAction(route: '/tasks');

      // Harvest reminder
      case SAHOOLNotificationType.harvestReminder:
        if (payload.fieldId != null) {
          return NotificationAction(
            route: '/field/harvest',
            arguments: {
              'fieldId': payload.fieldId,
              'data': payload.data,
            },
          );
        }
        return const NotificationAction(route: '/tasks');

      // Irrigation reminder
      case SAHOOLNotificationType.irrigationReminder:
        if (payload.fieldId != null) {
          return NotificationAction(
            route: '/field/irrigation',
            arguments: {
              'fieldId': payload.fieldId,
            },
          );
        }
        return const NotificationAction(route: '/irrigation');

      // Task reminder
      case SAHOOLNotificationType.taskReminder:
        final taskId = payload.data['task_id'] as String?;
        if (taskId != null) {
          return NotificationAction(
            route: '/task/details',
            arguments: {'taskId': taskId},
          );
        }
        return const NotificationAction(route: '/tasks');

      // Market price
      case SAHOOLNotificationType.marketPrice:
        return NotificationAction(
          route: '/market',
          arguments: {
            'crop': payload.cropType,
            'data': payload.data,
          },
        );

      // Payment due
      case SAHOOLNotificationType.paymentDue:
        return NotificationAction(
          route: '/payments',
          arguments: {'data': payload.data},
        );

      // Low stock
      case SAHOOLNotificationType.lowStock:
        final itemId = payload.data['item_id'] as String?;
        if (itemId != null) {
          return NotificationAction(
            route: '/inventory/item',
            arguments: {'itemId': itemId},
          );
        }
        return const NotificationAction(route: '/inventory');

      // System notifications
      case SAHOOLNotificationType.system:
        return const NotificationAction(route: '/notifications');
    }
  }

  /// Get field tab based on notification type
  String _getFieldTab(SAHOOLNotificationType type) {
    switch (type) {
      case SAHOOLNotificationType.satelliteReady:
        return 'satellite';
      case SAHOOLNotificationType.cropHealth:
        return 'health';
      case SAHOOLNotificationType.fieldUpdate:
        return 'overview';
      default:
        return 'overview';
    }
  }

  /// Parse action URL
  /// Format: /route?param1=value1&param2=value2
  NotificationAction? _parseActionUrl(String url) {
    try {
      final uri = Uri.parse(url);
      return NotificationAction(
        route: uri.path,
        arguments: uri.queryParameters,
      );
    } catch (e) {
      debugPrint('❌ Failed to parse action URL: $url');
      return null;
    }
  }

  /// Navigate to screen
  Future<void> navigateToScreen(
    String route, {
    Map<String, dynamic>? arguments,
  }) async {
    if (_navigatorKey?.currentState == null) {
      debugPrint('⚠️ Navigator not available');
      return;
    }

    try {
      await _navigatorKey!.currentState!.pushNamed(
        route,
        arguments: arguments,
      );
      debugPrint('📱 Navigated to: $route');
    } catch (e) {
      debugPrint('❌ Navigation failed: $e');
      // Fallback to home
      _navigatorKey!.currentState!.pushNamed('/');
    }
  }

  /// Increment unread count
  void _incrementUnreadCount() {
    _unreadCount++;
    _updateBadge();
  }

  /// Decrement unread count
  void _decrementUnreadCount() {
    if (_unreadCount > 0) {
      _unreadCount--;
      _updateBadge();
    }
  }

  /// Reset unread count
  void resetUnreadCount() {
    _unreadCount = 0;
    _updateBadge();
  }

  /// Update app badge
  void _updateBadge() {
    // Update platform badge
    // This requires flutter_local_notifications or similar
    debugPrint('📛 Badge count: $_unreadCount');
  }

  /// Mark notification as read
  Future<void> markAsRead(String notificationId) async {
    // TODO: Call API to mark notification as read
    _decrementUnreadCount();
  }

  /// Mark all as read
  Future<void> markAllAsRead() async {
    // TODO: Call API to mark all notifications as read
    resetUnreadCount();
  }
}

/// Extension for easy notification handling in widgets
extension NotificationHandlerExtension on BuildContext {
  /// Handle notification tap from any widget
  Future<void> handleNotification(SAHOOLNotificationPayload payload) async {
    await NotificationHandler.instance.handleNotificationTap(payload);
  }

  /// Navigate to notification screen
  Future<void> goToNotificationScreen(String route, {Map<String, dynamic>? args}) async {
    await NotificationHandler.instance.navigateToScreen(route, arguments: args);
  }
}

/// Notification list item widget
class NotificationListItem extends StatelessWidget {
  final SAHOOLNotificationPayload notification;
  final bool isRead;
  final VoidCallback? onTap;
  final VoidCallback? onDismiss;

  const NotificationListItem({
    super.key,
    required this.notification,
    this.isRead = false,
    this.onTap,
    this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    return Dismissible(
      key: Key(notification.id),
      direction: DismissDirection.endToStart,
      onDismissed: (direction) => onDismiss?.call(),
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        color: Colors.red,
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      child: ListTile(
        leading: CircleAvatar(
          child: Text(notification.type.icon),
        ),
        title: Text(
          notification.title,
          style: TextStyle(
            fontWeight: isRead ? FontWeight.normal : FontWeight.bold,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              notification.body,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            Text(
              _formatTime(notification.receivedAt),
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
        trailing: !isRead
            ? Container(
                width: 8,
                height: 8,
                decoration: const BoxDecoration(
                  color: Colors.blue,
                  shape: BoxShape.circle,
                ),
              )
            : null,
        onTap: () {
          onTap?.call();
          context.handleNotification(notification);
        },
      ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inMinutes < 1) {
      return 'الآن';
    } else if (diff.inHours < 1) {
      return 'منذ ${diff.inMinutes} دقيقة';
    } else if (diff.inDays < 1) {
      return 'منذ ${diff.inHours} ساعة';
    } else if (diff.inDays < 7) {
      return 'منذ ${diff.inDays} يوم';
    } else {
      return '${time.day}/${time.month}/${time.year}';
    }
  }
}

/// Notification badge widget
class NotificationBadge extends StatelessWidget {
  final int count;
  final Widget child;

  const NotificationBadge({
    super.key,
    required this.count,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (count > 0)
          Positioned(
            right: 0,
            top: 0,
            child: Container(
              padding: const EdgeInsets.all(4),
              decoration: BoxDecoration(
                color: Colors.red,
                borderRadius: BorderRadius.circular(10),
              ),
              constraints: const BoxConstraints(
                minWidth: 20,
                minHeight: 20,
              ),
              child: Text(
                count > 99 ? '99+' : count.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
      ],
    );
  }
}
