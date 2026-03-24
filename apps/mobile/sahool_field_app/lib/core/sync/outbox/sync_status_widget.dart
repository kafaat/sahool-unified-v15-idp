import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'sync_status_provider.dart';
import 'outbox_processor.dart';

/// SAHOOL Sync Status Widget
/// ويدجت حالة المزامنة
///
/// Displays sync status with visual indicators.
/// Shows:
/// - Sync state icon and color
/// - Pending/failed counts
/// - Progress indicator when syncing
/// - Arabic/English labels

class SyncStatusWidget extends ConsumerWidget {
  final bool showLabel;
  final bool showCount;
  final bool compact;
  final VoidCallback? onTap;

  const SyncStatusWidget({
    super.key,
    this.showLabel = true,
    this.showCount = true,
    this.compact = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statusInfo = ref.watch(syncStatusProvider);
    final isRtl = Directionality.of(context) == TextDirection.rtl;

    return GestureDetector(
      onTap: onTap,
      child: compact
          ? _buildCompact(context, statusInfo, isRtl)
          : _buildExpanded(context, statusInfo, isRtl),
    );
  }

  Widget _buildCompact(
    BuildContext context,
    SyncStatusInfo statusInfo,
    bool isRtl,
  ) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: _getBackgroundColor(statusInfo.status).withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildIcon(statusInfo),
          if (showCount && statusInfo.totalPending > 0) ...[
            const SizedBox(width: 4),
            _buildBadge(statusInfo.totalPending),
          ],
        ],
      ),
    );
  }

  Widget _buildExpanded(
    BuildContext context,
    SyncStatusInfo statusInfo,
    bool isRtl,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: _getBackgroundColor(statusInfo.status).withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _getBackgroundColor(statusInfo.status).withValues(alpha: 0.3),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildIcon(statusInfo),
          if (showLabel) ...[
            const SizedBox(width: 8),
            Text(
              isRtl ? statusInfo.message : statusInfo.messageEn,
              style: TextStyle(
                color: _getTextColor(statusInfo.status),
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
          if (showCount && statusInfo.totalPending > 0) ...[
            const SizedBox(width: 8),
            _buildBadge(statusInfo.totalPending),
          ],
        ],
      ),
    );
  }

  Widget _buildIcon(SyncStatusInfo statusInfo) {
    final color = _getIconColor(statusInfo.status);

    switch (statusInfo.status) {
      case SyncStatus.syncing:
        return SizedBox(
          width: 20,
          height: 20,
          child: CircularProgressIndicator(
            strokeWidth: 2,
            valueColor: AlwaysStoppedAnimation(color),
          ),
        );

      case SyncStatus.synced:
        return Icon(Icons.cloud_done, color: color, size: 20);

      case SyncStatus.pending:
        return Icon(Icons.cloud_upload, color: color, size: 20);

      case SyncStatus.error:
        return Icon(Icons.cloud_off, color: color, size: 20);

      case SyncStatus.offline:
        return Icon(Icons.signal_wifi_off, color: color, size: 20);
    }
  }

  Widget _buildBadge(int count) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.orange,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(
        count > 99 ? '99+' : count.toString(),
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Color _getIconColor(SyncStatus status) {
    switch (status) {
      case SyncStatus.synced:
        return Colors.green;
      case SyncStatus.syncing:
        return Colors.blue;
      case SyncStatus.pending:
        return Colors.orange;
      case SyncStatus.error:
        return Colors.red;
      case SyncStatus.offline:
        return Colors.grey;
    }
  }

  Color _getBackgroundColor(SyncStatus status) {
    return _getIconColor(status);
  }

  Color _getTextColor(SyncStatus status) {
    switch (status) {
      case SyncStatus.synced:
        return Colors.green.shade700;
      case SyncStatus.syncing:
        return Colors.blue.shade700;
      case SyncStatus.pending:
        return Colors.orange.shade700;
      case SyncStatus.error:
        return Colors.red.shade700;
      case SyncStatus.offline:
        return Colors.grey.shade700;
    }
  }
}

