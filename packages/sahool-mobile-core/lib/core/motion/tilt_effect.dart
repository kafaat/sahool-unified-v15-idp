// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Tilt Effect Widgets
// ودجات تأثير الميلان - للتأثيرات ثلاثية الأبعاد
// ═══════════════════════════════════════════════════════════════════════════

import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'parallax_layer.dart';

// ─────────────────────────────────────────────────────────────────────────────
// TILT CONFIGURATION
// ─────────────────────────────────────────────────────────────────────────────

/// Configuration for tilt effects
/// إعدادات تأثيرات الميلان
class TiltConfig {
  /// Maximum tilt angle in degrees on X axis (pitch)
  final double maxTiltX;

  /// Maximum tilt angle in degrees on Y axis (roll)
  final double maxTiltY;

  /// Whether to enable 3D perspective
  final bool enablePerspective;

  /// Perspective depth (higher = less dramatic)
  final double perspectiveDepth;

  /// Whether to add glare effect
  final bool enableGlare;

  /// Glare opacity (0.0 to 1.0)
  final double glareOpacity;

  /// Whether to enable dynamic shadow
  final bool enableShadow;

  /// Shadow intensity
  final double shadowIntensity;

  /// Maximum shadow offset
  final double maxShadowOffset;

  /// Animation duration
  final Duration animationDuration;

  /// Animation curve
  final Curve animationCurve;

  /// Whether effect is enabled
  final bool enabled;

  const TiltConfig({
    this.maxTiltX = 15.0,
    this.maxTiltY = 15.0,
    this.enablePerspective = true,
    this.perspectiveDepth = 1000.0,
    this.enableGlare = true,
    this.glareOpacity = 0.25,
    this.enableShadow = true,
    this.shadowIntensity = 0.3,
    this.maxShadowOffset = 15.0,
    this.animationDuration = const Duration(milliseconds: 150),
    this.animationCurve = Curves.easeOutCubic,
    this.enabled = true,
  });

  /// Default configuration
  static const TiltConfig defaultConfig = TiltConfig();

  /// Subtle configuration
  static const TiltConfig subtle = TiltConfig(
    maxTiltX: 8.0,
    maxTiltY: 8.0,
    glareOpacity: 0.15,
    shadowIntensity: 0.2,
    maxShadowOffset: 8.0,
  );

  /// Dramatic configuration
  static const TiltConfig dramatic = TiltConfig(
    maxTiltX: 25.0,
    maxTiltY: 25.0,
    perspectiveDepth: 800.0,
    glareOpacity: 0.35,
    shadowIntensity: 0.4,
    maxShadowOffset: 25.0,
  );

  /// Card-optimized configuration
  static const TiltConfig card = TiltConfig(
    maxTiltX: 12.0,
    maxTiltY: 12.0,
    enableGlare: true,
    glareOpacity: 0.2,
    enableShadow: true,
    shadowIntensity: 0.25,
    maxShadowOffset: 12.0,
  );

  /// Reduced motion configuration (accessibility)
  static const TiltConfig reducedMotion = TiltConfig(
    maxTiltX: 5.0,
    maxTiltY: 5.0,
    enableGlare: false,
    enableShadow: false,
    animationDuration: Duration(milliseconds: 300),
  );

