import 'package:flutter/material.dart';

/// SAHOOL Responsive Design Utilities
/// أدوات التصميم المتجاوب لتطبيق سهول
///
/// Provides consistent breakpoints and responsive helpers for
/// building adaptive UI across different screen sizes.

/// Screen breakpoints based on Material Design guidelines
/// نقاط توقف الشاشة بناءً على إرشادات Material Design
class SahoolBreakpoints {
  SahoolBreakpoints._();

  /// Mobile compact (phones) - أقل من 600 بكسل
  static const double mobileCompact = 360;

  /// Mobile medium (large phones) - 360-600 بكسل
  static const double mobileMedium = 480;

  /// Mobile expanded (tablets in portrait) - 600 بكسل فما فوق
  static const double mobileExpanded = 600;

  /// Tablet (tablets in landscape) - 840 بكسل فما فوق
  static const double tablet = 840;

  /// Desktop - 1200 بكسل فما فوق
  static const double desktop = 1200;
}

/// Device type enumeration for responsive layouts
/// تعداد نوع الجهاز للتخطيطات المتجاوبة
enum SahoolDeviceType {
  /// Small phones - الهواتف الصغيرة
  mobileCompact,

  /// Large phones - الهواتف الكبيرة
  mobileMedium,

  /// Tablets in portrait - الأجهزة اللوحية عموديًا
  mobileExpanded,

  /// Tablets in landscape - الأجهزة اللوحية أفقيًا
  tablet,

  /// Desktop screens - شاشات سطح المكتب
  desktop,
}

/// Responsive helper extension on BuildContext
/// امتداد مساعد متجاوب على BuildContext
extension SahoolResponsiveContext on BuildContext {
  /// Get screen size
  Size get screenSize => MediaQuery.sizeOf(this);

  /// Get screen width
  double get screenWidth => screenSize.width;

  /// Get screen height
  double get screenHeight => screenSize.height;

  /// Get device pixel ratio
  double get devicePixelRatio => MediaQuery.devicePixelRatioOf(this);

  /// Get text scale factor
  double get textScaleFactor => MediaQuery.textScalerOf(this).scale(1.0);

  /// Check if device is in portrait mode
  bool get isPortrait => screenHeight > screenWidth;

  /// Check if device is in landscape mode
  bool get isLandscape => screenWidth > screenHeight;

  /// Get current device type based on screen width
  SahoolDeviceType get deviceType {
    final width = screenWidth;
    if (width < SahoolBreakpoints.mobileCompact) {
      return SahoolDeviceType.mobileCompact;
    } else if (width < SahoolBreakpoints.mobileMedium) {
      return SahoolDeviceType.mobileMedium;
    } else if (width < SahoolBreakpoints.mobileExpanded) {
      return SahoolDeviceType.mobileExpanded;
    } else if (width < SahoolBreakpoints.tablet) {
      return SahoolDeviceType.tablet;
    } else {
      return SahoolDeviceType.desktop;
    }
  }

  /// Check if screen is mobile size (compact or medium)
  bool get isMobile =>
      deviceType == SahoolDeviceType.mobileCompact ||
      deviceType == SahoolDeviceType.mobileMedium;

  /// Check if screen is tablet size
  bool get isTablet =>
      deviceType == SahoolDeviceType.mobileExpanded ||
      deviceType == SahoolDeviceType.tablet;

  /// Check if screen is desktop size
  bool get isDesktop => deviceType == SahoolDeviceType.desktop;

  /// Get safe area padding
  EdgeInsets get safeAreaPadding => MediaQuery.paddingOf(this);

  /// Get view insets (keyboard, etc.)
  EdgeInsets get viewInsets => MediaQuery.viewInsetsOf(this);

  /// Check if keyboard is visible
  bool get isKeyboardVisible => viewInsets.bottom > 0;

  /// Get responsive horizontal padding based on screen size
  double get responsiveHorizontalPadding {
    if (isMobile) return 16.0;
    if (isTablet) return 24.0;
    return 32.0;
  }

  /// Get responsive grid cross axis count
  int get responsiveGridCrossAxisCount {
    if (isMobile) return 2;
    if (isTablet) return 3;
    return 4;
  }

  /// Get responsive card aspect ratio
  double get responsiveCardAspectRatio {
    if (isMobile) return 1.0;
    if (isTablet) return 1.2;
    return 1.4;
  }
}

/// Responsive builder widget for different screen sizes
/// ويدجت بناء متجاوب لأحجام الشاشات المختلفة
class SahoolResponsiveBuilder extends StatelessWidget {
  final Widget Function(BuildContext context, SahoolDeviceType deviceType)?
      builder;
  final Widget? mobileCompact;
  final Widget? mobileMedium;
  final Widget? mobileExpanded;
  final Widget? tablet;
  final Widget? desktop;

  const SahoolResponsiveBuilder({
    super.key,
    this.builder,
    this.mobileCompact,
    this.mobileMedium,
    this.mobileExpanded,
    this.tablet,
    this.desktop,
  });