/// Sync status indicator for app bar
class SyncStatusIndicator extends ConsumerWidget {
  const SyncStatusIndicator({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statusInfo = ref.watch(syncStatusProvider);

    return IconButton(
      icon: _buildIcon(statusInfo),
      tooltip: statusInfo.messageEn,
      onPressed: () => _showSyncDialog(context, ref),
    );
  }

  Widget _buildIcon(SyncStatusInfo statusInfo) {
    final color = _getColor(statusInfo.status);

    if (statusInfo.status == SyncStatus.syncing) {
      return SizedBox(
        width: 24,
        height: 24,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation(color),
        ),
      );
    }

    return Stack(
      children: [
        Icon(_getIconData(statusInfo.status), color: color),
        if (statusInfo.totalPending > 0)
          Positioned(
            right: 0,
            top: 0,
            child: Container(
              width: 8,
              height: 8,
              decoration: const BoxDecoration(
                color: Colors.orange,
                shape: BoxShape.circle,
              ),
            ),
          ),
      ],
    );
  }

  IconData _getIconData(SyncStatus status) {
    switch (status) {
      case SyncStatus.synced:
        return Icons.cloud_done;
      case SyncStatus.syncing:
        return Icons.sync;
      case SyncStatus.pending:
        return Icons.cloud_upload;
      case SyncStatus.error:
        return Icons.cloud_off;
      case SyncStatus.offline:
        return Icons.signal_wifi_off;
    }
  }

  Color _getColor(SyncStatus status) {
    switch (status) {
      case SyncStatus.synced:
        return Colors.green;
      case SyncStatus.syncing:
        return Colors.blue;
      case SyncStatus.pending:
        return Colors.orange;
      case SyncStatus.error:
        return Colors.red;
      case SyncStatus.offline:
        return Colors.grey;
    }
  }

  void _showSyncDialog(BuildContext context, WidgetRef ref) {
    showModalBottomSheet<void>(
      context: context,
      builder: (context) => const SyncStatusSheet(),
    );
  }
}

