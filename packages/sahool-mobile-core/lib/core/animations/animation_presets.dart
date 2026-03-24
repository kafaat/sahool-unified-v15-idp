import 'package:flutter/material.dart';

/// SAHOOL Animation Presets & Utilities - ثوابت ومساعدات التحريك
/// Centralized animation constants and helper utilities
///
/// Features:
/// - AnimationDurations constants
/// - AnimationCurves constants
/// - AnimatedListHelper
/// - StaggeredAnimation helper
/// - Animation extension methods

// =============================================================================
// ANIMATION DURATIONS - مدد التحريك
// =============================================================================

/// Standard animation durations for SAHOOL - مدد التحريك القياسية لساهول
class AnimationDurations {
  AnimationDurations._();

  /// Instant - فوري (0ms)
  static const Duration instant = Duration.zero;

  /// Ultra fast - سريع جداً (50ms)
  /// Use for very subtle changes like opacity shifts
  static const Duration ultraFast = Duration(milliseconds: 50);

  /// Very fast - سريع جداً (100ms)
  /// Use for micro-interactions like button taps
  static const Duration veryFast = Duration(milliseconds: 100);

  /// Fast - سريع (150ms)
  /// Use for quick feedback animations
  static const Duration fast = Duration(milliseconds: 150);

  /// Normal - عادي (200ms)
  /// Default duration for most UI animations
  static const Duration normal = Duration(milliseconds: 200);

  /// Medium - متوسط (300ms)
  /// Use for page transitions, reveals
  static const Duration medium = Duration(milliseconds: 300);

  /// Slow - بطيء (400ms)
  /// Use for complex transitions
  static const Duration slow = Duration(milliseconds: 400);

  /// Very slow - بطيء جداً (500ms)
  /// Use for elaborate animations
  static const Duration verySlow = Duration(milliseconds: 500);

  /// Ultra slow - بطيء للغاية (700ms)
  /// Use for dramatic effect
  static const Duration ultraSlow = Duration(milliseconds: 700);

  /// Page transition - انتقال الصفحة
  static const Duration pageTransition = Duration(milliseconds: 350);

  /// Modal transition - انتقال النافذة المنبثقة
  static const Duration modalTransition = Duration(milliseconds: 300);

  /// Drawer transition - انتقال الدرج
  static const Duration drawerTransition = Duration(milliseconds: 250);

  /// Snackbar - شريط الإشعار
  static const Duration snackbar = Duration(milliseconds: 250);

  /// FAB transformation - تحويل الزر العائم
  static const Duration fabTransformation = Duration(milliseconds: 200);

  /// List item stagger delay - تأخير عناصر القائمة
  static const Duration staggerDelay = Duration(milliseconds: 50);

  /// Chart animation - تحريك الرسم البياني
  static const Duration chartAnimation = Duration(milliseconds: 800);

  /// Loading spinner - مؤشر التحميل
  static const Duration loadingSpinner = Duration(milliseconds: 1500);

  /// Pulse animation - تحريك النبض
  static const Duration pulse = Duration(milliseconds: 1000);

  /// Ripple effect - تأثير التموج
  static const Duration ripple = Duration(milliseconds: 400);

  /// Hero animation - تحريك البطل
  static const Duration hero = Duration(milliseconds: 500);

  /// Shake animation - تحريك الاهتزاز
  static const Duration shake = Duration(milliseconds: 500);

  /// Bounce animation - تحريك الارتداد
  static const Duration bounce = Duration(milliseconds: 600);
}

// =============================================================================
// ANIMATION CURVES - منحنيات التحريك
// =============================================================================

/// Standard animation curves for SAHOOL - منحنيات التحريك القياسية لساهول
class AnimationCurves {
  AnimationCurves._();

  // ─────────────────────────────────────────────────────────────────────────
  // Standard Curves - منحنيات قياسية
  // ─────────────────────────────────────────────────────────────────────────

  /// Default curve - المنحنى الافتراضي
  static const Curve defaultCurve = Curves.easeInOut;

  /// Linear - خطي
  static const Curve linear = Curves.linear;

  /// Ease in - تسريع في البداية
  static const Curve easeIn = Curves.easeIn;

  /// Ease out - تباطؤ في النهاية
  static const Curve easeOut = Curves.easeOut;

  /// Ease in out - تسريع وتباطؤ
  static const Curve easeInOut = Curves.easeInOut;

  // ─────────────────────────────────────────────────────────────────────────
  // Cubic Curves - منحنيات تكعيبية
  // ─────────────────────────────────────────────────────────────────────────

