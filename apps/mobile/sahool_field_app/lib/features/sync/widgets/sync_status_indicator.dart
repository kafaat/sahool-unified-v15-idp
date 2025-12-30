import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/sync/queue_manager.dart';
import '../providers/sync_events_provider.dart';

/// Sync Status Indicator Widget
/// مؤشر حالة المزامنة مع دعم الأنماط المختلفة
class SyncStatusIndicator extends ConsumerStatefulWidget {
  final SyncIndicatorStyle style;
  final VoidCallback? onTap;
  final bool showLastSyncTime;
  final bool showPendingCount;

  const SyncStatusIndicator({
    super.key,
    this.style = SyncIndicatorStyle.compact,
    this.onTap,
    this.showLastSyncTime = true,
    this.showPendingCount = true,
  });

  @override
  ConsumerState<SyncStatusIndicator> createState() => _SyncStatusIndicatorState();
}

class _SyncStatusIndicatorState extends ConsumerState<SyncStatusIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );
    _rotationAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.linear),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final syncStatus = ref.watch(syncStatusProvider);
    final conflictsCount = ref.watch(unreadConflictsCountProvider);

    // Animate when syncing
    if (syncStatus.isSyncing && !_animationController.isAnimating) {
      _animationController.repeat();
    } else if (!syncStatus.isSyncing && _animationController.isAnimating) {
      _animationController.stop();
      _animationController.reset();
    }

    switch (widget.style) {
      case SyncIndicatorStyle.compact:
        return _buildCompact(syncStatus, conflictsCount);
      case SyncIndicatorStyle.expanded:
        return _buildExpanded(syncStatus, conflictsCount);
      case SyncIndicatorStyle.minimal:
        return _buildMinimal(syncStatus, conflictsCount);
      case SyncIndicatorStyle.detailed:
        return _buildDetailed(syncStatus, conflictsCount);
    }
  }

  /// Compact style - small pill-shaped indicator
  Widget _buildCompact(SyncStatusState status, int conflictsCount) {
    final displayStatus = _getDisplayStatus(status, conflictsCount);

    return GestureDetector(
      onTap: widget.onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: displayStatus.backgroundColor,
          borderRadius: BorderRadius.circular(20),
          boxShadow: SahoolShadows.small,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildAnimatedIcon(displayStatus),
            const SizedBox(width: 6),
            Text(
              displayStatus.label,
              style: TextStyle(
                color: displayStatus.color,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            if (widget.showPendingCount && status.pendingCount > 0) ...[
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: displayStatus.color,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  '${status.pendingCount}',
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

  /// Expanded style - larger card with more details
  Widget _buildExpanded(SyncStatusState status, int conflictsCount) {
    final displayStatus = _getDisplayStatus(status, conflictsCount);

    return GestureDetector(
      onTap: widget.onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: SahoolRadius.mediumRadius,
          boxShadow: SahoolShadows.small,
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: displayStatus.backgroundColor,
                borderRadius: SahoolRadius.smallRadius,
              ),
              child: _buildAnimatedIcon(displayStatus, size: 24),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    displayStatus.label,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  if (widget.showLastSyncTime) ...[
                    const SizedBox(height: 4),
                    Text(
                      _getLastSyncText(status.lastSyncTime),
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ],
              ),
            ),
            if (widget.showPendingCount && status.pendingCount > 0)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: displayStatus.color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${status.pendingCount}',
                  style: TextStyle(
                    color: displayStatus.color,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  /// Minimal style - just an icon
  Widget _buildMinimal(SyncStatusState status, int conflictsCount) {
    final displayStatus = _getDisplayStatus(status, conflictsCount);

    return GestureDetector(
      onTap: widget.onTap,
      child: Stack(
        children: [
          _buildAnimatedIcon(displayStatus, size: 24),
          if (widget.showPendingCount &&
              (status.pendingCount > 0 || conflictsCount > 0))
            Positioned(
              right: 0,
              top: 0,
              child: Container(
                width: 14,
                height: 14,
                decoration: BoxDecoration(
                  color: conflictsCount > 0 ? SahoolColors.warning : SahoolColors.info,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                ),
                child: Center(
                  child: Text(
                    _getBadgeCount(status, conflictsCount) > 9
                        ? '9+'
                        : '${_getBadgeCount(status, conflictsCount)}',
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
      ),
    );
  }

  /// Detailed style - full information card
  Widget _buildDetailed(SyncStatusState status, int conflictsCount) {
    final displayStatus = _getDisplayStatus(status, conflictsCount);
    final queueManager = ref.watch(queueManagerProvider);
    final healthStatus = queueManager.getHealthStatus();

    return GestureDetector(
      onTap: widget.onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: SahoolRadius.largeRadius,
          boxShadow: SahoolShadows.medium,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: displayStatus.backgroundColor,
                    shape: BoxShape.circle,
                  ),
                  child: _buildAnimatedIcon(displayStatus, size: 28),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        displayStatus.label,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        healthStatus.messageAr,
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),

            if (widget.showLastSyncTime) ...[
              const SizedBox(height: 16),
              Divider(color: Colors.grey[200]),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.access_time, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 8),
                  Text(
                    _getLastSyncText(status.lastSyncTime),
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ],

            // Stats
            if (status.pendingCount > 0 ||
                status.failedCount > 0 ||
                conflictsCount > 0) ...[
              const SizedBox(height: 16),
              Divider(color: Colors.grey[200]),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildStatColumn(
                    icon: Icons.cloud_upload,
                    label: 'معلق',
                    value: status.pendingCount,
                    color: SahoolColors.info,
                  ),
                  _buildStatColumn(
                    icon: Icons.error_outline,
                    label: 'فشل',
                    value: status.failedCount,
                    color: SahoolColors.danger,
                  ),
                  _buildStatColumn(
                    icon: Icons.warning_amber_rounded,
                    label: 'تعارض',
                    value: conflictsCount,
                    color: SahoolColors.warning,
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildAnimatedIcon(DisplayStatus status, {double size = 16}) {
    final icon = Icon(
      status.icon,
      size: size,
      color: status.color,
    );

    if (status.isAnimated) {
      return RotationTransition(
        turns: _rotationAnimation,
        child: icon,
      );
    }

    return icon;
  }

  Widget _buildStatColumn({
    required IconData icon,
    required String label,
    required int value,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(icon, size: 24, color: value > 0 ? color : Colors.grey[400]),
        const SizedBox(height: 6),
        Text(
          '$value',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 18,
            color: value > 0 ? color : Colors.grey[400],
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  DisplayStatus _getDisplayStatus(SyncStatusState status, int conflictsCount) {
    if (status.isSyncing) {
      return DisplayStatus(
        icon: Icons.sync,
        label: 'جاري المزامنة...',
        color: SahoolColors.info,
        backgroundColor: SahoolColors.info.withOpacity(0.1),
        isAnimated: true,
      );
    }

    if (!status.isOnline) {
      return DisplayStatus(
        icon: Icons.cloud_off,
        label: 'غير متصل',
        color: SahoolColors.danger,
        backgroundColor: SahoolColors.danger.withOpacity(0.1),
        isAnimated: false,
      );
    }

    if (status.hasError) {
      return DisplayStatus(
        icon: Icons.error_outline,
        label: 'خطأ في المزامنة',
        color: SahoolColors.danger,
        backgroundColor: SahoolColors.danger.withOpacity(0.1),
        isAnimated: false,
      );
    }

    if (conflictsCount > 0) {
      return DisplayStatus(
        icon: Icons.warning_amber_rounded,
        label: 'يوجد تعارضات',
        color: SahoolColors.warning,
        backgroundColor: SahoolColors.warning.withOpacity(0.1),
        isAnimated: false,
      );
    }

    if (status.pendingCount > 0) {
      return DisplayStatus(
        icon: Icons.cloud_upload,
        label: 'في انتظار المزامنة',
        color: Colors.orange,
        backgroundColor: Colors.orange.withOpacity(0.1),
        isAnimated: false,
      );
    }

    return DisplayStatus(
      icon: Icons.cloud_done,
      label: 'متزامن',
      color: SahoolColors.success,
      backgroundColor: SahoolColors.success.withOpacity(0.1),
      isAnimated: false,
    );
  }

  String _getLastSyncText(DateTime? lastSync) {
    if (lastSync == null) return 'لم يتم المزامنة بعد';

    final diff = DateTime.now().difference(lastSync);
    if (diff.inSeconds < 30) return 'الآن';
    if (diff.inMinutes < 1) return 'منذ لحظات';
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    if (diff.inDays == 1) return 'منذ يوم';
    if (diff.inDays < 7) return 'منذ ${diff.inDays} أيام';

    return 'في ${DateFormat('dd/MM/yyyy', 'ar').format(lastSync)}';
  }

  int _getBadgeCount(SyncStatusState status, int conflictsCount) {
    return conflictsCount > 0 ? conflictsCount : status.pendingCount;
  }
}

/// Sync Indicator Style
enum SyncIndicatorStyle {
  compact, // Small pill-shaped
  expanded, // Medium card
  minimal, // Just icon
  detailed, // Full details card
}

/// Display Status Model
class DisplayStatus {
  final IconData icon;
  final String label;
  final Color color;
  final Color backgroundColor;
  final bool isAnimated;

  const DisplayStatus({
    required this.icon,
    required this.label,
    required this.color,
    required this.backgroundColor,
    this.isAnimated = false,
  });
}
