/// Health Indicator Widget - ودجت مؤشر الصحة
/// Circular gauge widget for field health score (0-100)
library;

import 'package:flutter/material.dart';
import 'dart:math' as math;

class HealthIndicator extends StatelessWidget {
  final double score; // 0-100
  final String status; // good, warning, critical

  const HealthIndicator({
    super.key,
    required this.score,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getColorForStatus(status);
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Center(
      child: SizedBox(
        width: 150,
        height: 150,
        child: CustomPaint(
          painter: _HealthGaugePainter(
            score: score,
            color: color,
          ),
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  score.toStringAsFixed(0),
                  style: TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                Text(
                  _getStatusLabel(status, isArabic),
                  style: TextStyle(
                    fontSize: 14,
                    color: color,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getColorForStatus(String status) {
    switch (status.toLowerCase()) {
      case 'excellent':
        return const Color(0xFF4CAF50);
      case 'good':
        return const Color(0xFF8BC34A);
      case 'warning':
        return const Color(0xFFFFC107);
      case 'critical':
        return const Color(0xFFF44336);
      default:
        return const Color(0xFF9E9E9E);
    }
  }

  String _getStatusLabel(String status, bool isArabic) {
    if (isArabic) {
      switch (status.toLowerCase()) {
        case 'excellent':
          return 'ممتاز';
        case 'good':
          return 'جيد';
        case 'warning':
          return 'تحذير';
        case 'critical':
          return 'حرج';
        default:
          return 'غير معروف';
      }
    } else {
      return status[0].toUpperCase() + status.substring(1).toLowerCase();
    }
  }
}

class _HealthGaugePainter extends CustomPainter {
  final double score;
  final Color color;

  _HealthGaugePainter({
    required this.score,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 10;

    // Background circle
    final bgPaint = Paint()
      ..color = Colors.grey.withOpacity(0.2)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12.0
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, bgPaint);

    // Progress arc
    final progressPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 12.0
      ..strokeCap = StrokeCap.round;

    final sweepAngle = (score / 100) * 2 * math.pi;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2, // Start from top
      sweepAngle,
      false,
      progressPaint,
    );

    // Inner glow
    final glowPaint = Paint()
      ..color = color.withOpacity(0.1)
      ..style = PaintingStyle.fill;

    canvas.drawCircle(center, radius - 15, glowPaint);
  }

  @override
  bool shouldRepaint(_HealthGaugePainter oldDelegate) {
    return oldDelegate.score != score || oldDelegate.color != color;
  }
}
