/// SAHOOL Grouped Notification List Widget
/// عنصر قائمة الإشعارات المجمعة
///
/// Displays notifications grouped by:
/// - Date (Today, Yesterday, This Week, etc.)
/// - Category
/// - Custom grouping
library;

import 'package:flutter/material.dart';

import '../../domain/models/notification.dart';
import '../../domain/models/notification_category.dart';
import 'notification_card.dart';
import 'notification_badge.dart';

/// Grouping type
enum GroupingType {
  date,
  category,
  priority,
  custom,
}

/// Group header data
class NotificationGroupHeader {
  final String key;
  final String title;
  final String? subtitle;
  final IconData? icon;
  final Color? color;
  final int totalCount;
  final int unreadCount;

  const NotificationGroupHeader({
    required this.key,
    required this.title,
    this.subtitle,
    this.icon,
    this.color,
    required this.totalCount,
    required this.unreadCount,
  });
}

/// Grouped notification list widget
class GroupedNotificationList extends StatelessWidget {
  final List<AppNotification> notifications;
  final GroupingType groupingType;
  final Function(AppNotification) onTap;
  final Function(AppNotification)? onDismiss;
  final Function(AppNotification)? onMarkRead;
  final Function(AppNotification)? onLongPress;
  final bool isSelectionMode;
  final Set<String> selectedIds;
  final ScrollController? scrollController;
  final Widget? emptyWidget;
  final bool collapsible;
  final Set<String> expandedGroups;
  final Function(String)? onGroupToggle;

  const GroupedNotificationList({
    super.key,
    required this.notifications,
    this.groupingType = GroupingType.date,
    required this.onTap,
    this.onDismiss,
    this.onMarkRead,
    this.onLongPress,
    this.isSelectionMode = false,
    this.selectedIds = const {},
    this.scrollController,
    this.emptyWidget,
    this.collapsible = false,
    this.expandedGroups = const {},
    this.onGroupToggle,
  });

  @override
  Widget build(BuildContext context) {
    if (notifications.isEmpty) {
      return emptyWidget ?? _buildDefaultEmpty(context);
    }

    final groups = _groupNotifications();

    return ListView.builder(
      controller: scrollController,
      itemCount: _calculateItemCount(groups),
      itemBuilder: (context, index) {
        return _buildItem(context, index, groups);
      },
    );
  }

  Map<String, List<AppNotification>> _groupNotifications() {
    switch (groupingType) {
      case GroupingType.date:
        return _groupByDate();
      case GroupingType.category:
        return _groupByCategory();
      case GroupingType.priority:
        return _groupByPriority();
      case GroupingType.custom:
        return _groupByCustom();
    }
  }

  Map<String, List<AppNotification>> _groupByDate() {
    final groups = <String, List<AppNotification>>{};
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final thisWeek = today.subtract(Duration(days: today.weekday - 1));
    final thisMonth = DateTime(now.year, now.month, 1);

    for (final notification in notifications) {
      final date = DateTime(
        notification.createdAt.year,
        notification.createdAt.month,
        notification.createdAt.day,
      );

      String key;
      if (date == today) {
        key = 'today';
      } else if (date == yesterday) {
        key = 'yesterday';
      } else if (date.isAfter(thisWeek)) {
        key = 'this_week';
      } else if (date.isAfter(thisMonth)) {
        key = 'this_month';
      } else {
        key = 'older';
      }

      groups.putIfAbsent(key, () => []).add(notification);
    }

    return groups;
  }

  Map<String, List<AppNotification>> _groupByCategory() {
    final groups = <String, List<AppNotification>>{};

    for (final notification in notifications) {
      final key = notification.category.name;
      groups.putIfAbsent(key, () => []).add(notification);
    }

    return groups;
  }

  Map<String, List<AppNotification>> _groupByPriority() {
    final groups = <String, List<AppNotification>>{};

    for (final notification in notifications) {
      final key = notification.priority.name;
      groups.putIfAbsent(key, () => []).add(notification);
    }

    return groups;
  }

  Map<String, List<AppNotification>> _groupByCustom() {
    final groups = <String, List<AppNotification>>{};

    for (final notification in notifications) {
      final key = notification.groupId ?? 'ungrouped';
      groups.putIfAbsent(key, () => []).add(notification);
    }

    return groups;
  }

  int _calculateItemCount(Map<String, List<AppNotification>> groups) {
    int count = 0;
    for (final entry in groups.entries) {
      count++; // Header
      if (!collapsible || expandedGroups.contains(entry.key)) {
        count += entry.value.length;
      }
    }
    return count;
  }

  Widget _buildItem(
    BuildContext context,
    int index,
    Map<String, List<AppNotification>> groups,
  ) {
    int currentIndex = 0;

    for (final entry in groups.entries) {
      // Header
      if (currentIndex == index) {
        return _buildGroupHeader(context, entry.key, entry.value);
      }
      currentIndex++;

      // Items (if expanded)
      if (!collapsible || expandedGroups.contains(entry.key)) {
        for (final notification in entry.value) {
          if (currentIndex == index) {
            return _buildNotificationItem(notification);
          }
          currentIndex++;
        }
      }
    }

    return const SizedBox.shrink();
  }

