import 'dart:ui';
import 'package:flutter/material.dart';

/// SahoolGlass - Glassmorphism Widget
/// تأثير زجاجي أنيق للواجهات العائمة
class SahoolGlass extends StatelessWidget {
  final Widget child;
  final double opacity;
  final EdgeInsets padding;
  final double borderRadius;
  final double blurSigma;
  final Color? backgroundColor;
  final Color? borderColor;

  const SahoolGlass({
    super.key,
    required this.child,
    this.opacity = 0.85,
    this.padding = const EdgeInsets.all(12),
    this.borderRadius = 20,
    this.blurSigma = 10,
    this.backgroundColor,
    this.borderColor,
  });

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: blurSigma, sigmaY: blurSigma),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            color: (backgroundColor ?? Colors.white).withOpacity(opacity),
            border: Border.all(
              color: borderColor ?? Colors.white.withOpacity(0.3),
            ),
            borderRadius: BorderRadius.circular(borderRadius),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 15,
                spreadRadius: 2,
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}

/// SahoolGlassCard - بطاقة زجاجية مع عنوان
class SahoolGlassCard extends StatelessWidget {
  final String? title;
  final Widget child;
  final EdgeInsets padding;
  final VoidCallback? onTap;

  const SahoolGlassCard({
    super.key,
    this.title,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: SahoolGlass(
        padding: padding,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (title != null) ...[
              Text(
                title!,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 12),
            ],
            child,
          ],
        ),
      ),
    );
  }
}

/// SahoolGlassButton - زر زجاجي
class SahoolGlassButton extends StatelessWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final Color? color;
  final double size;

  const SahoolGlassButton({
    super.key,
    required this.child,
    this.onPressed,
    this.color,
    this.size = 48,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onPressed,
      child: SahoolGlass(
        padding: EdgeInsets.zero,
        borderRadius: size / 2,
        backgroundColor: color,
        child: SizedBox(
          width: size,
          height: size,
          child: Center(child: child),
        ),
      ),
    );
  }
}
