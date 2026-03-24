/// Chart Widget - ودجت الرسوم البيانية
/// Reusable chart component supporting multiple chart types
library;

import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/chart_config.dart';

/// Universal Chart Widget
/// ودجت الرسم البياني الموحد
class ChartWidget extends StatelessWidget {
  final ChartConfig config;
  final double? height;

  const ChartWidget({
    super.key,
    required this.config,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    if (!config.hasData) {
      return _buildEmptyState();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Chart title
        if (config.title.isNotEmpty) ...[
          Text(
            config.titleAr,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          if (config.subtitle != null) ...[
            const SizedBox(height: 4),
            Text(
              config.subtitleAr ?? config.subtitle!,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 13,
              ),
            ),
          ],
          const SizedBox(height: 16),
        ],

        // Chart
        SizedBox(
          height: height ?? 250,
          child: _buildChart(),
        ),

        // Legend
        if (config.showLegend && config.series.length > 1) ...[
          const SizedBox(height: 16),
          _buildLegend(),
        ],
      ],
    );
  }

  Widget _buildChart() {
    switch (config.type) {
      case ChartType.line:
      case ChartType.area:
        return _buildLineChart();
      case ChartType.bar:
      case ChartType.stackedBar:
        return _buildBarChart();
      case ChartType.pie:
      case ChartType.doughnut:
        return _buildPieChart();
      case ChartType.scatter:
        return _buildScatterChart();
      case ChartType.radar:
        return _buildRadarChart();
      case ChartType.combined:
        return _buildLineChart(); // Combined uses line chart base
    }
  }

