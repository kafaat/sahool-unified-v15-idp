import 'dart:ui';
import 'package:flutter/material.dart';

/// Modern Theme System for SAHOOL
/// نظام ثيم حديث مع تأثيرات متقدمة
///
/// Features:
/// - Glassmorphism effects
/// - Gradient systems
/// - Modern animations
/// - Soft shadows
/// - Glowing effects

// ═════════════════════════════════════════════════════════════════════════════
// MODERN COLOR SYSTEM
// ═════════════════════════════════════════════════════════════════════════════

class ModernColors {
  // ─────────────────────────────────────────────────────────────────────────
  // Primary Palette - مجموعة الألوان الأساسية
  // ─────────────────────────────────────────────────────────────────────────

  static const Color primaryGreen = Color(0xFF1B5E20);
  static const Color primaryGreen50 = Color(0xFFE8F5E9);
  static const Color primaryGreen100 = Color(0xFFC8E6C9);
  static const Color primaryGreen200 = Color(0xFFA5D6A7);
  static const Color primaryGreen300 = Color(0xFF81C784);
  static const Color primaryGreen400 = Color(0xFF66BB6A);
  static const Color primaryGreen500 = Color(0xFF4CAF50);
  static const Color primaryGreen600 = Color(0xFF43A047);
  static const Color primaryGreen700 = Color(0xFF388E3C);
  static const Color primaryGreen800 = Color(0xFF2E7D32);
  static const Color primaryGreen900 = Color(0xFF1B5E20);

  // ─────────────────────────────────────────────────────────────────────────
  // Glassmorphism Colors - ألوان التأثير الزجاجي
  // ─────────────────────────────────────────────────────────────────────────

  static const Color glassLight = Color(0xFFFFFFFF);
  static const Color glassDark = Color(0xFF000000);
  static const Color glassGreen = Color(0xFF4CAF50);
  static const Color glassBlue = Color(0xFF2196F3);
  static const Color glassPurple = Color(0xFF9C27B0);
  static const Color glassOrange = Color(0xFFFF9800);

  // ─────────────────────────────────────────────────────────────────────────
  // Gradient Colors - ألوان التدرجات
  // ─────────────────────────────────────────────────────────────────────────

  static const List<Color> emeraldGradient = [
    Color(0xFF1B5E20),
    Color(0xFF4CAF50),
  ];

  static const List<Color> sunsetGradient = [
    Color(0xFFFF6B6B),
    Color(0xFFFFD93D),
  ];

  static const List<Color> oceanGradient = [
    Color(0xFF2196F3),
    Color(0xFF00BCD4),
  ];

  static const List<Color> forestGradient = [
    Color(0xFF1B5E20),
    Color(0xFF388E3C),
    Color(0xFF66BB6A),
  ];

  static const List<Color> twilightGradient = [
    Color(0xFF667EEA),
    Color(0xFF764BA2),
  ];

  static const List<Color> autumnGradient = [
    Color(0xFFD4A84B),
    Color(0xFF8B7355),
  ];

  // ─────────────────────────────────────────────────────────────────────────
  // Glow Colors - ألوان التوهج
  // ─────────────────────────────────────────────────────────────────────────

  static const Color glowGreen = Color(0xFF4CAF50);
  static const Color glowBlue = Color(0xFF2196F3);
  static const Color glowPurple = Color(0xFF9C27B0);
  static const Color glowOrange = Color(0xFFFF9800);
  static const Color glowPink = Color(0xFFE91E63);
  static const Color glowCyan = Color(0xFF00BCD4);

  // ─────────────────────────────────────────────────────────────────────────
  // Semantic Colors - ألوان المعاني
  // ─────────────────────────────────────────────────────────────────────────

  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFF9800);
  static const Color error = Color(0xFFF44336);
  static const Color info = Color(0xFF2196F3);

  // Surfaces
  static const Color surfaceLight = Color(0xFFFFFFFF);
  static const Color surfaceDark = Color(0xFF1A1A1A);
  static const Color surfaceElevated = Color(0xFFF5F7FA);

  // Overlays
  static const Color overlayLight = Color(0x0A000000);
  static const Color overlayMedium = Color(0x14000000);
  static const Color overlayHeavy = Color(0x29000000);
}

