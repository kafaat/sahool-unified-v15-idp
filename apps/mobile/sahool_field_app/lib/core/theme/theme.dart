/// SAHOOL Theme System
/// نظام الثيم لتطبيق سهول
///
/// This barrel file exports all theme-related components.
/// يصدر هذا الملف جميع مكونات الثيم.
///
/// Primary Theme Usage:
/// - [SahoolTheme] from sahool_theme.dart: Main application theme with light/dark modes
/// - [SahoolColors] from sahool_theme.dart: Color palette
///
/// Specialized Themes:
/// - [SahoolProTheme] from sahool_pro_theme.dart: Professional/industrial theme variant
/// - [SahoolGlass] from sahool_glass.dart: Glassmorphism widgets
/// - [OrganicCard], [MetricCard] from organic_widgets.dart: Bento-style widgets
///
/// Recommended usage:
/// ```dart
/// MaterialApp(
///   theme: SahoolTheme.lightTheme,
///   darkTheme: SahoolTheme.darkTheme,
///   // ...
/// )
/// ```
library;

// Main theme - الثيم الرئيسي
export 'sahool_theme.dart';

// Professional theme variant - ثيم احترافي بديل
export 'sahool_pro_theme.dart';

// Glassmorphism widgets - ويدجات زجاجية
export 'sahool_glass.dart';

// Organic/Bento widgets - ويدجات عضوية
export 'organic_widgets.dart';

// Re-export from config for backwards compatibility
// إعادة التصدير من config للتوافق مع الإصدارات السابقة
export '../config/theme.dart' show SahoolTheme;
