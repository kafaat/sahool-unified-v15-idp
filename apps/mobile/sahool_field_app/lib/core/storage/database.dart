import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'package:latlong2/latlong.dart';
import 'package:sqlite3/sqlite3.dart';
import 'package:sqlcipher_flutter_libs/sqlcipher_flutter_libs.dart';
import '../utils/app_logger.dart';
import 'converters/geo_converter.dart';
import 'database_encryption.dart';

part 'database.g.dart';

/// Tasks Table with performance indexes
@TableIndex(name: 'tasks_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'tasks_field_idx', columns: {#fieldId})
@TableIndex(name: 'tasks_status_idx', columns: {#status})
@TableIndex(name: 'tasks_synced_idx', columns: {#synced})
@TableIndex(name: 'tasks_tenant_status_idx', columns: {#tenantId, #status})
@TableIndex(name: 'tasks_created_idx', columns: {#createdAt})
class Tasks extends Table {
  TextColumn get id => text()();
  TextColumn get tenantId => text()();
  TextColumn get fieldId => text()();
  TextColumn get farmId => text().nullable()();
  TextColumn get title => text()();
  TextColumn get description => text().nullable()();
  TextColumn get status => text().withDefault(const Constant('open'))();
  TextColumn get priority => text().withDefault(const Constant('medium'))();
  DateTimeColumn get dueDate => dateTime().nullable()();
  TextColumn get assignedTo => text().nullable()();
  TextColumn get evidenceNotes => text().nullable()();
  TextColumn get evidencePhotos => text().nullable()(); // JSON array
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

/// Outbox Table (for offline-first sync with ETag support)
@TableIndex(name: 'outbox_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'outbox_synced_idx', columns: {#isSynced})
@TableIndex(name: 'outbox_entity_idx', columns: {#entityType, #entityId})
@TableIndex(name: 'outbox_created_idx', columns: {#createdAt})
@TableIndex(name: 'outbox_tenant_synced_idx', columns: {#tenantId, #isSynced})
class Outbox extends Table {
  IntColumn get id => integer().autoIncrement()();

  // Tenant isolation
  TextColumn get tenantId => text()();

  // Entity targeting (for conflict handling)
  TextColumn get entityType => text()(); // 'field', 'task', etc.
  TextColumn get entityId => text()();

  // API request details
  TextColumn get apiEndpoint => text()();
  TextColumn get method =>
      text().withDefault(const Constant('POST'))(); // POST/PUT/DELETE
  TextColumn get payload => text()(); // JSON payload

  // ETag for optimistic locking (PUT requests)
  TextColumn get ifMatch => text().nullable()();

  // Sync metadata
  IntColumn get retryCount => integer().withDefault(const Constant(0))();
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

/// Fields Cache Table (GIS-enabled) with performance indexes
@TableIndex(name: 'fields_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'fields_farm_idx', columns: {#farmId})
@TableIndex(name: 'fields_synced_idx', columns: {#synced})
@TableIndex(name: 'fields_deleted_idx', columns: {#isDeleted})
@TableIndex(name: 'fields_tenant_deleted_idx', columns: {#tenantId, #isDeleted})
@TableIndex(name: 'fields_updated_idx', columns: {#updatedAt})
@TableIndex(name: 'fields_remote_idx', columns: {#remoteId})
class Fields extends Table {
  TextColumn get id => text()();
  TextColumn get remoteId => text().nullable()(); // PostGIS ID
  TextColumn get tenantId => text()();
  TextColumn get farmId => text().nullable()();
  TextColumn get name => text().withLength(min: 1, max: 100)();
  TextColumn get cropType => text().nullable()();

  // GIS: Polygon boundary stored as JSON coordinates
  // Converted to/from List<LatLng> via GeoPolygonConverter
  TextColumn get boundary => text().map(const GeoPolygonConverter())();

  // GIS: Centroid point for quick map display
  TextColumn get centroid => text().map(const GeoPointConverter()).nullable()();

  RealColumn get areaHectares => real()();
  TextColumn get status => text().nullable()(); // active, fallow, etc.
  RealColumn get ndviCurrent => real().nullable()();
  DateTimeColumn get ndviUpdatedAt => dateTime().nullable()();

  // Sync metadata
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  BoolColumn get isDeleted => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();

  // ETag for Conflict Resolution (v3)
  TextColumn get etag => text().nullable()();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

/// Sync Log Table with performance indexes
@TableIndex(name: 'sync_logs_status_idx', columns: {#status})
@TableIndex(name: 'sync_logs_timestamp_idx', columns: {#timestamp})
@TableIndex(name: 'sync_logs_type_status_idx', columns: {#type, #status})
class SyncLogs extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get type => text()();
  TextColumn get status => text()(); // success, failed
  TextColumn get message => text().nullable()();
  DateTimeColumn get timestamp => dateTime()();
}

/// Sync Events Table - أحداث المزامنة والتعارضات
@TableIndex(name: 'sync_events_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'sync_events_read_idx', columns: {#isRead})
@TableIndex(name: 'sync_events_tenant_read_idx', columns: {#tenantId, #isRead})
@TableIndex(name: 'sync_events_created_idx', columns: {#createdAt})
class SyncEvents extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get type => text()(); // CONFLICT/INFO/ERROR
  TextColumn get entityType => text().nullable()(); // field, task
  TextColumn get entityId => text().nullable()();
  TextColumn get message => text()();
  BoolColumn get isRead => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

/// AI Skills Memory Table - stores skill invocations and responses
@TableIndex(name: 'ai_memory_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'ai_memory_field_idx', columns: {#fieldId})
@TableIndex(name: 'ai_memory_skill_idx', columns: {#skillName})
@TableIndex(name: 'ai_memory_synced_idx', columns: {#synced})
@TableIndex(
  name: 'ai_memory_tenant_skill_idx',
  columns: {#tenantId, #skillName},
)
@TableIndex(name: 'ai_memory_created_idx', columns: {#createdAt})
class AiMemoryTable extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get fieldId => text().nullable()();
  TextColumn get farmId => text().nullable()();
  TextColumn get skillName => text()();
  TextColumn get skillVersion => text().withDefault(const Constant('1.0.0'))();
  TextColumn get request => text()();
  TextColumn get response => text().nullable()();
  IntColumn get executionTimeMs => integer().nullable()();
  RealColumn get confidence => real().nullable()();
  TextColumn get status =>
      text().withDefault(const Constant('pending'))();
  TextColumn get errorMessage => text().nullable()();
  TextColumn get errorStack => text().nullable()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  TextColumn get syncChecksum => text().nullable()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get completedAt => dateTime().nullable()();
  DateTimeColumn get syncedAt => dateTime().nullable()();
}

/// AI Context Cache Table - stores compressed context snapshots
@TableIndex(name: 'ai_context_cache_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'ai_context_cache_field_idx', columns: {#fieldId})
@TableIndex(name: 'ai_context_cache_ttl_idx', columns: {#expiresAt})
class AiContextCacheTable extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get fieldId => text()();
  TextColumn get context => text()();
  TextColumn get contextHash => text()();
  IntColumn get sizeBytes => integer()();
  RealColumn get compressionRatio => real().nullable()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get expiresAt => dateTime()();
  BoolColumn get isExpired => boolean().withDefault(const Constant(false))();
  IntColumn get accessCount => integer().withDefault(const Constant(0))();
  DateTimeColumn get lastAccessedAt => dateTime().nullable()();
}

/// AI Knowledge Base Table - stores learned patterns from skills
@TableIndex(name: 'ai_kb_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'ai_kb_type_idx', columns: {#knowledgeType})
@TableIndex(name: 'ai_kb_accuracy_idx', columns: {#accuracy})
class AiKnowledgeBaseTable extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get tenantId => text()();
  TextColumn get knowledgeType => text()();
  TextColumn get domain => text().nullable()();
  TextColumn get condition => text()();
  TextColumn get recommendation => text()();
  TextColumn get reasoning => text().nullable()();
  RealColumn get accuracy => real()();
  IntColumn get applicableCount => integer().withDefault(const Constant(0))();
  IntColumn get successCount => integer().withDefault(const Constant(0))();
  TextColumn get sourceSkill => text()();
  TextColumn get metadata => text().nullable()();
  DateTimeColumn get discoveredAt =>
      dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get lastValidatedAt => dateTime().nullable()();
}

@DriftDatabase(tables: [Tasks, Outbox, Fields, SyncLogs, SyncEvents, AiMemoryTable, AiContextCacheTable, AiKnowledgeBaseTable])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 5; // v5: AI Memory tables

  @override
  MigrationStrategy get migration => MigrationStrategy(
        onCreate: (Migrator m) async {
          await m.createAll();
        },
        onUpgrade: (Migrator m, int from, int to) async {
          if (from < 2) {
            // Migration from v1 to v2: recreate fields table with GIS columns
            await m.deleteTable('fields');
            await m.createTable(fields);
          }
          if (from < 3) {
            // Migration to v3: Add ETag support + SyncEvents
            await m.addColumn(fields, fields.etag);
            await m.addColumn(fields, fields.serverUpdatedAt);
            await m.createTable(syncEvents);
          }
          if (from < 4) {
            // Migration to v4: Unified Outbox schema with ETag support
            // Recreate outbox table with new structure
            await m.deleteTable('outbox');
            await m.createTable(outbox);
          }
          if (from < 5) {
            // Migration to v5: AI Memory tables
            await m.createTable(aiMemoryTable);
            await m.createTable(aiContextCacheTable);
            await m.createTable(aiKnowledgeBaseTable);
          }
        },
      );

  // ============================================================
  // Tasks Operations
  // ============================================================

  /// Get all tasks for a field
  Future<List<Task>> getTasksForField(String fieldId) {
    return (select(tasks)
          ..where((t) => t.fieldId.equals(fieldId))
          ..orderBy([(t) => OrderingTerm.desc(t.createdAt)]))
        .get();
  }

  /// Get all tasks for tenant
  Future<List<Task>> getAllTasks(String tenantId) {
    return (select(tasks)
          ..where((t) => t.tenantId.equals(tenantId))
          ..orderBy([(t) => OrderingTerm.desc(t.createdAt)]))
        .get();
  }

  /// Get pending tasks (open or in_progress)
  Future<List<Task>> getPendingTasks(String tenantId) {
    return (select(tasks)
          ..where((t) => t.tenantId.equals(tenantId))
          ..where((t) => t.status.isIn(['open', 'in_progress']))
          ..orderBy([
            (t) => OrderingTerm.asc(t.dueDate),
            (t) => OrderingTerm.desc(t.priority),
          ]))
        .get();
  }

  /// Get task by ID
  Future<Task?> getTaskById(String taskId) {
    return (select(tasks)..where((t) => t.id.equals(taskId))).getSingleOrNull();
  }

  /// Insert or update task
  Future<void> upsertTask(TasksCompanion task) {
    return into(tasks).insertOnConflictUpdate(task);
  }

  /// Bulk insert tasks from server
  Future<void> upsertTasksFromServer(List<Map<String, dynamic>> items) async {
    await batch((batch) {
      for (final item in items) {
        batch.insert(
          tasks,
          TasksCompanion.insert(
            id: item['id'],
            tenantId: item['tenant_id'],
            fieldId: item['field_id'],
            farmId: Value(item['farm_id']),
            title: item['title'],
            description: Value(item['description']),
            status: Value(item['status'] ?? 'open'),
            priority: Value(item['priority'] ?? 'medium'),
            dueDate: Value(item['due_date'] != null
                ? DateTime.parse(item['due_date'])
                : null),
            assignedTo: Value(item['assigned_to']),
            evidenceNotes: Value(item['evidence_notes']),
            evidencePhotos: Value(item['evidence_photos'] != null
                ? (item['evidence_photos'] as List).join(',')
                : null),
            createdAt: DateTime.parse(item['created_at']),
            updatedAt: DateTime.parse(item['updated_at']),
            synced: const Value(true),
          ),
          onConflict: DoUpdate((old) => TasksCompanion(
                status: Value(item['status'] ?? 'open'),
                updatedAt: Value(DateTime.parse(item['updated_at'])),
                synced: const Value(true),
              )),
        );
      }
    });
  }

  /// Mark task as done locally
  Future<void> markTaskDone({
    required String taskId,
    String? notes,
    List<String>? photos,
  }) async {
    await (update(tasks)..where((t) => t.id.equals(taskId))).write(
      TasksCompanion(
        status: const Value('done'),
        evidenceNotes: Value(notes),
        evidencePhotos: Value(photos?.join(',')),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ),
    );
  }

  // ============================================================
  // Outbox Operations (ETag-enabled for Conflict Resolution)
  // ============================================================

  /// Add item to outbox
  Future<void> addToOutbox(OutboxCompanion item) {
    return into(outbox).insert(item);
  }

  /// Add entity operation to outbox (helper method)
  Future<void> queueOutboxItem({
    required String tenantId,
    required String entityType,
    required String entityId,
    required String apiEndpoint,
    required String method,
    required String payload,
    String? ifMatch,
  }) {
    return into(outbox).insert(OutboxCompanion.insert(
      tenantId: tenantId,
      entityType: entityType,
      entityId: entityId,
      apiEndpoint: apiEndpoint,
      method: Value(method),
      payload: payload,
      ifMatch: Value(ifMatch),
    ));
  }

  /// Get pending outbox items (not synced)
  Future<List<OutboxData>> getPendingOutbox({int limit = 50}) {
    return (select(outbox)
          ..where((o) => o.isSynced.equals(false))
          ..orderBy([(o) => OrderingTerm.asc(o.createdAt)])
          ..limit(limit))
        .get();
  }

  /// Mark outbox item as done (synced)
  Future<void> markOutboxDone(int id) async {
    await (update(outbox)..where((o) => o.id.equals(id))).write(
      const OutboxCompanion(isSynced: Value(true)),
    );
  }

  /// Increment retry count
  Future<void> bumpOutboxRetry(int id) async {
    await customStatement(
      'UPDATE outbox SET retry_count = retry_count + 1 WHERE id = ?',
      [id],
    );
  }

  /// Delete synced outbox items (cleanup)
  Future<void> cleanupOutbox() async {
    await (delete(outbox)..where((o) => o.isSynced.equals(true))).go();
  }

  /// Get outbox item by ID
  Future<OutboxData?> getOutboxItemById(int id) {
    return (select(outbox)..where((o) => o.id.equals(id))).getSingleOrNull();
  }

  /// Delete outbox items older than given duration
  Future<void> cleanupOldOutbox(
      {Duration olderThan = const Duration(days: 7)}) async {
    final cutoff = DateTime.now().subtract(olderThan);
    await (delete(outbox)
          ..where((o) => o.isSynced.equals(true))
          ..where((o) => o.createdAt.isSmallerThanValue(cutoff)))
        .go();
  }

  // ============================================================
  // Sync Log Operations
  // ============================================================

  /// Add sync log entry
  Future<void> logSync({
    required String type,
    required String status,
    String? message,
  }) {
    return into(syncLogs).insert(SyncLogsCompanion.insert(
      type: type,
      status: status,
      message: Value(message),
      timestamp: DateTime.now(),
    ));
  }

  /// Get recent sync logs
  Future<List<SyncLog>> getRecentSyncLogs({int limit = 20}) {
    return (select(syncLogs)
          ..orderBy([(l) => OrderingTerm.desc(l.timestamp)])
          ..limit(limit))
        .get();
  }

  // ============================================================
  // Fields Operations (GIS)
  // ============================================================

  /// Get all fields for tenant (excluding soft-deleted)
  Future<List<Field>> getAllFields(String tenantId) {
    return (select(fields)
          ..where((f) => f.tenantId.equals(tenantId))
          ..where((f) => f.isDeleted.equals(false))
          ..orderBy([(f) => OrderingTerm.desc(f.updatedAt)]))
        .get();
  }

  /// Watch all fields for tenant (live stream)
  Stream<List<Field>> watchAllFields(String tenantId) {
    return (select(fields)
          ..where((f) => f.tenantId.equals(tenantId))
          ..where((f) => f.isDeleted.equals(false))
          ..orderBy([(f) => OrderingTerm.desc(f.updatedAt)]))
        .watch();
  }

  /// Get field by ID
  Future<Field?> getFieldById(String fieldId) {
    return (select(fields)..where((f) => f.id.equals(fieldId)))
        .getSingleOrNull();
  }

  /// Get fields for a farm
  Future<List<Field>> getFieldsForFarm(String farmId) {
    return (select(fields)
          ..where((f) => f.farmId.equals(farmId))
          ..where((f) => f.isDeleted.equals(false)))
        .get();
  }

  /// Insert or update field
  Future<void> upsertField(FieldsCompanion field) {
    return into(fields).insertOnConflictUpdate(field);
  }

  /// Insert new field (offline-first)
  Future<void> insertField(FieldsCompanion field) {
    return into(fields).insert(field);
  }

  /// Update field boundary (GIS)
  Future<void> updateFieldBoundary({
    required String fieldId,
    required List<LatLng> boundary,
    required LatLng? centroid,
    required double areaHectares,
  }) async {
    await (update(fields)..where((f) => f.id.equals(fieldId))).write(
      FieldsCompanion(
        boundary: Value(boundary),
        centroid: Value(centroid),
        areaHectares: Value(areaHectares),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ),
    );
  }

  /// Update field NDVI
  Future<void> updateFieldNdvi({
    required String fieldId,
    required double ndviScore,
  }) async {
    await (update(fields)..where((f) => f.id.equals(fieldId))).write(
      FieldsCompanion(
        ndviCurrent: Value(ndviScore),
        ndviUpdatedAt: Value(DateTime.now()),
        updatedAt: Value(DateTime.now()),
      ),
    );
  }

  /// Soft delete field
  Future<void> softDeleteField(String fieldId) async {
    await (update(fields)..where((f) => f.id.equals(fieldId))).write(
      FieldsCompanion(
        isDeleted: const Value(true),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ),
    );
  }

  /// Mark field as synced
  Future<void> markFieldSynced(String fieldId, String? remoteId) async {
    await (update(fields)..where((f) => f.id.equals(fieldId))).write(
      FieldsCompanion(
        remoteId: Value(remoteId),
        synced: const Value(true),
      ),
    );
  }

  /// Get unsynced fields
  Future<List<Field>> getUnsyncedFields() {
    return (select(fields)..where((f) => f.synced.equals(false))).get();
  }

  /// Bulk insert fields from server
  Future<void> upsertFieldsFromServer(List<Map<String, dynamic>> items) async {
    await batch((batch) {
      for (final item in items) {
        // Parse GeoJSON geometry to List<LatLng>
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

          // Calculate centroid
          if (boundary.isNotEmpty) {
            double sumLat = 0, sumLng = 0;
            for (final p in boundary) {
              sumLat += p.latitude;
              sumLng += p.longitude;
            }
            centroid =
                LatLng(sumLat / boundary.length, sumLng / boundary.length);
          }
        }

        batch.insert(
          fields,
          FieldsCompanion.insert(
            id: item['id'],
            remoteId: Value(item['remote_id'] ?? item['id']),
            tenantId: item['tenant_id'],
            farmId: Value(item['farm_id']),
            name: item['name'],
            cropType: Value(item['crop_type']),
            boundary: boundary,
            centroid: Value(centroid),
            areaHectares: (item['area_hectares'] as num?)?.toDouble() ?? 0,
            status: Value(item['status']),
            ndviCurrent: Value((item['ndvi_current'] as num?)?.toDouble()),
            ndviUpdatedAt: Value(item['ndvi_updated_at'] != null
                ? DateTime.parse(item['ndvi_updated_at'])
                : null),
            createdAt: DateTime.parse(item['created_at']),
            updatedAt: DateTime.parse(item['updated_at']),
            synced: const Value(true),
          ),
          onConflict: DoUpdate((old) => FieldsCompanion(
                name: Value(item['name']),
                boundary: Value(boundary),
                centroid: Value(centroid),
                areaHectares:
                    Value((item['area_hectares'] as num?)?.toDouble() ?? 0),
                ndviCurrent: Value((item['ndvi_current'] as num?)?.toDouble()),
                updatedAt: Value(DateTime.parse(item['updated_at'])),
                synced: const Value(true),
              )),
        );
      }
    });
  }

  // ============================================================
  // SyncEvents Operations (Conflict Notifications)
  // ============================================================

  /// Get unread sync events for tenant
  Future<List<SyncEvent>> getUnreadSyncEvents(String tenantId) {
    return (select(syncEvents)
          ..where((e) => e.tenantId.equals(tenantId))
          ..where((e) => e.isRead.equals(false))
          ..orderBy([(e) => OrderingTerm.desc(e.createdAt)]))
        .get();
  }

  /// Watch unread sync events count
  Stream<int> watchUnreadEventsCount(String tenantId) {
    final query = selectOnly(syncEvents)
      ..where(syncEvents.tenantId.equals(tenantId))
      ..where(syncEvents.isRead.equals(false))
      ..addColumns([syncEvents.id.count()]);
    return query
        .map((row) => row.read(syncEvents.id.count()) ?? 0)
        .watchSingle();
  }

  /// Add sync event
  Future<void> addSyncEvent({
    required String tenantId,
    required String type,
    required String message,
    String? entityType,
    String? entityId,
  }) {
    return into(syncEvents).insert(SyncEventsCompanion.insert(
      tenantId: tenantId,
      type: type,
      message: message,
      entityType: Value(entityType),
      entityId: Value(entityId),
    ));
  }

  /// Mark sync event as read
  Future<void> markSyncEventRead(int eventId) async {
    await (update(syncEvents)..where((e) => e.id.equals(eventId))).write(
      const SyncEventsCompanion(isRead: Value(true)),
    );
  }

  /// Mark all sync events as read for tenant
  Future<void> markAllSyncEventsRead(String tenantId) async {
    await (update(syncEvents)
          ..where((e) => e.tenantId.equals(tenantId))
          ..where((e) => e.isRead.equals(false)))
        .write(const SyncEventsCompanion(isRead: Value(true)));
  }

  /// Update field with ETag from server
  Future<void> updateFieldWithEtag({
    required String fieldId,
    required String etag,
    DateTime? serverUpdatedAt,
  }) async {
    await (update(fields)..where((f) => f.id.equals(fieldId))).write(
      FieldsCompanion(
        etag: Value(etag),
        serverUpdatedAt: Value(serverUpdatedAt ?? DateTime.now()),
        synced: const Value(true),
      ),
    );
  }

  // ============================================================
  // Transaction Support
  // ============================================================

  /// Execute multiple operations in a transaction
  ///
  /// Provides atomic execution - all operations succeed or all fail
  /// Usage:
  /// ```dart
  /// await db.runInTransaction(() async {
  ///   await db.insertField(field1);
  ///   await db.insertField(field2);
  ///   await db.addToOutbox(outboxItem);
  /// });
  /// ```
  Future<T> runInTransaction<T>(Future<T> Function() action) async {
    return transaction(action);
  }

  /// Execute batch operations efficiently
  ///
  /// All operations are executed in a single transaction
  Future<void> runBatch(void Function(Batch batch) operations) async {
    await batch(operations);
  }

  // ============================================================
  // Stream Watchers
  // ============================================================

  /// Watch tasks for a specific field (live stream)
  Stream<List<Task>> watchTasksForField(String fieldId) {
    return (select(tasks)
          ..where((t) => t.fieldId.equals(fieldId))
          ..orderBy([(t) => OrderingTerm.desc(t.createdAt)]))
        .watch();
  }

  /// Watch pending tasks for tenant (live stream)
  Stream<List<Task>> watchPendingTasks(String tenantId) {
    return (select(tasks)
          ..where((t) => t.tenantId.equals(tenantId))
          ..where((t) => t.status.isIn(['open', 'in_progress']))
          ..orderBy([
            (t) => OrderingTerm.asc(t.dueDate),
            (t) => OrderingTerm.desc(t.priority),
          ]))
        .watch();
  }

  /// Watch outbox count (for sync indicator)
  Stream<int> watchPendingOutboxCount() {
    final query = selectOnly(outbox)
      ..where(outbox.isSynced.equals(false))
      ..addColumns([outbox.id.count()]);
    return query.map((row) => row.read(outbox.id.count()) ?? 0).watchSingle();
  }

  /// Watch sync logs (live stream)
  Stream<List<SyncLog>> watchRecentSyncLogs({int limit = 20}) {
    return (select(syncLogs)
          ..orderBy([(l) => OrderingTerm.desc(l.timestamp)])
          ..limit(limit))
        .watch();
  }

  // ============================================================
  // Database Health and Maintenance
  // ============================================================

  /// Check database health
  ///
  /// Returns a map with health indicators
  Future<Map<String, dynamic>> checkHealth() async {
    try {
      // Check basic connectivity
      await customSelect('SELECT 1').get();

      // Get table counts
      final fieldsCount = await (selectOnly(fields)
            ..addColumns([fields.id.count()]))
          .map((row) => row.read(fields.id.count()) ?? 0)
          .getSingle();

      final tasksCount = await (selectOnly(tasks)
            ..addColumns([tasks.id.count()]))
          .map((row) => row.read(tasks.id.count()) ?? 0)
          .getSingle();

      final pendingOutboxCount = await (selectOnly(outbox)
            ..where(outbox.isSynced.equals(false))
            ..addColumns([outbox.id.count()]))
          .map((row) => row.read(outbox.id.count()) ?? 0)
          .getSingle();

      final unreadEventsCount = await (selectOnly(syncEvents)
            ..where(syncEvents.isRead.equals(false))
            ..addColumns([syncEvents.id.count()]))
          .map((row) => row.read(syncEvents.id.count()) ?? 0)
          .getSingle();

      return {
        'healthy': true,
        'fieldsCount': fieldsCount,
        'tasksCount': tasksCount,
        'pendingOutboxCount': pendingOutboxCount,
        'unreadEventsCount': unreadEventsCount,
        'schemaVersion': schemaVersion,
      };
    } catch (e) {
      return {
        'healthy': false,
        'error': e.toString(),
      };
    }
  }

  /// Vacuum database to reclaim space
  ///
  /// Should be called periodically during app maintenance
  Future<void> vacuum() async {
    await customStatement('VACUUM;');
    AppLogger.i('Database vacuumed', tag: 'Database');
  }

  /// Analyze database for query optimization
  Future<void> analyze() async {
    await customStatement('ANALYZE;');
    AppLogger.i('Database analyzed', tag: 'Database');
  }

  /// Clear all data for a specific tenant
  ///
  /// Use with caution - this permanently deletes data
  Future<void> clearTenantData(String tenantId) async {
    await transaction(() async {
      await (delete(tasks)..where((t) => t.tenantId.equals(tenantId))).go();
      await (delete(fields)..where((f) => f.tenantId.equals(tenantId))).go();
      await (delete(outbox)..where((o) => o.tenantId.equals(tenantId))).go();
      await (delete(syncEvents)..where((e) => e.tenantId.equals(tenantId)))
          .go();
    });
    AppLogger.i('Cleared tenant data',
        tag: 'Database', data: {'tenantId': tenantId});
  }

  /// Get database statistics
  Future<Map<String, dynamic>> getStatistics() async {
    final stats = <String, dynamic>{};

    // Get page count and size
    try {
      final pageCount = await customSelect('PRAGMA page_count;')
          .map((row) => row.read<int>('page_count'))
          .getSingle();
      final pageSize = await customSelect('PRAGMA page_size;')
          .map((row) => row.read<int>('page_size'))
          .getSingle();

      stats['pageCount'] = pageCount;
      stats['pageSize'] = pageSize;
      stats['estimatedSizeBytes'] = pageCount * pageSize;
    } catch (e) {
      stats['sizeError'] = e.toString();
    }

    // Get unsynced counts
    final unsyncedFields = await (selectOnly(fields)
          ..where(fields.synced.equals(false))
          ..addColumns([fields.id.count()]))
        .map((row) => row.read(fields.id.count()) ?? 0)
        .getSingle();

    final unsyncedTasks = await (selectOnly(tasks)
          ..where(tasks.synced.equals(false))
          ..addColumns([tasks.id.count()]))
        .map((row) => row.read(tasks.id.count()) ?? 0)
        .getSingle();

    stats['unsyncedFields'] = unsyncedFields;
    stats['unsyncedTasks'] = unsyncedTasks;

    return stats;
  }

  // ============================================================
  // Utility Methods
  // ============================================================

  /// Delete task by ID
  Future<void> deleteTask(String taskId) async {
    await (delete(tasks)..where((t) => t.id.equals(taskId))).go();
  }

  /// Delete all synced outbox items older than specified duration
  Future<int> pruneOldOutboxItems(
      {Duration olderThan = const Duration(days: 7)}) async {
    final cutoff = DateTime.now().subtract(olderThan);
    return (delete(outbox)
          ..where((o) => o.isSynced.equals(true))
          ..where((o) => o.createdAt.isSmallerThanValue(cutoff)))
        .go();
  }

  /// Get count of failed outbox items (retry count exceeded)
  Future<int> getFailedOutboxCount({int maxRetries = 5}) async {
    return (selectOnly(outbox)
          ..where(outbox.isSynced.equals(false))
          ..where(outbox.retryCount.isBiggerOrEqualValue(maxRetries))
          ..addColumns([outbox.id.count()]))
        .map((row) => row.read(outbox.id.count()) ?? 0)
        .getSingle();
  }

  /// Reset retry count for failed outbox items
  Future<void> resetFailedOutboxItems({int maxRetries = 5}) async {
    await (update(outbox)
          ..where((o) => o.isSynced.equals(false))
          ..where((o) => o.retryCount.isBiggerOrEqualValue(maxRetries)))
        .write(const OutboxCompanion(retryCount: Value(0)));
  }
}

/// Open encrypted database connection with SQLCipher
///
/// Features:
/// - 256-bit AES encryption using SQLCipher
/// - Secure key storage in platform keychain/keystore
/// - Automatic migration from unencrypted to encrypted database
/// - Backward compatibility support
/// - Robust error handling with retry mechanism
/// - Database integrity verification
LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    const maxRetries = 3;
    const retryDelay = Duration(milliseconds: 500);

    for (int attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await _initializeDatabase();
      } catch (e, stackTrace) {
        AppLogger.e(
          'Database initialization attempt $attempt failed',
          tag: 'Database',
          error: e,
          stackTrace: stackTrace,
        );

        if (attempt < maxRetries) {
          await Future<void>.delayed(retryDelay * attempt);
        } else {
          AppLogger.critical(
            'Database initialization failed after $maxRetries attempts',
            tag: 'Database',
            error: e,
          );
          rethrow;
        }
      }
    }

    // This should never be reached, but Dart requires a return
    throw StateError('Database initialization failed unexpectedly');
  });
}

/// Initialize database with encryption and migrations
Future<QueryExecutor> _initializeDatabase() async {
  // Ensure SQLCipher native library is loaded
  await applyWorkaroundToOpenSqlCipherOnOldAndroidVersions();

  final dbFolder = await getApplicationDocumentsDirectory();
  final dbPath = p.join(dbFolder.path, 'sahool_field.db');
  final dbFile = File(dbPath);
  final oldDbPath = p.join(dbFolder.path, 'sahool_field_unencrypted.db');

  // Initialize encryption key manager
  final encryption = DatabaseEncryption();

  // Check if we need to migrate from unencrypted database
  if (!await encryption.hasKey() && dbFile.existsSync()) {
    AppLogger.i('Migrating from unencrypted to encrypted database',
        tag: 'Database');

    // Backup unencrypted database
    await dbFile.copy(oldDbPath);
    AppLogger.i('Backup created', tag: 'Database', data: {'path': oldDbPath});

    // Generate new encryption key
    final encryptionKey = await encryption.getOrCreateKey();

    // Migrate to encrypted database
    await _migrateToEncryptedDatabase(
      dbPath,
      oldDbPath,
      encryptionKey,
      encryption,
    );

    AppLogger.i('Migration to encrypted database completed', tag: 'Database');
  } else if (!await encryption.hasKey()) {
    // First time setup - generate encryption key
    await encryption.getOrCreateKey();
    AppLogger.i('New encryption key generated', tag: 'Database');
  }

  // Get encryption key for opening database
  final encryptionKey = await encryption.getOrCreateKey();

  // Open database with encryption
  final database = NativeDatabase.createInBackground(
    dbFile,
    setup: (database) {
      _configureDatabase(database, encryption, encryptionKey);
    },
  );

  return database;
}

/// Configure database with encryption and optimizations
void _configureDatabase(
  Database database,
  DatabaseEncryption encryption,
  String encryptionKey,
) {
  // Set SQLCipher encryption key
  final pragma = encryption.getSqlCipherPragma(encryptionKey);
  database.execute(pragma);

  // Configure SQLCipher for better performance and security
  // Use SQLCipher 4.x compatibility
  database.execute('PRAGMA cipher_compatibility = 4;');

  // Optimize for mobile devices
  database.execute('PRAGMA cipher_page_size = 4096;');
  database.execute('PRAGMA kdf_iter = 64000;');
  database.execute('PRAGMA cipher_hmac_algorithm = HMAC_SHA512;');
  database.execute('PRAGMA cipher_kdf_algorithm = PBKDF2_HMAC_SHA512;');

  // Standard SQLite optimizations
  database.execute('PRAGMA foreign_keys = ON;');
  database.execute('PRAGMA journal_mode = WAL;');
  database.execute('PRAGMA synchronous = NORMAL;');
  database.execute('PRAGMA temp_store = MEMORY;');
  database.execute('PRAGMA mmap_size = 30000000000;');

  // Set busy timeout to handle concurrent access
  database.execute('PRAGMA busy_timeout = 5000;');

  // Verify database integrity
  _verifyDatabaseIntegrity(database);
}

/// Verify database integrity
void _verifyDatabaseIntegrity(Database database) {
  try {
    final result = database.select('PRAGMA integrity_check;');
    if (result.isNotEmpty && result.first['integrity_check'] != 'ok') {
      AppLogger.w(
        'Database integrity check warning',
        tag: 'Database',
        data: {'result': result.first['integrity_check']},
      );
    }
  } catch (e) {
    // Log but don't fail - the database might still be usable
    AppLogger.w('Could not verify database integrity', tag: 'Database');
  }
}

/// Migrate unencrypted database to encrypted database
///
/// This function:
/// 1. Opens the old unencrypted database
/// 2. Creates a new encrypted database
/// 3. Copies all data using table-by-table migration
/// 4. Verifies the migration
/// 5. Removes the old database file
///
/// Security Note: Uses hex key format to avoid SQL injection
Future<void> _migrateToEncryptedDatabase(
  String newDbPath,
  String oldDbPath,
  String encryptionKey,
  DatabaseEncryption encryption,
) async {
  final tempNewPath = '$newDbPath.encrypted';
  final tempNewFile = File(tempNewPath);
  final lockFile = File('$newDbPath.migration.lock');

  // Check for existing migration lock (crash recovery)
  if (lockFile.existsSync()) {
    AppLogger.w(
        'Found migration lock file - previous migration may have failed',
        tag: 'Database');
    // Clean up any partial migration
    if (tempNewFile.existsSync()) {
      await tempNewFile.delete();
    }
    await lockFile.delete();
  }

  // Remove temporary file if it exists
  if (tempNewFile.existsSync()) {
    await tempNewFile.delete();
  }

  // Create lock file to track migration state
  await lockFile.create();

  try {
    // Get hex key for safe SQL construction
    final hexKey = encryption.getHexKey(encryptionKey);

    // Open the old unencrypted database
    final oldDb = sqlite3.open(oldDbPath);

    try {
      // Attach new encrypted database using hex key format (safer than string escaping)
      // The x'...' format is a SQLite blob literal which is safe from injection
      oldDb.execute(
          "ATTACH DATABASE '$tempNewPath' AS encrypted KEY \"x'$hexKey'\";");

      // Configure SQLCipher settings for the attached database
      oldDb.execute('PRAGMA encrypted.cipher_compatibility = 4;');
      oldDb.execute('PRAGMA encrypted.cipher_page_size = 4096;');
      oldDb.execute('PRAGMA encrypted.kdf_iter = 64000;');
      oldDb.execute('PRAGMA encrypted.cipher_hmac_algorithm = HMAC_SHA512;');
      oldDb.execute(
          'PRAGMA encrypted.cipher_kdf_algorithm = PBKDF2_HMAC_SHA512;');

      // Export all data to encrypted database
      // Use sqlcipher_export() if available, otherwise use table-by-table copy
      try {
        oldDb.execute('SELECT sqlcipher_export("encrypted");');
        AppLogger.i('Used sqlcipher_export for migration', tag: 'Database');
      } catch (e) {
        // Fallback: Copy schema and data manually with transaction
        AppLogger.i('Using manual migration (sqlcipher_export not available)',
            tag: 'Database');

        // Begin transaction for data integrity
        oldDb.execute('BEGIN EXCLUSIVE TRANSACTION;');

        try {
          // Get all tables (excluding internal sqlite tables)
          final tables = oldDb.select(
            "SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'android_%' ORDER BY name",
          );

          for (final table in tables) {
            final tableName = table['name'] as String;
            final createSql = table['sql'] as String?;

            if (createSql != null && createSql.isNotEmpty) {
              // Validate table name to prevent injection (alphanumeric and underscore only)
              if (!RegExp(r'^[a-zA-Z_][a-zA-Z0-9_]*$').hasMatch(tableName)) {
                AppLogger.w('Skipping table with invalid name',
                    tag: 'Database', data: {'table': tableName});
                continue;
              }

              // Create table in encrypted database
              final encryptedCreateSql = createSql.replaceFirst(
                RegExp(r'CREATE TABLE\s+', caseSensitive: false),
                'CREATE TABLE IF NOT EXISTS encrypted.',
              );
              oldDb.execute(encryptedCreateSql);

              // Copy data
              oldDb.execute(
                  'INSERT OR REPLACE INTO encrypted."$tableName" SELECT * FROM main."$tableName";');

              AppLogger.d('Migrated table',
                  tag: 'Database', data: {'table': tableName});
            }
          }

          // Copy indices
          final indices = oldDb.select(
            "SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL AND name NOT LIKE 'sqlite_%'",
          );

          for (final index in indices) {
            final createSql = index['sql'] as String?;
            if (createSql != null && createSql.isNotEmpty) {
              try {
                final encryptedIndexSql = createSql.replaceFirst(
                  RegExp(r'CREATE INDEX\s+', caseSensitive: false),
                  'CREATE INDEX IF NOT EXISTS encrypted.',
                );
                oldDb.execute(encryptedIndexSql);
              } catch (e) {
                // Index might reference a table that doesn't exist, ignore
                AppLogger.d(
                  'Could not create index (may be expected)',
                  tag: 'Database',
                  data: {'index': index['name']},
                );
              }
            }
          }

          oldDb.execute('COMMIT;');
        } catch (e) {
          oldDb.execute('ROLLBACK;');
          rethrow;
        }
      }

      // Detach encrypted database
      oldDb.execute('DETACH DATABASE encrypted;');

      AppLogger.i('Data migration completed successfully', tag: 'Database');
    } finally {
      oldDb.dispose();
    }

    // Verify the encrypted database can be opened and has data
    final verifyDb = sqlite3.open(tempNewPath);
    try {
      final pragma = encryption.getSqlCipherPragma(encryptionKey);
      verifyDb.execute(pragma);
      verifyDb.execute('PRAGMA cipher_compatibility = 4;');

      // Test query to verify encryption worked
      final result = verifyDb.select(
          'SELECT COUNT(*) as count FROM sqlite_master WHERE type="table";');
      final tableCount = result.first['count'] as int;

      if (tableCount == 0) {
        throw StateError(
            'Migration verification failed: no tables found in encrypted database');
      }

      AppLogger.d('Verification: Found tables',
          tag: 'Database', data: {'count': tableCount});

      // Verify data integrity
      final integrityResult = verifyDb.select('PRAGMA integrity_check;');
      if (integrityResult.isEmpty ||
          integrityResult.first['integrity_check'] != 'ok') {
        throw StateError(
            'Migration verification failed: integrity check failed');
      }
    } finally {
      verifyDb.dispose();
    }

    // Replace old database with encrypted one
    final oldFile = File(newDbPath);
    if (oldFile.existsSync()) {
      await oldFile.delete();
    }
    await tempNewFile.rename(newDbPath);

    // Remove lock file - migration complete
    if (lockFile.existsSync()) {
      await lockFile.delete();
    }

    AppLogger.i('Encrypted database is now active', tag: 'Database');

    // Keep backup for safety (can be deleted manually later)
    AppLogger.i('Unencrypted backup kept',
        tag: 'Database', data: {'path': oldDbPath});
    AppLogger.i(
        'You can delete the backup manually after verifying the app works correctly',
        tag: 'Database');
  } catch (e, stackTrace) {
    AppLogger.e('Error during migration',
        tag: 'Database', error: e, stackTrace: stackTrace);

    // Clean up temporary file on error
    if (tempNewFile.existsSync()) {
      await tempNewFile.delete();
    }

    // Remove lock file
    if (lockFile.existsSync()) {
      await lockFile.delete();
    }

    rethrow;
  }
}
