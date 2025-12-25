import 'package:drift/drift.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/storage/database.dart';

/// Mock AppDatabase for testing
/// قاعدة بيانات وهمية للاختبارات
class MockAppDatabase extends Mock implements AppDatabase {
  final Map<String, Task> _tasks = {};
  final Map<String, Field> _fields = {};
  final List<OutboxData> _outbox = [];
  final List<SyncLog> _syncLogs = [];
  final List<SyncEvent> _syncEvents = [];

  int _nextOutboxId = 1;
  int _nextSyncLogId = 1;
  int _nextSyncEventId = 1;

  // Helper method to seed test data
  void seedTask(Task task) {
    _tasks[task.id] = task;
  }

  void seedField(Field field) {
    _fields[field.id] = field;
  }

  void seedOutboxItem(OutboxData item) {
    _outbox.add(item);
  }

  void clearAll() {
    _tasks.clear();
    _fields.clear();
    _outbox.clear();
    _syncLogs.clear();
    _syncEvents.clear();
  }

  // Task operations
  @override
  Future<List<Task>> getAllTasks(String tenantId) async {
    return _tasks.values
        .where((t) => t.tenantId == tenantId)
        .toList()
      ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
  }

  @override
  Future<List<Task>> getTasksForField(String fieldId) async {
    return _tasks.values
        .where((t) => t.fieldId == fieldId)
        .toList()
      ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
  }

  @override
  Future<List<Task>> getPendingTasks(String tenantId) async {
    return _tasks.values
        .where((t) =>
            t.tenantId == tenantId &&
            (t.status == 'open' || t.status == 'in_progress'))
        .toList()
      ..sort((a, b) {
        if (a.dueDate != null && b.dueDate != null) {
          return a.dueDate!.compareTo(b.dueDate!);
        }
        return 0;
      });
  }

  @override
  Future<Task?> getTaskById(String taskId) async {
    return _tasks[taskId];
  }

  @override
  Future<void> upsertTask(TasksCompanion task) async {
    final id = task.id.value;
    final existing = _tasks[id];

    if (existing != null) {
      // Update existing task
      _tasks[id] = Task(
        id: id,
        tenantId: task.tenantId.present ? task.tenantId.value : existing.tenantId,
        fieldId: task.fieldId.present ? task.fieldId.value : existing.fieldId,
        farmId: task.farmId.present ? task.farmId.value : existing.farmId,
        title: task.title.present ? task.title.value : existing.title,
        description: task.description.present ? task.description.value : existing.description,
        status: task.status.present ? task.status.value : existing.status,
        priority: task.priority.present ? task.priority.value : existing.priority,
        dueDate: task.dueDate.present ? task.dueDate.value : existing.dueDate,
        assignedTo: task.assignedTo.present ? task.assignedTo.value : existing.assignedTo,
        evidenceNotes: task.evidenceNotes.present ? task.evidenceNotes.value : existing.evidenceNotes,
        evidencePhotos: task.evidencePhotos.present ? task.evidencePhotos.value : existing.evidencePhotos,
        createdAt: existing.createdAt,
        updatedAt: task.updatedAt.present ? task.updatedAt.value : existing.updatedAt,
        synced: task.synced.present ? task.synced.value : existing.synced,
      );
    } else {
      // Create new task
      _tasks[id] = Task(
        id: id,
        tenantId: task.tenantId.value,
        fieldId: task.fieldId.value,
        farmId: task.farmId.value,
        title: task.title.value,
        description: task.description.value,
        status: task.status.value,
        priority: task.priority.value,
        dueDate: task.dueDate.value,
        assignedTo: task.assignedTo.value,
        evidenceNotes: task.evidenceNotes.value,
        evidencePhotos: task.evidencePhotos.value,
        createdAt: task.createdAt.value,
        updatedAt: task.updatedAt.value,
        synced: task.synced.value,
      );
    }
  }

  @override
  Future<void> markTaskDone({
    required String taskId,
    String? notes,
    List<String>? photos,
  }) async {
    final task = _tasks[taskId];
    if (task != null) {
      _tasks[taskId] = Task(
        id: task.id,
        tenantId: task.tenantId,
        fieldId: task.fieldId,
        farmId: task.farmId,
        title: task.title,
        description: task.description,
        status: 'done',
        priority: task.priority,
        dueDate: task.dueDate,
        assignedTo: task.assignedTo,
        evidenceNotes: notes,
        evidencePhotos: photos?.join(','),
        createdAt: task.createdAt,
        updatedAt: DateTime.now(),
        synced: false,
      );
    }
  }

