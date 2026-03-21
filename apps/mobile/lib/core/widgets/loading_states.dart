import 'package:flutter/material.dart';
import '../theme/sahool_theme.dart';

/// SAHOOL Loading States Widgets
/// مكونات حالات التحميل الموحدة
///
/// Provides consistent loading UI across the app with:
/// - Shimmer effects for skeleton loading
/// - Content-specific skeleton loaders
/// - Progress indicators with bilingual messages
/// - Animated transitions

// ═══════════════════════════════════════════════════════════════════════════
// Shimmer Loading Effect
// تأثير اللمعان للتحميل
// ═══════════════════════════════════════════════════════════════════════════

/// Shimmer effect widget for loading placeholders
/// مكون تأثير اللمعان للعناصر النائبة أثناء التحميل
class SahoolShimmer extends StatefulWidget {
  final Widget child;
  final bool enabled;
  final Color? baseColor;
  final Color? highlightColor;

  const SahoolShimmer({
    super.key,
    required this.child,
    this.enabled = true,
    this.baseColor,
    this.highlightColor,
  });

  @override
  State<SahoolShimmer> createState() => _SahoolShimmerState();
}

class _SahoolShimmerState extends State<SahoolShimmer>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();

    _animation = Tween<double>(begin: -1, end: 2).animate(
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
    if (!widget.enabled) return widget.child;

    final baseColor = widget.baseColor ?? Colors.grey[300]!;
    final highlightColor = widget.highlightColor ?? Colors.grey[100]!;

    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                baseColor,
                highlightColor,
                baseColor,
              ],
              stops: [
                (_animation.value - 0.3).clamp(0.0, 1.0),
                _animation.value.clamp(0.0, 1.0),
                (_animation.value + 0.3).clamp(0.0, 1.0),
              ],
            ).createShader(bounds);
          },
          blendMode: BlendMode.srcATop,
          child: widget.child,
        );
      },
      child: widget.child,
    );
  }
}

/// Shimmer container for consistent styling
/// حاوية اللمعان للتنسيق الموحد
class ShimmerContainer extends StatelessWidget {
  final double? width;
  final double height;
  final double borderRadius;
  final EdgeInsets? margin;

