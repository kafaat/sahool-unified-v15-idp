/// Zone Map Widget - خريطة المناطق
library;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../models/vra_models.dart';

/// خريطة تعرض المناطق مع الألوان والمعدلات
class ZoneMapWidget extends StatefulWidget {
  final List<ManagementZone> zones;
  final List<ApplicationRate> rates;
  final ManagementZone? selectedZone;
  final void Function(ManagementZone)? onZoneSelected;

  const ZoneMapWidget({
    super.key,
    required this.zones,
    required this.rates,
    this.selectedZone,
    this.onZoneSelected,
  });

  @override
  State<ZoneMapWidget> createState() => _ZoneMapWidgetState();
}

class _ZoneMapWidgetState extends State<ZoneMapWidget> {
  final MapController _mapController = MapController();
  ManagementZone? _hoveredZone;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fitBounds();
    });
  }

  void _fitBounds() {
    if (widget.zones.isEmpty) return;

    // حساب الحدود من جميع المناطق
    double minLat = double.infinity;
    double maxLat = -double.infinity;
    double minLng = double.infinity;
    double maxLng = -double.infinity;

    for (final zone in widget.zones) {
      final coordinates = _extractCoordinates(zone.geometry);
      for (final coord in coordinates) {
        if (coord.latitude < minLat) minLat = coord.latitude;
        if (coord.latitude > maxLat) maxLat = coord.latitude;
        if (coord.longitude < minLng) minLng = coord.longitude;
        if (coord.longitude > maxLng) maxLng = coord.longitude;
      }
    }

    if (minLat != double.infinity && maxLat != -double.infinity) {
      final bounds = LatLngBounds(
        LatLng(minLat, minLng),
        LatLng(maxLat, maxLng),
      );

      _mapController.fitCamera(
        CameraFit.bounds(
          bounds: bounds,
          padding: const EdgeInsets.all(50),
        ),
      );
    }
  }

  List<LatLng> _extractCoordinates(Map<String, dynamic> geometry) {
    final type = geometry['type'] as String;
    final coordinates = geometry['coordinates'];

    if (type == 'Polygon') {
      // Polygon coordinates are [[[lng, lat], [lng, lat], ...]]
      final ring = coordinates[0] as List;
      return ring.map((coord) {
        final c = coord as List;
        return LatLng(c[1] as double, c[0] as double);
      }).toList();
    } else if (type == 'MultiPolygon') {
      // MultiPolygon coordinates are [[[[lng, lat], [lng, lat], ...]]]
      final firstPolygon = coordinates[0] as List;
      final ring = firstPolygon[0] as List;
      return ring.map((coord) {
        final c = coord as List;
        return LatLng(c[1] as double, c[0] as double);
      }).toList();
    }

    return [];
  }

  Color _getZoneColor(ManagementZone zone, int index) {
    // تدرج من الأحمر للأصفر للأخضر بناءً على معدل التطبيق
    final rate = widget.rates.firstWhere(
      (r) => r.zoneId == zone.zoneId,
      orElse: () => ApplicationRate(
        rateId: '',
        zoneId: zone.zoneId,
        rate: 0,
        unit: '',
      ),
    );

    if (widget.rates.isEmpty) {
      // إذا لم يكن هناك معدلات، استخدم ألوان متدرجة بناءً على رقم المنطقة
      final hue = (index * 360 / widget.zones.length) % 360;
      return HSLColor.fromAHSL(0.6, hue, 0.7, 0.5).toColor();
    }

    // حساب نطاق المعدلات
    final allRates = widget.rates.map((r) => r.rate).toList();
    final minRate = allRates.reduce((a, b) => a < b ? a : b);
    final maxRate = allRates.reduce((a, b) => a > b ? a : b);

    // تطبيع المعدل
    double normalizedRate;
    if (maxRate == minRate) {
      normalizedRate = 0.5;
    } else {
      normalizedRate = (rate.rate - minRate) / (maxRate - minRate);
    }

    // تدرج من الأخضر (منخفض) إلى الأحمر (مرتفع)
    final hue = (1 - normalizedRate) * 120; // 120 = green, 0 = red
    return HSLColor.fromAHSL(0.6, hue, 0.8, 0.5).toColor();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.zones.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.map_outlined, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'No zones to display',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      );
    }

    return Stack(
      children: [
        FlutterMap(
          mapController: _mapController,
          options: MapOptions(
            initialCenter: const LatLng(24.7136, 46.6753), // Riyadh
            initialZoom: 13,
            interactionOptions: const InteractionOptions(
              flags: InteractiveFlag.all & ~InteractiveFlag.rotate,
            ),
          ),
          children: [
            // طبقة الخريطة الأساسية
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.sahool.unified',
            ),

            // طبقة المناطق
            PolygonLayer(
              polygons: widget.zones.asMap().entries.map((entry) {
                final index = entry.key;
                final zone = entry.value;
                final coordinates = _extractCoordinates(zone.geometry);

                final isSelected = widget.selectedZone?.zoneId == zone.zoneId;
                final isHovered = _hoveredZone?.zoneId == zone.zoneId;

                return Polygon(
                  points: coordinates,
                  color: _getZoneColor(zone, index),
                  borderColor: isSelected
                      ? Colors.blue
                      : isHovered
                          ? Colors.black
                          : Colors.white,
                  borderStrokeWidth: isSelected ? 3 : isHovered ? 2 : 1,
                  isFilled: true,
                );
              }).toList(),
            ),

            // طبقة التسميات
            MarkerLayer(
              markers: widget.zones.map((zone) {
                final coordinates = _extractCoordinates(zone.geometry);
                if (coordinates.isEmpty) return null;

                // حساب مركز المنطقة
                final center = _calculateCentroid(coordinates);

                return Marker(
                  point: center,
                  width: 80,
                  height: 40,
                  child: GestureDetector(
                    onTap: () {
                      if (widget.onZoneSelected != null) {
                        widget.onZoneSelected!(zone);
                      }
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.9),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(color: Colors.black54),
                      ),
                      child: Center(
                        child: Text(
                          'Zone ${zone.zoneNumber}',
                          style: const TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                  ),
                );
              }).whereType<Marker>().toList(),
            ),
          ],
        ),

        // معلومات المنطقة عند التحويم (للأجهزة اللوحية/سطح المكتب)
        if (_hoveredZone != null)
          Positioned(
            top: 16,
            right: 16,
            child: _buildZoneInfoCard(_hoveredZone!),
          ),
      ],
    );
  }

  Widget _buildZoneInfoCard(ManagementZone zone) {
    final locale = Localizations.localeOf(context).languageCode;
    final isRTL = locale == 'ar';

    final rate = widget.rates.firstWhere(
      (r) => r.zoneId == zone.zoneId,
      orElse: () => ApplicationRate(
        rateId: '',
        zoneId: zone.zoneId,
        rate: 0,
        unit: '',
      ),
    );

    return Card(
      elevation: 4,
      child: Container(
        padding: const EdgeInsets.all(12),
        constraints: const BoxConstraints(maxWidth: 200),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              zone.getDisplayName(locale),
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
            const Divider(),
            _buildInfoRow(
              isRTL ? 'المساحة' : 'Area',
              '${zone.area.toStringAsFixed(2)} ${isRTL ? 'هكتار' : 'ha'}',
            ),
            if (widget.rates.isNotEmpty)
              _buildInfoRow(
                isRTL ? 'المعدل' : 'Rate',
                '${rate.rate.toStringAsFixed(2)} ${rate.getUnit(locale)}',
              ),
            if (zone.averageNdvi != null)
              _buildInfoRow(
                isRTL ? 'NDVI' : 'NDVI',
                zone.averageNdvi!.toStringAsFixed(3),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontSize: 11)),
          Text(
            value,
            style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  LatLng _calculateCentroid(List<LatLng> coordinates) {
    if (coordinates.isEmpty) return const LatLng(0, 0);

    double sumLat = 0;
    double sumLng = 0;

    for (final coord in coordinates) {
      sumLat += coord.latitude;
      sumLng += coord.longitude;
    }

    return LatLng(
      sumLat / coordinates.length,
      sumLng / coordinates.length,
    );
  }
}
