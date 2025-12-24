/// Sample Fields Data for Testing
/// بيانات الحقول النموذجية للاختبارات

import 'package:sahool_field_app/core/storage/database.dart';
import 'package:latlong2/latlong.dart';
import 'package:drift/drift.dart';

class SampleFields {
  /// Sample wheat field
  static Field createWheatField({
    String? id,
    String tenantId = 'tenant_test',
  }) {
    return Field(
      id: id ?? 'field_wheat_001',
      remoteId: 'remote_wheat_001',
      tenantId: tenantId,
      farmId: 'farm_001',
      name: 'حقل القمح الشمالي',
      cropType: 'wheat',
      boundary: [
        const LatLng(15.3694, 44.1910),
        const LatLng(15.3700, 44.1915),
        const LatLng(15.3690, 44.1920),
        const LatLng(15.3685, 44.1912),
      ],
      centroid: const LatLng(15.3692, 44.1914),
      areaHectares: 150.5,
      status: 'active',
      ndviCurrent: 0.75,
      ndviUpdatedAt: DateTime.now().subtract(const Duration(days: 1)),
      synced: true,
      isDeleted: false,
      createdAt: DateTime.now().subtract(const Duration(days: 30)),
      updatedAt: DateTime.now().subtract(const Duration(days: 1)),
      etag: 'etag_wheat_001',
      serverUpdatedAt: DateTime.now().subtract(const Duration(days: 1)),
    );
  }

  /// Sample vegetable field
  static Field createVegetableField({
    String? id,
    String tenantId = 'tenant_test',
  }) {
    return Field(
      id: id ?? 'field_veg_001',
      remoteId: 'remote_veg_001',
      tenantId: tenantId,
      farmId: 'farm_001',
      name: 'البيت المحمي للخضروات',
      cropType: 'vegetables',
      boundary: [
        const LatLng(15.3650, 44.1890),
        const LatLng(15.3655, 44.1895),
        const LatLng(15.3648, 44.1898),
        const LatLng(15.3645, 44.1892),
      ],
      centroid: const LatLng(15.3650, 44.1894),
      areaHectares: 50.0,
      status: 'active',
      ndviCurrent: 0.82,
      ndviUpdatedAt: DateTime.now().subtract(const Duration(hours: 12)),
      synced: true,
      isDeleted: false,
      createdAt: DateTime.now().subtract(const Duration(days: 60)),
      updatedAt: DateTime.now().subtract(const Duration(hours: 12)),
      etag: 'etag_veg_001',
      serverUpdatedAt: DateTime.now().subtract(const Duration(hours: 12)),
    );
  }

  /// Sample fallow field
  static Field createFallowField({
    String? id,
    String tenantId = 'tenant_test',
  }) {
    return Field(
      id: id ?? 'field_fallow_001',
      remoteId: 'remote_fallow_001',
      tenantId: tenantId,
      farmId: 'farm_001',
      name: 'الحقل البور',
      cropType: null,
      boundary: [
        const LatLng(15.3720, 44.1930),
        const LatLng(15.3730, 44.1940),
        const LatLng(15.3715, 44.1945),
        const LatLng(15.3710, 44.1935),
      ],
      centroid: const LatLng(15.3719, 44.1938),
      areaHectares: 200.0,
      status: 'fallow',
      ndviCurrent: 0.35,
      ndviUpdatedAt: DateTime.now().subtract(const Duration(days: 7)),
      synced: true,
      isDeleted: false,
      createdAt: DateTime.now().subtract(const Duration(days: 90)),
      updatedAt: DateTime.now().subtract(const Duration(days: 7)),
      etag: 'etag_fallow_001',
      serverUpdatedAt: DateTime.now().subtract(const Duration(days: 7)),
    );
  }

  /// Sample unsynced field
  static Field createUnsyncedField({
    String? id,
    String tenantId = 'tenant_test',
  }) {
    return Field(
      id: id ?? 'field_unsynced_001',
      remoteId: null,
      tenantId: tenantId,
      farmId: 'farm_001',
      name: 'حقل جديد غير متزامن',
      cropType: 'corn',
      boundary: [
        const LatLng(15.3600, 44.1850),
        const LatLng(15.3610, 44.1860),
        const LatLng(15.3595, 44.1865),
        const LatLng(15.3590, 44.1855),
      ],
      centroid: const LatLng(15.3599, 44.1858),
      areaHectares: 75.0,
      status: 'active',
      ndviCurrent: null,
      ndviUpdatedAt: null,
      synced: false,
      isDeleted: false,
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
      etag: null,
      serverUpdatedAt: null,
    );
  }

  /// Sample deleted field
  static Field createDeletedField({
    String? id,
    String tenantId = 'tenant_test',
  }) {
    return Field(
      id: id ?? 'field_deleted_001',
      remoteId: 'remote_deleted_001',
      tenantId: tenantId,
      farmId: 'farm_001',
      name: 'حقل محذوف',
      cropType: 'wheat',
      boundary: [
        const LatLng(15.3500, 44.1800),
        const LatLng(15.3510, 44.1810),
        const LatLng(15.3495, 44.1815),
        const LatLng(15.3490, 44.1805),
      ],
      centroid: const LatLng(15.3499, 44.1808),
      areaHectares: 100.0,
      status: 'inactive',
      ndviCurrent: null,
      ndviUpdatedAt: null,
      synced: true,
      isDeleted: true,
      createdAt: DateTime.now().subtract(const Duration(days: 120)),
      updatedAt: DateTime.now().subtract(const Duration(days: 10)),
      etag: 'etag_deleted_001',
      serverUpdatedAt: DateTime.now().subtract(const Duration(days: 10)),
    );
  }

  /// Create list of sample fields
  static List<Field> createSampleFieldList({
    String tenantId = 'tenant_test',
  }) {
    return [
      createWheatField(tenantId: tenantId),
      createVegetableField(tenantId: tenantId),
      createFallowField(tenantId: tenantId),
      createUnsyncedField(tenantId: tenantId),
    ];
  }

  /// Create FieldsCompanion for insertion
  static FieldsCompanion createFieldCompanion({
    String? id,
    String tenantId = 'tenant_test',
    String name = 'حقل اختباري',
    String cropType = 'wheat',
    double areaHectares = 100.0,
  }) {
    return FieldsCompanion.insert(
      id: id ?? 'field_${DateTime.now().millisecondsSinceEpoch}',
      tenantId: tenantId,
      farmId: const Value('farm_001'),
      name: name,
      cropType: Value(cropType),
      boundary: [
        const LatLng(15.3694, 44.1910),
        const LatLng(15.3700, 44.1915),
        const LatLng(15.3690, 44.1920),
      ],
      centroid: const Value(LatLng(15.3695, 44.1915)),
      areaHectares: areaHectares,
      status: const Value('active'),
      createdAt: DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }

  /// Simple polygon for testing
  static List<LatLng> createSimplePolygon() {
    return [
      const LatLng(15.3694, 44.1910),
      const LatLng(15.3700, 44.1915),
      const LatLng(15.3690, 44.1920),
      const LatLng(15.3685, 44.1912),
    ];
  }

  /// Calculate centroid from polygon
  static LatLng calculateCentroid(List<LatLng> polygon) {
    if (polygon.isEmpty) return const LatLng(0, 0);

    double sumLat = 0;
    double sumLng = 0;

    for (final point in polygon) {
      sumLat += point.latitude;
      sumLng += point.longitude;
    }

    return LatLng(
      sumLat / polygon.length,
      sumLng / polygon.length,
    );
  }
}
