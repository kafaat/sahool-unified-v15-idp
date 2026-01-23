import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../models/rotation_models.dart';

class SoilHealthChart extends StatelessWidget {
  final List<SoilHealth> soilHealthData;

  const SoilHealthChart({
    Key? key,
    required this.soilHealthData,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (soilHealthData.isEmpty) {
      return const Center(
        child: Text('No soil health data available'),
      );
    }

    final latestData = soilHealthData.last;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.eco, color: Colors.green),
                const SizedBox(width: 8),
                const Text(
                  'Soil Health Analysis',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: _getHealthColor(latestData.overallScore),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    latestData.healthLevel,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Radar chart
            SizedBox(
              height: 250,
              child: RadarChart(
                data: latestData,
              ),
            ),

            const SizedBox(height: 24),

            // Trend indicators
            const Text(
              'Trend Over Time',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),

            _buildTrendIndicators(),

            const SizedBox(height: 16),

            // pH indicator
            _buildPhIndicator(latestData.ph),
          ],
        ),
      ),
    );
  }

  Widget _buildTrendIndicators() {
    if (soilHealthData.length < 2) {
      return const Text(
        'Not enough data for trend analysis',
        style: TextStyle(
          fontStyle: FontStyle.italic,
          color: Colors.grey,
        ),
      );
    }

    final oldest = soilHealthData.first;
    final latest = soilHealthData.last;

    return Column(
      children: [
        _buildTrendRow('Nitrogen', oldest.nitrogen, latest.nitrogen, Colors.blue),
        const SizedBox(height: 8),
        _buildTrendRow(
            'Phosphorus', oldest.phosphorus, latest.phosphorus, Colors.orange),
        const SizedBox(height: 8),
        _buildTrendRow(
            'Potassium', oldest.potassium, latest.potassium, Colors.purple),
        const SizedBox(height: 8),
        _buildTrendRow('Organic Matter', oldest.organicMatter,
            latest.organicMatter, Colors.brown),
        const SizedBox(height: 8),
        _buildTrendRow('Water Retention', oldest.waterRetention,
            latest.waterRetention, Colors.lightBlue),
      ],
    );
  }

  Widget _buildTrendRow(
      String label, double oldValue, double newValue, Color color) {
    final change = newValue - oldValue;
    final percentChange = (change / oldValue * 100).toStringAsFixed(1);
    final isImproving = change > 0;
    final isStable = change.abs() < 2;

    return Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            label,
            style: const TextStyle(fontSize: 13),
          ),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: isStable
                ? Colors.grey.shade200
                : isImproving
                    ? Colors.green.shade100
                    : Colors.red.shade100,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                isStable
                    ? Icons.horizontal_rule
                    : isImproving
                        ? Icons.trending_up
                        : Icons.trending_down,
                color: isStable
                    ? Colors.grey.shade600
                    : isImproving
                        ? Colors.green
                        : Colors.red,
                size: 16,
              ),
              const SizedBox(width: 4),
              Text(
                isStable ? 'Stable' : '${isImproving ? '+' : ''}$percentChange%',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: isStable
                      ? Colors.grey.shade600
                      : isImproving
                          ? Colors.green
                          : Colors.red,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPhIndicator(double ph) {
    String phLevel;
    Color phColor;

    if (ph < 6.0) {
      phLevel = 'Acidic';
      phColor = Colors.orange;
    } else if (ph > 7.5) {
      phLevel = 'Alkaline';
      phColor = Colors.blue;
    } else {
      phLevel = 'Neutral';
      phColor = Colors.green;
    }

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: phColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: phColor.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(Icons.science, color: phColor),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Soil pH Level',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Row(
                  children: [
                    Text(
                      ph.toStringAsFixed(1),
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: phColor,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: phColor,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Text(
                        phLevel,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // pH scale visualization
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              const Text(
                'pH Scale',
                style: TextStyle(fontSize: 10, color: Colors.grey),
              ),
              const SizedBox(height: 4),
              Container(
                width: 100,
                height: 8,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(4),
                  gradient: const LinearGradient(
                    colors: [
                      Colors.red, // Acidic
                      Colors.orange,
                      Colors.yellow,
                      Colors.green, // Neutral
                      Colors.lightBlue,
                      Colors.blue, // Alkaline
                    ],
                  ),
                ),
                child: Stack(
                  children: [
                    Positioned(
                      left: ((ph - 4.0) / 6.0 * 100).clamp(0, 100),
                      top: -2,
                      child: Container(
                        width: 4,
                        height: 12,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          border: Border.all(color: Colors.black, width: 2),
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 2),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('4', style: TextStyle(fontSize: 8, color: Colors.grey)),
                  SizedBox(width: 80),
                  Text('10', style: TextStyle(fontSize: 8, color: Colors.grey)),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _getHealthColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.lightGreen;
    if (score >= 40) return Colors.orange;
    return Colors.red;
  }
}

/// Radar chart for soil health visualization
class RadarChart extends StatelessWidget {
  final SoilHealth data;

  const RadarChart({
    Key? key,
    required this.data,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: RadarChartPainter(data),
      child: Container(),
    );
  }
}

class RadarChartPainter extends CustomPainter {
  final SoilHealth data;

  RadarChartPainter(this.data);

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 40;

    // Draw background circles
    _drawBackgroundCircles(canvas, center, radius);

    // Draw axes
    _drawAxes(canvas, center, radius);

    // Draw labels
    _drawLabels(canvas, center, radius);

    // Draw data polygon
    _drawDataPolygon(canvas, center, radius);
  }

  void _drawBackgroundCircles(Canvas canvas, Offset center, double radius) {
    final paint = Paint()
      ..color = Colors.grey.shade200
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.0;

    for (int i = 1; i <= 4; i++) {
      canvas.drawCircle(center, radius * i / 4, paint);
    }

    // Draw percentage labels
    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
    );

    for (int i = 1; i <= 4; i++) {
      final percentage = (i * 25).toString();
      textPainter.text = TextSpan(
        text: '$percentage%',
        style: TextStyle(
          color: Colors.grey.shade400,
          fontSize: 10,
        ),
      );
      textPainter.layout();
      textPainter.paint(
        canvas,
        Offset(center.dx + 5, center.dy - radius * i / 4 - 5),
      );
    }
  }

  void _drawAxes(Canvas canvas, Offset center, double radius) {
    final paint = Paint()
      ..color = Colors.grey.shade300
      ..strokeWidth = 1.0;

    final attributes = _getAttributes();
    final angleStep = 2 * math.pi / attributes.length;

    for (int i = 0; i < attributes.length; i++) {
      final angle = i * angleStep - math.pi / 2;
      final end = Offset(
        center.dx + radius * math.cos(angle),
        center.dy + radius * math.sin(angle),
      );
      canvas.drawLine(center, end, paint);
    }
  }

  void _drawLabels(Canvas canvas, Offset center, double radius) {
    final attributes = _getAttributes();
    final angleStep = 2 * math.pi / attributes.length;

    for (int i = 0; i < attributes.length; i++) {
      final angle = i * angleStep - math.pi / 2;
      final labelRadius = radius + 25;
      final position = Offset(
        center.dx + labelRadius * math.cos(angle),
        center.dy + labelRadius * math.sin(angle),
      );

      final textPainter = TextPainter(
        text: TextSpan(
          text: attributes[i].name,
          style: TextStyle(
            color: attributes[i].color,
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
        textAlign: TextAlign.center,
        textDirection: TextDirection.ltr,
      );

      textPainter.layout();

      // Center the text
      final offset = Offset(
        position.dx - textPainter.width / 2,
        position.dy - textPainter.height / 2,
      );

      textPainter.paint(canvas, offset);
    }
  }

  void _drawDataPolygon(Canvas canvas, Offset center, double radius) {
    final attributes = _getAttributes();
    final angleStep = 2 * math.pi / attributes.length;
    final path = Path();

    for (int i = 0; i < attributes.length; i++) {
      final angle = i * angleStep - math.pi / 2;
      final value = attributes[i].value / 100; // Normalize to 0-1
      final distance = radius * value;

      final point = Offset(
        center.dx + distance * math.cos(angle),
        center.dy + distance * math.sin(angle),
      );

      if (i == 0) {
        path.moveTo(point.dx, point.dy);
      } else {
        path.lineTo(point.dx, point.dy);
      }
    }

    path.close();

    // Fill
    final fillPaint = Paint()
      ..color = Colors.green.withOpacity(0.2)
      ..style = PaintingStyle.fill;
    canvas.drawPath(path, fillPaint);

    // Stroke
    final strokePaint = Paint()
      ..color = Colors.green
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;
    canvas.drawPath(path, strokePaint);

    // Draw points
    for (int i = 0; i < attributes.length; i++) {
      final angle = i * angleStep - math.pi / 2;
      final value = attributes[i].value / 100;
      final distance = radius * value;

      final point = Offset(
        center.dx + distance * math.cos(angle),
        center.dy + distance * math.sin(angle),
      );

      final pointPaint = Paint()
        ..color = attributes[i].color
        ..style = PaintingStyle.fill;

      canvas.drawCircle(point, 4, pointPaint);

      // Draw value text
      final textPainter = TextPainter(
        text: TextSpan(
          text: attributes[i].value.toStringAsFixed(0),
          style: const TextStyle(
            color: Colors.black,
            fontSize: 10,
            fontWeight: FontWeight.bold,
            backgroundColor: Colors.white,
          ),
        ),
        textAlign: TextAlign.center,
        textDirection: TextDirection.ltr,
      );

      textPainter.layout();
      textPainter.paint(
        canvas,
        Offset(point.dx - textPainter.width / 2, point.dy - textPainter.height - 8),
      );
    }
  }

  List<RadarAttribute> _getAttributes() {
    return [
      RadarAttribute('N', data.nitrogen, Colors.blue),
      RadarAttribute('P', data.phosphorus, Colors.orange),
      RadarAttribute('K', data.potassium, Colors.purple),
      RadarAttribute('OM', data.organicMatter, Colors.brown),
      RadarAttribute('WR', data.waterRetention, Colors.lightBlue),
    ];
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class RadarAttribute {
  final String name;
  final double value;
  final Color color;

  RadarAttribute(this.name, this.value, this.color);
}
