/// Pivot Irrigation Visualization Widget - Valley Style
/// ودجة عرض الري المحوري - بأسلوب فالي
library;

import 'dart:math' as math;
import 'package:flutter/material.dart';
import '../../domain/models/pivot_models.dart';

/// Valley-style pivot visualization widget
/// عنصر عرض المحوري بأسلوب فالي
class PivotVisualization extends StatefulWidget {
  final PivotConfiguration config;
  final PivotStatus? status;
  final bool showSectors;
  final bool showVRIZones;
  final bool showNDVI;
  final bool showArm;
  final bool animate;
  final Function(PivotSector)? onSectorTap;
  final Function(VRIZone)? onVRIZoneTap;
  final double? size;

  const PivotVisualization({
    super.key,
    required this.config,
    this.status,
    this.showSectors = true,
    this.showVRIZones = false,
    this.showNDVI = false,
    this.showArm = true,
    this.animate = true,
    this.onSectorTap,
    this.onVRIZoneTap,
    this.size,
  });

  @override
  State<PivotVisualization> createState() => _PivotVisualizationState();
}

class _PivotVisualizationState extends State<PivotVisualization>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _armAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(seconds: 60), // Full rotation in 60s for animation
      vsync: this,
    );

    _armAnimation = Tween<double>(begin: 0, end: 2 * math.pi).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.linear),
    );

    if (widget.animate && widget.status?.isIrrigating == true) {
      _animationController.repeat();
    }
  }

  @override
  void didUpdateWidget(PivotVisualization oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.status?.isIrrigating == true && widget.animate) {
      if (!_animationController.isAnimating) {
        _animationController.repeat();
      }
    } else {
      _animationController.stop();
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final size = widget.size ?? MediaQuery.of(context).size.width - 32;

    return SizedBox(
      width: size,
      height: size,
      child: AnimatedBuilder(
        animation: _animationController,
        builder: (context, child) {
          return GestureDetector(
            onTapUp: (details) => _handleTap(details, size),
            child: CustomPaint(
              size: Size(size, size),
              painter: _PivotPainter(
                config: widget.config,
                status: widget.status,
                showSectors: widget.showSectors,
                showVRIZones: widget.showVRIZones,
                showNDVI: widget.showNDVI,
                showArm: widget.showArm,
                armAngle: widget.status?.currentAngle ?? 0,
                animatedAngle: widget.animate && widget.status?.isIrrigating == true
                    ? _armAnimation.value
                    : null,
              ),
            ),
          );
        },
      ),
    );
  }

  void _handleTap(TapUpDetails details, double size) {
    final center = Offset(size / 2, size / 2);
    final tapOffset = details.localPosition - center;
    final angle = (math.atan2(tapOffset.dy, tapOffset.dx) * 180 / math.pi + 90 + 360) % 360;
    final distance = tapOffset.distance;
    final radius = size / 2 * 0.9;

    if (distance > radius) return; // Outside pivot circle

    // Find tapped sector
    for (final sector in widget.config.sectors) {
      if (angle >= sector.startAngle && angle <= sector.endAngle) {
        widget.onSectorTap?.call(sector);
        return;
      }
    }
  }
}

/// Custom painter for pivot visualization
class _PivotPainter extends CustomPainter {
  final PivotConfiguration config;
  final PivotStatus? status;
  final bool showSectors;
  final bool showVRIZones;
  final bool showNDVI;
  final bool showArm;
  final double armAngle;
  final double? animatedAngle;

