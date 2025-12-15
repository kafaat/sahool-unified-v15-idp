import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/map/offline_map_manager.dart';
import '../../../core/map/widgets/map_download_dialog.dart';
import '../../../core/ui/sync_indicator.dart';
import '../../../core/sync/queue_manager.dart';
import '../../../core/storage/database.dart';
import '../../../main.dart';
import '../providers/sync_events_provider.dart';
import 'conflict_resolution_dialog.dart';

/// Sync Center Screen - مركز المزامنة
/// إدارة البيانات المحلية والمزامنة مع السيرفر
class SyncScreen extends ConsumerStatefulWidget {
  const SyncScreen({super.key});

  @override
  ConsumerState<SyncScreen> createState() => _SyncScreenState();
}

class _SyncScreenState extends ConsumerState<SyncScreen> {
  // Map Manager
  final _mapManager = OfflineMapManager();
  String _mapCacheSize = '...';

  @override
  void initState() {
    super.initState();
    _loadMapCacheSize();
  }

  Future<void> _loadMapCacheSize() async {
    final size = await _mapManager.getCacheSizeFormatted();
    if (mounted) {
      setState(() => _mapCacheSize = size);
    }
  }

  void _startSync() async {
    final syncStatus = ref.read(syncStatusProvider.notifier);
    final statusState = ref.read(syncStatusProvider);

    if (!statusState.isOnline) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('لا يوجد اتصال بالإنترنت'),
          backgroundColor: SahoolColors.danger,
        ),
      );
      return;
    }

    final result = await syncStatus.syncNow();

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result.success ? 'تمت المزامنة بنجاح' : 'فشل في المزامنة: ${result.message}'),
          backgroundColor: result.success ? SahoolColors.success : SahoolColors.danger,
        ),
      );
    }
  }

  void _showConflictDialog(SyncEvent conflict) async {
    final choice = await showConflictResolutionDialog(
      context: context,
      conflict: conflict,
    );

    if (choice != null && mounted) {
      final eventsNotifier = ref.read(syncEventsProvider.notifier);
      await eventsNotifier.markAsRead(conflict.id);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(_getChoiceMessage(choice)),
          backgroundColor: SahoolColors.success,
        ),
      );
    }
  }

  String _getChoiceMessage(ConflictChoice choice) {
    switch (choice) {
      case ConflictChoice.keepLocal:
        return 'تم الاحتفاظ بالنسخة المحلية';
      case ConflictChoice.acceptServer:
        return 'تم قبول نسخة السيرفر';
      case ConflictChoice.reviewManually:
        return 'يرجى مراجعة البيانات يدوياً';
    }
  }

  @override
  Widget build(BuildContext context) {
    final syncStatus = ref.watch(syncStatusProvider);
    final eventsState = ref.watch(syncEventsProvider);

    return Scaffold(
      backgroundColor: SahoolColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        title: const Text('مركز المزامنة'),
        actions: [
          if (eventsState.hasConflicts)
            Padding(
              padding: const EdgeInsets.only(left: 8),
              child: Badge(
                label: Text('${eventsState.unreadCount}'),
                child: IconButton(
                  icon: const Icon(Icons.warning_amber_rounded),
                  onPressed: () => _scrollToConflicts(),
                ),
              ),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await ref.read(syncEventsProvider.notifier).refresh();
          await ref.read(queueManagerProvider).notifyStatsChanged();
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Connection status card using SyncStatusCard
            SyncStatusCard(
              onSyncTap: _startSync,
              onConflictsTap: () => _scrollToConflicts(),
            ),

            const SizedBox(height: 20),

            // Conflicts Section (if any)
            if (eventsState.hasConflicts) ...[
              _buildConflictsSection(eventsState),
              const SizedBox(height: 20),
            ],

            // Pending items from real queue
            _buildPendingSection(),

            const SizedBox(height: 20),

            // Offline data management
            _buildOfflineDataSection(),

            const SizedBox(height: 20),

            // Background sync info
            _buildBackgroundSyncInfo(),
          ],
        ),
      ),
    );
  }

  void _scrollToConflicts() {
    // Could implement scrolling to conflicts section
  }

  Widget _buildConflictsSection(SyncEventsState eventsState) {
    final conflicts = eventsState.events.where((e) => e.type == 'CONFLICT').toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Icon(Icons.warning_amber_rounded, color: Colors.amber[700], size: 20),
                const SizedBox(width: 8),
                const Text(
                  'التعارضات',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
              ],
            ),
            if (conflicts.isNotEmpty)
              TextButton(
                onPressed: () => ref.read(syncEventsProvider.notifier).markAllAsRead(),
                child: const Text('تجاهل الكل'),
              ),
          ],
        ),
        const SizedBox(height: 12),
        ...conflicts.map((conflict) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: ConflictListItem(
                conflict: conflict,
                onTap: () => _showConflictDialog(conflict),
                onDismiss: () => ref.read(syncEventsProvider.notifier).markAsRead(conflict.id),
              ),
            )),
      ],
    );
  }

  Widget _buildPendingSection() {
    final queueManager = ref.watch(queueManagerProvider);
    final stats = queueManager.currentStats;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'العمليات المعلقة',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            if (stats.totalPending > 0)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: SahoolColors.warning.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${stats.totalPending}',
                  style: const TextStyle(
                    color: SahoolColors.warning,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: 12),
        if (stats.isEmpty)
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Center(
              child: Column(
                children: [
                  Icon(Icons.check_circle, size: 48, color: SahoolColors.success),
                  const SizedBox(height: 12),
                  const Text('لا توجد عمليات معلقة'),
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
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: SahoolShadows.small,
            ),
            child: Column(
              children: [
                _buildQueueStatRow(
                  icon: Icons.cloud_upload,
                  label: 'في انتظار الرفع',
                  value: stats.totalPending,
                  color: SahoolColors.info,
                ),
                if (stats.totalFailed > 0) ...[
                  const Divider(height: 24),
                  _buildQueueStatRow(
                    icon: Icons.error_outline,
                    label: 'فشل في المزامنة',
                    value: stats.totalFailed,
                    color: SahoolColors.danger,
                  ),
                ],
                const SizedBox(height: 16),
                Row(
                  children: [
                    if (stats.totalFailed > 0)
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            final retried = await queueManager.retryFailed();
                            if (mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('تم إعادة محاولة $retried عنصر')),
                              );
                            }
                          },
                          icon: const Icon(Icons.refresh, size: 18),
                          label: const Text('إعادة المحاولة'),
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildQueueStatRow({
    required IconData icon,
    required String label,
    required int value,
    required Color color,
  }) {
    return Row(
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
        Expanded(child: Text(label)),
        Text(
          '$value',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: color,
            fontSize: 18,
          ),
        ),
      ],
    );
  }

  Widget _buildOfflineDataSection() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: SahoolShadows.small,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.storage, color: SahoolColors.primary),
              SizedBox(width: 12),
              Text(
                'البيانات المحلية',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildStorageItem('الخرائط المحملة', _mapCacheSize, Icons.map),
          _buildStorageItem('صور الحقول', '128 MB', Icons.photo_library),
          _buildStorageItem('بيانات NDVI', '23 MB', Icons.satellite_alt),
          _buildStorageItem('قاعدة البيانات', '12 MB', Icons.table_chart),
          const Divider(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('الإجمالي'),
              Text(
                '208 MB',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: SahoolColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _showMapDownloadDialog,
                  icon: const Icon(Icons.download),
                  label: const Text('تحميل خرائط'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              OutlinedButton(
                onPressed: _showClearMapCacheDialog,
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
                  foregroundColor: SahoolColors.danger,
                  side: const BorderSide(color: SahoolColors.danger),
                ),
                child: const Icon(Icons.delete_outline),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildBackgroundSyncInfo() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: SahoolColors.info.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: SahoolColors.info.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: SahoolColors.info.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.sync, color: SahoolColors.info, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'المزامنة التلقائية مفعّلة',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  'يتم مزامنة البيانات تلقائياً في الخلفية كل 15 دقيقة',
                  style: TextStyle(color: Colors.grey[600], fontSize: 12),
                ),
              ],
            ),
          ),
          const Icon(Icons.check_circle, color: SahoolColors.success, size: 24),
        ],
      ),
    );
  }

  void _showMapDownloadDialog() async {
    await showMapDownloadDialog(context);
    _loadMapCacheSize();
  }

  void _showClearMapCacheDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.delete_outline, color: SahoolColors.danger),
            SizedBox(width: 12),
            Text('مسح كاش الخرائط'),
          ],
        ),
        content: const Text(
          'سيتم حذف جميع الخرائط المحملة. ستحتاج لتحميلها مرة أخرى للعمل بدون إنترنت.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              await _mapManager.clearCache();
              _loadMapCacheSize();
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تم مسح كاش الخرائط'),
                    backgroundColor: SahoolColors.success,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolColors.danger,
            ),
            child: const Text('مسح'),
          ),
        ],
      ),
    );
  }

  Widget _buildStorageItem(String title, String size, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: Colors.grey[600], size: 20),
          const SizedBox(width: 12),
          Expanded(child: Text(title)),
          Text(size, style: TextStyle(color: Colors.grey[600])),
        ],
      ),
    );
  }
}