/// Sync status bottom sheet with details
class SyncStatusSheet extends ConsumerWidget {
  const SyncStatusSheet({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statusInfo = ref.watch(syncStatusProvider);
    final stats = ref.watch(outboxStatsProvider);
    final processorState = ref.watch(processorStateProvider);
    final isRtl = Directionality.of(context) == TextDirection.rtl;

    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Icon(
                _getIconData(statusInfo.status),
                color: _getColor(statusInfo.status),
                size: 32,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isRtl ? 'حالة المزامنة' : 'Sync Status',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    Text(
                      isRtl ? statusInfo.message : statusInfo.messageEn,
                      style: TextStyle(
                        color: _getColor(statusInfo.status),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const Divider(height: 24),

          // Stats
          stats.when(
            data: (s) => Column(
              children: [
                _buildStatRow(
                  context,
                  isRtl ? 'قيد الانتظار' : 'Pending',
                  s.pendingCount.toString(),
                  Icons.schedule,
                ),
                _buildStatRow(
                  context,
                  isRtl ? 'فاشل' : 'Failed',
                  s.failedCount.toString(),
                  Icons.error_outline,
                  color: s.failedCount > 0 ? Colors.red : null,
                ),
                _buildStatRow(
                  context,
                  isRtl ? 'مكتمل اليوم' : 'Completed Today',
                  s.completedTodayCount.toString(),
                  Icons.check_circle_outline,
                ),
                if (s.lastSyncTime != null)
                  _buildStatRow(
                    context,
                    isRtl ? 'آخر مزامنة' : 'Last Sync',
                    _formatTime(s.lastSyncTime!, isRtl),
                    Icons.access_time,
                  ),
              ],
            ),
            loading: () => const Center(
              child: CircularProgressIndicator(),
            ),
            error: (e, _) => Text(
              isRtl ? 'خطأ في تحميل الإحصائيات' : 'Error loading stats',
            ),
          ),

          const Divider(height: 24),

          // Actions
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              // Force sync button
              ElevatedButton.icon(
                onPressed: processorState == ProcessorState.processing
                    ? null
                    : () async {
                        await ref.read(
                          forceSyncProvider(null).future,
                        );
                      },
                icon: const Icon(Icons.sync),
                label: Text(isRtl ? 'مزامنة الآن' : 'Sync Now'),
              ),

              // Retry failed button
              if (statusInfo.failedCount > 0)
                OutlinedButton.icon(
                  onPressed: () async {
                    await ref.read(retryFailedProvider(null).future);
                  },
                  icon: const Icon(Icons.refresh),
                  label: Text(isRtl ? 'إعادة المحاولة' : 'Retry Failed'),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatRow(
    BuildContext context,
    String label,
    String value,
    IconData icon, {
    Color? color,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 20, color: color ?? Colors.grey),
          const SizedBox(width: 8),
          Expanded(child: Text(label)),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime time, bool isRtl) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inMinutes < 1) {
      return isRtl ? 'الآن' : 'Just now';
    } else if (diff.inMinutes < 60) {
      final m = diff.inMinutes;
      return isRtl ? 'منذ $m دقيقة' : '$m minutes ago';
    } else if (diff.inHours < 24) {
      final h = diff.inHours;
      return isRtl ? 'منذ $h ساعة' : '$h hours ago';
    } else {
      final d = diff.inDays;
      return isRtl ? 'منذ $d يوم' : '$d days ago';
    }
  }

  IconData _getIconData(SyncStatus status) {
    switch (status) {
      case SyncStatus.synced:
        return Icons.cloud_done;
      case SyncStatus.syncing:
        return Icons.sync;
      case SyncStatus.pending:
        return Icons.cloud_upload;
      case SyncStatus.error:
        return Icons.cloud_off;
      case SyncStatus.offline:
        return Icons.signal_wifi_off;
    }
  }

  Color _getColor(SyncStatus status) {
    switch (status) {
      case SyncStatus.synced:
        return Colors.green;
      case SyncStatus.syncing:
        return Colors.blue;
      case SyncStatus.pending:
        return Colors.orange;
      case SyncStatus.error:
        return Colors.red;
      case SyncStatus.offline:
        return Colors.grey;
    }
  }
}

/// Sync progress bar widget
class SyncProgressBar extends ConsumerWidget {
  const SyncProgressBar({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final progress = ref.watch(processingProgressStreamProvider);

    return progress.when(
      data: (p) => Column(
        children: [
          LinearProgressIndicator(
            value: p.percentage,
            backgroundColor: Colors.grey.shade200,
          ),
          const SizedBox(height: 4),
          Text(
            '${p.current}/${p.total}: ${p.currentEntity}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
    );
  }
}

/// Offline banner widget
class OfflineBanner extends ConsumerWidget {
  const OfflineBanner({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isOnline = ref.watch(isOnlineProvider);
    final isRtl = Directionality.of(context) == TextDirection.rtl;

    if (isOnline) return const SizedBox.shrink();

    return MaterialBanner(
      backgroundColor: Colors.orange.shade100,
      leading: const Icon(Icons.wifi_off, color: Colors.orange),
      content: Text(
        isRtl
            ? 'أنت غير متصل بالإنترنت. سيتم مزامنة التغييرات عند استعادة الاتصال.'
            : 'You are offline. Changes will sync when connection is restored.',
      ),
      actions: [
        TextButton(
          onPressed: () async {
            final networkStatus = ref.read(networkStatusProvider);
            await networkStatus.checkOnline();
          },
          child: Text(isRtl ? 'إعادة المحاولة' : 'Retry'),
        ),
      ],
    );
  }
}
