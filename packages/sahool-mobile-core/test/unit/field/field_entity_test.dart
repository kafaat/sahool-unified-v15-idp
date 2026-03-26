/// Comprehensive Field Domain Entity Tests
/// اختبارات شاملة لكيان الحقل الزراعي
///
/// Tests for:
/// - Field entity construction and properties
/// - NDVI health status calculation
/// - FieldStatus enum behavior
/// - GIS boundary handling
/// - JSON serialization/deserialization
/// - copyWith functionality
/// - Computed properties
///
/// Run with: flutter test test/unit/field/field_entity_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_mobile_core/features/field/domain/entities/field.dart';

/// Creates a sample field for testing
Field createTestField({
  String id = 'field-test-001',
  String tenantId = 'tenant-001',
  String name = 'Test Field',
  double areaHectares = 10.0,
  double? ndviCurrent,
  bool synced = false,
  bool isDeleted = false,
  List<LatLng>? boundary,
  String? cropType,
  String? farmId,
}) {
  final now = DateTime(2025, 1, 15, 8, 0, 0);
  return Field(
    id: id,
    tenantId: tenantId,
    name: name,
    areaHectares: areaHectares,
    ndviCurrent: ndviCurrent,
    synced: synced,
    isDeleted: isDeleted,
    boundary: boundary ??
        [
          const LatLng(24.7, 46.7),
          const LatLng(24.7, 46.8),
          const LatLng(24.8, 46.8),
          const LatLng(24.8, 46.7),
        ],
    createdAt: now,
    updatedAt: now,
    cropType: cropType,
    farmId: farmId,
  );
}

