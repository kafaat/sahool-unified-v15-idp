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

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../theme/atmosphere_theme.dart';

/// Field status indicating the current health/state of a field
enum FieldStatus {
  /// Field is operating normally
  active,

  /// Field requires attention (non-critical)
  warning,

  /// Field requires immediate attention (critical)
  alert,

  /// Field is not currently monitored
  inactive,
}

/// Extension on FieldStatus to provide localized labels
extension FieldStatusExtension on FieldStatus {
  /// Arabic label for the status
  String get labelAr {
    switch (this) {
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

  /// English label for the status
  String get labelEn {
    switch (this) {
      case FieldStatus.active:
        return 'Active';
      case FieldStatus.warning:
        return 'Warning';
      case FieldStatus.alert:
        return 'Alert';
      case FieldStatus.inactive:
        return 'Inactive';
    }
  }
}

/// Holographic Field Card Widget
///
/// Displays a field status card with 3D parallax effect and glassmorphism design.
/// The card shows moisture, temperature, and sunlight metrics with status-based
/// color coding.
class HolographicFieldCard extends StatefulWidget {
  /// Arabic name of the field
  final String fieldName;

  /// English name of the field
  final String fieldNameEn;

  /// Soil moisture percentage (0-100)
  final int moisture;

  /// Temperature in Celsius
  final int temperature;

  /// Sunlight intensity percentage (0-100)
  final int sunlight;

  /// Current status of the field
  final FieldStatus status;

  /// Optional callback when the card is tapped
  final VoidCallback? onTap;

  /// Optional callback when the card is long-pressed
  final VoidCallback? onLongPress;

  const HolographicFieldCard({
    super.key,
    required this.fieldName,
    required this.fieldNameEn,
    required this.moisture,
    required this.temperature,
    required this.sunlight,
    required this.status,
    this.onTap,
    this.onLongPress,
  });

  @override
  State<HolographicFieldCard> createState() => _HolographicFieldCardState();
}

class _HolographicFieldCardState extends State<HolographicFieldCard>
    with SingleTickerProviderStateMixin {
  // Rotation values for 3D effect (kept minimal for performance)
  double _xRotation = 0.0;
  double _yRotation = 0.0;

  // Animation controller for entrance and subtle idle animation
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _fadeAnimation;

  // Flag to track if sensors are available
  bool _sensorsInitialized = false;

  @override
  void initState() {
    super.initState();
    _initializeAnimations();
    _initializeSensors();
  }

  /// Initialize entrance and idle animations
  void _initializeAnimations() {
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

    // Add listener for subtle idle animation (only when entrance completes)
    _controller.addStatusListener((status) {
      if (status == AnimationStatus.completed && !_sensorsInitialized) {
        _startSubtleIdleAnimation();
      }
    });
  }

  /// Initialize device sensors for parallax effect
  void _initializeSensors() {
    // In real implementation, use sensors_plus package:
    // try {
    //   accelerometerEvents.listen((event) {
    //     if (mounted) {
    //       setState(() {
    //         _xRotation = (event.y * 0.01).clamp(-0.05, 0.05);
    //         _yRotation = (-event.x * 0.01).clamp(-0.05, 0.05);
    //       });
    //     }
    //   });
    //   _sensorsInitialized = true;
    // } catch (e) {
    //   _sensorsInitialized = false;
    // }
    _sensorsInitialized = false;
  }

  /// Start a subtle idle animation when sensors are not available
  /// Uses animation controller instead of Timer for better performance
  void _startSubtleIdleAnimation() {
    // Use a slower animation that doesn't trigger excessive rebuilds
    // This is much more efficient than a 50ms timer
    Future.delayed(const Duration(milliseconds: 100), () {
      if (mounted) {
        // Apply a very subtle static tilt for visual interest
        setState(() {
          _xRotation = 0.01;
          _yRotation = -0.01;
        });
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
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

  /// Get status glow color with reduced opacity for accessibility
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

  /// Build the accessibility description for this card
  String get _accessibilityDescription {
    final moistureStatus = _getMoistureDescription(widget.moisture);
    final tempStatus = _getTemperatureDescription(widget.temperature);

    return '${widget.fieldNameEn}, '
        'Status: ${widget.status.labelEn}, '
        'Moisture: ${widget.moisture}% ($moistureStatus), '
        'Temperature: ${widget.temperature} degrees Celsius ($tempStatus), '
        'Sunlight: ${widget.sunlight}%';
  }

  /// Get moisture status description for accessibility
  String _getMoistureDescription(int moisture) {
    if (moisture > 60) return 'high';
    if (moisture > 40) return 'optimal';
    if (moisture > 25) return 'low';
    return 'critical';
  }

  /// Get temperature status description for accessibility
  String _getTemperatureDescription(int temp) {
    if (temp > 35) return 'high';
    if (temp > 30) return 'warm';
    if (temp > 20) return 'optimal';
    return 'cool';
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: _accessibilityDescription,
      hint: 'Double tap to view details, long press for quick actions',
      button: true,
      child: FadeTransition(
        opacity: _fadeAnimation,
        child: ScaleTransition(
          scale: _scaleAnimation,
          child: GestureDetector(
            onTap: () {
              HapticFeedback.mediumImpact();
              widget.onTap?.call();
              // Navigate to field details
            },
            onLongPress: () {
              HapticFeedback.heavyImpact();
              widget.onLongPress?.call();
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
                    color: Color.lerp(
                      Colors.transparent,
                      _statusColor,
                      0.3,
                    )!,
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
                        _buildHeader(),

                        const SizedBox(height: AtmosphereSpacing.lg),

                        // Metrics Row
                        _buildMetricsRow(),

                        const SizedBox(height: AtmosphereSpacing.lg),

                        // Action Button
                        _buildActionButton(),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Build the header row with field name and status badge
  Widget _buildHeader() {
    return Row(
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
              ExcludeSemantics(
                child: Text(
                  widget.fieldNameEn.toUpperCase(),
                  style: AtmosphereTypography.labelSmall,
                ),
              ),
            ],
          ),
        ),
        // Status Badge
        _buildStatusBadge(),
      ],
    );
  }

  /// Build the status indicator badge
  Widget _buildStatusBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AtmosphereSpacing.md,
        vertical: AtmosphereSpacing.sm,
      ),
      decoration: BoxDecoration(
        color: Color.lerp(Colors.transparent, _statusColor, 0.15),
        borderRadius: BorderRadius.circular(AtmosphereRadius.full),
        border: Border.all(
          color: Color.lerp(Colors.transparent, _statusColor, 0.5)!,
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
            widget.status.labelAr,
            style: AtmosphereTypography.labelSmall.copyWith(
              color: _statusColor,
            ),
          ),
        ],
      ),
    );
  }

  /// Build the metrics row with moisture, temperature, and sunlight
  Widget _buildMetricsRow() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        _buildMetric(
          icon: Icons.water_drop_outlined,
          label: 'رطوبة',
          labelEn: 'Moisture',
          value: '${widget.moisture}%',
          color: _getMoistureColor(widget.moisture),
        ),
        _buildMetric(
          icon: Icons.thermostat_outlined,
          label: 'حرارة',
          labelEn: 'Temperature',
          value: '${widget.temperature}°C',
          color: _getTemperatureColor(widget.temperature),
        ),
        _buildMetric(
          icon: Icons.wb_sunny_outlined,
          label: 'إضاءة',
          labelEn: 'Sunlight',
          value: '${widget.sunlight}%',
          color: AtmosphereColors.warning,
        ),
      ],
    );
  }

