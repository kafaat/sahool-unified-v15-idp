import 'package:flutter/material.dart';
import '../../data/farm_entity.dart';
import '../../../../core/config/theme.dart';

/// Farm card widget for displaying farm summary in a grid
class FarmCard extends StatelessWidget {
  final FarmEntity farm;
  final VoidCallback? onTap;

  const FarmCard({
    super.key,
    required this.farm,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: SahoolTheme.primary.withValues(alpha: 0.3),
            width: 1.5,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.06),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Farm icon and status
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: SahoolTheme.primary.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.agriculture_rounded,
                      color: SahoolTheme.primary,
                      size: 24,
                    ),
                  ),
                  if (farm.status != null) _buildStatusBadge(farm.status!),
                ],
              ),
              const SizedBox(height: 10),

              // Farm name
              Text(
                farm.nameAr ?? farm.name,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 15,
                  color: Color(0xFF1A1A1A),
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),

              // Location
              Row(
                children: [
                  Icon(Icons.location_on_rounded, size: 13, color: Colors.grey[500]),
                  const SizedBox(width: 3),
                  Expanded(
                    child: Text(
                      farm.locationAr ?? farm.location ?? '—',
                      style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              // Area
              Row(
                children: [
                  const Icon(Icons.straighten_rounded, size: 13, color: SahoolTheme.primaryDark),
                  const SizedBox(width: 4),
                  Text(
                    '${farm.totalAreaHa.toStringAsFixed(1)} هـ',
                    style: const TextStyle(
                      fontSize: 13,
                      color: SahoolTheme.primaryDark,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 6),

              // Water source badge
              if (farm.waterSource != null && farm.waterSource!.isNotEmpty)
                _buildWaterSourceBadge(farm.waterSource!),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    final isActive = status == 'active';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: (isActive ? SahoolTheme.success : Colors.grey).withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        isActive ? 'نشط' : status,
        style: TextStyle(
          fontSize: 11,
          color: isActive ? SahoolTheme.success : Colors.grey[600],
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildWaterSourceBadge(String waterSource) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.blue.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.water_drop_rounded, size: 12, color: Colors.blue),
          const SizedBox(width: 4),
          Text(
            waterSource,
            style: const TextStyle(
              fontSize: 11,
              color: Colors.blue,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
