/// SAHOOL Lunar Mansion Card
/// بطاقة المنزلة القمرية

import 'package:flutter/material.dart';
import '../../models/astronomical_models.dart';

/// بطاقة عرض المنزلة القمرية
class LunarMansionCard extends StatelessWidget {
  final LunarMansion mansion;

  const LunarMansionCard({super.key, required this.mansion});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final scoreColor = _getScoreColor(mansion.farmingScore);

    return Card(
      elevation: 4,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // الرأس
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  Colors.purple.shade700,
                  Colors.purple.shade900,
                ],
              ),
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(12)),
            ),
            child: Row(
              children: [
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      '${mansion.number}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        mansion.name,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        mansion.nameEn,
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.8),
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                // درجة الزراعة
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: scoreColor.withOpacity(0.3),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: scoreColor, width: 2),
                  ),
                  child: Column(
                    children: [
                      Text(
                        '${mansion.farmingScore}',
                        style: TextStyle(
                          color: scoreColor,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        'الزراعة',
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
          // المحتوى
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // البرج والعنصر
                Row(
                  children: [
                    Expanded(
                      child: _InfoChip(
                        icon: Icons.auto_awesome,
                        label: 'البرج',
                        value: mansion.constellation,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: _InfoChip(
                        icon: Icons.blur_circular,
                        label: 'العنصر',
                        value: mansion.element,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                // الوصف
                Text(
                  mansion.description,
                  style: theme.textTheme.bodyMedium,
                ),
                const SizedBox(height: 16),
                // المحاصيل المناسبة
                if (mansion.crops.isNotEmpty) ...[
                  _SectionTitle(
                    icon: Icons.grass,
                    title: 'المحاصيل المناسبة',
                    color: Colors.green,
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: mansion.crops
                        .map((crop) => Chip(
                              label: Text(crop),
                              backgroundColor:
                                  Colors.green.withOpacity(0.1),
                            ))
                        .toList(),
                  ),
                ],
                const SizedBox(height: 16),
                // الأنشطة المناسبة
                if (mansion.activities.isNotEmpty) ...[
                  _SectionTitle(
                    icon: Icons.agriculture,
                    title: 'الأنشطة المناسبة',
                    color: Colors.blue,
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: mansion.activities
                        .map((activity) => Chip(
                              label: Text(activity),
                              backgroundColor: Colors.blue.withOpacity(0.1),
                            ))
                        .toList(),
                  ),
                ],
                const SizedBox(height: 16),
                // ما يجب تجنبه
                if (mansion.avoid.isNotEmpty) ...[
                  _SectionTitle(
                    icon: Icons.do_not_disturb,
                    title: 'يُتجنب',
                    color: Colors.red,
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: mansion.avoid
                        .map((item) => Chip(
                              label: Text(item),
                              backgroundColor: Colors.red.withOpacity(0.1),
                            ))
                        .toList(),
                  ),
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

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoChip({
    required this.icon,
    required this.label,
    required this.value,
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
      child: Row(
        children: [
          Icon(icon, size: 20, color: theme.colorScheme.primary),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: theme.textTheme.labelSmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              Text(
                value,
                style: theme.textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final IconData icon;
  final String title;
  final Color color;

  const _SectionTitle({
    required this.icon,
    required this.title,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
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
    );
  }
}
