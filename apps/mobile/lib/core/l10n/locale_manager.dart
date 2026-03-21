/// SAHOOL Locale Manager
/// مدير اللغة والترجمة
///
/// Features:
/// - Locale switching (AR/EN)
/// - RTL/LTR support
/// - Number and date formatting
/// - Pluralization helpers
/// - Islamic calendar support
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart' hide TextDirection;
import 'package:shared_preferences/shared_preferences.dart';

// =============================================================================
// Locale State - حالة اللغة
// =============================================================================

/// Current locale state
/// حالة اللغة الحالية
class LocaleState {
  final Locale locale;
  final bool isRTL;
  final String languageCode;

  const LocaleState({
    required this.locale,
    required this.isRTL,
    required this.languageCode,
  });

  factory LocaleState.arabic() => const LocaleState(
        locale: Locale('ar'),
        isRTL: true,
        languageCode: 'ar',
      );

  factory LocaleState.english() => const LocaleState(
        locale: Locale('en'),
        isRTL: false,
        languageCode: 'en',
      );

  bool get isArabic => languageCode == 'ar';
  bool get isEnglish => languageCode == 'en';

  TextDirection get textDirection =>
      isRTL ? TextDirection.rtl : TextDirection.ltr;
}

// =============================================================================
// Locale Provider - مزود اللغة
// =============================================================================

/// Locale state notifier provider
/// مزود إدارة حالة اللغة
final localeProvider =
    NotifierProvider<LocaleNotifier, LocaleState>(LocaleNotifier.new);

class LocaleNotifier extends Notifier<LocaleState> {
  static const String _localeKey = 'app_locale';

  @override
  LocaleState build() {
    _loadSavedLocale();
    return LocaleState.arabic(); // Default to Arabic
  }

  Future<void> _loadSavedLocale() async {
    final prefs = await SharedPreferences.getInstance();
    final savedLocale = prefs.getString(_localeKey);

    if (savedLocale == 'en') {
      state = LocaleState.english();
    } else {
      state = LocaleState.arabic();
    }
  }

  /// Switch to Arabic
  /// التبديل إلى العربية
  Future<void> switchToArabic() async {
    state = LocaleState.arabic();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_localeKey, 'ar');
  }

  /// Switch to English
  /// التبديل إلى الإنجليزية
  Future<void> switchToEnglish() async {
    state = LocaleState.english();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_localeKey, 'en');
  }

  /// Toggle between languages
  /// التبديل بين اللغات
  Future<void> toggleLocale() async {
    if (state.isArabic) {
      await switchToEnglish();
    } else {
      await switchToArabic();
    }
  }

  /// Set specific locale
  /// تعيين لغة محددة
  Future<void> setLocale(String languageCode) async {
    if (languageCode == 'en') {
      await switchToEnglish();
    } else {
      await switchToArabic();
    }
  }
}

// =============================================================================
// Number Formatting - تنسيق الأرقام
// =============================================================================

/// Number formatting utilities
/// أدوات تنسيق الأرقام
class NumberFormatter {
  final String locale;

  NumberFormatter(this.locale);

  /// Format number with thousand separators
  /// تنسيق رقم مع فواصل الآلاف
  String format(num number, {int decimalDigits = 0}) {
    final formatter = NumberFormat.decimalPattern(locale);
    formatter.minimumFractionDigits = decimalDigits;
    formatter.maximumFractionDigits = decimalDigits;
    return formatter.format(number);
  }

  /// Format as currency (SAR)
  /// تنسيق كعملة (ريال سعودي)
  String formatCurrency(num amount, {String symbol = 'ر.س'}) {
    final formatted = format(amount, decimalDigits: 2);
    if (locale == 'ar') {
      return '$formatted $symbol';
    }
    return '$symbol $formatted';
  }

  /// Format as percentage
  /// تنسيق كنسبة مئوية
  String formatPercent(num value, {int decimalDigits = 0}) {
    final formatter = NumberFormat.percentPattern(locale);
    formatter.minimumFractionDigits = decimalDigits;
    formatter.maximumFractionDigits = decimalDigits;
    return formatter.format(value / 100);
  }

  /// Format area (hectares)
  /// تنسيق المساحة (هكتار)
  String formatArea(num hectares) {
    final formatted = format(hectares, decimalDigits: 2);
    if (locale == 'ar') {
      return '$formatted هكتار';
    }
    return '$formatted ha';
  }

  /// Format weight (kg)
  /// تنسيق الوزن (كجم)
  String formatWeight(num kilograms) {
    final formatted = format(kilograms, decimalDigits: 1);
    if (locale == 'ar') {
      return '$formatted كجم';
    }
    return '$formatted kg';
  }

  /// Format distance (km)
  /// تنسيق المسافة (كم)
  String formatDistance(num kilometers) {
    final formatted = format(kilometers, decimalDigits: 1);
    if (locale == 'ar') {
      return '$formatted كم';
    }
    return '$formatted km';
  }

  /// Convert to Arabic numerals
  /// تحويل إلى أرقام عربية
  String toArabicNumerals(String number) {
    const english = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
    const arabic = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];

