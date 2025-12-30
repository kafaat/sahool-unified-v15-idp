import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';
import '../providers/sync_events_provider.dart';

/// Sync Status Banner Widget
/// لافتة تنبيه للحالات الهامة (غير متصل، خطأ، تعارضات)
class SyncStatusBanner extends ConsumerWidget {
  final VoidCallback? onRetryTap;
  final VoidCallback? onDismiss;
  final bool dismissible;

  const SyncStatusBanner({
    super.key,
    this.onRetryTap,
    this.onDismiss,
    this.dismissible = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncStatus = ref.watch(syncStatusProvider);
    final conflictsCount = ref.watch(unreadConflictsCountProvider);

    // Determine which banner to show (priority order)
    if (!syncStatus.isOnline) {
      return _buildOfflineBanner(context);
    }

    if (syncStatus.hasError) {
      return _buildErrorBanner(context, syncStatus.lastError);
    }

    if (conflictsCount > 0) {
      return _buildConflictsBanner(context, conflictsCount);
    }

    if (syncStatus.failedCount > 5) {
      return _buildWarningBanner(
        context,
        'يوجد ${syncStatus.failedCount} عنصر فشل في المزامنة',
        SahoolColors.warning,
      );
    }

    // No banner needed
    return const SizedBox.shrink();
  }

  /// Offline mode banner
  Widget _buildOfflineBanner(BuildContext context) {
    return _BannerContainer(
      color: SahoolColors.danger,
      icon: Icons.cloud_off,
      title: 'وضع عدم الاتصال',
      message: 'لا يوجد اتصال بالإنترنت. سيتم حفظ التغييرات محلياً.',
      dismissible: false,
      actions: [
        TextButton.icon(
          onPressed: onRetryTap,
          icon: const Icon(Icons.refresh, color: Colors.white, size: 18),
          label: const Text(
            'إعادة المحاولة',
            style: TextStyle(color: Colors.white),
          ),
        ),
      ],
    );
  }

  /// Error banner
  Widget _buildErrorBanner(BuildContext context, String? error) {
    return _BannerContainer(
      color: SahoolColors.danger,
      icon: Icons.error_outline,
      title: 'خطأ في المزامنة',
      message: error ?? 'حدث خطأ غير متوقع أثناء المزامنة',
      dismissible: dismissible,
      onDismiss: onDismiss,
      actions: [
        if (onRetryTap != null)
          TextButton.icon(
            onPressed: onRetryTap,
            icon: const Icon(Icons.refresh, color: Colors.white, size: 18),
            label: const Text(
              'إعادة المحاولة',
              style: TextStyle(color: Colors.white),
            ),
          ),
      ],
    );
  }

  /// Conflicts banner
  Widget _buildConflictsBanner(BuildContext context, int count) {
    return _BannerContainer(
      color: SahoolColors.warning,
      icon: Icons.warning_amber_rounded,
      title: 'يوجد تعارضات في البيانات',
      message: 'يوجد $count ${count == 1 ? 'تعارض' : 'تعارضات'} تحتاج لمراجعة',
      dismissible: dismissible,
      onDismiss: onDismiss,
      actions: [
        TextButton.icon(
          onPressed: () {
            // Navigate to sync details or conflicts
            if (onRetryTap != null) onRetryTap!();
          },
          icon: const Icon(Icons.visibility, color: Colors.white, size: 18),
          label: const Text(
            'عرض',
            style: TextStyle(color: Colors.white),
          ),
        ),
      ],
    );
  }

  /// Warning banner
  Widget _buildWarningBanner(BuildContext context, String message, Color color) {
    return _BannerContainer(
      color: color,
      icon: Icons.info_outline,
      title: 'تنبيه',
      message: message,
      dismissible: dismissible,
      onDismiss: onDismiss,
      actions: [
        if (onRetryTap != null)
          TextButton.icon(
            onPressed: onRetryTap,
            icon: const Icon(Icons.refresh, color: Colors.white, size: 18),
            label: const Text(
              'إعادة المحاولة',
              style: TextStyle(color: Colors.white),
            ),
          ),
      ],
    );
  }
}

/// Animated Sync Status Banner
/// لافتة متحركة تظهر/تختفي بشكل تلقائي
class AnimatedSyncStatusBanner extends StatefulWidget {
  final VoidCallback? onRetryTap;
  final VoidCallback? onDismiss;
  final bool dismissible;

  const AnimatedSyncStatusBanner({
    super.key,
    this.onRetryTap,
    this.onDismiss,
    this.dismissible = true,
  });

