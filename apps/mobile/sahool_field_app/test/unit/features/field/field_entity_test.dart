import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/field/domain/entities/field.dart';

void main() {
  group('FieldStatus enum', () {
    test('statusFromNdvi returns healthy for NDVI >= 0.6', () {
      expect(Field.statusFromNdvi(0.6), FieldStatus.healthy);
      expect(Field.statusFromNdvi(0.8), FieldStatus.healthy);
      expect(Field.statusFromNdvi(1.0), FieldStatus.healthy);
    });

    test('statusFromNdvi returns stressed for NDVI 0.4-0.6', () {
      expect(Field.statusFromNdvi(0.4), FieldStatus.stressed);
      expect(Field.statusFromNdvi(0.5), FieldStatus.stressed);
      expect(Field.statusFromNdvi(0.59), FieldStatus.stressed);
    });

    test('statusFromNdvi returns critical for NDVI > 0 and < 0.4', () {
      expect(Field.statusFromNdvi(0.1), FieldStatus.critical);
      expect(Field.statusFromNdvi(0.2), FieldStatus.critical);
      expect(Field.statusFromNdvi(0.39), FieldStatus.critical);
    });

    test('statusFromNdvi returns unknown for NDVI == 0', () {
      expect(Field.statusFromNdvi(0.0), FieldStatus.unknown);
    });
  });

  group('Field entity', () {
    late Field field;
    final now = DateTime(2026, 1, 15);

    setUp(() {
      field = Field(
        id: 'field-001',
        tenantId: 'tenant-001',
        name: 'حقل القمح',
        cropType: 'wheat',
        areaHectares: 5.5,
        ndviCurrent: 0.72,
        ndviUpdatedAt: now,
        createdAt: now,
        updatedAt: now,
        pendingTasks: 3,
      );
    });

    test('computed ndvi returns ndviCurrent when present', () {
      expect(field.ndvi, 0.72);
    });

    test('computed ndvi returns 0.0 when ndviCurrent is null', () {
      final f = field.copyWith(ndviCurrent: null);
      // ndviCurrent is null but copyWith doesn't support setting to null
      // Create a new field with no ndviCurrent
      final noNdvi = Field(
        id: 'f1',
        tenantId: 't1',
        name: 'test',
        createdAt: now,
        updatedAt: now,
      );
      expect(noNdvi.ndvi, 0.0);
    });

    test('healthStatus is healthy for NDVI 0.72', () {
      expect(field.healthStatus, FieldStatus.healthy);
    });

    test('needsAttention is false for healthy field', () {
      expect(field.needsAttention, false);
    });

    test('needsAttention is true for stressed field', () {
      final stressed = field.copyWith(ndviCurrent: 0.45);
      expect(stressed.needsAttention, true);
    });

    test('needsAttention is true for critical field', () {
      final critical = field.copyWith(ndviCurrent: 0.15);
      expect(critical.needsAttention, true);
    });

    test('isCritical is true only for critical fields', () {
      expect(field.isCritical, false);
      final critical = field.copyWith(ndviCurrent: 0.15);
      expect(critical.isCritical, true);
    });

    test('healthPercentage rounds NDVI to percentage', () {
      expect(field.healthPercentage, 72);
      final half = field.copyWith(ndviCurrent: 0.555);
      expect(half.healthPercentage, 56);
    });

    test('hasBoundary returns false when no boundary', () {
      expect(field.hasBoundary, false);
      expect(field.boundaryPointCount, 0);
    });

    test('areaHa returns areaHectares', () {
      expect(field.areaHa, 5.5);
    });

    test('centerLat/centerLng return null when no centroid', () {
      expect(field.centerLat, null);
      expect(field.centerLng, null);
    });

    test('equality is based on id', () {
      final same = field.copyWith(name: 'Different Name');
      expect(field, same);
    });

    test('different id means not equal', () {
      final different = field.copyWith(id: 'field-002');
      expect(field, isNot(different));
    });

    test('hashCode is based on id', () {
      expect(field.hashCode, 'field-001'.hashCode);
    });

    test('toString contains id, name, area, and NDVI', () {
      final str = field.toString();
      expect(str, contains('field-001'));
      expect(str, contains('حقل القمح'));
      expect(str, contains('5.50'));
      expect(str, contains('0.72'));
    });
  });

  group('Field.fromJson', () {
    test('parses GeoJSON Feature with geometry', () {
      final json = {
        'id': 'field-100',
        'geometry': {
          'type': 'Polygon',
          'coordinates': [
            [
              [46.7, 24.7],
              [46.8, 24.7],
              [46.8, 24.8],
              [46.7, 24.8],
            ]
          ],
        },
        'properties': {
          'tenant_id': 'tenant-1',
          'name': 'Test Field',
          'crop_type': 'barley',
          'area_hectares': 10.0,
          'ndvi_current': 0.65,
          'synced': true,
          'is_deleted': false,
          'pending_tasks': 2,
        },
      };

      final field = Field.fromJson(json);

      expect(field.id, 'field-100');
      expect(field.tenantId, 'tenant-1');
      expect(field.name, 'Test Field');
      expect(field.cropType, 'barley');
      expect(field.areaHectares, 10.0);
      expect(field.ndviCurrent, 0.65);
      expect(field.synced, true);
      expect(field.isDeleted, false);
      expect(field.pendingTasks, 2);
      expect(field.boundary.length, 4);
      expect(field.centroid, isNotNull);
      // GeoJSON [lng, lat] -> LatLng(lat, lng)
      expect(field.boundary[0].latitude, 24.7);
      expect(field.boundary[0].longitude, 46.7);
    });

    test('parses flat JSON without geometry', () {
      final json = {
        'id': 'field-200',
        'tenant_id': 'tenant-2',
        'name': 'Flat Field',
      };

      final field = Field.fromJson(json);
      expect(field.id, 'field-200');
      expect(field.name, 'Flat Field');
      expect(field.boundary, isEmpty);
      expect(field.centroid, isNull);
    });

    test('uses default name when name is missing', () {
      final json = {'id': 'f1', 'tenant_id': 't1'};
      final field = Field.fromJson(json);
      expect(field.name, 'غير محدد');
    });
  });

  group('Field.toJson', () {
    test('produces GeoJSON Feature format', () {
      final now = DateTime(2026, 3, 1);
      final field = Field(
        id: 'f1',
        tenantId: 't1',
        name: 'Test',
        areaHectares: 2.0,
        ndviCurrent: 0.5,
        createdAt: now,
        updatedAt: now,
      );

      final json = field.toJson();
      expect(json['type'], 'Feature');
      expect(json['id'], 'f1');
      expect(json['geometry'], isNull); // no boundary
      expect(json['properties']['name'], 'Test');
      expect(json['properties']['area_hectares'], 2.0);
      expect(json['properties']['ndvi_current'], 0.5);
    });
  });

  group('Field.copyWith', () {
    test('creates a copy with updated fields', () {
      final now = DateTime(2026, 1, 1);
      final field = Field(
        id: 'f1',
        tenantId: 't1',
        name: 'Original',
        createdAt: now,
        updatedAt: now,
      );

      final copy = field.copyWith(name: 'Updated', ndviCurrent: 0.8);
      expect(copy.name, 'Updated');
      expect(copy.ndviCurrent, 0.8);
      expect(copy.id, 'f1'); // unchanged
      expect(copy.tenantId, 't1'); // unchanged
    });
  });
}