  /// Build the action button at the bottom of the card
  Widget _buildActionButton() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AtmosphereSpacing.md),
      decoration: BoxDecoration(
        color: Color.lerp(Colors.transparent, _statusColor, 0.1),
        borderRadius: BorderRadius.circular(AtmosphereRadius.md),
        border: Border.all(
          color: Color.lerp(Colors.transparent, _statusColor, 0.5)!,
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.open_in_new,
            color: _statusColor,
            size: 18,
            semanticLabel: 'Open details',
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
    );
  }

  /// Build a single metric display with icon, value, and label
  Widget _buildMetric({
    required IconData icon,
    required String label,
    required String labelEn,
    required String value,
    required Color color,
  }) {
    return Semantics(
      label: '$labelEn: $value',
      excludeSemantics: true,
      child: Column(
        children: [
          Icon(
            icon,
            color: color,
            size: 28,
            semanticLabel: labelEn,
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
      ),
    );
  }

  /// Get color based on moisture level
  /// - > 60%: High (blue)
  /// - 40-60%: Optimal (green)
  /// - 25-40%: Low (yellow)
  /// - < 25%: Critical (red)
  Color _getMoistureColor(int moisture) {
    if (moisture > 60) return AtmosphereColors.info;
    if (moisture > 40) return AtmosphereColors.success;
    if (moisture > 25) return AtmosphereColors.warning;
    return AtmosphereColors.alert;
  }

  /// Get color based on temperature
  /// - > 35°C: High (red)
  /// - 30-35°C: Warm (yellow)
  /// - 20-30°C: Optimal (green)
  /// - < 20°C: Cool (blue)
  Color _getTemperatureColor(int temp) {
    if (temp > 35) return AtmosphereColors.alert;
    if (temp > 30) return AtmosphereColors.warning;
    if (temp > 20) return AtmosphereColors.success;
    return AtmosphereColors.info;
  }
}
