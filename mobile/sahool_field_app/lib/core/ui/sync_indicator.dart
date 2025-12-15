import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../features/sync/providers/sync_events_provider.dart';
import '../sync/queue_manager.dart';

/// Sync Indicator Widget
/// مؤشر حالة المزامنة للـ Home Cockpit
///
/// يعرض حالة الاتصال والمزامنة بشكل بصري واضح
class SyncIndicator extends StatelessWidget {
  final bool isOnline;
  final int pendingCount;
  final bool isSyncing;
  final int conflictsCount;
  final VoidCallback? onTap;

  const SyncIndicator({
    super.key,
    required this.isOnline,
    this.pendingCount = 0,
    this.isSyncing = false,
    this.conflictsCount = 0,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: _backgroundColor,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: _iconColor.withOpacity(0.3),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Sync icon with animation
            if (isSyncing)
              SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation(_iconColor),
                ),
              )
            else
              Icon(
                _icon,
                size: 16,
                color: _iconColor,
              ),
            const SizedBox(width: 6),
            // Status text
            Text(
              _statusText,
              style: TextStyle(
                color: _iconColor,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            // Pending badge
            if (pendingCount > 0 && !isSyncing) ...[
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.orange,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  '$pendingCount',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color get _backgroundColor {
    if (isSyncing) return Colors.blue.withOpacity(0.15);
    if (!isOnline) return Colors.red.withOpacity(0.15);
    if (conflictsCount > 0) return Colors.amber.withOpacity(0.15);
    if (pendingCount > 0) return Colors.orange.withOpacity(0.15);
    return Colors.green.withOpacity(0.15);
  }

  Color get _iconColor {
    if (isSyncing) return Colors.blue;
    if (!isOnline) return Colors.red;
    if (conflictsCount > 0) return Colors.amber[700]!;
    if (pendingCount > 0) return Colors.orange;
    return Colors.green;
  }

  IconData get _icon {
    if (!isOnline) return Icons.cloud_off;
    if (conflictsCount > 0) return Icons.warning_amber_rounded;
    if (pendingCount > 0) return Icons.cloud_upload;
    return Icons.cloud_done;
  }

  String get _statusText {
    if (isSyncing) return 'مزامنة...';
    if (!isOnline) return 'غير متصل';
    if (conflictsCount > 0) return 'تعارض';
    if (pendingCount > 0) return 'معلق';
    return 'متصل';
  }
}

/// Compact version for AppBar
class SyncIndicatorCompact extends StatelessWidget {
  final bool isOnline;
  final int pendingCount;
  final bool isSyncing;
  final int conflictsCount;

  const SyncIndicatorCompact({
    super.key,
    required this.isOnline,
    this.pendingCount = 0,
    this.isSyncing = false,
    this.conflictsCount = 0,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        if (isSyncing)
          const SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation(Colors.white),
            ),
          )
        else
          Icon(
            _icon,
            color: _iconColor,
            size: 24,
          ),
        if ((pendingCount > 0 || conflictsCount > 0) && !isSyncing)
          Positioned(
            right: 0,
            top: 0,
            child: Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: conflictsCount > 0 ? Colors.amber[700] : Colors.orange,
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  _badgeCount > 9 ? '9+' : '$_badgeCount',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 8,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }

  IconData get _icon {
    if (!isOnline) return Icons.cloud_off;
    if (conflictsCount > 0) return Icons.warning_amber_rounded;
    if (pendingCount > 0) return Icons.cloud_upload;
    return Icons.cloud_done;
  }

  Color get _iconColor {
    if (!isOnline) return Colors.red;
    if (conflictsCount > 0) return Colors.amber[700]!;
    if (pendingCount > 0) return Colors.orange;
    return Colors.green;
  }

  int get _badgeCount => conflictsCount > 0 ? conflictsCount : pendingCount;
}

/// Riverpod Connected Sync Indicator
/// يقرأ الحالة من Provider تلقائياً
class ConnectedSyncIndicator extends ConsumerWidget {
  final VoidCallback? onTap;

  const ConnectedSyncIndicator({super.key, this.onTap});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncStatus = ref.watch(syncStatusProvider);
    final conflictsCount = ref.watch(unreadConflictsCountProvider);

    return SyncIndicator(
      isOnline: syncStatus.isOnline,
      pendingCount: syncStatus.pendingCount,
      isSyncing: syncStatus.isSyncing,
      conflictsCount: conflictsCount,
      onTap: onTap,
    );
  }
}

/// Riverpod Connected Compact Sync Indicator
class ConnectedSyncIndicatorCompact extends ConsumerWidget {
  const ConnectedSyncIndicatorCompact({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncStatus = ref.watch(syncStatusProvider);
    final conflictsCount = ref.watch(unreadConflictsCountProvider);

    return SyncIndicatorCompact(
      isOnline: syncStatus.isOnline,
      pendingCount: syncStatus.pendingCount,
      isSyncing: syncStatus.isSyncing,
      conflictsCount: conflictsCount,
    );
  }
}

/// Detailed Sync Status Card
/// بطاقة تفصيلية لحالة المزامنة
class SyncStatusCard extends ConsumerWidget {
  final VoidCallback? onSyncTap;
  final VoidCallback? onConflictsTap;

  const SyncStatusCard({
    super.key,
    this.onSyncTap,
    this.onConflictsTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final syncStatus = ref.watch(syncStatusProvider);
    final queueManager = ref.watch(queueManagerProvider);
    final healthStatus = queueManager.getHealthStatus();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              _buildStatusIcon(syncStatus, healthStatus),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      healthStatus.messageAr,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      _getLastSyncText(syncStatus.lastSyncTime),
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              if (syncStatus.isSyncing)
                const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
            ],
          ),

          // Stats row
          if (syncStatus.pendingCount > 0 ||
              syncStatus.failedCount > 0 ||
              syncStatus.conflictsCount > 0) ...[
            const SizedBox(height: 16),
            const Divider(height: 1),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem(
                  icon: Icons.cloud_upload,
                  label: 'معلق',
                  value: syncStatus.pendingCount,
                  color: Colors.orange,
                ),
                _buildStatItem(
                  icon: Icons.error_outline,
                  label: 'فشل',
                  value: syncStatus.failedCount,
                  color: Colors.red,
                ),
                _buildStatItem(
                  icon: Icons.warning_amber_rounded,
                  label: 'تعارض',
                  value: syncStatus.conflictsCount,
                  color: Colors.amber[700]!,
                  onTap: syncStatus.conflictsCount > 0 ? onConflictsTap : null,
                ),
              ],
            ),
          ],

          // Actions
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: syncStatus.isSyncing ? null : onSyncTap,
                  icon: const Icon(Icons.sync, size: 18),
                  label: const Text('مزامنة الآن'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatusIcon(SyncStatusState status, QueueHealthStatus health) {
    IconData icon;
    Color color;

    switch (health) {
      case QueueHealthStatus.healthy:
        icon = Icons.check_circle;
        color = Colors.green;
        break;
      case QueueHealthStatus.busy:
        icon = Icons.sync;
        color = Colors.blue;
        break;
      case QueueHealthStatus.warning:
        icon = Icons.warning_amber_rounded;
        color = Colors.amber[700]!;
        break;
      case QueueHealthStatus.critical:
        icon = Icons.error;
        color = Colors.red;
        break;
    }

    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        shape: BoxShape.circle,
      ),
      child: Icon(icon, color: color, size: 24),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String label,
    required int value,
    required Color color,
    VoidCallback? onTap,
  }) {
    final content = Column(
      children: [
        Icon(icon, size: 20, color: value > 0 ? color : Colors.grey[400]),
        const SizedBox(height: 4),
        Text(
          '$value',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: value > 0 ? color : Colors.grey[400],
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey[600],
          ),
        ),
      ],
    );

