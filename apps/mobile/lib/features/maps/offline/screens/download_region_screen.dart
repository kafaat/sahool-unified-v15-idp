import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/maps/offline/region_manager.dart';
import '../../../../core/maps/offline/tile_downloader.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../widgets/region_selector.dart';
import 'download_progress_screen.dart';

/// Download Region Screen - شاشة تحميل منطقة جديدة
///
/// Features:
/// - Browse predefined Yemen regions - تصفح مناطق اليمن المعرفة
/// - Select custom region on map - اختيار منطقة مخصصة على الخريطة
/// - Configure zoom levels - ضبط مستويات التكبير
/// - View download estimate - عرض تقدير التحميل
class DownloadRegionScreen extends ConsumerStatefulWidget {
  final RegionManager regionManager;
  final MapRegion? preselectedRegion;
  final VoidCallback? onDownloadComplete;

  const DownloadRegionScreen({
    super.key,
    required this.regionManager,
    this.preselectedRegion,
    this.onDownloadComplete,
  });

  @override
  ConsumerState<DownloadRegionScreen> createState() =>
      _DownloadRegionScreenState();
}

class _DownloadRegionScreenState extends ConsumerState<DownloadRegionScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  MapRegion? _selectedRegion;
  RegionCategory? _selectedCategory;
  int _minZoom = 10;
  int _maxZoom = 16;
  DownloadEstimate? _estimate;

  // Custom region
  RegionBounds? _customBounds;
  String _customNameAr = '';
  String _customNameEn = '';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _selectedRegion = widget.preselectedRegion;
    if (_selectedRegion != null) {
      _updateEstimate();
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  void _updateEstimate() {
    if (_selectedRegion != null) {
      setState(() {
        _estimate = widget.regionManager.getDownloadEstimate(
          region: _selectedRegion!,
          minZoom: _minZoom,
          maxZoom: _maxZoom,
        );
      });
    } else if (_customBounds != null) {
      final downloader = TileDownloader();
      setState(() {
        _estimate = downloader.estimateDownloadSize(
          bounds: _customBounds!,
          minZoom: _minZoom,
          maxZoom: _maxZoom,
        );
      });
    }
  }

  void _selectRegion(MapRegion region) {
    setState(() {
      _selectedRegion = region;
      _customBounds = null;
    });
    _updateEstimate();
  }

  void _setCustomBounds(RegionBounds bounds) {
    setState(() {
      _customBounds = bounds;
      _selectedRegion = null;
    });
    _updateEstimate();
  }

  void _startDownload() {
    if (_selectedRegion != null) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => DownloadProgressScreen(
            regionManager: widget.regionManager,
            region: _selectedRegion!,
            minZoom: _minZoom,
            maxZoom: _maxZoom,
            onComplete: () {
              widget.onDownloadComplete?.call();
              Navigator.pop(context); // Pop progress screen
              Navigator.pop(context); // Pop this screen
            },
          ),
        ),
      );
    } else if (_customBounds != null &&
        _customNameAr.isNotEmpty &&
        _customNameEn.isNotEmpty) {
      final customRegion = MapRegion(
        id: 'custom_${DateTime.now().millisecondsSinceEpoch}',
        nameAr: _customNameAr,
        nameEn: _customNameEn,
        bounds: _customBounds!,
        category: RegionCategory.custom,
        iconName: 'location_on',
      );

      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => DownloadProgressScreen(
            regionManager: widget.regionManager,
            region: customRegion,
            minZoom: _minZoom,
            maxZoom: _maxZoom,
            onComplete: () {
              widget.onDownloadComplete?.call();
              Navigator.pop(context);
              Navigator.pop(context);
            },
          ),
        ),
      );
    }
  }

  bool get _canDownload {
    if (_selectedRegion != null) return true;
    if (_customBounds != null &&
        _customNameAr.isNotEmpty &&
        _customNameEn.isNotEmpty) {
      return true;
    }
    return false;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تحميل منطقة جديدة'),
        centerTitle: true,
        bottom: TabBar(
          controller: _tabController,
          labelColor: SahoolColors.primary,
          unselectedLabelColor: SahoolColors.textSecondary,
          indicatorColor: SahoolColors.primary,
          tabs: const [
            Tab(
              icon: Icon(Icons.list),
              text: 'المحافظات',
            ),
            Tab(
              icon: Icon(Icons.map),
              text: 'منطقة مخصصة',
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildRegionsList(),
                _buildCustomRegion(),
              ],
            ),
          ),

          // Zoom level selector and estimate
          _buildBottomSection(),
        ],
      ),
    );
  }

  Widget _buildRegionsList() {
    return CustomScrollView(
      slivers: [
        // Category filter
        SliverToBoxAdapter(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                _buildCategoryChip(null, 'الكل', Icons.public),
                const SizedBox(width: 8),
                _buildCategoryChip(
                    RegionCategory.highland, 'المرتفعات', Icons.terrain),
                const SizedBox(width: 8),
                _buildCategoryChip(
                    RegionCategory.coastal, 'الساحل', Icons.waves),
                const SizedBox(width: 8),
                _buildCategoryChip(
                    RegionCategory.desert, 'الصحراء', Icons.wb_sunny),
                const SizedBox(width: 8),
                _buildCategoryChip(
                    RegionCategory.island, 'الجزر', Icons.beach_access),
              ],
            ),
          ),
        ),

        // Regions list
        SliverPadding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          sliver: SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final filteredRegions = _selectedCategory == null
                    ? YemenRegions.all
                    : YemenRegions.all
                        .where((r) => r.category == _selectedCategory)
                        .toList();

                if (index >= filteredRegions.length) return null;

                final region = filteredRegions[index];
                final isSelected = _selectedRegion?.id == region.id;
                final estimate = widget.regionManager.getDownloadEstimate(
                  region: region,
                  minZoom: _minZoom,
                  maxZoom: _maxZoom,
                );

                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: _RegionListTile(
                    region: region,
                    estimate: estimate,
                    isSelected: isSelected,
                    onTap: () => _selectRegion(region),
                  ),
                );
              },
            ),
          ),
        ),

        // Bottom padding
        const SliverPadding(padding: EdgeInsets.only(bottom: 200)),
      ],
    );
  }

  Widget _buildCategoryChip(
      RegionCategory? category, String label, IconData icon) {
    final isSelected = _selectedCategory == category;

    return FilterChip(
      selected: isSelected,
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 16,
            color: isSelected ? Colors.white : SahoolColors.primary,
          ),
          const SizedBox(width: 4),
          Text(label),
        ],
      ),
      selectedColor: SahoolColors.primary,
      checkmarkColor: Colors.white,
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : SahoolColors.textDark,
      ),
      onSelected: (selected) {
        setState(() {
          _selectedCategory = selected ? category : null;
        });
      },
    );
  }

  Widget _buildCustomRegion() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Instructions
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: SahoolColors.info.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              children: [
                const Icon(Icons.info_outline, color: SahoolColors.info),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'حدد منطقة مخصصة على الخريطة بسحب المؤشرات',
                    style: TextStyle(color: Colors.grey[700]),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Map selector
          Container(
            height: 300,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.grey[300]!),
            ),
            clipBehavior: Clip.antiAlias,
            child: RegionSelector(
              initialBounds: _customBounds,
              onBoundsChanged: _setCustomBounds,
            ),
          ),
          const SizedBox(height: 16),

          // Region name inputs
          Text(
            'اسم المنطقة',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),

          TextField(
            decoration: const InputDecoration(
              labelText: 'الاسم بالعربية',
              hintText: 'مثال: حقول القمح الشمالية',
              prefixIcon: Icon(Icons.translate),
            ),
            textDirection: TextDirection.rtl,
            onChanged: (value) => setState(() => _customNameAr = value),
          ),
          const SizedBox(height: 12),

          TextField(
            decoration: const InputDecoration(
              labelText: 'الاسم بالإنجليزية',
              hintText: 'e.g., Northern Wheat Fields',
              prefixIcon: Icon(Icons.language),
            ),
            textDirection: TextDirection.ltr,
            onChanged: (value) => setState(() => _customNameEn = value),
          ),
          const SizedBox(height: 16),

          // Selected bounds info
          if (_customBounds != null)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'الإحداثيات المحددة',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Colors.grey[700],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'شمال: ${_customBounds!.north.toStringAsFixed(4)}°\n'
                    'جنوب: ${_customBounds!.south.toStringAsFixed(4)}°\n'
                    'شرق: ${_customBounds!.east.toStringAsFixed(4)}°\n'
                    'غرب: ${_customBounds!.west.toStringAsFixed(4)}°',
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),

          const SizedBox(height: 200), // Space for bottom section
        ],
      ),
    );
  }

  Widget _buildBottomSection() {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Zoom level selector
              Row(
                children: [
                  const Icon(Icons.zoom_in, size: 20, color: SahoolColors.primary),
                  const SizedBox(width: 8),
                  Text(
                    'مستوى التفاصيل:',
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _ZoomRangeSelector(
                      minZoom: _minZoom,
                      maxZoom: _maxZoom,
                      onChanged: (min, max) {
                        setState(() {
                          _minZoom = min;
                          _maxZoom = max;
                        });
                        _updateEstimate();
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              // Estimate display
              if (_estimate != null)
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: SahoolColors.primary.withValues(alpha: 0.05),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _EstimateItem(
                        icon: Icons.storage,
                        label: 'الحجم',
                        value: _estimate!.formattedSize,
                      ),
                      Container(
                        width: 1,
                        height: 40,
                        color: Colors.grey[300],
                      ),
                      _EstimateItem(
                        icon: Icons.grid_view,
                        label: 'البلاطات',
                        value: '${_estimate!.tileCount}',
                      ),
                      Container(
                        width: 1,
                        height: 40,
                        color: Colors.grey[300],
                      ),
                      _EstimateItem(
                        icon: Icons.timer,
                        label: 'الوقت',
                        value: _estimate!.formattedDuration,
                      ),
                    ],
                  ),
                ),
              const SizedBox(height: 16),

              // Download button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _canDownload ? _startDownload : null,
                  icon: const Icon(Icons.download),
                  label: Text(
                    _selectedRegion != null
                        ? 'تحميل ${_selectedRegion!.nameAr}'
                        : 'تحميل المنطقة المخصصة',
                  ),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Region list tile - عنصر قائمة المنطقة
class _RegionListTile extends StatelessWidget {
  final MapRegion region;
  final DownloadEstimate estimate;
  final bool isSelected;
  final VoidCallback onTap;

  const _RegionListTile({
    required this.region,
    required this.estimate,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected
              ? SahoolColors.primary.withValues(alpha: 0.1)
              : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? SahoolColors.primary : Colors.grey[200]!,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            // Category icon
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: _getCategoryColor(region.category).withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(
                _getCategoryIcon(region.category),
                color: _getCategoryColor(region.category),
                size: 24,
              ),
            ),
            const SizedBox(width: 12),

            // Region info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    region.nameAr,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                      color: isSelected ? SahoolColors.primary : null,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    region.nameEn,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 4),
                  if (region.descriptionAr != null)
                    Text(
                      region.descriptionAr!,
                      style: TextStyle(
                        color: Colors.grey[500],
                        fontSize: 11,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),

            // Estimate
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  estimate.formattedSize,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: isSelected ? SahoolColors.primary : Colors.grey[700],
                  ),
                ),
                Text(
                  '${estimate.tileCount} بلاطة',
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[500],
                  ),
                ),
              ],
            ),

            // Selection indicator
            const SizedBox(width: 8),
            Icon(
              isSelected ? Icons.check_circle : Icons.radio_button_unchecked,
              color: isSelected ? SahoolColors.primary : Colors.grey[400],
            ),
          ],
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

  Color _getCategoryColor(RegionCategory category) {
    return switch (category) {
      RegionCategory.highland => SahoolColors.primary,
      RegionCategory.coastal => Colors.blue,
      RegionCategory.desert => Colors.orange,
      RegionCategory.island => Colors.teal,
      RegionCategory.custom => Colors.purple,
    };
  }
}

/// Zoom range selector - محدد نطاق التكبير
class _ZoomRangeSelector extends StatelessWidget {
  final int minZoom;
  final int maxZoom;
  final void Function(int min, int max) onChanged;

  const _ZoomRangeSelector({
    required this.minZoom,
    required this.maxZoom,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text('$minZoom', style: const TextStyle(fontWeight: FontWeight.bold)),
        Expanded(
          child: RangeSlider(
            values: RangeValues(minZoom.toDouble(), maxZoom.toDouble()),
            min: 8,
            max: 18,
            divisions: 10,
            labels: RangeLabels('$minZoom', '$maxZoom'),
            activeColor: SahoolColors.primary,
            onChanged: (values) {
              onChanged(values.start.round(), values.end.round());
            },
          ),
        ),
        Text('$maxZoom', style: const TextStyle(fontWeight: FontWeight.bold)),
      ],
    );
  }
}

/// Estimate item widget - عنصر التقدير
class _EstimateItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _EstimateItem({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, size: 20, color: SahoolColors.primary),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
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
  }
}
