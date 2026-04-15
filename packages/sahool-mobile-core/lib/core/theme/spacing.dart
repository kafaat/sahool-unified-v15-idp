import 'package:flutter/widgets.dart';

// =============================================================================
// SahoolSpacing - نظام التباعد الموحد
// Centralized spacing scale following a 4-point grid system
//
// Replaces scattered magic numbers (12, 16, 20, 24, etc.) with named tokens.
// All values are multiples of 4 for consistent visual rhythm.
// =============================================================================

/// Spacing design tokens for the SAHOOL design system.
///
/// يوفر مقياس تباعد موحد يعتمد على شبكة 4 نقاط
/// لضمان إيقاع بصري متسق في جميع أنحاء التطبيق.
///
/// Usage:
/// ```dart
/// Padding(padding: EdgeInsets.all(SahoolSpacing.lg));
/// SizedBox(height: SahoolSpacing.sectionGap);
/// ```
class SahoolSpacing {
  SahoolSpacing._();

  // ---------------------------------------------------------------------------
  // Scale tokens - رموز المقياس
  // ---------------------------------------------------------------------------

  /// 2.0 - Minimal gap (e.g., between icon and badge)
  /// فجوة صغيرة جداً
  static const double xxs = 2.0;

  /// 4.0 - Tight gap (e.g., between inline elements)
  /// فجوة ضيقة
  static const double xs = 4.0;

  /// 8.0 - Small gap (e.g., between related items in a group)
  /// فجوة صغيرة
  static const double sm = 8.0;

  /// 12.0 - Medium gap (e.g., internal padding for compact widgets)
  /// فجوة متوسطة
  static const double md = 12.0;

  /// 16.0 - Large gap (e.g., standard card padding, screen margin)
  /// فجوة كبيرة
  static const double lg = 16.0;

  /// 20.0 - Extra-large gap (e.g., input field padding, dialog padding)
  /// فجوة كبيرة جداً
  static const double xl = 20.0;

  /// 24.0 - Section-level gap (e.g., between content sections)
  /// فجوة على مستوى القسم
  static const double xxl = 24.0;

  /// 32.0 - Major section gap (e.g., between page sections)
  /// فجوة رئيسية بين الأقسام
  static const double xxxl = 32.0;

  /// 48.0 - Huge gap (e.g., hero area spacing, large separators)
  /// فجوة ضخمة
  static const double huge = 48.0;

  /// 64.0 - Massive gap (e.g., page-level vertical spacing)
  /// فجوة هائلة
  static const double massive = 64.0;

  // ---------------------------------------------------------------------------
  // Semantic tokens - الرموز الدلالية
  // ---------------------------------------------------------------------------

  /// Internal card padding (16.0)
  /// الحشو الداخلي للبطاقات
  static const double cardPadding = lg;

  /// Gap between content sections (24.0)
  /// الفجوة بين أقسام المحتوى
  static const double sectionGap = xxl;

  /// Horizontal screen edge padding (16.0)
  /// حشو حواف الشاشة الأفقية
  static const double screenPadding = lg;

  /// Input field internal padding (20.0)
  /// الحشو الداخلي لحقول الإدخال
  static const double inputPadding = xl;

  /// Gap between list items (8.0)
  /// الفجوة بين عناصر القائمة
  static const double listItemGap = sm;

  /// Gap between form fields (16.0)
  /// الفجوة بين حقول النموذج
  static const double formFieldGap = lg;

  /// Horizontal button padding (24.0)
  /// الحشو الأفقي للأزرار
  static const double buttonPaddingH = xxl;

  /// Vertical button padding (14.0)
  /// الحشو العمودي للأزرار
  static const double buttonPaddingV = 14.0;

  /// Chip internal padding (12.0)
  /// الحشو الداخلي للشرائح
  static const double chipPadding = md;

  /// Icon-to-text gap (8.0)
  /// الفجوة بين الأيقونة والنص
  static const double iconTextGap = sm;

  // ---------------------------------------------------------------------------
  // EdgeInsets helpers - مساعدات الحشو
  // ---------------------------------------------------------------------------

  /// Standard screen padding (horizontal: 16)
  /// حشو الشاشة القياسي
  static const EdgeInsets screenH = EdgeInsets.symmetric(horizontal: lg);

  /// Standard card padding (all: 16)
  /// حشو البطاقة القياسي
  static const EdgeInsets cardAll = EdgeInsets.all(lg);

  /// Card margin (horizontal: 16, vertical: 8)
  /// هامش البطاقة
  static const EdgeInsets cardMargin =
      EdgeInsets.symmetric(horizontal: lg, vertical: sm);

  /// Input content padding (horizontal: 20, vertical: 16)
  /// حشو محتوى حقل الإدخال
  static const EdgeInsets inputContent =
      EdgeInsets.symmetric(horizontal: xl, vertical: lg);

  /// List tile padding (horizontal: 16, vertical: 4)
  /// حشو عنصر القائمة
  static const EdgeInsets listTile =
      EdgeInsets.symmetric(horizontal: lg, vertical: xs);
}

// =============================================================================
// SahoolRadius - نصف قطر الحواف الموحد
// Centralized border radius tokens
// =============================================================================

/// Border radius design tokens for the SAHOOL design system.
///
/// يوفر رموز نصف قطر الحواف الموحدة
/// لضمان تناسق الزوايا الدائرية في جميع أنحاء التطبيق.
///
/// Usage:
/// ```dart
/// Container(
///   decoration: BoxDecoration(
///     borderRadius: SahoolRadius.cardBorder,
///   ),
/// );
/// ClipRRect(borderRadius: SahoolRadius.buttonBorder, child: ...);
/// ```
class SahoolRadius {
  SahoolRadius._();

