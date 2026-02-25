import 'dart:async';
import 'package:drift/drift.dart';
import 'package:latlong2/latlong.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/storage/database.dart';

/// Mock AppDatabase for testing
/// قاعدة بيانات وهمية للاختبارات
///
/// This mock provides a full in-memory implementation of the database
/// for unit and integration testing without SQLite dependency.
class MockAppDatabase extends Mock implements AppDatabase {
  final Map<String, Task> _tasks = {};
  final Map<String, Field> _fields = {};
  final List<OutboxData> _outbox = [];
  final List<SyncLog> _syncLogs = [];
  final List<SyncEvent> _syncEvents = [];

  int _nextOutboxId = 1;
  int _nextSyncLogId = 1;
  int _nextSyncEventId = 1;

  // Stream controllers for watchers
  final _fieldsController = StreamController<List<Field>>.broadcast();
  final _tasksController = StreamController<List<Task>>.broadcast();
  final _pendingOutboxCountController = StreamController<int>.broadcast();
  final _syncEventsCountController = StreamController<int>.broadcast();

  // Helper method to seed test data
  void seedTask(Task task) {
    _tasks[task.id] = task;
    _notifyTasksChanged();
  }

  void seedField(Field field) {
    _fields[field.id] = field;
    _notifyFieldsChanged(field.tenantId);
  }

  void seedOutboxItem(OutboxData item) {
    _outbox.add(item);
    _notifyOutboxChanged();
  }

  void clearAll() {
    _tasks.clear();
    _fields.clear();
    _outbox.clear();
    _syncLogs.clear();
    _syncEvents.clear();
  }

  void dispose() {
    _fieldsController.close();
    _tasksController.close();
    _pendingOutboxCountController.close();
    _syncEventsCountController.close();
  }

  // Notification helpers
  void _notifyFieldsChanged(String tenantId) {
    final fields = _fields.values
        .where((f) => f.tenantId == tenantId && !f.isDeleted)
        .toList()
      ..sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
    _fieldsController.add(fields);
  }

  void _notifyTasksChanged() {
    _tasksController.add(_tasks.values.toList());
  }

  void _notifyOutboxChanged() {
    final count = _outbox.where((o) => !o.isSynced).length;
    _pendingOutboxCountController.add(count);
  }

  void _notifySyncEventsChanged(String tenantId) {
    final count =
        _syncEvents.where((e) => e.tenantId == tenantId && !e.isRead).length;
    _syncEventsCountController.add(count);
  }

  // Task operations
  @override
  Future<List<Task>> getAllTasks(String tenantId) async {
    return _tasks.values.where((t) => t.tenantId == tenantId).toList()
      ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
  }

