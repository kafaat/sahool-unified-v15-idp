import 'package:flutter/material.dart';
import '../domain/ndvi_value.dart';
import '../domain/ndvi_colormap.dart';
import '../domain/spectral_index.dart';

/// NDVI Health Indicator Widget
/// Circular gauge showing current NDVI health status
class NdviHealthIndicator extends StatelessWidget {
  final double ndviValue;
  final double size;
  final bool showLabel;
  final bool showValue;
  final bool animate;

  const NdviHealthIndicator({
    super.key,
    required this.ndviValue,
    this.size = 80,
    this.showLabel = true,
    this.showValue = true,
    this.animate = true,
  });

  @override
  Widget build(BuildContext context) {
    final category = NdviHealthCategory.fromValue(ndviValue);
    final color = NdviColormap.getColor(ndviValue, stops: NdviColormap.yemenStops);

    // Normalize to 0-1 for gauge (treating -1 to 1 as 0 to 1)
    final normalizedValue = ((ndviValue + 1) / 2).clamp(0.0, 1.0);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Background circle
              SizedBox(
                width: size,
                height: size,
                child: CircularProgressIndicator(
                  value: 1.0,
                  strokeWidth: size * 0.1,
                  color: Colors.grey[200],
                ),
              ),

              // Progress arc
              TweenAnimationBuilder<double>(
                duration: animate ? const Duration(milliseconds: 800) : Duration.zero,
                curve: Curves.easeOutCubic,
                tween: Tween(begin: 0, end: normalizedValue),
                builder: (context, value, child) {
                  return SizedBox(
                    width: size,
                    height: size,
                    child: CircularProgressIndicator(
                      value: value,
                      strokeWidth: size * 0.1,
                      color: color,
                      strokeCap: StrokeCap.round,
                    ),
                  );
                },
              ),

              // Center content
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    category.icon,
                    size: size * 0.3,
                    color: color,
                  ),
                  if (showValue)
                    Text(
                      ndviValue.toStringAsFixed(2),
                      style: TextStyle(
                        fontSize: size * 0.18,
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),

        if (showLabel) ...[
          const SizedBox(height: 8),
          Text(
            category.labelAr,
            style: TextStyle(
              fontSize: size * 0.15,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ],
    );
  }
}

/// Compact NDVI Badge
class NdviBadge extends StatelessWidget {
  final double ndviValue;
  final bool showTrend;
  final TrendDirection? trend;

  const NdviBadge({
    super.key,
    required this.ndviValue,
    this.showTrend = false,
    this.trend,
  });

  @override
  Widget build(BuildContext context) {
    final category = NdviHealthCategory.fromValue(ndviValue);
    final color = category.color;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(category.icon, size: 16, color: color),
          const SizedBox(width: 6),
          Text(
            'NDVI: ${ndviValue.toStringAsFixed(2)}',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          if (showTrend && trend != null) ...[
            const SizedBox(width: 6),
            Icon(trend!.icon, size: 14, color: trend!.color),
          ],
        ],
      ),
    );
  }
}

/// NDVI Legend Bar Widget
class NdviLegendBar extends StatelessWidget {
  final double width;
  final double height;
  final bool horizontal;
  final bool showLabels;

  const NdviLegendBar({
    super.key,
    this.width = 200,
    this.height = 20,
    this.horizontal = true,
    this.showLabels = true,
  });

