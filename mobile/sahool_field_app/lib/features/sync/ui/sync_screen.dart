import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/map/offline_map_manager.dart';
import '../../../core/map/widgets/map_download_dialog.dart';

/// Sync Center Screen - مركز المزامنة
/// إدارة البيانات المحلية والمزامنة مع السيرفر
class SyncScreen extends StatefulWidget {
  const SyncScreen({super.key});

  @override
  State<SyncScreen> createState() => _SyncScreenState();
}

class _SyncScreenState extends State<SyncScreen> {
  bool _isOnline = false;
  bool _isSyncing = false;
  double _syncProgress = 0;

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

  final List<_PendingItem> _pendingItems = [
    _PendingItem(type: 'task', title: 'تسميد حقل القمح', time: DateTime.now().subtract(const Duration(hours: 2))),
    _PendingItem(type: 'report', title: 'تقرير فحص الآفات', time: DateTime.now().subtract(const Duration(hours: 5))),
    _PendingItem(type: 'photo', title: '3 صور ميدانية', time: DateTime.now().subtract(const Duration(days: 1))),
    _PendingItem(type: 'reading', title: 'قراءات رطوبة التربة', time: DateTime.now().subtract(const Duration(days: 1))),
    _PendingItem(type: 'task', title: 'إكمال مهمة الري', time: DateTime.now().subtract(const Duration(days: 2))),
  ];

  void _startSync() async {
    if (!_isOnline) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('لا يوجد اتصال بالإنترنت'),
          backgroundColor: SahoolColors.danger,
        ),
      );
      return;
    }

    setState(() {
      _isSyncing = true;
      _syncProgress = 0;
    });

    // Simulate sync
    for (var i = 0; i < 100; i++) {
      await Future.delayed(const Duration(milliseconds: 50));
      if (mounted) {
        setState(() => _syncProgress = (i + 1) / 100);
      }
    }

    if (mounted) {
      setState(() {
        _isSyncing = false;
        _pendingItems.clear();
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('تمت المزامنة بنجاح'),
          backgroundColor: SahoolColors.success,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        title: const Text('مركز المزامنة'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Connection status
          _buildConnectionCard(),

          const SizedBox(height: 20),

          // Sync status
          _buildSyncStatusCard(),

          const SizedBox(height: 20),

          // Pending items
          _buildPendingSection(),

          const SizedBox(height: 20),

          // Offline data management
          _buildOfflineDataSection(),
        ],
      ),
    );
  }

  Widget _buildConnectionCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: _isOnline
            ? SahoolColors.primaryGradient
            : LinearGradient(
                colors: [Colors.grey[600]!, Colors.grey[700]!],
              ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: SahoolShadows.medium,
      ),
      child: Column(
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  _isOnline ? Icons.wifi : Icons.wifi_off,
                  color: Colors.white,
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _isOnline ? 'متصل بالإنترنت' : 'غير متصل',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      _isOnline
                          ? 'جميع البيانات محدثة'
                          : 'البيانات محفوظة محلياً',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.8),
                      ),
                    ),
                  ],
                ),
              ),
              Switch(
                value: _isOnline,
                onChanged: (value) => setState(() => _isOnline = value),
                activeColor: Colors.white,
                activeTrackColor: Colors.white.withOpacity(0.3),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSyncStatusCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: SahoolShadows.small,
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.sync,
                    color: _isSyncing ? SahoolColors.warning : SahoolColors.primary,
                  ),
                  const SizedBox(width: 12),
                  Text(
                    _isSyncing ? 'جارٍ المزامنة...' : 'حالة المزامنة',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
              if (!_isSyncing)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _pendingItems.isEmpty
                        ? SahoolColors.success.withOpacity(0.1)
                        : SahoolColors.warning.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    _pendingItems.isEmpty ? 'محدث' : '${_pendingItems.length} معلق',
                    style: TextStyle(
                      color: _pendingItems.isEmpty ? SahoolColors.success : SahoolColors.warning,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
            ],
          ),
          if (_isSyncing) ...[
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: _syncProgress,
                backgroundColor: Colors.grey[200],
                valueColor: const AlwaysStoppedAnimation(SahoolColors.primary),
                minHeight: 8,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '${(_syncProgress * 100).toInt()}%',
              style: TextStyle(
                color: Colors.grey[600],
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _isSyncing ? null : _startSync,
              icon: Icon(_isSyncing ? Icons.hourglass_empty : Icons.sync),
              label: Text(_isSyncing ? 'جارٍ المزامنة' : 'مزامنة الآن'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPendingSection() {
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
            if (_pendingItems.isNotEmpty)
              TextButton(
                onPressed: () {},
                child: const Text('مسح الكل'),
              ),
          ],
        ),
        const SizedBox(height: 12),
        if (_pendingItems.isEmpty)
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
                ],
              ),
            ),
          )
        else
          ...List.generate(_pendingItems.length, (index) {
            final item = _pendingItems[index];
            return _buildPendingItem(item, index);
          }),
      ],
    );
  }

  Widget _buildPendingItem(_PendingItem item, int index) {
    IconData icon;
    Color color;

    switch (item.type) {
      case 'task':
        icon = Icons.task_alt;
        color = SahoolColors.info;
        break;
      case 'report':
        icon = Icons.description;
        color = SahoolColors.warning;
        break;
      case 'photo':
        icon = Icons.photo_camera;
        color = SahoolColors.primary;
        break;
      default:
        icon = Icons.sensors;
        color = SahoolColors.secondary;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
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
                  item.title,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 4),
                Text(
                  _formatTime(item.time),
                  style: TextStyle(color: Colors.grey[500], fontSize: 12),
                ),
              ],
            ),
          ),
          Icon(Icons.cloud_upload, color: Colors.grey[400], size: 20),
        ],
      ),
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

  void _showMapDownloadDialog() async {
    await showMapDownloadDialog(context);
    // Refresh cache size after download
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

  String _formatTime(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inDays} يوم';
  }
}

class _PendingItem {
  final String type;
  final String title;
  final DateTime time;

  _PendingItem({
    required this.type,
    required this.title,
    required this.time,
  });
}
