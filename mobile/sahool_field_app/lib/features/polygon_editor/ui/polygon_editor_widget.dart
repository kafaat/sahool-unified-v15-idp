import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../domain/polygon_editor_state.dart';
import '../utils/geo_utils.dart';
import '../../../core/theme/sahool_theme.dart';

/// محرر المضلعات الاحترافي
/// Enterprise Polygon Editor with:
/// - Undo/Redo support
/// - Drag vertices with project/unproject
/// - Snap to vertex
/// - Real-time area calculation
/// - Arabic/English labels
class PolygonEditorWidget extends StatefulWidget {
  final MapController mapController;
  final PolygonEditorState editorState;
  final Color polygonColor;
  final Color vertexColor;
  final Color selectedVertexColor;
  final double vertexRadius;
  final bool showLabels;
  final bool enableSnap;
  final double snapThresholdMeters;
  final void Function(List<LatLng> polygon)? onPolygonChanged;

  const PolygonEditorWidget({
    super.key,
    required this.mapController,
    required this.editorState,
    this.polygonColor = const Color(0xFF4CAF50),
    this.vertexColor = Colors.white,
    this.selectedVertexColor = const Color(0xFF2196F3),
    this.vertexRadius = 12,
    this.showLabels = true,
    this.enableSnap = true,
    this.snapThresholdMeters = 15,
    this.onPolygonChanged,
  });

  @override
  State<PolygonEditorWidget> createState() => _PolygonEditorWidgetState();
}

class _PolygonEditorWidgetState extends State<PolygonEditorWidget> {
  int? _draggingIndex;
  Offset? _dragStartOffset;

  @override
  void initState() {
    super.initState();
    widget.editorState.addListener(_onStateChanged);
  }

  @override
  void dispose() {
    widget.editorState.removeListener(_onStateChanged);
    super.dispose();
  }

  void _onStateChanged() {
    setState(() {});
    widget.onPolygonChanged?.call(widget.editorState.points);
  }

  @override
  Widget build(BuildContext context) {
    final points = widget.editorState.points;

    return Stack(
      children: [
        // Polygon fill (if closed)
        if (widget.editorState.isClosed && points.length >= 3)
          PolygonLayer(
            polygons: [
              Polygon(
                points: points,
                color: widget.polygonColor.withOpacity(0.3),
                borderColor: widget.polygonColor,
                borderStrokeWidth: 3,
                isFilled: true,
              ),
            ],
          ),

        // Polyline (if not closed)
        if (!widget.editorState.isClosed && points.length >= 2)
          PolylineLayer(
            polylines: [
              Polyline(
                points: points,
                color: widget.polygonColor,
                strokeWidth: 3,
              ),
            ],
          ),

        // Vertex markers
        MarkerLayer(
          markers: _buildVertexMarkers(),
        ),

        // Edge midpoint markers (for inserting new points)
        if (points.length >= 2)
          MarkerLayer(
            markers: _buildMidpointMarkers(),
          ),
      ],
    );
  }

  /// بناء علامات الرؤوس
  List<Marker> _buildVertexMarkers() {
    final points = widget.editorState.points;
    final selectedIndex = widget.editorState.selectedPointIndex;

    return List.generate(points.length, (index) {
      final isSelected = index == selectedIndex;
      final isDragging = index == _draggingIndex;

      return Marker(
        point: points[index],
        width: widget.vertexRadius * 3,
        height: widget.vertexRadius * 3 + (widget.showLabels ? 20 : 0),
        child: GestureDetector(
          onTap: () => widget.editorState.selectPoint(index),
          onLongPress: () => _showVertexMenu(index),
          onPanStart: (details) => _startDrag(index, details),
          onPanUpdate: (details) => _updateDrag(index, details),
          onPanEnd: (details) => _endDrag(index),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Vertex circle
              AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                width: widget.vertexRadius * 2 * (isDragging ? 1.3 : 1),
                height: widget.vertexRadius * 2 * (isDragging ? 1.3 : 1),
                decoration: BoxDecoration(
                  color: isSelected || isDragging
                      ? widget.selectedVertexColor
                      : widget.vertexColor,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: widget.polygonColor,
                    width: 3,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: (isSelected ? widget.selectedVertexColor : widget.polygonColor)
                          .withOpacity(0.4),
                      blurRadius: isSelected ? 12 : 6,
                      spreadRadius: isSelected ? 2 : 0,
                    ),
                  ],
                ),
                child: Center(
                  child: Text(
                    '${index + 1}',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: isSelected || isDragging ? Colors.white : widget.polygonColor,
                    ),
                  ),
                ),
              ),

              // Label
              if (widget.showLabels && index == 0)
                Container(
                  margin: const EdgeInsets.only(top: 4),
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: widget.polygonColor,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Text(
                    'البداية',
                    style: TextStyle(
                      fontSize: 10,
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
        ),
      );
    });
  }

  /// بناء علامات منتصف الحواف (لإضافة نقاط جديدة)
  List<Marker> _buildMidpointMarkers() {
    final points = widget.editorState.points;
    final markers = <Marker>[];

    for (int i = 0; i < points.length; i++) {
      final j = (i + 1) % points.length;

      // Skip if polygon is not closed and this is the last edge
      if (!widget.editorState.isClosed && j == 0) continue;

      final midpoint = LatLng(
        (points[i].latitude + points[j].latitude) / 2,
        (points[i].longitude + points[j].longitude) / 2,
      );

      markers.add(Marker(
        point: midpoint,
        width: 24,
        height: 24,
        child: GestureDetector(
          onTap: () => widget.editorState.insertPoint(j, midpoint),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.8),
              shape: BoxShape.circle,
              border: Border.all(
                color: widget.polygonColor.withOpacity(0.5),
                width: 2,
              ),
            ),
            child: Icon(
              Icons.add,
              size: 16,
              color: widget.polygonColor,
            ),
          ),
        ),
      ));
    }

    return markers;
  }

  // ─────────────────────────────────────────────────────────────────
  // Drag Handling with project/unproject
  // ─────────────────────────────────────────────────────────────────

  void _startDrag(int index, DragStartDetails details) {
    _draggingIndex = index;
    _dragStartOffset = details.localPosition;
    widget.editorState.startDragPoint(index);
  }

  void _updateDrag(int index, DragUpdateDetails details) {
    if (_draggingIndex != index) return;

    final points = widget.editorState.points;
    final currentPoint = points[index];

    // Project current point to screen coordinates
    final screenPoint = widget.mapController.camera.latLngToScreenPoint(currentPoint);

    // Apply delta
    final newScreenPoint = Point<double>(
      screenPoint.x + details.delta.dx,
      screenPoint.y + details.delta.dy,
    );

    // Unproject back to LatLng
    var newLatLng = widget.mapController.camera.pointToLatLng(newScreenPoint);

    // Snap to vertex if enabled
    if (widget.enableSnap) {
      final otherPoints = List<LatLng>.from(points)..removeAt(index);
      final snapped = GeoUtils.snapToVertex(
        newLatLng,
        otherPoints,
        thresholdMeters: widget.snapThresholdMeters,
      );
      if (snapped != null) {
        newLatLng = snapped;
      }
    }

    widget.editorState.dragPoint(index, newLatLng);
  }

  void _endDrag(int index) {
    _draggingIndex = null;
    _dragStartOffset = null;
    widget.editorState.endDragPoint();
  }

  // ─────────────────────────────────────────────────────────────────
  // Context Menu
  // ─────────────────────────────────────────────────────────────────

  void _showVertexMenu(int index) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.delete, color: Colors.red),
              title: const Text('حذف النقطة'),
              subtitle: Text('النقطة ${index + 1}'),
              onTap: () {
                Navigator.pop(context);
                widget.editorState.removePoint(index);
              },
            ),
            if (index == widget.editorState.points.length - 1 &&
                widget.editorState.canClose &&
                !widget.editorState.isClosed)
              ListTile(
                leading: Icon(Icons.check_circle, color: widget.polygonColor),
                title: const Text('إغلاق المضلع'),
                subtitle: const Text('ربط النقطة الأخيرة بالأولى'),
                onTap: () {
                  Navigator.pop(context);
                  widget.editorState.closePolygon();
                },
              ),
          ],
        ),
      ),
    );
  }
}

