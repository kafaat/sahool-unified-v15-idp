import 'package:flutter/material.dart';
import '../../domain/entities/crop_health_entities.dart';

/// اختيار المنطقة
class ZoneSelector extends StatelessWidget {
  final List<Zone> zones;
  final String? selectedZoneId;
  final ValueChanged<String?> onZoneSelected;

  const ZoneSelector({
    super.key,
    required this.zones,
    this.selectedZoneId,
    required this.onZoneSelected,
  });

  @override
  Widget build(BuildContext context) {
    if (zones.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'المناطق',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 80,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: zones.length + 1, // +1 for "All" option
            separatorBuilder: (_, __) => const SizedBox(width: 12),
            itemBuilder: (context, index) {
              if (index == 0) {
                return _buildZoneChip(
                  context,
                  zoneId: null,
                  name: 'الكل',
                  nameAr: 'الكل',
                  isSelected: selectedZoneId == null,
                );
              }

              final zone = zones[index - 1];
              return _buildZoneChip(
                context,
                zoneId: zone.zoneId,
                name: zone.name,
                nameAr: zone.nameAr,
                areaHectares: zone.areaHectares,
                isSelected: selectedZoneId == zone.zoneId,
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildZoneChip(
    BuildContext context, {
    required String? zoneId,
    required String name,
    String? nameAr,
    double? areaHectares,
    required bool isSelected,
  }) {
    return GestureDetector(
      onTap: () => onZoneSelected(zoneId),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected
              ? const Color(0xFF367C2B)
              : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected
                ? const Color(0xFF367C2B)
                : Colors.grey[300]!,
            width: 2,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: const Color(0xFF367C2B).withOpacity(0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ]
              : null,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              nameAr ?? name,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: isSelected ? Colors.white : Colors.black87,
              ),
            ),
            if (areaHectares != null) ...[
              const SizedBox(height: 4),
              Text(
                '${areaHectares.toStringAsFixed(1)} هكتار',
                style: TextStyle(
                  fontSize: 12,
                  color: isSelected ? Colors.white70 : Colors.grey[600],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