// ═════════════════════════════════════════════════════════════════════════════
// MODERN TYPOGRAPHY SYSTEM
// ═════════════════════════════════════════════════════════════════════════════

class ModernTypography {
  static const String fontFamily = 'IBMPlexSansArabic';

  // ─────────────────────────────────────────────────────────────────────────
  // Display Styles - أنماط العناوين الكبيرة
  // ─────────────────────────────────────────────────────────────────────────

  static const TextStyle displayLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 57,
    fontWeight: FontWeight.bold,
    letterSpacing: -0.25,
    height: 1.12,
  );

  static const TextStyle displayMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 45,
    fontWeight: FontWeight.bold,
    letterSpacing: 0,
    height: 1.16,
  );

  static const TextStyle displaySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 36,
    fontWeight: FontWeight.bold,
    letterSpacing: 0,
    height: 1.22,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Headline Styles - أنماط العناوين
  // ─────────────────────────────────────────────────────────────────────────

  static const TextStyle headlineLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 32,
    fontWeight: FontWeight.bold,
    letterSpacing: 0,
    height: 1.25,
  );

  static const TextStyle headlineMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 28,
    fontWeight: FontWeight.bold,
    letterSpacing: 0,
    height: 1.29,
  );

  static const TextStyle headlineSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 24,
    fontWeight: FontWeight.bold,
    letterSpacing: 0,
    height: 1.33,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Title Styles - أنماط العناوين الفرعية
  // ─────────────────────────────────────────────────────────────────────────

  static const TextStyle titleLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 22,
    fontWeight: FontWeight.w600,
    letterSpacing: 0,
    height: 1.27,
  );

  static const TextStyle titleMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.15,
    height: 1.5,
  );

  static const TextStyle titleSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.1,
    height: 1.43,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Body Styles - أنماط النصوص
  // ─────────────────────────────────────────────────────────────────────────

  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16,
    fontWeight: FontWeight.normal,
    letterSpacing: 0.5,
    height: 1.5,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.normal,
    letterSpacing: 0.25,
    height: 1.43,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.normal,
    letterSpacing: 0.4,
    height: 1.33,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Label Styles - أنماط التسميات
  // ─────────────────────────────────────────────────────────────────────────

  static const TextStyle labelLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 14,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.1,
    height: 1.43,
  );

  static const TextStyle labelMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.5,
    height: 1.33,
  );

  static const TextStyle labelSmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.5,
    height: 1.45,
  );
}

// ═════════════════════════════════════════════════════════════════════════════
// MODERN SHADOW SYSTEM
// ═════════════════════════════════════════════════════════════════════════════

class ModernShadows {
  // ─────────────────────────────────────────────────────────────────────────
  // Soft Shadows - ظلال ناعمة
  // ─────────────────────────────────────────────────────────────────────────

  static List<BoxShadow> get soft1 => [
    BoxShadow(
      color: Colors.black.withOpacity(0.04),
      blurRadius: 4,
      offset: const Offset(0, 1),
    ),
  ];

  static List<BoxShadow> get soft2 => [
    BoxShadow(
      color: Colors.black.withOpacity(0.06),
      blurRadius: 8,
      offset: const Offset(0, 2),
    ),
  ];

  static List<BoxShadow> get soft3 => [
    BoxShadow(
      color: Colors.black.withOpacity(0.08),
      blurRadius: 16,
      offset: const Offset(0, 4),
    ),
  ];

  static List<BoxShadow> get soft4 => [
    BoxShadow(
      color: Colors.black.withOpacity(0.1),
      blurRadius: 24,
      offset: const Offset(0, 8),
    ),
  ];

  // ─────────────────────────────────────────────────────────────────────────
  // Layered Shadows - ظلال متعددة الطبقات
  // ─────────────────────────────────────────────────────────────────────────

  static List<BoxShadow> get layered1 => [
    BoxShadow(
      color: Colors.black.withOpacity(0.04),
      blurRadius: 2,
      offset: const Offset(0, 1),
    ),
    BoxShadow(
      color: Colors.black.withOpacity(0.04),
      blurRadius: 8,
      offset: const Offset(0, 2),
    ),
  ];

