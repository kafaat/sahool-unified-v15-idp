import 'package:flutter/material.dart';

import '../../../../core/maps/offline/tile_storage.dart';
import '../../../../core/theme/sahool_theme.dart';

/// Storage Usage Bar - شريط استخدام التخزين
///
/// Displays storage usage with breakdown by regions
class StorageUsageBar extends StatelessWidget {
  final int usedBytes;
  final Map<String, RegionStats>? regions;
  final int? totalBytes;
  final VoidCallback? onClearPressed;

  const StorageUsageBar({
    super.key,
    required this.usedBytes,
    this.regions,
    this.totalBytes,
    this.onClearPressed,
  });

  @override
  Widget build(BuildContext context) {
    // Assume 2GB total if not provided
    final total = totalBytes ?? (2 * 1024 * 1024 * 1024);
    final usagePercent = (usedBytes / total).clamp(0.0, 1.0);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: SahoolShadows.small,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: SahoolColors.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(
                      Icons.storage,
                      color: SahoolColors.primary,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'تخزين الخرائط',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        '${_formatBytes(usedBytes)} مستخدم',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              if (onClearPressed != null && usedBytes > 0)
                TextButton.icon(
                  onPressed: onClearPressed,
                  icon: const Icon(Icons.delete_outline, size: 18),
                  label: const Text('مسح'),
                  style: TextButton.styleFrom(
                    foregroundColor: SahoolColors.danger,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 16),

          // Usage bar
          _UsageProgressBar(
            usagePercent: usagePercent,
            regions: regions,
          ),
          const SizedBox(height: 8),

          // Usage text
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                '${(usagePercent * 100).toStringAsFixed(1)}% مستخدم',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
              Text(
                'متاح: ${_formatBytes(total - usedBytes)}',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),

          // Region breakdown
          if (regions != null && regions!.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 8),
            _RegionBreakdown(regions: regions!),
          ],
        ],
      ),
    );
  }

  String _formatBytes(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    }
    if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(2)} GB';
  }
}

/// Usage progress bar with segments - شريط التقدم مع الأقسام
class _UsageProgressBar extends StatelessWidget {
  final double usagePercent;
  final Map<String, RegionStats>? regions;

  const _UsageProgressBar({
    required this.usagePercent,
    this.regions,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: Container(
        height: 12,
        color: Colors.grey[200],
        child: Row(
          children: _buildSegments(),
        ),
      ),
    );
  }

  List<Widget> _buildSegments() {
    if (regions == null || regions!.isEmpty) {
      return [
        Flexible(
          flex: (usagePercent * 1000).round(),
          child: Container(color: SahoolColors.primary),
        ),
        Flexible(
          flex: ((1 - usagePercent) * 1000).round(),
          child: Container(color: Colors.transparent),
        ),
      ];
    }

    // Build colored segments for each region
    final segments = <Widget>[];
    final colors = [
      SahoolColors.primary,
      Colors.blue,
      Colors.orange,
      Colors.teal,
      Colors.purple,
      Colors.pink,
    ];

    var colorIndex = 0;
    for (final entry in regions!.entries) {
      final regionPercent = entry.value.sizeBytes /
          (2 * 1024 * 1024 * 1024); // Assuming 2GB total

      if (regionPercent > 0) {
        segments.add(
          Flexible(
            flex: (regionPercent * 1000).round().clamp(1, 1000),
            child: Container(
              color: colors[colorIndex % colors.length],
            ),
          ),
        );
        colorIndex++;
      }
    }

    // Add remaining space
    segments.add(
      Expanded(
        child: Container(color: Colors.transparent),
      ),
    );

    return segments;
  }
}

/// Region breakdown - تفاصيل المناطق
class _RegionBreakdown extends StatelessWidget {
  final Map<String, RegionStats> regions;

  const _RegionBreakdown({required this.regions});

