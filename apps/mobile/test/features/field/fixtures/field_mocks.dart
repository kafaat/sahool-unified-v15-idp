/// Field Test Mocks for SAHOOL Field App
/// محاكاة اختبار الحقول
///
/// Contains mock implementations for field-related unit tests using mocktail

import 'dart:async';
import 'package:mocktail/mocktail.dart';
import 'package:latlong2/latlong.dart';
import 'package:drift/drift.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

import 'package:sahool_field_app/core/http/api_client.dart';
import 'package:sahool_field_app/core/storage/database.dart';
import 'package:sahool_field_app/core/sync/network_status.dart';
import 'package:sahool_field_app/features/field/data/remote/fields_api.dart';
import 'package:sahool_field_app/features/field/data/repo/fields_repo.dart';
import 'package:sahool_field_app/features/field/domain/entities/field.dart' as domain;

// =============================================================================
// Mock Classes
// =============================================================================

/// Mock API Client
class MockApiClient extends Mock implements ApiClient {}

/// Mock Fields API
class MockFieldsApi extends Mock implements FieldsApi {}

/// Mock App Database
class MockAppDatabase extends Mock implements AppDatabase {}

/// Mock Network Status
class MockNetworkStatus extends Mock implements NetworkStatus {}

/// Mock Connectivity
class MockConnectivity extends Mock implements Connectivity {}

// =============================================================================
// Fake Classes for Matchers
// =============================================================================

/// Fake FieldsCompanion for argument matchers
class FakeFieldsCompanion extends Fake implements FieldsCompanion {}

/// Fake OutboxCompanion for argument matchers
class FakeOutboxCompanion extends Fake implements OutboxCompanion {}

/// Fake LatLng for argument matchers
class FakeLatLng extends Fake implements LatLng {}

// =============================================================================
// Test Database Field Helper
// =============================================================================

/// Creates a mock Field (database entity) for testing
Field createMockDbField({
  String id = 'field_001',
  String? remoteId,
  String tenantId = 'tenant_1',
  String? farmId,
  String name = 'Test Field',
  String? cropType,
  List<LatLng>? boundary,
  LatLng? centroid,
  double areaHectares = 5.0,
  String? status = 'active',
  double? ndviCurrent,
  DateTime? ndviUpdatedAt,
  bool synced = true,
  bool isDeleted = false,
  DateTime? createdAt,
  DateTime? updatedAt,
  String? etag,
  DateTime? serverUpdatedAt,
}) {
  final now = DateTime.now();
  return _TestField(
    id: id,
    remoteId: remoteId,
    tenantId: tenantId,
    farmId: farmId,
    name: name,
    cropType: cropType,
    boundary: boundary ?? [],
    centroid: centroid,
    areaHectares: areaHectares,
    status: status,
    ndviCurrent: ndviCurrent,
    ndviUpdatedAt: ndviUpdatedAt,
    synced: synced,
    isDeleted: isDeleted,
    createdAt: createdAt ?? now,
    updatedAt: updatedAt ?? now,
    etag: etag,
    serverUpdatedAt: serverUpdatedAt,
  );
}

/// Creates a mock domain Field entity for testing
domain.Field createMockDomainField({
  String id = 'field_001',
  String? remoteId,
  String tenantId = 'tenant_1',
  String? farmId,
  String name = 'Test Field',
  String? cropType,
  List<LatLng>? boundary,
  LatLng? centroid,
  double areaHectares = 5.0,
  String? status = 'active',
  double? ndviCurrent,
  DateTime? ndviUpdatedAt,
  bool synced = true,
  bool isDeleted = false,
  DateTime? createdAt,
  DateTime? updatedAt,
  int pendingTasks = 0,
}) {
  final now = DateTime.now();
  return domain.Field(
    id: id,
    remoteId: remoteId,
    tenantId: tenantId,
    farmId: farmId,
    name: name,
    cropType: cropType,
    boundary: boundary ?? [],
    centroid: centroid,
    areaHectares: areaHectares,
    status: status,
    ndviCurrent: ndviCurrent,
    ndviUpdatedAt: ndviUpdatedAt,
    synced: synced,
    isDeleted: isDeleted,
    createdAt: createdAt ?? now,
    updatedAt: updatedAt ?? now,
    pendingTasks: pendingTasks,
  );
}