/// شريط أدوات محرر المضلعات
class PolygonEditorToolbar extends StatelessWidget {
  final PolygonEditorState editorState;
  final VoidCallback? onSave;
  final VoidCallback? onCancel;
  final AreaUnit areaUnit;

  const PolygonEditorToolbar({
    super.key,
    required this.editorState,
    this.onSave,
    this.onCancel,
    this.areaUnit = AreaUnit.hectares,
  });

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: editorState,
      builder: (context, _) {
        final area = editorState.isClosed
            ? GeoUtils.calculateAreaHectares(editorState.points)
            : 0.0;

        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: SahoolShadows.medium,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Area display
              if (editorState.isClosed)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: BoxDecoration(
                    color: SahoolColors.success.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.straighten, size: 20, color: SahoolColors.success),
                      const SizedBox(width: 8),
                      Text(
                        '${area.toStringAsFixed(2)} ${areaUnit.label}',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: SahoolColors.success,
                        ),
                      ),
                    ],
                  ),
                ),

              // Toolbar buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  // Undo
                  _ToolbarButton(
                    icon: Icons.undo,
                    label: 'تراجع',
                    onPressed: editorState.canUndo ? editorState.undo : null,
                  ),

                  // Redo
                  _ToolbarButton(
                    icon: Icons.redo,
                    label: 'إعادة',
                    onPressed: editorState.canRedo ? editorState.redo : null,
                  ),

                  // Close polygon
                  _ToolbarButton(
                    icon: editorState.isClosed ? Icons.edit : Icons.check_circle,
                    label: editorState.isClosed ? 'تعديل' : 'إغلاق',
                    onPressed: editorState.canClose
                        ? () {
                            if (editorState.isClosed) {
                              editorState.openPolygon();
                            } else {
                              editorState.closePolygon();
                            }
                          }
                        : null,
                  ),

                  // Clear
                  _ToolbarButton(
                    icon: Icons.delete_outline,
                    label: 'مسح',
                    onPressed: editorState.hasPoints ? editorState.clear : null,
                    color: Colors.red,
                  ),

                  // Save
                  if (onSave != null)
                    _ToolbarButton(
                      icon: Icons.save,
                      label: 'حفظ',
                      onPressed: editorState.isClosed ? onSave : null,
                      color: SahoolColors.primary,
                    ),
                ],
              ),

              // Points count
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  '${editorState.pointCount} نقطة',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _ToolbarButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onPressed;
  final Color? color;

  const _ToolbarButton({
    required this.icon,
    required this.label,
    this.onPressed,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final isEnabled = onPressed != null;
    final buttonColor = color ?? SahoolColors.primary;

    return GestureDetector(
      onTap: onPressed,
      child: Opacity(
        opacity: isEnabled ? 1.0 : 0.4,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: isEnabled ? buttonColor.withOpacity(0.1) : Colors.grey[200],
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                color: isEnabled ? buttonColor : Colors.grey,
                size: 24,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: isEnabled ? buttonColor : Colors.grey,
                fontWeight: isEnabled ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
