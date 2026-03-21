import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../../core/maps/offline/tile_downloader.dart';
import '../../../../core/theme/sahool_theme.dart';

/// Region Selector - محدد المنطقة على الخريطة
///
/// Map-based region selection with draggable bounds
class RegionSelector extends StatefulWidget {
  final RegionBounds? initialBounds;
  final void Function(RegionBounds) onBoundsChanged;
  final LatLng? initialCenter;
  final double initialZoom;

  const RegionSelector({
    super.key,
    this.initialBounds,
    required this.onBoundsChanged,
    this.initialCenter,
    this.initialZoom = 8.0,
  });

  @override
  State<RegionSelector> createState() => _RegionSelectorState();
}

class _RegionSelectorState extends State<RegionSelector> {
  late MapController _mapController;
  late RegionBounds _bounds;
  bool _isDragging = false;
  _DragHandle? _activeHandle;

  // Yemen center coordinates
  static const _yemenCenter = LatLng(15.5, 48.0);

  @override
  void initState() {
    super.initState();
    _mapController = MapController();

    // Initialize bounds
    _bounds = widget.initialBounds ??
        RegionBounds(
          south: 15.2,
          west: 44.0,
          north: 15.5,
          east: 44.4,
        );
  }

  void _updateBounds(RegionBounds newBounds) {
    setState(() {
      _bounds = newBounds;
    });
    widget.onBoundsChanged(newBounds);
  }

  void _onHandleDrag(_DragHandle handle, LatLng position) {
    RegionBounds newBounds;

    switch (handle) {
      case _DragHandle.north:
        newBounds = RegionBounds(
          south: _bounds.south,
          west: _bounds.west,
          north: position.latitude,
          east: _bounds.east,
        );
        break;
      case _DragHandle.south:
        newBounds = RegionBounds(
          south: position.latitude,
          west: _bounds.west,
          north: _bounds.north,
          east: _bounds.east,
        );
        break;
      case _DragHandle.east:
        newBounds = RegionBounds(
          south: _bounds.south,
          west: _bounds.west,
          north: _bounds.north,
          east: position.longitude,
        );
        break;
      case _DragHandle.west:
        newBounds = RegionBounds(
          south: _bounds.south,
          west: position.longitude,
          north: _bounds.north,
          east: _bounds.east,
        );
        break;
      case _DragHandle.northEast:
        newBounds = RegionBounds(
          south: _bounds.south,
          west: _bounds.west,
          north: position.latitude,
          east: position.longitude,
        );
        break;
      case _DragHandle.northWest:
        newBounds = RegionBounds(
          south: _bounds.south,
          west: position.longitude,
          north: position.latitude,
          east: _bounds.east,
        );
        break;
      case _DragHandle.southEast:
        newBounds = RegionBounds(
          south: position.latitude,
          west: _bounds.west,
          north: _bounds.north,
          east: position.longitude,
        );
        break;
      case _DragHandle.southWest:
        newBounds = RegionBounds(
          south: position.latitude,
          west: position.longitude,
          north: _bounds.north,
          east: _bounds.east,
        );
        break;
      case _DragHandle.center:
        final latDelta = (_bounds.north - _bounds.south) / 2;
        final lngDelta = (_bounds.east - _bounds.west) / 2;
        newBounds = RegionBounds(
          south: position.latitude - latDelta,
          west: position.longitude - lngDelta,
          north: position.latitude + latDelta,
          east: position.longitude + lngDelta,
        );
        break;
    }

    // Ensure valid bounds (min size)
    if ((newBounds.north - newBounds.south).abs() >= 0.01 &&
        (newBounds.east - newBounds.west).abs() >= 0.01) {
      _updateBounds(newBounds);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Map
        FlutterMap(
          mapController: _mapController,
          options: MapOptions(
            initialCenter: widget.initialCenter ?? _yemenCenter,
            initialZoom: widget.initialZoom,
            minZoom: 4,
            maxZoom: 18,
            onTap: (tapPosition, point) {
              if (!_isDragging) {
                // Center selection on tap point
                final size = 0.15; // Default size in degrees
                _updateBounds(RegionBounds(
                  south: point.latitude - size,
                  west: point.longitude - size,
                  north: point.latitude + size,
                  east: point.longitude + size,
                ));
              }
            },
          ),
          children: [
            // Base tile layer
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.sahool.fieldapp',
            ),

            // Selection polygon
            PolygonLayer(
              polygons: [
                Polygon(
                  points: [
                    LatLng(_bounds.north, _bounds.west),
                    LatLng(_bounds.north, _bounds.east),
                    LatLng(_bounds.south, _bounds.east),
                    LatLng(_bounds.south, _bounds.west),
                  ],
                  color: SahoolColors.primary.withOpacity(0.2),
                  borderColor: SahoolColors.primary,
                  borderStrokeWidth: 2,
                ),
              ],
            ),

            // Drag handles
            MarkerLayer(
              markers: _buildDragHandles(),
            ),
          ],
        ),

        // Instructions overlay
        Positioned(
          top: 8,
          left: 8,
          right: 8,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.9),
              borderRadius: BorderRadius.circular(8),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                ),
              ],
            ),
            child: Row(
              children: [
                const Icon(Icons.touch_app, size: 18, color: SahoolColors.primary),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    'اضغط على الخريطة لتحديد منطقة، أو اسحب المقابض لتعديل الحدود',
                    style: TextStyle(fontSize: 12),
                  ),
                ),
              ],
            ),
          ),
        ),

        // Zoom to selection button
        Positioned(
          bottom: 16,
          right: 16,
          child: Column(
            children: [
              FloatingActionButton.small(
                heroTag: 'zoom_in',
                onPressed: () {
                  final currentZoom = _mapController.camera.zoom;
                  _mapController.move(
                    _mapController.camera.center,
                    currentZoom + 1,
                  );
                },
                backgroundColor: Colors.white,
                child: const Icon(Icons.add, color: SahoolColors.primary),
              ),
              const SizedBox(height: 8),
              FloatingActionButton.small(
                heroTag: 'zoom_out',
                onPressed: () {
                  final currentZoom = _mapController.camera.zoom;
                  _mapController.move(
                    _mapController.camera.center,
                    currentZoom - 1,
                  );
                },
                backgroundColor: Colors.white,
                child: const Icon(Icons.remove, color: SahoolColors.primary),
              ),
              const SizedBox(height: 8),
              FloatingActionButton.small(
                heroTag: 'fit_bounds',
                onPressed: () {
                  _mapController.fitCamera(
                    CameraFit.bounds(
                      bounds: LatLngBounds(
                        LatLng(_bounds.south, _bounds.west),
                        LatLng(_bounds.north, _bounds.east),
                      ),
                      padding: const EdgeInsets.all(50),
                    ),
                  );
                },
                backgroundColor: Colors.white,
                child: const Icon(Icons.crop_free, color: SahoolColors.primary),
              ),
            ],
          ),
        ),
      ],
    );
  }

  List<Marker> _buildDragHandles() {
    return [
      // Corner handles
      _buildHandle(_DragHandle.northWest, LatLng(_bounds.north, _bounds.west)),
      _buildHandle(_DragHandle.northEast, LatLng(_bounds.north, _bounds.east)),
      _buildHandle(_DragHandle.southWest, LatLng(_bounds.south, _bounds.west)),
      _buildHandle(_DragHandle.southEast, LatLng(_bounds.south, _bounds.east)),

      // Edge handles
      _buildHandle(
        _DragHandle.north,
        LatLng(_bounds.north, (_bounds.west + _bounds.east) / 2),
      ),
      _buildHandle(
        _DragHandle.south,
        LatLng(_bounds.south, (_bounds.west + _bounds.east) / 2),
      ),
      _buildHandle(
        _DragHandle.west,
        LatLng((_bounds.north + _bounds.south) / 2, _bounds.west),
      ),
      _buildHandle(
        _DragHandle.east,
        LatLng((_bounds.north + _bounds.south) / 2, _bounds.east),
      ),

      // Center handle
      _buildHandle(
        _DragHandle.center,
        LatLng(
          (_bounds.north + _bounds.south) / 2,
          (_bounds.west + _bounds.east) / 2,
        ),
        isCenter: true,
      ),
    ];
  }

  Marker _buildHandle(_DragHandle handle, LatLng position,
      {bool isCenter = false}) {
    return Marker(
      point: position,
      width: isCenter ? 30 : 24,
      height: isCenter ? 30 : 24,
      child: GestureDetector(
        onPanStart: (_) {
          setState(() {
            _isDragging = true;
            _activeHandle = handle;
          });
        },
        onPanUpdate: (details) {
          // Convert screen position to map coordinates
          final screenPoint =
              _mapController.camera.latLngToScreenOffset(position);
          final newScreenPoint = screenPoint + details.delta;
          final newLatLng =
              _mapController.camera.screenOffsetToLatLng(newScreenPoint);
          _onHandleDrag(handle, newLatLng);
        },
        onPanEnd: (_) {
          setState(() {
            _isDragging = false;
            _activeHandle = null;
          });
        },
        child: Container(
          decoration: BoxDecoration(
            color: isCenter
                ? SahoolColors.primary
                : (_activeHandle == handle
                    ? SahoolColors.secondary
                    : Colors.white),
            shape: BoxShape.circle,
            border: Border.all(
              color: SahoolColors.primary,
              width: 2,
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.2),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: isCenter
              ? const Icon(
                  Icons.open_with,
                  size: 16,
                  color: Colors.white,
                )
              : null,
        ),
      ),
    );
  }
}

