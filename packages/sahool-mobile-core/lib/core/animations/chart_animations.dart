import 'dart:math' as math;
import 'package:flutter/material.dart';

/// SAHOOL Chart Animations - تحريكات الرسوم البيانية
/// Animated chart components for data visualization
///
/// Features:
/// - Bar chart entry animations
/// - Line chart drawing animations
/// - Pie chart rotation
/// - Number counter animations

// =============================================================================
// BAR CHART ANIMATIONS - تحريكات الرسم الشريطي
// =============================================================================

/// Bar Chart Data
class BarData {
  final double value;
  final String label;
  final Color color;
  final String? tooltip;

  const BarData({
    required this.value,
    required this.label,
    required this.color,
    this.tooltip,
  });
}

/// Animated Bar Chart - رسم شريطي متحرك
class AnimatedBarChart extends StatefulWidget {
  final List<BarData> data;
  final double height;
  final Duration animationDuration;
  final Duration staggerDelay;
  final Curve curve;
  final double barWidth;
  final double spacing;
  final bool showLabels;
  final bool showValues;
  final TextStyle? labelStyle;
  final TextStyle? valueStyle;
  final bool horizontal;
  final Color? backgroundColor;
  final BorderRadius? barBorderRadius;

  const AnimatedBarChart({
    super.key,
    required this.data,
    this.height = 200,
    this.animationDuration = const Duration(milliseconds: 800),
    this.staggerDelay = const Duration(milliseconds: 100),
    this.curve = Curves.easeOutCubic,
    this.barWidth = 40,
    this.spacing = 20,
    this.showLabels = true,
    this.showValues = true,
    this.labelStyle,
    this.valueStyle,
    this.horizontal = false,
    this.backgroundColor,
    this.barBorderRadius,
  });

  @override
  State<AnimatedBarChart> createState() => _AnimatedBarChartState();
}

