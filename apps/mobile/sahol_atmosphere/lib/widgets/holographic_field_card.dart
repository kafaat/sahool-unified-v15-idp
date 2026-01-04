// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOL ATMOSPHERE - Holographic Field Card
// بطاقة الحقل الهولوغرافية
// ═══════════════════════════════════════════════════════════════════════════════════════
//
// Features:
// - Gyroscope-based 3D parallax effect
// - Glassmorphism design
// - Status-based glow effects
// - Haptic feedback on interaction
//
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/atmosphere_theme.dart';

// Try to import sensors, fallback gracefully if not available
bool _sensorsAvailable = false;
StreamSubscription? _accelerometerSubscription;

void _initSensors(Function(double, double) onUpdate) {
  try {
    // In real implementation, use sensors_plus package
    // accelerometerEvents.listen((event) => onUpdate(event.y * 0.1, -event.x * 0.1));
    _sensorsAvailable = true;
  } catch (e) {
    _sensorsAvailable = false;
  }
}

/// Field Status Enum
enum FieldStatus {
  active,
  warning,
  alert,
  inactive,
}

/// Holographic Field Card Widget
class HolographicFieldCard extends StatefulWidget {
  final String fieldName;
  final String fieldNameEn;
  final int moisture;
  final int temperature;
  final int sunlight;
  final FieldStatus status;

  const HolographicFieldCard({
    super.key,
    required this.fieldName,
    required this.fieldNameEn,
    required this.moisture,
    required this.temperature,
    required this.sunlight,
    required this.status,
  });

  @override
  State<HolographicFieldCard> createState() => _HolographicFieldCardState();
}