  Widget _buildGroupHeader(
    BuildContext context,
    String key,
    List<AppNotification> items,
  ) {
    final header = _getHeaderData(key, items);
    final isExpanded = !collapsible || expandedGroups.contains(key);

    return Material(
      color: header.color?.withValues(alpha: 0.1) ?? Colors.grey.shade100,
      child: InkWell(
        onTap: collapsible ? () => onGroupToggle?.call(key) : null,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            border: Border(
              bottom: BorderSide(
                color: header.color?.withValues(alpha: 0.3) ?? Colors.grey.shade300,
                width: 1,
              ),
            ),
          ),
          child: Row(
            children: [
              // Icon
              if (header.icon != null)
                Padding(
                  padding: const EdgeInsets.only(left: 12),
                  child: Icon(
                    header.icon,
                    size: 20,
                    color: header.color ?? Colors.grey.shade700,
                  ),
                ),

              // Title and subtitle
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      header.title,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: header.color ?? Colors.grey.shade800,
                      ),
                    ),
                    if (header.subtitle != null)
                      Text(
                        header.subtitle!,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                        ),
                      ),
                  ],
                ),
              ),

              // Count badge
              if (header.unreadCount > 0)
                NotificationBadge(
                  count: header.unreadCount,
                  small: true,
                  color: header.color,
                ),

              // Total count
              Padding(
                padding: const EdgeInsets.only(right: 8, left: 8),
                child: Text(
                  '${header.totalCount}',
                  style: TextStyle(
                    fontSize: 13,
                    color: Colors.grey.shade600,
                  ),
                ),
              ),

              // Expand/collapse icon
              if (collapsible)
                Icon(
                  isExpanded
                      ? Icons.keyboard_arrow_up
                      : Icons.keyboard_arrow_down,
                  color: Colors.grey.shade600,
                ),
            ],
          ),
        ),
      ),
    );
  }

  NotificationGroupHeader _getHeaderData(
    String key,
    List<AppNotification> items,
  ) {
    final unreadCount = items.where((n) => n.isUnread).length;

    switch (groupingType) {
      case GroupingType.date:
        return NotificationGroupHeader(
          key: key,
          title: _getDateTitle(key),
          totalCount: items.length,
          unreadCount: unreadCount,
          icon: Icons.calendar_today,
        );

      case GroupingType.category:
        final category = NotificationCategoryExtension.fromString(key);
        if (category != null) {
          return NotificationGroupHeader(
            key: key,
            title: category.labelAr,
            subtitle: category.descriptionAr,
            icon: category.icon,
            color: category.color,
            totalCount: items.length,
            unreadCount: unreadCount,
          );
        }
        break;

      case GroupingType.priority:
        final priority = _getPriorityFromName(key);
        return NotificationGroupHeader(
          key: key,
          title: priority.labelAr,
          icon: Icons.flag,
          color: priority.color,
          totalCount: items.length,
          unreadCount: unreadCount,
        );

      case GroupingType.custom:
        return NotificationGroupHeader(
          key: key,
          title: items.first.groupTitle ?? key,
          totalCount: items.length,
          unreadCount: unreadCount,
        );
    }

    return NotificationGroupHeader(
      key: key,
      title: key,
      totalCount: items.length,
      unreadCount: unreadCount,
    );
  }

  String _getDateTitle(String key) {
    switch (key) {
      case 'today':
        return 'اليوم';
      case 'yesterday':
        return 'أمس';
      case 'this_week':
        return 'هذا الأسبوع';
      case 'this_month':
        return 'هذا الشهر';
      case 'older':
        return 'أقدم';
      default:
        return key;
    }
  }

  NotificationPriority _getPriorityFromName(String name) {
    switch (name.toLowerCase()) {
      case 'low':
        return NotificationPriority.low;
      case 'normal':
        return NotificationPriority.normal;
      case 'high':
        return NotificationPriority.high;
      case 'critical':
        return NotificationPriority.critical;
      default:
        return NotificationPriority.normal;
    }
  }

  Widget _buildNotificationItem(AppNotification notification) {
    return NotificationCard(
      notification: notification,
      isSelected: selectedIds.contains(notification.id),
      showCheckbox: isSelectionMode,
      onTap: () => onTap(notification),
      onLongPress: onLongPress != null ? () => onLongPress!(notification) : null,
      onDismiss: onDismiss != null ? () => onDismiss!(notification) : null,
      onMarkRead: onMarkRead != null ? () => onMarkRead!(notification) : null,
    );
  }

  Widget _buildDefaultEmpty(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.notifications_off_outlined,
            size: 64,
            color: Colors.grey.shade300,
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد إشعارات',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade600,
            ),
          ),
        ],
      ),
    );
  }
}

/// Sticky header grouped list
class StickyGroupedNotificationList extends StatelessWidget {
  final List<AppNotification> notifications;
  final GroupingType groupingType;
  final Function(AppNotification) onTap;
  final Function(AppNotification)? onDismiss;
  final Function(AppNotification)? onMarkRead;

  const StickyGroupedNotificationList({
    super.key,
    required this.notifications,
    this.groupingType = GroupingType.date,
    required this.onTap,
    this.onDismiss,
    this.onMarkRead,
  });

  @override
  Widget build(BuildContext context) {
    // This would use a package like sticky_headers or grouped_list
    // For simplicity, using regular GroupedNotificationList
    return GroupedNotificationList(
      notifications: notifications,
      groupingType: groupingType,
      onTap: onTap,
      onDismiss: onDismiss,
      onMarkRead: onMarkRead,
    );
  }
}