  /// Fast out slow in - خروج سريع دخول بطيء (Material Design standard)
  static const Curve fastOutSlowIn = Curves.fastOutSlowIn;

  /// Ease in cubic - تسريع تكعيبي
  static const Curve easeInCubic = Curves.easeInCubic;

  /// Ease out cubic - تباطؤ تكعيبي
  static const Curve easeOutCubic = Curves.easeOutCubic;

  /// Ease in out cubic - تسريع وتباطؤ تكعيبي
  static const Curve easeInOutCubic = Curves.easeInOutCubic;

  // ─────────────────────────────────────────────────────────────────────────
  // Quart Curves - منحنيات رباعية
  // ─────────────────────────────────────────────────────────────────────────

  /// Ease in quart - تسريع رباعي
  static const Curve easeInQuart = Curves.easeInQuart;

  /// Ease out quart - تباطؤ رباعي
  static const Curve easeOutQuart = Curves.easeOutQuart;

  /// Ease in out quart - تسريع وتباطؤ رباعي
  static const Curve easeInOutQuart = Curves.easeInOutQuart;

  // ─────────────────────────────────────────────────────────────────────────
  // Special Curves - منحنيات خاصة
  // ─────────────────────────────────────────────────────────────────────────

  /// Bounce - ارتداد
  static const Curve bounce = Curves.bounceOut;

  /// Bounce in - ارتداد داخلي
  static const Curve bounceIn = Curves.bounceIn;

  /// Elastic - مرن
  static const Curve elastic = Curves.elasticOut;

  /// Elastic in - مرن داخلي
  static const Curve elasticIn = Curves.elasticIn;

  /// Overshoot (back) - تجاوز
  static const Curve overshoot = Curves.easeOutBack;

  /// Anticipate (back in) - توقع
  static const Curve anticipate = Curves.easeInBack;

  /// Decelerate - تباطؤ
  static const Curve decelerate = Curves.decelerate;

  /// Accelerate - تسارع
  static const Curve accelerate = Curves.fastLinearToSlowEaseIn;

  // ─────────────────────────────────────────────────────────────────────────
  // Context-Specific Curves - منحنيات سياقية
  // ─────────────────────────────────────────────────────────────────────────

  /// Page enter - دخول الصفحة
  static const Curve pageEnter = Curves.easeOutCubic;

  /// Page exit - خروج الصفحة
  static const Curve pageExit = Curves.easeInCubic;

  /// Modal enter - دخول النافذة المنبثقة
  static const Curve modalEnter = Curves.easeOutBack;

  /// Modal exit - خروج النافذة المنبثقة
  static const Curve modalExit = Curves.easeIn;

  /// Button press - ضغط الزر
  static const Curve buttonPress = Curves.easeIn;

  /// Button release - إفلات الزر
  static const Curve buttonRelease = Curves.easeOut;

  /// Card lift - رفع البطاقة
  static const Curve cardLift = Curves.easeOutCubic;

  /// Card drop - إسقاط البطاقة
  static const Curve cardDrop = Curves.easeInCubic;

  /// Chart draw - رسم المخطط
  static const Curve chartDraw = Curves.easeOutCubic;

  /// Loading pulse - نبض التحميل
  static const Curve loadingPulse = Curves.easeInOut;

  /// Attention bounce - ارتداد لفت الانتباه
  static const Curve attention = Curves.elasticOut;
}

// =============================================================================
// ANIMATED LIST HELPER - مساعد القائمة المتحركة
// =============================================================================

/// Helper class for managing animated lists - فئة مساعدة لإدارة القوائم المتحركة
class AnimatedListHelper<T> {
  final GlobalKey<AnimatedListState> listKey;
  final List<T> items;
  final Widget Function(T item, Animation<double> animation) buildItem;
  final Duration insertDuration;
  final Duration removeDuration;
  final Curve insertCurve;
  final Curve removeCurve;

  AnimatedListHelper({
    required this.listKey,
    required this.items,
    required this.buildItem,
    this.insertDuration = AnimationDurations.normal,
    this.removeDuration = AnimationDurations.normal,
    this.insertCurve = AnimationCurves.easeOutCubic,
    this.removeCurve = AnimationCurves.easeInCubic,
  });

  AnimatedListState? get _listState => listKey.currentState;

  /// Insert item at index
  void insert(int index, T item) {
    items.insert(index, item);
    _listState?.insertItem(
      index,
      duration: insertDuration,
    );
  }

