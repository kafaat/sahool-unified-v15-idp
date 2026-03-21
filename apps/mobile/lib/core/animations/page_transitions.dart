import 'package:flutter/material.dart';

/// SAHOOL Page Transitions - انتقالات الصفحات المتقدمة
/// Comprehensive page transition system for smooth navigation
///
/// Features:
/// - Slide transitions (all directions)
/// - Fade transitions with customizable curves
/// - Scale transitions
/// - Shared element transitions
/// - Combination transitions

// =============================================================================
// SLIDE TRANSITIONS - انتقالات الانزلاق
// =============================================================================

/// Slide direction for page transitions
enum SlideDirection {
  left,
  right,
  up,
  down,
}

/// Slide Page Transition - انتقال الانزلاق
/// Slides the new page in from the specified direction
class SlidePageTransition extends PageRouteBuilder {
  final Widget page;
  final SlideDirection direction;
  final Curve curve;
  final Duration duration;

  SlidePageTransition({
    required this.page,
    this.direction = SlideDirection.right,
    this.curve = Curves.easeInOutCubic,
    this.duration = const Duration(milliseconds: 350),
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            final offsetTween = _getOffsetTween(direction);
            final curvedAnimation = CurvedAnimation(
              parent: animation,
              curve: curve,
            );

            return SlideTransition(
              position: offsetTween.animate(curvedAnimation),
              child: child,
            );
          },
        );

  static Tween<Offset> _getOffsetTween(SlideDirection direction) {
    switch (direction) {
      case SlideDirection.left:
        return Tween(begin: const Offset(-1.0, 0.0), end: Offset.zero);
      case SlideDirection.right:
        return Tween(begin: const Offset(1.0, 0.0), end: Offset.zero);
      case SlideDirection.up:
        return Tween(begin: const Offset(0.0, -1.0), end: Offset.zero);
      case SlideDirection.down:
        return Tween(begin: const Offset(0.0, 1.0), end: Offset.zero);
    }
  }
}

/// Slide With Fade Transition - انتقال الانزلاق مع التلاشي
/// Combines slide and fade for a smoother transition
class SlideWithFadePageTransition extends PageRouteBuilder {
  final Widget page;
  final SlideDirection direction;
  final Curve curve;
  final Duration duration;

  SlideWithFadePageTransition({
    required this.page,
    this.direction = SlideDirection.right,
    this.curve = Curves.easeOutQuart,
    this.duration = const Duration(milliseconds: 400),
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            final slideOffset = _getPartialOffset(direction);
            final curvedAnimation = CurvedAnimation(
              parent: animation,
              curve: curve,
            );

            return FadeTransition(
              opacity: Tween<double>(begin: 0.0, end: 1.0).animate(
                CurvedAnimation(
                  parent: animation,
                  curve: const Interval(0.0, 0.6, curve: Curves.easeOut),
                ),
              ),
              child: SlideTransition(
                position: Tween<Offset>(
                  begin: slideOffset,
                  end: Offset.zero,
                ).animate(curvedAnimation),
                child: child,
              ),
            );
          },
        );

  static Offset _getPartialOffset(SlideDirection direction) {
    const distance = 0.3; // 30% of screen
    switch (direction) {
      case SlideDirection.left:
        return const Offset(-distance, 0.0);
      case SlideDirection.right:
        return const Offset(distance, 0.0);
      case SlideDirection.up:
        return const Offset(0.0, -distance);
      case SlideDirection.down:
        return const Offset(0.0, distance);
    }
  }
}

// =============================================================================
// FADE TRANSITIONS - انتقالات التلاشي
// =============================================================================

/// Fade Page Transition - انتقال التلاشي
/// Simple fade in/out transition
class FadePageTransition extends PageRouteBuilder {
  final Widget page;
  final Curve curve;
  final Duration duration;

  FadePageTransition({
    required this.page,
    this.curve = Curves.easeInOut,
    this.duration = const Duration(milliseconds: 300),
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(
              opacity: CurvedAnimation(parent: animation, curve: curve),
              child: child,
            );
          },
        );
}

