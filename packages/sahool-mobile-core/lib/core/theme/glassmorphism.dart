import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'glass_colors.dart';

/// SAHOOL Glassmorphism UI System
/// نظام واجهات زجاجية متقدم لسهول
///
/// Provides premium glass-effect widgets with:
/// - BackdropFilter blur effects | تأثيرات ضبابية
/// - Gradient borders | حدود متدرجة
/// - RTL support | دعم العربية
/// - Dark mode optimizations | تحسينات الوضع الداكن

// ═══════════════════════════════════════════════════════════════════════════
// Glass Container - الحاوية الزجاجية الأساسية
// ═══════════════════════════════════════════════════════════════════════════

/// Base glass container with customizable blur and appearance
/// الحاوية الزجاجية الأساسية مع تخصيص كامل
class GlassContainer extends StatelessWidget {
  final Widget child;
  final double blurIntensity;
  final double opacity;
  final double borderRadius;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry? margin;
  final Color? backgroundColor;
  final Color? borderColor;
  final double borderWidth;
  final List<BoxShadow>? shadows;
  final Gradient? gradient;
  final Gradient? borderGradient;
  final double? width;
  final double? height;
  final BoxConstraints? constraints;
  final AlignmentGeometry? alignment;
  final Clip clipBehavior;

