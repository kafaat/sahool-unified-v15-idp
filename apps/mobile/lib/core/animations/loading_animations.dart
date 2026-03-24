import 'dart:math' as math;
import 'package:flutter/material.dart';

/// SAHOOL Loading Animations - تحريكات التحميل
/// Branded loading indicators and skeleton screens
///
/// Features:
/// - SAHOOL branded loader
/// - Skeleton with shimmer
/// - Progress animations
/// - Staggered list animations

// =============================================================================
// SAHOOL BRANDED LOADER - محمّل ساهول المميز
// =============================================================================

/// SAHOOL Branded Loader - محمّل ساهول
/// Agricultural-themed loading animation with wheat/leaf motif
class SahoolLoader extends StatefulWidget {
  final double size;
  final Color primaryColor;
  final Color secondaryColor;
  final Duration duration;
  final LoaderStyle style;

  const SahoolLoader({
    super.key,
    this.size = 64,
    this.primaryColor = const Color(0xFF1B5E20),
    this.secondaryColor = const Color(0xFF4CAF50),
    this.duration = const Duration(milliseconds: 1500),
    this.style = LoaderStyle.leaf,
  });

  @override
  State<SahoolLoader> createState() => _SahoolLoaderState();
}

enum LoaderStyle {
  leaf,      // Growing leaves
  wheat,     // Wheat harvest
  circular,  // Circular spinner
  pulse,     // Pulsing logo
  water,     // Water drop
}

