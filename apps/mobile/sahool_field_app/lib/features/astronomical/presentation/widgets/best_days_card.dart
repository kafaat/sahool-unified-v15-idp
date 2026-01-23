/// SAHOOL Best Days Card
/// بطاقة أفضل الأيام للنشاط الزراعي

import 'package:flutter/material.dart';
import '../../models/astronomical_models.dart';

/// بطاقة عرض أفضل الأيام
class BestDaysCard extends StatelessWidget {
  final BestDaysResult result;

  const BestDaysCard({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // ملخص البحث
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    Icons.search,
                    color: theme.colorScheme.onPrimaryContainer,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'أفضل أيام ${result.activity}',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'خلال ${result.searchPeriodDays} يوم القادمة',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    '${result.totalFound} يوم',
                    style: const TextStyle(
                      color: Colors.green,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        // قائمة أفضل الأيام
        if (result.bestDays.isEmpty)
          Center(
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Column(
                children: [
                  Icon(
                    Icons.event_busy,
                    size: 64,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'لا توجد أيام مناسبة',
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  Text(
                    'جرب زيادة فترة البحث',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
          )
        else
          ...result.bestDays.asMap().entries.map(
                (entry) => _BestDayTile(
                  day: entry.value,
                  rank: entry.key + 1,
                ),
              ),
      ],
    );
  }
}

class _BestDayTile extends StatelessWidget {
  final BestDay day;
  final int rank;

  const _BestDayTile({
    required this.day,
    required this.rank,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scoreColor = _getScoreColor(day.score);
    final rankColor = _getRankColor(rank);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            // الترتيب
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: rankColor.withOpacity(0.2),
                shape: BoxShape.circle,
                border: Border.all(color: rankColor, width: 2),
              ),
              child: Center(
                child: Text(
                  '$rank',
                  style: TextStyle(
                    color: rankColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            // التفاصيل
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        day.date,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 15,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        day.hijriDate,
                        style: TextStyle(
                          color: theme.colorScheme.onSurfaceVariant,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        Icons.nightlight_round,
                        size: 14,
                        color: Colors.amber.shade600,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        day.moonPhase,
                        style: theme.textTheme.labelSmall,
                      ),
                      const SizedBox(width: 12),
                      Icon(
                        Icons.star,
                        size: 14,
                        color: Colors.purple.shade400,
                      ),
                      const SizedBox(width: 4),
                      Expanded(
                        child: Text(
                          day.lunarMansion,
                          style: theme.textTheme.labelSmall,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    day.reason,
                    style: TextStyle(
                      color: theme.colorScheme.onSurfaceVariant,
                      fontSize: 12,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            // الدرجة
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: scoreColor.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  Text(
                    '${day.score}',
                    style: TextStyle(
                      color: scoreColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                  Text(
                    'درجة',
                    style: TextStyle(
                      color: scoreColor,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getScoreColor(int score) {
    if (score >= 90) return Colors.green.shade700;
    if (score >= 80) return Colors.green;
    if (score >= 70) return Colors.lightGreen;
    if (score >= 60) return Colors.lime;
    return Colors.orange;
  }

  Color _getRankColor(int rank) {
    switch (rank) {
      case 1:
        return Colors.amber.shade700;
      case 2:
        return Colors.grey.shade500;
      case 3:
        return Colors.brown.shade400;
      default:
        return Colors.blueGrey;
    }
  }
}
