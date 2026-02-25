import 'package:flutter/material.dart';

/// Reusable Empty State Widget
/// Displays when lists or data are empty
///
/// واجهة الحالة الفارغة - تُعرض عندما لا توجد بيانات
class EmptyStateWidget extends StatelessWidget {
  final String title;
  final String? titleAr;
  final String message;
  final String? messageAr;
  final IconData icon;
  final String? actionLabel;
  final String? actionLabelAr;
  final VoidCallback? onAction;
  final bool showIcon;
  final Color? iconColor;
  final double iconSize;

  const EmptyStateWidget({
    super.key,
    required this.title,
    this.titleAr,
    required this.message,
    this.messageAr,
    this.icon = Icons.inbox_outlined,
    this.actionLabel,
    this.actionLabelAr,
    this.onAction,
    this.showIcon = true,
    this.iconColor,
    this.iconSize = 80.0,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isRtl = Directionality.of(context) == TextDirection.rtl;

    // Use Arabic text if RTL and Arabic text provided
    final displayTitle = isRtl && titleAr != null ? titleAr! : title;
    final displayMessage = isRtl && messageAr != null ? messageAr! : message;
    final displayActionLabel =
        isRtl && actionLabelAr != null ? actionLabelAr : actionLabel;

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Icon
            if (showIcon) ...[
              Icon(
                icon,
                size: iconSize,
                color: iconColor ?? theme.colorScheme.outline.withOpacity(0.5),
              ),
              const SizedBox(height: 24),
            ],

            // Title
            Text(
              displayTitle,
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.onSurface,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),

            // Message
            Text(
              displayMessage,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),

            // Action button
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: onAction,
                icon: const Icon(Icons.add),
                label: Text(displayActionLabel ?? actionLabel!),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 12,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Specialized Empty State Widgets for common use cases
class EmptyFieldsState extends StatelessWidget {
  final VoidCallback? onAddField;

  const EmptyFieldsState({
    super.key,
    this.onAddField,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      title: 'No Fields Yet',
      titleAr: 'لا توجد حقول بعد',
      message: 'Start by adding your first field to begin managing your farm.',
      messageAr: 'ابدأ بإضافة حقلك الأول لبدء إدارة مزرعتك.',
      icon: Icons.agriculture_outlined,
      actionLabel: 'Add Field',
      actionLabelAr: 'إضافة حقل',
      onAction: onAddField,
      iconColor: Colors.green,
    );
  }
}

class EmptyTasksState extends StatelessWidget {
  final VoidCallback? onAddTask;

  const EmptyTasksState({
    super.key,
    this.onAddTask,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      title: 'No Tasks',
      titleAr: 'لا توجد مهام',
      message: 'You have no pending tasks. Create a new task to get started.',
      messageAr: 'ليس لديك مهام معلقة. أنشئ مهمة جديدة للبدء.',
      icon: Icons.task_alt_outlined,
      actionLabel: 'Add Task',
      actionLabelAr: 'إضافة مهمة',
      onAction: onAddTask,
      iconColor: Colors.blue,
    );
  }
}

class EmptyNotificationsState extends StatelessWidget {
  const EmptyNotificationsState({super.key});

  @override
  Widget build(BuildContext context) {
    return const EmptyStateWidget(
      title: 'No Notifications',
      titleAr: 'لا توجد إشعارات',
      message: 'You\'re all caught up! No new notifications.',
      messageAr: 'أنت على اطلاع! لا توجد إشعارات جديدة.',
      icon: Icons.notifications_none_outlined,
      showIcon: true,
    );
  }
}

class EmptySearchResultsState extends StatelessWidget {
  final String? searchQuery;

  const EmptySearchResultsState({
    super.key,
    this.searchQuery,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      title: 'No Results Found',
      titleAr: 'لم يتم العثور على نتائج',
      message: searchQuery != null
          ? 'No results found for "$searchQuery". Try a different search term.'
          : 'Try adjusting your search criteria.',
      messageAr: searchQuery != null
          ? 'لم يتم العثور على نتائج لـ "$searchQuery". جرب مصطلح بحث مختلف.'
          : 'حاول تعديل معايير البحث الخاصة بك.',
      icon: Icons.search_off_outlined,
    );
  }
}

class EmptyEquipmentState extends StatelessWidget {
  final VoidCallback? onAddEquipment;

  const EmptyEquipmentState({
    super.key,
    this.onAddEquipment,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      title: 'No Equipment',
      titleAr: 'لا توجد معدات',
      message: 'Add equipment to track maintenance and usage.',
      messageAr: 'أضف المعدات لتتبع الصيانة والاستخدام.',
      icon: Icons.precision_manufacturing_outlined,
      actionLabel: 'Add Equipment',
      actionLabelAr: 'إضافة معدات',
      onAction: onAddEquipment,
      iconColor: Colors.orange,
    );
  }
}

class EmptyAlertsState extends StatelessWidget {
  const EmptyAlertsState({super.key});

  @override
  Widget build(BuildContext context) {
    return const EmptyStateWidget(
      title: 'No Active Alerts',
      titleAr: 'لا توجد تنبيهات نشطة',
      message: 'Great! Your fields are healthy with no active alerts.',
      messageAr: 'رائع! حقولك بصحة جيدة ولا توجد تنبيهات نشطة.',
      icon: Icons.check_circle_outline,
      iconColor: Colors.green,
    );
  }
}
