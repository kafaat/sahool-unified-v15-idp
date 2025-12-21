/// SAHOOL Polygon Editor - Enterprise GIS Drawing Tools
///
/// محرر المضلعات الاحترافي لرسم حدود الحقول
///
/// Features:
/// - Undo/Redo with history stack
/// - Drag vertices with project/unproject (zoom-stable)
/// - Snap to vertex / edge
/// - Real-time area calculation (hectares, feddan)
/// - GeoJSON / WKT export
/// - Arabic UI labels

library polygon_editor;

export 'domain/polygon_editor_state.dart';
export 'ui/polygon_editor_widget.dart';
export 'utils/geo_utils.dart';
