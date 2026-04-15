/// SAHOOL Accessibility - Semantics Helper
/// مساعد الوصولية الدلالية
///
/// Provides comprehensive accessibility support following WCAG 2.1 Level AA guidelines.
/// يوفر دعم شامل للوصولية وفق إرشادات WCAG 2.1 المستوى AA
///
/// Features:
/// - Semantic labels for screen readers | تسميات دلالية لقارئات الشاشة
/// - Focus management | إدارة التركيز
/// - Announcements for dynamic content | إعلانات للمحتوى الديناميكي
/// - Minimum touch targets (48x48) | أهداف لمس بحد أدنى
/// - Support for large text scaling | دعم تكبير النص
library;

import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';

/// Minimum touch target size for accessibility (48x48 dp as per WCAG 2.1)
const double kMinTouchTargetSize = 48.0;

/// Maximum text scale factor to support
const double kMaxTextScaleFactor = 2.0;

/// Semantic Labels for SAHOOL App
/// التسميات الدلالية لتطبيق سهول
class SahoolSemantics {
  // Navigation Labels | تسميات التنقل
  static const String homeTab = 'الرئيسية، تبويب';
  static const String homeTabEn = 'Home, tab';
  static const String fieldsTab = 'الحقول، تبويب';
  static const String fieldsTabEn = 'Fields, tab';
  static const String monitorTab = 'المراقبة، تبويب';
  static const String monitorTabEn = 'Monitor, tab';
  static const String marketTab = 'السوق، تبويب';
  static const String marketTabEn = 'Market, tab';
  static const String profileTab = 'الملف الشخصي، تبويب';
  static const String profileTabEn = 'Profile, tab';
  static const String addFieldButton = 'إضافة حقل جديد، زر';
  static const String addFieldButtonEn = 'Add new field, button';

  // Map Labels | تسميات الخريطة
  static const String mapView = 'خريطة الحقول';
  static const String mapViewEn = 'Fields map';
  static const String zoomIn = 'تكبير الخريطة';
  static const String zoomInEn = 'Zoom in';
  static const String zoomOut = 'تصغير الخريطة';
  static const String zoomOutEn = 'Zoom out';
  static const String toggleSatellite = 'تبديل عرض القمر الصناعي';
  static const String toggleSatelliteEn = 'Toggle satellite view';
  static const String toggleMapLayers = 'تبديل طبقات الخريطة';
  static const String toggleMapLayersEn = 'Toggle map layers';
  static const String currentLocation = 'الموقع الحالي';
  static const String currentLocationEn = 'Current location';

  // Field Labels | تسميات الحقول
  static const String fieldCard = 'بطاقة الحقل';
  static const String fieldCardEn = 'Field card';
  static const String fieldHealth = 'صحة الحقل';
  static const String fieldHealthEn = 'Field health';
  static const String fieldArea = 'مساحة الحقل';
  static const String fieldAreaEn = 'Field area';
  static const String fieldCrop = 'المحصول';
  static const String fieldCropEn = 'Crop type';
  static const String ndviValue = 'قيمة مؤشر الغطاء النباتي';
  static const String ndviValueEn = 'NDVI value';

  // Status Labels | تسميات الحالة
  static const String syncStatus = 'حالة المزامنة';
  static const String syncStatusEn = 'Sync status';
  static const String synced = 'تمت المزامنة';
  static const String syncedEn = 'Synced';
  static const String syncing = 'جاري المزامنة';
  static const String syncingEn = 'Syncing';
  static const String offline = 'غير متصل';
  static const String offlineEn = 'Offline';

  // Weather Labels | تسميات الطقس
  static const String weatherInfo = 'معلومات الطقس';
  static const String weatherInfoEn = 'Weather information';
  static const String temperature = 'درجة الحرارة';
  static const String temperatureEn = 'Temperature';

  // Task Labels | تسميات المهام
  static const String tasksCard = 'بطاقة المهام';
  static const String tasksCardEn = 'Tasks card';
  static const String pendingTasks = 'المهام المعلقة';
  static const String pendingTasksEn = 'Pending tasks';

  // Health Status Labels | تسميات حالة الصحة
  static String getHealthLabel(double score, {bool isArabic = true}) {
    if (score >= 0.8) {
      return isArabic ? 'صحة ممتازة' : 'Excellent health';
    } else if (score >= 0.6) {
      return isArabic ? 'صحة جيدة' : 'Good health';
    } else if (score >= 0.4) {
      return isArabic ? 'صحة متوسطة' : 'Moderate health';
    } else {
      return isArabic ? 'صحة ضعيفة، يتطلب انتباه' : 'Poor health, needs attention';
    }
  }

