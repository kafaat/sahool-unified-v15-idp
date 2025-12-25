/// SAHOOL Map Widget - Multi-Provider Map Component
/// مكون الخريطة متعدد المزودين
///
/// Features:
/// - Multiple map providers (MapLibre, OSM, Satellite)
/// - Offline map support
/// - Field polygon drawing
/// - Marker clustering
/// - Yemen-optimized defaults

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'map_providers.dart';

/// Map interaction mode
enum MapInteractionMode {
  view,        // View only
  selectPoint, // Select a single point
  drawPolygon, // Draw field polygon
  measure,     // Measure distance/area
}

/// SAHOOL Map Widget
/// مكون خريطة سهول
class SahoolMapWidget extends ConsumerStatefulWidget {
  /// Initial center point
  final LatLng? initialCenter;

  /// Initial zoom level
  final double initialZoom;

  /// Map provider configuration
  final MapProviderConfig? providerConfig;

  /// Show satellite layer toggle
  final bool showLayerToggle;

  /// Field polygons to display
  final List<List<LatLng>>? fieldPolygons;

  /// Markers to display
  final List<Marker>? markers;

  /// Interaction mode
  final MapInteractionMode interactionMode;

  /// Callback when point is selected
  final Function(LatLng)? onPointSelected;

  /// Callback when polygon is completed
  final Function(List<LatLng>)? onPolygonCompleted;

  /// Callback when map is moved
  final Function(LatLng center, double zoom)? onMapMoved;

  /// Show current location button
  final bool showMyLocation;

  /// Show zoom controls
  final bool showZoomControls;

  /// Enable offline mode
  final bool enableOffline;

  const SahoolMapWidget({
    super.key,
    this.initialCenter,
    this.initialZoom = 10.0,
    this.providerConfig,
    this.showLayerToggle = true,
    this.fieldPolygons,
    this.markers,
    this.interactionMode = MapInteractionMode.view,
    this.onPointSelected,
    this.onPolygonCompleted,
    this.onMapMoved,
    this.showMyLocation = true,
    this.showZoomControls = true,
    this.enableOffline = true,
  });

  @override
  ConsumerState<SahoolMapWidget> createState() => _SahoolMapWidgetState();
}

class _SahoolMapWidgetState extends ConsumerState<SahoolMapWidget> {
  late MapController _mapController;
  late MapProviderConfig _currentProvider;
  bool _showSatellite = false;
  List<LatLng> _drawnPoints = [];

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _currentProvider = widget.providerConfig ?? SahoolMapProviders.defaultProvider;
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  void _toggleSatellite() {
    setState(() {
      _showSatellite = !_showSatellite;
      _currentProvider = _showSatellite
          ? SahoolMapProviders.defaultSatellite
          : SahoolMapProviders.defaultProvider;
    });
  }

  void _handleTap(TapPosition tapPosition, LatLng point) {
    switch (widget.interactionMode) {
      case MapInteractionMode.selectPoint:
        widget.onPointSelected?.call(point);
        break;
      case MapInteractionMode.drawPolygon:
        setState(() {
          _drawnPoints.add(point);
        });
        break;
      default:
        break;
    }
  }

  void _completePolygon() {
    if (_drawnPoints.length >= 3) {
      widget.onPolygonCompleted?.call(List.from(_drawnPoints));
      setState(() {
        _drawnPoints.clear();
      });
    }
  }

