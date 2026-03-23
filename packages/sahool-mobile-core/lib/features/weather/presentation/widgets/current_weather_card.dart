import 'package:flutter/material.dart';
import '../../domain/entities/weather_entities.dart';

/// بطاقة الطقس الحالي
class CurrentWeatherCard extends StatelessWidget {
  final CurrentWeather weather;

  const CurrentWeatherCard({
    super.key,
    required this.weather,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF367C2B), Color(0xFF2D6623)],
          ),
        ),
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // الأيقونة ودرجة الحرارة
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  weather.icon,
                  style: const TextStyle(fontSize: 64),
                ),
                const SizedBox(width: 16),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      weather.temperatureDisplay,
                      style: const TextStyle(
                        fontSize: 56,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    Text(
                      weather.conditionAr,
                      style: const TextStyle(
                        fontSize: 18,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ],
            ),

            const SizedBox(height: 24),

            // التفاصيل
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildDetailItem(
                  icon: Icons.thermostat,
                  label: 'الشعور',
                  value: '${weather.feelsLike.round()}°',
                ),
                _buildDetailItem(
                  icon: Icons.water_drop,
                  label: 'الرطوبة',
                  value: '${weather.humidity}%',
                ),
                _buildDetailItem(
                  icon: Icons.air,
                  label: 'الرياح',
                  value: '${weather.windSpeed.round()} km/h',
                ),
                if (weather.uvIndex != null)
                  _buildDetailItem(
                    icon: Icons.wb_sunny,
                    label: 'UV',
                    value: weather.uvIndex!.round().toString(),
                  ),
              ],
            ),

            if (weather.precipitation != null && weather.precipitation! > 0) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.water, color: Colors.white, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      '${weather.precipitation!.toStringAsFixed(1)} mm هطول',
                      style: const TextStyle(color: Colors.white),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDetailItem({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white60,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}
