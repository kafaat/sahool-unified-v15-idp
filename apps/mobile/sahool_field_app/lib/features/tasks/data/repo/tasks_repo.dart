import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:uuid/uuid.dart';

import '../../../../core/contracts/api_endpoints.dart';
import '../../../../core/error_handling/error_handling.dart';
import '../../../../core/storage/database.dart';
import '../../../../core/sync/network_status.dart';
import '../../../../core/utils/app_logger.dart';
import '../../domain/entities/task.dart';
import '../remote/tasks_api.dart';

/// Tasks Repository - Offline-first data access
///
/// Provides task management with:
/// - Offline-first pattern with local SQLite storage
/// - Background sync via outbox queue
/// - Proper error handling with bilingual messages
class TasksRepo {
  final AppDatabase _db;
  final TasksApi _api;
  final NetworkStatus _networkStatus;
  final _uuid = const Uuid();
  static const _tag = 'TasksRepo';

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
  ///
  /// Returns the number of tasks refreshed.
  /// Throws [SyncException] if offline, or [AppException] on API errors.
  Future<int> refreshFromServer({String? fieldId}) async {
    if (!await _networkStatus.checkOnline()) {
      throw SyncException.offline();
    }

    try {
      final tasks = await _api.fetchTasks(fieldId: fieldId);

      // Upsert to local DB
      await _db.upsertTasksFromServer(
        tasks.map((t) => t.toJson()).toList(),
      );

      AppLogger.i('Tasks refreshed from server',
          tag: _tag, data: {'count': tasks.length});
      return tasks.length;
    } catch (e, stackTrace) {
      final appException = ErrorHandler().handle(
        e,
        stackTrace: stackTrace,
        tag: _tag,
      );
      throw appException;
    }
  }

  /// Complete task with offline-first pattern
  ///
  /// Marks the task as done locally and queues for sync.
  /// Throws [NotFoundException] if task doesn't exist.
  /// Throws [StorageException] on database errors.
  Future<void> completeTaskOfflineFirst({
    required String taskId,
    String? notes,
    List<String>? photos,
  }) async {
    try {
      // 1. Update local DB immediately
      await _db.markTaskDone(
        taskId: taskId,
        notes: notes,
        photos: photos,
      );

      // 2. Get task for tenant_id
      final task = await _db.getTaskById(taskId);
      if (task == null) {
        throw NotFoundException.task(taskId);
      }

      // 3. Add to outbox for sync
      await _db.queueOutboxItem(
        tenantId: task.tenantId,
        entityType: 'task',
        entityId: taskId,
        apiEndpoint: TaskEndpoints.complete(taskId),
        method: 'PUT',
        payload: jsonEncode({
          'task_id': taskId,
          'tenant_id': task.tenantId,
          'evidence_notes': notes,
          'evidence_photos': photos ?? [],
        }),
      );

      AppLogger.i('Task marked done locally and queued for sync',
          tag: _tag, data: {'taskId': taskId});
    } catch (e, stackTrace) {
      if (e is AppException) rethrow;
      throw ErrorHandler().handle(e, stackTrace: stackTrace, tag: _tag);
    }
  }

  /// Update task status with offline-first pattern
  ///
  /// Updates status locally and queues for sync.
  /// Throws [NotFoundException] if task doesn't exist.
  /// Throws [StorageException] on database errors.
  Future<void> updateTaskStatus({
    required String taskId,
    required TaskStatus status,
  }) async {
    try {
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
      if (task == null) {
        throw NotFoundException.task(taskId);
      }

      // 3. Add to outbox
      await _db.queueOutboxItem(
        tenantId: task.tenantId,
        entityType: 'task',
        entityId: taskId,
        apiEndpoint: TaskEndpoints.get(taskId),
        method: 'PUT',
        payload: jsonEncode({
          'task_id': taskId,
          'tenant_id': task.tenantId,
          'status': status.value,
        }),
      );

      AppLogger.i('Task status updated',
          tag: _tag, data: {'taskId': taskId, 'status': status.value});
    } catch (e, stackTrace) {
      if (e is AppException) rethrow;
      throw ErrorHandler().handle(e, stackTrace: stackTrace, tag: _tag);
    }
  }

  /// Create new task (offline-first)
  ///
  /// Creates task locally and queues for sync.
  /// Throws [ValidationException] if required fields are missing.
  /// Throws [StorageException] on database errors.
  Future<FieldTask> createTask({
    required String tenantId,
    required String fieldId,
    required String title,
    String? description,
    TaskPriority priority = TaskPriority.medium,
    DateTime? dueDate,
    String? assignedTo,
  }) async {
    // Validate required fields
    if (title.trim().isEmpty) {
      throw ValidationException.requiredField('title', 'العنوان');
    }

    try {
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
      await _db.queueOutboxItem(
        tenantId: tenantId,
        entityType: 'task',
        entityId: taskId,
        apiEndpoint: TaskEndpoints.list,
        method: 'POST',
        payload: jsonEncode(task.toJson()),
      );

      AppLogger.i('Task created',
          tag: _tag, data: {'taskId': taskId, 'title': title});
      return task;
    } catch (e, stackTrace) {
      if (e is AppException) rethrow;
      throw ErrorHandler().handle(e, stackTrace: stackTrace, tag: _tag);
    }
  }

