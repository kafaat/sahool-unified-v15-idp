import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:uuid/uuid.dart';

import '../../../../core/storage/database.dart';
import '../../../../core/sync/network_status.dart';
import '../../domain/entities/task.dart';
import '../remote/tasks_api.dart';

/// Tasks Repository - Offline-first data access
class TasksRepo {
  final AppDatabase _db;
  final TasksApi _api;
  final NetworkStatus _networkStatus;
  final _uuid = const Uuid();

  TasksRepo({
    required AppDatabase database,
    required TasksApi api,
    NetworkStatus? networkStatus,
  })  : _db = database,
        _api = api,
        _networkStatus = networkStatus ?? NetworkStatus();

  /// Get all tasks (from local DB)
  Future<List<FieldTask>> getAllTasks(String tenantId) async {
    final dbTasks = await _db.getAllTasks(tenantId);
    return dbTasks.map(_mapDbToEntity).toList();
  }

  /// Get tasks for a specific field
  Future<List<FieldTask>> getTasksForField(String fieldId) async {
    final dbTasks = await _db.getTasksForField(fieldId);
    return dbTasks.map(_mapDbToEntity).toList();
  }

  /// Get pending tasks (open or in_progress)
  Future<List<FieldTask>> getPendingTasks(String tenantId) async {
    final dbTasks = await _db.getPendingTasks(tenantId);
    return dbTasks.map(_mapDbToEntity).toList();
  }

  /// Get single task by ID
  Future<FieldTask?> getTaskById(String taskId) async {
    final dbTask = await _db.getTaskById(taskId);
    return dbTask != null ? _mapDbToEntity(dbTask) : null;
  }

  /// Refresh tasks from server
  Future<int> refreshFromServer({String? fieldId}) async {
    if (!await _networkStatus.checkOnline()) {
      throw Exception('لا يوجد اتصال بالإنترنت');
    }

    try {
      final tasks = await _api.fetchTasks(fieldId: fieldId);

      // Upsert to local DB
      await _db.upsertTasksFromServer(
        tasks.map((t) => t.toJson()).toList(),
      );

      return tasks.length;
    } catch (e) {
      print('❌ Failed to refresh tasks: $e');
      rethrow;
    }
  }

  /// Complete task with offline-first pattern
  Future<void> completeTaskOfflineFirst({
    required String taskId,
    String? notes,
    List<String>? photos,
  }) async {
    // 1. Update local DB immediately
    await _db.markTaskDone(
      taskId: taskId,
      notes: notes,
      photos: photos,
    );

    // 2. Get task for tenant_id
    final task = await _db.getTaskById(taskId);
    if (task == null) return;

    // 3. Add to outbox for sync
    await _db.addToOutbox(
      OutboxCompanion.insert(
        id: _uuid.v4(),
        type: 'task_complete',
        payloadJson: jsonEncode({
          'task_id': taskId,
          'tenant_id': task.tenantId,
          'evidence_notes': notes,
          'evidence_photos': photos ?? [],
        }),
        createdAt: DateTime.now(),
      ),
    );

    print('✅ Task $taskId marked done locally + queued for sync');
  }

  /// Update task status with offline-first pattern
  Future<void> updateTaskStatus({
    required String taskId,
    required TaskStatus status,
  }) async {
    // 1. Update local DB
    await _db.upsertTask(
      TasksCompanion(
        id: Value(taskId),
        status: Value(status.value),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ),
    );

    // 2. Get task for tenant_id
    final task = await _db.getTaskById(taskId);
    if (task == null) return;

    // 3. Add to outbox
    await _db.addToOutbox(
      OutboxCompanion.insert(
        id: _uuid.v4(),
        type: 'task_update',
        payloadJson: jsonEncode({
          'task_id': taskId,
          'tenant_id': task.tenantId,
          'status': status.value,
        }),
        createdAt: DateTime.now(),
      ),
    );
  }

  /// Create new task (offline-first)
  Future<FieldTask> createTask({
    required String tenantId,
    required String fieldId,
    required String title,
    String? description,
    TaskPriority priority = TaskPriority.medium,
    DateTime? dueDate,
    String? assignedTo,
  }) async {
    final taskId = _uuid.v4();
    final now = DateTime.now();

    final task = FieldTask(
      id: taskId,
      tenantId: tenantId,
      fieldId: fieldId,
      title: title,
      description: description,
      status: TaskStatus.open,
      priority: priority,
      dueDate: dueDate,
      assignedTo: assignedTo,
      createdAt: now,
      updatedAt: now,
      synced: false,
    );

    // 1. Save to local DB
    await _db.upsertTask(
      TasksCompanion.insert(
        id: taskId,
        tenantId: tenantId,
        fieldId: fieldId,
        title: title,
        description: Value(description),
        priority: Value(priority.value),
        dueDate: Value(dueDate),
        assignedTo: Value(assignedTo),
        createdAt: now,
        updatedAt: now,
      ),
    );

    // 2. Add to outbox for sync
    await _db.addToOutbox(
      OutboxCompanion.insert(
        id: _uuid.v4(),
        type: 'task_create',
        payloadJson: jsonEncode(task.toJson()),
        createdAt: now,
      ),
    );

    return task;
  }

  /// Map database entity to domain entity
  FieldTask _mapDbToEntity(Task dbTask) {
    return FieldTask(
      id: dbTask.id,
      tenantId: dbTask.tenantId,
      fieldId: dbTask.fieldId,
      farmId: dbTask.farmId,
      title: dbTask.title,
      description: dbTask.description,
      status: TaskStatus.fromString(dbTask.status),
      priority: TaskPriority.fromString(dbTask.priority),
      dueDate: dbTask.dueDate,
      assignedTo: dbTask.assignedTo,
      evidenceNotes: dbTask.evidenceNotes,
      evidencePhotos: dbTask.evidencePhotos?.split(',') ?? [],
      createdAt: dbTask.createdAt,
      updatedAt: dbTask.updatedAt,
      synced: dbTask.synced,
    );
  }
}