/// Cross Fade Page Transition - انتقال التلاشي المتقاطع
/// Fades out the old page while fading in the new one
class CrossFadePageTransition extends PageRouteBuilder {
  final Widget page;
  final Curve curve;
  final Duration duration;

  CrossFadePageTransition({
    required this.page,
    this.curve = Curves.easeInOutCubic,
    this.duration = const Duration(milliseconds: 350),
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          opaque: false,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            final fadeInAnimation = CurvedAnimation(
              parent: animation,
              curve: const Interval(0.3, 1.0, curve: Curves.easeOut),
            );
            final fadeOutAnimation = CurvedAnimation(
              parent: secondaryAnimation,
              curve: const Interval(0.0, 0.5, curve: Curves.easeIn),
            );

            return FadeTransition(
              opacity: Tween<double>(begin: 0.0, end: 1.0).animate(fadeInAnimation),
              child: FadeTransition(
                opacity: Tween<double>(begin: 1.0, end: 0.0).animate(fadeOutAnimation),
                child: child,
              ),
            );
          },
        );
}

// =============================================================================
// SCALE TRANSITIONS - انتقالات التكبير
// =============================================================================

/// Scale Page Transition - انتقال التكبير
/// Scales the page in from center
class ScalePageTransition extends PageRouteBuilder {
  final Widget page;
  final Curve curve;
  final Duration duration;
  final double beginScale;
  final Alignment alignment;

  ScalePageTransition({
    required this.page,
    this.curve = Curves.easeOutBack,
    this.duration = const Duration(milliseconds: 400),
    this.beginScale = 0.8,
    this.alignment = Alignment.center,
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            final curvedAnimation = CurvedAnimation(
              parent: animation,
              curve: curve,
            );

            return ScaleTransition(
              scale: Tween<double>(begin: beginScale, end: 1.0).animate(curvedAnimation),
              alignment: alignment,
              child: FadeTransition(
                opacity: Tween<double>(begin: 0.0, end: 1.0).animate(
                  CurvedAnimation(
                    parent: animation,
                    curve: const Interval(0.0, 0.5, curve: Curves.easeOut),
                  ),
                ),
                child: child,
              ),
            );
          },
        );
}

/// Scale And Rotate Transition - انتقال التكبير والدوران
/// Combines scale with subtle rotation
class ScaleRotatePageTransition extends PageRouteBuilder {
  final Widget page;
  final Curve curve;
  final Duration duration;
  final double beginScale;
  final double beginRotation;

  ScaleRotatePageTransition({
    required this.page,
    this.curve = Curves.easeOutCubic,
    this.duration = const Duration(milliseconds: 450),
    this.beginScale = 0.85,
    this.beginRotation = 0.05, // Radians
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            final curvedAnimation = CurvedAnimation(
              parent: animation,
              curve: curve,
            );

            return FadeTransition(
              opacity: Tween<double>(begin: 0.0, end: 1.0).animate(curvedAnimation),
              child: RotationTransition(
                turns: Tween<double>(begin: beginRotation, end: 0.0).animate(curvedAnimation),
                child: ScaleTransition(
                  scale: Tween<double>(begin: beginScale, end: 1.0).animate(curvedAnimation),
                  child: child,
                ),
              ),
            );
          },
        );
}

// =============================================================================
// SHARED ELEMENT TRANSITIONS - انتقالات العناصر المشتركة
// =============================================================================

/// Shared Element Hero Route - مسار عنصر البطل المشترك
/// Provides smooth transition for hero widgets
class SharedElementPageRoute<T> extends MaterialPageRoute<T> {
  final Curve heroAnimationCurve;
  final Duration heroAnimationDuration;

  SharedElementPageRoute({
    required super.builder,
    super.settings,
    this.heroAnimationCurve = Curves.easeInOutCubic,
    this.heroAnimationDuration = const Duration(milliseconds: 500),
  });