    if (onTap != null) {
      return InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(8),
          child: content,
        ),
      );
    }

    return content;
  }

  String _getLastSyncText(DateTime? lastSync) {
    if (lastSync == null) return 'لم يتم المزامنة بعد';

    final diff = DateTime.now().difference(lastSync);
    if (diff.inMinutes < 1) return 'الآن';
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inDays} يوم';
  }
}

/// Sync Progress Overlay Widget
/// طبقة تقدم المزامنة
class SyncProgressOverlay extends StatelessWidget {
  final double progress;
  final String message;
  final VoidCallback? onCancel;

  const SyncProgressOverlay({
    super.key,
    required this.progress,
    this.message = 'جاري المزامنة...',
    this.onCancel,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Circular progress
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 80,
                height: 80,
                child: CircularProgressIndicator(
                  value: progress,
                  strokeWidth: 6,
                  backgroundColor: Colors.grey[200],
                  valueColor: const AlwaysStoppedAnimation(Colors.green),
                ),
              ),
              Text(
                '${(progress * 100).toInt()}%',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(
            message,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
          if (onCancel != null) ...[
            const SizedBox(height: 12),
            TextButton(
              onPressed: onCancel,
              child: const Text('إلغاء'),
            ),
          ],
        ],
      ),
    );
  }
}
