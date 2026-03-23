import 'package:flutter/material.dart';

import '../../../../core/maps/offline/region_manager.dart';
import '../../../../core/maps/offline/tile_downloader.dart';
import '../../../../core/maps/offline/tile_storage.dart';
import '../../../../core/theme/sahool_theme.dart';

/// Region Card - بطاقة المنطقة
///
/// Displays region information with download status and actions
class RegionCard extends StatelessWidget {
  final MapRegion region;
  final DownloadEstimate? estimate;
  final DownloadedRegion? downloadedRegion;
  final bool isSelected;
  final VoidCallback? onTap;
  final VoidCallback? onDownload;
  final VoidCallback? onDelete;

  const RegionCard({
    super.key,
    required this.region,
    this.estimate,
    this.downloadedRegion,
    this.isSelected = false,
    this.onTap,
    this.onDownload,
    this.onDelete,
  });

  bool get isDownloaded =>
      downloadedRegion != null &&
      downloadedRegion!.status == DownloadStatus.completed;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: isSelected
              ? SahoolColors.primary.withOpacity(0.08)
              : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected
                ? SahoolColors.primary
                : isDownloaded
                    ? SahoolColors.success.withOpacity(0.5)
                    : Colors.grey[200]!,
            width: isSelected ? 2 : 1,
          ),
          boxShadow: SahoolShadows.small,
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Category icon
              _buildCategoryIcon(),
              const SizedBox(width: 16),

              // Region info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Name
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            region.nameAr,
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                              color:
                                  isSelected ? SahoolColors.primary : null,
                            ),
                          ),
                        ),
                        if (isDownloaded)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: SahoolColors.success.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  Icons.check_circle,
                                  size: 14,
                                  color: SahoolColors.success,
                                ),
                                SizedBox(width: 4),
                                Text(
                                  'محمّل',
                                  style: TextStyle(
                                    fontSize: 11,
                                    color: SahoolColors.success,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),

                    // English name
                    Text(
                      region.nameEn,
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                    ),

                    // Description
                    if (region.descriptionAr != null) ...[
                      const SizedBox(height: 4),
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
                    const SizedBox(height: 8),

                    // Size and stats
                    Row(
                      children: [
                        if (downloadedRegion != null) ...[
                          _buildInfoChip(
                            Icons.storage,
                            downloadedRegion!.formattedSize,
                          ),
                          const SizedBox(width: 8),
                          _buildInfoChip(
                            Icons.grid_view,
                            '${downloadedRegion!.tileCount}',
                          ),
                        ] else if (estimate != null) ...[
                          _buildInfoChip(
                            Icons.storage,
                            '≈ ${estimate!.formattedSize}',
                            isEstimate: true,
                          ),
                          const SizedBox(width: 8),
                          _buildInfoChip(
                            Icons.grid_view,
                            '≈ ${estimate!.tileCount}',
                            isEstimate: true,
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),

              // Action button
              if (onDownload != null || onDelete != null) ...[
                const SizedBox(width: 8),
                _buildActionButton(),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCategoryIcon() {
    final (color, icon) = _getCategoryStyle(region.category);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Icon(
        icon,
        color: color,
        size: 28,
      ),
    );
  }

  Widget _buildInfoChip(IconData icon, String label, {bool isEstimate = false}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 14,
            color: Colors.grey[600],
          ),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[600],
              fontStyle: isEstimate ? FontStyle.italic : FontStyle.normal,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton() {
    if (isDownloaded && onDelete != null) {
      return IconButton(
        onPressed: onDelete,
        icon: const Icon(Icons.delete_outline),
        color: SahoolColors.danger,
        tooltip: 'حذف',
      );
    }

    if (!isDownloaded && onDownload != null) {
      return IconButton(
        onPressed: onDownload,
        icon: const Icon(Icons.download),
        color: SahoolColors.primary,
        tooltip: 'تحميل',
      );
    }

    return const SizedBox.shrink();
  }

  (Color, IconData) _getCategoryStyle(RegionCategory category) {
    return switch (category) {
      RegionCategory.highland => (SahoolColors.primary, Icons.terrain),
      RegionCategory.coastal => (Colors.blue, Icons.waves),
      RegionCategory.desert => (Colors.orange, Icons.wb_sunny),
      RegionCategory.island => (Colors.teal, Icons.beach_access),
      RegionCategory.custom => (Colors.purple, Icons.location_on),
    };
  }
}

/// Compact Region Card - بطاقة منطقة مدمجة
///
/// A smaller version for lists
class CompactRegionCard extends StatelessWidget {
  final MapRegion region;
  final String? sizeLabel;
  final bool isSelected;
  final VoidCallback? onTap;

  const CompactRegionCard({
    super.key,
    required this.region,
    this.sizeLabel,
    this.isSelected = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isSelected
              ? SahoolColors.primary.withOpacity(0.1)
              : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? SahoolColors.primary : Colors.grey[200]!,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            // Icon
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: _getCategoryColor(region.category).withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                _getCategoryIcon(region.category),
                color: _getCategoryColor(region.category),
                size: 20,
              ),
            ),
            const SizedBox(width: 12),

            // Name
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    region.nameAr,
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                      color: isSelected ? SahoolColors.primary : null,
                    ),
                  ),
                  if (sizeLabel != null)
                    Text(
                      sizeLabel!,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[500],
                      ),
                    ),
                ],
              ),
            ),

            // Selection indicator
            Icon(
              isSelected
                  ? Icons.check_circle
                  : Icons.radio_button_unchecked,
              color: isSelected ? SahoolColors.primary : Colors.grey[400],
            ),
          ],
        ),
      ),
    );
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

/// Category Badge - شارة الفئة
class CategoryBadge extends StatelessWidget {
  final RegionCategory category;
  final bool showLabel;

  const CategoryBadge({
    super.key,
    required this.category,
    this.showLabel = true,
  });

  @override
  Widget build(BuildContext context) {
    final (color, icon) = _getCategoryStyle(category);

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: showLabel ? 10 : 6,
        vertical: 6,
      ),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          if (showLabel) ...[
            const SizedBox(width: 6),
            Text(
              category.nameAr,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: color,
              ),
            ),
          ],
        ],
      ),
    );
  }

  (Color, IconData) _getCategoryStyle(RegionCategory category) {
    return switch (category) {
      RegionCategory.highland => (SahoolColors.primary, Icons.terrain),
      RegionCategory.coastal => (Colors.blue, Icons.waves),
      RegionCategory.desert => (Colors.orange, Icons.wb_sunny),
      RegionCategory.island => (Colors.teal, Icons.beach_access),
      RegionCategory.custom => (Colors.purple, Icons.location_on),
    };
  }
}