  @override
  Duration get transitionDuration => heroAnimationDuration;

  @override
  Widget buildTransitions(
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    return FadeTransition(
      opacity: CurvedAnimation(
        parent: animation,
        curve: const Interval(0.0, 0.5, curve: Curves.easeOut),
      ),
      child: child,
    );
  }
}

/// Shared Axis Transition - انتقال المحور المشترك
/// Material Design shared axis transition
enum SharedAxisTransitionType {
  horizontal, // X axis
  vertical,   // Y axis
  scaled,     // Z axis (scale)
}

class SharedAxisPageTransition extends PageRouteBuilder {
  final Widget page;
  final SharedAxisTransitionType transitionType;
  final Curve curve;
  final Duration duration;

  SharedAxisPageTransition({
    required this.page,
    this.transitionType = SharedAxisTransitionType.horizontal,
    this.curve = Curves.easeInOutCubic,
    this.duration = const Duration(milliseconds: 400),
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            final curvedAnimation = CurvedAnimation(
              parent: animation,
              curve: curve,
            );

            switch (transitionType) {
              case SharedAxisTransitionType.horizontal:
                return _buildHorizontalAxisTransition(curvedAnimation, child);
              case SharedAxisTransitionType.vertical:
                return _buildVerticalAxisTransition(curvedAnimation, child);
              case SharedAxisTransitionType.scaled:
                return _buildScaledAxisTransition(curvedAnimation, child);
            }
          },
        );

  static Widget _buildHorizontalAxisTransition(
    Animation<double> animation,
    Widget child,
  ) {
    return FadeTransition(
      opacity: animation,
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0.3, 0.0),
          end: Offset.zero,
        ).animate(animation),
        child: child,
      ),
    );
  }

  static Widget _buildVerticalAxisTransition(
    Animation<double> animation,
    Widget child,
  ) {
    return FadeTransition(
      opacity: animation,
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0.0, 0.3),
          end: Offset.zero,
        ).animate(animation),
        child: child,
      ),
    );
  }

  static Widget _buildScaledAxisTransition(
    Animation<double> animation,
    Widget child,
  ) {
    return FadeTransition(
      opacity: animation,
      child: ScaleTransition(
        scale: Tween<double>(begin: 0.9, end: 1.0).animate(animation),
        child: child,
      ),
    );
  }
}

// =============================================================================
// CUSTOM CURVE DEFINITIONS - تعريفات المنحنيات المخصصة
// =============================================================================

/// SAHOOL Custom Curves - منحنيات ساهول المخصصة
class SahoolCurves {
  /// Smooth entrance curve - للدخول السلس
  static const Curve smoothEntry = Curves.easeOutCubic;

  /// Smooth exit curve - للخروج السلس
  static const Curve smoothExit = Curves.easeInCubic;

  /// Bounce entry curve - للدخول المرن
  static const Curve bounceEntry = Curves.elasticOut;

  /// Overshoot curve - للتجاوز
  static const Curve overshoot = Curves.easeOutBack;

  /// Anticipation curve - للتوقع (slight pullback before forward motion)
  static const Curve anticipation = _AnticipationCurve();

  /// Spring curve - للنابض
  static const Curve spring = _SpringCurve();

  /// Decelerate fast curve - للتباطؤ السريع
  static const Curve decelerateFast = _DecelerateFastCurve();

  /// Emphasized decelerate - تباطؤ مؤكد
  static const Curve emphasizedDecelerate = Curves.easeOutQuart;

  /// Emphasized accelerate - تسارع مؤكد
  static const Curve emphasizedAccelerate = Curves.easeInQuart;
}

/// Custom Anticipation Curve - منحنى التوقع
/// Pulls back slightly before moving forward
class _AnticipationCurve extends Curve {
  const _AnticipationCurve();

  @override
  double transformInternal(double t) {
    const c1 = 1.70158;
    const c3 = c1 + 1;
    return c3 * t * t * t - c1 * t * t;
  }
}

