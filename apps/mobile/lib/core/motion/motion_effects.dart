// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Motion Effects
// تأثيرات الحركة - للتأثيرات البصرية الديناميكية
// ═══════════════════════════════════════════════════════════════════════════

import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';

import 'motion_service.dart';
import 'parallax_controller.dart';
import 'parallax_layer.dart';

// ─────────────────────────────────────────────────────────────────────────────
// FLOAT EFFECT
// ─────────────────────────────────────────────────────────────────────────────

/// Configuration for floating effect
/// إعدادات تأثير الطفو
class FloatConfig {
  /// Maximum vertical float distance in pixels
  final double maxVerticalFloat;

  /// Maximum horizontal float distance in pixels
  final double maxHorizontalFloat;

  /// Float animation duration
  final Duration floatDuration;

  /// Whether to enable automatic floating (independent of motion)
  final bool enableAutoFloat;

  /// Auto-float amplitude
  final double autoFloatAmplitude;

  /// Auto-float speed multiplier
  final double autoFloatSpeed;

  /// Whether effect is enabled
  final bool enabled;

  const FloatConfig({
    this.maxVerticalFloat = 10.0,
    this.maxHorizontalFloat = 5.0,
    this.floatDuration = const Duration(milliseconds: 150),
    this.enableAutoFloat = false,
    this.autoFloatAmplitude = 5.0,
    this.autoFloatSpeed = 1.0,
    this.enabled = true,
  });

  static const FloatConfig defaultConfig = FloatConfig();

  static const FloatConfig gentle = FloatConfig(
    maxVerticalFloat: 6.0,
    maxHorizontalFloat: 3.0,
    enableAutoFloat: true,
    autoFloatAmplitude: 3.0,
    autoFloatSpeed: 0.8,
  );

  static const FloatConfig dramatic = FloatConfig(
    maxVerticalFloat: 20.0,
    maxHorizontalFloat: 12.0,
    enableAutoFloat: true,
    autoFloatAmplitude: 8.0,
    autoFloatSpeed: 1.5,
  );

  FloatConfig copyWith({
    double? maxVerticalFloat,
    double? maxHorizontalFloat,
    Duration? floatDuration,
    bool? enableAutoFloat,
    double? autoFloatAmplitude,
    double? autoFloatSpeed,
    bool? enabled,
  }) {
    return FloatConfig(
      maxVerticalFloat: maxVerticalFloat ?? this.maxVerticalFloat,
      maxHorizontalFloat: maxHorizontalFloat ?? this.maxHorizontalFloat,
      floatDuration: floatDuration ?? this.floatDuration,
      enableAutoFloat: enableAutoFloat ?? this.enableAutoFloat,
      autoFloatAmplitude: autoFloatAmplitude ?? this.autoFloatAmplitude,
      autoFloatSpeed: autoFloatSpeed ?? this.autoFloatSpeed,
      enabled: enabled ?? this.enabled,
    );
  }
}

/// Widget that floats gently based on device motion
/// ودجة تطفو برفق بناءً على حركة الجهاز
class FloatEffect extends StatefulWidget {
  /// Child widget
  final Widget child;

  /// Float configuration
  final FloatConfig config;

  /// Whether to respond to device motion
  final bool respondToMotion;

  /// Custom offset callback
  final void Function(Offset offset)? onOffsetChanged;

  const FloatEffect({
    super.key,
    required this.child,
    this.config = FloatConfig.defaultConfig,
    this.respondToMotion = true,
    this.onOffsetChanged,
  });

  @override
  State<FloatEffect> createState() => _FloatEffectState();
}