  _PivotPainter({
    required this.config,
    this.status,
    required this.showSectors,
    required this.showVRIZones,
    required this.showNDVI,
    required this.showArm,
    required this.armAngle,
    this.animatedAngle,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 * 0.9;

    // Draw background circle
    _drawBackgroundCircle(canvas, center, radius);

    // Draw sectors
    if (showSectors && config.sectors.isNotEmpty) {
      _drawSectors(canvas, center, radius);
    } else {
      _drawDefaultSectors(canvas, center, radius);
    }

    // Draw VRI zones overlay
    if (showVRIZones && config.vriZones.isNotEmpty) {
      _drawVRIZones(canvas, center, radius);
    }

    // Draw center point (pivot tower)
    _drawCenterTower(canvas, center);

    // Draw span towers
    _drawSpanTowers(canvas, center, radius);

    // Draw pivot arm
    if (showArm) {
      _drawPivotArm(canvas, center, radius);
    }

    // Draw direction indicators
    _drawDirectionIndicators(canvas, center, radius);

    // Draw scale ring
    _drawScaleRing(canvas, center, radius);
  }

  void _drawBackgroundCircle(Canvas canvas, Offset center, double radius) {
    final bgPaint = Paint()
      ..color = Colors.grey[200]!
      ..style = PaintingStyle.fill;

    canvas.drawCircle(center, radius, bgPaint);

    // Border
    final borderPaint = Paint()
      ..color = Colors.grey[400]!
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;

    canvas.drawCircle(center, radius, borderPaint);
  }

  void _drawSectors(Canvas canvas, Offset center, double radius) {
    for (final sector in config.sectors) {
      final startAngle = _degreesToRadians(sector.startAngle - 90);
      final sweepAngle = _degreesToRadians(sector.endAngle - sector.startAngle);

      Color sectorColor;
      if (showNDVI && sector.ndviValue != null) {
        sectorColor = _ndviToColor(sector.ndviValue!);
      } else {
        sectorColor = _hexToColor(sector.color);
      }

      // Dim disabled sectors
      if (!sector.isEnabled) {
        sectorColor = sectorColor.withOpacity(0.3);
      }

      final sectorPaint = Paint()
        ..color = sectorColor
        ..style = PaintingStyle.fill;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle,
        true,
        sectorPaint,
      );

      // Sector border
      final borderPaint = Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle,
        true,
        borderPaint,
      );

      // Draw sector number
      _drawSectorLabel(canvas, center, radius, sector);
    }
  }

  void _drawDefaultSectors(Canvas canvas, Offset center, double radius) {
    // Draw 8 default sectors
    const sectorCount = 8;
    const sectorAngle = 2 * math.pi / sectorCount;

    for (int i = 0; i < sectorCount; i++) {
      final startAngle = i * sectorAngle - math.pi / 2;

      final color = Colors.green[300 + (i % 3) * 100]!;
      final sectorPaint = Paint()
        ..color = color
        ..style = PaintingStyle.fill;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sectorAngle,
        true,
        sectorPaint,
      );

      // Sector border
      final borderPaint = Paint()
        ..color = Colors.white
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sectorAngle,
        true,
        borderPaint,
      );
    }
  }

  void _drawSectorLabel(Canvas canvas, Offset center, double radius, PivotSector sector) {
    final midAngle = _degreesToRadians((sector.startAngle + sector.endAngle) / 2 - 90);
    final labelRadius = radius * 0.65;

    final labelOffset = Offset(
      center.dx + labelRadius * math.cos(midAngle),
      center.dy + labelRadius * math.sin(midAngle),
    );

    final textPainter = TextPainter(
      text: TextSpan(
        text: '${sector.sectorNumber}',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 14,
          fontWeight: FontWeight.bold,
          shadows: [Shadow(blurRadius: 2, color: Colors.black54)],
        ),
      ),
      textDirection: TextDirection.ltr,
    );

    textPainter.layout();
    textPainter.paint(
      canvas,
      labelOffset - Offset(textPainter.width / 2, textPainter.height / 2),
    );
  }

  void _drawVRIZones(Canvas canvas, Offset center, double radius) {
    for (final zone in config.vriZones) {
      Color zoneColor = _hexToColor(zone.color).withOpacity(0.4);

      // Apply rate multiplier to color intensity
      if (zone.rateMultiplier < 0.5) {
        zoneColor = Colors.red.withOpacity(0.3); // Low application
      } else if (zone.rateMultiplier > 1.2) {
        zoneColor = Colors.blue.withOpacity(0.3); // High application
      }

      if (!zone.isActive) {
        zoneColor = Colors.grey.withOpacity(0.2);
      }

      // Draw VRI zone polygon (simplified as sectors for now)
      final zonePaint = Paint()
        ..color = zoneColor
        ..style = PaintingStyle.fill;

      // For simplicity, draw as overlay circles
      canvas.drawCircle(center, radius * 0.6, zonePaint);
    }
  }

  void _drawCenterTower(Canvas canvas, Offset center) {
    // Outer ring
    final outerPaint = Paint()
      ..color = Colors.grey[700]!
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, 12, outerPaint);

    // Inner dot
    final innerPaint = Paint()
      ..color = Colors.red
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, 6, innerPaint);

    // Highlight
    final highlightPaint = Paint()
      ..color = Colors.white.withOpacity(0.5)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center + const Offset(-2, -2), 2, highlightPaint);
  }

  void _drawSpanTowers(Canvas canvas, Offset center, double radius) {
    if (config.spansCount <= 0) return;

    final currentAngle = animatedAngle ?? _degreesToRadians(armAngle - 90);
    final spanSpacing = radius / (config.spansCount + 1);

    final towerPaint = Paint()
      ..color = Colors.grey[600]!
      ..style = PaintingStyle.fill;

    for (int i = 1; i <= config.spansCount; i++) {
      final towerRadius = spanSpacing * i;
      final towerOffset = Offset(
        center.dx + towerRadius * math.cos(currentAngle),
        center.dy + towerRadius * math.sin(currentAngle),
      );

      // Tower wheel
      canvas.drawCircle(towerOffset, 4, towerPaint);

      // Tower number
      if (i == config.spansCount) {
        final textPainter = TextPainter(
          text: TextSpan(
            text: 'T$i',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 8,
              fontWeight: FontWeight.bold,
            ),
          ),
          textDirection: TextDirection.ltr,
        );
        textPainter.layout();
        textPainter.paint(
          canvas,
          towerOffset + const Offset(-8, 8),
        );
      }
    }
  }

  void _drawPivotArm(Canvas canvas, Offset center, double radius) {
    final currentAngle = animatedAngle ?? _degreesToRadians(armAngle - 90);

    // Calculate arm end point
    final armEnd = Offset(
      center.dx + radius * math.cos(currentAngle),
      center.dy + radius * math.sin(currentAngle),
    );

    // Draw water spray effect
    _drawWaterSpray(canvas, center, armEnd, radius, currentAngle);

    // Draw arm shadow
    final shadowPaint = Paint()
      ..color = Colors.black.withOpacity(0.2)
      ..strokeWidth = 8
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(
      center + const Offset(2, 2),
      armEnd + const Offset(2, 2),
      shadowPaint,
    );

    // Draw main arm
    final armPaint = Paint()
      ..color = Colors.grey[800]!
      ..strokeWidth = 6
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(center, armEnd, armPaint);

    // Draw arm highlight
    final highlightPaint = Paint()
      ..color = Colors.grey[400]!
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;
    final highlightEnd = Offset(
      center.dx + (radius - 10) * math.cos(currentAngle),
      center.dy + (radius - 10) * math.sin(currentAngle),
    );
    canvas.drawLine(center, highlightEnd, highlightPaint);

    // Draw end gun if enabled
    if (config.hasEndGun && status?.endGunActive == true) {
      _drawEndGun(canvas, armEnd, currentAngle);
    }
  }

  void _drawWaterSpray(Canvas canvas, Offset center, Offset armEnd, double radius, double angle) {
    if (status?.isIrrigating != true) return;

    final sprayPaint = Paint()
      ..color = Colors.blue.withOpacity(0.15)
      ..style = PaintingStyle.fill;

    // Draw water spray arc behind the arm
    final sprayAngle = _degreesToRadians(15);
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      angle - sprayAngle,
      sprayAngle * 2,
      true,
      sprayPaint,
    );
  }

  void _drawEndGun(Canvas canvas, Offset armEnd, double angle) {
    final gunPaint = Paint()
      ..color = Colors.blue.withOpacity(0.3)
      ..style = PaintingStyle.fill;

    // End gun spray arc
    final gunRadius = config.overhangMeters > 0 ? 30.0 : 20.0;
    canvas.drawArc(
      Rect.fromCircle(center: armEnd, radius: gunRadius),
      angle - math.pi / 4,
      math.pi / 2,
      true,
      gunPaint,
    );
  }

  void _drawDirectionIndicators(Canvas canvas, Offset center, double radius) {
    // Draw N/S/E/W indicators
    final directions = ['N', 'E', 'S', 'W'];
    final angles = [-math.pi / 2, 0, math.pi / 2, math.pi];

    for (int i = 0; i < 4; i++) {
      final labelOffset = Offset(
        center.dx + (radius + 15) * math.cos(angles[i]),
        center.dy + (radius + 15) * math.sin(angles[i]),
      );

      final textPainter = TextPainter(
        text: TextSpan(
          text: directions[i],
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
        textDirection: TextDirection.ltr,
      );

      textPainter.layout();
      textPainter.paint(
        canvas,
        labelOffset - Offset(textPainter.width / 2, textPainter.height / 2),
      );
    }
  }

  void _drawScaleRing(Canvas canvas, Offset center, double radius) {
    // Draw degree markers every 30°
    final markerPaint = Paint()
      ..color = Colors.grey[400]!
      ..strokeWidth = 1;

    for (int deg = 0; deg < 360; deg += 30) {
      final angle = _degreesToRadians(deg - 90);
      final start = Offset(
        center.dx + (radius - 5) * math.cos(angle),
        center.dy + (radius - 5) * math.sin(angle),
      );
      final end = Offset(
        center.dx + radius * math.cos(angle),
        center.dy + radius * math.sin(angle),
      );
      canvas.drawLine(start, end, markerPaint);
    }
  }

  double _degreesToRadians(double degrees) => degrees * math.pi / 180;

  Color _hexToColor(String hex) {
    hex = hex.replaceFirst('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    return Color(int.parse(hex, radix: 16));
  }

  Color _ndviToColor(double ndvi) {
    // NDVI color scale: red (0) -> yellow (0.3) -> green (0.6) -> dark green (1)
    if (ndvi < 0.2) return Colors.red[400]!;
    if (ndvi < 0.35) return Colors.orange[400]!;
    if (ndvi < 0.5) return Colors.yellow[600]!;
    if (ndvi < 0.65) return Colors.lightGreen[400]!;
    if (ndvi < 0.8) return Colors.green[500]!;
    return Colors.green[800]!;
  }

  @override
  bool shouldRepaint(covariant _PivotPainter oldDelegate) {
    return oldDelegate.armAngle != armAngle ||
        oldDelegate.animatedAngle != animatedAngle ||
        oldDelegate.status?.operatingStatus != status?.operatingStatus;
  }
}

/// Compact pivot status indicator widget
/// مؤشر حالة المحوري المصغر
class PivotStatusIndicator extends StatelessWidget {
  final PivotStatus status;
  final double size;

  const PivotStatusIndicator({
    super.key,
    required this.status,
    this.size = 60,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Progress ring
          SizedBox(
            width: size,
            height: size,
            child: CircularProgressIndicator(
              value: status.progressPercent / 100,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(
                _statusColor(status.operatingStatus),
              ),
              strokeWidth: 4,
            ),
          ),

          // Status icon
          Icon(
            _statusIcon(status.operatingStatus),
            color: _statusColor(status.operatingStatus),
            size: size * 0.5,
          ),
        ],
      ),
    );
  }

  IconData _statusIcon(PivotOperatingStatus status) {
    switch (status) {
      case PivotOperatingStatus.running:
        return Icons.play_circle_filled;
      case PivotOperatingStatus.paused:
        return Icons.pause_circle_filled;
      case PivotOperatingStatus.stopped:
        return Icons.stop_circle;
      case PivotOperatingStatus.fault:
        return Icons.error;
      case PivotOperatingStatus.maintenance:
        return Icons.build_circle;
      case PivotOperatingStatus.scheduled:
        return Icons.schedule;
    }
  }

  Color _statusColor(PivotOperatingStatus status) {
    switch (status) {
      case PivotOperatingStatus.running:
        return Colors.green;
      case PivotOperatingStatus.paused:
        return Colors.orange;
      case PivotOperatingStatus.stopped:
        return Colors.grey;
      case PivotOperatingStatus.fault:
        return Colors.red;
      case PivotOperatingStatus.maintenance:
        return Colors.blue;
      case PivotOperatingStatus.scheduled:
        return Colors.purple;
    }
  }
}
