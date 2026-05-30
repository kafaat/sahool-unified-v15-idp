/// Satellite Time Series Tab - تبويب السلسلة الزمنية
library;

import 'dart:math' show Random;
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../../core/theme/sahool_theme.dart';

class SatelliteTimeseriesTab extends StatefulWidget {
  final String fieldId;

  const SatelliteTimeseriesTab({super.key, required this.fieldId});

  @override
  State<SatelliteTimeseriesTab> createState() => _SatelliteTimeseriesTabState();
}

class _SatelliteTimeseriesTabState extends State<SatelliteTimeseriesTab> {
  String _selectedPeriod = '30d';
  bool _loading = false;
  List<FlSpot> _spots = [];
  int? _touchedIndex;

  static const _periods = [
    _Period('7d', '7 أيام'),
    _Period('30d', '30 يوم'),
    _Period('90d', '90 يوم'),
    _Period('6m', '6 أشهر'),
    _Period('1y', 'سنة'),
  ];

  @override
  void initState() {
    super.initState();
    _spots = _generateMockData(_selectedPeriod);
  }

  List<FlSpot> _generateMockData(String period) {
    final count = period == '7d'
        ? 7
        : period == '30d'
            ? 30
            : period == '90d'
                ? 90
                : period == '6m'
                    ? 180
                    : 365;
    final random = Random(42);
    double ndvi = 0.55;
    return List.generate(count, (i) {
      ndvi += (random.nextDouble() - 0.45) * 0.05;
      ndvi = ndvi.clamp(0.2, 0.9);
      return FlSpot(i.toDouble(), double.parse(ndvi.toStringAsFixed(3)));
    });
  }

  void _changePeriod(String period) {
    setState(() {
      _selectedPeriod = period;
      _loading = true;
    });
    // Simulate network delay then use mock data
    Future.delayed(const Duration(milliseconds: 400), () {
      if (mounted) {
        setState(() {
          _spots = _generateMockData(period);
          _loading = false;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _buildPeriodSelector(),
        Expanded(
          child: _loading
              ? const Center(
                  child: CircularProgressIndicator(
                    valueColor: AlwaysStoppedAnimation<Color>(SahoolColors.primary),
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      _buildChart(),
                      const SizedBox(height: 16),
                      _buildStats(),
                    ],
                  ),
                ),
        ),
      ],
    );
  }

  Widget _buildPeriodSelector() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      child: Row(
        children: _periods.map((p) {
          final isSelected = _selectedPeriod == p.id;
          return Expanded(
            child: GestureDetector(
              onTap: () => _changePeriod(p.id),
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 3),
                padding: const EdgeInsets.symmetric(vertical: 8),
                decoration: BoxDecoration(
                  color: isSelected ? SahoolColors.primary : Colors.grey[100],
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  p.label,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: isSelected ? Colors.white : Colors.grey[700],
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildChart() {
    if (_spots.isEmpty) return const SizedBox.shrink();

    final minY = 0.0;
    final maxY = 1.0;

    return Container(
      padding: const EdgeInsets.fromLTRB(8, 20, 16, 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.only(right: 8, bottom: 12),
            child: Text(
              'السلسلة الزمنية لمؤشر NDVI',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
            ),
          ),
          SizedBox(
            height: 220,
            child: LineChart(
              LineChartData(
                minY: minY,
                maxY: maxY,
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  getDrawingHorizontalLine: (value) => FlLine(
                    color: Colors.grey[200]!,
                    strokeWidth: 1,
                  ),
                ),
                borderData: FlBorderData(
                  show: true,
                  border: Border(
                    bottom: BorderSide(color: Colors.grey[300]!, width: 1),
                    left: BorderSide(color: Colors.grey[300]!, width: 1),
                  ),
                ),
                titlesData: FlTitlesData(
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 36,
                      interval: 0.2,
                      getTitlesWidget: (value, meta) => Text(
                        value.toStringAsFixed(1),
                        style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                      ),
                    ),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 22,
                      interval: (_spots.length / 5).ceilToDouble(),
                      getTitlesWidget: (value, meta) {
                        final i = value.toInt();
                        if (i < 0 || i >= _spots.length) return const SizedBox.shrink();
                        return Text(
                          'ي${i + 1}',
                          style: TextStyle(fontSize: 9, color: Colors.grey[600]),
                        );
                      },
                    ),
                  ),
                ),
                lineTouchData: LineTouchData(
                  touchCallback: (event, response) {
                    setState(() {
                      _touchedIndex =
                          response?.lineBarSpots?.first.spotIndex;
                    });
                  },
                  touchTooltipData: LineTouchTooltipData(
                    getTooltipItems: (spots) => spots
                        .map(
                          (s) => LineTooltipItem(
                            'يوم ${(s.x + 1).toInt()}\n${s.y.toStringAsFixed(3)}',
                            const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                          ),
                        )
                        .toList(),
                  ),
                ),
                lineBarsData: [
                  LineChartBarData(
                    spots: _spots,
                    isCurved: true,
                    color: SahoolColors.primary,
                    barWidth: 2.5,
                    dotData: FlDotData(
                      show: _spots.length <= 30,
                      getDotPainter: (spot, percent, bar, index) =>
                          FlDotCirclePainter(
                        radius: 3,
                        color: SahoolColors.primary,
                        strokeWidth: 1,
                        strokeColor: Colors.white,
                      ),
                    ),
                    belowBarData: BarAreaData(
                      show: true,
                      color: SahoolColors.primary.withValues(alpha: 0.08),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStats() {
    if (_spots.isEmpty) return const SizedBox.shrink();

    final values = _spots.map((s) => s.y).toList();
    final avg = values.reduce((a, b) => a + b) / values.length;
    final min = values.reduce((a, b) => a < b ? a : b);
    final max = values.reduce((a, b) => a > b ? a : b);
    final last = values.last;

    return Row(
      children: [
        _buildStatCard('أحدث قيمة', last.toStringAsFixed(3), Colors.green),
        const SizedBox(width: 8),
        _buildStatCard('المتوسط', avg.toStringAsFixed(3), SahoolColors.primary),
        const SizedBox(width: 8),
        _buildStatCard('الأدنى', min.toStringAsFixed(3), Colors.red),
        const SizedBox(width: 8),
        _buildStatCard('الأعلى', max.toStringAsFixed(3), Colors.teal),
      ],
    );
  }

  Widget _buildStatCard(String label, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(10),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 6,
            ),
          ],
        ),
        child: Column(
          children: [
            Text(
              value,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(fontSize: 10, color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _Period {
  final String id;
  final String label;

  const _Period(this.id, this.label);
}
