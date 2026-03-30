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
import '../database/schema_version.dart';
import '../database/migration_strategy.dart';
import '../database/migrations/migration_verification.dart';

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

/// Sync Log Table
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

@DriftDatabase(tables: [Tasks, Outbox, Fields, SyncLogs, SyncEvents])
class AppDatabase extends _$AppDatabase {
  /// Callback for migration completion events
  void Function(MigrationResult)? onMigrationComplete;

  AppDatabase({this.onMigrationComplete}) : super(_openConnection());

  /// Constructor for testing with custom executor
  AppDatabase.forTesting(super.executor, {this.onMigrationComplete});

  @override
  int get schemaVersion => currentSchemaVersion; // v6: CachedUsers + CachedUserProfiles

  @override
  MigrationStrategy get migration => SahoolMigrationStrategy.create(
        database: this,
        createBackup: true,
        verifyMigrations: true,
        onMigrationComplete: onMigrationComplete,
      );

  /// Get a verifier for this database
  MigrationVerifier get verifier => MigrationVerifier(this);

  /// Run verification on this database
  Future<DatabaseVerificationReport> verifyDatabase() async {
    return verifier.runFullVerification();
  }

  /// Get database statistics
  Future<DatabaseStats> getStats() async {
    return verifier.getStats();
  }

