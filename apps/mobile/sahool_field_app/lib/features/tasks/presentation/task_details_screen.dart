import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/config/theme.dart';
import '../domain/entities/task.dart';
import '../providers/tasks_provider.dart';
import 'complete_task_screen.dart';

/// Task Details Screen - View and manage single task
class TaskDetailsScreen extends ConsumerWidget {
  final String taskId;

  const TaskDetailsScreen({super.key, required this.taskId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tasksState = ref.watch(tasksProvider);

    return tasksState.when(
      loading: () => const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      ),
      error: (error, _) => Scaffold(
        appBar: AppBar(title: const Text('تفاصيل المهمة')),
        body: Center(child: Text('خطأ: $error')),
      ),
      data: (tasks) {
        final task = tasks.where((t) => t.id == taskId).firstOrNull;

        if (task == null) {
          return Scaffold(
            appBar: AppBar(title: const Text('تفاصيل المهمة')),
            body: const Center(child: Text('المهمة غير موجودة')),
          );
        }

        return _TaskDetailsBody(task: task);
      },
    );
  }
}

class _TaskDetailsBody extends ConsumerWidget {
  final FieldTask task;

  const _TaskDetailsBody({required this.task});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dateFormat = DateFormat('yyyy/MM/dd - HH:mm', 'ar');

    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل المهمة'),
        actions: [
          if (!task.synced)
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: Icon(
                Icons.cloud_off,
                color: Colors.orange,
              ),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title & Status
            Row(
              children: [
                Expanded(
                  child: Text(
                    task.title,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                _StatusChip(status: task.status),
              ],
            ),

            const SizedBox(height: 16),

            // Priority & Due Date
            Row(
              children: [
                _PriorityBadge(priority: task.priority),
                const SizedBox(width: 16),
                if (task.dueDate != null) ...[
                  Icon(
                    Icons.calendar_today,
                    size: 16,
                    color: task.isOverdue ? Colors.red : Colors.grey,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    dateFormat.format(task.dueDate!),
                    style: TextStyle(
                      color: task.isOverdue ? Colors.red : Colors.grey[700],
                      fontWeight:
                          task.isOverdue ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                  if (task.isOverdue) ...[
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.red[100],
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text(
                        'متأخرة',
                        style: TextStyle(
                          color: Colors.red,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ],
              ],
            ),

            const Divider(height: 32),

            // Description
            if (task.description != null && task.description!.isNotEmpty) ...[
              const Text(
                'الوصف',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                task.description!,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[700],
                  height: 1.5,
                ),
              ),
              const Divider(height: 32),
            ],

            // Evidence (if task is completed)
            if (task.status == TaskStatus.done) ...[
              const Text(
                'الدليل',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),

              // Notes
              if (task.evidenceNotes != null &&
                  task.evidenceNotes!.isNotEmpty) ...[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(task.evidenceNotes!),
                ),
                const SizedBox(height: 12),
              ],

              // Photos
              if (task.evidencePhotos.isNotEmpty) ...[
                SizedBox(
                  height: 100,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: task.evidencePhotos.length,
                    itemBuilder: (context, index) {
                      final photoPath = task.evidencePhotos[index];
                      return Container(
                        width: 100,
                        height: 100,
                        margin: const EdgeInsets.only(left: 8),
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(8),
                          color: Colors.grey[300],
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(8),
                          child: Image.network(
                            photoPath,
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => const Icon(
                              Icons.image_not_supported,
                              color: Colors.grey,
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],

              const Divider(height: 32),
            ],

            // Metadata
            _MetadataRow(
              icon: Icons.location_on,
              label: 'معرف الحقل',
              value: task.fieldId,
            ),
            if (task.assignedTo != null)
              _MetadataRow(
                icon: Icons.person,
                label: 'مسند إلى',
                value: task.assignedTo!,
              ),
            _MetadataRow(
              icon: Icons.access_time,
              label: 'تاريخ الإنشاء',
              value: dateFormat.format(task.createdAt),
            ),
            _MetadataRow(
              icon: Icons.update,
              label: 'آخر تحديث',
              value: dateFormat.format(task.updatedAt),
            ),
          ],
        ),
      ),

      // Bottom action
      bottomNavigationBar: task.status != TaskStatus.done
          ? Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, -5),
                  ),
                ],
              ),
              child: ElevatedButton(
                onPressed: () => _completeTask(context),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolTheme.primary,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text(
                  'إكمال المهمة',
                  style: TextStyle(fontSize: 16),
                ),
              ),
            )
          : null,
    );
  }

  void _completeTask(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CompleteTaskScreen(task: task),
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  final TaskStatus status;

  const _StatusChip({required this.status});

  @override
  Widget build(BuildContext context) {
    Color color;
    switch (status) {
      case TaskStatus.open:
        color = Colors.blue;
        break;
      case TaskStatus.inProgress:
        color = Colors.orange;
        break;
      case TaskStatus.done:
        color = Colors.green;
        break;
      case TaskStatus.cancelled:
        color = Colors.grey;
        break;
    }

    return Chip(
      label: Text(
        status.arabicLabel,
        style: const TextStyle(color: Colors.white, fontSize: 12),
      ),
      backgroundColor: color,
      padding: EdgeInsets.zero,
    );
  }
}

class _PriorityBadge extends StatelessWidget {
  final TaskPriority priority;

  const _PriorityBadge({required this.priority});

  @override
  Widget build(BuildContext context) {
    Color color;
    IconData icon;

    switch (priority) {
      case TaskPriority.low:
        color = Colors.grey;
        icon = Icons.arrow_downward;
        break;
      case TaskPriority.medium:
        color = Colors.blue;
        icon = Icons.remove;
        break;
      case TaskPriority.high:
        color = Colors.orange;
        icon = Icons.arrow_upward;
        break;
      case TaskPriority.urgent:
        color = Colors.red;
        icon = Icons.priority_high;
        break;
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 16),
        const SizedBox(width: 4),
        Text(
          priority.arabicLabel,
          style: TextStyle(color: color),
        ),
      ],
    );
  }
}

class _MetadataRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _MetadataRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey),
          const SizedBox(width: 8),
          Text(
            '$label: ',
            style: TextStyle(color: Colors.grey[600]),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }
}