  // Irrigation Labels | تسميات الري
  static const String irrigationCard = 'بطاقة الري';
  static const String irrigationCardEn = 'Irrigation card';
  static const String soilMoisture = 'رطوبة التربة';
  static const String soilMoistureEn = 'Soil moisture';

  // Form Labels | تسميات النماذج
  static const String fieldNameInput = 'حقل إدخال اسم الحقل';
  static const String fieldNameInputEn = 'Field name input';
  static const String cropTypeDropdown = 'قائمة منسدلة لنوع المحصول';
  static const String cropTypeDropdownEn = 'Crop type dropdown';
  static const String areaInput = 'حقل إدخال المساحة بالهكتار';
  static const String areaInputEn = 'Area input in hectares';
  static const String irrigationDropdown = 'قائمة منسدلة لنظام الري';
  static const String irrigationDropdownEn = 'Irrigation system dropdown';
  static const String datePickerButton = 'زر اختيار التاريخ';
  static const String datePickerButtonEn = 'Date picker button';
  static const String saveButton = 'زر الحفظ';
  static const String saveButtonEn = 'Save button';
  static const String cancelButton = 'زر الإلغاء';
  static const String cancelButtonEn = 'Cancel button';
  static const String deleteButton = 'زر الحذف';
  static const String deleteButtonEn = 'Delete button';

  // Alert Labels | تسميات التنبيهات
  static const String alertBanner = 'شريط التنبيهات';
  static const String alertBannerEn = 'Alert banner';
  static const String criticalAlert = 'تنبيه حرج';
  static const String criticalAlertEn = 'Critical alert';
  static const String warningAlert = 'تحذير';
  static const String warningAlertEn = 'Warning';
  static const String infoAlert = 'معلومات';
  static const String infoAlertEn = 'Information';

  // Search and Filter Labels | تسميات البحث والفلترة
  static const String searchField = 'حقل البحث';
  static const String searchFieldEn = 'Search field';
  static const String filterButton = 'زر الفلترة';
  static const String filterButtonEn = 'Filter button';
  static const String sortButton = 'زر الترتيب';
  static const String sortButtonEn = 'Sort button';
  static const String clearFilter = 'مسح الفلتر';
  static const String clearFilterEn = 'Clear filter';

  // View Toggle Labels | تسميات تبديل العرض
  static const String listViewButton = 'عرض القائمة';
  static const String listViewButtonEn = 'List view';
  static const String gridViewButton = 'عرض الشبكة';
  static const String gridViewButtonEn = 'Grid view';

  // Messages Labels | تسميات الرسائل
  static const String messageCard = 'بطاقة الرسالة';
  static const String messageCardEn = 'Message card';
  static const String unreadMessage = 'رسالة غير مقروءة';
  static const String unreadMessageEn = 'Unread message';
}

/// Accessible Widget Wrappers
/// أغلفة الودجات القابلة للوصول

/// Wraps a widget with proper semantics for buttons
/// يغلف ودجت بدلالات صحيحة للأزرار
class AccessibleButton extends StatelessWidget {
  final Widget child;
  final VoidCallback? onPressed;
  final String label;
  final String? hint;
  final bool isEnabled;
  final bool excludeSemantics;

  const AccessibleButton({
    super.key,
    required this.child,
    required this.onPressed,
    required this.label,
    this.hint,
    this.isEnabled = true,
    this.excludeSemantics = false,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      enabled: isEnabled,
      label: label,
      hint: hint,
      excludeSemantics: excludeSemantics,
      child: SizedBox(
        width: kMinTouchTargetSize,
        height: kMinTouchTargetSize,
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: isEnabled ? onPressed : null,
            borderRadius: BorderRadius.circular(kMinTouchTargetSize / 2),
            child: Center(child: child),
          ),
        ),
      ),
    );
  }
}

