import 'package:flutter/material.dart';

/// SAHOOL Glass Colors System
/// نظام ألوان الزجاج لسهول
///
/// Provides comprehensive color palettes for glassmorphism effects:
/// - Light and dark mode colors | ألوان الوضع الفاتح والداكن
/// - Gradient definitions | تعريفات التدرجات
/// - Blur configurations | إعدادات الضبابية
/// - Border colors | ألوان الحدود

// ═══════════════════════════════════════════════════════════════════════════
// Glass Color Configuration
// ═══════════════════════════════════════════════════════════════════════════

/// Configuration class for glass colors based on brightness
/// فئة تكوين ألوان الزجاج بناءً على السطوع
class GlassColors {
  final Brightness brightness;

  const GlassColors._(this.brightness);

  /// Get glass colors for current context
  static GlassColors of(BuildContext context) {
    return GlassColors._(Theme.of(context).brightness);
  }

  /// Light mode glass colors
  static const GlassColors light = GlassColors._(Brightness.light);

  /// Dark mode glass colors
  static const GlassColors dark = GlassColors._(Brightness.dark);

  // ─────────────────────────────────────────────────────────────────────────
  // Base Glass Colors - ألوان الزجاج الأساسية
  // ─────────────────────────────────────────────────────────────────────────

  /// Primary glass background color for light mode
  Color get glassLight => const Color(0xFFFFFFFF);

  /// Primary glass background color for dark mode
  Color get glassDark => const Color(0xFF1A1A1A);

  /// Current mode glass color
  Color get glass => brightness == Brightness.light ? glassLight : glassDark;

  // ─────────────────────────────────────────────────────────────────────────
  // Border Colors - ألوان الحدود
  // ─────────────────────────────────────────────────────────────────────────

  /// Border color for light mode
  Color get borderLight => const Color(0xFFFFFFFF).withValues(alpha: 0.3);

  /// Border color for dark mode
  Color get borderDark => const Color(0xFFFFFFFF).withValues(alpha: 0.1);

  /// Current mode border color
  Color get border => brightness == Brightness.light ? borderLight : borderDark;

  // ─────────────────────────────────────────────────────────────────────────
  // Surface Colors - ألوان السطح
  // ─────────────────────────────────────────────────────────────────────────

  /// Surface light
  Color get surfaceLight => const Color(0xFFF5F7FA);

  /// Surface dark
  Color get surfaceDark => const Color(0xFF121212);

  /// Current mode surface
  Color get surface => brightness == Brightness.light ? surfaceLight : surfaceDark;

  // ─────────────────────────────────────────────────────────────────────────
  // Overlay Colors - ألوان التراكب
  // ─────────────────────────────────────────────────────────────────────────

  /// Overlay for light mode (subtle darkening)
  Color get overlayLight => Colors.black.withValues(alpha: 0.05);

  /// Overlay for dark mode (subtle lightening)
  Color get overlayDark => Colors.white.withValues(alpha: 0.05);

  /// Current mode overlay
  Color get overlay => brightness == Brightness.light ? overlayLight : overlayDark;
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Color Palettes - لوحات ألوان الزجاج
// ═══════════════════════════════════════════════════════════════════════════

/// Predefined glass color palettes
/// لوحات ألوان زجاجية محددة مسبقاً
class GlassColorPalette {
  GlassColorPalette._();

  // ─────────────────────────────────────────────────────────────────────────
  // Light Mode Palettes - لوحات الوضع الفاتح
  // ─────────────────────────────────────────────────────────────────────────

  /// Clean white glass palette
  static const lightWhite = GlassPalette(
    background: Color(0xFFFFFFFF),
    border: Color(0x4DFFFFFF),
    shadow: Color(0x1A000000),
    highlight: Color(0xCCFFFFFF),
  );

  /// Frosted glass palette
  static const lightFrosted = GlassPalette(
    background: Color(0xFFF8FAFC),
    border: Color(0x33FFFFFF),
    shadow: Color(0x0D000000),
    highlight: Color(0xE6FFFFFF),
  );

  /// Cream tinted glass
  static const lightCream = GlassPalette(
    background: Color(0xFFFAF8F5),
    border: Color(0x40E8E4D9),
    shadow: Color(0x15000000),
    highlight: Color(0xD9FFFFFF),
  );

