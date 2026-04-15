/// Fuel Gauge Widget - مقياس الوقود
/// Visual fuel level indicator
library;
import 'dart:math' as math;
import 'package:flutter/material.dart';

import '../../../../core/theme/sahool_theme.dart';

/// Fuel Gauge Widget - مقياس الوقود الدائري
class FuelGauge extends StatelessWidget {
  final double fuelPercent;
  final double size;
  final bool showLabel;
  final bool showValue;
  final double? fuelLiters;
  final double? capacity;

  const FuelGauge({
    super.key,
    required this.fuelPercent,
    this.size = 120,
    this.showLabel = true,
    this.showValue = true,
    this.fuelLiters,
    this.capacity,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getFuelColor();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: CustomPaint(
            painter: _FuelGaugePainter(
              percent: fuelPercent / 100,
              color: color,
              backgroundColor: Colors.grey[200]!,
            ),
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.local_gas_station,
                    color: color,
                    size: size * 0.2,
                  ),
                  if (showValue) ...[
                    Text(
                      '${fuelPercent.toInt()}%',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: size * 0.18,
                        color: color,
                      ),
                    ),
                    if (fuelLiters != null)
                      Text(
                        '${fuelLiters!.toStringAsFixed(0)}L',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: size * 0.1,
                        ),
                      ),
                  ],
                ],
              ),
            ),
          ),
        ),
        if (showLabel) ...[
          const SizedBox(height: 8),
          Text(
            _getFuelLevelLabel(),
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w600,
              fontSize: 14,
            ),
          ),
          if (capacity != null)
            Text(
              'السعة: ${capacity!.toStringAsFixed(0)}L',
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 11,
              ),
            ),
        ],
      ],
    );
  }

  Color _getFuelColor() {
    if (fuelPercent >= 50) return SahoolColors.forestGreen;
    if (fuelPercent >= 25) return SahoolColors.harvestGold;
    if (fuelPercent >= 10) return Colors.orange;
    return SahoolColors.danger;
  }

  String _getFuelLevelLabel() {
    if (fuelPercent >= 75) return 'ممتلئ';
    if (fuelPercent >= 50) return 'جيد';
    if (fuelPercent >= 25) return 'متوسط';
    if (fuelPercent >= 10) return 'منخفض';
    return 'حرج - يجب التعبئة!';
  }
}

/// Custom painter for fuel gauge
class _FuelGaugePainter extends CustomPainter {
  final double percent;
  final Color color;
  final Color backgroundColor;

  _FuelGaugePainter({
    required this.percent,
    required this.color,
    required this.backgroundColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 8;
    const strokeWidth = 12.0;
    const startAngle = math.pi * 0.75;
    const sweepAngle = math.pi * 1.5;

    // Background arc
    final bgPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      bgPaint,
    );

    // Foreground arc
    final fgPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle * percent,
      false,
      fgPaint,
    );

    // Tick marks
    final tickPaint = Paint()
      ..color = Colors.grey[400]!
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;

    for (var i = 0; i <= 4; i++) {
      final angle = startAngle + (sweepAngle * i / 4);
      final inner = radius - strokeWidth / 2 - 4;
      final outer = radius - strokeWidth / 2 - 10;

      canvas.drawLine(
        Offset(
          center.dx + inner * math.cos(angle),
          center.dy + inner * math.sin(angle),
        ),
        Offset(
          center.dx + outer * math.cos(angle),
          center.dy + outer * math.sin(angle),
        ),
        tickPaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _FuelGaugePainter oldDelegate) {
    return percent != oldDelegate.percent || color != oldDelegate.color;
  }
}

/// Horizontal Fuel Bar
class FuelBar extends StatelessWidget {
  final double fuelPercent;
  final double height;
  final bool showLabel;
  final bool showValue;

  const FuelBar({
    super.key,
    required this.fuelPercent,
    this.height = 24,
    this.showLabel = true,
    this.showValue = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getFuelColor();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (showLabel)
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              children: [
                Icon(Icons.local_gas_station, color: color, size: 16),
                const SizedBox(width: 4),
                Text(
                  'الوقود',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
                const Spacer(),
                if (showValue)
                  Text(
                    '${fuelPercent.toInt()}%',
                    style: TextStyle(
                      color: color,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
              ],
            ),
          ),
        Container(
          height: height,
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(height / 2),
          ),
          child: Stack(
            children: [
              FractionallySizedBox(
                widthFactor: fuelPercent / 100,
                child: Container(
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        color.withValues(alpha: 0.7),
                        color,
                      ],
                    ),
                    borderRadius: BorderRadius.circular(height / 2),
                    boxShadow: [
                      BoxShadow(
                        color: color.withValues(alpha: 0.3),
                        blurRadius: 4,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                ),
              ),
              // Fuel level markers
              Positioned.fill(
                child: Row(
                  children: List.generate(4, (index) {
                    return Expanded(
                      child: Container(
                        decoration: BoxDecoration(
                          border: Border(
                            left: index > 0
                                ? BorderSide(
                                    color: Colors.white.withValues(alpha: 0.5),
                                    width: 1,
                                  )
                                : BorderSide.none,
                          ),
                        ),
                      ),
                    );
                  }),
                ),
              ),
            ],
          ),
        ),
        if (fuelPercent < 20)
          const Padding(
            padding: EdgeInsets.only(top: 4),
            child: Row(
              children: [
                Icon(
                  Icons.warning_amber,
                  color: SahoolColors.danger,
                  size: 14,
                ),
                SizedBox(width: 4),
                Text(
                  'الوقود منخفض!',
                  style: TextStyle(
                    color: SahoolColors.danger,
                    fontSize: 11,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Color _getFuelColor() {
    if (fuelPercent >= 50) return SahoolColors.forestGreen;
    if (fuelPercent >= 25) return SahoolColors.harvestGold;
    if (fuelPercent >= 10) return Colors.orange;
    return SahoolColors.danger;
  }
}

/// Mini Fuel Indicator
class MiniFuelIndicator extends StatelessWidget {
  final double fuelPercent;
  final bool showWarning;

  const MiniFuelIndicator({
    super.key,
    required this.fuelPercent,
    this.showWarning = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getFuelColor();
    final isLow = fuelPercent < 20;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          Icons.local_gas_station,
          color: color,
          size: 16,
        ),
        const SizedBox(width: 4),
        Text(
          '${fuelPercent.toInt()}%',
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.w600,
            fontSize: 12,
          ),
        ),
        if (showWarning && isLow) ...[
          const SizedBox(width: 4),
          const Icon(
            Icons.warning,
            color: SahoolColors.danger,
            size: 14,
          ),
        ],
      ],
    );
  }

  Color _getFuelColor() {
    if (fuelPercent >= 50) return SahoolColors.forestGreen;
    if (fuelPercent >= 25) return SahoolColors.harvestGold;
    if (fuelPercent >= 10) return Colors.orange;
    return SahoolColors.danger;
  }
}