class _AnimatedBarChartState extends State<AnimatedBarChart>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _animations;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _startStaggeredAnimations();
  }

  void _initializeAnimations() {
    _controllers = List.generate(
      widget.data.length,
      (index) => AnimationController(
        duration: widget.animationDuration,
        vsync: this,
      ),
    );

    _animations = _controllers.map((controller) {
      return Tween<double>(begin: 0.0, end: 1.0).animate(
        CurvedAnimation(parent: controller, curve: widget.curve),
      );
    }).toList();
  }

  Future<void> _startStaggeredAnimations() async {
    for (int i = 0; i < _controllers.length; i++) {
      await Future.delayed(widget.staggerDelay);
      if (mounted) {
        _controllers[i].forward();
      }
    }
  }

  @override
  void didUpdateWidget(AnimatedBarChart oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.data != widget.data) {
      for (final controller in _controllers) {
        controller.dispose();
      }
      _initializeAnimations();
      _startStaggeredAnimations();
    }
  }

  @override
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  double get _maxValue =>
      widget.data.map((d) => d.value).reduce((a, b) => a > b ? a : b);

  @override
  Widget build(BuildContext context) {
    if (widget.horizontal) {
      return _buildHorizontalChart();
    }
    return _buildVerticalChart();
  }

  Widget _buildVerticalChart() {
    return SizedBox(
      height: widget.height,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        mainAxisAlignment: MainAxisAlignment.center,
        children: widget.data.asMap().entries.map((entry) {
          final index = entry.key;
          final data = entry.value;
          final barHeight = (data.value / _maxValue) * (widget.height - 40);

          return Padding(
            padding: EdgeInsets.symmetric(horizontal: widget.spacing / 2),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                if (widget.showValues)
                  AnimatedBuilder(
                    animation: _animations[index],
                    builder: (context, child) {
                      return Opacity(
                        opacity: _animations[index].value,
                        child: Text(
                          data.value.toStringAsFixed(1),
                          style: widget.valueStyle ??
                              TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: data.color,
                              ),
                        ),
                      );
                    },
                  ),
                const SizedBox(height: 4),
                AnimatedBuilder(
                  animation: _animations[index],
                  builder: (context, child) {
                    return Container(
                      width: widget.barWidth,
                      height: barHeight * _animations[index].value,
                      decoration: BoxDecoration(
                        color: data.color,
                        borderRadius: widget.barBorderRadius ??
                            const BorderRadius.vertical(top: Radius.circular(4)),
                        boxShadow: [
                          BoxShadow(
                            color: data.color.withValues(alpha: 0.3),
                            blurRadius: 8,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                    );
                  },
                ),
                if (widget.showLabels) ...[
                  const SizedBox(height: 8),
                  Text(
                    data.label,
                    style: widget.labelStyle ??
                        const TextStyle(fontSize: 10, color: Colors.grey),
                  ),
                ],
              ],
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildHorizontalChart() {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: widget.data.asMap().entries.map((entry) {
        final index = entry.key;
        final data = entry.value;

        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Row(
            children: [
              if (widget.showLabels)
                SizedBox(
                  width: 60,
                  child: Text(
                    data.label,
                    style: widget.labelStyle ??
                        const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ),
              Expanded(
                child: AnimatedBuilder(
                  animation: _animations[index],
                  builder: (context, child) {
                    return LayoutBuilder(
                      builder: (context, constraints) {
                        final barWidth =
                            (data.value / _maxValue) * constraints.maxWidth;
                        return Row(
                          children: [
                            Container(
                              height: widget.barWidth,
                              width: barWidth * _animations[index].value,
                              decoration: BoxDecoration(
                                color: data.color,
                                borderRadius: widget.barBorderRadius ??
                                    const BorderRadius.horizontal(
                                        right: Radius.circular(4)),
                              ),
                            ),
                            if (widget.showValues)
                              Padding(
                                padding: const EdgeInsets.only(left: 8),
                                child: Opacity(
                                  opacity: _animations[index].value,
                                  child: Text(
                                    data.value.toStringAsFixed(1),
                                    style: widget.valueStyle ??
                                        const TextStyle(
                                          fontSize: 12,
                                          fontWeight: FontWeight.bold,
                                        ),
                                  ),
                                ),
                              ),
                          ],
                        );
                      },
                    );
                  },
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }
}

// =============================================================================
// LINE CHART ANIMATIONS - تحريكات الرسم الخطي
// =============================================================================

/// Line Chart Data Point
class LineDataPoint {
  final double x;
  final double y;
  final String? label;

  const LineDataPoint({
    required this.x,
    required this.y,
    this.label,
  });
}

/// Line Chart Series
class LineSeries {
  final List<LineDataPoint> points;
  final Color color;
  final double strokeWidth;
  final bool showDots;
  final bool fillArea;
  final Color? fillColor;
  final String? name;

  const LineSeries({
    required this.points,
    this.color = Colors.blue,
    this.strokeWidth = 2,
    this.showDots = true,
    this.fillArea = false,
    this.fillColor,
    this.name,
  });
}

/// Animated Line Chart - رسم خطي متحرك
class AnimatedLineChart extends StatefulWidget {
  final List<LineSeries> series;
  final double height;
  final double width;
  final Duration animationDuration;
  final Curve curve;
  final bool showGrid;
  final bool showXLabels;
  final bool showYLabels;
  final Color gridColor;
  final int xDivisions;
  final int yDivisions;
  final EdgeInsets padding;

  const AnimatedLineChart({
    super.key,
    required this.series,
    this.height = 200,
    this.width = double.infinity,
    this.animationDuration = const Duration(milliseconds: 1200),
    this.curve = Curves.easeInOutCubic,
    this.showGrid = true,
    this.showXLabels = true,
    this.showYLabels = true,
    this.gridColor = const Color(0xFFE0E0E0),
    this.xDivisions = 5,
    this.yDivisions = 4,
    this.padding = const EdgeInsets.all(24),
  });

  @override
  State<AnimatedLineChart> createState() => _AnimatedLineChartState();
}

class _AnimatedLineChartState extends State<AnimatedLineChart>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _drawAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _drawAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: widget.curve),
    );
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: widget.height,
      width: widget.width,
      child: Padding(
        padding: widget.padding,
        child: AnimatedBuilder(
          animation: _drawAnimation,
          builder: (context, child) {
            return CustomPaint(
              size: Size(widget.width, widget.height),
              painter: _LineChartPainter(
                series: widget.series,
                progress: _drawAnimation.value,
                showGrid: widget.showGrid,
                gridColor: widget.gridColor,
                xDivisions: widget.xDivisions,
                yDivisions: widget.yDivisions,
              ),
            );
          },
        ),
      ),
    );
  }
}

class _LineChartPainter extends CustomPainter {
  final List<LineSeries> series;
  final double progress;
  final bool showGrid;
  final Color gridColor;
  final int xDivisions;
  final int yDivisions;

  _LineChartPainter({
    required this.series,
    required this.progress,
    required this.showGrid,
    required this.gridColor,
    required this.xDivisions,
    required this.yDivisions,
  });

  @override
  void paint(Canvas canvas, Size size) {
    // Calculate bounds
    double minX = double.infinity;
    double maxX = double.negativeInfinity;
    double minY = double.infinity;
    double maxY = double.negativeInfinity;

    for (final s in series) {
      for (final point in s.points) {
        minX = math.min(minX, point.x);
        maxX = math.max(maxX, point.x);
        minY = math.min(minY, point.y);
        maxY = math.max(maxY, point.y);
      }
    }

    // Add padding to Y range
    final yPadding = (maxY - minY) * 0.1;
    minY -= yPadding;
    maxY += yPadding;

    // Draw grid
    if (showGrid) {
      _drawGrid(canvas, size, minX, maxX, minY, maxY);
    }

    // Draw each series
    for (final s in series) {
      _drawSeries(canvas, size, s, minX, maxX, minY, maxY);
    }
  }

  void _drawGrid(
    Canvas canvas,
    Size size,
    double minX,
    double maxX,
    double minY,
    double maxY,
  ) {
    final gridPaint = Paint()
      ..color = gridColor
      ..strokeWidth = 1;

    // Vertical lines
    for (int i = 0; i <= xDivisions; i++) {
      final x = size.width * i / xDivisions;
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), gridPaint);
    }

    // Horizontal lines
    for (int i = 0; i <= yDivisions; i++) {
      final y = size.height * i / yDivisions;
      canvas.drawLine(Offset(0, y), Offset(size.width, y), gridPaint);
    }
  }

  void _drawSeries(
    Canvas canvas,
    Size size,
    LineSeries series,
    double minX,
    double maxX,
    double minY,
    double maxY,
  ) {
    if (series.points.isEmpty) return;

    final linePaint = Paint()
      ..color = series.color
      ..strokeWidth = series.strokeWidth
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    // Convert points to canvas coordinates
    final points = series.points.map((p) {
      final x = (p.x - minX) / (maxX - minX) * size.width;
      final y = size.height - (p.y - minY) / (maxY - minY) * size.height;
      return Offset(x, y);
    }).toList();

    // Create path
    final path = Path();
    path.moveTo(points.first.dx, points.first.dy);

    // Use smooth curves
    for (int i = 0; i < points.length - 1; i++) {
      final p0 = i > 0 ? points[i - 1] : points[i];
      final p1 = points[i];
      final p2 = points[i + 1];
      final p3 = i < points.length - 2 ? points[i + 2] : p2;

      final cp1 = Offset(
        p1.dx + (p2.dx - p0.dx) / 6,
        p1.dy + (p2.dy - p0.dy) / 6,
      );
      final cp2 = Offset(
        p2.dx - (p3.dx - p1.dx) / 6,
        p2.dy - (p3.dy - p1.dy) / 6,
      );

      path.cubicTo(cp1.dx, cp1.dy, cp2.dx, cp2.dy, p2.dx, p2.dy);
    }

    // Draw animated portion of path
    final pathMetrics = path.computeMetrics().first;
    final animatedPath = pathMetrics.extractPath(
      0,
      pathMetrics.length * progress,
    );

    // Fill area if enabled
    if (series.fillArea && progress > 0) {
      final fillPath = Path.from(animatedPath);
      final lastPoint = pathMetrics.getTangentForOffset(
        pathMetrics.length * progress,
      );
      if (lastPoint != null) {
        fillPath.lineTo(lastPoint.position.dx, size.height);
        fillPath.lineTo(points.first.dx, size.height);
        fillPath.close();

        final fillPaint = Paint()
          ..color = (series.fillColor ?? series.color).withValues(alpha: 0.2)
          ..style = PaintingStyle.fill;

        canvas.drawPath(fillPath, fillPaint);
      }
    }

    // Draw line
    canvas.drawPath(animatedPath, linePaint);

    // Draw dots
    if (series.showDots) {
      final dotPaint = Paint()
        ..color = series.color
        ..style = PaintingStyle.fill;

      final dotBorderPaint = Paint()
        ..color = Colors.white
        ..style = PaintingStyle.fill;

      final visiblePoints = (points.length * progress).ceil();
      for (int i = 0; i < visiblePoints && i < points.length; i++) {
        canvas.drawCircle(points[i], 6, dotBorderPaint);
        canvas.drawCircle(points[i], 4, dotPaint);
      }
    }
  }

  @override
  bool shouldRepaint(_LineChartPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

// =============================================================================
// PIE CHART ANIMATIONS - تحريكات الرسم الدائري
// =============================================================================

/// Pie Chart Segment
class PieSegment {
  final double value;
  final Color color;
  final String label;
  final String? tooltip;

  const PieSegment({
    required this.value,
    required this.color,
    required this.label,
    this.tooltip,
  });
}

/// Animated Pie Chart - رسم دائري متحرك
class AnimatedPieChart extends StatefulWidget {
  final List<PieSegment> segments;
  final double size;
  final double holeRadius;
  final Duration animationDuration;
  final Curve curve;
  final bool showLabels;
  final bool showPercentages;
  final TextStyle? labelStyle;
  final double startAngle;
  final Widget? centerWidget;
  final double explodeOffset;
  final int? selectedIndex;

  const AnimatedPieChart({
    super.key,
    required this.segments,
    this.size = 200,
    this.holeRadius = 0,
    this.animationDuration = const Duration(milliseconds: 1000),
    this.curve = Curves.easeOutCubic,
    this.showLabels = true,
    this.showPercentages = true,
    this.labelStyle,
    this.startAngle = -math.pi / 2,
    this.centerWidget,
    this.explodeOffset = 10,
    this.selectedIndex,
  });

  @override
  State<AnimatedPieChart> createState() => _AnimatedPieChartState();
}

class _AnimatedPieChartState extends State<AnimatedPieChart>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _sweepAnimation;
  late Animation<double> _rotationAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );

    _sweepAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: Interval(0.0, 0.8, curve: widget.curve),
      ),
    );

    _rotationAnimation = Tween<double>(begin: -0.1, end: 0.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.5, curve: Curves.easeOut),
      ),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  double get _totalValue =>
      widget.segments.map((s) => s.value).reduce((a, b) => a + b);

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              return Transform.rotate(
                angle: _rotationAnimation.value * 2 * math.pi,
                child: CustomPaint(
                  size: Size(widget.size, widget.size),
                  painter: _PieChartPainter(
                    segments: widget.segments,
                    progress: _sweepAnimation.value,
                    holeRadius: widget.holeRadius,
                    startAngle: widget.startAngle,
                    totalValue: _totalValue,
                    explodeOffset: widget.explodeOffset,
                    selectedIndex: widget.selectedIndex,
                  ),
                ),
              );
            },
          ),
          if (widget.centerWidget != null) widget.centerWidget!,
        ],
      ),
    );
  }
}