  @override
  Widget build(BuildContext context) {
    final colors = [
      SahoolColors.primary,
      Colors.blue,
      Colors.orange,
      Colors.teal,
      Colors.purple,
      Colors.pink,
    ];

    return Wrap(
      spacing: 12,
      runSpacing: 8,
      children: regions.entries.toList().asMap().entries.map((entry) {
        final index = entry.key;
        final region = entry.value;
        final color = colors[index % colors.length];

        return _RegionChip(
          regionId: region.value.regionId,
          size: region.value.formattedSize,
          color: color,
        );
      }).toList(),
    );
  }
}

/// Region chip - شريحة المنطقة
class _RegionChip extends StatelessWidget {
  final String regionId;
  final String size;
  final Color color;

  const _RegionChip({
    required this.regionId,
    required this.size,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            _formatRegionId(regionId),
            style: TextStyle(
              fontSize: 12,
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            size,
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  String _formatRegionId(String id) {
    // Convert ID to display name
    return id
        .replaceAll('_', ' ')
        .split(' ')
        .map((word) => word.isNotEmpty
            ? '${word[0].toUpperCase()}${word.substring(1)}'
            : '')
        .join(' ');
  }
}

/// Compact Storage Usage - استخدام التخزين المدمج
class CompactStorageUsage extends StatelessWidget {
  final int usedBytes;
  final int? totalBytes;

  const CompactStorageUsage({
    super.key,
    required this.usedBytes,
    this.totalBytes,
  });

  @override
  Widget build(BuildContext context) {
    final total = totalBytes ?? (2 * 1024 * 1024 * 1024);
    final usagePercent = (usedBytes / total).clamp(0.0, 1.0);

    return Row(
      children: [
        Icon(
          Icons.storage,
          size: 18,
          color: Colors.grey[600],
        ),
        const SizedBox(width: 8),
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: usagePercent,
              minHeight: 6,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation(
                usagePercent > 0.9 ? SahoolColors.danger : SahoolColors.primary,
              ),
            ),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          _formatBytes(usedBytes),
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  String _formatBytes(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) {
      return '${(bytes / 1024).toStringAsFixed(1)} KB';
    }
    if (bytes < 1024 * 1024 * 1024) {
      return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
    }
    return '${(bytes / (1024 * 1024 * 1024)).toStringAsFixed(2)} GB';
  }
}

/// Storage Warning Banner - شريط تحذير التخزين
class StorageWarningBanner extends StatelessWidget {
  final int usedBytes;
  final int totalBytes;
  final VoidCallback? onManagePressed;

  const StorageWarningBanner({
    super.key,
    required this.usedBytes,
    required this.totalBytes,
    this.onManagePressed,
  });

  @override
  Widget build(BuildContext context) {
    final usagePercent = usedBytes / totalBytes;

    if (usagePercent < 0.8) return const SizedBox.shrink();

    final isHigh = usagePercent >= 0.95;

    return Container(
      padding: const EdgeInsets.all(12),
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: (isHigh ? SahoolColors.danger : SahoolColors.warning)
            .withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isHigh ? SahoolColors.danger : SahoolColors.warning,
        ),
      ),
      child: Row(
        children: [
          Icon(
            isHigh ? Icons.error : Icons.warning,
            color: isHigh ? SahoolColors.danger : SahoolColors.warning,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isHigh ? 'التخزين ممتلئ تقريباً' : 'التخزين يقترب من الامتلاء',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: isHigh ? SahoolColors.danger : SahoolColors.warning,
                  ),
                ),
                Text(
                  '${(usagePercent * 100).toStringAsFixed(0)}% مستخدم. احذف بعض المناطق لتوفير مساحة.',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[700],
                  ),
                ),
              ],
            ),
          ),
          if (onManagePressed != null)
            TextButton(
              onPressed: onManagePressed,
              child: const Text('إدارة'),
            ),
        ],
      ),
    );
  }
}
