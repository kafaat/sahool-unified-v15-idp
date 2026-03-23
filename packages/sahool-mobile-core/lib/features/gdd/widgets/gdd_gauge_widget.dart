/// GDD Gauge Widget - ويدجت مقياس درجات النمو الحراري الدائري
library;

import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../models/gdd_models.dart';

/// ويدجت المقياس الدائري لـ GDD
class GDDGaugeWidget extends StatelessWidget {
  final double currentGDD;
  final double totalGDD;
  final GrowthStage? currentStage;
  final double? progressPercent;

  const GDDGaugeWidget({
    super.key,
    required this.currentGDD,
    required this.totalGDD,
    this.currentStage,
    this.progressPercent,
  });

  @override
  Widget build(BuildContext context) {
    final progress = (currentGDD / totalGDD).clamp(0.0, 1.0);

    return Card(
      elevation: 4,
      child: Container(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // العنوان
            Text(
              'تراكم GDD',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 24),

            // المقياس الدائري
            SizedBox(
              width: 220,
              height: 220,
              child: CustomPaint(
                painter: _GDDGaugePainter(
                  progress: progress,
                  currentGDD: currentGDD,
                  totalGDD: totalGDD,
                  currentStage: currentStage,
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        currentGDD.toStringAsFixed(0),
                        style: Theme.of(context).textTheme.displaySmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: _getProgressColor(progress),
                            ),
                      ),
                      Text(
                        'من ${totalGDD.toStringAsFixed(0)}',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Colors.grey.shade600,
                            ),
                      ),
                      if (currentStage != null) ...[
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 12,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: _getProgressColor(progress).withOpacity(0.2),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            currentStage!.getName('ar'),
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: _getProgressColor(progress),
                                ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),

            // شريط التقدم الخطي
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'نسبة الإكمال',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                    Text(
                      '${(progress * 100).toStringAsFixed(1)}%',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: _getProgressColor(progress),
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: progress,
                    minHeight: 12,
                    backgroundColor: Colors.grey.shade200,
                    valueColor: AlwaysStoppedAnimation<Color>(
                      _getProgressColor(progress),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Color _getProgressColor(double progress) {
    if (progress < 0.25) {
      return Colors.blue;
    } else if (progress < 0.5) {
      return Colors.green;
    } else if (progress < 0.75) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }
}

/// رسام المقياس الدائري
class _GDDGaugePainter extends CustomPainter {
  final double progress;
  final double currentGDD;
  final double totalGDD;
  final GrowthStage? currentStage;

  _GDDGaugePainter({
    required this.progress,
    required this.currentGDD,
    required this.totalGDD,
    this.currentStage,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 10;

    // رسم الخلفية (الدائرة الرمادية)
    final backgroundPaint = Paint()
      ..color = Colors.grey.shade200
      ..style = PaintingStyle.stroke
      ..strokeWidth = 20
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2 - math.pi * 0.75, // زاوية البداية
      math.pi * 1.5, // مدى الزاوية
      false,
      backgroundPaint,
    );

    // رسم التقدم (الدائرة الملونة)
    final progressPaint = Paint()
      ..shader = LinearGradient(
        colors: _getGradientColors(progress),
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
      ).createShader(Rect.fromCircle(center: center, radius: radius))
      ..style = PaintingStyle.stroke
      ..strokeWidth = 20
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2 - math.pi * 0.75, // زاوية البداية
      math.pi * 1.5 * progress, // مدى الزاوية حسب التقدم
      false,
      progressPaint,
    );

    // رسم علامات التدرج
    _drawTickMarks(canvas, center, radius);
  }

  void _drawTickMarks(Canvas canvas, Offset center, double radius) {
    final tickPaint = Paint()
      ..color = Colors.grey.shade400
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    // رسم 10 علامات
    for (int i = 0; i <= 10; i++) {
      final angle = -math.pi / 2 - math.pi * 0.75 + (math.pi * 1.5 * i / 10);
      final startRadius = radius - 15;
      final endRadius = radius - 5;

      final startPoint = Offset(
        center.dx + startRadius * math.cos(angle),
        center.dy + startRadius * math.sin(angle),
      );

      final endPoint = Offset(
        center.dx + endRadius * math.cos(angle),
        center.dy + endRadius * math.sin(angle),
      );

      canvas.drawLine(startPoint, endPoint, tickPaint);
    }
  }

  List<Color> _getGradientColors(double progress) {
    if (progress < 0.25) {
      return [Colors.blue.shade300, Colors.blue.shade600];
    } else if (progress < 0.5) {
      return [Colors.green.shade300, Colors.green.shade600];
    } else if (progress < 0.75) {
      return [Colors.orange.shade300, Colors.orange.shade600];
    } else {
      return [Colors.red.shade300, Colors.red.shade600];
    }
  }

  @override
  bool shouldRepaint(_GDDGaugePainter oldDelegate) {
    return oldDelegate.progress != progress ||
        oldDelegate.currentGDD != currentGDD ||
        oldDelegate.totalGDD != totalGDD;
  }
}