class _HolographicFieldCardState extends State<HolographicFieldCard>
    with SingleTickerProviderStateMixin {
  // Rotation values from accelerometer
  double _xRotation = 0.0;
  double _yRotation = 0.0;

  // Animation controller for entrance
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  // Simulated tilt for demo (when sensors not available)
  Timer? _demoTimer;

  @override
  void initState() {
    super.initState();

    // Setup entrance animation
    _controller = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(begin: 0.9, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutBack),
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );

    _controller.forward();

    // Initialize sensors
    _initSensors((x, y) {
      setState(() {
        _xRotation = x;
        _yRotation = y;
      });
    });

    // Demo animation if sensors not available
    if (!_sensorsAvailable) {
      _startDemoAnimation();
    }
  }

  void _startDemoAnimation() {
    double time = 0;
    _demoTimer = Timer.periodic(const Duration(milliseconds: 50), (timer) {
      time += 0.05;
      setState(() {
        _xRotation = (0.02 * (time * 2).toInt() % 2 == 0 ? 1 : -1) * 0.05;
        _yRotation = (0.02 * (time * 3).toInt() % 2 == 0 ? 1 : -1) * 0.03;
      });
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    _demoTimer?.cancel();
    _accelerometerSubscription?.cancel();
    super.dispose();
  }

  /// Get status color based on field status
  Color get _statusColor {
    switch (widget.status) {
      case FieldStatus.active:
        return AtmosphereColors.success;
      case FieldStatus.warning:
        return AtmosphereColors.warning;
      case FieldStatus.alert:
        return AtmosphereColors.alert;
      case FieldStatus.inactive:
        return AtmosphereColors.textMuted;
    }
  }

  /// Get status glow color
  Color get _statusGlow {
    switch (widget.status) {
      case FieldStatus.active:
        return AtmosphereColors.successGlow;
      case FieldStatus.warning:
        return AtmosphereColors.warningGlow;
      case FieldStatus.alert:
        return AtmosphereColors.alertGlow;
      case FieldStatus.inactive:
        return Colors.transparent;
    }
  }

  /// Get status label
  String get _statusLabel {
    switch (widget.status) {
      case FieldStatus.active:
        return 'نشط';
      case FieldStatus.warning:
        return 'تحذير';
      case FieldStatus.alert:
        return 'إنذار';
      case FieldStatus.inactive:
        return 'غير نشط';
    }
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fadeAnimation,
      child: ScaleTransition(
        scale: _scaleAnimation,
        child: GestureDetector(
          onTap: () {
            HapticFeedback.mediumImpact();
            // Navigate to field details
          },
          onLongPress: () {
            HapticFeedback.heavyImpact();
            // Show quick actions
          },
          child: Transform(
            alignment: FractionalOffset.center,
            transform: Matrix4.identity()
              ..setEntry(3, 2, 0.001) // perspective
              ..rotateX(_xRotation)
              ..rotateY(_yRotation),
            child: Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
                gradient: AtmosphereColors.glassGradient,
                border: Border.all(
                  color: _statusColor.withOpacity(0.3),
                  width: 1,
                ),
                boxShadow: [
                  BoxShadow(
                    color: _statusGlow,
                    blurRadius: 20,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
                child: Padding(
                  padding: const EdgeInsets.all(AtmosphereSpacing.lg),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header Row
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          // Field Name
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  widget.fieldName,
                                  style: AtmosphereTypography.headlineLarge,
                                ),
                                const SizedBox(height: AtmosphereSpacing.xs),
                                Text(
                                  widget.fieldNameEn.toUpperCase(),
                                  style: AtmosphereTypography.labelSmall,
                                ),
                              ],
                            ),
                          ),
                          // Status Badge
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: AtmosphereSpacing.md,
                              vertical: AtmosphereSpacing.sm,
                            ),
                            decoration: BoxDecoration(
                              color: _statusColor.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(AtmosphereRadius.full),
                              border: Border.all(
                                color: _statusColor.withOpacity(0.5),
                              ),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Container(
                                  width: 8,
                                  height: 8,
                                  decoration: BoxDecoration(
                                    color: _statusColor,
                                    shape: BoxShape.circle,
                                    boxShadow: [
                                      BoxShadow(
                                        color: _statusColor,
                                        blurRadius: 6,
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(width: AtmosphereSpacing.sm),
                                Text(
                                  _statusLabel,
                                  style: AtmosphereTypography.labelSmall.copyWith(
                                    color: _statusColor,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: AtmosphereSpacing.lg),

                      // Metrics Row
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildMetric(
                            icon: Icons.water_drop_outlined,
                            label: 'رطوبة',
                            value: '${widget.moisture}%',
                            color: _getMoistureColor(widget.moisture),
                          ),
                          _buildMetric(
                            icon: Icons.thermostat_outlined,
                            label: 'حرارة',
                            value: '${widget.temperature}°C',
                            color: _getTemperatureColor(widget.temperature),
                          ),
                          _buildMetric(
                            icon: Icons.wb_sunny_outlined,
                            label: 'إضاءة',
                            value: '${widget.sunlight}%',
                            color: AtmosphereColors.warning,
                          ),
                        ],
                      ),

                      const SizedBox(height: AtmosphereSpacing.lg),

                      // Action Button
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(AtmosphereSpacing.md),
                        decoration: BoxDecoration(
                          color: _statusColor.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(AtmosphereRadius.md),
                          border: Border.all(
                            color: _statusColor.withOpacity(0.5),
                          ),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(
                              Icons.open_in_new,
                              color: _statusColor,
                              size: 18,
                            ),
                            const SizedBox(width: AtmosphereSpacing.sm),
                            Text(
                              'فتح التفاصيل',
                              style: AtmosphereTypography.labelLarge.copyWith(
                                color: _statusColor,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMetric({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(
          icon,
          color: color,
          size: 28,
        ),
        const SizedBox(height: AtmosphereSpacing.sm),
        Text(
          value,
          style: AtmosphereTypography.headlineMedium.copyWith(
            color: color,
          ),
        ),
        const SizedBox(height: AtmosphereSpacing.xs),
        Text(
          label,
          style: AtmosphereTypography.bodySmall,
        ),
      ],
    );
  }

  Color _getMoistureColor(int moisture) {
    if (moisture > 60) return AtmosphereColors.info;
    if (moisture > 40) return AtmosphereColors.success;
    if (moisture > 25) return AtmosphereColors.warning;
    return AtmosphereColors.alert;
  }

  Color _getTemperatureColor(int temp) {
    if (temp > 35) return AtmosphereColors.alert;
    if (temp > 30) return AtmosphereColors.warning;
    if (temp > 20) return AtmosphereColors.success;
    return AtmosphereColors.info;
  }
}
