/// Satellite Indices Tab - تبويب المؤشرات
library;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../../core/theme/sahool_theme.dart';

class SatelliteIndicesTab extends StatefulWidget {
  final String fieldId;

  const SatelliteIndicesTab({super.key, required this.fieldId});

  @override
  State<SatelliteIndicesTab> createState() => _SatelliteIndicesTabState();
}

class _SatelliteIndicesTabState extends State<SatelliteIndicesTab> {
  String _selectedIndex = 'ndvi';

  static const _indexGroups = [
    _IndexGroup('تحليل أساسي', [
      _IndexItem('hybrid', 'تحليل مدمج', Colors.purple),
      _IndexItem('colorblind', 'صديق عمى الألوان', Colors.indigo),
    ]),
    _IndexGroup('صورة حقيقية', [
      _IndexItem('tci', 'صورة اللون الحقيقي (TCI)', Colors.blueGrey),
      _IndexItem('etci', 'صورة اللون الحقيقي المحسّنة (ETCI)', Colors.cyan),
    ]),
    _IndexGroup('صحة المحصول (مبكر)', [
      _IndexItem('ndvi', 'مؤشر النباتات (NDVI)', Colors.green),
      _IndexItem('evi', 'مؤشر النباتات المحسّن (EVI)', Colors.teal),
      _IndexItem('savi', 'مؤشر النباتات المعدّل للتربة (SAVI)', Colors.lightGreen),
    ]),
    _IndexGroup('صحة المحصول (متأخر)', [
      _IndexItem('ndre', 'مؤشر الحافة الحمراء (NDRE)', Colors.red),
    ]),
    _IndexGroup('الري والمياه', [
      _IndexItem('ndwi', 'مؤشر المياه (NDWI)', Colors.blue),
      _IndexItem('ndmi', 'مؤشر رطوبة النباتات (NDMI)', Colors.lightBlue),
      _IndexItem('evapotranspiration', 'التبخر والنتح (ET)', Colors.blueAccent),
    ]),
    _IndexGroup('صحة التربة', [
      _IndexItem('soc', 'الكربون العضوي (SOC)', Colors.brown),
    ]),
    _IndexGroup('تحليل متقدم', [
      _IndexItem('erosion', 'تآكل التربة', Colors.deepOrange),
    ]),
    _IndexGroup('التضاريس والرادار', [
      _IndexItem('dem', 'نموذج الارتفاع الرقمي (DEM)', Colors.grey),
      _IndexItem('sar_rvi', 'رادار الغطاء النباتي (SAR-RVI)', Colors.lime),
      _IndexItem('sar_rsm', 'رطوبة التربة بالرادار (SAR-RSM)', Colors.amber),
    ]),
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _buildSelectedPreview(),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            children: _indexGroups.map(_buildGroup).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildSelectedPreview() {
    // Find selected item display name
    String selectedName = _selectedIndex.toUpperCase();
    Color selectedColor = SahoolColors.primary;
    for (final group in _indexGroups) {
      for (final item in group.items) {
        if (item.id == _selectedIndex) {
          selectedName = item.nameAr;
          selectedColor = item.color;
          break;
        }
      }
    }

    return Container(
      color: Colors.grey[100],
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  color: selectedColor,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  selectedName,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Container(
            height: 160,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: selectedColor, width: 2),
            ),
            clipBehavior: Clip.antiAlias,
            child: FlutterMap(
              options: const MapOptions(
                initialCenter: LatLng(23.8859, 45.0792),
                initialZoom: 12,
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.sahool.app',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGroup(_IndexGroup group) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      child: ExpansionTile(
        title: Text(
          group.nameAr,
          style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
        iconColor: SahoolColors.primary,
        collapsedIconColor: Colors.grey[600],
        children: group.items.map(_buildIndexTile).toList(),
      ),
    );
  }

  Widget _buildIndexTile(_IndexItem item) {
    final isSelected = _selectedIndex == item.id;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8),
        border: isSelected
            ? Border.all(color: SahoolColors.primary, width: 1.5)
            : null,
        color: isSelected
            ? SahoolColors.primary.withValues(alpha: 0.06)
            : null,
      ),
      child: ListTile(
        dense: true,
        leading: Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: item.color,
            shape: BoxShape.circle,
          ),
        ),
        title: Text(
          item.nameAr,
          style: TextStyle(
            fontSize: 13,
            color: isSelected ? SahoolColors.primary : Colors.black87,
            fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
          ),
        ),
        trailing: isSelected
            ? const Icon(Icons.check_circle, color: SahoolColors.primary, size: 18)
            : null,
        onTap: () => setState(() => _selectedIndex = item.id),
      ),
    );
  }
}

class _IndexGroup {
  final String nameAr;
  final List<_IndexItem> items;

  const _IndexGroup(this.nameAr, this.items);
}

class _IndexItem {
  final String id;
  final String nameAr;
  final Color color;

  const _IndexItem(this.id, this.nameAr, this.color);
}
