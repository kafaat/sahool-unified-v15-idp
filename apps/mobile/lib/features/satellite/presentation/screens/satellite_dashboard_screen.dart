/// Satellite Dashboard Screen - شاشة لوحة الأقمار الصناعية
/// 8-tab layout for comprehensive satellite monitoring
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../widgets/satellite_overview_tab.dart';
import '../widgets/satellite_indices_tab.dart';
import '../widgets/satellite_timeseries_tab.dart';
import '../widgets/satellite_zones_tab.dart';
import '../widgets/satellite_soil_tab.dart';
import '../widgets/satellite_alerts_tab.dart';
import '../widgets/satellite_weather_tab.dart';
import '../widgets/satellite_yield_tab.dart';

class SatelliteDashboardScreen extends StatelessWidget {
  final String fieldId;
  final String fieldName;

  const SatelliteDashboardScreen({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 8,
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            fieldName.isNotEmpty ? fieldName : 'مراقبة الأقمار الصناعية',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          centerTitle: true,
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          bottom: const TabBar(
            isScrollable: true,
            indicatorColor: Colors.white,
            indicatorWeight: 3,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white60,
            labelStyle: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
            unselectedLabelStyle: TextStyle(fontSize: 12),
            tabs: [
              Tab(text: 'نظرة عامة'),
              Tab(text: 'المؤشرات'),
              Tab(text: 'السلسلة الزمنية'),
              Tab(text: 'تحليل المناطق'),
              Tab(text: 'التربة'),
              Tab(text: 'التنبيهات'),
              Tab(text: 'الطقس'),
              Tab(text: 'الإنتاجية'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            SatelliteOverviewTab(fieldId: fieldId),
            SatelliteIndicesTab(fieldId: fieldId),
            SatelliteTimeseriesTab(fieldId: fieldId),
            SatelliteZonesTab(fieldId: fieldId),
            SatelliteSoilTab(fieldId: fieldId),
            SatelliteAlertsTab(fieldId: fieldId),
            SatelliteWeatherTab(fieldId: fieldId),
            SatelliteYieldTab(fieldId: fieldId),
          ],
        ),
      ),
    );
  }
}