  const GlassContainer({
    super.key,
    required this.child,
    this.blurIntensity = 10.0,
    this.opacity = 0.1,
    this.borderRadius = 20.0,
    this.padding = const EdgeInsets.all(16),
    this.margin,
    this.backgroundColor,
    this.borderColor,
    this.borderWidth = 1.0,
    this.shadows,
    this.gradient,
    this.borderGradient,
    this.width,
    this.height,
    this.constraints,
    this.alignment,
    this.clipBehavior = Clip.antiAlias,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final glassColors = GlassColors.of(context);

    final effectiveBgColor = backgroundColor ??
        (isDark ? glassColors.glassDark : glassColors.glassLight);
    final effectiveBorderColor = borderColor ??
        (isDark ? glassColors.borderDark : glassColors.borderLight);

    Widget glass = ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      clipBehavior: clipBehavior,
      child: BackdropFilter(
        filter: ImageFilter.blur(
          sigmaX: blurIntensity,
          sigmaY: blurIntensity,
        ),
        child: Container(
          width: width,
          height: height,
          constraints: constraints,
          alignment: alignment,
          padding: padding,
          decoration: BoxDecoration(
            color: effectiveBgColor.withValues(alpha: opacity),
            gradient: gradient,
            borderRadius: BorderRadius.circular(borderRadius),
            border: borderGradient != null
                ? null
                : Border.all(
                    color: effectiveBorderColor,
                    width: borderWidth,
                  ),
            boxShadow: shadows ?? [
              BoxShadow(
                color: Colors.black.withValues(alpha: isDark ? 0.3 : 0.1),
                blurRadius: 20,
                spreadRadius: 2,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );

    // Wrap with gradient border if specified
    if (borderGradient != null) {
      glass = Container(
        decoration: BoxDecoration(
          gradient: borderGradient,
          borderRadius: BorderRadius.circular(borderRadius + borderWidth),
        ),
        padding: EdgeInsets.all(borderWidth),
        child: glass,
      );
    }

    if (margin != null) {
      glass = Padding(padding: margin!, child: glass);
    }

    return glass;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Card - البطاقة الزجاجية
// ═══════════════════════════════════════════════════════════════════════════

/// Glass card with optional title and actions
/// بطاقة زجاجية مع عنوان وإجراءات اختيارية
class GlassCard extends StatelessWidget {
  final Widget child;
  final String? title;
  final String? titleAr;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final double blurIntensity;
  final double opacity;
  final double borderRadius;
  final EdgeInsetsGeometry padding;
  final EdgeInsetsGeometry? margin;
  final Color? backgroundColor;
  final Gradient? borderGradient;
  final bool showDivider;
  final CrossAxisAlignment crossAxisAlignment;

  const GlassCard({
    super.key,
    required this.child,
    this.title,
    this.titleAr,
    this.leading,
    this.trailing,
    this.onTap,
    this.onLongPress,
    this.blurIntensity = 10.0,
    this.opacity = 0.1,
    this.borderRadius = 20.0,
    this.padding = const EdgeInsets.all(16),
    this.margin,
    this.backgroundColor,
    this.borderGradient,
    this.showDivider = true,
    this.crossAxisAlignment = CrossAxisAlignment.start,
  });

  @override
  Widget build(BuildContext context) {
    final hasHeader = title != null || titleAr != null || leading != null || trailing != null;
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayTitle = isRtl ? (titleAr ?? title) : (title ?? titleAr);

    return GestureDetector(
      onTap: onTap,
      onLongPress: onLongPress,
      child: GlassContainer(
        blurIntensity: blurIntensity,
        opacity: opacity,
        borderRadius: borderRadius,
        padding: padding,
        margin: margin,
        backgroundColor: backgroundColor,
        borderGradient: borderGradient,
        child: Column(
          crossAxisAlignment: crossAxisAlignment,
          mainAxisSize: MainAxisSize.min,
          children: [
            if (hasHeader) ...[
              Row(
                children: [
                  if (leading != null) ...[
                    leading!,
                    const SizedBox(width: 12),
                  ],
                  if (displayTitle != null)
                    Expanded(
                      child: Text(
                        displayTitle,
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  if (trailing != null) trailing!,
                ],
              ),
              if (showDivider) ...[
                const SizedBox(height: 12),
                Container(
                  height: 1,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Colors.transparent,
                        Colors.white.withValues(alpha: 0.2),
                        Colors.transparent,
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
              ] else
                const SizedBox(height: 16),
            ],
            child,
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass App Bar - شريط التطبيق الزجاجي
// ═══════════════════════════════════════════════════════════════════════════

/// Glassmorphism app bar with blur effect
/// شريط تطبيق زجاجي مع تأثير ضبابي
class GlassAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String? title;
  final String? titleAr;
  final Widget? titleWidget;
  final Widget? leading;
  final List<Widget>? actions;
  final double blurIntensity;
  final double opacity;
  final Color? backgroundColor;
  final double elevation;
  final bool centerTitle;
  final double toolbarHeight;
  final PreferredSizeWidget? bottom;
  final SystemUiOverlayStyle? systemOverlayStyle;

  const GlassAppBar({
    super.key,
    this.title,
    this.titleAr,
    this.titleWidget,
    this.leading,
    this.actions,
    this.blurIntensity = 15.0,
    this.opacity = 0.1,
    this.backgroundColor,
    this.elevation = 0,
    this.centerTitle = true,
    this.toolbarHeight = kToolbarHeight,
    this.bottom,
    this.systemOverlayStyle,
  });

  @override
  Size get preferredSize => Size.fromHeight(
    toolbarHeight + (bottom?.preferredSize.height ?? 0),
  );

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayTitle = isRtl ? (titleAr ?? title) : (title ?? titleAr);
    final glassColors = GlassColors.of(context);

    final effectiveOverlayStyle = systemOverlayStyle ??
        (isDark ? SystemUiOverlayStyle.light : SystemUiOverlayStyle.dark);

    return ClipRRect(
      child: BackdropFilter(
        filter: ImageFilter.blur(
          sigmaX: blurIntensity,
          sigmaY: blurIntensity,
        ),
        child: DecoratedBox(
          decoration: BoxDecoration(
            color: (backgroundColor ??
                (isDark ? glassColors.glassDark : glassColors.glassLight))
                .withValues(alpha: opacity),
            border: Border(
              bottom: BorderSide(
                color: isDark ? glassColors.borderDark : glassColors.borderLight,
                width: 0.5,
              ),
            ),
          ),
          child: AppBar(
            title: titleWidget ?? (displayTitle != null ? Text(displayTitle) : null),
            leading: leading,
            actions: actions,
            backgroundColor: Colors.transparent,
            elevation: elevation,
            centerTitle: centerTitle,
            toolbarHeight: toolbarHeight,
            bottom: bottom,
            systemOverlayStyle: effectiveOverlayStyle,
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Bottom Navigation - شريط التنقل السفلي الزجاجي
// ═══════════════════════════════════════════════════════════════════════════

/// Glassmorphism bottom navigation bar
/// شريط تنقل سفلي زجاجي
class GlassBottomNav extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;
  final List<GlassNavItem> items;
  final double blurIntensity;
  final double opacity;
  final double height;
  final double borderRadius;
  final Color? backgroundColor;
  final Color? selectedColor;
  final Color? unselectedColor;
  final bool showLabels;
  final bool floatingStyle;
  final EdgeInsetsGeometry margin;

  const GlassBottomNav({
    super.key,
    required this.currentIndex,
    required this.onTap,
    required this.items,
    this.blurIntensity = 15.0,
    this.opacity = 0.1,
    this.height = 70,
    this.borderRadius = 35,
    this.backgroundColor,
    this.selectedColor,
    this.unselectedColor,
    this.showLabels = false,
    this.floatingStyle = true,
    this.margin = const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final glassColors = GlassColors.of(context);
    final theme = Theme.of(context);

    final effectiveSelectedColor = selectedColor ?? theme.colorScheme.primary;
    final effectiveUnselectedColor = unselectedColor ??
        (isDark ? Colors.white70 : Colors.black54);

    Widget navBar = ClipRRect(
      borderRadius: BorderRadius.circular(floatingStyle ? borderRadius : 0),
      child: BackdropFilter(
        filter: ImageFilter.blur(
          sigmaX: blurIntensity,
          sigmaY: blurIntensity,
        ),
        child: Container(
          height: height,
          decoration: BoxDecoration(
            color: (backgroundColor ??
                (isDark ? glassColors.glassDark : glassColors.glassLight))
                .withValues(alpha: opacity),
            borderRadius: BorderRadius.circular(floatingStyle ? borderRadius : 0),
            border: floatingStyle
                ? Border.all(
                    color: isDark ? glassColors.borderDark : glassColors.borderLight,
                    width: 1,
                  )
                : Border(
                    top: BorderSide(
                      color: isDark ? glassColors.borderDark : glassColors.borderLight,
                      width: 0.5,
                    ),
                  ),
            boxShadow: floatingStyle
                ? [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: isDark ? 0.4 : 0.15),
                      blurRadius: 20,
                      offset: const Offset(0, -5),
                    ),
                  ]
                : null,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: List.generate(items.length, (index) {
              final item = items[index];
              final isSelected = index == currentIndex;

              return _GlassNavButton(
                item: item,
                isSelected: isSelected,
                selectedColor: effectiveSelectedColor,
                unselectedColor: effectiveUnselectedColor,
                showLabel: showLabels,
                onTap: () => onTap(index),
              );
            }),
          ),
        ),
      ),
    );

    if (floatingStyle) {
      navBar = Padding(padding: margin, child: navBar);
    }

    return navBar;
  }
}

/// Navigation item data
class GlassNavItem {
  final IconData icon;
  final IconData? activeIcon;
  final String label;
  final String? labelAr;
  final Widget? badge;

  const GlassNavItem({
    required this.icon,
    this.activeIcon,
    required this.label,
    this.labelAr,
    this.badge,
  });
}

class _GlassNavButton extends StatelessWidget {
  final GlassNavItem item;
  final bool isSelected;
  final Color selectedColor;
  final Color unselectedColor;
  final bool showLabel;
  final VoidCallback onTap;

  const _GlassNavButton({
    required this.item,
    required this.isSelected,
    required this.selectedColor,
    required this.unselectedColor,
    required this.showLabel,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayLabel = isRtl ? (item.labelAr ?? item.label) : item.label;
    final effectiveIcon = isSelected ? (item.activeIcon ?? item.icon) : item.icon;
    final color = isSelected ? selectedColor : unselectedColor;

    return Semantics(
      label: displayLabel,
      button: true,
      selected: isSelected,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          decoration: isSelected
              ? BoxDecoration(
                  color: selectedColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(16),
                )
              : null,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Stack(
                clipBehavior: Clip.none,
                children: [
                  Icon(effectiveIcon, color: color, size: 24),
                  if (item.badge != null)
                    Positioned(
                      right: -8,
                      top: -4,
                      child: item.badge!,
                    ),
                ],
              ),
              if (showLabel) ...[
                const SizedBox(height: 4),
                Text(
                  displayLabel,
                  style: TextStyle(
                    color: color,
                    fontSize: 10,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Button - الزر الزجاجي
// ═══════════════════════════════════════════════════════════════════════════

/// Glassmorphism button with various styles
/// زر زجاجي بأنماط متعددة
class GlassButton extends StatefulWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final VoidCallback? onLongPress;
  final double blurIntensity;
  final double opacity;
  final double borderRadius;
  final EdgeInsetsGeometry padding;
  final Color? backgroundColor;
  final Color? foregroundColor;
  final Gradient? gradient;
  final Gradient? borderGradient;
  final double? width;
  final double? height;
  final GlassButtonStyle style;
  final bool isLoading;
  final bool isDisabled;
  final IconData? icon;
  final double iconSize;

  const GlassButton({
    super.key,
    required this.child,
    this.onPressed,
    this.onLongPress,
    this.blurIntensity = 10.0,
    this.opacity = 0.15,
    this.borderRadius = 16.0,
    this.padding = const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
    this.backgroundColor,
    this.foregroundColor,
    this.gradient,
    this.borderGradient,
    this.width,
    this.height,
    this.style = GlassButtonStyle.filled,
    this.isLoading = false,
    this.isDisabled = false,
    this.icon,
    this.iconSize = 20,
  });

  /// Icon-only glass button
  GlassButton.icon({
    super.key,
    required IconData icon,
    this.onPressed,
    this.onLongPress,
    this.blurIntensity = 10.0,
    this.opacity = 0.15,
    double size = 48,
    this.backgroundColor,
    this.foregroundColor,
    this.gradient,
    this.borderGradient,
    this.isLoading = false,
    this.isDisabled = false,
  }) : child = Icon(icon),
       padding = EdgeInsets.zero,
       borderRadius = size / 2,
       width = size,
       height = size,
       style = GlassButtonStyle.filled,
       icon = null,
       iconSize = 20;

  @override
  State<GlassButton> createState() => _GlassButtonState();
}

enum GlassButtonStyle { filled, outlined, text }

class _GlassButtonState extends State<GlassButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  bool _isPressed = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.95).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleTapDown(TapDownDetails details) {
    if (!widget.isDisabled && !widget.isLoading) {
      setState(() => _isPressed = true);
      _controller.forward();
    }
  }

  void _handleTapUp(TapUpDetails details) {
    setState(() => _isPressed = false);
    _controller.reverse();
  }

  void _handleTapCancel() {
    setState(() => _isPressed = false);
    _controller.reverse();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final theme = Theme.of(context);
    final glassColors = GlassColors.of(context);

    final isEnabled = !widget.isDisabled && !widget.isLoading && widget.onPressed != null;
    final effectiveFgColor = widget.foregroundColor ??
        (isDark ? Colors.white : theme.colorScheme.onSurface);
    final effectiveBgColor = widget.backgroundColor ??
        (isDark ? glassColors.glassDark : glassColors.glassLight);

    final Widget buttonContent = widget.isLoading
        ? SizedBox(
            width: widget.iconSize,
            height: widget.iconSize,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(effectiveFgColor),
            ),
          )
        : Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (widget.icon != null) ...[
                Icon(widget.icon, size: widget.iconSize, color: effectiveFgColor),
                const SizedBox(width: 8),
              ],
              DefaultTextStyle(
                style: TextStyle(
                  color: effectiveFgColor,
                  fontWeight: FontWeight.bold,
                ),
                child: widget.child,
              ),
            ],
          );

    return GestureDetector(
      onTapDown: _handleTapDown,
      onTapUp: _handleTapUp,
      onTapCancel: _handleTapCancel,
      onTap: isEnabled ? widget.onPressed : null,
      onLongPress: isEnabled ? widget.onLongPress : null,
      child: AnimatedBuilder(
        animation: _scaleAnimation,
        builder: (context, child) {
          return Transform.scale(
            scale: _scaleAnimation.value,
            child: Opacity(
              opacity: isEnabled ? 1.0 : 0.5,
              child: GlassContainer(
                blurIntensity: widget.blurIntensity,
                opacity: widget.style == GlassButtonStyle.text ? 0 : widget.opacity,
                borderRadius: widget.borderRadius,
                padding: widget.padding,
                width: widget.width,
                height: widget.height,
                backgroundColor: widget.gradient != null ? null : effectiveBgColor,
                gradient: widget.gradient,
                borderGradient: widget.borderGradient,
                borderColor: widget.style == GlassButtonStyle.outlined
                    ? effectiveFgColor.withValues(alpha: 0.5)
                    : null,
                shadows: _isPressed ? [] : null,
                child: Center(child: buttonContent),
              ),
            ),
          );
        },
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Text Field - حقل النص الزجاجي
// ═══════════════════════════════════════════════════════════════════════════

/// Glassmorphism text field
/// حقل نص زجاجي
class GlassTextField extends StatelessWidget {
  final TextEditingController? controller;
  final String? hintText;
  final String? hintTextAr;
  final String? labelText;
  final String? labelTextAr;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final bool obscureText;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final ValueChanged<String>? onChanged;
  final ValueChanged<String>? onSubmitted;
  final VoidCallback? onTap;
  final String? Function(String?)? validator;
  final bool autofocus;
  final bool readOnly;
  final int? maxLines;
  final int? minLines;
  final double blurIntensity;
  final double opacity;
  final double borderRadius;
  final FocusNode? focusNode;

  const GlassTextField({
    super.key,
    this.controller,
    this.hintText,
    this.hintTextAr,
    this.labelText,
    this.labelTextAr,
    this.prefixIcon,
    this.suffixIcon,
    this.obscureText = false,
    this.keyboardType,
    this.textInputAction,
    this.onChanged,
    this.onSubmitted,
    this.onTap,
    this.validator,
    this.autofocus = false,
    this.readOnly = false,
    this.maxLines = 1,
    this.minLines,
    this.blurIntensity = 10.0,
    this.opacity = 0.08,
    this.borderRadius = 16.0,
    this.focusNode,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final glassColors = GlassColors.of(context);

    final displayHint = isRtl ? (hintTextAr ?? hintText) : (hintText ?? hintTextAr);
    final displayLabel = isRtl ? (labelTextAr ?? labelText) : (labelText ?? labelTextAr);

    return ClipRRect(
      borderRadius: BorderRadius.circular(borderRadius),
      child: BackdropFilter(
        filter: ImageFilter.blur(
          sigmaX: blurIntensity,
          sigmaY: blurIntensity,
        ),
        child: TextFormField(
          controller: controller,
          focusNode: focusNode,
          obscureText: obscureText,
          keyboardType: keyboardType,
          textInputAction: textInputAction,
          onChanged: onChanged,
          onFieldSubmitted: onSubmitted,
          onTap: onTap,
          validator: validator,
          autofocus: autofocus,
          readOnly: readOnly,
          maxLines: maxLines,
          minLines: minLines,
          style: TextStyle(
            color: isDark ? Colors.white : Colors.black87,
          ),
          decoration: InputDecoration(
            hintText: displayHint,
            labelText: displayLabel,
            prefixIcon: prefixIcon,
            suffixIcon: suffixIcon,
            filled: true,
            fillColor: (isDark ? glassColors.glassDark : glassColors.glassLight)
                .withValues(alpha: opacity),
            hintStyle: TextStyle(
              color: isDark ? Colors.white54 : Colors.black45,
            ),
            labelStyle: TextStyle(
              color: isDark ? Colors.white70 : Colors.black54,
            ),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(borderRadius),
              borderSide: BorderSide(
                color: isDark ? glassColors.borderDark : glassColors.borderLight,
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(borderRadius),
              borderSide: BorderSide(
                color: isDark ? glassColors.borderDark : glassColors.borderLight,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(borderRadius),
              borderSide: BorderSide(
                color: Theme.of(context).colorScheme.primary,
                width: 2,
              ),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(borderRadius),
              borderSide: BorderSide(
                color: Theme.of(context).colorScheme.error,
                width: 2,
              ),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 20,
              vertical: 16,
            ),
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Modal / Bottom Sheet - النافذة المنبثقة الزجاجية
// ═══════════════════════════════════════════════════════════════════════════

/// Show a glassmorphism modal bottom sheet
/// عرض نافذة سفلية زجاجية
Future<T?> showGlassBottomSheet<T>({
  required BuildContext context,
  required Widget Function(BuildContext) builder,
  double blurIntensity = 15.0,
  double opacity = 0.1,
  bool isDismissible = true,
  bool enableDrag = true,
  double? initialChildSize,
  double minChildSize = 0.25,
  double maxChildSize = 0.9,
  bool expand = false,
  bool useRootNavigator = false,
}) {
  return showModalBottomSheet<T>(
    context: context,
    isScrollControlled: true,
    isDismissible: isDismissible,
    enableDrag: enableDrag,
    useRootNavigator: useRootNavigator,
    backgroundColor: Colors.transparent,
    builder: (context) {
      final isDark = Theme.of(context).brightness == Brightness.dark;
      final glassColors = GlassColors.of(context);

      return ClipRRect(
        borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
        child: BackdropFilter(
          filter: ImageFilter.blur(
            sigmaX: blurIntensity,
            sigmaY: blurIntensity,
          ),
          child: DecoratedBox(
            decoration: BoxDecoration(
              color: (isDark ? glassColors.glassDark : glassColors.glassLight)
                  .withValues(alpha: opacity),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(28)),
              border: Border(
                top: BorderSide(
                  color: isDark ? glassColors.borderDark : glassColors.borderLight,
                ),
                left: BorderSide(
                  color: isDark ? glassColors.borderDark : glassColors.borderLight,
                ),
                right: BorderSide(
                  color: isDark ? glassColors.borderDark : glassColors.borderLight,
                ),
              ),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Handle
                Container(
                  margin: const EdgeInsets.only(top: 12, bottom: 8),
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: isDark ? Colors.white30 : Colors.black26,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                Flexible(child: builder(context)),
              ],
            ),
          ),
        ),
      );
    },
  );
}

/// Show a glassmorphism dialog
/// عرض حوار زجاجي
Future<T?> showGlassDialog<T>({
  required BuildContext context,
  required Widget Function(BuildContext) builder,
  double blurIntensity = 15.0,
  double opacity = 0.15,
  bool barrierDismissible = true,
  String? barrierLabel,
}) {
  return showDialog<T>(
    context: context,
    barrierDismissible: barrierDismissible,
    barrierLabel: barrierLabel,
    barrierColor: Colors.black54,
    builder: (context) {
      final isDark = Theme.of(context).brightness == Brightness.dark;
      final glassColors = GlassColors.of(context);

      return Dialog(
        backgroundColor: Colors.transparent,
        elevation: 0,
        child: ClipRRect(
          borderRadius: BorderRadius.circular(24),
          child: BackdropFilter(
            filter: ImageFilter.blur(
              sigmaX: blurIntensity,
              sigmaY: blurIntensity,
            ),
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: (isDark ? glassColors.glassDark : glassColors.glassLight)
                    .withValues(alpha: opacity),
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                  color: isDark ? glassColors.borderDark : glassColors.borderLight,
                ),
              ),
              child: builder(context),
            ),
          ),
        ),
      );
    },
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Chip - الشريحة الزجاجية
// ═══════════════════════════════════════════════════════════════════════════

/// Glassmorphism chip widget
/// شريحة زجاجية
class GlassChip extends StatelessWidget {
  final String label;
  final String? labelAr;
  final Widget? avatar;
  final Widget? deleteIcon;
  final VoidCallback? onTap;
  final VoidCallback? onDeleted;
  final bool isSelected;
  final Color? selectedColor;
  final double blurIntensity;
  final double opacity;

  const GlassChip({
    super.key,
    required this.label,
    this.labelAr,
    this.avatar,
    this.deleteIcon,
    this.onTap,
    this.onDeleted,
    this.isSelected = false,
    this.selectedColor,
    this.blurIntensity = 8.0,
    this.opacity = 0.1,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayLabel = isRtl ? (labelAr ?? label) : label;
    final glassColors = GlassColors.of(context);
    final theme = Theme.of(context);

    final effectiveSelectedColor = selectedColor ?? theme.colorScheme.primary;

    return GestureDetector(
      onTap: onTap,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: BackdropFilter(
          filter: ImageFilter.blur(
            sigmaX: blurIntensity,
            sigmaY: blurIntensity,
          ),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: isSelected
                  ? effectiveSelectedColor.withValues(alpha: 0.2)
                  : (isDark ? glassColors.glassDark : glassColors.glassLight)
                      .withValues(alpha: opacity),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: isSelected
                    ? effectiveSelectedColor
                    : (isDark ? glassColors.borderDark : glassColors.borderLight),
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                if (avatar != null) ...[
                  avatar!,
                  const SizedBox(width: 8),
                ],
                Text(
                  displayLabel,
                  style: TextStyle(
                    color: isSelected
                        ? effectiveSelectedColor
                        : (isDark ? Colors.white : Colors.black87),
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  ),
                ),
                if (onDeleted != null) ...[
                  const SizedBox(width: 4),
                  GestureDetector(
                    onTap: onDeleted,
                    child: deleteIcon ??
                        Icon(
                          Icons.close,
                          size: 16,
                          color: isDark ? Colors.white70 : Colors.black54,
                        ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Slider - المنزلق الزجاجي
// ═══════════════════════════════════════════════════════════════════════════

/// Glassmorphism slider widget
/// منزلق زجاجي
class GlassSlider extends StatelessWidget {
  final double value;
  final double min;
  final double max;
  final int? divisions;
  final ValueChanged<double>? onChanged;
  final ValueChanged<double>? onChangeStart;
  final ValueChanged<double>? onChangeEnd;
  final Color? activeColor;
  final Color? inactiveColor;
  final String? label;
  final double blurIntensity;
  final double opacity;
  final double trackHeight;
  final double thumbRadius;

  const GlassSlider({
    super.key,
    required this.value,
    this.min = 0.0,
    this.max = 1.0,
    this.divisions,
    this.onChanged,
    this.onChangeStart,
    this.onChangeEnd,
    this.activeColor,
    this.inactiveColor,
    this.label,
    this.blurIntensity = 8.0,
    this.opacity = 0.15,
    this.trackHeight = 8.0,
    this.thumbRadius = 12.0,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final theme = Theme.of(context);
    final glassColors = GlassColors.of(context);

    final effectiveActiveColor = activeColor ?? theme.colorScheme.primary;
    final effectiveInactiveColor = inactiveColor ??
        (isDark ? glassColors.glassDark : glassColors.glassLight);

    return ClipRRect(
      borderRadius: BorderRadius.circular(trackHeight),
      child: BackdropFilter(
        filter: ImageFilter.blur(
          sigmaX: blurIntensity,
          sigmaY: blurIntensity,
        ),
        child: SliderTheme(
          data: SliderThemeData(
            trackHeight: trackHeight,
            activeTrackColor: effectiveActiveColor,
            inactiveTrackColor: effectiveInactiveColor.withValues(alpha: opacity),
            thumbColor: effectiveActiveColor,
            overlayColor: effectiveActiveColor.withValues(alpha: 0.2),
            thumbShape: RoundSliderThumbShape(
              enabledThumbRadius: thumbRadius,
            ),
            overlayShape: RoundSliderOverlayShape(
              overlayRadius: thumbRadius * 1.5,
            ),
            trackShape: const RoundedRectSliderTrackShape(),
            valueIndicatorColor: effectiveActiveColor,
            valueIndicatorTextStyle: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          child: Slider(
            value: value,
            min: min,
            max: max,
            divisions: divisions,
            label: label,
            onChanged: onChanged,
            onChangeStart: onChangeStart,
            onChangeEnd: onChangeEnd,
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Progress Indicator - مؤشر التقدم الزجاجي
// ═══════════════════════════════════════════════════════════════════════════

/// Glassmorphism progress indicator
/// مؤشر تقدم زجاجي
class GlassProgressIndicator extends StatelessWidget {
  final double? value;
  final double height;
  final double borderRadius;
  final Color? backgroundColor;
  final Color? valueColor;
  final Gradient? valueGradient;
  final double blurIntensity;
  final double opacity;
  final String? label;
  final bool showPercentage;

  const GlassProgressIndicator({
    super.key,
    this.value,
    this.height = 8.0,
    this.borderRadius = 4.0,
    this.backgroundColor,
    this.valueColor,
    this.valueGradient,
    this.blurIntensity = 8.0,
    this.opacity = 0.1,
    this.label,
    this.showPercentage = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final theme = Theme.of(context);
    final glassColors = GlassColors.of(context);

    final effectiveValueColor = valueColor ?? theme.colorScheme.primary;
    final effectiveBgColor = backgroundColor ??
        (isDark ? glassColors.glassDark : glassColors.glassLight);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (label != null || showPercentage)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (label != null)
                  Text(
                    label!,
                    style: TextStyle(
                      color: isDark ? Colors.white70 : Colors.black54,
                      fontSize: 12,
                    ),
                  ),
                if (showPercentage && value != null)
                  Text(
                    '${(value! * 100).toInt()}%',
                    style: TextStyle(
                      color: effectiveValueColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
              ],
            ),
          ),
        ClipRRect(
          borderRadius: BorderRadius.circular(borderRadius),
          child: BackdropFilter(
            filter: ImageFilter.blur(
              sigmaX: blurIntensity,
              sigmaY: blurIntensity,
            ),
            child: Container(
              height: height,
              decoration: BoxDecoration(
                color: effectiveBgColor.withValues(alpha: opacity),
                borderRadius: BorderRadius.circular(borderRadius),
                border: Border.all(
                  color: isDark ? glassColors.borderDark : glassColors.borderLight,
                  width: 0.5,
                ),
              ),
              child: value != null
                  ? FractionallySizedBox(
                      alignment: Directionality.of(context) == TextDirection.rtl
                          ? Alignment.centerRight
                          : Alignment.centerLeft,
                      widthFactor: value!.clamp(0.0, 1.0),
                      child: Container(
                        decoration: BoxDecoration(
                          color: valueGradient == null ? effectiveValueColor : null,
                          gradient: valueGradient,
                          borderRadius: BorderRadius.circular(borderRadius),
                        ),
                      ),
                    )
                  : LinearProgressIndicator(
                      backgroundColor: Colors.transparent,
                      valueColor: AlwaysStoppedAnimation<Color>(effectiveValueColor),
                    ),
            ),
          ),
        ),
      ],
    );
  }
}
