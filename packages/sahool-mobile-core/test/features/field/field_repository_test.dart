/// Field Repository Tests for SAHOOL Field App
/// اختبارات مستودع الحقول
///
/// Tests for FieldsRepo including:
/// - CRUD operations
/// - Offline-first behavior
/// - GeoJSON transformation
/// - Outbox queuing

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:latlong2/latlong.dart';

import 'package:sahool_mobile_core/features/field/data/repo/fields_repo.dart';
import 'package:sahool_mobile_core/features/field/data/remote/fields_api.dart';
import 'package:sahool_mobile_core/features/field/domain/entities/field.dart' as domain;
import 'package:sahool_mobile_core/core/storage/database.dart';
import 'package:sahool_mobile_core/core/sync/network_status.dart';

import 'fixtures/field_fixtures.dart';
import 'fixtures/field_mocks.dart';

void main() {
  late MockAppDatabase mockDb;
  late MockFieldsApi mockApi;
  late MockNetworkStatus mockNetworkStatus;
  late FieldsRepo repository;

  setUpAll(() {
    registerFieldMockFallbackValues();
  });

  setUp(() {
    mockDb = MockAppDatabase();
    mockApi = MockFieldsApi();
    mockNetworkStatus = MockNetworkStatus();

    repository = FieldsRepo(
      database: mockDb,
      api: mockApi,
      networkStatus: mockNetworkStatus,
    );
  });

  group('FieldsRepo Read Operations', () {
    group('getAllFields', () {
      test('should return empty list when no fields exist', () async {
        // Arrange
        when(() => mockDb.getAllFields(any())).thenAnswer((_) async => []);

        // Act
        final fields = await repository.getAllFields(FieldTestFixtures.testTenantId);

        // Assert
        expect(fields, isEmpty);
        verify(() => mockDb.getAllFields(FieldTestFixtures.testTenantId)).called(1);
      });

      test('should return list of domain fields', () async {
        // Arrange
        final dbFields = [
          createMockDbField(
            id: 'field_001',
            name: 'Field 1',
            ndviCurrent: 0.72,
          ),
          createMockDbField(
            id: 'field_002',
            name: 'Field 2',
            ndviCurrent: 0.45,
          ),
        ];
        when(() => mockDb.getAllFields(any())).thenAnswer((_) async => dbFields);

        // Act
        final fields = await repository.getAllFields(FieldTestFixtures.testTenantId);

        // Assert
        expect(fields.length, 2);
        expect(fields[0].id, 'field_001');
        expect(fields[0].name, 'Field 1');
        expect(fields[1].id, 'field_002');
        expect(fields[1].name, 'Field 2');
      });

      test('should map all field properties correctly', () async {
        // Arrange
        final boundary = FieldTestFixtures.simpleRectangleBoundary;
        final centroid = const LatLng(15.3725, 44.1925);
        final dbField = createMockDbField(
          id: 'field_001',
          remoteId: 'remote_001',
          tenantId: FieldTestFixtures.testTenantId,
          farmId: FieldTestFixtures.testFarmId,
          name: 'الحقل الشمالي',
          cropType: 'wheat',
          boundary: boundary,
          centroid: centroid,
          areaHectares: 5.5,
          status: 'active',
          ndviCurrent: 0.72,
          ndviUpdatedAt: DateTime(2024, 1, 15),
          synced: true,
          isDeleted: false,
        );
        when(() => mockDb.getAllFields(any())).thenAnswer((_) async => [dbField]);

        // Act
        final fields = await repository.getAllFields(FieldTestFixtures.testTenantId);

        // Assert
        final field = fields.first;
        expect(field.id, 'field_001');
        expect(field.remoteId, 'remote_001');
        expect(field.farmId, FieldTestFixtures.testFarmId);
        expect(field.name, 'الحقل الشمالي');
        expect(field.cropType, 'wheat');
        expect(field.boundary, boundary);
        expect(field.centroid, centroid);
        expect(field.areaHectares, 5.5);
        expect(field.status, 'active');
        expect(field.ndviCurrent, 0.72);
        expect(field.synced, true);
        expect(field.isDeleted, false);
      });
    });

    group('watchAllFields', () {
      test('should emit field updates from database stream', () async {
        // Arrange
        final dbFields = [
          createMockDbField(id: 'field_001', name: 'Field 1'),
        ];
        when(() => mockDb.watchAllFields(any())).thenAnswer(
          (_) => Stream.value(dbFields),
        );

        // Act
        final stream = repository.watchAllFields(FieldTestFixtures.testTenantId);

        // Assert
        await expectLater(
          stream,
          emits(isA<List<domain.Field>>().having(
            (l) => l.first.id,
            'first field id',
            'field_001',
          )),
        );
      });

      test('should emit empty list when database is empty', () async {
        // Arrange
        when(() => mockDb.watchAllFields(any())).thenAnswer(
          (_) => Stream.value([]),
        );

        // Act
        final stream = repository.watchAllFields(FieldTestFixtures.testTenantId);

        // Assert
        await expectLater(stream, emits(isEmpty));
      });
    });

    group('getFieldById', () {
      test('should return null when field does not exist', () async {
        // Arrange
        when(() => mockDb.getFieldById(any())).thenAnswer((_) async => null);

        // Act
        final field = await repository.getFieldById('nonexistent');

        // Assert
        expect(field, isNull);
      });

      test('should return domain field when found', () async {
        // Arrange
        final dbField = createMockDbField(
          id: 'field_001',
          name: 'Test Field',
        );
        when(() => mockDb.getFieldById(any())).thenAnswer((_) async => dbField);

        // Act
        final field = await repository.getFieldById('field_001');

        // Assert
        expect(field, isNotNull);
        expect(field!.id, 'field_001');
        expect(field.name, 'Test Field');
      });
    });

    group('getFieldsForFarm', () {
      test('should return fields for specific farm', () async {
        // Arrange
        final dbFields = [
          createMockDbField(id: 'field_001', farmId: 'farm_001'),
          createMockDbField(id: 'field_002', farmId: 'farm_001'),
        ];
        when(() => mockDb.getFieldsForFarm(any())).thenAnswer(
          (_) async => dbFields,
        );

        // Act
        final fields = await repository.getFieldsForFarm('farm_001');

        // Assert
        expect(fields.length, 2);
        verify(() => mockDb.getFieldsForFarm('farm_001')).called(1);
      });

      test('should return empty list when farm has no fields', () async {
        // Arrange
        when(() => mockDb.getFieldsForFarm(any())).thenAnswer((_) async => []);

        // Act
        final fields = await repository.getFieldsForFarm('empty_farm');

        // Assert
        expect(fields, isEmpty);
      });
    });
  });

  group('FieldsRepo Write Operations (Offline-First)', () {
    group('createField', () {
      test('should create field with calculated area and centroid', () async {
        // Arrange
        setupDatabaseFieldMocks(mockDb);
        final boundary = FieldTestFixtures.simpleRectangleBoundary;

        // Act
        final field = await repository.createField(
          tenantId: FieldTestFixtures.testTenantId,
          name: 'New Field',
          boundary: boundary,
          cropType: 'wheat',
          farmId: FieldTestFixtures.testFarmId,
        );

        // Assert
        expect(field.name, 'New Field');
        expect(field.boundary, boundary);
        expect(field.cropType, 'wheat');
        expect(field.farmId, FieldTestFixtures.testFarmId);
        expect(field.areaHectares, greaterThan(0));
        expect(field.centroid, isNotNull);
        expect(field.synced, false); // Created offline
      });

      test('should save field to local database', () async {
        // Arrange
        setupDatabaseFieldMocks(mockDb);
        final boundary = FieldTestFixtures.triangleBoundary;

        // Act
        await repository.createField(
          tenantId: FieldTestFixtures.testTenantId,
          name: 'New Field',
          boundary: boundary,
        );

        // Assert
        verify(() => mockDb.insertField(any())).called(1);
      });

      test('should add GeoJSON payload to outbox for sync', () async {
        // Arrange
        setupDatabaseFieldMocks(mockDb);
        final boundary = FieldTestFixtures.simpleRectangleBoundary;

        // Act
        await repository.createField(
          tenantId: FieldTestFixtures.testTenantId,
          name: 'New Field',
          boundary: boundary,
        );

        // Assert
        verify(() => mockDb.addToOutbox(any())).called(1);
      });

      test('should generate unique field ID', () async {
        // Arrange
        setupDatabaseFieldMocks(mockDb);
        final boundary = FieldTestFixtures.triangleBoundary;

        // Act
        final field1 = await repository.createField(
          tenantId: FieldTestFixtures.testTenantId,
          name: 'Field 1',
          boundary: boundary,
        );

        final field2 = await repository.createField(
          tenantId: FieldTestFixtures.testTenantId,
          name: 'Field 2',
          boundary: boundary,
        );

        // Assert
        expect(field1.id, isNot(equals(field2.id)));
      });
    });

    group('updateFieldBoundary', () {
      test('should update boundary in database', () async {
        // Arrange
        final originalField = createMockDbField(
          id: 'field_001',
          boundary: FieldTestFixtures.triangleBoundary,
        );
        when(() => mockDb.getFieldById(any())).thenAnswer(
          (_) async => originalField,
        );
        when(() => mockDb.updateFieldBoundary(
          fieldId: any(named: 'fieldId'),
          boundary: any(named: 'boundary'),
          centroid: any(named: 'centroid'),
          areaHectares: any(named: 'areaHectares'),
        )).thenAnswer((_) async {});
        when(() => mockDb.addToOutbox(any())).thenAnswer((_) async {});

        final newBoundary = FieldTestFixtures.largeFieldBoundary;

        // Act
        await repository.updateFieldBoundary(
          fieldId: 'field_001',
          newBoundary: newBoundary,
        );

        // Assert
        verify(() => mockDb.updateFieldBoundary(
          fieldId: 'field_001',
          boundary: newBoundary,
          centroid: any(named: 'centroid'),
          areaHectares: any(named: 'areaHectares'),
        )).called(1);
      });

      test('should add update to outbox', () async {
        // Arrange
        final originalField = createMockDbField(id: 'field_001');
        when(() => mockDb.getFieldById(any())).thenAnswer(
          (_) async => originalField,
        );
        when(() => mockDb.updateFieldBoundary(
          fieldId: any(named: 'fieldId'),
          boundary: any(named: 'boundary'),
          centroid: any(named: 'centroid'),
          areaHectares: any(named: 'areaHectares'),
        )).thenAnswer((_) async {});
        when(() => mockDb.addToOutbox(any())).thenAnswer((_) async {});

        // Act
        await repository.updateFieldBoundary(
          fieldId: 'field_001',
          newBoundary: FieldTestFixtures.simpleRectangleBoundary,
        );

        // Assert
        verify(() => mockDb.addToOutbox(any())).called(1);
      });

      test('should do nothing when field not found', () async {
        // Arrange
        when(() => mockDb.getFieldById(any())).thenAnswer((_) async => null);
        when(() => mockDb.updateFieldBoundary(
          fieldId: any(named: 'fieldId'),
          boundary: any(named: 'boundary'),
          centroid: any(named: 'centroid'),
          areaHectares: any(named: 'areaHectares'),
        )).thenAnswer((_) async {});

        // Act
        await repository.updateFieldBoundary(
          fieldId: 'nonexistent',
          newBoundary: FieldTestFixtures.triangleBoundary,
        );

        // Assert
        verifyNever(() => mockDb.addToOutbox(any()));
      });
    });

    group('updateFieldProperties', () {
      test('should update field properties in database', () async {
        // Arrange
        final existingField = createMockDbField(id: 'field_001');
        when(() => mockDb.getFieldById(any())).thenAnswer(
          (_) async => existingField,
        );
        when(() => mockDb.upsertField(any())).thenAnswer((_) async {});
        when(() => mockDb.addToOutbox(any())).thenAnswer((_) async {});

        // Act
        await repository.updateFieldProperties(
          fieldId: 'field_001',
          name: 'Updated Name',
          cropType: 'barley',
          status: 'fallow',
        );

        // Assert
        verify(() => mockDb.upsertField(any())).called(1);
        verify(() => mockDb.addToOutbox(any())).called(1);
      });

      test('should only update specified properties', () async {
        // Arrange
        final existingField = createMockDbField(id: 'field_001');
        when(() => mockDb.getFieldById(any())).thenAnswer(
          (_) async => existingField,
        );
        when(() => mockDb.upsertField(any())).thenAnswer((_) async {});
        when(() => mockDb.addToOutbox(any())).thenAnswer((_) async {});

        // Act - only update name
        await repository.updateFieldProperties(
          fieldId: 'field_001',
          name: 'New Name',
        );

        // Assert
        verify(() => mockDb.upsertField(any())).called(1);
      });

      test('should do nothing when field not found', () async {
        // Arrange
        when(() => mockDb.getFieldById(any())).thenAnswer((_) async => null);

        // Act
        await repository.updateFieldProperties(
          fieldId: 'nonexistent',
          name: 'New Name',
        );

        // Assert
        verifyNever(() => mockDb.upsertField(any()));
        verifyNever(() => mockDb.addToOutbox(any()));
      });
    });

    group('deleteField', () {
      test('should soft delete field in database', () async {
        // Arrange
        final existingField = createMockDbField(id: 'field_001');
        when(() => mockDb.getFieldById(any())).thenAnswer(
          (_) async => existingField,
        );
        when(() => mockDb.softDeleteField(any())).thenAnswer((_) async {});
        when(() => mockDb.addToOutbox(any())).thenAnswer((_) async {});

        // Act
        await repository.deleteField('field_001');

        // Assert
        verify(() => mockDb.softDeleteField('field_001')).called(1);
      });

      test('should add delete to outbox', () async {
        // Arrange
        final existingField = createMockDbField(id: 'field_001');
        when(() => mockDb.getFieldById(any())).thenAnswer(
          (_) async => existingField,
        );
        when(() => mockDb.softDeleteField(any())).thenAnswer((_) async {});
        when(() => mockDb.addToOutbox(any())).thenAnswer((_) async {});

        // Act
        await repository.deleteField('field_001');

        // Assert
        verify(() => mockDb.addToOutbox(any())).called(1);
      });

      test('should do nothing when field not found', () async {
        // Arrange
        when(() => mockDb.getFieldById(any())).thenAnswer((_) async => null);

        // Act
        await repository.deleteField('nonexistent');

        // Assert
        verifyNever(() => mockDb.softDeleteField(any()));
        verifyNever(() => mockDb.addToOutbox(any()));
      });
    });
  });

  group('FieldsRepo Sync Operations', () {
    group('refreshFromServer', () {
      test('should throw exception when offline', () async {
        // Arrange
        setupNetworkStatusMocks(mockNetworkStatus, isOnline: false);

        // Act & Assert
        expect(
          () => repository.refreshFromServer(FieldTestFixtures.testTenantId),
          throwsException,
        );
      });

      test('should fetch fields from server when online', () async {
        // Arrange
        setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
        when(() => mockApi.fetchFields(
          tenantId: any(named: 'tenantId'),
          farmId: any(named: 'farmId'),
        )).thenAnswer((_) async => [
          FieldTestFixtures.sampleGeoJsonFeature,
        ]);
        when(() => mockDb.upsertFieldsFromServer(any())).thenAnswer((_) async {});

        // Act
        final count = await repository.refreshFromServer(FieldTestFixtures.testTenantId);

        // Assert
        expect(count, 1);
        verify(() => mockApi.fetchFields(
          tenantId: FieldTestFixtures.testTenantId,
          farmId: null,
        )).called(1);
      });

      test('should upsert fields to local database', () async {
        // Arrange
        setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
        when(() => mockApi.fetchFields(
          tenantId: any(named: 'tenantId'),
          farmId: any(named: 'farmId'),
        )).thenAnswer((_) async => [
          FieldTestFixtures.sampleGeoJsonFeature,
          FieldTestFixtures.stressedFieldJson,
        ]);
        when(() => mockDb.upsertFieldsFromServer(any())).thenAnswer((_) async {});

        // Act
        await repository.refreshFromServer(FieldTestFixtures.testTenantId);

        // Assert
        verify(() => mockDb.upsertFieldsFromServer(any())).called(1);
      });

      test('should return 0 when server returns empty list', () async {
        // Arrange
        setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
        when(() => mockApi.fetchFields(
          tenantId: any(named: 'tenantId'),
          farmId: any(named: 'farmId'),
        )).thenAnswer((_) async => []);
        when(() => mockDb.upsertFieldsFromServer(any())).thenAnswer((_) async {});

        // Act
        final count = await repository.refreshFromServer(FieldTestFixtures.testTenantId);

        // Assert
        expect(count, 0);
      });

      test('should rethrow API errors', () async {
        // Arrange
        setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
        when(() => mockApi.fetchFields(
          tenantId: any(named: 'tenantId'),
          farmId: any(named: 'farmId'),
        )).thenThrow(Exception('Server error'));

        // Act & Assert
        expect(
          () => repository.refreshFromServer(FieldTestFixtures.testTenantId),
          throwsException,
        );
      });
    });

    group('getUnsyncedFields', () {
      test('should return list of unsynced fields', () async {
        // Arrange
        final unsyncedFields = [
          createMockDbField(id: 'local_001', synced: false),
          createMockDbField(id: 'local_002', synced: false),
        ];
        when(() => mockDb.getUnsyncedFields()).thenAnswer(
          (_) async => unsyncedFields,
        );

        // Act
        final fields = await repository.getUnsyncedFields();

        // Assert
        expect(fields.length, 2);
        expect(fields.every((f) => !f.synced), true);
      });

      test('should return empty list when all fields are synced', () async {
        // Arrange
        when(() => mockDb.getUnsyncedFields()).thenAnswer((_) async => []);

        // Act
        final fields = await repository.getUnsyncedFields();

        // Assert
        expect(fields, isEmpty);
      });
    });
  });

  group('FieldsRepo Error Handling', () {
    test('should handle database errors gracefully', () async {
      // Arrange
      when(() => mockDb.getAllFields(any())).thenThrow(
        Exception('Database error'),
      );

      // Act & Assert
      expect(
        () => repository.getAllFields(FieldTestFixtures.testTenantId),
        throwsException,
      );
    });

    test('should handle network timeout during refresh', () async {
      // Arrange
      setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
      when(() => mockApi.fetchFields(
        tenantId: any(named: 'tenantId'),
        farmId: any(named: 'farmId'),
      )).thenThrow(Exception('Timeout'));

      // Act & Assert
      expect(
        () => repository.refreshFromServer(FieldTestFixtures.testTenantId),
        throwsException,
      );
    });
  });

  group('FieldsRepo Data Validation', () {
    test('should handle fields with null optional values', () async {
      // Arrange
      final fieldWithNulls = createMockDbField(
        id: 'field_001',
        remoteId: null,
        farmId: null,
        cropType: null,
        centroid: null,
        ndviCurrent: null,
        ndviUpdatedAt: null,
      );
      when(() => mockDb.getAllFields(any())).thenAnswer(
        (_) async => [fieldWithNulls],
      );

      // Act
      final fields = await repository.getAllFields(FieldTestFixtures.testTenantId);

      // Assert
      final field = fields.first;
      expect(field.remoteId, isNull);
      expect(field.farmId, isNull);
      expect(field.cropType, isNull);
      expect(field.centroid, isNull);
      expect(field.ndviCurrent, isNull);
      expect(field.ndviUpdatedAt, isNull);
    });

    test('should handle fields with empty boundary', () async {
      // Arrange
      final fieldWithEmptyBoundary = createMockDbField(
        id: 'field_001',
        boundary: [],
      );
      when(() => mockDb.getAllFields(any())).thenAnswer(
        (_) async => [fieldWithEmptyBoundary],
      );

      // Act
      final fields = await repository.getAllFields(FieldTestFixtures.testTenantId);

      // Assert
      expect(fields.first.boundary, isEmpty);
      expect(fields.first.hasBoundary, false);
    });
  });
}
