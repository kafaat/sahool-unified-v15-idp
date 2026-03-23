import 'package:flutter/foundation.dart';
import 'package:latlong2/latlong.dart';

/// حالة محرر المضلعات مع دعم Undo/Redo
/// Enterprise Polygon Editor State with full Undo/Redo support
class PolygonEditorState extends ChangeNotifier {
  List<LatLng> _points = [];
  final List<List<LatLng>> _undoStack = [];
  final List<List<LatLng>> _redoStack = [];

  int? _selectedPointIndex;
  bool _isDrawing = false;
  bool _isClosed = false;

  // ─────────────────────────────────────────────────────────────────
  // Getters
  // ─────────────────────────────────────────────────────────────────

  List<LatLng> get points => List.unmodifiable(_points);
  int? get selectedPointIndex => _selectedPointIndex;
  bool get isDrawing => _isDrawing;
  bool get isClosed => _isClosed;
  bool get canUndo => _undoStack.isNotEmpty;
  bool get canRedo => _redoStack.isNotEmpty;
  bool get hasPoints => _points.isNotEmpty;
  bool get canClose => _points.length >= 3;
  int get pointCount => _points.length;

  // ─────────────────────────────────────────────────────────────────
  // History Management (Undo/Redo)
  // ─────────────────────────────────────────────────────────────────

  /// حفظ الحالة الحالية قبل التعديل
  void _saveSnapshot() {
    _undoStack.add(List.from(_points));
    _redoStack.clear(); // Clear redo stack on new action

    // Limit history size to 50 entries
    if (_undoStack.length > 50) {
      _undoStack.removeAt(0);
    }
  }

  /// تراجع - Undo
  void undo() {
    if (!canUndo) return;

    _redoStack.add(List.from(_points));
    _points = _undoStack.removeLast();
    _selectedPointIndex = null;
    _updateClosedState();
    notifyListeners();
  }

  /// إعادة - Redo
  void redo() {
    if (!canRedo) return;

    _undoStack.add(List.from(_points));
    _points = _redoStack.removeLast();
    _selectedPointIndex = null;
    _updateClosedState();
    notifyListeners();
  }

  // ─────────────────────────────────────────────────────────────────
  // Point Operations
  // ─────────────────────────────────────────────────────────────────

  /// بدء الرسم
  void startDrawing() {
    _isDrawing = true;
    _isClosed = false;
    notifyListeners();
  }

  /// إيقاف الرسم
  void stopDrawing() {
    _isDrawing = false;
    notifyListeners();
  }

  /// إضافة نقطة جديدة
  void addPoint(LatLng point) {
    _saveSnapshot();
    _points.add(point);
    _selectedPointIndex = _points.length - 1;
    notifyListeners();
  }

  /// إضافة نقطة في موقع محدد (لإدراج بين نقطتين)
  void insertPoint(int index, LatLng point) {
    if (index < 0 || index > _points.length) return;

    _saveSnapshot();
    _points.insert(index, point);
    _selectedPointIndex = index;
    notifyListeners();
  }

  /// تحديث موقع نقطة (للسحب)
  void updatePoint(int index, LatLng newPosition) {
    if (index < 0 || index >= _points.length) return;

    // Save snapshot only on first move (not during continuous drag)
    if (_selectedPointIndex != index) {
      _saveSnapshot();
    }

    _points[index] = newPosition;
    _selectedPointIndex = index;
    notifyListeners();
  }

  /// بدء سحب نقطة (يحفظ snapshot)
  void startDragPoint(int index) {
    if (index < 0 || index >= _points.length) return;
    _saveSnapshot();
    _selectedPointIndex = index;
    notifyListeners();
  }

  /// تحريك نقطة أثناء السحب (بدون snapshot)
  void dragPoint(int index, LatLng newPosition) {
    if (index < 0 || index >= _points.length) return;
    _points[index] = newPosition;
    notifyListeners();
  }

  /// إنهاء سحب نقطة
  void endDragPoint() {
    // Snapshot was already saved in startDragPoint
    notifyListeners();
  }

  /// حذف نقطة
  void removePoint(int index) {
    if (index < 0 || index >= _points.length) return;

    _saveSnapshot();
    _points.removeAt(index);
    _selectedPointIndex = null;
    _updateClosedState();
    notifyListeners();
  }

  /// حذف النقطة المحددة
  void removeSelectedPoint() {
    if (_selectedPointIndex != null) {
      removePoint(_selectedPointIndex!);
    }
  }

  /// تحديد نقطة
  void selectPoint(int? index) {
    _selectedPointIndex = index;
    notifyListeners();
  }

  /// إلغاء التحديد
  void clearSelection() {
    _selectedPointIndex = null;
    notifyListeners();
  }

  // ─────────────────────────────────────────────────────────────────
  // Polygon Operations
  // ─────────────────────────────────────────────────────────────────

  /// إغلاق المضلع
  void closePolygon() {
    if (!canClose) return;
    _isClosed = true;
    _isDrawing = false;
    notifyListeners();
  }

  /// فتح المضلع للتعديل
  void openPolygon() {
    _isClosed = false;
    notifyListeners();
  }

  /// مسح كل النقاط
  void clear() {
    if (_points.isEmpty) return;

    _saveSnapshot();
    _points.clear();
    _selectedPointIndex = null;
    _isClosed = false;
    notifyListeners();
  }

  /// تحميل مضلع موجود
  void loadPolygon(List<LatLng> polygon, {bool closed = true}) {
    _saveSnapshot();
    _points = List.from(polygon);
    _isClosed = closed && polygon.length >= 3;
    _selectedPointIndex = null;
    _isDrawing = false;
    notifyListeners();
  }

  /// تحديث حالة الإغلاق
  void _updateClosedState() {
    if (_points.length < 3) {
      _isClosed = false;
    }
  }

  // ─────────────────────────────────────────────────────────────────
  // Export
  // ─────────────────────────────────────────────────────────────────

  /// تصدير المضلع كـ GeoJSON
  Map<String, dynamic> toGeoJson() {
    if (_points.isEmpty) {
      return {'type': 'Polygon', 'coordinates': []};
    }

    // Ensure polygon is closed for GeoJSON
    final coords = _points.map((p) => [p.longitude, p.latitude]).toList();
    if (_isClosed && coords.isNotEmpty) {
      // Add first point at end to close the ring
      coords.add([_points.first.longitude, _points.first.latitude]);
    }

    return {
      'type': 'Polygon',
      'coordinates': [coords],
    };
  }

  /// تصدير كـ WKT للـ PostGIS
  String toWkt() {
    if (_points.isEmpty) return 'POLYGON EMPTY';

    final coordsStr = _points.map((p) => '${p.longitude} ${p.latitude}').toList();

    // Close the ring
    if (_isClosed && _points.isNotEmpty) {
      coordsStr.add('${_points.first.longitude} ${_points.first.latitude}');
    }

    return 'POLYGON((${coordsStr.join(', ')}))';
  }
}
