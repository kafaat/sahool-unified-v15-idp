import 'dart:math' as math;
import 'package:flutter/material.dart';

/// SAHOOL Theme Animations System
/// نظام حركات الثيم لسهول
///
/// Features:
/// - Smooth theme transitions | انتقالات ثيم سلسة
/// - Color morphing animations | حركات تحول الألوان
/// - Background gradient animations | حركات التدرجات الخلفية
/// - Glass shimmer effects | تأثيرات اللمعان الزجاجي

// ═══════════════════════════════════════════════════════════════════════════
// Theme Transition Widget
// ═══════════════════════════════════════════════════════════════════════════

/// Animated theme transition wrapper
/// غلاف انتقال الثيم المتحرك
class AnimatedThemeTransition extends StatefulWidget {
  final Widget child;
  final ThemeData theme;
  final Duration duration;
  final Curve curve;

  const AnimatedThemeTransition({
    super.key,
    required this.child,
    required this.theme,
    this.duration = const Duration(milliseconds: 300),
    this.curve = Curves.easeInOut,
  });

  @override
  State<AnimatedThemeTransition> createState() => _AnimatedThemeTransitionState();
}

class _AnimatedThemeTransitionState extends State<AnimatedThemeTransition>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late ThemeData _oldTheme;
  late ThemeData _newTheme;

  @override
  void initState() {
    super.initState();
    _oldTheme = widget.theme;
    _newTheme = widget.theme;
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
  }

  @override
  void didUpdateWidget(AnimatedThemeTransition oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.theme != widget.theme) {
      _oldTheme = oldWidget.theme;
      _newTheme = widget.theme;
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
      animation: CurvedAnimation(
        parent: _controller,
        curve: widget.curve,
      ),
      builder: (context, child) {
        final t = _controller.value;
        return Theme(
          data: _lerpTheme(_oldTheme, _newTheme, t),
          child: widget.child,
        );
      },
    );
  }

  ThemeData _lerpTheme(ThemeData a, ThemeData b, double t) {
    // Lerp individual theme properties for smooth transition
    return ThemeData(
      useMaterial3: b.useMaterial3,
      brightness: t < 0.5 ? a.brightness : b.brightness,
      colorScheme: ColorScheme.lerp(a.colorScheme, b.colorScheme, t),
      scaffoldBackgroundColor: Color.lerp(
        a.scaffoldBackgroundColor,
        b.scaffoldBackgroundColor,
        t,
      ),
      cardColor: Color.lerp(a.cardColor, b.cardColor, t),
      dividerColor: Color.lerp(a.dividerColor, b.dividerColor, t),
      fontFamily: b.textTheme.bodyMedium?.fontFamily,
      // Preserve other theme data from target
      appBarTheme: b.appBarTheme,
      bottomNavigationBarTheme: b.bottomNavigationBarTheme,
      cardTheme: b.cardTheme,
      elevatedButtonTheme: b.elevatedButtonTheme,
      inputDecorationTheme: b.inputDecorationTheme,
      floatingActionButtonTheme: b.floatingActionButtonTheme,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Color Morphing Animation
// ═══════════════════════════════════════════════════════════════════════════

/// Animated color that morphs between values
/// لون متحرك يتحول بين القيم
class AnimatedMorphColor extends StatefulWidget {
  final Color color;
  final Duration duration;
  final Curve curve;
  final Widget Function(BuildContext context, Color color) builder;

  const AnimatedMorphColor({
    super.key,
    required this.color,
    required this.builder,
    this.duration = const Duration(milliseconds: 300),
    this.curve = Curves.easeInOut,
  });

  @override
  State<AnimatedMorphColor> createState() => _AnimatedMorphColorState();
}

class _AnimatedMorphColorState extends State<AnimatedMorphColor>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late ColorTween _colorTween;
  late Animation<Color?> _colorAnimation;
  Color? _previousColor;

  @override
  void initState() {
    super.initState();
    _previousColor = widget.color;
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
    _colorTween = ColorTween(begin: widget.color, end: widget.color);
    _colorAnimation = _colorTween.animate(
      CurvedAnimation(parent: _controller, curve: widget.curve),
    );
  }

  @override
  void didUpdateWidget(AnimatedMorphColor oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.color != widget.color) {
      _previousColor = _colorAnimation.value ?? _previousColor;
      _colorTween = ColorTween(begin: _previousColor, end: widget.color);
      _colorAnimation = _colorTween.animate(
        CurvedAnimation(parent: _controller, curve: widget.curve),
      );
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
      animation: _colorAnimation,
      builder: (context, child) {
        return widget.builder(context, _colorAnimation.value ?? widget.color);
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Background Gradient Animation
// ═══════════════════════════════════════════════════════════════════════════

/// Animated background gradient
/// تدرج خلفية متحرك
class AnimatedGradientBackground extends StatefulWidget {
  final List<Color> colors;
  final Duration duration;
  final Curve curve;
  final AlignmentGeometry begin;
  final AlignmentGeometry end;
  final Widget? child;
  final bool animate;
  final double? borderRadius;

  const AnimatedGradientBackground({
    super.key,
    required this.colors,
    this.duration = const Duration(seconds: 3),
    this.curve = Curves.easeInOut,
    this.begin = Alignment.topLeft,
    this.end = Alignment.bottomRight,
    this.child,
    this.animate = true,
    this.borderRadius,
  });

  @override
  State<AnimatedGradientBackground> createState() =>
      _AnimatedGradientBackgroundState();
}

class _AnimatedGradientBackgroundState extends State<AnimatedGradientBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
    _animation = CurvedAnimation(
      parent: _controller,
      curve: widget.curve,
    );
    if (widget.animate) {
      _controller.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(AnimatedGradientBackground oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.animate && !_controller.isAnimating) {
      _controller.repeat(reverse: true);
    } else if (!widget.animate && _controller.isAnimating) {
      _controller.stop();
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
        final colors = _interpolateColors(widget.colors, _animation.value);
        final decoration = BoxDecoration(
          gradient: LinearGradient(
            colors: colors,
            begin: widget.begin,
            end: widget.end,
          ),
          borderRadius: widget.borderRadius != null
              ? BorderRadius.circular(widget.borderRadius!)
              : null,
        );

        return DecoratedBox(
          decoration: decoration,
          child: widget.child,
        );
      },
    );
  }

  List<Color> _interpolateColors(List<Color> colors, double t) {
    if (colors.length < 2) return colors;

    final result = <Color>[];
    final shift = t * (colors.length - 1);

    for (int i = 0; i < colors.length; i++) {
      final index = (i + shift.floor()) % colors.length;
      final nextIndex = (index + 1) % colors.length;
      final localT = shift - shift.floor();

      result.add(Color.lerp(colors[index], colors[nextIndex], localT)!);
    }

    return result;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Mesh Gradient Animation
// ═══════════════════════════════════════════════════════════════════════════

/// Animated mesh gradient background (premium effect)
/// خلفية تدرج شبكي متحركة (تأثير متميز)
class AnimatedMeshGradient extends StatefulWidget {
  final List<Color> colors;
  final Duration duration;
  final double intensity;
  final Widget? child;
  final bool animate;

  const AnimatedMeshGradient({
    super.key,
    required this.colors,
    this.duration = const Duration(seconds: 5),
    this.intensity = 0.3,
    this.child,
    this.animate = true,
  });

  @override
  State<AnimatedMeshGradient> createState() => _AnimatedMeshGradientState();
}

class _AnimatedMeshGradientState extends State<AnimatedMeshGradient>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
    if (widget.animate) {
      _controller.repeat();
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
        return CustomPaint(
          painter: _MeshGradientPainter(
            colors: widget.colors,
            animationValue: _controller.value,
            intensity: widget.intensity,
          ),
          child: widget.child,
        );
      },
    );
  }
}

class _MeshGradientPainter extends CustomPainter {
  final List<Color> colors;
  final double animationValue;
  final double intensity;

  _MeshGradientPainter({
    required this.colors,
    required this.animationValue,
    required this.intensity,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;

    for (int i = 0; i < colors.length && i < 4; i++) {
      final angle = animationValue * 2 * math.pi + (i * math.pi / 2);
      final center = Offset(
        size.width * (0.5 + 0.3 * math.cos(angle)),
        size.height * (0.5 + 0.3 * math.sin(angle)),
      );

      final gradient = RadialGradient(
        center: Alignment(
          (center.dx / size.width) * 2 - 1,
          (center.dy / size.height) * 2 - 1,
        ),
        radius: 0.8,
        colors: [
          colors[i].withValues(alpha: intensity),
          colors[i].withValues(alpha: 0),
        ],
      );

      final paint = Paint()
        ..shader = gradient.createShader(rect)
        ..blendMode = BlendMode.srcOver;

      canvas.drawRect(rect, paint);
    }
  }

  @override
  bool shouldRepaint(_MeshGradientPainter oldDelegate) {
    return oldDelegate.animationValue != animationValue ||
        oldDelegate.colors != colors ||
        oldDelegate.intensity != intensity;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Shimmer Effect
// ═══════════════════════════════════════════════════════════════════════════

/// Shimmer effect for glass surfaces
/// تأثير اللمعان للأسطح الزجاجية
class GlassShimmer extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final Color? shimmerColor;
  final double intensity;
  final bool enabled;
  final Axis direction;

  const GlassShimmer({
    super.key,
    required this.child,
    this.duration = const Duration(seconds: 2),
    this.shimmerColor,
    this.intensity = 0.3,
    this.enabled = true,
    this.direction = Axis.horizontal,
  });

  @override
  State<GlassShimmer> createState() => _GlassShimmerState();
}

class _GlassShimmerState extends State<GlassShimmer>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
    if (widget.enabled) {
      _controller.repeat();
    }
  }

  @override
  void didUpdateWidget(GlassShimmer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.enabled && !_controller.isAnimating) {
      _controller.repeat();
    } else if (!widget.enabled && _controller.isAnimating) {
      _controller.stop();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.enabled) return widget.child;

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final shimmerColor = widget.shimmerColor ??
        (isDark ? Colors.white : Colors.white);

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return ShaderMask(
          blendMode: BlendMode.srcATop,
          shaderCallback: (bounds) {
            final shimmerGradient = widget.direction == Axis.horizontal
                ? LinearGradient(
                    begin: Alignment.centerLeft,
                    end: Alignment.centerRight,
                    colors: [
                      shimmerColor.withValues(alpha: 0),
                      shimmerColor.withValues(alpha: widget.intensity),
                      shimmerColor.withValues(alpha: 0),
                    ],
                    stops: const [0.0, 0.5, 1.0],
                    transform: _SlidingGradientTransform(
                      slidePercent: _controller.value,
                    ),
                  )
                : LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      shimmerColor.withValues(alpha: 0),
                      shimmerColor.withValues(alpha: widget.intensity),
                      shimmerColor.withValues(alpha: 0),
                    ],
                    stops: const [0.0, 0.5, 1.0],
                    transform: _SlidingGradientTransform(
                      slidePercent: _controller.value,
                    ),
                  );

            return shimmerGradient.createShader(bounds);
          },
          child: widget.child,
        );
      },
    );
  }
}