  /// Get migration history
  Future<List<Map<String, dynamic>>> getMigrationHistory() async {
    try {
      final result = await customSelect(
        'SELECT * FROM migration_history ORDER BY id DESC',
      ).get();
      return result.map((row) => row.data).toList();
    } catch (e) {
      // Table might not exist in older versions
      return [];
    }
  }

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
    await transaction(() async {
      await batch((batch) {
        for (final item in items) {
          // Validate required fields before insert
          final id = item['id'];
          final tenantId = item['tenant_id'];
          final fieldId = item['field_id'];
          final title = item['title'];
          if (id == null || tenantId == null || fieldId == null || title == null) {
            continue; // Skip items with missing required fields
          }

          batch.insert(
            tasks,
            TasksCompanion.insert(
              id: id.toString(),
              tenantId: tenantId.toString(),
              fieldId: fieldId.toString(),
              farmId: Value(item['farm_id'] as String?),
              title: title.toString(),
              description: Value(item['description'] as String?),
              status: Value((item['status'] as String?) ?? 'open'),
              priority: Value((item['priority'] as String?) ?? 'medium'),
              dueDate: Value(item['due_date'] != null
                  ? DateTime.tryParse(item['due_date'].toString())
                  : null),
              assignedTo: Value(item['assigned_to'] as String?),
              evidenceNotes: Value(item['evidence_notes'] as String?),
              evidencePhotos: Value(item['evidence_photos'] != null
                  ? (item['evidence_photos'] is List
                      ? (item['evidence_photos'] as List).join(',')
                      : item['evidence_photos'].toString())
                  : null),
              createdAt: DateTime.tryParse(item['created_at']?.toString() ?? '') ?? DateTime.now(),
              updatedAt: DateTime.tryParse(item['updated_at']?.toString() ?? '') ?? DateTime.now(),
              synced: const Value(true),
            ),
            onConflict: DoUpdate((old) => TasksCompanion(
                  status: Value((item['status'] as String?) ?? 'open'),
                  updatedAt: Value(DateTime.tryParse(item['updated_at']?.toString() ?? '') ?? DateTime.now()),
                  synced: const Value(true),
                )),
          );
        }
      });
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
    await transaction(() async {
      await batch((batch) {
        for (final item in items) {
          // Validate required fields before insert
          final id = item['id'];
          final tenantId = item['tenant_id'];
          final name = item['name'];
          if (id == null || tenantId == null || name == null) {
            continue; // Skip items with missing required fields
          }

          // Parse GeoJSON geometry to List<LatLng>
          List<LatLng> boundary = [];
          LatLng? centroid;

          final geometry = item['geometry'] as Map<String, dynamic>?;
          if (geometry != null && geometry['type'] == 'Polygon') {
            final coordinates = geometry['coordinates'] as List?;
            if (coordinates == null || coordinates.isEmpty) continue;
            final coords = coordinates[0] as List;
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
              id: id.toString(),
              remoteId: Value(item['remote_id']?.toString() ?? id.toString()),
              tenantId: tenantId.toString(),
              farmId: Value(item['farm_id'] as String?),
              name: name.toString(),
              cropType: Value(item['crop_type'] as String?),
              boundary: boundary,
              centroid: Value(centroid),
              areaHectares: (item['area_hectares'] as num?)?.toDouble() ?? 0,
              status: Value(item['status'] as String?),
              ndviCurrent: Value((item['ndvi_current'] as num?)?.toDouble()),
              ndviUpdatedAt: Value(item['ndvi_updated_at'] != null
                  ? DateTime.tryParse(item['ndvi_updated_at'].toString())
                  : null),
              createdAt: DateTime.tryParse(item['created_at']?.toString() ?? '') ?? DateTime.now(),
              updatedAt: DateTime.tryParse(item['updated_at']?.toString() ?? '') ?? DateTime.now(),
              synced: const Value(true),
            ),
            onConflict: DoUpdate((old) => FieldsCompanion(
                  name: Value(name.toString()),
                  boundary: Value(boundary),
                  centroid: Value(centroid),
                  areaHectares:
                      Value((item['area_hectares'] as num?)?.toDouble() ?? 0),
                  ndviCurrent: Value((item['ndvi_current'] as num?)?.toDouble()),
                  updatedAt: Value(DateTime.tryParse(item['updated_at']?.toString() ?? '') ?? DateTime.now()),
                  synced: const Value(true),
                )),
          );
        }
      });
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
}

/// Open encrypted database connection with SQLCipher
///
/// Features:
/// - 256-bit AES encryption using SQLCipher
/// - Secure key storage in platform keychain/keystore
/// - Automatic migration from unencrypted to encrypted database
/// - Backward compatibility support
LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    // Ensure SQLCipher native library is loaded
    await applyWorkaroundToOpenSqlCipherOnOldAndroidVersions();

    final dbFolder = await getApplicationDocumentsDirectory();
    final dbPath = p.join(dbFolder.path, 'sahool_field.db');
    final dbFile = File(dbPath);
    final oldDbPath = p.join(dbFolder.path, 'sahool_field_unencrypted.db');
    final oldDbFile = File(oldDbPath);

    // Initialize encryption key manager
    final encryption = DatabaseEncryption();

    // Check if we need to migrate from unencrypted database
    if (!await encryption.hasKey() && dbFile.existsSync()) {
      AppLogger.i('Migrating from unencrypted to encrypted database', tag: 'Database');

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
    return NativeDatabase.createInBackground(
      dbFile,
      setup: (database) {
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
      },
    );
  });
}

/// Migrate unencrypted database to encrypted database
///
/// This function:
/// 1. Opens the old unencrypted database
/// 2. Creates a new encrypted database
/// 3. Copies all data using ATTACH DATABASE
/// 4. Verifies the migration
/// 5. Removes the old database file
Future<void> _migrateToEncryptedDatabase(
  String newDbPath,
  String oldDbPath,
  String encryptionKey,
  DatabaseEncryption encryption,
) async {
  final tempNewPath = '$newDbPath.encrypted';
  final tempNewFile = File(tempNewPath);

  // Remove temporary file if it exists
  if (tempNewFile.existsSync()) {
    await tempNewFile.delete();
  }

  try {
    // Open the old unencrypted database
    final oldDb = sqlite3.open(oldDbPath);

    try {
      // Attach new encrypted database
      // Sanitize path and key to prevent SQL injection via ATTACH DATABASE
      final sanitizedPath = tempNewPath.replaceAll("'", "''");
      final pragma = encryption.getSqlCipherPragma(encryptionKey);
      final rawKey = pragma.split('"')[1];
      // Validate key contains only expected hex/alphanumeric characters
      if (!RegExp(r'^[a-fA-F0-9x]+$').hasMatch(rawKey)) {
        throw StateError('Invalid encryption key format - potential injection');
      }
      final sanitizedKey = rawKey.replaceAll('"', '""');
      oldDb.execute("ATTACH DATABASE '$sanitizedPath' AS encrypted KEY \"$sanitizedKey\";");

      // Configure SQLCipher settings for the attached database
      oldDb.execute('PRAGMA encrypted.cipher_compatibility = 4;');
      oldDb.execute('PRAGMA encrypted.cipher_page_size = 4096;');
      oldDb.execute('PRAGMA encrypted.kdf_iter = 64000;');

      // Export all data to encrypted database
      // Use sqlcipher_export() if available, otherwise use table-by-table copy
      try {
        oldDb.execute('SELECT sqlcipher_export("encrypted");');
      } catch (e) {
        // Fallback: Copy schema and data manually
        AppLogger.i('Using manual migration (sqlcipher_export not available)', tag: 'Database');

        // Get all tables
        final tables = oldDb.select(
          "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
        );

        for (final table in tables) {
          final tableName = table['name'] as String;

          // Copy schema
          final schema = oldDb.select(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            [tableName],
          );

          if (schema.isNotEmpty) {
            final createSql = schema.first['sql'] as String;
            oldDb.execute(createSql.replaceFirst('CREATE TABLE', 'CREATE TABLE encrypted.'));
          }

          // Copy data
          oldDb.execute('INSERT INTO encrypted.$tableName SELECT * FROM main.$tableName;');
        }

        // Copy indices
        final indices = oldDb.select(
          "SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL",
        );

        for (final index in indices) {
          final createSql = index['sql'] as String;
          try {
            oldDb.execute(createSql.replaceFirst('CREATE INDEX', 'CREATE INDEX encrypted.'));
          } catch (e) {
            // Index might already exist, ignore
            AppLogger.w(
              'Could not create index',
              tag: 'Database',
              data: {'error': e.toString()},
            );}
        }
      }

      // Detach encrypted database
      oldDb.execute('DETACH DATABASE encrypted;');

      AppLogger.i('Data migration completed successfully', tag: 'Database');
    } finally {
      oldDb.dispose();
    }

    // Verify the encrypted database can be opened
    final verifyDb = sqlite3.open(tempNewPath);
    try {
      final pragma = encryption.getSqlCipherPragma(encryptionKey);
      verifyDb.execute(pragma);
      verifyDb.execute('PRAGMA cipher_compatibility = 4;');

      // Test query to verify encryption worked
      final result = verifyDb.select('SELECT COUNT(*) as count FROM sqlite_master;');
      AppLogger.d('Verification: Found schema objects', tag: 'Database', data: {'count': result.first['count']});
    } finally {
      verifyDb.dispose();
    }

    // Replace old database with encrypted one
    final oldFile = File(newDbPath);
    if (oldFile.existsSync()) {
      await oldFile.delete();
    }
    await tempNewFile.rename(newDbPath);

    AppLogger.i('Encrypted database is now active', tag: 'Database');

    // Keep backup for safety (can be deleted manually later)
    AppLogger.i('Unencrypted backup kept', tag: 'Database', data: {'path': oldDbPath});
    AppLogger.i('You can delete the backup manually after verifying the app works correctly', tag: 'Database');

  } catch (e) {
    AppLogger.e('Error during migration', tag: 'Database', error: e);

    // Clean up temporary file on error
    if (tempNewFile.existsSync()) {
      await tempNewFile.delete();
    }

    rethrow;
  }
}
