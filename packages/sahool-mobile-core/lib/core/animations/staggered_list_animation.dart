/// StaggeredListAnimation - رسوم متحركة متتالية للقوائم
///
/// Wraps list children with fade + slide entrance animations
/// with configurable stagger delay between items.
///
/// Features:
/// - Fade + slide entrance animation for each child
/// - Configurable stagger delay between items
/// - Vertical and horizontal direction support
/// - Respects MediaQuery.disableAnimations for accessibility
/// - Auto-plays on first build
/// - Builder pattern support via [StaggeredListAnimation.builder]
library;

import 'package:flutter/material.dart';

import 'animation_presets.dart';

// =============================================================================
// STAGGERED LIST ANIMATION DIRECTION - اتجاه التحريك المتتابع
// =============================================================================

/// Direction for staggered slide animation - اتجاه الانزلاق المتتابع
enum StaggerDirection {
  /// Slide from bottom to top - انزلاق من الأسفل للأعلى
  vertical,

  /// Slide from right to left (or left to right for RTL) - انزلاق أفقي
  horizontal,
}

// =============================================================================
// ANIMATED LIST ITEM - عنصر قائمة متحرك
// =============================================================================

/// Animates a single list item with fade + slide entrance.
/// عنصر يظهر بتأثير التلاشي والانزلاق مع تأخير حسب الترتيب.
///
/// Usage:
/// ```dart
/// AnimatedListItem(
///   index: 0,
///   child: MyCard(),
/// )
/// ```
class AnimatedListItem extends StatefulWidget {
  /// Index of the item in the list, used to calculate stagger delay.
  /// ترتيب العنصر في القائمة لحساب التأخير.
  final int index;

  /// The child widget to animate.
  /// العنصر الفرعي المراد تحريكه.
  final Widget child;

  /// Delay between each item's animation start.
  /// التأخير بين بدء تحريك كل عنصر.
  final Duration delay;

  /// Duration of the fade + slide animation for each item.
  /// مدة تحريك التلاشي والانزلاق لكل عنصر.
  final Duration duration;

  /// Animation curve.
  /// منحنى التحريك.
  final Curve curve;

  /// Slide direction.
  /// اتجاه الانزلاق.
  final StaggerDirection direction;

  /// Slide offset magnitude (fraction of widget size).
  /// مقدار الانزلاق (نسبة من حجم العنصر).
  final double slideOffset;

  const AnimatedListItem({
    super.key,
    required this.index,
    required this.child,
    this.delay = AnimationDurations.staggerDelay,
    this.duration = AnimationDurations.medium,
    this.curve = AnimationCurves.easeOutCubic,
    this.direction = StaggerDirection.vertical,
    this.slideOffset = 0.3,
  });

  @override
  State<AnimatedListItem> createState() => _AnimatedListItemState();
}

class _AnimatedListItemState extends State<AnimatedListItem>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _slideAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    final curved = CurvedAnimation(
      parent: _controller,
      curve: widget.curve,
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(curved);

    final beginOffset = widget.direction == StaggerDirection.vertical
        ? Offset(0, widget.slideOffset)
        : Offset(widget.slideOffset, 0);

    _slideAnimation = Tween<Offset>(
      begin: beginOffset,
      end: Offset.zero,
    ).animate(curved);

    _scheduleAnimation();
  }

  void _scheduleAnimation() {
    final staggerDelay = widget.delay * widget.index;
    Future.delayed(staggerDelay, () {
      if (mounted) {
        _controller.forward();
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Respect accessibility: skip animations when disabled
    // احترام إمكانية الوصول: تخطي التحريك عند تعطيله
    final disableAnimations = MediaQuery.of(context).disableAnimations;
    if (disableAnimations) {
      return widget.child;
    }

    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: widget.child,
      ),
    );
  }
}

// =============================================================================
// STAGGERED LIST ANIMATION - تحريك القائمة المتتابع
// =============================================================================

/// Wraps a list of children with staggered fade + slide entrance animations.
/// يغلف قائمة من العناصر بتحريكات متتابعة (تلاشي + انزلاق).
///
/// Usage with children:
/// ```dart
/// StaggeredListAnimation(
///   children: [
///     MyCard(data: items[0]),
///     MyCard(data: items[1]),
///     MyCard(data: items[2]),
///   ],
/// )
/// ```
///
/// Usage with builder:
/// ```dart
/// StaggeredListAnimation.builder(
///   itemCount: items.length,
///   itemBuilder: (context, index) => MyCard(data: items[index]),
/// )
/// ```
class StaggeredListAnimation extends StatefulWidget {
  /// List of children to animate. Mutually exclusive with [itemCount] + [itemBuilder].
  /// قائمة العناصر الفرعية. لا يمكن استخدامها مع [itemCount] + [itemBuilder].
  final List<Widget>? children;

