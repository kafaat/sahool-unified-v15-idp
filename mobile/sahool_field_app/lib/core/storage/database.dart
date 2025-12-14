import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'package:latlong2/latlong.dart';
import 'converters/geo_converter.dart';

part 'database.g.dart';

/// Tasks Table
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

/// Outbox Table (for offline-first sync)
class Outbox extends Table {
  TextColumn get id => text()();
  TextColumn get type => text()(); // e.g., "task_complete"
  TextColumn get payloadJson => text()();
  DateTimeColumn get createdAt => dateTime()();
  IntColumn get retryCount => integer().withDefault(const Constant(0))();
  BoolColumn get completed => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

/// Fields Cache Table (GIS-enabled)
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

  @override
  Set<Column> get primaryKey => {id};
}

/// Sync Log Table
class SyncLogs extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get type => text()();
  TextColumn get status => text()(); // success, failed
  TextColumn get message => text().nullable()();
  DateTimeColumn get timestamp => dateTime()();
}

@DriftDatabase(tables: [Tasks, Outbox, Fields, SyncLogs])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 2; // v2: GIS-enabled Fields table

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
        },
      );

  // ============================================================
  // Tasks Operations
  // ============================================================

  /// Get all tasks for a field
  Future<List<Task>> getTasksForField(String fieldId) {
    return (select(tasks)
      ..where((t) => t.fieldId.equals(fieldId))
      ..orderBy([(t) => OrderingTerm.desc(t.createdAt)])
    ).get();
  }

  /// Get all tasks for tenant
  Future<List<Task>> getAllTasks(String tenantId) {
    return (select(tasks)
      ..where((t) => t.tenantId.equals(tenantId))
      ..orderBy([(t) => OrderingTerm.desc(t.createdAt)])
    ).get();
  }

  /// Get pending tasks (open or in_progress)
  Future<List<Task>> getPendingTasks(String tenantId) {
    return (select(tasks)
      ..where((t) => t.tenantId.equals(tenantId))
      ..where((t) => t.status.isIn(['open', 'in_progress']))
      ..orderBy([
        (t) => OrderingTerm.asc(t.dueDate),
        (t) => OrderingTerm.desc(t.priority),
      ])
    ).get();
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
  // Outbox Operations
  // ============================================================

  /// Add item to outbox
  Future<void> addToOutbox(OutboxCompanion item) {
    return into(outbox).insert(item);
  }

  /// Get pending outbox items
  Future<List<OutboxData>> getPendingOutbox({int limit = 50}) {
    return (select(outbox)
      ..where((o) => o.completed.equals(false))
      ..orderBy([(o) => OrderingTerm.asc(o.createdAt)])
      ..limit(limit)
    ).get();
  }

  /// Mark outbox item as done
  Future<void> markOutboxDone(String id) async {
    await (update(outbox)..where((o) => o.id.equals(id))).write(
      const OutboxCompanion(completed: Value(true)),
    );
  }

  /// Increment retry count
  Future<void> bumpOutboxRetry(String id) async {
    await customStatement(
      'UPDATE outbox SET retry_count = retry_count + 1 WHERE id = ?',
      [id],
    );
  }

  /// Delete completed outbox items
  Future<void> cleanupOutbox() async {
    await (delete(outbox)..where((o) => o.completed.equals(true))).go();
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
      ..limit(limit)
    ).get();
  }

  // ============================================================
  // Fields Operations (GIS)
  // ============================================================

  /// Get all fields for tenant (excluding soft-deleted)
  Future<List<Field>> getAllFields(String tenantId) {
    return (select(fields)
      ..where((f) => f.tenantId.equals(tenantId))
      ..where((f) => f.isDeleted.equals(false))
      ..orderBy([(f) => OrderingTerm.desc(f.updatedAt)])
    ).get();
  }

  /// Watch all fields for tenant (live stream)
  Stream<List<Field>> watchAllFields(String tenantId) {
    return (select(fields)
      ..where((f) => f.tenantId.equals(tenantId))
      ..where((f) => f.isDeleted.equals(false))
      ..orderBy([(f) => OrderingTerm.desc(f.updatedAt)])
    ).watch();
  }

  /// Get field by ID
  Future<Field?> getFieldById(String fieldId) {
    return (select(fields)..where((f) => f.id.equals(fieldId))).getSingleOrNull();
  }

  /// Get fields for a farm
  Future<List<Field>> getFieldsForFarm(String farmId) {
    return (select(fields)
      ..where((f) => f.farmId.equals(farmId))
      ..where((f) => f.isDeleted.equals(false))
    ).get();
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
    return (select(fields)
      ..where((f) => f.synced.equals(false))
    ).get();
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
            centroid = LatLng(sumLat / boundary.length, sumLng / boundary.length);
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
            areaHectares: Value((item['area_hectares'] as num?)?.toDouble() ?? 0),
            ndviCurrent: Value((item['ndvi_current'] as num?)?.toDouble()),
            updatedAt: Value(DateTime.parse(item['updated_at'])),
            synced: const Value(true),
          )),
        );
      }
    });
  }
}

/// Open database connection
LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, 'sahool_field.db'));
    return NativeDatabase.createInBackground(file);
  });
}
