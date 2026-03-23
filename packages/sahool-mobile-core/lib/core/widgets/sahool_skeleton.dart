import 'package:flutter/material.dart';
import '../theme/sahool_theme.dart';

/// SAHOOL Skeleton Widget System
/// نظام مكونات الهيكل العظمي للتحميل
///
/// Provides a comprehensive set of skeleton/shimmer widgets for
/// loading states across the SAHOOL platform.
/// يوفر مجموعة شاملة من مكونات الهيكل العظمي لحالات التحميل
///
/// Widgets:
/// - [SahoolSkeleton] - Base shimmer rectangle / مستطيل أساسي
/// - [SahoolSkeletonCard] - Card-shaped skeleton / بطاقة هيكلية
/// - [SahoolSkeletonList] - List with stagger animation / قائمة بتأثير متتابع
/// - [SahoolSkeletonText] - Text line skeleton / سطر نص هيكلي
/// - [SahoolSkeletonCircle] - Circular avatar skeleton / دائرة هيكلية
/// - [SahoolSkeletonGrid] - Grid of skeleton cards / شبكة بطاقات هيكلية

// =============================================================================
// SahoolSkeleton - Base Shimmer Widget
// المكون الأساسي - مستطيل لامع قابل للتخصيص
// =============================================================================

/// Base skeleton widget with configurable dimensions and shimmer effect.
/// المكون الأساسي للهيكل العظمي مع تأثير اللمعان القابل للتخصيص.
///
/// Adapts to dark mode automatically using [SahoolColors].
/// يتكيف مع الوضع الداكن تلقائياً.
class SahoolSkeleton extends StatefulWidget {
  /// Width of the skeleton. Uses full available width if null.
  /// عرض الهيكل. يستخدم العرض الكامل إذا كان فارغاً.
  final double? width;

  /// Height of the skeleton.
  /// ارتفاع الهيكل.
  final double height;

  /// Border radius of the skeleton corners.
  /// نصف قطر زوايا الهيكل.
  final double borderRadius;

  /// Optional margin around the skeleton.
  /// هامش اختياري حول الهيكل.
  final EdgeInsets? margin;

  /// Whether the shimmer animation is active.
  /// هل تأثير اللمعان نشط.
  final bool enabled;

  /// Custom base color override. Defaults to theme-aware grey.
  /// لون أساسي مخصص. الافتراضي هو رمادي متوافق مع السمة.
  final Color? baseColor;

  /// Custom highlight color override. Defaults to theme-aware light grey.
  /// لون إبراز مخصص. الافتراضي هو رمادي فاتح متوافق مع السمة.
  final Color? highlightColor;

  const SahoolSkeleton({
    super.key,
    this.width,
    required this.height,
    this.borderRadius = 8,
    this.margin,
    this.enabled = true,
    this.baseColor,
    this.highlightColor,
  });

  @override
  State<SahoolSkeleton> createState() => _SahoolSkeletonState();
}

class _SahoolSkeletonState extends State<SahoolSkeleton>
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
    final isDark = Theme.of(context).brightness == Brightness.dark;

    // ألوان متوافقة مع الوضع الداكن والفاتح
    final baseColor = widget.baseColor ??
        (isDark ? Colors.grey[800]! : Colors.grey[300]!);
    final highlightColor = widget.highlightColor ??
        (isDark ? Colors.grey[700]! : Colors.grey[100]!);

    final child = Container(
      width: widget.width,
      height: widget.height,
      margin: widget.margin,
      decoration: BoxDecoration(
        color: baseColor,
        borderRadius: BorderRadius.circular(widget.borderRadius),
      ),
    );

    if (!widget.enabled) return child;

    return AnimatedBuilder(
      animation: _animation,
      builder: (context, _) {
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [baseColor, highlightColor, baseColor],
              stops: [
                (_animation.value - 0.3).clamp(0.0, 1.0),
                _animation.value.clamp(0.0, 1.0),
                (_animation.value + 0.3).clamp(0.0, 1.0),
              ],
            ).createShader(bounds);
          },
          blendMode: BlendMode.srcATop,
          child: child,
        );
      },
    );
  }
}

// =============================================================================
// SahoolSkeletonCard - Card-shaped Skeleton
// بطاقة هيكلية مع منطقة صورة اختيارية
// =============================================================================

/// Card-shaped skeleton with optional image area at the top.
/// بطاقة هيكلية مع منطقة صورة اختيارية في الأعلى.
class SahoolSkeletonCard extends StatelessWidget {
  /// Total height of the card.
  /// الارتفاع الكلي للبطاقة.
  final double height;

  /// Card width. Uses full available width if null.
  /// عرض البطاقة.
  final double? width;

  /// Corner radius for the card.
  /// نصف قطر زوايا البطاقة.
  final double borderRadius;

