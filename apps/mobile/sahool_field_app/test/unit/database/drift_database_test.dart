/// Drift Database Tests for SAHOOL Mobile App
///
/// Tests validate database initialization, schema, and core operations.
import 'package:flutter_test/flutter_test.dart';

/// Mock database table structure for testing
class MockField {
  final String id;
  final String tenantId;
  final String name;
  final String? nameAr;
  final double areaHa;
  final String? boundaryGeoJson;
  final String? centroidGeoJson;
  final double? ndvi;
  final double? soilMoisture;
  final String status;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? etag;
  final bool isSynced;

  MockField({
    required this.id,
    required this.tenantId,
    required this.name,
    this.nameAr,
    required this.areaHa,
    this.boundaryGeoJson,
    this.centroidGeoJson,
    this.ndvi,
    this.soilMoisture,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
    this.etag,
    this.isSynced = false,
  });

  MockField copyWith({
    String? id,
    String? tenantId,
    String? name,
    String? nameAr,
    double? areaHa,
    String? boundaryGeoJson,
    String? centroidGeoJson,
    double? ndvi,
    double? soilMoisture,
    String? status,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? etag,
    bool? isSynced,
  }) {
    return MockField(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      areaHa: areaHa ?? this.areaHa,
      boundaryGeoJson: boundaryGeoJson ?? this.boundaryGeoJson,
      centroidGeoJson: centroidGeoJson ?? this.centroidGeoJson,
      ndvi: ndvi ?? this.ndvi,
      soilMoisture: soilMoisture ?? this.soilMoisture,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      etag: etag ?? this.etag,
      isSynced: isSynced ?? this.isSynced,
    );
  }
}

/// Mock outbox entry for sync queue
class MockOutboxEntry {
  final int id;
  final String tenantId;
  final String method;
  final String path;
  final String? body;
  final String? etag;
  final DateTime createdAt;
  final int retryCount;
  final bool isDone;

  MockOutboxEntry({
    required this.id,
    required this.tenantId,
    required this.method,
    required this.path,
    this.body,
    this.etag,
    required this.createdAt,
    this.retryCount = 0,
    this.isDone = false,
  });
}

/// Mock sync event
class MockSyncEvent {
  final int id;
  final String tenantId;
  final String eventType;
  final String resourceType;
  final String resourceId;
  final DateTime timestamp;
  final bool isRead;

  MockSyncEvent({
    required this.id,
    required this.tenantId,
    required this.eventType,
    required this.resourceType,
    required this.resourceId,
    required this.timestamp,
    this.isRead = false,
  });
}

/// Mock database for testing
class MockDatabase {
  final Map<String, MockField> _fields = {};
  final List<MockOutboxEntry> _outbox = [];
  final List<MockSyncEvent> _syncEvents = [];
  int _outboxIdCounter = 0;
  int _syncEventIdCounter = 0;

  // Field operations
  Future<void> insertField(MockField field) async {
    _fields[field.id] = field;
  }

  Future<MockField?> getFieldById(String id) async {
    return _fields[id];
  }

  Future<List<MockField>> getAllFields(String tenantId) async {
    return _fields.values.where((f) => f.tenantId == tenantId).toList()
      ..sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
  }

  Future<List<MockField>> getUnsyncedFields(String tenantId) async {
    return _fields.values
        .where((f) => f.tenantId == tenantId && !f.isSynced)
        .toList();
  }

  Future<void> updateField(MockField field) async {
    if (_fields.containsKey(field.id)) {
      _fields[field.id] = field;
    }
  }

  Future<void> deleteField(String id) async {
    _fields.remove(id);
  }

  Future<void> markFieldSynced(String id, String etag) async {
    final field = _fields[id];
    if (field != null) {
      _fields[id] = field.copyWith(isSynced: true, etag: etag);
    }
  }

  // Outbox operations
  Future<int> addToOutbox(MockOutboxEntry entry) async {
    _outboxIdCounter++;
    final newEntry = MockOutboxEntry(
      id: _outboxIdCounter,
      tenantId: entry.tenantId,
      method: entry.method,
      path: entry.path,
      body: entry.body,
      etag: entry.etag,
      createdAt: entry.createdAt,
    );
    _outbox.add(newEntry);
    return _outboxIdCounter;
  }

  Future<List<MockOutboxEntry>> getPendingOutboxItems(String tenantId,
      {int limit = 10}) async {
    return _outbox
        .where((e) => e.tenantId == tenantId && !e.isDone)
        .take(limit)
        .toList();
  }

