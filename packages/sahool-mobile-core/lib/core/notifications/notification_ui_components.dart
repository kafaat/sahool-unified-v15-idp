/// SAHOOL Notification UI Components
/// مكونات واجهة المستخدم للإشعارات
///
/// Features:
/// - In-app notification banner
/// - Notification badge with animation
/// - Notification list item
/// - Grouped notifications
/// - Action buttons
library;

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../config/theme.dart';
import '../ui/enhanced_widgets.dart';

// =============================================================================
// In-App Notification Banner - شريط إشعار داخل التطبيق
// =============================================================================

/// Overlay notification banner that slides in from top
/// شريط إشعار متراكب ينزلق من الأعلى
class InAppNotificationBanner extends StatefulWidget {
  final String title;
  final String? body;
  final IconData? icon;
  final Color? color;
  final Duration displayDuration;
  final VoidCallback? onTap;
  final VoidCallback? onDismiss;
  final List<NotificationAction>? actions;

  const InAppNotificationBanner({
    super.key,
    required this.title,
    this.body,
    this.icon,
    this.color,
    this.displayDuration = const Duration(seconds: 4),
    this.onTap,
    this.onDismiss,
    this.actions,
  });

  @override
  State<InAppNotificationBanner> createState() => _InAppNotificationBannerState();

  /// Show notification banner overlay
  /// عرض شريط الإشعار المتراكب
  static void show(
    BuildContext context, {
    required String title,
    String? body,
    IconData? icon,
    Color? color,
    Duration displayDuration = const Duration(seconds: 4),
    VoidCallback? onTap,
    VoidCallback? onDismiss,
    List<NotificationAction>? actions,
  }) {
    final overlay = Overlay.of(context);
    late OverlayEntry entry;

    entry = OverlayEntry(
      builder: (context) => _NotificationOverlay(
        title: title,
        body: body,
        icon: icon,
        color: color,
        displayDuration: displayDuration,
        onTap: onTap,
        onDismiss: () {
          entry.remove();
          onDismiss?.call();
        },
        actions: actions,
      ),
    );

    overlay.insert(entry);
  }
}

class _InAppNotificationBannerState extends State<InAppNotificationBanner> {
  @override
  Widget build(BuildContext context) {
    return _NotificationCard(
      title: widget.title,
      body: widget.body,
      icon: widget.icon,
      color: widget.color,
      onTap: widget.onTap,
      actions: widget.actions,
    );
  }
}

class _NotificationOverlay extends StatefulWidget {
  final String title;
  final String? body;
  final IconData? icon;
  final Color? color;
  final Duration displayDuration;
  final VoidCallback? onTap;
  final VoidCallback? onDismiss;
  final List<NotificationAction>? actions;

  const _NotificationOverlay({
    required this.title,
    this.body,
    this.icon,
    this.color,
    required this.displayDuration,
    this.onTap,
    this.onDismiss,
    this.actions,
  });

  @override
  State<_NotificationOverlay> createState() => _NotificationOverlayState();
}

class _NotificationOverlayState extends State<_NotificationOverlay>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;
  Timer? _dismissTimer;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );

    _slideAnimation = Tween<Offset>(
      begin: const Offset(0, -1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));

    _fadeAnimation = Tween<double>(begin: 0, end: 1).animate(_controller);

    _controller.forward();
    HapticFeedback.lightImpact();

    _dismissTimer = Timer(widget.displayDuration, _dismiss);
  }

  void _dismiss() {
    _controller.reverse().then((_) {
      widget.onDismiss?.call();
    });
  }

  @override
  void dispose() {
    _dismissTimer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: MediaQuery.of(context).padding.top + 8,
      left: 16,
      right: 16,
      child: SlideTransition(
        position: _slideAnimation,
        child: FadeTransition(
          opacity: _fadeAnimation,
          child: GestureDetector(
            onTap: () {
              widget.onTap?.call();
              _dismiss();
            },
            onVerticalDragEnd: (details) {
              if (details.velocity.pixelsPerSecond.dy < -100) {
                _dismiss();
              }
            },
            child: _NotificationCard(
              title: widget.title,
              body: widget.body,
              icon: widget.icon,
              color: widget.color,
              onTap: widget.onTap,
              actions: widget.actions,
              showDismissHint: true,
            ),
          ),
        ),
      ),
    );
  }
}

