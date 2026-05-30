/// Satellite Zones Tab - تبويب تحليل المناطق
library;

import 'dart:math' show Random;
import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';

class SatelliteZonesTab extends StatefulWidget {
  final String fieldId;

  const SatelliteZonesTab({super.key, required this.fieldId});

  @override
  State<SatelliteZonesTab> createState() => _SatelliteZonesTabState();
}

class _SatelliteZonesTabState extends State<SatelliteZonesTab> {
  bool _loading = false;
  late final List<_ZoneData> _zones;

  // Zone order for 3×3 grid: NW N NE / W C E / SW S SE
  static const _zoneIds = ['NW', 'N', 'NE', 'W', 'C', 'E', 'SW', 'S', 'SE'];
  static const _zoneLabels = {
    'NW': 'شمال غرب',
    'N': 'شمال',
    'NE': 'شمال شرق',
    'W': 'غرب',
    'C': 'مركز',
    'E': 'شرق',
    'SW': 'جنوب غرب',
    'S': 'جنوب',
    'SE': 'جنوب شرق',
  };

  @override
  void initState() {
    super.initState();
    _zones = _generateMockZones();
  }

  List<_ZoneData> _generateMockZones() {
    final rng = Random(7);
    return _zoneIds.map((id) {
      final ndvi = 0.3 + rng.nextDouble() * 0.55;
      return _ZoneData(
        id: id,
        label: _zoneLabels[id]!,
        ndvi: double.parse(ndvi.toStringAsFixed(2)),
      );
    }).toList();
  }

  String _healthLabel(double ndvi) {
    if (ndvi >= 0.6) return 'صحي';
    if (ndvi >= 0.4) return 'متوسط';
    if (ndvi >= 0.2) return 'مجهد';
    return 'حرج';
  }

  Color _healthColor(double ndvi) {
    if (ndvi >= 0.6) return Colors.green;
    if (ndvi >= 0.4) return Colors.amber;
    if (ndvi >= 0.2) return Colors.orange;
    return Colors.red;
  }

  bool _needsIrrigation(double ndvi) => ndvi < 0.5;

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(
          valueColor: AlwaysStoppedAnimation<Color>(SahoolColors.primary),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildHeader(),
          const SizedBox(height: 16),
          _buildGrid(),
          const SizedBox(height: 16),
          _buildLegend(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    final alertCount = _zones.where((z) => z.ndvi < 0.4).length;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(Icons.grid_view, color: SahoolColors.primary, size: 28),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'تحليل مناطق الحقل',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                Text(
                  '9 مناطق • ${alertCount > 0 ? "$alertCount تحتاج انتباه" : "جميعها بحالة جيدة"}',
                  style: TextStyle(
                    color: alertCount > 0 ? Colors.orange : Colors.green,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGrid() {
    return AspectRatio(
      aspectRatio: 1.0,
      child: GridView.count(
        crossAxisCount: 3,
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
        children: _zones.map(_buildZoneCard).toList(),
      ),
    );
  }

  Widget _buildZoneCard(_ZoneData zone) {
    final color = _healthColor(zone.ndvi);
    final needsIrrigation = _needsIrrigation(zone.ndvi);

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.4), width: 1.5),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            zone.label,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: Colors.grey[700],
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 4),
          Text(
            zone.ndvi.toStringAsFixed(2),
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            _healthLabel(zone.ndvi),
            style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: needsIrrigation
                  ? Colors.blue.withValues(alpha: 0.15)
                  : Colors.green.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              needsIrrigation ? 'يحتاج ري' : 'لا يحتاج',
              style: TextStyle(
                fontSize: 9,
                color: needsIrrigation ? Colors.blue[700] : Colors.green[700],
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLegend() {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'مقياس التصنيف',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
          ),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _legendItem(Colors.green, 'صحي', '≥ 0.60'),
              _legendItem(Colors.amber, 'متوسط', '0.40-0.60'),
              _legendItem(Colors.orange, 'مجهد', '0.20-0.40'),
              _legendItem(Colors.red, 'حرج', '< 0.20'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _legendItem(Color color, String label, String range) {
    return Column(
      children: [
        Container(
          width: 14,
          height: 14,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(height: 3),
        Text(label, style: TextStyle(fontSize: 11, color: Colors.grey[700])),
        Text(range, style: TextStyle(fontSize: 9, color: Colors.grey[500])),
      ],
    );
  }
}

class _ZoneData {
  final String id;
  final String label;
  final double ndvi;

  const _ZoneData({required this.id, required this.label, required this.ndvi});
}