  /// Whether to show an image placeholder area at the top.
  /// إظهار منطقة صورة نائبة في الأعلى.
  final bool showImage;

  /// Fraction of card height for the image area (0.0 to 1.0).
  /// نسبة ارتفاع البطاقة لمنطقة الصورة.
  final double imageHeightFraction;

  /// Optional margin around the card.
  /// هامش اختياري حول البطاقة.
  final EdgeInsets? margin;

  const SahoolSkeletonCard({
    super.key,
    this.height = 140,
    this.width,
    this.borderRadius = 16,
    this.showImage = false,
    this.imageHeightFraction = 0.5,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardColor = isDark ? SahoolColors.surfaceDark : Colors.white;
    final borderColor = isDark ? Colors.grey[700]! : Colors.grey[200]!;

    return Container(
      height: height,
      width: width,
      margin: margin ?? const EdgeInsets.symmetric(vertical: 6),
      decoration: BoxDecoration(
        color: cardColor,
        borderRadius: BorderRadius.circular(borderRadius),
        border: Border.all(color: borderColor),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // منطقة الصورة النائبة (اختياري)
            if (showImage)
              SahoolSkeleton(
                height: height * imageHeightFraction,
                borderRadius: 0,
              ),
            // منطقة المحتوى
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    SahoolSkeleton(
                      width: width != null ? width! * 0.7 : 140,
                      height: 14,
                      borderRadius: 4,
                    ),
                    const SizedBox(height: 8),
                    SahoolSkeleton(
                      width: width != null ? width! * 0.5 : 100,
                      height: 10,
                      borderRadius: 4,
                    ),
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

// =============================================================================
// SahoolSkeletonList - List with Stagger Animation
// قائمة هيكلية مع تأثير ظهور متتابع
// =============================================================================

/// A list of skeleton items with staggered fade-in animation.
/// قائمة من العناصر الهيكلية مع تأثير ظهور متتابع.
class SahoolSkeletonList extends StatefulWidget {
  /// Number of skeleton items to display.
  /// عدد العناصر الهيكلية.
  final int itemCount;

  /// Spacing between items.
  /// المسافة بين العناصر.
  final double spacing;

  /// Padding around the list.
  /// الحشوة حول القائمة.
  final EdgeInsets? padding;

  /// Custom builder for each skeleton item. Defaults to [SahoolSkeletonCard].
  /// بانٍ مخصص لكل عنصر. الافتراضي هو [SahoolSkeletonCard].
  final Widget Function(int index)? itemBuilder;

  /// Whether to shrink-wrap the list (no scroll).
  /// تقليص حجم القائمة (بدون تمرير).
  final bool shrinkWrap;

  /// Duration for the stagger delay between items.
  /// مدة التأخير المتتابع بين العناصر.
  final Duration staggerDelay;

  const SahoolSkeletonList({
    super.key,
    this.itemCount = 5,
    this.spacing = 12,
    this.padding,
    this.itemBuilder,
    this.shrinkWrap = true,
    this.staggerDelay = const Duration(milliseconds: 80),
  });

  @override
  State<SahoolSkeletonList> createState() => _SahoolSkeletonListState();
}

class _SahoolSkeletonListState extends State<SahoolSkeletonList>
    with SingleTickerProviderStateMixin {
  late AnimationController _staggerController;

  @override
  void initState() {
    super.initState();
    _staggerController = AnimationController(
      vsync: this,
      duration: Duration(
        milliseconds:
            300 + (widget.itemCount * widget.staggerDelay.inMilliseconds),
      ),
    )..forward();
  }

  @override
  void dispose() {
    _staggerController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      physics: widget.shrinkWrap
          ? const NeverScrollableScrollPhysics()
          : null,
      shrinkWrap: widget.shrinkWrap,
      padding: widget.padding ?? const EdgeInsets.all(16),
      itemCount: widget.itemCount,
      separatorBuilder: (_, __) => SizedBox(height: widget.spacing),
      itemBuilder: (context, index) {
        // حساب تأخير الظهور لكل عنصر
        final startFraction =
            (index * widget.staggerDelay.inMilliseconds) /
                _staggerController.duration!.inMilliseconds;
        final endFraction =
            (startFraction + 0.3).clamp(0.0, 1.0);

        final itemAnimation = Tween<double>(begin: 0, end: 1).animate(
          CurvedAnimation(
            parent: _staggerController,
            curve: Interval(
              startFraction.clamp(0.0, 1.0),
              endFraction,
              curve: Curves.easeOut,
            ),
          ),
        );

        return AnimatedBuilder(
          animation: itemAnimation,
          builder: (context, child) {
            return Opacity(
              opacity: itemAnimation.value,
              child: Transform.translate(
                offset: Offset(0, 20 * (1 - itemAnimation.value)),
                child: child,
              ),
            );
          },
          child: widget.itemBuilder?.call(index) ??
              const SahoolSkeletonCard(height: 100),
        );
      },
    );
  }
}

// =============================================================================
// SahoolSkeletonText - Text Line Skeleton
// سطر نص هيكلي بأحجام مختلفة
// =============================================================================

/// Text skeleton variants.
/// أنواع أحجام النص الهيكلي.
enum SahoolSkeletonTextSize {
  /// Short text line (~40% width, 10px height). / سطر قصير
  short,

  /// Medium text line (~65% width, 12px height). / سطر متوسط
  medium,

  /// Long text line (~90% width, 14px height). / سطر طويل
  long,

  /// Title text line (~50% width, 18px height). / عنوان
  title,
}

/// A single text line skeleton.
/// سطر نص هيكلي بحجم قابل للتخصيص.
class SahoolSkeletonText extends StatelessWidget {
  /// Size variant of the text skeleton.
  /// حجم سطر النص الهيكلي.
  final SahoolSkeletonTextSize size;

  /// Optional explicit width override.
  /// عرض مخصص اختياري.
  final double? width;

  /// Optional margin.
  /// هامش اختياري.
  final EdgeInsets? margin;

  const SahoolSkeletonText({
    super.key,
    this.size = SahoolSkeletonTextSize.medium,
    this.width,
    this.margin,
  });

  @override
  Widget build(BuildContext context) {
    final double effectiveWidth;
    final double effectiveHeight;

    switch (size) {
      case SahoolSkeletonTextSize.short:
        effectiveWidth = width ?? 80;
        effectiveHeight = 10;
      case SahoolSkeletonTextSize.medium:
        effectiveWidth = width ?? 160;
        effectiveHeight = 12;
      case SahoolSkeletonTextSize.long:
        effectiveWidth = width ?? 240;
        effectiveHeight = 14;
      case SahoolSkeletonTextSize.title:
        effectiveWidth = width ?? 120;
        effectiveHeight = 18;
    }

    return SahoolSkeleton(
      width: effectiveWidth,
      height: effectiveHeight,
      borderRadius: 4,
      margin: margin,
    );
  }
}

// =============================================================================
// SahoolSkeletonCircle - Circular Avatar Skeleton
// دائرة هيكلية للصورة الرمزية
// =============================================================================

/// Circular skeleton for avatar placeholders.
/// هيكل دائري للصور الرمزية النائبة.
class SahoolSkeletonCircle extends StatelessWidget {
  /// Diameter of the circle.
  /// قطر الدائرة.
  final double diameter;

  const SahoolSkeletonCircle({
    super.key,
    this.diameter = 48,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolSkeleton(
      width: diameter,
      height: diameter,
      borderRadius: diameter / 2,
    );
  }
}

// =============================================================================
// SahoolSkeletonGrid - Grid of Skeleton Cards
// شبكة من البطاقات الهيكلية
// =============================================================================

/// A grid of skeleton cards with configurable columns and aspect ratio.
/// شبكة من البطاقات الهيكلية بأعمدة ونسبة أبعاد قابلة للتخصيص.
class SahoolSkeletonGrid extends StatelessWidget {
  /// Number of items in the grid.
  /// عدد العناصر في الشبكة.
  final int itemCount;

  /// Number of columns.
  /// عدد الأعمدة.
  final int crossAxisCount;

  /// Aspect ratio of each grid cell.
  /// نسبة أبعاد كل خلية.
  final double childAspectRatio;

  /// Spacing between columns.
  /// المسافة بين الأعمدة.
  final double crossAxisSpacing;

  /// Spacing between rows.
  /// المسافة بين الصفوف.
  final double mainAxisSpacing;

  /// Padding around the grid.
  /// الحشوة حول الشبكة.
  final EdgeInsets? padding;

  /// Whether grid items show an image placeholder.
  /// إظهار منطقة صورة نائبة في عناصر الشبكة.
  final bool showImage;

  /// Custom builder for each grid item.
  /// بانٍ مخصص لكل عنصر في الشبكة.
  final Widget Function(int index)? itemBuilder;

  const SahoolSkeletonGrid({
    super.key,
    this.itemCount = 6,
    this.crossAxisCount = 2,
    this.childAspectRatio = 1.0,
    this.crossAxisSpacing = 12,
    this.mainAxisSpacing = 12,
    this.padding,
    this.showImage = false,
    this.itemBuilder,
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
        crossAxisSpacing: crossAxisSpacing,
        mainAxisSpacing: mainAxisSpacing,
      ),
      itemCount: itemCount,
      itemBuilder: (_, index) =>
          itemBuilder?.call(index) ??
          SahoolSkeletonCard(showImage: showImage),
    );
  }
}
