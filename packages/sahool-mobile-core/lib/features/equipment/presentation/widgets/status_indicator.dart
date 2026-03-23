/// Status Indicator Widget - مؤشر الحالة
/// Visual status indicators for equipment
library;
import 'package:flutter/material.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/equipment.dart';
import '../../domain/models/equipment_status.dart';

/// Equipment Status Indicator
class StatusIndicator extends StatelessWidget {
  final EquipmentStatus status;
  final double size;
  final bool showLabel;
  final bool animated;

  const StatusIndicator({
    super.key,
    required this.status,
    this.size = 12,
    this.showLabel = false,
    this.animated = false,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getStatusColor();

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        animated && status == EquipmentStatus.inUse
            ? _PulsingDot(color: color, size: size)
            : Container(
                width: size,
                height: size,
                decoration: BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: color.withValues(alpha: 0.4),
                      blurRadius: 4,
                      spreadRadius: 1,
                    ),
                  ],
                ),
              ),
        if (showLabel) ...[
          const SizedBox(width: 8),
          Text(
            status.nameAr,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w600,
              fontSize: size,
            ),
          ),
        ],
      ],
    );
  }

  Color _getStatusColor() {
    switch (status) {
      case EquipmentStatus.operational:
      case EquipmentStatus.standby:
        return SahoolColors.forestGreen;
      case EquipmentStatus.inUse:
        return Colors.blue;
      case EquipmentStatus.maintenance:
        return SahoolColors.harvestGold;
      case EquipmentStatus.inactive:
        return Colors.grey;
      case EquipmentStatus.repair:
        return SahoolColors.danger;
    }
  }
}

/// Pulsing dot for active status
class _PulsingDot extends StatefulWidget {
  final Color color;
  final double size;

  const _PulsingDot({required this.color, required this.size});

  @override
  State<_PulsingDot> createState() => _PulsingDotState();
}

class _PulsingDotState extends State<_PulsingDot>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat(reverse: true);
    _animation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
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
        return Container(
          width: widget.size,
          height: widget.size,
          decoration: BoxDecoration(
            color: widget.color,
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: widget.color.withValues(alpha: _animation.value * 0.6),
                blurRadius: 8 * _animation.value,
                spreadRadius: 2 * _animation.value,
              ),
            ],
          ),
        );
      },
    );
  }
}

/// Health Score Indicator
class HealthScoreIndicator extends StatelessWidget {
  final int score; // 0-100
  final double size;
  final bool showLabel;

  const HealthScoreIndicator({
    super.key,
    required this.score,
    this.size = 60,
    this.showLabel = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getScoreColor();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: Stack(
            fit: StackFit.expand,
            children: [
              CircularProgressIndicator(
                value: score / 100,
                strokeWidth: size / 10,
                backgroundColor: Colors.grey[200],
                valueColor: AlwaysStoppedAnimation<Color>(color),
              ),
              Center(
                child: Text(
                  '$score',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: size / 3,
                    color: color,
                  ),
                ),
              ),
            ],
          ),
        ),
        if (showLabel) ...[
          const SizedBox(height: 8),
          Text(
            _getScoreLabel(),
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.w600,
              fontSize: 12,
            ),
          ),
        ],
      ],
    );
  }

  Color _getScoreColor() {
    if (score >= 80) return SahoolColors.forestGreen;
    if (score >= 60) return SahoolColors.sageGreen;
    if (score >= 40) return SahoolColors.harvestGold;
    if (score >= 20) return Colors.orange;
    return SahoolColors.danger;
  }

  String _getScoreLabel() {
    if (score >= 80) return 'ممتاز';
    if (score >= 60) return 'جيد';
    if (score >= 40) return 'متوسط';
    if (score >= 20) return 'ضعيف';
    return 'حرج';
  }
}

/// Priority Indicator
class PriorityIndicator extends StatelessWidget {
  final MaintenancePriority priority;
  final bool showLabel;
  final bool compact;

  const PriorityIndicator({
    super.key,
    required this.priority,
    this.showLabel = true,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getPriorityColor();

    if (compact) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(4),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(_getPriorityIcon(), color: color, size: 12),
            if (showLabel) ...[
              const SizedBox(width: 4),
              Text(
                priority.nameAr,
                style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold),
              ),
            ],
          ],
        ),
      );
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(_getPriorityIcon(), color: color, size: 16),
          if (showLabel) ...[
            const SizedBox(width: 6),
            Text(
              priority.nameAr,
              style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold),
            ),
          ],
        ],
      ),
    );
  }

  Color _getPriorityColor() {
    switch (priority) {
      case MaintenancePriority.low:
        return Colors.green;
      case MaintenancePriority.medium:
        return SahoolColors.harvestGold;
      case MaintenancePriority.high:
        return Colors.orange;
      case MaintenancePriority.critical:
        return SahoolColors.danger;
    }
  }

  IconData _getPriorityIcon() {
    switch (priority) {
      case MaintenancePriority.low:
        return Icons.keyboard_arrow_down;
      case MaintenancePriority.medium:
        return Icons.remove;
      case MaintenancePriority.high:
        return Icons.keyboard_arrow_up;
      case MaintenancePriority.critical:
        return Icons.priority_high;
    }
  }
}

/// Alert Badge
class AlertBadge extends StatelessWidget {
  final int count;
  final Color? color;
  final double size;

  const AlertBadge({
    super.key,
    required this.count,
    this.color,
    this.size = 20,
  });

  @override
  Widget build(BuildContext context) {
    if (count == 0) return const SizedBox.shrink();

    final badgeColor = color ?? SahoolColors.danger;

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: badgeColor,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: badgeColor.withValues(alpha: 0.4),
            blurRadius: 4,
            spreadRadius: 1,
          ),
        ],
      ),
      child: Center(
        child: Text(
          count > 99 ? '99+' : '$count',
          style: TextStyle(
            color: Colors.white,
            fontSize: size * 0.55,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
