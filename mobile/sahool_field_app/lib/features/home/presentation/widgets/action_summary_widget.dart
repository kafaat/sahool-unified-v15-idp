import 'package:flutter/material.dart';

/// ويدجت ملخص الإجراءات
class ActionSummaryWidget extends StatelessWidget {
  const ActionSummaryWidget({super.key});

  @override
  Widget build(BuildContext context) {
    // Demo data - في الإنتاج سيكون من Provider
    final actions = [
      {
        'type': 'irrigation',
        'icon': '💧',
        'title': 'ري حقل القمح الشمالي',
        'priority': 'P0',
        'field': 'حقل القمح الشمالي',
        'timeWindow': '4 ساعات',
      },
      {
        'type': 'fertilization',
        'icon': '🌱',
        'title': 'تسميد حقل الشعير',
        'priority': 'P1',
        'field': 'حقل الشعير الغربي',
        'timeWindow': '24 ساعة',
      },
      {
        'type': 'scouting',
        'icon': '🔍',
        'title': 'فحص منطقة الضعف',
        'priority': 'P1',
        'field': 'حقل البرسيم',
        'timeWindow': '48 ساعة',
      },
    ];

    if (actions.isEmpty) {
      return Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: const Padding(
          padding: EdgeInsets.all(24),
          child: Center(
            child: Column(
              children: [
                Icon(Icons.check_circle, size: 48, color: Colors.green),
                SizedBox(height: 12),
                Text('لا توجد إجراءات مطلوبة'),
              ],
            ),
          ),
        ),
      );
    }

    return Column(
      children: [
        // شريط الملخص
        Card(
          color: const Color(0xFF367C2B).withOpacity(0.1),
          elevation: 0,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildSummaryItem('🔴', '1', 'عاجل'),
                _buildSummaryItem('🟠', '2', 'مهم'),
                _buildSummaryItem('🔵', '2', 'متوسط'),
              ],
            ),
          ),
        ),

        const SizedBox(height: 12),

        // قائمة الإجراءات
        ...actions.take(3).map((action) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: _buildActionTile(context, action),
            )),

        // زر عرض الكل
        TextButton(
          onPressed: () {
            // TODO: Navigate to all actions
          },
          child: const Text('عرض جميع الإجراءات'),
        ),
      ],
    );
  }

  Widget _buildSummaryItem(String emoji, String count, String label) {
    return Column(
      children: [
        Row(
          children: [
            Text(emoji, style: const TextStyle(fontSize: 16)),
            const SizedBox(width: 4),
            Text(
              count,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
          ],
        ),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Colors.grey),
        ),
      ],
    );
  }

  Widget _buildActionTile(BuildContext context, Map<String, dynamic> action) {
    final priorityColor = _getPriorityColor(action['priority'] as String);

    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
        side: BorderSide(color: priorityColor.withOpacity(0.3)),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: priorityColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Center(
            child: Text(
              action['icon'] as String,
              style: const TextStyle(fontSize: 20),
            ),
          ),
        ),
        title: Text(
          action['title'] as String,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
        ),
        subtitle: Row(
          children: [
            Icon(Icons.location_on, size: 12, color: Colors.grey[600]),
            const SizedBox(width: 2),
            Text(
              action['field'] as String,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
            const SizedBox(width: 8),
            Icon(Icons.schedule, size: 12, color: Colors.grey[600]),
            const SizedBox(width: 2),
            Text(
              action['timeWindow'] as String,
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: priorityColor,
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            action['priority'] as String,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        onTap: () {
          // TODO: Navigate to action details
        },
      ),
    );
  }

  Color _getPriorityColor(String priority) {
    switch (priority) {
      case 'P0':
        return Colors.red;
      case 'P1':
        return Colors.orange;
      case 'P2':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }
}
