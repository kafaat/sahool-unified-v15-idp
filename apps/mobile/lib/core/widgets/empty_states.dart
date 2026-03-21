import 'package:flutter/material.dart';
import '../theme/sahool_theme.dart';

/// SAHOOL Empty States Widgets
/// مكونات حالات البيانات الفارغة والأخطاء
///
/// Provides consistent empty, error, and status states with:
/// - Bilingual support (Arabic primary, English secondary)
/// - Consistent visual design
/// - Action buttons for user interaction
/// - Animated icons for better UX

// ═══════════════════════════════════════════════════════════════════════════
// Base Empty State Widget
// المكون الأساسي لحالة الفراغ
// ═══════════════════════════════════════════════════════════════════════════

/// Base empty state widget with bilingual support
/// المكون الأساسي لحالة الفراغ مع دعم ثنائي اللغة
class EmptyStateWidget extends StatelessWidget {
  final IconData icon;
  final String titleAr;
  final String? titleEn;
  final String? messageAr;
  final String? messageEn;
  final String? actionLabelAr;
  final String? actionLabelEn;
  final VoidCallback? onAction;
  final Widget? customIcon;
  final Widget? customAction;
  final Color? iconColor;
  final Color? backgroundColor;
  final double iconSize;
  final bool compact;

  const EmptyStateWidget({
    super.key,
    required this.icon,
    required this.titleAr,
    this.titleEn,
    this.messageAr,
    this.messageEn,
    this.actionLabelAr,
    this.actionLabelEn,
    this.onAction,
    this.customIcon,
    this.customAction,
    this.iconColor,
    this.backgroundColor,
    this.iconSize = 64,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveIconColor = iconColor ?? SahoolColors.sageGreen;
    final effectiveBackgroundColor =
        backgroundColor ?? effectiveIconColor.withOpacity(0.15);

    return Center(
      child: Padding(
        padding: EdgeInsets.all(compact ? 16 : 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: compact ? MainAxisSize.min : MainAxisSize.max,
          children: [
            // Icon
            customIcon ??
                Container(
                  padding: EdgeInsets.all(compact ? 16 : 24),
                  decoration: BoxDecoration(
                    color: effectiveBackgroundColor,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    icon,
                    size: compact ? 48 : iconSize,
                    color: effectiveIconColor,
                  ),
                ),

            SizedBox(height: compact ? 16 : 24),

            // Title (Arabic)
            Text(
              titleAr,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: SahoolColors.textDark,
                    fontSize: compact ? 18 : 22,
                  ),
              textAlign: TextAlign.center,
            ),

            // Title (English) - optional
            if (titleEn != null && !compact) ...[
              const SizedBox(height: 4),
              Text(
                titleEn!,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.grey[600],
                      fontSize: 16,
                    ),
                textAlign: TextAlign.center,
              ),
            ],

            // Message (Arabic)
            if (messageAr != null) ...[
              SizedBox(height: compact ? 8 : 12),
              Text(
                messageAr!,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: SahoolColors.textSecondary,
                      height: 1.4,
                    ),
                textAlign: TextAlign.center,
              ),
            ],

            // Message (English) - optional
            if (messageEn != null && !compact) ...[
              const SizedBox(height: 4),
              Text(
                messageEn!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[500],
                    ),
                textAlign: TextAlign.center,
              ),
            ],

            // Action
            if (onAction != null || customAction != null) ...[
              SizedBox(height: compact ? 20 : 32),
              customAction ??
                  ElevatedButton.icon(
                    onPressed: onAction,
                    icon: const Icon(Icons.add_rounded),
                    label: Text(actionLabelAr ?? 'إضافة'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: SahoolColors.primary,
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(
                        horizontal: compact ? 20 : 24,
                        vertical: compact ? 12 : 14,
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

/// Alias for backward compatibility
typedef SahoolEmptyState = EmptyStateWidget;

// ═══════════════════════════════════════════════════════════════════════════
// Error State Widget
// مكون حالة الخطأ
// ═══════════════════════════════════════════════════════════════════════════

/// Error state widget with retry functionality
/// مكون حالة الخطأ مع إمكانية إعادة المحاولة
class ErrorStateWidget extends StatelessWidget {
  final String? errorAr;
  final String? errorEn;
  final String? detailsAr;
  final String? detailsEn;
  final VoidCallback? onRetry;
  final VoidCallback? onGoBack;
  final bool showDetails;
  final IconData icon;
  final Color? iconColor;

  const ErrorStateWidget({
    super.key,
    this.errorAr,
    this.errorEn,
    this.detailsAr,
    this.detailsEn,
    this.onRetry,
    this.onGoBack,
    this.showDetails = false,
    this.icon = Icons.error_outline_rounded,
    this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Error icon
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: (iconColor ?? SahoolColors.danger).withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                size: 56,
                color: iconColor ?? SahoolColors.danger,
              ),
            ),

            const SizedBox(height: 24),

            // Error title (Arabic)
            Text(
              errorAr ?? 'حدث خطأ',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: SahoolColors.textDark,
                  ),
              textAlign: TextAlign.center,
            ),

            // Error title (English)
            if (errorEn != null) ...[
              const SizedBox(height: 4),
              Text(
                errorEn!,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.grey[600],
                    ),
                textAlign: TextAlign.center,
              ),
            ],

            const SizedBox(height: 12),

            // Error details
            if (detailsAr != null || detailsEn != null) ...[
              Text(
                detailsAr ?? detailsEn ?? '',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: SahoolColors.textSecondary,
                    ),
                textAlign: TextAlign.center,
              ),
              if (detailsEn != null && detailsAr != null) ...[
                const SizedBox(height: 4),
                Text(
                  detailsEn!,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey[500],
                      ),
                  textAlign: TextAlign.center,
                ),
              ],
            ],

            const SizedBox(height: 32),

            // Action buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (onGoBack != null) ...[
                  OutlinedButton.icon(
                    onPressed: onGoBack,
                    icon: const Icon(Icons.arrow_back_rounded),
                    label: const Text('رجوع'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: SahoolColors.textSecondary,
                      side: BorderSide(color: Colors.grey[300]!),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 12,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                ],
                if (onRetry != null)
                  ElevatedButton.icon(
                    onPressed: onRetry,
                    icon: const Icon(Icons.refresh_rounded),
                    label: const Text('إعادة المحاولة'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: SahoolColors.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 12,
                      ),
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// No Network State Widget
// مكون حالة عدم الاتصال
// ═══════════════════════════════════════════════════════════════════════════

/// No network connection state widget
/// مكون حالة عدم وجود اتصال بالشبكة
class NoNetworkWidget extends StatelessWidget {
  final VoidCallback? onRetry;
  final bool showOfflineDataOption;
  final VoidCallback? onViewOfflineData;

  const NoNetworkWidget({
    super.key,
    this.onRetry,
    this.showOfflineDataOption = true,
    this.onViewOfflineData,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Network icon with animation
            _AnimatedNetworkIcon(),

            const SizedBox(height: 24),

            // Title (Arabic)
            Text(
              'لا يوجد اتصال بالإنترنت',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: SahoolColors.textDark,
                  ),
              textAlign: TextAlign.center,
            ),

            // Title (English)
            const SizedBox(height: 4),
            Text(
              'No internet connection',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Colors.grey[600],
                  ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 12),

            // Message
            Text(
              'تحقق من اتصالك بالإنترنت وحاول مرة أخرى',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: SahoolColors.textSecondary,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              'Check your connection and try again',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey[500],
                  ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 32),

            // Retry button
            if (onRetry != null)
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('إعادة المحاولة'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 14,
                  ),
                ),
              ),

            // Offline data option
            if (showOfflineDataOption && onViewOfflineData != null) ...[
              const SizedBox(height: 16),
              TextButton.icon(
                onPressed: onViewOfflineData,
                icon: const Icon(Icons.offline_bolt_outlined),
                label: const Text('عرض البيانات المحفوظة'),
                style: TextButton.styleFrom(
                  foregroundColor: SahoolColors.textSecondary,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// Animated network icon for no connection state
class _AnimatedNetworkIcon extends StatefulWidget {
  @override
  State<_AnimatedNetworkIcon> createState() => _AnimatedNetworkIconState();
}

class _AnimatedNetworkIconState extends State<_AnimatedNetworkIcon>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _animation = Tween<double>(begin: 0.8, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Transform.scale(
          scale: _animation.value,
          child: Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.grey[200],
              shape: BoxShape.circle,
            ),
            child: Stack(
              alignment: Alignment.center,
              children: [
                Icon(
                  Icons.wifi_rounded,
                  size: 56,
                  color: Colors.grey[400],
                ),
                Positioned(
                  bottom: 0,
                  right: 0,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: SahoolColors.danger,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.close_rounded,
                      size: 16,
                      color: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// No Data State Widget
// مكون حالة عدم وجود بيانات
// ═══════════════════════════════════════════════════════════════════════════

/// Generic no data state widget
/// مكون حالة عدم وجود بيانات عام
class NoDataWidget extends StatelessWidget {
  final VoidCallback? onRefresh;
  final String? titleAr;
  final String? titleEn;
  final String? messageAr;
  final String? messageEn;
  final IconData icon;

  const NoDataWidget({
    super.key,
    this.onRefresh,
    this.titleAr,
    this.titleEn,
    this.messageAr,
    this.messageEn,
    this.icon = Icons.inbox_rounded,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      icon: icon,
      titleAr: titleAr ?? 'لا توجد بيانات',
      titleEn: titleEn ?? 'No data available',
      messageAr: messageAr ?? 'لم يتم العثور على بيانات للعرض',
      messageEn: messageEn ?? 'No data found to display',
      actionLabelAr: 'تحديث',
      actionLabelEn: 'Refresh',
      onAction: onRefresh,
      iconColor: SahoolColors.info,
      customAction: onRefresh != null
          ? OutlinedButton.icon(
              onPressed: onRefresh,
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('تحديث'),
              style: OutlinedButton.styleFrom(
                foregroundColor: SahoolColors.primary,
                side: const BorderSide(color: SahoolColors.primary),
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 14,
                ),
              ),
            )
          : null,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Predefined Empty States
// حالات الفراغ المعرفة مسبقاً
// ═══════════════════════════════════════════════════════════════════════════

/// No fields empty state
/// حالة عدم وجود حقول
class NoFieldsEmptyState extends StatelessWidget {
  final VoidCallback? onAddField;

  const NoFieldsEmptyState({
    super.key,
    this.onAddField,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      icon: Icons.grass_rounded,
      titleAr: 'لا توجد حقول بعد',
      titleEn: 'No fields yet',
      messageAr: 'أضف حقلك الأول لبدء إدارة مزرعتك',
      messageEn: 'Add your first field to start managing your farm',
      actionLabelAr: 'إضافة حقل',
      onAction: onAddField,
    );
  }
}

/// No tasks empty state
/// حالة عدم وجود مهام
class NoTasksEmptyState extends StatelessWidget {
  final VoidCallback? onAddTask;

  const NoTasksEmptyState({
    super.key,
    this.onAddTask,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      icon: Icons.task_alt_rounded,
      titleAr: 'لا توجد مهام',
      titleEn: 'No tasks',
      messageAr: 'ليس لديك أي مهام مجدولة حالياً',
      messageEn: 'You don\'t have any scheduled tasks',
      actionLabelAr: 'إضافة مهمة',
      onAction: onAddTask,
      iconColor: SahoolColors.info,
    );
  }
}

/// No alerts empty state
/// حالة عدم وجود تنبيهات
class NoAlertsEmptyState extends StatelessWidget {
  const NoAlertsEmptyState({super.key});

  @override
  Widget build(BuildContext context) {
    return const EmptyStateWidget(
      icon: Icons.notifications_none_rounded,
      titleAr: 'لا توجد تنبيهات',
      titleEn: 'No alerts',
      messageAr: 'كل شيء على ما يرام! لا توجد تنبيهات جديدة',
      messageEn: 'Everything is fine! No new alerts',
      iconColor: SahoolColors.success,
    );
  }
}

/// No notifications empty state
/// حالة عدم وجود إشعارات
class NoNotificationsEmptyState extends StatelessWidget {
  const NoNotificationsEmptyState({super.key});

  @override
  Widget build(BuildContext context) {
    return const EmptyStateWidget(
      icon: Icons.inbox_rounded,
      titleAr: 'صندوق الوارد فارغ',
      titleEn: 'Inbox is empty',
      messageAr: 'ستظهر هنا الإشعارات الجديدة',
      messageEn: 'New notifications will appear here',
      iconColor: SahoolColors.info,
    );
  }
}

/// No search results empty state
/// حالة عدم وجود نتائج بحث
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
    return EmptyStateWidget(
      icon: Icons.search_off_rounded,
      titleAr: 'لا توجد نتائج',
      titleEn: 'No results found',
      messageAr: searchQuery != null
          ? 'لم نجد نتائج لـ "$searchQuery"'
          : 'لم نجد أي نتائج مطابقة لبحثك',
      messageEn: searchQuery != null
          ? 'No results for "$searchQuery"'
          : 'No matching results found',
      actionLabelAr: 'مسح البحث',
      onAction: onClear,
      iconColor: SahoolColors.textSecondary,
      customAction: onClear != null
          ? TextButton.icon(
              onPressed: onClear,
              icon: const Icon(Icons.clear_rounded),
              label: const Text('مسح البحث'),
              style: TextButton.styleFrom(
                foregroundColor: SahoolColors.primary,
              ),
            )
          : null,
    );
  }
}

/// No data empty state (generic)
/// حالة عدم وجود بيانات (عام)
class NoDataEmptyState extends StatelessWidget {
  final VoidCallback? onRefresh;

  const NoDataEmptyState({
    super.key,
    this.onRefresh,
  });

  @override
  Widget build(BuildContext context) {
    return NoDataWidget(onRefresh: onRefresh);
  }
}

/// Offline empty state
/// حالة عدم الاتصال
class OfflineEmptyState extends StatelessWidget {
  final VoidCallback? onRetry;

  const OfflineEmptyState({
    super.key,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return NoNetworkWidget(
      onRetry: onRetry,
      showOfflineDataOption: false,
    );
  }
}

/// No equipment empty state
/// حالة عدم وجود معدات
class NoEquipmentEmptyState extends StatelessWidget {
  final VoidCallback? onAddEquipment;

  const NoEquipmentEmptyState({
    super.key,
    this.onAddEquipment,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      icon: Icons.agriculture_rounded,
      titleAr: 'لا توجد معدات',
      titleEn: 'No equipment',
      messageAr: 'أضف معداتك الزراعية لتتبعها وإدارتها',
      messageEn: 'Add your agricultural equipment to track and manage',
      actionLabelAr: 'إضافة معدة',
      onAction: onAddEquipment,
      iconColor: SahoolColors.earthBrown,
    );
  }
}

/// No transactions empty state
/// حالة عدم وجود معاملات
class NoTransactionsEmptyState extends StatelessWidget {
  const NoTransactionsEmptyState({super.key});

  @override
  Widget build(BuildContext context) {
    return const EmptyStateWidget(
      icon: Icons.receipt_long_rounded,
      titleAr: 'لا توجد معاملات',
      titleEn: 'No transactions',
      messageAr: 'ستظهر هنا سجل معاملاتك المالية',
      messageEn: 'Your financial transaction history will appear here',
      iconColor: SahoolColors.harvestGold,
    );
  }
}

/// No messages empty state
/// حالة عدم وجود رسائل
class NoMessagesEmptyState extends StatelessWidget {
  final VoidCallback? onStartChat;

  const NoMessagesEmptyState({
    super.key,
    this.onStartChat,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      icon: Icons.chat_bubble_outline_rounded,
      titleAr: 'لا توجد رسائل',
      titleEn: 'No messages',
      messageAr: 'ابدأ محادثة مع الخبراء الزراعيين',
      messageEn: 'Start a conversation with agricultural experts',
      actionLabelAr: 'بدء محادثة',
      onAction: onStartChat,
      iconColor: SahoolColors.info,
    );
  }
}

/// No weather data empty state
/// حالة عدم وجود بيانات الطقس
class NoWeatherDataEmptyState extends StatelessWidget {
  final VoidCallback? onRetry;

  const NoWeatherDataEmptyState({
    super.key,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      icon: Icons.cloud_off_rounded,
      titleAr: 'بيانات الطقس غير متوفرة',
      titleEn: 'Weather data unavailable',
      messageAr: 'تعذر تحميل بيانات الطقس. حاول مرة أخرى',
      messageEn: 'Could not load weather data. Please try again',
      actionLabelAr: 'إعادة المحاولة',
      onAction: onRetry,
      iconColor: SahoolColors.info,
    );
  }
}

/// No NDVI data empty state
/// حالة عدم وجود بيانات NDVI
class NoNdviDataEmptyState extends StatelessWidget {
  final VoidCallback? onRetry;

  const NoNdviDataEmptyState({
    super.key,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      icon: Icons.satellite_alt_rounded,
      titleAr: 'بيانات الغطاء النباتي غير متوفرة',
      titleEn: 'Vegetation data unavailable',
      messageAr: 'لا تتوفر صور أقمار صناعية حديثة لهذا الحقل',
      messageEn: 'No recent satellite imagery available for this field',
      actionLabelAr: 'تحديث',
      onAction: onRetry,
      iconColor: SahoolColors.sageGreen,
    );
  }
}

/// Coming soon empty state (for features in development)
/// حالة قريباً (للميزات قيد التطوير)
class ComingSoonEmptyState extends StatelessWidget {
  final String featureName;
  final String? featureNameEn;

  const ComingSoonEmptyState({
    super.key,
    required this.featureName,
    this.featureNameEn,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      icon: Icons.construction_rounded,
      titleAr: 'قريباً',
      titleEn: 'Coming Soon',
      messageAr: 'ميزة $featureName قيد التطوير وستكون متاحة قريباً',
      messageEn: featureNameEn != null
          ? '$featureNameEn feature is under development'
          : 'This feature is under development',
      iconColor: SahoolColors.harvestGold,
    );
  }
}

/// Permission denied empty state
/// حالة رفض الإذن
class PermissionDeniedEmptyState extends StatelessWidget {
  final String permissionAr;
  final String? permissionEn;
  final VoidCallback? onOpenSettings;

  const PermissionDeniedEmptyState({
    super.key,
    required this.permissionAr,
    this.permissionEn,
    this.onOpenSettings,
  });

  @override
  Widget build(BuildContext context) {
    return EmptyStateWidget(
      icon: Icons.lock_outline_rounded,
      titleAr: 'الإذن مطلوب',
      titleEn: 'Permission Required',
      messageAr: 'يحتاج التطبيق إلى إذن $permissionAr للمتابعة',
      messageEn: permissionEn != null
          ? 'App needs $permissionEn permission to continue'
          : null,
      actionLabelAr: 'فتح الإعدادات',
      onAction: onOpenSettings,
      iconColor: SahoolColors.warning,
      customAction: onOpenSettings != null
          ? ElevatedButton.icon(
              onPressed: onOpenSettings,
              icon: const Icon(Icons.settings_rounded),
              label: const Text('فتح الإعدادات'),
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 14,
                ),
              ),
            )
          : null,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Compact Empty States
// حالات الفراغ المضغوطة
// ═══════════════════════════════════════════════════════════════════════════

/// Compact empty state for smaller spaces
/// حالة فراغ مضغوطة للمساحات الصغيرة
class SahoolCompactEmptyState extends StatelessWidget {
  final IconData icon;
  final String message;
  final String? messageEn;
  final VoidCallback? onAction;
  final String? actionLabel;

  const SahoolCompactEmptyState({
    super.key,
    required this.icon,
    required this.message,
    this.messageEn,
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
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
          ),
          if (messageEn != null) ...[
            const SizedBox(height: 4),
            Text(
              messageEn!,
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
          ],
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

/// Empty list item placeholder
/// عنصر قائمة فارغ نائب
class EmptyListItem extends StatelessWidget {
  final String textAr;
  final String? textEn;
  final IconData icon;
  final VoidCallback? onTap;

  const EmptyListItem({
    super.key,
    required this.textAr,
    this.textEn,
    this.icon = Icons.add_circle_outline_rounded,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(
            color: Colors.grey[300]!,
            style: BorderStyle.solid,
          ),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              color: SahoolColors.primary,
              size: 24,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    textAr,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  if (textEn != null)
                    Text(
                      textEn!,
                      style: TextStyle(
                        color: Colors.grey[500],
                        fontSize: 12,
                      ),
                    ),
                ],
              ),
            ),
            if (onTap != null)
              Icon(
                Icons.chevron_left_rounded,
                color: Colors.grey[400],
              ),
          ],
        ),
      ),
    );
  }
}