class _FloatEffectState extends State<FloatEffect>
    with SingleTickerProviderStateMixin {
  late AnimationController _autoFloatController;
  Offset _currentOffset = Offset.zero;

  @override
  void initState() {
    super.initState();

    _autoFloatController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    );

    if (widget.config.enableAutoFloat) {
      _autoFloatController.repeat(reverse: true);
    }
  }

  @override
  void didUpdateWidget(FloatEffect oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (widget.config.enableAutoFloat != oldWidget.config.enableAutoFloat) {
      if (widget.config.enableAutoFloat) {
        _autoFloatController.repeat(reverse: true);
      } else {
        _autoFloatController.stop();
      }
    }
  }

  @override
  void dispose() {
    _autoFloatController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.config.enabled) {
      return widget.child;
    }

    final controller = ParallaxContainer.of(context);

    Widget child = widget.child;

    // Add auto-float animation
    if (widget.config.enableAutoFloat) {
      child = AnimatedBuilder(
        animation: _autoFloatController,
        builder: (context, child) {
          final autoOffset = _calculateAutoFloatOffset();
          return Transform.translate(
            offset: autoOffset,
            child: child,
          );
        },
        child: child,
      );
    }

    // Add motion-based floating
    if (widget.respondToMotion && controller != null) {
      child = AnimatedBuilder(
        animation: controller,
        builder: (context, child) {
          final offset = controller.currentOffset;

          // Calculate float offset
          final floatX = offset.normalizedX * widget.config.maxHorizontalFloat;
          final floatY = -offset.normalizedY * widget.config.maxVerticalFloat;

          _currentOffset = Offset(floatX, floatY);
          widget.onOffsetChanged?.call(_currentOffset);

          return TweenAnimationBuilder<Offset>(
            tween: Tween(begin: Offset.zero, end: _currentOffset),
            duration: widget.config.floatDuration,
            curve: Curves.easeOutCubic,
            builder: (context, offset, child) {
              return Transform.translate(
                offset: offset,
                child: child,
              );
            },
            child: child,
          );
        },
        child: child,
      );
    }

    return child;
  }

  Offset _calculateAutoFloatOffset() {
    final progress = _autoFloatController.value;
    final amplitude = widget.config.autoFloatAmplitude;
    final speed = widget.config.autoFloatSpeed;

    // Use sine wave for smooth floating
    final y = math.sin(progress * math.pi * 2 * speed) * amplitude;
    final x = math.sin(progress * math.pi * 1.5 * speed) * (amplitude * 0.5);

    return Offset(x, y);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// WAVE EFFECT
// ─────────────────────────────────────────────────────────────────────────────

/// Configuration for wave effect
/// إعدادات تأثير الموجة
class WaveConfig {
  /// Wave amplitude in pixels
  final double amplitude;

  /// Wave frequency
  final double frequency;

  /// Wave speed
  final double speed;

  /// Wave direction (0 = horizontal, pi/2 = vertical)
  final double direction;

  /// Whether to use device motion to control wave
  final bool motionControlled;

  /// Phase offset
  final double phaseOffset;

  /// Whether effect is enabled
  final bool enabled;

  const WaveConfig({
    this.amplitude = 8.0,
    this.frequency = 2.0,
    this.speed = 1.0,
    this.direction = 0.0,
    this.motionControlled = true,
    this.phaseOffset = 0.0,
    this.enabled = true,
  });

  static const WaveConfig defaultConfig = WaveConfig();

  static const WaveConfig gentle = WaveConfig(
    amplitude: 4.0,
    frequency: 1.5,
    speed: 0.8,
  );

  static const WaveConfig ocean = WaveConfig(
    amplitude: 12.0,
    frequency: 3.0,
    speed: 1.2,
    direction: math.pi / 4,
  );
}

/// Widget with wave-like motion effect
/// ودجة مع تأثير حركة موجية
class WaveEffect extends StatefulWidget {
  /// Child widget
  final Widget child;

  /// Wave configuration
  final WaveConfig config;

  /// Child index (for offset in lists)
  final int index;

  const WaveEffect({
    super.key,
    required this.child,
    this.config = WaveConfig.defaultConfig,
    this.index = 0,
  });

  @override
  State<WaveEffect> createState() => _WaveEffectState();
}

class _WaveEffectState extends State<WaveEffect>
    with SingleTickerProviderStateMixin {
  late AnimationController _waveController;

  @override
  void initState() {
    super.initState();

    _waveController = AnimationController(
      vsync: this,
      duration: Duration(milliseconds: (2000 / widget.config.speed).round()),
    )..repeat();
  }

  @override
  void dispose() {
    _waveController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.config.enabled) {
      return widget.child;
    }

    final controller = ParallaxContainer.of(context);

    return AnimatedBuilder(
      animation: _waveController,
      builder: (context, child) {
        // Get motion data if available
        double motionInfluence = 1.0;
        if (widget.config.motionControlled && controller != null) {
          final offset = controller.currentOffset;
          motionInfluence = 0.5 + (offset.normalizedX.abs() + offset.normalizedY.abs()) * 0.5;
        }

        // Calculate wave offset
        final phase = _waveController.value * 2 * math.pi * widget.config.frequency;
        final indexOffset = widget.index * 0.5;
        final totalPhase = phase + widget.config.phaseOffset + indexOffset;

        final waveOffset = math.sin(totalPhase) * widget.config.amplitude * motionInfluence;

        // Calculate offset based on direction
        final dx = math.cos(widget.config.direction) * waveOffset;
        final dy = math.sin(widget.config.direction) * waveOffset;

        return Transform.translate(
          offset: Offset(dx, dy),
          child: child,
        );
      },
      child: widget.child,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SHAKE DETECTOR
// ─────────────────────────────────────────────────────────────────────────────

/// Configuration for shake detection
/// إعدادات كشف الاهتزاز
class ShakeConfig {
  /// Minimum acceleration to trigger shake (m/s^2)
  final double threshold;

  /// Minimum time between shake events
  final Duration cooldown;

  /// Number of shakes required to trigger
  final int requiredShakes;

  /// Time window for counting shakes
  final Duration shakeWindow;

  /// Whether detection is enabled
  final bool enabled;

  const ShakeConfig({
    this.threshold = 25.0,
    this.cooldown = const Duration(milliseconds: 500),
    this.requiredShakes = 2,
    this.shakeWindow = const Duration(seconds: 1),
    this.enabled = true,
  });

  static const ShakeConfig defaultConfig = ShakeConfig();

  static const ShakeConfig sensitive = ShakeConfig(
    threshold: 20.0,
    requiredShakes: 1,
  );

  static const ShakeConfig strict = ShakeConfig(
    threshold: 30.0,
    requiredShakes: 3,
    cooldown: Duration(seconds: 1),
  );
}

/// Widget that detects shake gestures
/// ودجة تكتشف إيماءات الاهتزاز
class ShakeDetector extends StatefulWidget {
  /// Child widget
  final Widget child;

  /// Shake configuration
  final ShakeConfig config;

  /// Callback when shake is detected
  final VoidCallback onShake;

  /// Optional visual feedback widget
  final Widget Function(BuildContext context, bool isShaking)? feedbackBuilder;

  const ShakeDetector({
    super.key,
    required this.child,
    required this.onShake,
    this.config = ShakeConfig.defaultConfig,
    this.feedbackBuilder,
  });

  @override
  State<ShakeDetector> createState() => _ShakeDetectorState();
}

class _ShakeDetectorState extends State<ShakeDetector> {
  final MotionService _motionService = MotionService.instance;
  bool _isShaking = false;
  final List<DateTime> _shakeTimes = [];
  DateTime _lastShakeCallback = DateTime.now().subtract(const Duration(seconds: 10));

  @override
  void initState() {
    super.initState();

    if (widget.config.enabled) {
      _motionService.addShakeListener(_onShakeDetected);
    }
  }

  @override
  void didUpdateWidget(ShakeDetector oldWidget) {
    super.didUpdateWidget(oldWidget);

    if (widget.config.enabled != oldWidget.config.enabled) {
      if (widget.config.enabled) {
        _motionService.addShakeListener(_onShakeDetected);
      } else {
        _motionService.removeShakeListener(_onShakeDetected);
      }
    }
  }

  @override
  void dispose() {
    _motionService.removeShakeListener(_onShakeDetected);
    super.dispose();
  }

  void _onShakeDetected() {
    if (!widget.config.enabled) return;

    final now = DateTime.now();

    // Add shake time
    _shakeTimes.add(now);

    // Remove old shake times
    _shakeTimes.removeWhere((time) =>
        now.difference(time) > widget.config.shakeWindow);

    // Check if we have enough shakes
    if (_shakeTimes.length >= widget.config.requiredShakes) {
      // Check cooldown
      if (now.difference(_lastShakeCallback) >= widget.config.cooldown) {
        _lastShakeCallback = now;
        _shakeTimes.clear();

        // Visual feedback
        setState(() => _isShaking = true);
        Future.delayed(const Duration(milliseconds: 300), () {
          if (mounted) {
            setState(() => _isShaking = false);
          }
        });

        // Trigger callback
        widget.onShake();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.feedbackBuilder != null) {
      return widget.feedbackBuilder!(context, _isShaking);
    }

    return widget.child;
  }
}

/// Shake to refresh widget
/// ودجة الاهتزاز للتحديث
class ShakeToRefresh extends StatelessWidget {
  /// Child widget
  final Widget child;

  /// Refresh callback
  final Future<void> Function() onRefresh;

  /// Shake configuration
  final ShakeConfig config;

  /// Show indicator
  final bool showIndicator;

  const ShakeToRefresh({
    super.key,
    required this.child,
    required this.onRefresh,
    this.config = ShakeConfig.defaultConfig,
    this.showIndicator = true,
  });

  @override
  Widget build(BuildContext context) {
    return ShakeDetector(
      config: config,
      onShake: () async {
        if (showIndicator) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Row(
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                  SizedBox(width: 12),
                  Text('جارٍ التحديث...'),
                ],
              ),
              duration: Duration(seconds: 1),
            ),
          );
        }
        await onRefresh();
      },
      child: child,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// ROTATION TRACKER
// ─────────────────────────────────────────────────────────────────────────────

/// Configuration for rotation tracking
/// إعدادات تتبع الدوران
class RotationConfig {
  /// Maximum rotation angle in degrees
  final double maxRotation;

  /// Rotation sensitivity
  final double sensitivity;

  /// Animation duration
  final Duration animationDuration;

  /// Whether effect is enabled
  final bool enabled;

  const RotationConfig({
    this.maxRotation = 15.0,
    this.sensitivity = 1.0,
    this.animationDuration = const Duration(milliseconds: 100),
    this.enabled = true,
  });

  static const RotationConfig defaultConfig = RotationConfig();
}

/// Widget that rotates based on device rotation
/// ودجة تدور بناءً على دوران الجهاز
class RotationTracker extends StatelessWidget {
  /// Child widget
  final Widget child;

  /// Rotation configuration
  final RotationConfig config;

  /// Rotation axis (x, y, z)
  final Axis3D axis;

  const RotationTracker({
    super.key,
    required this.child,
    this.config = RotationConfig.defaultConfig,
    this.axis = Axis3D.z,
  });

  @override
  Widget build(BuildContext context) {
    if (!config.enabled) {
      return child;
    }

    final controller = ParallaxContainer.of(context);

    if (controller == null) {
      return child;
    }

    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        final offset = controller.currentOffset;

        // Calculate rotation based on axis
        double rotation = 0.0;
        switch (axis) {
          case Axis3D.x:
            rotation = offset.normalizedY * config.maxRotation * config.sensitivity;
            break;
          case Axis3D.y:
            rotation = offset.normalizedX * config.maxRotation * config.sensitivity;
            break;
          case Axis3D.z:
            rotation = (offset.normalizedX + offset.normalizedY) / 2 *
                config.maxRotation *
                config.sensitivity;
            break;
        }

        final radians = rotation * (math.pi / 180);

        return TweenAnimationBuilder<double>(
          tween: Tween(begin: 0.0, end: radians),
          duration: config.animationDuration,
          curve: Curves.easeOutCubic,
          builder: (context, angle, child) {
            Matrix4 transform = Matrix4.identity();

            switch (axis) {
              case Axis3D.x:
                transform.rotateX(angle);
                break;
              case Axis3D.y:
                transform.rotateY(angle);
                break;
              case Axis3D.z:
                transform.rotateZ(angle);
                break;
            }

            return Transform(
              transform: transform,
              alignment: Alignment.center,
              child: child,
            );
          },
          child: child,
        );
      },
      child: child,
    );
  }
}

/// 3D axis enum
enum Axis3D { x, y, z }

// ─────────────────────────────────────────────────────────────────────────────
// FLOATING ACTION BUTTON WITH MOTION
// ─────────────────────────────────────────────────────────────────────────────

/// Floating action button with motion effects
/// زر الإجراء العائم مع تأثيرات الحركة
class MotionFloatingActionButton extends StatelessWidget {
  /// Button icon
  final IconData icon;

  /// Button label (optional, for extended FAB)
  final String? label;

  /// On pressed callback
  final VoidCallback onPressed;

  /// Background color
  final Color? backgroundColor;

  /// Foreground color
  final Color? foregroundColor;

  /// Enable float effect
  final bool enableFloat;

  /// Enable tilt effect
  final bool enableTilt;

  /// Float configuration
  final FloatConfig floatConfig;

  /// Whether it's an extended FAB
  final bool isExtended;

  /// Hero tag
  final Object? heroTag;

  const MotionFloatingActionButton({
    super.key,
    required this.icon,
    required this.onPressed,
    this.label,
    this.backgroundColor,
    this.foregroundColor,
    this.enableFloat = true,
    this.enableTilt = true,
    this.floatConfig = FloatConfig.gentle,
    this.isExtended = false,
    this.heroTag,
  });

  @override
  Widget build(BuildContext context) {
    Widget fab;

    if (isExtended && label != null) {
      fab = FloatingActionButton.extended(
        onPressed: onPressed,
        icon: Icon(icon),
        label: Text(label!),
        backgroundColor: backgroundColor,
        foregroundColor: foregroundColor,
        heroTag: heroTag,
      );
    } else {
      fab = FloatingActionButton(
        onPressed: onPressed,
        backgroundColor: backgroundColor,
        foregroundColor: foregroundColor,
        heroTag: heroTag,
        child: Icon(icon),
      );
    }

    // Wrap with float effect
    if (enableFloat) {
      fab = FloatEffect(
        config: floatConfig,
        child: fab,
      );
    }

    // Wrap with rotation
    if (enableTilt) {
      fab = RotationTracker(
        config: const RotationConfig(maxRotation: 8.0),
        axis: Axis3D.z,
        child: fab,
      );
    }

    return fab;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// BOBBING EFFECT
// ─────────────────────────────────────────────────────────────────────────────

/// Widget with gentle bobbing animation
/// ودجة مع حركة ترجرج لطيفة
class BobbingEffect extends StatefulWidget {
  /// Child widget
  final Widget child;

  /// Bobbing amplitude
  final double amplitude;

  /// Bobbing duration
  final Duration duration;

  /// Whether to also rotate slightly
  final bool enableRotation;

  /// Maximum rotation angle
  final double maxRotation;

  /// Whether effect is enabled
  final bool enabled;

  const BobbingEffect({
    super.key,
    required this.child,
    this.amplitude = 5.0,
    this.duration = const Duration(seconds: 2),
    this.enableRotation = true,
    this.maxRotation = 3.0,
    this.enabled = true,
  });

  @override
  State<BobbingEffect> createState() => _BobbingEffectState();
}

class _BobbingEffectState extends State<BobbingEffect>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.enabled) {
      return widget.child;
    }

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final progress = Curves.easeInOut.transform(_controller.value);

        final yOffset = (progress * 2 - 1) * widget.amplitude;
        final rotation = widget.enableRotation
            ? (progress * 2 - 1) * widget.maxRotation * (math.pi / 180)
            : 0.0;

        return Transform(
          transform: Matrix4.identity()
            ..translate(0.0, yOffset)
            ..rotateZ(rotation),
          alignment: Alignment.center,
          child: child,
        );
      },
      child: widget.child,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PULSE EFFECT
// ─────────────────────────────────────────────────────────────────────────────

/// Widget with pulsing scale effect
/// ودجة مع تأثير نبض بالحجم
class PulseEffect extends StatefulWidget {
  /// Child widget
  final Widget child;

  /// Minimum scale
  final double minScale;

  /// Maximum scale
  final double maxScale;

  /// Pulse duration
  final Duration duration;

  /// Whether effect is enabled
  final bool enabled;

  const PulseEffect({
    super.key,
    required this.child,
    this.minScale = 0.95,
    this.maxScale = 1.05,
    this.duration = const Duration(milliseconds: 1500),
    this.enabled = true,
  });

  @override
  State<PulseEffect> createState() => _PulseEffectState();
}

class _PulseEffectState extends State<PulseEffect>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();

    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.enabled) {
      return widget.child;
    }

    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final progress = Curves.easeInOut.transform(_controller.value);
        final scale = widget.minScale + (widget.maxScale - widget.minScale) * progress;

        return Transform.scale(
          scale: scale,
          child: child,
        );
      },
      child: widget.child,
    );
  }
}
