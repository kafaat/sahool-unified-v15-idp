/// Crop Card Widget
/// بطاقة المحصول
///
/// Displays a crop card with image, name, variety, growth stage,
/// NDVI-based health indicator, and days since planting / to harvest.
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../../data/crop_helper.dart';
import '../providers/crops_provider.dart';

/// Crop card showing key information at a glance
/// بطاقة المحصول لعرض المعلومات الرئيسية بنظرة سريعة
class CropCard extends StatelessWidget {
  final ActiveCrop activeCrop;
  final VoidCallback? onTap;

  const CropCard({
    super.key,
    required this.activeCrop,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return OrganicCard(
      onTap: onTap,
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          // Crop icon with health ring
          _buildCropIcon(),
          const SizedBox(width: 16),

          // Crop info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Crop name and variety
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        '${activeCrop.crop.nameAr} (${activeCrop.crop.nameEn})',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    _buildHealthBadge(),
                  ],
                ),

                if (activeCrop.variety.isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Text(
                    'Variety | الصنف: ${activeCrop.variety}',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],

                const SizedBox(height: 6),

                // Growth stage
                Row(
                  children: [
                    Icon(Icons.trending_up, size: 14, color: Colors.grey[500]),
                    const SizedBox(width: 4),
                    Text(
                      '${activeCrop.growthStageAr} (${activeCrop.growthStage})',
                      style: const TextStyle(
                        fontSize: 12,
                        color: SahoolColors.forestGreen,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 6),

                // Field name and area
                Text(
                  '${activeCrop.fieldName} - ${activeCrop.areaHectares} ha',
                  style: TextStyle(fontSize: 11, color: Colors.grey[500]),
                ),

                const SizedBox(height: 8),

                // Timeline: days planted / days to harvest
                _buildTimeline(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Crop icon with NDVI-based color ring
  /// ايقونة المحصول مع حلقة لونية مبنية على NDVI
  Widget _buildCropIcon() {
    final healthColor = _getHealthColor();
    final emoji = CropHelper.getCropEmoji(activeCrop.crop.code);

    return Container(
      width: 64,
      height: 64,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: healthColor, width: 3),
        color: healthColor.withValues(alpha: 0.1),
      ),
      child: Center(
        child: Text(
          emoji,
          style: const TextStyle(fontSize: 28),
        ),
      ),
    );
  }

  /// Health status badge
  /// شارة حالة الصحة
  Widget _buildHealthBadge() {
    final healthColor = _getHealthColor();
    final ndviText = activeCrop.ndviValue > 0
        ? 'NDVI: ${activeCrop.ndviValue.toStringAsFixed(2)}'
        : activeCrop.healthStatusAr;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: healthColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: healthColor.withValues(alpha: 0.3)),
      ),
      child: Text(
        ndviText,
        style: TextStyle(
          fontSize: 10,
          color: healthColor,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  /// Timeline showing days since planting and days to harvest
  /// الجدول الزمني يظهر الايام منذ الزراعة والايام للحصاد
  Widget _buildTimeline() {
    final daysPlanted = activeCrop.daysSincePlanting;
    final totalDays = activeCrop.crop.growingSeasonDays;
    final progress = (daysPlanted / totalDays).clamp(0.0, 1.0);
    final daysToHarvest = activeCrop.daysToHarvest;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Progress bar
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation<Color>(_getHealthColor()),
            minHeight: 6,
          ),
        ),
        const SizedBox(height: 4),

        // Labels
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Day $daysPlanted | يوم $daysPlanted',
              style: TextStyle(fontSize: 10, color: Colors.grey[500]),
            ),
            if (daysToHarvest != null)
              Text(
                '$daysToHarvest days to harvest | يوم للحصاد',
                style: TextStyle(
                  fontSize: 10,
                  color: daysToHarvest < 14
                      ? SahoolColors.harvestGold
                      : Colors.grey[500],
                  fontWeight: daysToHarvest < 14
                      ? FontWeight.bold
                      : FontWeight.normal,
                ),
              ),
          ],
        ),
      ],
    );
  }

  /// Get health color based on NDVI value or health status
  /// الحصول على لون الصحة بناء على قيمة NDVI او حالة الصحة
  Color _getHealthColor() {
    if (activeCrop.ndviValue > 0) {
      if (activeCrop.ndviValue >= 0.6) return SahoolColors.healthExcellent;
      if (activeCrop.ndviValue >= 0.4) return SahoolColors.healthModerate;
      if (activeCrop.ndviValue >= 0.2) return SahoolColors.healthPoor;
      return SahoolColors.healthCritical;
    }

    switch (activeCrop.healthStatus) {
      case 'healthy':
      case 'excellent':
        return SahoolColors.healthExcellent;
      case 'good':
        return SahoolColors.healthGood;
      case 'moderate':
      case 'stressed':
        return SahoolColors.healthModerate;
      case 'poor':
        return SahoolColors.healthPoor;
      case 'critical':
        return SahoolColors.healthCritical;
      default:
        return SahoolColors.healthGood;
    }
  }
}