  Widget _buildLineChart() {
    final spots = <LineChartBarData>[];

    for (int i = 0; i < config.series.length; i++) {
      final series = config.series[i];
      final color = _parseColor(series.colorHex);

      spots.add(LineChartBarData(
        spots: series.dataPoints
            .asMap()
            .entries
            .map((e) => FlSpot(e.key.toDouble(), e.value.y))
            .toList(),
        isCurved: true,
        curveSmoothness: 0.35,
        color: color,
        barWidth: series.isDashed ? 2 : 3,
        dotData: FlDotData(
          show: config.showDataLabels,
          getDotPainter: (spot, percent, bar, index) => FlDotCirclePainter(
            radius: 4,
            color: color,
            strokeWidth: 2,
            strokeColor: Colors.white,
          ),
        ),
        belowBarData: (config.type == ChartType.area || series.fillArea)
            ? BarAreaData(
                show: true,
                color: color.withValues(alpha: 0.2),
              )
            : null,
        dashArray: series.isDashed ? [5, 5] : null,
      ));
    }

    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: config.yAxis?.interval,
          getDrawingHorizontalLine: (value) => FlLine(
            color: Colors.grey.withValues(alpha: 0.1),
            strokeWidth: 1,
          ),
        ),
        titlesData: _buildTitlesData(),
        borderData: FlBorderData(show: false),
        minY: config.yAxis?.min,
        maxY: config.yAxis?.max,
        lineBarsData: spots,
        lineTouchData: config.showTooltips
            ? LineTouchData(
                enabled: true,
                touchTooltipData: LineTouchTooltipData(
                  getTooltipColor: (_) => SahoolColors.primary.withValues(alpha: 0.9),
                  tooltipRoundedRadius: 8,
                  getTooltipItems: (touchedSpots) {
                    return touchedSpots.map((spot) {
                      final seriesIndex = spots.indexOf(spot.bar);
                      final series = config.series[seriesIndex];
                      return LineTooltipItem(
                        '${series.nameAr}: ${spot.y.toStringAsFixed(2)}',
                        const TextStyle(color: Colors.white, fontSize: 12),
                      );
                    }).toList();
                  },
                ),
              )
            : const LineTouchData(enabled: false),
      ),
      duration: config.enableAnimations
          ? Duration(milliseconds: config.animationDuration)
          : Duration.zero,
    );
  }

  Widget _buildBarChart() {
    if (config.series.isEmpty || config.series.first.dataPoints.isEmpty) {
      return _buildEmptyState();
    }

    final groups = <BarChartGroupData>[];
    final firstSeries = config.series.first;

    for (int i = 0; i < firstSeries.dataPoints.length; i++) {
      final rods = <BarChartRodData>[];

      for (int j = 0; j < config.series.length; j++) {
        final series = config.series[j];
        if (i < series.dataPoints.length) {
          rods.add(BarChartRodData(
            toY: series.dataPoints[i].y,
            color: _parseColor(series.colorHex),
            width: config.series.length > 1 ? 12 : 20,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
          ));
        }
      }

      groups.add(BarChartGroupData(
        x: i,
        barRods: rods,
        barsSpace: 4,
      ));
    }

    return BarChart(
      BarChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: config.yAxis?.interval,
          getDrawingHorizontalLine: (value) => FlLine(
            color: Colors.grey.withValues(alpha: 0.1),
            strokeWidth: 1,
          ),
        ),
        titlesData: _buildBarTitlesData(),
        borderData: FlBorderData(show: false),
        barGroups: groups,
        barTouchData: config.showTooltips
            ? BarTouchData(
                enabled: true,
                touchTooltipData: BarTouchTooltipData(
                  getTooltipColor: (_) => SahoolColors.primary.withValues(alpha: 0.9),
                  tooltipRoundedRadius: 8,
                  getTooltipItem: (group, groupIndex, rod, rodIndex) {
                    final series = config.series[rodIndex];
                    return BarTooltipItem(
                      '${series.nameAr}: ${rod.toY.toStringAsFixed(1)}',
                      const TextStyle(color: Colors.white, fontSize: 12),
                    );
                  },
                ),
              )
            : BarTouchData(enabled: false),
      ),
      duration: config.enableAnimations
          ? Duration(milliseconds: config.animationDuration)
          : Duration.zero,
    );
  }

  Widget _buildPieChart() {
    if (config.series.isEmpty || config.series.first.dataPoints.isEmpty) {
      return _buildEmptyState();
    }

    final sections = <PieChartSectionData>[];
    final dataPoints = config.series.first.dataPoints;
    final total = dataPoints.fold<double>(0, (sum, point) => sum + point.y);

    for (int i = 0; i < dataPoints.length; i++) {
      final point = dataPoints[i];
      final percentage = (point.y / total * 100);
      final color = point.colorHex != null
          ? _parseColor(point.colorHex!)
          : _getDefaultColor(i);

      sections.add(PieChartSectionData(
        value: point.y,
        title: config.showDataLabels ? '${percentage.toStringAsFixed(0)}%' : '',
        color: color,
        radius: config.type == ChartType.doughnut ? 60 : 100,
        titleStyle: const TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ));
    }

    return PieChart(
      PieChartData(
        sections: sections,
        centerSpaceRadius: config.type == ChartType.doughnut ? 50 : 0,
        sectionsSpace: 2,
        pieTouchData: config.showTooltips
            ? PieTouchData(
                enabled: true,
                touchCallback: (event, response) {},
              )
            : PieTouchData(enabled: false),
      ),
    );
  }

  Widget _buildScatterChart() {
    // Simplified scatter chart
    return _buildLineChart();
  }

  Widget _buildRadarChart() {
    // Radar chart not yet supported in fl_chart
    // Using a placeholder
    return Center(
      child: Text(
        'الرسم الراداري غير مدعوم حالياً',
        style: TextStyle(color: Colors.grey[500]),
      ),
    );
  }

  FlTitlesData _buildTitlesData() {
    return FlTitlesData(
      rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
      topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
      bottomTitles: AxisTitles(
        sideTitles: SideTitles(
          showTitles: true,
          reservedSize: 30,
          interval: 1,
          getTitlesWidget: (value, meta) {
            final index = value.toInt();
            if (config.series.isEmpty) return const SizedBox();
            final dataPoints = config.series.first.dataPoints;
            if (index < 0 || index >= dataPoints.length) return const SizedBox();

            // Show every nth label to avoid crowding
            final showEvery = (dataPoints.length / 6).ceil().clamp(1, 10);
            if (index % showEvery != 0 && index != dataPoints.length - 1) {
              return const SizedBox();
            }

            final point = dataPoints[index];
            String label = point.label ?? point.x.toString();

            // Format date if x is ISO string
            if (point.x is String && (point.x as String).contains('T')) {
              try {
                final date = DateTime.parse(point.x as String);
                label = DateFormat('MM/dd').format(date);
              } catch (_) {}
            }

            return Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                label,
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 10,
                ),
              ),
            );
          },
        ),
      ),
      leftTitles: AxisTitles(
        axisNameWidget: config.yAxis?.titleAr != null
            ? Text(
                config.yAxis!.titleAr!,
                style: TextStyle(color: Colors.grey[600], fontSize: 10),
              )
            : null,
        sideTitles: SideTitles(
          showTitles: true,
          reservedSize: 40,
          interval: config.yAxis?.interval,
          getTitlesWidget: (value, meta) {
            return Text(
              value.toStringAsFixed(value.truncateToDouble() == value ? 0 : 1),
              style: TextStyle(color: Colors.grey[600], fontSize: 10),
            );
          },
        ),
      ),
    );
  }

  FlTitlesData _buildBarTitlesData() {
    return FlTitlesData(
      rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
      topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
      bottomTitles: AxisTitles(
        sideTitles: SideTitles(
          showTitles: true,
          reservedSize: 30,
          getTitlesWidget: (value, meta) {
            final index = value.toInt();
            if (config.series.isEmpty) return const SizedBox();
            final dataPoints = config.series.first.dataPoints;
            if (index < 0 || index >= dataPoints.length) return const SizedBox();

            final point = dataPoints[index];
            final label = point.labelAr ?? point.label ?? point.x.toString();

            return Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                label,
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 10,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            );
          },
        ),
      ),
      leftTitles: AxisTitles(
        sideTitles: SideTitles(
          showTitles: true,
          reservedSize: 40,
          interval: config.yAxis?.interval,
          getTitlesWidget: (value, meta) {
            return Text(
              value.toStringAsFixed(value.truncateToDouble() == value ? 0 : 1),
              style: TextStyle(color: Colors.grey[600], fontSize: 10),
            );
          },
        ),
      ),
    );
  }

  Widget _buildLegend() {
    return Wrap(
      spacing: 16,
      runSpacing: 8,
      children: config.series.map((series) {
        final color = _parseColor(series.colorHex);
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(3),
              ),
            ),
            const SizedBox(width: 6),
            Text(
              series.nameAr,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[700],
              ),
            ),
          ],
        );
      }).toList(),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      height: height ?? 200,
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.show_chart, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 8),
            Text(
              'لا توجد بيانات للعرض',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Color _parseColor(String hexColor) {
    final hex = hexColor.replaceFirst('#', '');
    return Color(int.parse('FF$hex', radix: 16));
  }

  Color _getDefaultColor(int index) {
    const colors = [
      SahoolColors.primary,
      SahoolColors.secondary,
      SahoolColors.info,
      SahoolColors.warning,
      SahoolColors.danger,
      SahoolColors.harvestGold,
    ];
    return colors[index % colors.length];
  }
}
