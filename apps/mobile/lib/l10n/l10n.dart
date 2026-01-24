// SAHOOL Mobile App - Localization Configuration
// Supports Arabic (RTL) and English (LTR)
// Uses Flutter's gen_l10n for generated localization files

import 'package:flutter/material.dart';
import '../generated/l10n/app_localizations.dart';

// Re-export the generated AppLocalizations for convenience
export '../generated/l10n/app_localizations.dart';

/// Extension to easily access localization from BuildContext
extension LocalizationExtension on BuildContext {
  /// Get AppLocalizations instance (generated)
  AppLocalizations get l10n => AppLocalizations.of(this)!;

  /// Get AppLocalizations instance (nullable)
  AppLocalizations? get l10nOrNull => AppLocalizations.of(this);

  /// Get current locale
  Locale get currentLocale => Localizations.localeOf(this);

  /// Check if current locale is RTL
  bool get isRTL => Localizations.localeOf(this).languageCode == 'ar';

  /// Check if current locale is Arabic
  bool get isArabic => Localizations.localeOf(this).languageCode == 'ar';

  /// Check if current locale is English
  bool get isEnglish => Localizations.localeOf(this).languageCode == 'en';

  /// Get text direction
  TextDirection get textDirection =>
      isRTL ? TextDirection.rtl : TextDirection.ltr;

  /// Get current language name
  String get currentLanguageName => isArabic ? 'العربية' : 'English';

  /// Get language code
  String get languageCode => currentLocale.languageCode;
}

/// Locale Provider for state management
class LocaleProvider extends ChangeNotifier {
  Locale _locale = const Locale('ar');

  /// Default locale (Arabic for Yemen)
  static const Locale defaultLocale = Locale('ar');

  Locale get locale => _locale;

  /// Change locale
  void setLocale(Locale locale) {
    if (!AppLocalizations.supportedLocales.contains(locale)) return;
    _locale = locale;
    notifyListeners();
  }

  /// Toggle between Arabic and English
  void toggleLocale() {
    if (_locale.languageCode == 'ar') {
      setLocale(const Locale('en'));
    } else {
      setLocale(const Locale('ar'));
    }
  }

  /// Set Arabic locale
  void setArabic() {
    setLocale(const Locale('ar'));
  }

  /// Set English locale
  void setEnglish() {
    setLocale(const Locale('en'));
  }
}

/// Helper class for RTL/LTR-aware padding and positioning
class LocalizedLayout {
  final BuildContext context;

  LocalizedLayout(this.context);

  /// Get appropriate EdgeInsets based on text direction
  EdgeInsets edgeInsets({
    double? start,
    double? end,
    double? top,
    double? bottom,
    double? horizontal,
    double? vertical,
  }) {
    final isRTL = context.isRTL;

    if (horizontal != null) {
      return EdgeInsets.symmetric(
          horizontal: horizontal, vertical: vertical ?? 0);
    }

    if (vertical != null && start == null && end == null) {
      return EdgeInsets.symmetric(vertical: vertical);
    }

    final left = isRTL ? (end ?? 0) : (start ?? 0);
    final right = isRTL ? (start ?? 0) : (end ?? 0);

    return EdgeInsets.only(
      left: left,
      right: right,
      top: top ?? 0,
      bottom: bottom ?? 0,
    );
  }

  /// Get start-aligned EdgeInsets
  EdgeInsets startPadding(double value) {
    return context.isRTL
        ? EdgeInsets.only(right: value)
        : EdgeInsets.only(left: value);
  }

  /// Get end-aligned EdgeInsets
  EdgeInsets endPadding(double value) {
    return context.isRTL
        ? EdgeInsets.only(left: value)
        : EdgeInsets.only(right: value);
  }

  /// Get appropriate alignment based on text direction
  Alignment getAlignment(Alignment ltrAlignment) {
    if (!context.isRTL) return ltrAlignment;

    // Mirror horizontal alignments for RTL
    if (ltrAlignment == Alignment.centerLeft) {
      return Alignment.centerRight;
    } else if (ltrAlignment == Alignment.centerRight) {
      return Alignment.centerLeft;
    } else if (ltrAlignment == Alignment.topLeft) {
      return Alignment.topRight;
    } else if (ltrAlignment == Alignment.topRight) {
      return Alignment.topLeft;
    } else if (ltrAlignment == Alignment.bottomLeft) {
      return Alignment.bottomRight;
    } else if (ltrAlignment == Alignment.bottomRight) {
      return Alignment.bottomLeft;
    }

    return ltrAlignment;
  }

  /// Get start alignment
  Alignment get startAlignment =>
      context.isRTL ? Alignment.centerRight : Alignment.centerLeft;

  /// Get end alignment
  Alignment get endAlignment =>
      context.isRTL ? Alignment.centerLeft : Alignment.centerRight;

  /// Get appropriate TextAlign based on text direction
  TextAlign get defaultTextAlign =>
      context.isRTL ? TextAlign.right : TextAlign.left;

  /// Get appropriate TextAlign (start)
  TextAlign get startAlign => context.isRTL ? TextAlign.right : TextAlign.left;

  /// Get appropriate TextAlign (end)
  TextAlign get endAlign => context.isRTL ? TextAlign.left : TextAlign.right;

  /// Get text direction
  TextDirection get textDirection =>
      context.isRTL ? TextDirection.rtl : TextDirection.ltr;
}

/// Format numbers according to locale
class LocalizedNumberFormat {
  final Locale locale;

  LocalizedNumberFormat(this.locale);