  /// Insert item at the end
  void add(T item) {
    insert(items.length, item);
  }

  /// Remove item at index
  T removeAt(int index) {
    final item = items.removeAt(index);
    _listState?.removeItem(
      index,
      (context, animation) => _buildRemoveAnimation(item, animation),
      duration: removeDuration,
    );
    return item;
  }

  /// Remove specific item
  bool remove(T item) {
    final index = items.indexOf(item);
    if (index >= 0) {
      removeAt(index);
      return true;
    }
    return false;
  }

  /// Remove all items
  void clear() {
    while (items.isNotEmpty) {
      removeAt(0);
    }
  }

  /// Replace all items with new list
  void replaceAll(List<T> newItems) {
    clear();
    for (var i = 0; i < newItems.length; i++) {
      Future.delayed(
        Duration(milliseconds: i * AnimationDurations.staggerDelay.inMilliseconds),
        () => insert(i, newItems[i]),
      );
    }
  }

  Widget _buildRemoveAnimation(T item, Animation<double> animation) {
    final curvedAnimation = CurvedAnimation(
      parent: animation,
      curve: removeCurve,
    );

    return SizeTransition(
      sizeFactor: curvedAnimation,
      child: FadeTransition(
        opacity: curvedAnimation,
        child: buildItem(item, animation),
      ),
    );
  }

  /// Build method for AnimatedList itemBuilder
  Widget itemBuilder(BuildContext context, int index, Animation<double> animation) {
    final curvedAnimation = CurvedAnimation(
      parent: animation,
      curve: insertCurve,
    );

    return SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0, 0.5),
        end: Offset.zero,
      ).animate(curvedAnimation),
      child: FadeTransition(
        opacity: curvedAnimation,
        child: buildItem(items[index], animation),
      ),
    );
  }
}

// =============================================================================
// STAGGERED ANIMATION HELPER - مساعد التحريك المتتابع
// =============================================================================

/// Helper class for creating staggered animations - فئة مساعدة للتحريكات المتتابعة
class StaggeredAnimationHelper {
  final int itemCount;
  final Duration totalDuration;
  final Duration itemDuration;
  final Curve curve;

  StaggeredAnimationHelper({
    required this.itemCount,
    required this.totalDuration,
    Duration? itemDuration,
    this.curve = AnimationCurves.easeOutCubic,
  }) : itemDuration = itemDuration ?? _calculateItemDuration(itemCount, totalDuration);

  static Duration _calculateItemDuration(int count, Duration total) {
    // Each item's animation overlaps with the next by 50%
    final totalMs = total.inMilliseconds;
    final itemMs = (totalMs / (count * 0.5 + 0.5)).round();
    return Duration(milliseconds: itemMs);
  }

  /// Get the interval for an item at the given index
  Interval getInterval(int index) {
    final startTime = index / (itemCount * 2);
    final endTime = (index + 1) / (itemCount * 2) + 0.5;

    return Interval(
      startTime.clamp(0.0, 1.0),
      endTime.clamp(0.0, 1.0),
      curve: curve,
    );
  }

  /// Get animation for an item
  Animation<double> getAnimation(int index, Animation<double> parent) {
    return CurvedAnimation(
      parent: parent,
      curve: getInterval(index),
    );
  }

  /// Get slide animation for an item
  Animation<Offset> getSlideAnimation(
    int index,
    Animation<double> parent, {
    Offset begin = const Offset(0, 0.3),
    Offset end = Offset.zero,
  }) {
    return Tween<Offset>(begin: begin, end: end).animate(
      getAnimation(index, parent),
    );
  }

  /// Get fade animation for an item
  Animation<double> getFadeAnimation(int index, Animation<double> parent) {
    return Tween<double>(begin: 0.0, end: 1.0).animate(
      getAnimation(index, parent),
    );
  }

  /// Get scale animation for an item
  Animation<double> getScaleAnimation(
    int index,
    Animation<double> parent, {
    double begin = 0.8,
    double end = 1.0,
  }) {
    return Tween<double>(begin: begin, end: end).animate(
      getAnimation(index, parent),
    );
  }
}

// =============================================================================
// ANIMATION EXTENSIONS - امتدادات التحريك
// =============================================================================

/// Extension methods for Animation - طرق امتداد للتحريك
extension AnimationExtensions<T> on Animation<T> {
  /// Drive with a tween and custom curve
  Animation<U> driven<U>(Tween<U> tween, {Curve curve = Curves.linear}) {
    return tween.animate(CurvedAnimation(parent: this as Animation<double>, curve: curve));
  }
}

