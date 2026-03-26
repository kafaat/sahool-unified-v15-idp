import 'dart:convert';
import 'package:drift/drift.dart';
import 'package:latlong2/latlong.dart';
import 'package:uuid/uuid.dart';

import '../../../../core/storage/database.dart';
import '../../../../core/sync/network_status.dart';
import '../../../../core/geo/geojson.dart';
import '../../../../core/utils/app_logger.dart';
import '../../domain/entities/field.dart' as domain;
import '../remote/fields_api.dart';

/// Fields Repository - Offline-first GIS data access
///
/// Handles:
/// - Local SQLite storage with GeoPolygonConverter
/// - GeoJSON transformation for PostGIS sync
/// - Offline-first create/update operations
class FieldsRepo {
  final AppDatabase _db;
  final FieldsApi _api;
  final NetworkStatus _networkStatus;
  final _uuid = const Uuid();

  FieldsRepo({
    required AppDatabase database,
    required FieldsApi api,
    NetworkStatus? networkStatus,
  })  : _db = database,
        _api = api,
        _networkStatus = networkStatus ?? NetworkStatus();

  // ============================================================
  // Read Operations
  // ============================================================

  /// Get all fields for tenant (from local DB)
  Future<List<domain.Field>> getAllFields(String tenantId) async {
    final dbFields = await _db.getAllFields(tenantId);
    return dbFields.map(_mapDbToEntity).toList();
  }

  /// Watch all fields for tenant (live stream)
  Stream<List<domain.Field>> watchAllFields(String tenantId) {
    return _db.watchAllFields(tenantId).map(
          (dbFields) => dbFields.map(_mapDbToEntity).toList(),
        );
  }

  /// Get field by ID
  Future<domain.Field?> getFieldById(String fieldId) async {
    final dbField = await _db.getFieldById(fieldId);
    return dbField != null ? _mapDbToEntity(dbField) : null;
  }

  /// Get fields for a farm
  Future<List<domain.Field>> getFieldsForFarm(String farmId) async {
    final dbFields = await _db.getFieldsForFarm(farmId);
    return dbFields.map(_mapDbToEntity).toList();
  }

  // ============================================================
  // Write Operations (Offline-First)
  // ============================================================

  /// Create new field with polygon boundary
  ///
  /// 1. Saves locally with auto-calculated area and centroid
  /// 2. Queues GeoJSON payload for PostGIS sync
  Future<domain.Field> createField({
    required String tenantId,
    required String name,
    required List<LatLng> boundary,
    String? cropType,
    String? farmId,
  }) async {
    final fieldId = _uuid.v4();
    final now = DateTime.now();

    // Calculate GIS properties
    final areaHectares = GeoJson.calculateAreaHectares(boundary);
    final centroid = GeoJson.calculateCentroid(boundary);

    // 1. Save to local DB
    await _db.insertField(
      FieldsCompanion.insert(
        id: fieldId,
        tenantId: tenantId,
        farmId: Value(farmId),
        name: name,
        cropType: Value(cropType),
        boundary: boundary,
        centroid: Value(centroid),
        areaHectares: areaHectares,
        createdAt: now,
        updatedAt: now,
      ),
    );

    // 2. Create GeoJSON payload for PostGIS
    final geoJsonPayload = GeoJson.createPolygonFeature(
      boundary: boundary,
      properties: {
        'tenant_id': tenantId,
        'farm_id': farmId,
        'name': name,
        'crop_type': cropType,
        'area_hectares': areaHectares,
        'local_id': fieldId,
      },
    );

    // 3. Add to outbox for sync
    await _db.addToOutbox(
      OutboxCompanion.insert(
        tenantId: tenantId,
        entityType: 'field',
        entityId: fieldId,
        apiEndpoint: '/api/v1/fields',
        method: const Value('POST'),
        payload: jsonEncode(geoJsonPayload),
      ),
    );

    AppLogger.i('Field created locally', tag: 'FieldsRepo', data: {
      'name': name,
      'area_ha': areaHectares.toStringAsFixed(2),
    });

    return domain.Field(
      id: fieldId,
      tenantId: tenantId,
      farmId: farmId,
      name: name,
      cropType: cropType,
      boundary: boundary,
      centroid: centroid,
      areaHectares: areaHectares,
      createdAt: now,
      updatedAt: now,
      synced: false,
    );
  }

  /// Update field boundary (e.g., after redrawing polygon)
  Future<void> updateFieldBoundary({
    required String fieldId,
    required List<LatLng> newBoundary,
  }) async {
    // Calculate new GIS properties
    final areaHectares = GeoJson.calculateAreaHectares(newBoundary);
    final centroid = GeoJson.calculateCentroid(newBoundary);

    // 1. Update local DB
    await _db.updateFieldBoundary(
      fieldId: fieldId,
      boundary: newBoundary,
      centroid: centroid,
      areaHectares: areaHectares,
    );

    // 2. Get field for tenant info
    final field = await _db.getFieldById(fieldId);
    if (field == null) return;

    // 3. Create GeoJSON update payload
    final geoJsonPayload = {
      'field_id': fieldId,
      'remote_id': field.remoteId,
      'tenant_id': field.tenantId,
      'geometry': {
        'type': 'Polygon',
        'coordinates': [newBoundary.toGeoJsonCoordinates()],
      },
      'area_hectares': areaHectares,
    };

    // 4. Add to outbox
    await _db.addToOutbox(
      OutboxCompanion.insert(
        tenantId: field.tenantId,
        entityType: 'field',
        entityId: fieldId,
        apiEndpoint: '/api/v1/fields/$fieldId/boundary',
        method: const Value('PUT'),
        payload: jsonEncode(geoJsonPayload),
      ),
    );

    AppLogger.i('Field boundary updated', tag: 'FieldsRepo', data: {
      'fieldId': fieldId,
      'area_ha': areaHectares.toStringAsFixed(2),
    });
  }