  @override
  State<AnimatedSyncStatusBanner> createState() =>
      _AnimatedSyncStatusBannerState();
}

class _AnimatedSyncStatusBannerState extends State<AnimatedSyncStatusBanner>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _animation = CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0, -1),
        end: Offset.zero,
      ).animate(_animation),
      child: FadeTransition(
        opacity: _animation,
        child: SyncStatusBanner(
          onRetryTap: widget.onRetryTap,
          onDismiss: () {
            _controller.reverse().then((_) {
              if (widget.onDismiss != null) {
                widget.onDismiss!();
              }
            });
          },
          dismissible: widget.dismissible,
        ),
      ),
    );
  }
}

/// Internal Banner Container
class _BannerContainer extends StatelessWidget {
  final Color color;
  final IconData icon;
  final String title;
  final String message;
  final List<Widget> actions;
  final bool dismissible;
  final VoidCallback? onDismiss;

  const _BannerContainer({
    required this.color,
    required this.icon,
    required this.title,
    required this.message,
    this.actions = const [],
    this.dismissible = true,
    this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color,
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: SafeArea(
        bottom: false,
        child: Row(
          children: [
            // Icon
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                color: Colors.white,
                size: 24,
              ),
            ),
            const SizedBox(width: 12),

            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    message,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 12,
                    ),
                  ),
                  if (actions.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Row(
                      children: actions,
                    ),
                  ],
                ],
              ),
            ),

            // Dismiss button
            if (dismissible && onDismiss != null)
              IconButton(
                onPressed: onDismiss,
                icon: const Icon(Icons.close, color: Colors.white),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
              ),
          ],
        ),
      ),
    );
  }
}

/// Floating Sync Status Banner
/// لافتة عائمة (Snackbar-like) في أسفل الشاشة
class FloatingSyncStatusBanner extends StatelessWidget {
  final String message;
  final Color backgroundColor;
  final IconData icon;
  final VoidCallback? onActionTap;
  final String? actionLabel;
  final Duration duration;

  const FloatingSyncStatusBanner({
    super.key,
    required this.message,
    required this.backgroundColor,
    required this.icon,
    this.onActionTap,
    this.actionLabel,
    this.duration = const Duration(seconds: 4),
  });

  static void show(
    BuildContext context, {
    required String message,
    required Color backgroundColor,
    required IconData icon,
    VoidCallback? onActionTap,
    String? actionLabel,
    Duration duration = const Duration(seconds: 4),
  }) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(icon, color: Colors.white),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                message,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: backgroundColor,
        behavior: SnackBarBehavior.floating,
        duration: duration,
        action: onActionTap != null && actionLabel != null
            ? SnackBarAction(
                label: actionLabel,
                textColor: Colors.white,
                onPressed: onActionTap,
              )
            : null,
      ),
    );
  }

  /// Show offline banner
  static void showOffline(BuildContext context, {VoidCallback? onRetry}) {
    show(
      context,
      message: 'لا يوجد اتصال بالإنترنت',
      backgroundColor: SahoolColors.danger,
      icon: Icons.cloud_off,
      onActionTap: onRetry,
      actionLabel: onRetry != null ? 'إعادة' : null,
    );
  }

  /// Show sync error banner
  static void showError(BuildContext context, String error, {VoidCallback? onRetry}) {
    show(
      context,
      message: error,
      backgroundColor: SahoolColors.danger,
      icon: Icons.error_outline,
      onActionTap: onRetry,
      actionLabel: onRetry != null ? 'إعادة' : null,
    );
  }

  /// Show sync success banner
  static void showSuccess(BuildContext context, {String? message}) {
    show(
      context,
      message: message ?? 'تمت المزامنة بنجاح',
      backgroundColor: SahoolColors.success,
      icon: Icons.check_circle,
      duration: const Duration(seconds: 2),
    );
  }

  /// Show syncing banner
  static void showSyncing(BuildContext context) {
    show(
      context,
      message: 'جاري المزامنة...',
      backgroundColor: SahoolColors.info,
      icon: Icons.sync,
      duration: const Duration(seconds: 2),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: backgroundColor,
        borderRadius: SahoolRadius.mediumRadius,
        boxShadow: SahoolShadows.large,
      ),
      child: Row(
        children: [
          Icon(icon, color: Colors.white),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(color: Colors.white),
            ),
          ),
          if (onActionTap != null && actionLabel != null)
            TextButton(
              onPressed: onActionTap,
              child: Text(
                actionLabel!,
                style: const TextStyle(color: Colors.white),
              ),
            ),
        ],
      ),
    );
  }
}
