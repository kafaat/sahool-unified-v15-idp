/// SAHOOL Notifications Center Screen
/// شاشة مركز الإشعارات
///
/// Main inbox-style notifications screen with:
/// - Category filtering
/// - Group by date/category
/// - Bulk actions
/// - Pull to refresh

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../domain/models/notification.dart';
import '../../domain/models/notification_category.dart';
import '../../state/notifications_providers.dart';
import '../widgets/notification_card.dart';
import '../widgets/notification_filter.dart';
import '../widgets/notification_badge.dart';
import 'notification_settings_screen.dart';
import 'notification_details_screen.dart';

/// Grouping mode for notifications
enum NotificationGrouping {
  none,
  date,
  category,
}

class NotificationsCenterScreen extends ConsumerStatefulWidget {
  const NotificationsCenterScreen({super.key});

  @override
  ConsumerState<NotificationsCenterScreen> createState() =>
      _NotificationsCenterScreenState();
}

class _NotificationsCenterScreenState
    extends ConsumerState<NotificationsCenterScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  NotificationCategory? _selectedCategory;
  NotificationGrouping _grouping = NotificationGrouping.date;
  bool _isSelectionMode = false;
  final Set<String> _selectedIds = {};

  @override
  void initState() {
    super.initState();
    _tabController = TabController(
      length: NotificationCategory.values.length + 1,
      vsync: this,
    );
    _tabController.addListener(_onTabChanged);

    // Load notifications on init
    Future.microtask(() {
      ref.read(notificationsControllerProvider.notifier).loadNotifications();
    });
  }

  @override
  void dispose() {
    _tabController.removeListener(_onTabChanged);
    _tabController.dispose();
    super.dispose();
  }

  void _onTabChanged() {
    if (_tabController.indexIsChanging) return;

    setState(() {
      final categoryIndex = _tabController.index - 1;
      if (_tabController.index <= 0 || categoryIndex >= NotificationCategory.values.length) {
        _selectedCategory = null;
      } else {
        _selectedCategory = NotificationCategory.values[categoryIndex];
      }
      _selectedIds.clear();
      _isSelectionMode = false;
    });

    ref.read(notificationsControllerProvider.notifier).loadNotifications(
          category: _selectedCategory,
        );
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(notificationsControllerProvider);
    final unreadCounts = ref.watch(unreadCountByCategoryProvider);

    return Scaffold(
      appBar: _buildAppBar(context, state, unreadCounts),
      body: Column(
        children: [
          // Category tabs
          _buildCategoryTabs(unreadCounts),

          // Notifications list
          Expanded(
            child: RefreshIndicator(
              onRefresh: () async {
                await ref
                    .read(notificationsControllerProvider.notifier)
                    .refreshNotifications(category: _selectedCategory);
              },
              child: _buildBody(context, state),
            ),
          ),
        ],
      ),
      floatingActionButton: _isSelectionMode && _selectedIds.isNotEmpty
          ? _buildBulkActionsButton()
          : null,
    );
  }

  PreferredSizeWidget _buildAppBar(
    BuildContext context,
    NotificationsState state,
    Map<NotificationCategory, int> unreadCounts,
  ) {
    final totalUnread = unreadCounts.values.fold(0, (a, b) => a + b);

    if (_isSelectionMode) {
      return AppBar(
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () {
            setState(() {
              _isSelectionMode = false;
              _selectedIds.clear();
            });
          },
        ),
        title: Text('${_selectedIds.length} محدد'),
        actions: [
          TextButton(
            onPressed: () {
              setState(() {
                if (_selectedIds.length == state.notifications.length) {
                  _selectedIds.clear();
                } else {
                  _selectedIds.addAll(state.notifications.map((n) => n.id));
                }
              });
            },
            child: Text(
              _selectedIds.length == state.notifications.length
                  ? 'إلغاء الكل'
                  : 'تحديد الكل',
            ),
          ),
        ],
      );
    }

    return AppBar(
      title: Row(
        children: [
          const Text('الإشعارات'),
          if (totalUnread > 0) ...[
            const SizedBox(width: 8),
            NotificationBadge(count: totalUnread),
          ],
        ],
      ),
      actions: [
        // Group toggle
        PopupMenuButton<NotificationGrouping>(
          icon: const Icon(Icons.sort),
          tooltip: 'تجميع',
          onSelected: (grouping) {
            setState(() {
              _grouping = grouping;
            });
          },
          itemBuilder: (context) => [
            PopupMenuItem(
              value: NotificationGrouping.none,
              child: Row(
                children: [
                  Icon(
                    Icons.check,
                    color: _grouping == NotificationGrouping.none
                        ? Theme.of(context).primaryColor
                        : Colors.transparent,
                  ),
                  const SizedBox(width: 8),
                  const Text('بدون تجميع'),
                ],
              ),
            ),
            PopupMenuItem(
              value: NotificationGrouping.date,
              child: Row(
                children: [
                  Icon(
                    Icons.check,
                    color: _grouping == NotificationGrouping.date
                        ? Theme.of(context).primaryColor
                        : Colors.transparent,
                  ),
                  const SizedBox(width: 8),
                  const Text('تجميع بالتاريخ'),
                ],
              ),
            ),
            PopupMenuItem(
              value: NotificationGrouping.category,
              child: Row(
                children: [
                  Icon(
                    Icons.check,
                    color: _grouping == NotificationGrouping.category
                        ? Theme.of(context).primaryColor
                        : Colors.transparent,
                  ),
                  const SizedBox(width: 8),
                  const Text('تجميع بالفئة'),
                ],
              ),
            ),
          ],
        ),

        // Mark all read
        if (totalUnread > 0)
          IconButton(
            icon: const Icon(Icons.done_all),
            tooltip: 'تعليم الكل كمقروء',
            onPressed: () => _showMarkAllReadDialog(context),
          ),

        // Settings
        IconButton(
          icon: const Icon(Icons.settings),
          tooltip: 'الإعدادات',
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => const NotificationSettingsScreen(),
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildCategoryTabs(Map<NotificationCategory, int> unreadCounts) {
    final totalUnread = unreadCounts.values.fold(0, (a, b) => a + b);

    return Container(
      color: Theme.of(context).appBarTheme.backgroundColor,
      child: TabBar(
        controller: _tabController,
        isScrollable: true,
        tabAlignment: TabAlignment.start,
        tabs: [
          // All tab
          Tab(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('الكل'),
                if (totalUnread > 0) ...[
                  const SizedBox(width: 4),
                  NotificationBadge(count: totalUnread, small: true),
                ],
              ],
            ),
          ),
          // Category tabs
          ...NotificationCategory.values.map((category) {
            final count = unreadCounts[category] ?? 0;
            return Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(category.icon, size: 18),
                  const SizedBox(width: 4),
                  Text(category.labelAr),
                  if (count > 0) ...[
                    const SizedBox(width: 4),
                    NotificationBadge(
                      count: count,
                      small: true,
                      color: category.color,
                    ),
                  ],
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildBody(BuildContext context, NotificationsState state) {
    if (state.isLoading && state.notifications.isEmpty) {
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    if (state.error != null && state.notifications.isEmpty) {
      return _buildErrorState(state.error!);
    }

    if (state.notifications.isEmpty) {
      return _buildEmptyState();
    }

    // Group notifications if needed
    switch (_grouping) {
      case NotificationGrouping.none:
        return _buildFlatList(state.notifications);
      case NotificationGrouping.date:
        return _buildDateGroupedList(state.notifications);
      case NotificationGrouping.category:
        return _buildCategoryGroupedList(state.notifications);
    }
  }

  Widget _buildFlatList(List<AppNotification> notifications) {
    return ListView.builder(
      itemCount: notifications.length,
      itemBuilder: (context, index) {
        return _buildNotificationItem(notifications[index]);
      },
    );
  }

  Widget _buildDateGroupedList(List<AppNotification> notifications) {
    final groups = _groupByDate(notifications);

    return ListView.builder(
      itemCount: groups.length,
      itemBuilder: (context, index) {
        final group = groups[index];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildGroupHeader(group.titleAr, group.unreadCount),
            ...group.notifications.map(_buildNotificationItem),
          ],
        );
      },
    );
  }

  Widget _buildCategoryGroupedList(List<AppNotification> notifications) {
    final groups = _groupByCategory(notifications);

    return ListView.builder(
      itemCount: groups.length,
      itemBuilder: (context, index) {
        final group = groups[index];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildCategoryGroupHeader(group.category, group.unreadCount),
            ...group.notifications.map(_buildNotificationItem),
          ],
        );
      },
    );
  }

  Widget _buildGroupHeader(String title, int unreadCount) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.grey.shade100,
      child: Row(
        children: [
          Text(
            title,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade700,
            ),
          ),
          if (unreadCount > 0) ...[
            const SizedBox(width: 8),
            NotificationBadge(count: unreadCount, small: true),
          ],
        ],
      ),
    );
  }

  Widget _buildCategoryGroupHeader(
    NotificationCategory category,
    int unreadCount,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: category.lightColor,
      child: Row(
        children: [
          Icon(category.icon, size: 18, color: category.color),
          const SizedBox(width: 8),
          Text(
            category.labelAr,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: category.color,
            ),
          ),
          if (unreadCount > 0) ...[
            const SizedBox(width: 8),
            NotificationBadge(
              count: unreadCount,
              small: true,
              color: category.color,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildNotificationItem(AppNotification notification) {
    final isSelected = _selectedIds.contains(notification.id);

    return NotificationCard(
      notification: notification,
      isSelected: isSelected,
      showCheckbox: _isSelectionMode,
      onTap: () {
        if (_isSelectionMode) {
          setState(() {
            if (isSelected) {
              _selectedIds.remove(notification.id);
              if (_selectedIds.isEmpty) {
                _isSelectionMode = false;
              }
            } else {
              _selectedIds.add(notification.id);
            }
          });
        } else {
          _openNotificationDetails(notification);
        }
      },
      onLongPress: () {
        setState(() {
          _isSelectionMode = true;
          _selectedIds.add(notification.id);
        });
      },
      onDismiss: () => _dismissNotification(notification),
      onMarkRead: () => _markAsRead(notification),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            _selectedCategory?.icon ?? Icons.notifications_none,
            size: 80,
            color: Colors.grey.shade300,
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد إشعارات',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _selectedCategory != null
                ? 'لا توجد إشعارات في ${_selectedCategory!.labelAr}'
                : 'صندوق الإشعارات فارغ',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            error,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: () {
              ref
                  .read(notificationsControllerProvider.notifier)
                  .loadNotifications(category: _selectedCategory);
            },
            icon: const Icon(Icons.refresh),
            label: const Text('إعادة المحاولة'),
          ),
        ],
      ),
    );
  }

  Widget _buildBulkActionsButton() {
    return FloatingActionButton.extended(
      onPressed: _showBulkActionsSheet,
      icon: const Icon(Icons.checklist),
      label: Text('${_selectedIds.length} إجراءات'),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Actions
  // ─────────────────────────────────────────────────────────────────────────────

  void _openNotificationDetails(AppNotification notification) {
    // Mark as read when opened
    if (notification.isUnread) {
      ref
          .read(notificationsControllerProvider.notifier)
          .markAsRead(notification.id);
    }

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            NotificationDetailsScreen(notification: notification),
      ),
    );
  }

  void _dismissNotification(AppNotification notification) {
    // Store the notification and its index before deleting for undo support
    final deletedNotification = notification;
    final controller = ref.read(notificationsControllerProvider.notifier);
    final currentState = ref.read(notificationsControllerProvider);
    final originalIndex = currentState.notifications.indexWhere(
      (n) => n.id == notification.id,
    );

    controller.deleteNotification(notification.id);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('تم حذف الإشعار'),
        action: SnackBarAction(
          label: 'تراجع',
          onPressed: () {
            // Undo: restore the notification via the controller's public API,
            // then refresh from the server to ensure backend consistency.
            controller.restoreNotification(deletedNotification, originalIndex);
            controller.refreshNotifications(
              category: currentState.selectedCategory,
            );
          },
        ),
      ),
    );
  }

  void _markAsRead(AppNotification notification) {
    if (notification.isUnread) {
      ref
          .read(notificationsControllerProvider.notifier)
          .markAsRead(notification.id);
    } else {
      ref
          .read(notificationsControllerProvider.notifier)
          .markAsUnread(notification.id);
    }
  }

  void _showMarkAllReadDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تعليم الكل كمقروء'),
        content: Text(
          _selectedCategory != null
              ? 'هل تريد تعليم جميع إشعارات ${_selectedCategory!.labelAr} كمقروءة؟'
              : 'هل تريد تعليم جميع الإشعارات كمقروءة؟',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ref
                  .read(notificationsControllerProvider.notifier)
                  .markAllAsRead(category: _selectedCategory);
            },
            child: const Text('تأكيد'),
          ),
        ],
      ),
    );
  }

  void _showBulkActionsSheet() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.done_all),
              title: const Text('تعليم كمقروء'),
              onTap: () {
                Navigator.pop(context);
                for (final id in _selectedIds) {
                  ref
                      .read(notificationsControllerProvider.notifier)
                      .markAsRead(id);
                }
                setState(() {
                  _selectedIds.clear();
                  _isSelectionMode = false;
                });
              },
            ),
            ListTile(
              leading: const Icon(Icons.archive),
              title: const Text('أرشفة'),
              onTap: () {
                Navigator.pop(context);
                for (final id in _selectedIds) {
                  ref
                      .read(notificationsControllerProvider.notifier)
                      .archiveNotification(id);
                }
                setState(() {
                  _selectedIds.clear();
                  _isSelectionMode = false;
                });
              },
            ),
            ListTile(
              leading: const Icon(Icons.delete, color: Colors.red),
              title: const Text('حذف', style: TextStyle(color: Colors.red)),
              onTap: () {
                Navigator.pop(context);
                ref
                    .read(notificationsControllerProvider.notifier)
                    .deleteNotifications(_selectedIds.toList());
                setState(() {
                  _selectedIds.clear();
                  _isSelectionMode = false;
                });
              },
            ),
          ],
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Grouping Helpers
  // ─────────────────────────────────────────────────────────────────────────────

  List<NotificationGroup> _groupByDate(List<AppNotification> notifications) {
    final groups = <DateTime, List<AppNotification>>{};
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final thisWeek = today.subtract(Duration(days: today.weekday - 1));

    for (final notification in notifications) {
      final date = DateTime(
        notification.createdAt.year,
        notification.createdAt.month,
        notification.createdAt.day,
      );
      groups.putIfAbsent(date, () => []).add(notification);
    }

    return groups.entries.map((entry) {
      String title;
      String titleAr;

      if (entry.key == today) {
        title = 'Today';
        titleAr = 'اليوم';
      } else if (entry.key == yesterday) {
        title = 'Yesterday';
        titleAr = 'أمس';
      } else if (entry.key.isAfter(thisWeek)) {
        title = DateFormat('EEEE').format(entry.key);
        titleAr = DateFormat('EEEE', 'ar').format(entry.key);
      } else {
        title = DateFormat('MMM d, y').format(entry.key);
        titleAr = DateFormat('d MMM y', 'ar').format(entry.key);
      }

      return NotificationGroup(
        date: entry.key,
        title: title,
        titleAr: titleAr,
        notifications: entry.value,
      );
    }).toList()
      ..sort((a, b) => b.date.compareTo(a.date));
  }

  List<CategoryNotificationGroup> _groupByCategory(
    List<AppNotification> notifications,
  ) {
    final groups = <NotificationCategory, List<AppNotification>>{};

    for (final notification in notifications) {
      groups.putIfAbsent(notification.category, () => []).add(notification);
    }

    return groups.entries
        .map((entry) => CategoryNotificationGroup(
              category: entry.key,
              notifications: entry.value,
            ))
        .toList()
      ..sort((a, b) =>
          b.category.defaultPriority.compareTo(a.category.defaultPriority));
  }
}
