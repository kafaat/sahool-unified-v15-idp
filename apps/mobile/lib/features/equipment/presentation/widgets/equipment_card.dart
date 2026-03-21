/// Equipment Card Widget - بطاقة المعدة
/// Displays equipment info in a card format
library;
import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../../domain/models/equipment.dart';

/// Equipment Card Widget
class EquipmentCard extends StatelessWidget {
  final Equipment equipment;
  final VoidCallback? onTap;
  final bool showLocation;
  final bool showFuel;
  final bool showHours;
  final bool compact;

  const EquipmentCard({
    super.key,
    required this.equipment,
    this.onTap,
    this.showLocation = true,
    this.showFuel = true,
    this.showHours = true,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    final statusColor = _getStatusColor(equipment.status);

    return GestureDetector(
      onTap: onTap,
      child: OrganicCard(
        padding: EdgeInsets.all(compact ? 12 : 16),
        child: compact ? _buildCompactLayout(statusColor) : _buildFullLayout(statusColor),
      ),
    );
  }

  Widget _buildFullLayout(Color statusColor) {
    return Row(
      children: [
        // Equipment icon/image
        Container(
          width: 64,
          height: 64,
          decoration: BoxDecoration(
            color: SahoolColors.paleOlive.withOpacity(0.5),
            borderRadius: BorderRadius.circular(16),
          ),
          child: equipment.imageUrl != null
              ? ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: CachedNetworkImage(
                    imageUrl: equipment.imageUrl!,
                    fit: BoxFit.cover,
                    placeholder: (_, __) => const Center(child: CircularProgressIndicator(strokeWidth: 2)),
                    errorWidget: (_, __, ___) => _buildDefaultIcon(),
                  ),
                )
              : _buildDefaultIcon(),
        ),
        const SizedBox(width: 16),

        // Equipment info
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      equipment.getDisplayName('ar'),
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ),
                  StatusBadge(
                    label: equipment.status.nameAr,
                    color: statusColor,
                    isSmall: true,
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                equipment.equipmentType.nameAr,
                style: const TextStyle(color: Colors.grey, fontSize: 13),
              ),
              if (equipment.brand != null || equipment.model != null) ...[
                const SizedBox(height: 2),
                Text(
                  [equipment.brand, equipment.model].whereType<String>().join(' '),
                  style: TextStyle(color: Colors.grey[500], fontSize: 12),
                ),
              ],
              const SizedBox(height: 8),
              _buildMetricsRow(),
            ],
          ),
        ),

        const SizedBox(width: 8),
        const Icon(Icons.chevron_right, color: Colors.grey),
      ],
    );
  }

  Widget _buildCompactLayout(Color statusColor) {
    return Row(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: SahoolColors.paleOlive.withOpacity(0.5),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            _getEquipmentIcon(),
            size: 20,
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                equipment.getDisplayName('ar'),
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              Text(
                equipment.equipmentType.nameAr,
                style: const TextStyle(color: Colors.grey, fontSize: 11),
              ),
            ],
          ),
        ),
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: statusColor,
            shape: BoxShape.circle,
          ),
        ),
      ],
    );
  }

  Widget _buildMetricsRow() {
    return Row(
      children: [
        if (showLocation) ...[
          Icon(Icons.location_on, size: 14, color: Colors.grey[400]),
          const SizedBox(width: 4),
          Flexible(
            child: Text(
              equipment.locationName ?? 'غير محدد',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
        if (showFuel && equipment.currentFuelPercent != null) ...[
          if (showLocation) const SizedBox(width: 12),
          Icon(
            Icons.local_gas_station,
            size: 14,
            color: equipment.isLowFuel ? Colors.orange : Colors.green,
          ),
          const SizedBox(width: 4),
          Text(
            '${equipment.currentFuelPercent!.toInt()}%',
            style: TextStyle(
              fontSize: 12,
              color: equipment.isLowFuel ? Colors.orange : Colors.green,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
        if (showHours) ...[
          const Spacer(),
          Icon(Icons.timer, size: 14, color: Colors.grey[400]),
          const SizedBox(width: 4),
          Text(
            "${equipment.currentHours?.toStringAsFixed(0) ?? '-'}h",
            style: const TextStyle(fontSize: 12, color: Colors.grey),
          ),
        ],
      ],
    );
  }

  Widget _buildDefaultIcon() {
    return Icon(
      _getEquipmentIcon(),
      size: 32,
      color: SahoolColors.forestGreen,
    );
  }

  IconData _getEquipmentIcon() {
    switch (equipment.equipmentType) {
      case EquipmentType.tractor:
        return Icons.agriculture;
      case EquipmentType.pump:
        return Icons.water;
      case EquipmentType.drone:
        return Icons.flight;
      case EquipmentType.harvester:
        return Icons.grass;
      case EquipmentType.sprayer:
        return Icons.shower;
      case EquipmentType.pivot:
        return Icons.rotate_right;
      case EquipmentType.sensor:
        return Icons.sensors;
      case EquipmentType.vehicle:
        return Icons.local_shipping;
      case EquipmentType.iotDevice:
        return Icons.router;
      case EquipmentType.other:
        return Icons.build;
    }
  }

  Color _getStatusColor(EquipmentStatus status) {
    switch (status) {
      case EquipmentStatus.operational:
      case EquipmentStatus.standby:
        return SahoolColors.forestGreen;
      case EquipmentStatus.inUse:
        return Colors.blue;
      case EquipmentStatus.maintenance:
        return SahoolColors.harvestGold;
      case EquipmentStatus.inactive:
        return Colors.grey;
      case EquipmentStatus.repair:
        return SahoolColors.danger;
    }
  }
}

/// Large Equipment Card for dashboard
class EquipmentLargeCard extends StatelessWidget {
  final Equipment equipment;
  final VoidCallback? onTap;
  final VoidCallback? onMaintenanceTap;
  final VoidCallback? onFuelTap;

  const EquipmentLargeCard({
    super.key,
    required this.equipment,
    this.onTap,
    this.onMaintenanceTap,
    this.onFuelTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: OrganicCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: SahoolColors.paleOlive,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    _getEquipmentIcon(),
                    color: SahoolColors.forestGreen,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        equipment.getDisplayName('ar'),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        equipment.equipmentType.nameAr,
                        style: TextStyle(color: Colors.grey[600], fontSize: 12),
                      ),
                    ],
                  ),
                ),
                _buildStatusChip(),
              ],
            ),

            const SizedBox(height: 16),
            const Divider(height: 1),
            const SizedBox(height: 16),

            // Stats row
            Row(
              children: [
                _buildStatItem(
                  Icons.local_gas_station,
                  '${equipment.currentFuelPercent?.toInt() ?? '-'}%',
                  'الوقود',
                  equipment.isLowFuel ? Colors.orange : SahoolColors.forestGreen,
                ),
                _buildStatItem(
                  Icons.timer,
                  equipment.currentHours?.toStringAsFixed(0) ?? '-',
                  'ساعات',
                  Colors.blue,
                ),
                _buildStatItem(
                  Icons.build,
                  equipment.needsMaintenanceSoon ? '!' : '-',
                  'صيانة',
                  equipment.needsMaintenanceSoon
                      ? SahoolColors.harvestGold
                      : Colors.grey,
                ),
              ],
            ),

            // Action buttons
            if (onMaintenanceTap != null || onFuelTap != null) ...[
              const SizedBox(height: 16),
              Row(
                children: [
                  if (onMaintenanceTap != null)
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: onMaintenanceTap,
                        icon: const Icon(Icons.build, size: 16),
                        label: const Text('صيانة'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: SahoolColors.harvestGold,
                          side: const BorderSide(color: SahoolColors.harvestGold),
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                  if (onMaintenanceTap != null && onFuelTap != null)
                    const SizedBox(width: 12),
                  if (onFuelTap != null)
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: onFuelTap,
                        icon: const Icon(Icons.local_gas_station, size: 16),
                        label: const Text('تعبئة'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: SahoolColors.forestGreen,
                          side: const BorderSide(color: SahoolColors.forestGreen),
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatusChip() {
    final color = _getStatusColor();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 6),
          Text(
            equipment.status.nameAr,
            style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(IconData icon, String value, String label, Color color) {
    return Expanded(
      child: Column(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(color: Colors.grey[500], fontSize: 10),
          ),
        ],
      ),
    );
  }

  IconData _getEquipmentIcon() {
    switch (equipment.equipmentType) {
      case EquipmentType.tractor:
        return Icons.agriculture;
      case EquipmentType.pump:
        return Icons.water;
      case EquipmentType.drone:
        return Icons.flight;
      case EquipmentType.harvester:
        return Icons.grass;
      case EquipmentType.sprayer:
        return Icons.shower;
      case EquipmentType.pivot:
        return Icons.rotate_right;
      case EquipmentType.sensor:
        return Icons.sensors;
      case EquipmentType.vehicle:
        return Icons.local_shipping;
      case EquipmentType.iotDevice:
        return Icons.router;
      case EquipmentType.other:
        return Icons.build;
    }
  }

  Color _getStatusColor() {
    switch (equipment.status) {
      case EquipmentStatus.operational:
      case EquipmentStatus.standby:
        return SahoolColors.forestGreen;
      case EquipmentStatus.inUse:
        return Colors.blue;
      case EquipmentStatus.maintenance:
        return SahoolColors.harvestGold;
      case EquipmentStatus.inactive:
        return Colors.grey;
      case EquipmentStatus.repair:
        return SahoolColors.danger;
    }
  }
}
