// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Stats Panel Widget
// لوحة الإحصائيات
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import '../theme/atmosphere_theme.dart';

/// Statistics panel displaying live farm metrics
///
/// Shows key performance indicators including:
/// - Active fields count
/// - Sensors count
/// - Crop health percentage
/// - Water savings percentage
class StatsPanel extends StatelessWidget {
  const StatsPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Farm Statistics Panel - Live Data',
      child: Container(
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
            _buildLiveIndicator(),
            const SizedBox(height: AtmosphereSpacing.md),

            // Stats Grid - First Row
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    value: '1,247',
                    label: 'الحقول النشطة',
                    labelEn: 'Active Fields',
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
                    labelEn: 'Sensors',
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

            // Stats Grid - Second Row
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    value: '94.7%',
                    label: 'صحة المحاصيل',
                    labelEn: 'Crop Health',
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
                    labelEn: 'Water Savings',
                    icon: Icons.water_drop_outlined,
                    color: AtmosphereColors.info,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  /// Build the live indicator header
  Widget _buildLiveIndicator() {
    return Semantics(
      label: 'Data is updating live',
      child: Row(
        children: [
          // Pulsing indicator dot
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
          const SizedBox(width: AtmosphereSpacing.xs),
          ExcludeSemantics(
            child: Text(
              'LIVE',
              style: AtmosphereTypography.labelSmall.copyWith(
                color: AtmosphereColors.success,
                letterSpacing: 2,
                fontSize: 9,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Build a single stat item with icon, value, and label
  Widget _buildStatItem({
    required String value,
    required String label,
    required String labelEn,
    required IconData icon,
    required Color color,
  }) {
    return Semantics(
      label: '$labelEn: $value',
      excludeSemantics: true,
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                color: color,
                size: 20,
                semanticLabel: labelEn,
              ),
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
      ),
    );
  }
}
