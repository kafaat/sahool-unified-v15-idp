import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/http/api_client.dart';
import '../../../core/storage/database.dart';
import '../data/remote/tasks_api.dart';
import '../data/repo/tasks_repo.dart';
import '../domain/entities/task.dart';

/// Database provider
final databaseProvider = Provider<AppDatabase>((ref) {
  return AppDatabase();
});

/// API Client provider
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

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
}

/// Tasks provider
final tasksProvider =
    StateNotifierProvider<TasksNotifier, AsyncValue<List<FieldTask>>>((ref) {
  final repo = ref.watch(tasksRepoProvider);
  final client = ref.watch(apiClientProvider);
  return TasksNotifier(repo, client);
});

/// Single task provider
final taskByIdProvider =
    Provider.family<FieldTask?, String>((ref, taskId) {
  final tasksState = ref.watch(tasksProvider);
  return tasksState.when(
    data: (tasks) => tasks.where((t) => t.id == taskId).firstOrNull,
    loading: () => null,
    error: (_, __) => null,
  );
});

/// Pending tasks provider
final pendingTasksProvider = Provider<List<FieldTask>>((ref) {
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

/// Overdue tasks provider
final overdueTasksProvider = Provider<List<FieldTask>>((ref) {
  final tasksState = ref.watch(tasksProvider);
  return tasksState.when(
    data: (tasks) => tasks.where((t) => t.isOverdue).toList(),
    loading: () => [],
    error: (_, __) => [],
  );
});