  /// Create from BuildContext
  factory LocalizedNumberFormat.of(BuildContext context) {
    return LocalizedNumberFormat(Localizations.localeOf(context));
  }

  /// Check if locale is Arabic
  bool get isArabic => locale.languageCode == 'ar';

  /// Format number with appropriate separators
  String format(num number, {int? decimalDigits}) {
    if (decimalDigits != null) {
      final formatted = number.toStringAsFixed(decimalDigits);
      return isArabic ? _toArabicDigits(formatted) : formatted;
    }

    final formatted = number.toString();
    return isArabic ? _toArabicDigits(formatted) : formatted;
  }

  /// Format number with thousands separators
  String formatWithSeparators(num number, {int? decimalDigits}) {
    String formatted;
    if (decimalDigits != null) {
      formatted = number.toStringAsFixed(decimalDigits);
    } else {
      formatted = number.toString();
    }

    // Add thousands separators
    final parts = formatted.split('.');
    final integerPart = parts[0].replaceAllMapped(
      RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
      (Match m) => '${m[1]},',
    );

    if (parts.length > 1) {
      formatted = '$integerPart.${parts[1]}';
    } else {
      formatted = integerPart;
    }

    return isArabic ? _toArabicDigits(formatted) : formatted;
  }

  /// Convert Western digits to Arabic digits
  String _toArabicDigits(String input) {
    const arabicDigits = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
    const westernDigits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    var result = input;
    for (var i = 0; i < 10; i++) {
      result = result.replaceAll(westernDigits[i], arabicDigits[i]);
    }
    return result;
  }

  /// Convert Arabic digits to Western digits
  String toWesternDigits(String input) {
    const arabicDigits = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
    const westernDigits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    var result = input;
    for (var i = 0; i < 10; i++) {
      result = result.replaceAll(arabicDigits[i], westernDigits[i]);
    }
    return result;
  }

  /// Format currency for Saudi Riyal (SAR)
  String formatCurrency(num amount, {String? currencySymbol}) {
    final symbol = currencySymbol ?? (isArabic ? 'ريال' : 'SAR');
    final formatted = formatWithSeparators(amount, decimalDigits: 2);

    if (isArabic) {
      return '$formatted $symbol';
    } else {
      return '$symbol $formatted';
    }
  }

  /// Format percentage
  String formatPercentage(num value, {int decimalDigits = 1}) {
    final formatted = format(value, decimalDigits: decimalDigits);
    return isArabic ? '%$formatted' : '$formatted%';
  }

  /// Format area in hectares
  String formatArea(num hectares, {int decimalDigits = 1}) {
    final formatted = format(hectares, decimalDigits: decimalDigits);
    final unit = isArabic ? 'هـ' : 'ha';
    return '$formatted $unit';
  }

  /// Format weight in kilograms
  String formatWeight(num kg, {int decimalDigits = 0}) {
    final formatted = formatWithSeparators(kg, decimalDigits: decimalDigits);
    final unit = isArabic ? 'كجم' : 'kg';
    return '$formatted $unit';
  }

  /// Format weight in tons
  String formatTons(num tons, {int decimalDigits = 1}) {
    final formatted = formatWithSeparators(tons, decimalDigits: decimalDigits);
    final unit = isArabic ? 'طن' : 't';
    return '$formatted $unit';
  }

  /// Format volume in liters
  String formatLiters(num liters, {int decimalDigits = 0}) {
    final formatted = formatWithSeparators(liters, decimalDigits: decimalDigits);
    final unit = isArabic ? 'لتر' : 'L';
    return '$formatted $unit';
  }

  /// Format volume in cubic meters
  String formatCubicMeters(num m3, {int decimalDigits = 0}) {
    final formatted = formatWithSeparators(m3, decimalDigits: decimalDigits);
    final unit = isArabic ? 'م³' : 'm³';
    return '$formatted $unit';
  }
}

/// Direction-aware icon rotation
class DirectionalIcon extends StatelessWidget {
  final IconData icon;
  final double? size;
  final Color? color;
  final bool flipForRTL;

  const DirectionalIcon(
    this.icon, {
    super.key,
    this.size,
    this.color,
    this.flipForRTL = true,
  });

  @override
  Widget build(BuildContext context) {
    final shouldFlip = flipForRTL && context.isRTL;

    if (shouldFlip) {
      return Transform(
        alignment: Alignment.center,
        transform: Matrix4.rotationY(3.14159), // 180 degrees
        child: Icon(icon, size: size, color: color),
      );
    }

    return Icon(icon, size: size, color: color);
  }
}

/// Widget that wraps content with appropriate text direction
class DirectionalWrapper extends StatelessWidget {
  final Widget child;
  final bool forceRTL;
  final bool forceLTR;

  const DirectionalWrapper({
    super.key,
    required this.child,
    this.forceRTL = false,
    this.forceLTR = false,
  });

  @override
  Widget build(BuildContext context) {
    TextDirection direction;

    if (forceRTL) {
      direction = TextDirection.rtl;
    } else if (forceLTR) {
      direction = TextDirection.ltr;
    } else {
      direction = context.textDirection;
    }

    return Directionality(
      textDirection: direction,
      child: child,
    );
  }
}

/// Convenience extension for layout helpers
extension LayoutExtension on BuildContext {
  /// Get LocalizedLayout instance
  LocalizedLayout get layout => LocalizedLayout(this);

  /// Get LocalizedNumberFormat instance
  LocalizedNumberFormat get numberFormat => LocalizedNumberFormat.of(this);
}