/// Internal test implementation of Field database entity
/// Extends Fake so that unimplemented DataClass/Insertable methods
/// (toColumns, toJson, toJsonString, copyWith) compile via noSuchMethod.
class _TestField extends Fake implements Field {
  @override
  final String id;
  @override
  final String? remoteId;
  @override
  final String tenantId;
  @override
  final String? farmId;
  @override
  final String name;
  @override
  final String? cropType;
  @override
  final List<LatLng> boundary;
  @override
  final LatLng? centroid;
  @override
  final double areaHectares;
  @override
  final String? status;
  @override
  final double? ndviCurrent;
  @override
  final DateTime? ndviUpdatedAt;
  @override
  final bool synced;
  @override
  final bool isDeleted;
  @override
  final DateTime createdAt;
  @override
  final DateTime updatedAt;
  @override
  final String? etag;
  @override
  final DateTime? serverUpdatedAt;

  _TestField({
    required this.id,
    this.remoteId,
    required this.tenantId,
    this.farmId,
    required this.name,
    this.cropType,
    required this.boundary,
    this.centroid,
    required this.areaHectares,
    this.status,
    this.ndviCurrent,
    this.ndviUpdatedAt,
    required this.synced,
    required this.isDeleted,
    required this.createdAt,
    required this.updatedAt,
    this.etag,
    this.serverUpdatedAt,
  });
}

// =============================================================================
// Mock Setup Helpers
// =============================================================================

/// Sets up common mock behaviors for FieldsApi
void setupFieldsApiMocks(
  MockFieldsApi mockApi, {
  List<Map<String, dynamic>>? fieldsResponse,
  Exception? fetchError,
}) {
  if (fetchError != null) {
    when(() => mockApi.fetchFields(
      tenantId: any(named: 'tenantId'),
      farmId: any(named: 'farmId'),
    )).thenThrow(fetchError);
  } else {
    when(() => mockApi.fetchFields(
      tenantId: any(named: 'tenantId'),
      farmId: any(named: 'farmId'),
    )).thenAnswer((_) async => fieldsResponse ?? []);
  }
}

/// Sets up common mock behaviors for NetworkStatus
void setupNetworkStatusMocks(
  MockNetworkStatus mockNetworkStatus, {
  bool isOnline = true,
}) {
  when(() => mockNetworkStatus.isOnline).thenReturn(isOnline);
  when(() => mockNetworkStatus.checkOnline()).thenAnswer((_) async => isOnline);
  when(() => mockNetworkStatus.onlineStream).thenAnswer(
    (_) => Stream.value(isOnline),
  );
}

/// Sets up common mock behaviors for AppDatabase field operations
void setupDatabaseFieldMocks(
  MockAppDatabase mockDb, {
  List<Field>? allFields,
  Field? fieldById,
  List<Field>? unsyncedFields,
}) {
  // getAllFields
  when(() => mockDb.getAllFields(any())).thenAnswer(
    (_) async => allFields ?? [],
  );

  // watchAllFields
  when(() => mockDb.watchAllFields(any())).thenAnswer(
    (_) => Stream.value(allFields ?? []),
  );

  // getFieldById
  when(() => mockDb.getFieldById(any())).thenAnswer(
    (_) async => fieldById,
  );

  // getUnsyncedFields
  when(() => mockDb.getUnsyncedFields()).thenAnswer(
    (_) async => unsyncedFields ?? [],
  );

  // insertField - void return
  when(() => mockDb.insertField(any())).thenAnswer((_) async {});

  // upsertField - void return
  when(() => mockDb.upsertField(any())).thenAnswer((_) async {});

  // updateFieldBoundary - void return
  when(() => mockDb.updateFieldBoundary(
    fieldId: any(named: 'fieldId'),
    boundary: any(named: 'boundary'),
    centroid: any(named: 'centroid'),
    areaHectares: any(named: 'areaHectares'),
  )).thenAnswer((_) async {});

  // softDeleteField - void return
  when(() => mockDb.softDeleteField(any())).thenAnswer((_) async {});

  // addToOutbox - void return
  when(() => mockDb.addToOutbox(any())).thenAnswer((_) async {});

  // upsertFieldsFromServer - void return
  when(() => mockDb.upsertFieldsFromServer(any())).thenAnswer((_) async {});

  // getFieldsForFarm
  when(() => mockDb.getFieldsForFarm(any())).thenAnswer(
    (_) async => allFields?.where((f) => f.farmId != null).toList() ?? [],
  );
}

// =============================================================================
// Register Fallback Values
// =============================================================================

/// Call this in setUpAll to register fallback values for mocktail
void registerFieldMockFallbackValues() {
  registerFallbackValue(FakeFieldsCompanion());
  registerFallbackValue(FakeOutboxCompanion());
  registerFallbackValue(FakeLatLng());
  registerFallbackValue(<LatLng>[]);
  registerFallbackValue(<Map<String, dynamic>>[]);
}
