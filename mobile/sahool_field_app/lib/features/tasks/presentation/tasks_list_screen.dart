import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/theme.dart';
import '../domain/entities/task.dart';
import '../providers/tasks_provider.dart';
import 'task_details_screen.dart';
import 'widgets/task_card.dart';

/// Tasks List Screen - Main tasks view
class TasksListScreen extends ConsumerStatefulWidget {
  final String? fieldId;

  const TasksListScreen({super.key, this.fieldId});

  @override
  ConsumerState<TasksListScreen> createState() => _TasksListScreenState();
}

class _TasksListScreenState extends ConsumerState<TasksListScreen> {
  TaskStatus? _statusFilter;
  bool _isRefreshing = false;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _refresh() async {
    if (_isRefreshing) return;

    setState(() => _isRefreshing = true);

    try {
      await ref.read(tasksProvider.notifier).refresh(fieldId: widget.fieldId);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل التحديث: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isRefreshing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final tasksState = ref.watch(tasksProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('المهام'),
        actions: [
          // Filter button
          PopupMenuButton<TaskStatus?>(
            icon: Icon(
              Icons.filter_list,
              color: _statusFilter != null ? SahoolTheme.primaryGreen : null,
            ),
            onSelected: (status) {
              setState(() => _statusFilter = status);
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: null,
                child: Text('الكل'),
              ),
              ...TaskStatus.values.map(
                (status) => PopupMenuItem(
                  value: status,
                  child: Text(status.arabicLabel),
                ),
              ),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: tasksState.when(
          loading: () => const Center(
            child: CircularProgressIndicator(),
          ),
          error: (error, stack) => Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(
                  Icons.error_outline,
                  size: 64,
                  color: Colors.red,
                ),
                const SizedBox(height: 16),
                Text(
                  'حدث خطأ: $error',
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: _refresh,
                  child: const Text('إعادة المحاولة'),
                ),
              ],
            ),
          ),
          data: (tasks) {
            // Apply filter
            var filteredTasks = tasks;
            if (_statusFilter != null) {
              filteredTasks = tasks
                  .where((t) => t.status == _statusFilter)
                  .toList();
            }

            if (filteredTasks.isEmpty) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.task_alt,
                      size: 64,
                      color: Colors.grey[400],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      _statusFilter != null
                          ? 'لا توجد مهام ${_statusFilter!.arabicLabel}'
                          : 'لا توجد مهام',
                      style: TextStyle(
                        fontSize: 18,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              );
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: filteredTasks.length,
              itemBuilder: (context, index) {
                final task = filteredTasks[index];
                return TaskCard(
                  task: task,
                  onTap: () => _openTaskDetails(task),
                  onStatusChanged: (status) => _updateStatus(task, status),
                );
              },
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _createTask,
        backgroundColor: SahoolTheme.primaryGreen,
        child: const Icon(Icons.add),
      ),
    );
  }

  void _openTaskDetails(FieldTask task) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => TaskDetailsScreen(taskId: task.id),
      ),
    );
  }

  Future<void> _updateStatus(FieldTask task, TaskStatus status) async {
    try {
      await ref.read(tasksProvider.notifier).updateStatus(
            taskId: task.id,
            status: status,
          );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('تم تحديث حالة المهمة إلى ${status.arabicLabel}'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل تحديث الحالة: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _createTask() {
    // TODO: Navigate to create task screen
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('إنشاء مهمة جديدة - قريباً'),
      ),
    );
  }
}
