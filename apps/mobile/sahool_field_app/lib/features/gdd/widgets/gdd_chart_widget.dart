/// GDD Chart Widget - ويدجت الرسم البياني لدرجات النمو الحراري
library;

import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/gdd_models.dart';
import '../screens/gdd_chart_screen.dart';

/// ويدجت الرسم البياني لـ GDD
class GDDChartWidget extends StatefulWidget {
  final List<GDDRecord> records;
  final List<GDDForecast> forecasts;
  final List<GrowthStage> stages;
  final ChartViewMode viewMode;
  final double height;

  const GDDChartWidget({
    super.key,
    required this.records,
    this.forecasts = const [],
    this.stages = const [],
    this.viewMode = ChartViewMode.accumulated,
    this.height = 300,
  });

  @override
  State<GDDChartWidget> createState() => _GDDChartWidgetState();
}

class _GDDChartWidgetState extends State<GDDChartWidget> {
  int? _touchedIndex;

  @override
  Widget build(BuildContext context) {
    if (widget.records.isEmpty) {
      return SizedBox(
        height: widget.height,
        child: Center(
          child: Text(
            'لا توجد بيانات لعرضها',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey.shade600,
                ),
          ),
        ),
      );
    }

    return SizedBox(
      height: widget.height,
      child: LineChart(
        _buildChartData(),
        swapAnimationDuration: const Duration(milliseconds: 250),
      ),
    );
  }

  LineChartData _buildChartData() {
    return LineChartData(
      gridData: FlGridData(
        show: true,
        drawVerticalLine: true,
        getDrawingHorizontalLine: (value) {
          return FlLine(
            color: Colors.grey.shade300,
            strokeWidth: 1,
          );
        },
        getDrawingVerticalLine: (value) {
          return FlLine(
            color: Colors.grey.shade300,
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
            interval: _getXAxisInterval(),
            getTitlesWidget: (value, meta) {
              return _buildBottomTitle(value.toInt());
            },
          ),
        ),
        leftTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            reservedSize: 50,
            interval: _getYAxisInterval(),
            getTitlesWidget: (value, meta) {
              return Text(
                value.toStringAsFixed(0),
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center,
              );
            },
          ),
        ),
      ),
      borderData: FlBorderData(
        show: true,
        border: Border.all(color: Colors.grey.shade300),
      ),
      lineBarsData: _buildLineBars(),
      extraLinesData: ExtraLinesData(
        verticalLines: _buildStageLines(),
      ),
      lineTouchData: LineTouchData(
        enabled: true,
        touchTooltipData: LineTouchTooltipData(
          tooltipBgColor: Colors.blueGrey.withOpacity(0.9),
          getTooltipItems: (touchedSpots) {
            return touchedSpots.map((spot) {
              final record = widget.records[spot.x.toInt()];
              final dateFormat = DateFormat('dd/MM', 'ar');
              return LineTooltipItem(
                '${dateFormat.format(record.date)}\n'
                '${spot.y.toStringAsFixed(1)} GDD',
                const TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              );
            }).toList();
          },
        ),
        handleBuiltInTouches: true,
        touchCallback: (event, response) {
          if (response == null || response.lineBarSpots == null) {
            setState(() {
              _touchedIndex = null;
            });
            return;
          }
          setState(() {
            _touchedIndex = response.lineBarSpots!.first.x.toInt();
          });
        },
      ),
    );
  }

  List<LineChartBarData> _buildLineBars() {
    final bars = <LineChartBarData>[];

    // خط السجلات الفعلية
    final recordSpots = widget.records.asMap().entries.map((entry) {
      final index = entry.key;
      final record = entry.value;
      final yValue = widget.viewMode == ChartViewMode.accumulated
          ? record.accumulatedGDD
          : record.gddValue;
      return FlSpot(index.toDouble(), yValue);
    }).toList();

    bars.add(
      LineChartBarData(
        spots: recordSpots,
        isCurved: true,
        color: Colors.blue.shade600,
        barWidth: 3,
        isStrokeCapRound: true,
        dotData: FlDotData(
          show: widget.records.length < 30,
          getDotPainter: (spot, percent, barData, index) {
            return FlDotCirclePainter(
              radius: _touchedIndex == index ? 6 : 4,
              color: Colors.blue.shade600,
              strokeWidth: 2,
              strokeColor: Colors.white,
            );
          },
        ),
        belowBarData: BarAreaData(
          show: true,
          gradient: LinearGradient(
            colors: [
              Colors.blue.shade200.withOpacity(0.3),
              Colors.blue.shade100.withOpacity(0.1),
            ],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
      ),
    );

    // خط التوقعات
    if (widget.forecasts.isNotEmpty) {
      final lastRecordIndex = widget.records.length - 1;
      final forecastSpots = <FlSpot>[];

      // إضافة النقطة الأخيرة من السجلات
      if (widget.records.isNotEmpty) {
        final lastRecord = widget.records.last;
        forecastSpots.add(
          FlSpot(
            lastRecordIndex.toDouble(),
            widget.viewMode == ChartViewMode.accumulated
                ? lastRecord.accumulatedGDD
                : lastRecord.gddValue,
          ),
        );
      }

      // إضافة نقاط التوقعات
      for (var i = 0; i < widget.forecasts.length; i++) {
        final forecast = widget.forecasts[i];
        final yValue = widget.viewMode == ChartViewMode.accumulated
            ? forecast.cumulativeGDD
            : forecast.forecastGDD;
        forecastSpots.add(
          FlSpot((lastRecordIndex + i + 1).toDouble(), yValue),
        );
      }

      bars.add(
        LineChartBarData(
          spots: forecastSpots,
          isCurved: true,
          color: Colors.orange.shade400,
          barWidth: 2,
          isStrokeCapRound: true,
          dashArray: [5, 5], // خط متقطع
          dotData: FlDotData(
            show: true,
            getDotPainter: (spot, percent, barData, index) {
              return FlDotCirclePainter(
                radius: 3,
                color: Colors.orange.shade400,
                strokeWidth: 1,
                strokeColor: Colors.white,
              );
            },
          ),
        ),
      );
    }

    return bars;
  }

  List<VerticalLine> _buildStageLines() {
    if (widget.stages.isEmpty || widget.viewMode != ChartViewMode.accumulated) {
      return [];
    }

    final lines = <VerticalLine>[];
    final colors = [
      Colors.green.shade300,
      Colors.blue.shade300,
      Colors.orange.shade300,
      Colors.purple.shade300,
      Colors.red.shade300,
    ];

    for (var stage in widget.stages) {
      // إيجاد السجل الذي يصل إلى بداية هذه المرحلة
      final stageStartRecord = widget.records.indexWhere(
        (r) => r.accumulatedGDD >= stage.gddStart,
      );

      if (stageStartRecord != -1) {
        lines.add(
          VerticalLine(
            x: stageStartRecord.toDouble(),
            color: colors[stage.stageNumber % colors.length].withOpacity(0.5),
            strokeWidth: 2,
            dashArray: [4, 4],
            label: VerticalLineLabel(
              show: true,
              alignment: Alignment.topRight,
              padding: const EdgeInsets.all(4),
              style: TextStyle(
                color: colors[stage.stageNumber % colors.length],
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
              labelResolver: (line) => stage.getName('ar'),
            ),
          ),
        );
      }
    }

    return lines;
  }

  Widget _buildBottomTitle(int index) {
    if (index < 0 || index >= widget.records.length) {
      return const SizedBox.shrink();
    }

    final record = widget.records[index];
    final dateFormat = DateFormat('dd/MM', 'ar');

    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Transform.rotate(
        angle: -0.5,
        child: Text(
          dateFormat.format(record.date),
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ),
    );
  }

  double _getXAxisInterval() {
    final count = widget.records.length;
    if (count <= 10) return 1;
    if (count <= 30) return count / 5;
    if (count <= 90) return count / 6;
    return count / 8;
  }

  double _getYAxisInterval() {
    if (widget.records.isEmpty) return 100;

    final maxValue = widget.viewMode == ChartViewMode.accumulated
        ? widget.records.last.accumulatedGDD
        : widget.records.map((r) => r.gddValue).reduce((a, b) => a > b ? a : b);

    if (maxValue <= 100) return 20;
    if (maxValue <= 500) return 100;
    if (maxValue <= 1000) return 200;
    if (maxValue <= 2000) return 400;
    return 500;
  }
}
