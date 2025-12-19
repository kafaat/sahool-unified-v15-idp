import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../../../core/config/theme.dart';
import '../../domain/entities/task.dart';

/// Task Card Widget
class TaskCard extends StatelessWidget {
  final FieldTask task;
  final VoidCallback? onTap;
  final Function(TaskStatus)? onStatusChanged;

  const TaskCard({
    super.key,
    required this.task,
    this.onTap,
    this.onStatusChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: task.isOverdue
            ? const BorderSide(color: Colors.red, width: 2)
            : BorderSide.none,
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row
              Row(
                children: [
                  // Priority indicator
                  _PriorityIndicator(priority: task.priority),
                  const SizedBox(width: 12),

                  // Title
                  Expanded(
                    child: Text(
                      task.title,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),

                  // Sync indicator
                  if (!task.synced)
                    const Padding(
                      padding: EdgeInsets.only(right: 8),
                      child: Icon(
                        Icons.cloud_off,
                        size: 16,
                        color: Colors.orange,
                      ),
                    ),

                  // Status dropdown
                  _StatusDropdown(
                    status: task.status,
                    onChanged: onStatusChanged,
                  ),
                ],
              ),

              // Description preview
              if (task.description != null && task.description!.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  task.description!,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],

              const SizedBox(height: 12),

              // Footer row
              Row(
                children: [
                  // Due date
                  if (task.dueDate != null) ...[
                    Icon(
                      Icons.schedule,
                      size: 14,
                      color: task.isOverdue
                          ? Colors.red
                          : task.isDueToday
                              ? Colors.orange
                              : Colors.grey,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      _formatDueDate(task.dueDate!),
                      style: TextStyle(
                        fontSize: 12,
                        color: task.isOverdue
                            ? Colors.red
                            : task.isDueToday
                                ? Colors.orange
                                : Colors.grey[600],
                        fontWeight:
                            task.isOverdue ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ],

                  const Spacer(),

                  // Evidence indicator
                  if (task.evidencePhotos.isNotEmpty) ...[
                    Icon(
                      Icons.photo_camera,
                      size: 14,
                      color: Colors.grey[600],
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '${task.evidencePhotos.length}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],

                  // Assigned to
                  if (task.assignedTo != null) ...[
                    Icon(
                      Icons.person_outline,
                      size: 14,
                      color: Colors.grey[600],
                    ),
                    const SizedBox(width: 4),
                    Text(
                      task.assignedTo!,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDueDate(DateTime date) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final tomorrow = today.add(const Duration(days: 1));
    final dateOnly = DateTime(date.year, date.month, date.day);

    if (dateOnly == today) {
      return 'اليوم';
    } else if (dateOnly == tomorrow) {
      return 'غداً';
    } else if (dateOnly.isBefore(today)) {
      final days = today.difference(dateOnly).inDays;
      return 'متأخر $days يوم';
    } else {
      return DateFormat('MM/dd').format(date);
    }
  }
}

/// Priority indicator widget
class _PriorityIndicator extends StatelessWidget {
  final TaskPriority priority;

  const _PriorityIndicator({required this.priority});

  @override
  Widget build(BuildContext context) {
    Color color;
    switch (priority) {
      case TaskPriority.low:
        color = Colors.grey;
        break;
      case TaskPriority.medium:
        color = Colors.blue;
        break;
      case TaskPriority.high:
        color = Colors.orange;
        break;
      case TaskPriority.urgent:
        color = Colors.red;
        break;
    }

    return Container(
      width: 4,
      height: 40,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(2),
      ),
    );
  }
}

/// Status dropdown widget
class _StatusDropdown extends StatelessWidget {
  final TaskStatus status;
  final Function(TaskStatus)? onChanged;

  const _StatusDropdown({
    required this.status,
    this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    Color bgColor;
    switch (status) {
      case TaskStatus.open:
        bgColor = Colors.blue[50]!;
        break;
      case TaskStatus.inProgress:
        bgColor = Colors.orange[50]!;
        break;
      case TaskStatus.done:
        bgColor = Colors.green[50]!;
        break;
      case TaskStatus.cancelled:
        bgColor = Colors.grey[200]!;
        break;
    }

    return PopupMenuButton<TaskStatus>(
      onSelected: onChanged,
      enabled: onChanged != null && status != TaskStatus.done,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              status.arabicLabel,
              style: TextStyle(
                fontSize: 12,
                color: _getStatusColor(status),
              ),
            ),
            if (onChanged != null && status != TaskStatus.done) ...[
              const SizedBox(width: 4),
              Icon(
                Icons.arrow_drop_down,
                size: 16,
                color: _getStatusColor(status),
              ),
            ],
          ],
        ),
      ),
      itemBuilder: (context) => TaskStatus.values
          .where((s) => s != status && s != TaskStatus.done)
          .map(
            (s) => PopupMenuItem(
              value: s,
              child: Text(s.arabicLabel),
            ),
          )
          .toList(),
    );
  }

  Color _getStatusColor(TaskStatus status) {
    switch (status) {
      case TaskStatus.open:
        return Colors.blue;
      case TaskStatus.inProgress:
        return Colors.orange;
      case TaskStatus.done:
        return Colors.green;
      case TaskStatus.cancelled:
        return Colors.grey;
    }
  }
}
