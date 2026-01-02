// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Weather Widget
// ودجت الطقس
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import '../theme/atmosphere_theme.dart';

class WeatherWidget extends StatelessWidget {
  const WeatherWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AtmosphereSpacing.lg),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AtmosphereColors.warning.withOpacity(0.15),
            AtmosphereColors.warning.withOpacity(0.05),
          ],
        ),
        borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
        border: Border.all(
          color: AtmosphereColors.warning.withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          // Weather Icon
          Container(
            padding: const EdgeInsets.all(AtmosphereSpacing.md),
            decoration: BoxDecoration(
              color: AtmosphereColors.warning.withOpacity(0.2),
              borderRadius: BorderRadius.circular(AtmosphereRadius.md),
            ),
            child: const Icon(
              Icons.wb_sunny,
              color: AtmosphereColors.warning,
              size: 36,
            ),
          ),
          const SizedBox(width: AtmosphereSpacing.lg),

          // Weather Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      '32°C',
                      style: AtmosphereTypography.displayMedium.copyWith(
                        color: AtmosphereColors.textPrimary,
                      ),
                    ),
                    const SizedBox(width: AtmosphereSpacing.md),
                    Text(
                      'مشمس',
                      style: AtmosphereTypography.bodyLarge.copyWith(
                        color: AtmosphereColors.warning,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AtmosphereSpacing.xs),
                Text(
                  'الرياض، السعودية',
                  style: AtmosphereTypography.bodyMedium,
                ),
              ],
            ),
          ),

          // Forecast Mini
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Row(
                children: [
                  Icon(
                    Icons.water_drop,
                    color: AtmosphereColors.info,
                    size: 16,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '15%',
                    style: AtmosphereTypography.bodySmall.copyWith(
                      color: AtmosphereColors.info,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: AtmosphereSpacing.xs),
              Row(
                children: [
                  Icon(
                    Icons.air,
                    color: AtmosphereColors.textMuted,
                    size: 16,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    '12 كم/س',
                    style: AtmosphereTypography.bodySmall,
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}
