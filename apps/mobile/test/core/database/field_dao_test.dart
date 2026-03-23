/// Field DAO Tests - CRUD Operations for Fields Table
/// اختبارات عمليات الحقول - الانشاء والقراءة والتحديث والحذف
///
/// Tests for:
/// - Field insert, update, delete operations
/// - GIS boundary and centroid handling
/// - NDVI data management
/// - Sync status tracking
/// - Tenant isolation
/// - Complex queries
library;
import 'dart:convert';

import 'package:drift/drift.dart' hide isNull, isNotNull;
import 'package:drift/native.dart';
import 'package:flutter_test/flutter_test.dart';

part 'field_dao_test.g.dart';

/// GeoPolygon Converter for testing - matches production implementation
class GeoPolygonConverter extends TypeConverter<List<Map<String, double>>, String> {
  const GeoPolygonConverter();

  @override
  List<Map<String, double>> fromSql(String fromDb) {
    if (fromDb.isEmpty) return [];
    try {
      final jsonList = jsonDecode(fromDb) as List<dynamic>;
      return jsonList.map((point) {
        if (point is List && point.length >= 2) {
          return {
            'lng': (point[0] as num).toDouble(),
            'lat': (point[1] as num).toDouble(),
          };
        }
        return {'lat': 0.0, 'lng': 0.0};
      }).toList();
    } catch (e) {
      return [];
    }
  }

  @override
  String toSql(List<Map<String, double>> value) {
    if (value.isEmpty) return '[]';
    final jsonList = value.map((p) => [p['lng'], p['lat']]).toList();
    return jsonEncode(jsonList);
  }
}

/// GeoPoint Converter for testing
class GeoPointConverter extends TypeConverter<Map<String, double>?, String?> {
  const GeoPointConverter();

