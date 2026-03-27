import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';
import '../../../polygon_editor/utils/geo_utils.dart';

/// حالة الرسم - Drawing State
class DrawingState {
  final bool isDrawing;
  final List<LatLng> points;
  final String? fieldName;

  const DrawingState({
    this.isDrawing = false,
    this.points = const [],
    this.fieldName,
  });

  DrawingState copyWith({
    bool? isDrawing,
    List<LatLng>? points,
    String? fieldName,
  }) {
    return DrawingState(
      isDrawing: isDrawing ?? this.isDrawing,
      points: points ?? this.points,
      fieldName: fieldName ?? this.fieldName,
    );
  }

  /// هل المضلع صالح للحفظ؟ (يجب أن يكون مثلثاً على الأقل)
  bool get isValid => points.length >= 3;

  /// عدد النقاط
  int get pointCount => points.length;
}

/// Drawing Notifier - إدارة حالة الرسم
class DrawingNotifier extends StateNotifier<DrawingState> {
  DrawingNotifier() : super(const DrawingState());

  final List<LatLng> _redoStack = [];

  /// بدء وضع الرسم
  void startDrawing() {
    state = state.copyWith(isDrawing: true, points: []);
  }

  /// إضافة نقطة
  void addPoint(LatLng point) {
    if (!state.isDrawing) return;
    _redoStack.clear();
    state = state.copyWith(points: [...state.points, point]);
  }

  /// تراجع عن آخر نقطة
  void undoLastPoint() {
    if (state.points.isNotEmpty) {
      final removed = state.points.last;
      _redoStack.add(removed);
      state = state.copyWith(
        points: state.points.sublist(0, state.points.length - 1),
      );
    }
  }

  /// إعادة آخر نقطة تم التراجع عنها - Redo last undone point
  void redoPoint() {
    if (_redoStack.isNotEmpty) {
      final point = _redoStack.removeLast();
      state = state.copyWith(
        points: [...state.points, point],
      );
    }
  }

  /// هل يمكن الإعادة؟ - Whether redo is available
  bool get canRedo => _redoStack.isNotEmpty;

  /// حساب المحيط بالأمتار - Calculate perimeter in meters
  double get perimeterMeters {
    if (state.points.length < 2) return 0;
    return GeoUtils.calculatePerimeter(state.points);
  }

  /// تحديث نقطة (للسحب)
  void updatePoint(int index, LatLng newPosition) {
    if (index < 0 || index >= state.points.length) return;
    final newPoints = List<LatLng>.from(state.points);
    newPoints[index] = newPosition;
    state = state.copyWith(points: newPoints);
  }

  /// تعيين اسم الحقل
  void setFieldName(String name) {
    state = state.copyWith(fieldName: name);
  }

  /// إلغاء الرسم
  void cancelDrawing() {
    _redoStack.clear();
    state = const DrawingState(isDrawing: false, points: []);
  }

  /// إنهاء الرسم (للحفظ)
  List<LatLng> finishDrawing() {
    final points = List<LatLng>.from(state.points);
    state = const DrawingState(isDrawing: false, points: []);
    return points;
  }

  /// مسح جميع النقاط
  void clearPoints() {
    _redoStack.clear();
    state = state.copyWith(points: []);
  }
}

/// Provider للرسم
final drawingProvider = StateNotifierProvider<DrawingNotifier, DrawingState>((ref) {
  return DrawingNotifier();
});