class _PieChartPainter extends CustomPainter {
  final List<PieSegment> segments;
  final double progress;
  final double holeRadius;
  final double startAngle;
  final double totalValue;
  final double explodeOffset;
  final int? selectedIndex;

  _PieChartPainter({
    required this.segments,
    required this.progress,
    required this.holeRadius,
    required this.startAngle,
    required this.totalValue,
    required this.explodeOffset,
    this.selectedIndex,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2;

    double currentAngle = startAngle;

    for (int i = 0; i < segments.length; i++) {
      final segment = segments[i];
      final sweepAngle = (segment.value / totalValue) * 2 * math.pi * progress;

      final isSelected = selectedIndex == i;
      final offset = isSelected ? explodeOffset : 0.0;

      // Calculate offset direction
      final midAngle = currentAngle + sweepAngle / 2;
      final offsetX = offset * math.cos(midAngle);
      final offsetY = offset * math.sin(midAngle);
      final segmentCenter = center + Offset(offsetX, offsetY);

      final paint = Paint()
        ..color = segment.color
        ..style = PaintingStyle.fill;

      // Draw segment
      final path = Path()
        ..moveTo(segmentCenter.dx, segmentCenter.dy)
        ..arcTo(
          Rect.fromCircle(center: segmentCenter, radius: radius),
          currentAngle,
          sweepAngle,
          false,
        )
        ..close();

      // Cut out hole if needed
      if (holeRadius > 0) {
        final holePath = Path()
          ..addOval(Rect.fromCircle(center: segmentCenter, radius: holeRadius));
        canvas.drawPath(
          Path.combine(PathOperation.difference, path, holePath),
          paint,
        );
      } else {
        canvas.drawPath(path, paint);
      }

      // Add shadow for selected segment
      if (isSelected) {
        final shadowPaint = Paint()
          ..color = segment.color.withValues(alpha: 0.3)
          ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 8);
        canvas.drawPath(path, shadowPaint);
      }

      currentAngle += sweepAngle;
    }
  }