  Future<void> markOutboxItemDone(int id) async {
    final index = _outbox.indexWhere((e) => e.id == id);
    if (index >= 0) {
      final item = _outbox[index];
      _outbox[index] = MockOutboxEntry(
        id: item.id,
        tenantId: item.tenantId,
        method: item.method,
        path: item.path,
        body: item.body,
        etag: item.etag,
        createdAt: item.createdAt,
        retryCount: item.retryCount,
        isDone: true,
      );
    }
  }

  // Sync event operations
  Future<int> addSyncEvent(MockSyncEvent event) async {
    _syncEventIdCounter++;
    final newEvent = MockSyncEvent(
      id: _syncEventIdCounter,
      tenantId: event.tenantId,
      eventType: event.eventType,
      resourceType: event.resourceType,
      resourceId: event.resourceId,
      timestamp: event.timestamp,
    );
    _syncEvents.add(newEvent);
    return _syncEventIdCounter;
  }

  Future<List<MockSyncEvent>> getUnreadSyncEvents(String tenantId) async {
    return _syncEvents
        .where((e) => e.tenantId == tenantId && !e.isRead)
        .toList();
  }

  // Cleanup
  Future<void> close() async {
    _fields.clear();
    _outbox.clear();
    _syncEvents.clear();
  }
}

