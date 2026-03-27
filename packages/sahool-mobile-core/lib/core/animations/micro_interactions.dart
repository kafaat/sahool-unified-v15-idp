import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// SAHOOL Micro Interactions - التفاعلات الدقيقة
/// Delightful micro-animations for enhanced user experience
///
/// Features:
/// - Button press animations
/// - Card hover/press effects
/// - Icon animations (success, loading, error)
/// - Ripple effects
/// - Pulse animations

// =============================================================================
// BUTTON PRESS ANIMATIONS - تحريك ضغط الزر
// =============================================================================

/// Animated Press Button - زر بتأثير الضغط
/// Scales down on press with optional haptic feedback
class AnimatedPressButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final VoidCallback? onLongPress;
  final double pressScale;
  final Duration animationDuration;
  final Curve curve;
  final bool enableHapticFeedback;

  const AnimatedPressButton({
    super.key,
    required this.child,
    this.onPressed,
    this.onLongPress,
    this.pressScale = 0.95,
    this.animationDuration = const Duration(milliseconds: 100),
    this.curve = Curves.easeInOut,
    this.enableHapticFeedback = true,
  });

  @override
  State<AnimatedPressButton> createState() => _AnimatedPressButtonState();
}

class _AnimatedPressButtonState extends State<AnimatedPressButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: widget.pressScale,
    ).animate(CurvedAnimation(parent: _controller, curve: widget.curve));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onTapDown(TapDownDetails details) {
    _controller.forward();
    if (widget.enableHapticFeedback) {
      HapticFeedback.lightImpact();
    }
  }

  void _onTapUp(TapUpDetails details) {
    _controller.reverse();
  }

  void _onTapCancel() {
    _controller.reverse();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: widget.onPressed != null ? _onTapDown : null,
      onTapUp: widget.onPressed != null ? _onTapUp : null,
      onTapCancel: widget.onPressed != null ? _onTapCancel : null,
      onTap: widget.onPressed,
      onLongPress: widget.onLongPress,
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: widget.child,
          );
        },
      ),
    );
  }
}

/// Bounce Button - زر مرن
/// Bounces when pressed
class BounceButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final Duration duration;
  final double bounceFactor;

  const BounceButton({
    super.key,
    required this.child,
    this.onPressed,
    this.duration = const Duration(milliseconds: 200),
    this.bounceFactor = 0.9,
  });

  @override
  State<BounceButton> createState() => _BounceButtonState();
}

class _BounceButtonState extends State<BounceButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _bounceAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    _bounceAnimation = TweenSequence<double>([
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.0, end: widget.bounceFactor),
        weight: 40,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: widget.bounceFactor, end: 1.05),
        weight: 30,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.05, end: 1.0),
        weight: 30,
      ),
    ]).animate(CurvedAnimation(parent: _controller, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTap() {
    _controller.forward(from: 0.0);
    HapticFeedback.selectionClick();
    widget.onPressed?.call();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onPressed != null ? _handleTap : null,
      child: AnimatedBuilder(
        animation: _bounceAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _bounceAnimation.value,
            child: widget.child,
          );
        },
      ),
    );
  }
}

// =============================================================================
// CARD HOVER/PRESS EFFECTS - تأثيرات البطاقات
// =============================================================================

/// Animated Card - بطاقة متحركة
/// Card with lift and shadow animation on press
class AnimatedCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final double elevation;
  final double pressedElevation;
  final double hoverScale;
  final BorderRadius borderRadius;
  final Color? color;
  final Duration animationDuration;

  const AnimatedCard({
    super.key,
    required this.child,
    this.onTap,
    this.onLongPress,
    this.elevation = 4,
    this.pressedElevation = 8,
    this.hoverScale = 1.02,
    this.borderRadius = const BorderRadius.all(Radius.circular(16)),
    this.color,
    this.animationDuration = const Duration(milliseconds: 150),
  });

  @override
  State<AnimatedCard> createState() => _AnimatedCardState();
}