    var result = number;
    for (var i = 0; i < english.length; i++) {
      result = result.replaceAll(english[i], arabic[i]);
    }
    return result;
  }
}

// =============================================================================
// Date Formatting - تنسيق التاريخ
// =============================================================================

/// Date formatting utilities
/// أدوات تنسيق التاريخ
class DateFormatter {
  final String locale;

  DateFormatter(this.locale);

  /// Format full date
  /// تنسيق التاريخ الكامل
  String formatFull(DateTime date) {
    return DateFormat.yMMMMEEEEd(locale).format(date);
  }

  /// Format short date
  /// تنسيق تاريخ قصير
  String formatShort(DateTime date) {
    return DateFormat.yMd(locale).format(date);
  }

  /// Format time
  /// تنسيق الوقت
  String formatTime(DateTime date) {
    return DateFormat.jm(locale).format(date);
  }

  /// Format date and time
  /// تنسيق التاريخ والوقت
  String formatDateTime(DateTime date) {
    return DateFormat.yMd(locale).add_jm().format(date);
  }

  /// Format relative time (e.g., "2 hours ago")
  /// تنسيق الوقت النسبي (مثل "منذ ساعتين")
  String formatRelative(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inMinutes < 1) {
      return locale == 'ar' ? 'الآن' : 'just now';
    }

    if (diff.inMinutes < 60) {
      final minutes = diff.inMinutes;
      if (locale == 'ar') {
        return 'منذ ${_pluralizeArabic(minutes, 'دقيقة', 'دقيقتين', 'دقائق')}';
      }
      return '$minutes ${minutes == 1 ? 'minute' : 'minutes'} ago';
    }

    if (diff.inHours < 24) {
      final hours = diff.inHours;
      if (locale == 'ar') {
        return 'منذ ${_pluralizeArabic(hours, 'ساعة', 'ساعتين', 'ساعات')}';
      }
      return '$hours ${hours == 1 ? 'hour' : 'hours'} ago';
    }

    if (diff.inDays < 7) {
      final days = diff.inDays;
      if (locale == 'ar') {
        return 'منذ ${_pluralizeArabic(days, 'يوم', 'يومين', 'أيام')}';
      }
      return '$days ${days == 1 ? 'day' : 'days'} ago';
    }

    if (diff.inDays < 30) {
      final weeks = (diff.inDays / 7).floor();
      if (locale == 'ar') {
        return 'منذ ${_pluralizeArabic(weeks, 'أسبوع', 'أسبوعين', 'أسابيع')}';
      }
      return '$weeks ${weeks == 1 ? 'week' : 'weeks'} ago';
    }

    return formatShort(date);
  }

  /// Format day name
  /// تنسيق اسم اليوم
  String formatDayName(DateTime date) {
    return DateFormat.EEEE(locale).format(date);
  }

  /// Format month name
  /// تنسيق اسم الشهر
  String formatMonthName(DateTime date) {
    return DateFormat.MMMM(locale).format(date);
  }

  /// Get Hijri month names
  /// الحصول على أسماء الأشهر الهجرية
  static String getHijriMonthName(int month, String locale) {
    const arabicMonths = [
      'محرم',
      'صفر',
      'ربيع الأول',
      'ربيع الثاني',
      'جمادى الأولى',
      'جمادى الآخرة',
      'رجب',
      'شعبان',
      'رمضان',
      'شوال',
      'ذو القعدة',
      'ذو الحجة',
    ];

    const englishMonths = [
      'Muharram',
      'Safar',
      'Rabi\' al-Awwal',
      'Rabi\' al-Thani',
      'Jumada al-Awwal',
      'Jumada al-Thani',
      'Rajab',
      'Sha\'ban',
      'Ramadan',
      'Shawwal',
      'Dhu al-Qi\'dah',
      'Dhu al-Hijjah',
    ];

    if (month < 1 || month > 12) return '';

    return locale == 'ar' ? arabicMonths[month - 1] : englishMonths[month - 1];
  }

  String _pluralizeArabic(int count, String singular, String dual, String plural) {
    if (count == 1) return singular;
    if (count == 2) return dual;
    if (count >= 3 && count <= 10) return '$count $plural';
    return '$count $singular';
  }
}

// =============================================================================
// Pluralization - صيغ الجمع
// =============================================================================

/// Pluralization utilities
/// أدوات صيغ الجمع
class Pluralizer {
  final String locale;

  Pluralizer(this.locale);

  /// Pluralize based on count (Arabic)
  /// تحديد صيغة الجمع بناءً على العدد (عربي)
  String pluralize({
    required int count,
    required String singular,
    String? dual,
    required String plural,
    String? zeroForm,
  }) {
    if (locale != 'ar') {
      // English pluralization
      if (count == 0 && zeroForm != null) return zeroForm;
      return count == 1 ? singular : plural;
    }

    // Arabic pluralization rules
    if (count == 0) return zeroForm ?? plural;
    if (count == 1) return singular;
    if (count == 2) return dual ?? plural;
    if (count >= 3 && count <= 10) return plural;
    return singular; // For 11+, use singular form with the number
  }