/// Custom Spring Curve - منحنى النابض
class _SpringCurve extends Curve {
  const _SpringCurve();

  @override
  double transformInternal(double t) {
    const c4 = (2 * 3.14159265359) / 3;
    return t == 0
        ? 0
        : t == 1
            ? 1
            : _pow(2, -10 * t) * _sin((t * 10 - 0.75) * c4) + 1;
  }

  double _pow(double base, double exponent) {
    double result = 1.0;
    for (int i = 0; i < exponent.abs().toInt(); i++) {
      result *= base;
    }
    return exponent < 0 ? 1 / result : result;
  }

  double _sin(double x) {
    // Taylor series approximation for sin
    double result = x;
    double term = x;
    for (int i = 1; i < 10; i++) {
      term *= -x * x / ((2 * i) * (2 * i + 1));
      result += term;
    }
    return result;
  }
}

/// Decelerate Fast Curve - منحنى التباطؤ السريع
class _DecelerateFastCurve extends Curve {
  const _DecelerateFastCurve();

  @override
  double transformInternal(double t) {
    return 1.0 - (1.0 - t) * (1.0 - t) * (1.0 - t);
  }
}

// =============================================================================
// MODAL TRANSITIONS - انتقالات النوافذ المنبثقة
// =============================================================================

/// Modal Bottom Sheet Transition - انتقال النافذة السفلية
class ModalBottomSheetTransition extends PageRouteBuilder {
  final Widget page;
  final Curve curve;
  final Duration duration;
  final Color barrierColor;

  ModalBottomSheetTransition({
    required this.page,
    this.curve = Curves.easeOutCubic,
    this.duration = const Duration(milliseconds: 350),
    this.barrierColor = Colors.black54,
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          opaque: false,
          barrierColor: barrierColor,
          barrierDismissible: true,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            final slideAnimation = CurvedAnimation(
              parent: animation,
              curve: curve,
            );

            return SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(0.0, 1.0),
                end: Offset.zero,
              ).animate(slideAnimation),
              child: child,
            );
          },
        );
}

/// Dialog Pop Transition - انتقال الحوار المنبثق
class DialogPopTransition extends PageRouteBuilder {
  final Widget page;
  final Curve curve;
  final Duration duration;
  final Color barrierColor;

  DialogPopTransition({
    required this.page,
    this.curve = Curves.easeOutBack,
    this.duration = const Duration(milliseconds: 300),
    this.barrierColor = Colors.black54,
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: duration,
          reverseTransitionDuration: Duration(milliseconds: duration.inMilliseconds ~/ 2),
          opaque: false,
          barrierColor: barrierColor,
          barrierDismissible: true,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            final curvedAnimation = CurvedAnimation(
              parent: animation,
              curve: curve,
              reverseCurve: Curves.easeIn,
            );

            return ScaleTransition(
              scale: Tween<double>(begin: 0.8, end: 1.0).animate(curvedAnimation),
              child: FadeTransition(
                opacity: curvedAnimation,
                child: child,
              ),
            );
          },
        );
}

// =============================================================================
// NAVIGATION HELPERS - مساعدات التنقل
// =============================================================================

/// Navigation Extension for easy transitions
/// امتداد التنقل للانتقالات السهلة
extension NavigationExtension on NavigatorState {
  /// Push with slide transition - الانتقال بالانزلاق
  Future<T?> pushSlide<T>(
    Widget page, {
    SlideDirection direction = SlideDirection.right,
    Curve curve = Curves.easeInOutCubic,
    Duration duration = const Duration(milliseconds: 350),
  }) {
    return push<T>(SlidePageTransition(
      page: page,
      direction: direction,
      curve: curve,
      duration: duration,
    ) as Route<T>);
  }

  /// Push with fade transition - الانتقال بالتلاشي
  Future<T?> pushFade<T>(
    Widget page, {
    Curve curve = Curves.easeInOut,
    Duration duration = const Duration(milliseconds: 300),
  }) {
    return push<T>(FadePageTransition(
      page: page,
      curve: curve,
      duration: duration,
    ) as Route<T>);
  }

