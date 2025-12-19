import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';
import '../map_downloader.dart';
import '../offline_map_manager.dart';

/// Map Download Dialog - نافذة تحميل الخريطة
///
/// تعرض:
/// - قائمة المناطق المتاحة
/// - تقدير الحجم
/// - شريط التقدم أثناء التحميل
class MapDownloadDialog extends StatefulWidget {
  final OfflineMapManager mapManager;

  const MapDownloadDialog({
    super.key,
    required this.mapManager,
  });

  @override
  State<MapDownloadDialog> createState() => _MapDownloadDialogState();
}

class _MapDownloadDialogState extends State<MapDownloadDialog> {
  String? _selectedRegion;
  bool _isDownloading = false;
  double _progress = 0;
  String _statusText = '';
  DownloadResult? _result;

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: SahoolColors.primary.withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.download, color: SahoolColors.primary),
                ),
                const SizedBox(width: 12),
                const Text(
                  'تحميل خريطة للعمل بدون نت',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // إذا كان هناك تحميل جاري
            if (_isDownloading) ...[
              _buildDownloadProgress(),
            ]
            // إذا انتهى التحميل
            else if (_result != null) ...[
              _buildDownloadResult(),
            ]
            // اختيار المنطقة
            else ...[
              _buildRegionSelector(),
            ],

            const SizedBox(height: 24),

            // الأزرار
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                if (!_isDownloading)
                  TextButton(
                    onPressed: () => Navigator.pop(context),
                    child: Text(_result != null ? 'إغلاق' : 'إلغاء'),
                  ),
                if (_isDownloading)
                  TextButton(
                    onPressed: _cancelDownload,
                    child: const Text('إلغاء التحميل'),
                  ),
                if (!_isDownloading && _result == null) ...[
                  const SizedBox(width: 12),
                  ElevatedButton.icon(
                    onPressed: _selectedRegion != null ? _startDownload : null,
                    icon: const Icon(Icons.download),
                    label: const Text('تحميل'),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRegionSelector() {
    final regions = OfflineMapManager.predefinedRegions;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'اختر المنطقة:',
          style: TextStyle(fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 12),
        ...regions.entries.map((entry) {
          final isSelected = _selectedRegion == entry.key;
          final bounds = entry.value;
          final estimate = widget.mapManager.estimateDownloadSize(
            bounds: bounds,
            minZoom: 10,
            maxZoom: 15,
          );

          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: InkWell(
              onTap: () => setState(() => _selectedRegion = entry.key),
              borderRadius: BorderRadius.circular(12),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: isSelected
                      ? SahoolColors.primary.withOpacity(0.1)
                      : Colors.grey[100],
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isSelected ? SahoolColors.primary : Colors.transparent,
                    width: 2,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.location_on,
                      color: isSelected ? SahoolColors.primary : Colors.grey,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            entry.key,
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: isSelected ? SahoolColors.primary : null,
                            ),
                          ),
                          Text(
                            '≈ ${estimate.toStringAsFixed(1)} MB',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ),
                    if (isSelected)
                      const Icon(Icons.check_circle, color: SahoolColors.primary),
                  ],
                ),
              ),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildDownloadProgress() {
    return Column(
      children: [
        const SizedBox(
          width: 60,
          height: 60,
          child: CircularProgressIndicator(
            strokeWidth: 4,
            valueColor: AlwaysStoppedAnimation(SahoolColors.primary),
          ),
        ),
        const SizedBox(height: 20),
        Text(
          _statusText,
          style: const TextStyle(fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 12),
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: LinearProgressIndicator(
            value: _progress,
            backgroundColor: Colors.grey[200],
            valueColor: const AlwaysStoppedAnimation(SahoolColors.primary),
            minHeight: 8,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '${(_progress * 100).toInt()}%',
          style: TextStyle(
            color: Colors.grey[600],
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  Widget _buildDownloadResult() {
    final success = _result!.successful;
    final total = _result!.totalTiles;
    final isSuccess = _result!.successRate > 0.9;

    return Column(
      children: [
        Icon(
          isSuccess ? Icons.check_circle : Icons.warning,
          size: 60,
          color: isSuccess ? SahoolColors.success : SahoolColors.warning,
        ),
        const SizedBox(height: 16),
        Text(
          isSuccess ? 'تم التحميل بنجاح!' : 'تم التحميل مع بعض الأخطاء',
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              _buildStatRow('البلاطات المحملة', '$success / $total'),
              _buildStatRow('تم تخطيها (موجودة)', '${_result!.skipped}'),
              if (_result!.failed > 0)
                _buildStatRow('فشل التحميل', '${_result!.failed}', isError: true),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStatRow(String label, String value, {bool isError = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: isError ? SahoolColors.danger : null,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _startDownload() async {
    if (_selectedRegion == null) return;

    final bounds = OfflineMapManager.predefinedRegions[_selectedRegion]!;

    setState(() {
      _isDownloading = true;
      _progress = 0;
      _statusText = 'جارٍ تحميل خريطة $_selectedRegion...';
    });

    final result = await widget.mapManager.downloadRegion(
      bounds: bounds,
      minZoom: 10,
      maxZoom: 15,
      onProgress: (progress) {
        if (mounted) {
          setState(() {
            _progress = progress;
            _statusText = 'جارٍ تحميل خريطة $_selectedRegion...';
          });
        }
      },
    );

    if (mounted) {
      setState(() {
        _isDownloading = false;
        _result = result;
      });
    }
  }

  void _cancelDownload() {
    widget.mapManager.cancelDownload();
    setState(() {
      _isDownloading = false;
      _statusText = 'تم إلغاء التحميل';
    });
  }
}

/// فتح نافذة تحميل الخريطة
Future<void> showMapDownloadDialog(BuildContext context) async {
  final mapManager = OfflineMapManager();

  await showDialog(
    context: context,
    barrierDismissible: false,
    builder: (context) => MapDownloadDialog(mapManager: mapManager),
  );
}
