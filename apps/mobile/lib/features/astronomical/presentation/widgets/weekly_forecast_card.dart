/// SAHOOL Weekly Forecast Card
/// بطاقة التوقعات الأسبوعية

import 'package:flutter/material.dart';
import '../../models/astronomical_models.dart';

/// بطاقة عرض التوقعات الأسبوعية
class WeeklyForecastCard extends StatelessWidget {
  final WeeklyForecast forecast;

  const WeeklyForecastCard({super.key, required this.forecast});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // ملخص الأسبوع
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.calendar_month,
                        color: theme.colorScheme.primary),
                    const SizedBox(width: 8),
                    Text(
                      'ملخص الأسبوع',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  '${forecast.startDate} - ${forecast.endDate}',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                const Divider(height: 24),
                // أفضل أيام الزراعة
                if (forecast.bestPlantingDays.isNotEmpty) ...[
                  _DaysList(
                    icon: Icons.grass,
                    title: 'أفضل أيام الزراعة',
                    days: forecast.bestPlantingDays,
                    color: Colors.green,
                  ),
                  const SizedBox(height: 12),
                ],
                // أفضل أيام الحصاد
                if (forecast.bestHarvestingDays.isNotEmpty) ...[
                  _DaysList(
                    icon: Icons.agriculture,
                    title: 'أفضل أيام الحصاد',
                    days: forecast.bestHarvestingDays,
                    color: Colors.amber,
                  ),
                  const SizedBox(height: 12),
                ],
                // الأيام غير المناسبة
                if (forecast.avoidDays.isNotEmpty) ...[
                  _DaysList(
                    icon: Icons.do_not_disturb,
                    title: 'أيام يُتجنب العمل فيها',
                    days: forecast.avoidDays,
                    color: Colors.red,
                  ),
                ],
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        // قائمة الأيام
        Text(
          'تفاصيل الأيام',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        ...forecast.days.map((day) => _DayCard(day: day)),
      ],
    );
  }
}

class _DaysList extends StatelessWidget {
  final IconData icon;
  final String title;
  final List<String> days;
  final Color color;

  const _DaysList({
    required this.icon,
    required this.title,
    required this.days,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, size: 18, color: color),
            const SizedBox(width: 8),
            Text(
              title,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: days
              .map((day) => Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: color.withOpacity(0.3)),
                    ),
                    child: Text(
                      day,
                      style: TextStyle(
                        color: color,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ))
              .toList(),
        ),
      ],
    );
  }
}

class _DayCard extends StatelessWidget {
  final DailyAstronomicalData day;

  const _DayCard({required this.day});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scoreColor = _getScoreColor(day.overallFarmingScore);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          width: 50,
          height: 50,
          decoration: BoxDecoration(
            color: scoreColor.withOpacity(0.2),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Center(
            child: Text(
              '${day.overallFarmingScore}',
              style: TextStyle(
                color: scoreColor,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        title: Text(
          day.dateGregorian,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${day.dateHijri.day} ${day.dateHijri.monthName}',
              style: TextStyle(
                color: theme.colorScheme.onSurfaceVariant,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                Text(
                  day.moonPhase.icon,
                  style: const TextStyle(fontSize: 14),
                ),
                const SizedBox(width: 4),
                Text(
                  day.moonPhase.name,
                  style: theme.textTheme.labelSmall,
                ),
                const SizedBox(width: 8),
                Icon(Icons.star, size: 14, color: Colors.purple.shade300),
                const SizedBox(width: 4),
                Text(
                  day.lunarMansion.name,
                  style: theme.textTheme.labelSmall,
                ),
              ],
            ),
          ],
        ),
        trailing: Icon(
          Icons.chevron_right,
          color: theme.colorScheme.onSurfaceVariant,
        ),
      ),
    );
  }

  Color _getScoreColor(int score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.lightGreen;
    if (score >= 40) return Colors.orange;
    return Colors.red;
  }
}