/// Extension methods for AnimationController - طرق امتداد لمتحكم التحريك
extension AnimationControllerExtensions on AnimationController {
  /// Play forward then reverse (ping pong)
  Future<void> pingPong({int times = 1}) async {
    for (var i = 0; i < times; i++) {
      await forward();
      await reverse();
    }
  }

  /// Repeat with delay between repetitions
  void repeatWithDelay(Duration delay) {
    addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        Future.delayed(delay, () {
          if (isCompleted) {
            reset();
            forward();
          }
        });
      }
    });
    forward();
  }

  /// Play once and dispose
  Future<void> playOnce() async {
    await forward();
    dispose();
  }
}

// =============================================================================
// WIDGET ANIMATIONS - تحريكات العناصر
// =============================================================================

/// Fade In Widget - عنصر يظهر بالتلاشي
class FadeIn extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final Duration delay;
  final Curve curve;

  const FadeIn({
    super.key,
    required this.child,
    this.duration = AnimationDurations.normal,
    this.delay = Duration.zero,
    this.curve = AnimationCurves.easeOut,
  });

  @override
  State<FadeIn> createState() => _FadeInState();
}

class _FadeInState extends State<FadeIn> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _animation = CurvedAnimation(parent: _controller, curve: widget.curve);

    Future.delayed(widget.delay, () {
      if (mounted) _controller.forward();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _animation,
      child: widget.child,
    );
  }
}

/// Slide In Widget - عنصر يدخل بالانزلاق
class SlideIn extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final Duration delay;
  final Curve curve;
  final Offset from;

  const SlideIn({
    super.key,
    required this.child,
    this.duration = AnimationDurations.medium,
    this.delay = Duration.zero,
    this.curve = AnimationCurves.easeOutCubic,
    this.from = const Offset(0, 0.3),
  });

  @override
  State<SlideIn> createState() => _SlideInState();
}

class _SlideInState extends State<SlideIn> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _slideAnimation = Tween<Offset>(
      begin: widget.from,
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));
    _fadeAnimation = CurvedAnimation(parent: _controller, curve: widget.curve);

    Future.delayed(widget.delay, () {
      if (mounted) _controller.forward();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SlideTransition(
      position: _slideAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: widget.child,
      ),
    );
  }
}

/// Scale In Widget - عنصر يظهر بالتكبير
class ScaleIn extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final Duration delay;
  final Curve curve;
  final double from;

  const ScaleIn({
    super.key,
    required this.child,
    this.duration = AnimationDurations.medium,
    this.delay = Duration.zero,
    this.curve = AnimationCurves.overshoot,
    this.from = 0.8,
  });

  @override
  State<ScaleIn> createState() => _ScaleInState();
}

class _ScaleInState extends State<ScaleIn> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: widget.from,
      end: 1.0,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));
    _fadeAnimation = CurvedAnimation(parent: _controller, curve: Curves.easeOut);

    Future.delayed(widget.delay, () {
      if (mounted) _controller.forward();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _scaleAnimation,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: widget.child,
      ),
    );
  }
}

/// Shake Widget - عنصر يهتز
class Shake extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final double offset;
  final bool autoPlay;

  const Shake({
    super.key,
    required this.child,
    this.duration = AnimationDurations.shake,
    this.offset = 10,
    this.autoPlay = true,
  });

  @override
  State<Shake> createState() => ShakeState();
}

class ShakeState extends State<Shake> with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    if (widget.autoPlay) {
      _controller.forward();
    }
  }

  void shake() {
    _controller.forward(from: 0);
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
        final sineValue =
            (_controller.value * 3.14159 * 4).isNaN ? 0.0 :
            _sin(_controller.value * 3.14159 * 4) * (1 - _controller.value);
        return Transform.translate(
          offset: Offset(sineValue * widget.offset, 0),
          child: widget.child,
        );
      },
    );
  }

  double _sin(double x) {
    // Simple sine approximation
    double result = x;
    double term = x;
    for (int i = 1; i < 10; i++) {
      term *= -x * x / ((2 * i) * (2 * i + 1));
      result += term;
    }
    return result;
  }
}

// =============================================================================
// ANIMATION BUILDER WIDGETS - عناصر بناء التحريك
// =============================================================================

/// Implicit Animation Builder - باني التحريك الضمني
/// Provides a simple way to animate any value
class ImplicitAnimator extends StatefulWidget {
  final double value;
  final Duration duration;
  final Curve curve;
  final Widget Function(BuildContext context, double value) builder;

