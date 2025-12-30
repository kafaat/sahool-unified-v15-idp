import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/storage/database.dart';
import '../../../core/sync/queue_manager.dart';
import '../../../main.dart';
import '../providers/sync_events_provider.dart';
import '../widgets/sync_status_indicator.dart';
import '../widgets/sync_status_banner.dart';

/// Sync Details Screen
/// شاشة تفاصيل المزامنة - عرض السجلات والعناصر المعلقة
class SyncDetailsScreen extends ConsumerStatefulWidget {
  const SyncDetailsScreen({super.key});

  @override
  ConsumerState<SyncDetailsScreen> createState() => _SyncDetailsScreenState();
}

class _SyncDetailsScreenState extends ConsumerState<SyncDetailsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _dateFormat = DateFormat('dd/MM/yyyy hh:mm a', 'ar');

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final syncStatus = ref.watch(syncStatusProvider);

    return Scaffold(
      backgroundColor: SahoolColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        title: const Text('تفاصيل المزامنة'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _handleManualSync,
            tooltip: 'مزامنة يدوية',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'الحالة', icon: Icon(Icons.dashboard, size: 20)),
            Tab(text: 'المعلقة', icon: Icon(Icons.pending_actions, size: 20)),
            Tab(text: 'السجل', icon: Icon(Icons.history, size: 20)),
          ],
          labelColor: SahoolColors.primary,
          unselectedLabelColor: SahoolColors.textSecondary,
          indicatorColor: SahoolColors.primary,
        ),
      ),
      body: Column(
        children: [
          // Status banner at top
          const AnimatedSyncStatusBanner(),

          // Tab views
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildStatusTab(syncStatus),
                _buildPendingItemsTab(),
                _buildHistoryTab(),
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: syncStatus.isSyncing
          ? null
          : FloatingActionButton.extended(
              onPressed: _handleManualSync,
              icon: const Icon(Icons.sync),
              label: const Text('مزامنة الآن'),
            ),
    );
  }

  /// Status Tab - Overview
  Widget _buildStatusTab(SyncStatusState status) {
    return RefreshIndicator(
      onRefresh: () async {
        await ref.read(queueManagerProvider).notifyStatsChanged();
        await ref.read(syncEventsProvider.notifier).refresh();
      },
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Main sync status indicator
          SyncStatusIndicator(
            style: SyncIndicatorStyle.detailed,
            onTap: () => _handleManualSync(),
          ),

          const SizedBox(height: 20),

          // Quick stats
          _buildQuickStats(status),

          const SizedBox(height: 20),

          // Recent events
          _buildRecentEvents(),

          const SizedBox(height: 20),

          // Actions
          _buildQuickActions(status),
        ],
      ),
    );
  }

  /// Quick statistics cards
  Widget _buildQuickStats(SyncStatusState status) {
    final queueManager = ref.watch(queueManagerProvider);
    final stats = queueManager.currentStats;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'إحصائيات سريعة',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                icon: Icons.cloud_upload,
                label: 'معلق',
                value: '${status.pendingCount}',
                color: SahoolColors.info,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                icon: Icons.check_circle,
                label: 'تم اليوم',
                value: '${stats.processedToday}',
                color: SahoolColors.success,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                icon: Icons.error_outline,
                label: 'فشل',
                value: '${status.failedCount}',
                color: SahoolColors.danger,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                icon: Icons.warning_amber_rounded,
                label: 'تعارضات',
                value: '${stats.totalConflicts}',
                color: SahoolColors.warning,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: SahoolRadius.mediumRadius,
        boxShadow: SahoolShadows.small,
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
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
      ),
    );
  }

  /// Recent events section
  Widget _buildRecentEvents() {
    final eventsState = ref.watch(syncEventsProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'الأحداث الأخيرة',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            if (eventsState.events.isNotEmpty)
              TextButton(
                onPressed: () => _tabController.animateTo(2),
                child: const Text('عرض الكل'),
              ),
          ],
        ),
        const SizedBox(height: 12),
        if (eventsState.isLoading)
          const Center(child: CircularProgressIndicator())
        else if (eventsState.events.isEmpty)
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: SahoolRadius.mediumRadius,
            ),
            child: Center(
              child: Column(
                children: [
                  Icon(Icons.check_circle, size: 48, color: SahoolColors.success),
                  const SizedBox(height: 12),
                  const Text('لا توجد أحداث جديدة'),
                  const SizedBox(height: 4),
                  Text(
                    'جميع البيانات متزامنة',
                    style: TextStyle(color: Colors.grey[600], fontSize: 12),
                  ),
                ],
              ),
            ),
          )
        else
          ...eventsState.events.take(3).map((event) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: _buildEventCard(event),
              )),
      ],
    );
  }

  Widget _buildEventCard(SyncEvent event) {
    final isConflict = event.type == 'CONFLICT';
    final icon = isConflict ? Icons.warning_amber_rounded : Icons.info_outline;
    final color = isConflict ? SahoolColors.warning : SahoolColors.info;

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: SahoolRadius.smallRadius,
        border: Border.all(
          color: color.withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  event.message,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _dateFormat.format(event.createdAt),
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Quick actions section
  Widget _buildQuickActions(SyncStatusState status) {
    final queueManager = ref.watch(queueManagerProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'إجراءات سريعة',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        if (status.failedCount > 0)
          _buildActionButton(
            icon: Icons.refresh,
            label: 'إعادة محاولة العناصر الفاشلة',
            color: SahoolColors.warning,
            onTap: () async {
              final retried = await queueManager.retryFailed();
              if (mounted) {
                FloatingSyncStatusBanner.showSuccess(
                  context,
                  message: 'تم إعادة محاولة $retried عنصر',
                );
              }
            },
          ),
        const SizedBox(height: 8),
        _buildActionButton(
          icon: Icons.delete_sweep,
          label: 'تنظيف العناصر القديمة',
          color: SahoolColors.textSecondary,
          onTap: () async {
            await queueManager.cleanup();
            if (mounted) {
              FloatingSyncStatusBanner.showSuccess(
                context,
                message: 'تم تنظيف العناصر المكتملة',
              );
            }
          },
        ),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.white,
      borderRadius: SahoolRadius.mediumRadius,
      child: InkWell(
        onTap: onTap,
        borderRadius: SahoolRadius.mediumRadius,
        child: Container(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  label,
                  style: const TextStyle(
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              Icon(Icons.chevron_right, color: Colors.grey[400]),
            ],
          ),
        ),
      ),
    );
  }

  /// Pending Items Tab
  Widget _buildPendingItemsTab() {
    return FutureBuilder<List<OutboxData>>(
      future: ref.read(queueManagerProvider).getPendingItemsSorted(limit: 100),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(
            child: Text('خطأ: ${snapshot.error}'),
          );
        }

        final items = snapshot.data ?? [];

        if (items.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.check_circle, size: 64, color: SahoolColors.success),
                const SizedBox(height: 16),
                const Text(
                  'لا توجد عناصر معلقة',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'جميع البيانات متزامنة مع السيرفر',
                  style: TextStyle(color: Colors.grey[600]),
                ),
              ],
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: items.length,
          itemBuilder: (context, index) {
            final item = items[index];
            return _buildPendingItemCard(item);
          },
        );
      },
    );
  }

  Widget _buildPendingItemCard(OutboxData item) {
    final priority = QueueManager.getPriorityForOperation(
      item.entityType,
      item.method,
    );
    final isFailed = item.retryCount > 0;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: SahoolRadius.mediumRadius,
        boxShadow: SahoolShadows.small,
        border: isFailed
            ? Border.all(color: SahoolColors.danger.withOpacity(0.3))
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _buildPriorityBadge(priority),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  _getEntityTypeLabel(item.entityType),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                  ),
                ),
              ),
              _buildMethodBadge(item.method),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.access_time, size: 14, color: Colors.grey[600]),
              const SizedBox(width: 4),
              Text(
                _dateFormat.format(item.createdAt),
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
          if (isFailed) ...[
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: SahoolColors.danger.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.error_outline, size: 14, color: SahoolColors.danger),
                  const SizedBox(width: 4),
                  Text(
                    'فشل ${item.retryCount} ${item.retryCount == 1 ? 'مرة' : 'مرات'}',
                    style: TextStyle(
                      fontSize: 12,
                      color: SahoolColors.danger,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildPriorityBadge(QueuePriority priority) {
    Color color;
    String label;

    switch (priority) {
      case QueuePriority.critical:
        color = SahoolColors.danger;
        label = 'عاجل';
        break;
      case QueuePriority.high:
        color = SahoolColors.warning;
        label = 'مرتفع';
        break;
      case QueuePriority.normal:
        color = SahoolColors.info;
        label = 'عادي';
        break;
      case QueuePriority.low:
        color = SahoolColors.textSecondary;
        label: 'منخفض';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 11,
          color: color,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildMethodBadge(String method) {
    Color color;
    IconData icon;

    switch (method.toUpperCase()) {
      case 'POST':
        color = SahoolColors.success;
        icon = Icons.add;
        break;
      case 'PUT':
        color = SahoolColors.info;
        icon = Icons.edit;
        break;
      case 'DELETE':
        color = SahoolColors.danger;
        icon = Icons.delete;
        break;
      default:
        color = SahoolColors.textSecondary;
        icon = Icons.sync;
    }

    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        shape: BoxShape.circle,
      ),
      child: Icon(icon, size: 16, color: color),
    );
  }

  /// History Tab
  Widget _buildHistoryTab() {
    return FutureBuilder<List<SyncLog>>(
      future: ref.read(databaseProvider).getRecentSyncLogs(limit: 100),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text('خطأ: ${snapshot.error}'));
        }

        final logs = snapshot.data ?? [];

        if (logs.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.history, size: 64, color: Colors.grey[400]),
                const SizedBox(height: 16),
                const Text(
                  'لا يوجد سجل',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: logs.length,
          itemBuilder: (context, index) {
            final log = logs[index];
            return _buildLogCard(log);
          },
        );
      },
    );
  }

  Widget _buildLogCard(SyncLog log) {
    final isSuccess = log.status == 'success';
    final isError = log.status == 'failed' || log.status == 'error';
    final color = isSuccess
        ? SahoolColors.success
        : isError
            ? SahoolColors.danger
            : SahoolColors.info;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: SahoolRadius.smallRadius,
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                isSuccess
                    ? Icons.check_circle
                    : isError
                        ? Icons.error
                        : Icons.info,
                size: 16,
                color: color,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  log.message,
                  style: const TextStyle(fontSize: 13),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            _dateFormat.format(log.timestamp),
            style: TextStyle(fontSize: 11, color: Colors.grey[600]),
          ),
        ],
      ),
    );
  }

  String _getEntityTypeLabel(String entityType) {
    switch (entityType) {
      case 'field':
        return 'حقل';
      case 'task':
        return 'مهمة';
      case 'biodiversity_record':
        return 'سجل التنوع البيولوجي';
      case 'soil_health_record':
        return 'سجل صحة التربة';
      case 'water_conservation_record':
        return 'سجل الحفاظ على المياه';
      case 'farm_practice_record':
        return 'سجل الممارسات الزراعية';
      default:
        return entityType;
    }
  }

  Future<void> _handleManualSync() async {
    final syncStatus = ref.read(syncStatusProvider.notifier);
    final statusState = ref.read(syncStatusProvider);

    if (!statusState.isOnline) {
      FloatingSyncStatusBanner.showOffline(context);
      return;
    }

    if (statusState.isSyncing) {
      return;
    }

    FloatingSyncStatusBanner.showSyncing(context);

    final result = await syncStatus.syncNow();

    if (mounted) {
      if (result.success) {
        FloatingSyncStatusBanner.showSuccess(
          context,
          message: 'تمت المزامنة بنجاح: ${result.uploaded} مرفوع، ${result.downloaded} محمل',
        );
      } else {
        FloatingSyncStatusBanner.showError(
          context,
          result.message ?? 'فشل في المزامنة',
          onRetry: _handleManualSync,
        );
      }
    }
  }
}
