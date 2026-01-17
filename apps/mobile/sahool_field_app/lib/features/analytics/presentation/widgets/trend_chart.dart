/// Trend Chart Widget
/// ودجت مخطط الاتجاهات
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../providers/analytics_providers.dart';

/// Displays historical trend data as a line chart
/// يعرض بيانات الاتجاه التاريخية كمخطط خطي
class TrendChart extends ConsumerWidget {
  final String metricName;
  final String fieldId;
  final int days;

  const TrendChart({
    super.key,
    required this.metricName,
    required this.fieldId,
    this.days = 30,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final trendAsync = ref.watch(
      historicalTrendProvider(
        HistoricalTrendParams(
          fieldId: fieldId,
          metricName: metricName,
          days: days,
        ),
      ),
    );

    return trendAsync.when(
      data: (trend) => _buildChart(context, trend),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, _) => Center(
        child: Text(
          'Error: $error',
          style: const TextStyle(color: Colors.red),
        ),
      ),
    );
  }

  Widget _buildChart(BuildContext context, dynamic trend) {
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final dataPoints = trend.dataPoints;

    if (dataPoints.isEmpty) {
      return Center(
        child: Text(isRtl ? 'لا توجد بيانات' : 'No data available'),
      );
    }

    // Convert data points to FlSpot
    final spots = <FlSpot>[];
    for (int i = 0; i < dataPoints.length; i++) {
      spots.add(FlSpot(i.toDouble(), dataPoints[i].value));
    }

    // Calculate min/max for Y axis
    final values = dataPoints.map((d) => d.value).toList();
    final minY = values.reduce((a, b) => a < b ? a : b) - 10;
    final maxY = values.reduce((a, b) => a > b ? a : b) + 10;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  isRtl ? trend.metricNameAr : trend.metricName,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                _buildChangeIndicator(trend.changePercent, trend.trend, isRtl),
              ],
            ),
            const SizedBox(height: 16),
            Expanded(
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: 20,
                    getDrawingHorizontalLine: (value) => FlLine(
                      color: Colors.grey.shade200,
                      strokeWidth: 1,
                    ),
                  ),
                  titlesData: FlTitlesData(
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 40,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            value.toStringAsFixed(0),
                            style: const TextStyle(
                              fontSize: 10,
                              color: Colors.grey,
                            ),
                          );
                        },
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 30,
                        interval: (dataPoints.length / 5).ceil().toDouble(),
                        getTitlesWidget: (value, meta) {
                          final index = value.toInt();
                          if (index >= 0 && index < dataPoints.length) {
                            return Padding(
                              padding: const EdgeInsets.only(top: 8),
                              child: Text(
                                DateFormat('d/M').format(dataPoints[index].date),
                                style: const TextStyle(
                                  fontSize: 10,
                                  color: Colors.grey,
                                ),
                              ),
                            );
                          }
                          return const SizedBox();
                        },
                      ),
                    ),
                  ),
                  borderData: FlBorderData(
                    show: true,
                    border: Border(
                      bottom: BorderSide(color: Colors.grey.shade300),
                      left: BorderSide(color: Colors.grey.shade300),
                    ),
                  ),
                  minX: 0,
                  maxX: (dataPoints.length - 1).toDouble(),
                  minY: minY.clamp(0, 100),
                  maxY: maxY.clamp(0, 100),
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      curveSmoothness: 0.3,
                      color: _getTrendColor(trend.trend),
                      barWidth: 3,
                      isStrokeCapRound: true,
                      dotData: const FlDotData(show: false),
                      belowBarData: BarAreaData(
                        show: true,
                        color: _getTrendColor(trend.trend).withOpacity(0.1),
                      ),
                    ),
                  ],
                  lineTouchData: LineTouchData(
                    enabled: true,
                    touchTooltipData: LineTouchTooltipData(
                      getTooltipItems: (touchedSpots) {
                        return touchedSpots.map((spot) {
                          final index = spot.spotIndex;
                          final date = dataPoints[index].date;
                          return LineTooltipItem(
                            '${DateFormat('d MMM').format(date)}\n${spot.y.toStringAsFixed(1)}',
                            const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                            ),
                          );
                        }).toList();
                      },
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChangeIndicator(double changePercent, dynamic trend, bool isRtl) {
    final isPositive = changePercent >= 0;
    final color = _getTrendColor(trend);
    final icon = isPositive ? Icons.arrow_upward : Icons.arrow_downward;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 16),
        const SizedBox(width: 4),
        Text(
          '${isPositive ? '+' : ''}${changePercent.toStringAsFixed(1)}%',
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Color _getTrendColor(dynamic trend) {
    final trendStr = trend.toString();
    if (trendStr.contains('improving')) return Colors.green;
    if (trendStr.contains('declining')) return Colors.red;
    return Colors.amber;
  }
}