class _SahoolLoaderState extends State<SahoolLoader>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        switch (widget.style) {
          case LoaderStyle.leaf:
            return _buildLeafLoader();
          case LoaderStyle.wheat:
            return _buildWheatLoader();
          case LoaderStyle.circular:
            return _buildCircularLoader();
          case LoaderStyle.pulse:
            return _buildPulseLoader();
          case LoaderStyle.water:
            return _buildWaterLoader();
        }
      },
    );
  }

  Widget _buildLeafLoader() {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: CustomPaint(
        painter: _LeafLoaderPainter(
          progress: _controller.value,
          primaryColor: widget.primaryColor,
          secondaryColor: widget.secondaryColor,
        ),
      ),
    );
  }

  Widget _buildWheatLoader() {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: Stack(
        alignment: Alignment.center,
        children: List.generate(6, (index) {
          final delay = index / 6;
          final animValue = ((_controller.value + delay) % 1.0);
          final scale = 0.5 + (math.sin(animValue * math.pi) * 0.5);
          final opacity = math.sin(animValue * math.pi);

          return Transform.rotate(
            angle: (index * math.pi / 3),
            child: Transform.translate(
              offset: Offset(0, -widget.size * 0.3),
              child: Transform.scale(
                scale: scale,
                child: Opacity(
                  opacity: opacity.clamp(0.3, 1.0),
                  child: Icon(
                    Icons.eco,
                    size: widget.size * 0.25,
                    color: index.isEven
                        ? widget.primaryColor
                        : widget.secondaryColor,
                  ),
                ),
              ),
            ),
          );
        }),
      ),
    );
  }

  Widget _buildCircularLoader() {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: CustomPaint(
        painter: _CircularLoaderPainter(
          progress: _controller.value,
          primaryColor: widget.primaryColor,
          secondaryColor: widget.secondaryColor,
        ),
      ),
    );
  }

  Widget _buildPulseLoader() {
    final scale = 0.8 + (math.sin(_controller.value * 2 * math.pi) * 0.2);
    final opacity = 0.6 + (math.sin(_controller.value * 2 * math.pi) * 0.4);

    return Transform.scale(
      scale: scale,
      child: Opacity(
        opacity: opacity,
        child: Container(
          width: widget.size,
          height: widget.size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: LinearGradient(
              colors: [widget.primaryColor, widget.secondaryColor],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            boxShadow: [
              BoxShadow(
                color: widget.primaryColor.withValues(alpha: 0.3),
                blurRadius: widget.size * 0.3,
                spreadRadius: widget.size * 0.1,
              ),
            ],
          ),
          child: Center(
            child: Icon(
              Icons.agriculture,
              size: widget.size * 0.5,
              color: Colors.white,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildWaterLoader() {
    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: CustomPaint(
        painter: _WaterDropPainter(
          progress: _controller.value,
          color: widget.primaryColor,
        ),
      ),
    );
  }
}

class _LeafLoaderPainter extends CustomPainter {
  final double progress;
  final Color primaryColor;
  final Color secondaryColor;

  _LeafLoaderPainter({
    required this.progress,
    required this.primaryColor,
    required this.secondaryColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width * 0.35;

    // Draw rotating leaves
    for (int i = 0; i < 8; i++) {
      final angle = (i / 8) * 2 * math.pi + (progress * 2 * math.pi);
      final leafProgress = ((progress + i / 8) % 1.0);
      final scale = 0.3 + (math.sin(leafProgress * math.pi) * 0.7);
      final opacity = math.sin(leafProgress * math.pi);

      final leafCenter = Offset(
        center.dx + radius * math.cos(angle),
        center.dy + radius * math.sin(angle),
      );

      final paint = Paint()
        ..color = (i.isEven ? primaryColor : secondaryColor)
            .withValues(alpha: opacity.clamp(0.2, 1.0))
        ..style = PaintingStyle.fill;

      // Draw leaf shape
      final path = Path();
      final leafSize = size.width * 0.12 * scale;

      path.moveTo(leafCenter.dx, leafCenter.dy - leafSize);
      path.quadraticBezierTo(
        leafCenter.dx + leafSize * 0.8,
        leafCenter.dy,
        leafCenter.dx,
        leafCenter.dy + leafSize,
      );
      path.quadraticBezierTo(
        leafCenter.dx - leafSize * 0.8,
        leafCenter.dy,
        leafCenter.dx,
        leafCenter.dy - leafSize,
      );

      canvas.save();
      canvas.translate(leafCenter.dx, leafCenter.dy);
      canvas.rotate(angle + math.pi / 2);
      canvas.translate(-leafCenter.dx, -leafCenter.dy);
      canvas.drawPath(path, paint);
      canvas.restore();
    }
  }

  @override
  bool shouldRepaint(_LeafLoaderPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

class _CircularLoaderPainter extends CustomPainter {
  final double progress;
  final Color primaryColor;
  final Color secondaryColor;

  _CircularLoaderPainter({
    required this.progress,
    required this.primaryColor,
    required this.secondaryColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;
    final strokeWidth = size.width * 0.1;

    // Background track
    final trackPaint = Paint()
      ..color = primaryColor.withValues(alpha: 0.2)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, trackPaint);

    // Animated arc
    final arcPaint = Paint()
      ..shader = SweepGradient(
        colors: [
          secondaryColor.withValues(alpha: 0.0),
          primaryColor,
          secondaryColor,
        ],
        stops: const [0.0, 0.5, 1.0],
        transform: GradientRotation(progress * 2 * math.pi - math.pi / 2),
      ).createShader(Rect.fromCircle(center: center, radius: radius))
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    final sweepAngle = math.pi * 1.5 * (math.sin(progress * math.pi * 2) * 0.3 + 0.7);

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      progress * 2 * math.pi - math.pi / 2,
      sweepAngle,
      false,
      arcPaint,
    );
  }

  @override
  bool shouldRepaint(_CircularLoaderPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

class _WaterDropPainter extends CustomPainter {
  final double progress;
  final Color color;

  _WaterDropPainter({
    required this.progress,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);

    // Draw multiple concentric water drops
    for (int i = 0; i < 3; i++) {
      final dropProgress = ((progress + i / 3) % 1.0);
      final scale = dropProgress;
      final opacity = 1.0 - dropProgress;

      final paint = Paint()
        ..color = color.withValues(alpha: opacity * 0.6)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2;

      final dropPath = Path();
      final dropSize = size.width * 0.4 * scale;

      dropPath.moveTo(center.dx, center.dy - dropSize);
      dropPath.quadraticBezierTo(
        center.dx + dropSize * 0.8,
        center.dy,
        center.dx,
        center.dy + dropSize * 0.8,
      );
      dropPath.quadraticBezierTo(
        center.dx - dropSize * 0.8,
        center.dy,
        center.dx,
        center.dy - dropSize,
      );

      canvas.drawPath(dropPath, paint);
    }
  }

  @override
  bool shouldRepaint(_WaterDropPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

// =============================================================================
// SKELETON WITH SHIMMER - هيكل مع لمعان
// =============================================================================

/// Skeleton Widget with Shimmer Effect - عنصر الهيكل مع تأثير اللمعان
class SkeletonWithShimmer extends StatefulWidget {
  final double width;
  final double height;
  final BorderRadius borderRadius;
  final Color baseColor;
  final Color highlightColor;
  final Duration duration;

  const SkeletonWithShimmer({
    super.key,
    this.width = double.infinity,
    this.height = 20,
    this.borderRadius = const BorderRadius.all(Radius.circular(8)),
    this.baseColor = const Color(0xFFE0E0E0),
    this.highlightColor = const Color(0xFFF5F5F5),
    this.duration = const Duration(milliseconds: 1500),
  });

  @override
  State<SkeletonWithShimmer> createState() => _SkeletonWithShimmerState();
}

class _SkeletonWithShimmerState extends State<SkeletonWithShimmer>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _shimmerAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    )..repeat();

    _shimmerAnimation = Tween<double>(begin: -2, end: 2).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOutSine),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _shimmerAnimation,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: widget.borderRadius,
            gradient: LinearGradient(
              begin: Alignment(_shimmerAnimation.value - 1, 0),
              end: Alignment(_shimmerAnimation.value + 1, 0),
              colors: [
                widget.baseColor,
                widget.highlightColor,
                widget.baseColor,
              ],
              stops: const [0.0, 0.5, 1.0],
            ),
          ),
        );
      },
    );
  }
}

/// Skeleton Card - بطاقة هيكلية
/// Complete card skeleton with multiple elements
class SkeletonCard extends StatelessWidget {
  final double height;
  final bool hasImage;
  final bool hasSubtitle;
  final int textLines;

  const SkeletonCard({
    super.key,
    this.height = 120,
    this.hasImage = true,
    this.hasSubtitle = true,
    this.textLines = 2,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: height,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          if (hasImage) ...[
            const SkeletonWithShimmer(
              width: 80,
              height: 80,
              borderRadius: BorderRadius.all(Radius.circular(12)),
            ),
            const SizedBox(width: 16),
          ],
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SkeletonWithShimmer(
                  width: 140,
                  height: 18,
                ),
                if (hasSubtitle) ...[
                  const SizedBox(height: 8),
                  const SkeletonWithShimmer(
                    width: 100,
                    height: 14,
                  ),
                ],
                const SizedBox(height: 12),
                ...List.generate(
                  textLines,
                  (index) => Padding(
                    padding: const EdgeInsets.only(bottom: 6),
                    child: SkeletonWithShimmer(
                      width: index == textLines - 1 ? 150 : double.infinity,
                      height: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Skeleton List - قائمة هيكلية
class SkeletonList extends StatelessWidget {
  final int itemCount;
  final double itemHeight;
  final EdgeInsets padding;
  final double spacing;

  const SkeletonList({
    super.key,
    this.itemCount = 5,
    this.itemHeight = 100,
    this.padding = const EdgeInsets.all(16),
    this.spacing = 12,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: padding,
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      itemCount: itemCount,
      separatorBuilder: (context, index) => SizedBox(height: spacing),
      itemBuilder: (context, index) {
        return SkeletonCard(height: itemHeight);
      },
    );
  }
}

/// Skeleton Grid - شبكة هيكلية
class SkeletonGrid extends StatelessWidget {
  final int itemCount;
  final int crossAxisCount;
  final double childAspectRatio;
  final EdgeInsets padding;
  final double spacing;

  const SkeletonGrid({
    super.key,
    this.itemCount = 6,
    this.crossAxisCount = 2,
    this.childAspectRatio = 1.0,
    this.padding = const EdgeInsets.all(16),
    this.spacing = 12,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      padding: padding,
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        crossAxisSpacing: spacing,
        mainAxisSpacing: spacing,
        childAspectRatio: childAspectRatio,
      ),
      itemCount: itemCount,
      itemBuilder: (context, index) {
        return DecoratedBox(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.05),
                blurRadius: 10,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                flex: 3,
                child: ClipRRect(
                  borderRadius: BorderRadius.vertical(
                    top: Radius.circular(16),
                  ),
                  child: SkeletonWithShimmer(
                    width: double.infinity,
                    height: double.infinity,
                    borderRadius: BorderRadius.zero,
                  ),
                ),
              ),
              Expanded(
                flex: 2,
                child: Padding(
                  padding: EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      SkeletonWithShimmer(
                        width: double.infinity,
                        height: 14,
                      ),
                      SkeletonWithShimmer(
                        width: 80,
                        height: 12,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

// =============================================================================
// PROGRESS ANIMATIONS - تحريكات التقدم
// =============================================================================

/// Animated Progress Bar - شريط تقدم متحرك
class AnimatedProgressBar extends StatefulWidget {
  final double progress;
  final double height;
  final Color backgroundColor;
  final Color progressColor;
  final Gradient? gradient;
  final BorderRadius borderRadius;
  final Duration animationDuration;
  final bool showPercentage;
  final TextStyle? percentageStyle;

  const AnimatedProgressBar({
    super.key,
    required this.progress,
    this.height = 12,
    this.backgroundColor = const Color(0xFFE0E0E0),
    this.progressColor = const Color(0xFF1B5E20),
    this.gradient,
    this.borderRadius = const BorderRadius.all(Radius.circular(6)),
    this.animationDuration = const Duration(milliseconds: 500),
    this.showPercentage = false,
    this.percentageStyle,
  });

  @override
  State<AnimatedProgressBar> createState() => _AnimatedProgressBarState();
}

class _AnimatedProgressBarState extends State<AnimatedProgressBar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _progressAnimation;
  double _oldProgress = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _progressAnimation = Tween<double>(
      begin: 0,
      end: widget.progress,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic));
    _controller.forward();
  }

  @override
  void didUpdateWidget(AnimatedProgressBar oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.progress != widget.progress) {
      _oldProgress = _progressAnimation.value;
      _progressAnimation = Tween<double>(
        begin: _oldProgress,
        end: widget.progress,
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
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (widget.showPercentage)
          AnimatedBuilder(
            animation: _progressAnimation,
            builder: (context, child) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  '${(_progressAnimation.value * 100).toInt()}%',
                  style: widget.percentageStyle ??
                      const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                ),
              );
            },
          ),
        Container(
          height: widget.height,
          decoration: BoxDecoration(
            color: widget.backgroundColor,
            borderRadius: widget.borderRadius,
          ),
          child: AnimatedBuilder(
            animation: _progressAnimation,
            builder: (context, child) {
              return FractionallySizedBox(
                alignment: Alignment.centerLeft,
                widthFactor: _progressAnimation.value.clamp(0.0, 1.0),
                child: Container(
                  decoration: BoxDecoration(
                    borderRadius: widget.borderRadius,
                    gradient: widget.gradient,
                    color: widget.gradient == null ? widget.progressColor : null,
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

/// Circular Progress - تقدم دائري
class AnimatedCircularProgress extends StatefulWidget {
  final double progress;
  final double size;
  final double strokeWidth;
  final Color backgroundColor;
  final Color progressColor;
  final Gradient? gradient;
  final Duration animationDuration;
  final Widget? child;
  final bool showPercentage;

  const AnimatedCircularProgress({
    super.key,
    required this.progress,
    this.size = 100,
    this.strokeWidth = 10,
    this.backgroundColor = const Color(0xFFE0E0E0),
    this.progressColor = const Color(0xFF1B5E20),
    this.gradient,
    this.animationDuration = const Duration(milliseconds: 800),
    this.child,
    this.showPercentage = true,
  });

  @override
  State<AnimatedCircularProgress> createState() =>
      _AnimatedCircularProgressState();
}

class _AnimatedCircularProgressState extends State<AnimatedCircularProgress>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _progressAnimation;
  double _oldProgress = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _progressAnimation = Tween<double>(
      begin: 0,
      end: widget.progress,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic));
    _controller.forward();
  }

  @override
  void didUpdateWidget(AnimatedCircularProgress oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.progress != widget.progress) {
      _oldProgress = _progressAnimation.value;
      _progressAnimation = Tween<double>(
        begin: _oldProgress,
        end: widget.progress,
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
              if (widget.child != null)
                widget.child!
              else if (widget.showPercentage)
                Text(
                  '${(_progressAnimation.value * 100).toInt()}%',
                  style: TextStyle(
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

// =============================================================================
// STAGGERED LIST ANIMATIONS - قوائم متحركة متتابعة
// =============================================================================

/// Staggered Animation List - قائمة متحركة متتابعة
class StaggeredAnimationList extends StatefulWidget {
  final List<Widget> children;
  final Duration itemDuration;
  final Duration staggerDelay;
  final Offset slideOffset;
  final Curve curve;
  final ScrollController? scrollController;
  final EdgeInsets? padding;
  final bool shrinkWrap;
  final ScrollPhysics? physics;

  const StaggeredAnimationList({
    super.key,
    required this.children,
    this.itemDuration = const Duration(milliseconds: 400),
    this.staggerDelay = const Duration(milliseconds: 80),
    this.slideOffset = const Offset(0, 50),
    this.curve = Curves.easeOutCubic,
    this.scrollController,
    this.padding,
    this.shrinkWrap = false,
    this.physics,
  });

  @override
  State<StaggeredAnimationList> createState() => _StaggeredAnimationListState();
}

class _StaggeredAnimationListState extends State<StaggeredAnimationList>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  late List<Animation<double>> _fadeAnimations;
  late List<Animation<Offset>> _slideAnimations;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _startStaggeredAnimations();
  }

  void _initializeAnimations() {
    _controllers = List.generate(
      widget.children.length,
      (index) => AnimationController(
        duration: widget.itemDuration,
        vsync: this,
      ),
    );

    _fadeAnimations = _controllers.map((controller) {
      return Tween<double>(begin: 0.0, end: 1.0).animate(
        CurvedAnimation(parent: controller, curve: widget.curve),
      );
    }).toList();

    _slideAnimations = _controllers.map((controller) {
      return Tween<Offset>(begin: widget.slideOffset, end: Offset.zero).animate(
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
  void dispose() {
    for (final controller in _controllers) {
      controller.dispose();
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      controller: widget.scrollController,
      padding: widget.padding,
      shrinkWrap: widget.shrinkWrap,
      physics: widget.physics,
      itemCount: widget.children.length,
      itemBuilder: (context, index) {
        return AnimatedBuilder(
          animation: _controllers[index],
          builder: (context, child) {
            return Transform.translate(
              offset: _slideAnimations[index].value,
              child: Opacity(
                opacity: _fadeAnimations[index].value,
                child: widget.children[index],
              ),
            );
          },
        );
      },
    );
  }
}

/// Animated List Item - عنصر قائمة متحرك
/// Wrap individual items for animation
class AnimatedListItem extends StatefulWidget {
  final Widget child;
  final int index;
  final Duration duration;
  final Duration delay;
  final Curve curve;
  final Offset? slideOffset;
  final double? initialScale;

  const AnimatedListItem({
    super.key,
    required this.child,
    required this.index,
    this.duration = const Duration(milliseconds: 400),
    this.delay = const Duration(milliseconds: 50),
    this.curve = Curves.easeOutCubic,
    this.slideOffset,
    this.initialScale,
  });

  @override
  State<AnimatedListItem> createState() => _AnimatedListItemState();
}

class _AnimatedListItemState extends State<AnimatedListItem>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: widget.curve),
    );

    _slideAnimation = Tween<Offset>(
      begin: widget.slideOffset ?? const Offset(0, 30),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));

    _scaleAnimation = Tween<double>(
      begin: widget.initialScale ?? 0.95,
      end: 1.0,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));

    _startAnimation();
  }

  Future<void> _startAnimation() async {
    await Future.delayed(
      Duration(milliseconds: widget.delay.inMilliseconds * widget.index),
    );
    if (mounted) {
      _controller.forward();
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
      animation: _controller,
      builder: (context, child) {
        return Transform.translate(
          offset: _slideAnimation.value,
          child: Transform.scale(
            scale: _scaleAnimation.value,
            child: Opacity(
              opacity: _fadeAnimation.value,
              child: widget.child,
            ),
          ),
        );
      },
    );
  }
}

// =============================================================================
// LOADING OVERLAY - طبقة التحميل
// =============================================================================

/// Loading Overlay - طبقة التحميل
/// Shows loading indicator over content
class LoadingOverlay extends StatelessWidget {
  final bool isLoading;
  final Widget child;
  final Widget? loadingWidget;
  final Color? overlayColor;
  final bool dismissible;

  const LoadingOverlay({
    super.key,
    required this.isLoading,
    required this.child,
    this.loadingWidget,
    this.overlayColor,
    this.dismissible = false,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (isLoading)
          Positioned.fill(
            child: GestureDetector(
              onTap: dismissible ? null : () {},
              child: AnimatedOpacity(
                opacity: isLoading ? 1.0 : 0.0,
                duration: const Duration(milliseconds: 200),
                child: ColoredBox(
                  color: overlayColor ?? Colors.black.withValues(alpha: 0.3),
                  child: Center(
                    child: loadingWidget ?? const SahoolLoader(),
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

/// Full Screen Loading - تحميل كامل الشاشة
class FullScreenLoading extends StatelessWidget {
  final String? message;
  final Color? backgroundColor;

  const FullScreenLoading({
    super.key,
    this.message,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor ?? Theme.of(context).scaffoldBackgroundColor,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const SahoolLoader(size: 80),
            if (message != null) ...[
              const SizedBox(height: 24),
              Text(
                message!,
                style: Theme.of(context).textTheme.titleMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
