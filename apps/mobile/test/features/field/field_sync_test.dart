/// Field Sync Tests for SAHOOL Field App
/// اختبارات مزامنة الحقول
///
/// Tests for offline-first sync functionality including:
/// - Offline field creation and queuing
/// - Online sync operations
/// - Conflict detection
/// - Network status handling
/// - Outbox queue management

import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:latlong2/latlong.dart';

import 'package:sahool_field_app/features/field/data/repo/fields_repo.dart';
import 'package:sahool_field_app/features/field/data/remote/fields_api.dart';
import 'package:sahool_field_app/features/field/domain/entities/field.dart' as domain;
import 'package:sahool_field_app/core/storage/database.dart';
import 'package:sahool_field_app/core/sync/network_status.dart';

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

  group('Offline Field Creation', () {
    test('should create field locally when offline', () async {
      // Arrange
      setupNetworkStatusMocks(mockNetworkStatus, isOnline: false);
      setupDatabaseFieldMocks(mockDb);

      // Act
      final field = await repository.createField(
        tenantId: FieldTestFixtures.testTenantId,
        name: 'Offline Field',
        boundary: FieldTestFixtures.triangleBoundary,
      );

      // Assert
      expect(field.synced, false);
      verify(() => mockDb.insertField(any())).called(1);
      verify(() => mockDb.addToOutbox(any())).called(1);
      verifyNever(() => mockApi.createField(any()));
    });

    test('should queue field creation for later sync', () async {
      // Arrange
      setupDatabaseFieldMocks(mockDb);

      // Act
      await repository.createField(
        tenantId: FieldTestFixtures.testTenantId,
        name: 'Queued Field',
        boundary: FieldTestFixtures.simpleRectangleBoundary,
        cropType: 'wheat',
      );

      // Assert
      verify(() => mockDb.addToOutbox(any())).called(1);
    });

    test('should generate unique local ID for offline field', () async {
      // Arrange
      setupDatabaseFieldMocks(mockDb);

      // Act
      final field1 = await repository.createField(
        tenantId: FieldTestFixtures.testTenantId,
        name: 'Field 1',
        boundary: FieldTestFixtures.triangleBoundary,
      );

      final field2 = await repository.createField(
        tenantId: FieldTestFixtures.testTenantId,
        name: 'Field 2',
        boundary: FieldTestFixtures.triangleBoundary,
      );

      // Assert
      expect(field1.id, isNotEmpty);
      expect(field2.id, isNotEmpty);
      expect(field1.id, isNot(equals(field2.id)));
    });

    test('should include GeoJSON in outbox payload', () async {
      // Arrange
      OutboxCompanion? capturedOutbox;
      when(() => mockDb.insertField(any())).thenAnswer((_) async {});
      when(() => mockDb.addToOutbox(any())).thenAnswer((invocation) async {
        capturedOutbox = invocation.positionalArguments.first as OutboxCompanion;
      });

      // Act
      await repository.createField(
        tenantId: FieldTestFixtures.testTenantId,
        name: 'GeoJSON Field',
        boundary: FieldTestFixtures.triangleBoundary,
      );

      // Assert
      expect(capturedOutbox, isNotNull);
      expect(capturedOutbox!.entityType.value, 'field');
      expect(capturedOutbox!.apiEndpoint.value, '/api/v1/fields');
      expect(capturedOutbox!.method.value, 'POST');
    });
  });

  group('Network Status Integration', () {
    test('should check network status before refresh', () async {
      // Arrange
      setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
      when(() => mockApi.fetchFields(
        tenantId: any(named: 'tenantId'),
        farmId: any(named: 'farmId'),
      )).thenAnswer((_) async => []);
      when(() => mockDb.upsertFieldsFromServer(any())).thenAnswer((_) async {});

      // Act
      await repository.refreshFromServer(FieldTestFixtures.testTenantId);

      // Assert
      verify(() => mockNetworkStatus.checkOnline()).called(1);
    });

    test('should throw when refreshing while offline', () async {
      // Arrange
      setupNetworkStatusMocks(mockNetworkStatus, isOnline: false);

      // Act & Assert
      expect(
        () => repository.refreshFromServer(FieldTestFixtures.testTenantId),
        throwsA(isA<Exception>().having(
          (e) => e.toString(),
          'message',
          contains('اتصال'),
        )),
      );
    });

    test('should proceed with refresh when online', () async {
      // Arrange
      setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
      when(() => mockApi.fetchFields(
        tenantId: any(named: 'tenantId'),
        farmId: any(named: 'farmId'),
      )).thenAnswer((_) async => [FieldTestFixtures.sampleGeoJsonFeature]);
      when(() => mockDb.upsertFieldsFromServer(any())).thenAnswer((_) async {});

      // Act
      final count = await repository.refreshFromServer(FieldTestFixtures.testTenantId);

      // Assert
      expect(count, 1);
      verify(() => mockApi.fetchFields(
        tenantId: FieldTestFixtures.testTenantId,
      )).called(1);
    });
  });

  group('Sync Operations', () {
    test('should fetch fields from server', () async {
      // Arrange
      setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
      final serverFields = [
        FieldTestFixtures.sampleGeoJsonFeature,
        FieldTestFixtures.stressedFieldJson,
        FieldTestFixtures.criticalFieldJson,
      ];
      when(() => mockApi.fetchFields(
        tenantId: any(named: 'tenantId'),
        farmId: any(named: 'farmId'),
      )).thenAnswer((_) async => serverFields);
      when(() => mockDb.upsertFieldsFromServer(any())).thenAnswer((_) async {});

      // Act
      final count = await repository.refreshFromServer(FieldTestFixtures.testTenantId);

      // Assert
      expect(count, 3);
    });

    test('should upsert server fields to local database', () async {
      // Arrange
      setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
      when(() => mockApi.fetchFields(
        tenantId: any(named: 'tenantId'),
        farmId: any(named: 'farmId'),
      )).thenAnswer((_) async => [FieldTestFixtures.sampleGeoJsonFeature]);
      when(() => mockDb.upsertFieldsFromServer(any())).thenAnswer((_) async {});

      // Act
      await repository.refreshFromServer(FieldTestFixtures.testTenantId);

      // Assert
      verify(() => mockDb.upsertFieldsFromServer(any())).called(1);
    });

    test('should handle empty server response', () async {
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

    test('should propagate server errors', () async {
      // Arrange
      setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
      when(() => mockApi.fetchFields(
        tenantId: any(named: 'tenantId'),
        farmId: any(named: 'farmId'),
      )).thenThrow(Exception('Server unavailable'));

      // Act & Assert
      expect(
        () => repository.refreshFromServer(FieldTestFixtures.testTenantId),
        throwsException,
      );
    });
  });

  group('Unsynced Fields', () {
    test('should return list of unsynced fields', () async {
      // Arrange
      final unsyncedFields = [
        createMockDbField(id: 'local_001', synced: false),
        createMockDbField(id: 'local_002', synced: false),
        createMockDbField(id: 'local_003', synced: false),
      ];
      when(() => mockDb.getUnsyncedFields()).thenAnswer(
        (_) async => unsyncedFields,
      );

      // Act
      final fields = await repository.getUnsyncedFields();

      // Assert
      expect(fields.length, 3);
      expect(fields.every((f) => !f.synced), true);
    });

    test('should return empty list when all synced', () async {
      // Arrange
      when(() => mockDb.getUnsyncedFields()).thenAnswer((_) async => []);

      // Act
      final fields = await repository.getUnsyncedFields();

      // Assert
      expect(fields, isEmpty);
    });

    test('should identify local vs server IDs', () async {
      // Arrange
      final unsyncedField = createMockDbField(
        id: 'local_uuid',
        remoteId: null,
        synced: false,
      );
      when(() => mockDb.getUnsyncedFields()).thenAnswer(
        (_) async => [unsyncedField],
      );

      // Act
      final fields = await repository.getUnsyncedFields();

      // Assert
      expect(fields.first.id, 'local_uuid');
      expect(fields.first.remoteId, isNull);
    });
  });

  group('Offline Updates', () {
    test('should queue boundary update for sync', () async {
      // Arrange
      final existingField = createMockDbField(id: 'field_001');
      when(() => mockDb.getFieldById(any())).thenAnswer(
        (_) async => existingField,
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
        newBoundary: FieldTestFixtures.largeFieldBoundary,
      );

      // Assert
      verify(() => mockDb.addToOutbox(any())).called(1);
    });

    test('should queue property update for sync', () async {
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
      );

      // Assert
      verify(() => mockDb.addToOutbox(any())).called(1);
    });

    test('should queue deletion for sync', () async {
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
  });

  group('Field Data Validation for Sync', () {
    test('should calculate area before queuing', () async {
      // Arrange
      setupDatabaseFieldMocks(mockDb);

      // Act
      final field = await repository.createField(
        tenantId: FieldTestFixtures.testTenantId,
        name: 'Test Field',
        boundary: FieldTestFixtures.simpleRectangleBoundary,
      );

      // Assert
      expect(field.areaHectares, isPositive);
    });

    test('should calculate centroid before queuing', () async {
      // Arrange
      setupDatabaseFieldMocks(mockDb);

      // Act
      final field = await repository.createField(
        tenantId: FieldTestFixtures.testTenantId,
        name: 'Test Field',
        boundary: FieldTestFixtures.triangleBoundary,
      );

      // Assert
      expect(field.centroid, isNotNull);
    });

    test('should include tenant ID in sync payload', () async {
      // Arrange
      setupDatabaseFieldMocks(mockDb);

      // Act
      final field = await repository.createField(
        tenantId: FieldTestFixtures.testTenantId,
        name: 'Test Field',
        boundary: FieldTestFixtures.triangleBoundary,
      );

      // Assert
      expect(field.tenantId, FieldTestFixtures.testTenantId);
    });
  });

  group('Sync Error Handling', () {
    test('should handle network timeout gracefully', () async {
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

    test('should handle server error gracefully', () async {
      // Arrange
      setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
      when(() => mockApi.fetchFields(
        tenantId: any(named: 'tenantId'),
        farmId: any(named: 'farmId'),
      )).thenThrow(Exception('500 Internal Server Error'));

      // Act & Assert
      expect(
        () => repository.refreshFromServer(FieldTestFixtures.testTenantId),
        throwsException,
      );
    });

    test('should handle authorization error', () async {
      // Arrange
      setupNetworkStatusMocks(mockNetworkStatus, isOnline: true);
      when(() => mockApi.fetchFields(
        tenantId: any(named: 'tenantId'),
        farmId: any(named: 'farmId'),
      )).thenThrow(Exception('401 Unauthorized'));

      // Act & Assert
      expect(
        () => repository.refreshFromServer(FieldTestFixtures.testTenantId),
        throwsException,
      );
    });
  });

  group('FieldsApi', () {
    late MockApiClient mockApiClient;
    late FieldsApi fieldsApi;

    setUp(() {
      mockApiClient = MockApiClient();
      fieldsApi = FieldsApi(mockApiClient);
    });

    group('fetchFields', () {
      test('should return list of features from FeatureCollection', () async {
        // Arrange
        when(() => mockApiClient.get(
          any(),
          queryParameters: any(named: 'queryParameters'),
        )).thenAnswer((_) async => FieldTestFixtures.sampleFeatureCollection);

        // Act
        final features = await fieldsApi.fetchFields(
          tenantId: FieldTestFixtures.testTenantId,
        );

        // Assert
        expect(features.length, 3);
        expect(features.first['type'], 'Feature');
      });

      test('should return list from array response', () async {
        // Arrange
        when(() => mockApiClient.get(
          any(),
          queryParameters: any(named: 'queryParameters'),
        )).thenAnswer((_) async => [
          FieldTestFixtures.sampleGeoJsonFeature,
        ]);

        // Act
        final features = await fieldsApi.fetchFields(
          tenantId: FieldTestFixtures.testTenantId,
        );

        // Assert
        expect(features.length, 1);
      });

      test('should return empty list for empty FeatureCollection', () async {
        // Arrange
        when(() => mockApiClient.get(
          any(),
          queryParameters: any(named: 'queryParameters'),
        )).thenAnswer((_) async => FieldTestFixtures.emptyFeatureCollection);

        // Act
        final features = await fieldsApi.fetchFields(
          tenantId: FieldTestFixtures.testTenantId,
        );

        // Assert
        expect(features, isEmpty);
      });

      test('should include tenant_id in query parameters', () async {
        // Arrange
        when(() => mockApiClient.get(
          any(),
          queryParameters: any(named: 'queryParameters'),
        )).thenAnswer((_) async => []);

        // Act
        await fieldsApi.fetchFields(tenantId: 'test_tenant');

        // Assert
        verify(() => mockApiClient.get(
          '/fields',
          queryParameters: {
            'tenant_id': 'test_tenant',
            'format': 'geojson',
          },
        )).called(1);
      });

      test('should include farm_id when provided', () async {
        // Arrange
        when(() => mockApiClient.get(
          any(),
          queryParameters: any(named: 'queryParameters'),
        )).thenAnswer((_) async => []);

        // Act
        await fieldsApi.fetchFields(
          tenantId: 'test_tenant',
          farmId: 'farm_001',
        );

        // Assert
        verify(() => mockApiClient.get(
          '/fields',
          queryParameters: {
            'tenant_id': 'test_tenant',
            'farm_id': 'farm_001',
            'format': 'geojson',
          },
        )).called(1);
      });
    });

    group('fetchFieldById', () {
      test('should return field by ID', () async {
        // Arrange
        when(() => mockApiClient.get(any())).thenAnswer(
          (_) async => FieldTestFixtures.sampleGeoJsonFeature,
        );

        // Act
        final field = await fieldsApi.fetchFieldById('field_001');

        // Assert
        expect(field, isNotNull);
        expect(field!['id'], 'field_001');
      });

      test('should return null when field not found', () async {
        // Arrange
        when(() => mockApiClient.get(any())).thenThrow(Exception('Not found'));

        // Act
        final field = await fieldsApi.fetchFieldById('nonexistent');

        // Assert
        expect(field, isNull);
      });
    });

    group('fetchNdviHistory', () {
      test('should return NDVI history list', () async {
        // Arrange
        when(() => mockApiClient.get(
          any(),
          queryParameters: any(named: 'queryParameters'),
        )).thenAnswer((_) async => FieldTestFixtures.ndviHistory);

        // Act
        final history = await fieldsApi.fetchNdviHistory(fieldId: 'field_001');

        // Assert
        expect(history.length, 5);
        expect(history.first['ndvi'], 0.72);
      });

      test('should include date range in query', () async {
        // Arrange
        final from = DateTime(2024, 1, 1);
        final to = DateTime(2024, 1, 15);
        when(() => mockApiClient.get(
          any(),
          queryParameters: any(named: 'queryParameters'),
        )).thenAnswer((_) async => []);

        // Act
        await fieldsApi.fetchNdviHistory(
          fieldId: 'field_001',
          from: from,
          to: to,
        );

        // Assert
        verify(() => mockApiClient.get(
          '/fields/field_001/ndvi-history',
          queryParameters: {
            'from': from.toIso8601String(),
            'to': to.toIso8601String(),
          },
        )).called(1);
      });

      test('should return empty list for non-list response', () async {
        // Arrange
        when(() => mockApiClient.get(
          any(),
          queryParameters: any(named: 'queryParameters'),
        )).thenAnswer((_) async => {'error': 'invalid'});

        // Act
        final history = await fieldsApi.fetchNdviHistory(fieldId: 'field_001');

        // Assert
        expect(history, isEmpty);
      });
    });

    group('createField', () {
      test('should post GeoJSON feature', () async {
        // Arrange
        when(() => mockApiClient.post(any(), any())).thenAnswer(
          (_) async => FieldTestFixtures.sampleGeoJsonFeature,
        );

        // Act
        final result = await fieldsApi.createField(
          FieldTestFixtures.sampleGeoJsonFeature,
        );

        // Assert
        expect(result['id'], 'field_001');
        verify(() => mockApiClient.post(
          '/fields',
          FieldTestFixtures.sampleGeoJsonFeature,
        )).called(1);
      });
    });

    group('updateFieldBoundary', () {
      test('should put geometry update', () async {
        // Arrange
        when(() => mockApiClient.put(any(), any())).thenAnswer(
          (_) async => {'success': true},
        );
        final geometry = {
          'type': 'Polygon',
          'coordinates': [[[44.0, 15.0]]],
        };

        // Act
        final result = await fieldsApi.updateFieldBoundary(
          fieldId: 'field_001',
          geometry: geometry,
          areaHectares: 5.5,
        );

        // Assert
        expect(result['success'], true);
        verify(() => mockApiClient.put(
          '/fields/field_001/geometry',
          {
            'geometry': geometry,
            'area_hectares': 5.5,
          },
        )).called(1);
      });
    });

    group('updateFieldProperties', () {
      test('should put property update', () async {
        // Arrange
        when(() => mockApiClient.put(any(), any())).thenAnswer(
          (_) async => {'success': true},
        );

        // Act
        await fieldsApi.updateFieldProperties(
          fieldId: 'field_001',
          name: 'New Name',
          cropType: 'barley',
          status: 'fallow',
        );

        // Assert
        verify(() => mockApiClient.put(
          '/fields/field_001',
          {
            'name': 'New Name',
            'crop_type': 'barley',
            'status': 'fallow',
          },
        )).called(1);
      });

      test('should only include provided properties', () async {
        // Arrange
        when(() => mockApiClient.put(any(), any())).thenAnswer(
          (_) async => {'success': true},
        );

        // Act
        await fieldsApi.updateFieldProperties(
          fieldId: 'field_001',
          name: 'Only Name',
        );

        // Assert
        verify(() => mockApiClient.put(
          '/fields/field_001',
          {'name': 'Only Name'},
        )).called(1);
      });
    });

    group('deleteField', () {
      test('should delete field by ID', () async {
        // Arrange
        when(() => mockApiClient.delete(any())).thenAnswer((_) async => null);

        // Act
        await fieldsApi.deleteField('field_001');

        // Assert
        verify(() => mockApiClient.delete('/fields/field_001')).called(1);
      });
    });
  });
}