  /// Update field properties (name, crop type, etc.)
  Future<void> updateFieldProperties({
    required String fieldId,
    String? name,
    String? cropType,
    String? status,
  }) async {
    final field = await _db.getFieldById(fieldId);
    if (field == null) return;

    // 1. Update local DB
    await _db.upsertField(
      FieldsCompanion(
        id: Value(fieldId),
        name: name != null ? Value(name) : const Value.absent(),
        cropType: cropType != null ? Value(cropType) : const Value.absent(),
        status: status != null ? Value(status) : const Value.absent(),
        updatedAt: Value(DateTime.now()),
        synced: const Value(false),
      ),
    );

    // 2. Add to outbox
    await _db.addToOutbox(
      OutboxCompanion.insert(
        tenantId: field.tenantId,
        entityType: 'field',
        entityId: fieldId,
        apiEndpoint: '/api/v1/fields/$fieldId',
        method: const Value('PATCH'),
        payload: jsonEncode({
          'field_id': fieldId,
          'remote_id': field.remoteId,
          'tenant_id': field.tenantId,
          if (name != null) 'name': name,
          if (cropType != null) 'crop_type': cropType,
          if (status != null) 'status': status,
        }),
      ),
    );
  }

  /// Soft delete field
  Future<void> deleteField(String fieldId) async {
    final field = await _db.getFieldById(fieldId);
    if (field == null) return;

    // 1. Soft delete locally
    await _db.softDeleteField(fieldId);

    // 2. Add to outbox
    await _db.addToOutbox(
      OutboxCompanion.insert(
        tenantId: field.tenantId,
        entityType: 'field',
        entityId: fieldId,
        apiEndpoint: '/api/v1/fields/$fieldId',
        method: const Value('DELETE'),
        payload: jsonEncode({
          'field_id': fieldId,
          'remote_id': field.remoteId,
          'tenant_id': field.tenantId,
        }),
      ),
    );

    AppLogger.i('Field soft-deleted', tag: 'FieldsRepo', data: {'fieldId': fieldId});
  }

  // ============================================================
  // Sync Operations
  // ============================================================

  /// Refresh fields from server
  Future<int> refreshFromServer(String tenantId) async {
    if (!await _networkStatus.checkOnline()) {
      throw Exception('لا يوجد اتصال بالإنترنت');
    }

    try {
      // Fetch GeoJSON FeatureCollection from server
      final features = await _api.fetchFields(tenantId: tenantId);

      // Convert to map format expected by upsertFieldsFromServer
      final fieldMaps = features.map((feature) {
        final props = feature['properties'] as Map<String, dynamic>;
        return {
          'id': feature['id'] ?? props['local_id'],
          'remote_id': feature['id'],
          'tenant_id': props['tenant_id'] ?? tenantId,
          'farm_id': props['farm_id'],
          'name': props['name'],
          'crop_type': props['crop_type'],
          'geometry': feature['geometry'],
          'area_hectares': props['area_hectares'],
          'status': props['status'],
          'ndvi_current': props['ndvi_current'],
          'ndvi_updated_at': props['ndvi_updated_at'],
          'created_at': props['created_at'] ?? DateTime.now().toIso8601String(),
          'updated_at': props['updated_at'] ?? DateTime.now().toIso8601String(),
        };
      }).toList();

      // Upsert to local DB
      await _db.upsertFieldsFromServer(fieldMaps);

      return fieldMaps.length;
    } catch (e) {
      AppLogger.e('Failed to refresh fields', tag: 'FieldsRepo', error: e);
      rethrow;
    }
  }

  /// Get unsynced fields for manual sync UI
  Future<List<domain.Field>> getUnsyncedFields() async {
    final dbFields = await _db.getUnsyncedFields();
    return dbFields.map(_mapDbToEntity).toList();
  }

  // ============================================================
  // Helpers
  // ============================================================

  /// Map database entity to domain entity
  domain.Field _mapDbToEntity(Field dbField) {
    return domain.Field(
      id: dbField.id,
      remoteId: dbField.remoteId,
      tenantId: dbField.tenantId,
      farmId: dbField.farmId,
      name: dbField.name,
      cropType: dbField.cropType,
      boundary: dbField.boundary,
      centroid: dbField.centroid,
      areaHectares: dbField.areaHectares,
      status: dbField.status,
      ndviCurrent: dbField.ndviCurrent,
      ndviUpdatedAt: dbField.ndviUpdatedAt,
      synced: dbField.synced,
      isDeleted: dbField.isDeleted,
      createdAt: dbField.createdAt,
      updatedAt: dbField.updatedAt,
    );
  }
}
