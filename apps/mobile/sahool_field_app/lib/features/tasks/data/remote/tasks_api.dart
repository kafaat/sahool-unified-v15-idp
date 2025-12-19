import '../../../../core/http/api_client.dart';
import '../../domain/entities/task.dart';

/// Tasks API - Remote data source
class TasksApi {
  final ApiClient _client;

  TasksApi(this._client);

  /// Fetch all tasks for tenant
  Future<List<FieldTask>> fetchTasks({String? fieldId}) async {
    final queryParams = <String, dynamic>{
      'tenant_id': _client.tenantId,
    };

    if (fieldId != null) {
      queryParams['field_id'] = fieldId;
    }

    final response = await _client.get(
      '/tasks',
      queryParameters: queryParams,
    );

    if (response is List) {
      return response
          .cast<Map<String, dynamic>>()
          .map((json) => FieldTask.fromJson(json))
          .toList();
    }

    return [];
  }

  /// Fetch single task by ID
  Future<FieldTask?> fetchTaskById(String taskId) async {
    try {
      final response = await _client.get('/tasks/$taskId');

      if (response is Map<String, dynamic>) {
        return FieldTask.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to fetch task $taskId: $e');
    }

    return null;
  }

  /// Complete a task with evidence
  Future<bool> completeTask({
    required String taskId,
    String? notes,
    List<String>? photos,
  }) async {
    try {
      await _client.post(
        '/tasks/$taskId/complete',
        {
          'tenant_id': _client.tenantId,
          'evidence_notes': notes,
          'evidence_photos': photos ?? [],
        },
      );
      return true;
    } catch (e) {
      print('❌ Failed to complete task $taskId: $e');
      return false;
    }
  }

  /// Update task status
  Future<bool> updateTaskStatus({
    required String taskId,
    required TaskStatus status,
  }) async {
    try {
      await _client.put(
        '/tasks/$taskId',
        {
          'status': status.value,
        },
      );
      return true;
    } catch (e) {
      print('❌ Failed to update task status: $e');
      return false;
    }
  }

  /// Create new task
  Future<FieldTask?> createTask(FieldTask task) async {
    try {
      final response = await _client.post(
        '/tasks',
        task.toJson(),
      );

      if (response is Map<String, dynamic>) {
        return FieldTask.fromJson(response);
      }
    } catch (e) {
      print('❌ Failed to create task: $e');
    }

    return null;
  }
}