class _SlidingGradientTransform extends GradientTransform {
  final double slidePercent;

  const _SlidingGradientTransform({required this.slidePercent});

  @override
  Matrix4? transform(Rect bounds, {TextDirection? textDirection}) {
    return Matrix4.translationValues(
      bounds.width * (slidePercent * 2 - 1),
      0,
      0,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Pulsing Glow Effect
// ═══════════════════════════════════════════════════════════════════════════

/// Pulsing glow animation for glass elements
/// توهج نابض للعناصر الزجاجية
class PulsingGlow extends StatefulWidget {
  final Widget child;
  final Color glowColor;
  final Duration duration;
  final double minOpacity;
  final double maxOpacity;
  final double blurRadius;
  final bool enabled;

  const PulsingGlow({
    super.key,
    required this.child,
    required this.glowColor,
    this.duration = const Duration(seconds: 2),
    this.minOpacity = 0.2,
    this.maxOpacity = 0.6,
    this.blurRadius = 20,
    this.enabled = true,
  });

  @override
  State<PulsingGlow> createState() => _PulsingGlowState();
}

class _PulsingGlowState extends State<PulsingGlow>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _opacityAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
    _opacityAnimation = Tween<double>(
      begin: widget.minOpacity,
      end: widget.maxOpacity,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));
    if (widget.enabled) {
      _controller.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.enabled) return widget.child;

    return AnimatedBuilder(
      animation: _opacityAnimation,
      builder: (context, child) {
        return DecoratedBox(
          decoration: BoxDecoration(
            boxShadow: [
              BoxShadow(
                color: widget.glowColor.withValues(alpha: _opacityAnimation.value),
                blurRadius: widget.blurRadius,
                spreadRadius: widget.blurRadius / 4,
              ),
            ],
          ),
          child: widget.child,
        );
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Animated Glass Border
// ═══════════════════════════════════════════════════════════════════════════

/// Animated gradient border for glass elements
/// حدود متدرجة متحركة للعناصر الزجاجية
class AnimatedGlassBorder extends StatefulWidget {
  final Widget child;
  final List<Color> colors;
  final double borderWidth;
  final double borderRadius;
  final Duration duration;
  final bool enabled;

  const AnimatedGlassBorder({
    super.key,
    required this.child,
    required this.colors,
    this.borderWidth = 2,
    this.borderRadius = 16,
    this.duration = const Duration(seconds: 3),
    this.enabled = true,
  });

  @override
  State<AnimatedGlassBorder> createState() => _AnimatedGlassBorderState();
}

class _AnimatedGlassBorderState extends State<AnimatedGlassBorder>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
    if (widget.enabled) {
      _controller.repeat();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.enabled) {
      return DecoratedBox(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(widget.borderRadius),
          border: Border.all(
            color: widget.colors.first,
            width: widget.borderWidth,
          ),
        ),
        child: widget.child,
      );
    }

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final rotation = _controller.value * 2 * math.pi;

        return CustomPaint(
          painter: _AnimatedBorderPainter(
            colors: widget.colors,
            borderWidth: widget.borderWidth,
            borderRadius: widget.borderRadius,
            rotation: rotation,
          ),
          child: Padding(
            padding: EdgeInsets.all(widget.borderWidth),
            child: widget.child,
          ),
        );
      },
    );
  }
}