  @override
  Future<List<Task>> getTasksForField(String fieldId) async {
    return _tasks.values.where((t) => t.fieldId == fieldId).toList()
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
        tenantId:
            task.tenantId.present ? task.tenantId.value : existing.tenantId,
        fieldId: task.fieldId.present ? task.fieldId.value : existing.fieldId,
        farmId: task.farmId.present ? task.farmId.value : existing.farmId,
        title: task.title.present ? task.title.value : existing.title,
        description: task.description.present
            ? task.description.value
            : existing.description,
        status: task.status.present ? task.status.value : existing.status,
        priority:
            task.priority.present ? task.priority.value : existing.priority,
        dueDate: task.dueDate.present ? task.dueDate.value : existing.dueDate,
        assignedTo: task.assignedTo.present
            ? task.assignedTo.value
            : existing.assignedTo,
        evidenceNotes: task.evidenceNotes.present
            ? task.evidenceNotes.value
            : existing.evidenceNotes,
        evidencePhotos: task.evidencePhotos.present
            ? task.evidencePhotos.value
            : existing.evidencePhotos,
        createdAt: existing.createdAt,
        updatedAt:
            task.updatedAt.present ? task.updatedAt.value : existing.updatedAt,
        synced: task.synced.present ? task.synced.value : existing.synced,
      );
    } else {
      // Create new task - use defaults for absent values
      _tasks[id] = Task(
        id: id,
        tenantId: task.tenantId.value,
        fieldId: task.fieldId.value,
        farmId: task.farmId.present ? task.farmId.value : null,
        title: task.title.value,
        description: task.description.present ? task.description.value : null,
        status: task.status.present ? task.status.value : 'open',
        priority: task.priority.present ? task.priority.value : 'medium',
        dueDate: task.dueDate.present ? task.dueDate.value : null,
        assignedTo: task.assignedTo.present ? task.assignedTo.value : null,
        evidenceNotes:
            task.evidenceNotes.present ? task.evidenceNotes.value : null,
        evidencePhotos:
            task.evidencePhotos.present ? task.evidencePhotos.value : null,
        createdAt: task.createdAt.value,
        updatedAt: task.updatedAt.value,
        synced: task.synced.present ? task.synced.value : false,
      );
    }
    _notifyTasksChanged();
  }

  @override
  Future<void> upsertTasksFromServer(List<Map<String, dynamic>> items) async {
    for (final item in items) {
      final id = item['id'] as String;
      _tasks[id] = Task(
        id: id,
        tenantId: item['tenant_id'] as String,
        fieldId: item['field_id'] as String,
        farmId: item['farm_id'] as String?,
        title: item['title'] as String,
        description: item['description'] as String?,
        status: item['status'] as String? ?? 'open',
        priority: item['priority'] as String? ?? 'medium',
        dueDate: item['due_date'] != null
            ? DateTime.parse(item['due_date'] as String)
            : null,
        assignedTo: item['assigned_to'] as String?,
        evidenceNotes: item['evidence_notes'] as String?,
        evidencePhotos: item['evidence_photos'] != null
            ? (item['evidence_photos'] as List).join(',')
            : null,
        createdAt: DateTime.parse(item['created_at'] as String),
        updatedAt: DateTime.parse(item['updated_at'] as String),
        synced: true,
      );
    }
    _notifyTasksChanged();
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
      _notifyTasksChanged();
    }
  }

  @override
  Future<void> deleteTask(String taskId) async {
    _tasks.remove(taskId);
    _notifyTasksChanged();
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
  Stream<List<Field>> watchAllFields(String tenantId) {
    // Return initial data plus future updates
    return _fieldsController.stream.map((fields) =>
        fields.where((f) => f.tenantId == tenantId && !f.isDeleted).toList());
  }

  @override
  Future<Field?> getFieldById(String fieldId) async {
    return _fields[fieldId];
  }

  @override
  Future<List<Field>> getFieldsForFarm(String farmId) async {
    return _fields.values
        .where((f) => f.farmId == farmId && !f.isDeleted)
        .toList();
  }

  @override
  Future<void> insertField(FieldsCompanion field) async {
    final id = field.id.value;
    _fields[id] = Field(
      id: id,
      remoteId: field.remoteId.present ? field.remoteId.value : null,
      tenantId: field.tenantId.value,
      farmId: field.farmId.present ? field.farmId.value : null,
      name: field.name.value,
      cropType: field.cropType.present ? field.cropType.value : null,
      boundary: field.boundary.value,
      centroid: field.centroid.present ? field.centroid.value : null,
      areaHectares: field.areaHectares.value,
      status: field.status.present ? field.status.value : null,
      ndviCurrent: field.ndviCurrent.present ? field.ndviCurrent.value : null,
      ndviUpdatedAt:
          field.ndviUpdatedAt.present ? field.ndviUpdatedAt.value : null,
      synced: field.synced.present ? field.synced.value : false,
      isDeleted: field.isDeleted.present ? field.isDeleted.value : false,
      createdAt: field.createdAt.value,
      updatedAt: field.updatedAt.value,
      etag: field.etag.present ? field.etag.value : null,
      serverUpdatedAt:
          field.serverUpdatedAt.present ? field.serverUpdatedAt.value : null,
    );
    _notifyFieldsChanged(field.tenantId.value);
  }

  @override
  Future<void> upsertField(FieldsCompanion field) async {
    final id = field.id.value;
    final existing = _fields[id];

    if (existing != null) {
      _fields[id] = Field(
        id: id,
        remoteId:
            field.remoteId.present ? field.remoteId.value : existing.remoteId,
        tenantId:
            field.tenantId.present ? field.tenantId.value : existing.tenantId,
        farmId: field.farmId.present ? field.farmId.value : existing.farmId,
        name: field.name.present ? field.name.value : existing.name,
        cropType:
            field.cropType.present ? field.cropType.value : existing.cropType,
        boundary:
            field.boundary.present ? field.boundary.value : existing.boundary,
        centroid:
            field.centroid.present ? field.centroid.value : existing.centroid,
        areaHectares: field.areaHectares.present
            ? field.areaHectares.value
            : existing.areaHectares,
        status: field.status.present ? field.status.value : existing.status,
        ndviCurrent: field.ndviCurrent.present
            ? field.ndviCurrent.value
            : existing.ndviCurrent,
        ndviUpdatedAt: field.ndviUpdatedAt.present
            ? field.ndviUpdatedAt.value
            : existing.ndviUpdatedAt,
        synced: field.synced.present ? field.synced.value : existing.synced,
        isDeleted: field.isDeleted.present
            ? field.isDeleted.value
            : existing.isDeleted,
        createdAt: existing.createdAt,
        updatedAt: field.updatedAt.present
            ? field.updatedAt.value
            : existing.updatedAt,
        etag: field.etag.present ? field.etag.value : existing.etag,
        serverUpdatedAt: field.serverUpdatedAt.present
            ? field.serverUpdatedAt.value
            : existing.serverUpdatedAt,
      );
      _notifyFieldsChanged(existing.tenantId);
    }
  }

  @override
  Future<void> upsertFieldsFromServer(List<Map<String, dynamic>> items) async {
    for (final item in items) {
      final id = item['id'] as String;
      final tenantId = item['tenant_id'] as String;

      // Parse boundary from GeoJSON
      List<LatLng> boundary = [];
      LatLng? centroid;
      final geometry = item['geometry'];
      if (geometry != null && geometry['type'] == 'Polygon') {
        final coords = geometry['coordinates'][0] as List;
        boundary = coords.map((c) {
          final coord = c as List;
          return LatLng(
            (coord[1] as num).toDouble(),
            (coord[0] as num).toDouble(),
          );
        }).toList();

        if (boundary.isNotEmpty) {
          double sumLat = 0, sumLng = 0;
          for (final p in boundary) {
            sumLat += p.latitude;
            sumLng += p.longitude;
          }
          centroid = LatLng(sumLat / boundary.length, sumLng / boundary.length);
        }
      }

      _fields[id] = Field(
        id: id,
        remoteId: item['remote_id'] as String? ?? id,
        tenantId: tenantId,
        farmId: item['farm_id'] as String?,
        name: item['name'] as String,
        cropType: item['crop_type'] as String?,
        boundary: boundary,
        centroid: centroid,
        areaHectares: (item['area_hectares'] as num?)?.toDouble() ?? 0,
        status: item['status'] as String?,
        ndviCurrent: (item['ndvi_current'] as num?)?.toDouble(),
        ndviUpdatedAt: item['ndvi_updated_at'] != null
            ? DateTime.parse(item['ndvi_updated_at'] as String)
            : null,
        synced: true,
        isDeleted: false,
        createdAt: DateTime.parse(item['created_at'] as String),
        updatedAt: DateTime.parse(item['updated_at'] as String),
        etag: item['etag'] as String?,
        serverUpdatedAt: item['updated_at'] != null
            ? DateTime.parse(item['updated_at'] as String)
            : null,
      );
      _notifyFieldsChanged(tenantId);
    }
  }

  @override
  Future<void> updateFieldBoundary({
    required String fieldId,
    required List<LatLng> boundary,
    required LatLng? centroid,
    required double areaHectares,
  }) async {
    final field = _fields[fieldId];
    if (field != null) {
      _fields[fieldId] = Field(
        id: field.id,
        remoteId: field.remoteId,
        tenantId: field.tenantId,
        farmId: field.farmId,
        name: field.name,
        cropType: field.cropType,
        boundary: boundary,
        centroid: centroid,
        areaHectares: areaHectares,
        status: field.status,
        ndviCurrent: field.ndviCurrent,
        ndviUpdatedAt: field.ndviUpdatedAt,
        synced: false,
        isDeleted: field.isDeleted,
        createdAt: field.createdAt,
        updatedAt: DateTime.now(),
        etag: field.etag,
        serverUpdatedAt: field.serverUpdatedAt,
      );
      _notifyFieldsChanged(field.tenantId);
    }
  }

  @override
  Future<void> updateFieldNdvi({
    required String fieldId,
    required double ndviScore,
  }) async {
    final field = _fields[fieldId];
    if (field != null) {
      _fields[fieldId] = Field(
        id: field.id,
        remoteId: field.remoteId,
        tenantId: field.tenantId,
        farmId: field.farmId,
        name: field.name,
        cropType: field.cropType,
        boundary: field.boundary,
        centroid: field.centroid,
        areaHectares: field.areaHectares,
        status: field.status,
        ndviCurrent: ndviScore,
        ndviUpdatedAt: DateTime.now(),
        synced: field.synced,
        isDeleted: field.isDeleted,
        createdAt: field.createdAt,
        updatedAt: DateTime.now(),
        etag: field.etag,
        serverUpdatedAt: field.serverUpdatedAt,
      );
      _notifyFieldsChanged(field.tenantId);
    }
  }

  @override
  Future<void> softDeleteField(String fieldId) async {
    final field = _fields[fieldId];
    if (field != null) {
      _fields[fieldId] = Field(
        id: field.id,
        remoteId: field.remoteId,
        tenantId: field.tenantId,
        farmId: field.farmId,
        name: field.name,
        cropType: field.cropType,
        boundary: field.boundary,
        centroid: field.centroid,
        areaHectares: field.areaHectares,
        status: field.status,
        ndviCurrent: field.ndviCurrent,
        ndviUpdatedAt: field.ndviUpdatedAt,
        synced: false,
        isDeleted: true,
        createdAt: field.createdAt,
        updatedAt: DateTime.now(),
        etag: field.etag,
        serverUpdatedAt: field.serverUpdatedAt,
      );
      _notifyFieldsChanged(field.tenantId);
    }
  }

  @override
  Future<void> markFieldSynced(String fieldId, String? remoteId) async {
    final field = _fields[fieldId];
    if (field != null) {
      _fields[fieldId] = Field(
        id: field.id,
        remoteId: remoteId,
        tenantId: field.tenantId,
        farmId: field.farmId,
        name: field.name,
        cropType: field.cropType,
        boundary: field.boundary,
        centroid: field.centroid,
        areaHectares: field.areaHectares,
        status: field.status,
        ndviCurrent: field.ndviCurrent,
        ndviUpdatedAt: field.ndviUpdatedAt,
        synced: true,
        isDeleted: field.isDeleted,
        createdAt: field.createdAt,
        updatedAt: field.updatedAt,
        etag: field.etag,
        serverUpdatedAt: field.serverUpdatedAt,
      );
      _notifyFieldsChanged(field.tenantId);
    }
  }

  @override
  Future<List<Field>> getUnsyncedFields() async {
    return _fields.values.where((f) => !f.synced).toList();
  }

  @override
  Future<void> updateFieldWithEtag({
    required String fieldId,
    required String etag,
    DateTime? serverUpdatedAt,
  }) async {
    final field = _fields[fieldId];
    if (field != null) {
      _fields[fieldId] = Field(
        id: field.id,
        remoteId: field.remoteId,
        tenantId: field.tenantId,
        farmId: field.farmId,
        name: field.name,
        cropType: field.cropType,
        boundary: field.boundary,
        centroid: field.centroid,
        areaHectares: field.areaHectares,
        status: field.status,
        ndviCurrent: field.ndviCurrent,
        ndviUpdatedAt: field.ndviUpdatedAt,
        synced: true,
        isDeleted: field.isDeleted,
        createdAt: field.createdAt,
        updatedAt: field.updatedAt,
        etag: etag,
        serverUpdatedAt: serverUpdatedAt ?? DateTime.now(),
      );
      _notifyFieldsChanged(field.tenantId);
    }
  }

  // Outbox operations
  @override
  Future<void> addToOutbox(OutboxCompanion item) async {
    _outbox.add(OutboxData(
      id: _nextOutboxId++,
      tenantId: item.tenantId.value,
      entityType: item.entityType.value,
      entityId: item.entityId.value,
      apiEndpoint: item.apiEndpoint.value,
      method: item.method.value,
      payload: item.payload.value,
      ifMatch: item.ifMatch.value,
      retryCount: 0,
      isSynced: false,
      createdAt: DateTime.now(),
    ));
    _notifyOutboxChanged();
  }

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
    _notifyOutboxChanged();
  }

  @override
  Future<List<OutboxData>> getPendingOutbox({int limit = 50}) async {
    return _outbox.where((o) => !o.isSynced).take(limit).toList();
  }

  @override
  Future<OutboxData?> getOutboxItemById(int id) async {
    try {
      return _outbox.firstWhere((o) => o.id == id);
    } catch (e) {
      return null;
    }
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
      _notifyOutboxChanged();
    }
  }

  @override
  Future<void> bumpOutboxRetry(int id) async {
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
        retryCount: item.retryCount + 1,
        isSynced: item.isSynced,
        createdAt: item.createdAt,
      );
    }
  }

  @override
  Future<void> cleanupOutbox() async {
    _outbox.removeWhere((o) => o.isSynced);
    _notifyOutboxChanged();
  }

  @override
  Future<void> cleanupOldOutbox(
      {Duration olderThan = const Duration(days: 7)}) async {
    final cutoff = DateTime.now().subtract(olderThan);
    _outbox.removeWhere((o) => o.isSynced && o.createdAt.isBefore(cutoff));
    _notifyOutboxChanged();
  }

  @override
  Stream<int> watchPendingOutboxCount() {
    return _pendingOutboxCountController.stream;
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

  @override
  Stream<List<SyncLog>> watchRecentSyncLogs({int limit = 20}) {
    // For simplicity, return a stream that never updates
    // In real tests, you would want to add a controller
    return Stream.value(_syncLogs.take(limit).toList());
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
    _notifySyncEventsChanged(tenantId);
  }

  @override
  Future<List<SyncEvent>> getUnreadSyncEvents(String tenantId) async {
    return _syncEvents
        .where((e) => e.tenantId == tenantId && !e.isRead)
        .toList()
      ..sort((a, b) => b.createdAt.compareTo(a.createdAt));
  }

  @override
  Stream<int> watchUnreadEventsCount(String tenantId) {
    return _syncEventsCountController.stream;
  }

  @override
  Future<void> markSyncEventRead(int eventId) async {
    final index = _syncEvents.indexWhere((e) => e.id == eventId);
    if (index >= 0) {
      final event = _syncEvents[index];
      _syncEvents[index] = SyncEvent(
        id: event.id,
        tenantId: event.tenantId,
        type: event.type,
        entityType: event.entityType,
        entityId: event.entityId,
        message: event.message,
        isRead: true,
        createdAt: event.createdAt,
      );
      _notifySyncEventsChanged(event.tenantId);
    }
  }

  @override
  Future<void> markAllSyncEventsRead(String tenantId) async {
    for (int i = 0; i < _syncEvents.length; i++) {
      final event = _syncEvents[i];
      if (event.tenantId == tenantId && !event.isRead) {
        _syncEvents[i] = SyncEvent(
          id: event.id,
          tenantId: event.tenantId,
          type: event.type,
          entityType: event.entityType,
          entityId: event.entityId,
          message: event.message,
          isRead: true,
          createdAt: event.createdAt,
        );
      }
    }
    _notifySyncEventsChanged(tenantId);
  }

  // Health and maintenance operations
  @override
  Future<Map<String, dynamic>> checkHealth() async {
    return {
      'healthy': true,
      'fieldsCount': _fields.length,
      'tasksCount': _tasks.length,
      'pendingOutboxCount': _outbox.where((o) => !o.isSynced).length,
      'unreadEventsCount': _syncEvents.where((e) => !e.isRead).length,
      'schemaVersion': 4,
    };
  }

  @override
  Future<Map<String, dynamic>> getStatistics() async {
    return {
      'pageCount': 100,
      'pageSize': 4096,
      'estimatedSizeBytes': 409600,
      'unsyncedFields': _fields.values.where((f) => !f.synced).length,
      'unsyncedTasks': _tasks.values.where((t) => !t.synced).length,
    };
  }

  @override
  Future<void> clearTenantData(String tenantId) async {
    _tasks.removeWhere((_, t) => t.tenantId == tenantId);
    _fields.removeWhere((_, f) => f.tenantId == tenantId);
    _outbox.removeWhere((o) => o.tenantId == tenantId);
    _syncEvents.removeWhere((e) => e.tenantId == tenantId);
    _notifyOutboxChanged();
  }

  // Stream watchers for tasks
  @override
  Stream<List<Task>> watchTasksForField(String fieldId) {
    return _tasksController.stream
        .map((tasks) => tasks.where((t) => t.fieldId == fieldId).toList());
  }

  @override
  Stream<List<Task>> watchPendingTasks(String tenantId) {
    return _tasksController.stream.map((tasks) => tasks
        .where((t) =>
            t.tenantId == tenantId &&
            (t.status == 'open' || t.status == 'in_progress'))
        .toList());
  }

  // Transaction support (no-op for mock)
  @override
  Future<T> runInTransaction<T>(Future<T> Function() action) async {
    return action();
  }

  @override
  Future<void> runBatch(Function(Batch batch) operations) async {
    // For mock, just ignore batch operations
  }

  @override
  Future<void> vacuum() async {
    // No-op for mock
  }

  @override
  Future<void> analyze() async {
    // No-op for mock
  }

  @override
  Future<int> pruneOldOutboxItems(
      {Duration olderThan = const Duration(days: 7)}) async {
    final cutoff = DateTime.now().subtract(olderThan);
    final before = _outbox.length;
    _outbox.removeWhere((o) => o.isSynced && o.createdAt.isBefore(cutoff));
    return before - _outbox.length;
  }

  @override
  Future<int> getFailedOutboxCount({int maxRetries = 5}) async {
    return _outbox
        .where((o) => !o.isSynced && o.retryCount >= maxRetries)
        .length;
  }

  @override
  Future<void> resetFailedOutboxItems({int maxRetries = 5}) async {
    for (int i = 0; i < _outbox.length; i++) {
      final item = _outbox[i];
      if (!item.isSynced && item.retryCount >= maxRetries) {
        _outbox[i] = OutboxData(
          id: item.id,
          tenantId: item.tenantId,
          entityType: item.entityType,
          entityId: item.entityId,
          apiEndpoint: item.apiEndpoint,
          method: item.method,
          payload: item.payload,
          ifMatch: item.ifMatch,
          retryCount: 0,
          isSynced: item.isSynced,
          createdAt: item.createdAt,
        );
      }
    }
  }
}
