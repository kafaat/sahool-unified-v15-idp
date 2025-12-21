import 'package:flutter/material.dart';
import '../../domain/entities/weather_entities.dart';

/// قائمة التوقعات الساعية
class HourlyForecastList extends StatelessWidget {
  final List<HourlyForecast> forecasts;

  const HourlyForecastList({
    super.key,
    required this.forecasts,
  });

  @override
  Widget build(BuildContext context) {
    if (forecasts.isEmpty) {
      return const SizedBox.shrink();
    }

    return SizedBox(
      height: 120,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: forecasts.length,
        separatorBuilder: (_, __) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          final forecast = forecasts[index];
          final isNow = index == 0;

          return Container(
            width: 72,
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
            decoration: BoxDecoration(
              color: isNow ? const Color(0xFF367C2B) : Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isNow ? const Color(0xFF367C2B) : Colors.grey[300]!,
              ),
              boxShadow: isNow
                  ? [
                      BoxShadow(
                        color: const Color(0xFF367C2B).withOpacity(0.3),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ]
                  : null,
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Text(
                  isNow ? 'الآن' : forecast.hourDisplay,
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: isNow ? FontWeight.bold : FontWeight.normal,
                    color: isNow ? Colors.white : Colors.grey[600],
                  ),
                ),
                Text(
                  forecast.icon,
                  style: const TextStyle(fontSize: 28),
                ),
                Text(
                  '${forecast.temperature.round()}°',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: isNow ? Colors.white : Colors.black87,
                  ),
                ),
                if (forecast.precipitationChance > 0)
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.water_drop,
                        size: 12,
                        color: isNow ? Colors.white70 : Colors.blue,
                      ),
                      const SizedBox(width: 2),
                      Text(
                        '${forecast.precipitationChance}%',
                        style: TextStyle(
                          fontSize: 10,
                          color: isNow ? Colors.white70 : Colors.blue,
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}