  @override
  Widget build(BuildContext context) {
    final colors = NdviColormap.generateGradient(
      steps: 20,
      minNdvi: -1.0,
      maxNdvi: 1.0,
      stops: NdviColormap.yemenStops,
    );

    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: horizontal ? width : height,
          height: horizontal ? height : width,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(4),
            gradient: LinearGradient(
              colors: colors,
              begin: horizontal ? Alignment.centerLeft : Alignment.topCenter,
              end: horizontal ? Alignment.centerRight : Alignment.bottomCenter,
            ),
          ),
        ),
        if (showLabels) ...[
          const SizedBox(height: 4),
          SizedBox(
            width: width,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'ضعيف',
                  style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                ),
                Text(
                  'متوسط',
                  style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                ),
                Text(
                  'ممتاز',
                  style: TextStyle(fontSize: 10, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }
}

/// Full NDVI Legend Card
class NdviLegendCard extends StatelessWidget {
  const NdviLegendCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'مؤشر صحة النباتات (NDVI)',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ...NdviLegend.items.map((item) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      Container(
                        width: 24,
                        height: 24,
                        decoration: BoxDecoration(
                          color: item.color,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item.label,
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            Text(
                              item.range,
                              style: TextStyle(
                                fontSize: 10,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }
}

/// NDVI Time Series Chart (Simple version)
class NdviTrendChart extends StatelessWidget {
  final NdviStatistics statistics;
  final double height;

  const NdviTrendChart({
    super.key,
    required this.statistics,
    this.height = 120,
  });

  @override
  Widget build(BuildContext context) {
    if (statistics.history.isEmpty) {
      return SizedBox(
        height: height,
        child: const Center(
          child: Text('لا توجد بيانات تاريخية'),
        ),
      );
    }

    return SizedBox(
      height: height,
      child: CustomPaint(
        painter: _NdviChartPainter(statistics),
        size: Size.infinite,
      ),
    );
  }
}

class _NdviChartPainter extends CustomPainter {
  final NdviStatistics statistics;

  _NdviChartPainter(this.statistics);

  @override
  void paint(Canvas canvas, Size size) {
    if (statistics.history.isEmpty) return;

    final history = statistics.history;
    const padding = 20.0;
    final chartWidth = size.width - padding * 2;
    final chartHeight = size.height - padding * 2;

    // Draw grid
    final gridPaint = Paint()
      ..color = Colors.grey.withValues(alpha: 0.2)
      ..strokeWidth = 1;

    for (int i = 0; i <= 4; i++) {
      final y = padding + chartHeight * (i / 4);
      canvas.drawLine(
        Offset(padding, y),
        Offset(size.width - padding, y),
        gridPaint,
      );
    }

    // Calculate points
    final points = <Offset>[];
    final minValue = statistics.min;
    final maxValue = statistics.max;
    final range = maxValue - minValue;

    for (int i = 0; i < history.length; i++) {
      final x = history.length > 1
          ? padding + chartWidth * (i / (history.length - 1))
          : padding + chartWidth / 2;
      final normalizedY = range > 0
          ? (history[i].value - minValue) / range
          : 0.5;
      final y = size.height - padding - chartHeight * normalizedY;
      points.add(Offset(x, y));
    }

    // Draw line
    if (points.length > 1) {
      final path = Path()..moveTo(points.first.dx, points.first.dy);
      for (int i = 1; i < points.length; i++) {
        path.lineTo(points[i].dx, points[i].dy);
      }

      final linePaint = Paint()
        ..color = NdviColormap.getColor(statistics.current)
        ..strokeWidth = 2
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round;

      canvas.drawPath(path, linePaint);
    }

    // Draw points
    final pointPaint = Paint()
      ..color = NdviColormap.getColor(statistics.current)
      ..style = PaintingStyle.fill;

    for (int i = 0; i < points.length; i++) {
      final color = NdviColormap.getColor(history[i].value);
      pointPaint.color = color;
      canvas.drawCircle(points[i], 4, pointPaint);
    }
  }

  @override
  bool shouldRepaint(covariant _NdviChartPainter oldDelegate) {
    return oldDelegate.statistics != statistics;
  }
}

/// Spectral Health Indicator - Works with any SpectralIndex
/// Circular gauge showing current spectral index health status
class SpectralHealthIndicator extends StatelessWidget {
  final SpectralIndex index;
  final double value;
  final double size;
  final bool showLabel;
  final bool showValue;
  final bool animate;

  const SpectralHealthIndicator({
    super.key,
    required this.index,
    required this.value,
    this.size = 80,
    this.showLabel = true,
    this.showValue = true,
    this.animate = true,
  });

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    final color = SpectralColormap.getColor(index, value);
    final healthLabel = SpectralColormap.getHealthLabel(index, value, isArabic);

    // Normalize to 0-1 for gauge
    final range = index.maxValue - index.minValue;
    final normalizedValue = range > 0
        ? ((value - index.minValue) / range).clamp(0.0, 1.0)
        : 0.5;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Background circle
              SizedBox(
                width: size,
                height: size,
                child: CircularProgressIndicator(
                  value: 1.0,
                  strokeWidth: size * 0.1,
                  color: Colors.grey[200],
                ),
              ),

              // Progress arc
              TweenAnimationBuilder<double>(
                duration: animate
                    ? const Duration(milliseconds: 800)
                    : Duration.zero,
                curve: Curves.easeOutCubic,
                tween: Tween(begin: 0, end: normalizedValue),
                builder: (context, animValue, child) {
                  return SizedBox(
                    width: size,
                    height: size,
                    child: CircularProgressIndicator(
                      value: animValue,
                      strokeWidth: size * 0.1,
                      color: color,
                      strokeCap: StrokeCap.round,
                    ),
                  );
                },
              ),

              // Center content
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    index.icon,
                    size: size * 0.25,
                    color: color,
                  ),
                  if (showValue)
                    Text(
                      value.toStringAsFixed(2),
                      style: TextStyle(
                        fontSize: size * 0.16,
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                    ),
                  Text(
                    index.code,
                    style: TextStyle(
                      fontSize: size * 0.1,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),

        if (showLabel) ...[
          const SizedBox(height: 8),
          Text(
            healthLabel,
            style: TextStyle(
              fontSize: size * 0.14,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ],
    );
  }
}

/// Spectral Badge - Compact badge for any spectral index
class SpectralBadge extends StatelessWidget {
  final SpectralIndex index;
  final double value;

  const SpectralBadge({
    super.key,
    required this.index,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    final color = SpectralColormap.getColor(index, value);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(index.icon, size: 16, color: color),
          const SizedBox(width: 6),
          Text(
            '${index.code}: ${value.toStringAsFixed(2)}',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

/// Spectral Legend Card - Legend for any spectral index
class SpectralLegendCard extends StatelessWidget {
  final SpectralIndex index;

  const SpectralLegendCard({super.key, required this.index});

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    final legend = SpectralColormap.getLegend(index);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Icon(index.icon, size: 20, color: SpectralColormap.getColor(index, 0.6)),
                const SizedBox(width: 8),
                Text(
                  isArabic ? index.nameAr : index.name,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...legend.map((item) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    children: [
                      Container(
                        width: 24,
                        height: 24,
                        decoration: BoxDecoration(
                          color: item.color,
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              isArabic ? item.label : item.labelEn,
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            Text(
                              item.range,
                              style: TextStyle(
                                fontSize: 10,
                                color: Colors.grey[600],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }
}
