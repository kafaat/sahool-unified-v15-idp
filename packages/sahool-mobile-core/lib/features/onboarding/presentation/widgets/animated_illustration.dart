import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../../../../core/theme/sahool_theme.dart';

/// SAHOOL Animated Illustration Widget
/// ويدجت الرسم التوضيحي المتحرك
///
/// Creates animated illustrations for onboarding screens
/// ينشئ رسوم توضيحية متحركة لشاشات الإعداد

/// Types of animated illustrations
/// أنواع الرسوم التوضيحية المتحركة
enum IllustrationType {
  welcome,
  field,
  weather,
  ndvi,
  irrigation,
  tasks,
  completion,
}

class AnimatedIllustration extends StatefulWidget {
  /// Type of illustration to display
  final IllustrationType type;

  /// Size of the illustration
  final double size;

  /// Primary color override
  final Color? primaryColor;

  /// Whether animation is enabled
  final bool enableAnimation;

  const AnimatedIllustration({
    super.key,
    required this.type,
    this.size = 200,
    this.primaryColor,
    this.enableAnimation = true,
  });

  @override
  State<AnimatedIllustration> createState() => _AnimatedIllustrationState();
}

class _AnimatedIllustrationState extends State<AnimatedIllustration>
    with TickerProviderStateMixin {
  late AnimationController _mainController;
  late AnimationController _secondaryController;
  late Animation<double> _floatAnimation;
  late Animation<double> _pulseAnimation;
  late Animation<double> _rotateAnimation;

  @override
  void initState() {
    super.initState();

    _mainController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: this,
    );

    _secondaryController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    );

    _floatAnimation = Tween<double>(begin: -10, end: 10).animate(
      CurvedAnimation(parent: _mainController, curve: Curves.easeInOut),
    );

    _pulseAnimation = Tween<double>(begin: 0.95, end: 1.05).animate(
      CurvedAnimation(parent: _secondaryController, curve: Curves.easeInOut),
    );

    _rotateAnimation = Tween<double>(begin: -0.02, end: 0.02).animate(
      CurvedAnimation(parent: _mainController, curve: Curves.easeInOut),
    );

    if (widget.enableAnimation) {
      _mainController.repeat(reverse: true);
      _secondaryController.repeat(reverse: true);
    }
  }

  @override
  void dispose() {
    _mainController.dispose();
    _secondaryController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = widget.primaryColor ?? SahoolColors.primary;

    return SizedBox(
      width: widget.size,
      height: widget.size,
      child: AnimatedBuilder(
        animation: Listenable.merge([_mainController, _secondaryController]),
        builder: (context, child) {
          return _buildIllustration(color);
        },
      ),
    );
  }

  Widget _buildIllustration(Color color) {
    switch (widget.type) {
      case IllustrationType.welcome:
        return _buildWelcomeIllustration(color);
      case IllustrationType.field:
        return _buildFieldIllustration(color);
      case IllustrationType.weather:
        return _buildWeatherIllustration(color);
      case IllustrationType.ndvi:
        return _buildNdviIllustration(color);
      case IllustrationType.irrigation:
        return _buildIrrigationIllustration(color);
      case IllustrationType.tasks:
        return _buildTasksIllustration(color);
      case IllustrationType.completion:
        return _buildCompletionIllustration(color);
    }
  }

  Widget _buildWelcomeIllustration(Color color) {
    return Stack(
      alignment: Alignment.center,
      children: [
        // Background circles
        Transform.translate(
          offset: Offset(0, _floatAnimation.value),
          child: Transform.scale(
            scale: _pulseAnimation.value,
            child: Container(
              width: widget.size * 0.8,
              height: widget.size * 0.8,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    color.withValues(alpha: 0.2),
                    color.withValues(alpha: 0.05),
                  ],
                ),
              ),
            ),
          ),
        ),

        // Rotating elements
        Transform.rotate(
          angle: _rotateAnimation.value,
          child: Transform.translate(
            offset: Offset(0, _floatAnimation.value * 0.5),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Logo/Icon
                Container(
                  width: widget.size * 0.4,
                  height: widget.size * 0.4,
                  decoration: BoxDecoration(
                    color: color,
                    borderRadius: BorderRadius.circular(widget.size * 0.12),
                    boxShadow: [
                      BoxShadow(
                        color: color.withValues(alpha: 0.3),
                        blurRadius: 20,
                        spreadRadius: 5,
                      ),
                    ],
                  ),
                  child: Icon(
                    Icons.eco_rounded,
                    size: widget.size * 0.25,
                    color: Colors.white,
                  ),
                ),
                SizedBox(height: widget.size * 0.08),
                // Arabic text "ساهول"
                Text(
                  'ساهول',
                  style: TextStyle(
                    fontSize: widget.size * 0.12,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ],
            ),
          ),
        ),

        // Decorative elements
        ..._buildDecorations(color),
      ],
    );
  }

  Widget _buildFieldIllustration(Color color) {
    return Stack(
      alignment: Alignment.center,
      children: [
        // Field background
        Transform.translate(
          offset: Offset(0, _floatAnimation.value * 0.5),
          child: Container(
            width: widget.size * 0.85,
            height: widget.size * 0.6,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Stack(
              children: [
                // Field rows
                ...List.generate(4, (index) {
                  return Positioned(
                    top: widget.size * 0.1 + (index * widget.size * 0.12),
                    left: widget.size * 0.05,
                    right: widget.size * 0.05,
                    child: Container(
                      height: widget.size * 0.04,
                      decoration: BoxDecoration(
                        color: color.withValues(alpha: 0.3 + (index * 0.1)),
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ),
                  );
                }),
              ],
            ),
          ),
        ),

        // Field marker icon
        Transform.translate(
          offset: Offset(0, _floatAnimation.value),
          child: Transform.scale(
            scale: _pulseAnimation.value,
            child: Container(
              width: widget.size * 0.25,
              height: widget.size * 0.25,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: color.withValues(alpha: 0.4),
                    blurRadius: 15,
                  ),
                ],
              ),
              child: Icon(
                Icons.landscape_rounded,
                size: widget.size * 0.15,
                color: Colors.white,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildWeatherIllustration(Color color) {
    return Stack(
      alignment: Alignment.center,
      children: [
        // Sun
        Transform.translate(
          offset: Offset(widget.size * 0.15, -widget.size * 0.15 + _floatAnimation.value * 0.5),
          child: Transform.scale(
            scale: _pulseAnimation.value,
            child: Container(
              width: widget.size * 0.3,
              height: widget.size * 0.3,
              decoration: BoxDecoration(
                color: Colors.amber,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.amber.withValues(alpha: 0.4),
                    blurRadius: 20,
                    spreadRadius: 5,
                  ),
                ],
              ),
            ),
          ),
        ),

        // Cloud
        Transform.translate(
          offset: Offset(-widget.size * 0.1, _floatAnimation.value),
          child: Container(
            width: widget.size * 0.5,
            height: widget.size * 0.3,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(widget.size * 0.15),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.1),
                  blurRadius: 10,
                ),
              ],
            ),
            child: Icon(
              Icons.cloud_rounded,
              size: widget.size * 0.2,
              color: color.withValues(alpha: 0.6),
            ),
          ),
        ),

        // Weather icon
        Transform.translate(
          offset: Offset(0, widget.size * 0.25 + _floatAnimation.value * 0.3),
          child: Icon(
            Icons.thermostat_rounded,
            size: widget.size * 0.15,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildNdviIllustration(Color color) {
    return Stack(
      alignment: Alignment.center,
      children: [
        // Satellite dish
        Transform.rotate(
          angle: _rotateAnimation.value,
          child: Transform.translate(
            offset: Offset(0, _floatAnimation.value * 0.5),
            child: Container(
              width: widget.size * 0.6,
              height: widget.size * 0.6,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Colors.green[300]!,
                    Colors.green[700]!,
                  ],
                ),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Stack(
                children: [
                  // NDVI zones
                  Positioned(
                    top: widget.size * 0.1,
                    left: widget.size * 0.08,
                    child: Container(
                      width: widget.size * 0.15,
                      height: widget.size * 0.15,
                      decoration: BoxDecoration(
                        color: Colors.green[800],
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                  Positioned(
                    bottom: widget.size * 0.1,
                    right: widget.size * 0.08,
                    child: Container(
                      width: widget.size * 0.12,
                      height: widget.size * 0.12,
                      decoration: BoxDecoration(
                        color: Colors.yellow[600],
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),

        // Satellite icon
        Transform.translate(
          offset: Offset(widget.size * 0.25, -widget.size * 0.25 + _floatAnimation.value),
          child: Transform.scale(
            scale: _pulseAnimation.value,
            child: Container(
              width: widget.size * 0.2,
              height: widget.size * 0.2,
              decoration: BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.2),
                    blurRadius: 10,
                  ),
                ],
              ),
              child: Icon(
                Icons.satellite_alt_rounded,
                size: widget.size * 0.12,
                color: color,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildIrrigationIllustration(Color color) {
    return Stack(
      alignment: Alignment.center,
      children: [
        // Water drops
        ...List.generate(3, (index) {
          final angle = (index * 2 * math.pi / 3) + (_mainController.value * 0.5);
          final radius = widget.size * 0.25;
          return Transform.translate(
            offset: Offset(
              math.cos(angle) * radius,
              math.sin(angle) * radius + _floatAnimation.value,
            ),
            child: Transform.scale(
              scale: 0.8 + (index * 0.1),
              child: Icon(
                Icons.water_drop_rounded,
                size: widget.size * 0.12,
                color: Colors.blue.withValues(alpha: 0.7 - (index * 0.1)),
              ),
            ),
          );
        }),

        // Central sprinkler
        Transform.translate(
          offset: Offset(0, _floatAnimation.value * 0.5),
          child: Transform.scale(
            scale: _pulseAnimation.value,
            child: Container(
              width: widget.size * 0.35,
              height: widget.size * 0.35,
              decoration: BoxDecoration(
                color: Colors.blue,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.blue.withValues(alpha: 0.4),
                    blurRadius: 20,
                    spreadRadius: 5,
                  ),
                ],
              ),
              child: Icon(
                Icons.water_drop_rounded,
                size: widget.size * 0.2,
                color: Colors.white,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildTasksIllustration(Color color) {
    return Stack(
      alignment: Alignment.center,
      children: [
        // Task cards
        ...List.generate(3, (index) {
          final yOffset = (index - 1) * widget.size * 0.12;
          return Transform.translate(
            offset: Offset(
              (index - 1) * widget.size * 0.05,
              yOffset + _floatAnimation.value * (0.5 + index * 0.2),
            ),
            child: Transform.rotate(
              angle: (index - 1) * 0.05 + _rotateAnimation.value,
              child: Container(
                width: widget.size * 0.6,
                height: widget.size * 0.15,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Row(
                  children: [
                    Container(
                      width: widget.size * 0.08,
                      height: widget.size * 0.08,
                      margin: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: index == 1 ? Colors.orange : Colors.green,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        index == 1 ? Icons.pending : Icons.check,
                        color: Colors.white,
                        size: widget.size * 0.05,
                      ),
                    ),
                    Expanded(
                      child: Container(
                        margin: const EdgeInsets.symmetric(vertical: 12),
                        height: 8,
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                  ],
                ),
              ),
            ),
          );
        }),

        // Clipboard icon
        Transform.translate(
          offset: Offset(widget.size * 0.25, -widget.size * 0.2 + _floatAnimation.value * 0.3),
          child: Transform.scale(
            scale: _pulseAnimation.value,
            child: Container(
              width: widget.size * 0.18,
              height: widget.size * 0.18,
              decoration: BoxDecoration(
                color: Colors.orange,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Colors.orange.withValues(alpha: 0.4),
                    blurRadius: 10,
                  ),
                ],
              ),
              child: Icon(
                Icons.assignment_rounded,
                size: widget.size * 0.1,
                color: Colors.white,
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCompletionIllustration(Color color) {
    return Stack(
      alignment: Alignment.center,
      children: [
        // Celebration particles
        ..._buildCelebrationParticles(color),

        // Trophy/checkmark
        Transform.translate(
          offset: Offset(0, _floatAnimation.value * 0.5),
          child: Transform.scale(
            scale: _pulseAnimation.value,
            child: Container(
              width: widget.size * 0.45,
              height: widget.size * 0.45,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    color,
                    color.withValues(alpha: 0.8),
                  ],
                ),
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: color.withValues(alpha: 0.4),
                    blurRadius: 30,
                    spreadRadius: 10,
                  ),
                ],
              ),
              child: Icon(
                Icons.check_rounded,
                size: widget.size * 0.25,
                color: Colors.white,
              ),
            ),
          ),
        ),
      ],
    );
  }

  List<Widget> _buildDecorations(Color color) {
    return List.generate(5, (index) {
      final angle = (index * 2 * math.pi / 5) + (_mainController.value * 0.3);
      final radius = widget.size * 0.4;
      return Positioned(
        left: widget.size / 2 + math.cos(angle) * radius - 10,
        top: widget.size / 2 + math.sin(angle) * radius - 10,
        child: Container(
          width: 20,
          height: 20,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.3 - (index * 0.05)),
            shape: BoxShape.circle,
          ),
        ),
      );
    });
  }

  List<Widget> _buildCelebrationParticles(Color color) {
    return List.generate(8, (index) {
      final angle = (index * 2 * math.pi / 8) + (_mainController.value * 2);
      final radius = widget.size * (0.3 + _pulseAnimation.value * 0.1);
      final particleColor = [
        Colors.amber,
        color,
        Colors.orange,
        Colors.green,
      ][index % 4];

      return Transform.translate(
        offset: Offset(
          math.cos(angle) * radius,
          math.sin(angle) * radius,
        ),
        child: Transform.scale(
          scale: 0.6 + (math.sin(angle + _mainController.value * 4) * 0.3),
          child: Icon(
            Icons.star_rounded,
            size: widget.size * 0.08,
            color: particleColor,
          ),
        ),
      );
    });
  }
}
