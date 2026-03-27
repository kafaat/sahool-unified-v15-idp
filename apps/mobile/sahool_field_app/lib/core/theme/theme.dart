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

// Note: SahoolTheme from config/theme.dart is not re-exported here
// to avoid ambiguous_export with sahool_theme.dart's SahoolTheme.
// Import 'package:sahool_field_app/core/config/theme.dart' directly if needed.
// ملاحظة: لا يُعاد تصدير SahoolTheme من config/theme.dart هنا لتجنب التعارض.
