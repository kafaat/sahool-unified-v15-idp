import 'dart:ui';
import 'package:flutter/material.dart';
import '../../domain/entities/field_task.dart';
import 'task_tile.dart';
import '../../../../core/theme/sahool_theme.dart';

/// Daily Tasks Sheet - لوحة مهام اليوم المنزلقة
///
/// تظهر كـ "مقبض" صغير في أسفل الشاشة
/// يمكن سحبها للأعلى لرؤية جدول اليوم بالكامل
/// تستخدم BackdropFilter للتأثير الزجاجي
class DailyTasksSheet extends StatefulWidget {
  final List<FieldTask>? tasks;
  final ValueChanged<FieldTask>? onTaskTap;
  final ValueChanged<FieldTask>? onTaskCompleted;

  const DailyTasksSheet({
    super.key,
    this.tasks,
    this.onTaskTap,
    this.onTaskCompleted,
  });

  @override
  State<DailyTasksSheet> createState() => _DailyTasksSheetState();
}

class _DailyTasksSheetState extends State<DailyTasksSheet> {
  // Mock data for demo
  late List<FieldTask> _tasks;

  @override
  void initState() {
    super.initState();
    _tasks = widget.tasks ?? _getMockTasks();
  }

  List<FieldTask> _getMockTasks() {
    final now = DateTime.now();
    return [
      FieldTask(
        id: '1',
        title: 'ري حقل القمح',
        fieldName: 'القطعة الشمالية',
        dueTime: now.add(const Duration(hours: 1)),
        type: TaskType.irrigation,
        priority: TaskPriority.high,
      ),
      FieldTask(
        id: '2',
        title: 'إضافة سماد يوريا',
        fieldName: 'القطعة الجنوبية',
        dueTime: now.add(const Duration(hours: 3)),
        type: TaskType.fertilization,
      ),
      FieldTask(
        id: '3',
        title: 'فحص الآفات والحشرات',
        fieldName: 'مزرعة البن',
        dueTime: now.add(const Duration(hours: 5)),
        type: TaskType.scouting,
        priority: TaskPriority.urgent,
      ),
      FieldTask(
        id: '4',
        title: 'جني محصول الطماطم',
        fieldName: 'حقل الخضروات',
        dueTime: now.add(const Duration(hours: 7)),
        type: TaskType.harvest,
      ),
      FieldTask(
        id: '5',
        title: 'صيانة نظام الري بالتنقيط',
        fieldName: 'القطعة الشرقية',
        dueTime: now.subtract(const Duration(hours: 2)), // Overdue
        type: TaskType.other,
      ),
    ];
  }

  int get _pendingCount => _tasks.where((t) => !t.isCompleted).length;
  int get _completedCount => _tasks.where((t) => t.isCompleted).length;

  void _onTaskCompletedChanged(FieldTask task, bool completed) {
    setState(() {
      final index = _tasks.indexWhere((t) => t.id == task.id);
      if (index != -1) {
        _tasks[index] = task.copyWith(
          isCompleted: completed,
          completedAt: completed ? DateTime.now() : null,
        );
      }
    });
    widget.onTaskCompleted?.call(_tasks.firstWhere((t) => t.id == task.id));
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.12, // Peeking mode
      minChildSize: 0.12,
      maxChildSize: 0.55, // Half screen
      snap: true,
      snapSizes: const [0.12, 0.35, 0.55],
      builder: (context, scrollController) {
        return ClipRRect(
          borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
          child: BackdropFilter(
            filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
            child: Container(
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.92),
                borderRadius:
                    const BorderRadius.vertical(top: Radius.circular(24)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 20,
                    offset: const Offset(0, -5),
                  ),
                ],
              ),
              child: Column(
                children: [
                  // 1. Drag Handle
                  _buildHandle(),

                  // 2. Header with title & count
                  _buildHeader(),

                  // 3. Tasks List
                  Expanded(
                    child: _tasks.isEmpty
                        ? _buildEmptyState()
                        : ListView.builder(
                            controller: scrollController,
                            padding: const EdgeInsets.only(bottom: 20),
                            itemCount: _tasks.length,
                            itemBuilder: (context, index) {
                              final task = _tasks[index];
                              return TaskTile(
                                key: ValueKey(task.id),
                                task: task,
                                onCompletedChanged: (completed) =>
                                    _onTaskCompletedChanged(task, completed),
                                onTap: () => widget.onTaskTap?.call(task),
                              );
                            },
                          ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildHandle() {
    return Center(
      child: Container(
        margin: const EdgeInsets.only(top: 12),
        width: 40,
        height: 5,
        decoration: BoxDecoration(
          color: Colors.grey[300],
          borderRadius: BorderRadius.circular(10),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Title with icon
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: SahoolColors.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.task_alt,
                  color: SahoolColors.primary,
                  size: 18,
                ),
              ),
              const SizedBox(width: 10),
              const Text(
                'مهام اليوم',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
            ],
          ),

          // Count badges
          Row(
            children: [
              // Completed count
              if (_completedCount > 0)
                Container(
                  margin: const EdgeInsets.only(left: 8),
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: SahoolColors.success.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.check,
                        size: 12,
                        color: SahoolColors.success,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '$_completedCount',
                        style: TextStyle(
                          color: SahoolColors.success,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),

              // Pending count
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: _pendingCount > 0
                      ? SahoolColors.warning.withOpacity(0.1)
                      : SahoolColors.success.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  _pendingCount > 0 ? '$_pendingCount متبقية' : 'مكتملة!',
                  style: TextStyle(
                    color: _pendingCount > 0
                        ? SahoolColors.warning
                        : SahoolColors.success,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.check_circle_outline,
            size: 48,
            color: SahoolColors.success,
          ),
          const SizedBox(height: 12),
          const Text(
            'لا توجد مهام لهذا اليوم',
            style: TextStyle(
              color: Colors.grey,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          TextButton.icon(
            onPressed: () {
              // Navigate to add task
            },
            icon: const Icon(Icons.add),
            label: const Text('إضافة مهمة'),
          ),
        ],
      ),
    );
  }
}

/// Compact Tasks Summary - ملخص المهام المدمج
/// يُستخدم عندما يكون Context Panel مفتوحاً
class CompactTasksSummary extends StatelessWidget {
  final List<FieldTask> tasks;
  final VoidCallback? onTap;

  const CompactTasksSummary({
    super.key,
    required this.tasks,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final pending = tasks.where((t) => !t.isCompleted).length;
    final urgent = tasks.where((t) => t.priority == TaskPriority.urgent).length;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.all(16),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.9),
          borderRadius: BorderRadius.circular(16),
          boxShadow: SahoolShadows.small,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.task_alt,
              color: SahoolColors.primary,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              '$pending مهام',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            if (urgent > 0) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: SahoolColors.danger.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '$urgent عاجل',
                  style: TextStyle(
                    color: SahoolColors.danger,
                    fontWeight: FontWeight.bold,
                    fontSize: 10,
                  ),
                ),
              ),
            ],
            const SizedBox(width: 4),
            Icon(
              Icons.keyboard_arrow_up,
              color: Colors.grey[400],
              size: 18,
            ),
          ],
        ),
      ),
    );
  }
}
