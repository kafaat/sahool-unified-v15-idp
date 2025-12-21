import 'package:flutter/material.dart';

/// NDVI Health Chart Widget - رسم بياني لصحة المحاصيل
class HealthChartWidget extends StatelessWidget {
  final List<HealthDataPoint> dataPoints;
  final String title;
  final Color lineColor;
  final bool showLabels;

  const HealthChartWidget({
    super.key,
    required this.dataPoints,
    this.title = 'NDVI',
    this.lineColor = const Color(0xFF367C2B),
    this.showLabels = true,
  });

  @override
  Widget build(BuildContext context) {
    if (dataPoints.isEmpty) {
      return _buildEmptyState();
    }

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // العنوان والمؤشر
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                _buildCurrentValue(),
              ],
            ),
            const SizedBox(height: 16),

            // الرسم البياني
            SizedBox(
              height: 200,
              child: CustomPaint(
                size: const Size(double.infinity, 200),
                painter: _ChartPainter(
                  dataPoints: dataPoints,
                  lineColor: lineColor,
                  showLabels: showLabels,
                ),
              ),
            ),

            const SizedBox(height: 12),

            // مفتاح الألوان
            _buildLegend(),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: const Padding(
        padding: EdgeInsets.all(32),
        child: Center(
          child: Column(
            children: [
              Icon(Icons.show_chart, size: 48, color: Colors.grey),
              SizedBox(height: 8),
              Text('لا توجد بيانات', style: TextStyle(color: Colors.grey)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCurrentValue() {
    if (dataPoints.isEmpty) return const SizedBox.shrink();

    final latest = dataPoints.last;
    final color = _getHealthColor(latest.value);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color, width: 1.5),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _getHealthIcon(latest.value),
            size: 16,
            color: color,
          ),
          const SizedBox(width: 6),
          Text(
            latest.value.toStringAsFixed(2),
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLegend() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _buildLegendItem('ممتاز', const Color(0xFF2E7D32)),
        const SizedBox(width: 16),
        _buildLegendItem('جيد', const Color(0xFF4CAF50)),
        const SizedBox(width: 16),
        _buildLegendItem('متوسط', const Color(0xFFFF9800)),
        const SizedBox(width: 16),
        _buildLegendItem('ضعيف', const Color(0xFFF44336)),
      ],
    );
  }

  Widget _buildLegendItem(String label, Color color) {
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
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 11)),
      ],
    );
  }

  Color _getHealthColor(double value) {
    if (value >= 0.8) return const Color(0xFF2E7D32);
    if (value >= 0.6) return const Color(0xFF4CAF50);
    if (value >= 0.4) return const Color(0xFFFF9800);
    return const Color(0xFFF44336);
  }

  IconData _getHealthIcon(double value) {
    if (value >= 0.8) return Icons.trending_up;
    if (value >= 0.6) return Icons.trending_flat;
    if (value >= 0.4) return Icons.trending_down;
    return Icons.warning;
  }
}

/// نقطة بيانات صحة المحصول
class HealthDataPoint {
  final DateTime date;
  final double value;
  final String? label;

  const HealthDataPoint({
    required this.date,
    required this.value,
    this.label,
  });
}

/// رسام الرسم البياني
class _ChartPainter extends CustomPainter {
  final List<HealthDataPoint> dataPoints;
  final Color lineColor;
  final bool showLabels;

  _ChartPainter({
    required this.dataPoints,
    required this.lineColor,
    required this.showLabels,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (dataPoints.isEmpty) return;

    final paint = Paint()
      ..color = lineColor
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final fillPaint = Paint()
      ..color = lineColor.withOpacity(0.1)
      ..style = PaintingStyle.fill;

    final dotPaint = Paint()
      ..color = lineColor
      ..style = PaintingStyle.fill;

    // حساب النطاق
    final minVal = 0.0;
    final maxVal = 1.0;
    final range = maxVal - minVal;

    // رسم خطوط الشبكة
    _drawGridLines(canvas, size);

    // تحويل النقاط
    final points = <Offset>[];
    for (var i = 0; i < dataPoints.length; i++) {
      final x = (i / (dataPoints.length - 1)) * size.width;
      final y = size.height - ((dataPoints[i].value - minVal) / range) * size.height;
      points.add(Offset(x, y));
    }

    // رسم منطقة التعبئة
    final fillPath = Path()..moveTo(0, size.height);
    for (final point in points) {
      fillPath.lineTo(point.dx, point.dy);
    }
    fillPath.lineTo(size.width, size.height);
    fillPath.close();
    canvas.drawPath(fillPath, fillPaint);

    // رسم الخط
    final linePath = Path()..moveTo(points.first.dx, points.first.dy);
    for (var i = 1; i < points.length; i++) {
      linePath.lineTo(points[i].dx, points[i].dy);
    }
    canvas.drawPath(linePath, paint);

    // رسم النقاط
    for (var i = 0; i < points.length; i++) {
      final color = _getPointColor(dataPoints[i].value);
      dotPaint.color = color;
      canvas.drawCircle(points[i], 5, dotPaint);
      canvas.drawCircle(
        points[i],
        3,
        Paint()..color = Colors.white,
      );
    }
  }

  void _drawGridLines(Canvas canvas, Size size) {
    final gridPaint = Paint()
      ..color = Colors.grey.withOpacity(0.2)
      ..strokeWidth = 1;

    // خطوط أفقية
    for (var i = 0; i <= 4; i++) {
      final y = (i / 4) * size.height;
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }
  }

  Color _getPointColor(double value) {
    if (value >= 0.8) return const Color(0xFF2E7D32);
    if (value >= 0.6) return const Color(0xFF4CAF50);
    if (value >= 0.4) return const Color(0xFFFF9800);
    return const Color(0xFFF44336);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
