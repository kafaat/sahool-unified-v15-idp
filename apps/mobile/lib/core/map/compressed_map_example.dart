import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'compressed_tile_provider.dart';
import '../utils/image_compression.dart';
import '../services/tile_service.dart';
import '../utils/app_logger.dart';

/// شاشة مثال للخريطة مع ضغط البلاطات
/// Example screen for map with tile compression
///
/// توضح كيفية استخدام النظام الجديد لضغط البلاطات
/// Demonstrates how to use the new tile compression system
class CompressedMapExample extends StatefulWidget {
  const CompressedMapExample({super.key});

  @override
  State<CompressedMapExample> createState() => _CompressedMapExampleState();
}

class _CompressedMapExampleState extends State<CompressedMapExample> {
  late CompressedTileProvider _tileProvider;
  late CompressedTileManager _tileManager;
  late MapController _mapController;

  // إحصائيات - Statistics
  CacheSizeInfo? _cacheInfo;
  PrefetchResult? _lastPrefetch;
  bool _isPrefetching = false;
  double _prefetchProgress = 0.0;

  // إعدادات - Settings
  double _quality = ImageCompressionUtil.mobileQuality;
  ImageFormat _detectedFormat = ImageFormat.jpeg;

  // مواقع مهمة في اليمن - Important locations in Yemen
  static const LatLng sanaa = LatLng(15.3694, 44.1910);
  static const LatLng aden = LatLng(12.7855, 45.0187);
  static const LatLng taiz = LatLng(13.5779, 44.0224);
  static const LatLng hodeidah = LatLng(14.7979, 42.9545);

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _initializeTileProvider();
    _detectImageFormat();
  }

  /// تهيئة مزود البلاطات - Initialize tile provider
  void _initializeTileProvider() {
    // استخدم رابط خادم البلاطات الخاص بك
    // Use your tile server URL
    const baseUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

    _tileProvider = CompressedTileProvider(
      baseUrl: baseUrl,
      quality: _quality,
      enableResize: true,
    );

    _tileManager = CompressedTileManager(_tileProvider);

    _loadCacheInfo();
  }

  /// كشف صيغة الصورة المدعومة - Detect supported image format
  Future<void> _detectImageFormat() async {
    final format = await ImageCompressionUtil.getOptimalFormat();
    setState(() {
      _detectedFormat = format;
    });
    AppLogger.i('Detected format: ${format.name}', tag: 'COMPRESSED_MAP');
  }

  /// تحميل معلومات الكاش - Load cache info
  Future<void> _loadCacheInfo() async {
    final info = await _tileManager.getCacheInfo();
    setState(() {
      _cacheInfo = info;
    });
  }

  /// تحميل مسبق للمنطقة الحالية - Prefetch current area
  Future<void> _prefetchCurrentArea() async {
    setState(() {
      _isPrefetching = true;
      _prefetchProgress = 0.0;
    });

    try {
      // احصل على حدود الشاشة الحالية - Get current screen bounds
      final bounds = _mapController.camera.visibleBounds;
      final currentZoom = _mapController.camera.zoom.round();

      // حمّل المستويات الحالية والمجاورة - Load current and nearby zoom levels
      final zoomLevels = [
        if (currentZoom > 0) currentZoom - 1,
        currentZoom,
        if (currentZoom < 18) currentZoom + 1,
      ];

      AppLogger.i(
        'Starting prefetch for zoom levels: $zoomLevels',
        tag: 'COMPRESSED_MAP',
      );

      final result = await _tileManager.prefetchArea(
        bounds: bounds,
        zoomLevels: zoomLevels,
        onProgress: (completed, total) {
          setState(() {
            _prefetchProgress = completed / total;
          });
        },
      );

      setState(() {
        _lastPrefetch = result;
        _isPrefetching = false;
      });

      await _loadCacheInfo();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'تم تحميل ${result.successfulTiles} بلاطة في ${result.duration.inSeconds}ث\n'
              'Downloaded ${result.successfulTiles} tiles in ${result.duration.inSeconds}s',
            ),
          ),
        );
      }
    } catch (e) {
      AppLogger.e('Prefetch failed', tag: 'COMPRESSED_MAP', error: e);
      setState(() {
        _isPrefetching = false;
      });
    }
  }

  /// تحميل مسبق حول موقع محدد - Prefetch around a location
  Future<void> _prefetchAroundLocation(LatLng location, String name) async {
    setState(() {
      _isPrefetching = true;
      _prefetchProgress = 0.0;
    });

    try {
      // تحريك الخريطة للموقع - Move map to location
      _mapController.move(location, 12);

      // انتظار قليلاً لتحديث الخريطة - Wait for map to update
      await Future.delayed(const Duration(milliseconds: 500));

      final result = await _tileManager.prefetchAroundLocation(
        center: location,
        radiusKm: 10.0, // 10 كم حول الموقع - 10 km around location
        zoomLevels: [10, 11, 12],
        onProgress: (completed, total) {
          setState(() {
            _prefetchProgress = completed / total;
          });
        },
      );

      setState(() {
        _lastPrefetch = result;
        _isPrefetching = false;
      });

      await _loadCacheInfo();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'تم تحميل $name: ${result.successfulTiles} بلاطة\n'
              'Downloaded $name: ${result.successfulTiles} tiles',
            ),
          ),
        );
      }
    } catch (e) {
      AppLogger.e('Prefetch failed for $name', tag: 'COMPRESSED_MAP', error: e);
      setState(() {
        _isPrefetching = false;
      });
    }
  }

  /// مسح الكاش - Clear cache
  Future<void> _clearCache() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('مسح الكاش - Clear Cache'),
        content: const Text(
          'هل أنت متأكد من مسح جميع البلاطات المحفوظة؟\n'
          'Are you sure you want to clear all cached tiles?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('إلغاء - Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('مسح - Clear'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await _tileManager.clearCache();
      await _loadCacheInfo();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تم مسح الكاش - Cache cleared')),
        );
      }
    }
  }

  /// تغيير جودة الضغط - Change compression quality
  void _changeQuality(double quality) {
    setState(() {
      _quality = quality;
      _initializeTileProvider();
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'الجودة: ${(quality * 100).toInt()}% - Quality: ${(quality * 100).toInt()}%',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('خريطة مضغوطة - Compressed Map'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: _showSettings,
          ),
        ],
      ),
      body: Stack(
        children: [
          // الخريطة - Map
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: sanaa,
              initialZoom: 12.0,
              minZoom: 5.0,
              maxZoom: 18.0,
            ),
            children: [
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                tileProvider: _tileProvider,
                userAgentPackageName: 'com.sahool.field_app',
              ),
            ],
          ),

          // معلومات الحالة - Status info
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: _buildStatusCard(),
          ),

          // شريط التحميل المسبق - Prefetch progress bar
          if (_isPrefetching)
            Positioned(
              bottom: 80,
              left: 16,
              right: 16,
              child: _buildPrefetchProgress(),
            ),
        ],
      ),
      bottomNavigationBar: _buildBottomBar(),
      floatingActionButton: _buildFAB(),
    );
  }

  /// بطاقة معلومات الحالة - Status info card
  Widget _buildStatusCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(
                  _detectedFormat == ImageFormat.webp
                      ? Icons.check_circle
                      : Icons.info,
                  color: _detectedFormat == ImageFormat.webp
                      ? Colors.green
                      : Colors.orange,
                  size: 16,
                ),
                const SizedBox(width: 8),
                Text(
                  'الصيغة - Format: ${_detectedFormat.name.toUpperCase()}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (_cacheInfo != null) ...[
              Text('الكاش - Cache: ${_cacheInfo!.sizeFormatted}'),
              Text('الملفات - Files: ${_cacheInfo!.fileCount}'),
            ],
            if (_lastPrefetch != null) ...[
              const Divider(),
              Text(
                'آخر تحميل - Last prefetch: ${_lastPrefetch!.successfulTiles} tiles',
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// شريط تقدم التحميل المسبق - Prefetch progress bar
  Widget _buildPrefetchProgress() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('جاري التحميل - Prefetching...'),
            const SizedBox(height: 8),
            LinearProgressIndicator(value: _prefetchProgress),
            const SizedBox(height: 8),
            Text('${(_prefetchProgress * 100).toStringAsFixed(0)}%'),
          ],
        ),
      ),
    );
  }

  /// الشريط السفلي - Bottom bar
  Widget _buildBottomBar() {
    return BottomAppBar(
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _LocationButton(
            icon: Icons.location_city,
            label: 'صنعاء',
            onPressed: () => _mapController.move(sanaa, 12),
          ),
          _LocationButton(
            icon: Icons.location_city,
            label: 'عدن',
            onPressed: () => _mapController.move(aden, 12),
          ),
          _LocationButton(
            icon: Icons.location_city,
            label: 'تعز',
            onPressed: () => _mapController.move(taiz, 12),
          ),
          _LocationButton(
            icon: Icons.location_city,
            label: 'الحديدة',
            onPressed: () => _mapController.move(hodeidah, 12),
          ),
        ],
      ),
    );
  }

  /// زر عائم - Floating action button
  Widget _buildFAB() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        FloatingActionButton(
          heroTag: 'prefetch',
          onPressed: _isPrefetching ? null : _prefetchCurrentArea,
          tooltip: 'تحميل مسبق - Prefetch',
          child: const Icon(Icons.download),
        ),
        const SizedBox(height: 8),
        FloatingActionButton(
          heroTag: 'refresh',
          onPressed: _loadCacheInfo,
          tooltip: 'تحديث - Refresh',
          child: const Icon(Icons.refresh),
        ),
      ],
    );
  }

  /// عرض الإعدادات - Show settings
  void _showSettings() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'الإعدادات - Settings',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),

            // جودة الضغط - Compression quality
            Text('الجودة - Quality: ${(_quality * 100).toInt()}%'),
            Slider(
              value: _quality,
              min: 0.3,
              max: 1.0,
              divisions: 7,
              label: '${(_quality * 100).toInt()}%',
              onChanged: _changeQuality,
            ),

            const Divider(),

            // إعدادات مسبقة - Presets
            const Text('إعدادات مسبقة - Presets'),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                ElevatedButton(
                  onPressed: () => _changeQuality(ImageCompressionUtil.mobileQuality),
                  child: const Text('جوال - Mobile (60%)'),
                ),
                ElevatedButton(
                  onPressed: () => _changeQuality(ImageCompressionUtil.tabletQuality),
                  child: const Text('تابلت - Tablet (80%)'),
                ),
              ],
            ),

            const Divider(),

            // تحميل مسبق للمدن - Prefetch cities
            const Text('تحميل مسبق - Prefetch Cities'),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ElevatedButton(
                  onPressed: _isPrefetching
                      ? null
                      : () => _prefetchAroundLocation(sanaa, 'صنعاء - Sana\'a'),
                  child: const Text('صنعاء'),
                ),
                ElevatedButton(
                  onPressed: _isPrefetching
                      ? null
                      : () => _prefetchAroundLocation(aden, 'عدن - Aden'),
                  child: const Text('عدن'),
                ),
                ElevatedButton(
                  onPressed: _isPrefetching
                      ? null
                      : () => _prefetchAroundLocation(taiz, 'تعز - Taiz'),
                  child: const Text('تعز'),
                ),
                ElevatedButton(
                  onPressed: _isPrefetching
                      ? null
                      : () => _prefetchAroundLocation(hodeidah, 'الحديدة - Hodeidah'),
                  child: const Text('الحديدة'),
                ),
              ],
            ),

            const Divider(),

            // إدارة الكاش - Cache management
            ElevatedButton.icon(
              onPressed: _clearCache,
              icon: const Icon(Icons.delete),
              label: const Text('مسح الكاش - Clear Cache'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }
}

/// زر موقع - Location button
class _LocationButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  const _LocationButton({
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 20),
          Text(label, style: const TextStyle(fontSize: 10)),
        ],
      ),
      onPressed: onPressed,
      tooltip: label,
    );
  }
}
