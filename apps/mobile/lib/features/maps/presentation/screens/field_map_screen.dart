import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

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
    // In production, use flutter_map with vector_map_tiles
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

  void _centerOnField() {
    // TODO: Center map on field bounds
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('توسيط على الحقل')),
    );
  }

  void _openDiagnosis() {
    // TODO: Navigate to diagnosis screen
    Navigator.pushNamed(
      context,
      '/crop-health',
      arguments: {'fieldId': widget.fieldId},
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
