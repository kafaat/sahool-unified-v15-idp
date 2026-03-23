import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/maps/offline/region_manager.dart';
import '../../../../core/maps/offline/tile_downloader.dart';
import '../../../../core/maps/offline/tile_storage.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../widgets/storage_usage_bar.dart';
import 'download_region_screen.dart';

/// Offline Regions Screen - شاشة إدارة المناطق المحملة
///
/// Features:
/// - View downloaded regions - عرض المناطق المحملة
/// - Delete regions - حذف المناطق
/// - Storage usage tracking - تتبع استخدام التخزين
/// - Download new regions - تحميل مناطق جديدة
class OfflineRegionsScreen extends ConsumerStatefulWidget {
  const OfflineRegionsScreen({super.key});

  @override
  ConsumerState<OfflineRegionsScreen> createState() =>
      _OfflineRegionsScreenState();
}

class _OfflineRegionsScreenState extends ConsumerState<OfflineRegionsScreen> {
  final RegionManager _regionManager = RegionManager();
  List<DownloadedRegion> _downloadedRegions = [];
  StorageStats? _storageStats;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final regions = await _regionManager.getDownloadedRegions();
      final stats = await _regionManager.getStorageStats();

      setState(() {
        _downloadedRegions = regions;
        _storageStats = stats;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _deleteRegion(DownloadedRegion region) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف المنطقة'),
        content: Text('هل أنت متأكد من حذف "${region.nameAr}"؟\n'
            'سيتم حذف ${region.formattedSize} من البيانات.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolColors.danger,
            ),
            child: const Text('حذف'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await _regionManager.deleteRegion(region.id);
      await _loadData();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('تم حذف "${region.nameAr}"')),
        );
      }
    }
  }

  Future<void> _clearAllData() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('مسح كل البيانات'),
        content: const Text(
          'هل أنت متأكد من حذف جميع الخرائط المحملة؟\n'
          'لن تتمكن من استخدام الخرائط بدون اتصال بالإنترنت.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolColors.danger,
            ),
            child: const Text('مسح الكل'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      // Delete all regions
      for (final region in _downloadedRegions) {
        await _regionManager.deleteRegion(region.id);
      }
      await _loadData();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم مسح جميع الخرائط المحملة')),
        );
      }
    }
  }

  void _navigateToDownload() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => DownloadRegionScreen(
          regionManager: _regionManager,
          onDownloadComplete: () => _loadData(),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('الخرائط المحملة'),
        centerTitle: true,
        actions: [
          if (_downloadedRegions.isNotEmpty)
            PopupMenuButton<String>(
              onSelected: (value) {
                if (value == 'clear_all') {
                  _clearAllData();
                }
              },
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'clear_all',
                  child: Row(
                    children: [
                      Icon(Icons.delete_forever, color: SahoolColors.danger),
                      SizedBox(width: 8),
                      Text('مسح الكل'),
                    ],
                  ),
                ),
              ],
            ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _buildErrorState()
              : _buildContent(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _navigateToDownload,
        icon: const Icon(Icons.download),
        label: const Text('تحميل منطقة'),
        backgroundColor: SahoolColors.primary,
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: SahoolColors.danger),
          const SizedBox(height: 16),
          Text(
            'حدث خطأ',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(_error ?? ''),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _loadData,
            icon: const Icon(Icons.refresh),
            label: const Text('إعادة المحاولة'),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    return RefreshIndicator(
      onRefresh: _loadData,
      child: CustomScrollView(
        slivers: [
          // Storage usage section
          if (_storageStats != null)
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: StorageUsageBar(
                  usedBytes: _storageStats!.totalSizeBytes,
                  regions: _storageStats!.regions,
                  onClearPressed: _downloadedRegions.isNotEmpty
                      ? _clearAllData
                      : null,
                ),
              ),
            ),

          // Section header
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'المناطق المحملة',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: SahoolColors.primary,
                        ),
                  ),
                  Text(
                    '${_downloadedRegions.length} منطقة',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: SahoolColors.textSecondary,
                        ),
                  ),
                ],
              ),
            ),
          ),

          // Downloaded regions list
          if (_downloadedRegions.isEmpty)
            SliverFillRemaining(
              hasScrollBody: false,
              child: _buildEmptyState(),
            )
          else
            SliverPadding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              sliver: SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, index) {
                    final region = _downloadedRegions[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: DownloadedRegionCard(
                        region: region,
                        onDelete: () => _deleteRegion(region),
                      ),
                    );
                  },
                  childCount: _downloadedRegions.length,
                ),
              ),
            ),

          // Recommended regions section
          if (_downloadedRegions.length < 3)
            SliverToBoxAdapter(
              child: _buildRecommendedSection(),
            ),

          // Bottom padding for FAB
          const SliverPadding(padding: EdgeInsets.only(bottom: 80)),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: SahoolColors.primary.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.map_outlined,
              size: 64,
              color: SahoolColors.primary,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'لا توجد خرائط محملة',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          Text(
            'قم بتحميل خرائط المناطق لاستخدامها\nأثناء العمل بدون اتصال بالإنترنت',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: SahoolColors.textSecondary,
                ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _navigateToDownload,
            icon: const Icon(Icons.download),
            label: const Text('تحميل منطقة جديدة'),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendedSection() {
    final downloadedIds = _downloadedRegions.map((r) => r.id).toSet();
    final recommended = YemenRegions.recommended
        .where((r) => !downloadedIds.contains(r.id))
        .take(3)
        .toList();

    if (recommended.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Divider(),
          const SizedBox(height: 8),
          Text(
            'مناطق مُوصى بتحميلها',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: SahoolColors.primary,
                ),
          ),
          const SizedBox(height: 12),
          ...recommended.map((region) {
            final estimate = _regionManager.getDownloadEstimate(region: region);
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: RecommendedRegionCard(
                region: region,
                estimate: estimate,
                onDownload: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => DownloadRegionScreen(
                        regionManager: _regionManager,
                        preselectedRegion: region,
                        onDownloadComplete: () => _loadData(),
                      ),
                    ),
                  );
                },
              ),
            );
          }),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _regionManager.dispose();
    super.dispose();
  }
}

