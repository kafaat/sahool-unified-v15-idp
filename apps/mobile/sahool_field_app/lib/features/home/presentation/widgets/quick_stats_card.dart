import 'package:flutter/material.dart';

/// بطاقة الإحصائيات السريعة
class QuickStatsCard extends StatelessWidget {
  const QuickStatsCard({super.key});

  @override
  Widget build(BuildContext context) {
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
              value: '3',
              label: 'حقول',
              color: const Color(0xFF367C2B),
            ),
            _buildDivider(),
            _buildStatItem(
              icon: Icons.straighten,
              value: '106',
              label: 'هكتار',
              color: Colors.blue,
            ),
            _buildDivider(),
            _buildStatItem(
              icon: Icons.assignment_turned_in,
              value: '5',
              label: 'إجراءات',
              color: Colors.orange,
            ),
            _buildDivider(),
            _buildStatItem(
              icon: Icons.warning,
              value: '2',
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
            color: color.withOpacity(0.1),
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