  /// Common agricultural terms pluralization
  /// صيغ جمع المصطلحات الزراعية الشائعة
  String fields(int count) => pluralize(
        count: count,
        singular: locale == 'ar' ? 'حقل' : 'field',
        dual: locale == 'ar' ? 'حقلان' : null,
        plural: locale == 'ar' ? 'حقول' : 'fields',
        zeroForm: locale == 'ar' ? 'لا توجد حقول' : 'no fields',
      );

  String tasks(int count) => pluralize(
        count: count,
        singular: locale == 'ar' ? 'مهمة' : 'task',
        dual: locale == 'ar' ? 'مهمتان' : null,
        plural: locale == 'ar' ? 'مهام' : 'tasks',
        zeroForm: locale == 'ar' ? 'لا توجد مهام' : 'no tasks',
      );

  String notifications(int count) => pluralize(
        count: count,
        singular: locale == 'ar' ? 'إشعار' : 'notification',
        dual: locale == 'ar' ? 'إشعاران' : null,
        plural: locale == 'ar' ? 'إشعارات' : 'notifications',
        zeroForm: locale == 'ar' ? 'لا توجد إشعارات' : 'no notifications',
      );

  String crops(int count) => pluralize(
        count: count,
        singular: locale == 'ar' ? 'محصول' : 'crop',
        dual: locale == 'ar' ? 'محصولان' : null,
        plural: locale == 'ar' ? 'محاصيل' : 'crops',
      );

  String days(int count) => pluralize(
        count: count,
        singular: locale == 'ar' ? 'يوم' : 'day',
        dual: locale == 'ar' ? 'يومان' : null,
        plural: locale == 'ar' ? 'أيام' : 'days',
      );

  String hours(int count) => pluralize(
        count: count,
        singular: locale == 'ar' ? 'ساعة' : 'hour',
        dual: locale == 'ar' ? 'ساعتان' : null,
        plural: locale == 'ar' ? 'ساعات' : 'hours',
      );

  String minutes(int count) => pluralize(
        count: count,
        singular: locale == 'ar' ? 'دقيقة' : 'minute',
        dual: locale == 'ar' ? 'دقيقتان' : null,
        plural: locale == 'ar' ? 'دقائق' : 'minutes',
      );
}

// =============================================================================
// Locale Helpers Extension - إضافات مساعدة اللغة
// =============================================================================

/// Extension on WidgetRef for easy locale access
/// إضافة على WidgetRef للوصول السهل إلى اللغة
extension LocaleExtension on WidgetRef {
  LocaleState get locale => watch(localeProvider);
  LocaleNotifier get localeNotifier => read(localeProvider.notifier);

  NumberFormatter get numberFormatter => NumberFormatter(locale.languageCode);
  DateFormatter get dateFormatter => DateFormatter(locale.languageCode);
  Pluralizer get pluralizer => Pluralizer(locale.languageCode);

  bool get isArabic => locale.isArabic;
  bool get isEnglish => locale.isEnglish;
  bool get isRTL => locale.isRTL;
  TextDirection get textDirection => locale.textDirection;
}

/// Extension on BuildContext for locale access
/// إضافة على BuildContext للوصول إلى اللغة
extension LocaleContextExtension on BuildContext {
  bool get isRTL => Directionality.of(this) == TextDirection.rtl;

  /// Get current locale from Localizations
  String get currentLocale {
    return Localizations.localeOf(this).languageCode;
  }

  NumberFormatter get numberFormatter => NumberFormatter(currentLocale);
  DateFormatter get dateFormatter => DateFormatter(currentLocale);
  Pluralizer get pluralizer => Pluralizer(currentLocale);
}

// =============================================================================
// Language Switcher Widget - مكون تبديل اللغة
// =============================================================================

/// Widget for switching between AR/EN
/// مكون للتبديل بين العربية والإنجليزية
class LanguageSwitcher extends ConsumerWidget {
  final bool showLabel;
  final bool compact;

  const LanguageSwitcher({
    super.key,
    this.showLabel = true,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final locale = ref.watch(localeProvider);

    if (compact) {
      return IconButton(
        onPressed: () => ref.read(localeProvider.notifier).toggleLocale(),
        icon: Text(
          locale.isArabic ? 'EN' : 'ع',
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        tooltip: locale.isArabic ? 'Switch to English' : 'التبديل إلى العربية',
      );
    }

    return GestureDetector(
      onTap: () => ref.read(localeProvider.notifier).toggleLocale(),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.grey.shade200,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                color: locale.isArabic ? Colors.green : Colors.transparent,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Center(
                child: Text(
                  'ع',
                  style: TextStyle(
                    color: locale.isArabic ? Colors.white : Colors.grey,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                color: locale.isEnglish ? Colors.green : Colors.transparent,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Center(
                child: Text(
                  'EN',
                  style: TextStyle(
                    color: locale.isEnglish ? Colors.white : Colors.grey,
                    fontWeight: FontWeight.bold,
                    fontSize: 10,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