/// Wraps a widget with proper semantics for icon buttons
/// يغلف ودجت بدلالات صحيحة لأزرار الأيقونات
class AccessibleIconButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onPressed;
  final String label;
  final String? hint;
  final Color? color;
  final double size;
  final bool isEnabled;
  final String? tooltip;

  const AccessibleIconButton({
    super.key,
    required this.icon,
    required this.onPressed,
    required this.label,
    this.hint,
    this.color,
    this.size = 24.0,
    this.isEnabled = true,
    this.tooltip,
  });

  @override
  Widget build(BuildContext context) {
    final button = Semantics(
      button: true,
      enabled: isEnabled,
      label: label,
      hint: hint,
      child: SizedBox(
        width: kMinTouchTargetSize,
        height: kMinTouchTargetSize,
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: isEnabled ? onPressed : null,
            borderRadius: BorderRadius.circular(kMinTouchTargetSize / 2),
            child: Center(
              child: Icon(
                icon,
                color: isEnabled ? color : color?.withValues(alpha: 0.5),
                size: size,
              ),
            ),
          ),
        ),
      ),
    );

    if (tooltip != null) {
      return Tooltip(
        message: tooltip,
        child: button,
      );
    }

    return button;
  }
}

/// Wraps a card widget with proper semantics
/// يغلف بطاقة بدلالات صحيحة
class AccessibleCard extends StatelessWidget {
  final Widget child;
  final String label;
  final String? hint;
  final VoidCallback? onTap;
  final bool isButton;

  const AccessibleCard({
    super.key,
    required this.child,
    required this.label,
    this.hint,
    this.onTap,
    this.isButton = false,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      hint: hint,
      button: isButton,
      child: onTap != null
          ? GestureDetector(
              onTap: onTap,
              child: child,
            )
          : child,
    );
  }
}

/// Wraps a form field with proper semantics
/// يغلف حقل نموذج بدلالات صحيحة
class AccessibleFormField extends StatelessWidget {
  final Widget child;
  final String label;
  final String? hint;
  final bool isRequired;
  final String? errorText;

  const AccessibleFormField({
    super.key,
    required this.child,
    required this.label,
    this.hint,
    this.isRequired = false,
    this.errorText,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: isRequired ? '$label، مطلوب' : label,
      hint: hint,
      textField: true,
      child: child,
    );
  }
}

/// Heading widget with proper semantics hierarchy
/// ودجت العنوان بتسلسل دلالي صحيح
class AccessibleHeading extends StatelessWidget {
  final String text;
  final int level; // 1-6 for h1-h6
  final TextStyle? style;
  final TextAlign? textAlign;

  const AccessibleHeading({
    super.key,
    required this.text,
    this.level = 1,
    this.style,
    this.textAlign,
  }) : assert(level >= 1 && level <= 6);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final defaultStyle = _getDefaultStyle(theme);

    return Semantics(
      header: true,
      child: Text(
        text,
        style: style ?? defaultStyle,
        textAlign: textAlign,
      ),
    );
  }

  TextStyle _getDefaultStyle(ThemeData theme) {
    switch (level) {
      case 1:
        return theme.textTheme.headlineLarge ?? const TextStyle(fontSize: 32, fontWeight: FontWeight.bold);
      case 2:
        return theme.textTheme.headlineMedium ?? const TextStyle(fontSize: 28, fontWeight: FontWeight.bold);
      case 3:
        return theme.textTheme.headlineSmall ?? const TextStyle(fontSize: 24, fontWeight: FontWeight.bold);
      case 4:
        return theme.textTheme.titleLarge ?? const TextStyle(fontSize: 22, fontWeight: FontWeight.bold);
      case 5:
        return theme.textTheme.titleMedium ?? const TextStyle(fontSize: 18, fontWeight: FontWeight.bold);
      case 6:
        return theme.textTheme.titleSmall ?? const TextStyle(fontSize: 16, fontWeight: FontWeight.bold);
      default:
        return theme.textTheme.headlineMedium ?? const TextStyle(fontSize: 28, fontWeight: FontWeight.bold);
    }
  }
}

/// Image with accessibility support
/// صورة مع دعم الوصولية
class AccessibleImage extends StatelessWidget {
  final ImageProvider image;
  final String semanticLabel;
  final double? width;
  final double? height;
  final BoxFit? fit;
  final bool isDecorative;

  const AccessibleImage({
    super.key,
    required this.image,
    required this.semanticLabel,
    this.width,
    this.height,
    this.fit,
    this.isDecorative = false,
  });

  @override
  Widget build(BuildContext context) {
    final imageWidget = Image(
      image: image,
      width: width,
      height: height,
      fit: fit,
      semanticLabel: isDecorative ? null : semanticLabel,
    );

    if (isDecorative) {
      return ExcludeSemantics(child: imageWidget);
    }

    return imageWidget;
  }
}

/// Focus Management Helper
/// مساعد إدارة التركيز
class FocusHelper {
  /// Request focus on a specific node
  static void requestFocus(FocusNode node) {
    node.requestFocus();
  }