  @override
  Map<String, double>? fromSql(String? fromDb) {
    if (fromDb == null || fromDb.isEmpty) return null;
    try {
      final point = jsonDecode(fromDb) as List<dynamic>;
      if (point.length >= 2) {
        return {
          'lng': (point[0] as num).toDouble(),
          'lat': (point[1] as num).toDouble(),
        };
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  @override
  String? toSql(Map<String, double>? value) {
    if (value == null) return null;
    return jsonEncode([value['lng'], value['lat']]);
  }
}

/// Fields Table for DAO testing
@TableIndex(name: 'dao_fields_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'dao_fields_farm_idx', columns: {#farmId})
@TableIndex(name: 'dao_fields_synced_idx', columns: {#synced})
@TableIndex(name: 'dao_fields_deleted_idx', columns: {#isDeleted})
@TableIndex(name: 'dao_fields_tenant_deleted_idx', columns: {#tenantId, #isDeleted})
@TableIndex(name: 'dao_fields_updated_idx', columns: {#updatedAt})
@TableIndex(name: 'dao_fields_remote_idx', columns: {#remoteId})
class DaoFields extends Table {
  TextColumn get id => text()();
  TextColumn get remoteId => text().nullable()();
  TextColumn get tenantId => text()();
  TextColumn get farmId => text().nullable()();
  TextColumn get name => text().withLength(min: 1, max: 100)();
  TextColumn get nameAr => text().nullable()();
  TextColumn get cropType => text().nullable()();
  TextColumn get boundary => text().map(const GeoPolygonConverter())();
  TextColumn get centroid => text().map(const GeoPointConverter()).nullable()();
  RealColumn get areaHectares => real()();
  TextColumn get status => text().nullable()();
  RealColumn get ndviCurrent => real().nullable()();
  DateTimeColumn get ndviUpdatedAt => dateTime().nullable()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  BoolColumn get isDeleted => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()();
  TextColumn get etag => text().nullable()();
  DateTimeColumn get serverUpdatedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

/// Test Database for Field DAO
@DriftDatabase(tables: [DaoFields])
class FieldDaoTestDatabase extends _$FieldDaoTestDatabase {
  FieldDaoTestDatabase() : super(NativeDatabase.memory());

  @override
  int get schemaVersion => 1;

  // ============================================================
  // Field DAO Operations - mirrors production AppDatabase
  // ============================================================

  /// Get all fields for tenant (excluding soft-deleted)
  Future<List<DaoField>> getAllFields(String tenantId) {
    return (select(daoFields)
          ..where((f) => f.tenantId.equals(tenantId))
          ..where((f) => f.isDeleted.equals(false))
          ..orderBy([(f) => OrderingTerm.desc(f.updatedAt)]))
        .get();
  }

  /// Watch all fields for tenant (live stream)
  Stream<List<DaoField>> watchAllFields(String tenantId) {
    return (select(daoFields)
          ..where((f) => f.tenantId.equals(tenantId))
          ..where((f) => f.isDeleted.equals(false))
          ..orderBy([(f) => OrderingTerm.desc(f.updatedAt)]))
        .watch();
  }

  /// Get field by ID
  Future<DaoField?> getFieldById(String fieldId) {
    return (select(daoFields)..where((f) => f.id.equals(fieldId)))
        .getSingleOrNull();
  }

  /// Get fields for a farm
  Future<List<DaoField>> getFieldsForFarm(String farmId) {
    return (select(daoFields)
          ..where((f) => f.farmId.equals(farmId))
          ..where((f) => f.isDeleted.equals(false)))
        .get();
  }

  /// Insert or update field
  Future<void> upsertField(DaoFieldsCompanion field) {
    return into(daoFields).insertOnConflictUpdate(field);
  }

  /// Insert new field
  Future<void> insertField(DaoFieldsCompanion field) {
    return into(daoFields).insert(field);
  }

  /// Update field boundary (GIS)
  Future<void> updateFieldBoundary({
    required String fieldId,
    required List<Map<String, double>> boundary,
    required Map<String, double>? centroid,
    required double areaHectares,
  }) async {
    await (update(daoFields)..where((f) => f.id.equals(fieldId))).write(
      DaoFieldsCompanion(
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
    await (update(daoFields)..where((f) => f.id.equals(fieldId))).write(
      DaoFieldsCompanion(
        ndviCurrent: Value(ndviScore),
        ndviUpdatedAt: Value(DateTime.now()),
        updatedAt: Value(DateTime.now()),
      ),
    );
  }

  /// Soft delete field
  Future<void> softDeleteField(String fieldId) async {
    await (update(daoFields)..where((f) => f.id.equals(fieldId))).write(
      DaoFieldsCompanion(
        isDeleted: const Value(true),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ),
    );
  }

  /// Hard delete field (permanent)
  Future<void> hardDeleteField(String fieldId) async {
    await (delete(daoFields)..where((f) => f.id.equals(fieldId))).go();
  }

  /// Mark field as synced
  Future<void> markFieldSynced(String fieldId, String? remoteId) async {
    await (update(daoFields)..where((f) => f.id.equals(fieldId))).write(
      DaoFieldsCompanion(
        remoteId: Value(remoteId),
        synced: const Value(true),
      ),
    );
  }

  /// Get unsynced fields
  Future<List<DaoField>> getUnsyncedFields() {
    return (select(daoFields)..where((f) => f.synced.equals(false))).get();
  }

  /// Update field with ETag from server
  Future<void> updateFieldWithEtag({
    required String fieldId,
    required String etag,
    DateTime? serverUpdatedAt,
  }) async {
    await (update(daoFields)..where((f) => f.id.equals(fieldId))).write(
      DaoFieldsCompanion(
        etag: Value(etag),
        serverUpdatedAt: Value(serverUpdatedAt ?? DateTime.now()),
        synced: const Value(true),
      ),
    );
  }

  /// Get fields by crop type
  Future<List<DaoField>> getFieldsByCropType(String tenantId, String cropType) {
    return (select(daoFields)
          ..where((f) => f.tenantId.equals(tenantId))
          ..where((f) => f.cropType.equals(cropType))
          ..where((f) => f.isDeleted.equals(false)))
        .get();
  }

  /// Get fields with NDVI below threshold
  Future<List<DaoField>> getFieldsWithLowNdvi(String tenantId, double threshold) {
    return (select(daoFields)
          ..where((f) => f.tenantId.equals(tenantId))
          ..where((f) => f.ndviCurrent.isSmallerThanValue(threshold))
          ..where((f) => f.isDeleted.equals(false)))
        .get();
  }

  /// Get total area for tenant
  Future<double> getTotalArea(String tenantId) async {
    final result = await customSelect(
      'SELECT SUM(area_hectares) as total FROM dao_fields WHERE tenant_id = ? AND is_deleted = 0',
      variables: [Variable.withString(tenantId)],
    ).getSingle();
    return (result.read<double?>('total') ?? 0.0);
  }

  /// Search fields by name
  Future<List<DaoField>> searchFieldsByName(String tenantId, String query) {
    return (select(daoFields)
          ..where((f) => f.tenantId.equals(tenantId))
          ..where((f) => f.name.like('%$query%') | f.nameAr.like('%$query%'))
          ..where((f) => f.isDeleted.equals(false)))
        .get();
  }
}

/// Test fixtures for Field DAO
class FieldDaoFixtures {
  static List<Map<String, double>> createBoundary() {
    return [
      {'lat': 15.370, 'lng': 44.190},
      {'lat': 15.371, 'lng': 44.191},
      {'lat': 15.369, 'lng': 44.192},
      {'lat': 15.368, 'lng': 44.191},
      {'lat': 15.370, 'lng': 44.190}, // Close polygon
    ];
  }

  static Map<String, double> createCentroid() {
    return {'lat': 15.3695, 'lng': 44.191};
  }

  static DaoFieldsCompanion createField({
    String? id,
    String tenantId = 'tenant-1',
    String? farmId,
    String name = 'Test Field',
    String? nameAr,
    String? cropType,
    double areaHectares = 10.0,
    String? status,
    double? ndviCurrent,
    bool synced = false,
    bool isDeleted = false,
  }) {
    return DaoFieldsCompanion.insert(
      id: id ?? 'field-${DateTime.now().millisecondsSinceEpoch}',
      tenantId: tenantId,
      farmId: Value(farmId),
      name: name,
      nameAr: Value(nameAr),
      cropType: Value(cropType),
      boundary: createBoundary(),
      centroid: Value(createCentroid()),
      areaHectares: areaHectares,
      status: Value(status ?? 'active'),
      ndviCurrent: Value(ndviCurrent),
      synced: Value(synced),
      isDeleted: Value(isDeleted),
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }
}

void main() {
  group('Field DAO - Insert Operations', () {
    late FieldDaoTestDatabase db;

    setUp(() {
      db = FieldDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should insert a new field', () async {
      final field = FieldDaoFixtures.createField(
        id: 'field-001',
        name: 'North Field',
        nameAr: 'الحقل الشمالي',
      );

      await db.insertField(field);

      final result = await db.getFieldById('field-001');
      expect(result, isNotNull);
      expect(result!.name, equals('North Field'));
      expect(result.nameAr, equals('الحقل الشمالي'));
    });

    test('should insert field with all GIS data', () async {
      final boundary = FieldDaoFixtures.createBoundary();
      final centroid = FieldDaoFixtures.createCentroid();

      final field = FieldDaoFixtures.createField(
        id: 'field-gis',
        areaHectares: 25.5,
      );

      await db.insertField(field);

      final result = await db.getFieldById('field-gis');
      expect(result, isNotNull);
      expect(result!.boundary, hasLength(5));
      expect(result.centroid, isNotNull);
      expect(result.areaHectares, equals(25.5));
    });

    test('should insert field with NDVI data', () async {
      final field = FieldDaoFixtures.createField(
        id: 'field-ndvi',
        ndviCurrent: 0.72,
      );

      await db.insertField(field);

      final result = await db.getFieldById('field-ndvi');
      expect(result, isNotNull);
      expect(result!.ndviCurrent, equals(0.72));
    });

    test('should upsert field (insert or update)', () async {
      final field1 = FieldDaoFixtures.createField(
        id: 'field-upsert',
        name: 'Original Name',
      );

      await db.upsertField(field1);

      var result = await db.getFieldById('field-upsert');
      expect(result!.name, equals('Original Name'));

      // Upsert with updated name
      final field2 = DaoFieldsCompanion(
        id: const Value('field-upsert'),
        tenantId: const Value('tenant-1'),
        name: const Value('Updated Name'),
        boundary: Value(FieldDaoFixtures.createBoundary()),
        areaHectares: const Value(10.0),
        createdAt: Value(DateTime.now()),
        updatedAt: Value(DateTime.now()),
      );

      await db.upsertField(field2);

      result = await db.getFieldById('field-upsert');
      expect(result!.name, equals('Updated Name'));
    });

    test('should fail on duplicate primary key insert', () async {
      final field = FieldDaoFixtures.createField(id: 'field-dup');

      await db.insertField(field);

      expect(
        () async => db.insertField(field),
        throwsA(isA<SqliteException>()),
      );
    });
  });

  group('Field DAO - Read Operations', () {
    late FieldDaoTestDatabase db;

    setUp(() async {
      db = FieldDaoTestDatabase();

      // Insert test data
      await db.insertField(FieldDaoFixtures.createField(
        id: 'field-1',
        tenantId: 'tenant-1',
        farmId: 'farm-1',
        name: 'North Field',
        nameAr: 'الحقل الشمالي',
        cropType: 'wheat',
        areaHectares: 10.0,
        ndviCurrent: 0.75,
      ));

      await db.insertField(FieldDaoFixtures.createField(
        id: 'field-2',
        tenantId: 'tenant-1',
        farmId: 'farm-1',
        name: 'South Field',
        nameAr: 'الحقل الجنوبي',
        cropType: 'barley',
        areaHectares: 15.0,
        ndviCurrent: 0.65,
      ));

      await db.insertField(FieldDaoFixtures.createField(
        id: 'field-3',
        tenantId: 'tenant-1',
        farmId: 'farm-2',
        name: 'East Field',
        cropType: 'wheat',
        areaHectares: 20.0,
        ndviCurrent: 0.45,
      ));

      await db.insertField(FieldDaoFixtures.createField(
        id: 'field-4',
        tenantId: 'tenant-2',
        name: 'Other Tenant Field',
        areaHectares: 30.0,
      ));

      await db.insertField(FieldDaoFixtures.createField(
        id: 'field-deleted',
        tenantId: 'tenant-1',
        name: 'Deleted Field',
        isDeleted: true,
      ));
    });

    tearDown(() async {
      await db.close();
    });

    test('should get field by ID', () async {
      final result = await db.getFieldById('field-1');

      expect(result, isNotNull);
      expect(result!.id, equals('field-1'));
      expect(result.name, equals('North Field'));
    });

    test('should return null for non-existent field', () async {
      final result = await db.getFieldById('non-existent');
      expect(result, isNull);
    });

    test('should get all fields for tenant', () async {
      final fields = await db.getAllFields('tenant-1');

      // Should exclude deleted fields
      expect(fields.length, equals(3));
      expect(fields.every((f) => f.tenantId == 'tenant-1'), isTrue);
      expect(fields.every((f) => !f.isDeleted), isTrue);
    });

    test('should isolate fields by tenant', () async {
      final tenant1Fields = await db.getAllFields('tenant-1');
      final tenant2Fields = await db.getAllFields('tenant-2');

      expect(tenant1Fields.length, equals(3));
      expect(tenant2Fields.length, equals(1));
      expect(tenant2Fields.first.name, equals('Other Tenant Field'));
    });

    test('should get fields for a farm', () async {
      final farm1Fields = await db.getFieldsForFarm('farm-1');
      final farm2Fields = await db.getFieldsForFarm('farm-2');

      expect(farm1Fields.length, equals(2));
      expect(farm2Fields.length, equals(1));
    });

    test('should get fields by crop type', () async {
      final wheatFields = await db.getFieldsByCropType('tenant-1', 'wheat');

      expect(wheatFields.length, equals(2));
      expect(wheatFields.every((f) => f.cropType == 'wheat'), isTrue);
    });

    test('should get fields with low NDVI', () async {
      final lowNdviFields = await db.getFieldsWithLowNdvi('tenant-1', 0.5);

      expect(lowNdviFields.length, equals(1));
      expect(lowNdviFields.first.id, equals('field-3'));
      expect(lowNdviFields.first.ndviCurrent, lessThan(0.5));
    });

    test('should calculate total area for tenant', () async {
      final totalArea = await db.getTotalArea('tenant-1');

      expect(totalArea, equals(45.0)); // 10 + 15 + 20
    });

    test('should search fields by name', () async {
      final results = await db.searchFieldsByName('tenant-1', 'North');

      expect(results.length, equals(1));
      expect(results.first.name, equals('North Field'));
    });

    test('should search fields by Arabic name', () async {
      final results = await db.searchFieldsByName('tenant-1', 'الشمالي');

      expect(results.length, equals(1));
      expect(results.first.nameAr, equals('الحقل الشمالي'));
    });

    test('should return fields ordered by updated date', () async {
      final fields = await db.getAllFields('tenant-1');

      for (int i = 0; i < fields.length - 1; i++) {
        expect(
          fields[i].updatedAt.isAfter(fields[i + 1].updatedAt) ||
              fields[i].updatedAt.isAtSameMomentAs(fields[i + 1].updatedAt),
          isTrue,
        );
      }
    });
  });

  group('Field DAO - Update Operations', () {
    late FieldDaoTestDatabase db;

    setUp(() async {
      db = FieldDaoTestDatabase();

      await db.insertField(FieldDaoFixtures.createField(
        id: 'update-field',
        name: 'Original Name',
        areaHectares: 10.0,
        ndviCurrent: 0.6,
        synced: true,
      ));
    });

    tearDown(() async {
      await db.close();
    });

    test('should update field boundary', () async {
      final newBoundary = [
        {'lat': 15.380, 'lng': 44.200},
        {'lat': 15.381, 'lng': 44.201},
        {'lat': 15.379, 'lng': 44.202},
        {'lat': 15.380, 'lng': 44.200},
      ];

      final newCentroid = {'lat': 15.380, 'lng': 44.201};

      await db.updateFieldBoundary(
        fieldId: 'update-field',
        boundary: newBoundary,
        centroid: newCentroid,
        areaHectares: 15.0,
      );

      final result = await db.getFieldById('update-field');
      expect(result!.areaHectares, equals(15.0));
      expect(result.boundary.length, equals(4));
      expect(result.synced, isFalse); // Should be marked as unsynced
    });

    test('should update field NDVI', () async {
      await db.updateFieldNdvi(
        fieldId: 'update-field',
        ndviScore: 0.82,
      );

      final result = await db.getFieldById('update-field');
      expect(result!.ndviCurrent, equals(0.82));
      expect(result.ndviUpdatedAt, isNotNull);
    });

    test('should mark field as synced', () async {
      // First make it unsynced
      await db.updateFieldBoundary(
        fieldId: 'update-field',
        boundary: FieldDaoFixtures.createBoundary(),
        centroid: FieldDaoFixtures.createCentroid(),
        areaHectares: 10.0,
      );

      var result = await db.getFieldById('update-field');
      expect(result!.synced, isFalse);

      // Now sync it
      await db.markFieldSynced('update-field', 'remote-id-123');

      result = await db.getFieldById('update-field');
      expect(result!.synced, isTrue);
      expect(result.remoteId, equals('remote-id-123'));
    });

    test('should update field with ETag', () async {
      final serverTime = DateTime.now();

      await db.updateFieldWithEtag(
        fieldId: 'update-field',
        etag: '"abc123xyz"',
        serverUpdatedAt: serverTime,
      );

      final result = await db.getFieldById('update-field');
      expect(result!.etag, equals('"abc123xyz"'));
      expect(result.serverUpdatedAt, isNotNull);
      expect(result.synced, isTrue);
    });
  });

  group('Field DAO - Delete Operations', () {
    late FieldDaoTestDatabase db;

    setUp(() async {
      db = FieldDaoTestDatabase();

      await db.insertField(FieldDaoFixtures.createField(
        id: 'delete-field-1',
        tenantId: 'tenant-1',
        name: 'Field to Soft Delete',
      ));

      await db.insertField(FieldDaoFixtures.createField(
        id: 'delete-field-2',
        tenantId: 'tenant-1',
        name: 'Field to Hard Delete',
      ));
    });

    tearDown(() async {
      await db.close();
    });

    test('should soft delete field', () async {
      await db.softDeleteField('delete-field-1');

      // Field should still exist in database
      final result = await db.getFieldById('delete-field-1');
      expect(result, isNotNull);
      expect(result!.isDeleted, isTrue);
      expect(result.synced, isFalse);

      // But not in getAllFields
      final fields = await db.getAllFields('tenant-1');
      expect(fields.where((f) => f.id == 'delete-field-1'), isEmpty);
    });

    test('should hard delete field', () async {
      await db.hardDeleteField('delete-field-2');

      final result = await db.getFieldById('delete-field-2');
      expect(result, isNull);
    });

    test('should not include soft-deleted in farm queries', () async {
      await db.softDeleteField('delete-field-1');

      final fields = await db.getAllFields('tenant-1');
      expect(fields.any((f) => f.id == 'delete-field-1'), isFalse);
    });
  });

  group('Field DAO - Sync Operations', () {
    late FieldDaoTestDatabase db;

    setUp(() async {
      db = FieldDaoTestDatabase();

      // Insert mix of synced and unsynced fields
      await db.insertField(FieldDaoFixtures.createField(
        id: 'synced-field',
        name: 'Synced Field',
        synced: true,
      ));

      await db.insertField(FieldDaoFixtures.createField(
        id: 'unsynced-field-1',
        name: 'Unsynced Field 1',
        synced: false,
      ));

      await db.insertField(FieldDaoFixtures.createField(
        id: 'unsynced-field-2',
        name: 'Unsynced Field 2',
        synced: false,
      ));
    });

    tearDown(() async {
      await db.close();
    });

    test('should get unsynced fields', () async {
      final unsyncedFields = await db.getUnsyncedFields();

      expect(unsyncedFields.length, equals(2));
      expect(unsyncedFields.every((f) => !f.synced), isTrue);
    });

    test('should mark field as synced', () async {
      await db.markFieldSynced('unsynced-field-1', 'remote-123');

      final unsyncedFields = await db.getUnsyncedFields();
      expect(unsyncedFields.length, equals(1));
      expect(unsyncedFields.first.id, equals('unsynced-field-2'));

      final syncedField = await db.getFieldById('unsynced-field-1');
      expect(syncedField!.synced, isTrue);
      expect(syncedField.remoteId, equals('remote-123'));
    });
  });

  group('Field DAO - GeoJSON Handling', () {
    late FieldDaoTestDatabase db;

    setUp(() {
      db = FieldDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should store and retrieve polygon boundary', () async {
      final boundary = [
        {'lat': 15.370, 'lng': 44.190},
        {'lat': 15.375, 'lng': 44.195},
        {'lat': 15.380, 'lng': 44.190},
        {'lat': 15.375, 'lng': 44.185},
        {'lat': 15.370, 'lng': 44.190},
      ];

      await db.insertField(DaoFieldsCompanion.insert(
        id: 'geo-field',
        tenantId: 'tenant-1',
        name: 'Geo Field',
        boundary: boundary,
        areaHectares: 50.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      ));

      final result = await db.getFieldById('geo-field');
      expect(result, isNotNull);
      expect(result!.boundary.length, equals(5));
      expect(result.boundary.first['lat'], closeTo(15.370, 0.001));
      expect(result.boundary.first['lng'], closeTo(44.190, 0.001));
    });

    test('should store and retrieve centroid', () async {
      final centroid = {'lat': 15.375, 'lng': 44.190};

      await db.insertField(DaoFieldsCompanion.insert(
        id: 'centroid-field',
        tenantId: 'tenant-1',
        name: 'Centroid Field',
        boundary: FieldDaoFixtures.createBoundary(),
        centroid: Value(centroid),
        areaHectares: 50.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      ));

      final result = await db.getFieldById('centroid-field');
      expect(result!.centroid, isNotNull);
      expect(result.centroid!['lat'], closeTo(15.375, 0.001));
      expect(result.centroid!['lng'], closeTo(44.190, 0.001));
    });

    test('should handle empty boundary', () async {
      await db.insertField(DaoFieldsCompanion.insert(
        id: 'empty-boundary',
        tenantId: 'tenant-1',
        name: 'Empty Boundary Field',
        boundary: <Map<String, double>>[],
        areaHectares: 0.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      ));

      final result = await db.getFieldById('empty-boundary');
      expect(result!.boundary, isEmpty);
    });

    test('should handle null centroid', () async {
      await db.insertField(DaoFieldsCompanion.insert(
        id: 'null-centroid',
        tenantId: 'tenant-1',
        name: 'No Centroid Field',
        boundary: FieldDaoFixtures.createBoundary(),
        centroid: const Value(null),
        areaHectares: 10.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      ));

      final result = await db.getFieldById('null-centroid');
      expect(result!.centroid, isNull);
    });
  });

  group('Field DAO - Watch Streams', () {
    late FieldDaoTestDatabase db;

    setUp(() async {
      db = FieldDaoTestDatabase();

      await db.insertField(FieldDaoFixtures.createField(
        id: 'watch-field-1',
        tenantId: 'tenant-1',
        name: 'Initial Field',
      ));
    });

    tearDown(() async {
      await db.close();
    });

    test('should emit initial value on watch', () async {
      final stream = db.watchAllFields('tenant-1');
      final result = await stream.first;

      expect(result.length, equals(1));
      expect(result.first.name, equals('Initial Field'));
    });

    test('should emit on insert', () async {
      final stream = db.watchAllFields('tenant-1');
      final results = <List<DaoField>>[];

      final subscription = stream.listen((data) {
        results.add(data);
      });

      await Future<void>.delayed(const Duration(milliseconds: 50));

      await db.insertField(FieldDaoFixtures.createField(
        id: 'watch-field-2',
        tenantId: 'tenant-1',
        name: 'New Field',
      ));

      await Future<void>.delayed(const Duration(milliseconds: 50));

      await subscription.cancel();

      expect(results.length, greaterThanOrEqualTo(2));
      expect(results.last.length, equals(2));
    });

    test('should not emit for other tenants', () async {
      final stream = db.watchAllFields('tenant-1');
      final results = <List<DaoField>>[];

      final subscription = stream.listen((data) {
        results.add(data);
      });

      await Future<void>.delayed(const Duration(milliseconds: 50));

      // Insert field for different tenant
      await db.insertField(FieldDaoFixtures.createField(
        id: 'other-tenant-field',
        tenantId: 'tenant-2',
        name: 'Other Tenant Field',
      ));

      await Future<void>.delayed(const Duration(milliseconds: 50));

      await subscription.cancel();

      // Should still have only 1 field for tenant-1
      expect(results.last.length, equals(1));
    });
  });

  group('Field DAO - Validation', () {
    late FieldDaoTestDatabase db;

    setUp(() {
      db = FieldDaoTestDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should enforce name length constraint', () async {
      // Name must be 1-100 characters
      final validField = FieldDaoFixtures.createField(
        id: 'valid-name',
        name: 'Valid Name',
      );

      await db.insertField(validField);
      final result = await db.getFieldById('valid-name');
      expect(result, isNotNull);
    });

    test('should handle special characters in name', () async {
      await db.insertField(FieldDaoFixtures.createField(
        id: 'special-chars',
        name: "Field with 'quotes' and \"double quotes\"",
        nameAr: 'حقل مع علامات خاصة: () [] {}',
      ));

      final result = await db.getFieldById('special-chars');
      expect(result!.name, contains("'quotes'"));
      expect(result.nameAr, contains('علامات خاصة'));
    });

    test('should handle Unicode characters', () async {
      await db.insertField(FieldDaoFixtures.createField(
        id: 'unicode-field',
        name: 'Field with emojis: -', // Just descriptive, no actual emojis
        nameAr: 'حقل القمح - محافظة صنعاء',
      ));

      final result = await db.getFieldById('unicode-field');
      expect(result, isNotNull);
      expect(result!.nameAr, contains('صنعاء'));
    });
  });
}