  void _undoLastPoint() {
    if (_drawnPoints.isNotEmpty) {
      setState(() {
        _drawnPoints.removeLast();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final center = widget.initialCenter ?? YemenMapBounds.center;

    return Stack(
      children: [
        // Main Map
        FlutterMap(
          mapController: _mapController,
          options: MapOptions(
            initialCenter: center,
            initialZoom: widget.initialZoom,
            minZoom: YemenMapBounds.minZoom,
            maxZoom: YemenMapBounds.maxZoom,
            onTap: _handleTap,
            onPositionChanged: (position, hasGesture) {
              if (hasGesture && widget.onMapMoved != null) {
                widget.onMapMoved!(
                  position.center ?? center,
                  position.zoom ?? widget.initialZoom,
                );
              }
            },
          ),
          children: [
            // Tile Layer
            TileLayer(
              urlTemplate: _currentProvider.tileUrl,
              userAgentPackageName: 'app.sahool.field',
              maxZoom: _currentProvider.maxZoom.toDouble(),
            ),

            // Field Polygons
            if (widget.fieldPolygons != null && widget.fieldPolygons!.isNotEmpty)
              PolygonLayer(
                polygons: widget.fieldPolygons!.map((points) => Polygon(
                  points: points,
                  color: Colors.green.withOpacity(0.3),
                  borderColor: Colors.green,
                  borderStrokeWidth: 2,
                  isFilled: true,
                )).toList(),
              ),

            // Drawing polygon
            if (_drawnPoints.isNotEmpty)
              PolygonLayer(
                polygons: [
                  Polygon(
                    points: _drawnPoints,
                    color: Colors.blue.withOpacity(0.2),
                    borderColor: Colors.blue,
                    borderStrokeWidth: 3,
                    isFilled: true,
                  ),
                ],
              ),

            // Drawing points
            if (_drawnPoints.isNotEmpty)
              MarkerLayer(
                markers: _drawnPoints.asMap().entries.map((entry) => Marker(
                  point: entry.value,
                  width: 24,
                  height: 24,
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.blue,
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 2),
                    ),
                    child: Center(
                      child: Text(
                        '${entry.key + 1}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                )).toList(),
              ),

            // Custom markers
            if (widget.markers != null && widget.markers!.isNotEmpty)
              MarkerLayer(markers: widget.markers!),

            // Attribution
            RichAttributionWidget(
              attributions: [
                TextSourceAttribution(_currentProvider.attribution),
              ],
            ),
          ],
        ),

        // Layer Toggle Button
        if (widget.showLayerToggle)
          Positioned(
            top: 16,
            right: 16,
            child: Column(
              children: [
                _buildControlButton(
                  icon: _showSatellite ? Icons.map : Icons.satellite_alt,
                  tooltip: _showSatellite ? 'خريطة' : 'قمر صناعي',
                  onPressed: _toggleSatellite,
                ),
                const SizedBox(height: 8),
                _buildProviderSelector(),
              ],
            ),
          ),

        // Zoom Controls
        if (widget.showZoomControls)
          Positioned(
            bottom: 100,
            right: 16,
            child: Column(
              children: [
                _buildControlButton(
                  icon: Icons.add,
                  tooltip: 'تكبير',
                  onPressed: () {
                    final currentZoom = _mapController.camera.zoom;
                    _mapController.move(
                      _mapController.camera.center,
                      currentZoom + 1,
                    );
                  },
                ),
                const SizedBox(height: 8),
                _buildControlButton(
                  icon: Icons.remove,
                  tooltip: 'تصغير',
                  onPressed: () {
                    final currentZoom = _mapController.camera.zoom;
                    _mapController.move(
                      _mapController.camera.center,
                      currentZoom - 1,
                    );
                  },
                ),
              ],
            ),
          ),

        // Drawing Controls
        if (widget.interactionMode == MapInteractionMode.drawPolygon)
          Positioned(
            bottom: 16,
            left: 16,
            right: 16,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    Text(
                      'النقاط: ${_drawnPoints.length}',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    TextButton.icon(
                      onPressed: _drawnPoints.isNotEmpty ? _undoLastPoint : null,
                      icon: const Icon(Icons.undo),
                      label: const Text('تراجع'),
                    ),
                    ElevatedButton.icon(
                      onPressed: _drawnPoints.length >= 3 ? _completePolygon : null,
                      icon: const Icon(Icons.check),
                      label: const Text('إنهاء'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

        // Current Provider Info
        Positioned(
          bottom: 16,
          left: 16,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.black54,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              _currentProvider.nameAr,
              style: const TextStyle(color: Colors.white, fontSize: 10),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildControlButton({
    required IconData icon,
    required String tooltip,
    required VoidCallback onPressed,
  }) {
    return Material(
      elevation: 2,
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Tooltip(
            message: tooltip,
            child: Icon(icon, color: Colors.grey[700]),
          ),
        ),
      ),
    );
  }

  Widget _buildProviderSelector() {
    return PopupMenuButton<MapProviderConfig>(
      onSelected: (provider) {
        setState(() {
          _currentProvider = provider;
          _showSatellite = provider.provider == MapProvider.satellite;
        });
      },
      itemBuilder: (context) => SahoolMapProviders.freeProviders
          .map((provider) => PopupMenuItem(
                value: provider,
                child: Row(
                  children: [
                    Icon(
                      provider.provider == MapProvider.satellite
                          ? Icons.satellite_alt
                          : Icons.map,
                      size: 20,
                      color: _currentProvider == provider
                          ? Theme.of(context).primaryColor
                          : Colors.grey,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      provider.nameAr,
                      style: TextStyle(
                        fontWeight: _currentProvider == provider
                            ? FontWeight.bold
                            : FontWeight.normal,
                      ),
                    ),
                  ],
                ),
              ))
          .toList(),
      child: Material(
        elevation: 2,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
          ),
          child: const Icon(Icons.layers, color: Colors.grey),
        ),
      ),
    );
  }
}