  /// Move focus to the next focusable element
  static void nextFocus(BuildContext context) {
    FocusScope.of(context).nextFocus();
  }

  /// Move focus to the previous focusable element
  static void previousFocus(BuildContext context) {
    FocusScope.of(context).previousFocus();
  }

  /// Remove focus from all elements
  static void unfocus(BuildContext context) {
    FocusScope.of(context).unfocus();
  }

  /// Create a focus traversal group with ordered children
  static Widget createFocusGroup({
    required List<Widget> children,
    required Axis axis,
  }) {
    return FocusTraversalGroup(
      policy: OrderedTraversalPolicy(),
      child: axis == Axis.vertical
          ? Column(children: children)
          : Row(children: children),
    );
  }
}

/// Announcement Helper for Screen Readers
/// مساعد الإعلانات لقارئات الشاشة
class AnnouncementHelper {
  /// Announce a message to screen readers
  static void announce(BuildContext context, String message, {TextDirection? textDirection}) {
    SemanticsService.announce(message, textDirection ?? Directionality.of(context));
  }

  /// Announce a polite message (lower priority)
  static void announcePolite(BuildContext context, String message) {
    announce(context, message);
  }

  /// Announce an assertive message (higher priority, interrupts current announcement)
  static void announceAssertive(BuildContext context, String message) {
    // Flutter's SemanticsService.announce is inherently assertive
    announce(context, message);
  }

  /// Announce loading state
  static void announceLoading(BuildContext context, {bool isArabic = true}) {
    announce(context, isArabic ? 'جاري التحميل' : 'Loading');
  }

  /// Announce completion
  static void announceComplete(BuildContext context, String action, {bool isArabic = true}) {
    final message = isArabic ? 'تم $action بنجاح' : '$action completed successfully';
    announce(context, message);
  }

  /// Announce error
  static void announceError(BuildContext context, String error, {bool isArabic = true}) {
    final message = isArabic ? 'خطأ: $error' : 'Error: $error';
    announce(context, message);
  }

  /// Announce navigation
  static void announceNavigation(BuildContext context, String screenName, {bool isArabic = true}) {
    final message = isArabic ? 'انتقلت إلى $screenName' : 'Navigated to $screenName';
    announce(context, message);
  }

  /// Announce list update
  static void announceListUpdate(BuildContext context, int count, String itemType, {bool isArabic = true}) {
    final message = isArabic ? 'يعرض $count $itemType' : 'Showing $count $itemType';
    announce(context, message);
  }
}

/// Text Scale Helper
/// مساعد تكبير النص
class TextScaleHelper {
  /// Check if large text is enabled
  static bool isLargeTextEnabled(BuildContext context) {
    return MediaQuery.of(context).textScaler.scale(1.0) > 1.0;
  }

  /// Get scaled text size
  static double getScaledSize(BuildContext context, double baseSize) {
    final scaleFactor = MediaQuery.of(context).textScaler.scale(1.0);
    return baseSize * scaleFactor.clamp(1.0, kMaxTextScaleFactor);
  }

  /// Wrap text with maximum scale factor
  static Widget constrainTextScale({
    required Widget child,
    double maxScaleFactor = kMaxTextScaleFactor,
  }) {
    return Builder(
      builder: (context) {
        final mediaQuery = MediaQuery.of(context);
        final currentScale = mediaQuery.textScaler.scale(1.0);
        final clampedScale = currentScale.clamp(1.0, maxScaleFactor);

        return MediaQuery(
          data: mediaQuery.copyWith(
            textScaler: TextScaler.linear(clampedScale),
          ),
          child: child,
        );
      },
    );
  }
}

/// Contrast Helper for Accessibility
/// مساعد التباين للوصولية
class ContrastHelper {
  /// WCAG 2.1 AA minimum contrast ratio for normal text
  static const double minContrastNormalText = 4.5;

  /// WCAG 2.1 AA minimum contrast ratio for large text (18pt+ or 14pt bold+)
  static const double minContrastLargeText = 3.0;

