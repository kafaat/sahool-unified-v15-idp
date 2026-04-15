/// Maintenance Timeline Widget - الجدول الزمني للصيانة
/// Visual timeline of maintenance history and upcoming
library;
import 'package:flutter/material.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/maintenance_record.dart';
import '../../domain/models/equipment_status.dart';

/// Maintenance Timeline Widget
class MaintenanceTimeline extends StatelessWidget {
  final List<MaintenanceRecord> records;
  final int maxItems;
  final VoidCallback? onViewAll;

  const MaintenanceTimeline({
    super.key,
    required this.records,
    this.maxItems = 5,
    this.onViewAll,
  });

  @override
  Widget build(BuildContext context) {
    final displayRecords = records.take(maxItems).toList();

    if (displayRecords.isEmpty) {
      return _buildEmptyState();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: SahoolColors.harvestGold.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.history,
                color: SahoolColors.harvestGold,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              'سجل الصيانة',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const Spacer(),
            if (onViewAll != null && records.length > maxItems)
              TextButton(
                onPressed: onViewAll,
                child: const Text('عرض الكل'),
              ),
          ],
        ),
        const SizedBox(height: 16),

        // Timeline
        ...displayRecords.asMap().entries.map((entry) {
          final index = entry.key;
          final record = entry.value;
          final isLast = index == displayRecords.length - 1;

          return _MaintenanceTimelineItem(
            record: record,
            isLast: isLast,
          );
        }),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.build_circle_outlined,
              size: 48,
              color: Colors.grey[300],
            ),
            const SizedBox(height: 16),
            Text(
              'لا يوجد سجل صيانة',
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Single timeline item
class _MaintenanceTimelineItem extends StatelessWidget {
  final MaintenanceRecord record;
  final bool isLast;

  const _MaintenanceTimelineItem({
    required this.record,
    required this.isLast,
  });

  @override
  Widget build(BuildContext context) {
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Timeline indicator
          Column(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: _getTypeColor().withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Icon(
                  _getTypeIcon(),
                  color: _getTypeColor(),
                  size: 20,
                ),
              ),
              if (!isLast)
                Expanded(
                  child: Container(
                    width: 2,
                    color: Colors.grey[200],
                  ),
                ),
            ],
          ),
          const SizedBox(width: 12),

          // Content
          Expanded(
            child: Padding(
              padding: EdgeInsets.only(bottom: isLast ? 0 : 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Type and date
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          record.maintenanceType.nameAr,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      Text(
                        _formatDate(record.performedAt ?? record.createdAt),
                        style: TextStyle(
                          color: Colors.grey[500],
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),

                  // Description
                  Text(
                    record.getDescription('ar'),
                    style: TextStyle(
                      color: Colors.grey[700],
                      fontSize: 13,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),

                  // Meta row
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 12,
                    runSpacing: 4,
                    children: [
                      if (record.performedBy != null)
                        _buildMetaChip(
                          Icons.person,
                          record.performedBy!,
                        ),
                      if (record.cost != null)
                        _buildMetaChip(
                          Icons.attach_money,
                          record.formattedCost,
                        ),
                      if (record.partsReplaced != null &&
                          record.partsReplaced!.isNotEmpty)
                        _buildMetaChip(
                          Icons.build,
                          '${record.partsReplaced!.length} قطع',
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetaChip(IconData icon, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 12, color: Colors.grey[500]),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }

  Color _getTypeColor() {
    switch (record.maintenanceType) {
      case MaintenanceType.oilChange:
        return Colors.amber;
      case MaintenanceType.filterChange:
        return Colors.blue;
      case MaintenanceType.tireCheck:
        return Colors.grey;
      case MaintenanceType.batteryCheck:
        return Colors.green;
      case MaintenanceType.calibration:
        return Colors.purple;
      case MaintenanceType.generalService:
        return SahoolColors.forestGreen;
      case MaintenanceType.repair:
        return SahoolColors.danger;
      case MaintenanceType.inspection:
        return Colors.teal;
      case MaintenanceType.cleaning:
        return Colors.cyan;
      case MaintenanceType.partReplacement:
        return Colors.orange;
      case MaintenanceType.softwareUpdate:
        return Colors.indigo;
      case MaintenanceType.other:
        return Colors.grey;
    }
  }

  IconData _getTypeIcon() {
    switch (record.maintenanceType) {
      case MaintenanceType.oilChange:
        return Icons.oil_barrel;
      case MaintenanceType.filterChange:
        return Icons.filter_alt;
      case MaintenanceType.tireCheck:
        return Icons.tire_repair;
      case MaintenanceType.batteryCheck:
        return Icons.battery_charging_full;
      case MaintenanceType.calibration:
        return Icons.tune;
      case MaintenanceType.generalService:
        return Icons.build;
      case MaintenanceType.repair:
        return Icons.handyman;
      case MaintenanceType.inspection:
        return Icons.search;
      case MaintenanceType.cleaning:
        return Icons.cleaning_services;
      case MaintenanceType.partReplacement:
        return Icons.swap_horiz;
      case MaintenanceType.softwareUpdate:
        return Icons.system_update;
      case MaintenanceType.other:
        return Icons.settings;
    }
  }
}

/// Upcoming Maintenance Card
class UpcomingMaintenanceCard extends StatelessWidget {
  final ScheduledMaintenance schedule;
  final VoidCallback? onTap;
  final VoidCallback? onComplete;

  const UpcomingMaintenanceCard({
    super.key,
    required this.schedule,
    this.onTap,
    this.onComplete,
  });

  @override
  Widget build(BuildContext context) {
    final isOverdue = schedule.isOverdue;
    final isDueSoon = schedule.isDueSoon;
    final cardColor = isOverdue
        ? SahoolColors.danger.withValues(alpha: 0.1)
        : isDueSoon
            ? SahoolColors.harvestGold.withValues(alpha: 0.1)
            : Colors.white;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isOverdue
                ? SahoolColors.danger.withValues(alpha: 0.3)
                : isDueSoon
                    ? SahoolColors.harvestGold.withValues(alpha: 0.3)
                    : Colors.grey.withValues(alpha: 0.2),
          ),
        ),
        child: Row(
          children: [
            // Icon
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: _getPriorityColor().withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                _getTypeIcon(),
                color: _getPriorityColor(),
              ),
            ),
            const SizedBox(width: 12),

            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          schedule.equipmentName,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ),
                      _buildDueBadge(),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    schedule.maintenanceType.nameAr,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    schedule.getDescription('ar'),
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

            // Complete button
            if (onComplete != null)
              IconButton(
                onPressed: onComplete,
                icon: const Icon(Icons.check_circle_outline),
                color: SahoolColors.forestGreen,
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildDueBadge() {
    final isOverdue = schedule.isOverdue;
    final days = schedule.daysUntil;

    String text;
    Color color;

    if (isOverdue) {
      text = 'متأخر ${(-days)} يوم';
      color = SahoolColors.danger;
    } else if (days == 0) {
      text = 'اليوم';
      color = SahoolColors.harvestGold;
    } else if (days == 1) {
      text = 'غدا';
      color = SahoolColors.harvestGold;
    } else if (days <= 7) {
      text = 'بعد $days أيام';
      color = Colors.orange;
    } else {
      text = _formatDate(schedule.scheduledDate);
      color = Colors.grey;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontSize: 10,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}';
  }

  Color _getPriorityColor() {
    switch (schedule.priority) {
      case MaintenancePriority.low:
        return Colors.green;
      case MaintenancePriority.medium:
        return SahoolColors.harvestGold;
      case MaintenancePriority.high:
        return Colors.orange;
      case MaintenancePriority.critical:
        return SahoolColors.danger;
    }
  }

  IconData _getTypeIcon() {
    switch (schedule.maintenanceType) {
      case MaintenanceType.oilChange:
        return Icons.oil_barrel;
      case MaintenanceType.filterChange:
        return Icons.filter_alt;
      case MaintenanceType.tireCheck:
        return Icons.tire_repair;
      case MaintenanceType.batteryCheck:
        return Icons.battery_charging_full;
      case MaintenanceType.calibration:
        return Icons.tune;
      case MaintenanceType.generalService:
        return Icons.build;
      case MaintenanceType.repair:
        return Icons.handyman;
      case MaintenanceType.inspection:
        return Icons.search;
      case MaintenanceType.cleaning:
        return Icons.cleaning_services;
      case MaintenanceType.partReplacement:
        return Icons.swap_horiz;
      case MaintenanceType.softwareUpdate:
        return Icons.system_update;
      case MaintenanceType.other:
        return Icons.settings;
    }
  }
}
