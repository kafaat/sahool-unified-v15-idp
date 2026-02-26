import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';

/// SAHOOL Accessibility Utilities
/// أدوات إمكانية الوصول لتطبيق سهول
///
/// This module provides accessibility support for visually impaired users.
/// يوفر هذا الملف دعم إمكانية الوصول للمستخدمين ضعاف البصر

/// Semantic label wrapper for icons
/// غلاف تسميات الدلالية للأيقونات
class SahoolSemanticIcon extends StatelessWidget {
  final IconData icon;
  final String label;
  final String labelAr;
  final double? size;
  final Color? color;

  const SahoolSemanticIcon({
    super.key,
    required this.icon,
    required this.label,
    required this.labelAr,
    this.size,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final isArabic = locale.languageCode == 'ar';

    return Semantics(
      label: isArabic ? labelAr : label,
      child: ExcludeSemantics(
        child: Icon(
          icon,
          size: size,
          color: color,
        ),
      ),
    );
  }
}

/// Accessible button wrapper with bilingual labels
/// غلاف زر قابل للوصول مع تسميات ثنائية اللغة
class SahoolAccessibleButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final Widget child;
  final String hint;
  final String hintAr;
  final bool isLoading;
  final bool isDisabled;

  const SahoolAccessibleButton({
    super.key,
    required this.onPressed,
    required this.child,
    required this.hint,
    required this.hintAr,
    this.isLoading = false,
    this.isDisabled = false,
  });

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final isArabic = locale.languageCode == 'ar';

    String semanticHint = isArabic ? hintAr : hint;
    if (isLoading) {
      semanticHint = isArabic ? 'جارٍ التحميل...' : 'Loading...';
    } else if (isDisabled) {
      semanticHint = isArabic ? 'معطل' : 'Disabled';
    }

    return Semantics(
      button: true,
      enabled: !isDisabled && !isLoading,
      hint: semanticHint,
      child: child,
    );
  }
}

/// Accessible image with description
/// صورة قابلة للوصول مع وصف
class SahoolAccessibleImage extends StatelessWidget {
  final ImageProvider image;
  final String description;
  final String descriptionAr;
  final double? width;
  final double? height;
  final BoxFit? fit;

  const SahoolAccessibleImage({
    super.key,
    required this.image,
    required this.description,
    required this.descriptionAr,
    this.width,
    this.height,
    this.fit,
  });

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final isArabic = locale.languageCode == 'ar';

    return Semantics(
      image: true,
      label: isArabic ? descriptionAr : description,
      child: Image(
        image: image,
        width: width,
        height: height,
        fit: fit,
        semanticLabel: isArabic ? descriptionAr : description,
      ),
    );
  }
}

/// Accessible card container
/// حاوية بطاقة قابلة للوصول
class SahoolAccessibleCard extends StatelessWidget {
  final Widget child;
  final String? label;
  final String? labelAr;
  final VoidCallback? onTap;
  final bool isSelected;

  const SahoolAccessibleCard({
    super.key,
    required this.child,
    this.label,
    this.labelAr,
    this.onTap,
    this.isSelected = false,
  });

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final isArabic = locale.languageCode == 'ar';

    return Semantics(
      container: true,
      button: onTap != null,
      selected: isSelected,
      label: isArabic ? labelAr : label,
      child: onTap != null
          ? InkWell(
              onTap: onTap,
              child: child,
            )
          : child,
    );
  }
}

/// Semantic header for sections
/// رأس دلالي للأقسام
class SahoolSemanticHeader extends StatelessWidget {
  final String title;
  final String titleAr;
  final int level;
  final Widget? child;

  const SahoolSemanticHeader({
    super.key,
    required this.title,
    required this.titleAr,
    this.level = 1,
    this.child,
  });

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final isArabic = locale.languageCode == 'ar';

    return Semantics(
      header: true,
      label: isArabic ? titleAr : title,
      child: child ??
          Text(
            isArabic ? titleAr : title,
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
    );
  }
}

/// Text scale factor aware text widget
/// نص يراعي معامل تكبير النص
class SahoolScalableText extends StatelessWidget {
  final String text;
  final TextStyle? style;
  final TextAlign? textAlign;
  final int? maxLines;
  final TextOverflow? overflow;
  final double minScale;
  final double maxScale;

  const SahoolScalableText(
    this.text, {
    super.key,
    this.style,
    this.textAlign,
    this.maxLines,
    this.overflow,
    this.minScale = 0.8,
    this.maxScale = 2.0,
  });

