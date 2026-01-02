// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Stats Panel Widget
// لوحة الإحصائيات
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import '../theme/atmosphere_theme.dart';

class StatsPanel extends StatelessWidget {
  const StatsPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AtmosphereSpacing.lg),
      decoration: BoxDecoration(
        gradient: AtmosphereColors.glassGradient,
        borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
        border: Border.all(color: AtmosphereColors.glassBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with Live Indicator
          Row(
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: AtmosphereColors.success,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: AtmosphereColors.success,
                      blurRadius: 6,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: AtmosphereSpacing.sm),
              Text(
                'مباشر',
                style: AtmosphereTypography.labelSmall.copyWith(
                  color: AtmosphereColors.success,
                  letterSpacing: 2,
                ),
              ),
            ],
          ),
          const SizedBox(height: AtmosphereSpacing.md),

          // Stats Grid
          Row(
            children: [
              Expanded(
                child: _buildStatItem(
                  value: '1,247',
                  label: 'الحقول النشطة',
                  icon: Icons.landscape_outlined,
                  color: AtmosphereColors.success,
                ),
              ),
              Container(
                width: 1,
                height: 50,
                color: AtmosphereColors.glassBorder,
              ),
              Expanded(
                child: _buildStatItem(
                  value: '3,892',
                  label: 'المستشعرات',
                  icon: Icons.sensors_outlined,
                  color: AtmosphereColors.info,
                ),
              ),
            ],
          ),
          const SizedBox(height: AtmosphereSpacing.md),
          Container(
            height: 1,
            color: AtmosphereColors.glassBorder,
          ),
          const SizedBox(height: AtmosphereSpacing.md),
          Row(
            children: [
              Expanded(
                child: _buildStatItem(
                  value: '94.7%',
                  label: 'صحة المحاصيل',
                  icon: Icons.eco_outlined,
                  color: AtmosphereColors.success,
                ),
              ),
              Container(
                width: 1,
                height: 50,
                color: AtmosphereColors.glassBorder,
              ),
              Expanded(
                child: _buildStatItem(
                  value: '+23%',
                  label: 'توفير المياه',
                  icon: Icons.water_drop_outlined,
                  color: AtmosphereColors.info,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem({
    required String value,
    required String label,
    required IconData icon,
    required Color color,
  }) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(width: AtmosphereSpacing.sm),
            Text(
              value,
              style: AtmosphereTypography.displaySmall.copyWith(
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: AtmosphereSpacing.xs),
        Text(
          label,
          style: AtmosphereTypography.bodySmall,
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
