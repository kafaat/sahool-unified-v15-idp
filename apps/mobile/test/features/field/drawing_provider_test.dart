/// Drawing Provider Tests - اختبارات مزود الرسم
///
/// Tests for undo/redo stack, perimeter calculation,
/// and DrawingState management.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_field_app/features/field/ui/logic/drawing_provider.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // DrawingState Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('DrawingState', () {
    test('default state should not be drawing and have no points', () {
      const state = DrawingState();
      expect(state.isDrawing, isFalse);
      expect(state.points, isEmpty);
      expect(state.fieldName, isNull);
      expect(state.isValid, isFalse);
      expect(state.pointCount, equals(0));
    });

    test('isValid should return true when >= 3 points', () {
      const state = DrawingState(
        isDrawing: true,
        points: [
          LatLng(15.37, 44.19),
          LatLng(15.38, 44.19),
          LatLng(15.38, 44.20),
        ],
      );
      expect(state.isValid, isTrue);
      expect(state.pointCount, equals(3));
    });

    test('isValid should return false when < 3 points', () {
      const state = DrawingState(
        isDrawing: true,
        points: [
          LatLng(15.37, 44.19),
          LatLng(15.38, 44.19),
        ],
      );
      expect(state.isValid, isFalse);
    });

    test('copyWith should preserve unchanged fields', () {
      const original = DrawingState(
        isDrawing: true,
        points: [LatLng(15.37, 44.19)],
        fieldName: 'حقل القمح',
      );

      final copied = original.copyWith(fieldName: 'حقل الشعير');
      expect(copied.isDrawing, isTrue);
      expect(copied.points.length, equals(1));
      expect(copied.fieldName, equals('حقل الشعير'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DrawingNotifier Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('DrawingNotifier', () {
    late DrawingNotifier notifier;

    setUp(() {
      notifier = DrawingNotifier();
    });

    group('Basic Operations', () {
      test('startDrawing should set isDrawing to true', () {
        notifier.startDrawing();
        expect(notifier.state.isDrawing, isTrue);
        expect(notifier.state.points, isEmpty);
      });

      test('addPoint should add point when drawing', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        expect(notifier.state.points.length, equals(1));
        expect(notifier.state.points.first.latitude, equals(15.37));
      });

      test('addPoint should NOT add point when not drawing', () {
        notifier.addPoint(const LatLng(15.37, 44.19));
        expect(notifier.state.points, isEmpty);
      });

      test('clearPoints should empty points list', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.addPoint(const LatLng(15.38, 44.19));
        notifier.clearPoints();
        expect(notifier.state.points, isEmpty);
      });

      test('cancelDrawing should reset state', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.cancelDrawing();
        expect(notifier.state.isDrawing, isFalse);
        expect(notifier.state.points, isEmpty);
      });

      test('finishDrawing should return points and reset state', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.addPoint(const LatLng(15.38, 44.19));
        notifier.addPoint(const LatLng(15.38, 44.20));

        final points = notifier.finishDrawing();
        expect(points.length, equals(3));
        expect(notifier.state.isDrawing, isFalse);
        expect(notifier.state.points, isEmpty);
      });
    });

    group('Undo/Redo', () {
      test('undoLastPoint should remove last point and enable redo', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.addPoint(const LatLng(15.38, 44.19));

        expect(notifier.canRedo, isFalse);

        notifier.undoLastPoint();
        expect(notifier.state.points.length, equals(1));
        expect(notifier.state.points.first.latitude, equals(15.37));
        expect(notifier.canRedo, isTrue);
      });

      test('redoPoint should restore undone point', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.addPoint(const LatLng(15.38, 44.19));
        notifier.undoLastPoint();

        notifier.redoPoint();
        expect(notifier.state.points.length, equals(2));
        expect(notifier.state.points.last.latitude, equals(15.38));
        expect(notifier.canRedo, isFalse);
      });

      test('multiple undo/redo should work correctly', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19)); // point 1
        notifier.addPoint(const LatLng(15.38, 44.19)); // point 2
        notifier.addPoint(const LatLng(15.38, 44.20)); // point 3

        // Undo twice
        notifier.undoLastPoint();
        notifier.undoLastPoint();
        expect(notifier.state.points.length, equals(1));

        // Redo twice
        notifier.redoPoint();
        notifier.redoPoint();
        expect(notifier.state.points.length, equals(3));
      });

      test('addPoint should clear redo stack', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.addPoint(const LatLng(15.38, 44.19));

        notifier.undoLastPoint();
        expect(notifier.canRedo, isTrue);

        // Adding a new point should clear redo
        notifier.addPoint(const LatLng(15.39, 44.19));
        expect(notifier.canRedo, isFalse);
      });

      test('clearPoints should clear redo stack', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.undoLastPoint();
        expect(notifier.canRedo, isTrue);

        notifier.clearPoints();
        expect(notifier.canRedo, isFalse);
      });

      test('cancelDrawing should clear redo stack', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.undoLastPoint();
        expect(notifier.canRedo, isTrue);

        notifier.cancelDrawing();
        expect(notifier.canRedo, isFalse);
      });

      test('undo on empty points should do nothing', () {
        notifier.startDrawing();
        notifier.undoLastPoint();
        expect(notifier.state.points, isEmpty);
        expect(notifier.canRedo, isFalse);
      });

      test('redo on empty redo stack should do nothing', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.redoPoint(); // no undo was done
        expect(notifier.state.points.length, equals(1));
      });
    });

    group('Perimeter Calculation', () {
      test('perimeterMeters should be 0 with less than 2 points', () {
        notifier.startDrawing();
        expect(notifier.perimeterMeters, equals(0));

        notifier.addPoint(const LatLng(15.37, 44.19));
        expect(notifier.perimeterMeters, equals(0));
      });

      test('perimeterMeters should return positive value for valid polygon', () {
        notifier.startDrawing();
        // Create a ~1km square-ish polygon near Sanaa
        notifier.addPoint(const LatLng(15.3700, 44.1900));
        notifier.addPoint(const LatLng(15.3700, 44.2000));
        notifier.addPoint(const LatLng(15.3800, 44.2000));
        notifier.addPoint(const LatLng(15.3800, 44.1900));

        final perimeter = notifier.perimeterMeters;
        expect(perimeter, greaterThan(0));
        // Each side is roughly 1km, so perimeter ~4km
        expect(perimeter, greaterThan(2000)); // at least 2km
        expect(perimeter, lessThan(10000)); // less than 10km
      });

      test('perimeterMeters should increase when points are added', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.addPoint(const LatLng(15.38, 44.19));

        final perimeter2 = notifier.perimeterMeters;
        expect(perimeter2, greaterThan(0));

        notifier.addPoint(const LatLng(15.38, 44.20));
        final perimeter3 = notifier.perimeterMeters;
        expect(perimeter3, greaterThan(perimeter2));
      });
    });

    group('Point Update', () {
      test('updatePoint should modify point at index', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));
        notifier.addPoint(const LatLng(15.38, 44.19));

        notifier.updatePoint(0, const LatLng(15.39, 44.19));
        expect(notifier.state.points[0].latitude, equals(15.39));
        expect(notifier.state.points[1].latitude, equals(15.38));
      });

      test('updatePoint should ignore invalid indices', () {
        notifier.startDrawing();
        notifier.addPoint(const LatLng(15.37, 44.19));

        notifier.updatePoint(-1, const LatLng(15.39, 44.19));
        notifier.updatePoint(5, const LatLng(15.39, 44.19));
        expect(notifier.state.points[0].latitude, equals(15.37));
      });
    });
  });
}
