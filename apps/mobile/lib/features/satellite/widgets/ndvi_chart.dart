/// NDVI Chart Widget - ودجت مخطط NDVI
/// Line chart for NDVI time series data using fl_chart
library;

import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../data/models/ndvi_data.dart';

class NdviChart extends StatelessWidget {
  final List<NdviDataPoint> data;
  final double currentValue;

  const NdviChart({
    super.key,
    required this.data,
    required this.currentValue,
  });

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty) {
      return const Center(
        child: Text('No NDVI data available'),
      );
    }

    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: true,
          horizontalInterval: 0.2,
          verticalInterval: 1,
          getDrawingHorizontalLine: (value) {
            return FlLine(
              color: Colors.grey.withOpacity(0.2),
              strokeWidth: 1,
            );
          },
          getDrawingVerticalLine: (value) {
            return FlLine(
              color: Colors.grey.withOpacity(0.2),
              strokeWidth: 1,
            );
          },
        ),
        titlesData: FlTitlesData(
          show: true,
          rightTitles: AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          topTitles: AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 30,
              interval: 1,
              getTitlesWidget: (value, meta) {
                if (value.toInt() < 0 || value.toInt() >= data.length) {
                  return const Text('');
                }
                final date = data[value.toInt()].date;
                return Padding(
                  padding: const EdgeInsets.only(top: 8.0),
                  child: Text(
                    '${date.day}/${date.month}',
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
            sideTitles: SideTitles(
              showTitles: true,
              interval: 0.2,
              getTitlesWidget: (value, meta) {
                return Text(
                  value.toStringAsFixed(1),
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 10,
                  ),
                );
              },
              reservedSize: 42,
            ),
          ),
        ),
        borderData: FlBorderData(
          show: true,
          border: Border.all(color: Colors.grey.withOpacity(0.2)),
        ),
        minX: 0,
        maxX: (data.length - 1).toDouble(),
        minY: 0,
        maxY: 1,
        lineBarsData: [
          LineChartBarData(
            spots: data
                .asMap()
                .entries
                .map((e) => FlSpot(
                      e.key.toDouble(),
                      e.value.value.clamp(0.0, 1.0),
                    ))
                .toList(),
            isCurved: true,
            gradient: const LinearGradient(
              colors: [
                Color(0xFF367C2B),
                Color(0xFF4CAF50),
              ],
            ),
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: FlDotData(
              show: true,
              getDotPainter: (spot, percent, barData, index) {
                return FlDotCirclePainter(
                  radius: 4,
                  color: Colors.white,
                  strokeWidth: 2,
                  strokeColor: const Color(0xFF367C2B),
                );
              },
            ),
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                colors: [
                  const Color(0xFF367C2B).withOpacity(0.3),
                  const Color(0xFF367C2B).withOpacity(0.0),
                ],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
            ),
          ),
        ],
        lineTouchData: LineTouchData(
          touchTooltipData: LineTouchTooltipData(
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((spot) {
                final date = data[spot.x.toInt()].date;
                return LineTooltipItem(
                  '${date.day}/${date.month}\n${spot.y.toStringAsFixed(2)}',
                  const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                );
              }).toList();
            },
          ),
          handleBuiltInTouches: true,
        ),
        extraLinesData: ExtraLinesData(
          horizontalLines: [
            // Excellent threshold (0.8)
            HorizontalLine(
              y: 0.8,
              color: Colors.green.withOpacity(0.3),
              strokeWidth: 1,
              dashArray: [5, 5],
            ),
            // Good threshold (0.6)
            HorizontalLine(
              y: 0.6,
              color: Colors.lightGreen.withOpacity(0.3),
              strokeWidth: 1,
              dashArray: [5, 5],
            ),
            // Fair threshold (0.4)
            HorizontalLine(
              y: 0.4,
              color: Colors.orange.withOpacity(0.3),
              strokeWidth: 1,
              dashArray: [5, 5],
            ),
            // Poor threshold (0.2)
            HorizontalLine(
              y: 0.2,
              color: Colors.red.withOpacity(0.3),
              strokeWidth: 1,
              dashArray: [5, 5],
            ),
          ],
        ),
      ),
    );
  }
}