  // Field operations
  @override
  Future<List<Field>> getAllFields(String tenantId) async {
    return _fields.values
        .where((f) => f.tenantId == tenantId && !f.isDeleted)
        .toList()
      ..sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
  }

  @override
  Future<Field?> getFieldById(String fieldId) async {
    return _fields[fieldId];
  }

  @override
  Future<void> upsertField(FieldsCompanion field) async {
    final id = field.id.value;
    final existing = _fields[id];

    if (existing != null) {
      _fields[id] = Field(
        id: id,
        remoteId: field.remoteId.present ? field.remoteId.value : existing.remoteId,
        tenantId: field.tenantId.present ? field.tenantId.value : existing.tenantId,
        farmId: field.farmId.present ? field.farmId.value : existing.farmId,
        name: field.name.present ? field.name.value : existing.name,
        cropType: field.cropType.present ? field.cropType.value : existing.cropType,
        boundary: field.boundary.present ? field.boundary.value : existing.boundary,
        centroid: field.centroid.present ? field.centroid.value : existing.centroid,
        areaHectares: field.areaHectares.present ? field.areaHectares.value : existing.areaHectares,
        status: field.status.present ? field.status.value : existing.status,
        ndviCurrent: field.ndviCurrent.present ? field.ndviCurrent.value : existing.ndviCurrent,
        ndviUpdatedAt: field.ndviUpdatedAt.present ? field.ndviUpdatedAt.value : existing.ndviUpdatedAt,
        synced: field.synced.present ? field.synced.value : existing.synced,
        isDeleted: field.isDeleted.present ? field.isDeleted.value : existing.isDeleted,
        createdAt: existing.createdAt,
        updatedAt: field.updatedAt.present ? field.updatedAt.value : existing.updatedAt,
        etag: field.etag.present ? field.etag.value : existing.etag,
        serverUpdatedAt: field.serverUpdatedAt.present ? field.serverUpdatedAt.value : existing.serverUpdatedAt,
      );
    }
  }

  // Outbox operations
  @override
  Future<void> queueOutboxItem({
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    required String method,
    required String payload,
    String? ifMatch,
  }) async {
    _outbox.add(OutboxData(
      id: _nextOutboxId++,
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: apiEndpoint,
      method: method,
      payload: payload,
      ifMatch: ifMatch,
      retryCount: 0,
      isSynced: false,
      createdAt: DateTime.now(),
    ));
  }

  @override
  Future<List<OutboxData>> getPendingOutbox({int limit = 50}) async {
    return _outbox
        .where((o) => !o.isSynced)
        .take(limit)
        .toList();
  }

  @override
  Future<void> markOutboxDone(int id) async {
    final index = _outbox.indexWhere((o) => o.id == id);
    if (index >= 0) {
      final item = _outbox[index];
      _outbox[index] = OutboxData(
        id: item.id,
        tenantId: item.tenantId,
        entityType: item.entityType,
        entityId: item.entityId,
        apiEndpoint: item.apiEndpoint,
        method: item.method,
        payload: item.payload,
        ifMatch: item.ifMatch,
        retryCount: item.retryCount,
        isSynced: true,
        createdAt: item.createdAt,
      );
    }
  }

  @override
  Future<void> cleanupOutbox() async {
    _outbox.removeWhere((o) => o.isSynced);
  }

  // Sync log operations
  @override
  Future<void> logSync({
    required String type,
    required String status,
    String? message,
  }) async {
    _syncLogs.add(SyncLog(
      id: _nextSyncLogId++,
      type: type,
      status: status,
      message: message,
      timestamp: DateTime.now(),
    ));
  }

  @override
  Future<List<SyncLog>> getRecentSyncLogs({int limit = 20}) async {
    final logs = _syncLogs.toList()
      ..sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return logs.take(limit).toList();
  }

  // Sync events operations
  @override
  Future<void> addSyncEvent({
    required String tenantId,
    required String type,
    required String message,
    String? entityType,
    String? entityId,
  }) async {
    _syncEvents.add(SyncEvent(
      id: _nextSyncEventId++,
      tenantId: tenantId,
      type: type,
      entityType: entityType,
      entityId: entityId,
      message: message,
      isRead: false,
      createdAt: DateTime.now(),
    ));
  }

  @override
  Future<List<SyncEvent>> getUnreadSyncEvents(String tenantId) async {
    return _syncEvents
        .where((e) => e.tenantId == tenantId && !e.isRead)
        .toList()
      ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
  }
}