class _AnimatedCardState extends State<AnimatedCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _elevationAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: widget.hoverScale,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOut));
    _elevationAnimation = Tween<double>(
      begin: widget.elevation,
      end: widget.pressedElevation,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOut));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => _controller.forward(),
      onTapUp: (_) => _controller.reverse(),
      onTapCancel: () => _controller.reverse(),
      onTap: widget.onTap,
      onLongPress: widget.onLongPress,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: Material(
              elevation: _elevationAnimation.value,
              borderRadius: widget.borderRadius,
              color: widget.color ?? Theme.of(context).cardColor,
              child: ClipRRect(
                borderRadius: widget.borderRadius,
                child: widget.child,
              ),
            ),
          );
        },
      ),
    );
  }
}

/// Tilt Card - بطاقة مائلة
/// 3D tilt effect on touch
class TiltCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final double maxTilt;
  final Duration animationDuration;
  final BorderRadius borderRadius;
  final Color? color;
  final double elevation;

  const TiltCard({
    super.key,
    required this.child,
    this.onTap,
    this.maxTilt = 0.08, // radians
    this.animationDuration = const Duration(milliseconds: 200),
    this.borderRadius = const BorderRadius.all(Radius.circular(16)),
    this.color,
    this.elevation = 4,
  });

  @override
  State<TiltCard> createState() => _TiltCardState();
}

class _TiltCardState extends State<TiltCard>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  Offset _touchPosition = Offset.zero;
  bool _isTouching = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.animationDuration,
      vsync: this,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onPanStart(DragStartDetails details) {
    setState(() {
      _isTouching = true;
      _touchPosition = details.localPosition;
    });
    _controller.forward();
  }

  void _onPanUpdate(DragUpdateDetails details) {
    setState(() {
      _touchPosition = details.localPosition;
    });
  }

  void _onPanEnd(DragEndDetails details) {
    setState(() {
      _isTouching = false;
    });
    _controller.reverse();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanStart: _onPanStart,
      onPanUpdate: _onPanUpdate,
      onPanEnd: _onPanEnd,
      onTap: widget.onTap,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final center = Offset(
            constraints.maxWidth / 2,
            constraints.maxHeight / 2,
          );
          final offset = _isTouching ? _touchPosition - center : Offset.zero;
          final normalizedOffset = Offset(
            offset.dx / (constraints.maxWidth / 2),
            offset.dy / (constraints.maxHeight / 2),
          );

          return AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              final tiltX = normalizedOffset.dy * widget.maxTilt * _controller.value;
              final tiltY = -normalizedOffset.dx * widget.maxTilt * _controller.value;

              return Transform(
                alignment: Alignment.center,
                transform: Matrix4.identity()
                  ..setEntry(3, 2, 0.001) // perspective
                  ..rotateX(tiltX)
                  ..rotateY(tiltY),
                child: Material(
                  elevation: widget.elevation + (_controller.value * 4),
                  borderRadius: widget.borderRadius,
                  color: widget.color ?? Theme.of(context).cardColor,
                  child: ClipRRect(
                    borderRadius: widget.borderRadius,
                    child: widget.child,
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

// =============================================================================
// ICON ANIMATIONS - تحريك الأيقونات
// =============================================================================

/// Success Icon Animation - تحريك أيقونة النجاح
/// Animated checkmark that draws itself
class AnimatedSuccessIcon extends StatefulWidget {
  final double size;
  final Color color;
  final Duration duration;
  final bool autoPlay;
  final VoidCallback? onAnimationComplete;

  const AnimatedSuccessIcon({
    super.key,
    this.size = 64,
    this.color = Colors.green,
    this.duration = const Duration(milliseconds: 800),
    this.autoPlay = true,
    this.onAnimationComplete,
  });

  @override
  State<AnimatedSuccessIcon> createState() => AnimatedSuccessIconState();
}

class AnimatedSuccessIconState extends State<AnimatedSuccessIcon>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _circleAnimation;
  late Animation<double> _checkAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    _circleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.5, curve: Curves.easeOut),
      ),
    );

    _checkAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.4, 1.0, curve: Curves.easeOut),
      ),
    );

    _controller.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        widget.onAnimationComplete?.call();
      }
    });

    if (widget.autoPlay) {
      _controller.forward();
    }
  }

  /// Manually play the animation
  void play() {
    _controller.forward(from: 0.0);
  }

  /// Reset the animation
  void reset() {
    _controller.reset();
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
          size: Size(widget.size, widget.size),
          painter: _SuccessIconPainter(
            circleProgress: _circleAnimation.value,
            checkProgress: _checkAnimation.value,
            color: widget.color,
          ),
        );
      },
    );
  }
}

