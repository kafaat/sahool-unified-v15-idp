/// SAHOOL Offline UI Components
/// مكونات واجهة المستخدم للوضع غير المتصل
///
/// Features:
/// - Sync status indicator
/// - Pending changes badge
/// - Conflict resolution dialog
/// - Offline mode banner
/// - Queue status widget

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../config/theme.dart';
import '../sync/network_status.dart';
import '../utils/app_logger.dart';
import 'offline_sync_engine.dart' as sync_engine;

// =============================================================================
// Sync Status Indicator - مؤشر حالة المزامنة
// =============================================================================

/// Visual indicator for sync status
/// مؤشر مرئي لحالة المزامنة
class SyncStatusIndicator extends ConsumerWidget {
  final double size;
  final bool showLabel;

  const SyncStatusIndicator({
    super.key,
    this.size = 24,
    this.showLabel = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncStatus = ref.watch(sync_engine.syncStatusProvider).when(
      data: (engineStatus) => _mapEngineStatus(engineStatus),
      loading: () => SyncStatus.syncing,
      error: (_, __) => SyncStatus.error,
    );
    final networkStatus = ref.watch(networkStatusProvider);

    final color = _getStatusColor(syncStatus, networkStatus.isConnected);
    final icon = _getStatusIcon(syncStatus, networkStatus.isConnected);
    final label = _getStatusLabel(syncStatus, networkStatus.isConnected);

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _AnimatedSyncIcon(
          icon: icon,
          color: color,
          size: size,
          isAnimating: syncStatus == SyncStatus.syncing,
        ),
        if (showLabel) ...[
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ],
    );
  }

  /// Maps engine SyncStatus to UI SyncStatus
  SyncStatus _mapEngineStatus(sync_engine.SyncStatus engineStatus) {
    switch (engineStatus) {
      case sync_engine.SyncStatus.idle:
        return SyncStatus.idle;
      case sync_engine.SyncStatus.syncing:
        return SyncStatus.syncing;
      case sync_engine.SyncStatus.success:
        return SyncStatus.idle;
      case sync_engine.SyncStatus.partialSuccess:
        return SyncStatus.pending;
      case sync_engine.SyncStatus.error:
        return SyncStatus.error;
      case sync_engine.SyncStatus.offline:
        return SyncStatus.offline;
    }
  }

  Color _getStatusColor(SyncStatus status, bool isOnline) {
    if (!isOnline) return Colors.grey;

    switch (status) {
      case SyncStatus.idle:
        return SahoolTheme.success;
      case SyncStatus.syncing:
        return SahoolTheme.info;
      case SyncStatus.pending:
        return SahoolTheme.warning;
      case SyncStatus.error:
        return SahoolTheme.error;
      case SyncStatus.offline:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon(SyncStatus status, bool isOnline) {
    if (!isOnline) return Icons.cloud_off_rounded;

    switch (status) {
      case SyncStatus.idle:
        return Icons.cloud_done_rounded;
      case SyncStatus.syncing:
        return Icons.sync_rounded;
      case SyncStatus.pending:
        return Icons.cloud_upload_rounded;
      case SyncStatus.error:
        return Icons.cloud_off_rounded;
      case SyncStatus.offline:
        return Icons.cloud_off_rounded;
    }
  }

  String _getStatusLabel(SyncStatus status, bool isOnline) {
    if (!isOnline) return 'غير متصل';

    switch (status) {
      case SyncStatus.idle:
        return 'متزامن';
      case SyncStatus.syncing:
        return 'جاري المزامنة...';
      case SyncStatus.pending:
        return 'في انتظار المزامنة';
      case SyncStatus.error:
        return 'خطأ في المزامنة';
      case SyncStatus.offline:
        return 'غير متصل';
    }
  }
}

class _AnimatedSyncIcon extends StatefulWidget {
  final IconData icon;
  final Color color;
  final double size;
  final bool isAnimating;

  const _AnimatedSyncIcon({
    required this.icon,
    required this.color,
    required this.size,
    required this.isAnimating,
  });

  @override
  State<_AnimatedSyncIcon> createState() => _AnimatedSyncIconState();
}

class _AnimatedSyncIconState extends State<_AnimatedSyncIcon>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    );
    if (widget.isAnimating) _controller.repeat();
  }

  @override
  void didUpdateWidget(_AnimatedSyncIcon oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isAnimating && !oldWidget.isAnimating) {
      _controller.repeat();
    } else if (!widget.isAnimating && oldWidget.isAnimating) {
      _controller.stop();
      _controller.reset();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return RotationTransition(
      turns: widget.isAnimating ? _controller : const AlwaysStoppedAnimation(0),
      child: Icon(
        widget.icon,
        color: widget.color,
        size: widget.size,
      ),
    );
  }
}