class _AnimatedBorderPainter extends CustomPainter {
  final List<Color> colors;
  final double borderWidth;
  final double borderRadius;
  final double rotation;

  _AnimatedBorderPainter({
    required this.colors,
    required this.borderWidth,
    required this.borderRadius,
    required this.rotation,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Rect.fromLTWH(
      borderWidth / 2,
      borderWidth / 2,
      size.width - borderWidth,
      size.height - borderWidth,
    );
    final rrect = RRect.fromRectAndRadius(
      rect,
      Radius.circular(borderRadius - borderWidth / 2),
    );

    final gradient = SweepGradient(
      colors: [...colors, colors.first],
      transform: GradientRotation(rotation),
    );

    final paint = Paint()
      ..shader = gradient.createShader(rect)
      ..style = PaintingStyle.stroke
      ..strokeWidth = borderWidth;

    canvas.drawRRect(rrect, paint);
  }

  @override
  bool shouldRepaint(_AnimatedBorderPainter oldDelegate) {
    return oldDelegate.rotation != rotation ||
        oldDelegate.colors != colors ||
        oldDelegate.borderWidth != borderWidth;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Fade Through Transition
// ═══════════════════════════════════════════════════════════════════════════

/// Fade through page transition (Material Motion)
/// انتقال صفحة بالتلاشي (حركة ماتيريال)
class FadeThroughTransition extends StatelessWidget {
  final Animation<double> animation;
  final Animation<double> secondaryAnimation;
  final Widget child;

  const FadeThroughTransition({
    super.key,
    required this.animation,
    required this.secondaryAnimation,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: animation.drive(
        CurveTween(curve: const Interval(0.0, 0.5)),
      ),
      child: ScaleTransition(
        scale: animation.drive(
          Tween<double>(begin: 0.92, end: 1.0).chain(
            CurveTween(curve: Curves.easeOutCubic),
          ),
        ),
        child: child,
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Theme Transition Route
// ═══════════════════════════════════════════════════════════════════════════

/// Page route with glassmorphism transition
/// مسار صفحة مع انتقال زجاجي
class GlassPageRoute<T> extends PageRouteBuilder<T> {
  final Widget page;
  @override
  final Duration transitionDuration;
  @override
  final Duration reverseTransitionDuration;

  GlassPageRoute({
    required this.page,
    this.transitionDuration = const Duration(milliseconds: 400),
    this.reverseTransitionDuration = const Duration(milliseconds: 300),
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => page,
          transitionDuration: transitionDuration,
          reverseTransitionDuration: reverseTransitionDuration,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            final curvedAnimation = CurvedAnimation(
              parent: animation,
              curve: Curves.easeOutCubic,
              reverseCurve: Curves.easeInCubic,
            );

            return FadeTransition(
              opacity: curvedAnimation,
              child: SlideTransition(
                position: Tween<Offset>(
                  begin: const Offset(0, 0.05),
                  end: Offset.zero,
                ).animate(curvedAnimation),
                child: child,
              ),
            );
          },
        );
}

// ═══════════════════════════════════════════════════════════════════════════
// Utility Extensions
// ═══════════════════════════════════════════════════════════════════════════

/// Extension for easy color animation
extension AnimatedColorExtension on Color {
  /// Lerp to another color
  Color lerpTo(Color other, double t) => Color.lerp(this, other, t)!;

  /// Create a pulsing color
  Color pulsing(double t, {double minOpacity = 0.5}) {
    final opacity = minOpacity + (1 - minOpacity) * math.sin(t * math.pi);
    return withValues(alpha: opacity.clamp(0.0, 1.0));
  }
}

/// Extension for gradient animations
extension AnimatedGradientExtension on LinearGradient {
  /// Lerp to another gradient
  LinearGradient lerpTo(LinearGradient other, double t) {
    return LinearGradient(
      begin: Alignment.lerp(begin as Alignment?, other.begin as Alignment?, t)!,
      end: Alignment.lerp(end as Alignment?, other.end as Alignment?, t)!,
      colors: _lerpColors(colors, other.colors, t),
      stops: _lerpStops(stops, other.stops, t),
    );
  }

  List<Color> _lerpColors(List<Color> a, List<Color> b, double t) {
    final maxLength = math.max(a.length, b.length);
    return List.generate(maxLength, (i) {
      final colorA = i < a.length ? a[i] : a.last;
      final colorB = i < b.length ? b[i] : b.last;
      return Color.lerp(colorA, colorB, t)!;
    });
  }

  List<double>? _lerpStops(List<double>? a, List<double>? b, double t) {
    if (a == null && b == null) return null;
    final stopsA = a ?? List.generate(colors.length, (i) => i / (colors.length - 1));
    final stopsB = b ?? List.generate(colors.length, (i) => i / (colors.length - 1));
    final maxLength = math.max(stopsA.length, stopsB.length);
    return List.generate(maxLength, (i) {
      final stopA = i < stopsA.length ? stopsA[i] : stopsA.last;
      final stopB = i < stopsB.length ? stopsB[i] : stopsB.last;
      return stopA + (stopB - stopA) * t;
    });
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Animation Presets
// ═══════════════════════════════════════════════════════════════════════════

/// Preset animation configurations
class ThemeAnimationPresets {
  ThemeAnimationPresets._();

  /// Quick theme switch (for toggle buttons)
  static const Duration quickSwitch = Duration(milliseconds: 200);

  /// Standard theme transition
  static const Duration standard = Duration(milliseconds: 300);

  /// Smooth theme transition
  static const Duration smooth = Duration(milliseconds: 500);

  /// Dramatic theme transition
  static const Duration dramatic = Duration(milliseconds: 800);

  /// Page transition duration
  static const Duration pageTransition = Duration(milliseconds: 400);

  /// Shimmer loop duration
  static const Duration shimmerLoop = Duration(seconds: 2);

  /// Gradient animation duration
  static const Duration gradientLoop = Duration(seconds: 5);

  /// Pulse animation duration
  static const Duration pulseLoop = Duration(seconds: 2);

  /// Curves
  static const Curve standardCurve = Curves.easeInOut;
  static const Curve entranceCurve = Curves.easeOutCubic;
  static const Curve exitCurve = Curves.easeInCubic;
  static const Curve bounceCurve = Curves.elasticOut;
}