/// Downloaded Region Card - بطاقة المنطقة المحملة
class DownloadedRegionCard extends StatelessWidget {
  final DownloadedRegion region;
  final VoidCallback onDelete;

  const DownloadedRegionCard({
    super.key,
    required this.region,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final categoryIcon = _getCategoryIcon(region.bounds);

    return DecoratedBox(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: SahoolShadows.small,
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            // Icon
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: SahoolColors.primary.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                categoryIcon,
                color: SahoolColors.primary,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),

            // Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    region.nameAr,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    region.nameEn,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      _buildChip(
                        Icons.storage,
                        region.formattedSize,
                      ),
                      const SizedBox(width: 8),
                      _buildChip(
                        Icons.grid_view,
                        '${region.tileCount} بلاطة',
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      _buildChip(
                        Icons.zoom_in,
                        'تكبير ${region.minZoom}-${region.maxZoom}',
                      ),
                      const SizedBox(width: 8),
                      _buildStatusChip(region.status),
                    ],
                  ),
                ],
              ),
            ),

            // Delete button
            IconButton(
              onPressed: onDelete,
              icon: const Icon(Icons.delete_outline),
              color: SahoolColors.danger,
              tooltip: 'حذف',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChip(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Colors.grey[600]),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusChip(DownloadStatus status) {
    final (color, text) = switch (status) {
      DownloadStatus.completed => (SahoolColors.success, 'مكتمل'),
      DownloadStatus.downloading => (SahoolColors.info, 'جارٍ التحميل'),
      DownloadStatus.paused => (SahoolColors.warning, 'متوقف'),
      DownloadStatus.failed => (SahoolColors.danger, 'فشل'),
      DownloadStatus.pending => (Colors.grey, 'في الانتظار'),
    };

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            text,
            style: TextStyle(
              fontSize: 11,
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getCategoryIcon(dynamic bounds) {
    // Simple heuristic based on location
    return Icons.map;
  }
}

/// Recommended Region Card - بطاقة المنطقة المُوصى بها
class RecommendedRegionCard extends StatelessWidget {
  final MapRegion region;
  final DownloadEstimate estimate;
  final VoidCallback onDownload;

  const RecommendedRegionCard({
    super.key,
    required this.region,
    required this.estimate,
    required this.onDownload,
  });

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: SahoolColors.secondary.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            _getCategoryIcon(region.category),
            color: SahoolColors.secondary,
          ),
        ),
        title: Text(
          region.nameAr,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text(
          '≈ ${estimate.formattedSize}',
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        trailing: OutlinedButton.icon(
          onPressed: onDownload,
          icon: const Icon(Icons.download, size: 18),
          label: const Text('تحميل'),
          style: OutlinedButton.styleFrom(
            foregroundColor: SahoolColors.primary,
            side: const BorderSide(color: SahoolColors.primary),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          ),
        ),
      ),
    );
  }

  IconData _getCategoryIcon(RegionCategory category) {
    return switch (category) {
      RegionCategory.highland => Icons.terrain,
      RegionCategory.coastal => Icons.waves,
      RegionCategory.desert => Icons.wb_sunny,
      RegionCategory.island => Icons.beach_access,
      RegionCategory.custom => Icons.location_on,
    };
  }
}