  static List<BoxShadow> get layered2 => [
    BoxShadow(
      color: Colors.black.withOpacity(0.05),
      blurRadius: 4,
      offset: const Offset(0, 2),
    ),
    BoxShadow(
      color: Colors.black.withOpacity(0.05),
      blurRadius: 16,
      offset: const Offset(0, 4),
    ),
  ];

  static List<BoxShadow> get layered3 => [
    BoxShadow(
      color: Colors.black.withOpacity(0.06),
      blurRadius: 8,
      offset: const Offset(0, 4),
    ),
    BoxShadow(
      color: Colors.black.withOpacity(0.06),
      blurRadius: 24,
      offset: const Offset(0, 8),
    ),
  ];

  // ─────────────────────────────────────────────────────────────────────────
  // Colored Shadows - ظلال ملونة
  // ─────────────────────────────────────────────────────────────────────────

  static List<BoxShadow> coloredShadow(Color color, {double intensity = 0.3}) => [
    BoxShadow(
      color: color.withOpacity(intensity),
      blurRadius: 20,
      offset: const Offset(0, 8),
    ),
  ];

  static List<BoxShadow> get greenGlow => [
    BoxShadow(
      color: ModernColors.glowGreen.withOpacity(0.3),
      blurRadius: 20,
      offset: const Offset(0, 8),
    ),
    BoxShadow(
      color: ModernColors.glowGreen.withOpacity(0.15),
      blurRadius: 40,
      offset: const Offset(0, 12),
    ),
  ];

  static List<BoxShadow> get blueGlow => [
    BoxShadow(
      color: ModernColors.glowBlue.withOpacity(0.3),
      blurRadius: 20,
      offset: const Offset(0, 8),
    ),
    BoxShadow(
      color: ModernColors.glowBlue.withOpacity(0.15),
      blurRadius: 40,
      offset: const Offset(0, 12),
    ),
  ];

  // ─────────────────────────────────────────────────────────────────────────
  // Inner Shadows - ظلال داخلية (محاكاة)
  // ─────────────────────────────────────────────────────────────────────────

  static List<BoxShadow> get innerShadow => [
    BoxShadow(
      color: Colors.black.withOpacity(0.1),
      blurRadius: 4,
      offset: const Offset(0, 2),
    ),
  ];
}

// ═════════════════════════════════════════════════════════════════════════════
// MODERN ANIMATION CURVES
// ═════════════════════════════════════════════════════════════════════════════

class ModernCurves {
  // ─────────────────────────────────────────────────────────────────────────
  // Spring Curves - منحنيات مرنة
  // ─────────────────────────────────────────────────────────────────────────

  static const Curve spring = Curves.easeOutBack;
  static const Curve springIn = Curves.easeInBack;
  static const Curve springOut = Curves.easeOutBack;
  static const Curve springInOut = Curves.easeInOutBack;

  // ─────────────────────────────────────────────────────────────────────────
  // Smooth Curves - منحنيات ناعمة
  // ─────────────────────────────────────────────────────────────────────────

  static const Curve smooth = Curves.easeInOutCubic;
  static const Curve smoothIn = Curves.easeInCubic;
  static const Curve smoothOut = Curves.easeOutCubic;

  // ─────────────────────────────────────────────────────────────────────────
  // Quick Curves - منحنيات سريعة
  // ─────────────────────────────────────────────────────────────────────────

  static const Curve quick = Curves.easeInOutQuad;
  static const Curve quickIn = Curves.easeInQuad;
  static const Curve quickOut = Curves.easeOutQuad;

  // ─────────────────────────────────────────────────────────────────────────
  // Elastic Curves - منحنيات مطاطية
  // ─────────────────────────────────────────────────────────────────────────

  static const Curve elastic = Curves.elasticOut;
  static const Curve elasticIn = Curves.elasticIn;
  static const Curve elasticOut = Curves.elasticOut;
  static const Curve elasticInOut = Curves.elasticInOut;

  // ─────────────────────────────────────────────────────────────────────────
  // Bounce Curves - منحنيات ارتدادية
  // ─────────────────────────────────────────────────────────────────────────

  static const Curve bounce = Curves.bounceOut;
  static const Curve bounceIn = Curves.bounceIn;
  static const Curve bounceOut = Curves.bounceOut;
  static const Curve bounceInOut = Curves.bounceInOut;
}