  @override
  bool shouldRepaint(_PieChartPainter oldDelegate) {
    return oldDelegate.progress != progress ||
        oldDelegate.selectedIndex != selectedIndex;
  }
}

// =============================================================================
// NUMBER COUNTER ANIMATIONS - تحريكات عداد الأرقام
// =============================================================================

/// Animated Number Counter - عداد أرقام متحرك
class AnimatedNumberCounter extends StatefulWidget {
  final double value;
  final Duration duration;
  final Curve curve;
  final TextStyle? style;
  final String prefix;
  final String suffix;
  final int decimalPlaces;
  final String Function(double)? formatter;
  final bool animateOnUpdate;

  const AnimatedNumberCounter({
    super.key,
    required this.value,
    this.duration = const Duration(milliseconds: 1000),
    this.curve = Curves.easeOutCubic,
    this.style,
    this.prefix = '',
    this.suffix = '',
    this.decimalPlaces = 0,
    this.formatter,
    this.animateOnUpdate = true,
  });

  @override
  State<AnimatedNumberCounter> createState() => _AnimatedNumberCounterState();
}

class _AnimatedNumberCounterState extends State<AnimatedNumberCounter>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _valueAnimation;
  double _oldValue = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _valueAnimation = Tween<double>(
      begin: 0,
      end: widget.value,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));
    _controller.forward();
  }

  @override
  void didUpdateWidget(AnimatedNumberCounter oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.value != widget.value && widget.animateOnUpdate) {
      _oldValue = _valueAnimation.value;
      _valueAnimation = Tween<double>(
        begin: _oldValue,
        end: widget.value,
      ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));
      _controller.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  String _formatValue(double value) {
    if (widget.formatter != null) {
      return widget.formatter!(value);
    }
    return value.toStringAsFixed(widget.decimalPlaces);
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _valueAnimation,
      builder: (context, child) {
        return Text(
          '${widget.prefix}${_formatValue(_valueAnimation.value)}${widget.suffix}',
          style: widget.style ??
              Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
        );
      },
    );
  }
}