  /// Green tinted glass (SAHOOL brand)
  static const lightGreen = GlassPalette(
    background: Color(0xFFF0F7F0),
    border: Color(0x40367C2B),
    shadow: Color(0x15367C2B),
    highlight: Color(0xE6F5FFF5),
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Dark Mode Palettes - لوحات الوضع الداكن
  // ─────────────────────────────────────────────────────────────────────────

  /// Standard dark glass palette
  static const darkStandard = GlassPalette(
    background: Color(0xFF1A1A1A),
    border: Color(0x1AFFFFFF),
    shadow: Color(0x40000000),
    highlight: Color(0x0DFFFFFF),
  );

  /// AMOLED pure black glass palette
  static const darkAmoled = GlassPalette(
    background: Color(0xFF000000),
    border: Color(0x15FFFFFF),
    shadow: Color(0x60000000),
    highlight: Color(0x08FFFFFF),
  );

  /// Deep dark glass palette
  static const darkDeep = GlassPalette(
    background: Color(0xFF0D0D0D),
    border: Color(0x18FFFFFF),
    shadow: Color(0x50000000),
    highlight: Color(0x0AFFFFFF),
  );

  /// Charcoal dark glass
  static const darkCharcoal = GlassPalette(
    background: Color(0xFF1F1F1F),
    border: Color(0x20FFFFFF),
    shadow: Color(0x35000000),
    highlight: Color(0x10FFFFFF),
  );

  /// Green tinted dark glass (SAHOOL brand)
  static const darkGreen = GlassPalette(
    background: Color(0xFF0A1A0A),
    border: Color(0x20367C2B),
    shadow: Color(0x40000000),
    highlight: Color(0x0D367C2B),
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Accent Palettes - لوحات الألوان المميزة
  // ─────────────────────────────────────────────────────────────────────────

  /// Success (green) accent
  static const accentSuccess = GlassPalette(
    background: Color(0xFF4CAF50),
    border: Color(0x404CAF50),
    shadow: Color(0x304CAF50),
    highlight: Color(0x804CAF50),
  );

  /// Warning (amber) accent
  static const accentWarning = GlassPalette(
    background: Color(0xFFFF9800),
    border: Color(0x40FF9800),
    shadow: Color(0x30FF9800),
    highlight: Color(0x80FF9800),
  );

  /// Error (red) accent
  static const accentError = GlassPalette(
    background: Color(0xFFF44336),
    border: Color(0x40F44336),
    shadow: Color(0x30F44336),
    highlight: Color(0x80F44336),
  );

  /// Info (blue) accent
  static const accentInfo = GlassPalette(
    background: Color(0xFF2196F3),
    border: Color(0x402196F3),
    shadow: Color(0x302196F3),
    highlight: Color(0x802196F3),
  );

  /// Primary (SAHOOL green) accent
  static const accentPrimary = GlassPalette(
    background: Color(0xFF367C2B),
    border: Color(0x40367C2B),
    shadow: Color(0x30367C2B),
    highlight: Color(0x80367C2B),
  );
}

/// Individual glass palette definition
/// تعريف لوحة زجاجية فردية
class GlassPalette {
  final Color background;
  final Color border;
  final Color shadow;
  final Color highlight;

  const GlassPalette({
    required this.background,
    required this.border,
    required this.shadow,
    required this.highlight,
  });

  /// Create a copy with modifications
  GlassPalette copyWith({
    Color? background,
    Color? border,
    Color? shadow,
    Color? highlight,
  }) {
    return GlassPalette(
      background: background ?? this.background,
      border: border ?? this.border,
      shadow: shadow ?? this.shadow,
      highlight: highlight ?? this.highlight,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Gradients - التدرجات الزجاجية
// ═══════════════════════════════════════════════════════════════════════════

/// Predefined glass gradients for various effects
/// تدرجات زجاجية محددة مسبقاً لتأثيرات متنوعة
class GlassGradients {
  GlassGradients._();

  // ─────────────────────────────────────────────────────────────────────────
  // Light Mode Gradients - تدرجات الوضع الفاتح
  // ─────────────────────────────────────────────────────────────────────────

  /// Subtle white gradient for light mode glass
  static const LinearGradient lightSurface = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0x40FFFFFF),
      Color(0x20FFFFFF),
    ],
  );

  /// Frosted glass effect gradient
  static const LinearGradient lightFrosted = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [
      Color(0x60FFFFFF),
      Color(0x30FFFFFF),
      Color(0x10FFFFFF),
    ],
    stops: [0.0, 0.5, 1.0],
  );

  /// Light shimmer effect
  static const LinearGradient lightShimmer = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0x00FFFFFF),
      Color(0x40FFFFFF),
      Color(0x00FFFFFF),
    ],
    stops: [0.0, 0.5, 1.0],
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Dark Mode Gradients - تدرجات الوضع الداكن
  // ─────────────────────────────────────────────────────────────────────────

