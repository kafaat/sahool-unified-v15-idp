/// SAHOOL Today Astronomical Card
/// بطاقة البيانات الفلكية لليوم

import 'package:flutter/material.dart';
import '../../models/astronomical_models.dart';

/// بطاقة عرض البيانات الفلكية لليوم
class TodayCard extends StatelessWidget {
  final DailyAstronomicalData data;

  const TodayCard({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scoreColor = _getScoreColor(data.overallFarmingScore);

    return Card(
      elevation: 4,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // الرأس مع التاريخ والدرجة
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: theme.colorScheme.primaryContainer,
              borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      data.dateGregorian,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${data.dateHijri.day} ${data.dateHijri.monthName} ${data.dateHijri.year}',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onPrimaryContainer.withOpacity(0.8),
                      ),
                    ),
                  ],
                ),
                // درجة الزراعة
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: scoreColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: scoreColor, width: 2),
                  ),
                  child: Column(
                    children: [
                      Text(
                        '${data.overallFarmingScore}',
                        style: theme.textTheme.headlineMedium?.copyWith(
                          color: scoreColor,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'درجة الزراعة',
                        style: theme.textTheme.labelSmall?.copyWith(
                          color: scoreColor,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          // المحتوى
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // طور القمر والمنزلة
                Row(
                  children: [
                    Expanded(
                      child: _InfoTile(
                        icon: Icons.nightlight_round,
                        iconColor: Colors.amber,
                        title: 'طور القمر',
                        value: data.moonPhase.name,
                        subtitle: '${(data.moonPhase.illumination * 100).toInt()}% إضاءة',
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _InfoTile(
                        icon: Icons.star,
                        iconColor: Colors.purple,
                        title: 'المنزلة',
                        value: data.lunarMansion.name,
                        subtitle: 'رقم ${data.lunarMansion.number}',
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                // البرج والموسم
                Row(
                  children: [
                    Expanded(
                      child: _InfoTile(
                        icon: Icons.auto_awesome,
                        iconColor: Colors.indigo,
                        title: 'البرج',
                        value: data.zodiac.name,
                        subtitle: data.zodiac.element,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _InfoTile(
                        icon: Icons.wb_sunny,
                        iconColor: Colors.orange,
                        title: 'الموسم',
                        value: data.season.name,
                        subtitle: '',
                      ),
                    ),
                  ],
                ),
                // التوصيات
                if (data.recommendations.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  const Divider(),
                  const SizedBox(height: 8),
                  Text(
                    'التوصيات الزراعية',
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ...data.recommendations.take(3).map((rec) => _RecommendationTile(
                        activity: rec.activity,
                        suitability: rec.suitability,
                        score: rec.suitabilityScore,
                      )),
                ],
              ],
            ),
          ),
        ],
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

class _InfoTile extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String value;
  final String subtitle;

  const _InfoTile({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.value,
    required this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.5),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 18, color: iconColor),
              const SizedBox(width: 6),
              Text(
                title,
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: theme.textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          if (subtitle.isNotEmpty)
            Text(
              subtitle,
              style: theme.textTheme.labelSmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
        ],
      ),
    );
  }
}

class _RecommendationTile extends StatelessWidget {
  final String activity;
  final String suitability;
  final int score;

  const _RecommendationTile({
    required this.activity,
    required this.suitability,
    required this.score,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = _getSuitabilityColor(score);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              activity,
              style: theme.textTheme.bodyMedium,
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              suitability,
              style: theme.textTheme.labelSmall?.copyWith(
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getSuitabilityColor(int score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.lightGreen;
    if (score >= 40) return Colors.orange;
    return Colors.red;
  }
}
