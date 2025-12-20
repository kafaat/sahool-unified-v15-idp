import 'package:flutter/material.dart';
import '../theme/sahool_theme.dart';

/// SAHOOL Empty States Widgets
/// مكونات حالات البيانات الفارغة

/// Base empty state widget
class SahoolEmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? message;
  final String? actionLabel;
  final VoidCallback? onAction;
  final Widget? customAction;

  const SahoolEmptyState({
    super.key,
    required this.icon,
    required this.title,
    this.message,
    this.actionLabel,
    this.onAction,
    this.customAction,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Icon
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: SahoolColors.sageGreen.withOpacity(0.15),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                size: 64,
                color: SahoolColors.sageGreen,
              ),
            ),

            const SizedBox(height: 24),

            // Title
            Text(
              title,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: SahoolColors.textDark,
                  ),
              textAlign: TextAlign.center,
            ),

            // Message
            if (message != null) ...[
              const SizedBox(height: 12),
              Text(
                message!,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: SahoolColors.textSecondary,
                    ),
                textAlign: TextAlign.center,
              ),
            ],

            // Action
            if (onAction != null || customAction != null) ...[
              const SizedBox(height: 32),
              customAction ??
                  ElevatedButton.icon(
                    onPressed: onAction,
                    icon: const Icon(Icons.add_rounded),
                    label: Text(actionLabel ?? 'إضافة'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: SahoolColors.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 14,
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

// ═══════════════════════════════════════════════════════════════════════════
// Predefined Empty States
// ═══════════════════════════════════════════════════════════════════════════

/// No fields empty state
class NoFieldsEmptyState extends StatelessWidget {
  final VoidCallback? onAddField;

  const NoFieldsEmptyState({
    super.key,
    this.onAddField,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolEmptyState(
      icon: Icons.grass_rounded,
      title: 'لا توجد حقول بعد',
      message: 'أضف حقلك الأول لبدء إدارة مزرعتك',
      actionLabel: 'إضافة حقل',
      onAction: onAddField,
    );
  }
}

/// No tasks empty state
class NoTasksEmptyState extends StatelessWidget {
  final VoidCallback? onAddTask;

  const NoTasksEmptyState({
    super.key,
    this.onAddTask,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolEmptyState(
      icon: Icons.task_alt_rounded,
      title: 'لا توجد مهام',
      message: 'ليس لديك أي مهام مجدولة حالياً',
      actionLabel: 'إضافة مهمة',
      onAction: onAddTask,
    );
  }
}

/// No alerts empty state
class NoAlertsEmptyState extends StatelessWidget {
  const NoAlertsEmptyState({super.key});

  @override
  Widget build(BuildContext context) {
    return const SahoolEmptyState(
      icon: Icons.notifications_none_rounded,
      title: 'لا توجد تنبيهات',
      message: 'كل شيء على ما يرام! لا توجد تنبيهات جديدة',
    );
  }
}

/// No notifications empty state
class NoNotificationsEmptyState extends StatelessWidget {
  const NoNotificationsEmptyState({super.key});

  @override
  Widget build(BuildContext context) {
    return const SahoolEmptyState(
      icon: Icons.inbox_rounded,
      title: 'صندوق الوارد فارغ',
      message: 'ستظهر هنا الإشعارات الجديدة',
    );
  }
}

/// No search results empty state
class NoSearchResultsEmptyState extends StatelessWidget {
  final String? searchQuery;
  final VoidCallback? onClear;

  const NoSearchResultsEmptyState({
    super.key,
    this.searchQuery,
    this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolEmptyState(
      icon: Icons.search_off_rounded,
      title: 'لا توجد نتائج',
      message: searchQuery != null
          ? 'لم نجد نتائج لـ "$searchQuery"'
          : 'لم نجد أي نتائج مطابقة لبحثك',
      actionLabel: 'مسح البحث',
      onAction: onClear,
    );
  }
}

/// No data empty state (generic)
class NoDataEmptyState extends StatelessWidget {
  final VoidCallback? onRefresh;

  const NoDataEmptyState({
    super.key,
    this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolEmptyState(
      icon: Icons.folder_open_rounded,
      title: 'لا توجد بيانات',
      message: 'لم يتم العثور على بيانات للعرض',
      actionLabel: 'تحديث',
      onAction: onRefresh,
    );
  }
}

/// Offline empty state
class OfflineEmptyState extends StatelessWidget {
  final VoidCallback? onRetry;

  const OfflineEmptyState({
    super.key,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolEmptyState(
      icon: Icons.cloud_off_rounded,
      title: 'أنت غير متصل',
      message: 'البيانات المحلية غير متوفرة. اتصل بالإنترنت لتحميل البيانات.',
      actionLabel: 'إعادة المحاولة',
      onAction: onRetry,
    );
  }
}

/// No equipment empty state
class NoEquipmentEmptyState extends StatelessWidget {
  final VoidCallback? onAddEquipment;

  const NoEquipmentEmptyState({
    super.key,
    this.onAddEquipment,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolEmptyState(
      icon: Icons.agriculture_rounded,
      title: 'لا توجد معدات',
      message: 'أضف معداتك الزراعية لتتبعها وإدارتها',
      actionLabel: 'إضافة معدة',
      onAction: onAddEquipment,
    );
  }
}

/// No transactions empty state
class NoTransactionsEmptyState extends StatelessWidget {
  const NoTransactionsEmptyState({super.key});

  @override
  Widget build(BuildContext context) {
    return const SahoolEmptyState(
      icon: Icons.receipt_long_rounded,
      title: 'لا توجد معاملات',
      message: 'ستظهر هنا سجل معاملاتك المالية',
    );
  }
}

/// No messages empty state
class NoMessagesEmptyState extends StatelessWidget {
  final VoidCallback? onStartChat;

  const NoMessagesEmptyState({
    super.key,
    this.onStartChat,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolEmptyState(
      icon: Icons.chat_bubble_outline_rounded,
      title: 'لا توجد رسائل',
      message: 'ابدأ محادثة مع الخبراء الزراعيين',
      actionLabel: 'بدء محادثة',
      onAction: onStartChat,
    );
  }
}

/// Coming soon empty state (for features in development)
class ComingSoonEmptyState extends StatelessWidget {
  final String featureName;

  const ComingSoonEmptyState({
    super.key,
    required this.featureName,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolEmptyState(
      icon: Icons.construction_rounded,
      title: 'قريباً',
      message: 'ميزة $featureName قيد التطوير وستكون متاحة قريباً',
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Compact Empty States
// ═══════════════════════════════════════════════════════════════════════════

/// Compact empty state for smaller spaces
class SahoolCompactEmptyState extends StatelessWidget {
  final IconData icon;
  final String message;
  final VoidCallback? onAction;
  final String? actionLabel;

  const SahoolCompactEmptyState({
    super.key,
    required this.icon,
    required this.message,
    this.onAction,
    this.actionLabel,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 40,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 12),
          Text(
            message,
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
          if (onAction != null) ...[
            const SizedBox(height: 16),
            TextButton(
              onPressed: onAction,
              child: Text(actionLabel ?? 'إضافة'),
            ),
          ],
        ],
      ),
    );
  }
}