  /// Subtle dark gradient
  static const LinearGradient darkSurface = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0x20FFFFFF),
      Color(0x08FFFFFF),
    ],
  );

  /// Dark frosted glass effect
  static const LinearGradient darkFrosted = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [
      Color(0x15FFFFFF),
      Color(0x08FFFFFF),
      Color(0x03FFFFFF),
    ],
    stops: [0.0, 0.5, 1.0],
  );

  /// Dark shimmer effect
  static const LinearGradient darkShimmer = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0x00FFFFFF),
      Color(0x15FFFFFF),
      Color(0x00FFFFFF),
    ],
    stops: [0.0, 0.5, 1.0],
  );

  /// AMOLED optimized gradient
  static const LinearGradient amoledSurface = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0x10FFFFFF),
      Color(0x05FFFFFF),
    ],
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Border Gradients - تدرجات الحدود
  // ─────────────────────────────────────────────────────────────────────────

  /// Rainbow border gradient
  static const LinearGradient borderRainbow = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFFFF6B6B),
      Color(0xFFFFE66D),
      Color(0xFF4ECDC4),
      Color(0xFF45B7D1),
      Color(0xFFDDA0DD),
    ],
  );

  /// SAHOOL green gradient
  static const LinearGradient borderSahool = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFF367C2B),
      Color(0xFF4CAF50),
    ],
  );

  /// Golden harvest gradient
  static const LinearGradient borderGold = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFFD4A84B),
      Color(0xFFFFD700),
      Color(0xFFD4A84B),
    ],
  );

  /// Ocean blue gradient
  static const LinearGradient borderOcean = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFF1976D2),
      Color(0xFF42A5F5),
    ],
  );

  /// Sunset gradient
  static const LinearGradient borderSunset = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFFFF6B35),
      Color(0xFFF7931E),
      Color(0xFFFFD700),
    ],
  );

  /// Purple aurora gradient
  static const LinearGradient borderAurora = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFF667EEA),
      Color(0xFF764BA2),
      Color(0xFFB66DFF),
    ],
  );

  /// Silver gradient for light mode
  static const LinearGradient borderSilver = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFFE0E0E0),
      Color(0xFFF5F5F5),
      Color(0xFFE0E0E0),
    ],
  );

  /// Neon glow gradient for dark mode
  static const LinearGradient borderNeon = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      Color(0xFF00F5FF),
      Color(0xFF00FF87),
    ],
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Background Gradients - تدرجات الخلفية
  // ─────────────────────────────────────────────────────────────────────────

  /// Mesh gradient light
  static const RadialGradient meshLight = RadialGradient(
    center: Alignment(-0.5, -0.5),
    radius: 1.5,
    colors: [
      Color(0x20367C2B),
      Color(0x10D4A84B),
      Color(0x00FFFFFF),
    ],
  );

  /// Mesh gradient dark
  static const RadialGradient meshDark = RadialGradient(
    center: Alignment(-0.5, -0.5),
    radius: 1.5,
    colors: [
      Color(0x15367C2B),
      Color(0x08D4A84B),
      Color(0x00000000),
    ],
  );

  /// Animated gradient colors (for use with animation)
  static const List<Color> animatedColors = [
    Color(0xFF367C2B),
    Color(0xFF4CAF50),
    Color(0xFF8BC34A),
    Color(0xFFD4A84B),
    Color(0xFF367C2B),
  ];
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Blur Configurations - إعدادات الضبابية
// ═══════════════════════════════════════════════════════════════════════════

/// Predefined blur intensity configurations
/// إعدادات شدة الضبابية المحددة مسبقاً
class GlassBlur {
  GlassBlur._();

  /// No blur
  static const double none = 0.0;

  /// Subtle blur (minimal effect)
  static const double subtle = 5.0;

  /// Light blur (visible but not heavy)
  static const double light = 10.0;

  /// Medium blur (standard glass effect)
  static const double medium = 15.0;

  /// Heavy blur (strong glass effect)
  static const double heavy = 20.0;

  /// Extra heavy blur (very prominent)
  static const double extraHeavy = 30.0;

  /// Maximum blur (for overlays and modals)
  static const double maximum = 50.0;

  /// Performance-optimized blur for low-end devices
  static const double performance = 8.0;

