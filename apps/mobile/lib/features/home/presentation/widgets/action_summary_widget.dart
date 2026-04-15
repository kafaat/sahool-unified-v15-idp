import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../tasks/providers/tasks_provider.dart';
import '../../../tasks/domain/entities/task.dart';

/// ويدجت ملخص الإجراءات
/// Loads pending tasks from tasksProvider instead of hardcoded list
class ActionSummaryWidget extends ConsumerWidget {
  const ActionSummaryWidget({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tasksAsync = ref.watch(tasksProvider);

    return tasksAsync.when(
      loading: () => const SizedBox(
        height: 120,
        child: Center(child: CircularProgressIndicator()),
      ),
      error: (err, _) => Card(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Center(
            child: Column(
              children: [
                const Icon(Icons.error_outline, size: 48, color: Colors.red),
                const SizedBox(height: 12),
                Text('خطأ في تحميل الإجراءات: ${err.toString().length > 40 ? '${err.toString().substring(0, 40)}...' : err.toString()}'),
              ],
            ),
          ),
        ),
      ),
      data: (allTasks) {
        // Filter to pending / in-progress tasks
        final actions = allTasks
            .where((t) =>
                t.status == TaskStatus.open ||
                t.status == TaskStatus.inProgress)
            .toList()
          ..sort((a, b) => (a.priority.index).compareTo(b.priority.index));

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

        // Count by priority
        final urgentCount = actions.where((t) => t.priority == TaskPriority.urgent).length;
        final highCount = actions.where((t) => t.priority == TaskPriority.high).length;
        final mediumCount = actions.where((t) => t.priority == TaskPriority.medium || t.priority == TaskPriority.low).length;

        return Column(
          children: [
            // شريط الملخص
            Card(
              color: const Color(0xFF367C2B).withValues(alpha: 0.1),
              elevation: 0,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildSummaryItem('🔴', '$urgentCount', 'عاجل'),
                    _buildSummaryItem('🟠', '$highCount', 'مهم'),
                    _buildSummaryItem('🔵', '$mediumCount', 'متوسط'),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 12),

            // قائمة الإجراءات (top 3)
            ...actions.take(3).map((task) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: _buildTaskTile(context, task),
                )),

            // زر عرض الكل
            TextButton(
              onPressed: () {
                context.push('/tasks');
              },
              child: const Text('عرض جميع الإجراءات'),
            ),
          ],
        );
      },
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

  Widget _buildTaskTile(BuildContext context, FieldTask task) {
    final priorityColor = _getPriorityColor(task.priority);
    final priorityLabel = _getPriorityLabel(task.priority);
    final icon = _getTaskIcon(task.title);

    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(10),
        side: BorderSide(color: priorityColor.withValues(alpha: 0.3)),
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: priorityColor.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Center(
            child: Text(
              icon,
              style: const TextStyle(fontSize: 20),
            ),
          ),
        ),
        title: Text(
          task.title,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
        ),
        subtitle: Row(
          children: [
            Icon(Icons.location_on, size: 12, color: Colors.grey[600]),
            const SizedBox(width: 2),
            Flexible(
              child: Text(
                task.fieldId,
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            if (task.dueDate != null) ...[
              const SizedBox(width: 8),
              Icon(Icons.schedule, size: 12, color: Colors.grey[600]),
              const SizedBox(width: 2),
              Text(
                _formatDueDate(task.dueDate!),
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: priorityColor,
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(
            priorityLabel,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 11,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        onTap: () {
          context.push('/task/${task.id}');
        },
      ),
    );
  }

  String _formatDueDate(DateTime dueDate) {
    final now = DateTime.now();
    final diff = dueDate.difference(now);
    if (diff.isNegative) return 'متأخر';
    if (diff.inHours < 1) return '${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return '${diff.inHours} ساعة';
    return '${diff.inDays} يوم';
  }

  String _getTaskIcon(String title) {
    final lower = title.toLowerCase();
    if (lower.contains('ري') || lower.contains('irrigation')) return '💧';
    if (lower.contains('تسميد') || lower.contains('fertiliz')) return '🌱';
    if (lower.contains('فحص') || lower.contains('scout')) return '🔍';
    if (lower.contains('رش') || lower.contains('spray')) return '🧴';
    if (lower.contains('حصاد') || lower.contains('harvest')) return '🌾';
    return '📋';
  }

  Color _getPriorityColor(TaskPriority priority) {
    switch (priority) {
      case TaskPriority.urgent:
        return Colors.red;
      case TaskPriority.high:
        return Colors.orange;
      case TaskPriority.medium:
        return Colors.blue;
      case TaskPriority.low:
        return Colors.grey;
    }
  }

  String _getPriorityLabel(TaskPriority priority) {
    switch (priority) {
      case TaskPriority.urgent:
        return 'P0';
      case TaskPriority.high:
        return 'P1';
      case TaskPriority.medium:
        return 'P2';
      case TaskPriority.low:
        return 'P3';
    }
  }
}