  const ImplicitAnimator({
    super.key,
    required this.value,
    this.duration = AnimationDurations.normal,
    this.curve = AnimationCurves.easeInOut,
    required this.builder,
  });

  @override
  State<ImplicitAnimator> createState() => _ImplicitAnimatorState();
}

class _ImplicitAnimatorState extends State<ImplicitAnimator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  double _oldValue = 0;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _animation = Tween<double>(
      begin: widget.value,
      end: widget.value,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));
    _oldValue = widget.value;
  }

  @override
  void didUpdateWidget(ImplicitAnimator oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.value != widget.value) {
      _oldValue = _animation.value;
      _animation = Tween<double>(
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

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) => widget.builder(context, _animation.value),
    );
  }
}

// =============================================================================
// ANIMATION SEQUENCES - تسلسلات التحريك
// =============================================================================

/// Animation Sequence Item - عنصر تسلسل التحريك
class AnimationSequenceItem {
  final Duration duration;
  final Duration delay;
  final Curve curve;
  final Widget Function(Animation<double> animation) builder;

  const AnimationSequenceItem({
    required this.duration,
    this.delay = Duration.zero,
    this.curve = Curves.easeInOut,
    required this.builder,
  });
}

/// Sequential Animation Runner - مشغل التحريك التتابعي
class SequentialAnimationRunner extends StatefulWidget {
  final List<AnimationSequenceItem> sequence;
  final bool repeat;
  final VoidCallback? onComplete;

  const SequentialAnimationRunner({
    super.key,
    required this.sequence,
    this.repeat = false,
    this.onComplete,
  });

  @override
  State<SequentialAnimationRunner> createState() =>
      _SequentialAnimationRunnerState();
}

class _SequentialAnimationRunnerState extends State<SequentialAnimationRunner>
    with TickerProviderStateMixin {
  late List<AnimationController> _controllers;
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    _initControllers();
    _startSequence();
  }

  void _initControllers() {
    _controllers = widget.sequence.map((item) {
      return AnimationController(
        duration: item.duration,
        vsync: this,
      );
    }).toList();
  }

  Future<void> _startSequence() async {
    for (int i = 0; i < widget.sequence.length; i++) {
      _currentIndex = i;
      await Future.delayed(widget.sequence[i].delay);
      if (mounted) {
        await _controllers[i].forward();
      }
    }

    widget.onComplete?.call();

    if (widget.repeat && mounted) {
      for (final controller in _controllers) {
        controller.reset();
      }
      _startSequence();
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
    return Stack(
      children: widget.sequence.asMap().entries.map((entry) {
        final index = entry.key;
        final item = entry.value;
        final animation = CurvedAnimation(
          parent: _controllers[index],
          curve: item.curve,
        );

        return item.builder(animation);
      }).toList(),
    );
  }
}

// =============================================================================
// ANIMATION UTILITIES - أدوات التحريك
// =============================================================================

/// Utility class for animation calculations - فئة أدوات لحسابات التحريك
class AnimationUtils {
  AnimationUtils._();

  /// Calculate total duration for staggered animations
  static Duration calculateStaggeredDuration({
    required int itemCount,
    required Duration itemDuration,
    required Duration staggerDelay,
  }) {
    if (itemCount == 0) return Duration.zero;
    return itemDuration + (staggerDelay * (itemCount - 1));
  }

  /// Get delay for item in staggered animation
  static Duration getStaggeredDelay({
    required int index,
    required Duration staggerDelay,
  }) {
    return staggerDelay * index;
  }

  /// Lerp between two durations
  static Duration lerpDuration(Duration a, Duration b, double t) {
    return Duration(
      milliseconds: (a.inMilliseconds + (b.inMilliseconds - a.inMilliseconds) * t).round(),
    );
  }

  /// Check if device can handle complex animations
  static bool canAnimateSmoothly(BuildContext context) {
    final devicePixelRatio = MediaQuery.of(context).devicePixelRatio;
    // Lower pixel ratio typically means lower-end device
    return devicePixelRatio >= 2.0;
  }

  /// Get recommended animation duration based on device capabilities
  static Duration getRecommendedDuration(BuildContext context, Duration preferred) {
    if (canAnimateSmoothly(context)) {
      return preferred;
    }
    // Reduce animation duration on lower-end devices
    return Duration(milliseconds: (preferred.inMilliseconds * 0.7).round());
  }
}