// ═════════════════════════════════════════════════════════════════════════════
// MODERN DURATION SYSTEM
// ═════════════════════════════════════════════════════════════════════════════

class ModernDurations {
  static const Duration instant = Duration(milliseconds: 100);
  static const Duration fast = Duration(milliseconds: 200);
  static const Duration normal = Duration(milliseconds: 300);
  static const Duration slow = Duration(milliseconds: 500);
  static const Duration verySlow = Duration(milliseconds: 800);
}

// ═════════════════════════════════════════════════════════════════════════════
// GLASS CONTAINER - Modern Glassmorphism Widget
// ═════════════════════════════════════════════════════════════════════════════

class GlassContainer extends StatelessWidget {
  final Widget child;
  final double borderRadius;
  final double blur;
  final Color color;
  final double opacity;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final double? width;
  final double? height;
  final Border? border;
  final List<BoxShadow>? boxShadow;
  final Gradient? gradient;

  const GlassContainer({
    super.key,
    required this.child,
    this.borderRadius = 16,
    this.blur = 10,
    this.color = Colors.white,
    this.opacity = 0.15,
    this.padding,
    this.margin,
    this.width,
    this.height,
    this.border,
    this.boxShadow,
    this.gradient,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      width: width,
      height: height,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(borderRadius),
        boxShadow: boxShadow ?? ModernShadows.soft2,
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(borderRadius),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: blur, sigmaY: blur),
          child: Container(
            padding: padding ?? const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withOpacity(opacity),
              gradient: gradient,
              border: border ?? Border.all(
                color: Colors.white.withOpacity(0.2),
                width: 1.5,
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

// ═════════════════════════════════════════════════════════════════════════════
// GRADIENT BUTTON - Modern Gradient Button Widget
// ═════════════════════════════════════════════════════════════════════════════

class GradientButton extends StatefulWidget {
  final String text;
  final VoidCallback? onPressed;
  final List<Color> gradient;
  final double borderRadius;
  final EdgeInsets padding;
  final TextStyle? textStyle;
  final Widget? icon;
  final bool loading;
  final double? width;
  final double? height;
  final List<BoxShadow>? boxShadow;

  const GradientButton({
    super.key,
    required this.text,
    this.onPressed,
    this.gradient = ModernColors.emeraldGradient,
    this.borderRadius = 12,
    this.padding = const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
    this.textStyle,
    this.icon,
    this.loading = false,
    this.width,
    this.height,
    this.boxShadow,
  });

  @override
  State<GradientButton> createState() => _GradientButtonState();
}

class _GradientButtonState extends State<GradientButton>
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
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.95).animate(
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
      onTap: widget.onPressed != null && !widget.loading ? widget.onPressed : null,
      child: ScaleTransition(
        scale: _scaleAnimation,
        child: Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: widget.gradient,
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(widget.borderRadius),
            boxShadow: widget.boxShadow ?? ModernShadows.coloredShadow(widget.gradient.first),
          ),
          child: Material(
            color: Colors.transparent,
            child: Container(
              padding: widget.padding,
              child: widget.loading
                  ? const Center(
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                        ),
                      ),
                    )
                  : Row(
                      mainAxisSize: MainAxisSize.min,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if (widget.icon != null) ...[
                          widget.icon!,
                          const SizedBox(width: 8),
                        ],
                        Text(
                          widget.text,
                          style: widget.textStyle ??
                              ModernTypography.labelLarge.copyWith(
                                color: Colors.white,
                              ),
                        ),
                      ],
                    ),
            ),
          ),
        ),
      ),
    );
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// ANIMATED CARD - Modern Animated Card Widget
// ═════════════════════════════════════════════════════════════════════════════