  const ShimmerContainer({
    super.key,
    this.width,
    required this.height,
    this.borderRadius = 8,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
      margin: margin,
      decoration: BoxDecoration(
        color: Colors.grey[300],
        borderRadius: BorderRadius.circular(borderRadius),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Generic Skeleton Loaders
// الهياكل العامة للتحميل
// ═══════════════════════════════════════════════════════════════════════════

/// Shimmer Card placeholder
/// بطاقة نائبة بتأثير اللمعان
class SkeletonCard extends StatelessWidget {
  final double height;
  final double? width;
  final double borderRadius;
  final EdgeInsets? margin;
  final EdgeInsets? padding;
  final Widget? child;

  const SkeletonCard({
    super.key,
    this.height = 120,
    this.width,
    this.borderRadius = 16,
    this.margin,
    this.padding,
    this.child,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolShimmer(
      child: Container(
        height: height,
        width: width,
        margin: margin ?? const EdgeInsets.symmetric(vertical: 6),
        padding: padding,
        decoration: BoxDecoration(
          color: Colors.grey[300],
          borderRadius: BorderRadius.circular(borderRadius),
        ),
        child: child,
      ),
    );
  }
}

/// Shimmer List placeholder
/// قائمة نائبة بتأثير اللمعان
class SkeletonList extends StatelessWidget {
  final int itemCount;
  final double itemHeight;
  final double spacing;
  final EdgeInsets? padding;
  final Widget Function(int index)? itemBuilder;

  const SkeletonList({
    super.key,
    this.itemCount = 5,
    this.itemHeight = 80,
    this.spacing = 12,
    this.padding,
    this.itemBuilder,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      padding: padding ?? const EdgeInsets.all(16),
      itemCount: itemCount,
      separatorBuilder: (_, __) => SizedBox(height: spacing),
      itemBuilder: (context, index) =>
          itemBuilder?.call(index) ?? SkeletonCard(height: itemHeight),
    );
  }
}

/// Shimmer Grid placeholder
/// شبكة نائبة بتأثير اللمعان
class SkeletonGrid extends StatelessWidget {
  final int itemCount;
  final int crossAxisCount;
  final double childAspectRatio;
  final EdgeInsets? padding;

  const SkeletonGrid({
    super.key,
    this.itemCount = 6,
    this.crossAxisCount = 2,
    this.childAspectRatio = 1.0,
    this.padding,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      padding: padding ?? const EdgeInsets.all(16),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        childAspectRatio: childAspectRatio,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: itemCount,
      itemBuilder: (_, __) => const SkeletonCard(),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Content-Specific Skeleton Loaders
// الهياكل المخصصة للمحتوى
// ═══════════════════════════════════════════════════════════════════════════

/// Field card skeleton loader
/// هيكل بطاقة الحقل
class FieldCardSkeleton extends StatelessWidget {
  final bool isCompact;

  const FieldCardSkeleton({
    super.key,
    this.isCompact = false,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolShimmer(
      child: Container(
        height: isCompact ? 160 : 140,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.grey[200]!),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header row
            Row(
              children: [
                // Icon placeholder
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                const SizedBox(width: 12),
                // Title and subtitle
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      ShimmerContainer(width: 120, height: 16),
                      SizedBox(height: 8),
                      ShimmerContainer(width: 80, height: 12),
                    ],
                  ),
                ),
                // Health indicator
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    shape: BoxShape.circle,
                  ),
                ),
              ],
            ),
            const Spacer(),
            // Bottom row - stats
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: List.generate(
                3,
                (_) => const Column(
                  children: [
                    ShimmerContainer(width: 40, height: 10),
                    SizedBox(height: 4),
                    ShimmerContainer(width: 50, height: 14),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Fields list skeleton loader
/// هيكل قائمة الحقول
class FieldsListSkeleton extends StatelessWidget {
  final int count;
  final bool isGrid;

  const FieldsListSkeleton({
    super.key,
    this.count = 5,
    this.isGrid = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isGrid) {
      return GridView.builder(
        physics: const NeverScrollableScrollPhysics(),
        shrinkWrap: true,
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 0.85,
        ),
        itemCount: count,
        itemBuilder: (_, __) => const FieldCardSkeleton(isCompact: true),
      );
    }

    return ListView.builder(
      physics: const NeverScrollableScrollPhysics(),
      shrinkWrap: true,
      padding: const EdgeInsets.all(16),
      itemCount: count,
      itemBuilder: (_, index) => const Padding(
        padding: EdgeInsets.only(bottom: 12),
        child: FieldCardSkeleton(),
      ),
    );
  }
}

/// Weather card skeleton loader
/// هيكل بطاقة الطقس
class WeatherCardSkeleton extends StatelessWidget {
  const WeatherCardSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SahoolShimmer(
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.grey[300]!, Colors.grey[200]!],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Location and date
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                ShimmerContainer(width: 100, height: 14),
                ShimmerContainer(width: 80, height: 14),
              ],
            ),
            const SizedBox(height: 24),
            // Temperature
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Weather icon placeholder
                Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    color: Colors.grey[200],
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                const SizedBox(width: 16),
                const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    ShimmerContainer(width: 100, height: 48),
                    SizedBox(height: 8),
                    ShimmerContainer(width: 80, height: 16),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 24),
            // Weather details row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: List.generate(
                4,
                (_) => const Column(
                  children: [
                    ShimmerContainer(width: 24, height: 24),
                    SizedBox(height: 8),
                    ShimmerContainer(width: 40, height: 12),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Weather screen skeleton loader
/// هيكل شاشة الطقس
class WeatherScreenSkeleton extends StatelessWidget {
  const WeatherScreenSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Current weather card
          const WeatherCardSkeleton(),
          const SizedBox(height: 24),
          // Hourly section title
          const SahoolShimmer(child: ShimmerContainer(width: 120, height: 18)),
          const SizedBox(height: 12),
          // Hourly forecast
          SizedBox(
            height: 100,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: 6,
              itemBuilder: (_, __) => SahoolShimmer(
                child: Container(
                  width: 70,
                  margin: const EdgeInsets.only(right: 12),
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 24),
          // Daily section title
          const SahoolShimmer(child: ShimmerContainer(width: 140, height: 18)),
          const SizedBox(height: 12),
          // Daily forecast
          ...List.generate(
            5,
            (_) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: SahoolShimmer(
                child: Container(
                  height: 60,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Map skeleton loader
/// هيكل تحميل الخريطة
class MapSkeleton extends StatelessWidget {
  final String? message;
  final String? messageAr;

  const MapSkeleton({
    super.key,
    this.message,
    this.messageAr,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.grey[200],
      child: Stack(
        children: [
          // Grid pattern to simulate map
          CustomPaint(
            painter: _MapGridPainter(),
            size: Size.infinite,
          ),
          // Loading overlay
          Center(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.95),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 20,
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const SahoolLoadingSpinner(size: 40),
                  const SizedBox(height: 16),
                  Text(
                    messageAr ?? 'جاري تحميل الخريطة...',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 16,
                      color: SahoolColors.textDark,
                    ),
                  ),
                  if (message != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      message!,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Grid painter for map skeleton
class _MapGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.grey[300]!
      ..strokeWidth = 0.5;

    const spacing = 40.0;

    // Vertical lines
    for (double x = 0; x < size.width; x += spacing) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }

    // Horizontal lines
    for (double y = 0; y < size.height; y += spacing) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// NDVI/Vegetation index loading skeleton
/// هيكل تحميل مؤشر الغطاء النباتي
class NdviSkeleton extends StatelessWidget {
  const NdviSkeleton({super.key});

  @override
  Widget build(BuildContext context) {
    return SahoolShimmer(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.grey[200]!),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                ShimmerContainer(width: 100, height: 18),
                ShimmerContainer(width: 80, height: 14),
              ],
            ),
            const SizedBox(height: 20),
            // NDVI visualization placeholder
            Container(
              height: 180,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Center(
                child: Icon(
                  Icons.grass,
                  size: 48,
                  color: Colors.grey,
                ),
              ),
            ),
            const SizedBox(height: 16),
            // Color scale
            Container(
              height: 24,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(4),
                gradient: LinearGradient(
                  colors: [
                    Colors.grey[400]!,
                    Colors.grey[300]!,
                    Colors.grey[200]!,
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            // Stats row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: List.generate(
                4,
                (_) => const Column(
                  children: [
                    ShimmerContainer(width: 50, height: 12),
                    SizedBox(height: 4),
                    ShimmerContainer(width: 40, height: 20),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Chart/Analytics skeleton loader
/// هيكل تحميل الرسوم البيانية
class ChartSkeleton extends StatelessWidget {
  final double height;

  const ChartSkeleton({
    super.key,
    this.height = 200,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolShimmer(
      child: Container(
        height: height,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.grey[200]!),
        ),
        child: Column(
          children: [
            // Title
            const Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                ShimmerContainer(width: 100, height: 16),
                ShimmerContainer(width: 60, height: 14),
              ],
            ),
            const SizedBox(height: 20),
            // Chart area with bars
            Expanded(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: List.generate(
                  7,
                  (index) => Container(
                    width: 28,
                    height: (index + 1) * 15.0 + 20,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: const BorderRadius.vertical(
                        top: Radius.circular(4),
                      ),
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
            // X-axis labels
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: List.generate(
                7,
                (_) => const ShimmerContainer(width: 24, height: 10),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Loading Indicators
// مؤشرات التحميل
// ═══════════════════════════════════════════════════════════════════════════

/// Full screen loading indicator
/// مؤشر تحميل بملء الشاشة
class SahoolLoadingScreen extends StatelessWidget {
  final String? message;
  final String? messageAr;
  final bool showLogo;

  const SahoolLoadingScreen({
    super.key,
    this.message,
    this.messageAr,
    this.showLogo = false,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.background,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (showLogo) ...[
              // SAHOOL logo placeholder
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: SahoolColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Icon(
                  Icons.grass,
                  size: 48,
                  color: SahoolColors.primary,
                ),
              ),
              const SizedBox(height: 32),
            ],
            const SahoolLoadingSpinner(size: 48),
            if (messageAr != null || message != null) ...[
              const SizedBox(height: 24),
              if (messageAr != null)
                Text(
                  messageAr!,
                  style: const TextStyle(
                    color: SahoolColors.textDark,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                  textAlign: TextAlign.center,
                ),
              if (message != null) ...[
                const SizedBox(height: 4),
                Text(
                  message!,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ],
          ],
        ),
      ),
    );
  }
}

/// Custom loading spinner with SAHOOL branding
/// مؤشر تحميل مخصص بهوية سهول
class SahoolLoadingSpinner extends StatefulWidget {
  final double size;
  final Color? color;
  final double strokeWidth;

  const SahoolLoadingSpinner({
    super.key,
    this.size = 32,
    this.color,
    this.strokeWidth = 3,
  });

  @override
  State<SahoolLoadingSpinner> createState() => _SahoolLoadingSpinnerState();
}

class _SahoolLoadingSpinnerState extends State<SahoolLoadingSpinner>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
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
      child: CircularProgressIndicator(
        strokeWidth: widget.strokeWidth,
        valueColor: AlwaysStoppedAnimation<Color>(
          widget.color ?? SahoolColors.primary,
        ),
      ),
    );
  }
}

/// Loading overlay for async operations
/// طبقة تحميل للعمليات غير المتزامنة
class SahoolLoadingOverlay extends StatelessWidget {
  final bool isLoading;
  final Widget child;
  final String? message;
  final String? messageAr;
  final bool dismissible;

  const SahoolLoadingOverlay({
    super.key,
    required this.isLoading,
    required this.child,
    this.message,
    this.messageAr,
    this.dismissible = false,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        child,
        if (isLoading)
          GestureDetector(
            onTap: dismissible ? () {} : null,
            child: ColoredBox(
              color: Colors.black.withOpacity(0.3),
              child: Center(
                child: Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 20,
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const SahoolLoadingSpinner(size: 40),
                      if (messageAr != null || message != null) ...[
                        const SizedBox(height: 16),
                        if (messageAr != null)
                          Text(
                            messageAr!,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: SahoolColors.textDark,
                            ),
                          ),
                        if (message != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            message!,
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

/// Inline loading indicator
/// مؤشر تحميل مضمن
class SahoolInlineLoading extends StatelessWidget {
  final String? message;
  final String? messageAr;
  final MainAxisAlignment alignment;

  const SahoolInlineLoading({
    super.key,
    this.message,
    this.messageAr,
    this.alignment = MainAxisAlignment.center,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: alignment,
        children: [
          const SahoolLoadingSpinner(size: 20),
          if (messageAr != null || message != null) ...[
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                if (messageAr != null)
                  Text(
                    messageAr!,
                    style: const TextStyle(
                      color: SahoolColors.textDark,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                if (message != null)
                  Text(
                    message!,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Progress Indicators
// مؤشرات التقدم
// ═══════════════════════════════════════════════════════════════════════════

/// Progress indicator with message
/// مؤشر تقدم مع رسالة
class SahoolProgressIndicator extends StatelessWidget {
  final double? progress;
  final String? message;
  final String? messageAr;
  final bool showPercentage;

  const SahoolProgressIndicator({
    super.key,
    this.progress,
    this.message,
    this.messageAr,
    this.showPercentage = true,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (progress != null) ...[
            // Determinate progress
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 80,
                  height: 80,
                  child: CircularProgressIndicator(
                    value: progress,
                    strokeWidth: 6,
                    backgroundColor: Colors.grey[200],
                    valueColor: const AlwaysStoppedAnimation<Color>(
                      SahoolColors.primary,
                    ),
                  ),
                ),
                if (showPercentage)
                  Text(
                    '${(progress! * 100).round()}%',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: SahoolColors.textDark,
                    ),
                  ),
              ],
            ),
          ] else ...[
            // Indeterminate progress
            const SahoolLoadingSpinner(size: 48),
          ],
          if (messageAr != null || message != null) ...[
            const SizedBox(height: 20),
            if (messageAr != null)
              Text(
                messageAr!,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: SahoolColors.textDark,
                ),
                textAlign: TextAlign.center,
              ),
            if (message != null) ...[
              const SizedBox(height: 4),
              Text(
                message!,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ],
        ],
      ),
    );
  }
}

/// Linear progress indicator with label
/// مؤشر تقدم خطي مع تسمية
class SahoolLinearProgress extends StatelessWidget {
  final double? progress;
  final String? label;
  final String? labelAr;
  final Color? color;

  const SahoolLinearProgress({
    super.key,
    this.progress,
    this.label,
    this.labelAr,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (labelAr != null || label != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  labelAr ?? label ?? '',
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: SahoolColors.textDark,
                  ),
                ),
                if (progress != null)
                  Text(
                    '${(progress! * 100).round()}%',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
              ],
            ),
          ),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: progress,
            minHeight: 8,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation<Color>(
              color ?? SahoolColors.primary,
            ),
          ),
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Button Loading States
// حالات تحميل الأزرار
// ═══════════════════════════════════════════════════════════════════════════

/// Button with loading state
/// زر مع حالة تحميل
class SahoolLoadingButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final bool isLoading;
  final Widget child;
  final String? loadingText;
  final String? loadingTextAr;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final double? width;

  const SahoolLoadingButton({
    super.key,
    required this.onPressed,
    required this.isLoading,
    required this.child,
    this.loadingText,
    this.loadingTextAr,
    this.backgroundColor,
    this.foregroundColor,
    this.width,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      child: ElevatedButton(
        onPressed: isLoading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: backgroundColor ?? SahoolColors.primary,
          foregroundColor: foregroundColor ?? Colors.white,
          disabledBackgroundColor:
              (backgroundColor ?? SahoolColors.primary).withOpacity(0.7),
          disabledForegroundColor:
              (foregroundColor ?? Colors.white).withOpacity(0.9),
        ),
        child: isLoading
            ? Row(
                mainAxisSize: MainAxisSize.min,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        (foregroundColor ?? Colors.white).withOpacity(0.9),
                      ),
                    ),
                  ),
                  if (loadingTextAr != null || loadingText != null) ...[
                    const SizedBox(width: 12),
                    Text(loadingTextAr ?? loadingText ?? ''),
                  ],
                ],
              )
            : child,
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Pull to Refresh
// السحب للتحديث
// ═══════════════════════════════════════════════════════════════════════════

/// Custom refresh indicator with SAHOOL styling
/// مؤشر تحديث مخصص بتنسيق سهول
class SahoolRefreshIndicator extends StatelessWidget {
  final Widget child;
  final Future<void> Function() onRefresh;
  final Color? color;

  const SahoolRefreshIndicator({
    super.key,
    required this.child,
    required this.onRefresh,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: onRefresh,
      color: color ?? SahoolColors.primary,
      backgroundColor: Colors.white,
      strokeWidth: 3,
      displacement: 60,
      child: child,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Pulsing Dot Loader
// محمل النقاط النابضة
// ═══════════════════════════════════════════════════════════════════════════

/// Pulsing dot loader for lightweight loading indication
/// محمل النقاط النابضة للإشارة الخفيفة للتحميل
class PulsingDotLoader extends StatefulWidget {
  final Color? color;
  final double dotSize;
  final int dotCount;

  const PulsingDotLoader({
    super.key,
    this.color,
    this.dotSize = 10,
    this.dotCount = 3,
  });

  @override
  State<PulsingDotLoader> createState() => _PulsingDotLoaderState();
}

class _PulsingDotLoaderState extends State<PulsingDotLoader>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(widget.dotCount, (index) {
        return AnimatedBuilder(
          animation: _controller,
          builder: (context, child) {
            final delay = index * 0.2;
            final animation = ((_controller.value + delay) % 1.0);
            final scale = 0.5 + (animation < 0.5 ? animation : 1 - animation);

            return Container(
              margin: EdgeInsets.symmetric(horizontal: widget.dotSize * 0.3),
              child: Transform.scale(
                scale: scale,
                child: Container(
                  width: widget.dotSize,
                  height: widget.dotSize,
                  decoration: BoxDecoration(
                    color: widget.color ?? SahoolColors.primary,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            );
          },
        );
      }),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Shimmer Wrapper (for legacy compatibility)
// غلاف اللمعان (للتوافق مع الإصدارات السابقة)
// ═══════════════════════════════════════════════════════════════════════════

/// Alias for SahoolShimmer (legacy compatibility)
typedef ShimmerLoader = SahoolShimmer;

/// Alias for SahoolShimmerCard (legacy compatibility)
typedef SahoolShimmerCard = SkeletonCard;

/// Alias for SahoolShimmerList (legacy compatibility)
typedef SahoolShimmerList = SkeletonList;

/// Alias for SahoolShimmerGrid (legacy compatibility)
typedef SahoolShimmerGrid = SkeletonGrid;