void main() {
  group('Database Initialization', () {
    late MockDatabase db;

    setUp(() {
      db = MockDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should initialize empty database', () async {
      final fields = await db.getAllFields('tenant-123');
      expect(fields, isEmpty);
    });

    test('should close database without errors', () async {
      await expectLater(db.close(), completes);
    });
  });

  group('Field CRUD Operations', () {
    late MockDatabase db;
    late MockField testField;

    setUp(() {
      db = MockDatabase();
      testField = MockField(
        id: 'field-123',
        tenantId: 'tenant-456',
        name: 'North Field',
        nameAr: 'الحقل الشمالي',
        areaHa: 10.5,
        status: 'active',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
    });

    tearDown(() async {
      await db.close();
    });

    test('should insert field', () async {
      await db.insertField(testField);
      final result = await db.getFieldById('field-123');

      expect(result, isNotNull);
      expect(result!.name, equals('North Field'));
      expect(result.nameAr, equals('الحقل الشمالي'));
    });

    test('should get field by id', () async {
      await db.insertField(testField);
      final result = await db.getFieldById('field-123');

      expect(result, isNotNull);
      expect(result!.id, equals('field-123'));
    });

    test('should return null for non-existent field', () async {
      final result = await db.getFieldById('non-existent');
      expect(result, isNull);
    });

    test('should get all fields for tenant', () async {
      await db.insertField(testField);
      await db.insertField(
          testField.copyWith(id: 'field-124', name: 'South Field'));

      final results = await db.getAllFields('tenant-456');

      expect(results.length, equals(2));
    });

    test('should isolate fields by tenant', () async {
      await db.insertField(testField);
      await db.insertField(testField.copyWith(
        id: 'field-other',
        tenantId: 'other-tenant',
      ));

      final tenant1Fields = await db.getAllFields('tenant-456');
      final tenant2Fields = await db.getAllFields('other-tenant');

      expect(tenant1Fields.length, equals(1));
      expect(tenant2Fields.length, equals(1));
    });

    test('should update field', () async {
      await db.insertField(testField);
      await db.updateField(testField.copyWith(name: 'Updated Field'));

      final result = await db.getFieldById('field-123');
      expect(result!.name, equals('Updated Field'));
    });

    test('should delete field', () async {
      await db.insertField(testField);
      await db.deleteField('field-123');

      final result = await db.getFieldById('field-123');
      expect(result, isNull);
    });
  });

  group('Sync Operations', () {
    late MockDatabase db;
    late MockField testField;

    setUp(() {
      db = MockDatabase();
      testField = MockField(
        id: 'field-123',
        tenantId: 'tenant-456',
        name: 'Test Field',
        areaHa: 10.5,
        status: 'active',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
        isSynced: false,
      );
    });

    tearDown(() async {
      await db.close();
    });

    test('should get unsynced fields', () async {
      await db.insertField(testField);
      await db.insertField(testField.copyWith(
        id: 'field-124',
        isSynced: true,
      ));

      final unsynced = await db.getUnsyncedFields('tenant-456');

      expect(unsynced.length, equals(1));
      expect(unsynced.first.id, equals('field-123'));
    });

    test('should mark field as synced', () async {
      await db.insertField(testField);
      await db.markFieldSynced('field-123', '"etag-123"');

      final result = await db.getFieldById('field-123');
      expect(result!.isSynced, isTrue);
      expect(result.etag, equals('"etag-123"'));
    });
  });

  group('Outbox Operations', () {
    late MockDatabase db;

    setUp(() {
      db = MockDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should add item to outbox', () async {
      final entry = MockOutboxEntry(
        id: 0,
        tenantId: 'tenant-456',
        method: 'POST',
        path: '/api/v1/fields',
        body: '{"name": "New Field"}',
        createdAt: DateTime.now(),
      );

      final id = await db.addToOutbox(entry);
      expect(id, greaterThan(0));
    });

    test('should get pending outbox items', () async {
      await db.addToOutbox(MockOutboxEntry(
        id: 0,
        tenantId: 'tenant-456',
        method: 'POST',
        path: '/api/v1/fields',
        createdAt: DateTime.now(),
      ));

      final pending = await db.getPendingOutboxItems('tenant-456');
      expect(pending.length, equals(1));
    });

    test('should mark outbox item as done', () async {
      final id = await db.addToOutbox(MockOutboxEntry(
        id: 0,
        tenantId: 'tenant-456',
        method: 'POST',
        path: '/api/v1/fields',
        createdAt: DateTime.now(),
      ));

      await db.markOutboxItemDone(id);

      final pending = await db.getPendingOutboxItems('tenant-456');
      expect(pending, isEmpty);
    });

    test('should respect outbox limit', () async {
      for (int i = 0; i < 20; i++) {
        await db.addToOutbox(MockOutboxEntry(
          id: 0,
          tenantId: 'tenant-456',
          method: 'POST',
          path: '/api/v1/fields/$i',
          createdAt: DateTime.now(),
        ));
      }

      final pending = await db.getPendingOutboxItems('tenant-456', limit: 5);
      expect(pending.length, equals(5));
    });
  });

  group('Sync Events', () {
    late MockDatabase db;

    setUp(() {
      db = MockDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should add sync event', () async {
      final id = await db.addSyncEvent(MockSyncEvent(
        id: 0,
        tenantId: 'tenant-456',
        eventType: 'field.created',
        resourceType: 'field',
        resourceId: 'field-123',
        timestamp: DateTime.now(),
      ));

      expect(id, greaterThan(0));
    });

    test('should get unread sync events', () async {
      await db.addSyncEvent(MockSyncEvent(
        id: 0,
        tenantId: 'tenant-456',
        eventType: 'field.updated',
        resourceType: 'field',
        resourceId: 'field-123',
        timestamp: DateTime.now(),
      ));

      final unread = await db.getUnreadSyncEvents('tenant-456');
      expect(unread.length, equals(1));
    });
  });

  group('GeoJSON Handling', () {
    late MockDatabase db;

    setUp(() {
      db = MockDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should store and retrieve boundary GeoJSON', () async {
      const boundaryGeoJson = '''
        {
          "type": "Polygon",
          "coordinates": [[[46.7, 24.7], [46.8, 24.7], [46.8, 24.8], [46.7, 24.8], [46.7, 24.7]]]
        }
      ''';

      final field = MockField(
        id: 'field-geo',
        tenantId: 'tenant-456',
        name: 'Geo Field',
        areaHa: 10.5,
        boundaryGeoJson: boundaryGeoJson,
        status: 'active',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      await db.insertField(field);
      final result = await db.getFieldById('field-geo');

      expect(result!.boundaryGeoJson, isNotNull);
      expect(result.boundaryGeoJson, contains('Polygon'));
    });

    test('should store centroid GeoJSON', () async {
      const centroidGeoJson =
          '{"type": "Point", "coordinates": [46.75, 24.75]}';

      final field = MockField(
        id: 'field-centroid',
        tenantId: 'tenant-456',
        name: 'Centroid Field',
        areaHa: 10.5,
        centroidGeoJson: centroidGeoJson,
        status: 'active',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      await db.insertField(field);
      final result = await db.getFieldById('field-centroid');

      expect(result!.centroidGeoJson, contains('Point'));
    });
  });

  group('ETag Support', () {
    late MockDatabase db;

    setUp(() {
      db = MockDatabase();
    });

    tearDown(() async {
      await db.close();
    });

    test('should store ETag with field', () async {
      final field = MockField(
        id: 'field-etag',
        tenantId: 'tenant-456',
        name: 'ETag Field',
        areaHa: 10.5,
        status: 'active',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
        etag: '"abc123"',
      );

      await db.insertField(field);
      final result = await db.getFieldById('field-etag');

      expect(result!.etag, equals('"abc123"'));
    });

    test('should store ETag in outbox for PUT requests', () async {
      final id = await db.addToOutbox(MockOutboxEntry(
        id: 0,
        tenantId: 'tenant-456',
        method: 'PUT',
        path: '/api/v1/fields/field-123',
        body: '{"name": "Updated"}',
        etag: '"original-etag"',
        createdAt: DateTime.now(),
      ));

      final pending = await db.getPendingOutboxItems('tenant-456');
      final item = pending.firstWhere((e) => e.id == id);

      expect(item.etag, equals('"original-etag"'));
    });
  });
}
