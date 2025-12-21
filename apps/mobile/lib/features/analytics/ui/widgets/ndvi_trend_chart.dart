import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../domain/entities/field_history.dart';
import '../../../../core/theme/sahool_theme.dart';

/// NDVI Trend Chart - رسم بياني لتاريخ صحة الحقل
///
/// يعرض منحنى NDVI عبر الزمن مع تدرج لوني يعكس صحة النبات
class NdviTrendChart extends StatelessWidget {
  /// سجل القراءات التاريخية
  final List<NdviRecord> history;

  /// إظهار النقاط على المنحنى
  final bool showDots;

  /// إظهار التعبئة تحت المنحنى
  final bool showArea;

  /// ارتفاع الرسم البياني
  final double? height;

  const NdviTrendChart({
    super.key,
    required this.history,
    this.showDots = false,
    this.showArea = true,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    if (history.isEmpty) {
      return _buildEmptyState();
    }

    // تحضير نقاط البيانات
    final points = history
        .asMap()
        .entries
        .map((e) => FlSpot(e.key.toDouble(), e.value.value))
        .toList();

    // تحديد الاتجاه للتلوين
    final isImproving = history.length >= 2 &&
        history.last.value >= history.first.value;

    return SizedBox(
      height: height,
      child: AspectRatio(
        aspectRatio: height != null ? 2.0 : 1.70,
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18),
            color: Colors.white,
          ),
          child: Padding(
            padding: const EdgeInsets.only(
              right: 18,
              left: 12,
              top: 24,
              bottom: 12,
            ),
            child: LineChart(
              LineChartData(
                gridData: _buildGridData(),
                titlesData: _buildTitlesData(),
                borderData: FlBorderData(show: false),
                minX: 0,
                maxX: (history.length - 1).toDouble(),
                minY: 0,
                maxY: 1.0,
                lineTouchData: _buildTouchData(),
                lineBarsData: [
                  _buildLineData(points, isImproving),
                ],
              ),
              duration: const Duration(milliseconds: 300),
            ),
          ),
        ),
      ),
    );
  }

  /// شبكة الخلفية
  FlGridData _buildGridData() {
    return FlGridData(
      show: true,
      drawVerticalLine: false,
      horizontalInterval: 0.25,
      getDrawingHorizontalLine: (value) {
        return FlLine(
          color: Colors.grey.withOpacity(0.1),
          strokeWidth: 1,
        );
      },
    );
  }

  /// عناوين المحاور
  FlTitlesData _buildTitlesData() {
    return FlTitlesData(
      show: true,
      rightTitles: const AxisTitles(
        sideTitles: SideTitles(showTitles: false),
      ),
      topTitles: const AxisTitles(
        sideTitles: SideTitles(showTitles: false),
      ),
      // التواريخ في الأسفل
      bottomTitles: AxisTitles(
        sideTitles: SideTitles(
          showTitles: true,
          reservedSize: 30,
          interval: 1,
          getTitlesWidget: (value, meta) {
            final index = value.toInt();
            // إظهار كل ثاني تاريخ لتجنب الازدحام
            if (index >= 0 && index < history.length && index % 2 == 0) {
              return Padding(
                padding: const EdgeInsets.only(top: 8.0),
                child: Text(
                  DateFormat('MM/dd').format(history[index].date),
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 10,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              );
            }
            return const SizedBox();
          },
        ),
      ),
      // قيم NDVI على اليسار
      leftTitles: AxisTitles(
        sideTitles: SideTitles(
          showTitles: true,
          interval: 0.25,
          reservedSize: 30,
          getTitlesWidget: (value, meta) {
            return Text(
              value.toStringAsFixed(2),
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 10,
              ),
            );
          },
        ),
      ),
    );
  }

  /// بيانات التفاعل باللمس
  LineTouchData _buildTouchData() {
    return LineTouchData(
      enabled: true,
      touchTooltipData: LineTouchTooltipData(
        getTooltipColor: (touchedSpot) => SahoolColors.primary.withOpacity(0.9),
        tooltipRoundedRadius: 8,
        getTooltipItems: (touchedSpots) {
          return touchedSpots.map((spot) {
            final index = spot.x.toInt();
            final record = history[index];
            return LineTooltipItem(
              '${DateFormat('yyyy/MM/dd').format(record.date)}\n',
              const TextStyle(
                color: Colors.white70,
                fontSize: 10,
              ),
              children: [
                TextSpan(
                  text: 'NDVI: ${record.value.toStringAsFixed(2)}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
              ],
            );
          }).toList();
        },
      ),
      handleBuiltInTouches: true,
    );
  }

  /// بيانات الخط
  LineChartBarData _buildLineData(List<FlSpot> points, bool isImproving) {
    // ألوان التدرج بناءً على الاتجاه
    final gradientColors = isImproving
        ? [SahoolColors.warning, SahoolColors.success]
        : [SahoolColors.success, SahoolColors.warning];

    return LineChartBarData(
      spots: points,
      isCurved: true,
      curveSmoothness: 0.35,
      preventCurveOverShooting: true,
      gradient: LinearGradient(colors: gradientColors),
      barWidth: 4,
      isStrokeCapRound: true,
      dotData: FlDotData(
        show: showDots,
        getDotPainter: (spot, percent, bar, index) {
          final record = history[index];
          return FlDotCirclePainter(
            radius: 4,
            color: _getNdviColor(record.value),
            strokeWidth: 2,
            strokeColor: Colors.white,
          );
        },
      ),
      belowBarData: showArea
          ? BarAreaData(
              show: true,
              gradient: LinearGradient(
                colors: [
                  SahoolColors.primary.withOpacity(0.3),
                  SahoolColors.primary.withOpacity(0.0),
                ],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
            )
          : null,
    );
  }

  /// الحالة الفارغة
  Widget _buildEmptyState() {
    return Container(
      height: height ?? 150,
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(18),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.show_chart, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 8),
            Text(
              'لا توجد بيانات تاريخية',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  /// لون NDVI
  Color _getNdviColor(double value) {
    if (value >= 0.7) return SahoolColors.success;
    if (value >= 0.5) return SahoolColors.primary;
    if (value >= 0.3) return SahoolColors.warning;
    return SahoolColors.danger;
  }
}

/// Trend Indicator Widget - مؤشر الاتجاه المصغر
class TrendIndicator extends StatelessWidget {
  final TrendDirection trend;
  final double changeRate;

  const TrendIndicator({
    super.key,
    required this.trend,
    required this.changeRate,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: _backgroundColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_icon, size: 16, color: _iconColor),
          const SizedBox(width: 4),
          Text(
            '${changeRate >= 0 ? '+' : ''}${changeRate.toStringAsFixed(1)}%',
            style: TextStyle(
              color: _iconColor,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  IconData get _icon {
    switch (trend) {
      case TrendDirection.improving:
        return Icons.trending_up;
      case TrendDirection.declining:
        return Icons.trending_down;
      case TrendDirection.stable:
        return Icons.trending_flat;
    }
  }

  Color get _iconColor {
    switch (trend) {
      case TrendDirection.improving:
        return SahoolColors.success;
      case TrendDirection.declining:
        return SahoolColors.danger;
      case TrendDirection.stable:
        return SahoolColors.info;
    }
  }

  Color get _backgroundColor {
    switch (trend) {
      case TrendDirection.improving:
        return SahoolColors.success.withOpacity(0.1);
      case TrendDirection.declining:
        return SahoolColors.danger.withOpacity(0.1);
      case TrendDirection.stable:
        return SahoolColors.info.withOpacity(0.1);
    }
  }
}