  @override
  Widget build(BuildContext context) {
    final deviceType = context.deviceType;

    if (builder != null) {
      return builder!(context, deviceType);
    }

    switch (deviceType) {
      case SahoolDeviceType.mobileCompact:
        return mobileCompact ??
            mobileMedium ??
            mobileExpanded ??
            const SizedBox.shrink();
      case SahoolDeviceType.mobileMedium:
        return mobileMedium ??
            mobileCompact ??
            mobileExpanded ??
            const SizedBox.shrink();
      case SahoolDeviceType.mobileExpanded:
        return mobileExpanded ??
            tablet ??
            mobileMedium ??
            const SizedBox.shrink();
      case SahoolDeviceType.tablet:
        return tablet ?? mobileExpanded ?? desktop ?? const SizedBox.shrink();
      case SahoolDeviceType.desktop:
        return desktop ?? tablet ?? mobileExpanded ?? const SizedBox.shrink();
    }
  }
}

/// Responsive value selector
/// محدد قيمة متجاوبة
class SahoolResponsiveValue<T> {
  final T mobileCompact;
  final T? mobileMedium;
  final T? mobileExpanded;
  final T? tablet;
  final T? desktop;

  const SahoolResponsiveValue({
    required this.mobileCompact,
    this.mobileMedium,
    this.mobileExpanded,
    this.tablet,
    this.desktop,
  });

  /// Get value based on current device type
  T of(BuildContext context) {
    final deviceType = context.deviceType;

    switch (deviceType) {
      case SahoolDeviceType.mobileCompact:
        return mobileCompact;
      case SahoolDeviceType.mobileMedium:
        return mobileMedium ?? mobileCompact;
      case SahoolDeviceType.mobileExpanded:
        return mobileExpanded ?? mobileMedium ?? mobileCompact;
      case SahoolDeviceType.tablet:
        return tablet ?? mobileExpanded ?? mobileMedium ?? mobileCompact;
      case SahoolDeviceType.desktop:
        return desktop ??
            tablet ??
            mobileExpanded ??
            mobileMedium ??
            mobileCompact;
    }
  }
}

/// Responsive spacing presets
/// مسافات متجاوبة مسبقة الإعداد
class SahoolResponsiveSpacing {
  SahoolResponsiveSpacing._();

  static double xs(BuildContext context) => context.isMobile ? 4.0 : 6.0;
  static double sm(BuildContext context) => context.isMobile ? 8.0 : 12.0;
  static double md(BuildContext context) => context.isMobile ? 16.0 : 24.0;
  static double lg(BuildContext context) => context.isMobile ? 24.0 : 32.0;
  static double xl(BuildContext context) => context.isMobile ? 32.0 : 48.0;
}

/// Responsive text sizes
/// أحجام النص المتجاوبة
class SahoolResponsiveText {
  SahoolResponsiveText._();

  static double caption(BuildContext context) => context.isMobile ? 12.0 : 14.0;
  static double body(BuildContext context) => context.isMobile ? 14.0 : 16.0;
  static double title(BuildContext context) => context.isMobile ? 18.0 : 22.0;
  static double headline(BuildContext context) =>
      context.isMobile ? 24.0 : 32.0;
  static double display(BuildContext context) => context.isMobile ? 32.0 : 48.0;
}

/// Responsive layout helper for consistent padding
/// مساعد تخطيط متجاوب للحشو المتسق
class SahoolResponsivePadding extends StatelessWidget {
  final Widget child;
  final bool includeTop;
  final bool includeBottom;

  const SahoolResponsivePadding({
    super.key,
    required this.child,
    this.includeTop = false,
    this.includeBottom = false,
  });

  @override
  Widget build(BuildContext context) {
    final horizontalPadding = context.responsiveHorizontalPadding;

    return Padding(
      padding: EdgeInsets.only(
        left: horizontalPadding,
        right: horizontalPadding,
        top: includeTop ? horizontalPadding : 0,
        bottom: includeBottom ? horizontalPadding : 0,
      ),
      child: child,
    );
  }
}

/// Responsive grid layout
/// تخطيط شبكة متجاوب
class SahoolResponsiveGrid extends StatelessWidget {
  final List<Widget> children;
  final double spacing;
  final double runSpacing;
  final double childAspectRatio;
  final int? crossAxisCount;

  const SahoolResponsiveGrid({
    super.key,
    required this.children,
    this.spacing = 12.0,
    this.runSpacing = 12.0,
    this.childAspectRatio = 1.0,
    this.crossAxisCount,
  });

  @override
  Widget build(BuildContext context) {
    final count = crossAxisCount ?? context.responsiveGridCrossAxisCount;

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: count,
        crossAxisSpacing: spacing,
        mainAxisSpacing: runSpacing,
        childAspectRatio: childAspectRatio,
      ),
      itemCount: children.length,
      itemBuilder: (context, index) => children[index],
    );
  }
}

/// Orientation builder wrapper with device type awareness
/// غلاف بناء الاتجاه مع إدراك نوع الجهاز
class SahoolOrientationBuilder extends StatelessWidget {
  final Widget Function(BuildContext context, Orientation orientation,
      SahoolDeviceType deviceType) builder;

  const SahoolOrientationBuilder({
    super.key,
    required this.builder,
  });

  @override
  Widget build(BuildContext context) {
    return OrientationBuilder(
      builder: (context, orientation) {
        return builder(context, orientation, context.deviceType);
      },
    );
  }
}