  /// Number of items when using builder pattern.
  /// عدد العناصر عند استخدام نمط البناء.
  final int? itemCount;

  /// Builder function for each item.
  /// دالة بناء لكل عنصر.
  final Widget Function(BuildContext context, int index)? itemBuilder;

  /// Stagger delay between items.
  /// التأخير المتتابع بين العناصر.
  final Duration staggerDelay;

  /// Animation duration for each item.
  /// مدة التحريك لكل عنصر.
  final Duration itemDuration;

  /// Animation curve.
  /// منحنى التحريك.
  final Curve curve;

  /// Slide direction.
  /// اتجاه الانزلاق.
  final StaggerDirection direction;

  /// Slide offset magnitude.
  /// مقدار الانزلاق.
  final double slideOffset;

  /// Main axis alignment for the internal Column/Row.
  /// محاذاة المحور الرئيسي.
  final MainAxisAlignment mainAxisAlignment;

  /// Cross axis alignment for the internal Column/Row.
  /// محاذاة المحور العرضي.
  final CrossAxisAlignment crossAxisAlignment;

  /// Main axis size for the internal Column/Row.
  /// حجم المحور الرئيسي.
  final MainAxisSize mainAxisSize;

  /// Creates a StaggeredListAnimation with explicit children.
  const StaggeredListAnimation({
    super.key,
    required List<Widget> this.children,
    this.staggerDelay = AnimationDurations.staggerDelay,
    this.itemDuration = AnimationDurations.medium,
    this.curve = AnimationCurves.easeOutCubic,
    this.direction = StaggerDirection.vertical,
    this.slideOffset = 0.3,
    this.mainAxisAlignment = MainAxisAlignment.start,
    this.crossAxisAlignment = CrossAxisAlignment.stretch,
    this.mainAxisSize = MainAxisSize.min,
  })  : itemCount = null,
        itemBuilder = null;

  /// Creates a StaggeredListAnimation with a builder pattern.
  const StaggeredListAnimation.builder({
    super.key,
    required int this.itemCount,
    required Widget Function(BuildContext, int) this.itemBuilder,
    this.staggerDelay = AnimationDurations.staggerDelay,
    this.itemDuration = AnimationDurations.medium,
    this.curve = AnimationCurves.easeOutCubic,
    this.direction = StaggerDirection.vertical,
    this.slideOffset = 0.3,
    this.mainAxisAlignment = MainAxisAlignment.start,
    this.crossAxisAlignment = CrossAxisAlignment.stretch,
    this.mainAxisSize = MainAxisSize.min,
  }) : children = null;

  @override
  State<StaggeredListAnimation> createState() =>
      _StaggeredListAnimationState();
}

class _StaggeredListAnimationState extends State<StaggeredListAnimation> {
  @override
  Widget build(BuildContext context) {
    final disableAnimations = MediaQuery.of(context).disableAnimations;

    final int count;
    if (widget.children != null) {
      count = widget.children!.length;
    } else {
      count = widget.itemCount ?? 0;
    }

    final animatedChildren = List<Widget>.generate(count, (index) {
      final child = widget.children != null
          ? widget.children![index]
          : widget.itemBuilder!(context, index);

      if (disableAnimations) {
        return child;
      }

      return AnimatedListItem(
        index: index,
        delay: widget.staggerDelay,
        duration: widget.itemDuration,
        curve: widget.curve,
        direction: widget.direction,
        slideOffset: widget.slideOffset,
        child: child,
      );
    });

    if (widget.direction == StaggerDirection.horizontal) {
      return Row(
        mainAxisAlignment: widget.mainAxisAlignment,
        crossAxisAlignment: widget.crossAxisAlignment,
        mainAxisSize: widget.mainAxisSize,
        children: animatedChildren,
      );
    }

    return Column(
      mainAxisAlignment: widget.mainAxisAlignment,
      crossAxisAlignment: widget.crossAxisAlignment,
      mainAxisSize: widget.mainAxisSize,
      children: animatedChildren,
    );
  }
}