// =============================================================================
// Pending Changes Badge - شارة التغييرات المعلقة
// =============================================================================

/// Badge showing number of pending sync changes
/// شارة تعرض عدد التغييرات المعلقة للمزامنة
class PendingChangesBadge extends StatelessWidget {
  final int count;
  final Widget child;
  final Color? badgeColor;
  final Color? textColor;

  const PendingChangesBadge({
    super.key,
    required this.count,
    required this.child,
    this.badgeColor,
    this.textColor,
  });

  @override
  Widget build(BuildContext context) {
    if (count == 0) return child;

    return Stack(
      clipBehavior: Clip.none,
      children: [
        child,
        Positioned(
          right: -6,
          top: -6,
          child: TweenAnimationBuilder<double>(
            tween: Tween(begin: 0, end: 1),
            duration: const Duration(milliseconds: 300),
            curve: Curves.elasticOut,
            builder: (context, value, child) {
              return Transform.scale(
                scale: value,
                child: child,
              );
            },
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: badgeColor ?? SahoolTheme.warning,
                borderRadius: BorderRadius.circular(10),
                boxShadow: [
                  BoxShadow(
                    color: (badgeColor ?? SahoolTheme.warning)
                        .withValues(alpha: 0.4),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              constraints: const BoxConstraints(minWidth: 18),
              child: Text(
                count > 99 ? '99+' : count.toString(),
                style: TextStyle(
                  color: textColor ?? Colors.white,
                  fontSize: 10,
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
// Sync Conflict Dialog - حوار تعارض المزامنة
// =============================================================================

/// Dialog for resolving sync conflicts
/// حوار لحل تعارضات المزامنة
class SyncConflictDialog extends StatelessWidget {
  final SyncConflict conflict;
  final VoidCallback? onKeepLocal;
  final VoidCallback? onKeepRemote;
  final VoidCallback? onMerge;

  const SyncConflictDialog({
    super.key,
    required this.conflict,
    this.onKeepLocal,
    this.onKeepRemote,
    this.onMerge,
  });

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: SahoolTheme.warning.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.compare_arrows_rounded,
                color: SahoolTheme.warning,
              ),
            ),
            const SizedBox(width: 12),
            const Text('تعارض في البيانات'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'تم تعديل "${conflict.entityName}" من أكثر من مكان.',
              style: const TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 16),
            _ConflictOption(
              title: 'النسخة المحلية',
              subtitle: 'التعديلات التي أجريتها على هذا الجهاز',
              timestamp: conflict.localTimestamp,
              icon: Icons.phone_android_rounded,
              color: SahoolTheme.info,
            ),
            const SizedBox(height: 12),
            _ConflictOption(
              title: 'النسخة السحابية',
              subtitle: 'التعديلات المحفوظة على الخادم',
              timestamp: conflict.remoteTimestamp,
              icon: Icons.cloud_rounded,
              color: SahoolTheme.primary,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              HapticFeedback.selectionClick();
              onKeepLocal?.call();
              Navigator.of(context).pop();
            },
            child: const Text('استخدام المحلية'),
          ),
          TextButton(
            onPressed: () {
              HapticFeedback.selectionClick();
              onKeepRemote?.call();
              Navigator.of(context).pop();
            },
            child: const Text('استخدام السحابية'),
          ),
          if (onMerge != null)
            ElevatedButton(
              onPressed: () {
                HapticFeedback.selectionClick();
                onMerge?.call();
                Navigator.of(context).pop();
              },
              child: const Text('دمج التغييرات'),
            ),
        ],
      ),
    );
  }
}

class _ConflictOption extends StatelessWidget {
  final String title;
  final String subtitle;
  final DateTime timestamp;
  final IconData icon;
  final Color color;

  const _ConflictOption({
    required this.title,
    required this.subtitle,
    required this.timestamp,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
                Text(
                  _formatTimestamp(timestamp),
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatTimestamp(DateTime timestamp) {
    final now = DateTime.now();
    final diff = now.difference(timestamp);

    if (diff.inMinutes < 1) return 'الآن';
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inDays} يوم';
  }
}

// =============================================================================
// Offline Mode Banner - شريط وضع عدم الاتصال
// =============================================================================

/// Persistent banner for offline mode
/// شريط دائم لوضع عدم الاتصال
class OfflineModeBanner extends ConsumerWidget {
  final bool showRetryButton;
  final VoidCallback? onRetry;

  const OfflineModeBanner({
    super.key,
    this.showRetryButton = true,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final networkStatus = ref.watch(networkStatusProvider);

    if (networkStatus.isConnected) return const SizedBox.shrink();

    return Material(
      color: Colors.grey[800],
      child: Directionality(
        textDirection: TextDirection.rtl,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.wifi_off_rounded,
                  color: Colors.white,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      'أنت غير متصل بالإنترنت',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                      ),
                    ),
                    Text(
                      'التغييرات ستُزامن عند عودة الاتصال',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
              ),
              if (showRetryButton)
                TextButton(
                  onPressed: () {
                    HapticFeedback.lightImpact();
                    onRetry?.call();
                  },
                  style: TextButton.styleFrom(
                    foregroundColor: Colors.white,
                    backgroundColor: Colors.white.withValues(alpha: 0.1),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                  ),
                  child: const Text(
                    'إعادة المحاولة',
                    style: TextStyle(fontSize: 12),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// =============================================================================
// Sync Queue Status - حالة قائمة المزامنة
// =============================================================================

/// Widget showing sync queue status
/// مكون يعرض حالة قائمة المزامنة
class SyncQueueStatus extends StatelessWidget {
  final int pendingCount;
  final int failedCount;
  final VoidCallback? onViewQueue;
  final VoidCallback? onRetryFailed;

  const SyncQueueStatus({
    super.key,
    required this.pendingCount,
    this.failedCount = 0,
    this.onViewQueue,
    this.onRetryFailed,
  });

  @override
  Widget build(BuildContext context) {
    if (pendingCount == 0 && failedCount == 0) {
      return const SizedBox.shrink();
    }

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Card(
        margin: const EdgeInsets.all(16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(
                    Icons.sync_rounded,
                    color: SahoolTheme.primary,
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Text(
                      'قائمة المزامنة',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ),
                  if (onViewQueue != null)
                    TextButton(
                      onPressed: onViewQueue,
                      child: const Text('عرض الكل'),
                    ),
                ],
              ),
              const Divider(),
              if (pendingCount > 0)
                _QueueItem(
                  icon: Icons.hourglass_empty_rounded,
                  color: SahoolTheme.warning,
                  label: 'في الانتظار',
                  count: pendingCount,
                ),
              if (failedCount > 0) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: _QueueItem(
                        icon: Icons.error_outline_rounded,
                        color: SahoolTheme.error,
                        label: 'فشل',
                        count: failedCount,
                      ),
                    ),
                    if (onRetryFailed != null)
                      IconButton(
                        onPressed: onRetryFailed,
                        icon: const Icon(Icons.refresh_rounded),
                        color: SahoolTheme.error,
                        tooltip: 'إعادة المحاولة',
                      ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _QueueItem extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String label;
  final int count;

  const _QueueItem({
    required this.icon,
    required this.color,
    required this.label,
    required this.count,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 14,
          ),
        ),
        const Spacer(),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            count.toString(),
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
        ),
      ],
    );
  }
}

// =============================================================================
// Data Classes - فئات البيانات
// =============================================================================

/// Sync conflict data
/// بيانات تعارض المزامنة
class SyncConflict {
  final String entityId;
  final String entityType;
  final String entityName;
  final DateTime localTimestamp;
  final DateTime remoteTimestamp;
  final Map<String, dynamic> localData;
  final Map<String, dynamic> remoteData;

  const SyncConflict({
    required this.entityId,
    required this.entityType,
    required this.entityName,
    required this.localTimestamp,
    required this.remoteTimestamp,
    required this.localData,
    required this.remoteData,
  });
}

/// Sync status enum
/// تعداد حالة المزامنة
enum SyncStatus {
  idle,
  syncing,
  pending,
  error,
  offline,
}

// =============================================================================
// Extension for showing conflict dialog - إضافة لعرض حوار التعارض
// =============================================================================

extension SyncConflictDialogExtension on BuildContext {
  /// Show sync conflict dialog
  /// عرض حوار تعارض المزامنة
  Future<SyncResolution?> showSyncConflictDialog(SyncConflict conflict) async {
    return showDialog<SyncResolution>(
      context: this,
      barrierDismissible: false,
      builder: (context) => SyncConflictDialog(
        conflict: conflict,
        onKeepLocal: () => Navigator.of(context).pop(SyncResolution.keepLocal),
        onKeepRemote: () =>
            Navigator.of(context).pop(SyncResolution.keepRemote),
        onMerge: () => Navigator.of(context).pop(SyncResolution.merge),
      ),
    );
  }
}

enum SyncResolution { keepLocal, keepRemote, merge }