  /// Push with scale transition - الانتقال بالتكبير
  Future<T?> pushScale<T>(
    Widget page, {
    Curve curve = Curves.easeOutBack,
    Duration duration = const Duration(milliseconds: 400),
    double beginScale = 0.8,
    Alignment alignment = Alignment.center,
  }) {
    return push<T>(ScalePageTransition(
      page: page,
      curve: curve,
      duration: duration,
      beginScale: beginScale,
      alignment: alignment,
    ) as Route<T>);
  }

  /// Push as modal bottom sheet - كنافذة سفلية
  Future<T?> pushModalSheet<T>(
    Widget page, {
    Curve curve = Curves.easeOutCubic,
    Duration duration = const Duration(milliseconds: 350),
  }) {
    return push<T>(ModalBottomSheetTransition(
      page: page,
      curve: curve,
      duration: duration,
    ) as Route<T>);
  }

  /// Push as dialog - كحوار
  Future<T?> pushDialog<T>(
    Widget page, {
    Curve curve = Curves.easeOutBack,
    Duration duration = const Duration(milliseconds: 300),
  }) {
    return push(DialogPopTransition(
      page: page,
      curve: curve,
      duration: duration,
    ));
  }
}

// =============================================================================
// ROUTE BUILDERS FOR GO_ROUTER - بناة المسارات لـ GoRouter
// =============================================================================

/// Custom transition page for GoRouter
/// صفحة انتقال مخصصة لـ GoRouter
class SahoolTransitionPage<T> extends CustomTransitionPage<T> {
  SahoolTransitionPage({
    required super.child,
    super.key,
    super.name,
    super.arguments,
    super.restorationId,
    TransitionType type = TransitionType.slide,
    SlideDirection slideDirection = SlideDirection.right,
    Duration duration = const Duration(milliseconds: 350),
    Curve curve = Curves.easeInOutCubic,
  }) : super(
          transitionDuration: duration,
          reverseTransitionDuration: duration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return _buildTransition(
              type: type,
              animation: animation,
              child: child,
              slideDirection: slideDirection,
              curve: curve,
            );
          },
        );

  static Widget _buildTransition({
    required TransitionType type,
    required Animation<double> animation,
    required Widget child,
    required SlideDirection slideDirection,
    required Curve curve,
  }) {
    final curvedAnimation = CurvedAnimation(parent: animation, curve: curve);

    switch (type) {
      case TransitionType.slide:
        return SlideTransition(
          position: _getSlideOffset(slideDirection).animate(curvedAnimation),
          child: child,
        );
      case TransitionType.fade:
        return FadeTransition(
          opacity: curvedAnimation,
          child: child,
        );
      case TransitionType.scale:
        return ScaleTransition(
          scale: Tween<double>(begin: 0.8, end: 1.0).animate(curvedAnimation),
          child: FadeTransition(
            opacity: curvedAnimation,
            child: child,
          ),
        );
      case TransitionType.slideWithFade:
        return FadeTransition(
          opacity: curvedAnimation,
          child: SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(0.3, 0.0),
              end: Offset.zero,
            ).animate(curvedAnimation),
            child: child,
          ),
        );
    }
  }

  static Tween<Offset> _getSlideOffset(SlideDirection direction) {
    switch (direction) {
      case SlideDirection.left:
        return Tween(begin: const Offset(-1.0, 0.0), end: Offset.zero);
      case SlideDirection.right:
        return Tween(begin: const Offset(1.0, 0.0), end: Offset.zero);
      case SlideDirection.up:
        return Tween(begin: const Offset(0.0, -1.0), end: Offset.zero);
      case SlideDirection.down:
        return Tween(begin: const Offset(0.0, 1.0), end: Offset.zero);
    }
  }
}

/// Transition types for SahoolTransitionPage
enum TransitionType {
  slide,
  fade,
  scale,
  slideWithFade,
}
