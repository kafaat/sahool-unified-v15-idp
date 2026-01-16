/// Health Score Card Widget
/// ودجت بطاقة درجة الصحة
library;

import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../../data/models/analytics_models.dart';

/// Displays overall health score with visual indicator
/// يعرض درجة الصحة الإجمالية مع مؤشر بصري
class HealthScoreCard extends StatelessWidget {
  final double score;
  final HealthStatus status;
  final String statusNameAr;
  final HealthTrend trend;

  const HealthScoreCard({
    super.key,
    required this.score,
    required this.status,
    required this.statusNameAr,
    required this.trend,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isRtl = Directionality.of(context) == TextDirection.rtl;

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Text(
              isRtl ? 'درجة صحة الحقل' : 'Field Health Score',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: 180,
              height: 180,
              child: CustomPaint(
                painter: _HealthScorePainter(
                  score: score,
                  status: status,
                ),
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        score.toStringAsFixed(0),
                        style: theme.textTheme.headlineLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: _getStatusColor(status),
                        ),
                      ),
                      Text(
                        isRtl ? statusNameAr : _getStatusName(status),
                        style: TextStyle(
                          color: _getStatusColor(status),
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
            _buildTrendIndicator(isRtl),
          ],
        ),
      ),
    );
  }

  Widget _buildTrendIndicator(bool isRtl) {
    IconData icon;
    Color color;
    String text;

    switch (trend) {
      case HealthTrend.improving:
        icon = Icons.trending_up;
        color = Colors.green;
        text = isRtl ? 'تحسن' : 'Improving';
        break;
      case HealthTrend.stable:
        icon = Icons.trending_flat;
        color = Colors.amber;
        text = isRtl ? 'مستقر' : 'Stable';
        break;
      case HealthTrend.declining:
        icon = Icons.trending_down;
        color = Colors.red;
        text = isRtl ? 'تراجع' : 'Declining';
        break;
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 8),
        Text(
          text,
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Color _getStatusColor(HealthStatus status) {
    switch (status) {
      case HealthStatus.excellent:
        return Colors.green;
      case HealthStatus.good:
        return Colors.lightGreen;
      case HealthStatus.moderate:
        return Colors.amber;
      case HealthStatus.poor:
        return Colors.orange;
      case HealthStatus.critical:
        return Colors.red;
    }
  }

  String _getStatusName(HealthStatus status) {
    switch (status) {
      case HealthStatus.excellent:
        return 'Excellent';
      case HealthStatus.good:
        return 'Good';
      case HealthStatus.moderate:
        return 'Moderate';
      case HealthStatus.poor:
        return 'Poor';
      case HealthStatus.critical:
        return 'Critical';
    }
  }
}

class _HealthScorePainter extends CustomPainter {
  final double score;
  final HealthStatus status;

  _HealthScorePainter({
    required this.score,
    required this.status,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 10;

    // Background arc
    final backgroundPaint = Paint()
      ..color = Colors.grey.shade200
      ..style = PaintingStyle.stroke
      ..strokeWidth = 15
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      _degToRad(135),
      _degToRad(270),
      false,
      backgroundPaint,
    );

    // Score arc
    final scorePaint = Paint()
      ..color = _getStatusColor(status)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 15
      ..strokeCap = StrokeCap.round;

    final sweepAngle = (score / 100) * 270;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      _degToRad(135),
      _degToRad(sweepAngle),
      false,
      scorePaint,
    );

    // Tick marks
    final tickPaint = Paint()
      ..color = Colors.grey.shade400
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    for (int i = 0; i <= 10; i++) {
      final angle = _degToRad(135 + (i * 27));
      final outerPoint = Offset(
        center.dx + (radius + 5) * math.cos(angle),
        center.dy + (radius + 5) * math.sin(angle),
      );
      final innerPoint = Offset(
        center.dx + (radius - 5) * math.cos(angle),
        center.dy + (radius - 5) * math.sin(angle),
      );
      canvas.drawLine(outerPoint, innerPoint, tickPaint);
    }
  }

  double _degToRad(double deg) => deg * (math.pi / 180);

  Color _getStatusColor(HealthStatus status) {
    switch (status) {
      case HealthStatus.excellent:
        return Colors.green;
      case HealthStatus.good:
        return Colors.lightGreen;
      case HealthStatus.moderate:
        return Colors.amber;
      case HealthStatus.poor:
        return Colors.orange;
      case HealthStatus.critical:
        return Colors.red;
    }
  }

  @override
  bool shouldRepaint(covariant _HealthScorePainter oldDelegate) {
    return oldDelegate.score != score || oldDelegate.status != status;
  }
}