/// Animated Percentage Indicator - مؤشر نسبة مئوية متحرك
class AnimatedPercentageIndicator extends StatefulWidget {
  final double percentage;
  final double size;
  final Color backgroundColor;
  final Color progressColor;
  final Gradient? gradient;
  final double strokeWidth;
  final Duration duration;
  final Curve curve;
  final TextStyle? textStyle;
  final bool showPercentage;
  final Widget? centerWidget;

  const AnimatedPercentageIndicator({
    super.key,
    required this.percentage,
    this.size = 100,
    this.backgroundColor = const Color(0xFFE0E0E0),
    this.progressColor = const Color(0xFF1B5E20),
    this.gradient,
    this.strokeWidth = 10,
    this.duration = const Duration(milliseconds: 1000),
    this.curve = Curves.easeOutCubic,
    this.textStyle,
    this.showPercentage = true,
    this.centerWidget,
  });

  @override
  State<AnimatedPercentageIndicator> createState() =>
      _AnimatedPercentageIndicatorState();
}

class _AnimatedPercentageIndicatorState extends State<AnimatedPercentageIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _progressAnimation;
  double _oldPercentage = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _progressAnimation = Tween<double>(
      begin: 0,
      end: widget.percentage / 100,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));
    _controller.forward();
  }

  @override
  void didUpdateWidget(AnimatedPercentageIndicator oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.percentage != widget.percentage) {
      _oldPercentage = _progressAnimation.value;
      _progressAnimation = Tween<double>(
        begin: _oldPercentage,
        end: widget.percentage / 100,
      ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));
      _controller.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: AnimatedBuilder(
        animation: _progressAnimation,
        builder: (context, child) {
          return Stack(
            alignment: Alignment.center,
            children: [
              CustomPaint(
                size: Size(widget.size, widget.size),
                painter: _CircularProgressPainter(
                  progress: _progressAnimation.value,
                  strokeWidth: widget.strokeWidth,
                  backgroundColor: widget.backgroundColor,
                  progressColor: widget.progressColor,
                  gradient: widget.gradient,
                ),
              ),
              if (widget.centerWidget != null)
                widget.centerWidget!
              else if (widget.showPercentage)
                Text(
                  '${(_progressAnimation.value * 100).toInt()}%',
                  style: widget.textStyle ??
                      TextStyle(
                        fontSize: widget.size * 0.2,
                        fontWeight: FontWeight.bold,
                        color: widget.progressColor,
                      ),
                ),
            ],
          );
        },
      ),
    );
  }
}

