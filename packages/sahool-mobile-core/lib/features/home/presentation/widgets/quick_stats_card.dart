import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../logic/home_providers.dart';

/// بطاقة الإحصائيات السريعة
/// Derives stats from dashboardFieldsProvider, pendingTasksCountProvider,
/// and activeAlertsCountProvider instead of hardcoded values.
class QuickStatsCard extends ConsumerWidget {
  const QuickStatsCard({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fieldsCount = ref.watch(activeFieldsCountProvider);
    final totalArea = ref.watch(totalAreaHectaresProvider);
    final pendingTasks = ref.watch(pendingTasksCountProvider);
    final alertsCount = ref.watch(activeAlertsCountProvider);

    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildStatItem(
              icon: Icons.landscape,
              value: '$fieldsCount',
              label: 'حقول',
              color: const Color(0xFF367C2B),
            ),
            _buildDivider(),
            _buildStatItem(
              icon: Icons.straighten,
              value: totalArea > 0 ? '${totalArea.round()}' : '—',
              label: 'هكتار',
              color: Colors.blue,
            ),
            _buildDivider(),
            _buildStatItem(
              icon: Icons.assignment_turned_in,
              value: '$pendingTasks',
              label: 'إجراءات',
              color: Colors.orange,
            ),
            _buildDivider(),
            _buildStatItem(
              icon: Icons.warning,
              value: '$alertsCount',
              label: 'تنبيهات',
              color: Colors.red,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String value,
    required String label,
    required Color color,
  }) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: color, size: 24),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            fontSize: 12,
            color: Colors.grey,
          ),
        ),
      ],
    );
  }

  Widget _buildDivider() {
    return Container(
      height: 50,
      width: 1,
      color: Colors.grey[300],
    );
  }
}
