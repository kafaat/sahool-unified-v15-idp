/// Field Controller Tests for SAHOOL Field App
/// اختبارات التحكم بالحقول
///
/// Tests for DrawingProvider (polygon drawing state management)
/// and field domain entity operations
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import 'package:sahool_field_app/features/field/ui/logic/drawing_provider.dart';
import 'package:sahool_field_app/features/field/domain/entities/field.dart';

import 'fixtures/field_fixtures.dart';

void main() {
  group('DrawingState', () {
    test('should create DrawingState with default values', () {
      const state = DrawingState();

      expect(state.isDrawing, false);
      expect(state.points, isEmpty);
      expect(state.fieldName, isNull);
    });

    test('should create DrawingState with custom values', () {
      final points = FieldTestFixtures.simpleRectangleBoundary;
      final state = DrawingState(
        isDrawing: true,
        points: points,
        fieldName: 'Test Field',
      );

      expect(state.isDrawing, true);
      expect(state.points, points);
      expect(state.fieldName, 'Test Field');
    });

    test('copyWith should preserve values when not specified', () {
      final originalState = DrawingState(
        isDrawing: true,
        points: FieldTestFixtures.triangleBoundary,
        fieldName: 'Original',
      );

      final newState = originalState.copyWith();

      expect(newState.isDrawing, originalState.isDrawing);
      expect(newState.points, originalState.points);
      expect(newState.fieldName, originalState.fieldName);
    });

    test('copyWith should update specified values', () {
      const originalState = DrawingState(
        isDrawing: false,
        fieldName: 'Original',
      );

      final newState = originalState.copyWith(
        isDrawing: true,
        fieldName: 'Updated',
      );

      expect(newState.isDrawing, true);
      expect(newState.fieldName, 'Updated');
    });

    group('isValid', () {
      test('should return false for empty points', () {
        const state = DrawingState(points: []);
        expect(state.isValid, false);
      });

      test('should return false for 1 point', () {
        final state = DrawingState(
          points: FieldTestFixtures.singlePointBoundary,
        );
        expect(state.isValid, false);
      });

      test('should return false for 2 points', () {
        final state = DrawingState(
          points: FieldTestFixtures.twoPointsBoundary,
        );
        expect(state.isValid, false);
      });

      test('should return true for 3+ points (valid polygon)', () {
        final state = DrawingState(
          points: FieldTestFixtures.triangleBoundary,
        );
        expect(state.isValid, true);
      });

      test('should return true for complex polygon', () {
        final state = DrawingState(
          points: FieldTestFixtures.largeFieldBoundary,
        );
        expect(state.isValid, true);
      });
    });

    test('pointCount should return correct count', () {
      expect(const DrawingState().pointCount, 0);
      expect(
        DrawingState(points: FieldTestFixtures.triangleBoundary).pointCount,
        3,
      );
      expect(
        DrawingState(points: FieldTestFixtures.largeFieldBoundary).pointCount,
        10,
      );
    });
  });

  group('DrawingNotifier', () {
    late ProviderContainer container;
    late DrawingNotifier notifier;

    setUp(() {
      container = ProviderContainer();
      notifier = container.read(drawingProvider.notifier);
    });

    tearDown(() {
      container.dispose();
    });

    test('initial state should be not drawing with empty points', () {
      final state = container.read(drawingProvider);

      expect(state.isDrawing, false);
      expect(state.points, isEmpty);
      expect(state.fieldName, isNull);
    });

    group('startDrawing', () {
      test('should set isDrawing to true', () {
        notifier.startDrawing();

        final state = container.read(drawingProvider);
        expect(state.isDrawing, true);
      });

      test('should clear existing points', () {
        // Add some points first
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));
        notifier.addPoint(const LatLng(15.1, 44.1));

        // Start new drawing
        notifier.startDrawing();

        final state = container.read(drawingProvider);
        expect(state.points, isEmpty);
      });
    });

    group('addPoint', () {
      test('should not add point when not in drawing mode', () {
        notifier.addPoint(const LatLng(15.0, 44.0));

        final state = container.read(drawingProvider);
        expect(state.points, isEmpty);
      });

      test('should add point when in drawing mode', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));

        final state = container.read(drawingProvider);
        expect(state.points.length, 1);
        expect(state.points.first.latitude, 15.0);
        expect(state.points.first.longitude, 44.0);
      });

      test('should add multiple points in sequence', () {
        notifier.startDrawing();

        for (final point in FieldTestFixtures.triangleBoundary) {
          notifier.addPoint(point);
        }

        final state = container.read(drawingProvider);
        expect(state.points.length, 3);
        expect(state.isValid, true);
      });
    });

    group('undoLastPoint', () {
      test('should do nothing when points are empty', () {
        notifier.undoLastPoint();

        final state = container.read(drawingProvider);
        expect(state.points, isEmpty);
      });

      test('should remove the last point', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));
        notifier.addPoint(const LatLng(15.1, 44.1));
        notifier.addPoint(const LatLng(15.2, 44.2));

        notifier.undoLastPoint();

        final state = container.read(drawingProvider);
        expect(state.points.length, 2);
        expect(state.points.last.latitude, 15.1);
      });

      test('should be able to undo all points', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));
        notifier.addPoint(const LatLng(15.1, 44.1));

        notifier.undoLastPoint();
        notifier.undoLastPoint();

        final state = container.read(drawingProvider);
        expect(state.points, isEmpty);
      });
    });

    group('updatePoint', () {
      test('should do nothing for invalid index (negative)', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));

        notifier.updatePoint(-1, const LatLng(16.0, 45.0));

        final state = container.read(drawingProvider);
        expect(state.points.first.latitude, 15.0);
      });

      test('should do nothing for invalid index (out of bounds)', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));

        notifier.updatePoint(5, const LatLng(16.0, 45.0));

        final state = container.read(drawingProvider);
        expect(state.points.length, 1);
      });

      test('should update point at valid index', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));
        notifier.addPoint(const LatLng(15.1, 44.1));
        notifier.addPoint(const LatLng(15.2, 44.2));

        notifier.updatePoint(1, const LatLng(16.0, 45.0));

        final state = container.read(drawingProvider);
        expect(state.points[1].latitude, 16.0);
        expect(state.points[1].longitude, 45.0);
      });

      test('should preserve other points when updating', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));
        notifier.addPoint(const LatLng(15.1, 44.1));
        notifier.addPoint(const LatLng(15.2, 44.2));

        notifier.updatePoint(1, const LatLng(16.0, 45.0));

        final state = container.read(drawingProvider);
        expect(state.points[0].latitude, 15.0);
        expect(state.points[2].latitude, 15.2);
      });
    });

    group('setFieldName', () {
      test('should set field name', () {
        notifier.setFieldName('Test Field');

        final state = container.read(drawingProvider);
        expect(state.fieldName, 'Test Field');
      });

      test('should update field name', () {
        notifier.setFieldName('First Name');
        notifier.setFieldName('Second Name');

        final state = container.read(drawingProvider);
        expect(state.fieldName, 'Second Name');
      });

      test('should set Arabic field name', () {
        notifier.setFieldName('الحقل الشمالي');

        final state = container.read(drawingProvider);
        expect(state.fieldName, 'الحقل الشمالي');
      });
    });

    group('cancelDrawing', () {
      test('should reset drawing state', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));
        notifier.addPoint(const LatLng(15.1, 44.1));
        notifier.setFieldName('Test Field');

        notifier.cancelDrawing();

        final state = container.read(drawingProvider);
        expect(state.isDrawing, false);
        expect(state.points, isEmpty);
      });
    });

    group('finishDrawing', () {
      test('should return current points', () {
        notifier.startDrawing();
        for (final point in FieldTestFixtures.triangleBoundary) {
          notifier.addPoint(point);
        }

        final points = notifier.finishDrawing();

        expect(points.length, 3);
      });

      test('should reset state after finishing', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));

        notifier.finishDrawing();

        final state = container.read(drawingProvider);
        expect(state.isDrawing, false);
        expect(state.points, isEmpty);
      });

      test('should return empty list if no points', () {
        notifier.startDrawing();

        final points = notifier.finishDrawing();

        expect(points, isEmpty);
      });
    });

    group('clearPoints', () {
      test('should clear all points but keep isDrawing state', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.0, 44.0));
        notifier.addPoint(const LatLng(15.1, 44.1));

        notifier.clearPoints();

        final state = container.read(drawingProvider);
        expect(state.points, isEmpty);
        expect(state.isDrawing, true);
      });
    });
  });

  group('Field Domain Entity', () {
    group('fromJson', () {
      test('should parse field from JSON', () {
        final field = Field.fromJson(FieldTestFixtures.sampleFieldJson);

        expect(field.id, 'field_001');
        expect(field.name, 'الحقل الشمالي');
        expect(field.tenantId, 'tenant_1');
        expect(field.cropType, 'wheat');
        expect(field.areaHectares, 5.5);
        expect(field.ndviCurrent, 0.72);
        expect(field.synced, true);
      });

      test('should parse GeoJSON feature with polygon geometry', () {
        final field = Field.fromJson(FieldTestFixtures.sampleGeoJsonFeature);

        expect(field.id, 'field_001');
        expect(field.hasBoundary, true);
        expect(field.boundary.length, 5); // Closed polygon has 5 points
        expect(field.centroid, isNotNull);
      });

      test('should handle missing optional fields', () {
        final field = Field.fromJson(FieldTestFixtures.fieldWithoutNdviJson);

        expect(field.ndviCurrent, isNull);
        expect(field.cropType, isNull);
        expect(field.ndvi, 0.0); // Default via getter
      });

      test('should set default name for missing name', () {
        final json = Map<String, dynamic>.from(FieldTestFixtures.sampleFieldJson);
        json.remove('name');

        final field = Field.fromJson(json);

        expect(field.name, 'غير محدد');
      });
    });

    group('toJson', () {
      test('should serialize field to GeoJSON Feature', () {
        final boundary = FieldTestFixtures.simpleRectangleBoundary;
        final field = Field(
          id: 'test_001',
          tenantId: 'tenant_1',
          name: 'Test Field',
          boundary: boundary,
          areaHectares: 5.0,
          createdAt: DateTime(2024, 1, 1),
          updatedAt: DateTime(2024, 1, 15),
        );

        final json = field.toJson();

        expect(json['type'], 'Feature');
        expect(json['id'], 'test_001');
        expect(json['geometry'], isNotNull);
        expect(json['geometry']['type'], 'Polygon');
        expect(json['properties']['name'], 'Test Field');
      });

      test('should serialize field without boundary', () {
        final field = Field(
          id: 'test_001',
          tenantId: 'tenant_1',
          name: 'Test Field',
          boundary: const [],
          areaHectares: 0,
          createdAt: DateTime(2024, 1, 1),
          updatedAt: DateTime(2024, 1, 15),
        );

        final json = field.toJson();

        expect(json['geometry'], isNull);
        expect(json['properties']['name'], 'Test Field');
      });
    });

    group('Health Status', () {
      test('should return healthy status for NDVI > 0.6', () {
        final field = Field.fromJson(FieldTestFixtures.sampleGeoJsonFeature);

        expect(field.healthStatus, FieldStatus.healthy);
        expect(field.needsAttention, false);
        expect(field.isCritical, false);
      });

      test('should return stressed status for NDVI 0.4-0.6', () {
        final field = Field.fromJson(FieldTestFixtures.stressedFieldJson);

        expect(field.healthStatus, FieldStatus.stressed);
        expect(field.needsAttention, true);
        expect(field.isCritical, false);
      });

      test('should return critical status for NDVI < 0.4', () {
        final field = Field.fromJson(FieldTestFixtures.criticalFieldJson);

        expect(field.healthStatus, FieldStatus.critical);
        expect(field.needsAttention, true);
        expect(field.isCritical, true);
      });

      test('should return unknown status for null NDVI', () {
        final field = Field.fromJson(FieldTestFixtures.fieldWithoutNdviJson);

        expect(field.healthStatus, FieldStatus.unknown);
        expect(field.ndvi, 0.0);
      });
    });

    group('statusFromNdvi', () {
      test('should return correct status for all ranges', () {
        expect(Field.statusFromNdvi(0.8), FieldStatus.healthy);
        expect(Field.statusFromNdvi(0.6), FieldStatus.healthy);
        expect(Field.statusFromNdvi(0.59), FieldStatus.stressed);
        expect(Field.statusFromNdvi(0.4), FieldStatus.stressed);
        expect(Field.statusFromNdvi(0.39), FieldStatus.critical);
        expect(Field.statusFromNdvi(0.1), FieldStatus.critical);
        expect(Field.statusFromNdvi(0.0), FieldStatus.unknown);
      });
    });

    group('Computed Properties', () {
      test('healthPercentage should return NDVI * 100', () {
        final field = Field(
          id: 'test',
          tenantId: 'tenant_1',
          name: 'Test',
          ndviCurrent: 0.72,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        expect(field.healthPercentage, 72);
      });

      test('hasBoundary should return true when boundary exists', () {
        final field = Field(
          id: 'test',
          tenantId: 'tenant_1',
          name: 'Test',
          boundary: FieldTestFixtures.triangleBoundary,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        expect(field.hasBoundary, true);
        expect(field.boundaryPointCount, 3);
      });

      test('hasBoundary should return false when boundary is empty', () {
        final field = Field(
          id: 'test',
          tenantId: 'tenant_1',
          name: 'Test',
          boundary: const [],
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        expect(field.hasBoundary, false);
        expect(field.boundaryPointCount, 0);
      });

      test('areaHa should be alias for areaHectares', () {
        final field = Field(
          id: 'test',
          tenantId: 'tenant_1',
          name: 'Test',
          areaHectares: 5.5,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        expect(field.areaHa, 5.5);
      });

      test('centerLat and centerLng should return centroid coordinates', () {
        final field = Field(
          id: 'test',
          tenantId: 'tenant_1',
          name: 'Test',
          centroid: const LatLng(15.5, 44.5),
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        expect(field.centerLat, 15.5);
        expect(field.centerLng, 44.5);
      });
    });

    group('copyWith', () {
      test('should create copy with updated values', () {
        final original = Field(
          id: 'test',
          tenantId: 'tenant_1',
          name: 'Original',
          areaHectares: 5.0,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        final copy = original.copyWith(
          name: 'Updated',
          areaHectares: 10.0,
        );

        expect(copy.id, original.id);
        expect(copy.name, 'Updated');
        expect(copy.areaHectares, 10.0);
        expect(copy.tenantId, original.tenantId);
      });

      test('should preserve all values when no arguments', () {
        final original = Field(
          id: 'test',
          tenantId: 'tenant_1',
          name: 'Original',
          cropType: 'wheat',
          ndviCurrent: 0.7,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        final copy = original.copyWith();

        expect(copy.id, original.id);
        expect(copy.name, original.name);
        expect(copy.cropType, original.cropType);
        expect(copy.ndviCurrent, original.ndviCurrent);
      });
    });

    group('Equality', () {
      test('should be equal when IDs match', () {
        final field1 = Field(
          id: 'same_id',
          tenantId: 'tenant_1',
          name: 'Field 1',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        final field2 = Field(
          id: 'same_id',
          tenantId: 'tenant_2',
          name: 'Field 2',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        expect(field1, equals(field2));
        expect(field1.hashCode, equals(field2.hashCode));
      });

      test('should not be equal when IDs differ', () {
        final field1 = Field(
          id: 'id_1',
          tenantId: 'tenant_1',
          name: 'Field 1',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        final field2 = Field(
          id: 'id_2',
          tenantId: 'tenant_1',
          name: 'Field 1',
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        expect(field1, isNot(equals(field2)));
      });
    });

    group('toString', () {
      test('should return readable string representation', () {
        final field = Field(
          id: 'test_001',
          tenantId: 'tenant_1',
          name: 'Test Field',
          areaHectares: 5.5,
          ndviCurrent: 0.72,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        final string = field.toString();

        expect(string, contains('test_001'));
        expect(string, contains('Test Field'));
        expect(string, contains('5.50ha'));
        expect(string, contains('0.72'));
      });
    });
  });
}