class AnimatedCard extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final double borderRadius;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final Color? color;
  final List<BoxShadow>? boxShadow;
  final Border? border;
  final Gradient? gradient;

  const AnimatedCard({
    super.key,
    required this.child,
    this.onTap,
    this.borderRadius = 16,
    this.padding,
    this.margin,
    this.color,
    this.boxShadow,
    this.border,
    this.gradient,
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
      duration: ModernDurations.fast,
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.98).animate(
      CurvedAnimation(parent: _controller, curve: ModernCurves.quick),
    );
    _elevationAnimation = Tween<double>(begin: 1.0, end: 1.5).animate(
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
      onTapDown: widget.onTap != null ? _handleTapDown : null,
      onTapUp: widget.onTap != null ? _handleTapUp : null,
      onTapCancel: widget.onTap != null ? _handleTapCancel : null,
      onTap: widget.onTap,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          final baseShadow = widget.boxShadow ?? ModernShadows.soft3;
          final animatedShadow = baseShadow.map((shadow) {
            return BoxShadow(
              color: shadow.color,
              blurRadius: shadow.blurRadius * _elevationAnimation.value,
              offset: shadow.offset * _elevationAnimation.value,
              spreadRadius: shadow.spreadRadius,
            );
          }).toList();

          return Transform.scale(
            scale: _scaleAnimation.value,
            child: Container(
              margin: widget.margin,
              decoration: BoxDecoration(
                color: widget.color ?? Colors.white,
                gradient: widget.gradient,
                borderRadius: BorderRadius.circular(widget.borderRadius),
                border: widget.border,
                boxShadow: animatedShadow,
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(widget.borderRadius),
                child: Container(
                  padding: widget.padding ?? const EdgeInsets.all(16),
                  child: widget.child,
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// SHIMMER LOADING - Modern Shimmer Effect Widget
// ═════════════════════════════════════════════════════════════════════════════

class ShimmerLoading extends StatefulWidget {
  final double width;
  final double height;
  final double borderRadius;
  final Color baseColor;
  final Color highlightColor;

  const ShimmerLoading({
    super.key,
    required this.width,
    required this.height,
    this.borderRadius = 8,
    this.baseColor = const Color(0xFFE0E0E0),
    this.highlightColor = const Color(0xFFF5F5F5),
  });

  @override
  State<ShimmerLoading> createState() => _ShimmerLoadingState();
}

class _ShimmerLoadingState extends State<ShimmerLoading>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();
    _animation = Tween<double>(begin: -2, end: 2).animate(
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
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(widget.borderRadius),
            gradient: LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [
                widget.baseColor,
                widget.highlightColor,
                widget.baseColor,
              ],
              stops: [
                0.0,
                0.5,
                1.0,
              ],
              transform: _SlideGradientTransform(_animation.value),
            ),
          ),
        );
      },
    );
  }
}

class _SlideGradientTransform extends GradientTransform {
  final double slidePercent;

  const _SlideGradientTransform(this.slidePercent);

  @override
  Matrix4? transform(Rect bounds, {TextDirection? textDirection}) {
    return Matrix4.translationValues(bounds.width * slidePercent, 0.0, 0.0);
  }
}

// Helper widget for common shimmer layouts
class ShimmerBox extends StatelessWidget {
  final double? width;
  final double height;
  final double borderRadius;

  const ShimmerBox({
    super.key,
    this.width,
    this.height = 20,
    this.borderRadius = 8,
  });

