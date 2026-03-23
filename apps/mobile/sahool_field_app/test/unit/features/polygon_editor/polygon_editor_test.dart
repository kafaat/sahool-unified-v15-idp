import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_field_app/features/polygon_editor/domain/polygon_editor_state.dart';

void main() {
  late PolygonEditorState editor;

  setUp(() {
    editor = PolygonEditorState();
  });

  group('Initial state', () {
    test('starts with no points', () {
      expect(editor.points, isEmpty);
      expect(editor.hasPoints, false);
      expect(editor.pointCount, 0);
    });

    test('starts not drawing', () {
      expect(editor.isDrawing, false);
      expect(editor.isClosed, false);
    });

    test('cannot undo or redo initially', () {
      expect(editor.canUndo, false);
      expect(editor.canRedo, false);
    });

    test('cannot close with fewer than 3 points', () {
      expect(editor.canClose, false);
    });
  });

  group('Point operations', () {
    test('addPoint adds and selects the point', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      expect(editor.pointCount, 1);
      expect(editor.selectedPointIndex, 0);
      expect(editor.hasPoints, true);
    });

    test('addPoint multiple points', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));
      editor.addPoint(const LatLng(15.0, 44.2));
      expect(editor.pointCount, 3);
      expect(editor.selectedPointIndex, 2);
      expect(editor.canClose, true);
    });

    test('insertPoint inserts at specific index', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.2, 44.2));
      editor.insertPoint(1, const LatLng(15.1, 44.1));

      expect(editor.pointCount, 3);
      expect(editor.points[1].latitude, 15.1);
      expect(editor.selectedPointIndex, 1);
    });

    test('insertPoint ignores invalid index', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.insertPoint(-1, const LatLng(15.1, 44.1));
      expect(editor.pointCount, 1);

      editor.insertPoint(5, const LatLng(15.1, 44.1));
      expect(editor.pointCount, 1);
    });

    test('removePoint removes and clears selection', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));
      editor.removePoint(0);

      expect(editor.pointCount, 1);
      expect(editor.selectedPointIndex, isNull);
    });

    test('removePoint ignores invalid index', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.removePoint(5);
      expect(editor.pointCount, 1);
    });

    test('updatePoint changes point position', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.updatePoint(0, const LatLng(15.5, 44.5));

      expect(editor.points[0].latitude, 15.5);
      expect(editor.points[0].longitude, 44.5);
    });

    test('selectPoint and clearSelection work', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));

      editor.selectPoint(0);
      expect(editor.selectedPointIndex, 0);

      editor.clearSelection();
      expect(editor.selectedPointIndex, isNull);
    });
  });

  group('Drawing state', () {
    test('startDrawing enables drawing mode', () {
      editor.startDrawing();
      expect(editor.isDrawing, true);
      expect(editor.isClosed, false);
    });

    test('stopDrawing disables drawing mode', () {
      editor.startDrawing();
      editor.stopDrawing();
      expect(editor.isDrawing, false);
    });
  });

  group('Polygon operations', () {
    test('closePolygon requires at least 3 points', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));
      editor.closePolygon();
      expect(editor.isClosed, false);

      editor.addPoint(const LatLng(15.0, 44.2));
      editor.closePolygon();
      expect(editor.isClosed, true);
      expect(editor.isDrawing, false);
    });

    test('openPolygon reopens a closed polygon', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));
      editor.addPoint(const LatLng(15.0, 44.2));
      editor.closePolygon();
      expect(editor.isClosed, true);

      editor.openPolygon();
      expect(editor.isClosed, false);
    });

    test('clear removes all points', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));
      editor.clear();

      expect(editor.pointCount, 0);
      expect(editor.isClosed, false);
      expect(editor.selectedPointIndex, isNull);
    });

    test('clear on empty does nothing', () {
      editor.clear(); // should not throw
      expect(editor.pointCount, 0);
    });

    test('loadPolygon replaces current points', () {
      editor.addPoint(const LatLng(15.0, 44.0));

      editor.loadPolygon([
        const LatLng(16.0, 45.0),
        const LatLng(16.1, 45.1),
        const LatLng(16.0, 45.2),
      ]);

      expect(editor.pointCount, 3);
      expect(editor.points[0].latitude, 16.0);
      expect(editor.isClosed, true);
      expect(editor.isDrawing, false);
    });

    test('loadPolygon with closed=false', () {
      editor.loadPolygon(
        [const LatLng(16.0, 45.0), const LatLng(16.1, 45.1), const LatLng(16.0, 45.2)],
        closed: false,
      );
      expect(editor.isClosed, false);
    });

    test('removing points below 3 auto-opens polygon', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));
      editor.addPoint(const LatLng(15.0, 44.2));
      editor.closePolygon();
      expect(editor.isClosed, true);

      editor.removePoint(0);
      expect(editor.isClosed, false); // less than 3 points
    });
  });

  group('Undo/Redo', () {
    test('undo restores previous state', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));

      expect(editor.canUndo, true);
      editor.undo();
      expect(editor.pointCount, 1);
    });

    test('redo restores undone state', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));

      editor.undo();
      expect(editor.canRedo, true);

      editor.redo();
      expect(editor.pointCount, 2);
    });

    test('new action clears redo stack', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));

      editor.undo();
      expect(editor.canRedo, true);

      editor.addPoint(const LatLng(15.2, 44.2));
      expect(editor.canRedo, false);
    });

    test('multiple undo/redo cycles', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));
      editor.addPoint(const LatLng(15.2, 44.2));

      editor.undo();
      editor.undo();
      expect(editor.pointCount, 1);

      editor.redo();
      expect(editor.pointCount, 2);
    });

    test('undo on empty does nothing', () {
      editor.undo();
      expect(editor.pointCount, 0);
    });

    test('redo on empty does nothing', () {
      editor.redo();
      expect(editor.pointCount, 0);
    });
  });

  group('GeoJSON export', () {
    test('empty polygon produces empty coordinates', () {
      final geojson = editor.toGeoJson();
      expect(geojson['type'], 'Polygon');
      expect(geojson['coordinates'], isEmpty);
    });

    test('closed polygon produces GeoJSON with closed ring', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));
      editor.addPoint(const LatLng(15.0, 44.2));
      editor.closePolygon();

      final geojson = editor.toGeoJson();
      expect(geojson['type'], 'Polygon');

      final coords = (geojson['coordinates'] as List)[0] as List;
      expect(coords, hasLength(4)); // 3 points + closing point

      // GeoJSON is [lng, lat]
      expect(coords[0][0], 44.0); // longitude
      expect(coords[0][1], 15.0); // latitude

      // Last point should equal first (closed ring)
      expect(coords.last[0], coords.first[0]);
      expect(coords.last[1], coords.first[1]);
    });
  });

  group('WKT export', () {
    test('empty polygon returns POLYGON EMPTY', () {
      expect(editor.toWkt(), 'POLYGON EMPTY');
    });

    test('closed polygon produces valid WKT', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));
      editor.addPoint(const LatLng(15.0, 44.2));
      editor.closePolygon();

      final wkt = editor.toWkt();
      expect(wkt, startsWith('POLYGON(('));
      expect(wkt, endsWith('))'));
      // Should contain 4 coordinate pairs (3 + closing)
      expect(wkt.split(','), hasLength(4));
    });
  });

  group('Drag operations', () {
    test('startDragPoint saves snapshot', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.startDragPoint(0);
      expect(editor.selectedPointIndex, 0);
      expect(editor.canUndo, true);
    });

    test('dragPoint moves point without saving snapshot', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.startDragPoint(0);
      editor.dragPoint(0, const LatLng(15.5, 44.5));

      expect(editor.points[0].latitude, 15.5);
      // Should still only have 1 undo entry (from startDrag)
    });

    test('removeSelectedPoint removes currently selected', () {
      editor.addPoint(const LatLng(15.0, 44.0));
      editor.addPoint(const LatLng(15.1, 44.1));
      editor.selectPoint(0);
      editor.removeSelectedPoint();

      expect(editor.pointCount, 1);
      expect(editor.points[0].latitude, 15.1);
    });
  });
}