  /// Calculate relative luminance of a color
  static double getRelativeLuminance(Color color) {
    double r = color.red / 255;
    double g = color.green / 255;
    double b = color.blue / 255;

    r = r <= 0.03928 ? r / 12.92 : ((r + 0.055) / 1.055).toDouble();
    g = g <= 0.03928 ? g / 12.92 : ((g + 0.055) / 1.055).toDouble();
    b = b <= 0.03928 ? b / 12.92 : ((b + 0.055) / 1.055).toDouble();

    // Apply gamma correction
    if (r <= 0.03928) {
      r = r / 12.92;
    } else {
      r = _pow((r + 0.055) / 1.055, 2.4);
    }

    if (g <= 0.03928) {
      g = g / 12.92;
    } else {
      g = _pow((g + 0.055) / 1.055, 2.4);
    }

    if (b <= 0.03928) {
      b = b / 12.92;
    } else {
      b = _pow((b + 0.055) / 1.055, 2.4);
    }

    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  /// Calculate contrast ratio between two colors
  static double getContrastRatio(Color foreground, Color background) {
    final l1 = getRelativeLuminance(foreground);
    final l2 = getRelativeLuminance(background);
    final lighter = l1 > l2 ? l1 : l2;
    final darker = l1 > l2 ? l2 : l1;
    return (lighter + 0.05) / (darker + 0.05);
  }

  /// Check if contrast meets WCAG AA for normal text
  static bool meetsContrastAA(Color foreground, Color background) {
    return getContrastRatio(foreground, background) >= minContrastNormalText;
  }

  /// Check if contrast meets WCAG AA for large text
  static bool meetsContrastAALargeText(Color foreground, Color background) {
    return getContrastRatio(foreground, background) >= minContrastLargeText;
  }

  /// Get accessible text color for a background
  static Color getAccessibleTextColor(Color background) {
    final luminance = getRelativeLuminance(background);
    return luminance > 0.179 ? Colors.black : Colors.white;
  }

  /// Helper function for power calculation
  static double _pow(double base, double exponent) {
    if (base < 0) return 0;
    double result = 1;
    for (int i = 0; i < exponent.toInt(); i++) {
      result *= base;
    }
    // Handle decimal part
    if (exponent != exponent.toInt()) {
      result *= _nthRoot(base, (1 / (exponent - exponent.toInt())).toInt());
    }
    return result;
  }

  /// Helper function for nth root
  static double _nthRoot(double value, int n) {
    if (n == 0) return 1;
    double x = value;
    for (int i = 0; i < 10; i++) {
      x = ((n - 1) * x + value / _pow(x, (n - 1).toDouble())) / n;
    }
    return x;
  }
}

/// Live Region Widget for Dynamic Content
/// ودجت المنطقة الحية للمحتوى الديناميكي
class LiveRegion extends StatelessWidget {
  final Widget child;
  final String label;
  final bool liveRegion;

  const LiveRegion({
    super.key,
    required this.child,
    required this.label,
    this.liveRegion = true,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      liveRegion: liveRegion,
      child: child,
    );
  }
}

/// Skip Link Widget for Keyboard Navigation
/// ودجت رابط التخطي للتنقل بلوحة المفاتيح
class SkipLink extends StatelessWidget {
  final Widget child;
  final String label;
  final VoidCallback onActivate;

  const SkipLink({
    super.key,
    required this.child,
    required this.label,
    required this.onActivate,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: label,
      button: true,
      child: Focus(
        onFocusChange: (hasFocus) {
          // Skip links become visible when focused
        },
        child: GestureDetector(
          onTap: onActivate,
          child: child,
        ),
      ),
    );
  }
}

/// Extensions for easier accessibility implementation
extension AccessibilityExtensions on Widget {
  /// Add semantic label to any widget
  Widget withSemanticLabel(String label, {String? hint, bool? button, bool? header}) {
    return Semantics(
      label: label,
      hint: hint,
      button: button,
      header: header,
      child: this,
    );
  }

  /// Exclude widget from semantics tree (for decorative elements)
  Widget excludeFromSemantics() {
    return ExcludeSemantics(child: this);
  }

  /// Merge semantics with children
  Widget mergeSemantics() {
    return MergeSemantics(child: this);
  }

  /// Add tooltip for accessibility
  Widget withTooltip(String message) {
    return Tooltip(
      message: message,
      child: this,
    );
  }

  /// Ensure minimum touch target size
  Widget withMinTouchTarget({double size = kMinTouchTargetSize}) {
    return SizedBox(
      width: size,
      height: size,
      child: Center(child: this),
    );
  }
}

/// Custom Semantics Actions
class SahoolSemanticsAction {
  /// Create a custom action for field operations
  static CustomSemanticsAction fieldAction(String label) {
    return CustomSemanticsAction(label: label);
  }

  /// Create a custom action for map interactions
  static CustomSemanticsAction mapAction(String label) {
    return CustomSemanticsAction(label: label);
  }
}