class _NotificationCard extends StatelessWidget {
  final String title;
  final String? body;
  final IconData? icon;
  final Color? color;
  final VoidCallback? onTap;
  final List<NotificationAction>? actions;
  final bool showDismissHint;

  const _NotificationCard({
    required this.title,
    this.body,
    this.icon,
    this.color,
    this.onTap,
    this.actions,
    this.showDismissHint = false,
  });

  @override
  Widget build(BuildContext context) {
    final notificationColor = color ?? SahoolTheme.primary;

    return Material(
      elevation: 8,
      borderRadius: BorderRadius.circular(16),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border(
            left: BorderSide(color: notificationColor, width: 4),
          ),
        ),
        child: Directionality(
          textDirection: TextDirection.rtl,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                if (showDismissHint)
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      margin: const EdgeInsets.only(bottom: 8),
                      decoration: BoxDecoration(
                        color: Colors.grey[300],
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: notificationColor.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(
                        icon ?? Icons.notifications_rounded,
                        color: notificationColor,
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            title,
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                          if (body != null) ...[
                            const SizedBox(height: 4),
                            Text(
                              body!,
                              style: TextStyle(
                                color: Colors.grey[600],
                                fontSize: 12,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
                if (actions != null && actions!.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: actions!.map((action) {
                      return Padding(
                        padding: const EdgeInsets.only(left: 8),
                        child: TextButton(
                          onPressed: action.onPressed,
                          style: TextButton.styleFrom(
                            foregroundColor: action.isPrimary
                                ? notificationColor
                                : Colors.grey[600],
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 6,
                            ),
                          ),
                          child: Text(action.label),
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// =============================================================================
// Notification Badge - شارة الإشعارات
// =============================================================================

/// Animated notification badge
/// شارة إشعارات متحركة
class NotificationBadge extends StatefulWidget {
  final Widget child;
  final int count;
  final Color? color;
  final bool showZero;
  final bool animate;

  const NotificationBadge({
    super.key,
    required this.child,
    required this.count,
    this.color,
    this.showZero = false,
    this.animate = true,
  });

  @override
  State<NotificationBadge> createState() => _NotificationBadgeState();
}

class _NotificationBadgeState extends State<NotificationBadge>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  int _previousCount = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );

    _scaleAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween(begin: 1.0, end: 1.4),
        weight: 50,
      ),
      TweenSequenceItem(
        tween: Tween(begin: 1.4, end: 1.0),
        weight: 50,
      ),
    ]).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.elasticOut,
    ));

    _previousCount = widget.count;
  }

  @override
  void didUpdateWidget(NotificationBadge oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.count != _previousCount && widget.animate) {
      _controller.forward(from: 0);
      if (widget.count > _previousCount) {
        HapticFeedback.lightImpact();
      }
      _previousCount = widget.count;
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.count == 0 && !widget.showZero) {
      return widget.child;
    }

    return Stack(
      clipBehavior: Clip.none,
      children: [
        widget.child,
        Positioned(
          right: -8,
          top: -8,
          child: ScaleTransition(
            scale: _scaleAnimation,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: widget.color ?? SahoolTheme.error,
                borderRadius: BorderRadius.circular(10),
                boxShadow: [
                  BoxShadow(
                    color: (widget.color ?? SahoolTheme.error)
                        .withValues(alpha: 0.4),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              constraints: const BoxConstraints(minWidth: 20),
              child: Text(
                widget.count > 99 ? '99+' : widget.count.toString(),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

// =============================================================================
// Notification List Item - عنصر قائمة الإشعارات
// =============================================================================

/// Notification list item with swipe actions
/// عنصر قائمة الإشعارات مع إجراءات السحب
class NotificationListItem extends StatelessWidget {
  final NotificationData notification;
  final VoidCallback? onTap;
  final VoidCallback? onDismiss;
  final VoidCallback? onMarkAsRead;

  const NotificationListItem({
    super.key,
    required this.notification,
    this.onTap,
    this.onDismiss,
    this.onMarkAsRead,
  });

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Dismissible(
        key: Key(notification.id),
        direction: DismissDirection.horizontal,
        background: _buildSwipeBackground(
          color: SahoolTheme.success,
          icon: Icons.done_all_rounded,
          alignment: Alignment.centerRight,
        ),
        secondaryBackground: _buildSwipeBackground(
          color: SahoolTheme.error,
          icon: Icons.delete_rounded,
          alignment: Alignment.centerLeft,
        ),
        confirmDismiss: (direction) async {
          if (direction == DismissDirection.startToEnd) {
            onMarkAsRead?.call();
            return false;
          } else {
            return true;
          }
        },
        onDismissed: (_) => onDismiss?.call(),
        child: GestureDetector(
          onTap: onTap,
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: notification.isRead ? Colors.white : Colors.blue.shade50,
              border: Border(
                bottom: BorderSide(color: Colors.grey.shade200),
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildIcon(),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              notification.title,
                              style: TextStyle(
                                fontWeight: notification.isRead
                                    ? FontWeight.normal
                                    : FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                          ),
                          Text(
                            _formatTime(notification.timestamp),
                            style: TextStyle(
                              color: Colors.grey[500],
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                      if (notification.body != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          notification.body!,
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 13,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ],
                  ),
                ),
                if (!notification.isRead)
                  Container(
                    width: 8,
                    height: 8,
                    margin: const EdgeInsets.only(right: 8, top: 6),
                    decoration: const BoxDecoration(
                      color: SahoolTheme.primary,
                      shape: BoxShape.circle,
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildIcon() {
    final color = _getTypeColor();
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Icon(
        notification.icon ?? _getTypeIcon(),
        color: color,
        size: 20,
      ),
    );
  }

  Widget _buildSwipeBackground({
    required Color color,
    required IconData icon,
    required Alignment alignment,
  }) {
    return Container(
      color: color,
      alignment: alignment,
      padding: const EdgeInsets.symmetric(horizontal: 20),
      child: Icon(icon, color: Colors.white),
    );
  }

  Color _getTypeColor() {
    switch (notification.type) {
      case NotificationType.alert:
        return SahoolTheme.error;
      case NotificationType.warning:
        return SahoolTheme.warning;
      case NotificationType.success:
        return SahoolTheme.success;
      case NotificationType.info:
        return SahoolTheme.info;
      case NotificationType.task:
        return Colors.purple;
      case NotificationType.message:
        return SahoolTheme.primary;
    }
  }

  IconData _getTypeIcon() {
    switch (notification.type) {
      case NotificationType.alert:
        return Icons.warning_amber_rounded;
      case NotificationType.warning:
        return Icons.error_outline_rounded;
      case NotificationType.success:
        return Icons.check_circle_outline_rounded;
      case NotificationType.info:
        return Icons.info_outline_rounded;
      case NotificationType.task:
        return Icons.task_alt_rounded;
      case NotificationType.message:
        return Icons.chat_bubble_outline_rounded;
    }
  }

  String _formatTime(DateTime timestamp) {
    final now = DateTime.now();
    final diff = now.difference(timestamp);

    if (diff.inMinutes < 1) return 'الآن';
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} د';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} س';
    if (diff.inDays < 7) return 'منذ ${diff.inDays} يوم';
    return '${timestamp.day}/${timestamp.month}';
  }
}

// =============================================================================
// Grouped Notifications - إشعارات مجمعة
// =============================================================================

/// Widget that groups notifications by date
/// مكون يجمع الإشعارات حسب التاريخ
class GroupedNotificationList extends StatelessWidget {
  final List<NotificationData> notifications;
  final void Function(NotificationData)? onTap;
  final void Function(NotificationData)? onDismiss;
  final void Function(NotificationData)? onMarkAsRead;

  const GroupedNotificationList({
    super.key,
    required this.notifications,
    this.onTap,
    this.onDismiss,
    this.onMarkAsRead,
  });

  @override
  Widget build(BuildContext context) {
    final grouped = _groupByDate(notifications);

    return ListView.builder(
      itemCount: grouped.length,
      itemBuilder: (context, index) {
        final group = grouped[index];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                group.label,
                style: TextStyle(
                  color: Colors.grey[600],
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                ),
              ),
            ),
            ...group.notifications.map((notification) {
              return AnimatedListItem(
                index: group.notifications.indexOf(notification),
                child: NotificationListItem(
                  notification: notification,
                  onTap: () => onTap?.call(notification),
                  onDismiss: () => onDismiss?.call(notification),
                  onMarkAsRead: () => onMarkAsRead?.call(notification),
                ),
              );
            }),
          ],
        );
      },
    );
  }

  List<_NotificationGroup> _groupByDate(List<NotificationData> notifications) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final lastWeek = today.subtract(const Duration(days: 7));

    final todayList = <NotificationData>[];
    final yesterdayList = <NotificationData>[];
    final lastWeekList = <NotificationData>[];
    final olderList = <NotificationData>[];

    for (final notification in notifications) {
      final date = DateTime(
        notification.timestamp.year,
        notification.timestamp.month,
        notification.timestamp.day,
      );

      if (date == today) {
        todayList.add(notification);
      } else if (date == yesterday) {
        yesterdayList.add(notification);
      } else if (date.isAfter(lastWeek)) {
        lastWeekList.add(notification);
      } else {
        olderList.add(notification);
      }
    }

    return [
      if (todayList.isNotEmpty) _NotificationGroup('اليوم', todayList),
      if (yesterdayList.isNotEmpty) _NotificationGroup('أمس', yesterdayList),
      if (lastWeekList.isNotEmpty)
        _NotificationGroup('هذا الأسبوع', lastWeekList),
      if (olderList.isNotEmpty) _NotificationGroup('قديم', olderList),
    ];
  }
}

class _NotificationGroup {
  final String label;
  final List<NotificationData> notifications;

  _NotificationGroup(this.label, this.notifications);
}

// =============================================================================
// Data Classes - فئات البيانات
// =============================================================================

/// Notification action button
/// زر إجراء الإشعار
class NotificationAction {
  final String label;
  final VoidCallback onPressed;
  final bool isPrimary;

  const NotificationAction({
    required this.label,
    required this.onPressed,
    this.isPrimary = false,
  });
}

/// Notification data model
/// نموذج بيانات الإشعار
class NotificationData {
  final String id;
  final String title;
  final String? body;
  final NotificationType type;
  final DateTime timestamp;
  final bool isRead;
  final IconData? icon;
  final Map<String, dynamic>? data;

  const NotificationData({
    required this.id,
    required this.title,
    this.body,
    this.type = NotificationType.info,
    required this.timestamp,
    this.isRead = false,
    this.icon,
    this.data,
  });

  NotificationData copyWith({
    String? id,
    String? title,
    String? body,
    NotificationType? type,
    DateTime? timestamp,
    bool? isRead,
    IconData? icon,
    Map<String, dynamic>? data,
  }) {
    return NotificationData(
      id: id ?? this.id,
      title: title ?? this.title,
      body: body ?? this.body,
      type: type ?? this.type,
      timestamp: timestamp ?? this.timestamp,
      isRead: isRead ?? this.isRead,
      icon: icon ?? this.icon,
      data: data ?? this.data,
    );
  }
}

/// Notification type
/// نوع الإشعار
enum NotificationType {
  alert,
  warning,
  success,
  info,
  task,
  message,
}
