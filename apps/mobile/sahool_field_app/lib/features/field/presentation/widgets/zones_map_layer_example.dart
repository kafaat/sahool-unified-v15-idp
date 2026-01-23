/// Example usage of ZonesMapLayer widget
/// مثال على استخدام widget طبقة خريطة المناطق
///
/// This file demonstrates various use cases for the ZonesMapLayer widget

library;

import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';

import '../../../../core/theme/sahool_theme.dart';
import 'zones_map_layer.dart';

/// Example screen showing zones map
class ZonesMapExample extends StatefulWidget {
  const ZonesMapExample({super.key});

  @override
  State<ZonesMapExample> createState() => _ZonesMapExampleState();
}

class _ZonesMapExampleState extends State<ZonesMapExample> {
  ZoneHealth? _selectedZone;
  bool _isLoading = false;

  // Example zones data (Riyadh region)
  final List<ZoneHealth> _exampleZones = [
    ZoneHealth(
      id: 'zone_1',
      name: 'North Zone',
      nameAr: 'المنطقة الشمالية',
      ndvi: 0.75,
      areaHectares: 2.5,
      boundary: [
        const LatLng(24.7150, 46.6750),
        const LatLng(24.7160, 46.6750),
        const LatLng(24.7160, 46.6770),
        const LatLng(24.7150, 46.6770),
        const LatLng(24.7150, 46.6750),
      ],
      trend: 'up',
      recommendations: [
        'Maintain current irrigation schedule',
        'Monitor for pest activity',
      ],
      recommendationsAr: [
        'الحفاظ على جدول الري الحالي',
        'مراقبة نشاط الآفات',
      ],
      lastUpdated: DateTime.now().subtract(const Duration(hours: 6)),
    ),
    ZoneHealth(
      id: 'zone_2',
      name: 'South Zone',
      nameAr: 'المنطقة الجنوبية',
      ndvi: 0.52,
      areaHectares: 3.2,
      boundary: [
        const LatLng(24.7130, 46.6750),
        const LatLng(24.7140, 46.6750),
        const LatLng(24.7140, 46.6770),
        const LatLng(24.7130, 46.6770),
        const LatLng(24.7130, 46.6750),
      ],
      trend: 'stable',
      recommendations: [
        'Increase irrigation by 15%',
        'Consider fertilization in 2 weeks',
      ],
      recommendationsAr: [
        'زيادة الري بنسبة 15%',
        'النظر في التسميد خلال أسبوعين',
      ],
      lastUpdated: DateTime.now().subtract(const Duration(hours: 6)),
    ),
    ZoneHealth(
      id: 'zone_3',
      name: 'West Zone',
      nameAr: 'المنطقة الغربية',
      ndvi: 0.32,
      areaHectares: 1.8,
      boundary: [
        const LatLng(24.7140, 46.6730),
        const LatLng(24.7150, 46.6730),
        const LatLng(24.7150, 46.6745),
        const LatLng(24.7140, 46.6745),
        const LatLng(24.7140, 46.6730),
      ],
      trend: 'down',
      recommendations: [
        'URGENT: Increase irrigation immediately',
        'Check soil moisture levels',
        'Investigate potential disease or pest issues',
        'Consider adding organic matter',
      ],
      recommendationsAr: [
        'عاجل: زيادة الري فوراً',
        'فحص مستويات رطوبة التربة',
        'التحقق من احتمال وجود أمراض أو آفات',
        'النظر في إضافة مواد عضوية',
      ],
      lastUpdated: DateTime.now().subtract(const Duration(hours: 6)),
    ),
    ZoneHealth(
      id: 'zone_4',
      name: 'East Zone',
      nameAr: 'المنطقة الشرقية',
      ndvi: 0.68,
      areaHectares: 2.9,
      boundary: [
        const LatLng(24.7140, 46.6775),
        const LatLng(24.7150, 46.6775),
        const LatLng(24.7150, 46.6790),
        const LatLng(24.7140, 46.6790),
        const LatLng(24.7140, 46.6775),
      ],
      trend: 'up',
      recommendations: [
        'Continue current management practices',
        'Prepare for harvest in 4-6 weeks',
      ],
      recommendationsAr: [
        'الاستمرار في ممارسات الإدارة الحالية',
        'الاستعداد للحصاد خلال 4-6 أسابيع',
      ],
      lastUpdated: DateTime.now().subtract(const Duration(hours: 6)),
    ),
  ];

  void _handleZoneTap(ZoneHealth zone) {
    setState(() {
      _selectedZone = zone;
    });
  }

  void _simulateLoading() async {
    setState(() {
      _isLoading = true;
    });

    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: AppBar(
        title: const Text('Health Zones Map - خريطة المناطق الصحية'),
        backgroundColor: Colors.white,
        foregroundColor: SahoolColors.forestGreen,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _simulateLoading,
            tooltip: 'Refresh zones',
          ),
        ],
      ),
      body: Column(
        children: [
          // Info banner
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            color: SahoolColors.paleOlive,
            child: const Row(
              children: [
                Icon(
                  Icons.info_outline,
                  color: SahoolColors.forestGreen,
                  size: 20,
                ),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Tap on any zone to view detailed information',
                    style: TextStyle(
                      color: SahoolColors.forestGreen,
                      fontSize: 13,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Map container
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: ZonesMapLayer(
                zones: _exampleZones,
                selectedZone: _selectedZone,
                onZoneTapped: _handleZoneTap,
                initialCenter: const LatLng(24.7145, 46.6760),
                initialZoom: 15.0,
                showLabels: true,
                isLoading: _isLoading,
                enableSelection: true,
              ),
            ),
          ),

          // Selected zone info
          if (_selectedZone != null && !_isLoading)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    width: 8,
                    height: 60,
                    decoration: BoxDecoration(
                      color: _selectedZone!.healthStatus == HealthStatus.healthy
                          ? SahoolColors.sageGreen
                          : _selectedZone!.healthStatus ==
                                  HealthStatus.moderate
                              ? SahoolColors.harvestGold
                              : SahoolColors.danger,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${_selectedZone!.name} (${_selectedZone!.nameAr})',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: SahoolColors.forestGreen,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'NDVI: ${_selectedZone!.ndvi.toStringAsFixed(2)} • ${_selectedZone!.areaHectares.toStringAsFixed(1)} ha',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey[700],
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () {
                      setState(() {
                        _selectedZone = null;
                      });
                    },
                  ),
                ],
              ),
            ),

          // Statistics summary
          if (!_isLoading)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              color: SahoolColors.warmCream,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _StatItem(
                    label: 'Total Zones',
                    value: _exampleZones.length.toString(),
                    color: SahoolColors.forestGreen,
                  ),
                  _StatItem(
                    label: 'Healthy',
                    value: _exampleZones
                        .where((z) => z.healthStatus == HealthStatus.healthy)
                        .length
                        .toString(),
                    color: SahoolColors.sageGreen,
                  ),
                  _StatItem(
                    label: 'Moderate',
                    value: _exampleZones
                        .where((z) => z.healthStatus == HealthStatus.moderate)
                        .length
                        .toString(),
                    color: SahoolColors.harvestGold,
                  ),
                  _StatItem(
                    label: 'Critical',
                    value: _exampleZones
                        .where((z) => z.healthStatus == HealthStatus.critical)
                        .length
                        .toString(),
                    color: SahoolColors.danger,
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

/// Statistic item widget
class _StatItem extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _StatItem({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: color.withOpacity(0.15),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey[700],
          ),
        ),
      ],
    );
  }
}
