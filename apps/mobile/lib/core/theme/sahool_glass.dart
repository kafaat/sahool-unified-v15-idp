import 'dart:ui';
import 'package:flutter/material.dart';
import 'modern_theme.dart';
import 'sahool_theme.dart';

/// SahoolGlass - Enhanced Glassmorphism Widget System
/// تأثير زجاجي أنيق للواجهات العائمة مع تحسينات حديثة
///
/// Features:
/// - Advanced blur effects
/// - Gradient overlays
/// - Colored glass effects
/// - Smooth animations
class SahoolGlass extends StatelessWidget {
  final Widget child;
  final double opacity;
  final EdgeInsets padding;
  final EdgeInsets? margin;
  final double borderRadius;
  final double blurSigma;
  final Color? backgroundColor;
  final Color? borderColor;
  final double borderWidth;
  final List<BoxShadow>? boxShadow;
  final Gradient? gradient;
  final double? width;
  final double? height;

  const SahoolGlass({
    super.key,
    required this.child,
    this.opacity = 0.15,
    this.padding = const EdgeInsets.all(16),
    this.margin,
    this.borderRadius = 20,
    this.blurSigma = 10,
    this.backgroundColor,
    this.borderColor,
    this.borderWidth = 1.5,
    this.boxShadow,
    this.gradient,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      width: width,
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(borderRadius),
        boxShadow: boxShadow ?? ModernShadows.soft3,
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blurSigma, sigmaY: blurSigma),
          child: Container(
            padding: padding,
            decoration: BoxDecoration(
              color: (backgroundColor ?? Colors.white).withOpacity(opacity),
              gradient: gradient,
              border: Border.all(
                color: borderColor ?? Colors.white.withOpacity(0.2),
                width: borderWidth,
              ),
              borderRadius: BorderRadius.circular(borderRadius),
            ),
            child: child,
          ),
        ),
      ),
    );
  }
}

/// SahoolGlassVariant - Predefined glass styles
enum SahoolGlassVariant {
  light,
  dark,
  green,
  blue,
  purple,
  gradient,
}

/// SahoolGlassModern - Modern Glass with Variants
class SahoolGlassModern extends StatelessWidget {
  final Widget child;
  final SahoolGlassVariant variant;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final double borderRadius;
  final double? width;
  final double? height;

  const SahoolGlassModern({
    super.key,
    required this.child,
    this.variant = SahoolGlassVariant.light,
    this.padding,
    this.margin,
    this.borderRadius = 20,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    Color backgroundColor;
    Color borderColor;
    Gradient? gradient;
    double opacity;

    switch (variant) {
      case SahoolGlassVariant.light:
        backgroundColor = Colors.white;
        borderColor = Colors.white.withOpacity(0.3);
        opacity = 0.15;
        gradient = null;
        break;
      case SahoolGlassVariant.dark:
        backgroundColor = Colors.black;
        borderColor = Colors.white.withOpacity(0.1);
        opacity = 0.3;
        gradient = null;
        break;
      case SahoolGlassVariant.green:
        backgroundColor = SahoolColors.primary;
        borderColor = SahoolColors.secondary.withOpacity(0.3);
        opacity = 0.2;
        gradient = null;
        break;
      case SahoolGlassVariant.blue:
        backgroundColor = ModernColors.glowBlue;
        borderColor = ModernColors.glowCyan.withOpacity(0.3);
        opacity = 0.2;
        gradient = null;
        break;
      case SahoolGlassVariant.purple:
        backgroundColor = ModernColors.glowPurple;
        borderColor = ModernColors.glowPink.withOpacity(0.3);
        opacity = 0.2;
        gradient = null;
        break;
      case SahoolGlassVariant.gradient:
        backgroundColor = Colors.transparent;
        borderColor = Colors.white.withOpacity(0.3);
        opacity = 1.0;
        gradient = LinearGradient(
          colors: [
            Colors.white.withOpacity(0.2),
            Colors.white.withOpacity(0.1),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
        break;
    }

    return SahoolGlass(
      backgroundColor: backgroundColor,
      borderColor: borderColor,
      opacity: opacity,
      gradient: gradient,
      padding: padding ?? const EdgeInsets.all(16),
      margin: margin,
      borderRadius: borderRadius,
      width: width,
      height: height,
      child: child,
    );
  }
}

/// SahoolGlassCard - بطاقة زجاجية مع عنوان محدثة
class SahoolGlassCard extends StatelessWidget {
  final String? title;
  final String? subtitle;
  final Widget child;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final VoidCallback? onTap;
  final SahoolGlassVariant variant;
  final Widget? leading;
  final Widget? trailing;
  final double borderRadius;

  const SahoolGlassCard({
    super.key,
    this.title,
    this.subtitle,
    required this.child,
    this.padding,
    this.margin,
    this.onTap,
    this.variant = SahoolGlassVariant.light,
    this.leading,
    this.trailing,
    this.borderRadius = 20,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: SahoolGlassModern(
        variant: variant,
        padding: padding ?? const EdgeInsets.all(20),
        margin: margin,
        borderRadius: borderRadius,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (title != null || leading != null || trailing != null) ...[
              Row(
                children: [
                  if (leading != null) ...[
                    leading!,
                    const SizedBox(width: 12),
                  ],
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (title != null)
                          Text(
                            title!,
                            style: ModernTypography.titleMedium.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        if (subtitle != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            subtitle!,
                            style: ModernTypography.bodySmall.copyWith(
                              color: Colors.black.withOpacity(0.6),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                  if (trailing != null) ...[
                    const SizedBox(width: 12),
                    trailing!,
                  ],
                ],
              ),
              const SizedBox(height: 16),
            ],
            child,
          ],
        ),
      ),
    );
  }
}

/// SahoolGlassButton - زر زجاجي محدث مع تأثيرات حركية
class SahoolGlassButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final Color? color;
  final double size;
  final SahoolGlassVariant variant;
  final bool circular;

  const SahoolGlassButton({
    super.key,
    required this.child,
    this.onPressed,
    this.color,
    this.size = 48,
    this.variant = SahoolGlassVariant.light,
    this.circular = true,
  });

  @override
  State<SahoolGlassButton> createState() => _SahoolGlassButtonState();
}

class _SahoolGlassButtonState extends State<SahoolGlassButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: ModernDurations.fast,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.9).animate(
      CurvedAnimation(parent: _controller, curve: ModernCurves.quick),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTapDown(TapDownDetails details) {
    _controller.forward();
  }

  void _handleTapUp(TapUpDetails details) {
    _controller.reverse();
  }

  void _handleTapCancel() {
    _controller.reverse();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: widget.onPressed != null ? _handleTapDown : null,
      onTapUp: widget.onPressed != null ? _handleTapUp : null,
      onTapCancel: widget.onPressed != null ? _handleTapCancel : null,
      onTap: widget.onPressed,
      child: ScaleTransition(
        scale: _scaleAnimation,
        child: SahoolGlassModern(
          variant: widget.variant,
          padding: EdgeInsets.zero,
          borderRadius: widget.circular ? widget.size / 2 : 16,
          width: widget.size,
          height: widget.size,
          child: Center(child: widget.child),
        ),
      ),
    );
  }
}

/// SahoolGlassAppBar - شريط تطبيق زجاجي
class SahoolGlassAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String? title;
  final Widget? leading;
  final List<Widget>? actions;
  final SahoolGlassVariant variant;
  final double height;

