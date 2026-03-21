/// SAHOOL Notification Badge Widget
/// عنصر شارة الإشعارات
///
/// Displays unread count badge with customizable:
/// - Size (regular/small)
/// - Color
/// - Maximum display count
library;

import 'package:flutter/material.dart';

class NotificationBadge extends StatelessWidget {
  final int count;
  final bool small;
  final Color? color;
  final Color? textColor;
  final int maxCount;
  final bool animate;

  const NotificationBadge({
    super.key,
    required this.count,
    this.small = false,
    this.color,
    this.textColor,
    this.maxCount = 99,
    this.animate = true,
  });

  @override
  Widget build(BuildContext context) {
    if (count <= 0) return const SizedBox.shrink();

    final displayCount = count > maxCount ? '$maxCount+' : count.toString();
    final bgColor = color ?? Colors.red;
    final fgColor = textColor ?? Colors.white;

    final badge = Container(
      constraints: BoxConstraints(
        minWidth: small ? 16 : 20,
        minHeight: small ? 16 : 20,
      ),
      padding: EdgeInsets.symmetric(
        horizontal: small ? 4 : 6,
        vertical: small ? 2 : 3,
      ),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(small ? 8 : 10),
      ),
      child: Text(
        displayCount,
        textAlign: TextAlign.center,
        style: TextStyle(
          color: fgColor,
          fontSize: small ? 10 : 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );

    if (animate) {
      return TweenAnimationBuilder<double>(
        tween: Tween<double>(begin: 0.8, end: 1.0),
        duration: const Duration(milliseconds: 300),
        curve: Curves.elasticOut,
        builder: (context, value, child) {
          return Transform.scale(
            scale: value,
            child: child,
          );
        },
        child: badge,
      );
    }

    return badge;
  }
}

/// Notification icon with badge overlay
class NotificationIconWithBadge extends StatelessWidget {
  final int count;
  final IconData icon;
  final double iconSize;
  final Color? iconColor;
  final Color? badgeColor;
  final VoidCallback? onPressed;

  const NotificationIconWithBadge({
    super.key,
    required this.count,
    this.icon = Icons.notifications,
    this.iconSize = 24,
    this.iconColor,
    this.badgeColor,
    this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return IconButton(
      icon: Stack(
        clipBehavior: Clip.none,
        children: [
          Icon(
            icon,
            size: iconSize,
            color: iconColor,
          ),
          if (count > 0)
            Positioned(
              right: -8,
              top: -4,
              child: NotificationBadge(
                count: count,
                small: true,
                color: badgeColor,
              ),
            ),
        ],
      ),
      onPressed: onPressed,
    );
  }
}

/// Dot indicator for unread notifications
class NotificationDot extends StatelessWidget {
  final Color? color;
  final double size;
  final bool animate;

  const NotificationDot({
    super.key,
    this.color,
    this.size = 8,
    this.animate = false,
  });

  @override
  Widget build(BuildContext context) {
    final dotColor = color ?? Colors.red;

    final dot = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: dotColor,
        shape: BoxShape.circle,
      ),
    );

    if (animate) {
      return _AnimatedDot(color: dotColor, size: size);
    }

    return dot;
  }
}

class _AnimatedDot extends StatefulWidget {
  final Color color;
  final double size;

  const _AnimatedDot({
    required this.color,
    required this.size,
  });

  @override
  State<_AnimatedDot> createState() => _AnimatedDotState();
}

class _AnimatedDotState extends State<_AnimatedDot>
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

    _animation = Tween<double>(
      begin: 0.8,
      end: 1.2,
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
      animation: _animation,
      builder: (context, child) {
        return Transform.scale(
          scale: _animation.value,
          child: Container(
            width: widget.size,
            height: widget.size,
            decoration: BoxDecoration(
              color: widget.color,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: widget.color.withOpacity(0.4),
                  blurRadius: widget.size * _animation.value,
                  spreadRadius: widget.size * 0.2 * _animation.value,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

/// Category badge with icon and count
class CategoryNotificationBadge extends StatelessWidget {
  final String label;
  final IconData icon;
  final Color color;
  final int count;
  final VoidCallback? onTap;

  const CategoryNotificationBadge({
    super.key,
    required this.label,
    required this.icon,
    required this.color,
    required this.count,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: color.withOpacity(0.3),
              width: 1,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: color, size: 18),
              const SizedBox(width: 6),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w500,
                  fontSize: 13,
                ),
              ),
              if (count > 0) ...[
                const SizedBox(width: 6),
                NotificationBadge(
                  count: count,
                  small: true,
                  color: color,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
