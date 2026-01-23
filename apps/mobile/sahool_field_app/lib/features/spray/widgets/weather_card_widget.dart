/// Weather Card Widget - بطاقة الطقس
/// عرض معلومات الطقس الحالية وملاءمة الرش
library;

import 'package:flutter/material.dart';

import '../models/spray_models.dart';

class WeatherCardWidget extends StatelessWidget {
  final WeatherCondition weather;
  final String locale;
  final VoidCallback? onTap;

  const WeatherCardWidget({
    Key? key,
    required this.weather,
    this.locale = 'ar',
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isArabic = locale == 'ar';
    final suitabilityScore = weather.spraySuitabilityScore;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header: Condition & Time
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Icon(
                        _getWeatherIcon(weather.condition),
                        size: 32,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(width: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            weather.getCondition(locale),
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            _formatTime(weather.timestamp, isArabic),
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurface.withOpacity(0.6),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                  // Spray Suitability Indicator
                  _buildSuitabilityIndicator(suitabilityScore, theme, isArabic),
                ],
              ),
              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 16),
              // Weather Details Grid
              Row(
                children: [
                  Expanded(
                    child: _buildWeatherDetail(
                      icon: Icons.thermostat,
                      label: isArabic ? 'الحرارة' : 'Temperature',
                      value: '${weather.temperature.toStringAsFixed(1)}°C',
                      theme: theme,
                    ),
                  ),
                  Expanded(
                    child: _buildWeatherDetail(
                      icon: Icons.water_drop,
                      label: isArabic ? 'الرطوبة' : 'Humidity',
                      value: '${weather.humidity.toStringAsFixed(0)}%',
                      theme: theme,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildWeatherDetail(
                      icon: Icons.air,
                      label: isArabic ? 'الرياح' : 'Wind',
                      value: '${weather.windSpeed.toStringAsFixed(1)} km/h',
                      subtitle: weather.getWindDirection(locale),
                      theme: theme,
                    ),
                  ),
                  Expanded(
                    child: _buildWeatherDetail(
                      icon: Icons.umbrella,
                      label: isArabic ? 'المطر' : 'Rain',
                      value: '${weather.rainProbability.toStringAsFixed(0)}%',
                      theme: theme,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSuitabilityIndicator(int score, ThemeData theme, bool isArabic) {
    Color color;
    String label;
    IconData icon;

    if (score >= 80) {
      color = Colors.green;
      label = isArabic ? 'ممتاز' : 'Excellent';
      icon = Icons.check_circle;
    } else if (score >= 60) {
      color = Colors.lightGreen;
      label = isArabic ? 'جيد' : 'Good';
      icon = Icons.check_circle_outline;
    } else if (score >= 40) {
      color = Colors.orange;
      label = isArabic ? 'حذر' : 'Caution';
      icon = Icons.warning_amber;
    } else {
      color = Colors.red;
      label = isArabic ? 'تجنب' : 'Avoid';
      icon = Icons.cancel;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color, width: 2),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 6),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
              Text(
                '$score/100',
                style: TextStyle(
                  color: color,
                  fontSize: 10,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildWeatherDetail({
    required IconData icon,
    required String label,
    required String value,
    String? subtitle,
    required ThemeData theme,
  }) {
    return Column(
      children: [
        Icon(icon, color: theme.colorScheme.primary, size: 24),
        const SizedBox(height: 4),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurface.withOpacity(0.6),
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: theme.textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        if (subtitle != null) ...[
          const SizedBox(height: 2),
          Text(
            subtitle,
            style: theme.textTheme.bodySmall?.copyWith(
              fontSize: 10,
              color: theme.colorScheme.onSurface.withOpacity(0.5),
            ),
          ),
        ],
      ],
    );
  }

  IconData _getWeatherIcon(String condition) {
    switch (condition.toLowerCase()) {
      case 'clear':
      case 'sunny':
        return Icons.wb_sunny;
      case 'cloudy':
      case 'partly_cloudy':
        return Icons.cloud;
      case 'rainy':
      case 'rain':
        return Icons.umbrella;
      case 'stormy':
      case 'thunderstorm':
        return Icons.thunderstorm;
      case 'windy':
        return Icons.air;
      case 'foggy':
      case 'mist':
        return Icons.blur_on;
      default:
        return Icons.wb_cloudy;
    }
  }

  String _formatTime(DateTime time, bool isArabic) {
    final hour = time.hour;
    final minute = time.minute.toString().padLeft(2, '0');
    final period = hour >= 12 ? (isArabic ? 'م' : 'PM') : (isArabic ? 'ص' : 'AM');
    final displayHour = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);

    return '$displayHour:$minute $period';
  }
}

/// Compact Weather Card for lists
class CompactWeatherCard extends StatelessWidget {
  final WeatherCondition weather;
  final String locale;

  const CompactWeatherCard({
    Key? key,
    required this.weather,
    this.locale = 'ar',
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isArabic = locale == 'ar';

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: theme.colorScheme.outline.withOpacity(0.2),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildCompactDetail(
            icon: Icons.thermostat,
            value: '${weather.temperature.toStringAsFixed(0)}°C',
            theme: theme,
          ),
          _buildCompactDetail(
            icon: Icons.water_drop,
            value: '${weather.humidity.toStringAsFixed(0)}%',
            theme: theme,
          ),
          _buildCompactDetail(
            icon: Icons.air,
            value: '${weather.windSpeed.toStringAsFixed(0)} km/h',
            theme: theme,
          ),
          _buildCompactDetail(
            icon: Icons.umbrella,
            value: '${weather.rainProbability.toStringAsFixed(0)}%',
            theme: theme,
          ),
        ],
      ),
    );
  }

  Widget _buildCompactDetail({
    required IconData icon,
    required String value,
    required ThemeData theme,
  }) {
    return Row(
      children: [
        Icon(icon, size: 16, color: theme.colorScheme.primary),
        const SizedBox(width: 4),
        Text(
          value,
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}
