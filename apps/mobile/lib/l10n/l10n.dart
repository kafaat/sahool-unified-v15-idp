// SAHOOL Mobile App - Localization Configuration
// Supports Arabic (RTL) and English (LTR)
// Generated localization files using Flutter's intl package

import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

/// Supported locales for the SAHOOL application
class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  /// Helper method to access AppLocalizations from BuildContext
  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  /// Supported locales
  static const List<Locale> supportedLocales = [
    Locale('ar', ''), // Arabic (primary language for Yemen)
    Locale('en', ''), // English
  ];

  /// Default locale (Arabic for Yemen)
  static const Locale defaultLocale = Locale('ar', '');

  /// Localization delegates
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates = [
    AppLocalizationsDelegate(),
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ];

  /// Locale resolution callback
  static Locale localeResolutionCallback(
    Locale? locale,
    Iterable<Locale> supportedLocales,
  ) {
    // Check if the current device locale is supported
    if (locale != null) {
      for (var supportedLocale in supportedLocales) {
        if (supportedLocale.languageCode == locale.languageCode) {
          return supportedLocale;
        }
      }
    }
    // Default to Arabic for Yemen
    return defaultLocale;
  }

  /// Check if current locale is RTL (Right-to-Left)
  bool get isRTL => locale.languageCode == 'ar';

  /// Get text direction based on locale
  TextDirection get textDirection => isRTL ? TextDirection.rtl : TextDirection.ltr;

  /// Get current language name
  String get languageName {
    switch (locale.languageCode) {
      case 'ar':
        return 'العربية';
      case 'en':
        return 'English';
      default:
        return 'العربية';
    }
  }

  /// Get current language code
  String get languageCode => locale.languageCode;
}

/// AppLocalizations Delegate
class AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return AppLocalizations.supportedLocales
        .any((l) => l.languageCode == locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) {
    // Return a SynchronousFuture to avoid async overhead
    return SynchronousFuture<AppLocalizations>(AppLocalizations(locale));
  }

  @override
  bool shouldReload(AppLocalizationsDelegate old) => false;
}

/// Extension to easily access localization from BuildContext
extension LocalizationExtension on BuildContext {
  /// Get AppLocalizations instance
  AppLocalizations? get l10n => AppLocalizations.of(this);

  /// Get current locale
  Locale get currentLocale => Localizations.localeOf(this);

  /// Check if current locale is RTL
  bool get isRTL => Localizations.localeOf(this).languageCode == 'ar';

  /// Get text direction
  TextDirection get textDirection =>
      isRTL ? TextDirection.rtl : TextDirection.ltr;
}

/// Locale Provider for state management
class LocaleProvider extends ChangeNotifier {
  Locale _locale = AppLocalizations.defaultLocale;

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
      setLocale(const Locale('en', ''));
    } else {
      setLocale(const Locale('ar', ''));
    }
  }

  /// Set Arabic locale
  void setArabic() {
    setLocale(const Locale('ar', ''));
  }

  /// Set English locale
  void setEnglish() {
    setLocale(const Locale('en', ''));
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
      return EdgeInsets.symmetric(horizontal: horizontal, vertical: vertical ?? 0);
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

  /// Get appropriate TextAlign based on text direction
  TextAlign get defaultTextAlign => context.isRTL ? TextAlign.right : TextAlign.left;

  /// Get appropriate TextAlign (start)
  TextAlign get startAlign => context.isRTL ? TextAlign.right : TextAlign.left;

  /// Get appropriate TextAlign (end)
  TextAlign get endAlign => context.isRTL ? TextAlign.left : TextAlign.right;
}

/// Format numbers according to locale
class LocalizedNumberFormat {
  final Locale locale;

  LocalizedNumberFormat(this.locale);

  /// Format number with appropriate separators
  String format(num number, {int? decimalDigits}) {
    final isArabic = locale.languageCode == 'ar';

    if (decimalDigits != null) {
      final formatted = number.toStringAsFixed(decimalDigits);
      return isArabic ? _toArabicDigits(formatted) : formatted;
    }

    final formatted = number.toString();
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

  /// Format currency for Yemen (Yemeni Rial)
  String formatCurrency(num amount, {String? currencySymbol}) {
    final symbol = currencySymbol ?? 'ريال';
    final formatted = format(amount, decimalDigits: 2);

    if (locale.languageCode == 'ar') {
      return '$formatted $symbol';
    } else {
      return '$symbol$formatted';
    }
  }

  /// Format percentage
  String formatPercentage(num value, {int decimalDigits = 1}) {
    final formatted = format(value, decimalDigits: decimalDigits);
    return locale.languageCode == 'ar' ? '%$formatted' : '$formatted%';
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
    Key? key,
    this.size,
    this.color,
    this.flipForRTL = true,
  }) : super(key: key);

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