  /// Update task details (offline-first)
  ///
  /// Updates task locally and queues for sync.
  /// Throws [NotFoundException] if task doesn't exist.
  /// Throws [StorageException] on database errors.
  Future<FieldTask> updateTask({
    required String taskId,
    String? title,
    String? description,
    TaskPriority? priority,
    DateTime? dueDate,
    String? assignedTo,
  }) async {
    try {
      // 1. Get existing task
      final existingTask = await _db.getTaskById(taskId);
      if (existingTask == null) {
        throw NotFoundException.task(taskId);
      }

      final now = DateTime.now();

      // 2. Update local DB
      await _db.upsertTask(
        TasksCompanion(
          id: Value(taskId),
          title: title != null ? Value(title) : const Value.absent(),
          description:
              description != null ? Value(description) : const Value.absent(),
          priority:
              priority != null ? Value(priority.value) : const Value.absent(),
          dueDate: dueDate != null ? Value(dueDate) : const Value.absent(),
          assignedTo:
              assignedTo != null ? Value(assignedTo) : const Value.absent(),
          updatedAt: Value(now),
          synced: const Value(false),
        ),
      );

      // 3. Get updated task
      final updatedDbTask = await _db.getTaskById(taskId);
      final updatedTask = _mapDbToEntity(updatedDbTask!);

      // 4. Add to outbox for sync
      await _db.queueOutboxItem(
        tenantId: existingTask.tenantId,
        entityType: 'task',
        entityId: taskId,
        apiEndpoint: TaskEndpoints.get(taskId),
        method: 'PUT',
        payload: jsonEncode(updatedTask.toJson()),
      );

      AppLogger.i('Task updated', tag: _tag, data: {'taskId': taskId});
      return updatedTask;
    } catch (e, stackTrace) {
      if (e is AppException) rethrow;
      throw ErrorHandler().handle(e, stackTrace: stackTrace, tag: _tag);
    }
  }

  /// Delete task (offline-first with soft delete)
  ///
  /// Marks task as cancelled locally and queues for sync.
  /// Throws [NotFoundException] if task doesn't exist.
  /// Throws [StorageException] on database errors.
  Future<void> deleteTask(String taskId) async {
    try {
      // 1. Get existing task
      final existingTask = await _db.getTaskById(taskId);
      if (existingTask == null) {
        throw NotFoundException.task(taskId);
      }

      // 2. Mark as cancelled (soft delete)
      await _db.upsertTask(
        TasksCompanion(
          id: Value(taskId),
          status: const Value('cancelled'),
          updatedAt: Value(DateTime.now()),
          synced: const Value(false),
        ),
      );

      // 3. Add to outbox for sync
      await _db.queueOutboxItem(
        tenantId: existingTask.tenantId,
        entityType: 'task',
        entityId: taskId,
        apiEndpoint: TaskEndpoints.get(taskId),
        method: 'DELETE',
        payload:
            jsonEncode({'task_id': taskId, 'tenant_id': existingTask.tenantId}),
      );

      AppLogger.i('Task deleted (soft)', tag: _tag, data: {'taskId': taskId});
    } catch (e, stackTrace) {
      if (e is AppException) rethrow;
      throw ErrorHandler().handle(e, stackTrace: stackTrace, tag: _tag);
    }
  }

  /// Get overdue tasks for a tenant
  Future<List<FieldTask>> getOverdueTasks(String tenantId) async {
    final allTasks = await getAllTasks(tenantId);
    return allTasks.where((t) => t.isOverdue).toList();
  }

  /// Get tasks due today for a tenant
  Future<List<FieldTask>> getTasksDueToday(String tenantId) async {
    final allTasks = await getAllTasks(tenantId);
    return allTasks
        .where((t) => t.isDueToday && t.status != TaskStatus.done)
        .toList();
  }

  /// Get tasks due within specified days
  Future<List<FieldTask>> getTasksDueWithin(String tenantId, int days) async {
    final allTasks = await getAllTasks(tenantId);
    final now = DateTime.now();
    final deadline = now.add(Duration(days: days));

    return allTasks.where((t) {
      if (t.dueDate == null) return false;
      if (t.status == TaskStatus.done || t.status == TaskStatus.cancelled) {
        return false;
      }
      return t.dueDate!.isAfter(now) && t.dueDate!.isBefore(deadline);
    }).toList();
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
