import 'package:flutter/material.dart';
import '../../domain/entities/weather_entities.dart';

/// قائمة التوقعات اليومية
class DailyForecastList extends StatelessWidget {
  final List<DailyForecast> forecasts;

  const DailyForecastList({
    super.key,
    required this.forecasts,
  });

  @override
  Widget build(BuildContext context) {
    if (forecasts.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            for (int i = 0; i < forecasts.length; i++) ...[
              _buildDayRow(context, forecasts[i], isToday: i == 0),
              if (i < forecasts.length - 1)
                const Divider(height: 24),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildDayRow(
    BuildContext context,
    DailyForecast forecast, {
    bool isToday = false,
  }) {
    return Row(
      children: [
        // اليوم
        SizedBox(
          width: 80,
          child: Text(
            isToday ? 'اليوم' : forecast.dayName,
            style: TextStyle(
              fontWeight: isToday ? FontWeight.bold : FontWeight.normal,
              color: isToday ? const Color(0xFF367C2B) : Colors.black87,
            ),
          ),
        ),

        // نسبة الأمطار
        SizedBox(
          width: 50,
          child: forecast.precipitationChance > 0
              ? Row(
                  children: [
                    const Icon(Icons.water_drop, size: 14, color: Colors.blue),
                    const SizedBox(width: 2),
                    Text(
                      '${forecast.precipitationChance}%',
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.blue,
                      ),
                    ),
                  ],
                )
              : const SizedBox.shrink(),
        ),

        // الأيقونة
        Expanded(
          child: Center(
            child: Text(
              forecast.icon,
              style: const TextStyle(fontSize: 28),
            ),
          ),
        ),

        // درجات الحرارة
        Row(
          children: [
            Text(
              '${forecast.tempMax.round()}°',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '${forecast.tempMin.round()}°',
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 16,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