  TiltConfig copyWith({
    double? maxTiltX,
    double? maxTiltY,
    bool? enablePerspective,
    double? perspectiveDepth,
    bool? enableGlare,
    double? glareOpacity,
    bool? enableShadow,
    double? shadowIntensity,
    double? maxShadowOffset,
    Duration? animationDuration,
    Curve? animationCurve,
    bool? enabled,
  }) {
    return TiltConfig(
      maxTiltX: maxTiltX ?? this.maxTiltX,
      maxTiltY: maxTiltY ?? this.maxTiltY,
      enablePerspective: enablePerspective ?? this.enablePerspective,
      perspectiveDepth: perspectiveDepth ?? this.perspectiveDepth,
      enableGlare: enableGlare ?? this.enableGlare,
      glareOpacity: glareOpacity ?? this.glareOpacity,
      enableShadow: enableShadow ?? this.enableShadow,
      shadowIntensity: shadowIntensity ?? this.shadowIntensity,
      maxShadowOffset: maxShadowOffset ?? this.maxShadowOffset,
      animationDuration: animationDuration ?? this.animationDuration,
      animationCurve: animationCurve ?? this.animationCurve,
      enabled: enabled ?? this.enabled,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TILT DATA
// ─────────────────────────────────────────────────────────────────────────────

/// Current tilt state
class TiltData {
  /// X rotation angle in radians
  final double rotationX;

  /// Y rotation angle in radians
  final double rotationY;

  /// Normalized X position (-1.0 to 1.0)
  final double normalizedX;

  /// Normalized Y position (-1.0 to 1.0)
  final double normalizedY;

  /// Tilt magnitude (0.0 to ~1.41)
  final double magnitude;

  /// Tilt angle in radians
  final double angle;

  const TiltData({
    this.rotationX = 0.0,
    this.rotationY = 0.0,
    this.normalizedX = 0.0,
    this.normalizedY = 0.0,
    this.magnitude = 0.0,
    this.angle = 0.0,
  });

  static const TiltData zero = TiltData();

  /// Create from normalized values
  factory TiltData.fromNormalized({
    required double x,
    required double y,
    required TiltConfig config,
  }) {
    final rotationX = -y * config.maxTiltX * (math.pi / 180);
    final rotationY = x * config.maxTiltY * (math.pi / 180);
    final magnitude = math.sqrt(x * x + y * y);
    final angle = math.atan2(y, x);

    return TiltData(
      rotationX: rotationX,
      rotationY: rotationY,
      normalizedX: x,
      normalizedY: y,
      magnitude: magnitude,
      angle: angle,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TILT CONTAINER
// ─────────────────────────────────────────────────────────────────────────────

/// Container that applies 3D tilt effect based on device motion
/// حاوية تطبق تأثير الميلان ثلاثي الأبعاد بناءً على حركة الجهاز
class TiltContainer extends StatefulWidget {
  /// Child widget
  final Widget child;

  /// Tilt configuration
  final TiltConfig config;

  /// Border radius for clipping
  final BorderRadius? borderRadius;

  /// Whether to clip the child
  final bool clipChild;

  /// Builder for custom tilt handling
  final Widget Function(BuildContext context, TiltData tiltData, Widget child)?
      builder;

  const TiltContainer({
    super.key,
    required this.child,
    this.config = TiltConfig.defaultConfig,
    this.borderRadius,
    this.clipChild = true,
    this.builder,
  });

  @override
  State<TiltContainer> createState() => _TiltContainerState();
}

class _TiltContainerState extends State<TiltContainer>
    with SingleTickerProviderStateMixin {
  TiltData _currentTilt = TiltData.zero;

  @override
  Widget build(BuildContext context) {
    final controller = ParallaxContainer.of(context);

    if (controller == null || !widget.config.enabled) {
      return widget.child;
    }

    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        final offset = controller.currentOffset;

        // Calculate tilt data
        _currentTilt = TiltData.fromNormalized(
          x: offset.normalizedX,
          y: offset.normalizedY,
          config: widget.config,
        );

        // Use custom builder if provided
        if (widget.builder != null) {
          return widget.builder!(context, _currentTilt, widget.child);
        }

        return _buildTiltEffect();
      },
    );
  }

  Widget _buildTiltEffect() {
    Widget child = widget.child;

    // Apply clipping
    if (widget.clipChild && widget.borderRadius != null) {
      child = ClipRRect(
        borderRadius: widget.borderRadius!,
        child: child,
      );
    }

    return TweenAnimationBuilder<TiltData>(
      tween: _TiltDataTween(begin: TiltData.zero, end: _currentTilt),
      duration: widget.config.animationDuration,
      curve: widget.config.animationCurve,
      builder: (context, tilt, child) {
        // Build transform matrix
        final transform = Matrix4.identity();

        if (widget.config.enablePerspective) {
          transform.setEntry(3, 2, 1 / widget.config.perspectiveDepth);
        }

        transform.rotateX(tilt.rotationX);
        transform.rotateY(tilt.rotationY);

        return Transform(
          transform: transform,
          alignment: Alignment.center,
          child: child,
        );
      },
      child: child,
    );
  }
}

/// Tween for TiltData interpolation
class _TiltDataTween extends Tween<TiltData> {
  _TiltDataTween({super.begin, super.end});

  @override
  TiltData lerp(double t) {
    return TiltData(
      rotationX: _lerpDouble(begin!.rotationX, end!.rotationX, t),
      rotationY: _lerpDouble(begin!.rotationY, end!.rotationY, t),
      normalizedX: _lerpDouble(begin!.normalizedX, end!.normalizedX, t),
      normalizedY: _lerpDouble(begin!.normalizedY, end!.normalizedY, t),
      magnitude: _lerpDouble(begin!.magnitude, end!.magnitude, t),
      angle: _lerpDouble(begin!.angle, end!.angle, t),
    );
  }

  double _lerpDouble(double a, double b, double t) => a + (b - a) * t;
}

// ─────────────────────────────────────────────────────────────────────────────
// TILT CARD
// ─────────────────────────────────────────────────────────────────────────────

/// Card with 3D tilt effect and dynamic shadow
/// بطاقة مع تأثير ميلان ثلاثي الأبعاد وظل ديناميكي
class TiltCard extends StatelessWidget {
  /// Card content
  final Widget child;

  /// Tilt configuration
  final TiltConfig config;

  /// Card width
  final double? width;

  /// Card height
  final double? height;

  /// Card color
  final Color? color;

  /// Card gradient
  final Gradient? gradient;

  /// Border radius
  final BorderRadius borderRadius;

  /// Border
  final Border? border;

  /// Padding
  final EdgeInsets? padding;

  /// Margin
  final EdgeInsets? margin;

  /// On tap callback
  final VoidCallback? onTap;

  /// On long press callback
  final VoidCallback? onLongPress;

  const TiltCard({
    super.key,
    required this.child,
    this.config = TiltConfig.card,
    this.width,
    this.height,
    this.color,
    this.gradient,
    this.borderRadius = const BorderRadius.all(Radius.circular(16)),
    this.border,
    this.padding,
    this.margin,
    this.onTap,
    this.onLongPress,
  });

  @override
  Widget build(BuildContext context) {
    final controller = ParallaxContainer.of(context);
    final theme = Theme.of(context);

    if (controller == null || !config.enabled) {
      return _buildStaticCard(theme, null);
    }

    return AnimatedBuilder(
      animation: controller,
      builder: (context, _) {
        final offset = controller.currentOffset;
        final tilt = TiltData.fromNormalized(
          x: offset.normalizedX,
          y: offset.normalizedY,
          config: config,
        );

        return _buildAnimatedCard(theme, tilt);
      },
    );
  }

  Widget _buildStaticCard(ThemeData theme, TiltData? tilt) {
    return _buildCardContent(theme, tilt ?? TiltData.zero, [
      BoxShadow(
        color: Colors.black.withValues(alpha: 0.1),
        blurRadius: 12,
        offset: const Offset(0, 6),
      ),
    ]);
  }

  Widget _buildAnimatedCard(ThemeData theme, TiltData tilt) {
    return TweenAnimationBuilder<TiltData>(
      tween: _TiltDataTween(begin: TiltData.zero, end: tilt),
      duration: config.animationDuration,
      curve: config.animationCurve,
      builder: (context, animatedTilt, _) {
        // Calculate dynamic shadow
        final shadows = _calculateShadows(animatedTilt);

        // Build transform
        final transform = Matrix4.identity();
        if (config.enablePerspective) {
          transform.setEntry(3, 2, 1 / config.perspectiveDepth);
        }
        transform.rotateX(animatedTilt.rotationX);
        transform.rotateY(animatedTilt.rotationY);

        return Transform(
          transform: transform,
          alignment: Alignment.center,
          child: _buildCardContent(theme, animatedTilt, shadows),
        );
      },
    );
  }

  List<BoxShadow> _calculateShadows(TiltData tilt) {
    if (!config.enableShadow) {
      return [
        BoxShadow(
          color: Colors.black.withValues(alpha: 0.1),
          blurRadius: 12,
          offset: const Offset(0, 6),
        ),
      ];
    }

    // Calculate shadow offset based on tilt
    final shadowX = -tilt.normalizedX * config.maxShadowOffset;
    final shadowY = -tilt.normalizedY * config.maxShadowOffset;

    // Increase shadow blur with tilt magnitude
    final blurRadius = 12.0 + (tilt.magnitude * 8.0);

    return [
      // Main shadow
      BoxShadow(
        color: Colors.black.withValues(alpha: config.shadowIntensity * 0.8),
        blurRadius: blurRadius,
        offset: Offset(shadowX, shadowY + 6),
        spreadRadius: -2,
      ),
      // Soft ambient shadow
      BoxShadow(
        color: Colors.black.withValues(alpha: config.shadowIntensity * 0.3),
        blurRadius: blurRadius * 2,
        offset: Offset(shadowX / 2, shadowY / 2 + 4),
        spreadRadius: -4,
      ),
    ];
  }

  Widget _buildCardContent(
      ThemeData theme, TiltData tilt, List<BoxShadow> shadows) {
    Widget content = child;

    // Add glare effect
    if (config.enableGlare) {
      content = Stack(
        children: [
          content,
          Positioned.fill(
            child: _buildGlareOverlay(tilt),
          ),
        ],
      );
    }

    Widget card = Container(
      width: width,
      height: height,
      margin: margin,
      padding: padding,
      decoration: BoxDecoration(
        color: gradient == null ? (color ?? theme.cardColor) : null,
        gradient: gradient,
        borderRadius: borderRadius,
        border: border,
        boxShadow: shadows,
      ),
      child: ClipRRect(
        borderRadius: borderRadius,
        child: content,
      ),
    );

    // Add tap handling
    if (onTap != null || onLongPress != null) {
      card = GestureDetector(
        onTap: onTap,
        onLongPress: onLongPress,
        child: card,
      );
    }

    return card;
  }

  Widget _buildGlareOverlay(TiltData tilt) {
    // Calculate glare position based on tilt
    // Glare appears opposite to tilt direction
    final glareX = 0.5 - (tilt.normalizedX * 0.5);
    final glareY = 0.5 - (tilt.normalizedY * 0.5);

    // Opacity increases with tilt magnitude
    final opacity = (tilt.magnitude * config.glareOpacity).clamp(0.0, 0.5);

    return IgnorePointer(
      child: ClipRRect(
        borderRadius: borderRadius,
        child: Container(
          decoration: BoxDecoration(
            gradient: RadialGradient(
              center: Alignment(
                (glareX * 2 - 1).clamp(-1.0, 1.0),
                (glareY * 2 - 1).clamp(-1.0, 1.0),
              ),
              radius: 1.2,
              colors: [
                Colors.white.withValues(alpha: opacity),
                Colors.white.withValues(alpha: 0),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TILT INTERACTIVE CARD
// ─────────────────────────────────────────────────────────────────────────────

/// Card that responds to both touch and device motion
/// بطاقة تستجيب للمس وحركة الجهاز معاً
class TiltInteractiveCard extends StatefulWidget {
  /// Card content
  final Widget child;

  /// Tilt configuration
  final TiltConfig config;

  /// Card width
  final double? width;

  /// Card height
  final double? height;

  /// Card color
  final Color? color;

  /// Border radius
  final BorderRadius borderRadius;

  /// Padding
  final EdgeInsets? padding;

  /// On tap callback
  final VoidCallback? onTap;

  /// Whether to respond to touch
  final bool respondToTouch;

  /// Touch sensitivity multiplier
  final double touchSensitivity;

  const TiltInteractiveCard({
    super.key,
    required this.child,
    this.config = TiltConfig.card,
    this.width,
    this.height,
    this.color,
    this.borderRadius = const BorderRadius.all(Radius.circular(16)),
    this.padding,
    this.onTap,
    this.respondToTouch = true,
    this.touchSensitivity = 1.0,
  });

  @override
  State<TiltInteractiveCard> createState() => _TiltInteractiveCardState();
}

class _TiltInteractiveCardState extends State<TiltInteractiveCard> {
  Offset _touchOffset = Offset.zero;
  bool _isTouching = false;

  @override
  Widget build(BuildContext context) {
    final controller = ParallaxContainer.of(context);
    final theme = Theme.of(context);

    final Widget card = TiltCard(
      config: widget.config,
      width: widget.width,
      height: widget.height,
      color: widget.color,
      borderRadius: widget.borderRadius,
      padding: widget.padding,
      child: widget.child,
    );

    if (!widget.respondToTouch) {
      return card;
    }

    return GestureDetector(
      onTapDown: (details) {
        setState(() {
          _isTouching = true;
          _updateTouchOffset(details.localPosition);
        });
      },
      onTapUp: (_) {
        setState(() => _isTouching = false);
        widget.onTap?.call();
      },
      onTapCancel: () {
        setState(() => _isTouching = false);
      },
      onPanUpdate: (details) {
        if (_isTouching) {
          _updateTouchOffset(details.localPosition);
        }
      },
      onPanEnd: (_) {
        setState(() => _isTouching = false);
      },
      child: LayoutBuilder(
        builder: (context, constraints) {
          if (!_isTouching || !widget.config.enabled) {
            return card;
          }

          // Calculate tilt from touch position
          final centerX = (widget.width ?? constraints.maxWidth) / 2;
          final centerY = (widget.height ?? constraints.maxHeight) / 2;

          final normalizedX =
              ((_touchOffset.dx - centerX) / centerX).clamp(-1.0, 1.0) *
                  widget.touchSensitivity;
          final normalizedY =
              ((_touchOffset.dy - centerY) / centerY).clamp(-1.0, 1.0) *
                  widget.touchSensitivity;

          final tilt = TiltData.fromNormalized(
            x: normalizedX,
            y: normalizedY,
            config: widget.config,
          );

          // Build transform
          final transform = Matrix4.identity();
          if (widget.config.enablePerspective) {
            transform.setEntry(3, 2, 1 / widget.config.perspectiveDepth);
          }
          transform.rotateX(tilt.rotationX);
          transform.rotateY(tilt.rotationY);

          return Transform(
            transform: transform,
            alignment: Alignment.center,
            child: TiltCard(
              config: widget.config.copyWith(enabled: false),
              width: widget.width,
              height: widget.height,
              color: widget.color,
              borderRadius: widget.borderRadius,
              padding: widget.padding,
              child: widget.child,
            ),
          );
        },
      ),
    );
  }

  void _updateTouchOffset(Offset localPosition) {
    setState(() {
      _touchOffset = localPosition;
    });
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TILT WIDGET
// ─────────────────────────────────────────────────────────────────────────────

/// Generic widget wrapper with tilt effect
/// غلاف ودجة عام مع تأثير الميلان
class TiltWidget extends StatelessWidget {
  /// Child widget
  final Widget child;

  /// Tilt configuration
  final TiltConfig config;

  /// Whether to add shadow
  final bool addShadow;

  /// Shadow color
  final Color shadowColor;

  const TiltWidget({
    super.key,
    required this.child,
    this.config = TiltConfig.subtle,
    this.addShadow = false,
    this.shadowColor = Colors.black26,
  });

  @override
  Widget build(BuildContext context) {
    return TiltContainer(
      config: config,
      builder: (context, tilt, child) {
        // Build transform
        final transform = Matrix4.identity();
        if (config.enablePerspective) {
          transform.setEntry(3, 2, 1 / config.perspectiveDepth);
        }
        transform.rotateX(tilt.rotationX);
        transform.rotateY(tilt.rotationY);

        Widget result = Transform(
          transform: transform,
          alignment: Alignment.center,
          child: child,
        );

        // Add shadow if enabled
        if (addShadow && config.enableShadow) {
          final shadowX = -tilt.normalizedX * config.maxShadowOffset;
          final shadowY = -tilt.normalizedY * config.maxShadowOffset;

          result = DecoratedBox(
            decoration: BoxDecoration(
              boxShadow: [
                BoxShadow(
                  color: shadowColor,
                  blurRadius: 12 + (tilt.magnitude * 8),
                  offset: Offset(shadowX, shadowY + 6),
                ),
              ],
            ),
            child: result,
          );
        }

        return result;
      },
      child: child,
    );
  }
}