class _SuccessIconPainter extends CustomPainter {
  final double circleProgress;
  final double checkProgress;
  final Color color;

  _SuccessIconPainter({
    required this.circleProgress,
    required this.checkProgress,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;
    final strokeWidth = size.width * 0.08;

    // Draw circle
    final circlePaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * circleProgress,
      false,
      circlePaint,
    );

    // Draw checkmark
    if (checkProgress > 0) {
      final checkPaint = Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round;

      final path = Path();
      final checkStart = Offset(size.width * 0.25, size.height * 0.52);
      final checkMiddle = Offset(size.width * 0.42, size.height * 0.68);
      final checkEnd = Offset(size.width * 0.75, size.height * 0.35);

      if (checkProgress < 0.5) {
        final progress = checkProgress * 2;
        final currentPoint = Offset.lerp(checkStart, checkMiddle, progress)!;
        path.moveTo(checkStart.dx, checkStart.dy);
        path.lineTo(currentPoint.dx, currentPoint.dy);
      } else {
        final progress = (checkProgress - 0.5) * 2;
        path.moveTo(checkStart.dx, checkStart.dy);
        path.lineTo(checkMiddle.dx, checkMiddle.dy);
        final currentPoint = Offset.lerp(checkMiddle, checkEnd, progress)!;
        path.lineTo(currentPoint.dx, currentPoint.dy);
      }

      canvas.drawPath(path, checkPaint);
    }
  }

  @override
  bool shouldRepaint(_SuccessIconPainter oldDelegate) {
    return oldDelegate.circleProgress != circleProgress ||
        oldDelegate.checkProgress != checkProgress;
  }
}

/// Error Icon Animation - تحريك أيقونة الخطأ
/// Animated X mark with shake effect
class AnimatedErrorIcon extends StatefulWidget {
  final double size;
  final Color color;
  final Duration duration;
  final bool autoPlay;
  final VoidCallback? onAnimationComplete;

  const AnimatedErrorIcon({
    super.key,
    this.size = 64,
    this.color = Colors.red,
    this.duration = const Duration(milliseconds: 800),
    this.autoPlay = true,
    this.onAnimationComplete,
  });

  @override
  State<AnimatedErrorIcon> createState() => AnimatedErrorIconState();
}

class AnimatedErrorIconState extends State<AnimatedErrorIcon>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _circleAnimation;
  late Animation<double> _crossAnimation;
  late Animation<double> _shakeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    _circleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.4, curve: Curves.easeOut),
      ),
    );

    _crossAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.3, 0.7, curve: Curves.easeOut),
      ),
    );

    _shakeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.6, 1.0, curve: Curves.elasticOut),
      ),
    );

    _controller.addStatusListener((status) {
      if (status == AnimationStatus.completed) {
        widget.onAnimationComplete?.call();
      }
    });

    if (widget.autoPlay) {
      _controller.forward();
    }
  }

  void play() {
    _controller.forward(from: 0.0);
  }

  void reset() {
    _controller.reset();
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
        final shakeOffset = math.sin(_shakeAnimation.value * math.pi * 4) *
            (1 - _shakeAnimation.value) *
            8;

        return Transform.translate(
          offset: Offset(shakeOffset, 0),
          child: CustomPaint(
            size: Size(widget.size, widget.size),
            painter: _ErrorIconPainter(
              circleProgress: _circleAnimation.value,
              crossProgress: _crossAnimation.value,
              color: widget.color,
            ),
          ),
        );
      },
    );
  }
}