  // ---------------------------------------------------------------------------
  // Scale tokens - رموز المقياس
  // ---------------------------------------------------------------------------

  /// 4.0 - Extra-small radius (e.g., badges, tags)
  /// نصف قطر صغير جداً
  static const double xs = 4.0;

  /// 8.0 - Small radius (e.g., small chips, thumbnails)
  /// نصف قطر صغير
  static const double sm = 8.0;

  /// 12.0 - Medium radius (e.g., buttons, inputs, snackbars)
  /// نصف قطر متوسط
  static const double md = 12.0;

  /// 16.0 - Large radius (e.g., cards, containers)
  /// نصف قطر كبير
  static const double lg = 16.0;

  /// 20.0 - Extra-large radius (e.g., dialogs, glass cards)
  /// نصف قطر كبير جداً
  static const double xl = 20.0;

  /// 24.0 - Bottom sheets, modals
  /// نصف قطر للأوراق السفلية والنوافذ المنبثقة
  static const double xxl = 24.0;

  /// 100.0 - Full pill / circular shape
  /// شكل حبة دواء / دائري كامل
  static const double pill = 100.0;

  // ---------------------------------------------------------------------------
  // Semantic tokens - الرموز الدلالية
  // ---------------------------------------------------------------------------

  /// Card corner radius (16.0)
  /// نصف قطر زوايا البطاقة
  static const double card = lg;

  /// Button corner radius (12.0)
  /// نصف قطر زوايا الزر
  static const double button = md;

  /// Text input corner radius (12.0)
  /// نصف قطر زوايا حقل الإدخال
  static const double input = md;

  /// Bottom sheet top corners (24.0)
  /// نصف قطر الأوراق السفلية
  static const double bottomSheet = xxl;

  /// Dialog corner radius (20.0)
  /// نصف قطر نافذة الحوار
  static const double dialog = xl;

  /// Snackbar corner radius (12.0)
  /// نصف قطر شريط الإشعار
  static const double snackbar = md;

  /// Chip corner radius (20.0)
  /// نصف قطر الشريحة
  static const double chip = xl;

  /// FAB corner radius (16.0)
  /// نصف قطر زر الإجراء العائم
  static const double fab = lg;

  /// Glass card corner radius (20.0)
  /// نصف قطر بطاقة الزجاج
  static const double glassCard = xl;

  // ---------------------------------------------------------------------------
  // Legacy aliases - أسماء مستعارة قديمة
  // Preserved for backward compatibility with existing code.
  // ---------------------------------------------------------------------------

  /// @deprecated Use [sm] instead.
  static const double small = sm;

  /// @deprecated Use [md] instead.
  static const double medium = md;

  /// @deprecated Use [lg] instead.
  static const double large = lg;

  /// @deprecated Use [xl] instead.
  static const double xlarge = xl;

  /// @deprecated Use [pill] instead.
  static const double circular = pill;

  /// @deprecated Use [smBorder] instead.
  static BorderRadius get smallRadius => smBorder;

  /// @deprecated Use [mdBorder] instead.
  static BorderRadius get mediumRadius => mdBorder;

  /// @deprecated Use [lgBorder] instead.
  static BorderRadius get largeRadius => lgBorder;

  /// @deprecated Use [xlBorder] instead.
  static BorderRadius get xlargeRadius => xlBorder;

  // ---------------------------------------------------------------------------
  // BorderRadius helpers - مساعدات نصف القطر
  // ---------------------------------------------------------------------------

  /// BorderRadius for cards
  static BorderRadius get cardBorder => BorderRadius.circular(card);

  /// BorderRadius for buttons
  static BorderRadius get buttonBorder => BorderRadius.circular(button);

  /// BorderRadius for text inputs
  static BorderRadius get inputBorder => BorderRadius.circular(input);

  /// BorderRadius for bottom sheets (top corners only)
  static BorderRadius get bottomSheetBorder =>
      const BorderRadius.vertical(top: Radius.circular(xxl));

  /// BorderRadius for dialogs
  static BorderRadius get dialogBorder => BorderRadius.circular(dialog);

  /// BorderRadius for snackbars
  static BorderRadius get snackbarBorder => BorderRadius.circular(snackbar);

  /// BorderRadius for chips
  static BorderRadius get chipBorder => BorderRadius.circular(chip);

  /// BorderRadius for FABs
  static BorderRadius get fabBorder => BorderRadius.circular(fab);

  /// BorderRadius for glass cards
  static BorderRadius get glassCardBorder => BorderRadius.circular(glassCard);

  /// BorderRadius for pill shapes
  static BorderRadius get pillBorder => BorderRadius.circular(pill);

  /// BorderRadius for extra-small elements
  static BorderRadius get xsBorder => BorderRadius.circular(xs);

  /// BorderRadius for small elements
  static BorderRadius get smBorder => BorderRadius.circular(sm);

  /// BorderRadius for medium elements
  static BorderRadius get mdBorder => BorderRadius.circular(md);

  /// BorderRadius for large elements
  static BorderRadius get lgBorder => BorderRadius.circular(lg);

  /// BorderRadius for extra-large elements
  static BorderRadius get xlBorder => BorderRadius.circular(xl);

  /// BorderRadius for xxl elements
  static BorderRadius get xxlBorder => BorderRadius.circular(xxl);
}