  @override
  Widget build(BuildContext context) {
    final mediaQuery = MediaQuery.of(context);
    final textScaleFactor =
        mediaQuery.textScaler.scale(1.0).clamp(minScale, maxScale);

    return MediaQuery(
      data: mediaQuery.copyWith(
        textScaler: TextScaler.linear(textScaleFactor),
      ),
      child: Text(
        text,
        style: style,
        textAlign: textAlign,
        maxLines: maxLines,
        overflow: overflow,
      ),
    );
  }
}

/// Focus trap for modals and dialogs
/// مصيدة التركيز للنوافذ المنبثقة
class SahoolFocusTrap extends StatefulWidget {
  final Widget child;
  final bool autofocus;

  const SahoolFocusTrap({
    super.key,
    required this.child,
    this.autofocus = true,
  });

  @override
  State<SahoolFocusTrap> createState() => _SahoolFocusTrapState();
}

class _SahoolFocusTrapState extends State<SahoolFocusTrap> {
  final FocusScopeNode _focusScopeNode = FocusScopeNode();

  @override
  void initState() {
    super.initState();
    if (widget.autofocus) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _focusScopeNode.requestFocus();
      });
    }
  }

  @override
  void dispose() {
    _focusScopeNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FocusScope(
      node: _focusScopeNode,
      child: widget.child,
    );
  }
}

/// Live region for dynamic announcements
/// منطقة حية للإعلانات الديناميكية
class SahoolLiveRegion extends StatelessWidget {
  final Widget child;
  final bool isLive;
  final Assertiveness assertiveness;

  const SahoolLiveRegion({
    super.key,
    required this.child,
    this.isLive = true,
    this.assertiveness = Assertiveness.polite,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      liveRegion: isLive,
      child: child,
    );
  }
}

/// Assertiveness levels for live regions
enum Assertiveness {
  /// Polite announcements that don't interrupt
  polite,

  /// Assertive announcements that interrupt
  assertive,
}

/// Extension methods for accessibility
extension AccessibilityExtensions on Widget {
  /// Add semantic label to any widget
  Widget withSemantics({
    String? label,
    String? labelAr,
    bool? button,
    bool? header,
    bool? image,
    VoidCallback? onTap,
  }) {
    return Builder(builder: (context) {
      final locale = Localizations.localeOf(context);
      final isArabic = locale.languageCode == 'ar';

      return Semantics(
        label: isArabic ? (labelAr ?? label) : label,
        button: button,
        header: header,
        image: image,
        onTap: onTap,
        child: this,
      );
    });
  }

  /// Exclude widget from semantics tree
  Widget excludeFromSemantics() {
    return ExcludeSemantics(child: this);
  }

  /// Merge semantics with descendants
  Widget mergeSemantics() {
    return MergeSemantics(child: this);
  }
}

/// Accessibility preferences provider
/// مزود تفضيلات إمكانية الوصول
class SahoolAccessibilityProvider extends InheritedWidget {
  final bool reduceMotion;
  final bool highContrast;
  final bool boldText;
  final double textScale;

  const SahoolAccessibilityProvider({
    super.key,
    required super.child,
    this.reduceMotion = false,
    this.highContrast = false,
    this.boldText = false,
    this.textScale = 1.0,
  });

  static SahoolAccessibilityProvider? of(BuildContext context) {
    return context
        .dependOnInheritedWidgetOfExactType<SahoolAccessibilityProvider>();
  }

  @override
  bool updateShouldNotify(SahoolAccessibilityProvider oldWidget) {
    return reduceMotion != oldWidget.reduceMotion ||
        highContrast != oldWidget.highContrast ||
        boldText != oldWidget.boldText ||
        textScale != oldWidget.textScale;
  }
}

/// Get accessibility preferences from context
SahoolAccessibilityProvider? getAccessibilityPreferences(BuildContext context) {
  return SahoolAccessibilityProvider.of(context);
}

/// Check if animations should be reduced
bool shouldReduceMotion(BuildContext context) {
  final prefs = SahoolAccessibilityProvider.of(context);
  return prefs?.reduceMotion ?? MediaQuery.of(context).disableAnimations;
}

/// Announce message to screen readers
/// إعلان رسالة لقارئات الشاشة
void announceToScreenReader(BuildContext context, String message) {
  SemanticsService.announce(message, Directionality.of(context));
}

/// Bilingual announcement
/// إعلان ثنائي اللغة
void announceBilingual(
  BuildContext context, {
  required String message,
  required String messageAr,
}) {
  final locale = Localizations.localeOf(context);
  final isArabic = locale.languageCode == 'ar';
  SemanticsService.announce(
    isArabic ? messageAr : message,
    Directionality.of(context),
  );
}
