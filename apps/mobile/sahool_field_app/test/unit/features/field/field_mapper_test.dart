import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_field_app/features/field/domain/entities/field.dart' as domain;
import 'package:sahool_field_app/features/field/domain/mappers/field_mapper.dart';
import 'package:sahool_field_app/features/fields/domain/entities/field_entity.dart';

void main() {
  final now = DateTime(2026, 3, 1);

  domain.Field _createDomainField({
    String id = 'f1',
    String tenantId = 't1',
    String name = 'Test Field',
    String? cropType = 'wheat',
    double? ndviCurrent = 0.72,
    List<LatLng> boundary = const [],
    LatLng? centroid,
    String? status,
  }) {
    return domain.Field(
      id: id,
      tenantId: tenantId,
      name: name,
      cropType: cropType,
      boundary: boundary,
      centroid: centroid,
      areaHectares: 5.0,
      ndviCurrent: ndviCurrent,
      status: status,
      createdAt: now,
      updatedAt: now,
    );
  }

  group('FieldMapper.toFieldEntity', () {
    test('converts basic domain field to FieldEntity', () {
      final field = _createDomainField();
      final entity = FieldMapper.toFieldEntity(field);

      expect(entity.id, 'f1');
      expect(entity.tenantId, 't1');
      expect(entity.name, 'Test Field');
      expect(entity.cropType, 'wheat');
      expect(entity.areaHectares, 5.0);
      expect(entity.healthScore, 0.72); // NDVI as health score
      expect(entity.ndviValue, 0.72);
    });

    test('maps boundary from LatLng to GeoLocation', () {
      final field = _createDomainField(
        boundary: [
          const LatLng(15.0, 44.0),
          const LatLng(15.1, 44.1),
          const LatLng(15.0, 44.2),
        ],
      );

      final entity = FieldMapper.toFieldEntity(field);
      expect(entity.boundary, isNotNull);
      expect(entity.boundary!, hasLength(3));
      expect(entity.boundary![0].latitude, 15.0);
      expect(entity.boundary![0].longitude, 44.0);
    });

    test('maps centroid to GeoLocation center', () {
      final field = _createDomainField(
        centroid: const LatLng(15.5, 44.5),
      );

      final entity = FieldMapper.toFieldEntity(field);
      expect(entity.center, isNotNull);
      expect(entity.center!.latitude, 15.5);
      expect(entity.center!.longitude, 44.5);
    });

    test('maps healthy status to active', () {
      final field = _createDomainField(ndviCurrent: 0.72);
      final entity = FieldMapper.toFieldEntity(field);
      expect(entity.status, FieldStatus.active);
    });

    test('maps stressed status to active', () {
      final field = _createDomainField(ndviCurrent: 0.5);
      final entity = FieldMapper.toFieldEntity(field);
      expect(entity.status, FieldStatus.active);
    });

    test('maps critical status to active', () {
      final field = _createDomainField(ndviCurrent: 0.2);
      final entity = FieldMapper.toFieldEntity(field);
      expect(entity.status, FieldStatus.active);
    });

    test('maps unknown status using field.status string', () {
      final field = _createDomainField(ndviCurrent: null, status: 'fallow');
      final entity = FieldMapper.toFieldEntity(field);
      expect(entity.status, FieldStatus.fallow);
    });

    test('uses غير محدد for null cropType', () {
      final field = _createDomainField(cropType: null);
      final entity = FieldMapper.toFieldEntity(field);
      expect(entity.cropType, 'غير محدد');
    });

    test('boundary is null when domain field has no boundary', () {
      final field = _createDomainField(boundary: []);
      final entity = FieldMapper.toFieldEntity(field);
      expect(entity.boundary, isNull);
    });

    test('center is null when domain field has no centroid', () {
      final field = _createDomainField(centroid: null);
      final entity = FieldMapper.toFieldEntity(field);
      expect(entity.center, isNull);
    });
  });

  group('FieldMapper.fromFieldEntity', () {
    test('converts FieldEntity to domain Field', () {
      final entity = FieldEntity(
        id: 'f1',
        tenantId: 't1',
        name: 'UI Field',
        areaHectares: 3.5,
        cropType: 'tomato',
        healthScore: 0.8,
        ndviValue: 0.75,
        status: FieldStatus.active,
        center: const GeoLocation(latitude: 15.0, longitude: 44.0),
        boundary: [
          const GeoLocation(latitude: 15.0, longitude: 44.0),
          const GeoLocation(latitude: 15.1, longitude: 44.1),
          const GeoLocation(latitude: 15.0, longitude: 44.2),
        ],
        createdAt: now,
        updatedAt: now,
      );

      final field = FieldMapper.fromFieldEntity(entity);

      expect(field.id, 'f1');
      expect(field.tenantId, 't1');
      expect(field.name, 'UI Field');
      expect(field.cropType, 'tomato');
      expect(field.areaHectares, 3.5);
      expect(field.ndviCurrent, 0.75);
      expect(field.boundary, hasLength(3));
      expect(field.boundary[0].latitude, 15.0);
      expect(field.centroid!.latitude, 15.0);
      expect(field.synced, false);
      expect(field.isDeleted, false);
      expect(field.status, 'active');
    });

    test('handles null boundary and center', () {
      final entity = FieldEntity(
        id: 'f2',
        tenantId: 't1',
        name: 'No Geo',
        areaHectares: 1.0,
        cropType: 'wheat',
        createdAt: now,
        updatedAt: now,
      );

      final field = FieldMapper.fromFieldEntity(entity);
      expect(field.boundary, isEmpty);
      expect(field.centroid, isNull);
    });
  });

  group('FieldMapper batch conversions', () {
    test('toFieldEntities converts list', () {
      final fields = [
        _createDomainField(id: 'f1', name: 'Field 1'),
        _createDomainField(id: 'f2', name: 'Field 2'),
      ];

      final entities = FieldMapper.toFieldEntities(fields);
      expect(entities, hasLength(2));
      expect(entities[0].id, 'f1');
      expect(entities[1].id, 'f2');
    });

    test('fromFieldEntities converts list', () {
      final entities = [
        FieldEntity(id: 'e1', tenantId: 't1', name: 'E1', areaHectares: 1, cropType: 'wheat', createdAt: now, updatedAt: now),
        FieldEntity(id: 'e2', tenantId: 't1', name: 'E2', areaHectares: 2, cropType: 'corn', createdAt: now, updatedAt: now),
      ];

      final fields = FieldMapper.fromFieldEntities(entities);
      expect(fields, hasLength(2));
      expect(fields[0].id, 'e1');
      expect(fields[1].id, 'e2');
    });
  });

  group('Extension methods', () {
    test('DomainFieldExtension.toFieldEntity works', () {
      final field = _createDomainField(name: 'Ext Test');
      final entity = field.toFieldEntity();
      expect(entity.name, 'Ext Test');
    });

    test('FieldEntityExtension.toDomainField works', () {
      final entity = FieldEntity(
        id: 'ext1', tenantId: 't1', name: 'Ext Entity',
        areaHectares: 1, cropType: 'wheat', createdAt: now, updatedAt: now,
      );
      final field = entity.toDomainField();
      expect(field.name, 'Ext Entity');
    });

    test('DomainFieldListExtension.toFieldEntities works', () {
      final fields = [_createDomainField(id: 'l1'), _createDomainField(id: 'l2')];
      final entities = fields.toFieldEntities();
      expect(entities, hasLength(2));
    });

    test('FieldEntityListExtension.toDomainFields works', () {
      final entities = [
        FieldEntity(id: 'le1', tenantId: 't1', name: 'LE1', areaHectares: 1, cropType: 'a', createdAt: now, updatedAt: now),
      ];
      final fields = entities.toDomainFields();
      expect(fields, hasLength(1));
    });
  });
}
