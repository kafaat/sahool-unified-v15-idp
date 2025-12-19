import 'package:flutter/material.dart';

/// ويدجت الطقس المصغر للصفحة الرئيسية
class WeatherWidget extends StatelessWidget {
  const WeatherWidget({super.key});

  @override
  Widget build(BuildContext context) {
    // Demo data - في الإنتاج سيكون من Provider
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
                        'الرياض',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.8),
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '32',
                        style: TextStyle(
                          fontSize: 48,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
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
                  const Text(
                    'صافي',
                    style: TextStyle(
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
                  value: '25%',
                  label: 'رطوبة',
                ),
                const SizedBox(height: 12),
                _buildWeatherDetail(
                  icon: Icons.air,
                  value: '12 km/h',
                  label: 'رياح',
                ),
                const SizedBox(height: 12),
                _buildWeatherDetail(
                  icon: Icons.wb_sunny,
                  value: '8',
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
