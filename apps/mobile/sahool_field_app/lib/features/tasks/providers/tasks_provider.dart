import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/di/providers.dart';
import '../../../core/http/api_client.dart';
import '../../../core/notifications/notification_manager.dart';
import '../../../main.dart' show databaseProvider;
import '../data/remote/tasks_api.dart';
import '../data/repo/tasks_repo.dart';
import '../domain/entities/task.dart';

// Re-export for use in other files
export '../../../core/http/api_client.dart' show ApiClient;
export '../../../core/notifications/notification_manager.dart'
    show notificationManagerProvider;

// Note: databaseProvider is imported from main.dart (canonical source)
// Note: apiClientProvider is imported from core/di/providers.dart (with security config)

/// Tasks API provider
final tasksApiProvider = Provider<TasksApi>((ref) {
  final client = ref.watch(apiClientProvider);
  return TasksApi(client);
});

/// Tasks Repository provider
final tasksRepoProvider = Provider<TasksRepo>((ref) {
  final db = ref.watch(databaseProvider);
  final api = ref.watch(tasksApiProvider);
  return TasksRepo(database: db, api: api);
});

/// Tasks state notifier
class TasksNotifier extends StateNotifier<AsyncValue<List<FieldTask>>> {
  final TasksRepo _repo;
  final ApiClient _client;

  TasksNotifier(this._repo, this._client) : super(const AsyncValue.loading()) {
    _loadLocal();
  }

  /// Load tasks from local database
  Future<void> _loadLocal() async {
    try {
      final tasks = await _repo.getAllTasks(_client.tenantId);
      state = AsyncValue.data(tasks);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  /// Refresh from server
  Future<void> refresh({String? fieldId}) async {
    try {
      await _repo.refreshFromServer(fieldId: fieldId);
      await _loadLocal();
    } catch (e) {
      // Still show local data if server fails
      await _loadLocal();
      rethrow;
    }
  }

  /// Update task status
  Future<void> updateStatus({
    required String taskId,
    required TaskStatus status,
  }) async {
    await _repo.updateTaskStatus(taskId: taskId, status: status);
    await _loadLocal();
  }

  /// Complete task with evidence
  Future<void> completeTask({
    required String taskId,
    String? notes,
    List<String>? photos,
  }) async {
    await _repo.completeTaskOfflineFirst(
      taskId: taskId,
      notes: notes,
      photos: photos,
    );
    await _loadLocal();
  }

  /// Create new task
  Future<FieldTask> createTask({
    required String fieldId,
    required String title,
    String? description,
    TaskPriority priority = TaskPriority.medium,
    DateTime? dueDate,
  }) async {
    final task = await _repo.createTask(
      tenantId: _client.tenantId,
      fieldId: fieldId,
      title: title,
      description: description,
      priority: priority,
      dueDate: dueDate,
    );
    await _loadLocal();
    return task;
  }

  /// Update task details
  Future<FieldTask> updateTask({
    required String taskId,
    String? title,
    String? description,
    TaskPriority? priority,
    DateTime? dueDate,
    String? assignedTo,
  }) async {
    final task = await _repo.updateTask(
      taskId: taskId,
      title: title,
      description: description,
      priority: priority,
      dueDate: dueDate,
      assignedTo: assignedTo,
    );
    await _loadLocal();
    return task;
  }

  /// Delete task (soft delete - marks as cancelled)
  Future<void> deleteTask(String taskId) async {
    await _repo.deleteTask(taskId);
    await _loadLocal();
  }
}

/// Tasks provider
/// Uses autoDispose with ref.keepAlive() for critical data that should persist
/// but still clean up properly when app navigates away from tasks feature
final tasksProvider = StateNotifierProvider.autoDispose<TasksNotifier,
    AsyncValue<List<FieldTask>>>((ref) {
  final repo = ref.watch(tasksRepoProvider);
  final client = ref.watch(apiClientProvider);

  // Keep alive for the duration of the app session since tasks are frequently accessed
  final link = ref.keepAlive();

  // Auto-dispose after 5 minutes of inactivity to prevent memory leaks
  final timer = Timer(const Duration(minutes: 5), link.close);
  ref.onDispose(timer.cancel);

  return TasksNotifier(repo, client);
});

/// Single task provider - autoDispose to match parent provider
final taskByIdProvider =
    Provider.autoDispose.family<FieldTask?, String>((ref, taskId) {
  final tasksState = ref.watch(tasksProvider);
  return tasksState.when(
    data: (tasks) => tasks.where((t) => t.id == taskId).firstOrNull,
    loading: () => null,
    error: (_, __) => null,
  );
});

/// Pending tasks provider - autoDispose to match parent provider
final pendingTasksProvider = Provider.autoDispose<List<FieldTask>>((ref) {
  final tasksState = ref.watch(tasksProvider);
  return tasksState.when(
    data: (tasks) => tasks
        .where((t) =>
            t.status == TaskStatus.open || t.status == TaskStatus.inProgress)
        .toList(),
    loading: () => [],
    error: (_, __) => [],
  );
});

/// Overdue tasks provider - autoDispose to match parent provider
final overdueTasksProvider = Provider.autoDispose<List<FieldTask>>((ref) {
  final tasksState = ref.watch(tasksProvider);
  return tasksState.when(
    data: (tasks) => tasks.where((t) => t.isOverdue).toList(),
    loading: () => [],
    error: (_, __) => [],
  );
});