void main() {
  // ============================================================
  // FieldStatus Enum Tests
  // ============================================================
  group('FieldStatus Enum - تعداد حالة الحقل', () {
    test('has all expected values', () {
      expect(FieldStatus.values.length, equals(4));
      expect(FieldStatus.values, contains(FieldStatus.healthy));
      expect(FieldStatus.values, contains(FieldStatus.stressed));
      expect(FieldStatus.values, contains(FieldStatus.critical));
      expect(FieldStatus.values, contains(FieldStatus.unknown));
    });

    test('statusFromNdvi returns healthy for ndvi >= 0.6', () {
      expect(Field.statusFromNdvi(0.6), equals(FieldStatus.healthy));
      expect(Field.statusFromNdvi(0.7), equals(FieldStatus.healthy));
      expect(Field.statusFromNdvi(0.8), equals(FieldStatus.healthy));
      expect(Field.statusFromNdvi(1.0), equals(FieldStatus.healthy));
    });

    test('statusFromNdvi returns stressed for ndvi 0.4-0.599', () {
      expect(Field.statusFromNdvi(0.4), equals(FieldStatus.stressed));
      expect(Field.statusFromNdvi(0.5), equals(FieldStatus.stressed));
      expect(Field.statusFromNdvi(0.599), equals(FieldStatus.stressed));
    });

    test('statusFromNdvi returns critical for ndvi > 0.0 and < 0.4', () {
      expect(Field.statusFromNdvi(0.01), equals(FieldStatus.critical));
      expect(Field.statusFromNdvi(0.2), equals(FieldStatus.critical));
      expect(Field.statusFromNdvi(0.399), equals(FieldStatus.critical));
    });

    test('statusFromNdvi returns unknown for ndvi = 0.0 or negative', () {
      expect(Field.statusFromNdvi(0.0), equals(FieldStatus.unknown));
      expect(Field.statusFromNdvi(-0.1), equals(FieldStatus.unknown));
    });
  });

  // ============================================================
  // Field Entity Construction Tests
  // ============================================================
  group('Field Entity Construction - إنشاء كيان الحقل', () {
    test('creates field with required fields', () {
      final field = createTestField();

      expect(field.id, equals('field-test-001'));
      expect(field.tenantId, equals('tenant-001'));
      expect(field.name, equals('Test Field'));
      expect(field.areaHectares, equals(10.0));
      expect(field.synced, isFalse);
      expect(field.isDeleted, isFalse);
    });

    test('default ndvi is 0.0 when ndviCurrent is null', () {
      final field = createTestField(ndviCurrent: null);
      expect(field.ndvi, equals(0.0));
    });

    test('uses provided ndviCurrent value', () {
      final field = createTestField(ndviCurrent: 0.75);
      expect(field.ndvi, equals(0.75));
    });

    test('areaHa returns same as areaHectares', () {
      final field = createTestField(areaHectares: 15.5);
      expect(field.areaHa, equals(field.areaHectares));
      expect(field.areaHa, equals(15.5));
    });

    test('optional fields have correct defaults', () {
      final field = createTestField();
      expect(field.remoteId, isNull);
      expect(field.farmId, isNull);
      expect(field.cropType, isNull);
      expect(field.centroid, isNull);
      expect(field.status, isNull);
      expect(field.ndviUpdatedAt, isNull);
      expect(field.pendingTasks, equals(0));
    });
  });

  // ============================================================
  // NDVI Health Status Tests
  // ============================================================
  group('NDVI Health Status - حالة الصحة من NDVI', () {
    test('healthy field (NDVI >= 0.6)', () {
      final field = createTestField(ndviCurrent: 0.72);
      expect(field.healthStatus, equals(FieldStatus.healthy));
      expect(field.needsAttention, isFalse);
      expect(field.isCritical, isFalse);
    });

    test('stressed field (NDVI 0.4-0.6)', () {
      final field = createTestField(ndviCurrent: 0.45);
      expect(field.healthStatus, equals(FieldStatus.stressed));
      expect(field.needsAttention, isTrue);
      expect(field.isCritical, isFalse);
    });

    test('critical field (NDVI < 0.4)', () {
      final field = createTestField(ndviCurrent: 0.25);
      expect(field.healthStatus, equals(FieldStatus.critical));
      expect(field.needsAttention, isTrue);
      expect(field.isCritical, isTrue);
    });

    test('unknown health status (no NDVI data)', () {
      final field = createTestField(ndviCurrent: null);
      expect(field.healthStatus, equals(FieldStatus.unknown));
      expect(field.isCritical, isFalse);
    });

    test('health percentage calculation', () {
      expect(createTestField(ndviCurrent: 0.75).healthPercentage, equals(75));
      expect(createTestField(ndviCurrent: 0.45).healthPercentage, equals(45));
      expect(createTestField(ndviCurrent: 0.0).healthPercentage, equals(0));
      expect(createTestField(ndviCurrent: 1.0).healthPercentage, equals(100));
    });

    test('health percentage rounds correctly', () {
      expect(createTestField(ndviCurrent: 0.756).healthPercentage, equals(76));
      expect(createTestField(ndviCurrent: 0.754).healthPercentage, equals(75));
    });
  });

  // ============================================================
  // GIS Boundary Tests
  // ============================================================
  group('GIS Boundary - حدود الحقل الجغرافية', () {
    test('hasBoundary returns true when boundary is not empty', () {
      final field = createTestField();
      expect(field.hasBoundary, isTrue);
    });

    test('hasBoundary returns false for empty boundary', () {
      final field = createTestField(boundary: []);
      expect(field.hasBoundary, isFalse);
    });

    test('boundaryPointCount returns correct number', () {
      final boundary = [
        const LatLng(24.7, 46.7),
        const LatLng(24.7, 46.8),
        const LatLng(24.8, 46.8),
        const LatLng(24.8, 46.7),
      ];
      final field = createTestField(boundary: boundary);
      expect(field.boundaryPointCount, equals(4));
    });

    test('centerLat and centerLng return null when centroid is null', () {
      final field = createTestField();
      expect(field.centerLat, isNull);
      expect(field.centerLng, isNull);
    });

    test('centerLat and centerLng return correct values when centroid is set', () {
      final now = DateTime.now();
      final field = Field(
        id: 'field-1',
        tenantId: 'tenant-1',
        name: 'Test',
        boundary: const [],
        areaHectares: 5.0,
        centroid: const LatLng(24.75, 46.75),
        createdAt: now,
        updatedAt: now,
      );

      expect(field.centerLat, equals(24.75));
      expect(field.centerLng, equals(46.75));
    });
  });

  // ============================================================
  // copyWith Tests
  // ============================================================
  group('Field.copyWith - نسخ مع تعديل', () {
    test('copyWith preserves unchanged fields', () {
      final original = createTestField(
        name: 'Original Field',
        areaHectares: 10.0,
        ndviCurrent: 0.65,
      );

      final copied = original.copyWith(name: 'Updated Field');

      expect(copied.name, equals('Updated Field'));
      expect(copied.areaHectares, equals(10.0));
      expect(copied.ndviCurrent, equals(0.65));
      expect(copied.id, equals(original.id));
      expect(copied.tenantId, equals(original.tenantId));
    });

    test('copyWith updates synced status', () {
      final unsynced = createTestField(synced: false);
      final synced = unsynced.copyWith(synced: true);

      expect(unsynced.synced, isFalse);
      expect(synced.synced, isTrue);
    });

    test('copyWith updates isDeleted for soft delete', () {
      final active = createTestField(isDeleted: false);
      final deleted = active.copyWith(isDeleted: true);

      expect(active.isDeleted, isFalse);
      expect(deleted.isDeleted, isTrue);
    });

    test('copyWith updates NDVI value', () {
      final field = createTestField(ndviCurrent: 0.5);
      final updated = field.copyWith(ndviCurrent: 0.75);

      expect(updated.ndviCurrent, equals(0.75));
      expect(updated.healthStatus, equals(FieldStatus.healthy));
    });

    test('copyWith updates area', () {
      final field = createTestField(areaHectares: 5.0);
      final updated = field.copyWith(areaHectares: 12.5);

      expect(updated.areaHectares, equals(12.5));
    });
  });

  // ============================================================
  // JSON Serialization Tests
  // ============================================================
  group('Field JSON Serialization - التسلسل عبر JSON', () {
    test('toJson returns GeoJSON Feature with properties map', () {
      final field = createTestField(
        id: 'field-json-1',
        tenantId: 'tenant-json',
        name: 'JSON Test Field',
        areaHectares: 7.5,
        ndviCurrent: 0.68,
      );

      final json = field.toJson();

      expect(json, isA<Map<String, dynamic>>());
      // GeoJSON top-level shape
      expect(json['type'], equals('Feature'));
      expect(json['id'], equals('field-json-1'));
      expect(json['geometry'], isA<Map<String, dynamic>>());
      // Properties are nested under 'properties' with snake_case keys
      final props = json['properties'] as Map<String, dynamic>;
      expect(props['tenant_id'], equals('tenant-json'));
      expect(props['name'], equals('JSON Test Field'));
      expect(props['area_hectares'], equals(7.5));
      expect(props['ndvi_current'], equals(0.68));
    });

    test('fromJson creates field from valid GeoJSON', () {
      final now = DateTime(2025, 1, 15, 8, 0, 0);
      // Construct GeoJSON Feature with snake_case keys under 'properties'
      final json = {
        'type': 'Feature',
        'id': 'field-from-json',
        'geometry': {
          'type': 'Polygon',
          'coordinates': [
            [
              [46.7, 24.7],
              [46.8, 24.7],
              [46.8, 24.8],
              [46.7, 24.8],
              [46.7, 24.7],
            ]
          ],
        },
        'properties': {
          'id': 'field-from-json',
          'tenant_id': 'tenant-json',
          'name': 'From JSON Field',
          'area_hectares': 8.5,
          'ndvi_current': 0.72,
          'synced': false,
          'is_deleted': false,
          'created_at': now.toIso8601String(),
          'updated_at': now.toIso8601String(),
        },
      };

      final field = Field.fromJson(json);

      expect(field.id, equals('field-from-json'));
      expect(field.tenantId, equals('tenant-json'));
      expect(field.name, equals('From JSON Field'));
      expect(field.areaHectares, equals(8.5));
      expect(field.ndviCurrent, equals(0.72));
      expect(field.synced, isFalse);
    });

    test('toJson handles null optional fields', () {
      final field = createTestField(
        cropType: null,
        farmId: null,
        ndviCurrent: null,
      );

      final json = field.toJson();
      expect(json, isA<Map<String, dynamic>>());
    });
  });

  // ============================================================
  // Crop Type Tests
  // ============================================================
  group('Crop Type - نوع المحصول', () {
    test('supports wheat as crop type', () {
      final field = createTestField(cropType: 'wheat');
      expect(field.cropType, equals('wheat'));
    });

    test('supports various Arabic crop names', () {
      final crops = ['قمح', 'شعير', 'نخيل', 'طماطم', 'خيار', 'برسيم'];
      for (final crop in crops) {
        final field = createTestField(cropType: crop);
        expect(field.cropType, equals(crop));
      }
    });

    test('null crop type is handled', () {
      final field = createTestField(cropType: null);
      expect(field.cropType, isNull);
    });
  });

  // ============================================================
  // Multi-tenant Tests
  // ============================================================
  group('Multi-tenant Field Isolation - عزل الحقول متعددة المستأجرين', () {
    test('fields are scoped to their tenant', () {
      final tenantAField = createTestField(
        id: 'field-1',
        tenantId: 'tenant-A',
      );

      final tenantBField = createTestField(
        id: 'field-2',
        tenantId: 'tenant-B',
      );

      expect(tenantAField.tenantId, equals('tenant-A'));
      expect(tenantBField.tenantId, equals('tenant-B'));
      expect(tenantAField.tenantId, isNot(equals(tenantBField.tenantId)));
    });

    test('multiple fields can belong to same farm', () {
      const farmId = 'farm-001';
      const tenantId = 'tenant-001';

      final fields = List.generate(
        5,
        (i) => createTestField(
          id: 'field-$i',
          tenantId: tenantId,
          farmId: farmId,
        ),
      );

      for (final field in fields) {
        expect(field.tenantId, equals(tenantId));
        expect(field.farmId, equals(farmId));
      }
    });
  });

  // ============================================================
  // Soft Delete Tests
  // ============================================================
  group('Soft Delete - الحذف اللطيف', () {
    test('isDeleted defaults to false', () {
      final field = createTestField();
      expect(field.isDeleted, isFalse);
    });

    test('can mark field as deleted', () {
      final active = createTestField(isDeleted: false);
      final deleted = active.copyWith(isDeleted: true);

      expect(deleted.isDeleted, isTrue);
    });

    test('filters out deleted fields correctly', () {
      final fields = [
        createTestField(id: '1', isDeleted: false),
        createTestField(id: '2', isDeleted: true),
        createTestField(id: '3', isDeleted: false),
        createTestField(id: '4', isDeleted: true),
        createTestField(id: '5', isDeleted: false),
      ];

      final activeFields = fields.where((f) => !f.isDeleted).toList();
      expect(activeFields.length, equals(3));
      expect(activeFields.map((f) => f.id), containsAll(['1', '3', '5']));
    });
  });
}
