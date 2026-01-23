// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Weather Widget
// ودجت الطقس
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import '../theme/atmosphere_theme.dart';

/// Weather widget displaying current conditions
///
/// Shows temperature, weather condition, humidity, and wind speed
/// for the farm location.
class WeatherWidget extends StatelessWidget {
  /// Current temperature in Celsius
  final int temperature;

  /// Weather condition description in Arabic
  final String conditionAr;

  /// Weather condition description in English
  final String conditionEn;

  /// Location name in Arabic
  final String locationAr;

  /// Humidity percentage (0-100)
  final int humidity;

  /// Wind speed in km/h
  final int windSpeed;

  /// Optional callback when the widget is tapped
  final VoidCallback? onTap;

  const WeatherWidget({
    super.key,
    this.temperature = 32,
    this.conditionAr = 'مشمس',
    this.conditionEn = 'Sunny',
    this.locationAr = 'الرياض، السعودية',
    this.humidity = 15,
    this.windSpeed = 12,
    this.onTap,
  });

  /// Build accessibility description
  String get _accessibilityDescription {
    return 'Weather in $locationAr: '
        '$temperature degrees Celsius, $conditionEn, '
        'Humidity $humidity percent, '
        'Wind speed $windSpeed kilometers per hour';
  }

  /// Get weather icon based on condition
  IconData get _weatherIcon {
    final condition = conditionEn.toLowerCase();
    if (condition.contains('sun') || condition.contains('clear')) {
      return Icons.wb_sunny;
    } else if (condition.contains('cloud')) {
      return Icons.cloud;
    } else if (condition.contains('rain')) {
      return Icons.water_drop;
    } else if (condition.contains('storm') || condition.contains('thunder')) {
      return Icons.thunderstorm;
    } else if (condition.contains('wind')) {
      return Icons.air;
    }
    return Icons.wb_sunny;
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: _accessibilityDescription,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(AtmosphereSpacing.lg),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                Color.lerp(Colors.transparent, AtmosphereColors.warning, 0.15)!,
                Color.lerp(Colors.transparent, AtmosphereColors.warning, 0.05)!,
              ],
            ),
            borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
            border: Border.all(
              color: Color.lerp(
                Colors.transparent,
                AtmosphereColors.warning,
                0.3,
              )!,
            ),
          ),
          child: Row(
            children: [
              // Weather Icon
              _buildWeatherIcon(),
              const SizedBox(width: AtmosphereSpacing.lg),

              // Weather Info
              Expanded(
                child: _buildMainInfo(),
              ),

              // Forecast Mini
              _buildSecondaryInfo(),
            ],
          ),
        ),
      ),
    );
  }

  /// Build the main weather icon
  Widget _buildWeatherIcon() {
    return ExcludeSemantics(
      child: Container(
        padding: const EdgeInsets.all(AtmosphereSpacing.md),
        decoration: BoxDecoration(
          color: Color.lerp(
            Colors.transparent,
            AtmosphereColors.warning,
            0.2,
          ),
          borderRadius: BorderRadius.circular(AtmosphereRadius.md),
        ),
        child: Icon(
          _weatherIcon,
          color: AtmosphereColors.warning,
          size: 36,
          semanticLabel: conditionEn,
        ),
      ),
    );
  }

  /// Build the main temperature and condition info
  Widget _buildMainInfo() {
    return ExcludeSemantics(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                '$temperature°C',
                style: AtmosphereTypography.displayMedium.copyWith(
                  color: AtmosphereColors.textPrimary,
                ),
              ),
              const SizedBox(width: AtmosphereSpacing.md),
              Flexible(
                child: Text(
                  conditionAr,
                  style: AtmosphereTypography.bodyLarge.copyWith(
                    color: AtmosphereColors.warning,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: AtmosphereSpacing.xs),
          Text(
            locationAr,
            style: AtmosphereTypography.bodyMedium,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  /// Build the secondary info (humidity and wind)
  Widget _buildSecondaryInfo() {
    return ExcludeSemantics(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // Humidity
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.water_drop,
                color: AtmosphereColors.info,
                size: 16,
                semanticLabel: 'Humidity',
              ),
              const SizedBox(width: 4),
              Text(
                '$humidity%',
                style: AtmosphereTypography.bodySmall.copyWith(
                  color: AtmosphereColors.info,
                ),
              ),
            ],
          ),
          const SizedBox(height: AtmosphereSpacing.xs),
          // Wind Speed
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(
                Icons.air,
                color: AtmosphereColors.textMuted,
                size: 16,
                semanticLabel: 'Wind speed',
              ),
              const SizedBox(width: 4),
              Text(
                '$windSpeed كم/س',
                style: AtmosphereTypography.bodySmall,
              ),
            ],
          ),
        ],
      ),
    );
  }
}