  /// Get appropriate blur based on platform/performance
  static double adaptive(BuildContext context) {
    // Could be extended to check device capabilities
    return medium;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Opacity Configurations - إعدادات الشفافية
// ═══════════════════════════════════════════════════════════════════════════

/// Predefined opacity configurations for glass effects
/// إعدادات شفافية محددة مسبقاً للتأثيرات الزجاجية
class GlassOpacity {
  GlassOpacity._();

  /// Transparent (0%)
  static const double transparent = 0.0;

  /// Ghost (5%)
  static const double ghost = 0.05;

  /// Subtle (10%)
  static const double subtle = 0.1;

  /// Light (15%)
  static const double light = 0.15;

  /// Medium (20%)
  static const double medium = 0.2;

  /// Regular (30%)
  static const double regular = 0.3;

  /// Heavy (50%)
  static const double heavy = 0.5;

  /// Solid (70%)
  static const double solid = 0.7;

  /// Almost opaque (85%)
  static const double almostOpaque = 0.85;

  /// Opaque (100%)
  static const double opaque = 1.0;

  /// Light mode default
  static const double lightDefault = 0.1;

  /// Dark mode default (slightly higher for visibility)
  static const double darkDefault = 0.15;
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Shadows - الظلال الزجاجية
// ═══════════════════════════════════════════════════════════════════════════

/// Predefined shadow configurations for glass effects
/// إعدادات ظلال محددة مسبقاً للتأثيرات الزجاجية
class GlassShadows {
  GlassShadows._();

  /// No shadow
  static const List<BoxShadow> none = [];

  /// Subtle shadow for light mode
  static List<BoxShadow> subtleLight = [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.05),
      blurRadius: 10,
      spreadRadius: 0,
      offset: const Offset(0, 4),
    ),
  ];

  /// Subtle shadow for dark mode
  static List<BoxShadow> subtleDark = [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.2),
      blurRadius: 10,
      spreadRadius: 0,
      offset: const Offset(0, 4),
    ),
  ];

  /// Medium shadow for light mode
  static List<BoxShadow> mediumLight = [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.1),
      blurRadius: 20,
      spreadRadius: 2,
      offset: const Offset(0, 8),
    ),
  ];

  /// Medium shadow for dark mode
  static List<BoxShadow> mediumDark = [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.3),
      blurRadius: 20,
      spreadRadius: 2,
      offset: const Offset(0, 8),
    ),
  ];

  /// Heavy shadow for light mode
  static List<BoxShadow> heavyLight = [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.15),
      blurRadius: 30,
      spreadRadius: 4,
      offset: const Offset(0, 12),
    ),
  ];

  /// Heavy shadow for dark mode
  static List<BoxShadow> heavyDark = [
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.4),
      blurRadius: 30,
      spreadRadius: 4,
      offset: const Offset(0, 12),
    ),
  ];

  /// Glow shadow (for accented elements)
  static List<BoxShadow> glow(Color color, {double intensity = 0.3}) => [
    BoxShadow(
      color: color.withValues(alpha: intensity),
      blurRadius: 20,
      spreadRadius: 2,
      offset: Offset.zero,
    ),
  ];

  /// Inner shadow effect (requires Stack implementation)
  static List<BoxShadow> innerLight = [
    BoxShadow(
      color: Colors.white.withValues(alpha: 0.5),
      blurRadius: 10,
      spreadRadius: -5,
      offset: const Offset(0, -2),
    ),
    BoxShadow(
      color: Colors.black.withValues(alpha: 0.05),
      blurRadius: 10,
      spreadRadius: -5,
      offset: const Offset(0, 2),
    ),
  ];

  /// Get shadow based on brightness
  static List<BoxShadow> adaptive(BuildContext context, {bool heavy = false}) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    if (heavy) {
      return isDark ? heavyDark : heavyLight;
    }
    return isDark ? mediumDark : mediumLight;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Glass Border Radius - نصف قطر الحدود
// ═══════════════════════════════════════════════════════════════════════════

/// Predefined border radius values for glass elements
/// قيم نصف قطر الحدود المحددة مسبقاً للعناصر الزجاجية
class GlassBorderRadius {
  GlassBorderRadius._();

  /// No radius (sharp corners)
  static const double none = 0.0;

  /// Extra small radius
  static const double xs = 4.0;

  /// Small radius
  static const double sm = 8.0;

  /// Medium radius
  static const double md = 12.0;

  /// Large radius (default for cards)
  static const double lg = 16.0;

  /// Extra large radius
  static const double xl = 20.0;

  /// Double extra large radius
  static const double xxl = 24.0;

  /// Triple extra large radius
  static const double xxxl = 32.0;

  /// Full radius (for pills and circular elements)
  static const double full = 9999.0;

  /// Card default
  static const double card = 20.0;

  /// Button default
  static const double button = 16.0;

  /// Bottom sheet
  static const double bottomSheet = 28.0;

  /// Modal dialog
  static const double modal = 24.0;

  /// Chip
  static const double chip = 20.0;
}
