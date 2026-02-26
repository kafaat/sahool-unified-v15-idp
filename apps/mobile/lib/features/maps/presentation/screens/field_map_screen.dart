import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';

import '../../../../core/map/sahool_tile_provider.dart';

import '../../../../core/geo/geojson.dart';

/// شاشة خريطة الحقل مع طبقات NDVI
/// Field Map Screen with NDVI Layers
class FieldMapScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String? fieldName;
  final Map<String, dynamic>? initialCenter;

  const FieldMapScreen({
    super.key,
    required this.fieldId,
    this.fieldName,
    this.initialCenter,
  });

  @override
  ConsumerState<FieldMapScreen> createState() => _FieldMapScreenState();
}

class _FieldMapScreenState extends ConsumerState<FieldMapScreen> {
  String _selectedLayer = 'satellite';
  bool _showZones = true;
  bool _showNdvi = false;
  bool _showNdwi = false;
  bool _showGpsTrack = false;
  bool _isTracking = false;
  String? _selectedZoneId;
  double _currentZoom = 15.0;

  /// Map controller for programmatic camera control
  late final MapController _mapController;

  /// Field boundary coordinates (loaded from field data)
  List<LatLng> _fieldBoundary = [];

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _loadFieldBoundary();
  }

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  /// Load field boundary from initial center data or fetch from repository
  void _loadFieldBoundary() {
    // Try to extract boundary from initialCenter if provided as GeoJSON
    if (widget.initialCenter != null) {
      final geometry = widget.initialCenter!['geometry'];
      if (geometry != null && geometry['type'] == 'Polygon') {
        try {
          _fieldBoundary = GeoJson.parsePolygon(geometry as Map<String, dynamic>);
        } catch (_) {
          // Fallback: use center point to create a small bounding area
          _createBoundaryFromCenter();
        }
      } else if (widget.initialCenter!['lat'] != null &&
          widget.initialCenter!['lng'] != null) {
        _createBoundaryFromCenter();
      }
    }
  }

  /// Create a small bounding area from center point (fallback)
  void _createBoundaryFromCenter() {
    final lat = (widget.initialCenter!['lat'] as num?)?.toDouble();
    final lng = (widget.initialCenter!['lng'] as num?)?.toDouble();
    if (lat != null && lng != null) {
      // Create a small polygon around the center (approximately 100m x 100m)
      const offset = 0.001; // ~100m at equator
      _fieldBoundary = [
        LatLng(lat - offset, lng - offset),
        LatLng(lat - offset, lng + offset),
        LatLng(lat + offset, lng + offset),
        LatLng(lat + offset, lng - offset),
      ];
    }
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.fieldName ?? 'خريطة الحقل'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            IconButton(
              icon: const Icon(Icons.layers),
              onPressed: _showLayersSheet,
              tooltip: 'الطبقات',
            ),
            IconButton(
              icon: const Icon(Icons.my_location),
              onPressed: _centerOnField,
              tooltip: 'توسيط',
            ),
          ],
        ),
        body: Stack(
          children: [
            // الخريطة الرئيسية
            _buildMapView(),

            // شريط الأدوات العائم
            Positioned(
              top: 16,
              right: 16,
              child: _buildToolbar(),
            ),

            // معلومات المنطقة المحددة
            if (_selectedZoneId != null)
              Positioned(
                bottom: 100,
                left: 16,
                right: 16,
                child: _buildZoneInfoCard(),
              ),

            // مفتاح الألوان
            Positioned(
              bottom: 16,
              left: 16,
              child: _buildLegend(),
            ),
          ],
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: _openDiagnosis,
          backgroundColor: const Color(0xFF367C2B),
          icon: const Icon(Icons.medical_services),
          label: const Text('تشخيص'),
        ),
      ),
    );
  }

  Widget _buildMapView() {
    // Determine center point
    final center = _fieldBoundary.isNotEmpty
        ? GeoJson.calculateCentroid(_fieldBoundary)
        : (widget.initialCenter != null
            ? LatLng(
                (widget.initialCenter!['lat'] as num?)?.toDouble() ?? 15.3694,
                (widget.initialCenter!['lng'] as num?)?.toDouble() ?? 44.1910,
              )
            : const LatLng(15.3694, 44.1910));

    // Determine tile URL based on selected layer
    final String tileUrl;
    switch (_selectedLayer) {
      case 'satellite':
        tileUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
        break;
      case 'terrain':
        tileUrl = 'https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png';
        break;
      default:
        tileUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
    }

    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: center,
        initialZoom: _currentZoom,
        onPositionChanged: (position, hasGesture) {
          if (hasGesture && mounted) {
            setState(() => _currentZoom = position.zoom ?? _currentZoom);
          }
        },
        onTap: (tapPosition, point) {
          if (_selectedZoneId != null) {
            setState(() => _selectedZoneId = null);
          }
        },
      ),
      children: [
        // Base tile layer
        TileLayer(
          urlTemplate: tileUrl,
          userAgentPackageName: 'com.sahool.field',
          maxZoom: 19,
          tileProvider: SahoolTileProvider(),
        ),

        // Field boundary polygon
        if (_fieldBoundary.isNotEmpty)
          PolygonLayer(
            polygons: [
              Polygon(
                points: _fieldBoundary,
                color: _showNdvi
                    ? Colors.green.withOpacity(0.3)
                    : const Color(0xFF367C2B).withOpacity(0.15),
                borderColor: const Color(0xFF367C2B),
                borderStrokeWidth: 3,
                isFilled: true,
              ),
            ],
          ),

        // NDVI colored overlay (mock zones for visualization)
        if (_showNdvi && _fieldBoundary.isNotEmpty)
          PolygonLayer(
            polygons: [
              Polygon(
                points: _fieldBoundary,
                color: Colors.green.withOpacity(0.35),
                borderColor: Colors.green[700]!,
                borderStrokeWidth: 2,
                isFilled: true,
                label: 'NDVI: 0.72',
                labelStyle: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  shadows: [Shadow(color: Colors.black54, blurRadius: 4)],
                ),
              ),
            ],
          ),

        // NDWI overlay
        if (_showNdwi && _fieldBoundary.isNotEmpty)
          PolygonLayer(
            polygons: [
              Polygon(
                points: _fieldBoundary,
                color: Colors.blue.withOpacity(0.3),
                borderColor: Colors.blue[700]!,
                borderStrokeWidth: 2,
                isFilled: true,
                label: 'NDWI: -0.05',
                labelStyle: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  shadows: [Shadow(color: Colors.black54, blurRadius: 4)],
                ),
              ),
            ],
          ),

        // Center marker
        MarkerLayer(
          markers: [
            Marker(
              point: center,
              width: 40,
              height: 40,
              child: Icon(
                _isTracking ? Icons.my_location : Icons.location_on,
                size: 36,
                color: _isTracking ? Colors.blue : const Color(0xFF367C2B),
              ),
            ),
          ],
        ),

        // Tracking indicator
        if (_isTracking)
          MarkerLayer(
            markers: [
              Marker(
                point: center,
                width: 100,
                height: 100,
                child: Container(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.blue.withOpacity(0.15),
                    border: Border.all(color: Colors.blue.withOpacity(0.4), width: 2),
                  ),
                ),
              ),
            ],
          ),
      ],
    );
  }

  Widget _buildToolbar() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _buildToolButton(
              icon: Icons.add,
              onPressed: () {
                final zoom = _mapController.camera.zoom;
                _mapController.move(_mapController.camera.center, zoom + 1);
              },
              tooltip: 'تكبير',
            ),
            _buildToolButton(
              icon: Icons.remove,
              onPressed: () {
                final zoom = _mapController.camera.zoom;
                _mapController.move(_mapController.camera.center, zoom - 1);
              },
              tooltip: 'تصغير',
            ),
            const Divider(height: 16),
            _buildToolButton(
              icon: Icons.crop_square,
              isActive: _showZones,
              onPressed: () => setState(() => _showZones = !_showZones),
              tooltip: 'المناطق',
            ),
            _buildToolButton(
              icon: Icons.grass,
              isActive: _showNdvi,
              onPressed: () => setState(() => _showNdvi = !_showNdvi),
              tooltip: 'NDVI',
            ),
            _buildToolButton(
              icon: Icons.water_drop,
              isActive: _showNdwi,
              onPressed: () => setState(() => _showNdwi = !_showNdwi),
              tooltip: 'NDWI',
            ),
            const Divider(height: 16),
            _buildToolButton(
              icon: Icons.gps_fixed,
              isActive: _showGpsTrack,
              activeColor: Colors.orange,
              onPressed: () => setState(() => _showGpsTrack = !_showGpsTrack),
              tooltip: 'تتبع GPS',
            ),
            _buildToolButton(
              icon: _isTracking ? Icons.gps_off : Icons.my_location,
              isActive: _isTracking,
              activeColor: Colors.blue,
              onPressed: () => setState(() => _isTracking = !_isTracking),
              tooltip: _isTracking ? 'إيقاف التتبع' : 'بدء التتبع',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildToolButton({
    required IconData icon,
    required VoidCallback onPressed,
    required String tooltip,
    bool isActive = false,
    Color? activeColor,
  }) {
    final color = activeColor ?? const Color(0xFF367C2B);
    return Tooltip(
      message: tooltip,
      child: IconButton(
        icon: Icon(
          icon,
          color: isActive ? color : Colors.grey[600],
        ),
        onPressed: onPressed,
        style: IconButton.styleFrom(
          backgroundColor: isActive ? color.withOpacity(0.1) : Colors.transparent,
        ),
      ),
    );
  }

  Widget _buildZoneInfoCard() {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF367C2B).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.location_on,
                    color: Color(0xFF367C2B),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'المنطقة $_selectedZoneId',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      Text(
                        '5.2 هكتار',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => setState(() => _selectedZoneId = null),
                ),
              ],
            ),
            const Divider(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildIndicator('NDVI', '0.72', Colors.green),
                _buildIndicator('NDWI', '-0.05', Colors.blue),
                _buildIndicator('NDRE', '0.28', Colors.orange),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.timeline),
                    label: const Text('السلسلة الزمنية'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.medical_services),
                    label: const Text('تشخيص'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF367C2B),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIndicator(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 12,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
        ),
      ],
    );
  }

  Widget _buildLegend() {
    if (!_showNdvi && !_showNdwi) return const SizedBox.shrink();

    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              _showNdvi ? 'NDVI' : 'NDWI',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Container(
              width: 150,
              height: 16,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(4),
                gradient: LinearGradient(
                  colors: _showNdvi
                      ? [
                          Colors.red,
                          Colors.yellow,
                          Colors.green,
                          Colors.green[800]!,
                        ]
                      : [
                          Colors.brown,
                          Colors.yellow,
                          Colors.blue,
                          Colors.blue[800]!,
                        ],
                ),
              ),
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  _showNdvi ? '0' : '-1',
                  style: const TextStyle(fontSize: 10),
                ),
                Text(
                  _showNdvi ? '1' : '1',
                  style: const TextStyle(fontSize: 10),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showLayersSheet() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                  'طبقات الخريطة',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const Divider(),
              ListTile(
                leading: const Icon(Icons.satellite_alt),
                title: const Text('القمر الصناعي'),
                trailing: _selectedLayer == 'satellite'
                    ? const Icon(Icons.check, color: Color(0xFF367C2B))
                    : null,
                onTap: () {
                  setState(() => _selectedLayer = 'satellite');
                  Navigator.pop(context);
                },
              ),
              ListTile(
                leading: const Icon(Icons.terrain),
                title: const Text('التضاريس'),
                trailing: _selectedLayer == 'terrain'
                    ? const Icon(Icons.check, color: Color(0xFF367C2B))
                    : null,
                onTap: () {
                  setState(() => _selectedLayer = 'terrain');
                  Navigator.pop(context);
                },
              ),
              ListTile(
                leading: const Icon(Icons.map),
                title: const Text('الشوارع'),
                trailing: _selectedLayer == 'streets'
                    ? const Icon(Icons.check, color: Color(0xFF367C2B))
                    : null,
                onTap: () {
                  setState(() => _selectedLayer = 'streets');
                  Navigator.pop(context);
                },
              ),
              const Divider(),
              SwitchListTile(
                secondary: const Icon(Icons.crop_square),
                title: const Text('عرض المناطق'),
                value: _showZones,
                onChanged: (v) {
                  setState(() => _showZones = v);
                },
                activeColor: const Color(0xFF367C2B),
              ),
              SwitchListTile(
                secondary: const Icon(Icons.grass),
                title: const Text('طبقة NDVI'),
                value: _showNdvi,
                onChanged: (v) {
                  setState(() => _showNdvi = v);
                },
                activeColor: const Color(0xFF367C2B),
              ),
              SwitchListTile(
                secondary: const Icon(Icons.water_drop),
                title: const Text('طبقة NDWI'),
                value: _showNdwi,
                onChanged: (v) {
                  setState(() => _showNdwi = v);
                },
                activeColor: const Color(0xFF367C2B),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  /// Center map on field bounds with padding and smooth animation
  ///
  /// Calculates the bounding box of the field geometry and uses
  /// the map controller to fit the bounds with appropriate padding.
  void _centerOnField() {
    // Check if we have field boundary data
    if (_fieldBoundary.isEmpty) {
      // Try to use initialCenter as fallback
      if (widget.initialCenter != null) {
        final lat = (widget.initialCenter!['lat'] as num?)?.toDouble();
        final lng = (widget.initialCenter!['lng'] as num?)?.toDouble();
        if (lat != null && lng != null) {
          // Animate to center point with default zoom
          _mapController.move(
            LatLng(lat, lng),
            16.0, // Default zoom for single point
          );
          setState(() => _currentZoom = 16.0);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('تم التوسيط على موقع الحقل'),
              duration: Duration(seconds: 2),
            ),
          );
          return;
        }
      }

      // No boundary or center data available
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('لا تتوفر بيانات حدود الحقل'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    // Calculate the bounding box of the field geometry
    final bounds = GeoJson.calculateBounds(_fieldBoundary);

    // Add padding around the field (in screen pixels)
    // This ensures the field boundary is not flush against the screen edges
    const EdgeInsets padding = EdgeInsets.all(50.0);

    // Use fitCamera to fit the bounds with padding and animation
    // CameraFit.bounds calculates the optimal center and zoom level
    _mapController.fitCamera(
      CameraFit.bounds(
        bounds: bounds,
        padding: padding,
        // Maximum zoom level to prevent over-zooming on small fields
        maxZoom: 18.0,
      ),
    );

    // Update the current zoom state to reflect the new camera position
    // Note: The actual zoom is calculated by fitCamera based on bounds
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        setState(() {
          _currentZoom = _mapController.camera.zoom;
        });
      }
    });

    // Show feedback to user
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم التوسيط على حدود الحقل'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _openDiagnosis() {
    context.push('/crop-health', extra: {
      'fieldId': widget.fieldId,
      'fieldName': widget.fieldName,
    });
  }
}
