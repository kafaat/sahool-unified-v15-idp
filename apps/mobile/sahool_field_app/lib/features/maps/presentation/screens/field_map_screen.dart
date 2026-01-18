import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../../../../core/di/providers.dart';
import '../../../../core/geo/geojson.dart';
import '../../../crop_health/presentation/screens/crop_health_dashboard.dart';

/// شاشة خريطة الحقل مع طبقات NDVI
/// Field Map Screen with NDVI Layers
class FieldMapScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String? fieldName;
  final Map<String, dynamic>? initialCenter;
  final String? highlightZoneId;

  const FieldMapScreen({
    super.key,
    required this.fieldId,
    this.fieldName,
    this.initialCenter,
    this.highlightZoneId,
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

  /// Field boundary for map bounds calculation
  List<LatLng>? _fieldBoundary;

  /// Calculated field bounds
  LatLngBounds? _fieldBounds;

  /// Center point of the field
  LatLng? _fieldCenter;

  @override
  void initState() {
    super.initState();
    // Set initial zone selection from highlightZoneId parameter
    if (widget.highlightZoneId != null) {
      _selectedZoneId = widget.highlightZoneId;
    }
    // Load field data to get bounds
    _loadFieldData();
  }

  /// Load field data to calculate bounds for map centering
  Future<void> _loadFieldData() async {
    try {
      // Try to get field data from initial center if provided
      if (widget.initialCenter != null) {
        final lat = widget.initialCenter!['latitude'] as double?;
        final lng = widget.initialCenter!['longitude'] as double?;
        if (lat != null && lng != null) {
          setState(() {
            _fieldCenter = LatLng(lat, lng);
          });
          return;
        }
      }

      // Load field from repository
      final fieldsRepo = ref.read(fieldsRepoProvider);
      final fields = await fieldsRepo.getAllFields('');

      // Find the field matching our fieldId
      final matchingField = fields.where((f) => f.id == widget.fieldId).firstOrNull;

      if (matchingField != null && matchingField.boundary.isNotEmpty) {
        setState(() {
          _fieldBoundary = matchingField.boundary;
          _fieldBounds = GeoJson.calculateBounds(matchingField.boundary);
          _fieldCenter = matchingField.centroid ?? GeoJson.calculateCentroid(matchingField.boundary);
        });
      }
    } catch (e) {
      // Field data not available, use default behavior
      debugPrint('Could not load field data: $e');
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
    // Placeholder for MapLibre map
    // In production, use maplibre_gl package
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Colors.green[100]!,
            Colors.green[200]!,
          ],
        ),
      ),
      child: Stack(
        children: [
          // خلفية محاكاة للخريطة
          Positioned.fill(
            child: CustomPaint(
              painter: _MapGridPainter(),
            ),
          ),
          // محتوى الخريطة
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // أيقونة الموقع مع حركة
                AnimatedContainer(
                  duration: const Duration(milliseconds: 500),
                  child: Icon(
                    _isTracking ? Icons.my_location : Icons.location_on,
                    size: 60,
                    color: _isTracking ? Colors.blue : const Color(0xFF367C2B),
                  ),
                ),
                const SizedBox(height: 16),
                Text(
                  widget.fieldName ?? 'خريطة الحقل',
                  style: const TextStyle(
                    fontSize: 20,
                    color: Color(0xFF367C2B),
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.9),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    'تكبير: ${_currentZoom.toStringAsFixed(1)}x',
                    style: TextStyle(color: Colors.grey[700], fontSize: 12),
                  ),
                ),
                const SizedBox(height: 16),
                // عرض الطبقات النشطة
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    if (_showZones)
                      _buildActiveLayerChip('المناطق', Icons.crop_square, Colors.blue),
                    if (_showNdvi)
                      _buildActiveLayerChip('NDVI', Icons.grass, Colors.green),
                    if (_showNdwi)
                      _buildActiveLayerChip('NDWI', Icons.water_drop, Colors.cyan),
                    if (_showGpsTrack)
                      _buildActiveLayerChip('GPS', Icons.gps_fixed, Colors.orange),
                  ],
                ),
                const SizedBox(height: 24),
                if (_isTracking)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.blue),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.blue,
                          ),
                        ),
                        SizedBox(width: 8),
                        Text(
                          'جاري تتبع الموقع...',
                          style: TextStyle(color: Colors.blue),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActiveLayerChip(String label, IconData icon, Color color) {
    return Chip(
      avatar: Icon(icon, size: 16, color: color),
      label: Text(label, style: TextStyle(fontSize: 12, color: color)),
      backgroundColor: color.withOpacity(0.1),
      side: BorderSide(color: color.withOpacity(0.3)),
      padding: EdgeInsets.zero,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
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
              onPressed: () => setState(() {
                if (_currentZoom < 20) _currentZoom += 1;
              }),
              tooltip: 'تكبير',
            ),
            _buildToolButton(
              icon: Icons.remove,
              onPressed: () => setState(() {
                if (_currentZoom > 5) _currentZoom -= 1;
              }),
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

  /// Center the map camera on the field's geographic bounds
  /// When actual MapLibre map is integrated, this will animate the camera
  /// to fit the field bounds within the viewport with appropriate padding
  void _centerOnField() {
    if (_fieldBounds != null) {
      // When MapLibre is integrated, use:
      // mapController.fitBounds(
      //   _fieldBounds!,
      //   options: FitBoundsOptions(
      //     padding: EdgeInsets.all(50),
      //     maxZoom: 18,
      //   ),
      // );

      // Calculate optimal zoom level based on bounds span
      final latSpan = _fieldBounds!.north - _fieldBounds!.south;
      final lngSpan = _fieldBounds!.east - _fieldBounds!.west;
      final maxSpan = latSpan > lngSpan ? latSpan : lngSpan;

      // Approximate zoom level calculation
      // Higher span = lower zoom, smaller span = higher zoom
      double calculatedZoom = 15.0;
      if (maxSpan > 0.01) {
        calculatedZoom = 13.0;
      } else if (maxSpan > 0.005) {
        calculatedZoom = 14.0;
      } else if (maxSpan > 0.001) {
        calculatedZoom = 16.0;
      } else {
        calculatedZoom = 17.0;
      }

      setState(() {
        _currentZoom = calculatedZoom;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.center_focus_strong, color: Colors.white),
              const SizedBox(width: 8),
              Text(
                'تم توسيط الخريطة على ${widget.fieldName ?? "الحقل"} (تكبير: ${calculatedZoom.toStringAsFixed(1)}x)',
              ),
            ],
          ),
          backgroundColor: const Color(0xFF367C2B),
          duration: const Duration(seconds: 2),
        ),
      );
    } else if (_fieldCenter != null) {
      // If we only have center point, use it
      // When MapLibre is integrated, use:
      // mapController.move(_fieldCenter!, _currentZoom);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              const Icon(Icons.center_focus_strong, color: Colors.white),
              const SizedBox(width: 8),
              Text(
                'تم توسيط الخريطة على ${widget.fieldName ?? "الحقل"}',
              ),
            ],
          ),
          backgroundColor: const Color(0xFF367C2B),
          duration: const Duration(seconds: 2),
        ),
      );
    } else {
      // No field data available yet
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Row(
            children: [
              Icon(Icons.info_outline, color: Colors.white),
              SizedBox(width: 8),
              Text('جاري تحميل بيانات الحقل...'),
            ],
          ),
          backgroundColor: Colors.orange,
          duration: Duration(seconds: 2),
        ),
      );
      // Retry loading field data
      _loadFieldData();
    }
  }

  /// Navigate to the crop health diagnosis dashboard
  /// This opens the NDVI-based crop health analysis screen
  /// where farmers can view diagnosis results, zone health status,
  /// and recommended actions for their field
  void _openDiagnosis() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => CropHealthDashboard(
          fieldId: widget.fieldId,
          fieldName: widget.fieldName,
        ),
      ),
    );
  }
}