class _ErrorIconPainter extends CustomPainter {
  final double circleProgress;
  final double crossProgress;
  final Color color;

  _ErrorIconPainter({
    required this.circleProgress,
    required this.crossProgress,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 4;
    final strokeWidth = size.width * 0.08;

    // Draw circle
    final circlePaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * circleProgress,
      false,
      circlePaint,
    );

    // Draw cross
    if (crossProgress > 0) {
      final crossPaint = Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = strokeWidth
        ..strokeCap = StrokeCap.round;

      final crossSize = size.width * 0.25;
      final offset = crossSize * crossProgress;

      // First line
      canvas.drawLine(
        Offset(center.dx - offset, center.dy - offset),
        Offset(center.dx + offset, center.dy + offset),
        crossPaint,
      );

      // Second line
      canvas.drawLine(
        Offset(center.dx + offset, center.dy - offset),
        Offset(center.dx - offset, center.dy + offset),
        crossPaint,
      );
    }
  }

  @override
  bool shouldRepaint(_ErrorIconPainter oldDelegate) {
    return oldDelegate.circleProgress != circleProgress ||
        oldDelegate.crossProgress != crossProgress;
  }
}

/// Loading Icon Animation - تحريك أيقونة التحميل
/// Spinning loader with dots
class AnimatedLoadingIcon extends StatefulWidget {
  final double size;
  final Color color;
  final Duration duration;
  final int dotCount;

  const AnimatedLoadingIcon({
    super.key,
    this.size = 48,
    this.color = Colors.green,
    this.duration = const Duration(milliseconds: 1200),
    this.dotCount = 8,
  });

  @override
  State<AnimatedLoadingIcon> createState() => _AnimatedLoadingIconState();
}

class _AnimatedLoadingIconState extends State<AnimatedLoadingIcon>
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
        return CustomPaint(
          size: Size(widget.size, widget.size),
          painter: _LoadingIconPainter(
            progress: _controller.value,
            color: widget.color,
            dotCount: widget.dotCount,
          ),
        );
      },
    );
  }
}

class _LoadingIconPainter extends CustomPainter {
  final double progress;
  final Color color;
  final int dotCount;

  _LoadingIconPainter({
    required this.progress,
    required this.color,
    required this.dotCount,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 8;
    final dotRadius = size.width * 0.06;

    for (int i = 0; i < dotCount; i++) {
      final angle = (i / dotCount) * 2 * math.pi - math.pi / 2;
      final dotCenter = Offset(
        center.dx + radius * math.cos(angle),
        center.dy + radius * math.sin(angle),
      );

      // Calculate opacity based on position and progress
      final dotProgress = (progress - i / dotCount) % 1.0;
      final opacity = (1 - dotProgress).clamp(0.2, 1.0);

      final paint = Paint()..color = color.withValues(alpha: opacity);
      canvas.drawCircle(dotCenter, dotRadius, paint);
    }
  }

  @override
  bool shouldRepaint(_LoadingIconPainter oldDelegate) {
    return oldDelegate.progress != progress;
  }
}

// =============================================================================
// RIPPLE EFFECTS - تأثيرات التموج
// =============================================================================

/// Custom Ripple Effect - تأثير تموج مخصص
/// Creates expanding circles from touch point
class CustomRippleEffect extends StatefulWidget {
  final Widget child;
  final Color rippleColor;
  final Duration duration;
  final VoidCallback? onTap;

  const CustomRippleEffect({
    super.key,
    required this.child,
    this.rippleColor = Colors.white,
    this.duration = const Duration(milliseconds: 400),
    this.onTap,
  });

  @override
  State<CustomRippleEffect> createState() => _CustomRippleEffectState();
}

class _CustomRippleEffectState extends State<CustomRippleEffect>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  Offset? _tapPosition;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTapDown(TapDownDetails details) {
    setState(() {
      _tapPosition = details.localPosition;
    });
    _controller.forward(from: 0.0);
  }

