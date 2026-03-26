import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../weather/presentation/providers/weather_provider.dart';

/// ويدجت الطقس المصغر للصفحة الرئيسية
/// Uses weatherProvider for live data with graceful fallback
class WeatherWidget extends ConsumerWidget {
  const WeatherWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final weatherState = ref.watch(weatherProvider);

    // Extract live data or fall back to placeholders
    final String city;
    final String temp;
    final String condition;
    final String humidity;
    final String wind;
    final String uvIndex;

    if (weatherState.data != null) {
      final current = weatherState.data!.current;
      city = 'الموقع الحالي';
      temp = '${current.temperature.round()}';
      condition = current.conditionAr;
      humidity = '${current.humidity}%';
      wind = '${current.windSpeed.toStringAsFixed(0)} km/h';
      uvIndex = current.uvIndex != null ? '${current.uvIndex!.round()}' : '—';
    } else if (weatherState.isLoading) {
      return Card(
        elevation: 3,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Container(
          height: 140,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF367C2B), Color(0xFF2D6623)],
            ),
          ),
          child: const Center(
            child: CircularProgressIndicator(color: Colors.white70),
          ),
        ),
      );
    } else {
      // Fallback for error / no data -- clearly marked
      city = '—';
      temp = '—';
      condition = weatherState.error ?? 'لا توجد بيانات';
      humidity = '—';
      wind = '—';
      uvIndex = '—';
    }

    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF367C2B), Color(0xFF2D6623)],
          ),
        ),
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            // الطقس الحالي
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.location_on, color: Colors.white70, size: 16),
                      const SizedBox(width: 4),
                      Text(
                        city,
                        style: TextStyle(
                          color: Colors.white.withValues(alpha: 0.8),
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        temp,
                        style: const TextStyle(
                          fontSize: 48,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      if (temp != '—')
                        const Text(
                          '°C',
                          style: TextStyle(
                            fontSize: 20,
                            color: Colors.white70,
                          ),
                        ),
                      const Spacer(),
                      const Text(
                        '☀️',
                        style: TextStyle(fontSize: 48),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    condition,
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),

            // تفاصيل إضافية
            Container(
              height: 100,
              width: 1,
              color: Colors.white24,
            ),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildWeatherDetail(
                  icon: Icons.water_drop,
                  value: humidity,
                  label: 'رطوبة',
                ),
                const SizedBox(height: 12),
                _buildWeatherDetail(
                  icon: Icons.air,
                  value: wind,
                  label: 'رياح',
                ),
                const SizedBox(height: 12),
                _buildWeatherDetail(
                  icon: Icons.wb_sunny,
                  value: uvIndex,
                  label: 'UV',
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeatherDetail({
    required IconData icon,
    required String value,
    required String label,
  }) {
    return Row(
      children: [
        Icon(icon, color: Colors.white60, size: 16),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white60,
                fontSize: 10,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