/// Drag handle enum
enum _DragHandle {
  north,
  south,
  east,
  west,
  northEast,
  northWest,
  southEast,
  southWest,
  center,
}

/// Simple Region Preview - معاينة بسيطة للمنطقة
///
/// A non-interactive map preview showing a region
class RegionPreview extends StatelessWidget {
  final RegionBounds bounds;
  final double height;
  final bool showLabels;

  const RegionPreview({
    super.key,
    required this.bounds,
    this.height = 150,
    this.showLabels = false,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: SizedBox(
        height: height,
        child: FlutterMap(
          options: MapOptions(
            initialCenter: LatLng(bounds.centerLat, bounds.centerLng),
            initialZoom: 10,
            interactionOptions: const InteractionOptions(
              flags: InteractiveFlag.none,
            ),
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.sahool.fieldapp',
            ),
            PolygonLayer(
              polygons: [
                Polygon(
                  points: [
                    LatLng(bounds.north, bounds.west),
                    LatLng(bounds.north, bounds.east),
                    LatLng(bounds.south, bounds.east),
                    LatLng(bounds.south, bounds.west),
                  ],
                  color: SahoolColors.primary.withOpacity(0.2),
                  borderColor: SahoolColors.primary,
                  borderStrokeWidth: 2,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/// Preset Region Chips - شرائح المناطق المعرفة مسبقاً
class PresetRegionChips extends StatelessWidget {
  final List<({String label, RegionBounds bounds})> presets;
  final void Function(RegionBounds) onSelect;

  const PresetRegionChips({
    super.key,
    required this.presets,
    required this.onSelect,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: presets.map((preset) {
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ActionChip(
              label: Text(preset.label),
              avatar: const Icon(Icons.location_on, size: 18),
              onPressed: () => onSelect(preset.bounds),
            ),
          );
        }).toList(),
      ),
    );
  }
}