/// رسام شبكة الخريطة
class _MapGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.green.withOpacity(0.1)
      ..strokeWidth = 1;

    // رسم خطوط أفقية
    for (var i = 0; i < size.height; i += 30) {
      canvas.drawLine(
        Offset(0, i.toDouble()),
        Offset(size.width, i.toDouble()),
        paint,
      );
    }

    // رسم خطوط عمودية
    for (var i = 0; i < size.width; i += 30) {
      canvas.drawLine(
        Offset(i.toDouble(), 0),
        Offset(i.toDouble(), size.height),
        paint,
      );
    }

    // رسم بعض المربعات لمحاكاة الحقول
    final fieldPaint = Paint()
      ..color = Colors.green.withOpacity(0.3)
      ..style = PaintingStyle.fill;

    final fieldRects = [
      Rect.fromLTWH(size.width * 0.2, size.height * 0.3, 100, 80),
      Rect.fromLTWH(size.width * 0.5, size.height * 0.2, 120, 100),
      Rect.fromLTWH(size.width * 0.3, size.height * 0.6, 90, 70),
    ];

    for (final rect in fieldRects) {
      canvas.drawRRect(
        RRect.fromRectAndRadius(rect, const Radius.circular(8)),
        fieldPaint,
      );
      canvas.drawRRect(
        RRect.fromRectAndRadius(rect, const Radius.circular(8)),
        Paint()
          ..color = Colors.green
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