  const SahoolGlassAppBar({
    super.key,
    this.title,
    this.leading,
    this.actions,
    this.variant = SahoolGlassVariant.light,
    this.height = 56,
  });

  @override
  Size get preferredSize => Size.fromHeight(height);

  @override
  Widget build(BuildContext context) {
    return SahoolGlassModern(
      variant: variant,
      padding: EdgeInsets.zero,
      borderRadius: 0,
      height: height + MediaQuery.of(context).padding.top,
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            children: [
              if (leading != null)
                leading!
              else
                const SizedBox(width: 40),
              Expanded(
                child: Center(
                  child: title != null
                      ? Text(
                          title!,
                          style: ModernTypography.titleLarge.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        )
                      : const SizedBox.shrink(),
                ),
              ),
              if (actions != null)
                Row(children: actions!)
              else
                const SizedBox(width: 40),
            ],
          ),
        ),
      ),
    );
  }
}

/// SahoolGlassBottomNav - شريط تنقل سفلي زجاجي
class SahoolGlassBottomNav extends StatelessWidget {
  final List<SahoolGlassNavItem> items;
  final int currentIndex;
  final Function(int)? onTap;
  final SahoolGlassVariant variant;

  const SahoolGlassBottomNav({
    super.key,
    required this.items,
    this.currentIndex = 0,
    this.onTap,
    this.variant = SahoolGlassVariant.light,
  });

  @override
  Widget build(BuildContext context) {
    return SahoolGlassModern(
      variant: variant,
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      borderRadius: 0,
      child: SafeArea(
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: List.generate(items.length, (index) {
            final item = items[index];
            final isSelected = index == currentIndex;

            return GestureDetector(
              onTap: () => onTap?.call(index),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: isSelected
                      ? SahoolColors.primary.withOpacity(0.15)
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      item.icon,
                      color: isSelected
                          ? SahoolColors.primary
                          : Colors.grey[600],
                      size: 24,
                    ),
                    if (isSelected && item.label != null) ...[
                      const SizedBox(width: 8),
                      Text(
                        item.label!,
                        style: ModernTypography.labelMedium.copyWith(
                          color: SahoolColors.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            );
          }),
        ),
      ),
    );
  }
}

/// SahoolGlassNavItem - عنصر التنقل
class SahoolGlassNavItem {
  final IconData icon;
  final String? label;

  const SahoolGlassNavItem({
    required this.icon,
    this.label,
  });
}