  void _handleTap() {
    widget.onTap?.call();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: _handleTapDown,
      onTap: _handleTap,
      child: ClipRRect(
        child: Stack(
          children: [
            widget.child,
            if (_tapPosition != null)
              Positioned.fill(
                child: AnimatedBuilder(
                  animation: _controller,
                  builder: (context, child) {
                    return CustomPaint(
                      painter: _RipplePainter(
                        center: _tapPosition!,
                        progress: _controller.value,
                        color: widget.rippleColor,
                      ),
                    );
                  },
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _RipplePainter extends CustomPainter {
  final Offset center;
  final double progress;
  final Color color;

  _RipplePainter({
    required this.center,
    required this.progress,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final maxRadius = math.sqrt(size.width * size.width + size.height * size.height);
    final radius = maxRadius * progress;
    final opacity = (1 - progress).clamp(0.0, 0.3);

    final paint = Paint()
      ..color = color.withValues(alpha: opacity)
      ..style = PaintingStyle.fill;

    canvas.drawCircle(center, radius, paint);
  }

  @override
  bool shouldRepaint(_RipplePainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.center != center;
  }
}

// =============================================================================
// PULSE ANIMATIONS - تحريك النبض
// =============================================================================

/// Pulse Widget - عنصر نابض
/// Creates pulsing effect for attention-grabbing
class PulseWidget extends StatefulWidget {
  final Widget child;
  final Duration duration;
  final double minScale;
  final double maxScale;
  final bool infinite;

  const PulseWidget({
    super.key,
    required this.child,
    this.duration = const Duration(milliseconds: 1000),
    this.minScale = 0.95,
    this.maxScale = 1.05,
    this.infinite = true,
  });

  @override
  State<PulseWidget> createState() => _PulseWidgetState();
}

class _PulseWidgetState extends State<PulseWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    );

    _scaleAnimation = Tween<double>(
      begin: widget.minScale,
      end: widget.maxScale,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));

    if (widget.infinite) {
      _controller.repeat(reverse: true);
    } else {
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
      animation: _scaleAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: widget.child,
        );
      },
    );
  }
}

/// Glow Pulse - نبض متوهج
/// Pulsing glow effect around widget
class GlowPulse extends StatefulWidget {
  final Widget child;
  final Color glowColor;
  final double minGlow;
  final double maxGlow;
  final Duration duration;

  const GlowPulse({
    super.key,
    required this.child,
    this.glowColor = Colors.green,
    this.minGlow = 0,
    this.maxGlow = 20,
    this.duration = const Duration(milliseconds: 1500),
  });

  @override
  State<GlowPulse> createState() => _GlowPulseState();
}

class _GlowPulseState extends State<GlowPulse>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    )..repeat(reverse: true);

    _glowAnimation = Tween<double>(
      begin: widget.minGlow,
      end: widget.maxGlow,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _glowAnimation,
      builder: (context, child) {
        return DecoratedBox(
          decoration: BoxDecoration(
            boxShadow: [
              BoxShadow(
                color: widget.glowColor.withValues(alpha: 0.5),
                blurRadius: _glowAnimation.value,
                spreadRadius: _glowAnimation.value / 4,
              ),
            ],
          ),
          child: widget.child,
        );
      },
    );
  }
}

/// Attention Dot - نقطة لفت الانتباه
/// Pulsing notification dot
class AttentionDot extends StatefulWidget {
  final double size;
  final Color color;
  final Duration duration;

  const AttentionDot({
    super.key,
    this.size = 12,
    this.color = Colors.red,
    this.duration = const Duration(milliseconds: 1200),
  });

  @override
  State<AttentionDot> createState() => _AttentionDotState();
}

class _AttentionDotState extends State<AttentionDot>
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
        final scale = 1.0 + (_controller.value * 0.5);
        final opacity = 1.0 - _controller.value;

        return SizedBox(
          width: widget.size * 2,
          height: widget.size * 2,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Pulsing ring
              Transform.scale(
                scale: scale,
                child: Container(
                  width: widget.size,
                  height: widget.size,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: widget.color.withValues(alpha: opacity * 0.5),
                  ),
                ),
              ),
              // Solid dot
              Container(
                width: widget.size,
                height: widget.size,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: widget.color,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
