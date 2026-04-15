import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/error_handling/app_exceptions.dart';
import 'package:sahool_field_app/features/field/data/repo/fields_repo.dart';
import 'package:sahool_field_app/features/field/data/remote/fields_api.dart';
import 'package:sahool_field_app/features/field/domain/entities/field.dart'
    as domain;
import '../../../mocks/mock_app_database.dart';
import '../../../mocks/mock_network_status.dart';
import '../../../fixtures/sample_fields.dart';

/// Mock FieldsApi for testing
class MockFieldsApi extends Mock implements FieldsApi {}

void main() {
  group('FieldsRepo', () {
    late FieldsRepo fieldsRepo;
    late MockAppDatabase mockDatabase;
    late MockFieldsApi mockApi;
    late MockNetworkStatus mockNetworkStatus;

    setUp(() {
      mockDatabase = MockAppDatabase();
      mockApi = MockFieldsApi();
      mockNetworkStatus = MockNetworkStatus(isOnline: true);

      fieldsRepo = FieldsRepo(
        database: mockDatabase,
        api: mockApi,
        networkStatus: mockNetworkStatus,
      );

      // Clear database before each test
      mockDatabase.clearAll();
    });

    group('getAllFields', () {
      test('should return fields from local database', () async {
        // Arrange
        const tenantId = 'tenant_test';
        final field1 = SampleFields.createWheatField(tenantId: tenantId);
        final field2 = SampleFields.createDatePalmField(tenantId: tenantId);

        mockDatabase.seedField(field1);
        mockDatabase.seedField(field2);

        // Act
        final fields = await fieldsRepo.getAllFields(tenantId);

        // Assert
        expect(fields.length, 2);
        expect(fields.any((f) => f.id == field1.id), isTrue);
        expect(fields.any((f) => f.id == field2.id), isTrue);
      });

      test('should return empty list when no fields', () async {
        // Act
        final fields = await fieldsRepo.getAllFields('tenant_test');

        // Assert
        expect(fields, isEmpty);
      });

      test('should only return fields for specified tenant', () async {
        // Arrange
        final field1 =
            SampleFields.createWheatField(id: 'field_t1', tenantId: 'tenant_1');
        final field2 =
            SampleFields.createWheatField(id: 'field_t2', tenantId: 'tenant_2');

        mockDatabase.seedField(field1);
        mockDatabase.seedField(field2);

        // Act
        final fields = await fieldsRepo.getAllFields('tenant_1');

        // Assert
        expect(fields.length, 1);
        expect(fields.first.tenantId, 'tenant_1');
      });
    });

    group('getFieldById', () {
      test('should return field when found', () async {
        // Arrange
        const fieldId = 'field_001';
        final field = SampleFields.createWheatField(id: fieldId);
        mockDatabase.seedField(field);

        // Act
        final result = await fieldsRepo.getFieldById(fieldId);

        // Assert
        expect(result, isNotNull);
        expect(result!.id, fieldId);
      });

      test('should return null when not found', () async {
        // Act
        final result = await fieldsRepo.getFieldById('nonexistent');

        // Assert
        expect(result, isNull);
      });
    });

    group('getFieldsForFarm', () {
      test('should return fields for specific farm', () async {
        // Arrange
        const farmId = 'farm_001';
        final field1 = SampleFields.createWheatField(farmId: farmId);
        final field2 = SampleFields.createDatePalmField(farmId: farmId);
        final field3 =
            SampleFields.createWheatField(id: 'field_f2', farmId: 'farm_002');

        mockDatabase.seedField(field1);
        mockDatabase.seedField(field2);
        mockDatabase.seedField(field3);

        // Act
        final fields = await fieldsRepo.getFieldsForFarm(farmId);

        // Assert
        expect(fields.length, 2);
        expect(fields.every((f) => f.farmId == farmId), isTrue);
      });
    });

    group('createField', () {
      test('should create field with proper boundary calculation', () async {
        // Arrange
        const tenantId = 'tenant_test';
        const name = 'Test Field';
        final boundary = [
          const LatLng(24.7136, 46.6753),
          const LatLng(24.7140, 46.6753),
          const LatLng(24.7140, 46.6760),
          const LatLng(24.7136, 46.6760),
          const LatLng(24.7136, 46.6753), // Close the polygon
        ];

        // Act
        final field = await fieldsRepo.createField(
          tenantId: tenantId,
          name: name,
          boundary: boundary,
          cropType: 'wheat',
        );

        // Assert
        expect(field.id, isNotEmpty);
        expect(field.name, name);
        expect(field.tenantId, tenantId);
        expect(field.boundary, boundary);
        expect(field.areaHectares, greaterThan(0));
        expect(field.centroid, isNotNull);
        expect(field.synced, isFalse);

        // Verify saved in database
        final savedField = await mockDatabase.getFieldById(field.id);
        expect(savedField, isNotNull);
      });

      test('should queue new field in outbox', () async {
        // Arrange & Act
        await fieldsRepo.createField(
          tenantId: 'tenant_test',
          name: 'New Field',
          boundary: [
            const LatLng(24.7136, 46.6753),
            const LatLng(24.7140, 46.6753),
            const LatLng(24.7140, 46.6760),
            const LatLng(24.7136, 46.6760),
            const LatLng(24.7136, 46.6753),
          ],
        );

        // Assert
        final outboxItems = await mockDatabase.getPendingOutbox();
        expect(outboxItems, isNotEmpty);
        expect(outboxItems.first.method, 'POST');
        expect(outboxItems.first.apiEndpoint, '/api/v1/fields');
      });

      test('should generate unique ID for each field', () async {
        // Act
        final field1 = await fieldsRepo.createField(
          tenantId: 'tenant_test',
          name: 'Field 1',
          boundary: [
            const LatLng(24.7136, 46.6753),
            const LatLng(24.7140, 46.6753),
            const LatLng(24.7140, 46.6760),
            const LatLng(24.7136, 46.6760),
            const LatLng(24.7136, 46.6753),
          ],
        );

        final field2 = await fieldsRepo.createField(
          tenantId: 'tenant_test',
          name: 'Field 2',
          boundary: [
            const LatLng(24.7146, 46.6763),
            const LatLng(24.7150, 46.6763),
            const LatLng(24.7150, 46.6770),
            const LatLng(24.7146, 46.6770),
            const LatLng(24.7146, 46.6763),
          ],
        );

        // Assert
        expect(field1.id, isNot(equals(field2.id)));
      });
    });

    group('deleteField', () {
      test('should soft delete field locally', () async {
        // Arrange
        const fieldId = 'field_001';
        final field = SampleFields.createWheatField(id: fieldId);
        mockDatabase.seedField(field);

        // Act
        await fieldsRepo.deleteField(fieldId);

        // Assert
        final deletedField = await mockDatabase.getFieldById(fieldId);
        expect(deletedField!.isDeleted, isTrue);
        expect(deletedField.synced, isFalse);
      });

      test('should queue deletion in outbox', () async {
        // Arrange
        const fieldId = 'field_001';
        final field = SampleFields.createWheatField(id: fieldId);
        mockDatabase.seedField(field);

        // Act
        await fieldsRepo.deleteField(fieldId);

        // Assert
        final outboxItems = await mockDatabase.getPendingOutbox();
        expect(outboxItems, isNotEmpty);
        expect(outboxItems.first.method, 'DELETE');
      });
    });

    group('refreshFromServer', () {
      test('should throw SyncException when offline', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(false);

        // Act & Assert
        await expectLater(
          fieldsRepo.refreshFromServer('tenant_test'),
          throwsA(isA<SyncException>()),
        );
      });

      test('should fetch and save fields from server', () async {
        // Arrange
        mockNetworkStatus.setOnlineStatus(true);

        final serverFields = [
          {
            'id': 'server_field_1',
            'properties': {
              'name': 'Server Field',
              'tenant_id': 'tenant_test',
              'area_hectares': 5.5,
            },
            'geometry': {
              'type': 'Polygon',
              'coordinates': [
                [
                  [46.6753, 24.7136],
                  [46.6753, 24.7140],
                  [46.6760, 24.7140],
                  [46.6760, 24.7136],
                  [46.6753, 24.7136],
                ]
              ],
            },
          },
        ];

        when(() => mockApi.fetchFields(tenantId: any(named: 'tenantId')))
            .thenAnswer((_) async => serverFields);

        // Act
        final count = await fieldsRepo.refreshFromServer('tenant_test');

        // Assert
        expect(count, serverFields.length);
        verify(() => mockApi.fetchFields(tenantId: any(named: 'tenantId')))
            .called(1);
      });
    });

    group('getUnsyncedFields', () {
      test('should return only unsynced fields', () async {
        // Arrange
        final syncedField = SampleFields.createWheatField(synced: true);
        final unsyncedField = SampleFields.createDatePalmField(synced: false);

        mockDatabase.seedField(syncedField);
        mockDatabase.seedField(unsyncedField);

        // Act
        final unsyncedFields = await fieldsRepo.getUnsyncedFields();

        // Assert
        expect(unsyncedFields.length, 1);
        expect(unsyncedFields.first.synced, isFalse);
      });
    });
  });

  group('Field domain entity', () {
    test('should calculate isHealthy based on NDVI', () {
      final healthyField = domain.Field(
        id: 'field_001',
        tenantId: 'tenant_test',
        name: 'Healthy Field',
        boundary: [],
        areaHectares: 5.0,
        ndviCurrent: 0.7,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(healthyField.ndviCurrent, greaterThan(0.5));
    });

    test('should have proper equality', () {
      final field1 = domain.Field(
        id: 'field_001',
        tenantId: 'tenant_test',
        name: 'Test Field',
        boundary: [],
        areaHectares: 5.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final field2 = domain.Field(
        id: 'field_001',
        tenantId: 'tenant_test',
        name: 'Test Field',
        boundary: [],
        areaHectares: 5.0,
        createdAt: field1.createdAt,
        updatedAt: field1.updatedAt,
      );

      expect(field1.id, field2.id);
    });
  });
}