class _CircularProgressPainter extends CustomPainter {
  final double progress;
  final double strokeWidth;
  final Color backgroundColor;
  final Color progressColor;
  final Gradient? gradient;

  _CircularProgressPainter({
    required this.progress,
    required this.strokeWidth,
    required this.backgroundColor,
    required this.progressColor,
    this.gradient,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    // Background circle
    final backgroundPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, backgroundPaint);

    // Progress arc
    final progressPaint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    if (gradient != null) {
      progressPaint.shader = gradient!.createShader(
        Rect.fromCircle(center: center, radius: radius),
      );
    } else {
      progressPaint.color = progressColor;
    }

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * progress,
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(_CircularProgressPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

/// Rolling Number Display - عرض أرقام متدحرجة
class RollingNumberDisplay extends StatefulWidget {
  final int value;
  final Duration duration;
  final TextStyle? style;
  final double digitHeight;

  const RollingNumberDisplay({
    super.key,
    required this.value,
    this.duration = const Duration(milliseconds: 1000),
    this.style,
    this.digitHeight = 40,
  });

  @override
  State<RollingNumberDisplay> createState() => _RollingNumberDisplayState();
}

class _RollingNumberDisplayState extends State<RollingNumberDisplay>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  int _oldValue = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _animation = Tween<double>(
      begin: 0,
      end: widget.value.toDouble(),
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic));
    _controller.forward();
  }

  @override
  void didUpdateWidget(RollingNumberDisplay oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.value != widget.value) {
      _oldValue = _animation.value.toInt();
      _animation = Tween<double>(
        begin: _oldValue.toDouble(),
        end: widget.value.toDouble(),
      ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic));
      _controller.forward(from: 0);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        final currentValue = _animation.value.toInt();
        final digits = currentValue.toString().split('');

        return Row(
          mainAxisSize: MainAxisSize.min,
          children: digits.map((digit) {
            return _RollingDigit(
              digit: int.parse(digit),
              height: widget.digitHeight,
              style: widget.style,
              animation: _animation,
            );
          }).toList(),
        );
      },
    );
  }
}

class _RollingDigit extends StatelessWidget {
  final int digit;
  final double height;
  final TextStyle? style;
  final Animation<double> animation;

  const _RollingDigit({
    required this.digit,
    required this.height,
    this.style,
    required this.animation,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: height,
      width: height * 0.6,
      child: ClipRect(
        child: Stack(
          children: List.generate(10, (index) {
            final offset = ((digit - index + 10) % 10) * height;
            return Positioned(
              top: -offset + (animation.value % 1) * height,
              child: SizedBox(
                height: height,
                child: Center(
                  child: Text(
                    index.toString(),
                    style: style ??
                        TextStyle(
                          fontSize: height * 0.7,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ),
              ),
            );
          }),
        ),
      ),
    );
  }
}
