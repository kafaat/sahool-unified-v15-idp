/// Weather Card Widget - ودجت بطاقة الطقس
/// Summary card for weather information
library;

import 'package:flutter/material.dart';
import '../data/models/weather_data.dart';

class WeatherCard extends StatelessWidget {
  final WeatherSummary weather;
  final VoidCallback? onTap;

  const WeatherCard({
    super.key,
    required this.weather,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFF2196F3), Color(0xFF64B5F6)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  isArabic ? 'الطقس' : 'Weather',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                if (onTap != null)
                  const Icon(Icons.arrow_forward_ios, size: 16, color: Colors.white70),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  _getWeatherIcon(weather.condition),
                  size: 48,
                  color: Colors.white,
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${weather.temperature.toStringAsFixed(1)}°C',
                        style: const TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      Text(
                        isArabic ? weather.conditionAr : weather.condition,
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.white70,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildWeatherStat(
                  Icons.water_drop,
                  '${weather.humidity.toStringAsFixed(0)}%',
                  isArabic ? 'الرطوبة' : 'Humidity',
                ),
                _buildWeatherStat(
                  Icons.opacity,
                  '${weather.precipitation.toStringAsFixed(1)}mm',
                  isArabic ? 'الأمطار' : 'Rain',
                ),
                _buildWeatherStat(
                  Icons.waves,
                  '${weather.et0.toStringAsFixed(1)}mm',
                  'ET0',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeatherStat(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 10,
          ),
        ),
      ],
    );
  }

  IconData _getWeatherIcon(String condition) {
    switch (condition.toLowerCase()) {
      case 'sunny':
      case 'clear':
      case 'صافي':
        return Icons.wb_sunny;
      case 'cloudy':
      case 'غائم':
        return Icons.cloud;
      case 'rainy':
      case 'rain':
      case 'ممطر':
        return Icons.water_drop;
      case 'partly cloudy':
      case 'غائم جزئياً':
        return Icons.wb_cloudy;
      default:
        return Icons.wb_cloudy;
    }
  }
}
