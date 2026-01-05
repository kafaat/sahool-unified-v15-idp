/// SAHOOL Moon Phase Card
/// بطاقة طور القمر

import 'package:flutter/material.dart';
import '../../models/astronomical_models.dart';

/// بطاقة عرض طور القمر
class MoonPhaseCard extends StatelessWidget {
  final MoonPhase moonPhase;

  const MoonPhaseCard({super.key, required this.moonPhase});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // أيقونة القمر
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Colors.grey.shade800,
                    Colors.grey.shade900,
                  ],
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.amber.withOpacity(0.3),
                    blurRadius: 20,
                    spreadRadius: 5,
                  ),
                ],
              ),
              child: Center(
                child: Text(
                  moonPhase.icon,
                  style: const TextStyle(fontSize: 60),
                ),
              ),
            ),
            const SizedBox(height: 20),
            // اسم الطور
            Text(
              moonPhase.name,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              moonPhase.nameEn,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 20),
            // معلومات إضافية
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _InfoColumn(
                  icon: Icons.brightness_7,
                  label: 'الإضاءة',
                  value: '${(moonPhase.illumination * 100).toInt()}%',
                ),
                _InfoColumn(
                  icon: Icons.calendar_today,
                  label: 'عمر القمر',
                  value: '${moonPhase.ageDays.toInt()} يوم',
                ),
                _InfoColumn(
                  icon: moonPhase.isWaxing
                      ? Icons.trending_up
                      : Icons.trending_down,
                  label: 'الاتجاه',
                  value: moonPhase.isWaxing ? 'متصاعد' : 'متناقص',
                ),
              ],
            ),
            const SizedBox(height: 16),
            // مناسب للزراعة؟
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: moonPhase.farmingGood
                    ? Colors.green.withOpacity(0.2)
                    : Colors.orange.withOpacity(0.2),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    moonPhase.farmingGood ? Icons.check_circle : Icons.info,
                    color: moonPhase.farmingGood ? Colors.green : Colors.orange,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    moonPhase.farmingGood
                        ? 'مناسب للزراعة'
                        : 'غير مثالي للزراعة',
                    style: TextStyle(
                      color:
                          moonPhase.farmingGood ? Colors.green : Colors.orange,
                      fontWeight: FontWeight.bold,
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
}

class _InfoColumn extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoColumn({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      children: [
        Icon(icon, color: theme.colorScheme.primary),
        const SizedBox(height: 4),
        Text(
          label,
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        Text(
          value,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}