  @override
  Widget build(BuildContext context) {
    return ShimmerLoading(
      width: width ?? double.infinity,
      height: height,
      borderRadius: borderRadius,
    );
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// MODERN TEXT FIELD - Modern Input Field Widget
// ═════════════════════════════════════════════════════════════════════════════

class ModernTextField extends StatefulWidget {
  final TextEditingController? controller;
  final String? labelText;
  final String? hintText;
  final String? helperText;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final bool obscureText;
  final TextInputType? keyboardType;
  final String? Function(String?)? validator;
  final void Function(String)? onChanged;
  final void Function(String)? onSubmitted;
  final bool enabled;
  final int? maxLines;
  final int? maxLength;
  final FocusNode? focusNode;
  final bool autofocus;
  final Color? fillColor;
  final double borderRadius;
  final EdgeInsets? contentPadding;

  const ModernTextField({
    super.key,
    this.controller,
    this.labelText,
    this.hintText,
    this.helperText,
    this.prefixIcon,
    this.suffixIcon,
    this.obscureText = false,
    this.keyboardType,
    this.validator,
    this.onChanged,
    this.onSubmitted,
    this.enabled = true,
    this.maxLines = 1,
    this.maxLength,
    this.focusNode,
    this.autofocus = false,
    this.fillColor,
    this.borderRadius = 12,
    this.contentPadding,
  });

  @override
  State<ModernTextField> createState() => _ModernTextFieldState();
}

class _ModernTextFieldState extends State<ModernTextField>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _focusAnimation;
  late FocusNode _internalFocusNode;
  bool _isFocused = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: ModernDurations.fast,
      vsync: this,
    );
    _focusAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: ModernCurves.smooth),
    );
    _internalFocusNode = widget.focusNode ?? FocusNode();
    _internalFocusNode.addListener(_handleFocusChange);
  }

  @override
  void dispose() {
    _controller.dispose();
    if (widget.focusNode == null) {
      _internalFocusNode.dispose();
    }
    super.dispose();
  }

  void _handleFocusChange() {
    setState(() {
      _isFocused = _internalFocusNode.hasFocus;
    });
    if (_isFocused) {
      _controller.forward();
    } else {
      _controller.reverse();
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _focusAnimation,
      builder: (context, child) {
        return Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(widget.borderRadius),
            boxShadow: _isFocused
                ? ModernShadows.coloredShadow(
                    ModernColors.primaryGreen,
                    intensity: 0.15,
                  )
                : ModernShadows.soft1,
          ),
          child: TextFormField(
            controller: widget.controller,
            focusNode: _internalFocusNode,
            autofocus: widget.autofocus,
            obscureText: widget.obscureText,
            keyboardType: widget.keyboardType,
            validator: widget.validator,
            onChanged: widget.onChanged,
            onFieldSubmitted: widget.onSubmitted,
            enabled: widget.enabled,
            maxLines: widget.maxLines,
            maxLength: widget.maxLength,
            style: ModernTypography.bodyLarge,
            decoration: InputDecoration(
              labelText: widget.labelText,
              hintText: widget.hintText,
              helperText: widget.helperText,
              prefixIcon: widget.prefixIcon,
              suffixIcon: widget.suffixIcon,
              filled: true,
              fillColor: widget.fillColor ?? Colors.grey[50],
              contentPadding: widget.contentPadding ??
                  const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(widget.borderRadius),
                borderSide: BorderSide.none,
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(widget.borderRadius),
                borderSide: BorderSide(
                  color: Colors.grey[300]!,
                  width: 1.5,
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(widget.borderRadius),
                borderSide: BorderSide(
                  color: ModernColors.primaryGreen,
                  width: 2,
                ),
              ),
              errorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(widget.borderRadius),
                borderSide: const BorderSide(
                  color: ModernColors.error,
                  width: 1.5,
                ),
              ),
              focusedErrorBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(widget.borderRadius),
                borderSide: const BorderSide(
                  color: ModernColors.error,
                  width: 2,
                ),
              ),
              labelStyle: ModernTypography.bodyMedium.copyWith(
                color: _isFocused
                    ? ModernColors.primaryGreen
                    : Colors.grey[600],
              ),
              hintStyle: ModernTypography.bodyMedium.copyWith(
                color: Colors.grey[400],
              ),
            ),
          ),
        );
      },
    );
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// GRADIENT PRESETS - Ready-to-use Gradients
// ═════════════════════════════════════════════════════════════════════════════

class ModernGradients {
  static LinearGradient emerald = const LinearGradient(
    colors: ModernColors.emeraldGradient,
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static LinearGradient sunset = const LinearGradient(
    colors: ModernColors.sunsetGradient,
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static LinearGradient ocean = const LinearGradient(
    colors: ModernColors.oceanGradient,
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static LinearGradient forest = const LinearGradient(
    colors: ModernColors.forestGradient,
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static LinearGradient twilight = const LinearGradient(
    colors: ModernColors.twilightGradient,
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static LinearGradient autumn = const LinearGradient(
    colors: ModernColors.autumnGradient,
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  // Gradient with custom angle
  static LinearGradient custom(List<Color> colors, {AlignmentGeometry? begin, AlignmentGeometry? end}) {
    return LinearGradient(
      colors: colors,
      begin: begin ?? Alignment.topLeft,
      end: end ?? Alignment.bottomRight,
    );
  }

  // Radial gradient
  static RadialGradient radial(List<Color> colors) {
    return RadialGradient(
      colors: colors,
      center: Alignment.center,
      radius: 1.0,
    );
  }
}
